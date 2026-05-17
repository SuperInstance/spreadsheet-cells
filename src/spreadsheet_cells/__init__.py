#!/usr/bin/env python3
"""
Spreadsheet Cell Simulator

A fleet of cells connected by TE-weighted edges, with formula evaluation,
deterministic RNG, oscillator phases, and emergent pattern detection.

Cell formulas support:
- AVG(neighbor.value) - average of all neighbor values
- RNG() - deterministic random value
- sin(phase) - oscillator phase
- Coefficients like * 0.5

Example: "AVG(neighbor.value) * 0.5 + RNG() * sin(phase)"
"""

import argparse
import random
import math
import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict


class Cell:
    """A cell in the spreadsheet simulator."""

    def __init__(self, cell_id: int, rng_seed: int):
        self.id = cell_id
        self.value = random.uniform(-1, 1)  # Start with random value
        self.formula = "AVG(neighbor.value) * 0.5 + RNG() * sin(phase)"
        self.neighbors: List[Tuple[int, float]] = []  # List of (neighbor_id, weight)
        self.oscillator_period = random.uniform(10, 50)
        self.rng_seed = rng_seed
        self.rng = random.Random(rng_seed)
        self.phase = 0.0

    def compute_phase(self, tick: int):
        """Compute oscillator phase for this tick."""
        self.phase = 2 * math.pi * tick / self.oscillator_period

    def get_rng_value(self) -> float:
        """Get deterministic random value from seeded RNG."""
        return self.rng.random()

    def evaluate_formula(self, cells: Dict[int, 'Cell']) -> float:
        """Evaluate the cell's formula using neighbor values."""
        # Parse formula: AVG(neighbor.value) * 0.5 + RNG() * sin(phase)
        result = 0.0

        # Handle AVG(neighbor.value) * coefficient
        if 'AVG(neighbor.value)' in self.formula:
            if self.neighbors:
                avg_neighbor = sum(cells[nid].value for nid, _ in self.neighbors) / len(self.neighbors)
                # Extract coefficient
                coef = 1.0
                if '*' in self.formula:
                    parts = self.formula.split('*')
                    if len(parts) > 1 and 'AVG' in parts[0]:
                        try:
                            after_avg = parts[1].split('+')[0].strip()
                            coef = float(after_avg)
                        except:
                            coef = 1.0
                result += avg_neighbor * coef

        # Handle RNG() * sin(phase)
        if 'RNG()' in self.formula and 'sin(phase)' in self.formula:
            rng_val = self.get_rng_value()
            phase_val = math.sin(self.phase)
            result += rng_val * phase_val

        # Add damping to prevent overflow
        result = result * 0.95

        return result

    def _evaluate_term(self, term: str, cells: Dict[int, 'Cell']) -> float:
        """Evaluate a single term from the formula."""
        term = term.strip()

        # Handle neighbor.value * weight pattern
        if 'neighbor.value' in term:
            # Extract numeric multiplier if present (e.g., "0.5 * neighbor.value")
            multiplier = 1.0
            cleaned_term = term

            # Try to extract multiplier before "neighbor.value"
            if 'neighbor.value' in cleaned_term:
                before_neighbor = cleaned_term.split('neighbor.value')[0].strip()
                if before_neighbor and before_neighbor.endswith('*'):
                    multiplier_str = before_neighbor[:-1].strip()
                    try:
                        multiplier = float(multiplier_str)
                    except ValueError:
                        multiplier = 1.0

            # Use all neighbors with their stored weights
            total = 0.0
            for neighbor_id, weight in self.neighbors:
                if neighbor_id in cells:
                    total += cells[neighbor_id].value * weight

            return total * multiplier

        # Handle RNG() * sin(phase)
        elif 'RNG()' in term and 'sin(phase)' in term:
            parts = term.split('*')
            if len(parts) == 2:
                rng_val = self.get_rng_value()
                phase_val = math.sin(self.phase)
                return rng_val * phase_val

        # Handle just RNG()
        elif 'RNG()' in term:
            return self.get_rng_value()

        # Handle just sin(phase)
        elif 'sin(phase)' in term:
            return math.sin(self.phase)

        # Handle numeric constants
        try:
            return float(term)
        except ValueError:
            return 0.0


class Simulator:
    """Main simulator class."""

    def __init__(self, num_cells: int, num_ticks: int, topology: str, te_file: str = None):
        self.num_cells = num_cells
        self.num_ticks = num_ticks
        self.topology = topology
        self.te_file = te_file
        self.cells: Dict[int, Cell] = {}
        self.history: List[Dict[int, float]] = []

    def initialize_cells(self):
        """Create cells with deterministic RNG seeds."""
        for i in range(self.num_cells):
            self.cells[i] = Cell(cell_id=i, rng_seed=42 + i)

    def build_topology(self):
        """Build the cell topology based on the selected type."""
        if self.topology == 'random':
            self._build_random_topology()
        elif self.topology == 'ring':
            self._build_ring_topology()
        elif self.topology == 'te-derived':
            self._build_te_derived_topology()
        else:
            raise ValueError(f"Unknown topology: {self.topology}")

    def _build_random_topology(self):
        """Each cell connects to 2-4 random neighbors."""
        for cell_id, cell in self.cells.items():
            num_neighbors = random.randint(2, 4)
            potential_neighbors = [cid for cid in range(self.num_cells) if cid != cell_id]

            # Select random neighbors
            selected = random.sample(potential_neighbors, min(num_neighbors, len(potential_neighbors)))

            for neighbor_id in selected:
                weight = random.uniform(0.1, 1.0)
                cell.neighbors.append((neighbor_id, weight))

    def _build_ring_topology(self):
        """Cells connected in a ring."""
        for cell_id, cell in self.cells.items():
            prev_neighbor = (cell_id - 1) % self.num_cells
            next_neighbor = (cell_id + 1) % self.num_cells

            cell.neighbors.append((prev_neighbor, 0.5))
            cell.neighbors.append((next_neighbor, 0.5))

    def _build_te_derived_topology(self):
        """Read TE weights from a file."""
        if not self.te_file:
            raise ValueError("te-file must be specified for te-derived topology")

        try:
            with open(self.te_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        from_cell = int(parts[0])
                        to_cell = int(parts[1])
                        weight = float(parts[2])

                        if to_cell in self.cells:
                            self.cells[to_cell].neighbors.append((from_cell, weight))
        except FileNotFoundError:
            raise ValueError(f"TE file not found: {self.te_file}")

    def run_simulation(self):
        """Run the main simulation loop."""
        print(f"Starting simulation: {self.num_cells} cells, {self.num_ticks} ticks, topology={self.topology}")

        for tick in range(self.num_ticks):
            tick_values = {}

            # Compute phases
            for cell in self.cells.values():
                cell.compute_phase(tick)

            # Evaluate formulas and update values
            for cell in self.cells.values():
                new_value = cell.evaluate_formula(self.cells)
                cell.value = new_value
                tick_values[cell.id] = new_value

            self.history.append(tick_values)

            # Print progress with sparklines
            if tick % 100 == 0 or tick == self.num_ticks - 1:
                self._print_tick_line(tick, tick_values)

    def _print_tick_line(self, tick: int, values: Dict[int, float]):
        """Print a tick line with values and sparkline."""
        cell_strs = []
        for cell_id in range(self.num_cells):
            cell_strs.append(f"cell_{cell_id}: {values[cell_id]:.2f}")

        sparkline = self._generate_sparkline(list(values.values()))

        # Build full line and truncate if too long
        full_line = f"tick {tick} | " + " | ".join(cell_strs) + f" | {sparkline}"

        # Keep last 40 characters (sparkline + some context)
        if len(full_line) > 200:
            print(full_line[-200:])
        else:
            print(full_line)

    def _generate_sparkline(self, values: List[float]) -> str:
        """Generate a sparkline representation of values."""
        # Normalize values to [0, 1]
        min_val = min(values) if values else 0
        max_val = max(values) if values else 1

        if max_val == min_val:
            normalized = [0.5 for _ in values]
        else:
            normalized = [(v - min_val) / (max_val - min_val) for v in values]

        # Convert to sparkline characters
        spark_chars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        sparkline = ''.join(
            spark_chars[int(n * (len(spark_chars) - 1))]
            for n in normalized
        )

        return sparkline[-40:]  # Last 40 characters

    def analyze_results(self):
        """Analyze simulation results and print statistics."""
        print("\n" + "="*60)
        print("SIMULATION ANALYSIS")
        print("="*60)

        # Convert history to numpy array for analysis
        data = np.array([[tick_values[i] for i in range(self.num_cells)] for tick_values in self.history])

        # Mean value per cell
        means = np.mean(data, axis=0)
        print("\nMean values per cell:")
        for i, mean in enumerate(means):
            print(f"  cell_{i}: {mean:.4f}")

        # Value variance per cell (measure of noise)
        variances = np.var(data, axis=0)
        print("\nValue variance (noise level) per cell:")
        for i, var in enumerate(variances):
            print(f"  cell_{i}: {var:.4f}")

        # Cross-correlation matrix
        correlation_matrix = np.corrcoef(data.T)
        print("\nCross-correlation matrix:")
        print("        " + " ".join(f"cell_{i:>4}" for i in range(self.num_cells)))
        for i in range(self.num_cells):
            print(f"cell_{i}:  " + " ".join(f"{correlation_matrix[i][j]:>7.3f}" for j in range(self.num_cells)))

        # Emergent patterns: highly correlated pairs
        print("\nEmergent patterns (coordinating cell pairs, correlation > 0.5):")
        coordinating_pairs = []
        for i in range(self.num_cells):
            for j in range(i + 1, self.num_cells):
                corr = correlation_matrix[i][j]
                if corr > 0.5:
                    coordinating_pairs.append((i, j, corr))

        if coordinating_pairs:
            for i, j, corr in sorted(coordinating_pairs, key=lambda x: x[2], reverse=True):
                print(f"  cell_{i} ↔ cell_{j}: correlation = {corr:.4f}")
        else:
            print("  No coordinating cell pairs found (correlation > 0.5)")

        # Summary statistics
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Total cells: {self.num_cells}")
        print(f"Total ticks: {self.num_ticks}")
        print(f"Topology: {self.topology}")
        print(f"Coordinating pairs: {len(coordinating_pairs)}")
        print(f"Average variance: {np.mean(variances):.4f}")
        print(f"Maximum correlation: {np.max(np.abs(correlation_matrix - np.eye(self.num_cells))):.4f}")


def main():
    parser = argparse.ArgumentParser(description='Spreadsheet Cell Simulator')
    parser.add_argument('--cells', type=int, default=10, help='Number of cells')
    parser.add_argument('--ticks', type=int, default=1000, help='Number of ticks')
    parser.add_argument('--topology', type=str, default='random',
                        choices=['random', 'ring', 'te-derived'],
                        help='Topology type')
    parser.add_argument('--te-file', type=str, help='TE weights file for te-derived topology')

    args = parser.parse_args()

    # Create and run simulator
    sim = Simulator(
        num_cells=args.cells,
        num_ticks=args.ticks,
        topology=args.topology,
        te_file=args.te_file
    )

    sim.initialize_cells()
    sim.build_topology()
    sim.run_simulation()
    sim.analyze_results()


if __name__ == '__main__':
    main()
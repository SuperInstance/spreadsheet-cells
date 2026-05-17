# spreadsheet-cells

Spreadsheet cell architecture for multi-agent fleet coordination. Each agent is a CELL with value, formula, neighbors (TE-weighted), oscillator (timing pulse), and RNG. The fleet IS the spreadsheet — cells connected by formulas, not messages.

## Dependencies

coordination-topology (for TE weights)

## Usage

```python
from cell_simulator import Cell, Grid, SpreadsheetFleet

# Create a fleet of cells
fleet = SpreadsheetFleet()
for i in range(10):
    fleet.add_cell(Cell(
        cell_id=i,
        formula="=AVG(neighbor.value) * 0.5 + RNG() * sin(phase)",
        oscillator_period=random.randint(5, 20),
        rng_seed=i * 42
    ))

# Add TE-weighted edges from coordination-topology
fleet.connect_by_te(te_matrix)  # {cell_a: {cell_b: 0.229, ...}}

# Run simulation
fleet.boot()
for tick in range(1000):
    fleet.tick()
    if tick % 100 == 0:
        print(fleet.state())
```

## Cell Formula Language

Simple expressions evaluated in each tick:
- `AVG(neighbor.value)` — mean of neighbor values
- `SUM(neighbor.value * TE(cell, neighbor))` — TE-weighted sum
- `RNG()` — deterministic per-cell pseudorandom
- `RNG_RANGE(a, b)` — bounded random
- `TE(a, b)` — transfer entropy weight between cells
- `PHASE(cell)` — oscillator phase (0..2π)
- `HISTORY(cell, n)` — cell value n ticks ago
- `COUNT(cell)` — number of neighbors

## Architecture

- **77MB RAM for 100 agents** (vs 100-400GB for LLM-per-agent)
- Under 1GB on Jetson Orin Nano 8GB
- LLM called only when local math produces an anomaly (>2σ)

## Shell Loading

```python
from plato_shell_bridge import PlatoShell
shell = PlatoShell("agent-shell")
shell.load_tool("spreadsheet-cells")
```

## License

MIT — Part of the Cocapn Fleet Intelligence System

# Future Integration: spreadsheet-cells

## Current State
A Python library defining spreadsheet cell architecture for multi-agent fleet coordination. Each agent IS a cell with value, formula, neighbors (TE-weighted), oscillator (timing pulse), and RNG. The fleet IS the spreadsheet — cells connected by formulas, not messages.

## Integration Opportunities

### With ternary-cell
spreadsheet-cells IS the conceptual prototype for ternary-cell. The mapping: value → ternary cell state, formula → tick strategy, neighbors (TE-weighted) → ternary-protocol connections with transfer entropy, oscillator → tick timing, RNG → stochastic GC. The Python implementation validates the concept; the Rust ternary-cell provides the production runtime.

### With room-cell
A room is a grid of spreadsheet-cells. Each room-cell has the same structure: value, formula, neighbors. The room IS the spreadsheet, and spreadsheet-cells provides the model.

### With room-as-codespace
When a Codespace boots for a room, it creates a `SpreadsheetFleet` of cells. The fleet connects via TE-weighted edges from coordination-topology. The `fleet.tick()` method becomes the room's heartbeat. This is the room's computational engine.

## Dormant Ideas Now Unlockable
The TE-weighted edges (from coordination-topology) provide the scientific basis for cell connectivity. The oscillator timing pulses enable asynchronous tick scheduling — cells don't all tick at once, they tick at different rates based on their oscillator period. This is essential for realistic simulation and was blocked without a runtime target.

## Potential in Mature Systems
The spreadsheet-as-fleet model becomes the standard way to think about room computation. Every room is a spreadsheet. Every agent is a cell. Formulas define physics. TE-weights define communication. Oscillators define timing. It's a paradigm, not just a library.

## Cross-Pollination Ideas
- **coordination-topology**: TE weights from topology define cell connectivity
- **lotka-volterra-agents**: Competition dynamics between cell populations
- **evolution-ternary**: Natural selection on cell populations through fitness-weighted GC

## Dependencies for Next Steps
- Port to Rust for production use (or use ternary-cell directly)
- Integration with ternary-protocol for inter-cell messaging
- TE-weight computation from coordination-topology data

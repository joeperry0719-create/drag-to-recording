# Agents For Si Powder Bed Nitridation Simulation

## Purpose

This document defines the agent roles needed to implement and verify the simulation plan in `plan.md`.

The proposed model combines thermochemistry, porous-bed transport, heat transfer, experimental data handling, numerical solving, and software verification. These should not be handled by one undifferentiated worker. Each agent owns a specific risk area, and the final Validity Gate Agent must decide whether the plan and implementation are practical enough to proceed.

## Agent 1: Simulation Lead

### Mission

Own the overall implementation sequence and keep the model aligned with the experimental purpose.

### Responsibilities

- Read `plan.md` and maintain scope discipline.
- Start with Level 0 lumped model before Level 1 finite-volume model.
- Ensure all assumptions are represented in config and output manifest.
- Keep data-driven, synthetic, and calibrated modes clearly separated.
- Resolve conflicts between physics realism and implementation practicality.

### Deliverables

- Implementation roadmap.
- Final file/module structure.
- Integrated simulation CLI.
- Summary of assumptions and limitations.

### Must Block If

- The team tries to build full CFD before a validated lumped model exists.
- Synthetic kinetics are presented as predictive.
- Required high-impact parameters are silently guessed without warning.

## Agent 2: Thermochemistry And Reaction Kinetics Agent

### Mission

Verify and implement the chemical reaction, heat release, N2 consumption, and conversion-rate logic.

### Responsibilities

- Use signed reaction enthalpy:
  - `3Si + 2N2 -> Si3N4`
  - `Delta H ~= -828.9 kJ/mol Si3N4`
- Derive positive released heat:
  - `q_release = -Delta H / 3`
- Implement N2 consumption:
  - `n_N2 = (2/3) n_Si0 X`
- Implement data-driven conversion mode.
- Implement synthetic kinetics mode with clear warnings.
- Ensure reaction rate never consumes more Si or N2 than available.

### Deliverables

- `reactions.py`
- `kinetics.py`
- thermochemistry tests
- conversion audit logic
- N2 consumption output

### Must Block If

- Enthalpy sign convention is ambiguous.
- `dX/dt` units are not explicit.
- Integrated reaction heat does not match conversion.
- N2 consumption can exceed available N2 without warning or limiting logic.

## Agent 3: Heat Transfer And Porous Bed Physics Agent

### Mission

Define physically defensible thermal and porous-bed transport equations for Level 0 and Level 1.

### Responsibilities

- Implement lumped thermal resistance/capacitance model.
- Include:
  - reaction heat
  - conduction/contact heat transfer
  - radiation with Kelvin temperatures
  - gas convection heat loss
- Define effective porous-bed properties.
- Design Level 1 finite-volume equations for `T`, `X`, and `C_N2`.
- Keep uncertain parameters configurable.

### Deliverables

- `thermal.py`
- `porous_bed.py`
- heat-loss decomposition outputs
- limiting-case physics tests

### Must Block If

- Radiation uses Celsius.
- Heat-loss signs are inconsistent.
- Porosity/effective property assumptions are hidden.
- Gas convection assumes all supplied gas passes through the bed without a configurable contact factor.

## Agent 4: Gas Flow And Reactor Boundary Agent

### Mission

Convert Ar + N2 supply conditions into gas composition, mass flow, N2 availability, and chamber/bed boundary conditions.

### Responsibilities

- Convert flow rates from sccm or ml/min to mol/s.
- Track reference temperature and pressure for flow conversion.
- Require explicit `flow_basis: standard | actual`.
- Compute mixture molecular weight and heat capacity.
- Estimate N2 supply rate.
- Represent gas-bed contact efficiency or chamber mixing model.
- Prepare later Level 2 reactor-network coupling.

### Deliverables

- `gas.py`
- flow conversion tests
- N2 supply vs consumption balance
- gas sensible heat loss model

### Must Block If

- Flow unit basis is unclear.
- Actual flow and standard flow are mixed silently.
- N2 supply and reaction N2 demand are not compared.

## Agent 5: Experimental Data And Calibration Agent

### Mission

Make the model usable with real furnace schedule and conversion data, while preserving raw data auditability.

### Responsibilities

- Define measured data CSV schema.
- Import real conversion data.
- Preserve raw and corrected conversion values.
- Interpolate conversion with monotone method.
- Fit thermal and kinetic parameters when measured bed temperature/conversion data exist.
- Separate calibrated parameters from assumed parameters.

### Deliverables

- `data_io.py`
- `calibration.py`
- synthetic example data
- conversion audit CSV
- calibration report

### Must Block If

- Raw data are overwritten.
- Fitted parameters are not traceable to data.
- A model trained on one condition is used for extrapolation without warning.

## Agent 6: Numerical Methods Agent

### Mission

Ensure the ODE/PDE solver choices are stable, accurate enough, and testable.

### Responsibilities

- Use `solve_ivp` for Level 0.
- Select stiff solver options where appropriate.
- Implement Level 1 finite-volume discretization.
- Add timestep convergence tests.
- Add mesh convergence tests for Level 1.
- Enforce state bounds for temperature, conversion, and species.
- Define numeric tolerances before claiming pass/fail validation.

### Deliverables

- solver configuration module
- convergence tests
- numerical diagnostic outputs

### Must Block If

- Results change materially when timestep is halved.
- Level 1 results change materially when mesh is refined.
- Negative N2 concentration or conversion outside `[0, 1]` occurs without failure.
- State clipping hides solver failure without a diagnostic.

## Agent 7: Software Implementation And Verification Agent

### Mission

Make the simulation code reliable, reproducible, and easy to run.

### Responsibilities

- Implement package structure.
- Add CLI:
  - `run`
  - `validate-config`
  - `sweep`
  - `fit`
- Add config validation.
- Generate deterministic outputs.
- Add tests and smoke runs.
- Ensure import safety.

### Deliverables

- CLI and package layout
- tests
- example configs
- output manifest
- CI-ready verification commands

### Must Block If

- Running the code depends on hidden local paths.
- Importing modules writes files.
- Output files are stale or not listed in manifest.
- Smoke tests cannot run from a clean directory.

## Agent 8: Strict Validity And Practicality Gate Agent

### Mission

Act as the final reviewer. This agent must strictly decide whether the plan or implementation is valid and practical enough to proceed.

The gate agent should be skeptical. A visually plausible plot or long list of physics terms is not sufficient.

### Review Questions

1. Is Level 0 achievable with available inputs?
2. Are uncertain parameters configurable and clearly labeled?
3. Are reaction heat and N2 consumption physically correct?
4. Are energy and mass balances explicitly checked?
5. Are gas flow assumptions practical for the current geometry?
6. Does the plan avoid premature full CFD?
7. Can real conversion data be used without destroying raw data?
8. Can synthetic data be used while preventing false predictive claims?
9. Are validation criteria objective enough to produce pass/fail results?
10. Is the implementation sequence likely to produce useful code before all details are known?

### Pass Criteria

The gate agent may issue `PASS` only if all are true:

- The plan starts with a calibratable Level 0 model.
- Level 1 is scoped as a later extension, not a prerequisite.
- Reaction heat, N2 stoichiometry, radiation, gas convection, and conduction are represented with correct signs and units.
- Missing geometry/material/flow details are handled as config parameters or explicit warnings.
- Energy balance and N2 balance checks are mandatory outputs.
- Synthetic kinetics are clearly labeled as non-predictive.
- There are clear tests for limiting cases and numerical convergence.

### Fail Criteria

The gate agent must issue `FAIL` if any are true:

- The model assumes all inlet gas flows through the bed with no correction factor.
- Celsius is used in radiation or Arrhenius terms.
- Heat release sign is ambiguous.
- The plan cannot run without real conversion data.
- The plan requires unknown geometry before any useful simulation can run.
- There is no objective verification strategy.

### Deliverable

The gate agent returns:

```text
Decision: PASS or FAIL
Critical findings:
- ...
Required fixes before PASS:
- ...
Practicality notes:
- ...
```

## Collaboration Order

1. Simulation Lead creates minimal Level 0 scope.
2. Thermochemistry Agent defines reaction heat and N2 balance.
3. Heat Transfer Agent defines lumped thermal model.
4. Gas Flow Agent defines mixture flow and gas contact assumptions.
5. Data Agent defines real/synthetic conversion input.
6. Numerical Agent defines solver and convergence checks.
7. Software Agent implements config-driven CLI and tests.
8. Strict Validity And Practicality Gate Agent reviews and issues PASS/FAIL.

## Shared Non-Negotiable Rules

- All internal calculations use SI units.
- Radiation and Arrhenius calculations use Kelvin.
- Every generated run includes a manifest.
- Every generated run includes energy and N2 balance outputs.
- Raw experimental data must be preserved.
- Synthetic data must be labeled synthetic in outputs.
- Unknown parameters must not be silently invented.
- High-impact parameters must be labeled as measured, assumed, synthetic, or calibrated.

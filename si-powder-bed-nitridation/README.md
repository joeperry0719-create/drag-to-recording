# Si Powder Bed Nitridation Simulation

This folder is the working area for the Si powder bed nitridation simulation project.

## Current Scope

- Build a config-driven nitridation simulation for the described Ar + N2 furnace setup.
- Start with a Level 0 lumped thermal reactor model.
- Extend later to a Level 1 1D porous-bed finite-volume model.
- Include reaction heat, N2 supply/consumption, radiation, gas convection, and conduction/contact heat transfer.
- Support both measured conversion data and explicitly labeled synthetic kinetics.

## Documents

- `plan.md`: physical, chemical, numerical, and implementation plan.
- `agents.md`: agent roles and strict pass/fail review criteria.

## Working Rule

New code, configs, tests, and generated planning artifacts for this simulation should be placed under this folder.

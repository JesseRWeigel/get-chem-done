# Get Chem Done

> An AI copilot for autonomous computational chemistry research — from molecular hypothesis to simulation to publication.

**Inspired by [Get Physics Done](https://github.com/psi-oss/get-physics-done)** — the open-source AI copilot that autonomously conducts physics research. Get Chem Done adapts GPD's architecture for computational chemistry, molecular modeling, and drug discovery workflows.

## Vision

Computational chemistry research involves complex multi-step workflows: basis set selection, functional choice, geometry optimization, property calculation, and validation against experiment. Each choice cascades — a wrong basis set invalidates everything downstream. This is exactly the kind of problem GPD's convention-locking and verification architecture was built to solve.

Get Chem Done wraps LLM capabilities in a verification-first framework that:
- **Locks computational parameters** across phases (basis sets, functionals, force fields, convergence criteria)
- **Verifies chemical consistency** — energy conservation, symmetry preservation, comparison to experimental data
- **Decomposes research** into phases: system setup → geometry optimization → property calculation → validation → analysis → paper writing
- **Follows established workflows** — DFT best practices, molecular dynamics protocols, docking procedures

## Architecture

Adapted from GPD's three-layer design:

### Layer 1 — Core Library (Python)
State management, phase lifecycle, git operations, convention locks, verification kernel.

### Layer 2 — MCP Servers
- `gcd-state` — Project state queries
- `gcd-conventions` — Computational parameter lock management
- `gcd-protocols` — Chemistry methodology protocols (DFT, MD, docking, QM/MM, etc.)
- `gcd-patterns` — Cross-project learned patterns
- `gcd-verification` — Chemical consistency and convergence checks
- `gcd-errors` — Known LLM computational chemistry failure modes

### Layer 3 — Agents & Commands
- `gcd-planner` — Computational workflow planning
- `gcd-executor` — Simulation setup and execution
- `gcd-verifier` — Results verification and validation
- `gcd-researcher` — Literature and database research
- `gcd-analyst` — Data analysis and property extraction
- `gcd-paper-writer` — Manuscript generation
- `gcd-referee` — Methodology and results review

## Convention Lock Fields

1. Basis set (6-31G*, cc-pVTZ, def2-TZVP, etc.)
2. Exchange-correlation functional (B3LYP, PBE, wB97X-D, etc.)
3. Dispersion correction (D3, D3BJ, D4, etc.)
4. Solvent model (implicit: PCM, SMD, COSMO; explicit)
5. Force field (AMBER, CHARMM, OPLS, etc.)
6. Convergence criteria (energy, gradient, displacement thresholds)
7. Integration grid (fine, ultrafine, etc.)
8. Pseudopotential / ECP choice
9. Thermodynamic reference state (T, P, standard state)
10. Unit conventions (energy: kcal/mol, kJ/mol, Hartree, eV)

## Verification Framework

1. **Energy conservation** — MD trajectories conserve total energy
2. **Geometry convergence** — optimization converged to stationary point
3. **Frequency validation** — no imaginary frequencies for minima, one for TS
4. **Basis set convergence** — results stable with basis set improvement
5. **Functional sensitivity** — results consistent across reasonable functional choices
6. **Symmetry preservation** — molecular symmetry maintained appropriately
7. **Thermodynamic consistency** — free energies self-consistent
8. **Experimental comparison** — computed properties match experiment within expected accuracy
9. **Charge conservation** — total charge and spin multiplicity correct
10. **Sampling adequacy** — MD simulations converged (RMSD, energy fluctuations)
11. **Literature benchmarks** — known systems reproduced
12. **Reproducibility** — results reproducible with different starting conditions

## Status

**Early development** — Scaffolding and initial design. Seeking domain expert contributors!

## Relationship to GPD

Energy conservation, symmetry preservation, and convergence verification transfer from GPD's physics framework. Chemistry adds basis set/functional consistency and experimental validation.

We plan to showcase this in the [GPD Discussion Show & Tell](https://github.com/psi-oss/get-physics-done/discussions) once operational.

## Contributing

We're looking for contributors with:
- Computational chemistry research experience
- Experience with Gaussian, ORCA, VASP, GROMACS, or similar packages
- DFT, MD, or drug discovery workflow expertise
- Familiarity with GPD's architecture

See the [Issues](../../issues) for specific tasks.

## License

MIT

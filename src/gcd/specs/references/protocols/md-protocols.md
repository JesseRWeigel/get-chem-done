# Molecular Dynamics Protocols

> Step-by-step methodology guides for molecular dynamics simulations.

## Protocol: Classical MD Simulation

### When to Use
Sampling conformational space, computing ensemble-averaged properties, studying dynamics.

### Steps
1. **Prepare system** — add hydrogens, assign protonation states, solvate, add ions
2. **Assign force field** — check convention lock (AMBER ff19SB for proteins, GAFF2 for small molecules, CHARMM36m alternative)
3. **Choose water model** — check convention lock (TIP3P default for AMBER, SPC/E for bulk properties, OPC for accuracy)
4. **Energy minimization** — steepest descent then conjugate gradient (1000-5000 steps each)
5. **Heating** — gradual temperature ramp (0 K to target, 50-100 ps) with position restraints
6. **Equilibration (NVT)** — 100-500 ps with thermostat (Langevin, tau=1.0 ps)
7. **Equilibration (NPT)** — 100-500 ps with barostat (Monte Carlo barostat or Berendsen, then Parrinello-Rahman)
8. **Production run** — NPT (or NVT if volume should be fixed)
9. **Analysis** — RMSD, RMSF, radius of gyration, hydrogen bonds, etc.
10. **Convergence check** — block averaging, autocorrelation analysis

### Parameters
- Timestep: 2 fs (with SHAKE/LINCS for H-bonds), 1 fs without constraints
- Cutoff: 10-12 Angstrom for non-bonded interactions
- PME for long-range electrostatics (grid spacing ~1 Angstrom)
- Save coordinates every 10-100 ps depending on trajectory length

### Common LLM Pitfalls
- Skipping equilibration or making it too short
- Using too large a timestep (causes energy drift)
- Not checking for adequate sampling (E015 equivalent)
- Forgetting to add counterions for charged systems
- Using Berendsen thermostat/barostat for production (wrong ensemble)

---

## Protocol: QM/MM Simulation

### When to Use
When bond breaking/formation must be modeled within a larger molecular environment.

### Steps
1. **Define QM region** — active site + key residues (typically 50-200 atoms)
2. **Define MM region** — rest of the system
3. **Choose QM method** — DFT (B3LYP-D3(BJ) typical) for QM region
4. **Choose MM force field** — same as classical MD
5. **Handle boundary** — link atom scheme (most common) or frozen orbital
6. **Electrostatic embedding** — include MM point charges in QM Hamiltonian (recommended)
7. **Optimize QM/MM boundary** — minimize artifacts from partitioning
8. **Run QM/MM MD** — shorter than classical (10-100 ps typical)
9. **Validate** — compare QM/MM barrier with full QM on cluster model

### Common LLM Pitfalls
- Making QM region too small (missing key interactions)
- Cutting through conjugated systems at QM/MM boundary
- Not using electrostatic embedding (mechanical embedding misses polarization)
- Comparing QM/MM with gas-phase QM directly

---

## Protocol: Enhanced Sampling

### When to Use
When standard MD cannot cross energy barriers within simulation time.

### Steps — Replica Exchange (REMD)
1. **Set up replicas** — 16-64 replicas spanning temperature range (e.g., 300-600 K)
2. **Choose temperature distribution** — geometric spacing for ~20-30% exchange rate
3. **Run production** — at least 100 ns per replica
4. **Analyze exchanges** — check exchange rates (target: 20-30%)
5. **Analyze at target temperature** — extract frames at 300 K

### Steps — Metadynamics
1. **Choose collective variables (CVs)** — the reaction coordinate(s) to bias
2. **Set Gaussian parameters** — height (0.5-1.0 kJ/mol), width (0.1-0.5), deposition rate (every 500-1000 steps)
3. **Run well-tempered metadynamics** — bias factor 10-30
4. **Check convergence** — free energy surface should stop changing
5. **Reweight** — to obtain unbiased ensemble averages

### Common LLM Pitfalls
- Choosing poor CVs (most common failure in metadynamics)
- Gaussian hills too large (overshoot barriers)
- Not running long enough for convergence
- Not checking exchange acceptance rates in REMD

---

## Protocol: Free Energy Perturbation / Thermodynamic Integration

### When to Use
Computing relative binding affinities, solvation free energies, pKa values.

### Steps
1. **Define lambda windows** — 11-21 windows (0.0, 0.05, 0.1, ..., 1.0)
2. **Use soft-core potentials** — for appearing/disappearing atoms
3. **Equilibrate each window** — 1-5 ns
4. **Production** — 5-20 ns per window
5. **Analyze** — BAR or MBAR for free energy estimate
6. **Check convergence** — forward/reverse hysteresis < 0.5 kcal/mol
7. **Error estimation** — block bootstrap or MBAR uncertainty

### Common LLM Pitfalls
- Not using soft-core potentials for alchemical transformations
- Too few lambda windows (causes endpoint singularities)
- Not checking for convergence of dV/dlambda
- Ignoring finite-size corrections for charged mutations

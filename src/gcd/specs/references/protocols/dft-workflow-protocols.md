# DFT Workflow Protocols

> Step-by-step methodology guides for density functional theory calculations.

## Protocol: Geometry Optimization

### When to Use
Finding equilibrium structures (energy minima) or transition states.

### Steps
1. **Choose initial geometry** — from crystal structure, force field pre-optimization, or chemical intuition
2. **Select functional** — check convention lock; default B3LYP-D3(BJ) or wB97X-D for organics, PBE0-D3(BJ) for inorganics
3. **Select basis set** — check convention lock; def2-SVP for pre-optimization, def2-TZVP for production
4. **Set convergence criteria** — tight for frequency calculations, default otherwise
5. **Run optimization** — monitor energy convergence and gradient norms
6. **Verify convergence** — check max force, RMS force, max displacement, RMS displacement
7. **Run frequency calculation** — verify 0 imaginary for minimum, 1 for TS
8. **If imaginary frequencies found for minimum**: displace along mode, re-optimize

### Common LLM Pitfalls
- Skipping frequency validation (E005)
- Using too loose convergence for thermochemistry
- Not checking for multiple conformers (E012)
- Ignoring symmetry breaking (E009)

---

## Protocol: Thermochemistry Calculation

### When to Use
Computing reaction enthalpies, free energies, activation barriers.

### Steps
1. **Optimize all species** — same level of theory for all (check convention lock)
2. **Run frequency calculations** — verify no imaginary frequencies for minima
3. **Apply thermal corrections** — standard state (check convention lock, default 298.15 K, 1 atm)
4. **Apply quasi-harmonic corrections** — Grimme quasi-RRHO for low-frequency modes (< 100 cm^-1)
5. **Compute relative energies** — always use the SAME reference for all species
6. **Apply solvation corrections** — if solution-phase (SMD or PCM, check convention lock)
7. **Report G, H, and S** — not just electronic energy (E004 guard)
8. **Estimate uncertainty** — based on functional benchmarks (typically +/- 2-3 kcal/mol for DFT)

### Common LLM Pitfalls
- Confusing electronic energy with free energy (E004)
- Missing thermal corrections entirely
- Mixing reference states (E010)
- Ignoring solvation for charged species (E013)
- Over-interpreting small energy differences (E015)

---

## Protocol: Single-Point Energy Refinement

### When to Use
Computing accurate energies at a higher level of theory on geometries optimized at a lower level.

### Steps
1. **Optimize geometry** — at a reasonable level (e.g., B3LYP-D3(BJ)/def2-TZVP)
2. **Run single-point** — at higher level (e.g., DLPNO-CCSD(T)/cc-pVTZ)
3. **Add thermal corrections** — from the optimization-level frequency calculation
4. **This gives**: G = E_high_level + (G_low - E_low) = E_high_level + thermal_correction
5. **For basis set extrapolation**: run at two basis sets (TZ, QZ) and extrapolate
6. **Report the composite scheme** — specify both levels of theory clearly

### Common LLM Pitfalls
- Mixing thermal corrections from different levels of theory
- Not specifying the composite scheme clearly
- Using too small a basis set for the high-level calculation

---

## Protocol: Transition State Search

### When to Use
Finding saddle points for reaction pathways.

### Steps
1. **Generate initial TS guess** — from: QST2/QST3 (reactant/product), scan along reaction coordinate, or chemical intuition
2. **Optimize to TS** — using Berny algorithm, dimer method, or eigenvector following
3. **Verify** — exactly one imaginary frequency
4. **Verify mode** — imaginary frequency corresponds to expected bond breaking/forming
5. **Run IRC** — intrinsic reaction coordinate to confirm connection to reactant and product
6. **Optimize IRC endpoints** — verify they correspond to expected minima
7. **Compute barrier** — relative to reactant (not absolute)

### Common LLM Pitfalls
- Accepting a TS with wrong imaginary mode direction
- Not running IRC verification
- Confusing the TS for a higher-order saddle point (2+ imaginary frequencies)
- Not re-optimizing IRC endpoints

---

## Protocol: Excited State Calculations

### When to Use
Computing UV-Vis spectra, fluorescence, phosphorescence, photochemistry.

### Steps
1. **Optimize ground state geometry** — at appropriate level
2. **Select TD-DFT functional** — range-separated hybrids (CAM-B3LYP, wB97X-D) recommended for charge-transfer states
3. **Request sufficient states** — at least 2-3x the number of states of interest
4. **Analyze transitions** — identify dominant orbital contributions
5. **For emission**: optimize excited state geometry (TD-DFT opt), compute vertical emission
6. **For solvatochromism**: compare gas phase and solvated excitations
7. **Validate against experiment** — typical TD-DFT accuracy is +/- 0.3 eV

### Common LLM Pitfalls
- Using B3LYP for charge-transfer states (severely underestimates)
- Not requesting enough states
- Confusing absorption and emission geometries
- Ignoring state ordering issues between TD-DFT and experiment

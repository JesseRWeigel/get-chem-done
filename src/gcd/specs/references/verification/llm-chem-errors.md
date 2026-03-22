# Known LLM Computational Chemistry Failure Modes

> This catalog documents systematic failure patterns of LLMs in computational chemistry tasks.
> The verifier and analyst cross-reference against these patterns.

## Critical Errors (High Frequency)

### E001: Incorrect Charge/Multiplicity Assignment
**Pattern**: Wrong total charge or spin multiplicity in input files, especially for metal complexes, radicals, and ions.
**Example**: Setting a Cu(II) complex as singlet instead of doublet, or forgetting to add +1 charge for a cation.
**Guard**: Explicitly count electrons. For open-shell systems, verify 2S+1 matches the expected multiplicity.

### E002: Wrong Basis Set for Heavy Elements
**Pattern**: Using all-electron basis sets for elements where ECPs are required, or mismatching ECP and valence basis set.
**Example**: Using 6-31G(d) for iodine (needs ECP), or combining LANL2DZ pseudopotential with cc-pVTZ valence basis.
**Guard**: For elements Z > 36 (Kr), always specify an ECP. Verify ECP/basis set compatibility.

### E003: Missing Dispersion Correction for Non-Covalent Interactions
**Pattern**: Running DFT calculations on systems with significant dispersion interactions without empirical correction.
**Example**: Computing binding energy of a pi-stacked complex with B3LYP (no dispersion) — will dramatically underestimate binding.
**Guard**: Always include D3(BJ) or D4 for: pi-stacking, hydrogen bonding, van der Waals complexes, large molecules, molecular crystals.

### E004: Confusing Electronic Energy with Free Energy
**Pattern**: Reporting raw electronic energies as if they were free energies, or comparing energies computed at different levels of theory.
**Example**: Claiming a reaction barrier is 5 kcal/mol based on electronic energy difference, without thermal/entropic corrections.
**Guard**: Always specify which energy quantity is reported (E_elec, H, G). Apply thermal corrections from frequency calculations.

### E005: Imaginary Frequencies Ignored
**Pattern**: Proceeding with thermodynamic analysis on a structure with imaginary frequencies (not a true minimum).
**Example**: Computing the free energy of a "minimum" that has one imaginary frequency — it's actually a transition state or saddle point.
**Guard**: Always check frequency output. Zero imaginary for minima, exactly one for TS. Re-optimize if unexpected imaginary modes found.

## Serious Errors (Medium Frequency)

### E006: Basis Set Superposition Error (BSSE) Ignored
**Pattern**: Computing binding energies without counterpoise correction, especially with small basis sets.
**Example**: Reporting a binding energy 3 kcal/mol too strong because of BSSE with a 6-31G(d) basis.
**Guard**: Use counterpoise correction for intermolecular interactions, or use basis sets large enough that BSSE is negligible (def2-TZVP or larger).

### E007: Inappropriate Functional for the Problem
**Pattern**: Using a functional known to fail for the specific type of calculation.
**Example**: B3LYP for barrier heights (systematically underestimates), pure GGA for band gaps (severely underestimates), single-reference for strongly correlated systems.
**Guard**: Check benchmark studies for the property type. Use recommended functionals: M06-2X for thermochemistry/kinetics, PBE0/HSE06 for solids, range-separated hybrids for CT states.

### E008: SCF Convergence Issues Mishandled
**Pattern**: Declaring a calculation "failed" without trying standard convergence remedies, or accepting a non-converged result.
**Example**: Giving up after default DIIS fails, instead of trying damping, level shifting, or fractional occupation.
**Guard**: Try convergence aids in order: increase DIIS history, add damping (0.2-0.5), add level shift (0.1-0.5 Hartree), try SOSCF, try stability analysis.

### E009: Incorrect Symmetry Handling
**Pattern**: Forcing symmetry constraints that prevent finding the true minimum, or losing symmetry when it should be preserved.
**Example**: Constraining a molecule to D6h when Jahn-Teller distortion lowers it to D2h.
**Guard**: Start with no symmetry constraints (C1), then verify if the optimized structure has higher symmetry. Only enforce symmetry if physically justified.

### E010: Thermodynamic Reference State Confusion
**Pattern**: Mixing different reference states when comparing energies.
**Example**: Comparing gas-phase and solution-phase free energies without consistent reference state, or using different temperatures for different species.
**Guard**: Define the reference state once (T, P, concentration standard) and apply consistently to all species.

## Moderate Errors (Common but Usually Caught)

### E011: Unit Conversion Errors
**Pattern**: Incorrect conversion between energy units, especially Hartree to kcal/mol.
**Example**: Using 627.5 kcal/mol per Hartree instead of 627.509 (small but compounds over many values), or confusing kcal and kJ.
**Guard**: Use a single conversion factor consistently. 1 Hartree = 627.5095 kcal/mol = 2625.500 kJ/mol = 27.2114 eV.

### E012: Incomplete Conformational Search
**Pattern**: Computing properties for a single conformer when multiple low-energy conformers exist.
**Example**: Computing pKa from a single protonation site geometry when the molecule has rotatable bonds creating multiple relevant conformers.
**Guard**: Always consider conformational flexibility. Use systematic or stochastic conformer search for flexible molecules.

### E013: Solvent Effects Neglected
**Pattern**: Performing gas-phase calculations when solvent effects are critical.
**Example**: Computing relative energies of zwitterionic vs neutral forms without solvation — gas phase will always favor neutral.
**Guard**: Use implicit solvation (SMD/PCM) for any charged species, ionic reactions, or solution-phase properties. Explicit solvent for specific hydrogen bonding.

### E014: Relativistic Effects Neglected
**Pattern**: Ignoring scalar relativistic effects for elements heavier than Kr.
**Example**: Computing Au-ligand bond lengths without relativistic correction — will be too long by ~0.1 Angstrom.
**Guard**: For Z > 36: use ECPs (include relativistic effects implicitly) or scalar relativistic Hamiltonians (DKH2, ZORA). For Z > 80: consider spin-orbit coupling.

### E015: Numerical Noise Mistaken for Signal
**Pattern**: Interpreting small energy differences (< ~0.1 kcal/mol for DFT) as meaningful.
**Example**: Claiming conformer A is more stable than B by 0.02 kcal/mol at the B3LYP/6-31G(d) level — this is within numerical noise.
**Guard**: Know the accuracy limits of the method. DFT energies are typically accurate to ~1-3 kcal/mol. Don't over-interpret small differences.

## How to Use This Catalog

1. **Analyst**: Before execution, identify tasks where specific errors are likely. Add explicit guards.
2. **Executor**: Consult relevant entries when performing work of that type. Follow guards.
3. **Verifier**: After execution, cross-reference results against applicable error patterns.
4. **Pattern library**: When a new error pattern is discovered, add it here.

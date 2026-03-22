---
name: new-project
description: Initialize a new computational chemistry research project
---

<process>

## Initialize New Computational Chemistry Research Project

### Step 1: Create project structure
Create the `.gcd/` directory and all required subdirectories:
- `.gcd/` — project state and config
- `.gcd/observability/sessions/` — session logs
- `.gcd/traces/` — execution traces
- `knowledge/` — research knowledge base
- `calculations/` — calculation input/output files
- `.scratch/` — temporary working files (gitignored)

### Step 2: Gather project information
Ask the user:
1. **Project name**: What is this computational chemistry project about?
2. **System**: What molecular system(s) are you studying? (molecule, reaction, material)
3. **Target property**: What property/quantity do you want to compute? (energetics, spectra, dynamics, mechanism)
4. **Model profile**: high-accuracy (default), production, screening, review, or paper-writing?
5. **Research mode**: explore, balanced (default), exploit, or adaptive?

### Step 3: Create initial ROADMAP.md
Based on the research question, create a phase breakdown:

```markdown
# [Project Name] — Roadmap

## Phase 1: Literature Survey
**Goal**: Identify known computational results, benchmark data, and experimental references for [system]

## Phase 2: Method Selection and Benchmarking
**Goal**: Select and validate the level of theory (functional, basis set, corrections)

## Phase 3: Geometry Optimization
**Goal**: Obtain optimized geometries for all relevant species (minima, transition states, conformers)

## Phase 4: Property Calculations
**Goal**: Compute target properties at the validated level of theory

## Phase 5: Verification and Analysis
**Goal**: Independent verification and deep analysis of all results

## Phase 6: Paper Writing
**Goal**: Write publication-ready manuscript
```

Adjust phases based on the specific project. Some projects need additional phases (e.g., MD equilibration, conformational search, solvent screening).

### Step 4: Initialize state
Create STATE.md and state.json with:
- Project name and creation date
- Phase listing from ROADMAP
- Phase 1 set as active
- Research mode and autonomy mode

### Step 5: Initialize config
Create `.gcd/config.json` with user's choices.

### Step 6: Initialize git
If not already a git repo, initialize one. Add `.scratch/` to `.gitignore`.
Commit the initial project structure.

### Step 7: Convention prompting
Ask if the user wants to pre-set any conventions:
- Preferred software package (Gaussian, ORCA, Q-Chem, VASP, etc.)
- Preferred functional and basis set
- Unit conventions
- Standard state for thermodynamics

Lock any conventions the user specifies.

### Step 8: Summary
Display:
- Project structure created
- Phases from roadmap
- Active conventions
- Next step: run `plan-phase` to begin Phase 1

</process>

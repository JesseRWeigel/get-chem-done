"""Convention lock management for computational chemistry consistency.

Ensures computational parameters don't drift across phases of a research project.
Adapted from GPD's conventions.py for computational chemistry.
"""

from __future__ import annotations

from typing import Any

from .constants import CONVENTION_FIELDS
from .state import StateEngine, ConventionLock


# -- Convention Field Descriptions ------------------------------------------

CONVENTION_DESCRIPTIONS: dict[str, str] = {
    "basis_set": (
        "Gaussian basis set for electronic structure calculations. Examples: "
        "Pople-style (6-31G*, 6-311+G(d,p)), Dunning correlation-consistent "
        "(cc-pVDZ, aug-cc-pVTZ), Ahlrichs/Karlsruhe (def2-SVP, def2-TZVP), "
        "or plane-wave cutoff for periodic calculations."
    ),
    "functional": (
        "Exchange-correlation functional or post-HF method. Examples: "
        "GGA (PBE, BLYP), hybrid (B3LYP, PBE0), range-separated hybrid "
        "(wB97X-D, CAM-B3LYP), meta-GGA (TPSS, M06-2X), double-hybrid "
        "(B2PLYP), or wavefunction methods (MP2, CCSD(T), CASSCF)."
    ),
    "dispersion_correction": (
        "Empirical dispersion correction for DFT. Options: D3 (Grimme DFT-D3), "
        "D3(BJ) (with Becke-Johnson damping), D4 (newer Grimme), VV10 "
        "(van der Waals functional), or none. Critical for non-covalent "
        "interactions, large molecules, and molecular crystals."
    ),
    "solvent_model": (
        "Implicit or explicit solvation model. Implicit: PCM (polarizable "
        "continuum model), SMD (Truhlar solvation model), COSMO, COSMO-RS. "
        "Explicit: QM/MM, microsolvation. Specify solvent (water, DMSO, etc.) "
        "and dielectric constant if using implicit models."
    ),
    "force_field": (
        "Molecular mechanics force field for MD/MM calculations. Examples: "
        "AMBER (ff14SB, ff19SB for proteins; GAFF/GAFF2 for small molecules), "
        "CHARMM (CGenFF, CHARMM36m), OPLS-AA, AMOEBA (polarizable), "
        "ReaxFF (reactive). Specify water model (TIP3P, SPC/E, OPC, TIP4P-Ew)."
    ),
    "convergence_criteria": (
        "Numerical convergence thresholds. SCF convergence (energy change, "
        "density change), geometry optimization (max force, RMS force, max "
        "displacement, RMS displacement), and integral thresholds. Common: "
        "Gaussian tight/verytight, ORCA TightSCF/VeryTightSCF."
    ),
    "integration_grid": (
        "Numerical integration grid for DFT. Gaussian: UltraFine (99,590), "
        "SuperFine (175,974). ORCA: DefGrid2, DefGrid3. Q-Chem: SG-2, SG-3. "
        "Larger grids needed for meta-GGA functionals, weakly bound systems, "
        "and frequency calculations."
    ),
    "pseudopotential_ecp": (
        "Effective core potential / pseudopotential for heavy elements. "
        "Stuttgart/Cologne ECPs (SDD), LANL2DZ (Hay-Wadt), "
        "GTH pseudopotentials (CP2K/Quantum ESPRESSO), PAW (VASP). "
        "Specify which elements use ECPs and the small-core vs large-core choice."
    ),
    "thermodynamic_reference": (
        "Reference state for thermodynamic quantities. Standard: 298.15 K, "
        "1 atm (IUPAC). Specify: temperature, pressure, concentration standard "
        "(1 M for solution-phase), reference state for elements, and whether "
        "quasi-harmonic or quasi-RRHO corrections are applied (Grimme quasi-RRHO)."
    ),
    "unit_conventions": (
        "Unit system for reporting results. Energy: kcal/mol, kJ/mol, eV, "
        "Hartree, cm^-1. Distance: Angstrom, Bohr, pm. Angle: degrees, radians. "
        "Time: fs, ps. Pressure: atm, bar, GPa. Specify conversion factors "
        "for any non-standard units."
    ),
}

# -- Convention Validation --------------------------------------------------

# Common valid values for quick validation
CONVENTION_EXAMPLES: dict[str, list[str]] = {
    "basis_set": [
        "cc-pVDZ / cc-pVTZ / cc-pVQZ (Dunning)",
        "def2-SVP / def2-TZVP / def2-QZVPP (Ahlrichs)",
        "6-31G(d) / 6-311+G(d,p) / 6-311++G(2d,2p) (Pople)",
        "aug-cc-pVTZ (diffuse for anions/excited states)",
    ],
    "functional": [
        "B3LYP (general purpose hybrid)",
        "wB97X-D (range-separated + dispersion)",
        "PBE0 (parameter-free hybrid)",
        "M06-2X (thermochemistry, kinetics)",
        "CCSD(T) (gold standard wavefunction)",
    ],
    "dispersion_correction": [
        "D3(BJ) (recommended default)",
        "D4 (latest Grimme)",
        "VV10 (non-local vdW)",
        "none (not needed for methods with built-in dispersion)",
    ],
    "solvent_model": [
        "SMD (water, eps=78.39)",
        "PCM (IEFPCM, water)",
        "COSMO-RS (multi-solvent)",
        "gas phase (no solvation)",
    ],
    "unit_conventions": [
        "kcal/mol, Angstrom, degrees (common in biochemistry)",
        "kJ/mol, Angstrom, degrees (IUPAC/European convention)",
        "eV, Angstrom (solid state / materials science)",
        "Hartree, Bohr (atomic units)",
    ],
}


def get_field_description(field: str) -> str:
    """Get the description for a convention field."""
    return CONVENTION_DESCRIPTIONS.get(field, f"Convention field: {field}")


def get_field_examples(field: str) -> list[str]:
    """Get example values for a convention field."""
    return CONVENTION_EXAMPLES.get(field, [])


def list_all_fields() -> list[dict[str, Any]]:
    """List all convention fields with descriptions and examples."""
    return [
        {
            "field": f,
            "description": get_field_description(f),
            "examples": get_field_examples(f),
        }
        for f in CONVENTION_FIELDS
    ]


def check_conventions(engine: StateEngine) -> dict[str, Any]:
    """Check which conventions are locked and which are missing.

    Returns a report dict with locked, unlocked, and coverage stats.
    """
    state = engine.load()
    locked = {}
    unlocked = []

    for field in CONVENTION_FIELDS:
        if field in state.conventions:
            locked[field] = {
                "value": state.conventions[field].value,
                "locked_by": state.conventions[field].locked_by,
                "rationale": state.conventions[field].rationale,
            }
        else:
            unlocked.append(field)

    return {
        "locked": locked,
        "unlocked": unlocked,
        "coverage": f"{len(locked)}/{len(CONVENTION_FIELDS)}",
        "coverage_pct": round(100 * len(locked) / len(CONVENTION_FIELDS), 1)
        if CONVENTION_FIELDS
        else 100.0,
    }


def diff_conventions(
    engine: StateEngine,
    proposed: dict[str, str],
) -> dict[str, Any]:
    """Compare proposed convention values against current locks.

    Returns conflicts, new fields, and matching fields.
    """
    state = engine.load()
    conflicts = {}
    new_fields = {}
    matching = {}

    for field, proposed_value in proposed.items():
        if field in state.conventions:
            current = state.conventions[field].value
            if current != proposed_value:
                conflicts[field] = {
                    "current": current,
                    "proposed": proposed_value,
                }
            else:
                matching[field] = current
        else:
            new_fields[field] = proposed_value

    return {
        "conflicts": conflicts,
        "new_fields": new_fields,
        "matching": matching,
        "has_conflicts": bool(conflicts),
    }

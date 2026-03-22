"""Single source of truth for all directory/file names and environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


# -- Environment Variables --------------------------------------------------

ENV_GCD_HOME = "GCD_HOME"
ENV_GCD_PROJECT = "GCD_PROJECT"
ENV_GCD_INSTALL_DIR = "GCD_INSTALL_DIR"
ENV_GCD_DEBUG = "GCD_DEBUG"
ENV_GCD_AUTONOMY = "GCD_AUTONOMY"

# -- File Names -------------------------------------------------------------

STATE_MD = "STATE.md"
STATE_JSON = "state.json"
STATE_WRITE_INTENT = ".state-write-intent"
ROADMAP_MD = "ROADMAP.md"
CONFIG_JSON = "config.json"
CONVENTIONS_JSON = "conventions.json"

PLAN_PREFIX = "PLAN"
SUMMARY_PREFIX = "SUMMARY"
RESEARCH_MD = "RESEARCH.md"
RESEARCH_DIGEST_MD = "RESEARCH-DIGEST.md"
CONTINUE_HERE_MD = ".continue-here.md"

# -- Directory Names --------------------------------------------------------

GCD_DIR = ".gcd"
OBSERVABILITY_DIR = "observability"
SESSIONS_DIR = "sessions"
TRACES_DIR = "traces"
KNOWLEDGE_DIR = "knowledge"
PAPER_DIR = "paper"
SCRATCH_DIR = ".scratch"
CALCULATIONS_DIR = "calculations"

# -- Git --------------------------------------------------------------------

CHECKPOINT_TAG_PREFIX = "gcd-checkpoint"
COMMIT_PREFIX = "[gcd]"

# -- Autonomy Modes ---------------------------------------------------------

AUTONOMY_SUPERVISED = "supervised"
AUTONOMY_BALANCED = "balanced"
AUTONOMY_YOLO = "yolo"
VALID_AUTONOMY_MODES = {AUTONOMY_SUPERVISED, AUTONOMY_BALANCED, AUTONOMY_YOLO}

# -- Research Modes ---------------------------------------------------------

RESEARCH_EXPLORE = "explore"
RESEARCH_BALANCED = "balanced"
RESEARCH_EXPLOIT = "exploit"
RESEARCH_ADAPTIVE = "adaptive"
VALID_RESEARCH_MODES = {RESEARCH_EXPLORE, RESEARCH_BALANCED, RESEARCH_EXPLOIT, RESEARCH_ADAPTIVE}

# -- Model Tiers ------------------------------------------------------------

TIER_1 = "tier-1"  # Highest capability
TIER_2 = "tier-2"  # Balanced
TIER_3 = "tier-3"  # Fastest

# -- Verification Severity --------------------------------------------------

SEVERITY_CRITICAL = "CRITICAL"  # Blocks all downstream work
SEVERITY_MAJOR = "MAJOR"        # Must resolve before conclusions
SEVERITY_MINOR = "MINOR"        # Must resolve before publication
SEVERITY_NOTE = "NOTE"          # Informational

# -- Convention Lock Fields (Computational Chemistry) -----------------------

CONVENTION_FIELDS = [
    "basis_set",                  # cc-pVDZ, 6-311+G(d,p), def2-TZVP, etc.
    "functional",                 # B3LYP, PBE0, wB97X-D, CCSD(T), MP2, etc.
    "dispersion_correction",      # D3(BJ), D4, VV10, none, etc.
    "solvent_model",              # PCM, SMD, COSMO, explicit, gas phase, etc.
    "force_field",                # AMBER, CHARMM, OPLS-AA, GAFF, ReaxFF, etc.
    "convergence_criteria",       # SCF thresholds, geometry opt tolerances, etc.
    "integration_grid",           # UltraFine, SuperFine, (99,590), etc.
    "pseudopotential_ecp",        # Stuttgart, LANL2DZ, GTH, PAW, none, etc.
    "thermodynamic_reference",    # Standard state (298.15 K, 1 atm), reference energies
    "unit_conventions",           # kcal/mol, kJ/mol, eV, Hartree; Angstrom, Bohr, etc.
]

# -- Verification Checks ---------------------------------------------------

VERIFICATION_CHECKS = [
    "energy_conservation",        # Total energy stable across trajectory / consistent
    "geometry_convergence",       # Forces/displacements below thresholds
    "frequency_validation",       # No imaginary frequencies for minima, exactly one for TS
    "basis_set_convergence",      # Results stable with increasing basis set size
    "functional_sensitivity",     # Results consistent across reasonable functionals
    "symmetry_preservation",      # Point group / space group maintained where expected
    "thermodynamic_consistency",  # Free energies, enthalpies, entropies self-consistent
    "experimental_comparison",    # Results compared against experimental measurements
    "charge_conservation",        # Total charge and spin multiplicity preserved
    "sampling_adequacy",          # MD/MC sampling converged (autocorrelation, block averaging)
    "literature_benchmarks",      # Results compared with published computational benchmarks
    "reproducibility",            # Same inputs produce same outputs; seeds documented
]


@dataclass(frozen=True)
class ProjectLayout:
    """Resolved paths for a GCD project."""

    root: Path

    @property
    def gcd_dir(self) -> Path:
        return self.root / GCD_DIR

    @property
    def state_md(self) -> Path:
        return self.gcd_dir / STATE_MD

    @property
    def state_json(self) -> Path:
        return self.gcd_dir / STATE_JSON

    @property
    def state_write_intent(self) -> Path:
        return self.gcd_dir / STATE_WRITE_INTENT

    @property
    def roadmap_md(self) -> Path:
        return self.gcd_dir / ROADMAP_MD

    @property
    def config_json(self) -> Path:
        return self.gcd_dir / CONFIG_JSON

    @property
    def conventions_json(self) -> Path:
        return self.gcd_dir / CONVENTIONS_JSON

    @property
    def observability_dir(self) -> Path:
        return self.gcd_dir / OBSERVABILITY_DIR

    @property
    def sessions_dir(self) -> Path:
        return self.observability_dir / SESSIONS_DIR

    @property
    def traces_dir(self) -> Path:
        return self.gcd_dir / TRACES_DIR

    @property
    def knowledge_dir(self) -> Path:
        return self.root / KNOWLEDGE_DIR

    @property
    def paper_dir(self) -> Path:
        return self.root / PAPER_DIR

    @property
    def scratch_dir(self) -> Path:
        return self.root / SCRATCH_DIR

    @property
    def calculations_dir(self) -> Path:
        return self.root / CALCULATIONS_DIR

    @property
    def continue_here(self) -> Path:
        return self.gcd_dir / CONTINUE_HERE_MD

    def phase_dir(self, phase: str) -> Path:
        return self.root / f"phase-{phase}"

    def plan_path(self, phase: str, plan_number: str) -> Path:
        return self.phase_dir(phase) / f"{PLAN_PREFIX}-{plan_number}.md"

    def summary_path(self, phase: str, plan_number: str) -> Path:
        return self.phase_dir(phase) / f"{SUMMARY_PREFIX}-{plan_number}.md"

    def ensure_dirs(self) -> None:
        """Create all required directories."""
        for d in [
            self.gcd_dir,
            self.observability_dir,
            self.sessions_dir,
            self.traces_dir,
            self.knowledge_dir,
            self.scratch_dir,
            self.calculations_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)


def find_project_root(start: Path | None = None) -> Path:
    """Walk up from start (or cwd) looking for .gcd/ directory."""
    current = start or Path.cwd()
    while current != current.parent:
        if (current / GCD_DIR).is_dir():
            return current
        current = current.parent
    raise FileNotFoundError(
        f"No {GCD_DIR}/ directory found. Run 'gcd init' to create a project."
    )


def get_layout(start: Path | None = None) -> ProjectLayout:
    """Get the project layout, finding the root automatically."""
    env_project = os.environ.get(ENV_GCD_PROJECT)
    if env_project:
        return ProjectLayout(root=Path(env_project))
    return ProjectLayout(root=find_project_root(start))

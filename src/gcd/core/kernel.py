"""Content-addressed verification kernel.

Runs predicates over evidence registries and produces SHA-256 verdicts.
Adapted from GPD's kernel.py for computational chemistry verification.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from .constants import VERIFICATION_CHECKS, SEVERITY_CRITICAL, SEVERITY_MAJOR, SEVERITY_MINOR, SEVERITY_NOTE


class Severity(str, Enum):
    CRITICAL = SEVERITY_CRITICAL
    MAJOR = SEVERITY_MAJOR
    MINOR = SEVERITY_MINOR
    NOTE = SEVERITY_NOTE


@dataclass
class CheckResult:
    """Result of a single verification check."""

    check_id: str
    name: str
    status: str  # PASS | FAIL | SKIP | WARN
    severity: Severity
    message: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)
    suggestions: list[str] = field(default_factory=list)


@dataclass
class Verdict:
    """Complete verification verdict with content-addressed hashes."""

    registry_hash: str
    predicates_hash: str
    verdict_hash: str
    overall: str  # PASS | FAIL | PARTIAL
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    results: dict[str, CheckResult] = field(default_factory=dict)
    summary: str = ""

    @property
    def critical_failures(self) -> list[CheckResult]:
        return [
            r
            for r in self.results.values()
            if r.status == "FAIL" and r.severity == Severity.CRITICAL
        ]

    @property
    def major_failures(self) -> list[CheckResult]:
        return [
            r
            for r in self.results.values()
            if r.status == "FAIL" and r.severity == Severity.MAJOR
        ]

    @property
    def all_failures(self) -> list[CheckResult]:
        return [r for r in self.results.values() if r.status == "FAIL"]

    @property
    def pass_count(self) -> int:
        return sum(1 for r in self.results.values() if r.status == "PASS")

    @property
    def fail_count(self) -> int:
        return sum(1 for r in self.results.values() if r.status == "FAIL")

    def to_dict(self) -> dict[str, Any]:
        return {
            "registry_hash": self.registry_hash,
            "predicates_hash": self.predicates_hash,
            "verdict_hash": self.verdict_hash,
            "overall": self.overall,
            "timestamp": self.timestamp,
            "summary": self.summary,
            "results": {
                k: {
                    "check_id": v.check_id,
                    "name": v.name,
                    "status": v.status,
                    "severity": v.severity.value,
                    "message": v.message,
                    "evidence": v.evidence,
                    "suggestions": v.suggestions,
                }
                for k, v in self.results.items()
            },
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# -- Predicate Type ---------------------------------------------------------

# A predicate takes an evidence registry and returns a CheckResult
Predicate = Callable[[dict[str, Any]], CheckResult]


# -- Built-in Computational Chemistry Predicates ----------------------------

def check_energy_conservation(evidence: dict[str, Any]) -> CheckResult:
    """Check total energy stability across trajectory or calculation steps."""
    energy_values = evidence.get("energy_values", [])
    energy_drift = evidence.get("energy_drift", None)
    drift_threshold = evidence.get("drift_threshold", 1e-6)  # Hartree

    if not energy_values:
        return CheckResult(
            check_id="energy_conservation",
            name="Energy Conservation",
            status="SKIP",
            severity=Severity.CRITICAL,
            message="No energy values provided for verification.",
        )

    if energy_drift is not None and abs(energy_drift) > drift_threshold:
        return CheckResult(
            check_id="energy_conservation",
            name="Energy Conservation",
            status="FAIL",
            severity=Severity.CRITICAL,
            message=f"Energy drift {energy_drift:.2e} exceeds threshold {drift_threshold:.2e}.",
            evidence={"drift": energy_drift, "threshold": drift_threshold},
            suggestions=[
                "Reduce MD timestep.",
                "Check thermostat/barostat coupling parameters.",
                "Verify SCF convergence at each step.",
            ],
        )

    return CheckResult(
        check_id="energy_conservation",
        name="Energy Conservation",
        status="PASS",
        severity=Severity.CRITICAL,
        message=f"Energy stable across {len(energy_values)} data points.",
    )


def check_geometry_convergence(evidence: dict[str, Any]) -> CheckResult:
    """Check that geometry optimization converged properly."""
    converged = evidence.get("geometry_converged", None)
    max_force = evidence.get("max_force", None)
    rms_force = evidence.get("rms_force", None)
    max_displacement = evidence.get("max_displacement", None)
    rms_displacement = evidence.get("rms_displacement", None)
    force_threshold = evidence.get("force_threshold", 4.5e-4)  # Hartree/Bohr

    if converged is None:
        return CheckResult(
            check_id="geometry_convergence",
            name="Geometry Convergence",
            status="SKIP",
            severity=Severity.CRITICAL,
            message="No geometry convergence data provided.",
        )

    if not converged:
        return CheckResult(
            check_id="geometry_convergence",
            name="Geometry Convergence",
            status="FAIL",
            severity=Severity.CRITICAL,
            message="Geometry optimization did not converge.",
            evidence={
                "max_force": max_force,
                "rms_force": rms_force,
                "max_displacement": max_displacement,
                "rms_displacement": rms_displacement,
            },
            suggestions=[
                "Increase maximum optimization steps.",
                "Try a different optimization algorithm (e.g., RFO, GDIIS).",
                "Check for nearly degenerate electronic states.",
                "Use a better initial geometry.",
            ],
        )

    return CheckResult(
        check_id="geometry_convergence",
        name="Geometry Convergence",
        status="PASS",
        severity=Severity.CRITICAL,
        message="Geometry optimization converged within thresholds.",
    )


def check_frequency_validation(evidence: dict[str, Any]) -> CheckResult:
    """Check vibrational frequencies for proper characterization."""
    frequencies = evidence.get("frequencies", [])
    structure_type = evidence.get("structure_type", "minimum")  # minimum | ts
    imaginary_frequencies = evidence.get("imaginary_frequencies", [])

    if not frequencies:
        return CheckResult(
            check_id="frequency_validation",
            name="Frequency Validation",
            status="SKIP",
            severity=Severity.CRITICAL,
            message="No frequency data provided.",
        )

    n_imaginary = len(imaginary_frequencies)

    if structure_type == "minimum" and n_imaginary > 0:
        return CheckResult(
            check_id="frequency_validation",
            name="Frequency Validation",
            status="FAIL",
            severity=Severity.CRITICAL,
            message=f"Minimum has {n_imaginary} imaginary frequency(ies). Expected 0.",
            evidence={"imaginary": imaginary_frequencies},
            suggestions=[
                "Re-optimize geometry with tighter convergence criteria.",
                "Displace along imaginary mode and re-optimize.",
                "Use a finer integration grid.",
            ],
        )

    if structure_type == "ts" and n_imaginary != 1:
        return CheckResult(
            check_id="frequency_validation",
            name="Frequency Validation",
            status="FAIL",
            severity=Severity.CRITICAL,
            message=f"Transition state has {n_imaginary} imaginary frequency(ies). Expected exactly 1.",
            evidence={"imaginary": imaginary_frequencies},
            suggestions=[
                "Verify the TS structure connects the correct reactant/product.",
                "Re-optimize with a TS-specific algorithm (e.g., Berny, dimer method).",
            ],
        )

    return CheckResult(
        check_id="frequency_validation",
        name="Frequency Validation",
        status="PASS",
        severity=Severity.CRITICAL,
        message=f"Frequency analysis correct for {structure_type}: {len(frequencies)} modes, {n_imaginary} imaginary.",
    )


def check_basis_set_convergence(evidence: dict[str, Any]) -> CheckResult:
    """Check that results are converged with respect to basis set size."""
    basis_set_series = evidence.get("basis_set_series", [])
    energy_differences = evidence.get("basis_set_energy_diffs", [])
    convergence_threshold = evidence.get("basis_convergence_threshold", 1.0)  # kcal/mol

    if not basis_set_series or len(basis_set_series) < 2:
        return CheckResult(
            check_id="basis_set_convergence",
            name="Basis Set Convergence",
            status="WARN",
            severity=Severity.MAJOR,
            message="Fewer than 2 basis sets tested; convergence not assessed.",
            suggestions=[
                "Run calculations with at least DZ, TZ, QZ basis sets.",
                "Consider CBS extrapolation for high-accuracy work.",
            ],
        )

    if energy_differences and any(abs(d) > convergence_threshold for d in energy_differences):
        return CheckResult(
            check_id="basis_set_convergence",
            name="Basis Set Convergence",
            status="FAIL",
            severity=Severity.MAJOR,
            message="Results not converged with respect to basis set.",
            evidence={
                "basis_sets": basis_set_series,
                "energy_diffs_kcal": energy_differences,
            },
            suggestions=[
                "Use a larger basis set.",
                "Apply CBS extrapolation.",
                "Add diffuse functions if anionic species are involved.",
            ],
        )

    return CheckResult(
        check_id="basis_set_convergence",
        name="Basis Set Convergence",
        status="PASS",
        severity=Severity.MAJOR,
        message=f"Basis set converged across {len(basis_set_series)} sets.",
    )


def check_functional_sensitivity(evidence: dict[str, Any]) -> CheckResult:
    """Check results are consistent across reasonable functionals."""
    functionals_tested = evidence.get("functionals_tested", [])
    functional_energies = evidence.get("functional_energies", {})
    spread_threshold = evidence.get("functional_spread_threshold", 3.0)  # kcal/mol

    if not functionals_tested or len(functionals_tested) < 2:
        return CheckResult(
            check_id="functional_sensitivity",
            name="Functional Sensitivity",
            status="WARN",
            severity=Severity.MAJOR,
            message="Fewer than 2 functionals tested; sensitivity not assessed.",
            suggestions=[
                "Test with at least a GGA, hybrid, and range-separated hybrid.",
                "Include a dispersion-corrected functional if non-covalent interactions matter.",
            ],
        )

    if functional_energies:
        values = list(functional_energies.values())
        spread = max(values) - min(values) if values else 0
        if spread > spread_threshold:
            return CheckResult(
                check_id="functional_sensitivity",
                name="Functional Sensitivity",
                status="FAIL",
                severity=Severity.MAJOR,
                message=f"Functional spread {spread:.1f} kcal/mol exceeds threshold {spread_threshold:.1f}.",
                evidence={"functionals": functional_energies, "spread": spread},
                suggestions=[
                    "Use a higher-level reference method (CCSD(T), DLPNO-CCSD(T)).",
                    "Consider multi-reference methods if spread is large.",
                ],
            )

    return CheckResult(
        check_id="functional_sensitivity",
        name="Functional Sensitivity",
        status="PASS",
        severity=Severity.MAJOR,
        message=f"Results consistent across {len(functionals_tested)} functionals.",
    )


def check_symmetry_preservation(evidence: dict[str, Any]) -> CheckResult:
    """Check that molecular/crystal symmetry is preserved where expected."""
    expected_symmetry = evidence.get("expected_symmetry", None)
    actual_symmetry = evidence.get("actual_symmetry", None)
    symmetry_broken = evidence.get("symmetry_broken", False)

    if expected_symmetry is None:
        return CheckResult(
            check_id="symmetry_preservation",
            name="Symmetry Preservation",
            status="SKIP",
            severity=Severity.MAJOR,
            message="No symmetry expectations specified.",
        )

    if symmetry_broken or (actual_symmetry and actual_symmetry != expected_symmetry):
        return CheckResult(
            check_id="symmetry_preservation",
            name="Symmetry Preservation",
            status="FAIL",
            severity=Severity.MAJOR,
            message=f"Symmetry broken: expected {expected_symmetry}, got {actual_symmetry}.",
            evidence={"expected": expected_symmetry, "actual": actual_symmetry},
            suggestions=[
                "Check for Jahn-Teller distortion.",
                "Verify initial structure had correct symmetry.",
                "Consider whether symmetry breaking is physically meaningful.",
            ],
        )

    return CheckResult(
        check_id="symmetry_preservation",
        name="Symmetry Preservation",
        status="PASS",
        severity=Severity.MAJOR,
        message=f"Symmetry {expected_symmetry} preserved.",
    )


def check_thermodynamic_consistency(evidence: dict[str, Any]) -> CheckResult:
    """Check that free energies, enthalpies, and entropies are self-consistent."""
    has_thermo = evidence.get("thermodynamic_data", False)
    g_h_ts_consistent = evidence.get("g_equals_h_minus_ts", None)
    reference_state = evidence.get("reference_state_specified", False)

    if not has_thermo:
        return CheckResult(
            check_id="thermodynamic_consistency",
            name="Thermodynamic Consistency",
            status="SKIP",
            severity=Severity.MAJOR,
            message="No thermodynamic data to verify.",
        )

    issues = []
    if not reference_state:
        issues.append("Thermodynamic reference state not specified.")
    if g_h_ts_consistent is False:
        issues.append("G != H - TS relationship violated.")

    if issues:
        return CheckResult(
            check_id="thermodynamic_consistency",
            name="Thermodynamic Consistency",
            status="FAIL",
            severity=Severity.MAJOR,
            message=f"Thermodynamic inconsistencies: {'; '.join(issues)}",
            evidence={"issues": issues},
            suggestions=[
                "Verify temperature and pressure match across all calculations.",
                "Check that thermal corrections use the same level of theory.",
                "Ensure consistent reference state (298.15 K, 1 atm standard).",
            ],
        )

    return CheckResult(
        check_id="thermodynamic_consistency",
        name="Thermodynamic Consistency",
        status="PASS",
        severity=Severity.MAJOR,
        message="Thermodynamic quantities self-consistent.",
    )


def check_experimental_comparison(evidence: dict[str, Any]) -> CheckResult:
    """Check results against experimental measurements."""
    experimental_data = evidence.get("experimental_values", {})
    computed_data = evidence.get("computed_values", {})
    deviations = evidence.get("deviations_from_experiment", {})
    acceptable_deviation = evidence.get("acceptable_deviation", None)

    if not experimental_data:
        return CheckResult(
            check_id="experimental_comparison",
            name="Experimental Comparison",
            status="WARN",
            severity=Severity.MAJOR,
            message="No experimental data available for comparison.",
            suggestions=[
                "Search literature for experimental measurements.",
                "Note lack of experimental validation in manuscript.",
            ],
        )

    large_deviations = {
        k: v for k, v in deviations.items()
        if acceptable_deviation and abs(v) > acceptable_deviation
    }

    if large_deviations:
        return CheckResult(
            check_id="experimental_comparison",
            name="Experimental Comparison",
            status="FAIL",
            severity=Severity.MAJOR,
            message=f"{len(large_deviations)} property(ies) deviate significantly from experiment.",
            evidence={"deviations": large_deviations},
            suggestions=[
                "Check level of theory is appropriate for this property.",
                "Consider systematic error sources (BSSE, thermal corrections, solvation).",
                "Verify experimental conditions match computational model.",
            ],
        )

    return CheckResult(
        check_id="experimental_comparison",
        name="Experimental Comparison",
        status="PASS",
        severity=Severity.MAJOR,
        message=f"Results agree with {len(experimental_data)} experimental value(s).",
    )


def check_charge_conservation(evidence: dict[str, Any]) -> CheckResult:
    """Check that total charge and spin multiplicity are preserved."""
    expected_charge = evidence.get("expected_charge", None)
    actual_charge = evidence.get("actual_charge", None)
    expected_multiplicity = evidence.get("expected_multiplicity", None)
    actual_multiplicity = evidence.get("actual_multiplicity", None)
    spin_contamination = evidence.get("spin_contamination", None)
    spin_contamination_threshold = evidence.get("spin_contamination_threshold", 0.1)

    if expected_charge is None:
        return CheckResult(
            check_id="charge_conservation",
            name="Charge Conservation",
            status="SKIP",
            severity=Severity.CRITICAL,
            message="No charge/multiplicity data provided.",
        )

    issues = []
    if actual_charge is not None and actual_charge != expected_charge:
        issues.append(f"Charge mismatch: expected {expected_charge}, got {actual_charge}")
    if actual_multiplicity is not None and actual_multiplicity != expected_multiplicity:
        issues.append(f"Multiplicity mismatch: expected {expected_multiplicity}, got {actual_multiplicity}")
    if spin_contamination is not None and spin_contamination > spin_contamination_threshold:
        issues.append(f"Spin contamination <S^2> deviation = {spin_contamination:.4f}")

    if issues:
        return CheckResult(
            check_id="charge_conservation",
            name="Charge Conservation",
            status="FAIL",
            severity=Severity.CRITICAL,
            message=f"Charge/spin issues: {'; '.join(issues)}",
            evidence={"issues": issues},
            suggestions=[
                "Verify input charge and multiplicity.",
                "Use restricted methods if spin contamination is large.",
                "Consider ROHF/ROCIS for open-shell systems.",
            ],
        )

    return CheckResult(
        check_id="charge_conservation",
        name="Charge Conservation",
        status="PASS",
        severity=Severity.CRITICAL,
        message="Charge and spin multiplicity consistent.",
    )


def check_sampling_adequacy(evidence: dict[str, Any]) -> CheckResult:
    """Check that MD/MC sampling is converged."""
    sampling_method = evidence.get("sampling_method", None)  # MD | MC | metadynamics
    autocorrelation_time = evidence.get("autocorrelation_time", None)
    simulation_length = evidence.get("simulation_length", None)
    block_averaging_error = evidence.get("block_averaging_error", None)
    error_threshold = evidence.get("sampling_error_threshold", None)

    if sampling_method is None:
        return CheckResult(
            check_id="sampling_adequacy",
            name="Sampling Adequacy",
            status="SKIP",
            severity=Severity.MAJOR,
            message="No sampling-based calculation to verify.",
        )

    issues = []
    if autocorrelation_time and simulation_length:
        n_independent = simulation_length / autocorrelation_time
        if n_independent < 100:
            issues.append(f"Only ~{n_independent:.0f} independent samples (need >100).")

    if block_averaging_error and error_threshold and block_averaging_error > error_threshold:
        issues.append(f"Block averaging error {block_averaging_error:.4f} exceeds threshold {error_threshold:.4f}.")

    if issues:
        return CheckResult(
            check_id="sampling_adequacy",
            name="Sampling Adequacy",
            status="FAIL",
            severity=Severity.MAJOR,
            message=f"Sampling issues: {'; '.join(issues)}",
            evidence={"issues": issues},
            suggestions=[
                "Extend simulation length.",
                "Use enhanced sampling (replica exchange, metadynamics).",
                "Check for trapping in local minima.",
            ],
        )

    return CheckResult(
        check_id="sampling_adequacy",
        name="Sampling Adequacy",
        status="PASS",
        severity=Severity.MAJOR,
        message=f"Sampling adequate for {sampling_method} calculation.",
    )


def check_literature_benchmarks(evidence: dict[str, Any]) -> CheckResult:
    """Check results against published computational benchmarks."""
    benchmarks_checked = evidence.get("literature_benchmarks_checked", [])
    benchmark_mismatches = evidence.get("benchmark_mismatches", [])

    if not benchmarks_checked:
        return CheckResult(
            check_id="literature_benchmarks",
            name="Literature Benchmarks",
            status="WARN",
            severity=Severity.MAJOR,
            message="No literature benchmarks checked.",
            suggestions=[
                "Search for published benchmark studies on similar systems.",
                "Compare with GMTKN55, S22, or other standard benchmark sets.",
            ],
        )

    if benchmark_mismatches:
        return CheckResult(
            check_id="literature_benchmarks",
            name="Literature Benchmarks",
            status="FAIL",
            severity=Severity.MAJOR,
            message=f"Results disagree with {len(benchmark_mismatches)} literature benchmark(s).",
            evidence={"mismatches": benchmark_mismatches},
        )

    return CheckResult(
        check_id="literature_benchmarks",
        name="Literature Benchmarks",
        status="PASS",
        severity=Severity.MAJOR,
        message=f"Consistent with {len(benchmarks_checked)} literature benchmark(s).",
    )


def check_reproducibility(evidence: dict[str, Any]) -> CheckResult:
    """Check that calculations are reproducible."""
    inputs_documented = evidence.get("inputs_documented", False)
    software_version = evidence.get("software_version", None)
    random_seeds = evidence.get("random_seeds_documented", False)
    reproduced = evidence.get("reproduced_independently", None)

    issues = []
    if not inputs_documented:
        issues.append("Input files/parameters not fully documented.")
    if not software_version:
        issues.append("Software version not specified.")
    if not random_seeds:
        issues.append("Random seeds not documented (relevant for MD/MC).")

    if reproduced is False:
        return CheckResult(
            check_id="reproducibility",
            name="Reproducibility",
            status="FAIL",
            severity=Severity.CRITICAL,
            message="Independent reproduction attempt failed.",
            evidence={"issues": issues},
        )

    if issues:
        return CheckResult(
            check_id="reproducibility",
            name="Reproducibility",
            status="WARN",
            severity=Severity.MINOR,
            message=f"Reproducibility concerns: {'; '.join(issues)}",
            evidence={"issues": issues},
            suggestions=[
                "Document all input parameters and software versions.",
                "Save input files alongside outputs.",
                "Record random seeds for stochastic methods.",
            ],
        )

    return CheckResult(
        check_id="reproducibility",
        name="Reproducibility",
        status="PASS",
        severity=Severity.MINOR,
        message="Calculation fully documented and reproducible.",
    )


# -- Default predicate registry ---------------------------------------------

DEFAULT_PREDICATES: dict[str, Predicate] = {
    "energy_conservation": check_energy_conservation,
    "geometry_convergence": check_geometry_convergence,
    "frequency_validation": check_frequency_validation,
    "basis_set_convergence": check_basis_set_convergence,
    "functional_sensitivity": check_functional_sensitivity,
    "symmetry_preservation": check_symmetry_preservation,
    "thermodynamic_consistency": check_thermodynamic_consistency,
    "experimental_comparison": check_experimental_comparison,
    "charge_conservation": check_charge_conservation,
    "sampling_adequacy": check_sampling_adequacy,
    "literature_benchmarks": check_literature_benchmarks,
    "reproducibility": check_reproducibility,
}


# -- Verification Kernel ----------------------------------------------------

class VerificationKernel:
    """Content-addressed verification kernel.

    Runs predicates over evidence registries and produces
    SHA-256 verdicts for reproducibility and tamper-evidence.
    """

    def __init__(self, predicates: dict[str, Predicate] | None = None):
        self.predicates = predicates or dict(DEFAULT_PREDICATES)

    def _hash(self, data: str) -> str:
        return f"sha256:{hashlib.sha256(data.encode()).hexdigest()}"

    def verify(self, evidence: dict[str, Any]) -> Verdict:
        """Run all predicates against evidence and produce a verdict."""
        # Hash inputs
        evidence_json = json.dumps(evidence, sort_keys=True, default=str)
        registry_hash = self._hash(evidence_json)

        predicate_names = json.dumps(sorted(self.predicates.keys()))
        predicates_hash = self._hash(predicate_names)

        # Run predicates
        results: dict[str, CheckResult] = {}
        for check_id, predicate in self.predicates.items():
            try:
                result = predicate(evidence)
                results[check_id] = result
            except Exception as e:
                results[check_id] = CheckResult(
                    check_id=check_id,
                    name=check_id.replace("_", " ").title(),
                    status="FAIL",
                    severity=Severity.MAJOR,
                    message=f"Predicate raised exception: {e}",
                )

        # Determine overall status
        has_critical_fail = any(
            r.status == "FAIL" and r.severity == Severity.CRITICAL
            for r in results.values()
        )
        has_major_fail = any(
            r.status == "FAIL" and r.severity == Severity.MAJOR
            for r in results.values()
        )

        if has_critical_fail:
            overall = "FAIL"
        elif has_major_fail:
            overall = "PARTIAL"
        else:
            overall = "PASS"

        # Hash the results for tamper-evidence
        results_json = json.dumps(
            {k: v.message for k, v in results.items()},
            sort_keys=True,
        )
        verdict_hash = self._hash(
            f"{registry_hash}:{predicates_hash}:{results_json}"
        )

        # Build summary
        pass_count = sum(1 for r in results.values() if r.status == "PASS")
        fail_count = sum(1 for r in results.values() if r.status == "FAIL")
        skip_count = sum(1 for r in results.values() if r.status == "SKIP")
        warn_count = sum(1 for r in results.values() if r.status == "WARN")

        summary = (
            f"{overall}: {pass_count} passed, {fail_count} failed, "
            f"{warn_count} warnings, {skip_count} skipped "
            f"out of {len(results)} checks."
        )

        return Verdict(
            registry_hash=registry_hash,
            predicates_hash=predicates_hash,
            verdict_hash=verdict_hash,
            overall=overall,
            results=results,
            summary=summary,
        )

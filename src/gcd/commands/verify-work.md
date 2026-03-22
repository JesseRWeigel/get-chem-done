---
name: verify-work
description: Run the 12-check computational chemistry verification framework
---

<process>

## Verify Work

### Overview
Run post-hoc verification on completed phase work using the 12-check framework.

### Step 1: Collect Artifacts
Gather all output from the current phase:
- Calculation output files and logs
- Extracted results (energies, geometries, properties)
- SUMMARY files from executors

### Step 2: Build Evidence Registry
Extract verification evidence from artifacts:
- Energy values and convergence data
- Geometry optimization convergence metrics
- Vibrational frequencies
- Charge and spin multiplicity information
- Basis set and functional test results
- Experimental comparison data

### Step 3: Run Verification
Spawn gcd-verifier with:
- All phase artifacts
- Evidence registry
- Convention locks
- LLM error catalog

### Step 4: Process Verdict
Parse the VERIFICATION-REPORT.md:
- If PASS: record in state, proceed
- If PARTIAL: create targeted gap-closure for MAJOR failures
- If FAIL: create gap-closure for CRITICAL failures, block downstream

### Step 5: Route Failures
For each failure, route to the appropriate agent:
- Convergence failures — gcd-executor (re-optimize with adjusted settings)
- Basis set issues — gcd-executor (rerun with larger basis)
- Convention drift — convention resolution
- Experimental disagreement — gcd-researcher + gcd-analyst
- Sampling issues — gcd-executor (extend simulation)

### Step 6: Update State
Record verification results in STATE.md:
- Verdict hash (content-addressed)
- Pass/fail counts
- Any unresolved issues

</process>

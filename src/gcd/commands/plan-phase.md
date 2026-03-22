---
name: plan-phase
description: Plan the current phase — research, plan, and validate before execution
---

<process>

## Plan Phase

### Overview
Before execution, create validated plans for the current phase:
1. Research the domain (gcd-researcher)
2. Create plans (gcd-planner)
3. Validate plans (gcd-analyst)
4. Iterate until plans pass validation

### Step 1: Domain Research
Spawn gcd-researcher with:
- Phase goal from ROADMAP.md
- Current convention locks
- Research mode parameters

Collect RESEARCH.md output.

### Step 2: Plan Creation
Spawn gcd-planner with:
- Phase goal
- RESEARCH.md findings
- Convention locks
- Task sizing constraints (max 8-10 tasks per plan)

Collect PLAN-XX-YY.md files.

### Step 3: Plan Validation
For each plan, spawn gcd-analyst with:
- The PLAN.md
- Phase goal
- RESEARCH.md
- LLM error catalog

### Step 4: Revision Loop
If analyst returns REVISE:
1. Feed revision recommendations back to gcd-planner
2. Planner revises the plan
3. Re-check with analyst
4. Maximum 3 iterations

If analyst returns REJECT after 3 iterations:
- Present issues to user
- Ask for guidance on approach

### Step 5: Commit and Present
Once plans are validated:
1. Commit all PLAN.md files
2. Display plan summary to user
3. Show wave structure (what runs in parallel)
4. If autonomy is 'supervised': wait for user approval
5. If autonomy is 'balanced' or 'yolo': proceed to execute-phase

</process>

# Molecular Docking Protocols

> Step-by-step methodology guides for computational drug discovery workflows.

## Protocol: Protein-Ligand Docking

### When to Use
Predicting the binding mode and affinity of small molecules to a protein target for hit identification or lead optimization.

### Steps
1. **Prepare the protein structure** — obtain from PDB; remove crystallographic waters (except conserved active-site waters), add hydrogens, assign protonation states at physiological pH (PropKa, H++), minimize steric clashes
2. **Define the binding site** — use the co-crystallized ligand position, or identify the site from cavity detection (fpocket, SiteMap) or literature; set the grid box to encompass the site with 5–10 Å buffer
3. **Prepare the ligand(s)** — generate 3D coordinates, assign protonation states, enumerate tautomers and relevant stereoisomers, generate conformers (OMEGA, RDKit)
4. **Select the docking program** — AutoDock Vina (fast, good for virtual screening), Glide (standard/SP/XP modes, Schrodinger), GOLD (flexible scoring functions), or DOCK (historical)
5. **Run re-docking validation** — re-dock the co-crystallized ligand; RMSD < 2.0 Å to the experimental pose validates the docking setup
6. **Dock the ligands** — rigid receptor (standard) or flexible receptor (induced fit docking for flexible binding sites); generate 5–10 poses per ligand
7. **Score and rank** — use the docking score for initial ranking; re-score top hits with MM-GBSA, MM-PBSA, or a consensus of multiple scoring functions for improved ranking
8. **Visual inspection** — examine top-ranked poses for chemically reasonable interactions (hydrogen bonds, hydrophobic contacts, salt bridges); discard poses with steric clashes or unrealistic conformations

### Common LLM Pitfalls
- Skipping re-docking validation (if the program cannot reproduce the known pose, results are unreliable)
- Trusting docking scores as binding affinities (docking scores are rank-ordering tools, not ΔG predictors; typical R² to experimental affinity is 0.3–0.5)
- Ignoring protein flexibility when the binding site is known to be flexible (use ensemble docking or induced fit)
- Not enumerating protonation states and tautomers (wrong protonation can completely change the docking result)

---

## Protocol: Virtual Screening Workflow

### When to Use
Screening large compound libraries (10⁴–10⁷) to identify potential hits before experimental testing.

### Steps
1. **Define the target and criteria** — known binding site, desired selectivity profile, drug-likeness requirements
2. **Pre-filter the library** — apply drug-likeness filters (Lipinski Ro5: MW ≤ 500, LogP ≤ 5, HBD ≤ 5, HBA ≤ 10), PAINS filters (frequent hitters), and reactive group filters
3. **Run ligand-based pre-screening** (if known actives exist) — pharmacophore modeling, shape-based screening (ROCS), or fingerprint similarity (Tanimoto ≥ 0.3 to known actives) to reduce the library to 10⁴–10⁵
4. **Run structure-based docking** — dock the filtered library; use fast scoring (Vina, Glide SP) for primary screen
5. **Apply a score cutoff and cluster** — select the top 1–5% by score; cluster by chemical scaffold (Tanimoto, Murcko scaffold) to ensure diversity
6. **Re-score top hits** — re-dock with higher accuracy settings (Glide XP, flexible receptor) and/or re-score with MM-GBSA
7. **Visual inspection and expert filtering** — manually examine the top 100–500 poses; remove false positives with physically unreasonable binding modes
8. **Select for experimental testing** — choose 20–100 diverse compounds for in vitro assay (IC₅₀, K_d); aim for a hit rate of 5–30%

### Common LLM Pitfalls
- Not applying PAINS and reactive group filters (leads to false positives that are promiscuous binders)
- Selecting all top-scoring compounds without ensuring chemical diversity (results in redundant hits from one scaffold)
- Relying solely on docking scores without visual inspection (high-scoring poses can be physically unreasonable)
- Expecting hit rates above 50% (typical virtual screening hit rates are 5–30%; this is a filter, not a guarantee)

---

## Protocol: Scoring Function Evaluation

### When to Use
Selecting and validating scoring functions for docking or virtual screening accuracy.

### Steps
1. **Define the evaluation metrics** — pose prediction accuracy (RMSD < 2.0 Å, success rate), binding affinity ranking (Spearman/Kendall correlation with experimental IC₅₀/K_d), and enrichment (EF at 1%, 5%, AUROC)
2. **Assemble a benchmark set** — use curated datasets: PDBbind (binding affinity), DUD-E (decoys for enrichment), CASF (comprehensive assessment)
3. **Test pose prediction** — re-dock co-crystallized ligands; report success rate (% with RMSD < 2.0 Å) and median RMSD
4. **Test scoring/ranking** — score known actives and rank by predicted affinity; compute Pearson/Spearman correlation with experimental binding data
5. **Test enrichment** — screen actives mixed with decoys; compute enrichment factors and ROC curves; EF₁% > 10 is good for virtual screening
6. **Use consensus scoring** — combine rankings from 2–3 independent scoring functions (e.g., Vina + Glide + ChemPLP); consensus typically outperforms any single function
7. **Assess domain applicability** — scoring functions perform differently for different target classes (kinases, GPCRs, proteases); validate on your specific target class
8. **Report limitations** — no scoring function reliably predicts absolute binding affinity; report what the function is validated for (pose prediction vs ranking vs enrichment)

### Common LLM Pitfalls
- Using a single metric (e.g., only AUROC) to evaluate a scoring function (need pose accuracy, ranking, and enrichment)
- Validating on the training set of the scoring function (benchmark must be independent)
- Expecting scoring functions to predict absolute ΔG values (they are parameterized for ranking, not absolute prediction)
- Not testing on the specific target class of interest (a function that works well for kinases may fail for GPCRs)

---

## Protocol: ADMET Prediction

### When to Use
Predicting Absorption, Distribution, Metabolism, Excretion, and Toxicity properties of drug candidates in silico.

### Steps
1. **Compute physicochemical properties** — MW, LogP (cLogP, XLogP), HBD, HBA, PSA (topological polar surface area), rotatable bonds; check Lipinski Ro5, Veber rules (PSA ≤ 140 Å², rotatable bonds ≤ 10)
2. **Predict absorption** — oral bioavailability: Caco-2 permeability models, PAMPA prediction, P-gp substrate likelihood; check the "rule of 3" for fragment hits
3. **Predict distribution** — plasma protein binding (PPB), blood-brain barrier permeability (LogBB, CNS MPO score for CNS drugs), volume of distribution (Vd)
4. **Predict metabolism** — CYP450 inhibition/substrate prediction (CYP3A4, 2D6, 2C9, 2C19, 1A2); metabolic stability (intrinsic clearance from microsomes/hepatocytes); identify metabolic soft spots using site-of-metabolism prediction (SMARTCyp, P450 site of metabolism models)
5. **Predict excretion** — renal clearance, half-life estimation from clearance and Vd: t½ = 0.693 × Vd / CL
6. **Predict toxicity** — hERG liability (cardiac toxicity), Ames mutagenicity, hepatotoxicity (DILI), phototoxicity; use models like Derek Nexus, ProTox, or ADMET-AI
7. **Flag liabilities** — create a traffic-light summary: green (favorable), yellow (moderate risk), red (likely problematic) for each ADMET endpoint
8. **Prioritize compounds** — rank by multi-parameter optimization (MPO) score combining potency, selectivity, and ADMET profile

### Common LLM Pitfalls
- Treating in silico ADMET predictions as definitive (they are screening tools with typical accuracies of 70–85%; experimental validation is required)
- Applying Lipinski's rules rigidly to biologics, natural products, or "beyond rule of 5" chemical space
- Ignoring metabolic soft spots that can be addressed by medicinal chemistry (e.g., blocking metabolically labile positions)
- Not considering species differences in metabolism when translating from animal models to human predictions

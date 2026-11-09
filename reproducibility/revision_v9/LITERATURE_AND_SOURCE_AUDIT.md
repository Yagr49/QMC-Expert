# Literature and source audit — 11 October 2026

All four Desktop `Veresh_` folders were inventoried in `veresh_inventory.json`.
Library/dependency directories were excluded from the research inventory.

| Folder | Contribution to this revision |
|---|---|
| Veresh_Dataset_Paper | Publication-ready QMR workbook; endpoint qualifiers, organism/strain metadata, original numerical MIC records; stratified MIC audit |
| Veresh_Paper_Dataset | Earlier 13,404-row, 38-column raw workbook; a historical version of the same corpus, not another independent dataset |
| Veresh_paper | Earlier raw 13,404-row workbook, trained encoders, target and OOD structures/measurements, previous chemistry manuscripts |
| Veresh_paper_Mendeley | Standardised target, Q-HERO and ILToxDB tables; paired transfer outputs; quantitative endpoint/provenance and replicate audits; frozen-representation benchmarks |

The three raw/published QMR books are versions of one collection. They cannot be
counted as three independent quantitative datasets. In the new experiment, pooled MIC,
organism-matched exact MIC, and quantitative mammalian-cell cytotoxicity are genuinely
different supervision definitions; pooled and matched MIC still derive from QMR.
Q-HERO remains an external antibacterial evaluation collection.

## Causal claim audit

The Mendeley draft states that provenance homogeneity determines transfer and treats
the Q-HERO/QMR comparison as varying provenance alone. Endpoint identity and chemical
similarity do not control source selection, strain composition, chemical distribution,
sample size, aggregation, conflicting-label filtering or assay protocols. That contrast
is observational and cannot isolate provenance causally.

The archive also contains evidence against a blanket inter-laboratory-noise explanation:
`outputs/qmr_label_noise.csv` reports 38 same-compound/same-strain replicate strata;
the more detailed `qmr_noise_ladder.json` clarifies that these span only 23 compounds
and five strains. Median log2 range is zero and 94.7% are within one dilution.
By contrast, within-author-group strain sensitivity has a median range of 1 log2
unit over 279 strata. The small and selectively available replicate sample does
not establish universal reproducibility; it does rule out presenting the pooled
duplicate-conflict rate as a clean inter-laboratory error estimate.

The ILToxDB export combines CC50/IC50/EC50 in one field. Its 24h MTT selection
still includes multiple cell lines and protocols. Neither its repeat range nor
its transfer contrast identifies a pure laboratory effect or antibacterial mechanism.

## Verified primary literature

- Choung et al., *Extracting medicinal chemistry intuition via preference machine
  learning*, Nature Communications 14, 6651 (2023),
  https://doi.org/10.1038/s41467-023-42242-1.
  The study learns chemist preferences and evaluates prioritisation/design tasks.
  It establishes relevant prior work, not binary-label/MIC equivalence in QACs.
  This manuscript should make no universal first-ever claim for learning human judgement.
- Schölkopf et al., *Towards Causal Representation Learning* (2021),
  https://arxiv.org/abs/2102.11107.
  Representation alignment or prediction alone does not supply interventions on
  antibacterial mechanisms. Here the manipulated variable is supervision in a fixed
  computational training procedure.
- Toukach, Arakelyan and Egorova, *ILToxDB: A Database on Cytotoxicity of Ionic
  Liquids*, Environmental Science & Technology Letters 12, 1631–1635 (2025),
  https://doi.org/10.1021/acs.estlett.5c00860.
  This is mammalian-cell cytotoxicity, not MIC; the source paper reports 3,844
  assay entries, 1,224 ionic liquids, 154 cell lines and 152 publications.
  Our 273-molecule filtered source is a local slice, not the database size.
- CLSI M07, *Methods for Dilution Antimicrobial Susceptibility Tests for Bacteria
  That Grow Aerobically*, 12th edition (2024),
  https://clsi.org/shop/standards/m07/.
  The v8 microbiological-assay paragraph cites reference 76, but that bibliography
  entry is a lithium-ion-electrolyte paper. Replace the incorrect citation with
  the relevant broth-dilution reference; this correction does not verify actual
  compliance of the archived experimental procedure with every CLSI requirement.

QMR DOI `10.5281/zenodo.22286669` is recorded in the local source audit; its landing
page could not be read during this session, so its public availability is not
independently certified here.

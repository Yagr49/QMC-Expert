# Primary sources and interpretation

Models were selected before inspecting their extension results, by recent peer-reviewed publication and runnable public checkpoint, not by target scores.

- ChemFM: Cai et al., *ChemFM as a scaling law guided foundation model pre-trained on informative chemicals*, Communications Chemistry9,3(2026), published18December2025. https://www.nature.com/articles/s42004-025-01793-8 ; official code https://github.com/TheLuoFengLab/ChemFM ; checkpoint https://huggingface.co/ChemFM/ChemFM-1B . Frozen representation probe, not a reproduction of the paper's full fine-tuning leaderboard.
- ChemBERTa-3: Singh et al., Digital Discovery2026,5,662–685, DOI10.1039/D5DD00348B. https://pubs.rsc.org/en/content/articlelanding/2025/dd/d5dd00348b ; official code https://github.com/deepforestsci/chemberta3 ; released checkpoints https://huggingface.co/DeepChem/MoLFormer-c3-1.1B and https://huggingface.co/DeepChem/ChemBERTa-100M-MLM . ChemBERTa-3 is a framework with multiple checkpoints; the c3 name counts pretraining molecules, not model parameters.
- Q-HERO: Ghaemi et al., *Topology-Aware Generation and Activity-Based Filtering: A Computational-Experimental Framework for Data-Scarce Quaternary Ammonium Compound Discovery*, JCIM2026,66,3117–3128. https://doi.org/10.1021/acs.jcim.6c00390 ; accessible primary full text https://pmc.ncbi.nlm.nih.gov/articles/PMC13014459/ ; official source https://github.com/pb0316/Q-HERO . Programme-level coordination across two collaborating labs since2012 is documented. It does not establish row-level equality of historical assay conditions. The supplied603-row XLSX has structures, descriptors and one S.aureus MIC column, with no per-compound strain/protocol/lab provenance. The wet-lab SI PDF could not be retrieved (publisher403; PMCbot HTML response), so no strain-specific claim was inferred from it.

## What Mendeley material adds

The local manuscript's source-only Q-HERO/QMR/ILToxDB contrasts are useful as hypotheses about assay-aware transfer. They do not vary provenance alone: compound selection, size, chemistry, curation, organisms/strains and aggregation also change. The source comparisons and MIC replicate summaries are historical exploratory results, not controls in the new modern-backbone experiment.

The same-compound/same-strain QMR audit (38strata over23compounds, five strains; medianlog2range0,94.7%withinone dilution) contradicts using all pooled discordance as an inter-laboratory error rate. Available replicates are selective and small. The279within-group cross-strain strata have medianlog2range1; this supports examining strain context but does not show a universal strain effect or human denoising.

The new529-molecule intervention holds chemical composition fixed and replaces pooled MIC aggregation with exactS.aureus aggregation. Pooled source4049records versus exactSA855records. Therefore organism mixture, censoring treatment, number of reports and aggregation all change. Its outcome identifies the composite policy's effect inside one algorithm, not laboratory heterogeneity by itself.

## Reviewer corrections

Kimi described v9 as preregistered: incorrect. The local protocol was fixed before these new predictions, after earlier inspected experiments, and remains exploratory. Kimi questioned three-seed direct-ranking means: archived runs_direct.jsonl contains those means; a one-checkpoint bootstrap was an additional sensitivity. We incorporated useful suggestions without adopting its unsupported equivalence or universal-dominance language. Claude transfer is authorised, but local/server CLI credentials are unavailable.

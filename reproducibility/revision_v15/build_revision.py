"""Integrate completed model comparisons and reproduction audit into a new draft.

Input articles and experiment artifacts stay immutable. Native author fields,
chemistry sections, figures and reference XML are retained from v14.
"""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import re
import shutil
import xml.etree.ElementTree as E

import pandas as pd

ROOT = Path(__file__).resolve().parent
COMA = ROOT.parents[1]
PREVIOUS = ROOT.parent / 'revision_v14'
RUN = ROOT.parent / 'server_models_20261012'
ANALYSIS = RUN / 'analysis'
RECOVERY = ROOT.parent / 'notebook_recovery_20261012'
MAIN = COMA / '2026_10_12_Paper_2_edited-v15_models_and_reproducibility.docx'
SI = ROOT / 'Supplementary_Information_v15.docx'

spec = importlib.util.spec_from_file_location('v11_helpers', ROOT.parent / 'revision_v11/build_revision.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
h = v.h
W, NS = v.W, v.NS

MODEL = {'catboost': 'CatBoost (PCA control)', 'autogluon': 'AutoGluon',
         'tabpfn': 'TabPFN-V2', 'tabfm': 'TabFM', 'chemprop': 'Chemprop D-MPNN'}
REP = {'expert_seed0': 'Human', 'quant-continuous_seed0': 'Continuous MIC',
       'quant-binary_seed0': 'Binary MIC', 'raw-molformer': 'Raw MolFormer',
       'rdkit': 'RDKit descriptors', 'graph': 'Molecular graph'}
MODELS = ['catboost', 'autogluon', 'tabpfn', 'tabfm', 'chemprop']
REPS = ['expert_seed0', 'quant-continuous_seed0', 'quant-binary_seed0', 'raw-molformer', 'rdkit']

REFERENCES = [
    '9. Heid, E.; et al. Chemprop: A Machine Learning Package for Chemical Property Prediction. J. Chem. Inf. Model. 2024, 64 (1), 9–17. https://doi.org/10.1021/acs.jcim.3c01250.',
    '10. Hollmann, N.; Müller, S.; Purucker, L.; Krishnakumar, A.; Körfer, M.; Hoo, S. B.; Schirrmeister, R. T.; Hutter, F. Accurate predictions on small data with a tabular foundation model. Nature 2025, 637, 319–326. https://doi.org/10.1038/s41586-024-08328-6.',
    '11. Google Research. TabFM: Tabular Foundation Models. https://github.com/google-research/tabfm (accessed 2026-10-12); code revision fbb665569425fd2f490c6576b3af967876fe11ff904; JAX regression checkpoint google/tabfm-1.0.0-jax, revision d5e74033fcf257699fab013e2cdd7edf424ff904.',
    '12. Erickson, N.; Mueller, J.; Shirkov, A.; Zhang, H.; Larroy, P.; Li, M.; Smola, A. AutoGluon-Tabular: Robust and Accurate AutoML for Structured Data. arXiv 2020, arXiv:2003.06505. https://doi.org/10.48550/arXiv.2003.06505.',
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find(body, prefix):
    matches = [p for p in body.findall('w:p', NS) if h.text(p).startswith(prefix)]
    assert len(matches) == 1, (prefix, len(matches))
    return matches[0]


def insert_before(body, node, additions):
    index = list(body).index(node)
    for item in additions:
        body.insert(index, item)
        index += 1


def pooled_table(pooled):
    rows = [['Model', 'Representation', 'Cation CV', 'Scaffold CV', 'OOD-17']]
    for model in MODELS:
        for rep in (['graph'] if model == 'chemprop' else REPS):
            q = pooled[(pooled.model == model) & (pooled.representation == rep)].set_index('schema')
            assert set(q.index) == {'cation', 'scaffold', 'full-QAC105'}
            rows.append([MODEL[model], REP[rep], f'{q.loc["cation"].RMSE:.3f}',
                         f'{q.loc["scaffold"].RMSE:.3f}', f'{q.loc["full-QAC105"].RMSE:.3f}'])
    return rows


def prepare_inputs():
    (ROOT / 'analysis').mkdir(parents=True, exist_ok=True)
    (ROOT / 'figures').mkdir(exist_ok=True)
    names = ['comparison_pooled.csv', 'all_model_metrics.csv', 'paired_cluster_bootstrap.csv',
             'verification.json', 'layout_audit.json', 'source_repeat_array_audit.json']
    inputs = [COMA / '2026_10_11_Paper_2_edited-v14_QAC105_OOD17.docx',
              PREVIOUS / 'Supplementary_Information_v14.docx']
    for name in names:
        source = ANALYSIS / name
        shutil.copyfile(source, ROOT / 'analysis' / name)
        inputs.append(source)
    for extension in ['pdf', 'png']:
        source = ANALYSIS / ('new_decoder_error_violins.' + extension)
        shutil.copyfile(source, ROOT / 'figures' / ('figure6_decoder_error_violins.' + extension))
        inputs.append(source)
    inputs += [RECOVERY / 'README_RU.md', RECOVERY / 'article_number_provenance.csv',
               RUN / 'results_20261012T152125Z/audit_repeats.json']
    (ROOT / 'input_manifest.json').write_text(json.dumps({str(p.relative_to(COMA)): sha(p)
                                                        for p in inputs}, indent=2))


def build_main(pooled):
    files, tree, body = v.read_doc(COMA / '2026_10_11_Paper_2_edited-v14_QAC105_OOD17.docx')
    normal = find(body, 'Human annotations and numerical measurements')
    template = body.findall('w:tbl', NS)[1]

    def p(text, level=None):
        return v.paragraph(normal, text, level)

    abstract = ('Human Good/Bad judgements offer a coarse supervisory signal for molecular learning. '
                'We compare human, continuous-MIC and binary-MIC supervision on identical source molecules '
                'using matched partial MolFormer fine-tuning, five paired training seeds and common decoders '
                'for four antibacterial endpoints in 105 quaternary ammonium compounds. Under cation-held-out '
                'validation, mean pooled RMSE is 1.737, 1.715 and 1.806 log2(mg/L), respectively, versus '
                '1.858 for raw features. Real-versus-shuffled labels support a contribution from human '
                'supervision within this learning procedure. Scaffold holdout retains a pooled-loss benefit '
                'over raw features; 17 compounds from four new scaffold families expose limited absolute '
                'concentration prediction. Additional Chemprop, TabPFN-V2, TabFM, AutoGluon and descriptor '
                'comparisons show that human-guided representations remain competitive when the decoder changes, '
                'with RDKit providing a strong independent reference. These architectural comparisons use one '
                'source seed and do not establish universal superiority. Independent training repeats recover '
                'the matched representations exactly under the archived encoding layout, while altered batching '
                'reveals numerical sensitivity. Human annotation is thus useful molecular supervision under '
                'controlled label replacement; measurement equivalence, general adapter superiority and '
                'biological causality are not established.')
    h.replace(find(body, 'Human Good/Bad judgements offer'), abstract)

    h.replace(find(body, 'Molecular learning usually treats'),
              'Fine-tuning a molecular foundation model is one route to task-specific prediction (4). '
              'When only hundreds of source compounds are available, the choice of supervision and the amount '
              'of trainable capacity should be tested separately. Compact projections on frozen features '
              'offer a lower-parameter alternative, motivating a practical question: can a coarse human '
              'judgement supply useful guidance without treating more extensive adaptation as automatically '
              'better? Chemists already make categorical decisions about promising compounds, and such '
              'judgements can be learned for molecular prioritisation (1). We ask whether they also shape '
              'representations useful for predicting measured antibacterial activity in quaternary ammonium '
              'compounds, where structure, charge and activity vary across related series (2).')
    h.replace(find(body, 'Adaptation capacity also matters.'),
              'We separate supervision assignment from adaptation capacity. The historical 256-dimensional '
              'contrastive encoder compresses frozen molecular features. The primary controlled experiment '
              'instead applies the same partial MolFormer fine-tuning to every source arm, updating '
              '28,375,297 parameters under a fixed budget. This tests human versus quantitative guidance '
              'within one adaptation procedure. It does not provide a parameter-matched comparison of '
              'compact projections, full fine-tuning and internal adapters such as LoRA. In fact, the '
              'matched partial-fine-tuning results improve over raw features in several settings, so a '
              'general claim that fine-tuning is harmful would conflict with the evidence.')

    workflow = find(body, 'We preserve the original workflow:')
    h.replace(workflow, h.text(workflow) + ' A further fixed comparison varies the target decoder using '
              'Chemprop graphs, TabPFN-V2, TabFM, AutoGluon and RDKit descriptors (9–12). This distinguishes '
              'the value of the supplied supervision from dependence on a single CatBoost decoder.')

    causal = find(body, '2.5. What the controlled comparison identifies')
    additions = [
        p('2.5. Transfer across graph and tabular models', 2),
        p('We evaluated Chemprop D-MPNN (9), TabPFN-V2 (10), TabFM (11), AutoGluon (12) and a '
          'CatBoost control on the same QAC-105 cation and scaffold folds and the untouched OOD-17 '
          'collection. The four tabular decoders compare RDKit descriptors with raw and guided '
          'MolFormer features. Guided features use the existing human, continuous-MIC and binary-MIC '
          'source checkpoints for seed 0. Embeddings receive training-only PCA to 32 dimensions, and '
          'each endpoint has a separate fitted decoder. Consequently, this is an exploratory decoder '
          'robustness comparison; its scores are distinct from the five-seed joint-task primary model.'),
        h.table(template, pooled_table(pooled)),
        p('Table 5. Complete fixed-model comparison: pooled RMSE in log2(mg/L). Cation and scaffold '
          'CV retain all 105 compounds and 420 exact endpoints; OOD scoring uses 67 exact endpoints '
          'from 17 compounds, retaining the one >500 mg/L observation separately. Tabular results '
          'use one source seed and a fixed decoder seed. Chemprop entries average seed-specific '
          'RMSE across three graph-training seeds, rather than scoring an ensemble. RDKit features '
          'are not reduced by PCA. No model or representation was selected using OOD outcomes.'),
        p('Human-guided representations have lower pooled error point estimates than raw features '
          'for each of the four tabular decoders in all three evaluation regimes. They also '
          'have lower point errors than both quantitative representations under cation holdout '
          'and on OOD-17. Scaffold holdout exposes exceptions: continuous MIC gives CatBoost '
          'RMSE 1.892 versus human 1.901, and binary MIC gives AutoGluon 1.911 versus human '
          '1.934. The results support useful transfer across decoder choices, conditional '
          'on one source realisation. They do not override the primary five-seed cation-CV '
          'result, where continuous MIC has slightly lower mean error than human supervision.'),
        p('On OOD-17, human/continuous-MIC/binary-MIC/raw RMSE is 1.966/2.265/1.995/2.225 for '
          'TabPFN-V2 and 1.992/2.541/2.110/2.299 for TabFM (Figure 6). RDKit yields 1.978 and '
          '2.027, respectively, close to the human point estimates. The paired cation-cluster '
          'intervals for human minus RDKit include zero: [−0.150, +0.149] for TabPFN-V2 and '
          '[−0.162, +0.108] for TabFM. With only four OOD families, these estimates do not '
          'establish general OOD superiority or equivalence.'),
        v.embed(files, ROOT / 'figures/figure6_decoder_error_violins.png', 'rIdV15DecoderViolins'),
        p('Figure 6. Absolute endpoint-error distributions for TabPFN-V2 and TabFM under cation '
          'holdout, scaffold holdout and OOD evaluation. Colours compare all five representations. '
          'Bars indicate median and IQR. Each CV distribution contains 420 endpoint errors from '
          '105 compounds; OOD contains 67 exact endpoint errors from 17 compounds. Endpoints from '
          'one molecule are dependent. Density shape and overlapping medians are descriptive; '
          'paired intervals resample molecular groups. All visible errors are retained.'),
        p('The descriptor reference also challenges an unrestricted foundation-model claim. '
          'RDKit+CatBoost attains cation/scaffold RMSE 1.615/1.818, and RDKit+AutoGluon attains '
          '1.716/1.828. Chemprop gives 2.031/2.003/2.375 for cation/scaffold/OOD under its fixed '
          '100-epoch, three-seed protocol. These outcomes concern a small cohort and the declared '
          'budgets; they are not general rankings of graphs, descriptors and language models. '
          'All endpoint scores, unsuccessful predictions, model settings and paired intervals '
          'are reported in Supporting Information S21.'),
    ]
    figure = next(node for node in additions if node.find('.//w:drawing', NS) is not None)
    docpr = figure.find('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr')
    docpr.set('name', 'Figure 6: fixed decoder error distributions')
    docpr.set('descr', 'TabPFN-V2 and TabFM errors for five representations under cation, scaffold and OOD evaluation')
    insert_before(body, causal, additions)
    h.replace(causal, '2.6. What the controlled comparison identifies')

    conclusions = find(body, '3. Conclusions')
    insert_before(body, conclusions, [
        p('2.7. Reproduction and the origin of historical scores', 2),
        p('An independent repeat of all 30 matched partial-fine-tuning runs recovered the source '
          'initialisations, molecule order and final training losses exactly. With the archived '
          'target-encoding batch layout, all 93 historical target arrays and all 62 QAC-105/OOD-17 '
          'arrays are byte-identical. Refitting the archived v14 decoders from cached arrays also '
          'reproduces every saved cation and scaffold prediction. Re-encoding the same models '
          'with a different batch composition produces feature perturbations around 10−6 and '
          'changes some CatBoost decisions. Replaying the archived layout removes this discrepancy. '
          'The primary tables therefore retain that layout; the altered-layout sensitivity is '
          'reported separately in S22.'),
        p('Recovered April–May notebooks and a July follow-up contain saved outputs supporting '
          'the historical article scores. In particular, the July OOD regression RMSE is 2.133, '
          'whereas the May snapshot gives 2.276; these are different archived analyses. Their '
          'difference does not justify replacing the original 2.13 with 2.27. Earlier endpoint-row '
          'splits can place tasks from the same molecule in both training and test, and the '
          'historical representation sources overlap target chemistry. Those scores consequently '
          'address a different validation question from the strict source-excluded, cation/scaffold '
          'comparisons here. Exact Mac-to-Linux reproduction remains incomplete for some historical '
          'frozen-feature MLP branches; we retain these as supplementary environment sensitivities.'),
    ])

    limit = find(body, 'The limits are equally clear.')
    h.replace(limit, 'Changing the target decoder retains competitive human-guided predictions in the '
              'one-source-seed extension, while descriptor models remain strong competitors and Chemprop '
              'provides a graph-based reference. Holding out entire scaffold families is harder than '
              'holding out new cations; the 17-compound OOD collection does not establish accurate '
              'absolute concentrations. Text embeddings of four fixed task descriptions provide no '
              'consistently resolved advantage over one-hot metadata. Compact projections merit '
              'evaluation as a lower-parameter design choice, but the current comparisons do not '
              'identify a generally superior adaptation strategy. The contribution is a controlled '
              'comparison of supervisory signals, supported by independent training repeats and '
              'explicitly delimited by validation regime, decoder and chemical scope.')

    support_heading = find(body, 'Supporting Information')
    insert_before(body, support_heading, [
        p('4.6. Graph and tabular decoder comparison', 2),
        p('All model comparisons use the original v14 target folds and log2(mg/L) endpoints. '
          'Train-only median imputation, zero-variance removal and scaling are followed by full-SVD '
          'PCA-32 for each 768-dimensional representation; RDKit descriptors use their remaining '
          'native dimensions. Preprocessors are fitted once per outer training fold and never '
          'on test or OOD rows. Four separate endpoint models are fitted for each tabular '
          'representation. The full-QAC model uses all 105 compounds to supply context or '
          'training data for OOD predictions. The source features use the archived seed-0 '
          'checkpoints, avoiding re-encoding batch changes in the decoder comparison.'),
        p('The CatBoost control retains 300 iterations, depth five, learning rate 0.05 and seed '
          '1729. AutoGluon-Tabular 1.6.3 selects among RF, XT, GBM and CAT with a 60-second '
          'budget, a fixed group-disjoint inner holdout and no bagging, stacking or weighted '
          'ensemble. Its selected model is refitted on the complete outer training fold; refitting '
          'takes additional time. In the OOD run, the inner split groups QAC training compounds '
          'by scaffold. Preprocessing uses only the outer training fold, so this is an outer-test '
          'evaluation of the declared pipeline rather than a fully nested inner-preprocessing study.'),
        p('TabPFN 9.1.0 runs the publicly downloadable V2 regression checkpoint with four '
          'estimators, CUDA and seed 1729. This is a V2-weight result, not an evaluation of the '
          'newest checkpoint available in the package. TabFM 1.0.1 uses the pinned Google Research '
          'JAX regression checkpoint, four estimators, CPU float32 and seed 1729, retaining '
          'all training rows as context. Weight identifiers and hashes are recorded in S21 '
          'and the run manifests.'),
        p('Chemprop 2.3.1 trains a four-target D-MPNN on full-salt SMILES with hidden dimension '
          '300, message-passing depth three, mean aggregation, no batch normalisation, train-only '
          'target standardisation and batch size 32. Seeds 0, 1 and 2 each use 100 epochs '
          'and the final checkpoint, with no selection by outer-fold or OOD measurements. '
          'The graph model uses target activity data only, whereas guided representations '
          'also use the separate source supervision. The comparison does not equalise all '
          'pretraining data, model capacities or compute budgets.'),
        p('Across the fixed models, 913 fits comprise 880 endpoint fits for the four tabular '
          'decoders and 33 four-target graph fits. Every reported RMSE, MAE and R² was independently '
          'recomputed from saved predictions. Exploratory decoder contrasts use 2,000 paired '
          'cluster-bootstrap draws at fixed source seed: cation or scaffold groups for CV, '
          'and both cation and four-family groupings for OOD. These intervals are conditional '
          'on the fitted decoders and do not include source-seed variability. They are separate '
          'from the primary 10,000-draw seed/scaffold intervals.'),
        p('4.7. Reproduction and notebook provenance', 2),
        p('The independent server repeats preserve source IDs, label hashes, initial weights, '
          'minibatch order, update budget and pinned MolFormer revision. Reconstructed checkpoints '
          'retain trained parameters and all persistent and nonpersistent evaluation buffers. '
          'Exact target-array comparisons distinguish the archived batch layout from a fresh '
          '105-compound encoding layout. Historical notebook snapshots are provenance artifacts '
          'with saved outputs; finding an output is not equivalent to rerunning that entire '
          'notebook. Snapshot hashes, cell indices and the v5-number mapping are in '
          'notebook_recovery_20261012. The independent computational records are in '
          'server_models_20261012; S22 records unresolved cross-environment branches.'),
    ])
    statement = find(body, 'Full annotation/source audits;')
    h.replace(statement, h.text(statement) + ' Revision_v15 adds the completed fixed decoder '
              'comparisons, Figure 6, recovered notebook provenance and the independent reproduction '
              'audit in S21–S22; it preserves the primary revision_v14 result tables.')
    references_heading = find(body, 'References')
    reference_index = list(body).index(references_heading)
    assert len([n for n in list(body)[reference_index + 1:] if re.match(r'^\d+\. ', h.text(n))]) == 8
    section = body.find('w:sectPr', NS)
    insert_before(body, section, [p(text) for text in REFERENCES])
    v.TITLE = h.text(body[0])
    v.unique_ids(tree)
    h.write(files, tree, MAIN)
    v.exports(files, tree, ROOT / 'manuscript_v15_readable.md', ROOT / 'manuscript_v15.html')
    return normal, template


def build_si(normal, template, pooled):
    files, tree, body = v.read_doc(PREVIOUS / 'Supplementary_Information_v14.docx')
    section = body.find('w:sectPr', NS)

    def add(text, level=None):
        insert_before(body, section, [v.paragraph(normal, text, level)])

    def table(rows):
        insert_before(body, section, [h.table(template, rows)])

    h.replace(find(body, 'Scope of the QAC-105/OOD-17 revision'),
              'Scope of the QAC-105/OOD-17 revision and fixed-model extension')
    note = find(body, 'The main article now centres')
    h.replace(note, h.text(note) + ' Sections S21–S22 add the completed model comparison and '
              'independent reproduction audit from 12 October 2026. Older sections retain their '
              'archival protocols; recovered notebook provenance is described below and does '
              'not merge May and July metrics into one result.')
    old_ood = find(body, 'The 17 newly synthesised compounds are structurally held out, but')
    h.replace(old_ood, 'The historical 17-compound comparison is retained under its original '
              'log2 micromolar protocol, separately from the four-endpoint mg/L comparison '
              'in the current main article. The recovered May endpoint-residual bootstrap '
              'gives human minus regression mean ΔRMSE −0.086 [−0.227, +0.054]. It is '
              'descriptive, samples dependent endpoint residuals individually and does '
              'not establish statistical equivalence. The July metric provenance and '
              'the different modern grouped comparisons are documented in S22.')
    provenance = find(body, 'Primary artifacts:')
    h.replace(provenance, 'Primary archived artifacts include reproducibility/finetune/runs.jsonl, '
              'runs_direct.jsonl, recalibration.csv, qhero/qhero_metrics.csv, qhero_residuals.csv '
              'and analysis/ablation_bootstrap.csv. April–May notebook snapshots and a July '
              'SHAP/causal-analysis notebook were recovered on 12 October 2026, including code '
              'and saved metric outputs. The updated FINDINGS.md and S22 distinguish the '
              'provenance recovered from exact independent reproduction. Geometry and attribution '
              'remain descriptive; they do not identify biological causal mechanisms.')
    geometry = find(body, 'The archived CKA/probing table reports')
    h.replace(geometry, 'The archived CKA/probing table reports high alignment between MolFormer '
              'and the expert embedding (CKA 0.933 in-domain and 0.946 OOD; linear-probe R² '
              '0.891 from MolFormer to embedding and 0.844 in reverse). Generating code and '
              'selected outputs were recovered in notebook snapshots. Exact encoder and '
              'execution-state provenance for every historical summary is not fully resolved, '
              'and these values have not been independently regenerated. They remain descriptive '
              'evidence about geometry, not the causal supervision test.')
    old_ablation = find(body, 'A matched expert-versus-regression encoder ablation was run')
    h.replace(old_ablation, 'The recovered May causal_final notebook records historical OOD '
              'RMSE 2.314/2.189/2.276 for raw/human/regression. Its endpoint-residual bootstrap '
              'gives human minus regression mean ΔRMSE −0.086 [−0.227, +0.054], matching '
              'analysis/ablation_bootstrap.csv. It samples endpoint residuals rather than '
              'molecule or scaffold clusters and is retained as a descriptive historical '
              'analysis. The July shap_causal_analysis notebook instead records regression '
              'RMSE 2.133 with the same rounded raw and human values. This supplies the saved '
              'output behind the original article’s 2.13; the May result cannot be used as '
              'an arithmetic correction of it. Neither historical interval establishes '
              'equivalence or a chemical causal mechanism.')

    add('S21. Fixed graph and tabular model comparison', 1)
    add('All 913 fits completed. Metrics were independently recomputed from saved per-compound '
        'predictions. This extension was selected after earlier results and is exploratory. '
        'It uses one adapted source seed (0), fixed CV folds, full QAC-105 and all 17 OOD '
        'molecules. Four tabular decoders predict each endpoint separately; Chemprop predicts '
        'four targets jointly. Human and quantitative features use the archived layout. '
        'Absolute concentrations and qualifiers are preserved, including IT505 Ec_MBC >500 mg/L. '
        'The complete run, configuration and code-version ledgers are in server_models_20261012.')
    add('Table S23. Complete pooled-loss fixed-model comparison, corresponding to main Table 5. '
        'Units are log2(mg/L). Graph results are means of three seed-specific RMSE values; '
        'all tabular comparisons have one source seed. No point estimate is a declaration '
        'of general method superiority.')
    table(pooled_table(pooled))

    add('Table S24. Every endpoint score in the fixed-model comparison. Trained graph entries '
        'are mean ± graph-seed SD (three seeds); tabular entries have one fit per endpoint '
        'and no seed SD. Source-seed uncertainty is not included. Pooled R² is deliberately '
        'omitted; each reported R² assesses variation within one species/endpoint.')
    scores = pd.read_csv(ANALYSIS / 'all_model_metrics.csv')
    scores = scores[scores.task != 'pooled']
    rows = [['Model / representation', 'Scheme / endpoint', 'Seeds / n', 'RMSE', 'MAE / R²']]
    for key, group in scores.groupby(['model', 'representation', 'schema', 'cohort', 'task']):
        model, rep, schema, cohort, task = key
        seeds = group.seed.nunique()
        assert group.n.nunique() == 1
        def fmt(column):
            return (f'{group[column].mean():.3f} ± {group[column].std():.3f}' if seeds > 1
                    else f'{group[column].iloc[0]:.3f}')
        rows.append([MODEL[model] + ' / ' + REP[rep], schema + ' / ' + task,
                     f'{seeds} / {int(group.n.iloc[0])}', fmt('RMSE'), fmt('MAE') + ' / ' + fmt('R2')])
    table(rows)

    add('Table S25. All fixed-source-seed human-minus-comparator paired ΔRMSE intervals. '
        '2,000 paired cluster-bootstrap draws; negative values favour human. These '
        'unadjusted exploratory intervals condition on fitted decoders and one source '
        'seed. OOD cation grouping has 17 groups; scaffold grouping has only four '
        'families. The four-family estimates cannot be treated as stable population bounds.')
    rows = [['Model / scheme', 'Comparator', 'ΔRMSE / 95% interval', 'Grouping / groups', 'Exact n']]
    for row in pd.read_csv(ANALYSIS / 'paired_cluster_bootstrap.csv').itertuples():
        rows.append([MODEL[row.model] + ' / ' + row.schema, REP[row.comparator],
                     f'{row.delta_RMSE_human_minus_comparator:+.3f} [{row.low:+.3f}, {row.high:+.3f}]',
                     f'{row.grouping} / {row.groups}', str(row.n_exact)])
    table(rows)

    add('S21.1. Exact model versions and evaluation budgets', 2)
    add('Main Section 4.6 specifies the pipelines. Chemprop 2.3.1 uses three fixed graph seeds, '
        '100 final-checkpoint epochs, hidden dimension 300, depth three and four outputs. '
        'AutoGluon-Tabular 1.6.3 uses RF/XT/GBM/CAT, a 60-second selection budget and extra '
        'refit time. TabPFN library 9.1.0 uses the public V2 regressor with four estimators; '
        'checkpoint SHA256 2ab5a07d5c41dfe6db9aa7ae106fc6de898326c2765be66505a07e2868c10736. '
        'TabFM package 1.0.1 uses code fbb665569425fd2f490c6576b3af967876fe11ff904 and '
        'google/tabfm-1.0.0-jax revision d5e74033fcf257699fab013e2cdd7edf424ff904, '
        'CPU float32 and four estimators. RDKit descriptors use 2026.3.6. Package and '
        'checkpoint manifests distinguish code-version changes needed for setup from '
        'the parameters of each completed fit. Each recorded script and protocol SHA '
        'maps to its saved source in server_models_20261012/code_versions.')
    add('Group assignments are fixed across decoders. All preprocessing excludes outer test '
        'and OOD rows. AutoGluon preprocessing fits on the outer training fold before '
        'its grouped internal selection split, and is therefore not independently refitted '
        'inside that inner split. OOD is never used for architecture, epoch or hyperparameter '
        'selection. Descriptor, graph and guided-feature inputs contain different prior '
        'information and receive different fixed compute budgets. The study measures '
        'performance under these declared pipelines; it does not isolate architecture '
        'at equal total data or compute.')

    add('S22. Independent reproduction and recovered notebook provenance', 1)
    add('Table S26. Reproduction outcomes. The original v14 primary metrics remain associated '
        'with their archived batch layout. Altered-layout outputs are separately named '
        'sensitivity results, avoiding silent replacement of the primary tables.')
    table([
        ['Experiment', 'Evidence', 'Outcome', 'Scope', 'Record'],
        ['v14 cached cation refits', '27,816 common predictions', 'Exactly equal', 'All saved arms and encodings', 'audit_repeats.json'],
        ['v14 cached scaffold refits', '15,616 common predictions', 'Exactly equal', 'All saved scaffold arms', 'audit_repeats.json'],
        ['Matched partial fine-tuning', '30 independent source-training runs', 'Final losses exactly equal', 'Six arms × five seeds', 'audit_repeats.json'],
        ['Historical target representations', '93 target arrays', 'Byte-identical', 'Archived encoding layout', 'source_repeat_array_audit.json'],
        ['QAC-105/OOD-17 representations', '62 target arrays', 'Byte-identical', 'Independent models; archived layout', 'layout_audit.json'],
        ['Fresh QAC-105 batching', 'Feature changes around 10−6', 'Some CatBoost predictions differ', 'Changed layout; replay resolves', 'audit_repeats.json'],
        ['c3-MolFormer / ChemFM', 'Common archived predictions', 'Exactly equal', 'Declared frozen-feature repeats', 'audit_repeats.json'],
        ['MolFormer / ChemBERTa / context MLP', 'Equal initial weights and training IDs', 'Mac/Linux losses and predictions differ', 'Exact cause not fully localised', 'audit_repeats.json'],
        ['Historical Ridge sensitivity', 'Extreme predictions retained', 'Numerically unstable', 'Not evidence for a robust ranking', 'audit_repeats.json'],
    ])
    add('S22.1. Batch-layout sensitivity and checkpoint state', 2)
    add('Fresh target encoding uses the independently retrained models but a different compound '
        'batch layout. Small floating-point changes in feature vectors alter some CatBoost '
        'splits; individual predictions can change substantially despite vector differences '
        'around 10−6. The independently retrained models reproduce all 62 original QAC-105 '
        'and OOD-17 arrays byte-for-byte when the archived layout is replayed: the original '
        '104-compound target array is combined with the omitted compound encoded together '
        'with the same three reference compounds. This diagnostic uses structure identities '
        'and model state, not target activities or outcome-based checkpoint selection. '
        'Checkpoint reconstruction preserves all persistent and nonpersistent buffers. '
        'The exact replication refers to this pinned implementation and environment, '
        'rather than promising bitwise equality across arbitrary hardware or packages.')
    add('S22.2. Cross-environment historical branches', 2)
    add('The frozen-feature MLP comparison includes a transition from Mac/PyTorch 2.4.1 to '
        'Linux/PyTorch 2.14, with NumPy, BLAS and hardware differences. Some branches '
        'diverge despite identical initial model hashes and training identities. These '
        'differences are not fully attributed to an individual operation. They are '
        'retained as unresolved environment sensitivities, while c3-MolFormer, ChemFM '
        'and the matched partial-fine-tuning branches reproduce exactly in their '
        'declared replay conditions. Extreme Ridge errors are preserved and are '
        'not used to support general model rankings.')
    add('S22.3. Historical numbers recovered from saved notebook outputs', 2)
    add('The recovery inventory contains 48 saved notebook snapshots and selected April–May '
        'copies, plus the July follow-up. It records source paths, dates, hashes and '
        'cell numbers; credential literals are removed from recovered copies. The '
        'notebooks are not rerun by the recovery process. In the May task-comparison '
        'notebook, saved human categorical-task R² values are 0.7102, 0.6403, 0.4269 '
        'and 0.7394. The text-vector values are 0.7494, 0.6752, 0.5918 and 0.7708. '
        'Seven of eight agree with the v5 table after normal rounding. The Ec MIC '
        'text score rounds to 0.59 rather than the printed 0.60. Corresponding '
        'endpoint RMSE outputs are not printed in that cell, so this recovers '
        'their R² provenance rather than fully reproducing every historical metric.')
    add('Those cells stratify molecule × task rows by task identity and use CatBoost '
        'categorical task_id in the found baseline variant, not literal one-hot '
        'columns. Different endpoint rows of a molecule can cross the split. '
        'Historical source overlap is documented separately; an overlap count '
        'alone does not prove membership in the actual checkpoint training split. '
        'An April notebook searches 100 test seeds and selects seed 79, but its '
        'direct contribution to the v5 table has not been established. Finding '
        'that search therefore does not justify attributing all favourable '
        'historical scores to seed selection.')
    add('The May causal_final notebook prints raw/human/regression OOD RMSE '
        '2.314/2.189/2.276. The July shap_causal_analysis notebook prints '
        '2.314/2.189/2.133. The latter supports the original rounded regression '
        'value 2.13. The earlier suggestion of an arithmetic correction to '
        '2.27 is withdrawn. Distinct execution states, encoders and validation '
        'protocols must remain distinguishable. Saved notebook code may also '
        'have been edited after its last execution; output provenance alone '
        'does not establish a clean end-to-end reproduction.')
    v.unique_ids(tree)
    h.write(files, tree, SI)
    v.exports(files, tree, ROOT / 'supplement_v15_readable.md', ROOT / 'Supplementary_Information_v15.html')


def main():
    prepare_inputs()
    pooled = pd.read_csv(ANALYSIS / 'comparison_pooled.csv')
    normal, template = build_main(pooled)
    build_si(normal, template, pooled)
    print(MAIN)
    print(SI)


if __name__ == '__main__':
    main()

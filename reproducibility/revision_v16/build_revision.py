"""Add completed direct prediction and encoder-weight interventions to v15."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import shutil
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent
COMA = ROOT.parents[1]
PREVIOUS = ROOT.parent / 'revision_v15'
RUN = ROOT.parent / 'server_finetune_causal_20261012'
ANALYSIS = RUN / 'analysis'
PRIMARY_CONTRASTS = ROOT.parent / 'revision_v14/analysis/contrasts.csv'
MAIN = COMA / '2026_10_12_Paper_2_edited-v16_finetuning_and_weight_interventions.docx'
SI = ROOT / 'Supplementary_Information_v16.docx'
spec = importlib.util.spec_from_file_location('v15', PREVIOUS / 'build_revision.py')
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
v, h, NS = b.v, b.h, b.NS
ARM = {'raw-molformer':'Pretrained', 'expert':'Human', 'quant-continuous':'Continuous MIC',
       'quant-binary':'Binary MIC', 'expert-shuffled':'Shuffled human',
       'quant-shuffled':'Shuffled continuous MIC', 'quant-binary-shuffled':'Shuffled binary MIC'}
MODE = {'linear':'Frozen + linear', 'compact':'Frozen + MLP', 'lora':'LoRA',
        'partial':'Partial FT', 'full':'Full FT'}
VARIANT = {'raw':'Pure pretrained', 'intact':'Intact', 'rewind_outer_norm':'Rewind outer norm',
           'rewind_blocks':'Rewind eight blocks', 'rewind_all':'Rewind all weights'}
SCHEMES = ['cation','scaffold','full-QAC105']
LORA_REFERENCE = ('13. Hu, E. J.; Shen, Y.; Wallis, P.; Allen-Zhu, Z.; Li, Y.; Wang, S.; '
                  'Wang, L.; Chen, W. LoRA: Low-Rank Adaptation of Large Language Models. '
                  'arXiv 2021, arXiv:2106.09685. https://doi.org/10.48550/arXiv.2106.09685.')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def find(body, prefix):
    return b.find(body, prefix)


def fcell(row, key='RMSE'):
    sd = row[key+'_SD']
    return f'{row[key]:.3f}' + (f' ± {sd:.3f}' if row.runs > 1 else '')


def interval(row):
    return f'{row.delta_RMSE_a_minus_b:+.3f} [{row.low:+.3f}, {row.high:+.3f}]'.replace('-', '−')


def ci_row(ci, branch, a, bkey, schema, grouping='scaffold'):
    rows = ci[(ci.branch == branch) & (ci.a == a) & (ci.b == bkey) &
              (ci.schema == schema) & (ci.grouping == grouping)]
    assert len(rows) == 1, (branch, a, bkey, schema, grouping)
    return rows.iloc[0]


def config_order():
    return [('raw-molformer', mode) for mode in MODE] + [(arm,'partial') for arm in list(ARM)[1:]]


def direct_table(d, parameters):
    rows = [['Initialisation / target adaptation','Trainable parameters','Cation CV','Scaffold CV','OOD-17']]
    for arm, mode in config_order():
        group = d[(d.arm == arm) & (d['mode'] == mode) & (d.task == 'pooled')].set_index('schema')
        p = parameters[(parameters.arm == arm) & (parameters['mode'] == mode)].iloc[0]
        rows.append([ARM[arm]+' / '+MODE[mode], f'{int(p.parameters):,}'] + [fcell(group.loc[s]) for s in SCHEMES])
    return rows


def weight_table(ci):
    primary = pd.read_csv(PRIMARY_CONTRASTS)
    rows = [['Source supervision','All weights: cation CV','All weights: scaffold CV',
             'All weights: OOD-17','Real − shuffled: cation CV']]
    for arm, shuffled in [('expert','expert-shuffled'),('quant-continuous','quant-shuffled'),
                          ('quant-binary','quant-binary-shuffled')]:
        values = [interval(ci_row(ci,'ablation',arm+'/rewind_all',arm+'/intact',s)) for s in SCHEMES]
        prior = primary[(primary.cohort == 'QAC105') & (primary.task == 'pooled') &
                        (primary.comparison == arm+' minus '+shuffled)].iloc[0]
        replay = ci_row(ci,'ablation',arm+'/intact',shuffled+'/intact','cation')
        assert abs(prior.delta_RMSE - replay.delta_RMSE_a_minus_b) < 1e-12
        assert prior.draws == 10000
        values.append(interval(pd.Series(dict(delta_RMSE_a_minus_b=prior.delta_RMSE,
                                              low=prior.ci_low, high=prior.ci_high))))
        rows.append([ARM[arm]]+values)
    return rows


def censor_derivation():
    d = pd.read_csv(ANALYSIS/'ablation_predictions.csv')
    d = d[(d.arm == 'expert') & (d.variant == 'intact') & (d.schema == 'full-QAC105')]
    rows = []
    for seed, group in d.groupby('seed'):
        exact = group[group.qualifier == '=']
        bound = group[group.qualifier == '>']
        assert len(exact) == 67 and len(bound) == 1
        assert bound.compound_id.iloc[0] == 'IT505'
        error = max(float(np.log2(500) - bound.prediction.iloc[0]),0.)
        sse = float(np.sum((exact.y - exact.prediction)**2))
        mbc = exact[exact.task == 'Ec_MBC']
        mbc_sse = float(np.sum((mbc.y - mbc.prediction)**2))
        rows.append(dict(seed=int(seed),prediction_mg_l=2**float(bound.prediction.iloc[0]),
            error_lower_bound=error,pooled_exact_RMSE=np.sqrt(sse/67),
            pooled_RMSE_lower_bound=np.sqrt((sse+error**2)/68),
            Ec_MBC_exact_RMSE=np.sqrt(mbc_sse/16),
            Ec_MBC_RMSE_lower_bound=np.sqrt((mbc_sse+error**2)/17)))
    return pd.DataFrame(rows)


def censor_table(derivation):
    rows = [['Source seed','IT505 prediction (mg/L)','Error lower bound log2',
             'Pooled RMSE: 67 exact → 68 lower bound','Ec MBC RMSE: 16 exact → 17 lower bound']]
    for r in derivation.itertuples():
        rows.append([str(r.seed),f'{r.prediction_mg_l:.3f}',f'{r.error_lower_bound:.3f}',
                     f'{r.pooled_exact_RMSE:.3f} → {r.pooled_RMSE_lower_bound:.3f}',
                     f'{r.Ec_MBC_exact_RMSE:.3f} → {r.Ec_MBC_RMSE_lower_bound:.3f}'])
    rows.append(['Mean of seed-specific RMSEs','—','—',
        f'{derivation.pooled_exact_RMSE.mean():.3f} → {derivation.pooled_RMSE_lower_bound.mean():.3f}',
        f'{derivation.Ec_MBC_exact_RMSE.mean():.3f} → {derivation.Ec_MBC_RMSE_lower_bound.mean():.3f}'])
    return rows


def image(files, name, rid, title):
    element = v.embed(files, ROOT / 'figures' / (name+'.png'), rid)
    node = element.find('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr')
    node.set('name',title); node.set('descr',title)
    return element


def prepare_inputs():
    assert json.loads((ANALYSIS/'verification.json').read_text())['completed']
    (ROOT/'analysis').mkdir(parents=True, exist_ok=True); (ROOT/'figures').mkdir(exist_ok=True)
    inputs = [b.MAIN, b.SI, RUN/'PROTOCOL_RU.md', RUN/'run_experiments.py', RUN/'analyze.py',
              PRIMARY_CONTRASTS]
    shutil.copyfile(PRIMARY_CONTRASTS, ROOT/'analysis/primary_10000draw_contrasts.csv')
    for path in ANALYSIS.glob('*.csv'):
        inputs.append(path)
        if 'predictions' not in path.name:
            shutil.copyfile(path, ROOT/'analysis'/path.name)
    shutil.copyfile(ANALYSIS/'verification.json', ROOT/'analysis/verification.json')
    inputs.append(ANALYSIS/'verification.json')
    for name in ['figure7_direct_adaptation','figure8_weight_rewind','figureS22_prediction_route_violins']:
        for ext in ['pdf','png','svg']:
            path = ANALYSIS/(name+'.'+ext)
            shutil.copyfile(path, ROOT/'figures'/path.name); inputs.append(path)
    for name in ['published_metrics.csv','METRIC_AUDIT_RU.md','source_images_manifest.json']:
        path = RUN/'literature'/name
        shutil.copyfile(path, ROOT/'analysis'/name); inputs.append(path)
    censor_derivation().to_csv(ROOT/'analysis/human_censor_derivation.csv',index=False)
    (ROOT/'input_manifest.json').write_text(json.dumps({str(p.relative_to(COMA)):sha(p) for p in inputs},indent=2))


def build_main(direct, ablation, ci, parameters):
    files, tree, body = v.read_doc(b.MAIN)
    normal = find(body,'Human annotations and numerical measurements')
    template = body.findall('w:tbl', NS)[1]
    def p(text, level=None):
        return v.paragraph(normal,text,level)
    h.replace(find(body,'Fine-tuning a molecular foundation model'),
        'Fine-tuning can improve molecular property prediction, as demonstrated by MoLFormer (4). '
        'Modern foundation models also use low-rank adaptation for property prediction (6,13). '
        'For a small, chemically structured cohort, the amount of adaptation and the choice of '
        'supervision require separate tests. Chemists make categorical decisions about promising '
        'compounds, and such judgements can be learned for molecular prioritisation (1). We ask '
        'whether coarse human guidance can shape representations that transfer to measured MIC/MBC '
        'in quaternary ammonium compounds, even against matched numerical guidance, and which '
        'prediction route retains that signal (2).')
    h.replace(find(body,'We separate supervision assignment from adaptation capacity.'),
        'We separate supervision assignment from adaptation capacity. The historical 256-dimensional '
        'contrastive projection learns on frozen features. The primary controlled source experiment '
        'uses identical partial MolFormer fine-tuning for every label arm, updating 28,375,297 '
        'parameters, including its scalar source head. A new target-task extension compares frozen linear and MLP heads, actual '
        'LoRA, partial and full fine-tuning; it also compares direct prediction with a frozen guided '
        'encoder followed by a common decoder. These tests address declared procedures and budgets, '
        'rather than presupposing that fine-tuning is harmful or that smaller adapters are superior. '
        'Published benchmark scores and their split conventions are audited in S23; our regression '
        'scores use the same QAC cohorts, folds and log2(mg/L) units throughout.')
    workflow = find(body,'We preserve the original workflow:')
    h.replace(workflow,h.text(workflow)+' Finally, weight-rewind interventions test whether '
        'adapted encoder parameters contribute to held-out prediction while feature-map buffers '
        'are retained. Predictive performance is reported before interpreting these interventions.')
    source_method = find(body,'MolFormer-XL uses revision')
    assert 'layers 4–11, the pooler' in h.text(source_method)
    h.replace(source_method,h.text(source_method).replace('layers 4–11, the pooler and',
        'layers 4–11, the outer encoder LayerNorm and')+
        ' The pooler computes a parameter-free mean over token features; it is not a trained '
        'pooling layer. This architectural correction changes no source fit or numerical result.')
    h.replace(source_method,h.text(source_method)+' The partial encoder has 28,374,528 '
        'trainable parameters. Its scalar source head adds 769, giving 28,375,297 '
        'during source training. Direct target fitting discards that scalar head '
        'and trains a new LayerNorm plus four-output head with 4,612 parameters, '
        'giving the 28,379,140 total in Table 6.')
    censored = find(body,'The censored observation also bounds its error:')
    h.replace(censored,h.text(censored)+' Each source seed combines its own exact '
        'squared residuals and its own bound-error contribution before taking '
        'the square root; the reported values then average the five seed-specific '
        'roots. The complete derivation is given in Table S33.')
    old_causal = find(body,'2.6. What the controlled comparison identifies')
    hd = direct[(direct.arm == 'expert') & (direct['mode'] == 'partial') & (direct.task == 'pooled')].set_index('schema')
    raw = direct[(direct.arm == 'raw-molformer') & (direct['mode'] == 'partial') & (direct.task == 'pooled')].set_index('schema')
    first3 = pd.read_csv(ANALYSIS/'ablation_metrics.csv')
    first3 = first3[(first3.arm == 'expert') & (first3.variant == 'intact') &
                    first3.seed.isin([0,1,2]) & (first3.task == 'pooled')].groupby('schema').RMSE.mean()
    route = ci_row(ci,'routes','expert/partial','expert/intact','full-QAC105')
    capacity = direct[(direct.arm == 'raw-molformer') & (direct.task == 'pooled')].set_index(['mode','schema'])
    lora_full = ci_row(ci,'direct','raw-molformer/lora','raw-molformer/full','cation')
    human_continuous = ci_row(ci,'direct','expert/partial','quant-continuous/partial','full-QAC105')
    direct_label = ci_row(ci,'direct','expert/partial','expert-shuffled/partial','scaffold')
    additions = [p('2.6. Direct target fine-tuning and the prediction route',2),
        p('Before interpreting representation changes, we tested direct four-output MIC/MBC '
          'regression on the same five cation and scaffold folds and final QAC-105→OOD-17 split. '
          'From the pretrained encoder, frozen linear, frozen MLP, query/value LoRA, partial '
          'and full fine-tuning use three paired target seeds. Partial target fine-tuning is '
          'also initialised from each real and shuffled source arm with the matching source '
          'seed. All 363 target fits use a fixed 30-epoch budget and train-only standardisation '
          'of the four endpoints. Table 6 reports every configuration; endpoint R², MAE and '
          'rank correlations are in S24.'),
        h.table(template,direct_table(direct,parameters)),
        p('Table 6. Direct-target prediction: mean ± target-seed SD of pooled RMSE in log2(mg/L), '
          'three paired fits per evaluation regime. Counts include the target head and its '
          'LayerNorm; source pretraining is additional computation for the six guided '
          'initialisations. Source and target seeds are paired one-to-one, not crossed. '
          'CV scores retain 420 exact endpoints and OOD scores use 67 exact endpoints; '
          'the bound remains separate. These are final-checkpoint scores under declared '
          'budgets, without model selection by OOD.'),
        image(files,'figure7_direct_adaptation','rIdV16Direct','Figure 7: direct adaptation performance'),
        p('Figure 7. Predictive error for five target-adaptation strategies starting from the '
          'same pretrained model. Dots are three seed-specific pooled errors; horizontal '
          'bars show their arithmetic mean. The compact MLP learns an external projection '
          'on fixed features; LoRA learns rank-eight updates inside query/value modules. '
          'Lower parameter count is not itself evidence of a better prediction procedure.'),
        p('From pretrained initialisation, cation-CV RMSE is '
          f'{capacity.loc[("full","cation")].RMSE:.3f} for full fine-tuning, '
          f'{capacity.loc[("linear","cation")].RMSE:.3f} for a frozen linear head and '
          f'{capacity.loc[("lora","cation")].RMSE:.3f} for LoRA. '
          f'LoRA minus full-fine-tuning ΔRMSE is {interval(lora_full)} under the '
          'exploratory scaffold-group interval convention. This outcome does not favour '
          'small adapters in the tested cation-CV procedure. The OOD point ordering differs: '
          f'linear/LoRA/full RMSE is {capacity.loc[("linear","full-QAC105")].RMSE:.3f}/'
          f'{capacity.loc[("lora","full-QAC105")].RMSE:.3f}/'
          f'{capacity.loc[("full","full-QAC105")].RMSE:.3f}. '
          'Prediction quality and the amount of adaptation must therefore be discussed '
          'with the validation regime and fixed optimisation recipe.'),
        p('With human source initialisation, direct target fine-tuning gives cation/scaffold/OOD '
          f'RMSE {hd.loc["cation"].RMSE:.3f}/{hd.loc["scaffold"].RMSE:.3f}/{hd.loc["full-QAC105"].RMSE:.3f}; '
          'pretrained-initialised partial target fine-tuning gives '
          f'{raw.loc["cation"].RMSE:.3f}/{raw.loc["scaffold"].RMSE:.3f}/{raw.loc["full-QAC105"].RMSE:.3f}. '
          'Source guidance therefore changes the starting representation; this comparison '
          'also includes its additional source-training data and budget. Real-versus-shuffled '
          'source controls, reported with all intervals in S26, distinguish label assignment '
          'from simply adding a training stage.'),
        p('The direct prediction route also retains a label-assignment effect: human '
          f'minus shuffled-human scaffold-CV ΔRMSE is {interval(direct_label)}. '
          'Cation-CV human point error remains above both real quantitative initialisations '
          '(Table 6); the human-versus-quantitative cation intervals include zero. On '
          f'OOD, direct human minus continuous-MIC ΔRMSE is {interval(human_continuous)}. '
          'That conditional contrast favours the human arm in this four-family collection, '
          'without establishing universal superiority over numerical measurements.'),
        p('The two prediction routes are compared using the same first three source checkpoints. '
          'For human guidance, direct/frozen-encoder-plus-CatBoost RMSE is '
          f'{hd.loc["cation"].RMSE:.3f}/{first3.loc["cation"]:.3f} under cation holdout, '
          f'{hd.loc["scaffold"].RMSE:.3f}/{first3.loc["scaffold"]:.3f} under scaffold holdout and '
          f'{hd.loc["full-QAC105"].RMSE:.3f}/{first3.loc["full-QAC105"]:.3f} on OOD. '
          f'The OOD direct-minus-decoder contrast is {interval(route)}. '
          'This conditional, four-family interval addresses the declared prediction pipelines. '
          'The primary five-source-seed decoder results in Tables 2–4 remain separate. '
          'Figure S22 shows split violins for both routes under all three real source signals; '
          'density shapes do not establish causal knowledge.'),
        p('Fixed epoch count does not guarantee equal optimisation difficulty, and the five '
          'strategies have different trainable capacities and learning rates. Frozen heads '
          'use the archived feature-map state; encoder training can also refresh nonpersistent '
          'feature-map buffers. This capacity comparison evaluates full computational procedures. '
          'It is not a pure intervention on parameter count or a claim about the best achievable '
          'LoRA/full-fine-tuning configuration. The separate weight controls below hold those '
          'buffers fixed.'),
    ]
    b.insert_before(body,old_causal,additions)
    h.replace(old_causal,'2.7. What label and weight interventions identify')
    first_causal = find(body,'The paired intervention changes which supervision')
    rewind = ci_row(ci,'ablation','expert/rewind_all','expert/intact','cation')
    scaffold = ci_row(ci,'ablation','expert/rewind_all','expert/intact','scaffold')
    ood = ci_row(ci,'ablation','expert/rewind_all','expert/intact','full-QAC105')
    buffers = ci_row(ci,'ablation','expert/rewind_all','raw-molformer/raw','full-QAC105')
    b.insert_before(body,first_causal,[
        p('We use an operational definition of learned signal: the contribution of adapted '
          'encoder parameters to held-out MIC/MBC prediction after refitting a common decoder. '
          'For each of 30 matched source checkpoints, we restore the pretrained outer encoder '
          'LayerNorm, upper eight blocks, or all encoder parameters, retaining the checkpoint’s '
          'persistent and nonpersistent feature-map buffers. CatBoost is refitted for each '
          'representation, avoiding the confound of feeding modified features to a decoder '
          'trained only on the intact representation. The pure pretrained reference retains '
          'its original buffers and is evaluated separately.'),
        p('All intact encodings reproduce the archived arrays exactly, and refitting reproduces '
          'all 93 intact/raw cation, scaffold and OOD prediction sets. Source arms share '
          'buffer state within seed. Restoring all encoder parameters makes all six source '
          'arms identical in representation and decoder predictions within every seed and '
          'regime. Thus their label-dependent prediction differences require the adapted '
          'encoder weights; the controls do not identify the meaning of an individual '
          'feature or a biological mechanism.'),
        h.table(template,weight_table(ci)),
        p('Table 7. Encoder-weight contribution and label assignment. Columns 2–4 give '
          'rewind-all minus intact ΔRMSE; positive values mean higher error after restoring '
          'pretrained weights while retaining source-checkpoint buffers. Column 5 gives '
          'real minus shuffled ΔRMSE, where negative values favour real labels. All entries '
          'are mean seed-specific pooled contrasts with unadjusted 95% paired seed/scaffold '
          'bootstrap intervals and five source seeds. Columns 2–4 use the new 5,000-draw '
          'weight-control analysis; column 5 retains the primary 10,000-draw intervals '
          'from Section 2.2. CV groups are 29 target '
          'scaffolds; OOD has four families. These are conditional interventions in the '
          'learning procedure.'),
        image(files,'figure8_weight_rewind','rIdV16Rewind','Figure 8: encoder-weight rewind controls'),
        p('Figure 8. Error after component-specific weight rewind relative to the intact '
          'encoder. Points show pooled ΔRMSE and bars show paired seed/scaffold intervals '
          'for human, continuous-MIC and binary-MIC supervision. Each modified representation '
          'receives a refitted common decoder; source-checkpoint buffers remain fixed. '
          'Component effects may interact and cannot be added to allocate causal credit. '
          'The four-family OOD intervals have limited generalisation scope.'),
        p('For human guidance, restoring all encoder weights changes cation/scaffold/OOD '
          f'RMSE by {interval(rewind)}, {interval(scaffold)} and {interval(ood)}, respectively. '
          'The rewind-all representation is not the pure raw reference: on OOD its '
          f'contrast with pure raw is {interval(buffers)}. '
          'This separates the learned-weight contribution from a shared post-training '
          'feature-map state. The intervention supports only a contribution to the specified '
          'prediction loss where its interval resolves an effect. Whether the label signal '
          'contains independent human chemical knowledge still depends on H1–H7, including '
          'what numerical information annotators saw.'),
        p('The human rewind-all interval resolves a higher cation-held-out error after '
          'removing learned weight updates. Its scaffold and four-family OOD intervals '
          'include zero. An interval containing zero is inconclusive at the present sample '
          'size, rather than evidence that no signal was learned. The outer-normalisation '
          'rewind leaves the human decoder predictions unchanged, whereas reverting '
          'the upper eight blocks produces almost the same loss contrast as reverting '
          'all encoder weights. This locates sensitivity within the tested computational '
          'procedure, not within a named human chemical concept.'),
    ])
    h.replace(find(body,'2.7. Reproduction and the origin'), '2.8. Reproduction and the origin of historical scores')
    conclusion = find(body,'Changing the target decoder retains competitive')
    h.replace(conclusion,h.text(conclusion)+' The new direct-target comparison tests LoRA and '
        'backbone fine-tuning explicitly, while weight rewinds delimit the contribution of '
        'learned encoder updates from feature-map state. These additions strengthen the '
        'controlled computational interpretation; they do not establish general adapter '
        'superiority or semantic and biological causality.')
    metrics = find(body,'RMSE, MAE, R² and Spearman correlation are recomputed')
    h.replace(metrics,h.text(metrics)+' Within each seed, pooled RMSE is the square root '
        'of the mean squared residual over all exact compound–endpoint pairs. The '
        'reported multi-seed pooled score averages these seed-specific roots; it '
        'does not average four endpoint RMSEs or score an ensemble prediction.')
    abstract = find(body,'Human Good/Bad judgements offer')
    h.replace(abstract,
        'Human Good/Bad judgements offer coarse supervision for molecular learning. We compare '
        'human, continuous-MIC and binary-MIC signals on identical source molecules using matched '
        'partial MolFormer fine-tuning, five paired source seeds and common decoders for four '
        'antibacterial endpoints in 105 quaternary ammonium compounds. Cation-held-out pooled '
        'RMSE is 1.737, 1.715 and 1.806 log2(mg/L), respectively, versus 1.858 for raw features. '
        'Real-versus-shuffled labels support a contribution from human supervision. Scaffold '
        'holdout and 17 compounds from four new scaffold families expose limits to absolute '
        'concentration prediction. Graph, tabular and descriptor comparisons test decoder '
        'dependence. A further 363-fit extension compares direct target prediction by frozen '
        'heads, LoRA, partial and full fine-tuning with the representation-plus-decoder route. '
        'Encoder-weight rewinds preserve feature-map buffers and refit the decoder, separating '
        'learned updates from computational state. Reverting all weights removes label-dependent '
        'differences across source arms. Independent repeats recover the matched representations '
        'and predictions under the archived encoding layout. Human annotation is useful supervision '
        'under controlled computational interventions; equivalence to measurements, universal '
        'adapter superiority, independent chemical intuition and biological causality are not established.')
    support = find(body,'Supporting Information')
    b.insert_before(body,support,[p('4.8. Direct target prediction and weight controls',2),
        p('The direct extension uses three paired seeds (0–2), five fixed cation folds, five '
          'fixed scaffold folds and one final QAC→OOD fit per configuration. Frozen linear '
          'and compact MLP branches use archived 768-dimensional features. Each non-MLP '
          'target head is LayerNorm(768) followed by Linear(4). The MLP uses dimensions '
          '768→256→128→4, GELU and dropout 0.1. LoRA (13) wraps query and value matrices '
          'in all 12 transformer blocks with rank 8, alpha 16 and dropout 0.1; the backbone '
          'stays frozen. Partial target fine-tuning updates upper eight blocks and the '
          'outer encoder LayerNorm; full fine-tuning updates the entire encoder. All methods '
          'fit train-only task mean/SD and minimise joint standardised MSE for 30 epochs '
          'with batch size 32, AdamW weight decay 0.01, OneCycle scheduling, gradient clipping '
          'at 1, head/LoRA learning rate 10−3 and backbone learning rate 3×10−5. Final '
          'checkpoints are scored; neither outer tests nor OOD select a checkpoint.'),
        p('For source-initialised direct prediction, each target seed uses the matching source '
          'checkpoint. Head initialisation, minibatch order, stochastic schedules and target '
          'scaling are matched across source arms. The direct extension has 363 fits: 165 '
          'pretrained-initialised capacity fits and 198 source-initialised partial-target fits. '
          'Full trained weights are retained for final OOD fits; partial/full CV retains '
          'heads, buffers, encoder hashes, predictions and the deterministic replay recipe. '
          'Prediction files and ledgers are in server_finetune_causal_20261012.'),
        p('Weight controls use five paired source seeds and six source arms. The 120 '
          'intact/rewound configurations plus one pure raw reference each receive 11 '
          'CatBoost fits, totalling 1,331. The decoder uses the primary species-plus-endpoint '
          'one-hot metadata, 300 trees, depth 5, learning rate 0.05, seed 1729 and two '
          'CPU threads. Weight rewinds restore 2 outer-normalisation tensors, 128 tensors '
          'from eight transformer blocks, or all 195 named encoder parameter tensors. '
          'Buffers and encoding layout are held fixed and verified by hashes. All reported '
          'scores are independently recomputed from endpoint predictions. New contrasts '
          'use 5,000 paired seed/group draws and are exploratory, unadjusted and conditional '
          'on the fitted models. The target and source seeds in direct fits are paired, '
          'not independent variance components. Three paired seeds provide a coarse '
          'estimate of stochastic variation. OOD-family inference is limited to four '
          'groups. This follow-up was chosen after earlier results; its protocol was '
          'recorded before its own predictions.'),
    ])
    statement = find(body,'Full annotation/source audits;')
    h.replace(statement,h.text(statement)+' Revision_v16 adds direct-target adaptation '
        '(Table 6; Figure 7), encoder-weight controls (Table 7; Figure 8), split route '
        'violins (Figure S22) and the primary-publication metric audit in S23–S27. '
        'All original annotation and assay fields remain for coauthor completion.')
    for node in body.findall('w:p',NS):
        if h.text(node).startswith('6. Cai, F.; Hanna, K.;'):
            h.replace(node,h.text(node).replace('Hanna, K.','Zacour, K.'))
    b.insert_before(body,body.find('w:sectPr',NS),[p(LORA_REFERENCE)])
    v.TITLE = h.text(body[0]); v.unique_ids(tree); h.write(files,tree,MAIN)
    v.exports(files,tree,ROOT/'manuscript_v16_readable.md',ROOT/'manuscript_v16.html')
    return normal, template


def build_si(normal,template,direct,ablation,ci,parameters):
    files,tree,body = v.read_doc(b.SI)
    section = body.find('w:sectPr',NS)
    def add(text,level=None):
        b.insert_before(body,section,[v.paragraph(normal,text,level)])
    def table(rows):
        b.insert_before(body,section,[h.table(template,rows)])
    for node in body.findall('w:p',NS):
        if 'Cai, F.; Hanna, K.;' in h.text(node):
            h.replace(node,h.text(node).replace('Hanna, K.','Zacour, K.'))
    note = find(body,'The main article now centres')
    h.replace(note,h.text(note)+' Sections S23–S27 add completed direct-target fine-tuning, '
        'weight rewinds and the publication metric audit; earlier section numbers and '
        'archival experiments are retained.')
    add('S23. Published metrics and adaptation context',1)
    add('Before interpreting the new comparison, primary publications and the official '
        'ChemBERTa-3 repository were checked. Table S27 preserves dataset and split context '
        'and cannot be ranked against our log2(mg/L) scores. The MoLFormer comparison '
        'uses the same rotary model family and five QM9 splits; its ± is SD. The '
        'ChemBERTa-3 repository states that ± is the range of three runs, not SD or '
        'a confidence interval. ChemFM’s antibiotic result is classification, not '
        'MIC/MBC regression. These examples motivate testing adaptation rather than '
        'assuming that fine-tuning is harmful.')
    published = pd.read_csv(RUN/'literature/published_metrics.csv').fillna('')
    rows = [['Model / adaptation','Dataset / metric','Split or comparison','Reported value','Primary locator']]
    for r in published.itertuples():
        score = f'{r.value:.4f}' if r.dataset == 'QM9 dipole mu' else f'{r.value:.3f}'
        if r.dispersion != '':
            score += f' ± {float(r.dispersion):.4f}' if r.dataset == 'QM9 dipole mu' else f' ± {float(r.dispersion):.3f}'
        rows.append([r.model+' / '+r.adaptation,r.dataset+' / '+r.metric,
                     r.split+'; '+r.dispersion_meaning,score,r.locator])
    add('Table S27. Selected verified published results. Dataset identity, units, '
        'split conventions and uncertainty definitions are not interchangeable across rows.')
    table(rows)
    add('Primary sources: Ross et al., doi:10.1038/s42256-022-00580-7, author manuscript '
        'https://arxiv.org/html/2106.09553v3, Table 11; Singh et al., '
        'doi:10.1039/D5DD00348B, official repository https://github.com/deepforestsci/chemberta3 '
        'and its two benchmark figures, pinned commit 706f58472c351825960edc05ee9dd9aebd7bec6c; '
        'Cai, Zacour et al., doi:10.1038/s42004-025-01793-8, antibiotic-discovery results '
        'and training-efficiency subsection. The latter reports 6.5 million trainable '
        'parameters for rank-four LoRA on ChemFM-3B. Our query/value rank-eight MolFormer '
        'adapter is a separate recipe. Published ESOL values are retained on their reported '
        'benchmark scale; no conversion to QAC concentration is attempted. The complete '
        'audit and figure hashes are in server_finetune_causal_20261012/literature.')
    add('S24. Direct four-target fine-tuning',1)
    add('All 363 direct fits completed. Three source/target seeds are paired one-to-one. '
        'No adaptation configuration is selected on OOD. All fits have 30 epochs '
        '(90 CV updates, or 120 updates in final QAC-105 training); train-only target '
        'standardisation is inverted before scoring in log2(mg/L). Train/test IDs, '
        'parameters, head hashes, batch-order hashes, curves and predictions are archived. '
        'Partially and fully trained CV backbone weights are identified by hashes '
        'and replay recipes; full final-OOD trainable weights are retained on the server.')
    add('Table S28. Complete direct-target pooled errors, matching main Table 6. '
        'Means and SD describe three seed-specific scores, not an ensemble.')
    table(direct_table(direct,parameters))
    add('Table S29. All direct-target endpoint scores. RMSE and MAE are mean ± SD '
        'over three paired seeds. R² and Spearman are means of seed-specific scores. '
        'QAC has 105 exact values per task; OOD has 17 except Ec_MBC, which has 16.')
    endpoint_table(direct,'mode',table)
    add('S25. Encoder-weight controls and both prediction routes',1)
    add('All 1,331 decoder fits completed. Six source arms × five seeds × four encoder '
        'states are evaluated in each of three regimes, alongside one pure raw reference. '
        'Encoder buffers are fixed across interventions; the decoder is independently '
        'refitted. Source arms share buffer state within each seed. Restoring all '
        'weights makes all six representations and all their decoder predictions '
        'identical within every seed/regime. Restoring just one component may interact '
        'with the remaining adapted weights; component effects are not additive.')
    add('Table S30. Every pooled weight-control score. Mean ± SD is over five '
        'source seeds; the pure raw reference has one fixed fit per split.')
    rows = [['Source supervision','Encoder state / regime','Seeds / exact pairs','RMSE','MAE']]
    for r in ablation[ablation.task == 'pooled'].itertuples():
        rows.append([ARM[r.arm],VARIANT[r.variant]+' / '+r.schema,f'{r.runs} / {r.n_exact}',
                     fcell(pd.Series(r._asdict())),fcell(pd.Series(r._asdict()),'MAE')])
    table(rows)
    add('Table S31. Every endpoint score after encoder-weight controls. Pooled R² '
        'is excluded from within-task interpretation.')
    endpoint_table(ablation,'variant',table)
    b.insert_before(body,section,[image(files,'figureS22_prediction_route_violins',
        'rIdV16RouteViolins','Figure S22: split prediction-route violins')])
    add('Figure S22. Split violins compare direct target fine-tuning (blue, left) '
        'with frozen guided encoder plus CatBoost (orange, right) for three real '
        'supervisory signals. Each density uses mean absolute error over the same '
        'three seed-specific predictions for each compound/endpoint; these are '
        'not residuals of an ensemble prediction. Cation/scaffold panels contain '
        '420 endpoint summaries, OOD 67. Bars show median and IQR; all tails are '
        'retained. Dependencies between endpoints and seeds require paired '
        'cluster inference rather than tests on plotted densities.')
    add('S26. All new paired contrasts',1)
    add('Table S32. Complete exploratory paired seed/group bootstrap contrasts '
        '(5,000 draws, seed 1729). ΔRMSE is A minus B. Both predictions for an '
        'endpoint and all endpoints in the sampled group move together. Paired '
        'seed indices are resampled as one source/target unit. Cation CV is '
        'shown under cation and scaffold grouping; scaffold CV under scaffold '
        'grouping; OOD under cation and four-family grouping. Intervals are '
        'unadjusted, conditional on fitted models and do not refit training '
        'data or add independent OOD families. Source/target seeds are not '
        'crossed, so their separate variance components cannot be identified.')
    add('The primary real-label contrasts retain their archived 10,000-draw intervals '
        'in main Section 2.2 and Table 7. Table S32 repeats those contrasts using '
        'the new 5,000-draw procedure on identical predictions and point effects. '
        'Small interval-edge changes reflect Monte Carlo resampling rather than '
        'a change in measurements, predictions or the pooled-loss calculation.')
    rows = [['Procedure / contrast','A minus B','Regime / grouping','Seeds / groups','ΔRMSE [95% interval]']]
    for r in ci.itertuples():
        rows.append([r.branch+' / '+r.contrast,r.a+' − '+r.b,r.schema+' / '+r.grouping,
                     f'{r.seeds} / {r.groups}',interval(r)])
    table(rows)
    add('S27. Independent verification and limitations',1)
    add('Every target value, qualifier and group membership was checked against '
        'the original registry. No train/test cation or held-out scaffold overlap '
        'was found under the applicable scheme. Paired direct fits share initial '
        'linear heads, minibatch order and train-only target scale. All 93 intact/raw '
        'prediction sets agree with v14 to CSV numerical precision (<10−12); all '
        '62 original intact/raw QAC/OOD representation arrays replay exactly. '
        'All six rewind-all prediction sets are identical within each seed and '
        'regime. The source buffers are shared within seed and unchanged by '
        'intervention. All 33 final-OOD target models were independently reloaded '
        'from saved checkpoints and reproduce their 2,244 predictions, including '
        'the bound, within CSV precision (<10−12). Server code, hashes, launch ledgers and the archived '
        'encoding layout support replay without the Mac being active.')
    add('The bound IT505 Ec_MBC >500 mg/L is excluded from exact scores and retained '
        'in every prediction file. Censor-sensitivity CSVs use max(log2(500) − '
        'prediction, 0) with the exact residuals, giving lower bounds on RMSE/MAE '
        'rather than treating 500 as the measured value. Actual concentrations '
        'above the bound remain unknown. All endpoint scores and unsuccessful '
        'predictions are retained. These results identify effects of specific '
        'label assignments and computational weight interventions; they do '
        'not identify a causal antibacterial mechanism or an independent '
        'human-information channel before annotation provenance is supplied.')
    add('Architectural correction to main Methods: the pinned MolFormer pooler '
        'uses parameter-free mean pooling. Matched source fine-tuning trained '
        'upper eight blocks, the outer encoder LayerNorm and a scalar head '
        '(28,375,297 parameters), rather than a trainable pooler. Direct partial '
        'target fits additionally use a four-output head and head LayerNorm '
        '(28,379,140 parameters). The code and every original result are unchanged '
        'by correcting this description. Bibliographic correction: ChemFM’s '
        'second author is K. Zacour, replacing the earlier erroneous K. Hanna.')
    add('Table S33. Per-seed derivation of the primary human-guided censored-endpoint '
        'sensitivity from independently replayed predictions. Each seed has its own '
        'exact residuals and its own IT505 lower-bound error. All errors use log2(mg/L). '
        'The final row averages seed-specific RMSE values, not their predictions.')
    table(censor_table(censor_derivation()))
    add('For seed s, let SSE_s be the sum of squared residuals on its 67 exact '
        'pooled endpoints, and h_s = max(log2(500) − prediction_s(IT505 Ec_MBC), 0). '
        'Its 68-endpoint RMSE lower bound is sqrt((SSE_s + h_s²)/68). The Ec_MBC '
        'calculation uses its 16 exact residuals and denominator 17. Averaging '
        'the five seed-specific roots yields pooled 2.100536 (reported 2.101) '
        'and Ec_MBC 2.355897 (reported 2.356). The minimum error across seeds '
        'is not used as if it applied to every fitted model. The true unknown '
        'concentration may give a larger error.')
    v.TITLE = h.text(body[0]); v.unique_ids(tree); h.write(files,tree,SI)
    v.exports(files,tree,ROOT/'supplement_v16_readable.md',ROOT/'Supplementary_Information_v16.html')


def endpoint_table(summary, category, table):
    rows = [['Initialisation / adaptation','Regime / endpoint','Seeds / n','RMSE','MAE / R² / Spearman']]
    for _, r in summary[summary.task != 'pooled'].iterrows():
        adaptation = MODE[r[category]] if category == 'mode' else VARIANT[r[category]]
        rows.append([ARM[r.arm]+' / '+adaptation,r.schema+' / '+r.task,
                     f'{r.runs} / {r.n_exact}',fcell(r),
                     f'{fcell(r,"MAE")} / {r.R2:.3f} / {r.Spearman:.3f}'])
    table(rows)


def main():
    prepare_inputs()
    direct = pd.read_csv(ANALYSIS/'direct_summary.csv')
    ablation = pd.read_csv(ANALYSIS/'ablation_summary.csv')
    ci = pd.read_csv(ANALYSIS/'paired_bootstrap.csv')
    parameters = pd.read_csv(ANALYSIS/'parameters_and_budgets.csv')
    normal,template = build_main(direct,ablation,ci,parameters)
    build_si(normal,template,direct,ablation,ci,parameters)
    print(MAIN); print(SI)


if __name__ == '__main__':
    main()

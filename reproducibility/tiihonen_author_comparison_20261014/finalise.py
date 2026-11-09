"""Summarise completed predictions and document benchmark scope."""
from pathlib import Path
import hashlib,json,pickle,warnings
import numpy as np,pandas as pd
from rdkit import Chem,RDLogger

ROOT=Path(__file__).resolve().parent;COMA=ROOT.parents[1]
RDLogger.DisableLog('rdApp.*')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def parent_nostereo(s):
 m=Chem.MolFromSmiles(str(s))
 if m is None:return None
 parts=Chem.GetMolFrags(m,asMols=True,sanitizeFrags=True)
 pos=[x for x in parts if Chem.GetFormalCharge(x)>0]
 m=max(pos or parts,key=lambda x:x.GetNumHeavyAtoms())
 Chem.RemoveStereochemistry(m)
 return Chem.MolToSmiles(m)

def main():
 reg=pd.read_csv(ROOT/'endpoint_registry.csv');data=COMA/'Data_and_models/Data'
 full=pd.read_csv(data/'dataset_outliers_dropped.csv',index_col=0)
 raw=pd.read_excel(data/'04142021 5k descriptors.xlsx','SMILES').set_index('No.')
 # Original workbook identifiers (No.) preserve the lookup despite name edits.
 bounded=[]
 for _,row in reg.iterrows():
  no=full.loc[row.author_index,'no'];original=raw.loc[no]
  mic=str(original['MIC VALUE (Y VALUE)'])
  if mic.startswith('>'):
   bound=float(mic[1:]);expected=np.log2(2*bound)
   bounded.append(dict(author_index=int(row.author_index),split=row.split,
    raw_name=original.NAME,original_MIC=mic,imputed_MIC=2*bound,log2mic=float(row.log2mic),
    author_imputation_matches=bool(row.log2mic==expected)))
 pd.DataFrame(bounded).to_csv(ROOT/'author_censor_substitution.csv',index=False)
 overlap=[]
 expert=pd.read_csv(COMA/'expert_labels/expert_labels_1103.csv').canonical_smiles
 expert_keys={parent_nostereo(s) for s in expert};expert_keys.discard(None)
 for split,d in reg.groupby('split'):
  hit=d[[parent_nostereo(s) in expert_keys for s in d.smiles]]
  overlap.append(dict(source='expert1103',split=split,comparison='counterion-free and stereochemistry ignored',
   n_target_overlap=len(hit),author_indices=hit.author_index.tolist(),names=hit.name.tolist()))
 # Old locally owned scaler was saved in sklearn1.6; verify its stored affine map.
 with warnings.catch_warnings():
  warnings.simplefilter('ignore')
  scaler=pickle.load((COMA.parent/'Veresh_paper/scaler_classification.pkl').open('rb'))
  x=np.load(ROOT/'v5_raw_embeddings.npy');sc=scaler.transform(x)
 expected=((x.astype('float64')-scaler.mean_)/scaler.scale_).astype('float32')
 maxerr=float(np.max(np.abs(sc-expected)))
 assert np.allclose(sc,expected,atol=1e-5,rtol=1e-5)
 rf=pd.read_csv(ROOT/'rf_metrics.csv');mf=pd.read_csv(ROOT/'v5_metrics.csv')
 paper=rf[(rf.train=='author_descriptor_train80')&(rf.evaluation=='test20')].iloc[0]
 assert abs(paper.R2-.6491613775156464)<1e-12
 assert abs(paper.RMSE-1.093782292173194)<1e-12
 comparison=rf[rf.evaluation=='test20'][['model','train','n_train','n','R2','RMSE']].copy()
 mf=mf[mf.evaluation=='test'].copy();mf['train']='matched_valid_smiles_train78'
 comparison=pd.concat([comparison,mf[comparison.columns]],ignore_index=True)
 comparison.to_csv(ROOT/'comparison_test20.csv',index=False)
 validation=dict(completed=True,native_rf_matches_archived_paper_code_to_1e_12=True,
  references_and_descriptor_frame_all107_smiles_identical=bool(all(full.loc[r.author_index,'smiles']==r.smiles for _,r in reg.iterrows())),
  target_censoring_substitution_matches=bool(all(x['author_imputation_matches'] for x in bounded)),
  test20_censored_as_exact_by_author=len([x for x in bounded if x['split']=='test']),
  conservative_source_overlap=overlap,scaler_stored_affine_max_abs_error=maxerr,
  source_checkpoint_retrained_on_COE=False,catboost_test_tuning=False,
  old_quantitative_ft_not_used='3/20 test cations overlap old quantitative FT sources',
  original_manuscript_modified=False)
 (ROOT/'validation.json').write_text(json.dumps(validation,indent=2))
 lines=['# Сравнение с Tiihonen et al., JACS 2021','',
  'Завершено 14 октября 2026. Это отдельный набор COE / MIC E. coli K12, DOI [10.1021/jacs.1c05055](https://doi.org/10.1021/jacs.1c05055), а не Q-HERO.',
  '', 'Использована пользовательская локальная папка `COMA/Data_and_models`. Все 57 файлов совпадают побайтово с публичным архивом репозитория [PV-Lab/MLforCOE](https://github.com/PV-Lab/MLforCOE). Публичные pickle-модели не загружались: RF обучен заново из CSV.',
  '', '## Результат на одних и тех же 20 отложенных молекулах','',
  '| Процедура | Train | R² | RMSE log₂(mg/L) |','|---|---:|---:|---:|']
 for _,r in comparison.iterrows():
  label={'Author_RF21_refit':'RF авторов, 21 дескриптор','v5_raw_CatBoost':'Frozen MolFormer → CatBoost',
         'v5_human_CatBoost':'Frozen MolFormer → человеческий v5-адаптер → CatBoost'}[r.model]
  lines.append('| '+label+' | '+str(r.n_train)+' | '+format(r.R2,'.6f')+' | '+format(r.RMSE,'.6f')+' |')
 lines += ['', 'Человеческий адаптер улучшает исходные эмбеддинги, но в данном заранее фиксированном запуске не превосходит авторский RF. Даже RF, переобученный на тех же 78 RDKit-valid тренировочных структурах, сильнее обеих наших процедур. Ни исходный опубликованный R²=0.65, ни новый результат не являются оценками Q-HERO.',
  '', '## Что именно воспроизведено','',
  'RF80: сохранённый авторский split (80 train, 20 test), 21 опубликованный AlvaDesc-дескриптор; 236 деревьев, max_depth18, max_features log2, max_samples0.99, min_samples_split2, min_samples_leaf1, bootstrap=True, random_state3. criterion=mse заменён на современное тождественное имя squared_error. Полученные R²=0.6491613775156464 и RMSE=1.093782292173194 совпадают с footer публичного кода до 1e−12.',
  '', 'В Methods статьи заявлены 78 train, но descriptor CSV и опубликованный train_idx содержат 80. Два SMILES (author_index108 и109: COE-Y4IM2 иCOE-Y6IM2) не читаются RDKit. Сохранённый y_smiles_train_seed3.csv точно равен остальным 78. Поэтому отдельно обучен RF78 для контроля объёма и состава данных. Мы не исправляли эти структуры вручную и не добавляли искусственных эмбеддингов.',
  '', 'Raw/human: 78 train и те же20 test; фиксированный CatBoost500/depth6/lr0.05/seed42. Архитектура, scaler и human checkpoint взяты из v5; на COE адаптер не переобучался. MolFormer локальный, frozen, CPU, deterministic_eval; canonical SMILES, pooler_output, max_length202. Максимум168 токенов, обрезанных молекул0. Файлы, хеши и параметры сохранены в JSON. Подбора по20 test не было. Одного сохранённого адаптера и одного фиксированного decoderseed недостаточно для SD по независимым запускам; «±» не выдуман.',
  '', 'Старый локальный StandardScaler сохранён sklearn1.6.1, прочитан1.3.2; его transform дополнительно проверен по сохранённым mean_/scale_ (см.validation.json). Публичные pickle-файлы не исполнялись.',
  '', '## Границы сравнения','',
  '- Единицы авторов µg/mL численно равны mg/L. Это не молярный пересчёт Q-HERO.',
  '- Два тестовых MIC были >64µg/mL. По авторскому правилу они заменены128 (log₂=7); это репликация авторского benchmark, а не censor-aware анализ20 точных значений. Все такие замены сохранены в author_censor_substitution.csv.',
  '- Human1103 source:0/20 тестовых катионов,2/78 тренировочных,1/7 newdata. Ноль пересечений test сохраняется после удаления стереохимии. Это аудит известного human-source, а не аудит всего огромного pretraining-корпуса MolFormer. Фактическое train/validation-членство каждой source-молекулы в историческом checkpoint восстановлено не полностью.',
  '- Старые quantitative FT checkpoint не использованы: их source содержат3/20 тестовых COE-катионов. Нужен новый source-excluded fit для честного сравнения количественного fine-tuning.',
  '- В архивах y_opt_newdata7, а не15 из статьи. Среди этих7 Amethyl уже есть в human-source, поэтому их нельзя объявлять полностью независимым human-transfer тестом. Вторичные результаты7 сохранены, но не смешаны с test20 и не заменяют опубликованные15.',
  '- Test20 — один небольшой авторский split; результаты не доказывают универсального превосходства архитектур или причинного механизма. Авторский отбор21 дескриптора и оптимизация RF имеют собственный budget; наши процедуры используют заранее зафиксированный бюджет.',
  '', 'Основной текст v20 и SI не изменены. Независимый фактический Claude Sonnet4.6 работал через локальный CLI Mac; исходный ответ, метаданные и разбор принятых/исправленных замечаний находятся в reviews/.', '']
 (ROOT/'README_RU.md').write_text('\n'.join(lines))
 print(comparison.to_string(index=False));print('validation complete')

if __name__=='__main__':main()

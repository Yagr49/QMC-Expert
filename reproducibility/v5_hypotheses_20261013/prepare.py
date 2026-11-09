"""Package v5 artifacts and fixed hypothesis checks; no API or upstream retraining."""
from pathlib import Path
import hashlib,json,pickle,shutil
import numpy as np,pandas as pd,torch
from torch import nn
from rdkit import Chem
from sklearn.model_selection import GroupShuffleSplit,GroupKFold

ROOT=Path(__file__).resolve().parent;COMA=ROOT.parents[1];REPRO=ROOT.parent
V14=REPRO/'revision_v14';ARCHIVE=COMA.parent/'Veresh_paper'
TASKS=['Sa_MIC','Sa_MBC','Ec_MIC','Ec_MBC']
COLS=['S. aureus ATCC 43300 Activity MIC, мг/л','S. aureus ATCC 43300 Activity MBC, мг/л',
      'E. coli ATCC 25922 Activity MIC, мг/л','E. coli ATCC 25922 Activity MBC, мг/л']
INPUTS={}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def note(path):INPUTS[str(path)]=sha(path);return Path(path)

class HistoricalEncoder(nn.Module):
 def __init__(self):
  super().__init__();layers=[];previous=768
  for width in [512,384,256]:
   layers.extend([nn.Linear(previous,width),nn.BatchNorm1d(width),nn.ReLU(),nn.Dropout(.3)]);previous=width
  self.encoder=nn.Sequential(*layers)
  self.projection_head=nn.Sequential(nn.Linear(256,128),nn.BatchNorm1d(128),nn.ReLU(),
                                    nn.Dropout(.15),nn.Linear(128,128),nn.BatchNorm1d(128))

def main():
 data=ROOT/'data';data.mkdir(parents=True,exist_ok=True)
 for name in ['QAC105.csv','OOD17.csv','endpoint_registry.csv','task_text_embeddings.npy','task_text_embeddings.json']:
  shutil.copyfile(note(V14/'data'/name),data/name)
 q=pd.read_csv(data/'QAC105.csv');o=pd.read_csv(data/'OOD17.csv')
 q['scaffold_fold']=0
 for fold,(_,te) in enumerate(GroupKFold(n_splits=5).split(q,groups=q.scaffold)):q.loc[te,'scaffold_fold']=fold
 q.to_csv(data/'QAC105.csv',index=False)
 for prefix in ['legacy-raw','legacy-human','legacy-quantitative']:
  # legacy-quantitative is the saved QAC activity-only ablation, not the
  # missing full measured-corpus multitarget checkpoint from original Table 2.
  dest={'legacy-raw':'v5_raw','legacy-human':'v5_human','legacy-quantitative':'v5_qac_ablation'}[prefix]
  for cohort in ['QAC105','OOD17']:
   shutil.copyfile(note(V14/'representations'/(prefix+'_'+cohort+'.npy')),data/(dest+'_'+cohort+'.npy'))
 original=pd.read_excel(note(ARCHIVE/'Data_biocides.xlsx'))
 raw=pd.read_excel(note(ARCHIVE/'Test_molformer_original_biocides.xlsx')).drop(columns=['Unnamed: 0']).to_numpy(dtype=np.float32)
 assert len(original)==len(raw)==108
 scaler=pickle.load(note(ARCHIVE/'scaler_classification.pkl').open('rb'))
 net=HistoricalEncoder();net.load_state_dict(torch.load(note(ARCHIVE/'encoder_borderline_smote.pth'),map_location='cpu',weights_only=False));net.eval()
 with torch.no_grad():human=net.encoder(torch.tensor(scaler.transform(raw),dtype=torch.float32)).numpy()
 net.load_state_dict(torch.load(note(COMA/'analysis/encoder_reg_only.pth'),map_location='cpu',weights_only=False));net.eval()
 with torch.no_grad():activity=net.encoder(torch.tensor(scaler.transform(raw),dtype=torch.float32)).numpy()
 canonical=[Chem.MolToSmiles(Chem.MolFromSmiles(str(s))) for s in original['General formula']]
 rows=[]
 for task,col in zip(TASKS,COLS):
  for i,value in enumerate(pd.to_numeric(original[col],errors='coerce')):
   if np.isfinite(value) and value>0:rows.append(dict(molecule_index=i,compound_id='original_row_'+str(i),can=canonical[i],task=task,y=float(np.log2(value)),qualifier='='))
 pd.DataFrame(rows).to_csv(data/'original108_endpoints.csv',index=False)
 for name,a in [('v5_raw',raw),('v5_human',human),('v5_qac_ablation',activity)]:np.save(data/(name+'_original108.npy'),a)
 source=pd.read_csv(note(REPRO/'revision_v12/data/matched-pooled_expert.csv'))
 quant=pd.read_csv(note(REPRO/'revision_v12/data/matched-pooled_quant.csv'))
 assert source.can.tolist()==quant.can.tolist()
 train,val=next(GroupShuffleSplit(n_splits=1,test_size=.15,random_state=1729).split(source,groups=source.scaffold))
 assert len(train)==377 and len(val)==304
 assert not set(source.cation)&(set(q.cation)|set(o.cation))
 source['quant_y']=quant.y.to_numpy();source['source_split']='validation';source.loc[train,'source_split']='train'
 source.to_csv(data/'matched_source.csv',index=False)
 smiles=json.loads(note(REPRO/'revision_v9/data/smiles.json').read_text())
 matrix=np.load(note(REPRO/'revision_v9/data/molformer.npy'));lookup={s:i for i,s in enumerate(smiles)}
 for name,frame in [('source',source),('QAC105',q),('OOD17',o)]:
  assert set(frame.can).issubset(lookup)
  np.save(data/('matched_raw_'+name+'.npy'),matrix[[lookup[s] for s in frame.can]])
 metadata=dict(base='2026_07_09_Paper_2_edited-v5_NF_3.docx',decoder=dict(iterations=500,depth=6,learning_rate=.05,random_seed=42),
  original_rows=108,unique_full_salts=105,cations=103,OOD=17,exact_OOD_endpoints=67,
  archived_human_checkpoint=str(ARCHIVE/'encoder_borderline_smote.pth'),
  full_measured_corpus_Table2_checkpoint='Not located; reported table and notebook retained as provenance',
  qac_ablation_checkpoint='analysis/encoder_reg_only.pth; distinct from measured-corpus multitarget model',
  text_cache='Fresh reconstruction of cell-8 descriptions; original cell-17 cache absent. Replay is approximate, not an exact notebook execution.',
  source=dict(molecules=681,train=377,validation=304,positive_train=int(source.y.iloc[train].sum())),
  compact_controls=dict(encoder=[768,512,384,256],projection=[256,128,128],epochs=80,batch_size=64,
   paired_source_seeds=list(range(5)),source_scaler='Fit only on 377 training molecules',
   original_training_difference='Uniform source batches; no SMOTE, augmentation or early stopping, to fix molecule exposure and final budget.',
   objective='April hard-negative contrastive loss temp .05, alpha .3 for human/binary MIC; standardised MSE for continuous MIC',
   continuous_objective_difference=True),inputs_sha256=INPUTS)
 (data/'manifest.json').write_text(json.dumps(metadata,indent=2))
 (ROOT/'input_manifest.json').write_text(json.dumps(INPUTS,indent=2))
 print(json.dumps(dict(original_pairs=len(rows),source=len(source),train=len(train),validation=len(val),ready=True),indent=2))

if __name__=='__main__':main()

import os,sys
from pathlib import Path
R=Path(__file__).resolve().parent
os.environ['HF_HOME']=str(R/'runtime/hf');os.environ['HF_HUB_DISABLE_XET']='1';os.environ['TOKENIZERS_PARALLELISM']='false'
# Task-scoped libraries, base numpy/pandas, user torch; avoid incompatible optional torchvision.
sys.path.insert(0,str(R/'deps'));sys.path.append('/home/yagr/.local/lib/python3.12/site-packages');sys.modules['torchvision']=None
import json,hashlib,time
import numpy as np
import torch
from huggingface_hub import HfApi,snapshot_download
from transformers import AutoModel,AutoTokenizer
MODELS=[('c3-molformer','DeepChem/MoLFormer-c3-1.1B','pooler'),('chemberta100m','DeepChem/ChemBERTa-100M-MLM','mean'),('chemfm1b','ChemFM/ChemFM-1B','last')]
smis=json.loads((R/'data/smiles.json').read_text());torch.set_num_threads(4);torch.manual_seed(1729)
for label,repo,pooling in MODELS:
 out=R/'data'/f'{label}.npy'
 if out.exists(): print('cached',label,flush=True);continue
 revision=HfApi().model_info(repo).sha
 print('DOWNLOAD',repo,revision,flush=True)
 path=snapshot_download(repo,revision=revision,allow_patterns=['*.json','*.safetensors','*.py','*.model','*.txt'])
 code_revision='7b12d946c181a37f6012b9dc3b002275de070314' if pooling=='pooler' else None
 tok=AutoTokenizer.from_pretrained(path,trust_remote_code=True,use_fast=False,code_revision=code_revision)
 if tok.pad_token_id is None:tok.pad_token=tok.eos_token
 tok.padding_side='right'
 lengths=[len(v) for v in tok(smis,truncation=False)['input_ids']]
 kwargs={'trust_remote_code':True,'torch_dtype':torch.float16 if pooling=='last' else torch.float32,'output_loading_info':True,'code_revision':code_revision}
 if pooling=='pooler':kwargs['deterministic_eval']=True
 model,info=AutoModel.from_pretrained(path,**kwargs)
 context=int(getattr(model.config,'max_position_embeddings',512))
 if max(lengths)>context:raise ValueError((label,max(lengths),context))
 if pooling=='pooler':
  for module in model.modules():
   if hasattr(module,'deterministic'):module.deterministic=True
 model=model.to('cuda').eval();features=[];start=time.time();batchsize=8 if pooling=='last' else 32
 with torch.inference_mode():
  for i in range(0,len(smis),batchsize):
   b=tok(smis[i:i+batchsize],padding=True,truncation=False,return_tensors='pt').to('cuda')
   if pooling=='last':b.pop('token_type_ids',None)
   o=model(**b);h=o.last_hidden_state
   if pooling=='last':v=h[torch.arange(h.shape[0],device=h.device),b.attention_mask.sum(1)-1]
   elif pooling=='mean':v=(h*b.attention_mask.unsqueeze(-1)).sum(1)/b.attention_mask.sum(1,keepdim=True)
   else:v=o.pooler_output
   features.append(v.float().cpu().numpy())
   if i%128==0:print(label,min(i+batchsize,len(smis)),round(time.time()-start,1),flush=True)
 x=np.vstack(features).astype('float32');assert len(x)==len(smis) and np.isfinite(x).all();np.save(out,x)
 meta={'model':repo,'revision':revision,'remote_code_revision':code_revision,'pooling':pooling,'shape':list(x.shape),'max_tokens':max(lengths),'context':context,'truncated':0,'dtype':str(next(model.parameters()).dtype),'parameters':sum(p.numel() for p in model.parameters()),'loading_info':info,'torch':torch.__version__,'seconds':time.time()-start,'smiles_sha256':hashlib.sha256((R/'data/smiles.json').read_bytes()).hexdigest(),'features_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
 (R/'data'/f'{label}_meta.json').write_text(json.dumps(meta,indent=2,default=str));print('DONE',label,x.shape,flush=True)
 del model;torch.cuda.empty_cache()

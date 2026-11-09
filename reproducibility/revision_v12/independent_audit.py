"""Independent standard-library metric, identity and budget audit (no ML stack)."""
import argparse,csv,json,math,hashlib,statistics,platform
from pathlib import Path
from collections import defaultdict

def read(path):
    with open(path,newline='') as f:return list(csv.DictReader(f))
def groups(rows,fields):
    out=defaultdict(list)
    for row in rows:out[tuple(row[k] for k in fields)].append(row)
    return out
def ranks(values):
    out=[0.]*len(values);order=sorted(range(len(values)),key=lambda i:values[i]);i=0
    while i<len(order):
        j=i+1
        while j<len(order) and values[order[j]]==values[order[i]]:j+=1
        r=(i+1+j)/2
        for k in order[i:j]:out[k]=r
        i=j
    return out
def rho(x,y):
    a=ranks(x);b=ranks(y);ma=statistics.mean(a);mb=statistics.mean(b)
    cov=sum((u-ma)*(v-mb) for u,v in zip(a,b))
    return cov/math.sqrt(sum((u-ma)**2 for u in a)*sum((v-mb)**2 for v in b))
def auc(labels,scores):
    r=ranks(scores);n1=sum(labels);n0=len(labels)-n1
    return (sum(v for v,k in zip(r,labels) if k)-n1*(n1+1)/2)/(n0*n1)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parent);a=ap.parse_args()
    root=a.root;r=root/'results';m=json.loads((r/'manifest.json').read_text());assert m['completed']
    p=read(r/'predictions.csv');dp=read(r/'direct_predictions.csv');metrics=read(r/'metrics.csv');direct=read(r/'direct_metrics.csv')
    assert len(metrics)==93 and len(p)==16306 and len(direct)==90 and len(dp)==15780
    by_metric={tuple(d[k] for k in ['arm','seed','target']):d for d in metrics};errors=[]
    for key,rows in groups(p,['arm','seed','target']).items():
        y=[float(d['y']) for d in rows];pred=[float(d['pred']) for d in rows]
        se=sum((u-v)**2 for u,v in zip(y,pred));mean=statistics.mean(y);sst=sum((u-mean)**2 for u in y)
        rmse=math.sqrt(se/len(rows));r2=1-se/sst;d=by_metric[key]
        errors.extend([abs(rmse-float(d['RMSE'])),abs(r2-float(d['R2']))])
        assert len(rows)==int(d['n']) and len({d['can'] for d in rows})==len(rows)
    by_direct={tuple(d[k] for k in ['arm','seed','target']):d for d in direct};rank_errors=[];auc_errors=[]
    for key,rows in groups(dp,['arm','seed','target']).items():
        y=[float(d['y']) for d in rows];rankscore=[float(d['rank_score']) for d in rows];d=by_direct[key]
        rank_errors.append(abs(rho(y,rankscore)-float(d['rank_agreement'])))
        active=[int(v<statistics.median(y)) for v in y]
        auc_errors.append(abs(auc(active,[-v for v in rankscore])-float(d['AUC'])))
    assert max(errors)<1e-10 and max(rank_errors)<1e-10 and max(auc_errors)<1e-10
    training=read(r/'training.csv');assert len(training)==30
    for seed,rows in groups(training,['seed']).items():
        assert len(rows)==6
        for field in ['initial_sha256','batch_order_sha256','train_id_sha256']:assert len({d[field] for d in rows})==1
    assert all(int(d['updates'])==360 and int(d['epochs'])==30 for d in training)
    source=read(root/'data/matched-pooled_expert.csv');quant=read(root/'data/matched-pooled_quant.csv')
    assert len(source)==681 and [(d['can'],d['cation'],d['scaffold']) for d in source]==[(d['can'],d['cation'],d['scaffold']) for d in quant]
    cations=set()
    for target in ['QAC-104','Q-HERO-405','OOD-17']:cations.update(d['cation'] for d in read(root/'data'/f'target_{target}.csv'))
    assert not cations & {d['cation'] for d in source}
    split=read(r/'source_split.csv');by_split=groups(split,['partition'])
    assert len(by_split[('train',)])==377 and len(by_split[('validation',)])==304
    assert not {d['scaffold'] for d in by_split[('train',)]} & {d['scaffold'] for d in by_split[('validation',)]}
    folds=read(root/'data/target_folds.csv')
    target_groups={name:{d['can']:d['scaffold'] for d in read(root/'data'/f'target_{name}.csv')} for name in ['QAC-104','Q-HERO-405']}
    for target in target_groups:
        d=[row for row in folds if row['target']==target];seen={}
        for row in d:
            scaffold=target_groups[target][row['can']]
            if scaffold in seen:assert seen[scaffold]==row['fold']
            seen[scaffold]=row['fold']
        assert len(d)==len(target_groups[target]) and len({row['can'] for row in d})==len(d)
    for name,digest in m['output_sha256'].items():assert hashlib.sha256((r/name).read_bytes()).hexdigest()==digest
    report=dict(passed=True,python=platform.python_version(),dependencies='standard library only',
        downstream_metrics=93,direct_metrics=90,prediction_rows=16306,direct_prediction_rows=15780,
        max_metric_difference=max(errors),max_rank_difference=max(rank_errors),max_auc_difference=max(auc_errors),
        paired_initialisation_batches_and_updates=True,source_target_cation_overlap=0,source_and_target_partitions_audited=True,
        original_output_checksums_valid=True,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (root/'independent_audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

if __name__=='__main__':main()

"""Replace Figure2 with a faithful vector-source redraw; retain the raster as archive."""
from pathlib import Path
import copy,hashlib,importlib.util,json,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parent;COMA=ROOT.parents[1];OLD=ROOT.parent/'revision_v19'
s=importlib.util.spec_from_file_location('old',OLD/'build_revision.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
v,h,NS=b.v,b.h,b.NS
MAIN=COMA/'2026_10_13_Paper_2_edited-v20_soft_contrastive_figure.docx';SI=ROOT/'Supplementary_Information_v20.docx'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 files,tree,body=v.read_doc(b.MAIN);source_files={k:value for k,value in files.items()}
 caption=next(p for p in body if h.text(p).startswith('Figure 2.'));index=list(body).index(caption);old_image=copy.deepcopy(list(body)[index-1])
 assert len(old_image.findall('.//wp:docPr',NS))==1
 new_image=v.embed(files,ROOT/'figures/figure2_contrastive_before_after_soft.png','rIdV20Contrastive')
 body.remove(list(body)[index-1]);body.insert(index-1,new_image)
 text=('Figure 2. Soft redraw of the archived before/after contrastive-learning visualisation. '
  'All 221 scatter-marker positions per panel are recovered directly from publication_tsne_before_after.pdf: '
  '172 Bad and 49 Good observations. Only typography, marker styling and layout are changed; no t-SNE is rerun. '
  'The PDF reports silhouette 0.007→0.107; the original manuscript raster reports 0.108 after training and is retained in Figure S31. '
  'These are archive-specific classification-geometry summaries, not quantitative regression or causal-performance metrics.')
 h.replace(caption,text)
 paragraph=next(p for p in body if h.text(p).startswith('The archived t-SNE analysis'))
 h.replace(paragraph,('The archived t-SNE visualisation illustrates the molecular representation before and after expert-guided refinement (Figure 2). '
  'The figure is redrawn from the exact scatter-marker centres in the original vector PDF, preserving all 221 observations and their class assignments. '
  'That PDF prints silhouette 0.007→0.107, while the original manuscript raster prints 0.108 after training; both source versions are documented, '
  'and the raster is retained in Figure S31. The original analysis also reports Davies–Bouldin index 6.54→2.58 and Calinski–Harabasz score 3.60→22.08. '
  'Those reported values are not recomputed from display coordinates. They describe class-associated geometry, rather than quantitative regression '
  'performance or acquisition of an antibacterial mechanism. Figure 6 uses the different 105-QAC cohort and colours structural classes rather than activity labels.'))
 # State the comparator explicitly: TabFM improves the raw/separate baseline.
 for node in body:
  text=h.text(node)
  if text.startswith('None of the modern tabular pipelines consistently improves'):
   h.replace(node,('Relative to archived human/text CatBoost (Table 3), no tested tabular pipeline has lower point-estimate loss in all three regimes. '
    'Against the separate-endpoint raw CatBoost reference in Table 5 and Figure 8, however, TabFM gives lower cation/scaffold/OOD RMSE '
    '(1.903/2.080/2.118 versus 1.916/2.086/2.208). Modern decoders can therefore improve that specific pipeline, while human/text CatBoost '
    'retains the lower OOD point estimate of 2.023. TabPFN with raw features gives OOD RMSE 2.058 versus 2.165 with human-guided features; '
    'AutoGluon gives 2.163 versus 2.081, showing decoder-dependent ordering. These are point comparisons, not tests of statistical superiority. '
    'Chemprop’s graph benchmark (84) and RDKit alternatives on the same 105/17 target registers remain in SI and are not relabelled as compact-encoder experiments.'))
  elif text.startswith('Third, modern decoders and direct fine-tuning'):
   old_sentence=next(sentence for sentence in text.split('. ') if sentence.startswith('None of the tested tabular models'))
   h.replace(node,text.replace(old_sentence,
    'Relative to the archived human/text CatBoost reference, none of the tested tabular pipelines improves all three point-estimate losses; TabFM nevertheless improves the separate-endpoint raw CatBoost baseline'))
 v.unique_ids(tree);h.write(files,tree,MAIN);v.TITLE=b.b.TITLE
 v.exports(files,tree,ROOT/'manuscript_v20_readable.md',ROOT/'manuscript_v20.html')
 sif,sit,sib=v.read_doc(b.SI);normal=next(p for p in sib if h.text(p));p=lambda text,level=None:v.paragraph(normal,text,level)
 safe=b.b.previous.import_blocks
 image=safe(sif,source_files,[old_image],'V20ArchivedTSNE',distinct_styles=True)[0]
 new=[p('S33. Before/after figure sources and graphic-only redraw',1),
  p('The revised main Figure2 uses exact vector marker centres from publication_tsne_before_after.pdf, with no new dimensionality reduction. '
    'The PDF contains 221 marker calls in each panel (172 Bad,49 Good) and prints silhouette 0.007/0.107. '
    'The original Word raster below instead prints 0.108 for the after panel. The archive variants are not silently equated. '
    'Display-point coordinates do not recover molecule identifiers or the original high-dimensional features, and are not used to recalculate cluster metrics. '
    'All previous predictive metrics, uncertainty intervals and tables remain unchanged.'),
  image,p('Figure S31. Original v5 before/after contrastive-learning raster, retained byte-for-byte. '
    'Its printed silhouette after training is 0.108; the vector-PDF variant redrawn in main Figure2 prints 0.107. '
    'The old raster remains available as source provenance, not as a new calculation.')]
 sec=sib.find('w:sectPr',NS);h.add_sequence(sib,sec,new);v.add_styles(sif);v.unique_ids(sit);h.write(sif,sit,SI)
 v.exports(sif,sit,ROOT/'supplement_v20_readable.md',ROOT/'Supplementary_Information_v20.html')
 (ROOT/'revision_manifest.json').write_text(json.dumps(dict(base_main=str(b.MAIN),base_main_sha256=sha(b.MAIN),base_SI=str(b.SI),base_SI_sha256=sha(b.SI),
  main=str(MAIN),main_sha256=sha(MAIN),SI=str(SI),SI_sha256=sha(SI),figure='Figure2',original_raster_retained='FigureS31',
  no_prediction_metrics_changed=True,tabular_comparator_scope_clarified=True,no_new_QHERO_content_added=True,style='Aptos, muted peach and mint, white background, minimal labels',
  coordinate_source='tsne_source_provenance.json',no_points_selected_added_or_moved_within_panel=True),indent=2))
 # Keep the latest chapter file linked to the correct revision.
 note=('v20: Figure2 перерисована в Aptos с мягкими персиковыми/мятными точками из оригинального векторного PDF. '
  'Сохранены все 221 точки каждой панели. В PDF после обучения silhouette 0.107, в исходном Word-рисунке 0.108; '
  'варианты указаны явно, старый рисунок сохранён в SI FigureS31. Метрики предсказания и ± из v19 не менялись. '
  'Уточнён компаратор табличных моделей: TabFM улучшает raw/separate CatBoost во всех трёх режимах по точечным значениям; '
  'human/text CatBoost сохраняет меньшую OOD-ошибку.\n\n')
 (ROOT/'ARTICLE_BY_CHAPTERS_RU.txt').write_text(note+(OLD/'ARTICLE_BY_CHAPTERS_RU.txt').read_text().replace('СТАТЬЯ v19:','СТАТЬЯ v20:'))
 (ROOT/'README_RU.md').write_text(note+'Рисунки: figures/figure2_contrastive_before_after_soft.{pdf,svg,png}; второй вариант: *_lavender.*. '
  'Контроль происхождения и координат: tsne_source_provenance.json, tsne_style_validation.json. Q-HERO обсуждён отдельно в чате; новых его результатов в статью/SI не добавлено.\n')
 print('Saved main v20 and SI; all numerical tables unchanged.')
if __name__=='__main__':main()

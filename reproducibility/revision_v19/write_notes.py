"""Keep the user-facing guide in sync with the new uncertainty definitions."""
from pathlib import Path
import hashlib,importlib.util,json,re
ROOT=Path(__file__).resolve().parent;OLD=ROOT.parent/'revision_v18'
s=importlib.util.spec_from_file_location('builder',ROOT/'build_revision.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
note='''Что добавлено в v19.

Tables 1–2: три отдельные новые строки пятифолдовой CV сохранённого человеческого encoder: task_id, organism+endpoint и text codes. Каждая RMSE/R² имеет собственное среднее ± SD по пяти фолдам. Это 30 новых CatBoost fit с вашим бюджетом 500/depth6/lr0.05/seed42. Сохранённое обучение encoder с SMOTE не изменялось; для текста используется восстановленный октябрьский кэш. Первые строки таблиц остаются вашими исходными holdout-числами; CV-разброс к ним не приписывается.

Table 4: среднее ± SD по пяти полным source-seed запускам. Например, Human: cation 1.872±0.034, scaffold 2.158±0.050, OOD 2.268±0.077. Это разброс обучения моделей, а не разброс CV-фолдов.

Table 6: среднее ± SD по трём парным source/target запускам. Оба маршрута human partial сравниваются на seed 0–2.

Исходный probing: восстановлены ваши сохранённые R² 0.891±0.037 и 0.844±0.060 по пяти CV-фолдам. Это восстановление координат embedding, а не MIC/MBC performance.

SI Tables S40–S44: полные fold metrics, source-seed variability, grouped fold variability, original probing и соответствие новых опытов вашим подходам. Fold SD используется с numpy.std ddof=0, как в вашем CV-коде; SD повторных source-run — sample SD ddof=1. Оба вида ± не являются автоматически 95% доверительными интервалами; прежние bootstrap CI сохранены отдельно.

Новые вычислительные данные получены на ваших целевых наборах: 105 QAC и 17 OOD. Для реконструкции исходной CV используется прежний spreadsheet-view из 108 строк, представляющих 105 уникальных солей. В row-wise CV разные задачи одной молекулы могут быть по обе стороны разбиения; grouped evaluation остаётся отдельной проверкой новых молекул.

Основа новых расчётов — ваш frozen MolFormer → compact encoder → task-aware CatBoost. Matched source-control сохраняет архитектуру, но меняет source panel и не использует SMOTE; direct fine-tuning и новые графовые/табличные модели — самостоятельные сравнения. Точное соответствие находится в SI Table S44.
'''
def main():
 old=(OLD/'ARTICLE_BY_CHAPTERS_RU.txt').read_text().replace('СТАТЬЯ v18:','СТАТЬЯ v19:')
 (ROOT/'ARTICLE_BY_CHAPTERS_RU.txt').write_text(note+'\n'+old)
 (ROOT/'README_RU.md').write_text(note+'\nОсновной файл: `../../'+b.MAIN.name+'`. SI: `'+b.SI.name+'`. Проверки: `document_validation.json`. Исходный v5 и v18 сохранены. Новые CV-результаты: `rowcv_results/`, отдельные fold/seed summaries: `analysis/`.\n')
 # Match summaries to paragraph text, so inserted CV paragraphs cannot shift the mapping silently.
 previous=json.loads((OLD/'paragraph_walkthrough.json').read_text())['paragraphs']
 mapping={r['source_text']:r['summary_ru'] for r in previous}
 _,_,body=b.v.read_doc(b.MAIN);records=[];out=[note,'Краткий разбор содержательных абзацев.',''];section=''
 for i,node in enumerate(body):
  text=b.h.text(node)
  if re.match(r'^(?:[1-3]\. |2\.\d|4\.3)',text):section=text
  ru=mapping.get(text)
  if text.startswith('The archived representation analysis reports'):ru='CKA и probing показывают геометрическую связь с MolFormer. Возвращены исходные пятьфолдовые R²±SD: 0.891±0.037 и 0.844±0.060; они не являются MIC/MBC метриками.'
  if text.startswith('To restore the author’s uncertainty-reporting approach'):ru='Добавлен отдельный пятифолдовый повтор вашего подхода. Собственные CV-mean±SD стоят рядом с исходными holdout-значениями; свежий text-cache и среда делают это approximate reconstruction.'
  if text.startswith('Uncertainty notation follows'):ru='Различаем fold SD, source-seed SD и 95% bootstrap intervals. У одного OOD запуска нет фолдового или межseedового разброса.'
  if ru:
   records.append(dict(native_body_index=i,section=section,source_text=text,summary_ru=ru));out.extend([f'{section} — абзац ({i})',ru,''])
 assert len(records)==62,len(records)
 (ROOT/'ARTICLE_BY_PARAGRAPHS_RU.md').write_text('\n'.join(out))
 (ROOT/'paragraph_walkthrough.json').write_text(json.dumps(dict(manuscript_sha256=hashlib.sha256(b.MAIN.read_bytes()).hexdigest(),paragraphs=records),ensure_ascii=False,indent=2))
 print('Notes and',len(records),'paragraph summaries saved')
if __name__=='__main__':main()

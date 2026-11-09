"""Russian paragraph guide linked to the final native document's body indices."""
from pathlib import Path
import hashlib,importlib.util,json,re
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('builder',ROOT/'build_revision.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
SUMMARIES={
12:'Вводим проблему антибиотикорезистентности и ограниченного инновационного pipeline. Отделяем системные антибиотики из отчётов WHO от исследуемых топических биоцидов.',
13:'Показываем, почему ML полезен для поиска антибактериальных соединений и оптимизации их свойств; сохраняем литературный вход исходного v5.',
14:'Объясняем разные способы внесения domain knowledge: физические ограничения, химические признаки и биологические связи. Это мотивирует сравнение видов информации.',
15:'Переходим от ограничений модели к человеческому суждению как метке обучения. MolSkill и другие работы мотивируют проверку Good/Bad для последующей количественной регрессии.',
16:'Связанные виды бактерий и MIC/MBC можно моделировать совместно. Текстовые коды задач проверяем отдельно от простого указания task identity.',
17:'Численные данные неоднородны по протоколам. Эксперт потенциально может их обобщать, но это не установленный факт без записей о сборе разметки.',
18:'Обосновываем выбранную химическую задачу: катионные биоциды QAC и предыдущие ML-подходы в этой области.',
19:'Связываем предыдущую QAC-работу с новым вопросом: откуда приходит полезная информация для представления. Обозначаем последовательность исходных результатов и новых проверок.',
21:'Подробно объясняем три объекта: frozen MolFormer выдаёт 768 признаков; внешний encoder создаёт 256; количественный decoder использует эти признаки и код задачи. Source-метки не нужны для inference новой молекулы.',
22:'Определяем внешний адаптер признаков и отличаем его от LoRA, partial и full fine-tuning. Меньшая модель не гарантирует лучшее качество; это проверяем.',
28:'В финальном архиве 1103 Good/Bad. Старые утверждения про 1500 соединений, три голоса и blind collection должны подтвердить соавторы.',
29:'Классификационный screen мотивирует MolFormer. Цитируем именно F1=0.665 на сохранённом SI-графике; 0.655 и accuracy 0.856 из текста имеют отдельный исторический статус.',
30:'Возвращаем contrastive encoder v5 с BatchNorm, ReLU, dropout и историческим Borderline SMOTE. Отличаем encoder output от projection head и регрессионного decoder.',
31:'Сохраняем t-SNE и cluster metrics как геометрический анализ. Это не доказательство качества регрессии или причинного знания механизма.',
36:'Исходные embeddings предсказывают четыре log2 endpoint. В восстановленном CatBoost task_id — native categorical; literal one-hot имеет отдельную новую проверку.',
37:'Показываем подтверждённые сохранённым майским выводом сильные R² human/text и human/categorical. Исправляем округление 0.5918→0.59; не заявляем воспроизведение всех старых RMSE.',
42:'Сохраняем исходные parity-панели. Их выигрыш мотивирует проверки, но не устанавливает перенос на новые бактерии или новые виды активности.',
46:'Возвращаем сравнение с большой количественной multitarget моделью. Её checkpoint пока не найден; это не доказательство, что старая таблица использовала другую модель.',
47:'Разводим 1559 молекул, >18000 смешанных activity records и MIC-only экспорт 9338 записей/1153 молекулы. Число записей не равно числу независимых структур.',
48:'Старые human/text R² конкурентоспособны с количественными. Разница 0.59 vs 0.58 описательная; формальной эквивалентности или десятикратной экономии она не доказывает.',
49:'Интерпретация Good/Bad как обобщения измерений условна. Если эксперты видели те же числа, разметка является человеческим сжатием этих данных, а не независимым каналом.',
55:'Новые 17 соединений относятся к четырём семействам. В untouched OOD остаются 67 точных значений и одна граница IT505 E. coli MBC >500.',
58:'Описываем архитектуру QAC: core, tail, linker и три класса по количеству катионных центров.',
59:'Вводим четыре выбранных гетероциклических scaffold и их экспериментальную оценку MIC/MBC.',
61:'Сохраняем путь синтеза kojic-acid bis-QACs: димеризация, хлорирование и кватернизация с алкиламинопиридинами.',
66:'Сохраняем multicomponent synthesis tetrahydropyridine-платформ и дальнейшую реакцию Menshutkin.',
69:'Объясняем оптимизацию синтеза, конкурирующий pyran и эпимеризацию. Вспомогательные химические SI-материалы зарезервированы для соавторов.',
71:'Сохраняем синтез CF3-dihydropyran mono-QACs и последующее N-алкилирование.',
76:'Сохраняем четырёхстадийный путь glycoluril multi-QACs. Исправляем подпись схемы, которая ошибочно называла их mono-QACs.',
81:'Сохраняем исходный OOD benchmark и различаем regression, classification и ±1-class agreement. Label-free там означает отсутствие task-code, а не отсутствие target training.',
82:'Уточняем старые zero-shot/few-shot термины. Few-shot использует часть OOD и является отдельным exploratory опытом; новые проверки не обучаются на этих 17 молекулах.',
86:'Ставим вопрос о геометрии и предсказательной роли embeddings. Новая PCA-картинка показывает реальные 105 молекул, не причинное разделение знания.',
89:'CKA 0.933/0.946 и probing 0.891 показывают выравнивание и линейную восстанавливаемость признаков. Остаток нельзя назвать биологическим знанием.',
90:'Сохраняем старый SHAP, но не трактуем отношение вкладов 0.22 как причинную долю информации. Коррелированные блоки могут перераспределять attribution.',
91:'Разделяем QAC-only binned ablation, полную quantitative модель, майский/июльский архив и новый расчёт. CausalForest и bootstrap ΔRMSE — разные анализы.',
92:'На 17 молекулах subgroup effects ограниченно оцениваются. Отсутствие resolved advantage не доказывает отсутствия гетерогенности.',
93:'Сохраняем исходную идею полезного направленного представления. Для вывода о содержании человеческих меток нужны более сильные контроли.',
95:'Майский split разбивал строки molecule×task. Это другая задача, чем предсказание нового соединения; не объясняем весь разрыв метрик одним split.',
96:'Девять реконструированных конфигураций совпадают на двух серверах. Новые task-векторы и среда отличаются от исторических, поэтому это approximate reconstruction.',
97:'На всех 105 солях считаем grouped CV: 103 катиона и 29 scaffold. Старые source-корпусы пересекаются с QAC; matched source исключает target cations.',
98:'В новом archived-feature OOD human/text RMSE 2.023 против raw/text 2.245. На grouped CV аналогичного выигрыша нет; разные task codes сравниваются отдельно.',
102:'Шесть matched compact arms на одной source-выборке, пять paired seeds и 480 updates. No-SMOTE контроль отличается от исторического v5; continuous objective отличается от binary.',
103:'Показываем действительное число параметров: 691584 encoder, 741504 contrastive route, 691841 regression route. Усредняем метрики отдельных seed, не ошибки ансамбля.',
104:'Human/binary/continuous дают близкую cation CV. На OOD human лучше raw, но human–continuous интервал не устанавливает превосходства.',
105:'Главный semantic-content контроль real vs shuffled human не выигрывает. Альтернативные объяснения остаются гипотезами; положительный partial-backbone результат — отдельный опыт.',
106:'С одним compact checkpoint заменяем только task codes. Text, permutation и random codes не устанавливают semantic advantage на четырёх знакомых задачах.',
112:'264 tabular fit на старых raw/human v5 embeddings. PCA32 и бюджеты объявлены; OOD не выбирает лучший representation.',
113:'TabPFN, TabFM и AutoGluon не улучшают одновременно все regimes. Chemprop и RDKit сохранены как отдельные структурные сравнения в SI.',
118:'Full fine-tuning хорош на cation CV, но слаб на OOD при этом бюджете. Human partial frozen representation + CatBoost лучше прямого prediction на тех же трёх seed.',
122:'Compact weight-only reset сохраняет BatchNorm state; full initial-state reset удаляет и его. Интервалы compact reset включают ноль.',
123:'Отдельный partial-backbone опыт обнаруживает вклад весов на cation CV. Это вычислительное вмешательство, а не обнаруженный биологический механизм.',
124:'Ограничиваем causal claim конкретным intervention и измеряемым loss. Независимость human knowledge требует H1–H7; statistical equivalence не следует из interval covering zero.',
126:'Главные исходные положительные R² остаются частью статьи. У них частичная notebook provenance, а новые проверки идут рядом.',
127:'Полезность внешнего адаптера зависит от task encoding и decoder. OOD и molecule×task holdout отвечают на разные вопросы.',
128:'Новый compact контроль не доказывает вклад содержания human labels. Частично положительные backbone результаты поддерживают условную, а не универсальную интерпретацию.',
129:'Современные модели и direct fine-tuning дают практический контекст. Дальнейшие необходимые данные: annotation information access, quantitative checkpoint и перенос между assay contexts.',
213:'H1–H7 оставлены для восстановления сбора разметки. Итоговые calls доступны; индивидуальные голоса не выдумываем.',
222:'Фиксируем историческую архитектуру, reconstructed CatBoost budget, splits, версии task descriptions и кодовые контроли.',
224:'Фиксируем matched training split, train-only preprocessing, AdamW schedule, 80 epochs, 480 updates и paired state/batch hashes.',
226:'Все 420 QAC endpoint точные; OOD 67 exact +1 bound. Описываем seed-mean scores и paired cluster bootstrap; четыре OOD scaffold ограничивают выводы.'}
def main():
 f,t,body=b.v.read_doc(b.MAIN);out=['Краткий разбор содержательных абзацев v18.','',
  'Число в скобках — индекс блока в native Word XML; подписи и таблицы отдельно не пересказываются. Полные экспериментальные характеристики соединений сохранены, ниже кратко пересказаны вычислительные методы.','']
 records=[];section=''
 for i,node in enumerate(body):
  text=b.h.text(node)
  if i<11:continue
  if re.match(r'^(?:[1-3]\. |2\.\d|4\.3)',text):section=text;out.extend([section,''])
  if i in SUMMARIES:
   out.extend([f'Абзац ({i}). '+SUMMARIES[i],'']);records.append(dict(native_body_index=i,section=section,source_text=text,summary_ru=SUMMARIES[i]))
  if i==130:out.extend(['4.1–4.2. Химические характеристики и microbiological protocol: исходный текст сохранён без изменений.',''])
  if i>227:break
 assert len(records)==len(SUMMARIES)
 (ROOT/'ARTICLE_BY_PARAGRAPHS_RU.md').write_text('\n'.join(out))
 (ROOT/'paragraph_walkthrough.json').write_text(json.dumps(dict(manuscript_sha256=hashlib.sha256(b.MAIN.read_bytes()).hexdigest(),paragraphs=records),ensure_ascii=False,indent=2))
 print('Russian summaries:',len(records),'paragraphs')
if __name__=='__main__':main()

# Три insights

Эти три результата стоит рассматривать вместе, потому что они образуют замкнутый аргументативный контур: проблему (CAT), её эмпирическое следствие (Smaldino), и условия её решения (Hong-Henrich). Каждый по отдельности интересный. Вместе — они структурируют твой design space.

## Insight 1: транзмиссия идей реконструктивна, не репликативна (Sperber и CAT)

**Что утверждается.** Когда идея «передаётся» от человека к человеку, реципиент не копирует её. Он реконструирует её в своей голове из частичных сигналов которые получил, заполняя пробелы из собственного когнитивного состояния, prior knowledge, attention biases. Каждое «событие транзмиссии» структурно ближе к перевыводу чем к копированию. Это в корне отличается от генетической репликации где physical molecule копируется с высокой fidelity.

**Эмпирическая база.** Transmission-chain experiments, начиная с Bartlett (1932), систематически показывают высокую rate transformation на каждом шаге. Истории компрессируются, narratives смещаются к stereotype-consistent forms, языки эволюционируют к learnability-friendly grammars. Acerbi, Charbonneau, Miton & Scott-Phillips (2021) показали в *Evolutionary Human Sciences* что стабильные cultural patterns могут возникать через convergent transformations *без копирования и без selection вообще*. Это сильный результат: то что в genetic evolution описывается selection, в cultural evolution иногда не требует selection — достаточно факта что reconstructions сходятся к attractors.

**Почему это структурно важно для проекта.** Если транзмиссия реконструктивна, то традиционная метафора «знание это то что копируется в paper-form» неверна. Paper это не молекула — это набор сигналов из которых reader реконструирует understanding. Это означает несколько вещей.

Во-первых, потеря информации в современной научной коммуникации — feature, не bug. Reader получает финальный артефакт и реконструирует процесс. Reconstruction errors неизбежны и систематичны. Failure data, decision rationale, alternatives considered — всё то что не попадает в paper — это ровно то что reader должен реконструировать с нуля. Когда два независимых reader реконструируют one paper по-разному, это и есть та divergence о которой пишут историки науки годами.

Во-вторых, в LLM-mediated environment это становится буквальным. LLM делает reconstructive transmission механически: каждый «summary» это reconstruction. Когда ты используешь LLM для научного синтеза, ты буквально используешь reconstruction-based transmission. Это не метафора. И тогда CAT прямо предсказывает: сходимость к attractors в семантическом пространстве происходит независимо от того представляют ли эти attractors truth. Это связано с preprint про epistemic monoculture — correlated errors моделей это observable consequence того что reconstruction process имеет shared biases.

В-третьих, для design fitness function это означает что naive подход «измерим как часто идею копируют» концептуально неверен. Правильнее измерять «насколько устойчиво идея реконструируется в attractor», что операционализируемо в embedding space. Но также ясно что attractor-occupancy это не truth-tracking — точка в семантическом пространстве куда сходятся reconstructions может быть incorrect.

**Что это даёт проекту конкретно.** Arbitration trace становится не просто «log of disagreements» а *capture of the reconstruction process itself*. Когда два агента реконструируют одну ситуацию по-разному и человек арбитрирует, ты захватываешь именно тот transformation которым реальный reconstruction отличается от ground truth. Это data type который CAT-literature предсказывает должен существовать но никто систематически не собирает.

## Insight 2: transmission-fitness систематически расходится с truth-fitness (Smaldino-McElreath)

**Что утверждается.** Если «fitness» научной методологии измеряется через её способность производить публикации (transmission proxy), и если incentives структурированы так что labs которые публикуют больше выживают, то selection действует на методологию. Smaldino & McElreath (2016) формализовали это через agent-based model и показали неожиданно сильный результат: при реалистичных параметрах selection driven by publication производит *менее rigorous* methodology over time, не более. Low-power studies дают больше publications за единицу времени и effort. False positives дают значимые результаты которые публикуются. Replicable, careful, rigorous studies дают меньше outputs и проигрывают в cultural selection.

**Эмпирическая база.** Replication crisis в психологии и других областях с 2011 года это observable consequence предсказания модели. Open Science Collaboration replication rates в 36-39% для psychology, similar for cancer biology. Kohrt et al. (2023) реплицировали Smaldino-McElreath с дополнительными механизмами и подтвердили robustness. Bergstrom & West и другие в metascience развивают это далее.

**Почему это важно для проекта.** Это эмпирически установленный baseline factor который fitness function *обязана* учесть, иначе она автоматически inherits эту патологию. Если ты обучаешь fitness function на корпусе successful papers (т.е. high transmission fitness), ты по построению обучаешь её на artefacts отбора который частично селектирует на bad methodology. Smaldino-McElreath не просто говорит «be careful» — он даёт квантитативный аргумент почему naive transmission-based fitness systematically anti-correlated с epistemic quality в современных institutional conditions.

Это connects напрямую к DFE paper. Когда я ранее критиковал interpretation 13% beneficial fraction, аргумент имел такую же структуру: то что попадает в published corpus прошло filter selection, и этот filter не является truth-tracking, он является transmission-tracking. Smaldino-McElreath даёт generalised форму этого аргумента и показывает что в worst case selection активно anti-truth.

**Что это даёт проекту конкретно.** Fitness function для научных идей не может быть обучена purely на published-success signal. Нужен корректирующий компонент который инкорпорирует прямой epistemic signal — predictive accuracy на out-of-sample data, replication rate, theoretical coherence, productive follow-up. Это не косметическое дополнение, это структурное требование. Без него fitness function reproduces патологию которую Smaldino-McElreath documented.

И это даёт concrete validation criterion для пилота: если LLM-as-judge калибруется только на «was this published in top venue» signal, она inherits Smaldino-McElreath bias. Если она калибруется на retrodictive truth-tracking signals (idea predicted future findings, idea reproduced under independent replication), она потенциально escapes этот bias. Этот distinction измеримый.

## Insight 3: наука как epistemic technology выравнивает transmission и truth-fitness (Hong-Henrich)

**Что утверждается.** Hong & Henrich (2021, *Human Nature*) выводят рамку в которой различные cultural systems можно классифицировать по тому насколько хорошо их institutional structure aligns transmission-fitness с truth-fitness. Магия, divination, witchcraft — culturally fit systems которые robust в transmission но not truth-tracking. Modern science — culturally evolved system который при определённых условиях aligns these. Условия не trivial: peer review, replication, predictive testing, theoretical accountability — это institutional features которые делают transmission of incorrect ideas costly enough что truth-tracking начинает доминировать в long-run dynamics.

**Эмпирическая база.** Comparative studies across cultures и historical periods. Hong & Henrich конкретно analyzed divination systems и показали как они sustain themselves несмотря на отсутствие predictive power — через features которые reduce falsifiability и distribute credit/blame. Современная science studies показывает что когда institutional features ослабевают (publication pressure overwhelms peer review, citation gaming substitutes for scientific contribution), system reverts toward Smaldino-McElreath dynamics.

**Почему это важно для проекта.** Это даёт positive design framework, не только critique. Hong-Henrich формулирует что наука работает не потому что учёные более rational чем shamans, а потому что *institutional structure* создаёт conditions при которых transmission-fitness и truth-fitness alignется. Это означает что проект — building infrastructure для научного процесса в эпоху AI — это буквально *design of an epistemic technology*. И есть literature которая позволяет рассуждать о design choices не intuitively а через analytical framework.

Конкретные institutional features которые делают alignment:

— *Pre-registration* делает costly опубликовать idea которая не предсказывает outcome правильно. Без неё easy to retrofit interpretation. С ней failure visible.

— *Replication* делает costly опубликовать non-reproducible result. Reduces selective advantage low-power studies.

— *Adversarial review* делает costly опубликовать idea с obvious flaws. Не perfect filter, но non-zero.

— *Predictive testing на out-of-sample data* делает costly опубликовать over-fit idea.

— *Theoretical coherence requirement* (когда оно действует) делает costly опубликовать ad-hoc explanations.

Каждая из этих features добавляет cost к transmission incorrect idea. Когда они ослабевают, bias возвращается.

**Что это даёт проекту конкретно.** Дизайн системы должен явно encode эти features. Не как ритуал, а как структурные cost-imposing mechanisms. Pre-registration не как optional шаг а как hash-locked artifact который reviewers могут проверить. Failure log не как гигиена а как first-class entity которая ranks researcher reputation. Adversarial review через triangulation не как nicety а как required gate. Каждое из этих design choices imposes небольшой cost на bad-faith использование системы и preserves alignment.

И это даёт coherent message для positioning. Ты не строишь «yet another research tool». Ты строишь next-generation epistemic technology — designed with explicit awareness того как previous epistemic technologies (peer-reviewed paper) сломались под современными pressures, и проектируешь corrective features в основу.

## Как они складываются

CAT говорит: transmission реконструктивна, что делает naive «копирование» неверной моделью. Smaldino-McElreath говорит: transmission-fitness активно расходится с truth-fitness под realistic incentives. Hong-Henrich говорит: alignment возможен но требует institutional features которые impose cost on incorrect transmission.

Конкретно для проекта это даёт: (1) операционализировать transmission через reconstruction-distance в embedding space, не через copy-count; (2) включить explicit truth-tracking signal в fitness function потому что transmission alone systematically biased; (3) проектировать institutional features (pre-reg, failure logging, triangulation, adversarial review) как cost-imposing mechanisms внутри инфраструктуры, не как optional add-ons.

Это converges into design thesis который defensible в literature и testable. Это уже нечто концептуально более crystallized чем «AI infrastructure for science».

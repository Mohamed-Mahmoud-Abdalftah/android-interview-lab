#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
DATE = "2026-10-11"
SRC = "../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt"
TEST = "../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt"

units = [
    {
        "id": "COR-003", "day": 9, "title": "Cooperative cancellation and cleanup",
        "path": "02-Coroutines-Flow/cor-003-cooperative-cancellation-and-cleanup.md",
        "prereqs": ["COR-002"], "qstart": 11, "scenario": 20, "lab": 19,
        "sources": ["https://kotlinlang.org/docs/cancellation-and-timeouts.html", "https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/ensure-active.html", "https://developer.android.com/kotlin/coroutines/coroutines-best-practices"],
        "model": "الإلغاء في coroutines تعاوني: طلب الإلغاء يغيّر حالة الـJob، والكود يوقف لما يوصل suspension point قابلة للإلغاء أو يعمل فحص صريح. loop حسابية طويلة من غير تعليق أو فحص ممكن تكمل بعد إلغاء الشاشة. cleanup يتحط في finally، وNonCancellable يتستخدم لأصغر جزء لازم يخلص فعلًا.",
        "trace": ["الـowner يبدأ import تحت Job مملوكة له.", "المستخدم يخرج؛ الـJob تصبح cancelling.", "الـloop تصل إلى ensureActive أو yield فترمي CancellationException.", "finally يقفل المورد، والـparent يلاحظ cancelled بدل success كاذب."],
        "wrong": "suspend fun import(rows: List<Row>) {\n    for (row in rows) expensiveParse(row) // no suspension/checkpoint\n}",
        "correct": "suspend fun import(rows: List<Row>) {\n    try {\n        for (row in rows) {\n            currentCoroutineContext().ensureActive()\n            expensiveParse(row)\n        }\n    } finally {\n        closeParser()\n    }\n}",
        "failure": "الـloop الثقيلة تتجاهل cancellation، أو catch عام يبلع CancellationException، أو cleanup طويل داخل NonCancellable يؤخر إغلاق الشاشة.",
        "tests": "اختبر إلغاء parent بعد batch معلومة، وتأكد إن مفيش عناصر اتعالجت بعدها، وإن finally اتنفذ مرة واحدة، وإن الفشل business لا يتصنف cancellation.",
        "english": "Cancellation is cooperative. Suspending APIs usually check it, but CPU loops need explicit checkpoints such as ensureActive or yield. I keep cleanup in finally, rethrow CancellationException, and restrict NonCancellable to a small bounded cleanup operation.",
        "qs": [
            ("Cooperative cancellation checkpoints", "A CPU-heavy loop is inside a suspend function but ignores cancellation. Explain why and choose checkpoints without destroying throughput.", "A suspend modifier does not insert cancellation checks into ordinary CPU instructions. I add ensureActive at a measured batch boundary or yield when fairness is needed, then test how much work completes after cancellation.", "suspend لا تضيف checkpoint داخل loop تلقائيًا. اختار batch boundary توازن بين سرعة الاستجابة وتكلفة الفحص، وقِس worst-case cancellation latency.", "Does delay check cancellation", "Yes. Delay is cancellable, but a loop that never reaches it can still ignore the request.", "Why not check every instruction", "That adds overhead and noise; use a bounded batch based on the latency requirement."),
            ("CancellationException handling", "Review a repository that catches Exception and returns Result.failure. What cancellation bug can it create?", "CancellationException is an Exception. Mapping it to a normal failure can continue retries or publish stale state after the owner is gone. I rethrow it before mapping expected domain or transport failures.", "الـrepository خلط انتهاء العمر بفشل business. لازم cancellation تطلع للمالك، ويمسك فقط exceptions اللي يقدر يصنفها.", "Can ensureActive repair a broad catch", "It can reassert cancellation, but a narrow catch remains easier to audit.", "Should cancellation be logged as an error", "Usually no; record it separately only when operationally useful and avoid alert noise."),
            ("finally and NonCancellable", "A team wraps a network upload in withContext(NonCancellable) so cleanup finishes. Review the decision.", "NonCancellable around the upload defeats the owner's cancellation and can delay shutdown. I keep the upload cancellable and reserve NonCancellable for a short bounded cleanup such as closing or recording a local terminal marker.", "استخدام NonCancellable على العملية كلها بيحوّل cleanup لعمل جديد طويل. حدّد invariant صغير لازم يكتمل وحط timeout مناسب لو ينفع.", "Can finally call suspending code after cancellation", "A suspending call can immediately throw; only a truly required small section may need NonCancellable.", "What if server outcome is unknown", "Persist an unknown state and reconcile; do not keep the UI owner alive indefinitely."),
            ("Timeout ownership", "Where should withTimeout live when UI, repository, and HTTP client all have deadlines?", "Each timeout represents a different contract. The HTTP client owns transport timeouts, the repository owns operation policy, and the UI may own a shorter patience window. I preserve the cause so timeout, cancellation, and unknown server outcome remain distinguishable.", "ما تجمعش كل deadlines في رقم واحد. اكتب مين يملك كل مهلة وإيه اللي يحصل لو انتهت، خصوصًا لو request ممكن تكون committed على السيرفر.", "Is timeout always safe to retry", "No. A timed-out side effect may have committed, so retries need idempotency or reconciliation.", "Does withTimeout block a thread", "No; it cancels the coroutine when the deadline expires."),
            ("Cancellation verification", "Design a deterministic test for cancellation and cleanup without Thread.sleep.", "I use runTest, gates such as CompletableDeferred, start the child, advance the scheduler to the known suspension point, cancel the parent, and assert cancellation plus exactly-once cleanup and no later publication.", "الاختبار يتحكم في نقطة البداية والإلغاء بدل سباق الوقت. لازم يثبت negative behavior: مفيش state اتنشرت بعد الإلغاء.", "Why is a finally flag insufficient", "It proves cleanup ran but not that stale output stopped or resources closed correctly.", "Would this prove Android lifecycle behavior", "No. It proves the suspend contract; lifecycle wiring needs an Android integration test."),
        ],
        "scenario_title": "An import keeps using CPU after the screen closes",
        "scenario_body": "تطبيق استيراد يقرأ 80 ألف row في loop حسابية على Default. المستخدم يقفل الشاشة لكن CPU يفضل عالي والنتيجة القديمة تظهر لما يفتح حساب تاني. تتبع owner والـJob ومواضع suspension. أصلحها بفحص cancellation عند batch boundary، generation للنتيجة، وfinally يقفل parser. اختبر حد أقصى لعدد rows بعد الإلغاء بدل الاعتماد على sleep.",
        "lab_title": "Bounded cooperative batches",
        "lab_contract": "قسّم العناصر batches، وارجع فقط الـbatches المكتملة قبل cancellation boundary. ارفض batch size غير موجب، ولا تعدّل input. النموذج pure يثبت boundary الحسابية؛ توصيل ensureActive الحقيقي موضح في الدرس ويحتاج coroutine integration test.",
    },
    {
        "id": "COR-004", "day": 10, "title": "Flow cold/hot, StateFlow and SharedFlow",
        "path": "02-Coroutines-Flow/cor-004-flow-cold-hot-stateflow-and-sharedflow.md",
        "prereqs": ["COR-001"], "qstart": 16, "scenario": 21, "lab": 20,
        "sources": ["https://kotlinlang.org/docs/flow.html", "https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/", "https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/", "https://developer.android.com/kotlin/flow/stateflow-and-sharedflow"],
        "model": "الـcold Flow وصف لشغل يبدأ من جديد لكل collector. StateFlow hot وعندها current value واحدة؛ collector جديد ياخد أحدث state. SharedFlow hot broadcast بسياسة replay وbuffer لازم تتصمم بوضوح. اختار primitive من معنى البيانات: state قابلة للقراءة دلوقتي، event لحظي، أو query تتعاد لكل جمع.",
        "trace": ["Collector A يجمع cold flow فتبدأ network chain A.", "Collector B يجمع نفس الوصف فتبدأ chain B مستقلة.", "تحويلها بـstateIn يبدأ sharing coroutine مملوكة لـscope.", "WhileSubscribed يحدد إمتى upstream تبدأ وتتوقف؛ إلغاء collector لا يلغي hot flow نفسها."],
        "wrong": "val navigation = MutableStateFlow<Route?>(null)\n// A new collector can receive an old navigation command again.",
        "correct": "private val _state = MutableStateFlow(ScreenState())\nval state = _state.asStateFlow()\n// Durable state stays in StateFlow; transient effects get an explicit policy.",
        "failure": "double collection يعمل duplicate requests، أو StateFlow تستخدم event فتتعاد، أو SharedFlow buffer تضيع events من غير contract، أو sharing scope تعيش أطول من feature.",
        "tests": "اختبر initial state، equality conflation، collectors جدد، توقف upstream مع subscription policy، والفرق بين غياب subscriber وبين buffer ممتلئة.",
        "english": "I choose a stream from data semantics. Cold Flow restarts per collector. StateFlow represents a current state value and conflates equal updates. SharedFlow broadcasts future emissions with an explicit replay and buffer policy. The sharing scope owns upstream lifetime.",
        "qs": [
            ("Cold flow collection", "Two collectors collect the same cold Flow and duplicate a network request. Explain the behavior and valid fixes.", "A cold Flow executes its upstream separately for every collector. I either keep one collector, move the request behind a cache, or share it with stateIn or shareIn in a scope whose lifetime and start policy match the feature.", "الـFlow هنا recipe مش pipe واحدة. الإصلاح يعتمد هل المطلوب cache state ولا broadcast، ومين يملك sharing coroutine.", "Does flowOn make it hot", "No. It changes upstream context, not collection multiplicity.", "Can shareIn leak work", "Yes, if its scope outlives the feature or its start policy keeps upstream active unnecessarily."),
            ("StateFlow conflation", "Why might assigning an equal data-class value to MutableStateFlow produce no new emission?", "StateFlow uses equality-based conflation. If the new value compares equal to the current value, collectors are not notified. State should be immutable and equality must represent every observable field.", "لو mutable object اتغيرت جوه نفس reference، equality ومراقبة التغيير ممكن يخفوا update. انشر نسخة immutable جديدة فيها كل الحقول المرئية.", "Would adding a random nonce fix it", "It forces emissions but corrupts state semantics; model a real version only if version is part of the contract.", "Is every state update delivered", "Collectors receive the latest state and may skip intermediate values when slow."),
            ("SharedFlow replay and buffer", "Choose replay and buffer behavior for analytics events versus a critical payment result.", "Best-effort analytics may tolerate dropping with a measured buffer policy. A payment result is durable business state and should be persisted or represented in state, not trusted to an in-memory SharedFlow with no subscriber.", "replay مش durability. process death تمسح الذاكرة، وغياب collector ممكن يضيّع event حسب السياسة.", "Does replay zero guarantee delivery to active collectors", "Emission behavior also depends on buffer and suspension; define and test the chosen overflow policy.", "Can SharedFlow represent completion", "It never completes normally; completion or failure must be materialized as data."),
            ("State versus event", "A snackbar says Save failed. Should it be StateFlow or SharedFlow?", "I first ask whether the message must survive recreation and be acknowledged. If it is part of durable UI state, model it with an ID and acknowledgement. A transient effect can use an event stream only when missed delivery is acceptable and ownership is explicit.", "مافيش جواب باسم component بس. حدد guarantee: هل الرسالة لازم تتشاف مرة، هل process death مهمة، وهل إعادة العرض مقبولة.", "Why is nullable state event risky", "A new collector may receive the old non-null value, and clearing it introduces races.", "How do you test acknowledgement", "Reduce an acknowledge action and assert the event ID cannot be consumed twice."),
            ("Lifecycle collection", "Why is collecting a UI Flow in a plain launch risky on Android?", "The coroutine may keep collecting while the view is stopped, wasting work or updating a dead view. I use lifecycle-aware collection with the correct owner and keep the producer lifetime separate from a collector lifetime.", "في Fragment فرّق بين lifecycle بتاعة Fragment وviewLifecycleOwner. collector بتلمس views لازم ترتبط بعمر الـview.", "Does cancelling one collector stop StateFlow", "No. A hot flow and its producer have their own scope.", "What needs an Android test", "STARTED/STOPPED collection, recreation, and view-owner wiring require lifecycle integration evidence."),
        ],
        "scenario_title": "One screen makes duplicate requests and another loses an event",
        "scenario_body": "كل recomposition أو collector جديد بيجمع cold flow فتتكرر request، وفي نفس الوقت navigation معمولة StateFlow فتتعاد بعد rotation. افصل state عن effect، شارك upstream في scope مناسبة بسياسة WhileSubscribed، واربط collection بعمر الـview. اختبر عدد subscriptions وإعادة الإنشاء وغياب subscriber.",
        "lab_title": "Choose the stream from its contract",
        "lab_contract": "اكتب decision function: لو محتاج current value فالاختيار State؛ لو كل subscribers الحاليين لازم يشوفوا future emissions فالاختيار Event؛ غير كده Query باردة. اشرح إن النموذج يساعد السؤال لكنه لا يختار replay أو persistence بدل requirements.",
    },
    {
        "id": "COR-005", "day": 11, "title": "Latest operators, buffering and stale writes",
        "path": "02-Coroutines-Flow/cor-005-latest-operators-buffering-and-stale-writes.md",
        "prereqs": ["COR-003", "COR-004"], "qstart": 21, "scenario": 22, "lab": 21,
        "sources": ["https://kotlinlang.org/docs/flow.html", "https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/collect-latest.html", "https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/flat-map-latest.html"],
        "model": "latest operators تلغي الشغل القديم لما value جديدة توصل، لكنها تعتمد إن الشغل القديم قابل للإلغاء. buffer يسمح للمنتج يسبق consumer ضمن capacity، وconflate يحتفظ بالأحدث ويهمل الوسط. ولا واحدة منهم تمنع stale database write لو side effect غير cancellable أو بدأ commit بالفعل؛ ساعتها تحتاج generation أو idempotency عند boundary.",
        "trace": ["المستخدم يكتب a فتبدأ request 41.", "يكتب ab؛ flatMapLatest تلغي collection القديمة وتبدأ request 42.", "لو client يتعاون، 41 تتوقف. لو commit حصل، response 41 قد ترجع.", "generation gate تقبل 42 فقط؛ UI لا تستبدل النتيجة الجديدة بالقديمة."],
        "wrong": "queryFlow.collect { query ->\n    val result = api.search(query)\n    _state.value = result // an older request can win\n}",
        "correct": "queryFlow.flatMapLatest(api::searchFlow)\n    .collectLatest { result -> render(result) }\n// Add a request generation at non-cancellable write boundaries.",
        "failure": "conflate تضيع progress مطلوب، buffer غير محدودة تستهلك memory، أو latest cancellation تتفهم غلط كـrollback لعملية server بدأت بالفعل.",
        "tests": "بوابات controlled لطلبين ترجع القديم بعد الجديد، assertion إن generation القديمة مرفوضة، واختبارات overflow policy وside-effect idempotency.",
        "english": "Latest operators cancel obsolete coroutine work, but cancellation is not transaction rollback. I use them for superseded UI work, then add request generations or idempotency at boundaries where an old side effect can still complete. Buffer and conflate are semantic choices, not automatic performance fixes.",
        "qs": [
            ("collectLatest cancellation", "What exactly does collectLatest cancel when a new value arrives, and what can still escape?", "It cancels the previous collector action and waits for its cancellation before running the next. Blocking or already-committed external work may continue, so I do not treat cancellation as rollback.", "اللي بيتلغي coroutine action. server request أو database commit قد يكون عدى نقطة الرجوع؛ محتاج contract إضافي.", "When is ordinary collect correct", "When every value must be processed in order and backpressure is acceptable.", "Can finally delay the next value", "Yes. collectLatest waits for cancellation cleanup, so slow cleanup delays the replacement."),
            ("buffer versus conflate", "A progress stream emits 1 through 100 faster than rendering. Compare buffer and conflate.", "Buffer lets the producer get ahead until capacity fills, preserving queued values. Conflate lets a slow collector skip intermediates and process the latest. I use conflate only when intermediate progress has no business meaning.", "لو كل رقم transaction أو audit event، إسقاط الوسط غلط. لو progress visual، أحدث قيمة غالبًا تكفي.", "Does buffer make work faster", "It can overlap producer and consumer, but adds memory and latency; measurement and capacity matter.", "What does unlimited capacity risk", "Unbounded memory growth when the consumer remains slower."),
            ("flatMapLatest search", "Design type-ahead search with debounce, distinctUntilChanged, and flatMapLatest. Name the remaining risks.", "I normalize input, debounce UI noise, remove equal queries, and switch to the latest search Flow. I still handle cancellation cooperation, cache policy, errors, loading state, and stale writes outside the cancellable pipeline.", "ترتيب operators جزء من المعنى. distinct قبل normalization ممكن يعتبر مسافتين queries مختلفة، وcatch في مكان غلط ممكن يقفل stream كلها.", "Where should loading state be emitted", "At the request transformation boundary so each query has a traceable loading and terminal state.", "Should errors terminate query input", "Usually each request error becomes data so later queries can still run; preserve cancellation."),
            ("Stale result generation", "Why use a request generation if flatMapLatest already cancels old requests?", "Because cancellation is cooperative and external work can complete after cancellation. A monotonically increasing generation lets the owner accept only results for the current request.", "generation gate تمنع publish، لكنها مش بتلغي تكلفة الشغل ولا تمنع server side effect. دي طبقة correctness إضافية.", "Can timestamps replace generation", "Clock order can be ambiguous; an owner-local monotonic ID is simpler for request ordering.", "Where is the check placed", "At the state mutation or commit boundary owned by the latest request."),
            ("Backpressure contract", "A telemetry pipeline drops values under load. How do you decide whether this is a bug?", "I classify each value: durable business event, diagnostic sample, or replaceable state. Durable events need persistence and acknowledgement; samples can use a documented drop policy with counters; state can conflate to latest.", "قبل اختيار Channel أو Flow اكتب delivery guarantee. الأداء مش مبرر لإسقاط بيانات من غير معرفة معناها.", "What metric reveals hidden loss", "Count produced, accepted, dropped by reason, and queue age without logging sensitive payloads.", "Can retry solve overflow", "Retry can amplify overload; admission control and durable queues may be required."),
        ],
        "scenario_title": "Old search results overwrite the latest query",
        "scenario_body": "request لكلمة قصيرة بطيئة ترجع بعد request لكلمة أطول، فتستبدل state الجديدة. استخدم controlled responses لإثبات الترتيب، ثم flatMapLatest للشغل القابل للإلغاء وrequest generation عند publish boundary. راقب cancelled، stale-dropped، latency، وما تعتبرش cancellation rollback للسيرفر.",
        "lab_title": "Reject a stale versioned result",
        "lab_contract": "استقبل current request ID وcandidate فيها requestId وvalue. رجع value فقط لو IDs متساوية. اختبر القديم والجديد وحدود Long. اشرح إن gate تحمي state لكنها لا توقف الشغل الخارجي.",
    },
    {
        "id": "COR-006", "day": 12, "title": "Revision: deterministic coroutine tests and DSA",
        "path": "02-Coroutines-Flow/cor-006-revision-deterministic-coroutine-tests-and-dsa.md",
        "prereqs": ["COR-003", "COR-004"], "qstart": 26, "scenario": 23, "lab": 22,
        "sources": ["https://developer.android.com/kotlin/coroutines/test", "https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/", "https://kotlinlang.org/docs/collections-overview.html"],
        "model": "اختبار coroutine deterministic يتحكم في scheduler والـdispatcher والـinputs؛ ما يستناش wall clock. runTest يتابع coroutines على test scheduler، وadvanceTimeBy يحرك virtual time، وrunCurrent يشغل المهام الجاهزة. dispatcher injection تمنع production Dispatchers من الهروب خارج سيطرة الاختبار. جزء DSA يراجع invariant للـhash map بدل حفظ الحل.",
        "trace": ["الاختبار ينشئ TestScope وStandardTestDispatcher على scheduler واحدة.", "ينادي subject؛ الشغل يتجدول لكنه لا يجري سحريًا.", "runCurrent يشغل الموجود عند الزمن الحالي؛ advanceTimeBy يحرك deadline.", "assertions تفحص states والـJobs، ثم runTest يتأكد إن مفيش coroutine معلقة."],
        "wrong": "@Test fun retryWorks() = runBlocking {\n    subject.retry()\n    Thread.sleep(3_000)\n    assertEquals(Success, subject.state.value)\n}",
        "correct": "@Test fun retryWorks() = runTest {\n    subject = Subject(dispatcher = StandardTestDispatcher(testScheduler))\n    subject.retry()\n    advanceTimeBy(3_000)\n    runCurrent()\n    assertEquals(Success, subject.state.value)\n}",
        "failure": "test يستخدم scheduler مختلفة، أو production dispatcher ثابتة، أو assert قبل runCurrent، أو hot flow collection تفضل معلقة، أو test تثبت timing بدل behavior.",
        "tests": "اختبر intermediate state قبل تحريك الوقت، terminal state بعده، cancellation، cleanup، وعدم وجود tasks معلقة. في DSA اختبر empty وduplicates وoverflow وعدم تعديل input.",
        "english": "A deterministic coroutine test owns the dispatcher, scheduler, and completion gates. I assert intermediate state before advancing virtual time, then advance only the work needed. I avoid sleeps and make every launched coroutine visible to runTest. For DSA I state the invariant before code and test boundaries, not just the happy path.",
        "qs": [
            ("runTest and virtual time", "What does runTest give you that runBlocking plus delay does not?", "runTest provides a TestScope, tracks child coroutines, skips compatible delays through virtual time, and reports unfinished work. It makes scheduling controllable instead of coupling assertions to machine speed.", "runBlocking يوقف thread لكنه مش test scheduler. sleep يخلي الاختبار بطيء وflaky ومش يثبت state transitions بدقة.", "Does runTest control Dispatchers IO automatically", "No. Inject dispatchers or replace the relevant main dispatcher; escaped real dispatchers break virtual-time control.", "Why assert before advance", "It proves the intermediate state exists and the result was not published eagerly."),
            ("One scheduler rule", "Why should test dispatchers in one test usually share a TestCoroutineScheduler?", "A shared scheduler gives one virtual clock and one queue, so advance and runCurrent control all subject work consistently. Separate schedulers can leave work invisible to the test's clock.", "لو كل dependency عندها ساعة مختلفة، الاختبار يتحرك واحدة ويفتكر إن الكل خلص. مرّر testScheduler نفسها لكل dispatcher.", "Standard or Unconfined test dispatcher", "Standard queues predictably; Unconfined starts eagerly and can simplify some tests but changes ordering, so choose intentionally.", "What should production accept", "CoroutineDispatcher or a small dispatcher provider at the boundary that owns execution."),
            ("Testing hot flows", "How do you test a StateFlow that never completes without hanging the test?", "Read value for current state, use take or first for a bounded expectation, or launch a collector in backgroundScope and cancel it. The test must own collector lifetime.", "collect العادية على hot flow مش هترجع. خلّي expected count أو predicate تقفل المسار، أو اربط collector بـbackgroundScope.", "When is Turbine useful", "It can make emission assertions clearer, but the same ownership and virtual-time rules still apply.", "What about equality conflation", "Publish equal and different states explicitly and assert the documented emission behavior."),
            ("Hash-map invariant", "For two-sum on an unsorted array, state the one-pass hash-map invariant before coding.", "Before index i, the map contains values from earlier indices and their chosen indices. I ask whether target minus current exists before inserting current, which prevents using the same element twice and returns according to the specified index policy.", "قول invariant والـoverflow contract. target - value على Int ممكن overflow؛ استخدم Long لو العقد يسمح بكل Int values.", "How do duplicates work", "Checking before insertion allows two equal values at distinct indices to form the pair.", "What complexity claim is honest", "Expected O(n) time and O(n) extra space under normal hash behavior."),
            ("Flaky test diagnosis", "A coroutine test passes alone and fails in the suite. Give an evidence-first debugging plan.", "I inspect leaked scopes, shared mutable fakes, real dispatchers, wall-clock waits, and global Main replacement cleanup. I reproduce with ordering and repetition, then remove the uncontrolled dependency rather than increasing sleeps.", "الفشل حسب ترتيب suite غالبًا ownership أو global state. اجمع trace للـscheduler والـjobs، ومتخبيش السباق بtimeout أكبر.", "Can retries in CI be the fix", "Retries can measure flakiness temporarily, but a merge gate should not normalize an uncontrolled test.", "What cleanup is mandatory", "Reset any replaced global dispatcher and cancel test-owned scopes in guaranteed teardown."),
        ],
        "scenario_title": "A retry test passes locally and flakes in CI",
        "scenario_body": "الاختبار يستخدم runBlocking وdelay حقيقي، والsubject يشغل Dispatchers.IO مباشرة. تحت ضغط CI الـassertion تسبق النتيجة. احقن dispatcher، شارك testScheduler، اثبت Loading قبل الوقت وSuccess بعد advance، وألغ collector الدائم. شغّل الاختبار مكررًا كتشخيص ثم أوقف الاعتماد على retry كحل.",
        "lab_title": "A deterministic task queue",
        "lab_contract": "نفّذ queue تشغّل snapshot من المهام الجاهزة؛ task تضيف task جديدة لا تتنفذ في نفس runCurrent. اختبر الترتيب والـnested scheduling. النموذج يشرح scheduler semantics ولا يدّعي إنه بديل لـkotlinx-coroutines-test.",
    },
]

def front_list(values):
    return "[" + ", ".join(values) + "]"

def lesson(u):
    qids = [f"COR-Q{i:03d}" for i in range(u["qstart"], u["qstart"] + 5)]
    trace = "\n".join(f"<li>{step}</li>" for step in u["trace"])
    return f'''---
id: {u['id']}
title: {u['title']}
module: 02-Coroutines-Flow
tier: Core
estimated_minutes: 60
prerequisite_ids: {front_list(u['prereqs'])}
learning_outcomes:
  - Explain the runtime contract under interview pressure
  - Trace success failure cancellation and ownership
  - Review wrong code and defend a corrected design
  - Design deterministic tests and name evidence limits
status: reviewed
code_verification: tested
last_source_checked: {DATE}
source_urls:
''' + "\n".join(f"  - {s}" for s in u["sources"]) + f'''
example_paths:
  - {SRC}
  - {TEST}
question_ids: {front_list(qids)}
---

# {u['id']} — {u['title']}

**Interview target:** اشرح الـcontract، ارسم execution trace، راجع failure path، ثم اقترح test يفرق بين الأسباب المتنافسة. الاسم من غير trace مش إجابة senior.

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">المشكلة العملية في الوحدة دي: {u['failure']} المطلوب في المقابلة مش ذكر operator؛ المطلوب تربط الـsymptom بالـowner والـordering والـfailure policy، وبعدها تختار إصلاح تقدر تختبره.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">{u['model']}</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ابدأ من الـJob أو collection owner. كل child أو collector له lifetime، وكل value لها ordering وdelivery contract. الـguarantee الموثقة في الـAPI غير implementation detail وغير behavior خاص بـAndroid lifecycle. لما operation تعدّي boundary خارجية زي network أو database، إلغاء coroutine مش معناه rollback للعمل الخارجي.</p>

## Trace خطوة بخطوة — Execution trace

<ol dir="rtl" lang="ar">
{trace}
</ol>

<p dir="rtl" lang="ar">في المقابلة، سمّي المالك والعملية والـboundary قبل اختيار operator. فرّق بين نتيجة business، exception تقنية، وإلغاء بسبب انتهاء العمر. بعدين قول إيه اللي الاختبار يقدر يثبته وإيه اللي محتاج Android أو network integration.</p>

## Wrong and corrected implementation

```kotlin
{u['wrong']}
```

<p dir="rtl" lang="ar"><strong>المشكلة:</strong> {u['failure']}</p>

```kotlin
{u['correct']}
```

<p dir="rtl" lang="ar">التصحيح هنا يوضح intent، لكنه مش وصفة تتنسخ من غير requirements. راجع lifetime، ordering، backpressure، retry safety، وprivacy قبل production.</p>

## مثال Production حقيقي

<p dir="rtl" lang="ar">{u['scenario_body']} في production، ضيف identity للطلب أو الـJob في trace، وصنّف النهاية إلى success أو failure متوقعة أو cancellation أو stale drop. متسجلش payload حساسة، وحط rollout signal يقدر يوقف النشر لو correctness اتدهورت.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives

<p dir="rtl" lang="ar">استخدم الـprimitive لما contract البيانات يطابقها، مش عشان هي الأشهر. لو كل value لازم تتعالج، متستخدمش policy تسقط الوسط. لو العملية side effect غير قابلة للrollback، متعتمدش على cancellation وحدها. ولو lifetime قصيرة، متحطش الشغل في scope أطول من المالك. الحل الأبسط sequential أفضل لو مفيش استقلال حقيقي أو latency تستفيد من concurrency.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">{u['tests']}</p>

- Test the happy path and the first observable intermediate state.
- Force the failure at a named boundary; do not mock away the behavior under discussion.
- Cancel the owner and assert that no stale output appears later.
- Record the JVM/Android evidence boundary explicitly.

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> {u['model']}</p>

**English, 20 seconds:** “{u['english']}”

**English, 60–90 seconds:** “I begin with ownership and product semantics, then choose the coroutine or Flow primitive. I trace the successful path, ordinary failure, parent cancellation, and a late result. I keep recoverable errors explicit, preserve cancellation, and test scheduling with controlled gates rather than sleep. I also state the evidence boundary: a JVM test proves the pure contract, while lifecycle, transport, or device behavior needs the matching integration test.”

## Senior follow-ups

1. **{u['qs'][0][1]}** {u['qs'][0][2]}
2. **{u['qs'][1][1]}** {u['qs'][1][2]}
3. **{u['qs'][2][1]}** {u['qs'][2][2]}

## Misconceptions and revision

- API names are not a failure policy; draw the owner and child relationships.
- Cancellation is not rollback for an external side effect.
- A passing happy-path test is not evidence for ordering or cleanup.
- Buffering, retry, and supervision must preserve the product contract.

## Hands-on lab and further learning

<p dir="rtl" lang="ar">ابدأ باختبارات <a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt">CompletionModelsTest.kt</a>، وبعدها راجع implementation. غيّر test واحدة بحيث تكشف الحل الغلط قبل ما تعدّل الكود. مصادر الدرس فوق رسمية ومتراجعة بتاريخ {DATE}؛ Android-specific behavior لسه محتاج SDK integration.</p>

**Practice:** answer {qids[0]}–{qids[-1]}, solve [LAB-{u['lab']:03d}](../Coding-Challenges/LAB-{u['lab']:03d}-{slug(u['lab_title'])}.md), and investigate [SCN-{u['scenario']:03d}](../Real-World-Scenarios/SCN-{u['scenario']:03d}-{slug(u['scenario_title'])}.md).

**Evidence limit:** The linked Kotlin/JVM tests exercise the pure decision model. Android lifecycle and real transport behavior are sourced but not executed without the Android toolchain.
'''

def slug(text):
    import re
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def question_files(u):
    out = []
    difficulties = ["foundational", "senior", "intermediate", "senior", "senior"]
    styles = ["conceptual", "code-review", "debugging", "architecture", "debugging"]
    for offset, data in enumerate(u["qs"]):
        topic, prompt, spoken, ar, f1q, f1a, f2q, f2a = data
        n = u["qstart"] + offset
        qid = f"COR-Q{n:03d}"
        q = f'''---
id: {qid}
lesson_id: {u['id']}
topic: {topic}
difficulty: {difficulties[offset]}
style: {styles[offset]}
expected_minutes: {4 + (offset > 0)}
status: reviewed
---
# {qid} — {topic}

{prompt}

[Open complete model answer](../Model-Answers/{qid}.md) · [Lesson](../../{u['path']})
'''
        a = f'''---
id: {qid}-ANSWER
question_id: {qid}
status: reviewed
---
# {qid} — Complete model answer

**Spoken answer:** “{spoken}”

<p dir="rtl" lang="ar">{ar}</p>

**Mechanics:** Tie the answer to `{u['id']}`: identify the owner, the execution or collection boundary, the terminal states, and the exact behavior after cancellation. The official sources in the lesson were checked {DATE}.

**Common wrong answer:** “The API name guarantees correctness.” It does not; lifetime, failure, ordering, buffering, and external side effects still need an explicit contract.

**Follow-up 1:** {f1q}? {f1a} I would verify that claim at the named boundary with controlled inputs, then record the observable state transition rather than infer it from elapsed time.

**Follow-up 2:** {f2q}? {f2a} The chosen behavior belongs in the API or state contract, with a regression test for the most tempting alternative implementation.

**Rubric for self-review:** Give a direct answer, trace one failure, reject the tempting wrong fix, and name a deterministic test plus its evidence limit.
'''
        out.append((qid, q, a, difficulties[offset], styles[offset], topic))
    return out

def scenario(u):
    sid = f"SCN-{u['scenario']:03d}"
    return f'''---
id: {sid}
lesson_id: {u['id']}
status: reviewed
code_verification: tested
---
# {sid} — {u['scenario_title']}

## Reproduction and competing causes

<p dir="rtl" lang="ar">{u['scenario_body']}</p>

1. Capture an ordered trace with request or job identity.
2. Reproduce success, failure, cancellation, and late completion separately.
3. Change one boundary at a time and keep sensitive values out of logs.

## Correction and verification

<p dir="rtl" lang="ar">الإصلاح لازم يطابق contract الدرس، ويكون له regression test يثبت behavior مش الوقت. اعمل rollout تدريجي، وراقب cancellation، stale drops، failures المصنفة، والموارد المعلقة.</p>

## Senior follow-ups

1. **What evidence separates scheduling from business-state bugs?** A trace with owner, generation, cancellation, and publish timestamps.
2. **What is the rollback signal?** A predefined correctness or health regression, not a vague feeling after release.
3. **What remains unproved?** The JVM model does not prove Android lifecycle or production transport behavior.
'''

def lab(u):
    lid = f"LAB-{u['lab']:03d}"
    return f'''---
id: {lid}
lesson_id: {u['id']}
status: reviewed
code_verification: tested
---
# {lid} — {u['lab_title']}

<p dir="rtl" lang="ar"><strong>Contract:</strong> {u['lab_contract']}</p>

**Code:** [CompletionModels.kt](../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt)

**Tests:** [CompletionModelsTest.kt](../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt)

Run `./gradlew test --tests academy.CompletionModelsTest --no-daemon` from `projects/kotlin-jvm-labs`.

**Interview extension:** State the invariant, complexity or delivery guarantee before changing the implementation. Add one failure test that rejects a plausible wrong solution.
'''

for u in units:
    (ROOT / u["path"]).write_text(lesson(u), encoding="utf-8")
    for qid, q, a, *_ in question_files(u):
        (ROOT / f"Interview-Question-Bank/Questions/{qid}.md").write_text(q, encoding="utf-8")
        (ROOT / f"Interview-Question-Bank/Model-Answers/{qid}.md").write_text(a, encoding="utf-8")
    (ROOT / f"Real-World-Scenarios/SCN-{u['scenario']:03d}-{slug(u['scenario_title'])}.md").write_text(scenario(u), encoding="utf-8")
    (ROOT / f"Coding-Challenges/LAB-{u['lab']:03d}-{slug(u['lab_title'])}.md").write_text(lab(u), encoding="utf-8")
    (ROOT / f"Flashcards-Revision/{u['id']}.md").write_text(
        f"# {u['id']} revision cards\n\n" + "\n".join(f"{i+1}. **{q[0]}:** {q[2]}" for i, q in enumerate(u["qs"])) + "\n", encoding="utf-8")
    (ROOT / f"Speaking-Shadowing/DAY-{u['day']:02d}.md").write_text(
        f"# Day {u['day']} — {u['title']}\n\n## 20-second answer\n\n“{u['english']}”\n\n## Pressure prompts\n\n" + "\n".join(f"- {q[1]}" for q in u["qs"]) + "\n", encoding="utf-8")

# Keep the machine-readable catalog and interview registries synchronized with the authored files.
manifest_path = ROOT / "CONTENT-MANIFEST.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
items = manifest["items"]
by_id = {item["id"]: item for item in items}
examples = [
    "projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt",
    "projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt",
]
for u in units:
    qids = [f"COR-Q{i:03d}" for i in range(u["qstart"], u["qstart"] + 5)]
    topic = by_id[u["id"]]
    topic.update(status="reviewed", code_verification="tested", verification_evidence="BUILD-VERIFICATION.md",
                 question_ids=qids, example_paths=examples, source_urls=u["sources"], source_status="verified")
    for qid in qids:
        if qid not in by_id:
            entry = {
                "id": qid, "type": "question", "path": f"Interview-Question-Bank/Questions/{qid}.md",
                "answer_path": f"Interview-Question-Bank/Model-Answers/{qid}.md", "prerequisites": [u["id"]],
                "status": "reviewed", "code_verification": "not_applicable", "verification_evidence": "scripts/validate.py",
                "question_ids": [], "example_paths": [], "source_urls": [u["sources"][0]], "source_status": "verified",
            }
            items.append(entry); by_id[qid] = entry
    sid = f"SCN-{u['scenario']:03d}"
    if sid not in by_id:
        entry = {
            "id": sid, "type": "scenario", "path": f"Real-World-Scenarios/{sid}-{slug(u['scenario_title'])}.md",
            "prerequisites": [u["id"]], "status": "reviewed", "code_verification": "tested",
            "verification_evidence": "BUILD-VERIFICATION.md", "question_ids": [], "example_paths": examples,
            "source_urls": [u["sources"][0]], "source_status": "verified",
        }
        items.append(entry); by_id[sid] = entry
    lid = f"LAB-{u['lab']:03d}"
    if lid not in by_id:
        entry = {
            "id": lid, "type": "coding_challenge", "path": f"Coding-Challenges/{lid}-{slug(u['lab_title'])}.md",
            "prerequisites": [u["id"]], "status": "reviewed", "code_verification": "tested",
            "verification_evidence": "BUILD-VERIFICATION.md", "question_ids": [], "example_paths": examples,
            "source_urls": [u["sources"][0]], "source_status": "verified",
        }
        items.append(entry); by_id[lid] = entry
manifest["as_of"] = DATE
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

topic_index = ROOT / "Interview-Question-Bank/BY-TOPIC.md"
difficulty_index = ROOT / "Interview-Question-Bank/BY-DIFFICULTY.md"
style_index = ROOT / "Interview-Question-Bank/BY-INTERVIEW-STYLE.md"
topic_text = topic_index.read_text(encoding="utf-8")
difficulty_text = difficulty_index.read_text(encoding="utf-8")
style_text = style_index.read_text(encoding="utf-8")
for u in units:
    for qid, _, _, difficulty, style, topic_name in question_files(u):
        qlink = f"[${qid}]"  # replaced below to keep formatting obvious
        qlink = f"[{qid}](Questions/{qid}.md)"
        alink = f"[answer](Model-Answers/{qid}.md)"
        if f"Questions/{qid}.md" not in topic_text:
            topic_text += f"\n| {topic_name} | {qlink} | [Model answer](Model-Answers/{qid}.md) |"
        if f"Questions/{qid}.md" not in difficulty_text:
            difficulty_text += f"\n- {difficulty.title()}: {qlink} — {alink}"
        if f"Questions/{qid}.md" not in style_text:
            style_text += f"\n- {style.replace('-', ' ').title()}: {qlink} — {alink}"
topic_index.write_text(topic_text.rstrip() + "\n", encoding="utf-8")
difficulty_index.write_text(difficulty_text.rstrip() + "\n", encoding="utf-8")
style_index.write_text(style_text.rstrip() + "\n", encoding="utf-8")

coverage_path = ROOT / "COVERAGE-MATRIX.md"
coverage_lines = coverage_path.read_text(encoding="utf-8").splitlines()
for u in units:
    for index, line in enumerate(coverage_lines):
        if line.startswith(f"| {u['id']} |"):
            prereqs = ", ".join(u["prereqs"])
            qfirst, qlast = u["qstart"], u["qstart"] + 4
            coverage_lines[index] = (
                f"| {u['id']} | 02-Coroutines-Flow | Core | {prereqs} | 120 | [{u['id']}]({u['path']}) | "
                f"COR-Q{qfirst:03d}–{qlast:03d} | [JVM tests](projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt) | "
                f"[official]({u['sources'][0]}) | reviewed | Interview traces, failure policy and deterministic verification |"
            )
            break
coverage_path.write_text("\n".join(coverage_lines) + "\n", encoding="utf-8")

print(f"Authored {len(units)} coroutine lessons and {sum(len(u['qs']) for u in units)} interview pairs")

from harden_interview_bank import harden_bank
print("Hardened interview bank:", harden_bank())

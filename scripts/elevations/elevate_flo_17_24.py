#!/usr/bin/env python3
"""Elevate FLO-17 through FLO-24 with bilingual content parity and conversational spoken answers."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import elevation_engine as ee

TOPIC_AR = "الـ Flow و StateFlow و SharedFlow والـ Channels"
REVIEWED_DATE_AR = "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."

DATA = {}

# ==========================================
# FLO-17: flowOn and upstream execution
# ==========================================
DATA["FLO-17"] = {
    "concept_en": """The flowOn operator changes the CoroutineContext—most notably the CoroutineDispatcher—for upstream flow execution while preserving the context of downstream collectors, enforcing the fundamental flow invariant of Context Preservation.
In Kotlin Flow, the execution context naturally defaults to the CoroutineContext of the collector invoking collect. When heavy computations, cryptographic hashing, or blocking disk/network operations reside upstream, collecting on Dispatchers.Main freezes the UI frame pipeline.
The flowOn operator alters the dispatcher strictly for preceding (upstream) operators and producers without mutating downstream stages. Furthermore, flowOn introduces an asynchronous Channel buffer at the boundary between the upstream dispatcher and the downstream collector. This decouples thread execution: the upstream block produces elements on a background thread (e.g., Dispatchers.IO or Dispatchers.Default) and routes them into the channel buffer, allowing the downstream collector on Dispatchers.Main to consume items without thread-blocking or context leakage.""",
    "walkthrough_en": """Switching execution context cleanly with flowOn:
```kotlin
class ImageProcessingRepository(private val context: Context) {
    fun loadAndFilterBitmap(uri: Uri): Flow<Bitmap> = flow {
        // Runs on Dispatchers.IO because flowOn(Dispatchers.IO) is chained downstream:
        val rawBytes = context.contentResolver.openInputStream(uri)?.use { it.readBytes() }
            ?: throw IOException("Failed to read image")
        val bitmap = BitmapFactory.decodeByteArray(rawBytes, 0, rawBytes.size)
        val filtered = applySepiaFilter(bitmap) // CPU-intensive operation
        emit(filtered)
    }
    .flowOn(Dispatchers.IO) // Upstream executes on IO background threads!
    // Downstream collectors collect on their own dispatcher:
}

// In the ViewModel:
viewModelScope.launch(Dispatchers.Main) { // Collector runs on Main
    repository.loadAndFilterBitmap(imageUri)
        .collect { bitmap ->
            // Receives bitmap directly on Dispatchers.Main safely:
            _uiState.value = ImageUiState.Ready(bitmap)
        }
}
```""",
    "short_en": """flowOn changes the CoroutineDispatcher strictly for upstream operators and producers, preserving downstream collector context. It decouples execution across threads using an internal Channel buffer, allowing background thread production on Dispatchers.IO while safely collecting and updating UI on Dispatchers.Main.""",
    "structured_en": """To begin with, flowOn establishes clean thread boundaries by modulating the execution context of upstream producers.
From an architectural standpoint, Kotlin Flow strictly enforces context preservation: a flow must never emit directly from a different coroutine context than the collector's context. Rather than wrapping emit in withContext—which throws an IllegalStateException—we declare flowOn to switch upstream execution safely.
In production scenarios, flowOn allows data and domain layers to guarantee main-safety. A repository reading from disk or running complex parsing chains calls flowOn(Dispatchers.IO), ensuring that even if a ViewModel collects from the Main thread, the UI remains perfectly fluid without frame drops.
As for boundary management, flowOn applies strictly to upstream nodes. If multiple flowOn operators are chained, each one governs the segment immediately preceding it, creating distinct execution stages connected via asynchronous channel buffers.""",
    "deep_senior_en": """Under the hood in kotlinx.coroutines.flow, flowOn is implemented as ChannelFlowOperator. It validates that the downstream context is not violated. If a developer attempts to switch threads inside a flow builder using withContext(Dispatchers.IO) { emit(value) }, the internal check in SafeCollector catches the foreign CoroutineContext and throws an IllegalStateException: "Flow invariant is violated: Emission from another coroutine is prohibited".
To solve this cleanly, flowOn launches a dedicated coroutine in the specified CoroutineDispatcher, collecting the upstream flow and pushing elements into an internal Channel buffer (defaulting to BUFFERED capacity with 64 slots). The downstream collector then reads from this channel within its own caller context.
This architectural design decouples the producer and consumer execution loops across OS threads. Because emissions pass through a channel buffer, the producer can run ahead of a slow UI consumer up to the buffer limit, automatically managing backpressure by suspending the background coroutine when the buffer saturates.
Furthermore, chaining multiple flowOn operators establishes distinct execution segments. Upstream operators execute on their respective designated dispatchers without thread leakage, while downstream transformations default to the collector context unless explicitly overridden.
Staff engineers enforce repository main-safety: every repository flow performing I/O or intensive CPU transformation must append flowOn before exposing the stream, freeing UI consumers from dispatcher orchestration concerns.""",
    "meta_ar": {
        "id": "FLO-17",
        "questionAr": "كيف يؤثر مشغل flowOn على تنفيذ التدفق العلوي (Upstream)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- فهم مبدأ الحفاظ على السياق (Context Preservation) في Flow.\n- معرفة لماذا يُحظر استخدام withContext مع emit واستخدام flowOn كبديل معماري آمن.\n- استيعاب أن flowOn يؤثر فقط على ما قبله (Upstream) وينشئ Channel وسيطة بين الخيوط.",
        "why_it_matters_ar": "تشغيل عمليات ثقيلة زي فك تشفير الصور أو قراءة قواعد البيانات على خيط الـ Main يجمد واجهة المستخدم ويسبب أخطاء ANR، ومحاولة تغيير الخيط بـ withContext داخل الـ Flow تؤدي لكراش فوري بسبب انتهاك قيود كوتلن المعمارية.",
        "worked_example_ar": "نقل المعالجة الثقيلة لخيط الخلفية بأمان تام:\n```kotlin\nfun parseLargeJson(file: File): Flow<ParsedData> = flow {\n    // يعمل على Dispatchers.IO بسبب وجود flowOn في الأسفل:\n    val text = file.readText()\n    val result = jsonParser.parse(text)\n    emit(result)\n}\n.flowOn(Dispatchers.IO) // يغير الخيط لكل ما قبله فقط\n\n// في الواجهة: يتم الجمع على خيط الـ Main بأمان:\nviewModelScope.launch(Dispatchers.Main) {\n    parseLargeJson(file).collect { data -> updateUi(data) }\n}\n```",
        "trade_offs_ar": "`flowOn` يحقق الـ Main-safety بامتياز ويفصل الخيوط، ولكنه يضيف طبقة وسيطة (Channel Buffer) في الذاكرة لتمرير البيانات بين الخيوط.",
        "failure_modes_ar": "محاولة كتابة `withContext(Dispatchers.IO) { emit(...) }` داخل `flow { }` مما يتسبب في كراش `IllegalStateException`. خطأ آخر هو وضع `flowOn` في نهاية الـ Flow بعد دالة `collect` أو توقع تأثيره على ما بعده في السلسلة.",
        "production_perspective_ar": "في المشروعات الاحترافية، نلزم طبقة الـ Repository بضمان الـ Main-safety؛ أي دالة ترجع Flow يتضمن عمليات قراءة أو معالجة معقدة يجب أن تختم بـ `.flowOn(Dispatchers.IO)` أو `Default`، بحيث لا تضطر الواجهة لمعرفة أي Dispatcher مطلوب.",
        "how_to_answer_ar": "- **الوظيفة المعمارية:** `flowOn` يغير الـ CoroutineDispatcher للكود والعمليات السابقة له فقط (Upstream).\n- **مبدأ Context Preservation:** كوتلن تمنع تغيير الخيط عبر withContext حول emit وترمي IllegalStateException.\n- **كيف يعمل بالداخل:** ينشئ Channel وسيطة، المنتج ينتج في خيط الخلفية والمستهلك يجمع في خيطه الخاص بأمان.\n- **Main-safety:** جعل طبقة الـ Repository مسؤولة عن تحديد خيوطها لتبقى آمنة للاستدعاء من خيط الـ Main.\n- **سلسلة المشغلات:** لو وجد كذا flowOn، كل واحد يتحكم في الجزء الذي يسبقه مباشرة.",
        "talking_points_ar": "ناقش كلاس ChannelFlowOperator، وكيف يتحقق SafeCollector من تطابق الـ Context، ودور الـ Buffer الافتراضي (64 عنصر) في إدارة الضغط العكسي بين الخيوط.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لو استخدمت withContext حول دالة emit داخل الـ Flow؟\"\n  **المرشح:** \"التطبيق هيعمل كراش فوري بـ `IllegalStateException: Flow invariant is violated`. لأن كوتلن بتفرض مبدأ Context Preservation؛ مينفعش المشترك يطلب الجمع على الـ Main وتتفاجأ الواجهة بانبعاث قادم من خيط IO تاني. الحل المعتمد هو استخدام `flowOn`.\"\n\n- **المحاور:** \"لو وضعت `flowOn(Dispatchers.IO)` وبعده `map` وبعده `flowOn(Dispatchers.Default)`، كيف تتوزع الخيوط؟\"\n  **المرشح:** \"كود الـ Flow الأصلي هيشتغل على `Dispatchers.IO`، بعد كده معامل الـ `map` هيشتغل على `Dispatchers.Default`، والمستهلك النهائي بعدهم هيجمع على خيطه الخاص (زي Main)، لأن كل `flowOn` بيحكم الجزء اللي فوقه مباشرة.\"",
        "self_check_ar": "هل شرحت تأثير flowOn على الـ Upstream فقط؟ هل وضحت سبب كراش withContext؟ وهل بينت دوره في تحقيق Main-safety؟",
        "references_ar": f"- [Kotlin Flow context preservation](https://kotlinlang.org/docs/flow.html#flow-context) — توثيق كوتلن لسياق التدفق.\n- [flowOn official documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/flow-on.html) — توثيق مشغل flowOn.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "`flowOn` بيغير سياق التنفيذ والـ Dispatcher للكود اللي قبله فقط (Upstream) ومبيأثرش على المشترك اللي بعده. بيعمل ده عن طريق إنشاء قناة وسيطة بتسمح للمنتج يشتغل في الخلفية زي IO والمستهلك يجمع الداتا على خيط الواجهة بأمان تام بدون أي تجميد للشاشة.",
        "best_answer_ar": "مشغل `flowOn` هو الأداة الرسمية في كوتلن للتحكم في خيوط التنفيذ والـ Dispatchers داخل التدفقات، والسر فيه إنه بيطبق مبدأ مهم جداً اسمه الحفاظ على السياق (Context Preservation).\n\nلو عندك كود بينتج بيانات ثقيلة زي قراءة ملفات من الذاكرة أو فك تشفير صور، ومحتاج تعمله على خيط خلفي، مينفعش تكتب `withContext(Dispatchers.IO)` وتعمل جواه `emit`؛ لأن كوتلن هترمي كراش فوري `IllegalStateException` لحماية سياق المشترك.\n\nبدل كده، بنحط `flowOn(Dispatchers.IO)` في مسار التدفق؛ المشغل ده بيأثر حصراً على الكود والمعاملات اللي قبله (Upstream)، فيخلي كل العمليات العلوية تتنفذ على خيوط الـ IO، بينما المستهلك في الواجهة يقدر يجمع الداتا على خيط `Dispatchers.Main` بسلام وبدون أي تعليق للفريمات.\n\nوفي بيئات الإنتاج، بنستخدم `flowOn` في طبقة الـ Repository علشان نضمن مبدأ الـ Main-safety؛ يعني أي دالة ترجع Flow تكون آمنة 100% إن الواجهة تجمعها مباشرة بدون ما تشيل هم تبديل الخيوط.",
        "deep_answer_ar": "تحت الكابوت في مكتبة `kotlinx.coroutines`، مشغل `flowOn` بيطبق كلاس اسمه `ChannelFlowOperator`. لما الـ Collector بينادي `collect()`، الـ `flowOn` مبيسمحش بتشغيل كود المنتج مباشرة على نفس سياق المستدعي لو كان الـ Dispatcher مختلف؛ هو بيفتح كوروتين جديدة مخصصة على الـ Dispatcher المحدد (زي `Dispatchers.IO`) ويجمع التدفق العلوي فيها، وبيمرر العناصر للجامع السفلي عبر `Channel` وسيطة حجمها الافتراضي 64 عنصر.\n\nالآلية دي هي اللي بتمنع كراش انتهاك القواعد المعمارية (Flow Invariant Violation)؛ لأن كلاس `SafeCollector` الداخلي بيعمل مقارنة بين سياق الكوروتين الحالية وسياق المشترك الأصلي، فلو لقى انبعاث بيحصل من سياق مختلف بدون قناة وسيطة بيرمي استثناء فوراً.\n\nالميزة الإضافية للـ Channel الوسيطة دي هي تنظيم الضغط العكسي (Backpressure)؛ لو معالجة الـ IO سريعة جداً وخيط الـ Main مشغول في رسم فريم، القناة بتستوعب العناصر لحد ما تتملي، وأول ما تتملي بتعلق كوروتين الـ IO تلقائياً لحد ما خيط الـ Main يسحب عنصر ويفضي مكان في القناة.\n\nولو عندك كذا `flowOn` في نفس السلسلة، كل مشغل بيحكم فقط النطاق اللي بيسبقه مباشرة لحد ما يقابل `flowOn` تاني أو يوصل لمنبع التدفق، وده بيدي مرونة فائقة لتقسيم العمليات بين حسابات رياضية على `Default` وقراءات قرص على `IO`، وفي النهاية الجمع بيكون على `Main` بأعلى كفاءة ممكنة."
    }
}

# ==========================================
# FLO-18: catch, retry, retryWhen, onCompletion
# ==========================================
DATA["FLO-18"] = {
    "concept_en": """Flow error handling and completion mechanisms rely on catch, retry, retryWhen, and onCompletion, which provide structured, declarative management of exceptions and termination lifecycles without disrupting coroutine hierarchies.
catch encapsulates upstream exceptions, preventing crashes by handling errors, executing recovery logic, or emitting fallback default states; crucially, it handles exceptions occurring strictly upstream, leaving downstream collector exceptions untouched.
retry and retryWhen intercept upstream exceptions and resubscribe to the upstream flow from the beginning, either for a fixed iteration count or based on dynamic predicate evaluations (such as applying exponential backoff delays for network recovery).
onCompletion acts as a reactive finally block, executing when the flow terminates either normally upon reaching EOF or exceptionally due to an unhandled failure or cancellation, receiving a nullable Throwable cause parameter to distinguish clean completion from failure.""",
    "walkthrough_en": """Resilient error handling and retry with exponential backoff:
```kotlin
fun observeExchangeRates(): Flow<ExchangeRates> = flow {
    emit(api.fetchLiveRates()) // Might throw IOException
}
.retryWhen { cause, attempt ->
    if (cause is IOException && attempt < 3) {
        val backoffDelay = (attempt + 1) * 1000L
        delay(backoffDelay) // Exponential backoff: 1s, 2s, 3s
        true // Resubscribes upstream
    } else {
        false // Do not retry, let exception propagate to catch
    }
}
.catch { throwable ->
    // Handle error gracefully by emitting offline cached rates:
    emit(cacheDao.getCachedRates())
}
.onCompletion { cause ->
    if (cause != null) logError("Stream terminated with error: $cause")
    else logInfo("Stream completed successfully")
}
```""",
    "short_en": """catch captures upstream exceptions and can emit fallback values; retry and retryWhen re-collect upstream upon errors based on retry counts or backoff predicates; and onCompletion executes at stream termination, receiving a nullable Throwable indicating clean completion or failure.""",
    "structured_en": """To begin with, declarative error operators in Flow isolate exception handling from procedural try-catch blocks.
From an architectural standpoint, catch intercepts errors originating strictly upstream. When an upstream database query or network call throws an exception, catch absorbs the failure, logs diagnostic telemetry, and conditionally emits a fallback state, preventing unhandled exceptions from crashing the parent CoroutineScope.
In production scenarios, transient network failures require resilience. retry resubscribes up to a fixed attempt limit, while retryWhen allows senior engineers to implement exponential backoff by inspecting the error type and applying delay before returning true.
As for boundary management, onCompletion serves as the declarative lifecycle finalizer. It executes regardless of whether the stream finishes normally, cancels due to lifecycle changes, or aborts via an error, enabling deterministic cleanup of socket handles, file descriptors, and loading indicators.""",
    "deep_senior_en": """Under the hood in kotlinx.coroutines.flow, catch operates by intercepting exceptions thrown during upstream FlowCollector.emit or transformation calls. When an exception is trapped, catch verifies the exception type: if the exception is a CancellationException, it rethrows it immediately to preserve structured concurrency cancellation semantics.
Crucially, catch cannot trap downstream exceptions. If an exception is thrown inside the action block of collect { ... }, downstream of catch, catch will not intercept it, causing the coroutine to crash. To protect against downstream collection crashes, developers must place catch after intermediate operators or wrap the collector block in procedural try-catch.
retry and retryWhen operate by wrapping the upstream flow inside an iterative loop. When an exception occurs, if the predicate returns true, the operator cancels the failed subscription and invokes collect on the original upstream Flow from the beginning. This requires upstream producers to be idempotent; if an upstream flow performed partial mutations before throwing, retrying without rollback duplicates operations.
In addition, onCompletion intercepts stream termination by inspecting the nullable Throwable cause parameter. If upstream fails or the parent job cancels, the cause is forwarded into the lambda for diagnostics and resource cleanup before the exception propagates downstream.
Staff engineers structure error boundaries cleanly: placing retryWhen with backoff upstream, followed by catch emitting cached UI state models, and finishing with onCompletion resetting loading spinners.""",
    "meta_ar": {
        "id": "FLO-18",
        "questionAr": "قارن بين مشغلات معالجة الأخطاء: catch و retry و retryWhen و onCompletion",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- الفهم المعماري للتعامل التصريحي مع الأخطاء في Flow.\n- إدراك أن catch يلتقط الأخطاء العلوية فقط (Upstream) ولا يمسك أخطاء collect السفلية.\n- معرفة كيفية تطبيق التراجع الأسي (Exponential Backoff) بـ retryWhen ودور onCompletion ككتلة finally تفاعلية.",
        "why_it_matters_ar": "التعامل الخاطئ مع الاستثناءات يسقط التطبيق فوراً؛ فاعتقاد المطور أن `catch` يحميه من أخطاء داخل `collect` يسبب كراشات غير متوقعة، بينما غياب `retryWhen` الذكي يجبر المستخدم على الضغط اليدوي لإعادة المحاولة عند أبسط تذبذب في الشبكة.",
        "worked_example_ar": "بناء مسار مرن للتعافي من أخطاء الشبكة:\n```kotlin\nratesRepository.fetchRatesFlow()\n    .retryWhen { cause, attempt ->\n        // إعادة المحاولة 3 مرات مع تأخير زمني عند أخطاء الشبكة المؤقتة:\n        cause is IOException && attempt < 3 && run { delay(1000L * (attempt + 1)); true }\n    }\n    .catch { error ->\n        emit(ratesDao.getLastKnownRates()) // إرسال الكاش القديم كبديل آمن\n    }\n    .onCompletion { cause ->\n        hideLoadingSpinner() // تنظيف الموارد وإخفاء اللودينج سواء نجح أو فشل\n    }\n```",
        "trade_offs_ar": "`catch` ممتاز للتعافي السلس وبث قيم بديلة، ولكنه قد يخفي أخطاء برمجية حقيقية لو لم يتم تسجيلها. `retry` يعزز المرونة ولكنه يتطلب أن تكون العمليات العلوية آمنة للتكرار (Idempotent).",
        "failure_modes_ar": "وقوع استثناء داخل كود `collect { ... }` والاعتقاد بأن مشغل `catch` بالأعلى سيمسكه؛ حيث سيتجاهله catch ويسقط التطبيق. خطأ آخر هو كتم استثناء `CancellationException` مما يمنع إلغاء الكوروتين ويسرب الموارد.",
        "production_perspective_ar": "في المشروعات الكبرى، نصمم سياسة أخطاء موحدة: استخدام `retryWhen` لأخطاء الـ Timeout مع exponential backoff، واستخدام `catch` في الـ ViewModel لتحويل الاستثناءات إلى حالات خطأ بصرية في الـ State، واستخدام `onCompletion` لتنظيف مؤشرات التحميل.",
        "how_to_answer_ar": "- **catch:** يمسك الاستثناءات القادمة من الأعلى (Upstream)، ويتيح تسجيلها أو بث قيمة بديلة (Fallback).\n- **قاعدة catch الذهبية:** لا يلتقط استثناءات كود collect السفلي؛ لحمايتها يجب وضع try-catch حول collect أو وضع المشغلات قبله.\n- **retry و retryWhen:** يعيدان الاشتراك في التدفق من البداية؛ retryWhen يسمح بفحص نوع الخطأ وتطبيق تأخير زمني (Backoff).\n- **onCompletion:** مثل بلوك `finally`؛ يعمل عند انتهاء التدفق سواء اكتمل بنجاح أو بكراش أو بإلغاء، ويستلم معامل Throwable لمعرفة السبب.\n- **احترام الإلغاء:** التأكيد على عدم اعتراض `CancellationException` لضمان عمل Structured Concurrency.",
        "talking_points_ar": "ناقش كيف يعيد retry الاشتراك عبر حلقة تكرارية، وكيف يتجاهل catch الـ Downstream Exceptions عمداً، ودور معامل cause في onCompletion للتمييز بين النجاح والإلغاء.",
        "follow_ups_ar": "- **المحاور:** \"لماذا لا يلتقط مشغل catch الأخطاء التي تحدث داخل دالة collect؟\"\n  **المرشح:** \"لأن Flow بيطبق مبدأ الشفافية وحصر المسؤولية؛ `catch` بيعالج فقط الأخطاء اللي حصلت في العمليات اللي فوقه (Upstream). لو حصل كراش جوه بلوك `collect` بتاعك، ده معناه إن فيه Bug في معالجة البيانات في الواجهة، فالمكتبة بتسيبه يترمي علشان ميتمش كتم أخطاء الواجهة خلسة.\"\n\n- **المحاور:** \"كيف تفرق في onCompletion بين التدفق الذي انتهى طبيعياً والتدفق الذي ألغي؟\"\n  **المرشح:** \"عبر فحص معامل `cause`؛ لو كان `null` يبقى التدفق كمل طبيعي للنهاية. لو كان نوعه `CancellationException` يبقى الشاشة اتقفلت والكوروتين اتلغت، ولو كان استثناء تاني زي `IOException` يبقى التدفق ضرب كراش غير معالج.\"",
        "self_check_ar": "هل بينت اختصاص catch بالأخطاء العلوية فقط؟ هل شرحت التراجع الأسي في retryWhen؟ وهل وضحت دور onCompletion كبديل لـ finally؟",
        "references_ar": f"- [Kotlin Flow exception handling](https://kotlinlang.org/docs/flow.html#flow-exceptions) — دليل كوتلن الرسمي للتعامل مع الاستثناءات.\n- [Flow catch operator docs](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/catch.html) — توثيق مشغل catch.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "`catch` بيمسك أخطاء التدفق العلوي وبيقدر يبعت داتا بديلة من الكاش بس مبيشوفش أخطاء collect السفلية. و`retry` و `retryWhen` بيعيدوا المحاولة من الأول مع إمكانية عمل تأخير زمني، أما `onCompletion` فده زي بلوك `finally` بيشتغل لما التدفق يخلص سواء بنجاح أو بكراش أو بإلغاء.",
        "best_answer_ar": "إدارة الأخطاء في Flow بتعتمد على مجموعة مشغلات تصريحية بتغنينا عن فوضى كتل try-catch التقليدية.\n\nمشغل `catch` وظيفته التقاط أي استثناء يحصل في العمليات العلوية (Upstream)؛ زي فشل نداء الشبكة أو تعطل استعلام الداتابيز. لما بيمسك الخطأ، بيسجله في الـ Crashlytics ويقدر يعمل `emit` لقيمة بديلة من الكاش المحلي علشان الواجهة متتعطلش، لكن مهم جداً نتذكر إنه مبيشوفش ولا بيمسك أي استثناء يحصل جوه كود الـ `collect` السفلي.\n\nمشغل `retryWhen` هو بطل المرونة في الشبكات الضعيفة؛ بيفحص سبب الفشل وعدد المحاولات السابقة، وبنستخدمه لتطبيق التراجع الأسي (Exponential Backoff)؛ يعني لو الاتصال فصل، يستنى ثانية ويعيد المحاولة، لو فشل يستنى ثانيتين، وهكذا قبل ما يستسلم ويرمي الخطأ لـ catch.\n\nوأخيراً `onCompletion` بيمثل بلوك `finally` التفاعلي؛ بيتنفذ حتماً أول ما التدفق يتقفل، سواء قفل طبيعي بنجاح، أو اتلغى لأن المستخدم خرج من الشاشة، أو رمى استثناء غير معالج. وبيدينا معامل `cause` اللي بنفحصه علشان نقفل مؤشرات التحميل (Spinners) وننظف الموارد بنظافة تامة.",
        "deep_answer_ar": "على مستوى الميكانيزم الداخلي في مكتبة الكوروتينات، `catch` بيغلف الـ `FlowCollector` الداخلي بـ `try-catch` بيمسك أي `Throwable` صادر من الـ Upstream. الميزة الجوهرية هنا هي احترامه الصارم لمبدأ الـ Structured Concurrency؛ لو الاستثناء كان من نوع `CancellationException`، المشغل مبيكتموش، هو بيعيده فوراً (Rethrow) علشان يتيح للكوروتين الحاضنة إنها تتفكك وتلغي المهام التابعة بدون أي تسريب موارد.\n\nوالنقطة الهندسية اللي بيختبروك فيها دايماً في المقابلات هي سلوك `catch` مع الـ Downstream؛ لو كتبت: `flow.catch { ... }.collect { throw RuntimeException() }`، التطبيق هيعمل كراش فوراً والـ `catch` مش هيدخل فيه نهائياً. ده قرار تصميمي مقصود في كوتلن؛ لأن الاستثناء حصل في كود المشترك مش في خط إنتاج البيانات، وعلاجه وضع `try-catch` صريحة داخل `collect`.\n\nمشغل `retryWhen` بيشتغل عبر حلقة `while` بتجمع الـ Flow من البداية. لو حصل استثناء، بيبعت الاستثناء ورقم المحاولة للـ Predicate. لو رجعت `true`، بيلغي الاشتراك الفاشل ويبدأ `collect` جديد من أول سطر في الـ Flow العلوي، وده بيفرض شرط معماري إن الـ Upstream Flow لازم يكون Idempotent وملوش آثار جانبية مكررة.\n\nأما `onCompletion`، فبيعتمد على الـ Continuation Interceptor؛ بيضمن تشغيل الكود المحدد سواء اكتمل الـ Flow بسلام (`cause == null`) أو بكراش صريح أو بـ `JobCancellation`. وده بيخليه الأداة المثالية لإغلاق المقابس وتصفير مؤشرات الـ UI Loading في كل الحالات الممكنة."
    }
}

# ==========================================
# FLO-19: replay, extraBufferCapacity, BufferOverflow in SharedFlow
# ==========================================
DATA["FLO-19"] = {
    "concept_en": """Configuring MutableSharedFlow relies on three interrelated buffering parameters: replay, extraBufferCapacity, and onBufferOverflow, which govern backpressure mitigation, subscriber catch-up, and memory allocation.
replay designates the size of the replay cache—the exact number of previously emitted elements retained in memory and instantly delivered to newly attached subscribers.
extraBufferCapacity designates additional reserved buffer slots beyond the replay cache, providing temporary shock absorption when upstream producers generate emissions faster than downstream subscribers can consume them.
onBufferOverflow defines the precise eviction strategy executed when the total buffer capacity (the sum of replay plus extraBufferCapacity) is fully saturated. It supports three distinct strategies: BufferOverflow.SUSPEND (suspends the emitter until buffer space frees up), BufferOverflow.DROP_OLDEST (evicts the oldest buffered element to accommodate the incoming item without suspending), and BufferOverflow.DROP_LATEST (discards the newly arriving emission immediately, preserving existing buffer contents).""",
    "walkthrough_en": """Tuning SharedFlow buffer parameters for production workloads:
```kotlin
class LiveEventBus {
    // 1. Lossless event bus: Suspends emitter, guarantees zero event drops
    private val _criticalEvents = MutableSharedFlow<PaymentEvent>(
        replay = 0,
        extraBufferCapacity = 64,
        onBufferOverflow = BufferOverflow.SUSPEND
    )
    val criticalEvents = _criticalEvents.asSharedFlow()

    // 2. High-throughput sensor ticker: Never suspends, drops oldest ticks
    private val _sensorTicks = MutableSharedFlow<Float>(
        replay = 1, // Latest tick delivered to new screens
        extraBufferCapacity = 16,
        onBufferOverflow = BufferOverflow.DROP_OLDEST // Drops stale ticks under load
    )
    val sensorTicks = _sensorTicks.asSharedFlow()

    suspend fun postPayment(event: PaymentEvent) {
        _criticalEvents.emit(event) // Suspends if buffer fills up
    }

    fun postTick(value: Float) {
        _sensorTicks.tryEmit(value) // Always returns true with DROP_OLDEST
    }
}
```""",
    "short_en": """replay sets how many past items are replayed to new subscribers; extraBufferCapacity adds buffer headroom beyond replay; and onBufferOverflow decides what happens when the buffer fills up: SUSPEND pauses the emitter, DROP_OLDEST evicts the oldest item, and DROP_LATEST drops the incoming item.""",
    "structured_en": """To begin with, configuring MutableSharedFlow requires balancing memory consumption against backpressure and subscriber guarantees.
From an architectural standpoint, replay controls historical catch-up for newly attached observers. Setting replay = 1 mirrors StateFlow behavior, whereas replay = 0 ensures subscribers receive strictly future emissions, preventing stale event replays.
In production scenarios, extraBufferCapacity decouples producer velocity from consumer processing latency. When background tasks produce bursts of events, this extra cushion prevents immediate emitter suspension, smoothing out processing spikes.
As for boundary management, onBufferOverflow governs the saturation policy when total buffer capacity is exceeded. Using BufferOverflow.SUSPEND ensures zero data loss for transactional workloads like audit logs. In contrast, BufferOverflow.DROP_OLDEST is mandatory when using tryEmit from non-suspending contexts, guaranteeing that freshest sensor updates override stale pending data without blocking threads.""",
    "deep_senior_en": """Under the hood in SharedFlow.kt, emissions are managed across an internal circular buffer array whose capacity equals replay + extraBufferCapacity. Each active subscriber is tracked via a SharedFlowSlot holding an index pointer into this circular array.
When an emitter invokes emit(value), the implementation checks whether any active subscriber is lagging behind. If the distance between the newest element index and a lagging subscriber's index exceeds the allocated total buffer capacity, a buffer overflow condition occurs.
If onBufferOverflow is configured as SUSPEND, the emitter creates a CancellableContinuation and enters a suspended state, enqueueing itself until the lagging subscriber advances its index pointer and frees buffer space. However, if onBufferOverflow is configured as DROP_OLDEST, the buffer simply advances the head pointer, dropping the oldest element and immediately resuming without suspending. This enables tryEmit(value) to succeed synchronously without suspending the caller. Conversely, DROP_LATEST drops the incoming item, leaving the buffer unaltered.
A critical architectural pitfall occurs when configuring replay = 0, extraBufferCapacity = 0, and default SUSPEND. Under this configuration, tryEmit always returns false if there are no active subscribers, dropping the event completely.
Staff engineers enforce clear rules: high-frequency real-time telemetry uses DROP_OLDEST to ensure tryEmit never blocks, while critical business commands use extraBufferCapacity with SUSPEND to guarantee lossless delivery.""",
    "meta_ar": {
        "id": "FLO-19",
        "questionAr": "اشرح معاملات: replay و extraBufferCapacity و BufferOverflow في SharedFlow",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- الفهم الدقيق لمعاملات الـ Buffer في MutableSharedFlow.\n- التمييز بين حجم كاش الإعادة (replay) وسعة التخزين الإضافية (extraBufferCapacity).\n- استيعاب استراتيجيات BufferOverflow الثلاثة وأثرها على دالة tryEmit ونجاحها المتزامن.",
        "why_it_matters_ar": "الضبط الخاطئ لمعاملات `SharedFlow` قد يتسبب في فقدان معاملات دفع حرجة إذا تم استخدام `DROP_OLDEST`، أو في تجميد خيط المعالجة بالكامل إذا تم استخدام `SUSPEND` مع مستهلك بطيء، وفهم الفرق يحمي النظام من تسريب الذاكرة وتجمد التطبيق.",
        "worked_example_ar": "ضبط SharedFlow للتعامل مع الأحداث بدون فقدان أو تعليق:\n```kotlin\n// طابور أحداث مصرفية: يمنع ضياع أي حدث ويعلق المنتج لو امتلأ الطابور\nval paymentEvents = MutableSharedFlow<PaymentEvent>(\n    replay = 0, // لا يعيد أي حدث قديم للشاشات الجديدة\n    extraBufferCapacity = 32, // طابور وسيط يستوعب 32 حدث\n    onBufferOverflow = BufferOverflow.SUSPEND // تعليق المنتج لو الطابور اتملى\n)\n\n// تدفق أسعار العملات: يسقط الأسعار القديمة ويحتفظ بأحدث سعر فوراً\nval tickerEvents = MutableSharedFlow<PriceTick>(\n    replay = 1, // إعطاء أحدث سعر لأي شاشة تفتح\n    extraBufferCapacity = 16,\n    onBufferOverflow = BufferOverflow.DROP_OLDEST // مسح السعر القديم لو زاد الضغط\n)\n```",
        "trade_offs_ar": "`BufferOverflow.SUSPEND` تضمن عدم فقدان أي بيانات نهائياً ولكنها قد تعلق المنتج. `DROP_OLDEST` تمنع تعليق الكود وتجعل `tryEmit` متزامنة وناجحة دائماً ولكنها تسقط البيانات القديمة عند الضغط.",
        "failure_modes_ar": "استخدام `MutableSharedFlow()` بالقيم الافتراضية (`replay = 0, extraBufferCapacity = 0, onBufferOverflow = SUSPEND`) واستدعاء `tryEmit`، حيث ستفشل الدالة دائماً وترجع `false` ويضيع الحدث لو مفيش جامع جاهز في نفس الملي ثانية.",
        "production_perspective_ar": "في المشروعات الكبيرة، نمنع استخدام `tryEmit` إلا إذا كان `extraBufferCapacity > 0` أو استراتيجية الطفح هي `DROP_OLDEST`. للأحداث الحساسة، نستخدم `emit` المعلقة مع `SUSPEND` لضمان استلام كل حركة بنكية بنجاح.",
        "how_to_answer_ar": "- **replay:** عدد العناصر السابقة التي يحتفظ بها في الذاكرة ويبثها فوراً لأي مشترك جديد ينضم لاحقاً.\n- **extraBufferCapacity:** سعة تخزين إضافية فوق الـ replay لامتصاص طفرات السرعة بين المنتج والمستهلك.\n- **BufferOverflow:** سياسة التصرف لو الطابور الكلي (replay + extra) اتملى بالكامل:\n  1. `SUSPEND:` تعليق الـ Emitter لحد ما المشترك البطيء يقرأ ويفضي مكان.\n  2. `DROP_OLDEST:` مسح أقدم عنصر في الطابور وإدخال الجديد بدونه تعليق.\n  3. `DROP_LATEST:` إسقاط العنصر الجديد القادم والحفاظ على الطابور كما هو.\n- **أثرها على tryEmit:** دالة `tryEmit` المتزامنة تنجح فوراً مع DROP_OLDEST وتفشل لو كان SUSPEND والطابور ممتلئاً.",
        "talking_points_ar": "ناقش الـ Circular Buffer الداخلي في SharedFlow.kt، ودور مؤشر SharedFlowSlot لكل مشترك، ومأزق tryEmit مع الإعدادات الافتراضية.",
        "follow_ups_ar": "- **المحاور:** \"لماذا تفشل دالة tryEmit دائماً مع MutableSharedFlow بالقيم الافتراضية؟\"\n  **المرشح:** \"لأن بالقيم الافتراضية الـ buffer سعته صفر والسياسة هي SUSPEND؛ فلما تستدعي `tryEmit` ومفيش جامع نشط معلق مستني، مفيش أي مكان في الذاكرة لتخزين الحدث وبما إن tryEmit دالة عادية مش suspend ومتقدرش تعلق الكود، فبترجع `false` فوراً والحدث بيضيع.\"\n\n- **المحاور:** \"متى تختار DROP_OLDEST ومتى تختار SUSPEND في بيئة إنتاجية؟\"\n  **المرشح:** \"بنختار `DROP_OLDEST` لما تكون البيانات عبارة عن قراءات متجددة زي أسعار أسهم أو مؤشرات GPS والمستخدم يهمه الأحدث دائماً. وبنختار `SUSPEND` لما تكون البيانات أحداث حيوية مينفعش تضيع زي عمليات الدفع أو أوامر التحويل البنكي.\"",
        "self_check_ar": "هل شرحت وظيفة المعاملات الثلاثة بدقة؟ هل وضحت العلاقة بين السعة الكلية وسياسة الطفح؟ وهل كشفت مأزق tryEmit؟",
        "references_ar": f"- [MutableSharedFlow official documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-mutable-shared-flow.html) — توثيق كوتلن الرسمي لـ MutableSharedFlow.\n- [SharedFlow buffering guide](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) — دليل أندرويد الرسمي لـ SharedFlow.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "`replay` بيحدد كام عنصر قديم يتبعت للمشترك الجديد أول ما يفتح، و`extraBufferCapacity` سعة إضافية في الذاكرة لامتصاص فرق السرعة، و`BufferOverflow` هي السياسة لو الطابور اتملى: يا إما `SUSPEND` يعلق الكود، أو `DROP_OLDEST` يسقط أقدم عنصر، أو `DROP_LATEST` يسقط العنصر الجديد.",
        "best_answer_ar": "المعاملات التلاتة دول هما اللي بيحددوا شخصية الـ `SharedFlow` وطريقة تعامله مع الذاكرة والضغط العكسي في كوتلن.\n\nمعامل `replay` بيحدد حجم الكاش التاريخي؛ يعني لو خليته 1، أي شاشة جديدة تشترك هتستلم آخر قيمة انبعثت فوراً زي StateFlow، ولو خليته صفر، المشترك الجديد هيستلم فقط الأحداث المستقبلية اللي هتحصل بعد لحظة اشتراكه.\n\nمعامل `extraBufferCapacity` هو وسادة الأمان الإضافية؛ مساحة تخزين فوق الـ replay معمولة علشان تمتص طفرات السرعة لو المنتج بيبعت بيانات بسرعة والواجهة أو المستهلك واخدين وقت في المعالجة، فبيمنع تعليق المنتج فوراً.\n\nوأخيراً `BufferOverflow` هي خطة الطوارئ أول ما مساحة الـ Buffer الكلية (replay + extra) تتملي على آخرها:\nلو اخترت `SUSPEND`، المنتج بيتعلق ومبيكملش إلا لما المستهلك يقرا ويفضي مكان، وده بيضمن صفر فقدان للبيانات في العمليات البنكية. ولو اخترت `DROP_OLDEST`، النظام بيمسح أقدم عنصر في الطابور ويدخل العنصر الجديد مكانه بدون أي تعليق، وده بيمكننا من استخدام `tryEmit` المتزامنة بنجاح 100% لتحديثات الحساسات والبورصة السريعة.",
        "deep_answer_ar": "تحت الكابوت في `SharedFlow.kt`، البيانات بتتخزن في مصفوفة دائرية (Circular Array Buffer) حجمها الإجمالي بيساوي حاصل جمع `replay + extraBufferCapacity`. كل مشترك بيتم تمثيله بكائن `SharedFlowSlot` جواه مؤشر (Index Pointer) بيتعقب موقعه في قراءة المصفوفة دي.\n\nلما المنتج بيستدعي `emit(value)`، الكود بيفحص المسافة بين أحدث عنصر اتكتب ومؤشر أبطأ مشترك موجود. لو المسافة دي تجاوزت حجم الـ Buffer الكلي، بيحصل طفح (Buffer Overflow).\n\nهنا بيتحدد السلوك حسب `onBufferOverflow`:\nلو كانت `SUSPEND`، كود الـ emit بينشئ كائن `CancellableContinuation` وبيعلق نفسه ويدخل في طابور انتظار داخلي لحد ما المشترك البطيء يسحب عناصر ويحرك مؤشره للأمام فيصحى المنتج.\n\nأما لو كانت `DROP_OLDEST`، المشغل ببساطة بيحرك مؤشر بداية الـ Buffer خطوة للأمام ويسقط أقدم عنصر بدون ما يعلق الكوروتين، وده السر الهندسي اللي بيخلي استدعاء `tryEmit()` يرجع `true` فوراً بدون الحاجة لدوال معلقة.\n\nوهنا بتظهر أشهر مصيدة برمجية في أندرويد: لما مبرمج ينشئ `MutableSharedFlow()` بالقيم الافتراضية (`replay = 0, extraBufferCapacity = 0, SUSPEND`) ويحاول ينادي `tryEmit()`؛ الدالة هترجع `false` والحدث هيضيع في الهواء تماماً لو مفيش مشترك معلق في نفس اللحظة!\n\nعلشان كده في بيئات الإنتاج، بنفرض قاعدة صارمة: إما استخدام `emit` المعلقة للأحداث الحتمية مع `SUSPEND`، أو تخصيص `extraBufferCapacity > 0` مع `DROP_OLDEST` لو هنعتمد على `tryEmit` المتزامنة."
    }
}

# ==========================================
# FLO-20: Channel vs SharedFlow (Event Loss & Delivery)
# ==========================================
DATA["FLO-20"] = {
    "concept_en": """The architectural distinction between Channel and SharedFlow centers on communication topology, delivery guarantees, and event-loss characteristics under lifecycle transitions.
Channel is a point-to-point (unicast), queue-based communication primitive. Every element sent to a Channel is delivered to and consumed by exactly one receiver; if multiple collectors listen to the same Channel, emissions are distributed competitively (fan-out worker queue) rather than broadcasted. Importantly, a buffered Channel retains elements in memory until consumed, guaranteeing that one-off events are not lost even if the UI is temporarily stopped.
SharedFlow is a broadcasting (multicast), hot reactive stream. Every element emitted is distributed simultaneously to all active collectors. However, SharedFlow requires active subscribers at emission time; if an event is emitted when zero subscribers are active (and replay cache is zero), the event is dropped permanently into the void, creating catastrophic event loss for navigation intents during lifecycle pauses.""",
    "walkthrough_en": """Contrasting Channel unicast delivery with SharedFlow multicasting:
```kotlin
class OrderProcessingViewModel : ViewModel() {
    // 1. Channel: Guarantees delivery to exactly ONE receiver, buffers during onStop
    private val _navigationChannel = Channel<OrderNavigationEvent>(Channel.BUFFERED)
    val navigationEvents = _navigationChannel.receiveAsFlow()

    // 2. SharedFlow: Broadcasts to ALL active screens, drops if no one is listening
    private val _orderUpdates = MutableSharedFlow<OrderBroadcast>(
        replay = 0,
        extraBufferCapacity = 16,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val orderUpdates = _orderUpdates.asSharedFlow()

    fun onOrderApproved(orderId: String) {
        viewModelScope.launch {
            // Buffered until UI unpauses: Never lost!
            _navigationChannel.send(OrderNavigationEvent.OpenReceipt(orderId))

            // Multicast to all active observer screens:
            _orderUpdates.emit(OrderBroadcast.StatusChanged(orderId, "APPROVED"))
        }
    }
}
```""",
    "short_en": """Channel is a unicast queue delivering each item to exactly one consumer, buffering events safely during UI pauses. SharedFlow is a multicast stream broadcasting to all active observers simultaneously, but drops emissions permanently if no subscribers exist at emission time unless replay or buffer is configured.""",
    "structured_en": """To begin with, Channel and SharedFlow represent fundamentally distinct concurrency primitives serving opposing architectural topologies.
From an architectural standpoint, Channel implements queue semantics (unicast). Elements sent into a Channel remain in its buffer until a consumer dequeues them. When multiple collectors observe a Channel, each emission is consumed by only one worker, making Channel ideal for transactional work distribution.
In production scenarios, SharedFlow implements pub-sub broadcasting (multicast). Every emission is fanned out concurrently to all registered collectors, making it the premier choice for broadcasting state invalidation, user logout notifications, or global configuration updates across multiple screens.
As for boundary management, the primary risk with SharedFlow is event loss. If an event is emitted while an Activity is in onStop and has detached its collector, a SharedFlow with replay = 0 discards the event completely. Conversely, a Channel buffers the message, delivering it reliably as soon as the UI enters onStart and resumes collection.""",
    "deep_senior_en": """Under the hood in kotlinx.coroutines, Channel implements the SendChannel and ReceiveChannel interfaces, backed by low-level lock-free queues managing sender and receiver continuations. When send is invoked without an active receiver, the item sits in the channel buffer array. When receive or receiveAsFlow is invoked, the first waiting receiver extracts the element and dequeues it permanently.
Conversely, SharedFlow manages an array of SharedFlowSlots. When emit is invoked, it iterates through all registered slots, incrementing their read head pointers. If the slot array is empty (zero subscribers), the emit operation immediately returns. Unless replay is positive or extraBufferCapacity is configured with an uncollected buffer, the emission evaporates completely without trace.
However, Channel introduces its own architectural caveat: Single Consumer Queue semantics. If a developer uses receiveAsFlow() and collects it in two different Composables or Fragments, the collectors race to dequeue emissions. Collector A consumes event 1, and Collector B consumes event 2, resulting in split-brain event processing where neither UI screen observes the complete sequence.
During Android configuration changes, a buffered Channel safely queues one-shot navigation events while the Activity recreates, delivering the pending intent immediately upon reconnection without duplicating events across screen rotations.
Staff engineers apply strict architectural boundaries: Channel is reserved strictly for private 1:1 one-off UI events (like single-destination navigation), while SharedFlow is used strictly for 1:N multi-subscriber broadcasts with deliberate replay caching.""",
    "meta_ar": {
        "id": "FLO-20",
        "questionAr": "قارن بين Channel و SharedFlow من حيث فقدان الأحداث وضمانات التسليم",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- الفهم المعماري للفرق بين طابور التوزيع الفردي (Unicast) والبث العام (Multicast).\n- إدراك مشكلة فقدان الأحداث (Event Loss) في SharedFlow عند غياب المشتركين في onStop.\n- معرفة مأزق تنافس المستهلكين (Split-Brain / Competitive Consumption) في Channel.",
        "why_it_matters_ar": "استخدام `SharedFlow` لإرسال حدث التنقل لشاشة الدفع أثناء توقف التطبيق المؤقت يسقط الحدث تماماً ويجعل التطبيق معلقاً، بينما جمع `Channel` في شاشتين مختلفتين يقسم الأحداث بينهما عشوائياً ويخلق كوارث في تتبع حالة المستخدم.",
        "worked_example_ar": "مقارنة عملية بين طابور الأحداث الفردية وبث التحديثات العامة:\n```kotlin\nclass CartViewModel : ViewModel() {\n    // 1. Channel: طابور مضمون لحدث الانتقال (مستحيل يضيع في الخلفية)\n    private val _navChannel = Channel<NavTarget>(Channel.BUFFERED)\n    val navEvents = _navChannel.receiveAsFlow()\n\n    // 2. SharedFlow: بث تحديث السلة لكل الشاشات المفتوحة بالتوازي\n    private val _cartUpdates = MutableSharedFlow<CartUpdate>()\n    val cartUpdates = _cartUpdates.asSharedFlow()\n\n    fun checkout() {\n        viewModelScope.launch {\n            _navChannel.send(NavTarget.Checkout) // محفوظ في الـ Buffer لو الشاشة مغلقة\n            _cartUpdates.emit(CartUpdate.Cleared) // يوزع على الشاشات النشطة فقط\n        }\n    }\n}\n```",
        "trade_offs_ar": "`Channel` يضمن وصول الحدث لمستهلك واحد حتى بعد فترات التوقف، ولكنه يفشل لو أردت إرسال الحدث لعدة شاشات في نفس الوقت. `SharedFlow` يبث لجميع الشاشات بامتياز، ولكنه يسقط الأحداث لو لم يكن هناك مستمع نشط لحظة الانبعاث.",
        "failure_modes_ar": "استخدام `SharedFlow(replay = 0)` لإرسال نتائج العمليات الحساسة، حيث تضيع في الهواء إذا حدثت أثناء تدوير الشاشة أو وضع التطبيق في الخلفية. خطأ آخر هو قراءة `Channel` في شاشتين في نفس الوقت مما يؤدي لاقتسام الأحداث عشوائياً.",
        "production_perspective_ar": "في المشروعات الكبرى، القاعدة واضحة: أحداث الملاحة والعمليات الفردية (One-shot Actions) تمر عبر `Channel` مغلق ومكشوف كـ Flow لشاشة واحدة فقط، بينما أحداث البث العام (مثل تسجيل الخروج وتغيير السمة) تبث عبر `SharedFlow` متعدد المشتركين.",
        "how_to_answer_ar": "- **Channel:** طابور فردي (Unicast)؛ كل رسالة تذهب لمستهلك واحد فقط، ويخزن البيانات في الـ Buffer لو لم يوجد مستهلك لحظتها (مفيش فقدان أحداث).\n- **SharedFlow:** بث عام (Multicast)؛ كل رسالة توزع بالتوازي على كل المشتركين النشطين، ولكن لو مفيش مشترك لحظة الإرسال، الحدث يضيع تماماً.\n- **خطر SharedFlow في أندرويد:** ضياع أحداث التنقل أثناء توقف الشاشة في onStop لو replay = 0.\n- **خطر Channel:** لو جمعه كلاسين، يتنافسان على الأحداث وكل كلاس يأخذ جزءاً عشوائياً.\n- **التوجيه الهندسي:** Channel لأحداث الشاشة الفردية (Navigation)، و SharedFlow للبث المتعدد (Event Bus).",
        "talking_points_ar": "ناقش Lock-free queues في Channel، ومصفوفة SharedFlowSlot في SharedFlow، وكيف يتصرف receiveAsFlow مع عدة جامعين.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لو قمت بجمع `channel.receiveAsFlow()` في شاشتين مختلفتين بالتوازي؟\"\n  **المرشح:** \"هيحصل تنافس بين الشاشتين (Competitive Consumption)؛ الشاشة الأولى هتسحب الحدث رقم 1، والشاشة التانية هتسحب الحدث رقم 2، ومفيش شاشة فيهم هتشوف كل الأحداث كاملة! علشان كده الـ Channel لازم يجمعه مستهلك واحد فقط.\"\n\n- **المحاور:** \"كيف تمنع SharedFlow من إسقاط أحداث الملاحة أثناء دوران الشاشة؟\"\n  **المرشح:** \"الحل المعماري هو عدم استخدام SharedFlow لأحداث الملاحة واستبداله بـ Channel، أو ضبط `replay = 1` مع ضرورة مسح الحدث بعد استهلاكه لتفادي تكراره، لكن الحل الأنظف هو الـ Channel لأنه مصمم أصلاً كطابور استهلاك فردي.\"",
        "self_check_ar": "هل فرقت بين Unicast و Multicast؟ هل شرحت أسباب فقدان الأحداث في SharedFlow؟ وهل حذرت من تنافس قراءة الـ Channel؟",
        "references_ar": f"- [Kotlin Channels official guide](https://kotlinlang.org/docs/channels.html) — توثيق قنوات كوتلن الرسمية.\n- [SharedFlow vs Channels in Android](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) — دليل أندرويد لاختيار التدفق المناسب.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ `Channel` هو طابور فردي (Unicast) الرسالة فيه بتروح لمستهلك واحد فقط وبيحفظها في الذاكرة ومبتضيعش حتى لو الشاشة مقفولة. أما الـ `SharedFlow` فده بث إذاعي (Multicast) بيبعت الرسالة لكل الشاشات المفتوحة مع بعض، لكن عيبه إن الرسالة بتضيع في الهواء لو انبعثت ومفيش مستمع نشط لحظتها.",
        "best_answer_ar": "الفارق الجوهري بين `Channel` و `SharedFlow` بيتمحور حول طوبولوجيا التوزيع (Topology) وضمانات تسليم الرسائل.\n\nالـ `Channel` متصمم كطابور تواصل فردي بنظام (Unicast)؛ يعني العنصر اللي بتبعته بيوصل لمستهلك واحد فقط، والميزة الكبرى فيه إنه بيحتفظ بالرسالة في الـ Buffer الداخلي لو مفيش مستهلك جاهز لحظتها. فلو بعت حدث انتقال لشاشة جديدة أثناء ما المستخدم كان بيعمل تدوير للشاشة والتطبيق في `onStop`، الرسالة هتفضل مستنية في الطابور وأول ما الشاشة ترجع في `onStart` هتستلمها فوراً بدون أي فقدان.\n\nفي المقابل، الـ `SharedFlow` شغال بنمط البث العام (Multicast Pub-Sub)؛ يعني الانبعاث الواحد بيتوزع بالتوازي على كل المشتركين المسجلين في نفس اللحظة، وده ممتاز لما تحب تبلغ 3 شاشات مفتوحة في نفس الوقت إن المستخدم سجل خروج مثلاً.\n\nلكن العيب القاتل في SharedFlow هو فقدان الأحداث (Event Loss)؛ لو بعت حدث والمشتركين كانوا مفصولين في الـ Background والـ replay كان بصفر، الحدث هيتبخر تماماً في الهواء ومحدش هيستلمه. ومن الناحية التانية، عيب الـ Channel إنه مينفعش يشترك فيه أكتر من شاشة؛ لأنهم هيتنافسوا على الطابور وكل شاشة هتاخد نص الأحداث وتسيب الباقي.",
        "deep_answer_ar": "على مستوى الـ Concurrency Internals في مكتبة كوتلن، الـ `Channel` مبني فوق هياكل بيانات Lock-free Queue بتدير طوابير منفصلة للـ Senders والـ Receivers. لما بتستدعي `channel.send(event)`، لو مفيش كائن `receive` نشط ومستني، العنصر بيتخزن في مصفوفة الـ Buffer. ولما الواجهة تستدعي `receiveAsFlow().collect { }`، المشترك بيسحب العنصر ويفضي مكانه من الذاكرة فوراً (FIFO Dequeue).\n\nأما الـ `SharedFlow`، فهو بيدير مصفوفة من كائنات `SharedFlowSlot`. لما بتنادي `emit(value)`، هو بيلف على المشتركين المسجلين حالياً فقط ويحرك مؤشرات القراءة بتاعتهم. لو مصفوفة المشتركين كانت فاضية، دالة `emit` بتنتهي في جزء من المايكروثانية بدون أي تخزين لو كان الـ replay بصفر والـ buffer فاضي، وده السبب الحقيقي في ضياع أحداث التنقل أثناء فترات خمول الواجهة.\n\nلكن لازم ننتبه لمأزق هندسي خطير جداً في الـ Channel اسمه التنافس على الاستهلاك (Competitive Consumption)؛ لو عندك شاشتين أو كلاسين عملوا `collect` لنفس الـ `receiveAsFlow()`، الـ Channel مش هيعمل Multicast، هو هيسلم أول حدث للشاشة (أ) وتاني حدث للشاشة (ب) وثالث حدث للشاشة (أ)، وده بيخلق حالة Split-Brain وانقسام في بيانات التطبيق.\n\nعلشان كده في بيئات الإنتاج، بنتبع قاعدة معمارية صارمة: الـ Channels مخصصة للأحداث الفردية الحتمية زي الـ Navigation والـ One-off Actions بشرط وجود جامع وحيد، والـ SharedFlow مخصص للبث الجماعي المتعدد للشاشات المستقلة مع ضبط دقيق للـ Buffers."
    }
}

# ==========================================
# FLO-21: callbackFlow and awaitClose
# ==========================================
DATA["FLO-21"] = {
    "concept_en": """The callbackFlow builder bridges legacy, callback-driven asynchronous APIs—such as Android LocationManager, Firebase listeners, broadcast receivers, and sensor hardware—into idiomatic, cold Kotlin Flows.
Unlike the standard flow { } builder, which operates sequentially and throws an IllegalStateException if emissions occur from external threads, callbackFlow is thread-safe and channel-backed, allowing asynchronous callbacks executed by the OS or thread pools to push emissions safely via trySend or send.
The awaitClose lambda is mandatory in callbackFlow. It suspends the internal producer coroutine, keeping the channel open while collectors are listening. When downstream collection terminates—whether due to normal completion, explicit cancellation, or lifecycle disposal—awaitClose resumes immediately, executing the specified teardown block to unregister listeners, release hardware handles, and prevent catastrophic memory and battery leaks.""",
    "walkthrough_en": """Wrapping an Android LocationListener into a leak-free callbackFlow:
```kotlin
class LocationDataSource(private val locationManager: LocationManager) {
    fun observeLocationUpdates(): Flow<Location> = callbackFlow {
        val listener = object : LocationListener {
            override fun onLocationChanged(location: Location) {
                // Thread-safe emission from OS callback thread:
                trySend(location).isSuccess
            }
            override fun onProviderDisabled(provider: String) {}
            override fun onProviderEnabled(provider: String) {}
        }

        // Register listener with system service on the calling thread:
        locationManager.requestLocationUpdates(
            LocationManager.GPS_PROVIDER,
            1000L,
            1f,
            listener
        )

        // MANDATORY: Keeps flow alive and cleans up when cancelled
        awaitClose {
            println("Collector cancelled: Unregistering GPS listener")
            locationManager.removeUpdates(listener) // Releases hardware!
        }
    }
}
```""",
    "short_en": """callbackFlow converts multi-shot callback APIs into cold Flows using an internal channel. awaitClose is mandatory: it keeps the producer coroutine suspended while active, and executes cleanup logic to unregister listeners and release hardware resources when the flow is cancelled.""",
    "structured_en": """To begin with, callbackFlow is the primary bridge for wrapping multi-shot asynchronous callbacks into reactive Kotlin streams.
From an architectural standpoint, standard flow builders cannot emit across foreign threads. Because Android system callbacks (like GPS updates, WebSocket frames, or Bluetooth beacons) fire asynchronously from arbitrary background threads, callbackFlow provides a thread-safe Channel buffer that accepts trySend invocations across thread boundaries.
In production scenarios, omitting cleanup in callback-based architectures causes devastating memory leaks and battery depletion. When an Activity detaches, the GPS listener must be removed immediately to power down the location hardware.
As for boundary management, awaitClose is strictly enforced at runtime. It suspends the producer coroutine, preventing immediate flow completion, and guarantees that when the collecting scope cancels, the registered teardown block unbinds listeners and frees native resources cleanly.""",
    "deep_senior_en": """Under the hood in kotlinx.coroutines.flow, callbackFlow extends ChannelFlow, backed by an internal Channel buffer. When collect is invoked, callbackFlow launches a producer coroutine executing within a ProducerScope.
Because ProducerScope implements SendChannel, emissions execute via trySend(element) or send(element). In callback contexts, trySend is heavily preferred over suspending send, because asynchronous system callbacks (such as LocationListener.onLocationChanged) are synchronous void callbacks that cannot suspend. If trySend fails due to buffer saturation, engineers configure buffer(Channel.CONFLATED) or explicit buffer capacities to prevent dropped events.
The awaitClose invocation is governed by runtime enforcement: if the builder block completes without invoking awaitClose, callbackFlow throws an IllegalStateException: "awaitClose() should be used at the end of callbackFlow to keep the flow open and clean up resources".
Internally, awaitClose registers a completion handler on the producer coroutine's Job. When the downstream collector's scope terminates or cancels, the Job enters the cancelling state, un-suspending awaitClose and executing its lambda on the underlying context. This guarantees atomic teardown even during sudden unhandled collector failures or rapid Activity recreations.
Omitting awaitClose or failing to unregister listeners leaves native hardware interrupts and operating system hooks active, causing severe battery drain and holding application contexts in memory permanently.
Staff engineers mandate strict pairing: every callback registration inside callbackFlow must have its exact inverse unregistration call inside awaitClose, preventing persistent leaks of Activity contexts and hardware locks.""",
    "meta_ar": {
        "id": "FLO-21",
        "questionAr": "ما هو callbackFlow؟ وما الوظيفة الإلزامية لدالة awaitClose؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- فهم كيفية تحويل الـ Callbacks القديمة وحساسات النظام إلى Flow حديث.\n- إدراك سبب فشل flow العادي مع الـ Callbacks متعددة الخيوط واستخدام trySend.\n- استيعاب الوظيفة الحيوية لـ awaitClose في منع إغلاق التدفق فوراً وتنظيف الموارد عند الإلغاء.",
        "why_it_matters_ar": "نسيان `awaitClose` أو عدم إلغاء تسجيل الـ Listeners داخلها يبقي حساسات الـ GPS والـ Bluetooth ومستمعات الـ Firebase نشطة في الخلفية حتى بعد غلق التطبيق، مما يسرب الذاكرة ويفرغ بطارية المستخدم في وقت قياسي.",
        "worked_example_ar": "تحويل مستشعر الموقع الجغرافي لتدفق آمن بدون تسريب:\n```kotlin\nfun observeLocation(mgr: LocationManager): Flow<Location> = callbackFlow {\n    val listener = LocationListener { location ->\n        trySend(location) // إرسال آمن من خيط النظام غير المعلق\n    }\n    mgr.requestLocationUpdates(LocationManager.GPS_PROVIDER, 1000L, 10f, listener)\n\n    // إلزامي: تعليق التدفق وتنظيف الحساس فور إلغاء التجميع:\n    awaitClose {\n        mgr.removeUpdates(listener) // غلق عتاد الـ GPS وتوفير البطارية\n    }\n}\n```",
        "trade_offs_ar": "`callbackFlow` يوفر أماناً نوعياً وتكاملاً سلساً مع الكوروتينات، ولكنه يعتمد على قناة داخلية (Channel) تتطلب إدارة واعية للـ Backpressure عبر trySend واختيار سعة الـ Buffer المناسبة.",
        "failure_modes_ar": "نسيان استدعاء `awaitClose` مما يسبب كراش فوري `IllegalStateException` عند تشغيل الكود. خطأ آخر هو استخدام `send(x)` المعلقة داخل كول باك عادي غير معلق مما يمنع تمرير البيانات لو كان الطابور ممتلئاً.",
        "production_perspective_ar": "في المشروعات الاحترافية، نغلف جميع حساسات النظام (GPS, Sensors, ConnectivityManager) بـ `callbackFlow` مع مراجعة دقيقة لكتلة `awaitClose` للتأكد من إلغاء تسجيل الـ Callbacks لمنع تسريب الـ Context ومطابقة معايير ترشيد البطارية.",
        "how_to_answer_ar": "- **ما هو callbackFlow:** باني تدفقات مصمم خصيصاً لتحويل الـ Callbacks متعددة الانبعاثات إلى Flow آمن وخيطياً.\n- **لماذا لا نستخدم flow العادي:** لأن flow العادي يتطلب emit من نفس الخيط المتزامن، بينما Callbacks النظام تأتي من خيوط عشوائية.\n- **دور awaitClose الأول:** تعليق الكوروتين وإبقاء التدفق مفتوحاً؛ بدونها ينتهي البلوك فوراً ويغلق التدفق قبل وصول أي Callback.\n- **دور awaitClose الثاني:** تنظيف الموارد وإلغاء تسجيل الـ Listener فور إلغاء المشترك للتدفق.\n- **طريقة الإرسال:** استخدام `trySend(x)` لأن دوال الكول باك في أندرويد دوال عادية وليست suspend.",
        "talking_points_ar": "ناقش كلاس ProducerScope في كوتلن، ولماذا يرمي المترجم IllegalStateException بدون awaitClose، وكيف يتعامل trySend مع كائن ChannelResult.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لو نسيت كتابة awaitClose داخل callbackFlow؟\"\n  **المرشح:** \"أول ما تشغل الكود، الكوروتين هترمي استثناء فوري `IllegalStateException: awaitClose() should be used at the end of callbackFlow`. كوتلن بتفرضها برمجياً لأن من غيرها البلوك هيوصل لآخره ويقفل التدفق في نفس اللحظة قبل ما أي كول باك يلحق يبعت داتا!\"\n\n- **المحاور:** \"لماذا نستخدم trySend بدلاً من send داخل كول باك النظام؟\"\n  **المرشح:** \"لأن دوال الـ Callbacks بتاعة نظام أندرويد (زي LocationListener) هي دوال عادية مش suspend ومتقدرش تعلق الكود. فدالة `trySend` متزامنة وبترجع كائن `ChannelResult` فوري يوضح هل العنصر دخل الـ Buffer بنجاح ولا الطابور ممتلئ.\"",
        "self_check_ar": "هل شرحت سبب الحاجة لـ callbackFlow بدلاً من flow العادي؟ هل بينت الوظيفتين الأساسيتين لـ awaitClose؟ وهل وضحت استخدام trySend؟",
        "references_ar": f"- [callbackFlow official documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/callback-flow.html) — توثيق كوتلن الرسمي لـ callbackFlow.\n- [A safer way to collect callbacks in Android](https://medium.com/androiddevelopers/a-safer-way-to-collect-gestures-and-events-in-android-4a34b2230a10) — مقال فريق أندرويد الرسمي.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "`callbackFlow` هو باني تدفقات بيحول الـ Callbacks القديمة لحساسات النظام لـ Flow حديث وآمن. ودالة `awaitClose` إلزامية؛ وظيفتها الأولى إنها تعلق الكوروتين وتخلي التدفق شغال وميقفلش فوراً، ووظيفتها التانية إنها تلغي تسجيل الـ Listener وتنظف الموارد فور خروج المستخدم لمنع تسريب الميموري والبطارية.",
        "best_answer_ar": "مشغل `callbackFlow` هو الجسر المعماري الرسمي في كوتلن لتحويل أي مكتبة قديمة شغالة بالـ Callbacks المتكررة إلى Cold Flow حديث ومتوافق مع الكوروتينات.\n\nلو حاولت تستخدم باني `flow { }` العادي مع كول باك زي مراقبة الـ GPS أو حساسات الحركة، التطبيق هيعمل كراش؛ لأن كول باكات النظام بتشتغل على خيوط تانية من الـ OS وكوتلن بتمنع الـ emit عبر خيوط خارجية. `callbackFlow` بيحل المشكلة دي لأنه مبني على قناة داخلية خيطياً (Thread-safe Channel) بتسمح باستدعاء دالة `trySend` من أي خيط بأمان.\n\nأما دالة `awaitClose` فدي دالة إلزامية وحتمية ولازم تتكتب في آخر البلوك، وليها وظيفتين جوهريتين:\nالوظيفة الأولى إنها بتعلق الكوروتين في مكانها وتخلي التدفق مفتوح؛ لأن من غيرها الكود هيخلص السطر الأخير ويقفل التدفق فوراً قبل ما الحساس يبعت أي إحداثيات.\nوالوظيفة التانية هي تنظيف الموارد (Cleanup)؛ أول ما الشاشة تتقفل والمشترك يلغي التجميع، كود الـ `awaitClose` بيتفكك فوراً وينفذ عملية `removeUpdates` لإلغاء تسجيل الـ Listener وغلق حساس الـ GPS وتوفير البطارية تماماً.",
        "deep_answer_ar": "تحت الكابوت في `kotlinx.coroutines.flow`، كلاس `callbackFlow` بيورث من `ChannelFlow` وبيشغل مسار التنفيذ داخل نطاق كلاس اسمه `ProducerScope`. النطاق ده بيطبق واجهة `SendChannel`، وده بيفسر ليه بنقدر ننادي `trySend(value)` مباشرة.\n\nفي كول باكات أندرويد، استدعاء `send(value)` المعلقة مستحيل في أغلب الأحيان؛ لأن دوال زي `onLocationChanged` هي دوال Java عادية لا تقبل التعليق (Non-suspending void methods). استخدام `trySend` بيحاول يضع العنصر في الـ Buffer فوراً وبيرجع كائن `ChannelResult` بيفيد بالنجاح أو الامتلاء، وبنقدر ندمجه مع `buffer(Channel.CONFLATED)` لو بنتعامل مع حساسات سريعة جداً علشان ميسقطش داتا.\n\nالأهمية القصوى لـ `awaitClose` بتظهر في فحص الـ Runtime؛ لو المطور نسي يكتبها، الكود بيرمي `IllegalStateException` فوري. داخلياً، الدالة دي بتسجل `invokeOnCompletion` على الـ Job بتاع الكوروتين الحاضنة وتعلق نفسها بتعليق تعاوني.\n\nأول ما المستهلك في الواجهة يدمر الشاشة وتتلغي الكوروتين في `repeatOnLifecycle`، بيتبعت إشعار إلغاء للكوروتين المنتجة. الإلغاء ده بيصحي دالة `awaitClose` فوراً وينفذ الـ Lambda اللي جواها على نفس السياق، فتقدر تستدعي دوال الـ Unregistering وتفكك قيود الـ WakeLocks والمقابس بدون أي احتمالية لتسريب الذاكرة (Memory Leaks).\n\nعلشان كده في بيئات الإنتاج، بنراجع كود `callbackFlow` بصرامة للتأكد من إن أي `registerListener` مكتوبة فوق ليها ما يقابلها حرفياً كـ `unregisterListener` جوه `awaitClose` لضمان استقرار التطبيق."
    }
}

# ==========================================
# FLO-22: repeatOnLifecycle vs collectAsStateWithLifecycle
# ==========================================
DATA["FLO-22"] = {
    "concept_en": """The repeatOnLifecycle and collectAsStateWithLifecycle APIs represent modern Android's official, lifecycle-aware flow collection mechanisms designed to eliminate background execution waste and UI crashes.
repeatOnLifecycle is a suspending extension on LifecycleOwner (or Lifecycle) used primarily in imperative View-based architectures or coroutine launch blocks. It restarts a new coroutine executing the provided block whenever the lifecycle reaches a target state (typically Lifecycle.State.STARTED), and actively cancels that coroutine when the lifecycle drops below that state (e.g., entering STOPPED when the app is backgrounded).
collectAsStateWithLifecycle is a specialized Jetpack Compose Composable operator that wraps repeatOnLifecycle under the hood. It collects emissions from a Flow in a lifecycle-aware manner, converting the latest value into a Compose State<T> snapshot, and automatically halts collection when the hosting Composable's lifecycle drops below the specified minimum active state.""",
    "walkthrough_en": """Applying lifecycle-aware collection in Views and Jetpack Compose:
```kotlin
// 1. In Views (Fragments / Activities) using repeatOnLifecycle:
class UserProfileFragment : Fragment(R.layout.fragment_profile) {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            // Suspends when view is destroyed; restarts on STARTED, cancels on STOPPED:
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.profileState.collect { state ->
                    updateProfileViews(state)
                }
            }
        }
    }
}

// 2. In Jetpack Compose using collectAsStateWithLifecycle:
@Composable
fun UserProfileScreen(viewModel: ProfileViewModel) {
    // Automatically pauses collection when app is in background:
    val uiState by viewModel.profileState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is ProfileUiState.Loading -> FullScreenSpinner()
        is ProfileUiState.Success -> ProfileContent(state.user)
    }
}
```""",
    "short_en": """repeatOnLifecycle executes and cancels a coroutine block as the lifecycle enters and leaves a target state, ideal for Views; collectAsStateWithLifecycle is its Compose equivalent, collecting a Flow into a Compose State while automatically pausing collection when the app backgrounds.""",
    "structured_en": """To begin with, these APIs guarantee that UI components collect data streams strictly while the user is actively viewing the screen.
From an architectural standpoint, standard coroutine collection using lifecycleScope.launch continues collecting even when the app is in the background, wasting CPU cycles and network data. repeatOnLifecycle solves this by launching collection at Lifecycle.State.STARTED and cancelling the coroutine when the UI enters STOPPED.
In production scenarios, Jetpack Compose applications originally used collectAsState(), which observes flows throughout composition existence without pausing when the screen is placed in the background. Google introduced collectAsStateWithLifecycle to bridge this gap, ensuring that Compose applications pause flow consumption during backgrounding.
As for boundary management, pairing WhileSubscribed(5000) on ViewModels with collectAsStateWithLifecycle or repeatOnLifecycle ensures that upstream subscription counts drop to zero in the background, shutting down hardware sensors and database queries cleanly.""",
    "deep_senior_en": """Under the hood in androidx.lifecycle, repeatOnLifecycle creates a custom LifecycleObserver. When the target state (e.g., STARTED) is entered via onStart, the observer launches a new child coroutine in the parent scope, executing the user's suspended block. When the lifecycle drops to STOPPED via onStop, the observer explicitly cancels the launched child coroutine by throwing a CancellationException.
If the Activity returns to the foreground later, onStart fires again, and repeatOnLifecycle launches an entirely fresh coroutine, resubscribing to the Flow from scratch. This periodic restart is what decrements StateFlow's subscriptionCount to zero when combined with SharingStarted.WhileSubscribed(5000), cleanly terminating upstream database queries and network sockets after the five-second grace period.
The Compose extension collectAsStateWithLifecycle wraps this exact pattern: it integrates remember(flow, lifecycle, minActiveState) and produces a State<T> backed by produceState. Whenever the Composable transitions to the background, produceState stops flow collection, preventing redundant recompositions and memory retention.
A critical architectural pitfall in legacy code was using lifecycleScope.launchWhenStarted. Google officially deprecated launchWhenStarted because it merely suspended the coroutine instead of cancelling it; keeping collectors suspended in the background held resources open and prevented upstream flows from shutting down.
Staff engineers mandate collectAsStateWithLifecycle across all Compose screens to guarantee zero background CPU waste and maximum battery efficiency.""",
    "meta_ar": {
        "id": "FLO-22",
        "questionAr": "قارن بين repeatOnLifecycle و collectAsStateWithLifecycle في أندرويد",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- الفهم العميق لإدارة دورة حياة جمع التدفقات في أندرويد الحديث.\n- معرفة سبب إلغاء جوجل لدوال launchWhenStarted القديمة واستبدالها بـ repeatOnLifecycle.\n- إدراك الفرق بين collectAsState العادي و collectAsStateWithLifecycle في Jetpack Compose.",
        "why_it_matters_ar": "جمع التدفقات في الخلفية بدون مراعاة الـ Lifecycle يهدر بطارية الجهاز ويستنزف باقة الإنترنت بمواصلة استقبال بيانات لا يراها أحد، وقد يتسبب في كراشات واجهة شائعة مثل محاولة تحديث View غير موجود في الذاكرة.",
        "worked_example_ar": "الجمع الآمن لدورة الحياة في الـ Views وفي الـ Compose:\n```kotlin\n// في الـ Views (Fragments):\nviewLifecycleOwner.lifecycleScope.launch {\n    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {\n        viewModel.uiState.collect { updateUi(it) } // يلغى في onStop ويبدأ في onStart\n    }\n}\n\n// في Jetpack Compose:\n@Composable\nfun HomeScreen(viewModel: HomeViewModel) {\n    // يوقف التجميع في الخلفية تلقائياً:\n    val state by viewModel.uiState.collectAsStateWithLifecycle()\n    Text(text = state.title)\n}\n```",
        "trade_offs_ar": "هذه الأدوات تلغي وتعيد تشغيل الكوروتين مع كل خروج ودخول للشاشة، مما يفرض تصميم تدفقات تتحمل إعادة الاشتراك بدون تكرار طلبات ثقيلة (عبر StateFlow أو WhileSubscribed).",
        "failure_modes_ar": "استخدام `collectAsState()` العادي في Compose مما يبقي التدفق نشطاً في الخلفية للأبد. خطأ آخر هو استخدام `launchWhenStarted` الملغاة رسمياً، والتي كانت تعلق الكود بدلاً من إلغائه فتبقي اتصالات الشبكة مفتوحة.",
        "production_perspective_ar": "في تطبيقات Compose الإنتاجية، نضع قاعدة Lint تمنع استخدام `collectAsState()` وتفرض `collectAsStateWithLifecycle()`، لضمان هبوط عداد المشتركين إلى الصفر وتوفير بطارية المستخدم عند تصغير التطبيق.",
        "how_to_answer_ar": "- **الوظيفة المشتركة:** جمع التدفقات فقط عندما تكون الشاشة مرئية ونشطة للمستخدم، وإيقاف التجميع تماماً في الخلفية.\n- **repeatOnLifecycle:** دالة معلقة مخصصة للـ Views/Fragments؛ تشغل الكوروتين عند الوصول لحالة معينة (زي STARTED) وتلغيها تماماً عند الخروج منها (onStop).\n- **collectAsStateWithLifecycle:** معامل خاص بـ Jetpack Compose يغلف repeatOnLifecycle داخلياً ويحول الـ Flow إلى Compose State آمنة.\n- **لماذا ألغيت launchWhenStarted:** لأنها كانت تعلق الكوروتين فقط ولا تلغيها، فكانت تبقي الاتصالات والمصادر معلقة في الخلفية.\n- **التكامل مع WhileSubscribed:** هذا الإلغاء هو الذي يجعل عداد المشتركين ينزل لصفر ويوقف المصدر في الخلفية.",
        "talking_points_ar": "ناقش LifecycleObserver الداخلي في repeatOnLifecycle، والفرق المعماري بين تعليق الكوروتين وإلغائها التام، وتكامل produceState في Compose.",
        "follow_ups_ar": "- **المحاور:** \"لماذا حذرت جوجل من استخدام launchWhenStarted واستبدلتها بـ repeatOnLifecycle؟\"\n  **المرشح:** \"لأن `launchWhenStarted` كانت بتعمل Suspend للكوروتين في الخلفية ومش بتلغيها؛ وده معناه إن الـ Emitter العلوي بيفضل شغال والـ Flow بيفضل متصل بالشبكة والداتابيز وتفضل البطارية بتستنزف. أما `repeatOnLifecycle` فبتلغي الكوروتين تماماً في onStop بـ CancellationException، وده بيسمح لـ WhileSubscribed إنه يوقف المصدر العلوي ويوفر البطارية.\"\n\n- **المحاور:** \"ما هو الخطر في استخدام `collectAsState()` العادية في شاشات Compose؟\"\n  **المرشح:** \"معامل `collectAsState()` العادي ملوش علاقة بدورة حياة الـ Lifecycle؛ بيفضل يجمع الداتا طالما الـ Composable في الذاكرة حتى لو التطبيق نزل في الـ Background، وده بيهدر موارد الموبايل. الحل هو استخدام `collectAsStateWithLifecycle()` علشان يفصل التجميع في الخلفية فوراً.\"",
        "self_check_ar": "هل فرقت بين استخدام Views واستخدام Compose؟ هل شرحت سر إلغاء launchWhenStarted؟ وهل بينت التكامل مع WhileSubscribed؟",
        "references_ar": f"- [repeatOnLifecycle official guide](https://developer.android.com/topic/architecture/ui-layer/lifecycle-aware) — دليل جوجل الرسمي لجمع التدفقات مع دورة الحياة.\n- [Consuming flows safely in Jetpack Compose](https://medium.com/androiddevelopers/consuming-flows-safely-in-jetpack-compose-cde01474d380) — مقال فريق أندرويد لـ collectAsStateWithLifecycle.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "`repeatOnLifecycle` بتشغل كوروتين التجميع لما الشاشة تدخل في حالة نشطة زي `STARTED` وبتلغيها تماماً أول ما الشاشة تروح في الخلفية في `STOPPED` وده المعتمد في الـ Views. أما `collectAsStateWithLifecycle` فدي النسخة المخصصة لـ Jetpack Compose اللي بتعمل نفس الحركة وتوقف التجميع في الخلفية لتوفير البطارية.",
        "best_answer_ar": "الأداتين دول بيمثلوا المعيار الرسمي والحديث من جوجل لجمع تدفقات البيانات بطريقة واعية تماماً بدورة حياة الشاشة (Lifecycle-aware).\n\nالمشكلة القديمة كانت إن المطورين بيستخدموا `lifecycleScope.launch`؛ وده كان بيخلي التجميع يفضل شغال حتى لو المستخدم خرج من التطبيق وراح يتصفح تطبيق تاني، وده كان بيهدر باقة الإنترنت وطاقة البطارية على شاشة محدش شايفها.\n\nدالة `repeatOnLifecycle` حلت الكارثة دي في شاشات الـ Views؛ بتحدد لها حالة زي `STARTED`، أول ما الشاشة تفتح وتشترك بتبدأ كود التجميع، وأول ما تدخل في `onStop` بتلغي الكوروتين تماماً بـ `CancellationException` وتفكك الموارد، ولما المستخدم يرجع للتطبيق بتشغل كوروتين جديدة من الصفر.\n\nأما في Jetpack Compose، فجوجل قدمت لنا `collectAsStateWithLifecycle()`؛ وهي تحت الكابوت بتغلف نفس منطق `repeatOnLifecycle` تماماً، وبتحول الـ Flow لـ Compose State بيتوقف عن استقبال البيانات وتحديث الذاكرة فوراً لو التطبيق نزل في الـ Background، وده بيحمي فريمات الجهاز ويوفر البطارية بنسبة 100%.",
        "deep_answer_ar": "على مستوى الـ Lifecycle Architecture في مكتبة AndroidX، دالة `repeatOnLifecycle` بتسجل كائن `LifecycleEventObserver` داخل الـ LifecycleOwner. لما يوصل حدث `ON_START`، المراقب ده بيفتح كوروتين فرعية مخصصة تنفذ الـ Lambda بتاعة الـ Collect. ولما يوصل حدث `ON_STOP`، المراقب بينادي صراحة على `job.cancel()` للكوروتين دي.\n\nالإلغاء ده بيلعب دور محوري في معمارية التدفقات الحديثة؛ لأن لما الكوروتين تتلغي، اشتراك المشترك في الـ `StateFlow` بينتهي، فعداد المشتركين `subscriptionCount` بينزل للصفر. وهنا بيتدخل مشغل `SharingStarted.WhileSubscribed(5000)`، وبعد 5 ثوانٍ بيلغي استعلامات قاعدة بيانات Room ويفصل اتصال الـ WebSocket تماماً ويوفر العتاد.\n\nوده هو السبب اللي خلى جوجل تلغي رسمياً (Deprecate) دوال قديمة زي `launchWhenStarted` و `launchWhenResumed`؛ لأن الدوال القديمة كانت بتعمل مجرد `suspend` للكوروتين في الخلفية بدون إلغائها، فكان الـ Flow بيفضل متصل والـ Emitter بيفضل شغال ويستهلك البطارية بدون أي داعٍ.\n\nوفي Jetpack Compose، مشغل `collectAsStateWithLifecycle()` بيعتمد داخلياً على دالة `produceState` مع `repeatOnLifecycle(minActiveState)`. وده بيضمن إن الـ Composition Runtime ميعملش أي Recomposition أو يصحى من النوم طالما الشاشة مش معروضة أمام المستخدم.\n\nعلشان كده في بيئات الإنتاج، بنفرض قاعدة صارمة في الـ Code Review: ممنوع نهائياً استخدام `collectAsState()` العادي داخل أي Composable شغال مع تدفقات حية، ولازم استبداله بـ `collectAsStateWithLifecycle()` لضمان مطابقة معايير أداء أندرويد الحديثة."
    }
}

# ==========================================
# FLO-23: Indefinite UI collection without lifecycle
# ==========================================
DATA["FLO-23"] = {
    "concept_en": """Collecting asynchronous data streams indefinitely in Android UI layers without lifecycle awareness triggers severe architectural failure modes: chronic memory leaks, background battery exhaustion, wasted cellular bandwidth, and fatal UI state corruption.
When a collection coroutine is launched directly in a non-lifecycle scope—such as GlobalScope, an uncancelled custom CoroutineScope, or improperly using lifecycleScope.launch without repeatOnLifecycle—the collection loop continues executing indefinitely after the Activity, Fragment, or Composable transitions to the background.
If the underlying flow connects to persistent physical sources (such as hardware GPS providers, Bluetooth Low Energy scanners, camera frames, or long-lived WebSocket connections), the device hardware radios remain fully powered, draining mobile battery rapidly. Furthermore, collecting inside a backgrounded UI frame can trigger IllegalStateException crashes if the collector tries to mutate Fragment view hierarchies, commit FragmentTransactions, or show DialogFragments when the window state is already saved.""",
    "walkthrough_en": """Demonstrating the dangers of unmanaged collection versus lifecycle safety:
```kotlin
class DangerousFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ❌ CATASTROPHIC ANTI-PATTERN:
        // Continues collecting when app is backgrounded, leaking GPS hardware and battery!
        lifecycleScope.launch {
            locationRepository.observeGpsUpdates().collect { location ->
                // If this attempts Fragment transaction after onSaveInstanceState: CRASH!
                updateCoordinatesOnMap(location)
            }
        }

        // ✅ SAFE PRODUCTION PATTERN:
        // Cancels upstream collection when app is in background, frees GPS hardware:
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                locationRepository.observeGpsUpdates().collect { location ->
                    updateCoordinatesOnMap(location)
                }
            }
        }
    }
}
```""",
    "short_en": """Collecting a flow indefinitely without lifecycle awareness keeps background coroutines alive, causing severe memory leaks, battery exhaustion from active GPS or network sockets, wasted cellular data, and fatal IllegalStateException crashes when mutating UI state after onSaveInstanceState.""",
    "structured_en": """To begin with, collecting flows without lifecycle awareness is one of the most destructive architectural bugs in Android development.
From an architectural standpoint, an Android component's visual lifecycle is transient. Launching a raw collection loop that outlives screen visibility breaks the unidirectional data flow contract, maintaining active references to destroyed views and preventing garbage collection.
In production scenarios, the impact on device hardware is severe. If the collected flow wraps sensor listeners, location updates, or real-time WebSockets, background execution forces mobile CPUs and radio chipsets to remain powered, depleting user battery within hours and generating negative app store reviews.
As for boundary management, background UI mutations trigger runtime crashes. If a backgrounded collector receives an emission and attempts to display a DialogFragment or navigate via Jetpack Navigation after onSaveInstanceState has already executed, the Android framework throws a fatal IllegalStateException, terminating the application process.""",
    "deep_senior_en": """At the Android framework and operating system boundary level, collecting flows indefinitely violates OS memory and resource management principles.
When an Activity moves to the background, the framework invokes onStop and onSaveInstanceState. If a coroutine launched in lifecycleScope (without repeatOnLifecycle) continues collecting, its collector block holds direct or implicit references to the Fragment or Activity instance through closures. Because the coroutine Job remains active in the CoroutineContext, the garbage collector cannot reclaim the Activity, causing a significant retain cycle and OutOfMemoryError crashes under memory pressure.
Furthermore, if the stream is exposed via stateIn(viewModelScope, WhileSubscribed(5000)), the uncancelled background collector keeps subscriptionCount above zero perpetually. Consequently, WhileSubscribed never transitions to zero, preventing the upstream flow from tearing down its network connections or Room query observers. Active physical hardware sensors like GPS chips and BLE modems stay powered, rapidly exhausting battery reserves and violating Google Play Vitals battery guidelines.
Even worse are UI framework crashes: attempting to invoke FragmentManager.commit() or show dialogs from an asynchronous collector when the Fragment is in the STOPPED state triggers: "java.lang.IllegalStateException: Can not perform this action after onSaveInstanceState".
Staff engineers eliminate this via automated static analysis and strict guidelines: every UI collection in Views must be wrapped in viewLifecycleOwner.repeatOnLifecycle(STARTED), and every Compose collection must utilize collectAsStateWithLifecycle.""",
    "meta_ar": {
        "id": "FLO-23",
        "questionAr": "ماذا يحدث إذا جمعت واجهة المستخدم التدفق للأبد دون مراعاة دورة الحياة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- معرفة المخاطر الكارثية للتجميع غير المنضبط للتدفقات في أندرويد.\n- إدراك استنزاف البطارية وتسريب الذاكرة عند بقاء الحساسات ومقابس الشبكة مفتوحة في الخلفية.\n- فهم كراشات النظام الشهيرة مثل IllegalStateException عند تعديل الواجهة بعد onSaveInstanceState.",
        "why_it_matters_ar": "تجميع التدفق في الخلفية بدون دورة حياة قد يجعل التطبيق يستنزف بطارية الهاتف بالكامل في ساعات قليلة بسبب استمرار عمل الـ GPS، ويتسبب في مراجعات سلبية وتقييم نجمة واحدة على المتجر بسبب الكراشات المفاجئة أثناء وجود التطبيق في الخلفية.",
        "worked_example_ar": "الفرق بين التجميع الكارثي والتجميع المحمي بدورة الحياة:\n```kotlin\n// ❌ كارثة إنتاجية: يظل يجمع في الخلفية ويسرب الـ GPS والبطارية:\nlifecycleScope.launch {\n    locationFlow.collect { updateUi(it) }\n}\n\n// ✅ المعيار الهندسي السليم: يوقف التجميع ويفصل الحساس في الخلفية:\nviewLifecycleOwner.lifecycleScope.launch {\n    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {\n        locationFlow.collect { updateUi(it) }\n    }\n}\n```",
        "trade_offs_ar": "إدارة دورة الحياة بـ `repeatOnLifecycle` تتطلب كوداً إضافياً بسيطاً وإعادة اشتراك مع العودة للواجهة، ولكنها في المقابل تمنح التطبيق كفاءة طاقة قصوى واستقراراً بنسبة 100% ضد الكراشات.",
        "failure_modes_ar": "محاولة عرض DialogFragment أو عمل Commit لـ FragmentTransaction من داخل تجميع شغال في الخلفية بعد استدعاء `onSaveInstanceState`؛ مما يسبب كراش فوري `IllegalStateException: Can not perform this action after onSaveInstanceState`.",
        "production_perspective_ar": "في المشروعات الكبيرة، نراقب معدل استهلاك البطارية عبر Google Vitals و Firebase Performance. أي شاشة تجمع تدفقات في الخلفية بدون `repeatOnLifecycle` تُعتبر P0 Bug ويتم إصلاحها فوراً لضمان عدم حظر التطبيق من متجر Google Play بسبب سوء إدارة الطاقة.",
        "how_to_answer_ar": "- **استنزاف الموارد والبطارية:** بقاء اتصالات الشبكة، الـ WebSockets، وحساسات الـ GPS والـ Bluetooth تعمل بكامل طاقتها في الخلفية.\n- **تسريب الذاكرة (Memory Leaks):** تعليق الـ Activity أو الـ Fragment في الذاكرة ومنع الـ Garbage Collector من تنظيفها لو تم التجميع في Scope عام.\n- **كراشات حالة الواجهة:** حدوث كراش `IllegalStateException` لو حاول التجميع تعديل الواجهة أو فتح شاشة بعد `onSaveInstanceState`.\n- **إفشال ميزة WhileSubscribed:** بقاء المستمع نشطاً يجعل عداد `subscriptionCount` لا يصل للصفر أبداً، فيفشل الـ ViewModel في إيقاف التدفق العلوي.\n- **الحل الوقائي:** استخدام `repeatOnLifecycle(STARTED)` في الـ Views و `collectAsStateWithLifecycle` في Compose.",
        "talking_points_ar": "ناقش ظاهرة Retain Cycles في الـ Heap، وكيف تؤثر على تقييمات Google Vitals، وميكانيزم حماية حالة النظام بعد onSaveInstanceState.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يحدث كراش IllegalStateException لو استلمت داتا في الـ Background؟\"\n  **المرشح:** \"لأن أندرويد بعد ما بينادي `onSaveInstanceState` بيقفل حالة الشاشة (State Loss Prevention). فلو التدفق استلم داتا في الخلفية وحاول يعمل `fragmentManager.commit()` أو يظهر Dialog، النظام بيرمي استثناء فوري لمنع فقدان الحالة، وده من أشهر أسباب الكراشات لو مفيش repeatOnLifecycle.\"\n\n- **المحاور:** \"كيف يؤثر التجميع المستمر في الخلفية على StateFlow مضبوط بـ WhileSubscribed(5000)؟\"\n  **المرشح:** \"بيفشله تماماً؛ لأن فكرة WhileSubscribed بتعتمد على إن عدد المشتركين ينزل لصفر في الخلفية علشان يوقف المصدر العلوي. فلو الواجهة فضلت مجمعة في الخلفية، العداد هيفضل 1 ومش هيقف أبداً وهيستمر في سحب بطارية الموبايل.\"",
        "self_check_ar": "هل ذكرت الآثار الأربعة: البطارية، تسريب الذاكرة، كراشات الواجهة، وإفشال WhileSubscribed؟ وهل حددت الحل الصحيح؟",
        "references_ar": f"- [Android lifecycle-aware components](https://developer.android.com/topic/libraries/architecture/lifecycle) — دليل جوجل الرسمي لإدارة دورة الحياة.\n- [Avoid UI state loss in Android](https://developer.android.com/guide/fragments/saving-state) — تجنب كراشات حفظ حالة الواجهة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بيحصل كوارث في أداء واستقرار التطبيق: استنزاف فظيع للبطارية وباقة الإنترنت لأن حساسات الـ GPS والشبكة بتفضل شغالة في الخلفية، تسريب ميموري لمنع تنظيف الشاشة من الـ RAM، وكراش فوري `IllegalStateException` لو الكود حاول يعدل الواجهة بعد ما الشاشة راحت في الـ Background.",
        "best_answer_ar": "تجميع التدفقات للأبد في واجهة المستخدم بدون وعي بدورة الحياة (Lifecycle) هو أحد أخطر الأخطاء المعمارية في أندرويد، وبيترتب عليه 4 كوارث إنتاجية مباشرة:\n\nأولاً، استنزاف البطارية والموارد؛ لو الـ Flow ده متصل بـ GPS أو Bluetooth أو WebSocket، العتاد ده هيفضل شغال ويسحب طاقة في الخلفية والمستخدم قافل الشاشة ومش بيستخدم التطبيق، وده بيفرغ البطارية في ساعات معدودة ويجيب تقييمات سلبية على المتجر.\n\nثانياً، تسريب الذاكرة (Memory Leak)؛ لأن الكوروتين اللي شغالة بتفضل ماسكة مرجع للـ Activity أو الـ Fragment، والـ Garbage Collector مش هيقدر يمسحها من الـ RAM، وده بيعمل تراكم ويسبب OutOfMemoryError.\n\nثالثاً، كراشات الـ UI القاتلة؛ لو الكود اللي بيجمع الداتا حاول يفتح Dialog أو يعمل Commit لـ Fragment بعد ما الشاشة دخلت في الـ Background واستدعت `onSaveInstanceState`، أندرويد هيرمي كراش فوري `IllegalStateException: Can not perform this action after onSaveInstanceState`.\n\nرابعاً، إفساد استراتيجية `WhileSubscribed` في الـ ViewModel؛ لأن التدفق العلوي مش هيعرف إن الشاشة اتقفلت، وعداد المشتركين هيفضل أكبر من صفر، فمش هيوقف استهلاك الموارد أبداً.",
        "deep_answer_ar": "على مستوى الـ Operating System Architecture ونظام إدارة الطاقة في أندرويد، التجميع المستمر بينتهك سياسات الـ Doze Mode والـ Background Execution Limits. لما التطبيق بيكون في الخلفية والـ Collector شغال يطلب إحداثيات GPS، النظام بيعتبر التطبيق مستهلكاً شرهاً للطاقة (High Battery Drainer) وبيصنفه في تقارير Google Play Vitals ضمن التطبيقات السيئة، وممكن يمنع ظهوره في الاقتراحات الأولى للمتجر.\n\nمن الناحية التقنية، لما الـ Collector بيكون شغال داخل `lifecycleScope.launch` بدون `repeatOnLifecycle`، الكوروتين بتفضل `Active`. وبما إن الـ Closure بتاع الـ Lambda ماسك متغيرات الواجهة، فكائن الـ Binding والـ Views بتفضل محبوسة في الـ Heap، وده بينشئ Retained Memory ضخمة جداً بتخنق التطبيق مع تدوير الشاشة المتكرر.\n\nوالكارثة المعمارية الأكبر هي الـ Fragment State Invariant؛ نظام أندرويد مصمم لمنع الـ State Loss. أول ما النظام يستدعي `onSaveInstanceState`، أي محاولة لتغيير الـ UI Hierarchy من كوروتين بتستلم داتا في الخلفية بتعتبر تعدي أمني ومعماري، والنظام مصمم إنه يرمي كراش فوري ويقفل البروسيس في الحال.\n\nبالإضافة لكده، ده بيعطل دورة حياة الـ StateFlow المعكوسة؛ لأن `MutableStateFlow` بيراقب مصفوفة الـ Slots، فلو الـ Scope مفصلش، `subscriptionCount` مستحيل يوصل للصفر، وده بيمنع الـ Repository من إنه يقفل الـ SQLite Locks أو مقابس السيرفر.\n\nعلشان كده في معايير الجودة للشركات الكبرى، بنعتبر التجميع المباشر ده P0 Bug، وبنلزم استخدام `viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED)` في الـ Fragments و `collectAsStateWithLifecycle()` في Jetpack Compose كقاعدة هندسية غير قابلة للنقاش."
    }
}

# ==========================================
# FLO-24: Testing Flow with runTest and Turbine
# ==========================================
DATA["FLO-24"] = {
    "concept_en": """Testing Kotlin Flow and StateFlow pipelines reliably requires pairing the modern kotlinx-coroutines-test framework (specifically runTest and StandardTestDispatcher) with the Turbine assertion library.
runTest provides an isolated, deterministic coroutine testing environment featuring virtual time control (TestCoroutineScheduler) that automatically skips real-time delay calls, preventing flaky unit tests and slow test execution.
StandardTestDispatcher executes coroutines deterministically using a queue that advances only when virtual time is explicitly advanced via advanceTimeBy or when pending tasks are executed via runCurrent.
Turbine is a specialized, fluent testing library built specifically for Kotlin Flow. It converts asynchronous streams into an intuitive, sequential testing DSL using the test { } extension function. Turbine validates sequential emissions via awaitItem(), verifies terminal states via awaitComplete(), asserts exceptions via awaitError(), and enforces strict cleanliness by ensuring no unconsumed emissions remain at test completion.""",
    "walkthrough_en": """Testing ViewModel StateFlow pipelines using runTest and Turbine:
```kotlin
class ProductViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule() // Sets Dispatchers.Main to StandardTestDispatcher

    @Test
    fun `loadProducts emits loading then success state`() = runTest {
        val fakeRepository = FakeProductRepository()
        val viewModel = ProductViewModel(fakeRepository)

        // Using Turbine to test StateFlow emissions:
        viewModel.uiState.test {
            // 1. Initial state emitted immediately:
            assertEquals(ProductUiState.Loading, awaitItem())

            // Trigger action:
            viewModel.loadProducts()

            // 2. Await subsequent data update:
            val successItem = awaitItem() as ProductUiState.Success
            assertEquals(3, successItem.products.size)

            // 3. Ensure no trailing unexpected emissions:
            expectNoEvents()
        }
    }
}
```""",
    "short_en": """runTest provides deterministic coroutine testing with virtual time control, automatically skipping delays instantly. Turbine tests Flows sequentially using awaitItem(), awaitComplete(), and expectNoEvents(), eliminating flaky assertions, asynchronous timing bugs, and race conditions in production stream testing.""",
    "structured_en": """To begin with, testing asynchronous data streams requires deterministic scheduling and strict emission verification.
From an architectural standpoint, testing flows with standard procedural assertions causes severe race conditions and timing flakes. runTest provides virtual time control, executing suspending coroutines deterministically on a single test thread and automatically skipping delays.
In production scenarios, Turbine provides the definitive testing DSL for Kotlin Flow. Calling flow.test { } launches a background collector and captures emissions into an internal queue, allowing engineers to verify each emission step-by-step using awaitItem().
As for boundary management, Turbine guarantees test rigor through strict completion checks. It requires developers to explicitly assert terminal events via awaitComplete() or expectNoEvents(), guaranteeing that no unexpected side-effect emissions or lingering background tasks escape validation.""",
    "deep_senior_en": """Under the hood, runTest instantiates a TestScope bound to a TestCoroutineScheduler and a StandardTestDispatcher. When a flow under test invokes delay(5000L), the virtual scheduler increments its internal clock without stalling the physical CPU thread, executing the delayed coroutine in single-digit milliseconds.
Turbine connects to this test infrastructure by launching a dedicated collector coroutine inside the TestScope via flow.test { }. It routes emitted items into an internal Channel. When the test invokes awaitItem(), Turbine suspends the test body until an item arrives in the channel. If virtual time needs advancement to trigger an emission (such as testing a debounce(300L) operator), the test invokes advanceTimeBy(301L), driving the scheduler clock forward deterministically.
A vital production distinction exists between testing cold Flows and testing hot StateFlows. Because StateFlow conflates identical values, calling awaitItem() captures only state transitions that produce distinct structural equality changes. Furthermore, testing StateFlows created with SharingStarted.WhileSubscribed(5000) requires advancing virtual time past the 5000ms threshold to test subscriber detachment and stream cancellation. StandardTestDispatcher enforces full control over coroutine execution order via runCurrent(), making race conditions reproducible and easy to debug.
Staff engineers enforce strict test suites: replacing Thread.sleep or manual polling loops with Turbine assertions to guarantee fast, deterministic CI pipeline verification.""",
    "meta_ar": {
        "id": "FLO-24",
        "questionAr": "كيف تختبر الـ Flow و StateFlow باحترافية باستخدام runTest ومكتبة Turbine؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- الفهم الاحترافي لاختبار التدفقات غير المتزامنة في أندرويد.\n- إتقان استخدام بيئة runTest والتحكم بالوقت الافتراضي (Virtual Time).\n- استخدام مكتبة Turbine للتحقق المتسلسل من الانبعاثات (awaitItem, awaitComplete, expectNoEvents).",
        "why_it_matters_ar": "اختبار الـ Flow بطرق تقليدية زي `Thread.sleep` يجعل الـ CI بطيئاً جداً وممتلئاً بالاختبارات المتقلبة الفاشلة عشوائياً (Flaky Tests)، بينما غياب فحص الأحداث بدقة يسمح بتسريب أخطاء الـ State Conflation والـ Race Conditions لنسخة الإنتاج.",
        "worked_example_ar": "كتابة اختبار حتمي وسريع لحالة الـ ViewModel عبر Turbine:\n```kotlin\n@Test\nfun `test user login updates state correctly`() = runTest {\n    val viewModel = AuthViewModel(fakeAuthRepo)\n\n    viewModel.uiState.test {\n        // 1. فحص الحالة الابتدائية فوراً:\n        assertEquals(AuthUiState.Idle, awaitItem())\n\n        // تنفيذ الحدث:\n        viewModel.login(\"user\", \"pass\")\n\n        // 2. التحقق من حالة التحميل ثم حالة النجاح بالترتيب:\n        assertEquals(AuthUiState.Loading, awaitItem())\n        val successState = awaitItem() as AuthUiState.Success\n        assertEquals(\"token_123\", successState.token)\n\n        // 3. التأكد من عدم وجود أي انبعاثات غير متوقعة:\n        expectNoEvents()\n    }\n}\n```",
        "trade_offs_ar": "مكتبة Turbine تفرض اختبارات صارمة جداً؛ فعدم استهلاك كل الانبعاثات يسقط الاختبار فوراً، ولكنه في المقابل يضمن اختبارات موثوقة وسريعة تعمل في أجزاء من الثانية.",
        "failure_modes_ar": "استخدام `Thread.sleep` بدلاً من تقديم الوقت الافتراضي بـ `advanceTimeBy`، مما يبطئ الاختبارات. خطأ آخر هو نسيان أن `StateFlow` يقوم بعمل Conflation؛ فلو انبعثت حالتان متطابقتان فلن تصدر إلا قيمة واحدة ولن تستلم Turbine العنصر المكرر.",
        "production_perspective_ar": "في المشروعات المصرفية والأنظمة المعقدة، نمنع دمج أي كود لا يحتوي على Unit Tests مبنية بـ `runTest` و `Turbine`. هذا المعيار يرفع موثوقية الـ ViewModels إلى 100% ويقلل أوقات تنفيذ الـ CI من نصف ساعة إلى دقيقة واحدة.",
        "how_to_answer_ar": "- **بيئة runTest:** توفر بيئة اختبار حتمية تتحكم في الوقت الافتراضي (Virtual Time Scheduler) وتتخطى التأخيرات الزمنية فوراً بدون انتظار حقيقي.\n- **مكتبة Turbine:** مكتبة رسمية متخصصة تتيح اختبار التدفقات عبر دالة `flow.test { }` بنمط تسلسلي بسيط.\n- **الدوال الأساسية:**\n  1. `awaitItem():` تستلم وتتحقق من العنصر المنبعث التالي بالترتيب.\n  2. `awaitComplete():` تتأكد من اكتمال التدفق بسلام.\n  3. `expectNoEvents():` تتأكد من عدم وجود أي أحداث إضافية معلقة.\n- **فخ الـ Conflation في StateFlow:** التنبيه بأن الحالات المتطابقة تُسقط ولا تظهر في awaitItem.\n- **اختبار المشغلات الزمنية:** استخدام `advanceTimeBy` لتقديم الوقت واختبار debounce بسهولة.",
        "talking_points_ar": "ناقش TestCoroutineScheduler و StandardTestDispatcher، وكيف تدير Turbine طابور القناة الداخلي، وكيفية اختبار WhileSubscribed(5000) بتقديم الوقت الافتراضي.",
        "follow_ups_ar": "- **المحاور:** \"كيف تختبر مشغل debounce(300L) باستخدام Turbine بدون انتظار حقيقي؟\"\n  **المرشح:** \"باستخدام `runTest`؛ بنبعث القيمة في الـ Flow، وبعدين بننادي `advanceTimeBy(301L)` لتقديم الوقت الافتراضي في الـ TestScheduler، وفي اللحظة دي الـ debounce بيبعت القيمة فوراً وبنستلمها بـ `awaitItem()` في جزء من الملي ثانية بدون أي تأخير حقيقي.\"\n\n- **المحاور:** \"ماذا يحدث لو انتهى كود اختبار Turbine وفيه عنصر منبعث لم يتم استدعاء awaitItem له؟\"\n  **المرشح:** \"اختبار Turbine هيفشل فوراً ويرمي `AssertionError: Expected no events but found Item(...)`. Turbine بتفرض صرامة كاملة بإن كل انبعاث لازم يتم التحقق منه صراحة لضمان عدم وجود أي آثار جانبية خفية في الكود.\"",
        "self_check_ar": "هل شرحت دور runTest والوقت الافتراضي؟ هل وضحت دوال Turbine الأساسية؟ وهل نبهت لمأزق Conflation مع StateFlow؟",
        "references_ar": f"- [Testing Kotlin flows official guide](https://developer.android.com/kotlin/flow/test) — دليل أندرويد الرسمي لاختبار التدفقات.\n- [Turbine library on GitHub](https://github.com/cashapp/turbine) — التوثيق الرسمي لمكتبة Turbine من Cash App.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنستخدم `runTest` للتحكم في الوقت الافتراضي وتخطي الـ `delay` في أجزاء من الثانية بدون انتظار، وبنستخدم مكتبة `Turbine` عبر بلوك `flow.test { }` لاختبار كل انبعاث متسلسل بـ `awaitItem()` والتأكد من عدم وجود انبعاثات زايدة بـ `expectNoEvents()`، وده بيقضي تماماً على الاختبارات المتقلبة.",
        "best_answer_ar": "اختبار الـ Flow والـ StateFlow في كوتلن وصل لقمة النضج بفضل دمج بيئة `runTest` مع مكتبة `Turbine` من شركه Cash App.\n\nبيئة `runTest` هي الأساس؛ وظيفتها إنها بتوفر جدولة حتمية (Deterministic Scheduling) وبتتحكم في الوقت الافتراضي عبر `TestCoroutineScheduler`. فلو الكود بتاعك فيه `delay(5000L)` لتأخير معين أو اختبار `WhileSubscribed(5000)`، الاختبار مبيستناش 5 ثوانٍ حقيقية، هو بيقدم الوقت الافتراضي فوراً ويخلص الاختبار في 10 مللي ثانية.\n\nأما مكتبة `Turbine` فهي الأداة القياسية لاختبار التدفقات؛ بتنادي `flow.test { }` وتبدأ تستلم العناصر بالترتيب باستخدام `awaitItem()`. فتقدر تتأكد مثلاً إن الـ StateFlow بدأ بحالة `Loading`، وبعد نداء الدالة انبعثت حالة `Success`، وفي النهاية بتنادي `expectNoEvents()` علشان تضمن إن مفيش أي انبعاثات عشوائية تانية حصلت.\n\nوالنقطة الذكية اللي لازم تاخد بالك منها في الاختبارات هي إن `StateFlow` بيعمل Conflation؛ يعني لو انبعثت حالتين ورا بعض متطابقتين في البيانات، Turbine هتستلم قيمة واحدة بس لأن فحص التساوي بيسقط التكرار، وده بيخلي اختباراتك دقيقة ومطابقة لسلوك التطبيق في الإنتاج بنسبة 100%.",
        "deep_answer_ar": "تحت الكابوت، بيئة `runTest` بتنشئ `TestScope` مربوط بـ `StandardTestDispatcher` ومتحكم فيه `TestCoroutineScheduler`. الفارق الجوهري بينه وبين الـ Dispatchers العادية هو إن المهام المؤجلة بتدخل في طابور مهام افتراضي، ومبتتنفذش إلا لما انت كمهندس اختبار تقول له صراحة: `advanceTimeBy(millis)` أو `runCurrent()`.\n\nمكتبة `Turbine` بتستغل البيئة دي بذكاء شديد؛ أول ما بتكتب `flow.test { }`، المكتبة بتفتح كوروتين تجميع فرعية مخصصة على الـ TestScope، وبتحول كل الانبعاثات والاستثناءات وإشارات الإغلاق لقناة داخلية (Internal Channel). ولما بتستدعي `awaitItem()`، كود التيست بيعلق نفسه لحد ما يوصل عنصر في القناة، وده بيمنع تماماً أي مشاكل Race Conditions أو الحاجة لانتظار عشوائي.\n\nأحد أهم التطبيقات العملية لـ Turbine هو اختبار مشغلات الوقت زي `debounce(300L)`؛ كل اللي بتعمله إنك بتبعت الحرف في الـ StateFlow، وبعدها بتستدعي `advanceTimeBy(301L)`، فتلاقي الـ Turbine استلمت الكلمة في `awaitItem()` فوراً وبدون ما تضيع جزء من الثانية من وقت السيرفر في الـ CI Pipeline.\n\nالميزة الإضافية لـ Turbine هي الصرامة الإجبارية (Strict Contract Enforcement)؛ لو الـ Flow بعت 3 عناصر وانت عملت `awaitItem()` لعنصرين بس وخلصت التيست، البلوك هيرمي `AssertionError` فوري ويسقط الاختبار لأنك مهملتش التحقق من باقي الداتا، وده بيضمن جودة كود وخلوه من الآثار الجانبية غير المتوقعة."
    }
}


def main():
    print(f"Elevating 8 questions in FLO (FLO-17 to FLO-24)...")
    for qid, data in DATA.items():
        ee.update_canonical_question(
            qid=qid,
            concept_en=data["concept_en"],
            walkthrough_en=data["walkthrough_en"],
            short_en=data["short_en"],
            structured_en=data["structured_en"],
            deep_senior_en=data["deep_senior_en"]
        )

    # Save metadata chunk
    chunk_meta = {qid: DATA[qid]["meta_ar"] for qid in DATA}
    meta_path = ee.DATA_DIR / "metadata_flo_17_24.json"
    ee.DATA_DIR.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(chunk_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved Arabic metadata to {meta_path}")

    # Merge metadata into master
    ee.merge_all_metadata()

    # Validate all 8 questions
    all_ok = True
    for qid in DATA:
        errs = ee.validate_question(qid)
        if errs:
            print(f"❌ {qid} validation failed with {len(errs)} errors:")
            for e in errs:
                print(f"  - {e}")
            all_ok = False
        else:
            print(f"✅ {qid} passed validation with 0 errors!")

    if not all_ok:
        print("Some questions failed validation!")
        sys.exit(1)
    else:
        print("All 8 FLO questions (FLO-17 to FLO-24) successfully elevated and passed validation!")


if __name__ == "__main__":
    import json
    main()

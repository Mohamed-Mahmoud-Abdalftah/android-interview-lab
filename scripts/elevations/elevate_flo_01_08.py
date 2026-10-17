#!/usr/bin/env python3
"""Elevate FLO-01 through FLO-08 for bilingual parity and senior spoken answers."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import elevation_engine as ee

TOPIC_AR = "الـ Flow و StateFlow و SharedFlow والـ Channels"
REVIEWED_DATE_AR = "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."

DATA = {}

# ==========================================
# FLO-01: What is Flow? Compare Flow & suspend
# ==========================================
DATA["FLO-01"] = {
    "concept_en": """Kotlin Flow is an asynchronous data stream built on top of coroutines that sequentially emits multiple values over time, operating under reactive stream principles with cooperative backpressure. The fundamental architectural distinction between a standard suspending function and a Flow centers on cardinality and execution lifetime. A suspending function models a single asynchronous computation returning exactly one value (1:1 cardinality)—such as executing a network request, writing a record to a database, or reading a configuration flag. Once the suspend function produces its outcome or throws an exception, its execution frame finishes. Conversely, a Flow represents an asynchronous sequence of values (1:N cardinality) that emits continuous updates—such as observing real-time database modifications, streaming GPS location coordinates, or listening to incoming WebSocket frames. Cold by default, a Flow does not allocate resources or execute upstream producers until a terminal operator like collect is invoked, and it cancels automatically when the collector's coroutine scope terminates.""",
    "walkthrough_en": """Contrasting single-shot operations with continuous observation in an Android repository:
```kotlin
interface UserAccountRepository {
    // 1. One-shot operation: Suspend function returns a single asynchronous result
    suspend fun updateDisplayName(newName: String): Result<Unit>

    // 2. Continuous data stream: Flow emits multiple values over time as database mutates
    fun observeAccountBalance(): Flow<BigDecimal>
}

// In the ViewModel:
class AccountViewModel(private val repository: UserAccountRepository) : ViewModel() {
    val balance: StateFlow<BigDecimal> = repository.observeAccountBalance()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = BigDecimal.ZERO
        )

    fun changeName(name: String) {
        viewModelScope.launch {
            repository.updateDisplayName(name)
        }
    }
}
```""",
    "short_en": """A suspend function produces a single asynchronous result (one-shot), completing immediately once returned. A Flow is an asynchronous data stream that sequentially emits multiple values over time (1:N), supporting cooperative backpressure, reactive transformations, and automatic cancellation through structured concurrency.""",
    "structured_en": """To begin with, the core divergence between a suspend function and a Flow is cardinality and stream duration.
From an architectural standpoint, a suspending function models a single asynchronous operation with a discrete start and end, returning exactly one value or throwing an error. We use suspend functions for discrete transactions like authenticating a user, triggering a remote refresh, or writing a key-value setting.
In production scenarios, Flow models continuous state or event emissions over time. We expose Flow from Room database queries, location providers, or WebSocket clients where the UI layer must continuously observe ongoing changes without repeatedly polling the underlying source.
As for boundary management, Flow is cold by default, meaning upstream production only starts when an active terminal operator like collect is invoked. Because it operates within coroutine structured concurrency, if the collecting ViewModelScope or lifecycle scope cancels, upstream production and channel resources are cleanly dismantled without requiring manual disposable teardown.""",
    "deep_senior_en": """Under the hood in kotlinx.coroutines, Flow is defined as a deceptively simple interface with a single method: suspend fun collect(collector: FlowCollector<T>). Because collect is itself a suspending function, the entire execution pipeline of a cold Flow runs synchronously inside the collector's CoroutineContext unless explicitly switched using flowOn.
This architectural design delivers three distinct advantages over legacy reactive libraries like RxJava. First, it eliminates thread-hopping overhead; emissions execute directly on the collector's current dispatcher without scheduling tasks on intermediate thread pool queues. Second, backpressure is resolved natively through continuation suspension. When FlowCollector.emit is invoked, it is a suspending call. If the downstream collector is executing slow computations or rendering frames, the upstream emitter suspends automatically until the collector completes its processing loop, preventing memory bloat without complex buffer overflow policies.
Third, lifecycle management is bound directly to structured concurrency. When a collecting coroutine cancels, the suspension point inside collect or emit throws a CancellationException, unwinding the upstream try-finally blocks immediately.
In unit tests, suspending functions are verified with straightforward assertions on their returned values, whereas Flow pipelines require dedicated assertions via Turbine to test intermediate states, emissions, and completion signals reliably.
Staff engineers enforce strict API boundaries: repositories expose suspend functions for mutations and one-shot fetches, while reserving Flow strictly for observable data sources to prevent unnecessary stream wrapping of single scalar values.""",
    "meta_ar": {
        "id": "FLO-01",
        "questionAr": "ما هو الـ Flow؟ وما الفرق بينه وبين دالة suspend عادية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- التمييز بين استرجاع قيمة واحدة (1:1) وبث تدفق بيانات مستمر (1:N).\n- فهم الطبيعة الكسولة (Cold Stream) وتأجيل التنفيذ حتى استدعاء دالة طرفية مثل collect.\n- استيعاب آلية الـ Backpressure التلقائية عبر تعليق الكوروتينات وتفكيك الموارد مع الإلغاء.",
        "why_it_matters_ar": "الخلط بين الدوال المعلقة والـ Flow يسبب تعقيداً معمارياً غير مبرر؛ فتغليف عملية وحيدة (One-shot) داخل Flow يضيف تكلفة إنشاء كائنات ومسارات اشتراك لا داعي لها، بينما استخدام دالة suspend عادية لمراقبة قاعدة بيانات يجبر الواجهة على السحب اليدوي (Polling) بدلاً من التحديث التفاعلي الفوري.",
        "worked_example_ar": "الفارق العملي في طبقة المستودع بين استدعاء وحيد وتدفق مستمر:\n```kotlin\ninterface UserRepository {\n    // استدعاء وحيد: يرجع قيمة واحدة وينتهي:\n    suspend fun updateName(name: String): Result<Unit>\n\n    // تدفق مستمر: يبث تحديثات الرصيد كلما تغير في قاعدة البيانات:\n    fun observeBalance(): Flow<BigDecimal>\n}\n```\nالعملية الأولى تبدأ وتنتهي فوراً، بينما الثانية تظل تبث قيماً جديدة للمشترك طالما كانت شاشة التطبيق مفتوحة.",
        "trade_offs_ar": "استخدام دالة suspend بسيط ومباشر بدون استهلاك لموارد التتبع، ولكنه مقتصر على ناتج واحد. الـ Flow يوفر قدرات تحويلية هائلة (map, filter, combine) والـ Backpressure التلقائي، ولكنه يتطلب إدارة واعية لدورة حياة المشترك لمنع استمرار استهلاك الموارد في الخلفية.",
        "failure_modes_ar": "تغليف استدعاءات الشبكة العادية داخل Cold Flow وإعادة الاشتراك فيها عدة مرات في الواجهة، مما يتسبب في إرسال طلب HTTP جديد مع كل جامع. خطأ آخر هو قراءة Flow في واجهة المستخدم داخل GlobalScope مما يسرب الاتصال ويستنزف البطارية بعد مغادرة الشاشة.",
        "production_perspective_ar": "في تطبيقات الإنتاج الحديثة، تتبع الفرق الهندسية قاعدة صارمة: دوال التعديل وجلب اللقطات الفردية تكون suspend functions صريحة، بينما تقتصر الـ Flows على مراقبة الجداول المحلية في Room وإشعارات WebSockets مع ربط الجمع بـ `repeatOnLifecycle`.",
        "how_to_answer_ar": "- **الفارق الجوهري:** ابدأ بتوضيح التعددية (Cardinality)؛ دالة suspend لقيمة واحدة (1:1) والـ Flow لسلسلة قيم عبر الزمن (1:N).\n- **طبيعة العمل:** وضح أن Flow كائن بارد (Cold) لا يبدأ عمله إلا عند استدعاء collect.\n- **الميزة المعمارية:** اذكر الـ Backpressure التلقائي بفضل دالة emit المعلقة والاندماج مع الـ Structured Concurrency.\n- **أمثلة واقعية:** قارن بين تحديث الاسم (suspend) ومراقبة الرصيد (Flow).\n- **التوجيه الهندسي:** منع تغليف العمليات الفردية داخل Flow دون حاجة حقيقية للبث.",
        "talking_points_ar": "ناقش الواجهة البسيطة `suspend fun collect(collector: FlowCollector<T>)`، وكيف تحل دالة emit المعلقة مشكلة الـ Backpressure مقارنة بـ RxJava، وعدم الحاجة لـ Schedulers معقدة بفضل توريث الـ CoroutineContext.",
        "follow_ups_ar": "- **المحاور:** \"هل يمكن لـ Flow أن يظل يبث قيماً إلى ما لا نهاية؟\"\n  **المرشح:** \"أيوة، الـ Flow يقدر يبث قيماً غير محدودة طالما الكوروتين الحاضنة نشطة ومفيش استثناء، زي مراقبة الـ GPS أو الـ WebSockets، ومش بينتهي إلا لما الـ Scope يتلغي أو المصدر يقفل البث صراحة.\"\n\n- **المحاور:** \"كيف يتعامل Flow مع بطء المستهلك مقارنة بـ RxJava؟\"\n  **المرشح:** \"في Flow، دالة `emit` هي دالة معلقة (suspend fun)؛ لو المستهلك بطيء، الـ emitter بيتعلق تلقائياً في مكانه ومش بيبعت العنصر التالي إلا لما الـ collector يخلص، وده بيحل مشكلة الـ Backpressure بشكل طبيعي وبدون الحاجة لسياسات Buffer معقدة.\"",
        "self_check_ar": "هل فرقت بين 1:1 و 1:N؟ هل شرحت الطبيعة الكسولة للـ Cold Flow؟ وهل وضحت آلية الـ Backpressure الطبيعية؟",
        "references_ar": f"- [Kotlin Flow official documentation](https://kotlinlang.org/docs/flow.html) — الدليل الرسمي لمكتبة Flow والتفاعل.\n- [Coroutines and Streams guide](https://developer.android.com/kotlin/flow) — أفضل ممارسات استخدام Flow في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الدالة المعلقة `suspend` بترجع قيمة واحدة بس وبتنتهي في وقتها بنظام One-shot، زي إرسال طلب شبكة أو قراءة قيمة واحدة. أما الـ `Flow` فده تيار متدفق غير متزامن بيبث عدة قيم ورا بعض عبر الزمن بنظام 1:N، وهو بارد افتراضياً ومبيشتغلش إلا لما تطلب الجمع بـ collect وبيدعم الـ Backpressure تلقائياً.",
        "best_answer_ar": "الفارق الجوهري بين الدالة المعلقة والـ Flow بيتلخص في عدد القيم وتوقيت البث على مدار دورة حياة المهمة.\n\nالدالة المعلقة `suspend fun` مصممة لحساب وإرجاع قيمة واحدة غير متزامنة (One-shot)؛ بتبدأ وتنفذ العملية زي جلب بيانات بروفايل أو حفظ إعداد وترجع النتيجة وتنتهي تماماً، ومتقدرش تبعت تحديثات تانية لنفس النداء.\n\nأما الـ `Flow` فهو Stream تفاعلي مصمم لبث سلسلة من القيم المتتابعة عبر الزمن؛ بنستخدمه لما الواجهة تحتاج تراقب بيانات بتتغير باستمرار، زي مراقبة رصيد الحساب من داتابيز Room أو تتبع إحداثيات الـ GPS أو رسائل الـ WebSocket.\n\nبالإضافة لكده، الـ Flow كائن بارد (Cold) افتراضياً، يعني كود الإنتاج جواه مبيتحركش ولا بيستهلك ميموري إلا لما المستدعي ينادي دالة طرفية زي `collect()`. وبما إنه مبني بالكامل على الكوروتينات، فهو بيتعامل مع الـ Backpressure بذكاء؛ لأن دالة `emit` معلقة وبتستنى المستهلك يخلص معالجة قبل ما تبعت القيمة اللي بعدها، ومع إلغاء الـ Scope بيتقفل المصدر فوراً.",
        "deep_answer_ar": "تحت الكابوت في `kotlinx.coroutines`، الـ `Flow` مبني على واجهة شديدة البساطة فيها دالة واحدة بس: `suspend fun collect(collector: FlowCollector<T>)`. ولأن `collect` دالة معلقة، فدورة حياة الـ Flow بالكامل بتتنفذ داخل الـ CoroutineContext بتاع المستدعي، وده بيدي Flow ميزة هندسية ضخمة مقارنة بأطر العمل القديمة زي RxJava.\n\nالميزة الأولى هي انعدام تكلفة التبديل العشوائي بين الخيوط (Thread Hopping)؛ الـ Flow مبيحتاجش Schedulers معقدة، هو بيعلق نفسه على نفس خيط المعالجة بتاع المشترك بشكل تعاوني.\n\nالميزة التانية هي الـ Native Backpressure؛ دالة `emit` المعلقة لما بتتبعت بتعلق الـ Emitter لو كان الـ Collector مشغول في عملية رسم أو معالجة داتا تقيلة، فبتمنع تراكم آلاف الكائنات في الذاكرة بدون الحاجة لسياسات Buffer معقدة في الحالات العادية.\n\nالميزة التالتة هي الاندماج الصارم مع الـ Structured Concurrency؛ لما كوروتين التجميع بتتلغي عند تدمير الشاشة، بيترمي `CancellationException` بيفكك كل كتل الـ `try-finally` في مسار الإنتاج فوراً بدون أي تسريب لمصادر الشبكة أو قواعد البيانات.\n\nوفي اختبارات الـ Unit Testing، اختبار الدوال المعلقة بيكون مباشر وبسيط بمقارنة القيمة الراجعة، بينما اختبار الـ Flow بيتطلب أدوات مخصصة زي مكتبة Turbine للتحقق من تسلسل الانبعاثات وإشارات الإلغاء بدقة.\n\nعلشان كده في بيئات الإنتاج، بنمنع تماماً تغليف العمليات الفردية جوه Flow لمجرد المظهر المعماري، وبنلزم الفرق باستخدام suspend functions صريحة للعمليات الفردية وحصر Flow في المصادر الحقيقية دائمة التغير."
    }
}

# ==========================================
# FLO-02: Cold flows & multiple collectors
# ==========================================
DATA["FLO-02"] = {
    "concept_en": """Cold flows in Kotlin represent declarative, on-demand data pipelines whose execution blocks are completely dormant until a terminal operator is invoked. Created primarily via the flow { } builder or derived transformations, a cold flow does not store state in memory, does not maintain an internal buffer, and does not broadcast emissions to shared listeners. When multiple collectors invoke collect on the same cold flow instance, the underlying builder block executes independently and from the beginning for each individual collector. This means that upstream operations—such as opening network sockets, querying databases, reading disk files, or spawning timers—are completely duplicated per subscription. Each collector receives its own isolated sequence of emissions operating inside its own coroutine context. Transforming a cold flow into a shared or broadcasted stream requires explicit hot conversions using operators like stateIn or shareIn.""",
    "walkthrough_en": """Demonstrating duplicate execution with multiple collectors on a cold flow:
```kotlin
// Cold Flow definition: Network fetch executed inside flow { } builder
fun fetchPriceTicker(symbol: String): Flow<Double> = flow {
    println("Starting price fetch for $symbol...") // Prints every time collect() is called!
    val price = api.getLatestPrice(symbol)
    emit(price)
}

// In the UI or test harness:
suspend fun demonstrateColdCollectors() = coroutineScope {
    val priceFlow = fetchPriceTicker("BTC")

    // Collector 1 triggers a dedicated network request:
    launch {
        priceFlow.collect { price -> println("Collector 1 received: $price") }
    }

    // Collector 2 triggers a SECOND, independent network request:
    launch {
        priceFlow.collect { price -> println("Collector 2 received: $price") }
    }
    // Result: "Starting price fetch..." is printed TWICE, executing two HTTP calls!
}
```""",
    "short_en": """A cold flow is passive and executes its builder block independently for every collector. Multiple collectors do not share emissions; instead, each collect call restarts upstream production from scratch. If a cold flow makes network or database calls, collecting it three times triggers three separate network requests unless converted to hot via shareIn.""",
    "structured_en": """To begin with, cold flows represent declarative blueprints that execute on-demand rather than active data producers.
From an architectural standpoint, the defining characteristic of a cold flow is independent unicast execution. The code inside the flow builder does not execute until collect is invoked. When multiple subscribers collect the identical Flow reference, the upstream block executes independently for each subscription, duplicating all internal operations.
In production scenarios, this duplication can cause severe performance and financial issues. If a cold flow wraps an expensive REST API call or an SQLite table query, having three separate UI components collect the stream triggers three redundant HTTP transactions or database read operations, saturating network bandwidth and CPU cycles.
As for boundary management, when multiple collectors must observe identical data without duplicating upstream execution, engineers convert the cold flow into a hot stream using shareIn or stateIn, configuring a single upstream subscription that multicasts emissions across all active downstream collectors.""",
    "deep_senior_en": """Under the hood of the Kotlin coroutines framework, a cold flow created via flow { ... } instantiates a SafeFlow object. The SafeFlow class overrides collectSafely by passing the downstream FlowCollector into the lambda block as its receiver context. Because there is no intermediary dispatcher, registry, or central buffer, invoking collect is functionally equivalent to invoking a regular suspending function that takes a callback parameter.
Consequently, each collect invocation constructs an independent SafeCollector instance with its own CoroutineContext validation and state tracking. If collector A suspends due to a slow UI frame, collector B continues processing its own emissions unimpeded on its own thread, because their execution frames are entirely separate.
However, when cold flows interact with external reactive sources (such as hardware sensors, LocationManager callbacks, or Firebase real-time listeners), independent collection leads to catastrophic resource waste and battery drain. If three ViewModels collect a raw cold callbackFlow wrapping a GPS listener, the device hardware activates three separate GPS provider registrations, dramatically accelerating battery depletion.
Staff Android engineers resolve this by enforcing clean architectural layering: data layers expose cold flows representing raw queries, domain use cases apply operators, and ViewModels convert cold streams into hot StateFlow or SharedFlow instances at the presentation boundary using shareIn or stateIn with SharingStarted.WhileSubscribed(5000), guaranteeing single-instance upstream execution shared across all UI consumers.""",
    "meta_ar": {
        "id": "FLO-02",
        "questionAr": "اشرح مفهوم الـ Cold Flows وماذا يحدث عند وجود عدة جامعين (Collectors)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- الفهم المعماري للـ Cold Streams وعدم بدء الإنتاج إلا مع استدعاء collect.\n- إدراك تكرار تنفيذ الكود الداخلي بالكامل مع كل مشترك جديد (Unicast).\n- معرفة متى وكيف يتم تحويل الـ Cold Flow إلى Hot Stream لتفادي استنزاف الموارد.",
        "why_it_matters_ar": "الجهل بطبيعة الـ Cold Flow يسبب كوارث في الإنتاج؛ فإذا كان الـ Flow يرسل طلب شبكة أو يفتح اتصال قاعدة بيانات، وجمعه 3 عناصر واجهة في نفس الوقت، فسيتم إرسال 3 طلبات HTTP مكررة للسيرفر، مما يضاعف استهلاك الباقة والبطارية وقد يتسبب في حظر المستخدم بسبب الـ Rate Limiting.",
        "worked_example_ar": "توضيح تكرار تنفيذ الكود العلوي مع كل مشترك جديد:\n```kotlin\nfun fetchStockPrice(symbol: String): Flow<Double> = flow {\n    println(\"طلب شبكة جديد للسهم $symbol\") // يطبع مع كل collect جديد!\n    emit(api.getPrice(symbol))\n}\n\n// عند استدعاء الجامعين بالتوازي:\nlaunch { priceFlow.collect { ... } } // يشغل طلب شبكة أول\nlaunch { priceFlow.collect { ... } } // يشغل طلب شبكة ثانٍ مكرر تماماً!\n```\nالكود يوضح أن كل مشترك ينشئ مسار تنفيذ منفصل تماماً يعيد تشغيل الكود من بدايته.",
        "trade_offs_ar": "الـ Cold Flow ممتاز للمهام التي تتطلب بيانات معزولة ومخصصة لكل طالب (مثل قراءة ملف محدد)، ولا يستهلك أي ذاكرة طالما لا يوجد مستمع نشط. ولكنه غير مناسب للبيانات المشتركة بين عدة شاشات ما لم يتم تحويله إلى SharedFlow أو StateFlow.",
        "failure_modes_ar": "ربط عدة شاشات أو مكونات Compose بنفس الـ Cold Flow مباشرة، مما يؤدي لتكرار فتح اتصالات الـ WebSocket أو تكرار استعلامات SQLite الثقيلة. خطأ آخر هو توقع احتفاظ الـ Cold Flow بآخر قيمة مبعوثة، فهو لا يخزن أي حالة في الذاكرة.",
        "production_perspective_ar": "في تطبيقات الإنتاج، نوفر الـ Cold Flows حصراً في طبقة الـ Data Source كمخططات استعلام، وبمجرد وصولها للـ ViewModel نحولها فوراً إلى Hot StateFlow عبر `stateIn` مع استراتيجية `SharingStarted.WhileSubscribed(5000)`، لضمان اشتراك علوي واحد فقط تتشاركه جميع عناصر الشاشة.",
        "how_to_answer_ar": "- **التعريف المعماري:** الـ Cold Flow هو مخطط كسول (Lazy Blueprint) لا ينتج بيانات إلا بطلب صريح.\n- **ماذا يحدث مع عدة جامعين:** كل جامع يعيد تشغيل كود الـ Emitter من الصفر وبشكل مستقل تماماً (Unicast).\n- **الخطر الإنتاجي:** تكرار طلبات الشبكة، استنزاف البطارية، وتكرار فتح حساسات الـ GPS.\n- **الحل الهندسي:** استخدام `shareIn` أو `stateIn` لتحويله إلى تيار ساخن ومشترك (Multicast).\n- **توزيع المسؤوليات:** طبقة البيانات تنتج Cold، وطبقة الـ ViewModel تحول إلى Hot.",
        "talking_points_ar": "ناقش كلاس SafeFlow و SafeCollector، وكيف يتم تمرير كائن FlowCollector كمعامل في الدالة المعلقة، واستقلالية مسارات الـ CoroutineContext لكل مشترك، وأثر تكرار تسجيل الـ Callbacks في حساسات النظام.",
        "follow_ups_ar": "- **المحاور:** \"كيف تمنع تكرار طلبات الشبكة لو عندي 3 شاشات بتجمع نفس الـ Flow؟\"\n  **المرشح:** \"بنحول الـ Cold Flow لـ Hot SharedFlow أو StateFlow باستخدام معامل `shareIn` أو `stateIn` في الـ ViewModel. ده بيعمل اشتراك علوي واحد فقط ويوزع البيانات بالتوازي على المشتركين التلاتة كـ Multicast.\"\n\n- **المحاور:** \"هل الـ Cold Flow بيحتفظ بآخر قيمة تم إرسالها في الذاكرة؟\"\n  **المرشح:** \"لأ، الـ Cold Flow ملوش أي كاش ومبيحتفظش بأي حالة في الذاكرة. لو جامع جديد بدأ، الـ Flow بيبدأ إنتاج القيم من أول سطر كود من جديد.\"",
        "self_check_ar": "هل وضحت المعنى الحقيقي لكونه بارداً؟ هل بينت أن كل جامع ينشئ مساراً مستقلاً تماماً؟ وهل شرحت كيفية توحيد الاشتراك بـ shareIn؟",
        "references_ar": f"- [Cold flows in Kotlin](https://kotlinlang.org/docs/flow.html#flows-are-cold) — التوثيق الرسمي لخصائص التدفقات الكسولة.\n- [SharedFlow and StateFlow guide](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) — تحويل التدفقات الباردة إلى ساخنة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ Cold Flow هو تدفق بارد وكسول؛ مبيشتغلش ولا بينفذ أي سطر كود إلا لما جامع يستدعي `collect()`. ولما يكون فيه كذا جامع، كل واحد فيهم بيعيد تشغيل الكود من الأول بشكل مستقل تماماً، فلو الكود بيطلب داتا من السيرفر، هيتكرر طلب الـ HTTP بعدد الجامعين، وعلاجه تحويله لـ Hot Stream عبر `shareIn`.",
        "best_answer_ar": "مفهوم الـ Cold Flow بيعني إنه مجرد توصيف أو كود كسول (Lazy Blueprint) نايم في الذاكرة ومش بينفذ أي عملية إنتاج إلا لما مستهلك يطلب ده صراحة عبر دالة طرفية زي `collect()`.\n\nوالنقطة المحورية اللي لازم ينتبه ليها أي مهندس أندرويد هي سلوك الـ Flow مع تعدد المشتركين؛ الـ Cold Flow بطبيعته Unicast ومبيشاركش البيانات، يعني لو عندك شاشتين استدعوا `collect()` لنفس الـ Flow اللي بيعمل نداء شبكة، كود الـ Emitter هيشتغل مرتين من البداية وهيبعت طلبين HTTP مكررين للسيرفر، ولو تلاتة هيشتغل تلات مرات!\n\nده ممتاز في حالات القراءة المعزولة لكل مستخدم، لكنه كارثي لو البيانات مشتركة؛ لأنه بيستنزف باقة الإنترنت والبطارية وممكن السيرفر يقفل الحساب بسبب تكرار الطلبات.\n\nعلشان كده في بيئات الإنتاج، بنصمم طبقة الـ Repository إنها ترجع Cold Flow عادي، لكن بمجرد ما يوصل للـ ViewModel بنحوله لـ Hot Stream باستخدام `stateIn` أو `shareIn`، وده بيضمن وجود اتصال واحد فقط في الخلفية بيتوزع على كل جامعي الواجهة بنمط الـ Multicast.",
        "deep_answer_ar": "على مستوى الـ Implementation الداخلي لمكتبة الكوروتينات، لما بتكتب `flow { ... }`، المترجم بينشئ كائن من كلاس `SafeFlow`. الدالة دي لما حد بينادي عليها `collect()`، بتمرر الـ `FlowCollector` بتاع المشترك مباشرة كـ Receiver للبلوك، وده معناه ببساطة إن `collect` ما هي إلا استدعاء دالة عادية بتاخد Lambda، ومفيش أي كاش مركزي أو Event Loop وسيط.\n\nعلشان كده، كل جامع بينشئ كائن `SafeCollector` مستقل تماماً بالسياق الزمني والـ CoroutineContext بتاعه. لو الجامع الأول خيطه بطيء، الجامع التاني شغال على خيطه بأقصى سرعة بدون أي تأثير متبادل، لأنهم عملياً عمليتين مختلفتين تماماً في الذاكرة.\n\nالخطورة الحقيقية بتظهر لما الـ Cold Flow يغلف عتاد حقيقي للجهاز عبر `callbackFlow`، زي حساسات الـ GPS أو قراءة الـ Bluetooth. لو تلاتة ViewModels عملوا collect للـ Cold Flow ده، الجهاز هيسجل 3 Listeners على مستوى الـ Hardware، وده بيسحب طاقة البطارية في دقايق معدودة.\n\nالحل المعماري القياسي هو تحويل الـ Cold Flow إلى Hot StateFlow في طبقة الـ Presentation باستخدام `stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), InitialState)`. الاستراتيجية دي بتضمن دمج كل الجامعين في اشتراك علوي وحيد، ومع إغلاق الشاشة بتستنى 5 ثوانٍ قبل ما تفكك الاشتراك لتفادي إعادة فتح الاتصالات أثناء تدوير الشاشة."
    }
}

# ==========================================
# FLO-03: StateFlow and SharedFlow (Why hot?)
# ==========================================
DATA["FLO-03"] = {
    "concept_en": """StateFlow and SharedFlow are specialized \"hot\" stream primitives in Kotlin coroutines whose execution and lifecycle exist independently of the presence or number of active collectors. Unlike cold flows, a hot stream begins executing and holds values in memory as soon as it is allocated in a CoroutineScope, broadcasting emissions to multiple concurrent subscribers simultaneously (multicast). StateFlow is a state-holder hot stream that always stores and exposes a current value, requires an initial value upon instantiation, conflates sequential updates, and replays exactly its latest state to newly arriving subscribers. SharedFlow is a highly configurable, general-purpose hot event bus that supports custom replay cache sizes, extra buffer capacities, and configurable BufferOverflow drop strategies. They are classified as \"hot\" because their upstream producers emit regardless of whether downstream collectors are actively listening, and emissions not captured within configured buffers are dropped.""",
    "walkthrough_en": """Contrasting StateFlow state retention with SharedFlow event broadcasting:
```kotlin
class NewsFeedViewModel : ViewModel() {
    // 1. StateFlow: Holds current state, requires initial value, always replays 1 to new collectors
    private val _uiState = MutableStateFlow<NewsUiState>(NewsUiState.Loading)
    val uiState: StateFlow<NewsUiState> = _uiState.asStateFlow()

    // 2. SharedFlow: Broadcasts transient events, zero replay by default, drops if uncollected
    private val _userEvents = MutableSharedFlow<UserMessage>(
        replay = 0,
        extraBufferCapacity = 1,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val userEvents: SharedFlow<UserMessage> = _userEvents.asSharedFlow()

    fun onRefresh() {
        viewModelScope.launch {
            _uiState.value = NewsUiState.Success(fetchNews())
            _userEvents.emit(UserMessage.ShowToast("Feed updated successfully!"))
        }
    }
}
```""",
    "short_en": """StateFlow and SharedFlow are hot streams because they exist and emit independently of collectors, multicasting values to multiple subscribers. StateFlow is a state holder that always retains a current value, requires an initial state, and conflates updates. SharedFlow is a configurable event stream with customizable replay cache, buffer capacity, and overflow policies.""",
    "structured_en": """To begin with, StateFlow and SharedFlow represent hot streams whose lifecycles operate independently of downstream collectors.
From an architectural standpoint, the definition of a \"hot\" stream is that it produces and retains values in memory regardless of whether any subscriber is actively listening. When values are emitted, they are broadcast simultaneously to all active collectors using a multicast distribution model.
In production scenarios, we choose between them based on state persistence versus event transmission. StateFlow is designed specifically for UI state management. It requires an initial value, exposes a synchronous value getter, replays exactly its current state to new subscribers, and automatically conflates identical consecutive values.
As for boundary management, SharedFlow serves as an event stream. It does not require an initial value and allows engineers to customize replay capacity, buffer size, and overflow behavior, making it the preferred primitive for broadcasting one-off events, system notifications, or shared domain messages across multiple application components.""",
    "deep_senior_en": """At the lower plumbing layer of kotlinx.coroutines, StateFlow and SharedFlow are built on top of AbstractSharedFlow, a thread-safe allocation-free synchronization structure. Unlike cold flows that execute via sequential continuation passes, hot flows maintain an internal array of active subscriber slots (StateFlowSlot and SharedFlowSlot). When emit is invoked, the hot stream acquires an internal mutex, iterates over its active slot table, and wakes up suspended collector continuations directly.
StateFlow is mathematically equivalent to a specialized SharedFlow configured with replay = 1 and onBufferOverflow = BufferOverflow.DROP_OLDEST, coupled with strict Any.equals conflation. When MutableStateFlow.value is updated, it performs an equality check: if the new value equals the existing value, the emission is discarded immediately without waking collector slots, preventing redundant recompositions in Jetpack Compose and frame drops.
SharedFlow provides fine-grained backpressure tuning through three constructor parameters: replay determines how many previous emissions are cached for new subscribers; extraBufferCapacity provides headroom for emissions when collectors are slow; and onBufferOverflow dictates whether emit suspends (SUSPEND), drops the oldest buffered value (DROP_OLDEST), or drops the newly emitted value (DROP_LATEST).
Staff engineers enforce strict guidelines: UI screens must observe state via StateFlow to guarantee that rotated screens instantly render the current state; transient one-off events must either use SharedFlow with replay = 0 or be modeled directly as consumed fields within the single immutable StateFlow to prevent event loss or double execution.""",
    "meta_ar": {
        "id": "FLO-03",
        "questionAr": "ما هما StateFlow و SharedFlow؟ ولماذا يعتبران تيارين ساخنين (Hot Streams)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- الفهم الدقيق لمعنى التدفق الساخن (Hot Stream) واستقلالية الإنتاج عن وجود المشتركين.\n- التمييز المعماري بين StateFlow لحفظ الحالة و SharedFlow لبث الأحداث والرسائل.\n- فهم خصائص StateFlow: القيمة الابتدائية، الـ Conflation، وتوزيع الـ Multicast.",
        "why_it_matters_ar": "الخلط بين التدفق الساخن والبارد يؤدي لفقدان أحداث التطبيق أو تسريب الذاكرة؛ فاستخدام تيار ساخن للأحداث بدون ضبط التخزين المؤقت يضيع الإشعارات إذا لم يكن هناك مستمع نشط، بينما استخدام تيار بارد لعرض حالة الواجهة يعيد تحميل البيانات من الصفر مع كل دوران للشاشة.",
        "worked_example_ar": "مقارنة عملية بين StateFlow لحالة الشاشة و SharedFlow لأحداث الـ Toast:\n```kotlin\nclass HomeViewModel : ViewModel() {\n    // StateFlow: يحتفظ بأحدث حالة معروضة، ويتطلب قيمة أولية:\n    private val _state = MutableStateFlow<HomeState>(HomeState.Loading)\n    val state = _state.asStateFlow()\n\n    // SharedFlow: يبث أحداثاً عابرة بدون تخزين افتراضي:\n    private val _events = MutableSharedFlow<String>(replay = 0)\n    val events = _events.asSharedFlow()\n\n    fun notifyUser() {\n        _state.value = HomeState.Success\n        viewModelScope.launch { _events.emit(\"تم الحفظ بنجاح!\") }\n    }\n}\n```",
        "trade_offs_ar": "الـ StateFlow ممتاز لحالة الواجهة لضمان ظهور البيانات فوراً بعد التدوير، ولكنه يبتلع التكرار (Conflation) فلا يناسب أحداث النقر. والـ SharedFlow مرن جداً في التحكم بحجم الـ Buffer والـ Replay، ولكنه يسقط الأحداث الصادرة في حال عدم وجود مشتركين نشطين إذا كان replay = 0.",
        "failure_modes_ar": "استخدام StateFlow لبث رسائل SnackBar المتطابقة المتتالية، حيث يتجاهل StateFlow القيمة الثانية بسبب تساويها مع الأولى. خطأ آخر هو إرسال حدث ملاحة عبر SharedFlow بريبلاي 0 قبل أن تكتمل تهيئة الشاشة فيضيع الحدث في الفراغ.",
        "production_perspective_ar": "في تطبيقات أندرويد الحديثة، نعتمد على StateFlow كخيار افتراضي وحيد لحالة الواجهة في نمط MVI/UDF، بحيث يحتوي كائن الحالة على كل ما تحتاجه الشاشة. ونقيد استخدام SharedFlow للأحداث العامة بين عدة موديولات مع ضبط `extraBufferCapacity` لتفادي حظر الكوروتينات المنتجة.",
        "how_to_answer_ar": "- **سبب التسمية بـ Hot:** وضح أن التيارات الساخنة حية وتنتج بيانات باستمرار حتى بدون وجود أي جامع نشط، وتبث لكل المشتركين كـ Multicast.\n- **تعريف StateFlow:** وعاء حالة (State Holder) يحتفظ بآخر قيمة، يتطلب قيمة أولية، ويدمج التكرار (Conflation).\n- **تعريف SharedFlow:** ناقل أحداث عام وقابل للتخصيص الكامل في الـ Replay والـ Buffer والـ Overflow.\n- **المقارنة المعمارية:** StateFlow للحالة المستمرة للشاشة، و SharedFlow للأحداث والرسائل المشتركة.\n- **نصيحة الإنتاج:** تفضيل تمثيل أحداث الواجهة كجزء من كائن الـ StateFlow الموحد.",
        "talking_points_ar": "اشرح البنية الداخلية المبنية على AbstractSharedFlow ومصفوفة StateFlowSlot، وكيف يعادل StateFlow كائناً من SharedFlow بـ replay=1 و DROP_OLDEST مع فحص equals الصارم، وآليات تفادي Recomposition في Compose.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لحدث أرسلناه بـ SharedFlow بـ replay = 0 لو مكنش فيه أي شاشة بتسمع في اللحظة دي؟\"\n  **المرشح:** \"الحدث هيسقط ويضيع في الفراغ تماماً؛ لأن replay=0 يعني مفيش أي كاش للاحتفاظ بالقيم السابقة، وده سلوك مقصود في التيارات الساخنة لو مفيش مستمع جاهز في وقت البث.\"\n\n- **المحاور:** \"هل StateFlow يرسل نفس القيمة للمشتركين لو أسندناها له مرتين ورا بعض؟\"\n  **المرشح:** \"لأ، StateFlow بيعمل Conflation وبيفحص التساوي بـ Any.equals()؛ لو القيمة الجديدة مطابقة تماماً للقديمة، بيتجاهلها تماماً ومش بيصحي المشتركين، وده بيمنع إعادة رسم الواجهة بدون داعٍ.\"",
        "self_check_ar": "هل وضحت سبب تسميتهما بـ Hot؟ هل ميزت بين وظيفة كل منهما؟ وهل شرحت خصائص StateFlow الثلاثية (قيمة أولية، كاش 1، ومنع التكرار)؟",
        "references_ar": f"- [StateFlow and SharedFlow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) — التوثيق الرسمي لمنصات أندرويد.\n- [SharedFlow deep dive](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/) — تفاصيل البنية الداخلية والتحكم في الـ Buffer.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بيعتبروا تيارات ساخنة (Hot Streams) لأنهم موجودين وعايشين في الذاكرة وبينتجوا بيانات سواء كان فيه شاشات بتسمع ليهم أو لأ، وبيوزعوا الداتا بنظام الـ Multicast على كل المشتركين. الـ StateFlow وعاء حالة بيحتفظ بآخر قيمة دايماً ومحتاج قيمة ابتدائية، والـ SharedFlow ناقل أحداث مرن تقدر تظبط له حجم الكاش والـ Buffer والتعامل مع الازدحام.",
        "best_answer_ar": "السبب اللي بيخليهم تيارات ساخنة (Hot Streams) هو استقلالية دورة حياتهم عن المشتركين؛ الـ Flow البارد مبيشتغلش إلا لما حد ينادي collect، أما StateFlow و SharedFlow فهم كائنات حية بتبدأ وتفضل شغالة في الـ CoroutineScope بتاعها، وبتبث القيم بالتوازي لجميع المشتركين بنظام الـ Multicast.\n\nالـ `StateFlow` هو وعاء حالة (State Holder) مخصص لحالة الشاشات؛ بيمتلك خاصية أساسية إنه دايماً معاه قيمة حالية جاهزة للقراءة اللحظية عبر `.value`، وبيشترط تمرير قيمة ابتدائية أول ما يتعرف، ولما أي شاشة جديدة تشترك فيه بيبعت لها فوراً آخر حالة تم الوصول إليها، بالإضافة إلى إنه بيلغي التكرار (Conflation) فمبيبعتش الداتا لو القيمة مفيهاش أي تغيير.\n\nأما الـ `SharedFlow` فده ناقل أحداث عام وعالي المرونة؛ مش بيطلب قيمة ابتدائية، وبيديك تحكم كامل في حجم الـ Replay (كم رسالة قديمة تفضل محفوظة للجداد)، وسعة الـ Buffer، وسلوك التعامل مع فيضان البيانات (BufferOverflow) زي إسقاط أقدم رسالة أو تعليق المنتج.\n\nفي الشغل العملي، بنعتمد على StateFlow لعرض حالة الشاشة في الـ ViewModel علشان نضمن ظهورها فوراً بعد تدوير الشاشة، وبنستخدم SharedFlow للأحداث المشتركة أو بنفضل دمج الأحداث جوه كائن الحالة نفسه.",
        "deep_answer_ar": "على مستوى الـ Low-level Implementation في مكتبة الكوروتينات، StateFlow و SharedFlow مبنيين فوق كلاس أساسي اسمه `AbstractSharedFlow`. الكلاس ده بيدير مصفوفة داخلية من الـ Slots اسمها `SharedFlowSlot` و `StateFlowSlot`. لما دالة `emit` بتستدعى، النظام بياخذ Mutex داخلي وبيلف على كل المشتركين المسجلين في المصفوفة ويصحي الـ Continuations بتاعتهم مباشرة بالتوازي.\n\nمن الناحية المعمارية، الـ `StateFlow` هو عملياً تطبيق متخصص من `SharedFlow` مضبوط بإعدادات ثابتة: `replay = 1` و `onBufferOverflow = BufferOverflow.DROP_OLDEST`، مع إضافة شرط فحص التساوي الصارم باستخدام `Any.equals()`. يعني لو أسندت نفس كائن الـ Data Class بنفس القيم، الـ StateFlow بيفحص التساوي وبيرفض استدعاء المشتركين، وده اللي بيحمي Jetpack Compose من الـ Unnecessary Recompositions وبيوفر فريمات الشاشة.\n\nفي المقابل، الـ `SharedFlow` بيوفر بارامترات دقيقة جداً لحل مشاكل الـ Backpressure: بارامتر `replay` بيحدد عدد الرسائل المخزنة للمشتركين الجدد، و `extraBufferCapacity` بيدي مساحة إضافية لتخزين الرسائل لو كان فيه مستهلك بطيء، و `onBufferOverflow` بيحدد هل نعلق الكوروتين بـ SUSPEND، ولا نسقط أقدم رسالة بـ DROP_OLDEST، ولا نسقط الرسالة الجديدة بـ DROP_LATEST.\n\nوفي بيئات الإنتاج، الـ Staff Engineers بيحذروا من استخدام SharedFlow للأحداث الفردية الحساسة لو الـ replay كان 0، لأن لو الـ Event خرج والشاشة كانت في حالة Stopped أو بتمر بـ Configuration Change، الحدث هيضيع للأبد بدون أي أثر."
    }
}

# ==========================================
# FLO-04: Compare Flow, StateFlow, SharedFlow, LiveData
# ==========================================
DATA["FLO-04"] = {
    "concept_en": """Modern Android stream primitives span four core abstractions: cold Flow, hot StateFlow, hot SharedFlow, and legacy LiveData. Cold Flow represents passive asynchronous data pipelines executed independently per subscription, ideal for repository disk/network queries. StateFlow is a hot, state-holding coroutine stream with a synchronous value accessor, mandatory initial value, conflation, and single-item replay, designed for presentation state management. SharedFlow is a hot event broadcast bus without initial value requirements, offering configurable replay, buffering, and overflow strategies. LiveData is an older lifecycle-aware observable data holder designed exclusively for the Android main thread. While LiveData handled lifecycle safety natively in XML-based architectures, it lacks native coroutine integration, does not support reactive composition operators without Transformations wrappers, and couples business logic to Android framework dependencies, making StateFlow the definitive modern standard.""",
    "walkthrough_en": """Comparing stream usage across Android application layers:
```kotlin
// 1. Data Layer: Cold Flow emits database/network data on demand
class ProductRepository(private val dao: ProductDao) {
    fun getProducts(): Flow<List<Product>> = dao.observeProducts() // Cold
}

// 2. ViewModel Layer: StateFlow holds UI state, SharedFlow broadcasts one-off events
class ProductViewModel(private val repository: ProductRepository) : ViewModel() {
    // Modern UI State: StateFlow replaces LiveData
    val uiState: StateFlow<ProductUiState> = repository.getProducts()
        .map { ProductUiState.Success(it) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), ProductUiState.Loading)

    // Modern Navigation Event: SharedFlow
    private val _navEvents = MutableSharedFlow<String>()
    val navEvents = _navEvents.asSharedFlow()
}

// 3. UI Layer (Jetpack Compose): Collects with lifecycle awareness
@Composable
fun ProductScreen(viewModel: ProductViewModel) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    // Renders state safely
}
```""",
    "short_en": """Cold Flow is a passive stream that re-executes per collector for data operations. StateFlow is a hot state-holder with an initial value, conflation, and latest-state replay for UI state. SharedFlow is a hot, configurable event bus for broadcasting messages. LiveData is a legacy, main-thread-bound observable holder now superseded by StateFlow.""",
    "structured_en": """To begin with, modern Android architecture categorizes reactive stream primitives into cold streams, hot streams, and framework-bound observables.
From an architectural standpoint, cold Flow operates as a lazy pipeline that executes independently for each subscription, making it the ideal primitive for repository queries in Room and Retrofit. StateFlow functions as a hot state holder that stores a current value, requires an initial state, conflates updates, and replays its latest state to newly attached collectors, serving as the standard replacement for LiveData.
In production scenarios, SharedFlow operates as a hot event broadcast bus without requiring an initial value, offering customizable buffer and replay policies for transient events and notifications. LiveData, by comparison, is an older Android framework observable tightly coupled to the Main thread and Android lifecycle.
As for boundary management, while LiveData provided automatic lifecycle safety in legacy View systems, it lacks pure Kotlin multiplatform support, rich reactive operators, and coroutine primitives. Consequently, modern architectures utilize cold Flow in data layers, StateFlow in presentation layers, and collect via repeatOnLifecycle in the UI.""",
    "deep_senior_en": """At the systems engineering and architectural migration level, transitioning from LiveData to StateFlow represents a shift from framework-coupled UI binding to pure Kotlin coroutine primitives. LiveData was deeply coupled to android.arch.lifecycle, enforcing main-thread delivery via ArchTaskExecutor and relying on active LifecycleOwner observer states. This created architectural leakage: domain layers and repositories could not use LiveData without dragging Android platform classes into pure Kotlin modules, and unit testing required InstantTaskExecutorRule to bypass main-thread looper assertions.
StateFlow eliminates this platform dependency. As a pure Kotlin construct, it runs seamlessly in multiplatform modules (KMP), operates across any CoroutineDispatcher, and integrates natively with standard coroutine operators like flatMapLatest, debounce, and combine.
However, StateFlow is not intrinsically lifecycle-aware. Collecting StateFlow directly inside an Activity or Fragment using lifecycleScope.launch keeps the collector active in the background when the app is minimized, wasting CPU cycles and battery. To match and exceed LiveData's lifecycle safety, Android introduced repeatOnLifecycle and collectAsStateWithLifecycle. When the lifecycle drops below the specified state (like Lifecycle.State.STARTED), repeatOnLifecycle cancels the collecting coroutine, triggering upstream cancellation via WhileSubscribed(5000), and automatically restarts collection when the UI returns to the foreground.
Staff engineers enforce complete deprecation of LiveData in new codebases, migrating legacy implementations to StateFlow for state management and SharedFlow for broadcast messaging.""",
    "meta_ar": {
        "id": "FLO-04",
        "questionAr": "قارن بين Flow و StateFlow و SharedFlow و LiveData مع توضيح حالات الاستخدام.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- المقارنة المعمارية الشاملة بين الأنماط الأربعة من حيث السخونة ودورة الحياة والـ Threading.\n- فهم عيوب LiveData التاريخية وارتباطها بخيط الـ Main واعتمادها على أندرويد.\n- إدراك كيفية توظيف كل تيار في الطبقة المناسبة (Data vs Domain vs Presentation).",
        "why_it_matters_ar": "اختيار الأداة التفاعلية الخاطئة يسبب فوضى معمارية؛ فاستخدام LiveData في طبقات الـ Domain يكسر استقلالية الكود عن نظام أندرويد ويعطل الـ Kotlin Multiplatform، واستخدام Flow العادي في الواجهة يكرر الاتصالات، بينما يمثل StateFlow المعيار الحديث المتفق عليه مع Jetpack Compose.",
        "worked_example_ar": "توزيع التيارات الأربعة بحسب الطبقات المعمارية في التطبيق:\n```kotlin\n// 1. Data Layer: استخدام Flow العادي لجلب البيانات عند الطلب:\nfun getFeed(): Flow<List<Post>> = roomDao.getPostsFlow()\n\n// 2. ViewModel: استخدام StateFlow لحفظ حالة الشاشة واستبدال LiveData:\nval uiState: StateFlow<UiState> = repository.getFeed()\n    .map { UiState.Content(it) }\n    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), UiState.Loading)\n\n// 3. ViewModel: استخدام SharedFlow لإرسال أحداث الملاحة بين الشاشات:\nval navEvents = MutableSharedFlow<NavTarget>()\n```",
        "trade_offs_ar": "الـ LiveData كانت ممتازة في بساطة مراقبة دورة الحياة تلقائياً للواجهات القديمة، لكنها مقيدة بالـ Main thread وتفتقر للمشغلات المعقدة. الـ StateFlow يتفوق في كل شيء مع Kotlin الخالص والتوافق مع Compose، ولكنه يتطلب استخدام `repeatOnLifecycle` لضمان أمان دورة الحياة.",
        "failure_modes_ar": "جمع StateFlow في الشاشة باستخدام `lifecycleScope.launch` بدون `repeatOnLifecycle`، مما يجعل الجمع مستمراً في الخلفية بعد خروج المستخدم ويستنزف البطارية. خطأ آخر هو محاولة تشغيل LiveData في ثريدات خلفية عبر `postValue` المتكرر سريعاً مما يسبب سقوط بعض القيم.",
        "production_perspective_ar": "في المشروعات الحديثة، LiveData تعتبر Legacy وممنوعة في الكود الجديد. نستخدم Cold Flow في المستودعات وقواعد البيانات، ونحوله إلى StateFlow في الـ ViewModel لحالة الواجهة، ونجمعه في Compose عبر `collectAsStateWithLifecycle`، ونستخدم SharedFlow للأحداث العامة.",
        "how_to_answer_ar": "- **التصنيف الرباعي:** قسّم الأدوات إلى: بارد (Flow)، ساخن لحالة (StateFlow)، ساخن لأحداث (SharedFlow)، ووعاء قديم مقيد بأندرويد (LiveData).\n- **موقع كل أداة:** Flow للـ Data Layer، و StateFlow للـ Presentation، و SharedFlow لأحداث النظام.\n- **لماذا استبدلنا LiveData:** لأنها مرتبطة بنظام أندرويد والـ Main Thread، بينما StateFlow كود كوتلن خالص يدعم KMP ومشغلات الكوروتينات.\n- **أمان دورة الحياة:** اشرح كيف يعوض `repeatOnLifecycle` ميزة LiveData التلقائية.\n- **منظور Jetpack Compose:** بين التكامل الكامل لـ StateFlow مع Compose.",
        "talking_points_ar": "ناقش ارتباط LiveData بـ ArchTaskExecutor، ومشاكل فقدان القيم في postValue، وتوافق StateFlow مع Kotlin Multiplatform، وحل مشكلة دورة الحياة عبر Lifecycle.repeatOnLifecycle.",
        "follow_ups_ar": "- **المحاور:** \"لماذا نفضل StateFlow على LiveData في المشاريع الحديثة؟\"\n  **المرشح:** \"لأن StateFlow كود Kotlin خالص مستقل عن أندرويد، بيشتغل على أي ثريد، وبيدعم كل مشغلات الكوروتينات التفاعلية زي map و combine، ومتوافق مع Kotlin Multiplatform (KMP) و Jetpack Compose، بعكس LiveData المرتبطة بـ Main Thread وكلاسات أندرويد.\"\n\n- **المحاور:** \"كيف تضمن أن جمع StateFlow في الشاشة لا يستنزف البطارية في الخلفية مثل LiveData؟\"\n  **المرشح:** \"باستخدام دالة `repeatOnLifecycle(Lifecycle.State.STARTED)` أو `collectAsStateWithLifecycle()` في Compose؛ وده بيلغي كوروتين الجمع تلقائياً أول ما الشاشة تروح للخلفية ويعيد تشغيلها فور عودة المستخدم للواجهة.\"",
        "self_check_ar": "هل قارنت بين الأدوات الأربع بدقة؟ هل وضحت عيوب LiveData المعمارية؟ وهل بينت مكان استخدام كل أداة في طبقات التطبيق؟",
        "references_ar": f"- [Migrating from LiveData to StateFlow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow#livedata) — الدليل الرسمي للهجرة.\n- [A safer way to collect flows](https://medium.com/androiddevelopers/a-safer-way-to-collect-flows-from-android-uis-230faf36e3f8) — تفاصيل repeatOnLifecycle في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ Flow العادي بارد ومناسب للـ Data Layer لأنه بيشتغل بالطلب لكل جامع. الـ StateFlow ساخن ومخصص لحالة الواجهة في الـ ViewModel لأنه بيحفظ آخر قيمة ويمنع التكرار. الـ SharedFlow ساخن للأحداث المتنقلة بـ Buffer قابل للتخصيص. أما الـ LiveData فدي أداة قديمة مرتبطة بنظام أندرويد وخيط الـ Main واستبدلناها كلياً بـ StateFlow.",
        "best_answer_ar": "المقارنة بين الأدوات الأربعة بتعتمد على تصنيفهم من حيث طبيعة البث (بارد أم ساخن) والارتباط بنظام أندرويد.\n\nالـ `Flow` العادي هو تدفق بارد وكسول (Cold Stream)؛ مبيشتغلش إلا لما نطلب منه بـ `collect()`، ومثالي جداً لطبقة البيانات (Data Layer) زي قراءة ملفات أو استعلامات Room وطلبات الشبكة.\n\nالـ `StateFlow` هو تيار ساخن (Hot Stream) مخصص لإدارة حالة الشاشة في الـ ViewModel؛ بيحتفظ بآخر قيمة في الذاكرة، وبيطلب قيمة أولية، وبيدمج القيم المتطابقة (Conflation)، وبيمثل البديل العصري والمباشر للـ LiveData في كل تطبيقات كوتلن الحديثة.\n\nالـ `SharedFlow` هو تيار ساخن برضه، لكنه مخصص لبث الأحداث والرسائل (Events Bus)؛ ملوش قيمة أولية افتراضية، وبيديك تحكم كامل في حجم الـ Replay وسعة الـ Buffer للتعامل مع الأحداث المشتركة بين عدة أطراف.\n\nأما الـ `LiveData` فدي أداة قديمة ومقيدة؛ كانت كويسة زمان علشان متابعة دورة الحياة تلقائياً، لكن عيبها القاتل إنها مربوطة بكلاسات أندرويد والـ Main Thread، ومبتدعمش مشغلات الكوروتينات التفاعلية. علشان كده في المشروعات الحديثة بنستبدلها تماماً بـ StateFlow وبنستخدم `repeatOnLifecycle` لضمان نفس أمان دورة الحياة وأكتر.",
        "deep_answer_ar": "على المستوى المعماري العميق، التحول من LiveData لـ StateFlow هو تحول من إطار عمل مقيد بالمنصة إلى كود Kotlin خالص متوافق مع KMP و Clean Architecture. الـ LiveData كانت بتعتمد داخلياً على `ArchTaskExecutor` وبترغم أي تحديث على المرور بخيط الـ Main عبر `postValue`، وده كان بيعمل مشاكل تتابع للبيانات لأن لو أرسلت قيمتين متتاليتين بسرعة قبل ما خيط الـ Main يسحب، القيمة الأولى كانت بتسقط وتضيع.\n\nبالإضافة لكده، استخدام LiveData في طبقات الـ Domain كان بيجبر المطورين على تضمين تبعيات أندرويد جوه كود الـ Pure Kotlin، وكان بيتطلب JUnit Rules خاصة زي `InstantTaskExecutorRule` علشان الاختبارات متضربش كراش بسبب غياب الـ Main Looper.\n\nالـ StateFlow بيحل كل المشاكل دي؛ هو كود Kotlin خالص شغال على أي Thread وبيدعم كل مشغلات الكوروتينات زي `flatMapLatest` و `debounce` و `combine`. لكن التحدي الوحيد فيه إنه مكنش مدرك لدورة حياة الشاشة (Lifecycle-unaware) تلقائياً زي LiveData.\n\nعلشان كده فريق أندرويد في جوجل قدم أداتين قياسيتين: `repeatOnLifecycle` للـ Views العادية و `collectAsStateWithLifecycle` لـ Jetpack Compose. الدوال دي بتراقب حالة الـ LifecycleOwner؛ وأول ما تنزل تحت STARTED، بتلغي كوروتين التجميع وتفعل استراتيجية `WhileSubscribed(5000)` لإيقاف التدفق العلوي وتوفير موارد المعالج والبطارية بنسبة 100%."
    }
}

# ==========================================
# FLO-05: MutableStateFlow initial value
# ==========================================
DATA["FLO-05"] = {
    "concept_en": """MutableStateFlow mandates an initial value by fundamental architectural definition because it represents a state-holder rather than a transient event stream. In software engineering, state is defined as a continuous, always-present condition: an application screen or component is never in a state of 'nothingness'; it is either uninitialized, loading, displaying content, or presenting an error. By requiring an initial value in its constructor, MutableStateFlow guarantees that its synchronous value property is non-null and immediately readable by any consumer without blocking or suspending. This design contract ensures that new collectors attaching to the StateFlow instantly receive a valid state snapshot—such as UiState.Loading—eliminating the race conditions, flashing uninitialized screens, and nullability assertions that historically plagued asynchronous data observation in mobile architectures.""",
    "walkthrough_en": """Illustrating the safety of mandatory initial state in a ViewModel:
```kotlin
// Explicit state modeling: always begins in a well-defined Loading condition
sealed interface ProfileUiState {
    data object Loading : ProfileUiState
    data class Content(val username: String, val email: String) : ProfileUiState
    data class Error(val message: String) : ProfileUiState
}

class ProfileViewModel(private val repository: ProfileRepository) : ViewModel() {
    // MutableStateFlow enforces that a valid state is available from millisecond zero:
    private val _uiState = MutableStateFlow<ProfileUiState>(ProfileUiState.Loading)
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    init {
        loadUserProfile()
    }

    private fun loadUserProfile() {
        viewModelScope.launch {
            _uiState.value = repository.fetchProfile()
                .fold(
                    onSuccess = { ProfileUiState.Content(it.name, it.email) },
                    onFailure = { ProfileUiState.Error(it.localizedMessage ?: "Unknown error") }
                )
        }
    }
}
```""",
    "short_en": """MutableStateFlow requires an initial value because it represents state, which is continuous and always exists. This guarantees that its synchronous value getter is always non-null and valid. When UI components or rotated screens collect the stream, they instantly receive a deterministic state (like Loading) without waiting or crashing on uninitialized values.""",
    "structured_en": """To begin with, MutableStateFlow enforces an initial value by fundamental architectural design.
From an architectural standpoint, state represents a persistent snapshot of an application component. Unlike discrete events that occur momentarily and vanish, state is continuous and always present; a screen is never in a void, it is fundamentally loading, idle, populating data, or displaying an error.
In production scenarios, requiring an initial value guarantees the integrity of StateFlow's synchronous value getter. Any consumer can query stateFlow.value at any millisecond without suspension, knowing with compile-time certainty that a valid state instance exists.
As for boundary management, this requirement completely eliminates initial nullability ambiguity and UI render flickers. When a newly created Activity or recomposing Composable attaches to the StateFlow, it immediately receives this initial state, allowing the interface to render a loading spinner or shimmer skeleton instantly while background asynchronous fetches resolve.""",
    "deep_senior_en": """At the lower typing and synchronization level of the Kotlin standard library, StateFlow is modeled around the invariant that state must be non-nullable unless explicitly typed as StateFlow<T?>. In legacy LiveData, observing a newly constructed instance yielded null until setValue or postValue was executed. This forced developers to write defensive null-checks or handle uninitialized edge cases throughout View binding layers.
StateFlow formalizes this contract through StateFlowSlot. Each slot maintains an internal index tracking whether the collector has received the current head element. Because MutableStateFlow initializes with a non-null head value in heap memory, newly registered collector slots immediately observe that head value on their very first suspension pass.
Furthermore, this mandatory initialization powers the stateIn operator. When converting cold upstream flows via stateIn(scope, started, initialValue), the caller must provide an initialValue. This guarantees that between the moment the ViewModel is instantiated and the moment the upstream database or network cold flow emits its first item, downstream UI composables do not hang or crash; they render the explicit initialValue without hesitation.
Staff engineers leverage this to model explicit sealed state hierarchies: initializing with UiState.Loading or UiState.Idle guarantees clean unidirectional data flow (UDF) transitions, enforces exhaustive when expressions in the UI, and prevents undefined intermediate states across the entire application lifecycle.""",
    "meta_ar": {
        "id": "FLO-05",
        "questionAr": "لماذا يتطلب MutableStateFlow قيمة ابتدائية إجبارية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- الفهم المعماري لمفهوم الحالة (State) كقيمة مستمرة ودائمة الوجود.\n- إدراك أهمية الوصول المتزامن للخاصية `stateFlow.value` بدون تعليق أو Nullability.\n- تفادي شاشات الوميض والغموض البرمجي الذي كان يحدث في LiveData غير المهيأة.",
        "why_it_matters_ar": "الحالة في واجهات المستخدم لا يمكن أن تكون 'فراغاً'؛ فالشاشة إما في حالة تحميل أو عرض محتوى أو خطأ. إجبار المطور على وضع قيمة ابتدائية يمنع أخطاء NullPointerException ويضمن أن أي شاشة تفتح أو يعاد تدويرها تجد حالة جاهزة للعرض فوراً بدون انتظار أو وميض بصري مزعج.",
        "worked_example_ar": "تهيئة الـ StateFlow بحالة تحميل صريحة تمنع أي غموض برمجياً:\n```kotlin\nsealed interface ScreenState {\n    data object Loading : ScreenState // الحالة الابتدائية الحتمية\n    data class Success(val data: String) : ScreenState\n}\n\n// إجبار تمرير Loading يضمن أن الواجهة ترسم الـ Spinner فوراً:\nval uiState = MutableStateFlow<ScreenState>(ScreenState.Loading)\n```\nأي مراقب يستدعي `uiState.value` سيحصل فوراً على `ScreenState.Loading` بدون أي تأخير.",
        "trade_offs_ar": "اشتراط قيمة ابتدائية يفرض على المطور تصميم Sealed Class يمثل حالة التحميل أو القيمة الافتراضية، وهو ما يتطلب كوداً إضافياً بسيطاً، ولكنه في المقابل يمنح التطبيق أماناً نوعياً تاماً ويقضي على الـ Null Safety الحائر في الواجهة.",
        "failure_modes_ar": "محاولة الالتفاف على الشرط بوضع `MutableStateFlow<Type?>(null)`، مما يعيد التطبيق لمصيدة الـ Nullability القديمة ويجبر الواجهة على فحص الـ Null في كل سطر. الحل الصحيح هو نمذجة الحالة كـ Sealed Interface يحتوي على Loading أو Idle.",
        "production_perspective_ar": "في تطبيقات الإنتاج الضخمة، نمنع نهائياً استخدام Nullable StateFlows لحالة الشاشة. نصمم State Class محكم يبدأ بـ `Loading`، مما يتيح للـ Compose UI عرض Shimmer Skeleton فوراً بينما يقوم الـ Repository بجلب البيانات من الكاش أو السيرفر.",
        "how_to_answer_ar": "- **المفهوم الفلسفي للحالة:** الحالة شيء مستمر ودائم الوجود وليست حدثاً عابراً؛ الشاشة دائماً في وضع محدد (تحميل، نجاح، خطأ).\n- **الوصول المتزامن:** StateFlow يوفر خاصية `.value` للقراءة المباشرة بدون suspend، ولا بد من وجود قيمة صالحة لقراءتها.\n- **تجربة المستخدم:** منع وميض الشاشة الفارغة وتوفير حالة أولية زي Loading لرسمها فوراً.\n- **مقارنة بـ LiveData:** كانت تبدأ بفراغ وتسبب NullPointerException أو تضارب في الشاشات الأولى.\n- **أفضل ممارسة:** استخدام Sealed Class وتجنب تمرير `null` كقيمة ابتدائية.",
        "talking_points_ar": "ناقش مصفوفة StateFlowSlot وكيف تقرأ أول عنصر فوراً، ودور القيمة الابتدائية في مشغل `stateIn` لسد الفجوة الزمنية قبل أول انبعاث من التدفق البارد، وتطبيق نمط Unidirectional Data Flow.",
        "follow_ups_ar": "- **المحاور:** \"لو معنديش داتا جاهزة في البداية، هل أعمل `MutableStateFlow<Data?>(null)`؟\"\n  **المرشح:** \"ممكن تقنياً، لكن معمارياً ده مضاد للأنماط النظيفة (Anti-pattern) لأنه بيرجعنا لمشاكل فحص الـ Null. الحل الأفضل هو استخدام Sealed Interface بيمثل الحالة، وتكون القيمة الابتدائية هي كائن `UiState.Loading` صريح.\"\n\n- **المحاور:** \"كيف تفيد القيمة الابتدائية عند استخدام مشغل `stateIn` مع تدفق بارد بطيء؟\"\n  **المرشح:** \"مشغل `stateIn` بيلزمك بقيمة ابتدائية لأن التدفق البارد القادم من الداتابيز أو الشبكة بيحتاج وقت لحد ما يجيب أول عنصر، فالقيمة الابتدائية بتسد الفجوة دي فوراً وتخلي الـ Composable يرسم الـ Loading بدون ما الشاشة تتجمد أو تنتظر.\"",
        "self_check_ar": "هل بينت المفهوم الفلسفي لدوام الحالة؟ هل شرحت دور القراءة المتزامنة لـ `.value`؟ وهل حذرت من استخدام `null` كمهرب من التهيئة؟",
        "references_ar": f"- [StateFlow documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/) — التوثيق الرسمي لخصائص StateFlow.\n- [UI State production modeling](https://developer.android.com/topic/architecture/ui-layer#define-ui-state) — نمذجة حالة الواجهة في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "لأن الـ StateFlow بيمثل حالة (State) والحالة بطبيعتها مستمرة وموجودة دايماً؛ الشاشة مفيش لحظة بتكون فيها في العدم، هي إما بتحمل أو بتعرض داتا أو خطأ. وكمان علشان خاصية `stateFlow.value` متزامنة ولازم ترجع قيمة صالحة فوراً بدون ما تعلق الكود أو ترجع null، وده بيمنع وميض الواجهة وكراشات الـ Null.",
        "best_answer_ar": "اشتراط القيمة الابتدائية في `MutableStateFlow` هو قرار معماري مقصود ومحوري لنظام إدارة الحالة.\n\nالـ StateFlow بيمثل حالة (State)، ومفهوم الحالة في هندسة البرمجيات بيعني لقطة مستمرة ودائمة الوجود للنظام؛ شاشة التطبيق يستحيل تكون في حالة 'فراغ'، هي دايماً إما في حالة تحميل أو بتعرض محتوى أو بتظهر رسالة خطأ.\n\nالسبب التقني التاني هو إن StateFlow بيوفر وصولاً متزامناً للقيمة الحالية عبر خاصية `.value` بدون الحاجة لدوال معلقة (Suspend). فعلشان كوتلن تضمن إن القراءة دي تكون Type-safe وخالية من الـ Null بدون أي احتمال للكراش، كان لازم تفرض وجود قيمة صالحة من أول ملي ثانية لإنشاء الكائن.\n\nده بيفيدنا جداً في تجربة المستخدم؛ أول ما الشاشة تفتح أو يعاد تدويرها، الـ Composable أو الـ Activity بتستلم القيمة الابتدائية دي فوراً (زي Loading) وترسم الـ Spinner أو الـ Skeleton في نفس اللحظة بدون أي وميض أو شاشات بيضاء، لحد ما داتا الشبكة توصل في الخلفية.",
        "deep_answer_ar": "على مستوى الـ Memory Model وهيكل الكوروتينات الداخلي، الـ `StateFlow` متصمم حول مبدأ الـ Non-null State Invariant ما لم يعرف المطور النوع صراحة كـ Nullable. في مكتبة LiveData القديمة، الكائن كان بيبدأ فاضي تماماً، وده كان بيخلي أول قراءة ترجع null ويجبر المطورين على كتابة كود فحص دفاعي مليان أخطاء في كل طبقات الواجهة.\n\nالـ `StateFlowSlot` الداخلي بيدير مؤشر قراءة لكل مشترك بيتحقق من وصوله لأحدث Head Element في الذاكرة. وجود قيمة ابتدائية بيضمن إن أول لفة فحص للـ Slot تلاقي كائن صالح في الـ Heap بدون ما تحتاج تعلق المشترك أو تدخله في طابور انتظار.\n\nالأهم من كده هو تكامل الخاصية دي مع مشغل `stateIn`؛ لما بنحول تيار بارد جاي من Room أو السيرفر عبر `stateIn(scope, started, initialValue)`، القيمة الابتدائية دي هي اللي بتسد الفجوة الزمنية الحرجة بين لحظة فتح الشاشة ولحظة وصول أول رد من الداتابيز، فالواجهة بتعرض Loading بشكل حتمي ومتوقع.\n\nبالإضافة لكده، ده بيضمن في الـ Unit Tests إن الاختبارات تبدأ من حالة قاعدية متوقعة ومستقرة، وتقدر تفحص `viewModel.uiState.value` فوراً بعد الإنشاء وتتأكد إنها في حالة التحميل قبل بدء أي أحداث محاكاة.\n\nوفي المشروعات الضخمة، بنمنع تماماً استخدام `MutableStateFlow<T?>(null)` كمهرب من التهيئة، وبنفرض استخدام Sealed Hierarchy بيبدأ بـ `UiState.Loading` لضمان سريان نمط الـ Unidirectional Data Flow (UDF) بدون أي حالات غير معرفة."
    }
}

# ==========================================
# FLO-06: Conflation & equality suppression
# ==========================================
DATA["FLO-06"] = {
    "concept_en": """Conflation and equality-based suppression are StateFlow's primary performance optimizations designed to eliminate redundant processing and UI frame drops. Conflation is a backpressure mitigation strategy where intermediate emissions are automatically discarded if a collector is slower than the emitter; the collector skips older unconsumed states and receives only the most recent update. Equality suppression operates at the mutation boundary: whenever a new value is assigned to MutableStateFlow.value, StateFlow performs a structural equality check using Any.equals. If the incoming value is structurally equal to the currently stored state, the assignment is discarded immediately: the state does not change, collector slots are not notified, and no downstream emissions occur. In modern Android applications utilizing Jetpack Compose, this prevents unnecessary recomposition cycles and ensures that the UI renders only when observable data has genuinely mutated.""",
    "walkthrough_en": """Demonstrating equality suppression and rapid conflation in action:
```kotlin
data class FeedState(val count: Int, val title: String)

suspend fun demonstrateConflationAndEquality() = coroutineScope {
    val state = MutableStateFlow(FeedState(1, "News"))

    val job = launch {
        state.collect { item ->
            println("Collected: $item")
            delay(100) // Simulates slow UI processing
        }
    }

    delay(20)
    // 1. Equality suppression: Identical value is completely ignored
    state.value = FeedState(1, "News") // EQUALS current -> Discarded, prints nothing!

    // 2. Conflation: Rapid emissions while collector is suspended at delay(100)
    state.value = FeedState(2, "News") // Discarded!
    state.value = FeedState(3, "News") // Discarded!
    state.value = FeedState(4, "News") // Retained as the latest head

    delay(200)
    job.cancel()
    // Output:
    // Collected: FeedState(count=1, title=News)
    // Collected: FeedState(count=4, title=News) (States 2 and 3 were conflated!)
}
```""",
    "short_en": """Conflation and equality suppression prevent redundant UI rendering in StateFlow. Equality suppression uses Any.equals to discard incoming values identical to the current state, preventing unnecessary emissions. Conflation drops intermediate states when a collector is slow, guaranteeing that the collector always receives the freshest available state without buffer overflow.""",
    "structured_en": """To begin with, conflation and equality suppression represent StateFlow's core performance optimizations for state rendering.
From an architectural standpoint, equality suppression prevents redundant work at the mutation boundary. When a new value is assigned to MutableStateFlow, it evaluates structural equality via Any.equals against the current state. If the values are identical, the assignment is dropped immediately; collector continuations are not woken up, and downstream streams remain idle.
In production scenarios, conflation handles consumer-producer speed mismatches. When an upstream data source emits state updates faster than the UI can process or render them, StateFlow does not buffer intermediate values. Instead, it conflates the stream, dropping older pending states so the collector always receives the freshest state snapshot.
As for boundary management, these mechanisms are essential for Jetpack Compose stability. They prevent recomposition loops and frame drops when ViewModels compute state updates that resolve to identical data classes, guaranteeing smooth sixty or one-hundred-twenty hertz UI rendering.""",
    "deep_senior_en": """Under the hood in StateFlow.kt, the assignment of a new value executes inside a synchronized block operating on the StateFlow instance. The implementation first checks: if (curValue == newState) return. This structural comparison relies on the implementation of equals() provided by data classes. If the comparison returns true, the method terminates early without incrementing the internal sequence version counter or notifying attached StateFlowSlots.
This optimization introduces a critical architectural pitfall: mutable reference modification. If a developer mutates a property inside a mutable object or collection held by StateFlow (such as modifying an existing ArrayList or changing a var inside a class) and reassigns that same instance to StateFlow.value, curValue == newState evaluates to true because both reference handles point to the identical heap object. Consequently, StateFlow suppresses the emission, and the UI completely fails to update. StateFlow mandates strictly immutable data structures (data classes with val properties and immutable collections).
Conflation operates via StateFlowSlot's sequence number tracking. Each slot tracks the sequence of the last processed value. When the collector resumes, it fetches the value associated with the current sequence number. If five updates occurred while the collector was suspended, the collector simply reads the latest value, inherently conflating the intermediate four.
Staff engineers leverage this to protect UI performance: pairing immutable state models with StateFlow ensures zero redundant Compose passes and guarantees lag-free state tracking under high-frequency background event bursts.""",
    "meta_ar": {
        "id": "FLO-06",
        "questionAr": "ما هو الـ Conflation؟ وكيف يستخدم StateFlow فحص التساوي لمنع تكرار الحالة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- فهم معنى الـ Conflation وإسقاط القيم الوسيطة عند بطء المستهلك.\n- إدراك آلية فحص التساوي البنيوي (Structural Equality via Any.equals) في StateFlow.\n- معرفة مأزق تعديل الكائنات المتبدلة (Mutable Objects) وفشل تحديث الواجهة بسبب تطابق المراجع.",
        "why_it_matters_ar": "الـ Conflation وفحص التساوي هما صمام الأمان لأداء واجهات أندرويد؛ بدونهما ستتعرض الواجهة لآلاف عمليات إعادة الرسم (Recomposition) غير الضرورية لحالات متطابقة، أو يتجمد التطبيق بسبب تراكم آلاف القيم الوسيطة في الذاكرة عند تدفق بيانات سريع من المستشعرات.",
        "worked_example_ar": "توضيح إسقاط القيم المتطابقة وتجاوز القيم الوسيطة السريعة:\n```kotlin\nval state = MutableStateFlow(UserState(id = 1, name = \"Ali\"))\n\n// 1. فحص التساوي: إسناد نفس البيانات يتم تجاهله تماماً ولا يوقظ الواجهة:\nstate.value = UserState(id = 1, name = \"Ali\") // Discarded! equals == true\n\n// 2. الدمج السريع (Conflation): لو انبعثت قيم سريعة والمستهلك مشغول:\nstate.value = UserState(id = 1, name = \"Omar\") // تسقط لو المستهلك بطيء\nstate.value = UserState(id = 1, name = \"Zaid\") // المستهلك يستلم أحدث قيمة فقط فور تفرغه\n```",
        "trade_offs_ar": "الـ Conflation ممتاز لحالة الشاشات لأنه يضمن عرض أحدث قيمة دائماً، ولكنه غير مناسب إطلاقاً للأحداث الحسابية أو المعاملات المالية التي تتطلب معالجة كل عنصر بالترتيب دون إسقاط أي خطوة.",
        "failure_modes_ar": "تعديل خاصية `var` داخل كائن State مع الاحتفاظ بنفس المرجع، ثم إسناده للـ StateFlow؛ حيث سيفحص المترجم المرجع ويجده مساوياً لنفسه (`old == new`) فيتجاهل التحديث تماماً ولا تتحدث الشاشة. الحل هو استخدام data classes بخواص `val` واستدعاء `copy()`.",
        "production_perspective_ar": "في تطبيقات Compose الحديثة، نعتمد على كلاسات بيانات غير قابلة للتعديل (Immutable Data Classes) مع مكتبة `kotlinx.collections.immutable`. فحص التساوي في StateFlow مع استقرار Compose يمنعان إعادة رسم القوائم إذا لم تتغير البيانات، مما يوفر 60 فريماً ثابتاً في الثانية.",
        "how_to_answer_ar": "- **تعريف Conflation:** آلية دمج وإسقاط القيم الوسيطة عند بطء المستهلك لضمان استلام أحدث لقطة فقط.\n- **فحص التساوي (Equality Suppression):** فحص `Any.equals` الصارم عند إسناد قيمة جديدة؛ لو مطابقة للحالية يتم تجاهلها فوراً دون إبلاغ المشتركين.\n- **الفائدة الهندسية:** حماية الأداء وتفادي إعادة الرسم غير الضرورية (Recomposition Skipping) في Compose.\n- **المأزق القاتل:** تعديل كائن Mutable داخلياً يخدع فحص التساوي ويمنع تحديث الشاشة.\n- **القاعدة الصارمة:** استخدام Data Classes غير قابلة للتعديل (val) والنسخ عبر `copy()`.",
        "talking_points_ar": "ناقش الكود المصدري لـ StateFlow.kt والتحقق من `curValue == newState`، ودور عداد الـ Sequence Number في StateFlowSlot لإسقاط القيم القديمة، والتكامل مع Compose Compiler Stability.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لو عدلت عنصر في `ArrayList` جوه StateFlow وأعدت إسناد نفس القائمة للـ `.value`؟\"\n  **المرشح:** \"الشاشة مش هتتحدث نهائياً؛ لأن StateFlow بيقارن المرجع الجديد بالقديم بـ equals، ولأنهم نفس الكائن في الـ Heap فالنتيجة هتكون true، وهيعتبر مفيش تغيير ويكتم الانبعاث. الحل هو استخدام كائنات غير قابلة للتعديل وعمل نسخة جديدة بـ toList() أو PersistentList.\"\n\n- **المحاور:** \"هل Conflation ممكن يسبب ضياع بيانات للمستخدم؟\"\n  **المرشح:** \"لو بتستخدمه مع حالة الشاشة (State) مش بيضيع حاجة، لأن المستخدم يهمه يشوف أحدث وضع فقط. لكن لو بتستخدمه مع أحداث متتالية زي نقرات شراء أو معاملات دفع، فالـ Conflation هيسقط العمليات الوسيطة، وعلشان كده بنستخدم Channels أو SharedFlow للأحداث دي.\"",
        "self_check_ar": "هل فرقت بين Conflation وفحص التساوي؟ هل شرحت مأزق الـ Mutable Object بالتفصيل؟ وهل بينت دوره في حماية أداء Compose؟",
        "references_ar": f"- [StateFlow conflation details](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/) — التوثيق الرسمي لآلية Conflation.\n- [Compose stability and equality](https://developer.android.com/develop/ui/compose/performance/stability) — استقرار الكلاسات وتفادي إعادة الرسم.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ Conflation هو إسقاط الحالات الوسيطة لو المشترك بطيء، علشان يستلم دايماً أحدث قيمة موجودة بدون تأخير. أما فحص التساوي فده فحص بـ `equals` بيعمله StateFlow أول ما تسند قيمة جديدة؛ لو مطابقة للقيمة الحالية بيكتمها تماماً ومبيصحيش المشتركين، وده بيمنع إعادة رسم الواجهة بدون داعٍ ويحمي فريمات الشاشة.",
        "best_answer_ar": "الـ Conflation وفحص التساوي هما أهم ميزتين بيخلوا StateFlow الأداة المثالية لإدارة حالة الواجهة في أندرويد.\n\nالـ `Conflation` وظيفته حل مشكلة التفاوت في السرعة بين المنتج والمستهلك؛ لو الباك جراوند بتبعت 10 تحديثات سريعة في ثانية واحدة، والشاشة مشغولة في رسم فريم، الـ StateFlow مش بيخزن الـ 10 حالات في طابور، هو ببساطة بيسقط الحالات الوسيطة القديمة وبيسلم الشاشة أحدث حالة وصلت فور تفرغها، وده منطقي لأن المستخدم ميهموش يشوف الحالات القديمة المؤقتة.\n\nأما فحص التساوي (Equality Suppression)، فده بيحصل عند لحظة إسناد القيمة لـ `MutableStateFlow.value`؛ النظام بيفحص هل القيمة الجديدة مطابقة للقيمة الحالية عبر `Any.equals()`. لو لقاهما متطابقين، بيلغي العملية فوراً ومش بيصحي أي مشترك، وده بيحمي Jetpack Compose من الـ Recompositions غير الضرورية.\n\nولازم ننبه لمأزق قاتل: لو كائن الـ State كان جواه متغيرات `var` أو قائمة `ArrayList` عادية، والمطور عدل عنصر في القائمة وأسند نفس الكائن، الـ StateFlow هيلاقي المرجع القديم هو نفس الجديد (`old == new`) ومش هيحدث الشاشة نهائياً! علشان كده بنلزم استخدام Data Classes بخصائص `val` واستدعاء `copy()`.",
        "deep_answer_ar": "على مستوى الكود المصدري داخل `StateFlow.kt`، إسناد قيمة جديدة بيتم داخل synchronized block بيفحص أولاً: `if (curValue == newState) return`. المقارنة دي بتعتمد على كود الـ equals المولد في الـ Data Classes. لو الشرط تحقق، الدالة بتنتهي فوراً بدون زيادة عداد الـ Sequence الداخلي وبدون إشعار أي عقدة في مصفوفة المشتركين.\n\nالخاصية دي بتلعب دور حاسم في Jetpack Compose Compiler؛ لما بنمرر StateFlow لكومبوزابل، الـ Compiler بيعتمد على ثبات الكلاس (Stability). فلما نضمن عدم انبعاث قيم متطابقة، الـ Compose Runtime بيعمل Recomposition Skipping للقوائم المعروضة ويوفر عمليات حسابية ضخمة للـ CPU.\n\nأما آلية الـ Conflation، فبتتم من خلال تعقب مؤشر الـ Sequence في كلاس `StateFlowSlot`. كل مشترك بيمتلك slot مسجل فيه رقم آخر لقطة استلمها. لو الكوروتين علقت بسبب delay أو رسم بطيء، وحصلت 5 تعديلات في الـ StateFlow، المشترك أول ما يصحى بيقرا القيمة المقابلة لأحدث Sequence Number مباشرة، وبكده الحالات الأربعة السابقة بيتم تجاوزهم (Conflated) تلقائياً بدون أي تخصيص لذاكرة مؤقتة.\n\nعلشان كده في بيئات الإنتاج، بنفرض استخدام Immutable Collections من مكتبة `kotlinx.collections.immutable`؛ لأن تعديل أي عنصر بينشئ نسخة جديدة بمرجع مختلف ومضمون، وده بيحافظ على فحص التساوي دقيقاً ويضمن تحديث الواجهة بسلاسة وثبات 100%."
    }
}

# ==========================================
# FLO-07: Read-only state via asStateFlow()
# ==========================================
DATA["FLO-07"] = {
    "concept_en": """Exposing read-only state via asStateFlow() is the foundational encapsulation and unidirectional data flow (UDF) pattern in modern Android architecture. In the presentation layer, a ViewModel manages a private, mutable backing property (MutableStateFlow) to mutate internal screen state in response to user actions or domain responses. However, exposing MutableStateFlow publicly violates object-oriented encapsulation and architectural boundaries by allowing external classes—such as Activities, Fragments, Composables, or peer components—to directly mutate the state from the outside. The asStateFlow() extension function solves this by wrapping the mutable instance inside a ReadonlyStateFlow proxy. This read-only abstraction enforces at compile time that only the owning ViewModel holds write privileges, while public consumers can only observe emissions or read the synchronous value property.""",
    "walkthrough_en": """Encapsulating state within an Android ViewModel:
```kotlin
class CheckoutViewModel(private val repository: CheckoutRepository) : ViewModel() {
    // 1. Private mutable state: Only this ViewModel can mutate the backing state
    private val _uiState = MutableStateFlow<CheckoutUiState>(CheckoutUiState.Initial)

    // 2. Public read-only projection: Downstream UI layers can only observe
    val uiState: StateFlow<CheckoutUiState> = _uiState.asStateFlow()

    fun completePurchase() {
        viewModelScope.launch {
            _uiState.value = CheckoutUiState.Processing
            val result = repository.submitOrder()
            _uiState.value = result.fold(
                onSuccess = { CheckoutUiState.Success(it.orderId) },
                onFailure = { CheckoutUiState.Error(it.message ?: "Failed") }
            )
        }
    }
}

// In the UI Layer (Activity / Composable):
// viewModel.uiState.value = CheckoutUiState.Success("fake") // COMPILE ERROR! Read-only.
```""",
    "short_en": """asStateFlow() wraps a private MutableStateFlow into a read-only StateFlow, preventing external layers from mutating ViewModel state. This enforces unidirectional data flow (UDF) and encapsulation, ensuring that the ViewModel remains the single source of truth and the only component with write privileges.""",
    "structured_en": """To begin with, exposing state via asStateFlow() enforces encapsulation and unidirectional data flow.
From an architectural standpoint, the ViewModel must maintain exclusive ownership over its state transitions. By declaring MutableStateFlow as a private backing property and exposing a public read-only StateFlow using asStateFlow(), we establish a compile-time boundary preventing external components from modifying state.
In production scenarios, allowing UI layers or testing utilities to mutate state directly creates chaotic multi-directional mutations, introduces race conditions, and complicates state debugging. When state mutates strictly through ViewModel member functions, business logic remains centralized, testable, and auditable.
As for boundary management, asStateFlow() returns a ReadonlyStateFlow instance that intercepts casting attempts. Merely declaring val uiState: StateFlow = _uiState without asStateFlow() allows malicious or erroneous code to downcast the reference back to MutableStateFlow at runtime, whereas asStateFlow() guarantees immutable encapsulation.""",
    "deep_senior_en": """At the compiler and runtime API boundary level, the difference between a direct upcast and asStateFlow() represents a vital defense against reflection and unsafe type casting. In naive implementations, developers write: val uiState: StateFlow<T> get() = _uiState. Because MutableStateFlow implements the StateFlow interface directly, the runtime instance remains an instance of MutableStateFlowImpl. A consumer can write (viewModel.uiState as MutableStateFlow).value = newState, successfully bypassing encapsulation and mutating state externally.
The asStateFlow() extension function specifically mitigates this by wrapping the mutable instance in an internal ReadonlyStateFlow wrapper. ReadonlyStateFlow implements StateFlow and CancellableFlow, delegating collect and value calls to the wrapped instance while concealing the MutableStateFlow interface entirely. An unsafe downcast to MutableStateFlow throws a runtime ClassCastException, closing the vulnerability.
Furthermore, this pattern guarantees the Unidirectional Data Flow (UDF) lifecycle contract: State flows down from the ViewModel to the UI, and Events flow up from the UI to the ViewModel. If the UI could mutate the state directly, state consistency models would shatter, making automated UI testing and bug reproduction nearly impossible.
This discipline ensures that testing harnesses and UI previews interact strictly with predictable read contracts, while mutations remain isolated to explicit, testable ViewModel intent handlers.
Staff engineers enforce this via Detekt and Android Lint rules: flagging any public MutableStateFlow or MutableSharedFlow property as an architectural violation across all repository, use case, and presentation layers.""",
    "meta_ar": {
        "id": "FLO-07",
        "questionAr": "كيف تكشف حالة القراءة فقط عبر asStateFlow()؟ ولماذا تعتبر هذه الممارسة ضرورية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- تطبيق مبدأ الـ Encapsulation ونمط الـ Unidirectional Data Flow (UDF).\n- التمييز بين Upcast العادي وبين التغليف الحقيقي بكائن ReadonlyStateFlow.\n- حماية الحالة من التعديل الخارجي وتفادي كسر أحادية مصدر الحقيقة في الـ ViewModel.",
        "why_it_matters_ar": "كشف الـ MutableStateFlow للعامة يسمح لأي كود في الشاشة أو كلاس خارجي بتعديل حالة التطبيق مباشرة، مما يكسر مبدأ المصدر الوحيد للحقيقة (Single Source of Truth) ويخلق سباقات بيانات وأخطاء عشوائية مستحيلة التتبع في بيئات الإنتاج.",
        "worked_example_ar": "النمط القياسي لعزل الحالة القابلة للتعديل خلف واجهة قراءة فقط:\n```kotlin\nclass CartViewModel : ViewModel() {\n    // متغير خاص قابل للتعديل داخل هذا الكلاس فقط:\n    private val _uiState = MutableStateFlow<CartState>(CartState.Empty)\n\n    // واجهة قراءة فقط مكشوفة للواجهة عبر asStateFlow:\n    val uiState: StateFlow<CartState> = _uiState.asStateFlow()\n\n    fun addItem(item: CartItem) {\n        _uiState.value = CartState.Loaded(listOf(item))\n    }\n}\n```\nالواجهة تستطيع مراقبة `uiState` ولكن يستحيل عليها كتابة `uiState.value = ...`.",
        "trade_offs_ar": "استخدام نمط Backing Property مع `asStateFlow()` يضيف سطراً برمجياً إضافياً لكل متغير حالة، ولكنه يمنح المشروع حماية معمارية صارمة وقت البناء (Compile-time Safety) تمنع التعديلات العشوائية تماماً.",
        "failure_modes_ar": "كتابة `val uiState: StateFlow = _uiState` بدون `asStateFlow()`؛ حيث يسمح ذلك لأي كود خارجي بعمل Cast قسري `as MutableStateFlow` وتعديل القيمة. خطأ آخر هو كشف دوال عامة تعدل الحالة بدون التحقق من صحة المدخلات.",
        "production_perspective_ar": "في المشروعات الكبيرة، نكتب قواعد Detekt و ArchUnit مخصصة تفحص الـ ViewModels وتمنع دمج أي PR يكشف كلاسات Mutable للعامة. الحالة تنساب للأسفل للقراءة فقط، وتعديلات المستخدم تصعد للأعلى كأفعال ودوال صريحة (UDF).",
        "how_to_answer_ar": "- **الهدف المعماري:** عزل التعديل داخل الـ ViewModel وحماية مبدأ أحادية تدفق البيانات (UDF).\n- **طريقة التطبيق:** تعريف `_state` خاص بـ MutableStateFlow، وكشف `state` عام كـ StateFlow عبر `asStateFlow()`.\n- **سر دالة asStateFlow:** تغلف الكائن بـ ReadonlyStateFlow لمنع الكاست القسري (Unsafe Cast) الذي ينجح مع الـ Upcast العادي.\n- **مخاطر الكشف المباشر:** فقدان السيطرة على الحالة، صعوبة التتبع، وسباق البيانات بين الواجهات.\n- **أتمتة الفحص:** فرض القاعدة عبر أدوات التحليل الثابت في الـ CI.",
        "talking_points_ar": "ناقش كلاس ReadonlyStateFlow في مكتبة الكوروتينات، ولماذا يفشل الـ ClassCastException في حماية التطبيق لو لم نستخدم الدالة، ودور النمط في تسهيل الـ Unit Testing والـ Mocking.",
        "follow_ups_ar": "- **المحاور:** \"ما الفرق بين `val state: StateFlow = _state` وبين `val state = _state.asStateFlow()`؟\"\n  **المرشح:** \"في الحالة الأولى ده مجرد Upcast؛ الكائن في الذاكرة بيفضل MutableStateFlow وأي حد يقدر يعمل كاست `(state as MutableStateFlow).value = ...` ويعدل الحالة. أما `asStateFlow()` فبتغلف الكائن بكلاس حقيقي اسمه ReadonlyStateFlow يمنع الكاست تماماً ويرمي ClassCastException لو حد حاول يتذاكى.\"\n\n- **المحاور:** \"كيف يخدم هذا النمط مبدأ الـ Unidirectional Data Flow (UDF)؟\"\n  **المرشح:** \"النمط بيضمن إن البيانات تتدفق في اتجاه واحد فقط: الحالة تنزل من الـ ViewModel للشاشة للقراءة فقط، وأي تفاعل من المستخدم بيطلع للـ ViewModel كـ Event أو دالة صريحة، وده بيخلي تتبع الأخطاء واختبار الكود حتمياً بنسبة 100%.\"",
        "self_check_ar": "هل شرحت مبدأ الـ Encapsulation؟ هل وضحت الفرق الدقيق بين Upcast و ReadonlyStateFlow؟ وهل ربطته بنمط الـ UDF؟",
        "references_ar": f"- [Encapsulation in StateFlow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow#stateflow) — أفضل ممارسات كشف الحالة في أندرويد.\n- [Unidirectional Data Flow](https://developer.android.com/topic/architecture/ui-layer#architecture-principles) — مبادئ هندسة الواجهات الحديثة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنكشف الحالة كقراءة فقط باستخدام `asStateFlow()` علشان نطبق مبدأ الـ Encapsulation ونضمن إن الـ ViewModel هو الوحيد صاحب الحق في تعديل حالته. الدالة دي مش مجرد Cast، دي بتغلف الكائن بـ `ReadonlyStateFlow` يمنع أي كود خارجي من التعديل أو عمل Cast قسري، وبتحافظ على نمط تدفق البيانات أحادي الاتجاه (UDF).",
        "best_answer_ar": "نمط الـ Backing Property واستخدام `asStateFlow()` هو حجر الأساس لهندسة الواجهات الحديثة في أندرويد (UDF).\n\nالفكرة المعمارية هي إن الـ ViewModel لازم يكون هو المالك الحصري والمصدر الوحيد للحقيقة (Single Source of Truth) لحالة الشاشة. فعلشان نحقق ده، بنعرف متغير خاص `_uiState` من نوع `MutableStateFlow` يقدر الـ ViewModel يعدل فيه براحته، وبنكشف واجهة عامة `uiState` للقراءة فقط من نوع `StateFlow` باستخدام دالة `asStateFlow()`.\n\nلو كشفنا الـ MutableStateFlow مباشرة، أي Activity أو Composable خارجية هتقدر تعدل في الحالة من ورا ضهر الـ ViewModel، وده بيخلق فوضى معمارية وتضارب في البيانات وسباق خيوط مستحيل تصحيحه في الإنتاج.\n\nوالنقطة الهندسية الدقيقة هي إن استخدام `asStateFlow()` بيغلف الكائن داخلياً بكلاس اسمه `ReadonlyStateFlow`؛ ده بيمنع أي مبرمج من إنه يعمل Unsafe Cast زي `(state as MutableStateFlow).value = ...` لأن النظام هيرمي ClassCastException فوراً، وبكده بنضمن الأمان المعماري بنسبة 100%.",
        "deep_answer_ar": "على مستوى الـ Type System والـ Compiler Internals في Kotlin، الـ `MutableStateFlow` بيورث مباشرة من واجهة `StateFlow`. لو المطور اكتفى بكتابة: `val uiState: StateFlow<T> = _uiState`، ده في الـ Bytecode مجرد Upcast شكلي؛ الكائن الحقيقي في الـ Heap بيفضل `MutableStateFlowImpl`، وده معناه إن أي حد يقدر يعمل Runtime Type Cast ويكتب: `(viewModel.uiState as MutableStateFlow).value = hackedState` والتعديل هينجح بدون أي اعتراض من المترجم.\n\nدالة `asStateFlow()` اتصممت خصيصاً لسد الثغرة دي؛ هي بتغلف الـ instance بكلاس داخلي اسمه `ReadonlyStateFlow`. الكلاس ده بيطبق واجهات `StateFlow` و `CancellableFlow` فقط، وبيحول كل نداءات `collect` و `value` للكائن الأصلي، لكنه مبيطبقش `MutableStateFlow` نهائياً. فلو حد حاول يعمل Downcast، الـ ART هيرمي `java.lang.ClassCastException` فوري ويوقف العبث.\n\nالنمط ده هو الضامن الحقيقي لقاعدة الـ Unidirectional Data Flow (UDF)؛ الحالة بتنساب لأسفل للواجهة كلقطة غير قابلة للتعديل، وإجراءات المستخدم بتصعد لأعلى كـ Events ودوال في الـ ViewModel. ده بيسهل عمل الـ Unit Testing والـ UI Testing جداً لأنك ضامن إن مفيش Side Effect خارجي يقدر يغير حالة الشاشة فجأة بدون المرور بمنطق الـ Business Logic.\n\nوفي الفرق الهندسية الكبيرة، بنضيف قواعد Lint مخصصة تمنع خروج أي خاصية عامة بتبدأ بـ Mutable من أي ViewModel أو Repository لضمان استقرار المشروع."
    }
}

# ==========================================
# FLO-08: What are stateIn and shareIn?
# ==========================================
DATA["FLO-08"] = {
    "concept_en": """The stateIn and shareIn operators in Kotlin coroutines are transformative bridging mechanisms that convert cold, on-demand flows into hot, multicasting streams within a defined CoroutineScope. Cold flows execute independently from scratch for every collector, which causes severe resource duplication when multiple components collect shared database queries or network feeds. The shareIn operator converts a cold flow into a hot SharedFlow, multicasting upstream emissions across multiple subscribers while configuring replay cache size and buffer overflow strategies. The stateIn operator converts a cold flow into a hot StateFlow, enforcing state-holder invariants by requiring an initial value, conflating identical updates, and maintaining a single-item replay cache for immediate snapshot retrieval. Both operators accept a SharingStarted policy parameter governing when upstream production activates and ceases based on subscriber presence.""",
    "walkthrough_en": """Converting a cold database flow into hot presentation streams:
```kotlin
class ProductCatalogViewModel(private val repository: ProductRepository) : ViewModel() {
    // 1. stateIn: Converts cold Flow into hot StateFlow for UI state rendering
    val catalogState: StateFlow<CatalogUiState> = repository.observeProducts()
        .map { CatalogUiState.Success(it) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000), // Grace period for rotation
            initialValue = CatalogUiState.Loading // Immediate fallback state
        )

    // 2. shareIn: Converts cold Flow into hot SharedFlow for broadcast events
    val stockAlerts: SharedFlow<StockAlert> = repository.observeGlobalStockAlerts()
        .shareIn(
            scope = viewModelScope,
            started = SharingStarted.Lazily, // Starts when first subscriber arrives, stays active
            replay = 1 // Keeps the latest alert for new screens
        )
}
```""",
    "short_en": """stateIn and shareIn convert cold flows into hot streams within a CoroutineScope. shareIn produces a SharedFlow that multicasts emissions across multiple collectors with custom replay. stateIn produces a StateFlow that holds a current value, requires an initial state, and conflates updates. Both use SharingStarted strategies to control upstream execution lifecycles.""",
    "structured_en": """To begin with, stateIn and shareIn are conversion operators that transform cold flows into hot, multicasting streams.
From an architectural standpoint, cold flows execute redundantly for every collector. To share a single upstream connection across multiple UI collectors without duplicating network requests or database queries, we bridge the cold stream into a CoroutineScope using these operators.
In production scenarios, we use stateIn when the stream represents UI state. It requires an initial value, maintains a single-item replay cache, conflates identical states, and exposes a synchronous value getter. Conversely, we use shareIn when transforming continuous event streams where customized replay sizes or buffer capacities are required without enforcing an initial state.
As for boundary management, both operators take a SharingStarted strategy. The gold standard for Android UI is SharingStarted.WhileSubscribed(5000), which activates upstream production only while subscribers exist, adding a five-second buffer to bridge screen rotations without tearing down the upstream flow.""",
    "deep_senior_en": """Under the hood, stateIn and shareIn instantiate a specialized CoroutineScope subscription pipeline that collects the cold upstream flow and forwards emissions into an internal Channel-backed buffer. The execution is governed entirely by the SharingStarted policy.
When SharingStarted.Eagerly is configured, the operator launches the upstream collection immediately upon instantiation, keeping the upstream flow alive until the parent CoroutineScope terminates, regardless of whether any subscriber ever collects it. SharingStarted.Lazily defers upstream execution until the very first subscriber attaches, but once started, never suspends even if all subscribers detach.
SharingStarted.WhileSubscribed(stopTimeoutMillis, replayExpirationMillis) implements the most sophisticated lifecycle control. It monitors the active subscriber count in the underlying AbstractSharedFlow. When the subscriber count transitions from zero to one, it launches the upstream collection job. When the subscriber count drops back to zero (such as during Activity onStop or screen rotation), it starts a cancellation timer set to stopTimeoutMillis. If a new subscriber arrives before the timeout expires (e.g., the Activity recreates in landscape within 300ms), the cancellation is aborted, preserving upstream database locks and socket connections. If the timer elapses, the upstream coroutine is cancelled, releasing physical resources and saving battery.
Staff engineers enforce stateIn with WhileSubscribed(5000) at presentation boundaries to bridge cold repository queries into battery-efficient, lifecycle-resilient UI state.""",
    "meta_ar": {
        "id": "FLO-08",
        "questionAr": "ما هما عاملا التحويل stateIn و shareIn؟ وكيف تختار بينهما؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- فهم آلية تحويل التيارات الباردة الكسولة إلى تيارات ساخنة ومشتركة (Cold-to-Hot).\n- التمييز بين إنتاج حالة مستمرة عبر stateIn وإنتاج ناقل أحداث عبر shareIn.\n- استيعاب دور معاملات SharingStarted وضبط مهلة WhileSubscribed(5000).",
        "why_it_matters_ar": "بدون stateIn و shareIn، ستضطر كل شاشة وكل كارت واجهة لتكرار استعلامات قاعدة البيانات أو طلبات الشبكة من الصفر مع كل اشتراك. الاستخدام الصحيح لهذين العاملين يوحد مسار الإنتاج في اشتراك واحد مشترك ويوفر بطارية الهاتف وذاكرة النظام.",
        "worked_example_ar": "تحويل تدفق قاعدة بيانات بارد إلى StateFlow و SharedFlow في الـ ViewModel:\n```kotlin\nclass CatalogViewModel(repository: ProductRepository) : ViewModel() {\n    // تحويل لـ StateFlow لعرض قائمة المنتجات مع قيمة أولية Loading:\n    val uiState: StateFlow<CatalogState> = repository.getProductsFlow()\n        .map { CatalogState.Success(it) }\n        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), CatalogState.Loading)\n\n    // تحويل لـ SharedFlow لبث تنبيهات الأسعار لأكثر من شاشة مع ريبلاي:\n    val priceAlerts: SharedFlow<PriceAlert> = repository.getPriceAlertsFlow()\n        .shareIn(viewModelScope, SharingStarted.Lazily, replay = 1)\n}\n```",
        "trade_offs_ar": "التحويل لتيار ساخن يستهلك كوروتين نشطة في الـ ViewModelScope، ولكنه يمنع التكرار تماماً ويوحد البيانات. استخدام `stateIn` يفرض قيمة أولية ويدمج التكرار، بينما `shareIn` يمنحك مرونة كاملة في سعة الـ Buffer لكنه لا يوفر خاصية `.value` المباشرة.",
        "failure_modes_ar": "استخدام `SharingStarted.Eagerly` لتيار موقع جغرافي (GPS)، مما يجعله يعمل في الخلفية ويستنزف البطارية حتى لو لم يكن هناك أي جامع. خطأ آخر هو وضع مهلة `WhileSubscribed` بصفر، مما يتسبب في إعادة تشغيل استعلام الداتابيز وإلغائه مع كل تدوير للشاشة.",
        "production_perspective_ar": "في تطبيقات أندرويد المعيارية، `stateIn` مع `SharingStarted.WhileSubscribed(5000)` هو النمط القياسي الإلزامي في الـ ViewModels لتحويل بيانات Room والشبكة إلى حالة واجهة متوافقة مع Jetpack Compose وتتحمل تدوير الشاشة بسلاسة.",
        "how_to_answer_ar": "- **الوظيفة المعمارية:** هما عاملا تحويل التيارات الباردة الكسولة إلى تيارات ساخنة مشتركة (Cold-to-Hot Conversion).\n- **الفرق بينهما:** `stateIn` ينتج StateFlow (حالة، قيمة أولية، دمج)، و `shareIn` ينتج SharedFlow (أحداث، تحكم بالـ Replay والـ Buffer).\n- **دور النطاق:** كلاهما يتطلب CoroutineScope (زي viewModelScope) للعمل بداخله.\n- **سياسات التشغيل (SharingStarted):** قارن بين Eagerly و Lazily و WhileSubscribed.\n- **قاعدة الإنتاج الذهبية:** استخدام `WhileSubscribed(5000)` لحماية موارد البطارية وسد فجوة تدوير الشاشة.",
        "talking_points_ar": "ناقش دور مهلة الـ 5 ثوانٍ في سد فجوة تدمير وإعادة إنشاء الـ Activity أثناء الـ Configuration Change، وكيفية تتبع عدد المشتركين داخلياً في AbstractSharedFlow، والتعامل مع replayExpirationMillis.",
        "follow_ups_ar": "- **المحاور:** \"لماذا نضع 5000 ميلي ثانية تحديداً في `WhileSubscribed(5000)`؟\"\n  **المرشح:** \"الـ 5 ثوانٍ دي مهلة أمان (Grace Period)؛ لما الشاشة بتتدور، الـ Activity القديمة بتعمل onStop والمشتركين بيبقوا 0، وبعدها بـ 300 ملي ثانية الـ Activity الجديدة بتفتح وتشترك. مهلة الـ 5 ثوانٍ بتمنع إيقاف التدفق العلوي وإعادة تشغيله من الصفر أثناء التدوير، وتوفر اتصالات الشبكة والداتابيز.\"\n\n- **المحاور:** \"متى تختار `shareIn` بدلاً من `stateIn`؟\"\n  **المرشح:** \"بختار `shareIn` لما أكون بنقل تيار أحداث عابرة أو إشعارات مش محتاج ليها قيمة أولية إجبارية، أو لما أحتاج احتفظ بـ replay لأكتر من عنصر (زي آخر 5 رسائل شات)، أو لما أكون محتاج أتحكم في سياسة الـ BufferOverflow.\"",
        "self_check_ar": "هل وضحت فكرة التحويل من بارد لساخن؟ هل ميزت بين إنتاج StateFlow و SharedFlow؟ وهل شرحت سر مهلة 5000ms في WhileSubscribed؟",
        "references_ar": f"- [Things to know about Flow's shareIn and stateIn](https://medium.com/androiddevelopers/things-to-know-about-flows-sharein-and-statein-operators-20e6ec54d3d) — دليل جوجل الرسمي للمشغلين.\n- [StateFlow API reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/state-in.html) — توثيق المشغل وتفاصيل السياسات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "هم مشغلات بيحولوا التدفق البارد الكسول (Cold Flow) لتدفق ساخن ومشترك (Hot Stream) جوه CoroutineScope. مشغل `stateIn` بيحوله لـ StateFlow لحفظ حالة الواجهة وبيطلب قيمة أولية، ومشغل `shareIn` بيحوله لـ SharedFlow لبث الأحداث مع إمكانية ضبط الـ Replay والـ Buffer. والاتنين بيتحكموا في توقيت التشغيل بسياسة SharingStarted.",
        "best_answer_ar": "عوامـل `stateIn` و `shareIn` هما الجسر المعماري اللي بنستخدمه لتحويل الـ Cold Flows اللي جاية من طبقة البيانات إلى Hot Streams مشتركة في طبقة الـ Presentation.\n\nالـ Cold Flow بطبيعته بيعيد تشغيل الكود مع كل جامع؛ فلو عندي شاشتين بيسمعوا لنفس قائمة المنتجات في الداتابيز، هيتكرر الاستعلام مرتين. باستخدام المشغلين دول جوه `viewModelScope`، بنفتح اشتراك واحد بس في الخلفية ونوزع الداتا على المشتركين بنظام الـ Multicast.\n\nبنختار `stateIn` لما نكون بنعرض حالة شاشة؛ لأنه بيلزمنا بقيمة ابتدائية، وبيحفظ أحدث لقطة في الذاكرة، وبيلغي التكرار (Conflation)، وبيوفر خاصية `.value` المتزامنة.\n\nأما `shareIn` فبنختاره لما نكون بنبث أحداث أو إشعارات عامة مش محتاجة قيمة أولية، أو لما نحتاج نتحكم في حجم الـ Replay (مثلاً نحتفظ بآخر 3 إشعارات) أو نظبط سعة الـ Buffer.\n\nوأهم نقطة هي اختيار سياسة التشغيل؛ في أندرويد بنستخدم دايماً `SharingStarted.WhileSubscribed(5000)` مع `stateIn`، علشان التدفق يشتغل فقط والشاشة مفتوحة، وبمهلة 5 ثوانٍ تحمي الاتصال من الإلغاء أثناء تدوير الشاشة.",
        "deep_answer_ar": "على مستوى الـ Systems Implementation، مشغلي `stateIn` و `shareIn` بيطلقوا كوروتين داخل الـ CoroutineScope الممرر، الكوروتين دي بتعمل `collect` للـ Cold Flow العلوي وبتضخ البيانات في Channel Buffer داخلي مربوط بمصفوفة الـ Slots.\n\nالتحكم في دورة حياة الكوروتين دي بيتم بالكامل من خلال واجهة `SharingStarted`. لو اخترنا `Eagerly`، التدفق العلوي بيبدأ فوراً ويفضل شغال طول ما الـ Scope عايش حتى لو مفيش ولا مشترك. ولو اخترنا `Lazily`، بيستنى أول مشترك يوصل، لكن بمجرد ما يبدأ مش بيقف أبداً حتى لو كل المشتركين خرجوا.\n\nالاحترافية بتبان في استخدام `SharingStarted.WhileSubscribed(stopTimeoutMillis, replayExpirationMillis)`. السياسة دي بتراقب عداد المشتركين (Subscription Count) في الـ AbstractSharedFlow. أول ما العداد يتحول من 0 لـ 1، بتطلق كوروتين الجمع العلوي. وأول ما يرجع لـ 0، بتشغل Timer بالمهلة المحددة (مثلاً 5000ms). لو وصل مشترك جديد قبل ما الـ 5 ثواني تخلص (زي ما بيحصل في الـ Configuration Change لما الـ Activity يعاد إنشاؤها في 300ms)، الـ Timer بيتلغي والاتصال بيفضل مستمر بدون أي انقطاع.\n\nلو الـ 5 ثواني خلصوا ومحدش جه (زي خروج المستخدم للـ Home Screen)، الكوروتين بتلغي الجمع العلوي وتفصل الـ Database Connection أو اتصال الـ Socket لتوفير البطارية والذاكرة.\n\nعلشان كده في بيئات الإنتاج، الـ Staff Engineers بيعتبروا تركيبة `stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), InitialState)` هي المعيار الذهبي الإلزامي لربط بيانات الـ Data Layer بشاشات Jetpack Compose."
    }
}

def run():
    print(f"Elevating {len(DATA)} questions in FLO (FLO-01 to FLO-08)...")
    
    # 1. Update canonical markdown files
    for qid in sorted(DATA.keys()):
        data = DATA[qid]
        ee.update_canonical_question(
            qid=qid,
            concept_en=data["concept_en"],
            walkthrough_en=data["walkthrough_en"],
            structured_en=data["structured_en"],
            deep_senior_en=data["deep_senior_en"],
            short_en=data["short_en"],
        )
        print(f"Updated canonical question {qid}")

    # 2. Save Arabic metadata dictionary
    meta_dict = {qid: DATA[qid]["meta_ar"] for qid in sorted(DATA.keys())}
    meta_file = SCRIPT_DIR / "data" / "metadata_flo_01_08.json"
    meta_file.write_text(json.dumps(meta_dict, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved Arabic metadata to {meta_file}")

    # 3. Merge all metadata
    ee.merge_all_metadata()

    # 4. Validate each question
    all_passed = True
    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            all_passed = False
            print(f"❌ {qid} validation failed with {len(errs)} errors:")
            for e in errs:
                print("  -", e)
        else:
            print(f"✅ {qid} passed validation with 0 errors!")

    if not all_passed:
        print("Some questions failed validation!", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"All {len(DATA)} FLO questions (FLO-01 to FLO-08) successfully elevated and passed validation!")

if __name__ == "__main__":
    run()

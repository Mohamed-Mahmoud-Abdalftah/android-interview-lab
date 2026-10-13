#!/usr/bin/env python3
"""Generator for FLO-01 through FLO-06 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "flo.json"

FLO_01_06 = [
    {
        "id": "FLO-01",
        "arabic_explanation": (
            "المقارنة بين `Flow` ودالة `suspend` عادية بتحدد الفرق بين استرجاع قيمة واحدة (One-shot) واسترجاع تدفق مستمر من البيانات (Continuous Stream):\n\n"
            "1. الدالة المعلقة العادية (`suspend fun`):\n"
            "   - تمثل **Single Asynchronous Value** (1:1).\n"
            "   - تبدأ، تنفذ طلباً غير متزامن (زي جلب تفاصيل مستخدم من API أو قراءة إعدادات من DataStore)، وترجع قيمة واحدة فقط ثم تنتهي دورة حياتها.\n"
            "   - لا يمكنها إرسال تحديثات تالية لنفس الاستدعاء.\n\n"
            "2. الـ `Flow` (Reactive Stream):\n"
            "   - يمثل **Asynchronous Data Stream** يبث عدة قيم عبر الزمن (1:N) بطريقة معلقة (Asynchronously emits multiple values).\n"
            "   - مبني بالكامل على Coroutines، ويدعم Backpressure تلقائياً.\n"
            "   - مناسب جداً للبيانات المتغيرة بمرور الوقت: زي مراقبة جدول في قاعدة بيانات Room، تتبع الموقع الجغرافي بالـ GPS كل ثانية، أو استقبال رسائل WebSocket."
        ),
        "practical_walkthrough": (
            "في شاشة الملف الشخصي والرصيد البنكي:\n"
            "- **متى نستخدم `suspend fun`؟**\n"
            "  `suspend fun updateNickname(name: String): Result<Unit>`\n"
            "  عملية إرسال وحيدة (One-shot)؛ نرسل الاسم وننتظر نجاح أو فشل التعديل.\n"
            "- **متى نستخدم `Flow`؟**\n"
            "  `fun observeBalance(): Flow<BigDecimal>`\n"
            "  تدفق مستمر؛ كلما أودع المستخدم أموالاً أو أجرى عملية شراء، قاعدة البيانات تصدر (emit) الرصيد الجديد، وشاشة التطبيق تحدث العرض تلقائياً بدون أن يضطر المستخدم لسحب الشاشة للتحديث (Pull to refresh)."
        ),
        "quick_answer": "A suspend function computes and returns a single value asynchronously (one-shot). A Flow is an asynchronous data stream that emits multiple values sequentially over time, supporting backpressure, reactive operators, and lifecycle-aware observation.",
        "best_answer": (
            "The fundamental difference is cardinality: a suspend function models a single asynchronous value (one-shot), while a Flow models a sequence of asynchronous values emitted over time (stream).\n\n"
            "I use a suspend function when an operation has a discrete beginning and end that produces a single result—such as submitting an order, logging in, or reading a configuration flag. Once the function returns, its execution finishes.\n\n"
            "I use Flow when the UI needs to observe continuous state or event changes over time—such as observing real-time Room database changes, streaming GPS location updates, or listening to WebSocket push notifications. Flow is cold by default, handles backpressure automatically through coroutine suspension, and provides rich transformation operators like map, filter, and combine."
        ),
        "deep_answer": (
            "Under the hood, `Flow` is defined as a clean interface with a single method: `suspend fun collect(collector: FlowCollector<T>)`. "
            "Because `collect` is a suspending function, the entire lifecycle of a Flow is executed within the caller's CoroutineContext. This gives Flow a massive advantage over older reactive frameworks like RxJava:\n\n"
            "1. **Zero Thread Hopping Overhead:** Flow does not need complex schedulers; it cooperatively suspends on the collector's thread.\n"
            "2. **Built-in Backpressure:** Emission via `emit()` is a suspending function. If the collector is slow or doing heavy rendering, the emitter's coroutine is suspended until the collector finishes processing the previous element. No special buffer strategy is required for basic safety.\n\n"
            "3. **Structured Concurrency:** If the collector coroutine is cancelled (e.g., the user rotates the screen and the ViewModel clears), the Flow's upstream emitter is automatically cancelled immediately without any manual disposal boilerplate."
        ),
        "follow_ups": [
            {
                "interviewer": "Can a Flow emit an infinite sequence of values?",
                "answer": "Yes. A Flow can emit indefinitely as long as its coroutine scope remains active (e.g., a timer flow or continuous socket listener). It only terminates when the emitter completes, throws an exception, or the collector cancels its scope."
            },
            {
                "interviewer": "How does Flow backpressure compare to RxJava's Flowable?",
                "answer": "RxJava requires complex backpressure strategies (like BUFFER, DROP, or LATEST) because non-suspending threads must manage unread items in memory. Kotlin Flow handles backpressure naturally through coroutine suspension: emit() simply suspends until collect() is ready for the next item."
            },
            {
                "interviewer": "Can a suspend function return a Flow?",
                "answer": "Usually, no. Returning a cold Flow should be an immediate, non-suspending function call (e.g., `fun observeData(): Flow<Data>`). The work inside the Flow should only begin when `collect()` is invoked, not during the method call itself."
            }
        ]
    },
    {
        "id": "FLO-02",
        "arabic_explanation": (
            "فهم الـ Cold Flows وما يحدث عند وجود مستمعين متعددين (Multiple Collectors) هو ركيزة أساسية في معمارية الـ Streams:\n\n"
            "1. ما هو الـ Cold Flow؟\n"
            "   - الـ Cold Flow هو تدفق كسول (Lazy Stream).\n"
            "   - **لا ينفذ أي كود إطلاقاً** ولا يبدأ في إنتاج البيانات إلا عندما ينادي مستمع (Collector) دالة `collect()`!\n"
            "   - يشبه تشغيل أسطوانة CD أو فيلم على Netflix: الفيلم لا يبدأ حتى تضغط 'Play'.\n\n"
            "2. ماذا يحدث عند وجود Multiple Collectors؟\n"
            "   - **كل مستمع يبدأ تنفيذاً مستقلاً وجديداً بالكامل من البداية (Independent Execution Pipeline)!**\n"
            "   - لو عندك Cold Flow يقوم بعمل طلب شبكة: واستمع إليه Collector A و Collector B في نفس الوقت، سيتم إرسال **طلبي شبكة حقيقيين ومنفصلين للسيرفر**!\n"
            "   - الكود داخل بلوك `flow { ... }` سيتكرر تنفيذه لكل مستمع على حدة.\n\n"
            "3. كيف نحول الـ Cold Flow إلى Shared Stream لتجنب تكرار العمليات؟\n"
            "   - باستخدام مشغلات التحويل إلى Hot Streams: مثل `shareIn()` أو `stateIn()`، والتي تشارك بثاً واحداً مشتركاً بين جميع المستمعين (Multicasting)."
        ),
        "practical_walkthrough": (
            "المشكلة العملية وتصحيحها المعماري:\n"
            "```kotlin\n"
            "// ❌ Cold Flow يكرر استدعاء الشبكة لكل شاشة:\n"
            "val userFlow: Flow<User> = flow {\n"
            "    println(\"Executing API call!\")\n"
            "    emit(api.getUser()) // سيتكرر لكل مستمع!\n"
            "}\n"
            "\n"
            "// في الشاشة الأولى:\n"
            "userFlow.collect { renderHeader(it) } // يطبع: Executing API call!\n"
            "// في الشاشة الثانية:\n"
            "userFlow.collect { renderSidebar(it) } // يطبع: Executing API call! (طلب شبكة إضافي غير مبرر!)\n"
            "\n"
            "// ✅ الحل باستخدام stateIn لتحويله إلى Hot StateFlow مشترك:\n"
            "val sharedUser: StateFlow<User?> = userFlow.stateIn(\n"
            "    scope = viewModelScope,\n"
            "    started = SharingStarted.WhileSubscribed(5_000L),\n"
            "    initialValue = null\n"
            ") // الآن كلا الشاشتين تتشاركان نفس النتيجة بطلب شبكة واحد فقط!\n"
            "```"
        ),
        "quick_answer": "A cold flow does not execute its producer block until collect() is invoked. When multiple collectors subscribe, each collector triggers a completely separate, independent execution of the upstream flow from the beginning, repeating network calls or queries unless converted to a hot stream via shareIn() or stateIn().",
        "best_answer": (
            "A cold flow is inherently passive and lazy: the producer code inside the `flow { }` builder does not run until a terminal operator like `collect()` is called.\n\n"
            "When multiple collectors listen to a cold flow, **each collector starts an independent execution pipeline from scratch**. For example, if a cold flow makes an HTTP GET request or performs a heavy Room query, two concurrent collectors will execute two separate network requests and two separate database queries. They do not share execution or multicast emissions by default.\n\n"
            "To prevent redundant expensive work when multiple UI components observe the same data, we convert cold flows into hot multicasting streams using `shareIn()` or `stateIn()`. This shares a single upstream execution and broadcasts values to all active collectors simultaneously."
        ),
        "deep_answer": (
            "At the architectural implementation level, a cold flow represents a blueprint for execution rather than an active pipeline. "
            "Each call to `flow.collect(collector)` creates a new instance of the flow builder's state machine in the collector's coroutine frame. If five collectors collect a cold flow concurrently, there are five separate coroutines running the upstream code independently.\n\n"
            "This independence is sometimes desirable: for instance, a flow reading a file from disk should start at byte 0 for each independent reader. However, in modern Android UI architecture where multiple fragments, composables, or widgets observe the same repository state, cold execution is an antipattern.\n\n"
            "By applying `shareIn(scope, SharingStarted.WhileSubscribed(5000), replay = 1)`, we introduce an intermediary `SharedFlow` that acts as a multicasting bridge: it opens a single upstream connection to the cold data source and broadcasts each emission to downstream subscribers, maintaining cache locality and network efficiency."
        ),
        "follow_ups": [
            {
                "interviewer": "Can a cold flow emit values if there are zero collectors?",
                "answer": "No, never. Cold flows only begin emitting when `collect()` is called. If no one collects, zero CPU cycles are spent and zero values are produced."
            },
            {
                "interviewer": "How do you test a cold flow in a unit test?",
                "answer": "Using Turbine (`flow.test { ... }`) or `flow.toList()` inside `runTest`. The test acts as the collector, activating the cold flow and asserting on emitted items sequentially."
            },
            {
                "interviewer": "Is a Room DAO query that returns `Flow<List<User>>` cold or hot?",
                "answer": "It is a cold flow! Room does not query SQLite until `collect()` is called. When you collect it, Room sets up an invalidation tracker; when you cancel collection, Room detaches the observer automatically."
            }
        ]
    },
    {
        "id": "FLO-03",
        "arabic_explanation": (
            "الـ `StateFlow` والـ `SharedFlow` هما الـ Hot Streams الأساسيان في Kotlin Coroutines، وفهم سبب كونهما 'Hot' هو جوهر إدارة الحالة والأحداث:\n\n"
            "1. ما معنى أنهما 'Hot Streams'؟\n"
            "   - الـ Hot Stream **موجود ونشط وينتج بيانات باستمرار في الذاكرة (Memory-resident)** بغض النظر عما إذا كان هناك مستمعين (Collectors) أم لا!\n"
            "   - يشبه البث المباشر في الراديو أو التلفزيون: المذيع يتكلم حتى لو لا يوجد أحد يستمع؛ ومن يفتح الراديو يسمع ما يُبث في اللحظة الحالية فقط.\n\n"
            "2. ما هو الـ `StateFlow`؟\n"
            "   - مخصص لـ **إدارة الحالة (State Management)**.\n"
            "   - يحمل دائماً **قيمة حالية في الذاكرة** يمكن قراءتها في أي وقت عبر `stateFlow.value` (Synchronous read).\n"
            "   - يتطلب قيمة ابتدائية إلزامية (Initial Value).\n"
            "   - لديه **Conflation مدمج:** لو الحالة لم تتغير (وفقاً للـ `equals()`)، فلن يرسل أي تحديث للمستمعين.\n\n"
            "3. ما هو الـ `SharedFlow`؟\n"
            "   - مخصص لـ **بث الأحداث والإشارات (Events & Multicasting)**.\n"
            "   - لا يشترط وجود قيمة ابتدائية.\n"
            "   - يمكن ضبطه بـ `replay = N` لتحديد عدد الأحداث السابقة التي يستلمها أي مستمع جديد.\n"
            "   - مناسب جداً للأحداث العابرة (Navigation, Show Snackbar, Analytics)."
        ),
        "practical_walkthrough": (
            "في شاشة تسجيل الدخول (Login Screen):\n"
            "- **إدارة الـ State باستخدام `StateFlow`:**\n"
            "  `private val _uiState = MutableStateFlow<LoginUiState>(LoginUiState.Idle)`\n"
            "  `val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()`\n"
            "  الشاشة تعرض `uiState.value`؛ ولو دور المستخدم الشاشة، الشاشة الجديدة تقرأ القيمة الحالية فوراً بدون إعادة تحميل.\n"
            "- **إدارة الـ Navigation Event باستخدام `SharedFlow`:**\n"
            "  `private val _events = MutableSharedFlow<LoginEvent>()`\n"
            "  `val events: SharedFlow<LoginEvent> = _events.asSharedFlow()`\n"
            "  عند نجاح تسجيل الدخول، نرسل: `_events.emit(LoginEvent.NavigateToHome)`.\n"
            "  الحدث يتم استهلاكه لمرة واحدة فقط؛ ولا يعاد تشغيله عند تدوير الشاشة."
        ),
        "quick_answer": "StateFlow and SharedFlow are hot streams because they exist and emit independently of collectors, residing in memory. StateFlow manages observable state, always retains a current value (.value), and suppresses duplicate emissions; SharedFlow broadcasts events to multiple collectors with configurable replay caches and buffer policies.",
        "best_answer": (
            "StateFlow and SharedFlow are 'hot' streams because their lifecycles are completely decoupled from subscribers. Unlike cold flows that only execute when collected, hot flows exist in memory, accept emissions, and retain state regardless of whether any collectors are active.\n\n"
            "**StateFlow** is specialized for state management. It is a state machine that always holds an accessible current value via `.value`. It requires an initial value, retains exactly the latest emission, and features built-in conflation—meaning it uses `Any.equals()` to suppress emissions if the new state is identical to the current state.\n\n"
            "**SharedFlow** is a general-purpose, highly configurable multicaster designed for broadcasting events to multiple collectors. It does not require an initial value, supports configurable replay buffer sizes (`replay = N`), and handles backpressure buffer overflow strategies (`BufferOverflow.DROP_OLDEST` or `SUSPEND`)."
        ),
        "deep_answer": (
            "Under the hood, `StateFlow` is actually a specialized, optimized subtype of `SharedFlow`. Specifically, `StateFlow` behaves identically to a `SharedFlow` configured with `replay = 1` and `onBufferOverflow = BufferOverflow.DROP_OLDEST`, augmented with two critical characteristics:\n\n"
            "1. **Synchronous Value Access:** You can read `stateFlow.value` at any time from any thread without launching a coroutine.\n"
            "2. **State Deduplication:** When you write `_stateFlow.value = newState`, it compares `newState == oldState`. If true, the update is a no-op; it skips notifying collectors and avoids triggering Jetpack Compose recompositions.\n\n"
            "In contrast, `MutableSharedFlow` allows duplicate identical emissions. If you emit `SnackbarMessage(\"Error\")` twice, collectors receive both events sequentially, which is why SharedFlow is chosen for discrete user actions and events."
        ),
        "follow_ups": [
            {
                "interviewer": "Can a subscriber to a StateFlow miss intermediate values?",
                "answer": "Yes! Because StateFlow is conflated, if the producer emits values 1, 2, and 3 faster than a slow collector can process them, the collector may jump directly from 1 to 3, missing 2. StateFlow guarantees delivery of the most recent state, not historical delivery of every transition."
            },
            {
                "interviewer": "Why does StateFlow require an initial value while SharedFlow does not?",
                "answer": "Because StateFlow represents continuous state and exposes a synchronous `.value` property that must never return undefined or null unless explicitly typed as nullable (e.g., `StateFlow<User?>`)."
            },
            {
                "interviewer": "What happens when you emit to a `SharedFlow` with `replay = 0` when there are no collectors?",
                "answer": "The emission is dropped immediately and permanently lost. Any subscriber that connects a millisecond later will not receive that event."
            }
        ]
    },
    {
        "id": "FLO-04",
        "arabic_explanation": (
            "المقارنة الشاملة بين `Flow` و `StateFlow` و `SharedFlow` و `LiveData` هي أحد أكثر الأسئلة المعمارية شيوعاً في مقابلات أندرويد الحديثة:\n\n"
            "1. الـ Cold `Flow`:\n"
            "   - **طبيعته:** Cold Stream.\n"
            "   - **الاستخدام:** طبقة البيانات (Data Layer / Room / DataStore / Network).\n"
            "   - **الخصائص:** ينفذ الكود لكل مستمع على حدة؛ لا يحفظ قيمة في الذاكرة؛ يتعامل مع الـ Coroutines بشكل طبيعي.\n\n"
            "2. الـ `StateFlow`:\n"
            "   - **طبيعته:** Hot Stream.\n"
            "   - **الاستخدام:** إدارة حالة الـ UI في الـ ViewModel وعرضها على الشاشة.\n"
            "   - **الخصائص:** يحمل دائماً القيمة الحالية (`.value`)؛ Conflated (يتجاهل القيم المكررة)؛ يتطلب قيمة ابتدائية.\n\n"
            "3. الـ `SharedFlow`:\n"
            "   - **طبيعته:** Hot Stream.\n"
            "   - **الاستخدام:** إرسال الأحداث لعدة مستمعين (One-off Events / Navigation / Snackbars).\n"
            "   - **الخصائص:** لا يشترط قيمة ابتدائية؛ Replay قابل للتخصيص؛ يسمح بالقيم المكررة.\n\n"
            "4. الـ `LiveData` (المكتبة القديمة):\n"
            "   - **طبيعته:** Hot Stream مربوط بـ Android UI Lifecycle.\n"
            "   - **عيوبه مقارنة بـ StateFlow:** مربوط حصرياً بالـ Android Framework (لا يعمل في Kotlin Multiplatform ولا الـ Domain Layer)؛ محصور على الـ Main Thread في التحديث بـ `setValue`؛ يفتقر للـ Operators القوية الموجودة في Coroutines Flow."
        ),
        "practical_walkthrough": (
            "جدول مقارنة سريع ومعماري:\n"
            "| المعيار | Cold Flow | StateFlow | SharedFlow | LiveData |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n"
            "| **Cold vs Hot** | Cold | Hot | Hot | Hot |\n"
            "| **مكان الاستخدام** | Repository / DAO | ViewModel UI State | Events / Navigation | Legacy UI State |\n"
            "| **يحمل .value؟** | لا | نعم دائماً | لا (إلا لو replay >= 1) | نعم (`.value?`) |\n"
            "| **Platform** | Pure Kotlin (KMP) | Pure Kotlin (KMP) | Pure Kotlin (KMP) | Android Only |\n"
            "| **Lifecycle-Aware** | عبر collectAsState | عبر collectAsState | عبر repeatOnLifecycle | تلقائياً في UI |\n"
            "| **Deduplication** | اختياري | مدمج (`equals`) | لا | لا |"
        ),
        "quick_answer": "Flow is a cold stream for asynchronous data sources in repositories; StateFlow is a hot, conflated state-holder for UI state in ViewModels; SharedFlow is a hot multicaster for one-off events; and LiveData is a legacy, Android-bound UI state holder that lacks KMP support and rich coroutine operators.",
        "best_answer": (
            "Here is how I architecturally classify each stream primitive in modern Android development:\n\n"
            "**Cold Flow** is designed for the data and repository layers. It is lazy, executes per collector, and naturally handles streaming sources like Room, DataStore, or Paging3.\n\n"
            "**StateFlow** is the standard replacement for LiveData in modern ViewModel UI state management. It is hot, holds a current immutable value synchronously via `.value`, requires an initial state, conflates repeated values via `equals()`, and is 100% Kotlin Multiplatform compatible.\n\n"
            "**SharedFlow** is the hot event broadcaster. It has no mandatory initial value, does not conflate identical emissions, and allows custom replay caches, making it ideal for broadcast events like navigation triggers or toast messages.\n\n"
            "**LiveData** is Android's legacy, lifecycle-aware observable. While it automatically pauses observers in the background, it is tightly coupled to Android platform lifecycles (breaking KMP), is restricted to main-thread dispatches, and lacks the composability and operator depth of Coroutines Flow. Modern projects standardize on StateFlow."
        ),
        "deep_answer": (
            "The primary technical driver for migrating from LiveData to StateFlow is architectural purity and Kotlin Multiplatform (KMP) readiness. LiveData requires the `androidx.lifecycle` Android dependency, polluting pure Kotlin Domain and UseCase layers with platform imports.\n\n"
            "Furthermore, LiveData's threading model has known edge cases: calling `postValue()` from background threads conflates intermediate values if posted faster than the main Looper can dispatch them, leading to lost events in rapid succession.\n\n"
            "With StateFlow and Jetpack Compose, the integration is seamless via `collectAsStateWithLifecycle()`. In XML layouts, `lifecycleScope.launch { repeatOnLifecycle(Lifecycle.State.STARTED) { stateFlow.collect { ... } } }` achieves identical or superior lifecycle safety to LiveData without any platform lock-in."
        ),
        "follow_ups": [
            {
                "interviewer": "Why is `collectAsStateWithLifecycle()` needed in Compose instead of plain `collectAsState()`?",
                "answer": "`collectAsState()` continues collecting from the flow even when the Android app is in the background, wasting CPU and battery. `collectAsStateWithLifecycle()` pauses collection when the Activity/Fragment lifecycle drops below the specified state (like STARTED)."
            },
            {
                "interviewer": "Can you convert a LiveData into a Flow and vice versa?",
                "answer": "Yes. The `androidx.lifecycle:lifecycle-livedata-ktx` library provides `liveData.asFlow()` to convert LiveData to Flow, and `flow.asLiveData()` to convert Flow to LiveData."
            },
            {
                "interviewer": "Does StateFlow work with Jetpack Compose better than LiveData?",
                "answer": "Yes. StateFlow is a first-class citizen in Kotlin, has direct support in Compose runtime via state snapshot systems, and avoids the additional observeAsState LiveData bridging adapter."
            }
        ]
    },
    {
        "id": "FLO-05",
        "arabic_explanation": (
            "اشتراط وجود قيمة ابتدائية (Initial Value) في `MutableStateFlow` هو قرار تصميمي مقصود ومحوري لفهم مفهوم 'الحالة' (State):\n\n"
            "1. ما هو الفرق بين الحالة (State) والحدث (Event)؟\n"
            "   - **الحالة (State)** شيء موجود دائماً وله قيمة حالية في أي لحظة زمنية. لا يمكن أن تسأل: 'ما هي حالة الشاشة الآن؟' فيكون الجواب: 'لا يوجد شيء، فراغ تام!'.\n"
            "   - الشاشة دائماً إما في حالة `Loading` أو `Empty` أو `Success` أو `Error`.\n\n"
            "2. الـ Synchronous Access (`.value`):\n"
            "   - الـ `StateFlow` يوفر دالة قراءة متزامنة فورية: `stateFlow.value`.\n"
            "   - لو لم يكن هناك قيمة ابتدائية، ماذا سترجع `stateFlow.value` لو استدعاها كود قبل وصول أي تحديث؟ هل ترجع `null`؟ هذا سيجبر المطورين على جعل كل أنواع البيانات `Nullable`!\n\n"
            "3. منع الـ Race Conditions والـ Flashing في واجهة المستخدم (UI):\n"
            "   - عند فتح شاشة جديدة أو تدوير الجهاز، الـ Composable أو الـ View يحتاج لقراءة حالة فورية لرسم الإطار الأول (First Frame) دون انتظار غير متزامن."
        ),
        "practical_walkthrough": (
            "تصميم حالة الشاشة بنظافة مع قيمة ابتدائية واضحة:\n"
            "```kotlin\n"
            "sealed interface ProductUiState {\n"
            "    data object Loading : ProductUiState // حالة البداية الواضحة\n"
            "    data class Success(val products: List<Product>) : ProductUiState\n"
            "    data class Error(val message: String) : ProductUiState\n"
            "}\n"
            "\n"
            "class ProductViewModel(private val repository: ProductRepository) : ViewModel() {\n"
            "    // نمرر Loading كـ Initial Value إلزامي:\n"
            "    private val _uiState = MutableStateFlow<ProductUiState>(ProductUiState.Loading)\n"
            "    val uiState: StateFlow<ProductUiState> = _uiState.asStateFlow()\n"
            "}\n"
            "```\n"
            "عندما يفتح المستخدم الشاشة، الـ UI يرسم شريط التحميل فوراً بدون وميض وبدون أي Null checks."
        ),
        "quick_answer": "MutableStateFlow requires an initial value because it represents continuous, stateful data that must guarantee a non-null, synchronously readable state via .value at any instant, eliminating undefined states and ensuring the UI can render its first frame immediately.",
        "best_answer": (
            "MutableStateFlow requires an initial value by fundamental architectural design: it represents state, and state cannot be undefined.\n\n"
            "First, StateFlow guarantees synchronous access to its current state via the `.value` property. If an initial value were not mandatory, calling `.value` before the first emission would have to return null, forcing every single StateFlow to be nullable (`StateFlow<T?>`) and burdening codebases with null-assertions.\n\n"
            "Second, in UI frameworks like Jetpack Compose, the UI renders immediately upon composition. A mandatory initial state (such as `UiState.Loading` or `UiState.Initial`) guarantees that the screen always has valid, predictable data for its very first frame without flicker or unhandled states.\n\n"
            "If your use case genuinely represents a stream that has no initial value until an action occurs, then it is an **event stream**, not a state stream, and should be modeled using `SharedFlow` or `Channel` instead."
        ),
        "deep_answer": (
            "From a type-theory perspective, StateFlow models a continuous signal `t -> V`, where for any time `t >= 0`, there exists a value `V`. "
            "In contrast, cold Flow and SharedFlow model discrete events `(t_i, V_i)` where emissions occur at discrete points in time.\n\n"
            "Because StateFlow models a continuous signal, `StateFlow.collect()` immediately delivers the current value to any new collector before suspending. Requiring an initial value ensures that this contract is unbroken: a collector is never left in an uninitialized limbo awaiting an asynchronous task.\n\n"
            "When converting a cold Flow to a StateFlow using the `stateIn()` operator in a ViewModel, the compiler explicitly enforces this contract by requiring an `initialValue` parameter:\n\n"
            "```kotlin\n"
            "val items = repository.observeItems()\n"
            "    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())\n"
            "```\n\n"
            "Here, `emptyList()` guarantees that the UI has a valid baseline state while the repository initializes."
        ),
        "follow_ups": [
            {
                "interviewer": "What should you do if your initial value can only be computed asynchronously?",
                "answer": "Define a sealed UI state hierarchy (e.g., `sealed interface UiState`) with a dedicated `data object Loading : UiState` as the synchronous initial value, and emit `Success` once the asynchronous computation completes."
            },
            {
                "interviewer": "Can a StateFlow's initial value be `null`?",
                "answer": "Yes, if the generic type parameter is explicitly declared as nullable: `MutableStateFlow<User?>(null)`. However, using a sealed state (Loading/Success/Error) is generally cleaner domain modeling than nullable types."
            },
            {
                "interviewer": "How does `SharedFlow` behave without an initial value?",
                "answer": "`SharedFlow` suspends new collectors until an emission occurs. It does not expose a synchronous `.value` property unless initialized with `replay >= 1` and at least one item has already been emitted."
            }
        ]
    },
    {
        "id": "FLO-06",
        "arabic_explanation": (
            "الـ Conflation وقمع الحالات المكررة (Equality Suppression) في `StateFlow` هو أحد أذكى تصاميم الأداء في Kotlin:\n\n"
            "1. ما هو الـ Conflation؟\n"
            "   - الـ Conflation يعني **الدمج وتخطي القيم القديمة لصالح القيمة الأحدث**.\n"
            "   - لو الـ Producer أنتج 10 قيم سريعة في الثانية، والـ Collector بطيء ولا يستطيع استيعاب إلا قيمتين، الـ StateFlow سيتخطى القيم المتوسطة ويعطي الـ Collector القيمة الأحدث فوراً.\n\n"
            "2. كيف يستخدم StateFlow الـ Equality لقمع التكرار؟\n"
            "   - في دالة `_stateFlow.value = newState`، الـ StateFlow يقوم داخلياً بعمل فحص:\n"
            "     `if (oldState == newState) return` (باستخدام `Any.equals()`).\n"
            "   - لو كانت القيمة الجديدة مطابقة للقيمة القديمة (Equal)، الـ StateFlow **لن يرسل أي إشعار للمستمعين إطلاقاً (Suppressed)**!\n\n"
            "3. الفائدة الضخمة في Android و Jetpack Compose:\n"
            "   - يمنع إعادة الرسم غير الضرورية (Recomposition loops).\n"
            "   - لو ضغط المستخدم على زر الفرز وكان الفرز الحالي هو 'الأحدث' بالفعل، لن يتم إعادة رسم القائمة أو استهلاك الـ CPU في الـ UI."
        ),
        "practical_walkthrough": (
            "مثال عملي يوضح الفخ الذي يقع فيه المطورون مع الـ Mutable Objects:\n"
            "```kotlin\n"
            "// ❌ فخ كارثي: استخدام Mutable Object داخل StateFlow:\n"
            "class FilterState {\n"
            "    var selectedCategory = \"All\"\n"
            "}\n"
            "val state = MutableStateFlow(FilterState())\n"
            "\n"
            "// لو عدلت الحقل في نفس الكائن وحاولت تبعته:\n"
            "state.value.selectedCategory = \"Shoes\"\n"
            "state.value = state.value // لن يحدث أي شيء! الـ UI لن يتحدث إطلاقاً!\n"
            "// السبب: الكائن هو نفسه في الذاكرة، و equals() ترجع true، فـ StateFlow يقمع التحديث!\n"
            "\n"
            "// ✅ الحل الصحيح: استخدام Immutable Data Classes مع دالة copy():\n"
            "data class FilterState(val selectedCategory: String = \"All\")\n"
            "val state = MutableStateFlow(FilterState())\n"
            "\n"
            "state.update { current -> current.copy(selectedCategory = \"Shoes\") }\n"
            "// الآن تم إنشاء New Instance بقيم مختلفة، equals() ترجع false، والـ UI يتحدث فوراً!\n"
            "```"
        ),
        "quick_answer": "Conflation drops intermediate values for slow collectors in favor of the latest value. StateFlow uses structural equality (Any.equals()) on state assignment: if a newly assigned value equals the current value, StateFlow suppresses emission completely to eliminate redundant UI recompositions and allocations.",
        "best_answer": (
            "Conflation and equality suppression are StateFlow's core performance optimizations for state management.\n\n"
            "**Conflation** means that StateFlow only preserves the latest state. If a producer rapidly emits multiple updates while a collector is busy processing on the main thread, StateFlow drops intermediate states and delivers only the freshest state when the collector is ready.\n\n"
            "**Equality suppression** means that StateFlow compares newly assigned values against the existing state using `Any.equals()`. If `newState == oldState`, StateFlow suppresses the emission entirely: it does not dispatch to collectors and does not trigger Jetpack Compose recompositions.\n\n"
            "This makes **immutable data classes** mandatory when working with StateFlow. If you mutate a property inside a mutable object and reassign it to StateFlow, `equals()` will return true (same object reference), and StateFlow will silently swallow the update, leaving your UI stale."
        ),
        "deep_answer": (
            "Under the hood, StateFlow implements equality suppression via its internal CAS update loop in `StateFlowImpl`:\n\n"
            "```kotlin\n"
            "override var value: T\n"
            "    get() = ...\n"
            "    set(value) {\n"
            "        val curSequence = ...\n"
            "        var curValue = ...\n"
            "        if (curValue == value) return // Equality check suppresses emission!\n"
            "        updateState(...) // Notifies slots\n"
            "    }\n"
            "```\n\n"
            "In Android architecture, this has profound implications: "
            "1. **Compose Recomposition Skipping:** When Compose observes a StateFlow via `collectAsState()`, duplicate emissions are filtered at the source, preventing unnecessary layout and drawing passes. "
            "2. **State Modeling Integrity:** It forces teams to model UI state using immutable data classes with value equality. "
            "If you need to deliver an identical event multiple times in sequence (e.g., clicking the same button twice), you must not use StateFlow; you must use `SharedFlow` or `Channel` which do not perform equality suppression."
        ),
        "follow_ups": [
            {
                "interviewer": "How does `StateFlow.update { }` work with equality suppression?",
                "answer": "`StateFlow.update` evaluates the transform lambda inside an atomic CAS loop. If the lambda returns an object equal to the current state, StateFlow recognizes equality and avoids notifying collectors."
            },
            {
                "interviewer": "Can you disable equality suppression in StateFlow?",
                "answer": "No. Equality suppression is hardcoded into `StateFlowImpl`. If you require every emission to be delivered regardless of equality, you should use `MutableSharedFlow` with `replay = 1` instead."
            },
            {
                "interviewer": "What happens if a data class contains an Array property?",
                "answer": "Standard Kotlin data classes use referential `equals()` for raw Arrays, not content equality. Two arrays with identical elements will not be considered equal unless you override `equals()` using `contentEquals()`, which can lead to unexpected recompositions."
            }
        ]
    }
]


def main() -> None:
    existing = []
    if DATA_FILE.exists():
        try:
            existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            existing = []

    combined = []
    seen = set()
    for q in existing:
        combined.append(q)
        seen.add(q["id"])

    for q in FLO_01_06:
        if q["id"] not in seen:
            combined.append(q)
            seen.add(q["id"])
        else:
            for idx, item in enumerate(combined):
                if item["id"] == q["id"]:
                    combined[idx] = q
                    break

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(combined, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions FLO-01 to FLO-06. Total questions: {len(combined)}")


if __name__ == "__main__":
    main()

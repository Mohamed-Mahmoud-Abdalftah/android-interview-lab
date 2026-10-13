#!/usr/bin/env python3
"""Generator for FLO-07 through FLO-12 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "flo.json"

FLO_07_12 = [
    {
        "id": "FLO-07",
        "arabic_explanation": (
            "نمط الكبسولة (Encapsulation Pattern) باستخدام `asStateFlow()` هو القاعدة الذهبية في تصميم الـ ViewModels في أندرويد:\n\n"
            "1. المشكلة التي يحلها:\n"
            "   - في الـ ViewModel، نحتاج أن نكون قادرين على تعديل الحالة (`_uiState.value = ...` أو `_uiState.update { }`).\n"
            "   - ولكن **الـ View (Activity/Fragment/Composable) يجب ألا تكون قادرة على تعديل الحالة إطلاقاً!**\n"
            "   - لو تم كشف `MutableStateFlow` مباشرة للـ UI، يمكن لأي زر أو كود في الـ UI أن يكتب `viewModel.uiState.value = BadState`، مما يكسر مبدأ **UDF (Unidirectional Data Flow)** ويجعل تتبع الأخطاء كابوساً.\n\n"
            "2. ما الذي تفعله دالة `asStateFlow()`؟\n"
            "   - تقوم بإنشاء **Read-Only View Wrapper** (`ReadOnlyStateFlow`) حول الـ `MutableStateFlow`.\n"
            "   - تمنع أي شخص من عمل Cast خبيث أو غير مقصود: حتى لو حاول المطور كتابة `(uiState as MutableStateFlow).value = ...`، الـ Wrapper الداخلي يمنع ذلك ويرمي `ClassCastException` في وقت التشغيل!\n\n"
            "3. النمط القياسي للتنفيذ:\n"
            "   - متغير خاص للتعديل: `private val _uiState = MutableStateFlow(...)`\n"
            "   - متغير عام للقراءة فقط: `val uiState: StateFlow<T> = _uiState.asStateFlow()`"
        ),
        "practical_walkthrough": (
            "الكود القياسي في الـ ViewModel:\n"
            "```kotlin\n"
            "class CheckoutViewModel : ViewModel() {\n"
            "    // 1. Mutable خاص بالـ ViewModel فقط:\n"
            "    private val _uiState = MutableStateFlow(CheckoutUiState.Initial)\n"
            "    \n"
            "    // 2. Read-only مكشوف للـ UI:\n"
            "    val uiState: StateFlow<CheckoutUiState> = _uiState.asStateFlow()\n"
            "    \n"
            "    fun onPromoCodeEntered(code: String) {\n"
            "        // التعديل محصور حصرياً داخل دوال الـ ViewModel:\n"
            "        _uiState.update { it.copy(promoCode = code) }\n"
            "    }\n"
            "}\n"
            "```\n"
            "في الـ Composable: الشاشة تقرأ فقط `val state by viewModel.uiState.collectAsStateWithLifecycle()`، وأي محاولة لتعديل الحالة تتم بإرسال حدث للـ ViewModel."
        ),
        "quick_answer": "Use asStateFlow() to expose a read-only StateFlow interface from a private MutableStateFlow backing property. This enforces Unidirectional Data Flow (UDF) by ensuring only the ViewModel can mutate state while UI components can only observe it, with a runtime wrapper that prevents unsafe downcasting.",
        "best_answer": (
            "Exposing state via `asStateFlow()` is the foundational encapsulation pattern in modern Android architecture for enforcing **Unidirectional Data Flow (UDF)**.\n\n"
            "We declare a private mutable backing property:\n"
            "`private val _uiState = MutableStateFlow(InitialState)`\n"
            "And expose a public read-only property:\n"
            "`val uiState: StateFlow<MyState> = _uiState.asStateFlow()`\n\n"
            "This architectural separation guarantees that state mutations remain strictly confined to the ViewModel's business methods. The UI layer can observe emissions and read values, but it can never directly assign or mutate state.\n\n"
            "Crucially, `asStateFlow()` does not perform a simple interface upcast; it wraps the mutable flow in a dedicated `ReadOnlyStateFlow` class. This provides defensive type-safety: if a consumer attempts to dangerously downcast `(uiState as MutableStateFlow).value = ...`, the JVM throws a `ClassCastException`, preventing state corruption."
        ),
        "deep_answer": (
            "Under the hood, why not simply write `val uiState: StateFlow<T> = _uiState` (a simple compiler upcast)?\n\n"
            "A plain upcast only provides compile-time visibility restrictions. At runtime, the underlying JVM object remains an instance of `StateFlowImpl` (which implements `MutableStateFlow`). Any caller in Java, or any Kotlin developer using unsafe casting (`as MutableStateFlow`), could bypass your architectural boundary and mutate the internal state from the UI or test classes.\n\n"
            "`asStateFlow()` wraps the instance in `ReadOnlyStateFlow`, an internal wrapper that only implements `StateFlow` and delegates read methods to the underlying instance without exposing mutation handles. "
            "In enterprise code reviews, we enforce this via lint rules: every public state exposed by a ViewModel must be a read-only `StateFlow` or `SharedFlow` derived via `asStateFlow()` or `stateIn()`."
        ),
        "follow_ups": [
            {
                "interviewer": "Why not use a custom getter `val uiState get() = _uiState`?",
                "answer": "A custom getter returns the raw `_uiState` reference on every property access, which permits unsafe runtime casting to `MutableStateFlow`. `asStateFlow()` creates the protective wrapper once."
            },
            {
                "interviewer": "What is the equivalent function for SharedFlow?",
                "answer": "For `MutableSharedFlow`, the equivalent function is `asSharedFlow()`, which wraps the instance in a read-only `ReadOnlySharedFlow`."
            },
            {
                "interviewer": "How does Jetpack Compose interact with `asStateFlow()`?",
                "answer": "Compose consumes it via `collectAsStateWithLifecycle()`, which observes the read-only StateFlow and converts it into a Compose `State<T>`, triggering recomposition only when new distinct states are emitted."
            }
        ]
    },
    {
        "id": "FLO-08",
        "arabic_explanation": (
            "المشغلان `stateIn` و `shareIn` هما جسر التحويل من الـ Cold Flows إلى الـ Hot Streams:\n\n"
            "1. ما الذي يفعله `stateIn`؟\n"
            "   - يحول أي Cold Flow إلى **Hot StateFlow**.\n"
            "   - **يتطلب 3 معاملات:**\n"
            "     * `scope`: نطاق الـ Coroutine الذي سيعيش فيه الـ Flow (عادة `viewModelScope`).\n"
            "     * `started`: استراتيجية بدء وإيقاف البث (`SharingStarted.WhileSubscribed`, `Eagerly`, `Lazily`).\n"
            "     * `initialValue`: القيمة الابتدائية الإلزامية التي تعرض فوراً قبل اكتمال أول تدفق.\n"
            "   - النتيجة: StateFlow يحمل دائماً `.value` ويعمل له Conflation.\n\n"
            "2. ما الذي يفعله `shareIn`؟\n"
            "   - يحول أي Cold Flow إلى **Hot SharedFlow** متعدد المستمعين (Multicaster).\n"
            "   - **المعاملات:** `scope`, `started`, و `replay` (كم قيمة سابقة يتم الاحتفاظ بها للمستمعين الجدد).\n"
            "   - لا يشترط قيمة ابتدائية، ولا يقوم بعمل conflation للقيم المتطابقة.\n\n"
            "3. متى نستخدم كل منهما؟\n"
            "   - استخدم `stateIn` لتمثيل **حالة الشاشة (UI State)** المأخوذة من Room أو DataStore.\n"
            "   - استخدم `shareIn` لبث **أحداث أو إشعارات** مشتركة لعدة شاشات في نفس الوقت."
        ),
        "practical_walkthrough": (
            "تحويل Room Cold Flow إلى UI StateFlow في الـ ViewModel:\n"
            "```kotlin\n"
            "class UsersViewModel(private val repository: UserRepository) : ViewModel() {\n"
            "    \n"
            "    // repository.getUsers() ترجع Cold Flow<List<User>> من Room DB.\n"
            "    // نحولها لـ StateFlow باستخدام stateIn:\n"
            "    val usersUiState: StateFlow<List<User>> = repository.getUsers()\n"
            "        .map { it.filter { user -> user.isActive } }\n"
            "        .stateIn(\n"
            "            scope = viewModelScope,\n"
            "            started = SharingStarted.WhileSubscribed(5_000L),\n"
            "            initialValue = emptyList()\n"
            "        )\n"
            "}\n"
            "```\n"
            "النتيجة: لا يتم إطلاق استعلام Room إلا عندما تكون الشاشة مرئية وتستمع للـ Flow، ويتم مشاركة البيانات بين كل المكونات بدون تكرار."
        ),
        "quick_answer": "stateIn converts a cold Flow into a hot StateFlow with an initial value and latest-state retention (.value); shareIn converts a cold Flow into a hot SharedFlow with configurable replay cache. Both share a single upstream execution across multiple collectors within a specified CoroutineScope.",
        "best_answer": (
            "`stateIn` and `shareIn` are the standard conversion operators used to transform cold, lazy flows into hot, multicasting streams within a specific `CoroutineScope`.\n\n"
            "I use **`stateIn`** when transforming data sources into UI state. It converts any upstream cold flow into a `StateFlow`. It requires an `initialValue` so synchronous access via `.value` is immediately available, retains the latest emission, and conflates updates to suppress identical values.\n\n"
            "I use **`shareIn`** when broadcasting event or data streams to multiple subscribers without state semantics. It converts a cold flow into a `SharedFlow`, allows configuring `replay = N` to determine how many past emissions new subscribers receive, and does not require an initial value.\n\n"
            "Both operators take a `SharingStarted` strategy, which controls precisely when the upstream cold flow begins executing and when it cancels to save device battery."
        ),
        "deep_answer": (
            "Under the hood, both operators launch a single sharing coroutine inside the provided `CoroutineScope`. This coroutine acts as a bridge: it collects from the upstream cold flow once, and fans out each emitted item to an internal `StateFlowImpl` or `SharedFlowImpl`.\n\n"
            "The magic lies in how they manage the upstream subscription. When using cold streams like Room DAO queries or Bluetooth scanners, executing them continuously when the user minimizes the app drains battery. "
            "By pairing `stateIn` with `SharingStarted.WhileSubscribed(5000)`, the operator tracks active downstream subscribers via reference counting (`subscriptionCount`). "
            "When the last collector unsubscribes, it waits 5 seconds (to tolerate screen rotation) and then cancels the upstream collection coroutine, releasing hardware and database locks."
        ),
        "follow_ups": [
            {
                "interviewer": "Why is the 5-second timeout in `WhileSubscribed(5000)` important?",
                "answer": "During an Android configuration change (like screen rotation), the old Activity/Fragment destroys its view (unsubscribes) and the new view is created and resubscribes within a few hundred milliseconds. A 5-second grace period prevents tearing down and immediately restarting the upstream network or database flow during rotation."
            },
            {
                "interviewer": "What happens if you use `stateIn` with `SharingStarted.Eagerly`?",
                "answer": "The upstream flow starts collecting immediately upon ViewModel instantiation and never stops until the ViewModel is destroyed, even if no UI component is observing the state."
            },
            {
                "interviewer": "Can you call `stateIn` without providing an `initialValue`?",
                "answer": "Only if using the 2-argument overload of `stateIn(scope)`, which is a suspending function that waits for the first upstream emission before returning the StateFlow. In a ViewModel property initializer, you must use the 3-argument non-suspending overload with an explicit `initialValue`."
            }
        ]
    },
    {
        "id": "FLO-09",
        "arabic_explanation": (
            "المقارنة بين استراتيجيات `SharingStarted` في `stateIn` و `shareIn` هي جوهر الحفاظ على موارد الهاتف والبطارية في أندرويد:\n\n"
            "1. `SharingStarted.Eagerly` (البدء الفوري المستمر):\n"
            "   - يبدأ البث فوراً بمجرد إنشاء الـ ViewModel في الذاكرة.\n"
            "   - **لا يتوقف أبداً** حتى لو لم يكن هناك أي مستمع، وحتى لو خرج المستخدم من الشاشة وظل الـ ViewModel حياً في الـ Backstack!\n"
            "   - **الاستخدام:** البيانات الحيوية جداً التي يجب أن تظل محدثة في الخلفية دائماً، ولكن يجب الحذر منه لتجنب إهدار البطارية.\n\n"
            "2. `SharingStarted.Lazily` (البدء الكسول مع أول مستمع):\n"
            "   - لا يبدأ حتى يشترك أول مستمع (First Subscriber).\n"
            "   - **بمجرد أن يبدأ، لا يتوقف أبداً!** حتى لو ألغى كل المستمعين اشتراكاتهم لاحقاً.\n\n"
            "3. `SharingStarted.WhileSubscribed(stopTimeoutMillis)` (الاستراتيجية الذهبية لأندرويد):\n"
            "   - يبدأ العمل فقط عندما يكون هناك مستمع نشط على الشاشة.\n"
            "   - **يتوقف ويلغي الـ Upstream تلقائياً** عندما يغادر آخر مستمع الشاشة بعد انتهاء مهلة الـ Timeout (عادة 5 ثوانٍ).\n"
            "   - **لماذا 5 ثوانٍ (5_000L)؟** لتغطية وقت تدوير الشاشة (Configuration Change)؛ حتى لا نلغي طلب الشبكة أو استعلام الداتابيز ونعيده من الصفر أثناء تدوير الشاشة!"
        ),
        "practical_walkthrough": (
            "مقارنة عملية في استهلاك البطارية والشبكة:\n"
            "```kotlin\n"
            "class FeedViewModel(private val feedRepository: FeedRepository) : ViewModel() {\n"
            "    \n"
            "    // ✅ الاستراتيجية الصحيحة بنسبة 100% في Android:\n"
            "    val feedState: StateFlow<FeedUiState> = feedRepository.observeLiveFeed()\n"
            "        .map { FeedUiState.Success(it) }\n"
            "        .stateIn(\n"
            "            scope = viewModelScope,\n"
            "            started = SharingStarted.WhileSubscribed(5_000L),\n"
            "            initialValue = FeedUiState.Loading\n"
            "        )\n"
            "}\n"
            "```\n"
            "لو المستخدم وضع التطبيق في الخلفية (Background): بعد 5 ثوانٍ يتم إيقاف `observeLiveFeed()` وتوفير بطارية الجهاز. لو فتح التطبيق مجدداً، يعود البث تلقائياً."
        ),
        "quick_answer": "Eagerly starts upstream immediately and never stops; Lazily starts with the first subscriber and stays active permanently; WhileSubscribed(5000) starts with the first subscriber, cancels upstream when subscribers drop to zero after a 5-second grace period, making it the premier choice for battery conservation across Android rotations.",
        "best_answer": (
            "The `SharingStarted` strategy governs the lifecycle of the upstream flow in `stateIn` and `shareIn`, deciding when collection starts and stops based on subscriber presence.\n\n"
            "**SharingStarted.Eagerly** starts collecting from upstream immediately upon creation and never cancels until the parent scope is destroyed, regardless of whether any UI component is observing. It is best for critical background sync tasks that must start immediately.\n\n"
            "**SharingStarted.Lazily** defers execution until the first subscriber collects, but once started, it remains active indefinitely even if all subscribers disconnect. It is suitable for expensive one-time caches that should not restart.\n\n"
            "**SharingStarted.WhileSubscribed(5000)** is the gold standard for Android UI development. It only activates upstream collection when there is at least one active subscriber. When subscribers drop to zero, it waits 5,000 milliseconds before cancelling the upstream flow. This 5-second window prevents cancelling and restarting expensive network or database queries during configuration changes like screen rotations."
        ),
        "deep_answer": (
            "At the technical mechanism level, `WhileSubscribed` monitors the `subscriptionCount` state flow of the underlying `SharedFlow`. "
            "When `subscriptionCount.value` transitions from 0 to 1, it starts the upstream collector coroutine. When it drops back to 0, it launches a delay timer:\n\n"
            "```kotlin\n"
            "SharingStarted.WhileSubscribed(stopTimeoutMillis = 5_000, replayExpirationMillis = 0)\n"
            "```\n\n"
            "If a new subscriber attaches within the 5,000ms window (which happens during Activity recreation upon screen rotation), the cancellation timer is cancelled and upstream collection continues uninterrupted.\n\n"
            "The second parameter, `replayExpirationMillis`, determines when the cached replay buffer is reset. Leaving it at 0 means that when the upstream is cancelled due to inactivity, the cached state is kept. If set to a duration, it evicts stale cached state after the user leaves the screen for an extended period."
        ),
        "follow_ups": [
            {
                "interviewer": "What happens if you use `WhileSubscribed()` without a timeout parameter (i.e. timeout = 0)?",
                "answer": "If timeout is 0, the upstream flow cancels instantly the millisecond the Activity is destroyed during rotation. A fraction of a second later when the new Activity recreates and collects, the flow starts over from scratch, triggering duplicate network requests and UI flickering."
            },
            {
                "interviewer": "Can you unit test `WhileSubscribed(5000)` deterministically?",
                "answer": "Yes. When testing with `runTest` and Turbine, `testScheduler` skips the 5,000ms delay virtually with `advanceTimeBy(5001)`, allowing you to verify that upstream collection halted."
            },
            {
                "interviewer": "Does `WhileSubscribed` work if the UI collects using plain `collectAsState()` in Compose?",
                "answer": "`collectAsState()` does not pause collection when the app is in the background, so `subscriptionCount` never drops to 0 while the composition is active. You must use `collectAsStateWithLifecycle()` to ensure subscribers drop to 0 when the app is backgrounded."
            }
        ]
    },
    {
        "id": "FLO-10",
        "arabic_explanation": (
            "الفرق بين الحالة (State) والأحداث العابرة (Transient Events) هو من أهم النقاط المعمارية لتجنب تكرار الأحداث (Duplicate Events Bug) عند تدوير الشاشة:\n\n"
            "1. ما هي الحالة (State)؟\n"
            "   - تمثل **الوضع الحالي الدائم للواجهة (What the UI looks like right now)**.\n"
            "   - خاصية: **Persistent across Re-renders / Rotations**.\n"
            "   - مثال: قائمة المنتجات، نص البحث، هل الزر معطل أم مفعل، حالة التحميل `isLoading`.\n"
            "   - التمثيل النموذجي: `StateFlow<UiState>`.\n\n"
            "2. ما هي الأحداث العابرة (Transient Events)؟\n"
            "   - تمثل **أفعال تحدث لمرة واحدة فقط (One-off Actions / Side Effects)**.\n"
            "   - خاصية: **Must be consumed exactly once!** ولا يجب إعادة تنفيذها إذا تم تدوير الشاشة.\n"
            "   - مثال: الانتقال لشاشة ثانية (Navigate to Details)، إظهار Snackbar أو Toast برسالة خطأ، أو إغلاق لوحة المفاتيح.\n\n"
            "3. المشكلة الشائعة (The Bug):\n"
            "   - لو تم تخزين حدث الانتقال `Navigate` داخل `StateFlow`: عند تدوير الشاشة، الشاشة الجديدة ستقرأ القيمة المخزنة في `StateFlow.value` وتعيد الانتقال مرة ثانية بالخطأ!\n"
            "   - الحل: استخدام `Channel` أو `SharedFlow` (مع `replay = 0`)، أو نمط استهلاك الحدث في State وإرسال Intent للـ ViewModel بـ `onEventConsumed()`."
        ),
        "practical_walkthrough": (
            "أفضل نمط معماري للتعامل مع الأحداث العابرة في Jetpack Compose و MVI:\n"
            "```kotlin\n"
            "// 1. تعريف الـ Event كـ Sealed Interface:\n"
            "sealed interface LoginSideEffect {\n"
            "    data object NavigateToHome : LoginSideEffect\n"
            "    data class ShowToast(val message: String) : LoginSideEffect\n"
            "}\n"
            "\n"
            "class LoginViewModel : ViewModel() {\n"
            "    // State عادي للواجهة:\n"
            "    val uiState: StateFlow<LoginUiState> = ...\n"
            "    \n"
            "    // Channel للأحداث العابرة (One-off Events):\n"
            "    private val _effectChannel = Channel<LoginSideEffect>(Channel.BUFFERED)\n"
            "    val effects: Flow<LoginSideEffect> = _effectChannel.receiveAsFlow()\n"
            "    \n"
            "    fun onLoginSuccess() {\n"
            "        viewModelScope.launch {\n"
            "            _effectChannel.send(LoginSideEffect.NavigateToHome)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```\n"
            "في الـ UI: نستمع لـ `effects` عبر `LaunchedEffect`؛ يتم استهلاك الحدث مرة واحدة، وتدوير الشاشة لن يكرر الانتقال إطلاقاً."
        ),
        "quick_answer": "State represents persistent screen conditions that survive rotation and should always be observable via StateFlow; transient events are one-off side effects (like navigation or snackbars) that must be consumed exactly once and never replayed on screen rotation, typically modeled using Channel or SharedFlow.",
        "best_answer": (
            "Distinguishing between persistent state and transient events is crucial for preventing duplicate navigation or repeated snackbars in Android.\n\n"
            "**State** represents the durable condition of the UI at any given moment: the list of items, form input text, or loading indicators. State must be retained across configuration changes so that rotating the device immediately restores the exact same visual representation. We model state using `StateFlow`.\n\n"
            "**Transient Events** (also called Side Effects) represent one-off occurrences that must happen exactly once: navigating to a details screen, showing a temporary error Toast, or requesting biometric authentication. If you store an event inside a StateFlow, the new Activity created after a rotation will observe that same StateFlow, re-reading the event and navigating a second time.\n\n"
            "We model transient events either through a separate one-shot stream like `Channel.receiveAsFlow()` or by embedding an event in UI state paired with an explicit confirmation action (`onEventHandled()`)."
        ),
        "deep_answer": (
            "Historically, developers addressed this issue using `SingleLiveEvent` or `Event<T>` wrappers containing an `isHandled` boolean flag. While functional, those patterns are considered workarounds that break reactive purity.\n\n"
            "In modern Android architecture, Google's Architecture Guide recommends two clean approaches: "
            "1. **Channel as Event Stream:** A ViewModel exposes `val sideEffects = effectChannel.receiveAsFlow()`. Channels guarantee single-receiver delivery (FIFO queue); once an event is received and handled by `LaunchedEffect` in Compose, it is dequeued and cannot be replayed on rotation. "
            "2. **State-Driven Events:** Model the event directly inside the UI state with a unique ID: `data class UiState(val userMessage: UserMessage? = null)`. When the UI displays the message, it immediately dispatches an intent `viewModel.onMessageShown(message.id)`, and the ViewModel clears `userMessage = null`. This keeps everything in a single unidirectional state pipeline."
        ),
        "follow_ups": [
            {
                "interviewer": "What is the danger of using `SharedFlow` with `replay = 0` for one-off events?",
                "answer": "If an event is emitted to a `SharedFlow` while the UI is between lifecycles (e.g., during rotation or before `LaunchedEffect` starts collecting), the event is dropped permanently and lost because there were zero active collectors."
            },
            {
                "interviewer": "Why does `Channel(Channel.BUFFERED)` solve that dropped event issue?",
                "answer": "A buffered Channel retains sent items in its internal queue until a collector connects. If an event is sent during rotation, the Channel holds it and delivers it as soon as the recreated screen begins collecting."
            },
            {
                "interviewer": "Can you use Jetpack Compose's `LaunchedEffect` to observe a Channel event flow?",
                "answer": "Yes. `LaunchedEffect(Unit) { viewModel.effects.collect { effect -> handleEffect(effect) } }` is the standard pattern for observing side-effect streams in Compose."
            }
        ]
    },
    {
        "id": "FLO-11",
        "arabic_explanation": (
            "الـ Intermediate Operators في Kotlin Flow بتحدد كيفية تحويل ومراقبة تدفق البيانات بدون استهلاكها حتى يأتي Terminal Operator:\n\n"
            "1. `map`:\n"
            "   - يحول كل عنصر قادم من النوع `A` إلى النوع `B` (1:1 transformation).\n"
            "   - مثال: تحويل `UserDto` القادم من الشبكة إلى `UserUiModel`.\n\n"
            "2. `filter`:\n"
            "   - يمرر فقط العناصر التي تحقق شرطاً معيناً (Predicate) ويتجاهل الباقي.\n"
            "   - مثال: تصفية المنتجات المتاحة فقط في المخزن `filter { it.inStock }`.\n\n"
            "3. `transform`:\n"
            "   - الأب الروحي الأكثر مرونة لـ `map` و `filter`.\n"
            "   - يسمح لك بإصدار 0 أو 1 أو أكثر من عنصر لكل عنصر وارد عبر استدعاء `emit()` اليدوي داخل البلوك.\n\n"
            "4. `onEach`:\n"
            "   - لتنفيذ أثر جانبي (Side Effect) على كل عنصر دون تعديل قيمته.\n"
            "   - مثال: تسجيل السجلات `onEach { Log.d(\"Tag\", it.toString()) }` أو حفظه في Cache.\n\n"
            "5. `launchIn(scope)`:\n"
            "   - دالة مساعدة لجمع الـ Flow داخل `CoroutineScope` محدد بدون الحاجة لكتابة `scope.launch { flow.collect() }`.\n"
            "   - بترجع كائن `Job` يمكن استخدامه لإلغاء المراقبة."
        ),
        "practical_walkthrough": (
            "سلسلة عمليات متكاملة توضح استخدام الـ Operators معاً:\n"
            "```kotlin\n"
            "repository.observeTransactions()\n"
            "    .filter { it.amount > 0 } // 1. استبعاد المعاملات الصفرية\n"
            "    .map { it.toUiDisplay() } // 2. تحويل لنموذج العرض في الواجهة\n"
            "    .onEach { uiModel ->\n"
            "        analytics.trackTransactionRendered(uiModel.id) // 3. أثر جانبي للتتبع\n"
            "    }\n"
            "    .transform { uiModel ->\n"
            "        emit(uiModel) // 4. إصدار العنصر الأصلي\n"
            "        if (uiModel.isHighValue) {\n"
            "            emit(uiModel.createFraudWarning()) // إصدار عنصر إضافي اختياري!\n"
            "        }\n"
            "    }\n"
            "    .onEach { _uiState.value = it }\n"
            "    .launchIn(viewModelScope) // 5. إطلاق الجمع داخل viewModelScope\n"
            "```"
        ),
        "quick_answer": "map transforms elements 1-to-1; filter conditionally allows elements; transform provides arbitrary emissions (0, 1, or many per element) via emit(); onEach performs non-mutating side effects like logging; and launchIn(scope) launches a coroutine to collect the flow, returning a cancellable Job.",
        "best_answer": (
            "These intermediate operators form the core transformation pipeline of Kotlin Flow, executing lazily as upstream emissions arrive:\n\n"
            "**`map`** performs a 1-to-1 transformation, converting an upstream element `T` into `R` (e.g., mapping database entities to domain models).\n\n"
            "**`filter`** evaluates a boolean predicate, allowing only matching elements to proceed downstream.\n\n"
            "**`transform`** is the most versatile foundational operator. It exposes a `FlowCollector`, allowing you to emit zero, one, or multiple transformed elements for each incoming item, or perform complex asynchronous transformations with `emit()`.\n\n"
            "**`onEach`** attaches a side-effect without modifying the stream. It is ideal for logging, telemetry, or updating intermediate in-memory caches.\n\n"
            "**`launchIn(scope)`** is a concise terminal shorthand: instead of writing `scope.launch { flow.collect() }`, calling `.launchIn(scope)` launches collection in the given scope and returns the resulting `Job` for lifecycle management."
        ),
        "deep_answer": (
            "Under the hood, intermediate operators like `map`, `filter`, and `transform` do not launch coroutines. They simply return a new `Flow` instance that wraps the upstream flow's collector with custom logic. "
            "For instance, `map` compiles down to:\n\n"
            "```kotlin\n"
            "inline fun <T, R> Flow<T>.map(crossinline transform: suspend (T) -> R): Flow<R> = transform { value ->\n"
            "    return@transform emit(transform(value))\n"
            "}\n"
            "```\n\n"
            "Because `transform` is inlined, chaining multiple operators like `filter { ... }.map { ... }` generates virtually zero intermediate object allocations in hot paths, executing within the collector's original coroutine frame.\n\n"
            "Contrast this with `launchIn(scope)`: `launchIn` is a terminal operator that invokes `scope.launch { collect() }`. In clean architecture, we prefer `launchIn` or `repeatOnLifecycle` at the UI layer, but avoid launching unconfined streams inside pure repository layers."
        ),
        "follow_ups": [
            {
                "interviewer": "Can you call suspending functions inside `map` and `filter`?",
                "answer": "Yes! All transformation lambdas in Flow operators (`map`, `filter`, `transform`, `onEach`) are suspending lambdas (`suspend (T) -> R`), allowing you to call suspending repository functions or database queries directly inside the stream."
            },
            {
                "interviewer": "Does `launchIn` catch exceptions thrown upstream?",
                "answer": "No. `launchIn` merely launches a coroutine to call `collect()`. Any unhandled upstream exception will propagate to the parent scope unless guarded with the `.catch { }` operator prior to `launchIn`."
            },
            {
                "interviewer": "What is the difference between `onEach` and `map`?",
                "answer": "`map` alters the downstream value by returning a new item. `onEach` performs a side-effect and forwards the original upstream value unchanged."
            }
        ]
    },
    {
        "id": "FLO-12",
        "arabic_explanation": (
            "المقارنة بين المشغلات النهائية (Terminal Operators) `collect` و `collectLatest` و `first`:\n\n"
            "1. المشغل `collect`:\n"
            "   - يجمع **كل عنصر بالترتيب** وينفذ البلوك الخاص به حتى ينتهي بالكامل قبل الانتقال للعنصر التالي.\n"
            "   - يطبق Backpressure: لو معالجة العنصر استغرقت ثانيتين، الـ Producer ينتظر ويتعلق حتى ينتهي الـ Collector.\n"
            "   - يضمن معالجة 100% من العناصر بدون إسقاط أي عنصر.\n\n"
            "2. المشغل `collectLatest`:\n"
            "   - **يلغي معالجة العنصر الحالي إذا وصل عنصر جديد فوراً!**\n"
            "   - لو البلوك شغال بيعالج العنصر 1، ووصل العنصر 2، يلغي الـ Coroutine الخاصة بالعنصر 1 ويبدأ فوراً في معالجة العنصر 2.\n"
            "   - مناسب جداً لواجهات المستخدم (UI updates والبحث): إذا غير المستخدم نص البحث، لا نريد استكمال البحث عن النص القديم؛ نلغيه ونبحث عن النص الأحدث.\n\n"
            "3. المشغل `first`:\n"
            "   - يأخذ **أول عنصر فقط** يطابق الشرط، ثم **يلغي الـ Flow بالكامل فوراً** ويرجع القيمة للمتصل.\n"
            "   - يحول الـ Flow إلى دالة One-shot suspend ترجع قيمة مفردة."
        ),
        "practical_walkthrough": (
            "مقارنة عملية في شاشة البحث وتفاصيل المستخدم:\n"
            "```kotlin\n"
            "// 1. استخدام collectLatest في البحث بالـ UI:\n"
            "searchQueryFlow.collectLatest { query ->\n"
            "    val results = api.search(query) // لو المستخدم كتب حرف جديد أثناء الطلب، يتم إلغاء هذا الطلب فوراً!\n"
            "    _uiState.value = results\n"
            "}\n"
            "\n"
            "// 2. استخدام first لجلب التوكن لمرة واحدة (One-shot read):\n"
            "suspend fun getAuthToken(): String {\n"
            "    // نأخذ أول قيمة غير فارغة ونلغي تدفق الـ DataStore فوراً:\n"
            "    return dataStore.tokenFlow.first { it.isNotEmpty() }\n"
            "}\n"
            "\n"
            "// 3. استخدام collect لتسجيل أحداث في Analytics (يجب معالجة كل حدث):\n"
            "analyticsEventsFlow.collect { event ->\n"
            "    analyticsSdk.log(event) // يضمن عدم إسقاط أي حدث!\n"
            "}\n"
            "```"
        ),
        "quick_answer": "collect processes every single emitted element sequentially without dropping items; collectLatest cancels the processing block of the previous element as soon as a new element arrives; and first() retrieves only the first matching element and cancels the stream immediately.",
        "best_answer": (
            "These three terminal operators handle stream consumption with distinct execution and cancellation semantics:\n\n"
            "**`collect`** is the baseline terminal operator. It processes every emission sequentially. If processing an item takes 500ms, upstream suspension ensures no items are skipped or cancelled. I use `collect` when every event must be processed, such as database synchronization or analytics logging.\n\n"
            "**`collectLatest`** is optimized for UI state and search. When a new emission arrives while the previous emission's block is still executing, `collectLatest` cancels the previous block's coroutine and starts processing the new item immediately. If a user types 'A' then quickly 'B', the API call for 'A' is cancelled mid-flight in favor of 'B'.\n\n"
            "**`first()`** is a suspending function that takes the very first emitted value (or the first value matching a predicate) and immediately cancels the flow. It effectively converts a continuous stream into a one-shot query, ideal for reading an initial token from DataStore."
        ),
        "deep_answer": (
            "Under the hood, `collectLatest` is implemented using `channelFlow` and `mapLatest` mechanics. "
            "Every time upstream emits, `collectLatest` cancels the inner child coroutine using `CancellationException`. "
            "However, this introduces an important production caveat: **if the work inside `collectLatest` does not suspend, it cannot be cancelled!** "
            "Cancellation is cooperative: if your block executes a non-suspending synchronous calculation without checking `ensureActive()`, `collectLatest` cannot cancel it midway.\n\n"
            "With `first()`, the implementation works by throwing a private, internal `AbortFlowException` once the first matching element is collected, which unwinds the collector and safely terminates upstream collection without bubbling an error to the caller.\n\n"
            "In unit testing with Turbine, `awaitItem()` behaves like `first()` by synchronously verifying and consuming one item from the testing event queue."
        ),
        "follow_ups": [
            {
                "interviewer": "What happens if a flow is empty and you call `first()`?",
                "answer": "Calling `first()` on an empty flow throws a `NoSuchElementException: Expected at least one element`. You should use `firstOrNull()` if the flow might complete without emissions."
            },
            {
                "interviewer": "Can `collectLatest` result in wasted work?",
                "answer": "Yes, if the cancelled work was an expensive network call that already triggered a server-side side effect. For write operations (like placing an order or saving data), always use standard `collect` to ensure operations run to completion."
            },
            {
                "interviewer": "How does `first()` compare to `take(1).collect()`?",
                "answer": "`take(1).collect { }` limits the stream to 1 item and collects it, but returns `Unit`. `first()` is a suspending function that returns the actual element `T` directly."
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

    for q in FLO_07_12:
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
    print(f"Updated {DATA_FILE} with questions FLO-07 to FLO-12. Total questions: {len(combined)}")


if __name__ == "__main__":
    main()

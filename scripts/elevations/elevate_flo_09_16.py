#!/usr/bin/env python3
"""Elevate FLO-09 through FLO-16 with bilingual content parity and conversational spoken answers."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import elevation_engine as ee

TOPIC_AR = "الـ Flow و StateFlow و SharedFlow والـ Channels"
REVIEWED_DATE_AR = "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."

DATA = {}

# ==========================================
# FLO-09: SharingStarted.Eagerly, Lazily, WhileSubscribed
# ==========================================
DATA["FLO-09"] = {
    "concept_en": """The SharingStarted strategy parameter in stateIn and shareIn governs the precise execution lifecycle of the upstream cold flow subscription, dictating when data production commences and terminates based on collector presence.
SharingStarted.Eagerly starts upstream collection immediately upon instantiation of the sharing coroutine and executes indefinitely until the parent CoroutineScope terminates, regardless of whether any UI subscriber ever collects the stream.
SharingStarted.Lazily defers upstream execution until the very first subscriber attaches, but once activated, it remains executing permanently even if all subscribers subsequently detach.
SharingStarted.WhileSubscribed(stopTimeoutMillis, replayExpirationMillis) provides the standard Android UI lifecycle strategy. It activates upstream production only when at least one active subscriber is observing, and introduces a configurable grace period (typically 5,000 milliseconds) when the subscriber count drops to zero. This 5-second window prevents wasteful upstream cancellation and restart cycles during transient configuration changes like screen rotations, while ensuring physical resources such as network sockets, database query observers, and hardware sensors are cleanly shut down when the screen is placed in the background.""",
    "walkthrough_en": """Configuring sharing strategies in an Android ViewModel:
```kotlin
class LiveScoresViewModel(private val repository: ScoresRepository) : ViewModel() {
    // Standard Android presentation strategy:
    // Survives screen rotation without restarting, stops 5s after app backgrounds
    val matchScores: StateFlow<MatchUiState> = repository.observeLiveScores()
        .map { MatchUiState.Live(it) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(stopTimeoutMillis = 5_000),
            initialValue = MatchUiState.Loading
        )

    // Eager background sync: runs continuously while ViewModel is alive
    val unreadBadgeCount: StateFlow<Int> = repository.observeUnreadCount()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.Eagerly,
            initialValue = 0
        )
}
```""",
    "short_en": """SharingStarted controls when upstream collection starts and stops in stateIn and shareIn. Eagerly starts immediately and never stops; Lazily starts with the first subscriber and runs forever; WhileSubscribed with a 5000ms timeout activates only while UI subscribers exist and waits five seconds before cancelling, bridging screen rotations while preserving battery in the background.""",
    "structured_en": """To begin with, the SharingStarted policy dictates the lifetime and execution boundary of the upstream coroutine in stateIn and shareIn.
From an architectural standpoint, each policy strikes a different balance between freshness and resource consumption. Eagerly starts upstream production the instant the ViewModel is instantiated, ignoring subscriber presence completely. We reserve it for critical background sync tasks that must start immediately.
In production scenarios, Lazily defers execution until the initial subscriber attaches, but continues running even after all subscribers detach. This makes it suitable for immutable caches that should warm up on demand without restarting.
As for boundary management, WhileSubscribed with a five-second timeout is the definitive gold standard for Android presentation layers. When UI collectors transition to zero during screen rotation, the five-second countdown prevents tearing down expensive database or WebSocket connections. If the user navigates away or backgrounds the app, the timer elapses and cancels upstream production, stopping battery drain and radio activity.""",
    "deep_senior_en": """Under the hood in kotlinx.coroutines, WhileSubscribed is implemented by observing the subscriptionCount StateFlow of the underlying SharedFlow instance. When subscriptionCount transitions from zero to one, WhileSubscribed emits SharingCommand.START, instructing the sharing loop to launch the upstream collector coroutine.
When subscriptionCount drops back to zero, such as when an Activity invokes onStop and unbinds its repeatOnLifecycle block, WhileSubscribed emits a command sequence: it introduces a delay of stopTimeoutMillis, followed by SharingCommand.STOP. If a new subscriber arrives before the timer completes—which reliably happens during Activity recreation within 300 milliseconds—subscriptionCount rises back to one, aborting the pending cancellation timer and keeping the upstream connection intact.
The second configuration parameter, replayExpirationMillis, governs cache freshness. Setting replayExpirationMillis to zero preserves the cached state indefinitely during pauses. Supplying a non-zero timeout resets the replay cache to initialValue once the timeout elapses, preventing the UI from showing stale financial data when the user returns after thirty minutes.
Additionally, in automated unit testing, test dispatchers pause virtual time; developers must call advanceTimeBy(5001) to simulate subscriber detachment and verify that the upstream sharing job was cancelled cleanly as expected.
Staff engineers pair WhileSubscribed(5000) with collectAsStateWithLifecycle in Jetpack Compose or repeatOnLifecycle in Views. Using plain collectAsState fails to decrement subscriptionCount in the background, keeping WhileSubscribed running perpetually and defeating battery conservation.""",
    "meta_ar": {
        "id": "FLO-09",
        "questionAr": "قارن بين استراتيجيات SharingStarted: Eagerly و Lazily و WhileSubscribed",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- فهم كيفية إدارة دورة حياة التدفق العلوي (Upstream) في stateIn و shareIn.\n- التمييز بين التشغيل الدائم والتشغيل الكسول والتشغيل المشروط بوجود مستمعين.\n- استيعاب سبب اختيار مهلة 5000 مللي ثانية مع WhileSubscribed لحماية البطارية وتجاوز تدوير الشاشة.",
        "why_it_matters_ar": "الاستراتيجية الخاطئة في `SharingStarted` قد تدمر أداء التطبيق وبطارية الجهاز؛ فاستخدام `Eagerly` أو `Lazily` مع تدفقات تراقب الموقع الجغرافي أو الـ WebSockets يبقي الحساسات واتصالات الشبكة مفتوحة في الخلفية حتى بعد خروج المستخدم، بينما ضبط `WhileSubscribed` بدون مهلة يعيد تشغيل الاتصالات من الصفر مع كل لفة شاشة.",
        "worked_example_ar": "النمط الذهبي لإدارة حالة الشاشة مع حماية موارد الجهاز:\n```kotlin\nclass ScoresViewModel(repo: ScoresRepository) : ViewModel() {\n    val scores: StateFlow<ScoresUiState> = repo.observeLiveScores()\n        .map { ScoresUiState.Success(it) }\n        .stateIn(\n            scope = viewModelScope,\n            started = SharingStarted.WhileSubscribed(stopTimeoutMillis = 5_000),\n            initialValue = ScoresUiState.Loading\n        )\n}\n```\nأثناء تدوير الشاشة، مهلة الـ 5 ثوانٍ تمنع قطع الاتصال، وعند غلق التطبيق يُلغى الاستعلام تلقائياً.",
        "trade_offs_ar": "استراتيجية `Eagerly` توفر البيانات فوراً بدون انتظار أول مستمع ولكنها تهدر البطارية مبكراً. `Lazily` توفر الموارد في البداية لكنها لا تغلق المصدر أبداً بعد بدئه. `WhileSubscribed(5000)` توفر الموارد وتتكيف مع دورة حياة الواجهة بامتياز.",
        "failure_modes_ar": "استخدام `WhileSubscribed(0)` مما يتسبب في إلغاء تدفق الشبكة وإعادة تشغيله مع كل تدوير للشاشة مما يسبب وميضاً في الواجهة. خطأ آخر هو جمع التدفق بـ `collectAsState()` العادي في Compose مما يجعل عدد المشتركين لا ينخفض للصفر أبداً في الخلفية.",
        "production_perspective_ar": "في المشروعات الإنتاجية الكبرى، نعتمد `WhileSubscribed(5_000)` كمعيار إلزامي لجميع شاشات العرض بالاشتراك مع `collectAsStateWithLifecycle`، ونلزم الفرق بعدم استخدام `Eagerly` إلا لعمليات التزامن الخلفية الحرجة جداً على مستوى الـ Singleton Repository.",
        "how_to_answer_ar": "- **الوظيفة المعمارية:** معامل `SharingStarted` يتحكم في توقيت بدء وإلغاء جمع التدفق العلوي في `stateIn` و `shareIn`.\n- **Eagerly:** يبدأ فوراً ويستمر للأبد دون النظر لوجود مستمعين.\n- **Lazily:** ينتظر أول مستمع، وبمجرد أن يبدأ يستمر للأبد حتى لو غادر الجميع.\n- **WhileSubscribed(5000):** المعيار الذهبي لأندرويد؛ يعمل فقط بوجود مستمع نشط، ويمهل التطبيق 5 ثوانٍ عند انعدام المشتركين لتجاوز تدوير الشاشة وحماية البطارية.\n- **التكامل مع Compose:** التأكيد على ضرورة استخدام `collectAsStateWithLifecycle` حتى يتم تصفير العداد في الخلفية.",
        "talking_points_ar": "ناقش تدفق `subscriptionCount` الداخلي في SharedFlow، وأوامر START و STOP في محرك SharingStarted، ودور معامل `replayExpirationMillis` في تنظيف الكاش القديم عند الغياب الطويل.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لو استخدمت WhileSubscribed بدون مهلة (timeout = 0)؟\"\n  **المرشح:** \"مع تدوير الشاشة، الـ Activity بتتدمر وتتنشئ في 300 مللي ثانية؛ لو المهلة صفر، التدفق العلوي هيتلغي في نفس اللحظة وهيبدأ من الصفر مع الشاشة الجديدة، وده هيكرر طلبات الشبكة ويسبب وميضاً مزعجاً في الواجهة.\"\n\n- **المحاور:** \"هل WhileSubscribed بتوفر بطارية لو بنستخدم `collectAsState()` في Compose؟\"\n  **المرشح:** \"لأ، لأن `collectAsState()` العادية ملهاش علاقة بدورة حياة الـ Lifecycle وبتفضل مجمعة طالما الـ Composable في الذاكرة، فـ subscriptionCount مبيوصلش للصفر في الـ Background. لازم نستخدم `collectAsStateWithLifecycle()` علشان تفصل في onStop والعداد ينزل للصفر.\"",
        "self_check_ar": "هل وضحت الفارق بين الاستراتيجيات الثلاث؟ هل بررت سر الـ 5 ثوانٍ؟ وهل نبهت لأهمية collectAsStateWithLifecycle؟",
        "references_ar": f"- [Kotlin SharingStarted official docs](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-sharing-started/) — توثيق كوتلن الرسمي.\n- [Things to know about StateFlow and WhileSubscribed](https://medium.com/androiddevelopers/things-to-know-about-flows-sharein-and-statein-operators-20e6ccb2b09a) — مقال فريق أندرويد الرسمي.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "استراتيجيات `SharingStarted` بتحدد إمتى التدفق العلوي يبدأ ويقف في `stateIn`. `Eagerly` بيبدأ فوراً ومبيوقفش خالص، و`Lazily` بيبدأ مع أول مستمع وبيفضل شغال للأبد، أما `WhileSubscribed(5000)` فده المعيار الذهبي في أندرويد؛ بيشتغل بس لما تكون الشاشة مفتوحة وفيها مستمعين، وبيديك مهلة 5 ثوانٍ عند تدوير الشاشة قبل ما يلغي التدفق ويوفر البطارية.",
        "best_answer_ar": "استراتيجيات `SharingStarted` هي المسؤولة عن التحكم في دورة حياة الـ Upstream Flow اللي بنحوله بـ `stateIn` أو `shareIn`، وقرار اختيارها بيأثر مباشرة على استهلاك البطارية والشبكة.\n\nاستراتيجية `Eagerly` بتبدأ التجميع فور إنشاء الـ ViewModel في الذاكرة ومبتوقفش أبداً لحد ما الـ Scope كله يتلغي، حتى لو مفيش ولا عنصر واجهة بيسمع، وبنستخدمها فقط لمزامنة خلفية حرجة جداً لازم تشتغل فوراً.\n\nأما `Lazily` فبتأجل الشغل لحد ما أول جامع يشترك في التدفق، لكن بمجرد ما تبدأ، بتفضل شغالة على طول ومش بتلغي الاشتراك حتى لو كل الشاشات قفلت، وده مناسب لكاش البيانات الثابتة اللي بنجهزه لمرة واحدة.\n\nالخيار القياسي لأي شاشة أندرويد هو `WhileSubscribed(5_000)`؛ لأنها بتربط تشغيل المصدر بوجود مستمع نشط في الواجهة، وأول ما عدد المشتركين ينزل لصفر، بتبدأ عداد مدته 5 ثوانٍ. لو المستخدم كان مجرد بيدور الشاشة، الشاشة الجديدة بتشترك خلال جزء من الثانية والاشتراك بيفضل مكمل بدون إعادة طلب الداتا. ولو نزل التطبيق في الخلفية، الـ 5 ثوانٍ بتخلص والتدفق بيتلغي ويوفر البطارية.",
        "deep_answer_ar": "على مستوى الميكانيزم الداخلي في مكتبة الكوروتينات، `WhileSubscribed` بتراقب الـ `subscriptionCount` بتاع الـ SharedFlow كـ StateFlow داخلي. لما العداد يتحول من 0 لـ 1، المشغل بيبعت أمر اسمه `SharingCommand.START` لمسار التجميع العلوي، فيبدأ يطلب داتا من الـ Room أو الـ WebSocket.\n\nولما العداد ينزل لـ 0، زي لما المستخدم يخرج من الشاشة وتدخل في `onStop` مع `repeatOnLifecycle`، المشغل مبيوقفش فوراً؛ هو بيعمل delay بقيمة `stopTimeoutMillis` اللي هي 5000 مللي ثانية. لو الـ Activity اتعاد تدويرها في الـ Configuration Change، الشاشة الجديدة بتشترك في خلال 300 مللي ثانية، فالعداد بيطلع لـ 1 تاني، والمشغل بيلغي مؤقت التوقف وبيفضل الاتصال مفتوح ومستقر بدون أي استهلاك إضافي.\n\nالمعامل التاني المهم في الدالة هو `replayExpirationMillis`؛ ده بيحدد صلاحية الكاش بعد ما المشتركين يمشوا. القيمة الافتراضية صفر بتخلي الكاش يفضل محفوظ في الذاكرة، لكن لو حددت مدة زمنية، الـ StateFlow بيفضي الكاش ويرجع للـ `initialValue` لو المستخدم غاب فترة طويلة علشان ميشوفش أسعار أو أرصدة قديمة أول ما يرجع.\n\nوفي تطبيقات الإنتاج، بنحذر دائماً من استخدام `collectAsState()` العادية في Compose مع `WhileSubscribed`، لأنها مابتوقفش الاشتراك لما التطبيق يروح في الخلفية، والحل الصارم هو استخدام `collectAsStateWithLifecycle()` لضمان انخفاض العداد إلى الصفر وتوفير موارد الجهاز."
    }
}

# ==========================================
# FLO-10: State vs Transient Events
# ==========================================
DATA["FLO-10"] = {
    "concept_en": """In reactive Android architecture, distinguishing between persistent State and transient Events is fundamental to predictable UI rendering and avoiding duplicate side effects.
State represents an enduring, observable snapshot of the user interface at any given instant—such as a list of loaded products, a loading spinner visibility flag, or an error screen layout. State is persistent, non-destructive, supports immediate replay to newly attached observers, and conflates intermediate updates so that collectors always receive the freshest representation.
Transient Events represent momentary, one-off side effects that must be consumed exactly once—such as triggering screen navigation, showing a SnackBar notification, requesting biometric authentication, or playing an audio alert. Events must not persist in the UI state buffer; if an event is held in a regular state stream, configuration changes like screen rotations cause newly recreated UI observers to collect the cached event a second time, triggering repeated navigation loops or duplicate toast popups.""",
    "walkthrough_en": """Contrasting UI state with one-off transient events in an Android ViewModel:
```kotlin
// 1. UI State: Persistent snapshot of screen data
data class CheckoutUiState(
    val isProcessing: Boolean = false,
    val cartTotal: BigDecimal = BigDecimal.ZERO
)

// 2. Transient Events: One-off navigation or snackbar intents
sealed interface CheckoutUiEvent {
    data class NavigateToReceipt(val orderId: String) : CheckoutUiEvent
    data class ShowErrorSnackBar(val message: String) : CheckoutUiEvent
}

class CheckoutViewModel : ViewModel() {
    // State: Exposed via StateFlow with initial loading state
    private val _uiState = MutableStateFlow(CheckoutUiState())
    val uiState: StateFlow<CheckoutUiState> = _uiState.asStateFlow()

    // Events: Exposed via Channel or SharedFlow(replay = 0)
    private val _eventChannel = Channel<CheckoutUiEvent>(Channel.BUFFERED)
    val events = _eventChannel.receiveAsFlow()

    fun completeCheckout() {
        viewModelScope.launch {
            _uiState.update { it.copy(isProcessing = true) }
            val orderId = api.placeOrder()
            _uiState.update { it.copy(isProcessing = false) }
            // Transient event sent once:
            _eventChannel.send(CheckoutUiEvent.NavigateToReceipt(orderId))
        }
    }
}
```""",
    "short_en": """State represents a continuous, persistent snapshot of the screen that survives rotation and supports replay. Transient events represent one-shot actions like navigation or toasts that must execute exactly once. Storing transient events in StateFlow causes duplicate execution upon rotation, requiring either Channel-backed event streams or consumed state flags.""",
    "structured_en": """To begin with, the architectural dichotomy between state and transient events dictates how data streams are modeled and consumed.
From an architectural standpoint, state represents what the screen currently displays. It is persistent, stateful, and must replay immediately when an Activity recreates after rotation. We model UI state using StateFlow, conflating updates so the UI always reflects the latest snapshot.
In production scenarios, transient events represent fire-and-forget side effects like triggering navigation, displaying a toast, or vibrating the haptic engine. These actions must be delivered and processed exactly once.
As for boundary management, modeling one-off events inside a StateFlow is a frequent source of severe bugs. When the device rotates, newly registered collectors re-read the cached state, causing redundant navigation commands or re-showing dismissed SnackBars. We solve this by modeling events as Channel-backed streams or resetting state properties via explicit event consumption patterns.""",
    "deep_senior_en": """At the system and lifecycle boundary level, handling transient events reliably in Android coroutines has undergone substantial architectural evolution. Naive historical patterns, such as SingleLiveEvent or wrapping events in an Event<T> wrapper with a getContentIfNotHandled() flag, suffered from race conditions and anti-pattern state mutability inside the presentation layer.
Modern reactive patterns utilize two primary production approaches. The first approach is Channel-based event streaming: creating a private Channel<Event>(Channel.BUFFERED) and exposing it downstream via channel.receiveAsFlow(). Because a Channel operates on queue semantics with individual message delivery, each emitted event is consumed by exactly one collector and immediately dequeued. However, if an event is emitted while the UI is between onStop and onStart, the Channel buffers the event in memory until the UI lifecycle resumes and collects it.
The second, increasingly recommended pattern from Google Android Architecture guidelines is Pure State Modeling: treating UI messages as part of the immutable UiState data class. In this pattern, the state includes a nullable message object with a unique identifier. Once the Composable or Fragment displays the SnackBar, it invokes an explicit callback on the ViewModel (such as onMessageDismissed(messageId)), which updates the StateFlow to nullify that specific event property.
Staff engineers select pure state modeling for user-facing visual notifications to guarantee state idempotency, while reserving Channels for critical single-shot operational commands like navigation transitions.""",
    "meta_ar": {
        "id": "FLO-10",
        "questionAr": "ما الفرق الجوهري بين الحالة (State) والأحداث المؤقتة (Transient Events)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- التمييز المعماري بين الحالة المستمرة والأحداث الفردية العابرة (One-shot Actions).\n- فهم كارثة تكرار الأحداث (Event Replay Bug) مع تدوير الشاشة عند وضع الأحداث في StateFlow.\n- معرفة الحلول الهندسية المتبعة: Channel-backed Flow أو نمط استهلاك الحالة الصريح.",
        "why_it_matters_ar": "الخلط بين الحالة والأحداث يتسبب في أخطاء إنتاجية شهيرة؛ مثل فتح شاشة الدفع مرتين متتاليتين عند تدوير الهاتف، أو تكرار ظهور رسالة الخطأ (SnackBar) كلما تنقل المستخدم بين التطبيقات، مما يربك تجربة المستخدم ويؤدي لعمليات سحب مالي مكررة.",
        "worked_example_ar": "عزل الحالة الدائمة عن أحداث الملاحة الفردية:\n```kotlin\n// الحالة: تعرض بشكل مستمر وتتحمل التدوير\nval uiState: StateFlow<CheckoutState> = _uiState.asStateFlow()\n\n// الأحداث المؤقتة: تستهلك مرة واحدة فقط عبر Channel\nprivate val _events = Channel<UiEvent>(Channel.BUFFERED)\nval events = _events.receiveAsFlow()\n\nfun onPaymentSuccess() {\n    _events.send(UiEvent.NavigateToReceipt) // لن تتكرر مع تدوير الشاشة\n}\n```",
        "trade_offs_ar": "نمذجة الأحداث داخل `Channel` تضمن تسليم الحدث مرة واحدة فقط بدون تكرار، ولكنها تتطلب استهلاكاً واعياً للـ Backpressure. أما نمط دمج الأحداث في الـ State مع دالة استهلاك صريحة فهو أسهل في الاختبارات لكنه يتطلب كوداً إضافياً لإبلاغ الـ ViewModel بانتهاء العرض.",
        "failure_modes_ar": "وضع أحداث التنقل في `MutableStateFlow`، مما يجعل أي جامع جديد بعد تدوير الشاشة يقرأ نفس الحدث ويعيد الانتقال مجدداً. خطأ آخر هو استخدام `SharedFlow` بدون تخزين مؤقت بينما الشاشة في الخلفية، مما يؤدي لضياع الحدث تماماً.",
        "production_perspective_ar": "في المشروعات المصرفية والتطبيقات الكبرى، نعتمد إما `Channel` للأحداث التي يجب ألا تضيع (Navigation / Payment results)، أو ندمج رسائل التنبيهات داخل كائن الحالة `UiState` مع إجبار الواجهة على استدعاء `onEventHandled(id)` لحذفها من الحالة وضمان عدم تكرارها نهائياً.",
        "how_to_answer_ar": "- **الفرق المعماري:** الحالة (State) هي وصف مستمر للشاشة وما تحتويه؛ أما الحدث (Event) فهو فعل عابر يحدث لمرة واحدة وينتهي (زي Navigation أو Toast).\n- **مشكلة التدوير:** الـ StateFlow يحتفظ بآخر قيمة ويعيد بثها للجامع الجديد؛ فلو وضعت Event جواه، هيتكرر مع تدوير الشاشة.\n- **حلول الإنتاج:** استخدام `Channel` كطابور أحداث يُستهلك مرة واحدة، أو نمذجة الحدث داخل الـ UiState مع دالة `onDismiss` لمسحه.\n- **تطور الحلول:** التحذير من الأنماط القديمة زي SingleLiveEvent أو Event wrapper ومقارنتها بالتوجيهات الحديثة.",
        "talking_points_ar": "ناقش عيوب SingleLiveEvent و EventWrapper، وسلوك طابور الـ Channel عند تعليق الشاشة في onStop، وإرشادات جوجل الرسمية لنمذجة رسائل الواجهة كجزء من الـ State.",
        "follow_ups_ar": "- **المحاور:** \"لماذا لا نستخدم SharedFlow(replay = 0) لإرسال أحداث الملاحة؟\"\n  **المرشح:** \"لو أرسلت حدث في SharedFlow والشاشة كانت في الخلفية (بين onStop و onStart) ومفيش جامع نشط بيسمع، الحدث هيضيع في الهواء تماماً بدون أي استهلاك. على عكس الـ Channel اللي بيحفظ الحدث في الـ Buffer لحد ما الواجهة ترجع تشتغل وتستلمه.\"\n\n- **المحاور:** \"ما هي الطريقة المفضلة في الدليل الرسمي لجوجل للتعامل مع أحداث الواجهة؟\"\n  **المرشح:** \"جوجل بتفضل نمذجة رسائل الواجهة داخل كائن الـ UiState نفسه كعنصر قابل للـ Null أو له ID فريد، والـ Composable أول ما يعرض الرسالة يستدعي دالة في الـ ViewModel زي `userMessageShown(id)` علشان يصفر القيمة ويضمن عدم تكرارها مع الحفاظ على مبدأ UDF الكامل.\"",
        "self_check_ar": "هل فرقت بدقة بين ماهية State وماهية Event؟ هل بينت كارثة تكرار الحدث مع تدوير الشاشة؟ وهل شرحت Channel و Consumed State؟",
        "references_ar": f"- [Android UI events official guide](https://developer.android.com/topic/architecture/ui-layer/events) — إرشادات جوجل الرسمية لأحداث الواجهة.\n- [StateFlow and SharedFlow event pitfalls](https://medium.com/androiddevelopers/a-safer-way-to-collect-gestures-and-events-in-android-4a34b2230a10) — تجنب مشاكل الأحداث المؤقتة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الحالة (State) هي لقطة مستمرة ودائمة لشكل الشاشة زي القوائم والتحميل وبتحتفظ بآخر قيمة مع تدوير الشاشة. أما الحدث (Event) فده أمر عابر بيحصل مرة واحدة بس زي فتح شاشة جديدة أو إظهار رسالة تنبيه. وضع الأحداث في StateFlow بيسبب كارثة تكرارها مع التدوير، وعلاجها استخدام Channel أو مسح الحدث فور استهلاكه.",
        "best_answer_ar": "التمييز بين الـ State والـ Event هو جوهر تصميم واجهات المستخدم التفاعلية بطريقة تمنع الـ Bugs العشوائية.\n\nالـ `State` بتمثل الوضع الحالي المستمر للشاشة؛ يعني الشاشة بتعرض إيه دلوقتي: هل فيه لودينج؟ هل القائمة مليانة؟ البيانات دي مستمرة ومش مؤقتة، ولازم أول ما المستخدم يدور الشاشة والـ Activity تتنشئ من جديد تستلم نفس القيمة فوراً عبر `StateFlow` بدون ما تفقد بياناتها.\n\nأما الـ `Event` فده فعل عابر ولحظي بيحصل مرة واحدة بس (One-off Action) ومينفعش يتكرر؛ زي الانتقال لشاشة الدفع، أو إظهار رسالة SnackBar، أو طلب بصمة الإصبع.\n\nالكارثة الإنتاجية بتحصل لما المطور يحط الـ Events دي جوه كائن StateFlow؛ لأن الـ StateFlow بيحتفظ بآخر قيمة ويعيد بثها لأي مشترك جديد، فالمستخدم لما يدور شاشة الموبايل، الشاشة الجديدة هتستلم نفس حدث الانتقال القديم وتفتحه مرة تانية في حلقة مفرغة!\n\nعلشان كده في بيئات الإنتاج، بنفصل الأحداث العابرة إما عبر `Channel` بيضمن تسليم الحدث لمستهلك واحد فقط ومسحه فوراً، أو بنحط الحدث جوه كائن الـ UiState مع دالة استهلاك صريحة زي `onEventHandled()` بتمسح الحدث بعد تنفيذه مباشرة.",
        "deep_answer_ar": "في تاريخ تطوير أندرويد، محاولة حل مشكلة الـ One-off Events مرت بمراحل كتيرة؛ بدأنا بـ `SingleLiveEvent` ثم كلاس `Event<T>` الشهير اللي بيعتمد على فلاج داخلي اسمه `hasBeenHandled`. المشكلة المعمارية في الأنماط دي إنها كانت بتسمح بتعديل المتغيرات داخل طبقة العرض وتخلق مشاكل في الـ Concurrency والـ Unit Testing.\n\nالحل الأول الحديث هو استخدام `Channel<UiEvent>(Channel.BUFFERED)`. ميزة الـ Channel إنه شغال بنظام الطابور (Queue)؛ الحدث بينبعث ويستهلكه مشترك واحد بس ويتحذف من الطابور فوراً، وده بيقضي تماماً على مشكلة تكرار الحدث عند تدوير الشاشة. الميزة التانية إنه لو الحدث انبعث والشاشة كانت في الخلفية، الـ Buffer بيحفظ الحدث ومبيسقطوش، وأول ما الكوروتين تصحى في `repeatOnLifecycle` بتستلم الحدث بدون أي فقدان.\n\nالحل التاني واللي بتفضله جوجل حالياً في هندسة Jetpack Compose هو نمط الـ Pure State Modeling؛ إننا نعتبر الرسائل والتنبيهات جزء من الـ UiState نفسه كـ Data Class. مثلاً الـ State بيكون جواه `userMessage: UserMessage?`، ولما الـ Composable يعرض الـ SnackBar، بيستدعي دالة في الـ ViewModel زي `dismissMessage(messageId)`. الدالة دي بتعمل `update` للـ StateFlow وترجع الخاصية لـ null.\n\nفي المشاريع البنكية والتطبيقات الكبيرة، بنفضل الـ Channels لعمليات الملاحة الحساسة وإشارات قفل الجلسة (Logout)، وبنستخدم الـ State Modeling لرسائل الواجهة البصرية لضمان الحتمية الكاملة ومطابقة معايير الاختبارات الآلية."
    }
}

# ==========================================
# FLO-11: map, filter, transform, onEach, launchIn
# ==========================================
DATA["FLO-11"] = {
    "concept_en": """Kotlin Flow operators provide a functional, declarative pipeline for processing, transforming, and consuming asynchronous data streams.
map transforms each emitted upstream element by applying a synchronous or suspending transformation function, yielding a 1:1 stream of transformed items.
filter evaluates each upstream emission against a boolean predicate, forwarding only elements that satisfy the condition (1:0 or 1:1).
transform is the foundational, highly flexible generalization of map and filter; its lambda receiver is a FlowCollector, allowing developers to emit zero, one, or multiple values (1:N) for every incoming upstream element, or conditionally emit based on complex business rules.
onEach executes a suspending side effect (such as logging, updating analytics, or writing to an external cache) for each emitted element without modifying the stream contents or types.
launchIn is a concise terminal utility that collects a flow by launching a new coroutine within a specified CoroutineScope, returning the associated Job instance without suspending the caller.""",
    "walkthrough_en": """Composing intermediate operators and launching execution:
```kotlin
fun observeFilteredTransactions(accountFlow: Flow<Transaction>): Job {
    return accountFlow
        // 1. filter: Keep only approved transactions
        .filter { it.status == TransactionStatus.APPROVED }
        // 2. map: Convert domain entity to UI display model
        .map { it.toUiModel() }
        // 3. transform: Conditionally emit extra alert badges for large amounts
        .transform { item ->
            emit(item)
            if (item.amount > 10_000) {
                emit(item.copy(isLargeAlert = true))
            }
        }
        // 4. onEach: Side effect logging without altering stream
        .onEach { logDebug("Displaying transaction: ${it.id}") }
        // 5. launchIn: Starts collection in viewModelScope, returns Job
        .launchIn(viewModelScope)
}
```""",
    "short_en": """map transforms elements 1:1; filter drops elements based on a predicate; transform offers generalized 1:N emissions via FlowCollector; onEach runs side effects without altering data; and launchIn starts collection asynchronously in a given CoroutineScope, returning a cancellable Job.""",
    "structured_en": """To begin with, intermediate Flow operators construct declarative data transformation pipelines without executing upstream code until collection occurs.
From an architectural standpoint, map and filter handle basic data flow adjustments. map applies a one-to-one transformation, converting raw database entities into immutable UI models. filter conditionally excludes elements that fail validation predicates.
In production scenarios, transform provides total flexibility when map or filter are insufficient. Because transform exposes a FlowCollector receiver, a single upstream emission can produce zero, one, or multiple downstream emissions, making it ideal for splitting batches or emitting supplemental notifications.
As for boundary management, onEach executes non-destructive side effects such as audit logging or analytics tracking. Instead of calling collect inside a launch block, launchIn combines both into a concise, chainable call that binds flow collection to a CoroutineScope and returns a Job for cancellation control.""",
    "deep_senior_en": """Under the hood in kotlinx.coroutines.flow, intermediate operators like map and filter do not allocate coroutines or background threads. Instead, they wrap the upstream Flow instance in a new Flow implementation whose collectSafely method wraps the downstream FlowCollector in an internal decorator collector.
For example, map { transform(it) } compiles into a collector that receives upstream value T, executes the suspending transform block, and immediately invokes downstreamCollector.emit(R). If the transformation function suspends, the upstream producer cooperatively suspends on the exact same thread, preserving backpressure without intermediate queue overhead.
The transform operator exposes this mechanism directly: the lambda receiver is FlowCollector<R>, giving developers direct control over downstream emission cardinality and error boundaries.
The launchIn(scope) operator is a syntactic convenience defined as: scope.launch { collect() }. While launchIn creates clean, fluent code chains, staff engineers caution against overusing it inside ViewModels for UI state. In presentation layers, bridging cold flows using stateIn is heavily preferred because launchIn does not produce a state holder, does not survive screen rotations, and cannot provide synchronous value inspection for UI composables.
Furthermore, chaining multiple transformations without intermediate buffering maintains strict synchronous backpressure, meaning an unconsumed emission blocks upstream generation all the way back to the original source.""",
    "meta_ar": {
        "id": "FLO-11",
        "questionAr": "اشرح وظائف المعاملات: map و filter و transform و onEach و launchIn",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- استيعاب المعاملات الأساسية للتحويل والتصفية في تدفقات كوتلن.\n- إدراك المرونة الفائقة لمشغل transform في التحكم بتعددية الانبعاثات (1:N).\n- فهم كيفية عمل launchIn والفارق بينه وبين stateIn في طبقة العرض.",
        "why_it_matters_ar": "كتابة مسارات معالجة البيانات بكفاءة تمنع تعقيد الأكواد وتكرار الـ Coroutines غير الضرورية؛ فاستخدام `launchIn` غير المنضبط قد يخلق كوروتينات يصعب تعقبها أو إلغاؤها، بينما فهم `transform` يوفر كتابة شفرات معقدة كانت تتطلب إنشاء تدفقات وسيطة في الذاكرة.",
        "worked_example_ar": "بناء مسار تحويل بيانات متكامل:\n```kotlin\norderFlow\n    .filter { it.isPaid } // تصفية الطلبات المدفوعة فقط\n    .map { it.toUiModel() } // تحويل الكائن لنموذج الواجهة\n    .transform { item ->\n        emit(item) // إرسال العنصر الأساسي\n        if (item.isVip) emit(item.createVipBanner()) // إرسال عنصر إضافي\n    }\n    .onEach { logAnalytics(it) } // تسجيل الحدث كـ Side Effect\n    .launchIn(viewModelScope) // بدء الجمع وربطه بالـ Scope\n```",
        "trade_offs_ar": "المعاملات الوسيطة (map, filter, transform) خفيفة جداً ولا تنشئ خيوطاً جديدة، ولكن زيادة تعقيد العمليات الحسابية داخلها بدون استخدام `flowOn` قد يعطل خيط المعالجة الرئيسي إذا كان التجميع يتم على Main Dispatcher.",
        "failure_modes_ar": "استخدام `launchIn` في الـ ViewModel لجمع بيانات الشاشة بدلاً من `stateIn`؛ مما يحرم الشاشة من الاحتفاظ بآخر قيمة ويفقد البيانات عند تدوير الهاتف. خطأ آخر هو تنفيذ عمليات تعديل الحالة المشتركة (Mutable State) داخل `onEach` مما يخلق سباقات بيانات خطيرة.",
        "production_perspective_ar": "في المشروعات النظيفة، تُستخدم `map` و `filter` حصراً لتحويل نماذج البيانات عبر الطبقات. أما `launchIn` فنقتصر في استخدامه على جمع أحداث الـ Analytics أو الـ Push Notifications في الخلفية، بينما تظل حالة الشاشات محكومة ومكشوفة عبر `stateIn`.",
        "how_to_answer_ar": "- **map:** تحويل كل عنصر لعنصر آخر (1:1).\n- **filter:** تصفية العناصر بناءً على شرط منطقي (1:0 أو 1:1).\n- **transform:** المشغل الشامل؛ يتيح بث صفر أو عدة عناصر (1:N) لكل عنصر علوي عبر FlowCollector.\n- **onEach:** تنفيذ أثر جانبي (Side Effect) زي اللوجينج دون تعديل البيانات.\n- **launchIn:** تشغيل التجميع فوراً داخل Scope معين دون الحاجة لكتابة `scope.launch { collect() }` صراحة، وإرجاع كائن Job.\n- **المقارنة المعمارية:** التحذير من استخدام `launchIn` لحالة الشاشات وتفضيل `stateIn`.",
        "talking_points_ar": "ناقش كيف تُنفذ هذه المشغلات عبر FlowCollector Decorators بدون تخصيص خيوط، وتوريث الـ CoroutineContext، وتكامل دالة emit المعلقة في الحفاظ على الـ Backpressure.",
        "follow_ups_ar": "- **المحاور:** \"ما الفرق الجوهري بين map و transform؟\"\n  **المرشح:** \"معامل `map` بياخد دالة بترجع قيمة واحدة بس وينبعث عنصر واحد لكل عنصر داخل (1:1). أما `transform` فبيديك الـ `FlowCollector` كـ Receiver، فتقدر تعمل `emit` كذا مرة أو متعملش خالص لكل عنصر علوي، وده بيخليه ممتاز لتقسيم الداتا أو بث تنبيهات إضافية مشروطة (1:N).\"\n\n- **المحاور:** \"لماذا نفضل `stateIn` على `launchIn` في شاشات Compose؟\"\n  **المرشح:** \"لأن `launchIn` مجرد اختصار لـ `launch { collect() }` وبيرجع كائن Job ملوش أي كاش ومبيحتفظش بحالة، فمع تدوير الشاشة بتفقد الداتا. أما `stateIn` فبيرجع كائن `StateFlow` متصل بدورة حياة الشاشة وبيحتفظ بآخر قيمة ويعرضها فوراً بدون إعادة طلب الشبكة.\"",
        "self_check_ar": "هل شرحت كل معامل بدقة؟ هل وضحت ميزة transform في التحكم بعدد الانبعاثات؟ وهل بينت متى نستخدم launchIn ومتى نتجنبه؟",
        "references_ar": f"- [Kotlin Flow intermediate operators](https://kotlinlang.org/docs/flow.html#intermediate-flow-operators) — دليل كوتلن الرسمي للمشغلات.\n- [Kotlin Coroutines Flow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/) — التوثيق الرسمي لمكتبة التدفقات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "`map` بتحول كل عنصر لعنصر جديد بنظام 1:1، و`filter` بتصفي العناصر بشرط معين، و`transform` بتديك تحكم كامل تقدر تبعت منها كذا قيمة أو متبعتش خالص لكل عنصر (1:N). أما `onEach` فبتنفذ كود جانبي زي اللوجينج بدون ما تغير الداتا، و`launchIn` بتشغل التجميع فوراً جوه CoroutineScope وترجعلك Job بدون ما تعلق الدالة.",
        "best_answer_ar": "المعاملات دي بتمثل خط الإنتاج التفاعلي (Functional Pipeline) لمعالجة البيانات في Flow بدون أي تعقيد.\n\nمعامل `map` وظيفته واضحة؛ بياخد كل عنصر علوي ويطبّق عليه عملية تحويل ويرجع عنصر جديد مكانه بنظام 1:1، زي لما نحول Entity من الداتابيز لـ UiModel.\n\nمعامل `filter` بيختبر كل عنصر بشرط منطقي (Boolean)، لو وافق الشرط بيعديه، ولو خالفه بيسقطه ومبيوصلش للجامع.\n\nأما `transform` فده المشغل الأكثر مرونة وقوة؛ لأنه بيكشفلك الـ `FlowCollector` كـ Receiver مباشر. ده معناه إنك لكل عنصر علوي يوصلك، تقدر تعمل `emit` ولا مرة، أو تعمله مرة واحدة، أو تعمله عشر مرات، فبيديك تحكم كامل بنظام 1:N.\n\nمعامل `onEach` معمول للآثار الجانبية (Side Effects) زي طباعة الـ Logs أو تسجيل الـ Analytics بدون ما يغير في محتوى أو نوع البيانات المتدفقة.\n\nوأخيراً `launchIn` هو اختصار أنيق لكتابة `scope.launch { flow.collect() }`؛ بيبدأ التجميع في الـ CoroutineScope اللي بتحدده وبيرجعلك كائن `Job` علشان تقدر تلغيه في أي وقت، لكن بنحذر من استخدامه لحالة الشاشة لأن `stateIn` أفضل وأضمن في الحفاظ على أحدث قيمة.",
        "deep_answer_ar": "تحت الكابوت في `kotlinx.coroutines.flow`، المعاملات الوسيطة دي مابتنشئش أي خيوط أو كوروتينات جديدة على الإطلاق؛ هي مجرد Decorators بتغلف الـ `FlowCollector` الداخلي بكلاس جديد.\n\nيعني مثلاً لما بتنادي `map { transform(it) }`، الكود بيغلف الـ Flow الأصلي بـ SafeCollector جديد بينفذ كود التحويل المعلق ويمرر النتيجة فوراً للـ `emit` بتاعة المشترك النهائي. وبما إن كل العمليات دي بتتم عبر دوال معلقة (suspend funs)، فالـ Backpressure بيفضل شغال بتعاون تام وبدون أي فقدان للأداء، ولو الـ transform أخد وقت طويل، المصدر بيتعلق تلقائياً على نفس الخيط.\n\nمعامل `transform` بيعتمد على نفس الآلية تماماً، بس بيمررلك الـ `FlowCollector` نفسه جوه الـ Lambda، وده بيخليك تقدر تبني معالجات معقدة جداً زي دمج لقطات إضافية أو إرسال فواصل زمنية بدون الحاجة لكتابة كود Flow مخصص من الصفر.\n\nأما `launchIn(scope)`، فالكود المصدري بتاعه حرفياً هو: `scope.launch { collect() }`. ورغم بساطته وأناقته في كتابة الـ Fluent API، مهندسي الـ Staff في أندرويد بيتجنبوا استخدامه في طبقة الـ Presentation؛ لأن `launchIn` ملوش أي كاش ولا بيحتفظ بآخر قيمة، وبالتالي مبيصلحش لتمثيل حالة الواجهات في Jetpack Compose وبيفقد ميزة الـ Conflation اللي بيوفرها `StateFlow`.\n\nبالإضافة لكده، الربط المباشر بين المعاملات دي بيحافظ على التدفق المتزامن المباشر، ومفيش أي استهلاك لذاكرة وسيطة طالما لم نطلب استخدام buffer صراحة."
    }
}

# ==========================================
# FLO-12: collect vs collectLatest vs first
# ==========================================
DATA["FLO-12"] = {
    "concept_en": """The terminal operators collect, collectLatest, and first provide distinct consumption contracts governing execution duration, concurrency handling, and element completion.
collect is the foundational, sequential terminal operator that processes every emitted value to total completion; if processing an item takes time, the upstream emitter is suspended cooperatively until the collector block finishes before emitting the subsequent item.
collectLatest is a cancelling terminal operator designed for high-frequency or latency-sensitive streams; whenever a new element is emitted upstream while the previous element's collector block is still suspended, collectLatest immediately cancels the previous execution block and launches a new coroutine to process the newly arrived element.
first is a one-shot terminal operator that collects the stream, awaits and returns exactly the first emitted element (or the first element matching an optional predicate), and immediately cancels upstream collection, terminating the subscription cleanly.""",
    "walkthrough_en": """Contrasting collect, collectLatest, and first in practical scenarios:
```kotlin
suspend fun demonstrateTerminalOperators(queryFlow: Flow<String>) {
    // 1. collect: Guaranteed full processing of every single item sequentially
    queryFlow.collect { query ->
        processPaymentAudit(query) // Must finish completely for each item
    }

    // 2. collectLatest: Cancels in-flight work when a newer search query arrives
    queryFlow.collectLatest { query ->
        val results = searchRemoteBackend(query) // Cancelled if user types another letter!
        displaySearchResults(results)
    }

    // 3. first: Grabs the initial token snapshot and cancels upstream immediately
    val initialToken = queryFlow.first()
}
```""",
    "short_en": """collect executes sequentially to completion for every emission; collectLatest cancels the current processing block if a newer emission arrives upstream before completion; and first collects the first matching element, immediately cancels upstream collection, and returns the scalar value.""",
    "structured_en": """To begin with, terminal operators dictate how and when flow execution proceeds, resolving backpressure through sequential processing, cancellation, or truncation.
From an architectural standpoint, collect guarantees that every emitted item is processed completely. Because emit suspends until collect completes, no data is dropped or skipped, making it mandatory for transactional operations like auditing or database writes.
In production scenarios, collectLatest is tailored for latency-sensitive UI updates like search suggestions or video frame rendering. When the upstream emits a new value while the previous collector block is suspended, collectLatest cancels the active coroutine block immediately and starts processing the new element, ensuring the UI never wastes resources processing stale inputs.
As for boundary management, first transforms a continuous stream into a one-shot suspending computation. It collects the first emitted element that satisfies an optional condition, cancels the upstream coroutine via CancellationException, and returns the result, ideal for reading a single configuration flag.""",
    "deep_senior_en": """Under the hood in kotlinx.coroutines, collectLatest is implemented as a specialized channelFlow operator combined with flow.buffer(Channel.CONFLATED). It launches a collector loop where each incoming emission cancels the Job of the previous emission's child coroutine block before invoking the user action block in a freshly spawned coroutine.
This cancellation introduces a critical production danger: partial execution and atomic corruption. If the action block inside collectLatest performs multiple mutations (such as inserting a record into a database and then updating a remote tracker), an incoming emission can cancel the coroutine precisely between the two operations. The second operation never executes, leaving database records or memory state in an inconsistent state. Therefore, collectLatest must only wrap idempotent read operations or pure UI rendering tasks.
The first operator utilizes cooperative cancellation internally. Upon receiving the initial matching item, it throws an internal AbortFlowException carrying the captured element. The operator catches this exception, cleans up upstream channel resources, and returns the extracted element synchronously.
In unit tests, validating collectLatest requires testing race conditions where rapid test emissions simulate user interruptions, verifying that previous jobs received CancellationException and halted further processing.
Staff engineers enforce strict rules: transactional and mutating tasks mandate plain collect; user-driven query searches and UI animations use collectLatest; and initial configuration lookups use first.""",
    "meta_ar": {
        "id": "FLO-12",
        "questionAr": "قارن بين المشغلات الطرفية: collect و collectLatest و first",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- الفهم العميق لسلوك المشغلات الطرفية (Terminal Operators) في Flow.\n- إدراك آلية الإلغاء التلقائي في collectLatest ومخاطرها مع العمليات غير المتكررة (Non-idempotent).\n- معرفة متى نستخدم first لتحويل التدفق المستمر إلى قيمة مفردة مع إنهاء الاشتراك.",
        "why_it_matters_ar": "استخدام `collectLatest` مع عمليات حفظ البيانات أو الدفع الإلكتروني قد يتسبب في إلغاء المعاملة في منتصفها وتخريب قاعدة البيانات، بينما استخدام `collect` العادية مع حقول البحث يجعل الواجهة تتجمد وتعرض نتائج قديمة للمستخدم بعد أن يكون قد كتب كلمة جديدة.",
        "worked_example_ar": "مقارنة عملية بين المعالجة الكاملة وإلغاء العمليات القديمة:\n```kotlin\n// 1. collect: يضمن إكمال كتابة كل المعاملات بالترتيب وبدون إلغاء\ntransactionFlow.collect { tx -> saveToDatabase(tx) }\n\n// 2. collectLatest: يلغي البحث القديم فور كتابة حرف جديد في مربع البحث\nsearchQueryFlow.collectLatest { query ->\n    val results = searchApi(query) // يلغى فوراً لو المستخدم ضغط حرفاً تالياً\n    updateUi(results)\n}\n\n// 3. first: قراءة التوكن الأولي وإلغاء مراقبة التدفق فوراً\nval token = authFlow.first()\n```",
        "trade_offs_ar": "`collect` تضمن معالجة كل عنصر ولكنها قد تبطئ المسار إذا كان المستهلك بطيئاً. `collectLatest` تحافظ على حداثة الشاشة دائماً ولكنها تسقط وتلغي العمليات السابقة. `first` سريعة لقراءة عنصر واحد لكنها تغلق التدفق ولا تتابع التحديثات اللاحقة.",
        "failure_modes_ar": "استخدام `collectLatest` لتحديث قاعدة بيانات أو تنفيذ طلبات شراء، حيث يؤدي وصول حدث جديد إلى إلغاء الكوروتين في منتصف عملية الحفظ وتخريب البيانات. خطأ آخر هو استدعاء `first()` على تدفق فارغ تماماً مما يسبب تعليق الكود إلى ما لا نهاية ما لم يُغلق التدفق.",
        "production_perspective_ar": "في المشروعات الإنتاجية، نضع قاعدة هندسية صارمة: أي عملية كتابة (Mutation/Persistence) تُجمع حصراً بـ `collect` العادية لضمان الاكتمال التام، بينما يقتصر استخدام `collectLatest` على عرض الرسوميات وتحديثات الواجهة واستعلامات البحث التي تلغي نفسها ذاتياً.",
        "how_to_answer_ar": "- **collect:** المشغل الأساسي المتسلسل؛ يعالج كل عنصر للنهاية ويعلق Emitter عند البطء.\n- **collectLatest:** المشغل الملغي؛ لو وصل عنصر جديد أثناء انشغال الكوروتين، يلغي تنفيذ العنصر السابق فوراً ويبدأ الجديد.\n- **first:** المشغل الأحادي؛ يستلم أول عنصر يطابق الشرط، ويلغي التدفق فوراً ويرجع القيمة كـ One-shot.\n- **الخطر الإنتاجي:** التحذير من استخدام collectLatest في عمليات الكتابة والمعاملات المالية غير القابلة للإلغاء.\n- **أمثلة واقعية:** البحث في الواجهة (collectLatest)، كتابة الداتابيز (collect)، فحص تسجيل الدخول (first).",
        "talking_points_ar": "ناقش كلاس AbortFlowException في تطبيق مشغل first، وكيف يعتمد collectLatest على إلغاء الـ Job الداخلي، ودور مبدأ Idempotency في حماية البيانات.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لو استدعيت `collectLatest` وبداخلها عمليتي حفظ في الداتابيز؟\"\n  **المرشح:** \"لو انبعث عنصر جديد أثناء تنفيذ العملية الأولى، الكوروتين هتتلغي فوراً بـ CancellationException والعملية التانية مش هتشتغل نهائياً، وده بيسيب الداتابيز في حالة تالفة أو غير مكتملة (Inconsistent State). علشان كده collectLatest ممنوعة تماماً في عمليات الكتابة والحفظ.\"\n\n- **المحاور:** \"كيف ينهي مشغل `first()` التدفق فور استلام القيمة؟\"\n  **المرشح:** \"تحت الكابوت، أول ما `first()` تستلم أول عنصر يطابق الشرط، بترمي استثناء داخلي اسمه `AbortFlowException`. المشغل بيمسك الاستثناء ده ويكتمه ويرجع القيمة الراجعة، بينما رمي الاستثناء بيمر عبر سلسلة الـ Upstream ويلغي كل كوروتينات الإنتاج وحلقات الـ `try-finally` بنظافة تامة.\"",
        "self_check_ar": "هل فرقت بوضوح بين المشغلات الثلاثة؟ هل نبهت لخطر collectLatest مع الـ Mutations؟ وهل شرحت آلية عمل first الداخلية؟",
        "references_ar": f"- [Kotlin Flow terminal operators](https://kotlinlang.org/docs/flow.html#terminal-flow-operators) — دليل كوتلن الرسمي للمشغلات الطرفية.\n- [collectLatest API documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/collect-latest.html) — توثيق collectLatest الرسمي.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "`collect` بتعالج كل عنصر بالترتيب لحد ما يخلص تماماً بدون ما تلغي أي حاجة، و`collectLatest` بتلغي معالجة العنصر القديم فوراً لو وصل عنصر جديد وبتعالج الأحدث بس، أما `first` فبتاخد أول قيمة توصل للتدفق وتلغي الاشتراك العلوي فوراً وترجعلك القيمة كأنها دالة عادية.",
        "best_answer_ar": "المشغلات الطرفية دي بتحدد الطريقة اللي بنستهلك بيها تدفق البيانات وكيفية التعامل مع الوقت والإلغاء.\n\nمعامل `collect` هو المشغل الأساسي التتابعي؛ بياخد كل عنصر بالترتيب وينفذ عليه الكود بالكامل، ومبيستلمش العنصر اللي بعده إلا لما الأول يخلص تماماً بفضل الـ Backpressure، وده مشغل إلزامي لأي عمليات حساسة زي حفظ البيانات في الداتابيز أو تنفيذ المدفوعات.\n\nأما `collectLatest` فده معمول خصيصاً للواجهات والعمليات الحساسة للسرعة زي البحث؛ لما يوصل عنصر جديد وكان الكود لسه شغال بيعالج العنصر اللي قبله، بيلغي الكوروتين السابقة فوراً ويبدأ معالجة العنصر الجديد في الحال، وده بيضمن إن الشاشة دايماً بتعالج أحدث طلب وما تضيعش وقت في طلبات قديمة المستخدم مابقاش مهتم بيها.\n\nومشغل `first` بيحول الـ Flow المستمر لدالة معلقة عادية؛ بيشترك في التدفق ويستنى أول عنصر ينبعث ويستلمه، وبمجرد ما يوصل بيلغي التدفق العلوي فوراً ويرجع القيمة للمستدعي، وده ممتاز لقراءة إعداد محدد أو جلب التوكن لأول مرة.",
        "deep_answer_ar": "على مستوى الهيكل البرمجي في `kotlinx.coroutines`، مشغل `collectLatest` مبني عبر دمج مشغلين: بيعمل buffer داخلي بنظام `CONFLATED`، وبيشغل كل انبعاث جديد في كوروتين فرعية مخصصة. أول ما يوصل عنصر جديد، المشغل بينادي صراحة على `job.cancel()` للكوروتين بتاعة العنصر السابق قبل ما يفتح كوروتين جديدة للمعامل الجديد.\n\nوهنا بتكمن خطورة إنتاجية بالغة الأهمية: الإلغاء ده بيخلي `collectLatest` غير آمنة تماماً لأي عمليات غير متكررة (Non-idempotent)؛ يعني لو الكود بيكتب في داتابيز وبعدها بيبعت إشعار للشبكة، وجاء عنصر جديد في النص، الكوروتين هتتلغي في منتصف التنفيذ وتترك قاعدة البيانات في حالة تالفة. علشان كده بنحظر استخدامه في عمليات الـ Persistence والـ Business Logic ونقصره على قراءة الواجهة.\n\nأما مشغل `first()`، فآليته في تفكيك الموارد بتعتمد على نمط رمي الاستثناءات التعاونية؛ أول ما المشترك بيستلم العنصر الأول، بيرمي كلاس داخلي خاص اسمه `AbortFlowException`. المشغل بيمسك الاستثناء ده ويكتمه ويرجع القيمة الراجعة، بينما رمي الاستثناء بيمر عبر سلسلة الـ Upstream ويلغي كل كوروتينات الإنتاج وحلقات الـ `try-finally` بنظافة تامة.\n\nوفي اختبارات الـ Unit Testing، التحقق من سلوك `collectLatest` بيتطلب محاكاة انبعاثات متتالية سريعة للتأكد من إن الـ Job القديمة استلمت `CancellationException` ووقفت شغلها بشكل سليم تماماً.\n\nوفي بيئات الإنتاج، بنتبع قاعدة معمارية واضحة: نداءات الحفظ والتعديل تُجمع بـ `collect`، وعمليات البحث والعرض بـ `collectLatest`، والقراءات المعزولة بـ `first`."
    }
}

# ==========================================
# FLO-13: combine vs zip
# ==========================================
DATA["FLO-13"] = {
    "concept_en": """The combine and zip operators merge multiple asynchronous flows into a unified output stream, diverging fundamentally in how they handle temporal alignment, emission pairing, and lifecycle termination.
combine operates on the latest-value principle: after each participating flow has emitted at least once, combine recalculates and emits a new composite value whenever any individual source flow emits a new element, reusing the most recently cached values of the other flows.
zip operates on strict pairwise alignment: it pairs the N-th emission of the first flow with the N-th emission of the second flow in strict sequential lockstep (first with first, second with second). If one flow emits ten items rapidly while the other emits slowly, zip buffers the faster flow's emissions and waits until matching counterpart elements arrive before emitting the zipped pair. Furthermore, zip completes as soon as any of its participating flows completes, whereas combine completes only after all upstream flows have finished.""",
    "walkthrough_en": """Contrasting combine for UI state with zip for paired transactions:
```kotlin
// 1. combine: Updates UI state whenever user search OR category filter changes
fun observeFilteredProducts(
    searchFlow: Flow<String>,
    categoryFlow: Flow<Category>
): Flow<List<Product>> {
    return combine(searchFlow, categoryFlow) { query, category ->
        productDao.queryProducts(query, category)
    }
}

// 2. zip: Strictly pairs requests with their corresponding response receipts
fun pairTransactions(
    orderIds: Flow<OrderId>,
    receiptTokens: Flow<ReceiptToken>
): Flow<ConfirmedOrder> {
    return orderIds.zip(receiptTokens) { id, token ->
        ConfirmedOrder(orderId = id, receiptToken = token)
    }
}
```""",
    "short_en": """combine emits a new value whenever ANY source flow emits, combining the latest value from each stream. zip strictly pairs emissions one-to-one in sequential lockstep (first with first, second with second) and buffers fast streams until matching pairs arrive, completing when the shorter flow terminates.""",
    "structured_en": """To begin with, combine and zip combine multiple asynchronous streams but serve completely distinct architectural use cases.
From an architectural standpoint, combine recalculates downstream values dynamically whenever any source stream updates. Once all streams have emitted an initial value, a new emission from any single flow immediately produces an updated composite state, making combine the quintessential operator for multi-source UI state aggregation.
In production scenarios, zip enforces strict pairwise 1:1 synchronization. It matches the first element of flow A with the first element of flow B, the second with the second, and so on. If one flow emits faster, zip suspends or buffers until the lagging flow produces the matching item.
As for boundary management, combine terminates only when all participating source flows have completed, whereas zip terminates immediately as soon as any single participating flow finishes emitting, discarding any excess unzipped emissions from the longer stream.""",
    "deep_senior_en": """Under the hood in kotlinx.coroutines.flow, combine and zip manage concurrency and buffering through differing channel architectures.
combine utilizes an internal select expression or a fan-in Channel array where emissions from all upstream sources are directed into a central distributor. Each source maintains a dedicated slot storing its latest emitted value. When any upstream flow emits, the slot updates and the transform lambda executes immediately with the latest snapshot of all slots. Because combine holds only the latest single reference per stream, it does not cause memory leaks or buffer bloat when streams operate at radically different frequencies.
Conversely, zip allocates internal Channel buffers for each upstream flow. When upstream flow A emits faster than upstream flow B, emissions from A accumulate in its Channel queue awaiting matching emissions from B. If stream A is an infinite rapid sensor feed while stream B is a slow network polling loop, this internal queue grows unbounded, precipitating OutOfMemoryError exceptions if backpressure cannot suspend upstream production.
Staff engineers enforce strict guidelines: combine is mandatory for aggregating reactive UI state (such as combining user profiles, permissions, and theme settings), while zip is reserved for atomic paired computations (such as combining coordinate pairs or sequential transaction tokens).""",
    "meta_ar": {
        "id": "FLO-13",
        "questionAr": "قارن بين المشغلين: combine و zip ومتى تستخدم كلاً منهما؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- الفهم الدقيق لآلية دمج التدفقات في كوتلن.\n- التمييز بين نمط أحدث قيمة (Latest Value) في combine ونمط الاقتران الحتمي (1:1 Lockstep) في zip.\n- استيعاب مخاطر الذاكرة في zip وتفضيل combine لتجميع حالات واجهات المستخدم.",
        "why_it_matters_ar": "استخدام `zip` لتجميع بيانات الشاشة قد يوقف تحديث الواجهة تماماً؛ لأن تغيير أحد الحقول 5 مرات بينما الآخر لم يتغير يمنع انبعاث أي قيمة جديدة، بينما استخدام `combine` يضمن تحديث الشاشة فوراً مع أي تغيير في أي مصدر.",
        "worked_example_ar": "تجميع حالة الشاشة من عدة مصادر عبر combine:\n```kotlin\n// في الـ ViewModel: تحديث القائمة لو البحث اتغير أو التصنيف اتغير\nval uiState = combine(\n    searchQueryFlow,\n    selectedCategoryFlow,\n    userFavoritesFlow\n) { query, category, favorites ->\n    ProductsUiState(query, category, favorites)\n}.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), ProductsUiState())\n```",
        "trade_offs_ar": "`combine` ممتازة لحالات الواجهة لأنها لا تراكم طوابير في الذاكرة وتحدث فوراً، ولكنها تتجاهل التزامن الفردي. `zip` تضمن اقتران كل عنصر بقرينه المقابل تماماً ولكنها قد تستهلك ذاكرة لو تفاوتت سرعة التدفقين.",
        "failure_modes_ar": "استخدام `zip` لدمج تدفق سريع جداً (حساسات) مع تدفق بطيء، مما يؤدي لتراكم مئات العناصر في الـ Buffer الداخلي لـ zip وحدوث OutOfMemoryError. خطأ آخر هو نسيان أن `zip` ينتهي فور اكتمال أقصر تدفق متجاهلاً باقي عناصر التدفق الأطول.",
        "production_perspective_ar": "في المشروعات الحقيقية، يُستخدم `combine` في 95% من الحالات لتجميع مصادر الـ UiState المختلفة في الـ ViewModel، بينما يُحفظ `zip` للعمليات الرياضية أو المعاملات التي تتطلب اقتران زوجي صارم بين طلبين متزامنين.",
        "how_to_answer_ar": "- **combine:** ينتظر أول انبعاث من كل المصادر، وبعدها أي انبعاث جديد من أي تيار يعيد الحساب فوراً باستخدام أحدث القيم للتيارات الأخرى.\n- **zip:** يعمل بنظام الاقتران التزامني الصارم (1:1)؛ الأول مع الأول والثاني مع الثاني؛ ولو تيار أسرع بينتظر التاني في طابور.\n- **الانتهاء:** combine ينتهي بانتهاء كل التدفقات، بينما zip ينتهي فور انتهاء أقصر تدفق.\n- **خطر الذاكرة:** التفاوت في السرعة مع zip يراكم الذاكرة، بينما combine يحتفظ بآخر لقطة فقط.\n- **الاستخدام الإنتاجي:** combine لتجميع حالة الواجهات، و zip للاقتران الحسابي الزوجي.",
        "talking_points_ar": "ناقش الـ Internal Channel Buffers في zip، ومصفوفة الـ Slots في combine، وكيف يحل combine مشكلة Multi-stream State Management في نمط MVI/MVVM.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لو أحد التدفقات في combine لم يرسل أي قيمة نهائياً؟\"\n  **المرشح:** \"مشغل `combine` مش هيبعت أي قيمة نهائياً للجامع؛ لأنه بيشترط إن كل تدفق يبعت أول قيمة على الأقل علشان يقدر يجمعهم في لقطة كاملة. لو فيه تدفق ممكن يتأخر، بنستخدم معاه `onStart { emit(initial) }` علشان نفك التعليق.\"\n\n- **المحاور:** \"لماذا ينتهي zip فور اكتمال أقصر تدفق؟\"\n  **المرشح:** \"لأن الفلسفة التصميمية لـ `zip` هي الاقتران الزوجي (Pairs)؛ فبمجرد ما تيار يخلص، العناصر المتبقية في التيار التاني مش هيكون ليها شريك تقترن بيه، وبالتالي المشغل بيلغي التيار التاني فوراً وينهي التجميع.\"",
        "self_check_ar": "هل فرقت بين آلية الاقتران في الاثنين؟ هل شرحت سلوك الانتهاء في كل منهما؟ وهل وضحت سبب تفضيل combine لشاشات أندرويد؟",
        "references_ar": f"- [Kotlin Flow combine documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/combine.html) — توثيق مشغل combine.\n- [Kotlin Flow zip documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/zip.html) — توثيق مشغل zip.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "`combine` بيبعت قيمة جديدة كل ما أي تدفق يبعت داتا، وبياخد أحدث قيمة من التيارات التانية وده المشغل المثالي لحالة الشاشات. أما `zip` فبيقرن العناصر بالترتيب الصارم بنظام 1:1؛ الأول مع الأول والتاني مع التاني، ولو تدفق سريع بيستنى التاني في طابور، وبينتهي فور اكتمال أقصر تدفق فيهم.",
        "best_answer_ar": "المشغلين `combine` و `zip` بيجمعوا كذا Flow مع بعض، لكن طريقة الدمج والتوقيت مختلفة تماماً من الناحية المعمارية.\n\nمشغل `combine` بيعتمد على مبدأ أحدث قيمة (Latest Value)؛ أول ما كل التدفقات تبعت أول عنصر ليها، بعد كده أي تدفق فيهم يبعت قيمة جديدة، الـ combine بيشتغل فوراً وياخد القيمة الجديدة دي ويدمجها مع آخر قيم كانت مبعوثة من باقي التدفقات ويبعت الناتج للشاشة. وده بيخليه المشغل الأساسي في أندرويد لتجميع حالة الشاشة (UiState) من كذا مصدر زي نص البحث واختيار التصنيف وحالة تسجيل الدخول.\n\nأما مشغل `zip` فبيعتمد على الاقتران التزامني الصارم (Strict Pairwise)؛ يعني بيمسك العنصر الأول من التدفق (أ) ويقرنه بالعنصر الأول من التدفق (ب)، والعنصر التاني مع التاني، وهكذا. فلو التدفق الأول بعت 10 عناصر والتاني بعت عنصر واحد بس، الـ `zip` هيبعت زوج واحد ويحجز باقي العناصر في طابور انتظار لحد ما التدفق التاني يبعت باقي أزواجه.\n\nبالإضافة لكده، `zip` بينتهي فوراً بمجرد ما يخلص أقصر تدفق فيهم ويلغي باقي العناصر، بينما `combine` بيفضل شغال ومبينتهيش إلا لما كل التدفقات تخلص تماماً.",
        "deep_answer_ar": "على مستوى الـ Implementation الداخلي وإدارة الذاكرة، الفارق بين `combine` و `zip` بيمثل فارق جوهري في استهلاك الـ Heap والموارد.\n\nمشغل `combine` مبيراكمش عناصر في الذاكرة؛ هو بيستخدم مصفوفة داخلية من الـ Slots بتخزن مؤشر لأحدث قيمة لكل تدفق. لما أي تدفق يبعت إشعار عبر الـ Internal Channel، المشغل بيحدث الـ Slot بتاعه وينفذ الـ Lambda التحويلية فوراً. وبما إنه محتفظ بلقطة واحدة فقط لكل تدفق، فمهما تفاوتت سرعة التدفقات مستحيل يحصل OutOfMemoryError.\n\nفي المقابل، مشغل `zip` بينشئ Channel Buffer لكل تدفق علوي. لما تدفق سريع يبعت بيانات، العناصر دي بتتراكم في طابور الـ Channel ده بانتظار وصول العناصر المقابلة من التدفق البطيء. لو التدفق الأول بيبعت قراءات سريعة جداً من مستشعر والتاني بيعمل نداء شبكة بطيء، الطابور ده هيفضل يتضخم في الذاكرة وممكن يوقع التطبيق بكراش OOM لو الـ Backpressure معرفش يعلق المصنع في الوقت المناسب.\n\nالنقطة التانية هي سلوك الإنهاء (Termination)؛ `zip` بيطبق عقد الـ Pairwise الصارم، فأول ما تدفق يرسل إشارة `close`، المشغل بيرمي CancellationException للتدفق التاني ويفكك موارده لأنه مستحيل يلاقي شريك للعناصر المتبقية.\n\nعلشان كده في بيئات الإنتاج، بنستخدم `combine` في 95% من سيناريوهات تجميع الـ ViewModels، ونقصر `zip` على العمليات الحسابية المتزامنة زي ربط أزواج إحداثيات أو دمج طلبات معتمدة على أرقام تسلسلية حتمية."
    }
}

# ==========================================
# FLO-14: flatMapLatest, flatMapConcat, flatMapMerge
# ==========================================
DATA["FLO-14"] = {
    "concept_en": """The flattening operators flatMapLatest, flatMapConcat, and flatMapMerge transform upstream elements into inner flows and flatten the resulting streams into a single downstream sequence, differing in concurrency, ordering, and cancellation semantics.
flatMapLatest switches to a new inner flow on each incoming upstream emission; if the previous inner flow is still actively emitting when a new upstream element arrives, flatMapLatest cancels the previous inner flow immediately and switches downstream collection to the newly generated flow.
flatMapConcat flattens flows sequentially: it collects each inner flow to total completion before beginning the collection of the subsequent inner flow, strictly preserving sequential order and applying backpressure upstream.
flatMapMerge flattens flows concurrently: it collects multiple inner flows simultaneously up to a configurable concurrency limit (concurrency parameter, defaulting to DEFAULT_CONCURRENCY which is 16), merging their emissions non-deterministically as they arrive.""",
    "walkthrough_en": """Contrasting flattening operators in Android repositories and ViewModels:
```kotlin
class SearchViewModel(private val api: SearchApi) : ViewModel() {
    // 1. flatMapLatest: Cancels stale network search when user types a new character
    val searchResults: Flow<List<SearchResult>> = searchQueryFlow
        .flatMapLatest { query ->
            api.searchProductsFlow(query) // Previous search cancelled immediately!
        }

    // 2. flatMapConcat: Strictly sequential file uploads, one after another
    val uploadProgress: Flow<UploadResult> = fileListFlow
        .flatMapConcat { file ->
            uploader.uploadFileFlow(file) // Waits for file 1 to finish before file 2 starts
        }

    // 3. flatMapMerge: Concurrent photo downloads, up to 4 parallel streams
    val downloadedPhotos: Flow<Bitmap> = photoUrlsFlow
        .flatMapMerge(concurrency = 4) { url ->
            downloader.downloadPhotoFlow(url)
        }
}
```""",
    "short_en": """flatMapLatest cancels the active inner flow when a new upstream item arrives, ideal for search; flatMapConcat collects inner flows sequentially one-by-one to completion; and flatMapMerge collects multiple inner flows concurrently up to a specified limit, merging emissions as they arrive.""",
    "structured_en": """To begin with, flattening operators transform emissions into nested flows and resolve them into a single downstream output stream.
From an architectural standpoint, flatMapLatest operates as a switching mechanism. When an upstream value triggers a new inner flow while the previous inner flow is still executing, flatMapLatest cancels the active inner coroutine immediately. This is the cornerstone of responsive search interfaces, guaranteeing that slow, obsolete network queries are discarded when newer queries arrive.
In production scenarios, flatMapConcat enforces strict serial execution. It collects each inner flow completely before starting the next inner flow, preserving chronological order and preventing concurrent operations. We use it for sequential background sync queues or ordered file migrations.
As for boundary management, flatMapMerge provides parallel execution across multiple inner streams. It accepts a concurrency parameter controlling how many inner flows run concurrently, merging items non-deterministically to accelerate batch downloads or concurrent API fetches.""",
    "deep_senior_en": """Under the hood in kotlinx.coroutines.flow, flatMapLatest is implemented as transformLatest { emitAll(transform(it)) }. When a new upstream emission arrives, the internal CoroutineScope of the active transform block is cancelled via CancellationException, triggering immediate teardown of upstream sockets and network jobs attached to that specific inner flow.
flatMapConcat is functionally equivalent to flatMapMerge with concurrency = 1. Internally, it invokes collect on each inner flow sequentially inside the collector's loop. The upstream flow is suspended cooperatively until the active inner flow emits all elements and completes its block. This makes flatMapConcat strictly backpressured but susceptible to catastrophic head-of-line blocking if an inner flow hangs or executes an infinite stream.
flatMapMerge executes multiple inner collections concurrently by routing emissions through a shared channel of size DEFAULT_CONCURRENCY (16). While highly performant for batch operations, unbounded or high concurrency drains connection pools and database sockets rapidly.
Staff engineers enforce clear design boundaries: flatMapLatest is required for interactive UI input and search boxes; flatMapConcat is required for ordered transactional pipelines; and flatMapMerge is used strictly with explicit, bounded concurrency parameters for batch background operations.
In unit tests, validating concurrency boundaries requires mocking delayed inner emissions and verifying that collector invocations execute within expected parallel timeframes without exceeding memory bounds.""",
    "meta_ar": {
        "id": "FLO-14",
        "questionAr": "قارن بين المشغلات: flatMapLatest و flatMapConcat و flatMapMerge",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- الفهم المعماري لمشغلات التسطيح (Flattening Operators) في كوتلن.\n- إدراك سلوك الإلغاء في flatMapLatest وحماية موارد الشبكة في البحث.\n- التمييز بين التنفيذ المتسلسل في flatMapConcat والتنفيذ المتوازي في flatMapMerge مع قيود التزامن.",
        "why_it_matters_ar": "استخدام المشغل الخاطئ يسبب كوارث أداء؛ فاستخدام `flatMapConcat` في مربع البحث يجعل النتائج القديمة تظهر بعد ثوانٍ وتلخبط المستخدم بسبب الانتظار الإجباري، بينما استخدام `flatMapMerge` بدون تقييد قد يفتح عشرات الاتصالات المتزامنة ويسقط السيرفر.",
        "worked_example_ar": "استخدام flatMapLatest لمربع البحث لإلغاء الطلبات القديمة:\n```kotlin\nval searchResults = searchQuery\n    .debounce(300)\n    .distinctUntilChanged()\n    .flatMapLatest { query ->\n        repository.searchProducts(query) // يلغي الاستعلام السابق فور كتابة حرف جديد\n    }\n    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())\n```",
        "trade_offs_ar": "`flatMapLatest` تضمن الاستجابة لأحدث مدخل وإلغاء القديم ولكنها تسقط العمليات غير المكتملة. `flatMapConcat` تحافظ على الترتيب والتمام ولكنها قد تسبب تجمد الطابور (Head-of-line blocking). `flatMapMerge` سريعة ومتوازية ولكن انبعاثاتها غير مرتبة.",
        "failure_modes_ar": "استخدام `flatMapConcat` مع تدفقات داخلية لا نهائية (Infinite Flows)، مما يجعل التطبيق يتجمد للأبد عند أول تدفق ولا ينتقل للثاني. خطأ آخر هو ترك `concurrency` في `flatMapMerge` على القيمة الافتراضية (16) في شبكات ضعيفة مما يخنق الـ Connection Pool.",
        "production_perspective_ar": "في المشروعات الإنتاجية الكبرى، نمنع استخدام `flatMapConcat` إلا لعمليات التحديث المترابطة خطوة بخطوة، ونفرض استخدام `flatMapLatest` لجميع مدخلات البحث والملاحة، مع وضع سقف صريح للتزامن في `flatMapMerge` لتفادي استنزاف موارد الهاتف.",
        "how_to_answer_ar": "- **الوظيفة العامة:** مشغلات التسطيح بتحول كل عنصر علوي لـ Flow داخلي، وتدمج النواتج في Flow واحد نهائي.\n- **flatMapLatest:** يلغي التدفق الداخلي السابق فور وصول عنصر علوي جديد ويبدأ جمع التدفق الجديد (مثالي للبحث).\n- **flatMapConcat:** ينفذ التدفقات الداخلية بالتتابع الصارم؛ لا يبدأ التدفق الثاني إلا بعد اكتمال الأول بالكامل (مثالي لرفع الملفات بالترتيب).\n- **flatMapMerge:** ينفذ عدة تدفقات داخلية بالتوازي في نفس الوقت ويدمج انبعاثاتها فور وصولها (مثالي للتحميل المتوازي).\n- **معامل Concurrency:** التنبيه على خطورة ترك التزامن مفتوحاً في flatMapMerge وتحديد قيم معقولة.",
        "talking_points_ar": "ناقش كيف يُترجم flatMapLatest إلى transformLatest و emitAll، ومخاطر Head-of-line blocking في flatMapConcat، وإدارة الـ Buffer الداخلي في flatMapMerge.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يعتبر flatMapLatest هو الخيار الإلزامي في ميزات البحث التفاعلي؟\"\n  **المرشح:** \"لأن المستخدم لما بيكتب 'K' وبعدين بسرعة 'Ko' وبعدين 'Kot'، مش منطقي نستنى رد السيرفر عن حرف 'K' ونتجاهل أحدث كلمة. `flatMapLatest` بيلغي طلب الشبكة القديم في نفس اللحظة بـ CancellationException وبيبدأ طلب الكلمة الجديدة، وده بيوفر باقة الإنترنت ويمنع Race Conditions في عرض النتائج.\"\n\n- **المحاور:** \"ما هو الخطر القاتل في استخدام flatMapConcat؟\"\n  **المرشح:** \"لو التدفق الداخلي كان تدفق مستمر مبيخلصش (زي الاستماع لـ WebSocket أو مراقبة جدول في Room)، `flatMapConcat` هيفضل ماسك في التدفق الأول ده للأبد وعمره ما هينتقل للعنصر العلوي التاني، وده بنسميه Head-of-line blocking.\"",
        "self_check_ar": "هل بينت الفرق بدقة بين الأنماط الثلاثة؟ هل شرحت سر إلغاء flatMapLatest للطلبات السابقة؟ وهل حذرت من أخطار flatMapConcat و flatMapMerge؟",
        "references_ar": f"- [Kotlin Flow flattening operators](https://kotlinlang.org/docs/flow.html#flattening-flows) — دليل كوتلن الرسمي لمشغلات التسطيح.\n- [flatMapLatest official documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/flat-map-latest.html) — توثيق كوتلن الرسمي.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "`flatMapLatest` بيلغي التدفق القديم فوراً ويبدأ الجديد مع كل مدخل علوي وده الأنسب لمربعات البحث. و`flatMapConcat` بيعالج التدفقات بالتتابع الصارم ومبيبدأش التاني إلا لما الأول يخلص تماماً. أما `flatMapMerge` فبيشغل كذا تدفق بالتوازي مع بعض وبيدمج نتايجهم فور صدورها لتسريع التحميل.",
        "best_answer_ar": "مشغلات الـ Flattening وظيفتها إنها تحول كل عنصر علوي لـ Flow داخلي، وتدمج كل التدفقات الناتجة دي في Flow نهائي واحد للجامع، والفرق بينهم هو التزامن والإلغاء.\n\nمشغل `flatMapLatest` هو بطل واجهات المستخدم؛ وظيفته إنه يلغي التدفق الداخلي السابق فوراً لو وصل عنصر علوي جديد. يعني لو المستخدم كتب في مربع البحث حرف 'A' وبدأ السيرفر يبحث، وفجأة كتب 'B'، المشغل بيلغي استعلام 'A' فوراً ويبدأ استعلام 'AB' بدون ما يعطل الشاشة، وده بيمنع أي تضارب في النتائج.\n\nأما مشغل `flatMapConcat` فبيطبق مبدأ التتابع الصارم (Sequential Execution)؛ بياخد العنصر الأول ويشغل الـ Flow الداخلي بتاعه ويستنى لحد ما ينتهي بنسبة 100%، وبعدها يدخل على العنصر التاني، وده ممتاز لو عندك طابور عمليات لازم تمشي بالترتيب زي رفع ملفات معتمدة على بعض.\n\nومشغل `flatMapMerge` بيشغل التدفقات الداخلية بالتوازي في نفس الوقت، وبيدمج انبعاثاتهم في تيار واحد أول ما تجهز. وبياخد معامل `concurrency` بيحدد مسموح بكام تدفق يشتغل في نفس اللحظة، وده بيستخدم لتحميل صور أو ملفات متعددة بالتوازي لتسريع الأداء.",
        "deep_answer_ar": "على مستوى الميكانيزم الداخلي في كوتلن، `flatMapLatest` مبني فوق كود `transformLatest { emitAll(transform(it)) }`. أول ما بيوصل عنصر علوي جديد، الكوروتين الحاضنة للتدفق الداخلي السابق بيتبعت لها `CancellationException`، وده بيفكك مقابس الشبكة وطلبات الـ HTTP المعلقة فوراً ويوفر استهلاك الباندويث وبطارية الموبايل.\n\nأما `flatMapConcat`، فهو تحت الكابوت عملياً عبارة عن `flatMapMerge(concurrency = 1)`. هو بيعمل `collect` لكل تدفق داخلي داخل حلقة التجميع، وبيعلق الـ Emitter العلوي تماماً لحد ما التدفق الحالي يكمل. وهنا بيظهر الخطر القاتل المسمى بـ Head-of-line blocking؛ لو التدفق الداخلي كان تياراً مستمراً (زي مراقبة Room)، المشغل هيفضل عالق فيه ومش هينتقل للعنصر التاني أبداً.\n\nبالنسبة لـ `flatMapMerge`، فهو بيدير قناة وسيطة (Internal Channel) حجمها الافتراضي 16 (`DEFAULT_CONCURRENCY`). ورغم قوته في المهام المتوازية، تركه بالقيمة الافتراضية في أندرويد ممكن يفتح 16 اتصال شبكة أو استعلام داتابيز في نفس الوقت، وده بيخنق الـ Connection Pool ويستهلك الذاكرة.\n\nوفي اختبارات الـ Unit Testing، التحقق من سلوك التزامن بيتطلب محاكاة تأخير في التدفقات الداخلية للتأكد من إن المشغل شغال بالتوازي الفعلي ومبيكسرش حدود الذاكرة المحددة ليه.\n\nعلشان كده في بيئات الإنتاج، بنلزم الفرق باستخدام `flatMapLatest` حصراً لعمليات البحث والملاحة التفاعلية، ونقصر `flatMapConcat` على الطوابير الحتمية القصيرة، ونفرض تحديد سقف صارم للـ `concurrency` (زي 3 أو 4) مع `flatMapMerge` لحماية استقرار النظام."
    }
}

# ==========================================
# FLO-15: debounce and distinctUntilChanged for search
# ==========================================
DATA["FLO-15"] = {
    "concept_en": """The debounce and distinctUntilChanged operators represent the essential filtering pipeline for interactive search and high-frequency user input in modern Android applications.
debounce introduces a temporal rate-limiting window; it suppresses upstream emissions until a specified quiet duration (e.g., 300 milliseconds) has elapsed without any new emissions arriving. If the user types keystrokes rapidly within the window, the timer resets on each stroke, emitting only the final stable query once the user pauses typing.
distinctUntilChanged applies structural equality filtering; it discards consecutive duplicate emissions by evaluating Any.equals (or a custom comparator lambda) against the immediately preceding item.
Combined in a search pipeline, debounce eliminates redundant intermediate network requests during active keystroke bursts, while distinctUntilChanged prevents duplicate API executions if the user presses backspace and immediately retypes the identical character or triggers a redundant orientation event.""",
    "walkthrough_en": """Building an optimal production search pipeline:
```kotlin
class SearchViewModel(private val repository: SearchRepository) : ViewModel() {
    private val _searchQuery = MutableStateFlow("")
    val searchQuery = _searchQuery.asStateFlow()

    val searchResults: StateFlow<SearchUiState> = _searchQuery
        // 1. debounce: Wait 300ms of user silence before firing search
        .debounce(300L)
        // 2. filter: Do not search on empty query strings
        .filter { it.isNotBlank() }
        // 3. distinctUntilChanged: Ignore if text is identical to last searched string
        .distinctUntilChanged()
        // 4. flatMapLatest: Execute API and cancel if new debounced query arrives
        .flatMapLatest { query ->
            repository.searchCatalogFlow(query)
                .map { SearchUiState.Success(it) }
                .catch { emit(SearchUiState.Error(it.message ?: "Failed")) }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = SearchUiState.Idle
        )

    fun onQueryChanged(newQuery: String) {
        _searchQuery.value = newQuery
    }
}
```""",
    "short_en": """debounce delays emission until a specified quiet duration elapses without new user keystrokes, eliminating search spam; distinctUntilChanged suppresses consecutive identical query strings using Any.equals. Together with flatMapLatest, they construct the canonical, responsive Android search pipeline.""",
    "structured_en": """To begin with, debounce and distinctUntilChanged form the definitive rate-limiting foundation for search queries and user inputs.
From an architectural standpoint, debounce mitigates high-frequency input spam. When a user types a ten-character search phrase, firing an API call per keystroke floods the backend with ten rapid requests. debounce introduces a cooldown period (typically three hundred milliseconds), resetting the timer on each keystroke and emitting only when the user pauses typing.
In production scenarios, distinctUntilChanged suppresses consecutive identical items. If a user types a letter and immediately deletes it, or if configuration changes emit the same text snapshot, distinctUntilChanged compares the candidate string against the previous emission and drops it immediately.
As for boundary management, chaining debounce, distinctUntilChanged, and flatMapLatest prevents race conditions, saves mobile battery, drastically reduces server load, and guarantees that search results strictly reflect the user's latest stable intent.""",
    "deep_senior_en": """Under the hood in kotlinx.coroutines, debounce is implemented using a select expression paired with an internal Channel and a delay timer. When an upstream item arrives, debounce stores it in an internal reference slot and starts a timer coroutine for the configured timeout duration. If a new upstream item arrives before the timer completes, the select expression selects the upstream channel branch, replaces the stored reference with the newer item, and restarts the timer from scratch. Only when the timer completes without interruption does debounce emit the stored item downstream.
distinctUntilChanged maintains a single reference handle representing the last successfully emitted element. When a new element arrives, it evaluates: areEquivalent(previousKey, currentKey). If the structural equality evaluates to true, the element is discarded without notifying downstream collectors.
A subtle production pitfall involves testing debounce with coroutine test dispatchers. Because debounce relies on real-time delays, testing it via StandardTestDispatcher requires advancing virtual time using advanceTimeBy(301L) or runCurrent() to trigger the emission deterministically.
This layered pipeline guarantees that the UI layer remains exceptionally fluid even when users edit complex search queries at high typing speeds.
Staff engineers always pair this pipeline with flatMapLatest: debounce reduces request volume by 80%, distinctUntilChanged eliminates false triggers, and flatMapLatest guarantees that any in-flight slow search is cancelled if the user resumes typing after the pause.""",
    "meta_ar": {
        "id": "FLO-15",
        "questionAr": "اشرح دور debounce و distinctUntilChanged في بناء مربع بحث ذكي وسريع",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- الفهم الهندسي لتقييد معدل الإرسال (Rate Limiting) في واجهات المستخدم.\n- إدراك آلية عمل debounce في كتم الضربات السريعة وتوفير طلبات السيرفر.\n- معرفة دور distinctUntilChanged في منع التكرار وبناء مسار بحث متكامل مع flatMapLatest.",
        "why_it_matters_ar": "بدون `debounce`، كتابة كلمة من 10 حروف سترسل 10 طلبات HTTP متتالية للسيرفر في أقل من ثانيتين، مما يستنزف باقة المستخدم ويرهق خوادم الشركة وقد يتسبب في حظر المستخدم، بينما غياب `distinctUntilChanged` يكرر طلب البحث عند حذف حرف وإعادة كتابته فوراً.",
        "worked_example_ar": "المسار القياسي لبناء مربع بحث احترافي في أندرويد:\n```kotlin\nsearchQueryFlow\n    .debounce(300L) // انتظار 300 مللي ثانية بعد توقف المستخدم عن الكتابة\n    .filter { it.isNotBlank() } // تجاهل النصوص الفارغة\n    .distinctUntilChanged() // منع البحث لو النص مطابق لآخر بحث تم فعلياً\n    .flatMapLatest { query -> searchApi(query) } // إلغاء أي بحث قديم جاري\n    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), SearchState.Idle)\n```",
        "trade_offs_ar": "مهلة `debounce` القصيرة (100ms) قد ترسل طلبات كثيرة غير ضرورية، والمهلة الطويلة (800ms) تشعر المستخدم ببطء التطبيق. الرقم المثالي لمعظم التطبيقات يتراوح بين 300 إلى 400 مللي ثانية.",
        "failure_modes_ar": "نسيان `distinctUntilChanged` مما يكرر طلب البحث عند تدوير الشاشة لو أعادت الواجهة بث نفس النص. خطأ آخر هو وضع `debounce` بعد `flatMapLatest` بدلاً من قبله، مما يبطل مفعوله تماماً وينفذ كل الطلبات.",
        "production_perspective_ar": "في التطبيقات الضخمة، نضع مسار البحث هذا كمعيار في الـ UI Architecture. هذا المسار يقلل طلبات الشبكة بنسبة تفوق 80%، ويضمن استجابة فائقة للشاشة وتوفيراً كبيراً في استهلاك بطارية الجهاز وخوادم الـ Backend.",
        "how_to_answer_ar": "- **debounce:** تأجيل إرسال القيمة حتى تمر فترة هدوء محددة (عادة 300ms) دون كتابة أي حرف جديد؛ لتفادي إرسال طلب شبكة مع كل ضغطة كيبورد.\n- **distinctUntilChanged:** مقارنة القيمة الحالية بالقيمة السابقة بـ equals؛ لو متطابقتين تسقط القيمة وتمنع تكرار طلب نفس الكلمة.\n- **التكامل المعماري:** دمج الاثنين مع `flatMapLatest` لإلغاء أي طلب قديم لو بدأ المستخدم يكتب مجدداً.\n- **اختبار الكود:** الإشارة لكيفية اختبار debounce باستخدام `advanceTimeBy` في `runTest`.\n- **الأثر الإنتاجي:** توفير 80% من طلبات السيرفر وحماية التطبيق من الـ Rate Limiting.",
        "talking_points_ar": "ناقش تعبير select الداخلي والمؤقت في debounce، وفحص equals في distinctUntilChanged، وكيف يتعامل Turbine مع الوقت الافتراضي في الاختبارات.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لو المستخدم كتب حرف وحذفه بسرعة في أقل من 300 مللي ثانية؟\"\n  **المرشح:** \"المؤقت في `debounce` هيتصفر مع كل ضغطة زر، ولما يرجع لنفس الكلمة الأصلية وتعدي الـ 300ms، `distinctUntilChanged` هيفحص النص ويلاقيه مطابق لآخر نص تم البحث عنه، فيسقطه تماماً وميتبعتش أي طلب للسيرفر!\"\n\n- **المحاور:** \"لماذا نضع debounce قبل flatMapLatest وليس بعده؟\"\n  **المرشح:** \"لو وضعت `debounce` بعد `flatMapLatest`، هيكون طلب الشبكة اشتغل خلاص والـ Flow الداخلي اتنشأ، وده بيبطل فائدة الـ debounce تماماً. الترتيب الصحيح هو تصفية وتأخير النص أولاً، وبعد استقراره نمرره للـ `flatMapLatest` لتنفيذ البحث.\"",
        "self_check_ar": "هل وضحت الفارق بين وظيفة كل معامل؟ هل بينت سر دمجهم معاً في البحث؟ وهل شرحت الترتيب الصحيح للمشغلات؟",
        "references_ar": f"- [Flow debounce documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/debounce.html) — التوثيق الرسمي لمشغل debounce.\n- [Flow distinctUntilChanged documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/distinct-until-changed.html) — التوثيق الرسمي لمشغل distinctUntilChanged.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "`debounce` بيستنى فترة هدوء (زي 300ms) بعد ما المستخدم يبطل كتابة علشان يبعت الكلمة الأخيرة بس ويوفر طلبات السيرفر، و`distinctUntilChanged` بيمنع تكرار البحث لو النص مغيرش عن آخر مرة عبر فحص `equals`. دمجهم مع بعض مع `flatMapLatest` بيعمل مسار بحث احترافي وسريع جداً.",
        "best_answer_ar": "المشغلين `debounce` و `distinctUntilChanged` هما الركيزة الأساسية لبناء أي مربع بحث احترافي في أندرويد لحماية السيرفر والبطارية.\n\nمعامل `debounce` وظيفته هي التحكم في سرعة تدفق البيانات (Rate Limiting)؛ لما المستخدم بيكتب كلمة زي 'Android' في مربع البحث، بيكتبها في ثانية واحدة وبيضغط 7 حروف. فبدل ما نبعت 7 طلبات HTTP للسيرفر مع كل حرف، بنحط `debounce(300L)`؛ ده بيخلي الـ Flow يستنى 300 مللي ثانية هدوء بعد آخر ضغطة كيبورد، ولو المستخدم كتب حرف جديد بيصفر العداد، ومبيبعتش إلا الكلمة المستقرة بعد ما المستخدم يوقف كتابة.\n\nأما `distinctUntilChanged` فوظيفته منع التكرار السطحي؛ بيفحص القيمة الجديدة مقارنة بالقيمة السابقة بـ `equals()`. فلو المستخدم كتب حرف وحذفه بسرعة فرجع لنفس الكلمة، أو التطبيق اتعمله تدوير شاشة وبث نفس النص، المشغل بيسقط القيمة فوراً ومبيشغلش السيرفر بدون داعٍ.\n\nولما بنربطهم مع `flatMapLatest`، بنضمن إن لو المستخدم بدأ يكتب تاني وبحث عن كلمة تانية، أي طلب قديم كان لسه شغال بيتلغي فوراً، وده بيوفر أكتر من 80% من استهلاك الشبكة ويمنع أي تضارب في نتائج الواجهة.",
        "deep_answer_ar": "تحت الكابوت في كوتلن، `debounce` متصمم بطريقة عبقرية باستخدام تعبير `select` مع قناة داخلية ومؤقت تعليق (Timer Coroutine). أول ما بيوصل حرف جديد، بيتحط في متغير مرجعي ويبدأ مؤقت مدته 300ms. لو الـ Emitter بعت حرف تاني قبل ما المؤقت يخلص، الـ `select` بيفضل مسار القناة، ويستبدل المرجع بالحرف الجديد، ويعيد تشغيل المؤقت من الصفر. وفقط لما المؤقت ينتهي بدون أي مقاطعة، بيتم استدعاء `emit` للجامع السفلي.\n\nأما مشغل `distinctUntilChanged` فبيحتفظ بمرجع داخلي وحيد لآخر عنصر تم إرساله بنجاح، ولما يوصل عنصر جديد، بينفذ فحص التساوي البنيوي عبر `areEquivalent(old, new)` اللي بيعتمد على `Any.equals` افتراضياً. لو النتيجة `true`، الانبعاث بيتم كتمه فوراً بدون إشعار أي مشترك.\n\nالنقطة المهمة في بيئات الإنتاج هي اختبار المسار ده في الـ Unit Tests؛ لأن `debounce` بيعتمد على الوقت الحقيقي، فاختباره بـ `runTest` و `StandardTestDispatcher` بيتطلب استخدام `advanceTimeBy(301L)` لتقديم الوقت الافتراضي وإجبار الـ Flow على إخراج القيمة.\n\nوالمسار المحكم ده بيضمن إن الشاشة تفضل سلسة وسريعة الاستجابة حتى لو المستخدم كتب ومسح بسرعة عالية جداً على الكيبورد بدون أي تهنيج.\n\nوفي هندسة التطبيقات المصرفية والتجارية، بنلزم الفرق بوضع `debounce` و `distinctUntilChanged` قبل `flatMapLatest` مباشرة؛ لأن عكس الترتيب بيشغل نداء الشبكة ويلغي تأثير التهدئة، والترتيب الصحيح بيوفر ملايين الـ API Calls يومياً على السيرفرات."
    }
}

# ==========================================
# FLO-16: merge, buffer, conflate, collectLatest
# ==========================================
DATA["FLO-16"] = {
    "concept_en": """Managing stream combination, backpressure, and consumer-producer speed mismatches in Kotlin Flow requires a clear architectural distinction between merge, buffer, conflate, and collectLatest.
merge is an aggregation operator that combines multiple independent flows into a single unified stream, emitting elements concurrently from all sources without altering their internal timing or values.
buffer introduces an asynchronous Channel buffer between the upstream emitter and the downstream collector, decoupling their execution threads and allowing the upstream producer to continue producing items even if the downstream consumer is temporarily suspended.
conflate is a specialized backpressure mitigation operator that buffers only the single latest emission (buffer capacity of 1 with BufferOverflow.DROP_OLDEST); if the downstream collector is slower than the producer, intermediate pending emissions are dropped so the collector always receives the most recent snapshot.
collectLatest is a terminal operator that processes emissions sequentially by actively cancelling in-flight work: whenever a new element arrives upstream while the previous element's collector block is still executing, collectLatest cancels the previous coroutine block and starts processing the new element immediately.""",
    "walkthrough_en": """Comparing backpressure and stream merging strategies:
```kotlin
suspend fun demonstrateFlowBackpressure(flowA: Flow<Int>, flowB: Flow<Int>) {
    // 1. merge: Combines multiple flows into a single interleaved stream
    val mergedFlow = merge(flowA, flowB)

    // 2. buffer: Decouples fast producer from slow consumer with queue
    mergedFlow
        .buffer(capacity = 64)
        .collect { slowConsumerOperation(it) }

    // 3. conflate: Drops intermediate values when consumer is busy
    mergedFlow
        .conflate()
        .collect { latestState -> renderUi(latestState) }

    // 4. collectLatest: Cancels current execution when a new item arrives
    mergedFlow.collectLatest { item ->
        expensiveRendering(item) // Cancelled if next item arrives before this finishes!
    }
}
```""",
    "short_en": """merge combines multiple flows into one stream concurrently; buffer decouples producer and consumer with a channel queue; conflate skips intermediate pending emissions to deliver only the latest item; and collectLatest actively cancels active consumer processing whenever a new emission arrives.""",
    "structured_en": """To begin with, these operators address different dimensions of stream composition, concurrency, and consumer-producer rate mismatches.
From an architectural standpoint, merge aggregates multiple independent data streams into a single downstream pipeline without transforming data or altering pacing. We use it to merge real-time events from local databases and remote sockets into a unified event bus.
In production scenarios, buffer resolves rate discrepancies by introducing an intermediary queue. When a producer generates bursts faster than a database writer can consume, buffer allows the producer to continue without suspension until the queue fills.
As for boundary management, conflate and collectLatest address slow consumers through different strategies. conflate drops intermediate values silently in the buffer, allowing the collector to finish its current job before reading the newest state. In contrast, collectLatest immediately cancels the collector's active job in-flight to prioritize the fresh emission, ideal for UI animations and responsive search displays.""",
    "deep_senior_en": """Under the hood in kotlinx.coroutines.flow, the technical divergence between conflate and collectLatest represents a critical design choice between non-destructive latest-state delivery and cooperative cancellation.
conflate is implemented directly as buffer(CONFLATED), which allocates an internal Channel with a capacity of 1 and an overflow policy of DROP_OLDEST. When the collector is suspended executing a block, the upstream emitter pushes new items into the single-item buffer, overwriting previous pending items. Crucially, the collector's current execution block is never cancelled; it completes uninterrupted, and upon its next iteration, reads whatever latest element currently resides in the buffer slot.
Conversely, collectLatest launches each incoming emission inside an independent child coroutine using a conflated channel. If a previous child coroutine is still executing when a new emission arrives, it explicitly invokes job.cancel(), throwing CancellationException inside the active collector block.
This difference has profound architectural consequences: if processing an element involves non-cancellable or transactional operations (such as disk writes or database commits), collectLatest aborts the operation midway, creating partial corruption. In those scenarios, conflate guarantees complete execution of the current item while dropping intermediate noise safely.
This clear architectural segregation prevents corrupted offline database states while delivering flawless 60fps rendering in presentation components.
Staff engineers reserve collectLatest strictly for UI visual rendering, while applying buffer and conflate to data layer pipelines.""",
    "meta_ar": {
        "id": "FLO-16",
        "questionAr": "قارن بين merge و buffer و conflate و collectLatest في إدارة تدفق البيانات",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- الفهم العميق لآليات إدارة الضغط العكسي (Backpressure) في كوتلن.\n- التمييز بين دمج التدفقات (merge) وفصل الخيوط بطابور (buffer).\n- التمييز الدقيق بين إسقاط القيم الوسيطة (conflate) وإلغاء المعالجة الحالية (collectLatest).",
        "why_it_matters_ar": "الخلط بين `conflate` و `collectLatest` يسبب أخطاء خفية؛ فاستخدام `collectLatest` مع عمليات حفظ البيانات يلغي العملية في منتصفها ويخرب قاعدة البيانات، بينما غياب `buffer` أو `conflate` مع مستشعرات سريعة يتسبب في تجمد التطبيق واستهلاك الذاكرة.",
        "worked_example_ar": "مقارنة عملية في إدارة سرعة الإنتاج والاستهلاك:\n```kotlin\n// 1. merge: دمج إشعارات السيرفر مع أحداث الداتابيز في تيار واحد\nval allEvents = merge(remoteEventsFlow, localEventsFlow)\n\n// 2. buffer: يسمح للمنتج السريع بالاستمرار دون انتظار معالجة الداتابيز البطيئة\nallEvents.buffer(64).collect { saveToDisk(it) }\n\n// 3. conflate: يسقط الحالات القديمة ويضمن استلام أحدث حالة فقط دون إلغاء الكود الحالي\nstockTicks.conflate().collect { tick -> drawChart(tick) }\n\n// 4. collectLatest: يلغي رسم الفريم القديم فوراً للبدء في رسم الفريم الأحدث\nuiFrames.collectLatest { frame -> render(frame) }\n```",
        "trade_offs_ar": "`merge` تدمج دون تنظيم للسرعة. `buffer` تحافظ على كل البيانات ولكنها تستهلك ذاكرة إضافية للطابور. `conflate` تسقط البيانات الوسيطة مع إكمال العملية الحالية. `collectLatest` تلغي العملية الحالية فوراً للتركيز على الأحدث.",
        "failure_modes_ar": "استخدام `collectLatest` لعمليات كتابة الملفات مما يؤدي لإلغاء الكتابة وتلف الملف. خطأ آخر هو استخدام `buffer()` بدون سعة محددة مع منتج لا نهائي وسريع جداً مما يسبب OutOfMemoryError.",
        "production_perspective_ar": "في المشروعات الكبيرة، نعتمد `buffer` عند تحميل الملفات المتزامنة لتفادي تجميد الاتصال، ونستخدم `conflate` مع تدفقات البورصة والموقع الجغرافي لضمان عرض أحدث قيمة دون إجهاد المعالج، ونحصر `collectLatest` في تحريك الواجهة والبحث.",
        "how_to_answer_ar": "- **merge:** يدمج عدة تدفقات في تيار واحد ويعملون بالتوازي دون تعديل في السرعة.\n- **buffer:** يفصل خيط المنتج عن المستهلك عبر طابور وسيط؛ حتى لا يتعطل المنتج لو كان المستهلك بطيئاً.\n- **conflate:** يسقط القيم الوسيطة القديمة ويحتفظ بآخر قيمة فقط، ولكن الكود الحالي الشغال بيكمل للنهاية بدون إلغاء.\n- **collectLatest:** يلغي الكود الشغال حالياً فوراً بـ CancellationException لو وصل عنصر جديد ويبدأ الجديد.\n- **الفرق الجوهري:** conflate يكمل الشغل الحالي ويسقط اللي في الطابور، collectLatest يلغي الشغل الحالي فوراً.",
        "talking_points_ar": "ناقش الـ Internal Channel في buffer، وكيف يطبق conflate استراتيجية DROP_OLDEST، والفرق المعماري بين الإلغاء الفوري وإكمال الدورة الحالية.",
        "follow_ups_ar": "- **المحاور:** \"ما هو الفارق الدقيق بين conflate و collectLatest عند استلام قيمة جديدة؟\"\n  **المرشح:** \"مع `conflate`، لو الكوروتين مشغولة بتعالج عنصر، العنصر الجديد بيقعد في الـ Buffer والعنصر الحالي بيكمل شغله للنهاية بدون أي مقاطعة، وأول ما يخلص بياخد أحدث عنصر. أما مع `collectLatest`، فالشغل الحالي بيتلغي في نفس اللحظة بـ CancellationException وبيبدأ معالجة العنصر الجديد فوراً.\"\n\n- **المحاور:** \"متى تختار buffer بسعة محددة بدلاً من conflate؟\"\n  **المرشح:** \"بنختار `buffer` لما تكون كل البيانات مهمة ومينفعش نسقط أي عنصر (زي حفظ حركات الحساب البنكي أو قراءة سطور ملف)، فبنعمل Buffer يستوعب طفرات السرعة. أما `conflate` فبنختاره لما تكون البيانات عبارة عن حالات أو إحداثيات والمستخدم يهمه يشوف أحدث وضع فقط.\"",
        "self_check_ar": "هل فرقت بدقة بين المشغلات الأربعة؟ هل شرحت الفارق الدقيق بين conflate و collectLatest؟ وهل نبهت لمخاطر الإلغاء؟",
        "references_ar": f"- [Kotlin Flow buffering documentation](https://kotlinlang.org/docs/flow.html#buffering) — توثيق كوتلن الرسمي لـ buffer و conflate.\n- [Flow merge official API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/merge.html) — توثيق مشغل merge.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "`merge` بيدمج كذا تدفق في تيار واحد بالتوازي، و`buffer` بيعمل طابور وسيط يفصل سرعة المنتج عن المستهلك علشان المنتج ميتعطلش، و`conflate` بيسقط القيم القديمة ويسيب أحدث قيمة بس مع إكمال العملية الحالية، أما `collectLatest` فبيلغي العملية الحالية فوراً ويبدأ الأحدث أول ما يوصل عنصر جديد.",
        "best_answer_ar": "المشغلات دي بتمثل الأدوات الأساسية للتحكم في الضغط العكسي (Backpressure) وسرعة تدفق البيانات بين المنتج والمستهلك.\n\nمشغل `merge` وظيفته تجميعية بحتة؛ بياخد كذا Flow مستقل ويدمجهم في Flow واحد يبعت نواتجهم كلهم بالتوازي بدون أي تغيير في السرعة أو المحتوى.\n\nمشغل `buffer` بيحل مشكلة التفاوت المؤقت في السرعة؛ هو بينشئ طابور (Channel Queue) وسيط بين المنتج والمستهلك. فلو المنتج سريع والمستهلك بياخد وقت، المنتج بيفضل يرمي في الـ Buffer ومبيتعلقش، لحد ما الـ Buffer يتملي.\n\nأما الفارق الجوهري والشهير في المقابلات هو بين `conflate` و `collectLatest`:\nمع `conflate`، لو المستهلك شغال بيعالج عنصر والمنتج بعت 5 عناصر سريعة، الـ 5 عناصر هيتم إسقاطهم وهيحتفظ بآخر عنصر بس، لكن الميزة الكبرى إن المعالجة الحالية هتكمل للنهاية بنجاح وبدون أي إلغاء، وده مناسب لكتابة الداتابيز وحفظ البيانات.\n\nفي المقابل، `collectLatest` مش بيستنى المستهلك يخلص؛ أول ما يوصل عنصر جديد بيلغي الشغل الحالي فوراً في منتصفه ويبدأ معالجة العنصر الجديد في الحال، وده ممتاز للبحث وتحريك الرسومات في الواجهة لكنه خطير جداً لعمليات الحفظ.",
        "deep_answer_ar": "تحت الكابوت في `kotlinx.coroutines.flow`، الفارق الهندسي بين `conflate` و `collectLatest` بيحدد استقرار النظام وتفادي تلف البيانات.\n\nمشغل `conflate` ما هو إلا اختصار لـ `buffer(capacity = 1, onBufferOverflow = BufferOverflow.DROP_OLDEST)`. لما المستهلك بيكون معلق في عملية معالجة، المنتج بيكتب في الـ Slot الوحيد ده وبيستبدل القديم بالجديد، لكنه مبيلمسش الكوروتين الحالية بتاعة المشترك؛ بتكمل شغلها بهدوء، وأول ما تلف اللفة الجاية بتقرا أحدث قيمة اتكتبت. ده بيخليه الخيار الأمثل والآمن هندسياً للتعامل مع تدفقات البورصة وحساسات الـ GPS لما نكون بنعمل عمليات كتابة في الداتابيز.\n\nأما `collectLatest`، فبيعتمد على إنشاء كوروتين فرعية لكل عنصر جديد وإلغاء الكوروتين السابقة عبر `job.cancel()`. الإلغاء ده بيرمي `CancellationException` داخلي؛ فلو كان الكود جواه عمليتين حفظ في الداتابيز أو كتابة ملف على الـ Disk، الكود هيتقطع في نصه والملف هيبوظ أو الداتابيز هتفقد ترابطها.\n\nومشغل `buffer(capacity)` بيستخدم قناة من نوع `ArrayChannel`. لو حددت capacity بـ 64، المنتج مش هيتعلق إلا لو الطابور اتملى بالـ 64 عنصر، وده بيوفر توازن ممتاز للعمليات الدورية ذات الطفرات المؤقتة.\n\nعلشان كده في بيئات الإنتاج، بنتبع قاعدة معمارية صارمة: `buffer` للمهام المتسلسلة ذات الطفرات، و`conflate` للمهام التي تكتفي بآخر لقطة مع ضمان إكمال الحفظ، و`collectLatest` حصراً لرسوميات الشاشة ومربعات البحث التفاعلية."
    }
}


def main():
    print(f"Elevating 8 questions in FLO (FLO-09 to FLO-16)...")
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
    meta_path = ee.DATA_DIR / "metadata_flo_09_16.json"
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
        print("All 8 FLO questions (FLO-09 to FLO-16) successfully elevated and passed validation!")


if __name__ == "__main__":
    import json
    main()

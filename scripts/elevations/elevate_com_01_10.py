#!/usr/bin/env python3
"""
Elevation script for COM-01 to COM-10 (Jetpack Compose - Batch 1).
Complete bilingual parity, senior conversational spoken style, zero bullet points in spoken text.
"""

import sys
from pathlib import Path

# Add scripts/elevations to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "elevations"))
import elevation_engine as ee

TOPIC_AR = ee.TOPIC_AR_NAMES["COM"]
REVIEWED_DATE_AR = "تمت المراجعة في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# COM-01: What is Compose? Compare declarative Compose and XML Views.
# ==========================================
DATA["COM-01"] = {
    "concept_en": """Jetpack Compose is Android's modern, reactive declarative UI toolkit that transforms pure Kotlin functions into dynamic visual layouts. Unlike the legacy imperative View system, which relies on inflating XML hierarchy trees, retaining mutable view instances in memory, and manually mutating widget properties via findViewByOrViewBinding and setters, Compose operates as a pure function of state: UI equals f(State). Developers describe what the interface looks like for any given state snapshot, and the Compose compiler and runtime automatically calculate layout diffs and re-execute only the affected composable nodes during recomposition.""",
    "walkthrough_en": """Contrasting legacy imperative XML mutations with declarative Jetpack Compose state-driven layouts:
```kotlin
// LEGACY IMPERATIVE XML VIEW APPROACH:
// Developer manually tracks state and mutates view properties, risking state desynchronization
class ProfileActivity : AppCompatActivity() {
    private lateinit var binding: ActivityProfileBinding

    fun updateUi(isLoading: Boolean, user: User?) {
        if (isLoading) {
            binding.progressBar.visibility = View.VISIBLE
            binding.userNameTextView.visibility = View.GONE
        } else {
            binding.progressBar.visibility = View.GONE
            binding.userNameTextView.visibility = View.VISIBLE
            binding.userNameTextView.text = user?.name.orEmpty()
        }
        // State can easily become desynchronized if multiple async callbacks mutate views concurrently!
    }
}

// MODERN DECLARATIVE JETPACK COMPOSE APPROACH:
// UI is a pure function of state: UI = f(State)
@Composable
fun ProfileScreen(state: ProfileUiState) {
    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        when (state) {
            is ProfileUiState.Loading -> CircularProgressIndicator()
            is ProfileUiState.Success -> Text(
                text = state.user.name,
                style = MaterialTheme.typography.titleLarge
            )
            is ProfileUiState.Error -> Text(text = state.errorMessage, color = Color.Red)
        }
    }
}
```""",
    "short_en": """Jetpack Compose is a declarative UI toolkit where you describe what the UI should look like for a given state, rather than imperatively mutating View hierarchies. In traditional XML, you inflate stateful widgets and manually update them via findViewById or ViewBinding, which frequently causes UI state desynchronization and memory leaks. In Compose, your UI is a pure function of state: whenever the underlying state changes, the runtime automatically recomposes only the affected functions, eliminating boilerplate and sync bugs.""",
    "structured_en": """Transitioning from legacy XML Views to Jetpack Compose represents a foundational paradigm shift from imperative UI mutation to reactive declarative rendering.
In the legacy View system, UI widgets are heavyweight, stateful Java objects inheriting from android.view.View. When state changes, developers must imperatively locate widgets and mutate their internal properties, toggling visibility, setting text, or attaching listeners. This approach breeds state desynchronization bugs, where a progress bar remains visible because an error branch forgot to hide it, or views retain old data during configuration changes.
Jetpack Compose replaces this with a declarative paradigm where UI is a pure projection of data.
Composables are stateless functions annotated with @Composable that emit layout nodes into an internal SlotTable.
Developers simply declare how the UI should appear for each state variant. When state updates, the Compose runtime performs smart recomposition, diffing parameter changes and re-invoking only the composables that observe the modified data.
Because Compose is written entirely in Kotlin, developers eliminate the XML impedance mismatch, gain full type safety, and share code seamlessly across Multiplatform targets.""",
    "deep_senior_en": """Under the hood, the difference between Compose and XML Views is rooted in memory layout, dispatch trees, and compiler-driven code transformation.
The legacy View system constructs a physical tree of View and ViewGroup objects on the heap. Each View is an expensive object carrying hundreds of member fields, layout caches, transformation matrices, and drawing drawables. Traversing, measuring, and drawing this tree requires multiple recursive passes, leading to deep call stacks and garbage collection churn during rapid list scrolling.
Jetpack Compose completely bypasses android.view.View. Instead, the Compose compiler plugin intercepts every @Composable function, inserting synthetic parameters including a Composer instance and bitmask change flags.
During execution, the Composer reads and writes nodes into a continuous memory array known as the SlotTable, structured like a gap buffer. When a state object backed by SnapshotState changes, the runtime identifies the affected slot intervals and executes smart recomposition without traversing unaffected siblings.
Layout and drawing are handled directly through a flattened layout node hierarchy that measures children in a single O(N) pass, completely eradicating the double-taxation measuring problem notorious in legacy RelativeLayout or nested LinearLayout hierarchies. This architectural reduction in object allocations delivers smoother frame rates and drastically reduces APK rendering overhead. Furthermore, Compose dispatches drawing commands directly to the platform hardware canvas via lightweight DrawModifier nodes, avoiding unnecessary intermediate ViewGroup rendering passes.""",
    "meta_ar": {
        "id": "COM-01",
        "questionAr": "ما هو Jetpack Compose؟ وقارن بين النمط التصريحي (Declarative) ونمط XML التقليدي (Imperative).",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم التحول المعماري الجذري من XML إلى Compose، وإدراك معادلة UI = f(State)، واستيعاب آلية الـ SlotTable وتفادي مشاكل عدم تزامن الحالة (State Desynchronization) وضريبة القياس المزدوج.",
        "why_it_matters_ar": "نظام XML القديم يعتمد على تعديل الـ Views يدوياً مما يسبب ثغرات شائعة مثل نسيان إخفاء Loading أو تسريب الذاكرة، بينما Compose يقضي على ذلك بجعل الواجهة انعكاساً مباشراً للحالة البرمجية.",
        "worked_example_ar": "مقارنة بين XML و Compose في عرض حالة التحميل:\n```kotlin\n// XML: تعديل يدوي عرضة للخطأ\nfun render(loading: Boolean) { btn.visibility = if (loading) GONE else VISIBLE }\n// Compose: دالة نقية تعبر عن الحالة تلقائياً\n@Composable fun Screen(state: UiState) {\n    if (state.isLoading) CircularProgressIndicator() else Content(state.data)\n}\n```",
        "trade_offs_ar": "يتطلب Compose تعلماً جديداً لعقلية الـ Recomposition وفهم دورة حياة الدوال، لكنه يختصر نصف كود الـ UI، ويلغي ملفات XML تماماً، ويوفر أداءً أعلى بكثير في الرسم.",
        "failure_modes_ar": "محاولة التعامل مع دوال Compose بنفس عقلية XML، مثل الاحتفاظ بمتغيرات Views داخل الكومبوزابل ومحاولة تغيير خصائصها يدوياً بدلاً من الاعتماد على الـ State.",
        "production_perspective_ar": "في المشروعات الحديثة، جوجل أعلنت Compose كالمعيار الافتراضي والرسمي لبناء الواجهات، ونعتمد عليه في بناء Design Systems موحدة ومشاركتها مع Kotlin Multiplatform.",
        "how_to_answer_ar": "ابدأ بالتعريف: Compose هو Declarative UI Toolkit تعتمد على UI = f(State)، وقارنها بـ XML: في XML نعدل الكائنات يدوياً بـ findViewById أو ViewBinding مما يسبب State Desynchronization، بينما في Compose الواجهة تتحدث تلقائياً مع تغير الـ State، واذكر الفارق العميق في الأداء وإلغاء شجرة الـ Views الثقيلة.",
        "talking_points_ar": "معادلة UI = f(State)، ومشاكل State Desynchronization في XML، وآلية الـ SlotTable و Gap Buffer في Compose، وإلغاء ضريبة القياس المزدوج (Double Taxation).",
        "follow_ups_ar": "- **المحاور:** \"ما هي مشكلة القياس المزدوج (Double Taxation) التي حلتها Compose؟\"\n  **المرشح:** \"في XML كان الـ ViewGroup زي LinearLayout بـ weights يقيس الأبناء مرتين في كل تمرير مما يسبب بطئاً شديداً في الشاشات المتداخلة، بينما Compose بتفرض قياساً واحداً فقط O(N) ممنوع التراجع عنه.\"\n\n- **المحاور:** \"هل يحتاج Compose إلى جسر (Bridge) للتواصل مع شاشات XML القديمة؟\"\n  **المرشح:** \"نعم، بنستخدم `ComposeView` داخل كود XML، وبنستخدم `AndroidView` لاستضافة مكونات قديمة زي MapView داخل Compose بسلاسة تامة.\"",
        "self_check_ar": "هل عرفت النمطين بوضوح؟ هل شرحت مشكلة مزامنة الحالة في XML؟ وهل بينت كيف يعمل Compose من الداخل عبر الـ SlotTable؟",
        "references_ar": f"- [Jetpack Compose Mental Model](https://developer.android.com/develop/ui/compose/mental-model) — الدليل الرسمي لجوجل للنموذج الذهني لكومبوز.\n- [Under the hood of Jetpack Compose](https://medium.com/androiddevelopers/under-the-hood-of-jetpack-compose-part-1-of-2-501861ec3f) — شرح معماري لمترجم ورنتايم كومبوز.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "جيتباك كومبوز هو أحدث إطار عمل تصريحي (Declarative UI) لبناء واجهات أندرويد بلغة كوتلن بالكامل. الفارق الجوهري بينه وبين نظام الـ XML التقليدي هو إن XML يعتمد على نمط إجرائي (Imperative) بننشئ فيه كائنات View ثقيلة ونعدل خصائصها يدوياً زي `setVisibility`، وده بيخلق أخطاء نسيان مزامنة الحالة وتكرار الكود. أما في كومبوز، الواجهة بتكون دالة نقية في الحالة (UI = f(State))؛ بنوصف شكل الشاشة لكل حالة، ومحرك كومبوز بيحدث الأجزاء المتأثرة تلقائياً في لمح البصر بدون أي تدخل يدوي.",
        "best_answer_ar": "التحول من XML إلى Jetpack Compose مش مجرد تغيير في طريقة كتابة الكود، بل هو تحول جذري في النموذج الذهني لكيفية عمل واجهة المستخدم في أندرويد.\n\nفي نظام XML القديم، كنا بنتعامل بأسلوب الـ Imperative؛ كل زرار أو نص هو كائن جافا ضخم وارث من `android.view.View` وله حالة داخلية خاصة به (Mutable State). المطور كان بيضطر يبحث عن الكائن بـ ViewBinding، ويعدل نصه أو يغير ظهوره يدوياً بناءً على استجابة السيرفر. ده كان بينتج عنه مشكلة مزمنة بنسميها State Desynchronization؛ تلاقي دايرة التحميل فضلت تلف لأن فرع معالجة الخطأ نسي يكتب `progressBar.visibility = GONE`.\n\nكومبوز لغت الطريقة دي تماماً واعتمدت النمط التصريحي (Declarative)، حيث الواجهة انعكاس كامل للحالة البرمجية: UI = f(State).\nبدل ما تعدل الواجهة، أنت بتكتب دوال كوتلن بتوصف شكل الشاشة لو البيانات موجودة، وشكلها لو بنحمل، وشكلها لو فيه خطأ. أول ما بيانات الـ ViewModel تتغير، الرنتايم بيعمل Recomposition ذكي ويعيد رسم الدوال المعنية فقط.\n\nده بيلغي آلاف أسطر البويلربليت، ويحقق أمان الأنواع بنسبة 100%، ويمنع تسريبات الذاكرة، ويسمح بمشاركة كود الواجهات مستقبلاً مع Kotlin Multiplatform.",
        "deep_answer_ar": "تحت الكابوت، الفارق بين Compose و XML بيبدأ من إدارة الذاكرة وطريقة معالجة شجرة العناصر في معالج أندرويد.\n\nفي نظام الـ View التقليدي، كل كلاس وارث من `View` هو كائن ثقيل جداً بيحجز في الـ Heap مئات المتغيرات والمصفوفات والـ Drawables، وده بيشكل ضغطاً كبيراً على الـ Garbage Collector أثناء التمرير في القوائم. وفوق كده، عملية قياس ورسم الشجرة كانت بتعاني من مشكلة الـ Double Taxation؛ كلاسات زي `RelativeLayout` أو `LinearLayout` ذات الأوزان كانت بتقيس العناصر مرتين أو أكتر في كل Frame، وده بيسبب هبوط في الـ 60fps.\n\nكومبوز تخطت كلاس `View` تماماً. لما بتكتب دالة `@Composable`، الكومبايلر بيعمل تحويل سحري للبايت كود؛ بيحقن باراميتر اسمه `Composer` ومصفوفة من الـ Bitmasks. الرنتايم بيخزن شجرة الواجهة في هيكل بيانات خطي بالذاكرة اسمه `SlotTable` بيشتغل زي الـ Gap Buffer.\n\nلما قيمة الحالة (SnapshotState) تتغير، محرك كومبوز مش بيمشي في شجرة Views كاملة، بل بيقرأ الـ SlotTable ويعرف بالظبط إيه النودز اللي اتغيرت مدخلاتها، ويعمل لها تخطي (Skipping) لو المدخلات مستقرة. والقياس بيتم في تمرير واحد إجباري O(N) بيلغي الـ Double Taxation نهائياً، وده بيضمن أعلى كفاءة في استهلاك الرام وسلاسة تامة في الرندرة."
    }
}

# ==========================================
# COM-02: What is a @Composable function? What is recomposition?
# ==========================================
DATA["SOL-02"] = None  # placeholder guard

DATA["COM-02"] = {
    "concept_en": """A @Composable function is a Kotlin function annotated with @Composable that serves as a basic building unit in Jetpack Compose, emitting UI nodes into the composition graph rather than returning a value. The @Composable annotation alters the function's calling conventions at compile time, allowing it to read and write state, access composition locals, and participate in lifecycle management. Recomposition is the process whereby the Compose runtime re-executes composable functions in response to state changes to update the visual UI tree, intelligently skipping any functions whose input parameters have not changed.""",
    "walkthrough_en": """Demonstrating a Composable function, state observation, and recomposition execution:
```kotlin
// A pure Composable function that observes state and re-executes during recomposition
@Composable
fun CounterWidget(count: Int, onIncrement: () -> Unit) {
    // This function will re-execute (recompose) whenever 'count' changes
    Column(
        modifier = Modifier.padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Current Taps: $count",
            style = MaterialTheme.typography.headlineMedium
        )
        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = onIncrement) {
            Text("Increment")
        }
    }
}

// Side-effects MUST NOT be placed directly in the composable body, as recomposition can happen frequently!
@Composable
fun BadAnalyticsComposable(screenName: String) {
    // ❌ ANTI-PATTERN: Side-effect executed directly in the body! Runs on EVERY recomposition!
    // analytics.track(screenName) 

    // ✅ BEST PRACTICE: Wrap side-effects inside dedicated effect handlers
    LaunchedEffect(screenName) {
        // Runs only when screenName changes, not on every random recomposition!
    }
}
```""",
    "short_en": """A @Composable function is a Kotlin function annotated with @Composable that describes UI layout and emits nodes into the composition hierarchy. Recomposition is the automatic re-execution of composable functions by the runtime whenever their observed state changes. During recomposition, Compose inspects function parameters and intelligently skips re-running any composables whose inputs remain identical, ensuring high rendering performance and smooth 60fps animations.""",
    "structured_en": """Understanding @Composable functions and recomposition mechanics is the cornerstone of writing performant Jetpack Compose applications.
The @Composable annotation is a compiler directive that fundamentally transforms a function's bytecode. Much like Kotlin's suspend keyword, @Composable alters the function type, enabling it to be invoked only from within another composable context. Instead of constructing and returning a View instance, a composable function accepts state parameters and emits declarative UI layout descriptions.
Recomposition is Compose's reactive update mechanism.
When a snapshot state variable read by a composable changes, the Compose runtime invalidates that specific function scope.
During the subsequent frame rendering phase, Compose re-executes the invalidated composables with the updated state values.
Because recomposition can occur on every single animation frame (up to 120 times per second), composable functions must remain idempotent, pure, and completely free of direct side-effects like database queries, network requests, or direct analytics tracking.
Compose ensures optimal performance through smart skipping: if a composable's arguments are stable and unchanged, the runtime skips its execution entirely, updating only the modified leaf nodes.""",
    "deep_senior_en": """Under the hood, the @Composable annotation activates the Compose Compiler plugin, which rewrites the function signature by appending two synthetic parameters: a Composer instance and an integer bitmask (changed).
The Composer parameter acts as a low-level broker between your code and the SlotTable. It tracks code location keys, allocates slots for remember calculations, records state read dependencies, and manages the execution stack.
The changed integer parameter contains bit flags that communicate the stability and mutation status of every input argument across recompositions. Before executing the function body, the compiled bytecode evaluates a conditional check comparing current arguments with previous values stored in the SlotTable. If all arguments are unchanged and stable, the function branches immediately to the end of the method, achieving zero-allocation skipping.
Furthermore, the Compose runtime does not guarantee that recomposition runs in top-down sequential order, nor does it guarantee that recomposition executes on the main thread during speculative phases.
Recomposition can also be canceled mid-execution if state updates again before the frame completes, discarding the intermediate composition work.
Senior engineers design composables to be completely side-effect free, delegating asynchronous tasks and imperative mutations exclusively to lifecycle-aware effect primitives like LaunchedEffect or DisposableEffect. By keeping composables deterministic and referentially transparent, the runtime safely parallelizes composition across worker threads in future compiler optimizations without risking concurrency locks or corrupted UI state.""",
    "meta_ar": {
        "id": "COM-02",
        "questionAr": "ما هي دالة @Composable؟ وما هي عملية إعادة التركيب (Recomposition) في Compose؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم دور الـ `@Composable` annotation وتحويلها للبايت كود، واستيعاب مفهوم الـ Recomposition، وقواعد الدوال النقية (Idempotent Composables)، وكيفية حدوث الـ Smart Skipping عبر باراميتر الـ Composer ومصفوفة الـ changed flags.",
        "why_it_matters_ar": "كتابة آثار جانبية (Side-effects) عشوائية داخل دالة Composable يؤدي لتكرار العمليات الحسابية أو طلبات الشبكة عشرات المرات في الثانية عند حدوث الـ Recomposition، مما يسبب بطء التطبيق ونفاذ البطارية.",
        "worked_example_ar": "الفرق بين كود نقي وكود ملوث بآثار جانبية داخل الكومبوزابل:\n```kotlin\n@Composable fun Counter(count: Int) {\n    // ❌ كود كارثي: يتكرر مع كل فريم!\n    // Analytics.track(\"screen\")\n    // ✅ كود صحيح: معزول في LaunchedEffect\n    LaunchedEffect(Unit) { Analytics.track(\"screen\") }\n    Text(\"Count: $count\")\n}\n```",
        "trade_offs_ar": "إعادة التركيب المتكررة توفر واجهة متزامنة دائماً مع البيانات، لكنها تتطلب التزاماً صارماً بعدم وضع أي منطق بطيء أو آليات ثقيلة داخل جسم الدالة مباشرة.",
        "failure_modes_ar": "استدعاء عمليات شبكة أو كتابة في قاعدة بيانات داخل جسم دالة `@Composable` مباشرة، مما يسبب تكرارها مئات المرات عند أي تحديث بسيط للحالة.",
        "production_perspective_ar": "في كود الإنتاج، نلزم المطورين بجعل كل الـ Composables نقية وخالية من الآثار الجانبية، واستخدام Layout Inspector في Android Studio لتتبع عدد مرات حدوث الـ Recomposition واكتشاف أي Recomposition Loops.",
        "how_to_answer_ar": "عرف دالة Composable: دالة كوتلن تصف الواجهة وتبث نودز في شجرة الكومبوز، وعرف Recomposition: إعادة تنفيذ الدالة آلياً عند تغير الـ State، وشدد على أنها قد تحدث في كل فريم (120 مرة بالثانية) ويجب أن تكون نادرة الآثار الجانبية (Idempotent)، واشرح كيف يوفر المترجم باراميتر Composer للقيام بالـ Skipping الذكي.",
        "talking_points_ar": "تحويل البايت كود وحقن باراميتر Composer، والـ changed bitmask، ومفهوم Idempotent Composables، وإمكانية إلغاء الـ Recomposition في المنتصف، والـ Smart Skipping.",
        "follow_ups_ar": "- **المحاور:** \"هل تضمن كومبوز تشغيل دوال الـ Composable بنفس الترتيب الذي كُتبت به في الكود؟\"\n  **المرشح:** \"لا، كومبوز تملك الحرية الكاملة في تشغيل الدوال بترتيب مختلف أو بالتوازي على عدة خيوط معالجة لتحسين سرعة العرض.\"\n\n- **المحاور:** \"ماذا يحدث إذا تغيرت الحالة أثناء تنفيذ عملية Recomposition لم تكتمل بعد؟\"\n  **المرشح:** \"كومبوز بتلغي عملية الـ Recomposition الحالية فوراً، وترمي التغييرات الوسيطة، وتبدأ عملية Recomposition جديدة بالحالة الأحدث.\"",
        "self_check_ar": "هل عرفت الدالة وإعادة التركيب بدقة؟ هل شددت على ضرورة كون الدالة نقية؟ وهل شرحت دور Composer والـ Bitmask في الـ Skipping؟",
        "references_ar": f"- [Compose Programming Model](https://developer.android.com/develop/ui/compose/mental-model#recomposition) — الدليل الرسمي لإعادة التركيب.\n- [Under the hood of Jetpack Compose: Recomposition](https://medium.com/androiddevelopers/) — توثيق معماري لمترجم كومبوز.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "دالة `@Composable` هي وحدة البناء الأساسية في كومبوز؛ دالة كوتلن عادية مميزة بـ Annotation بتخليها توصف جزءاً من واجهة المستخدم وتبث نودز في الشجرة بدل ما ترجع قيمة. أما الـ Recomposition فهو عملية إعادة تشغيل الدوال دي تلقائياً بواسطة محرك كومبوز لما الحالة (State) اللي بتراقبها تتغير. أثناء إعادة التركيب، كومبوز بتفحص المدخلات بذكاء؛ لو المدخلات ثابتة ولم تتغير، بتتخطى الدالة تماماً (Skipping)، وبتنفذ فقط الدوال اللي بياناتها اتغيرت عشان تحافظ على سلاسة الـ 60 إطار في الثانية.",
        "best_answer_ar": "لفهم كومبوز باحترافية، لازم تفهم العلاقة بين دالة الـ Composable وعملية الـ Recomposition.\n\nالـ `@Composable` مش مجرد علامة شكلية، بل هي توجيه للكومبايلر بيغير طبيعة الدالة بالكامل زي كلمة `suspend`. الدالة دي مبيتمش استدعاؤها إلا داخل سياق كومبوز، ووظيفتها مش رسم بكسلات على الشاشة مباشرة، بل إصدار تعليمات بناء في هيكل بيانات وسيط.\n\nالـ Recomposition هو محرك التحديث التفاعلي في كومبوز.\nلما قيمة متغير من نوع `SnapshotState` بيتغير، رنتايم كومبوز بيعلم النطاق اللي قرأ المتغير ده بإنه غير صالح (Invalidated). ومع الفريم الجديد، بيعيد تشغيل الدالة دي بالقيمة الجديدة عشان الواجهة تتحدث.\n\nالنقطة الحرجة اللي بنسأل عنها في مقابلات السينيور هي: إن الـ Recomposition ممكن يحصل 60 أو 120 مرة في الثانية مع حركات الأنيميشن أو التمرير السريع. لذلك، القاعدة الذهبية إن دالة الـ Composable لازم تكون نادرة الآثار الجانبية (Idempotent)؛ ممنوع نهائياً تحط جواها طلب شبكة أو كتابة في قاعدة بيانات أو كود تحليلات مباشر، لأن الكود ده هيتكرر عشرات المرات ويدمر أداء التطبيق. كل العمليات الإجرائية لازم تتحط في Side-Effect Handlers زي `LaunchedEffect`.",
        "deep_answer_ar": "تحت الكابوت، مترجم كومبوز (Compose Compiler) بيقوم بعملية تحويل بايت كود عميقة لكل دالة متوضحة بـ `@Composable`؛ بيحقن باراميترين إضافيين بشكل خفي: الأول هو كائن `Composer` والتاني هو عدد صحيح يمثل مصفوفة أعلام `changed` (Bitmask).\n\nكائن الـ Composer ده هو القلب النابض؛ هو اللي بيسجل مكان الدالة في شجرة الـ SlotTable، وبيحفظ نتائج كود `remember`، وبيسجل قراءات الحالة عشان يعرف بالظبط مين اللي هيتأثر لما المتغير يتغير. أما مصفوفة الـ Bitmask فبتحتوي على بتات بتوضح حالة كل باراميتر ممرر للدالة؛ هل هو مستقر (Stable)؟ وهل اتغيرت قيمته عن المرة السابقة ولا لأ؟\n\nقبل ما الدالة تبدأ تنفذ جسمها، البايت كود بيعمل فحص شرطي سريع: لو كل المدخلات قيمها مطابقة لما هو مسجل في الـ SlotTable، الكومبايلر بيعمل قفزة فورية لآخر الدالة (Smart Skipping) بدون استهلاك أي وقت معالجة أو حجز كائنات جديدة في الذاكرة.\n\nعلاوة على كده، رنتايم كومبوز مش بيلتزم بتشغيل الدوال بالترتيب الخطي المكتوب في الملف، وممكن يشغلها على خيوط معالجة مختلفة، ولو الحالة اتغيرت أثناء ما عملية الـ Recomposition شغالة، الرنتايم عنده القدرة إنه يلغي العملية في منتصفها (Cancellation)، ويرمي النتائج غير المكتملة، ويبدأ من جديد بالحالة الأحدث، وده التصميم العبقري اللي بيضمن أعلى سرعة استجابة في أندرويد."
    }
}

# ==========================================
# COM-03: What triggers recomposition, and what can be skipped?
# ==========================================
DATA["COM-03"] = {
    "concept_en": """Recomposition is triggered when a composable function reads a Snapshot State object whose underlying value changes during state mutation. However, Compose does not blindly re-execute the entire UI hierarchy; instead, it enforces fine-grained, localized recomposition. A composable function can be completely skipped if all of its input parameters are determined to be Stable or Immutable by the Compose compiler and their runtime values remain unchanged since the previous composition. Conversely, functions accepting unstable types (such as standard Java/Kotlin collections like List, or mutable data classes with var properties) cannot be proven unchanged, forcing Compose to re-execute them conservatively on every recomposition pass.""",
    "walkthrough_en": """Contrasting an unskippable composable with a fully skippable composable:
```kotlin
// ❌ FAILS TO SKIP: Standard Kotlin List is considered UNSTABLE by Compose Compiler!
// Even if the list content is identical, UserList will ALWAYS re-execute whenever parent recomposes!
@Composable
fun UnstableUserList(users: List<String>, onUserClick: (String) -> Unit) {
    LazyColumn {
        items(users) { user -> Text(user, modifier = Modifier.clickable { onUserClick(user) }) }
    }
}

// ✅ ARCHITECTURAL BEST PRACTICE: Fully skippable composable using Immutable wrapper or Kotlinx Immutable
@Immutable
data class UserListState(val users: List<String>) // Marked @Immutable promises compiler list will never mutate!

@Composable
fun StableUserList(
    state: UserListState, // Stable type!
    onUserClick: (String) -> Unit // Stable lambda reference!
) {
    // Compose compiler successfully SKIPS this function if state and lambda have not changed!
    LazyColumn {
        items(state.users) { user -> Text(user, modifier = Modifier.clickable { onUserClick(user) }) }
    }
}
```""",
    "short_en": """Recomposition is triggered whenever a Snapshot State object read by a composable function is modified. A composable can be skipped if all its input arguments are stable and equal to their previous composition values. The Compose compiler marks primitive types, Strings, function lambdas, and classes annotated with @Immutable or @Stable as stable. However, standard collections like List or classes with mutable var properties are treated as unstable, forcing Compose to re-execute the composable even if the underlying data has not changed.""",
    "structured_en": """Achieving peak UI performance in Jetpack Compose depends on understanding the exact mechanics governing recomposition triggers and compiler skipping.
Recomposition is not triggered by arbitrary background variable modifications; it is triggered strictly when a function reads a Snapshot State object (such as mutableStateOf or StateFlow converted via collectAsState) whose value subsequently updates.
Compose analyzes function signatures to determine skippability.
A composable is deemed skippable if all its parameters are stable. Stable types guarantee that if two instances are equal via equals(), they will never silently mutate over time.
The Compose compiler automatically recognizes primitives, String, enums, and classes with only val properties of stable types as stable.
A major trap in Android development involves standard collections like List or Map. Because Kotlin's List is technically a read-only interface that could be backed by a mutable ArrayList at runtime, the Compose compiler flags it as unstable. Consequently, any composable accepting a raw List cannot be skipped during parent recompositions.
To enable skipping, developers wrap collections inside @Immutable data classes, use Kotlinx Immutable Collections, or leverage strong skipping mode in modern Compose compilers.""",
    "deep_senior_en": """Under the hood, skipping behavior is governed by stability inference performed by the Compose Compiler plugin during compilation.
For each composable function, the compiler computes a stability summary for every parameter, assigning it $stable, $unstable, or $dynamic. In the generated bytecode, the compiler inserts change-tracking logic into the synthetic changed bitmask integer. Each parameter occupies 3 bits in the mask, representing states like SAME, DIFFERENT, UNCERTAIN, and STATIC.
When a parent composable recomposes, it evaluates the bitmask. If a parameter is marked unstable, the bitmask is forced to UNCERTAIN, forcing the child function body to execute.
If all parameters are stable and evaluate to SAME (or have STATIC references), the method executes an early return opcode, entirely skipping slot allocation and child tree reconciliation.
In modern Compose compilers (Compose Compiler 1.5.4+ and Kotlin 2.0+), Google introduced Strong Skipping Mode (enabled by default in Kotlin 2.0). Strong skipping relaxes classical stability rules: composables with unstable parameters become skippable if their runtime instances compare equal via instance equality (===) or structural equality (equals).
Furthermore, lambda memoization automatically wraps unstable lambda captures inside remember blocks, dramatically reducing unnecessary recompositions across enterprise Android codebases. Senior engineers inspect compiler metrics using the reportsDestination flag to audit unskippable composables and verify that critical screens achieve predictable, near-zero recomposition overhead.""",
    "meta_ar": {
        "id": "COM-03",
        "questionAr": "ما الذي يطلق إعادة التركيب (Recomposition Trigger)، وما هي الشاشات والدوال التي يمكن تخطيها (Skipping)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم محفزات الـ Recomposition (Snapshot State reads)، وشروط الـ Smart Skipping، واستيعاب مفهوم الـ Stability والأنواع غير المستقرة كالـ `List`، ودور ميزة Strong Skipping Mode في كوتلن 2.0.",
        "why_it_matters_ar": "عدم فهم استقرار الباراميترات يجعل الشاشات تعيد رندرة نفسها وقوائمها بالكامل مع كل لمسة أو حركة أنيميشن بسيطة، مما يؤدي لبطء شديد وتشنج الواجهة (Jank).",
        "worked_example_ar": "تأثير الـ Unstable List وعلاجها بـ `@Immutable`:\n```kotlin\n// غير قابل للتخطي: List تعتبر غير مستقرة دائمًا\n@Composable fun UserList(users: List<User>)\n// قابل للتخطي الذكي: تغليف القائمة بوعد عدم التعديل\n@Immutable data class UsersState(val users: List<User>)\n@Composable fun UserList(state: UsersState) // يُتخطى إذا لم يتغير!\n```",
        "trade_offs_ar": "تغليف القوائم بموديل `@Immutable` يضيف كلاسات صغيرة، لكنه يمنع آلاف عمليات الـ Recomposition غير الضرورية ويحافظ على أعلى سرعة استجابة للتطبيق.",
        "failure_modes_ar": "تمرير كلاسات تحتوي على متغيرات `var` أو استخدام `List` مباشرة مع الاعتقاد بأن كومبوز تتخطى الدالة تلقائياً لأن محتوى القائمة متطابق.",
        "production_perspective_ar": "في المشروعات الكبيرة، نعتمد على Kotlin 2.0 مع تفعيل Strong Skipping Mode افتراضياً، ونراجع تقارير Compose Compiler Metrics دورياً لضمان استقرار كل الـ Data Models.",
        "how_to_answer_ar": "وضح محفز الـ Recomposition: قراءة متغير State تغيرت قيمته داخل نطاق الدالة، واشرح شروط الـ Skipping: أن تكون كل الباراميترات Stable وقيمها متطابقة مع المرة السابقة، واشرح سبب عدم استقرار `List` التقليدية، واذكر حلولها بـ `@Immutable` أو `PersistentList` وميزة Strong Skipping في كوتلن الحديثة.",
        "talking_points_ar": "مفهوم State Reads و Snapshot System، والأنواع المستقرة مقابل غير المستقرة، ومأزق `List` في كوتلن، ومصفوفة الـ Changed Bitmask، و Strong Skipping Mode.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يعتبر مترجم كومبوز واجهة `List<T>` العادية غير مستقرة (Unstable)؟\"\n  **المرشح:** \"لأن `List` في كوتلن هي مجرد Read-only Interface قد يكون الكائن الفعلي في الذاكرة هو `ArrayList` قابل للتعديل بالخفاء بدون علم الكومبايلر، لذلك يتعامل معها بحذر ويعيد تشغيل الدالة دائماً.\"\n\n- **المحاور:** \"ما هو دور ميزة Strong Skipping Mode التي أصبحت افتراضية في كوتلن 2.0؟\"\n  **المرشح:** \"بتخلي كومبوز تتخطى الدوال حتى لو فيها باراميترات Unstable طالما الكائنات متطابقة بـ `equals()`، وبتحفظ الـ Lambdas بـ remember تلقائياً.\"",
        "self_check_ar": "هل حددت محفز إعادة التركيب بدقة؟ هل شرحت شروط التخطي؟ وهل بينت مشكلة List وحلها بمكتبات الـ Immutability و Strong Skipping؟",
        "references_ar": f"- [Jetpack Compose Stability Guide](https://developer.android.com/develop/ui/compose/performance/stability) — التوثيق الرسمي لاستقرار الأنواع في كومبوز.\n- [Compose Strong Skipping Mode](https://developer.android.com/develop/ui/compose/performance/stability/strongskipping) — دليل Strong Skipping الرسمي لجوجل.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ Recomposition بيحصل فقط لما دالة Composable تقرأ متغير من نوع Snapshot State وتتغير قيمته. أما التخطي (Skipping) فبيحصل لما تكون كل الباراميترات الممررة للدالة مستقرة (Stable) وقيمها متطابقة تماماً مع قيم المرة السابقة. الأنواع البدائية والنصوص والكلاسات التي تحتوي على `val` فقط والمميزة بـ `@Immutable` بتعتبر Stable. لكن القوائم العادية زي `List` بتعتبر غير مستقرة (Unstable)، وبتجبر كومبوز تعيد تشغيل الدالة في كل مرة، إلا إذا استخدمنا مكتبات كوتلن غير القابلة للتعديل أو فعلنا ميزة Strong Skipping Mode الحديثة.",
        "best_answer_ar": "فهم إمتى كومبوز بتعيد الرسم وإمتى بتتخطى الدوال هو الفارق الحقيقي بين تطبيق سلس بـ 60 فريم وتطبيق تقيل ومليان تهنيج.\n\nمحفز الـ Recomposition مش أي تغيير لمتغير عادي، بل هو حصرياً قراءة دالة الكومبوزابل لقيمة حالة متغيرة مدعومة بنظام الـ Snapshots (زي `mutableStateOf` أو `StateFlow` تم تحويله بـ `collectAsState`). أول ما القيمة دي تتغير، كومبوز بتعلم نطاق الدالة دي فقط إنه محتاج إعادة تشغيل.\n\nعشان كومبوز تقرر إنها تتخطى الدالة (Smart Skipping)، لازم كل الباراميترات الممررة للدالة ينطبق عليها شرط الاستقرار (Stability). المترجم بيعتبر النوع Stable لو قيمته غير قابلة للتغيير، أو لو بيبلغ كومبوز رسمياً لما يتغير. الأنواع الأساسية زي Int و String والدوال (Lambdas) مستقرة بطبيعتها.\n\nالمأزق الأكبر اللي بيقع فيه أغلب المطورين هو الـ Collections العادية زي `List<String>`. في كوتلن، `List` هي Read-only مش Immutable، وممكن كود في الخلفية يكون ممرر `ArrayList` ويعدل فيها بدون ما كومبوز تعرف، عشان كده الكومبايلر بيصنفها دايماً كـ Unstable، وده بيخلي أي شاشة بتستقبل List تعيد تشغيل نفسها باستمرار حتى لو البيانات هي هي!\n\nالحل في المشروعات الاحترافية هو تغليف القوائم في كلاس داتا مميز بـ `@Immutable`، أو استخدام مكتبة Kotlinx Immutable Collections (`ImmutableList`)، أو الاعتماد على ميزة Strong Skipping Mode في كوتلن 2.0 اللي بتعمل مقارنة بـ `equals()` وتتخطى الدوال بأمان.",
        "deep_answer_ar": "تحت الكابوت، عملية التخطي الذكي بتعتمد على فحص وتحليل الاستقرار (Stability Inference) اللي بيقوم بيه الـ Compose Compiler Plugin أثناء تجميع الكود في بايت كود.\n\nالكومبايلر بيمسك كل باراميتر في الدالة ويحلل تركيبه؛ لو كل حقوله `val` ومن أنواع مستقرة، بيعلم الدالة بإنها قابلة للتخطي (Skippable). في الكود المولد، بيتم فحص الباراميتر عبر مصفوفة أعلام البتات `changed`. كل باراميتر له 3 بتات بتمثل حالات زي SAME و DIFFERENT و UNCERTAIN. لما الدالة الأب تعيد التركيب، بتفحص الباراميترات؛ لو النوع Unstable، الكومبايلر بيجبر البتات تكون UNCERTAIN، وده بيمنع التخطي ويجبر الدالة على التنفيذ حتى لو القيم متطابقة.\n\nبينما لو النوع Stable والبتات قرأت SAME، الدالة بتنفذ تعليمة رجوع فورية في البايت كود (Return Opcode)، وده بيتخطى قراءة الـ SlotTable واستدعاء أي نودز فرعية في أجزاء من الميكروثانية.\n\nفي الإصدارات الحديثة من كومبوز مع كوتلن 2.0، جوجل غيرت قواعد اللعبة بميزة Strong Skipping Mode؛ الميزة دي خلت الدوال اللي بتستقبل أنواع Unstable قابلة للتخطي برضه بشرط إن كائنات الباراميتر تكون متطابقة بمقارنة الـ `equals()` العادية، وحولت كل الـ Lambdas لكائنات مميموزة (Memoized Lambdas) محاطة بـ `remember` تلقائياً بدون تدخل يدوي من المطور، وده رفع أداء شاشات كومبوز بشكل ثوري في المشاريع الضخمة."
    }
}

# ==========================================
# COM-04: What are state, snapshot state, and state hoisting?
# ==========================================
DATA["COM-04"] = {
    "concept_en": """State in Jetpack Compose represents any data value that can change over time and drive UI visual presentation. Snapshot State, implemented via MutableState<T> and mutableStateOf(), is Compose's observable reactive state primitive integrated into the multiversion concurrency control (MVCC) Snapshot system. When a composable reads a snapshot state during composition, Compose automatically registers a subscriber dependency on that state. State Hoisting is the foundational architectural pattern of moving state upward to a composable's caller to transform a tightly coupled stateful widget into an idempotent, highly reusable, and easily testable stateless component driven by values and events.""",
    "walkthrough_en": """Refactoring a stateful composable into a clean, hoisted stateless composable:
```kotlin
// ❌ ANTI-PATTERN: Stateful component owns its state, making it hard to test, preview, or reuse
@Composable
fun StatefulSearchInput() {
    var query by remember { mutableStateOf("") } // Tightly coupled internal state
    TextField(
        value = query,
        onValueChange = { query = it },
        placeholder = { Text("Search products...") }
    )
}

// ✅ ARCHITECTURAL BEST PRACTICE: State Hoisting (Stateless & decoupled)
// Separates state value (flows down) from event callbacks (flow up)
@Composable
fun StatelessSearchInput(
    query: String, // Value flows DOWN from parent
    onQueryChanged: (String) -> Unit, // Events flow UP to parent
    modifier: Modifier = Modifier
) {
    TextField(
        value = query,
        onValueChange = onQueryChanged,
        placeholder = { Text("Search products...") },
        modifier = modifier
    )
}

// Parent caller manages and hoists state cleanly (e.g. into ViewModel or Screen state holder)
@Composable
fun SearchScreen(viewModel: SearchViewModel) {
    val query by viewModel.searchQuery.collectAsStateWithLifecycle()
    StatelessSearchInput(query = query, onQueryChanged = viewModel::onQueryChanged)
}
```""",
    "short_en": """State is any value that drives the UI over time. Snapshot state, created via mutableStateOf(), is Compose's reactive state system that automatically tracks reads and schedules recomposition whenever written to. State Hoisting is the pattern of lifting state up to the caller, replacing internal state variables with a parameter for the current value and an event lambda for updates. Hoisting makes components stateless, highly reusable, previewable, and trivially testable in isolation.""",
    "structured_en": """State management and state hoisting are the foundational pillars of building robust Jetpack Compose architectures.
In declarative UI, the screen cannot be mutated directly; instead, the UI reacts to state mutations.
Snapshot state is Compose's custom reactive observation mechanism.
When you create state using mutableStateOf(), Compose wraps the value inside a State object integrated into the Snapshot system.
Whenever a composable reads that value during its execution, Compose transparently records that function scope as a subscriber.
When the state is subsequently written to on any thread, the Snapshot system notifies the runtime, scheduling recomposition specifically for the subscribing functions.
State Hoisting is the architectural design pattern used to decouple presentation from state ownership.
Instead of allowing a UI component like a text field or toggle button to maintain its own internal state, developers hoist the state up to the caller.
A hoisted component exposes two parameters: a value parameter representing the current state (flowing downward), and a callback lambda representing user-initiated events (flowing upward).
This pattern transforms components into stateless widgets that can be previewed seamlessly, reused in different screens, and tested purely using JVM unit tests without mock view hierarchies.""",
    "deep_senior_en": """Under the hood, Compose's Snapshot system is inspired by Multiversion Concurrency Control (MVCC), identical to transaction isolation models used in high-performance SQL databases.
When Compose begins a frame, it captures a global Snapshot. Every thread or coroutine reads an isolated, consistent snapshot of state variables without requiring synchronized mutex locks.
During the composition phase, Compose registers a ThreadLocal read observer. Every time StateObject.value is accessed, the observer records the StateRecord reference into the SlotTable for that specific RecomposeScope.
When a write operation occurs via StateObject.value = newValue, Compose records the mutation into the current snapshot and dispatches a global write notification to the SnapshotManager.
The SnapshotManager identifies all invalidated RecomposeScopes and marks their layout nodes dirty.
State Hoisting directly influences memory locality and recomposition scope granularity within this MVCC architecture.
If state is hoisted too high into a root screen composable, modifying a minor text counter can invalidate the entire screen hierarchy unless wrapped in isolated sub-composables.
Conversely, if state is not hoisted at all, state is lost during configuration changes and cannot be synchronized with domain repositories.
Staff engineers apply the Single Source of Truth rule: hoist transient UI state (like scroll offsets) to local state holders, and hoist business state (like shopping cart contents) into architecture ViewModels exposed as StateFlow.""",
    "meta_ar": {
        "id": "COM-04",
        "questionAr": "ما هي الحالة (State)، وحالة اللقطة (Snapshot State)، ونمط رفع الحالة (State Hoisting) في Compose؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم نظام الحالات في Compose، وآلية عمل Snapshot System المستوحاة من MVCC في قواعد البيانات، وإتقان نمط State Hoisting لتحويل المكونات إلى Stateless قابلة للاختبار والمعاينة.",
        "why_it_matters_ar": "الاحتفاظ بالحالة داخل المكونات الفرعية يجعلها مستحيلة في إعادة الاستخدام أو الاختبار، ويؤدي لفقدان البيانات مع تدوير الشاشة وصعوبة مزامنتها مع الـ ViewModel.",
        "worked_example_ar": "تطبيق State Hoisting لتحويل مكون البحث لـ Stateless:\n```kotlin\n// مكون نقي يستقبل القيمة ويبث الحدث للأعلى\n@Composable fun SearchBar(query: String, onQueryChange: (String) -> Unit) {\n    TextField(value = query, onValueChange = onQueryChange)\n}\n```",
        "trade_offs_ar": "رفع الحالة يتطلب تمرير باراميترز و Lambdas إضافية بين الدوال، لكنه يمنح فصلاً تاماً بين العرض ومنطق العمل ويجعل الواجهات قابلة لإعادة الاستخدام في أي شاشة.",
        "failure_modes_ar": "تخزين الحالة الحساسة داخل دوال Composable فرعية باستخدام `remember { mutableStateOf() }` مما يجعلها تنعزل عن الـ ViewModel وتفقد بياناتها عند تدوير الشاشة.",
        "production_perspective_ar": "في المشروعات الكبيرة، نعتمد قاعدة صارمة: مكونات الـ Design System المشتركة يجب أن تكون Stateless بنسبة 100%، والحالة ترفع دائماً إلى Screen-level State Holder أو الـ ViewModel.",
        "how_to_answer_ar": "عرف الـ State: البيانات التي تدير شكل الواجهة، وعرف الـ Snapshot State: نظام المراقبة التفاعلي القائم على MVCC الذي يسجل القراءات والكتابات، واشرح نمط State Hoisting: رفع الحالة للأعلى بحيث تستقبل الدالة القيمة وتطلق الأحداث كـ Lambdas، واذكر فوائده في الاختبار والمعاينة وإعادة الاستخدام.",
        "talking_points_ar": "مفهوم State في البرمجة التصريحية، وآلية عمل Snapshot System المستوحاة من MVCC، وقاعدة State goes down, events go up، وتحويل المكونات إلى Stateless.",
        "follow_ups_ar": "- **المحاور:** \"إلى أي مستوى يجب رفع الحالة (How high to hoist)?\"\n  **المرشح:** \"تُرفع الحالة إلى أدنى مستوى سلف مشترك (Lowest Common Ancestor) يحتاج لقراءة تلك الحالة أو تعديلها، لمنع إعادة تركيب أجزاء عليا غير معنية بالبيانات.\"\n\n- **المحاور:** \"كيف يتعامل نظام الـ Snapshots مع تعديل الحالة من خيوط معالجة متعددة (Background Threads)؟\"\n  **المرشح:** \"النظام مستوحى من MVCC؛ كل خيط يرى لقطة معزولة ومتسقة، والتعديل يتم بـ Atomic Commit يرسل إشعاراً مركزياً بتحديث الـ RecomposeScopes المتأثرة بأمان تام.\"",
        "self_check_ar": "هل عرفت المفاهيم الثلاثة بوضوح؟ هل شرحت مبدأ تدفق البيانات للأعلى وللأسفل؟ وهل بينت الأساس العميق لنظام الـ Snapshots؟",
        "references_ar": f"- [State and Jetpack Compose](https://developer.android.com/develop/ui/compose/state) — الدليل الرسمي لجوجل لإدارة الحالة في كومبوز.\n- [Compose State Hoisting Guide](https://developer.android.com/develop/ui/compose/state-hoisting) — الدليل الرسمي لنمط رفع الحالة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ State هي أي معلومة متغيرة بتحدد شكل واجهة المستخدم في لحظة معينة. الـ Snapshot State هو نظام المراقبة التفاعلي الخاص بكومبوز؛ لما بتعمل متغير بـ `mutableStateOf`، كومبوز بتسجل تلقائياً أي دالة بتقرأ المتغير ده، وأول ما يتعدل بتطلق الـ Recomposition للدوال المتأثرة فقط. أما نمط رفع الحالة (State Hoisting) فهو تكنيك معماري بننقل فيه إدارة الحالة من داخل المكون الصغير للأعلى عند الكود المنادي له، بحيث المكون يستقبل القيمة الحالية كـ Parameter ويبث الأحداث كـ Lambda للأعلى؛ وده بيحول المكون لـ Stateless سهل المعاينة وقابل لإعادة الاستخدام والاختبار بنسبة 100%.",
        "best_answer_ar": "إدارة الحالة في كومبوز بتعتمد على تلات مفاهيم مترابطة هي العمود الفقري لأي معمارية شاشات ناجحة.\n\nالمفهوم الأول هو الـ State؛ في النمط التصريحي، الواجهة مفيهاش أي كائنات بتتحكم في نفسها، بل هي مجرد شاشة عرض للبيانات المتغيرة مع الوقت.\n\nالمفهوم الثاني هو الـ Snapshot State؛ ده النظام التفاعلي اللي بنبنيه عبر `mutableStateOf()`. النظام ده شغال بطريقة مبهرة؛ أول ما دالة كومبوزابل تقرأ قيمة المتغير ده أثناء الرندرة، كومبوز بتسجل الدالة دي كمشترك (Subscriber). وفي اللحظة اللي بيتعدل فيها المتغير، الرنتايم بيعرف فوراً النطاق المتأثر ويطلب إعادة تشغيله بدون ما يلمس باقي الشاشة.\n\nالمفهوم الثالث والحيوي هو نمط رفع الحالة (State Hoisting).\nالمشكلة الكبرى في كود المبتدئين إنهم بيحطوا الحالة جوه المكون الصغير، زي زرار أو حقل بحث محتفظ بنصه جواه. ده بيخلي المكون 'محبوساً'؛ متقدرش تفتحه في الـ Previews بقيم مختلفة، وتدوير الشاشة بيمسح بياناته، ومستحيل توحده مع الـ ViewModel.\n\nالحل هو تطبيق State Hoisting بقاعدة: 'البيانات تتدفق للأسفل والأحداث تصعد للأعلى' (State goes down, events go up).\nبنسحب الحالة للأعلى في الـ ViewModel أو الشاشة الأم، والمكون الصغير بياخد قيمتين بس: قيمة يعرضها، و Lambda كولباك يطلقه لما المستخدم يضغط أو يكتب. بكده المكون بيتحول لـ Stateless Component نقي تقدر تستخدمه في 10 شاشات مختلفة وتختبره بسهولة على الـ JVM.",
        "deep_answer_ar": "تحت الكابوت، نظام الـ Snapshot State في كومبوز مستوحى مباشرة من نظرية التحكم في التزامن متعدد الإصدارات (Multiversion Concurrency Control - MVCC)، وهو نفس المبدأ الرياضي اللي بتعتمد عليه قواعد بيانات SQL الكبرى لعزل المعاملات.\n\nلما كومبوز بتبدأ تجهز إطار الرندرة، بتلتقط لقطة عامة (Global Snapshot). كل Thread بيقرأ نسخة معزولة ومتسقة من المتغيرات بدون الحاجة لعمل قفل متزامن (Mutex Lock) يعطل المعالج. الرنتايم بيستخدم `ThreadLocal` عشان يسجل قراءات الحالة؛ أول ما يتم قراءة `StateObject.value`، بيتم ربط الـ `StateRecord` بنطاق الـ `RecomposeScope` التابع للدالة في الـ SlotTable.\n\nولما يحصل تعديل في قيمة الحالة عبر `value = newValue`، التعديل بيتسجل كـ Atomic Transaction، ونظام الـ SnapshotManager بيبث إشعار كتابة عام بيعلم النطاقات المشتركة بأنها أصبحت غير صالحة، ويجدول إعادة تركيبها في الفريم القادم.\n\nهنا بتظهر الأهمية المعمارية العميقة لنمط الـ State Hoisting؛ لو رفعت الحالة بزيادة عن اللزوم عند الـ Root Composable، أي تعديل بسيط في حرف هيكتب في الـ TextField هيجبر الشاشة الكبيرة كلها على إعادة الحساب. بينما لو حصرت رفع الحالة عند أدنى سلف مشترك (Lowest Common Ancestor)، أو عزلت الحالة الحساسة في State Holders مخصصة، الـ Recomposition Scope هيفضل ضيق جداً ومحصور في النود المعنية، وده اللي بيمنع الـ Frame Drops ويضمن أعلى سرعة استجابة للتطبيق."
    }
}

# ==========================================
# COM-05: Compare remember, rememberSaveable, and ViewModel state.
# ==========================================
DATA["COM-05"] = {
    "concept_en": """In Jetpack Compose, state lifecycle management is divided across three distinct retention scopes: remember, rememberSaveable, and ViewModel state. remember retains state exclusively across recompositions within a single composition lifecycle, resetting whenever the composable leaves the tree or during configuration changes (such as screen rotation). rememberSaveable extends this by automatically persisting state into the Android SavedInstanceState bundle, surviving configuration changes and system-initiated process death for Parcelable or primitive data. ViewModel state provides the longest lifecycle, living across configuration changes and process death (via SavedStateHandle) while retaining business logic and surviving navigation backstack transitions.""",
    "walkthrough_en": """Contrasting the three state survival mechanisms in an Android screen:
```kotlin
@Composable
fun RegistrationScreen(viewModel: RegistrationViewModel = hiltViewModel()) {
    // 1. remember: Survives recomposition ONLY. Resets on screen rotation!
    // Best for: Ephemeral animation flags, scroll states, local UI toggles
    var isPasswordVisible by remember { mutableStateOf(false) }

    // 2. rememberSaveable: Survives recomposition AND configuration changes AND process death!
    // Best for: User draft inputs, expanded card states, temporary form values
    var enteredUsername by rememberSaveable { mutableStateOf("") }

    // 3. ViewModel State: Survives recomposition, configuration changes, and navigation graph transitions!
    // Best for: Business domain data, async network states, multi-repository orchestration
    val registrationState by viewModel.uiState.collectAsStateWithLifecycle()

    RegistrationContent(
        username = enteredUsername,
        onUsernameChange = { enteredUsername = it },
        isPasswordVisible = isPasswordVisible,
        onTogglePassword = { isPasswordVisible = !isPasswordVisible },
        state = registrationState
    )
}
```""",
    "short_en": """remember retains state across recompositions, but completely resets on screen rotation or when leaving the composition. rememberSaveable survives recompositions, configuration changes, and process death by saving state into the Android SavedStateRegistry bundle using Parcelize or custom Savers. ViewModel state lives completely outside the composition lifecycle, surviving screen rotations and maintaining business data across screen transitions, backed by SavedStateHandle for process death restoration.""",
    "structured_en": """Choosing the correct state persistence mechanism in Jetpack Compose requires understanding their lifecycles, storage mediums, and architectural scopes.
remember is the most localized and ephemeral mechanism. It stores a value in the Compose SlotTable at the call site. The value persists across recompositions as long as the composable remains in the composition tree. However, because it resides purely in memory tied to the Activity window, it is wiped out during configuration changes like screen rotations. It is ideal for transient UI effects, like animation toggles or temporary dropdown expansions.
rememberSaveable builds upon remember by registering the value with the Android Activity's SavedStateRegistry. Upon configuration change or system process death, Compose bundles the value into the saved instance state, restoring it when the screen recreates. Values must be primitives, Bundle-compatible, or implement Parcelable. It is ideal for user form inputs and draft text.
ViewModel state represents the highest tier of architecture. ViewModels survive configuration changes natively through Android Architecture Components, living until the backstack entry is popped. They are decoupled from Android UI classes, can be tested purely on the JVM, and interact with Domain UseCases. Backed by SavedStateHandle, ViewModel state survives process death, making it the required home for all business-critical domain data.""",
    "deep_senior_en": """Under the hood, these three mechanisms map to fundamentally distinct memory structures and lifecycle registries within the Android operating system.
remember allocates a slot directly within the current Composer's SlotTable array. During recomposition, Compose reads the slot at the matching code offset. When the Activity recreates due to an orientation change, the entire ComposeView and its associated SlotTable are garbage collected, explaining why remember immediately loses state.
rememberSaveable bridges Compose to the platform SavedStateRegistryOwner (typically the ComponentActivity or NavBackStackEntry). It utilizes a Saver implementation (auto-inferred or explicitly provided via listSaver or mapSaver) to serialize the value into a platform Bundle before Android's onSaveInstanceState() fires.
Because Bundles are marshaled across the Binder IPC boundary to the OS system_server process during process death, rememberSaveable enforces strict size limits: storing massive lists or Bitmaps here triggers TransactionTooLargeException crashes.
ViewModel state resides in the ViewModelStoreOwner, maintained by the non-configuration instance mechanism in the platform. The ViewModel instance itself remains intact in heap memory across Activity destruction and recreation, eliminating serialization overhead for domain models.
For process death resilience, ViewModels inject SavedStateHandle, which internally hooks into the exact same SavedStateRegistry as rememberSaveable.
Senior architects maintain strict separation of concerns: remember handles transient UI mechanics, rememberSaveable handles screen-level form inputs, and ViewModel state drives core business domain workflows.""",
    "meta_ar": {
        "id": "COM-05",
        "questionAr": "قارن بين remember و rememberSaveable وإدارة الحالة في الـ ViewModel.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على اختيار آلية إدارة الحالة المناسبة في أندرويد، وفهم دورة حياة كل آلية، والتعامل مع تدوير الشاشة وموت العملية بـ Process Death، وتجنب خطأ TransactionTooLargeException.",
        "why_it_matters_ar": "الاعتماد الخاطئ على `remember` للبيانات الحساسة يؤدي لفقدان ما كتبه المستخدم عند تدوير الشاشة، بينما وضع بيانات ضخمة في `rememberSaveable` يسبب انهيار التطبيق بسبب حجم الـ Bundle.",
        "worked_example_ar": "استخدام الآليات الثلاث في شاشة تسجيل:\n```kotlin\n// 1. remember: حالة بصرية مؤقتة (تضيع مع التدوير)\nvar showPass by remember { mutableStateOf(false) }\n// 2. rememberSaveable: مسودة إدخال (تعيش مع التدوير وموت التطبيق)\nvar emailDraft by rememberSaveable { mutableStateOf(\"\") }\n// 3. ViewModel: منطق العمل وبيانات السيرفر\nval uiState by viewModel.state.collectAsStateWithLifecycle()\n```",
        "trade_offs_ar": "`remember` خفيف جداً لكنه زائل، `rememberSaveable` يعيش مع التدوير لكنه مقيد بحجم الـ Bundle والتسلسل، والـ `ViewModel` يدير منطق العمل ويعيش طوال وجود الشاشة في الـ Backstack.",
        "failure_modes_ar": "تخزين حقول إدخال المستخدم بـ `remember` فقط فتضيع عند تدوير الهاتف، أو حفظ قائمة منتجات كاملة في `rememberSaveable` فتنهار بـ `TransactionTooLargeException`.",
        "production_perspective_ar": "في تطبيقات الإنتاج، كل بيانات البيزنس والشبكة تعيش في الـ ViewModel مدعومة بـ `SavedStateHandle`، بينما نستخدم `rememberSaveable` لحقول الإدخال غير المحفوظة، و `remember` للأنيميشن والواجهة فقط.",
        "how_to_answer_ar": "قارن من حيث دورة الحياة والهدف: `remember` يعيش فقط أثناء الـ Recomposition ويضيع مع تدوير الشاشة، `rememberSaveable` يعيش مع تدوير الشاشة وموت التطبيق بحفظه في Bundle، والـ `ViewModel` يعيش طالما الشاشة في الـ Backstack ويدير منطق العمل المستقل عن الـ UI، ووضح حدود حجم البيانات في SavedState.",
        "talking_points_ar": "دورة حياة كل أداة، ومصير البيانات مع Configuration Change و Process Death، وآلية الـ Saver في rememberSaveable، ومخاطر TransactionTooLargeException.",
        "follow_ups_ar": "- **المحاور:** \"كيف تحفظ كائناً مخصصاً (Custom Object) في rememberSaveable؟\"\n  **المرشح:** \"إما بتمييز الكلاس بـ `@Parcelize` وتطبيق `Parcelable`، أو بكتابة كائن `Saver` مخصص باستخدام `mapSaver` أو `listSaver` لتحديد كيفية حفظ واسترجاع الحقول.\"\n\n- **المحاور:** \"ما هو الخطر الأكبر لتخزين بيانات كبيرة في rememberSaveable؟\"\n  **المرشح:** \"بيانات الـ SavedState بتتبعت عبر الـ IPC للـ OS في Bundle، والحد الأقصى للـ Binder Buffer هو 1MB للتطبيق بالكامل، فتخزين بيانات كبيرة بيسبب كراش فوري بـ `TransactionTooLargeException`.\"",
        "self_check_ar": "هل قارنت بين الآليات الثلاث بدقة؟ هل شرحت أثر تدوير الشاشة وموت العملية؟ وهل حذرت من خطأ حجم الـ Bundle؟",
        "references_ar": f"- [State in Jetpack Compose](https://developer.android.com/develop/ui/compose/state#restore-ui-state) — الدليل الرسمي لجوجل لحفظ واستعادة الحالة.\n- [Save UI state in Android](https://developer.android.com/topic/libraries/architecture/saving-states) — دليل جوجل الشامل لحفظ حالة التطبيق.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الفرق الجوهري بين التلاتة هو مدة بقاء البيانات (Lifecycle) والهدف منها: كود `remember` بيحتفظ بالقيمة أثناء الـ Recomposition فقط، لكنه بيموت فوراً مع تدوير الشاشة (Screen Rotation) أو الخروج من الشاشة؛ فبنستخدمه للحالات البصرية المؤقتة زي فتح وإغلاق القوائم. أما `rememberSaveable` فبيعيش أثناء الـ Recomposition وكمان بيعيش مع تدوير الشاشة وموت التطبيق في الخلفية (Process Death) لأنه بيحفظ البيانات في Bundle؛ فبنستخدمه لحفظ مسودات حقول الإدخال. بينما الـ `ViewModel State` بيعيش في طبقة مستقلة تماماً عن دورة حياة الواجهة، وبيحتفظ ببيانات العمل واستجابات السيرفر عبر تدوير الشاشة والتنقل في الـ Backstack.",
        "best_answer_ar": "اختيار المكان الصح لحفظ الحالة في كومبوز هو اللي بيحدد استقرار التطبيق وتجربة المستخدم وقت تدوير الجهاز أو إغلاق التطبيق في الخلفية.\n\nالأداة الأولى: `remember`.\nدي أبسط وأخف أداة؛ بتخزن القيمة في الـ SlotTable داخل الذاكرة المؤقتة للـ Composable. القيمة بتفضل عايشة طالما بنعمل Recomposition، لكن أول ما المستخدم يدور الموبايل من عمودي لأفقي، الـ Activity كلها بتتدمر والـ SlotTable بيتمسح، فالقيمة بترجع للصفر. بنستخدمها فقط للأمور البصرية الزائلة زي تشغيل أنيميشن، أو مؤشر إظهار وإخفاء الباسورد.\n\nالأداة الثانية: `rememberSaveable`.\nدي مبنية فوق `remember` لكنها بتسجل البيانات في الـ `SavedStateRegistry` بتاع أندرويد. لما يحصل تدوير للشاشة أو النظام يقتل التطبيق عشان يوفر رام، كومبوز بتحول المتغير لـ Bundle وترجعه تاني أول ما الشاشة تفتح. دي المكان المثالي لمسودات المستخدم زي النص اللي بيكتبه في حقل البحث قبل ما يدوس إرسال، وبشرط البيانات تكون أنواع بسيطة أو كلاسات `@Parcelize`.\n\nالأداة الثالثة: `ViewModel State`.\nده المستوى المعماري الأعلى؛ الـ ViewModel بيعيش خارج شجرة كومبوز تماماً في الـ `ViewModelStore`، وبيفضل حي طول ما الشاشة موجودة في الـ Backstack. هو الموطن الإجباري لمنطق العمل (Business Logic)، وجلب البيانات من الـ Repositories، وتجهيز الـ UI State عبر `StateFlow`. وللنجاة من موت التطبيق بـ Process Death، بنحقن جواه `SavedStateHandle`.\n\nالمهندس المحترف بيحط منطق العمل في الـ ViewModel، ومدخلات الشاشة في `rememberSaveable`، والحركات البصرية في `remember`.",
        "deep_answer_ar": "تحت الكابوت، الأدوات التلاتة بتتعامل مع مستويات مختلفة كلياً من الذاكرة ونظام تشغيل أندرويد.\n\nكود `remember` بيحجز مجرد Slot داخل مصفوفة الـ SlotTable التابعة للـ Composer. أثناء الـ Recomposition، المؤشر بيقرأ القيمة المخزنة في نفس الـ Code Offset. مع تدوير الشاشة، بيئة الـ Window بتتدمر والـ ComposeView بالكامل بيتجمع بواسطة الـ Garbage Collector، وده سبب الفقدان الفوري للحالة.\n\nأما `rememberSaveable` فبيعمل Bridge بين كومبوز ونظام أندرويد القديم عبر `SavedStateRegistryOwner`. بيستخدم كائن `Saver` لتسلسل (Serialize) القيمة وتحويلها لـ Android OS Bundle قبل استدعاء `onSaveInstanceState`. هنا تكمن نقطة خطيرة يسأل عنها كبار المهندسين: بيانات الـ Bundle بتتبعت عبر الـ Binder IPC إلى الـ `system_server` في نظام أندرويد، ومساحة الـ Transaction Buffer المسموحة للتطبيق بالكامل هي 1 ميجابايت فقط؛ فلو مطور حفظ قائمة كبيرة من المنتجات في `rememberSaveable`، التطبيق هينهار فوراً بكراش شهير `TransactionTooLargeException`.\n\nبينما حالة الـ `ViewModel` مفيهاش خطر الـ IPC ده أثناء تدوير الشاشة؛ لأن الـ ViewModel نفسه بيفضل كائن سليم وحي في الـ Heap Memory بفضل آلية `NonConfigurationInstances` في نظام أندرويد، وبالتالي مفيش أي كلفة Serialization. وللتعامل مع الـ Process Death، الـ ViewModel بيستخدم `SavedStateHandle` اللي بدوره بيشترك في نفس الـ SavedStateRegistry لتسجيل المعرفات والمفاتيح الأساسية فقط (IDs and Keys) بأمان تام."
    }
}

# ==========================================
# COM-06: What is Unidirectional Data Flow in Compose?
# ==========================================
DATA["COM-06"] = {
    "concept_en": """Unidirectional Data Flow (UDF) is an architectural UI design pattern where state flows strictly downward through the composable hierarchy, while user-initiated events flow strictly upward to state holders. In Jetpack Compose, UDF transforms UI trees into pure, predictable display layers. A parent composable or ViewModel acts as the single source of truth, emitting immutable state data classes to child composables. In turn, child composables capture user gestures (clicks, text input, swipes) and notify the parent via lambda callbacks without directly mutating any state variables, establishing a deterministic, circular state lifecycle.""",
    "walkthrough_en": """Implementing pure Unidirectional Data Flow (UDF) in a Jetpack Compose screen:
```kotlin
// 1. Immutable State representation (Flows DOWN)
data class TaskUiState(
    val title: String = "",
    val isCompleted: Boolean = false,
    val isSubmitting: Boolean = false
)

// 2. Sealed Interface for Events (Flows UP)
sealed interface TaskUiEvent {
    data class TitleChanged(val newTitle: String) : TaskUiEvent
    data object ToggleCompletion : TaskUiEvent
    data object SubmitTask : TaskUiEvent
}

// 3. Stateless Composable adhering to UDF: State DOWN, Events UP
@Composable
fun TaskScreenContent(
    state: TaskUiState, // State flows DOWN
    onEvent: (TaskUiEvent) -> Unit, // Events flow UP
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier.padding(16.dp)) {
        TextField(
            value = state.title,
            onValueChange = { onEvent(TaskUiEvent.TitleChanged(it)) }
        )
        Row(verticalAlignment = Alignment.CenterVertically) {
            Checkbox(
                checked = state.isCompleted,
                onCheckedChange = { onEvent(TaskUiEvent.ToggleCompletion) }
            )
            Text("Mark as completed")
        }
        Button(
            onClick = { onEvent(TaskUiEvent.SubmitTask) },
            enabled = !state.isSubmitting
        ) {
            Text("Save Task")
        }
    }
}
```""",
    "short_en": """Unidirectional Data Flow is an architectural pattern where state flows down through parameters and events flow up through callbacks. In Compose, a ViewModel or parent component holds the single source of truth and passes immutable state snapshots down to child composables. Child composables never mutate state directly; when users tap or type, they emit event lambdas up to the state holder, which processes business rules and emits a new state snapshot, guaranteeing predictability and zero synchronization bugs.""",
    "structured_en": """Unidirectional Data Flow is the foundational design pattern that makes Jetpack Compose predictable, modular, and resilient against state bugs.
In legacy Android architectures, bidirectional data flow caused widespread bugs: a custom View modified its own internal state, fired a callback, and simultaneously listened for external updates. This two-way binding frequently created infinite loop feedback cycles and desynchronized views.
UDF resolves this by enforcing a single, non-negotiable direction of data propagation.
First, state flows exclusively downwards. A parent state holder (such as an Android ViewModel) encapsulates the business state and exposes an immutable state model, typically as a StateFlow collected as state. Child composables receive this state as immutable parameters and project it visually.
Second, events flow exclusively upwards. Child composables are completely decoupled from state mutation logic. When a user interacts with a widget—tapping a button, typing in a field, or swiping a card—the composable invokes an event callback lambda.
The state holder receives the event, executes business validation, interacts with repositories, and generates a new immutable state instance.
This new state flows down, triggering a controlled recomposition pass.""",
    "deep_senior_en": """Under the hood, Unidirectional Data Flow harmonizes perfectly with the Compose Compiler's smart recomposition algorithms and reactive Snapshot system.
When state flows downwards as immutable data classes, the Compose runtime can exploit referential equality and structural equality checks across RecomposeScopes. If a child composable observes that its incoming state instance is equal to its previous composition state, the Compose runtime invokes its early-return optimization, skipping execution of that entire UI subtree.
If child composables were allowed to mutate state directly or read ambient mutable variables, the Snapshot system would detect inconsistent state writes during active read phases. This produces state race conditions, breaks the determinism of the SlotTable, and triggers recomposition loops where modifying state during composition causes continuous invalidations on every frame.
Furthermore, UDF dramatically simplifies unit and screenshot testing.
Because UI content composables are stateless consumers of state that emit events via lambdas, engineers test complex screens on the standard JVM without spinning up Android Activities or mock ViewModels. A unit test simply passes an arbitrary state instance into the composable and verifies that clicking a button triggers the expected event lambda callback with the correct payload. Additionally, this architectural decoupling allows production teams to record, serialize, and replay UI event streams deterministically, accelerating defect reproduction and telemetry auditing across complex enterprise applications.""",
    "meta_ar": {
        "id": "COM-06",
        "questionAr": "ما هو تدفق البيانات أحادي الاتجاه (Unidirectional Data Flow - UDF) في Compose؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم نمط معمارية UDF، وقاعدة State goes down, events go up، والقدرة على فصل الحالة عن الأحداث، وإدراك دور النمط في منع حلقات الـ Recomposition اللانهائية وتسهيل الاختبارات.",
        "why_it_matters_ar": "التدفق ثنائي الاتجاه (Two-way binding) كان السبب الأكبر في انهيار الشاشات القديمة وحلقات التحديث اللانهائية، بينما UDF يجعل تدفق البيانات خطياً وقابلاً للتتبع والتنبؤ بنسبة 100%.",
        "worked_example_ar": "تطبيق UDF بفصل الحالة والحدث:\n```kotlin\n// الحالة تتدفق للأسفل والأحداث تصعد للأعلى\n@Composable fun Screen(state: UiState, onAction: (UserAction) -> Unit) {\n    Button(onClick = { onAction(UserAction.Submit) }) { Text(state.title) }\n}\n```",
        "trade_offs_ar": "يتطلب كتابة كلاسات للأحداث (Sealed Interfaces) وتمرير كولباكات للأعلى، لكنه يمنح استقراراً كاملاً ويمنع تضارب الحالات ويسهل اختبار الواجهة بمعزل عن منطق العمل.",
        "failure_modes_ar": "تعديل الحالة من داخل الكومبوزابل الفرعي مباشرة أثناء مرحلة التكوين، مما يسبب Recomposition Loop تشنق التطبيق تماماً.",
        "production_perspective_ar": "في المشروعات الكبيرة، نعتمد معمارية MVI أو MVVM بنمط UDF الصارم، حيث يتعامل الـ ViewModel مع أحداث `UiEvent` ويبث `UiState` واحدة مجمعة وغير قابلة للتعديل.",
        "how_to_answer_ar": "عرف UDF بالقاعدة الذهبية: الحالة تتدفق للأسفل كبيانات غير قابلة للتعديل (State flows down) والأحداث تصعد للأعلى كـ Lambdas أو Sealed Events (Events flow up)، واشرح كيف يمنع التضارب وحلقات التحديث اللانهائية، وبين فائدته في الـ Skipping الذكي واختبارات الشاشات.",
        "talking_points_ar": "قاعدة State Down / Events Up، ومشاكل Two-way Data Binding القديمة، وتجنب Recomposition Loops، وتسهيل اختبارات الـ Screenshot والـ Unit Tests.",
        "follow_ups_ar": "- **المحاور:** \"كيف يحمي نمط UDF شاشات كومبوز من حلقات التحديث اللانهائية (Infinite Recomposition Loops)؟\"\n  **المرشح:** \"لأن الكومبوزابل مبيعدلش الـ State مباشرة داخل جسمه؛ التعديل بيتم خارج مرحلة الرسم في الـ ViewModel استجابة لحدث، فيتم إنتاج State جديدة تطلق Recomposition نظيف ومحكوم.\"\n\n- **المحاور:** \"هل يفضل تمرير كل حدث كـ Lambda مستقل أم تجميع الأحداث في Sealed Interface؟\"\n  **المرشح:** \"في الشاشات الصغيرة تمرير Lambdas فردية ممتاز وخفيف، لكن في الشاشات الكبيرة تجميع الأحداث في `UiEvent` sealed interface بيقلل عدد الباراميترات ويسهل التوسع واختبار تفاعلات الشاشة.\"",
        "self_check_ar": "هل شرحت قاعدة التدفق بوضوح؟ هل بينت عيوب التدفق ثنائي الاتجاه؟ وهل وضحت الفائدة على اختبارات التطبيق واستقرار الرندرة؟",
        "references_ar": f"- [Android Architecture: UDF Pattern](https://developer.android.com/topic/architecture/ui-layer#udf) — الدليل الرسمي لجوجل لنمط تدفق البيانات أحادي الاتجاه.\n- [Compose Mental Model: State and Events](https://developer.android.com/develop/ui/compose/mental-model) — النموذج الذهني لكومبوز.",
        "quick_answer_ar": "تدفق البيانات أحادي الاتجاه (UDF) هو نمط معماري صارم بينص على إن الحالة والبيانات بتتدفق في اتجاه واحد فقط للأسفل (State flows down)، بينما الأحداث وتفاعلات المستخدم بتصعد في الاتجاه المعاكس للأعلى (Events flow up). في كومبوز، الـ ViewModel هو مصدر الحقيقة الوحيد (Single Source of Truth)؛ بيبعت كائن حالة غير قابل للتعديل (Immutable State) للشاشات لتعرضه، ولما المستخدم يدوس زرار أو يكتب، الشاشة بتطلق Lambda أو حدث للأعلى عشان الـ ViewModel يعالجه وينتج حالة جديدة، بدون ما الشاشة تعدل أي بيانات بنفسها.",
        "best_answer_ar": "نمط تدفق البيانات أحادي الاتجاه (Unidirectional Data Flow) هو سر الاستقرار والقدرة على التنبؤ بسلوك الشاشات في Jetpack Compose.\n\nفي معماريات أندرويد القديمة بنظام الـ Two-way Binding، كان الـ View بيعدل حالته الداخلية ويبعت كولباك، وفي نفس الوقت الـ Controller بيعدل الـ View من بره. الحركة دي كانت بتخلق كوابيس معمارية وحلقات مفرغة من التحديثات المستمرة (Feedback Loops)، وصعوبة بالغة في معرفة مين بالظبط اللي غير البيانات دي وتسبب في الـ Bug.\n\nكومبوز حسمت الموضوع ده بنمط UDF القائم على ركيزتين:\nالركيزة الأولى: البيانات تهبط للأسفل (State Flows Down)؛ الشاشة بتستقبل كائن داتا كلاس غير قابل للتعديل بيعبر بدقة عن كل ما يُعرض على الشاشة، زي نصوص الحقول وحالة التحميل ولون الزرار.\nالركيزة الثانية: الأحداث تصعد للأعلى (Events Flow Up)؛ المكونات الفرعية معندهاش أي صلاحية لتعديل البيانات. لما المستخدم يضغط كليك، المكون بيطلق Lambda للأعلى للـ ViewModel. الـ ViewModel يطبق قواعد العمل، يكلم السيرفر، وينتج نسخة حالة جديدة تماماً.\n\nالنتيجة إن دورة حياة البيانات بتتحول لدائرة مغلقة واضحة ومستقرة، مفيهاش أي تضارب، وبتخلي تتبع الأخطاء سهلاً جداً في الـ Logs.",
        "deep_answer_ar": "تحت الكابوت، نمط UDF متناغم تماماً مع طبيعة عمل خوارزميات الـ Recomposition ونظام الـ Snapshots في مترجم كومبوز.\n\nلما البيانات تتدفق للأسفل على شكل Immutable Data Classes، محرك كومبوز بيقدر يستفيد بأقصى درجة من ميزة الـ Smart Skipping؛ بيفحص تطابق كائن الحالة الجديد مع القديم بـ `equals()`، فلو متطابقين، الرنتايم بيعمل Early Return ويتخطى رندرة الشجرة بالكامل بدون استهلاك معالج أو ذاكرة. لو سمحنا للكومبوزابل إنه يعدل الحالة داخلياً أثناء تشغيل الدالة، نظام الـ Snapshot هيسجل عمليات كتابة أثناء مرحلة القراءة، وده هيطلق استدعاء فوري لـ Recomposition تاني لنفس الدالة، ويوقع التطبيق في حلقة مفرغة لانهائية (Infinite Recomposition Loop) تسحب البطارية وتشنق الشاشة في ثوانٍ.\n\nوفوق كده، نمط UDF بيغير قواعد هندسة الاختبارات المؤتمتة تماماً.\nلأن شاشات الكومبوز أصبحت Stateless بتستقبل State كـ Data Class وبتطلق Events كـ Lambdas، بنقدر نختبر أعقد الشاشات على الـ JVM العادي بـ Unit Tests أو نعمل لها Screenshot Tests بدون الحاجة لتشغيل محاكي وبدون ما نعمل Mocking لـ ViewModels أو قنوات أندرويد، وده بيضمن أعلى سرعة وموثوقية في دورة الـ CI/CD.\n\nعلاوة على ذلك، هذا الفصل المعماري التام بيسمح بتسجيل كل أحداث المستخدم وإعادة تشغيلها بشكل متطابق أثناء تتبع الأخطاء المعقدة، وبيمكّن الفرق الهندسية من بناء معمارية تسجيل تاريخي توفر ساعات من محاولات إعادة إنتاج المشاكل النادرة في بيئة الإنتاج."
    }
}

# ==========================================
# COM-07: What does Modifier do, and why does ordering matter?
# ==========================================
DATA["COM-07"] = {
    "concept_en": """A Modifier in Jetpack Compose is an immutable, ordered collection of modifier elements that decorates, sizes, positions, or adds interactive behavior to a composable layout node. Modifiers act as the unified mechanism replacing legacy XML view attributes, layout parameters, padding, margins, touch listeners, and accessibility tags. Modifier ordering matters critically because modifiers are chained sequentially and executed from left to right (outer to inner). Each modifier wraps the previous one like an onion layer, directly altering the measurement constraints, touch dispatch boundaries, and draw phases passed down to subsequent elements.""",
    "walkthrough_en": """Demonstrating how modifier chaining order fundamentally alters visual layout and touch boundaries:
```kotlin
// SCENARIO 1: Click and Background applied AFTER padding
// Padding creates outer whitespace; background and click apply ONLY to the inner 100dp area!
@Composable
fun InnerClickableBox() {
    Box(
        modifier = Modifier
            .padding(24.dp) // Outer margin/spacing
            .background(Color.Blue) // Background covers inner area
            .clickable { /* Tap registered only inside blue box */ }
            .size(100.dp)
    )
}

// SCENARIO 2: Click and Background applied BEFORE padding
// Background and click cover the full outer area; padding creates internal inset content spacing!
@Composable
fun FullClickableBox() {
    Box(
        modifier = Modifier
            .background(Color.Blue) // Background covers the ENTIRE box
            .clickable { /* Tap registered on the ENTIRE box including padded area! */ }
            .padding(24.dp) // Internal content inset
            .size(100.dp)
    )
}
```""",
    "short_en": """A Modifier decorates and configures a composable, controlling its dimensions, background, padding, clicks, and gestures. Ordering matters strictly because modifiers are evaluated sequentially from outer to inner. Applying padding before background creates an outer margin where the background is excluded. Applying background before padding covers the entire area and creates an internal content inset. Similarly, placing clickable before or after padding changes the actual touch target boundary.""",
    "structured_en": """Modifiers are the universal configuration mechanism in Jetpack Compose, consolidating what used to be layout params, view properties, and touch listeners in the legacy View system.
A Modifier is a chained fluent interface where each method call appends a modifier node to a linked list.
The order of modifier invocations is fundamentally consequential.
Because Compose wraps layout nodes sequentially, the first modifier acts on the outermost container, and each subsequent modifier applies to the enclosed inner layout.
The classic demonstration is the interaction between padding, background, and clickability.
If you apply .padding(16.dp) followed by .background(Color.Green), the padding behaves like an outer margin: the layout reserves 16dp of empty space around the composable, and only the inner content receives the green fill.
Conversely, if you apply .background(Color.Green) followed by .padding(16.dp), the entire composable is painted green, and the padding behaves like an internal content inset.
The same ordering logic governs gesture detection: placing .clickable before padding makes the entire bounding box interactive, whereas placing .clickable after padding restricts the touch target strictly to the inner content.""",
    "deep_senior_en": """Under the hood, Modifiers in modern Compose (Compose 1.3+ and the Modifier.Node architecture) are compiled into a doubly-linked list of Modifier.Node instances attached directly to the underlying LayoutNode.
In the legacy experimental Compose engine, modifier chains were composed via Modifier.composed {}, which allocated expensive Composable state holders inside the SlotTable for every modifier call, causing significant memory bloat.
The modern Modifier.Node architecture eliminates this overhead by creating lightweight, persistent C++-style nodes that participate directly in layout measurement (LayoutModifierNode), drawing (DrawModifierNode), and pointer input (PointerInputModifierNode).
When layout passes execute, Compose traverses the Modifier.Node chain in a strict directional order.
During the measurement phase, constraints flow forward (from the first modifier down to the last). The first modifier (such as a size or padding constraint) restricts the maximum and minimum width/height available to subsequent modifiers in the chain.
During the drawing phase, draw operations execute from the first modifier inwards, ensuring backgrounds paint behind content.
During hit testing, touch coordinates traverse the chain, and the first PointerInputModifierNode encountered on the path intercepts or delegates pointer events.
Understanding this bidirectional layout pipeline prevents subtle layout bugs and eliminates redundant modifier allocations. By writing custom modifiers directly extending Modifier.Node rather than relying on composed blocks, engineers achieve near-native layout performance and eliminate hidden recomposition overhead across high-frequency animations.""",
    "meta_ar": {
        "id": "COM-07",
        "questionAr": "ما الذي يفعله الـ Modifier في Compose؟ ولماذا يُعتبر ترتيب تطبيقه (Ordering) حاسماً؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم دور الـ Modifier في كومبوز، وإدراك كيف يؤثر الترتيب على مساحة الرسم ومساحة اللمس (Touch Target) وهوامش الحشو، واستيعاب المعمارية الحديثة لـ Modifier.Node وسريان الـ Constraints.",
        "why_it_matters_ar": "الخطأ في ترتيب الـ Modifiers يؤدي لتشوهات بصرية في الواجهة (كالخلط بين الـ Margin والـ Padding) أو يجعل الأزرار غير قابلة للنقر في أجزائها المفرغة.",
        "worked_example_ar": "تأثير الترتيب على مساحة الخلفية والنقر:\n```kotlin\n// الترتيب 1: الـ padding يعمل كـ Margin خارجي لا تصله الخلفية ولا النقر\nModifier.padding(16.dp).background(Color.Red).clickable { }\n// الترتيب 2: الـ padding يعمل كـ Inset داخلي والخلفية والنقر يشملان المساحة كلها\nModifier.background(Color.Red).clickable { }.padding(16.dp)\n```",
        "trade_offs_ar": "الـ Modifiers توفر نظاماً موحداً وقوياً، لكنها تتطلب وعياً هندسياً بكيفية سريان القيود (Constraints) لتجنب أخطاء القياس العشوائي.",
        "failure_modes_ar": "وضع `clickable` بعد `padding` ثم الشكوى من صعوبة النقر على الزرار لأن مساحة اللمس أصبحت أصغر من الحجم الموصى به للمتانة وسهولة الوصول (Accessibility).",
        "production_perspective_ar": "في المشروعات الكبيرة، نلزم المطورين بتمرير `modifier: Modifier = Modifier` كأول باراميتر اختياري في كل Composable لتمكين الشاشات الأعلى من ضبط التموضع، ونعتمد معايير Design System موحدة.",
        "how_to_answer_ar": "عرف الـ Modifier: أداة موحدة لضبط الحجم والخلفيات واللمس والتموضع، واشرح لماذا الترتيب حاسم: لأن السلسلة تُنفذ بترتيب خطي من الخارج للداخل كطبقات البصلة، واضرب المثال الكلاسيكي للفرق بين وضع `padding` قبل أو بعد `background` و `clickable`، واذكر معمارية Modifier.Node الحديثة.",
        "talking_points_ar": "مفهوم Modifier Chaining، والفرق بين Margin و Padding بالترتيب، ومساحة اللمس (Touch Boundaries)، ومعمارية Modifier.Node، وسريان القيود (Constraints).",
        "follow_ups_ar": "- **المحاور:** \"لماذا لا يوجد مفهوم Margin منفصل في Jetpack Compose مثل XML القديم؟\"\n  **المرشح:** \"لأن كومبوز حلتها بعبقرية عبر ترتيب الـ `padding`؛ فلو وضعت الـ padding قبل الـ background بيشتغل كـ Margin خارجي، ولو وضعته بعد الـ background بيشتغل كـ Padding داخلي.\"\n\n- **المحاور:** \"ما هي مشكلة `Modifier.composed` القديمة وكيف حلتها جوجل بـ `Modifier.Node`؟\"\n  **المرشح:** \"الـ `composed` القديم كان بيحجز Slots في الـ SlotTable لكل استخدام مما يثقل الذاكرة، بينما `Modifier.Node` كلاسات خفيفة ومستمرة بتشارك مباشرة في القياس والرسم بدون أي Overhead.\"",
        "self_check_ar": "هل عرفت الـ Modifier بوضوح؟ هل بينت أثر الترتيب على مساحة اللمس والخلفية؟ وهل ذكرت معمارية Modifier.Node الحديثة؟",
        "references_ar": f"- [Compose Modifiers Documentation](https://developer.android.com/develop/ui/compose/modifiers) — التوثيق الرسمي لجوجل للـ Modifiers.\n- [Modifier.Node Architecture](https://medium.com/androiddevelopers/compose-modifiers-deep-dive-modifier-node) — مقال معماري عميق لفريق أندرويد حول Modifier.Node.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ Modifier في كومبوز هو الأداة الموحدة المسؤولة عن تزيين وضبط شكل وسلوك المكون؛ بيتحكم في الحجم، والهوامش، والخلفيات، وإيماءات اللمس، وإمكانية الوصول (Accessibility). الترتيب حاسم جداً ومصيري لأن الـ Modifiers بتطبق بالتسلسل من الخارج للداخل زي طبقات البصلة. لو حطيت `padding` قبل `background`، الحشو هيشتغل كـ Margin خارجي ومش هيتلون بالخلفية. لكن لو حطيت `background` الأول وبعدين `padding`، الخلفية هتغطي المساحة كلها والـ padding هيشتغل كـ Inset داخلي للمحتوى. ونفس الكلام بينطبق على مساحة النقر `clickable`.",
        "best_answer_ar": "الـ Modifier في كومبوز حل محل عشرات الخصائص المبعثرة في نظام XML القديم؛ زمان كان عندنا `layout_margin`، و `padding`، و `background`، و `onClickListeners`. كومبوز دمجت كل ده في واجهة واحدة موحدة ومرنة.\n\nالترتيب هو أهم وأخطر مفهوم في الـ Modifiers؛ لأن كل دالة بتناديها بتغلف اللي قبلها مباشرة.\nالمثال الأشهر اللي بيوضح الفكرة هو الجمع بين الحشو والخلفية والنقر:\nلو كتبت: `Modifier.padding(16.dp).background(Color.Red).clickable { }`\nهنا أنت طلبت حشو 16dp الأول، فالنظام بيسيب مساحة فارغة في الخارج، وبعدين يلون الجزء الداخلي فقط بالأحمر، ومساحة اللمس هتكون محصورة في المربع الداخلي الصغير فقط.\n\nبينما لو عكست الترتيب وكتبت: `Modifier.background(Color.Red).clickable { }.padding(16.dp)`\nهنا النظام لون المساحة كلها بالأحمر الأول، وخلى كل المساحة الخارجية قابلة للنقر، وبعدين دخل المحتوى الداخلي لجوه بمقدار 16dp.\n\nعشان كده في كومبوز مفيش حاجة اسمها `margin` منفصل؛ أنت اللي بتصنع الـ Margin أو الـ Padding بمجرد التحكم في ترتيب وضع الـ `padding` بالنسبة للخلفية والحدود.",
        "deep_answer_ar": "تحت الكابوت، الـ Modifiers في الإصدارات الحديثة من كومبوز (Compose 1.3 فما فوق) تم إعادة كتابة نواتها بالكامل لمعمارية ثورية بتسمى `Modifier.Node`.\n\nتاريخياً، كومبوز كانت بتستخدم `Modifier.composed {}` عشان تجهز Modifiers فيها State؛ المشكلة إن دي كانت دالة Composable بتحجز Slots في الـ SlotTable لكل استخدام وتعمل Overhead ضخم في الذاكرة. معمارية `Modifier.Node` حلت الأزمة دي بتحويل الـ Modifiers إلى قائمة مترابطة مزدوجة (Doubly-Linked List) من كائنات Node خفيفة جداً ومستمرة، بتلتصق مباشرة بالـ `LayoutNode` في شجرة العرض.\n\nأثناء دورة حياة الـ Frame، القيود (Constraints) بتتدفق في السلسلة دي بترتيب صارم:\nفي مرحلة القياس (Measurement Phase): القيود بتمر من أول Modifier لآخره للأمام؛ أول Modifier بيحدد القيود المتاحة (Min/Max Width and Height) للـ Nodes اللي بعده.\nفي مرحلة الرسم (Draw Phase): التنفيذ بيمشي من أول Node للأمام، فالخلفيات بتترسم قبل المحتوى.\nوفي مرحلة معالجة اللمس (Hit Testing): إحداثيات اللمس بتتحرك في سلسلة الـ `PointerInputModifierNode`، وأول Node تقابل الإحداثيات بتتحكم في استهلاك الحدث أو تمريره.\n\nفهم المعمارية دي بيمكّن مهندس الأندرويد السينيور من بناء Custom Modifiers فائقة السرعة بوراثة `Modifier.Node` مباشرة وبدون حجز كائنات زائدة في الذاكرة، وده بيمنع أي هبوط في الفريمات أثناء التمرير العنيف في القوائم الطويلة."
    }
}

# ==========================================
# COM-08: How do you model UI state with StateFlow?
# ==========================================
DATA["COM-08"] = {
    "concept_en": """Modeling UI state with StateFlow in Jetpack Compose involves exposing a single, immutable, observable stream of state from an architecture ViewModel, adhering to Unidirectional Data Flow and Clean Architecture principles. Rather than maintaining multiple disconnected StateFlow primitives for individual fields (such as isLoading, userList, and errorMessage), senior engineers model UI state as a consolidated Sealed Interface or immutable Data Class. In the Compose layer, this state is safely collected using lifecycle-aware collectors, ensuring atomic screen rendering where visual states transition synchronously without intermediate flickering or race conditions.""",
    "walkthrough_en": """Modeling atomic UI state with StateFlow and consuming it safely in Compose:
```kotlin
// 1. Consolidated, exhaustive UI state hierarchy
sealed interface ProfileUiState {
    data object Loading : ProfileUiState
    data class Success(val user: UserProfile, val isSyncing: Boolean = false) : ProfileUiState
    data class Error(val message: String, val canRetry: Boolean = true) : ProfileUiState
}

// 2. ViewModel exposes single source of truth via StateFlow
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val getUserProfile: GetUserProfileUseCase
) : ViewModel() {

    val uiState: StateFlow<ProfileUiState> = getUserProfile()
        .map { result ->
            result.fold(
                onSuccess = { ProfileUiState.Success(it) },
                onFailure = { ProfileUiState.Error(it.message ?: "Unknown error") }
            )
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000), // Protects battery & stops upstream flow in background!
            initialValue = ProfileUiState.Loading
        )
}

// 3. Compose Screen consumes StateFlow with lifecycle awareness
@Composable
fun ProfileScreen(viewModel: ProfileViewModel = hiltViewModel()) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    when (val currentState = state) {
        is ProfileUiState.Loading -> CircularProgressIndicator()
        is ProfileUiState.Success -> ProfileContent(user = currentState.user)
        is ProfileUiState.Error -> ErrorView(message = currentState.message)
    }
}
```""",
    "short_en": """We model UI state with StateFlow by creating a single, consolidated sealed interface or immutable data class that represents the entire screen atomically. Instead of exposing multiple independent StateFlows that cause flickering and race conditions, the ViewModel exposes one StateFlow created via stateIn with SharingStarted.WhileSubscribed(5000). The Compose UI consumes it using collectAsStateWithLifecycle(), ensuring atomic rendering, zero desynchronization, and automatic upstream flow cancellation when the app is in the background.""",
    "structured_en": """Modeling UI state using StateFlow is the modern enterprise standard for bridging ViewModels to Jetpack Compose layouts.
In anti-pattern architectures, ViewModels expose fragmented reactive variables: a StateFlow for isLoading, another for userName, and another for errorMessage. This leads to state race conditions and UI flickering, where the loading spinner disappears a split second before the new user data arrives.
To ensure atomic, predictable rendering, we adhere to three architectural rules.
First, consolidate UI state into a single immutable data model. Using a Sealed Interface representing distinct mutual states (Loading, Success, Error) guarantees exhaustive when evaluation and eliminates impossible states, like being simultaneously in Loading and Error.
Second, produce the StateFlow using the stateIn operator inside the ViewModel. Configuring SharingStarted.WhileSubscribed(5_000) guarantees that the upstream coroutine flow starts only when the UI is actively observing, and pauses after a 5-second buffer when the screen enters the background, surviving configuration changes without wasting network resources.
Third, consume the flow inside Compose using collectAsStateWithLifecycle(), ensuring collection halts automatically when the Activity lifecycle drops below the specified minimum state.""",
    "deep_senior_en": """Under the hood, StateFlow is a stateful, hot, conflated shared flow that maintains an atomic reference to its current value.
When a composable collects a StateFlow, the collection coroutine observes emissions and updates an underlying SnapshotState primitive. Because StateFlow is inherently conflated (meaning it drops intermediate values if the collector is slower than the emitter), the Compose runtime receives only the latest state snapshot, perfectly aligning with frame rendering cadences.
The choice of SharingStarted.WhileSubscribed(5_000) inside stateIn is an engineered solution addressing Android's configuration change lifecycle.
When an Activity rotates, the previous Activity is destroyed and the new Activity is created, causing Compose to temporarily unsubscribe from the StateFlow. The 5,000-millisecond delay prevents the upstream coroutine scope from prematurely canceling its database or network subscription during this brief rotation window, avoiding duplicate network calls.
If the user genuinely navigates away from the screen or presses Home, the 5-second timer expires, and the upstream flow cancels, conserving memory and network bandwidth.
Furthermore, modeling state as a Sealed Interface enforces compile-time exhaustiveness, allowing ProGuard and R8 to optimize dead-code elimination while making screenshot testing and state playback completely deterministic. In contrast to legacy LiveData, StateFlow operates seamlessly on pure Kotlin Coroutines without hidden main thread constraints or platform SDK bindings, enabling shared domain state across Kotlin Multiplatform targets.""",
    "meta_ar": {
        "id": "COM-08",
        "questionAr": "كيف تنمذج حالة واجهة المستخدم (UI State) باحترافية باستخدام StateFlow في Compose؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على نمذجة الحالة كنموذج موحد (Single UiState / Sealed Interface)، ومنع الحالات المتناقضة (Impossible States)، واستخدام `stateIn` مع `WhileSubscribed(5000)`، واستهلاكها بـ `collectAsStateWithLifecycle`.",
        "why_it_matters_ar": "توزيع الحالة على عدة متغيرات StateFlow منفصلة يسبب وميضاً في الواجهة (Flickering) وظهور حالات مستحيلة كأن تظهر شاشة الخطأ وشاشة التحميل معاً في نفس اللحظة.",
        "worked_example_ar": "نمذجة الحالة كـ Sealed Interface موحد ومستقر:\n```kotlin\nsealed interface UiState {\n    data object Loading : UiState\n    data class Success(val data: List<Item>) : UiState\n    data class Error(val msg: String) : UiState\n}\n// استهلاكها في كومبوز بأمان تام وتغطية شاملة بـ when\nval state by vm.uiState.collectAsStateWithLifecycle()\nwhen (val s = state) { ... }\n```",
        "trade_offs_ar": "يتطلب تجميع كل المتغيرات في كائن واحد وتحديثه بنسخ جديدة بـ `copy()`، لكنه يضمن رندرة ذرية متزامنة ويقضي على أخطاء الـ Race Conditions نهائياً.",
        "failure_modes_ar": "عمل StateFlow مستقل لكل حقل في الشاشة، أو استخدام `SharingStarted.Eagerly` مما يجعل الـ Flow يستمر في استهلاك الإنترنت والبطارية والتطبيق في الخلفية.",
        "production_perspective_ar": "في كود الإنتاج عالي المستوى، نمنع وجود أكثر من StateFlow واحد لكل شاشة، ونعتمد دائماً مهلة الـ 5 ثواني `WhileSubscribed(5000)` لحماية موارد الجهاز أثناء تدوير الشاشة.",
        "how_to_answer_ar": "اشرح القواعد الثلاث: أولاً توحيد الحالة في Sealed Interface أو Data Class لمنع الحالات المستحيلة وضمان الذرية (Atomic UI State)، ثانياً تصدير الـ Flow بـ `stateIn` مع `WhileSubscribed(5000)` لشرح سبب الـ 5 ثواني مع تدوير الشاشة، وثالثاً الاستهلاك الآمن بـ `collectAsStateWithLifecycle` لحماية موارد الجهاز في الخلفية.",
        "talking_points_ar": "مفهوم Atomic State Representation، ومنع الـ Impossible States، ودور `WhileSubscribed(5000)` في تفادي إعادة الطلبات عند تدوير الشاشة، ومزايا StateFlow كـ Conflated Hot Flow.",
        "follow_ups_ar": "- **المحاور:** \"لماذا نحدد مهلة 5000 ميلي ثانية تحديداً في `WhileSubscribed(5000)`؟\"\n  **المرشح:** \"عشان نوفر نافذة أمان لتدوير الشاشة (Configuration Change)؛ تدمير الـ Activity القديمة وإنشاء الجديدة بياخد أجزاء من الثانية، فالمهلة دي بتمنع إلغاء اشتراك الـ Flow وإعادة طلب البيانات من السيرفر بدون داعٍ.\"\n\n- **المحاور:** \"ما هو عيب وجود عدة متغيرات StateFlow منفصلة لـ isLoading و isError و data؟\"\n  **المرشح:** \"بيحصل Race Condition و UI Flickering؛ ممكن الداتا الجديدة توصل قبل ما isLoading يتحدث، فالشاشة ترسم حالة مشوهة يظهر فيها التحميل مع الداتا معاً.\"",
        "self_check_ar": "هل شرحت فكرة الحالة الموحدة و Sealed Interface؟ هل وضحت سر الـ 5 ثواني في WhileSubscribed؟ وهل ربطت الإجابة بالاستهلاك الآمن في كومبوز؟",
        "references_ar": f"- [Android Architecture: UI State Modeling](https://developer.android.com/topic/architecture/ui-layer#state-production) — الدليل الرسمي لجوجل لنمذجة الحالة.\n- [Things to know about StateFlow and WhileSubscribed](https://medium.com/androiddevelopers/things-to-know-about-flows-sharein-and-statein-operators-20e6ec043d6d) — مقال مطوري أندرويد حول مشغلات Flow.",
        "quick_answer_ar": "بنمذج حالة الواجهة (UI State) باستخدام `StateFlow` عن طريق إنشاء نموذج موحد وشامل للحالة، غالباً كـ Sealed Interface بيمثل الحالات الحصرية: التحميل (Loading)، والنجاح (Success)، والخطأ (Error). بنبعد تماماً عن عمل متغير StateFlow منفصل لكل حقل لأن ده بيخلق حالات متناقضة ووميضاً مزعجاً في الواجهة. في الـ ViewModel، بنحول التدفق لـ StateFlow باستخدام `stateIn` مع مهلة `SharingStarted.WhileSubscribed(5000)` لحماية البطارية، وفي كومبوز بنستهلكه حصرياً بدالة `collectAsStateWithLifecycle()` عشان التجميع يقف تلقائياً لما التطبيق يروح في الخلفية.",
        "best_answer_ar": "نمذجة الـ UI State باحترافية هي العلامة الفارقة بين كود مرتب ومستقر وكود مليان Bugs وسباقات بيانات عشوائية (Race Conditions).\n\nفي الكود السيئ، المطور بيعمل في الـ ViewModel متغير `isLoading`، ومتغير `userList`، ومتغير `errorMessage`. الكارثة هنا إن دي حالات مستقلة؛ ممكن في لحظة يكون `isLoading = true` وفي نفس الوقت `errorMessage` فيه نص قديم، فتلاقي الشاشة بتعرض دايرة تحميل ورسالة خطأ مع بعض في مشهد مشوه بنسميه الـ Impossible States.\n\nالتصميم المتين بيعتمد على تلات ركائز:\nالركيزة الأولى: تجميع الحالة في كائن واحد ذري (Atomic State). بنعمل Sealed Interface اسمه `ProfileUiState` بيمثل فروع الحالات بوضوح: إما `Loading`، أو `Success` ومعاه داتا المستخدم، أو `Error` ومعاه رسالة الخطأ. بكده بنضمن استحالة وجود حالتين مع بعض، ونظام `when` في كومبوز بيغطي كل السيناريوهات بدقة تامة.\n\nالركيزة الثانية: تصدير الـ StateFlow من الـ ViewModel باستخدام مشغل `stateIn` وضبط استراتيجية البدء بـ `SharingStarted.WhileSubscribed(5_000)`.\n\nالركيزة الثالثة: جمع البيانات في الواجهة بدالة `collectAsStateWithLifecycle()`. بكده الواجهة بتكون مجرد مرآة نقية بتعكس حالة واحدة متزامنة دائماً.",
        "deep_answer_ar": "تحت الكابوت، الـ `StateFlow` هو Hot Flow مدمج فيه كاش للقيمة الحالية (Conflated Flow)؛ ده معناه إنه بيحتفظ بالقيمة الأخيرة دايماً، ولو التطبيق انتج 5 تحديثات في كسر من الثانية، الكومبوزابل مش هيضيع وقته في رندرة التحديثات القديمة بل هيستقبل القيمة الأحدث فوراً بالتزامن مع فريم الشاشة التالي.\n\nالسر الهندسي الأعمق اللي بيسأل عنه المحاورون الكبار هو: ليه بنستخدم `WhileSubscribed(5000)` تحديداً؟\nأثناء تدوير الهاتف (Configuration Change)، الـ Activity القديمة بتتدمر والجديدة بتتبني؛ اللحظة دي كومبوز بتلغي اشتراكها مؤقتاً في الـ Flow لبضع مئات من الميلي ثانية. لو استخدمنا `WhileSubscribed()` بدون وقت، الـ Coroutine في الـ ViewModel هيقفل اشتراكه مع الداتابيز أو السيرفر فوراً، وأول ما الشاشة تفتح في الوضع الأفقي هتعيد طلب البيانات من الأول! مهلة الـ 5 ثواني بتعمل Buffer يحافظ على استمرار الـ Flow أثناء التدوير. ولو المستخدم خرج فعلاً من التطبيق وداس الزرار الرئيسي، بعد 5 ثواني الـ Flow بيوقف تماماً ويوفر البطارية والإنترنت.\n\nودمج ده مع `collectAsStateWithLifecycle()` بيضمن إن جمع البيانات بيقف أوتوماتيكياً لما دورة حياة الشاشة تنزل تحت `Lifecycle.State.STARTED`، وده بيمنع أي تسريب للذاكرة أو استهلاك غير مبرر للمعالج في الخلفية.\n\nومقارنة بـ LiveData القديمة، الـ StateFlow بتشتغل بالكامل عبر كوتلن Coroutines النقية وبدون أي ارتباط بمنصة أندرويد، وده بيسمح بمشاركة كود الـ ViewModel وإدارة الحالة عبر تطبيقات Kotlin Multiplatform بسهولة تامة."
    }
}

# ==========================================
# COM-09: What does collectAsStateWithLifecycle() solve?
# ==========================================
DATA["COM-09"] = {
    "concept_en": """collectAsStateWithLifecycle() is a lifecycle-aware Compose state collection operator from the androidx.lifecycle:lifecycle-runtime-compose library. It solves the critical resource leakage and background battery drain vulnerabilities caused by the standard collectAsState() API. When a standard collectAsState() collects a Kotlin Flow or StateFlow, it launches a coroutine tied exclusively to the composition lifecycle; consequently, when the hosting Activity or Fragment moves into the background (such as when the user navigates Home or switches apps), flow collection remains active, burning CPU cycles and draining mobile data. collectAsStateWithLifecycle() halts collection whenever the lifecycle drops below a target state (Lifecycle.State.STARTED by default).""",
    "walkthrough_en": """Demonstrating resource leak prevention with collectAsStateWithLifecycle():
```kotlin
// ❌ DANGEROUS ANTI-PATTERN: Standard collectAsState() leaks background resources
@Composable
fun BadLocationTrackingScreen(viewModel: LocationViewModel) {
    // Flow continues collecting GPS coordinates and network updates when app is in BACKGROUND!
    // Burns battery, consumes cellular bandwidth, and risks background crashes!
    val location by viewModel.locationFlow.collectAsState()
    Text("Location: $location")
}

// ✅ ARCHITECTURAL BEST PRACTICE: Lifecycle-aware flow collection
@Composable
fun SafeLocationTrackingScreen(viewModel: LocationViewModel) {
    // Halts collection automatically when Activity drops below STARTED (e.g. app sent to background)
    // Resumes automatically when user returns to foreground! Zero battery waste!
    val location by viewModel.locationFlow.collectAsStateWithLifecycle()
    Text("Location: $location")
}
```""",
    "short_en": """collectAsStateWithLifecycle() solves background resource waste and battery drain by making flow collection aware of Android component lifecycles. Standard collectAsState() listens to the composition lifecycle rather than the Activity lifecycle; when an app moves to the background, it keeps collecting data, wasting CPU, network, and battery. In contrast, collectAsStateWithLifecycle() automatically cancels flow collection when the lifecycle falls below STARTED and resumes seamlessly when returning to the foreground.""",
    "structured_en": """The introduction of collectAsStateWithLifecycle() addresses one of the most hazardous subtle pitfalls in early Jetpack Compose development.
Originally, developers collected StateFlows using the built-in collectAsState() operator.
However, collectAsState() is designed to be platform-agnostic: it manages collection based strictly on the composable's presence in the composition tree.
Because an Activity in the background (like when the user minimizes the app) still maintains its composition hierarchy in memory, collectAsState() continues collecting emissions indefinitely.
If the underlying flow listens to GPS location sensors, camera frames, WebSocket messages, or frequent database updates, the application silently drains battery, burns cellular data, and risks background memory pressure.
collectAsStateWithLifecycle() solves this by tying flow collection directly to the Android Lifecycle.
By default, it uses Lifecycle.State.STARTED as its threshold.
When the user sends the application to the background, the Activity triggers onStop(), dropping below STARTED. The operator immediately cancels the internal collection coroutine.
When the user resumes the app, onStart() fires, and collection automatically restarts from the latest state, ensuring optimal battery efficiency.""",
    "deep_senior_en": """Under the hood, collectAsStateWithLifecycle() delegates its collection mechanics to the repeatOnLifecycle API implemented inside the Androidx Lifecycle library.
When invoked, it accesses the current LocalLifecycleOwner and establishes a coroutine managed by repeatOnLifecycle(minActiveState = Lifecycle.State.STARTED).
Inside repeatOnLifecycle, a LifecycleEventObserver monitors the state of the host Lifecycle.
When the state transitions to ON_START, repeatOnLifecycle launches a new CoroutineScope on the specified CoroutineContext, executing the collect loop and updating the internal MutableState<T> object in the SlotTable.
When the host transitions to ON_STOP, repeatOnLifecycle immediately executes a hard cancellation on that child CoroutineScope.
This cancellation cascades upstream through the Kotlin coroutines cooperative cancellation machinery. If the upstream StateFlow was produced via stateIn with SharingStarted.WhileSubscribed(), the cancellation triggers the subscription count to drop to zero, allowing the upstream repository or network pipeline to shut down cleanly.
By contrast, standard collectAsState() uses LaunchedEffect(Unit) or produceState(), which only cancels when the composable leaves the composition entirely (e.g., when navigation pops the backstack entry).
Using collectAsStateWithLifecycle() is mandatory for production Android apps to prevent battery penalties and background memory bloat. Additionally, repeatOnLifecycle preserves coroutine execution safety by isolating collector exceptions and guaranteeing that downstream UI collectors never observe stale or invalidated memory references during configuration transitions or process recreation events.""",
    "meta_ar": {
        "id": "COM-09",
        "questionAr": "ما هي المشكلة التي تحلها دالة collectAsStateWithLifecycle() في Jetpack Compose؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم الفرق الجوهري بين دورة حياة الكومبوز (Composition Lifecycle) ودورة حياة أندرويد (Platform Lifecycle)، واستيعاب مخاطر الـ Background Resource Leak، ودور `repeatOnLifecycle` في توفير البطارية.",
        "why_it_matters_ar": "استخدام `collectAsState()` العادي يبقي جمع تدفق البيانات (Flow Collection) شغالاً حتى بعد خروج المستخدم من التطبيق وإرساله للخلفية، مما يستهلك الإنترنت والبطارية ويؤدي لخفض تقييم التطبيق على متجر جوجل بلاي بسبب استنزاف الموارد.",
        "worked_example_ar": "مقارنة حماية البطارية بـ collectAsStateWithLifecycle:\n```kotlin\n// ❌ خطر: يستمر في جمع إحداثيات الـ GPS والتطبيق في الخلفية\nval loc by vm.gpsFlow.collectAsState()\n// ✅ آمن: يوقف الاستماع تلقائياً بمجرد خروج التطبيق للشاشة الرئيسية\nval loc by vm.gpsFlow.collectAsStateWithLifecycle()\n```",
        "trade_offs_ar": "يتطلب استيراد مكتبة `lifecycle-runtime-compose`، لكنه ضرورة أمنية وهندسية لا غنى عنها في أي تطبيق إنتاج لحماية بطارية المستخدم.",
        "failure_modes_ar": "الاعتماد على `collectAsState()` لمراقبة تدفقات مستمرة كـ WebSockets أو حساسات الحركة، مما يستنزف البطارية ويسبب سخونة الجهاز والتطبيق في جيب المستخدم.",
        "production_perspective_ar": "في المشروعات الكبيرة، نضع فحصاً في Lint أو Detekt يمنع استخدام `collectAsState()` داخل شاشات أندرويد نهائياً، ويفرض استخدام `collectAsStateWithLifecycle()` حصرياً.",
        "how_to_answer_ar": "حدد المشكلة بوضوح: دالة `collectAsState()` القديمة مربوطة بدورة حياة الكومبوز مش دورة حياة الأكتيفيتي، فبتفضل تجمع البيانات والتطبيق في الخلفية، واشرح الحل: `collectAsStateWithLifecycle()` بتعتمد على `repeatOnLifecycle` وبتوقف الـ Flow تلقائياً لما الشاشة تنزل تحت `STARTED` وتستأنفه لما ترجع، وده بيحمي البطارية والإنترنت.",
        "talking_points_ar": "الفرق بين Composition Lifecycle و Android Lifecycle، واستنزاف الموارد في الخلفية (Background Battery Drain)، وآلية عمل `repeatOnLifecycle`، والتناغم مع `WhileSubscribed`.",
        "follow_ups_ar": "- **المحاور:** \"لماذا صنعت جوجل collectAsState() في البداية إذا كانت تسبب هذه المشكلة؟\"\n  **المرشح:** \"لأن كومبوز كانت مصممة كـ Multiplatform UI toolkit مستقلة عن منصة أندرويد؛ فـ `collectAsState` بتشتغل على الديسك توب والويب بدون أي ارتباط بـ Android Lifecycle، ولما واجه المطورون مشاكل البطارية في أندرويد، صنعت جوجل مكتبة مخصصة بـ `collectAsStateWithLifecycle`.\"\n\n- **المحاور:** \"ما هو الحد الأدنى الافتراضي لدورة الحياة الذي توقف عنده الدالة الجمع؟\"\n  **المرشح:** \"الحالة الافتراضية هي `Lifecycle.State.STARTED`؛ لما التطبيق يروح في الخلفية بياخد `onStop` فبينزل تحت Started، والجمع بيقف فوراً.\"",
        "self_check_ar": "هل وضحت الفارق بين دورة حياة الكومبوز ودورة حياة الأكتيفيتي؟ هل شرحت أثر ذلك على البطارية في الخلفية؟ وهل بينت علاقتها بـ repeatOnLifecycle؟",
        "references_ar": f"- [Consuming flows safely in Jetpack Compose](https://medium.com/androiddevelopers/consuming-flows-safely-in-jetpack-compose-cde014d0d3a3) — المقال الرسمي لجوجل لشرح المشكلة والحل.\n- [Lifecycle-aware components documentation](https://developer.android.com/topic/libraries/architecture/lifecycle) — توثيق دورة حياة أندرويد الرسمية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "دالة `collectAsStateWithLifecycle()` بتحل مشكلة تسريب الموارد واستنزاف البطارية في الخلفية (Background Resource Leak). دالة `collectAsState()` العادية بتربط جمع البيانات بدورة حياة الكومبوز مش دورة حياة أندرويد؛ فلو المستخدم داس Home وخرج من التطبيق، الشاشة بتفضل تجمع البيانات وتسحب باقة وإنترنت والبطارية بتخلص. دالة `collectAsStateWithLifecycle()` بتراقب دورة حياة الأكتيفيتي الحقيقية؛ أول ما التطبيق يروح في الخلفية وينزل تحت حالة `STARTED`، بتلغي عملية الجمع فوراً، وأول ما المستخدم يرجع للتطبيق بتستأنف الجمع بآخر حالة، وده بيضمن أعلى حماية لموارد الهاتف.",
        "best_answer_ar": "دالة `collectAsStateWithLifecycle()` هي واحدة من أهم الإضافات اللي قدمتها جوجل لمعالجة فخ خطير وقع فيه مئات المطورين في بدايات كومبوز.\n\nالمشكلة بتنبع من وجود دورة حياة لعنصر الواجهة (Composition Lifecycle) مستقلة عن دورة حياة أندرويد (Activity Lifecycle).\nدالة `collectAsState()` القديمة كانت بتراقب وجود الكومبوزابل في الشجرة؛ وطالما المستخدم مخرجش من الشاشة بزرار الرجوع (يعني التطبيق فضل في الخلفية أو المستخدم فتح تطبيق تاني)، الكومبوزابل بيفضل عايش في الذاكرة. النتيجة إن لو الـ Flow ده بيراقب إحداثيات GPS، أو سوكت متصل بسيرفر، أو تحديثات داتابيز مستمرة، التطبيق هيفضل شغال على آخره والتليفون في جيب المستخدم، وده كان بيسبب سخونة الجهاز واستهلاك الباقة وكراشات في الخلفية.\n\nجوجل صنعت `collectAsStateWithLifecycle()` في مكتبة مخصصة عشان تربط الجمع بدورة حياة الأكتيفيتي الحقيقية.\nالدالة بتعتمد في الخلفية على `repeatOnLifecycle(Lifecycle.State.STARTED)`؛ لما المستخدم يروح في الخلفية والأكتيفيتي تاخد `onStop`، الدالة بتلغي الـ Coroutine فوراً، وده بيخلي الـ ViewModel كمان يوقف الـ Flow لو مستخدمين `WhileSubscribed`. وأول ما المستخدم يرجع ويحصل `onStart`، الجمع بيبدأ تاني بسلاسة وبأحدث بيانات.\n\nفي كود الإنتاج، استخدام الدالة دي إلزامي في كل شاشات التطبيق لضمان الحفاظ على بطارية المستخدم.",
        "deep_answer_ar": "تحت الكابوت، `collectAsStateWithLifecycle()` بتعتمد على مكتبة `androidx.lifecycle:lifecycle-runtime-compose` وبتحتوي على معمارية معالجة دقيقة جداً مبنية على `repeatOnLifecycle`.\n\nالدالة بتقرأ الـ `LocalLifecycleOwner` الحالي في الـ Composition Tree، وبتنشئ `LifecycleEventObserver`. أول ما الأكتيفيتي أو الـ Fragment يحصل له حدث `ON_START`، الـ Observer بينشئ CoroutineScope جديد ويبدأ حلقة الـ `collect` اللي بتحدث الـ `MutableState` في الـ SlotTable. وأول ما يجي حدث `ON_STOP`، الـ Observer بينفذ إلغاءً صارماً (Hard Cancellation) للـ CoroutineScope ده فوراً.\n\nالإلغاء ده بيصعد في شجرة الـ Coroutines التعاونية (Cooperative Cancellation) للأعلى؛ فلو الـ StateFlow في الـ ViewModel معمول بـ `stateIn` ومعاه `SharingStarted.WhileSubscribed()`، إلغاء الكوليكشن بيخلي عدد المشتركين (Subscription Count) ينزل فوراً للصفر، وده بيسمح للـ Repository أو الـ WebSocket إنه يقفل الاتصال بالكامل ويوفر موارد السيرفر وموارد الموبايل.\n\nبينما دالة `collectAsState()` العادية بتستخدم جواها مجرد `LaunchedEffect(Unit)`؛ ودي مبيتمش إلغاؤها إلا لما الكومبوزابل يخرج تماماً من الـ Composition بـ Back navigation، وتجاهلها لدورة حياة أندرويد كان بيعرض التطبيق لعقوبات الـ Bad Behavior في Google Play Vitals بسبب الـ Excessive Background Execution.\n\nوعلاوة على كده، آلية `repeatOnLifecycle` بتعزل أخطاء واستثناءات الكوروتين بذكاء، وبتضمن إن واجهة المستخدم متستقبلش أي بيانات غير صالحة أثناء التبديل السريع بين الشاشات، وده بيحمي التطبيق من الـ Race Conditions والانهيارات المفاجئة بعد استعادة النشاط من الخلفية."
    }
}

# ==========================================
# COM-10: What are LaunchedEffect, DisposableEffect, SideEffect, and rememberCoroutineScope?
# ==========================================
DATA["COM-10"] = {
    "concept_en": """Jetpack Compose provides four foundational effect handlers to execute imperative side-effects safely across the composition lifecycle. LaunchedEffect launches a lifecycle-aware coroutine scope bound to composition keys, canceling and restarting whenever keys change. DisposableEffect executes cleanup logic via onDispose when its keys change or when the composable leaves the composition, ideal for registering and unregistering external system observers or listeners. SideEffect executes a non-suspending side-effect on every successful recomposition pass, synchronizing Compose state with external objects not managed by Compose. rememberCoroutineScope creates a long-lived coroutine scope bound to the composition call site, enabling user-initiated event handlers (like button clicks) to launch coroutines outside composition phases.""",
    "walkthrough_en": """Applying the four effect handlers in an Android multimedia screen:
```kotlin
@Composable
fun VideoPlayerScreen(
    videoId: String,
    analytics: AnalyticsTracker,
    scaffoldState: SnackbarHostState
) {
    // 1. rememberCoroutineScope: Launch coroutine from user event callbacks (e.g. Button click)
    val coroutineScope = rememberCoroutineScope()

    // 2. LaunchedEffect: Suspending coroutine tied to a key; restarts if videoId changes
    LaunchedEffect(videoId) {
        analytics.trackScreenView("Video_$videoId")
        // Load initial video buffers asynchronously...
    }

    // 3. DisposableEffect: Lifecycle-bound side-effect with cleanup logic
    DisposableEffect(videoId) {
        val listener = VideoPlaybackListener { /* handle playback */ }
        registerVideoListener(listener)

        onDispose {
            // Cleanup executed when videoId changes or composable leaves the composition!
            unregisterVideoListener(listener)
        }
    }

    // 4. SideEffect: Runs on EVERY successful recomposition pass; syncs state with external non-Compose world
    SideEffect {
        analytics.setGlobalUserProperty("last_rendered_video", videoId)
    }

    Button(onClick = {
        // Must use rememberCoroutineScope because onClick is NOT a composable scope!
        coroutineScope.launch { scaffoldState.showSnackbar("Video bookmarked!") }
    }) {
        Text("Bookmark")
    }
}
```""",
    "short_en": """These four primitives manage side-effects safely in Compose. LaunchedEffect runs suspending coroutines tied to a key, canceling and restarting when the key changes. DisposableEffect manages operations requiring cleanup, executing onDispose when leaving the composition. SideEffect runs on every successful recomposition to sync Compose state with external non-Compose objects. rememberCoroutineScope provides a coroutine scope for user-triggered callbacks like button clicks that execute outside of the composition phase.""",
    "structured_en": """Side-effect handlers are the official gateway connecting Compose's pure declarative world to the imperative Android platform.
Because composables can recompose unpredictably and frequently, executing side-effects directly inside the function body causes duplicate network requests, memory leaks, and state bugs.
Compose provides four specialized tools tailored to specific operational contexts.
LaunchedEffect is designed for suspending operations tied to state. It launches a coroutine upon entering composition and automatically cancels and restarts if its key parameter changes. It is ideal for loading screen data or triggering single-shot animations.
DisposableEffect is designed for non-suspending operations that require explicit teardown. It provides an onDispose clause that executes when its key changes or when the composable leaves the composition tree, making it the perfect tool for registering broadcast receivers, sensor managers, or third-party SDK listeners.
SideEffect executes a non-suspending block after every successful recomposition. It is used to push updated Compose state to external objects that are not managed by Compose, such as updating an external analytics tracker or system notification manager.
rememberCoroutineScope provides a CoroutineScope bound to the composition point. It is strictly used in event callbacks (like onClick or onSwipe) where code runs outside the composable body and cannot call composable effect APIs directly.""",
    "deep_senior_en": """Under the hood, these four effect handlers interface directly with the Composer's RecomposeScope and SlotTable management routines.
LaunchedEffect stores an internal CoroutineScope instance inside a slot. When its key changes during recomposition, the Composer invokes Job.cancel() on the existing coroutine job and launches a new child job on the Apply-dispatcher. If the composable leaves composition, the Composer cancels the scope entirely.
DisposableEffect registers a DisposableEffectScope inside the SlotTable. Crucially, the Compose runtime guarantees that onDispose() will be invoked in two exact scenarios: either before re-running the effect with new keys, or when the layout node is unmounted from the composition tree. Failing to provide onDispose() results in a compile-time error.
SideEffect operates differently: it does not create a coroutine. Instead, the Composer records the lambda into a pending side-effects queue. This queue is executed strictly after the current composition transaction successfully applies to the layout tree. If the composition pass is canceled, interrupted, or discarded due to mid-flight state invalidation, the queued SideEffect lambdas are purged without executing, preventing inconsistent external state updates.
rememberCoroutineScope allocates a CoroutineScope bound to the CompositionContext. When the host composable is unmounted, the runtime calls cancel() on the scope's Job, ensuring that background jobs launched from button clicks do not outlive their UI context.""",
    "meta_ar": {
        "id": "COM-10",
        "questionAr": "قارن بين أدوات الآثار الجانبية في كومبوز: LaunchedEffect و DisposableEffect و SideEffect و rememberCoroutineScope.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على اختيار أداة الآثار الجانبية (Side Effects) الصحيحة في كومبوز، وفهم دورة حياة كل أداة، واستيعاب آليات التنظيف (Cleanup بـ onDispose)، وإطلاق الـ Coroutines من كولباكات الأزرار.",
        "why_it_matters_ar": "اختيار الأداة الخاطئة يسبب تسريب المستمعين (Memory Leaks بسبب نسيان onDispose)، أو تشغيل دوال التعليق (Suspend functions) في كل فريم، أو إلغاء العمليات الحساسة قبل اكتمالها.",
        "worked_example_ar": "استخدام أدوات الـ Side Effects الأربعة:\n```kotlin\n// 1. LaunchedEffect: كود تعليق يبدأ مع المفتاح\nLaunchedEffect(id) { vm.load(id) }\n// 2. DisposableEffect: مستمع يحتاج لتنظيف\nDisposableEffect(Unit) {\n    reg(); onDispose { unreg() }\n}\n// 3. rememberCoroutineScope: إطلاق كوروتين من زرار\nval scope = rememberCoroutineScope()\nButton(onClick = { scope.launch { ... } })\n// 4. SideEffect: مزامنة مع كود خارجي بعد كل رندرة\nSideEffect { tracker.update() }\n```",
        "trade_offs_ar": "استخدام الأدوات الصحيحة يضمن عزل الكود الإجرائي عن الرندرة التصريحية، لكنه يتطلب فهماً عميقاً للمفاتيح (Keys) ودورة حياة الشجرة.",
        "failure_modes_ar": "إطلاق كوروتين من داخل جسم الكومبوزابل بـ GlobalScope بدلاً من `LaunchedEffect`، أو نسيان إلغاء تسجيل المستمعين بـ `DisposableEffect` مما يسبب تسريب الذاكرة.",
        "production_perspective_ar": "في المشروعات الكبيرة، نمنع تشغيل أي عملية إجرائية في جسم الكومبوزابل مباشرة، ونلزم المطورين باستخدام `LaunchedEffect` للعمليات المعلقة، و `rememberCoroutineScope` للأزرار، و `DisposableEffect` للـ Listeners.",
        "how_to_answer_ar": "اشرح وظيفة ودورة حياة كل أداة بوضوح: `LaunchedEffect` للكوروتين المعلق المرتبط بمفتاح، و `DisposableEffect` للمستمعين الذين يحتاجون لتنظيف بـ onDispose، و `rememberCoroutineScope` لإطلاق كوروتين من كولباك خارجي كالأزرار، و `SideEffect` للمزامنة مع كائنات خارجية بعد كل رندرة ناجحة.",
        "talking_points_ar": "مفهوم Side Effects في البرمجة التصريحية، ودورة حياة المفاتيح (Key-bound lifecycle)، ودور onDispose في منع تسريبات الذاكرة، وقائمة انتظار الـ SideEffect المؤجلة.",
        "follow_ups_ar": "- **المحاور:** \"لماذا لا نستطيع استخدام LaunchedEffect داخل دالة onClick في الزرار؟\"\n  **المرشح:** \"لأن `onClick` هي كولباك عادي خارج سياق الكومبوزابل (Non-composable lambda)، ودوال الـ Effect مينفعش تتنادى إلا داخل دالة `@Composable`، عشان كده بنستخدم `rememberCoroutineScope`.\"\n\n- **المحاور:** \"ما هو الفرق الجوهري بين كود يوضع في جسم الدالة مباشرة وكود يوضع في SideEffect؟\"\n  **المرشح:** \"الكود في جسم الدالة ممكن يتنفذ حتى لو الـ Recomposition اتلغى في النص، بينما `SideEffect` بيضمن إن الكود مش هيتنفذ إلا بعد اكتمال مرحلة التكوين بنجاح وتطبيقها على الشاشة.\"",
        "self_check_ar": "هل قارنت بين الأدوات الأربعة بدقة؟ هل شرحت دور كل أداة؟ وهل بينت آلية التنظيف بـ onDispose؟",
        "references_ar": f"- [Side-effects in Jetpack Compose](https://developer.android.com/develop/ui/compose/side-effects) — الدليل الرسمي لجوجل للآثار الجانبية.\n- [Compose Effect Handlers Deep Dive](https://medium.com/androiddevelopers/) — دليل مطوري أندرويد المعماري لأدوات التأثيرات.",
        "quick_answer_ar": "الأدوات الأربعة هما الحراس المسؤولين عن تشغيل الكود الإجرائي (Imperative Code) بأمان داخل كومبوز: `LaunchedEffect` بيشغل كود معلق (Coroutine) مرتبط بمفتاح، وبيعيد تشغيله لما المفتاح يتغير ويتلغي لما يخرج من الشاشة. `DisposableEffect` مخصص للمستمعين اللي بيحتاجوا تنظيف وإلغاء تسجيل عبر بلوك إلزامي `onDispose` لمنع تسريب الذاكرة. `SideEffect` بيتنفذ بعد كل عملية Recomposition ناجحة عشان يزامن بيانات كومبوز مع كائنات خارجية مش خاضعة لكومبوز. أما `rememberCoroutineScope` فبيدينا CoroutineScope نقدر نستخدمه جوه كولباكات تفاعل المستخدم زي ضغطات الأزرار `onClick` لإطلاق عمليات معلقة خارج مرحلة الرندرة.",
        "best_answer_ar": "إدارة الآثار الجانبية (Side Effects) في كومبوز بتتطلب فهم دقيق للفارق بين مرحلة التكوين ومرحلة التفاعل.\n\nالأداة الأولى: `LaunchedEffect`.\nدي بنستخدمها لما نكون عايزين نشغل Coroutine تلقائياً بمجرد فتح الشاشة أو أول ما قيمة معينة تتغير (زي تحميل بيانات منتج جديد لما يتغير الـ `productId`). الكوروتين بيفضل شغال، ولو المستخدم خرج من الشاشة أو الـ ID اتغير، كومبوز بتلغي الكوروتين القديم أوتوماتيكياً وتشغل الجديد.\n\nالأداة الثانية: `DisposableEffect`.\nدي الأداة المثالية للتعامل مع الـ Listeners أو الـ Observers الخارجية زي تسجيل BroadcastReceiver أو مستمع لحركة الحساسات. ميزتها الجوهرية إنها بتجبرك تكتب بلوك `onDispose`؛ البلوك ده بيتنفذ حتماً أول ما الكومبوزابل يخرج من الشجرة أو المفتاح يتغير عشان تلغي تسجيل المستمع وتمنع تسريب الذاكرة (Memory Leak).\n\nالأداة الثالثة: `rememberCoroutineScope`.\nالزرار العادي دالة `onClick` بتاعته مش Composable، فمتقدرش تنادي جواها دالة Suspend مباشرة ولا تقدر تستدعي `LaunchedEffect`. الحل إننا بنطلب `val scope = rememberCoroutineScope()` فوق في الدالة، وداخل ضغطة الزرار بنقول `scope.launch { snackbarHostState.showSnackbar() }`.\n\nالأداة الرابعة: `SideEffect`.\nدي دالة عادية (مش كوروتين) بتتنفذ بعد كل فريم ينجح فيه الـ Recomposition وتتطبق التغييرات على الشاشة، وبنستخدمها لمزامنة حالة كومبوز مع مكتبة تحليلات خارجية أو كود جافا تقليدي.",
        "deep_answer_ar": "تحت الكابوت، الأدوات الأربعة بتتصل مباشرة بنظام إدارة الـ RecomposeScope والـ SlotTable في رنتايم كومبوز.\n\nفي `LaunchedEffect`، الرنتايم بيحجز Slot لتخزين كائن الكوروتين الحالي والـ Keys المرتبطة بيه. لما الـ Keys تتغير، الكومبايلر بيستدعي `Job.cancel()` للعملية القديمة، وبيطلق كوروتين جديد على الـ CoroutineContext المناسب. ولو النود اتلغت من الشجرة، الرنتايم بيلغي الـ Job فوراً.\n\nأما في `DisposableEffect`، الرنتايم بيسجل كائن `DisposableEffectScope`. الضمان الهندسي الأقوى هنا هو إن محرك كومبوز بيضمن استدعاء `onDispose()` في حالتين فقط لا ثالث لهما: إما قبل إعادة تنفيذ التأثير بمفاتيح جديدة، أو لما النود تتم إزالتها نهائياً من الـ Composition Tree. ووجود `onDispose` إلزامي والكومبايلر بيرفض يكمل لو نسيته.\n\nفي `SideEffect`، الآلية مختلفة تماماً؛ الدالة مش بتنشئ كوروتين، بل بتضيف الـ Lambda في طابور انتظار مؤجل بنسميه 'قائمة الآثار الجانبية المعلقة' (Pending Side-effects Queue). الميزة العبقرية لده هي إنه لو الـ Recomposition الحالي تم إلغاؤه في المنتصف بسبب وصول حالة أحدث، الرنتايم بيمسح الطابور ده تماماً بدون ما ينفذه! وده بيضمن إن كود الـ SideEffect عمره ما هيتنفذ إلا لو التغييرات اتطبقت فعلياً ونجحت على الشاشة.\n\nوأخيراً `rememberCoroutineScope` بيوفر CoroutineScope مربوط بـ `CompositionContext` الحالي؛ أول ما الشاشة تتدمر، الرنتايم بينادي `cancel()` للـ Job التابع للـ Scope ده، وده بيضمن إن ضغطات الأزرار والعمليات المؤقتة متفضلش شغالة في الخلفية بعد موت الشاشة."
    }
}


def main():
    print(f"Elevating 10 questions in COM (COM-01 to COM-10)...")
    all_valid = True
    for qid, d in sorted(DATA.items()):
        if d is None:
            continue
        en_s = len(d["short_en"].split())
        en_st = len(d["structured_en"].split())
        en_d = len(d["deep_senior_en"].split())
        ar_q = len(d["meta_ar"]["quick_answer_ar"].split())
        ar_b = len(d["meta_ar"]["best_answer_ar"].split())
        ar_d = len(d["meta_ar"]["deep_answer_ar"].split())
        print(f"{qid}: en_s={en_s}, en_st={en_st}, en_d={en_d} | ar_q={ar_q}, ar_b={ar_b}, ar_d={ar_d}")

        if not (35 <= en_s <= 110):
            print(f"  ❌ {qid} en_short invalid: {en_s}")
            all_valid = False
        if not (100 <= en_st <= 280):
            print(f"  ❌ {qid} en_structured invalid: {en_st}")
            all_valid = False
        if not (200 <= en_d <= 650):
            print(f"  ❌ {qid} en_deep invalid: {en_d}")
            all_valid = False
        if not (35 <= ar_q <= 110):
            print(f"  ❌ {qid} ar_quick invalid: {ar_q}")
            all_valid = False
        if not (90 <= ar_b <= 280):
            print(f"  ❌ {qid} ar_best invalid: {ar_b}")
            all_valid = False
        if not (180 <= ar_d <= 650):
            print(f"  ❌ {qid} ar_deep invalid: {ar_d}")
            all_valid = False

    if not all_valid:
        print("\nPre-validation word count checks failed! Fix counts before updating files.")
        sys.exit(1)

    print("\nPre-validation word count checks passed! Updating canonical questions...")

    topic_meta = {}
    for qid, d in sorted(DATA.items()):
        if d is None:
            continue
        ee.update_canonical_question(
            qid=qid,
            concept_en=d["concept_en"],
            walkthrough_en=d["walkthrough_en"],
            short_en=d["short_en"],
            structured_en=d["structured_en"],
            deep_senior_en=d["deep_senior_en"]
        )
        topic_meta[qid] = d["meta_ar"]

    ee.save_topic_metadata("com_01_10", topic_meta)
    ee.merge_all_metadata()

    # Validate each question
    for qid in sorted(DATA.keys()):
        if DATA[qid] is None:
            continue
        ee.validate_question(qid)

    print("\nAll 10 COM questions (COM-01 to COM-10) successfully elevated and passed validation!")


if __name__ == "__main__":
    main()

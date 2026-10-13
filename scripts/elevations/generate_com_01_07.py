#!/usr/bin/env python3
"""Generator for COM-01 through COM-07 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "com.json"

COM_01_07 = [
    {
        "id": "COM-01",
        "arabic_explanation": (
            "المقارنة الجوهرية بين النموذج الإعلاني (Declarative) في Jetpack Compose والنموذج الأمري (Imperative) في XML Views:\n\n"
            "1. كيف تعمل واجهات XML التقليدية (Imperative Model)؟\n"
            "   - في نظام الـ Views، الشاشة عبارة عن شجرة كائنات ذات حالة داخلية متغيرة (`View Hierarchy`).\n"
            "   - المطور مسؤول عن مزامنة الحالة يدوياً: العثور على العنصر (`findViewById` أو `ViewBinding`) ثم تغيير خصائصه برمجياً (`textView.text = ...`, `progressBar.visibility = GONE`).\n"
            "   - العيب القاتل: حدوث **تضارب الحالة (State Inconsistency)**؛ مثل أن ينسى المطور إخفاء الـ ProgressBar في سيناريو الـ Error، فيظهر لودينج لا نهائي مع رسالة خطأ!\n\n"
            "2. كيف يعمل Jetpack Compose (Declarative Model)؟\n"
            "   - في Compose، الواجهة عبارة عن دوال برمجية بسيطة تصف كيف تبدو الشاشة بناءً على الحالة الحالية: `UI = f(State)`.\n"
            "   - لا توجد كائنات View ممسوكة في الذاكرة لتعديلها يدوياً؛ عندما تتغير الـ State، يقوم محرك Compose بإعادة تشغيل الدوال المتأثرة تلقائياً فيما يُعرف بـ **Recomposition**.\n"
            "   - هذا يضمن استحالة حدوث State Desync، لأن الواجهة هي انعكاس رياضي مباشر وحتمي للبيانات.\n\n"
            "3. الفروق المعمارية على مستوى الأداء والكود:\n"
            "   - **Kotlin بنسبة 100%**: التخلص من طبقة ترجمة XML المعقدة وتكرار الـ Attributes.\n"
            "   - **Flattened Layout Tree**: لا توجد قيود الـ Nested Layouts التي كانت تتطلب قياسات مزدوجة (Double Taxation) في Views، بل يفرض Compose نظام Single-Pass Measure."
        ),
        "practical_walkthrough": (
            "مقارنة عملية بين XML التقليدي و Jetpack Compose في التعامل مع حالات التحميل والبيانات:\n"
            "```kotlin\n"
            "// ❌ في نظام XML التقليدي: تعديل أمري عرضة لتضارب الحالات:\n"
            "fun renderState(state: UiState) {\n"
            "    when (state) {\n"
            "        is UiState.Loading -> {\n"
            "            binding.progressBar.visibility = View.VISIBLE\n"
            "            binding.textView.visibility = View.GONE // إذا نسيت هذا السطر يظل النص القديم ظاهراً!\n"
            "        }\n"
            "        is UiState.Success -> {\n"
            "            binding.progressBar.visibility = View.GONE\n"
            "            binding.textView.visibility = View.VISIBLE\n"
            "            binding.textView.text = state.data\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ في Jetpack Compose: وصف تصريحي حتمي، يستحيل معه تضارب الحالة:\n"
            "@Composable\n"
            "fun UserProfileScreen(uiState: UiState) {\n"
            "    when (uiState) {\n"
            "        is UiState.Loading -> CircularProgressIndicator()\n"
            "        is UiState.Success -> Text(text = uiState.data)\n"
            "        is UiState.Error -> Text(text = uiState.message, color = MaterialTheme.colorScheme.error)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "XML Views are imperative and stateful: developers manually mutate mutable view hierarchies via `findViewById`/`ViewBinding`, often causing state desynchronization. Jetpack Compose is declarative: UI is a pure function of state (`UI = f(State)`), written entirely in Kotlin, where state mutations automatically trigger targeted recomposition of affected nodes.",
        "best_answer": (
            "The architectural shift from XML to Jetpack Compose is a paradigm transition from imperative view mutation to declarative state projection.\n\n"
            "In legacy Android Views, UI widgets are stateful objects maintaining their own internal state. To update a screen, developers write imperative glue code to look up views and mutate properties—calling `setText()`, `setVisibility()`, or animating frames. "
            "Because data sources and UI widgets hold separate copies of state, screens frequently suffer from **state desynchronization bugs** (e.g. a spinner running while content is already displayed).\n\n"
            "Jetpack Compose replaces mutable view objects with composable functions that describe the UI as a direct projection of data: **`UI = f(State)`**. "
            "When state updates, Compose's runtime executes **Recomposition**, intelligently re-running only the composables that observe the modified state while skipping unchanged nodes. "
            "It is 100% Kotlin, eliminating XML attribute boilerplate, supporting compile-time safety, and enforcing a single-pass measurement model that eradicates layout nesting penalties."
        ),
        "deep_answer": (
            "Under the hood, Compose eliminates the overhead of `View` and `ViewGroup` objects. A traditional `View` class inherits over 80 fields and thousands of lines of legacy layout logic. "
            "In Compose, `@Composable` functions emit nodes into an in-memory **Slot Table** managed by the Compose Compiler and Runtime (`androidx.compose.runtime`). "
            "The compiler augments composable functions with a synthetic `$composer` parameter, recording call hierarchy, state reads, and memoized values.\n\n"
            "Regarding layout passes: Android Views often perform multi-pass measurements (such as `RelativeLayout` or nested weights in `LinearLayout`), leading to $O(2^n)$ measurement complexity. "
            "Compose strictly enforces that no node in the UI tree can be measured more than once per layout pass (`Single-Pass Measurement`), while providing **Intrinsic Measurements** when children need to negotiate sizes before full measurement.\n\n"
            "Interoperability is seamless: legacy code embeds Compose via `ComposeView`, while Compose embeds legacy views using `AndroidView`, enabling low-risk incremental migration."
        ),
        "follow_ups": [
            {
                "question": "What is the Compose Slot Table and how does it manage composition state?",
                "answer": "The Slot Table is Compose's internal continuous array data structure. It stores composable call groups, parameters, and `remember` values sequentially. During recomposition, the runtime walks the slot table using a gap buffer algorithm, updating changed slots and reusing unchanged results."
            },
            {
                "question": "Why does Compose enforce single-pass measurement?",
                "answer": "Single-pass measurement guarantees that UI tree traversal scales linearly $O(n)$ with the number of nodes, preventing exponential layout calculation slowdowns caused by deeply nested layouts in legacy XML views."
            }
        ]
    },
    {
        "id": "COM-02",
        "arabic_explanation": (
            "ما هي دالة `@Composable` وما هو مفهوم الـ Recomposition؟\n\n"
            "1. طبيعة الـ `@Composable Annotation`:\n"
            "   - الـ `@Composable` ليس مجرد وسم شكلي (Annotation)، بل هو **مغير نوع للغة كوتلن (Type modifier)** يفهمه الـ Compose Compiler Plugin.\n"
            "   - تماماً كما أن كلمة `suspend` تغير توقيع الدالة وتمرر `Continuation`، فإن `@Composable` تجبر المترجم على حقن بارامتر خفي اسمه `$composer` داخل الدالة وتغيير نوعها لتصبح صالحة للاستدعاء فقط من داخل دوال `@Composable` أخرى.\n\n"
            "2. ما هي الـ Recomposition (إعادة التركيب)؟\n"
            "   - هي العملية التي يقوم فيها محرك Compose بإعادة تشغيل (Re-executing) دوال الـ Composable عندما تتغير البيانات أو الحالات (`State`) التي تقرأها تلك الدوال.\n"
            "   - الهدف: تحديث شجرة العرض بما يتطابق مع الحالة الجديدة.\n\n"
            "3. القواعد الذهبية للـ Recomposition التي يجب أن يعيها مهندس الـ Senior:\n"
            "   - **Recomposition is Optimistic**: قد يبدأ Compose إعادة التركيب، وإذا تغيرت الحالة مجدداً قبل اكتمال الفريم، يلغي العملية ويعيدها بالحالة الأحدث.\n"
            "   - **Executes in Any Order**: لا تضمن ترتيب تنفيذ دوال الـ Composable؛ قد تعمل بالتوازي.\n"
            "   - **Side-Effect Free**: يجب ألا تحتوي دالة الـ Composable على أي Side Effects (مثل استدعاء شبكة، أو تعديل متغير عام، أو تشغيل صوت) خارج الـ Effect APIs المخصصة (`LaunchedEffect` / `SideEffect`)."
        ),
        "practical_walkthrough": (
            "كيف يؤدي كود يحتوي على Side-Effect داخل دالة Composable إلى كوارث أداء وكيفية علاجه:\n"
            "```kotlin\n"
            "// ❌ كود كارثي: تشغيل Side-Effect مباشرة داخل جسم الـ Composable:\n"
            "@Composable\n"
            "fun BadUserCounter(count: Int) {\n"
            "    // 💥 كارثة: في كل مرة يعاد فيها رسم الشاشة (Recomposition)، يتم إرسال طلب تحليلات جديد!\n"
            "    AnalyticsTracker.logEvent(\"screen_viewed\")\n"
            "\n"
            "    Text(text = \"Count: $count\")\n"
            "}\n"
            "\n"
            "// ✅ كود سليم: عزل الـ Side-Effects داخل Effect Handlers المخصصة:\n"
            "@Composable\n"
            "fun GoodUserCounter(count: Int) {\n"
            "    // يتم استدعاؤه مرة واحدة فقط عند دخول الـ Composable لأول مرة:\n"
            "    LaunchedEffect(Unit) {\n"
            "        AnalyticsTracker.logEvent(\"screen_viewed\")\n"
            "    }\n"
            "\n"
            "    Text(text = \"Count: $count\")\n"
            "}\n"
            "```"
        ),
        "quick_answer": "A `@Composable` function is a Kotlin function transformed by the Compose compiler to emit UI nodes into the composition tree. Recomposition is the process where Compose re-executes composables whose observed `State` has changed to produce updated UI, skipping unchanged composables intelligently.",
        "best_answer": (
            "A `@Composable` annotation transforms a Kotlin function at compile time. Much like the `suspend` keyword modifies a function's calling convention to inject a `Continuation`, `@Composable` modifies the function type to inject a `$composer` parameter and runtime control structures.\n\n"
            "**Recomposition** is the core reactive mechanism of Jetpack Compose. When a snapshot `State` object read within a composable changes its value, the Compose runtime invalidates that specific scope in the **Slot Table** and re-executes the composable function to produce updated UI nodes.\n\n"
            "Three critical operational rules govern recomposition:\n"
            "1. **Idempotency & Purity**: Composables must be free of side-effects because recomposition can execute on every single frame during animations.\n"
            "2. **Parallel & Arbitrary Order**: Composables may run concurrently on background thread pools or in arbitrary order.\n"
            "3. **Optimistic Cancellation**: If state updates again while recomposition is underway, Compose discards the pending pass and restarts with the fresh state."
        ),
        "deep_answer": (
            "Under the hood, the Compose Compiler generates synthetic bytecode called **Restartable and Replaceable Groups**. "
            "A composable marked with `@Composable` is wrapped in `$composer.startRestartGroup()` and `$composer.endRestartGroup()`. "
            "The returned scope implements `RecomposeScopeImpl`, which registers itself as an observer of snapshot state reads.\n\n"
            "When you read `state.value` inside a composable, the `Snapshot` system records that read against the active `RecomposeScope`. "
            "When `state.value = newValue` is assigned, the snapshot system marks that `RecomposeScope` as dirty and dispatches an invalidation to the Choreographer frame loop.\n\n"
            "If all parameters passed to a composable are known to be **Stable** and have not changed by `equals()` comparison, Compose skips executing the function body entirely (`Skipping`), which is why understanding Compose compiler stability is fundamental to fluid 120fps performance."
        ),
        "follow_ups": [
            {
                "question": "Can a composable function run on a background thread during recomposition?",
                "answer": "Yes. While Compose dispatches UI node mutations on the main thread, the actual execution and calculation of composable function logic can be executed across thread pools, meaning composable bodies must never read or write non-thread-safe state."
            },
            {
                "question": "What happens if a composable is recomposed 60 times per second during an animation?",
                "answer": "If the function is pure, it recalculates UI values smoothly. But if it performs allocations, IO, or side-effects, it triggers immediate memory churn, GC pauses, and dropped frames."
            }
        ]
    },
    {
        "id": "COM-03",
        "arabic_explanation": (
            "ما الذي يطلق الـ Recomposition (Triggers) وما الذي يمكن للـ Runtime تخطيه (Skipping)؟\n\n"
            "1. ما الذي يُطلق الـ Recomposition؟\n"
            "   - **قراءة Snapshot State معدلة**: إذا قرأت دالة Composable قيمة `State<T>` (مثل `mutableStateOf` أو `StateFlow.collectAsStateWithLifecycle`) ثم تغيرت هذه القيمة.\n"
            "   - **تغير البارامترات الممررة (Parameter Changes)**: إذا تم استدعاء الـ Composable بقيم بارامترات جديدة تختلف عن القيم السابقة.\n\n"
            "2. ما هو التخطي الذكي (Smart Skipping)؟\n"
            "   - عندما يُعاد تركيب دالة أب (Parent Composable)، يفحص Compose كل الدوال الفرعية (Children).\n"
            "   - إذا كانت جميع بارامترات الدالة الفرعية **مستقرة (Stable)** ولم تتغير قيمتها (حسب مقارنة `equals()`)، ولم تقرأ الدالة أي State معدلة، يقوم محرك Compose بـ **تخطي (Skip)** استدعاء الدالة الفرعية تماماً!\n\n"
            "3. لماذا تفشل بعض الدوال في التخطي وتُعاد بدون داعٍ؟\n"
            "   - **أنواع غير مستقرة (Unstable Types)**: مثل مجموعات كوتلن القياسية `List<T>`, `Set<T>`, `Map<T>` (لأن المترجم لا يضمن أنها غير قابلة للتعديل `MutableList`).\n"
            "   - **كائنات عادية بدون `@Immutable` أو `@Stable`**: إذا كان الكلاس يحتوي على `var` أو كان معرفاً في مكتبة خارجية غير مجمعة بواسطة Compose Compiler.\n"
            "   - **Lambdas تلتقط متغيرات غير مستقرة**."
        ),
        "practical_walkthrough": (
            "كود يوضح الفرق بين دالة يمكن تخطيها ودالة يُعاد تركيبها دائماً بسبب `List` غير مستقرة:\n"
            "```kotlin\n"
            "// ❌ دالة تفشل في الـ Skipping بسبب استخدام List<String> القياسية:\n"
            "@Composable\n"
            "fun UnskippableUserList(users: List<String>, onUserClick: (String) -> Unit) {\n"
            "    // Compose Compiler يعتبر List نوعاً Unstable، لذا يُعاد تنفيذ هذه الدالة في كل recomposition للأب!\n"
            "    LazyColumn {\n"
            "        items(users) { user ->\n"
            "            Text(text = user, modifier = Modifier.clickable { onUserClick(user) })\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ دالة مستقرة تقبل التخطي (Skippable) باستخدام ImmutableList:\n"
            "import kotlinx.collections.immutable.ImmutableList\n"
            "\n"
            "@Composable\n"
            "fun SkippableUserList(users: ImmutableList<String>, onUserClick: (String) -> Unit) {\n"
            "    // هنا يعلم المترجم أن users مستقرة تماماً، فإذا لم تتغير القائمة، يتم تخطي الدالة 100%:\n"
            "    LazyColumn {\n"
            "        items(users) { user ->\n"
            "            Text(text = user, modifier = Modifier.clickable { onUserClick(user) })\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Recomposition is triggered when a composable reads a `State` object whose value changes, or when its parent recomposes with updated parameters. A composable can be skipped if all its arguments are `Stable` and structurally equal to their previous values, and no observed internal states have changed.",
        "best_answer": (
            "Recomposition triggers strictly through state reads and parameter mutations.\n\n"
            "1. **The Trigger**: The Compose snapshot system observes which `State<T>` objects are read within each `RecomposeScope`. When an assignment occurs on a state property, all scopes that registered a read for that property are scheduled for recomposition.\n\n"
            "2. **Smart Skipping**: During a recomposition pass of a parent composable, Compose inspects child composables. A child composable is **skipped** if and only if:\n"
            "   - The composable is marked **restartable** and **skippable** by the Compose Compiler.\n"
            "   - All parameters passed to the function are **Stable**.\n"
            "   - None of the parameter values have changed according to their `equals()` implementation.\n\n"
            "If a single parameter is inferred as **Unstable** (such as standard Kotlin `List<T>`, collections, or classes containing `var` properties), Compose cannot guarantee that the object's contents haven't changed behind its back. "
            "Consequently, the compiler forces the child to recompose every single time the parent recomposes, degrading performance."
        ),
        "deep_answer": (
            "The Compose Compiler classifies types into three stability categories: **Immutable** (all public properties are `val` of primitive or immutable types; will never change), **Stable** (may mutate, but notifies the composition when mutations occur via snapshot state), and **Unstable** (may mutate without notifying Compose).\n\n"
            "With the introduction of the **Strong Skipping Mode** in recent Compose compiler releases (enabled by default in Kotlin 2.0+), Compose became significantly smarter: composables with unstable parameters can now be skipped if the instance reference has not changed (`===`), and lambdas with captures are automatically memoized using `remember`.\n\n"
            "To audit stability in production apps, we enable Compose Compiler Metrics (`reportsDestination`). "
            "The generated reports categorize every composable as `skippable` or `restartable only`, and pinpoint exact unstable parameters (e.g. `unstable users: List<User>`), guiding us to wrap them in Kotlinx `ImmutableList` or annotate models with `@Immutable`."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between restartable and skippable in Compose Compiler metrics?",
                "answer": "A restartable composable can act as a RecomposeScope boundary to re-execute when its internal states change. A skippable composable can be completely bypassed when called by a recomposing parent if its parameters haven't changed."
            },
            {
                "question": "How did Strong Skipping Mode change Compose behavior for lambdas?",
                "answer": "Before Strong Skipping, lambdas capturing variables were re-instantiated on every composition pass, causing child composables to receive a new instance and fail skipping. Strong Skipping wraps these lambdas in `remember`, stabilizing their references across recompositions."
            }
        ]
    },
    {
        "id": "COM-04",
        "arabic_explanation": (
            "مفاهيم الـ State والـ Snapshot State ورفع الحالة (State Hoisting) في Jetpack Compose:\n\n"
            "1. ما هو الـ State في Compose؟\n"
            "   - الـ State هو أي قيمة متغيرة تؤثر على ما يراه المستخدم على الشاشة (مثل نص في حقل إدخال، حالة لودينج، قائمة رسائل).\n"
            "   - في Compose، لا نستخدم متغيرات عادية `var count = 0`، لأن محرك Compose لا يمكنه تتبع قراءتها أو تعديلها.\n"
            "   - نستخدم **`SnapshotState`** عبر `mutableStateOf(value)`؛ وهو غلاف تفاعلي يُشعر نظام Compose بلحظات القراءة والكتابة.\n\n"
            "2. كيف يعمل الـ Snapshot State داخلياً؟\n"
            "   - مستوحى من نظام قواعد البيانات متعددة النسخ (MVCC - Multi-Version Concurrency Control).\n"
            "   - عندما يُقرأ الـ State، يُسجل الـ Snapshot System أن الـ Composable الفلاني يراقب هذه القيمة.\n"
            "   - عند تعديل القيمة، يُنشئ الـ Snapshot نسخة جديدة ويطلق إشعار Invalidation للنطاقات المراقبة فقط.\n\n"
            "3. ما هو رفع الحالة (State Hoisting)؟\n"
            "   - هو نمط معماري لنقل الـ State للأعلى إلى الدالة المستدعية (Caller) لجعل الـ Composable **عديم الحالة (Stateless)**.\n"
            "   - النمط القياسي: استبدال المتغير الداخلي ببارامترين:\n"
            "     * `value: T` (القيمة الحالية للعرض).\n"
            "     * `onValueChange: (T) -> Unit` (حدث يُطلق عندما يطلب المستخدم التغيير).\n"
            "   - الفوائد: سهولة إعادة استخدام المكون، قابلية الاختبار بنسبة 100% دون حاجة لمحاكاة Compose Runtime، و Single Source of Truth."
        ),
        "practical_walkthrough": (
            "تطبيق نمط State Hoisting لتحويل مكون Stateful إلى Stateless قابل لإعادة الاستخدام والاختبار:\n"
            "```kotlin\n"
            "// ❌ مكون يحتفظ بحالته داخلياً (Stateful): يصعب اختباره وإعادة استخدامه في شاشات أخرى:\n"
            "@Composable\n"
            "fun StatefulSearchField() {\n"
            "    var query by remember { mutableStateOf(\"\") }\n"
            "    TextField(value = query, onValueChange = { query = it })\n"
            "}\n"
            "\n"
            "// ✅ تطبيق State Hoisting: فصل القيمة عن الأحداث (Stateless Composable):\n"
            "@Composable\n"
            "fun StatelessSearchField(\n"
            "    query: String,\n"
            "    onQueryChanged: (String) -> Unit,\n"
            "    modifier: Modifier = Modifier\n"
            ") {\n"
            "    TextField(\n"
            "        value = query,\n"
            "        onValueChange = onQueryChanged,\n"
            "        placeholder = { Text(\"Search products...\") },\n"
            "        modifier = modifier\n"
            "    )\n"
            "}\n"
            "```"
        ),
        "quick_answer": "State in Compose is any dynamic data driving the UI. Snapshot state (`mutableStateOf`) enables Compose's runtime to track reads and writes for precise recomposition. State Hoisting is the architectural pattern of moving state up to make child composables stateless, parameterized by `value: T` and `onValueChange: (T) -> Unit`.",
        "best_answer": (
            "In Jetpack Compose, state is the single source of truth that dictates visual rendering.\n\n"
            "To make state observable to the Compose runtime, we wrap it in a **Snapshot State**—typically created via `mutableStateOf(initialValue)`. "
            "Compose's snapshot system tracks reads during the execution of composables. Whenever a write occurs on that state, the runtime schedules recomposition exclusively for the scopes that read that specific value, achieving highly granular updates.\n\n"
            "**State Hoisting** is the foundational architectural pattern for building modular, robust Compose UI. "
            "Instead of letting a component manage its own internal state (making it *stateful* and tightly coupled), we hoist the state up to its caller by replacing it with two parameters:\n"
            "1. The current state representation: `value: T`\n"
            "2. An event lambda: `onValueChange: (T) -> Unit`\n\n"
            "This transforms the composable into a **stateless component**, making it trivial to preview in Android Studio, share across different navigation screens, and verify in isolated unit and screenshot tests."
        ),
        "deep_answer": (
            "Under the hood, `mutableStateOf` relies on Android's global `Snapshot` system (`androidx.compose.runtime.snapshots`). "
            "The snapshot system functions like software transactional memory (STM) or Git: each thread or composition operates in an isolated snapshot of state. "
            "When a state mutation is performed, the modified records are committed to the global snapshot, which broadcasts invalidation notifications to all active `SnapshotStateObserver` instances.\n\n"
            "When architecting production applications, state hoisting operates across three distinct levels:\n"
            "1. **Component-level hoisting**: Hoisting basic input values (text fields, checkboxes) into immediate parents.\n"
            "2. **Screen-level UI State Holder**: Hoisting complex widget coordination (like custom scroll interactions and animation sync) into an unmanaged plain Kotlin class (e.g. `rememberSearchState()`).\n"
            "3. **Business-level hoisting**: Hoisting domain and repository operations into an architecture-level `ViewModel` exposing `StateFlow<UiState>`."
        ),
        "follow_ups": [
            {
                "question": "What happens if you update a normal Kotlin `var` inside a Composable without `mutableStateOf`?",
                "answer": "The variable value changes in memory, but Compose runtime has no observation mechanism on standard JVM properties. No recomposition is scheduled, and the screen remains frozen showing the old value."
            },
            {
                "question": "What is the difference between a Stateful and Stateless composable in design systems?",
                "answer": "A Stateless composable exposes pure inputs and outputs via parameters and callbacks, ideal for reusable UI design systems. A Stateful composable acts as an orchestration container that owns or manages state for a specific feature screen."
            }
        ]
    },
    {
        "id": "COM-05",
        "arabic_explanation": (
            "المقارنة الشاملة بين `remember` و `rememberSaveable` وحالة الـ `ViewModel` ومتى تستخدم كلاً منها:\n\n"
            "1. دالة `remember { ... }`:\n"
            "   - **نطاق البقاء (Lifetime)**: تعيش فقط طالما أن الـ Composable موجود داخل شجرة الـ Composition.\n"
            "   - **ما تحميه**: تحمي القيمة من الضياع أثناء **Recomposition** العادي.\n"
            "   - **ما تفقده**: تُفقد وتُعاد تهيئتها بالكامل عند **تغيير اتجاه الشاشة (Configuration Change)** أو موت العملية (Process Death) أو مغادرة الشاشة في الـ Navigation.\n"
            "   - **الاستخدام المثالي**: العمليات الحسابية المؤقتة للـ UI، كائنات التنسيق `remember { SimpleDateFormat(...) }`، وحالات الرسوم المتحركة المؤقتة.\n\n"
            "2. دالة `rememberSaveable { ... }`:\n"
            "   - **نطاق البقاء**: تعيش عبر الـ Recomposition **وتنجو أيضاً من Configuration Change وموت العملية (Process Death)**!\n"
            "   - **كيف تعمل**: تخزن البيانات في `SavedStateHandle` / `Bundle` الخاص بالنظام، وتشترط أن تكون البيانات قابلة للـ Serialization (مثل Primitives أو Parcelable أو عبر Custom Saver).\n"
            "   - **الاستخدام المثالي**: مدخلات المستخدم غير المحفوظة في السيرفر (نص مسودة في حقل بحث، موضع التمرير المحدد، رقم التبويب النشط).\n\n"
            "3. حالة الـ `ViewModel` (`StateFlow` / `SavedStateHandle`):\n"
            "   - **نطاق البقاء**: تعيش طوال فترة بقاء الشاشة في الـ BackStack، وتنجو من Configuration Change بالكامل، وتنجو من Process Death عبر `SavedStateHandle`.\n"
            "   - **الاستخدام المثالي**: حالة العمل الحقيقية للتطبيق (Business State)، استجابات الشبكة، بيانات المستخدم، وقواعد التحقق."
        ),
        "practical_walkthrough": (
            "أمثلة توضح متى نستخدم كل آلية في شاشة تطبيق حقيقية:\n"
            "```kotlin\n"
            "@Composable\n"
            "fun CheckoutScreen(viewModel: CheckoutViewModel = viewModel()) {\n"
            "    // 1. ViewModel State: بيانات الـ Business والـ Backend تنجو من التدوير والـ Navigation:\n"
            "    val uiState by viewModel.uiState.collectAsStateWithLifecycle()\n"
            "\n"
            "    // 2. rememberSaveable: حالة واجهة مستخدم خاصة بالشاشة تنجو من تدوير الهاتف وموت العملية:\n"
            "    var promoCodeInput by rememberSaveable { mutableStateOf(\"\") }\n"
            "\n"
            "    // 3. remember: كائن مؤقت خاص بالرسم أو الحسابات يضيع عند التدوير ويعاد إنشاؤه بسهولة:\n"
            "    val currencyFormatter = remember(Locale.getDefault()) {\n"
            "        NumberFormat.getCurrencyInstance(Locale.getDefault())\n"
            "    }\n"
            "\n"
            "    CheckoutContent(\n"
            "        total = currencyFormatter.format(uiState.totalAmount),\n"
            "        promoCode = promoCodeInput,\n"
            "        onPromoChange = { promoCodeInput = it }\n"
            "    )\n"
            "}\n"
            "```"
        ),
        "quick_answer": "`remember` preserves state across recompositions but resets on configuration change. `rememberSaveable` survives configuration change and process death by persisting values into the Android `Bundle`. ViewModel state outlives configuration change and hosts business logic, persisting across backstack navigation until the screen is permanently destroyed.",
        "best_answer": (
            "Choosing between `remember`, `rememberSaveable`, and `ViewModel` depends strictly on lifecycle scope and state ownership.\n\n"
            "1. **`remember`**: Retains an object in the Slot Table across **recomposition passes** as long as the composable remains in the composition tree. However, it is wiped on configuration changes (screen rotations) and process death. It is designed for ephemeral UI calculations, such as expensive formatting objects, scroll state listeners, or animation progress.\n\n"
            "2. **`rememberSaveable`**: Preserves state across recomposition *and* **configuration changes and system-initiated process death**. It automatically serializes data into the Android `Bundle` using a `Saver` implementation. It is ideal for transient, UI-only user input like uncommitted text fields, active tab indexes, or accordion expansion states.\n\n"
            "3. **ViewModel State**: Scoped to the `ViewModelStoreOwner` (surviving configuration changes and backstack journeys). It holds business state, coordinates with repositories and network layers, and survives process death when paired with `SavedStateHandle`. Business logic and server-driven state should always reside here."
        ),
        "deep_answer": (
            "Under the hood, `rememberSaveable` delegates to Compose's `SaveableStateRegistry`. "
            "When the OS destroys an Activity to reclaim memory, `SaveableStateRegistry` collects registered values into the saved instance state Bundle. "
            "If you store custom data classes inside `rememberSaveable`, you must provide a custom `Saver` (e.g. `listSaver` or `mapSaver`) or mark the class `@Parcelize Parcelable`; storing non-parcelable types crashes at runtime with an `IllegalArgumentException`.\n\n"
            "Conversely, storing everything in the `ViewModel` is an anti-pattern known as *State Bloat*. "
            "Fine-grained UI behaviors (like whether a tooltip is currently visible or an animation state) clutter the domain model and break composable encapsulation. "
            "Senior architects establish a clean boundary: pure UI transient state stays in `remember`/`rememberSaveable`, while actionable domain data belongs in the ViewModel."
        ),
        "follow_ups": [
            {
                "question": "What happens if you put a non-Parcelable object into `rememberSaveable`?",
                "answer": "It will work during normal recomposition, but as soon as a configuration change or process death triggers state saving into the Android Bundle, the app crashes with an `IllegalArgumentException: ... cannot be saved using the current SaveableStateRegistry`."
            },
            {
                "question": "How do you create a custom Saver for a non-Parcelable class?",
                "answer": "Using `listSaver(save = { listOf(it.id, it.name) }, restore = { MyClass(it[0], it[1]) })` or `mapSaver`, defining explicit serialization and deserialization steps into supported primitive types."
            }
        ]
    },
    {
        "id": "COM-06",
        "arabic_explanation": (
            "مفهوم تدفق البيانات أحادي الاتجاه (Unidirectional Data Flow - UDF) في Jetpack Compose:\n\n"
            "1. ما هو تدفق البيانات أحادي الاتجاه (UDF)؟\n"
            "   - هو نمط تصميم هيكلي يدور فيه تدفق البيانات والتفاعل في **حلقة مغلقة ذات اتجاه واحد لا ينعكس أبداً**:\n"
            "     * **State Flows Down**: الحالة والبيانات تتدفق دائماً من الأعلى إلى الأسفل (من ViewModel إلى الشاشات ومنها للمكونات الفرعية كـ Parameters).\n"
            "     * **Events Flow Up**: الأحداث وتفاعلات المستخدم (Taps, Text Input) تتدفق دائماً من الأسفل إلى الأعلى (من المكونات الفرعية إلى الـ ViewModel كـ Lambdas).\n\n"
            "2. لماذا يعتبر UDF حجر الأساس في Compose؟\n"
            "   - **فصل المسؤوليات (Separation of Concerns)**: مكونات الواجهة تقتصر مهمتها على رسم ما يُعطى لها فقط دون التفكير في كيفية جلب البيانات أو تعديلها.\n"
            "   - **مصدر وحيد للحقيقة (Single Source of Truth)**: لا يمكن لشاشتين أن تختلفا في البيانات المعروضة، لأن كلاهما يراقبان نفس الحالة المركزية في الـ ViewModel.\n"
            "   - **سهولة الاختبار الخارق (Testability)**: يمكنك اختبار الـ Composable بمجرد تمرير State وهمية والتأكد من إطلاق الـ Event المناسب عند النقر.\n\n"
            "3. الفرق بينه وبين التدفق ثنائي الاتجاه (Bi-directional Binding):\n"
            "   - في الأنظمة القديمة (مثل DataBinding بالاتجاهين)، كانت الواجهة تستطيع تغيير المتغير مباشرة، مما كان يسبب سباقات بيانات (Race Conditions) وتناقضات يصعب تصحيحها."
        ),
        "practical_walkthrough": (
            "تطبيق نمط UDF بشكل قياسي في شاشة Compose:\n"
            "```kotlin\n"
            "// 1. تمثيل الـ State كبيانات تتدفق للأسفل:\n"
            "data class CounterUiState(val count: Int = 0, val isMaxReached: Boolean = false)\n"
            "\n"
            "// 2. تمثيل الأحداث التي تتدفق للأعلى:\n"
            "sealed interface CounterEvent {\n"
            "    data object Increment : CounterEvent\n"
            "    data object Decrement : CounterEvent\n"
            "}\n"
            "\n"
            "// 3. المكون البصري: State Flows Down, Events Flow Up:\n"
            "@Composable\n"
            "fun CounterWidget(\n"
            "    state: CounterUiState,\n"
            "    onEvent: (CounterEvent) -> Unit,\n"
            "    modifier: Modifier = Modifier\n"
            ") {\n"
            "    Row(modifier = modifier, verticalAlignment = Alignment.CenterVertically) {\n"
            "        Button(onClick = { onEvent(CounterEvent.Decrement) }) { Text(\"-\") }\n"
            "        Text(text = \"Count: ${state.count}\", modifier = Modifier.padding(horizontal = 16.dp))\n"
            "        Button(\n"
            "            onClick = { onEvent(CounterEvent.Increment) },\n"
            "            enabled = !state.isMaxReached\n"
            "        ) { Text(\"+\") }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Unidirectional Data Flow (UDF) is the design pattern where State flows down from state holders to UI composables, and Events flow up from user interactions to state holders. This decouples visual rendering from business logic, establishes a single source of truth, and eliminates race conditions.",
        "best_answer": (
            "Unidirectional Data Flow (UDF) is the architectural backbone of Jetpack Compose.\n\n"
            "The principle dictates a strict single-direction communication cycle:\n"
            "1. **State Flows Down**: The state holder (typically an architecture-level `ViewModel`) maintains the immutable `StateFlow<UiState>`. The UI layer observes this state and passes concrete read-only properties down through the composable hierarchy.\n"
            "2. **Events Flow Up**: When a user interacts with the UI (tapping a button, entering text, pulling to refresh), the leaf composables do not mutate state directly. Instead, they emit callbacks and event lambdas up the tree to the state holder.\n"
            "3. **State Mutation**: The state holder processes the event (validating inputs, querying repositories), modifies its internal state, and emits a new immutable state snapshot, which flows back down to trigger recomposition.\n\n"
            "This pattern enforces a single source of truth, prevents state desynchronization, and makes UI components entirely decoupled and trivially testable."
        ),
        "deep_answer": (
            "Under the hood, UDF works synergistically with Compose's Snapshot system. "
            "Because composables simply consume immutable states and emit lambdas, they adhere to functional programming purity. "
            "This purity is what empowers the Compose compiler to perform intelligent skipping: if the state flowing down has not changed, the entire composable branch is bypassed during recomposition.\n\n"
            "Contrast this with legacy bi-directional data binding (`@={...}`), where UI components and underlying models mutated each other simultaneously. "
            "Bi-directional patterns frequently generated infinite update loops, layout thrashing, and difficult-to-reproduce race conditions when rapid asynchronous events arrived.\n\n"
            "In modern enterprise Android architectures, we formalize UDF using MVI (Model-View-Intent) or Android's official Architecture Guidance: modeling UI State as a sealed interface, UI Events as typed actions, and consuming them via `StateFlow` and `collectAsStateWithLifecycle()`."
        ),
        "follow_ups": [
            {
                "question": "How does UDF prevent infinite update loops in Jetpack Compose?",
                "answer": "Because child composables cannot mutate state directly, they cannot trigger recursive invalidations. State is mutated only in response to discrete events processed by the state holder, ensuring deterministic state transitions."
            },
            {
                "question": "Can a screen have multiple state holders while maintaining UDF?",
                "answer": "Yes. A screen typically has a business-logic ViewModel state holder for domain data, and one or more plain Kotlin class UI state holders (like `ScrollState` or `DrawerState`) for purely visual coordination."
            }
        ]
    },
    {
        "id": "COM-07",
        "arabic_explanation": (
            "ما هي الـ Modifiers في Jetpack Compose ولماذا يُعتبر ترتيب كتابتها (Ordering) حاسماً ومؤثراً على النتيجة؟\n\n"
            "1. ما هو الـ Modifier؟\n"
            "   - الـ `Modifier` هو كائن كوتلن يُستخدم لتخصيص سلوك ومظهر الـ Composable:\n"
            "   - يتحكم في: الحجم والأبعاد (`size`, `fillMaxWidth`)، المظهر والزخرفة (`background`, `border`, `clip`)، السلوك والتفاعل (`clickable`, `scrollable`)، والدلالات والوصول (`semantics`).\n\n"
            "2. لماذا يُعتبر ترتيب الـ Modifiers حاسماً؟\n"
            "   - في نظام Views القديم، كان لكل View خصائص مستقلة (Padding, Background, Margin) يحدد الـ View ترتيب تطبيقها داخلياً.\n"
            "   - في Compose، يتم تطبيق الـ Modifiers **تسلسلياً من اليسار إلى اليمين (ومن الأعلى إلى الأسفل)** بنظام السلسلة (Chaining).\n"
            "   - كل دالة modifier تغلف (wraps) الـ Layout Node أو التأثير الذي يليها، مما يعني أن تغيير ترتيب استدعاء دالتين يعطي نتيجة بصرية وسلوكية مختلفة كلياً!\n\n"
            "3. مثال شهير: الـ Padding والـ Clickable والـ Background:\n"
            "   - إذا وضعت `clickable` قبل `padding`، تكون منطقة النقر تشمل المساحة بالكامل.\n"
            "   - إذا وضعت `padding` قبل `clickable`، تصبح منطقة النقر مقتصرة على المحتوى الداخلي فقط بعد طرح الهوامش!\n"
            "   - لا يوجد مفهوم `margin` في Compose، لأن `margin` هو مجرد `padding` يوضع قبل `background`."
        ),
        "practical_walkthrough": (
            "توضيح عملي لكيفية تأثير الترتيب على مساحة الخلفية ومساحة النقر:\n"
            "```kotlin\n"
            "// ❌ الترتيب الأول: الخلفية والنقر يشملان فقط المحتوى الداخلي:\n"
            "Box(\n"
            "    modifier = Modifier\n"
            "        .padding(16.dp) // مسافة خارجية (تعمل كـ Margin)\n"
            "        .background(Color.Blue)\n"
            "        .clickable { /* ينقر فقط داخل المربع الأزرق */ }\n"
            ") {\n"
            "    Text(\"Blue with Margin\", color = Color.White)\n"
            "}\n"
            "\n"
            "// ✅ الترتيب الثاني: الخلفية والنقر يمتدان ليشملان كل شيء قبل الـ Padding الداخلي:\n"
            "Box(\n"
            "    modifier = Modifier\n"
            "        .background(Color.Blue) // يلون المساحة بالكامل\n"
            "        .clickable { /* Ripple يغطي المساحة كاملة */ }\n"
            "        .padding(16.dp) // مسافة داخلية (تعمل كـ Padding حقيقي)\n"
            ") {\n"
            "    Text(\"Blue with Content Padding\", color = Color.White)\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Modifiers configure a composable's size, layout, appearance, and gestures. Ordering matters strictly because modifier chains are applied sequentially from top to bottom; each modifier wraps the subsequent nodes. Swapping `padding` and `clickable`, or `padding` and `background`, changes touch target dimensions and visual bounds completely.",
        "best_answer": (
            "In Jetpack Compose, Modifiers are immutable objects that decorate or augment a composable's appearance, sizing, semantics, and gesture interactions.\n\n"
            "**Ordering is critical** because Compose processes modifier chains sequentially from outer to inner (top-to-bottom in code). Each modifier function wraps the remainder of the chain into a layout hierarchy node.\n\n"
            "This sequential execution manifests in everyday scenarios:\n"
            "1. **Padding vs Background**: Placing `.padding(16.dp)` *before* `.background(Color.Red)` acts like an outer margin, leaving the padded area uncolored. Placing `.background(Color.Red)` *before* `.padding(16.dp)` fills the entire box with red, creating inner content padding.\n"
            "2. **Clickable vs Padding**: Placing `.clickable { ... }` *before* `.padding(16.dp)` extends the touch target and ripple effect to the outer bounding box. Reversing them restricts the clickable touch target strictly to the inner unpadded bounds.\n\n"
            "Because of this chaining mechanism, Compose has no need for a distinct `margin` attribute; margins and paddings are merely positional applications of `.padding()`."
        ),
        "deep_answer": (
            "Under the hood, Compose modernized its modifier architecture with **Modifier.Node** (`androidx.compose.ui.node.ModifierNodeElement`). "
            "Earlier Compose versions allocated separate wrapper objects on every recomposition pass (`composed { ... }`), which created considerable allocation churn. "
            "Modern `Modifier.Node` separates modifier configuration from its long-lived runtime state, caching nodes in the LayoutNode tree and allowing properties to update without recreating graph nodes.\n\n"
            "When sizing modifiers are chained, layout constraints flow top-down while measured sizes flow bottom-up. "
            "For instance, chaining `.size(100.dp).size(50.dp)` results in a 100.dp widget because the first modifier imposes fixed constraints (min=100, max=100) that override downstream sizing modifiers unless explicitly bypassed using `requiredSize()`.\n\n"
            "As an API design best practice, every reusable composable should accept an optional `modifier: Modifier = Modifier` as its first optional parameter and apply it directly to its root layout element."
        ),
        "follow_ups": [
            {
                "question": "Why did Google migrate custom modifiers from `composed { ... }` to `Modifier.Node`?",
                "answer": "`composed { ... }` ran its composition lambda on every recomposition and couldn't be skipped by the compiler, creating heavy memory allocation and CPU overhead. `Modifier.Node` is lightweight, allocates once, and reuses instances across frames."
            },
            {
                "question": "What is the difference between `Modifier.size()` and `Modifier.requiredSize()`?",
                "answer": "`Modifier.size()` respects incoming parent constraints (e.g. will not exceed parent max bounds). `Modifier.requiredSize()` overrides incoming constraints completely, allowing the composable to draw at its specified size even if it overflows the parent layout."
            }
        ]
    }
]

def main() -> None:
    if DATA_FILE.exists():
        existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        by_id = {item["id"]: item for item in existing}
    else:
        by_id = {}

    for item in COM_01_07:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions COM-01 to COM-07. Total questions: {len(output)}")

if __name__ == "__main__":
    main()

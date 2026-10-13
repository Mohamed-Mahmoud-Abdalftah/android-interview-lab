#!/usr/bin/env python3
"""Generator for KOT-16 through KOT-22 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "kot.json"

KOT_16_22 = [
    {
        "id": "KOT-16",
        "arabic_explanation": (
            "المقارنة بين `List` و `MutableList` و `ArrayList` و `Sequence` بتكشف فهمك الحقيقي للـ Collections والـ Memory والـ API Design في Kotlin:\n\n"
            "1. `List<T>` (Read-Only Interface):\n"
            "   - في Kotlin، `List` هي **Read-Only Interface** وليست Immutable Collection بالمعنى الصارم. هي لا تحتوي على دوال تعديل (`add`, `remove`).\n"
            "   - **نقطة جوهرية:** الكائن الفعلي اللي في الـ Heap ممكن يكون `MutableList` متخفي وراء واجهة `List`. لو كود تاني معاه reference لنفس الكائن وعدل فيه، قراءتك هتتغير!\n"
            "   - علشان تضمن Immutability حقيقية، لازم تعمل defensive copy (زي `toList()` أو تستخدم Persistent Collections).\n\n"
            "2. `MutableList<T>` (Mutable Interface):\n"
            "   - بتورث من `List<T>` وبتضيف دوال التعديل (`add`, `clear`, `remove`). دي واجهة مش Implementation.\n\n"
            "3. `ArrayList<T>` (Concrete Implementation):\n"
            "   - هو الـ Class الفعلي المبني على Resizable Array في الـ JVM (`java.util.ArrayList`).\n"
            "   - بيدي O(1) random access بالقراءة والكتابة بالـ Index، لكن إضافة عناصر في البداية أو المنتصف بتكلف O(N) بسبب إزاحة العناصر، وتكبير المصفوفة عند امتلاء الـ Capacity بيكلف O(N) allocation و copy.\n\n"
            "4. `Sequence<T>` (Lazy Stream Pipeline):\n"
            "   - مش مخزن عناصر في الـ Heap أصلاً! هو Pipeline من العمليات الكسولة (Lazy Evaluation).\n"
            "   - بينفذ العمليات element-by-element (Vertical processing) ومش هيعمل أي حسابات إلا لما تنادي **Terminal Operation** (زي `toList()`, `first()`, `count()`).\n"
            "   - بيمنع إنشاء Intermediate Lists في الذاكرة عند عمل عدة transformations متتالية."
        ),
        "practical_walkthrough": (
            "في شاشة عرض قائمة الطلبات (Order History):\n"
            "- عندنا 10,000 طلب جايين من Cache، وعايزين نفلتر الطلبات المكتملة، ناخد أول 5، ونحولهم لـ UI Model.\n"
            "- **النهج الخاطئ مع Collections عادية:**\n"
            "  `orders.filter { it.isCompleted }.map { it.toUiModel() }.take(5)`\n"
            "  الكود ده هيعمل Loop كاملة على الـ 10,000 عنصر وينشئ New List في الـ Heap للـ filter، ثم New List ثانية للـ map، وبعدين ياخد 5! إهدار كبير للـ RAM والـ GC.\n"
            "- **النهج الصحيح مع Sequence:**\n"
            "  `orders.asSequence().filter { it.isCompleted }.map { it.toUiModel() }.take(5).toList()`\n"
            "  الـ Sequence هيمشي عنصر بعنصر: يفحص الطلب، لو مكتمل يحوله لـ UI Model، وأول ما يجمع 5 عناصر يوقف فوراً بدون ما يلمس باقي الـ 9,995 طلب!\n"
            "- **Defensive Copying في الـ ViewModel:**\n"
            "  private val _items = ArrayList<Item>()\n"
            "  val items: List<Item> get() = _items.toList() // Defensive snapshot يمنع الـ Race Condition"
        ),
        "quick_answer": "List is a read-only interface with no mutation methods; MutableList adds mutation methods like add and remove; ArrayList is the concrete resizable-array implementation under the hood; and Sequence is a lazy evaluation pipeline that processes elements one-by-one without creating intermediate heap collections.",
        "best_answer": (
            "The core distinction is between interfaces, implementations, and evaluation strategies. "
            "List is Kotlin's read-only interface—it exposes accessors but no mutation methods. Importantly, it is read-only, not strictly immutable, meaning the underlying instance could still be mutated by another reference. "
            "MutableList extends List and adds modification APIs. "
            "ArrayList is the concrete JVM class implementing MutableList, backed by a dynamic array offering O(1) indexed reads. "
            "Sequence, on the other hand, is not a collection at all; it is a lazy pipeline. Instead of executing transformations eagerly and allocating intermediate lists on the heap, a Sequence processes elements vertically one-by-one only when a terminal operation like toList() or first() is called. "
            "I use standard eager collections for small, in-memory lists because the iterator overhead of Sequences is unnecessary. But for multi-step pipelines on large datasets, or where short-circuiting like take(n) applies, Sequences prevent GC pressure."
        ),
        "deep_answer": (
            "From an architectural and memory standpoint, returning List<T> from a public API signals that callers cannot mutate the collection. However, in concurrent environments, simply upcasting a private MutableList to List does not provide thread safety. If a background coroutine calls add() while a UI thread iterates the read-only view, you risk a ConcurrentModificationException. In production, I expose a defensive copy using toList() or an immutable snapshot via kotlinx.collections.immutable.\n\n"
            "When comparing ArrayList to Sequence, we analyze heap allocations and CPU cache locality. Standard eager collection operations like filter and map generate intermediate java.util.ArrayList allocations at every step. If you chain three transformations on a list of 5,000 items, you allocate three separate lists on the heap, triggering Gen0/Gen1 GC sweeps.\n\n"
            "Sequences avoid intermediate allocations by composing Iterator wrappers. However, each transformation step wraps an Iterator object and invokes a function reference, adding slight indirection and call overhead. If the list is small—under a few hundred items—eager processing is actually faster because of CPU cache locality and zero iterator indirection. Sequences shine when the dataset is large, the transformation chain has multiple stages, or an early terminal operation like find or take can short-circuit before processing the entire source."
        ),
        "follow_ups": [
            {
                "interviewer": "If List<T> is read-only, can the underlying elements still be modified?",
                "answer": "Yes. First, if the element type T is mutable (for example, a class with var properties), callers can mutate element fields even through a read-only List. Second, if the List is just a cast of a MutableList, any holder of the mutable reference can add or remove elements, reflecting changes in the read-only view. True immutability requires immutable elements and a defensive copy."
            },
            {
                "interviewer": "Why not use Sequences everywhere by default if they avoid intermediate allocations?",
                "answer": "Because Sequences have per-element iterator overhead and function call indirection. For small collections, allocating a tiny intermediate array is faster and has better CPU cache locality than the boxing and iterator state-machine machinery of Sequences. Furthermore, Sequences cannot be indexed directly with O(1) random access without converting them back to a List."
            },
            {
                "interviewer": "How does kotlinx.collections.immutable differ from standard Kotlin toList()?",
                "answer": "Standard toList() creates a full defensive copy, which is an O(N) allocation and copy. Kotlinx Immutable Collections use persistent data structures (like Hash Array Mapped Tries). Modifications create a new version sharing most of the memory tree with the old version (structural sharing) in O(log N) time, making them ideal for Jetpack Compose state stability without copying overhead."
            }
        ]
    },
    {
        "id": "KOT-17",
        "arabic_explanation": (
            "الفرق بين الـ Eager Collection Processing والـ Lazy Sequences بيمس استهلاك الذاكرة والـ Performance بشكل مباشر:\n\n"
            "1. الـ Eager Processing (الافتراضي مع `Iterable`):\n"
            "   - كل دالة (زي `filter`, `map`, `sorted`) بتلف على كل عناصر الـ List فوراً، وتنشئ قائمة جديدة في الـ Heap للنتيجة (Horizontal Evaluation).\n"
            "   - لو عندك Pipeline من 3 خطوات على 10,000 عنصر، هيتعمل 3 مصفوفات مؤقتة في الـ Heap، وكل خطوة لازم تخلص 10,000 عنصر قبل ما الخطوة اللي بعدها تبدأ.\n\n"
            "2. الـ Lazy Evaluation (مع `Sequence`):\n"
            "   - العمليات بتتقسم لـ نوعين:\n"
            "     * **Intermediate Operations:** (زي `filter`, `map`, `take`) دي مش بتنفذ أي كود؛ هي مجرد بتغلف الـ Iterator في كائن Decorator جديد.\n"
            "     * **Terminal Operations:** (زي `toList`, `first`, `reduce`, `forEach`) هي دي اللي بتبدأ سحب العناصر.\n"
            "   - التنفيذ بيتم **Element-by-Element (Vertical Evaluation)**: العنصر الأول يدخل في الـ filter، لو نجح يروح للـ map فوراً، ثم للـ take. بعدين يجي العنصر التاني وهكذا.\n\n"
            "3. الـ Short-circuiting Benefit:\n"
            "   - لو بتدور على أول عنصر يطابق شرط (`find`) أو بتاخد أول 10 عناصر (`take(10)`)، الـ Sequence بيوقف المعالجة فوراً، بدون ما يكمل باقي عناصر الـ Collection!"
        ),
        "practical_walkthrough": (
            "في شاشة بحث عن مستخدمين:\n"
            "- بنقرأ قائمة من 50,000 جهة اتصال من الـ SQLite Database.\n"
            "- محتاجين نعرض أول 10 جهات اتصال يبدأ اسمهم بـ 'Mohamed' ولديهم صورة شخصية.\n"
            "- **النهج السيئ (Eager):**\n"
            "  `contacts.filter { it.name.startsWith(\"Mohamed\") }.filter { it.hasAvatar }.take(10)`\n"
            "  ده هيفحص الـ 50,000 جهة اتصال مرتين وينشئ قائمتين وسيطتين كبيرتين في الـ Heap قبل ما ياخد 10 عناصر!\n"
            "- **النهج الاحترافي (Lazy Sequence):**\n"
            "  `contacts.asSequence().filter { it.name.startsWith(\"Mohamed\") }.filter { it.hasAvatar }.take(10).toList()`\n"
            "  بمجرد العثور على 10 جهات اتصال مطابقة، الـ Terminal Operation `take(10)` بتوقف الـ Iterator فوراً. بقية الـ 49,900 جهة اتصال لم يتم فحصهم إطلاقاً، وتوفير الـ CPU والـ Memory بيكون هائل."
        ),
        "quick_answer": "Eager collection operations process the entire dataset horizontally at each step, creating intermediate heap allocations. Lazy sequences evaluate elements vertically one at a time on demand, executing transformations only when a terminal operation is called, which enables short-circuiting and avoids intermediate collections.",
        "best_answer": (
            "The primary difference lies in how elements flow through transformation pipelines: eagerly horizontally versus lazily vertically. "
            "With standard Kotlin collections, operations like filter and map are eager. Each step iterates across the entire list, creates a brand-new intermediate list on the heap, and passes that to the next step. "
            "Sequences evaluate lazily. Intermediate operations merely chain iterator decorators without executing any work. "
            "When a terminal operation like toList() or first() is invoked, elements flow vertically one-by-one through the entire pipeline: element zero passes through filter, then map, then destination, before element one is even touched. "
            "This gives two massive benefits: zero intermediate collection allocations and short-circuiting. If you call take(5) or find, the sequence halts as soon as five matching items are found, ignoring the rest of the dataset."
        ),
        "deep_answer": (
            "In Android development, deciding between Sequences and Collections comes down to allocation profiling versus CPU cycle overhead. "
            "Eager collections compile down to straightforward for-loops operating over primitive arrays. Because there are no intermediate abstraction layers, the JVM and ART can optimize loop bounds and capitalize on hardware CPU cache lines (L1/L2 cache locality). For small collections—typically under 100 to 200 items—eager processing is almost always faster in wall-clock time, even with a small temporary array allocation.\n\n"
            "Sequences introduce indirection. Each intermediate step instantiates a Sequence and an Iterator wrapper (such as FilteringSequence and TransformingSequence). Every element access requires a virtual method call to hasNext() and next(). If your pipeline has 5 steps, every single item makes 5 virtual method calls per element. "
            "However, when dealing with thousands of records—like parsing large telemetry batches or heavy contact lists—the GC pressure of allocating 3 or 4 intermediate ArrayLists of thousands of objects will trigger ART garbage collection pauses, which can cause UI frame drops. In those scenarios, or whenever short-circuiting operations like firstOrNull or any are used, Sequences are unequivocally superior."
        ),
        "follow_ups": [
            {
                "interviewer": "Can a sequence be iterated multiple times?",
                "answer": "It depends. A sequence generated from a standard collection via asSequence() can be iterated multiple times. But sequences generated from generators or single-use streams (like generateSequence or stream.asSequence()) might throw an IllegalStateException if traversed a second time. If you need multiple passes over a sequence result, convert it to a List via toList() first."
            },
            {
                "interviewer": "How does `Sequence.sorted()` behave? Is it still lazy?",
                "answer": "sorted() is a stateful intermediate operation. While it defers execution until a terminal operation is called, it cannot sort elements vertically one-by-one. When triggered, it must consume the entire sequence into an internal list, sort it in memory, and then yield elements lazily downstream. So sorted() breaks true streaming pipelining and requires O(N) memory."
            },
            {
                "interviewer": "How do Java Streams compare to Kotlin Sequences on Android?",
                "answer": "Kotlin Sequences are lightweight language constructs that run on all Android API levels without requiring Java 8 desugaring. Java Streams require API level 24 or R8 desugaring. Additionally, Java Streams support parallel processing via parallelStream(), which Kotlin Sequences do not support natively (Kotlin uses Coroutines and Flow for concurrency instead)."
            }
        ]
    },
    {
        "id": "KOT-18",
        "arabic_explanation": (
            "الـ `typealias` في Kotlin هو ميزة لإعادة تسمية الأنواع الموجودة بدون إنشاء كائن جديد في الـ Bytecode:\n\n"
            "1. إيه هو الـ `typealias` تحت الغطاء؟\n"
            "   - هو مجرد **Compile-Time Alias** (اسم مستعار). المترجم بيبدل الاسم المستعار بالنوع الأصلي تماماً في مرحلة الترجمة.\n"
            "   - لا يوجد أي Runtime Overhead، ولا يتم إنشاء Class جديد أو Wrapper في الـ Heap.\n\n"
            "2. إمتى يفيد جداً (When it helps)?\n"
            "   - **تبسيط الـ Function Types المعقدة:** لما يكون عندك Callback طويل زي `(Result<List<User>>, Int, String?) -> Unit`، تسميته `typealias UserFetchCallback = ...` بيخلي الكود مقروء جداً.\n"
            "   - **حل تعارض الأسماء (Disambiguation):** لما تستخدم مكتبتين فيهم نفس اسم الكلاس (زي `android.graphics.Path` و `com.squareup.wire.schema.internal.parser.Path`)، تقدر تعمل alias لواحد منهم بدلاً من كتابة الـ Fully Qualified Name في كل حتة.\n\n"
            "3. إمتى يضر الـ Readability ويكون خطر (When it hurts)?\n"
            "   - **وهم الـ Type Safety:** الـ `typealias` لا يوفر Type Safety إطلاقاً! لو عملت `typealias UserId = String` و `typealias OrderId = String`، تقدر تمرر `OrderId` في دالة متوقعة `UserId` بدون أي خطأ من المترجم! لو عايز حماية حقيقية للنوع، استخدم `@JvmInline value class`.\n"
            "   - إخفاء التعقيد غير المبرر: اختراع أسماء aliases غامضة يخلي المطورين الجدد محتاجين يعملوا Command+Click باستمرار لمعرفة ماهية النوع الحقيقي."
        ),
        "practical_walkthrough": (
            "في نظام التحليلات والتتبع (Analytics Module):\n"
            "- عندنا Event Parameters عبارة عن `Map<String, List<Pair<String, Any>>>`.\n"
            "- كتابة النوع ده في 10 دوال مختلفة بيخلي الـ signatures كابوس للقراءة.\n"
            "- **الاستخدام الصحيح للـ Typealias:**\n"
            "  `typealias AnalyticsPayload = Map<String, List<Pair<String, Any>>>`\n"
            "  `typealias EventDispatcher = (eventName: String, payload: AnalyticsPayload) -> Unit`\n"
            "  ده وضح المقصد وجعل الكود نظيفاً بدون أي تكلفة في الذاكرة.\n"
            "- **المقارنة مع Value Class للأمان:**\n"
            "  // خطأ: typealias لا يمنع الخلط بين المعرفات:\n"
            "  typealias AccountId = Long\n"
            "  typealias TransactionId = Long\n"
            "  fun transfer(from: AccountId, tx: TransactionId) {}\n"
            "  transfer(txId, accountId) // سيمر بنجاح ويدمر البيانات منطقياً!\n"
            "  // الحل الصحيح هو: @JvmInline value class AccountId(val value: Long)"
        ),
        "quick_answer": "A typealias provides an alternative name for an existing type purely at compile time, introducing zero runtime or allocation overhead. It improves readability for long generic types and function signatures, but it offers zero type safety—the compiler treats the alias and underlying type as completely interchangeable.",
        "best_answer": (
            "A typealias is a compile-time alias for an existing type. Under the hood, the Kotlin compiler replaces every occurrence of the alias with the underlying type in the generated bytecode, so there is zero runtime penalty or memory allocation.\n\n"
            "It is best used to clean up verbose, deeply nested signatures—especially complex higher-order function types or nested generics like Map<String, List<Pair<String, Any>>>. It is also useful for resolving import name collisions between Android framework classes and third-party libraries.\n\n"
            "Where it hurts is when developers mistake it for domain modeling or type safety. If you write `typealias UserId = String` and `typealias OrderId = String`, they are 100% interchangeable to the compiler; passing an OrderId into a UserId parameter compiles without warning. When you need real type safety to prevent primitive obsession, a @JvmInline value class is the right architectural choice, not a typealias."
        ),
        "deep_answer": (
            "Architecturally, typealias operates at the same abstraction level as C++ typedef or type aliases. It exists solely in the compiler's symbol table and Kotlin metadata. In decompiled Java bytecode, you will see the raw underlying type directly.\n\n"
            "In team codebases, excessive typealiasing can actually reduce cognitive velocity. When developers define aliases for standard framework types or shallow generics—such as `typealias StringList = List<String>`—it forces code reviewers to constantly jump to definitions to decipher simple types. It also muddies IDE autocompletion by introducing redundant symbols.\n\n"
            "Our engineering guideline is simple: use typealias only for: 1) complex functional callback signatures where parameter naming in the typealias documents the contract; 2) resolving unavoidable package name collisions; and 3) deprecation migration paths where a class has moved packages. For domain boundaries, ID wrappers, or units of measurement, we strictly mandate `@JvmInline value class` to get real compiler-enforced type boundaries."
        ),
        "follow_ups": [
            {
                "interviewer": "Can you define extension functions specifically for a typealias without affecting the original type?",
                "answer": "No. Because a typealias is fully desugared at compile time, an extension function declared on the typealias is actually declared on the underlying type. Every instance of the original type will also receive that extension function."
            },
            {
                "interviewer": "How does `typealias` compare with `@JvmInline value class` in terms of bytecode and performance?",
                "answer": "A typealias has zero bytecode presence and zero wrapper overhead; it is literally the original type. A value class creates a distinct domain type that the compiler enforces, inlining the underlying primitive or reference whenever possible to avoid heap allocation, but boxing it when used in generic or nullable positions."
            },
            {
                "interviewer": "Can a typealias have its own constructors or override methods?",
                "answer": "No. A typealias cannot have constructors, companion objects, or method overrides because it is not a class or interface; it is purely an alias for an existing declaration."
            }
        ]
    },
    {
        "id": "KOT-19",
        "arabic_explanation": (
            "التعامل مع الأخطاء والـ Failures في Kotlin من أهم مواضيع الـ Clean Architecture:\n\n"
            "1. إيه هو `kotlin.Result<T>`؟\n"
            "   - هو Discriminated Union بيعبر عن إما نجاح (`Result.success(value)`) أو فشل استثنائي (`Result.failure(throwable)`).\n"
            "   - هو `@JvmInline value class`، يعني لو تم استخدامه كـ Return type مباشر، المترجم بيحاول يعمل inline للقيمة لتجنب الـ Heap Allocation.\n"
            "   - **المشكلة الكبرى في `kotlin.Result`:** الفشل محصور دائماً في `java.lang.Throwable`! ده معناه إنه بيعامل أخطاء الـ Domain العادية (زي رصيد غير كاف، كلمة سر غير صحيحة، أو منتج غير متوفر) كأنها Exceptions، وإنشاء Throwable بيكلف جمع الـ StackTrace المكلف جداً في الـ CPU.\n\n"
            "2. ليه نمذجة أخطاء الـ Domain بـ Sealed Hierarchy أفضل بكثير؟\n"
            "   - في الـ Business Logic، الفشل مش 'حادث استثنائي'؛ الفشل هو نتيجة متوقعة وشرعية من قواعد العمل (Expected Business Outcome).\n"
            "   - باستخدام `sealed interface DomainResult<out T, out E>`:\n"
            "     * بنفصل النجاح والخطأ بدقة Type-safe.\n"
            "     * أخطاء الـ Domain (زي `InsufficientFunds`, `UserBlocked`) بتكون كائنات عادية بدون StackTrace وبدون Overhead.\n"
            "     * الـ Compiler بالـ `when` expression بيجبر المطور يعالج كل حالات الخطأ بدون نسيان (Exhaustive Handling)."
        ),
        "practical_walkthrough": (
            "في نظام الدفع والشراء في تطبيق Android:\n"
            "- المستخدم بيضغط 'تأكيد الدفع' بمبلغ 100 دولار.\n"
            "- **النهج السيئ باستخدام Exceptions و Result:**\n"
            "  `fun pay(): Result<Receipt> = try { ... } catch(e: InsufficientFundsException) { Result.failure(e) }`\n"
            "  كل مرة رصيد المستخدم لا يكفي، بننشئ Exception ونجمع الـ Stack Trace كامل من الـ OS! ده بطيء ومسيء لنمذجة منطق العمل.\n"
            "- **النهج الاحترافي باستخدام Domain Sealed Result:**\n"
            "  sealed interface PaymentResult {\n"
            "      data class Success(val receipt: Receipt) : PaymentResult\n"
            "      sealed interface Failure : PaymentResult {\n"
            "          data class InsufficientFunds(val balance: BigDecimal, val required: BigDecimal) : Failure\n"
            "          data object NetworkTimeout : Failure\n"
            "          data class CardExpired(val expiryDate: String) : Failure\n"
            "      }\n"
            "  }\n"
            "- في الـ ViewModel:\n"
            "  `when (result) { is Success -> navigate(); is InsufficientFunds -> showTopUpDialog(); ... }`\n"
            "  الـ IDE والـ Compiler يضمنان معالجة كل حالة بنسبة 100% بدون أي Runtime Crash."
        ),
        "quick_answer": "Kotlin's built-in Result models either a value or a Throwable as an inline value class. For domain logic, modeling errors with a custom sealed hierarchy or an Either type is much better because domain failures are expected business outcomes, not exceptions; sealed classes avoid costly stack-trace generation and enable exhaustive compiler-checked handling.",
        "best_answer": (
            "Kotlin's standard Result<T> is designed primarily for encapsulating the outcome of operations that might throw exceptions, capturing either a successful value or a Throwable. Because it is implemented as an inline value class, it avoids heap allocations when used directly.\n\n"
            "However, using Result for domain errors has a fundamental flaw: its failure branch is hardcoded to Throwable. In clean domain architecture, business failures—such as InsufficientFunds or InvalidCredentials—are not unexpected runtime exceptions; they are legitimate, expected outcomes of domain rules. Creating a Throwable forces the JVM to capture an entire stack trace, which is expensive in terms of CPU and memory.\n\n"
            "Instead, I model domain outcomes using a custom sealed interface—like `sealed interface DataResult<out T, out E>`—or dedicated state hierarchies. This gives compile-time exhaustive type checking via when expressions, attaches strongly typed metadata to failures, and avoids the performance penalty of exception allocation."
        ),
        "deep_answer": (
            "When designing domain layers in production Android apps, the choice between Kotlin Result, Arrow's Either, and custom sealed hierarchies directly impacts code clarity and diagnostic capabilities. "
            "Until Kotlin 1.5, kotlin.Result could not even be returned from functions without compiler flags because of inline class ABI considerations. Even today, it suffers from ergonomic limitations: you cannot customize the failure type, and functions like `mapCatching` swallow all Throwables, including `CancellationException`, which breaks Coroutine cancellation hierarchies if not carefully handled.\n\n"
            "With a custom sealed hierarchy like `sealed interface AppResult<out T, out E>`: "
            "1. Domain errors can carry rich context (e.g., `data class NetworkError(val httpCode: Int, val retryAfterSeconds: Int)`). "
            "2. When consuming the result in a ViewModel or MVI reducer, the Kotlin compiler enforces exhaustiveness on the `E` domain error sealed branch without needing an `else` branch, eliminating runtime unhandled edge cases. "
            "3. Stack traces are never collected for expected business validation failures, reducing GC churn in high-frequency operations."
        ),
        "follow_ups": [
            {
                "interviewer": "Why is catching Throwable or using `runCatching` dangerous with Kotlin Coroutines?",
                "answer": "`runCatching` catches all `Throwable` instances, which includes `CancellationException`. If a Coroutine is cancelled and runs code inside `runCatching`, the cancellation exception is swallowed and converted into a `Result.failure`, breaking structured concurrency and preventing the coroutine from canceling properly. You must always rethrow `CancellationException`."
            },
            {
                "interviewer": "When would you actually recommend using `kotlin.Result`?",
                "answer": "It is well-suited for low-level infrastructure boundaries, such as wrapping raw HTTP client calls, database drivers, or legacy Java SDKs where exceptions are the native error mechanism. At that boundary, you can catch the Throwable, and then map it into your typed domain sealed error hierarchy before passing it up to use cases."
            },
            {
                "interviewer": "Does `kotlin.Result` allocate memory on the heap?",
                "answer": "When returned directly from a function, it is compiled as an inline value class and unboxed, avoiding allocation. However, if you store it in a generic collection like `List<Result<T>>` or cast it to Any, it is boxed into a heap object."
            }
        ]
    },
    {
        "id": "KOT-20",
        "arabic_explanation": (
            "الـ Scope Functions في Kotlin (`let`, `run`, `with`, `apply`, `also`) بتفرق بشكل أساسي في حاجتين: **سياق الوصول للكائن (Context Object)** و **القيمة المرجعة (Return Value)**:\n\n"
            "1. Context Object: Receiver (`this`) مقابل Argument (`it`):\n"
            "   - **Receiver (`this`):** زي `apply`, `run`, `with`.\n"
            "     * بتتعامل مع الكائن وكأنك جواه مباشرة: بتنادي الـ methods والـ properties بدون ما تكتب اسم المتغير.\n"
            "     * مناسبة جداً للـ Object Configuration والتهيئة.\n"
            "     * **العيب والتحذير:** لو بتستخدمها داخل كلاس، `this` ممكن يختلط عليك بين الكائن الخارجي والداخلي (Shadowing)، مما يسبب أخطاء خفية.\n"
            "   - **Argument (`it`):** زي `let`, `also`.\n"
            "     * الكائن بيمر كـ Lambda Parameter (`it` أو تقدر تديله اسم صريح زي `user ->`).\n"
            "     * مناسبة جداً للـ Null Checks (`user?.let { ... }`) والـ Side Effects والـ Parameter Passing.\n"
            "     * ميزة كبيرة: تقدر تسمي المتغير اسم واضح وتتجنب أي لبس في الـ Scope.\n\n"
            "2. Return Value:\n"
            "   - **بيرجع الكائن نفسه (Context Object):** `apply` و `also`.\n"
            "   - **بيرجع نتيجة الـ Lambda (Lambda Result):** `let`, `run`, `with`."
        ),
        "practical_walkthrough": (
            "في شاشة بناء Intent وتجهيز بيانات المستخدم:\n"
            "- **الاستخدام الخاطئ والملتبس:**\n"
            "  استخدام `run` أو `apply` داخل Activity لتهيئة كائن تاني فيه نفس أسماء الدوال، زي `title = ...` أو `finish()`. الكود مش بيبقى واضح هو بيعدل الـ Activity ولا الكائن الجديد!\n"
            "- **الاستخدام النظيف الصحيح:**\n"
            "  // 1. تهيئة الكائن (Object Configuration) نستخدم apply:\n"
            "  val intent = Intent(context, ProfileActivity::class.java).apply {\n"
            "      putExtra(EXTRA_ID, user.id)\n"
            "      flags = Intent.FLAG_ACTIVITY_CLEAR_TOP\n"
            "  }\n"
            "  // 2. التحقق من Null والتحويل نستخدم let مع تسمية صريحة:\n"
            "  user?.let { safeUser ->\n"
            "      analytics.logUserLogin(safeUser.id)\n"
            "  }\n"
            "  // 3. التدقيق و Side Effects نستخدم also:\n"
            "  val validatedOrder = createOrder(cart).also { order ->\n"
            "      logger.debug(\"Created order with id: ${order.id}\")\n"
            "  }"
        ),
        "quick_answer": "Scope functions differ in how they expose the context object: receiver functions (apply, run, with) expose it as 'this' for direct property access, while argument functions (let, also) pass it as 'it' or a named parameter. Additionally, apply and also return the context object itself, whereas let, run, and with return the lambda result.",
        "best_answer": (
            "Kotlin scope functions provide temporary scopes to execute code blocks on an object, differing along two architectural axes: how the context object is referenced and what the block returns.\n\n"
            "First, for the context reference: receiver-based functions—apply, run, and with—bind the object to `this`. This allows concise member access without repetitive prefixes, making them ideal for object configuration and initialization. In contrast, argument-based functions—let and also—pass the object as a lambda parameter `it`. This is safer when you want to avoid `this` shadowing, need to pass the object to another method, or want to rename the parameter for clarity.\n\n"
            "Second, for return values: apply and also return the original context object itself, enabling fluent method chaining. Let, run, and with return whatever the last expression of the lambda evaluates to, making them suitable for mapping and transformation pipelines."
        ),
        "deep_answer": (
            "Under the hood, all five scope functions are inline functions in the Kotlin standard library (`inline fun <T, R> ...`). This means they compile directly to flat bytecode with zero lambda object allocations or virtual dispatch overhead, provided you do not capture local variables in non-inlined contexts.\n\n"
            "However, using receiver semantics (`this`) introduces cognitive and shadowing risks in complex classes. For instance, in an Android Activity or Composable, calling `binding.run { title = ... }` might inadvertently shadow the Activity's own `title` property. If a property name clashes, you must write `this@MainActivity.title`, which degrades readability. In contrast, argument semantics (`it`) force explicit naming, preventing subtle shadowing bugs.\n\n"
            "In professional code review, we enforce distinct roles: `apply` exclusively for configuring newly constructed objects; `also` exclusively for side-effects like logging or caching during builder chains without mutating the subject; `let` for null-safe operations (`?.let`) or transforming a scoped value; and `run` only when evaluating a multi-step block that returns a derived computation."
        ),
        "follow_ups": [
            {
                "interviewer": "Why is chaining multiple scope functions considered an anti-pattern?",
                "answer": "Chaining scopes (e.g., `user?.let { it.address }?.run { ... }?.also { ... }`) obscures the origin of values and context objects, drastically harming code readability and making debugging with breakpoints frustrating. Standard local variables with descriptive names are much clearer."
            },
            {
                "interviewer": "What is the difference between `run` and `with`?",
                "answer": "`with` is a non-extension function that takes the receiver as its first argument (`with(receiver) { ... }`), while `run` is an extension function called directly on the receiver (`receiver.run { ... }`). `run` also supports null-safe invocation (`receiver?.run { ... }`), which `with` does not."
            },
            {
                "interviewer": "Does using `let` on a nullable variable prevent race conditions if the variable is a mutable var?",
                "answer": "Yes! Because `let` passes the variable as a lambda parameter, the value is read once and copied into a local immutable reference (`it`). Even if another thread mutates the original `var` property concurrently, the code inside the lambda safely operates on the non-null captured local snapshot."
            }
        ]
    },
    {
        "id": "KOT-21",
        "arabic_explanation": (
            "الـ Value Classes (المعرفة بـ `@JvmInline value class`) هي أداة قوية في Kotlin لإنشاء أنواع مخصصة قوية (Domain Types) بدون تكلفة الذاكرة المرتبطة بإنشاء كائنات على الـ Heap:\n\n"
            "1. المشكلة اللي بتحلها (Primitive Obsession):\n"
            "   - في تطبيقات كتير بنستخدم `String` للـ `UserId` و `OrderId` و `Email`. الخلط بينهم في الـ Parameters وارد جداً وبيعمل Bugs صعبة في الإنتاج.\n"
            "   - لو عملت `data class UserId(val value: String)`، حليت مشكلة الأمان، لكن أنشأت Object جديد في الـ Heap لكل ID، وده بيضغط على الـ Garbage Collector بشدة.\n\n"
            "2. إزاي بتشتغل تحت الغطاء (How it works in JVM):\n"
            "   - المترجم بيعمل **Inlining** للقيمة الأساسية في معظم الحالات. في الـ Bytecode، الدالة اللي بتاخد `UserId` بتتحول لدالة عادية بتاخد `String` مباشرة، مع **Name Mangling** في اسم الدالة (زي `getUser-xxxx(String)`) لمنع تصادم الـ Signatures في الـ JVM.\n\n"
            "3. متى يحدث الـ Boxing (Boxing Caveats):\n"
            "   - لو استخدمت الـ Value Class في **Generics** (زي `List<UserId>`).\n"
            "   - لو جعلتها **Nullable** (زي `UserId?`).\n"
            "   - لو عاملتها كـ **Interface** (Polymorphism).\n"
            "   - في الحالات دي، الـ JVM مضطر يعمل **Boxing** وينشئ كائن Wrapper في الـ Heap، وتفقد ميزة انعدام الـ Allocation."
        ),
        "practical_walkthrough": (
            "في نظام التجارة الإلكترونية:\n"
            "- العملات والمبالغ المالية:\n"
            "  `@JvmInline value class Money(val cents: Long)`\n"
            "  `@JvmInline value class UserId(val raw: String)`\n"
            "- الآن الدوال أصبحت آمنة تماماً:\n"
            "  `fun debit(user: UserId, amount: Money)`\n"
            "  مستحيل المطور يمرر المعرفات بالخطأ.\n"
            "- في الـ Bytecode:\n"
            "  الدالة بتتحول لـ `debit(String user, long amount)` بدون أي Heap Object إضافي!\n"
            "- **التحذير من الـ Interoperability مع Java:**\n"
            "  كود Java لا يستطيع مناداة الدالة دي بسهولة بسبب الـ Name Mangling اللي بيضيفه Kotlin (`debit-abc(String, long)`). لو محتاج تستدعيها من Java، لازم تستخدم `@JvmName` صريح أو تتعامل مع الـ Wrapper."
        ),
        "quick_answer": "Value classes (@JvmInline value class) wrap a single underlying value to provide compile-time type safety with zero heap allocation in unboxed scenarios. In bytecode, the compiler inlines the underlying representation directly, but boxes it into a heap object when used as generics, nullables, or interfaces.",
        "best_answer": (
            "Value classes, annotated with @JvmInline, solve the problem of primitive obsession without runtime performance penalties. They let you wrap a single value in a strongly-typed domain abstraction—such as wrapping a String in a UserId or a Long in Money.\n\n"
            "At compile time, the Kotlin compiler enforces complete type safety so you can never accidentally pass an OrderId where a UserId is expected. In generated bytecode, the compiler unboxes the value class, replacing it with the underlying primitive or reference type directly. This gives you expressive domain types without allocating objects on the heap.\n\n"
            "However, you must be aware of boxing caveats. Whenever a value class is used in a generic collection like List<UserId>, passed as an interface, or declared as nullable (UserId?), the JVM cannot use the bare primitive and must box it into a wrapper object on the heap, negating the allocation savings."
        ),
        "deep_answer": (
            "At the JVM bytecode level, the Kotlin compiler uses two mechanisms to make value classes work: unboxing and name mangling. "
            "To prevent signature conflicts caused by type erasure—for example, two overloaded functions `process(id: UserId)` and `process(id: OrderId)` which both erase to `process(String)`—the compiler appends a hash suffix to the method name in bytecode (e.g., `process-u18aD(String)`). While transparent to Kotlin callers, this makes calling value class methods from Java cumbersome unless annotated with `@JvmName`.\n\n"
            "Regarding memory: in a high-frequency Android event bus or audio processing pipeline, allocating millions of wrapper objects triggers garbage collection churn. Unboxed value classes eliminate this entirely because they reside on the stack or in CPU registers as bare primitives.\n\n"
            "However, developers frequently lose these benefits through accidental boxing: 1) Storing them in standard collections like `List<ItemId>` forces boxing because Java generics are object-based; 2) Casting to an interface implemented by the value class forces a heap instance; 3) Marking it as nullable (`ItemId?`) forces boxing because a primitive cannot represent null. In performance-critical hot paths, profiling heap allocations with Android Studio Memory Profiler is necessary to confirm that inlining is actually occurring."
        ),
        "follow_ups": [
            {
                "interviewer": "Can a value class have properties and methods?",
                "answer": "Yes. A value class can declare methods, computed properties, and init blocks. However, it cannot have secondary backing fields, late-initialized properties, or inherit from class hierarchies (it can only implement interfaces)."
            },
            {
                "interviewer": "Why does the Kotlin compiler apply name mangling to functions taking value classes?",
                "answer": "Because unboxing erases the value class to its underlying type. If you have two overloads `fun send(id: UserId)` and `fun send(id: AccountId)` where both wrap String, Java bytecode would see two identical methods `void send(String)`. Mangling prevents JVM method signature collisions."
            },
            {
                "interviewer": "Can a value class wrap multiple properties?",
                "answer": "Currently on JVM Android, value classes can only wrap a single underlying property. Kotlin has experimental multi-field value class support on Kotlin/Native and future Valhalla JVMs, but for current Android production apps, single-property wrapping is the rule."
            }
        ]
    },
    {
        "id": "KOT-22",
        "arabic_explanation": (
            "الـ Reflection في Kotlin و Android (عبر `kotlin-reflect` أو `java.lang.reflect`) هي آلية لفحص الـ Classes والـ Methods والـ Properties واستدعائها ديناميكياً أثناء وقت التشغيل (Runtime):\n\n"
            "1. تكلفة وأضرار الـ Reflection في Android:\n"
            "   - **بطء في وقت التشغيل (Performance Penalty):** استدعاء الدوال عبر الـ Reflection أبطأ بعشرات المرات من الاستدعاء المباشر؛ لأنه بيتطلب تجاوز الـ JIT/AOT inlining، والبحث في الـ Method Table، وعمل Boxing/Unboxing للـ Arguments.\n"
            "   - **حجم الـ APK والذاكرة:** مكتبة `kotlin-reflect.jar` بتضيف حوالي 2.5 إلى 3 ميجابايت لحجم الـ APK ومئات الكيلوبايتس في الـ RAM عند تحميل الـ Metadata.\n\n"
            "2. خطر الـ R8 والـ ProGuard Minification:\n"
            "   - الـ R8 بيقوم بعمل Code Shrinking و Obfuscation وتغيير أسماء الكلاسات والـ Fields (زي تحويل `userName` لـ `a`).\n"
            "   - لو كودك بيبحث عن Field باسم معين بالـ Reflection، التطبيق هيعمل Crash بـ `NoSuchFieldException` أو `NoSuchMethodException` في الـ Release Build!\n\n"
            "3. البدائل الحديثة في Android Modern Development:\n"
            "   - استبدال الـ Reflection بـ **Compile-Time Annotation Processing أو KSP (Kotlin Symbol Processing)**.\n"
            "   - زي ما بتعمل مكتبات Moshi مع `@JsonClass(generateAdapter = true)`، ومكتبة Room، ومكتبة Dagger/Hilt، حيث يتم توليد كود Kotlin عادي وصريح وقت الـ Compile بدون أي Reflection."
        ),
        "practical_walkthrough": (
            "في طبقة تحويل الـ JSON (Serialization):\n"
            "- **النهج السيئ (Runtime Reflection):**\n"
            "  استخدام مكتبة قديمة تقرأ الـ Fields وقت التشغيل بالـ Reflection:\n"
            "  عند تحويل 5,000 كائن في الـ Feed، الـ Reflection بيعمل آلاف الـ Method Lookups، ويتسبب في تجميد الـ UI Thread وسقوط فريمات (Jank).\n"
            "  والأسوأ: في الـ Release Build مع R8، كل أسماء الحقول تتغير والتطبيق يفشل في جلب البيانات.\n"
            "- **النهج الاحترافي (Compile-Time Generation مع KSP):**\n"
            "  استخدام Moshi Code Gen أو Kotlinx Serialization:\n"
            "  `@Serializable data class UserDto(val id: String, val name: String)`\n"
            "  المترجم يولد `UserDto$$serializer.kt` كود مباشر وسريع جداً، متوافق 100% مع R8 بدون الحاجة لكتابة ProGuard rules معقدة."
        ),
        "quick_answer": "Reflection inspects and invokes code dynamically at runtime. It is expensive and risky on Android because it degrades CPU performance, disables JIT/AOT inlining, increases APK size (via kotlin-reflect), and breaks under R8 minification when class and member names are obfuscated.",
        "best_answer": (
            "Reflection allows code to inspect its own classes, constructors, methods, and properties dynamically at runtime. While powerful for generic frameworks, using reflection in production Android apps carries significant risks and performance penalties.\n\n"
            "First, performance: invoking members via reflection bypasses JVM/ART inline optimizations, requires runtime security checks, and forces argument boxing and dynamic lookups, making it orders of magnitude slower than direct method invocation.\n\n"
            "Second, app size: bundling `kotlin-reflect` adds roughly 2.5MB to your release APK, which is substantial for mobile.\n\n"
            "Third, minification failures: R8 and ProGuard aggressively shrink and obfuscate class names and member fields in release builds. Reflection that looks up fields by string name will fail with NoSuchFieldException or NoSuchMethodException unless accompanied by fragile, manually maintained ProGuard keep rules.\n\n"
            "Modern Android architecture avoids runtime reflection by relying on compile-time code generation via KSP or Kotlin compiler plugins, as seen in kotlinx.serialization, Moshi codegen, Room, and Hilt."
        ),
        "deep_answer": (
            "From an engine perspective, ART (Android Runtime) optimizes regular Kotlin/Java calls through Ahead-Of-Time (AOT) and Just-In-Time (JIT) compilation, devirtualizing calls and inlining short methods directly into caller machine code. Reflection defeats all of this: `Method.invoke()` cannot be inlined, allocations are made for parameter arrays, and primitives are boxed onto the heap.\n\n"
            "Furthermore, Kotlin Reflection (`KClass`, `KProperty`, `KFunction`) relies on parsing the `@Metadata` annotation embedded in Kotlin class bytecode. Parsing this metadata on an Android mobile device causes noticeable startup latency and heap spike during app cold starts.\n\n"
            "In our CI/CD and architecture governance, we enforce zero runtime reflection policies for data models. By adopting Kotlin Symbol Processing (KSP) and kotlinx.serialization, adapters and dependency graphs are generated as plain, type-safe Kotlin files during compilation. This ensures full R8 optimization, zero metadata parsing overhead, and compile-time verification of model integrity."
        ),
        "follow_ups": [
            {
                "interviewer": "How does Kotlin Symbol Processing (KSP) replace reflection?",
                "answer": "KSP analyzes Kotlin source code and annotations during the compilation phase, before bytecode generation. It allows compiler plugins to generate concrete, strongly-typed Kotlin classes (like serializers or DAO implementations) that call methods directly, achieving the convenience of reflection without any runtime performance or R8 penalties."
            },
            {
                "interviewer": "If a third-party SDK must use reflection, how do you safeguard release builds?",
                "answer": "You must write precise ProGuard/R8 `-keep` rules (e.g., `-keepclassmembers class com.example.model.** { <fields>; }`) and verify them in release-mode UI tests. In addition, you should inspect mapping files (`mapping.txt`) to confirm that required fields remain accessible."
            },
            {
                "interviewer": "What is the difference between `java.lang.reflect` and `kotlin-reflect`?",
                "answer": "`java.lang.reflect` is built into the standard Android runtime and handles standard Java classes, but it lacks knowledge of Kotlin-specific features like nullability, coroutines, value classes, and default arguments. `kotlin-reflect` understands these semantics by parsing Kotlin metadata, but requires an external library that increases APK size."
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

    for q in KOT_16_22:
        if q["id"] not in seen:
            combined.append(q)
            seen.add(q["id"])
        else:
            # Update existing
            for idx, item in enumerate(combined):
                if item["id"] == q["id"]:
                    combined[idx] = q
                    break

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(combined, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions through KOT-22. Total questions: {len(combined)}")


if __name__ == "__main__":
    main()

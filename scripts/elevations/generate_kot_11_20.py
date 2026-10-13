#!/usr/bin/env python3
"""Generator for KOT-11 through KOT-20 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "kot.json"

existing = []
if DATA_FILE.exists():
    try:
        existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        existing = []

KOT_11_20 = [
    {
        "id": "KOT-11",
        "arabic_explanation": (
            "الـ Local Functions هي دوال بتتعرف داخل دوال تانية (Nested Functions)، والهدف الأساسي منها هو **الـ Clean Code وتقسيم المنطق المعقد (Code Encapsulation)**:\n\n"
            "1. إمتى بنحتاجها؟\n"
            "   لما يكون عندك دالة كبيرة (زي Parsing معقد أو Recursive Algorithm أو Validation مركب) وفيه جزء منطقي بيتكرر أكتر من مرة، لكن الجزء ده ملوش أي معنى ولا فايدة لأي كائن بره الدالة دي.\n\n"
            "2. الـ Closure وقراءة المتغيرات:\n"
            "   الـ Local Function بتقدر تقرأ المتغيرات المحلية للدالة الخارجية مباشرة من غير ما تمررها كـ Parameters. لكن انتبه: ده بيعمل Closure في الـ Bytecode.\n\n"
            "3. تحت الغطاء في الـ JVM:\n"
            "   لو الـ Local Function بتعمل Capture لمتغيرات محلية واتحولت لـ Function Reference، المترجم هيولد New Object في الـ Heap. لكن لو استدعاؤها عادي ومباشر، المترجم بيحولها لـ Private Static Method بتاخد المتغيرات كـ Parameters بدون overhead إضافي."
        ),
        "practical_walkthrough": (
            "في شاشة تسجيل مستخدم جديدة:\n"
            "- الدالة `registerUser(name: String, email: String, age: Int)` محتاجة تعمل Validation للحقول.\n"
            "- النهج الخاطئ: كتابة 5 private methods في الكلاس علشان يتنادوا مرة واحدة بس من دالة التسجيل، مما يزحم الكلاس بـ Utility methods ملهاش علاقة بباقي الكود.\n"
            "- النهج الصحيح: استخدام Local Function `validateOrThrow` داخل `registerUser`:\n"
            "  fun registerUser(...) {\n"
            "      fun validateField(value: String, fieldName: String) {\n"
            "          if (value.isBlank()) throw ValidationException(\"$fieldName cannot be blank\")\n"
            "      }\n"
            "      validateField(name, \"Name\")\n"
            "      validateField(email, \"Email\")\n"
            "  }\n"
            "- التحقق: الكود بيبقى مقروء جداً ومنطقي، ووحدة الاختبار بتختبر `registerUser` بمدخلات ناقصة وتتأكد من رسائل الخطأ."
        ),
        "quick_answer": "Local functions are functions defined inside other functions. They encapsulate repetitive helper logic that is relevant only to that specific enclosing function. They have direct access to variables in the outer scope, which eliminates parameter boilerplate while keeping class bodies clean.",
        "best_answer": (
            "A local function is a function declared inside another function. I use them to break down complex or repetitive algorithms without cluttering the outer class with single-use private methods.\n\n"
            "The big advantage is scoping: a local function is invisible to the rest of the class, cleanly encapsulating logic that has no business being called anywhere else. "
            "It can also access the outer function's local variables directly without needing them passed as parameters.\n\n"
            "For example, inside a complex data-mapping function, I might define a local sanitize() helper to validate and clean individual string fields.\n\n"
            "The trade-off is readability if overused: a local function that spans dozens of lines makes the parent function hard to follow. I keep them short and focused on a single responsibility."
        ),
        "deep_answer": (
            "Under the hood, kotlinc compiles a local function by generating a private static method or, if it captures variables from its enclosing scope and is passed as a reference, "
            "an anonymous FunctionN class on the heap. When invoked as a direct call, the compiler optimizes it into an ordinary static call with captured variables passed as synthetic parameters, "
            "avoiding runtime allocation.\n\n"
            "Local functions are particularly effective for implementing tail-recursive algorithms (with the tailrec modifier) or complex recursive graph traversals, "
            "such as validating circular dependencies in a dependency graph or deeply nested JSON tree parsing.\n\n"
            "In production codebases, we enforce a strict rule: if a local function grows beyond 10-15 lines or requires independent unit testing, "
            "it must be extracted into a dedicated top-level or private member function. Local functions should purely be formatting and encapsulation aids, not hiding places for un-tested business rules."
        ),
        "follow_ups": [
            {
                "interviewer": "Can a local function be marked with the `tailrec` modifier for recursion?",
                "answer": "Yes! Local functions fully support the `tailrec` keyword. The compiler will optimize recursive calls into an iterative loop in bytecode, preventing stack overflow errors while keeping the helper scoped inside the outer function."
            },
            {
                "interviewer": "Does a local function cause heap allocations if it references outer variables?",
                "answer": "If the local function is invoked directly as a normal call, the compiler optimizes it into a private static method and passes captured outer variables as method parameters, resulting in zero heap allocations. An allocation only occurs if you take a function reference (like `::myLocalHelper`) and pass it to a higher-order function."
            },
            {
                "interviewer": "How do you unit test a local function?",
                "answer": "You cannot unit-test a local function in isolation because it is strictly scoped to the enclosing function's body. If the logic inside a local function is complex enough to warrant its own dedicated unit tests, that is an immediate architectural signal to extract it into a standalone class or internal member function."
            }
        ]
    },
    {
        "id": "KOT-12",
        "arabic_explanation": (
            "الـ `inline` keyword في Kotlin هي أداة لتحسين الأداء (Compiler Optimization) بتطلب من المترجم إنه **ينسخ كود الدالة والـ Lambdas اللي جواها مباشرة في مكان الاستدعاء (Call Site)** بدل ما يعمل Function Call حقيقية:\n\n"
            "1. الفائدة الأساسية (The Win):\n"
            "   في الـ Higher-Order Functions العادية، تمرير Lambda بيولد كائن `FunctionN` في الـ Heap مع كل استدعاء. الـ `inline` بيحذف هذا الـ Object Allocation تماماً وبيحذف الـ Method Call Overhead.\n\n"
            "2. المزايا الإضافية:\n"
            "   - بتسمح بـ **Non-local Return**: تقدر تعمل `return` من الدالة الخارجية مباشرة من جوه الـ Lambda.\n"
            "   - بتسمح بـ **Reified Type Parameters**: فحص الـ Generic Type في الـ Runtime (زي `inline fun <reified T> parse()`).\n\n"
            "3. التكلفة والمخاطر (The Cost):\n"
            "   **Code Bloat (تضخم حجم الكود)**: لو عملت inline لدالة كبيرة، وتكررت في 200 مكان في التطبيق، حجم الـ Bytecode والـ DEX هيكبر جداً، والـ APK حجمه هيزيد.\n\n"
            "قاعدة ذهبية: متعملش `inline` إلا لو الدالة بتقبل Lambda كـ Parameter وتكون الدالة صغيرة وبسيطة!"
        ),
        "practical_walkthrough": (
            "في Kotlin Standard Library:\n"
            "- دوال زي `filter` و `map` و `let` و `apply` معمولة `inline` لأنها صغيرة وبتاخد Lambdas، وده بيوفر ملايين الـ Heap Allocations في كل لفة loop.\n"
            "- النهج الخاطئ: عمل `inline` لدالة عادية مبتاخدش أي Lambda باراميتر: `inline fun calculateTax(amount: Double): Double`. المترجم هيطلع لك Warning صريح: \"Expected performance impact from inlining is negligible. Inlining works best for functions with parameters of functional types\".\n"
            "- التحقق: افتح `Show Kotlin Bytecode` وشوف ازاي استدعاء دالة `inline` بينسخ جسم الدالة في الـ bytecode بدون إنشاء أي كائن `Function`."
        ),
        "quick_answer": "The inline modifier instructs the compiler to copy the function's bytecode and its lambda parameters directly into the call site. This eliminates Function object heap allocations and virtual call overhead, enabling non-local returns and reified types. However, inlining large functions inflates bytecode size and APK method count.",
        "best_answer": (
            "The inline modifier is a compiler optimization for higher-order functions. Instead of generating a standard method call and allocating an anonymous Function object on the heap for the lambda, the compiler copies the function's body and lambda bytecode directly into the call site.\n\n"
            "This yields two major benefits: it eliminates heap allocations during hot loops or frequent UI callbacks, and it enables language features like reified type parameters and non-local returns.\n\n"
            "The cost is bytecode bloat. If an inlined function is large or called in hundreds of places, it significantly increases the compiled DEX size and APK size.\n\n"
            "In production, I only inline small, frequently called utility functions that accept lambda parameters. Inlining a function with no functional parameters is an anti-pattern that the compiler explicitly warns against."
        ),
        "deep_answer": (
            "At the bytecode level, executing a non-inlined lambda involves creating an instance of a synthetic class implementing kotlin.jvm.functions.FunctionN, "
            "followed by an invokeinterface bytecode instruction. In hot execution paths like collection transformations or frame render passes, this creates garbage collection pressure.\n\n"
            "When marked inline, kotlinc eliminates both the invocation and the Function object. It splices the instruction stream directly into the caller's stack frame. "
            "This enables non-local returns: a return statement inside the inlined lambda returns from the outer enclosing function, mimicking the behavior of built-in control structures like for loops or if statements.\n\n"
            "However, inlining comes with severe architectural trade-offs: code size explosion, inability to access private members of the enclosing class from public inline functions (unless marked @PublishedApi), "
            "and compiler recompilation cascades in multi-module builds. If a library updates an inline function, all downstream consumers must be recompiled. In production Android apps, we monitor APK method count and avoid inlining complex business methods."
        ),
        "follow_ups": [
            {
                "interviewer": "Why does the Kotlin compiler warn you if you use `inline` on a function with no lambda parameters?",
                "answer": "Because the modern JVM and Android ART runtimes already perform aggressive JIT inlining on small standard methods at runtime. The Kotlin `inline` keyword exists specifically to eliminate FunctionN object heap allocations and enable non-local returns. Inlining a function with no lambdas provides negligible performance improvement while unnecessarily inflating bytecode."
            },
            {
                "interviewer": "What is `@PublishedApi`, and when do you have to use it with inline functions?",
                "answer": "When an `inline` function is public or internal, its bytecode is copied into external call sites. If that inline function attempts to access private members of its declaring class, compilation fails because external callers cannot access private fields. Annotating the private member with `@PublishedApi` makes it synthetic-public in bytecode so the inline function can access it, while keeping it invisible to ordinary Kotlin callers."
            },
            {
                "interviewer": "Can an inline function be recursive?",
                "answer": "No. The compiler cannot inline a function that calls itself recursively because inlining it would cause infinite bytecode expansion during compilation. Recursive functions cannot be marked `inline`."
            }
        ]
    },
    {
        "id": "KOT-13",
        "arabic_explanation": (
            "المفاهيم الأربعة دي بتكمل فهمك العميق للـ `inline` functions في Kotlin:\n\n"
            "1. Non-local Return:\n"
            "   في الـ inline function، لما تكتب `return` جوه الـ lambda، الـ return دي بترجع من **الدالة الكبيرة المحيطة بيها بالكامل** مش بس من الـ lambda! ده لأن الكود اتنسخ مباشرة في الـ call site زي حلقة `for` عادية.\n\n"
            "2. `crossinline`:\n"
            "   لو الـ lambda بتتنادى جوه سياق تاني (Execution Context مختلف زي `Runnable` أو Coroutine أو Thread تاني)، الـ Non-local return بيكون مستحيل فيزيائياً لأن الدالة الأصلية ممكن تكون خلصت خلاص! "
            "   هنا المترجم بيجبرك تحط `crossinline` علشان يمنع الـ non-local return ويسمح بـ inlining لباقي الكود بأمان.\n\n"
            "3. `noinline`:\n"
            "   لو الدالة بتاخد كذا lambda، وعايز تعمل inline لواحدة وتخزن التانية في متغير أو تمررها لدالة عادية، بتحط على التانية `noinline`. المترجم هيتعامل معاها كـ Function object عادي.\n\n"
            "4. `reified` Type Parameters:\n"
            "   بسبب الـ Type Erasure في الـ JVM، الـ Generics بتتمسح وقت التشغيل (`List<String>` بتبقى `List`). لكن مع `inline fun <reified T>`، لأن الكود بيتنسخ في الـ Call site، "
            "   المترجم بيعرف النوع الفعلي وبيسيبه في الـ Bytecode، وتقدر تكتب `T::class.java` بدون ما تمرر `Class<T>` كـ parameter!"
        ),
        "practical_walkthrough": (
            "في كود أندرويد اليومي:\n"
            "- استخدام `reified` في Navigation أو Serialization:\n"
            "  `inline fun <reified T : Activity> Context.startActivity() = startActivity(Intent(this, T::class.java))`\n"
            "  الاستدعاء بيبقى ساحر: `startActivity<DetailActivity>()` بدل كتابة `DetailActivity::class.java` في كل مكان.\n"
            "- استخدام `crossinline` عند تمرير Callback لـ View listener:\n"
            "  `inline fun setupButton(crossinline onClick: () -> Unit) { button.setOnClickListener { onClick() } }`\n"
            "  هنا `crossinline` إلزامي لأن `onClick` هتتنفذ مستقبلاً من الـ Android OS لما المستخدم يضغط، مش وقت استدعاء `setupButton`."
        ),
        "quick_answer": "Non-local returns allow a lambda inside an inline function to return from the enclosing function. crossinline forbids non-local returns when the lambda is executed in a different execution context like a callback or thread. noinline prevents inlining for specific lambda parameters, and reified preserves generic type parameters at runtime by copying type information into the call site.",
        "best_answer": (
            "These keywords fine-tune inlining behavior:\n\n"
            "A non-local return allows a return statement inside an inlined lambda to exit the outer enclosing function directly, behaving like a native language loop.\n\n"
            "crossinline is used when an inlined lambda is passed into a nested execution context—like an Android View click listener or a background thread. "
            "Because that context might execute after the outer function finishes, a non-local return is impossible. crossinline forbids non-local returns while keeping the lambda inlined.\n\n"
            "noinline disables inlining for a specific lambda parameter if you need to store it in a field or pass it to non-inlined code.\n\n"
            "Finally, reified is a massive productivity feature: because an inline function's bytecode is copied to the call site, the compiler knows the exact generic type argument and preserves it, "
            "allowing expressions like T::class.java without passing explicit Class tokens."
        ),
        "deep_answer": (
            "On the JVM, generic type arguments are erased at compile time (type erasure). Writing isInstance<T>() or T::class.java in standard methods is a compiler error because T is erased to Object. "
            "With inline functions, kotlinc eliminates type erasure via reification. At each call site, the compiler knows the concrete type (e.g., Gson.fromJson<UserProfile>()) "
            "and replaces T in the inlined bytecode with the actual bytecode representation of UserProfile.class. This enables clean JSON deserialization and dependency injection APIs without reflection.\n\n"
            "The distinction between inline, noinline, and crossinline is about lifecycle and escape analysis. An inlined lambda parameter cannot escape its calling scope unless it is non-inlined. "
            "If you attempt to assign an inlined lambda to a property or pass it to a non-inlined function, the compiler blocks you. Marking it noinline compiles it into a standard FunctionN reference, "
            "allowing it to escape.\n\n"
            "If the lambda is executed inside a local object or asynchronous callback, marking it crossinline permits inlining for performance while prohibiting non-local return statements, "
            "preventing illegal stack unwinding."
        ),
        "follow_ups": [
            {
                "interviewer": "Why does `reified` only work with `inline` functions?",
                "answer": "Because the JVM does not support reified generics at the bytecode instruction level. The only way Kotlin can provide reified types is by inlining the function body directly into the call site, where the compiler already knows the concrete type argument and can hardcode its `Class` reference directly into the calling bytecode."
            },
            {
                "interviewer": "What happens if you try to use `return` inside a `crossinline` lambda?",
                "answer": "The compiler produces an error: 'return is not allowed here'. You can only return from the lambda itself using labeled return syntax (`return@functionName`), which prevents attempting to unwind an outer stack frame that may have already returned."
            },
            {
                "interviewer": "When would you deliberately use `noinline` on one lambda in an inline function with two lambdas?",
                "answer": "When one lambda is executed immediately in a hot loop (and should be inlined for speed), but the second lambda is stored in a collection or passed to a worker thread for asynchronous execution. You mark the second lambda `noinline` so the compiler generates a heap-allocated `Function` reference for it."
            }
        ]
    },
    {
        "id": "KOT-14",
        "arabic_explanation": (
            "الـ Generics والـ Variance في Kotlin بتحدد إزاي الأنواع الفرعية (Subtypes) بتتعامل لما تتغلف جوه Generics:\n\n"
            "1. الـ Invariance (الوضع الافتراضي):\n"
            "   لو `Dog` بترث من `Animal`، فـ `List<Dog>` **مش** Subtype من `List<Animal>`. ده لمنع كوارث زي كتابة `Cat` جوه قائمة `Dogs`!\n\n"
            "2. الـ Covariance (`out`):\n"
            "   - الكلاس بيعمل **إنتاج للبيانات فقط (Producer Only)**.\n"
            "   - الـ `out T` بتسمح إن `List<Dog>` تكون Subtype من `List<Animal>`.\n"
            "   - القاعدة: تقدر تقرأ `T` (Return Type)، لكن مستحيل تدخله كـ Parameter (ممنوع في الـ `in` position). مثال: `List<out E>` في Kotlin هي Read-Only.\n\n"
            "3. الـ Contravariance (`in`):\n"
            "   - الكلاس بيعمل **استهلاك للبيانات فقط (Consumer Only)**.\n"
            "   - الـ `in T` بتعكس العلاقة: `Comparable<Animal>` بتعتبر Subtype من `Comparable<Dog>` (لأن اللي يقدر يقارن أي حيوان يقدر يقارن الكلاب بالتأكيد).\n"
            "   - القاعدة: تقدر تمرر `T` كـ Parameter، لكن مينفعش ترجعه.\n\n"
            "4. الـ Star Projection (`*`):\n"
            "   بتستخدمها لما متعرفش أو ميهمكش النوع الدقيق للـ Generic (زي `List<*>`)؛ ده بيعادل `List<out Any?>`، يعني تقدر تقرأ منها بأمان كـ `Any?` لكن مستحيل تكتب فيها."
        ),
        "practical_walkthrough": (
            "في معمارية أندرويد:\n"
            "- الـ StateFlow والـ LiveData هي Covariant (`StateFlow<out T>`): ده بيسمح إن `StateFlow<UserUiState.Success>` تتمرر لدالة مستنية `StateFlow<UserUiState>` بدون أي مشاكل.\n"
            "- في الـ Repository، واجهة القراءة فقط بنعمل لها Covariant:\n"
            "  `interface ReadOnlyRepository<out T> { fun getById(id: String): T }`\n"
            "- بينما الـ Serializer أو الـ Consumer بنعمل له Contravariant:\n"
            "  `interface JsonWriter<in T> { fun write(item: T): String }`\n"
            "- الخطأ الشائع: محاولة وضع دالة `fun update(item: T)` داخل واجهة متعلمة بـ `out T`؛ المترجم هيرفض البناء فوراً: \"Type parameter T is declared as 'out' but occurs in 'in' position\"."
        ),
        "quick_answer": "Variance governs subtyping of generic types. Invariant types require exact type matches. Covariant (out) types are producers that allow subtypes (List<Dog> is a subtype of List<Animal>) but restrict T from input positions. Contravariant (in) types are consumers that reverse subtyping (Comparable<Animal> is a subtype of Comparable<Dog>) and restrict T from return positions. Star projection represents unknown types safely.",
        "best_answer": (
            "Variance defines how subtyping between base types relates to subtyping between generic types parameterized by them.\n\n"
            "By default, generics in Kotlin are invariant: a MutableList of Dog is not a subtype of MutableList of Animal, which prevents adding a Cat to a list of Dogs.\n\n"
            "When a class only produces data, we mark it covariant using out. For example, Kotlin's read-only List is declared as List<out E>. "
            "This allows a List of Dog to be passed wherever a List of Animal is expected, but the compiler forbids E in parameter input positions.\n\n"
            "Conversely, when a class only consumes data, we mark it contravariant using in, like Comparable<in T>. "
            "This inverts subtyping: a comparator that handles all Animals can safely be used to compare Dogs.\n\n"
            "Star projection (*) is used when the type argument is unknown, safely allowing reads as Any? while preventing writes."
        ),
        "deep_answer": (
            "Kotlin's variance system improves on Java's wildcard generics (? extends T and ? super T) by supporting declaration-site variance. "
            "In Java, variance must be repeated at every call site (e.g., List<? extends Animal>). In Kotlin, we declare variance on the interface definition itself (e.g., interface Source<out T>), "
            "and all call sites automatically inherit covariant subtyping without wildcard annotations.\n\n"
            "Kotlin still supports use-site variance (type projections) for invariant classes like Array or MutableList. Writing copy(from: Array<out Any>, to: Array<in Any>) "
            "applies Java-style PECS (Producer Extends, Consumer Super) at specific call sites.\n\n"
            "Under the hood, declaration-site variance is enforced strictly by the compiler's position checker. If a type parameter is marked out, "
            "it can only appear in output positions (return types, read-only property types). If marked in, it can only appear in input positions (method parameters). "
            "If an out type parameter genuinely needs to be accepted in an internal private method or constructor, it must be annotated with @UnsafeVariance to bypass compiler checks, "
            "a technique used carefully inside Kotlin's standard library collections."
        ),
        "follow_ups": [
            {
                "interviewer": "Why is Kotlin's `List<T>` covariant (`out T`), while `MutableList<T>` is invariant?",
                "answer": "`List<T>` is read-only, meaning it only produces items. Passing `List<Dog>` to a function expecting `List<Animal>` is completely type-safe because callers can only read `Animal` instances. `MutableList<T>` allows writing: if `MutableList<Dog>` could be passed as `MutableList<Animal>`, a caller could add a `Cat` to it, crashing the app when retrieving a `Dog` later."
            },
            {
                "interviewer": "What is the difference between `List<*>` and `List<Any>`?",
                "answer": "`List<Any>` requires a list parameterized specifically with `Any` (or subtypes if covariant). `List<*>` represents a list of an unknown type. You can read from `List<*>` safely as `Any?`, but you cannot add anything into it (except null, if permitted). It acts as an abstraction over any list type regardless of its generic argument."
            },
            {
                "interviewer": "What is `@UnsafeVariance`, and why is it used in `Collection.contains(element: @UnsafeVariance E)`?",
                "answer": "In `Collection<out E>`, `E` is covariant. However, `contains(element: E)` takes `E` in an input position, which violates covariance rules. In reality, `contains` only reads the element to call `.equals()` and never mutates the collection. `@UnsafeVariance` suppresses the compiler error where the author mathematically proves that the operation is safe."
            }
        ]
    },
    {
        "id": "KOT-15",
        "arabic_explanation": (
            "الـ Delegation (التفويض) في Kotlin بيمثل تطبيق أصيل لمبدأ \"Composition over Inheritance\"، وعندنا نوعين رئيسيين:\n\n"
            "1. تفويض الواجهات (Interface Delegation بـ `by`):\n"
            "   - بيسمح لك تعمل Decorator Pattern بسطر واحد بدون كتابة Boilerplate تفويض لكل دالة يدوياً.\n"
            "   - `class LoggingRepository(private val inner: Repository) : Repository by inner`\n"
            "   - المترجم بيولد تلقائياً كل دوال `Repository` وبيخليها تنادي `inner.method()`. وأي دالة محتاج تغير سلوكها بتعمل لها `override` فقط!\n\n"
            "2. تفويض الخصائص (Property Delegation بـ `by`):\n"
            "   - بيسمح بتفويض قراءة (`getValue`) أو كتابة (`setValue`) المتغير لكائن خارجي (Delegate Object).\n"
            "   - أمثلة شهيرة: `by lazy`، و `by Delegates.observable` (للرد على تغير القيمة)، و `by viewModels()` في أندرويد، و `by remember { mutableStateOf() }` في Jetpack Compose.\n\n"
            "في الـ Bytecode، المترجم بيولد حقل مخفي (Synthetic Field) اسمه `prop$delegate`، وكل قراءة بتتحول لاستدعاء `delegate.getValue(this, ::prop)`."
        ),
        "practical_walkthrough": (
            "في شاشات أندرويد:\n"
            "- تفويض الـ ViewModels: `val viewModel: UserViewModel by viewModels()` بيفوض إنشاء وإدارة دورة حياة الـ ViewModel لـ Android Jetpack `ViewModelLazy`.\n"
            "- تفويض المراقبة: `var count: Int by Delegates.observable(0) { prop, old, new -> updateBadge(new) }` بيحدث الـ UI تلقائياً كل ما القيمة تتغير.\n"
            "- تفويض الـ SharedPreferences: نقدر نعمل Custom Delegate يخزن ويقرأ من الـ DataStore أو الشيرد بريفرنسز تلقائياً بدون تكرار كود الحفظ والقراءة في كل مكان."
        ),
        "quick_answer": "Delegation implements composition over inheritance natively. Interface delegation allows a class to implement an interface by delegating all method calls to an internal instance. Property delegation delegates getter and setter logic to a separate object implementing getValue and setValue, powering features like by lazy, by viewModels, and Compose state.",
        "best_answer": (
            "Kotlin natively supports the delegation pattern for both interfaces and properties using the by keyword.\n\n"
            "Interface delegation enables clean decorators without boilerplate: by writing class AnalyticsRepo(inner: Repo) : Repo by inner, "
            "the compiler automatically forwards all interface methods to inner, letting me override only the methods I want to intercept.\n\n"
            "Property delegation delegates a property's getter and setter to a delegate object implementing getValue and setValue. "
            "This powers fundamental Android utilities like by lazy for deferred initialization, by viewModels() for lifecycle-scoped ViewModel acquisition, and Jetpack Compose's mutableStateOf delegates.\n\n"
            "It promotes separation of concerns by encapsulating repetitive state or storage logic in reusable delegate classes."
        ),
        "deep_answer": (
            "Under the hood, property delegation relies on operator conventions. For a read-only val, the delegate class must implement an operator function: "
            "operator fun getValue(thisRef: Any?, property: KProperty<*>): T. For a var, it must also provide operator fun setValue(thisRef: Any?, property: KProperty<*>, value: T).\n\n"
            "The compiler generates a private backing field for the delegate named property$delegate and replaces all property reads with delegate.getValue(this, KProperty). "
            "Starting in modern Kotlin versions, if the delegate does not utilize the KProperty metadata, the compiler optimizes away the KProperty allocation to eliminate reflection overhead.\n\n"
            "Interface delegation compiles by generating forwarding methods for every interface member in the implementing class. However, an important caveat is that delegated methods "
            "do not have polymorphic access to the outer decorator class: inside the delegate, this refers to the delegate instance, not the wrapper. In production Android codebases, "
            "we use custom property delegates for DataStore persistence and Fragment lifecycle binding cleanup."
        ),
        "follow_ups": [
            {
                "interviewer": "How does `by Delegates.observable` work, and when would you use it?",
                "answer": "`Delegates.observable` takes an initial value and a lambda callback `(property, oldValue, newValue) -> Unit`. Every time the property is assigned a new value, the delegate executes the callback. It is useful for lightweight internal state changes or updating a UI badge when an in-memory counter changes."
            },
            {
                "interviewer": "Does using property delegates impact memory and performance?",
                "answer": "Yes, slightly. Each delegated property allocates an additional backing delegate object on the heap, and accessing the property involves a method call indirection (`getValue`). For typical UI components or ViewModels, the overhead is negligible, but inside hot rendering loops or tight mathematical routines, plain primitive fields are preferred."
            },
            {
                "interviewer": "What happens if a class overrides a method that is also delegated via interface delegation `by inner`?",
                "answer": "The explicit class override takes precedence. The compiler generates the overriding implementation in the class body, and external calls execute your overridden method instead of forwarding to the `inner` delegate."
            }
        ]
    }
]


def main() -> None:
    combined = []
    seen = set()
    for q in existing:
        combined.append(q)
        seen.add(q["id"])

    for q in KOT_11_20:
        if q["id"] not in seen:
            combined.append(q)
            seen.add(q["id"])

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(combined, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions through KOT-15. Total questions: {len(combined)}")


if __name__ == "__main__":
    main()

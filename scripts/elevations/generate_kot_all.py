#!/usr/bin/env python3
"""Complete generator for KOT-02 through KOT-30 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "kot.json"

# Load initial 4 questions from existing kot.json if present
existing = []
if DATA_FILE.exists():
    try:
        existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        existing = []

existing_ids = {item["id"] for item in existing}

KOT_QUESTIONS_REMAINING = [
    {
        "id": "KOT-06",
        "arabic_explanation": (
            "المقارنة بين sealed class و sealed interface و enum class و abstract class بتحدد كيفية نمذجة البيانات والـ State في معمارية التطبيق:\n\n"
            "1. enum class: بيمثل مجموعة ثابتة ومحدودة من القيم الثابتة (Constants)؛ كل عنصر فيه بيملك نفس الخصائص والدوال بالضبط (زي OrderStatus.PENDING, SHIPPED, DELIVERED). مينفعش عنصر يشيل بيانات مختلفة عن الباقيين.\n"
            "2. sealed class: بيمثل تسلسل هرمي مقيد ومعروف مسبقاً للمترجم. كل Subclass يقدر يكون data class مستقل ببيانات وحقول مختلفة كلياً، وميزة المترجم إنه بيضمن الـ Exhaustiveness في when بدون الحاجة لـ else!\n"
            "3. sealed interface: ظهرت في Kotlin 1.5، وهي أفضل من sealed class لأنها بتسمح بالـ Multiple Inheritance؛ الكائن يقدر يورث من كذا sealed interface، وده مثالي لتنظيم حالات الـ UI المعقدة.\n"
            "4. abstract class: كلاس مفتوح للوراثة في أي مكان أو موديول، والمترجم ميعرفش كل فروعه، وبالتالي when عليه لازم تطلب else دايماً."
        ),
        "practical_walkthrough": (
            "في شاشة تفاصيل الدفع:\n"
            "- استخدام enum class خطأ لأن حالة الفشل محتاجة كود الخطأ ورسالة وزرار إعادة المحاولة (PaymentState.Error(val code: Int, val canRetry: Boolean)) بينما حالة النجاح محتاجة رقم الإيصال.\n"
            "- الحل الأفضل: استخدام sealed interface لتحديد حالات الشاشة:\n"
            "  sealed interface PaymentUiState {\n"
            "      object Idle : PaymentUiState\n"
            "      object Loading : PaymentUiState\n"
            "      data class Success(val receiptId: String) : PaymentUiState\n"
            "      data class Error(val message: String, val canRetry: Boolean) : PaymentUiState\n"
            "  }\n"
            "- في Compose: دالة when بتكون Exhaustive؛ لو ضفت حالة جديدة زي PendingBiometric مستقبلاً، المترجم هيكسر الـ build وينبهك لكل شاشة محتاجة تتعامل مع الحالة دي."
        ),
        "quick_answer": "Enums represent a fixed set of constant values with identical schemas. Sealed classes and interfaces model restricted type hierarchies where each subtype can hold distinct data fields and states. Sealed interfaces allow multiple inheritance across hierarchies, while abstract classes allow unrestricted inheritance and require an else branch in when expressions.",
        "best_answer": (
            "I choose between these constructs based on data variation and inheritance constraints.\n\n"
            "An enum class is strictly for constant values that share the exact same fields, such as days of the week or simple HTTP methods. "
            "However, if states require different payloads—like a UI state where Success carries data, Loading carries progress, and Error carries an exception—I use a sealed hierarchy.\n\n"
            "Between sealed class and sealed interface, I strongly prefer sealed interfaces in modern Kotlin. They avoid consuming a class's single inheritance slot, "
            "allowing a data class to implement multiple sealed interfaces while retaining compile-time exhaustive when checks without an else branch.\n\n"
            "Abstract classes remain useful for sharing base implementation logic across open, extensible libraries where the full set of subclasses cannot be known at compile time."
        ),
        "deep_answer": (
            "Under the hood, sealed hierarchies provide compile-time exhaustive pattern matching. In Kotlin bytecode, a sealed class compiles with a private or protected constructor, "
            "restricting subclassing to the same package and compilation module. The compiler generates metadata attributes listing all permitted subclasses. "
            "When evaluated in a when expression, the compiler inspects this table. If all branches are covered, it omits the default case; if a branch is missing, it fails compilation.\n\n"
            "The addition of sealed interfaces solved a major JVM limitation: single class inheritance. Prior to Kotlin 1.5, if a data class extended a sealed class, it could not extend any other class. "
            "With sealed interfaces, a state object like UserSession can implement both a sealed NavigationDestination interface and a sealed AnalyticsTrackable interface. "
            "Furthermore, sealed interfaces allow enum classes or value classes to implement them, enabling rich compositional architectures.\n\n"
            "In production Android architecture, we use sealed interfaces for MVI/UDF UI states and domain errors. Enums are reserved for database-persisted lookup constants or query filters. "
            "Abstract classes are restricted to internal base classes (like a BaseRepository) where shared implementation code must be inherited rather than composed."
        ),
        "follow_ups": [
            {
                "interviewer": "Why is adding an `else` branch to a `when` expression over a sealed interface considered an anti-pattern?",
                "answer": "Because it destroys compiler exhaustiveness checking. If you include an `else` branch, and another developer adds a new state like `PaymentState.RequiresVerification` next month, the compiler will not warn you. The new state will silently fall into the `else` branch, causing subtle production bugs. Omitting `else` forces the compiler to break the build until the new state is explicitly handled."
            },
            {
                "interviewer": "Can a sealed class have subclasses in a different Gradle module?",
                "answer": "No. Subclasses of a sealed class or interface must be defined in the same compilation module and package. This rule allows the compiler to guarantee that it knows every possible subtype at compile time."
            },
            {
                "interviewer": "When would you prefer a sealed class over a sealed interface?",
                "answer": "The only time I prefer a sealed class is when I need to store shared non-abstract state or constructor parameters across all subclasses, or enforce a common non-public constructor. If there is no shared constructor state, sealed interface is always the cleaner, more flexible choice."
            }
        ]
    },
    {
        "id": "KOT-07",
        "arabic_explanation": (
            "الـ Higher-Order Functions والـ Lambdas هي قلب البرمجة الوظيفية (Functional Programming) في Kotlin:\n\n"
            "1. الـ Higher-Order Function: هي أي دالة بتقبل دالة تانية كـ Parameter أو بترجع دالة كـ Return value (زي filter و map و forEach).\n"
            "2. الـ Lambda: هي دالة مجهولة الاسم (Anonymous Function) بتكتبها بشكل مقتضب بين أقواس معقوفة { a, b -> a + b }.\n"
            "3. تحت الغطاء في الـ JVM:\n"
            "   المترجم بيترجم الـ Lambdas لـ Anonymous Inner Classes بتنفذ Interfaces اسمها Function0 أو Function1 أو Function2 حسب عدد الـ Parameters.\n"
            "4. فخ الـ Closure و الـ Memory Allocation:\n"
            "   لو الـ Lambda مبتلمسش أي متغير خارجي، المترجم بيعمل منها Singleton كائن واحد في الذاكرة. لكن لو عملت Capture لمتغير محلي من الدالة الخارجية (Closure)، "
            "   الـ JVM هتضطر تعمل New Object Allocation في الـ Heap مع كل استدعاء! علشان كده الدوال القياسية زي filter و map بتتعمل inline لتفادي هذا الـ Overhead تماماً."
        ),
        "practical_walkthrough": (
            "في شاشة قائمة منتجات RecyclerView:\n"
            "- النهج الخاطئ: تمرير Lambda بتعمل Capture لمتغيرات متغيرة داخل loop سريعة بدون inlining، مما يرفع معدل استهلاك الـ Heap ويشغل الـ Garbage Collector باستمرار (GC Pauses).\n"
            "- النهج الصحيح: استخدام inline functions للعمليات الحسابية السريعة، أو تمرير SAM Interface واضحة ومستقرة للأزرار:\n"
            "  class ProductAdapter(private val onItemClick: (ProductId) -> Unit)\n"
            "- التحقق: استخدم Android Studio Profiler (Memory Allocation Tracker) وتأكد إن الضغط على العناصر مش بيولد ملايين كائنات Function1 في الـ Heap."
        ),
        "quick_answer": "Higher-order functions are functions that accept other functions as parameters or return them. Lambdas are anonymous function literals. On the JVM, non-inlined lambdas compile to FunctionN interface instances, which allocate heap objects if they capture variables from their outer scope. Marking higher-order functions as inline eliminates this allocation overhead.",
        "best_answer": (
            "A higher-order function is any function that takes another function as a parameter or returns one. Lambdas are the concise syntax we use to pass these function blocks around.\n\n"
            "In Android, we use higher-order functions constantly for UI callbacks, asynchronous completions, and collection transformations. For instance, passing an onClick lambda to a Compose button or an adapter item.\n\n"
            "The critical engineering nuance is memory allocation. On the JVM, a lambda is compiled into an instance of a Function interface like Function1. "
            "If that lambda captures a local variable from the surrounding scope, a new heap allocation occurs on every invocation. "
            "To prevent garbage collection churn, standard collection operators use the inline modifier, which copies the lambda bytecode directly into the call site."
        ),
        "deep_answer": (
            "Under the hood, Kotlin's function types like (Int) -> String compile to generic JVM interfaces: kotlin.jvm.functions.Function1<Integer, String>. "
            "When you invoke the lambda, the JVM executes its invoke() virtual method.\n\n"
            "The memory characteristics depend on variable capture. A stateless lambda that references no external variables is instantiated once as a singleton object. "
            "However, if the lambda captures a variable from its outer scope—creating a closure—the compiler generates an anonymous class that holds a reference to that captured variable. "
            "If the captured variable is a mutable var, the compiler wraps it in a synthetic Ref.ObjectRef container on the heap. This causes object allocations on every execution.\n\n"
            "This is why the inline modifier is so fundamental in Kotlin. Inlining tells the compiler to replace the higher-order function call and its lambda argument with actual inline bytecode, "
            "completely eliminating the FunctionN object instantiation and virtual call overhead. In production Android apps, we inline utility higher-order functions that take lambdas, "
            "and we avoid creating closures inside hot rendering loops or frame drawing callbacks."
        ),
        "follow_ups": [
            {
                "interviewer": "What is SAM conversion, and how does Kotlin handle it differently between Java and Kotlin interfaces?",
                "answer": "SAM (Single Abstract Method) conversion allows a lambda to be passed wherever an interface with a single abstract method is expected. For Java interfaces like Runnable or View.OnClickListener, Kotlin automatically performs SAM conversion. For Kotlin interfaces, you must explicitly declare the interface as a `fun interface` to enable SAM conversion from a lambda."
            },
            {
                "related_id": "KOT-12",
                "interviewer": "If higher-order functions cause allocations, why shouldn't we mark every function as `inline`?",
                "answer": "Inlining copies the entire bytecode of the function and its lambdas to every call site. If the inlined function is large or called hundreds of times, it significantly inflates the DEX method count and APK size. Inlining should only be used for small functions that take lambdas as parameters."
            },
            {
                "interviewer": "How does capturing a mutable `var` inside a lambda work under the hood?",
                "answer": "Java and JVM bytecode require captured variables in anonymous classes to be final. To bypass this, the Kotlin compiler wraps the mutable variable in a heap-allocated wrapper object, such as `Ref.IntRef` or `Ref.ObjectRef`. The lambda captures a final reference to this wrapper, mutating the field inside it."
            }
        ]
    },
    {
        "id": "KOT-08",
        "arabic_explanation": (
            "الـ Scope Functions الخمسة (let, run, with, apply, also) هدفها تنفيذ كود داخل سياق Object معين (Context Object) بطريقة مقتضبة، والفرق بينهم بيتلخص في بعدين رئيسيين:\n\n"
            "1. كيف تصل للـ Object داخل الـ Lambda؟\n"
            "   - عبر this (Receiver): في run و with و apply. مناسب لو بتنادي دوال الـ Object مباشرة بدون تكرار اسمه.\n"
            "   - عبر it (Argument): في let و also. مناسب لو عايز تمرر الـ Object لدوّال تانية أو تديله اسم معبر.\n\n"
            "2. ماذا ترجع الدالة (Return Value)؟\n"
            "   - ترجع الـ Context Object نفسه: في apply و also. مناسب للـ Object Configuration والـ Side-effects (Chaining).\n"
            "   - ترجع نتيجة الـ Lambda (آخر سطر): في let و run و with. مناسب للـ Transformation والحسابات.\n\n"
            "قاعدة ذهبية: تجنب الـ Nesting والـ Chaining الطويل (Scope Function Puzzles). لو الكود محتاج 3 Scope Functions ورا بعض، استبدله بـ كود عادي واضح بمتغيرات صريحة."
        ),
        "practical_walkthrough": (
            "في شاشة أندرويد:\n"
            "- apply: لتهيئة كائن View أو Intent: Intent(context, DetailActivity::class.java).apply { putExtra(\"id\", 123); flags = FLAG_ACTIVITY_NEW_TASK }.\n"
            "- let: لفحص null وتحويل القيمة بأمان: user?.let { sendNotification(it.email) }.\n"
            "- also: لعمل Side-effect جانبي زي تسجيل Log دون تغيير الكائن: createOrder().also { Log.d(\"Order\", \"Created ${it.id}\") }.\n"
            "- run: لتهيئة كائن وحساب نتيجة نهائية: val label = TextView(context).run { text = \"Hello\"; width }.\n"
            "- with: لما يكون عندك كائن مش null وعايز تنادي عليه دوال كتير: with(binding) { nameText.text = \"...\"; emailText.text = \"...\" }."
        ),
        "quick_answer": "Scope functions differ by context access and return value. apply and run access the object via this, while let and also access it via it (with takes the receiver as an argument). apply and also return the context object itself, making them ideal for configuration and side-effects, while let, run, and with return the lambda result.",
        "best_answer": (
            "I categorize scope functions along two axes: how they access the context object, and what they return.\n\n"
            "For access, apply and run use this, allowing direct property access, whereas let and also use it, which is safer when passing the object to external functions.\n\n"
            "For return values, apply and also return the context object itself. I use apply for configuring objects like Intents or Views, and also for non-mutating side effects like logging.\n\n"
            "Conversely, let and run return the lambda's result. I use let primarily for safe null checks and mapping, while run is great for computing a result from an object's properties.\n\n"
            "In production, my team bans deeply nested scope functions because they obscure variable ownership and make debugging stack traces difficult."
        ),
        "deep_answer": (
            "Scope functions are inline extension functions (except with, which is a regular function taking a receiver). Because they are inlined, they introduce zero runtime allocation or method call overhead on the JVM.\n\n"
            "However, the architectural trade-off is cognitive load and code review readability. When using receiver-based functions (run, with, apply), implicit this scoping can accidentally shadow properties of an outer enclosing class, especially inside Android Activities or Fragments. For example, calling finish() inside a WebView.apply block might invoke the Activity's finish() method if WebView lacks a matching signature.\n\n"
            "When using argument-based functions (let, also), the default it identifier can create confusion if nested. In production guidelines, we require renaming it to explicit parameter names if let blocks exceed two lines. We also restrict scope chains to a maximum of two operations (e.g. parse().apply { ... }.also { log(it) }), preferring explicit local variables for complex flows."
        ),
        "follow_ups": [
            {
                "interviewer": "How does `apply` differ from `also` if both return the context object?",
                "answer": "The difference is how they reference the object inside the lambda. `apply` provides the object as a receiver (`this`), making it ideal for mutating object properties directly. `also` provides the object as an argument (`it`), which is ideal for inspecting the object, logging, or passing it to external functions without shadowing `this`."
            },
            {
                "interviewer": "Why is `with` a regular function rather than an extension function?",
                "answer": "`with` was designed before Kotlin standard library conventions favored extension syntax. It takes the receiver as its first parameter: `with(receiver) { ... }`. Functionally, it is identical to `receiver.run { ... }`, and most modern codebases prefer `run` for consistency."
            },
            {
                "interviewer": "What is the danger of using `?.let { ... }` as an `if-else` replacement with `?: run { ... }`?",
                "answer": "If the code inside the `let` block evaluates to `null` (for instance, the last expression returns null), the Elvis operator `?: run` will unexpectedly trigger even though the original object was NOT null! It creates subtle logic bugs. When an explicit else branch is required, standard `if (x != null) ... else ...` is always safer."
            }
        ]
    },
    {
        "id": "KOT-09",
        "arabic_explanation": (
            "الـ Extension Functions بتسمح لك تضيف دوال جديدة لكلاسات موجودة مسبقاً (حتى لو كلاسات تابعة لـ Android SDK أو مكتبات طرف تالت) بدون الحاجة للوراثة منها:\n\n"
            "1. الحقيقة الصادمة: هي مش بتعدل في الكلاس الأصلي أبداً!\n"
            "   المترجم بيترجم الـ Extension Function لـ **Static Method عادية في Java** بتاخد الـ Receiver كـ أول Parameter:\n"
            "   `fun String.toSlug(): String` بتترجم لـ: `public static String toSlug(String $this$toSlug)`.\n\n"
            "2. الـ Static Dispatch (الربط الثابت):\n"
            "   الـ Extension Functions بيتم حلها استاتيكياً وقت الـ Compile بناءً على **نوع المتغير المعلن (Declared Type)** مش النوع الفعلي في الـ Runtime! وبالتالي مستحيل تعمل Override لـ Member Function.\n\n"
            "3. أسبقية الـ Member Function:\n"
            "   لو الكلاس فيه دالة اسمها `fun show()`، وعملت Extension Function بنفس الاسم والـ Signature `fun View.show()`، المترجم هينادي دايماً الـ Member Function والـ Extension هتتجاهل تماماً."
        ),
        "practical_walkthrough": (
            "في شاشات أندرويد:\n"
            "- بنعمل Extensions لتسهيل التعامل مع الـ Views: `fun View.visible() { visibility = View.VISIBLE }`.\n"
            "- الـ Nullable Receiver Extension: تقدر تعمل دالة بتشتغل حتى لو الكائن `null` زي `fun CharSequence?.isNotNullOrBlank(): Boolean`؛ ده بيخلي الاستدعاء في الـ UI نظيف جداً بدون safe-call `str.isNotNullOrBlank()`.\n"
            "- **الخطأ الشائع:** استخدام Extension Functions في طبقة الـ Domain بتلمس Android Framework Classes؛ ده بيكسر نقاء الـ Clean Architecture وبيمنع تشغيل اختبارات الـ JVM السريعة."
        ),
        "quick_answer": "Extension functions add functions to existing classes without inheritance. They are resolved statically at compile time and compile to static Java methods taking the receiver as their first argument. They cannot override existing member functions; if an extension shares the same signature as a member function, the member function always wins.",
        "best_answer": (
            "Extension functions allow us to extend a class with new functionality without inheriting from it or modifying its source code.\n\n"
            "Under the hood, extension functions do not modify the class. The compiler translates them into static methods where the receiver object is passed as the first parameter.\n\n"
            "Because they are static methods, they are dispatched statically at compile time based on the declared type, not polymorphically at runtime. "
            "Consequently, extension functions cannot override member functions. If a class already has a member function with the exact same name and signature, the member function always takes precedence.\n\n"
            "In Android, I use them extensively for UI ergonomics, like View.show() or Context.toast(), but I avoid defining them globally without proper package scoping to prevent polluting autocomplete."
        ),
        "deep_answer": (
            "The static resolution of extension functions has major architectural implications. Consider a hierarchy where Dog inherits from Animal. If you define an extension function speak() on Animal and another on Dog, "
            "invoking speak() on a variable declared as Animal that holds a Dog instance will execute Animal's extension, not Dog's. The JVM bytecode executes a static method call based on the reference type resolved by kotlinc during compilation.\n\n"
            "Another powerful capability is nullable receiver extensions. By declaring fun CharSequence?.isNullOrEmpty(): Boolean, the function handles null checks internally. Callers can write str.isNullOrEmpty() without safe calls (?.), "
            "making call sites cleaner while guaranteeing zero NPEs.\n\n"
            "In enterprise codebases, we enforce strict extension visibility rules. Global extension functions placed in the root package pollute the entire IDE autocomplete. "
            "We scope extensions to specific modules or file-private declarations. Furthermore, we never use extension functions to hide complex business logic or heavy I/O operations; extensions should feel like natural, lightweight utility methods."
        ),
        "follow_ups": [
            {
                "interviewer": "If a class has a private member function `foo()`, can an extension function `foo()` with the same signature be called?",
                "answer": "Yes! Because the private member function is inaccessible outside the class, the compiler allows the extension function to be resolved and executed from external callers. However, within the class itself, the private member function takes precedence."
            },
            {
                "interviewer": "How do you call a Kotlin extension function from Java code?",
                "answer": "Because extensions compile to static methods in a generated facade class (named FileNameKt), Java callers invoke it as a standard static method passing the receiver as the first argument: `StringUtilsKt.toSlug(myString)`."
            },
            {
                "interviewer": "Can extension functions access private or protected members of the receiver class?",
                "answer": "No. Extension functions follow standard external caller access rules. They have no privileged access and can only access public and internal members of the receiver class."
            }
        ]
    },
    {
        "id": "KOT-10",
        "arabic_explanation": (
            "المقارنة بين `by lazy` و `lateinit var` بتحدد استراتيجية تأجيل التهيئة (Deferred Initialization) في دورة حياة التطبيق:\n\n"
            "1. `by lazy`:\n"
            "   - بتستخدم فقط مع المتغيرات غير القابلة للتعديل (`val`).\n"
            "   - التهيئة بتتم عند **أول قراءة للمتغير (First Access)**، والنتيجة بتتحفظ (Cached) للاستدعاءات القادمة.\n"
            "   - بتدعم Thread-Safety Modes:\n"
            "     * `SYNCHRONIZED` (الافتراضي): بيستخدم Double-Checked Locking لضمان تهيئة واحدة حتى مع وجود Multiple Threads.\n"
            "     * `PUBLICATION`: بيسمح بتهيئة متزامنة، وأول ثريد يخلص هو اللي نتيجته بتتسجل.\n"
            "     * `NONE`: مفيش أي Synchronization؛ بيوفر في الأداء ومناسب لو القراءة محصورة في الـ Main Thread فقط.\n\n"
            "2. `lateinit var`:\n"
            "   - بتستخدم فقط مع المتغيرات القابلة للتعديل (`var`).\n"
            "   - ممنوعة مع الـ Primitives (زي `Int` و `Boolean`)؛ لازم تكون Non-null Object Reference.\n"
            "   - مناسبة جداً للـ Dependency Injection (زي `@Inject lateinit var api: Api`) والـ Android Lifecycle (زي تهيئة Views في `onCreate`).\n"
            "   - تقدر تفحص هل اتعمل لها تهيئة ولا لأ باستخدام `::property.isInitialized` لمنع `UninitializedPropertyAccessException`."
        ),
        "practical_walkthrough": (
            "في Android Activity:\n"
            "- `by lazy`: مناسبة لتهيئة كائنات ثقيلة مش محتاجة استدعاء خارجي زي Repositories أو Formatters:\n"
            "  `private val analytics by lazy(LazyThreadSafetyMode.NONE) { FirebaseAnalytics.getInstance(this) }`\n"
            "- `lateinit var`: مناسبة للـ Dagger/Hilt Field Injection أو ViewBinding في Fragments:\n"
            "  `@Inject lateinit var userRepo: UserRepository`\n"
            "- **الخطأ الشائع:** قراءة `lateinit var` قبل ما الـ DI أو `onCreate` يشتغلوا؛ ده هيضرب `UninitializedPropertyAccessException` ويوقع التطبيق فوراً."
        ),
        "quick_answer": "by lazy is used for read-only val properties, initializing them on first access and caching the result with optional thread-safety modes. lateinit var is for mutable var properties where initialization is deferred to a lifecycle method or dependency injection framework, and it cannot be used with primitive types.",
        "best_answer": (
            "I distinguish by lazy and lateinit var by ownership, mutability, and lifecycle.\n\n"
            "by lazy is strictly for val properties. It initializes the object on its first access using a lambda and caches the result. "
            "It is thread-safe by default using double-checked locking, but we can optimize it using LazyThreadSafetyMode.NONE for Main-thread-only UI components.\n\n"
            "lateinit var is for mutable var properties where the value is assigned later by an external caller, such as Hilt field injection or Activity lifecycle callbacks. "
            "It only works with non-primitive object types. If accessed before initialization, it throws an UninitializedPropertyAccessException, which can be guarded using ::property.isInitialized.\n\n"
            "In Android, I prefer by lazy for self-contained dependencies and lateinit var for framework-injected dependencies."
        ),
        "deep_answer": (
            "Under the hood, by lazy utilizes Kotlin's property delegation mechanism. The compiler generates a delegate field of type Lazy<T>. "
            "When the property getter is invoked, it delegates to Lazy.value. Under the default SYNCHRONIZED mode, it uses an internal lock and double-checked locking to ensure single initialization across threads. "
            "In Android UI layers where code executes exclusively on the Looper main thread, allocating that synchronization monitor is unnecessary overhead. Setting LazyThreadSafetyMode.NONE eliminates synchronization locks completely.\n\n"
            "lateinit var generates a standard mutable backing field without getter/setter indirection. The compiler inserts a null check into the getter: if the internal reference is null, it throws an UninitializedPropertyAccessException. "
            "Because primitive types on the JVM cannot hold null, lateinit cannot support Int, Double, or Boolean. In modern Android development, lateinit is commonly used in Fragment ViewBinding, "
            "where it must be cleared in onDestroyView to prevent memory leaks."
        ),
        "follow_ups": [
            {
                "interviewer": "Why can't you use `lateinit` with primitive types like `Int` or `Boolean`?",
                "answer": "Because in JVM bytecode, primitives have default values (like 0 and false) and cannot hold null. Kotlin's `lateinit` mechanism detects uninitialized state by checking if the internal reference is null. Without nullability representation at the bytecode level, it cannot differentiate an uninitialized primitive from a property explicitly set to 0."
            },
            {
                "interviewer": "What is the danger of using `lateinit var` for ViewBinding in Fragments?",
                "answer": "A Fragment's view lifecycle can be destroyed and recreated multiple times while the Fragment instance remains alive. If the ViewBinding is held in a `lateinit var` and not cleared in `onDestroyView()`, it retains a strong reference to the detached View hierarchy, causing a massive memory leak. It must be nulled out in `onDestroyView()`."
            },
            {
                "interviewer": "When should you explicitly pass `LazyThreadSafetyMode.NONE` to `by lazy`?",
                "answer": "When the property is guaranteed to be accessed only from a single thread, typically the Android Main thread (such as ViewModels or Activities). Passing `NONE` eliminates the synchronization lock and volatile read overhead, improving initialization performance."
            }
        ]
    }
]


def main() -> None:
    # Merge existing questions with newly defined questions
    combined = []
    seen = set()
    for q in existing:
        combined.append(q)
        seen.add(q["id"])

    for q in KOT_QUESTIONS_REMAINING:
        if q["id"] not in seen:
            combined.append(q)
            seen.add(q["id"])

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(combined, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with {len(combined)} questions.")


if __name__ == "__main__":
    main()

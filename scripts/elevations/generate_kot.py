#!/usr/bin/env python3
"""Generator for KOT (Kotlin Core & Advanced) elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "kot.json"

KOT_DATA = [
    {
        "id": "KOT-02",
        "arabic_explanation": (
            "علشان تفهم الفرق بين val و var بعمق، لازم تفصل تماماً بين مفهومين في الـ Memory: الـ Reference (المؤشر) والـ Object نفسه في الـ Heap.\n\n"
            "val في Kotlin تعني Read-Only Reference؛ يعني بمجرد ما المتغير يشاور على مكان في الـ Heap، مستحيل تخليه يشاور على مكان تاني (Reassignment ممنوع زي final في Java). "
            "لكن ده مش معناه أبداً إن الـ Object نفسه بقى Immutable (غير قابل للتعديل)!\n"
            "- لو كتبت val cart = mutableListOf(\"Phone\")، الـ Reference cart ثابت، بس تقدر تعمل cart.add(\"Case\") عادي جداً لأن الـ Object اللي جوه الـ Heap نوعه MutableList.\n"
            "- حتى لما تستخدم List<T> في Kotlin، هي بتديك Read-Only Interface فقط، وممكن تكون تحت الغطاء ArrayList عادية وأي مؤشر تاني يقدر يعدل فيها!\n\n"
            "في الـ Concurrency، الـ val لا توفر أي Thread-Safety للمحتوى. لو عندك ثريد بيقرأ من val list = mutableListOf() وثريد تاني بيكتب فيها، "
            "هيحصل Race Condition و ConcurrentModificationException فوراً."
        ),
        "practical_walkthrough": (
            "في تطبيق تجارة إلكترونية، تخيل كلاس Cart State Holder:\n"
            "- النهج الخاطئ: كشف val items = mutableListOf<CartItem>() كـ Public Property. أي شاشة تقدر تعمل items.add(newItem) مباشرة من غير ما تعدي على الـ ViewModel، وبالتالي الـ UI مش هيجيلها State Update والـ State هتتشتت بين الشاشات.\n"
            "- النهج الصحيح: إخفاء الـ Mutable State داخل الـ ViewModel، ونشر Snapshot غير قابل للتعديل:\n"
            "  private val _items = mutableListOf<CartItem>()\n"
            "  val items: List<CartItem> get() = _items.toList()\n"
            "- التحقق: اكتب Unit Test يثبت إن استدعاء add على الـ Mutable List الداخلية بعد أخذ الـ Snapshot مش بيغير القائمة القديمة المعروضة في الـ UI."
        ),
        "quick_answer": "val prevents rebinding a reference to a new memory address, while var allows reassignment. However, val does not make the referenced object immutable. A val pointing to a MutableList can still have its elements modified, and sharing it across threads requires explicit synchronization or defensive copies.",
        "best_answer": (
            "In Kotlin, val defines a read-only reference, meaning you cannot reassign that variable once initialized. "
            "But it is crucial to remember that val does not guarantee object immutability. If a val references a mutable collection like a MutableList, "
            "the object in the heap can still be mutated freely.\n\n"
            "In Android ViewModels, if I expose a val MutableList to the UI, other components could modify items directly without triggering state emissions, "
            "or concurrent background threads could trigger a ConcurrentModificationException.\n\n"
            "My rule in production is to use val by default for all references, keep mutable state private, and expose only immutable data classes or "
            "defensive list copies using toList. That separates reference immutability from actual object and state stability."
        ),
        "deep_answer": (
            "When discussing val versus var, I evaluate three distinct concerns: reference rebinding, object state mutability, and thread safety. "
            "The Kotlin compiler translates a local val into a regular Java local variable without reassignment, and a val property into a private final field with a getter.\n\n"
            "However, object mutability is completely orthogonal. A val property pointing to an object with var fields or a mutable collection allows internal state changes. "
            "Furthermore, Kotlin's standard List interface is merely a read-only view, not an immutable collection. It omits mutating methods, but if the underlying JVM instance is an ArrayList, "
            "another reference with a MutableList interface can modify it concurrently.\n\n"
            "In an enterprise Android application, this distinction directly impacts architecture. In a repository or ViewModel, mutating a shared val collection across coroutine dispatchers "
            "causes race conditions because val provides no memory visibility or synchronization guarantees. To handle state safely, I encapsulate mutable collections privately and emit immutable "
            "snapshots to StateFlow. If defensive copying becomes a performance bottleneck under high-frequency updates, I use Kotlinx persistent collections rather than relaxing encapsulation."
        ),
        "follow_ups": [
            {
                "related_id": "KOT-25",
                "interviewer": "Does declaring a shared collection as val protect you from multithreaded race conditions?",
                "answer": "No, not at all. val only prevents the pointer itself from being reassigned to a different list instance. If two coroutines running on Dispatchers.Default and Dispatchers.IO concurrently append items to that same list, they will cause memory corruption or a ConcurrentModificationException. Thread safety requires mutual exclusion like Mutex, thread confinement, or immutable data structures."
            },
            {
                "related_id": "KOT-16",
                "interviewer": "If an API returns a read-only List, can a caller cast it to MutableList and modify it?",
                "answer": "On the JVM, Kotlin's List and MutableList compile down to java.util.List. If the underlying instance is an ArrayList, an unchecked cast to MutableList will technically succeed at runtime. However, doing so violates the API contract. If the implementation returns emptyList() or Collections.unmodifiableList(), that cast will crash with UnsupportedOperationException upon mutation. In production, we never cast read-only lists and enforce lint rules against it."
            },
            {
                "interviewer": "What happens if a data class has a val property that holds a mutable list when you call copy()?",
                "answer": "copy() only creates a shallow copy of the data class. The new instance receives a copy of the reference pointing to the exact same mutable list in memory. If either instance modifies that list, both instances reflect the change. To keep data classes truly immutable, all nested properties must also be immutable types."
            }
        ]
    },
    {
        "id": "KOT-03",
        "arabic_explanation": (
            "نظام الـ Null Safety في Kotlin هو واحد من أقوى أسلحة اللغة ضد الـ NullPointerException (NPE)، لأنه بينقل الفحص من وقت التشغيل (Runtime) لوقت البناء (Compile Time).\n\n"
            "الـ Type System ثنائي التفريع: نوع Non-Nullable زي String مستحيل يحمل null، ونوع Nullable زي String? بيعلن صراحة إن القيمة ممكن تكون غائبة. "
            "الأدوات الأساسية تشمل Safe Call (?.) اللي بينادي الدالة فقط لو مش null، و Elvis Operator (?:) اللي بيدي قيمة بديلة أو خروج مبكر، و Not-Null Assertion (!!) اللي بيجبر فك التغليف ويضرب Crash لو القيمة null.\n\n"
            "في الـ Bytecode، لما بتكتب دالة بتاخد Non-Nullable parameter، المترجم بيولد تلقائياً في أول سطر Intrinsics.checkNotNullParameter لضمان الـ Fail-Fast لو تم استدعاؤها من Java."
        ),
        "practical_walkthrough": (
            "في شاشة تفاصيل المستخدم، بنستلم UserDto من Retrofit:\n"
            "- النهج الخاطئ: استخدام !! لفك التغليف بناءً على افتراضات واهية: val address = userDto.profile!!.address!!.city (Crash فوري لو البروفايل ناقص).\n"
            "- النهج الصحيح: استخدام سلسلة Safe-calls مع Elvis Operator لإنشاء حالة عرض آمنة أو العودة المبكرة:\n"
            "  val city = userDto.profile?.address?.city ?: \"Unknown City\"\n"
            "- التحقق: اكتب Unit Test يمرر UserDto بحقول null في أماكن غير متوقعة، وتأكد إن الشاشة بتعرض Fallback UI نظيف بدون أي Crash."
        ),
        "quick_answer": "Kotlin distinguishes nullable types (T?) from non-nullable types (T) at compile time. Safe calls (?.) execute only if non-null, the Elvis operator (?:) provides default values or early exits, and the not-null assertion (!!) forces unwrapping, which risks a NullPointerException if null. In production, we avoid !! in favor of safe calls, Elvis guards, and smart casts.",
        "best_answer": (
            "Kotlin enforces null safety directly in the type system by separating types into non-nullable T and nullable T?. "
            "This forces us to handle potential absence before the code ever compiles.\n\n"
            "We work with nullable types using safe calls (?.) to navigate chains without risking a NullPointerException, "
            "and the Elvis operator (?:) to supply default values or return early. The not-null assertion (!!) forces an unwrap and throws an immediate NullPointerException if the value is null.\n\n"
            "In Android development, I strictly treat !! as a code smell because unexpected network payloads or asynchronous race conditions will crash the app. "
            "Instead, I combine safe calls with takeIf and Elvis operators to transform raw DTOs into valid domain models, ensuring that missing backend fields result in clean UI fallback states rather than production crashes."
        ),
        "deep_answer": (
            "Kotlin null safety is a static type system feature enforced during compilation. For non-nullable parameters, the compiler injects Intrinsics.checkNotNullParameter bytecode calls "
            "at method boundaries to ensure fail-fast behavior when invoked from Java. For local variables, the compiler performs data-flow analysis to enable smart casting: once a nullable variable is checked for null, "
            "it is automatically treated as non-nullable within that scope.\n\n"
            "However, smart casts have limitations. A mutable var or a custom getter on a property cannot be smart-cast because another thread or getter invocation could change the value between the check and its usage. "
            "In those cases, we capture the property into a local val or use scope functions like let.\n\n"
            "A critical risk area is platform types (T!) originating from unannotated Java SDKs. The Kotlin compiler cannot know whether an unannotated Java method returns null, so it disables static checks on those expressions. "
            "If an unannotated method returns null and you treat it as non-null, it crashes at runtime with an NPE generated by Kotlin's auto-generated null check bytecode. In production, we explicitly annotate Java boundaries with @Nullable and @NonNull, "
            "configure detekt to fail on !!, and handle ambiguous Java returns using safe-casts as? and nullable local adapters."
        ),
        "follow_ups": [
            {
                "interviewer": "Why can't you smart-cast a public var property after checking if (property != null)?",
                "answer": "Because the compiler cannot guarantee that another thread hasn't modified that property between the null check and the line where you use it. It also cannot guarantee that a custom getter doesn't return null on the second invocation. To solve this, I copy the property into a local val, or use safe-call with let: property?.let { ... }."
            },
            {
                "related_id": "KOT-23",
                "interviewer": "What happens when a Java method with no annotations returns null to Kotlin?",
                "answer": "Kotlin treats it as a platform type, denoted as Type!. The compiler relaxes null checks, allowing you to assign it to either Type or Type?. If you assign it to a non-nullable type and it happens to be null, Kotlin's bytecode intrinsics will throw an immediate NullPointerException. In production, I always assign unannotated Java returns to explicit nullable variables to stay safe."
            },
            {
                "interviewer": "Is there any valid scenario to use the !! operator in Android?",
                "answer": "The only defensible scenario is in test code where an assertion has already established that an object must exist, or an immediate crash with a stack trace is desired if a test fixture is broken. In production app code, there is virtually no scenario where !! cannot be replaced with an explicit error(...) check or clean Elvis fallback."
            }
        ]
    },
    {
        "id": "KOT-04",
        "arabic_explanation": (
            "الفرق بين == و === في Kotlin هو الفرق بين المحتوى (Structural Equality) و الهوية في الذاكرة (Referential Identity).\n\n"
            "المساواة الهيكلية (==) بتتحول مباشرة لاستدعاء دالة equals() مع فحص null آمن تحت الغطاء (a?.equals(b) ?: (b === null)). "
            "ده معناه إنه مستحيل يضرب NullPointerException لو الطرف الشمال null. في data class، الـ equals() بتتولد تلقائياً لتقارن كل القيم الموجودة في الـ Primary Constructor.\n\n"
            "المساواة المرجعية (===) بتقارن هل المتغيرين بيشاوروا على نفس الـ Address تماماً في الـ Heap، وده بيترجم لـ acmp instruction في الـ JVM bytecode.\n\n"
            "انتبه لفخ الـ Integer Caching: الأرقام من -128 لـ 127 بتتعمل لها Cache في الـ JVM، فلو قارنت 100 مع 100 بـ === هترجع true، لكن لو قارنت 1000 مع 1000 بـ === هترجع false لأن كل واحد اتعمل له Box في كائن مستقل في الـ Heap!"
        ),
        "practical_walkthrough": (
            "في DiffUtil في RecyclerView:\n"
            "- areItemsTheSame بتستخدم == لمقارنة الـ unique ID (oldItem.id == newItem.id) لتحديد هوية العنصر.\n"
            "- areContentsTheSame بتستخدم == لمقارنة محتويات الـ data class بالكامل (oldItem == newItem).\n"
            "- لو استخدمت === بالغلط في areContentsTheSame، كل ما الـ Repository يرجع New Immutable Instance لنفس البيانات، DiffUtil هيفتكر إن البيانات اتغيرت وهيعيد رسم العنصر بالكامل بدون داعي."
        ),
        "quick_answer": "In Kotlin, == checks structural equality by calling equals() with safe null checks under the hood, whereas === checks referential identity, determining whether two references point to the exact same object in heap memory. For data classes, == compares primary constructor properties, while === compares memory addresses.",
        "best_answer": (
            "In Kotlin, == represents structural equality, while === represents referential identity.\n\n"
            "When you write a == b, the compiler translates this into a safe call to equals(): it checks if either operand is null first, preventing NullPointerExceptions automatically. "
            "In data classes, equals() is generated for you to compare all primary constructor properties.\n\n"
            "On the other hand, === checks whether two references point to the exact same instance in heap memory, compiling down to an acmp bytecode instruction on the JVM.\n\n"
            "In Android, we rely on this distinction heavily in places like DiffUtil or Compose recomposition. For example, in DiffUtil, areItemsTheSame checks if unique IDs match, "
            "while areContentsTheSame uses == to check if property values changed. Using === for content comparison would trigger unnecessary UI redraws whenever new immutable instances are emitted from a repository."
        ),
        "deep_answer": (
            "Structural equality (==) and referential identity (===) differ in both intent and bytecode compilation. When compiling ==, Kotlin emits a call to Intrinsics.areEqual(a, b), "
            "which handles null checks before invoking equals(). For primitives, == maps directly to JVM primitive comparison instructions unless they are boxed into nullable types or generics.\n\n"
            "A subtle pitfall arises with boxed primitives due to JVM Integer caching. Integers between -128 and 127 are cached by the JVM runtime. Comparing two boxed Int? values like 100 with === returns true because they share the cached instance. "
            "But comparing two boxed Int? values of 1000 with === evaluates to false because they are distinct heap allocations. This is why you must never rely on === for value types.\n\n"
            "Another nuance is floating-point equality. IEEE 754 states that Float.NaN == Float.NaN is false. However, Kotlin adheres to total order equality when floats are statically typed as Any, boxed in collections, or compared in equals(): "
            "in that context, NaN equals NaN, and -0.0 is considered less than 0.0. In production, we override equals() and hashCode() carefully in custom classes, ensure consistency with data classes, and avoid === outside of performance caches or identity maps."
        ),
        "follow_ups": [
            {
                "interviewer": "How does Kotlin's == prevent a NullPointerException if the left-hand variable is null?",
                "answer": "The compiler translates a == b into a?.equals(b) ?: (b === null). If a is null, it checks whether b is also null. If both are null, it evaluates to true; if only one is null, it evaluates to false. Neither path can trigger a NullPointerException."
            },
            {
                "related_id": "KOT-05",
                "interviewer": "If two data class instances have different values in properties declared in the class body, does == evaluate to true?",
                "answer": "Yes! Kotlin only generates equals(), hashCode(), and toString() using properties declared in the primary constructor. Properties declared in the class body are completely ignored by generated equality. If two instances have identical constructor fields but different body fields, == will still return true."
            },
            {
                "interviewer": "Why is Float.NaN == Float.NaN false, but in a Set<Float> it's treated as equal?",
                "answer": "When evaluated directly as primitive floats, Kotlin follows IEEE 754 specifications where NaN is not equal to anything, including itself. But when floats are boxed into a collection like a Set or compared through equals(), Kotlin applies total ordering so that hash tables and sets work deterministically. Under total ordering, NaN equals NaN."
            }
        ]
    },
    {
        "id": "KOT-05",
        "arabic_explanation": (
            "في Kotlin، عندنا 4 تصنيفات رئيسية للكلاسات، كل واحد فيهم معمول علشان يحل مشكلة معمارية محددة:\n\n"
            "1. الـ data class: معمول خصيصاً لتمثيل حوامل البيانات (Data Holders). المترجم بيولد له تلقائياً equals و hashCode و toString و copy و componentN بناءً على حقول الـ Primary Constructor.\n"
            "2. الـ Regular Class: كلاس عادي للخدمات والمنطق (Services, ViewModels, Repositories). افتراضياً مقفول ضد الوراثة (final)، ومبيولدش دوال مقارنة تلقائية.\n"
            "3. الـ object: يعرف Singleton حقيقي على مستوى الـ Process، بيتم إنشاؤه بطريقة Thread-safe بواسطة الـ ClassLoader في الـ static initializer (<clinit>).\n"
            "4. الـ companion object: كائن مرتبط بالكلاس نفسه وهو البديل للـ static members في Java، ومناسب جداً للـ Factory Methods وحفظ الـ Constants."
        ),
        "practical_walkthrough": (
            "في تطبيق أندرويد بنكي:\n"
            "- بنستخدم data class لتمثيل حالة الشاشة TransferUiState(val amount: Double, val recipient: String).\n"
            "- بنستخدم companion object داخل الـ State لتعريف الحالة الابتدائية: companion object { val Initial = TransferUiState(0.0, \"\") }.\n"
            "- بنستخدم object لتعريف Singleton عديم الحالة زي PaymentFormatter.\n"
            "- احذر من تخزين Activity Context أو مراجع دورية داخل object؛ ده هيعمل Memory Leak طول عمر التطبيق لأن الـ Singleton مبيتحذفش أبداً من الـ Garbage Collector."
        ),
        "quick_answer": "A data class automatically generates equals, hashCode, toString, copy, and component functions for data modeling. A regular class is an unspecialized class used for logic and behavior. An object defines a thread-safe singleton managed by the JVM classloader. A companion object belongs to the class itself, serving as a factory or static-like member container.",
        "best_answer": (
            "In Kotlin, each of these constructs serves a distinct architectural purpose:\n\n"
            "A data class is designed for pure data holders. The compiler generates equals, hashCode, toString, componentN, and copy functions based on its primary constructor properties, "
            "making it the ideal choice for UI states, network DTOs, and domain entities.\n\n"
            "A regular class holds business logic, state machines, or services like ViewModels and Repositories, where identity and lifecycle matter more than structural value comparison.\n\n"
            "An object declares a lazy, thread-safe singleton initialized upon first classloader access. It is great for stateless utilities or navigation routes.\n\n"
            "Finally, a companion object acts like static members in Java but remains a first-class object that can implement interfaces. I primarily use companion objects for factory methods like fromDto or storing class-scoped constants."
        ),
        "deep_answer": (
            "Under the hood on the JVM, these four constructs compile into very different bytecode patterns.\n\n"
            "A data class generates bytecode for equals() that compares every primary constructor property, an appropriate hashCode() using primes, and a copy() method with default arguments that uses synthetic flags to selectively replace fields. "
            "It is strictly final and cannot be open or abstract. A critical caveat is that properties declared inside the class body are completely ignored by generated equality and copy methods.\n\n"
            "An object compiles into a final class with a private constructor and a public static final INSTANCE field initialized in the static initializer (<clinit>). The JVM specification guarantees that class loading is synchronized, "
            "making object instantiation inherently thread-safe without explicit locking. However, using objects to store mutable state creates global state, complicates unit testing, and risks memory leaks if Android Context is stored.\n\n"
            "A companion object compiles into an inner class named Companion, with a static instance held by the enclosing class. When called from Kotlin, it provides concise syntax, but from Java, callers must use EnclosingClass.Companion.method() "
            "unless annotated with @JvmStatic. In production architecture, I use data classes for immutable UI states and DTOs, companion objects for test factories or serializers, and avoid stateful objects in favor of dependency injection with Hilt."
        ),
        "follow_ups": [
            {
                "interviewer": "Why can't a data class be marked as open or abstract?",
                "answer": "Because the compiler generates equals(), hashCode(), and copy() based strictly on primary constructor properties. If a data class were subclassed with additional properties, the symmetric contract of equals() (a.equals(b) == b.equals(a)) would break, leading to subtle bugs in collections. To model polymorphic hierarchies, we use sealed classes or sealed interfaces with data class leaves."
            },
            {
                "interviewer": "How is a Kotlin object guaranteed to be thread-safe without using synchronized blocks?",
                "answer": "In JVM bytecode, the singleton instance is assigned in the static class initializer block (<clinit>). The JVM specification strictly guarantees that class loading and static initialization are atomic and thread-safe. No thread can see the instance in a partially constructed state."
            },
            {
                "interviewer": "When should you annotate a companion object method with @JvmStatic?",
                "answer": "You use @JvmStatic when the method must be called from Java code as a real static method, such as ClassName.method() rather than ClassName.Companion.method(). It is also required when creating methods for certain frameworks or JUnit 5 @MethodSource factories that reflectively look for static methods."
            }
        ]
    }
]


def main() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(KOT_DATA, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Generated {len(KOT_DATA)} questions in {DATA_FILE}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generator for KOT-23 through KOT-30 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "kot.json"

KOT_23_30 = [
    {
        "id": "KOT-23",
        "arabic_explanation": (
            "الـ Java/Kotlin Interoperability هي من أقوى مميزات Kotlin، لكن فيها تفاصيل تقنية دقيقة لازم كل Senior Engineer يفهمها:\n\n"
            "1. أنواع المنصة (Platform Types `T!`):\n"
            "   - لما كود Kotlin ينادي دالة Java بترجع نوع غير محدد بـ Nullability Annotations (زي `@Nullable` أو `@NonNull`)، المترجم بيعتبر النوع **Platform Type** (`String!`).\n"
            "   - المترجم بيسمحلك تعامله كـ Nullable (`String?`) أو Non-Nullable (`String`). لو عاملته كـ Non-Nullable والـ Java رجعت `null`، التطبيق هيعمل Crash بـ `NullPointerException` فوراً مع رسالة فشل في الـ Assertion.\n\n"
            "2. الـ SAM Conversions (Single Abstract Method):\n"
            "   - في Java، أي Interface فيها Method واحدة فقط (زي `Runnable` أو `OnClickListener`)، Kotlin بتسمحلك تمرر Lambda بدلاً من كتابة كائن مجهول (Anonymous Class) بشكل فوري.\n"
            "   - في Kotlin 1.4+، أصبح بإمكانك كتابة `fun interface` في كوتلن نفسها للحصول على نفس الميزة.\n\n"
            "3. الـ Calling Annotations عند استدعاء Kotlin من Java:\n"
            "   - `@JvmStatic`: لتوليد Static Method حقيقية في كلاس Java.\n"
            "   - `@JvmOverloads`: لتوليد Overloaded Methods بالمعاملات الافتراضية (Default Arguments) لـ Java.\n"
            "   - `@JvmField`: لمنع توليد الـ Getters/Setters والوصول للمتغير مباشرة كـ Public Field."
        ),
        "practical_walkthrough": (
            "في دمج مكتبة Java قديمة للدفع (Legacy Payment SDK):\n"
            "- دالة من Java: `public UserProfile getUser() { ... }` (بدون annotations).\n"
            "- **النهج الكارثي:**\n"
            "  `val user = paymentSdk.getUser()` // نوعها `UserProfile!`\n"
            "  `val name = user.name` // لو SDK رجع null، هيعمل Crash بـ NPE غير متوقع في الإنتاج!\n"
            "- **النهج الاحترافي (Ingress Defensive Boundary):**\n"
            "  `val user: UserProfile? = paymentSdk.getUser()` // نجبر Kotlin على معاملتها كـ Nullable صراحة\n"
            "  `if (user == null) handleLegacyError()`\n"
            "- **كتابة كود Kotlin ليستدعى من Java بنظافة:**\n"
            "  class UserRepository @JvmOverloads constructor(\n"
            "      val api: Api,\n"
            "      val timeoutMs: Long = 5000L // @JvmOverloads يولد constructor بـ 1 parameter وآخر بـ 2 لـ Java\n"
            "  )"
        ),
        "quick_answer": "Kotlin provides 100% two-way Java interoperability. Types coming from unannotated Java are treated as Platform Types (T!), relaxing null checks and risking NPEs unless defensively typed. SAM conversions allow passing lambdas to single-method Java interfaces, and @Jvm annotations (@JvmStatic, @JvmOverloads, @JvmField) tailor Kotlin declarations for clean Java consumption.",
        "best_answer": (
            "Kotlin and Java interoperate seamlessly on the JVM, but handling their architectural differences requires deliberate design.\n\n"
            "The biggest risk is Platform Types (denoted as T!). When calling Java methods that lack nullability annotations like @NonNull or @Nullable, Kotlin cannot know if the return value can be null. It gives you the freedom to treat it as nullable or non-nullable. If you treat it as non-null and Java returns null, Kotlin generates an implicit null check that throws a NullPointerException immediately. In production, we treat all platform types as nullable at the ingress boundary.\n\n"
            "For functional APIs, Kotlin provides automatic SAM (Single Abstract Method) conversions, allowing concise lambdas for Java interfaces like Runnable or OnClickListener. On the Kotlin side, defining `fun interface` brings this same ergonomic benefit.\n\n"
            "Finally, when exposing Kotlin libraries to Java callers, we use @JvmStatic to produce true static bytecode methods, @JvmOverloads to generate multiple method signatures for default arguments, and @JvmField to expose fields without getter overhead."
        ),
        "deep_answer": (
            "Under the hood, Kotlin enforces strict bytecode contracts when interacting with Java. For every non-null parameter in a public Kotlin function, the compiler inserts `Intrinsics.checkNotNullParameter()` at the very beginning of the bytecode method. If Java code passes null, it throws an IllegalArgumentException before any method logic runs, defending Kotlin's null-safety guarantees.\n\n"
            "With platform types, the compiler inserts `Intrinsics.checkNotNullExpressionValue()` at the call site in Kotlin. If Java returns null, the exception is thrown immediately upon assignment rather than later when dereferenced, aiding debugging. However, to maintain architectural safety in multi-module codebases where legacy Java modules feed domain layers, we enforce an ingress adapter pattern: wrap Java SDK models in pure Kotlin data classes at the repository boundary, verifying nullability once.\n\n"
            "Another critical interop consideration is exception handling. Kotlin does not have checked exceptions. If a Kotlin function throws an IOException, Java callers are not forced to catch it unless the Kotlin function is annotated with `@Throws(IOException::class)`. Without `@Throws`, Java code attempting to catch IOException will not even compile if the Java compiler thinks no checked exception can be thrown."
        ),
        "follow_ups": [
            {
                "interviewer": "Why does Java code fail to compile when trying to catch an exception from a Kotlin function without `@Throws`?",
                "answer": "Because the Java compiler enforces checked exceptions. If Java tries to catch a checked exception (like IOException) from a method whose signature does not declare `throws IOException`, javac flags an 'unreachable catch block' compile error. Adding `@Throws(IOException::class)` in Kotlin generates the Java `throws` clause in bytecode."
            },
            {
                "interviewer": "Can you use Kotlin default parameters when calling Kotlin from Java?",
                "answer": "Only if the function or constructor is annotated with `@JvmOverloads`. Without it, Kotlin generates only a single full-parameter method and a synthetic method with bitmask flags that is unwieldy and practically unusable from plain Java."
            },
            {
                "interviewer": "What happens if a Java class implements a Kotlin interface with property getters and setters?",
                "answer": "In Java bytecode, Kotlin properties become standard getters and setters (e.g., `getName()` and `setName()`). The Java class must implement those explicit accessor methods."
            }
        ]
    },
    {
        "id": "KOT-24",
        "arabic_explanation": (
            "الـ JNI (Java Native Interface) والـ Android NDK (Native Development Kit) هما الجسر اللي بيربط كود Kotlin/Java في الـ JVM بكود C و C++ الأصلي المترجم لـ Machine Code للـ CPU:\n\n"
            "1. ليه تطبيق Android ممكن يحتاج C++ و NDK؟\n"
            "   - **معالجة الوسائط والألعاب عالية الأداء:** معالجة الفيديو في الوقت الفعلي (OpenCV)، محركات الألعاب (Unreal, Unity, Vulkan)، ومعالجة الصوت فائقة السرعة زمنياً (AAudio, Oboe).\n"
            "   - **إعادة استخدام مكتبات C/C++ العريقة:** زي SQLite core، تشفير OpenSSL، أو موديلات الذكاء الاصطناعي (TensorFlow Lite C++ API, llama.cpp).\n"
            "   - **حسابات رياضية مكثفة:** تستفيد من تعليمات الـ CPU المباشرة زي ARM NEON SIMD instructions.\n\n"
            "2. تكاليف وعيوب الـ JNI Bridge (The JNI Overhead):\n"
            "   - عبور جسر الـ JNI (JNI Call Overhead) مكلف! كل نداء بين Kotlin و C++ بيحتاج Context Switch وتجهيز الـ Call Frame وعمل Pinning للذاكرة أو نسخ للـ Buffers.\n"
            "   - استدعاء دالة C++ صغيرة ملايين المرات داخل Loop ممكن يكون **أبطأ** من كتابتها في Kotlin بسبب تكلفة العبور!\n"
            "   - صعوبة الصيانة وتعدد الـ ABIs: مضطر تبني الـ Shared Library (`.so`) لعدة معماريات (`arm64-v8a`, `armeabi-v7a`, `x86_64`) مما يزيد حجم الـ APK."
        ),
        "practical_walkthrough": (
            "في تطبيق معالجة صور الكاميرا (Image Filter Application):\n"
            "- الكاميرا بتخرج 60 إطار في الثانية (60 FPS) بدقة 4K بصيغة YUV_420_888.\n"
            "- **النهج الخاطئ عبر JNI:**\n"
            "  المرور على كل بكسل واستدعاء دالة native لكل بكسل:\n"
            "  `for (pixel in pixels) nativeFilterPixel(pixel)` // كارثة أداء! تكلفة الـ JNI overhead هتوقف الـ App فوراً.\n"
            "- **النهج الصحيح:**\n"
            "  تمرير Direct ByteBuffer للـ Frame كامل مرة واحدة:\n"
            "  `val directBuffer = ByteBuffer.allocateDirect(frameSize)`\n"
            "  `nativeProcessFrame(directBuffer, width, height)`\n"
            "  في C++، بنقرا الـ Pointer مباشرة بدون نسخ للبيانات وبنستخدم ARM NEON instructions لمعالجة 16 بكسل في دورة CPU واحدة.\n"
            "- النتيجة: معالجة سلسة عند 60 FPS بدون استهلاك زائد للـ Garbage Collector."
        ),
        "quick_answer": "JNI connects Kotlin/JVM code with native C/C++ libraries compiled with the Android NDK. It is used for CPU-intensive tasks like low-latency audio, computer vision, game engines, and reusing existing C++ libraries. However, crossing the JNI boundary has call overhead, increases APK size across ABIs, and introduces native memory leak risks.",
        "best_answer": (
            "JNI, or Java Native Interface, is the bridging mechanism that allows Android's managed runtime (ART) to call into compiled native C/C++ code, and vice versa. Using the Android NDK, teams compile native shared libraries (.so files) for target CPU architectures.\n\n"
            "We use C++ in Android primarily for four scenarios: 1) low-latency, real-time audio using libraries like Oboe; 2) heavy image and video signal processing with OpenCV or custom shaders; 3) running machine learning inference runtimes like ONNX or TensorFlow Lite; and 4) cross-platform shared domain cores written in C++.\n\n"
            "However, JNI is not a silver bullet. Crossing the JNI boundary incurs noticeable CPU overhead due to argument marshaling, memory boundary synchronization, and ART JNI transition frames. If you make high-frequency native calls in a loop, it will actually perform worse than pure Kotlin. To use JNI effectively, you batch data using Direct ByteBuffers, minimizing crossings."
        ),
        "deep_answer": (
            "At the systems level, ART manages native interactions through JNIEnv pointers. Calling a native method requires ART to transition thread states from Runnable to Native. During this time, the garbage collector cannot relocate objects referenced by native pointers unless they are properly registered as JNI Global, Local, or Weak references. "
            "Passing Java arrays across JNI often forces the runtime to either pin the array memory or allocate a duplicate native buffer via `GetPrimitiveArrayCritical`, risking severe memory fragmentation or thread stalls.\n\n"
            "To achieve peak performance with JNI: 1) Allocate off-heap native memory using `ByteBuffer.allocateDirect()`, which lets C++ access the memory pointer via `GetDirectBufferAddress()` with zero copies; 2) Leverage CPU-specific vectorization like ARM NEON instructions in C++; 3) Keep the API surface coarse-grained—send one heavy buffer per frame rather than hundreds of granular calls.\n\n"
            "Finally, native crashes (SIGSEGV, SIGBUS) do not trigger standard Java crash handlers; they terminate the process instantly unless hooked via a native crash reporting library like Google Breakpad or Firebase Crashlytics NDK."
        ),
        "follow_ups": [
            {
                "interviewer": "What causes a memory leak in JNI?",
                "answer": "Failing to release native heap memory allocated with `malloc`/`new`, or failing to delete JNI references. Creating `NewGlobalRef` or accumulating unreleased `LocalRef` handles inside a loop exhausts the JNI local reference table (which has a default limit of 512 entries on Android) and causes process crashes."
            },
            {
                "interviewer": "How does JNI affect APK size?",
                "answer": "Every compiled C++ library must be packaged into the APK for each supported CPU ABI (arm64-v8a, armeabi-v7a, x86_64). Unless using Android App Bundles (AAB) to split APKs by ABI at install time, bundling multiple native libraries drastically inflates total download size."
            },
            {
                "interviewer": "Can C++ call back into Kotlin functions through JNI?",
                "answer": "Yes. C++ code can use the `JNIEnv` pointer to look up Kotlin/Java class signatures (`FindClass`), find method IDs (`GetMethodID`), and invoke methods (`CallVoidMethod`). However, caching class and method IDs in native code is essential, as dynamic lookups at runtime are extremely slow."
            }
        ]
    },
    {
        "id": "KOT-25",
        "arabic_explanation": (
            "السؤال عن `val list = mutableListOf<String>()` بيختبر فهمك للفرق الجوهري بين **Immutability of Reference** و **Thread Safety of Data**:\n\n"
            "1. معنى `val` في Kotlin:\n"
            "   - `val` تعني فقط إن الـ **Reference** (المؤشر) نفسه ثابت لا يمكن إعادة إسناده لكائن آخر في الـ Heap.\n"
            "   - `val` **لا تعني أبداً** إن الكائن نفسه Immutable!\n\n"
            "2. هل `mutableListOf()` Thread-Safe؟\n"
            "   - **إطلاقاً! لا توجد أي Thread-Safety!**\n"
            "   - `mutableListOf()` في الـ JVM بترجع `java.util.ArrayList`. الـ ArrayList غير محمية بأي مزامنة (Non-synchronized).\n"
            "   - لو Thread بيكتب عنصر (`add()`) في نفس الوقت اللي Thread تاني بيقرأ أو بيلف على الـ List (`for` loop):\n"
            "     * هيحصل `ConcurrentModificationException` فوراً.\n"
            "     * أو يحصل Data Corruption وفقدان بيانات في الـ internal array بدون استثناء ظاهر (Silent Bug).\n\n"
            "3. الحلول الإنتاجية الصحيحة (Production Solutions):\n"
            "   - **Concurrent Collections:** استخدام `CopyOnWriteArrayList` (لو القراءات كتيرة جداً والتعديلات نادرة).\n"
            "   - **مزامنة عبر Coroutines:** حصر تعديل وقراءة الـ List على Single Thread أو استخدام Coroutines Mutex (`Mutex.withLock`).\n"
            "   - **StateFlow مع Immutable Snapshots:** في الـ MVI، بنحتفظ بـ `List` غير قابلة للتعديل ونعمل Update بإنشاء New List باستخدام `_state.update { it.copy(...) }`."
        ),
        "practical_walkthrough": (
            "في شاشة الدردشة وتلقي الرسائل عبر WebSocket:\n"
            "- الرسائل بتوصل من WebSocket Thread، وشاشة العرض بتقرأ القائمة في الـ Main Thread.\n"
            "- **الكود الكارثي:**\n"
            "  val messages = mutableListOf<Message>()\n"
            "  // في WebSocket Thread:\n"
            "  messages.add(newMessage)\n"
            "  // في UI Thread:\n"
            "  for (msg in messages) render(msg) // CRASH: ConcurrentModificationException!\n"
            "- **الحل الإنتاجي باستخدام Mutex و Defensive Copying:**\n"
            "  private val mutex = Mutex()\n"
            "  private val _messages = mutableListOf<Message>()\n"
            "  suspend fun addMessage(msg: Message) = mutex.withLock {\n"
            "      _messages.add(msg)\n"
            "  }\n"
            "  suspend fun getSnapshot(): List<Message> = mutex.withLock {\n"
            "      _messages.toList() // Snapshot آمن تماماً للقراءة في الـ UI\n"
            "  }"
        ),
        "quick_answer": "No, it is completely thread-unsafe. The 'val' keyword only makes the variable reference immutable, not the underlying collection. Because mutableListOf returns an unsynchronized ArrayList, concurrent reads and writes across threads will cause ConcurrentModificationExceptions, index corruption, and silent data loss.",
        "best_answer": (
            "It is definitively not thread-safe. A common misconception is that declaring a collection with `val` confers immutability or concurrency protection. In reality, `val` simply prevents reassigning the variable reference to another object on the heap; the underlying object itself remains completely mutable.\n\n"
            "Under the hood, `mutableListOf()` instantiates a `java.util.ArrayList`. ArrayList has zero internal synchronization. If one thread is executing `add()` while another is iterating the list, the `modCount` counter mismatch will throw a `ConcurrentModificationException`. Even worse, if two background threads execute `add()` simultaneously, race conditions on the internal array index can overwrite elements, corrupt the list size, or cause an internal ArrayIndexOutOfBoundsException.\n\n"
            "To handle concurrent collections in production, I use one of three strategies: 1) synchronize access using a Coroutines `Mutex`; 2) use thread-safe data structures like `CopyOnWriteArrayList` for read-heavy scenarios; or 3) follow functional state management with `MutableStateFlow` and immutable lists, updating state atomically via `_state.update { current -> current + newItem }`."
        ),
        "deep_answer": (
            "At the memory architecture level, standard Java collections like ArrayList do not use memory barriers or volatile writes for internal array elements. This means writes from thread A may remain cached in CPU L1/L2 caches and never become visible to thread B in a timely fashion, violating the happens-before relationship defined by the Java Memory Model (JMM).\n\n"
            "In modern Android architecture, using traditional Java synchronization like `synchronized(lock)` or `Collections.synchronizedList()` is discouraged because it blocks operating system threads, which can cause ANR (Application Not Responding) if invoked on the main thread.\n\n"
            "Instead, we adopt structured concurrency paradigms: "
            "1. Confinement: confine state mutation to a single coroutine dispatcher, or use a dedicated Actor / single-threaded dispatcher (`Dispatchers.Default.limitedParallelism(1)`). "
            "2. Non-blocking synchronization: use Kotlin Coroutines `Mutex`, ensuring suspending calls rather than thread-blocking locks. "
            "3. Pure immutability: store only persistent immutable lists (`persistentListOf()`), replacing the reference atomically via compare-and-swap (CAS) loops inside `AtomicReference` or `StateFlow.update()`."
        ),
        "follow_ups": [
            {
                "interviewer": "Why is `CopyOnWriteArrayList` not suitable for frequent write operations?",
                "answer": "Because every single write operation (add, remove, set) creates a full copy of the entire underlying array. If you have 5,000 items and append 100 items per second, it allocates 100 arrays of 5,000 items every second, creating extreme heap churn and triggering severe GC pauses."
            },
            {
                "interviewer": "How does `StateFlow.update { }` ensure thread safety without locks?",
                "answer": "`StateFlow.update` uses an atomic Compare-And-Set (CAS) loop on an `AtomicReference`. It reads the current value, computes the new value in the transform lambda, and attempts an atomic CAS. If another thread updated the state in the meantime, the CAS fails and it retries the loop automatically."
            },
            {
                "interviewer": "What is the difference between Kotlin's Mutex and Java's synchronized block?",
                "answer": "A Java synchronized block blocks the underlying OS thread, keeping it idle and unavailable for other work. Kotlin's Mutex is suspension-aware: when a coroutine waits for a locked Mutex, it suspends its state machine, freeing the underlying thread to execute other coroutines."
            }
        ]
    },
    {
        "id": "KOT-26",
        "arabic_explanation": (
            "المقارنة بين `enum` و `sealed class` / `sealed interface` في نمذجة الحالات (UI & Payment States) هي محور أساسي في تصميم الأنظمة الحديثة:\n\n"
            "1. متى يكون الـ Enum كافياً (When Enum is enough)?\n"
            "   - الـ Enum مناسب فقط لما تكون الحالات **مجموعة ثابتة من الثوابت المجردة (Simple Fixed Constants)** بدون بيانات متغيرة خاصة بكل حالة.\n"
            "   - مثال: اتجاهات الشاشة (`LANDSCAPE`, `PORTRAIT`) أو أيام الأسبوع (`MONDAY`, `TUESDAY`).\n"
            "   - عيب الـ Enum: كل القيم لازم تشترك في نفس الـ Properties المحددة في الـ Constructor، ولا يمكن لحالة واحدة تحمل Payload مختلف عن باقي الحالات.\n\n"
            "2. متى تكون الـ Sealed Hierarchy متفوقة وضرورية (Why Sealed Hierarchies Win)?\n"
            "   - في الـ UI States والـ Payment States، كل حالة بتحتاج **بيانات مختلفة تماماً (State-Specific Payloads)**:\n"
            "     * حالة `Idle`: لا بيانات.\n"
            "     * حالة `Loading`: رسالة تحميل اختيارية ونسبة مئوية `progress: Float`.\n"
            "     * حالة `Success`: بيانات الإيصال `receipt: PaymentReceipt` ومعرف المعاملة.\n"
            "     * حالة `Failure`: نوع الخطأ `error: PaymentError` ورقم هاتف الدعم ورابط إعادة المحاولة.\n"
            "   - الـ `sealed interface` بتسمح بتعريف `data object` للحالات المجردة (لتوفير الذاكرة)، و `data class` للحالات اللي فيها بيانات.\n"
            "   - الـ Compiler في `when` بيضمن معالجة كل الحالات (Exhaustive Checking) ويقوم بعمل Smart Cast تلقائياً للبيانات الخاصة بكل حالة."
        ),
        "practical_walkthrough": (
            "في شاشة إتمام عملية الدفع (Checkout Payment Flow):\n"
            "- **النهج الفاشل باستخدام Enum و God Data Class:**\n"
            "  data class CheckoutState(\n"
            "      val status: PaymentStatus, // Enum: IDLE, PROCESSING, SUCCESS, ERROR\n"
            "      val receipt: Receipt? = null,\n"
            "      val errorMessage: String? = null,\n"
            "      val retryCount: Int = 0\n"
            "  )\n"
            "  هذا التصميم يخلق حالات غير شرعية (Illegal States): ممكن يكون الـ Status = SUCCESS لكن الـ receipt = null! المطور مضطر يكتب `receipt!!` أو `receipt?.let` في كل حتة.\n"
            "- **النهج الصحيح باستخدام Sealed Interface (Make Illegal States Unrepresentable):**\n"
            "  sealed interface PaymentUiState {\n"
            "      data object Idle : PaymentUiState\n"
            "      data class Processing(val step: String) : PaymentUiState\n"
            "      data class Success(val receipt: Receipt) : PaymentUiState\n"
            "      data class Failed(val reason: PaymentError, val canRetry: Boolean) : PaymentUiState\n"
            "  }\n"
            "  الآن مستحيل تقنياً تمثيل حالة نجاح بدون إيصال!"
        ),
        "quick_answer": "Enums are strictly for static constants that share identical attributes across all instances. Sealed hierarchies are superior for UI and payment states because they allow individual states to hold distinct payloads (e.g., Success holds a Receipt, while Failed holds an ErrorReason), eliminating invalid states and enabling compiler-enforced smart casting in when expressions.",
        "best_answer": (
            "I choose sealed hierarchies over enums whenever different states require different payloads. Enums represent fixed sets of uniform constants; every enum entry must share the exact same constructor properties, and every entry is a singleton instantiated when the class is loaded.\n\n"
            "In real-world UI and payment flows, states are inherently heterogeneous. An Idle state carries no data, a Loading state might carry a progress percentage, a Success state carries a PaymentReceipt object, and a Failed state carries an error domain model and a retry policy. Modeling this with an enum forces you into a bloated 'God state' with dozens of nullable properties, creating invalid states like being in Success status with a null receipt.\n\n"
            "With a sealed interface, illegal states become unrepresentable in the type system. In the UI or ViewModel, Kotlin's when expression guarantees exhaustive branch coverage and smart-casts each branch to its concrete type, giving safe, direct access to that state's payload without null assertions."
        ),
        "deep_answer": (
            "From an architectural domain-modeling perspective, sealed hierarchies embody Algebraic Data Types (specifically Sum Types with Product Type variants). "
            "Using `sealed interface` combined with `data object` (introduced in Kotlin 1.9) gives the best of both worlds: parameterless states like `Idle` compile to singletons with clean toString() logging, while parameterized states like `Success(val receipt: Receipt)` allocate new instances holding distinct payloads.\n\n"
            "In contrast, forcing an enum to represent dynamic states leads to architectural rot: developers often resort to mutable companion objects, global singletons, or nullable fields in a single giant class. If a new business requirement emerges—such as adding a `TwoFactorRequired(val challengeToken: String)` state to a payment flow—with a sealed interface, the Kotlin compiler will fail compilation at every single `when` expression across the entire project that doesn't handle the new variant, acting as an automated refactoring guide.\n\n"
            "In Jetpack Compose, sealed states are especially critical for recomposition stability. Distinct state classes allow Compose to skip recomposition when only unrelated properties in sibling states change, boosting rendering performance."
        ),
        "follow_ups": [
            {
                "interviewer": "Can a sealed class have subclasses outside the module?",
                "answer": "No. All direct subclasses of a sealed class or interface must be defined in the same package and the same compilation module. This restriction is precisely what allows the Kotlin compiler to guarantee exhaustive when expressions without requiring an else branch."
            },
            {
                "interviewer": "Why prefer `sealed interface` over `sealed class` in modern Kotlin?",
                "answer": "`sealed interface` allows multiple inheritance (a state can implement multiple domain marker interfaces, like `NavigableState` and `CacheableState`), and it does not consume a class inheritance slot on the JVM. It also generates cleaner bytecode with less hierarchy overhead."
            },
            {
                "interviewer": "How do you serialize a sealed state hierarchy to JSON with kotlinx.serialization?",
                "answer": "By annotating the sealed interface with `@Serializable`. Kotlinx.serialization automatically attaches a polymorphic class discriminator (by default `type: \"Success\"`) to the JSON output and decodes incoming payloads into the exact concrete subclass at runtime without reflection."
            }
        ]
    },
    {
        "id": "KOT-27",
        "arabic_explanation": (
            "الـ `inline` keyword في Kotlin هي أداة لتحسين الأداء (Optimization)، لكن استخدامها الخاطئ بيؤدي لـ **Code Bloat** وتضخم كبير في حجم الـ Bytecode والـ APK:\n\n"
            "1. إمتى `inline` بيكون مكسب ممتاز (Performance Win)?\n"
            "   - لما تكون الدالة **Higher-Order Function** بتاخد Lambda parameter (زي `filter`, `map`, `repeat`).\n"
            "   - بدون inline، الـ JVM مضطر ينشئ كائن جديد (`Function0` أو `Function1`) في الـ Heap لكل استدعاء للـ Lambda، مما يسبب GC allocations.\n"
            "   - مع inline، المترجم بينسخ كود الـ Lambda وكود الدالة مباشرة في مكان الاستدعاء (Call Site)، فيختفي الـ Object Allocation والـ Function Call Overhead.\n\n"
            "2. إمتى `inline` يسبب Code Bloat وكوارث في الأداء؟\n"
            "   - **لما يكون جسم الدالة كبيراً (Large Function Body):** لو الدالة فيها 50 سطر كود ومستدعاة في 100 مكان، المترجم هينسخ الـ 50 سطر 100 مرة في الـ Bytecode! ده بيكبر حجم الـ DEX/APK ويملأ الـ CPU Instruction Cache.\n"
            "   - **دوال بدون Function Parameters:** استخدام inline على دالة عادية بتاخد Parameters عادية (مش Lambdas) لا فائدة منه، والـ JVM JIT Compiler أصلاً بيعمل Inlining للدوال الصغيرة تلقائياً وبذكاء أكبر.\n"
            "   - **Reified Type Parameters:** أحياناً بنضطر نستخدم inline علشان `reified` (زي `inline fun <reified T> parse()`)، لكن لو دالة الـ parse كبيرة جداً، الحل الصح هو فصلها: دالة inline صغيرة لـ `T::class.java` تفوض العمل لدالة خاصة عادية غير inlined."
        ),
        "practical_walkthrough": (
            "في شاشة معالجة الأحداث والـ Logging:\n"
            "- **النهج السيئ المسبب لـ Code Bloat:**\n"
            "  inline fun executeWithTracing(action: () -> Unit) {\n"
            "      // 40 سطر من تهيئة الـ Trace، قراءة الـ Thread info، حساب الوقت، والكتابة في ملف...\n"
            "      val start = System.currentTimeMillis()\n"
            "      action()\n"
            "      // 30 سطر إضافي لحساب الإحصائيات وإرسال تقرير...\n"
            "  }\n"
            "  لو تم استدعاء الدالة دي 200 مرة في التطبيق، 70 سطر كود تم تكرارهم 200 مرة = 14,000 سطر Bytecode متكرر في ملف الـ DEX!\n"
            "- **النهج الاحترافي (Inline Wrapper + Private Non-inlined Helper):**\n"
            "  inline fun executeWithTracing(action: () -> Unit) {\n"
            "      val traceId = startTraceInternal() // دالة عادية غير inlined\n"
            "      try {\n"
            "          action()\n"
            "      } finally {\n"
            "          stopTraceInternal(traceId) // دالة عادية غير inlined\n"
            "      }\n"
            "  }\n"
            "  هنا الـ Lambda تم عمل Inlining لها بدون أي Heap Object، وفي نفس الوقت الكود الثقيل ظل مركزاً في دالة واحدة بدون أي تضخم في الـ Bytecode."
        ),
        "quick_answer": "Inline causes code bloat when applied to functions with large bodies or functions that do not take lambda parameters. Because the compiler copies the entire function bytecode into every single call site, inlining large functions repeatedly balloons the generated DEX bytecode, degrades CPU instruction cache locality, and inflates APK size.",
        "best_answer": (
            "The inline modifier is primarily intended for higher-order functions that take lambda parameters. Without inline, every lambda invocation instantiates an anonymous Function object on the heap. Inlining eliminates this allocation by copying the function's body and the lambda directly into the call site.\n\n"
            "However, inline causes code bloat when developers inline large functions or functions without functional parameters. Because bytecode is duplicated at every single call site, inlining a 50-line function called in 100 places injects 5,000 lines of bytecode into your compiled DEX files. This inflates APK size and pollutes the CPU's instruction cache (I-cache), which can actually make execution slower due to cache misses.\n\n"
            "In production, I follow the rule: only inline higher-order functions with small, concise bodies. If a function requires inlining for a reified type parameter but contains substantial logic, I extract the heavy work into a non-inlined private helper, keeping the inline public shell as minimal as possible."
        ),
        "deep_answer": (
            "At the JVM and ART level, the runtime JIT compiler is already capable of inlining hot standard methods during execution using runtime profiling. Forcing Kotlin compiler-level inlining on non-higher-order methods bypasses runtime heuristics and permanently bloats compiled DEX binaries.\n\n"
            "When using `reified` type parameters—which mandate the `inline` keyword because the compiler needs concrete class metadata at the call site—developers frequently write monolithic functions like `inline fun <reified T> parseNetworkResponse(json: String): T`. If that function contains 80 lines of error-handling and logging logic, that entire block is stamped into every API call site across the project.\n\n"
            "To solve this, we use the 'trampoline' or 'delegate' pattern: the public inline function extracts `T::class.java` and immediately passes `Class<T>` to an internal, non-inlined function that does the heavy lifting. Furthermore, if an inline higher-order function takes multiple lambdas and one of them is large or executed infrequently, annotating it with `noinline` prevents unnecessary call-site expansion."
        ),
        "follow_ups": [
            {
                "interviewer": "What is the difference between `inline`, `noinline`, and `crossinline`?",
                "answer": "`inline` inlines both the function and its lambda parameters. `noinline` tells the compiler not to inline a specific lambda parameter, keeping it as an object (e.g., if you need to store it in a property). `crossinline` allows inlining the lambda but forbids non-local returns (`return`), which is necessary when the lambda is executed inside an execution context like a nested runnable or coroutine."
            },
            {
                "interviewer": "Does the Kotlin compiler warn you if you use inline improperly?",
                "answer": "Yes. If you add `inline` to a function that has no lambda parameters, the compiler issues a warning: 'Expected performance impact from inlining is insignificant. Inlining works best for functions with parameters of functional types.'"
            },
            {
                "interviewer": "Can inline functions access private members of their declaring class?",
                "answer": "By default, no. Because the bytecode is inlined into external call sites, the JVM access rules forbid access to private members. To allow access, private members must be annotated with `@PublishedApi`, which makes them effectively public in bytecode while hiding them from Kotlin autocompletion."
            }
        ]
    },
    {
        "id": "KOT-28",
        "arabic_explanation": (
            "تصميم Type-Safe Result API بدون فقدان تفاصيل الخطأ (Without losing error context) هو الفارق بين كود مبتدئ وكود معماري ناضج:\n\n"
            "1. المشاكل في الـ APIs التقليدية للنتائج:\n"
            "   - **`kotlin.Result<T>`:** بيحصر الخطأ في `Throwable` فقط؛ فبتفقد الـ Type-Safety لأخطاء الـ Domain، ومضطر تعمل Type Cast للـ Throwable.\n"
            "   - **الـ Nullable Returns (`User?`):** لو الدالة رجعت `null`، المتصل ميعرفش السبب: هل المستخدم غير موجود؟ ولا السيرفر واقع؟ ولا التوكن انتهى؟ تفقد كل سياق الخطأ تماماً.\n"
            "   - **الـ Generic Error Code (`Int` أو `String`):** استخدام أكواد رقمية زي `404` أو strings زي `\"USER_NOT_FOUND\"` يفتقر للـ Type Safety وعرضة للأخطاء الإملائية.\n\n"
            "2. أفضل نمط معماري (The Senior Pattern):\n"
            "   - استخدام `sealed interface Result<out T, out E>`:\n"
            "     * المتغير `T` يمثل البيانات الناجحة (Success Data).\n"
            "     * المتغير `E` يمثل الـ Domain Error ويكون هو نفسه Sealed Hierarchy.\n"
            "   - في حالة الفشل، الـ Error Model يحمل معلومات غنية ومحددة (Structured Metadata)، زي `HttpCode`, `UserMessage`, أو `RetryPolicy`.\n"
            "   - توفير Extension Functions عملية زي `map`, `flatMap`, `onSuccess`, `onError` لسهولة ربط العمليات بسلاسة (Monadic Chaining)."
        ),
        "practical_walkthrough": (
            "في طبقة المصادقة وتسجيل الدخول (Authentication Repository):\n"
            "- **تصميم الـ Result API:**\n"
            "  sealed interface AuthResult<out T> {\n"
            "      data class Success<T>(val data: T) : AuthResult<T>\n"
            "      sealed interface Error : AuthResult<Nothing> {\n"
            "          data class InvalidCredentials(val attemptsRemaining: Int) : Error\n"
            "          data class AccountLocked(val unlockTime: Instant) : Error\n"
            "          data class Network(val cause: IOException) : Error\n"
            "      }\n"
            "  }\n"
            "- **في الـ ViewModel:**\n"
            "  when (val result = authRepository.login(username, password)) {\n"
            "      is AuthResult.Success -> emitNavigation(HomeRoute)\n"
            "      is AuthResult.Error.InvalidCredentials -> showWarning(\"Remaining: ${result.attemptsRemaining}\")\n"
            "      is AuthResult.Error.AccountLocked -> showLockedScreen(result.unlockTime)\n"
            "      is AuthResult.Error.Network -> showRetrySnackbar()\n"
            "  }\n"
            "- النتيجة: الـ ViewModel يعرف بالضبط كل تفصيلة خطأ بدون أي Exception وبدون أي Casting."
        ),
        "quick_answer": "Design a typed sealed hierarchy like Result<out T, out E> where both success and failure are strongly typed. Failures carry structured metadata rather than generic strings or raw Throwables, eliminating casting and allowing the compiler to enforce exhaustive, context-rich error handling.",
        "best_answer": (
            "To design a type-safe result API without losing error context, I use a parametric sealed hierarchy: `sealed interface NetworkResult<out T, out E>`. "
            "The key design principle is treating failures as first-class domain entities rather than second-class exceptions or generic strings.\n\n"
            "In this design, `Success<T>` holds the strongly typed response payload. The failure branch is not tied to `java.lang.Throwable`; instead, it is typed to a sealed error hierarchy `E` specific to that feature—such as `AuthError.InvalidCredentials(val attemptsRemaining: Int)` or `AuthError.AccountLocked(val unlockTime: Instant)`. This preserves rich diagnostic context and metadata.\n\n"
            "Callers consume the API with exhaustive `when` expressions, giving the compiler the ability to verify that every domain error variant is explicitly handled. We also provide functional transformations like `map`, `mapError`, and `flatMap` so pipelines can chain results cleanly without nested try-catch blocks."
        ),
        "deep_answer": (
            "Architecturally, a well-engineered Result type follows Monadic patterns (similar to Arrow's Either<L, R>) while maintaining idiomatic Kotlin ergonomics. "
            "To maximize performance and ergonomics in Android: "
            "1. Covariance: use `out T` and `out E` with `Success<out T>` and `Failure<out E> : Result<Nothing, E>`, allowing seamless polymorphism and subtyping. "
            "2. Preserve low-level diagnostics: for network and infrastructure failures, attach the underlying root cause (`val cause: Throwable? = null`) so logging and Crashlytics can report full diagnostic breadcrumbs without exposing Throwables to the domain logic. "
            "3. Inline utility methods: implement combinators like `inline fun <T, E, R> Result<T, E>.map(transform: (T) -> R): Result<R, E>` as inline functions to ensure zero heap allocation overhead during transformation chains.\n\n"
            "This pattern completely decouples business error recovery from system crash reporting, providing absolute compile-time safety across multi-module boundaries."
        ),
        "follow_ups": [
            {
                "interviewer": "Why not just use Kotlin's built-in `Result<T>`?",
                "answer": "Because `kotlin.Result<T>` fixes the error type to `Throwable`. In domain logic, business errors are not exceptions. Tying errors to Throwable loses domain type specificity, requires runtime type-casting (`e as CustomException`), and causes performance overhead due to stack-trace capture."
            },
            {
                "interviewer": "How do you handle Coroutine cancellation with custom Result types?",
                "answer": "When wrapping repository calls, if a `CancellationException` is caught, you must immediately re-throw it instead of wrapping it into your custom Result.failure. Wrapping CancellationException breaks structured concurrency and prevents the coroutine tree from terminating properly."
            },
            {
                "interviewer": "How does this pattern benefit unit testing?",
                "answer": "It simplifies unit tests immensely. Instead of testing for thrown exceptions with `assertFailsWith` and inspecting exception messages, you assert directly on strongly typed sealed objects (e.g., `assertThat(result).isEqualTo(AuthResult.Error.AccountLocked(expectedTime))`)."
            }
        ]
    },
    {
        "id": "KOT-29",
        "arabic_explanation": (
            "الاعتقاد بأن حفظ الـ API Keys أو الـ Secrets داخل كود C++ Native يمنع الـ Reverse Engineering هو **وهم أمني خطير (Security Fallacy)**:\n\n"
            "1. هل كود C++ يمنع الـ Reverse Engineering؟\n"
            "   - **إطلاقاً! لا يمنعه إطلاقاً.**\n"
            "   - بمجرد بناء المكتبة (`.so` file) داخل الـ APK، أي شخص يقدر يشغل أمر بسيط جداً في الـ Terminal زي:\n"
            "     `strings libnative-lib.so | grep -i api_key`\n"
            "     والـ String هيظهر أمامه بنص واضح ومباشر في ثانية واحدة!\n\n"
            "2. لو عملت Obfuscation أو Xor Encryption للـ Strings في C++؟\n"
            "   - المهاجم يقدر يفتح الملف بأدوات الهندسة العكسية زي **Ghidra** أو **IDA Pro** ويشوف كود فك التشفير بسهولة، أو يستخدم **Frida** لعمل Hook لدالة الـ JNI واعتراض القيمة المفكوكة أثناء خروجها للـ Java Layer!\n\n"
            "3. القاعدة الذهبية لأمان تطبيقات الموبايل:\n"
            "   - **Client-Side Secrets Are Never Truly Secret.** أي شيء موجود على جهاز العميل يمكن استخراجه.\n"
            "   - الحل الصحيح هو: عدم تخزين الـ Secrets الحساسة (زي Stripe Secret Key أو Private Keys) في التطبيق نهائياً. يتم تخزينها في الـ Backend Server، والتطبيق يحصل على Short-lived Tokens عبر OAuth2 / App Check."
        ),
        "practical_walkthrough": (
            "في تطبيق بنكي أو تطبيق دفع:\n"
            "- الفريق الهندسي قرر يحط الـ `PAYMENT_GATEWAY_SECRET_KEY` في ملف C++ اسمه `secrets.cpp` ظناً منهم إنه محمي.\n"
            "- **إزاي بيتم اختراقه في 3 خطوات:**\n"
            "  1. فتح الـ APK وفك ضغط `lib/arm64-v8a/libsecrets.so`.\n"
            "  2. تشغيل سكريبت Frida صغير يعمل Hook لدالة `Java_com_bank_NativeBridge_getSecretKey()`.\n"
            "  3. تشغيل التطبيق؛ الدالة تستدعى، وفريدا يطبع المفتاح في الكونسول بدون حتى فك تشفير C++!\n"
            "- **الحل المعماري الحقيقي:**\n"
            "  - المفتاح السري مكانه فقط في الـ Backend Server.\n"
            "  - التطبيق يطلب من الـ Server إنشاء جلسة دفع (`createPaymentSession`).\n"
            "  - الـ Server يستخدم الـ Secret Key ويكلم بوابة الدفع ويرجع للتطبيق Session Token مؤقت ينتهي بعد 15 دقيقة ومخصص فقط للعملية الحالية.\n"
            "  - تفعيل Firebase App Check و SafetyNet/Play Integrity لضمان أن الطلبات قادمة من تطبيقك الشرعي."
        ),
        "quick_answer": "No. Storing secrets in C++ native code does not prevent reverse engineering; it only provides minor security through obscurity. Plain strings in .so libraries are trivially extractable via the 'strings' CLI command, and even encrypted strings can be decompiled with Ghidra or intercepted at runtime via Frida JNI hooks.",
        "best_answer": (
            "Storing sensitive values in native C++ libraries does not prevent reverse engineering. At best, it offers a minor layer of obfuscation that slows down amateur attackers, but it cannot stop a determined engineer.\n\n"
            "If hardcoded as raw strings, any attacker running the standard command-line utility `strings` on the unzipped `.so` file will see the plain text secret immediately. Even if you obfuscate or XOR-encrypt the string in C++, disassembly tools like Ghidra and IDA Pro easily decompile the native routines. More practically, an attacker doesn't even need to decompile the C++: using dynamic instrumentation tools like Frida, they can hook the JNI function boundary and intercept the decrypted string the moment it is returned to the JVM layer.\n\n"
            "The golden rule of mobile security is that the client cannot be trusted with true secrets. High-privilege API keys, database credentials, and signing secrets must reside strictly on your backend server. The mobile app should authenticate via ephemeral OAuth tokens, protected by Play Integrity and Firebase App Check."
        ),
        "deep_answer": (
            "From a threat modeling and penetration testing perspective, native binaries are merely compiled machine instructions. A reverse engineer uses a combination of static analysis (Ghidra, Hopper, IDA Pro) and dynamic binary analysis (Frida, GDB, lldb, eBPF) to inspect program memory.\n\n"
            "When security teams insist on storing client-identifying keys locally—such as non-sensitive third-party client tokens (e.g., Google Maps API key, Algolia search-only key)—native code with string splitting, runtime XOR masking, and JNI integrity checks can raise the barrier to entry against script kiddies. "
            "However, protecting sensitive assets requires defense-in-depth: "
            "1. Architecture: use a Backend-For-Frontend (BFF) proxy pattern where the mobile app never communicates directly with third-party paid APIs using sensitive tokens. "
            "2. Attestation: integrate the Google Play Integrity API to cryptographically verify device and app binary authenticity before granting access to backend endpoints. "
            "3. R8 / DexGuard: apply code obfuscation and root/hook detection (detecting Frida, Magisk, and debugger attachments), acknowledging that client-side protections can always eventually be bypassed by an adversary with root hardware access."
        ),
        "follow_ups": [
            {
                "interviewer": "If true secrets should not be in the app, how do you handle public client IDs like Google Maps keys?",
                "answer": "Public client IDs are designed to be embedded in apps. You protect them by restricting them at the API provider dashboard: restrict the Google Maps key to your exact Android package name and release SHA-1 signing certificate fingerprint so it cannot be abused from other apps or domains."
            },
            {
                "interviewer": "How does Frida hook JNI functions?",
                "answer": "Frida injects a Google V8 JavaScript engine into the target process's memory space. It hooks function pointers in the native library's export table or hooks the JVM's `art::ArtMethod` structure, intercepting inputs and return values in real time without modifying the APK on disk."
            },
            {
                "interviewer": "What role does the Android Keystore play in storing secrets?",
                "answer": "The Android Keystore is for storing cryptographic keys securely on-device, protected by hardware security modules (TEE or StrongBox). However, it is used for securing per-user keys generated on that specific device (like biometric tokens or private session keys), not for distributing pre-shared company secrets embedded across all APK downloads."
            }
        ]
    },
    {
        "id": "KOT-30",
        "arabic_explanation": (
            "مراجعة كود Kotlin للتحقق من الـ Readability و الـ Null Safety و الـ Allocation Cost هي المهارة التي تميز الـ Senior / Staff Engineer في الـ Code Review:\n\n"
            "1. مراجعة الـ Null Safety (Null Safety Review):\n"
            "   - **التخلص من `!!` (Force-unwrap):** أي استخدام لـ `!!` هو Code Smell ويجب حظره؛ بدلاً منه نستخدم `?:` (Elvis operator) أو smart casts أو explicit error handling.\n"
            "   - **Platform Types Ingress:** فحص أي استدعاء لمكتبات Java والتأكد من تحديد النوع صراحة كـ Nullable (`Type?`) عند الدخول.\n"
            "   - **تجنب الـ `lateinit` العشوائي:** `lateinit` يجب أن يقتصر على حقن الاعتماديات (DI) أو دورات حياة محددة مع اختبار `::prop.isInitialized` عند الحاجة.\n\n"
            "2. مراجعة تكلفة الذاكرة والـ Allocations (Memory & Allocations):\n"
            "   - **الـ Lambdas في الـ Loops والـ High-Frequency Paths:** التأكد من عدم إنشاء Lambdas بتعمل capture لمتغيرات محلية داخل loops أو Composables بدون inline.\n"
            "   - **Collections vs Sequences:** مراجعة الـ Pipelines المتتالية (`filter.map.take`) واستخدام `asSequence()` للبيانات الكبيرة لمنع intermediate collections.\n"
            "   - **Primitive Obsession & Boxing:** فحص استخدام `@JvmInline value class` لتجنب إنشاء كائنات للـ IDs، والتأكد من عدم عمل Boxing غير مقصود في Generic collections.\n\n"
            "3. مراجعة الـ Readability والتصميم اللغوي (Idiomatic Kotlin):\n"
            "   - **عدم المبالغة في الـ Scope Functions:** منع سلاسل `?.let { }?.also { }?.apply { }` المتشابكة.\n"
            "   - **الـ Immutability بالتصميم:** تفضيل `val` على `var`، وتفضيل `List` على `MutableList` في الـ Public APIs."
        ),
        "practical_walkthrough": (
            "قائمة تدقيق عملية (Checklist) بنطبقها في الـ Pull Requests:\n"
            "```kotlin\n"
            "// ❌ كود سيء في الـ PR:\n"
            "fun processUsers(users: List<User>) {\n"
            "    val valid = users.filter { it.age > 18 }.map { it.id!! } // خطر !! وتكلفة مصفوفتين وسيطتين\n"
            "    for (id in valid) {\n"
            "        analytics.track { log(id) } // إنشاء Lambda object في كل لفة لو track غير inlined\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ الكود بعد مراجعة الـ Senior:\n"
            "fun processUsers(users: List<User>) {\n"
            "    users.asSequence()\n"
            "        .filter { it.age > 18 }\n"
            "        .mapNotNull { it.id } // حماية من null وبدون !!\n"
            "        .forEach { id ->\n"
            "            analytics.track(id) // استدعاء مباشر بدون تخصيص ذاكرة زائد\n"
            "        }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "I review Kotlin APIs across three pillars: 1) Null Safety (eliminating '!!', guarding Java platform types, minimizing lateinit); 2) Allocation Cost (using Sequences for large chains, avoiding captured lambdas in loops, leveraging inline and value classes); and 3) Readability (enforcing immutability by default, preventing nested scope functions, and ensuring expressive domain naming).",
        "best_answer": (
            "When reviewing a Kotlin API or Pull Request, I evaluate code against three architectural pillars: null safety, allocation cost, and idiomatic readability.\n\n"
            "For null safety, I have a zero-tolerance policy for the double-bang operator (!!). I look for defensive boundary checks where Java platform types enter the module, ensure nullable types are handled via safe calls or exhaustive when expressions, and verify that `lateinit` is restricted to framework dependency injection.\n\n"
            "For allocation cost, I audit hot paths and collections. I look for chained collection transformations that allocate intermediate lists and recommend Sequences for larger datasets. I check if lambdas capture outer variables inside loops, which causes repeated heap allocations, and verify that value classes aren't inadvertently boxed in generic collections.\n\n"
            "For readability, I ensure public APIs expose read-only types (`List` rather than `MutableList`), prefer `val` over `var`, and flag tangled scope function chains like `let` inside `also` inside `apply`. Code must be readable from left-to-right without requiring cognitive gymnastics."
        ),
        "deep_answer": (
            "In enterprise Android codebases, code review is an engineering gate supported by static analysis tooling. We configure Detekt and Android Lint in CI to mechanically enforce baseline rules (flagging `!!`, catching unused return values, and restricting `lateinit`), freeing human reviewers to focus on architectural nuance.\n\n"
            "At the deeper review level: "
            "1. Jetpack Compose Stability: I inspect data classes passed to Composables, ensuring properties are `val` and collections are wrapped in immutable types (like Kotlinx ImmutableList) so the Compose compiler marks parameters as stable, enabling recomposition skipping. "
            "2. Coroutine Hygiene: I check that suspend functions do not block threads, that `withContext(Dispatchers.IO)` is confined to the lowest data layer, and that `CancellationException` is never swallowed by broad `catch (e: Exception)` blocks. "
            "3. Binary Compatibility: For shared library modules, I ensure public API changes do not break binary backward compatibility, using the Jetpack Binary Compatibility Validator plugin to track public symbol diffs."
        ),
        "follow_ups": [
            {
                "interviewer": "How do you detect accidental allocations during code review?",
                "answer": "By looking for: 1) boxing of value classes into generic collections or nullable types; 2) non-inlined higher-order functions in loops; 3) string concatenation inside high-frequency loops instead of StringBuilder; and 4) eagerly chained collection transformations on large collections. When in doubt, we inspect the decompiled bytecode in Android Studio."
            },
            {
                "interviewer": "Why is `mapNotNull` preferred over `filter { it != null }.map { it!! }`?",
                "answer": "`mapNotNull` performs the null check and transformation in a single pass without allocating an intermediate list, and completely eliminates the unsafe `!!` operator, making the code both cleaner and safer."
            },
            {
                "interviewer": "What automated tools do you integrate into CI to enforce Kotlin code quality?",
                "answer": "We integrate Detekt for Kotlin-specific code smells and complexity metrics, KtLint for formatting consistency, Android Lint for Android-specific bugs and performance warnings, and the Jetpack Binary Compatibility Validator for public API changes."
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

    for q in KOT_23_30:
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
    print(f"Updated {DATA_FILE} with questions through KOT-30. Total questions: {len(combined)}")


if __name__ == "__main__":
    main()

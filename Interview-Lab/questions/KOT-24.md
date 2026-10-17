---
id: "KOT-24"
question: "What is JNI, and why might an Android project use C++?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "B"
phase: 1
priority: "P1"
order: 24
editorial_status: "reviewed"
---

# KOT-24

## Original interview question

What is JNI, and why might an Android project use C++?

## What the interviewer evaluates

Define JNI bridge, realistic NDK reasons, cross-boundary costs and native failure/security limits.

## Concept and technical explanation

The Java Native Interface (JNI) and Android Native Development Kit (NDK) provide the interoperability bridge allowing managed Kotlin and Java code executing on the Android Runtime (ART) to call, and be called by, native applications and libraries written in C and C++. In Android engineering, JNI is predominantly used for computationally intensive or low-latency domains: real-time digital audio processing via Oboe or AAudio, computer vision and image processing using OpenCV, high-performance game rendering via Vulkan, machine learning inference engines like TensorFlow Lite or ONNX Runtime, and reusing mature cross-platform C/C++ core engines. However, JNI is not an automatic performance booster. Crossing the JNI boundary incurs substantial CPU call overhead due to thread state transitions, stack frame adjustments, and argument marshaling. Additionally, NDK code increases APK size across CPU architectures (ABIs), complicates debugging with fatal SIGSEGV signals that bypass JVM exception handlers, and introduces native memory leak risks outside the garbage collector.

## Practical walkthrough (English)

Consider a real-time camera filter application processing 4K video frames at 60 frames per second. A catastrophic anti-pattern is calling JNI per-pixel in a nested loop: `for (y in 0 until height) for (x in 0 until width) applyNativeFilter(pixel[x][y])`. The JNI call overhead and boundary transitions executed millions of times per frame will freeze the application and drop frames completely. The high-performance architecture utilizes Direct Buffers: Kotlin allocates a single direct byte buffer outside the garbage-collected heap: `val directBuffer = ByteBuffer.allocateDirect(frameSize)`, and passes it to native code once per frame: `nativeProcessFrame(directBuffer, width, height)`. In C++, the native implementation obtains the direct raw memory pointer using `env->GetDirectBufferAddress(directBuffer)` and leverages ARM NEON SIMD vector instructions to process sixteen pixels per CPU clock cycle with zero data copying and zero GC allocation.

## Explanation in Arabic

الـ JNI (Java Native Interface) والـ Android NDK (Native Development Kit) هما الجسر اللي بيربط كود Kotlin/Java في الـ JVM بكود C و C++ الأصلي المترجم لـ Machine Code للـ CPU:

1. ليه تطبيق Android ممكن يحتاج C++ و NDK؟
   - **معالجة الوسائط والألعاب عالية الأداء:** معالجة الفيديو في الوقت الفعلي (OpenCV)، محركات الألعاب (Unreal, Unity, Vulkan)، ومعالجة الصوت فائقة السرعة زمنياً (AAudio, Oboe).
   - **إعادة استخدام مكتبات C/C++ العريقة:** زي SQLite core، تشفير OpenSSL، أو موديلات الذكاء الاصطناعي (TensorFlow Lite C++ API, llama.cpp).
   - **حسابات رياضية مكثفة:** تستفيد من تعليمات الـ CPU المباشرة زي ARM NEON SIMD instructions.

2. تكاليف وعيوب الـ JNI Bridge (The JNI Overhead):
   - عبور جسر الـ JNI (JNI Call Overhead) مكلف! كل نداء بين Kotlin و C++ بيحتاج Context Switch وتجهيز الـ Call Frame وعمل Pinning للذاكرة أو نسخ للـ Buffers.
   - استدعاء دالة C++ صغيرة ملايين المرات داخل Loop ممكن يكون **أبطأ** من كتابتها في Kotlin بسبب تكلفة العبور!
   - صعوبة الصيانة وتعدد الـ ABIs: مضطر تبني الـ Shared Library (`.so`) لعدة معماريات (`arm64-v8a`, `armeabi-v7a`, `x86_64`) مما يزيد حجم الـ APK.

## Practical walkthrough

في تطبيق معالجة صور الكاميرا (Image Filter Application):
- الكاميرا بتخرج 60 إطار في الثانية (60 FPS) بدقة 4K بصيغة YUV_420_888.
- **النهج الخاطئ عبر JNI:**
  المرور على كل بكسل واستدعاء دالة native لكل بكسل:
  `for (pixel in pixels) nativeFilterPixel(pixel)` // كارثة أداء! تكلفة الـ JNI overhead هتوقف الـ App فوراً.
- **النهج الصحيح:**
  تمرير Direct ByteBuffer للـ Frame كامل مرة واحدة:
  `val directBuffer = ByteBuffer.allocateDirect(frameSize)`
  `nativeProcessFrame(directBuffer, width, height)`
  في C++، بنقرا الـ Pointer مباشرة بدون نسخ للبيانات وبنستخدم ARM NEON instructions لمعالجة 16 بكسل في دورة CPU واحدة.
- النتيجة: معالجة سلسة عند 60 FPS بدون استهلاك زائد للـ Garbage Collector.

## Why it matters and how it works

JNI enables reuse of native code and access to native APIs, but introduces a second runtime and ABI. The application must manage thread attachment, reference lifetimes, errors, and build variants.

## Worked example

Conceptual Android declaration only; it requires a matching C/C++ implementation built for supported ABIs and loaded by `System.loadLibrary`.
```kotlin
object SignalEngine {
    init { System.loadLibrary("signal") }
    external fun process(samples: ShortArray): ShortArray
}
```
The native implementation must validate lengths and handle memory and exceptions; this snippet alone is not executable.

## Trade-offs and decision criteria

Prefer Kotlin/Java for ordinary app logic. Choose NDK when a native library or measured compute path justifies tooling, ABI packaging, and crash-debugging cost. Minimize crossings by passing sensible batches, but avoid giant copies that inflate memory.

## Failure modes

Caching a local JNI reference across calls or using `JNIEnv*` on another thread can crash. Validate inputs, use correct global reference lifetime, and test with sanitizers where possible. Also avoid shipping API secrets in native constants: an attacker can reverse engineer the binary.

## Production perspective

An audio editor reuses a mature C++ DSP engine. Kotlin owns UI and lifecycle; a narrow JNI adapter batches samples, maps errors, packages needed ABIs, and is exercised on devices under cancellation and memory pressure. Server-side licensing decisions remain authoritative.

## Interview answer — short

JNI connects managed Kotlin/JVM code with native C/C++ libraries compiled with the Android NDK. It is justified for CPU-intensive computing like low-latency audio, computer vision, game engines, and reusing existing C++ libraries. However, crossing the JNI boundary has measurable call overhead, increases APK size across ABIs, and introduces native memory leak risks.

## Interview answer — structured

The Java Native Interface, or JNI, is the bridging mechanism that connects managed Kotlin code on the Android Runtime with compiled native C and C++ libraries. Using the Android NDK, teams compile native shared libraries tailored for target device CPU architectures.

An Android project adopts C++ primarily for low-latency digital signal processing like real-time audio, heavy image manipulation, machine learning inference engines, or reusing mature cross-platform core libraries.

In production, however, JNI is never a silver bullet for general app performance. Crossing the JNI boundary incurs noticeable CPU overhead due to thread state synchronization, argument marshaling, and ART transition frames.

High-frequency granular native calls in loops perform significantly worse than pure Kotlin, which is why senior engineers batch data using direct byte buffers to minimize crossings.


## Interview answer — deep senior

Under the hood on ART, crossing the JNI boundary requires a formal runtime transition between managed and native thread execution states. When a thread invokes a `native` function, ART must transition the thread from `Runnable` to `Native` state, push a JNI transition frame onto the call stack, register local reference tables, and synchronize CPU registers. This transition boundary prevents the ART JIT and AOT compilers from inlining the native call into calling Kotlin bytecode. Memory management across the boundary presents severe hazards. Every Java object passed into native code creates a local reference in JNIEnv's Local Reference Table, which has a default capacity of 512 entries. Looping over objects in native code without calling `DeleteLocalRef` will overflow this table and crash the process with a fatal JNI error. Furthermore, passing primitive arrays with functions like `GetPrimitiveArrayCritical` pins memory in the ART heap or creates a full memory copy, stalling the garbage collector. To achieve true zero-copy performance in high-throughput workloads, architects mandate `ByteBuffer.allocateDirect()`, which allocates native memory on the POSIX heap that C++ can access directly via raw pointers. Finally, crashes in native code—such as buffer overflows or null pointer dereferences—manifest as uncatchable Linux kernel signals like SIGSEGV or SIGBUS, terminating the Android process instantly without generating a standard JVM crash trace.

## How to answer in the interview

- **Why:** Execute performance-critical algorithms, reuse cross-platform C/C++ libraries, or interface with low-level OS APIs.
- **How:** Declare `external fun` in Kotlin and implement the corresponding native method using the Java Native Interface (JNI).
- **Trade-offs:** JNI introduces bridging overhead, memory management complexity (manual allocation/deallocation), and multi-architecture APK bloat (`armeabi-v7a`, `arm64-v8a`).
- **Failure cases:** Hardcoding sensitive API keys or crypto secrets in C++ believing they cannot be extracted; native shared libraries (`.so`) are easily decompiled using Ghidra or IDA Pro.
- **Production solution:** Restrict JNI to heavy computational workloads (video processing, game engines, custom audio DSP), and protect secrets using backend authorization and Play Integrity.

## Deep-dive talking points

Discuss ABI splits, `JNIEnv` thread affinity, local/global references, exception handling, array copying, native crash observability and APK inspection.

## Follow-up questions

- **Interviewer:** "What causes a memory leak in JNI?"
  **Answer:** "Failing to release native heap memory allocated with `malloc`/`new`, or failing to delete JNI references. Creating `NewGlobalRef` or accumulating unreleased `LocalRef` handles inside a loop exhausts the JNI local reference table (which has a default limit of 512 entries on Android) and causes process crashes."

- **Interviewer:** "How does JNI affect APK size?"
  **Answer:** "Every compiled C++ library must be packaged into the APK for each supported CPU ABI (arm64-v8a, armeabi-v7a, x86_64). Unless using Android App Bundles (AAB) to split APKs by ABI at install time, bundling multiple native libraries drastically inflates total download size."

- **Interviewer:** "Can C++ call back into Kotlin functions through JNI?"
  **Answer:** "Yes. C++ code can use the `JNIEnv` pointer to look up Kotlin/Java class signatures (`FindClass`), find method IDs (`GetMethodID`), and invoke methods (`CallVoidMethod`). However, caching class and method IDs in native code is essential, as dynamic lookups at runtime are extremely slow."

## Self-check rubric

Name two legitimate JNI uses, two boundary costs, and one native memory or security failure.

## References and reviewed-on date

- [Android add native code](https://developer.android.com/studio/projects/add-native-code) — NDK integration.
- [Android JNI tips](https://developer.android.com/ndk/guides/jni-tips) — references, threads and performance.

Technically reviewed against primary documentation on 2026-10-13.

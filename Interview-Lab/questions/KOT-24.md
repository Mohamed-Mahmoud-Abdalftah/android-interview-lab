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

JNI connects Kotlin/JVM code with native C/C++ libraries compiled with the Android NDK. It is used for CPU-intensive tasks like low-latency audio, computer vision, game engines, and reusing existing C++ libraries. However, crossing the JNI boundary has call overhead, increases APK size across ABIs, and introduces native memory leak risks.

## Interview answer — structured

JNI, or Java Native Interface, is the bridging mechanism that allows Android's managed runtime (ART) to call into compiled native C/C++ code, and vice versa. Using the Android NDK, teams compile native shared libraries (.so files) for target CPU architectures.

We use C++ in Android primarily for four scenarios: 1) low-latency, real-time audio using libraries like Oboe; 2) heavy image and video signal processing with OpenCV or custom shaders; 3) running machine learning inference runtimes like ONNX or TensorFlow Lite; and 4) cross-platform shared domain cores written in C++.

However, JNI is not a silver bullet. Crossing the JNI boundary incurs noticeable CPU overhead due to argument marshaling, memory boundary synchronization, and ART JNI transition frames. If you make high-frequency native calls in a loop, it will actually perform worse than pure Kotlin. To use JNI effectively, you batch data using Direct ByteBuffers, minimizing crossings.

## Interview answer — deep senior

At the systems level, ART manages native interactions through JNIEnv pointers. Calling a native method requires ART to transition thread states from Runnable to Native. During this time, the garbage collector cannot relocate objects referenced by native pointers unless they are properly registered as JNI Global, Local, or Weak references. Passing Java arrays across JNI often forces the runtime to either pin the array memory or allocate a duplicate native buffer via `GetPrimitiveArrayCritical`, risking severe memory fragmentation or thread stalls.

To achieve peak performance with JNI: 1) Allocate off-heap native memory using `ByteBuffer.allocateDirect()`, which lets C++ access the memory pointer via `GetDirectBufferAddress()` with zero copies; 2) Leverage CPU-specific vectorization like ARM NEON instructions in C++; 3) Keep the API surface coarse-grained—send one heavy buffer per frame rather than hundreds of granular calls.

Finally, native crashes (SIGSEGV, SIGBUS) do not trigger standard Java crash handlers; they terminate the process instantly unless hooked via a native crash reporting library like Google Breakpad or Firebase Crashlytics NDK.

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

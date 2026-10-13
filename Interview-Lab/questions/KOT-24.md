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

JNI هي Java Native Interface: جسر بين Kotlin/Java على JVM وبين native C/C++ library. Android project يستخدم NDK لما عنده library C/C++ موجودة، codec أو DSP محتاج native implementation، أو API hardware/library بواجهة native. ده مش معناه إن C++ أسرع لكل شغل؛ عبور boundary، تحويل strings/arrays، وإدارة references مكلف. `JNIEnv*` مرتبط بالـthread، local/global references لها lifetime، وnative memory bugs ممكن تعمل crash صعب. كمان الـ`.so` داخل APK قابل للتحليل، فلا تخزن فيه سر وتعتبره محمي.

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

## Practical walkthrough

لو عندك C++ signal-processing library موجودة أو function اتقاست وطلعت محتاجة native implementation، JNI bridge ممكن يستحق التكلفة. `external fun process(samples: ShortArray)` لازم يقابله symbol/build صحيح لكل ABI، و`System.loadLibrary` ممكن يفشل بـ`UnsatisfiedLinkError` لو packaging غلط. نقل array عبر bridge ممكن يعمل copy/pinning، وnative crash يوقع process كله؛ راجع bounds، exceptions، thread attachment، وrelease symbols. اعمل thin API بمدخلات ومخرجات واضحة واختبر arm64/device الواقعي. لو الهدف إخفاء secret، JNI مش trust boundary والمفتاح الثابت يفضل قابل للاستخراج.

## Trade-offs and decision criteria

Prefer Kotlin/Java for ordinary app logic. Choose NDK when a native library or measured compute path justifies tooling, ABI packaging, and crash-debugging cost. Minimize crossings by passing sensible batches, but avoid giant copies that inflate memory.

## Failure modes

Caching a local JNI reference across calls or using `JNIEnv*` on another thread can crash. Validate inputs, use correct global reference lifetime, and test with sanitizers where possible. Also avoid shipping API secrets in native constants: an attacker can reverse engineer the binary.

## Production perspective

An audio editor reuses a mature C++ DSP engine. Kotlin owns UI and lifecycle; a narrow JNI adapter batches samples, maps errors, packages needed ABIs, and is exercised on devices under cancellation and memory pressure. Server-side licensing decisions remain authoritative.

## Interview answer — short

JNI is the bridge between JVM code and native code. I use it for an existing C++ library or measured native requirement, then account for ABI packaging, data copying, memory safety, and native crashes. It does not make client-side secrets safe.

## Interview answer — structured

I would first justify the boundary: perhaps a mature C++ codec or measured signal-processing workload. Kotlin declares an `external` method and loads a native library, but the project must build matching binaries for supported ABIs and honor JNI signatures. Crossing the boundary can copy data, and native memory errors can crash the process outside ordinary Kotlin exception handling. I keep the interface narrow, validate array sizes and error codes, retain symbols for crash diagnosis, and run device tests in release configuration. I would not introduce JNI merely to hide an API key; the native library is still shipped to the client.

## Interview answer — deep senior

The decision starts with a measured or integration requirement: reuse a native codebase or access a native API. I account for build variants, ABI size, symbols, crash collection, sanitizers, and lifecycle. `JNIEnv` is thread-specific; local references are call-scoped, while global references require explicit deletion. Arrays and strings may be copied or pinned depending on API and implementation, so batching matters. Native code also expands the attack surface, and APK-delivered binaries are inspectable. Business authority and long-term secrets stay on a trusted server.

For a C++ image codec, I would keep the JNI entry point narrow: pass a bounded byte buffer, validate lengths, return a documented status, and release native references correctly. I would package and test the supported ABIs, preserve native symbols for crash reports, and run sanitizers where possible. A blocking native call still blocks the Java/Kotlin caller, so it must not run on Main. I would compare the bridge and copying overhead against a pure Kotlin or Java implementation under a real workload. JNI is justified by reuse or measured behavior, not by a belief that C++ hides secrets.

## How to answer in the interview

- **Why:** Execute performance-critical algorithms, reuse cross-platform C/C++ libraries, or interface with low-level OS APIs.
- **How:** Declare `external fun` in Kotlin and implement the corresponding native method using the Java Native Interface (JNI).
- **Trade-offs:** JNI introduces bridging overhead, memory management complexity (manual allocation/deallocation), and multi-architecture APK bloat (`armeabi-v7a`, `arm64-v8a`).
- **Failure cases:** Hardcoding sensitive API keys or crypto secrets in C++ believing they cannot be extracted; native shared libraries (`.so`) are easily decompiled using Ghidra or IDA Pro.
- **Production solution:** Restrict JNI to heavy computational workloads (video processing, game engines, custom audio DSP), and protect secrets using backend authorization and Play Integrity.

## Deep-dive talking points

Discuss ABI splits, `JNIEnv` thread affinity, local/global references, exception handling, array copying, native crash observability and APK inspection.

## Follow-up questions

- [KOT-29](../kot-29/): Does moving a key to C++ protect it? **Answer:** no; the native library is distributed with the app and can be inspected.
- [KOT-30](../kot-30/): How should JNI cost be reviewed? **Answer:** measure crossing frequency, copies, memory and crash rates on target devices.

## Self-check rubric

Name two legitimate JNI uses, two boundary costs, and one native memory or security failure.

## References and reviewed-on date

- [Android add native code](https://developer.android.com/studio/projects/add-native-code) — NDK integration.
- [Android JNI tips](https://developer.android.com/ndk/guides/jni-tips) — references, threads and performance.

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.

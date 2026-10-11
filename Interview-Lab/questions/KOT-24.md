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

## Trade-offs and decision criteria

Prefer Kotlin/Java for ordinary app logic. Choose NDK when a native library or measured compute path justifies tooling, ABI packaging, and crash-debugging cost. Minimize crossings by passing sensible batches, but avoid giant copies that inflate memory.

## Failure modes

Caching a local JNI reference across calls or using `JNIEnv*` on another thread can crash. Validate inputs, use correct global reference lifetime, and test with sanitizers where possible. Also avoid shipping API secrets in native constants: an attacker can reverse engineer the binary.

## Production perspective

An audio editor reuses a mature C++ DSP engine. Kotlin owns UI and lifecycle; a narrow JNI adapter batches samples, maps errors, packages needed ABIs, and is exercised on devices under cancellation and memory pressure. Server-side licensing decisions remain authoritative.

## Interview answer — short

JNI is the bridge from JVM code to native C/C++ code. Android apps use it for existing native libraries or justified performance work. It adds ABI, memory, threading, and debugging complexity, and native code does not hide secrets.

## Interview answer — structured

Kotlin can declare an `external` function and load a shared library through the NDK. JNI then marshals values across the VM/native boundary. That is useful for a proven C++ codec or computation engine, but each crossing and conversion costs time and memory. I keep the interface narrow, validate inputs, manage JNI references and thread attachment, and test native crashes on supported ABIs. I do not put client secrets in the `.so` and call them secure. I would justify JNI when reusing a proven native codec or when profiling shows a compute path benefits from C++, not for normal view or repository code. The Kotlin declaration is only one side; the C++ library has to be built for supported ABIs and loaded. I would keep boundary calls coarse enough to avoid constant copying, then test reference lifetimes, native crashes, and cancellation behavior on actual devices.

## Interview answer — deep senior

The decision starts with a measured or integration requirement: reuse a native codebase or access a native API. I account for build variants, ABI size, symbols, crash collection, sanitizers, and lifecycle. `JNIEnv` is thread-specific; local references are call-scoped, while global references require explicit deletion. Arrays and strings may be copied or pinned depending on API and implementation, so batching matters. Native code also expands the attack surface, and APK-delivered binaries are inspectable. Business authority and long-term secrets stay on a trusted server. JNI connects code executing in the JVM to native C or C++ functions, often packaged through the Android NDK. Native heap bugs are outside Kotlin's memory safety and may crash the process without an ordinary exception. I would design a narrow interface, validate sizes and types on both sides, package supported ABIs, symbolicate crash reports, and use sanitizers in testing. Performance is workload-specific; crossing the bridge for tiny operations can lose more than native computation gains. I would also define what happens if native code reports an error or the UI cancels while a call is running. JNI does not automatically make C++ work cancellable; the adapter and engine need an explicit contract. Operationally, I need symbols and device/ABI crash data to debug failures.

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

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.

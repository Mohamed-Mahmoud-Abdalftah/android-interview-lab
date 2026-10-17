---
id: "BLD-14"
question: "How do you diagnose missing native libraries or ABI incompatibility?"
topic: "Gradle, AGP, R8, Signing & Release Engineering"
code: "BLD"
group: "B"
phase: 4
priority: "P1"
order: 388
editorial_status: "reviewed"
---

# BLD-14

## Original interview question

How do you diagnose missing native libraries or ABI incompatibility?

## What the interviewer evaluates

- Connect device ABI, packaged `.so` paths and runtime loader error.
- Inspect AAB-derived splits and transitive native dependencies.
- Test supported ABI matrix without indiscriminate `pickFirst` or filters.

## Concept and technical explanation

Diagnosing native library crashes and ABI incompatibilities requires understanding how Android's dynamic linker and 64-bit zygote process resolve native binaries:
- The Error Signature: java.lang.UnsatisfiedLinkError: dlopen failed: library "libcustom.so" not found or has text relocations or 32-bit instead of 64-bit.
- The Partial ABI Coverage Trap: The most insidious native packaging bug occurs when third-party libraries supply mismatched ABI sets. If Library A supplies arm64-v8a and armeabi-v7a, but Library B supplies only armeabi-v7a, Android's OS loader sees that the APK contains an arm64-v8a directory. Consequently, on modern 64-bit hardware, the OS launches the application inside a 64-bit Zygote process and configures the native library search path to point exclusively to the app's 64-bit native lib directory. When code attempts to load Library B via System.loadLibrary(), the linker cannot locate a 64-bit .so, throwing an immediate UnsatisfiedLinkError at runtime!
- Diagnostic Protocol:
  1. Inspect APK composition with APK Analyzer: Open the lib/ directory and ensure that every single .so file present in armeabi-v7a also exists in arm64-v8a.
  2. Inspect binary dependencies with readelf -d libcustom.so: Examine the NEEDED dynamic section to verify all required runtime dependencies (such as libc++_shared.so) are bundled.
  3. Enforce ABI Symmetry via ndk.abiFilters: Configure Gradle to prune unsupported ABIs or restrict packaging to uniform targets.

## Practical walkthrough (English)

Inspecting dynamic linkage with readelf and enforcing uniform ABI filters in Gradle:
```bash
# 1. Inspect dynamic shared library requirements via readelf
aarch64-linux-android-readelf -d libcustom.so | grep NEEDED
# Example output: (NEEDED) Shared library: [libc++_shared.so]
```

```kotlin
// 2. build.gradle.kts: Enforcing uniform ABI coverage
android {
    defaultConfig {
        ndk {
            // Strictly enforce symmetric dual-ARM architecture support
            abiFilters += listOf("armeabi-v7a", "arm64-v8a")
        }
    }

    packaging {
        jniLibs {
            // Ensure first copy of shared C++ STL is selected
            pickFirsts += listOf("**/libc++_shared.so")
        }
    }
}
```

## Explanation in Arabic

كيف تستكشف وتصلح أخطاء غياب مكتبات الـ Native (UnsatisfiedLinkError) ومشاكل عدم توافق معمارية المعالج (ABI Incompatibility)؟

1. خطأ الانهيار الشهير (UnsatisfiedLinkError: dlopen failed):
   - يحدث عندما يحاول التطبيق استدعاء `System.loadLibrary("crypto")` أو تشغيل كود C++ عبر JNI، ولكنه لا يجد ملف `libcrypto.so` المخصص لمعمارية الهاتف الحالية.

2. الكارثة الشائعة: الـ 32-bit vs 64-bit Mismatch (مشكلة الـ ABI غير المتناسقة):
   - إذا استخدم تطبيقك مكتبتين:
     * مكتبة A توفر كود لكل من: `arm64-v8a` و `armeabi-v7a`.
     * مكتبة B توفر كود لـ `armeabi-v7a` فقط (لا تملك كود 64-bit)!
   - **ماذا يفعل أندرويد على هاتف حديث (64-bit)**؟
     * يرى النظام أن التطبيق يحتوي على مجلد `lib/arm64-v8a/`، فيقوم بتشغيل التطبيق في وضع 64-bit ويبحث عن جميع المكتبات داخل هذا المجلد فقط!
     * عندما يحاول التطبيق تشغيل مكتبة B، لا يجدها في مجلد 64-bit، فينهار التطبيق فوراً برمي `UnsatisfiedLinkError`!

3. خطوات التشخيص والحل:
   - فحص الـ APK عبر **APK Analyzer**: فتح مجلد `lib/` والتأكد من أن كل ملف `.so` موجود في **جميع** مجلدات المعماريات بالتساوي.
   - **الحل**: إما الحصول على نسخة 64-bit من المكتبة الناقصة، أو إجبار التطبيق على العمل في وضع 32-bit عبر تقييد الـ `ndk.abiFilters` على `armeabi-v7a` فقط.

## Practical walkthrough

تشخيص محتويات الـ ABIs داخل الـ APK وحل مشكلة عدم تناسق المكتبات:
```bash
# 1. فحص ملفات الـ .so المضمنة في كل معمارية باستخدام unzip:
unzip -l app-release.apk "lib/*"

# النتيجة توضح وجود عدم تناسق (libfoo موجود في المعماريتين، بينما libbar ناقص في 64-bit!):
# lib/arm64-v8a/libfoo.so
# lib/armeabi-v7a/libfoo.so
# lib/armeabi-v7a/libbar.so   <-- غائب في arm64-v8a!
```

```kotlin
// 2. الحل المؤقت في build.gradle.kts إذا لم تتوفر نسخة 64-bit للمكتبة:
android {
    defaultConfig {
        ndk {
            // إجبار التطبيق بالكامل على العمل في وضع 32-bit لحين ترقية المكتبة:
            abiFilters.clear()
            abiFilters.add("armeabi-v7a")
        }
    }
}
```

## Why it matters and how it works

Android selects native code compatible with a device ABI from package paths and linked dependencies. App Bundles can deliver ABI-specific splits, so a universal APK may not match production packaging. A library can be present yet fail because of missing dependent `.so`, incompatible symbols, STL or minSdk/architecture assumptions. The loader message and packaged artifact narrow the cause.

## Worked example

Payment scanner works on arm64 but x86_64 emulator throws `dlopen failed: library libscan.so not found`. Inspect bundletool's x86_64 APK set and find the vendor AAR only ships arm64. Choose a vendor-supported x86_64 build or exclude x86_64 from supported delivery intentionally with product/device coverage review; do not copy arm64 `.so` into an x86 folder.

## Trade-offs and decision criteria

Supporting more ABIs increases build/package/test cost; dropping one excludes devices or emulators and may violate store policy. A fallback to Java/Kotlin implementation may preserve a feature when native acceleration is optional. Updating vendor SDK can solve packaging but warrants regression testing across ABIs.

## Failure modes

Only arm64 device is tested. A transitive native dependency is omitted from one split. `pickFirst` chooses an incompatible duplicate. ABI filters remove a required platform unexpectedly. Engineers assume a missing file when the actual error is an unresolved symbol inside it.

## Production perspective

Maintain supported ABI matrix, install bundle-derived artifacts on representative devices/emulators, and assert required `.so` entries and native startup. Segment crash telemetry by ABI and OS version.

## Interview answer — short

Diagnosing native UnsatisfiedLinkError crashes requires resolving partial ABI coverage where libraries provide mismatched architectures, causing 64-bit devices to fail when loading 32-bit binaries. Engineers use APK Analyzer to verify symmetric lib folders, inspect shared dependencies with readelf, and enforce consistent architectures using ndk.abiFilters.

## Interview answer — structured

Diagnosing UnsatisfiedLinkError exceptions and native ABI mismatches requires understanding Android's dynamic linker and process architecture.
First, identify the root cause. The most frequent failure is partial ABI coverage: if one dependency provides an arm64-v8a binary while another provides only armeabi-v7a, a 64-bit device launches a 64-bit Zygote process and searches solely within 64-bit directories, failing to load the 32-bit library.
Second, inspect binary packaging with APK Analyzer. Verify that every .so file in armeabi-v7a has an identical 64-bit counterpart inside arm64-v8a.
Third, inspect dynamic linkage using readelf -d on the compiled library to identify missing dependencies like libc++_shared.so.
Fourth, enforce uniform ABI packaging in build.gradle.kts using ndk.abiFilters, ensuring all bundled libraries support the declared target architectures.

## Interview answer — deep senior

In Android platform engineering, native C++ runtime crashes—typically manifesting as java.lang.UnsatisfiedLinkError: dlopen failed—are among the most catastrophic defects because they bypass standard Java exception handlers and crash the process immediately.
The classic trap in native packaging is the Partial ABI Coverage phenomenon.
Modern Android devices run a 64-bit kernel and launch applications using a 64-bit Zygote process whenever possible.
When the Android package manager installs an APK, it inspects the lib/ directory.
If it discovers an arm64-v8a folder, it marks the application as 64-bit capable and restricts the native linker (dlopen) to searching the 64-bit library directory.
If a legacy third-party dependency only ships a 32-bit armeabi-v7a binary without an arm64-v8a slice, the app runs fine on old 32-bit hardware but crashes instantly on modern devices the moment System.loadLibrary() executes, because the 64-bit loader refuses to load 32-bit binaries.
To diagnose this, our platform triage workflow opens the APK inside APK Analyzer.
We verify symmetry across architecture folders: every .so file in armeabi-v7a must have an exact equivalent in arm64-v8a.
Next, we run readelf -d on the failing binary to inspect its NEEDED header tags, identifying unbundled shared dependencies such as libc++_shared.so.
Finally, in build.gradle.kts, we enforce strict ndk.abiFilters to eliminate incomplete architectures or declare pickFirsts in packaging.jniLibs to resolve duplicate shared library clashes.

## How to answer in the interview

- **Why:** native path depends on device split.
- **How:** inspect ABI, .so and JNI symbols.
- **Trade-off:** reach versus compatible support.
- **Failure case:** debug APK works but release split fails.
- **Production solution:** test target hardware and delivery path.

## Deep-dive talking points

Discuss loader text, ABI selection, split paths, transitive `.so`, symbols, filters and device tests.

## Follow-up questions

- **Interviewer:** "What does readelf -d libfoo.so show?"
  **Answer:** "It displays the dynamic section of the ELF binary, including shared library dependencies listed in NEEDED tags."

- **Interviewer:** "Does Google Play allow uploading 32-bit only APKs today?"
  **Answer:** "No; since August 2019, Google Play mandates 64-bit (arm64-v8a) support for all apps bundling native code."

## Self-check rubric

Trace one loader error to ABI packaging, distinguish absent file from symbol failure, and define matrix tests.

## References and reviewed-on date

- [Android ABIs](https://developer.android.com/ndk/guides/abis) — native package paths and compatibility.
- [Build and test an App Bundle](https://developer.android.com/guide/app-bundle/test) — split delivery tests.

Technically reviewed against primary documentation on 2026-10-13.

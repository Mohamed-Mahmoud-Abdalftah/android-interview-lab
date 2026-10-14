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

Diagnose UnsatisfiedLinkError by inspecting the APK's lib/ directory with APK Analyzer to detect ABI mismatches. If one library includes 64-bit (arm64-v8a) while another only provides 32-bit (armeabi-v7a), the 64-bit OS runs in 64-bit mode and crashes when looking for the missing library. Resolve by adding 64-bit binaries or filtering to 32-bit.

## Interview answer — structured

`java.lang.UnsatisfiedLinkError` occurs when the Android dynamic linker (`dlopen`) fails to locate or load a required native shared object (`.so`) for the current CPU architecture.

First, **The 32-bit vs. 64-bit Asymmetry Trap**. Next, if any third-party SDK includes a 64-bit binary in `lib/arm64-v8a/`, the Android OS launches the app inside a 64-bit Zygote process.
Once running in 64-bit mode, the OS dynamic linker looks **strictly** inside `lib/arm64-v8a/` and will never fall back to 32-bit folders. If a second library in your project only supplied 32-bit `armeabi-v7a` binaries, calls to load that library crash immediately with `UnsatisfiedLinkError: dlopen failed: library not found`.
**Inspection & Diagnosis**. Open the compiled APK in Android Studio's **APK Analyzer** or execute `unzip -l app.apk "lib/*"`.
Verify that the exact same set of `.so` library names exists across all supported ABI folders. **Resolution Strategies**.
With Preferred, procure or compile 64-bit `.so` binaries for the missing dependencies (mandatory for Google Play compliance). Finally, with Fallback, enforce uniform 32-bit packaging via `ndk.abiFilters.add("armeabi-v7a")` until 64-bit dependencies are available.


## Interview answer — deep senior

From an OS loader and systems architecture perspective, native linking errors can also stem from missing transitive dependencies and text relocations.

First, missing Transitive Dependencies (`NEEDED` ELF headers) is a `. So` file often depends on secondary libraries (e.g. `libnative.so` depends on `libcrypto.so`). If `libcrypto.so` is missing from the APK or stripped by packaging excludes, `dlopen("libnative.so")` fails with `library "libcrypto.so" not found`. Inspect ELF dependencies using `readelf -d libnative.so | grep NEEDED`. Next, with Text Relocations (API 23+), since Android 6.0, Android blocks libraries with text relocations (`W^X` memory protection). Libraries compiled with legacy NDK toolchains without `-fPIC` throw `dlopen failed: has text relocations` and crash on modern devices.
Finally, with Automated ABI Verification in CI, add an automated assertion test in CI that unpacks the built APK and asserts that the file lists under `lib/arm64-v8a/` and `lib/armeabi-v7a/` are identical, failing the build on asymmetric native packaging.


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

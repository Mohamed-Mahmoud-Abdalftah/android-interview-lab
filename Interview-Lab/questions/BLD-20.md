---
id: "BLD-20"
question: "A feature works on arm64 but fails on another ABI. How do you debug packaging?"
topic: "Gradle, AGP, R8, Signing & Release Engineering"
code: "BLD"
group: "C"
phase: 4
priority: "P1"
order: 394
editorial_status: "reviewed"
---

# BLD-20

## Original interview question

A feature works on arm64 but fails on another ABI. How do you debug packaging?

## What the interviewer evaluates

- Compare actual delivered splits and native dependency closure by ABI.
- Diagnose missing file versus incompatible symbols/loader behavior.
- Make support policy explicit and test the affected architecture.

## Concept and technical explanation

Diagnosing feature failures on specific CPU ABIs (such as armeabi-v7a or x86_64) while passing on arm64-v8a requires inspecting native packaging and architecture compatibility:
- Primary Root Causes of Single-ABI Failures:
  1. Packaging Asymmetry: An upstream transitive library bundles .so shared objects for arm64-v8a but omits them for 32-bit ARM or x86. Android's dynamic linker loads the 32-bit runtime on 32-bit devices and fails with dlopen failed: library not found.
  2. Android 15 16KB Page Alignment Violations: Android 15 introduces support for 16KB memory page sizes. Native libraries compiled with older NDKs targeting 4KB boundaries fail to load on 16KB-configured devices with memory alignment faults.
  3. CPU Instruction Incompatibilities: Native C/C++ routines invoking architecture-specific vector registers (e.g. ARM NEON SIMD) without runtime CPU capability detection crash with SIGILL (Illegal Instruction) on incompatible hardware or emulators.
  4. C++ Runtime Collisions: Multiple native dependencies bundling mismatched libc++_shared.so versions resolved via pickFirsts, creating memory layout incompatibilities.
- Systematic Packaging Debugging Protocol:
  - Step 1: Inspect native directories inside the APK via unzip -l app.apk "lib/*" or APK Analyzer to verify parity across all ABI subfolders.
  - Step 2: Audit ELF memory page alignment using readelf -l libname.so | grep -A 1 LOAD to verify that Align equals 0x4000 (16KB).
  - Step 3: Run the app on an emulator targeting the failing ABI and capture linker diagnostics via adb logcat | grep -E "linker|DEBUG".
- Remediation: Enforce ndk.abiFilters in build.gradle.kts, update NDK toolchains to r27+, and implement CPU runtime feature probing.

## Practical walkthrough (English)

Native binary inspection commands and Gradle ABI configuration:
```bash
# 1. Audit native library parity across all bundled ABI directories:
unzip -l app/build/outputs/apk/release/app-release.apk "lib/*"

# 2. Check 16KB memory page size alignment for Android 15+ compatibility:
readelf -l app/build/intermediates/merged_native_libs/release/mergeReleaseNativeLibs/out/lib/arm64-v8a/libnative.so | grep -A 1 LOAD
# Verify that Align equals 0x4000 (16KB)

# 3. Capture dynamic linker errors on failing emulator:
adb logcat | grep -E "linker|DEBUG"
```

```kotlin
// 4. Configure ABI filters and CMake compilation in build.gradle.kts:
android {
    defaultConfig {
        ndk {
            abiFilters.addAll(listOf("arm64-v8a", "armeabi-v7a", "x86_64"))
        }
        externalNativeBuild {
            cmake {
                arguments("-DANDROID_STL=c++_shared")
            }
        }
    }
}
```

## Explanation in Arabic

ميزة برمجية تعمل بكفاءة على معمارية `arm64-v8a` ولكنها تنهار على معمارية أخرى (مثل `armeabi-v7a` أو `x86_64`). كيف تستكشف وتصلح أخطاء الحزم البرمجية (Packaging)؟

1. الأسباب الشائعة للفشل على معمارية معينة دون غيرها:
   - **غياب مكتبة Native مخصصة للمعمارية (Missing .so binary)**: مكتبة خارجية وفرت كود لـ ARM64 فقط وتجاهلت 32-bit أو x86.
   - **أخطاء في محاذاة الـ 16KB Page Alignment (Android 15+)**: أندرويد 15 يتطلب محاذاة صفحات الذاكرة لمكتبات الـ Native على 16KB بدلاً من 4KB. إذا كانت المكتبة مجمعة بـ NDK قديم، تفشل في العمل على الأجهزة الحديثة.
   - **استدعاء دوال غير مدعومة في المعالج (CPU Instruction Incompatibilities)**: كود C++ يستخدم تعليمات خاصة بمعالجات معينة (مثل ARM NEON instructions) دون فحص دعم المعالج عبر CPU Features.

2. خطوات التشخيص:
   - فحص مجلدات الـ `lib/` في الـ APK عبر `unzip -l app.apk "lib/*"`.
   - تشغيل الـ APK على محاكي بالمعمارية الفاشلة ومراقبة سجلات `adb logcat | grep -E "DEBUG|linker"` لمعرفة اسم الملف أو الدالة المفقودة.

3. الحلول الهندسية:
   - إعادة تجميع كود الـ C++ عبر الـ NDK لجميع الـ ABIs المطلوبة.
   - ضبط `ndk.abiFilters` في `build.gradle.kts` لاستبعاد المعماريات غير المدعومة رسمياً.

## Practical walkthrough

تشخيص وفحص محاذاة صفحات الـ 16KB والتأكد من دعم المعماريات المختلفة:
```bash
# 1. فحص محاذاة صفحات الـ ELF لمكتبات الـ Native (16KB Page Size Alignment):
readelf -l app/build/intermediates/merged_native_libs/release/mergeReleaseNativeLibs/out/lib/arm64-v8a/libnative.so | grep LOAD
# يجب أن تكون قيمة الـ Align هي 0x4000 (16KB) لدعم أجهزة Android 15+

# 2. التحقق من تكامل ملفات الـ .so عبر جميع مجلدات المعماريات:
apkanalyzer apk summary app-release.apk
```

```kotlin
// 3. ضبط CMake / NDK في build.gradle.kts لضمان التجميع لجميع المعماريات المطلوبة:
android {
    defaultConfig {
        externalNativeBuild {
            cmake {
                abiFilters("arm64-v8a", "armeabi-v7a", "x86_64")
                arguments("-DANDROID_STL=c++_shared")
            }
        }
    }
}
```

## Why it matters and how it works

Native machine code is ABI-specific. Play may deliver a different set of split APKs per device, so arm64 success does not prove x86_64 package integrity. A shared library can depend on another `.so` or symbol that is absent or incompatible even when its own file is packaged. The loader message and artifact contents distinguish these paths.

## Worked example

A document scanner's arm64 split contains `libscan.so` and `libcrypto_helper.so`; x86_64 split contains only `libscan.so`. On x86_64, `dlopen` reports missing helper library. Trace the vendor AAR and `jniLibs` packaging, supply a compatible x86_64 helper, then install the rebuilt bundle-derived split on an emulator and run scan. A manifest or R8 change would not fix the native dependency closure.

## Trade-offs and decision criteria

Supporting every ABI increases build and QA cost; narrowing support may exclude users and affect store compatibility. A pure Kotlin fallback may preserve limited functionality if native acceleration is optional. Vendor upgrade can repair binaries but may alter API behavior, requiring cross-ABI regression tests.

## Failure modes

Team inspects a universal debug APK rather than Play-delivered release splits. `pickFirst` selects wrong native version. Only top-level `.so` presence is checked while its dependency is missing. An ABI filter hides devices without a product decision. Runtime error is blamed on R8 even though symbols cannot resolve.

## Production perspective

Keep a supported ABI matrix and generate/install artifact sets for each representative device in CI. Assert native file closure, exercise the feature, and monitor release failures segmented by ABI and OS.

## Interview answer — short

We debug ABI-specific packaging failures by inspecting the APK lib directory using unzip or APK Analyzer to verify that all architectures contain identical shared native libraries. We inspect dynamic linker errors in Logcat, verify Android 15 16KB page alignment using readelf, audit CPU instruction compatibility, and align ndk.abiFilters in Gradle.

## Interview answer — structured

When an Android feature functions seamlessly on arm64-v8a but fails on other architectures, senior engineers isolate packaging asymmetry and runtime ABI constraints.
First, we audit the compiled binary. Running unzip on the APK or opening it in APK Analyzer reveals the native directory structure under lib. If a transitive dependency bundles native libraries exclusively for arm64-v8a while omitting them for armeabi-v7a or x86_64, the operating system dynamic linker throws an immediate UnsatisfiedLinkError on 32-bit devices because the expected shared library is missing from that ABI slice.
Second, on Android 15 devices supporting 16KB memory pages, we check ELF binary alignment. Executing readelf on native shared objects verifies whether the LOAD segment alignment equals 0x4000. Libraries built with older NDK toolchains aligned to 4KB crash during process loading on 16KB kernels.
Third, we capture logcat output on the failing architecture emulator. If native C++ code executes vector instructions like ARM NEON without runtime CPU feature detection, it triggers SIGILL crashes.
We remediate these issues by updating to modern NDK toolchains, aligning ndk.abiFilters, and compiling native code with 16KB page alignment.

## Interview answer — deep senior

From a systems programming and multi-architecture runtime perspective, ABI execution divergences arise from packaging disparity, linker constraints, and hardware vector instruction incompatibilities.
In Android's process model, the Zygote selects an application's 32-bit or 64-bit runtime environment based on available native libraries. If an APK contains a primary native library for both arm64-v8a and armeabi-v7a, but a secondary third-party dependency only packages arm64-v8a, the app boots into a 32-bit process on 32-bit devices. When the app attempts to load the secondary library via System.loadLibrary, dlopen fails catastrophically because the 32-bit linker cannot find or load 64-bit binaries.
Another critical issue in modern releases is the Android 15 16KB memory page size mandate. Devices configured with 16KB page sizes reject ELF binaries whose segments are aligned to legacy 4KB boundaries, crashing the process before native code can execute. We verify compliance across all native dependencies by running readelf and asserting an alignment value of 0x4000, updating NDK compilation flags to enforce 16KB alignment.
Additionally, native C++ dependencies often collide on shared runtime libraries like libc++_shared.so. When developers use packaging jniLibs.pickFirsts to resolve duplicate file collisions between libraries compiled against different NDK versions, subtle C++ ABI incompatibilities cause runtime memory corruption and SIGSEGV crashes.
To permanently prevent ABI packaging failures, our continuous integration runs an automated testing matrix executing instrumented tests on both ARM64 and x86_64 emulator system images, ensuring native binaries load cleanly across all targeted architectures before release approval.

## How to answer in the interview

- **Why:** ABI mix changes shipped native set.
- **How:** inspect split and vendor matrix.
- **Trade-off:** reach versus compatibility.
- **Failure case:** universal APK gives false confidence.
- **Production solution:** release device-matrix test.

## Deep-dive talking points

Discuss device-targeted splits, native transitive closure, symbols, filters, vendor AAR and ABI matrix.

## Follow-up questions

- **Interviewer:** "What is the 16KB page size requirement in Android 15?"
  **Answer:** "Android 15 supports devices configured with 16KB memory pages; native ELF binaries must be compiled and aligned with 16KB boundaries (Align 0x4000) or they fail to load."

- **Interviewer:** "What happens if an app loads a native library built with a newer NDK STL than other libraries?"
  **Answer:** "Symbol resolution collisions or memory layout incompatibilities in libc++_shared.so can trigger SIGSEGV crashes at runtime."

## Self-check rubric

Trace one ABI failure from device log to split contents, correct it and validate on target hardware.

## References and reviewed-on date

- [Android ABIs](https://developer.android.com/ndk/guides/abis) — native paths and compatibility.
- [Build and test an App Bundle](https://developer.android.com/guide/app-bundle/test) — targeted split testing.

Technically reviewed against primary documentation on 2026-10-13.

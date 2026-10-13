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

Debug ABI packaging issues by inspecting the APK's lib/ subfolders with unzip or APK Analyzer to confirm whether required .so files exist for the failing architecture. Check for missing 32-bit binaries, Android 15 16KB page alignment violations using readelf, or CPU instruction set incompatibilities.

## Interview answer — structured

When features execute correctly on `arm64-v8a` but fail on other architectures, the failure is typically caused by packaging asymmetry or native instruction incompatibility:

1. **Packaging Asymmetry Audit**:
   - Extract the native binary tree: `unzip -l app.apk "lib/*"`.
   - Verify that the failing architecture (e.g. `armeabi-v7a` or `x86_64`) contains the exact identical set of `.so` shared libraries as `arm64-v8a`. If a transitive SDK only bundles ARM64, loading native components fails on 32-bit devices.

2. **Android 15 16KB Page Alignment Requirements**:
   - Android 15 introduces support for 16KB memory page sizes. Native libraries compiled with older NDK versions aligned to 4KB fail to load on 16KB devices. Inspect alignment using `readelf -l libxyz.so | grep -A 1 LOAD` to verify `Align` equals `0x4000` (16KB).

3. **CPU Instruction Set & NEON Compatibility**:
   - Native C/C++ routines employing hardware-accelerated instructions (e.g., ARM NEON SIMD) crash with `SIGILL (Illegal Instruction)` if executed on CPUs or emulators lacking those specific hardware execution registers. Implement runtime feature probing (`cpufeatures` library) before invoking vector extensions.

## Interview answer — deep senior

From a multi-architecture testing and CI perspective, validating native stability requires matrix testing:

1. **CI Architecture Emulation Matrix**: Run automated instrumentation tests against multiple emulator architectures in CI: ARM64 system images on Apple Silicon/ARM runners, and x86_64 system images on Intel/AMD runners, catching ABI packaging gaps before deployment.

2. **Packaging PickFirsts & Duplicate JNI Libraries**: If two dependencies bundle conflicting versions of `libc++_shared.so`, AGP fails the build with a duplicate file collision. Setting `packaging { jniLibs.pickFirsts.add("**/libc++_shared.so") }` resolves compilation, but can crash at runtime if the picked version has an incompatible C++ ABI. Ensure all native dependencies compile against identical NDK toolchain versions.

3. **NDK abiFilters Alignment**: Explicitly declare `ndk.abiFilters` in `build.gradle.kts` matching the target distribution: `arm64-v8a` and `armeabi-v7a` for consumer devices, plus `x86_64` for developer emulators.

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

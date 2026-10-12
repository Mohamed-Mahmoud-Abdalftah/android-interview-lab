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

سجّل ABI المتأثرة و`UnsatisfiedLinkError`/crash كاملة، version/variant وطريقة التثبيت. استخرج APKs من AAB للـdevice spec بـbundletool، وقارن `lib/arm64-v8a` مع `lib/x86_64` أو ABI المعنية: أسماء .so، transitive dependencies، checksum وpackaging rules. لو .so ناقصة، افحص AAR/NDK build و`abiFilters`; لو موجودة لكن loader يرفضها، ابحث عن symbols/STL/minSdk/CPU instructions. لا تنقل arm64 binary إلى مجلد ABI أخرى. أصلح vendor SDK/build config أو أعلن عدم دعم ABI بعد تقييم المستخدمين، ثم اختبر release split على جهاز/محاكي مناسب.

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

“I reproduce on the failing ABI, inspect its actual AAB-derived APKs and all required `.so` dependencies, then fix packaging or binary compatibility and retest that ABI.”

## Interview answer — structured

“I gather the loader error, device ABI and exact release artifact, generate the corresponding APK set and compare native paths with arm64. A missing file points toward vendor AAR, `jniLibs` or filters; a present file with `dlopen` failure points toward dependent libraries or symbols. I never copy an arm64 binary into an x86 path. The fix is validated by installing the target split and running the feature, then reflected in the supported ABI matrix.”

## Interview answer — deep senior

“I investigate the binary the failing device actually received, not the one that happened to work on my arm64 phone. I record version, variant, install channel, `SUPPORTED_ABIS` and complete `UnsatisfiedLinkError` or native tombstone. I use bundletool or Play testing to extract the device-targeted APKs and inspect `lib/<abi>` contents. Then I compare the transitive native closure: `libscan.so` may be present but depend on a helper missing only for x86_64. If files exist, I inspect unresolved symbols, STL linkage, NDK/minimum platform and instruction assumptions. Gradle `abiFilters`, packaging options or vendor AAR content may explain an omission; `pickFirst` is not a safe general repair for duplicate versions. I obtain the correct ABI binary or document a supported fallback, and only narrow ABI support with product/device impact review. CI installs the minified bundle-derived artifact on representative ABIs and exercises the feature, while crash telemetry is segmented by architecture. The causal fix is demonstrated on the ABI that failed.”

## Deep-dive talking points

Discuss device-targeted splits, native transitive closure, symbols, filters, vendor AAR and ABI matrix.

## Follow-up questions

- Why not trust arm64 success? **Answer:** each ABI receives different machine code and possibly different splits.
- Can a packaged `.so` still fail to load? **Answer:** yes; its dependent libraries or required symbols may be absent.
- What proves the repair? **Answer:** a release-derived package runs the feature on the previously failing ABI.

## Self-check rubric

Trace one ABI failure from device log to split contents, correct it and validate on target hardware.

## References and reviewed-on date

- [Android ABIs](https://developer.android.com/ndk/guides/abis) — native paths and compatibility.
- [Build and test an App Bundle](https://developer.android.com/guide/app-bundle/test) — targeted split testing.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Vendor binaries require direct inspection.

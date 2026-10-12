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

اجمع `UnsatisfiedLinkError` الكامل، device `SUPPORTED_ABIS`، version/variant وطريقة التوزيع. افحص APK/AAB-derived split: هل `/lib/<abi>/libname.so` موجودة للـABI المختارة؟ وهل dependencies native الأخرى مبنية لنفس architecture/NDK/STL؟ راجع `abiFilters`, packaging options وAAR dependencies. قد يعمل arm64 لكن x86 emulator يفشل لأن vendor SDK لا يقدم x86. لا تستخدم `pickFirst` لتخفي نسختين مختلفتين دون فهم؛ ولا تعلن دعم ABI لا تستطيع اختبارها. تأكد من load order والسيمبولات إذا الملف موجود ولكن loader يرفضه.

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

“I match the loader error and device ABI to the actual delivered APK split, inspect `/lib/<abi>` plus transitive native dependencies, then test every supported architecture.”

## Interview answer — structured

“I capture the full `UnsatisfiedLinkError`, device ABI list and exact release artifact. I use APK Analyzer or bundletool to inspect the split delivered for that ABI, then compare `abiFilters`, vendor AAR contents and dependent `.so` files. If the file exists, I investigate unresolved symbols or incompatible binaries rather than call it missing. I choose a supported SDK build or an explicit ABI policy and add matrix tests; `pickFirst` is not a diagnosis.”

## Interview answer — deep senior

“Native failures are about the binary actually loaded on one device. I start with full loader text, version, device `SUPPORTED_ABIS`, OS and whether installation came from Play splits or a local APK. I inspect the delivered package for `/lib/<abi>/libfoo.so` and its transitive native dependencies. If one is absent, I trace vendor AAR contents, Gradle ABI filters and packaging rules. If the file is present, I look for `dlopen` symbol errors, incompatible STL/NDK build or minimum-platform assumptions. An arm64 success says little about x86_64; App Bundle targeting can distribute different native sets. I do not copy an arm64 binary under an x86_64 directory or use `pickFirst` on duplicate libraries without confirming ABI and version compatibility. The product choice may be to obtain the correct vendor binary, provide a non-native fallback, or intentionally narrow supported devices after reviewing user impact and store policy. CI installs bundle-derived APK sets on the supported ABI matrix and records native startup evidence, while production telemetry is segmented by ABI.”

## Deep-dive talking points

Discuss loader text, ABI selection, split paths, transitive `.so`, symbols, filters and device tests.

## Follow-up questions

- Can an arm64 `.so` work if copied to x86_64 path? **Answer:** no; its machine code ABI is incompatible.
- What if the `.so` exists but load fails? **Answer:** inspect dependent libraries, unresolved symbols and platform compatibility.
- Why inspect AAB-derived splits? **Answer:** Play-targeted packaging may differ from a universal local APK.

## Self-check rubric

Trace one loader error to ABI packaging, distinguish absent file from symbol failure, and define matrix tests.

## References and reviewed-on date

- [Android ABIs](https://developer.android.com/ndk/guides/abis) — native package paths and compatibility.
- [Build and test an App Bundle](https://developer.android.com/guide/app-bundle/test) — split delivery tests.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Vendor ABI availability must be verified separately.
How do you diagnose missing native libraries or ABI incompatibility?

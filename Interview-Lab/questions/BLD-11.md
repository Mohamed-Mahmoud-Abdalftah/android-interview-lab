---
id: "BLD-11"
question: "How do you analyze APK/AAB size and bundled native ABIs?"
topic: "Gradle, AGP, R8, Signing & Release Engineering"
code: "BLD"
group: "B"
phase: 4
priority: "P1"
order: 385
editorial_status: "reviewed"
---

# BLD-11

## Original interview question

How do you analyze APK/AAB size and bundled native ABIs?

## What the interviewer evaluates

- Inspect actual delivered size and artifact contents.
- Identify code/resources/assets/native libraries and ABI targeting.
- Distinguish compressed download, install size and runtime memory.

## Explanation in Arabic

كيف تقوم بتحليل حجم الـ APK والـ AAB وفحص مكتبات الـ Native ABIs المضمنة لتفادي التضخم (App Bloat)؟

1. أدوات تحليل حجم التطبيق:
   - **APK Analyzer المدمج في Android Studio**: أسرع أداة لفحص تشريح الـ APK. يقسم الحجم إلى: `classes.dex`, `res/`, `resources.arsc`, `lib/` (Native Libraries), و `assets/`.
   - **أداة `apkanalyzer` عبر السطر البرمجي**: تتيح فحص الحجم في الـ CI/CD ومقارنة الفروق بين إصدارين (`apkanalyzer apk compare old.apk new.apk`).

2. تضخم مكتبات الـ Native (Native ABI Bloat):
   - مجلد `lib/` يحتوي على ملفات الـ `.so`. إذا تضمن التطبيق معمارية غير مطلوبة، قد يتضاعف حجم التطبيق 3 مرات!
   - المعماريات الشائعة: `arm64-v8a` (معظم الهواتف الحديثة 64-bit)، `armeabi-v7a` (الهواتف القديمة 32-bit)، `x86_64` (المحاكيات وChromebooks).

3. تقنيات تقليص الحجم العملية:
   - **استخدام Android App Bundle (AAB)**: يقسم التطبيق تلقائياً عبر `bundletool` ويرسل للمستخدم معمارية معالجه ولغته فقط.
   - **ضغط الموارد وتنزيلها عند الطلب**: استخدام Play Feature Delivery للميزات الكبيرة، وتحويل الصور إلى صيغ WebP أو Vector Drawables.
   - **حذف الـ ABIs غير الضرورية**: تقييد الـ ABIs في `build.gradle.kts` عبر `ndk.abiFilters`.

## Practical walkthrough

تكوين فلاتر المعالجات (ABI Filters) واستخدام apkanalyzer لمقارنة الحجم في سطر الأوامر:
```kotlin
// في build.gradle.kts: تقييد حزم الـ Native على المعماريات المستهدفة فقط:
android {
    defaultConfig {
        ndk {
            // حصر المكتبات المجمعة على أجهزة الهواتف الحقيقية فقط واستبعاد x86 من الإنتاج:
            abiFilters += listOf("arm64-v8a", "armeabi-v7a")
        }
    }
}
```

```bash
# 1. فحص ملخص حجم مكونات الـ APK عبر السطر البرمجي:
apkanalyzer apk summary app-release.apk

# 2. مقارنة حجم نسختين من الـ APK في CI لاكتشاف الزيادات غير المتوقعة (Size Regressions):
apkanalyzer apk compare --different-only old-release.apk new-release.apk
```

## Why it matters and how it works

An AAB is converted into device-targeted APKs, so its total archive size is not a user's download. Native libraries are typically packaged under ABI-specific paths and may be selected into splits. Compressed transfer size, installed disk footprint and in-memory cost measure different things. An APK Analyzer helps attribute bytes, while bundletool/Play testing verifies delivered combinations.

## Worked example

A camera SDK adds 18 MB of `.so` files across arm64-v8a and x86_64. APK Analyzer shows native bytes dominate the universal build; bundletool shows an arm64 phone receives only its compatible split while an emulator gets x86_64. A missing x86_64 dependency causes emulator launch failure, so removing that ABI from only one transitive library is unsafe.

## Trade-offs and decision criteria

R8 and resource shrinking reduce unused code/resources but require release testing. Asset compression or server delivery may lower download size while increasing first-use latency. Dropping an ABI lowers package scope but excludes devices; decide from actual device support data and SDK compatibility. Dynamic features add installation states.

## Failure modes

Team optimizes total AAB size yet Play download is already small. Duplicate native libraries are hidden in dependencies. One ABI ships a wrapper `.so` but not its transitive native dependency. Baseline compares debug APK with minified release bundle. A resource shrink rule removes dynamically referenced assets.

## Production perspective

Track device-targeted download and install size by release, inspect APK/AAB diff on significant regressions, and test representative ABIs/locales/densities from bundle-derived packages. Tie size changes to user impact and crash data.

## Interview answer — short

Analyze APK/AAB size using Android Studio's APK Analyzer or apkanalyzer CLI to inspect classes.dex, resources, and lib/ native folders. Eliminate bloat by publishing with AABs to deliver split ABIs, converting assets to WebP/Vectors, and configuring ndk.abiFilters to exclude unused architectures.

## Interview answer — structured

Auditing and optimizing binary footprint requires inspecting artifact composition across distinct asset categories.

First, **Binary Composition Breakdown**. Next, with classes.dex, compiled bytecode. Optimized via R8 shrinking, dead code elimination, and method inlining.
Additionally, with lib/` (Native `.so` Binaries), compiled C/C++ libraries. Often constitutes 50–70% of total download size if multiple ABIs are bundled. With res/` & `resources.arsc, images, XMLs, and indexed resource tables. Optimized via resource shrinking, WebP conversion, and vector drawables.
With assets/, uncompressed arbitrary files (fonts, databases, ML models). **Native ABI Optimization**.
When building fat APKs for direct distribution, restrict bundled ABIs using `ndk.abiFilters += listOf("arm64-v8a", "armeabi-v7a")`, stripping unused `x86` and `x86_64` emulators. When distributing via Google Play, publish via **Android App Bundle (AAB)**. Google Play delivers a single architecture split matching the user's phone, slashing native download weight.
**Automated CI Size Budgets**. Finally, integrate `apkanalyzer` or GitHub size-diff actions into CI. Set an alert threshold (e.g., fail PR if download size increases by > 500KB) to prevent accidental bundling of massive third-party assets.


## Interview answer — deep senior

From an advanced mobile performance perspective, download size directly dictates user conversion and uninstall rates.

First, with The Size-to-Install Dropoff Correlation, google Play telemetry demonstrates that every 6MB increase in APK download size correlates with a 1% drop in install conversion rates, particularly across emerging market cellular connections. Next, with Uncompressed Native Libraries (android:extractNativeLibs), setting `android:extractNativeLibs="false"` in the manifest (default in modern AGP) stores `.so` files uncompressed and page-aligned inside the APK. The APK file size increases slightly, but the OS maps libraries directly into memory without extracting them to disk upon install, saving 50MB+ of device storage post-installation.
Finally, with Font & Emoji Bundling Optimization, replace bundled TrueType/OpenType font files (which can add 15MB) with Google Play Services **Downloadable Fonts**, fetching shared system typography at runtime without bundling font files in the APK.


## How to answer in the interview

- **Why:** size and compatibility vary per device.
- **How:** inspect generated splits and native inventory.
- **Trade-off:** smaller download versus supported devices.
- **Failure case:** universal APK hides missing split.
- **Production solution:** profile size and install on ABI matrix.

## Deep-dive talking points

Discuss artifact size metrics, APK Analyzer, bundletool, `.so` paths, ABI support, shrinking and device matrix.

## Follow-up questions

- **Interviewer:** "What is the benefit of android:extractNativeLibs=false?"
  **Answer:** "It page-aligns native libraries inside the APK so the OS executes them directly via mmap without extracting copies to disk, reducing device disk usage."

- **Interviewer:** "How do Vector Drawables reduce APK size compared to PNGs?"
  **Answer:** "A single XML vector scales to all screen densities, replacing five separate rasterized PNG files (mdpi through xxxhdpi)."

## Self-check rubric

Define metric, attribute bytes, inspect two ABIs and verify delivery compatibility.

## References and reviewed-on date

- [Analyze your build with APK Analyzer](https://developer.android.com/studio/build/apk-analyzer) — size inspection.
- [Build and test an App Bundle](https://developer.android.com/guide/app-bundle/test) — device-targeted outputs.

Technically reviewed against primary documentation on 2026-10-13.

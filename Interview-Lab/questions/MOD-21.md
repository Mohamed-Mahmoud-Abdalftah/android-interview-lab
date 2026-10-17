---
id: "MOD-21"
question: "When are dynamic feature modules inappropriate because of offline/runtime constraints?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "C"
phase: 4
priority: "P1"
order: 374
editorial_status: "reviewed"
---

# MOD-21

## Original interview question

When are dynamic feature modules inappropriate because of offline/runtime constraints?

## What the interviewer evaluates

- Assess critical-path availability, latency and offline contract.
- Explain install failure and Play distribution constraints.
- Offer install-time/base alternatives with evidence.

## Concept and technical explanation

While Dynamic Feature Modules (DFMs) effectively shrink initial APK download sizes through Google Play Feature Delivery, they introduce profound operational risks that make them entirely inappropriate in specific mission-critical scenarios:
1. Offline-First and Field Operation Constraints: Applications operating in connectivity-deprived environments (field service, maritime logistics, emergency response, flight management) cannot rely on on-demand downloading; missing features leave users stranded without network fallback.
2. Core Revenue and Critical Funnels: Core revenue journeys (login, user registration, onboarding, primary checkout flows, emergency customer support) must never be dynamic. A transient network timeout, cellular data limit, or Play Store service glitch directly destroys user acquisition and financial conversion.
3. Latency-Sensitive User Experiences: Features requiring immediate responsiveness (real-time camera capture, QR code scanner at a store checkout, instant authentication) degrade user satisfaction if the user must endure a 30-second download progress dialog.
4. Non-Google Play Ecosystems: Devices lacking Google Play Services (Chinese domestic Android stores, Huawei AppGallery, Amazon FireOS, enterprise sideloaded APKs) do not natively support Play Core split installations, requiring complex, fragile multi-APK fallback architectures.
5. Storage and OS Cleanup Risks: On Android Go or low-storage devices, the Android package manager may reclaim storage by clearing split APKs, forcing unexpected redownloads at awkward moments.

## Practical walkthrough (English)

Evaluating dynamic delivery feasibility against operational constraints:
```kotlin
// ❌ DANGEROUS: Putting core onboarding or payment into a Dynamic Feature Module!
// If network drops or Google Play Store fails, user CANNOT register or pay!

// ✅ APPROPRIATE ARCHITECTURAL DECISION:
// Keep Mission-Critical paths inside Base APK:
// - :feature:auth          -> In Base APK (Zero-tolerance for download failures)
// - :feature:checkout      -> In Base APK (Core revenue path must be offline-capable)

// Reserve Dynamic Delivery ONLY for Heavy, Niche, Optional features:
// - :dynamic:ar-viewer     -> 35MB AR Core models, used by < 5% of users.
// - :dynamic:tax-scanner   -> Heavy ML model, used once per year.
```

## Explanation in Arabic

متى تكون موديولات الميزات الديناميكية (Dynamic Feature Modules - DFMs) غير مناسبة وخياراً معمارياً سيئاً بسبب قيود وضع عدم الاتصال وأوقات التشغيل؟

1. الحالات التي يُحظر فيها استخدام Dynamic Feature Modules:
   - **الميزات الأساسية في المسار الحرج (Critical User Journey)**: شاشات تسجيل الدخول (Login), سلة المشتريات (Cart), أو إتمام الدفع (Checkout). لا يجوز أبداً أن يفتح المستخدم التطبيق ليشتري منتجاً فيفاجأ بشاشة 'جارِ تنزيل شاشة الدفع بنسبة 12%'!
   - **التطبيقات التي تتطلب العمل دون اتصال (Offline-First Apps)**: تطبيقات الطوارئ، تطبيقات الميدان والمستودعات، أو تطبيقات السفر والملاحة. إذا كان المستخدم في منطقة بدون شبكة، فلن يستطيع تنزيل الميزة وستتعطل وظيفته بالكامل.
   - **الميزات ذات زمن الانتقال الحرج (Low-Latency SLA)**: إذا كانت الميزة تتطلب استجابة فورية (مثل كاميرا فحص الباركود في السوبرماركت)، فإن انتظار تنزيل 15MB عبر شبكة الجوال يقتل تجربة المستخدم.
   - **التطبيقات الموزعة خارج متجر Google Play**: الـ Dynamic Delivery يعتمد حصرياً على Google Play Core Services. إذا كان تطبيقك يُوزع عبر Huawei AppGallery أو Samsung Galaxy Store أو تثبيت مباشر (Sideloading/Enterprise APKs)، فلن تعمل الـ DFMs على الإطلاق!

2. البديل المعماري الموصى به:
   - استخدم النمطية العادية (Standard Library Modules `com.android.library`) المجمعة في الـ Base APK، واستفد من تقنيات تصغير الحجم مثل R8، وتحويل الصور إلى WebP، وضغط الموارد لتحقيق حجم خفيف دون التضحية بالموثوقية.

## Practical walkthrough

مقارنة متى تستخدم Dynamic Delivery ومتى تعتمد على Standard Modularization:
```text
┌──────────────────────────────────────────────┬──────────────────────────────────┐
│ سيناريو الميزة                              │ الاختيار المعماري الصحيح         │
├──────────────────────────────────────────────┼──────────────────────────────────┤
│ تسجيل الدخول وشاشات المصادقة (Auth)          │ ❌ Base APK (Standard Module)    │
│ إتمام الشراء والدفع (Checkout/Payment)       │ ❌ Base APK (مسار حرج لا يحتمل)  │
│ تطبيق ملاحة ومستودعات يعمل Offline           │ ❌ Base APK (غير متصل بالإنترنت) │
│ توزيع خارج Google Play (Huawei, Enterprise)   │ ❌ Base APK (Google Play غير متاح│
│ وضع واقع معزز ثقيل (50MB AR Viewer)          │ ✅ Dynamic Feature Module (DFM)  │
│ فحص وثائق الهوية نادراً ما يُستخدم (KYC Scan) │ ✅ Dynamic Feature Module (DFM)  │
└──────────────────────────────────────────────┴──────────────────────────────────┘
```

## Why it matters and how it works

On-demand delivery separates feature availability from app installation. Before a successful split install, code and resources cannot be assumed present. Play Feature Delivery relies on supported distribution and installation mechanisms; test environments may package modules differently. An install-time module remains part of initial delivery, so it trades initial bytes for immediate availability.

## Worked example

A transit app shows an already purchased ticket offline at a station. Making ticket display on demand could strand the rider after a fresh install or device restore without network; include the secure ticket viewer and required assets in the initial install. An optional 3D station tour can be on demand with a download prompt, retry and graceful offline fallback.

## Trade-offs and decision criteria

Base/install-time size increases, but reliability of a critical path improves. On-demand reduces initial footprint but adds install UX, telemetry, QA matrix and possible policy/channel limits. A feature can be preinstalled conditionally depending on supported delivery modes, but do not assume it is available for every user until verified.

## Failure modes

The app navigates to a class before the split installs. An offline user cannot view a paid ticket. A test sideloads all splits and falsely concludes on-demand works offline. Install cancellation is not modeled, leaving a broken back stack. A library used by base is moved into a removable feature.

## Production perspective

Write availability requirements per journey, test fresh install/offline/poor network/cancellation and process recreation, and monitor install latency and failure rate. Keep emergency and recovery paths in reliably delivered code.

## Interview answer — short

Dynamic Feature Modules are inappropriate for offline-first applications, core revenue funnels like login and checkout, and latency-critical interactions like payment scanners. They are also unsuitable for apps distributed outside Google Play (such as Amazon FireOS or Huawei AppGallery) and low-end devices where the OS frequently uninstalls split APKs to free up storage.

## Interview answer — structured

While Dynamic Feature Modules optimize initial download sizes, they introduce runtime vulnerabilities that make them unsuitable for critical application workflows.
Dynamic delivery is fundamentally inappropriate for offline-first applications where users operate in environments with spotty or nonexistent internet connectivity.
Similarly, core business funnels such as user onboarding, authentication, checkout, and emergency support must never be placed in dynamic modules.
A single network timeout or Google Play Store error during download prevents users from completing transactions, causing direct revenue loss and customer churn.
Furthermore, dynamic features are impractical for apps distributed across diverse app stores like Huawei AppGallery, Amazon FireOS, or third-party enterprise distribution, as Play Feature Delivery relies strictly on Google Play Services.
High-frequency, latency-sensitive features like QR code scanners should remain in the base APK to eliminate download waiting screens.

## Interview answer — deep senior

In production mobile architecture, Dynamic Feature Modules represent a calculated gamble: trading runtime reliability for initial download size reduction.
When a feature is packaged dynamically, availability ceases to be a deterministic compile-time guarantee and becomes a volatile runtime network dependency subject to cellular coverage, Google Play Core service health, device storage availability, and roaming data limits.
Consequently, deploying dynamic modules across mission-critical workflows is a catastrophic anti-pattern.
First, core revenue paths must remain in the base APK.
Placing registration, login, or checkout into a dynamic module means that an error code from SplitInstallManager directly translates into aborted customer onboarding and lost revenue.
Second, offline-first architectures demand immediate local availability.
Field engineering tools, warehouse scanners, and healthcare emergency apps cannot tolerate an 'Unable to download module, check your internet connection' error dialog when an ambulance technician or remote inspector opens a screen.
Third, distribution platform fragmentation presents a hard technical blocker.
Play Feature Delivery is fundamentally proprietary to Google Play Services.
If your application targets global markets including China, runs on Huawei HMS devices, or distributes via enterprise MDMs, dynamic modules fail to load unless you maintain complex, parallel multi-flavor fallback architectures that package the dynamic modules back into monolithic APKs.
Finally, Android Go and low-end devices introduce storage volatility.
When physical device storage runs low, the Android OS package manager can silently purge unmounted split APKs, forcing a paying user to re-download a previously installed feature unexpectedly.
Senior architects mandate dynamic modules exclusively for heavy, optional, low-frequency capabilities—such as a 30-megabyte augmented reality preview or an annual tax return scanner—while anchoring all core business capabilities firmly inside the immutable base APK.

## How to answer in the interview

- **Why:** runtime availability is a product constraint.
- **How:** classify offline-critical versus optional feature.
- **Trade-off:** initial size versus reliable access.
- **Failure case:** critical payment UI absent offline.
- **Production solution:** choose install-time/base and test failure.

## Deep-dive talking points

Discuss offline contract, split availability, base/install-time alternative, real delivery tests and telemetry.

## Follow-up questions

- **Interviewer:** "Can Dynamic Feature Modules be pre-installed conditionally based on device capabilities?"
  **Answer:** "Yes. Conditional Delivery can install modules during initial app install if the device meets hardware criteria (e.g. has ARCore support), avoiding runtime download friction."

- **Interviewer:** "What error code indicates insufficient storage during dynamic install?"
  **Answer:** "`SplitInstallErrorCode.INSUFFICIENT_STORAGE` (-10), which must be caught to notify the user to free up device space."

## Self-check rubric

Classify one critical and one optional feature, model install failure, and define real distribution tests.

## References and reviewed-on date

- [Play Feature Delivery overview](https://developer.android.com/guide/playcore/feature-delivery) — delivery modes and installation.
- [Android modularization guide](https://developer.android.com/topic/modularization) — module trade-offs.

Technically reviewed against primary documentation on 2026-10-13.

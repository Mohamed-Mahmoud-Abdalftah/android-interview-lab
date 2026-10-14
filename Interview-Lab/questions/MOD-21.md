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

Dynamic Feature Modules are inappropriate for critical paths (login, checkout), offline-first apps, latency-sensitive workflows, and apps distributed outside Google Play. Downloading on-demand introduces network failure points, loading spinners, and dependency on Google Play Services that ruin core app experiences.

## Interview answer — structured

Dynamic Feature Modules (DFMs) solve APK download size constraints, but they introduce severe runtime failure vectors that make them inappropriate for core application functionality.

First, with Critical Path User Journeys, onboarding, Authentication, Catalog browsing, and Checkout must **never** be dynamic features. Requiring a user to wait for a 15MB download before they can log in or swipe their credit card causes catastrophic conversion drops. Next, with Offline-First Architectural Constraints, if an application must operate without active cellular connectivity (e.g., warehouse inventory scanning, field inspections, emergency response), an uninstalled on-demand module is completely unreachable, turning core features into dead buttons.
Finally, with Store Vendor Lock-in, google Play Feature Delivery relies strictly on the Google Play Core library and Play Store client infrastructure. If the app is distributed via sideloading, enterprise MDM, Amazon Appstore, or Huawei AppGallery, dynamic split downloading is unsupported.

Reserve DFMs strictly for non-critical, heavy, infrequently used capabilities (e.g. A 40MB AR furniture previewer or an annual tax calculator). Core capabilities should always be bundled into the base APK using standard Gradle library modules.


## Interview answer — deep senior

When analyzing failure modes for on-demand DFMs in production telemetry.

First, with High Download Drop-off, network metrics reveal that 10% to 25% of on-demand download requests fail due to mobile network handoffs, slow roaming data, or insufficient device disk storage (`ERROR_INSUFFICIENT_STORAGE`). Next, with User Drop-off During Progress Spinners, even when the download succeeds, placing a 10-second download progress bar between a user's tap and screen presentation causes over 30% of users to abandon the funnel.
Finally, with The Architectural Sweet Spot, if module size reduction is the primary goal, senior teams evaluate asset streaming (downloading heavy 3D assets or ML models from a standard CDN to local disk) rather than dynamic code splits. Streaming assets keeps code paths in the base APK with full compile-time type safety while keeping initial download sizes minimal.


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

---
id: SYS-003
title: Mobile auth and session state design
module: 08-Mobile-System-Design
tier: Core
estimated_minutes: 65
prerequisite_ids: [ARC-003, PRO-002, PRO-003]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: not_applicable
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/privacy-and-security/risks/unsafe-use-of-deeplinks
  - https://developer.android.com/privacy-and-security/keystore
  - https://owasp.org/www-project-mobile-application-security/
example_paths: []
question_ids: [SYS-Q011, SYS-Q012, SYS-Q013, SYS-Q014, SYS-Q015]
---

# SYS-003 — Mobile auth and session state design

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">refresh قديمة ترجع بعد logout فتحيي session، أو cache من account A تظهر في B. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">الموبايل يحتفظ session state لكن server هو authority. access token قصيرة، refresh boundary، logout/revocation، account switch، offline UX، وsecure storage كلها state machine. ممنوع client تعتبر claims إذن نهائي لعملية حساسة.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>الموبايل يحتفظ session state لكن server هو authority. access token قصيرة، refresh boundary، logout/revocation، account switch، offline UX، وsecure storage كلها state machine. ممنوع client تعتبر claims إذن نهائي لعملية حساسة.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: refresh قديمة ترجع بعد logout فتحيي session، أو cache من account A تظهر في B.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: اعمل generation/account namespace، single-flight refresh، clear/partition caches، وserver reauthorization لكل resource.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
if (token != null) showAccount()
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> refresh قديمة ترجع بعد logout فتحيي session، أو cache من account A تظهر في B.</p>

```kotlin
when (session) { Active -> loadAuthorized(); else -> clearSensitiveUi() }
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> اعمل generation/account namespace، single-flight refresh، clear/partition caches، وserver reauthorization لكل resource. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">اعمل generation/account namespace، single-flight refresh، clear/partition caches، وserver reauthorization لكل resource. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> Model signed out, authenticating, active, refreshing, and reauthentication-required with explicit transitions.</p>

**English, 20 seconds:** “Model signed out, authenticating, active, refreshing, and reauthentication-required with explicit transitions.”

**English, 60–90 seconds:** “Model signed out, authenticating, active, refreshing, and reauthentication-required with explicit transitions. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: refresh قديمة ترجع بعد logout فتحيي session، أو cache من account A تظهر في B. I would implement this policy: اعمل generation/account namespace، single-flight refresh، clear/partition caches، وserver reauthorization لكل resource. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain Session state machine under a production failure.** Model signed out, authenticating, active, refreshing, and reauthentication-required with explicit transitions.
2. **Explain Refresh race under a production failure.** A refresh result is accepted only for the current account generation and cannot revive a logged-out session.
3. **Explain Secure storage under a production failure.** Keystore protects key material; it does not make arbitrary stored plaintext or server trust unnecessary.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع SYS-Q011 إلى SYS-Q015، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

اكتب test matrix وحدد بوضوح ما يحتاج Android/device evidence.

حلّل [SCN-042](../Real-World-Scenarios/SCN-042-sys-003-mobile-auth-and-session-state-design.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.

---
id: SCN-001
lesson_id: KOT-001
status: reviewed
code_verification: tested
---
# SCN-001 — Profile screen crash after SDK update

**Hypothetical exercise, not a real production incident.** A profile header crashes for a small subset of IDs after a vendor SDK update. The app is a Kotlin/JVM model of an Android integration; no device-specific behavior is asserted. Environment: JDK 17, Kotlin 2.4.20, fake unannotated Java API. A corresponding Android investigation would record app/OS/SDK versions before attributing a root cause.

<p dir="rtl" lang="ar"><strong>ملخص بالمصري:</strong> تخيّل إن شاشة profile بتقع لبعض الـ IDs بعد تحديث vendor SDK. ما ينفعش نقول فورًا إن المشكلة lifecycle أو network. هنفصل الفرضيات بدليل: Java method ممكن ترجع null من غير annotation، وKotlin يسمح بـ <code dir="ltr">.length</code> على platform type. المعمل بيختبر الفرضية دي بـ fake SDK، لكن أي incident حقيقي محتاج logs وإصدارات التطبيق والـ SDK قبل الجزم.</p>

## Symptom and reproducible evidence

The buggy expression `LegacyProfileApi.nameFor(id).length` compiles. In the fake API, `"ada"` returns `" Ada "`, `"blank"` returns spaces, and other IDs return null. Calling the buggy expression with `"missing"` would dereference null. The checked-in correction and [eight JUnit cases](../projects/kotlin-jvm-labs/src/test/kotlin/academy/LabChecksTest.kt) cover missing, blank, and ordinary values; one case executes the unsafe expression inside `assertThrows` and verifies the expected `NullPointerException`. The exact production stack trace and affected device count are **not known**.

## Competing hypotheses and separating evidence

1. **Null from Java SDK:** Capture the return at one boundary, use a controlled fake that returns null, and inspect the crash's top application frame. Expected clue: failure at direct member access.
2. **Blank but non-null data:** Compare raw null versus trimmed blank in a local reproducer. A blank name may show an empty UI but does not itself cause `.length` to dereference null.
3. **UI lifecycle race:** Reproduce with stable input outside Android. If the crash persists in the JVM-only call, lifecycle is not required to explain it; still inspect device evidence before ruling out additional causes.

For a real Android incident, collect a redacted `adb logcat` around the crash, app/version/SDK versions, and a minimal SDK-call reproducer. Avoid logging PII. A `dumpsys activity` snapshot may help establish screen/task state but cannot prove the SDK's null contract. Do not claim an ANR from this evidence.

## Root cause and correction

**High confidence in the fake reproduction:** The unannotated Java return is a Kotlin platform type, which permits a direct call despite possible runtime null. [Kotlin Java interop](https://kotlinlang.org/docs/java-interop.html) documents this behavior (checked 2026-10-10). For a real vendor SDK this remains a hypothesis until logs and contract review confirm it.

<p dir="rtl" lang="ar">بالمصري: السبب هنا واضح <strong>داخل الـ fake</strong> لأننا عارفين الـ Java method بترجع null، وشايفين الـ Kotlin call المباشر. في production ما نساويش ده بتشخيص مؤكد غير لما crash evidence وسلوك الـ SDK الحقيقي يتطابقوا. الإصلاح عند الـ boundary بيخلّي احتمال null ظاهر، وقرار <code dir="ltr">Guest</code> يفضل خاص باسم عرض اختياري.</p>

```kotlin
val raw: String? = LegacyProfileApi.nameFor(id)
val label = ProfileName.parse(raw)?.value ?: "Guest"
```

The [full implementation](../projects/kotlin-jvm-labs/src/main/kotlin/academy/ProfileName.kt) validates at the boundary. The fallback is acceptable only for an optional display label. For a required identity, propagate a typed error instead. The test command and observed output are in [BUILD-VERIFICATION](../BUILD-VERIFICATION.md).

## Tempting wrong fixes

- `nameFor(id)!!` only makes the runtime failure explicit; it does not handle it.
- Catching every `Exception` and showing `Guest` can conceal network, parser, or programmer defects.
- Repeating `nameFor(id)` in the null check and use can read two different values if the API is stateful; capture one result.

## Prevention and rollout

Add fake-SDK contract checks for null, blank, and valid values. In Android integration tests, exercise the relevant vendor SDK version/device combinations when available. Ship a small change behind normal release verification, watch the affected crash signature and profile-load error rate, and roll back if new failures appear. This is a proposed deployment plan, **not an executed rollout**.

## Senior follow-ups

1. **Would a nullability annotation on the Java method solve it?** It improves compile-time mapping if recognized and truthful; it cannot fix a vendor implementation that violates the annotation. Keep a boundary test.
2. **What if the SDK call sometimes throws?** Model that separately from “missing name.” Decide whether to retry, show an error, or use cached data based on product requirements; do not conflate exceptions with null results.

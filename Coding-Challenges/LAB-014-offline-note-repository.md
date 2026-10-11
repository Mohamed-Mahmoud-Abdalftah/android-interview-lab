---
id: LAB-014
lesson_id: ARC-003
status: reviewed
code_verification: tested
---
# LAB-014 — Offline note repository transitions

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> اعمل repository in-memory تجعل local record مصدر القراءة. <code dir="ltr">saveLocal</code> تحفظ draft Pending مع mutation ID. <code dir="ltr">sync</code> تحول accepted إلى Clean، وتترك network failure Pending بنفس ID، وتحول version conflict إلى Conflict مع حفظ local draft وremote evidence. ابدأ بالtests قبل <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/OfflineNotesRepository.kt">reference</a>.</p>

**Acceptance:** [ستة اختبارات](../projects/kotlin-jvm-labs/src/test/kotlin/academy/OfflineNotesRepositoryTest.kt) تغطي visibility، acceptance، retry identity، conflict، second edit، وinvalid input. اشرح أين تحتاج Room transaction وWorkManager في Android.

<p dir="rtl" lang="ar"><strong>حدود المعمل:</strong> الذاكرة تضيع مع process death، والremote synchronous fake. لا تعتبره offline persistence. امتداد مفيد: DAO/outbox حقيقية في transaction، worker يعاد تشغيلها مرتين، وAPI fake تحفظ idempotency result.</p>

**Complexity:** Map access is expected O(1); `all()` copies n records in O(n). Durable storage and indexed queries depend on the actual database. Run `./gradlew clean test check run --no-daemon`.

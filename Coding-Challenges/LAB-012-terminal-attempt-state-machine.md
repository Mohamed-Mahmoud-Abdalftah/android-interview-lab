---
id: LAB-012
lesson_id: EXT-POS-01
status: reviewed
code_verification: tested
---
# LAB-012 — Payment terminal attempt state machine

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> مثّل <code dir="ltr">Idle</code> و<code dir="ltr">AwaitingTap</code> و<code dir="ltr">Authorizing</code> وoutcomes <code dir="ltr">Approved/Declined/Unknown</code>. اربط كل event بـ attempt ID، استخدم مبلغ minor units موجب، لا تخزن token في state، امنع محاولة جديدة أثناء progress، ولا تسمح لنتيجة متأخرة تغير outcome نهائية. اكتب tests قبل <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/TerminalAttempt.kt">reference</a>.</p>

**Acceptance:** [Seven tests](../projects/kotlin-jvm-labs/src/test/kotlin/academy/TerminalAttemptTest.kt) تغطي البداية، card event، stale/blank input، approved/declined، unknown transport، ومنع overlap. أضف test لprocess restart في adapter أعلى وprovider fake مع idempotency.

<p dir="rtl" lang="ar"><strong>حدود المعمل:</strong> reducer لا تنفذ EMV أو NFC ولا authorization. token مجرد إشارة مبهمة ولا تُحفظ. اشرح كيف تربط hardware callback وbackend result بالحالة من غير ما UI تصبح مصدر الحقيقة.</p>

**Complexity:** Each transition is O(1) time and space for bounded identifiers; external reconciliation complexity is outside this reducer. Run `./gradlew clean test check run --no-daemon` and inspect [BUILD-VERIFICATION](../BUILD-VERIFICATION.md).

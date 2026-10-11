---
id: LAB-010
lesson_id: ARC-002
status: reviewed
code_verification: tested
---
# LAB-010 — Editor state and stale completion

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> ابني pure reducer لـ editor فيها draft title وpending وmessage وrequest identity. <code dir="ltr">SaveTapped</code> ترفض blank title، تمنع double tap وقت pending، وتبدأ request جديدة للعنوان الصالح. <code dir="ltr">TitleChanged</code> تغير draft وتمسح رسالة قديمة. نتيجة حفظ تطابق الطلب الحالي فقط. حاول الحل قبل <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/EditorReducer.kt">reference</a>.</p>

**Acceptance cases:** [Six JUnit tests](../projects/kotlin-jvm-labs/src/test/kotlin/academy/EditorReducerTest.kt) cover blank input, valid pending state, success/acknowledgment, repeated tap, edit/failure, and late success for an old request. Extend the exercise with late failure after a newer success and a repository fake holding title snapshots.

<p dir="rtl" lang="ar"><strong>ربط Android لاحقًا:</strong> ViewModel تملك state وoperation، وتستخدم structured coroutine scope؛ UI تجمع state مع lifecycle وترسمها. بعد العملية ابعت completion بالـ ID الذي صدر عند البداية. reducer هنا لا تشغّل I/O ولا تعالج process death أو cancellation؛ اكتب integration tests لها بدل اعتبار unit tests كافية.</p>

**Complexity:** Each reducer transition uses constant additional space and constant work apart from string blank checking, which scans up to title length. Request ID handling is illustrative and needs a production overflow/lifetime policy.

**Verification:** Run `./gradlew clean test check run --no-daemon` in `projects/kotlin-jvm-labs`. Optional rubric (10): validation 2, pending/double tap 2, matching completion 2, stale completion 2, Android integration limits 2. [Scenario](../Real-World-Scenarios/SCN-011-stale-editor-save-result.md).

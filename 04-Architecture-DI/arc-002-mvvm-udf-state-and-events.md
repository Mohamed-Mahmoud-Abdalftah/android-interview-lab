---
id: ARC-002
title: MVVM, UDF, state and events
module: 04-Architecture-DI
tier: Core
estimated_minutes: 55
prerequisite_ids: [AND-001]
learning_outcomes:
  - Trace a user action through a state holder to an observable UI state
  - Distinguish durable screen state from a transient notification request
  - Prevent a stale asynchronous result from overwriting a newer edit
  - State what a pure reducer test cannot establish about Android lifecycle and persistence
status: reviewed
code_verification: tested
last_source_checked: 2026-10-10
source_urls:
  - https://developer.android.com/topic/architecture/ui-layer
  - https://developer.android.com/topic/architecture/ui-layer/stateholders
  - https://developer.android.com/topic/architecture/ui-layer/events
  - https://developer.android.com/topic/architecture/recommendations
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/EditorReducer.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/EditorReducerTest.kt
question_ids: [ARC-Q006, ARC-Q007, ARC-Q008, ARC-Q009, ARC-Q010]
---

# ARC-002 — MVVM, UDF, state and events

**Starting point:** [AND-001](../03-Android-Internals/and-001-activity-fragment-and-view-lifecycle.md) distinguished a Fragment from its shorter lived view. This lesson adds a state holder and a one way event/state trace. **Two-hour route:** 55 minutes here, 20 minutes on [five complete answers](../Interview-Question-Bank/BY-TOPIC.md), 25 minutes on [LAB-010](../Coding-Challenges/LAB-010-editor-state-reducer.md), 10 minutes [revision](../Flashcards-Revision/ARC-002.md), optional 10 minutes [spoken practice](../Speaking-Shadowing/DAY-20.md).

## Mental model

<p dir="rtl" lang="ar">في MVVM، الشاشة تقرأ حالة جاهزة للرسم وتبعت فعل المستخدم إلى state holder زي ViewModel. اتجاه المعلومات واضح: المستخدم يعمل action، الـ holder يحدث UI state، والواجهة ترسم آخر state. ده معنى عملي لـ UDF، مش إن كل click لازم يتخزن للأبد. Android بتوصي بـ ViewModel على مستوى الشاشة، immutable UI state، وتجميع الحالة بشكل واعٍ للـ lifecycle. راجع <a dir="ltr" href="https://developer.android.com/topic/architecture/ui-layer">UI layer guide</a> و<a dir="ltr" href="https://developer.android.com/topic/architecture/recommendations">architecture recommendations</a>، اتراجعوا 2026-10-10.</p>

<p dir="rtl" lang="ar">فرّق بين <strong>حالة</strong> ممكن الشاشة تعيد رسمها، زي title وloading وerror، وبين <strong>طلب تأثير</strong> زي فتح شاشة أو إظهار snackbar. رسالة نجاح يمكن تمثيلها في state مع acknowledgment واضح لو مهم إنها ما تضيعش عند إعادة collection؛ لكن قرار إعادة عرضها بعد rotation/process death منتج لازم يتحدد. Android event guide يشرح إن ViewModel تعالج events وتحدّث state، والـ UI هي التي تنفذ navigation عندما تكون مناسبة. <a dir="ltr" href="https://developer.android.com/topic/architecture/ui-layer/events">Events guide</a>.</p>

## Mechanism and execution trace

<p dir="rtl" lang="ar">معمل JVM فيه <code dir="ltr">EditorUiState</code> immutable و<code dir="ltr">EditorEvent</code> و<code dir="ltr">reduceEditor</code> pure function. هي لا تحفظ note؛ <code dir="ltr">SaveTapped</code> تنقل الحالة إلى pending وتزيد <code dir="ltr">requestId</code>. الـ owner الخارجي، لو اتبنى في Android، يأخذ الطلب ويبدأ repository operation، ثم يرجع completion بنفس ID. لو المستخدم عدّل title وبدأ طلبًا أحدث، رد الطلب القديم لا يغيّر الحالة. اقرأ <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/EditorReducer.kt">التنفيذ</a> و<a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/EditorReducerTest.kt">الاختبارات</a>.</p>

<table dir="rtl" lang="ar"><thead><tr><th>حدث</th><th>قبل</th><th>بعد</th></tr></thead><tbody>
<tr><td dir="ltr"><code dir="ltr">SaveTapped</code></td><td>title فاضي</td><td>رسالة validation؛ لا pending.</td></tr>
<tr><td dir="ltr"><code dir="ltr">SaveTapped</code></td><td>title صالح وidle</td><td>pending ورقم طلب جديد؛ لا ادعاء نجاح.</td></tr>
<tr><td dir="ltr"><code dir="ltr">TitleChanged</code></td><td>طلب قديم pending</td><td>draft جديد، pending false، الرسالة تُمسح؛ العملية الخارجية قد تظل تعمل.</td></tr>
<tr><td dir="ltr"><code dir="ltr">SaveSucceeded(oldId)</code></td><td>طلب أحدث pending</td><td>تجاهل النتيجة القديمة بالكامل.</td></tr>
<tr><td dir="ltr"><code dir="ltr">SaveFailed(currentId)</code></td><td>الطلب الحالي pending</td><td>توقف pending واعرض فشل قابل للرسم.</td></tr>
</tbody></table>

## Wrong and corrected implementation

<p dir="rtl" lang="ar"><strong>النمط الخاطئ:</strong> callback قديمة تنادي <code dir="ltr">showToast("Saved")</code> مباشرة بعد ما المستخدم غيّر draft، أو قناة حدث one-shot بلا سياسة replay/acknowledgment تضيع رسالة مهمة عند توقف collector. كمان <code dir="ltr">isSaving</code> وحدها لا تميز طلب قديم من طلب جديد. غياب generation check يجعل completion القديمة تلوّث حالة أحدث.</p>

```kotlin
// Conceptual anti-pattern: stale completion can overwrite newer screen work.
fun onSaveFinished() { state = state.copy(isSaving = false, message = "Saved") }
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> owner يربط كل operation بـ <code dir="ltr">requestId</code> صادر من state، وينشر completion بهذا الرقم، وreducer تقبل النتيجة فقط لو هي الطلب الحالي وهو pending. عند تغيير title تلغي صلاحية النتيجة القديمة بالنسبة للـ UI. في production، الإلغاء الفعلي للعمل الخارجي، idempotency للتخزين، وتحديد هل المستخدم يقدر يحفظ نسختين مسؤوليات منفصلة؛ تجاهل completion في UI لا يمسح كتابة تمت بالفعل. لو مطلوب حفظ snapshot ثابت، خزّن النص/ID المرتبطين بالطلب عند البدء بدل قراءة draft متغيرة لاحقًا.</p>

## Alternatives and trade-offs

<p dir="rtl" lang="ar">ممكن ViewModel تستعمل <code dir="ltr">StateFlow</code> مع data class للحالة وتتعامل مع intents في methods، بدون reducer منفصلة. reducer مفيدة لما transitions كثيرة ونحتاج test deterministic. لو رسالة النجاح مهمة بعد إعادة إنشاء view، خزنها كجزء من state مع consume/acknowledge؛ لو لا، حدد سياسة عدم الإعادة صراحة. Channel أو SharedFlow يحتاجوا ضبط buffer/replay والcollector lifecycle؛ ما فيش اختيار universal. <a dir="ltr" href="https://developer.android.com/topic/architecture/ui-layer/stateholders">State holders</a> و<a dir="ltr" href="https://developer.android.com/topic/architecture/ui-layer/events">events</a>.</p>

<p dir="rtl" lang="ar">الـ <code dir="ltr">requestId</code> التعليمي هنا <code dir="ltr">Int</code> محلي للحالة؛ في تطبيق طويل العمر أو عمليات متزامنة كثيرة اختَر معرفًا يراعي overflow وإعادة إنشاء العملية، ولا تستخدمه كمعرف durable للكتابة عبر process death. إدارة العملية نفسها ونتيجة repository تحتاج integration test. Unidirectional flow لا تمنع race وحدها؛ identity والownership للطلبات لازمين.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">ستة JUnit tests تغطي validation، بداية الطلب، success/acknowledgment، تكرار tap أثناء pending، تعديل draft ثم failure مرئي، وcompletion قديمة بعد حفظ أحدث. الاختبارات تثبت transitions لدالة JVM فقط. لا يوجد Android SDK أو <code dir="ltr">ViewModel</code> فعلية أو <code dir="ltr">StateFlow</code> collector أو lifecycle test أو repository persistence في هذا المعمل. شغّل <code dir="ltr">./gradlew clean test check run --no-daemon</code> وراجع <a dir="ltr" href="../BUILD-VERIFICATION.md">evidence</a>.</p>

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> الشاشة تبعت event والـ ViewModel تمسك state قابلة للرسم. لما المستخدم يحفظ، أظهر pending، وأربط نتيجة الطلب برقم. لو كتب title جديدة وجاء رد قديم، ما أقولش Saved للنسخة الجديدة. الـ reducer اختبرتها JVM، لكن اختبار lifecycle وrepository يحتاج Android/integration.</p>

**English, about 20 seconds:** “I model the editor as immutable UI state. User actions update the state through a state holder. Each save has an identity, so a stale completion cannot report success for a newer draft.”

**English, about 60–90 seconds:** “With MVVM and unidirectional data flow, the UI renders state and sends actions; the state holder coordinates work and emits a new state. The save state includes a request identity. A title edit invalidates the old UI request, and only a completion matching the current pending request can display success or failure. That protects the screen from a stale callback, but it does not cancel a database write or prove the right record was persisted. I would test the reducer separately, then test the ViewModel collection and persistence contract with the real Android and data dependencies.”

## Senior follow-ups

<ol dir="rtl" lang="ar"><li><strong>هل تجاهل رد قديم يلغي الكتابة؟</strong> لأ؛ ممكن operation تكون خلصت. لازم تحدد cancel/idempotency أو reconcile من source of truth.</li><li><strong>هل كل effect لازم state؟</strong> لأ؛ حدد lifetime وإعادة العرض المطلوبة. رسالة مهمّة بعد rotation تحتاج acknowledgment أو state مناسبة، navigation قرار UI.</li><li><strong>متى reducer منفصلة زيادة؟</strong> لما الحالة صغيرة جدًا وانتقالات واضحة داخل ViewModel؛ افصلها عندما التعقيد أو الاختبار يكسبوا من ذلك.</li></ol>

## Misconceptions and revision

<ul dir="rtl" lang="ar"><li>“UDF يمنع كل race.” غلط؛ اتبع هوية الطلب وملكية العملية.</li><li>“رسالة Saved تثبت التخزين.” غلط؛ UI state لا تثبت durability.</li><li>“One-shot event لا تضيع أبدًا.” غلط؛ توقف collector وإعادة الإنشاء يغيران delivery.</li><li>“ViewModel تبقى طول عمر التطبيق.” غلط؛ lifetime مربوط بالـ owner وprocess death ينهيها.</li></ul>

<p dir="rtl" lang="ar"><strong>راجع نفسك:</strong> اشرح لماذا success قديم لا يُقبل، ماذا يحدث للكتابة القديمة، وكيف ستختبر rotation وprocess death. بعدين حل <a dir="ltr" href="../Real-World-Scenarios/SCN-011-stale-editor-save-result.md">SCN-011</a>.</p>

**Evidence limit:** Official Android guidance checked 2026-10-10; only a pure JVM transition model was built/tested. No Android UI, ViewModel, Flow collection, persistence, lifecycle, or device behavior is claimed.

---
id: EXT-POS-01
title: POS/NFC
module: 10-Optional-POS-Specialist
tier: Specialist
estimated_minutes: 70
prerequisite_ids: [PRO-003]
learning_outcomes:
  - Separate NFC transport, card protocol, authorization and settlement responsibilities
  - Model a payment attempt with explicit terminal and unknown outcomes
  - Explain why a transport timeout must not trigger a blind payment retry
  - Bound JVM state-machine evidence against hardware, scheme and certification evidence
status: reviewed
code_verification: tested
last_source_checked: 2026-10-10
source_urls:
  - https://developer.android.com/develop/connectivity/nfc
  - https://developer.android.com/reference/android/nfc/NfcAdapter
  - https://developer.android.com/develop/connectivity/nfc/hce
  - https://www.emvco.com/wp-content/uploads/2022/09/EMV%C2%AE-Chip-At-A-Glance-EMVCo-eBook.pdf
  - https://www.emvco.com/wp-content/uploads/2023/06/EMVCo_QRG_EMV-CONTACTLESS_FINAL.pdf
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/TerminalAttempt.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/TerminalAttemptTest.kt
question_ids: [POS-Q001, POS-Q002, POS-Q003, POS-Q004, POS-Q005, POS-Q006, POS-Q007, POS-Q008, POS-Q009, POS-Q010]
---

# EXT-POS-01 — POS/NFC

ده درس specialist خارج الـ 48 يوم الأساسية. ابدأ بـ [PRO-003](../06-Production-Engineering/pro-003-security-and-threat-modeling.md)، لأن payment flow محتاجة threat boundaries وidempotency قبل hardware APIs. **مسار مقترح:** 70 دقيقة شرح وتتبع، 20 دقيقة أسئلة، 25 دقيقة [LAB-012](../Coding-Challenges/LAB-012-terminal-attempt-state-machine.md)، و15 دقيقة [SCN-013](../Real-World-Scenarios/SCN-013-unknown-payment-outcome.md) والمراجعة.

## Mental model — طبقات العملية مش API واحدة

<p dir="rtl" lang="ar">NFC وسيلة اتصال قصيرة المدى، مش مرادف للدفع ومش ضمان نجاح. Android يفرق بين reader/writer mode، حيث الجهاز يقرأ tag، وcard emulation mode، حيث الجهاز يتصرف ككارت أمام reader. فوق الاتصال فيه protocol ورسائل، وبعدها terminal/kernel/provider، ثم authorization من جهة مالية، وبعدها capture/settlement/reconciliation. لما interview تسألك عن POS، افصل الطبقات دي قبل ما تقول <code dir="ltr">NfcAdapter</code>.</p>

<p dir="rtl" lang="ar">في Android، <code dir="ltr">enableReaderMode</code> تربط القراءة بـ Activity في foreground وتختار technologies/flags. HCE تستخدم <code dir="ltr">HostApduService</code> وAID routing عشان Android يوجه APDUs للservice المناسبة. ده لا يعني إن أي HCE app بقت payment wallet معتمدة؛ payment schemes، keys، secure element/tokenization، kernel requirements، vendor SDK، PCI والاعتمادات خارج نطاق API العامة. راجع <a dir="ltr" href="https://developer.android.com/develop/connectivity/nfc">Android NFC overview</a> و<a dir="ltr" href="https://developer.android.com/develop/connectivity/nfc/hce">HCE guide</a>، اتراجعوا 2026-10-10.</p>

<table dir="rtl" lang="ar"><thead><tr><th>طبقة</th><th>مسؤوليتها</th><th>مثال فشل</th></tr></thead><tbody>
<tr><td>NFC transport</td><td>اكتشاف tag وتبادل bytes.</td><td>الكارت اتشال أو link انقطعت.</td></tr>
<tr><td>Protocol/kernel</td><td>ترتيب الرسائل والتحقق من outcome.</td><td>APDU غير متوقعة أو timeout.</td></tr>
<tr><td>Authorization</td><td>قرار approve/decline من authority.</td><td>issuer لا يرد أو يرفض.</td></tr>
<tr><td>Application state</td><td>تعرض حالة المحاولة وتمنع duplicate action.</td><td>UI تقول Declined رغم إن الطلب اتقبل.</td></tr>
<tr><td>Reconciliation</td><td>تحسم الحالات غير المعروفة من provider/source of truth.</td><td>network ضاعت بعد الإرسال وقبل الرد.</td></tr>
</tbody></table>

## Mechanism and execution trace

<p dir="rtl" lang="ar">المعمل يعمل state machine تعليمية: <code dir="ltr">Idle → AwaitingTap → Authorizing → Approved/Declined/Unknown</code>. كل محاولة معها <code dir="ltr">attemptId</code> ومبلغ بوحدة صغرى مثل القرش/cent كعدد صحيح؛ ما تستخدمش floating point للفلوس. لما token مبهمة توصل للمحاولة الصحيحة، الحالة تدخل Authorizing من غير تخزين card data في state. provider result لازم تحمل نفس attempt ID. أي event قديمة أو terminal outcome متأخرة تتجاهل.</p>

```text
Idle --Start(a1, 1250)--> AwaitingTap(a1)
AwaitingTap(a1) --CardRead(a1, opaque)--> Authorizing(a1)
Authorizing(a1) --Approved(a1, receipt)--> Approved(a1)
Authorizing(a1) --TransportLost(a1)--> Unknown(a1)
```

<p dir="rtl" lang="ar">الحالة <code dir="ltr">Unknown</code> أساسية: معناها التطبيق لا يعرف outcome النهائية. لو network انقطعت بعد إرسال authorization، تحويلها تلقائيًا إلى Declined كذب، وإعادة الدفع تلقائيًا قد تعمل duplicate charge. الحل يوقف محاولة جديدة لنفس intent التجاري، ويحفظ correlation آمنة، ويسأل provider/backend عن الحالة أو يبدأ reversal حسب العقد. اقرأ <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/TerminalAttempt.kt">state machine</a> و<a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/TerminalAttemptTest.kt">JUnit tests</a>.</p>

<p dir="rtl" lang="ar">EMV Chip specifications تصف تبادل المعلومات بين chip والterminal لتنفيذ transaction، وcontactless مجرد interface أسرع للمستخدم. التفاصيل الكاملة والاختبارات المعتمدة تتبع EMVCo وشبكات الدفع ومزود terminal. الدرس لا يعيد تنفيذ EMV kernel ولا APDUs دفع حقيقية؛ بيعلّم ownership للحالة والفشل. راجع <a dir="ltr" href="https://www.emvco.com/wp-content/uploads/2022/09/EMV%C2%AE-Chip-At-A-Glance-EMVCo-eBook.pdf">EMV Chip overview</a>.</p>

## Wrong and corrected implementation

<p dir="rtl" lang="ar"><strong>غلط:</strong> callback اسمها <code dir="ltr">onNfcRead</code> تعتبر القراءة نجاح، أو timeout تعمل retry بنفسها، أو UI تخزن PAN/token خام في state/log. قراءة الكارت تعني إن transport جابت data، مش إن issuer وافقت. والtimeout معناها النتيجة غير معروفة، إلا لو protocol/provider يضمن إن الطلب لم يصل.</p>

```kotlin
fun onNfcRead(cardBytes: ByteArray) {
    showApproved()              // No authorization evidence.
    analytics.log(cardBytes)    // Sensitive data leak.
}

fun onTimeout() = authorizeAgain() // Possible duplicate charge.
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> حوّل hardware callbacks إلى events صغيرة لا تحمل بيانات حساسة بعد tokenization، اربطها بمحاولة واحدة، واجعل terminal outcomes نهائية. عند ambiguity استخدم Unknown ثم reconciliation. أي retry مالي يستخدم idempotency key واتفاق provider، مش مجرد coroutine retry. افصل hardware adapter عن reducer عشان تقدر تختبر transitions من غير جهاز، وبعدها اختبر adapter على hardware حقيقي ومصفوفة أجهزة.</p>

## Hardware lifecycle and operational design

<p dir="rtl" lang="ar">لو التطبيق قارئ NFC، reader mode مربوطة بـ Activity foreground؛ فعّلها واقفلها مع lifecycle المناسب، وتعامل مع غياب FEATURE_NFC، adapter مقفولة، tag اتشالت، وdevice variations. ما تحاولش تشغل NFC programmatically لتطبيق عادي؛ صلاحيات وسلوك APIs تختلف حسب الإصدار والدور. <a dir="ltr" href="https://developer.android.com/reference/android/nfc/NfcAdapter">NfcAdapter reference</a> توثق إن reader mode تحد الجهاز للقارئ أثناء الـ Activity.</p>

<p dir="rtl" lang="ar">في HCE، النظام يوجه APDU حسب AID للـ service. <code dir="ltr">processCommandApdu</code> ليست مكان network بطيئة بلا تصميم؛ زمن التبادل وتجربة tap محدودين. <code dir="ltr">onDeactivated</code> معناه link اتكسرت أو AID أخرى اتحددت، وليس بالضرورة decline. ما تعرضش تفاصيل protocol أو card data في logs. افصل telemetry التشغيلية عن البيانات الحساسة، وراجع lock-screen وSecure NFC وdevice behavior قبل claim دعم.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">سبعة اختبارات JVM بدأت بفشل compile ثم نجحت: مبلغ موجب وهوية محاولة، CardRead مطابقة، رفض event قديمة أو token فارغة، outcome واحدة نهائية، decline صريحة، transport loss إلى Unknown، ومنع Start جديدة وهي في progress. الاختبارات تثبت reducer فقط. لا تختبر NFC radio، APDU bytes، kernel، provider SDK، encryption keys، terminal certification، receipts، offline approval، reversal أو settlement.</p>

<p dir="rtl" lang="ar">خطة تحقق حقيقية تشمل: fake hardware adapter deterministic، instrumented tests للـ lifecycle/permissions، hardware-in-loop على أجهزة معتمدة، provider sandbox بحالات approve/decline/timeout/duplicate، واختبار reconciliation بعد process death وانقطاع الشبكة. اعمل trace بـ attempt ID غير حساس من Start لحد backend outcome، وحدد SLO للحالات Unknown ومَن يصعّدها تشغيليًا.</p>

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> بفصل NFC transport عن authorization. قراءة tag تبدأ العملية لكنها مش نجاح دفع. كل محاولة لها ID ومبلغ integer، والـ state machine تسمح outcome نهائية واحدة. لو الاتصال ضاع بعد إرسال الطلب، أحط Unknown بدل Declined أو retry أعمى، وبعدها reconcile من provider باستخدام idempotency. unit tests تثبت transitions، والهاردوير والشهادات محتاجين test lab منفصلة.</p>

**English, 20 seconds:** “NFC is transport, not payment authority. I model one identified attempt with explicit approved, declined, and unknown outcomes, and I reconcile ambiguity instead of blindly retrying.”

**English, 60–90 seconds:** “I separate the radio and protocol layers from authorization and settlement. A card read moves an identified attempt into authorization without storing sensitive card data in UI state. Only a matching provider result can create a terminal outcome. If transport is lost after submission, the state is unknown because the payment may already have been authorized. I use idempotency and provider reconciliation before allowing another charge. The JVM reducer proves transition rules; hardware-in-loop, provider sandbox, security, and certification evidence are separate release gates.”

## Senior follow-ups

<ol dir="rtl" lang="ar"><li><strong>ليه timeout مش decline؟</strong> لأن عدم وصول الرد لا يثبت عدم تنفيذ الطلب؛ النتيجة epistemically unknown.</li><li><strong>إزاي تمنع duplicate charge؟</strong> business attempt ID/idempotency end-to-end، state transition واحدة، وreconciliation قبل retry.</li><li><strong>هل نخزن PAN في logs عشان debugging؟</strong> لأ؛ قلل البيانات واستخدم identifiers غير حساسة وسياسات provider/compliance.</li><li><strong>فرق HCE وreader mode؟</strong> HCE تجعل الجهاز card endpoint للreader؛ reader mode تجعل الجهاز يقرأ tag/card حسب protocol مدعوم.</li><li><strong>هل unit state machine كفاية لشهادة دفع؟</strong> إطلاقًا؛ certification وhardware/provider tests وعقود scheme مستقلة.</li></ol>

## Misconceptions and revision

<ul dir="rtl" lang="ar"><li>“NFC read = paid.” غلط؛ دي خطوة transport.</li><li>“Timeout = declined.” غلط؛ قد تكون النتيجة Unknown.</li><li>“Retry الشبكة آمن تلقائيًا.” غلط في العمليات المالية من غير idempotency.</li><li>“HCE API تكفي لبناء wallet دفع.” غلط؛ protocol، provisioning، keys، scheme واعتماد مطلوبة.</li><li>“المبلغ Double مناسب.” غلط؛ استخدم minor units integer وعملة واضحة.</li></ul>

**Evidence limit:** Seven pure Kotlin state-transition tests ran. No Android NFC APIs, APDUs, payment cards, reader hardware, provider SDK, certification, key material, authorization, capture, reversal, settlement, or reconciliation service ran here.

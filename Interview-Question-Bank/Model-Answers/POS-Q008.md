---
id: POS-Q008-ANSWER
question_id: POS-Q008
status: reviewed
---
# POS-Q008 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Every attempt has stable identity across UI, SDK, host, retry, receipt, and recovery.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> payment attempt لها stable ID وterminal outcome واحدة؛ authorization/settlement/reversal سجلات مختلفة، وunknown لا تصبح retry جديدة قبل reconciliation.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Design a payment attempt ID that survives process death, duplicate callbacks, reconnects, and retries across app, terminal SDK, backend, and provider.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Terminal operation identity:</strong> payment attempt تبدأ بـstable operation ID وتتحرك بين states واضحة. authorization response المفقودة تعني Unknown لاDeclined؛ settlement وreversal مراحل ledger مختلفة. callback لا تُقبل إلا لو attempt ID تطابق الحالية، والdiagnostics لا تخزن card secrets.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـTerminal operation identity: persist attempt identity والحالة قبل SDK call، طابق كل callback، reconcile مع host بعد disconnect، ونفذ reversal حسب protocol من غير تخزين card secrets.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “A lost response means the payment failed, so create a new attempt immediately.”

<p dir="rtl" lang="ar">في <strong>Terminal operation identity</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: payment attempt لها stable ID وterminal outcome واحدة؛ authorization/settlement/reversal سجلات مختلفة، وunknown لا تصبح retry جديدة قبل reconciliation. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Terminal operation identity: manual operator reconciliation لازمة لو host لا يوفر status/idempotency؛ UI undo لا تعادل protocol reversal.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Terminal operation identity: اقطع hardware/network قبل وبعد authorization، كرر callback وأعد process، واثبت outcome واحدة وreceipt صحيحة وlogs خالية من PAN/track/PIN/cryptogram.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Terminal operation identity، الـshortcut هي: <bdi dir="ltr">A lost response means the payment failed, so create a new attempt immediately.</bdi> ودي تكسر: payment attempt لها stable ID وterminal outcome واحدة؛ authorization/settlement/reversal سجلات مختلفة، وunknown لا تصبح retry جديدة قبل reconciliation.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Terminal operation identity: اقطع hardware/network قبل وبعد authorization، كرر callback وأعد process، واثبت outcome واحدة وreceipt صحيحة وlogs خالية من PAN/track/PIN/cryptogram.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Terminal operation identity: manual operator reconciliation لازمة لو host لا يوفر status/idempotency؛ UI undo لا تعادل protocol reversal.</span>

## English model answer

“Every attempt has stable identity across UI, SDK, host, retry, receipt, and recovery. I would keep one stable payment-attempt identity across the terminal and host, model unknown outcomes explicitly, and reconcile before any retry that could create a second charge. I would simulate disconnects and duplicate callbacks, then reconcile by the original attempt identity while keeping diagnostics PCI-safe.”

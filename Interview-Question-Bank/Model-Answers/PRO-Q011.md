---
id: PRO-Q011-ANSWER
question_id: PRO-Q011
status: reviewed
---
# PRO-Q011 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Connect, read, call, and application deadlines have different meanings and ownership.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> اسم timeout وحده لا يحدد هل الاتصال بدأ، هل request bytes خرجت، هل response بدأت، أو هل server commit حصل؛ كل deadline لها stage وowner ودليل مختلف.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">An API call reports a timeout. Distinguish connect, read, call, and application deadlines. For each one, state what you know about whether the server executed the request.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Timeout taxonomy:</strong> اسم timeout وحده لا يحدد هل الاتصال بدأ، هل request bytes خرجت، هل response بدأت، أو هل server commit حصل؛ كل deadline لها stage وowner ودليل مختلف. سجّل connect/read/write/call/application deadline منفصلة، اربطها بـoperation ID، واعمل retry فقط لما operation آمنة أو idempotent؛ write ذات outcome مجهولة تنتقل لـstatus lookup أوreconciliation.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـTimeout taxonomy: سجّل connect/read/write/call/application deadline منفصلة، اربطها بـoperation ID، واعمل retry فقط لما operation آمنة أو idempotent؛ write ذات outcome مجهولة تنتقل لـstatus lookup أوreconciliation.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “A timeout proves that the server did not execute the request.”

<p dir="rtl" lang="ar">في <strong>Timeout taxonomy</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: اسم timeout وحده لا يحدد هل الاتصال بدأ، هل request bytes خرجت، هل response بدأت، أو هل server commit حصل؛ كل deadline لها stage وowner ودليل مختلف. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Timeout taxonomy: deadline واحدة end-to-end أبسط للcaller، لكن احتفظ بسبب داخلي يسمح بالتشخيص وسياسة retry الصحيحة.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Timeout taxonomy: اقطع الاتصال قبل connect، أثناء request body، بعد server commit وقبل response، وأثناء response body؛ تحقق من classification ومن عدم تكرار side effect.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Timeout taxonomy، الـshortcut هي: <bdi dir="ltr">A timeout proves that the server did not execute the request.</bdi> ودي تكسر: اسم timeout وحده لا يحدد هل الاتصال بدأ، هل request bytes خرجت، هل response بدأت، أو هل server commit حصل؛ كل deadline لها stage وowner ودليل مختلف.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Timeout taxonomy: اقطع الاتصال قبل connect، أثناء request body، بعد server commit وقبل response، وأثناء response body؛ تحقق من classification ومن عدم تكرار side effect.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Timeout taxonomy: deadline واحدة end-to-end أبسط للcaller، لكن احتفظ بسبب داخلي يسمح بالتشخيص وسياسة retry الصحيحة.</span>

## English model answer

“Connect, read, call, and application deadlines have different meanings and ownership. I would classify the failure, correlate it with the exact release and cohort, protect irreversible side effects, and define rollout and rollback evidence before changing production behavior. I would use a release-like build, comparable cohorts and percentiles, failure injection, and a predefined rollback threshold.”

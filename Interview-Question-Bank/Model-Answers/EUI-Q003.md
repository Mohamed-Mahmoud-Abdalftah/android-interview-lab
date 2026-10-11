---
id: EUI-Q003-ANSWER
question_id: EUI-Q003
status: reviewed
---
# EUI-Q003 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Stable means observable public behavior will not change unexpectedly; false annotations can hide updates.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الـUI تحافظ على state identity وsemantics/focus، وكل optimization تُنسب للمرحلة المقاسة: composition أو layout أو draw أو input أو GPU.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">What does Compose stability allow the runtime to skip, and why does stable never mean immutable, thread-safe, or cheap to render?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Stability contract:</strong> Compose تسجل snapshot state المقروءة أثناء composition. تغيير observable value يعمل invalidation للscopes اللي قرأتها؛ mutation داخل List عادية لا تُرى. stability تساعد skipping فقط لو contract صادقة، ولا تعالج work غالية داخل composition.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـStability contract: حدد stage من trace، استخدم stable keys وobservable snapshots، نسّق nested input/insets عند owner واحدة، وابن semantics قبل custom visuals.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Fewer recompositions or a matching screenshot proves the whole UI pipeline is correct and fast.”

<p dir="rtl" lang="ar">في <strong>Stability contract</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الـUI تحافظ على state identity وsemantics/focus، وكل optimization تُنسب للمرحلة المقاسة: composition أو layout أو draw أو input أو GPU. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Stability contract: platform component أفضل لما custom layout/gesture لا تقدم مكسب مقاس وتزيد صيانة accessibility.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Stability contract: قِس frames على release-like build، أعد ترتيب items وغيّر adaptive layout، واختبر TalkBack/keyboard/focus وinsets بعد التحسين.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Stability contract، الـshortcut هي: <bdi dir="ltr">Fewer recompositions or a matching screenshot proves the whole UI pipeline is correct and fast.</bdi> ودي تكسر: الـUI تحافظ على state identity وsemantics/focus، وكل optimization تُنسب للمرحلة المقاسة: composition أو layout أو draw أو input أو GPU.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Stability contract: قِس frames على release-like build، أعد ترتيب items وغيّر adaptive layout، واختبر TalkBack/keyboard/focus وinsets بعد التحسين.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Stability contract: platform component أفضل لما custom layout/gesture لا تقدم مكسب مقاس وتزيد صيانة accessibility.</span>

## English model answer

“Stable means observable public behavior will not change unexpectedly; false annotations can hide updates. I would locate the issue in state, composition, layout, draw, input, or semantics, then measure that stage and recheck accessibility after the optimization. I would measure the relevant frame stage on a release-like build and recheck semantics and focus after the change.”

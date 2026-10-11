---
id: EUI-Q006-ANSWER
question_id: EUI-Q006
status: reviewed
---
# EUI-Q006 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Coordinate gesture consumption and ownership instead of stacking independent scroll containers blindly.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الـUI تحافظ على state identity وsemantics/focus، وكل optimization تُنسب للمرحلة المقاسة: composition أو layout أو draw أو input أو GPU.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A collapsing toolbar and inner list both consume drag deltas. Trace pre-scroll, child consumption, and post-scroll, including fling ownership.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Nested scroll:</strong> frame تبدأ input/state ثم composition أوview traversal، measure/layout، draw وGPU. stable keys تحفظ item identity، nested scroll توزع deltas بين parent/child، وinsets لها owner واحدة. لازم تحدد أي stage بطيئة قبل optimization.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـNested scroll: حدد stage من trace، استخدم stable keys وobservable snapshots، نسّق nested input/insets عند owner واحدة، وابن semantics قبل custom visuals.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Fewer recompositions or a matching screenshot proves the whole UI pipeline is correct and fast.”

<p dir="rtl" lang="ar">في <strong>Nested scroll</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الـUI تحافظ على state identity وsemantics/focus، وكل optimization تُنسب للمرحلة المقاسة: composition أو layout أو draw أو input أو GPU. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Nested scroll: platform component أفضل لما custom layout/gesture لا تقدم مكسب مقاس وتزيد صيانة accessibility.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Nested scroll: قِس frames على release-like build، أعد ترتيب items وغيّر adaptive layout، واختبر TalkBack/keyboard/focus وinsets بعد التحسين.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Nested scroll، الـshortcut هي: <bdi dir="ltr">Fewer recompositions or a matching screenshot proves the whole UI pipeline is correct and fast.</bdi> ودي تكسر: الـUI تحافظ على state identity وsemantics/focus، وكل optimization تُنسب للمرحلة المقاسة: composition أو layout أو draw أو input أو GPU.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Nested scroll: قِس frames على release-like build، أعد ترتيب items وغيّر adaptive layout، واختبر TalkBack/keyboard/focus وinsets بعد التحسين.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Nested scroll: platform component أفضل لما custom layout/gesture لا تقدم مكسب مقاس وتزيد صيانة accessibility.</span>

## English model answer

“Coordinate gesture consumption and ownership instead of stacking independent scroll containers blindly. I would locate the issue in state, composition, layout, draw, input, or semantics, then measure that stage and recheck accessibility after the optimization. I would measure the relevant frame stage on a release-like build and recheck semantics and focus after the change.”

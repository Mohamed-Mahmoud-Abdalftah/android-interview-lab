---
id: EUI-Q005-ANSWER
question_id: EUI-Q005
status: reviewed
---
# EUI-Q005 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Stable keys preserve item identity and state across insertion, removal, and reorder.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الـUI تحافظ على state identity وsemantics/focus، وكل optimization تُنسب للمرحلة المقاسة: composition أو layout أو draw أو input أو GPU.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A LazyColumn uses list indices as keys and items are inserted at the top. Explain the state and animation bugs, then choose stable keys and content types.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Lazy list identity:</strong> frame تبدأ input/state ثم composition أوview traversal، measure/layout، draw وGPU. stable keys تحفظ item identity، nested scroll توزع deltas بين parent/child، وinsets لها owner واحدة. لازم تحدد أي stage بطيئة قبل optimization.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـLazy list identity: حدد stage من trace، استخدم stable keys وobservable snapshots، نسّق nested input/insets عند owner واحدة، وابن semantics قبل custom visuals.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Fewer recompositions or a matching screenshot proves the whole UI pipeline is correct and fast.”

<p dir="rtl" lang="ar">في <strong>Lazy list identity</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الـUI تحافظ على state identity وsemantics/focus، وكل optimization تُنسب للمرحلة المقاسة: composition أو layout أو draw أو input أو GPU. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Lazy list identity: platform component أفضل لما custom layout/gesture لا تقدم مكسب مقاس وتزيد صيانة accessibility.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Lazy list identity: قِس frames على release-like build، أعد ترتيب items وغيّر adaptive layout، واختبر TalkBack/keyboard/focus وinsets بعد التحسين.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Lazy list identity، الـshortcut هي: <bdi dir="ltr">Fewer recompositions or a matching screenshot proves the whole UI pipeline is correct and fast.</bdi> ودي تكسر: الـUI تحافظ على state identity وsemantics/focus، وكل optimization تُنسب للمرحلة المقاسة: composition أو layout أو draw أو input أو GPU.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Lazy list identity: قِس frames على release-like build، أعد ترتيب items وغيّر adaptive layout، واختبر TalkBack/keyboard/focus وinsets بعد التحسين.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Lazy list identity: platform component أفضل لما custom layout/gesture لا تقدم مكسب مقاس وتزيد صيانة accessibility.</span>

## English model answer

“Stable keys preserve item identity and state across insertion, removal, and reorder. I would locate the issue in state, composition, layout, draw, input, or semantics, then measure that stage and recheck accessibility after the optimization. I would measure the relevant frame stage on a release-like build and recheck semantics and focus after the change.”

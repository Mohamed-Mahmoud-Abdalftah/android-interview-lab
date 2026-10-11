---
id: EUI-Q007-ANSWER
question_id: EUI-Q007
status: reviewed
---
# EUI-Q007 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Expose one meaningful control or structured descendants without duplicate announcements.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الـUI تحافظ على state identity وsemantics/focus، وكل optimization تُنسب للمرحلة المقاسة: composition أو layout أو draw أو input أو GPU.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A clickable card contains an icon, title, and status. Decide whether to merge descendants and show how the choice changes TalkBack output and test selectors.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Semantics merging:</strong> الـlayout تختار من available window size وتستخدم start/end بدل left/right. semantics tree هي الواجهة اللي TalkBack والtests تقرأها، وممكن تختلف عن pixels. font scale وfocus order جزء من functional correctness، مش polish.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـSemantics merging: حدد stage من trace، استخدم stable keys وobservable snapshots، نسّق nested input/insets عند owner واحدة، وابن semantics قبل custom visuals.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Fewer recompositions or a matching screenshot proves the whole UI pipeline is correct and fast.”

<p dir="rtl" lang="ar">في <strong>Semantics merging</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الـUI تحافظ على state identity وsemantics/focus، وكل optimization تُنسب للمرحلة المقاسة: composition أو layout أو draw أو input أو GPU. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Semantics merging: platform component أفضل لما custom layout/gesture لا تقدم مكسب مقاس وتزيد صيانة accessibility.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Semantics merging: قِس frames على release-like build، أعد ترتيب items وغيّر adaptive layout، واختبر TalkBack/keyboard/focus وinsets بعد التحسين.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Semantics merging، الـshortcut هي: <bdi dir="ltr">Fewer recompositions or a matching screenshot proves the whole UI pipeline is correct and fast.</bdi> ودي تكسر: الـUI تحافظ على state identity وsemantics/focus، وكل optimization تُنسب للمرحلة المقاسة: composition أو layout أو draw أو input أو GPU.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Semantics merging: قِس frames على release-like build، أعد ترتيب items وغيّر adaptive layout، واختبر TalkBack/keyboard/focus وinsets بعد التحسين.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Semantics merging: platform component أفضل لما custom layout/gesture لا تقدم مكسب مقاس وتزيد صيانة accessibility.</span>

## English model answer

“Expose one meaningful control or structured descendants without duplicate announcements. I would locate the issue in state, composition, layout, draw, input, or semantics, then measure that stage and recheck accessibility after the optimization. I would measure the relevant frame stage on a release-like build and recheck semantics and focus after the change.”

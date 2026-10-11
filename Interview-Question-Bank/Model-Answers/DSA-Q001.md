---
id: DSA-Q001-ANSWER
question_id: DSA-Q001
status: reviewed
---
# DSA-Q001 — Complete model answer

<p dir="rtl" lang="ar">distance map فيها أحسن cost مكتشفة لكل node، والheap تطلع أقل candidate. لما entry الحالية تطابق map وتخرج كأقل قيمة، الأوزان غير السالبة تضمن إن طريق يمر بمسافة أكبر مش هيقللها لاحقًا. negative edge تكسر الضمان ده.</p>

**Spoken answer:** “The map stores the best discovered distance and the heap yields the smallest current candidate. Non-negative edges ensure a settled minimum cannot later be improved through a more expensive prefix.”

**Common wrong answer:** “The first time a node enters the heap, its shortest distance is final.”

**Follow-up 1:** Why compare the popped entry with the map? An improved route may have inserted a newer entry, leaving the older larger candidate stale.

**Follow-up 2:** What algorithm would you consider with negative edges? Bellman-Ford is one option when negative edges exist and negative cycles need detection.

**Rubric:** State map, heap, settled candidate, non-negative condition, and stale entry handling.

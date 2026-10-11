---
id: DSA-Q003-ANSWER
question_id: DSA-Q003
status: reviewed
---
# DSA-Q003 — Complete model answer

<p dir="rtl" lang="ar">لما نكتشف route أحسن، Java PriorityQueue ما عندهاش decrease-key مباشر رخيص، فنضيف entry جديدة. القديمة تفضل لحد poll. نقارن مسافتها بقيمة distance map؛ لو مختلفة نتجاهلها. حذف object من PriorityQueue خطي، فـ lazy deletion أبسط.</p>

**Spoken answer:** “Each improvement inserts a new candidate because the queue has no convenient decrease-key. On poll, I skip an entry whose distance no longer equals the current distance map.”

**Common wrong answer:** Marking a node visited at insertion time, which can prevent a later cheaper route from being processed.

**Follow-up 1:** Does the queue iterator return priority order? No. Java documents that iterator traversal is not guaranteed to be sorted; use poll.

**Follow-up 2:** How does lazy deletion affect complexity? The queue can hold entries proportional to successful relaxations, so a conservative bound uses log E.

**Rubric:** Explain duplicate origin, skip condition, removal cost, iterator semantics, and complexity impact.

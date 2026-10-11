---
id: ARC-Q001-ANSWER
question_id: ARC-Q001
status: reviewed
---
# ARC-Q001 — Complete model answer

**Spoken answer:** “I would let the UI send an action and display state, keep the product validation in a use case or repository, and let a data adapter own persistence. I would make failures visible instead of reporting success after a catch.”

<p dir="rtl" lang="ar">الـ UI تعرض state وتستقبل الحدث. قاعدة صلاحية note مكانها في boundary قابلة للاختبار. adapter التخزين تعرف SQL والـ transaction. catch عام يعرض نجاح وهمي يخلط المسؤوليات.</p>

**Mechanics:** The boundary follows independent reasons for change: presentation, product policy, and storage mechanics. The Android architecture guide recommends distinct UI and data responsibilities, while a domain layer is useful when logic is complex or reused. [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) and [data layer guide](https://developer.android.com/topic/architecture/data-layer) were checked 2026-10-10.

**Common wrong answer:** “Put every line in a separate class.” More classes do not by themselves establish a meaningful contract.

**Follow-up 1:** Would every simple save action need a domain class? No. A small feature can call a repository directly; add a use case when the rule is reused or complexity makes the boundary useful.

**Follow-up 2:** Who decides whether an empty title is an expected user error? The product contract decides; the domain can return a validation result, and the UI maps that result to accessible feedback.

**Rubric for self-review:** Name the behavioral contract, trace validation and storage effects, justify the smallest useful boundary, and separate fake-test proof from Android/database evidence. This is visible practice, not a scored assessment.

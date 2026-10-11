---
id: ARC-Q005-ANSWER
question_id: ARC-Q005
status: reviewed
---
# ARC-Q005 — Complete model answer

**Spoken answer:** “I would start with the product rule and one narrow writer dependency. A generic hierarchy adds inheritance and hidden contracts without a demonstrated need; Hilt may be useful later for Android graph wiring but does not improve the rule itself.”

<p dir="rtl" lang="ar">ابدأ بسلوك مطلوب واختبار واضح. inheritance هنا ممكن تخفي failure semantics وتفرض abstraction على feature صغيرة. constructor injection كافية للمعمل، وHilt قرار wiring لاحقًا.</p>

**Mechanics:** Composition keeps the save rule explicit. Android guidance permits a small repository/data-source merge and suggests a domain layer for reuse or complexity, so layer count should follow actual needs. [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) and [data layer guide](https://developer.android.com/topic/architecture/data-layer) were checked 2026-10-10.

**Common wrong answer:** “Staff-level architecture requires a pattern for every action.” The evidence is clarity, change isolation and correct failure behavior, not pattern count.

**Follow-up 1:** When would a use-case class become worthwhile? When business rules are reused, require orchestration, or become hard to test and explain inside the existing owner.

**Follow-up 2:** When might a DI framework be worthwhile? When the Android dependency graph has multiple scopes and bindings whose manual wiring becomes error-prone; test the graph separately.

**Rubric for self-review:** Name the behavioral contract, trace validation and storage effects, justify the smallest useful boundary, and separate fake-test proof from Android/database evidence. This is visible practice, not a scored assessment.

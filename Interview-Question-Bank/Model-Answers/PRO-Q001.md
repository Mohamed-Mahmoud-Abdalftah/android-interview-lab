---
id: PRO-Q001-ANSWER
question_id: PRO-Q001
status: reviewed
---
# PRO-Q001 — Complete model answer

<p dir="rtl" lang="ar">أحدد assets: session، order ownership، payment state وبيانات العميل. أحدد actors والentry points: browser، تطبيق خارجي، exported Activity وbackend. أرسم boundaries بين OS routing والتطبيق والشبكة. بعدين أكتب abuse cases زي host شبيه، تعديل status، order لمستخدم تاني، replay، وتسريب URL في logs. كل خطر يتربط بـ control واختبار محدد.</p>

**Spoken answer:** “I identify assets, actors, entry points, and trust boundaries, then list concrete abuse cases. Each mitigation gets evidence at the right layer: parser tests, device routing tests, and backend authorization tests.”

**Common wrong answer:** Starting with a generic list of encryption tools without tracing the feature's actual data and authority.

**Follow-up 1:** Who should join the threat-model review? Include Android, backend, product, and security owners because the flow crosses all of their boundaries.

**Follow-up 2:** When should the model be updated? Update it when entry points, assets, dependencies, authorization rules, or data flows materially change.

**Rubric:** Name assets, actors, entry points, boundaries, abuse cases, controls, and layer-specific evidence.

---
id: ARC-Q011-ANSWER
question_id: ARC-Q011
status: reviewed
---
# ARC-Q011 — Complete model answer

<p dir="rtl" lang="ar">Repository تعرض domain data لباقي التطبيق، تحدد source of truth، تنسق local/remote، تدير refresh/write/sync policy، وتحول models/errors عند boundary. لو هي مجرد pass-through لمصدر واحد قد تظل boundary مفيدة، لكن القيمة تظهر مع policy فعلية مش تغيير أسماء.</p>

**Spoken answer:** “A repository owns the data contract and coordination policy: what the app reads, how sources update the source of truth, and how writes, refreshes, and conflicts are handled.”

**Common wrong answer:** “A repository is an interface in front of Retrofit so the ViewModel can mock it.”

**Follow-up 1:** Can a small repository contain its only data source? Yes. Keep the boundary simple and split a separate source when another source or distinct responsibility appears.

**Follow-up 2:** Should the UI receive network DTOs? Prefer stable application models so transport fields and nullability do not become presentation contracts accidentally.

**Rubric:** Name exposure, source of truth, source coordination, write/conflict policy, and model boundary.

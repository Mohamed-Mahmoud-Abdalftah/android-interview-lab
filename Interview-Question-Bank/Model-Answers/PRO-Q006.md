---
id: PRO-Q006-ANSWER
question_id: PRO-Q006
status: reviewed
---
# PRO-Q006 — Complete model answer

<p dir="rtl" lang="ar">القرار يبدأ من شكل البيانات والعمليات. Room مناسبة لـentities، علاقات، indexes، filtering، partial updates وtransactions بين صفوف متعددة. DataStore مناسبة لإعدادات صغيرة يملكها التطبيق زي theme أو onboarding state؛ Preferences مرنة بالمفاتيح وProto typed. قائمة كبيرة قابلة للبحث أو JSON ضخم جوه preference علامة إننا محتاجين database. كمان أحدد source of truth، migration policy، failure handling وownership في DI قبل اختيار API.</p>

**Spoken answer:** “I choose from the data contract. Relational, queryable state with multi-row invariants belongs in Room. Small application settings that are read and updated as one value fit DataStore. I also define ownership, migration, and corruption behavior instead of choosing solely by API convenience.”

**Common wrong answer:** DataStore is newer, so it should replace Room for every local data set.

**Follow-up 1:** Would a list of downloaded articles fit DataStore? No, it needs indexed queries, per-row updates, and scalable relational storage, so Room is the stronger fit.

**Follow-up 2:** When would Proto DataStore beat Preferences DataStore? When the setting benefits from a typed schema, explicit defaults, and controlled schema evolution.

**Rubric:** Discuss data shape, queries, transactions, size, typed settings, ownership, migrations, and failure policy.

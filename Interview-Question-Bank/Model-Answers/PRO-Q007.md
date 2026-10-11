---
id: PRO-Q007-ANSWER
question_id: PRO-Q007
status: reviewed
---
# PRO-Q007 — Complete model answer

<p dir="rtl" lang="ar">أجمع starting schema version والexception والمigrations المسجلة وschema exports. أعيد الاختبار بقاعدة file من version 1 وفيها rows تمثل edge cases، وبعدها أفتحها بالنسخة 4. أدور على edge ناقصة زي 1→2 أو transformation تفشل بسبب null/duplicate data. أصلحها كـforward migration، وأفحص schema والبيانات وDAO queries. ما أستخدمش destructive fallback لإخفاء المشكلة، وأختبر كل starting version مدعومة قبل staged rollout.</p>

**Spoken answer:** “I reproduce from an exported version-one database, not a fresh install. I inspect the registered migration graph and execute the full path with representative rows. The fix is a tested forward migration with data and constraint assertions, followed by a staged rollout and version-specific monitoring.”

**Common wrong answer:** Add destructive fallback because the schema is only a local cache.

**Follow-up 1:** Why can a fresh-install test pass? It creates the target schema directly and never executes the historical transformation path.

**Follow-up 2:** How do duplicate rows affect a new unique index? Index creation can fail, so the migration needs an explicit product rule for resolving existing duplicates.

**Rubric:** Require exact starting version, exported file, graph inspection, representative data, forward repair, full assertions, and rollout evidence.

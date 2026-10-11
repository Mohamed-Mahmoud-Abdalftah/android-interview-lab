---
id: KOT-Q009-ANSWER
question_id: KOT-Q009
status: reviewed
---
# KOT-Q009 — Model answer

**Spoken answer:** “The generated data-class equality and hash code include `tenantId`, because it is a primary-constructor property. Mutating it after insertion changes the key's logical value while the map still holds that object. The Java `Map` contract leaves behavior unspecified when a key changes in a way that affects equality, so I would not promise that every lookup fails. I would use an immutable key and insert a new mapping under a new key when the tenant changes.”

<p dir="rtl" lang="ar"><strong>الشرح بالمصري:</strong> الـ <code dir="ltr">data class</code> بتحسب <code dir="ltr">equals()</code> و<code dir="ltr">hashCode()</code> من <code dir="ltr">tenantId</code> و<code dir="ltr">profileId</code>. بعد ما المفتاح يدخل الـ <code dir="ltr">Map</code>، تغيير <code dir="ltr">tenantId</code> بيغيّر معنى المفتاح وهو لسه جواها. ممكن تشوف <code dir="ltr">cache miss</code>، لكن ما ينفعش أقول إنه هيحصل دائمًا؛ عقد Java بيعتبر السلوك غير محدد لما تغيير المفتاح يأثر على المساواة. الحل مفتاح بقيم ثابتة، ونقل الـ mapping بمفتاح جديد واضح.</p>

**Mechanics:** Generated data-class equality and hashing normally use all primary-constructor properties, including `var` properties. The Java SE 17 `Map` contract explicitly does not specify map behavior after a key changes in a way that affects equality. A hash-based implementation may expose surprising lookups, but collision patterns and implementation details prevent a universal output claim for `cache[key]`. [Kotlin data classes](https://kotlinlang.org/docs/data-classes.html), [Kotlin equality](https://kotlinlang.org/docs/equality.html), and [Java Map contract](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Map.html), checked 2026-10-10.

**Common wrong answer:** “The lookup must return null after this mutation.” The design is unsafe, but that exact result is not portable. **When not to add a mutable key:** For an intentional rekey, remove or invalidate the old entry before changing identity, then insert a fresh immutable key; do not rely on finding an already-mutated key to remove it.

**Follow-up 1:** Would moving a mutable display label into the data-class body remove it from generated equality? **Yes, generated equality ignores body properties.** That may be appropriate if the label is truly presentation-only, but it does not make a mutable object a good identity key by itself; define the key's stable identity explicitly.

**Follow-up 2:** Would `key.copy()` make an immutable replacement if a constructor property holds a mutable list? **No.** Data-class `copy()` is shallow and can share that list. A key must contain stable, defensively captured components all the way down for its equality/hash behavior to remain stable.

**Fair rubric (10):** 3 generated equality/hash inputs, 3 map-contract uncertainty, 2 immutable redesign, 1 update order, 1 shallow-copy caveat. No claim of a specific observed lookup result.

---
id: SCN-002
lesson_id: KOT-002
status: reviewed
code_verification: not_run
---
# SCN-002 — Profile cache drifts after a mutable key update

**Hypothetical debugging exercise, not a production incident or a tested cache implementation.** A profile cache appears to miss after a tenant switch. Environment for the reasoning: Kotlin/JVM with a map backed by a Java `Map` implementation; no Android runtime behavior, hit-rate measurement, or particular map lookup result is asserted. Start with the [Day 2 lesson](../01-Kotlin-JVM-ART/kot-002-val-var-types-equality-and-identity.md).

<p dir="rtl" lang="ar"><strong>ملخص بالمصري:</strong> تخيّل إن cache لبيانات profile بقت تعمل <code dir="ltr">miss</code> بعد تغيير الـ tenant. المفتاح <code dir="ltr">data class</code> وفيه <code dir="ltr">var</code>؛ لو اتغيّر وهو جوه الـ <code dir="ltr">Map</code>، معنى المساواة والـ <code dir="ltr">hashCode()</code> ممكن يتغيّر. دي مخاطرة مؤكدة في التصميم، لكن نتيجة كل <code dir="ltr">lookup</code> مش مضمونة؛ لازم نجمع دليل ونقارن بفرضيات تانية.</p>

## Symptom and controlled reproduction

The following sketch exposes the risky operation but is **not** a claim that `observed` always equals null:

```kotlin
data class ProfileCacheKey(var tenant: String, val userId: String)
val key = ProfileCacheKey("north", "42")
val cache = hashMapOf(key to "cached-profile")
key.tenant = "south"
val observed = cache[key]
```

The key's `tenant` is a primary-constructor property, so the generated `equals()` and `hashCode()` include it. The exact map lookup result after this mutation is not portable. The [Java SE 17 `Map` contract](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Map.html) says behavior is unspecified when a key changes in a way that affects equality. That is enough to reject this key design without inventing an observed outcome.

## Competing hypotheses and separating evidence

1. **Equality-significant key mutation:** Record redacted key fields and computed hash before insertion and before lookup; inspect every write to `tenant`. A changed identity field while stored is direct evidence of a contract violation, even if one local lookup happens to succeed.
2. **Normal eviction or cache recreation:** Trace cache instance identity, configured size/expiry, and eviction events. A miss with a new cache instance does not require key mutation.
3. **Tenant-scoping error:** Check that the lookup builds a key for the same tenant and user as the insertion. A correctly immutable key cannot repair a caller that asks for the wrong tenant.
4. **Concurrent access:** Establish ownership or synchronization around map operations. A plain mutable map shared across threads can have separate concurrency problems; do not attribute them to `hashCode()` without evidence.

For a real Android incident, capture app/version information, a redacted event sequence for insertion, tenant switch, and lookup, and a minimal JVM reproducer using the actual cache implementation. Avoid logging profile data or raw account identifiers. No device logs, stack trace, or production metrics are available for this exercise.

## Root cause in the exercise and correction

The explicit mutation of `tenant` after insertion breaks the stable-key assumption. It does **not** establish a universal return value for `cache[key]`; implementations and collisions can differ. [Kotlin data classes](https://kotlinlang.org/docs/data-classes.html) generate equality and hashing from primary-constructor properties, and [Kotlin equality](https://kotlinlang.org/docs/equality.html) explains the `equals()`/`hashCode()` relationship.

<p dir="rtl" lang="ar">الإصلاح هنا إن الـ key يبقى بقيم ثابتة، مثل <code dir="ltr">data class ProfileCacheKey(val tenant: String, val userId: String)</code>. عند تغيير الـ tenant، الغِ الربط القديم بمفتاحه الأصلي قبل أي تغيير في الهوية، وأنشئ مفتاحًا جديدًا، وبعد التحقق من الصلاحية حمّل بيانات الـ tenant الجديدة. ما تنقلش profile قديمة بين tenants لمجرد إن الاسم متشابه.</p>

## Tempting wrong fixes

- Changing only `val key` to `var key` or vice versa does not freeze a `var tenant` inside the object.
- Reconstructing an equal-looking key after mutation does not repair the contract already violated while the original key was stored.
- Treating every miss as normal and silently refilling the cache can hide an identity or tenant-isolation bug.
- Assuming `cache[key]` must fail for every map implementation overstates the evidence.

## Prevention and review

Use stable value fields for keys, keep tenant identity explicit, and test insertion, lookup, invalidation, and tenant switching with the chosen implementation. Include a test that no cached profile crosses tenant boundaries. Review nested key fields for mutable collections because a `data class` `copy()` is shallow. This is a proposed test and review plan, not an executed rollout.

## Senior follow-ups

1. **Would moving a mutable display field into the class body help?** It removes that field from generated data-class equality and hashing, but only if display text is truly not part of key identity. Keep identity fields immutable and explicit.
2. **Should a failing lookup be the only regression assertion?** No. The Java `Map` contract makes an exact post-mutation lookup result non-portable. Assert the intended stable-key design and tenant isolation; use any implementation-specific miss only as a diagnostic observation.

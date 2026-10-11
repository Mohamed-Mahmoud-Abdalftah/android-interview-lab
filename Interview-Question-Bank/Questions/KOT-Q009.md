---
id: KOT-Q009
lesson_id: KOT-002
topic: Data-class equality and mutable map keys
difficulty: senior
style: debugging
expected_minutes: 4
status: reviewed
---
# KOT-Q009 — A key changes inside a cache

Review the risk in this sketch without assuming an exact lookup result:

```kotlin
data class CacheKey(var tenantId: String, val profileId: String)
val key = CacheKey("north", "42")
val cache = hashMapOf(key to "cached")
key.tenantId = "south"
val observed = cache[key]
```

Which generated functions depend on `tenantId`? What does the Java `Map` contract say about mutating an equality-significant key? Propose a key design and an update path that avoid this risk.

[Open complete model answer](../Model-Answers/KOT-Q009.md) · [Lesson](../../01-Kotlin-JVM-ART/kot-002-val-var-types-equality-and-identity.md)

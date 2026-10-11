---
id: MOCK-001
status: reviewed
---
# MOCK-001 — Kotlin and coroutines

**Recommended time:** 75 minutes. **Default:** Learning Mode; scoring is optional and self-reported. Read the rubric before starting.

## Question-only interview

1. **KOT-Q001:** Explain `String` versus `String?`. Trace `fun length(s: String?): Int = s?.length ?: 0` for `null` and `"Ada"`. When is zero an unsuitable fallback?
2. **KOT-Q002:** An unannotated Java SDK method `String nameFor(String id)` sometimes returns null. Why can Kotlin compile `nameFor(id).length`, and how would you contain the risk?
3. **KOT-Q003:** Review `if (holder.name != null) println(holder.name.length)` when `name` is mutable. What is the concern, and what does a local snapshot solve?
4. **KOT-Q004:** A backend can return null or blank display names. Compare a UI fallback with a typed validation error. Where should normalization live, and what tests would you write?
5. **KOT-Q005:** Why is `data class ProfileName private constructor(val value: String)` risky as a validated type? Propose a design that keeps blank values out.
6. **KOT-Q006:** Consider: ```kotlin val labels = mutableListOf("Ada") val alias = labels labels.add("Mona") ``` What does `val` prevent here, what does `alias` observe, and how would changing `labels` to `var` alter the guarantees? Explain how you would expose this data if callers must not mutate it.
7. **KOT-Q007:** Review this code: ```kotlin val inferred = mutableListOf("Ada") val view: List<String> = inferred ``` What are the static types of `inferred` and `view`? Which of `inferred.add("Mona")` and `view.add("Mona")` compiles? Does `view` provide a snapshot, and when would you declare an explicit type at an API boundary?
8. **KOT-Q008:** Predict the three comparisons and explain the rule behind each: ```kotlin data class Candidate(val id: String) val first = Candidate("7") val second = Candidate("7") val alias = first first == second first === second first === alias ``` How does `==` behave if one operand is null? Why is `===` a poor substitute for a value comparison?
9. **KOT-Q009:** Review the risk in this sketch without assuming an exact lookup result: ```kotlin data class CacheKey(var tenantId: String, val profileId: String) val key = CacheKey("north", "42") val cache = hashMapOf(key to "cached") key.tenantId = "south" val observed = cache[key] ``` Which generated functions depend on `tenantId`? What does the Java `Map` contract say about mutating an equality-significant key? Propose a key design and an update path that avoid this risk.
10. **KOT-Q010:** A Java SDK returns a live, mutable `java.util.List<String>` and may change it later. Kotlin stores that object in a `val` and exposes it to callers through a `List<String>` property. Assume the SDK returned a non-null list. What do `val` and Kotlin's read-only `List` interface guarantee, and what can still change? Design a boundary that provides a stable snapshot. State one limit of a shallow copy and one concurrency concern.
11. **KOT-Q011:** Given a class with a property initializer, then an init block, then another property initializer, in what order do they run? Trace the events for the ConstructionTimeline test with input " Ada ". What happens to later steps when validation throws?
12. **KOT-Q012:** Compare a constructor parameter declared as name: String with val name: String. Which becomes a property accessible after construction? In a domain model for an Android repository, when would you deliberately avoid storing the raw input?

## Answer key

1. **KOT-Q001:** `String` expresses a non-null Kotlin contract, while `String?` requires a null-aware branch. For null, the safe call yields null and Elvis returns zero; for `Ada`, it returns three. Zero is only right when the product contract treats absence as zero. [Complete answer](../Interview-Question-Bank/Model-Answers/KOT-Q001.md)
2. **KOT-Q002:** An unannotated Java return is a platform type, so Kotlin cannot enforce the same null contract. I assign it to `String?`, validate it once, and expose a safe domain result. I test null and blank responses from a fake SDK. [Complete answer](../Interview-Question-Bank/Model-Answers/KOT-Q002.md)
3. **KOT-Q003:** The two property accesses can observe different values, so Kotlin may refuse the smart cast. I capture `val snapshot = holder.name` and check that local before using it. This keeps the two operations on one value, but it does not make updates to the holder atomic. [Complete answer](../Interview-Question-Bank/Model-Answers/KOT-Q003.md)
4. **KOT-Q004:** For an optional display label, a documented `Guest` fallback is reasonable. For a required identity, I return a typed error and preserve evidence for diagnosis. I normalize at the data-to-domain boundary so downstream UI code does not repeatedly guess, and I test null, blank, valid, and malformed responses. [Complete answer](../Interview-Question-Bank/Model-Answers/KOT-Q004.md)
5. **KOT-Q005:** A generated data-class `copy` can expose a way to construct a changed value, undermining a private validation factory. For this small type I use an ordinary class with a private constructor and a `parse` function that checks every input. If value semantics are needed, I add them deliberately without exposing an unchecked constructor path. [Complete answer](../Interview-Question-Bank/Model-Answers/KOT-Q005.md)
6. **KOT-Q006:** `val` prevents me from assigning a different list to `labels`; it does not freeze the list object. `labels.add( [Complete answer](../Interview-Question-Bank/Model-Answers/KOT-Q006.md)
7. **KOT-Q007:** The initializer gives `inferred` the static type `MutableList<String>`, so `inferred.add` compiles. The declared type of `view` is `List<String>`, which has no `add`, so `view.add` does not compile. Both names still refer to the same underlying list, so `view` is not a snapshot. I use an explicit type at a public boundary to state the intended operations, and copy when I promise stable contents. [Complete answer](../Interview-Question-Bank/Model-Answers/KOT-Q007.md)
8. **KOT-Q008:** `first == second` is true because the data class generates equality from its primary-constructor `id`. `first === second` is false because these are two constructed instances. `first === alias` is true because `alias` points to `first`. I use `==` for value semantics and reserve `===` for a real identity question. [Complete answer](../Interview-Question-Bank/Model-Answers/KOT-Q008.md)
9. **KOT-Q009:** The generated data-class equality and hash code include `tenantId`, because it is a primary-constructor property. Mutating it after insertion changes the key's logical value while the map still holds that object. The Java `Map` contract leaves behavior unspecified when a key changes in a way that affects equality, so I would not promise that every lookup fails. I would use an immutable key and insert a new mapping under a new key when the tenant changes. [Complete answer](../Interview-Question-Bank/Model-Answers/KOT-Q009.md)
10. **KOT-Q010:** `val` prevents rebinding one Kotlin reference, and `List<String>` prevents mutation through that Kotlin interface. Neither stops the Java SDK from changing the live backing list. If callers need a stable list of strings, I copy the elements into a separately owned list at the boundary and expose a read-only type. The copy is shallow, and I must coordinate with the SDK if it can mutate during the copy. [Complete answer](../Interview-Question-Bank/Model-Answers/KOT-Q010.md)
11. **KOT-Q011:** Kotlin interleaves property initializers and init blocks in their source order. In this example normalization records property:Ada, validation records init, and the later label initializer records label:ADA. If require fails, construction throws before the later initializer runs. [Complete answer](../Interview-Question-Bank/Model-Answers/KOT-Q011.md)
12. **KOT-Q012:** A primary-constructor parameter without val or var is an input to construction, not automatically a stored property. Adding val stores a read-only property that members and callers can access according to visibility. I often normalize raw input and store only the validated value. [Complete answer](../Interview-Question-Bank/Model-Answers/KOT-Q012.md)

## Published rubric

Score each answer 0–4: **0** absent/unsafe, **1** definition only, **2** correct core contract, **3** mechanism plus failure/test, **4** senior trade-off, evidence boundary, and clear communication. Coding questions also require compiling logic, boundary tests, and honest complexity. The score is practice evidence, never a hiring guarantee.

## Debrief

Record three items: the first wrong assumption, the slowest explanation, and the missing test. Return to linked lessons before repeating this pack. Do not memorize the answer key wording.

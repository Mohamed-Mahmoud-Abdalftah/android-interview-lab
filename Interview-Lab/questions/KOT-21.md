---
id: "KOT-21"
question: "What are value classes, and what performance/interop caveats do they have?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "B"
phase: 1
priority: "P1"
order: 21
editorial_status: "reviewed"
---

# KOT-21

## Original interview question

What are value classes, and what performance/interop caveats do they have?

## What the interviewer evaluates

Explain distinct domain type identity, conditional unboxed representation, boxing sites, and Java/serialization boundaries.

## Concept and technical explanation

Value classes in Kotlin (declared using `@JvmInline value class`) provide a compiler-enforced mechanism for creating strongly typed domain wrappers around a single underlying value with zero runtime heap allocation in unboxed positions. They directly eliminate primitive obsession—such as passing a raw Long where a specific UserId, AccountId, or Milliseconds unit is required—without paying the memory and garbage collection penalty of traditional object wrappers. At compile time, the Kotlin compiler enforces complete type isolation. In compiled bytecode, the compiler unboxes the value class whenever possible, replacing parameter and return signatures with the raw underlying primitive or reference. However, boxing into a heap-allocated wrapper object is mandatory whenever the value class is used as a generic type argument (such as in `List<UserId>`), cast to an interface, or held in a nullable variable (such as `UserId?`). Additionally, the compiler mangles function names accepting value classes to prevent Java bytecode signature collisions.

## Practical walkthrough (English)

Consider a financial transfer API vulnerable to primitive transposition: `fun transfer(fromAccountId: Long, toAccountId: Long, amountCents: Long)`. Callers can accidentally swap `fromAccountId` and `toAccountId` without receiving any compiler warnings, corrupting customer ledger balances. By introducing value classes: `@JvmInline value class AccountId(val value: Long)` and `@JvmInline value class AmountCents(val value: Long)`, the method signature becomes `fun transfer(from: AccountId, to: AccountId, amount: AmountCents)`. Transposing arguments now fails compilation immediately. In bytecode, the parameters remain raw primitive `long` types, avoiding object allocations. However, if the API stores accounts in a generic collection: `val accounts = listOf(AccountId(1L))`, the JVM must box the primitive into a heap-allocated `AccountId` instance because generic type arguments on the JVM cannot hold primitives.

## Explanation in Arabic

الـ Value Classes (المعرفة بـ `@JvmInline value class`) هي أداة قوية في Kotlin لإنشاء أنواع مخصصة قوية (Domain Types) بدون تكلفة الذاكرة المرتبطة بإنشاء كائنات على الـ Heap:

1. المشكلة اللي بتحلها (Primitive Obsession):
   - في تطبيقات كتير بنستخدم `String` للـ `UserId` و `OrderId` و `Email`. الخلط بينهم في الـ Parameters وارد جداً وبيعمل Bugs صعبة في الإنتاج.
   - لو عملت `data class UserId(val value: String)`، حليت مشكلة الأمان، لكن أنشأت Object جديد في الـ Heap لكل ID، وده بيضغط على الـ Garbage Collector بشدة.

2. إزاي بتشتغل تحت الغطاء (How it works in JVM):
   - المترجم بيعمل **Inlining** للقيمة الأساسية في معظم الحالات. في الـ Bytecode، الدالة اللي بتاخد `UserId` بتتحول لدالة عادية بتاخد `String` مباشرة، مع **Name Mangling** في اسم الدالة (زي `getUser-xxxx(String)`) لمنع تصادم الـ Signatures في الـ JVM.

3. متى يحدث الـ Boxing (Boxing Caveats):
   - لو استخدمت الـ Value Class في **Generics** (زي `List<UserId>`).
   - لو جعلتها **Nullable** (زي `UserId?`).
   - لو عاملتها كـ **Interface** (Polymorphism).
   - في الحالات دي، الـ JVM مضطر يعمل **Boxing** وينشئ كائن Wrapper في الـ Heap، وتفقد ميزة انعدام الـ Allocation.

## Practical walkthrough

في نظام التجارة الإلكترونية:
- العملات والمبالغ المالية:
  `@JvmInline value class Money(val cents: Long)`
  `@JvmInline value class UserId(val raw: String)`
- الآن الدوال أصبحت آمنة تماماً:
  `fun debit(user: UserId, amount: Money)`
  مستحيل المطور يمرر المعرفات بالخطأ.
- في الـ Bytecode:
  الدالة بتتحول لـ `debit(String user, long amount)` بدون أي Heap Object إضافي!
- **التحذير من الـ Interoperability مع Java:**
  كود Java لا يستطيع مناداة الدالة دي بسهولة بسبب الـ Name Mangling اللي بيضيفه Kotlin (`debit-abc(String, long)`). لو محتاج تستدعيها من Java، لازم تستخدم `@JvmName` صريح أو تتعامل مع الـ Wrapper.

## Why it matters and how it works

Value classes encode domain distinctions without always paying a wrapper allocation. The representation changes by use site, so performance and Java ABI require inspection. Type safety is the primary benefit; allocation reduction is conditional.

## Worked example

JVM illustration with a validated identifier.
```kotlin
@JvmInline value class UserId(val value: String) {
    init { require(value.isNotBlank()) }
}
fun loadUser(id: UserId): String = id.value
fun main() = println(loadUser(UserId("u-7")))
```
A Java-facing or serialization API needs explicit interop tests for the compiler version in use.

## Trade-offs and decision criteria

Prefer value class for one-field identifiers or units with clear invariants. Use data class for multiple fields or when stable object identity/interop simplicity matters. A typealias is cheaper syntactically but provides no distinct type. Avoid promising performance without profiling boxed generic and nullable paths.

## Failure modes

An API returns `List<UserId>` and assumes every element is unboxed because the class is “inline”; generic storage can box. Another risk is Java callers unable to access default mangled/unboxed signatures. Design and test the Java surface deliberately.

## Production perspective

A commerce app models `ProductId` and `OrderId` as separate value classes, validates them at the network boundary, and uses explicit serializers. Benchmark hot paths using release builds; database and Java adapter tests cover representation boundaries.

## Interview answer — short

Value classes wrap a single underlying value to provide strong domain typing without heap allocation overhead in unboxed contexts. The compiler replaces them with their raw underlying type in bytecode, but boxes them into heap wrapper objects whenever they are stored in generic collections, cast to interfaces, or declared as nullable.

## Interview answer — structured

Value classes in Kotlin, annotated with `@JvmInline`, introduce domain-level type safety around a single property without incurring the memory footprint of a full object. They eradicate primitive obsession by ensuring that raw primitives like strings or integers are bound to distinct, non-interchangeable domain types at compile time.

The Kotlin compiler optimizes value classes by unboxing them in generated bytecode, passing the raw primitive directly in method parameters and return values.

In production, however, senior engineers must recognize mandatory boxing sites. Whenever a value class is placed into a generic collection like List, cast to a shared interface, or marked nullable, the runtime must allocate a wrapper object on the heap.

Kotlin mangles bytecode function names that accept value classes to prevent JVM signature clashes, which requires careful planning when designing public APIs consumed by Java callers.


## Interview answer — deep senior

At the bytecode and JVM ABI level, `@JvmInline value class` introduces sophisticated name mangling. If a Kotlin function is declared as `fun process(id: UserId)` where UserId wraps a String, another function `fun process(name: String)` would have an identical JVM signature `(Ljava/lang/String;)V`, causing an invalid bytecode collision. To resolve this, the Kotlin compiler mangles the value-class function name by appending a hash suffix—such as `process-u7aFq8g(String id)`. Consequently, calling this function directly from Java code requires invoking the mangled name or providing an un-mangled `@JvmName` override. Regarding memory behavior, unboxing is guaranteed only in direct variable assignments, non-null function parameters, and non-null return values. Boxing occurs in three critical scenarios: 1) Generics: because JVM generics erase to `java.lang.Object`, writing `List<UserId>` instantiates a `java.util.List` containing boxed `UserId` heap instances, negating allocation savings in large collections; 2) Interfaces: if `UserId` implements `interface EntityId`, passing it as `EntityId` forces immediate heap boxing; and 3) Nullability: declaring `val id: UserId? = null` requires a boxed wrapper because primitive types cannot represent null directly without a sentinel or wrapper on the JVM. In enterprise Android architectures, we leverage value classes extensively in domain and presentation models for IDs and units of measure, while ensuring high-throughput data processing layers avoid generic boxing pitfalls.

## How to answer in the interview

- **Why:** Create domain-specific, strongly-typed wrappers around primitive values without heap allocation overhead.
- **How:** Define `@JvmInline value class UserId(val raw: String)` so the compiler replaces instances with the underlying type in bytecode.
- **Trade-offs:** Value classes box into heap objects when used in generic contexts, nullable types, or collections (`List<UserId>`).
- **Failure cases:** Name-mangled value class methods called from Java code, resulting in cryptic compiler errors or missing symbols on the Java side.
- **Production solution:** Use value classes to enforce domain type safety for IDs, currencies, and tokens, adding `@JvmName` when Java interoperability is required.

## Deep-dive talking points

Compare typealias and value class, identity, method mangling, boxed generics, nullability, Java exposure, and serializer tests.

## Follow-up questions

- **Interviewer:** "Can a value class have properties and methods?"
  **Answer:** "Yes. A value class can declare methods, computed properties, and init blocks. However, it cannot have secondary backing fields, late-initialized properties, or inherit from class hierarchies (it can only implement interfaces)."

- **Interviewer:** "Why does the Kotlin compiler apply name mangling to functions taking value classes?"
  **Answer:** "Because unboxing erases the value class to its underlying type. If you have two overloads `fun send(id: UserId)` and `fun send(id: AccountId)` where both wrap String, Java bytecode would see two identical methods `void send(String)`. Mangling prevents JVM method signature collisions."

- **Interviewer:** "Can a value class wrap multiple properties?"
  **Answer:** "Currently on JVM Android, value classes can only wrap a single underlying property. Kotlin has experimental multi-field value class support on Kotlin/Native and future Valhalla JVMs, but for current Android production apps, single-property wrapping is the rule."

## Self-check rubric

State the single-field rule, identify two boxing situations, and explain one Java interop risk.

## References and reviewed-on date

- [Kotlin inline value classes](https://kotlinlang.org/docs/inline-classes.html) — representation and boxing.
- [Calling Kotlin from Java](https://kotlinlang.org/docs/java-to-kotlin-interop.html) — Java exposure.

Technically reviewed against primary documentation on 2026-10-13.

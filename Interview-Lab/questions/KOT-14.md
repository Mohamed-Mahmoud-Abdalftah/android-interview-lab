---
id: "KOT-14"
question: "Explain Kotlin variance: in, out, invariance, and star projections."
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "B"
phase: 1
priority: "P1"
order: 14
editorial_status: "reviewed"
---

# KOT-14

## Original interview question

Explain Kotlin variance: in, out, invariance, and star projections.

## What the interviewer evaluates

Apply producer/consumer variance safely, distinguish declaration/use-site variance and star projections.

## Concept and technical explanation

Variance in Kotlin defines how subtyping between more complex generic types relates to subtyping between their component type arguments. It resolves type safety issues surrounding generic collections and containers:
1. Invariance (default): If Dog is a subtype of Animal, Box<Dog> has NO subtyping relationship with Box<Animal>. Invariance protects mutable containers from runtime type corruption, preventing callers from inserting a Cat into a Box<Dog> masquerading as Box<Animal>.
2. Covariance (out): Preserves the subtyping relationship: if Dog is a subtype of Animal, List<Dog> is a subtype of List<Animal>. The type parameter is designated as a Producer, meaning it can only appear in out positions (function return types) and cannot appear in in positions (function parameter types).
3. Contravariance (in): Inverts the subtyping relationship: if Dog is a subtype of Animal, Consumer<Animal> is a subtype of Consumer<Dog>. The type parameter is designated as a Consumer, meaning it can only appear in in positions (function arguments) and cannot be returned.
4. Star Projections (*): Used when type arguments are unknown or unconstrained. List<*> denotes a list of unknown type that can safely produce Any?, equivalent to List<out Any?>. MutableList<*> permits reading Any? but forbids writing any element except null.
Kotlin supports declaration-site variance directly on the class or interface definition, as well as use-site variance via type projections.

## Practical walkthrough (English)

Consider handling UI states and event listeners in an Android reactive architecture:

Failure Scenario — Mutable Container Subtyping Violation (Why Invariance Exists):
```kotlin
open class Animal
class Dog : Animal()
class Cat : Animal()

// Hypothetical scenario if MutableList were Covariant:
val dogs: MutableList<Dog> = mutableListOf(Dog())
val animals: MutableList<Animal> = dogs // Compile Error! Kotlin enforces invariance!

// If allowed, this would corrupt runtime heap state:
// animals.add(Cat()) // Heap pollution! dogs now contains a Cat!
// val dog: Dog = dogs[1] // Crash: ClassCastException at runtime!
```
Kotlin prevents this critical failure by making mutable collections strictly invariant.

Production Architecture — Covariant Producers and Contravariant Consumers:
```kotlin
// 1. Covariance (out): Producer interface for read-only UI state
interface StateProducer<out T> {
    fun produceCurrentState(): T // Allowed: T is in 'out' return position
    // fun update(item: T) // Compile Error: T cannot be in 'in' position!
}

// 2. Contravariance (in): Consumer interface for handling actions
interface ActionConsumer<in T> {
    fun consumeAction(action: T) // Allowed: T is in 'in' argument position
    // fun getLatest(): T // Compile Error: T cannot be in 'out' position!
}

// Safe polymorphic assignment in ViewModel
fun observeState(producer: StateProducer<Animal>) {
    val animal = producer.produceCurrentState()
}

fun main() {
    val dogProducer: StateProducer<Dog> = object : StateProducer<Dog> {
        override fun produceCurrentState() = Dog()
    }
    // Allowed because StateProducer is covariant (out)
    observeState(dogProducer) 
}
```

Bytecode Decompilation Verification:
Decompiling Kotlin variance declarations to Java reveals that JVM generics are completely erased to their upper bound (`Object` or the declared constraint):
```java
// Kotlin: interface StateProducer<out T : Animal>
// Compiled Java bytecode:
public interface StateProducer {
    Animal produceCurrentState();
}
```
At the call site, kotlinc emits synthetic `checkcast` instructions to guarantee type safety without runtime reflection.

## Explanation in Arabic

الـ Generics والـ Variance في Kotlin بتحدد إزاي الأنواع الفرعية (Subtypes) بتتعامل لما تتغلف جوه Generics:

1. الـ Invariance (الوضع الافتراضي):
   لو `Dog` بترث من `Animal`، فـ `List<Dog>` **مش** Subtype من `List<Animal>`. ده لمنع كوارث زي كتابة `Cat` جوه قائمة `Dogs`!

2. الـ Covariance (`out`):
   - الكلاس بيعمل **إنتاج للبيانات فقط (Producer Only)**.
   - الـ `out T` بتسمح إن `List<Dog>` تكون Subtype من `List<Animal>`.
   - القاعدة: تقدر تقرأ `T` (Return Type)، لكن مستحيل تدخله كـ Parameter (ممنوع في الـ `in` position). مثال: `List<out E>` في Kotlin هي Read-Only.

3. الـ Contravariance (`in`):
   - الكلاس بيعمل **استهلاك للبيانات فقط (Consumer Only)**.
   - الـ `in T` بتعكس العلاقة: `Comparable<Animal>` بتعتبر Subtype من `Comparable<Dog>` (لأن اللي يقدر يقارن أي حيوان يقدر يقارن الكلاب بالتأكيد).
   - القاعدة: تقدر تمرر `T` كـ Parameter، لكن مينفعش ترجعه.

4. الـ Star Projection (`*`):
   بتستخدمها لما متعرفش أو ميهمكش النوع الدقيق للـ Generic (زي `List<*>`)؛ ده بيعادل `List<out Any?>`، يعني تقدر تقرأ منها بأمان كـ `Any?` لكن مستحيل تكتب فيها.

## Practical walkthrough

في معمارية أندرويد:
- الـ StateFlow والـ LiveData هي Covariant (`StateFlow<out T>`): ده بيسمح إن `StateFlow<UserUiState.Success>` تتمرر لدالة مستنية `StateFlow<UserUiState>` بدون أي مشاكل.
- في الـ Repository، واجهة القراءة فقط بنعمل لها Covariant:
  `interface ReadOnlyRepository<out T> { fun getById(id: String): T }`
- بينما الـ Serializer أو الـ Consumer بنعمل له Contravariant:
  `interface JsonWriter<in T> { fun write(item: T): String }`
- الخطأ الشائع: محاولة وضع دالة `fun update(item: T)` داخل واجهة متعلمة بـ `out T`؛ المترجم هيرفض البناء فوراً: "Type parameter T is declared as 'out' but occurs in 'in' position".

## Why it matters and how it works

Variance lets an API expose flexible subtyping without runtime corruption. Read-only producers and write-only consumers have different safe directions. Use-site projections help when the generic type itself is invariant but one operation has a limited role.

## Worked example

Runnable JVM illustration: a source of cats can be consumed as a source of animals.
```kotlin
open class Animal
class Cat : Animal()
interface Source<out T> { fun get(): T }
class CatSource : Source<Cat> { override fun get() = Cat() }
fun inspect(source: Source<Animal>) = println(source.get() is Cat)
fun main() = inspect(CatSource())
```

## Trade-offs and decision criteria

Declare variance on interfaces with stable producer/consumer roles. Use a projection at a method boundary when the role is temporary. Avoid casts to force subtype relationships; they can move a type error to runtime. Star projections are useful for introspection but sacrifice write precision.

## Failure modes

A mutable `Box<Cat>` treated as `Box<Animal>` would allow inserting a Dog, breaking the Cat reader. Kotlin invariance prevents this. Another mistake is assuming `List<*>` permits arbitrary additions; its element type is unknown.

## Production perspective

A repository returns `Flow<out DomainEvent>`-like producer contracts where consumers only read events; command handlers accept contravariant processors. Public APIs name producer/consumer roles rather than leaking mutable generic containers.

## Interview answer — short

Variance governs subtyping between generic types. Invariance (default) means Box<Dog> is unrelated to Box<Animal>, protecting mutable containers from type pollution. Covariance (out) marks a producer where List<Dog> is a subtype of List<Animal>, allowing T only as a return type. Contravariance (in) marks a consumer where Consumer<Animal> is a subtype of Consumer<Dog>, allowing T only as a parameter. Star projections (*) represent safely readable unknown types.

## Interview answer — structured

Variance determines whether generic types preserve, invert, or ignore the subtyping relationships of their underlying type parameters. The default in Kotlin is invariance, which ensures that a mutable container holding a derived type cannot be assigned to a reference expecting a base type, preventing runtime heap corruption.

Kotlin elegantly divides roles into producers and consumers. When a type only produces values, marking it with out makes it covariant, so a List of Dog can be safely passed where a List of Animal is expected. Conversely, when a type only consumes values, marking it with in makes it contravariant, allowing a general Animal consumer to handle specific Dog events.

In production, declaration-site variance drastically reduces code verbosity compared to Java's wildcard syntax.

Senior engineers model reactive streams like StateFlow as covariant producers, design event sinks and comparators as contravariant consumers, and utilize star projections when inspecting generic payloads whose exact type argument is irrelevant.


## Interview answer — deep senior

A deep exploration of variance reveals how Kotlin's type system provides mathematical soundness while compiling down to Java's type-erased bytecode. On the JVM, all generic type parameters are erased at compile time to their declared upper bound (or java.lang.Object). Consequently, variance in Kotlin is an entirely static compiler enforcement mechanism that does not exist at runtime on the ART virtual machine.

The necessity of invariance stems directly from the Liskov Substitution Principle applied to mutable heap memory. If a mutable container MutableList<Dog> were assignable to MutableList<Animal>, a caller could insert a Cat into the list through the Animal reference. Because both references point to the exact same physical heap array, the original Dog reader would encounter a ClassCastException upon dereferencing the Cat as a Dog. By enforcing strict invariance on mutable structures, kotlinc eliminates heap pollution entirely at compile time.

Covariance (out) allows subtyping (Sub<Derived> is a subtype of Sub<Base>) by strictly forbidding the type parameter from appearing in mutable input positions. In bytecode, the compiler ensures that no method accepts a T parameter, meaning the internal state can never be modified from the outside. When a caller reads from a covariant interface, kotlinc inserts an explicit checkcast instruction casting the erased Object return type to the expected call-site type.

Contravariance (in) reverses subtyping (Sub<Base> is a subtype of Sub<Derived>) by restricting the type parameter strictly to input positions. A classic architectural example is Comparator<in T>: a Comparator<Animal> that compares animals by age can safely sort a List<Dog>, because any operation performed on an Animal is valid on a Dog.

Kotlin's declaration-site variance represents a massive architectural leap over Java's use-site wildcards (? extends T and ? super T). In Java, every consumer method signature must declare wildcards (such as void process(List<? extends Animal> list)), whereas Kotlin allows declaring interface List<out E> once at the declaration site, making all consuming code clean and idiomatic.

## How to answer in the interview

- **Why:** Preserve type safety in generic collections and interfaces while enabling flexible subtyping.
- **How:** Use declaration-site variance: `out` for producers (covariance) and `in` for consumers (contravariance).
- **Trade-offs:** Covariant types (`out T`) cannot accept `T` as a method argument; contravariant types (`in T`) cannot return `T`.
- **Failure cases:** Bypassing variance rules via `@UnsafeVariance` incorrectly, causing `ClassCastException` at runtime when writing incompatible types to a collection.
- **Production solution:** Design read-only domain interfaces as covariant (`Producer<out T>`) and event/sink handlers as contravariant (`Consumer<in T>`), using star projections (`*`) when element type is irrelevant.

## Deep-dive talking points

Explain PECS-style producer/consumer reasoning, type erasure, use-site projections, and why mutable lists are invariant.

## Follow-up questions

- **Interviewer:** "Why is Kotlin's `List<T>` covariant (`out T`), while `MutableList<T>` is invariant?"
  **Answer:** "`List<T>` is read-only, meaning it only produces items. Passing `List<Dog>` to a function expecting `List<Animal>` is completely type-safe because callers can only read `Animal` instances. `MutableList<T>` allows writing: if `MutableList<Dog>` could be passed as `MutableList<Animal>`, a caller could add a `Cat` to it, crashing the app when retrieving a `Dog` later."

- **Interviewer:** "What is the difference between `List<*>` and `List<Any>`?"
  **Answer:** "`List<Any>` requires a list parameterized specifically with `Any` (or subtypes if covariant). `List<*>` represents a list of an unknown type. You can read from `List<*>` safely as `Any?`, but you cannot add anything into it (except null, if permitted). It acts as an abstraction over any list type regardless of its generic argument."

- **Interviewer:** "What is `@UnsafeVariance`, and why is it used in `Collection.contains(element: @UnsafeVariance E)`?"
  **Answer:** "In `Collection<out E>`, `E` is covariant. However, `contains(element: E)` takes `E` in an input position, which violates covariance rules. In reality, `contains` only reads the element to call `.equals()` and never mutates the collection. `@UnsafeVariance` suppresses the compiler error where the author mathematically proves that the operation is safe."

## Self-check rubric

Predict safe assignment direction for producer and consumer, reject a mutable-container cast, and describe one star-projection limitation.

## References and reviewed-on date

- [Kotlin generics](https://kotlinlang.org/docs/generics.html) — variance and star projections.

Technically reviewed against primary documentation on 2026-10-13.

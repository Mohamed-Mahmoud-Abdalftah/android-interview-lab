---
id: "KOT-15"
question: "What is delegation? Compare interface delegation and delegated properties."
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "B"
phase: 1
priority: "P1"
order: 15
editorial_status: "reviewed"
---

# KOT-15

## Original interview question

What is delegation? Compare interface delegation and delegated properties.

## What the interviewer evaluates

Separate interface implementation forwarding from property access delegation and discuss ownership.

## Explanation in Arabic

Kotlin delegation ليها صورتين مختلفتين. `class X(service: Service) : Service by service` تخلي compiler يولّد forwarding لعضو interface ناحية object تاني؛ لو عملت override لعضو في X، ده العضو اللي العميل يشوفه. Delegated property زي `val x by lazy { ... }` بتسند `getValue`/`setValue` لـdelegate. الاتنين يقللوا boilerplate لكن ماينقلوش lifecycle أو thread-safety تلقائيًا. انتبه إن delegate object اللي اتاخد وقت construction هو اللي بيستقبل forwarding، ومش لازم يشوف overrides من wrapper كأنها virtual call داخلية.

## Why it matters and how it works

Interface delegation favors composition over hand-written forwarding. Property delegation abstracts storage or computation of a property. Both hide generated calls, so understanding which object owns state and when it is initialized is essential.

## Worked example

JVM example: wrapper forwards `read` while replacing `label`.
```kotlin
interface Store { fun read(): String; fun label(): String }
class MemoryStore : Store {
    override fun read() = "value"
    override fun label() = "memory"
}
class LoggingStore(private val delegate: Store) : Store by delegate {
    override fun label() = "wrapped ${delegate.label()}"
}
fun main() = println(LoggingStore(MemoryStore()).label())
```

## Trade-offs and decision criteria

Use interface delegation when most methods should forward unchanged; write explicit forwarding when behavior must be audited per method. Use property delegates for consistent access semantics such as lazy initialization or observable state, but avoid magic that hides expensive I/O in a getter.

## Failure modes

A wrapper overrides `label` and assumes calls made inside the delegate’s `read` will dispatch to the wrapper override. The delegate is a separate object, so that assumption fails. Another risk is a property delegate retaining a View after its lifecycle ends.

## Production perspective

A metrics wrapper delegates a storage interface and overrides selected methods to record latency. It documents which calls are instrumented and uses constructor-injected, lifecycle-appropriate storage. Sensitive fields are excluded from logs.

## Interview answer — short

Interface delegation generates forwarding to another object; delegated properties outsource getter/setter behavior to a delegate such as `lazy`. Both are composition tools, but neither automatically changes ownership, thread safety, or internal dispatch.

## Interview answer — structured

`by` can mean two related but distinct things. For `Store by delegate`, the wrapper implements an interface by forwarding unoverridden members. For `val parser by lazy`, property access is handled by a delegate protocol. I use the first to avoid repetitive adapters and the second for a clear access policy. I still inspect lifecycle and forwarding behavior, especially when overrides are expected to affect calls made inside the delegate. Interface delegation lets a wrapper forward most methods to a collaborator while overriding only the methods that add policy, such as metrics. Both reduce repetitive code, but I still inspect which object owns the state and whether expensive work is hidden behind a getter.

## Interview answer — deep senior

Interface delegation is compile-time generated forwarding to a specific object. Wrapper overrides affect calls through the wrapper, but calls internal to the delegate remain on the delegate. Property delegation is a getter/setter protocol and can represent lazy, observable, or map-backed state. Both can conceal work behind syntax, so I keep expensive or blocking behavior visible in names and contracts. In Android I check that delegates do not retain Activity or View references beyond their owner. Consider a logging wrapper implementing a storage interface with `by delegate`. Kotlin generates forwarding for methods I do not override, so the wrapper is concise. That matters for authorization, metrics, and testing. Delegated properties use a protocol for reads and writes, with `lazy` as a common example. A custom delegate could hide a database access in a property getter, which would be surprising on Android Main. I would document thread and lifetime behavior, inject collaborators with a suitable owner, and avoid retaining a View or Activity in a delegate that outlives it. Composition helps design only when forwarding semantics remain clear.

## Deep-dive talking points

Explain generated forwarding, wrapper override behavior, `getValue`/`setValue`, delegate lifetime and testing.

## Follow-up questions

- [KOT-10](../kot-10/): What is `lazy`? **Answer:** a property delegate that computes and caches on first access.
- [KOT-05](../kot-05/): Why prefer a delegated wrapper over inheritance? **Answer:** it composes behavior without requiring the wrapped class to be open.

## Self-check rubric

Give an example of each delegation form, predict an override/internal-call result, and name a lifecycle risk.

## References and reviewed-on date

- [Kotlin delegation](https://kotlinlang.org/docs/delegation.html) — interface forwarding.
- [Kotlin delegated properties](https://kotlinlang.org/docs/delegated-properties.html) — property delegate protocol.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets; no Android device claim is made.

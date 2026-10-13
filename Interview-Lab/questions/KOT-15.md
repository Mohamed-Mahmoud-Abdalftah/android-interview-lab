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

## Practical walkthrough

لو `LoggingStore : Store by delegate`، compiler بيولّد forwarding للـStore methods للـdelegate المحدد. الـwrapper يقدر يعمل override لـ`read` عشان metrics، بس لو implementation جوه delegate نادت method من نفسها، مش هتعدّي على override بتاع الـwrapper؛ راجع call path. property delegation زي `val config by lazy { load() }` آلية مختلفة: delegate بيتحكم في `getValue`/`setValue`، مش بيطبّق interface بالكامل. في production استخدم interface delegation للـdecorator صغير، لكن لو السياسة فيها state وانتقالات معقدة اكتب forwarding واضح عشان ما تختفيش side effects.

## Trade-offs and decision criteria

Use interface delegation when most methods should forward unchanged; write explicit forwarding when behavior must be audited per method. Use property delegates for consistent access semantics such as lazy initialization or observable state, but avoid magic that hides expensive I/O in a getter.

## Failure modes

A wrapper overrides `label` and assumes calls made inside the delegate’s `read` will dispatch to the wrapper override. The delegate is a separate object, so that assumption fails. Another risk is a property delegate retaining a View after its lifecycle ends.

## Production perspective

A metrics wrapper delegates a storage interface and overrides selected methods to record latency. It documents which calls are instrumented and uses constructor-injected, lifecycle-appropriate storage. Sensitive fields are excluded from logs.

## Interview answer — short

Interface delegation forwards an implemented interface to another object, while delegated properties hand property access to a delegate such as `lazy`. I use the first for small wrappers and the second for a specific storage or initialization rule. I still inspect forwarding behavior.

## Interview answer — structured

With `class LoggingStore(private val base: Store) : Store by base`, Kotlin generates forwarding members for the interface, and I can override selected methods in the wrapper. That is useful for a lightweight decorator. It is not the same as `val parser by lazy { ... }`, where a property delegate controls access to one property through the delegate protocol. A subtle wrapper issue is that calls made inside `base` stay inside `base`; they do not automatically dispatch through the wrapper override. In production I would test the observed call path and prefer explicit composition when instrumentation or policy is complex.

## Interview answer — deep senior

Interface delegation is compile-time generated forwarding to a specific object. Wrapper overrides affect calls through the wrapper, but calls internal to the delegate remain on the delegate. Property delegation is a getter/setter protocol and can represent lazy, observable, or map-backed state. Both can conceal work behind syntax, so I keep expensive or blocking behavior visible in names and contracts. In Android I check that delegates do not retain Activity or View references beyond their owner.

A logging decorator built with `Store by delegate` is useful when only one or two methods need interception, but I would test whether the call is made through the wrapper or internally by the delegate. Internal delegate calls do not re-enter wrapper overrides, which can silently omit metrics or policy. A property delegate such as `lazy` solves a different problem: it owns access to one property through `getValue`, not every method of an interface. In production I would make blocking storage work obvious in names, avoid delegates retaining a screen Context, and switch to explicit composition if behavior becomes complex.

## How to answer in the interview

- **Why:** Prefer composition over inheritance by delegating interface implementations or property storage.
- **How:** Use class delegation (`class SecureRepo(base: Repo) : Repo by base`) and property delegates (`by lazy`, `by Delegates.observable`, custom delegates).
- **Trade-offs:** Class delegation only delegates interface methods; internal calls within the delegate cannot see overrides in the delegating class.
- **Failure cases:** Accessing a delegated property before its backing mechanism is configured, or writing heavy side-effects inside property delegate getters.
- **Production solution:** Use interface delegation for transparent decorator patterns (e.g., adding logging or caching), and custom property delegates for reusable Android preference or bundle bindings.

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

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets; no Android device claim is made.

---
id: "SOL-14"
question: "How does Hilt support dependency wiring without automatically guaranteeing DIP?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "B"
phase: 2
priority: "P1"
order: 185
editorial_status: "reviewed"
---

# SOL-14

## Original interview question

How does Hilt support dependency wiring without automatically guaranteeing DIP?

## What the interviewer evaluates

Can the candidate separate graph construction from source dependency direction, inspect a useful contract rather than an interface name, and state what Hilt or Gradle actually verifies?

## Concept and technical explanation

Hilt generates and validates an object graph: it knows how to provide constructor-injected types, interface bindings, component lifetimes, and scoped instances. Dependency Inversion Principle (DIP) concerns the direction of source dependencies around high-level policy. Hilt can wire a ViewModel directly to a network adapter if both types are visible; the graph may compile while presentation policy is coupled to transport details. Conversely, a manual composition root can wire a policy to a stable port without Hilt.

`@Binds` maps an implementation to an interface, but an interface named `UserRepository` is not automatically a good policy boundary. If it exposes Retrofit `Response`, Room entities, or network-specific error codes, the caller still knows about those details. Inspect the method signatures, imports, Gradle dependencies, and ownership of the contract. A useful port represents the operation and data the high-level policy needs; the data adapter implements it and maps transport types at the edge.

## Practical walkthrough (English)

A checkout eligibility rule needs a domain-facing status. If a ViewModel or use case imports `RetrofitEligibilityApi`, Hilt may inject it, but a change in the transport model can reach policy code. Define `EligibilitySource` in a policy-facing module and an adapter in the data module. A Hilt binding in an assembly-visible module maps adapter to port. For a small app, the same boundary can be wired manually. The design decision is the boundary; Hilt only creates its objects.

## Explanation in Arabic

Hilt بتبني وتتحقق من Object Graph: تعرف تنشئ Dependencies وتربط Interface بتنفيذ وتدير Scopes. لكن DIP سؤال عن اتجاه اعتماد الكود ومعنى الـ Contract. لو UseCase بتستورد Retrofit `Response`، كتابة `@Binds` لواجهة بترجع نفس الـ `Response` ما عزلتش الـ policy. خلّي الـ Contract تعبر عن احتياج الـ policy، والـ Data Adapter تترجم تفاصيل الشبكة عند الحد. وبص على Imports وGradle Dependencies، مش اسم الـ Interface بس.

## Why it matters and how it works

Compile-time graph validation catches missing or cyclic bindings, not poor domain boundaries. If a feature only compiles against a policy-facing contract, accidental direct imports of data internals become harder. The app assembly still needs access to both the binding and implementation. Dependency boundaries may improve change isolation, but a source or public API change can still trigger compilation; do not promise a fixed build-time gain.

## Worked example

Runnable Kotlin/JVM boundary independent of Android. In an Android app, a Hilt `@Binds` method in an assembly-visible module could map `NetworkEligibilitySource` to `EligibilitySource`:

```kotlin
interface EligibilitySource {
    suspend fun status(customerId: String): Eligibility
}

data class Eligibility(val allowed: Boolean, val reason: String?)

class CheckEligibility(private val source: EligibilitySource) {
    suspend fun forCustomer(customerId: String): Eligibility =
        source.status(customerId)
}

class NetworkEligibilitySource(
    private val fetch: suspend (String) -> Pair<Boolean, String?>
) : EligibilitySource {
    override suspend fun status(customerId: String): Eligibility {
        val (allowed, reason) = fetch(customerId)
        return Eligibility(allowed, reason)
    }
}
```

The policy type imports no transport or Hilt annotation. Hilt wiring would live outside this code; this JVM example does not claim an Android Hilt component was built or tested.

## Trade-offs and decision criteria

Hilt reduces repeated construction and provides scopes, at the cost of generated graph configuration and build tooling. A policy-facing interface adds an adapter and mapping work. Use one where it protects a meaningful change boundary; avoid creating an interface for every class by reflex. `@Binds` is appropriate for a constructor-injected implementation of an interface; `@Provides` supplies a value when construction needs code or comes from a third-party API. Neither annotation judges architectural quality.

## Failure modes

A `Repository` interface returns Retrofit `Response<Dto>`, so the use case still branches on HTTP status. An `@Binds` method compiles while this coupling survives. Another failure is installing the binding in a component that cannot satisfy its dependencies or lacks the needed lifetime; Hilt can catch graph errors, while scope suitability still needs design review. Do not claim all concrete dependencies violate DIP: a stable value or policy type can be concrete.

## Production perspective

For eligibility, keep approval authority on the server. The client-side rule reads a domain status from `EligibilitySource`, while an adapter maps network responses. A JVM test can inject a fake port to test local policy; adapter integration tests still need real serialization and failure handling. Review module imports in code review and use dependency rules where the repository benefits from them.

## Interview answer — short

Hilt builds and validates the dependency graph; DIP concerns which way high-level policy depends on implementation details. Hilt can inject a concrete network class into a ViewModel and compile successfully. `@Binds` helps connect an interface to an adapter, but the interface must expose a policy-facing contract rather than transport DTOs. I check the actual imports and method signatures, not the annotation alone.

## Interview answer — structured

I separate two questions. Hilt answers, “How do I construct and scope these objects?” DIP asks, “Does high-level policy know about a low-level detail?” A Hilt graph can be valid while a use case directly imports Retrofit types. An `@Binds` interface is not enough if its methods still return `Response<Dto>`; that just moves the coupling behind a name.

For an eligibility flow I would define a small policy-facing `EligibilitySource` whose result uses domain terms. A data adapter maps network responses into that result, and Hilt binds the adapter to the port in a module visible to the app assembly. A manual composition root could do the same. I inspect imports and module dependencies and test the policy with a fake, then test the adapter separately. I do not promise that this arrangement automatically makes builds faster or eliminates all integration tests.

## Interview answer — deep senior

Hilt provides generated component graphs, binding resolution, and lifecycle scopes. It can tell us a constructor dependency is missing or a binding graph is invalid. It cannot decide whether a dependency points from high-level business policy toward a transport implementation. A ViewModel can inject a concrete API type and still produce a valid Hilt graph. Equally, manual DI can respect DIP if the policy depends on a stable contract and the composition root supplies its implementation.

I review the contract's ownership and vocabulary. If `EligibilitySource` lives with the policy and returns a domain `Eligibility`, an adapter can translate network data at the edge. If the interface returns Retrofit `Response` or Room entities, the policy remains coupled even when Hilt uses `@Binds`. I also avoid the opposite overcorrection: injecting a concrete immutable value or stable policy class does not automatically violate DIP. The key issue is whether volatile details dictate policy and source dependencies.

In a multi-module Android project, a feature can compile against the contract while a data module implements it and an assembly module sees the binding. That gives the compiler a useful boundary against accidental imports. It does not guarantee that every data change skips feature compilation; public API changes, annotation processing, and Gradle configuration still matter. Hilt scopes also need separate lifecycle review. I test local policy through a fake port and test the network adapter's mapping and errors independently. For a small application where the boundary has little value, manual construction and fewer interfaces may be clearer.

## How to answer in the interview

- Say what Hilt validates and what DIP asks.
- Show a graph that compiles but exposes transport details to policy.
- Repair the contract's ownership and data types, then bind the adapter.
- Mention module visibility, test seams, and the absence of automatic build guarantees.

## Deep-dive talking points

`@Binds` versus `@Provides`; graph validity versus contract semantics; module assembly visibility; transport DTO leakage; lifecycle scope review; fake-based policy tests and adapter integration tests.

## Follow-up questions

- **Interviewer:** “Does `@Binds` guarantee DIP?” **Answer:** “No. It maps an implementation to an interface; the interface can still expose transport details or be owned by the wrong layer.”
- **Interviewer:** “Must every dependency be an interface?” **Answer:** “No. I introduce a port where it protects a meaningful policy boundary, not for every stable value or class.”
- **Interviewer:** “Will this always speed up Gradle builds?” **Answer:** “No. Module boundaries can help isolate some changes, but compilation depends on public APIs, processors, and build configuration.”

## Self-check rubric

Can I identify a valid Hilt graph with a bad policy dependency, repair the contract, and avoid universal testing or build claims?

## References and reviewed-on date

- [Android Hilt guide](https://developer.android.com/training/dependency-injection/hilt-android) — graph construction, `@Binds`, `@Provides`, and module visibility.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository and data-source responsibilities.
- [Gradle Java plugin](https://docs.gradle.org/current/userguide/java_plugin.html) — compilation and module boundaries.

Technically reviewed against primary documentation on 2026-10-19.

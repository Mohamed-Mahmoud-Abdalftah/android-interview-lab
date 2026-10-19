---
id: "MOD-11"
question: "How do you manage dependency injection across modules?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 364
editorial_status: "reviewed"
---

# MOD-11

## Original interview question

How do you manage dependency injection across modules?

## What the interviewer evaluates

Explain Hilt binding visibility across regular Gradle modules, contract and implementation ownership, scope and qualifier choices, variant verification, and the Dagger component dependency bridge required for Play dynamic feature modules.

## Concept and technical explanation

For regular Gradle modules, the module compiling the `Application` class must see Hilt modules and constructor-injected classes through transitive dependencies. A contract can live in an API/domain module; its implementation and `@Binds` declaration live near their owner or in app composition where variant selection belongs. `@InstallIn` selects a Hilt component; a scoping annotation controls instance reuse within that component. Qualifiers distinguish bindings of the same type. A Play dynamic feature reverses the dependency direction, so base Hilt processing cannot simply aggregate its annotations. Android's documented bridge declares an `@EntryPoint` in an app-visible module and a Dagger component in the dynamic feature depending on that entry point.

## Practical walkthrough (English)

`:core:session:api` declares `SessionSource`; `:data:session` implements it and provides a Hilt binding. Checkout requests the contract. The app includes the implementation module for the relevant variant and checks the qualifier and scope. A dynamic scanner feature obtains base dependencies through an app-visible `@EntryPoint`, then injects its own objects using a Dagger component with that entry point as a component dependency. Merely calling `EntryPoints.get` does not assemble the feature's full injection graph.

## Explanation in Arabic

في Regular Gradle Modules، Hilt تقدر تجمع الـ bindings لو module اللي بتبني `Application` شايفة Hilt modules والـ `@Inject` classes عبر Transitive Dependencies. حط Contract مثل `SessionSource` في API/Domain Module مناسبة، والتنفيذ والـ `@Binds` قريبين من Data Module أو Composition Module حسب Ownership. `@InstallIn` تختار Component Lifetime؛ `@Singleton` مش اختيار افتراضي لكل شيء. لو فيه Implementations متعددة استخدم Qualifier واضح وافحص Binding كل Variant.

Play Dynamic Feature مختلفة لأن اتجاه اعتماد Gradle معكوس: الـ base app ما بتشوفش annotations الموجودة داخلها بنفس الطريقة. التوثيق الرسمي يقترح `@EntryPoint` في app أو module تعالجها Hilt، وDagger Component في Dynamic Feature يعتمد على الـ EntryPoint، ثم تُحقن كائنات الميزة عبر الـ component ده. مجرد `EntryPoints.get` يجيب Dependencies من الـ base graph؛ مش بيعمل حقن لكل Graph الميزة تلقائيًا.

## Practical walkthrough

مثال Session: `:core:session:api` تعرّف `SessionSource`، و`:data:session` توفر `RealSessionSource` وHilt `@Binds`. `:feature:checkout` تطلب العقد في constructor، و`:app` تعتمد على modules اللازمة للـ variant. لو Release تستخدم SessionSource مختلفة عن Debug، افحص Qualifiers والـ bindings في كل Variant. في Dynamic Scanner Feature، حدد Base Dependencies المطلوبة في `@EntryPoint` داخل module مرئية لـ Hilt، ثم ابنِ Dagger Component تعتمد عليها داخل الميزة. اختبر Assembly الفعلي ومسار فتح الميزة، مش Unit Test للـ constructor فقط.

## Why it matters and how it works

Hilt does not infer bindings from module names. Gradle classpath visibility determines the graph available at compilation. A binding can exist but select the wrong business implementation or live for the wrong component lifetime. Tests should distinguish consumer behavior with a fake from assembling each important app variant and dynamic-feature path.

## Worked example

This Kotlin/JVM contract shows direct fake construction for a consumer test. It does not compile or verify an Android Hilt graph.

```kotlin
interface SessionSource { fun currentUserId(): String? }
class CheckoutAccess(private val sessions: SessionSource) {
    fun canCheckout(): Boolean = sessions.currentUserId() != null
}
class FixedSession(private val userId: String?) : SessionSource {
    override fun currentUserId() = userId
}
fun main() {
    check(CheckoutAccess(FixedSession("u-1")).canCheckout())
    check(!CheckoutAccess(FixedSession(null)).canCheckout())
}
```

## Trade-offs and decision criteria

Bindings near implementations make ownership visible; app-level selection can clarify variants but enlarge composition code. Hilt catches many missing or duplicate known bindings, not semantically wrong release selection. Multibindings are useful for independent contributions to a set or map, not a mandatory multi-module technique. Avoid broad scopes for shorter-lived state.

## Failure modes

An implementation module absent from the app variant yields a missing binding. Two unqualified bindings of the same type conflict. An app-scoped instance retains Activity or stale session data. A Play dynamic feature declares Hilt modules internally and assumes base aggregation can see them. Check transitive classpath, qualifier, scope, and the documented component-dependency bridge.

## Production perspective

Maintain a map from contract to implementation, binding module, qualifier, scope, and variant. Assemble important variants and test their real graph. Unit-test consumers with fakes separately. Exercise a dynamic feature's Dagger component and entry-point path in an Android integration environment; a JVM fake test cannot prove that path.

## Interview answer — short

For regular modules, put a contract where consumers can see it, place implementation and binding with their owner, and ensure the app's transitive dependencies expose Hilt modules and injected classes. Choose scope and qualifier by actual lifetime and variant, then assemble the graph. A Play dynamic feature is different: expose base dependencies through an app-visible `@EntryPoint` and use a Dagger component dependency inside the feature.

## Interview answer — structured

Start with Gradle visibility. In regular modules, the module compiling `Application` needs Hilt modules and constructor-injected classes in its transitive dependencies. I might put `SessionSource` in a contract module and its implementation plus `@Binds` in a data module; checkout requests only the contract and the app includes the right implementation per variant.

Scope and qualifier are separate decisions. A graph can compile and still bind release to a sandbox implementation or keep session state too long. I assemble important variants and test the real graph, while focused JVM tests construct the consumer with a fake.

A Play dynamic feature has inverted module dependencies. Base Hilt processing does not handle its annotations like a regular library module. The Android-documented solution declares an `@EntryPoint` in an app-visible module, then creates a Dagger component in the feature that depends on it. Reading one dependency with `EntryPoints.get` alone does not inject the feature graph.

## Interview answer — deep senior

Multi-module DI begins with compile-time visibility. Hilt code generation requires the module compiling `Application` to have all Hilt modules and constructor-injected classes in its transitive dependencies. Then decide ownership: checkout imports a `SessionSource` contract; a data module provides `RealSessionSource` and the binding, or app composition owns the binding when variant selection is best expressed there. The source dependency direction should remain explicit.

`@InstallIn(SingletonComponent::class)` places a binding in the component; `@Singleton` scopes instance reuse to that component. Neither is an automatic choice for every repository. An app-scoped instance holding Activity Context or per-user session state may outlive its owner. Qualifiers distinguish same-type bindings, yet a correctly typed release binding can still point to a sandbox implementation. Compile and smoke-test important variants.

A Play dynamic feature differs from a regular Gradle library. It depends on the base app, so the base cannot aggregate annotations from the feature through its normal transitive graph. Android's documented pattern declares an `@EntryPoint` in app or another Hilt-processable module, creates a Dagger component in the dynamic feature that depends on it, and uses that component for injection. `EntryPointAccessors.fromApplication` can obtain base dependencies for an application component; it is not by itself the feature's injector.

Construct a consumer such as `CheckoutAccess` with a fake `SessionSource` in JVM unit tests to verify its decisions. Separately assemble the app graph for each significant variant and exercise the dynamic-feature injection path in Android integration tests. Use set or map multibindings only when independent modules genuinely contribute extensions. Hilt's compile checks prove graph completeness for visible bindings, not lifetime or business correctness.

## How to answer in the interview

- **Regular modules:** transitive Hilt visibility, contract, implementation and binding ownership.
- **Correctness:** scope, qualifier and variant tests.
- **Dynamic feature:** app-visible `@EntryPoint` plus a Dagger component dependency in the feature.
- **Testing:** consumer fake test does not prove Android graph assembly.

## Deep-dive talking points

Transitive Gradle dependencies, Hilt aggregation, `@Binds`, `@InstallIn`, scopes, qualifiers, variants, dynamic-feature entry points and Dagger component dependencies, optional multibindings.

## Follow-up questions

- **Interviewer:** "Is `@EntryPoint` alone enough to inject a Play dynamic feature?"
  **Answer:** "It exposes dependencies from base Hilt. The documented approach also builds a Dagger component in the dynamic feature depending on that entry point and uses it to inject feature objects."

- **Interviewer:** "How can a graph compile yet be wrong?"
  **Answer:** "A valid qualifier may select a sandbox implementation in release, or an app-scoped object may retain a shorter-lived session. Test variants and lifetimes."

## Self-check rubric

Explain Hilt's transitive visibility, locate binding and contract owners, choose scope and qualifier, and describe both parts of the dynamic-feature bridge.

## References and reviewed-on date

- [Hilt in multi-module apps](https://developer.android.com/training/dependency-injection/hilt-multi-module) — classpath and feature-module bridge.
- [Hilt on Android](https://developer.android.com/training/dependency-injection/hilt-android) — component bindings.
- [Dagger multibindings](https://dagger.dev/dev-guide/multibindings.html) — optional contributions.

Technically reviewed against primary documentation on 2026-10-19.

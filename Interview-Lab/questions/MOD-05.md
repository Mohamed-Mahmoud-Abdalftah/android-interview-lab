---
id: "MOD-05"
question: "Compare Gradle api and implementation dependencies."
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "A"
phase: 4
priority: "P1"
order: 358
editorial_status: "reviewed"
---

# MOD-05

## Original interview question

Compare Gradle api and implementation dependencies.

## What the interviewer evaluates

- Explain consumer compile classpath and public ABI exposure.
- Choose `api` only when public signatures require it.
- Connect choice to rebuild fan-out and published metadata.

## Explanation in Arabic

`implementation` dependency تستخدمها module داخليًا، ولا تعرض types الخاصة بها على compile classpath للمستهلكين كجزء من API. `api` تصدّر dependency للمستهلكين؛ تحتاجها لو public method أو superclass/interface في module يكشف type من تلك المكتبة. مثلًا لو `:core:ui` public function تأخذ `SomeLibraryType` فالمستهلك يحتاج المكتبة عند compilation. استخدم `implementation` افتراضيًا و`api` عند عقد فعلي؛ الإفراط في `api` يكبر classpath ويجعل تغييرات أكثر تعيد compilation. الحكم يتأثر بـGradle/AGP variant model وABI الفعلي.

## Why it matters and how it works

Gradle separates a library's API dependencies from internal implementation dependencies. Consumers compile against exported API classpaths, while runtime still includes required implementation dependencies. Hiding an internal dependency reduces accidental imports and can avoid consumer recompilation when the implementation changes. Publishing metadata conveys the distinction to downstream builds where supported.

## Worked example

`:core:images` exposes `fun load(url: String): ImageResult` and uses OkHttp internally: declare OkHttp as `implementation`. If it publicly returns `okhttp3.Response`, that type enters its ABI and requires `api` or, preferably, a domain-owned result type to avoid leaking transport details. Compare Gradle compile classpaths after changing dependency declaration.

## Trade-offs and decision criteria

`api` can be necessary for a genuine public type but expands consumer knowledge and build fan-out. Hiding a type behind a stable facade costs adapter code yet preserves implementation freedom. Do not change a required API dependency to implementation just to chase build speed; consumers must still compile correctly.

## Failure modes

A public signature refers to a type hidden as `implementation`, breaking consumers. Everything is declared `api`, so downstream modules import internal libraries and rebuild broadly. A library POM misrepresents needed compile types. A feature relies on a transitive import rather than declaring its own direct dependency.

## Production perspective

Inspect public ABI and dependency insight reports, enforce explicit direct dependencies, and benchmark incremental builds. Review any newly added `api` edge because it is a product of the library contract, not merely a local build choice.

## Interview answer — short

“`api` exports a dependency on the consumer compile classpath; `implementation` keeps it internal. I use `api` only when its types are part of my public ABI.”

## Interview answer — structured

“If my module uses OkHttp privately, I declare `implementation`; the app gets it at runtime without compiling against OkHttp as my module's API. If a public function exposes `okhttp3.Response`, consumers need that type and an `api` declaration, though I may redesign the API to avoid transport leakage. Narrow implementation classpaths improve encapsulation and can reduce recompilation. I verify the actual public signatures and published metadata rather than flipping configurations by habit.”

## Interview answer — deep senior

“I frame `api` and `implementation` as a compile-contract decision. A library's public ABI may include parameters, return types, supertypes or annotations from another dependency; in that case consumers must see the dependency on their compile classpath, so `api` is appropriate. If the dependency only helps implement private behavior, `implementation` keeps it off that consumer compile classpath while preserving runtime availability. For an image module using OkHttp internally, I prefer a stable image result type and `implementation` for the client. Publicly returning an OkHttp Response would make the network library part of every consumer's contract, complicating replacement and widening recompilation. I do not use `implementation` to hide a type that genuinely appears in public signatures, because consumers can fail to compile. I inspect Gradle's dependency graph and published metadata, add direct dependencies rather than leaning on accidental transitive exposure, and measure incremental build impact. The default is a narrow API, but correctness of the ABI comes first.”

## Deep-dive talking points

Discuss ABI, consumer classpath, runtime availability, POM metadata, transitive import and compile fan-out.

## Follow-up questions

- Does `implementation` mean absent at runtime? **Answer:** no; it is internal to the consumer compile API, not necessarily missing at runtime.
- When is `api` required? **Answer:** when the dependency's types are exposed in the public ABI.
- Why wrap an OkHttp response? **Answer:** to avoid leaking a transport library into a stable feature contract.

## Self-check rubric

Classify two dependencies, inspect a public signature, and explain consumer recompilation impact.

## References and reviewed-on date

- [Gradle Java Library Plugin](https://docs.gradle.org/current/userguide/java_library_plugin.html) — API/implementation separation.
- [Android modularization patterns](https://developer.android.com/topic/modularization/patterns) — module dependencies.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Android variant behavior should be checked in the project toolchain.
Compare Gradle api and implementation dependencies.

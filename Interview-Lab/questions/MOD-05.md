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

## Concept and technical explanation

In modern Gradle dependency management (via java-library and com.android.library plugins), the implementation and api configurations dictate how dependencies leak across compilation boundaries:
- implementation: Hides the dependency from the compile classpath of downstream consumers. Types from the dependency are available at runtime and to the declaring module at compile time, but any module that imports the declaring module cannot resolve those types. This establishes an ABI (Application Binary Interface) boundary: changes to implementation dependencies do not trigger recompilation of downstream modules, dramatically improving incremental build times.
- api: Transitively exports the dependency onto the compile classpath of all downstream consumers. It is required when a module exposes types from the dependency in its own public method signatures, interfaces, or return types. Overusing api destroys compilation isolation, creating cascading recompilations across the entire build graph whenever the dependency changes.

## Practical walkthrough (English)

Demonstrating compilation isolation between implementation and api in Gradle:
```kotlin
// module: :core:network/build.gradle.kts
dependencies {
    // OkHttp is an internal engine implementation detail
    implementation(libs.okhttp)
    // Retrofit interfaces exposed in public API methods require 'api'
    api(libs.retrofit)
}

// module: :feature:news/build.gradle.kts
dependencies {
    implementation(project(":core:network"))
}

// Inside :feature:news source code:
// val service: Retrofit = ... // COMPILES! (Retrofit is exposed via 'api')
// val client: OkHttpClient = ... // COMPILER ERROR! (OkHttp is hidden via 'implementation')
```

## Explanation in Arabic

المقارنة الجوهرية بين `api` و `implementation` في Gradle وكيف تؤثران على وقت البناء والـ ABI:

1. ما هو الفرق الأساسي؟
   - **`implementation` (خاص بالداخل)**: التبعية متاحة فقط للموديول الحالي أثناء التجميع (Compile Classpath). الموديولات التي تعتمد على هذا الموديول **لا ترى** هذه التبعية ولا تستطيع استيرادها.
   - **`api` (مكشوف للجميع - Transitive Exposure)**: التبعية مكشوفة في الواجهة العامة للـ Module (الـ Public ABI). أي موديول يعتمد على هذا الموديول يرث هذه التبعية تلقائياً في الـ Compile Classpath الخاص به.

2. الأثر الكارثي لـ `api` على وقت البناء (Build Fan-out):
   - لنفترض أن Module C يعتمد على B، و B يعتمد على A.
   - إذا استخدم B كلمة `implementation(A)`: عند تغيير كود داخلي في A، يقوم Gradle بتجميع A ثم B فقط. الموديول C لا يعاد تجميعه لأن الـ ABI الخاص بـ B لم يتغير!
   - إذا استخدم B كلمة `api(A)`: أي تغيير في A يكسر الـ ABI الخاص بـ B، مما يجبر Gradle على إعادة تجميع B و C وجميع الموديولات التابعة لهما في المشروع بالكامل!

3. القاعدة الذهبية لمهندس البرمجيات الأول (Senior Rule of Thumb):
   - **اجعل `implementation` هو الخيار الافتراضي دائماً في 99% من الحالات**.
   - استخدم `api` فقط وفقط إذا كانت كلاسات ودوال الموديول الحالي تُرجع أو تقبل كائنات من التبعية في دوالها العامة (Public Functions or Return Types).

## Practical walkthrough

المقارنة العملية لتأثير `api` مقابل `implementation` على الـ Classpath ووقت البناء:
```kotlin
// 📁 في موديول ':data:user' build.gradle.kts:
dependencies {
    // ✅ استخدام implementation: Retrofit تفصيل داخلي لا يجب أن يراه الـ UI:
    implementation(libs.retrofit)
    
    // لو استخدمنا api(libs.retrofit):
    // أي موديول يعتمد على :data:user سيستورد Retrofit تلقائياً،
    // ولو غيرنا نسخة Retrofit، سيعيد تجميع كل الـ Feature Modules في التطبيق!
}

// 📁 متى يكون استخدام api مبرراً وإلزامياً؟
// في موديول ':core:designsystem' build.gradle.kts:
dependencies {
    // بما أن موديول الـ Design System يُصدر Composables تعتمد مباشرة على Compose UI:
    api(libs.androidx.compose.ui)
    api(libs.androidx.compose.material3)
}
// هنا مبرر لأن أي شاشة تستخدم DesignSystem تحتاج تلقائياً كائنات Compose UI في شاشاتها.
```

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

The implementation configuration keeps a dependency private to the declaring module, preventing downstream consumers from seeing its types at compile time and shielding them from recompilation when internal code changes. The api configuration exports the dependency transitively to consumers, required only when types appear in public signatures but causing cascading rebuilds when overused.

## Interview answer — structured

Understanding the difference between Gradle api and implementation configurations is essential for building performant multi-module architectures.
The implementation configuration keeps the dependency internal to the declaring module.
Types from that library are omitted from the compile classpath of any downstream consumer that depends on the module.
This creates a strict compilation firewall: as long as the module's public ABI remains unchanged, modifications to its implementation dependencies will not trigger recompilations of downstream modules.
Conversely, the api configuration transitively exposes the dependency to the compile classpath of all downstream modules.
You should use api only when types from the underlying library are exposed in the module's public method signatures, interface contracts, or public property definitions.
Defaulting to api is an architectural anti-pattern that tightly couples modules and invalidates the Gradle build cache across the entire project.

## Interview answer — deep senior

At the compiler level, the distinction between api and implementation hinges on the Application Binary Interface boundary.
When Gradle analyzes task dependencies for compileKotlin, it evaluates the compile classpath of each subproject.
By utilizing implementation, a module encapsulates its internal dependencies.
If module B depends on module A using implementation, and module A refactors an internal library or upgrades an implementation dependency, Gradle determines that module A's ABI has not changed.
Consequently, module B's compileKotlin task is marked as UP-TO-DATE, bypassing recompilation entirely.
If module A had declared the dependency using api, Gradle would be forced to assume that module B's compile classpath is dirty, triggering cascading recompilation downstream across dozens of dependent feature modules.
In enterprise multi-module codebases, our governing rule is: default to implementation everywhere.
We only promote a dependency to api when an exported type from that library is an inescapable part of our module's public API contract.
Even then, senior architects prefer wrapping third-party types in internal domain models rather than leaking external library types across module boundaries, preserving complete control over our compilation topology. We enforce this policy through automated static architecture checks in CI, automatically detecting when an implementation dependency is inadvertently exposed and preventing build cache invalidation regressions across downstream feature modules.

## How to answer in the interview

- **Why:** dependency exposure affects coupling.
- **How:** choose api only for public types.
- **Trade-off:** reuse ease versus recompilation.
- **Failure case:** implementation hides required public type.
- **Production solution:** consumer compile and build profile.

## Deep-dive talking points

Discuss ABI, consumer classpath, runtime availability, POM metadata, transitive import and compile fan-out.

## Follow-up questions

- **Interviewer:** "What happens if you use a type from an `implementation` dependency in a public function?"
  **Answer:** "The Kotlin/Java compiler will throw an error or warning because downstream consumers cannot resolve the public signature on their compile classpath."

- **Interviewer:** "Does `implementation` reduce APK final size compared to `api`?"
  **Answer:** "No. Both configurations bundle the library into the final APK's runtime classpath. The advantage of `implementation` is strictly compile-time isolation and build speed."

## Self-check rubric

Classify two dependencies, inspect a public signature, and explain consumer recompilation impact.

## References and reviewed-on date

- [Gradle Java Library Plugin](https://docs.gradle.org/current/userguide/java_library_plugin.html) — API/implementation separation.
- [Android modularization patterns](https://developer.android.com/topic/modularization/patterns) — module dependencies.

Technically reviewed against primary documentation on 2026-10-13.

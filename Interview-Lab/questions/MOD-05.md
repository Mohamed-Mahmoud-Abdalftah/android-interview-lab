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

implementation keeps a dependency private to the module's compile classpath, hiding internal transitive types and preventing downstream recompilations when internals change. api exposes the dependency transitively to all consumers, polluting their classpaths and forcing costly rebuild cascades across all downstream modules.

## Interview answer — structured

The difference between `api` and `implementation` in Gradle determines whether a dependency leaks into the consumer's compile classpath.

First, implementation` (Default Choice) is the dependency is present on the compile classpath of the current module and on the runtime classpath of consumers, but **hidden from the compile classpath of consumers**. If module `B` uses `implementation(A)`, module `C` depending on `B` cannot reference types from `A`. This enforces strict encapsulation and dramatically accelerates incremental compilation. Finally, with api` (Public ABI Exposure), transitively exposes the dependency to any module that depends on this module. If `B` declares `api(A)`, `C` can import symbols from `A` directly.

The golden architectural rule: use `implementation` by default. Only promote a dependency to `api` if its types appear directly in the module's public function parameters, return types, or inherited interfaces (part of its public Application Binary Interface - ABI).


## Interview answer — deep senior

Under the hood, Gradle distinguishes between a module's **Compile Classpath** and its **Runtime Classpath**, optimizing builds via **ABI (Application Binary Interface) hashing**.

When Gradle compiles a module, it generates an ABI hash representing only public and protected method signatures, return types, and fields. Method implementation bodies (private logic inside a function) do not change the ABI hash.

First, when module `B` uses `implementation(A)`, Gradle excludes `A` from `C`'s compile classpath. If a developer changes private code inside `A`, `A` recompiles, but `B`'s ABI remains unchanged, and Gradle completely skips recompiling `C`. Finally, when `B` uses `api(A)`, `A` is part of `B`'s public interface. Any ABI change in `A` invalidates the ABI of `B`, triggering a massive recompile cascade across the entire downstream dependency tree.

Using `implementation` isolates compile boundaries, maximizes Gradle's `UP-TO-DATE` task checks, and keeps developer build loops lightning-fast.


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

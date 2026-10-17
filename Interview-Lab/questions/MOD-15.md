---
id: "MOD-15"
question: "How do api/implementation influence compilation boundaries and rebuilds?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 368
editorial_status: "reviewed"
---

# MOD-15

## Original interview question

How do api/implementation influence compilation boundaries and rebuilds?

## What the interviewer evaluates

- Trace ABI exposure and consumer compile classpath.
- Explain incremental rebuild effects without absolute guarantees.
- Diagnose a concrete high-fan-out dependency change.

## Concept and technical explanation

The distinction between Gradle api and implementation configurations governs compilation avoidance and task up-to-date checking at the bytecode level:
- implementation: Hides transitive dependency types from the downstream consumer's compile classpath, placing them exclusively on the runtime classpath. When internal code within an implementation dependency changes without modifying public method signatures, interfaces, or visible fields, Gradle detects that the declaring module's Application Binary Interface (ABI) remains identical. Downstream consumers are marked UP-TO-DATE, completely bypassing recompilation and preserving build cache performance.
- api: Exposes transitive dependency types onto the compile classpath of every downstream consumer. Any modification to an api dependency—even a minor private method change—forces Gradle to invalidate the compile classpath of all dependent modules, triggering cascading recompilation across the entire build graph. Senior architects enforce implementation by default to maintain resilient compilation firewalls.

## Practical walkthrough (English)

Comparing ABI compilation boundaries between implementation and api:
```kotlin
// In :core:network/build.gradle.kts
dependencies {
    // 1. Implementation keeps OkHttp private to :core:network
    implementation(libs.okhttp)
    // 2. Api exposes Retrofit to all consumers of :core:network
    api(libs.retrofit)
}

// In :feature:checkout/build.gradle.kts
dependencies {
    implementation(project(":core:network"))
}

// Compilation result:
// If OkHttp upgrades from 4.11 to 4.12:
// - :core:network recompiles.
// - :feature:checkout ABI is UNCHANGED; its compileKotlin task is UP-TO-DATE!
// If Retrofit interfaces change:
// - :feature:checkout compile classpath is dirty, forcing full recompilation.
```

## Explanation in Arabic

كيف يؤثر اختيار `api` مقابل `implementation` في Gradle على حدود التجميع (Compilation Boundaries) وإعادة البناء التزايدي (Incremental Rebuilds)؟

1. المفهوم التقني لـ ABI (Application Binary Interface):
   - الـ ABI يمثل الهيكل العام الخارجي للكلاسات: أسماء الدوال العامة (Public Methods)، أنواع المعاملات (Parameter Types)، قيم الإرجاع (Return Types)، والحقول العامة.
   - لا يشمل الـ ABI الكود التنفيذي الداخلي داخل جسم الدوال الخاصة (Private method bodies).

2. ما الذي يحدث عند استخدام `implementation`؟
   - التبعية تكون محصورة داخل الموديول فقط.
   - إذا قمت بتعديل كود داخلي (Private Implementation) في الموديول الأدنى A، يقوم Gradle بإعادة تجميع A فقط.
   - يكتشف Gradle أن الـ ABI الخاص بـ A لم يتغير، فيقوم بعمل **Skip** لتجميع الموديولات B و C المستهلكة (يضع عليها علامة `UP-TO-DATE` أو `FROM-CACHE`).

3. ما الذي يحدث عند استخدام `api` (خطر الـ Rebuild Cascade)؟
   - التبعية تُكشف في الـ Compile Classpath لجميع الموديولات التابعة.
   - أي تغيير في الموديول A يُبطل صلاحية الـ ABI لجميع الموديولات التي تعتمد عليه عبر `api`، مما يجبر Gradle على إعادة تجميع سلسلة الموديولات بالكامل، وهو ما يقتل سرعة التطوير اليومي.

## Practical walkthrough

تجربة عملية توضح سلوك Gradle مع التعديلات في implementation مقابل api:
```kotlin
// السيناريو: لدينا 3 موديولات: :core:network <- :data:auth <- :feature:login

// الحالة 1: استخدام implementation في :data:auth build.gradle.kts:
dependencies {
    implementation(projects.core.network)
}
// إذا قمنا بتعديل دالة خاصة داخل :core:network (مثلاً تحسين لوج الاتصال):
// نتيجة تشغيل ./gradlew :feature:login:assembleDebug:
// > Task :core:network:compileKotlin SUCCESS
// > Task :data:auth:compileKotlin UP-TO-DATE  (لم يُعد تجميعه لأن ABI لم يتغير!)
// > Task :feature:login:compileKotlin UP-TO-DATE (تم التخطي تماماً!)

// الحالة 2: استخدام api في :data:auth build.gradle.kts:
dependencies {
    api(projects.core.network)
}
// أي تعديل في :core:network يُسقط الـ ABI Cache:
// > Task :core:network:compileKotlin SUCCESS
// > Task :data:auth:compileKotlin SUCCESS     (إعادة تجميع إجبارية!)
// > Task :feature:login:compileKotlin SUCCESS (إعادة تجميع إجبارية!)
// الفرق في وقت البناء: من ثانية واحدة إلى 25 ثانية مع كل تعديل بسيط!
```

## Why it matters and how it works

Gradle computes compile inputs per module. API dependencies widen what consumers compile against; internal implementation dependencies need not. An ABI-stable private change can stay local, while modifying exported types invalidates downstream consumers. Android builds add resource and variant tasks, so a graph improvement may not dominate total wall time.

## Worked example

`:core:payments` publicly returns `ProviderResponse` from an SDK declared `api`, causing checkout and orders compile classpaths to include that SDK. Replace the public response with owned `PaymentResult` and declare SDK `implementation`. A private provider adapter update now need not force API consumers to compile against SDK types. Verify task graphs on a warm incremental build.

## Trade-offs and decision criteria

Hiding a dependency stabilizes architecture but adds mapping code. An `api` dependency is correct when public signatures genuinely expose its types. Fewer compile classpath entries can help builds, but module configuration and code generation may still dominate; optimize based on actual build scans.

## Failure modes

A public type remains exposed after switching to implementation and consumer compilation fails. An inline public function leaks an implementation detail. Teams benchmark clean builds only, missing incremental effects. An `api` edge is kept for convenience so consumers accidentally import internal SDK classes.

## Production perspective

Track ABI changes and affected compile tasks for high-fan-out modules, inspect dependency reports, and compare clean and incremental builds with controlled caches. Review `api` additions as contract changes.

## Interview answer — short

The implementation configuration creates a strict ABI compilation firewall, keeping dependencies off downstream compile classpaths and shielding consumers from recompilation when internal implementations change. The api configuration transitively exposes dependencies to consumers, causing cascading recompilations across the entire build graph whenever the dependency is modified.

## Interview answer — structured

Understanding how api and implementation influence compilation boundaries is the key to mastering Gradle build performance.
When a module declares a dependency using implementation, Gradle places that library on the module's compile classpath, but hides it from downstream consumers.
This establishes an Application Binary Interface firewall.
When an engineer refactors internal code or upgrades an internal library, Gradle analyzes the generated class signatures.
Because the module's public ABI has not changed, Gradle marks downstream compilation tasks as UP-TO-DATE, skipping compilation entirely.
Conversely, declaring a dependency with api forces Gradle to place that library on the compile classpath of all downstream modules.
Any change to that library marks the compile classpath dirty for every consumer, triggering cascading rebuilds across dozens of modules.
Defaulting to implementation preserves the remote build cache and keeps incremental compilation fast.

## Interview answer — deep senior

At the compiler level, Gradle's compilation avoidance mechanism relies on ABI hashing to determine whether downstream tasks can be safely bypassed.
When a module compiles, Gradle computes a cryptographic hash of its public ABI, which includes public and protected method signatures, parameter types, return types, and class hierarchies, while ignoring private methods and method body bytecode.
When we use implementation, the dependency is excluded from our consumers' compile classpath.
If we refactor internal algorithms or modify private helper functions inside our module, our public ABI hash remains identical.
When Gradle evaluates downstream modules, it compares their compile classpath hashes against previous build snapshots.
Finding no change, Gradle skips compileKotlin and marks the task UP-TO-DATE.
If we had used api, the dependency would form part of the consumer's compile classpath.
Any change to that dependency, including updating internal transitive dependencies, invalidates the consumer's compile classpath hash, triggering a cascading rebuild that sweeps across the dependency graph.
In enterprise architectures, we treat api declarations as structural debt.
We enforce implementation across all build scripts, promoting to api only when an external type is an unavoidable component of our module's public contract.
We also configure automated linter rules to flag any PR that introduces domain-specific entity names or endpoint paths inside infrastructure modules, preserving platform purity.

## How to answer in the interview

- **Why:** classpath exposure increases rebuild surface.
- **How:** audit signatures and choose api/implementation.
- **Trade-off:** encapsulation versus convenient transitive access.
- **Failure case:** consumer relied on hidden transitive type.
- **Production solution:** compile consumers and measure tasks.

## Deep-dive talking points

Discuss ABI, compiler inputs, high fan-out, inline/codegen caveats, task graph and build measurement.

## Follow-up questions

- **Interviewer:** "Do Kotlin `inline fun` declarations affect ABI stability?"
  **Answer:** "Yes! Inline functions are inlined directly at the call site in bytecode. Changing the body of an inline function changes the ABI and forces all callers to recompile."

- **Interviewer:** "Can Gradle lint detect unnecessary `api` dependencies?"
  **Answer:** "Yes. The Dependency Analysis Gradle Plugin analyzes class usage and flags dependencies that can be safely demoted from `api` to `implementation`."

## Self-check rubric

Trace a public type leak, propose an API boundary, and compare task graphs empirically.

## References and reviewed-on date

- [Gradle Java Library Plugin](https://docs.gradle.org/current/userguide/java_library_plugin.html) — API/implementation semantics.
- [Gradle performance guide](https://docs.gradle.org/current/userguide/performance.html) — measured build behavior.

Technically reviewed against primary documentation on 2026-10-13.

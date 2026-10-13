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

implementation hides dependencies from the consumer's compile classpath, allowing Gradle to skip downstream recompilations if the dependency's public ABI hasn't changed. api leaks dependencies into downstream classpaths, invalidating ABI caches and triggering expensive rebuild cascades across all transitive consumers whenever any upstream change occurs.

## Interview answer — structured

The difference between `api` and `implementation` directly dictates how Gradle performs incremental compilation and task avoidance:

1. **Compilation Boundaries (`implementation`)**: A dependency declared with `implementation` is available to the declaring module's compiler, but is strictly stripped from the compile classpath of downstream consumers. If module `A` changes an internal implementation detail, Gradle recompiles `A`, verifies its public ABI hash is intact, and skips compiling downstream modules (`UP-TO-DATE`).

2. **ABI Leakage (`api`)**: Declaring a dependency with `api` publishes it onto the compile classpath of every transitive consumer. Any change to the upstream dependency invalidates the ABI hash of intermediate modules, causing a massive rebuild cascade that recompiles the entire downstream subtree.

To maximize build speeds in large modularized codebases, enforce `implementation` universally. Reserve `api` exclusively for types that are formally part of the module's public function signatures or return types.

## Interview answer — deep senior

Under the hood, Gradle's Kotlin compile task (`compileKotlin`) computes an **ABI (Application Binary Interface) digest** based on public classes, method signatures, return types, and annotations.

When module `A` compiles, Gradle compares its new ABI digest against the cached digest from the previous run:
- If the digest matches (meaning only private method bodies, local variables, or comments changed), Gradle halts recompilation for all modules connected via `implementation`.
- However, if `B` exposes `A` via `api`, Gradle cannot guarantee that `C` didn't transitively rely on inline functions, constants, or bytecode metadata from `A`. It is forced to re-evaluate and recompile `C`.

In modern Android architectures, using `implementation` alongside the **Gradle Build Cache** and **Configuration Avoidance APIs** transforms what would be a 40-second build into a sub-second cached fetch.

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

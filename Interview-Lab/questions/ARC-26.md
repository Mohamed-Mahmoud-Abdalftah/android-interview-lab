---
id: "ARC-26"
question: "How do you enforce boundaries without a huge number of boilerplate interfaces?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "C"
phase: 2
priority: "P1"
order: 171
editorial_status: "reviewed"
---

# ARC-26

## Original interview question

How do you enforce boundaries without a huge number of boilerplate interfaces?

## What the interviewer evaluates

Enforce meaningful dependencies with modules, visibility and tests while minimizing ceremonial contracts.

## Explanation in Arabic

كيف تفرض وتضبط حدود المعمارية (Architectural Boundaries) بصرامة دون الغرق في أطنان من الواجهات العقيمة (Boilerplate Interfaces)؟

1. المعضلة: Interface Boilerplate مقابل الحدود الرخوة (Loose Boundaries):
   - يعتقد بعض المطورين أن الطريقة الوحيدة لفرض Clean Architecture هي كتابة `interface` لكل كلاس في التطبيق، مما يضاعف عدد الملفات ويصيب الفريق بالإرهاق (Interface Exhaustion).
   - على الجانب الآخر، إلغاء الواجهات بالكامل يفتح الباب لتسريب التبعيات وتشابك الكود (Spaghetti Code).

2. الحلول الهندسية الحديثة لفرض الحدود بذكاء:
   - **فرض الحدود على مستوى الـ Gradle Modules (Compiler-Enforced Boundaries)**:
     * تقسيم المشروع إلى موديولات مستقلة: `:feature:checkout` و `:core:data`.
     * الـ Compiler هو الشرطي الذي يمنع التجاوز: يستحيل على كود الـ UI استدعاء كود الـ Database إذا لم يكن هناك `implementation(project(...))` في ملف `build.gradle.kts`!
   - **استخدام الـ Kotlin Visibility Modifiers (`internal`)**:
     * داخل الموديول، اجعل الكلاسات الملموسة `internal` واكشف فقط نقطة الدخول العامة.
   - **أتمتة الفحص عبر Konsist / ArchUnit (Architecture Testing)**:
     * كتابة اختبارات آلية تفحص قواعد المعمارية في CI/CD وتمنع دمج أي PR يخالف القواعد دون الحاجة لـ Interfaces يدوية في كل مكان!

## Practical walkthrough

فرض قواعد المعمارية آلياً باستخدام مكتبة Konsist في الـ Unit Tests:
```kotlin
// اختبار Konsist يعمل في CI للتحقق من أن الـ ViewModels لا تستورد Room أو Retrofit أبداً:
class ArchitectureBoundaryTest {
    @Test
    fun viewModels_mustNotDependOn_dataOrNetwork() {
        Konsist.scopeFromProject()
            .classes()
            .withNameEndingWith("ViewModel")
            .withoutName("ArchitectureBoundaryTest")
            .assertNot {
                it.hasImportWithText { import ->
                    import.startsWith("retrofit2") ||
                    import.startsWith("androidx.room") ||
                    import.contains(".data.")
                }
            }
    }

    @Test
    fun useCases_mustHaveSinglePublicMethod_invoke() {
        Konsist.scopeFromProject()
            .classes()
            .withNameEndingWith("UseCase")
            .assert {
                it.numPublicDeclarations() == 1 && it.hasFunctionWithText { f -> f.contains("operator fun invoke") }
            }
    }
}
```

## Why it matters and how it works

Boundaries are compile-time dependency rules and stable API contracts. Gradle module edges, visibility, lint/architecture checks and review can enforce them. Interfaces are one tool, not the only enforcement mechanism.

## Worked example

Conceptual graph: `:feature:search` depends on `:core:model` and `:core:data-api`; `:data:search` implements the API and depends on Retrofit/Room; `:app` wires them. A pure `SearchFormatter` remains concrete and `internal` in its feature. CI checks that UI modules do not depend on Retrofit.

## Trade-offs and decision criteria

Modules and checks add build/configuration cost; too many tiny modules slow navigation. Package conventions are lightweight but not hard enforcement. Choose a few real boundaries, measure build and change locality, and expand only when leakage appears.

## Failure modes

A project has one interface per class but UI module still imports DTOs through those interfaces: boundary failed. Another has perfect packages but no module rules, so a new direct DAO call compiles. Test source dependencies and public types, not naming conventions.

## Production perspective

A growing marketplace keeps feature modules independent, core contracts small, and data adapters replaceable. Architecture tests catch forbidden imports, while reviews challenge new interfaces that have no consumer need.

## Interview answer — short

Enforce architectural boundaries without boilerplate interfaces by leveraging Gradle multi-module compilation isolation, Kotlin `internal` visibility modifiers to encapsulate implementation details, and automated architectural linting rules via Konsist or ArchUnit in CI.

## Interview answer — structured

Enforcing architectural boundaries does not require suffocating codebases under 1-to-1 boilerplate interfaces (`Foo` / `FooImpl`). Modern Android engineering employs structural, compiler-enforced, and automated tooling mechanisms.

1. **Compiler-Enforced Gradle Boundaries**: The strongest boundary is compilation failure. By splitting code into independent Gradle modules (`:feature:home`, `:core:domain`, `:core:database`), the build graph physically prevents forbidden calls. If a developer attempts to call a Room DAO from a ViewModel in a feature module that has no dependency on `:core:database`, the project will not compile.

2. **Kotlin `internal` Visibility Modifiers**: Within a module, mark concrete classes, network DTOs, and helper mappers as `internal`. Expose only the required public entry point or interface. Consuming modules cannot access internal types even if they depend on the module.

3. **Automated Architecture Tests (Konsist / ArchUnit)**: Rather than relying on manual code reviews, we write executable unit tests using **Konsist** that verify architectural invariants across the entire repository in CI.

## Interview answer — deep senior

Tools like **Konsist** revolutionize architectural governance. In just 5 lines of Kotlin test code, an engineering team can enforce contracts such as:
- *'No class in `:presentation` may import anything from `androidx.room` or `retrofit2`.'*
- *'Every Repository implementation must reside inside the `data` package.'*
- *'All UseCases must reside in `:domain` and expose only `operator fun invoke()`.'*

If any developer violates these rules, the test fails in local builds and blocks GitHub Actions CI. This eliminates the need for speculative interface wrapping while maintaining ironclad architectural discipline across large distributed teams.

## How to answer in the interview

- **Why:** architecture needs enforceable dependencies.
- **How:** use modules and targeted interfaces.
- **Trade-off:** guardrails versus boilerplate.
- **Failure case:** package names look clean but imports cross.
- **Production solution:** CI dependency check and contract tests.

## Deep-dive talking points

Audit module graph, exported types, `internal` helpers, interface necessity and CI architecture checks.

## Follow-up questions

- **Interviewer:** "What is Konsist, and how does it differ from Android Lint?"
  **Answer:** "Konsist is a Kotlin-first static analysis and architecture linter that allows writing unit tests asserting package structure, class inheritance, import rules, and naming conventions using an idiomatic Kotlin DSL."

- **Interviewer:** "How does `internal` visibility enhance multi-module architecture?"
  **Answer:** "`internal` restricts class visibility strictly to the declaring Gradle compilation module, preventing external modules from depending on concrete implementation details."

## Self-check rubric

Design an allowed module graph and identify one meaningful interface and one avoidable interface.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — module boundaries.
- [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) — adaptable architecture practices.

Technically reviewed against primary documentation on 2026-10-13.

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

## Concept and technical explanation

Enforcing architectural boundaries without succumbing to ceremonial boilerplate interfaces requires utilizing compiler-enforced Gradle modularization, Kotlin language visibility controls, and automated architecture linting tools. The traditional dogma of creating an interface for every single class (such as UserRepository for UserRepositoryImpl) doubles file counts and adds cognitive friction without delivering tangible architectural safety. Instead, senior engineers enforce boundaries at compile-time by structuring the project into focused Gradle modules where forbidden imports physically fail compilation. Implementation details are encapsulated using Kotlin's internal visibility modifier, while architecture enforcement frameworks like Konsist or ArchUnit validate structural rules in continuous integration.

## Practical walkthrough (English)

Enforcing architectural boundaries via Konsist tests and Kotlin internal visibility:
```kotlin
// 1. Module encapsulation: Keep concrete classes internal, exposing only required entry points
// Inside module ':core:database'
internal class RoomUserDao : UserDao { ... } // Inaccessible to presentation modules!

// 2. Automated Architecture Testing in CI with Konsist
class ArchitectureRulesTest {
    @Test
    fun presentationMustNotAccessDatabaseOrNetworkInternals() {
        Konsist.scopeFromProject()
            .classes()
            .withNameEndingWith("ViewModel")
            .assertNot { viewModel ->
                viewModel.hasImportWithText { importPath ->
                    importPath.startsWith("androidx.room") ||
                    importPath.startsWith("retrofit2") ||
                    importPath.contains(".data.local.")
                }
            }
    }

    @Test
    fun useCasesMustResideInDomainAndExposeOnlyInvoke() {
        Konsist.scopeFromProject()
            .classes()
            .withNameEndingWith("UseCase")
            .assert { useCase ->
                useCase.resideInPackage("..domain..") &&
                useCase.numPublicDeclarations() == 1 &&
                useCase.hasFunctionWithText { it.contains("operator fun invoke") }
            }
    }
}
```

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

Enforce architectural boundaries without boilerplate interfaces by leveraging Gradle multi-module compilation isolation, Kotlin internal visibility modifiers to encapsulate implementation details, and automated architectural linting rules via Konsist or ArchUnit in continuous integration to catch violations before merging.

## Interview answer — structured

Enforcing architectural boundaries does not require suffocating a codebase under ceremonial one-to-one boilerplate interfaces for every repository and helper class. Modern Android architecture relies on structural, compiler-enforced, and automated tooling mechanisms.
The primary mechanism is compiler-enforced Gradle module boundaries. By organizing the codebase into independent Gradle modules—such as feature modules, domain modules, and core database modules—the build graph enforces structural boundaries. If a developer attempts to call a Room database DAO directly from a feature ViewModel without an explicit Gradle dependency, the code fails to compile.
The second mechanism is Kotlin visibility modifiers. By marking concrete implementations, database entities, and network DTOs with the internal modifier, they remain strictly accessible within their declaring Gradle module. External modules cannot access internal types even if they declare a dependency on that module.
The third mechanism is automated architecture testing. Rather than relying on manual code reviews, teams write executable unit tests using Konsist or ArchUnit in CI. These tests automatically assert that ViewModels never import networking libraries and that repositories follow required conventions, providing ironclad architectural guardrails without redundant interface overhead.

## Interview answer — deep senior

Under the hood, dogmatic adherence to one-to-one interfaces (such as CartRepository alongside CartRepositoryImpl) stems from legacy Java testing limitations where mocking required interfaces. In modern Kotlin and Android development, classes can be tested directly with lightweight fakes or instantiated concretely when design requirements do not involve multiple polymorphic implementations.
Relying solely on interfaces to enforce boundaries is often an illusion: a feature module can still import network DTOs through an interface if both reside in the same package. In contrast, compiler-level modularization provides hard physical guarantees. A Gradle module boundary is inviolable; code outside the module cannot see internal declarations, and missing dependencies halt the build pipeline instantly.
Furthermore, static analysis frameworks like Konsist revolutionize architectural governance. By parsing the Kotlin Abstract Syntax Tree (AST) directly within standard JUnit tests, Konsist allows engineers to write declarative assertions regarding package structures, class inheritance, import rules, and naming conventions.
For example, a five-line Konsist test can mandate that no class in the presentation layer may import anything from Retrofit or Room, and that all UseCases must reside in domain packages and expose exactly one public operator fun invoke.
Staff engineers replace ceremonial interface proliferation with this combination of module boundaries, internal visibility, and automated AST checks, keeping codebases concise, clean, and architecturally disciplined.

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

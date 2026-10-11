---
id: SCN-003
lesson_id: KOT-003
status: reviewed
code_verification: not_run
---
# SCN-003 — Crash while a subclass is being constructed

**Hypothetical incident, not an observed production crash.** A new configuration screen sometimes fails while creating a subclass of a shared base controller. The exercise assumes Kotlin/JVM semantics, with the exact Android app, device, OS version, stack trace and frequency unknown. Start with [KOT-003](../01-Kotlin-JVM-ART/kot-003-classes-constructors-initialization-order.md).

<p dir="rtl" lang="ar">التشخيص المبدئي: base class بتستدعي method <code dir="ltr">open</code> جوه <code dir="ltr">init</code>. الـ override في subclass بتقرأ property لسه initializer بتاعتها ما اشتغلش. ده تفسير محتمل، لكن في incident حقيقي لازم stack trace وترتيب الإنشاء قبل إعلان root cause. ما تنسبش أي crash في الشاشة للـ lifecycle لمجرد إنها Android.</p>

## Symptom and reproducible sketch

```kotlin
open class BaseController {
    init { verify() } // unsafe extension point during construction
    open fun verify() {}
}
class ProfileController : BaseController() {
    private val token = "ready"
    override fun verify() { require(token.length == 5) }
}
```

The derived initializer is not guaranteed to have run when the base calls the override. [Kotlin inheritance](https://kotlinlang.org/docs/inheritance.html), checked 2026-10-10, documents this hazard. This abbreviated sketch is for source review and is not one of the executed lab tests; no specific exception or Android stack trace is claimed.

## Competing hypotheses and evidence

1. **Premature virtual dispatch:** Find the top application frame, base constructor or init call, and derived override in the stack trace. Add a local order trace with a fake constructor path. A reproducible call chain before derived initializer runs supports this cause.
2. **Invalid input:** Test the same class with a valid and invalid config. An explicit require failure after full initialization is a different failure from an early read of an uninitialized field.
3. **Lifecycle callback or saved-state mismatch:** Reproduce construction in a pure JVM test without Activity/Fragment. If it fails there, lifecycle is unnecessary for the initial failure, although the screen may have other bugs.

For a real Android incident, collect a redacted logcat excerpt, app/OS/version information, constructor call path, and a minimal test. Do not log credentials or full profile identifiers. A production rollout or measured crash rate is not available here.

## Corrective design and tests

Move base validation to a private/final function that uses constructor arguments owned by the base. Delay overridable hooks until an explicit post-construction method called by a clear owner. Test base creation, derived creation, invalid input, and callback ordering. The [Day 3 lab](../Coding-Challenges/LAB-003-construction-boundary.md) tests source-order initialization and validation; a future Android integration test would cover the actual controller lifecycle.

**Tempting wrong fixes:** A broad catch around construction masks the invalid state. Changing the derived property from val to lateinit or using a null assertion only shifts the failure. Adding a delay or posting to the main thread makes ordering nondeterministic and does not repair the constructor contract.

**Rollout plan, not executed:** Keep the change small, add the reproducer to CI, verify the target screen on its supported device matrix, monitor the exact crash signature after staged release, and roll back if an unexpected constructor path appears.

## Senior follow-ups

1. **Can base code call a private final helper during init?** Yes, if it only uses base-owned arguments/state already initialized; final dispatch cannot jump to a derived override. Still avoid side effects that leak a partially built object.
2. **Would a factory prevent all such crashes?** No. A factory can choose when to publish the instance, but it cannot undo a base constructor that calls open behavior while creating it. Fix the hierarchy's construction path first.

---
id: "SOL-11"
question: "How would you replace a giant BaseActivity with smaller composable behaviors?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "B"
phase: 2
priority: "P1"
order: 182
editorial_status: "reviewed"
---

# SOL-11

## Original interview question

How would you replace a giant BaseActivity with smaller composable behaviors?

## What the interviewer evaluates

Replace a giant inheritance hub with optional capabilities while preserving lifecycle and behavior.

## Explanation in Arabic

ابدأ بـinventory لـ`BaseActivity`: toolbar، analytics، permission launcher، navigation، loading، dependency lookup. اختبر current behavior للشاشات المهمة. بعدها طلّع كل behavior له lifetime واضح لـcollaborator صغير: toolbar controller للشاشات المناسبة، analytics observer مسجّل/متشال مع lifecycle، navigator، permission coordinator. Activity تتركب من اللي تحتاجه بدل ترث كل شيء. نقل تدريجي screen واحدة كل مرة مع parity tests، مش حذف base في PR ضخمة. خليك حذر من callbacks محتفظة بـActivity بعد destroy.

## Why it matters and how it works

A giant base class couples every child to unrelated hooks and shared lifecycle assumptions. Composition exposes only needed capabilities and makes ownership testable. Incremental migration limits regressions.

## Worked example

Conceptual flow: `CatalogActivity` receives `ToolbarController` and `AnalyticsObserver`; `CameraActivity` receives only analytics. Both may extend the framework `ComponentActivity`, but neither has to implement an unsupported `setupToolbar()`. The analytics observer registers and unregisters at documented lifecycle points.

## Trade-offs and decision criteria

Composition adds wiring and possibly small interfaces. A tiny stable base helper can remain if every child truly uses it and the contract is sound. Avoid replacing one giant base with a giant service locator.

## Failure modes

BaseActivity holds a View binding and global analytics callback after Activity recreation, leaking the old screen. Moving code without lifecycle review preserves the leak. Contract tests and LeakCanary/device checks may be needed for actual device behavior.

## Production perspective

A media app migrates toolbar screens first, then permission flows, while keeping old base compatibility temporarily. Each release verifies recreation and back navigation. After all callers move, the base is removed.

## Interview answer — short

I inventory the base class’s responsibilities, add characterization tests, and move optional behaviors into lifecycle-aware collaborators. Screens compose only what they need, and I migrate incrementally to avoid hidden regressions.

## Interview answer — structured

A giant BaseActivity often mixes toolbar, navigation, analytics and permissions because inheritance made sharing easy. I would first capture behavior and lifecycle assumptions, then extract cohesive collaborators one at a time. Toolbar screens receive a toolbar controller; full-screen camera does not. Analytics registration gets explicit lifecycle cleanup. I move screens incrementally and test recreation, permissions and back behavior. I do not replace the base with a global service locator or a dozen empty interfaces. I would migrate one representative screen first and compare behavior before moving the rest. The new controller or observer must have an explicit cleanup path; otherwise the refactor only relocates a leak. After parity, I can remove the old hook and simplify subclasses.

## Interview answer — deep senior

The important step is to map responsibilities and owners, not merely split a file. A toolbar is a UI capability, a permission launcher is tied to an Activity lifecycle, and analytics may need an observer registered only while active. Each should have a contract and scope appropriate to that lifetime. I would write characterization tests for representative screens and identify subclasses that override methods with no-op or throws—signs the base promise is too broad. Then I introduce collaborators behind the old API, migrate one screen at a time, and remove the old hooks after parity. Tests cover configuration change, navigation and callback cleanup; device inspection is needed before claiming leak freedom. The result is explicit composition, with framework inheritance only where required. A giant base class often hides state shared across children, so extraction must identify ownership. A permission launcher belongs to an Activity lifecycle, a toolbar controller to the screen UI, and an analytics observer may register only while started. I would not inject all of them as an application singleton. During migration I add tests for no-toolbar screens, repeated recreation, and listener cleanup. If a collaborator has no variation, it can be concrete; composition does not require a new interface for every behavior. The objective is explicit optional capabilities and safe lifetimes, not just a smaller base file.

## Deep-dive talking points

Plan an incremental migration, assign lifecycle owners, and identify an LSP violation hidden by base hooks.

## Follow-up questions

- [SOL-10](../sol-10/): Why is mandatory toolbar setup risky? **Answer:** a no-toolbar child cannot honor the base contract.
- [SOL-09](../sol-09/): Why composition? **Answer:** screens select capabilities without inheriting unrelated behavior.

## Self-check rubric

List three base responsibilities, one lifecycle leak, and a two-step migration with parity checks.

## References and reviewed-on date

- [Android app architecture](https://developer.android.com/topic/architecture) — component lifecycle and separation of concerns.
- [Kotlin delegation](https://kotlinlang.org/docs/delegation.html) — composition helper.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.

---
id: "COM-27"
question: "How do you test a screen with loading, error, success, and permission states?"
topic: "Jetpack Compose"
code: "COM"
group: "C"
phase: 3
priority: "P1"
order: 256
editorial_status: "reviewed"
---

# COM-27

## Original interview question

How do you test a screen with loading, error, success, and permission states?

## What the interviewer evaluates

- Separate pure state rendering tests from Route/platform integration tests.
- Assert semantics and actions across a state matrix.
- Include lifecycle, permission denial/revocation, and restoration paths.

## Explanation in Arabic

عرّف `UiState` واضحة ثم اختبر Screen composable ببيانات fake لكل حالة: Loading يعلن progress، Error رسالة وRetry action، Success البيانات، PermissionRequired شرح وطلب access. Compose UI test يستخدم semantics nodes وأفعال حقيقية بدل البحث عن implementation details. ViewModel unit tests تتحقق من transitions وretry. Permission dialog نفسها منصة Android؛ اختبرها في instrumented test/وسيلة مناسبة للـActivity Result، مع denial وrevocation من Settings. Previews تساعد بصريًا لكنها ليست assertions.

### Practical walkthrough in Egyptian Arabic

اختبر Screen بحالات injected بدل ما تحاول تضبط network وpermission حقيقية لكل assertion. `Loading` لازم progress واضح، `Error` فيها Retry يعمل callback مرة، و`PermissionRequired` فيها rationale؛ `Success` تعرض البيانات. بعد كده اختبر Route على emulator للـpermission dialog والعودة من Settings والـlifecycle. Preview تعرض الشكل فقط؛ مش هتكشف callback مكررة أو permission dialog حقيقية. غطّ كل state باختبار semantics، ثم Route على emulator للرفض والعودة من Settings.

## Why it matters and how it works

A stateless Screen can be rendered under Compose test rule with explicit state and callback spies. Its semantics tree exposes labels, roles and actions. ViewModel tests isolate state transitions without device setup. Route tests prove integration with navigation, lifecycle collection and permission launcher, which pure Screen tests cannot claim.

## Worked example

For a photo-upload Screen, inject `Loading` and assert progress semantics, inject `Error(network)` and tap Retry once, inject `Ready(images)` and assert content descriptions, then inject `PermissionRequired` and assert rationale plus Grant callback. An emulator test launches the route, denies permission, returns from Settings with changed grant, and checks the state updates without duplicate dialog.

### Compose/Kotlin walkthrough

```kotlin
// Instrumented Compose UI test against a stateless Screen.
class UploadScreenTest {
    @get:Rule val rule = createComposeRule()

    @Test fun errorOffersRetry() {
        var retries = 0
        rule.setContent { UploadScreen(UploadState.Error, onRetry = { retries++ }) }
        rule.onNodeWithText("Retry").performClick()
        rule.runOnIdle { assertEquals(1, retries) }
    }
}
// Imports: androidx.compose.ui.test.junit4.createComposeRule,
// androidx.compose.ui.test.onNodeWithText/performClick;
// org.junit.Test, org.junit.Rule, org.junit.Assert.assertEquals.
```

## Trade-offs and decision criteria

State matrix tests are fast and deterministic; platform permission tests cost device time but cover contracts fakes cannot. Screenshot tests catch layout regressions but do not replace semantic/action assertions. Overusing mocks for every nested composable makes tests brittle; pass coherent states instead.

## Failure modes

A preview exists but no test checks Retry. Tests match exact layout hierarchy and break on harmless refactor. A unit test claims permission dialog behavior despite no Android runtime. Loading blocks controls but semantics do not announce progress. The screen crashes after rotation due to missing saved ID.

## Production perspective

Keep a canonical state matrix and at least one action assertion per meaningful state. Add device coverage for grant/deny/revoke and lifecycle recreation, and run accessibility checks with screen reader on a target device.

## Interview answer — short

“I test each state in an isolated Compose Screen, assert semantics and actions, unit-test transitions, then instrument the Route for permission and lifecycle behavior. Test each visual state with injected inputs, then test platform wiring separately.”

## Interview answer — structured

“A stateless Screen lets me inject Loading, Error, Success and PermissionRequired directly in Compose tests. I assert visible semantics and user actions, such as Retry calling its callback once, rather than implementation layout. ViewModel tests verify how repository outcomes produce those states. I reserve instrumented tests for Activity Result permissions, navigation and lifecycle because a pure UI test cannot prove Android dialogs or revocation handling. Previews are useful review aids but not proof. An Error screen test taps Retry once; an emulator test covers the real permission dialog and return from Settings.”

## Interview answer — deep senior

“I divide the claim into rendering, transition, and platform integration. For rendering, I provide a coherent `UiState` to a Screen that has no hidden ViewModel or NavController dependency. A Compose test checks loading progress semantics, error message and Retry action, success content and accessible labels, and the permission rationale/action. For transitions, a ViewModel unit test uses a fake repository and controlled dispatcher to drive loading, success, error and retry. For Android behavior, an instrumented Route test covers the Activity Result launcher, denial, a later grant or revocation, lifecycle restart and navigation. I do not let a screenshot stand in for a button action, or a fake permission result stand in for platform dialog behavior. I also check rotation and saved-state restoration where the workflow requires them, plus TalkBack focus when an error or dialog appears. The test matrix should state precisely which layer proves each behavior, keeping most feedback fast while retaining a small device suite for risks only Android can expose. The test suite asserts accessible meaning and state transitions, not just what a preview screenshot looks like.”

## How to answer in the interview

- **Why:** each state has a different user promise.
- **How:** feed explicit state into Screen and assert semantics plus callbacks.
- **Trade-off:** Screen tests cannot prove platform permission wiring.
- **Failure case:** previews look fine while Route repeats a dialog.
- **Production solution:** combine state tests, ViewModel transition tests, and emulator integration.

## Deep-dive talking points

Discuss state matrix, semantics assertions, ViewModel transitions, platform permission test, restoration and accessibility.

## Follow-up questions

- Do previews count as tests? **Answer:** no; they help visual review but provide no automated assertion.
- Can a JVM ViewModel test prove Android permission dialog behavior? **Answer:** no; instrument the platform integration.
- What should Retry test assert? **Answer:** its semantic action is available and invokes the intended callback/transition.

## Self-check rubric

Map four states to assertions and one action, then identify unit and device integration claims.

## References and reviewed-on date

- [Test Compose layouts](https://developer.android.com/develop/ui/compose/testing) — semantics and UI tests.
- [Request permissions](https://developer.android.com/training/permissions/requesting) — platform permission behavior.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. No device run is claimed for this example.

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

كيفية اختبار شاشة Compose شاملة تغطي حالات التحميل (Loading)، الخطأ (Error)، النجاح (Success)، والأذونات (Permissions):

1. الأساس المعماري للاختبار السهل (Testability Architecture):
   - كما شرحنا في COM-18، نختبر دائماً **Stateless Screen Composable** النقي وليس الـ Route Composable المحمل بـ Hilt و Navigation.
   - نقوم بتمرير حالات الـ `UiState` يدوياً وبشكل مباشر، مما يجعل الاختبار سريعاً، وموثوقاً، ويعمل بنسبة 100% دون أي Mocking معقد.

2. كتابة اختبارات Compose باستخدام `createComposeRule()`:
   - **حالة التحميل (Loading)**: استدعاء `composeTestRule.setContent { Screen(UiState.Loading) }` والتحقق من ظهور `assertIsDisplayed()` لمؤشر التحميل.
   - **حالة النجاح (Success)**: تمرير قائمة بيانات وهمية والتحقق من ظهور النصوص (`assertTextEquals`)، ومحاكاة النقر (`performClick()`) والتحقق من إطلاق الـ Callback المناسب.
   - **حالة الخطأ (Error)**: تمرير رسالة خطأ والتحقق من ظهور زر إعادة المحاولة (Retry) وإطلاقه للحدث.
   - **حالة الأذونات (Permissions)**: تمرير حالة الإذن كـ Parameter في الـ Screen والتحقق من ظهور شاشة التبرير (Rationale) أو زر طلب الإذن.

## Practical walkthrough

كتابة اختبار شامل لحالات الشاشة المختلفة باستخدام Compose UI Test:
```kotlin
@RunWith(AndroidJUnit4::class)
class DocumentScreenTest {
    @get:Rule
    val composeRule = createComposeRule()

    @Test
    fun whenStateIsLoading_showsProgressIndicator() {
        composeRule.setContent {
            DocumentScreen(uiState = DocumentUiState.Loading, onAction = {})
        }
        composeRule.onNodeWithTag("LOADING_SPINNER").assertIsDisplayed()
    }

    @Test
    fun whenStateIsSuccess_displaysDocumentsAndHandlesClick() {
        var clickedId: String? = null
        val docs = persistentListOf(Document("1", "Invoice"))

        composeRule.setContent {
            DocumentScreen(
                uiState = DocumentUiState.Success(docs),
                onAction = { if (it is DocumentAction.Open) clickedId = it.id }
            )
        }

        composeRule.onNodeWithText("Invoice").assertIsDisplayed().performClick()
        assertEquals("1", clickedId)
    }

    @Test
    fun whenPermissionDenied_showsRationale() {
        composeRule.setContent {
            DocumentScreen(
                uiState = DocumentUiState.PermissionRequired(shouldShowRationale = true),
                onAction = {}
            )
        }
        composeRule.onNodeWithText("Storage permission is required to view documents").assertIsDisplayed()
    }
}
```

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

Test multi-state screens by testing the stateless Screen composable directly using `createComposeRule()`. Pass explicit state objects for Loading, Success, Error, and PermissionRequired without mocking ViewModels, and assert node visibility using Semantics finders (`onNodeWithText`, `onNodeWithTag`) and user action assertions (`performClick`).

## Interview answer — structured

Testing a multi-state Compose screen requires verifying that each distinct state renders its expected UI hierarchy and responds accurately to interaction callbacks.

1. **Target the Stateless Screen**: We never write UI tests against the ViewModel-bound Route composable. We test the pure Screen composable (`MyScreen(uiState, onAction)`), eliminating the need for MockWebServer, Hilt, or simulated Coroutine dispatchers.

2. **Structuring the Test Suite** with `createComposeRule()`:
   - **Loading State**: Render `UiState.Loading`. Assert that the loading spinner exists and content nodes are absent.
   - **Success State**: Render `UiState.Success(data)`. Verify item texts with `onNodeWithText()`, scroll through lists with `performScrollToIndex()`, and verify item clicks with `performClick()`, asserting that callback lambdas capture expected parameters.
   - **Error State**: Render `UiState.Error("Network timeout")`. Assert that the error banner appears, click 'Retry', and verify that `onAction(Retry)` is fired.
   - **Permission State**: Render `UiState.PermissionDenied`. Assert that the rationale dialog is displayed and actionable.

## Interview answer — deep senior

Under the hood, Compose UI tests interact directly with the **Semantics Tree** rather than the physical Android view hierarchy. To make assertions robust against localization changes, we use `Modifier.testTag("tag_name")` or check semantic properties like `hasClickAction()`.

When testing asynchronous state flows in Route composables (integration testing), we use `createAndroidComposeRule<MainActivity>()`. Compose's test rule automatically synchronizes with the main looper and idling resources: `composeTestRule.waitForIdle()` waits for all recompositions, measure passes, and active animations to settle before executing assertions, eliminating flaky sleeps.

In modern CI/CD, we pair these unit UI tests with **Screenshot Testing** (using Roborazzi running on JVM), rendering all four states in headless tests in seconds to detect accidental visual regressions.

## How to answer in the interview

- **Why:** each state has a different user promise.
- **How:** feed explicit state into Screen and assert semantics plus callbacks.
- **Trade-off:** Screen tests cannot prove platform permission wiring.
- **Failure case:** previews look fine while Route repeats a dialog.
- **Production solution:** combine state tests, ViewModel transition tests, and emulator integration.

## Deep-dive talking points

Discuss state matrix, semantics assertions, ViewModel transitions, platform permission test, restoration and accessibility.

## Follow-up questions

- **Interviewer:** "Why is testing the stateless Screen composable faster than testing the Activity/Route?"
  **Answer:** "It avoids booting up Android Activities, Hilt dependency graphs, SQLite databases, and NavControllers. It mounts only the pure UI hierarchy directly into the Compose test rule."

- **Interviewer:** "How does `composeTestRule` avoid flaky timing issues compared to Espresso?"
  **Answer:** "`composeTestRule` has built-in synchronization with Compose's internal clock and snapshot system, automatically advancing virtual clock time and idling until all pending recompositions and animations complete."

## Self-check rubric

Map four states to assertions and one action, then identify unit and device integration claims.

## References and reviewed-on date

- [Test Compose layouts](https://developer.android.com/develop/ui/compose/testing) — semantics and UI tests.
- [Request permissions](https://developer.android.com/training/permissions/requesting) — platform permission behavior.

Technically reviewed against primary documentation on 2026-10-13.

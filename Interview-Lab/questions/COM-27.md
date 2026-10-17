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

## Concept and technical explanation

Testing a Jetpack Compose screen across loading, error, success, and permission states requires a multi-tiered testing strategy combining JVM component tests, screenshot tests, and ViewModel state verification. By decoupling the architecture into stateless Screen composables and stateful Routes, presentation testing becomes pure and fast. Using Compose UI Test APIs (createComposeRule()), engineers inject static state fixtures into the Screen composable to verify semantic visibility, button enablement, and retry callbacks directly on the JVM with Robolectric or on emulators. Screenshot testing tools like Paparazzi or Roborazzi capture pixel-perfect golden images of all state permutations without mocking Android platform dependencies.

## Practical walkthrough (English)

Testing multi-state UI variants using Compose UI Test rules and semantic assertions:
```kotlin
// Stateless Screen under test
@Composable
fun ProfileScreen(state: ProfileUiState, onRetry: () -> Unit, onRequestPermission: () -> Unit) {
    when (state) {
        is ProfileUiState.Loading -> CircularProgressIndicator(modifier = Modifier.testTag("loading_tag"))
        is ProfileUiState.Error -> Column {
            Text(text = state.message)
            Button(onClick = onRetry) { Text("Retry") }
        }
        is ProfileUiState.PermissionRequired -> Button(onClick = onRequestPermission) { Text("Grant Access") }
        is ProfileUiState.Success -> Text(text = "Welcome, ${state.user.name}")
    }
}

// JVM / Instrumented Compose UI Test
class ProfileScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun errorState_showsMessage_andTriggersRetryCallback() {
        var retryClicked = false

        // Inject Error State Fixture
        composeTestRule.setContent {
            ProfileScreen(
                state = ProfileUiState.Error("Network Timeout"),
                onRetry = { retryClicked = true },
                onRequestPermission = {}
            )
        }

        // Verify Semantics and Interactions
        composeTestRule.onNodeWithText("Network Timeout").assertIsDisplayed()
        composeTestRule.onNodeWithText("Retry").assertIsDisplayed().performClick()

        assertTrue(retryClicked)
    }

    @Test
    fun loadingState_showsProgressIndicator() {
        composeTestRule.setContent {
            ProfileScreen(state = ProfileUiState.Loading, onRetry = {}, onRequestPermission = {})
        }
        composeTestRule.onNodeWithTag("loading_tag").assertIsDisplayed()
    }
}
```

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

We test multi-state Compose screens by decoupling them into stateless Screen composables and verifying each state variant independently. Using createComposeRule(), we inject static UI state fixtures (Loading, Error, Success, Permission) into the screen, asserting that correct texts, loaders, and buttons appear and that callbacks fire when clicked. We also run screenshot tests using Paparazzi or Roborazzi to verify visual fidelity across all states on the JVM without needing emulators.

## Interview answer — structured

Thoroughly verifying complex UI states—Loading, Error, Success, and Permission Required—is made exceptionally fast and deterministic through Jetpack Compose's declarative model.
In traditional XML testing, validating multi-state screens required complex Espresso orchestration, mocking network endpoints, and waiting for asynchronous ViewModels.
In Compose, our architecture cleanly separates the stateful Route from the stateless Screen presenter.
This separation transforms UI testing into pure state projection verification.
Using the official Compose Test API via createComposeRule(), we author isolated UI component tests.
For the Loading state, we inject the loading fixture and assert that the progress indicator node is displayed using onNodeWithTag().
For the Error state, we inject an error model, assert that the error description renders, and simulate a user click on the Retry button to verify that the retry callback lambda fires with the correct payload.
For the Permission state, we verify that the educational rationale and grant button render appropriately.
Finally, we complement semantic tests with JVM screenshot tests using tools like Paparazzi or Roborazzi.
Screenshot tests render all four state variants across phone and tablet configurations in seconds, establishing baseline golden images that catch accidental visual regressions in CI.

## Interview answer — deep senior

Under the hood, Compose UI testing operates by querying the Semantics Tree rather than traversing the physical LayoutNode or Android View hierarchies.
When createComposeRule().setContent {} executes, the test runner builds a headless Composition hierarchy.
Assertion methods like onNodeWithText() and onNodeWithTag() execute search algorithms across the SemanticsNode tree matching SemanticsPropertyKey entries (such as Text, TestTag, and Role).
Because testing targets the stateless Screen composable directly, tests run synchronously on the JVM using Robolectric or headless desktop runners without launching Android Activity lifecycles, Hilt dependency injection graphs, or MockWebServer instances.
Furthermore, Compose UI tests integrate automatic synchronization via IdlingResource mechanics.
The ComposeTestRule automatically waits for the Compose runtime to settle—ensuring all pending recompositions, layout passes, draw steps, and coroutine effect blocks within the composition scope finish before assertions execute.
If testing requires verifying intermediate animations or infinite progress bars, developers control the virtual clock using mainClock.autoAdvance = false and advanceTimeBy() to take deterministic snapshots.
For testing the stateful Route and ViewModel layers, engineers author complementary Unit tests using Turbine.
Turbine collects the ViewModel's uiState StateFlow, asserting that user action events transition the state sequentially: from Loading, to Error, and finally to Success.
This layered testing pyramid provides 100% test coverage with sub-second execution speeds in automated CI pipelines.

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

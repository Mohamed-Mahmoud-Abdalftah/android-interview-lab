---
id: "TST-14"
question: "How do you test Compose UI semantics, navigation, and accessibility?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 409
editorial_status: "reviewed"
---

# TST-14

## Original interview question

How do you test Compose UI semantics, navigation, and accessibility?

## What the interviewer evaluates

- Semantics-based Compose assertions and accessible interactions.
- Navigation contract versus implementation-specific route strings.

## Explanation in Arabic

كيف تختبر شجرة المعاني (Semantics Tree)، والتنقل (Navigation)، وإمكانية الوصول (Accessibility) في Jetpack Compose؟

1. اختبار شجرة المعاني في Compose (Semantics Tree Testing):
   - في Compose، لا توجد View IDs! الواجهة تُمثل كـ **Semantics Tree** يصف معنى ومحتوى كل عنصر للمستخدم وقارئات الشاشة.
   - **أدوات الاختيار والتوثيق**:
     * `onNodeWithText("Submit")`: البحث بالنص المعروض.
     * `onNodeWithContentDescription("Back")`: البحث بوصف المحتوى للأيقونات.
     * `onNodeWithTag("login_button")`: البحث بـ TestTag صريح (يُستخدم كحل أخير إذا لم يتوفر نص أو وصف).
   - **التوكيدات (Assertions)**:
     * `assertIsDisplayed()`, `assertIsEnabled()`, `assertIsSelected()`, `assertHasClickAction()`.

2. اختبار التنقل (Compose Navigation Testing):
   - نستخدم `TestNavHostController` من مكتبة `navigation-testing`.
   - نقوم بربط الـ Controller بـ `NavHost`، وتنفيذ إجراءات النقر، والتحقق من المسار الحالي:
     `assertEquals("details/{orderId}", navController.currentBackStackEntry?.destination?.route)`.

3. فحص إمكانية الوصول (Accessibility Testing - A11y):
   - التأكد من أن مساحة النقر لا تقل عن 48×48dp (Touch Target Size).
   - دمج العقد المترابطة لتسهيل القراءة عبر `Modifier.semantics(mergeDescendants = true)`.

## Practical walkthrough

اختبار شجرة المعاني والتنقل وفحص إمكانية الوصول في Compose:
```kotlin
class ComposeUiAndNavigationTest {
    @get:Rule
    val composeTestRule = createComposeRule()
    private lateinit var navController: TestNavHostController

    @Before
    fun setupAppNavHost() {
        composeTestRule.setContent {
            navController = TestNavHostController(LocalContext.current)
            navController.navigatorProvider.addNavigator(ComposeNavigator())
            AppNavHost(navController = navController)
        }
    }

    @Test
    fun navigateFromHomeToDetails_verifiesRouteAndAccessibility() {
        // 1. التحقق من وجود الزر بإمكانية وصول سليمة والضغط عليه:
        composeTestRule.onNodeWithContentDescription("View Order Details")
            .assertIsDisplayed()
            .assertHasClickAction()
            .performClick()

        // 2. التحقق من انتقال الـ NavController إلى الشاشة والمسار الصحيح:
        assertEquals("order_details/{id}", navController.currentBackStackEntry?.destination?.route)
    }
}
```

## Why it matters and how it works

Compose test rules synchronize with recomposition and expose semantics nodes. Merged semantics can hide child nodes, so understand `useUnmergedTree` only when needed. Accessibility checks require meaningful labels, roles and state descriptions, not arbitrary test tags.

## Worked example

On a checkout form, enter an invalid amount, tap Pay, assert a readable error and that confirmation does not appear. Then provide valid input, tap Pay and assert a pending state and accessible confirmation destination. Use a fake payment source to avoid real charges.

## Trade-offs and decision criteria

Test tags are stable when text is localized, but overusing them can bypass user-visible semantics. Screenshot tests catch visual regressions but cannot replace semantic/a11y assertions.

## Failure modes

A button appears visually but has no content description when icon-only, so screen readers cannot identify it. A test selecting by internal tag passes; add semantics assertion or accessibility audit.

## Production perspective

Run Compose tests on supported screen sizes, RTL locales and font scaling; include keyboard/focus flow and TalkBack review for critical paths. Financial outcome remains backed by domain state, not a UI click assertion.

## Interview answer — short

Test Compose UI via createComposeRule by querying the Semantics Tree with onNodeWithText or onNodeWithContentDescription and asserting states like assertIsDisplayed(). Test navigation using TestNavHostController to assert active backstack routes. Validate accessibility by enforcing semantic content descriptions and 48dp minimum touch targets.

## Interview answer — structured

Testing Jetpack Compose interfaces exercises the semantic contract presented to users and assistive technologies:

1. **Semantics Tree Node Queries**:
   - Query UI nodes using real user semantics: `composeTestRule.onNodeWithText("Checkout")` or `onNodeWithContentDescription("Shopping Cart")`. Prefer semantic matchers over arbitrary `Modifier.testTag()`, as semantic matchers validate that the UI is accessible to screen readers.

2. **State & Action Assertions**:
   - Assert node properties: `assertIsDisplayed()`, `assertIsEnabled()`, `assertIsToggleable()`, `assertValueEquals("100")`. Trigger actions via `performClick()`, `performScrollTo()`, or `performTextInput("text")`.

3. **Navigation Contract Testing**:
   - Mount the `NavHost` using `TestNavHostController(LocalContext.current)`.
   - Execute UI interactions, then assert destination state via `assertEquals("details_route", navController.currentBackStackEntry?.destination?.route)` without launching real activities.

4. **Accessibility (a11y) Auditing**:
   - Enable AndroidX `AccessibilityChecks.enable()` during Compose tests. The framework automatically flags insufficient color contrast, missing content descriptions, and touch targets smaller than 48x48dp.

## Interview answer — deep senior

From an advanced design system testing perspective, semantic merging and unmerged tree inspection provide deep control:

1. **Merged vs. Unmerged Semantics Trees**: By default, Compose merges child semantics into parent nodes for accessibility (e.g. merging a `Button` with its inner `Text` label into a single clickable node). If you need to test a specific inner element, query the unmerged tree explicitly: `onNodeWithText("Subtext", useUnmergedTree = true)`.

2. **Testing Custom Semantics Properties**: When building custom UI components (e.g. custom sliders, star ratings), expose custom semantic properties via `Modifier.semantics { set(CustomKey, value) }`. In tests, query and assert against these typed semantic keys directly.

3. **Robolectric Compose UI Testing**: With modern Robolectric, Compose UI tests using `createComposeRule()` execute directly on the host JVM in seconds, providing rapid UI verification without booting Android emulators.

## How to answer in the interview

- **Why:** users interact with semantics and destinations, not composable internals.
- **How:** type invalid/valid input, click and assert error, pending and destination.
- **Trade-off:** stable semantic selectors versus tags tied to implementation.
- **Failure case:** test only verifies navigate() call or ignores inaccessible icon labels.
- **Production solution:** UI assertions plus device accessibility review.

## Deep-dive talking points

Prompt for semantics tree, merged nodes, accessible name, navigation outcome and RTL/font scaling.

## Follow-up questions

- **Interviewer:** "What is the difference between merged and unmerged semantics trees in Compose?"
  **Answer:** "The merged tree collapses child nodes into parent containers for screen readers (TalkBack); the unmerged tree preserves every individual composable node."

- **Interviewer:** "Why should Modifier.testTag() be used as a last resort in Compose tests?"
  **Answer:** "Test tags do not improve accessibility for real users; querying by text, content description, or semantic role validates both functionality and accessibility."

## Self-check rubric

Use semantics to enter invalid input, assert an accessible error and absent destination, then submit valid input and assert pending/navigation state. Identify one screen-reader or platform behavior requiring device review.

## References and reviewed-on date

- [Compose testing](https://developer.android.com/develop/ui/compose/testing) — semantics and test rules.
- [Compose accessibility](https://developer.android.com/develop/ui/compose/accessibility) — semantics and accessible UI.

Technically reviewed against primary documentation on 2026-10-13.

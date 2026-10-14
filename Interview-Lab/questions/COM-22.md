---
id: "COM-22"
question: "How do you support accessibility, screen readers, and adaptive layouts?"
topic: "Jetpack Compose"
code: "COM"
group: "B"
phase: 3
priority: "P1"
order: 251
editorial_status: "reviewed"
---

# COM-22

## Original interview question

How do you support accessibility, screen readers, and adaptive layouts?

## What the interviewer evaluates

- Address semantics, roles, labels, focus and touch targets.
- Adapt to window size and text scaling rather than device labels alone.
- Include RTL, screen-reader and real-device verification.

## Explanation in Arabic

كيفية دعم إمكانية الوصول (Accessibility)، وقارئات الشاشة (TalkBack)، والتصميمات المتكيفة (Adaptive Layouts) في Jetpack Compose:

1. دعم قارئات الشاشة (TalkBack) وشجرة الدلالات (Semantics Tree):
   - في Compose، يتم تمثيل واجهة المستخدم بشجرتين: شجرة الـ Layout وشجرة الـ **Semantics Tree** التي تقرأها خدمات إمكانية الوصول.
   - **ContentDescription**: إضافة وصف نصي واضح للأيقونات والصور غير التزيينية، ووضع `contentDescription = null` للأيقونات التزيينية فقط لتجاهلها.
   - **دمج الدلالات (Merge Descendants)**: عند وجود بطاقة تحتوي على عنوان وسعر وحالة، يجب استخدام `Modifier.semantics(mergeDescendants = true)` حتى يقرأ TalkBack البطاقة كوحدة واحدة متماسكة بضغطة واحدة بدلاً من إجبار المستخدم على النقر 4 مرات!
   - **Touch Targets**: الالتزام بالحد الأدنى لمساحة اللمس وهو **48dp × 48dp** لتسهيل النقر لذوي الاحتياجات الخاصة.

2. التصميمات المتكيفة (Adaptive Layouts) للشاشات الكبيرة والقابلة للطي:
   - استخدام **Window Size Classes** المعتمدة من Google (`Compact`, `Medium`, `Expanded`):
     * **Compact (الهواتف العادية)**: واجهة بعمود واحد (Single Pane).
     * **Medium / Expanded (الأجهزة اللوحية والقابلة للطي Foldables)**: واجهة متكيفة ذات لوحين (List-Detail Pane Scaffold).
   - تجنب فحص أبعاد البكسل الثابتة، واستخدام مكونات Material 3 Adaptive مثل `SupportingPaneScaffold` و `NavigationSuiteScaffold`.

## Practical walkthrough

تطبيق دمج الدلالات في TalkBack ودعم الـ Window Size Classes المتكيفة:
```kotlin
// 1. دمج دلالات بطاقة المنتج لقارئات الشاشة TalkBack:
@Composable
fun AccessibleProductCard(product: Product, onCardClick: () -> Unit) {
    Card(
        onClick = onCardClick,
        modifier = Modifier
            .fillMaxWidth()
            // دمج العناصر الداخلية ليقرأها TalkBack جملة واحدة متسلسلة:
            .semantics(mergeDescendants = true) {
                contentDescription = "Product ${product.name}, Price: ${product.price} dollars"
            }
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(product.name, style = MaterialTheme.typography.titleMedium)
            Text("$${product.price}", style = MaterialTheme.typography.bodyMedium)
        }
    }
}

// 2. تكييف الواجهة حسب فئة حجم الشاشة (WindowWidthSizeClass):
@Composable
fun AdaptiveHomeScreen(windowSizeClass: WindowWidthSizeClass) {
    when (windowSizeClass) {
        WindowWidthSizeClass.Compact -> SinglePaneFeed() // الهواتف العادية
        WindowWidthSizeClass.Medium, WindowWidthSizeClass.Expanded -> TwoPaneFeedWithDetail() // التابلت والـ Foldables
    }
}
```

## Why it matters and how it works

Accessibility services consume a semantics tree that can differ from the visual composable tree. Material components provide some built-in semantics, but custom controls need explicit meaning and actions. Window size can change at runtime through resizing or folding; adaptive layout should respond to current constraints. Large text and RTL can change line breaks, order and available target space.

## Worked example

A transaction row displays amount, merchant and a small receipt icon. Give the row a clear combined spoken description and an accessible “Open receipt” action, or keep icon action separately focusable if it does something distinct. On compact width use a single column; on expanded width show list/detail panes. Test TalkBack swipe order, keyboard focus, 200% font and Arabic layout with a resizable emulator.

### Compose/Kotlin walkthrough

```kotlin
@Composable
fun ReceiptAction(onOpen: () -> Unit) {
    IconButton(onClick = onOpen) {
        Icon(Icons.Default.Info, contentDescription = "Open receipt")
    }
}
@Composable
fun AdaptiveOrders(width: Dp, orders: List<OrderUi>) {
    if (width < 600.dp) OrdersList(orders)
    else Row { OrdersList(orders); OrderDetails() }
}
// Imports: material3.IconButton/Icon, material.icons.Icons,
// material.icons.filled.Info, ui.unit.Dp/dp.
// In production derive width from current window constraints/window size class.
```

## Trade-offs and decision criteria

Merged semantics reduce verbosity for a row but can hide independent actions, so choose based on interaction. Two-pane layouts use available width well but need state continuity when crossing breakpoints. Custom drawing affords control but requires more accessibility work than standard Material controls.

## Failure modes

A clickable Box has no role or label. Two actions are merged into one inaccessible node. A fixed-height card clips text at large font scale. Layout chooses tablet mode from device type and fails in split-screen. RTL reverses visual order without a sensible reading order.

## Production perspective

Add semantics assertions, automated accessibility checks where available, and hands-on TalkBack/keyboard tests. Maintain a matrix for compact/expanded windows, font scaling, dark mode and Arabic RTL; inspect focus after navigation or dialog changes.

## Interview answer — short

Support accessibility by populating the Semantics tree with meaningful `contentDescription`s, merging compound components with `Modifier.semantics(mergeDescendants = true)`, and ensuring minimum 48dp touch targets. Support adaptive layouts using Window Size Classes (Compact, Medium, Expanded) and Jetpack Compose Material 3 Adaptive components like List-Detail panes.

## Interview answer — structured

Building accessible and adaptive applications in Jetpack Compose is a core engineering requirement for global-scale products.

First, **Accessibility & Semantics**. Next, alongside the Layout Tree, Compose generates a parallel **Semantics Tree** consumed by Android Accessibility Services (TalkBack, Switch Access).
Every interactive element must supply meaningful semantics. Purely decorative icons must explicitly set `contentDescription = null` to prevent screen reader noise. For compound widgets (like a shopping cart item with title, image, and price), we apply `Modifier.semantics(mergeDescendants = true)`. This groups children into a single accessibility focus node, reading them as a coherent sentence rather than forcing frustrating sequential focus jumps.
We enforce a minimum **48dp × 48dp touch target** using `Modifier.minimumInteractiveComponentSize()`. **Adaptive Layouts**.
Rather than checking device models or orientation booleans, we categorize display width into canonical **Window Size Classes** (`Compact < 600dp`, `Medium 600-840dp`, `Expanded > 840dp`). Finally, on `Compact` screens, we show standard single-pane flows. On `Medium`/`Expanded` (foldables, tablets, Chromebooks), we render multi-pane layouts using Material 3 Adaptive components like `ListDetailPaneScaffold` and `NavigationSuiteScaffold`.


## Interview answer — deep senior

Under the hood, TalkBack navigates nodes using Android's `AccessibilityNodeInfo`. In Compose, custom actions can be exposed directly to TalkBack via `customActions`: `semantics { customActions = listOf(CustomAccessibilityAction("Delete item") { ... }) }`. This empowers users relying on screen readers to trigger secondary actions without hunting for small swipe gestures or nested overflow menus.

For adaptive design, foldable devices present dynamic hinge postures. Using Jetpack **WindowManager** and Compose's `FoldingFeature`, we detect tabletop and book postures, adjusting spacing so content isn't split awkwardly across a physical screen crease.

We automate accessibility verification in CI using Compose UI tests with `assertHasClickAction()`, `assertContentDescriptionEquals()`, and Android Studio's Accessibility Scanner, establishing strict zero-regression gates.


## How to answer in the interview

- **Why:** semantics and current window space determine usability.
- **How:** show a spoken action and a responsive branch.
- **Trade-off:** merged semantics can hide distinct actions.
- **Failure case:** color-only status or clipped large text.
- **Production solution:** test TalkBack, keyboard, RTL, resizing, and font scaling.

## Deep-dive talking points

Discuss semantics tree, roles/actions, merge policy, focus, current window size, fold changes, font scaling and RTL.

## Follow-up questions

- **Interviewer:** "What does `mergeDescendants = true` do in Compose semantics?"
  **Answer:** "It instructs accessibility services like TalkBack to treat the composable and all its child elements as a single unified semantic node, reading its contents together and combining click targets."

- **Interviewer:** "Why should touch targets never be smaller than 48dp x 48dp?"
  **Answer:** "Android accessibility guidelines require a minimum 48dp physical target size to accommodate users with motor impairments or vision difficulties and prevent accidental taps."

## Self-check rubric

Design one accessible row, choose an adaptive breakpoint response, and describe TalkBack/RTL verification.

## References and reviewed-on date

- [Compose semantics](https://developer.android.com/develop/ui/compose/accessibility/semantics) — accessibility meaning and actions.
- [Window size classes](https://developer.android.com/develop/adaptive-apps/guides/use-window-size-classes) — adaptive layout decisions.

Technically reviewed against primary documentation on 2026-10-13.

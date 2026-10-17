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

## Concept and technical explanation

Supporting accessibility, screen readers, and adaptive layouts in Jetpack Compose ensures inclusive, robust applications across all device form factors. Accessibility and screen readers like TalkBack are supported via the Compose Semantics Tree, where modifiers like Modifier.semantics define contentDescription, custom roles, click actions, and state descriptions, while mergeDescendants merges fragmented child elements into coherent interactive cards. Adaptive layouts are engineered using Material 3 WindowSizeClass (Compact, Medium, Expanded), swapping navigation rails, permanent drawers, and split-pane multi-column layouts like SupportingPaneScaffold to seamlessly support foldables, tablets, and desktop form factors.

## Practical walkthrough (English)

Implementing merged accessibility semantics and adaptive layout switching:
```kotlin
// 1. Accessibility: Merge descendants into a single coherent TalkBack item
@Composable
fun AccessibleUserCard(user: User, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .semantics(mergeDescendants = true) {
                // TalkBack announces this entire card as a single unified sentence!
                contentDescription = "User profile for ${user.name}, status is ${user.status}"
                role = Role.Button
            }
            .padding(16.dp)
    ) {
        Column {
            Text(user.name, style = MaterialTheme.typography.titleMedium)
            Text(user.status, style = MaterialTheme.typography.bodySmall)
        }
    }
}

// 2. Adaptive Layouts: Responsive UI switching via WindowSizeClass
@Composable
fun AdaptiveAppLayout(
    windowSizeClass: WindowSizeClass,
    content: @Composable () -> Unit
) {
    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> {
            // Standard Phone: Bottom Navigation Bar
            Scaffold(bottomBar = { BottomNavBar() }) { content() }
        }
        WindowWidthSizeClass.Medium -> {
            // Foldable / Small Tablet: Navigation Rail
            Row {
                AppNavRail()
                Box(modifier = Modifier.weight(1f)) { content() }
            }
        }
        WindowWidthSizeClass.Expanded -> {
            // Desktop / Large Tablet: Permanent Navigation Drawer + Split Pane
            PermanentNavigationDrawer(drawerContent = { DrawerContent() }) {
                content()
            }
        }
    }
}
```

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

We support accessibility and screen readers using the Semantics tree, applying Modifier.semantics with contentDescription, role, and mergeDescendants to unify complex cards for TalkBack, and ensuring a minimum 48dp touch target. For adaptive layouts, we use Material 3 WindowSizeClass, adapting navigation and layouts from compact phones using bottom navigation to medium foldables using navigation rails and expanded tablets using permanent drawers and split-pane scaffolds.

## Interview answer — structured

Building production applications that serve global audiences requires equal attention to assistive accessibility technologies and multi-device form factor adaptation.
For accessibility and screen readers like TalkBack, Jetpack Compose constructs a parallel Semantics Tree alongside the visual layout tree.
Instead of allowing TalkBack to read individual fragmented text labels—forcing vision-impaired users to swipe through multiple elements for a single item—we use Modifier.semantics(mergeDescendants = true).
This collapses all child nodes into a single semantic container, announcing a unified description and a clear Role like Role.Button.
Additionally, we enforce the Android accessibility guideline requiring a minimum interactive touch target of 48dp by 48dp using Modifier.minimumInteractiveComponentSize().
For adaptive layouts, modern Compose moves beyond rigid screen width checks by embracing Material 3 WindowSizeClass.
Classified into Compact (phones in portrait), Medium (foldables and small tablets), and Expanded (large tablets and desktop monitors), window size classes dictate responsive navigation patterns.
A phone displays a BottomNavigationBar, a foldable transitions to a NavigationRail, and an expanded tablet presents a dual-column ListDetailPaneScaffold, delivering an optimized user experience across all form factors.

## Interview answer — deep senior

Under the hood, Compose maintains two parallel node hierarchies: the LayoutNode tree for visual measurement and drawing, and the SemanticsNode tree for assistive accessibility services.
When an assistive technology like TalkBack or Switch Access connects to the Android system, the Android accessibility framework queries the app's View hierarchy.
Compose bridges this via AndroidComposeViewAccessibilityDelegateCompat.
This delegate translates Compose's SemanticsNode hierarchy into native Android AccessibilityNodeInfo objects.
When mergeDescendants is set to true on a modifier, the semantics pipeline merges the sub-tree's semantic properties into a single synthetic AccessibilityNodeInfo, suppressing individual child node traversal and drastically reducing screen reader navigation fatigue.
Custom accessibility actions can also be injected via customActions, allowing users to perform contextual actions (like deleting or archiving an email) through TalkBack menus without navigating to individual small action buttons.
Furthermore, enforcing the minimumInteractiveComponentSize modifier ensures touch targets expand invisible bounds to at least 48dp by 48dp, satisfying platform accessibility criteria even when visible icons measure only 24dp.
On the adaptive layout frontier, Compose Material 3 Adaptive integrates with AndroidX WindowManager.
It dynamically calculates WindowSizeClass from real-time window metrics, accounting for system bars, camera cutouts, and folding hinges.
Using canonical scaffold components like ListDetailPaneScaffold, Compose leverages the underlying Predictive Back and layout animation systems to automatically split or merge panes as devices fold, unfold, or rotate, maintaining uninterrupted user flow without manual activity restarts.

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

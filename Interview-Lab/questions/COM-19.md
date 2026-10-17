---
id: "COM-19"
question: "How do you implement a reusable design system and themes?"
topic: "Jetpack Compose"
code: "COM"
group: "B"
phase: 3
priority: "P1"
order: 248
editorial_status: "reviewed"
---

# COM-19

## Original interview question

How do you implement a reusable design system and themes?

## What the interviewer evaluates

- Build tokens and semantic components rather than copy-pasted styling.
- Support dynamic color, typography, shape, dark mode and accessibility.
- Balance central consistency with feature autonomy and versioning.

## Concept and technical explanation

Implementing a reusable design system and custom theme in Jetpack Compose involves creating a unified system of design tokens—Colors, Typography, Shapes, and Spacing—and distributing them through the composition tree via CompositionLocal. Rather than hardcoding styles or relying solely on standard MaterialTheme defaults, enterprise teams define strongly typed, immutable token models and wrap their application inside a custom Theme composable backed by CompositionLocalProvider. By exposing convenient accessor objects (such as AppTheme.colors and AppTheme.spacing), UI components consume standardized tokens with automatic dark mode adaptation, dynamic theming support, and zero performance overhead.

## Practical walkthrough (English)

Building a custom design system token hierarchy in Jetpack Compose:
```kotlin
// 1. Define custom design tokens (e.g. Spacing)
@Immutable
data class AppSpacing(
    val extraSmall: Dp = 4.dp,
    val small: Dp = 8.dp,
    val medium: Dp = 16.dp,
    val large: Dp = 24.dp,
    val extraLarge: Dp = 32.dp
)

// 2. Create static CompositionLocals (Static prevents re-evaluating the whole tree on reads!)
val LocalAppSpacing = staticCompositionLocalOf { AppSpacing() }

// 3. Custom Theme composable providing tokens
@Composable
fun AppDesignTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    spacing: AppSpacing = AppSpacing(),
    content: @Composable () -> Unit
) {
    CompositionLocalProvider(
        LocalAppSpacing provides spacing
    ) {
        MaterialTheme(content = content)
    }
}

// 4. Clean theme accessor object for developers
object AppTheme {
    val spacing: AppSpacing
        @Composable
        @ReadOnlyComposable
        get() = LocalAppSpacing.current
}

// 5. Usage in any UI component
@Composable
fun ThemedCard(title: String) {
    Card(modifier = Modifier.padding(AppTheme.spacing.medium)) {
        Text(title, modifier = Modifier.padding(AppTheme.spacing.small))
    }
}
```

## Explanation in Arabic

كيفية بناء نظام تصميم (Design System) وثيمات (Themes) قابلة لإعادة الاستخدام في Jetpack Compose:

1. ركائز نظام التصميم في Compose (Material 3 Foundations):
   - **الألوان (Color Scheme)**: لوحات ألوان متوافقة مع الوضع الفاتح والداكن (Light & Dark) ودعم Dynamic Color (Material You في أندرويد 12+).
   - **الخطوط والطباعة (Typography)**: أنماط نصية معيارية (`displayLarge`, `headlineMedium`, `bodySmall`) مبنية على كلاسات `TextStyle`.
   - **الأشكال والحدود (Shapes)**: مستويات استدارة الحواف (`extraSmall`, `medium`, `large`).

2. توفير الـ Theme عبر الـ CompositionLocal:
   - يقوم الثيم بتغليف المحتوى باستخدام `MaterialTheme(...)`.
   - يتم تمرير الألوان والخطوط ضمنياً عبر شجرة الـ Composition باستخدام `staticCompositionLocalOf` أو `compositionLocalOf`.
   - الوصول للألوان في أي مكان يكون عبر: `MaterialTheme.colorScheme.primary` دون الحاجة لتمرير الثيم كـ Parameter في كل دالة!

3. بناء سمات مخصصة تزيد عن Material Theme (Extended Design Tokens):
   - عندما تحتاج الشركة لرموز تصميم خاصة لا توجد في Material 3 (مثل ألوان تحذير خاصة، أبعاد Spacings موحدة، أو مقاسات أيقونات):
   - نقوم بإنشاء `data class AppSpacing(...)` و `CompositionLocalProvider(LocalAppSpacing provides customSpacing)`.
   - ننشئ Object مخصص للوصول: `AppTheme.spacing.medium`.

## Practical walkthrough

بناء Theme متكامل يدعم توكنز مخصصة للمسافات (Custom Spacing Tokens):
```kotlin
// 1. تعريف توكنز المسافات المخصصة:
@Immutable
data class AppSpacing(
    val extraSmall: Dp = 4.dp,
    val small: Dp = 8.dp,
    val medium: Dp = 16.dp,
    val large: Dp = 24.dp
)
val LocalAppSpacing = staticCompositionLocalOf { AppSpacing() }

// 2. إنشاء Theme مخصص يدمج MaterialTheme مع التوكنز الجديدة:
@Composable
fun EnterpriseAppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    val spacing = AppSpacing()

    CompositionLocalProvider(LocalAppSpacing provides spacing) {
        MaterialTheme(
            colorScheme = colorScheme,
            typography = AppTypography,
            shapes = AppShapes,
            content = content
        )
    }
}

// 3. كائن وصول سريع (Theme Accessor):
object AppTheme {
    val spacing: AppSpacing
        @Composable
        @ReadOnlyComposable
        get() = LocalAppSpacing.current
}
```

## Why it matters and how it works

A theme supplies ambient design values to a composition. Semantic roles let UI adapt without hard-coding a color for each screen. Reusable components wrap consistent behavior, semantics and styling while accepting caller layout decisions. An API that exposes domain entities directly creates dependency cycles and makes the design system hard to evolve.

## Worked example

An `AppPrimaryButton(text, enabled, loading, onClick, modifier)` applies theme colors, minimum touch target and loading semantics. Checkout and profile features reuse it without importing each other's models. A theme preview renders the button in light, dark, large text and Arabic RTL; a screenshot or semantic test checks regression.

### Compose/Kotlin walkthrough

```kotlin
@Composable
fun AcademyTheme(content: @Composable () -> Unit) {
    val colors = if (isSystemInDarkTheme()) darkColorScheme() else lightColorScheme()
    MaterialTheme(colorScheme = colors, content = content)
}
@Composable
fun AppPrimaryButton(
    label: String, loading: Boolean, onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Button(onClick = onClick, enabled = !loading, modifier = modifier) {
        if (loading) CircularProgressIndicator(Modifier.size(18.dp)) else Text(label)
    }
}
// Imports: material3.*, foundation.isSystemInDarkTheme,
// ui.Modifier, foundation.layout.size, ui.unit.dp.
```

## Trade-offs and decision criteria

Centralizing components reduces drift but can become a bottleneck if every feature variant is forced into one giant API. Prefer a small stable core and deliberate extension points. Dynamic color improves platform fit but may conflict with brand contrast; validate both. CompositionLocals simplify access to tokens but hide dependencies if overused for behavior.

## Failure modes

A screen hard-codes a light color and fails dark mode. Component ignores caller Modifier, so sizing and test tags break. A shared button has 20 Boolean flags for every team's exception. A design-system release changes padding globally without visual regression coverage. Text truncates at large font scale.

## Production perspective

Maintain documented token and component contracts, a preview/gallery matrix, screenshot/semantics tests, and accessibility review. Version changes with migration notes and measure affected screens before broad release.

## Interview answer — short

We implement a custom design system by defining strongly typed, immutable token models for Colors, Typography, Shapes, and Spacing, and providing them down the composition tree using staticCompositionLocalOf. A custom AppTheme composable wraps the content and provides these values via CompositionLocalProvider. We expose an accessor object like AppTheme.spacing and AppTheme.colors so UI components consume consistent design tokens that support dark mode and dynamic theming seamlessly.

## Interview answer — structured

Constructing a scalable, multiplatform design system in Jetpack Compose requires centralizing visual tokens and distributing them cleanly without prop drilling.
A robust design system standardizes four primary token pillars: Color palettes (supporting Light, Dark, and High-Contrast schemes), Typography scales, Shape definitions, and Spacing/Elevation dimensions.
The implementation begins by modeling these tokens as @Immutable data classes.
To expose tokens globally without passing them as parameters to every composable, we leverage CompositionLocal.
Choosing between compositionLocalOf and staticCompositionLocalOf is a crucial architectural decision.
For design system tokens that rarely change at runtime—such as typography styles, shapes, and spacing—we use staticCompositionLocalOf.
When a static CompositionLocal's value changes, Compose invalidates the entire content tree; however, because theme tokens change only during rare events like toggling dark mode, using static composition locals eliminates internal tracking overhead, speeding up normal frame execution.
Finally, we provide a unified AppTheme object with @ReadOnlyComposable accessors, enabling developers to write AppTheme.spacing.medium or AppTheme.colors.brandPrimary cleanly across all app modules.

## Interview answer — deep senior

Under the hood, CompositionLocal mechanisms govern token propagation throughout the Compose SlotTable hierarchy.
When a token is provided using CompositionLocalProvider, the Composer inserts a new entry into the ambient locals map for that subcomposition scope.
The architectural difference between compositionLocalOf and staticCompositionLocalOf centers on dependency tracking and invalidation scopes.
compositionLocalOf registers a snapshot read dependency whenever .current is read inside a composable function. If the provided value changes, the Compose runtime invalidates only the specific RecomposeScopes that read that token. However, this fine-grained tracking incurs a continuous memory and CPU cost to maintain read records in the SlotTable.
In contrast, staticCompositionLocalOf does not track individual consumer reads.
If a static token changes, the runtime conservatively re-executes the entire content lambda provided to CompositionLocalProvider.
Because design system tokens (such as Spacing dimensions, Typography fonts, and CornerRadius shapes) never change on a frame-by-frame basis—they change only during user-initiated theme toggles or system dark-mode switches—staticCompositionLocalOf is the mathematically optimal choice, delivering maximum runtime performance and zero memory bloat during standard rendering.
Furthermore, annotating accessor getters with @ReadOnlyComposable informs the Compose compiler that reading AppTheme.spacing produces no mutable state reads or slot writes, allowing the compiler to optimize the calling site into a direct property access.

## How to answer in the interview

- **Why:** semantic tokens and components keep behavior consistent.
- **How:** show theme role and component contract.
- **Trade-off:** a shared API must stay independent of feature models.
- **Failure case:** fixed sizing breaks Arabic large text.
- **Production solution:** preview and test themes, RTL, contrast, and semantics.

## Deep-dive talking points

Discuss semantic tokens, theme propagation, component API, caller Modifier, RTL/accessibility matrix, and governance.

## Follow-up questions

- **Interviewer:** "What is the difference between `compositionLocalOf` and `staticCompositionLocalOf`?"
  **Answer:** "`compositionLocalOf` tracks state reads and recomposes only the specific composables that read `.current`. `staticCompositionLocalOf` doesn't track individual reads; when its value changes, it recomposes the entire child tree. It is preferred for static theme values because it avoids tracking overhead."

- **Interviewer:** "Why should theme accessor properties be annotated with `@ReadOnlyComposable`?"
  **Answer:** "`@ReadOnlyComposable` signals to the Compose compiler that the getter reads composition locals but emits no UI nodes and does not restart or generate a recomposition group, saving bytecode size and runtime overhead."

## Self-check rubric

Name tokens and a component contract, cover accessibility and theme variants, and explain versioning.

## References and reviewed-on date

- [Theming in Compose](https://developer.android.com/develop/ui/compose/designsystems/material3) — Material theme design.
- [Accessibility in Compose](https://developer.android.com/develop/ui/compose/accessibility) — semantics and inclusive UI.

Technically reviewed against primary documentation on 2026-10-13.

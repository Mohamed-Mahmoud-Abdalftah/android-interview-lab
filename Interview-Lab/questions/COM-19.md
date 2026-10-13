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

Build reusable design systems in Compose using Material 3 themes providing `ColorScheme`, `Typography`, and `Shapes`. Extend custom branding tokens (like Spacings or elevation) using `staticCompositionLocalOf`, provide them via `CompositionLocalProvider`, and expose a clean accessor object like `AppTheme.spacing`.

## Interview answer — structured

A production-grade design system in Jetpack Compose is anchored on Material 3 foundations augmented with custom design tokens.

1. **Core Material 3 Contracts**: We define standard tokens using `lightColorScheme` and `darkColorScheme`, supporting Android 12+ dynamic theming via `dynamicLightColorScheme(context)` when appropriate. Typography is centralized in `Typography`, ensuring consistent scaling across accessibility font scales, and `Shapes` standardizes border radii.

2. **Custom Design Tokens (Extensions)**: Enterprise design systems frequently require dimensions that Material 3 does not model—such as standardized component paddings (`Spacing`), custom border widths, or domain-specific semantic colors (e.g. `cryptoGreen`, `fraudAlertRed`). We model these as immutable data classes and provide them through **`CompositionLocal`**:
   - `val LocalAppSpacing = staticCompositionLocalOf { AppSpacing() }`
   - In the top-level theme composable, we wrap the hierarchy with `CompositionLocalProvider(LocalAppSpacing provides spacing)`.

3. **Unified Accessor**: We provide an ergonomic theme accessor object `AppTheme` with `@ReadOnlyComposable` getters, allowing engineers to write `AppTheme.spacing.medium` with zero recomposition overhead.

## Interview answer — deep senior

The choice between `compositionLocalOf` and `staticCompositionLocalOf` is a key performance consideration. `staticCompositionLocalOf` does not track reads during composition; when its value changes, the **entire composition tree below the provider is recomposed from scratch**. Because design system tokens (colors, spacings, fonts) rarely or never change dynamically within a single user session (only on dark-mode toggle), `staticCompositionLocalOf` is drastically faster because it skips registering per-read slot observers.

In large design systems, we build custom UI component libraries (Buttons, InputFields, Cards) that enforce strict internal modifier rules. For example, an `AppButton` internally enforces standard touch targets (minimum 48dp for accessibility), applies `AppTheme.spacing` internal padding, and maps visual variants to semantic tokens, preventing inconsistent raw Material calls across feature teams.

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

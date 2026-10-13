---
id: "SYS-23"
question: "How would you migrate a large legacy XML app incrementally to Compose?"
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "C"
phase: 4
priority: "P1"
order: 352
editorial_status: "reviewed"
---

# SYS-23

## Original interview question

How would you migrate a large legacy XML app incrementally to Compose?

## What the interviewer evaluates

Migrate legacy XML UI to Compose incrementally without breaking behavior.

## Explanation in Arabic

كيف تهاجر تطبيق أندرويد ضخم وقديم مبني بـ XML View System إلى Jetpack Compose بشكل تدريجي وآمن؟

1. استراتيجية الهجرة الواقعية (Pragmatic Migration Strategy):
   - **قاعدة ذهبية**: تجنب فكرة "إعادة كتابة التطبيق بالكامل من الصفر (Complete Rewrite)"! إعادة الكتابة الكاملة تستغرق سنوات وتوقف تطوير الميزات وتخلق أخطاء جديدة غير متوقعة.
   - **الهجرة التدريجية (Incremental Migration)** هي الحل الصحيح والمعتمد في الشركات الكبرى (مثل Google, Twitter, Airbnb).

2. مسارات الهجرة التدريجية (Bottom-Up vs. Top-Down):
   - **Bottom-Up (من الأسفل للأعلى - الموصى به للميزات القائمة)**:
     * البدء بالمكونات الصغيرة المنعزلة (Leaf Views مثل الأزرار، الكروت، وقوائم الـ Dialogs) باستخدام `ComposeView` داخل ملفات الـ XML القديمة.
     * بعد تحويل عناصر القوائم، يتم استبدال `RecyclerView` بـ `LazyColumn`.
   - **Top-Down (من الأعلى للأسفل - للميزات الجديدة بالكامل)**:
     * أي شاشة جديدة تُبنى بنسبة 100% بـ Jetpack Compose داخل `ComponentActivity.setContent`.

3. جسر نظام التصميم (Design System Bridging):
   - توحيد الـ Themes: ربط ألوان وخطوط وأشكال الـ XML القديمة (`Theme.MaterialComponents`) برموز الـ Compose `MaterialTheme` حتى تبدو شاشات الـ XML وشاشات الـ Compose متطابقة تماماً للمستخدم.

4. التعايش وإدارة دورة الحياة (Interoperability & Lifecycle):
   - استخدام `ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed` لمنع تسريب الذاكرة عند استخدام Compose داخل Fragments.

## Practical walkthrough

دمج Compose داخل Fragment قديم يعتمد على XML وتطبيق استراتيجية التخلص الآمن من الذاكرة:
```kotlin
class LegacyProfileFragment : Fragment(R.layout.fragment_legacy_profile) {
    private val viewModel: ProfileViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        // 1. العثور على الـ ComposeView المدمج داخل ملف الـ XML القديم:
        val composeView = view.findViewById<ComposeView>(R.id.compose_header_container)
        
        composeView.apply {
            // 2. إلزامي: ضبط استراتيجية التخلص من الـ Composition لمنع تسريب الذاكرة مع دورة حياة الـ Fragment:
            setViewCompositionStrategy(ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed)
            
            setContent {
                // 3. تغليف الـ Composable بنظام الـ Theme الموحد:
                AppTheme {
                    val profileState by viewModel.uiState.collectAsStateWithLifecycle()
                    ProfileHeaderComponent(
                        state = profileState,
                        onEditClicked = { navigateToEditProfile() }
                    )
                }
            }
        }
    }
}
```

## Why it matters and how it works

Interop enables coexistence of Views and Compose. Move state ownership to ViewModel/Flow, collect lifecycle-aware, and avoid duplicating sources of truth between mutable LiveData/View state/Compose state. Release gradually behind flags; test configuration change, process death, accessibility and performance.

## Worked example

Conceptual Fragment interop; Compose dependencies/theming and app ViewModel are assumed.

```kotlin
import androidx.compose.ui.platform.ComposeView
import androidx.compose.ui.platform.ViewCompositionStrategy
import androidx.fragment.app.Fragment

class ProfileFragment : Fragment() {
    override fun onCreateView(inflater: android.view.LayoutInflater,
        container: android.view.ViewGroup?, state: android.os.Bundle?): android.view.View =
        ComposeView(requireContext()).apply {
            setViewCompositionStrategy(
                ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed
            )
            setContent { ProfileScreen() }
        }
}
// ProfileScreen is the app composable and uses the existing ViewModel state.
```

## Trade-offs and decision criteria

Incremental migration reduces release risk but temporarily maintains two UI stacks and design systems. Big-bang rewrite may simplify final architecture but risks feature freeze. Interop has lifecycle/performance edges; test each bridge.

## Failure modes

Creating a new repository for Compose while XML uses old one yields inconsistent session state. Missing ViewCompositionStrategy can retain composition beyond view lifecycle. Doing network call directly in composable can repeat on recomposition.

## Production perspective

A large banking app migrates noncritical settings screen first, shares existing ViewModel/repository, creates Compose design tokens, adds screenshot/accessibility tests and monitors startup/jank. Payment flow migrates later with dual-path validation.

## Interview answer — short

Migrate legacy XML to Jetpack Compose incrementally: build new screens entirely in Compose, migrate existing screens bottom-up by embedding ComposeView into XML layouts with DisposeOnViewTreeLifecycleDestroyed, bridge themes via MaterialTheme wrappers, and replace RecyclerViews with LazyColumns gradually.

## Interview answer — structured

Migrating an enterprise Android app from the View system to Jetpack Compose requires an incremental coexistence strategy rather than a risky all-at-once rewrite:

1. **Pragmatic Migration Direction**:
   - **Top-Down for New Features**: Mandate that all net-new screens are written exclusively in 100% Jetpack Compose using `ComponentActivity.setContent { }`.
   - **Bottom-Up for Existing Screens**: Convert leaf components (buttons, custom cards, headers) first. Embed them inside legacy XML layouts using `ComposeView`.

2. **Lifecycle & Memory Management in Fragments**:
   - In Android Fragments, the Fragment View lifecycle is distinct from the Fragment instance lifecycle. When using `ComposeView` in Fragments, always set `setViewCompositionStrategy(ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed)`. Failing to do so leaks View compositions across fragment backstack transactions.

3. **Design System & Theme Bridging**:
   - Maintain visual parity by bridging your existing XML theme attributes into Compose `MaterialTheme` tokens (using `accompanist/themeadapter-material` or custom mappers). This ensures that XML views and Compose widgets share identical colors, shapes, and typography during migration.

4. **RecyclerView to LazyColumn Transition**:
   - As individual `ViewHolder` items are migrated to Composables, avoid leaving hundreds of tiny `ComposeView` wrappers inside a `RecyclerView` due to layout measurement overhead. Once item viewholders are composed, replace the parent `RecyclerView` with a native Compose `LazyColumn`.

## Interview answer — deep senior

From an architectural governance and performance perspective, managing hybrid View/Compose runtimes requires strict profiling:

1. **Interoperability Layout Overhead**: Nesting Views inside Compose via `AndroidView` or nesting Compose inside Views via `ComposeView` incurs measurement overhead. Hybrid lists with `ComposeView` inside `RecyclerView` can drop frames during fast flings unless items use fixed height modifiers or enable Baseline Profiles.

2. **Baseline Profiles for Startup & Jank**: Jetpack Compose relies on runtime compilation (AOT/JIT). Uncompiled Compose code can cause significant jank on first run. Generate and bundle **Baseline Profiles** using Macrobenchmark to pre-compile critical Composable paths during app installation, restoring 60fps scrolling.

3. **State Management Bridging**: Legacy ViewModels exposing `LiveData` should be converted to reactive `StateFlow`. In Compose, observe them via `collectAsStateWithLifecycle()` to automatically halt collection when the host Activity/Fragment is backgrounded.

## How to answer in the interview

- **Why:** migration should preserve user behavior while reducing risk.
- **How:** introduce ComposeView at one seam and retain shared state contracts.
- **Trade-off:** hybrid UI temporarily duplicates theme/navigation work.
- **Failure case:** composition outlives Fragment view or accessibility regresses.
- **Production solution:** release slices, lifecycle strategy, performance and accessibility tests.

## Deep-dive talking points

Trace one screen migration, lifecycle interop and performance evidence.

## Follow-up questions

- **Interviewer:** "Why is DisposeOnViewTreeLifecycleDestroyed required in Fragments?"
  **Answer:** "Because a Fragment's view can be destroyed while the Fragment instance remains in memory; this strategy disposes the composition when the view hierarchy is detached, preventing memory leaks."

- **Interviewer:** "How do you embed a legacy custom Android View inside a Jetpack Compose screen?"
  **Answer:** "Using the AndroidView composable: AndroidView(factory = { context -> LegacyCustomView(context) }, update = { view -> view.setData(...) })."

## Self-check rubric

Can I migrate incrementally, avoid dual truth and test ComposeView lifecycle?

## References and reviewed-on date

- [Android Compose interop](https://developer.android.com/develop/ui/compose/migrate/interoperability-apis) — Views/Compose bridge.
- [ComposeView in Fragments](https://developer.android.com/develop/ui/compose/migrate/interoperability-apis/compose-in-views) — composition disposal with the view lifecycle.
- [Android architecture guide](https://developer.android.com/topic/architecture) — state ownership.

Technically reviewed against primary documentation on 2026-10-13.

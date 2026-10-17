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

## Concept and technical explanation

Migrating a large-scale enterprise Android application with hundreds of legacy XML layouts and ViewBinding screens to Jetpack Compose requires a disciplined, incremental migration strategy rather than a risky whole-app rewrite. Big-bang rewrites introduce severe business regressions, stall product feature delivery, and risk introducing subtle UI discrepancies. A production-ready migration follows a bottom-up leaf-node progression: begin by porting design system components, color palettes, typography styles, and atomic custom views to Compose. Next, embed these new Compose components inside existing XML layouts using ComposeView, ensuring the ViewCompositionStrategy is explicitly set to DisposeOnViewTreeLifecycleDestroyed to prevent memory leaks with Fragment lifecycles. New screens and features are authored entirely in pure Compose. Over time, parent Fragments and Activities are refactored into pure Compose destinations, systematically retiring legacy XML files while maintaining a single, uninterrupted product release cadence.

## Practical walkthrough (English)

Embedding Compose components inside legacy XML Fragments with lifecycle safety:
```kotlin
// 1. Embedding a Compose header inside an existing XML Fragment layout
class LegacyUserProfileFragment : Fragment(R.layout.fragment_user_profile) {
    private val viewModel: UserProfileViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Locate the ComposeView embedded inside the legacy XML layout
        val composeHeaderView = view.findViewById<ComposeView>(R.id.compose_header_container)

        composeHeaderView.apply {
            // Mandatory: Configure lifecycle disposition strategy to prevent memory leaks in Fragments
            setViewCompositionStrategy(ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed)

            setContent {
                AppTheme {
                    val userState by viewModel.userState.collectAsStateWithLifecycle()
                    UserProfileHeader(
                        user = userState,
                        onAvatarClicked = { viewModel.onAvatarClicked() }
                    )
                }
            }
        }
    }
}

// 2. Pure Jetpack Compose component replacing legacy custom XML view
@Composable
fun UserProfileHeader(
    user: UserProfileState,
    onAvatarClicked: () -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        AsyncImage(
            model = user.avatarUrl,
            contentDescription = "User Avatar",
            modifier = Modifier
                .size(64.dp)
                .clip(CircleShape)
                .clickable { onAvatarClicked() }
        )
        Spacer(modifier = Modifier.width(16.dp))
        Column {
            Text(text = user.fullName, style = MaterialTheme.typography.titleMedium)
            Text(text = user.email, style = MaterialTheme.typography.bodyMedium)
        }
    }
}
```

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

We migrate legacy XML applications to Compose incrementally using a bottom-up approach. We migrate atomic design system components first, embedding them into XML layouts via ComposeView with lifecycle disposal strategies. We build all new features purely in Compose, gradually refactoring parent screens without stalling roadmap feature velocity.

## Interview answer — structured

Migrating a large legacy Android application to Jetpack Compose must be executed incrementally to prevent feature freezes and UI regressions.
I reject high-risk big-bang rewrites in favor of a bottom-up component migration.
We begin at the design system foundation, porting theme attributes, color tokens, typography, and atomic UI widgets like buttons, input fields, and badges to Compose.
These composables are integrated directly into existing XML layouts using ComposeView.
When embedding Compose inside Fragments, setting ViewCompositionStrategy to DisposeOnViewTreeLifecycleDestroyed is mandatory to prevent composition memory leaks when the Fragment view is destroyed.
Next, all newly requested product features are built in pure Compose from day one.
Finally, we migrate screen-level containers. Complex RecyclerViews are converted to LazyColumns, and parent Fragments are gradually retired in favor of Compose destinations, keeping the app stable and continuously releasable throughout the migration.

## Interview answer — deep senior

From a staff engineering perspective, migrating to Compose is as much an architectural state-management alignment as it is a UI framework change.
The most common mistake teams make during migration is duplicating state holders. In a hybrid codebase, an XML screen and an embedded ComposeView must observe the exact same ViewModel StateFlow stream. Using collectAsStateWithLifecycle in Compose ensures that composable rendering pauses automatically when the hosting lifecycle drops below the Started state, matching the lifecycle behavior of ViewBinding.
Performance must be monitored vigilantly during hybrid coexistence. Running ComposeView inside every item of a legacy RecyclerView creates severe frame drops because the composition runtime is repeatedly initialized and disposed during scrolling. The correct approach is either migrating the entire list to a LazyColumn at once, or converting individual complex screens rather than scattering micro-composables inside scrolling view holders.
Furthermore, interoperability must handle third-party legacy views that lack native Compose equivalents, such as MapView, AdViews, or CameraX previews. We bridge these using AndroidView wrappers with explicit update lambdas, ensuring seamless two-way binding.
Finally, we track migration progress through automated dashboard metrics, measuring the ratio of Composable functions versus XML layout files in CI, providing leadership with clear visibility into code health improvements and bundle size reductions.

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

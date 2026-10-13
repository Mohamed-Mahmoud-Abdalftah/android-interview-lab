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

نبدأ screen أو component صغيرة، نثبت state holder وrepository contract، ونضيف `ComposeView` داخل Fragment أو نستخدم AndroidView لlegacy view عند الحاجة. نبقي navigation, theming, accessibility وtest IDs متسقة، ونقارن behavior/performance قبل نقل بقية الشاشات. Compose recomposition لا تعني إعادة تنفيذ كل شيء دائمًا؛ state immutable وside effects APIs الصحيحة تمنع شغل مكرر.

## Practical walkthrough

ابدأ component صغيرة داخل Fragment ب`ComposeView` وstrategy تتقفل مع view lifecycle، وخلي نفس ViewModel/Repository عشان ما تعملش business state مزدوجة. وحّد theme وnavigation وaccessibility/test tags، وقس startup وscroll jank قبل وبعد. XML وCompose يعيشوا سوا فترة؛ نقل الشاشة كلها مرة واحدة بيزود risk، خصوصًا لو legacy views فيها focus أو accessibility behavior حساس.

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

“I migrate screen by screen using View/Compose interop, keep one ViewModel/repository source of truth, and verify lifecycle, navigation, accessibility and performance before widening rollout.”

## Interview answer — structured

“A big-bang rewrite is rarely necessary. I choose a bounded screen, embed Compose in an existing Fragment or host legacy Views from Compose, and keep the same ViewModel and repository contract. State is collected with lifecycle awareness, while themes, navigation and accessibility stay consistent. I configure composition disposal to the view lifecycle, avoid side effects during recomposition, and test rotation, process death and UI parity. I stage rollout and measure jank rather than assuming Compose is automatically faster.”

## Interview answer — deep senior

“I would migrate a large XML app as a sequence of compatible slices, starting with a low-risk screen that has clear behavior and accessibility tests. A Fragment can host Compose through `ComposeView`, with `DisposeOnViewTreeLifecycleDestroyed` tying the composition to the Fragment view; the existing ViewModel and repository remain the single source of business state. I would collect state with lifecycle awareness and route user actions through the same event contract as XML, so recomposition cannot accidentally repeat a network write. During coexistence, design tokens, navigation destinations, back behavior, focus order and saved state need adapters and parity checks. I would compare startup, scroll jank, screenshot output and screen-reader behavior on supported devices, then roll out by cohort with a rollback switch. The goal is to replace rendering technology without changing payment or session semantics in the same release. High-risk checkout screens come after the bridge and test strategy have proven stable; an all-at-once rewrite would make regressions much harder to isolate.”

## How to answer in the interview

- **Why:** migration should preserve user behavior while reducing risk.
- **How:** introduce ComposeView at one seam and retain shared state contracts.
- **Trade-off:** hybrid UI temporarily duplicates theme/navigation work.
- **Failure case:** composition outlives Fragment view or accessibility regresses.
- **Production solution:** release slices, lifecycle strategy, performance and accessibility tests.

## Deep-dive talking points

Trace one screen migration, lifecycle interop and performance evidence.

## Follow-up questions

- [SYS-16](../sys-16/): Does UI toolkit change business layers? **Answer:** no, state/repository ownership can stay stable.
- [SYS-17](../sys-17/): What rollout metric? **Answer:** jank, crash/ANR and business error by migrated cohort.

## Self-check rubric

Can I migrate incrementally, avoid dual truth and test ComposeView lifecycle?

## References and reviewed-on date

- [Android Compose interop](https://developer.android.com/develop/ui/compose/migrate/interoperability-apis) — Views/Compose bridge.
- [ComposeView in Fragments](https://developer.android.com/develop/ui/compose/migrate/interoperability-apis/compose-in-views) — composition disposal with the view lifecycle.
- [Android architecture guide](https://developer.android.com/topic/architecture) — state ownership.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.

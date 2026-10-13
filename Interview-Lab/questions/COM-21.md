---
id: "COM-21"
question: "What is NavHost, and how is state restored after process death?"
topic: "Jetpack Compose"
code: "COM"
group: "B"
phase: 3
priority: "P1"
order: 250
editorial_status: "reviewed"
---

# COM-21

## Original interview question

What is NavHost, and how is state restored after process death?

## What the interviewer evaluates

- Explain navigation graph/back-stack ownership in Navigation Compose.
- Separate saved navigation/UI state from ViewModel and durable data.
- Test deep link and process recreation without overclaiming restoration.

## Explanation in Arabic

في Navigation Compose، `NavHost` يربط NavController بالـnavigation graph وdestinations؛ لكل back-stack entry lifecycle وsaved state وViewModel ownership مناسب. عند system-initiated process death قد يعيد Android/Navigation حفظ back stack والarguments الصغيرة، لكن ViewModel instance لا تعيش؛ أعد إنشاءها واسترجع ID من `SavedStateHandle` ثم حمّل البيانات من repository. `rememberSaveable` لحالة UI صغيرة داخل destination. لا تعتمد على object كبير أو singleton in-memory وحده. تأكد من الإعدادات والنسخة وتجربة kill/recreate فعليًا.

## Practical walkthrough

`NavHost` تعرض destination من back stack. لو Android رجّع task بعد process death، الـViewModel جديدة؛ استخدم `articleId` المحفوظ في args/`SavedStateHandle` لتحميل المقال من repository. `rememberSaveable` يصلح لتبويب صغير؛ لو المقال اتحذف، اعرض error بدل محاولة استرجاع object قديم من الذاكرة. استرجاع route لا يضمن إن المقال ما زال موجودًا؛ لازم Error واضحة لو ID اتحذف أو user فقد الصلاحية. اختبر eligible process death بالـID وبحالة data اتغيرت.

## Why it matters and how it works

The navigation host renders the current destination from a back stack. Back-stack entries provide owners for lifecycle, ViewModel and saved state, so scope choice affects retention and restoration. Android saved-state mechanisms can restore small navigation/UI information after eligible system recreation; they do not persist arbitrary process memory or unfinished external work. Durable business data belongs in a repository or persistent store.

## Worked example

An article route passes `articleId`, not an `Article` object. The destination ViewModel reads that ID from its saved-state handle and loads the article. A local selected tab uses saveable state. After system process recreation, NavHost returns to the article destination if the platform restores the task, the ViewModel is new, and it reloads by ID; a deleted article shows a valid error state.

### Compose/Kotlin walkthrough

```kotlin
// Navigation graph; article destination reads only a small stable ID.
@Composable
fun ArticleGraph(navController: NavHostController) {
NavHost(navController, startDestination = "feed") {
    composable("feed") { FeedScreen(onOpen = { id ->
        navController.navigate("article/$id")
    }) }
    composable("article/{articleId}") { entry ->
        val id = requireNotNull(entry.arguments?.getString("articleId"))
        ArticleRoute(articleId = id)
    }
}
}
// Imports: androidx.navigation.NavHostController, navigation.compose.NavHost/composable;
// encode arbitrary IDs
// before route interpolation, or use supported typed routes.
```

## Trade-offs and decision criteria

Small route arguments are robust and deep-linkable but require reloading. Saving large objects avoids a fetch only superficially and risks Bundle size/version problems. Graph-scoped ViewModels can share state across destinations, but overly broad ownership may leak stale flows. Navigation library generations differ; describe behavior for the installed version.

## Failure modes

The app assumes a ViewModel survives process death. A route serializes a large mutable entity. A destination depends on an in-memory Singleton cache and opens blank after restoration. A back-stack entry is scoped incorrectly, causing a prior account's state to reappear. A user-dismissed task is treated as guaranteed to restore.

## Production perspective

Test rotation, background system process death, deep links, and missing/stale IDs separately. Inspect saved-state size, use durable storage for user work, and add a loading/recovery path while data reloads.

## Interview answer — short

“NavHost displays destinations from a NavController back stack. After eligible process recreation, restore small navigation/UI identifiers and rebuild new ViewModels that reload durable data. NavHost restores destination identity when eligible; the new ViewModel reloads by ID.”

## Interview answer — structured

“I define destinations in NavHost and use the back-stack entry as the intended lifecycle and ViewModel owner. I navigate with a small ID. Navigation and saved-state mechanisms can restore the destination and arguments after system recreation, but the ViewModel instance and in-memory repository cache are gone. The new ViewModel reads the ID from `SavedStateHandle`, reloads the entity, and handles missing data. I save only small UI choices locally and test real process recreation. An article route passes articleId, and its recreated owner asks the repository for current content.”

## Interview answer — deep senior

“NavHost is the Navigation Compose boundary that renders a graph's current back-stack entry, with entry-specific lifecycle, saved state and ViewModel ownership. That owner is important: an Activity-scoped ViewModel can unintentionally share one destination's state with another, while a destination-scoped one is recreated when its entry is removed. For restoration I pass a stable article ID in the route, not an entire domain object. On eligible system process death, Android and Navigation can restore small back-stack and argument state; the old ViewModel and caches do not survive. A new ViewModel obtains the ID from saved state and reloads article data from durable storage or network, showing loading and an error if the item no longer exists. A selected tab or draft text can use `rememberSaveable` or saved-state handle when small and appropriate. I avoid promising restoration after every user-initiated dismissal or arbitrary kill path. I test rotation, system recreation, deep link entry, stale IDs and back navigation on the installed Navigation version. Any in-flight high-value action needs its own durable recovery and idempotency, independent of NavHost restoration. I include a deleted-article error path because restoring an ID does not guarantee the resource still exists.”

## How to answer in the interview

- **Why:** a back stack restores destination identity, not process memory.
- **How:** pass ID, recreate owner, reload authoritative data.
- **Trade-off:** saved state is small and restoration is platform-conditional.
- **Failure case:** in-memory singleton or large argument disappears.
- **Production solution:** test eligible process recreation and deleted-content errors.

## Deep-dive talking points

Discuss back-stack owners, saved arguments, ViewModel recreation, durable reload, deep links, and test conditions.

## Follow-up questions

- Does NavHost preserve a ViewModel object after process death? **Answer:** no; a new process constructs a new instance.
- Why pass an ID instead of a domain object? **Answer:** small stable arguments restore and deep-link more reliably; data can be reloaded.
- Is every task guaranteed to restore? **Answer:** no; behavior depends on system-initiated saved-state conditions and task lifecycle.

## Self-check rubric

Trace one route through process recreation, assign owners, and handle stale data and non-restoration cases.

## References and reviewed-on date

- [Navigation with Compose](https://developer.android.com/develop/ui/compose/navigation) — NavHost and destination practices.
- [Save UI state in Compose](https://developer.android.com/develop/ui/compose/state-saving) — process recreation limits.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Exact restoration depends on platform and Navigation version.

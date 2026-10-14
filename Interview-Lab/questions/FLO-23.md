---
id: "FLO-23"
question: "What happens if a UI collects indefinitely without lifecycle awareness?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "B"
phase: 1
priority: "P1"
order: 136
editorial_status: "reviewed"
---

# FLO-23

## Original interview question

What happens if a UI collects indefinitely without lifecycle awareness?

## What the interviewer evaluates

Explain continued offscreen collection, view retention and cold-source cost.

## Explanation in Arabic

ماذا يحدث إذا قامت واجهة المستخدم بجمع تدفقات البيانات إلى ما لا نهاية دون مراعاة دورة الحياة (Without Lifecycle Awareness)؟

1. استنزاف البطارية وموارد الجهاز في الخلفية (Resource & Battery Drain):
   - لو التطبيق وضع في الخلفية (المستخدم ضغط Home button أو قفل الشاشة)، الـ Flow سيظل يطلب بيانات من السيرفر، يقرأ من الـ Database، ويفحص إحداثيات الـ GPS كل ثانية!
   - نظام أندرويد يعتبر هذا 'Bad Behavior' ويسجله في Google Play Console كـ Background CPU Spikes مما يخفض تقييم التطبيق.

2. تسريب الذاكرة (Memory Leaks):
   - الـ Collector يحمل مراجع لكائنات الـ UI (Views, Fragments, Composables). بقاء الـ Coroutine نشطة في الخلفية يمنع الـ Garbage Collector من تحرير هذه الكائنات.

3. انهيار التطبيق (Crashes & Illegal State):
   - محاولة تعديل View أو تشغيل Navigation Transaction أثناء وجود الشاشة في حالة `STOPPED` يرمي `IllegalStateException: Can not perform this action after onSaveInstanceState`.

4. الحل:
   - استخدام `repeatOnLifecycle` في الـ Views، و `collectAsStateWithLifecycle()` في Compose.

## Practical walkthrough

تحليل العطل الناتج عن الجمع الخاطئ:
```kotlin
// ❌ الجمع الكارثي بدون lifecycle awareness:
lifecycleScope.launch {
    viewModel.locationFlow.collect { location ->
        // عندما يكون التطبيق في الخلفية، الـ GPS يعمل بأقصى طاقة ويسحب البطارية!
        // وإذا حاول تنفيذ navigation هنا:
        findNavController().navigate(R.id.action_next) // CRASH: IllegalStateException!
    }
}

// ✅ الجمع الآمن دورياً:
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.locationFlow.collect { location ->
            updateMapPin(location) // يتوقف تماماً عند الخروج للـ Background!
        }
    }
}
```

## Why it matters and how it works

LifecycleScope cancellation happens at owner destruction, not at every STOP. `repeatOnLifecycle` cancels and relaunches the inner collection at configured states. `viewLifecycleOwner` matches Fragment view lifetime. Upstream sharing can prevent repeated expensive source setup on transient stops.

## Worked example

Android conceptual snippet; in a Fragment, `state` is StateFlow and `render` is app code.

```kotlin
import androidx.fragment.app.Fragment
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

// Call after Fragment.onViewCreated; stops collection below STARTED.
fun Fragment.collectVisible(flow: StateFlow<String>, render: (String) -> Unit) {
    viewLifecycleOwner.lifecycleScope.launch {
        viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
            flow.collect { render(it) }
        }
    }
}
// Avoid collecting against Fragment.lifecycle when render touches its View.
```

## Trade-offs and decision criteria

Stopping collection saves offscreen work but can miss ephemeral replay-zero events. StateFlow resumes with current value, which is appropriate for state. For required events, persist/acknowledge them rather than collecting forever to avoid loss.

## Failure modes

A collector tied to Fragment lifecycle can retain a destroyed view after onDestroyView. Even if no leak occurs, an offscreen collector can keep a socket or sensor active. A cold source may re-register on each START; sharing policy should be deliberate.

## Production perspective

A location screen collects a ViewModel StateFlow only while STARTED and unregisters callbackFlow listener when inactive. A worker maintains necessary background location only under Android’s supported background execution rules, separate from a hidden UI collector.

## Interview answer — short

Collecting without lifecycle awareness continues active flow processing in the background, causing severe battery drain, continuous CPU/network usage, potential memory leaks from retained view references, and fatal runtime crashes like IllegalStateException when attempting navigation while the activity is stopped.

## Interview answer — structured

Collecting flows indefinitely without lifecycle awareness (such as launching directly in `lifecycleScope.launch` without `repeatOnLifecycle`, or using plain `collectAsState()` in Compose) leads to three severe production defects.

First, **Severe Battery and Network Drain:** If the flow is connected to an upstream sensor, location updates, WebSocket, or polling repository, collection remains completely active even when the phone is locked in a user's pocket. Google Play Console will flag the app for excessive background execution and wake-locks. Next, **Memory Leaks:** The active coroutine retains references to the View or Composable in its closure. If the user navigates between screens, destroyed views cannot be garbage-collected as long as the background collection coroutine is alive.
Finally, **IllegalState Crashes:** When an emission arrives while the app is in the background, attempting to trigger fragment navigation or show dialogs throws `IllegalStateException: Can not perform this action after onSaveInstanceState`.

Enforcing `repeatOnLifecycle(STARTED)` or `collectAsStateWithLifecycle()` eliminates all these issues by pausing collection the moment the UI leaves the foreground.


## Interview answer — deep senior

At the systems level, Android's OS kernel prioritizes foreground processes (OOM adj 0) and demotes background apps down the OOM adj score list. If a background app continuously spins CPU threads or makes network sockets because of an unpaused Flow collection, Android's system watchdog detects high battery consumption via Batterystats and issues a warning in Android Vitals.

Furthermore, pairing lifecycle-aware collectors with `WhileSubscribed(5000)` in the ViewModel creates an end-to-end reactive circuit: When `repeatOnLifecycle` cancels the collector upon entering `STOPPED`, the ViewModel's `StateFlow.subscriptionCount` drops to 0. After 5 seconds, the ViewModel shuts down upstream Room or Network observations, freeing SQLite cursor locks and closing network sockets at the operating system level.


## How to answer in the interview

- **Why:** DESTROYED is later than offscreen STOPPED.
- **How:** tie UI collection to STARTED and view owner.
- **Trade-off:** restart may re-run cold upstream.
- **Failure case:** hidden screen keeps sensor or render work active.
- **Production solution:** lifecycle tests and upstream audit.

## Deep-dive talking points

Trace STOP versus DESTROY, Fragment view lifecycle and no-subscriber event behavior.

## Follow-up questions

- **Interviewer:** "Why did `lifecycleScope.launchWhenStarted` get deprecated?"
  **Answer:** "`launchWhenStarted` only paused execution; it did NOT cancel the coroutine. The upstream flow continued emitting items in the background, buffering them in memory until the app resumed, which still wasted CPU, network bandwidth, and memory."

- **Interviewer:** "How does `repeatOnLifecycle` differ from `launchWhenStarted`?"
  **Answer:** "`repeatOnLifecycle` actively cancels the collection coroutine when leaving the target state and relaunches a fresh coroutine when re-entering, allowing upstream flows to clean up and shut down completely."

- **Interviewer:** "Can a background worker still collect flows safely?"
  **Answer:** "Yes, in a background Service or WorkManager task, flow collection is governed by the worker's own CoroutineScope, which terminates when the background work completes."

## Self-check rubric

Can I explain offscreen cost, bind a Fragment view correctly and preserve required events independently?

## References and reviewed-on date

- [Android lifecycle coroutines](https://developer.android.com/topic/libraries/architecture/coroutines) — collection recommendations.

Technically reviewed against primary documentation on 2026-10-13.

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

## Concept and technical explanation

Collecting asynchronous data streams indefinitely in Android UI layers without lifecycle awareness triggers severe architectural failure modes: chronic memory leaks, background battery exhaustion, wasted cellular bandwidth, and fatal UI state corruption.
When a collection coroutine is launched directly in a non-lifecycle scope—such as GlobalScope, an uncancelled custom CoroutineScope, or improperly using lifecycleScope.launch without repeatOnLifecycle—the collection loop continues executing indefinitely after the Activity, Fragment, or Composable transitions to the background.
If the underlying flow connects to persistent physical sources (such as hardware GPS providers, Bluetooth Low Energy scanners, camera frames, or long-lived WebSocket connections), the device hardware radios remain fully powered, draining mobile battery rapidly. Furthermore, collecting inside a backgrounded UI frame can trigger IllegalStateException crashes if the collector tries to mutate Fragment view hierarchies, commit FragmentTransactions, or show DialogFragments when the window state is already saved.

## Practical walkthrough (English)

Demonstrating the dangers of unmanaged collection versus lifecycle safety:
```kotlin
class DangerousFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ❌ CATASTROPHIC ANTI-PATTERN:
        // Continues collecting when app is backgrounded, leaking GPS hardware and battery!
        lifecycleScope.launch {
            locationRepository.observeGpsUpdates().collect { location ->
                // If this attempts Fragment transaction after onSaveInstanceState: CRASH!
                updateCoordinatesOnMap(location)
            }
        }

        // ✅ SAFE PRODUCTION PATTERN:
        // Cancels upstream collection when app is in background, frees GPS hardware:
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                locationRepository.observeGpsUpdates().collect { location ->
                    updateCoordinatesOnMap(location)
                }
            }
        }
    }
}
```

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

Collecting a flow indefinitely without lifecycle awareness keeps background coroutines alive, causing severe memory leaks, battery exhaustion from active GPS or network sockets, wasted cellular data, and fatal IllegalStateException crashes when mutating UI state after onSaveInstanceState.

## Interview answer — structured

Collecting flows without lifecycle awareness is one of the most destructive architectural bugs in Android development.

An Android component's visual lifecycle is transient. Launching a raw collection loop that outlives screen visibility breaks the unidirectional data flow contract, maintaining active references to destroyed views and preventing garbage collection.

In production, the impact on device hardware is severe. If the collected flow wraps sensor listeners, location updates, or real-time WebSockets, background execution forces mobile CPUs and radio chipsets to remain powered, depleting user battery within hours and generating negative app store reviews.

Background UI mutations trigger runtime crashes. If a backgrounded collector receives an emission and attempts to display a DialogFragment or navigate via Jetpack Navigation after onSaveInstanceState has already executed, the Android framework throws a fatal IllegalStateException, terminating the application process.


## Interview answer — deep senior

At the Android framework and operating system boundary level, collecting flows indefinitely violates OS memory and resource management principles.
When an Activity moves to the background, the framework invokes onStop and onSaveInstanceState. If a coroutine launched in lifecycleScope (without repeatOnLifecycle) continues collecting, its collector block holds direct or implicit references to the Fragment or Activity instance through closures. Because the coroutine Job remains active in the CoroutineContext, the garbage collector cannot reclaim the Activity, causing a significant retain cycle and OutOfMemoryError crashes under memory pressure.
Furthermore, if the stream is exposed via stateIn(viewModelScope, WhileSubscribed(5000)), the uncancelled background collector keeps subscriptionCount above zero perpetually. Consequently, WhileSubscribed never transitions to zero, preventing the upstream flow from tearing down its network connections or Room query observers. Active physical hardware sensors like GPS chips and BLE modems stay powered, rapidly exhausting battery reserves and violating Google Play Vitals battery guidelines.
Even worse are UI framework crashes: attempting to invoke FragmentManager.commit() or show dialogs from an asynchronous collector when the Fragment is in the STOPPED state triggers: "java.lang.IllegalStateException: Can not perform this action after onSaveInstanceState".
Staff engineers eliminate this via automated static analysis and strict guidelines: every UI collection in Views must be wrapped in viewLifecycleOwner.repeatOnLifecycle(STARTED), and every Compose collection must utilize collectAsStateWithLifecycle.

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

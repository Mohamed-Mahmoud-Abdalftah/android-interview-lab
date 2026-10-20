---
id: "AND-07"
question: "What is process death? How is it different from configuration change?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "A"
phase: 1
priority: "P1"
order: 37
editorial_status: "reviewed"
---

# AND-07

## Original interview question

What is process death? How is it different from configuration change?

## What the interviewer evaluates

- Recognize that process death removes all in-memory objects, including ViewModels and singletons.
- Explain how Android can later recreate a previously stopped screen without having called its old `onDestroy()`.
- Recover UI state and external operations from durable identity instead of replaying side effects blindly.

## Concept and technical explanation

System-initiated process death removes the app process and all in-memory objects, including ViewModels, singletons and jobs. It can happen while an app is stopped; the old Activity may receive no final `onDestroy()` callback, so that callback is not a durability hook. If the task is later restored, Android can provide previously saved small UI state, but the availability and freshness depend on the save path and how the user returns. Persistent local data and server state remain separate recovery sources. A configuration change normally recreates UI inside the same living process, retaining a correctly scoped ViewModel. Do not replay an uncertain external operation after process death: persist an attempt ID and reconcile status with the server.

## Practical walkthrough (English)

To exercise one process-death path, navigate to a screen, press Home, then run `adb shell am kill com.example.myapp`; return through Recents. Verify the process actually exited and a new PID appears. This is more representative than “Don't keep activities,” which destroys activities but does not itself prove process death. A Logcat Stop/force-stop action can change task restoration semantics, so do not treat it as equivalent. If the screen has an `orderId`, save that small route key and reload the order from a repository; handle a missing key instead of crashing. For a payment, persist the attempt ID and idempotency key in durable storage and query backend status before any retry. The sample command is illustrative; device behavior and saved-state delivery still need an Android test.

## Explanation in Arabic

Process death يعني إن Android أنهى عملية التطبيق وهي في الخلفية؛ كل اللي في الـ heap يضيع، بما فيه ViewModel وsingletons وcoroutines. النظام مش ملزم ينادي `onDestroy()` قبل ما يقتل العملية، فلا تخلي حفظ بيانات مهمة مستني callback دي. ده غير configuration change العادي: الشاشة بتتعمل من جديد داخل نفس الـ process، وViewModel صحيحة النطاق بتفضل.

لو النظام رجّع المهمة بعد موت العملية، ممكن يوفر Saved State صغيرة كانت اتحفظت قبل القتل، زي `orderId` أو نص مسودة. بس الاستعادة مش وعد بعد كل طريقة إغلاق، وممكن القيمة تكون ناقصة أو قديمة بحسب توقيت الحفظ. البيانات الدائمة في Room أو DataStore والحقائق اللي على السيرفر مصادر تانية مستقلة؛ `SavedStateHandle` مش دفتر معاملات.

في الدفع، احفظ معرف المحاولة ومفتاح idempotency في مخزن دائم، وبعد فتح التطبيق اسأل السيرفر عن الحالة قبل إعادة أي POST. للاختبار، حط التطبيق في الخلفية ثم استخدم `adb shell am kill <package>` وتأكد إن PID اتغير لما ترجع من Recents. خيار “Don't keep activities” يختبر هدم Activity، مش موت العملية نفسه.

## Practical walkthrough

جرّب استعادة شاشة طلب على جهاز اختبار:
1. افتح الشاشة واحفظ `orderId` صغير في Saved State، مع حفظ بيانات الطلب المهمة في repository.
2. اضغط Home ونفّذ `adb shell am kill com.example.myapp` ثم تأكد إن العملية انتهت.
3. ارجع من Recents وراقب PID جديد، ثم اقرأ الـ ID إن كان متاحاً وأعد تحميل البيانات.
4. لو مفيش ID محفوظ، اعرض مسار fallback مفهوم بدل `checkNotNull` وكراش.
5. لو فيه طلب دفع غير محسوم، استعلم عن حالته بمعرف محاولة دائم قبل إعادة الإرسال.

اختبار `force-stop` أو “Don't keep activities” له سلوك مختلف؛ سجّل بالضبط أي مسار اختبرته.

## Why it matters and how it works

Android may kill a stopped application's process to reclaim resources. No in-process scope or static field is a recovery mechanism; even a process-level singleton will be reconstructed. The system can provide a previously saved Bundle when it later recreates a task, subject to the saved-state lifecycle and exit path. Persisted app data remains on disk, while server-owned transactions must be reconciled with the server. A configuration change, by contrast, normally recreates the UI within the still-running process and retains a correctly scoped ViewModel.

## Worked example

For a receipt screen, write the server's `paymentAttemptId` to a durable local record before leaving the initiation flow. The restored ViewModel reads that ID and calls a read-only status endpoint. Only the backend decides whether the attempt succeeded. Illustrative flow: `Persist attempt ID → submit with idempotency key → process is killed → reopen → read ID → fetch server status → render receipt/pending/failure`. A small `SavedStateHandle` key may restore which receipt page was open, but is not the transaction ledger.

## Trade-offs and decision criteria

Saved state is fast and convenient for small UI reconstruction keys; it is constrained by serialization cost, size, and save timing. Room or another durable store survives process death and supports richer data, but requires schema and I/O design. WorkManager can schedule deferrable recovery work under system constraints, while opening the screen can also trigger a foreground reconciliation. Neither makes an uncertain payment outcome safe to repeat without a server idempotency and status contract.

## Failure modes

Assuming `onDestroy()` will run before process termination loses unsaved data and cleanup actions. Keeping an upload cursor or payment state only in a ViewModel makes it disappear. Reissuing a POST on screen restoration can duplicate a non-idempotent operation. Test with a real background process kill and task return; simple rotation exercises a different path. Also test when no saved Bundle is available and when the server status request times out.

## Production perspective

An offline note editor persists drafts incrementally, saves only the note ID and cursor position as lightweight UI state, and reloads the note after restart. A payment screen persists attempt identity and uses an authenticated status API. Metrics distinguish restoration failures, stale pending attempts, and duplicate-request prevention. Treat logs as potentially sensitive; do not log tokens or payment credentials while diagnosing recreation.

## Interview answer — short

System process death removes the app's entire in-memory state, including ViewModels and singletons; the old Activity is not guaranteed a final `onDestroy()`. A normal configuration change recreates UI within the same process and usually retains a scoped ViewModel. Saved UI state may restore small keys after eligible process recreation, while durable data and server status must be reloaded.

## Interview answer — structured

The memory boundary is the central distinction. During an ordinary configuration change, Android usually creates a new Activity in the existing process and retains a correctly scoped ViewModel. During system-initiated process death, the entire app process and heap disappear: all ViewModels, singletons and running jobs are gone. The old Activity may not receive `onDestroy()`, so I do not save critical data there. If Android later restores the task, previously saved UI state can provide small route keys or draft input, subject to lifecycle timing and the way the task was closed. It is not the only surviving data: Room or DataStore persist on disk, and server-side work continues independently. I use a saved `orderId` to fetch authoritative order state; if the key is absent I show a fallback. For payment, I persist an attempt ID and idempotency key, then query the backend before considering a retry. To test, I background the app, kill the process with `adb shell am kill`, verify a new PID and return through Recents. I do not confuse that with activity-only developer options or force-stop.

## Interview answer — deep senior

Process death is an OS lifetime boundary. A stopped app process may be reclaimed under memory pressure, and the old process cannot be trusted to run final cleanup callbacks. Exact low-memory policy, signals and priority scores vary by Android version and device; the stable architectural fact is that every Java/Kotlin object in that process is gone. This includes the Activity, ViewModels, singleton graphs and in-memory cache. `onDestroy()` and ViewModel `onCleared()` are not durable commit hooks for that path.

In an ordinary configuration recreation, the process normally stays alive and a ViewModel tied to a retained owner can carry in-memory state to a new Activity instance. After process death, Android may recreate a task with saved instance state if that state was previously captured and the user returns through a supported path. Saved State is for small reconstruction inputs, and Android's guidance warns that writes are captured at lifecycle save points, not synchronously persisted as a journal. User dismissal, force-stop and first launch are different cases. Persistent local storage remains after system process death, and a server may have completed a request even though the client never received its response.

That uncertainty matters for uploads and payments. Before starting an operation, I durably record an attempt ID and use a server idempotency key. On restart I load the ID from storage, query a read-only status endpoint and render pending, success or failure. Reissuing a non-idempotent POST just because a new ViewModel has `Loading` state risks duplicate work. For an ordinary details screen, a small saved `orderId` can help locate the record, but I handle missing or stale keys and reload from repository. I verify one real process-kill path by backgrounding the app, using `adb shell am kill <package>`, checking the new PID and returning through Recents; I also test no-saved-state and network-timeout cases. Rotation alone does not exercise this boundary.

## How to answer in the interview

- **Why:** Process memory can vanish while an external operation remains uncertain.
- **How:** Contrast recreation within one process with a new process and optional saved state.
- **Trade-offs:** Save small route keys in state; persist critical attempt identity durably.
- **Failure cases:** Reject reliance on `onDestroy` or an in-memory singleton.
- **Production solution:** Reconcile a payment attempt with the server before any retry.

## Deep-dive talking points

Explain process importance, Bundle save timing, why `onDestroy()` is not a durability hook, ViewModel retention only across ordinary configuration recreation, and safe handling of unknown network outcomes after a restart.

## Follow-up questions

- **Interviewer:** "Why does a ViewModel survive rotation but not process death?"
  **Answer:** "An ordinary rotation keeps the process and retained owner store; process death removes the heap containing the ViewModel."
- **Interviewer:** "Does `rememberSaveable` always survive a kill?"
  **Answer:** "It can restore small values after eligible system-initiated recreation if saved state was captured. It is not a guarantee after every exit path or a durable store."
- **Interviewer:** "Is ‘Don't keep activities’ a process-death test?"
  **Answer:** "No. It destroys Activities aggressively but does not by itself prove the process was killed. I verify a new PID after a background kill."

## Self-check rubric

State exactly what process death destroys; contrast it with a configuration change; choose restoration stores for a draft, screen ID, and payment attempt; explain why `onDestroy()` is insufficient; and describe a real process-kill test.

## References and reviewed-on date

- [Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle) — process reclamation and UI recreation.
- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — saved-state timing and durable alternatives.
- [ViewModel overview](https://developer.android.com/topic/libraries/architecture/viewmodel) — in-memory owner lifetime.

Technically reviewed against primary documentation on 2026-10-19.

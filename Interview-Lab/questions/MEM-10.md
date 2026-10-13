---
id: "MEM-10"
question: "What is an ANR, and what are common causes?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "A"
phase: 1
priority: "P1"
order: 65
editorial_status: "reviewed"
---

# MEM-10

## Original interview question

What is an ANR, and what are common causes?

## What the interviewer evaluates

- Define ANR as a responsiveness failure with component-specific timeouts, not simply a crash.
- Identify Main-thread blockage, lock/Binder waits, broadcast/service work, and system contention.
- Diagnose with ANR traces and timing evidence before choosing a fix.

## Explanation in Arabic

الـANR اختصار Application Not Responding: النظام كان مستني التطبيق يرد على input أو ينهي نوع معيّن من component work في الوقت المطلوب، والتطبيق ما استجابش. أشهر سبب إن Main thread مشغول بـnetwork أو disk أو CPU أو مستني lock أو Binder call بطيء. ممكن كمان receiver أو service callback يوقف Main؛ `Service` نفسه مش worker thread. مش كل ANR سببه app code مباشر، فبص على traces وحالة threads و`system_server` عند الحاجة. نقل سطر عشوائي لخلفية من غير معرفة مين ماسك lock ممكن ما يحلش المشكلة.

## Practical walkthrough

في checkout، المستخدم ضغط Pay والواجهة وقفت. شوف ANR type وMain stack: هل واقفة في network، ولا مستنية lock ماسكه worker، ولا Binder call بطيء؟ سجل زمن التوقف قبل تعديل الكود. نقل button handler لـcoroutine مش كفاية لو repository فيها synchronized block طويل. حل السبب: transaction قصيرة، I/O بره lock، وشغل blocking خارج Main، وبعدها تابع ANR rate لنفس cohort.

## Why it matters and how it works

Android dispatches UI input and lifecycle/component callbacks through constrained threads and deadlines. When an event cannot be handled in time, it records an ANR and may show a dialog. Input-dispatch timeouts often point to Main being blocked, but thread dumps captured late can show an idle frame rather than the earlier cause. Slow Binder replies, lock contention, expensive startup, synchronous I/O, and long calculations can all delay responsiveness. Perfetto scheduling and ANR clusters help separate runnable-but-starved Main from a thread waiting on another dependency.

## Worked example

Suppose an order screen sometimes freezes after tapping “Pay”. The ANR cluster shows Main waiting for a synchronized token refresh while a worker thread holds the lock during a network request. Moving only the button handler to a coroutine still leaves Main waiting if UI state reads the same lock. Shorten the critical section, avoid network under the lock, make the repository API main-safe, and measure traces before and after. A timeout in payment submission remains an unknown business outcome even after the UI becomes responsive.

## Trade-offs and decision criteria

Moving blocking work off Main is necessary, but unbounded offloading can exhaust worker threads or overload a service. Reducing lock scope may be better than adding threads. Asynchronous APIs can improve resource use but require cancellation and error handling. StrictMode in development catches some accidental Main-thread operations; production ANR/vitals data reveals real-device timing and OEM effects. Set a measurable responsiveness budget rather than relying only on a single reproduction.

## Failure modes

Calling `Thread.sleep` inside `viewModelScope.launch` still blocks Main. A receiver doing network work inside `onReceive` can exceed its deadline. A delayed trace with `nativePollOnce` may not identify the original blocker; correlate with earlier slices and other threads. Catching every exception and retrying repeatedly in a callback can prolong a freeze. Fix the root cause and verify rate changes across a rollout, not just one local trace.

## Production perspective

Cluster ANRs by trigger, Android version, device, and stack; gather representative traces and app custom trace spans. Identify whether Main is running, waiting on a lock/Binder, or not scheduled. Reproduce with slow network and load, write a targeted regression test where possible, and monitor Play vitals ANR rate after rollout. Keep the fix separate from payment transaction safety so reducing a UI stall does not introduce duplicate charges.

## Interview answer — short

“An ANR is Android reporting that the app missed a responsiveness deadline, often because Main is blocked by I/O, CPU work, a lock, or Binder. I inspect ANR traces and thread timing, fix the actual blocker, and verify the ANR rate improves.”

## Interview answer — structured

“An ANR is not simply an exception crash. The system expected input or component work to respond within a deadline and it did not. I first look at the ANR cluster and main-thread stack, then identify whether Main is doing expensive work, waiting on a lock, or blocked in Binder; I also consider system contention. I use Perfetto when a late stack dump is misleading. The fix might be a main-safe repository, shorter lock scope, or less work in a receiver. I validate with traces and production rate.”

## Interview answer — deep senior

“I start with the ANR type and its deadline rather than guessing from one top frame. For an input ANR I trace Main around the last responsive frame and follow any lock or Binder dependency to the holder thread or system service. A worker doing network under a lock can block Main even when the button handler uses a coroutine. I then change the ownership of blocking work, bound concurrency, remove long critical sections, and add targeted trace spans and tests. I distinguish app-caused stalls from scheduling or system-server delays and compare production ANR clusters by device/API after rollout. If the flow is financial, the responsiveness fix does not change how unknown transaction outcomes are reconciled. For a checkout ANR, I capture the Main wait chain and the worker holding any lock before refactoring. Shortening a critical section may fix the freeze even if the button already launches a coroutine. I keep a trace marker around the transaction and compare the same ANR cohort after rollout.”

## How to answer in the interview

- **Why:** Define responsiveness deadline and trace evidence.
- **How:** Follow Main's wait chain to the lock or service holder.
- **Trade-off:** Moving work off Main may add concurrency pressure.
- **Failure case:** A worker-held lock can still freeze Main.
- **Production solution:** Shorten lock scope and verify ANR cohort after rollout.

## Deep-dive talking points

Explain input and component deadlines, Main-thread state, late stack traces, Binder and lock chains, StrictMode, Perfetto scheduling, and production cluster verification.

## Follow-up questions

- [MEM-22](../mem-22/): Can a coroutine still cause ANR? **Answer:** yes; it can run blocking code on Main or wait on a lock.
- [MEM-25](../mem-25/): What if Main waits on a database lock? **Answer:** inspect the holder and transaction duration; offloading the caller alone may not remove contention.
- [MEM-05](../mem-05/): Is ANR equivalent to OOM? **Answer:** no; one is responsiveness failure, the other allocation failure.

## Self-check rubric

Define ANR precisely; name four causes; follow a lock or Binder wait from Main; explain why a late trace can mislead; and propose a rate-based validation after fixing it.

## References and reviewed-on date

- [Diagnose and fix ANRs](https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs) — types, traces, and contention diagnosis.
- [Android coroutines best practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) — main-safe blocking boundaries.

Technically reviewed against these primary sources on 2026-10-13 by automated editorial review. The payment-lock scenario is illustrative and was not traced on a device.

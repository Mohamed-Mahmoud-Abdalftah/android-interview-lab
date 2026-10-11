---
id: "AND-22"
question: "A crash occurs only after backgrounding the app for several hours. How would you investigate lifecycle and process restoration?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "C"
phase: 1
priority: "P1"
order: 52
editorial_status: "reviewed"
---

# AND-22

## Original interview question

A crash occurs only after backgrounding the app for several hours. How would you investigate lifecycle and process restoration?

## What the interviewer evaluates

- Form a process-death hypothesis without assuming every background crash is caused by process death.
- Reproduce cold restoration and inspect crash evidence, state ownership, and entry intent.
- Fix missing durable state or invalid lifecycle assumptions and verify the original path.

## Explanation in Arabic

أبدأ من crash stack trace ووقت الحدث: هل العملية اتقتلت واتفتحت من جديد؟ ولا Activity كانت موجودة وعملت resume؟ في الخلفية النظام ممكن يستعيد memory فيقتل process، وعند رجوع المستخدم ينشئ Activity وViewModel جديدين. لو الشاشة بتفترض إن singleton أو `lateinit` اتملأ في خطوة onboarding قبل كده هتنهار. أفحص الـsaved state والـIntent والـrepository، وأعيد بناء الشاشة من IDs صغيرة ومصدر بيانات دائم. كمان أراجع token expiry، permission revocation، والـnetwork timeouts، لأن ساعات الانتظار تغيّر هذه الحالات حتى لو process لم يُقتل.

## Why it matters and how it works

Background process lifetime is controlled by Android. Saved instance state can restore lightweight UI context when system-initiated recreation occurs, but it is not a durable database. A ViewModel is constructed afresh after process death. Entry can arrive from Recents, notification, or a deep link, each with different Intent and back-stack context. Production crash clusters, process-start telemetry, and stack traces distinguish an uninitialized in-memory dependency from token expiry or a stale URI grant.

## Worked example

A parcel-tracking screen crashes on return because `CurrentShipment.id` was held only in an application singleton. A notification resumes the route after the process was killed, leaving that field null. Store the shipment ID in route/saved state, load shipment data from repository, and render loading/error states. If the account was signed out or the shipment no longer exists, navigate to a safe destination rather than force-unwrapping. This is a diagnostic case study, not a claim about a specific crash report.

## Trade-offs and decision criteria

Saved state is fast and appropriate for small identifiers and UI choices; durable storage is needed for user work that must survive app closure and device reboot. Re-fetching server data improves freshness but needs offline behavior and loading UX. Persisting entire response objects increases staleness and Bundle pressure. A one-off “Don't keep activities” reproduction probes recreation but is not equivalent to killing the app process; verify both.

## Failure modes

An Activity reads a `lateinit` property initialized only during an earlier flow. A callback arrives after permissions are revoked. A temporary content URI is no longer readable. A token expires during hours in background and a blind retry loops. A network result is applied to a destroyed screen. Guard each boundary, handle domain errors, and preserve cancellation when jobs no longer have an owner.

## Production perspective

Collect stack trace, breadcrumbs for lifecycle and process start, app/OS version, and entry source without logging customer data. Build a reproduction matrix: warm return, Activity recreation, actual process kill and Recents return, notification launch, and expired session. Add a regression test for the identified state path; monitor the crash cluster and restoration success rate after rollout. A payment or order operation must reconcile by stable server ID and idempotency key, never silently submit again.

## Interview answer — short

“I inspect the crash evidence and reproduce both long background return and process death. I check whether state lived only in memory, then restore a small ID and reload durable data while handling expired session and permissions.”

## Interview answer — structured

“I first group crashes by stack, OS version, and entry source, then establish whether the process restarted. A ViewModel and singleton disappear after process death, while saved state can restore small UI keys; important business data belongs in storage or the backend. I reproduce warm return, Activity recreation, process kill, and notification launch separately. In the fix, the destination accepts a stable ID, loads current data, and handles missing data, expired auth, and revoked grants explicitly. I then monitor the production crash cluster and restoration metrics. I would reproduce the entry path after hours in background, not just rotate the screen. A new process can receive a notification or deep link with no initialized singleton; saved state may be absent or stale. I inspect crash clusters by OS, device, app version and entry route, then test expired auth, revoked permission and lost URI access.”
## Interview answer — deep senior

“Hours in the background suggest several failure mechanisms, so I do not jump straight to an OOM or lifecycle bug. I inspect the stack trace and process-start breadcrumbs, ask how the user re-entered, and compare warm resume with true process recreation. I trace every assumption the crashing code makes about a ViewModel, singleton, Intent extra, URI permission, token, or cached response. Android may kill the process; a restored Activity must rebuild from saved small identifiers and durable repository state. I design loading and invalid-session outcomes instead of force-unwrapping. For operations with side effects, especially payment, I persist an operation ID and reconcile with the server rather than retrying blindly. Regression tests reproduce the actual entry and kill conditions, and release telemetry confirms the crash rate falls without creating duplicate work. I start from the stack trace and a timeline: when was the app stopped, was its process killed, and did the user return through Recents, notification or link? Each path has different Intent and back-stack context. I look for `lateinit` fields set only in an earlier screen, stale Context/binding references, expired credentials, URI grants and callbacks that outlive the view. I reproduce with an actual background process kill on the affected API/device, not a mere Activity recreation. The fix reconstructs from durable IDs and validates current permissions and account state. If a payment request was in flight, the client queries server status rather than replaying it.”
## Deep-dive talking points

Discuss stack evidence, process-start markers, saved-state boundaries, notification/deep-link entry, token expiry, URI revocation, and idempotent recovery.

## Follow-up questions

- Does “Don't keep activities” simulate process death exactly? **Answer:** no; it destroys activities aggressively but does not reproduce every process-kill path or loss of all process state.
- What survives process death? **Answer:** durable repository data and eligible saved small UI state; in-memory ViewModels and singletons do not.
- Why might a notification reveal the bug? **Answer:** it can cold-start a destination without the earlier navigation flow that populated in-memory state.

## Self-check rubric

Describe two competing hypotheses, collect evidence, reproduce true process death, fix state ownership, and verify the original entry path.

## References and reviewed-on date

- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — process-death restoration limits.
- [Processes and app lifecycle](https://developer.android.com/guide/components/activities/process-lifecycle) — process importance and termination.
- [Start an Activity from a Notification](https://developer.android.com/develop/ui/views/notifications/navigation) — notification entry and back stack.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The parcel case is illustrative; no device reproduction is claimed.

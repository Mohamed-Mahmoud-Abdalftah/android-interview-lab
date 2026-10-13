---
id: "TST-18"
question: "How do you test process death, rotation, and offline transitions?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 413
editorial_status: "reviewed"
---

# TST-18

## Original interview question

How do you test process death, rotation, and offline transitions?

## What the interviewer evaluates

- Distinguishing rotation, process death and network offline.
- Durable state recovery versus retained ViewModel state.

## Explanation in Arabic

Rotation تغيّر Activity instance غالبًا، لكن مش مساوية لـprocess death. اختبر أثناء Loading إن ViewModel/state وoperation ID لا يتكرروا بعد rotation، والـscreen الجديدة ترجع تعرض state. لاختبار process death فعليًا لازم state المهمة تتخزن قبل الإرسال في Room أو `SavedStateHandle` حسب عمرها؛ اقتل العملية وأعد فتح التطبيق وتأكد إن intent تتقرأ من durable source، مش ذاكرة singleton.

## Practical walkthrough

Offline transition بعد approval أخطر من مجرد “network unavailable”: الرد ممكن يضيع بعد server commit، فالواجهة تظهر Unknown وتعمل status lookup/reconciliation بدل Declined أو charge جديدة. اختبر login/session وpermission restoration حسب workflow. UI test وحدها لا تثبت إن backend منع duplicate؛ محتاج backend contract/integration test.

## Why it matters and how it works

Android may recreate components for configuration change and may later kill the process. Saved instance state is limited and not a substitute for durable financial records. Network loss can happen before or after a remote side effect; the client needs status lookup.

## Worked example

For a checkout screen, rotate during Loading and assert same operation ID. Kill/recreate the process after intent persistence and assert state reloads from Room. Cut network after server approval but before response and assert Unknown plus reconciliation, not Declined.

## Trade-offs and decision criteria

SavedStateHandle is convenient for UI navigation state but is not a transaction log. Room adds durability but cannot prove remote outcome. Emulator controls make tests repeatable; real device drills expose OEM behavior.

## Failure modes

A test calls Activity.recreate() and claims payment survives process death; the ViewModel survived, so it missed a lost in-memory operation ID. Use process-kill tooling and reopen app with persisted state.

## Production perspective

CI includes rotation/locale changes and background process recreation. Release drills include offline/online transitions at each payment boundary with backend sandbox and safe identifiers.

## Interview answer — short

“Rotation and process death are different: a ViewModel can survive the former but not the latter. I persist financial intent and test reopen, and I treat network loss after send as an unknown outcome.”

## Interview answer — structured

“I test configuration recreation, actual process termination and connectivity transitions separately. A ViewModel survives ordinary rotation, but process death requires state reconstructed from SavedStateHandle for small UI details and durable storage/backend for important data. For payments, I persist operation ID before send and test offline after remote success; timeout becomes Unknown until status lookup resolves it. UI-only recreation tests cannot establish crash recovery.”

## Interview answer — deep senior

“I separate three failure modes that are often collapsed into one UI test. Rotation recreates an Activity, so I trigger it while a request is pending and assert that the operation ID remains stable and the new screen observes the same state without submitting again. Process death is stronger: memory, ViewModel and ordinary coroutine scope disappear. I persist the intended operation before network send, kill and relaunch the process in an instrumented test, and assert the repository reconstructs pending or unknown state from durable storage. For offline transitions I test both before-send failure and after-server-commit lost response. The latter must not become Declined; the client should show Unknown, retain the original identity and reconcile with the authority. I also verify that a late callback from an old screen generation cannot overwrite newer state. A fake can drive the app’s state machine deterministically, but it does not prove the backend’s idempotency or real Android restoration by itself. I record exactly which layer and device environment supports each claim.”

## How to answer in the interview

- **Why:** rotation, process death and offline loss have different state survivors.
- **How:** rotate, kill/relaunch and drop reply after approval in separate tests.
- **Trade-off:** fast fake state tests versus expensive Android and backend evidence.
- **Failure case:** a recreated screen sends a new charge ID.
- **Production solution:** durable intent, Unknown state and reconciliation.

## Deep-dive talking points

Prompt for lifetime table, actual process kill, same operation ID, offline-after-approval and backend reconciliation.

## Follow-up questions

- [TST-20](../tst-20/): What if response is lost? **Answer:** same ID and authoritative lookup, never a new charge.
- [TST-16](../tst-16/): Which environment tests process death? **Answer:** Android device/emulator with actual process recreation.

## Self-check rubric

Rotate while loading and verify one stable operation ID, recreate after persisted intent and verify recovery, then drop the network after server approval and assert Unknown plus reconciliation. Distinguish rotation from actual process death.

## References and reviewed-on date

- [Android saving UI state](https://developer.android.com/topic/libraries/architecture/saving-states) — state lifetimes.
- [Android offline-first data layer](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable data design.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.

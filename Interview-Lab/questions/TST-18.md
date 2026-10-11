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

Rotation عادة Activity تتعاد وViewModel يفضل في نفس process؛ process death يمسح memory وViewModel، فلازم `SavedStateHandle` للـsmall UI state وRoom/backend للبيانات الدائمة. Offline transition يغير availability وقد يحدث وسط request؛ لازم state unknown لو payment response ضاع. نختبر كل حالة بشكل مستقل، مش نعتبر rotation اختبار process death.

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

“I test configuration recreation, actual process termination and connectivity transitions separately. A ViewModel survives ordinary rotation, but process death requires state reconstructed from SavedStateHandle for small UI details and durable storage/backend for important data. For payments, I persist operation ID before send and test offline after remote success; timeout becomes Unknown until status lookup resolves it. UI-only recreation tests cannot establish crash recovery. The mechanics matter. Android may recreate components for configuration change and may later kill the process. Saved instance state is limited and not a substitute for durable financial records. Network loss can happen before or after a remote side effect; the client needs status lookup. The choice has a trade-off. SavedStateHandle is convenient for UI navigation state but is not a transaction log. Room adds durability but cannot prove remote outcome. Emulator controls make tests repeatable; real device drills expose OEM behavior.”

## Interview answer — deep senior

“I enumerate state by lifetime: composable memory, ViewModel, saved instance state, local database and backend ledger. Each test kills the owning lifetime and checks the next layer restores correctly. Rotation tests verify no duplicate request; process-death tests relaunch from Room and query provider authority; network tests sever the connection at different points to expose ambiguous outcomes. I run release-like device tests because lifecycle and vendor SDK behavior may differ from fakes. A screen appearing correct after Activity recreation is not evidence of durable payment recovery. Consider a concrete case. For a checkout screen, rotate during Loading and assert same operation ID. Kill/recreate the process after intent persistence and assert state reloads from Room. Cut network after server approval but before response and assert Unknown plus reconciliation, not Declined. A failure case illustrates the risk. A test calls Activity.recreate() and claims payment survives process death; the ViewModel survived, so it missed a lost in-memory operation ID. Use process-kill tooling and reopen app with persisted state. In production, the response is concrete. CI includes rotation/locale changes and background process recreation. Release drills include offline/online transitions at each payment boundary with backend sandbox and safe identifiers.”

## Deep-dive talking points

Prompt for lifetime table, actual process kill, same operation ID, offline-after-approval and backend reconciliation.

## Follow-up questions

- [TST-20](../tst-20/): What if response is lost? **Answer:** same ID and authoritative lookup, never a new charge.
- [TST-16](../tst-16/): Which environment tests process death? **Answer:** Android device/emulator with actual process recreation.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [Android saving UI state](https://developer.android.com/topic/libraries/architecture/saving-states) — state lifetimes.
- [Android offline-first data layer](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable data design.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.

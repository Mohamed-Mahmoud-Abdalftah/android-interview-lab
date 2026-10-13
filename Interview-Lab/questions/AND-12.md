---
id: "AND-12"
question: "How do you restore a screen after process death without losing user input?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "B"
phase: 1
priority: "P1"
order: 42
editorial_status: "reviewed"
---

# AND-12

## Original interview question

How do you restore a screen after process death without losing user input?

## What the interviewer evaluates

- Separate volatile UI state from user data that must be saved before the process is killed.
- Recreate the screen from small saved keys and durable data without repeating side effects.
- Name concrete tests for system-initiated process death and missing/corrupt restoration input.

## Explanation in Arabic

بعد process death، الـActivity وViewModel بيتبنوا من الصفر؛ مفيش memory ترجع تعتمد عليها. ابدأ بتقسيم state: قيمة بسيطة زي current tab أو search query تتحفظ في `SavedStateHandle` أو `rememberSaveable`، أما draft مهم للمستخدم يتحفظ تدريجيًا في Room/DataStore حسب شكله. خزن ID للحاجة في saved state بدل ما تحط object كبير. لما الشاشة ترجع، اقرأ الـID، حمّل البيانات من repository، واظهر loading/error واضح. لو في عملية خارجية شغالة، زي upload أو payment، ارجع لحالتها من durable record والـserver قبل أي إعادة إرسال.

## Why it matters and how it works

Android can reclaim a background process without invoking a convenient final save callback. A previously stopped task may later receive saved-instance-state data, but the new process has new repositories and ViewModels. Saved state is for compact reconstruction hints; durable storage preserves meaningful edits and operation IDs across process termination and ordinary relaunch. A restoration path must handle absent saved state, old schema, missing/deleted item, authentication changes, and unavailable network.

## Worked example

For a note editor, persist each user edit to a repository with a short debounce and a final explicit save action; keep the stable `noteId` in `SavedStateHandle`. The recreated ViewModel reads that ID and observes the stored note. A transient toolbar expansion can use `rememberSaveable`. Debounce alone is not a durability guarantee: if edits must never be lost, commit before telling the user they are saved and surface pending/failed saves. This is an architectural example; a production implementation needs a repository transaction, error state, and tests.

## Practical walkthrough

note editor لو حفظت draft بس في ViewModel، user ممكن يرجع بعد process kill يلاقي text ضاع. خلي `noteId` في route/`SavedStateHandle`، واعمل durable write للـdraft حسب product contract؛ لو autosave debounce، اعرض pending/failed save وما تقولش “Saved” قبل commit. بعد restart اقرأ ID، ابدأ loading، حمّل draft من repository، وبعدين رجّع cursor/toolbar state الصغير بـsaveable state لو مناسب. لو المحتوى حساس، راجع access, encryption, retention حسب threat model. في payment screen، status query واجبة بدل تكرار submit.

## Trade-offs and decision criteria

Saving on every keystroke improves durability but can waste I/O; batching or debouncing reduces writes but creates an at-risk window. Use a clear saved/unsaved indicator and an explicit commit boundary for critical data. A Bundle is simple but size-limited and tied to lifecycle timing. Room handles structured drafts and transactions; DataStore fits small settings, not a rich document. Remote autosave needs conflict/version handling when another device edits concurrently.

## Failure modes

Holding the draft only in ViewModel loses edits. Saving an entire image or note history in `onSaveInstanceState` risks oversized state and main-thread work. Replaying a submit effect from `onCreate` can create duplicate orders. Restoration might reference a deleted note; show a recoverable missing-item state rather than crash. A user logout must prevent restoring another account's private draft; scope local records and access checks to the active identity.

## Production perspective

Define a recovery matrix for rotation, background process kill, app update, force-stop/new launch, logout, and storage failure. On launch, construct the ViewModel from a note ID, load the most recent persisted revision, and compare pending local edits with server revision before syncing. Telemetry records restore source, revision, and failure category without note contents. Automated tests inject process recreation and storage failures; a device test verifies actual task return after a background kill.

## Interview answer — short

“I persist meaningful user input as it changes, save only small reconstruction keys in saved state, and rebuild a new ViewModel from a repository after process death. I never rely on the old ViewModel or `onDestroy()` and I do not replay external submissions automatically.”

## Interview answer — structured

I first classify state. A tab or note ID fits SavedStateHandle or rememberSaveable; the draft itself belongs in durable local storage. After process death, Android may recreate the Activity with saved state, but it creates a new ViewModel, so that ViewModel reloads the note by ID and exposes loading/error states. I make writes visible and test lost network, missing records, and a genuine background process kill. For an in-flight payment I query status rather than resubmit.

## Interview answer — deep senior

Recovery starts before the kill: I establish a durable write boundary for user edits and operation identity, then treat saved-instance-state as a compact pointer into that durable model. On recreation I build a fresh dependency graph, validate account and navigation arguments, load by ID, and render explicit loading, conflict, missing, and error states. I do not execute a one-time effect merely because a composable or Activity was recreated. The data layer resolves revisions and sync conflicts, while the UI only reflects committed versus pending edits. I test a matrix of rotation, system process kill, force-stop, logout, and failed persistence because their guarantees differ. A process kill can happen while the app is backgrounded without a last-minute save callback.

The note editor gives a clear durability test: if the UI says “Saved,” the repository write must have completed according to the product’s persistence contract. Debounced autosave can reduce writes, but it creates a pending interval that must be represented honestly. On recreation I restore a note ID, reload the durable draft, then restore small cursor or expansion state if applicable. A large text body should not rely solely on a Bundle. For a payment operation the same principle applies more strongly: restore an attempt identity and query authoritative status, never replay submission merely because the UI was rebuilt.

## How to answer in the interview

- **Why:** Process loss should not erase user input that the app promised to save.
- **How:** Restore a small note ID and UI position, then reload a durable draft.
- **Trade-offs:** Debounced autosave reduces writes but needs honest pending state.
- **Failure cases:** Name Bundle-only storage and false “Saved” confirmation.
- **Production solution:** Commit drafts before confirmation and test real process recreation.

## Deep-dive talking points

Explain saved-state timing and size, durable draft write semantics, idempotent restoration versus one-time side effects, account scoping, revision conflicts, and the difference between a simulated recreation test and a real process kill.

## Follow-up questions

- [AND-07](../and-07/): Why not rely on `onDestroy()`? **Answer:** process termination need not run it, so save critical data earlier.
- [AND-09](../and-09/): Where should a large note draft live? **Answer:** durable storage; saved state should hold its ID and small UI values.
- [AND-21](../and-21/): Should restoration repeat a payment POST? **Answer:** no; read the persisted attempt and reconcile server status first.

## Self-check rubric

Classify a tab, note ID, draft text, and payment attempt by storage lifetime; state a safe write boundary; describe the new-process load path; handle absent saved state; and name one process-death test and one storage-failure test.

## References and reviewed-on date

- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — saved-state timing, size, and durable-storage distinction.
- [ViewModel overview](https://developer.android.com/topic/libraries/architecture/viewmodel) — screen ownership and process-death boundary.

Technically reviewed against these primary sources on 2026-10-13 by editorial review. The note-editor flow is a design example; no Android instrumentation was run for this record.

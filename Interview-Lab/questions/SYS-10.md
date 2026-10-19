---
id: "SYS-10"
question: "How do you model states and transitions with an explicit state machine?"
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "B"
phase: 4
priority: "P1"
order: 339
editorial_status: "reviewed"
---

# SYS-10

## Original interview question

How do you model states and transitions with an explicit state machine?

## What the interviewer evaluates

Name states, events, and legal transitions; keep effects outside a pure reducer; guard stale asynchronous results with request identity or version; separate restorable UI state from durable business state.

## Concept and technical explanation

An explicit state machine names possible states and events instead of combining independent flags. Kotlin sealed interfaces make a `when` over known variants exhaustive, but do not prove every business transition or payload valid at compile time. A reducer checks current state, event, and operation identity at runtime. External work runs outside the reducer and returns a result event. For durable operations, a repository or server remains authoritative; `SavedStateHandle` can retain small UI restoration keys but is not a transaction ledger.

## Practical walkthrough (English)

For upload, `Idle + Start(id)` becomes `Sending(id)`. `Sending(id) + Succeeded(id, receipt)` becomes `Complete`; a completion carrying an older ID is ignored or recorded as stale. A handler performs the upload and emits the result with the same ID. If a newer request starts first, the old callback cannot overwrite it. For payment, recover the authoritative operation state after process recreation rather than trusting a restored screen label.

## Explanation in Arabic

State Machine صريحة معناها تسمي الحالات الممكنة والأحداث اللي تنقل بينها، بدل Boolean flags منفصلة ممكن تركّب Loading وSuccess وError مع بعض. `sealed interface` تساعد الـ compiler يراجع فروع `when` للأنواع المعروفة، لكن مش كل Transition business تتمنع وقت الـ compile؛ reducer لازم يتحقق من الـ current state والـ event والـ IDs وقت التشغيل. في Upload مثلًا `Start` ينقل Idle إلى Sending مع requestId، و`Succeeded` تقبل فقط لو نفس requestId لسه نشطة؛ Response قديمة تتجاهل أو تسجل كـ stale. تنفيذ Network Request أو Navigation يحصل خارج reducer، ونتيجته ترجع Event. لو عملية لها أثر دائم، Repository أو Server هو المصدر المعتمد، و`SavedStateHandle` تحفظ فقط الحد الأدنى اللازم لإعادة بناء UI، مش ضمان لكل حالة بعد Process Death.

## Practical walkthrough

ابدأ برسم جدول: `Idle + Start -> Sending(id)`، و`Sending(id) + Success(id) -> Complete`، و`Success(otherId)` تتعامل معها كـ stale. خَلّي reducer pure لتختبر الجدول. Handler منفصلة تنفذ Upload وترجع `Succeeded` أو `Failed` بنفس ID. لو المستخدم بدأ محاولة أحدث، القديمة ما تكتبش فوقها. في عملية دفع، مجرد UI State لا تثبت النتيجة المالية؛ بعد Process Death ارجع إلى Journal/Server authoritative state وفك حالة UNKNOWN وفق العقد.

## Why it matters and how it works

A transition table makes invariants reviewable and testable. It does not eliminate races by itself: two asynchronous producers still need ordering or a version guard, and durable state changes may need transactional compare-and-set. Distinguish transient UI projection from persistent operation state.

## Worked example

This runnable Kotlin/JVM reducer rejects a late upload completion for an older request.

```kotlin
sealed interface UploadState {
    data object Idle : UploadState
    data class Sending(val requestId: String) : UploadState
    data class Complete(val receipt: String) : UploadState
}
sealed interface UploadEvent {
    data class Start(val requestId: String) : UploadEvent
    data class Succeeded(val requestId: String, val receipt: String) : UploadEvent
}
fun reduce(state: UploadState, event: UploadEvent): UploadState = when (state) {
    UploadState.Idle -> when (event) {
        is UploadEvent.Start -> UploadState.Sending(event.requestId)
        is UploadEvent.Succeeded -> state
    }
    is UploadState.Sending -> when (event) {
        is UploadEvent.Start -> UploadState.Sending(event.requestId)
        is UploadEvent.Succeeded -> if (event.requestId == state.requestId) UploadState.Complete(event.receipt) else state
    }
    is UploadState.Complete -> state
}
fun main() {
    val state = reduce(UploadState.Sending("new"), UploadEvent.Succeeded("old", "r-1"))
    check(state == UploadState.Sending("new"))
}
```

## Trade-offs and decision criteria

Explicit state/event types add code and transition tests, justified for workflows with several rules or overlapping asynchronous results. A simple screen may need a smaller model. Silently ignoring every illegal event can hide a bug; choose rejection or diagnostic logging where appropriate.

## Failure modes

Request A completes after request B starts and overwrites B's state. A restored screen label claims processing though the work did not resume after process death. A one-off effect is replayed on collection and repeats navigation. Use operation IDs, distinguish durable and UI state, and test out-of-order completion and restoration.

## Production perspective

Carry an operation ID or version through workers and network callbacks. When several producers update durable state, apply transitions transactionally or with compare-and-set in the repository and reconcile server truth. Test legal and illegal transitions, duplicates, stale results, and process recreation. A sealed type or actor is not a guarantee of distributed consistency.

## Interview answer — short

I define explicit states and events, then a reducer validates legal transitions against the current state. Kotlin sealed interfaces make `when` exhaustive, but business guards still run at runtime. A late result must carry a request ID or version so it cannot overwrite a newer attempt. Effects stay outside the reducer, and durable operation truth comes from a repository or server rather than `SavedStateHandle` alone.

## Interview answer — structured

If an upload screen has independent loading, error, and done flags, it can display contradictory combinations. I model `Idle`, `Sending(requestId)`, and `Complete(receipt)`, then events such as `Start` and `Succeeded`. A pure reducer decides transitions. The sealed hierarchy helps the compiler check all variants; the rule that success belongs to the active request still needs a runtime ID comparison.

The network request runs in a handler outside the reducer and emits a result event. If request A finishes after B starts, A's result cannot overwrite B. Illegal events should be rejected or diagnosed deliberately rather than always ignored.

For a simple screen, a smaller model may suffice. For a durable operation, restore from a repository or server after process death. `SavedStateHandle` is useful for small UI keys, not proof that an external transaction completed.

## Interview answer — deep senior

A state machine makes a workflow's states, events, and transition preconditions explicit. It replaces scattered loading/error flags with a reviewable table. Kotlin sealed interfaces close the direct variant set and permit exhaustive `when` expressions, but they do not establish that every payload value or business transition is legal. A reducer checks the current state and event at runtime and may return an effect description for work handled outside it.

For upload, `Idle + Start(id)` yields `Sending(id)`. `Sending(id) + Succeeded(id, receipt)` yields `Complete`. A success with another ID is stale. Network callbacks carry the operation ID because completion order can differ from start order. Serial event handling or version/CAS guards can help with local concurrency; a worker or server updating persistent state needs a transactional guard in the repository as well.

Network and navigation effects run outside the pure reducer and feed result events back with identities. One-off UI actions need a delivery contract to avoid loss or replay on recollection. `SavedStateHandle` is suitable for small inputs used to reconstruct UI after process death, but not as an authoritative ledger. In checkout or payments, query durable repository or server state before claiming completion or retrying.

Test legal and illegal transitions, duplicate completions, stale results after a new attempt, and UI reconstruction. More state types are justified only when they clarify actual rules. The test is whether the invariants are visible and verifiable, not the number of sealed classes.

## How to answer in the interview

- **Model:** state/event table and legal transitions.
- **Guard:** correlate asynchronous results with request IDs or versions.
- **Separate:** pure reducer from effects and UI restoration from durable state.
- **Test:** duplicates, stale results, illegal transitions, and process recreation.

## Deep-dive talking points

Sealed hierarchy versus runtime guards; pure transition function; operation identity and versioning; effect delivery; `SavedStateHandle` limitations; durable repository authority.

## Follow-up questions

- **Interviewer:** "Do sealed classes make every illegal transition impossible at compile time?"
  **Answer:** "No. They close state variants and help exhaustive `when`, but a success event for an old request is still well typed. The reducer compares identity at runtime."

- **Interviewer:** "Can `SavedStateHandle` restore a payment flow completely?"
  **Answer:** "It can restore small UI keys. Durable financial outcome must be reconciled with the repository or provider/server."

## Self-check rubric

Name states and events, show an illegal transition and stale-result guard, and separate UI restoration from authoritative operation state.

## References and reviewed-on date

- [Kotlin sealed classes](https://kotlinlang.org/docs/sealed-classes.html) — exhaustive `when` and hierarchy limits.
- [Saved State for ViewModel](https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate) — UI restoration.
- [Android UI state holders](https://developer.android.com/topic/architecture/ui-layer/stateholders) — state ownership.

Technically reviewed against primary documentation on 2026-10-19.

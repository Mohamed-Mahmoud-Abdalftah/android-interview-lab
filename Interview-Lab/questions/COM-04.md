---
id: "COM-04"
question: "What are state, snapshot state, and state hoisting?"
topic: "Jetpack Compose"
code: "COM"
group: "A"
phase: 3
priority: "P1"
order: 233
editorial_status: "reviewed"
---

# COM-04

## Original interview question

What are state, snapshot state, and state hoisting?

## What the interviewer evaluates

- Distinguish a UI value from Compose's observable state mechanism.
- Explain snapshot reads/writes and single-source ownership.
- Place state at the lowest common owner with events flowing upward.

## Explanation in Arabic

State هي القيمة التي تصف ما يظهر الآن؛ Compose snapshot state مثل `mutableStateOf` تجعل القراءة والكتابة مرصودتين عند الـruntime. عند تغير القيمة، scopes التي قرأتها قد تتحدث. State hoisting يعني نقل ملكية state للـcaller بدل أن يحتفظ child بنسخة مخفية: child يأخذ `value` و`onValueChange`. انقلها إلى أقل owner مشترك بين من يقرأ ويعدل؛ لا ترفع كل checkbox إلى ViewModel بلا سبب. إذا business logic أو مشاركة عدة أجزاء تحتاجها، ViewModel قد يكون المالك المناسب.

## Why it matters and how it works

Compose snapshots provide a consistency model for reads and writes of observable state. Reading a state value in composition establishes a relationship used for invalidation. Hoisted state turns a UI element into a controlled component, allowing one source of truth and easier testing. The owner applies updates; the child emits an event without mutating a hidden duplicate.

## Worked example

`SearchField(query, onQueryChange)` receives text and emits edits. A route owner holds `query` because both the field and result list need it. By contrast, a purely decorative expanded-tooltip flag can stay local inside one composable. If a filter affects data loading and restoration, a ViewModel owns the filter and exposes UI state.

## Trade-offs and decision criteria

Hoisting improves reuse and coordination but can create verbose parameter threading if taken too far. Local state is simpler for isolated UI behavior. ViewModel state suits business rules and screen-wide sharing, but an Activity-wide global owner for every small UI choice increases coupling. Snapshot state solves observability; it does not replace persistence.

## Failure modes

A child has its own text while the ViewModel also has text, producing divergent sources. A plain mutable field changes without an observable state holder. A parent handles `onValueChange` but fails to emit the new value, so typing appears broken. State is hoisted to a process Singleton and leaks one screen's user input into another.

## Production perspective

Document owner, update event, and restoration need for each significant state. Test that user events update the single owner and that the UI follows after rotation/process recreation according to the product requirement.

## Interview answer — short

“State describes current UI; snapshot state is Compose-observable data. Hoisting moves ownership to a caller and gives children a value plus event callback.”

## Interview answer — structured

“I separate the value from where it lives. A `mutableStateOf` value participates in Compose snapshots, so reads can be tracked and changed readers invalidated. Hoisting means a child does not secretly own a second copy: it receives `query` and sends `onQueryChange`, while the lowest common owner updates the value. A local toggle may stay in the composable; a filter shared with results or business logic belongs higher, often in a ViewModel. I choose storage and restoration separately.”

## Interview answer — deep senior

“State is the model of what the user currently sees, while Compose snapshot state is one mechanism for making changes observable to composition. A read during composition registers a dependency; changing the snapshot value can invalidate the scope that read it. State hoisting is an ownership decision. If a search field and a result list need the same query, I hold it in their lowest common ancestor, send the value down, and let the field report edits through a callback. That gives a single source of truth and makes the field reusable and testable. I do not hoist every ephemeral detail to the ViewModel: a tooltip's temporary expansion may belong to one composable. If state drives business logic, must be shared across a screen, or needs saved-state coordination, the ViewModel can own it and expose a screen model. I also decide how it survives recreation; snapshot observability alone does not persist across process death. The common failure is duplicate ownership: a child caches its own text while a route holds another value, so validation and display drift. I test event flow and restoration at the relevant owner boundary.”

## Deep-dive talking points

Explain snapshot observability, read invalidation, controlled components, lowest common ancestor, and restoration.

## Follow-up questions

- Must every state live in a ViewModel? **Answer:** no; keep isolated UI-only state near its consumer.
- What does `onValueChange` do in a hoisted component? **Answer:** it reports intent; the owner updates and supplies the new value.
- Does snapshot state persist after process death? **Answer:** no; separate saveable or durable storage is needed.

## Self-check rubric

Choose an owner for two consumers, trace an edit event, distinguish observability from persistence, and identify duplicate state.

## References and reviewed-on date

- [State and Jetpack Compose](https://developer.android.com/develop/ui/compose/state) — observable state and hoisting.
- [Where to hoist state](https://developer.android.com/develop/ui/compose/state-hoisting) — ownership guidance.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The search example is illustrative.
What are state, snapshot state, and state hoisting?

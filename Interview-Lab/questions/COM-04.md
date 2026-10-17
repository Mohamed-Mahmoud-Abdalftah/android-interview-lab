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

## Concept and technical explanation

State in Jetpack Compose represents any data value that can change over time and drive UI visual presentation. Snapshot State, implemented via MutableState<T> and mutableStateOf(), is Compose's observable reactive state primitive integrated into the multiversion concurrency control (MVCC) Snapshot system. When a composable reads a snapshot state during composition, Compose automatically registers a subscriber dependency on that state. State Hoisting is the foundational architectural pattern of moving state upward to a composable's caller to transform a tightly coupled stateful widget into an idempotent, highly reusable, and easily testable stateless component driven by values and events.

## Practical walkthrough (English)

Refactoring a stateful composable into a clean, hoisted stateless composable:
```kotlin
// ❌ ANTI-PATTERN: Stateful component owns its state, making it hard to test, preview, or reuse
@Composable
fun StatefulSearchInput() {
    var query by remember { mutableStateOf("") } // Tightly coupled internal state
    TextField(
        value = query,
        onValueChange = { query = it },
        placeholder = { Text("Search products...") }
    )
}

// ✅ ARCHITECTURAL BEST PRACTICE: State Hoisting (Stateless & decoupled)
// Separates state value (flows down) from event callbacks (flow up)
@Composable
fun StatelessSearchInput(
    query: String, // Value flows DOWN from parent
    onQueryChanged: (String) -> Unit, // Events flow UP to parent
    modifier: Modifier = Modifier
) {
    TextField(
        value = query,
        onValueChange = onQueryChanged,
        placeholder = { Text("Search products...") },
        modifier = modifier
    )
}

// Parent caller manages and hoists state cleanly (e.g. into ViewModel or Screen state holder)
@Composable
fun SearchScreen(viewModel: SearchViewModel) {
    val query by viewModel.searchQuery.collectAsStateWithLifecycle()
    StatelessSearchInput(query = query, onQueryChanged = viewModel::onQueryChanged)
}
```

## Explanation in Arabic

مفاهيم الـ State والـ Snapshot State ورفع الحالة (State Hoisting) في Jetpack Compose:

1. ما هو الـ State في Compose؟
   - الـ State هو أي قيمة متغيرة تؤثر على ما يراه المستخدم على الشاشة (مثل نص في حقل إدخال، حالة لودينج، قائمة رسائل).
   - في Compose، لا نستخدم متغيرات عادية `var count = 0`، لأن محرك Compose لا يمكنه تتبع قراءتها أو تعديلها.
   - نستخدم **`SnapshotState`** عبر `mutableStateOf(value)`؛ وهو غلاف تفاعلي يُشعر نظام Compose بلحظات القراءة والكتابة.

2. كيف يعمل الـ Snapshot State داخلياً؟
   - مستوحى من نظام قواعد البيانات متعددة النسخ (MVCC - Multi-Version Concurrency Control).
   - عندما يُقرأ الـ State، يُسجل الـ Snapshot System أن الـ Composable الفلاني يراقب هذه القيمة.
   - عند تعديل القيمة، يُنشئ الـ Snapshot نسخة جديدة ويطلق إشعار Invalidation للنطاقات المراقبة فقط.

3. ما هو رفع الحالة (State Hoisting)؟
   - هو نمط معماري لنقل الـ State للأعلى إلى الدالة المستدعية (Caller) لجعل الـ Composable **عديم الحالة (Stateless)**.
   - النمط القياسي: استبدال المتغير الداخلي ببارامترين:
     * `value: T` (القيمة الحالية للعرض).
     * `onValueChange: (T) -> Unit` (حدث يُطلق عندما يطلب المستخدم التغيير).
   - الفوائد: سهولة إعادة استخدام المكون، قابلية الاختبار بنسبة 100% دون حاجة لمحاكاة Compose Runtime، و Single Source of Truth.

## Practical walkthrough

تطبيق نمط State Hoisting لتحويل مكون Stateful إلى Stateless قابل لإعادة الاستخدام والاختبار:
```kotlin
// ❌ مكون يحتفظ بحالته داخلياً (Stateful): يصعب اختباره وإعادة استخدامه في شاشات أخرى:
@Composable
fun StatefulSearchField() {
    var query by remember { mutableStateOf("") }
    TextField(value = query, onValueChange = { query = it })
}

// ✅ تطبيق State Hoisting: فصل القيمة عن الأحداث (Stateless Composable):
@Composable
fun StatelessSearchField(
    query: String,
    onQueryChanged: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    TextField(
        value = query,
        onValueChange = onQueryChanged,
        placeholder = { Text("Search products...") },
        modifier = modifier
    )
}
```

## Why it matters and how it works

Compose snapshots provide a consistency model for reads and writes of observable state. Reading a state value in composition establishes a relationship used for invalidation. Hoisted state turns a UI element into a controlled component, allowing one source of truth and easier testing. The owner applies updates; the child emits an event without mutating a hidden duplicate.

## Worked example

`SearchField(query, onQueryChange)` receives text and emits edits. A route owner holds `query` because both the field and result list need it. By contrast, a purely decorative expanded-tooltip flag can stay local inside one composable. If a filter affects data loading and restoration, a ViewModel owns the filter and exposes UI state.

### Compose/Kotlin walkthrough

```kotlin
// Caller: var query by rememberSaveable { mutableStateOf("") }
@Composable
fun SearchField(value: String, onValueChange: (String) -> Unit) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text("Search products") }
    )
}
// Both SearchField(query, ...) and Results(query) read the same owner value.
```

## Trade-offs and decision criteria

Hoisting improves reuse and coordination but can create verbose parameter threading if taken too far. Local state is simpler for isolated UI behavior. ViewModel state suits business rules and screen-wide sharing, but an Activity-wide global owner for every small UI choice increases coupling. Snapshot state solves observability; it does not replace persistence.

## Failure modes

A child has its own text while the ViewModel also has text, producing divergent sources. A plain mutable field changes without an observable state holder. A parent handles `onValueChange` but fails to emit the new value, so typing appears broken. State is hoisted to a process Singleton and leaks one screen's user input into another.

## Production perspective

Document owner, update event, and restoration need for each significant state. Test that user events update the single owner and that the UI follows after rotation/process recreation according to the product requirement.

## Interview answer — short

State is any value that drives the UI over time. Snapshot state, created via mutableStateOf(), is Compose's reactive state system that automatically tracks reads and schedules recomposition whenever written to. State Hoisting is the pattern of lifting state up to the caller, replacing internal state variables with a parameter for the current value and an event lambda for updates. Hoisting makes components stateless, highly reusable, previewable, and trivially testable in isolation.

## Interview answer — structured

State management and state hoisting are the foundational pillars of building robust Jetpack Compose architectures.
In declarative UI, the screen cannot be mutated directly; instead, the UI reacts to state mutations.
Snapshot state is Compose's custom reactive observation mechanism.
When you create state using mutableStateOf(), Compose wraps the value inside a State object integrated into the Snapshot system.
Whenever a composable reads that value during its execution, Compose transparently records that function scope as a subscriber.
When the state is subsequently written to on any thread, the Snapshot system notifies the runtime, scheduling recomposition specifically for the subscribing functions.
State Hoisting is the architectural design pattern used to decouple presentation from state ownership.
Instead of allowing a UI component like a text field or toggle button to maintain its own internal state, developers hoist the state up to the caller.
A hoisted component exposes two parameters: a value parameter representing the current state (flowing downward), and a callback lambda representing user-initiated events (flowing upward).
This pattern transforms components into stateless widgets that can be previewed seamlessly, reused in different screens, and tested purely using JVM unit tests without mock view hierarchies.

## Interview answer — deep senior

Under the hood, Compose's Snapshot system is inspired by Multiversion Concurrency Control (MVCC), identical to transaction isolation models used in high-performance SQL databases.
When Compose begins a frame, it captures a global Snapshot. Every thread or coroutine reads an isolated, consistent snapshot of state variables without requiring synchronized mutex locks.
During the composition phase, Compose registers a ThreadLocal read observer. Every time StateObject.value is accessed, the observer records the StateRecord reference into the SlotTable for that specific RecomposeScope.
When a write operation occurs via StateObject.value = newValue, Compose records the mutation into the current snapshot and dispatches a global write notification to the SnapshotManager.
The SnapshotManager identifies all invalidated RecomposeScopes and marks their layout nodes dirty.
State Hoisting directly influences memory locality and recomposition scope granularity within this MVCC architecture.
If state is hoisted too high into a root screen composable, modifying a minor text counter can invalidate the entire screen hierarchy unless wrapped in isolated sub-composables.
Conversely, if state is not hoisted at all, state is lost during configuration changes and cannot be synchronized with domain repositories.
Staff engineers apply the Single Source of Truth rule: hoist transient UI state (like scroll offsets) to local state holders, and hoist business state (like shopping cart contents) into architecture ViewModels exposed as StateFlow.

## How to answer in the interview

- **Why:** one source of truth keeps field and results in sync.
- **How:** hoist to the lowest common owner and send edits upward.
- **Trade-off:** local decoration state need not move to a ViewModel.
- **Failure case:** a hidden child copy diverges from its parent.
- **Production solution:** use observable state and test edits from both consumers.

## Deep-dive talking points

Explain snapshot observability, read invalidation, controlled components, lowest common ancestor, and restoration.

## Follow-up questions

- **Interviewer:** "What happens if you update a normal Kotlin `var` inside a Composable without `mutableStateOf`?"
  **Answer:** "The variable value changes in memory, but Compose runtime has no observation mechanism on standard JVM properties. No recomposition is scheduled, and the screen remains frozen showing the old value."

- **Interviewer:** "What is the difference between a Stateful and Stateless composable in design systems?"
  **Answer:** "A Stateless composable exposes pure inputs and outputs via parameters and callbacks, ideal for reusable UI design systems. A Stateful composable acts as an orchestration container that owns or manages state for a specific feature screen."

## Self-check rubric

Choose an owner for two consumers, trace an edit event, distinguish observability from persistence, and identify duplicate state.

## References and reviewed-on date

- [State and Jetpack Compose](https://developer.android.com/develop/ui/compose/state) — observable state and hoisting.
- [Where to hoist state](https://developer.android.com/develop/ui/compose/state-hoisting) — ownership guidance.

Technically reviewed against primary documentation on 2026-10-13.

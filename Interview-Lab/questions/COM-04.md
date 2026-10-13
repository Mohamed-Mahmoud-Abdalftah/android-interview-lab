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

State in Compose is any dynamic data driving the UI. Snapshot state (`mutableStateOf`) enables Compose's runtime to track reads and writes for precise recomposition. State Hoisting is the architectural pattern of moving state up to make child composables stateless, parameterized by `value: T` and `onValueChange: (T) -> Unit`.

## Interview answer — structured

In Jetpack Compose, state is the single source of truth that dictates visual rendering.

To make state observable to the Compose runtime, we wrap it in a **Snapshot State**—typically created via `mutableStateOf(initialValue)`. Compose's snapshot system tracks reads during the execution of composables. Whenever a write occurs on that state, the runtime schedules recomposition exclusively for the scopes that read that specific value, achieving highly granular updates.

**State Hoisting** is the foundational architectural pattern for building modular, robust Compose UI. Instead of letting a component manage its own internal state (making it *stateful* and tightly coupled), we hoist the state up to its caller by replacing it with two parameters:
1. The current state representation: `value: T`
2. An event lambda: `onValueChange: (T) -> Unit`

This transforms the composable into a **stateless component**, making it trivial to preview in Android Studio, share across different navigation screens, and verify in isolated unit and screenshot tests.

## Interview answer — deep senior

Under the hood, `mutableStateOf` relies on Android's global `Snapshot` system (`androidx.compose.runtime.snapshots`). The snapshot system functions like software transactional memory (STM) or Git: each thread or composition operates in an isolated snapshot of state. When a state mutation is performed, the modified records are committed to the global snapshot, which broadcasts invalidation notifications to all active `SnapshotStateObserver` instances.

When architecting production applications, state hoisting operates across three distinct levels:
1. **Component-level hoisting**: Hoisting basic input values (text fields, checkboxes) into immediate parents.
2. **Screen-level UI State Holder**: Hoisting complex widget coordination (like custom scroll interactions and animation sync) into an unmanaged plain Kotlin class (e.g. `rememberSearchState()`).
3. **Business-level hoisting**: Hoisting domain and repository operations into an architecture-level `ViewModel` exposing `StateFlow<UiState>`.

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

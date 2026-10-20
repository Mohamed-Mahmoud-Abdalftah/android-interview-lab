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

UI state is data needed to describe the current screen. `mutableStateOf` creates Compose snapshot state, whose reads and writes the runtime can observe. A changed value can invalidate the composition scope that read it; reads in layout and draw have their own invalidation paths. State hoisting moves ownership to the lowest suitable common owner and passes the current value down with a callback for proposed changes. A component may remain stateful when no other consumer needs that state. Hoisting helps share and test behavior, but neither snapshot state nor hoisting provides durable persistence by itself.

## Practical walkthrough (English)

Refactoring a stateful composable into a clean, hoisted stateless composable:
```kotlin
// Local state is appropriate when no caller needs to coordinate this query.
@Composable
fun StatefulSearchInput() {
    var query by remember { mutableStateOf("") }
    TextField(
        value = query,
        onValueChange = { query = it },
        placeholder = { Text("Search products...") }
    )
}

// Hoist when the caller or another child needs the same query.
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

الـ State هي البيانات اللي الواجهة بتعرضها حالياً. لو القيمة بتتغير، لازم التغيير يوصل لـ Compose بطريقة observable، زي `mutableStateOf` أو `StateFlow` بعد جمعه كـ Compose State. متغير Kotlin عادي ممكن يتغير في الذاكرة، لكن Compose مش هتعرف منه وحده إن الواجهة لازم تتحدث.

الـ Snapshot system بيتابع قراءات حالة Compose. لو نطاق قرأ قيمة أثناء الـ Composition واتغيرت فعلاً حسب mutation policy، النطاق ده ممكن يتعمله invalidation. القراءة في Layout أو Draw ممكن تعيد المرحلة دي بدل إعادة Composition. مش كل كتابة تعني Recomposition، ومش كل Recomposition تعني Draw. تفاصيل إدارة الـ snapshots الداخلية قابلة للتغير، فاشرح السلوك المرصود بدل الادعاء إن كل تعديل بيخلق نسخة كاملة أو بيعمل قفل على كل thread.

State hoisting يعني تنقل ملكية الحالة للـ caller اللي محتاج ينسق بين المستهلكين. المكون بياخد `value` و`onValueChange`؛ القيمة تنزل والحدث يطلع. مثلاً نص البحث لو الـ field والنتائج محتاجينه، خليه عند أقرب مالك مشترك. أما tooltip محدش غيره محتاج حالته، ممكن تسيبه محلي. الـ ViewModel مناسب لو الحالة مرتبطة بمنطق الشاشة أو repository، لكنه مش شرط لكل toggle. الـ Snapshot State تعالج الملاحظة؛ الحفظ بعد إعادة إنشاء الشاشة مسألة تانية.

## Practical walkthrough

مثال فيه مصدر حقيقة واحد للنص ونتائج البحث:
```kotlin
@Composable
fun SearchRoute() {
    var query by rememberSaveable { mutableStateOf("") }
    Column {
        SearchInput(value = query, onValueChange = { query = it })
        Text("Searching for: $query")
    }
}

@Composable
fun SearchInput(value: String, onValueChange: (String) -> Unit) {
    OutlinedTextField(value = value, onValueChange = onValueChange)
}
```

لو البحث بيستدعي repository، خليه في state holder مناسب بدل عمل طلب شبكة من جسم الـ Composable. السطر اللي بيغير `query` شغال داخل event callback، مش أثناء وصف الواجهة.

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

State is data needed to describe UI. Compose snapshot state makes reads and writes observable, so a changed value can invalidate readers in the relevant phase. State hoisting moves ownership to a suitable common caller and exposes a value plus a change event. Hoist when consumers must share or coordinate the value; keep isolated UI state local.

## Interview answer — structured

Start with the user-visible value: for a search screen, the text and results depend on a query. `mutableStateOf` is one observable holder for that query. When composition reads it, Compose can track the read and invalidate the relevant scope after an effective change. A normal Kotlin property does not notify Compose by itself, while an external `StateFlow` needs lifecycle-aware collection into Compose state. Reads in later phases can lead to layout or draw invalidation rather than composition. State hoisting addresses ownership, not observability alone. The search input receives `value` and reports `onValueChange`; the caller applies the change and sends the new value back down. If the results also need the query, use their lowest suitable common owner. If a disclosure flag affects only one component, local remembered state can be simpler. For business rules or repository interaction, a screen state holder such as a ViewModel can own the state. Test that an event updates the owner and returns as UI state; decide separately what must survive recreation.

## Interview answer — deep senior

The Compose snapshot system supplies observable state with a consistency model for reads and writes. A composable reading `State.value` in composition establishes a dependency for invalidation. The behavior also depends on the mutation policy: assigning a value considered equivalent may produce no effective change. The reader's phase matters. If a state value is only read during layout or draw, Compose can perform less work than a composition restart. The implementation uses snapshots and records internally, but claiming a full copy on every write or a fixed thread model would overstate the public contract.

Hoisting is about choosing a source of truth. A stateless input exposes the current value and an event requesting a new one; it does not own a duplicate mutable copy. The state owner validates or transforms the event, then exposes a new value. For two consumers, the owner must be at least their lowest common parent and high enough to handle writes. If a child also keeps its own hidden text, a parent update can conflict with what the user typed. On the other hand, moving every local visual flag to a screen-wide ViewModel increases coupling and makes small interactions harder to understand.

In production, I trace who reads and who writes each value, what happens on screen recreation, and whether data must be reloaded from persistence. I test the UI behavior at the appropriate level: a pure state transition can be a JVM unit test, while actual Compose rendering and callbacks need Compose test infrastructure. Snapshot state does not turn memory into durable storage. Performance changes should be based on a trace and user-visible frame cost, not on an assumption that hoisting always narrows recomposition.

## How to answer in the interview

- **Why:** one source of truth keeps field and results in sync.
- **How:** hoist to the lowest common owner and send edits upward.
- **Trade-off:** local decoration state need not move to a ViewModel.
- **Failure case:** a hidden child copy diverges from its parent.
- **Production solution:** use observable state and test edits from both consumers.

## Deep-dive talking points

Explain snapshot observability, read invalidation, controlled components, lowest common ancestor, and restoration.

## Follow-up questions

- **Interviewer:** "What if I change a plain Kotlin `var`?"
  **Answer:** "The value changes, but Compose does not observe that property by itself. I expose observable state or collect a flow, then verify the UI reads that state."
- **Interviewer:** "Should every local state move into a ViewModel?"
  **Answer:** "No. I place state at the lowest owner that can serve every reader and writer. A local tooltip flag can stay in a composable; screen business logic belongs in an appropriate state holder."

## Self-check rubric

Choose an owner for two consumers, trace an edit event, distinguish observability from persistence, and identify duplicate state.

## References and reviewed-on date

- [State and Jetpack Compose](https://developer.android.com/develop/ui/compose/state) — observable state and hoisting.
- [Where to hoist state](https://developer.android.com/develop/ui/compose/state-hoisting) — ownership guidance.

Technically reviewed against primary documentation on 2026-10-19.

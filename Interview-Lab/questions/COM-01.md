---
id: "COM-01"
question: "What is Compose? Compare declarative Compose and XML Views."
topic: "Jetpack Compose"
code: "COM"
group: "A"
phase: 3
priority: "P1"
order: 230
editorial_status: "reviewed"
---

# COM-01

## Original interview question

What is Compose? Compare declarative Compose and XML Views.

## What the interviewer evaluates

- Explain declarative UI as a function of observable state.
- Compare update ownership, interoperability, and lifecycle rather than claiming automatic performance gains.
- Identify when migration can be incremental.

## Explanation in Arabic

Jetpack Compose toolkit لبناء Android UI بـKotlin. في XML Views غالبًا تنشئ hierarchy ثم تغير widgets بأوامر مثل `textView.text = ...`؛ في Compose تصف الـUI المطلوبة بناءً على state، والإطار يعيد تنفيذ الأجزاء اللازمة عندما تتغير state المرصودة. هذا لا يلغي lifecycle ولا business logic ولا يحل performance تلقائيًا. يمكن دمج `ComposeView` داخل View screen أو `AndroidView` لعنصر قديم، وبالتالي النقل تدريجي. المهم يكون مصدر state واضح وتبعد side effects عن جسم composable.

## Practical walkthrough

في شاشة تسجيل دخول حقيقية، خلي `LoginUiState` هي المصدر الوحيد لقيمة الإيميل والتحميل والخطأ. الـ`ViewModel` يستقبل `onEmailChange` و`onSubmit` ويغيّر الـstate؛ الـUI لا تستدعي الشبكة وهي بتترسم. وقت النقل من XML، اختار شاشة كاملة أو component بحدود ownership واضحة، وتأكد إن نفس الحقل مش متخزن مرتين. لو خليت XML وCompose يكتبوا نفس قيمة الإيميل، هتظهر race وحالة قديمة بعد rotation. في production اعمل event contract واحد واختبر شاشة النقل قبل تعميمه.

## Why it matters and how it works

Compose records a composition of UI descriptions. Reads of observable state establish invalidation relationships; a change schedules recomposition of affected scopes. The runtime can skip eligible calls, while layout and draw remain separate work. Views are also capable of state-driven architecture, but imperative widget mutation is the conventional integration surface. Both approaches ultimately render through Android and obey owner lifecycles.

## Worked example

A login form in Views observes a ViewModel and writes each field, progress indicator, and error label explicitly when state changes. A Compose `LoginScreen(state, onEvent)` selects its text, enabled button and error branch from one immutable `LoginUiState`. In either case, the ViewModel handles authentication and the UI sends an intent, not a direct network request from rendering.

### Compose/Kotlin walkthrough

```kotlin
// Assumes Material3 and a state owner supplies immutable state and callbacks.
data class LoginUiState(val email: String = "", val saving: Boolean = false)
@Composable
fun LoginScreen(state: LoginUiState, onEmail: (String) -> Unit, onSubmit: () -> Unit) {
    Column {
        OutlinedTextField(state.email, onValueChange = onEmail, label = { Text("Email") })
        Button(onClick = onSubmit, enabled = !state.saving && state.email.isNotBlank()) {
            Text(if (state.saving) "Signing in…" else "Sign in")
        }
    }
}
```

## Trade-offs and decision criteria

Compose improves local reuse and state-oriented composition, but migration adds interoperability, tooling and team-learning costs. Existing custom Views or SDK widgets may remain appropriate. Performance should be measured in release configuration; neither XML nor Compose is inherently faster for every screen.

## Failure modes

A developer starts a network call in a composable body and repeats it on recomposition. Mutable collections change without observable state, so UI remains stale. A mixed View/Compose screen has two sources of truth for one form. A team assumes Compose eliminates accessibility or lifecycle testing.

## Production perspective

Migrate a vertical screen with explicit state/event contracts, test process recreation and semantics, and profile release builds. Keep stable boundaries around legacy widgets and retire duplicate event handling as each screen moves.

## Interview answer — short

“Compose describes UI from state in Kotlin; XML Views usually update an existing widget tree. Recomposition updates affected descriptions when observed state changes. For a login form, the owner changes state and Compose redraws the result.”

## Interview answer — structured

“I think of Compose as a declarative UI toolkit: the screen function receives state and emits UI, while events go back to its owner. In a View screen, I typically inflate XML and imperatively set widget properties on state updates. Compose can recompose scopes that read changed state and skip eligible work, but I still keep effects lifecycle-aware. I can adopt it incrementally with `ComposeView` or `AndroidView`, and I measure real rendering rather than assuming a performance win. I would demonstrate the shift with a login form: a single immutable UI state feeds the field, button, and error.”

## Interview answer — deep senior

“The important shift is who owns the update procedure. With Views I commonly inflate a hierarchy and write the changes to each widget when a model changes; with Compose I provide a function that describes the UI for current inputs and observable state. Compose tracks reads, invalidates relevant scopes, and may skip calls whose inputs allow it. That model encourages a single state owner and event callbacks, but it does not remove navigation, lifecycle, or side-effect discipline. A network request in the composable body would be a bug because rendering may run repeatedly. I keep data and business decisions in a ViewModel or other owner, expose a coherent state, and use effects only for work tied to composition. For migration I choose a screen boundary and use interoperability APIs around existing Views or SDK widgets, then test semantics, state restoration and performance on a release build. The choice is not an ideological replacement of XML: an established custom View can remain useful, while Compose often makes dynamic, reusable UI easier to express and reason about. I would migrate one screen first and check that the legacy and Compose sides do not each own the same form value.”

## How to answer in the interview

- **Why:** one state owner makes a dynamic form predictable.
- **How:** explain that a callback updates the owner, then observed state drives the next description.
- **Trade-off:** existing custom Views can stay behind interop boundaries.
- **Failure case:** a request in the body repeats.
- **Production solution:** migrate one screen and verify restoration, accessibility, and release-frame timing.

## Deep-dive talking points

Discuss observable state, invalidation, recomposition versus draw, side effects, interoperability, and measured migration.

## Follow-up questions

- Does recomposition rebuild the entire Android View hierarchy? **Answer:** no; Compose updates its own composition and can limit and skip work by scope.
- Can a project mix Compose and Views? **Answer:** yes, using supported interoperability APIs during incremental adoption.
- Where should network work run? **Answer:** in an owner or lifecycle-aware effect, never as an uncontrolled render-body call.

## Self-check rubric

Compare update models, explain a state change, name an interoperability path, and avoid performance absolutes.

## References and reviewed-on date

- [Compose mental model](https://developer.android.com/develop/ui/compose/mental-model) — declarative UI and recomposition.
- [Compose and Views interoperability](https://developer.android.com/develop/ui/compose/migrate/interoperability-apis) — gradual migration.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The login form is illustrative.

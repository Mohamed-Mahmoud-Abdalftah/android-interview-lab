---
id: "PAT-09"
question: "Compare State and Strategy with concrete examples."
topic: "Design Patterns"
code: "PAT"
group: "B"
phase: 2
priority: "P1"
order: 200
editorial_status: "reviewed"
---

# PAT-09

## Original interview question

Compare State and Strategy with concrete examples.

## What the interviewer evaluates

Contrast interchangeable algorithm selection with behavior governed by current state and transitions.

## Explanation in Arabic

المقارنة الدقيقة بين نمط الحالة (State Pattern) ونمط الاستراتيجية (Strategy Pattern) مع أمثلة عملية واقعية في Android:

1. وجه الشبه الخادع (The Identical Structure):
   - النمطان يمتلكان نفس المخطط الهيكلي (UML Structure) تماماً: كلاس سياق (Context Class) يمتلك مرجعاً لـ Interface مجرد، وهذا الـ Interface له عدة تطبيقات ملموسة.

2. الفرق الجوهري في النية والسلوك (Intent & Behavior):
   - **نمط الاستراتيجية (Strategy Pattern)**:
     * **النية**: تبديل **خوارزميات متبادلة (Interchangeable Algorithms)** تؤدي نفس الهدف بأساليب مختلفة.
     * **طريقة الاستخدام**: العميل (Client) يحدد الاستراتيجية غالباً مرة واحدة (مثل اختيار المستخدم: "أريد الدفع بـ PayPal")، والاستراتيجيات لا تعلم شيئاً عن بعضها البعض.
     * **مثال**: استراتيجيات ضغط الصور (JPEG vs WebP vs PNG) أو استراتيجيات الدفع.
   - **نمط الحالة (State Pattern)**:
     * **النية**: جعل الكائن **يغير سلوكه بالكامل عندما تتغير حالته الداخلية** (Finite State Machine).
     * **طريقة الاستخدام**: الحالة تتغير تلقائياً وبشكل ديناميكي ومستمر استجابةً للأحداث، وحالات الـ State غالباً هي التي تقرر وتطلق الانتقال إلى الحالة التالية بنفسها!
     * **مثال**: آلة حالات اتصال البلوتوث (`Disconnected -> Connecting -> Connected -> Disconnecting`).

## Practical walkthrough

مقارنة بين Strategy للدفع و State لاتصال البلوتوث في كود Kotlin:
```kotlin
// 1. STRATEGY PATTERN: خوارزميات متبادلة لا تغير نفسها ولا تعلم عن بعضها:
interface ImageCompressionStrategy {
    fun compress(bitmap: Bitmap): ByteArray
}
class JpegCompression : ImageCompressionStrategy { ... }
class WebPCompression : ImageCompressionStrategy { ... }
// العميل يختار استراتيجية واحدة ويمررها للعملية:
imageSaver.save(bitmap, WebPCompression())

// 2. STATE PATTERN: آلة حالات ديناميكية حيث تغير الحالات سلوك الجهاز وتنتقل ذاتياً:
sealed interface BleConnectionState {
    fun connect(context: BleManager)
    fun disconnect(context: BleManager)
}

class DisconnectedState : BleConnectionState {
    override fun connect(context: BleManager) {
        context.startScan()
        context.transitionTo(ConnectingState()) // الحالة تنقل السياق للحالة التالية!
    }
    override fun disconnect(context: BleManager) { /* لا شيء */ }
}

class ConnectingState : BleConnectionState {
    override fun connect(context: BleManager) { /* تجاهل: الاتصال جارٍ بالفعل */ }
    override fun disconnect(context: BleManager) { context.cancel(); context.transitionTo(DisconnectedState()) }
}
```

## Why it matters and how it works

Strategy encapsulates interchangeable policies; State encapsulates behavior that varies with an object’s lifecycle state. Similar class diagrams can hide distinct ownership and transition requirements.

## Worked example

Conceptual example: `PaymentStrategy.submit()` has card/wallet implementations. `CheckoutState` sealed cases determine whether Submit is legal and how timeout is represented. A reducer updates state; a selected strategy performs the provider request.

## Trade-offs and decision criteria

An explicit `when` can be simpler than either pattern for a few stable cases. A State pattern or reducer helps when transitions multiply. Strategy helps when independently replaceable algorithms exist. Avoid provider selection logic scattered through state classes.

## Failure modes

A timeout is handled by strategy as final failure and state immediately returns to Idle, allowing duplicate charge. Represent uncertainty as pending verification and reconcile with server; keep strategy result semantics consistent.

## Production perspective

A checkout ViewModel uses a reducer for state transitions and a gateway strategy for provider variation, with persisted request ID. Contract tests cover all providers and transition tests cover late confirmation.

## Interview answer — short

Strategy encapsulates interchangeable algorithms usually chosen once by the client (e.g. Payment methods, image compression). State models a dynamic state machine where an object alters its behavior based on internal state changes, with states often triggering transitions to succeeding states (e.g. Media playback or Bluetooth connectivity).

## Interview answer — structured

While State and Strategy share an identical structural UML diagram (a Context class delegating to an Interface with polymorphic implementations), they diverge sharply in architectural intent and lifecycle behavior.

First, **Strategy Pattern (Interchangeable Algorithms)**. Next, with Intent, provide alternative ways of accomplishing the exact same task.
Additionally, a Selection is configured from the outside by the client or dependency injection container (e.g. Selecting `PaypalStrategy` vs `StripeStrategy`, or sorting via `PriceComparator`). With Independence, strategies are completely decoupled from each other and have no awareness of succeeding strategies.
**State Pattern (Dynamic Behavioral Transformation)**. With Intent, enable an object to behave like an entirely different class when its internal state changes (Finite State Machine).
With Transitions, driven internally by events occurring over time. State implementations actively invoke callbacks on the Context to transition it to succeeding states (e.g. `ConnectingState` transitions the context to `ConnectedState` upon receiving a BLE GATT callback). Finally, with Coupling, states often hold references to valid neighboring target states in the state machine.


## Interview answer — deep senior

In modern Android architecture, the classic GoF State pattern has evolved into **Declarative State Machines (MVI)**. Instead of mutable context objects passing polymorphic pointers (`context.transitionTo(...)`), modern Kotlin architecture uses.

First, a `sealed interface DeviceState` representing immutable state models. Next, a `sealed interface DeviceEvent` representing incoming triggers.
Finally, a pure Reducer function: `reduce(currentState: DeviceState, event: DeviceEvent): DeviceState`.

This functional evolution preserves the exact intent of the State pattern while guaranteeing complete thread-safety, zero memory leaks, and seamless integration with Jetpack Compose.


## How to answer in the interview

- **Why:** Behavior variation and current workflow phase are different axes.
- **How:** Card/Wallet Strategy feeds one sealed checkout State reducer.
- **Trade-off:** Lambda strategy may suffice; state transitions still need tests.
- **Failure case:** Impossible boolean combinations or timeout mapped to definite failure.
- **Production solution:** Test provider outcomes against one legal transition table.

## Deep-dive talking points

Draw two axes—provider choice and checkout lifecycle—and test each independently.

## Follow-up questions

- **Interviewer:** "Can a class use both State and Strategy simultaneously?"
  **Answer:** "Yes. An `AudioPlayer` can use the State pattern to manage playback lifecycles (`Playing`, `Paused`, `Buffering`), while simultaneously using the Strategy pattern to select an audio decoding strategy (`OpusDecoder` vs `FlacDecoder`)."

- **Interviewer:** "How does the State pattern eliminate complex nested if/else statements?"
  **Answer:** "Instead of checking `if (state == PLAYING) ... else if (state == PAUSED)` in every method, the context delegates execution directly to `currentState.handle()`, replacing branching logic with polymorphism."

## Self-check rubric

State who selects Strategy, what changes State, and model a timeout without declaring failure.

## References and reviewed-on date

- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — original Strategy and State patterns.
- [Android UI state guidance](https://developer.android.com/topic/architecture/ui-layer/stateholders) — screen state modeling.

Technically reviewed against primary documentation on 2026-10-13.

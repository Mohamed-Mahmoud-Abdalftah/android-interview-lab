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

## Concept and technical explanation

The State and Strategy patterns share identical Unified Modeling Language (UML) structural class diagrams based on interface delegation, but diverge fundamentally in their behavioral intent, contextual ownership, and state transition mechanics. In the Strategy pattern, the client explicitly chooses, configures, or injects a specific algorithm from the outside; strategies are typically stateless, independent of one another, and execute interchangeable algorithmic calculations without knowing about other strategies. In the State pattern, the context object encapsulates dynamic behavioral modes where the internal state alters its behavior autonomously; concrete state subclasses are tightly coupled to state transition graphs, actively driving transitions to subsequent state nodes as internal lifecycle events unfold.

## Practical walkthrough (English)

Contrasting Strategy vs State implementations in Kotlin:
```kotlin
// 1. STRATEGY PATTERN: Client injects interchangeable algorithm from outside
interface ShippingCostStrategy { fun calculateCost(weightKg: Double): Double }
class StandardShipping : ShippingCostStrategy { override fun calculateCost(weightKg: Double) = weightKg * 5.0 }
class ExpressShipping : ShippingCostStrategy { override fun calculateCost(weightKg: Double) = weightKg * 15.0 + 20.0 }

class OrderCheckout(var shippingStrategy: ShippingCostStrategy) {
    // Client or UI sets strategy based on user selection; strategies don't know each other
    fun finalizeOrder(weightKg: Double): Double = shippingStrategy.calculateCost(weightKg)
}

// 2. STATE PATTERN: Internal autonomous state transition machine
sealed interface MediaPlayerState {
    fun play(player: MediaPlayerContext)
    fun pause(player: MediaPlayerContext)
}

class PlayingState : MediaPlayerState {
    override fun play(player: MediaPlayerContext) { /* Already playing */ }
    override fun pause(player: MediaPlayerContext) {
        println("Pausing audio playback")
        player.state = PausedState() // State itself drives the transition!
    }
}

class PausedState : MediaPlayerState {
    override fun play(player: MediaPlayerContext) {
        println("Resuming audio playback")
        player.state = PlayingState() // State itself drives the transition!
    }
    override fun pause(player: MediaPlayerContext) { /* Already paused */ }
}

class MediaPlayerContext { var state: MediaPlayerState = PausedState() }
```

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

Strategy and State share identical interface delegation structures but have opposing intents. Strategy encapsulates interchangeable algorithms chosen by the client from the outside, with strategies remaining independent and unaware of each other. State encapsulates dynamic behavioral modes where the context's behavior changes autonomously, and concrete state classes actively drive transitions to other states as events occur.

## Interview answer — structured

While the State and Strategy patterns appear structurally identical in class diagrams, their architectural purpose and operational dynamics are completely distinct.
In the Strategy pattern, the primary intent is providing interchangeable implementations of a specific algorithmic capability. The consuming client or caller explicitly selects, configures, or injects the strategy from the outside. Strategies are typically stateless and operate in total isolation; an ExpressShippingStrategy has no knowledge of or relationship to a StandardShippingStrategy. The client changes the strategy when a functional preference changes, such as selecting a payment gateway or sorting criteria.
In the State pattern, the primary intent is modeling an autonomous state machine where an object's observable behavior changes completely based on its internal state. The client does not manually swap state implementations; rather, state transitions occur internally in response to events and lifecycle triggers. Crucially, concrete state implementations know about each other, actively instantiating and transitioning the context to subsequent state nodes.
In Android, Strategy is ideal for dynamic policies like discount calculations and retry backoffs, while State is ideal for lifecycle-rich components like media players, connection session holders, and complex checkout workflows.

## Interview answer — deep senior

Under the hood, both patterns delegate work through an interface reference held by a context object, utilizing polymorphic virtual method dispatch. The senior distinction lies in transition ownership and mutability dynamics.
Strategy represents a 'has-a' relationship representing a swappable tool. Because strategies are usually stateless, they can be instantiated as immutable singletons and shared across multiple threads safely without synchronization overhead. In Kotlin, trivial strategies are often simplified into first-class lambdas (val sortStrategy: (Item, Item) -> Int), entirely bypassing class generation.
State represents an evolving lifecycle mode. Concrete state classes frequently require bidirectional access to the context object to trigger transitions (context.setState(NewState)). In legacy object-oriented designs, this created cyclic references and mutable state leak hazards.
Modern Android engineering reconciles the State pattern with reactive Unidirectional Data Flow (UDF). Rather than utilizing mutating state classes that pass context references around, senior engineers model state as an immutable sealed interface hierarchy (sealed interface PlayerState: Idle, Buffering, Playing, Error). A ViewModel or StateMachine reducer acts as the single transition authority, receiving user intents and emitting new immutable states across a StateFlow.
This functional state transition paradigm provides all the encapsulation benefits of the classic GoF State pattern while eliminating mutable state bugs, simplifying unit testing, and integrating seamlessly with Jetpack Compose re-composition cycles.

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

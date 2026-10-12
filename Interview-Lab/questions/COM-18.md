---
id: "COM-18"
question: "What are Route Composable and Screen Composable?"
topic: "Jetpack Compose"
code: "COM"
group: "B"
phase: 3
priority: "P1"
order: 247
editorial_status: "reviewed"
---

# COM-18

## Original interview question

What are Route Composable and Screen Composable?

## What the interviewer evaluates

- Separate app wiring/navigation from reusable rendering.
- Explain state collection, ViewModel ownership and callbacks.
- Avoid treating the split as a framework requirement.

## Explanation in Arabic

Route composable هي boundary للتطبيق: تستخرج navigation arguments، تحصل على ViewModel بالـowner الصحيح، تجمع state مع lifecycle، وتوصل callbacks/navigation. Screen composable تأخذ `UiState` وevents/`Modifier` كمدخلات وتعرض UI بدون معرفة NavController أو Hilt. هذا pattern تنظيمي وليس API إلزامي من Compose. فائدته previews واختبارات UI أسهل وإعادة استخدام الشاشة؛ لو الشاشة بسيطة جدًا قد يكون فصلها إلى ملفين زائدًا، لكن لا تخلط load/network مباشرًا في body.

## Why it matters and how it works

The route couples the screen to application concerns such as a back stack entry, dependency creation, and lifecycle collection. The screen is a rendering function over explicit inputs, so preview and Compose tests can supply states directly. Event callbacks flow to the route or ViewModel. The navigation owner matters because a ViewModel scoped to the wrong graph or destination can retain or lose state unexpectedly.

## Worked example

`ProductRoute(productId, onBack)` retrieves its ViewModel and `uiState`, then calls `ProductScreen(state, onRetry, onAddToCart, modifier)`. The Screen renders loading/error/product content in preview without Hilt or NavController. The Route handles Add-to-Cart result navigation and parses a small ID, while repository loading remains in the ViewModel.

## Trade-offs and decision criteria

The split improves testability and keeps UI dependencies narrow, but adds function parameters and can become ceremony for a tiny static screen. Passing a single state object and focused callbacks balances readability. Avoid an excessively generic `onEvent(Any)` API that hides contracts.

## Failure modes

The Screen reaches into NavController, breaking previews and reuse. The Route holds long-lived mutable form data only in a local variable. The ViewModel is obtained under the Activity owner when it should be destination-scoped, causing stale data on back-stack changes. A route serializes a large object in navigation arguments.

## Production perspective

Adopt consistent ownership in feature modules, provide previews for key states, and test Route integration separately from Screen rendering. Verify back-stack recreation and deep-link arguments for screens that navigate independently.

## Interview answer — short

“A Route wires navigation, ViewModel and lifecycle state; a Screen renders explicit state and reports events. It is an architectural convention for clear ownership and testability.”

## Interview answer — structured

“I use a Route at the destination boundary to obtain the ViewModel, collect its state, parse the route ID and connect navigation. The Screen gets only `UiState`, callbacks and a Modifier, so I can preview loading, error and success without a graph. The split also makes UI tests focused. I keep the ViewModel scoped to the intended back-stack owner and avoid passing large objects as route arguments.”

## Interview answer — deep senior

“Route and Screen are names for an application design seam, not magic Compose components. The Route knows the destination and its owner: it reads a small navigation argument, obtains the correct ViewModel, collects state with lifecycle awareness, and maps callbacks to actions or navigation. The Screen knows how to render a supplied model and issue user intents through typed callbacks. That lets me preview and Compose-test loading, error, ready and permission states without creating a NavController, Hilt graph or network. It also makes it easier to keep effects out of rendering. I remain careful about the owner: using an Activity-scoped ViewModel accidentally can preserve data across destinations that should be independent, while obtaining a new instance on every recomposition would lose state. I test deep links and back-stack recreation at the Route level and state/semantics at the Screen level. For a small static leaf the split may not warrant extra files, but the same principle still applies: external wiring and UI description have distinct responsibilities.”

## Deep-dive talking points

Explain app boundary, UI inputs, ViewModelStoreOwner, previews, typed events, and test layers.

## Follow-up questions

- Is Route/Screen required by Compose? **Answer:** no; it is a useful architectural convention.
- What can a Screen preview avoid? **Answer:** Hilt, network, and navigation setup by receiving explicit fake state.
- Why does ViewModel owner choice matter? **Answer:** it determines state lifetime across destination and back-stack changes.

## Self-check rubric

Assign wiring and rendering tasks, name the owner, and propose one Screen test and one Route test.

## References and reviewed-on date

- [Compose architecture](https://developer.android.com/develop/ui/compose/architecture) — state/event separation.
- [Navigation with Compose](https://developer.android.com/develop/ui/compose/navigation) — destination boundaries.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Route/Screen naming is a design convention.

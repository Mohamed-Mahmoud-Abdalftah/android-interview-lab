---
id: "ARC-09"
question: "How does UI state differ from business/domain state?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "A"
phase: 2
priority: "P1"
order: 154
editorial_status: "reviewed"
---

# ARC-09

## Original interview question

How does UI state differ from business/domain state?

## What the interviewer evaluates

Separate durable business facts from screen-specific rendering and interaction state.

## Explanation in Arabic

Domain state حقيقة تخص business زي `OrderStatus.Paid` من server أو `AccountBalance` validated. UI state هي snapshot الشاشة: loading، displayed text، selected tab، enablement، snackbar/permission prompt visibility. نفس domain value ممكن يترندر بشكل مختلف حسب locale والشاشة. UI state أحيانًا ephemeral وتختفي بعد recreation، لكن business state لازم مصدرها data layer وتترجع بعد process death. ما تعتبرش `success = true` في ViewModel دليل إن payment اتسجل؛ السيرفر مصدر الحقيقة.

## Why it matters and how it works

UI state describes what to display now, while domain state describes application facts and rules. A ViewModel transforms domain/data streams into screen state; the repository remains responsible for the underlying source of truth.

## Worked example

Conceptual mapping: `Order(status = Pending, totalMinor = 1299)` is domain data; `CheckoutUiState(showSpinner = true, totalText = "EGP 12.99", canRetry = false)` is presentation. On server confirmation, repository updates order status; ViewModel emits a new UI state. The label is not persisted as canonical money.

## Trade-offs and decision criteria

A separate UI model costs mapping but prevents display details from contaminating domain. Very small screens may render a domain model directly if no distinct presentation contract exists. Do not persist every transient UI flag as though it were business truth.

## Failure modes

A ViewModel sets `isPaid = true` after an HTTP timeout because it saw a local click. The client has no confirmed outcome; render pending verification and reconcile. Another failure is storing locale-formatted amount in database and later parsing it for payment logic.

## Production perspective

An order details screen observes Room-backed order status and composes locale-specific text. After process death, it reloads business status from repository; selected accordion state may restore from saved UI state if worthwhile.

## Interview answer — short

Domain state is a business fact or rule, while UI state is the screen’s current renderable snapshot. ViewModel maps one into the other, and durable facts come from the data source of truth rather than a UI flag.

## Interview answer — structured

An order can be `Pending` in the domain while one screen shows a spinner and another shows a status badge. Those visual choices are UI state. Domain state carries facts that other features and the server care about; UI state carries display text, selection, loading, and interaction flags. I map between them in a state holder and restore durable facts from the repository after process death. A local success animation never becomes proof of a completed payment. In a checkout screen, a pending server transaction can display a spinner, a status badge, or a retry-disabled button depending on the screen. Those are projections, while the request ID and confirmed status are domain data. I keep the projection recomputable.

## Interview answer — deep senior

I separate lifetime and authority. Domain data such as an account balance or payment status should be validated and obtained from the app’s data layer, with server authority where appropriate. UI state is a projection for one screen; it may include localized strings, transient loading, selected tab, or whether a button is enabled. Some UI state deserves SavedStateHandle restoration, while other effects can be derived anew. Conflating them causes bugs: a local Boolean can masquerade as a payment result, or a formatted string can be used as a monetary amount. I model domain transitions explicitly, use the repository as source of truth, and let each ViewModel derive its own immutable UI state. Tests verify both policy and rendering separately. I also consider restoration separately. A selected tab might be saved in a SavedStateHandle, while a confirmed payment must come from repository/server state after recreation. If the ViewModel merely remembers a Boolean, process death can erase or falsely preserve a conclusion. Tests should cover mapping the same domain state into different screen models and should verify that transport uncertainty never becomes a paid UI state. This separation protects both UX and business correctness.

## Deep-dive talking points

Contrast durable order status with a screen spinner, selected tab, and localized total. Discuss process death and server authority for payments.

## Follow-up questions

- [ARC-10](../arc-10/): Where does durable order status live? **Answer:** in a data source of truth, not only a ViewModel flag.
- [ARC-11](../arc-11/): What belongs in UI state? **Answer:** loading, content, empty/error display and interaction status.

## Self-check rubric

Give two domain facts and two UI-only fields, then explain how a ViewModel derives UI state after recreation.

## References and reviewed-on date

- [Android state holders](https://developer.android.com/topic/architecture/ui-layer/stateholders) — screen UI state versus data.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — application data ownership.

Technically reviewed against the linked official Android architecture guidance on 2026-10-11. Conceptual flows and snippets are not device-tested.

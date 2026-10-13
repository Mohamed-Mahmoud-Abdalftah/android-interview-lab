---
id: "ARC-12"
question: "How should domain/data errors be mapped into actionable UI errors?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "B"
phase: 2
priority: "P1"
order: 157
editorial_status: "reviewed"
---

# ARC-12

## Original interview question

How should domain/data errors be mapped into actionable UI errors?

## What the interviewer evaluates

Map typed domain/data failure categories into actionable UI behavior without leaking raw exception text.

## Explanation in Arabic

Data layer تعرف `IOException`, HTTP status، database failure؛ domain ممكن تعبّر عنها كـ`Offline`, `Unauthorized`, `Validation(field)`, `Conflict`, `Unknown` حسب contract. Presentation تحوّل category إلى message localized وaction: retry، login، تصحيح field، أو انتظار sync. ما تعرضش `exception.message` مباشرة: ممكن يكون غير مفهوم أو يحتوي sensitive data. وما تحولش كل error إلى “حصل خطأ” لو user يقدر يتصرف. في payment timeout لازم `PendingVerification` مش “Failed” مؤكدة، لأن السيرفر ممكن يكون نفّذ الطلب.

### Practical walkthrough in Egyptian Arabic

Data errors الخام مثل 401/409/timeout لا تذهب UI كنص backend. Repository يصنف transport/auth/conflict، domain يحدد معنى business، ViewModel يحولها لفعل: login, retry, resolve conflict, or Unknown status. Cancellation تظل cancellation. لا تعرض “فشل الدفع” عند timeout غير محسوم؛ اعرض pending واستعلم status.

## Why it matters and how it works

Error mapping separates transport details from product decisions. Stable categories let UI render guidance and tests assert behavior without parsing strings. Keep diagnostic causes and correlation IDs in protected logs, not public UI text.

## Worked example

Conceptual mapping: repository catches an HTTP 401 and yields `AuthRequired`; transport timeout yields `Uncertain(requestId)` for a submitted payment; ViewModel maps these to `LoginAgain` or `CheckingStatus` screen states. Cancellation propagates rather than becoming `Unknown`.

## Trade-offs and decision criteria

More categories improve actionability but can overfit every HTTP code. Model decisions the UI can actually make. Preserve unknown failures with observability and a safe generic message. Localization belongs in UI/resources.

## Failure modes

A repository catches `Throwable`, including coroutine cancellation, and maps every case to “retry,” causing cancelled requests to trigger UI errors. Rethrow cancellation and classify only expected failures. Raw server messages can leak account details or mislead.

## Production perspective

An account app gives offline users a retry with cached data, unauthorized users a reauthentication route, and validation errors field-level hints. Telemetry records safe category and correlation ID, never a token.

## Interview answer — short

I map low-level failures into stable domain categories, then into localized UI messages and actions. I preserve diagnostic context privately, propagate cancellation, and represent uncertain server outcomes explicitly.

## Interview answer — structured

The repository should translate network and storage exceptions into a small domain error taxonomy, such as offline, auth required, validation, or unknown. The ViewModel maps that into what the user can do: retry, sign in, correct a field, or wait for verification. I do not pass raw exception messages to Compose because they are unstable and may leak details. I keep cancellation out of the error path and treat payment timeouts as uncertain rather than rejected. A 401 can lead to reauthentication; a validation response can point to a field; an offline read may show cached data with retry. A generic error card for all three loses useful information. But raw server text can also be unsafe or unstable.

## Interview answer — deep senior

I design errors from recovery behavior. HTTP status alone is not the domain contract; different endpoints may have different meanings. Data maps transport failures and preserves safe diagnostic context, while domain outcomes express stable product categories. Presentation turns them into localized text and available actions. I test every mapping, including malformed responses and unknown codes. A cancelled coroutine must remain cancelled. A payment timeout can follow a committed server operation, so the UI shows pending verification and repository reconciles before enabling a retry. Logs use correlation IDs and scrub sensitive payloads. This avoids both extremes: leaking raw infrastructure exceptions into UI and collapsing actionable failures into a generic message. I define error categories at a boundary where transport details are understood, then preserve a safe code and correlation ID for diagnostics. UI chooses localized text and action, not a parser of exception messages. I test unknown codes and malformed responses, because a new server status should not silently become success. For network writes, an uncertain timeout deserves verification rather than an automatic retry that could duplicate effects. Cancellation passes through the coroutine hierarchy as control flow.

## How to answer in the interview

- **Why:** error semantics drive safe action.
- **How:** map transport to domain to UI action.
- **Trade-off:** precise types versus modeling cost.
- **Failure case:** timeout shown as decline and user pays again.
- **Production solution:** typed errors and user-safe recovery.

## Deep-dive talking points

Trace an IOException, 401, validation response and uncertain payment timeout through data/domain/UI layers.

## Follow-up questions

- [KOT-28](../kot-28/): Why use typed errors? **Answer:** callers can choose recovery without parsing exception text.
- [ARC-11](../arc-11/): Can error coexist with content? **Answer:** yes, a refresh error can coexist with cached content.

## Self-check rubric

Can you map four failures to different user actions and explain where localization, cancellation and telemetry belong?

## References and reviewed-on date

- [Android UI events](https://developer.android.com/topic/architecture/ui-layer/events) — state-driven UI actions.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — data boundary.

Technically reviewed against the linked official Android guidance on 2026-10-11. Conceptual examples are not device-tested.

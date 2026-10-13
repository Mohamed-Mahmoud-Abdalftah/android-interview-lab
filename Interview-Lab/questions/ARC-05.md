---
id: "ARC-05"
question: "What belongs in ViewModel versus UseCase versus Repository?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "A"
phase: 2
priority: "P1"
order: 150
editorial_status: "reviewed"
---

# ARC-05

## Original interview question

What belongs in ViewModel versus UseCase versus Repository?

## What the interviewer evaluates

Place UI state/lifecycle, reusable policy, and data-source coordination with the right owner.

## Explanation in Arabic

ViewModel شاشة: تستقبل UI events، تنادي domain/data، وتطلع `UiState` مناسب للعرض؛ ما تمسكش View/Activity reference وما تعملش blocking I/O على Main. UseCase، لو موجودة، لقاعدة business أو workflow معاد استخدامها أو معقدة، من غير Android UI types. Repository لداتا التطبيق: local/remote، cache، merge، error mapping من transport. مثال: ViewModel يحوّل `Balance` لعملة معروضة؟ formatting المحلي للـUI عند presentation؛ التحقق من حد التحويل في domain؛ جلب balance وحفظه في data.

### Practical walkthrough in Egyptian Arabic

ViewModel يحول events إلى UiState ويمسك scope للشاشة؛ UseCase ينفذ business decision قابل للاستخدام خارج الشاشة؛ Repository يتعامل مع cache/network/DB. لو ViewModel فيها JSON parsing وretry/payment rule، ابدأ بنقل rule مع test ثم adapter، لا rewrite كامل. UI state بعد process death يعاد من durable ID. راقب إن ViewModel لا تحتفظ بـActivity.

## Why it matters and how it works

Screen state holder owns state production and event handling. Domain use cases encapsulate reusable business operations. Repositories expose data and coordinate sources. Keeping owners distinct makes lifecycle, testing, and change impact clearer.

## Worked example

Conceptual flow: `TransferViewModel.onSubmit` disables duplicate UI submit and calls `SubmitTransferUseCase`; the use case enforces amount rules and invokes `TransfersRepository`; repository sends with an idempotency key and persists pending status; ViewModel maps result to `TransferUiState`. Server still validates the transfer.

## Trade-offs and decision criteria

A small screen can call a repository directly. Do not move every `map` into a use case: formatting or selection purely for a screen can live in Presentation. Conversely, a rule needed by multiple screens should not be copied across ViewModels.

## Failure modes

A 1,000-line ViewModel that parses JSON and retries network requests becomes hard to test and lifecycle-sensitive. A repository that emits Snackbar string resources leaks UI concerns. A use case that holds Activity context is not presentation-independent.

## Production perspective

A checkout feature tests ViewModel state transitions with a fake use case, transfer policy with fake repositories, and repository sync with fake service/DAO. Production logs distinguish user action, policy rejection, and transport uncertainty.

## Interview answer — short

ViewModel owns screen state and user-event handling; UseCase owns reusable or complex business behavior; Repository owns app data and source coordination. I place code by reason to change and keep boundaries typed.

## Interview answer — structured

I ask whether a line of code changes when the screen design changes, a business rule changes, or a storage/network mechanism changes. The ViewModel should handle the first, including loading and error UI state. A use case, when justified, handles the second. The repository handles the third and may own data consistency rules. That means a ViewModel should not call Retrofit directly, and a repository should not emit localized Snackbar text. A small feature may skip the use case layer. I also decide who owns timing. The ViewModel can cancel an obsolete search when the screen leaves, but a committed payment should have a persisted request identity and reconciliation path. That lifecycle distinction is as important as where a method lives.

## Interview answer — deep senior

There are gray areas, so I use ownership questions rather than a rigid checklist. A repository can contain data-centric business logic such as conflict resolution because it owns the source of truth. A use case expresses product behavior across repositories or reused by multiple screens. A ViewModel produces UI state and calls those APIs in a lifecycle-aware scope, but should not be a durable transaction owner. For an uncertain transfer, repository and server track status through process death; ViewModel only renders the resulting state. I test each boundary with a fake for the next one down, and I review public types to ensure transport DTOs and Android Views do not cross into domain. If a use case merely forwards a call, it may not earn its maintenance cost. A difficult review case is a rule that mixes data and presentation. I ask whether the result is valid across screens and locales. Transfer limits are domain policy; a red warning label is UI. Repository owns the latest validated limit data and request status, while domain applies policy and ViewModel maps to screen state. Tests should prove that a timeout leads to pending verification rather than a false success or failure. A thin ViewModel is useful only if the lower layers have clear contracts.

## How to answer in the interview

- **Why:** one owner per kind of decision.
- **How:** route event through VM, policy and data.
- **Trade-off:** smaller classes versus navigation overhead.
- **Failure case:** VM becomes network and ledger god object.
- **Production solution:** refactor slice with regression test.

## Deep-dive talking points

Walk a transfer submit from tap to server confirmation. Separate UI duplicate-tap handling, policy validation, data retry, and server authority.

## Follow-up questions

- [ARC-18](../arc-18/): Who ensures blocking work is main-safe? **Answer:** the data/domain boundary should provide main-safe suspend APIs; ViewModel calls them.
- [ARC-13](../arc-13/): Must every screen have use cases? **Answer:** no; only when complexity/reuse justifies them.

## Self-check rubric

Place four lines of transfer code with ViewModel, UseCase, or Repository; explain why an uncertain result cannot be treated as success.

## References and reviewed-on date

- [Android UI layer](https://developer.android.com/topic/architecture/ui-layer) — ViewModel state-holder role.
- [Android domain layer](https://developer.android.com/topic/architecture/domain-layer) — use-case scope.

Technically reviewed against the linked official Android architecture guidance on 2026-10-11. Conceptual flows and snippets are not device-tested.

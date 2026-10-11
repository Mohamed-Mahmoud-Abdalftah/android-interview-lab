---
id: "PAT-16"
question: "You need to swap vendor SDKs with different callbacks. Which patterns and boundaries help?"
topic: "Design Patterns"
code: "PAT"
group: "C"
phase: 2
priority: "P1"
order: 207
editorial_status: "reviewed"
---

# PAT-16

## Original interview question

You need to swap vendor SDKs with different callbacks. Which patterns and boundaries help?

## What the interviewer evaluates

Use adapters and a stable boundary to switch vendor callbacks without leaking vendor types or result semantics.

## Explanation in Arabic

Vendor A ترجع callback `onSuccess/onError`، Vendor B ترجع listener مع status codes مختلفة. اعمل Adapter لكل SDK يحوّل لdomain-facing `PaymentGateway` أو `IdentityVerifier` contract. Facade/Repository قدامهم تبقى API واحدة للfeatures، وDI composition تختار implementation. لازم توحّد semantics مش syntax بس: duplicate callbacks، cancellation، timeout، threading، request IDs. tests fake SDKs بتجرّب callback order وأخطاء. لما تبدّل vendor، UI وdomain ما يستوردوش SDK classes. Server validation والsecrets تفضل على backend.

## Why it matters and how it works

Adapters translate incompatible interfaces; a facade or repository exposes a stable application contract. DI supplies the active vendor. Migration is safe only when behaviors and failure semantics are compared, not just method names.

## Worked example

Conceptual contract: `suspend fun verify(requestId: String): VerificationOutcome`. Vendor A adapter resumes once from callbacks and unregisters on cancellation; Vendor B adapter maps status codes and may query server for uncertain outcomes. Both pass one contract suite.

## Trade-offs and decision criteria

A generic gateway adds indirection but localizes vendor churn. If vendors differ in capabilities, expose optional capabilities explicitly rather than falsifying a single contract. A facade should not become a vendor switch with every SDK detail.

## Failure modes

Vendor A fires success twice after retry; adapter resumes/handles twice and UI navigates twice. Guard callback completion, persist request identity, and let server decide final status. Cancellation of waiting does not necessarily cancel remote work.

## Production perspective

A bank app swaps identity SDKs behind a verification boundary with staged rollout and metrics on error mapping. Tests compare accepted, rejected, timeout and cancellation; no identity data is logged raw.

## Interview answer — short

I put each vendor behind an Adapter and expose a stable domain-facing Facade or Repository contract. The switch then changes the adapter and wiring, while contract tests protect callback, timeout and cancellation behavior.

## Interview answer — structured

I would first define the result semantics the app needs, then write an adapter for each vendor’s callback shape. A facade or repository exposes that result without SDK types. The app DI graph selects the active adapter. Before replacing a vendor, I run the same contract tests against both: success, rejection, duplicate callback, timeout and cancellation. If a vendor has a missing capability, I model that explicitly rather than throw unexpectedly. Backend status remains the final authority for sensitive operations.

## Interview answer — deep senior

Vendor swaps fail when an adapter only changes method signatures but not behavior. One SDK may call back on Main, another on a worker; one may invoke twice; cancellation may stop a listener but not a remote transaction. I design a domain contract with thread, lifetime and outcome semantics and put each SDK behind an adapter. A facade/repository coordinates durable request identity and maps unknown outcomes to pending verification. DI handles selection, and staged rollout plus telemetry compares real failure categories without exposing personal data. UI and domain import only stable types, so vendor classes remain contained. I test callback order and resource cleanup in addition to happy-path values, and I keep provider credentials on the server.

## Deep-dive talking points

Compare callback semantics, thread, cancellation, duplicates, staged migration and server authority.

## Follow-up questions

- [PAT-04](../pat-04/): Adapter versus Facade? **Answer:** adapter translates vendor interface; facade offers a smaller app API.
- [PAT-12](../pat-12/): Why facade for unreliable SDK? **Answer:** normalize complexity while preserving typed uncertainty.

## Self-check rubric

Define a common outcome and two vendor adapters; specify four shared contract tests.

## References and reviewed-on date

- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — Adapter and Facade patterns.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — application data boundary.

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.

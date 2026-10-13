---
id: "SOL-18"
question: "A new payment provider requires editing 10 existing classes. Which principles would help?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "C"
phase: 2
priority: "P1"
order: 189
editorial_status: "reviewed"
---

# SOL-18

## Original interview question

A new payment provider requires editing 10 existing classes. Which principles would help?

## What the interviewer evaluates

Use OCP/DIP/SRP/ISP/LSP together for a provider change that touches too much code.

## Explanation in Arabic

Provider جديد بيستلزم تعديل 10 classes؟ أولًا اعمل change map: هل provider-specific checks موزعة في UI/ViewModel/repository؟ OCP توجّهك لـextension seam مثل `PaymentStrategy`; DIP تخلي checkout policy تعتمد على contract مش SDK. SRP تفصل provider translation عن UI state والbusiness rules. ISP تخلي contract ضيقة للعمليات المشتركة، وLSP تلزم كل adapter بنفس timeout/cancellation semantics. لكن إضافة provider لسه تحتاج DI wiring، server config، security/compliance review، واختبارات؛ ما توعدش بصفر تعديل.

## Why it matters and how it works

Scattered provider conditionals indicate a missing variation boundary. A narrow strategy adapter localizes SDK differences; stable policy remains shared. Substitution and error semantics are critical to safe replacement.

## Worked example

Migration sketch: extract one `PaymentGateway` contract from existing provider path, write contract tests, route current provider through adapter, then add second provider adapter and composition binding. Keep server-side provider credentials and final transaction verification.

## Practical walkthrough

لما provider جديد يلمس 10 classes، ارسم طريق التغيير: selection، policy، UI، analytics، SDK، backend mapping. مش كل تعديل خطأ؛ registration واختبارات provider الجديدة متوقعة. لكن تكرار `when` عبر الطبقات علامة إن variation مش في مكان واحد. اعمل `PaymentGateway` contract ضيق، adapter للموجود، tests مشتركة، ثم ضيف الجديد. خليك صريح إن provider ممكن يحتاج policy مختلفة أو legal flow خاص، فلا تضغط الاختلاف الحقيقي في interface كاذبة. راقب عدد الملفات المتغيرة في الإضافة التالية، وتأكد من server confirmation وidempotency.

## Trade-offs and decision criteria

A strategy layer is worth the cost if providers change or SDKs differ materially. For one stable provider, a concrete repository may be simpler. Avoid a god-factory that knows every SDK and business rule.

## Failure modes

One provider reports a timeout as confirmed failure and the UI retries, risking duplicate charge. Contract tests must require `PendingVerification` for uncertainty and reconciliation with the backend.

## Production perspective

A commerce app adds wallet provider by writing an adapter, binding it, and testing shared checkout policy plus provider-specific error mapping. Metrics compare outcomes across providers without leaking payment data.

## Interview answer — short

I would use OCP and DIP to create a narrow provider strategy boundary, SRP to separate SDK translation from business policy, and LSP/ISP to keep adapters safely substitutable. Wiring and verification still change.

## Interview answer — structured

Ten edited classes suggest provider decisions are scattered. I would first map those edits, then extract a `PaymentGateway` or strategy contract that checkout policy can use without knowing SDK types. Provider adapters translate callbacks and errors. The interface should include only shared capabilities and every implementation must preserve result and cancellation semantics. This localizes future additions, though DI registration, tests and server configuration still need changes. I would migrate the current provider first to verify the seam. I would first migrate the existing provider into the new seam and confirm no behavior changes, then add the next one.

## Interview answer — deep senior

I would not immediately build a plugin framework; I would trace why ten classes change. If UI, ViewModel and repositories all branch on provider code, I separate stable checkout policy from variable SDK operations. OCP motivates an extension seam, DIP sets source dependency direction, SRP keeps mapping out of UI, ISP keeps the gateway narrow, and LSP demands substitutable outcomes. I write contract tests for accepted, declined, timeout, duplicate callbacks and cancellation before adding another adapter. The backend still owns credentials and authoritative payment status; a timeout may require reconciliation rather than retry. New provider work should then mostly touch its adapter, app wiring and targeted integration tests. If differences cannot fit one truthful contract, I split capabilities instead of creating a god-factory with hidden special cases. I would inspect the ten edits before naming a principle. Some are legitimate, such as provider registration, copy, and tests; repeated branching through UI, policy, and data is the problem. OCP suggests a provider extension seam, DIP keeps policy from importing SDK types, SRP separates mapping from eligibility, and LSP requires every adapter to honor the shared outcome contract. I would migrate the existing provider through the contract first and add contract tests before adding the new one. The trade-off is extra indirection and potentially divergent provider capabilities. If legal or authorization rules truly differ, I would model that explicitly instead of forcing false uniformity. The backend remains authoritative for transaction state.

## How to answer in the interview

- **Why:** Trace the ten edits.
- **How:** propose one variation seam.
- **Trade-offs:** note legitimate registration edits.
- **Failure cases:** flag false uniformity.
- **Production solutions:** finish with adapter contracts and backend verification..

## Deep-dive talking points

Trace ten edits to one variation axis, propose migration steps, and verify provider contract semantics.

## Follow-up questions

- [SOL-03](../sol-03/): What does OCP change? **Answer:** add an adapter at a designed seam instead of scattering edits.
- [PAT-15](../pat-15/): How avoid a god-factory? **Answer:** keep selection/wiring separate from provider behavior and policy.

## Self-check rubric

Name three principles relevant to provider churn, show one contract, and include timeout reconciliation.

## References and reviewed-on date

- [Robert C. Martin, OCP](https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html) — extension boundaries.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — adapter ownership.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.

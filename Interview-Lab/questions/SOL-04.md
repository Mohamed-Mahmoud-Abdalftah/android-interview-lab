---
id: "SOL-04"
question: "Explain Liskov Substitution Principle with an Android example."
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "A"
phase: 2
priority: "P1"
order: 175
editorial_status: "reviewed"
---

# SOL-04

## Original interview question

Explain Liskov Substitution Principle with an Android example.

## What the interviewer evaluates

Test behavioral substitutability, including preconditions, postconditions and failure semantics.

## Explanation in Arabic

LSP معناها object من subtype ينفع يحل مكان base من غير ما يكسر توقعات client. مش مجرد compiler يقبل inheritance. لو `BaseStorage.save()` contract بتقول تحفظ وترجع result، subclass ترمي `UnsupportedOperationException` للـsave، فهي غالبًا لا تصلح substitution. Android مثال: `ImageLoader` implementations لازم تتفق على callback/cancellation/error semantics. subtype ما تزودش precondition مفاجئة ولا تضعف postcondition. أحيانًا الحل تقسيم interface أو composition بدل inheritance.

## Why it matters and how it works

Subtyping is a behavioral promise. Clients rely on documented preconditions, outcomes, side effects and lifetime. A subclass that rejects valid base calls or silently weakens results breaks that promise even if signatures match.

## Worked example

Illustrative contract: `interface ThumbnailLoader { suspend fun load(uri: Uri): Bitmap? }`. An implementation that throws for all remote URIs violates the contract if remote URIs were promised. Either narrow the contract to supported schemes or provide separate capabilities. This is conceptual Android code; imports and permission/lifecycle details are intentionally omitted.

## Practical walkthrough

لو `ThumbnailLoader` عقده بيقبل أي `Uri`، implementation محلي بيرمي exception مع `https` مش بديل صالح حتى لو الـcompiler وافق. اكتب contract واضح: أنواع URI المدعومة، null معناها إيه، وهل failure بترجع result ولا exception، وهل call قابل للإلغاء. بعدين شغّل نفس الاختبارات على disk وnetwork implementations. لو واحدة قدراتها أضيق، صغّر العقد أو افصل capability بدل ما تخبي المشكلة بـ`UnsupportedOperationException`. في Android خلي الاختبار يشمل permission وفقدان الاتصال، لأن دي الحالات اللي غالبًا تكشف اختلاف السلوك.

## Trade-offs and decision criteria

Inheritance is useful when all subtypes truly share behavior and invariants. Composition or small capability interfaces are safer when implementations differ fundamentally. Overly strict contracts can exclude useful implementations, so document supported inputs explicitly.

## Failure modes

`OfflineImageLoader` overrides `load` and throws for every HTTP URI accepted by the base contract; callers now need subtype checks, showing substitution failed. Fix the contract or use a separate loader strategy with declared capabilities.

## Production perspective

An SDK adapter contract defines success, failure, cancellation and timeout behavior. Contract tests run against each vendor implementation to ensure callers can swap providers without hidden special cases.

## Interview answer — short

LSP means a subtype must honor the behavior promised by its base type, not just match its method signatures. If an implementation throws for a valid base operation, I revisit the contract or use smaller interfaces.

## Interview answer — structured

I review a subtype from the caller’s perspective. Can the caller use it without new `is VendorX` branches or surprise exceptions? A base contract includes supported inputs, result meaning, cancellation and side effects. If a subclass strengthens preconditions or weakens guarantees, it violates substitution. For example, a storage implementation that throws `UnsupportedOperationException` for a promised `save` method is a poor subtype. I would split capabilities or prefer composition. For Android, cancellation behavior is part of the promise too.

## Interview answer — deep senior

LSP is the behavioral side of polymorphism. The compiler verifies signatures, but it cannot prove that every implementation accepts the same valid inputs, returns outcomes with the same meaning, or preserves cancellation and failure contracts. In Android, adapters for image loading, payments or storage are often swapped by DI. I write contract tests that every implementation must pass: successful input, invalid input, timeout, cancellation, and resource cleanup. If one provider cannot support a promised operation, I do not hide that behind a runtime throw. I narrow the abstraction, split interfaces, or model capability explicitly. Inheritance is useful only where the shared contract is real; otherwise composition makes differences visible. Substitution is behavioral: the caller must be able to use any promised implementation without changing its assumptions. I would write the preconditions, postconditions, and error behavior of `ThumbnailLoader` before deciding if a disk-only adapter belongs there. If remote URIs are valid inputs, throwing only from one implementation surprises callers and violates that promise. We can narrow the input contract, split local and remote capabilities, or have both return an explicit unsupported result if that is part of the contract. The production test is a shared suite run for every implementation, including cancellation and permission errors. A type-compatible subclass alone proves very little.

## How to answer in the interview

- **Why:** State the behavioral promise.
- **How:** test both implementations with the same cases.
- **Trade-offs:** discuss narrower contracts.
- **Failure cases:** show the throwing subtype.
- **Production solutions:** finish with contract tests including Android failures..

## Deep-dive talking points

Discuss behavioral contracts beyond signatures, strengthened preconditions, weakened postconditions and contract-test suites.

## Follow-up questions

- [SOL-10](../sol-10/): Why can BaseFragment violate LSP? **Answer:** a no-toolbar fragment cannot honor a mandatory toolbar operation.
- [SOL-17](../sol-17/): What does UnsupportedOperationException signal? **Answer:** possibly a broken substitution contract.

## Self-check rubric

State one behavioral promise, one violating subclass, and a contract test or interface split.

## References and reviewed-on date

- [Liskov and Wing, A Behavioral Notion of Subtyping](https://www.cs.columbia.edu/~wing/publications/LiskovWing94.pdf) — behavioral substitution; hosted academic copy.
- [Kotlin inheritance](https://kotlinlang.org/docs/inheritance.html) — language mechanics only.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.

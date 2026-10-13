---
id: "SOL-19"
question: "When should you deliberately accept a little duplication instead of introducing an abstraction?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "C"
phase: 2
priority: "P1"
order: 190
editorial_status: "reviewed"
---

# SOL-19

## Original interview question

When should you deliberately accept a little duplication instead of introducing an abstraction?

## What the interviewer evaluates

Choose small duplication over premature shared abstraction when concepts only look alike.

## Explanation in Arabic

مش كل duplication لازم تتشال فورًا. لو شاشتين عندهم form validation شبه بعض لكن rules مرشحة تختلف، “universal validator” بـflags وcallbacks يمكن يكون أصعب من نسختين صغيرتين واضحتين. استنى تلات استخدامات أو variation حقيقية؟ دي heuristic مش قانون. اسأل: هل نفس business concept والسبب للتغيير واحد؟ لو آه extract cohesive abstraction. لو مجرد شكل الكود شبه بعض، احتفظ بتكرار محدود واختبارات واضحة. تكلفة wrong abstraction تشمل branching، coupling، migration على كل feature.

## Why it matters and how it works

A premature abstraction can couple independent changes and create configuration flags. Duplication has a visible local cost; a wrong shared model can make every change harder. Extract when the common behavior and invariant are proven.

## Worked example

Example: checkout address validation requires a verified billing postcode, while profile address edit permits an optional postcode. A shared `validateAddress(isCheckout: Boolean)` may grow flags. Two small validators can remain separate until a stable common primitive emerges.

## Practical walkthrough

عندك validation عنوان في checkout يتطلب billing postcode مؤكد، وفي profile التعديل يسمح postcode فاضي. تشابه السطور مغري لعمل `validateAddress(isCheckout)`، بس flag هيتوسع ومعنى الدالتين مختلف. سيب التكرار الصغير مؤقتًا، مع tests توضح شرط كل flow. لما يظهر stable primitive مثل postcode format مستقل عن policy، استخرجه فقط. القرار يتغير لو bugs متكررة في نفس logic وبيحتاجوا تحديث متزامن. التكرار هنا تكلفة واعية، مش تجاهل للنظافة؛ وثّق نقطة المراجعة بعد variation ثالثة أو change history واضح.

## Trade-offs and decision criteria

Duplication risks drift and repeated bug fixes. A genuine shared policy should be centralized. Accept modest duplication only when the variation is unclear or change reasons differ; revisit with evidence.

## Failure modes

A “generic” form engine gains ten Boolean switches and a reflection registry, making a simple new field require edits in every feature. Unwind to explicit feature rules and extract only shared invariant pieces.

## Production perspective

A team allows two small UI mappers for different screens while sharing one authoritative tax calculation policy. They track divergent bugs and extract common behavior when stable.

## Interview answer — short

I accept small, clear duplication when two pieces only look alike but may change for different reasons. A premature abstraction can create flags and coupling; I extract once the shared invariant is real.

## Interview answer — structured

I compare the reason each copy changes. Two screens may both have address validation but one follows billing rules and the other profile-edit rules. A universal validator with mode flags could be harder to maintain than two small explicit functions. I would keep the duplication temporarily, test both, and revisit after the variation becomes clear. If both are applying the same tax law or security policy, that is genuine shared behavior and should be centralized. I would mark duplicated rules for later review and watch whether bug fixes repeatedly need the same change in both places. That is evidence of a real shared invariant.

## Interview answer — deep senior

Abstraction is a bet that two behaviors will continue to change together. If that bet is wrong, every new requirement adds conditionals to a shared component and couples independent teams. A few duplicated lines can be a safer, reversible choice. I inspect domain meaning, change actors and invariants rather than visual code similarity. In an Android app, two UI mappers may legitimately differ by screen, while the authoritative pricing rule should not be copied. I keep tests around each path and monitor whether bug fixes must be repeated. When the common part stabilizes, I extract a small named primitive with a truthful contract—not a giant configurable engine. I accept duplication when two pieces look similar but answer different change requests. Checkout address validation may require a verified billing postcode, while profile editing may permit an optional one. A shared function with `isCheckout` flags tends to accumulate policy branches and makes each flow harder to reason about. I would keep two small validators with separate tests, then extract a genuinely stable primitive such as postcode syntax if both need it. The trade-off is possible drift; repeated identical bug fixes are evidence to revisit the decision. I would state that trigger explicitly in review rather than abstracting on the first two matching lines.

## How to answer in the interview

- **Why:** Use address-policy divergence.
- **How:** explain extraction trigger.
- **Trade-offs:** acknowledge drift cost.
- **Failure cases:** flag boolean-flag abstraction.
- **Production solutions:** finish with separate tests and review threshold..

## Deep-dive talking points

Compare syntactic duplication with semantic duplication; diagnose mode-flag growth and extraction timing.

## Follow-up questions

- [SOL-03](../sol-03/): Should OCP create every possible extension seam now? **Answer:** no; closure is strategic around credible change axes.
- [SOL-20](../sol-20/): How explain trade-offs? **Answer:** compare maintenance cost of duplication and abstraction using real change examples.

## Self-check rubric

Give an example of safe temporary duplication and one shared policy that must be centralized.

## References and reviewed-on date

- [Android domain layer](https://developer.android.com/topic/architecture/domain-layer) — extracting reusable business logic when justified.
- [Robert C. Martin, SRP](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — change reasons.
- [Robert C. Martin, OCP](https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html) — strategic extension.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.

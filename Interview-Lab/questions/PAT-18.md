---
id: "PAT-18"
question: "How can patterns turn into unnecessary indirection? Give an example."
topic: "Design Patterns"
code: "PAT"
group: "C"
phase: 2
priority: "P1"
order: 209
editorial_status: "reviewed"
---

# PAT-18

## Original interview question

How can patterns turn into unnecessary indirection? Give an example.

## What the interviewer evaluates

Recognize accidental indirection and choose a simpler design with a concrete example.

## Explanation in Arabic

Pattern تبقى عبء لما تضيف classes/wrappers من غير variation أو boundary حقيقية. مثال screen صغيرة بتقرأ settings: `ViewModel -> GetSettingsUseCase -> SettingsFacade -> SettingsRepository -> SettingsAdapter -> DAO` وكل واحدة بس تنادي اللي بعدها. ده يصعّب debug ويكبر DI graph، ومش بيعزل تغيّر مستقل. احتفظ بـViewModel + Repository contract واضح، واستخرج use case لما rule معقدة/reused. برضه مفيش داعي Factory لبناء data class بسيطة أو Observer custom بدل StateFlow موجودة. قِس changed-file count ووقت فهم flow.

## Why it matters and how it works

Patterns encode trade-offs; without the forces they solve, they add navigation and maintenance cost. A simpler direct collaboration can be more testable and readable. Keep correctness boundaries even when removing ceremony.

## Worked example

Concrete simplification: replace a one-line `GetThemeUseCase` and `ThemeFacade` with `SettingsViewModel(settingsRepository)` if they add no policy. Repository still owns DataStore access and main-safety; ViewModel produces UI state. This removes indirection without sending I/O into Compose.

## Practical walkthrough

لو `GetThemeUseCase` بس بتنادي `settingsRepository.theme()` و`ThemeFacade` بتنادي use case من غير policy، caller بيمشي خلال classes كتير عشان function واحدة؛ stack traces وتعديل API يبقوا أصعب. ممكن ViewModel تعتمد repository مباشرة مع interface واضحة؛ لو use case مستقبلًا تجمع مصادر/validation أو تتكرر في screens كثيرة، ارجعها وقتها. نفس الشيء Factory لا معنى لها لو provider واحد وconstructor مباشر. احذف طبقة بعد ما تثبت إنها لا تملك invariant ولا test seam ولا variation حقيقية، مع الحفاظ على boundaries مهمة زي data source vs UI. قِس تبسيط call graph وراجع tests.

## Trade-offs and decision criteria

Too little structure can leak DTOs or duplicate business rules. Too much structure makes local changes touch many wrappers. Choose a seam when independent change, substitution or reuse is demonstrated. Keep a path to extract later.

## Failure modes

A new setting requires editing six forwarding interfaces and generated bindings but no new behavior. Refactor to direct repository use. Conversely, removing the repository and calling DataStore from UI would lose ownership; simplify only ceremonial layers.

## Production perspective

A small settings feature ships with two clear classes and behavior tests. When profile and checkout later share a policy, team extracts one focused use case; they do not prebuild a generic pattern framework.

## Interview answer — short

Patterns become unnecessary indirection when wrappers merely forward calls and protect no real variation. I simplify to clear UI/data ownership, then add a focused pattern only when change pressure justifies it.

## Interview answer — structured

I look for a concrete benefit from each layer. If `GetSettingsUseCase`, `SettingsFacade` and `SettingsAdapter` all forward one call, they add navigation, DI wiring and tests without isolating an independent change. I would let the ViewModel use a repository that owns storage and main safety. If shared business policy later emerges, I can extract a use case. Simplification should remove ceremony, not collapse data access into Compose or erase error handling.

## Interview answer — deep senior

A pattern is a response to a design force. A Factory is useful when construction varies, an Adapter when interfaces differ, and a Facade when a subsystem is genuinely complex. Applying all three to a two-field settings model may obscure what happens rather than help. I review call chains, changed-file count and whether each wrapper has distinct behavior or ownership. If several merely delegate, I remove them in small tested steps, retaining a repository boundary for data consistency and a ViewModel for UI state. I also watch the opposite extreme: direct vendor SDK calls from UI may appear simpler now but cause repeated change and lifecycle bugs later. The right design is the least structure that keeps important changes local and contracts truthful.

I ask what decision each layer owns. If `GetThemeUseCase` only forwards to `SettingsRepository` and `ThemeFacade` only forwards again, neither adds a policy, invariant, or useful test seam. I would let the ViewModel depend on the repository and keep the data boundary intact. That reduces navigation through files and makes failures easier to trace. I would retain a use case when it combines sources, applies shared business rules, or is reused across multiple screens; the choice is about responsibility, not a prohibition on layers. The same principle applies to a Factory for one fixed constructor or an Adapter around an identical interface. I remove ceremonial indirection and add it back when change pressure justifies it.

## How to answer in the interview

- **Why:** Indirection costs reading, debugging and API churn.
- **How:** Walk a theme call graph and remove pass-through layers.
- **Trade-off:** Keep a layer when it owns reuse, policy, validation or boundary.
- **Failure case:** Pattern names hide no-op forwarding and obscure errors.
- **Production solution:** Simplify call sites, preserve data boundary and verify tests.

## Deep-dive talking points

Trace a six-wrapper chain, identify pass-through layers, retain useful repository ownership and extraction trigger.

## Follow-up questions

- [PAT-01](../pat-01/): What makes a pattern useful? **Answer:** a recurring problem and trade-off it actually addresses.
- [SOL-19](../sol-19/): When accept duplication? **Answer:** when a premature shared abstraction would couple independently changing behavior.

## Self-check rubric

Remove two ceremonial wrappers from a sample chain while preserving data/UI correctness boundaries.

## References and reviewed-on date

- [Android domain layer](https://developer.android.com/topic/architecture/domain-layer) — optional use cases.
- [GoF pattern catalog](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — original pattern context.

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.

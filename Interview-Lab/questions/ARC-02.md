---
id: "ARC-02"
question: "Explain Presentation, Domain, and Data layers."
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "A"
phase: 2
priority: "P1"
order: 147
editorial_status: "reviewed"
---

# ARC-02

## Original interview question

Explain Presentation, Domain, and Data layers.

## What the interviewer evaluates

Assign responsibilities to UI, optional domain, and data without confusing policy with rendering.

## Explanation in Arabic

Presentation بتاخد data وتحوّلها لـUI state، تستقبل user events، وتتعامل مع lifecycle/navigation. Domain اختيارية للـbusiness operations المشتركة أو المعقدة، زي حساب eligibility أو تنسيق workflow، من غير معرفة Compose أو DTO. Data layer فيها repositories، local/remote data sources، caching، conflict resolution، ومصدر الحقيقة. ViewModel مش مكان network mapping أو SQL؛ وRepository مش مكان snackbar text. الحدود تبقى واضحة في types: DTO عند transport، entity عند persistence، domain model في policy، UI model عند الشاشة.

## Practical walkthrough

Presentation يعرض UiState ويستقبل events، Domain يملك rule مستقل عن Android إن كان مفيدًا، Data ينسق Room/Retrofit/cache. مثال account balance: UI لا تقرر أن timeout يعني declined؛ domain يعبّر عن Unknown، data تطلب status من backend. لا تخلط DTO مع UiState لأن API field قد يتغير. اختبر كل طبقة حسب contract.

## Why it matters and how it works

Android guidance recommends a UI layer and data layer, with a domain layer when reuse or complexity calls for it. UI state holders produce screen state and delegate business operations. Data repositories coordinate data sources, own consistency decisions, and expose app data. Domain use cases can combine or transform repository outputs without adopting UI/framework types.

## Worked example

Conceptual flow: `LoginScreen` emits `Submit(credentials)` to `LoginViewModel`; ViewModel invokes `SignInUseCase` if the workflow is shared; use case calls `AuthRepository`; repository maps Retrofit response into a domain session and persists it. ViewModel maps domain outcome to `LoginUiState`. No layer promises server trust by itself.

## Trade-offs and decision criteria

A separate domain layer adds types, mapping, and navigation overhead. Keep a simple one-screen feature in UI/data if no reusable policy exists. Put rules at the lowest layer that owns them; avoid “use case” wrappers that merely delegate one method with no value.

## Failure modes

If Presentation receives a raw `HttpException`, it may branch on transport status and become coupled to Retrofit. If Domain imports `android.app.Activity`, its tests and reuse suffer. Map at boundaries and keep lifecycle-specific work in UI.

## Production perspective

An offline account screen observes repository data backed by Room; domain computes account eligibility reused by checkout and settings; ViewModels render different states. Network failure is reported without replacing valid cached data with a false empty screen.

## Interview answer — short

Presentation produces UI state and handles UI events. Data owns repositories and data sources. An optional domain layer holds reusable or complex business operations. I keep transport and persistence models from leaking into the screen.

## Interview answer — structured

I would draw the path from a user action to visible state. The screen sends an event to a ViewModel, which manages screen state and delegates business work. A domain use case belongs between UI and data when it expresses reusable policy or coordinates multiple repositories. The repository owns network, database, caching, and mapping into app data. This division helps test UI behavior separately from data consistency. I do not create an empty domain layer just to satisfy a diagram. For example, locale-specific amount formatting is a screen concern, transfer eligibility is a product rule, and cache reconciliation belongs with the repository. If a ViewModel imports a DTO or a use case imports an Activity, I treat that as a boundary smell and ask what change would force a rewrite.

## Interview answer — deep senior

The boundaries are about change and ownership. Presentation knows resources, navigation and lifecycle; it should not decide database truth or parse HTTP payloads. Data knows transport, persistence, refresh policy, and source of truth. Domain, when present, expresses application rules that can be tested independently of Android and reused across screens. A repository might expose a Flow of domain data while reconciling local and remote sources; ViewModel turns that into loading/content/error UI state. I inspect actual imports and model types to catch leaks. I also ask where failures are mapped: transport errors can become typed domain errors, then actionable UI messages. This layered design should clarify product behavior, not multiply trivial passthrough classes. I also distinguish the classic Clean Architecture interpretation from Android guidance: Android calls domain optional and allows UI to depend on the data layer directly. The important contract is still that screen state is produced from stable app data and data sources are hidden. I test a repository using representative server/database cases and a ViewModel using a fake repository. A payment status does not become authoritative because it passed through a domain class; backend confirmation remains necessary.

## How to answer in the interview

- **Why:** layers assign decision ownership.
- **How:** trace event through UI, policy and adapters.
- **Trade-off:** isolation versus mapping cost.
- **Failure case:** DTO leaks directly into screen.
- **Production solution:** contract tests per boundary.

## Deep-dive talking points

Compare a screen event, reusable rule, and repository refresh. Identify where locale formatting, HTTP mapping, conflict resolution, and lifecycle state belong; test each boundary separately.

## Follow-up questions

- [ARC-05](../arc-05/): Where should filtering for display live? **Answer:** UI-specific sorting/labels in Presentation; reusable business eligibility in Domain/Data.
- [ARC-06](../arc-06/): Where does a Room entity live? **Answer:** in Data, close to persistence.

## Self-check rubric

Can you assign a ViewModel, use case, repository, DTO, and Room entity without mixing responsibilities? Explain one business rule and one rendering rule.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — layer responsibilities.
- [Android domain layer](https://developer.android.com/topic/architecture/domain-layer) — optional domain use cases.

Technically reviewed against the linked official Android architecture guidance on 2026-10-11. Conceptual flows and snippets are not device-tested.

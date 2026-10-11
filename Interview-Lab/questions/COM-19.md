---
id: "COM-19"
question: "How do you implement a reusable design system and themes?"
topic: "Jetpack Compose"
code: "COM"
group: "B"
phase: 3
priority: "P1"
order: 248
editorial_status: "reviewed"
---

# COM-19

## Original interview question

How do you implement a reusable design system and themes?

## What the interviewer evaluates

- Build tokens and semantic components rather than copy-pasted styling.
- Support dynamic color, typography, shape, dark mode and accessibility.
- Balance central consistency with feature autonomy and versioning.

## Explanation in Arabic

ابدأ بـdesign tokens دلالية: ألوان roles (surface, primary, error)، typography، spacing، shapes، ثم Compose theme توفرها عبر MaterialTheme أو CompositionLocals بحذر. ابنِ components مثل AppButton وPriceCard بعقود state/events واضحة و`Modifier` من caller، بدل نسخ style في كل feature. اختبر light/dark، dynamic color عندما المنتج يسمح، RTL، font scaling وcontrast. لا تجعل design-system module يعتمد على feature business types؛ استخدم UI primitives. قد تحتاج versioning ومراجعة migration إذا التغييرات تكسر screens.

## Why it matters and how it works

A theme supplies ambient design values to a composition. Semantic roles let UI adapt without hard-coding a color for each screen. Reusable components wrap consistent behavior, semantics and styling while accepting caller layout decisions. An API that exposes domain entities directly creates dependency cycles and makes the design system hard to evolve.

## Worked example

An `AppPrimaryButton(text, enabled, loading, onClick, modifier)` applies theme colors, minimum touch target and loading semantics. Checkout and profile features reuse it without importing each other's models. A theme preview renders the button in light, dark, large text and Arabic RTL; a screenshot or semantic test checks regression.

## Trade-offs and decision criteria

Centralizing components reduces drift but can become a bottleneck if every feature variant is forced into one giant API. Prefer a small stable core and deliberate extension points. Dynamic color improves platform fit but may conflict with brand contrast; validate both. CompositionLocals simplify access to tokens but hide dependencies if overused for behavior.

## Failure modes

A screen hard-codes a light color and fails dark mode. Component ignores caller Modifier, so sizing and test tags break. A shared button has 20 Boolean flags for every team's exception. A design-system release changes padding globally without visual regression coverage. Text truncates at large font scale.

## Production perspective

Maintain documented token and component contracts, a preview/gallery matrix, screenshot/semantics tests, and accessibility review. Version changes with migration notes and measure affected screens before broad release.

## Interview answer — short

“I centralize semantic tokens and small accessible components, expose theme variants and caller modifiers, then verify dark mode, RTL, large text and visual regressions.”

## Interview answer — structured

“I define a theme from semantic color, type, shape and spacing roles, then build reusable components whose APIs express UI state and events rather than feature-specific business objects. Each component respects the caller's Modifier and provides accessible behavior. I preview and test light/dark, RTL and font scaling. I avoid one giant component with flags for every exception and version the shared API when changes affect many features.”

## Interview answer — deep senior

“A design system is a contract between visual language and implementation. I start with semantic tokens—surface, content, error, emphasis, typography scale, spacing and shape—so a dark theme or dynamic color choice can change values without rewriting screens. Compose theme and carefully scoped CompositionLocals expose those tokens. Components then encode repeated behavior as well as appearance: an AppButton accepts enabled/loading state, click callback and caller Modifier, owns a minimum interactive size and semantics, and does not know checkout domain models. I keep the shared module dependency-light to avoid feature cycles. The hard part is governance: if every feature adds a Boolean to a universal component, the API becomes unreadable, so I keep a stable primitive core and allow focused variants. I test a gallery across light/dark, Arabic RTL, large text and contrast, and use screenshot plus semantic tests to catch global regressions. A token change is a product migration with review and release notes, not a trivial refactor. I also measure whether abstractions complicate performance on complex screens.”

## Deep-dive talking points

Discuss semantic tokens, theme propagation, component API, caller Modifier, RTL/accessibility matrix, and governance.

## Follow-up questions

- Why use semantic colors instead of hex values in features? **Answer:** roles can adapt across themes while preserving intended meaning.
- Should design-system components depend on checkout models? **Answer:** generally no; keep them reusable UI contracts.
- What validates a global token change? **Answer:** previews, visual/semantic regression checks and affected-screen review.

## Self-check rubric

Name tokens and a component contract, cover accessibility and theme variants, and explain versioning.

## References and reviewed-on date

- [Theming in Compose](https://developer.android.com/develop/ui/compose/designsystems/material3) — Material theme design.
- [Accessibility in Compose](https://developer.android.com/develop/ui/compose/accessibility) — semantics and inclusive UI.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Governance choices are engineering recommendations.
How do you implement a reusable design system and themes?

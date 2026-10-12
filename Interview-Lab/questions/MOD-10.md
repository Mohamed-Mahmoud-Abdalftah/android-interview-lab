---
id: "MOD-10"
question: "How do navigation contracts work across modules?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 363
editorial_status: "reviewed"
---

# MOD-10

## Original interview question

How do navigation contracts work across modules?

## What the interviewer evaluates

- Separate destination identity/API from screen implementation.
- Explain app registration, deep links, arguments and versioning.
- Preserve module dependency direction and restoration.

## Explanation in Arabic

Feature يمكنها إعلان public destination contract مثل route/type ومعلمات صغيرة (`orderId`) في API module، بينما implementation تعرف Composable أو Fragment. app shell تجمع graph وتربط contract بالتنفيذ؛ feature أخرى تطلب navigation للـcontract دون استيراد screen class. للـdeep link اختبر validation/auth وفشل ID مفقود؛ لا تمرر domain object كامل. العقد نفسه public API يحتاج versioning إذا تغير argument أو route. في dynamic feature يجب التأكد من install قبل فتح destination.

## Why it matters and how it works

Navigation is a cross-feature capability but destination implementations should remain encapsulated. A route contract can express stable identifiers and expected arguments, while an app graph or registry contributes actual destination code. The back stack and saved state can restore small arguments after eligible process recreation; the destination reloads data from a repository.

## Worked example

Orders exposes `OrderDetailsDestination(orderId)` as a small contract. A notification or Checkout requests it through an app navigator. The app registers the Orders UI destination, validates the route parameter and resolves authorization in the Orders ViewModel. A deep link into a deleted order renders Not Found instead of crashing.

## Trade-offs and decision criteria

Central graph registration is explicit but can become a large file; feature-owned graph contributions scale but need careful API and dependency arrangement. String routes are flexible but typo-prone; typed route APIs depend on Navigation version. A navigation facade simplifies testing but should not become an opaque global service locator.

## Failure modes

A feature imports another's screen implementation. A route contains a large Parcelable and fails after process death. Deep-link arguments bypass authorization. A dynamic feature route is opened before installation. A rename silently breaks notifications or external links.

## Production perspective

Version and test public routes, deep links, argument parsing, app graph assembly and back-stack restoration. Monitor navigation failures and provide a safe fallback for missing or unauthorized destinations.

## Interview answer — short

“Expose a small stable destination contract, let app or graph composition bind it to feature UI, and pass validated IDs rather than implementation classes or large objects.”

## Interview answer — structured

“I keep the destination's public identity separate from its Composable implementation. Orders may expose a typed route with `orderId`; checkout asks the app navigator to open it, and app graph registration maps it to Orders UI. The destination validates arguments and authorization and reloads data. I test deep links, process recreation and route compatibility. For an on-demand feature, installation is part of the navigation precondition.”

## Interview answer — deep senior

“A navigation contract is a public API between feature boundaries. It should describe a destination and minimal arguments, not expose the other feature's screen class or ViewModel. I might place `OrderDetails(orderId)` in a small Orders API module and let the app composition root register the actual Orders UI. Checkout or a notification can request that contract without knowing how Orders renders. The route uses a stable identifier so the back stack and deep link can be restored; the Orders owner reloads data and enforces authorization, because a crafted link can supply any ID. I consider route changes like API changes: renaming a path or parameter can break notifications, bookmarks or other modules, so compatibility and tests matter. A graph-contribution mechanism can avoid a giant app file, but it must keep dependency direction visible. With dynamic delivery, a navigator first resolves installation state and only then opens the destination. I test the assembled graph, deep-link parsing, missing/deleted IDs, back-stack behavior and eligible process restoration.”

## Deep-dive talking points

Cover route API, app mapping, typed versus string routes, deep-link security, versioning and dynamic install.

## Follow-up questions

- Should a route carry an entire Order entity? **Answer:** generally no; pass a stable ID and reload it.
- Who enforces deep-link authorization? **Answer:** the destination/domain boundary, not trust in route formatting.
- What changes for a dynamic feature? **Answer:** install availability must be checked before entering its code.

## Self-check rubric

Define a destination contract, show graph mapping, and cover deep link, restoration and install tests.

## References and reviewed-on date

- [Navigation with Compose](https://developer.android.com/develop/ui/compose/navigation) — routes and arguments.
- [Android modularization patterns](https://developer.android.com/topic/modularization/patterns) — graph composition.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The navigation facade is a design option.

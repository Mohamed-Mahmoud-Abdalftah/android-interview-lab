---
id: "AND-15"
question: "Compare Activity, Fragment, Compose navigation, and deep links."
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "B"
phase: 1
priority: "P1"
order: 45
editorial_status: "reviewed"
---

# AND-15

## Original interview question

Compare Activity, Fragment, Compose navigation, and deep links.

## What the interviewer evaluates

- Separate platform component lifecycle from in-app destinations and external entry routes.
- Explain back stack, saved state, arguments, and process restoration across each choice.
- Recognize that a deep link must be validated and authorized regardless of UI toolkit.

## Explanation in Arabic

`Activity` مكوّن Android مستقل يقدر النظام يبدأه وله task/back stack وlifecycle. `Fragment` جزء واجهة تديره Activity وله lifecycle للـFragment وآخر للـview؛ مفيد لشاشات أو أجزاء داخل Activity. `Navigation Compose` يمثل destinations داخل Compose و`NavHost` بيتحكم في مسار التنقل وحالة الـback stack، لكنه مش بديل عن Activity كنقطة دخول للنظام. `deep link` عنوان أو Intent بيبدأ مسار من خارج التطبيق أو داخله؛ لازم تتحقق من بياناته ومن صلاحية المستخدم قبل عرض محتوى حساس. القرار يتحدد بحدود النظام والتعقيد الموجود، مش بقاعدة إن تطبيق Compose لازم يكون Activity واحدة دائمًا.

## Why it matters and how it works

An Activity is a platform component with its own task semantics and lifecycle. A Fragment is hosted and managed by an Activity; its view can be destroyed independently of the Fragment. Compose Navigation models destinations as entries in an in-app back stack, with arguments and scoped state. A deep link is an address into a destination, potentially delivered at cold start with a new process. Each layer must cooperate on restoration: the system recreates components and saved state, while repositories reload durable business data.

## Worked example

A commerce app has one host Activity with Compose destinations for catalog, product, and cart. A verified HTTPS App Link opens `/product/42`; the Activity parses a stable product ID, Navigation creates the destination, and the ViewModel loads the product from a repository. If the user is unauthenticated for a private order route, navigation goes through sign-in and resumes only after authorization. This is an architecture sketch; exact navigation code depends on library version and existing app structure.

## Trade-offs and decision criteria

Multiple Activities can express platform tasks or separate surfaces, but cross-Activity state and transitions take more coordination. Fragments remain appropriate for existing View-based apps and some hosted integrations; observe their view lifecycle correctly. Navigation Compose keeps Compose destination behavior together but requires deliberate argument and state design. Deep links improve reachability while expanding the input surface; prefer stable IDs over serialized objects in URLs.

## Failure modes

Treating a Fragment's lifecycle as its view lifecycle leaks bindings. Passing a mutable object through a navigation route creates stale or oversized state. A deep link may arrive with no prior in-memory session and crash a destination that assumes earlier screens ran. Back-stack behavior can differ after an external launch. Test cold links, authenticated and unauthenticated cases, rotation, process recreation, and Up versus Back navigation.

## Production perspective

Define a route contract per destination, sanitize untrusted URI parameters, and reconstruct screen state from stable IDs. Keep authorization in a domain or data boundary, not only in navigation guards. Record link-routing failures without sensitive query data. Add UI tests for task entry from notification and browser as well as ordinary in-app movement.

## Interview answer — short

“Activities are Android components, Fragments are hosted UI components, Compose Navigation manages in-app destinations, and deep links are entry routes. They solve different layers of navigation, so I design their back stack and restoration together.”

## Interview answer — structured

“An Activity is a platform entry point and task participant. A Fragment lives in an Activity and has a separate view lifecycle. Compose Navigation offers a destination back stack for Compose UI. A deep link can target a destination from outside the app, including on a cold start. I pass stable IDs, restore screen data through ViewModels and repositories, and check authentication and authorization on every external entry. I choose a host structure based on existing UI architecture and task requirements rather than assuming one universal pattern. These concepts operate at different layers: Activity and Fragment are platform UI containers, Compose Navigation manages destinations within an app, and a deep link is an external entry address. I pass stable IDs rather than large mutable objects as route arguments, then reload authorized state. Cold-start links must work without previous screens or singleton state.”
## Interview answer — deep senior

“I distinguish platform navigation from UI navigation. Android owns Activity launch and task behavior; a FragmentManager or Compose NavHost owns nested destinations. Each has independent state and lifecycle details. For a product deep link, I validate the URI, derive a stable ID, construct the appropriate back stack, and load durable state instead of relying on a previous screen's object. Process death and external launch are normal paths. Security checks live below routing because a crafted deep link or internal call must not bypass authorization. I test Back and Up after cold launch, rotation, restored state, and unauthenticated entry. In a legacy View app, Fragments may be the cleanest choice; in a Compose app, Navigation Compose fits destination state, while additional Activities remain valid for platform-level task boundaries. An Activity has task/back-stack semantics defined by Android; a Fragment has a separate view lifecycle inside its host; Compose Navigation manages destination entries and scoped state. A deep link may target any of these flows from outside, including when the process is dead, so it cannot assume a prior login screen ran. I validate scheme/host/path and ID format, authenticate the user and ask the backend to authorize the referenced resource. Navigation arguments carry a stable key rather than a Parcelable graph that becomes stale or oversized. I test Back behavior after notification and cold-link entry, as well as rotation and process restoration. The UI pattern does not replace durable business state.”
## Deep-dive talking points

Discuss task stack versus NavHost stack, Fragment view lifecycle, deep-link trust boundaries, state restoration, and stable route arguments.

## Follow-up questions

- Does Navigation Compose replace the Activity lifecycle? **Answer:** no; destinations run inside a host Activity and must work with its lifecycle and saved state.
- Why pass an ID rather than a full product object? **Answer:** it gives a compact, restorable route and lets the repository load current data after process death.
- Is a verified App Link sufficient authorization? **Answer:** no; link verification establishes domain association, while the app must still authenticate and authorize access to private data.

## Self-check rubric

Define all four layers; describe a cold deep-link launch, back stack and state restoration; give a security check and a Fragment view-lifecycle pitfall.

## References and reviewed-on date

- [Guide to app architecture](https://developer.android.com/topic/architecture) — UI, state, and data boundaries.
- [Navigation with Compose](https://developer.android.com/develop/ui/compose/navigation) — Compose destinations and route arguments.
- [Create deep links](https://developer.android.com/training/app-links/deep-linking) — external navigation entry.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The commerce flow is illustrative.

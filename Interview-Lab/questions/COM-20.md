---
id: "COM-20"
question: "How do you handle previews, permissions, and navigation?"
topic: "Jetpack Compose"
code: "COM"
group: "B"
phase: 3
priority: "P1"
order: 249
editorial_status: "reviewed"
---

# COM-20

## Original interview question

How do you handle previews, permissions, and navigation?

## What the interviewer evaluates

- Keep previewable UI independent of runtime-only services.
- Use Activity Result permission contracts with lifecycle-aware ownership.
- Navigate with small validated arguments and test denial/restoration paths.

## Explanation in Arabic

خلّي Screen composable تأخذ state/callbacks فتقدر تعرض preview لحالات loading/error/permission بدون Hilt أو Activity حقيقية. Route تربط ViewModel وNavController وpermission launcher عبر Activity Result API، وتعرض rationale عندما يلزم وتتعامل مع رفض أو تغيير الإذن من Settings. لا تطلب permission أثناء كل recomposition؛ الطلب ينطلق من user action أو effect مضبوط. Navigation تمرر ID صغير أو route typed حسب API المستخدمة، وتعيد تحميل data من repository؛ لا ترسل object كبير أو sensitive في route.

## Why it matters and how it works

Previews render composables under limited tooling context, so runtime dependencies and side effects make them brittle. Permission requests are asynchronous platform interactions tied to an Activity/registry owner; the user can deny or revoke later. A navigation back stack stores destination and arguments, and process restoration works best with small stable identifiers rather than in-memory object references.

## Worked example

A photo upload screen preview receives `PermissionRequired` and a fake `onGrant` callback. At runtime the route registers a permission launcher, asks for image access only after the user chooses Upload, and handles denial with a non-blocking explanation and settings path when appropriate. On grant, the ViewModel receives a content URI and copies or reads it under current access rules; navigation to editor uses a persisted draft ID.

## Trade-offs and decision criteria

Keeping runtime wiring in a route adds a layer but enables useful previews and isolated UI tests. Request timing should follow user intent and platform guidance, not a generic startup prompt. A content URI may have temporary access; persist or copy data when a workflow must survive. Navigation APIs vary by library version; preserve validated small arguments.

## Failure modes

A preview crashes because it invokes `hiltViewModel()` or accesses unavailable services. A permission dialog reopens on recomposition. UI assumes permission remains granted forever. A large Parcelable route argument breaks after process death or exceeds saved-state limits. Denial leaves the user at a dead end.

## Production perspective

Maintain previews for key UI states, run device tests for grant/deny/revoke and process recreation, and validate navigation/deep links. Include accessibility labels and alternate actions when permission is denied.

## Interview answer — short

“I preview a stateless Screen with sample states, handle runtime permissions in an owner using Activity Result APIs, and navigate with small validated identifiers.”

## Interview answer — structured

“I separate the reusable Screen from its Route so previews can inject loading, error and permission states without Hilt or navigation setup. The Route owns permission launchers and NavController; it requests access from a user action, handles denial and later revocation, and sends results to the ViewModel. Navigation passes a small ID and reloads data, which is safer for recreation than passing a large object. I test deep links, grant and denial on device.”

## Interview answer — deep senior

“I use previews to exercise rendering contracts, not to simulate the whole Android runtime. A Screen takes explicit `UiState` and callbacks, so I can preview loading, permission-required, denied and ready states. A Route connects that screen to ViewModel, navigation and the Activity Result registry. Permission work must reflect platform state: I request only when the user reaches the capability, show rationale when appropriate, handle denial without trapping them, and recheck when returning from Settings because grants can change. A request launched from a composable body would repeat under recomposition, so it belongs to an event or carefully keyed effect. For navigation I pass a stable ID or supported typed route and load the entity from a repository; large mutable objects in arguments are fragile under process death. If the workflow depends on a selected content URI, I account for the grant's lifetime and persist or copy content as appropriate. I verify previews for visual states, Compose tests for callbacks, and device tests for permission and back-stack restoration. Each layer proves a different claim.”

## Deep-dive talking points

Discuss stateless previews, Activity Result ownership, rationale/denial, URI grants, route arguments, and restoration.

## Follow-up questions

- Why not call a launcher during every composition? **Answer:** rendering can repeat and show duplicate requests.
- Are permission grants permanent? **Answer:** no; users or the system can revoke access, so check at use time.
- Why pass an ID rather than an entity through navigation? **Answer:** it is smaller and can be reloaded after recreation.

## Self-check rubric

Show a preview contract, permission event flow, denial path, and process-safe navigation argument.

## References and reviewed-on date

- [Permissions in Compose](https://developer.android.com/training/permissions/requesting) — runtime request and rationale.
- [Navigation with Compose](https://developer.android.com/develop/ui/compose/navigation) — arguments and navigation.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Exact permission contract depends on the capability and API level.
How do you handle previews, permissions, and navigation?

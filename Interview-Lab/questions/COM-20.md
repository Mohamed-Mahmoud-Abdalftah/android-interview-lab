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

## Practical walkthrough

Preview ما عندهاش Activity Result launcher حقيقي؛ اعرض Screen بحالة fake، وخلي Route هي اللي تسجل launcher وتقرر متى تطلب permission. طلبها يكون بسبب user action، وبعدين تعامل مع grant/deny/revoke، مش كل recomposition. عند navigation مرر draft ID صغير، لا تمرر Bitmap أو object حساس. لو المستخدم رفض location، البحث اليدوي لازم يفضل شغال؛ وإلا الإذن بقى باب مقفول بلا داعٍ. قبل كل استخدام للموقع راجع grant الحالية، وللصور استخدم Photo Picker بدل طلب access واسع إذا كان مناسب.

## Why it matters and how it works

Previews render composables under limited tooling context, so runtime dependencies and side effects make them brittle. Permission requests are asynchronous platform interactions tied to an Activity/registry owner; the user can deny or revoke later. A navigation back stack stores destination and arguments, and process restoration works best with small stable identifiers rather than in-memory object references.

## Worked example

A nearby-places screen preview receives `PermissionRequired` and a fake `onRequestLocation` callback. At runtime its route requests coarse location only after the user taps “Use my location”; denial leaves manual place search available. On grant, the ViewModel checks the permission again before using the location provider. Navigation to place detail passes a persisted place ID rather than a location object. For picking an existing photo instead, Android Photo Picker usually avoids a broad media permission request.

### Compose/Kotlin walkthrough

```kotlin
// Route owns platform launcher; Screen only emits the user's intent.
@Composable
fun NearbyRoute(viewModel: NearbyViewModel, state: NearbyState) {
    val launcher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted -> viewModel.onPermissionResult(granted) }
    NearbyScreen(
        state = state,
        onRequestLocation = {
            launcher.launch(Manifest.permission.ACCESS_COARSE_LOCATION)
        },
        onManualSearch = viewModel::searchManually
    )
}
// Assumes manifest declares ACCESS_COARSE_LOCATION. NearbyViewModel/State/Screen
// are app-defined; check the grant again before reading location.
// Imports: androidx.activity.compose.rememberLauncherForActivityResult,
// androidx.activity.result.contract.ActivityResultContracts, android.Manifest.
// @Preview can render NearbyScreen(PermissionRequired, {}, {}).
```

## Trade-offs and decision criteria

Keeping runtime wiring in a route adds a layer but enables useful previews and isolated UI tests. Request timing should follow user intent and platform guidance, not a generic startup prompt. A content URI may have temporary access; persist or copy data when a workflow must survive. Navigation APIs vary by library version; preserve validated small arguments.

## Failure modes

A preview crashes because it invokes `hiltViewModel()` or accesses unavailable services. A permission dialog reopens on recomposition. UI assumes permission remains granted forever. A large Parcelable route argument breaks after process death or exceeds saved-state limits. Denial leaves the user at a dead end.

## Production perspective

Maintain previews for key UI states, run device tests for grant/deny/revoke and process recreation, and validate navigation/deep links. Include accessibility labels and alternate actions when permission is denied.

## Interview answer — short

“I preview a stateless Screen with sample states, handle runtime permissions in an owner using Activity Result APIs, and navigate with small validated identifiers. Preview the pure Screen; keep permission launch and navigation in the Route.”

## Interview answer — structured

“I separate the reusable Screen from its Route so previews can inject loading, error and permission states without Hilt or navigation setup. The Route owns permission launchers and NavController; it requests access from a user action, handles denial and later revocation, and sends results to the ViewModel. Navigation passes a small ID and reloads data, which is safer for recreation than passing a large object. I test deep links, grant and denial on device. For nearby places, the Route requests coarse location only after the user asks and keeps manual search available.”

## Interview answer — deep senior

“I use previews to exercise rendering contracts, not to simulate the whole Android runtime. A Screen takes explicit `UiState` and callbacks, so I can preview loading, permission-required, denied and ready states. A Route connects that screen to ViewModel, navigation and the Activity Result registry. Permission work must reflect platform state: I request only when the user reaches the capability, show rationale when appropriate, handle denial without trapping them, and recheck when returning from Settings because grants can change. A request launched from a composable body would repeat under recomposition, so it belongs to an event or carefully keyed effect. For navigation I pass a stable ID or supported typed route and load the entity from a repository; large mutable objects in arguments are fragile under process death. If the feature picks existing photos rather than reading location, I use the Photo Picker contract where suitable and account for the selected URI grant's lifetime. I verify previews for visual states, Compose tests for callbacks, and device tests for permission and back-stack restoration. Each layer proves a different claim. A preview cannot prove denial and Settings-return behavior, so I cover those paths on an emulator.”

## How to answer in the interview

- **Why:** platform permission state is asynchronous and revocable.
- **How:** separate previewable Screen from launcher-owning Route.
- **Trade-off:** add integration tests for the Activity path.
- **Failure case:** requesting on every recomposition loops the dialog.
- **Production solution:** handle denial, Settings return, and durable draft IDs.

## Deep-dive talking points

Discuss stateless previews, Activity Result ownership, location rationale/denial, Photo Picker as a separate contract, route arguments, and restoration.

## Follow-up questions

- Why not call a launcher during every composition? **Answer:** rendering can repeat and show duplicate requests.
- Are permission grants permanent? **Answer:** no; users or the system can revoke access, so check at use time.
- Why pass an ID rather than an entity through navigation? **Answer:** it is smaller and can be reloaded after recreation.

## Self-check rubric

Show a preview contract, permission event flow, denial path, and process-safe navigation argument.

## References and reviewed-on date

- [Permissions in Compose](https://developer.android.com/training/permissions/requesting) — runtime request and rationale.
- [Navigation with Compose](https://developer.android.com/develop/ui/compose/navigation) — arguments and navigation.
- [Android Photo Picker](https://developer.android.com/training/data-storage/shared/photo-picker) — selected-media access without a broad library permission.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Exact permission contract depends on the capability and API level.

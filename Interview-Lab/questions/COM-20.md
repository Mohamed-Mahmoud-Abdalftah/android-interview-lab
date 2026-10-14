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

كيفية التعامل الاحترافي مع المعاينات (Previews)، الأذونات (Permissions)، والتنقل (Navigation) في Jetpack Compose:

1. المعاينات (Compose Previews):
   - استخدام الـ **Multipreview Annotations** لإنشاء وسم مخصص مثل `@DevicePreviews` يجمع بين:
     * وضع النهار ووضع الليل (Light / Dark).
     * أحجام شاشات متعددة (Phone, Tablet, Foldable).
     * أحجام خطوط وصول متعددة (Font Scale 1.5x للتحقق من إمكانية الوصول Accessibility).
   - استخدام `PreviewParameterProvider` لتمرير حالات بيانات مختلفة (Loading, Error, Success) إلى نفس دالة المعاينة.

2. التعامل مع الأذونات (Runtime Permissions):
   - استخدام مكتبة **Accompanist Permissions** أو الـ `rememberLauncherForActivityResult` المدمج مع `ActivityResultContracts.RequestPermission()`.
   - التعامل مع تدفق الأذونات بثلاث حالات:
     * إذن ممنوح (`PermissionStatus.Granted`): عرض الميزة فوراً.
     * إذن مرفوض مع مبرر (`shouldShowRationale`): عرض شاشة تشرح للمستخدم لماذا يحتاج التطبيق هذا الإذن.
     * إذن مرفوض نهائياً: توجيه المستخدم لفتح إعدادات النظام (`Settings`).

3. التنقل (Navigation):
   - استخدام **Type-Safe Navigation** المتاح في Jetpack Navigation 2.8+ المبني على Kotlin Serialization بدلاً من الـ String URLs القديمة والمعرضة للأخطاء الإملائية.

## Practical walkthrough

إعداد Multipreview احترافي واستخدام Type-Safe Navigation وطلب الأذونات:
```kotlin
// 1. Multipreview Annotation لاختبار كل حالات الشاشة بضغطة زر:
@Retention(AnnotationRetention.BINARY)
@Target(AnnotationTarget.FUNCTION)
@Preview(name = "Light Phone", showBackground = true)
@Preview(name = "Dark Phone", uiMode = Configuration.UI_MODE_NIGHT_YES, showBackground = true)
@Preview(name = "Large Font", fontScale = 1.5f, showBackground = true)
annotation class DevicePreviews

// 2. استخدام Type-Safe Navigation مع Kotlinx Serialization (Navigation 2.8+):
import kotlinx.serialization.Serializable

@Serializable
data object HomeDestination

@Serializable
data class ProfileDestination(val userId: String)

fun NavGraphBuilder.appNavGraph(navController: NavController) {
    composable<HomeDestination> {
        HomeScreen(onProfileClick = { id -> navController.navigate(ProfileDestination(id)) })
    }
    composable<ProfileDestination> {
        ProfileRoute()
    }
}
```

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

Handle Previews using custom Multipreview annotations and `PreviewParameterProvider` for multi-state rendering. Manage runtime permissions cleanly using `rememberLauncherForActivityResult` with rationale handling. Implement navigation using modern Type-Safe Navigation (Navigation 2.8+) via `@Serializable` classes instead of fragile route strings.

## Interview answer — structured

Managing Previews, Permissions, and Navigation cleanly requires adopting modern Jetpack Compose tooling standards.

First, with Compose Previews, rather than writing individual `@Preview` annotations per file, we define custom **Multipreview Annotations** (e.g. `@ThemePreviews`, `@DevicePreviews`) that automatically render composables in Light mode, Dark mode, large accessibility font scales (1.5x), and tablet layouts. For state permutations, we use `@PreviewParameter(UserProvider::class)` to render empty, loaded, and error variants simultaneously. Next, we manage runtime permissions using `rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission())` paired with rationale logic. If denied, we check `ActivityCompat.shouldShowRationale()` to explain the user value before requesting again; if permanently denied, we provide a clean intent redirecting to Android System Settings.
Finally, with Type-Safe Navigation (Navigation 2.8+), we discard legacy string URLs (`"profile/{userId}"`) in favor of official **Type-Safe Navigation**. Destined routes and arguments are modeled as `@Serializable` data classes and objects. The compiler verifies parameter types at compile time, eliminating URL encoding bugs and null-pointer parsing errors.


## Interview answer — deep senior

Type-Safe Navigation in Navigation 2.8+ transforms route handling under the hood. When navigating to `navController.navigate(ProfileDestination(userId = "123"))`, Navigation serializes the object into an internal route bundle using Kotlinx Serialization. Inside `composable<ProfileDestination> { backStackEntry -> ... }`, accessing arguments is completely type-safe: `val profile = backStackEntry.toRoute<ProfileDestination>()`, with automatic parsing of custom parcelable objects and primitive types.

For permissions, handling configuration changes during an in-flight permission dialog is critical. Because `rememberLauncherForActivityResult` hooks into `ActivityResultRegistry`, recreation during rotation preserves the pending request callback, resolving correctly when the permission dialog dismisses.

In testing, Type-Safe destinations make asserting navigation trivial: in Compose UI tests, we can query `navController.currentBackStackEntry?.toRoute<ProfileDestination>()` to verify that a button click routed to the expected typed destination.


## How to answer in the interview

- **Why:** platform permission state is asynchronous and revocable.
- **How:** separate previewable Screen from launcher-owning Route.
- **Trade-off:** add integration tests for the Activity path.
- **Failure case:** requesting on every recomposition loops the dialog.
- **Production solution:** handle denial, Settings return, and durable draft IDs.

## Deep-dive talking points

Discuss stateless previews, Activity Result ownership, location rationale/denial, Photo Picker as a separate contract, route arguments, and restoration.

## Follow-up questions

- **Interviewer:** "What is the primary advantage of Type-Safe Navigation in Navigation 2.8+?"
  **Answer:** "Compile-time validation of route parameters, eliminating runtime typos, manual URI string building, manual bundle key retrieval, and parameter type casting bugs."

- **Interviewer:** "Why shouldn't you request a runtime permission directly in `LaunchedEffect(Unit)`?"
  **Answer:** "Triggering permission dialogs automatically without user context or gesture violates Android guidelines, confuses users, and leads to high permission denial rates. Permissions should always be requested in response to an explicit user interaction."

## Self-check rubric

Show a preview contract, permission event flow, denial path, and process-safe navigation argument.

## References and reviewed-on date

- [Permissions in Compose](https://developer.android.com/training/permissions/requesting) — runtime request and rationale.
- [Navigation with Compose](https://developer.android.com/develop/ui/compose/navigation) — arguments and navigation.
- [Android Photo Picker](https://developer.android.com/training/data-storage/shared/photo-picker) — selected-media access without a broad library permission.

Technically reviewed against primary documentation on 2026-10-13.

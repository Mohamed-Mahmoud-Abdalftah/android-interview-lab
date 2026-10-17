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

## Concept and technical explanation

Handling previews, runtime permissions, and navigation in Jetpack Compose requires modular decoupling across the UI architecture. Previews are built using stateless Screen composables paired with @PreviewParameter and custom multi-preview annotations for light, dark, and font-scale configurations without mocking heavy framework dependencies. Permissions are managed using the official rememberLauncherForActivityResult API with RequestPermission contracts, presenting user-friendly rationale dialogs before prompting system dialogs. Navigation is isolated by hoisting navigation callbacks as pure lambdas to the top-level NavHost graph, enforcing type-safe routing and keeping leaf UI components completely agnostic of NavController instances.

## Practical walkthrough (English)

Unified demonstration of previews, permissions, and decoupled navigation:
```kotlin
// 1. Preview Provider for multi-state design testing
class UserStateProvider : PreviewParameterProvider<UserUiState> {
    override val values = sequenceOf(
        UserUiState(name = "Ahmed", hasCameraAccess = false),
        UserUiState(name = "Sara", hasCameraAccess = true)
    )
}

// 2. Stateless Screen Composable with permission request and hoisted navigation
@Composable
fun CameraScreenContent(
    state: UserUiState,
    onNavigateBack: () -> Unit,
    onRequestPermission: () -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(modifier = modifier) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Text("User: ${state.name}")
            if (state.hasCameraAccess) {
                Text("Camera Active", color = Color.Green)
            } else {
                Button(onClick = onRequestPermission) { Text("Grant Camera Permission") }
            }
            Spacer(modifier = Modifier.height(16.dp))
            Button(onClick = onNavigateBack) { Text("Back to Home") }
        }
    }
}

// 3. Preview Annotation
@Preview(name = "Light Mode", showBackground = true)
@Preview(name = "Dark Mode", uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
private fun CameraScreenPreview(@PreviewParameter(UserStateProvider::class) state: UserUiState) {
    MaterialTheme { CameraScreenContent(state = state, onNavigateBack = {}, onRequestPermission = {}) }
}

// 4. Route Composable handling real runtime permission launcher
@Composable
fun CameraRoute(onNavigateBack: () -> Unit) {
    var hasPermission by remember { mutableStateOf(false) }
    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted -> hasPermission = isGranted }

    CameraScreenContent(
        state = UserUiState(name = "Production User", hasCameraAccess = hasPermission),
        onNavigateBack = onNavigateBack,
        onRequestPermission = { permissionLauncher.launch(Manifest.permission.CAMERA) }
    )
}
```

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

We handle previews by designing stateless screen composables and supplying mock data via PreviewParameterProvider across light and dark multi-previews. Runtime permissions are managed using rememberLauncherForActivityResult with RequestPermission, decoupling permission launchers from presenter composables. Navigation is decoupled by hoisting event lambdas to the NavHost boundary, keeping individual screens pure, previewable, and completely independent of NavController instances.

## Interview answer — structured

Architecting a robust Jetpack Compose application requires clean separation across three major system concerns: visual tooling previews, Android runtime permissions, and navigation dispatching.
First, for Android Studio Previews, we avoid injecting ViewModels or system contexts into screen composables.
By keeping the Screen Composable stateless, we can feed it mock domain fixtures using PreviewParameterProvider.
Creating custom multi-preview meta-annotations enables instant verification across light, dark, and localized font configurations in a single compilation pass.
Second, for runtime permissions, we leverage the official Activity Result APIs inside Compose.
Using rememberLauncherForActivityResult with ActivityResultContracts.RequestPermission creates an asynchronous bridge to the platform permission manager.
We present educational in-app rationale sheets when shouldShowRequestPermissionRationale is true, and provide direct settings deep-links if permissions are permanently denied, ensuring graceful degradation.
Third, for navigation, we strictly enforce navigation hoisting.
Screens never accept NavHostController as a parameter.
Instead, they expose explicit lambda callbacks like onBackClick or onItemSelected.
The hosting Route composable maps these callbacks directly into type-safe navigation routes, ensuring leaf widgets remain 100% reusable and testable on the JVM.

## Interview answer — deep senior

Under the hood, these three mechanisms illustrate Compose's boundary mediation with the underlying Android operating system.
The @Preview annotation relies on Android Studio's LayoutLib, a specialized headless desktop rendering engine that emulates the Android framework. Because LayoutLib lacks an active Dagger or Hilt dependency graph, passing stateful ViewModels or platform service managers into a composable immediately crashes the preview renderer. Decoupling screens into stateless presenters allows LayoutLib to render composables purely from memory fixtures in the SlotTable.
The rememberLauncherForActivityResult API interfaces with the host ComponentActivity's ActivityResultRegistry.
When the composable registers the launcher, Compose generates a unique synthetic key and attaches an observer to the Activity's lifecycle.
When the platform permission dialog returns a result, the registry routes the boolean callback to the composition thread, safely updating a SnapshotMutableState and triggering recomposition without memory leaks or configuration change losses.
For navigation, decoupling NavController preserves compiler skipping optimizations.
Because NavController is an unstable platform object containing deep backstacks, passing it down through parameters forces the Compose compiler to mark the composable as unskippable.
By converting navigation actions into stable lambda function types (such as () -> Unit), the compiler enables zero-allocation skipping, preventing entire screen trees from recomposing during unrelated parent UI updates.

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

---
id: "AND-13"
question: "How do you handle runtime permissions and denial/permanent denial?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "B"
phase: 1
priority: "P1"
order: 43
editorial_status: "reviewed"
---

# AND-13

## Original interview question

How do you handle runtime permissions and denial/permanent denial?

## What the interviewer evaluates

- Request only a capability required for a user-initiated feature, at the moment of use.
- Handle grant, ordinary denial, repeated denial, revocation, and Settings return without trapping the user.
- Avoid treating `shouldShowRequestPermissionRationale()` as a universal permanent-denial oracle.

## Concept and technical explanation

The Android runtime permission model, introduced in Android 6.0 (API level 23) and continuously refined in recent platform releases, requires applications to request dangerous permissions at runtime rather than relying solely on install-time grants. Dangerous permissions guard user privacy and sensitive hardware access, including camera, microphone, precise location, contacts, and media storage.

Handling runtime permissions requires orchestrating four distinct permission states:
1. Already Granted:
Verified via `ContextCompat.checkSelfPermission()`. If granted, the application executes the feature workflow immediately.
2. Initial State / Not Yet Requested:
The permission has never been presented to the user. The application can trigger the system permission prompt directly.
3. Denied (Temporary Denial):
The user tapped Deny once. When the feature is re-triggered, `ActivityCompat.shouldShowRequestPermissionRationale()` returns true. The application must display an educational rationale dialog explaining why the capability is needed for the requested feature, before launching the system prompt again.
4. Permanently Denied ("Don't Ask Again"):
The user denied the permission twice or explicitly checked 'Don't ask again'. In this terminal state, `shouldShowRequestPermissionRationale()` returns false after denial, and the system prompt will no longer appear. The application must gracefully disable the dependent feature and present an informative dialog offering to navigate the user to the application's system settings screen (`Settings.ACTION_APPLICATION_DETAILS_SETTINGS`).

Modern architectures strictly manage permissions via the AndroidX Activity Result API (`ActivityResultContracts.RequestPermission()`), registering typed callback launchers unconditionally during Activity or Fragment initialization.

## Practical walkthrough (English)

Comprehensive implementation of runtime permission handling using the Activity Result API and rationale routing:
```kotlin
class CameraFeatureActivity : AppCompatActivity() {

    // 1. Unconditionally register the permission launcher during initialization
    private val requestCameraLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            launchCameraHardware()
        } else {
            handlePermissionDenial()
        }
    }

    fun onCaptureButtonClicked() {
        when {
            ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED -> {
                launchCameraHardware()
            }
            ActivityCompat.shouldShowRequestPermissionRationale(this, Manifest.permission.CAMERA) -> {
                showRationaleDialog {
                    requestCameraLauncher.launch(Manifest.permission.CAMERA)
                }
            }
            else -> {
                // First-time request or permanently denied
                requestCameraLauncher.launch(Manifest.permission.CAMERA)
            }
        }
    }

    private fun handlePermissionDenial() {
        if (!ActivityCompat.shouldShowRequestPermissionRationale(this, Manifest.permission.CAMERA)) {
            // Permanently denied: guide user to system settings
            showSettingsRedirectDialog()
        } else {
            // Temporary denial: feature disabled with explanation
            showFeatureDisabledBanner()
        }
    }

    private fun showSettingsRedirectDialog() {
        AlertDialog.Builder(this)
            .setTitle("Camera Permission Required")
            .setMessage("Camera access was permanently disabled. Please enable it in Settings to take photos.")
            .setPositiveButton("Open Settings") { _, _ ->
                val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                    data = Uri.fromParts("package", packageName, null)
                }
                startActivity(intent)
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}
```

## Explanation in Arabic

التعامل مع أذونات التشغيل (Runtime Permissions) في أندرويد الحديث وإدارة حالات الرفض الدائم (Permanent Denial) هي إحدى أهم متطلبات تجربة المستخدم (UX) والأمان:

1. شجرة القرار المنطقية للأذونات (Permission Decision Flow):
   - **الخطوة 1: الفحص المسبق (`ContextCompat.checkSelfPermission`):**
     * هل الإذن ممنوح بالفعل؟ لو نعم -> نفذ العملية فوراً (افتح الكاميرا مثلاً).
   - **الخطوة 2: فحص مبرر الإذن (`shouldShowRequestPermissionRationale`):**
     * لو رجعت `true`: هذا يعني أن المستخدم رفض الإذن مرة واحدة من قبل! هنا **يجب إظهار شاشة توضيحية (Rationale UI/Dialog)** تشرح له بوضوح وفائدة: 'لماذا يحتاج التطبيق إذن الكاميرا لمسح باركود الشحنة'، مع زر لطلب الإذن مجدداً.
   - **الخطوة 3: طلب الإذن عبر Activity Result API:**
     * استدعاء `requestPermissionLauncher.launch(permission)`.

2. الرفض الدائم (Permanent Denial - 'Don't ask again'):
   - في أندرويد الحديث (Android 11+)، إذا رفض المستخدم الإذن مرتين، النظام يمنع ظهور نافذة الإذن نهائياً، ودالة `shouldShowRequestPermissionRationale` ترجع `false`!
   - **كيف يتعامل الـ Senior Engineer مع الرفض الدائم؟**
     * لا نستسلم ولا نترك الزر معطلاً بدون شرح؛ نظهر Dialog للمستخدم يشرح: 'تم تعطيل إذن الكاميرا. يرجى تفعيله من إعدادات التطبيق للمتابعة'، مع زر يفتح صفحة إعدادات التطبيق مباشرة عبر Intent: `Settings.ACTION_APPLICATION_DETAILS_SETTINGS`.

## Practical walkthrough

التنفيذ البرمجي الكامل باستخدام Activity Result API:
```kotlin
class CameraFeatureActivity : AppCompatActivity() {

    // 1. تسجيل الـ Launcher في البداية:
    private val requestCameraLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            openCamera()
        } else {
            // فحص هل الرفض دائم؟
            if (!shouldShowRequestPermissionRationale(Manifest.permission.CAMERA)) {
                showSettingsRedirectDialog() // توجيه للإعدادات
            } else {
                showPermissionDeniedToast()
            }
        }
    }

    fun onCaptureClicked() {
        when {
            ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED -> {
                openCamera()
            }
            shouldShowRequestPermissionRationale(Manifest.permission.CAMERA) -> {
                showEducationalDialog { requestCameraLauncher.launch(Manifest.permission.CAMERA) }
            }
            else -> {
                requestCameraLauncher.launch(Manifest.permission.CAMERA)
            }
        }
    }

    private fun showSettingsRedirectDialog() {
        AlertDialog.Builder(this)
            .setTitle("Camera Permission Required")
            .setMessage("You have permanently disabled camera access. Please enable it in Settings to scan QR codes.")
            .setPositiveButton("Settings") { _, _ ->
                val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                    data = Uri.fromParts("package", packageName, null)
                }
                startActivity(intent)
            }
            .show()
    }
}
```

## Why it matters and how it works

Dangerous permissions need runtime grant on supported Android versions and can be revoked. The Activity Result `RequestPermission` contract gives a lifecycle-aware result; the app must still check permission at use time and handle the denied path. Rationale helps explain why a specific feature needs access; it is not a coercive gate. If the system stops showing the prompt after repeated denial, the app cannot grant itself access. Platform permission rules vary by API level and permission category, so code should follow current guidance for camera, location, media, notifications, and background location separately.

## Worked example

A nearby-store Activity registers its launcher before user interaction. This abbreviated Android snippet assumes a manifest declaration for coarse location and app methods to load nearby stores or offer a manual city.
```kotlin
import android.Manifest
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts

class NearbyActivity : ComponentActivity() {
    private val requestLocation = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) loadNearby() else showManualCity()
    }

    fun onNearMeTapped() {
        requestLocation.launch(Manifest.permission.ACCESS_COARSE_LOCATION)
    }

    private fun loadNearby() { /* app-owned location flow */ }
    private fun showManualCity() { /* fallback UI */ }
}
```
Check the current permission before loading and again after returning from Settings; a `false` callback does not by itself prove permanent denial. Offer manual city selection regardless of the denial path.

## Trade-offs and decision criteria

Asking at onboarding is easy for code but often lacks user context and increases denial; just-in-time requests explain value. Precise location can improve results but coarse location may be sufficient and less intrusive. A system picker can avoid broad media access, but may not meet bulk background processing requirements. Settings navigation should be optional and explained; denying the feature must not make unrelated app functions unusable.

## Failure modes

An app asks repeatedly after every denial, causing a hostile loop. Another assumes permission remains granted forever and crashes after revocation. Treating false rationale as a permanent-denial flag on first launch misclassifies users. Requesting background location alongside foreground location can violate platform flow and confuse users. Test first request, one denial, repeated denial, Settings grant/revoke, and API-version differences on real devices.

## Production perspective

For a delivery app, keep address search usable manually and request location only when the user selects GPS assistance. Record aggregate permission funnel events without storing coordinates unnecessarily. A feature gate checks current grant before accessing location and handles `SecurityException` as defense in depth. The release test matrix covers target SDK and supported API levels, revocation while backgrounded, and the return path from Settings.

## Interview answer — short

Runtime permissions must be requested contextually at the point of need using the Activity Result API. If granted, execute the feature; if denied, evaluate shouldShowRequestPermissionRationale to display an educational explanation; if permanently denied, inform the user and direct them to App Settings.

## Interview answer — structured

Android's runtime permission model requires applications to request sensitive capabilities—such as camera, location, and audio recording—in context at the moment of use, rather than requesting blanket access during installation.

An application must gracefully manage three core user responses: permission grant, temporary denial, and permanent denial. When access is granted, the feature proceeds immediately. If the user denies the request, the platform's shouldShowRequestPermissionRationale API evaluates whether we should present an educational dialog explaining the concrete functional value of the permission before re-requesting it.

When a user repeatedly denies a permission or selects 'Don't ask again', the operating system suppresses future system permission dialogs. In this permanent denial state, shouldShowRequestPermissionRationale returns false. Our architectural responsibility is to avoid trapping the user in a broken loop; instead, we offer a clear prompt redirecting them to the application's system settings page via Settings.ACTION_APPLICATION_DETAILS_SETTINGS.

In production, we execute permission workflows through the AndroidX Activity Result API using ActivityResultContracts.RequestPermission. Registering this launcher during initialization guarantees that permission results survive Activity recreation and background process suspension without callback loss.


## Interview answer — deep senior

At the operating system and Linux kernel level, runtime permissions are governed by the PermissionManagerService and AppOpsManager running inside system_server. When an application is granted a dangerous permission, the framework dynamically maps the application's Linux User ID (UID) to underlying kernel supplementary groups (GIDs), adjusting file system sandboxes and hardware device driver nodes (such as /dev/video for camera hardware).

The state machine driving shouldShowRequestPermissionRationale() is nuanced and platform-dependent. In the system server's permission database, each permission grant record maintains bitwise flags: USER_SET, USER_FIXED, and POLICY_FIXED. Prior to the initial request, the rationale method returns false. Following a single user denial, the USER_SET flag is applied, causing shouldShowRequestPermissionRationale() to return true. If the user selects 'Don't ask again' or denies the prompt a second time on Android 11+, the USER_FIXED flag is set. Once USER_FIXED is active, the system server immediately rejects future requestPermissions() IPC transactions without showing a prompt, and shouldShowRequestPermissionRationale() permanently returns false.

Modern Android versions introduce additional privacy boundaries: Android 11 added one-time permissions ('Only this time'), where grants expire as soon as the process terminates. Android 12 introduced approximate versus precise location, Android 13 introduced runtime notification permissions, and Android 14 added partial photo access.

Staff engineers structure permission architectures so that core business logic never assumes permanent grants. Features must verify permissions prior to every hardware invocation, provide graceful functional degradation when access is withheld, and implement clean fallback pathways when users return from the system settings screen via onResume() observation.

## How to answer in the interview

- **Why:** Permission is a revocable user choice, not a startup formality.
- **How:** Request in feature context, handle callback, and recheck before access.
- **Trade-offs:** Offer manual city or scoped API when location is unnecessary.
- **Failure cases:** Reject the claim that `shouldShowRequestPermissionRationale() == false` always means permanent denial.
- **Production solution:** Test denial, approximate/temporary grant, Settings return, and revocation.

## Deep-dive talking points

Discuss permission minimization, rationale state ambiguity, repeated denial, revocation, Activity Result registration, coarse versus fine location, settings return, and API-version test coverage.

## Follow-up questions

- **Interviewer:** "Why must you register the Activity Result launcher before `onStart()`?"
  **Answer:** "Because the Activity Result API requires registering listeners during `onCreate()` or property initialization so that if the Activity is destroyed and recreated while the permission dialog is visible, the result can be reconnected to the callback."

- **Interviewer:** "Can you request multiple permissions at once?"
  **Answer:** "Yes, using `ActivityResultContracts.RequestMultiplePermissions()`, which takes an array of permissions and returns a `Map<String, Boolean>` mapping each permission to its grant result."

- **Interviewer:** "What happens if you request a permission that is not declared in AndroidManifest.xml?"
  **Answer:** "The system will immediately deny the permission without showing any dialog to the user, and will log a security warning in Logcat."

## Self-check rubric

Name a permission-free alternative; describe a just-in-time request; handle first and repeated denial; explain rationale ambiguity; and test revocation and Settings return.

## References and reviewed-on date

- [Request runtime permissions](https://developer.android.com/training/permissions/requesting) — request timing, rationale, denial, and revocation.
- [Get a result from an activity](https://developer.android.com/training/basics/intents/result) — lifecycle-aware launcher registration.

Technically reviewed against primary documentation on 2026-10-13.

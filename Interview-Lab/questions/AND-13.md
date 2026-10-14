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

Check permission with ContextCompat.checkSelfPermission(). If denied, check shouldShowRequestPermissionRationale() to show an educational rationale dialog before requesting. If denied permanently ('Don't ask again'), guide the user to the app's system Settings screen via Settings.ACTION_APPLICATION_DETAILS_SETTINGS.

## Interview answer — structured

Handling runtime permissions cleanly requires adhering to Android's modern 4-step permission lifecycle.

First, with Check Status, query `ContextCompat.checkSelfPermission()`. If granted, execute the protected feature immediately. Next, with Check Rationale, if not granted, evaluate `ActivityCompat.shouldShowRequestPermissionRationale()`. If this returns `true`, the user has previously denied the request. Before showing the system dialog again, display an in-app educational rationale dialog explaining *why* the camera or location is required for this specific feature.
Additionally, with Request via Activity Result API, launch the request using `ActivityResultContracts.RequestPermission()`, which replaces deprecated `onRequestPermissionsResult`. Finally, with Handle Permanent Denial, in modern Android, if the user denies the permission twice, the OS permanently suppresses system dialogs. If permission is denied and `shouldShowRequestPermissionRationale()` returns `false`, the permission is permanently denied. Display a clear UI explanation with an actionable button redirecting the user to `Settings.ACTION_APPLICATION_DETAILS_SETTINGS` to enable it manually.


## Interview answer — deep senior

From an OS policy perspective, Android 11+ introduces **One-time Permissions** and automatic permission resets for unused apps. When a user grants 'Only this time', the permission is granted only while the Activity is in the foreground and is revoked the moment the process dies.

Furthermore, in Android 13 (API 33), runtime permissions were added for `POST_NOTIFICATIONS` and granular media (`READ_MEDIA_IMAGES`, `READ_MEDIA_VIDEO`, `READ_MEDIA_AUDIO`), deprecating the old broad `READ_EXTERNAL_STORAGE`. In Android 14 (API 34), users can grant **Partial Media Access** (`READ_MEDIA_VISUAL_USER_SELECTED`), allowing access to a selected subset of photos. Apps must handle this partial authorization without crashing or assuming full gallery visibility.


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

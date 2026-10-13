---
id: "AND-22"
question: "A crash occurs only after backgrounding the app for several hours. How would you investigate lifecycle and process restoration?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "C"
phase: 1
priority: "P1"
order: 52
editorial_status: "reviewed"
---

# AND-22

## Original interview question

A crash occurs only after backgrounding the app for several hours. How would you investigate lifecycle and process restoration?

## What the interviewer evaluates

- Form a process-death hypothesis without assuming every background crash is caused by process death.
- Reproduce cold restoration and inspect crash evidence, state ownership, and entry intent.
- Fix missing durable state or invalid lifecycle assumptions and verify the original path.

## Explanation in Arabic

عطل (Crash) يحدث فقط بعد ترك التطبيق في الخلفية لعدة ساعات: كيف تحقق في هذا العطل وتكتشف علاقته بدورة الحياة والـ Process Restoration؟

1. تشخيص العطل (The Diagnosis):
   - العطل الذي يظهر فقط بعد ساعات في الخلفية هو بنسبة 99% **عطل ناتج عن Process Death غير المعالج (Unmanaged Process Death Crash)**!
   - عندما يترك التطبيق لساعات، يقوم نظام أندرويد بقتل الـ Process لتوفير الرام.
   - عند عودة المستخدم، يقوم النظام بإعادة فتح **نفس الشاشة الداخلية التي كان يقف عليها** (Restored Activity) من الـ Backstack، ولكن كل الـ In-memory Singletons والـ Static variables والـ Cache أصبحت `null`!
   - الكود يحاول قراءة `UserSession.currentUser.id` فيحدث `NullPointerException` فوراً!

2. كيف تعيد تمثيل العطل في ثوانٍ في بيئة التطوير (Reproduction in 5 seconds)؟
   - لا تنتظر ساعات! افتح الشاشة في المحاكي، اضغط زر Home، ثم نفذ أمر:
     `adb shell am kill <package_name>`
   - ثم افتح التطبيق من Recents؛ سيعاد إنتاج الـ Crash فوراً!

3. الحل المعماري الجذري:
   - عدم الاعتماد على Singletons عائمة في الذاكرة لتمرير البيانات بين الشاشات.
   - استخدام `SavedStateHandle` لتمرير المعرفات (IDs)، وإعادة تحميل البيانات من قاعدة بيانات Room أو DataStore عند بدء الشاشة.

## Practical walkthrough

التحقيق والحل في الكود:
```kotlin
// ❌ الكود المسبب للكراش بعد ساعات:
class OrderDetailsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // كارثة: يفترض أن الـ Singleton يحتوي على بيانات المستخدم!
        // بعد ساعات في الخلفية، AppSession تصبح null ويحدث Crash فوراً:
        val user = AppSession.currentUser!! // NullPointerException!
        loadOrder(user.token)
    }
}

// ✅ الحل المعماري المستقر:
class OrderDetailsViewModel(
    savedStateHandle: SavedStateHandle,
    authRepository: AuthRepository,
    orderRepository: OrderRepository
) : ViewModel() {
    // نقرأ المعرفات المحفوظة من SavedStateHandle ونقرأ التوكن من DataStore دائم التخزين:
    val orderId: String = checkNotNull(savedStateHandle["order_id"])
    val uiState = authRepository.observeSessionToken().flatMapLatest {
        orderRepository.observeOrder(orderId)
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), Loading)
}
```

## Why it matters and how it works

Background process lifetime is controlled by Android. Saved instance state can restore lightweight UI context when system-initiated recreation occurs, but it is not a durable database. A ViewModel is constructed afresh after process death. Entry can arrive from Recents, notification, or a deep link, each with different Intent and back-stack context. Production crash clusters, process-start telemetry, and stack traces distinguish an uninitialized in-memory dependency from token expiry or a stale URI grant.

## Worked example

A parcel-tracking screen crashes on return because `CurrentShipment.id` was held only in an application singleton. A notification resumes the route after the process was killed, leaving that field null. Store the shipment ID in route/saved state, load shipment data from repository, and render loading/error states. If the account was signed out or the shipment no longer exists, navigate to a safe destination rather than force-unwrapping. This is a diagnostic case study, not a claim about a specific crash report.

## Trade-offs and decision criteria

Saved state is fast and appropriate for small identifiers and UI choices; durable storage is needed for user work that must survive app closure and device reboot. Re-fetching server data improves freshness but needs offline behavior and loading UX. Persisting entire response objects increases staleness and Bundle pressure. A one-off “Don't keep activities” reproduction probes recreation but is not equivalent to killing the app process; verify both.

## Failure modes

An Activity reads a `lateinit` property initialized only during an earlier flow. A callback arrives after permissions are revoked. A temporary content URI is no longer readable. A token expires during hours in background and a blind retry loops. A network result is applied to a destroyed screen. Guard each boundary, handle domain errors, and preserve cancellation when jobs no longer have an owner.

## Production perspective

Collect stack trace, breadcrumbs for lifecycle and process start, app/OS version, and entry source without logging customer data. Build a reproduction matrix: warm return, Activity recreation, actual process kill and Recents return, notification launch, and expired session. Add a regression test for the identified state path; monitor the crash cluster and restoration success rate after rollout. A payment or order operation must reconcile by stable server ID and idempotency key, never silently submit again.

## Interview answer — short

This is a classic Process Death crash. After hours in the background, Android killed the app process. Upon return, Android recreates the top Activity while in-memory singletons and static caches are completely null, triggering NullPointerExceptions. Reproduce it instantly via 'adb shell am kill <package>' and fix it using SavedStateHandle and persistent Room/DataStore storage.

## Interview answer — structured

A crash that manifests only after the app has been backgrounded for several hours is the quintessential signature of **Unmanaged Process Death**.

**Why it occurs:**

While in the background, Android's Low Memory Killer terminated the process. When the user taps the app in Recents hours later, Android attempts to restore user continuity by restoring the exact top Activity the user was on. However, because the process was killed, all in-memory static variables, singletons, Dagger graphs, and cache objects were wiped. When the restored Activity attempts to dereference `AppCache.selectedUser` or `SessionManager.currentUser`, it crashes immediately with a `NullPointerException`.

**How I investigate and fix it:**

1. **Instant Reproduction**: Background the app on an emulator, run `adb shell am kill <package_name>`, and click the app in Recents. This reproduces the multi-hour crash in 5 seconds.
2. **Inspect Navigation & Bundles**: Verify that the restored Activity/Fragment extracts its required IDs from `SavedStateHandle` or `Intent.extras` rather than relying on global memory caches.
3. **Persistent Auth Fallback**: If user authentication is required, retrieve the auth token asynchronously from encrypted DataStore; if expired, gracefully redirect the backstack to the Login screen rather than crashing.

## Interview answer — deep senior

From a root-cause analysis perspective, inspect the stack trace in Crashlytics: A process death crash almost always shows the Activity's `onCreate(savedInstanceState)` receiving a non-null `Bundle`, while an in-memory utility class threw NPE.

In enterprise codebases, we enforce architectural defenses against process death bugs: 1. **Never use static variables or Singletons as cross-screen data transport.** 2. **Enable 'Don't keep activities' during developer QA.** 3. **Session Interceptor Pattern**: In the base Activity or root Navigation Host, evaluate whether a mandatory user session is valid. If the session was purged by process death, immediately navigate to the Splash/Auth screen with a return intent flag, restoring the session before any deep Activity code runs.

## How to answer in the interview

- **Why:** Long background gaps expose assumptions about in-memory state and revoked resources.
- **How:** Correlate stack traces with lifecycle events and reproduce real process restoration.
- **Trade-offs:** Restore small keys, reload authoritative data, and show loading/error states.
- **Failure cases:** Name singleton nulls, expired auth, lost URI grants, and misleading rotation-only tests.
- **Production solution:** Patch the parcel screen’s route restoration and monitor the crash cohort.

## Deep-dive talking points

Discuss stack evidence, process-start markers, saved-state boundaries, notification/deep-link entry, token expiry, URI revocation, and idempotent recovery.

## Follow-up questions

- **Interviewer:** "What is the Developer Option 'Don't keep activities' and does it simulate process death?"
  **Answer:** "'Don't keep activities' only simulates Activity lifecycle destruction and recreation across configuration changes; it does NOT kill the underlying Linux process or wipe in-memory singletons. Full process death must be simulated using `adb shell am kill`."

- **Interviewer:** "Why does Android restore internal screens instead of always restarting from the launcher?"
  **Answer:** "To provide a seamless multitasking user experience. If a user was composing an email or editing a profile, Android attempts to bring them back to their exact work in progress rather than kicking them back to the home screen."

- **Interviewer:** "How do you test this scenario in automated CI/CD UI tests?"
  **Answer:** "In Espresso or UI Automator tests, invoke `UiDevice.getInstance().pressHome()`, execute the shell command `am kill`, and then reopen the app from the recent task switcher."

## Self-check rubric

Describe two competing hypotheses, collect evidence, reproduce true process death, fix state ownership, and verify the original entry path.

## References and reviewed-on date

- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — process-death restoration limits.
- [Processes and app lifecycle](https://developer.android.com/guide/components/activities/process-lifecycle) — process importance and termination.
- [Start an Activity from a Notification](https://developer.android.com/develop/ui/views/notifications/navigation) — notification entry and back stack.

Technically reviewed against primary documentation on 2026-10-13.

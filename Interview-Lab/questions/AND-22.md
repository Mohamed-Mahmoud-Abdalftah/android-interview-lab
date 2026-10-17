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

## Concept and technical explanation

Crashes that occur exclusively after an application has remained in the background for extended periods are almost universally caused by unhandled background process death. When an app is placed in the background, its Linux process transitions to a cached state. Under system memory constraints, the Android Low Memory Killer daemon (lmkd) terminates the process without invoking onDestroy.
When the user subsequently relaunches the application from the Overview/Recents screen, the Android framework resurrects the process, invokes Application.onCreate(), and directly recreates the top Activity from the backstack, restoring its saved state via the savedInstanceState Bundle. However, all in-memory static variables, singletons, and non-retained caches that were initialized by antecedent screens in the task flow remain completely uninitialized (null). When the restored Activity attempts to access these assumed in-memory objects, it immediately crashes with a NullPointerException. Investigating and remediating this issue requires simulating process death in development environments, verifying state restoration pipelines, and enforcing durable repository architectures.

## Practical walkthrough (English)

Investigating and resolving process death crashes caused by uninitialized static singletons:

```kotlin
// ❌ Flawed implementation crashing after process death:
class OrderDetailsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Crash! AppSession was initialized by LoginActivity, which did not run upon restoration:
        val userId = AppSession.currentUser.id 
        loadOrder(userId)
    }
}

// ✅ Resilient architecture using SavedStateHandle and durable storage:
@HiltViewModel
class OrderDetailsViewModel @Inject constructor(
    private val savedStateHandle: SavedStateHandle,
    private val userRepository: UserRepository,
    private val orderRepository: OrderRepository
) : ViewModel() {

    // Preserved across process death via SavedStateHandle:
    private val orderId: String = checkNotNull(savedStateHandle["order_id"])

    val uiState: StateFlow<OrderUiState> = userRepository.getUserIdFlow()
        .flatMapLatest { userId -> orderRepository.getOrderStream(userId, orderId) }
        .map { order -> OrderUiState.Success(order) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), OrderUiState.Loading)
}
```

Failure scenario: An e-commerce app stores the active user session and cart items in an in-memory singleton during checkout. When the user leaves the app in the background overnight, Android kills the process. Tapping the app the next morning restores CheckoutActivity, which immediately crashes with NullPointerException: AppSession.cart is null.

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

Crashes occurring after hours in the background indicate unhandled process death by the Low Memory Killer. Android recreates the top Activity while all in-memory static singletons and non-retained ViewModels are lost. Reproduce the bug using adb shell am kill, pass stable identifiers through Intent extras and SavedStateHandle, and load data from local databases rather than assuming in-memory state.

## Interview answer — structured

Crashes that materialize only after an application has spent hours in the background are classic symptoms of unhandled process death. The Low Memory Killer terminates the cached Linux process to reclaim RAM, and when the user returns, Android attempts to resurrect the top Activity while all in-memory static caches and singletons are re-instantiated as null.

We reproduce this failure deterministically using developer tooling. We background the application and execute adb shell am kill with the package name, or enable Don't keep activities in Developer Options to stress state serialization boundaries. Inspecting logcat reveals whether the crash is a NullPointerException stemming from uninitialized memory.

In production, screens must never rely on preceding Activities to populate in-memory singletons. Every screen must be fully autonomous, receiving stable entity identifiers via Intent extras or SavedStateHandle, and retrieving fresh domain data directly from durable Room databases or reactive repositories.

If a session token or essential user credential has expired during the extended background interval, the app must intercept navigation cleanly, redirecting the user to the authentication gateway rather than allowing an unauthenticated screen to crash.


## Interview answer — deep senior

Under the hood, Android's process management is orchestrated by the ActivityManagerService and the Linux kernel's Low Memory Killer daemon (lmkd). When an application is moved to the background, its oom_score_adj is adjusted to cached priority (CACHED_APP, values 900 to 999). When system RAM drops below kernel watermarks, lmkd sends a SIGKILL signal to the process. Crucially, the operating system saves the task hierarchy and the serialized onSaveInstanceState Bundles in the system server process (ActivityTaskManagerService), while the entire heap and all static class variables in ART are wiped out.
When the user taps the app in Recents, Zygote forks a new process, the runtime calls Application.onCreate(), and ActivityTaskManager restores ONLY the top Activity that was visible, passing the saved Bundle to onCreate(savedInstanceState). Junior architectures often assume a linear navigation pipeline where Splash, Login, Home, and Details always run sequentially. In process restoration, DetailsActivity is created directly without Splash or Home ever executing. Any singleton like UserManager.currentUser that was initialized in an earlier screen will be null, resulting in an immediate crash.
To diagnose these failures in production, we analyze stack traces in Crashlytics. A key signature of process restoration crashes is a NullPointerException occurring on an internal screen within seconds of cold process initialization without antecedent breadcrumbs.
The architectural remedy requires three interventions: First, replace static singleton dependencies with Dependency Injection (Hilt) scoped to repositories. Second, store lightweight entity IDs in SavedStateHandle so the ViewModel can reload state independently. Third, establish an application-level session guard: if the app requires an authenticated session and the local token is missing or invalid upon cold restoration, the navigation router intercepts the launch and routes the task back to the Login gateway gracefully.

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

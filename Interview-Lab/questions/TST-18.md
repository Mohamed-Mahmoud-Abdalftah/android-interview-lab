---
id: "TST-18"
question: "How do you test process death, rotation, and offline transitions?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 413
editorial_status: "reviewed"
---

# TST-18

## Original interview question

How do you test process death, rotation, and offline transitions?

## What the interviewer evaluates

- Distinguishing rotation, process death and network offline.
- Durable state recovery versus retained ViewModel state.

## Concept and technical explanation

Testing process death, configuration rotation, and offline transitions requires distinguishing between three fundamentally different runtime failure vectors in Android architecture. Configuration change (such as device rotation or dark mode toggling) destroys and recreates the host Activity while preserving the ViewModelStore and all in-memory ViewModel state intact. Process death occurs when the Android operating system terminates the application's background process under system-wide RAM pressure, destroying the entire JVM instance, static variables, and ViewModelStore; upon return, the application must reconstruct its state exclusively from SavedStateHandle (for ephemeral UI state under 500KB) and durable local persistence (Room SQLite or DataStore). Offline transitions test data resilience when active network sockets fail, verifying that repositories gracefully fall back to local cached SQLite entities and expose unambiguous offline UI states without throwing unhandled exceptions.

## Practical walkthrough (English)

Testing rotation, process death restoration, and offline fallback transitions:
```kotlin
// 1. Testing configuration rotation with ActivityScenario
@Test
fun profileScreen_rotation_preservesUiState() {
    val scenario = ActivityScenario.launch(ProfileActivity::class.java)

    // Type text into input field
    onView(withId(R.id.name_input)).perform(typeText("Alex"), closeSoftKeyboard())

    // Trigger physical configuration change: recreate activity
    scenario.recreate()

    // Assert ViewModel retained state preserves the entered text
    onView(withId(R.id.name_input)).check(matches(withText("Alex")))
    scenario.close()
}

// 2. Testing process death restoration using SavedStateHandle
@Test
fun checkoutViewModel_processDeath_restoresDraftOrder() {
    // Stage initial state in SavedStateHandle
    val savedState = SavedStateHandle(mapOf("draft_order_id" to "order_9988"))
    val fakeRepo = FakeOrderRepository()

    // Instantiate ViewModel simulating fresh process resurrection
    val viewModel = CheckoutViewModel(savedStateHandle = savedState, repository = fakeRepo)

    // Assert that draft order was restored directly from saved state
    assertEquals("order_9988", viewModel.uiState.value.orderId)
    assertTrue(viewModel.uiState.value.isRestoredFromDeath)
}

// 3. Testing offline network loss fallback in Repository
@Test
fun fetchFeed_networkThrowsIOException_returnsCachedDatabaseEntities() = runTest {
    val mockApi = mockk<NewsApiService>()
    val fakeDatabase = FakeNewsDao()

    // Pre-populate local cache with verified offline entities
    fakeDatabase.insertAll(listOf(NewsEntity(id = 1, title = "Offline Cached Headline")))

    // Simulate complete network disconnection
    coEvery { mockApi.getLatestNews() } throws IOException("No route to host")

    val repository = NewsRepositoryImpl(api = mockApi, dao = fakeDatabase)
    val result = repository.getNewsStream().first()

    // Assert repository recovers gracefully by emitting cached content
    assertTrue(result.isSuccess)
    assertEquals("Offline Cached Headline", result.getOrNull()?.first()?.title)
}
```

## Explanation in Arabic

كيف تختبر سيناريوهات موت العملية (Process Death)، وتدوير الشاشة (Screen Rotation)، والانتقال لوضع عدم الاتصال (Offline Transitions)؟

1. اختبار موت العملية (Process Death Testing):
   - **المشكلة**: عند تشغيل التطبيق ووضعه في الخلفية، قد يقوم نظام أندرويد بقتل الـ Process لتوفير الذاكرة! عندما يعود المستخدم، يعاد بناء الـ Activity ولكن كل المتغيرات العادية في الذاكرة تصبح `null`.
   - **طريقة الاختبار**: استخدام `SavedStateHandle` ومحاكاة موت العملية برمجياً في الاختبارات باستخدام `ActivityScenario.recreate()` أو أمر ADB:
     `adb shell am kill <package_name>`.

2. اختبار تدوير الشاشة (Configuration Changes / Rotation):
   - التأكد من أن الـ ViewModel يحتفظ بالبيانات المحملة مسبقاً ولا يعيد طلبها من الشبكة عند تدوير الهاتف.
   - التأكد من أن حالات واجهة Compose المحفوظة بـ `rememberSaveable` تستعيد قيمها بدقة.

3. اختبار الانتقال لوضع عدم الاتصال (Offline Transition Testing):
   - قطع الاتصال بالإنترنت أثناء استخدام المستخدم للتطبيق، والتأكد من ظهور رسالة تنبيهية للمستخدم دون انهيار، وتخزين العمليات في طابور الـ Outbox المحلي.

## Practical walkthrough

اختبار استعادة الحالة بعد موت العملية باستخدام SavedStateHandle في Unit Test محلي:
```kotlin
class RegistrationViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    var email: String
        get() = savedStateHandle.get<String>("key_email") ?: ""
        set(value) = savedStateHandle.set("key_email", value)

    var step: Int
        get() = savedStateHandle.get<Int>("key_step") ?: 1
        set(value) = savedStateHandle.set("key_step", value)
}

class ProcessDeathStateRestorationTest {
    @Test
    fun `state survives process death simulation via SavedStateHandle`() {
        // 1. محاكاة الحالة قبل موت العملية:
        val initialHandle = SavedStateHandle()
        val viewModelBeforeDeath = RegistrationViewModel(initialHandle)
        viewModelBeforeDeath.email = "user@example.com"
        viewModelBeforeDeath.step = 2

        // 2. محاكاة حفظ الحالة واستعادتها في Process جديدة تماماً:
        val savedBundle = initialHandle.savedStateProvider().saveState()
        val restoredHandle = SavedStateHandle.createHandle(savedBundle, null)

        // 3. إنشاء ViewModel جديد في العملية المستعادة والتحقق من بقاء البيانات:
        val viewModelAfterDeath = RegistrationViewModel(restoredHandle)
        assertEquals("user@example.com", viewModelAfterDeath.email)
        assertEquals(2, viewModelAfterDeath.step)
    }
}
```

## Why it matters and how it works

Android may recreate components for configuration change and may later kill the process. Saved instance state is limited and not a substitute for durable financial records. Network loss can happen before or after a remote side effect; the client needs status lookup.

## Worked example

For a checkout screen, rotate during Loading and assert same operation ID. Kill/recreate the process after intent persistence and assert state reloads from Room. Cut network after server approval but before response and assert Unknown plus reconciliation, not Declined.

## Trade-offs and decision criteria

SavedStateHandle is convenient for UI navigation state but is not a transaction log. Room adds durability but cannot prove remote outcome. Emulator controls make tests repeatable; real device drills expose OEM behavior.

## Failure modes

A test calls Activity.recreate() and claims payment survives process death; the ViewModel survived, so it missed a lost in-memory operation ID. Use process-kill tooling and reopen app with persisted state.

## Production perspective

CI includes rotation/locale changes and background process recreation. Release drills include offline/online transitions at each payment boundary with backend sandbox and safe identifiers.

## Interview answer — short

We test rotation by calling ActivityScenario.recreate, verifying the ViewModel retains state across the destroyed Activity. We test process death by simulating OS termination, asserting the ViewModel recovers its critical state from SavedStateHandle or Room rather than resetting to defaults. We test offline transitions by mocking network IOExceptions, verifying the repository emits cached SQLite data while the UI updates to show offline mode cleanly.

## Interview answer — structured

A robust Android application must survive three distinct real-world lifecycle interruptions: screen rotation, low-memory process termination, and sudden network loss.
Screen rotation represents a transient configuration change.
The Android operating system destroys the Activity window and inflates a new layout, but the ViewModelStoreOwner survives on the non-configuration instance registry.
We test this using ActivityScenario.recreate, asserting that user input and loaded UI models persist across the transition without restarting background network fetch calls.
Process death is a far harsher survival test.
When the user switches away from the application and Android experiences memory pressure, the Linux kernel kills the entire application process.
When the user returns, Android allocates a brand new process and launches the destination Activity from scratch.
Because the ViewModel is destroyed, state can only be restored if it was written into SavedStateHandle or persisted to Room SQLite.
We test this by passing pre-populated SavedStateHandle instances into ViewModels or using StateRestorationTester in Jetpack Compose to assert exact state restoration.
Offline transitions test resilience to physical connectivity loss.
We verify our repositories by mocking network exceptions like SocketTimeoutException or UnknownHostException, asserting that the local Room cache immediately serves stale data with an offline UI indicator.

## Interview answer — deep senior

Under the hood, these three scenarios exercise different Android operating system contracts, kernel memory management signals, and persistence lifecycles.
Configuration change lifecycle is mediated by ActivityClientRecord and ConfigurationController within the Android framework.
When rotation occurs, the ActivityThread invokes retainNonConfigurationInstances(), stashing the ViewModelStore in memory before destroying the View decor and window.
Process death, however, triggers an operating system eviction sequence orchestrated by the ActivityManagerService and the Linux Low Memory Killer (LMK) daemon.
When an app moves to the cached background LRU state, Android serializes the Activity's onSaveInstanceState bundle into an IPC binder transaction, holding this Parcelable payload in system server memory while the app's PID is SIGKILLed.
Because the Binder transaction buffer is capped at approximately one megabyte across all active transactions, passing large data models in SavedStateHandle causes a fatal TransactionTooLargeException.
Senior engineers test process death by verifying that SavedStateHandle only retains lightweight identifier tokens (such as order IDs or draft UUIDs), while heavy payload data is reloaded from local Room SQLite databases.
Offline transition testing verifies the Single Source of Truth architecture.
Repositories use Room Flows as the primary stream; when network requests fail, the coroutine catches transport exceptions without terminating the Flow collector, allowing cached database rows to render smoothly while dispatching a one-shot Snackbar event via an isolated UI channel.

## How to answer in the interview

- **Why:** rotation, process death and offline loss have different state survivors.
- **How:** rotate, kill/relaunch and drop reply after approval in separate tests.
- **Trade-off:** fast fake state tests versus expensive Android and backend evidence.
- **Failure case:** a recreated screen sends a new charge ID.
- **Production solution:** durable intent, Unknown state and reconciliation.

## Deep-dive talking points

Prompt for lifetime table, actual process kill, same operation ID, offline-after-approval and backend reconciliation.

## Follow-up questions

- **Interviewer:** "What is TransactionTooLargeException in Android?"
  **Answer:** "An exception thrown when data passed across Binder IPC (such as saved instance state or intent extras) exceeds the shared 1MB buffer limit."

- **Interviewer:** "Why does ActivityScenario.recreate() not fully simulate process death?"
  **Answer:** "recreate() destroys and recreates the Activity within the same process, keeping static and singleton memory intact; real process death destroys the entire OS Linux process."

## Self-check rubric

Rotate while loading and verify one stable operation ID, recreate after persisted intent and verify recovery, then drop the network after server approval and assert Unknown plus reconciliation. Distinguish rotation from actual process death.

## References and reviewed-on date

- [Android saving UI state](https://developer.android.com/topic/libraries/architecture/saving-states) — state lifetimes.
- [Android offline-first data layer](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable data design.

Technically reviewed against primary documentation on 2026-10-13.

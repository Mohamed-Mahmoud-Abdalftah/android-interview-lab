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

Test process death by verifying SavedStateHandle state restoration in JVM unit tests, or by calling ActivityScenario.recreate() and adb shell am kill in instrumentation tests. Test rotation by verifying ViewModels retain data without re-fetching, and test offline transitions using reactive NetworkCallback fakes.

## Interview answer — structured

Testing OS lifecycle edge cases verifies resilience against system memory pressure and hardware configuration shifts:

1. **Testing Process Death**:
   - **JVM Unit Testing (SavedStateHandle)**: Save a state snapshot via `savedStateHandle.savedStateProvider().saveState()`, feed the bundle into a fresh `SavedStateHandle.createHandle()`, instantiate a new ViewModel, and assert that form inputs, active step indexes, and navigation tokens survive.
   - **On-Device Instrumentation Testing**: Use AndroidX `ActivityScenario`. Navigate through a flow, background the app, trigger process death via `adb shell am kill <package>`, bring the app foreground, and assert that the activity restores state without crashing.

2. **Testing Configuration Changes (Rotation)**:
   - In Compose tests or `ActivityScenario`, invoke `scenario.recreate()`. Assert that the screen rebinds to existing ViewModel state flows without re-triggering network fetches or resetting scroll offsets.

3. **Testing Dynamic Offline Transitions**:
   - Inject a `FakeNetworkMonitor` exposing a `Flow<Boolean>`. While collecting active UI flows, flip network availability to `false`. Assert that the UI renders an offline banner, falls back to cached Room records, and routes mutations to an internal pending outbox.

## Interview answer — deep senior

From an architectural systems perspective, handling process death exposes state boundaries:

1. **Transient UI State vs. Heavy Domain State**: A frequent architectural anti-pattern is storing large domain objects (such as complete 5MB JSON lists) in `SavedStateHandle`. Android restricts the system `TransactionTooLargeException` buffer to 1MB across the entire process. Tests must assert that only lightweight restoration keys (e.g., `selectedUserId: String`, `scrollIndex: Int`) are saved to state bundles.

2. **rememberSaveable Custom Savers**: In Jetpack Compose, test custom savers (`Saver<T, Any>`) by writing unit tests that serialize custom UI state objects to bundles and deserialize them, asserting object equivalence.

3. **Network Flakiness Injection via OkHttp**: Rather than relying on physical airplane mode toggles in CI, inject an OkHttp interceptor into the test network client that programmatically drops connections after the 2nd request, asserting that retry queues and offline outboxes trigger reliably.

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

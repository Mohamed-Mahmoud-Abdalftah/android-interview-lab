---
id: "AND-09"
question: "Compare ViewModel, SavedStateHandle, rememberSaveable, and persistent storage."
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "A"
phase: 1
priority: "P1"
order: 39
editorial_status: "reviewed"
---

# AND-09

## Original interview question

Compare ViewModel, SavedStateHandle, rememberSaveable, and persistent storage.

## What the interviewer evaluates

- Map each state mechanism to ownership, lifetime, size, and recovery guarantee.
- Avoid treating Bundle-backed state as durable business storage.
- Design one screen that restores correctly after rotation and system-initiated process death.

## Explanation in Arabic

المقارنة الشاملة بين أدوات حفظ الحالة الأربعة في أندرويد:

1. الـ `ViewModel`:
   - **مكان الحفظ:** في الذاكرة الحية (JVM Heap Memory).
   - **ماذا ينجو منه؟** ينجو من الـ Configuration Changes فقط.
   - **هل ينجو من Process Death؟** **لا!** يضيع بالكامل.
   - **الاستخدام:** البيانات الكبيرة، الـ UI State المعقد، والعمليات الجارية في `viewModelScope`.

2. الـ `SavedStateHandle`:
   - **مكان الحفظ:** في الـ OS System Server عبر `onSaveInstanceState` (Bundle Serialized).
   - **ماذا ينجو منه؟** ينجو من الـ Configuration Changes **وينجو من الـ Process Death**!
   - **حدوده:** محكوم بسعة الـ Binder Buffer (حوالي 50-100KB كحد أقصى للسلامة)؛ مخصص للمعرفات الصغيرة (IDs) والمدخلات النصية فقط.

3. الـ `rememberSaveable` (في Compose):
   - **مكان الحفظ:** في الـ `SaveableStateRegistry` المربوط بـ Bundle الـ Activity.
   - **ماذا ينجو منه؟** ينجو من الـ Configuration Changes و Process Death داخل واجهة Compose.
   - **الاستخدام:** حالة الـ UI المحلية الخاصة بـ Composable معين (مثل: هل القائمة مفتوحة، موضع الـ Scroll).

4. الـ Persistent Storage (Room / DataStore / Files):
   - **مكان الحفظ:** على القرص الصلب (Flash Storage / Disk).
   - **ماذا ينجو منه؟** ينجو من كل شيء: Process Death، إعادة تشغيل الهاتف، وإغلاق التطبيق لأسابيع.
   - **الاستخدام:** البيانات الحيوية، المقالات، التوكنز، والإعدادات الدائمة.

## Practical walkthrough

جدول مقارنة معماري واضح:
| المعيار | ViewModel | SavedStateHandle | rememberSaveable | Room / DataStore |
| :--- | :--- | :--- | :--- | :--- |
| **مكان التخزين** | RAM (Heap) | OS Bundle (Binder) | OS Bundle (Binder) | Disk (Flash) |
| **ينجو من التدوير؟** | نعم | نعم | نعم | نعم |
| **ينجو من Process Death؟** | لا | نعم | نعم | نعم |
| **ينجو من Reboot الجهاز؟** | لا | لا | لا | نعم |
| **السرعة** | فورية (O(1) memory) | سريعة (Serialization) | سريعة | أبطأ (Disk I/O) |
| **حدود الحجم** | حجم الـ Heap المتاح | < 50 KB | < 50 KB | جيجابايت |

## Why it matters and how it works

ViewModel is retained in memory across ordinary configuration recreation for its owner; it is not serialized. `SavedStateHandle` and `rememberSaveable` participate in saved-instance-state restoration, so they can reconstruct compact inputs after eligible system-initiated process death. Their save timing and Bundle size mean they are unsuitable for a large object graph, bitmap, or transaction history. Persistent storage is under the app's data layer and can survive process death and normal app restarts, subject to user deletion, storage errors, and backup policy. The server remains authoritative for remote operations.

## Worked example

In a product detail screen, keep `productId` in navigation/saved state, `selectedTab` in `rememberSaveable`, and fetched product UI state in a destination-scoped ViewModel. Cache products in Room if offline access is a requirement. On process recreation, rebuild the ViewModel, read the ID, and query the repository. This is a design example; whether a local cache is appropriate depends on freshness and data sensitivity.

## Trade-offs and decision criteria

ViewModel avoids refetching on rotation but costs memory. `rememberSaveable` is convenient for UI-only values; putting business rules in composables makes testing and ownership unclear. `SavedStateHandle` suits ViewModel reconstruction keys. Room suits structured durable records; DataStore suits small preferences, not relational queries. All saved-state APIs should hold small simple values, while durable storage needs migration and backup decisions.

## Failure modes

Saving a 10 MB image or response list in a Bundle can slow the main thread or exceed transaction limits. Keeping a draft only in ViewModel loses it when the process dies. Persisting a transient animation offset to Room creates unnecessary writes. Assuming saved state runs on every force-stop, finish, or crash leads to missing data. For payments, neither saved state nor a local flag proves server success; reconcile by operation ID.

## Production perspective

An offline-first note editor stores note content in Room after each debounced edit, keeps the current note ID in `SavedStateHandle`, and uses `rememberSaveable` for an expanded toolbar state. ViewModel combines the note stream and validation logic. Tests rotate, kill the background process, reopen the app, and simulate a failed disk write to verify the draft is either saved or visibly unsaved.

## Interview answer — short

ViewModel stores complex state in RAM across rotation but dies on process death; SavedStateHandle serializes lightweight IDs in OS Bundles to survive process death; rememberSaveable does the same for local Compose UI state; and Persistent Storage (Room/DataStore) saves arbitrary data to disk across app reboots.

## Interview answer — structured

These four state mechanisms represent distinct tiers across longevity, storage location, and size limits:

1. **`ViewModel`**: Resides in RAM heap. Survives configuration changes, but is completely destroyed upon process death. Ideal for rich domain models, complex UI states, and active coroutine streams.

2. **`SavedStateHandle`**: Integrated into the ViewModel, backed by Android's `onSaveInstanceState` Bundle in the OS system server. Survives both configuration change and process death. Strictly bounded by Binder IPC limits (<50KB), ideal for saving navigation arguments, active search text, and record IDs.

3. **`rememberSaveable`**: Compose's UI-layer equivalent of `SavedStateHandle`. Restores transient Composable UI state (scroll positions, expanded dropdown flags, tab indices) across rotation and process death.

4. **Persistent Storage (Room / DataStore)**: Written directly to flash storage on disk. Survives process death, device reboots, and app updates. Used for domain databases, offline caching, and user authentication credentials.

## Interview answer — deep senior

Architecturally, a well-engineered screen orchestrates all four in harmony:

```kotlin
class OrderViewModel(savedStateHandle: SavedStateHandle, repository: OrderRepository) : ViewModel() {
    // 1. SavedStateHandle: يسترجع ID الطلب بعد process death بأمان:
    private val orderId: String = checkNotNull(savedStateHandle["order_id"])
    
    // 2. Room (Persistent Storage): جلب بيانات الطلب من الديسك:
    // 3. ViewModel: حفظ الـ StateFlow في الرام أثناء التدوير:
    val orderState: StateFlow<OrderUiState> = repository.observeOrder(orderId)
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), OrderUiState.Loading)
}
```

In Compose, `rememberSaveable` manages the local UI scroll state, `SavedStateHandle` tracks the screen's core query, `ViewModel` manages the active stream, and `Room` provides the durable data.

## How to answer in the interview

- **Why:** UI state has different survival and correctness requirements.
- **How:** Place ephemeral composition state, saveable UI element state, ViewModel logic, and durable data in their scopes.
- **Trade-offs:** Save IDs rather than large objects; reload data when freshness matters.
- **Failure cases:** Name process-death loss and stale account-specific data.
- **Production solution:** Restore product ID/tab and re-query the repository with authorization checks.

## Deep-dive talking points

Discuss ViewModelStore retention, Bundle size and save timing, business versus UI state ownership, Room versus DataStore, and how backup and process termination alter recovery assumptions.

## Follow-up questions

- **Interviewer:** "What error occurs if you put too much data in `SavedStateHandle`?"
  **Answer:** "`TransactionTooLargeException`. The Android Binder buffer is shared across all inter-process communications with a maximum limit of approximately 1MB total. Storing large lists in SavedStateHandle causes immediate crashes."

- **Interviewer:** "Can custom objects be saved in `SavedStateHandle`?"
  **Answer:** "Yes, if they implement `Parcelable` or `Serializable`, or by providing a custom `SavedStateRegistry.AutoSavedStateProvider`."

- **Interviewer:** "How does `rememberSaveable` handle custom classes in Compose?"
  **Answer:** "By providing a custom `Saver` object: `rememberSaveable(stateSaver = MyCustomSaver) { mutableStateOf(MyObject()) }`."

## Self-check rubric

Compare all four tools by owner and lifetime; choose a home for product ID, selected tab, fetched list, and note draft; describe a Bundle size risk; and explain how to recover after process death.

## References and reviewed-on date

- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — saved state, ViewModel, and durable storage boundaries.
- [ViewModel overview](https://developer.android.com/topic/libraries/architecture/viewmodel) — screen state ownership.

Technically reviewed against primary documentation on 2026-10-13.

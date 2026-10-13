---
id: "AND-06"
question: "What are configuration changes, and what survives them?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "A"
phase: 1
priority: "P1"
order: 36
editorial_status: "reviewed"
---

# AND-06

## Original interview question

What are configuration changes, and what survives them?

## What the interviewer evaluates

- Distinguish recreation of an Activity instance from death of the app process.
- Place transient screen state, small restorable state, and durable data in the right owners.
- Test rotation, resizing, locale changes, and night mode without assuming a particular callback order is a persistence contract.

## Explanation in Arabic

الـconfiguration change هو تغيّر في ظروف عرض التطبيق، زي rotation أو تغيير اللغة أو حجم النافذة أو night mode. الـAndroid غالبًا بيعيد إنشاء الـActivity علشان يحمّل resources المناسبة؛ الـobject القديم وحقوله العادية بيروحوا. الـprocess نفسه غالبًا لسه عايش، فـViewModel المرتبط بالـscreen بيكمل مع الـActivity الجديدة. حالة صغيرة قابلة للتسلسل، زي selected tab أو draft text، ممكن ترجع من saved state. أما بيانات الطلب أو نتيجة الدفع فلازم تتخزن تخزين دائم أو تُستعاد من مصدر موثوق. ماينفعش تقول إن ViewModel وحده بيحمي من process death: وقتها ذاكرته كلها بتروح.

## Why it matters and how it works

Android can destroy the current Activity and create a new instance with resources matching the new configuration. A ViewModel scoped to the retained ViewModelStoreOwner survives an ordinary configuration recreation, but Activity fields, view references, and unowned jobs do not. `SavedStateHandle` or `rememberSaveable` stores a small serializable reconstruction key across eligible system-initiated recreation; Room or another durable store owns data that must outlive a task or process. The saved-state callback is not a transaction log and is not guaranteed for every exit path.

## Worked example

In a search screen, keep the current query in `SavedStateHandle`, derive results from a repository, and collect UI state with the lifecycle. The ViewModel is recreated with the saved query after eligible process restoration; the repository reloads results. This is illustrative Android code with Lifecycle and ViewModel SavedState dependencies and an application-provided `SearchRepository`.

```kotlin
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class SearchViewModel(
    private val savedState: SavedStateHandle,
    private val repository: SearchRepository
) : ViewModel() {
    private val mutableResults = MutableStateFlow<List<SearchResult>>(emptyList())
    val results = mutableResults.asStateFlow()
    val query: String get() = savedState["query"] ?: ""

    fun search(value: String) {
        savedState["query"] = value
        viewModelScope.launch { mutableResults.value = repository.search(value) }
    }
}
```

The surrounding app supplies `SearchRepository` and `SearchResult`; competing searches need cancellation or `flatMapLatest` if stale results are possible. The example illustrates ownership, not a complete search feature.

## Practical walkthrough

rotation أو تغيير locale/font size ممكن يخلق Activity جديدة؛ الـViewModel المرتبط بالـscope المناسب غالبًا يبقى عبر configuration recreation، لكن الـviews وActivity نفسها تتبني من جديد. `SavedStateHandle` ينفع لـquery أو item ID صغير، مش result list كبيرة. بعد process death ViewModel جديدة تتولد وتقرأ saved key إن state اتسجلت، وبعدين repository تعيد البيانات. متعتمدش على object في memory لو user كتب draft مهم؛ احفظه بشكل durable قبل ما تقول له Saved. اختبر resize والـrotation مع loading في النص، وشوف old Activity ما اتسربتش.

## Trade-offs and decision criteria

Retaining a ViewModel avoids needless reloads and preserves screen logic during rotation, but it consumes memory and cannot survive process death. Saved state is suitable for small reconstruction inputs, not large lists or bitmaps. Durable storage costs I/O but is appropriate for user data and operation records. Opting out of Activity recreation with `configChanges` shifts resource updating onto the app and is rarely a substitute for correct state ownership.

## Failure modes

A developer stores a payment attempt only in an Activity field; rotation loses the attempt and a new screen sends a second charge. Persist the attempt ID and ask the backend for its status before retrying. Another failure is retaining the old Activity in a ViewModel or singleton, leaking views and resources across recreation. Holding a bitmap in saved state can also create oversized Bundles and slow restoration.

## Production perspective

For a checkout screen, persist the server operation ID and user-entered draft separately. On recreation, render the draft from saved state and rehydrate payment state from the persisted operation and server. Instrument recreation tests with rotation, locale/night mode, and background process termination. Trace duplicate submissions and state restoration failures by operation ID without logging payment credentials.

## Interview answer — short

“A configuration change is a change such as rotation, locale, or window size that normally recreates an Activity. Its ordinary fields and views are lost. A correctly scoped ViewModel survives that recreation; small saved state can restore UI inputs, while important data belongs in durable storage. Process death is a separate case.”

## Interview answer — structured

Android often destroys and recreates an Activity to apply new configuration resources. I keep screen logic in a ViewModel, small reconstruction keys in SavedStateHandle or rememberSaveable, and business data in a repository backed by durable storage. The new Activity observes the same retained ViewModel in an ordinary configuration change. I still design restoration after process death because the ViewModel will not survive that. I test resizing and rotation and avoid keeping references to the old Activity.

## Interview answer — deep senior

The important boundary is the owner of each piece of state. Configuration recreation replaces Activity and view instances while the process generally remains alive, so the ViewModelStore can retain a ViewModel. Saved-state APIs capture compact serializable inputs for eligible recreation, but their timing and size make them unsuitable as a ledger. For a checkout, I persist an operation ID before issuing a request, restore a draft separately, and reconcile with the server after a restart. I also check that callbacks, listeners, and repository jobs do not retain the destroyed UI, and test rotation, multi-window resizing, locale, and a real process kill. When rotation or locale changes, Android can replace Activity and resources while keeping the process and ViewModelStore.

If a search screen rotates mid-request, the Activity and view hierarchy are recreated, and the new view should collect from the retained ViewModel rather than restart an accidental duplicate request. I save only a small query or item ID in `SavedStateHandle`; the result list comes from the repository. If the process later dies, a new ViewModel reconstructs state from that key and reloads. A draft that the user expects never to lose requires durable storage before showing “Saved.” I verify rotation, locale change, and resize separately because they exercise layout and resource behavior differently.

## How to answer in the interview

- **Why:** The system can recreate UI for resource/configuration changes.
- **How:** Distinguish new Activity/views from retained scoped ViewModel and saved small keys.
- **Trade-offs:** Put transient UI position in saved state, durable draft data in storage.
- **Failure cases:** Mention stale Activity references and oversized Bundles.
- **Production solution:** Restore a search query, reload results, and test rotation during loading.

## Deep-dive talking points

Discuss Activity recreation versus manual configuration handling, resource qualifier selection, ViewModelStore ownership, saved-state size/timing, and why an external operation requires durable identity. Explain how a recreation test differs from a process-death test.

## Follow-up questions

- [AND-07](../and-07/): Does a ViewModel survive process death? **Answer:** no; restore small keys from saved state and reload durable data.
- [AND-09](../and-09/): Where should a large result list live? **Answer:** in a repository/cache; save its query or ID, not the whole list in a Bundle.
- [AND-18](../and-18/): Does multi-window always mean a rotation? **Answer:** no; it can alter size and lifecycle visibility independently, so test the actual callbacks and window constraints.

## Self-check rubric

Explain one configuration change and its recreation effect; name what a ViewModel, saved state, and durable store each preserve; identify a stale Activity reference; design a checkout restoration path; and distinguish process-death testing from rotation testing.

## References and reviewed-on date

- [Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle) — Activity recreation and process state.
- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — saved-state boundaries and size guidance.
- [ViewModel overview](https://developer.android.com/topic/libraries/architecture/viewmodel) — scope and configuration retention.

Technically reviewed against these primary sources on 2026-10-13 by editorial review. The Android snippet is illustrative and was not device-compiled.

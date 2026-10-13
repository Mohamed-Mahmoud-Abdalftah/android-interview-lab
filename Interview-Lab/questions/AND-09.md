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

الأربع أدوات مش بدائل متطابقة. الـViewModel بيحتفظ بـscreen logic وstate في memory أثناء configuration change، لكن بيختفي مع process death. `SavedStateHandle` جوه ViewModel بيحفظ قيم صغيرة تساعده يعيد بناء الحالة لما النظام يرجّع الشاشة. `rememberSaveable` مناسب لحالة UI محلية في Compose، زي tab أو input بسيط، وبيستخدم saved-state mechanism تحت الغطاء. التخزين الدائم زي Room أو DataStore بيحفظ بيانات المستخدم بعد غلق التطبيق أو موت الـprocess، لكن له تكلفة I/O وإدارة schema. احفظ ID أو query صغيرة في saved state، وحمّل المحتوى الكبير من مصدر دائم.

## Why it matters and how it works

ViewModel is retained in memory across ordinary configuration recreation for its owner; it is not serialized. `SavedStateHandle` and `rememberSaveable` participate in saved-instance-state restoration, so they can reconstruct compact inputs after eligible system-initiated process death. Their save timing and Bundle size mean they are unsuitable for a large object graph, bitmap, or transaction history. Persistent storage is under the app's data layer and can survive process death and normal app restarts, subject to user deletion, storage errors, and backup policy. The server remains authoritative for remote operations.

## Worked example

In a product detail screen, keep `productId` in navigation/saved state, `selectedTab` in `rememberSaveable`, and fetched product UI state in a destination-scoped ViewModel. Cache products in Room if offline access is a requirement. On process recreation, rebuild the ViewModel, read the ID, and query the repository. This is a design example; whether a local cache is appropriate depends on freshness and data sensitivity.

## Practical walkthrough

في product page، `rememberSaveable` تحفظ selected tab/scroll الصغير طالما نوعه saveable، والـViewModel تملك data fetching وscreen state على navigation scope. `SavedStateHandle` تحفظ `productId` أو query صغير تحتاجه ViewModel بعد restore. Room أو server يبقى source of truth للproduct نفسه لما correctness/offline مطلوب؛ لا تخزن object كبير في Bundle. `remember` وحدها بس داخل composition الحالية، وViewModel ما تنجو من process death. لو item اتحذف أو user اتسجل خروج أثناء غياب app، restoration لازم تعرض missing/unauthorized بدل stale product.

## Trade-offs and decision criteria

ViewModel avoids refetching on rotation but costs memory. `rememberSaveable` is convenient for UI-only values; putting business rules in composables makes testing and ownership unclear. `SavedStateHandle` suits ViewModel reconstruction keys. Room suits structured durable records; DataStore suits small preferences, not relational queries. All saved-state APIs should hold small simple values, while durable storage needs migration and backup decisions.

## Failure modes

Saving a 10 MB image or response list in a Bundle can slow the main thread or exceed transaction limits. Keeping a draft only in ViewModel loses it when the process dies. Persisting a transient animation offset to Room creates unnecessary writes. Assuming saved state runs on every force-stop, finish, or crash leads to missing data. For payments, neither saved state nor a local flag proves server success; reconcile by operation ID.

## Production perspective

An offline-first note editor stores note content in Room after each debounced edit, keeps the current note ID in `SavedStateHandle`, and uses `rememberSaveable` for an expanded toolbar state. ViewModel combines the note stream and validation logic. Tests rotate, kill the background process, reopen the app, and simulate a failed disk write to verify the draft is either saved or visibly unsaved.

## Interview answer — short

“ViewModel keeps screen logic and state in memory across configuration changes. SavedStateHandle stores small ViewModel reconstruction values; rememberSaveable does the same for local Compose UI state. Persistent storage holds data that must survive process death and future launches. I save IDs and small inputs, not large objects, in saved state.”

## Interview answer — structured

I choose by lifetime and owner. ViewModel is the screen's in-memory state holder and survives rotation, but not process death. SavedStateHandle carries compact keys into a recreated ViewModel, and rememberSaveable handles small composable-local UI values. Room or DataStore belongs to the data layer for durable content. For a product page I save the product ID and selected tab, then reload the product from a repository.

## Interview answer — deep senior

The distinction is retention versus reconstruction versus durability. ViewModel retention works while the owner is recreated in the same process. SavedStateHandle and rememberSaveable serialize limited UI inputs at saved-state lifecycle points; they are backup mechanisms, not guaranteed databases. A durable store survives process loss and normal restarts, but its schema, transaction boundaries, encryption and backup policy require design. For a note editor I persist the draft to Room, save only its ID and cosmetic UI state in saved state, then reconstruct streams and repository state after restart. For server actions I reconcile with the backend rather than trusting any client-side flag.

The distinction matters during account switching and process recreation. A saveable tab index is harmless to restore, but a cached product object may be stale, too large for the saved-state Bundle, or belong to a previous account. I restore the small product ID, query the repository under the current user, and let the ViewModel rebuild screen state. If offline display is required, a persistent cache needs freshness and access rules; it is not automatically justified by state restoration. I test route restoration with deleted products and signed-out users, not only the happy path.

## How to answer in the interview

- **Why:** UI state has different survival and correctness requirements.
- **How:** Place ephemeral composition state, saveable UI element state, ViewModel logic, and durable data in their scopes.
- **Trade-offs:** Save IDs rather than large objects; reload data when freshness matters.
- **Failure cases:** Name process-death loss and stale account-specific data.
- **Production solution:** Restore product ID/tab and re-query the repository with authorization checks.

## Deep-dive talking points

Discuss ViewModelStore retention, Bundle size and save timing, business versus UI state ownership, Room versus DataStore, and how backup and process termination alter recovery assumptions.

## Follow-up questions

- [AND-06](../and-06/): Which state survives rotation without serialization? **Answer:** a correctly scoped ViewModel's in-memory state.
- [AND-07](../and-07/): Which of these is a transaction ledger after process death? **Answer:** durable storage can record local operations, while the server decides remote transaction status.
- [COM-05](../com-05/): Does `rememberSaveable` make a large list persistent? **Answer:** no; it saves compact UI state through the saved-state mechanism.

## Self-check rubric

Compare all four tools by owner and lifetime; choose a home for product ID, selected tab, fetched list, and note draft; describe a Bundle size risk; and explain how to recover after process death.

## References and reviewed-on date

- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — saved state, ViewModel, and durable storage boundaries.
- [ViewModel overview](https://developer.android.com/topic/libraries/architecture/viewmodel) — screen state ownership.

Technically reviewed against these primary sources on 2026-10-13 by editorial review. The note-editor example is architectural and was not device-tested.

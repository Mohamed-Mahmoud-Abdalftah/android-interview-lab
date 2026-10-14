---
id: "COM-05"
question: "Compare remember, rememberSaveable, and ViewModel state."
topic: "Jetpack Compose"
code: "COM"
group: "A"
phase: 3
priority: "P1"
order: 234
editorial_status: "reviewed"
---

# COM-05

## Original interview question

Compare remember, rememberSaveable, and ViewModel state.

## What the interviewer evaluates

- Map each state holder to its lifetime and owner.
- Explain process-death restoration without claiming a ViewModel survives it.
- Keep saved bundles small and reload heavy data.

## Explanation in Arabic

المقارنة الشاملة بين `remember` و `rememberSaveable` وحالة الـ `ViewModel` ومتى تستخدم كلاً منها:

1. دالة `remember { ... }`:
   - **نطاق البقاء (Lifetime)**: تعيش فقط طالما أن الـ Composable موجود داخل شجرة الـ Composition.
   - **ما تحميه**: تحمي القيمة من الضياع أثناء **Recomposition** العادي.
   - **ما تفقده**: تُفقد وتُعاد تهيئتها بالكامل عند **تغيير اتجاه الشاشة (Configuration Change)** أو موت العملية (Process Death) أو مغادرة الشاشة في الـ Navigation.
   - **الاستخدام المثالي**: العمليات الحسابية المؤقتة للـ UI، كائنات التنسيق `remember { SimpleDateFormat(...) }`، وحالات الرسوم المتحركة المؤقتة.

2. دالة `rememberSaveable { ... }`:
   - **نطاق البقاء**: تعيش عبر الـ Recomposition **وتنجو أيضاً من Configuration Change وموت العملية (Process Death)**!
   - **كيف تعمل**: تخزن البيانات في `SavedStateHandle` / `Bundle` الخاص بالنظام، وتشترط أن تكون البيانات قابلة للـ Serialization (مثل Primitives أو Parcelable أو عبر Custom Saver).
   - **الاستخدام المثالي**: مدخلات المستخدم غير المحفوظة في السيرفر (نص مسودة في حقل بحث، موضع التمرير المحدد، رقم التبويب النشط).

3. حالة الـ `ViewModel` (`StateFlow` / `SavedStateHandle`):
   - **نطاق البقاء**: تعيش طوال فترة بقاء الشاشة في الـ BackStack، وتنجو من Configuration Change بالكامل، وتنجو من Process Death عبر `SavedStateHandle`.
   - **الاستخدام المثالي**: حالة العمل الحقيقية للتطبيق (Business State)، استجابات الشبكة، بيانات المستخدم، وقواعد التحقق.

## Practical walkthrough

أمثلة توضح متى نستخدم كل آلية في شاشة تطبيق حقيقية:
```kotlin
@Composable
fun CheckoutScreen(viewModel: CheckoutViewModel = viewModel()) {
    // 1. ViewModel State: بيانات الـ Business والـ Backend تنجو من التدوير والـ Navigation:
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    // 2. rememberSaveable: حالة واجهة مستخدم خاصة بالشاشة تنجو من تدوير الهاتف وموت العملية:
    var promoCodeInput by rememberSaveable { mutableStateOf("") }

    // 3. remember: كائن مؤقت خاص بالرسم أو الحسابات يضيع عند التدوير ويعاد إنشاؤه بسهولة:
    val currencyFormatter = remember(Locale.getDefault()) {
        NumberFormat.getCurrencyInstance(Locale.getDefault())
    }

    CheckoutContent(
        total = currencyFormatter.format(uiState.totalAmount),
        promoCode = promoCodeInput,
        onPromoChange = { promoCodeInput = it }
    )
}
```

## Why it matters and how it works

Compose remembers values by composition position and keys. Saveable state uses a registry and Bundle-compatible saving path rather than durable database persistence. A ViewModel has an owner lifecycle independent of individual composable invocations, making it suitable for screen decisions and asynchronous work. After system process death the ViewModel instance is recreated; only saved identifiers or durable storage can restore its meaningful state.

## Worked example

A search screen keeps an expanded-filter chip locally with `rememberSaveable`, while a ViewModel owns the query and result loading because query changes drive repository work. It stores the query or a route ID in `SavedStateHandle` and reloads results after recreation. A temporary animation flag can use `remember` if losing it on recreation is harmless.

### Compose/Kotlin walkthrough

```kotlin
// UI-only selection; saveable for eligible system restoration.
@Composable
fun CatalogTabs() {
    var selected by rememberSaveable { mutableIntStateOf(0) }
    TabRow(selectedTabIndex = selected) {
        listOf("All", "Saved").forEachIndexed { index, label ->
            Tab(selected = index == selected, onClick = { selected = index }, text = { Text(label) })
        }
    }
}
// ViewModel: val productId = checkNotNull(savedStateHandle["productId"] as String?)
```

## Trade-offs and decision criteria

Local state reduces architectural plumbing; ViewModel state improves sharing and business-rule testing. Saveable values carry serialization/size costs and are not a database. A ViewModel survives rotation but needs explicit recovery for process death. Choose by ownership first, then restoration semantics.

## Failure modes

Remembered form text disappears at rotation. A ViewModel is assumed immortal and shows an empty screen after process death. A huge object is placed in saved state and risks transaction-size errors. Two copies of query state diverge between UI and ViewModel.

## Production perspective

Classify each field as ephemeral UI, restorable UI, or business state; document its owner and reload source. Exercise rotation and system recreation, including missing/stale IDs, rather than relying on a happy-path preview.

## Interview answer — short

`remember` preserves state across recompositions but resets on configuration change. `rememberSaveable` survives configuration change and process death by persisting values into the Android `Bundle`. ViewModel state outlives configuration change and hosts business logic, persisting across backstack navigation until the screen is permanently destroyed.

## Interview answer — structured

Choosing between `remember`, `rememberSaveable`, and `ViewModel` depends strictly on lifecycle scope and state ownership.

First, with remember, retains an object in the Slot Table across **recomposition passes** as long as the composable remains in the composition tree. However, it is wiped on configuration changes (screen rotations) and process death. It is designed for ephemeral UI calculations, such as expensive formatting objects, scroll state listeners, or animation progress. Next, with rememberSaveable, preserves state across recomposition *and* **configuration changes and system-initiated process death**. It automatically serializes data into the Android `Bundle` using a `Saver` implementation. It is ideal for transient, UI-only user input like uncommitted text fields, active tab indexes, or accordion expansion states.
Finally, with ViewModel State, scoped to the `ViewModelStoreOwner` (surviving configuration changes and backstack journeys). It holds business state, coordinates with repositories and network layers, and survives process death when paired with `SavedStateHandle`. Business logic and server-driven state should always reside here.


## Interview answer — deep senior

Under the hood, `rememberSaveable` delegates to Compose's `SaveableStateRegistry`. When the OS destroys an Activity to reclaim memory, `SaveableStateRegistry` collects registered values into the saved instance state Bundle. If you store custom data classes inside `rememberSaveable`, you must provide a custom `Saver` (e.g. `listSaver` or `mapSaver`) or mark the class `@Parcelize Parcelable`; storing non-parcelable types crashes at runtime with an `IllegalArgumentException`.

Conversely, storing everything in the `ViewModel` is an anti-pattern known as *State Bloat*. Fine-grained UI behaviors (like whether a tooltip is currently visible or an animation state) clutter the domain model and break composable encapsulation. Senior architects establish a clean boundary: pure UI transient state stays in `remember`/`rememberSaveable`, while actionable domain data belongs in the ViewModel.


## How to answer in the interview

- **Why:** each holder survives a different lifetime.
- **How:** map ephemeral UI, saveable UI, and business state to their owners.
- **Trade-off:** saved state is small and conditional on platform restoration.
- **Failure case:** assuming a ViewModel instance survives process death.
- **Production solution:** persist identifiers and reload authoritative data.

## Deep-dive talking points

Compare composition lifetime, saved-state registry, ViewModel ownership, process death, and Bundle size.

## Follow-up questions

- **Interviewer:** "What happens if you put a non-Parcelable object into `rememberSaveable`?"
  **Answer:** "It will work during normal recomposition, but as soon as a configuration change or process death triggers state saving into the Android Bundle, the app crashes with an `IllegalArgumentException: ... cannot be saved using the current SaveableStateRegistry`."

- **Interviewer:** "How do you create a custom Saver for a non-Parcelable class?"
  **Answer:** "Using `listSaver(save = { listOf(it.id, it.name) }, restore = { MyClass(it[0], it[1]) })` or `mapSaver`, defining explicit serialization and deserialization steps into supported primitive types."

## Self-check rubric

Assign three example values to owners, explain rotation and process death, and avoid a duplicate source of truth.

## References and reviewed-on date

- [Save UI state in Compose](https://developer.android.com/develop/ui/compose/state-saving) — lifetime and small saved values.
- [Where to hoist state](https://developer.android.com/develop/ui/compose/state-hoisting) — owner choice.

Technically reviewed against primary documentation on 2026-10-13.

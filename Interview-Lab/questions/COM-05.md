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

## Concept and technical explanation

In Jetpack Compose, state lifecycle management is divided across three distinct retention scopes: remember, rememberSaveable, and ViewModel state. remember retains state exclusively across recompositions within a single composition lifecycle, resetting whenever the composable leaves the tree or during configuration changes (such as screen rotation). rememberSaveable extends this by automatically persisting state into the Android SavedInstanceState bundle, surviving configuration changes and system-initiated process death for Parcelable or primitive data. ViewModel state provides the longest lifecycle, living across configuration changes and process death (via SavedStateHandle) while retaining business logic and surviving navigation backstack transitions.

## Practical walkthrough (English)

Contrasting the three state survival mechanisms in an Android screen:
```kotlin
@Composable
fun RegistrationScreen(viewModel: RegistrationViewModel = hiltViewModel()) {
    // 1. remember: Survives recomposition ONLY. Resets on screen rotation!
    // Best for: Ephemeral animation flags, scroll states, local UI toggles
    var isPasswordVisible by remember { mutableStateOf(false) }

    // 2. rememberSaveable: Survives recomposition AND configuration changes AND process death!
    // Best for: User draft inputs, expanded card states, temporary form values
    var enteredUsername by rememberSaveable { mutableStateOf("") }

    // 3. ViewModel State: Survives recomposition, configuration changes, and navigation graph transitions!
    // Best for: Business domain data, async network states, multi-repository orchestration
    val registrationState by viewModel.uiState.collectAsStateWithLifecycle()

    RegistrationContent(
        username = enteredUsername,
        onUsernameChange = { enteredUsername = it },
        isPasswordVisible = isPasswordVisible,
        onTogglePassword = { isPasswordVisible = !isPasswordVisible },
        state = registrationState
    )
}
```

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

remember retains state across recompositions, but completely resets on screen rotation or when leaving the composition. rememberSaveable survives recompositions, configuration changes, and process death by saving state into the Android SavedStateRegistry bundle using Parcelize or custom Savers. ViewModel state lives completely outside the composition lifecycle, surviving screen rotations and maintaining business data across screen transitions, backed by SavedStateHandle for process death restoration.

## Interview answer — structured

Choosing the correct state persistence mechanism in Jetpack Compose requires understanding their lifecycles, storage mediums, and architectural scopes.
remember is the most localized and ephemeral mechanism. It stores a value in the Compose SlotTable at the call site. The value persists across recompositions as long as the composable remains in the composition tree. However, because it resides purely in memory tied to the Activity window, it is wiped out during configuration changes like screen rotations. It is ideal for transient UI effects, like animation toggles or temporary dropdown expansions.
rememberSaveable builds upon remember by registering the value with the Android Activity's SavedStateRegistry. Upon configuration change or system process death, Compose bundles the value into the saved instance state, restoring it when the screen recreates. Values must be primitives, Bundle-compatible, or implement Parcelable. It is ideal for user form inputs and draft text.
ViewModel state represents the highest tier of architecture. ViewModels survive configuration changes natively through Android Architecture Components, living until the backstack entry is popped. They are decoupled from Android UI classes, can be tested purely on the JVM, and interact with Domain UseCases. Backed by SavedStateHandle, ViewModel state survives process death, making it the required home for all business-critical domain data.

## Interview answer — deep senior

Under the hood, these three mechanisms map to fundamentally distinct memory structures and lifecycle registries within the Android operating system.
remember allocates a slot directly within the current Composer's SlotTable array. During recomposition, Compose reads the slot at the matching code offset. When the Activity recreates due to an orientation change, the entire ComposeView and its associated SlotTable are garbage collected, explaining why remember immediately loses state.
rememberSaveable bridges Compose to the platform SavedStateRegistryOwner (typically the ComponentActivity or NavBackStackEntry). It utilizes a Saver implementation (auto-inferred or explicitly provided via listSaver or mapSaver) to serialize the value into a platform Bundle before Android's onSaveInstanceState() fires.
Because Bundles are marshaled across the Binder IPC boundary to the OS system_server process during process death, rememberSaveable enforces strict size limits: storing massive lists or Bitmaps here triggers TransactionTooLargeException crashes.
ViewModel state resides in the ViewModelStoreOwner, maintained by the non-configuration instance mechanism in the platform. The ViewModel instance itself remains intact in heap memory across Activity destruction and recreation, eliminating serialization overhead for domain models.
For process death resilience, ViewModels inject SavedStateHandle, which internally hooks into the exact same SavedStateRegistry as rememberSaveable.
Senior architects maintain strict separation of concerns: remember handles transient UI mechanics, rememberSaveable handles screen-level form inputs, and ViewModel state drives core business domain workflows.

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

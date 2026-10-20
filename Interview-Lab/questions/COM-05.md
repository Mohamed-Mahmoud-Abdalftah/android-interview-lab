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

`remember` retains a value while its call remains in the composition. `rememberSaveable` adds saving through the local saveable-state registry, commonly backed by Android saved instance state, so a small supported value can be restored after eligible activity or system process recreation. It does not provide durable persistence after user dismissal or every app termination. A ViewModel is scoped to its owner and survives configuration recreation while that owner remains; the instance does not survive process death. `SavedStateHandle` can restore small UI element state used to reconstruct ViewModel state, while large or authoritative data should be reloaded from persistent storage.

## Practical walkthrough (English)

Contrasting the three state survival mechanisms in an Android screen:
```kotlin
@Composable
fun RegistrationScreen(viewModel: RegistrationViewModel = hiltViewModel()) {
    // 1. remember: retained while this call remains in the composition.
    // This ephemeral visibility flag may reset after activity recreation.
    var isPasswordVisible by remember { mutableStateOf(false) }

    // 2. rememberSaveable: saves a small supported value for eligible recreation.
    // It is not durable storage after every kind of process termination.
    var enteredUsername by rememberSaveable { mutableStateOf("") }

    // 3. ViewModel: scoped to its owner; survives configuration recreation.
    // A new ViewModel must rebuild state after system process death.
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

اختيار المكان اللي الحالة تعيش فيه يبدأ بالسؤال: مين مالكها، وإيه اللي لازم يحصل لو الشاشة اتخلقت من جديد؟

- `remember` بيحفظ القيمة طول ما موضع الاستدعاء موجود في الـ Composition. ينفع لحالة مؤقتة زي ظهور عنصر، وبيضيع عادةً لو الـ Activity اتعملت من جديد أو العنصر خرج من الشجرة.
- `rememberSaveable` بيضيف مسار حفظ عبر `SaveableStateRegistry`؛ على Android ده عادةً مرتبط بـ saved instance state. يقدر يرجع قيمة صغيرة مدعومة أو قيمة ليها `Saver` بعد تدوير الشاشة أو **system-initiated process death** لما النظام يرجع نفس المهمة بحالتها. مش قاعدة بيانات، ومش ضمان بعد ما المستخدم يقفل المهمة بنفسه.
- الـ `ViewModel` عمره مرتبط بالـ `ViewModelStoreOwner`، زي destination أو Activity حسب طريقة إنشائه. نفس الـ instance بيكمل عبر configuration change، لكن بيتخلق من جديد بعد process death. `SavedStateHandle` بيرجع مفاتيح صغيرة زي `productId` أو نص فلتر؛ بعدها الـ ViewModel يعيد تحميل البيانات من الـ repository. لا تخزن response كبير في الـ Bundle.

التدوير، الخروج من الـ back stack، والقتل بواسطة النظام حالات مختلفة. اختبر اللي يهم المنتج على جهاز أو emulator، وحدد مسار إعادة التحميل بدل القول إن أي واحدة من الأدوات "بتحفظ كل البيانات".

## Practical walkthrough

في شاشة منتج، خزّن معرّف المنتج القابل للاسترجاع وأعد تحميل البيانات بعد إنشاء الـ ViewModel:
```kotlin
@Composable
fun ProductRoute(viewModel: ProductViewModel) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    var detailsExpanded by rememberSaveable { mutableStateOf(false) }
    var pressed by remember { mutableStateOf(false) }
    ProductContent(
        state = uiState,
        expanded = detailsExpanded,
        onExpand = { detailsExpanded = !detailsExpanded },
        pressed = pressed,
        onPress = { pressed = true }
    )
}
// ViewModel: اقرأ productId من SavedStateHandle ثم حمّل المنتج من repository.
```

`remember` هنا لحركة مؤقتة؛ `rememberSaveable` لتفضيل صغير؛ ومصدر بيانات المنتج يفضل الـ repository. المثال توضيحي وبيعتمد على وجود `ProductContent` و`ProductViewModel` في التطبيق.

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

`remember` survives recomposition while its call remains in composition. `rememberSaveable` also saves small supported values for eligible activity or system process recreation. A ViewModel survives configuration changes within its owner's scope, but its instance dies with the process; use `SavedStateHandle` for small restoration inputs and reload authoritative data.

## Interview answer — structured

I choose by owner and restoration need. `remember` caches a value at a composition call site. It is appropriate for ephemeral UI state that can reset after recreation. `rememberSaveable` uses a saveable-state registry and a `Saver` or supported Bundle-compatible value to restore small UI state when Android recreates an eligible activity or process. It should hold text, selection or an ID, not a large network result. A `ViewModel` belongs to a `ViewModelStoreOwner`, often a navigation destination. Its instance survives configuration change while that owner remains, and is cleared when the owner is removed. It does not survive system process death. `SavedStateHandle` can restore small inputs into a new ViewModel, which can then rebuild screen state from a repository. User dismissal or force-stop is not the same restoration path. For a product screen, keep the product ID in saved state and fetch the product again. Test rotation and system recreation separately; avoid maintaining two writable copies of the same query.

## Interview answer — deep senior

The three APIs solve different lifetime problems. `remember` associates a calculated value with a composition call position and optional keys. Recomposition can reuse it, but removing that call from composition generally removes its remembered value. It is not a process persistence mechanism. `rememberSaveable` layers a saver and saveable-state registry over composition memory. In Android hosts this can participate in saved instance state, which is meant for small transient UI state. Supported types and custom `Saver` contracts determine what can be stored. The saved-state path is conditional on lifecycle and task restoration, so saying it always survives process death is too broad.

A `ViewModel` has a different owner: an Activity, Fragment or navigation back-stack entry depending on creation. Its instance survives a configuration recreation while the owner retains its store. When the process is killed, that instance and in-memory `StateFlow` are gone. A new instance can read small values from `SavedStateHandle`, which also uses saved-state infrastructure; it should use a stable ID to reload large or authoritative screen data from a repository or database. Do not serialize a full product catalog into a Bundle. There is no universal fixed safe number of bytes per value because saved state shares transaction limits with other app state.

For a draft checkout screen, I might keep a local expanded panel in `rememberSaveable`, move a business-relevant promo code into a ViewModel if it affects validation, save only the code or cart ID in `SavedStateHandle`, and reload totals. I verify configuration recreation, system-initiated process recreation and leaving the destination as separate scenarios. I also check whether the state holder's owner scope is correct so that one navigation entry does not leak data into another.

## How to answer in the interview

- **Why:** each holder survives a different lifetime.
- **How:** map ephemeral UI, saveable UI, and business state to their owners.
- **Trade-off:** saved state is small and conditional on platform restoration.
- **Failure case:** assuming a ViewModel instance survives process death.
- **Production solution:** persist identifiers and reload authoritative data.

## Deep-dive talking points

Compare composition lifetime, saved-state registry, ViewModel ownership, process death, and Bundle size.

## Follow-up questions

- **Interviewer:** "Does a ViewModel object survive process death?"
  **Answer:** "No. A new instance is created. `SavedStateHandle` can restore small values if saved-state restoration is available, and the ViewModel must rebuild the rest from durable data."
- **Interviewer:** "What can I store in `rememberSaveable`?"
  **Answer:** "Small values supported by the local registry, or values with a suitable `Saver`. I avoid large graphs and test the actual save/restore path rather than assuming every object is supported."

## Self-check rubric

Assign three example values to owners, explain rotation and process death, and avoid a duplicate source of truth.

## References and reviewed-on date

- [Save UI state in Compose](https://developer.android.com/develop/ui/compose/state-saving) — lifetime and small saved values.
- [Where to hoist state](https://developer.android.com/develop/ui/compose/state-hoisting) — owner choice.

Technically reviewed against primary documentation on 2026-10-19.

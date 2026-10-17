---
id: "AND-14"
question: "What is the Activity Result API, and why use it?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "B"
phase: 1
priority: "P1"
order: 44
editorial_status: "reviewed"
---

# AND-14

## Original interview question

What is the Activity Result API, and why use it?

## What the interviewer evaluates

- Know the registration, launch, and callback contract for an external activity or permission request.
- Explain lifecycle recreation and why stable registration order matters.
- Choose typed contracts or a custom contract instead of manually managing request codes.

## Concept and technical explanation

The Activity Result API is the modern, type-safe framework introduced in AndroidX to handle cross-activity communication and result retrieval, completely superseding the legacy, deprecated `startActivityForResult()` and `onActivityResult()` pattern.

The legacy approach suffered from severe architectural deficiencies:
1. Lifecycle Coupling and Fragment Collisions:
Result handling was tightly bound to the Activity or Fragment class, forcing developers to route disparate results through a monolithic, error-prone `onActivityResult` switch-case block using integer request codes. Request code collisions frequently occurred across large, multi-module codebases.
2. The Fatal Low-Memory Process Kill Bug:
When launching an external resource-heavy activity—such as the system camera or a file gallery picker—Android frequently terminated the background caller Activity under memory pressure. When the user returned with the captured photo, the calling Activity was recreated from scratch, but its `onActivityResult` callback frequently lost transient references or executed before view models were initialized, leading to blank screens or NullPointerExceptions.

The Activity Result API addresses these problems by decoupling result handling through dedicated contracts (`ActivityResultContract<I, O>`) and registering persistent, type-safe launchers via `registerForActivityResult()`. The framework mandates registering launchers unconditionally during initialization or `onCreate()`. By doing so, if the host Activity is destroyed while the target activity is active, the framework re-registers the callback prior to entering the STARTED lifecycle state, automatically delivering the result to the rehydrated launcher without state loss.

## Practical walkthrough (English)

Selecting an image and handling results type-safely via the Activity Result API:
```kotlin
class ProfileActivity : AppCompatActivity() {

    // 1. Unconditionally register the typed contract during property initialization
    private val pickImageLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        // 2. Type-safe callback invoked automatically even if Activity was recreated
        if (uri != null) {
            loadAvatarPreview(uri)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_profile)

        findViewById<Button>(R.id.btn_change_avatar).setOnClickListener {
            // 3. Launch with type-safe input parameter
            pickImageLauncher.launch("image/*")
        }
    }

    private fun loadAvatarPreview(imageUri: Uri) {
        findViewById<ImageView>(R.id.avatar_image).setImageURI(imageUri)
    }
}
```
Failure scenario:
If an engineer attempts to register `registerForActivityResult` inside a button click listener or after `onStart()`, the runtime immediately throws an `IllegalStateException: LifecycleOwner is attempting to register while current state is STARTED`. The callback MUST be registered during initialization so the OS can restore it if the Activity is killed in the background.

## Explanation in Arabic

الـ Activity Result API هو البديل الحديث والموثوق لـ `startActivityForResult` القديمة المعيبة:

1. المشاكل الكارثية في `startActivityForResult` القديمة:
   - كانت تعتمد على دالة عملاقة واحدة `onActivityResult(requestCode, resultCode, data)`.
   - تتطلب إدارة أكواد يدوية (`REQUEST_CODE = 101, 102, 103`) وعشرات كتل الـ `switch-case` المعقدة.
   - **الكارثة الكبرى (Process Death Bug):** عندما تفتح الكاميرا لتصوير صورة، تطبيق الكاميرا يستهلك 500MB من الرام، فيقوم النظام بـ **قتل الـ Activity الخاصة بتطبيقك في الخلفية**! عند التقاط الصورة والعودة، كانت النتائج تضيع أو يحدث Crash لأن الـ Activity أعيد بناؤها وفقدت سياق الـ Callback!

2. ما الذي يوفره الـ Activity Result API؟
   - **Type-Safety كامل:** عقود محددة (Contracts) تحدد نوع المدخلات والمخرجات بدقة (مثل `GetContent`, `TakePicture`, `RequestPermission`).
   - **مقاوم للـ Process Death 100%:** يتم تسجيل الـ Callback في مرحلة الـ Initialization/onCreate عبر `registerForActivityResult`. حتى لو ماتت الـ Activity وتمت إعادة بنائها، النظام يعيد ربط النتيجة بالـ Callback تلقائياً بدون أي سطر كود إضافي.

3. إمكانية كتابة عقود مخصصة (Custom Contracts):
   - يمكنك إنشاء `ActivityResultContract<Input, Output>` مخصص لتغليف أي Intent وتحويل النتيجة مباشرة لـ Domain Model.

## Practical walkthrough

مقارنة بين القديم والحديث لاختيار صورة من المعرض:
```kotlin
class ProfileActivity : AppCompatActivity() {

    // ✅ النمط الحديث باستخدام Activity Result API:
    private val pickImageLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { imageUri: Uri? ->
        // يتم استدعاؤها بنجاح حتى لو ماتت الـ Activity أثناء وجود المستخدم في المعرض!
        imageUri?.let { avatarImageView.setImageURI(it) }
    }

    fun onChangeAvatarClicked() {
        pickImageLauncher.launch("image/*") // استدعاء نظيف بـ Type-safe contract
    }
}
```

## Why it matters and how it works

The API replaces manual `onActivityResult` request-code routing with `ActivityResultContract`, `registerForActivityResult`, and a callback. Registration associates a key with the lifecycle owner, so pending results can be routed to a new instance after recreation. Launch only when the owner is ready and the user has chosen the action. The returned URI or permission Boolean is a result to validate; it is not proof that a file remains readable forever or that permission can never be revoked.

## Worked example

In an Activity, declare `private val pickPhoto = registerForActivityResult(ActivityResultContracts.GetContent()) { uri -> if (uri != null) showPreview(uri) }`, then call `pickPhoto.launch("image/*")` from a click handler. This abbreviated Kotlin snippet assumes AndroidX Activity KTX and an implementation of `showPreview`; it is not standalone compilable. For long-lived URI access, use the appropriate document contract and persistable grant flow instead of assuming `GetContent` grants it.

## Trade-offs and decision criteria

Built-in contracts cover common actions with typed inputs and outputs. A custom contract can normalize a proprietary flow but adds parsing and compatibility work. A launcher tied to a Fragment's lifecycle is suitable for its UI; a shared singleton launcher is unsafe because registration belongs to an owner. Choose the system Photo Picker where appropriate to avoid broad media permissions.

## Failure modes

Conditional or reordered registration can route a pending result to the wrong callback. Registering after the lifecycle is started throws or misses delivery. Treating cancellation as a selected item causes null handling errors. A process may die between launch and callback, so restore the minimum request context from saved state and independently validate returned data and grants.

## Production perspective

A profile editor stores the pending operation ID in `SavedStateHandle`, registers its photo picker launcher unconditionally, and handles null as cancellation. It validates MIME type and size before upload, handles URI read failure, and checks that a restored editor still has a valid account session. UI tests cover selection, cancellation, rotation while the picker is open, and return after process recreation.

## Interview answer — short

The Activity Result API replaces legacy startActivityForResult with a type-safe, decoupled contract pattern. By mandating launcher registration during component initialization, it ensures result callbacks survive caller Activity destruction and background process reclamation when external activities like the camera or gallery consume system RAM.

## Interview answer — structured

The Activity Result API is Android's modern standard for initiating external component flows and processing their return results, completely superseding the deprecated startActivityForResult and onActivityResult pattern.

The legacy model suffered from two fundamental flaws: tightly coupling all result parsing to a monolithic switch-case method inside the Activity, and failing catastrophically when the calling Activity was destroyed in the background due to low memory while a memory-intensive camera or document picker was active.

The Activity Result API decouples result handling into modular, type-safe contracts using ActivityResultContract. A launcher specifies typed input parameters and yields strongly typed output objects, eliminating manual integer request codes and Intent parsing boilerplate.

In production, registration timing is critical. Launchers must be declared unconditionally during initialization or in onCreate before the lifecycle reaches STARTED. This timing contract allows the underlying ActivityResultRegistry to rebind the result listener automatically upon Activity recreation, guaranteeing seamless delivery even after process death.


## Interview answer — deep senior

At the framework architecture and lifecycle registry level, the Activity Result API is orchestrated by ComponentActivity's internal ActivityResultRegistry. In the legacy startActivityForResult model, the platform dispatched results directly through ActivityThread into onActivityResult(). If the operating system terminated the calling Activity process while the user was interacting with an external camera application, re-instantiating the Activity frequently led to lost callbacks because the receiving listeners were not yet attached when the system delivered the result bundle.

The ActivityResultRegistry resolves this synchronization race through a durable key-based registry. When registerForActivityResult(contract, callback) is invoked during initialization, the registry generates or retrieves a unique persistent string key for that operation. If the hosting Activity is killed by the Low Memory Killer while the camera is open, the camera returns its result across Binder IPC to ActivityTaskManagerService.

When the caller Activity is reconstructed, ActivityThread invokes performCreate(), restoring the saved state Bundle. Because the launcher is registered unconditionally before onStart(), the ActivityResultRegistry matches the incoming system result against the re-registered key and queues the dispatch until the lifecycle reaches CREATED, delivering the parsed result safely to the developer's callback.

Furthermore, Staff engineers leverage custom ActivityResultContracts to establish clean architectural boundaries. By extending ActivityResultContract<Input, Output>, teams encapsulate complex Intent assembly, URI permissions, and output parsing (such as transforming raw Intent extras into domain-specific DTOs) into isolated, unit-testable components, passing mock ActivityResultRegistry instances during testing without launching actual Android UI components.

## How to answer in the interview

- **Why:** Result callbacks need stable lifecycle ownership and typed contracts.
- **How:** Register a contract and callback before launch; handle cancellation result.
- **Trade-offs:** Select `GetContent` or document access by required URI lifetime.
- **Failure cases:** Name late registration, null URI assumptions, and lost URI permission.
- **Production solution:** Build and restore a photo-selection flow with explicit grant handling.

## Deep-dive talking points

Discuss stable registration order, result registry, owner lifecycle, cancellation, URI grant duration, and saved request context.

## Follow-up questions

- **Interviewer:** "Why must `registerForActivityResult` be called unconditionally during initialization?"
  **Answer:** "Because the callback must be registered before the Activity transitions past `CREATED`. If the Activity was recreated after process death, the framework delivers pending results during `onStart()`, so the callback must already be registered to receive them."

- **Interviewer:** "Can you use the Activity Result API in a standalone non-UI class?"
  **Answer:** "Yes! By accepting an `ActivityResultRegistry` and a `LifecycleOwner`, a standalone presenter or repository class can register and launch activity contracts without being an Activity subclass."

- **Interviewer:** "What contract is used for picking visual media in Android 13+?"
  **Answer:** "`ActivityResultContracts.PickVisualMedia()`, which opens the modern, privacy-preserving Android Photo Picker without requiring any storage permissions."

## Self-check rubric

Explain contract, launcher, callback, registration timing, recreation, cancellation, and URI validation.

## References and reviewed-on date

- [Get a result from an activity](https://developer.android.com/training/basics/intents/result) — registry and lifecycle registration.
- [ActivityResultContracts](https://developer.android.com/reference/androidx/activity/result/contract/ActivityResultContracts) — built-in contracts.

Technically reviewed against primary documentation on 2026-10-13.

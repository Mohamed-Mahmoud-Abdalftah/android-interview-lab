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

The Activity Result API replaces error-prone startActivityForResult and onActivityResult with strongly-typed, modular ActivityResultContracts. Crucially, it registers callbacks during initialization so results are safely reconnected even if the calling Activity is killed by process death while the external app is open.

## Interview answer — structured

The Activity Result API completely modernizes inter-activity result handling by replacing legacy `startActivityForResult` and monolithic `onActivityResult` overrides.

It solves three major architectural defects of the old API:

1. **Process Death Resilience**: When launching memory-heavy external applications (like the camera or gallery), Android frequently kills the calling Activity process in the background. Because `registerForActivityResult()` registers the callback handle before `onStart()`, when the Activity recreates upon returning, the result is re-delivered to the restored callback cleanly without data loss.

2. **Type-Safe Modular Contracts**: It uses `ActivityResultContract<I, O>` abstractions that explicitly define typed inputs and outputs—such as `TakePicture`, `GetContent`, or `RequestPermission`—eliminating raw `Intent` parsing and fragile `requestCode` integer switch statements.

3. **Decoupled Architecture**: Result launchers can be registered inside standalone helper classes and lifecycle observers, removing bloated navigation code from the Activity class body.

## Interview answer — deep senior

Under the hood, the API is managed by `ActivityResultRegistry`. When you invoke `registerForActivityResult(contract, callback)`, it generates a unique key and registers the callback in the registry. When `launch(input)` is called, the contract generates an Intent, saves the request key in the instance state Bundle, and dispatches the Intent.

You can also write powerful **Custom Contracts**:

```kotlin
class SelectUserContract : ActivityResultContract<String, UserProfile?>() {
    override fun createIntent(context: Context, input: String): Intent =
        Intent(context, UserPickerActivity::class.java).putExtra("team_id", input)

    override fun parseResult(resultCode: Int, intent: Intent?): UserProfile? =
        if (resultCode == Activity.RESULT_OK) intent?.getParcelableExtra("user") else null
}
```

This encapsulates all intent parsing, extras keys, and result code checks into a single reusable component across multi-module codebases.

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

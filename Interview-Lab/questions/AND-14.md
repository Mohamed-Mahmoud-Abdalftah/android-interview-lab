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

`Activity Result API` بتنظم طلب نتيجة من Activity تانية، زي اختيار صورة أو طلب permission. بتسجل launcher في كل إنشاء للـActivity أو Fragment قبل ما يوصل لـ`STARTED`، وبعدين تطلقه لما المستخدم يعمل action؛ الـcallback يستقبل نتيجة typed حسب الـcontract. النظام والمكتبة يتعاملوا مع إعادة إنشاء الـActivity وقت rotation أو process recreation وتوصيل النتيجة للـcallback المُسجل. لازم التسجيل يكون بنفس الترتيب كل مرة، وما تخزّنش launcher في singleton أو تسجله متأخر بعد ما lifecycle بدأ.

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

“Activity Result APIs register a typed contract and callback with a lifecycle owner, then launch an external operation such as a picker or permission request. They avoid manual request-code handling and support result delivery after recreation.”

## Interview answer — structured

“I register the launcher consistently during Activity or Fragment creation and launch it in response to a user action. The contract defines input and parsed output, and the callback handles success or cancellation. Lifecycle-aware registration lets a recreated owner receive a pending result, but registration order must remain stable. For a photo picker I still validate the URI and handle access errors; the result alone is not durable storage or authorization. The callback survives component recreation through the registry when registration is stable, which removes brittle request-code routing. I register launchers unconditionally in a consistent order before the lifecycle is started, launch after a user action, and handle cancellation or null data. A returned URI still needs validation and appropriate read grants.”
## Interview answer — deep senior

“The result registry decouples an external request from a particular Activity instance. I register every launcher on each creation, in stable order, before the owner reaches STARTED, and keep the callback small enough to validate and hand off work. I choose an AndroidX contract for permissions, documents, or media when possible, and a custom contract only when the external protocol warrants it. During process recreation the launcher can receive a pending result, while my own request context must be restored separately. I handle cancellation, malformed results, revoked URI access, and stale account state. For an upload, that means copying or consuming the selected content under the correct grant and making the upload itself resilient to network failures. The Activity Result API pairs a contract with a lifecycle-aware registration key so a pending result can reach a recreated Activity or Fragment. That guarantee depends on registering again in the same order and at the correct lifecycle point; conditional registration can deliver to the wrong callback. I keep the minimum request context in saved state, not a live Activity reference. When a picker returns a URI, I treat it as external input: verify type, size and permissions, then copy or process it under the app’s data policy. For a permission contract I still recheck current grant before using the resource because it may change after the callback. Tests cover cancellation, rotation during launch and process recreation.”
## Deep-dive talking points

Discuss stable registration order, result registry, owner lifecycle, cancellation, URI grant duration, and saved request context.

## Follow-up questions

- Why register unconditionally? **Answer:** a result launched by an earlier instance must map to the same callback after recreation.
- Does `GetContent` guarantee permanent access to a URI? **Answer:** no; choose a document contract and persistable permission when durable access is required.
- How do you handle a picker return after logout? **Answer:** validate the restored session and discard the result if its original operation is no longer authorized.

## Self-check rubric

Explain contract, launcher, callback, registration timing, recreation, cancellation, and URI validation.

## References and reviewed-on date

- [Get a result from an activity](https://developer.android.com/training/basics/intents/result) — registry and lifecycle registration.
- [ActivityResultContracts](https://developer.android.com/reference/androidx/activity/result/contract/ActivityResultContracts) — built-in contracts.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The Kotlin excerpt is illustrative.

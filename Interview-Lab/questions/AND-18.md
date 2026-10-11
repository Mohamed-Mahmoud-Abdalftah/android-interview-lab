---
id: "AND-18"
question: "How do multi-window, rotation, and background/foreground transitions affect state?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "B"
phase: 1
priority: "P1"
order: 48
editorial_status: "reviewed"
---

# AND-18

## Original interview question

How do multi-window, rotation, and background/foreground transitions affect state?

## What the interviewer evaluates

- Separate configuration recreation, visibility/focus changes, and process death.
- Put transient UI state, retained presentation state, and durable data in appropriate owners.
- Avoid assumptions that `onPause` implies invisibility or that `ViewModel` survives process death.

## Explanation in Arabic

الدوران غالبًا configuration change: الـActivity تتدمر وتتعمل تاني، والـViewModel عادة يفضل موجود لنفس logical screen. لكن النظام ممكن يقتل process وهو في الخلفية، وساعتها الـViewModel يضيع ولازم ترجع من saved state وstorage. في multi-window الشاشة ممكن تكون ظاهرة من غير ما تكون resumed أو focused، لذلك ربط كل تحديث بـ`onResume` فقط ممكن يوقف واجهة ظاهرة. `onStart`/`onStop` أو lifecycle-aware collection عادة أنسب للمحتوى المرئي. لا تستخدم `onPause` كضمان لحفظ طويل أو إكمال upload؛ persist المهمات المهمة مبكرًا واستعمل آلية background work مناسبة.

## Why it matters and how it works

Rotation changes resources and can recreate UI components. Multi-window changes size and focus independently of whether content remains visible. Backgrounding moves lifecycle state and makes process termination possible; returning may resume an existing instance or build a new one. `rememberSaveable` and `SavedStateHandle` restore small UI state from saved instance state when available, while Room or another durable store owns business data. A ViewModel survives ordinary configuration change but not arbitrary process termination.

## Worked example

A search screen keeps its query and selected tab in saveable state, search results in a repository/cache, and the active request in a ViewModel with cancellation. On rotation it recreates layout and continues from retained state. If the process dies in background, it restores the query and reloads results. In split screen it adapts width and continues visible updates even when another window has focus. The scenario describes ownership; implementation must be tested for supported API levels.

## Trade-offs and decision criteria

Saving every large result bundle in instance state is expensive and can exceed transaction limits; save keys and reload. Retaining all state only in a ViewModel is simple across rotation but loses it after process death. Persisting every keystroke to disk may be unnecessary; choose durability based on user cost. Prefer responsive layouts over forced orientation to handle device sizes and multi-window.

## Failure modes

A screen assumes `onCreate` runs only once and duplicates side effects after rotation. Another assumes `onPause` means invisible and stops a visible split-screen preview. A payment draft stored only in memory disappears after process death. Long work started in Activity scope is cancelled on destruction; use a suitable persistent scheduler if the work must survive. Test rotation, resizing, home/return, and developer option “Don't keep activities,” but do not treat that option as identical to process death.

## Production perspective

For a delivery checkout, save the address draft and idempotency key durably before submitting payment. Use `SavedStateHandle` for navigation/UI selection and repository data for the order. Observe network results while visible, but make the server operation independent of Activity recreation. Run UI tests across portrait, landscape, split screen, and process-kill restoration, and log state recovery failures without customer data.

## Interview answer — short

“Rotation can recreate UI, multi-window separates visibility from focus, and backgrounding can lead to process death. I keep small UI state saveable, business data durable, and never assume a ViewModel survives a killed process.”

## Interview answer — structured

“I treat these as different events. A configuration change commonly recreates an Activity, while its ViewModel normally remains for that logical screen. Multi-window can leave a screen visible without focus, so I use lifecycle states appropriate to visibility rather than equating pause with hidden. After background process death, in-memory ViewModels and coroutines are gone; saved instance state can restore small UI keys, and repositories reload durable data. I test each path separately and avoid placing large result objects in a Bundle. Multi-window means paused does not always equal invisible, and the app may be resized without a simple rotation assumption. I classify state by lifetime: transient layout state, ViewModel state, saved reconstruction keys and durable business data. A background transition also opens the possibility of process death, so I test restoration rather than only resume.”
## Interview answer — deep senior

“State ownership drives my implementation. Ephemeral view details can be saveable, screen logic can live in a ViewModel, and anything the user must not lose belongs in durable storage or a backend. Rotation recreates views and resources, so side effects must not accidentally duplicate; a ViewModel handles ordinary configuration changes but is rebuilt after process death. Multi-window means STARTED and RESUMED are not interchangeable for visible updates. Background work that must complete cannot depend on an Activity coroutine. On return I restore stable keys, reconcile with current repository state, and avoid replaying a non-idempotent action such as payment. I verify this with resize, rotation, background/foreground, and actual process-kill scenarios. I avoid mapping every lifecycle callback to a single product state. A split-screen Activity can remain visible while paused, while another window has focus; a responsive UI should adapt to dimensions and current capability, not assume portrait/fullscreen. Rotation can recreate the Activity and views while retaining its ViewModel, but a later background process kill removes all in-memory objects. I save compact UI hints with saved state and persist drafts or operation IDs independently. An Activity-scoped coroutine may be canceled on recreation, so durable upload/payment work needs an appropriate repository/scheduler and server status contract. I test resize, rotation, background/foreground and process kill as separate transitions.”
## Deep-dive talking points

Discuss visible versus focused lifecycle states, configuration change, process death, Bundle limits, durable drafts, and idempotent recovery.

## Follow-up questions

- Does a ViewModel survive process death? **Answer:** no; it is retained across ordinary configuration recreation, while process death creates a new instance.
- Why might `onPause` fire while content remains visible? **Answer:** multi-window can transfer focus to another window without fully hiding this one.
- Where should a payment idempotency key live? **Answer:** durably with the pending transaction so a restored process can reconcile rather than duplicate submission.

## Self-check rubric

Contrast rotation, multi-window, and process death; allocate three types of state; describe a visible-but-paused screen and a restored transaction.

## References and reviewed-on date

- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — state ownership and process recreation.
- [Multi-window support](https://developer.android.com/develop/ui/views/layout/support-multi-window-mode) — lifecycle and resizing considerations.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The checkout flow is illustrative.

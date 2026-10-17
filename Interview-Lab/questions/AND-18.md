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

## Concept and technical explanation

State preservation in Android is driven by three distinct system-level triggers: configuration changes, multi-window visibility transitions, and background process death.
During configuration changes (such as screen rotation, folding/unfolding foldable displays, or system locale updates), the operating system destroys and completely recreates the Activity instance to reload optimized resources. In contrast, multi-window mode (introduced in Android 7.0 and refined with multi-resume in Android 10) decouples window visibility from window focus. In multi-window or picture-in-picture mode, an Activity may remain visible in the STARTED state while another window holds user focus, meaning background transitions must not immediately halt rendering or media playback. Finally, when an application is moved to the background, it transitions through onPause to onStop. Under severe memory pressure, the Linux Low Memory Killer terminates the cached process without warning. Preserving application continuity requires a multi-tiered state management architecture: ephemeral UI state stored in SavedStateHandle, presentation logic retained across configuration changes in a ViewModel, and durable business state persisted immediately in a local Room database.

## Practical walkthrough (English)

A video player implementation must adapt its playback lifecycle to multi-window mode, continuing playback while visible in onStart rather than pausing prematurely in onPause:

```kotlin
class VideoPlayerActivity : AppCompatActivity() {
    private var player: ExoPlayer? = null

    override fun onStart() {
        super.onStart()
        // Initialize player when visible in multi-window mode:
        initializePlayer()
    }

    override fun onResume() {
        super.onResume()
        // Resume full interactive controls
    }

    override fun onPause() {
        super.onPause()
        // Do not release player here in multi-window mode!
    }

    override fun onStop() {
        super.onStop()
        // Release hardware decoding resources when completely hidden:
        releasePlayer()
    }

    private fun initializePlayer() { /* ExoPlayer setup */ }
    private fun releasePlayer() {
        player?.release()
        player = null
    }
}
```

Failure scenario: A banking transfer screen retains the transfer amount only inside a ViewModel. When the user backgrounds the app to copy a verification code, the operating system kills the process. When the user returns, the system recreates the Activity, but the ViewModel is re-instantiated with default null values, wiping out the uncommitted form data and causing severe user frustration.

## Explanation in Arabic

تأثير الـ Multi-Window (تقسيم الشاشة)، التدوير (Rotation)، والانتقال بين الخلفية والمقدمة (Background/Foreground) على حالة التطبيق:

1. الـ Multi-Window / Split-Screen (تقسيم الشاشة):
   - في وضع تقسيم الشاشة، قد يكون تطبيقك **مرئياً تماماً على الشاشة ولكنه ليس في بؤرة التركيز التفاعلي (Visible but Not Focused)** لأن المستخدم يتفاعل مع التطبيق الآخر في النصف الثاني!
   - **حالة الـ Lifecycle:** التطبيق يكون في حالة **`onStart()` / `onPause()`** (أو `RESUMED` في أندرويد 10+ مع ميزة Multi-resume)!
   - **الخطأ الكارثي:** لو كنت توقف تحديثات الفيديو أو الرسوم في `onPause()`، فالفيديو سيتوقف ويتجمد أمام عيني المستخدم في وضع تقسيم الشاشة! لذلك يجب إيقاف الفيديو والرسوم في **`onStop()`**، وليس في `onPause()`.

2. الـ Rotation (تدوير الشاشة):
   - يدمر الـ Activity ويعيد بناؤها بالكامل (`onDestroy` -> `onCreate`).
   - الـ ViewModel والـ SavedStateHandle ينجوان في الذاكرة.

3. الـ Background / Foreground Transitions:
   - عند الانتقال للخلفية: تستدعى `onPause()` ثم `onStop()`. يدخل التطبيق في تجمع الـ 'Killable' للـ Low Memory Killer.
   - حفظ الحالة الإلزامي يتم في `onSaveInstanceState(Bundle)` قبل أن يصبح التطبيق عرضة للـ Process Death.

## Practical walkthrough

تطبيق عملي: مشغل فيديو (Video Player) في وضع Multi-Window:
```kotlin
class VideoPlayerActivity : AppCompatActivity() {
    private var player: ExoPlayer? = null

    override fun onStart() {
        super.onStart()
        // 1. نبدأ تشغيل الفيديو في onStart حتى يعمل في وضع Multi-Window بسلاسة:
        initializePlayer()
    }

    override fun onStop() {
        super.onStop()
        // 2. نحرر الـ Player في onStop عندما تختفي الشاشة تماماً عن عين المستخدم:
        releasePlayer()
    }
    // لا نوقف الفيديو في onPause() أبداً حتى لا يتجمد في Split-screen!
}
```

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

Manage state across three distinct layers: use ViewModel for transient configuration changes like rotation; use SavedStateHandle and onSaveInstanceState for lightweight navigation state surviving background process death; and persist durable business data immediately in Room or DataStore. In multi-window mode, handle visibility in onStart and onStop rather than onResume and onPause.

## Interview answer — structured

Handling state transitions requires separating configuration recreation from background process termination. Rotation destroys and recreates the Activity window to reload layout resources, whereas moving an app to the background transitions the process to a cached state where the Linux kernel can kill it silently at any moment.

We structure state management into three resilient tiers. The ViewModel retains complex presentation state across configuration changes like rotation and screen folding. For surviving background process death, lightweight UI parameters and navigation IDs are preserved in SavedStateHandle via onSaveInstanceState.

In production, involving multi-window and picture-in-picture modes on tablets and foldables, visibility is decoupled from touch focus. An Activity in split-screen remains visible even when unfocused, so continuous operations like video playback must be bound to onStart and onStop rather than prematurely suspended in onPause.

Critical user actions and financial transactions must be persisted immediately to local durable storage like Room or DataStore rather than relying on late lifecycle callbacks.


## Interview answer — deep senior

Under the hood, configuration changes cause the ActivityThread to execute handleRelaunchActivity, invoking onSaveInstanceState, destroying the current Activity instance via onDestroy, and instantiating a fresh one. The existing ViewModelStore is preserved across this destruction by the NonConfigurationInstances holder maintained by the Android framework. However, during background process death, the entire Linux process is terminated by the Low Memory Killer daemon (lmkd) via a SIGKILL signal. The ViewModelStore and all in-memory static singletons are entirely obliterated.
When the user subsequently restores the task from the Overview screen, the system launches a brand-new process, executes Application.onCreate(), and passes the parcelized savedInstanceState Bundle back to Activity.onCreate(). If an application relies solely on ViewModel properties or static caches without saving state in SavedStateHandle, it will throw a NullPointerException or reset to a broken initial state upon restoration.
Regarding multi-window mechanics, Android 7.0 introduced multi-window where only the top focused app was in RESUMED, while visible side-by-side apps were kept in PAUSED. Android 10 introduced multi-resume, allowing all visible activities in split-screen or multi-display environments to remain in RESUMED if their manifests permit. Stopping video playback or location updates in onPause breaks the user experience in multi-window scenarios; resources tied to visual rendering must remain active throughout the STARTED state and only shut down when transitioning to STOPPED.
Furthermore, developers must respect the 1MB IPC transaction limit when writing to onSaveInstanceState. The saved instance state bundle is marshaled across Binder to the system server process (ActivityTaskManagerService). Exceeding this buffer by attempting to store large bitmaps or extensive JSON lists triggers a TransactionTooLargeException, crashing the process during state preservation.

## How to answer in the interview

- **Why:** Visibility and focus can change independently of process lifetime.
- **How:** Describe resize/rotation recreation, background callbacks, and possible later process loss.
- **Trade-offs:** Use STARTED for visible collection and RESUMED for focus-sensitive resources when appropriate.
- **Failure cases:** Name lost query, stale request, and assumptions that pause always means invisible.
- **Production solution:** Test one search screen in split screen, rotation, and delayed return.

## Deep-dive talking points

Discuss visible versus focused lifecycle states, configuration change, process death, Bundle limits, durable drafts, and idempotent recovery.

## Follow-up questions

- **Interviewer:** "What is 'Multi-Resume' in Android 10+?"
  **Answer:** "In Android 10 (API 29) and above, all visible activities in multi-window mode or split-screen are placed in the `RESUMED` state simultaneously, rather than keeping only the top-focused activity resumed."

- **Interviewer:** "How does `isInMultiWindowMode` help?"
  **Answer:** "It is an Activity method (`isInMultiWindowMode`) that returns a boolean indicating whether the activity is currently operating in multi-window split-screen mode, allowing customized UI layouts."

- **Interviewer:** "Why must you avoid fixed orientation lock (`android:screenOrientation="portrait"`) on foldables and tablets?"
  **Answer:** "Locking orientation is explicitly ignored or letterboxed by Android 12L+ on large screens and foldables to prevent broken user experiences. Apps must support fluid multi-orientation layouts."

## Self-check rubric

Contrast rotation, multi-window, and process death; allocate three types of state; describe a visible-but-paused screen and a restored transaction.

## References and reviewed-on date

- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — state ownership and process recreation.
- [Multi-window support](https://developer.android.com/develop/ui/views/layout/support-multi-window-mode) — lifecycle and resizing considerations.

Technically reviewed against primary documentation on 2026-10-13.

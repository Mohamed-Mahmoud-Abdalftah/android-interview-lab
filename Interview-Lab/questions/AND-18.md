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

In multi-window, the app can be visible (onStart) without having input focus (onPause), so media playback and rendering must be controlled in onStart/onStop, not onResume/onPause. Rotation triggers full Activity recreation with ViewModel preservation, and backgrounding moves the app to onStop where it becomes killable by the OS.

## Interview answer — structured

These three transitions impact Android lifecycle states and resource management differently.

First, a Multi-Window / Foldable Resizing is the app shares screen real estate with another process. The app is fully visible, but may not have user touch focus. Prior to Android 10, an app without focus was kept in `onPause()`. In Android 10+ with **Multi-Resume**, all visible apps in multi-window remain in `RESUMED`. Therefore, video playback, map rendering, and animations must be bound to **`onStart()` and `onStop()`**; stopping them in `onPause()` causes frozen video playback in split-screen mode. Next, with Screen Rotation, triggers a full Configuration Change: `onPause -> onStop -> onDestroy` followed by recreation. The UI hierarchy and view bindings are destroyed, while the ViewModel and SavedStateHandle survive in memory.
Finally, with Background/Foreground Transitions, navigating away invokes `onPause()` followed by `onStop()`. The OS calls `onSaveInstanceState()` to serialize state. Once in `onStop()`, the app's process is marked killable by the Low Memory Killer if RAM is constrained.


## Interview answer — deep senior

On modern **Foldable devices** (e.g., Samsung Galaxy Fold, Google Pixel Fold), unfolding the device transitions the app from a compact external display to a large unfolded inner display. This triggers dynamic configuration changes where screen size, aspect ratio, and smallest screen width (`sw600dp`) change on the fly.

To support foldables seamlessly in modern architecture: 1. Use **Jetpack WindowManager** (`WindowInfoTracker.getOrCreate(context).windowLayoutInfo(activity)`) to observe folding postures (Flat, Half-Opened / Tabletop mode, and display hinge folding features). 2. Adopt adaptive UI layouts with Compose (`calculateWindowSizeClass()`), switching dynamically between single-pane, list-detail, and supporting pane layouts without manual Activity recreation hacks.


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

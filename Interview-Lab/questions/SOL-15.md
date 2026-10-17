---
id: "SOL-15"
question: "How would you split a large interface with mostly unused methods?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "B"
phase: 2
priority: "P1"
order: 186
editorial_status: "reviewed"
---

# SOL-15

## Original interview question

How would you split a large interface with mostly unused methods?

## What the interviewer evaluates

Split a fat interface by consumer capabilities while preserving migration compatibility and behavior.

## Concept and technical explanation

Splitting a bloated interface with mostly unused methods enforces the Interface Segregation Principle (ISP) and eliminates fragile client coupling. When an interface combines disparate operational concerns, it becomes a 'fat interface' that forces callers to implement or depend on methods they never invoke. To split it effectively, senior engineers analyze client usage patterns, partition the contract along natural actor and consumer boundaries into fine-grained role interfaces (frequently Single Abstract Method / SAM interfaces in Kotlin), and use interface inheritance, composite interfaces, or Kotlin class delegation (by) to preserve backward compatibility where unified access is legitimately required.

## Practical walkthrough (English)

Refactoring a fat media player interface into cohesive role interfaces:
```kotlin
// BAD ANTI-PATTERN: Fat interface violating ISP (Forces audio-only player to implement video methods)
interface MediaPlayerController {
    fun play()
    fun pause()
    fun seekTo(positionMs: Long)
    fun setVideoSurface(surface: Surface) // Video-only concern!
    fun adjustSubtitleTrack(trackId: Int) // Video-only concern!
    fun setPlaybackSpeed(speed: Float)
}

// ARCHITECTURAL BEST PRACTICE: Segregated role interfaces based on client capabilities
interface PlaybackControls {
    fun play()
    fun pause()
    fun seekTo(positionMs: Long)
}

interface SpeedAdjustable {
    fun setPlaybackSpeed(speed: Float)
}

interface VideoSurfaceController {
    fun setVideoSurface(surface: Surface)
    fun adjustSubtitleTrack(trackId: Int)
}

// Composite interface for clients that genuinely need full multimedia capabilities
interface FullVideoPlayerContract : PlaybackControls, SpeedAdjustable, VideoSurfaceController

// Concrete implementation satisfies granular interfaces cleanly
class ExoPlayerWrapper @Inject constructor() : FullVideoPlayerContract {
    override fun play() { /* ... */ }
    override fun pause() { /* ... */ }
    override fun seekTo(positionMs: Long) { /* ... */ }
    override fun setPlaybackSpeed(speed: Float) { /* ... */ }
    override fun setVideoSurface(surface: Surface) { /* ... */ }
    override fun adjustSubtitleTrack(trackId: Int) { /* ... */ }
}

// Audio-only notification widget depends strictly on minimal playback controls!
class AudioWidgetPresenter(private val controls: PlaybackControls) {
    fun onPlayClicked() = controls.play()
}
```

## Explanation in Arabic

كيف تقوم بتقسيم واجهة ضخمة (Fat Interface) تحتوي على دوال كثيرة غير مستخدمة؟ وما هي الخطوات العملية؟

1. تشخيص الواجهة المتضخمة (Fat Interface Diagnosis):
   - واجهة مثل `interface MediaPlaybackListener` فيها 12 دالة (play, pause, stop, seek, buffer, volumeChanged, trackChanged, error, metadataLoaded, subtitleAvailable, bitrateChanged, qualityDropped).
   - معظم الشاشات المستهلكة (Clients) تحتاج فقط لمعرفة `onPlaybackStateChanged` و `onError`، وتضطر لتنفيذ باقي الدوال كـ No-op فارغة!

2. استراتيجية التقسيم بناءً على أدوار العملاء (Role-Based Segregation):
   - تطبيق مبدأ **ISP (Interface Segregation Principle)**: تجميع الدوال بناءً على من يستخدمها وكيف تتغير معاً:
     * `interface PlaybackStateListener` (للتشغيل والإيقاف المؤقت).
     * `interface MediaTrackListener` (للترجمات والمسارات الصوتية).
     * `interface PlaybackMetricsListener` (للتحليلات والـ Bitrate).

3. استخدام ميزات Kotlin الحديثة:
   - توفير **Default Implementations** في الـ Interface: `fun onBuffering() {}` بحيث لا يجبر المستدعي على كتابتها.
   - استخدام **SAM / Functional Interfaces** (`fun interface`) والـ Extension functions مع Lambdas (مثل `player.onPlayStateChange { ... }`).

## Practical walkthrough

تقسيم واجهة تشغيل وسائط ضخمة إلى واجهات متخصصة:
```kotlin
// ❌ واجهة ضخمة تجبر كل الشاشات على تنفيذ 6 دوال معظمها غير مستخدم:
interface FatAudioListener {
    fun onPlay()
    fun onPause()
    fun onTrackChanged(track: String)
    fun onVolumeChanged(volume: Float)
    fun onBitrateDrop(bitrate: Int)
    fun onError(error: String)
}

// ✅ تقسيمها حسب الأدوار وحاجة العملاء (ISP):
fun interface PlaybackStateListener {
    fun onStateChanged(isPlaying: Boolean)
}

fun interface TrackChangeListener {
    fun onTrackChanged(track: String)
}

fun interface MediaErrorListener {
    fun onError(error: String)
}

// في المشغل: دعم تسجيل المستمعين المتخصصين بشكل منفصل وبسيط عبر Lambdas:
class AudioPlayer {
    fun addStateListener(listener: PlaybackStateListener) { ... }
    fun addErrorListener(listener: MediaErrorListener) { ... }
}

// شاشة العرض البسيطة تسجل فقط ما تحتاجه بضغطة واحدة:
player.addStateListener { isPlaying -> updatePlayButtonIcon(isPlaying) }
```

## Why it matters and how it works

ISP reduces client coupling to unrelated methods. A capability map guides the split; one implementation can satisfy several views. Migration should preserve behavior while narrowing public dependencies.

## Worked example

Conceptual Kotlin:
```kotlin
interface SessionReader { fun observeUserId(): kotlinx.coroutines.flow.Flow<String?> }
interface SignOut { suspend fun signOut() }
class AccountMenu(private val signOut: SignOut)
```
The menu cannot accidentally call token-refresh internals just because they share an implementation.

## Trade-offs and decision criteria

Many tiny interfaces cost wiring and navigation. Choose cohesive capability groups. For a private one-consumer class, a concrete API may be simpler; ISP becomes important when consumers use disjoint subsets or modules rebuild together.

## Failure modes

A fake for a read-only widget stubs `deleteAccount()` and `chargeCard()` with unimplemented throwing stubs because the interface is wide; production code may accidentally call those methods. Split surface and test only promised behavior.

## Production perspective

A large app gradually migrates account features to session-read, profile-edit and sign-out contracts. Security review verifies that payment and token operations are not exposed through a general UI dependency.

## Interview answer — short

We split a large interface by identifying cohesive groupings based on client consumption rather than implementation convenience. Following ISP, we break the monolith into focused role interfaces, such as separating a bloated media player into PlaybackControls, SpeedAdjustable, and VideoSurfaceController. Clients like audio widgets depend only on the playback controls they actually use. For callers needing all features, we provide a composite interface combining the smaller ones, maintaining clean decoupling and zero unused boilerplate.

## Interview answer — structured

Refactoring a bloated interface into client-centric role interfaces is a direct application of the Interface Segregation Principle.
When an interface accumulates too many methods, it becomes a fat interface. Callers requiring only a small subset of features are forced to depend on methods they never invoke. In Android, this leads to empty stub implementations, brittle test mocks, and unwanted recompilation cycles whenever unused method signatures change.
The refactoring process follows a disciplined three-step workflow.
First, perform client consumption analysis. Audit all existing consumers to map which methods each caller actually invokes. Natural cluster boundaries will emerge between read operations, write operations, administrative actions, or media types.
Second, extract fine-grained role interfaces matching these consumer clusters. In Kotlin, these often take the form of functional types, SAM interfaces, or small 2-to-3 method contracts like PlaybackControls and VideoSurfaceController.
Third, satisfy backward compatibility and full-featured implementations using composite interfaces and Kotlin class delegation. A full player class can implement multiple role interfaces simultaneously, while callers depend strictly on their dedicated slice of functionality.

## Interview answer — deep senior

Under the hood, splitting fat interfaces preserves binary interface stability (ABI) and unlocks Gradle Compilation Avoidance in large-scale multi-module Android codebases.
When a module depends on a bloated interface, any modification to an uncalled method's signature alters the interface's public ABI bytecode. When Gradle compiles the project, its incremental analysis detects an ABI change in the upstream dependency, forcing the invalidation of compile caches and triggering a full recompilation of the consumer module even though the consumer's source code never referenced the altered method.
By decomposing the fat interface into granular role interfaces, the consumer module depends exclusively on its specific contract. Changes to unrelated methods remain isolated to their respective interfaces, allowing Gradle to completely skip recompilation of unaffected modules during continuous integration builds.
Furthermore, interface segregation dramatically simplifies test harness engineering. In unit tests for components depending on a fat interface, developers must create voluminous mock objects or stubs for dozens of methods to prevent NullPointerExceptions or unmet mock expectations.
With segregated role interfaces, test doubles require only implementing the one or two methods relevant to the test case, often represented as pure Kotlin lambdas, enabling clean, deterministic, and blazing-fast JVM test suites. This razor-thin contract segregation protects client modules from unrelated API refactoring across the repository.

## How to answer in the interview

- **Why:** Show client-method matrix.
- **How:** extract role interfaces.
- **Trade-offs:** note type count.
- **Failure cases:** cite empty fake methods.
- **Production solutions:** finish with staged migration and dependency checks..

## Deep-dive talking points

Construct a consumer-method matrix, capability split, migration adapter and contract tests.

## Follow-up questions

- **Interviewer:** "What is a SAM (Single Abstract Method) interface in Kotlin?"
  **Answer:** "An interface declared as `fun interface` containing exactly one abstract method. In Kotlin, callers can implement it concisely using a standard lambda expression without anonymous class boilerplate."

- **Interviewer:** "How do interface default methods prevent breaking changes?"
  **Answer:** "In Kotlin and Java 8+, adding a method with a default implementation to an existing interface does not force existing implementers to override it, preventing compile-time breakages."

## Self-check rubric

Group six methods into two or three client capabilities and explain migration without empty stubs.

## References and reviewed-on date

- [Robert C. Martin, A Little Architecture](https://blog.cleancoder.com/uncle-bob/2016/01/04/ALittleArchitecture.html) — interface segregation.
- [Android modularization guide](https://developer.android.com/topic/modularization) — client module boundaries.

Technically reviewed against primary documentation on 2026-10-13.

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

Split a large interface by analyzing client call sites, grouping methods by cohesion and consumer role into smaller functional interfaces (`PlaybackStateListener`, `MediaErrorListener`), providing interface default method implementations, and utilizing Kotlin SAM lambdas.

## Interview answer — structured

Splitting a bloated 'Fat Interface' requires role-based refactoring governed by the Interface Segregation Principle (ISP).

1. **Audit Call Sites and Consumer Personas**: Analyze every client implementing the interface. Identify distinct clusters of methods that are invoked together by specific consumers. For example, in a massive `MediaController` interface, the UI widget only cares about play/pause, the metadata notification only cares about track titles, and the analytics telemetry service only cares about buffer underruns and bitrates.

2. **Extract Role Interfaces**: Deconstruct the interface into cohesive, fine-grained contracts:
   - `PlaybackStateListener`: `onPlay()`, `onPause()`
   - `TrackMetadataListener`: `onTrackChanged()`
   - `StreamingQualityListener`: `onBitrateDrop()`, `onBufferStall()`

3. **Leverage Kotlin SAM & Default Implementations**:
   - Convert single-method contracts into `fun interface` (Single Abstract Method), allowing callers to pass simple trailing lambdas.
   - Provide default no-op method bodies (`fun onBuffering() {}`) in interfaces for truly optional callbacks, preventing implementers from writing redundant stub methods.

## Interview answer — deep senior

To migrate safely without breaking existing production consumers, apply the **Adapter or Composite Interface pattern** during refactoring. Declare the new segregated interfaces first. Then, define the legacy interface as a composite that inherits the new interfaces: `interface LegacyMediaListener : PlaybackStateListener, TrackMetadataListener`. Mark the legacy interface `@Deprecated(message = "Use specific segregated listeners")`.

Existing legacy code continues compiling without modification, while all new feature developments adopt the fine-grained role interfaces.

In unit testing, this reduces mocking boilerplate exponentially: testing a play button requires passing a 1-line lambda rather than a 15-method mock instance.

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

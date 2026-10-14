---
id: "PAT-08"
question: "Where do Singleton, Adapter, and Observer show up in Android?"
topic: "Design Patterns"
code: "PAT"
group: "B"
phase: 2
priority: "P1"
order: 199
editorial_status: "reviewed"
---

# PAT-08

## Original interview question

Where do Singleton, Adapter, and Observer show up in Android?

## What the interviewer evaluates

Identify Android examples while separating framework implementation details from pattern intent and lifecycle.

## Explanation in Arabic

أين تظهر أنماط Singleton و Adapter و Observer بشكل طبيعي في مكونات وأطر عمل Android؟

1. نمط الكائن الأحادي (Singleton Pattern in Android):
   - **أين يظهر؟**:
     * كائنات `object` في Kotlin.
     * مدير قاعدة بيانات **Room Database** عبر `Room.databaseBuilder()` الموجه كـ Singleton.
     * عميل شبكة **OkHttpClient** و **Retrofit**؛ مشاركة connection pool و cache عبر التطبيق.
     * خدمات نظام أندرويد (System Services مثل `getSystemService(Context.CONNECTIVITY_SERVICE)`).

2. نمط المحول (Adapter Pattern in Android):
   - **أين يظهر؟**:
     * **`RecyclerView.Adapter`**: يحول قائمة كائنات بيانات غير متوافقة مع الـ Views إلى `ViewHolders` تفهمها شجرة العرض.
     * **`ArrayAdapter`** في الـ Spinners و AutoCompleteTextViews.
     * محولات التنسيق في Retrofit: **`Converter.Factory`** (Moshi / Gson / Kotlinx Serialization) التي تحول HTTP ResponseBody إلى Kotlin Data Classes.

3. نمط المراقب (Observer Pattern in Android):
   - **أين يظهر؟**:
     * **Kotlin Flow & StateFlow & SharedFlow**: اشتراك تفاعلي يراقب انبعاثات البيانات.
     * **`LiveData`** ومراقبتها في الـ UI عبر `observe(lifecycleOwner)`.
     * **`BroadcastReceiver`**: مراقبة أحداث نظام التشغيل (مثل انقطاع الإنترنت أو شحن البطارية).
     * **`SnapshotState`** في Jetpack Compose؛ يعيد تشغيل الـ Composable فور تغير الحالة المراقبة.

## Practical walkthrough

توضيح ظهور الأنماط الثلاثة داخل دورة حياة تطبيق Android:
```kotlin
// 1. SINGLETON: قاعدة بيانات Room واحدة مشتركة عبر Hilt:
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    @Provides
    @Singleton // نمط Singleton يضمن حجز DB واحدة فقط في الذاكرة
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(context, AppDatabase::class.java, "app.db").build()
    }
}

// 2. ADAPTER: تحويل بيانات إلى ViewHolders في RecyclerView:
class UserAdapter : RecyclerView.Adapter<UserViewHolder>() {
    // يحول الـ Data Object إلى Android View layout
}

// 3. OBSERVER: مراقبة الـ StateFlow بنمط مراقب حديث مرتبط بدورة الحياة:
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.uiState.collect { state -> // Observer Pattern
            renderUi(state)
        }
    }
}
```

## Why it matters and how it works

Android APIs often embody pattern intent but add lifecycle and process constraints. Recognizing the pattern helps choose a boundary, while the concrete API contract determines threading, replay, and lifetime.

## Worked example

Scenario: `object CurrencyFormatter` is stateless; `LegacyLocationAdapter` converts callback results; `ProfileViewModel.state: StateFlow<ProfileUiState>` is collected by a lifecycle-aware screen. The formatter is not a session store, and the state stream is not a payment event queue.

## Trade-offs and decision criteria

Using framework APIs can reduce custom pattern boilerplate. A hand-written singleton or observer registry may add leaks and concurrency hazards. Choose existing lifecycle-aware tools when they fit; still test delivery semantics.

## Failure modes

An Activity registers a custom observer on an application singleton and never unregisters, so old Activity remains reachable. Or a ViewModel collects a hot Flow beyond screen lifetime. Tie registration/collection to owner and test rotation.

## Production perspective

A delivery app wraps a vendor GPS callback API with an adapter, injects the repository at an appropriate scope, and exposes location state to UI with lifecycle-aware collection. It never treats cached location as authoritative delivery proof.

## Interview answer — short

Singleton appears in Room database instances, OkHttpClient, and Android System Services. Adapter appears in `RecyclerView.Adapter`, `ArrayAdapter`, and Retrofit Converter Factories. Observer appears in `StateFlow`, `LiveData`, `BroadcastReceiver`, and Jetpack Compose's Snapshot state system.

## Interview answer — structured

These three Gang of Four patterns are deeply woven into the fabric of the Android Operating System and Jetpack libraries.

First, **Singleton Pattern in Android**. Next, with Room Database, creating multiple database instances causes database lock contention and memory thrashing; Room requires a single process-level instance.
Additionally, with OkHttpClient, shares an HTTP connection pool, thread pool, and disk cache across the application. With Android System Services, system managers retrieved via `context.getSystemService()` (e.g. `NotificationManager`, `ConnectivityManager`) act as system-wide service singletons.
**Adapter Pattern in Android**. With RecyclerView.Adapter, converts raw application domain collections (`List<Item>`) into Android UI nodes (`ViewHolder` and `View`).
With Retrofit Converter Factories, adapts raw HTTP byte streams from OkHttp into structured Kotlin data classes via Moshi or Kotlinx Serialization. **Observer Pattern in Android**.
With Reactive Streams (`StateFlow` / `LiveData`), observables emit state updates to observing UI controllers. BroadcastReceiver is the OS acts as the Subject broadcasting system events (battery status, network changes) to registered receiver Observers.
Finally, with Jetpack Compose Runtime, Compose's Snapshot system registers composable scopes as observers of `State<T>` properties, re-executing functions upon mutation.


## Interview answer — deep senior

Under the hood, understanding how the OS implements these patterns avoids common bugs.

First, a non-scoped Singleton holding an Activity Context produces a severe memory leak, which is why Android Singletons must strictly bind to `applicationContext`. Next, in `RecyclerView.Adapter`, calling `notifyDataSetChanged()` is an unoptimized observer broadcast invalidating the whole layout; using `ListAdapter` with `DiffUtil` applies granular observer updates (`notifyItemInserted`, `notifyItemMoved`).
Finally, in Compose, the Snapshot observer system operates at the microsecond level, tracking exact property reads within the Slot Table to skip recomposition of unobserved UI branches.


## How to answer in the interview

- **Why:** Pattern use must match Android lifetime and ownership.
- **How:** Map scoped client, callback adapter and StateFlow observer to three boundaries.
- **Trade-off:** Share listeners deliberately; avoid global state for session data.
- **Failure case:** Leaked Activity, duplicate callback registration or stale view collector.
- **Production solution:** Rotation/process-recreation tests plus explicit listener cleanup.

## Deep-dive talking points

Map object scope, SDK adaptation and observation; distinguish LiveData/Flow lifecycle behavior.

## Follow-up questions

- **Interviewer:** "Why does OkHttpClient need to be a Singleton?"
  **Answer:** "Each OkHttpClient instance creates its own connection pool, thread pool, and cache. Creating multiple instances wastes memory, exhausts file descriptors, and prevents HTTP/2 multiplexing across requests."

- **Interviewer:** "How does DiffUtil improve upon standard RecyclerView.Adapter updates?"
  **Answer:** "DiffUtil calculates the minimal list mutations on a background thread using Myers' diff algorithm, dispatching precise structural adapter updates rather than redrawing the whole screen."

## Self-check rubric

Give one Android example of each pattern and one lifecycle failure for Singleton or Observer.

## References and reviewed-on date

- [Kotlin object declarations](https://kotlinlang.org/docs/object-declarations.html) — object lifetime syntax.
- [Android LiveData overview](https://developer.android.com/topic/libraries/architecture/livedata) — observer behavior.

Technically reviewed against primary documentation on 2026-10-13.

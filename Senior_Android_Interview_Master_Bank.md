# Senior Android Engineer — Interview Master Bank

> النسخة المنظمة من الأسئلة التي قدّمتها + تغطية جديدة لسد فجوات Senior Android. الأسئلة بالإنجليزية لتتدرب على صياغتها في المقابلة؛ الإرشادات بالعربية.

## كيف تستخدم الملف

- داخل كل Topic: **A = Fundamentals**، ثم **B = Practical / Implementation**، ثم **C = Senior Scenarios / Trade-offs**.
- لكل سؤال: حضّر تعريفًا موجزًا بالإنجليزية، مثال Android، خطأ شائعًا، Trade-off، وكود أو اختبار لو مناسب.
- غيّر خانة `[ ]` إلى `[x]` عند المراجعة، واستخدم الأكواد `COR-01` وغيرها للرجوع السريع للسؤال.
- **P1** = أساسي للمقابلات؛ **P2** = مهم للتغطية المتكاملة؛ **Bonus** = تخصص الدفع/الأمان.
- الأسئلة في أول القائمة مبنية على المواد التي أرسلتها. الموضوعات المكملة تشمل Android Lifecycle/Process Death، Room، WorkManager، Networking، R8، Performance، Testing، وLeadership.

## خارطة المنهج

| المرحلة | الفكرة | الموديولات |
|---|---|---|
| 1 | الأساسيات وسلوك الـRuntime | Kotlin, Android Fundamentals, Memory & Performance, Coroutines, Flow |
| 2 | تصميم الكود واعتماديته | Architecture, SOLID, Patterns, DI |
| 3 | بناء Features في Production | Compose, Data/Networking, Background Work, Security |
| 4 | هندسة المنتج والتسليم | System Design, Modularization, Gradle/Release, Testing, CI/CD & Git |
| 5 | Senior depth | Algorithms, Technical Leadership, Payment/POS Bonus |

## الفهرس وإحصائيات الأسئلة

| الكود | Topic | المرحلة | الأولوية | الأسئلة |
|---|---|---:|---|---:|
| `KOT` | Kotlin Core & Advanced | 1 | P1 | 30 |
| `AND` | Android Fundamentals, Lifecycle & Context | 1 | P1 | 25 |
| `MEM` | Memory Management, ANR & Performance | 1 | P1 | 26 |
| `COR` | Kotlin Coroutines & Concurrency | 1 | P1 | 32 |
| `FLO` | Flow, StateFlow, SharedFlow & Channels | 1 | P1 | 32 |
| `ARC` | Clean Architecture, MVVM, MVI & UDF | 2 | P1 | 26 |
| `SOL` | SOLID & Object-Oriented Design | 2 | P1 | 20 |
| `PAT` | Design Patterns | 2 | P1 | 18 |
| `DI` | Dependency Injection: Hilt & Dagger | 2 | P1 | 20 |
| `COM` | Jetpack Compose | 3 | P1 | 28 |
| `DAT` | Networking, Room, DataStore & Offline-First | 3 | P1 | 22 |
| `BG` | Background Work, WorkManager & OS Constraints | 3 | P1 | 18 |
| `SEC` | Android Security, Crypto & Fintech Threat Modeling | 3 | P1 | 32 |
| `SYS` | Android System Design & Architecture Decisions | 4 | P1 | 24 |
| `MOD` | Gradle Modularization & Dependency Boundaries | 4 | P1 | 21 |
| `BLD` | Gradle, AGP, R8, Signing & Release Engineering | 4 | P1 | 21 |
| `TST` | Testing, Quality & Reliability | 4 | P1 | 24 |
| `CIC` | CI/CD, Git & Team Delivery | 4 | P2 | 20 |
| `DSA` | Data Structures, Algorithms & Big O | 5 | P2 | 16 |
| `LEAD` | Senior Ownership, Communication & Technical Leadership | 5 | P2 | 15 |
| `PAY` | Bonus: Payment/POS & Security Scenarios | 5 | P2 / Domain bonus | 15 |
| **Total** | **21 topics** | | | **485** |

---

## 01. Kotlin Core & Advanced  — `KOT` · P1

**Phase 1** · **30 questions**

### A. Fundamentals

- [ ] **KOT-01** — What is Kotlin, and why is it popular in Android development?
- [ ] **KOT-02** — What is the difference between val and var? Does val guarantee immutability?
- [ ] **KOT-03** — Explain Kotlin null safety, safe calls, Elvis operator, and the not-null assertion operator.
- [ ] **KOT-04** — What is the difference between == and ===?
- [ ] **KOT-05** — Compare data class, regular class, object, and companion object.
- [ ] **KOT-06** — Compare sealed class, sealed interface, enum class, and abstract class.
- [ ] **KOT-07** — What are higher-order functions and lambdas?
- [ ] **KOT-08** — Explain let, run, with, apply, and also with appropriate use cases.
- [ ] **KOT-09** — What are extension functions? Can they override member functions?
- [ ] **KOT-10** — Compare lazy and lateinit. When is each appropriate?
- [ ] **KOT-11** — What are local functions, and when would you use one?

### B. Practical / Implementation

- [ ] **KOT-12** — What does inline do? What are its costs and benefits?
- [ ] **KOT-13** — Explain noinline, crossinline, non-local return, and reified type parameters.
- [ ] **KOT-14** — Explain Kotlin variance: in, out, invariance, and star projections.
- [ ] **KOT-15** — What is delegation? Compare interface delegation and delegated properties.
- [ ] **KOT-16** — What is the difference between List, MutableList, ArrayList, and Sequence?
- [ ] **KOT-17** — Explain lazy sequences versus eager collection operations.
- [ ] **KOT-18** — What is a typealias? When does it help or hurt readability?
- [ ] **KOT-19** — What is Kotlin Result? How would you model domain errors instead?
- [ ] **KOT-20** — Explain scope-function receiver versus argument semantics.
- [ ] **KOT-21** — What are value classes, and what performance/interop caveats do they have?
- [ ] **KOT-22** — What is Reflection, and when is it expensive or risky?
- [ ] **KOT-23** — What is Java/Kotlin interoperability (platform types, SAM interfaces, nullability)?
- [ ] **KOT-24** — What is JNI, and why might an Android project use C++?

### C. Senior Scenarios / Trade-offs

- [ ] **KOT-25** — Your app has a mutable val list shared across threads. Is it thread-safe? Explain.
- [ ] **KOT-26** — When would a sealed hierarchy be better than an enum for UI or payment states?
- [ ] **KOT-27** — When does inline cause code bloat rather than a performance win?
- [ ] **KOT-28** — How do you design a type-safe result API without losing error information?
- [ ] **KOT-29** — Does storing sensitive values in native code prevent reverse engineering?
- [ ] **KOT-30** — How would you review a Kotlin API for readability, null safety, and allocation cost?

---

## 02. Android Fundamentals, Lifecycle & Context  — `AND` · P1

**Phase 1** · **25 questions**

### A. Fundamentals

- [ ] **AND-01** — What are Activity, Fragment, Service, BroadcastReceiver, and ContentProvider?
- [ ] **AND-02** — Explain the Activity and Fragment lifecycles.
- [ ] **AND-03** — Compare Fragment lifecycle and Fragment view lifecycle.
- [ ] **AND-04** — What is Context? Compare Activity Context and Application Context.
- [ ] **AND-05** — When must you use an Activity Context rather than Application Context?
- [ ] **AND-06** — What are configuration changes, and what survives them?
- [ ] **AND-07** — What is process death? How is it different from configuration change?
- [ ] **AND-08** — What is ViewModel, and when is it cleared?
- [ ] **AND-09** — Compare ViewModel, SavedStateHandle, rememberSaveable, and persistent storage.
- [ ] **AND-10** — What are Intent and PendingIntent? Explain explicit versus implicit intents.
- [ ] **AND-11** — What is the role of AndroidManifest.xml?

### B. Practical / Implementation

- [ ] **AND-12** — How do you restore a screen after process death without losing user input?
- [ ] **AND-13** — How do you handle runtime permissions and denial/permanent denial?
- [ ] **AND-14** — What is the Activity Result API, and why use it?
- [ ] **AND-15** — Compare Activity, Fragment, Compose navigation, and deep links.
- [ ] **AND-16** — How do you protect exported Android components?
- [ ] **AND-17** — How should you register/unregister lifecycle-dependent listeners?
- [ ] **AND-18** — How do multi-window, rotation, and background/foreground transitions affect state?
- [ ] **AND-19** — What are foreground services and notification requirements at a high level?
- [ ] **AND-20** — How do you share data or communicate across processes (Binder/IPC)?

### C. Senior Scenarios / Trade-offs

- [ ] **AND-21** — A payment screen is killed by Android mid-operation. What must be reconstructed, and what must not be repeated?
- [ ] **AND-22** — A crash occurs only after backgrounding the app for several hours. How would you investigate lifecycle and process restoration?
- [ ] **AND-23** — A Singleton needs a Context. How do you choose the correct lifecycle and prevent a leak?
- [ ] **AND-24** — Your app receives an untrusted deep link. What validation should happen before navigation?
- [ ] **AND-25** — How would you support predictable navigation after notification taps and process recreation?

---

## 03. Memory Management, ANR & Performance  — `MEM` · P1

**Phase 1** · **26 questions**

### A. Fundamentals

- [ ] **MEM-01** — What is memory management in Android? What does garbage collection do?
- [ ] **MEM-02** — What are GC roots, and how does the GC determine reachability?
- [ ] **MEM-03** — Compare stack and heap at a high level. What lives on each?
- [ ] **MEM-04** — What is a memory leak, and how is it different from a large memory allocation?
- [ ] **MEM-05** — Compare memory leak, OutOfMemoryError, ANR, and StackOverflowError.
- [ ] **MEM-06** — What causes boxing/unboxing, and when does it matter?
- [ ] **MEM-07** — Explain int versus Integer in Java interoperability.
- [ ] **MEM-08** — Why can a Singleton holding Activity Context leak memory?
- [ ] **MEM-09** — Can a ViewModel or coroutine leak memory? How?
- [ ] **MEM-10** — What is an ANR, and what are common causes?

### B. Practical / Implementation

- [ ] **MEM-11** — Why must Fragment ViewBinding references be released with the view lifecycle?
- [ ] **MEM-12** — How can callbacks, Handler, observers, listeners, or static references cause leaks?
- [ ] **MEM-13** — How do Bitmap allocations and image-loading libraries affect memory?
- [ ] **MEM-14** — How do you analyze a heap dump and use LeakCanary?
- [ ] **MEM-15** — How do you use Android Studio Memory/CPU Profilers?
- [ ] **MEM-16** — What are StrictMode, Perfetto/System Trace, and Android vitals useful for?
- [ ] **MEM-17** — What is UI jank? Explain frame timing, recompositions, and excessive work on Main.
- [ ] **MEM-18** — How do Baseline Profiles and Macrobenchmark help performance?
- [ ] **MEM-19** — What are cold start, warm start, and hot start?
- [ ] **MEM-20** — How can cache design and large lists trigger memory or performance regressions?

### C. Senior Scenarios / Trade-offs

- [ ] **MEM-21** — Production reports increasing memory usage over days. How do you isolate the cause?
- [ ] **MEM-22** — Your main thread is blocked even though you launched a coroutine. Why?
- [ ] **MEM-23** — An app freezes only when decoding a large image. How do you diagnose it?
- [ ] **MEM-24** — How do you reduce slow app startup without breaking correctness?
- [ ] **MEM-25** — How do you find a rare ANR associated with database lock contention?
- [ ] **MEM-26** — How would you create measurable performance budgets and regression tests?

---

## 04. Kotlin Coroutines & Concurrency  — `COR` · P1

**Phase 1** · **32 questions**

### A. Fundamentals

- [ ] **COR-01** — What is a coroutine, and how is it different from a thread?
- [ ] **COR-02** — What does suspend mean? Does a suspend function imply background execution?
- [ ] **COR-03** — What are CoroutineScope, CoroutineContext, Job, and Deferred?
- [ ] **COR-04** — What is structured concurrency, and why is it valuable?
- [ ] **COR-05** — Compare launch and async/await.
- [ ] **COR-06** — Compare viewModelScope, lifecycleScope, and custom application-level scopes.
- [ ] **COR-07** — What do Dispatchers.Main, IO, Default, and Unconfined do?
- [ ] **COR-08** — Does Dispatchers.Main use the UI thread? Does IO use a pool?
- [ ] **COR-09** — What is withContext? When do you use it?
- [ ] **COR-10** — What is cooperative cancellation? What are cancellation points?

### B. Practical / Implementation

- [ ] **COR-11** — Compare coroutineScope and supervisorScope including failure propagation.
- [ ] **COR-12** — Compare Job and SupervisorJob.
- [ ] **COR-13** — What happens to a parent and siblings when a child coroutine fails?
- [ ] **COR-14** — When does CoroutineExceptionHandler run, and where does it not help?
- [ ] **COR-15** — How do launch exceptions differ from async exceptions?
- [ ] **COR-16** — How do you propagate CancellationException correctly?
- [ ] **COR-17** — How do timeout, withTimeout, and withTimeoutOrNull work?
- [ ] **COR-18** — How do you retry requests with exponential backoff and jitter?
- [ ] **COR-19** — What is a race condition? Why are coroutines not automatically thread-safe?
- [ ] **COR-20** — Compare Mutex, synchronized, atomic types, and confinement.
- [ ] **COR-21** — What is a semaphore? How do you limit parallelism?
- [ ] **COR-22** — When should you use ensureActive or yield during CPU-bound work?
- [ ] **COR-23** — How do you safely adapt a callback API to suspending code?
- [ ] **COR-24** — What is the risk of GlobalScope or creating a scope inside each repository method?

### C. Senior Scenarios / Trade-offs

- [ ] **COR-25** — Call 3 dependent APIs concurrently. If one fails, how do you cancel siblings and return a consistent failure?
- [ ] **COR-26** — Call 3 independent APIs concurrently. How do you preserve partial success without swallowing cancellation?
- [ ] **COR-27** — A payment timeout occurs after a request reaches the server. How do you avoid duplicate charges on retry?
- [ ] **COR-28** — Two coroutines update a shared balance. Demonstrate and fix a race condition.
- [ ] **COR-29** — A blocking SDK call does not respond to coroutine cancellation. What can you do?
- [ ] **COR-30** — A ViewModel disappears but critical persistence must finish. Who should own that work?
- [ ] **COR-31** — A coroutine starts on Main, calls blocking library code, and causes ANR. Explain the exact failure and fix.
- [ ] **COR-32** — How do you test concurrent cancellation, supervision, and a timeout deterministically?

---

## 05. Flow, StateFlow, SharedFlow & Channels  — `FLO` · P1

**Phase 1** · **32 questions**

### A. Fundamentals

- [ ] **FLO-01** — What is Flow? Compare Flow and a single suspend function.
- [ ] **FLO-02** — Explain cold flows and what happens with multiple collectors.
- [ ] **FLO-03** — What are StateFlow and SharedFlow? Why are they hot?
- [ ] **FLO-04** — Compare Flow, StateFlow, SharedFlow, and LiveData.
- [ ] **FLO-05** — Why does MutableStateFlow require an initial value?
- [ ] **FLO-06** — What is conflation, and how does StateFlow use equality to suppress repeated states?
- [ ] **FLO-07** — How do you expose read-only state via asStateFlow()?
- [ ] **FLO-08** — What are stateIn and shareIn?
- [ ] **FLO-09** — Compare SharingStarted.Eagerly, Lazily, and WhileSubscribed.
- [ ] **FLO-10** — What is the difference between state and transient events?

### B. Practical / Implementation

- [ ] **FLO-11** — Explain map, filter, transform, onEach, and launchIn.
- [ ] **FLO-12** — Compare collect, collectLatest, and first.
- [ ] **FLO-13** — Compare combine and zip.
- [ ] **FLO-14** — Compare flatMapLatest, flatMapConcat, and flatMapMerge.
- [ ] **FLO-15** — Explain debounce and distinctUntilChanged for search.
- [ ] **FLO-16** — Compare merge, buffer, conflate, and collectLatest.
- [ ] **FLO-17** — How does flowOn affect upstream execution?
- [ ] **FLO-18** — Compare catch, retry, retryWhen, and onCompletion.
- [ ] **FLO-19** — Explain replay, extraBufferCapacity, and BufferOverflow in SharedFlow.
- [ ] **FLO-20** — Compare Channel and SharedFlow, including event-loss and delivery caveats.
- [ ] **FLO-21** — What is callbackFlow? What does awaitClose do?
- [ ] **FLO-22** — Compare repeatOnLifecycle and collectAsStateWithLifecycle.
- [ ] **FLO-23** — What happens if a UI collects indefinitely without lifecycle awareness?
- [ ] **FLO-24** — How do you test Flow/StateFlow with runTest and Turbine?

### C. Senior Scenarios / Trade-offs

- [ ] **FLO-25** — Design a search box that debounces input and cancels stale API calls.
- [ ] **FLO-26** — Your UI must display the most recent state after rotation. What stream type do you use and why?
- [ ] **FLO-27** — A navigation event fires twice after rotation. How do you investigate event modeling and consumption?
- [ ] **FLO-28** — A flow combines cached Room data with remote refresh. Who is source of truth?
- [ ] **FLO-29** — A rapidly emitting upstream stream makes rendering slow. Which backpressure strategy fits?
- [ ] **FLO-30** — A SharedFlow event has no active subscribers. What guarantees do replay and buffering actually give?
- [ ] **FLO-31** — How do you choose SharingStarted for battery, correctness, and subscription behavior?
- [ ] **FLO-32** — What is the danger of using runCatching around cancellable flow/coroutine work?

---

## 06. Clean Architecture, MVVM, MVI & UDF  — `ARC` · P1

**Phase 2** · **26 questions**

### A. Fundamentals

- [ ] **ARC-01** — What is Clean Architecture, and what problem does it solve?
- [ ] **ARC-02** — Explain Presentation, Domain, and Data layers.
- [ ] **ARC-03** — What is the Dependency Rule, and in which direction should dependencies point?
- [ ] **ARC-04** — What is the Repository pattern? What is a UseCase?
- [ ] **ARC-05** — What belongs in ViewModel versus UseCase versus Repository?
- [ ] **ARC-06** — Where should DTOs, Room entities, domain models, and UI models live?
- [ ] **ARC-07** — Why do we use mappers between models?
- [ ] **ARC-08** — Compare MVC, MVP, MVVM, MVI, and UDF.
- [ ] **ARC-09** — How does UI state differ from business/domain state?
- [ ] **ARC-10** — What is Single Source of Truth (SSOT)?

### B. Practical / Implementation

- [ ] **ARC-11** — How do you expose loading, content, empty, and error state?
- [ ] **ARC-12** — How should domain/data errors be mapped into actionable UI errors?
- [ ] **ARC-13** — When is a separate domain layer genuinely useful versus optional?
- [ ] **ARC-14** — Why should UI not call Retrofit or Room DAOs directly?
- [ ] **ARC-15** — When do you introduce interfaces, and when can concrete implementations be sufficient?
- [ ] **ARC-16** — Compare package-by-layer and package-by-feature.
- [ ] **ARC-17** — How do you manage one-time effects in a UDF architecture?
- [ ] **ARC-18** — How do you keep a ViewModel main-safe and testable?
- [ ] **ARC-19** — How do you handle cache and server updates within the data layer?
- [ ] **ARC-20** — How do you test Presentation, Domain, and Data independently?

### C. Senior Scenarios / Trade-offs

- [ ] **ARC-21** — A ViewModel contains 1,000 lines of networking, mapping, and business logic. How do you refactor it incrementally?
- [ ] **ARC-22** — A Repository returns an API DTO directly to Compose. What coupling risks follow?
- [ ] **ARC-23** — You have a very small app. When is Clean Architecture overengineering?
- [ ] **ARC-24** — Design a cross-feature account/session state without creating circular dependencies.
- [ ] **ARC-25** — Compare MVVM and MVI for a payment state machine with many transitions.
- [ ] **ARC-26** — How do you enforce boundaries without a huge number of boilerplate interfaces?

---

## 07. SOLID & Object-Oriented Design  — `SOL` · P1

**Phase 2** · **20 questions**

### A. Fundamentals

- [ ] **SOL-01** — What does SOLID stand for, and why does it matter?
- [ ] **SOL-02** — Explain Single Responsibility Principle with an Android example.
- [ ] **SOL-03** — Explain Open/Closed Principle with an Android example.
- [ ] **SOL-04** — Explain Liskov Substitution Principle with an Android example.
- [ ] **SOL-05** — Explain Interface Segregation Principle with an Android example.
- [ ] **SOL-06** — Explain Dependency Inversion Principle with an Android example.
- [ ] **SOL-07** — Compare DIP and Dependency Injection (DI).
- [ ] **SOL-08** — Compare SRP and ISP.
- [ ] **SOL-09** — What is composition over inheritance?

### B. Practical / Implementation

- [ ] **SOL-10** — A BaseFragment requires setupToolbar() but some screens have no toolbar. When does this violate LSP?
- [ ] **SOL-11** — How would you replace a giant BaseActivity with smaller composable behaviors?
- [ ] **SOL-12** — How does strategy-based payment routing support OCP?
- [ ] **SOL-13** — Why can creating an interface for every class make design worse?
- [ ] **SOL-14** — How does Hilt support dependency wiring without automatically guaranteeing DIP?
- [ ] **SOL-15** — How would you split a large interface with mostly unused methods?
- [ ] **SOL-16** — How do you identify cohesive responsibilities within a God Class?

### C. Senior Scenarios / Trade-offs

- [ ] **SOL-17** — A subclass needs to throw UnsupportedOperationException for a base behavior. What design principle might be violated?
- [ ] **SOL-18** — A new payment provider requires editing 10 existing classes. Which principles would help?
- [ ] **SOL-19** — When should you deliberately accept a little duplication instead of introducing an abstraction?
- [ ] **SOL-20** — How would you explain SOLID trade-offs to a team overengineering a small feature?

---

## 08. Design Patterns  — `PAT` · P1

**Phase 2** · **18 questions**

### A. Fundamentals

- [ ] **PAT-01** — What is a design pattern, and how is it different from architecture?
- [ ] **PAT-02** — Compare creational, structural, and behavioral patterns.
- [ ] **PAT-03** — Explain Singleton, Factory, Abstract Factory, and Builder.
- [ ] **PAT-04** — Explain Adapter, Facade, Decorator, and Proxy.
- [ ] **PAT-05** — Explain Observer, Strategy, State, Command, and Chain of Responsibility.
- [ ] **PAT-06** — Where does Repository fit as an architectural/data-access pattern?
- [ ] **PAT-07** — What does Dependency Injection as a pattern accomplish?

### B. Practical / Implementation

- [ ] **PAT-08** — Where do Singleton, Adapter, and Observer show up in Android?
- [ ] **PAT-09** — Compare State and Strategy with concrete examples.
- [ ] **PAT-10** — Compare Factory and Abstract Factory.
- [ ] **PAT-11** — Where might Builder be useful in API or SDK design?
- [ ] **PAT-12** — How would Facade simplify an unreliable third-party SDK?
- [ ] **PAT-13** — How do callback/lifecycle observers relate to Flow and LiveData?
- [ ] **PAT-14** — How can an explicit state machine replace scattered boolean flags?

### C. Senior Scenarios / Trade-offs

- [ ] **PAT-15** — Design multiple payment providers with Strategy or Factory. How do you avoid a god-factory?
- [ ] **PAT-16** — You need to swap vendor SDKs with different callbacks. Which patterns and boundaries help?
- [ ] **PAT-17** — A global Singleton makes tests order-dependent. How do you redesign ownership?
- [ ] **PAT-18** — How can patterns turn into unnecessary indirection? Give an example.

---

## 09. Dependency Injection: Hilt & Dagger  — `DI` · P1

**Phase 2** · **20 questions**

### A. Fundamentals

- [ ] **DI-01** — What is DI and which problems does it solve?
- [ ] **DI-02** — Compare constructor injection, field injection, and manual DI.
- [ ] **DI-03** — Compare Dagger and Hilt.
- [ ] **DI-04** — What do @Inject, @Module, @Provides, and @Binds do?
- [ ] **DI-05** — What are @HiltAndroidApp, @AndroidEntryPoint, and @HiltViewModel?
- [ ] **DI-06** — What is a DI graph? What is a component hierarchy?
- [ ] **DI-07** — Compare @Singleton, @ActivityScoped, and @ViewModelScoped.
- [ ] **DI-08** — What is a qualifier? Compare @Named and custom qualifiers.

### B. Practical / Implementation

- [ ] **DI-09** — How do you provide Retrofit, Room, and an interface implementation with Hilt?
- [ ] **DI-10** — When do you choose @Binds over @Provides?
- [ ] **DI-11** — How do you inject multiple implementations of the same contract?
- [ ] **DI-12** — How do scopes interact with Context and lifecycle ownership?
- [ ] **DI-13** — How do you replace dependencies in unit and instrumented tests?
- [ ] **DI-14** — What problems occur if every dependency is a Singleton?
- [ ] **DI-15** — How do you handle assisted injection or runtime parameters?
- [ ] **DI-16** — How do you integrate DI with multiple Gradle modules?

### C. Senior Scenarios / Trade-offs

- [ ] **DI-17** — An SDK constructs objects internally and cannot use Hilt. How do you integrate it?
- [ ] **DI-18** — An Activity Context was accidentally captured in a Singleton. Where is the DI design error?
- [ ] **DI-19** — A dynamic-feature module needs dependencies supplied by the base app. What are the options?
- [ ] **DI-20** — How would you migrate manual DI to Hilt while keeping tests stable?

---

## 10. Jetpack Compose  — `COM` · P1

**Phase 3** · **28 questions**

### A. Fundamentals

- [ ] **COM-01** — What is Compose? Compare declarative Compose and XML Views.
- [ ] **COM-02** — What is a @Composable function? What is recomposition?
- [ ] **COM-03** — What triggers recomposition, and what can be skipped?
- [ ] **COM-04** — What are state, snapshot state, and state hoisting?
- [ ] **COM-05** — Compare remember, rememberSaveable, and ViewModel state.
- [ ] **COM-06** — What is Unidirectional Data Flow in Compose?
- [ ] **COM-07** — What does Modifier do, and why does ordering matter?
- [ ] **COM-08** — How do you model UI state with StateFlow?
- [ ] **COM-09** — What does collectAsStateWithLifecycle() solve?
- [ ] **COM-10** — What are LaunchedEffect, DisposableEffect, SideEffect, and rememberCoroutineScope?

### B. Practical / Implementation

- [ ] **COM-11** — Compare LaunchedEffect(Unit) and LaunchedEffect(key).
- [ ] **COM-12** — What are rememberUpdatedState, derivedStateOf, and snapshotFlow?
- [ ] **COM-13** — How do you correctly implement Snackbar, navigation, and callbacks?
- [ ] **COM-14** — What are stable keys and content types in LazyColumn?
- [ ] **COM-15** — What does stability mean for Compose types and parameters?
- [ ] **COM-16** — How do you identify avoidable recomposition?
- [ ] **COM-17** — How do you optimize a long list and expensive calculations?
- [ ] **COM-18** — What are Route Composable and Screen Composable?
- [ ] **COM-19** — How do you implement a reusable design system and themes?
- [ ] **COM-20** — How do you handle previews, permissions, and navigation?
- [ ] **COM-21** — What is NavHost, and how is state restored after process death?
- [ ] **COM-22** — How do you support accessibility, screen readers, and adaptive layouts?

### C. Senior Scenarios / Trade-offs

- [ ] **COM-23** — A Compose screen re-renders excessively after each keystroke. How do you profile and fix it?
- [ ] **COM-24** — A listener keeps working after a composable leaves composition. Which effect is wrong?
- [ ] **COM-25** — A user taps Save twice while a request is in flight. How do you make UI and domain behavior safe?
- [ ] **COM-26** — A LazyColumn scroll position resets after data refresh. What should you inspect?
- [ ] **COM-27** — How do you test a screen with loading, error, success, and permission states?
- [ ] **COM-28** — When should you avoid derivedStateOf because its overhead exceeds the benefit?

---

## 11. Networking, Room, DataStore & Offline-First  — `DAT` · P1

**Phase 3** · **22 questions**

### A. Fundamentals

- [ ] **DAT-01** — How do Retrofit and OkHttp fit into a typical Android networking stack?
- [ ] **DAT-02** — What are HTTP methods, common status codes, and idempotency?
- [ ] **DAT-03** — What are connect, read, write, and call timeouts?
- [ ] **DAT-04** — Compare REST, GraphQL, and WebSockets at a high level.
- [ ] **DAT-05** — Compare Room, DataStore, and SharedPreferences.
- [ ] **DAT-06** — What is a Room Entity, DAO, transaction, migration, and Flow query?
- [ ] **DAT-07** — What is an offline-first application?
- [ ] **DAT-08** — What are cache-first, network-first, and stale-while-revalidate strategies?

### B. Practical / Implementation

- [ ] **DAT-09** — How do you implement authentication interceptors and refresh-token logic safely?
- [ ] **DAT-10** — How do you avoid concurrent refresh-token races?
- [ ] **DAT-11** — How do you design a migration that preserves user data?
- [ ] **DAT-12** — How do you use Room transactions for all-or-nothing writes?
- [ ] **DAT-13** — How would you implement Paging 3 and RemoteMediator?
- [ ] **DAT-14** — How do you design retries while respecting idempotency and rate limits?
- [ ] **DAT-15** — How do you sync local writes after offline edits?
- [ ] **DAT-16** — How should conflicts be resolved when local and server state diverge?
- [ ] **DAT-17** — How do you manage caching expiration and invalidation?

### C. Senior Scenarios / Trade-offs

- [ ] **DAT-18** — A transaction is saved but disappears after restart in release builds only. What should you investigate?
- [ ] **DAT-19** — Two refresh-token requests both invalidate the session. How do you serialize refresh correctly?
- [ ] **DAT-20** — The server accepted a payment but the response was lost. How do you recover safely?
- [ ] **DAT-21** — Design a paginated news feed that opens instantly and syncs when online.
- [ ] **DAT-22** — You must migrate encrypted and unencrypted local databases. How do you protect against data loss?

---

## 12. Background Work, WorkManager & OS Constraints  — `BG` · P1

**Phase 3** · **18 questions**

### A. Fundamentals

- [ ] **BG-01** — When should you use a coroutine, WorkManager, foreground service, or AlarmManager?
- [ ] **BG-02** — What is WorkManager, and what guarantees does it provide?
- [ ] **BG-03** — Compare OneTimeWorkRequest and PeriodicWorkRequest.
- [ ] **BG-04** — What are Worker, CoroutineWorker, and ListenableWorker?
- [ ] **BG-05** — What are constraints, backoff policies, and unique work?
- [ ] **BG-06** — What are Doze mode and app standby restrictions?
- [ ] **BG-07** — What is the difference between lifecycle-bound work and durable work?

### B. Practical / Implementation

- [ ] **BG-08** — How do you queue offline synchronization and retry with WorkManager?
- [ ] **BG-09** — How do you cancel or replace unique background work?
- [ ] **BG-10** — How do you persist progress and communicate it to UI?
- [ ] **BG-11** — How do you avoid duplicate processing when a Worker is retried?
- [ ] **BG-12** — What are foreground-service restrictions and notification requirements?
- [ ] **BG-13** — When should an exact alarm be used instead of periodic work?
- [ ] **BG-14** — How do you coordinate WorkManager with repository and database transactions?

### C. Senior Scenarios / Trade-offs

- [ ] **BG-15** — An upload must survive process death and network loss. Design its lifecycle.
- [ ] **BG-16** — A job ran twice after a crash. How do you enforce idempotency?
- [ ] **BG-17** — A business requirement asks for second-perfect periodic background execution. What Android limitations matter?
- [ ] **BG-18** — A payment reversal must eventually reach backend after app exits. What durable mechanism and server contract do you need?

---

## 13. Android Security, Crypto & Fintech Threat Modeling  — `SEC` · P1

**Phase 3** · **32 questions**

### A. Fundamentals

- [ ] **SEC-01** — What is the Android application sandbox and permission model?
- [ ] **SEC-02** — What is Android Keystore, and what is hardware-backed key storage?
- [ ] **SEC-03** — Compare cryptographic keys, access tokens, refresh tokens, API keys, and passwords.
- [ ] **SEC-04** — Why is local.properties not a runtime security mechanism?
- [ ] **SEC-05** — Can an API secret bundled into an APK ever be fully secret?
- [ ] **SEC-06** — What are encryption at rest and encryption in transit?
- [ ] **SEC-07** — Compare encryption, hashing, HMAC, and digital signatures.
- [ ] **SEC-08** — What is TLS and what does certificate pinning add?
- [ ] **SEC-09** — What is obfuscation, and what are its limitations?
- [ ] **SEC-10** — What is reverse engineering? What do root, hooking, and instrumentation change?

### B. Practical / Implementation

- [ ] **SEC-11** — How do you implement Keystore-backed encryption for small app secrets?
- [ ] **SEC-12** — What should you know about the deprecated EncryptedSharedPreferences API?
- [ ] **SEC-13** — How do you handle key invalidation, key rotation, backups, and reinstall?
- [ ] **SEC-14** — Where should access and refresh tokens be stored and how are they revoked?
- [ ] **SEC-15** — How do you prevent token leakage through logs, screenshots, crash reports, and analytics?
- [ ] **SEC-16** — Why might CharArray be preferable to String for passwords, and what are its limitations?
- [ ] **SEC-17** — How do you protect sensitive buffers and reduce memory residence time?
- [ ] **SEC-18** — How do you validate exported components, deep links, and PendingIntents?
- [ ] **SEC-19** — How do you secure WebView, JavaScript bridges, and file/content URIs?
- [ ] **SEC-20** — How do you implement certificate pinning with a rotation/recovery strategy?
- [ ] **SEC-21** — What is Play Integrity API? What trust decisions must happen on the server?
- [ ] **SEC-22** — How do you design biometric-gated access to a Keystore operation?
- [ ] **SEC-23** — What are the threats of insecure backup and local database files?
- [ ] **SEC-24** — How can native code/JNI be analyzed or instrumented?
- [ ] **SEC-25** — What are OWASP MASVS/MASTG, and how do they guide mobile security reviews?

### C. Senior Scenarios / Trade-offs

- [ ] **SEC-26** — Design secure session storage for a fintech app on a potentially compromised device.
- [ ] **SEC-27** — An attacker modifies an APK and bypasses client-only checks. How should the backend defend itself?
- [ ] **SEC-28** — An embedded TLS certificate expires. How do you rotate pins without bricking the app?
- [ ] **SEC-29** — A rooted device can hook your code with Frida. What protections help and what can they not guarantee?
- [ ] **SEC-30** — A payment app must mask PAN and avoid sensitive logs. Design a logging/observability policy.
- [ ] **SEC-31** — A team puts a private API key in BuildConfig from local.properties. Why is this not sufficient?
- [ ] **SEC-32** — A security SDK falsely flags legitimate devices. How would you handle risk and availability?

---

## 14. Android System Design & Architecture Decisions  — `SYS` · P1

**Phase 4** · **24 questions**

### A. Fundamentals

- [ ] **SYS-01** — How do you begin a mobile system-design interview (requirements, scale, constraints, trade-offs)?
- [ ] **SYS-02** — Design a scalable multi-feature Android application.
- [ ] **SYS-03** — Design login, session management, and secure token refresh.
- [ ] **SYS-04** — Design an offline-first system with a local source of truth.
- [ ] **SYS-05** — Design a robust payment transaction lifecycle.
- [ ] **SYS-06** — Design caching, pagination, and remote synchronization.
- [ ] **SYS-07** — Design a notification system with deep links.
- [ ] **SYS-08** — Design a feature flags and staged rollout system.
- [ ] **SYS-09** — Design analytics, logs, metrics, and crash reporting.

### B. Practical / Implementation

- [ ] **SYS-10** — How do you model states and transitions with an explicit state machine?
- [ ] **SYS-11** — How do you deal with concurrency, timeouts, retries, and idempotency?
- [ ] **SYS-12** — How do you make a reusable Android SDK with a stable public API?
- [ ] **SYS-13** — How do you manage database migrations and backwards compatibility?
- [ ] **SYS-14** — How do you design API boundaries for multiple teams?
- [ ] **SYS-15** — Compare monolith and multi-module designs.
- [ ] **SYS-16** — Compare simple MVVM and Clean Architecture for different app sizes.
- [ ] **SYS-17** — How do you design operational monitoring and remote kill switches?
- [ ] **SYS-18** — How do you support version skew between older apps and newer backend contracts?

### C. Senior Scenarios / Trade-offs

- [ ] **SYS-19** — Your app has 20 feature teams and takes 25 minutes to build. How do you redesign team ownership and dependencies?
- [ ] **SYS-20** — A payment was authorized but the UI timed out. Design recovery and reconciliation.
- [ ] **SYS-21** — Design a Home screen that relies on 3 independent services with partial failure.
- [ ] **SYS-22** — A feature flag accidentally enables a broken security-sensitive path. How do you contain the impact?
- [ ] **SYS-23** — How would you migrate a large legacy XML app incrementally to Compose?
- [ ] **SYS-24** — How would you design for poor connectivity and intermittent power loss?

---

## 15. Gradle Modularization & Dependency Boundaries  — `MOD` · P1

**Phase 4** · **21 questions**

### A. Fundamentals

- [ ] **MOD-01** — What is modularization, and what trade-offs does it introduce?
- [ ] **MOD-02** — Compare app, feature, core, data, domain, and design-system modules.
- [ ] **MOD-03** — What is a dependency graph? Why must it be acyclic?
- [ ] **MOD-04** — What is high cohesion and low coupling?
- [ ] **MOD-05** — Compare Gradle api and implementation dependencies.
- [ ] **MOD-06** — What are Dynamic Feature Modules / Play Feature Delivery?

### B. Practical / Implementation

- [ ] **MOD-07** — Design a multi-module structure for a large app.
- [ ] **MOD-08** — What belongs in :core:network, :core:database, :core:ui, and feature modules?
- [ ] **MOD-09** — How should feature modules communicate without direct coupling?
- [ ] **MOD-10** — How do navigation contracts work across modules?
- [ ] **MOD-11** — How do you manage dependency injection across modules?
- [ ] **MOD-12** — How do version catalogs and convention plugins reduce config duplication?
- [ ] **MOD-13** — When should a module depend on an interface versus a concrete type?
- [ ] **MOD-14** — How do you avoid circular dependencies and giant core/common modules?
- [ ] **MOD-15** — How do api/implementation influence compilation boundaries and rebuilds?
- [ ] **MOD-16** — How do you test and publish a reusable Android library/SDK module?

### C. Senior Scenarios / Trade-offs

- [ ] **MOD-17** — When is a new feature module justified, and when is it unnecessary complexity?
- [ ] **MOD-18** — A shared model change forces recompilation of many modules. How would you shrink the impact?
- [ ] **MOD-19** — Two feature teams need the same business logic. Where should it live?
- [ ] **MOD-20** — How do you migrate a monolith to modules without blocking feature delivery?
- [ ] **MOD-21** — When are dynamic feature modules inappropriate because of offline/runtime constraints?

---

## 16. Gradle, AGP, R8, Signing & Release Engineering  — `BLD` · P1

**Phase 4** · **21 questions**

### A. Fundamentals

- [ ] **BLD-01** — Explain Gradle, Android Gradle Plugin (AGP), and Kotlin compiler roles.
- [ ] **BLD-02** — What are build types, product flavors, variants, and source sets?
- [ ] **BLD-03** — Compare APK and Android App Bundle (AAB).
- [ ] **BLD-04** — What is the difference between debug and release signing?
- [ ] **BLD-05** — What are build cache, configuration cache, and incremental compilation?
- [ ] **BLD-06** — What are R8, shrinking, optimization, and obfuscation?
- [ ] **BLD-07** — What is consumerProguardFiles for Android libraries?

### B. Practical / Implementation

- [ ] **BLD-08** — How do you debug crashes that occur only in release builds?
- [ ] **BLD-09** — How do you decide R8 keep rules for reflection, serialization, JNI, and SDKs?
- [ ] **BLD-10** — How do you use retrace with mapping files?
- [ ] **BLD-11** — How do you analyze APK/AAB size and bundled native ABIs?
- [ ] **BLD-12** — How do you configure signing keys and Play App Signing safely?
- [ ] **BLD-13** — How do you manage versionCode/versionName and release notes?
- [ ] **BLD-14** — How do you diagnose missing native libraries or ABI incompatibility?
- [ ] **BLD-15** — How do you investigate dependency version conflicts and build-speed regressions?
- [ ] **BLD-16** — How do you set up reproducible builds and dependency verification?

### C. Senior Scenarios / Trade-offs

- [ ] **BLD-17** — An app installs in debug but crashes on launch in release due to renamed classes. How do you prove the cause?
- [ ] **BLD-18** — A release manifest merge drops a required ContentProvider authority. What CI check would catch it?
- [ ] **BLD-19** — A release bundle was signed with the wrong key. How do you contain it and correct the pipeline?
- [ ] **BLD-20** — A feature works on arm64 but fails on another ABI. How do you debug packaging?
- [ ] **BLD-21** — How would you safely roll out and then roll back a bad Android release?

---

## 17. Testing, Quality & Reliability  — `TST` · P1

**Phase 4** · **24 questions**

### A. Fundamentals

- [ ] **TST-01** — Compare unit, integration, instrumentation, UI, and end-to-end tests.
- [ ] **TST-02** — Compare fake, mock, stub, spy, and test double.
- [ ] **TST-03** — What are JUnit, MockK/Mockito, Espresso, and Compose UI Testing?
- [ ] **TST-04** — What makes a class testable?
- [ ] **TST-05** — What is runTest? How are virtual time and TestScope used?
- [ ] **TST-06** — Compare StandardTestDispatcher and UnconfinedTestDispatcher.
- [ ] **TST-07** — What is the test pyramid, and where do contract tests fit?

### B. Practical / Implementation

- [ ] **TST-08** — How do you unit-test ViewModels, UseCases, and Repositories?
- [ ] **TST-09** — How do you test Flow, StateFlow, and SharedFlow with Turbine?
- [ ] **TST-10** — How do you test cancellation, error, retry, timeout, and backoff?
- [ ] **TST-11** — How do you test Room DAOs, database migrations, and transactions?
- [ ] **TST-12** — How do you test HTTP failures with MockWebServer or equivalent?
- [ ] **TST-13** — How do you test DI substitutions and scoped dependencies?
- [ ] **TST-14** — How do you test Compose UI semantics, navigation, and accessibility?
- [ ] **TST-15** — How do you reduce flaky UI tests and control scheduling?
- [ ] **TST-16** — What should be unit-tested versus verified with an emulator/device?
- [ ] **TST-17** — What are screenshot tests, Baseline Profiles, and Macrobenchmark tests?
- [ ] **TST-18** — How do you test process death, rotation, and offline transitions?

### C. Senior Scenarios / Trade-offs

- [ ] **TST-19** — Write tests for three parallel APIs with partial success and cancellation.
- [ ] **TST-20** — Write tests for a payment retry path guaranteeing no duplicate charge.
- [ ] **TST-21** — A flaky test passes locally but fails on CI. Explain triage and mitigation.
- [ ] **TST-22** — A database migration fails only with old customer data. How do you generate realistic fixtures?
- [ ] **TST-23** — How would you create a risk-based test plan for a security-sensitive release?
- [ ] **TST-24** — How do you gate PRs without creating an unreasonably slow pipeline?

---

## 18. CI/CD, Git & Team Delivery  — `CIC` · P2

**Phase 4** · **20 questions**

### A. Fundamentals

- [ ] **CIC-01** — What are CI, Continuous Delivery, and Continuous Deployment?
- [ ] **CIC-02** — What are typical stages in an Android CI pipeline?
- [ ] **CIC-03** — What are build artifacts and release tracks?
- [ ] **CIC-04** — Compare Git merge, rebase, squash, revert, and reset.
- [ ] **CIC-05** — Compare git reset --soft versus --hard.
- [ ] **CIC-06** — When is revert safer than reset on shared branches?
- [ ] **CIC-07** — What are git stash, cherry-pick, and fork?

### B. Practical / Implementation

- [ ] **CIC-08** — How do you configure PR checks for lint, static analysis, and tests?
- [ ] **CIC-09** — How do you protect signing material and CI secrets?
- [ ] **CIC-10** — How do you publish builds to internal testing and Play Console?
- [ ] **CIC-11** — How do you automate versioning, changelog, and tagging?
- [ ] **CIC-12** — How do you reduce Gradle cold-build and CI execution times?
- [ ] **CIC-13** — How do you deal with flaky tests, retries, and quarantine policies?
- [ ] **CIC-14** — How do you use staged rollout, crash-rate gates, and rollback plans?
- [ ] **CIC-15** — What Git conflicts can a revert of an older commit cause?
- [ ] **CIC-16** — How do you handle multiple environments and flavors?

### C. Senior Scenarios / Trade-offs

- [ ] **CIC-17** — A production hotfix is needed while feature branches have diverged. Explain your Git strategy.
- [ ] **CIC-18** — A malicious pull request tries to access signing secrets. How do you prevent leakage?
- [ ] **CIC-19** — The app release pipeline deploys the wrong flavor. How do you prevent recurrence?
- [ ] **CIC-20** — The CI pipeline takes 40 minutes. How would you profile and prioritize optimizations?

---

## 19. Data Structures, Algorithms & Big O  — `DSA` · P2

**Phase 5** · **16 questions**

### A. Fundamentals

- [ ] **DSA-01** — What is time complexity versus space complexity?
- [ ] **DSA-02** — Explain O(1), O(log n), O(n), O(n log n), and O(n²).
- [ ] **DSA-03** — Why are constants and lower-order terms omitted in asymptotic analysis?
- [ ] **DSA-04** — Does Big O necessarily describe the worst case? Explain upper bounds versus cases.
- [ ] **DSA-05** — Compare arrays, linked lists, stacks, queues, hash maps, and sets.
- [ ] **DSA-06** — What are average and worst-case HashMap lookup complexities?
- [ ] **DSA-07** — What is binary search, and what precondition does it require?

### B. Practical / Implementation

- [ ] **DSA-08** — How would you detect duplicates efficiently in a large list?
- [ ] **DSA-09** — How do you calculate complexity for nested loops with dependent bounds?
- [ ] **DSA-10** — How do you design and analyze an LRU cache?
- [ ] **DSA-11** — Explain BFS versus DFS and their typical applications.
- [ ] **DSA-12** — How do you identify an accidental O(n²) transformation in a RecyclerView/Compose list?
- [ ] **DSA-13** — How can Kotlin collection chaining create temporary allocations?

### C. Senior Scenarios / Trade-offs

- [ ] **DSA-14** — A product list freezes on low-end devices. How do you distinguish rendering bottlenecks from algorithmic complexity?
- [ ] **DSA-15** — Build a rate limiter or deduplication map for requests. What data structure fits?
- [ ] **DSA-16** — How do you optimize an algorithm while keeping code maintainable and correct?

---

## 20. Senior Ownership, Communication & Technical Leadership  — `LEAD` · P2

**Phase 5** · **15 questions**

### A. Fundamentals

- [ ] **LEAD-01** — How do you explain architectural trade-offs clearly in an interview?
- [ ] **LEAD-02** — How do you review code for correctness, security, readability, and testability?
- [ ] **LEAD-03** — What is technical debt, and how do you prioritize it?
- [ ] **LEAD-04** — How do you estimate an unfamiliar feature and communicate risk?
- [ ] **LEAD-05** — How do you mentor junior developers and improve team engineering practice?

### B. Practical / Implementation

- [ ] **LEAD-06** — How do you write an RFC/ADR for a major architecture change?
- [ ] **LEAD-07** — How do you align mobile, backend, QA, and security teams on an API contract?
- [ ] **LEAD-08** — What metrics tell you whether a refactor was successful?
- [ ] **LEAD-09** — How do you run an incident postmortem without blame?
- [ ] **LEAD-10** — How do you decide build versus buy for third-party libraries/SDKs?

### C. Senior Scenarios / Trade-offs

- [ ] **LEAD-11** — A team disagrees about MVVM vs MVI. How do you lead a decision based on constraints?
- [ ] **LEAD-12** — Tell me about a production incident you owned and how you prevented recurrence.
- [ ] **LEAD-13** — You discover a critical vulnerability days before launch. What is your release decision process?
- [ ] **LEAD-14** — You inherit a legacy app with low test coverage and frequent bugs. What is your first 90-day plan?
- [ ] **LEAD-15** — How would you push back on a requirement that conflicts with mobile OS/security constraints?

---

## 21. Bonus: Payment/POS & Security Scenarios  — `PAY` · P2 / Domain bonus

**Phase 5** · **15 questions**

### A. Fundamentals

- [ ] **PAY-01** — What is a payment state machine (initiated, processing, approved, declined, unknown, reversed)?
- [ ] **PAY-02** — What is idempotency, and why does it matter for financial transactions?
- [ ] **PAY-03** — What are authorization, reversal, void, refund, and reconciliation?
- [ ] **PAY-04** — What risks arise when a local payment record is not durably committed?
- [ ] **PAY-05** — What is a transaction correlation ID, and why is it needed?

### B. Practical / Implementation

- [ ] **PAY-06** — How do you ensure atomic persistence of transaction status and reversal intent?
- [ ] **PAY-07** — How do you design a reversal queue that survives a battery removal?
- [ ] **PAY-08** — How do you avoid duplicate payment requests after UI timeout?
- [ ] **PAY-09** — How do you isolate a hardware/EMV SDK behind a clean interface?
- [ ] **PAY-10** — How do you make a payment workflow observable without logging PAN/PIN or secrets?
- [ ] **PAY-11** — How would you test SDK callback timeout and device disconnection?

### C. Senior Scenarios / Trade-offs

- [ ] **PAY-12** — A POS transaction is approved by issuer but the terminal loses power before saving it. Describe recovery and reconciliation.
- [ ] **PAY-13** — A timeout handler exits the UI before enqueueing a reversal. How do you redesign ownership and ordering?
- [ ] **PAY-14** — A release-only native dependency fails on some hardware ABIs. What is your investigation and safe rollout plan?
- [ ] **PAY-15** — The server is unreachable when a reversal is due. How do you guarantee eventual delivery without duplicates?

---

## 3 أنواع إجابات لازم تتمرن عليها

1. **Explain** — Definition → Why → Android Example → Pitfall.
2. **Compare** — Behavior → Guarantees → When to choose → Trade-off.
3. **Design/Debug** — Clarify requirements → Failure modes → Proposed design → Tests → Monitoring.

## اختيار عملي: 4 أسابيع (يمكن تعديل المدة)

| الأسبوع | المحتوى | المخرجات |
|---|---|---|
| 1 | KOT, AND, MEM, COR, FLO | 3 Coding Exercises + 2 Debugging Scenarios |
| 2 | ARC, SOL, PAT, DI, COM | رسم معماري + Compose screen + Mock Interview |
| 3 | DAT, BG, SEC, TST | Offline-first feature + secure storage design + tests |
| 4 | SYS, MOD, BLD, CIC, DSA, LEAD + PAY (اختياري) | System design + release checklist + 2 Mock Interviews |

## أهم ملاحظات الدقة في الإجابات

- `EncryptedSharedPreferences` مذكور في الأسئلة القديمة كاختيار افتراضي، لكنه **deprecated** في مرجع AndroidX الرسمي؛ اتكلم عن Keystore-backed encryption وتصميم التخزين والتحذيرات الخاصة بالنسخ الاحتياطي وتدوير المفاتيح، مش عن API واحدة كأنها التوصية النهائية.
- `supervisorScope` يعزل فشل **الأبناء المباشرين**؛ هذا لا يعني أن كل الأخطاء تم التعامل معها تلقائيًا. لا تبلع `CancellationException` عند استخدام `runCatching` بلا تمييز.
- `StateFlow` عنده قيمة حالية ويطبّق equality-based conflation؛ وتدفّق `Flow` الأساسي عادةً cold، بينما `StateFlow` و`SharedFlow` hot.
- `Big O` هو حد asymptotic (مثل upper bound)، وليس مرادفًا مطلقًا لـ worst-case.
- overriding empty setupToolbar لا يثبت LSP violation وحده من دون معرفة العقد السلوكي للـbase type.
- لا تعد بأن الـKeystore أو obfuscation أو JNI يجعلون أسرارًا يملكها التطبيق محصنة على جهاز مخترق.

## مراجع تحقق تقنية (ليست أسئلة من موادك الأصلية)

- Android architecture recommendations: https://developer.android.com/topic/architecture/recommendations
- Android lifecycle / architecture: https://developer.android.com/topic/architecture
- StateFlow and SharedFlow: https://developer.android.com/kotlin/flow/stateflow-and-sharedflow
- Modularization: https://developer.android.com/topic/modularization
- AndroidX Security Crypto package reference: https://developer.android.com/reference/androidx/security/crypto/package-summary

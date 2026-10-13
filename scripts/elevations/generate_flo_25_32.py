#!/usr/bin/env python3
"""Generator for FLO-25 through FLO-32 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "flo.json"

FLO_25_32 = [
    {
        "id": "FLO-25",
        "arabic_explanation": (
            "تصميم شريط بحث (Search Box) احترافي يجمع بين الـ Debounce وإلغاء الطلبات القديمة (Cancelling stale API calls) هو أحد أهم الأسئلة المعمارية العملية:\n\n"
            "1. المتطلبات الهندسية لشريط البحث المثالي:\n"
            "   - **تأخير الإرسال (Debounce):** لا نرسل طلب شبكة مع كل حرف يكتبه المستخدم؛ ننتظر 300ms حتى يتوقف عن الكتابة.\n"
            "   - **منع التكرار (Deduplication):** لو مسح المستخدم حرفاً وأعاده فوراً في أقل من 300ms، لا نكرر نفس البحث.\n"
            "   - **إلغاء الطلبات البطيئة السابقة (Stale Request Cancellation):** لو تم إرسال طلب للبحث عن 'App' واستغرق وقتاً طويلاً، ثم كتب المستخدم 'Apple'، يجب **إلغاء طلب 'App' فوراً** حتى لا تعود نتيجته متأخرة وتمسح شاشة نتائج 'Apple' (Race condition)!\n"
            "   - **معالجة النصوص الفارغة (Empty Query):** مسح النتائج فوراً دون إرسال طلب للسيرفر.\n\n"
            "2. التركيبة المعمارية الثلاثية:\n"
            "   - `debounce(300L)`\n"
            "   - `distinctUntilChanged()`\n"
            "   - `flatMapLatest { query -> ... }`"
        ),
        "practical_walkthrough": (
            "تنفيذ كامل للـ Search Pipeline في ViewModel:\n"
            "```kotlin\n"
            "class SearchViewModel(\n"
            "    private val searchRepository: SearchRepository\n"
            ") : ViewModel() {\n"
            "\n"
            "    val queryFlow = MutableStateFlow(\"\")\n"
            "\n"
            "    val searchState: StateFlow<SearchUiState> = queryFlow\n"
            "        .map { it.trim() } // 1. تنظيف الفراغات\n"
            "        .debounce(300L)   // 2. تأخير 300ms للانتظار بعد انتهاء الكتابة\n"
            "        .distinctUntilChanged() // 3. تجاهل الكلمات المكررة المتتالية\n"
            "        .flatMapLatest { query -> // 4. يلغي الطلب القديم المعلق فوراً بمجرد وصول كلمة جديدة\n"
            "            if (query.isBlank()) {\n"
            "                flowOf(SearchUiState.Idle)\n"
            "            } else {\n"
            "                searchRepository.searchProducts(query)\n"
            "                    .map { SearchUiState.Success(it) }\n"
            "                    .onStart { emit(SearchUiState.Loading) }\n"
            "                    .catch { emit(SearchUiState.Error(it.message ?: \"Error\")) }\n"
            "            }\n"
            "        }\n"
            "        .stateIn(\n"
            "            scope = viewModelScope,\n"
            "            started = SharingStarted.WhileSubscribed(5_000L),\n"
            "            initialValue = SearchUiState.Idle\n"
            "        )\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design the search pipeline using query.map { it.trim() }.debounce(300).distinctUntilChanged().flatMapLatest { query -> repository.search(query) }. flatMapLatest guarantees that any in-flight, stale network call is immediately cancelled the moment a new query arrives.",
        "best_answer": (
            "To build a responsive search pipeline that debounces input and cancels stale API calls, I chain four essential Flow operators in the ViewModel:\n\n"
            "1. **`map { it.trim() }`**: Sanitizes whitespace to avoid trivial variations.\n"
            "2. **`debounce(300L)`**: Waits for a 300ms quiet period after the user stops typing, preventing rapid keystroke storms.\n"
            "3. **`distinctUntilChanged()`**: Prevents redundant search dispatches if the query string after trimming equals the previous search.\n"
            "4. **`flatMapLatest { query -> ... }`**: This is the critical cancellation operator. If a query 'A' is sent and takes 800ms, and the user types 'AB' at 500ms, `flatMapLatest` immediately cancels the ongoing HTTP call for 'A' via cooperative cancellation, executing the fresh search for 'AB' instead. This completely eliminates out-of-order response race conditions."
        ),
        "deep_answer": (
            "From an API optimization and networking standpoint, `flatMapLatest` cancels the OkHttp Call at the network layer if OkHttp's asynchronous enqueue or Coroutine bridge is used, terminating the underlying socket read loop and saving device radio battery.\n\n"
            "Inside `flatMapLatest`, we wrap the repository call with: "
            "`.onStart { emit(SearchUiState.Loading) }` and `.catch { emit(SearchUiState.Error(...)) }`. "
            "This encapsulates the entire asynchronous lifecycle of each individual query cleanly within the inner flow.\n\n"
            "Finally, pairing this with `stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), SearchUiState.Idle)` ensures that if the user rotates the device, the current search results are retained instantly from the `StateFlow`'s cache without re-triggering the network query."
        ),
        "follow_ups": [
            {
                "interviewer": "What happens if the network API returns responses out of order without `flatMapLatest`?",
                "answer": "If query 'A' is slow (takes 2s) and query 'AB' is fast (takes 200ms), without `flatMapLatest`, 'AB' will render first, and 1.8 seconds later 'A' will arrive and overwrite the screen with stale results! `flatMapLatest` completely prevents this."
            },
            {
                "interviewer": "How do you handle immediate searches when the user taps the search keyboard button?",
                "answer": "Expose an `onSearchSubmitted(query)` method in the ViewModel that directly updates an active query without going through the debounce delay."
            },
            {
                "interviewer": "Can you test this search pipeline deterministically in a unit test?",
                "answer": "Yes, using `runTest` and Turbine. Emit 'A', call `advanceTimeBy(100)`, emit 'AB', call `advanceTimeBy(300)`, and verify that only the search for 'AB' was dispatched."
            }
        ]
    },
    {
        "id": "FLO-26",
        "arabic_explanation": (
            "عرض أحدث حالة للواجهة بعد تدوير الشاشة (Displaying the most recent state after rotation) هو الوظيفة الأساسية التي صُمم من أجلها `StateFlow`:\n\n"
            "1. ما هو نوع الـ Stream المطلوب ولماذا؟\n"
            "   - **النوع المطلوب هو: `StateFlow<UiState>`**.\n"
            "   - **السبب 1 (State Retention):** الـ StateFlow يحتفظ دائماً بآخر قيمة تم إصدارها في الذاكرة (`.value`). عندما يتم تدوير الشاشة وتدمير الـ Activity القديمة وإنشاء Activity جديدة، تشترك الـ Activity الجديدة في الـ StateFlow فتستلم القيمة الأخيرة فوراً في نفس الفريم (Instantaneous restore).\n"
            "   - **السبب 2 (No Re-execution):** لأنه Hot Stream، لا يعيد تشغيل استعلام قاعدة البيانات أو طلب الشبكة من الصفر (على عكس Cold Flow الذي سيبدأ من البداية عند كل تدوير).\n"
            "   - **السبب 3 (Conflation):** لو الحالة لم تتغير، لن يسبب Recomposition غير ضروري.\n\n"
            "2. لماذا لا نستخدم SharedFlow أو Cold Flow؟\n"
            "   - Cold Flow سيعيد إرسال طلب الشبكة عند كل تدوير للشاشة!\n"
            "   - SharedFlow بـ `replay = 0` لن يرسل أي شيء للشاشة الجديدة بعد التدوير، وستظل الشاشة فارغة أو بيضاء!"
        ),
        "practical_walkthrough": (
            "النمط المتبع في الـ Production:\n"
            "```kotlin\n"
            "class DashboardViewModel(private val repository: DashboardRepository) : ViewModel() {\n"
            "    \n"
            "    // نحول تدفق البيانات إلى StateFlow يحتفظ بالحالة عبر التدوير:\n"
            "    val uiState: StateFlow<DashboardUiState> = repository.observeDashboardData()\n"
            "        .map { DashboardUiState.Success(it) }\n"
            "        .stateIn(\n"
            "            scope = viewModelScope,\n"
            "            started = SharingStarted.WhileSubscribed(5_000L), // 5 ثوانٍ تكفي التدوير وزيادة\n"
            "            initialValue = DashboardUiState.Loading\n"
            "        )\n"
            "}\n"
            "```\n"
            "عندما يدور المستخدم الهاتف من عمودي لأفقي: يتم إغلاق الـ Activity القديمة، وإنشاء الجديدة، وتشترك في `uiState`، فتستلم `DashboardUiState.Success` المحفوظ في الكاش في صفر ثانية بدون أي شاشة تحميل أو وميض."
        ),
        "quick_answer": "Use StateFlow. Because StateFlow is a hot stream that retains its latest value (.value) in memory and replays it immediately to new subscribers, the newly recreated Activity/Composable after rotation receives the exact current UI state instantly without re-fetching from the network or database.",
        "best_answer": (
            "To display the most recent UI state immediately after screen rotation, the required stream primitive is **`StateFlow`**.\n\n"
            "When an Android device rotates, the Activity is destroyed and recreated. Because the ViewModel survives configuration changes, any state retained in the ViewModel is preserved in memory.\n\n"
            "StateFlow is tailor-made for this scenario:\n\n"
            "1. It is a **hot stream** that holds the most recent state in its `.value` property.\n"
            "2. When the newly created Activity or Composable subscribes, StateFlow immediately replays that latest cached state, allowing the UI to render the complete screen instantly on its very first frame.\n\n"
            "If you used a plain cold Flow, the new Activity would trigger a fresh execution of the flow, repeating database reads or network calls. If you used a SharedFlow with `replay = 0`, the new Activity would receive nothing and render an empty blank screen."
        ),
        "deep_answer": (
            "Architecturally, pairing `StateFlow` with `SharingStarted.WhileSubscribed(5000)` in `stateIn()` is what makes this robust: "
            "During rotation, the old Activity's `repeatOnLifecycle` or `collectAsStateWithLifecycle` unbinds, dropping `subscriptionCount` to 0. "
            "The 5-second buffer prevents the ViewModel from cancelling the upstream repository flow. "
            "When the new Activity binds within a few hundred milliseconds, `subscriptionCount` jumps back to 1. StateFlow delivers the cached state immediately without missing a beat.\n\n"
            "In Jetpack Compose, the UI consumes it via:\n\n"
            "```kotlin\n"
            "val uiState by viewModel.uiState.collectAsStateWithLifecycle()\n"
            "```\n\n"
            "Compose reads the cached value on initial composition, preventing any flash of an empty state or loading spinner."
        ),
        "follow_ups": [
            {
                "interviewer": "What if the process is killed by the OS due to low memory instead of a rotation?",
                "answer": "StateFlow in memory is lost on process death. For states that must survive process death (like draft forms or navigation arguments), persist critical fields into `SavedStateHandle` using `savedStateHandle.getStateFlow(key, initialValue)`."
            },
            {
                "interviewer": "Can you use `SharedFlow(replay = 1)` instead of `StateFlow`?",
                "answer": "Conceptually yes, but `StateFlow` is superior for UI state because it enforces non-nullable initial state, provides synchronous `.value` access, and includes built-in equality suppression via `equals()`."
            },
            {
                "interviewer": "Why is `LiveData` also capable of surviving rotation?",
                "answer": "Because `LiveData` also caches its latest value (`mValue`) in memory and dispatches it to active observers upon lifecycle start. However, StateFlow is preferred because it is pure Kotlin Multiplatform and integrates with coroutines seamlessly."
            }
        ]
    },
    {
        "id": "FLO-27",
        "arabic_explanation": (
            "تكرار حدث الانتقال مرتين بعد تدوير الشاشة (Navigation Event firing twice after rotation) هو أحد أشهر الـ Bugs الكلاسيكية في تطبيقات أندرويد:\n\n"
            "1. كيف تحقق في هذا العطل وتكتشف سببه؟\n"
            "   - **السبب رقم 1 (تخزين الحدث في StateFlow أو LiveData):** لو الـ ViewModel قام بتخزين أمر الانتقال في `StateFlow` (مثل `_uiState.value = NavigateToDetails`)، فالـ StateFlow بطبيعته يحتفظ بالقيمة الأخيرة في الذاكرة. عند تدوير الشاشة، الشاشة الجديدة تشترك في الـ StateFlow فتستلم نفس أمر الانتقال مجدداً وتنتقل مرتين!\n"
            "   - **السبب رقم 2 (استخدام SharedFlow بـ replay >= 1):** لو تم ضبط `replay = 1`، المشترك الجديد بعد التدوير يستلم الحدث القديم من الـ Cache مجدداً.\n\n"
            "2. الحلول المعمارية الصحيحة (The Architectural Fixes):\n"
            "   - **الحل 1 (استخدام Channel للأحداث الفردية):** استخدام `Channel<NavigationEvent>(Channel.BUFFERED).receiveAsFlow()`. الـ Channel طابور يضمن تسليم العنصر لمرة واحدة فقط واستهلاكه فوراً، فلا يعاد بعد التدوير.\n"
            "   - **الحل 2 (نمط استهلاك الحدث الصريح - Event Handled Pattern):** إذا كان الحدث داخل State، يتم إعطاؤه معرف فريد أو كائن `Event<T>`، وتطلب من الـ UI إرسال Intent للـ ViewModel فور استهلاكه (`viewModel.onNavigationHandled()`) ليقوم الـ ViewModel بتصفير الحالة إلى `null`."
        ),
        "practical_walkthrough": (
            "إصلاح العطل في الـ ViewModel باستخدام Channel:\n"
            "```kotlin\n"
            "// ❌ الكود المسبب لتكرار الانتقال مرتين:\n"
            "val navEvent = MutableStateFlow<NavRoute?>(null)\n"
            "fun onCardClicked() { navEvent.value = NavRoute.Details } // عند التدوير سيعاد تنفيذه!\n"
            "\n"
            "// ✅ الكود المصحح باستخدام Channel:\n"
            "class MyViewModel : ViewModel() {\n"
            "    private val _navEvents = Channel<NavRoute>(Channel.BUFFERED)\n"
            "    val navEvents = _navEvents.receiveAsFlow()\n"
            "\n"
            "    fun onCardClicked() {\n"
            "        viewModelScope.launch {\n"
            "            _navEvents.send(NavRoute.Details)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```\n"
            "في Compose:\n"
            "```kotlin\n"
            "LaunchedEffect(Unit) {\n"
            "    viewModel.navEvents.collect { route ->\n"
            "        navController.navigate(route) // يتم استهلاكه وحذفه من الـ Channel؛ لن يتكرر أبداً!\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "This bug occurs when navigation events are improperly modeled as persistent state in StateFlow or SharedFlow with replay >= 1, causing the recreated UI to re-read and re-execute the cached event. Fix it by modeling one-off events using a buffered Channel.receiveAsFlow() or consuming and clearing the event from state immediately upon execution.",
        "best_answer": (
            "When a navigation event fires twice after screen rotation, it is almost always caused by modeling a transient event as durable state.\n\n"
            "The root cause is storing navigation commands in a `StateFlow` or a `SharedFlow` configured with `replay >= 1`. When the device rotates, the Activity is destroyed and recreated. When the new Activity subscribes to the stream, the flow dutifully replays the cached navigation command from memory, triggering a duplicate navigation transaction.\n\n"
            "To fix this, we change the event modeling to guarantee **single-time consumption**:\n\n"
            "1. **Channel-based Events:** Use a private `Channel<NavTarget>(Channel.BUFFERED)` and expose `channel.receiveAsFlow()`. Channels are FIFO queues: once an event is consumed by the UI, it is dequeued. A recreated Activity on rotation will find the channel empty.\n\n"
            "2. **State-driven Acknowledgment:** If kept in UI state (`data class UiState(val navRoute: NavRoute? = null)`), the UI must immediately notify the ViewModel upon navigation (`viewModel.onNavigated()`), which resets `navRoute = null` before any rotation can occur."
        ),
        "deep_answer": (
            "In code review investigations, I verify the event lifecycle across three audit checkpoints:\n\n"
            "1. **Stream Type Inspection:** Check if the event flow is declared as `MutableStateFlow` or `MutableSharedFlow(replay = 1)`. If yes, replace it with `Channel(Channel.BUFFERED).receiveAsFlow()`.\n\n"
            "2. **Collection Lifecycle Inspection:** In View-based code, verify that navigation events are collected inside `viewLifecycleOwner.lifecycleScope.launch { viewLifecycleOwner.repeatOnLifecycle(STARTED) { ... } }`. In Compose, verify it uses `LaunchedEffect(Unit)`.\n\n"
            "3. **Queue Deduplication:** If using Channel, ensure the channel is buffered (`Channel.BUFFERED`) so events sent while the screen is in transit between lifecycles are retained until the new screen is ready, but consumed strictly once."
        ),
        "follow_ups": [
            {
                "interviewer": "Why did `SingleLiveEvent` fall out of favor?",
                "answer": "Because `SingleLiveEvent` only supported a single observer. If multiple observers registered, only one received the event. Furthermore, it relied on an internal boolean atomic flag that violated reactive stream contracts."
            },
            {
                "interviewer": "What happens if a navigation event is sent while the app is in the background?",
                "answer": "With `Channel(Channel.BUFFERED)`, the event waits safely in the buffer. When the app returns to the foreground and collection resumes, the event is consumed and navigation proceeds safely."
            },
            {
                "interviewer": "Can you handle navigation directly from the ViewModel instead?",
                "answer": "In clean architecture, the ViewModel should not hold a reference to `NavController` or Android Views. It should only emit abstract routes (e.g., `NavRoute.Profile`), leaving the actual navigation mechanics to the UI layer."
            }
        ]
    },
    {
        "id": "FLO-28",
        "arabic_explanation": (
            "دمج بيانات Room المحلية المخبأة مع التحديث من السيرفر البعيد وسؤال 'من هو المصدر الوحيد للحقيقة (Single Source of Truth)' هو جوهر الـ **Offline-First Architecture**:\n\n"
            "1. من هو المصدر الوحيد للحقيقة (Single Source of Truth - SSOT)؟\n"
            "   - **قاعدة البيانات المحلية (Room Database) هي المصدر الوحيد للحقيقة دائماً! (Local DB is the SSOT).**\n"
            "   - واجهة المستخدم (UI) **لا تستمع إلى الـ Network إطلاقاً**؛ الـ UI يستمع حصرياً إلى الـ Flow القادم من قاعدة بيانات Room!\n\n"
            "2. كيف تتدفق البيانات بنظافة (The Reactive Data Flow)؟\n"
            "   - 1. الـ UI يطلب البيانات من الـ Repository ويستمع لـ `roomDao.observeItems()`.\n"
            "   - 2. الـ UI يعرض فوراً البيانات المخزنة محلياً في Room بدون أي تأخير (Instant Offline Loading).\n"
            "   - 3. في نفس الوقت، الـ Repository يطلق طلباً في الخلفية لجلب أحدث البيانات من السيرفر (`api.fetchItems()`).\n"
            "   - 4. عندما ينجح طلب السيرفر، الـ Repository يقوم بحفظ وتحديث البيانات في **Room Database** (`roomDao.insertAll(newItems)`).\n"
            "   - 5. بمجرد تحديث Room، تقوم الـ Database تلقائياً بإصدار (emit) القائمة الجديدة للـ UI عبر الـ Flow!\n\n"
            "3. الفوائد الهائلة:\n"
            "   - دعم كامل للـ Offline Mode بنسبة 100%.\n"
            "   - تجنب أي تعارض في البيانات أو تذبذب في واجهة المستخدم."
        ),
        "practical_walkthrough": (
            "تنفيذ النمط في الـ Repository:\n"
            "```kotlin\n"
            "class ArticleRepository(\n"
            "    private val articleDao: ArticleDao,\n"
            "    private val articleApi: ArticleApi,\n"
            "    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO\n"
            ") {\n"
            "    // 1. الواجهة تستمع حصرياً لـ Room DB:\n"
            "    fun observeArticles(): Flow<List<Article>> =\n"
            "        articleDao.getArticles().map { entities -> entities.map { it.toDomain() } }\n"
            "\n"
            "    // 2. دالة التحديث تحدث Room ولا ترجع بيانات مباشرة للـ UI:\n"
            "    suspend fun refreshArticles() = withContext(ioDispatcher) {\n"
            "        try {\n"
            "            val remoteArticles = articleApi.fetchArticles()\n"
            "            articleDao.insertAll(remoteArticles.map { it.toEntity() }) // Room تحدث الـ Flow تلقائياً!\n"
            "        } catch (e: Exception) {\n"
            "            // لو الشبكة مقطوعة، لا نفشل؛ البيانات المحلية تظل معروضة بسلاسة\n"
            "            if (e is CancellationException) throw e\n"
            "            Log.e(\"Repo\", \"Failed to refresh remote articles\", e)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "The local database (Room) is the Single Source of Truth (SSOT). The UI exclusively observes the Flow emitted by Room. Remote network calls write fresh data into Room, and Room automatically emits the updated data to the UI, guaranteeing seamless offline-first operation.",
        "best_answer": (
            "In an offline-first Android architecture, the local database (Room) is strictly the **Single Source of Truth (SSOT)**.\n\n"
            "The architecture follows a unidirectional reactive pipeline:\n\n"
            "1. **UI Observes Room:** The UI layer never observes raw network responses directly; it exclusively collects a Flow emitted by Room DAO (`articleDao.observeArticles()`). This guarantees that cached data is rendered instantly upon launch with zero network latency.\n\n"
            "2. **Network Updates Room:** When a refresh is triggered, the repository makes a network call to the remote API. Upon receiving the payload, the repository persists it directly into the local Room database (`articleDao.upsert(data)`).\n\n"
            "3. **Automatic Reactive UI Emission:** Because Room's SQLite database observer tracks table modifications, inserting new data automatically triggers Room to re-query and emit the fresh list through its cold Flow. The UI receives the update automatically without any manual coordination."
        ),
        "deep_answer": (
            "Under the hood, Room achieves this via SQLite transaction hooks and `InvalidationTracker`. "
            "When you return `Flow<List<T>>` from a DAO method, Room registers a table observer. Whenever any DAO write transaction commits against that table, `InvalidationTracker` dispatches an invalidation event on Room's query executor, prompting the Flow to re-query SQLite and emit the fresh snapshot.\n\n"
            "In enterprise codebases, we guard against stale deletions and conflicts using **Database Synchronization Strategies**: "
            "Instead of naive `insertAll()`, we either use `@Upsert` (introduced in Room 2.5) or execute a clean transaction: `withTransaction { dao.deleteStale(); dao.insertAll(fresh) }`. "
            "This ensures that items deleted on the backend are removed from local storage without breaking the continuous Flow observation."
        ),
        "follow_ups": [
            {
                "interviewer": "How does the UI know if the network refresh failed?",
                "answer": "Expose a separate UI state or status stream for the refresh operation (e.g., `isRefreshing: Boolean` and `refreshError: String?`) in the ViewModel, keeping data state and sync status decoupled."
            },
            {
                "interviewer": "What if the remote response has 50,000 items? Does Room re-emit the whole list?",
                "answer": "For massive datasets, pair Room with the Paging 3 library (`PagingSource`). Paging 3 queries Room incrementally in chunks (e.g., 20 items per page), keeping memory and UI rendering fast."
            },
            {
                "interviewer": "Why shouldn't the network call emit directly to a `combine` operator with Room?",
                "answer": "Emitting directly from both network and Room creates two competing sources of truth, causing UI state jitter, duplicate items, and race conditions where a fast network call is overwritten by a slower disk read."
            }
        ]
    },
    {
        "id": "FLO-29",
        "arabic_explanation": (
            "عندما يقوم الـ Upstream بإصدار بيانات بسرعة هائلة تجعل رسم الشاشة بطيئاً (Rapid Upstream causing slow UI rendering)، نحتاج إلى استراتيجية ملائمة للتعامل مع الـ Backpressure:\n\n"
            "1. تحليل المشكلة:\n"
            "   - الـ Upstream يصدر 100 تحديث في الثانية (مثل: قراءات حساس البوصلة، تحديثات أسهم البورصة، أو موقع GPS السريع).\n"
            "   - الـ UI يستغرق 16ms لرسم كل فريم (60 FPS). محاولة معالجة كل التحديثات ستؤدي لتراكم المهام، إسقاط الفريمات (Jank)، وتجمد التطبيق.\n\n"
            "2. ما هي الاستراتيجية الأنسب؟\n"
            "   - **الاستراتيجية الأولى والأفضل: `conflate()`**\n"
            "     * تسقط وتتجاهل التحديثات الوسيطة في الذاكرة، وتعطي الـ UI أحدث قيمة فقط في اللحظة التي يفرغ فيها لرسم الإطار التالي.\n"
            "     * ممتازة لأسعار الأسهم، عدادات السرعة، ومؤشرات التقدم.\n"
            "   - **الاستراتيجية الثانية: `sample(periodMillis)`**\n"
            "     * تلتقط عينة واحدة فقط كل فترة زمنية ثابتة (مثل: عينة واحدة كل 100ms)، وتتجاهل كل ما يصدر خلال تلك الفترة.\n"
            "   - **الاستراتيجية الثالثة: `collectLatest`**\n"
            "     * تلغي رسم الفريم القديم فوراً وتبدأ برسم الفريم الجديد."
        ),
        "practical_walkthrough": (
            "تطبيق عملي لمراقبة أسعار الأسهم اللحظية (Stock Ticker):\n"
            "```kotlin\n"
            "// الحساس أو السيرفر يرسل آلاف التحديثات في الثانية:\n"
            "stockRepository.observeLiveStockPrices()\n"
            "    .conflate() // يسقط التحديثات القديمة أثناء رسم الشاشة، ويضمن أحدث سعر دائماً\n"
            "    .onEach { latestPrice ->\n"
            "        renderStockPrice(latestPrice) // يعمل بسلاسة عند 60 FPS بدون أي تأخير أو lag\n"
            "    }\n"
            "    .launchIn(viewLifecycleOwner.lifecycleScope)\n"
            "```"
        ),
        "quick_answer": "Use 'conflate()' or 'sample(periodMillis)'. conflate() drops intermediate unrendered values to deliver only the freshest state when the UI thread becomes available; sample(period) emits a single periodic snapshot, capping the rendering frequency to match the display refresh rate.",
        "best_answer": (
            "When an upstream flow emits data faster than the Android UI layer can render it, applying the right backpressure throttling strategy is mandatory to avoid frame drops (jank) and ANRs.\n\n"
            "The two best backpressure strategies are:\n\n"
            "1. **`conflate()`**: If the UI thread is busy rendering a frame or layout pass, `conflate()` silently drops intermediate upstream emissions in memory. The moment the UI becomes idle, it immediately receives the single most recent state. This is ideal for real-time dashboards, stock tickers, or sensor gauges where only the freshest value matters.\n\n"
            "2. **`sample(100L)`**: If emissions are high-frequency bursts (e.g., streaming audio decibel meters), `sample(period)` periodically polls and emits the latest value once every N milliseconds, strictly capping the UI update rate to 10 FPS or 60 FPS.\n\n"
            "Never use unconstrained `buffer()` in this scenario: buffering high-frequency streams will accumulate thousands of items in memory, creating significant GC pressure and causing the UI to permanently lag seconds behind real-time reality."
        ),
        "deep_answer": (
            "At the systems level, Android displays refresh at 60Hz (16.6ms per frame) or 120Hz (8.3ms per frame). "
            "Dispatching UI updates to Compose or Views at rates exceeding the display refresh rate (e.g., 200 emissions/sec) wastes CPU cycles on layout recalculations that will never be drawn to the screen.\n\n"
            "Under the hood, `conflate()` compiles to an internal `ConflatedChannel` of capacity 1 with `BufferOverflow.DROP_OLDEST`. "
            "It decouples the producer thread from the consumer thread via an atomic pointer swap. "
            "This ensures zero memory allocation churn and zero lock contention during high-throughput bursts, allowing the upstream sensor or socket parser to run at maximum native speed while keeping UI rendering pinned at a buttery-smooth 60/120 FPS."
        ),
        "follow_ups": [
            {
                "interviewer": "Why is `collectLatest` sometimes worse than `conflate` for heavy rendering?",
                "answer": "Because `collectLatest` cancels and relaunches coroutines constantly on every emission. If 1,000 emissions arrive, `collectLatest` creates 1,000 coroutines and cancels them, causing coroutine allocation overhead and GC churn. `conflate` lets the current block finish undisturbed."
            },
            {
                "interviewer": "How does `StateFlow` handle rapid emissions automatically?",
                "answer": "StateFlow has built-in conflation: assigning a new value to `stateFlow.value` overwrites the current slot. Slow collectors naturally skip intermediate values and only receive the latest state."
            },
            {
                "interviewer": "When would you use `buffer(capacity)` instead of `conflate()`?",
                "answer": "When every single event must be processed without loss (e.g., recording telemetry logs or processing payment batches), and you simply want to smooth out temporary burst spikes."
            }
        ]
    },
    {
        "id": "FLO-30",
        "arabic_explanation": (
            "ما هي الضمانات الحقيقية التي يقدمها `replay` و `buffering` في `SharedFlow` عند عدم وجود أي مستمع نشط (No active subscribers)؟\n\n"
            "1. سلوك الـ `replay` عند عدم وجود مستمعين:\n"
            "   - الـ `replay` **مضمون 100% ويتم حفظه في الذاكرة (Guaranteed in memory)**.\n"
            "   - إذا كان `replay = 2` وتم إصدار 5 عناصر في غياب أي مستمع، سيحتفظ الـ SharedFlow بآخر عنصرين في ذاكرة التخزين المؤقت.\n"
            "   - عندما يأتي أول مستمع مستقبلاً، سيستلم هذين العنصرين فوراً!\n\n"
            "2. سلوك الـ `extraBufferCapacity` عند عدم وجود مستمعين:\n"
            "   - **تحذير حرج جداً (The Critical Caveat):** الـ `extraBufferCapacity` **لا يعمل إطلاقاً في غياب المستمعين!**\n"
            "   - الـ Buffer الإضافي مخصص فقط لتخفيف الضغط بين Producer سريع ومستمعين بطيئين متصلين حالياً. إذا كان عدد المستمعين **صفراً**، العناصر الزائدة عن `replay` **يتم إسقاطها فوراً وتضيع للأبد**، حتى لو كانت سعة الـ extra buffer = 1000!\n\n"
            "3. النتيجة الإنتاجية:\n"
            "   - لو أردت ضمان وصول أحداث لمستمعين قد يشتركون لاحقاً، يجب زيادة قيمة `replay` أو استخدام `Channel` بدلاً من SharedFlow."
        ),
        "practical_walkthrough": (
            "إثبات عملي لسلوك الذاكرة في SharedFlow:\n"
            "```kotlin\n"
            "val sharedFlow = MutableSharedFlow<Int>(\n"
            "    replay = 1,\n"
            "    extraBufferCapacity = 10 // سعة إضافية 10\n"
            ")\n"
            "\n"
            "// لا يوجد أي مستمع حالياً (subscribers = 0):\n"
            "sharedFlow.tryEmit(100)\n"
            "sharedFlow.tryEmit(200)\n"
            "sharedFlow.tryEmit(300)\n"
            "\n"
            "// الآن يشترك أول مستمع:\n"
            "sharedFlow.test { // باستخدام Turbine\n"
            "    // سيستلم 300 فقط! (عنصر واحد فقط من replay = 1)\n"
            "    assertEquals(300, awaitItem())\n"
            "    // العناصر 100 و 200 ضاعت للأبد ولم يتم حفظها في extraBufferCapacity!\n"
            "}\n"
            "```"
        ),
        "quick_answer": "replay is guaranteed to retain up to N latest items in memory for future subscribers even when subscriber count is 0; however, extraBufferCapacity only buffers for active subscribers. With 0 subscribers, emissions exceeding the replay capacity are dropped immediately and cannot be queued in extra buffer space.",
        "best_answer": (
            "This is one of the most critical and frequently misunderstood memory guarantees in Kotlin Coroutines:\n\n"
            "1. **`replay` guarantees retention:** The replay cache is permanent and memory-resident. If `replay = 2`, `SharedFlow` retains the last 2 emitted items in memory indefinitely, even if there are zero active subscribers. When a new collector subscribes in the future, it is guaranteed to receive those 2 replayed items immediately.\n\n"
            "2. **`extraBufferCapacity` provides ZERO retention with 0 subscribers:** A common misconception is that an extra buffer of 10 will hold 10 items while waiting for subscribers. It does not. The extra buffer capacity exists solely to absorb backpressure for *active, currently connected* slow subscribers. If `subscriptionCount == 0`, emissions beyond the `replay` count are dropped immediately and permanently, regardless of how large `extraBufferCapacity` is configured.\n\n"
            "If your architecture requires guaranteed delivery of queued events to future subscribers, you must use a buffered **Channel** (`Channel(Channel.BUFFERED)`), not a SharedFlow."
        ),
        "deep_answer": (
            "Under the hood, in `SharedFlowImpl`, the internal buffer consists of a `head` and `tail` pointer array representing replay slots and extra buffer slots. "
            "When `emit()` or `tryEmit()` is called, the implementation checks `if (nSubscribers == 0)`. "
            "If true, the code path strictly executes `updateReplayCache(value)` and returns immediately. It completely skips queuing items into the extra buffer indices.\n\n"
            "This behavior is by design: `SharedFlow` models broadcast pub-sub, not a persistent task queue. "
            "If a SharedFlow preserved unconsumed items without subscribers, a ViewModel that emits analytics or telemetry while unobserved would leak memory infinitely until a subscriber attached. "
            "For guaranteed queueing semantics across lifecycles, `Channel.send()` is the appropriate concurrency primitive."
        ),
        "follow_ups": [
            {
                "interviewer": "What happens if you call `emit()` with 0 subscribers and `onBufferOverflow = SUSPEND`?",
                "answer": "With 0 subscribers, `emit()` will NOT suspend. It updates the replay cache and returns immediately, dropping any non-replayed items."
            },
            {
                "interviewer": "Can a `SharedFlow` with `replay = 0` ever deliver an event to a subscriber that connects 1 millisecond after emission?",
                "answer": "No, never. With `replay = 0`, the emission is dropped the instant it occurs if there are no active collectors at that exact moment."
            },
            {
                "interviewer": "How does `StateFlow` behave with 0 subscribers?",
                "answer": "StateFlow is a SharedFlow with `replay = 1`. With 0 subscribers, it updates its `.value` slot. When a subscriber connects later, it receives that updated value immediately."
            }
        ]
    },
    {
        "id": "FLO-31",
        "arabic_explanation": (
            "اختيار استراتيجية `SharingStarted` المناسبة لتحقيق التوازن بين استهلاك البطارية والصحة البرمجية وسلوك الاشتراكات:\n\n"
            "1. شجرة القرار الهندسي (Engineering Decision Tree):\n"
            "   - **هل التدفق يمثل UI State في ViewModel ويعرض على الشاشة؟**\n"
            "     * الإجابة دائماً: **`SharingStarted.WhileSubscribed(5_000L)`**.\n"
            "     * **لماذا؟** يوقف التدفق في الـ Background لتوفير البطارية، ومهلة الـ 5 ثوانٍ تحافظ على استمرار التدفق أثناء تدوير الشاشة بدون إعادة تشغيل.\n\n"
            "   - **هل التدفق يمثل Cache عالمي مشترك (Singleton / App Scope) لا نريد إعادة حسابه؟**\n"
            "     * الإجابة: **`SharingStarted.Lazily`**.\n"
            "     * **لماذا؟** ينتظر حتى تطلبه أول شاشة، وبمجرد تشغيله يظل حياً في الذاكرة لتستفيد منه كل الشاشات اللاحقة بدون تكرار الحساب.\n\n"
            "   - **هل التدفق يمثل عملية حيوية يجب أن تبدأ فوراً حتى لو لم ينظر إليها أحد؟**\n"
            "     * الإجابة: **`SharingStarted.Eagerly`**.\n"
            "     * **لماذا؟** يبدأ فوراً مع إنشاء الكلاس، مثل: جلب وتجهيز إعدادات الأمان والتشفير عند بدء التطبيق."
        ),
        "practical_walkthrough": (
            "تطبيق عملي لتوزيع الاستراتيجيات في تطبيق حقيقي:\n"
            "```kotlin\n"
            "// 1. شاشة UI عادية -> WhileSubscribed(5000):\n"
            "val userProfile: StateFlow<UserProfile> = repository.observeUser()\n"
            "    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000L), UserProfile.Empty)\n"
            "\n"
            "// 2. كاش أسعار العملات في Singleton Repository -> Lazily:\n"
            "@Singleton\n"
            "class CurrencyRepository(api: CurrencyApi, appScope: CoroutineScope) {\n"
            "    val exchangeRates = api.streamRates()\n"
            "        .shareIn(appScope, SharingStarted.Lazily, replay = 1)\n"
            "}\n"
            "\n"
            "// 3. مراقبة حالة اتصال الإنترنت للتطبيق كله -> Eagerly:\n"
            "@Singleton\n"
            "class NetworkMonitor(context: Context, appScope: CoroutineScope) {\n"
            "    val isOnline = observeNetworkConnectivity(context)\n"
            "        .stateIn(appScope, SharingStarted.Eagerly, initialValue = true)\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Choose WhileSubscribed(5000) for ViewModel UI states to conserve battery in the background while surviving configuration changes; choose Lazily for shared application-scoped caches that should initialize on first access and stay cached; choose Eagerly for critical process-wide monitoring that must start immediately upon creation.",
        "best_answer": (
            "Choosing the right `SharingStarted` strategy is an exercise in balancing battery conservation, memory retention, and UI latency across three architectural tiers:\n\n"
            "1. **`WhileSubscribed(5000)` for ViewModel UI State:** This is the default standard for feature screens. It activates upstream collection only when UI collectors are active. When the user backgrounds the app, it cancels upstream after a 5-second grace period to save battery, but survives screen rotation without re-fetching. It is essential for offline-first Room or network observation flows.\n\n"
            "2. **`Lazily` for In-Memory Shared Caches:** In singleton repositories or domain services, `Lazily` delays expensive upstream initialization until the very first consumer requests the data. Once started, it remains active in memory, caching emissions for all subsequent app features without redundant restarts.\n\n"
            "3. **`Eagerly` for Mission-Critical Infrastructure:** For application-wide monitors that must begin capturing state immediately upon app launch—such as monitoring network connectivity flags or device security posture—`Eagerly` ensures the flow is immediately active before any UI subscribes."
        ),
        "deep_answer": (
            "The battery implications of these choices are profound in production Android vitals. "
            "If an engineer naively defaults to `SharingStarted.Eagerly` in a ViewModel, and that ViewModel observes an upstream location flow or a continuous Room database query, that query will run indefinitely in the background whenever that screen is in the backstack! "
            "Over hundreds of thousands of users, this results in significant battery drain and elevated uninstallation rates.\n\n"
            "By implementing `WhileSubscribed(5000)`: "
            "The 5-second timer is specifically calibrated to Android OS lifecycle timings. An Activity recreation during rotation typically takes between 100ms and 500ms. A 5,000ms timeout provides a 10x safety margin, guaranteeing zero flow thrashing during rotation while reliably shutting down within 5 seconds when the user navigates away or presses the home button."
        ),
        "follow_ups": [
            {
                "interviewer": "Why not set `stopTimeoutMillis` to 10 minutes just to be safe?",
                "answer": "Setting it to 10 minutes defeats battery conservation. The upstream network and database sensors will continue running in the user's pocket for 10 full minutes after leaving the screen, draining device battery."
            },
            {
                "interviewer": "What is `replayExpirationMillis` in `WhileSubscribed`?",
                "answer": "It configures when the replay cache expires after all subscribers leave. By default (0), the cache is kept forever. Setting it to e.g. 60,000ms evicts the cached state if the user stays away for longer than a minute, forcing a fresh load on return."
            },
            {
                "interviewer": "Can you implement a custom `SharingStarted` strategy?",
                "answer": "Yes. `SharingStarted` is an interface with a `command(subscriptionCount: StateFlow<Int>): Flow<SharingCommand>` function. You can emit `SharingCommand.START` and `SharingCommand.STOP` based on custom business rules or network states."
            }
        ]
    },
    {
        "id": "FLO-32",
        "arabic_explanation": (
            "خطر استخدام `runCatching` حول كود الـ Coroutines والـ Flows هو أحد أكثر الأخطاء الخفية والمكلفة في Kotlin:\n\n"
            "1. ما هو أصل المشكلة في `runCatching`؟\n"
            "   - دالة `kotlin.runCatching { ... }` تم تصميمها لـ Standard Kotlin القديمة، وتقوم بالتقاط **`Throwable` بالكامل** (`catch (e: Throwable)`).\n"
            "   - في Kotlin Coroutines، آلية الإلغاء (Cancellation Mechanism) تعتمد بالكامل على رمي **`CancellationException`**.\n"
            "   - بما أن `CancellationException` تورث من `Throwable`، فإن `runCatching` **تلتقط إشارة الإلغاء وتبتلعها وتغلفها كـ `Result.failure`**!\n\n"
            "2. النتائج الكارثية في الـ Production:\n"
            "   - **كسر الـ Structured Concurrency:** الكوروتين ترفض التوقف! لو تم إلغاء الـ ViewModel أو الـ Scope، الكود يستمر في التنفيذ ويضيع الموارد.\n"
            "   - **كسر المشغلات المعلقة (Operators Failure):** المشغلات التي تعتمد على الإلغاء (مثل `withTimeout`, `collectLatest`, `flatMapLatest`) تتوقف عن العمل بشكل سليم لأن الإلغاء يتم ابتلاعه!\n\n"
            "3. الحل السليم:\n"
            "   - عدم استخدام `runCatching` مع الدوال المعلقة، أو استخدام دالة مخصصة `runSuspendCatching` تعيد رمي `CancellationException` فوراً:\n"
            "     `if (e is CancellationException) throw e`"
        ),
        "practical_walkthrough": (
            "المقارنة بين الكود المعطوب والكود المصحح:\n"
            "```kotlin\n"
            "// ❌ الكود الكارثي باستخدام runCatching:\n"
            "suspend fun syncData() {\n"
            "    runCatching {\n"
            "        api.fetchUpdates() // لو تم إلغاء الـ coroutine، سيتم رمي CancellationException\n"
            "    }.onFailure {\n"
            "        // ابتلاع الإلغاء! الكود يظن أن السيرفر فشل، والـ coroutine لا تتوقف!\n"
            "        showErrorDialog()\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ الكود المصحح والآمن مع Coroutines:\n"
            "inline fun <T> runSuspendCatching(block: () -> T): Result<T> {\n"
            "    return try {\n"
            "        Result.success(block())\n"
            "    } catch (e: CancellationException) {\n"
            "        throw e // إعادة الرمي فوراً لضمان الإلغاء السليم!\n"
            "    } catch (e: Throwable) {\n"
            "        Result.failure(e)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "runCatching catches all Throwables including CancellationException. This swallows coroutines' cooperative cancellation signals, converting cancellations into regular failures, breaking structured concurrency, leaking background tasks, and causing operators like withTimeout and flatMapLatest to malfunction.",
        "best_answer": (
            "Using `kotlin.runCatching` around cancellable coroutine or flow work is a well-documented antipattern because it fundamentally breaks structured concurrency.\n\n"
            "`runCatching` is implemented with an indiscriminate `catch (e: Throwable)`. In Kotlin Coroutines, cooperative cancellation is driven by throwing `CancellationException`. Because `CancellationException` inherits from `Throwable`, `runCatching` intercepts the cancellation signal and encapsulates it as a `Result.failure(cancellationException)`.\n\n"
            "This causes catastrophic side effects:\n\n"
            "1. The coroutine refuses to terminate, continuing to execute subsequent statements when it was supposed to stop.\n"
            "2. Operators that rely on cancellation—such as `withTimeout`, `collectLatest`, and `debounce`—fail to work properly.\n\n"
            "In production, we strictly forbid `runCatching` on suspend functions, replacing it with a custom `runSuspendCatching` helper or standard `try-catch` blocks that explicitly rethrow `CancellationException`."
        ),
        "deep_answer": (
            "Under the hood, why was `runCatching` designed this way in the Kotlin standard library?\n\n"
            "Because `kotlin.Result` was introduced as a general JVM feature, independent of the coroutines library. When coroutines adopted `CancellationException` as a control-flow unwinding mechanism, the two APIs came into conflict.\n\n"
            "Consider what happens inside a Flow pipeline:\n\n"
            "```kotlin\n"
            "flow.map {\n"
            "    runCatching { api.call(it) } // CATCHES CANCELLATION!\n"
            "}\n"
            "```\n\n"
            "If the collector cancels, `api.call(it)` throws `CancellationException`. `runCatching` catches it, treats it as an error, and downstream receives `Result.failure`. The downstream collector then attempts to process this 'failure', triggering secondary bugs like showing an error snackbar for a screen that the user voluntarily closed!\n\n"
            "In enterprise codebases, we enforce a Detekt static analysis rule: flagging any invocation of `kotlin.runCatching` containing a suspending call."
        ),
        "follow_ups": [
            {
                "interviewer": "How does Kotlin Flow's `.catch { }` operator handle `CancellationException`?",
                "answer": "Flow's `.catch { }` operator is coroutine-aware: it explicitly rethrows `CancellationException` internally, guaranteeing that downstream cancellation unwinds properly while only intercepting real application exceptions."
            },
            {
                "interviewer": "Can you use `runCatching` if you check the exception in `onFailure`?",
                "answer": "You could write `.onFailure { if (it is CancellationException) throw it }`, but it is error-prone and easy for junior engineers to forget. Using a dedicated `runSuspendCatching` is much safer."
            },
            {
                "interviewer": "Does `withContext` swallow `CancellationException`?",
                "answer": "No. `withContext` properly rethrows `CancellationException` upon entry and exit, adhering to structured concurrency."
            }
        ]
    }
]


def main() -> None:
    existing = []
    if DATA_FILE.exists():
        try:
            existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            existing = []

    combined = []
    seen = set()
    for q in existing:
        combined.append(q)
        seen.add(q["id"])

    for q in FLO_25_32:
        if q["id"] not in seen:
            combined.append(q)
            seen.add(q["id"])
        else:
            for idx, item in enumerate(combined):
                if item["id"] == q["id"]:
                    combined[idx] = q
                    break

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(combined, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions FLO-25 to FLO-32. Total questions: {len(combined)}")


if __name__ == "__main__":
    main()

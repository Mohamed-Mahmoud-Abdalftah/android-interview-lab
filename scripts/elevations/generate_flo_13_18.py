#!/usr/bin/env python3
"""Generator for FLO-13 through FLO-18 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "flo.json"

FLO_13_18 = [
    {
        "id": "FLO-13",
        "arabic_explanation": (
            "المقارنة بين `combine` و `zip` بتحدد كيفية دمج تدفقين من البيانات (Merging two Flows):\n\n"
            "1. المشغل `combine` (الدمج عند أي تحديث جديد):\n"
            "   - يدمج التدفقين، و **يصدر قيمة جديدة في كل مرة يصدر فيها أي من التدفقين قيمة جديدة** (بشرط أن يكون كلا التدفقين قد أصدرا قيمة أولى على الأقل).\n"
            "   - يأخذ أحدث قيمة من التدفق الأول مع أحدث قيمة من التدفق الثاني (Latest values combined).\n"
            "   - **الاستخدام المثالي في Android:** تجميع مدخلات شاشة متعددة (مثل: نص البحث + خيار الفلتر المختار + حالة الاتصال بالإنترنت) لتوليد حالة الـ UI.\n\n"
            "2. المشغل `zip` (الربط الزوجي المتسلسل 1:1):\n"
            "   - يربط العناصر **زوجاً بزوج حسب الترتيب (Strict 1-to-1 Pairing)**.\n"
            "   - العنصر الأول من التدفق A يُربط فقط مع العنصر الأول من التدفق B. والعنصر الثاني مع الثاني، وهكذا.\n"
            "   - لو التدفق A أصدر 10 عناصر بينما التدفق B أصدر عنصراً واحداً فقط، الـ `zip` سينتظر ويتعلق حتى يصدر B عنصره الثاني قبل إنتاج الزوج الثاني!\n"
            "   - ينتهي البث بمجرد انتهاء أقصر تدفق بينهما."
        ),
        "practical_walkthrough": (
            "مقارنة عملية في الكود:\n"
            "```kotlin\n"
            "val flowA = flowOf(\"A1\", \"A2\", \"A3\")\n"
            "val flowB = flowOf(\"B1\", \"B2\")\n"
            "\n"
            "// مع zip:\n"
            "flowA.zip(flowB) { a, b -> \"$a-$b\" }.collect { println(it) }\n"
            "// النتيجة: \"A1-B1\", \"A2-B2\" فقط! (A3 تم تجاهله لأن B انتهى)\n"
            "\n"
            "// مع combine في الـ ViewModel الحقيقي:\n"
            "combine(\n"
            "    searchQueryFlow,\n"
            "    selectedCategoryFlow,\n"
            "    sortByFlow\n"
            ") { query, category, sort ->\n"
            "    // كلما غير المستخدم الفلتر أو الحرف المكتوب، يتم إنتاج حالة جديدة فوراً بأحدث القيم:\n"
            "    FilterState(query, category, sort)\n"
            "}.collect { updateUi(it) }\n"
            "```"
        ),
        "quick_answer": "combine emits a new paired value whenever EITHER flow emits, using the latest values from both streams; zip pairs elements strictly 1-to-1 by order index (item 1 with item 1, item 2 with item 2) and halts when the shorter flow completes.",
        "best_answer": (
            "The difference between `combine` and `zip` comes down to temporal pairing versus index-based pairing.\n\n"
            "**`combine`** is the standard workhorse for Android UI state generation. Once each upstream flow emits at least once, `combine` produces a new value whenever *either* flow emits, pairing the newly emitted item with the most recent cached item from the other stream. I use it constantly in ViewModels to merge search text, category filters, and user authentication status into a single unified `UiState`.\n\n"
            "**`zip`** enforces strict index-based 1-to-1 pairing. Element 0 from Flow A is paired only with Element 0 from Flow B. If Flow A emits 5 items while Flow B emits 1, `zip` suspends after the first pair, waiting until Flow B produces its second item. Furthermore, `zip` terminates as soon as the shorter flow completes."
        ),
        "deep_answer": (
            "Under the hood, `combine` is implemented using internal channels and fair selector loops (`select` expression). It maintains internal state slots for each upstream stream. "
            "When any upstream sends a new value, the slot is updated, and the transform lambda is evaluated with the latest snapshot of all slots.\n\n"
            "In contrast, `zip` buffers upstream emissions sequentially in paired queues. If one flow is fast and the other is slow, `zip` buffers the fast flow's items in memory waiting for corresponding pairs, which can create heap memory pressure if the flows emit at vastly different cadences.\n\n"
            "In modern Android development, `combine` supports merging up to 5 flows directly with type-safe overloads, or an arbitrary `Array<Flow<T>>` for dynamic widget configurations."
        ),
        "follow_ups": [
            {
                "interviewer": "Why won't `combine` emit anything if one of the flows never emits an initial item?",
                "answer": "Because `combine` requires a full set of values to evaluate its transform lambda. If Flow A emits 10 values but Flow B has not emitted anything yet, `combine` buffers the latest from Flow A and remains silent until Flow B emits its first element."
            },
            {
                "interviewer": "Can you combine more than 5 flows in Kotlin?",
                "answer": "Yes. There is an overload `combine(vararg flows: Flow<T>) { array -> ... }` that takes an array or collection of flows, returning an array of latest values."
            },
            {
                "interviewer": "When would you actually use `zip` in a real Android app?",
                "answer": "When you have two ordered sequential streams that correspond 1-to-1, such as pairing a stream of recorded audio frames with a synchronized stream of video frame timestamps."
            }
        ]
    },
    {
        "id": "FLO-14",
        "arabic_explanation": (
            "المقارنة بين مشغلات التسطيح (Flattening Operators) `flatMapLatest` و `flatMapConcat` و `flatMapMerge`:\n\n"
            "1. `flatMapConcat` (التسطيح التسلسلي المتتابع):\n"
            "   - ينتظر انتهاء التدفق الداخلي الأول بالكامل قبل أن يبدأ التدفق الداخلي التالي (Sequential).\n"
            "   - لو عندك أحداث سريعة، كل حدث سينتظر في الطابور حتى ينتهي التدفق السابق تماماً.\n"
            "   - يضمن الترتيب الصارم 100%، لكنه بطيء ولا يدعم التوازي.\n\n"
            "2. `flatMapMerge` (التسطيح المتوازي المتزامن):\n"
            "   - يجمع التدفقات الداخلية بالتوازي في نفس الوقت (Concurrent).\n"
            "   - يسمح بتحديد سقف التوازي عبر معامل `concurrency` (الافتراضي 16).\n"
            "   - النتائج قد تتداخل وتصل بدون ترتيب زمني مطابق لترتيب الانطلاق.\n\n"
            "3. `flatMapLatest` (التسطيح مع الإلغاء الفوري للأقدم):\n"
            "   - **يلغي التدفق الداخلي الحالي فوراً بمجرد وصول عنصر جديد من الـ Upstream!**\n"
            "   - المشغل رقم 1 في شاشات البحث والـ UI: إذا كتب المستخدم حرفاً جديداً، يلغي طلب الشبكة الداخلي القديم فوراً ويبدأ طلباً للبحث الجديد."
        ),
        "practical_walkthrough": (
            "مقارنة عملية في شاشة البحث عن مستخدمين:\n"
            "```kotlin\n"
            "// 1. flatMapLatest في البحث (هو الأنسب دائماً): \n"
            "searchQueryFlow\n"
            "    .debounce(300L)\n"
            "    .flatMapLatest { query ->\n"
            "        repository.searchUsers(query) // لو كتب المستخدم كلمة جديدة، يلغي البحث السابق فوراً!\n"
            "    }\n"
            "    .collect { render(it) }\n"
            "\n"
            "// 2. flatMapConcat في معالجة طلبات متسلسلة (تفريغ طابور حفظ):\n"
            "uploadQueueFlow\n"
            "    .flatMapConcat { file ->\n"
            "        repository.uploadSingleFile(file) // لا يبدأ رفع الملف الثاني حتى ينتهي الأول تماماً\n"
            "    }\n"
            "\n"
            "// 3. flatMapMerge في جلب تفاصيل متوازية:\n"
            "userIdsFlow\n"
            "    .flatMapMerge(concurrency = 3) { id ->\n"
            "        repository.fetchUserDetails(id) // يجلب 3 مستخدمين بالتوازي لتوفير الوقت\n"
            "    }\n"
            "```"
        ),
        "quick_answer": "flatMapConcat flattens streams sequentially, waiting for the previous inner flow to complete before starting the next; flatMapMerge flattens inner streams concurrently with a concurrency limit; and flatMapLatest cancels the active inner flow immediately whenever a new upstream value arrives.",
        "best_answer": (
            "These three flattening operators transform incoming values into child flows, differing in how they handle concurrency and cancellation:\n\n"
            "**`flatMapConcat`** executes child flows sequentially. When an upstream item arrives, it collects its child flow to completion before collecting the child flow of the next upstream item. It strictly preserves ordering but does not allow concurrency.\n\n"
            "**`flatMapMerge`** collects multiple child flows concurrently, merging their emissions into a single downstream stream as they arrive. You can configure the `concurrency` parameter (default 16) to limit simultaneous inner flows. Output order is interleaved and non-deterministic.\n\n"
            "**`flatMapLatest`** cancels the currently executing child flow as soon as a new upstream value arrives, switching collection to the new child flow immediately. This is the definitive operator for search queries and UI filters: if the user types a new character, the previous in-flight network request is cancelled immediately."
        ),
        "deep_answer": (
            "Under the hood, `flatMapLatest` is an experimental shorthand composed of `mapLatest { transform(it) }.flattenConcat()`. "
            "Because it relies on cooperative coroutine cancellation, if the child flow invokes non-suspending, blocking network calls or un-cancellable loops, cancellation will fail to terminate the background work until the call returns.\n\n"
            "In enterprise Android architectures, using `flatMapLatest` for read operations (search, filters, suggestions) is recommended. "
            "However, **never use `flatMapLatest` for write or mutation operations** (such as placing an order, uploading receipts, or database migrations). If a user taps a submit button twice rapidly, `flatMapLatest` will cancel the first purchase mid-flight, leaving backend transactions in an inconsistent or orphaned state. For mutations, use `flatMapConcat` or discrete sequential coroutines."
        ),
        "follow_ups": [
            {
                "interviewer": "Why is `flatMapConcat` dangerous with infinite child flows?",
                "answer": "If a child flow is infinite (e.g., a continuous database observation stream that never completes), `flatMapConcat` will collect that child flow forever and will never process any subsequent upstream items!"
            },
            {
                "interviewer": "What is the default concurrency limit of `flatMapMerge`?",
                "answer": "The default concurrency limit is `DEFAULT_CONCURRENCY`, which is 16. You can constrain it (e.g., `flatMapMerge(concurrency = 4)`) to throttle parallel operations."
            },
            {
                "interviewer": "How does `flatMapLatest` compare to RxJava's `switchMap`?",
                "answer": "`flatMapLatest` in Kotlin Flow is the exact conceptual equivalent of RxJava's `switchMap`: both cancel the previous inner subscription when a new item arrives."
            }
        ]
    },
    {
        "id": "FLO-15",
        "arabic_explanation": (
            "المشغلان `debounce` و `distinctUntilChanged` هما الثنائي الكلاسيكي لبناء مربع بحث (Search Box) فائق الكفاءة والسرعة:\n\n"
            "1. المشغل `debounce(timeoutMillis)`:\n"
            "   - يؤخر تمرير العنصر حتى يمر وقت محدد (مثلاً 300ms) **بدون أن يصدر الـ Upstream أي عنصر جديد**.\n"
            "   - **لماذا في البحث؟** المستخدم عندما يكتب كلمة 'Android'، يضغط على 7 أزرار في أقل من ثانية. بدون debounce، التطبيق سيرسل 7 طلبات شبكة للسيرفر! مع `debounce(300L)`، التطبيق ينتظر حتى يتوقف المستخدم عن الكتابة لمدة 300ms ثم يرسل طلباً واحداً فقط بالكلمة النهائية.\n\n"
            "2. المشغل `distinctUntilChanged()`:\n"
            "   - يقمع ويتجاهل العنصر الجديد **إذا كان مطابقاً للعنصر السابق مباشرة** (بالمقارنة بـ `equals()`).\n"
            "   - **لماذا في البحث؟** لو المستخدم كتب 'Kotlin'، ثم مسح حرف الـ 'n' ثم أعاد كتابته بسرعة في أقل من 300ms، النص النهائي لا يزال 'Kotlin'! المشغل `distinctUntilChanged()` يكتشف أن النص لم يتغير ويتجاهل إرسال طلب شبكة مكرر للسيرفر."
        ),
        "practical_walkthrough": (
            "الكود المعماري المثالي لشريط البحث في ViewModel:\n"
            "```kotlin\n"
            "class SearchViewModel(private val repository: SearchRepository) : ViewModel() {\n"
            "    val searchQuery = MutableStateFlow(\"\")\n"
            "\n"
            "    val searchResults: StateFlow<SearchResultsUiState> = searchQuery\n"
            "        .map { it.trim() } // 1. تنظيف المسافات الزائدة\n"
            "        .debounce(300L)   // 2. الانتظار 300ms بعد توقف المستخدم عن الكتابة\n"
            "        .distinctUntilChanged() // 3. منع تكرار البحث لو النص مطابق للسابق\n"
            "        .flatMapLatest { query ->\n"
            "            if (query.isEmpty()) {\n"
            "                flowOf(SearchResultsUiState.Empty)\n"
            "            } else {\n"
            "                repository.search(query)\n"
            "                    .map { SearchResultsUiState.Success(it) }\n"
            "                    .catch { emit(SearchResultsUiState.Error(it.message ?: \"Error\")) }\n"
            "            }\n"
            "        }\n"
            "        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000L), SearchResultsUiState.Empty)\n"
            "}\n"
            "```"
        ),
        "quick_answer": "debounce pauses emission until a specified quiet period (e.g., 300ms) elapses with no new input, throttling rapid typing; distinctUntilChanged filters out emissions that equal the immediately preceding emission, preventing duplicate search requests for identical query strings.",
        "best_answer": (
            "In Android search architecture, `debounce` and `distinctUntilChanged` work in tandem to eliminate redundant network traffic and improve UI responsiveness.\n\n"
            "**`debounce(300L)`** acts as a rate limiter. When a user types rapidly on a software keyboard, an emission fires for every keystroke. `debounce` starts a timer on each character. If another keystroke arrives before 300 milliseconds elapse, the timer resets. Only when the user pauses typing for a full 300ms does the latest text emission proceed downstream.\n\n"
            "**`distinctUntilChanged()`** acts as an equality filter. It compares the incoming value against the previously emitted value using `equals()`. If the user types 'A', quickly deletes it, and types 'A' again, the debounced text is still 'A'. `distinctUntilChanged` recognizes that the query hasn't changed and suppresses the duplicate emission, preventing a redundant network query."
        ),
        "deep_answer": (
            "Under the hood, `debounce` launches a timer coroutine on the coroutine scheduler. When a new upstream emission arrives, the previous delayed task is cancelled, and a new delayed emission is scheduled. "
            "When testing `debounce` with `runTest`, virtual time makes verification instantaneous: you can advance time by 299ms to assert no search occurred, and then call `advanceTimeBy(2)` to verify the search query triggered.\n\n"
            "With `distinctUntilChanged()`, the operator maintains a reference to the previous emission in memory. You can also provide a custom key selector: `distinctUntilChangedBy { it.id }` or a custom comparison lambda. "
            "Pairing this pipeline with `flatMapLatest` guarantees that even if a debounced search query is sent, if the user starts typing again while the backend is responding, the stale network call is immediately cancelled in favor of the newer query."
        ),
        "follow_ups": [
            {
                "interviewer": "Why should you call `.map { it.trim() }` before `distinctUntilChanged()`?",
                "answer": "Because users frequently type accidental trailing spaces. Trimming the query beforehand ensures that 'Android ' and 'Android' evaluate as equal, preventing duplicate search queries."
            },
            {
                "interviewer": "What happens if a user submits a search via the keyboard 'Enter' action?",
                "answer": "The 'Enter' action should bypass the debounce delay. In the ViewModel, you provide an explicit `searchImmediately()` method that immediately triggers the search without waiting for the 300ms debounce timer."
            },
            {
                "interviewer": "Does `distinctUntilChanged()` work on complex data classes?",
                "answer": "Yes, as long as the data class generates structural `equals()` for all properties. If custom classes are used, you must properly implement `equals()` and `hashCode()`."
            }
        ]
    },
    {
        "id": "FLO-16",
        "arabic_explanation": (
            "المقارنة الشاملة بين استراتيجيات التعامل مع الضغط العكسي وتزاحم البيانات (Backpressure & Concurrency Strategies):\n\n"
            "1. `merge` (الدمج المتزامن):\n"
            "   - يدمج عدة Flows في تدفق واحد ويبث عناصرها في نفس اللحظة التي تصدر فيها (Interleaved).\n"
            "   - لا يؤخر ولا يلغي أي شيء.\n\n"
            "2. `buffer(capacity)` (التخزين المؤقت في الذاكرة):\n"
            "   - يفصل الـ Producer عن الـ Collector في خيوط/كوروتينز منفصلة باستخدام Channel وسيطة.\n"
            "   - يسمح للـ Producer بالاستمرار في إنتاج البيانات حتى لو كان الـ Collector بطيئاً، حتى يمتلئ الـ Buffer.\n\n"
            "3. `conflate` (التخطي لصالح الأحدث):\n"
            "   - حالة خاصة من `buffer(capacity = 1, onBufferOverflow = DROP_OLDEST)`.\n"
            "   - لو الـ Collector مشغول في معالجة عنصر، والـ Producer أنتج 5 عناصر جديدة، يتم **إسقاط وتخطي الـ 4 عناصر القديمة**، وإعطاء الـ Collector العنصر الأخير فقط بمجرد أن يفرغ!\n\n"
            "4. `collectLatest` (الإلغاء الفوري للعمل الحالي):\n"
            "   - لا ينتظر الـ Collector حتى يفرغ! **يلغي الـ Coroutine الخاصة بالعنصر القديم فوراً** ويبدأ معالجة العنصر الجديد في اللحظة التي يصل فيها."
        ),
        "practical_walkthrough": (
            "توضيح الفرق بالرسم ومثال قراءة الحساسات (Sensor Data):\n"
            "- حساس الحركة يصدر 100 إحداثية في الثانية، والـ UI يستغرق 50ms لرسم الشاشة:\n"
            "  * بدون أي شيء (Default): الـ Producer سيتعلق وينتظر الـ Collector، فتنخفض قراءات الحساس ويحدث بطء عام.\n"
            "  * مع `buffer(100)`: الحساس ينتج في الذاكرة، ولكن الـ UI سيتأخر أكثر فأكثر عن الواقع (Lagging UI) لأن الطابور يزداد طولاً!\n"
            "  * مع `conflate()`: الـ UI يكمل رسم الإطار الحالي، ولما يخلص يأخذ أحدث إحداثية من الحساس ويسقط كل ما حدث أثناء الرسم. ممتاز لعرض عداد السرعة!\n"
            "  * مع `collectLatest`: إذا وصل إحداثي جديد، يتم إلغاء رسم الإطار القديم فوراً والبدء في رسم الإحداثي الجديد."
        ),
        "quick_answer": "merge combines multiple streams concurrently into one; buffer decouples producer and collector via an in-memory queue to absorb speed mismatches; conflate drops intermediate unread values keeping only the newest; and collectLatest cancels the collector's current in-flight execution immediately when a new value arrives.",
        "best_answer": (
            "These operators provide distinct concurrency and backpressure buffering strategies when producer and collector speeds diverge:\n\n"
            "**`merge`** combines emissions from multiple flows into a single unified stream, executing concurrently and interleaving items as they appear.\n\n"
            "**`buffer(capacity)`** runs the upstream producer and downstream collector in separate concurrent coroutines connected via a Channel queue. It allows a fast producer to continue generating values without suspending, absorbing bursty spikes as long as the buffer has room.\n\n"
            "**`conflate()`** is a backpressure dropper. If the collector is slow, `conflate` skips intermediate upstream values and only delivers the freshest, most recent item when the collector finishes its current task. The collector finishes its work uninterrupted.\n\n"
            "**`collectLatest`** takes cancellation further: rather than letting the slow collector finish, it cancels the active collector block immediately the instant a new emission arrives, switching work immediately to the latest value."
        ),
        "deep_answer": (
            "Under the hood, `conflate()` is literally defined in the Kotlin standard library as `buffer(Channel.CONFLATED)`. "
            "A conflated channel holds a buffer of size 1 and uses `BufferOverflow.DROP_OLDEST`. "
            "This makes `conflate` allocation-friendly: it retains a single slot on the heap and overwrites the pointer without allocating queue nodes.\n\n"
            "The difference between `conflate` and `collectLatest` is a frequent staff-level interview distinction: "
            "With `conflate`, the collector **never gets interrupted** while working on an item; it completes its current iteration fully, and only then reads the latest element from the buffer. "
            "With `collectLatest`, the collector **is aggressively interrupted and cancelled** via `CancellationException` mid-execution whenever an upstream item arrives. "
            "If your collector block modifies persistent storage (like saving a file), `collectLatest` can abort mid-write, while `conflate` lets each write complete cleanly."
        ),
        "follow_ups": [
            {
                "interviewer": "When would you prefer `conflate` over `collectLatest`?",
                "answer": "When the collector's work is a transactional task that must run to completion once started (like saving a frame to disk or completing a database transaction), but you only want to process the latest available item next."
            },
            {
                "interviewer": "What is the default buffer size in `buffer()`?",
                "answer": "Calling `buffer()` without parameters uses `Channel.BUFFERED`, which defaults to a capacity of 64 elements."
            },
            {
                "interviewer": "Does `buffer()` change the CoroutineDispatcher of the upstream flow?",
                "answer": "No. `buffer()` only introduces a Channel between concurrent coroutines. To change the dispatcher of the upstream flow, you must use `flowOn()`."
            }
        ]
    },
    {
        "id": "FLO-17",
        "arabic_explanation": (
            "المشغل `flowOn` ومبدأ **Context Preservation** هو أحد أهم قواعد تدفق السياق في Kotlin Flow:\n\n"
            "1. ما هو مبدأ Context Preservation؟\n"
            "   - في Kotlin Flow، القاعدة الصارمة هي: **الـ Flow يحافظ على سياق المستمع (Collector's Context)**.\n"
            "   - لا يجوز للـ Flow أن يقوم بعمل `withContext` داخل بلوك `flow { ... }` لتغيير الـ Dispatcher وإصدار قيم منه! لو حاولت كتابة `withContext(Dispatchers.IO) { emit(data) }`، التطبيق سيعمل Crash فوراً بـ `IllegalStateException: Flow invariant is violated`!\n\n"
            "2. ما الذي يفعله `flowOn`؟\n"
            "   - `flowOn` هو الأداة الشرعية الوحيدة لتغيير سياق تنفيذ الـ Flow.\n"
            "   - يؤثر **فقط على الـ Upstream (ما قبله في السلسلة)**، ولا يؤثر إطلاقاً على الـ Downstream (ما بعده أو الـ Collector)!\n"
            "   - يقوم بإنشاء Coroutine منفصلة للـ Upstream على الـ Dispatcher المحدد، ويربطها بالـ Downstream عبر Channel."
        ),
        "practical_walkthrough": (
            "تطبيق عملي يوضح اتجاه تأثير `flowOn` بدقة:\n"
            "```kotlin\n"
            "flow {\n"
            "    // 1. هذا الكود سيعمل على Dispatchers.IO بسبب flowOn(Dispatchers.IO):\n"
            "    val fileData = readHeavyFileFromDisk()\n"
            "    emit(fileData)\n"
            "}\n"
            ".flowOn(Dispatchers.IO) // يغير سياق كل ما قبله فقط (Upstream)!\n"
            ".map {\n"
            "    // 2. هذا الكود سيعمل على Dispatchers.Default بسبب flowOn(Dispatchers.Default):\n"
            "    parseJsonCompute(it)\n"
            "}\n"
            ".flowOn(Dispatchers.Default) // يغير سياق map فقط!\n"
            ".collect { uiData ->\n"
            "    // 3. هذا الكود سيعمل على سياق الـ Collector (مثلاً Dispatchers.Main):\n"
            "    renderUi(uiData)\n"
            "}\n"
            "```"
        ),
        "quick_answer": "flowOn changes the CoroutineContext (such as Dispatcher) of upstream operations preceding it in the pipeline, without affecting downstream operators or the collector. It enforces Flow's Context Preservation rule by managing thread switching through an internal channel buffer rather than illegal withContext emissions.",
        "best_answer": (
            "`flowOn` controls the execution context—primarily the `CoroutineDispatcher`—of the **upstream** operations that precede it in the flow pipeline.\n\n"
            "In Kotlin Flow, there is a foundational invariant called **Context Preservation**: a flow must always emit values within the context of the collector, and calling `withContext` inside a `flow { }` builder to emit values is strictly forbidden and throws an `IllegalStateException`.\n\n"
            "To safely offload expensive upstream work without breaking this invariant, we use `flowOn`. It launches the upstream operations in a separate coroutine on the specified dispatcher (e.g., `Dispatchers.IO`), streams the emitted values through an internal buffer channel, and delivers them to downstream operators and the collector on their own designated dispatcher (e.g., `Dispatchers.Main`)."
        ),
        "deep_answer": (
            "Under the hood, why does Kotlin forbid `withContext` around `emit()`?\n\n"
            "```kotlin\n"
            "// ❌ ILLEGAL - Throws IllegalStateException:\n"
            "flow {\n"
            "    withContext(Dispatchers.IO) {\n"
            "        emit(loadData()) // VIOLATES FLOW INVARIANT!\n"
            "    }\n"
            "}\n"
            "```\n\n"
            "Because `emit` calls the collector's suspending lambda directly. If upstream used `withContext`, it would forcibly drag the collector's execution onto a foreign thread without the collector's knowledge or consent, breaking structured concurrency.\n\n"
            "`flowOn` avoids this by introducing an asynchronous channel boundary. It acts like a concurrent pipe: the upstream produces elements onto a worker thread, writes them to a Channel, and the downstream collector reads from that Channel on its own caller thread. "
            "You can chain multiple `flowOn` calls: each `flowOn` operator dictates the dispatcher for everything above it up to the previous `flowOn` boundary."
        ),
        "follow_ups": [
            {
                "interviewer": "Does `flowOn` affect the thread of the `collect { }` block?",
                "answer": "No, never. The `collect { }` block always executes on the CoroutineContext of the coroutine that invoked `collect`. `flowOn` only modifies the context of operators upstream from it."
            },
            {
                "interviewer": "Does `flowOn` add an internal buffer?",
                "answer": "Yes. Because `flowOn` switches dispatchers between producer and consumer coroutines, it introduces an internal buffer channel (default capacity 64 or Channel.BUFFERED) to prevent producer stalls."
            },
            {
                "interviewer": "What happens if you have two `flowOn` operators in a chain?",
                "answer": "Each `flowOn` applies strictly to the upstream pipeline segments above it up to the preceding `flowOn`. This allows reading on `Dispatchers.IO` and parsing on `Dispatchers.Default` in a single declarative chain."
            }
        ]
    },
    {
        "id": "FLO-18",
        "arabic_explanation": (
            "المقارنة بين مشغلات معالجة الأخطاء وإنهاء التدفق `catch` و `retry` و `retryWhen` و `onCompletion`:\n\n"
            "1. المشغل `catch`:\n"
            "   - يلتقط الاستثناءات التي تحدث في **الـ Upstream فقط (ما قبله في السلسلة)**.\n"
            "   - يسمح لك بإصدار قيمة بديلة عبر `emit(fallback)` أو تسجيل الخطأ.\n"
            "   - **تحذير خطير:** الـ `catch` لا يلتقط الأخطاء التي تحدث في الـ Downstream أو داخل بلوك `collect { }` الذي يليه!\n\n"
            "2. المشغل `retry(retries)`:\n"
            "   - يعيد محاولة جمع الـ Flow من البداية لعدد محدد من المرات إذا حدث استثناء في الـ Upstream.\n\n"
            "3. المشغل `retryWhen(predicate)`:\n"
            "   - أكثر مرونة وتحكماً؛ يمرر لك سبب الخطأ ورقم المحاولة الحالية (`cause: Throwable, attempt: Long`).\n"
            "   - يسمح بتطبيق **Exponential Backoff** عبر مناداة `delay()` داخل البلوك وإرجاع `true` لإعادة المحاولة أو `false` للاستسلام.\n\n"
            "4. المشغل `onCompletion`:\n"
            "   - ينفذ كود عند انتهاء الـ Flow سواء انتهى بنجاح طبيعي (`cause == null`) أو انتهى بسبب استثناء أو إلغاء (`cause != null`).\n"
            "   - يشبه كتلة الـ `finally` في الـ try-catch."
        ),
        "practical_walkthrough": (
            "سلسلة معالجة أخطاء إنتاجية متكاملة في Repository:\n"
            "```kotlin\n"
            "fun getLiveFeed(): Flow<FeedState> = feedApi.streamUpdates()\n"
            "    .retryWhen { cause, attempt ->\n"
            "        // 1. إعادة المحاولة فقط في أخطاء الشبكة المؤقتة وبحد أقصى 3 مرات:\n"
            "        if (cause is IOException && attempt < 3) {\n"
            "            delay(1000L * (attempt + 1)) // exponential delay\n"
            "            true // أعد المحاولة\n"
            "        } else false // استسلم ومرر الخطأ للأسفل\n"
            "    }\n"
            "    .catch { error ->\n"
            "        // 2. التقاط الخطأ النهائي وإصدار حالة الفشل بدلاً من تحطيم التطبيق:\n"
            "        emit(FeedState.Error(error.message ?: \"Network error\"))\n"
            "    }\n"
            "    .onCompletion { cause ->\n"
            "        // 3. تنظيف وإغلاق الاتصال:\n"
            "        closeConnectionHandles()\n"
            "    }\n"
            "```"
        ),
        "quick_answer": "catch intercepts upstream exceptions and emits fallback values; retry attempts upstream re-collection for a fixed count; retryWhen provides dynamic retry predicates with exponential backoff; and onCompletion executes cleanup upon completion or failure, analogous to a finally block.",
        "best_answer": (
            "These operators handle resilience, recovery, and cleanup across the lifecycle of a Flow:\n\n"
            "**`catch`** intercepts exceptions thrown by upstream operators or the producer block. It allows graceful recovery by inspecting the error, logging telemetry, or emitting a fallback state via `emit()`. Crucially, `catch` only intercepts upstream errors; it does not catch exceptions thrown inside the downstream `collect { }` block.\n\n"
            "**`retry`** transparently re-subscribes to the upstream flow if an upstream exception occurs, up to a specified attempt count.\n\n"
            "**`retryWhen`** is the advanced predicate version, passing the `Throwable` and the current `attempt` counter. It allows implementing exponential backoff with jitter via `delay()` and selectively retrying transient IOExceptions while failing immediately on permanent 4xx errors.\n\n"
            "**`onCompletion`** executes when the stream terminates, receiving a nullable `Throwable?` parameter. If `cause == null`, the flow finished normally; if non-null, it completed due to an exception or cancellation. It serves as Flow's reactive `finally` block for closing resources."
        ),
        "deep_answer": (
            "A frequent architecture trap in code reviews is placing `catch` above operators that might also fail, or failing to handle errors thrown inside `collect`:\n\n"
            "```kotlin\n"
            "// ❌ BUG: catch does not intercept collect errors:\n"
            "flow.catch { emit(Fallback) }\n"
            "    .collect { throw RuntimeException() } // Crash! catch cannot see this!\n"
            "```\n\n"
            "To catch errors that occur during element handling, the recommended pattern is moving the collection logic into `onEach` before `catch`, and terminating with a plain `collect()`:\n\n"
            "```kotlin\n"
            "// ✅ SAFE: catches both producer and processing errors:\n"
            "flow\n"
            "    .onEach { processItem(it) }\n"
            "    .catch { handleException(it) }\n"
            "    .collect()\n"
            "```\n\n"
            "Furthermore, inside `catch`, `CancellationException` is respected by default: if a collector coroutine is cancelled, `catch` rethrows `CancellationException` to preserve structured concurrency."
        ),
        "follow_ups": [
            {
                "interviewer": "Can you emit values from inside `onCompletion`?",
                "answer": "Yes. `onCompletion` exposes a `FlowCollector`, allowing you to emit final sentinel values (e.g., `emit(UiState.Finished)`) upon stream completion, provided the flow did not abort due to an unhandled exception."
            },
            {
                "interviewer": "Why does `retryWhen` re-collect from the beginning of the flow?",
                "answer": "Because cold flows are lazy blueprints. When `retryWhen` returns true, it triggers a brand-new `collect()` invocation on the upstream flow, executing its producer code from the starting state."
            },
            {
                "interviewer": "Does `catch` swallow the exception if you don't call `emit()`?",
                "answer": "Yes. If the `catch` lambda simply logs the error and exits, the exception is considered handled and the stream completes cleanly without throwing an exception to the caller."
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

    for q in FLO_13_18:
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
    print(f"Updated {DATA_FILE} with questions FLO-13 to FLO-18. Total questions: {len(combined)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generator for FLO-19 through FLO-24 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "flo.json"

FLO_19_24 = [
    {
        "id": "FLO-19",
        "arabic_explanation": (
            "المعاملات الثلاثة لـ `MutableSharedFlow` (`replay`, `extraBufferCapacity`, `onBufferOverflow`) بتحدد سلوك الذاكرة وتوزيع الأحداث بدقة بالغة:\n\n"
            "1. المعامل `replay` (ذاكرة الإعادة للمستمعين الجدد):\n"
            "   - يحدد عدد العناصر السابقة (Past Items) التي يتم حفظها في الذاكرة لتسليمها فوراً لأي مستمع جديد يشترك مستقبلاً.\n"
            "   - لو `replay = 0`: المستمع الجديد لن يستلم أي شيء من الماضي؛ يستلم فقط ما يصدر بعد لحظة اشتراكه.\n"
            "   - لو `replay = 1`: المستمع الجديد يستلم أحدث عنصر فور اشتراكه (كما يفعل StateFlow).\n\n"
            "2. المعامل `extraBufferCapacity` (سعة التخزين المؤقت الإضافية):\n"
            "   - يحدد حجم الـ Buffer المتاح للـ Producer قبل أن يضطر للتعليق (Suspension) عند بطء المستمعين.\n"
            "   - الحجم الكلي المتاح للذاكرة المؤقتة هو: `replay + extraBufferCapacity`.\n\n"
            "3. المعامل `onBufferOverflow` (استراتيجية التصرف عند امتلاء الـ Buffer):\n"
            "   - **`BufferOverflow.SUSPEND` (الافتراضي):** الـ Producer يتعلق في دالة `emit()` وينتظر حتى يفرغ المستمع مساحة في الـ Buffer.\n"
            "   - **`BufferOverflow.DROP_OLDEST`:** يسقط أقدم عنصر في الـ Buffer لتوفير مساحة للعنصر الجديد بدون تعليق الـ Producer.\n"
            "   - **`BufferOverflow.DROP_LATEST`:** يسقط العنصر الجديد الحالي ويحافظ على العناصر القديمة بدون تعليق."
        ),
        "practical_walkthrough": (
            "تصميم SharedFlow للأحداث وسجل الإشعارات:\n"
            "```kotlin\n"
            "class NotificationCenter {\n"
            "    // نحتفظ بآخر 3 إشعارات للمشتركين الجدد، مع سعة إضافية 10، وإسقاط الأقدم عند الامتلاء:\n"
            "    val notifications = MutableSharedFlow<Notification>(\n"
            "        replay = 3,\n"
            "        extraBufferCapacity = 10,\n"
            "        onBufferOverflow = BufferOverflow.DROP_OLDEST\n"
            "    )\n"
            "    \n"
            "    fun postNotification(notification: Notification) {\n"
            "        // بفضل DROP_OLDEST، دالة tryEmit تنجح دائماً بدون الحاجة لكوروتين suspend:\n"
            "        notifications.tryEmit(notification)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "replay sets how many historical items are cached and re-emitted to new subscribers; extraBufferCapacity adds buffer space beyond replay to absorb bursts; and onBufferOverflow dictates behavior when the buffer fills: SUSPEND (pauses emitter), DROP_OLDEST (drops oldest item), or DROP_LATEST (drops new item).",
        "best_answer": (
            "These three parameters configure the buffer mechanics and backpressure semantics of `MutableSharedFlow`:\n\n"
            "**`replay`** defines the size of the replay cache. When a new collector subscribes, it immediately receives up to `replay` cached historical emissions. If set to 0, late subscribers receive nothing from the past. `StateFlow` is conceptually a SharedFlow with `replay = 1`.\n\n"
            "**`extraBufferCapacity`** provides additional queue capacity beyond the replay cache. The total buffer size is `replay + extraBufferCapacity`. It allows fast producers to continue emitting without suspension when downstream collectors are busy.\n\n"
            "**`onBufferOverflow`** configures backpressure behavior when the combined buffer is full. `BufferOverflow.SUSPEND` suspends `emit()` until downstream collectors catch up. `BufferOverflow.DROP_OLDEST` evicts the oldest buffered element to make room for the new one, enabling non-suspending `tryEmit()` to always succeed. `BufferOverflow.DROP_LATEST` discards the incoming item, preserving the existing buffer."
        ),
        "deep_answer": (
            "At the internal implementation level, `SharedFlowImpl` allocates a continuous array of slots representing the buffer. "
            "A critical engineering requirement involves `tryEmit()`. `tryEmit()` is a non-suspending method to post events. "
            "If `onBufferOverflow` is set to `BufferOverflow.SUSPEND` (the default) and there are slow collectors or the buffer is saturated, **`tryEmit()` will return `false` and drop the event silently**!\n\n"
            "Therefore, in Android architecture, if you intend to dispatch events from synchronous callbacks using `tryEmit()` (such as view click listeners without launching a coroutine), you must configure `extraBufferCapacity >= 1` and `onBufferOverflow = BufferOverflow.DROP_OLDEST`. This guarantees that `tryEmit()` never fails and never drops events unexpectedly."
        ),
        "follow_ups": [
            {
                "interviewer": "Why does `tryEmit` fail on a default `MutableSharedFlow()`?",
                "answer": "Because a default `MutableSharedFlow()` has `replay = 0`, `extraBufferCapacity = 0`, and `onBufferOverflow = SUSPEND`. Without any buffer capacity, an emission can only be accepted if all subscribers are actively suspended in `collect`. If any subscriber is not immediately ready, `tryEmit()` returns false."
            },
            {
                "interviewer": "How does `StateFlow` configure these three parameters internally?",
                "answer": "`StateFlow` is conceptually configured with `replay = 1`, `extraBufferCapacity = 0`, and `onBufferOverflow = BufferOverflow.DROP_OLDEST`, plus state deduplication via `equals()`."
            },
            {
                "interviewer": "Can the replay cache be cleared dynamically?",
                "answer": "Yes. `MutableSharedFlow.resetReplayCache()` clears all currently stored values from the replay buffer, ensuring future collectors start with an empty cache."
            }
        ]
    },
    {
        "id": "FLO-20",
        "arabic_explanation": (
            "المقارنة بين `Channel` و `SharedFlow` هي الفارق الجوهري بين طوابير المهام الفردية (Work Queues) والبث الجماعي (Broadcasting):\n\n"
            "1. الـ `Channel` (Queue - 1:1 Delivery):\n"
            "   - يعمل كـ **طابور مهام (Queue)** بين المنتجين والمستهلكين.\n"
            "   - **العنصر الواحد يستهلكه مستمع واحد فقط (Single Consumer / Point-to-Point)!** لو عندك مستمعان (Collector A و B)، العنصر الأول سيذهب لـ A، والعنصر الثاني سيذهب لـ B بالتناوب.\n"
            "   - يضمن عدم فقدان الأحداث (No event loss) لو تم استخدام `Channel.BUFFERED`، حيث تنتظر الأحداث في الطابور حتى يأتي مستهلك لقراءتها.\n"
            "   - مثالي جداً لـ: **أحداث الـ Navigation و Side Effects لمرة واحدة (One-off events)**.\n\n"
            "2. الـ `SharedFlow` (Broadcast - 1:N Multicast):\n"
            "   - يعمل كـ **محطة إذاعة وراديو (Broadcast)**.\n"
            "   - **العنصر الواحد يذهب لجميع المستمعين النشطين في نفس الوقت (Fan-out / Multicast)!**\n"
            "   - **خطر فقدان الأحداث (Event Loss Caveat):** لو تم بث حدث ولا يوجد أي مستمع متصل حالياً (وكان `replay = 0`)، **الحدث يضيع في الفضاء للأبد**!\n"
            "   - مثالي جداً لـ: مراقبة أحداث عامة مشتركة، إشعارات التطبيق، أو تحديثات حالة يشترك فيها عدة شاشات."
        ),
        "practical_walkthrough": (
            "مقارنة عملية في التعامل مع حدث الانتقال (Navigation Event):\n"
            "```kotlin\n"
            "// ❌ فخ الـ SharedFlow مع الـ Navigation:\n"
            "val navEvents = MutableSharedFlow<NavRoute>() // replay = 0\n"
            "// إذا ضغط المستخدم الزر أثناء انتقال الشاشة وقبل أن يبدأ Composable الجديد بالاستماع:\n"
            "navEvents.emit(NavRoute.Details) // ضاع الحدث للأبد! لن ينتقل التطبيق!\n"
            "\n"
            "// ✅ الحل باستخدام Channel للأحداث الفردية:\n"
            "private val _navChannel = Channel<NavRoute>(Channel.BUFFERED)\n"
            "val navFlow = _navChannel.receiveAsFlow()\n"
            "\n"
            "fun onNavigateClicked() {\n"
            "    viewModelScope.launch {\n"
            "        _navChannel.send(NavRoute.Details) // ينتظر بأمان في الـ Buffer حتى تفتح الشاشة وتستقبله!\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "A Channel is a point-to-point FIFO queue where each element is consumed by exactly one receiver with zero event loss when buffered; SharedFlow is a broadcast multicaster where every emission fans out to all active subscribers, but drops events if no subscribers are listening when replay is 0.",
        "best_answer": (
            "The architectural distinction between `Channel` and `SharedFlow` lies in communication topology and event delivery guarantees.\n\n"
            "A **Channel** is a point-to-point communication primitive (1-to-1). It models a queue: if multiple collectors read from a Channel, they compete for items, and each item is consumed by exactly one collector. Because it is buffered (`Channel.BUFFERED`), it guarantees zero event loss: an event sent while the UI is rotating or backgrounded waits safely in the queue until the UI recreates and consumes it. This makes Channels ideal for one-off side effects like navigation commands.\n\n"
            "A **SharedFlow** is a broadcast multicaster (1-to-N). Every emitted item is delivered to all active subscribers simultaneously. However, its major caveat is event loss: if an emission occurs when zero collectors are subscribed and `replay = 0`, the event is dropped permanently. It is suited for telemetry and broadcast notifications where dropped transient events are acceptable."
        ),
        "deep_answer": (
            "Under the hood, `Channel` manages an explicit queue of elements and suspended continuations. When `send()` is invoked, if a receiver is waiting in `receive()`, the value is handed off directly between continuations without buffering. "
            "When converting a Channel to a Flow using `receiveAsFlow()`, you get a hot flow backed by that Channel. However, if multiple collectors collect from `receiveAsFlow()`, they will interleave item consumption rather than multicasting.\n\n"
            "In contrast, `SharedFlow` maintains a ring buffer and an array of subscriber slot pointers. Each subscriber tracks its own index in the buffer. "
            "In Android architecture, this distinction dictates our pattern for ViewModel-to-UI communication: "
            "Use **StateFlow** for state (`UiState`); "
            "Use **Channel.receiveAsFlow()** for single-consumption events (`Navigation`, `Toast`); and "
            "Use **SharedFlow** only when multiple independent screens/subscribers must receive the exact same event."
        ),
        "follow_ups": [
            {
                "interviewer": "What happens if a Channel is closed?",
                "answer": "Calling `channel.close()` signals that no more elements will be sent. Any buffered elements are delivered to receivers, and subsequent receive attempts return closed indicators or throw a ClosedReceiveChannelException."
            },
            {
                "interviewer": "Can you consume a Channel from multiple coroutines?",
                "answer": "Yes, this is known as the 'Fan-out' pattern. Multiple worker coroutines can listen to the same Channel, processing tasks concurrently where each task is picked up by the first available worker."
            },
            {
                "interviewer": "Why does Google recommend modeling events as UI State instead of Channels?",
                "answer": "Because modeling events as state (e.g., `data class UiState(val message: Message?)`) keeps everything in a single unidirectional data flow pipeline, is easier to test, and naturally survives process recreation with SavedStateHandle."
            }
        ]
    },
    {
        "id": "FLO-21",
        "arabic_explanation": (
            "الـ `callbackFlow` هو الأداة القياسية في Kotlin لتحويل الـ Multi-shot Callbacks و الـ Listeners المستمرة إلى Reactive Flow:\n\n"
            "1. ما هو `callbackFlow`؟\n"
            "   - هو Flow builder متخصص مصمم لتغليف الـ Callbacks التي تصدر **عدة أحداث عبر الزمن** (مثل: GPS location listener, Bluetooth scan updates, WebSocket events).\n"
            "   - يوفر دالة `trySend(element)` لإرسال البيانات للـ Flow بطريقة Thread-safe وبدون حظر.\n\n"
            "2. ما هي وظيفة `awaitClose` الإلزامية؟\n"
            "   - `awaitClose` هي **أهم سطر كود داخل `callbackFlow`**!\n"
            "   - تقوم بتعليق الـ Flow builder وإبقائه حياً في الذاكرة طالما هناك مستمع يجمع البيانات.\n"
            "   - **تنظيف الـ Listener (Cleanup Block):** تأخذ lambda يتم تنفيذها تلقائياً عندما يتوقف المستمع أو تُلغى الـ Coroutine (مثل إزالة الـ Listener من نظام الأندرويد).\n\n"
            "3. ماذا يحدث لو نسيت `awaitClose`؟\n"
            "   - **كارثة برمجية فورية!** الـ Flow builder سينتهي فوراً ويغلق التدفق في نفس الميلي-ثانية، ولن يستلم المستمع أي تحديثات نهائياً!"
        ),
        "practical_walkthrough": (
            "تحويل Location Listener إلى callbackFlow آمن من التسريب 100%:\n"
            "```kotlin\n"
            "fun FusedLocationProviderClient.locationUpdates(request: LocationRequest): Flow<Location> = callbackFlow {\n"
            "    val callback = object : LocationCallback() {\n"
            "        override fun onLocationResult(result: LocationResult) {\n"
            "            result.lastLocation?.let {\n"
            "                trySend(it) // إرسال الإحداثيات للـ Flow بأمان\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "\n"
            "    // 1. تسجيل الـ Listener:\n"
            "    requestLocationUpdates(request, callback, Looper.getMainLooper())\n"
            "\n"
            "    // 2. awaitClose إلزامية: تعلق الـ coroutine وتفصل الـ Listener عند الإلغاء:\n"
            "    awaitClose {\n"
            "        removeLocationUpdates(callback) // يمنع استنزاف البطارية والـ Memory Leaks!\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "callbackFlow converts multi-event callback APIs into cold Flows using trySend() to emit thread-safely. awaitClose keeps the coroutine active while subscribers exist and executes mandatory cleanup (unregistering listeners) when collection cancels, preventing fatal resource leaks.",
        "best_answer": (
            "`callbackFlow` is the specialized cold flow builder used to bridge legacy, multi-shot callback listeners (like GPS location updates, Bluetooth scanning, or sensor managers) into reactive Kotlin Flows.\n\n"
            "Inside the block, we register the callback listener and use **`trySend(value)`** to emit values thread-safely into the flow channel.\n\n"
            "The critical component is **`awaitClose { ... }`**, which serves two vital purposes:\n\n"
            "1. It suspends the coroutine block, keeping the flow channel open as long as collectors are actively observing.\n"
            "2. It acts as the mandatory cleanup hook: when the downstream collector cancels its coroutine (e.g., the screen is backgrounded or destroyed), `awaitClose` wakes up and executes its lambda, where you must unregister the listener from the Android system service.\n\n"
            "If you omit `awaitClose`, the flow builder executes top-to-bottom and closes immediately, terminating before any callbacks can fire."
        ),
        "deep_answer": (
            "Under the hood, `callbackFlow` is built on top of `channelFlow` with an extra safety invariant: the builder checks that `awaitClose` is explicitly invoked before the block completes. If you attempt to exit a `callbackFlow` without calling `awaitClose`, it throws an `IllegalStateException` at runtime.\n\n"
            "Another critical detail is using `trySend()` versus `send()`: "
            "`trySend()` is non-suspending and thread-safe. Because Android callbacks often trigger on arbitrary Binder IPC or background threads that cannot call suspending functions, `trySend()` allows posting events without launching extra coroutines. "
            "However, if the channel buffer overflows, `trySend().isFailure` will be true. "
            "To prevent dropping sensor or location events, we frequently chain `.buffer(Channel.UNLIMITED)` or `.conflate()` onto the `callbackFlow`."
        ),
        "follow_ups": [
            {
                "interviewer": "Why can't you use `flow { }` instead of `callbackFlow { }` for callbacks?",
                "answer": "Because standard `flow { }` does not allow concurrent or asynchronous calls to `emit()`. Calling `emit()` from inside an asynchronous callback lambda violates Flow's Context Preservation rule and throws an IllegalStateException. `callbackFlow` uses a Channel internally to provide thread-safe emissions."
            },
            {
                "interviewer": "What happens if the callback emits faster than the downstream flow can collect?",
                "answer": "By default, `callbackFlow` uses a buffer size of 64. If the buffer fills, `trySend()` fails and drops emissions unless you configure `.buffer()` or `.conflate()`."
            },
            {
                "interviewer": "Can you use `awaitClose` without a lambda?",
                "answer": "Yes, `awaitClose()` can be called with no arguments just to keep the flow open, but doing so without registering cleanup logic leaks the underlying listener when cancelled."
            }
        ]
    },
    {
        "id": "FLO-22",
        "arabic_explanation": (
            "المقارنة بين `repeatOnLifecycle` و `collectAsStateWithLifecycle` هي جوهر استهلاك البيانات الآمن دورياً (Lifecycle-Safe Collection) في أندرويد:\n\n"
            "1. المشكلة في الجمع التقليدي (`collect` العادي في `lifecycleScope`):\n"
            "   - لو كتبت `lifecycleScope.launch { flow.collect { } }`، الـ Coroutine ستظل تجمع وتستقبل بيانات حتى لو التطبيق في الخلفية (Background) والشاشة غير مرئية!\n"
            "   - هذا يستهلك المعالج والبطارية ويرسل طلبات شبكة ويحدث Views غير مرئية في الخلفية.\n\n"
            "2. دالة `repeatOnLifecycle(Lifecycle.State)` (في XML / Views):\n"
            "   - دالة Suspending تعيد تشغيل الـ Coroutine عندما يصل الـ Lifecycle لحالة معينة (عادة `STARTED`).\n"
            "   - **وتلغي الـ Coroutine تلقائياً فوراً** عندما ينزل الـ Lifecycle تحت تلك الحالة (مثل `STOPPED` عند وضع التطبيق في الخلفية)!\n"
            "   - عند عودة المستخدم للتطبيق، يعاد تشغيل الـ Collection من جديد بنظافة.\n\n"
            "3. دالة `collectAsStateWithLifecycle()` (في Jetpack Compose):\n"
            "   - هي التوأم المخصص لـ Jetpack Compose.\n"
            "   - تستمع للـ Flow بطريقة Lifecycle-aware وتنتج Compose `State<T>`.\n"
            "   - تتوقف عن جمع البيانات تلقائياً عندما تكون الشاشة في الخلفية، وتستأنف عند العودة."
        ),
        "practical_walkthrough": (
            "مقارنة عملية في الكود:\n"
            "```kotlin\n"
            "// 1. في XML Activity / Fragment:\n"
            "override fun onViewCreated(view: View, savedInstanceState: Bundle?) {\n"
            "    super.onViewCreated(view, savedInstanceState)\n"
            "    viewLifecycleOwner.lifecycleScope.launch {\n"
            "        viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {\n"
            "            viewModel.uiState.collect { state ->\n"
            "                renderUi(state)\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. في Jetpack Compose Composable:\n"
            "@Composable\n"
            "fun ProfileScreen(viewModel: ProfileViewModel) {\n"
            "    // توأم repeatOnLifecycle المخصص لـ Compose:\n"
            "    val state by viewModel.uiState.collectAsStateWithLifecycle()\n"
            "    ProfileContent(state)\n"
            "}\n"
            "```"
        ),
        "quick_answer": "repeatOnLifecycle pauses and restarts coroutine collection when an Android Lifecycle enters and exits a specified target state (e.g. STARTED) in View-based code; collectAsStateWithLifecycle is its Jetpack Compose equivalent, converting a Flow into Compose State with automatic background collection pausing.",
        "best_answer": (
            "Both APIs solve the critical problem of **Lifecycle-Safe Flow Collection**, ensuring that backgrounded Android screens stop observing data streams to conserve battery and CPU.\n\n"
            "**`repeatOnLifecycle(Lifecycle.State.STARTED)`** is designed for the View/XML layer (Activities and Fragments). It is a suspending function that launches a collection block when the lifecycle enters `STARTED`. When the user minimizes the app and the lifecycle drops to `STOPPED`, it **cancels the coroutine immediately**. When the user returns to the app, it relaunches the block fresh.\n\n"
            "**`collectAsStateWithLifecycle()`** is the specialized Jetpack Compose equivalent from `androidx.lifecycle.compose`. It collects a Flow in a lifecycle-aware manner (defaulting to `Lifecycle.State.STARTED`) and emits a Compose `State<T>`. When the app goes into the background, it suspends collection, preventing recompositions and stopping upstream cold flows until the screen is visible again."
        ),
        "deep_answer": (
            "Historically, developers used `flowWithLifecycle()`. However, `repeatOnLifecycle` is vastly superior because it can host multiple parallel flow collections inside a single block, avoiding multiple observer allocations:\n\n"
            "```kotlin\n"
            "viewLifecycleOwner.lifecycleScope.launch {\n"
            "    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {\n"
            "        launch { viewModel.feed.collect { ... } }\n"
            "        launch { viewModel.notifications.collect { ... } }\n"
            "    }\n"
            "}\n"
            "```\n\n"
            "In Jetpack Compose, using plain `collectAsState()` is an antipattern because it keeps the flow collection active as long as the composable is part of the composition tree, even when the Activity is paused or stopped in the background. "
            "`collectAsStateWithLifecycle()` internally uses `repeatOnLifecycle` under the hood to unsubscribe from the Flow during backgrounding, which in turn triggers `WhileSubscribed(5000)` in the ViewModel to shut down upstream network and database sensors."
        ),
        "follow_ups": [
            {
                "interviewer": "Why must you use `viewLifecycleOwner` instead of `this` in Fragments?",
                "answer": "Because a Fragment's view lifecycle is destroyed and recreated separately from the Fragment instance itself (e.g., when placed on the backstack). Using `viewLifecycleOwner` ensures flow collection cancels when the view is destroyed, preventing view memory leaks."
            },
            {
                "interviewer": "Why is `Lifecycle.State.STARTED` the recommended state instead of `RESUMED`?",
                "answer": "`STARTED` ensures that the UI updates even when partially visible in multi-window or picture-in-picture mode. `RESUMED` only runs when the window has full user touch focus, which pauses updates in split-screen mode."
            },
            {
                "interviewer": "What dependency is required for `collectAsStateWithLifecycle`?",
                "answer": "It requires the `androidx.lifecycle:lifecycle-runtime-compose` dependency."
            }
        ]
    },
    {
        "id": "FLO-23",
        "arabic_explanation": (
            "ماذا يحدث إذا قامت واجهة المستخدم بجمع تدفقات البيانات إلى ما لا نهاية دون مراعاة دورة الحياة (Without Lifecycle Awareness)؟\n\n"
            "1. استنزاف البطارية وموارد الجهاز في الخلفية (Resource & Battery Drain):\n"
            "   - لو التطبيق وضع في الخلفية (المستخدم ضغط Home button أو قفل الشاشة)، الـ Flow سيظل يطلب بيانات من السيرفر، يقرأ من الـ Database، ويفحص إحداثيات الـ GPS كل ثانية!\n"
            "   - نظام أندرويد يعتبر هذا 'Bad Behavior' ويسجله في Google Play Console كـ Background CPU Spikes مما يخفض تقييم التطبيق.\n\n"
            "2. تسريب الذاكرة (Memory Leaks):\n"
            "   - الـ Collector يحمل مراجع لكائنات الـ UI (Views, Fragments, Composables). بقاء الـ Coroutine نشطة في الخلفية يمنع الـ Garbage Collector من تحرير هذه الكائنات.\n\n"
            "3. انهيار التطبيق (Crashes & Illegal State):\n"
            "   - محاولة تعديل View أو تشغيل Navigation Transaction أثناء وجود الشاشة في حالة `STOPPED` يرمي `IllegalStateException: Can not perform this action after onSaveInstanceState`.\n\n"
            "4. الحل:\n"
            "   - استخدام `repeatOnLifecycle` في الـ Views، و `collectAsStateWithLifecycle()` في Compose."
        ),
        "practical_walkthrough": (
            "تحليل العطل الناتج عن الجمع الخاطئ:\n"
            "```kotlin\n"
            "// ❌ الجمع الكارثي بدون lifecycle awareness:\n"
            "lifecycleScope.launch {\n"
            "    viewModel.locationFlow.collect { location ->\n"
            "        // عندما يكون التطبيق في الخلفية، الـ GPS يعمل بأقصى طاقة ويسحب البطارية!\n"
            "        // وإذا حاول تنفيذ navigation هنا:\n"
            "        findNavController().navigate(R.id.action_next) // CRASH: IllegalStateException!\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ الجمع الآمن دورياً:\n"
            "viewLifecycleOwner.lifecycleScope.launch {\n"
            "    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {\n"
            "        viewModel.locationFlow.collect { location ->\n"
            "            updateMapPin(location) // يتوقف تماماً عند الخروج للـ Background!\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Collecting without lifecycle awareness continues active flow processing in the background, causing severe battery drain, continuous CPU/network usage, potential memory leaks from retained view references, and fatal runtime crashes like IllegalStateException when attempting navigation while the activity is stopped.",
        "best_answer": (
            "Collecting flows indefinitely without lifecycle awareness (such as launching directly in `lifecycleScope.launch` without `repeatOnLifecycle`, or using plain `collectAsState()` in Compose) leads to three severe production defects:\n\n"
            "1. **Severe Battery and Network Drain:** If the flow is connected to an upstream sensor, location updates, WebSocket, or polling repository, collection remains completely active even when the phone is locked in a user's pocket. Google Play Console will flag the app for excessive background execution and wake-locks.\n\n"
            "2. **Memory Leaks:** The active coroutine retains references to the View or Composable in its closure. If the user navigates between screens, destroyed views cannot be garbage-collected as long as the background collection coroutine is alive.\n\n"
            "3. **IllegalState Crashes:** When an emission arrives while the app is in the background, attempting to trigger fragment navigation or show dialogs throws `IllegalStateException: Can not perform this action after onSaveInstanceState`.\n\n"
            "Enforcing `repeatOnLifecycle(STARTED)` or `collectAsStateWithLifecycle()` eliminates all these issues by pausing collection the moment the UI leaves the foreground."
        ),
        "deep_answer": (
            "At the systems level, Android's OS kernel prioritizes foreground processes (OOM adj 0) and demotes background apps down the OOM adj score list. "
            "If a background app continuously spins CPU threads or makes network sockets because of an unpaused Flow collection, Android's system watchdog detects high battery consumption via Batterystats and issues a warning in Android Vitals.\n\n"
            "Furthermore, pairing lifecycle-aware collectors with `WhileSubscribed(5000)` in the ViewModel creates an end-to-end reactive circuit: "
            "When `repeatOnLifecycle` cancels the collector upon entering `STOPPED`, the ViewModel's `StateFlow.subscriptionCount` drops to 0. "
            "After 5 seconds, the ViewModel shuts down upstream Room or Network observations, freeing SQLite cursor locks and closing network sockets at the operating system level."
        ),
        "follow_ups": [
            {
                "interviewer": "Why did `lifecycleScope.launchWhenStarted` get deprecated?",
                "answer": "`launchWhenStarted` only paused execution; it did NOT cancel the coroutine. The upstream flow continued emitting items in the background, buffering them in memory until the app resumed, which still wasted CPU, network bandwidth, and memory."
            },
            {
                "interviewer": "How does `repeatOnLifecycle` differ from `launchWhenStarted`?",
                "answer": "`repeatOnLifecycle` actively cancels the collection coroutine when leaving the target state and relaunches a fresh coroutine when re-entering, allowing upstream flows to clean up and shut down completely."
            },
            {
                "interviewer": "Can a background worker still collect flows safely?",
                "answer": "Yes, in a background Service or WorkManager task, flow collection is governed by the worker's own CoroutineScope, which terminates when the background work completes."
            }
        ]
    },
    {
        "id": "FLO-24",
        "arabic_explanation": (
            "اختبار الـ Flow و StateFlow باستخدام `runTest` ومكتبة **Turbine** من CashApp هو المعيار الذهبي المعتمد عالمياً في اختبارات Kotlin:\n\n"
            "1. المشكلة في اختبار الـ Flows بدون Turbine:\n"
            "   - الـ Flow هو Asynchronous Stream. لو حاولت كتابة `flow.collect()` داخل الـ Test، الـ `collect()` دالة معلقة لا تنتهي أبداً، والاختبار سيتعلق ويتجمد!\n"
            "   - ولو حاولت استخدام `toList()`، سيتعلق للأبد أيضاً لو كان الـ Flow لا نهائياً (زي StateFlow).\n\n"
            "2. لماذا مكتبة Turbine هي الأفضل؟\n"
            "   - توفر دالة `flow.test { ... }`.\n"
            "   - تسمح لك باستهلاك العناصر عنصراً بعنصر بشكل متزامن وحتمي:\n"
            "     * `awaitItem()`: تنتظر وتسترجع العنصر التالي وتتحقق من قيمته.\n"
            "     * `awaitComplete()`: تتحقق من انتهاء التدفق بنجاح.\n"
            "     * `awaitError()`: تتحقق من رمي الاستثناء المتوقع.\n"
            "     * `expectNoEvents()`: تتأكد من عدم وجود أي انبعاثات جديدة.\n\n"
            "3. التكامل مع `runTest`:\n"
            "   - `runTest` تسرع الوقت الافتراضي وتتحكم في الـ `StandardTestDispatcher` لضمان اختبارات سريعة ومستقرة 100% بدون أي Flakiness."
        ),
        "practical_walkthrough": (
            "كتابة Unit Test كامل لاختبار ViewModel StateFlow باستخدام Turbine:\n"
            "```kotlin\n"
            "@Test\n"
            "fun `searchQuery updates uiState from Loading to Success`() = runTest {\n"
            "    val fakeRepo = FakeRepository()\n"
            "    val viewModel = SearchViewModel(fakeRepo)\n"
            "\n"
            "    // نختبر تدفق الـ StateFlow باستخدام Turbine:\n"
            "    viewModel.uiState.test {\n"
            "        // 1. أول عنصر يجب أن يكون القيمة الابتدائية Loading:\n"
            "        assertEquals(SearchUiState.Loading, awaitItem())\n"
            "\n"
            "        // 2. تفعيل البحث:\n"
            "        viewModel.onSearchQueryChanged(\"Kotlin\")\n"
            "\n"
            "        // 3. ننتظر العنصر الثاني ونتحقق من نتائج البحث:\n"
            "        val successItem = awaitItem()\n"
            "        assertTrue(successItem is SearchUiState.Success)\n"
            "        assertEquals(\"Kotlin\", (successItem as SearchUiState.Success).query)\n"
            "\n"
            "        // 4. نلغي المراقبة بأمان:\n"
            "        cancelAndIgnoreRemainingEvents()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Test flows deterministically using runTest paired with CashApp's Turbine library. Turbine's flow.test { } provides awaitItem(), awaitComplete(), and expectNoEvents() to assert on emissions sequentially without hanging on infinite streams like StateFlow.",
        "best_answer": (
            "Testing Kotlin Flows deterministically requires pairing `kotlinx-coroutines-test` (`runTest`) with Cash App's **Turbine** library.\n\n"
            "Standard assertions fail on flows because terminal operators like `collect()` or `toList()` suspend indefinitely on infinite streams like `StateFlow`. Turbine solves this by providing the `flow.test { }` extension.\n\n"
            "Inside the `test` block, Turbine exposes a sequential event-driven API:\n\n"
            "1. **`awaitItem()`**: Suspends until the next emission arrives and returns it for assertion.\n"
            "2. **`awaitComplete()`**: Asserts that the stream completed normally.\n"
            "3. **`awaitError()`**: Asserts that the stream terminated with an expected exception.\n"
            "4. **`expectNoEvents()`**: Verifies that no unexpected emissions occurred within the virtual time window.\n"
            "5. **`cancelAndIgnoreRemainingEvents()`**: Cleans up subscriptions on infinite flows like StateFlow so tests finish without uncompleted coroutine errors."
        ),
        "deep_answer": (
            "Under the hood, Turbine wraps the flow inside an internal Channel that records emitted items, completion signals, and exceptions as typed `Event<T>` instances. "
            "Because it operates inside `runTest`, delays in operators like `debounce` or `WhileSubscribed` do not require real-time sleep: `testScheduler.advanceTimeBy()` triggers delayed emissions instantaneously.\n\n"
            "When testing `StateFlow` created via `stateIn(viewModelScope, WhileSubscribed(5000), Initial)`: "
            "1. Calling `stateFlow.test { }` subscribes to the flow, advancing `subscriptionCount` from 0 to 1 and triggering the upstream flow. "
            "2. The first `awaitItem()` immediately yields the `initialValue`. "
            "3. Advancing virtual time or completing fake repository coroutines triggers subsequent `awaitItem()` yields. "
            "4. Finally, calling `cancelAndConsumeRemainingEvents()` drops `subscriptionCount` back to 0, ensuring full lifecycle test coverage."
        ),
        "follow_ups": [
            {
                "interviewer": "Why does calling `stateFlow.toList()` cause a unit test to hang indefinitely?",
                "answer": "Because `toList()` collects until the flow terminates. `StateFlow` is an infinite stream that never completes on its own, so `toList()` will suspend forever until the test framework times out."
            },
            {
                "interviewer": "What is `turbineScope { }`?",
                "answer": "`turbineScope` allows testing multiple flows concurrently within the same test block (e.g., verifying that emitting on one flow triggers an expected update on another flow)."
            },
            {
                "interviewer": "How do you test a debounced flow with Turbine?",
                "answer": "Call `flow.test { ... }`, emit a query, assert with `expectNoEvents()`, call `advanceTimeBy(300L)`, and then assert the debounced query using `awaitItem()`."
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

    for q in FLO_19_24:
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
    print(f"Updated {DATA_FILE} with questions FLO-19 to FLO-24. Total questions: {len(combined)}")


if __name__ == "__main__":
    main()

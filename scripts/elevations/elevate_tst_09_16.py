#!/usr/bin/env python3
"""Elevate TST-09 to TST-16: Software Testing, Quality & Reliability (Batch 2)."""
import os
import sys
from pathlib import Path

# Insert elevations directory to import elevation_engine
ROOT = Path("/Volumes/M&M/Android/InterView/untitled folder/android quation")
sys.path.insert(0, str(ROOT / "scripts" / "elevations"))
import elevation_engine as ee

TOPIC_CODE = "TST"
TOPIC_AR = ee.TOPIC_AR_NAMES[TOPIC_CODE]
REVIEWED_DATE_AR = "تمت المراجعة والتدقيق الهندسي في 17 أكتوبر 2026."

DATA = {}

# ==========================================
# TST-09: How do you test Flow, StateFlow, and SharedFlow with Turbine?
# ==========================================
DATA["TST-09"] = {
    "concept_en": """Testing Kotlin asynchronous reactive streams—cold Flow, StateFlow, and SharedFlow—requires tailored testing strategies driven by stream lifecycle and subscription semantics. Cold flows instantiate builders and execute emission pipelines on-demand whenever collected, allowing deterministic sequential assertions terminating in completion. StateFlow is a hot, conflated stream with replay of one that never completes naturally; it always holds an active initial value and skips rapid intermediate state mutations if new values arrive before the consumer reads the slot. SharedFlow is a configurable broadcast stream where emissions occurring prior to collector initialization are permanently dropped unless explicitly buffered via replay. CashApp's Turbine library provides a testing harness that connects a rendezvous channel to the stream, exposing synchronous assertion primitives like awaitItem(), expectNoEvents(), awaitComplete(), and awaitError().""",
    "walkthrough_en": """Testing cold Flows, StateFlow, and SharedFlow sequentially using Turbine:
```kotlin
class StreamTestingDemo {
    // 1. Cold Flow: Starts on collection and finishes with completion
    @Test
    fun coldFlow_emitsSequence_andCompletes() = runTest {
        val coldFlow = flow {
            emit("First")
            emit("Second")
        }

        coldFlow.test {
            assertEquals("First", awaitItem())
            assertEquals("Second", awaitItem())
            awaitComplete()
        }
    }

    // 2. StateFlow: Always yields initial state; never completes naturally
    @Test
    fun stateFlow_emitsInitialState_andUpdates() = runTest {
        val stateFlow = MutableStateFlow("Initial")

        stateFlow.test {
            assertEquals("Initial", awaitItem()) // Guaranteed initial value

            stateFlow.value = "Updated"
            assertEquals("Updated", awaitItem())

            cancelAndIgnoreRemainingEvents() // Must cancel hot infinite collector!
        }
    }

    // 3. SharedFlow: Subscription must be established BEFORE emitting!
    @Test
    fun sharedFlow_collectsEvents_whenSubscribedPriorToEmission() = runTest {
        val sharedFlow = MutableSharedFlow<String>()

        sharedFlow.test {
            // Collector is now active! Emit event:
            sharedFlow.emit("Alert")
            assertEquals("Alert", awaitItem())

            expectNoEvents()
            cancelAndIgnoreRemainingEvents()
        }
    }
}
```""",
    "short_en": """We test reactive streams using Turbine by opening a test collector channel. Cold flows emit on collection and terminate with awaitComplete. StateFlow is hot and conflated, so its initial value is received immediately via awaitItem, requiring cancelAndIgnoreRemainingEvents to avoid hanging. SharedFlow drops unbuffered emissions, so the Turbine test block must be opened before emitting events. Turbine catches unhandled stream exceptions and prevents test deadlocks synchronously.""",
    "structured_en": """Testing asynchronous Kotlin flows reliably requires navigating the profound behavioral differences between cold and hot streams.
Standard collection approaches—such as calling toList() on a stream—frequently cause infinite test hangs because StateFlow and SharedFlow are hot streams that never complete.
CashApp's Turbine library solves this by providing a lightweight, structured testing scope.
When testing cold flows, Turbine initiates collection upon entering the test block.
Because cold flows follow structured completion, the test asserts items sequentially using awaitItem() and terminates with awaitComplete().
When testing StateFlow, developers must account for its hot, conflated nature.
Entering the test block immediately yields StateFlow's current value as the first item.
Subsequent state updates emitted by ViewModels are asserted sequentially, but because StateFlow never completes, the test block must conclude with cancelAndIgnoreRemainingEvents() to unregister the observer cleanly.
When testing SharedFlow, timing is paramount.
Because SharedFlow drops emissions when there are zero active subscribers unless replay is configured, the Turbine test block must be launched prior to calling emit().
Turbine provides expectNoEvents() to verify that quiescent streams do not leak phantom updates.""",
    "deep_senior_en": """Under the hood, Turbine connects to Kotlin Coroutines by establishing a bridge between the Flow collector pipeline and an internal Channel.
When flow.test { ... } is invoked, Turbine launches an asynchronous consumer coroutine that invokes collect on the target Flow, routing every incoming value into an unbuffered rendezvous Channel.
When the test author invokes awaitItem(), Turbine suspends the test thread until the consumer coroutine offers an element into the channel, popping the value in O(1) time without thread sleeps.
If an unexpected exception is thrown inside the flow builder, Turbine catches the failure, surfaces it via awaitError(), and halts execution with a detailed failure diff.
Understanding stream mechanics separates junior tests from senior harnesses.
With StateFlow, rapid successive emissions can be conflated by the runtime; if the ViewModel executes _state.value = A followed immediately by _state.value = B within the same execution frame, StateFlow overwrites its internal state slot, and Turbine will only observe state B unless intermediate suspensions occur.
With SharedFlow, the buffer overflow policy dictates behavior.
If extraBufferCapacity is zero and BufferOverflow.SUSPEND is active, calling emit() from outside a coroutine can suspend indefinitely if no collector exists.
Turbine eliminates these hazards by ensuring the collector's Job is child-linked to the test's CoroutineScope, guaranteeing that canceling the test harness synchronously disposes of all underlying hot stream subscriptions without leaking coroutines on CI workers.""",
    "meta_ar": {
        "id": "TST-09",
        "questionAr": "كيف تختبر الـ Flow و StateFlow و SharedFlow باحترافية باستخدام مكتبة Turbine؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على اختبار التدفقات التفاعلية (Reactive Streams) في كوتلن، وفهم الفارق بين Cold Flows و Hot Flows (StateFlow و SharedFlow)، والتحكم في دورة حياة المستمع وتجنب الـ Deadlocks بـ Turbine.",
        "why_it_matters_ar": "استخدام `toList()` أو الجمع المباشر مع StateFlow يسبب تعليق الاختبار للأبد (Hanging) لأن التدفقات الساخنة لا تنتهي، بينما إطلاق الانبعاثات قبل الاشتراك في SharedFlow يؤدي لفقدان الأحداث وفشل الاختبار عشوائياً.",
        "worked_example_ar": "اختبار التدفقات الثلاثة بمكتبة Turbine:\n```kotlin\n// 1. Cold Flow ينتهي بـ awaitComplete\nflowOf(1, 2).test { assertEquals(1, awaitItem()); assertEquals(2, awaitItem()); awaitComplete() }\n// 2. StateFlow تدفق ساخن يبدأ بقيمة ابتدائية ويلزم إلغاؤه في النهاية\nstateFlow.test { assertEquals(\"Init\", awaitItem()); stateFlow.value = \"New\"; assertEquals(\"New\", awaitItem()); cancelAndIgnoreRemainingEvents() }\n```",
        "trade_offs_ar": "استخدام Turbine يتطلب إضافة مكتبة خارجية لكود الاختبار، لكنه البديل الآمن الوحيد لتفادي الـ Deadlocks ومراقبة تسلسل الحالات بدقة متناهية.",
        "failure_modes_ar": "إطلاق الأحداث في SharedFlow قبل فتح بلوك `sharedFlow.test`، مما يؤدي لسقوط الحدث لأن SharedFlow معندوش Replay افتراضياً، فيفشل التيست بانتظار حدث لن يصل.",
        "production_perspective_ar": "في المشروعات الكبيرة، نعتمد Turbine كمعيار إلزامي لاختبار كل الـ ViewModels التي تعرض StateFlow أو تطلق أحداث One-off عبر SharedFlow.",
        "how_to_answer_ar": "قارن بين نوعي التدفقات: Cold Flow يبدأ مع الجمع وينتهي بـ `awaitComplete()`، و StateFlow ساخن ومدمج (Conflated) يبدأ بالقيمة الحالية فوراً ولا ينتهي فيلزم إنهاؤه بـ `cancelAndIgnoreRemainingEvents()`، و SharedFlow يسقط البيانات لو لم يكن هناك مشترك فيلزم فتح بلوك `test` قبله، واشرح كيف تمنع Turbine الـ Deadlocks.",
        "talking_points_ar": "الفارق بين Cold و Hot Flows، وقناة الـ Channel الداخلية في Turbine، ودوال awaitItem و awaitComplete و cancelAndIgnoreRemainingEvents، ومفهوم الـ Conflation في StateFlow، وتوقيت الاشتراك في SharedFlow.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يسبب استدعاء `flow.toList()` تعليق الاختبار (Deadlock) مع StateFlow؟\"\n  **المرشح:** \"لأن StateFlow تدفق ساخن ملوش نهاية طبيعية؛ فـ `toList()` هتفضل مستنية التدفق يقفل عشان ترجع القائمة، وده مش هيحصل أبداً. Turbine بتحل ده بإنها بتفحص كل عنصر لوحده بـ `awaitItem()`.\"\n\n- **المحاور:** \"ماذا يحدث لو قمت بتحديث StateFlow مرتين وراء بعض بسرعة في نفس الفريم؟\"\n  **المرشح:** \"خاصية الـ Conflation هتخلي StateFlow يحتفظ بآخر قيمة فقط ويسقط القيمة الأولى، فـ Turbine هتشوف القيمة التانية فقط، إلا لو كان فيه تعليق حقيقي سمح بجمع القيمة الأولى.\"",
        "self_check_ar": "هل وضحت الفارق بين اختبار Cold Flow و Hot Flow؟ هل شرحت أسلوب التعامل مع StateFlow و SharedFlow؟ وهل بينت آلية عمل Turbine الداخلية؟",
        "references_ar": f"- [CashApp Turbine](https://github.com/cashapp/turbine) — التوثيق الرسمي لمكتبة Turbine لاختبار التدفقات.\n- [Testing Kotlin Flows](https://developer.android.com/kotlin/flow/test) — دليل مطوري أندرويد لاختبار الـ Flows.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنختبر الـ Flows باحترافية باستخدام مكتبة `Turbine` عبر فتح قناة فحص مخصصة ببلوك `.test { ... }`. في الـ `Cold Flow` العادي، التدفق بيبدأ مع الجمع وبيصدر قيمه بالترتيب وينتهي بـ `awaitComplete()`. في الـ `StateFlow`، لأنه تدفق ساخن لا نهائي (Hot Stream)، بنستلم القيمة الابتدائية فوراً بـ `awaitItem()`، ومع كل تحديث بنستقبل الحالة الجديدة، ولازم ننهي الاختبار بـ `cancelAndIgnoreRemainingEvents()` لمنع تعليق التيست. أما في الـ `SharedFlow`، فلازم نفتح بلوك الـ `test` قبل إطلاق الحدث عشان نضمن وجود مشترك وميسقطش الحدث في الهواء.",
        "best_answer_ar": "اختبار الـ Flows بيعتبر اختباراً حقيقياً لمدى فهم المهندس لطبيعة التدفقات الباردة والساخنة في كوتلن كوروتينز.\n\nاستخدام الطرق التقليدية زي `toList()` مع الـ ViewModels الحديثة بيعتبر خطأ قاتل؛ لأن `StateFlow` و `SharedFlow` هي تدفقات ساخنة مستمرة للأبد، فـ `toList()` هتخلي التيست يعلق في Deadlock للأبد مستني التدفق يقفل!\n\nمكتبة `Turbine` بتحل المعضلة دي بذكاء، وبنتعامل مع كل تدفق حسب خصائصه:\nأولاً: الـ `Cold Flow`؛ ده بيشتغل عند الطلب فقط؛ بنفتح `flow.test { ... }` وننادي `awaitItem()` لكل عنصر، وفي الآخر بنستدعي `awaitComplete()` عشان نتأكد إن التدفق أغلق بنجاح وبدون استثناءات.\n\nثانياً: الـ `StateFlow`؛ ده تدفق مدمج وساخن (Hot and Conflated) بيحتفظ بآخر قيمة. أول ما بتفتح البلوك بتاعه بـ Turbine، بيوصلك فوراً أول `awaitItem()` بالقيمة الابتدائية. لما تستدعي دالة في الـ ViewModel تحدث الحالة، بتنادي `awaitItem()` عشان تفحص الحالة الجديدة، وقبل ما تخرج من البلوك لازم تنادي `cancelAndIgnoreRemainingEvents()` عشان تقفل الكوروتين المستمع وميحصلش تسريب.\n\nثالثاً: الـ `SharedFlow`؛ ده بيبث أحداث لحظية (One-off Events) ومبيحتفظش بقيمة لو الـ Replay بصفر. هنا الترتيب حاسم؛ لازم تفتح `sharedFlow.test` الأول عشان يكون فيه مشترك نشط، وبعدين تطلق دالة الإنتاج، وتستقبل الحدث بـ `awaitItem()`، وتقدر تتأكد بـ `expectNoEvents()` إن مفيش أحداث وهمية تسربت.",
        "deep_answer_ar": "تحت الكابوت، مكتبة Turbine بتعمل جسر ذكي جداً بين معمارية الـ Flow ونظام قنوات الكوروتينات (Kotlin Channels).\nأول ما بتنادي `flow.test { ... }`، المكتبة بتطلق كوروتين خفي في الخلفية وظيفته عمل `collect` للـ Flow وتمرير كل عنصر بيوصل لقناة تزامنية من نوع `Rendezvous Channel`.\n\nلما كود الاختبار بينادي `awaitItem()`، خيط الفحص بيتعلق مؤقتاً لحد ما القناة تستقبل عنصر من الكوروتين التاني، فبيتم سحبه فوراً في زمن O(1) وبدون أي نوم للخيط الحقيقي (No Thread.sleep).\nولو الـ Flow رمى استثناء، Turbine بتلتقطه وتلغي القناة وتسمح لك تفحصه بـ `awaitError()` وتطلع تقرير تفصيلي يكشف الخطأ.\n\nوفي كود الإنتاج، المهندس السينيور بياخد باله من خاصية الـ Conflation في `StateFlow`؛ لو الـ ViewModel غير الحالة مرتين متتاليتين بسرعة فائقة في نفس الفريم قبل ما خيط التيست يستهلك القيمة الأولى، محرك `StateFlow` بيستبدل القيمة الأولى بالتانية في الـ Slot الداخلي، فـ Turbine هتشوف القيمة التانية فقط ومش هتشوف الأولى، وده سلوك طبيعي للنظام.\nوعلى جانب `SharedFlow`، لو أطلقت الحدث قبل ما قناة Turbine تتصل، الحدث بيضيع تماماً في الذاكرة لأن `extraBufferCapacity` الافتراضي بصفر.\nعشان كده، التنسيق الصارم لدورة حياة الـ Test Collector بـ Turbine بيضمن اختبارات خالية تماماً من الـ Flakiness في بيئات الـ CI الكبرى."
    }
}

# ==========================================
# TST-10: How do you test cancellation, error, retry, timeout, and backoff?
# ==========================================
DATA["TST-10"] = {
    "concept_en": """Testing coroutine cancellation, error propagation, retries, timeouts, and exponential backoff requires strict deterministic control over virtual time and failure injection. Cancellation in Kotlin is cooperative and mediated by CancellationException; tests verify that parent scopes cancel child jobs cleanly without propagating failure upward or leaking unclosed resources. Error testing validates that domain exceptions are caught, logged, or mapped to typed Result failures rather than crashing the hosting scope. Retry and exponential backoff algorithms are tested by combining fake network endpoints that simulate transient failures with runTest's TestScope, advancing virtual time via advanceTimeBy() to assert that retry attempts execute at precise exponential delay intervals without real-world latency. Timeouts are verified using withTimeout or withTimeoutOrNull to ensure operations abort cleanly when deadlines expire.""",
    "walkthrough_en": """Testing retry with exponential backoff and cancellation using virtual time:
```kotlin
class RetryBackoffTest {
    // Fake client failing twice with IOException before succeeding
    class FlakyApiClient {
        var attempts = 0
        suspend fun fetchData(): String {
            attempts++
            if (attempts <= 2) throw IOException("Transient server blip")
            return "Success"
        }
    }

    suspend fun fetchWithBackoff(client: FlakyApiClient): String {
        var currentDelay = 1000L
        repeat(3) {
            try {
                return client.fetchData()
            } catch (e: IOException) {
                delay(currentDelay)
                currentDelay *= 2 // Exponential backoff: 1000ms -> 2000ms
            }
        }
        return client.fetchData()
    }

    @Test
    fun retryWithBackoff_retriesAtExactVirtualTimeIntervals() = runTest {
        val client = FlakyApiClient()
        val job = launch { fetchWithBackoff(client) }

        // Attempt 1 fails immediately at T = 0ms; schedules delay(1000)
        runCurrent()
        assertEquals(1, client.attempts)

        // Advance past first backoff interval (1000ms)
        advanceTimeBy(1001)
        // Attempt 2 fails; schedules delay(2000)
        assertEquals(2, client.attempts)

        // Advance past second backoff interval (2000ms)
        advanceTimeBy(2001)
        // Attempt 3 succeeds!
        assertEquals(3, client.attempts)

        job.join()
    }
}
```""",
    "short_en": """We test cancellation, errors, and backoff deterministically using runTest. Cancellation is tested by canceling jobs and asserting that CancellationException is respected without leaking tasks. Errors are tested by injecting mock exceptions and verifying domain Result mapping. Retries with exponential backoff are tested by advancing virtual time with advanceTimeBy, asserting that retry attempts execute at exact mathematical delay intervals without sleeping real threads.""",
    "structured_en": """Validating asynchronous error resilience and lifecycle cancellation is essential for mission-critical enterprise Android applications.
Testing cancellation requires verifying coroutine cooperative behavior.
When a test cancels a parent Job via job.cancel(), it must assert that active child coroutines abort promptly, release locks, and unregister listeners without bubbling up as fatal test exceptions, since CancellationException is a normal completion signal in coroutines.
Testing error handling focuses on exception boundaries.
By injecting fake data sources that throw custom domain or network exceptions, tests verify that repositories catch low-level throwables and encapsulate them into sealed Result.Failure models rather than permitting uncaught exceptions to crash the application.
Testing retries, timeouts, and exponential backoff algorithms relies entirely on the virtual time capabilities of runTest.
When an operation fails with a transient error and initiates exponential backoff (such as waiting one second, then two seconds, then four seconds), tests do not block execution with thread sleeps.
Instead, developers query invocation counters at exact points along the virtual timeline using advanceTimeBy(millis).
The test asserts that the retry occurs only after the designated backoff interval elapses, verifying that retry budgets are respected and that non-retryable 4xx client errors abort immediately without wasteful retransmissions.""",
    "deep_senior_en": """Under the hood, testing cancellation and backoff exposes the delicate interaction between Kotlin's Continuation state machine and TestCoroutineScheduler.
When testing cancellation, senior engineers strictly verify that business code does not catch CancellationException under a broad catch (e: Exception) clause.
Swallowing CancellationException prevents the coroutine runtime from transitioning the Job into the Cancelling state, causing jobs to hang and leaking background threads.
In unit tests, if a coroutine swallows cancellation, runTest detects the leaked active child upon completion and throws an UncompletedCoroutinesError.
When testing exponential backoff, the algorithm schedules delayed resumptions by invoking delay(currentDelay).
Under runTest, the TestDispatcher enqueues these resumptions into the scheduler's Min-Heap queue.
When advanceTimeBy(millis) is called, the scheduler advances its currentTime property and dispatches all scheduled continuations whose trigger timestamp has arrived.
This allows tests to verify intricate backoff formulas—including full jitter calculations—by asserting invocation timestamps down to the exact millisecond.
When testing timeouts via withTimeout(duration), the coroutine library schedules a TimeoutCancellationException on the scheduler.
If the monitored task completes before the virtual clock reaches the duration, the timeout task is cancelled from the queue.
If the virtual clock reaches the timeout threshold, the scheduler throws the timeout exception, unwinding the stack and canceling child operations cleanly.
This ensures that long-running operations fail gracefully in milliseconds without requiring flaky wall-clock timeouts on CI runners.""",
    "meta_ar": {
        "id": "TST-10",
        "questionAr": "كيف تختبر الإلغاء (Cancellation) والخطأ وإعادة المحاولة (Retry) والمهلة (Timeout) والـ Backoff باحترافية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على اختبار آليات المرونة والتعافي في الكوروتينات، والتحقق من صحة الإلغاء التعاوني (Cooperative Cancellation)، واختبار خوارزميات الـ Exponential Backoff بالوقت الافتراضي بدون أي انتظار حقيقي.",
        "why_it_matters_ar": "ابتلاع استثناء `CancellationException` في كود الإنتاج يكسر التزامن المعماري ويسرب العمليات الخلفية، واختبار خوارزميات إعادة المحاولة بانتظار حقيقي يجعل الـ CI بطيئاً جداً وغير مستقر.",
        "worked_example_ar": "اختبار إعادة المحاولة بـ Exponential Backoff بالوقت الافتراضي:\n```kotlin\n@Test fun testBackoff() = runTest {\n    val job = launch { retryWithBackoff() } // محاولة كل 1000ms ثم 2000ms\n    runCurrent(); assertEquals(1, attempts)\n    advanceTimeBy(1001); assertEquals(2, attempts)\n    advanceTimeBy(2001); assertEquals(3, attempts)\n    job.join()\n}\n```",
        "trade_offs_ar": "اختبار خوارزميات الـ Backoff بالوقت الافتراضي يتطلب حسابات دقيقة للميلي ثانية، لكنه يوفر أقصى ثقة برمجية بدون إبطاء خطوط الـ CI ولو لثانية واحدة.",
        "failure_modes_ar": "كتابة `catch (e: Exception)` بدون إعادة رمي `CancellationException`، مما يمنع الكوروتين من الإلغاء ويجعل `runTest` تفشل بـ `UncompletedCoroutinesError`.",
        "production_perspective_ar": "في المشروعات الكبيرة، نلزم تغطية كل دوال الدفع والشبكة باختبارات ترقية المحاولات (Retry Budget) والتأكد من توقف المحاولات فوراً مع أخطاء 4xx مثل 401 Unauthorized.",
        "how_to_answer_ar": "وضح معالجة المحاور الخمسة: الإلغاء بالتأكد من عدم ابتلاع `CancellationException`، والأخطاء بحقن استثناءات وفحص تغليفها في Result، وإعادة المحاولة والـ Backoff بتقديم الوقت الافتراضي بـ `advanceTimeBy` لفحص المواعيد بالمللي ثانية، والـ Timeout بفحص إلغاء المهمة مع `withTimeout`.",
        "talking_points_ar": "الإلغاء التعاوني و CancellationException، ومصيدة ابتلاع الاستثناء بـ catch Exception، واختبار الـ Exponential Backoff بـ advanceTimeBy، واختبار الـ Timeouts بـ withTimeout، وحدود محاولات الـ Retry.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يعتبر ابتلاع `CancellationException` داخل دالة الشبكة خطأ كارثياً؟\"\n  **المرشح:** \"لأن الكوروتينات بتعتمد على الاستثناء ده عشان تنفذ الإلغاء؛ فلو الكود عمل له catch واعتبره خطأ عادي، الكوروتين هيفضل شغال ومش هيقف لما المستخدم يقفل الشاشة، وده بيسرب موارد وذاكرة.\"\n\n- **المحاور:** \"كيف تختبر خوارزمية Exponential Backoff تنتظر 1 ثانية ثم 2 ثم 4 بدون إبطاء التيست؟\"\n  **المرشح:** \"عبر دالة `runTest`؛ بنستخدم `advanceTimeBy(1001)` لفحص المحاولة التانية، ثم `advanceTimeBy(2001)` للثالثة، وبكده بنختبر 7 ثواني كاملة في أقل من جزء من الميلي ثانية على المعالج.\"",
        "self_check_ar": "هل شرحت كيفية اختبار الإلغاء بدقة؟ هل بينت خطورة ابتلاع CancellationException؟ وهل وضحت اختبار الـ Backoff بالوقت الافتراضي؟",
        "references_ar": f"- [Coroutines Cancellation and Exceptions](https://kotlinlang.org/docs/cancellation-and-exceptions.html) — الدليل الرسمي لجيت برينز لإدارة الإلغاء والاستثناءات.\n- [Testing Coroutines Exception Handling](https://developer.android.com/kotlin/coroutines/test) — دليل جوجل لاختبار استثناءات الكوروتينات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنختبر الإلغاء والأخطاء والـ Backoff بدقة قطعية وسرعة فائقة باستخدام بيئة `runTest`. في الإلغاء (Cancellation)، بنلغي الـ Job ونتأكد إن المهام الفرعية توقفت فوراً بدون تسريب استثناءات قاتلة وبدون ابتلاع كائن `CancellationException`. في الأخطاء، بنحقن استثناءات في الـ Fake sources ونتأكد إن الـ Repository بيغلفها في كائن `Result.failure` آمن. وفي إعادة المحاولة (Retry) والـ Exponential Backoff، بنستغل الوقت الافتراضي؛ بنقدم الساعة بـ `advanceTimeBy()` بالمللي ثانية المحددة (زي 1000ms ثم 2000ms) ونتأكد إن المحاولات بتتنفذ في توقيتها المحسوب بالضبط بدون أي نوم حقيقي للخيط.",
        "best_answer_ar": "اختبار سيناريوهات الفشل والإلغاء وإعادة المحاولة بيكشف عمق تمكن المهندس من آليات الكوروتينات وإدارة الشبكة في أندرويد.\n\nالخطة الاحترافية بتغطي الأركان دي بتناغم:\nأولاً: اختبار الإلغاء (Cancellation)؛ الكوروتينات بتعتمد على الإلغاء التعاوني عبر `CancellationException`. بنختبر إن استدعاء `job.cancel()` بيوقف العملية فوراً وينظف الموارد. أكبر خطأ بنفحصه هنا هو التأكد إن كود المطور مبيبتلعش `CancellationException` داخل بلوك `catch (e: Exception)` عام؛ لأن ابتلاعه بيكسر هيكل التزامن وبيخلي الكوروتين يفضل شغال في الخلفية ويسرب الذاكرة.\n\nثانياً: اختبار الأخطاء (Error Handling)؛ بنحقن أخطاء شبكة أو استثناءات مخصصة، ونتأكد إن طبقة البيانات بتلتقطها وتحولها لحالات فشل واضحة في الـ UiState بدون انهيار التطبيق.\n\nثالثاً: اختبار إعادة المحاولة والـ Exponential Backoff؛ لما السيرفر يرجع خطأ مؤقت، الكود بيعيد المحاولة بتأخير متضاعف: ثانية ثم ثانيتين ثم أربع ثوانٍ. في الاختبار، مش بنستنى 7 ثوانٍ حقيقية، بل بنستخدم `advanceTimeBy(1001)` ونتأكد إن عداد المحاولات زاد لـ 2، وبعدين `advanceTimeBy(2001)` ونتأكد إنه زاد لـ 3، وده بيسمح باختبار أعقد خوارزميات الـ Backoff والـ Jitter في أجزاء من الميلي ثانية.\n\nرابعاً: اختبار المهلة (Timeout)؛ بنستخدم `withTimeout` ونتأكد إن انتهاء الوقت الافتراضي بيلغي العملية الفرعية فوراً وبيرمي `TimeoutCancellationException` لحماية التطبيق من التعليق.",
        "deep_answer_ar": "تحت الكابوت، اختبار الإلغاء والمهام الزمنية بيعتمد على التفاعل الدقيق بين آلة حالات الكوروتينات (Continuation State Machine) وجدول `TestCoroutineScheduler`.\n\nفيما يخص الإلغاء، لما بتنادي `job.cancel()`، الرنتايم بيحط الـ Job في حالة `Cancelling` وينادي دوال الـ `invokeOnCompletion`. لو كان الكود بينفذ دالة suspend زي `delay` أو قراءة داتابيز، بيتم مقاطعتها ورمي `CancellationException` لإلغاء المكدس.\nلو المطور كاتب في الكود `catch (e: Exception)` بدون ما يفحص `if (e is CancellationException) throw e`، الكوروتين هيبتلع الاستثناء ويكمل شغل وكأنه مفيش حاجة حصلت! في بيئة `runTest`، الرنتايم بيراقب شجرة الـ Scope كاملة، وأول ما التيست يخلص لو لقى إن فيه كوروتين فرعي لسه شغال وماتلغاش، التيست بيفشل فوراً بـ `UncompletedCoroutinesError` عشان يفضح التسريب ده.\n\nأما بخصوص الـ Exponential Backoff، دالة `delay(time)` بتسجل الـ Continuation داخل طابور الـ Min-Heap التابع للـ TestScheduler.\nلما كود الاختبار يستدعي `advanceTimeBy(1000)`، الـ Scheduler بيعدل ساعة الـ Virtual Time ويفرغ كل المهام اللي وصل ميعادها، وده بيسمح بفحص عدد مرات الاستدعاء بدقة البايت كود.\nوفوق كده، في اختبارات الـ Timeouts عبر `withTimeout(duration)`، المحرك بيسجل مهمة إلغاء مجدولة عند زمن الـ duration؛ فلو العملية اكتملت قبلها بيتم مسح مهمة الإلغاء من الطابور O(1)، ولو الوقت الافتراضي وصل للحد الأقصى بيتم إطلاق استثناء المهلة فوراً، وده بيضمن بيئة اختبار محكمة بنسبة 100% على خوادم الـ CI."
    }
}

# ==========================================
# TST-11: How do you test Room DAOs, database migrations, and transactions?
# ==========================================
DATA["TST-11"] = {
    "concept_en": """Testing local persistence with Room requires isolating database operations into three specialized verification tiers: DAO contract testing, database migration testing, and transactional rollback testing. DAO unit testing validates CRUD queries, relational joins, transactions, and reactive Flow emissions using an ephemeral in-memory database built via Room.inMemoryDatabaseBuilder(). Database migration testing is mission-critical and must be executed as an instrumentation test using Room's MigrationTestHelper; it programmatically creates the database at historical schema version N, populates it with realistic raw SQLite fixtures, executes the Migration(N, N+1) object, and asserts that the schema hash and persisted data survive intact without data loss. Transaction testing verifies that multi-table batch operations roll back atomically when any constituent operation throws an exception, preventing database corruption.""",
    "walkthrough_en": """Testing Room DAOs in memory and verifying database schema migrations using MigrationTestHelper:
```kotlin
// 1. In-Memory DAO Testing on JVM / Instrumentation
@RunWith(AndroidJUnit4::class)
class UserDaoTest {
    private lateinit var db: AppDatabase
    private lateinit var userDao: UserDao

    @Before
    fun createDb() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java)
            .allowMainThreadQueries() // Acceptable strictly in isolated unit tests
            .build()
        userDao = db.userDao()
    }

    @After
    fun closeDb() = db.close()

    @Test
    fun insertAndReadUser() = runTest {
        val user = UserEntity(id = 1, name = "Mahmoud")
        userDao.insert(user)
        assertEquals("Mahmoud", userDao.findById(1)?.name)
    }
}

// 2. Migration Instrumentation Test using MigrationTestHelper
@RunWith(AndroidJUnit4::class)
class AppDatabaseMigrationTest {
    private val TEST_DB = "migration-test.db"

    @get:Rule
    val helper: MigrationTestHelper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java.canonicalName,
        FrameworkSQLiteOpenHelperFactory()
    )

    @Test
    fun migrate1To2_addsEmailColumn_andPreservesData() {
        // Create DB at version 1 and insert legacy row via raw SQLite
        helper.createDatabase(TEST_DB, 1).apply {
            execSQL("INSERT INTO users (id, name) VALUES (1, 'Ali')")
            close()
        }

        // Re-open and run migration to version 2 (adds email column)
        val db = helper.runMigrationsAndValidate(TEST_DB, 2, true, MIGRATION_1_2)

        // Verify data survived and new column defaults properly
        val cursor = db.query("SELECT id, name, email FROM users WHERE id = 1")
        assertTrue(cursor.moveToFirst())
        assertEquals("Ali", cursor.getString(cursor.getColumnIndexOrThrow("name")))
        assertEquals("", cursor.getString(cursor.getColumnIndexOrThrow("email")))
        cursor.close()
    }
}
```""",
    "short_en": """We test Room across three tiers. DAO queries and transactions are tested using an in-memory database built with Room.inMemoryDatabaseBuilder, ensuring fast, isolated execution that clears on close. Database migrations are verified on an emulator using MigrationTestHelper, which boots the database at version N, inserts legacy raw SQL fixtures, executes the Migration to N+1, and validates the schema hash and data integrity without data loss.""",
    "structured_en": """Securing enterprise persistence in Android requires an unyielding testing strategy across Room DAOs, schema migrations, and database transactions.
For DAO testing, we avoid touching disk storage by constructing an ephemeral in-memory database using Room.inMemoryDatabaseBuilder().
Because the database resides purely in RAM, tests execute rapidly and leave zero state behind upon teardown.
We test complex SQL queries, relational entity joins, cascading foreign key deletions, and reactive Flow emissions to verify that Room generates correct SQLite query plans.
For database migrations, testing is non-negotiable because an invalid migration crashes the application on app launch with an IllegalStateException in production.
We write automated instrumentation tests using Room's MigrationTestHelper.
The helper creates the database at historical version N using Room's exported schema JSON files, allows us to insert realistic legacy SQLite records, executes the production Migration(N, N+1) instance, and validates that the resulting schema matches version N+1 perfectly while preserving existing customer records.
Finally, we test multi-operation database transactions annotated with @Transaction, intentionally throwing an exception mid-operation to assert that Room rolls back all intermediate inserts atomically, preventing database corruption.""",
    "deep_senior_en": """Under the hood, Room database testing relies on SQLite's in-memory VFS and Room's schema identity hash verification architecture.
When Room.inMemoryDatabaseBuilder is used, Room passes :memory: as the database filename to sqlite3_open_v2.
The operating system creates an anonymous, private in-memory database instance tied to the SQLite connection handle; closing the connection instantly returns the RAM pages to the OS without disk I/O bottlenecks.
For schema migrations, Room enforces compile-time schema safety through exported JSON files generated by room.schemaLocation in the Gradle build configuration.
Every schema version generates a JSON snapshot detailing table names, column affinities, nullability constraints, primary keys, and indices, alongside an identityHash string.
When MigrationTestHelper.runMigrationsAndValidate(name, targetVersion, validateDroppedTables, migration) executes, it inspects targetVersion's JSON schema file.
It executes the custom Migration SQL statements on the SQLite engine and subsequently queries sqlite_master to reconstruct the actual schema in memory.
It compares this runtime schema column-by-column against the expected schema JSON.
Finally, it updates the room_master_table with the new identityHash.
If an engineer accidentally made a column NOT NULL without a DEFAULT value in the migration SQL, or mismatched an index definition, the helper fails with an explicit IllegalStateException diff detailing the exact column discrepancy before production release.
Senior engineers automate migration tests across all historic upgrade paths (such as migrating directly from v1 to v5) in CI pipelines to guarantee zero-crash updates for legacy app users.""",
    "meta_ar": {
        "id": "TST-11",
        "questionAr": "كيف تختبر قواعد بيانات Room: الـ DAOs والـ Migrations والـ Transactions باحترافية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على وضع استراتيجية شاملة لاختبار قواعد بيانات Room، واستخدام الـ In-memory Database للـ DAOs، واستخدام `MigrationTestHelper` لفحص ترقية الـ Schema، والتحقق من ذرية الـ Transactions.",
        "why_it_matters_ar": "فشل ترقية قاعدة البيانات (Migration) في الإنتاج يسبب كراش فوري لكل المستخدمين عند فتح التطبيق بعد التحديث، مما يؤدي لمراجعات سلبية وخسارة العملاء.",
        "worked_example_ar": "اختبار الـ DAO بـ In-memory واختبار الـ Migration بـ MigrationTestHelper:\n```kotlin\n// 1. DAO: قاعدة بيانات مؤقتة في الرام\nval db = Room.inMemoryDatabaseBuilder(context, AppDb::class.java).build()\n// 2. Migration: اختبار الترقية من إصدار 1 لـ 2 والتأكد من بقاء البيانات\nhelper.createDatabase(NAME, 1).apply { execSQL(\"INSERT INTO users VALUES (1, 'Ali')\"); close() }\nval db2 = helper.runMigrationsAndValidate(NAME, 2, true, MIGRATION_1_2)\n```",
        "trade_offs_ar": "اختبارات الـ Migration تتطلب تشغيل محاكي وإعداد ملفات الـ schema JSON في Gradle، لكنها الضمان الوحيد لمنع كراش `IllegalStateException` القاتل عند تحديث التطبيق.",
        "failure_modes_ar": "تعديل جدول في Room وزيادة رقم الإصدار مع تفعيل `fallbackToDestructiveMigration` في الإنتاج، مما يمسح داتابيز المستخدم بالكامل ويفقد كل بياناته المخزنة محلياً.",
        "production_perspective_ar": "في المشروعات الكبيرة، نلزم تصدير ملفات الـ Schema بـ `room.schemaLocation`، ونشغل اختبارات لكل مسارات الترقية القديمة (من v1 لـ v5) للتأكد من عدم مسح بيانات أي عميل قديم.",
        "how_to_answer_ar": "قسم الإجابة لثلاثة محاور متكاملة: أولاً اختبار الـ DAOs باستخدام `inMemoryDatabaseBuilder` في الرام لسرعة الفحص، ثانياً اختبار الـ Migrations بـ `MigrationTestHelper` وبناء الإصدار القديم بـ Raw SQL ثم تشغيل الترقية والتأكد من بقاء البيانات والـ Schema Hash، وثالثاً اختبار الـ Transactions برمي خطأ متعمد للتأكد من التراجع الذري (Rollback).",
        "talking_points_ar": "قاعدة بيانات الذاكرة (:memory:) للـ DAOs، ومكون MigrationTestHelper، وملفات الـ Schema JSON والـ Identity Hash، ومخاطر Destructive Migration، والـ Atomic Rollback في الـ Transactions.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يستحيل اختبار ترقيات Room (Migrations) بدون أجهزة أندرويد حقيقية أو محاكي؟\"\n  **المرشح:** \"لأن `MigrationTestHelper` بيحتاج محرك SQLite حقيقي ونظام ملفات متكامل يتبع لـ Android Framework عشان ينشئ الجداول الحقيقية ويطابق الـ Schema، وده مش موجود في الـ JVM العادي.\"\n\n- **المحاور:** \"كيف يتأكد Room من صحة الـ Schema بعد انتهاء الترقية برمجياً؟\"\n  **المرشح:** \"بيقارن الجداول الناتجة في SQLite مع ملف الـ JSON المصدر في البناء، وبيسجل كود فريد اسمه `identityHash` في جدول داخلي اسمه `room_master_table`؛ لو اختلف حقل واحد بيرمي خطأ فوري.\"",
        "self_check_ar": "هل غطيت الـ DAOs والـ Migrations والـ Transactions بالتفصيل؟ هل شرحت آلية عمل MigrationTestHelper؟ وهل بينت كيفية حماية بيانات المستخدمين؟",
        "references_ar": f"- [Testing Room migrations](https://developer.android.com/training/data-storage/room/testing-db) — الدليل الرسمي لجوجل لاختبار قواعد بيانات وترقيات Room.\n- [Room In-Memory Database](https://developer.android.com/reference/androidx/room/Room#inMemoryDatabaseBuilder) — توثيق استخدام قواعد بيانات الذاكرة المؤقتة.",
        "quick_answer_ar": "بنختبر قواعد بيانات Room على تلات مستويات احترافية: أولاً اختبارات الـ DAOs والـ Transactions بنعملها باستخدام قاعدة بيانات مؤقتة في الذاكرة بـ `Room.inMemoryDatabaseBuilder()`؛ بتشتغل في الرام بسرعة فائقة وتتمسح فور قفلها بدون لمس القرص الصلب. ثانياً اختبارات الـ Migrations دي اختبارات أجهزة حتمية بـ `MigrationTestHelper`؛ بننشئ الداتابيز برقم الإصدار القديم، ونحقن بيانات بـ Raw SQL، ونشغل كود الترقية `Migration`، ونتأكد إن الجداول اتحدثت والبيانات القديمة متمسحتش. ثالثاً اختبار الـ Transactions بنتأكد فيه إن رمي استثناء في نص العملية بيرجع الداتابيز لحالتها السابقة فوراً بدون تشويه البيانات.",
        "best_answer_ar": "اختبار طبقة البيانات في Room هو خط الدفاع الأول لمنع كراشات تحديث التطبيق وفقدان بيانات المستخدمين الحساسة.\n\nالمنهجية الهندسية المتينة بتنقسم لتلات محاور:\nالمحور الأول: اختبار الـ DAOs؛ بنستخدم `Room.inMemoryDatabaseBuilder()`. الميزة الكبرى إن الداتابيز بتكون محبوسة في الرام فقط (`:memory:`) ومبتكتبش أي ملفات على ذاكرة التخزين، فبنقدر نختبر صحة استعلامات الـ SQL المعقدة والـ Joins وتدفقات الـ Flow في بضعة أجزاء من الثانية مع تنظيف الذاكرة تلقائياً عند انتهاء الفحص.\n\nالمحور الثاني: اختبار الـ Migrations؛ ده أخطر جزء في التطبيق؛ لأن أي غلطة في سطر SQL للترقية بتخلي التطبيق ينهار بـ `IllegalStateException` عند كل المستخدمين أول ما يفتحوا التحديث! بنكتب اختبار Instrumentation على المحاكي باستخدام `MigrationTestHelper`. بنشغل الداتابيز بالإصدار القديم (مثلاً v1)، ونضيف مستخدمين بالـ Raw SQL، وبعدين ننفذ كائن الـ `Migration(1, 2)`؛ الأداة بتفحص إن الجدول الجديد اتضاف وإن بيانات المستخدم القديم فضلت سليمة بدون أي ضياع.\n\nالمحور الثالث: اختبار الـ Transactions؛ لما يكون عندنا عملية بتكتب في جدولين معاً بـ `@Transaction`، بنختبر إن حدوث خطأ في الجدول التاني بيعمل Rollback ذري للجدول الأول، وبكده بنضمن سلامة وتماسك البيانات في أصعب الظروف.",
        "deep_answer_ar": "تحت الكابوت، محرك Room بيتعامل مع محرك SQLite ونظام الـ Schema Identity Hash بطريقة بالغة الدقة.\nلما بتطلب `inMemoryDatabaseBuilder`، أندرويد بيمرر المسار الخاص `:memory:` لدالة `sqlite3_open_v2` في كود C++ الخاص بـ SQLite. المحرك بيحجز صفحات الذاكرة في الـ Virtual Memory المؤقتة للـ Process، وأول ما تقفل الاتصال بـ `db.close()`، نظام التشغيل بيفرغ الصفحات دي فوراً بصفر I/O على القرص الصلب.\n\nأما في اختبارات الـ Migrations، القوة الحقيقية بتنبع من تصدير ملفات الـ Schema بصيغة JSON عبر إعداد `room.schemaLocation` في ملف Gradle. ملف الـ JSON ده بيسجل كل صغيرة وكبيرة: أسماء الأعمدة، والـ Nullability، والـ Primary Keys، والـ Foreign Keys، وقيمة الـ `identityHash` الخاصة بكل جدول.\nأداة `MigrationTestHelper.runMigrationsAndValidate()` بتنفذ تعليمات الـ Migration على محرك SQLite، وبعدين بتعمل استعلام لجدول `sqlite_master` الداخلي وتبني شجرة الـ Schema اللي اتنفذت في الذاكرة، وتقارنها حرفاً بحرف مع ملف الـ JSON المتوقع للإصدار الجديد.\nلو نسيت تحط قيمة افتراضية لحقل جديد مش Nullable، أو نسيت تعمل Index متطابق، الأداة بتفشل فوراً وتطلع تقرير يوضح الفرق الدقيق بين الكودين قبل ما يوصل أي كود للمتجر.\nوفي كبرى الشركات، بنشغل اختبارات ترقية تراكمية تغطي كل الإصدارات من النسخة 1 للنسخة الحالية لضمان استقرار التطبيق لجميع المستخدمين."
    }
}

# ==========================================
# TST-12: How do you test HTTP failures with MockWebServer or equivalent?
# ==========================================
DATA["TST-12"] = {
    "concept_en": """Testing network communication resilience against HTTP failures requires intercepting network traffic with high protocol fidelity without relying on volatile external staging servers. OkHttp's MockWebServer provides a local, in-process HTTP/HTTPS server that binds to a loopback socket on localhost. Rather than mocking Retrofit interfaces or OkHttp clients—which bypasses the entire networking serialization pipeline—MockWebServer exercises real network protocol negotiation, HTTP connection pooling, authentication interceptors, and JSON deserialization. Engineers simulate deterministic failure matrices by enqueueing mock responses with HTTP 4xx client errors (such as 401 Unauthorized or 404 Not Found), 5xx server outages (500 Internal Server Error, 503 Service Unavailable), malformed JSON payloads, and network socket timeouts or abrupt connection drops via SocketPolicy.""",
    "walkthrough_en": """Simulating 503 Service Unavailable and socket disconnects with MockWebServer:
```kotlin
class UserApiServiceTest {
    private val mockWebServer = MockWebServer()
    private lateinit var apiService: UserApiService

    @Before
    fun startServer() {
        mockWebServer.start()
        apiService = Retrofit.Builder()
            .baseUrl(mockWebServer.url("/"))
            .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
            .build()
            .create(UserApiService::class.java)
    }

    @After
    fun stopServer() = mockWebServer.shutdown()

    @Test
    fun fetchUserProfile_server503Error_throwsHttpException() = runTest {
        // Enqueue an HTTP 503 Service Unavailable response with custom error payload
        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(503)
                .setBody("{\"error\": \"Database maintenance\", \"retry_after\": 60}")
        )

        try {
            apiService.getUserProfile("user_42")
            fail("Expected HttpException was not thrown!")
        } catch (e: HttpException) {
            assertEquals(503, e.code())
        }

        // Verify outgoing request headers and path
        val recordedRequest = mockWebServer.takeRequest()
        assertEquals("/users/user_42", recordedRequest.path)
        assertEquals("GET", recordedRequest.method)
    }

    @Test
    fun fetchUserProfile_socketDisconnect_throwsIOException() = runTest {
        // Simulate physical network cable unplug or abrupt TCP reset
        mockWebServer.enqueue(MockResponse().setSocketPolicy(SocketPolicy.DISCONNECT_AT_START))

        try {
            apiService.getUserProfile("user_42")
            fail("Expected IOException on socket disconnect!")
        } catch (e: IOException) {
            // Handled cleanly as a transport-level network exception
            assertNotNull(e.message)
        }
    }
}
```""",
    "short_en": """We test HTTP failures using MockWebServer, a local in-process HTTP server on localhost. Rather than mocking Retrofit interfaces, MockWebServer runs real OkHttp networking and JSON deserialization. We enqueue mock responses simulating 4xx client errors, 5xx server outages, malformed payloads, and transport-level connection cuts using SocketPolicy, while takeRequest asserts that outgoing HTTP headers, query parameters, and auth tokens match specifications.""",
    "structured_en": """Verifying application resilience in the face of unpredictable network failures is a primary requirement for production-grade mobile engineering.
A common architectural mistake is mocking the Retrofit API interface directly using MockK.
Mocking Retrofit bypasses OkHttp interceptors, authenticator refresh loops, SSL pinning configurations, and JSON serialization converters, leaving the entire networking pipeline untested.
The industry standard solution is OkHttp's MockWebServer.
MockWebServer launches a lightweight, real HTTP server on the local device loopback interface.
Retrofit is configured with the server's local URL, allowing network requests to traverse the complete production networking stack.
To test failure recovery, engineers enqueue predetermined MockResponse instances onto MockWebServer's queue.
We simulate 401 Unauthorized responses to verify that OkHttp Authenticator interceptors trigger token refresh workflows and retry the original request.
We enqueue 500 and 503 server errors to verify that repositories convert HTTP status codes into domain-friendly failure states and schedule exponential backoff retries.
We inject malformed or incomplete JSON to verify that Kotlinx Serialization exceptions are caught cleanly without crashing the UI.
Finally, using SocketPolicy.DISCONNECT_AT_START or SocketPolicy.NO_RESPONSE, we test how the application handles abrupt TCP disconnects, packet drops, and read timeouts.""",
    "deep_senior_en": """Under the hood, MockWebServer operates by creating a genuine ServerSocket bound to an ephemeral loopback port on 127.0.0.1.
When Retrofit executes an HTTP network call, OkHttp's RealCall initiates a complete TCP three-way handshake (SYN, SYN-ACK, ACK) with MockWebServer's active listening socket.
The outbound request traverses OkHttp's full interceptor pipeline: RetryAndFollowUpInterceptor, BridgeInterceptor, CacheInterceptor, ConnectInterceptor, and CallServerInterceptor.
Every outgoing header, including Authorization Bearer tokens, User-Agent strings, and Gzip compression flags, is serialized into wire-format HTTP/1.1 or HTTP/2 frames.
MockWebServer reads the incoming byte stream, logs the parsed payload into an in-memory RecordedRequest queue, and matches it against enqueued MockResponse objects.
When testing socket failures, MockWebServer manipulates the underlying TCP socket channel directly.
Configuring SocketPolicy.DISCONNECT_AT_START forces MockWebServer to close the TCP socket immediately upon accepting the connection, causing OkHttp's SocketChannel to receive an RST packet and throw a raw java.io.IOException or SocketException.
Configuring SocketPolicy.NO_RESPONSE leaves the socket open without writing response bytes, verifying that OkHttp's readTimeoutMillis triggers properly and cleans up allocated connection resources.
Engineers use takeRequest() to assert that request paths, query parameters, custom headers, and JSON mutation bodies strictly adhere to API specifications before test assertions complete.
This rigorous testing approach provides 100% network stack fidelity without depending on external internet connections or flaky staging servers.""",
    "meta_ar": {
        "id": "TST-12",
        "questionAr": "كيف تختبر أخطاء وفشل اتصالات الـ HTTP باحترافية باستخدام MockWebServer؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على اختبار طبقة الشبكة بموثوقية عالية، واستخدام `MockWebServer` بدلاً من عمل Mock لـ Retrofit، واختبار أخطاء الـ 4xx والـ 5xx، ومحاكاة انقطاع الاتصال ومشاكل الـ Sockets بـ `SocketPolicy`.",
        "why_it_matters_ar": "عمل Mock لواجهة Retrofit يتخطى كل الـ Interceptors والـ Serialization ويخفي أخطاء الشبكة الحقيقية، بينما MockWebServer يختبر خط أنابيب الشبكة بالكامل محلياً وبدون خوادم خارجية.",
        "worked_example_ar": "محاكاة خطأ 503 وانقطاع السوكت بـ MockWebServer:\n```kotlin\n// محاكاة سيرفر واقعي محلياً على الـ JVM\nserver.enqueue(MockResponse().setResponseCode(503).setBody(\"{\"error\":\"Busy\"}\"))\nassertThrows(HttpException::class.java) { api.getData() }\n// محاكاة قطع الاتصال فجأة من كابل الإنترنت\nserver.enqueue(MockResponse().setSocketPolicy(SocketPolicy.DISCONNECT_AT_START))\nassertThrows(IOException::class.java) { api.getData() }\n```",
        "trade_offs_ar": "تشغيل MockWebServer يفتح Local TCP Socket حقيقي على الـ JVM، وده أبطأ بجزء بسيط جداً من مجرد عمل Mock عادي، لكنه يمنح موثوقية 100% ويختبر الـ Interceptors والـ DTO parsing الحقيقي.",
        "failure_modes_ar": "الاعتماد على سيرفرات Staging حقيقية في الـ CI؛ مما يجعل الاختبارات تفشل عشوائياً عند انقطاع الإنترنت أو أثناء صيانة السيرفر الخارجي.",
        "production_perspective_ar": "في المشروعات الكبيرة، نمنع عمل Mock لكلاسات الـ Retrofit تماماً؛ كل اختبارات الـ Repository والـ Network تمر عبر MockWebServer مع فحص الـ Headers بـ `takeRequest()`.",
        "how_to_answer_ar": "وضح الفارق الجوهري: عمل Mock لـ Retrofit هو ممارسة سيئة لأنه يتخطى الـ Interceptors والـ Parsers، والحل القياسي هو MockWebServer الذي يفتح سيرفر محلي حقيقي على 127.0.0.1، واشرح محاكاة أخطاء 4xx و 5xx ومحاكاة انقطاع الاتصال والـ Timeouts باستخدام `SocketPolicy`، وفحص الطلبات المرسلة بـ `takeRequest()`.",
        "talking_points_ar": "سيرفر MockWebServer المحلي على الـ Loopback، وعيوب عمل Mock لواجهة Retrofit، واختبار أخطاء 4xx و 5xx، والـ SocketPolicy لمحاكاة انقطاع الشبكة، وفحص الـ Headers بـ takeRequest.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يعتبر عمل Mock لواجهة Retrofit بـ MockK ممارسة غير مستحسنة؟\"\n  **المرشح:** \"لأنك بتعمل Mock للكلاس النهائي وبتتخطى كل الـ OkHttp Interceptors زي توكن الأمان والـ Logging، وبتتخطى تحويل الـ JSON بـ kotlinx.serialization؛ فلو السيرفر بعت داتا بنوع مختلف التيست مش هيكتشف الكراش.\"\n\n- **المحاور:** \"كيف تحاكي انقطاع النت في نص التحميل باستخدام MockWebServer؟\"\n  **المرشح:** \"باستخدام `SocketPolicy.DISCONNECT_DURING_RESPONSE_BODY`؛ السيرفر بيبعت جزء من البيانات وبعدين يقفل الاتصال فجأة، وده بيختبر قدرة التطبيق على التقاط الـ IOException وإعادة المحاولة.\"",
        "self_check_ar": "هل شرحت سبب تفضيل MockWebServer على Mocking Retrofit؟ هل وضحت اختبار أخطاء الـ HTTP المختلفة؟ وهل ذكرت دور SocketPolicy و takeRequest؟",
        "references_ar": f"- [OkHttp MockWebServer](https://github.com/square/okhttp/tree/master/mockwebserver) — التوثيق الرسمي لمكتبة MockWebServer من Square.\n- [Testing Android Network Layers](https://developer.android.com/training/testing/) — دليل جوجل لاختبار طبقات الاتصال والشبكة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنختبر أخطاء وفشل الـ HTTP باحترافية باستخدام `MockWebServer` من Square؛ الأداة دي بتشغل سيرفر HTTP حقيقي محلياً على الجهاز (`localhost`)، وده بيمكّننا من اختبار شبكة حقيقية كاملة بكل الـ Interceptors والـ Serialization بدون خوادم خارجية متقلبة. بنجهز استجابات وهمية في الطابور بـ `server.enqueue()` لمحاكاة كود 401 لفحص تجديد التوكن، وكود 503 لفحص إعادة المحاولة، و `SocketPolicy.DISCONNECT_AT_START` لمحاكاة انقطاع كابل النت، وبنستخدم `takeRequest()` للتأكد من إرسال الترويسات والـ Headers والـ Auth Tokens بشكل سليم.",
        "best_answer_ar": "اختبار طبقة الشبكة باستخدام `MockWebServer` هو الأسلوب الاحترافي المعتمد عالمياً، والبديل الصارم للأسلوب الخاطئ الشائع وهو عمل Mock لواجهة الـ Retrofit بـ MockK.\n\nالخطأ في عمل Mock لـ Retrofit إنه بيتخطى خط أنابيب الشبكة بالكامل؛ يعني مبيختبرش الـ Auth Interceptors، ولا الـ Logging، ولا الـ Gzip، ولا فك شفرة الـ JSON. لو السيرفر غير اسم حقل، التيست هينجح والتطبيق هيكرش في الإنتاج!\n\n`MockWebServer` بيحل ده بعبقرية؛ بيفتح Local Socket حقيقي على الـ JVM، وبنربط به الـ Base URL بتاع التطبيق. بنختبر مصفوفة الفشل المتكاملة بالطرق دي:\nأولاً: أخطاء الـ Client (4xx)؛ بنحط كود 401 Unauthorized في السيرفر، ونتأكد إن الـ OkHttp Authenticator التقط الخطأ وراح جدد التوكن وأعاد إرسال الطلب الأصلي تلقائياً.\n\nثانياً: أخطاء السيرفر (5xx)؛ بنحاكي كود 500 أو 503، ونتأكد إن الـ Repository بيلف الخطأ في كائن Result سليم ومبيطلعش كراش للواجهة.\n\nثالثاً: مشاكل عتاد الشبكة والـ Sockets؛ بنستخدم خاصية `SocketPolicy` المدمجة؛ نقدر نحاكي انقطاع الاتصال فجأة بـ `DISCONNECT_AT_START`، أو نحاكي تأخر السيرفر بـ `NO_RESPONSE`، وده بيختبر قدرة التطبيق على معالجة الـ `SocketTimeoutException` بنجاح تام وبدون تذبذب في خوادم الـ CI.",
        "deep_answer_ar": "تحت الكابوت، `MockWebServer` بيعتمد على إنشاء كائن `ServerSocket` أصلي في الجافا على عنوان `127.0.0.1` مع تخصيص Port عشوائي فارغ.\nلما كود أندرويد يستدعي دالة الشبكة عبر Retrofit، مكتبة OkHttp بتنفذ دورة الاتصال الحقيقية بالكامل (TCP Handshake)، وبتمرر الطلب عبر مصفوفة الـ Interceptors الخمسة الأصلية في OkHttp: من الـ `RetryAndFollowUpInterceptor` لحد الـ `CallServerInterceptor`.\nالطلب بيتم تحويله لـ Raw HTTP Bytes وبيتبعت عبر الـ Loopback Socket المفتوح محلياً.\n\nكائن MockWebServer بيقرأ البايتات دي ويسجلها في كائن `RecordedRequest` متاح للفحص عبر `server.takeRequest()`، وده بيمكّننا من التأكد إن الـ Headers والـ Query Parameters المشفرة والـ Body اتبعتوا صح بنسبة 100% وبدون أي نقص.\n\nوعند محاكاة أخطاء الـ Socket، قوة MockWebServer بتظهر في التحكم بمستوى بروتوكول الـ TCP نفسه:\nلما بتحدد `SocketPolicy.DISCONNECT_AT_START`، السيرفر بيقبل الاتصال وفوراً بينادي `socket.close()`؛ فخيط الـ OkHttp بيستقبل حزمة TCP Reset (RST Packet) فورية، وبيرمي استثناء `java.io.IOException` أصلي من الـ SocketChannel.\nولما بتحدد `SocketPolicy.NO_RESPONSE`، السيرفر بيمسك الـ Socket مفتوح ومبيردش ولا بايت، فبيتفعل تايم آوت الـ `readTimeout` المبرمج في OkHttp وبيتم إغلاق الاتصال بأمان.\nده بيحقق واقعية تامة بنسبة 100% لاختبار أصعب سيناريوهات فشل الشبكة وانقطاع الاتصال بدون الاعتماد على إنترنت حقيقي وبدون Flakiness."
    }
}

# ==========================================
# TST-13: How do you test DI substitutions and scoped dependencies?
# ==========================================
DATA["TST-13"] = {
    "concept_en": """Testing dependency injection substitutions and scoped dependencies ensures that production component graphs can be reconfigured cleanly for automated verification without state leaks or architecture violations. In pure JVM unit testing, dependency substitution is achieved seamlessly through constructor injection by supplying test doubles directly. In Hilt on-device or Robolectric testing, substitution operates at the Dagger dependency graph level using @HiltAndroidTest. Developers override production Dagger modules using @UninstallModules and provide test replacements via nested @TestInstallIn modules or @BindValue fields. Testing scoped dependencies (such as @Singleton, @ActivityRetainedScoped, or @ViewModelScoped) requires verifying that instances are reused within their active lifecycle scope and destroyed deterministically when the hosting scope terminates.""",
    "walkthrough_en": """Substituting Hilt modules and testing scoped dependencies using @TestInstallIn:
```kotlin
// 1. Production Module bound to SingletonComponent
@Module
@InstallIn(SingletonComponent::class)
abstract class AnalyticsModule {
    @Binds
    @Singleton
    abstract fun bindAnalytics(impl: FirebaseAnalyticsTracker): AnalyticsTracker
}

// 2. Test Module replacing production module across all tests in the test suite
@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [AnalyticsModule::class]
)
abstract class FakeAnalyticsModule {
    @Binds
    @Singleton
    abstract fun bindFakeAnalytics(fake: FakeAnalyticsTracker): AnalyticsTracker
}

// 3. Instrumented Hilt Test verifying scoped dependency substitution
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class CheckoutActivityTest {
    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var analyticsTracker: AnalyticsTracker

    @Before
    fun setup() {
        hiltRule.inject() // Injects FakeAnalyticsTracker!
    }

    @Test
    fun checkout_logsPurchaseEvent_onFakeInstance() {
        val fake = analyticsTracker as FakeAnalyticsTracker
        assertEquals(0, fake.loggedEvents.size)

        launchActivity<CheckoutActivity>().use {
            onView(withId(R.id.btn_buy)).perform(click())
            assertEquals("purchase_completed", fake.loggedEvents.first())
        }
    }
}
```""",
    "short_en": """We test DI substitutions differently across testing tiers. In JVM unit tests, we bypass DI frameworks entirely using constructor injection to pass test doubles directly. In Hilt instrumented or Robolectric tests, we use @HiltAndroidTest, replacing production modules with test doubles via @TestInstallIn or @UninstallModules and @BindValue. For scoped dependencies, we verify that instances remain identical within their lifecycle scope and recreate across process recreation.""",
    "structured_en": """Architecting dependency injection with testing in mind is one of the greatest advantages of using Hilt and Dagger in enterprise Android engineering.
At the local JVM unit testing tier, the most effective strategy is to avoid running the DI framework altogether.
Because classes rely on constructor injection, unit tests instantiate the class directly with standard Kotlin constructors, passing in lightweight fakes or mocks without Dagger reflection or annotation processing overhead.
At the instrumented and integration testing tiers, tests must execute against real or emulated dependency graphs.
Hilt provides first-class support for this via the @HiltAndroidTest annotation and HiltAndroidRule.
To substitute an external production service—such as swapping a live payment gateway or Firebase analytics with an in-memory fake—we annotate a test module with @TestInstallIn, explicitly declaring which production module it replaces across the SingletonComponent.
For localized single-test substitutions, developers use @UninstallModules alongside @BindValue, injecting an inline mock directly into the test class.
When validating scoped dependencies, tests assert instance equality (assertSame) across multiple injections within the same Activity or ViewModel lifecycle, and verify that rotating the screen or recreating the component cleans up the scoped instance, preventing cross-test state pollution.""",
    "deep_senior_en": """Under the hood, Hilt dependency substitution orchestrates compile-time bytecode rewriting, custom annotation processing, and specialized test application class loading.
Standard production Hilt applications extend a generated Hilt_MyApplication that initializes the root SingletonComponent during onCreate().
When @HiltAndroidTest is executed, the Android test runner (such as HiltTestRunner) substitutes the application instance with HiltTestApplication before component binding starts.
Hilt's annotation processor scans the test classpath for all @TestInstallIn declarations and constructs a bespoke Dagger component graph specifically for the test suite execution.
Any module listed in replaces = [...] is stripped out of the generated Dagger component definition, ensuring that production bindings are never instantiated.
When @BindValue is used, Hilt generates a subcomponent binding that intercepts the injection graph at compile time, passing the exact instance initialized in the test class register.
Regarding scope lifecycles, Hilt scopes correspond to memoization entries stored in a thread-safe ScopeMap inside the generated Dagger subcomponent.
For example, @ActivityRetainedScoped instances are stored in an ActivityRetainedComponent holder that survives configuration changes by attaching to an internal headless ViewModelStore.
Testing these scopes requires simulating configuration changes using ActivityScenario.recreate() and asserting that the injected dependency retains its exact identity hash code, whereas calling ActivityScenario.close() disposes of the component and evicts all scoped references from memory, preventing memory leaks between test executions.""",
    "meta_ar": {
        "id": "TST-13",
        "questionAr": "كيف تختبر استبدال التبعيات (DI Substitutions) والتبعيات المحددة النطاق (Scoped Dependencies) في Hilt؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على استبدال التبعيات في اختبارات Hilt بـ `@TestInstallIn` و `@UninstallModules`، وفهم الفرق بين اختبار الـ JVM المباشر واختبارات الـ Component، والتحقق من دورة حياة الـ Scopes.",
        "why_it_matters_ar": "استخدام كود الإنتاج الحقيقي (زي Firebase أو بوابات الدفع) أثناء الاختبارات يفسد قواعد البيانات الحقيقية ويسرب بيانات العملاء، بينما عزل التبعيات بـ Hilt يوفر بيئة اختبار آمنة ومستقرة.",
        "worked_example_ar": "استبدال موديول الإنتاج بموديول تجريبي بـ TestInstallIn:\n```kotlin\n@Module\n@TestInstallIn(components = [SingletonComponent::class], replaces = [NetworkModule::class])\nabstract class FakeNetworkModule {\n    @Binds @Singleton abstract fun bindRepo(fake: FakeRepo): Repo\n}\n```",
        "trade_offs_ar": "استخدام `@TestInstallIn` يستبدل الموديول لكل اختبارات المشروع في موديول التيست، بينما `@UninstallModules` و `@BindValue` يسمحان بالاستبدال داخل كلاس اختبار واحد فقط.",
        "failure_modes_ar": "نسيان وضع `@HiltAndroidTest` و `HiltAndroidRule` في اختبار الـ Instrumentation، مما يجعل حقول `@Inject` فارغة وترمي `UninitializedPropertyAccessException`.",
        "production_perspective_ar": "في المشروعات الكبيرة، نعتمد Constructor Injection المباشر في 80% من اختبارات الـ Unit Tests على الـ JVM، ونقصر Hilt Test Graph على اختبارات التكامل والـ E2E.",
        "how_to_answer_ar": "وضح المستويين: أولاً في الـ Unit Tests على الـ JVM نتجنب تشغيل فريمورك الـ DI تماماً ونحقن التبعيات بالـ Constructor مباشرة لسرعة الاختبار، ثانياً في اختبارات Hilt بـ `@HiltAndroidTest` نستخدم `@TestInstallIn` لاستبدال الموديول على مستوى المشروع أو `@BindValue` لكلاس محدد، واشرح فحص الـ Scopes والتأكد من بقائها مع تدوير الشاشة.",
        "talking_points_ar": "حقن التبعيات المباشر في الـ JVM، ومكون `@HiltAndroidTest` و `HiltAndroidRule`، وموديولات `@TestInstallIn` مقابل `@UninstallModules`، واستخدام `@BindValue`، واختبار الـ Scopes بـ `ActivityScenario`.",
        "follow_ups_ar": "- **المحاور:** \"متى تختار `@TestInstallIn` ومتى تفضل `@BindValue`؟\"\n  **المرشح:** \"`@TestInstallIn` بنستخدمه لما نكون عايزين استبدال عام وشامل على مستوى كل الاختبارات (زي Fake Analytics)، بينما `@BindValue` بنستخدمه داخل ملف اختبار واحد فقط لتمرير Mock أو قيمة محددة لشاشة معينة.\"\n\n- **المحاور:** \"كيف تتأكد أن كائناً معيناً يحترم نطاق `@ActivityRetainedScoped` في الاختبار؟\"\n  **المرشح:** \"باستخدام `ActivityScenario.recreate()` لتدوير الشاشة، ونتأكد بـ `assertSame` إن الكائن المحقون محتفظ بنفس الـ Hash Code ولم تتم إعادة بنائه من الصفر.\"",
        "self_check_ar": "هل وضحت الفارق بين اختبار الـ JVM واختبارات Hilt؟ هل شرحت كيفية استبدال الموديولات بـ TestInstallIn؟ وهل بينت فحص الـ Scopes؟",
        "references_ar": f"- [Hilt Testing Guide](https://developer.android.com/training/dependency-injection/hilt-testing) — التوثيق الرسمي لجوجل لاختبار Hilt واستبدال التبعيات.\n- [Dagger Testing Best Practices](https://dagger.dev/testing) — أفضل ممارسات اختبار الرسوم البيانية للتبعيات.",
        "quick_answer_ar": "بنتعامل مع استبدال التبعيات (DI Substitution) بذكاء حسب بيئة الاختبار: في اختبارات الـ `Unit Tests` على الـ JVM، بنستغني تماماً عن تشغيل Hilt، وبنمرر كائنات الـ Fake مباشرة في الـ Constructor لسرعة التنفيذ الخارقة. أما في اختبارات الـ Instrumentation أو Robolectric، بنستخدم `@HiltAndroidTest` مع `HiltAndroidRule`؛ وبنستبدل موديولات الإنتاج باستخدام `@TestInstallIn(replaces = [...])` لتعميم الـ Fake على كل الاختبارات، أو بنستخدم `@BindValue` داخل كلاس اختبار معين لحقن Mock محدد. وبالنسبة للـ Scopes، بنختبر إن الكائن بيفضل هو نفسه عبر `assertSame` ومبيعدش إنشاؤه إلا مع انتهاء نطاق دورة حياته.",
        "best_answer_ar": "التعامل باحترافية مع استبدال التبعيات في Hilt بيكشف مدى استيعاب المهندس للفرق بين اختبارات المكونات السريعة واختبارات التكامل الحقيقية.\n\nالمنهجية المتبعة بتنقسم لمستويين:\nالمستوى الأول: اختبارات الوحدة على الـ JVM؛ دي بتمثل 80% من الكود، وأفضل ممارسة هنا هي عدم استخدام Hilt على الإطلاق! طالما كودك بيعتمد على الـ Constructor Injection، بنبني الكلاس بالـ Constructor العادي ونمرر كائنات Fake أو Mock، وده بيخلي التيست ينفذ في 10 ميلي ثانية وبدون تكلفة معالجة الـ Annotations.\n\nالمستوى الثاني: اختبارات التكامل بـ Hilt؛ هنا بنحتاج الـ Dependency Graph الكامل يشتغل. بنحط فوق كلاس التيست `@HiltAndroidTest` ونضيف قاعدة `HiltAndroidRule`. لاستبدال موديول إنتاج زي بوابات الدفع أو Analytics، بنعمل موديول اختبار ونحط عليه `@TestInstallIn(components = [SingletonComponent::class], replaces = [AnalyticsModule::class])`، فـ Hilt أوتوماتيكياً بتحذف موديول الإنتاج وتحط بداله الموديول الوهمي.\nولو عايزين نستبدل كائن في تيست واحد محدد، بنستخدم `@BindValue` في التيست مباشرة.\n\nوفي اختبار النطاقات (Scopes) زي `@ActivityRetainedScoped`، بنستخدم `ActivityScenario` وندور الشاشة بـ `recreate()` ونتأكد إن الكائن المحقون لم يتغير واحتفظ بنفس الـ State، ولما الـ Activity تتقفل خالص نتأكد إن الـ Scope اتهدم تماماً لمنع تسريب الذاكرة بين الاختبارات.",
        "deep_answer_ar": "تحت الكابوت، Hilt بتنفذ استبدال التبعيات عبر تعديل شجرة توليد كود Dagger في مرحلة الـ Annotation Processing وربطها بـ Test Application مخصص.\nفي الوضع الطبيعي، التطبيق بيشتغل بـ `Hilt_Application` اللي بتبني الـ `SingletonComponent` عند الإقلاع. في بيئة الاختبار بـ `@HiltAndroidTest`، مشغل الاختبار `HiltTestRunner` بيستبدل كلاس التطبيق بـ `HiltTestApplication` قبل بدء بناء شجرة التبعيات.\nمعالج الكود بيمسح الـ Classpath بالكامل؛ أول ما يلاقي موديول عليه `@TestInstallIn(replaces = [ProductionModule::class])`، بيقوم بحذف موديول الإنتاج من شجرة التوليد تماماً، ويبني الـ Dagger Graph بالاعتماد على الموديول التجريبي، وده بيضمن عدم استدعاء كود الإنتاج نهائياً.\n\nولما بتستخدم `@BindValue` داخل كلاس التيست، Hilt بتولد Subcomponent Binding مؤقت بيتسجل في مصفوفة الحقول وقت استدعاء `hiltRule.inject()`.\n\nأما بخصوص الـ Scopes، فـ Dagger بتديرها داخلياً عبر كائن `ScopeMap` في كل Subcomponent؛ لما كلاس يكون `@Singleton`، الكائن بيتكيش في الماب التابعة لـ `SingletonComponent`. وفي حالة `@ActivityRetainedScoped`، الكائن بيتكيش داخل Subcomponent خاص مربوط بـ `ViewModelStore` خفي من أندرويد لكي ينجو من الـ Configuration Changes.\nالتحقق من صحة الـ Scopes في الاختبار بيضمن إن الكائنات دي بتحافظ على هويتها وحالتها البرمجية بدقة ومبتتحولش لـ Singletons أبدية تسرب الذاكرة بين الاختبارات المتتالية على نفس الـ CI Runner."
    }
}

# ==========================================
# TST-14: How do you test Compose UI semantics, navigation, and accessibility?
# ==========================================
DATA["TST-14"] = {
    "concept_en": """Testing Jetpack Compose user interfaces across semantics, navigation, and accessibility requires testing directly against the Compose Semantics tree rather than inspecting physical Android View hierarchies or raw pixels. The official Compose Test API (createComposeRule() or createAndroidComposeRule<T>()) mounts composables in an isolated, headless testing scope. Semantics assertions query accessibility properties using matchers like onNodeWithText(), onNodeWithContentDescription(), and hasClickAction(). Accessibility testing asserts that interactive widgets expose meaningful content descriptions, meet the minimum 48dp by 48dp interactive touch target size, and merge composite child components into unified cards using mergeDescendants. Navigation testing decouples screen destinations from real navigation transitions using TestNavHostController to assert currentBackStackEntry routes deterministically on the JVM.""",
    "walkthrough_en": """Testing Compose accessibility semantics and navigation with TestNavHostController:
```kotlin
class ComposeUiAccessibilityAndNavTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    // 1. Accessibility Semantics & Touch Target Test
    @Test
    fun saveButton_satisfiesAccessibilityCriteria() {
        composeTestRule.setContent {
            IconButton(
                onClick = {},
                modifier = Modifier.semantics {
                    contentDescription = "Save Document"
                    role = Role.Button
                }
            ) {
                Icon(Icons.Default.Save, contentDescription = null)
            }
        }

        // Verify contentDescription, role, and minimum 48dp touch target
        composeTestRule.onNodeWithContentDescription("Save Document")
            .assertIsDisplayed()
            .assertTouchBoundsInRootIsEqualTo(48.dp, 48.dp)
    }

    // 2. Deterministic Navigation Flow Test using TestNavHostController
    @Test
    fun navigatingFromHomeToDetails_updatesBackStackRoute() {
        lateinit var navController: TestNavHostController

        composeTestRule.setContent {
            val context = LocalContext.current
            navController = TestNavHostController(context).apply {
                navigatorProvider.addNavigator(ComposeNavigator())
            }
            AppNavHost(navController = navController)
        }

        // Click product card and verify destination route
        composeTestRule.onNodeWithText("View Details").performClick()
        assertEquals("details/{productId}", navController.currentBackStackEntry?.destination?.route)
    }
}
```""",
    "short_en": """We test Compose UIs by querying the Semantics tree with createComposeRule. Accessibility is tested by asserting contentDescription on non-text elements, verifying mergeDescendants on complex cards, and checking minimum 48dp touch bounds. Navigation is tested by injecting a TestNavHostController into the NavHost, simulating button clicks, and asserting that currentBackStackEntry reflects the expected destination route deterministically without emulators.""",
    "structured_en": """Testing modern Android user interfaces in Jetpack Compose operates fundamentally differently from traditional View-based Espresso testing.
Because Compose bypasses the android.view.View hierarchy to draw directly onto a hardware Canvas, Compose UI testing queries the parallel Semantics tree.
Using createComposeRule(), tests render composables in headless JVM or instrumented environments.
To verify visual correctness and interactions, we use semantic matchers like onNodeWithText() and performClick(), checking that buttons trigger user event callbacks.
For accessibility verification, the test suite asserts that assistive technologies like TalkBack can convey meaningful context.
We verify that icons and images provide explicit contentDescription properties, that complex list cards utilize Modifier.semantics(mergeDescendants = true) to unify fragmented child labels into a single readable announcement, and that touch targets satisfy the 48dp by 48dp minimum boundary via assertTouchBoundsInRootIsEqualTo().
For navigation testing, the architecture avoids coupling tests to live platform window animations.
We inject a TestNavHostController into the navigation composable.
Upon dispatching click events on the screen, the test asserts that navController.currentBackStackEntry.destination.route matches the target destination string, validating the entire navigation graph deterministically in sub-second execution times.""",
    "deep_senior_en": """Under the hood, Compose UI testing inspects SemanticsNode instances generated by the Compose compiler during layout passes.
Every Composable emitting layout modifiers contributes to a SemanticsConfiguration map stored within its corresponding LayoutNode.
When createComposeRule().setContent { ... } executes, Compose builds the layout tree and synchronizes it with an internal SemanticsOwner.
Assertion APIs like onNodeWithText() traverse this SemanticsNode tree matching SemanticsPropertyKey entries (such as ContentDescription, Text, Role, and Selected).
Because this architecture operates on semantic metadata rather than rendered pixel buffers, tests run flawlessly on headless JVM desktop runners via Robolectric without needing physical GPU drivers.
When testing accessibility, Compose bridges its SemanticsNode hierarchy to Android's native AccessibilityNodeInfoCompat via AndroidComposeViewAccessibilityDelegateCompat.
Using mergeDescendants = true collapses the sub-tree's semantic properties into a single synthetic node, preventing TalkBack from forcing visually impaired users to traverse redundant child nodes.
When testing navigation, TestNavHostController provides a synchronous, in-memory implementation of NavHostController.
It stores navigation destination entries inside a standard ArrayDeque backstack structure.
When a test clicks a navigation trigger, TestNavHostController bypasses the platform Choreographer transition animations, updating the backstack synchronously on the test execution thread.
Senior engineers combine semantics assertions with TestNavHostController to achieve complete UI and navigation verification with zero emulator flakiness in automated CI pipelines.""",
    "meta_ar": {
        "id": "TST-14",
        "questionAr": "كيف تختبر واجهات Jetpack Compose: شجرة الـ Semantics والتنقل (Navigation) وسهولة الوصول (Accessibility)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على اختبار واجهات كومبوز عبر شجرة الـ Semantics Tree، وفحص إمكانية الوصول وقارئات الشاشة (TalkBack)، وضبط حدود اللمس 48dp، واختبار مسارات التنقل بـ `TestNavHostController`.",
        "why_it_matters_ar": "إهمال اختبار الـ Semantics يمرر واجهات غير قابلة للاستخدام لفاقدي البصر، واختبار التنقل على المحاكي بانتظار الأنيميشن يهدر ساعات في الـ CI بدلاً من الفحص المتزامن السريع.",
        "worked_example_ar": "اختبار الـ Semantics وإمكانية الوصول والتنقل في Compose:\n```kotlin\n// 1. فحص إمكانية الوصول ووصف العنصر ومساحة اللمس 48dp\nrule.onNodeWithContentDescription(\"Save\").assertTouchBoundsInRootIsEqualTo(48.dp, 48.dp)\n// 2. فحص التنقل بـ TestNavHostController\nrule.onNodeWithText(\"Details\").performClick()\nassertEquals(\"details_route\", navController.currentBackStackEntry?.destination?.route)\n```",
        "trade_offs_ar": "اختبار شجرة الـ Semantics أسرع وأثبت بكثير من اختبارات الشاشة الكاملة، لكنه يتحقق من معاني ووظائف المكونات البرمجية وليس من الألوان والبكسلات الدقيقة (التي تتطلب Screenshot testing).",
        "failure_modes_ar": "استخدام نصوص عشوائية في `testTag` لاختبار كل عنصر بدلاً من الاعتماد على نصوص الواجهة وإمكانية الوصول الحقيقية، مما يقلل من فحص جودة الـ Accessibility.",
        "production_perspective_ar": "في المشروعات الكبيرة، نعتمد اختبار شجرة الـ Semantics كمعيار أساسي لفحص جودة الشاشات في الـ CI، ونلزم فحص الـ 48dp Touch Targets لكل الأزرار التفاعلية.",
        "how_to_answer_ar": "قسم الإجابة لثلاثة محاور: أولاً شجرة الـ Semantics وكيفية فحص المكونات بـ `createComposeRule`، ثانياً إمكانية الوصول (Accessibility) بفحص `contentDescription` و `mergeDescendants` ومساحة اللمس 48dp، وثالثاً التنقل بحقن `TestNavHostController` وفحص مسارات الـ Backstack بدون انتظار حركات الأنيميشن.",
        "talking_points_ar": "شجرة الـ SemanticsNode مقابل الـ Views، ودور createComposeRule، وفحص إمكانية الوصول لـ TalkBack، وحد أدنى لمساحة اللمس 48dp، واختبار مسارات التنقل بـ TestNavHostController.",
        "follow_ups_ar": "- **المحاور:** \"لماذا نفضل البحث بـ `onNodeWithText` بدلاً من وضع `testTag` على كل عنصر؟\"\n  **المرشح:** \"لأن البحث بالنصوص ووصف الوصول بيفحص ما يراه ويسمعه المستخدم الحقيقي بالفعل، وده بيضمن جودة الـ Accessibility، بينما `testTag` بيكون مجرد كود إضافي ملوش فائدة للمستخدم العادي.\"\n\n- **المحاور:** \"كيف يسرع `TestNavHostController` اختبارات التنقل في خطوط الـ CI؟\"\n  **المرشح:** \"لأنه بينفذ التنقل متزامناً في الذاكرة ويتخطى حركات الأنيميشن وشاشات الانتقال البصرية، فبنقدر نتأكد من مسار الصفحة الجديدة في أجزاء من الميلي ثانية وبدون محاكي.\"",
        "self_check_ar": "هل غطيت شجرة الـ Semantics وإمكانية الوصول والتنقل؟ هل بينت فحص مساحة اللمس 48dp؟ وهل شرحت دور TestNavHostController؟",
        "references_ar": f"- [Testing Compose Layouts](https://developer.android.com/develop/ui/compose/testing) — الدليل الرسمي لجوجل لاختبار واجهات كومبوز.\n- [Compose Accessibility Testing](https://developer.android.com/develop/ui/compose/accessibility#test) — توثيق فحص إمكانية الوصول في كومبوز.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنختبر واجهات Jetpack Compose بالتعامل مباشرة مع شجرة المعاني (Semantics Tree) مش مع بكسلات الشاشة ولا كائنات الـ Views القديمة. بنستخدم أداة `createComposeRule()`؛ بنفحص ظهور النصوص وتفاعل الأزرار بـ `onNodeWithText()` و `performClick()`. وفي إمكانية الوصول (Accessibility)، بنعمل Assert على وجود `contentDescription` للأيقونات، ودمج الكروت المعقدة بـ `mergeDescendants` لقارئ TalkBack، والتأكد إن مساحة اللمس لا تقل عن 48x48dp. أما في التنقل، بنحقن كائن `TestNavHostController` ونتأكد إن الضغط على الأزرار بيغير مسار الـ `currentBackStackEntry` بشكل متزامن وفوري وبدون الحاجة لانتظار أنيميشن الشاشات.",
        "best_answer_ar": "اختبار واجهات Jetpack Compose الحديثة بيعتبر نقلة نوعية في السرعة والموثوقية مقارنة بنظام الـ Views القديم.\n\nالمنهجية الاحترافية بتغطي تلات ركائز أساسية:\nالركيزة الأولى: شجرة المعاني (Semantics Tree)؛ كومبوز مش بترسم عناصر عادية نقدر نمسكها بـ findViewById، بل بتبني شجرة موازية اسمها Semantics Tree بتعبر عن وظيفة كل عنصر. بنستخدم `createComposeRule()` لفحص الواجهة؛ بنعثر على العناصر باللي بيشوفه المستخدم بـ `onNodeWithText(\"Login\")` وننفذ الضغط بـ `performClick()` ونتأكد إن كولباك الحدث اشتغل بنجاح.\n\nالركيزة الثانية: سهولة الوصول (Accessibility)؛ دي خطوة إجبارية في التطبيقات العالمية؛ بنتأكد إن الأيقونات التفاعلية ليها `contentDescription` واضح يقدر يقرأه TalkBack، وإن الكروت المجمعة بتستخدم `mergeDescendants = true` عشان تتقرأ كجملة واحدة مفيدة للكفيف بدل التشتيت، وبنعمل Assert على مساحة اللمس إنها لا تقل عن 48dp بـ `assertTouchBoundsInRootIsEqualTo(48.dp, 48.dp)` لسهولة الضغط.\n\nالركيزة الثالثة: اختبار التنقل (Navigation)؛ أكبر غلطة هي تشغيل المحاكي وانتظار أنيميشن الانتقال بين الشاشات. الأسلوب السينيور هو حقن `TestNavHostController` داخل الـ `NavHost` على الـ JVM؛ بنعمل محاكاة للضغطة، ونتأكد في نفس اللحظة إن `navController.currentBackStackEntry?.destination?.route` اتغير للمسار الجديد، وبكده بنختبر رسمة التنقل بالكامل في أجزاء من الميلي ثانية.",
        "deep_answer_ar": "تحت الكابوت، محرك كومبوز بيولد كائنات `SemanticsNode` أثناء مرحلة قياس ورسم الشاشة في الـ Layout Pass.\nكل Modifier بيحتوي على دالة semantics بيسجل خريطة خصائص اسمها `SemanticsConfiguration` تابعة للـ LayoutNode الأصلي. أداة `createComposeRule` بترتبط بكائن الـ `SemanticsOwner` في جذر الشاشة.\nدوال الفحص زي `onNodeWithText` بتبحث في مصفوفات الـ `SemanticsPropertyKey` (زي Text و Role و ContentDescription) المخزنة في الـ SlotTable، وده السبب اللي بيخلي اختبارات كومبوز تشتغل بسرعة فائقة على الـ JVM بـ Robolectric وبدون الحاجة لمعالج رسومات حقيقي (GPU).\n\nوفيما يخص الـ Accessibility، المحرك بيربط شجرة الـ SemanticsNode بنظام أندرويد عبر `AndroidComposeViewAccessibilityDelegateCompat` اللي بيترجمها لكائنات `AccessibilityNodeInfoCompat` لنظام التشغيل. لما تستخدم `mergeDescendants = true`، المحرك بيمسح النودز الفرعية من شجرة الـ Accessibility ويضم نصوصها في عقدة واحدة مجمعة، وده بيقلل إرهاق مستخدم قارئ الشاشة.\n\nأما بخصوص اختبارات التنقل، كائن `TestNavHostController` بيطبق نفس واجهات الـ NavController لكن مع استبدال محرك الانتقالات بنظام مكدس في الذاكرة (`ArrayDeque`).\nأول ما الكود ينادي `navigate()`، الـ TestNavHostController بيحدث مكدس الـ Backstack فوراً وبشكل متزامن على خيط الفحص وبدون المرور بـ Choreographer VSYNC أو تشغيل أي Transition Animations، وده بيحقق استقراراً بنسبة 100% في الـ CI وبدون أي تذبذب."
    }
}

# ==========================================
# TST-15: How do you reduce flaky UI tests and control scheduling?
# ==========================================
DATA["TST-15"] = {
    "concept_en": """Eliminating flaky UI tests and establishing deterministic execution schedules requires systematically eradicating non-deterministic asynchronous timing, uncoordinated thread concurrency, device environmental variance, and unseeded test fixtures. In automated Android UI testing, flakiness stems from four primary root causes: hardcoded sleep statements (Thread.sleep) guessing asynchronous latency, uncoordinated background coroutines updating UI state out of sync with test assertions, system animations causing touch dispatch misses, and shared state bleed between test runs. Senior engineers resolve this by replacing sleeps with IdlingResource or Compose automatic recomposition synchronization, disabling system animations globally via test orchestration, injecting deterministic TestDispatchers, scoping test fixtures to ephemeral sandboxes, and executing automated flakiness triage runs in continuous integration.""",
    "walkthrough_en": """Eliminating flakiness via IdlingResource and Compose virtual clock control:
```kotlin
// 1. Espresso IdlingResource for legacy background coordination (NO Thread.sleep!)
object OkHttpIdlingResourceRule : TestWatcher() {
    private val resource = OkHttp3IdlingResource.create("OkHttp", OkHttpClientProvider.client)

    override fun starting(description: Description) {
        IdlingRegistry.getInstance().register(resource)
    }

    override fun finished(description: Description) {
        IdlingRegistry.getInstance().unregister(resource)
    }
}

// 2. Compose Test Rule: Synchronizing virtual clock and auto-idling
class FlakyFreeComposeTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun testLoadingTransition_withoutFlakiness() {
        // Compose automatically waits for recomposition, layout, and effects to settle!
        composeTestRule.setContent {
            ProductScreen(viewModel = fakeViewModel)
        }

        // Deterministic synchronization without sleep!
        composeTestRule.waitForIdle()

        // Freeze and manually advance virtual clock for infinite animations
        composeTestRule.mainClock.autoAdvance = false
        composeTestRule.mainClock.advanceTimeBy(500)

        composeTestRule.onNodeWithText("Products Loaded").assertIsDisplayed()
    }
}
```""",
    "short_en": """We eliminate flaky UI tests by targeting root causes: never use Thread.sleep, disable system animations via Gradle test options, and replace hardcoded waits with IdlingResource in Espresso or automatic recomposition synchronization in Compose. We control scheduling by injecting virtual TestDispatchers, controlling Compose's mainClock for animations, isolating databases in memory, and running flakiness quarantine pipelines in CI to detect intermittent failures before merging.""",
    "structured_en": """Eliminating flaky tests is one of the highest-leverage productivity investments in enterprise mobile development because unstable tests destroy team confidence in continuous integration.
The single most prevalent cause of test flakiness is hardcoded timing, such as inserting Thread.sleep(2000) while waiting for network responses or animations.
On congested CI build agents, a two-second sleep is frequently too short, causing random timeout failures.
To achieve absolute determinism, senior engineers implement three fundamental practices.
First, we eliminate arbitrary waits by enforcing event-driven synchronization.
In Espresso, we register IdlingResource implementations on OkHttp connection pools and background coroutines so the test pauses execution until network calls complete.
In Compose, createComposeRule() automatically synchronizes with the Recomposer clock, waiting for all state mutations, layout passes, and effect coroutines to settle before assertions run.
Second, we control scheduling and animations.
We disable system window animations, transition scales, and animator durations across test devices using the Android Test Orchestrator.
For infinite progress bars or complex transitions, we freeze Compose's virtual clock via mainClock.autoAdvance = false and advance time deterministically using advanceTimeBy().
Third, we enforce hermetic isolation by clearing in-memory databases and shared preferences between test runs, preventing polluted state from cascading across the suite.""",
    "deep_senior_en": """Under the hood, flakiness is an entropy problem arising from the decoupling of the test runner thread, the Android main Looper thread, and background coroutine thread pools.
When Espresso executes onNode or onView assertions, it queries IdlingRegistry and platform Looper queues.
If an application launches background coroutines via standard Dispatchers.IO without an IdlingResource bridge, the main thread's MessageQueue reports idle status even while data fetches are still in flight.
The test runner immediately executes assertions against stale UI state and fails.
In Compose, synchronization is natively built into the Snapshot state engine.
ComposeTestRule hooks into the Snapshot.registerApplyObserver pipeline and the root Recomposer.
When a state value commits, the Recomposer flags an internal invalidation bitmask.
ComposeTestRule.waitForIdle() enters a spinning synchronization loop that processes Choreographer frames, executes measure and layout passes, and resumes LaunchedEffect coroutines until the Recomposer state machine enters the Idle state.
If an infinite animation—such as an indeterminate CircularProgressIndicator—is rendering, it continuously invalidates the Choreographer, which would cause waitForIdle() to hang indefinitely.
To neutralize this, senior engineers pause the Compose mainClock: setting autoAdvance to false decouples the test from the host Choreographer VSYNC pulses, allowing developers to step through frame deltas with millisecond precision.
In CI environments, teams combine Android Test Orchestrator (which runs each test in a sandboxed, freshly booted instrumentation process) with Flaky Test Quarantine pipelines to run suspicious tests 50 times in isolation before permitting code to merge.""",
    "meta_ar": {
        "id": "TST-15",
        "questionAr": "كيف تقلل من الاختبارات المتقلبة (Flaky UI Tests) وتتحكم في جدولة العمليات في أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تشخيص وحل مشكلة الاختبارات المتقلبة (Flaky Tests)، ومنع استخدام `Thread.sleep`، واستخدام أدوات المزامنة (IdlingResource و Compose waitForIdle)، والتحكم في ساعة الأنيميشن بـ `mainClock`، وإعدادات الـ CI المستقرة.",
        "why_it_matters_ar": "الاختبارات المتقلبة تفقد الفريق الثقة في الـ CI وتجعل المطورين يتجاهلون رسائل الفشل، مما يؤدي لتمرير أخطاء حقيقية للإنتاج وتأخر تسليم الميزات.",
        "worked_example_ar": "التحكم في مزامنة الواجهة وساعة الأنيميشن بدون Thread.sleep:\n```kotlin\n// إيقاف التقدم التلقائي لساعة الأنيميشن لتجنب التعليق اللانهائي\nrule.mainClock.autoAdvance = false\nrule.waitForIdle()\nrule.mainClock.advanceTimeBy(500) // تقديم دقيق للأنيميشن بـ 500ms\nrule.onNodeWithText(\"Loaded\").assertIsDisplayed()\n```",
        "trade_offs_ar": "ضبط المزامنة بدقة وإيقاف الأنيميشن يتطلب فهماً عميقاً لآليات رندرة الواجهة، لكنه يحول خط الـ CI من بيئة عشوائية تفشل يومياً إلى بيئة مستقرة بنسبة 100%.",
        "failure_modes_ar": "وضع `Thread.sleep(3000)` لانتظار تحميل الشاشة؛ لأن سرعة أجهزة الـ CI تتغير، فالـ 3 ثواني قد تكون كافية محلياً لكنها تفشل على الخادم البطيء.",
        "production_perspective_ar": "في المشروعات الكبيرة، نمنع دمج أي PR يحتوي على `Thread.sleep` بقواعد فحص صارمة، ونعطل أنيميشن الأجهزة في الـ CI بأمر `adb shell settings put global window_animation_scale 0`.",
        "how_to_answer_ar": "حدد أسباب الـ Flakiness الرئيسية: الـ Thread.sleep العشوائي، والأنيميشن، وعدم مزامنة الكوروتينات، وتلوث الحالة بين الاختبارات. ثم اشرح الحلول الهندسية: المزامنة الآلية بـ Compose waitForIdle و IdlingResource، وإيقاف أنيميشن النظام، والتحكم في ساعة الكومبوز بـ `mainClock.autoAdvance = false`، وعزل بيئة كل اختبار بـ Test Orchestrator.",
        "talking_points_ar": "حظر Thread.sleep نهائياً، والمزامنة الذكية بـ IdlingResource، ومزامنة Compose التلقائية وساعة mainClock، وإيقاف أنيميشن النظام في الـ CI، واستخدام Android Test Orchestrator.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يعلق اختبار Compose أحياناً في `waitForIdle` للأبد عند وجود CircularProgressIndicator؟\"\n  **المرشح:** \"لأن مؤشر التحميل بيحتوي على Infinite Animation بتطلب إعادة رندرة في كل فريم VSYNC، فالمحرك مبيوصلش لحالة الـ Idle أبداً. الحل هو إيقاف الساعة بـ `mainClock.autoAdvance = false` وتقديم الوقت يدوياً.\"\n\n- **المحاور:** \"ما هي فائدة استخدام Android Test Orchestrator في الـ CI؟\"\n  **المرشح:** \"إنه بيشغل كل اختبار في Process أندرويد مستقلة تماماً بـ APK نظيف، فبيمنع أي تسريب للذاكرة أو الـ Static State بين التيستات المتتالية.\"",
        "self_check_ar": "هل حددت أسباب تذبذب الاختبارات؟ هل حذرت من Thread.sleep؟ وهل شرحت التحكم في mainClock والمزامنة بـ IdlingResource؟",
        "references_ar": f"- [Flaky Tests in Android](https://developer.android.com/training/testing/fundamentals#flaky-tests) — توثيق جوجل الرسمي لمكافحة تذبذب الاختبارات.\n- [Compose UI Test Clock](https://developer.android.com/develop/ui/compose/testing#controlling-the-clock) — دليل التحكم في ساعة الاختبار في كومبوز.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنتخلص من الاختبارات المتقلبة (Flaky Tests) بالقضاء على أسبابها الجذرية: أولاً بنمنع تماماً استخدام `Thread.sleep()` العشوائي ونستبدله بالمزامنة الحدثية عبر `IdlingResource` في Espresso أو المزامنة التلقائية المدمجة في Compose بـ `waitForIdle()`. ثانياً بنعطل أنيميشن النظام في أجهزة الـ CI بالكامل بـ `adb` لتفادي سقوط اللمسات. ثالثاً بنتحكم في ساعة الرندرة في Compose بـ `mainClock.autoAdvance = false` لتخطي مؤشرات التحميل والأنيميشن اللانهائي بدون تعليق. ورابعاً بنعزل بيئة كل اختبار بـ `Android Test Orchestrator` لضمان عدم تسريب الذاكرة أو البيانات بين الاختبارات.",
        "best_answer_ar": "القضاء على الاختبارات المتقلبة (Flaky UI Tests) هو أهم استثمار لضمان سرعة وثقة فريق التطوير في خطوط الـ CI/CD.\n\nالمنهجية الهندسية الصارمة بتعتمد على أربع ركائز:\nالركيزة الأولى: حظر الـ `Thread.sleep` نهائياً؛ النوم الثابت هو العدو الأول للاستقرار؛ لأن جهاز الـ CI لو مضغوط، التأخير المكتوب مش هيكفي والتيست هيفشل عشوائياً. بنستبدله بالمزامنة الذكية: في Espresso بنسجل `IdlingResource` على مكتبة OkHttp وخيوط الكوروتينات عشان التيست يستنى انتهاء الشبكة بدقة، وفي Jetpack Compose، ميزة `createComposeRule()` بتوفر مزامنة آلية كاملة مع محرك الـ Recomposition.\n\nالركيزة الثانية: التحكم في ساعة الأنيميشن؛ وجود أنيميشن لا نهائي زي `CircularProgressIndicator` بيخلي Compose تطلب فريمات VSYNC مستمرة، فالتيست يعلق في `waitForIdle`. بنحل ده بتجميد الساعة: `composeRule.mainClock.autoAdvance = false` وتقديم الوقت يدوياً بـ `advanceTimeBy()` لفحص الحالة بدقة.\n\nالركيزة الثالثة: إيقاف أنيميشن نظام أندرويد؛ في الـ CI بنعطل `window_animation_scale` و `transition_animation_scale` بالكامل عبر إعدادات الـ Gradle والمحاكي عشان الشاشات تفتح في صفر ميلي ثانية بدون تداخل حركات الانتقال مع النقرات.\n\nالركيزة الرابعة: العزل التام بـ `Android Test Orchestrator`؛ الأداة دي بتشغل كل Test Method في Process منفصلة وجديدة كلياً، فبتضمن إن كاش الداتابيز أو المتغيرات الساكنة متتسربش من اختبار للتاني وتسبب فشل وهمي.",
        "deep_answer_ar": "تحت الكابوت، ظاهرة الـ Flakiness بتنشأ بسبب عدم التزامن بين خيط الاختبار وخيط الـ Main Looper التابع للأكتيفيتي وخيوط الكوروتينات في الـ Background Thread Pool.\nفي Espresso القديم، المحرك بيراقب طابور رسائل الـ `Looper.getMainLooper()` فقط. فلو أطلقت كوروتين بـ `Dispatchers.IO` لجلب بيانات من الشبكة، خيط الـ Main Looper هيكون فاضي؛ Espresso بتعتقد خطأً إن التطبيق مستقر، فبتفحص الواجهة فوراً قبل ما بيانات الشبكة توصل، وبيرمي فحص النص خطأ فوري!\n\nفي Jetpack Compose، الرنتايم بيعالج المشكلة دي جذرياً من خلال الارتباط بنظام الـ Snapshots.\nأداة `ComposeTestRule` بتسجل مراقب عبر `Snapshot.registerApplyObserver` ومحرك الـ Recomposer.\nأول ما قيمة تتغير في الـ State، المحرك بيسجل علم عدم استقرار (Invalidation Bitmask). دالة `waitForIdle()` بتدخل في حلقة فحص متزامنة بتنتظر تصفية كل رسائل الـ Choreographer، وانتهاء مراحل الـ Measure والـ Layout، واكتمال كل كوروتينات الـ `LaunchedEffect` داخل شجرة الرندرة.\n\nأما عند وجود أنيميشن مستمر، فكل نبضة VSYNC بتطلب فريم جديد؛ تجميد الساعة عبر `mainClock.autoAdvance = false` بيفصل بيئة الاختبار عن نبضات الـ VSYNC الحقيقية في عتاد الشاشة، وبيسمح للمطور بتقديم عقارب الساعة الافتراضية خطوة بخطوة بالمللي ثانية.\nودمج ده مع خط أنابيب الـ CI اللي بيشغل كود الاختبار 50 مرة في بيئة عزل (Quarantine Pipeline) قبل قبول الكود بيضمن قضاء تام على الاختبارات المتقلبة في كبرى التطبيقات العالمية."
    }
}

# ==========================================
# TST-16: What should be unit-tested versus verified with an emulator/device?
# ==========================================
DATA["TST-16"] = {
    "concept_en": """Establishing a rigorous architectural boundary between local JVM unit testing and on-device instrumentation testing dictates the speed, fidelity, and operational cost of an Android engineering pipeline. Approximately 70 to 80 percent of application logic should be unit-tested purely on the host JVM in milliseconds without booting Android runtimes. This includes ViewModels, UseCases, business domain rules, mapping algorithms, offline caching logic using MockWebServer, and isolated Compose UI rendering via Robolectric. Conversely, on-device or emulator testing (comprising 15 to 20 percent) is strictly reserved for behaviors inextricably bound to the physical Android OS and ART runtime: complex SQLite Room database schema migrations, hardware biometric authentication via Android Keystore, native C++ NDK interop, WorkManager background constraints, CameraX hardware streams, and release-candidate macrobenchmarks.""",
    "walkthrough_en": """Contrasting local JVM domain testing with on-device biometric Keystore verification:
```kotlin
// 1. JVM Unit Test in src/test/ (Pure business validation executing in ~5ms)
class CartPricingUseCaseTest {
    @Test
    fun calculateTotal_appliesVatAndDiscountDeterministically() {
        val useCase = CalculateCartTotalUseCase()
        val total = useCase(items = listOf(CartItem(price = 100.0, qty = 2)), discount = 20.0)
        // 200 - 20 = 180 + 14% VAT = 205.2
        assertEquals(205.2, total, 0.001)
    }
}

// 2. Instrumented Test in src/androidTest/ (Strictly requires real Android Keystore hardware!)
@RunWith(AndroidJUnit4::class)
class CryptographyManagerIntegrationTest {
    private lateinit var cryptoManager: CryptographyManager

    @Before
    fun setup() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        cryptoManager = CryptographyManagerImpl(context)
    }

    @Test
    fun encryptAndDecryptToken_usingHardwareAndroidKeyStore() {
        val rawToken = "super_secret_jwt_token_payload"
        // Interacts with Android KeyStore provider inside hardware TEE / StrongBox!
        val encryptedData = cryptoManager.encrypt(alias = "auth_key", data = rawToken)
        val decryptedData = cryptoManager.decrypt(alias = "auth_key", encryptedData = encryptedData)

        assertEquals(rawToken, decryptedData)
    }
}
```""",
    "short_en": """We divide testing strictly by execution environment. Fast JVM unit tests in src/test cover 70-80% of code: ViewModels, UseCases, business logic, mapping, and repositories with MockWebServer. Instrumented tests in src/androidTest cover 15-20% and are reserved strictly for platform-bound code: Room database migrations, Android Keystore encryption, hardware sensors, WorkManager system constraints, and release Macrobenchmarks that cannot execute accurately on the desktop JVM.""",
    "structured_en": """Striking the optimal balance between JVM unit tests and on-device emulator tests is the hallmark of a senior Android engineer.
The governing design principle is to run every test on the cheapest, fastest platform possible that still yields decisive confidence.
On the local JVM in src/test, we execute the vast majority of our test suite—roughly 70 to 80 percent.
Because JVM tests bypass Android OS boot cycles and run in milliseconds, they are ideal for testing domain UseCases, mathematical pricing logic, ViewModel state emissions with Turbine, data mapping, and repository network synchronization with MockWebServer.
Furthermore, using Robolectric or modern desktop Compose tooling, teams can even verify UI semantic layout and screenshot golden images directly on the JVM.
Conversely, on-device or emulator tests in src/androidTest are expensive, slow, and compute-intensive.
We reserve this tier strictly for functionality that directly interfaces with the compiled Android Runtime (ART) and native platform subsystems.
This includes verifying complex Room database migrations across historic SQLite versions, testing hardware biometric authentication backed by the Android Keystore and Secure Element, verifying background WorkManager scheduling under system battery-saver constraints, and executing Macrobenchmark startup and frame-timing metrics before production release.""",
    "deep_senior_en": """Under the hood, the boundary between JVM and device testing is defined by runtime bytecode execution, native framework bridges, and hardware abstraction layers.
Local JVM tests compile against mockable-android.jar and run inside a desktop HotSpot or OpenJDK virtual machine.
Because desktop JVMs lack Android's native Linux zygote process, Binder IPC drivers, and hardware security modules, any attempt to test Android Keystore or SQLite file transactions requires either mocking or third-party shadows.
However, using shadows for complex hardware features introduces false confidence; Robolectric cannot replicate the exact cryptographic behavior of a hardware Trusted Execution Environment (TEE) or StrongBox keymaster.
Therefore, cryptographic key generation, biometric cipher initialization, and Room schema migrations must be validated inside the real Android Runtime (ART) via an emulator or physical device.
In src/androidTest, the test runner compiles code into Dalvik Executable (DEX) format and executes inside a real Linux process initialized by the Zygote daemon.
This guarantees genuine interaction with the Linux kernel, native C++ libsqlite3 engines, and hardware drivers.
Conversely, running pure business logic on an emulator wastes immense CI compute resources: booting an emulator takes minutes and running a suite takes ten times longer than on the JVM.
Senior engineers enforce an architectural firewall: if code contains pure business algorithms or presentation state transitions, it must be testable on the JVM via dependency injection; device execution is reserved strictly for platform integration validation.""",
    "meta_ar": {
        "id": "TST-16",
        "questionAr": "ما الذي يجب اختباره كوحدة (Unit Test) وما الذي يجب التحقق منه عبر محاكي أو جهاز حقيقي؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على وضع حدود معمارية صارمة بين بيئة الـ JVM المحلية وبيئة أجهزة أندرويد الحقيقية، وتحسين تكلفة وسرعة الـ CI، واختيار بيئة الفحص المناسبة لكل ميزة برمجية.",
        "why_it_matters_ar": "تشغيل اختبارات منطق الأعمال على المحاكي يهدر ساعات في الـ CI ويبطئ دورة التطوير، بينما محاولة اختبار التشفير والعتاد على JVM تعطي ثقة زائفة وتسبب كراشات في الإنتاج.",
        "worked_example_ar": "فصل منطق الأعمال على JVM عن فحص عتاد الأمان على جهاز حقيقي:\n```kotlin\n// 1. JVM Unit Test (ينفذ في 5ms على الكمبيوتر): حساب الأسعار والخصومات\n@Test fun testCart() = assertEquals(180.0, CartCalculator.applyDiscount(200.0, 10))\n// 2. Instrumented Test (يتطلب جهاز حقيقي): التشفير بـ Android Keystore و TEE\n@Test fun testKeystore() = assertEquals(token, cryptoManager.decrypt(cryptoManager.encrypt(token)))\n```",
        "trade_offs_ar": "اختبارات الـ JVM سريعة ورخيصة جداً لكنها لا تفحص نظام أندرويد الفعلي، واختبارات الأجهزة واقعية بنسبة 100% لكنها بطيئة ومكلفة في الـ CI.",
        "failure_modes_ar": "كتابة اختبارات الـ ViewModels والـ UseCases داخل مجلد `src/androidTest` مما يرفع زمن بناء الـ CI لعشرات الدقائق بدون أي فائدة إضافية.",
        "production_perspective_ar": "في المشروعات الكبيرة، نلزم المطورين بإنشاء 80% من الاختبارات في `src/test` على الـ JVM، ونحصر `src/androidTest` في اختبارات ترقيات Room والتشفير وقياسات الأداء بـ Macrobenchmark.",
        "how_to_answer_ar": "وضح المعيار الحاكم: كل ما يمكن اختباره على الـ JVM يجب أن يختبر هناك لرخص التكلفة والسرعة، وحدد ما يختبر على JVM (ViewModels, UseCases, Mappers, Repositories with MockWebServer, Compose semantics بـ Robolectric)، وما يحجز للجهاز الحقيقي (ترقيات Room، وتشفير Android Keystore، ومستشعرات العتاد، وقيود WorkManager، ومقاييس الأداء Macrobenchmark).",
        "talking_points_ar": "المفاضلة بين بيئة JVM وبيئة ART، وسرعة الـ CI وتكلفة البناء، وما يختبر على JVM، وما يختبر حتماً على الأجهزة الحقيقية (Keystore, Room migrations, Hardware sensors, Macrobenchmark).",
        "follow_ups_ar": "- **المحاور:** \"لماذا يستحيل اختبار التشفير بـ Android Keystore بشكل موثوق على الـ JVM؟\"\n  **المرشح:** \"لأن Keystore بيعتمد على عتاد أمني حقيقي داخل الهاتف زي شريحة TEE أو StrongBox، ومكتبة JVM العادية معندهاش الوصول ده، وأي محاكاة وهمية بتكون غير مطابقة للواقع.\"\n\n- **المحاور:** \"هل يمكن اختبار شاشات Jetpack Compose على الـ JVM بدون محاكي؟\"\n  **المرشح:** \"نعم، باستخدام مكتبة Robolectric أو أدوات فحص Compose الحديثة؛ بنقدر نختبر شجرة الـ Semantics والتنقل ونلتقط Screenshot tests بالكامل على الـ JVM في ثوانٍ معدودة.\"",
        "self_check_ar": "هل وضحت الفارق المعماري بين البيئتين؟ هل حددت بوضوح ما يختبر على JVM وما يختبر على المحاكي؟ وهل شرحت أثر ذلك على أداء الـ CI؟",
        "references_ar": f"- [Android Testing Strategy](https://developer.android.com/training/testing/fundamentals#what-to-test) — دليل جوجل الرسمي لتحديد استراتيجية وبيئة الاختبار.\n- [Macrobenchmark and Performance Testing](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) — توثيق اختبارات الأداء على الأجهزة الحقيقية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بنفصل الاختبارات بمعيار هندسي صارم قائم على البيئة والسرعة: على الـ `JVM` المحلي في مجلد `src/test` بنكتب من 70% إلى 80% من الاختبارات؛ بنختبر كل الـ ViewModels والـ UseCases ومنطق الأعمال وحسابات الأسعار والـ Mappers واختبارات الـ Repository بـ MockWebServer وحتى شاشات Compose بـ Robolectric لسرعتها الفائقة في ثوانٍ معدودة. أما على `المحاكي أو الجهاز الحقيقي` في `src/androidTest` (15% إلى 20%)، فبنقصره حصرياً على الميزات المربوطة بنظام وعتاد أندرويد الفعلي: ترقيات قواعد بيانات Room المعقدة، والتشفير بشريحة الأمان `Android Keystore`، وحساسات البصمة والكاميرا، وقيود بطارية `WorkManager`، واختبارات أداء التطبيق بـ Macrobenchmark.",
        "best_answer_ar": "تحديد الحدود الفاصلة بين ما يختبر على الـ JVM وما يختبر على المحاكي هو علامة النضج المعماري الأولى لمهندس أندرويد السينيور، وهدفه تحقيق أقصى موثوقية بأقل وقت وتكلفة للـ CI.\n\nالقاعدة الذهبية هي: 'أي كود ينفع يختبر على الـ JVM، لازم يختبر على الـ JVM فوراً'.\nفي مجلد `src/test` على الـ JVM، بنختبر الأغلبية الساحقة من كود التطبيق:\nأولاً: منطق الأعمال الصافي في الـ UseCases والـ Domain Entities والتحويلات الحسابية.\nثانياً: حالات واجهة المستخدم في الـ ViewModels وتدفقات الـ StateFlow بـ Turbine.\nثالثاً: طبقة البيانات والـ Repositories باستخدام MockWebServer لفحص اتصالات الشبكة وسياسات الكاش.\nرابعاً: واجهات Jetpack Compose؛ بنقدر نفحص شجرة الـ Semantics ونعمل اختبارات لقطات الشاشة (Screenshot Tests) على الـ JVM في ثوانٍ معدودة بفضل Robolectric.\n\nأما في مجلد `src/androidTest` على المحاكي أو الجهاز الحقيقي، فبنحجزه حصرياً للأشياء التي يستحيل محاكاتها خارج نظام أندرويد ومحرك ART:\nأولاً: ترقيات قواعد بيانات Room الكبيرة للتأكد من عدم ضياع بيانات العملاء على محرك SQLite الحقيقي.\nثانياً: التشفير والأمان المعتمد على عتاد الجهاز الفعلي، زي شريحة الـ StrongBox والـ Hardware-backed Keystore والبصمة الحيوية.\nثالثاً: قيود النظام في الخلفية مع الـ WorkManager وإدارة استهلاك البطارية ووضع الـ Doze Mode.\nرابعاً: اختبارات الأداء والسرعة بـ Macrobenchmark لقياس زمن فتح التطبيق الحقيقي واستهلاك الفريمات، وبكده بنضمن خط بناء سريع ومستقر بنسبة 100%.",
        "deep_answer_ar": "تحت الكابوت، الفارق الجذري بين بيئة الـ JVM وبيئة الجهاز الحقيقي بيكمن في نوع الـ Bytecode المنفذ، وطبقة الـ HAL (Hardware Abstraction Layer)، ونظام أذونات النواة (Linux Kernel).\n\nاختبارات الـ JVM بتشتغل داخل الـ Host Java Virtual Machine (زي OpenJDK)، وبتترجم ضد ملف `mockable-android.jar`. البيئة دي سريعة جداً لأنها بتشتغل مباشرة على معالج الكمبيوتر المكتبي بدون محاكاة، لكنها تفتقر لوجود كود الـ Zygote، ومحركات الـ Binder IPC، وشريحة الأمان (Secure Element).\nلو حاولت تختبر كود بيستخدم `KeyGenParameterSpec` لتوليد مفتاح تشفير في الـ Android Keystore على الـ JVM، الاختبار هيفشل فوراً أو هيعتمد على Shadow غير حقيقي لا يطابق قيود الـ TEE الحقيقية في هواتف أندرويد، وده بيعطي ثقة وهمية مضللة.\n\nبينما في بيئة `src/androidTest`، كود الاختبار بيترجم لـ Dalvik Executable (DEX) وبيشتغل داخل نظام أندرويد حقيقي تحت إدارة محرك ART.\nالـ Process بتحصل على Context حقيقي، وتتواصل مع خدمات النظام الأصلية في C++، وتتعامل مع شريحة الـ Titan M أو الـ TEE في الهاتف لتشفير البيانات، وتنفذ عمليات الـ SQLite على نظام ملفات حقيقي بـ ext4 أو f2fs.\n\nلكن تشغيل محاكي في الـ CI بيستهلك دقائق للإقلاع وذاكرة ضخمة؛ عشان كده، المهندس السينيور بيمنع كتابة اختبارات منطق الأعمال أو الـ ViewModels في مجلد `src/androidTest`، ويصمم الكود بحقن التبعيات عشان يشتغل 80% منه على الـ JVM في أجزاء من الثانية، وتوفير المحاكيات فقط لما يفرضه العتاد ونظام التشغيل."
    }
}

def main():
    print("Elevating 8 questions in TST (TST-09 to TST-16)...")
    all_valid = True
    for qid, d in sorted(DATA.items()):
        if d is None:
            continue
        en_s = len(d["short_en"].split())
        en_st = len(d["structured_en"].split())
        en_d = len(d["deep_senior_en"].split())
        ar_q = len(d["meta_ar"]["quick_answer_ar"].split())
        ar_b = len(d["meta_ar"]["best_answer_ar"].split())
        ar_d = len(d["meta_ar"]["deep_answer_ar"].split())
        print(f"{qid}: en_s={en_s}, en_st={en_st}, en_d={en_d} | ar_q={ar_q}, ar_b={ar_b}, ar_d={ar_d}")

        if not (35 <= en_s <= 110):
            print(f"  ❌ {qid} en_short invalid: {en_s}")
            all_valid = False
        if not (100 <= en_st <= 280):
            print(f"  ❌ {qid} en_structured invalid: {en_st}")
            all_valid = False
        if not (200 <= en_d <= 650):
            print(f"  ❌ {qid} en_deep invalid: {en_d}")
            all_valid = False
        if not (35 <= ar_q <= 110):
            print(f"  ❌ {qid} ar_quick invalid: {ar_q}")
            all_valid = False
        if not (90 <= ar_b <= 280):
            print(f"  ❌ {qid} ar_best invalid: {ar_b}")
            all_valid = False
        if not (180 <= ar_d <= 650):
            print(f"  ❌ {qid} ar_deep invalid: {ar_d}")
            all_valid = False

    if not all_valid:
        print("\nPre-validation word count checks failed! Fix counts before updating files.")
        sys.exit(1)

    print("\nPre-validation word count checks passed! Updating canonical questions...")

    topic_meta = {}
    for qid, d in sorted(DATA.items()):
        if d is None:
            continue
        ee.update_canonical_question(
            qid=qid,
            concept_en=d["concept_en"],
            walkthrough_en=d["walkthrough_en"],
            short_en=d["short_en"],
            structured_en=d["structured_en"],
            deep_senior_en=d["deep_senior_en"]
        )
        topic_meta[qid] = d["meta_ar"]

    ee.save_topic_metadata("tst_09_16", topic_meta)
    ee.merge_all_metadata()

    # Validate each question
    for qid in sorted(DATA.keys()):
        if DATA[qid] is None:
            continue
        ee.validate_question(qid)

    print("\nAll 8 TST questions (TST-09 to TST-16) successfully elevated and passed validation!")

if __name__ == "__main__":
    main()

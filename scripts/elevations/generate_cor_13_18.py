#!/usr/bin/env python3
"""Generator for COR-13 through COR-18 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "cor.json"

COR_13_18 = [
    {
        "id": "COR-13",
        "arabic_explanation": (
            "سلوك الأب والإخوة عند فشل أحد الأبناء (Child Coroutine Failure) بيعتمد بنسبة 100% على **نوع الـ Parent Job**:\n\n"
            "1. في حالة الـ Standard Job (أو داخل `coroutineScope`):\n"
            "   - **تسلسل الانهيار (Cascading Teardown):**\n"
            "     1. الابن بيرمي Uncaught Exception.\n"
            "     2. الابن يرسل إشعار إلغاء للأب (`parent.childCancelled(cause)`).\n"
            "     3. الأب يلغي نفسه فوراً.\n"
            "     4. الأب يرسل إشارات إلغاء لجميع الأبناء الآخرين (Siblings)، ويتم إلغاؤهم بـ `CancellationException`.\n"
            "     5. الأب يجمع أي Exceptions حدثت في الإخوة كـ Suppressed Exceptions ويرمي الاستثناء الأصلي للأعلى.\n"
            "   - الهدف: الحفاظ على اتساق البيانات (Consistency)؛ لا نترك عمليات نصف مكتملة في الخلفية.\n\n"
            "2. في حالة الـ `SupervisorJob` (أو داخل `supervisorScope`):\n"
            "   - **عزل الفشل (Failure Isolation):**\n"
            "     1. الابن يرمي Exception.\n"
            "     2. الأب (Supervisor) يتجاهل الإلغاء ويظل حياً ونشطاً (`isActive = true`).\n"
            "     3. باقي الإخوة (Siblings) يستمرون في العمل بدون أي تأثر.\n"
            "     4. الابن الفاشل فقط هو الذي ينتهي، واستثناؤه يتم توجيهه للـ `CoroutineExceptionHandler` الخاص به أو إلى الـ Thread Uncaught Exception Handler."
        ),
        "practical_walkthrough": (
            "في شاشة عرض تفاصيل الطلب (Order Details):\n"
            "- بنطلب 3 خدمات: 1. معلومات الشحن، 2. معلومات الفاتورة، 3. توصيات منتجات إضافية.\n"
            "- **تحليل السيناريو المعماري:**\n"
            "  * الشحن والفاتورة: عمليتان حرجتان؛ لو فشل الشحن، لا فائدة من الفاتورة. هنا نستخدم `coroutineScope` العادي لكي يلغي العملية الأخرى فوراً عند الفشل (Fail-Fast).\n"
            "  * توصيات المنتجات: خدمة غير حرجة؛ لو فشلت لا نريد إلغاء الشحن والفاتورة. هنا نضعها داخل `supervisorScope` أو نفصلها لكي لا يؤثر فشلها على العمليات الحيوية."
        ),
        "quick_answer": "In a standard Job hierarchy, if a child coroutine fails with an uncaught exception, it cancels its parent, which immediately cancels all other siblings (fail-fast). In a SupervisorJob or supervisorScope, the failure is isolated: the parent remains active and siblings continue executing undisturbed.",
        "best_answer": (
            "What happens to the parent and siblings depends entirely on whether the parent is a standard Job or a SupervisorJob.\n\n"
            "In a standard Job hierarchy—such as inside a standard `coroutineScope`—the behavior is 'fail-fast'. When a child coroutine encounters an uncaught exception (other than CancellationException), it notifies its parent. The parent cancels itself, and that cancellation cascades downwards to immediately cancel all sibling coroutines. This prevents partial state corruption, ensuring that if one critical step in an operation fails, related parallel tasks are cleaned up.\n\n"
            "In contrast, under a `SupervisorJob` or `supervisorScope`, child failure is strictly isolated. The supervisor parent does not cancel itself when a child fails, and active sibling coroutines continue running to completion. The failed child terminates independently, and its exception must be handled locally or by a CoroutineExceptionHandler attached to that child."
        ),
        "deep_answer": (
            "At the internal implementation level, when a child throws an unhandled exception, it calls `parent.childCancelled(e)`. "
            "A standard `JobSupport` parent returns `true` to acknowledge the cancellation, transitions its state to Cancelling, and iterates through its `NodeList` of child handles, calling `child.cancel(CancellationException(cause))` on every active child.\n\n"
            "If another sibling also throws an exception while being cancelled, the parent attaches that second exception as a suppressed exception (`Throwable.addSuppressed()`) to the root cause, ensuring that no diagnostic failure information is lost in stack traces.\n\n"
            "In Android architecture, recognizing this distinction determines whether you use `coroutineScope` or `supervisorScope`. If parallel sub-tasks are interdependent (e.g., merging two API responses into a single combined UI entity), use `coroutineScope`. If the sub-tasks are independent UI components (e.g., separate dashboard cards), use `supervisorScope` so one failed widget doesn't blank out the entire screen."
        ),
        "follow_ups": [
            {
                "interviewer": "Does a child failing with `CancellationException` cancel its parent or siblings?",
                "answer": "No! `CancellationException` is special. It signifies normal, cooperative task termination. When a child throws `CancellationException`, it terminates itself without notifying the parent as an error, so the parent and sibling coroutines continue running normally."
            },
            {
                "interviewer": "If an `async` child fails inside `coroutineScope`, does it cancel siblings before `await()` is called?",
                "answer": "Yes! Even if you never call `await()`, an uncaught exception in an `async` child inside a standard `coroutineScope` immediately cancels the parent scope and all sibling coroutines."
            },
            {
                "interviewer": "How do you inspect suppressed exceptions from cancelled siblings?",
                "answer": "When catching the parent's exception, you can inspect `exception.suppressed` or `exception.suppressedExceptions` array, which contains any secondary exceptions thrown by siblings during their cancellation unwinding."
            }
        ]
    },
    {
        "id": "COR-14",
        "arabic_explanation": (
            "الـ `CoroutineExceptionHandler` (CEH) هو من أكثر الأدوات التي يساء فهمها في Kotlin Coroutines:\n\n"
            "1. متى يعمل الـ `CoroutineExceptionHandler`؟\n"
            "   - يعمل **فقط** كـ **Last-Resort Global Catch Block** (ملاذ أخير) للتعامل مع الـ Uncaught Exceptions.\n"
            "   - يعمل **فقط** إذا كان ملحقاً بـ **Root Coroutine** (أي Coroutine يتم إطلاقها مباشرة من Scope، زي `scope.launch(ceh)`).\n"
            "   - يعمل فقط مع `launch`؛ ولا يعمل أبداً مع `async` لأن `async` تغلف استثناءها داخل كائن `Deferred`!\n\n"
            "2. أين لا يساعد الـ CEH ولا يعمل إطلاقاً (Where it does NOT help)?\n"
            "   - **داخل Child Coroutines:** لو وضعت CEH على ابن داخل `coroutineScope`، فلن يُستدعى أبداً! لأن الابن يصعد الاستثناء لأبيه فوراً.\n"
            "   - **مع `async`:** استثناءات `async` لا تذهب للـ CEH؛ هي تنتظر حتى يتم استدعاء `await()`.\n"
            "   - **للتعافي من الخطأ (Error Recovery):** الـ CEH لا يمكنه إعادة تشغيل الـ Coroutine أو إخفاء الخطأ؛ عند وصول الاستثناء للـ CEH، تكون الـ Coroutine قد ماتت بالفعل وانتهت!\n"
            "   - وظيفته الصحيحة الوحيدة: تسجيل الخطأ للـ Crashlytics، أو إظهار رسالة عامة للمستخدم، وليس استعادة مسار العمل."
        ),
        "practical_walkthrough": (
            "توضيح عملي للفرق بين المكان الصحيح والخاطئ لـ CEH:\n"
            "```kotlin\n"
            "val handler = CoroutineExceptionHandler { _, exception ->\n"
            "    Log.e(\"App\", \"Uncaught exception: $exception\")\n"
            "}\n"
            "\n"
            "// ✅ يعمل بنجاح: ملحق بـ Root Coroutine مستخدمة launch:\n"
            "val scope = CoroutineScope(SupervisorJob() + handler)\n"
            "scope.launch {\n"
            "    throw RuntimeException(\"Root failed!\") // سيتم التقاطه في handler\n"
            "}\n"
            "\n"
            "// ❌ لن يعمل إطلاقاً (فخ شائع):\n"
            "scope.launch { // Root\n"
            "    launch(handler) { // Child! الـ handler هنا سيتم تجاهله تماماً!\n"
            "        throw RuntimeException(\"Child failed!\") // يصعد للـ Root ويتجاهل handler الابن\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "CoroutineExceptionHandler only catches uncaught exceptions in root coroutines launched with 'launch'. It does not catch exceptions in child coroutines (which delegate to their parent), it does not catch exceptions in 'async' (which encapsulate errors until await), and it cannot recover from failures—it only logs or reports them after the coroutine has already terminated.",
        "best_answer": (
            "A `CoroutineExceptionHandler` (CEH) is purely a last-resort error logging and global reporting mechanism, not a general error recovery tool.\n\n"
            "It only triggers under strict conditions: 1) It must be installed on a **root coroutine** or scope; and 2) the coroutine must be launched via `launch`. If an unhandled exception reaches the root of the hierarchy, the CEH executes its callback, typically used to log breadcrumbs to Crashlytics or show a generic error toast.\n\n"
            "Where it does NOT help: First, it has zero effect when attached to child coroutines. A child coroutine always delegates unhandled exceptions upward to its parent, ignoring its own CEH. Second, it does not catch exceptions from `async` coroutines, which encapsulate errors inside the `Deferred` until `await()` is called. Third, it cannot recover or resume execution—by the time CEH runs, the coroutine has already crashed and unwound."
        ),
        "deep_answer": (
            "Under the hood, exception handling in structured concurrency operates through a hierarchical delegation chain. When a child coroutine throws an unhandled exception, it checks if it has a parent. If a parent Job exists, the child passes the exception to the parent via `parent.childCancelled(cause)` and terminates. It completely bypasses its own context's `CoroutineExceptionHandler`.\n\n"
            "Only when the exception reaches the root `Job` (a Job with no parent), does the coroutine machinery check the root context for a `CoroutineExceptionHandler`. If present, it invokes `handleException(context, exception)`. If no CEH is found in the root context, it delegates to the JVM's `Thread.currentThread().uncaughtExceptionHandler`, which results in a fatal Android app crash.\n\n"
            "In production architecture, CEH should never replace standard `try-catch` blocks or domain Result wrapping in repositories and ViewModels. It should only be configured once on top-level scopes (like custom application-level scopes) as a safety net against unexpected runtime crashes."
        ),
        "follow_ups": [
            {
                "interviewer": "Why does attaching CEH to `async` not catch the exception?",
                "answer": "Because `async` wraps its result and any thrown exception inside the `Deferred<T>` object. The exception is considered handled until someone invokes `deferred.await()`, at which point it is rethrown at the `await()` call site. CEH only handles uncaught exceptions from `launch`."
            },
            {
                "interviewer": "Can you use `try-catch` around a `launch` call to catch exceptions thrown inside it?",
                "answer": "No! Wrapping `try { scope.launch { throw Exception() } } catch (e: Exception)` does nothing because `launch` returns immediately and executes asynchronously on a dispatcher. The exception is thrown inside the coroutine block, not in the calling thread."
            },
            {
                "interviewer": "Where should error handling actually live in an Android app?",
                "answer": "In the repository or use-case layer using `try-catch` wrapped into domain Result/Either sealed classes, or in the ViewModel around suspending calls, so the UI can gracefully show retry buttons and descriptive error messages."
            }
        ]
    },
    {
        "id": "COR-15",
        "arabic_explanation": (
            "الفارق الجوهري في معالجة الاستثناءات بين `launch` و `async` هو من أهم الأسئلة التي تميز الفهم العميق لـ Kotlin Coroutines:\n\n"
            "1. استثناءات دالة `launch` (Eager Exception Propagation):\n"
            "   - `launch` مصممة كـ Fire-and-Forget.\n"
            "   - أي Uncaught Exception بيحدث داخلها **يتم رميه فوراً للأعلى (Eagerly Thrown)**.\n"
            "   - يصعد للـ Parent Job، يلغي الـ Scope، ويصل للـ `CoroutineExceptionHandler` أو يوقع التطبيق بـ Crash لو لم يتم التقاطه داخل الـ Coroutine نفسه عبر `try-catch`.\n\n"
            "2. استثناءات دالة `async` (Deferred / Encapsulated Exception Propagation):\n"
            "   - `async` مصممة لحساب نتيجة وإرجاعها في المستقبل كائن `Deferred<T>`.\n"
            "   - **في Root Coroutines:** لو أطلقت `val deferred = scope.async { throw Exception() }`، الاستثناء بيتم كتمه وتغليفه داخل كائن `Deferred`. لن يتم رمي الاستثناء إلا عندما ينادي المستدعي `deferred.await()`! إذا لم تنادِ `await()`، الاستثناء لن يُرمى أبداً!\n"
            "   - **داخل `coroutineScope` (الفخ الأكبر):** لو استدعيت `async` كـ Child داخل `coroutineScope`، حتى لو لم تنادِ `await()`، الاستثناء سيلغي الـ `coroutineScope` ويلغي باقي الإخوة فوراً بمجرد حدوثه!"
        ),
        "practical_walkthrough": (
            "مقارنة عملية توضح الفرق في الكود:\n"
            "```kotlin\n"
            "// 1. سلوك launch:\n"
            "viewModelScope.launch {\n"
            "    throw IllegalStateException(\"Error A\") // يرمى فوراً ويلغي viewModelScope لو لم يكن supervisor!\n"
            "}\n"
            "\n"
            "// 2. سلوك async كـ Root (خارج structured scope عادي):\n"
            "val deferred = scope.async {\n"
            "    throw IllegalStateException(\"Error B\") // يتم تخزينه داخل deferred بهدوء\n"
            "}\n"
            "// لن تشعر بأي استثناء حتى تكتب:\n"
            "try {\n"
            "    deferred.await() // هنا فقط يتم رمي IllegalStateException(\"Error B\")!\n"
            "} catch (e: Exception) {\n"
            "    println(\"Caught from await: $e\")\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Exceptions in 'launch' propagate eagerly and immediately up the job hierarchy to the parent and uncaught exception handlers. Exceptions in root 'async' coroutines are encapsulated inside the Deferred object and are only rethrown when await() is called.",
        "best_answer": (
            "The key difference lies in timing and delivery: exceptions in `launch` are treated as immediate unhandled failures, whereas exceptions in `async` are encapsulated into the return value until observed.\n\n"
            "When a coroutine launched with `launch` encounters an unhandled exception, it treats it like an uncaught exception in a thread: it immediately propagates up to its parent, cancels its scope, and delegates to a `CoroutineExceptionHandler` or crashes the process.\n\n"
            "When a root coroutine launched with `async` throws an exception, the exception is stored inside the resulting `Deferred<T>` instance. It remains dormant and unthrown until the caller invokes `deferred.await()`, at which point `await()` rethrows the original exception. This allows the caller to handle failures locally using a standard `try-catch` block around `await()`."
        ),
        "deep_answer": (
            "There is a crucial architectural nuance that trips up many engineers: **the context of `async` determines whether it behaves quietly or eagerly**.\n\n"
            "If `async` is launched as a child inside a standard `coroutineScope { }`:\n\n"
            "```kotlin\n"
            "coroutineScope {\n"
            "    val task = async { throw NetworkException() }\n"
            "}\n"
            "```\n\n"
            "Even if you never call `task.await()`, the moment the child `async` fails, it signals failure to its parent `coroutineScope`. The parent immediately cancels all other siblings and rethrows the `NetworkException`. Wrapping `task.await()` in a `try-catch` will catch the exception locally, but the parent `coroutineScope` has already been destroyed!\n\n"
            "To catch an `async` exception locally with `try-catch` around `await()` without cancelling sibling operations, you must run the operations inside a `supervisorScope { }`."
        ),
        "follow_ups": [
            {
                "interviewer": "What happens if you never call `await()` on a failing root `async` coroutine?",
                "answer": "If it is a root coroutine (e.g., launched on an independent scope with SupervisorJob), the exception is completely swallowed and never thrown, leading to silent failures that are difficult to debug."
            },
            {
                "interviewer": "How do you handle multiple `async` tasks where one might fail?",
                "answer": "Run them inside `supervisorScope`, wrap each `deferred.await()` in individual `try-catch` blocks or use `runCatching { deferred.await() }`, allowing you to handle partial failures gracefully."
            },
            {
                "interviewer": "Does `CoroutineExceptionHandler` catch exceptions from `async`?",
                "answer": "No, never. CEH only handles unhandled exceptions from `launch`. Because `async` stores its exception in the Deferred object, it is considered handled by design until await is called."
            }
        ]
    },
    {
        "id": "COR-16",
        "arabic_explanation": (
            "التعامل مع `CancellationException` في Kotlin Coroutines هو أحد أدق وأهم المواضيع في الـ Senior Level:\n\n"
            "1. ما هي `CancellationException`؟\n"
            "   - هي الـ Exception المخصص الذي تستخدمه مكتبة Coroutines لنقل إشارة الإلغاء وتفكيك الـ Call Stack للـ Coroutine عند إلغائها.\n"
            "   - هي ليست خطأ حقيقياً (Not a failure)؛ بل هي **آلية عمل طبيعية (Control-flow mechanism)**.\n\n"
            "2. الكارثة الأكثر شيوعاً: ابتلاع الاستثناء (Swallowing CancellationException):\n"
            "   - لو كتبت:\n"
            "     `try { repo.fetchData() } catch (e: Exception) { Log.e(\"Tag\", e.message) }`\n"
            "   - لأن `CancellationException` تورث من `java.lang.Exception`، الـ catch block هيلتقطها ويبلعها!\n"
            "   - النتيجة: الـ Coroutine ترفض التوقف! لو المستخدم قفل الشاشة والـ ViewModel اتلغى، الكود هيفضل شغال في الخلفية ويسرب الذاكرة والبطارية!\n\n"
            "3. القاعدة الذهبية للتعامل مع CancellationException:\n"
            "   - **إما أن تلتقط استثناءات محددة فقط (Catch specific exceptions):** زي `catch (e: IOException)`.\n"
            "   - **أو لو مضطر تلتقط `Exception` أو `Throwable`، لازم تعيد رميها فوراً:**\n"
            "     `if (e is CancellationException) throw e`"
        ),
        "practical_walkthrough": (
            "نمط الكود الصحيح الذي نطبقه في الـ Production:\n"
            "```kotlin\n"
            "// ❌ النهج الكارثي: يبلع الإلغاء ويمنع التوقف:\n"
            "suspend fun uploadAvatar(file: File) {\n"
            "    try {\n"
            "        api.upload(file)\n"
            "    } catch (e: Exception) {\n"
            "        showErrorToast()\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ النهج السليم والاحترافي:\n"
            "suspend fun uploadAvatar(file: File) {\n"
            "    try {\n"
            "        api.upload(file)\n"
            "    } catch (e: CancellationException) {\n"
            "        throw e // إعادة الرمي فوراً ليتم الإلغاء بنجاح\n"
            "    } catch (e: IOException) {\n"
            "        showErrorToast() // معالجة أخطاء الشبكة فقط\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "CancellationException is coroutines' internal control-flow signal for cooperative cancellation. It must never be swallowed. If catching broad Exception or Throwable, you must always rethrow CancellationException immediately so the coroutine can unwind its call stack and terminate cleanly.",
        "best_answer": (
            "In Kotlin Coroutines, `CancellationException` is not a bug or system failure; it is the fundamental control-flow mechanism used to unwind the coroutine call stack when a task is cancelled.\n\n"
            "The most dangerous and common pitfall is swallowing `CancellationException` by catching generic `Exception`:\n\n"
            "```kotlin\n"
            "try {\n"
            "    doWork()\n"
            "} catch (e: Exception) {\n"
            "    // BUG: Swallows CancellationException!\n"
            "}\n"
            "```\n\n"
            "Because `CancellationException` inherits from `java.lang.Exception`, this catch block suppresses the cancellation signal. The coroutine assumes it recovered, refuses to terminate, and continues executing, creating background resource leaks and zombie network requests.\n\n"
            "To propagate it correctly: either catch only specific domain exceptions like `IOException` or `HttpException`, or if you must catch broad `Exception`, check for `if (e is CancellationException) throw e` before handling other errors."
        ),
        "deep_answer": (
            "Under the hood, when `Job.cancel()` is called, active suspension points throw a `CancellationException`. "
            "The coroutine runtime distinguishes `CancellationException` from other throwables: it does not mark the Job as failed, does not report to `CoroutineExceptionHandler`, and does not cancel the parent Job. It simply transitions the coroutine to the CANCELLED state.\n\n"
            "This has serious implications for utility methods like `runCatching` in the standard library. `kotlin.runCatching` catches all `Throwable` instances, including `CancellationException`. If you use `runCatching` around suspending calls, it converts `CancellationException` into a `Result.failure`, breaking structured concurrency unless you explicitly inspect and rethrow it.\n\n"
            "In our Android architecture, we forbid raw `runCatching` on suspend functions in code review, replacing it with a custom `runSuspendCatching` helper that automatically rethrows `CancellationException`."
        ),
        "follow_ups": [
            {
                "interviewer": "Why is `kotlin.runCatching` dangerous with Coroutines?",
                "answer": "Because `runCatching` catches `Throwable`, which intercepts `CancellationException` and encapsulates it as a failure. This silences coroutine cancellation and causes cancelled tasks to continue executing subsequent statements."
            },
            {
                "interviewer": "Can you provide a custom message or cause when cancelling a Job?",
                "answer": "Yes. You can invoke `job.cancel(CancellationException(\"User clicked cancel\", customCause))` to attach diagnostic reasons for debugging and logging."
            },
            {
                "interviewer": "What should you do if you need to run suspending cleanup code after cancellation?",
                "answer": "Place the cleanup logic inside a `finally` block and wrap any suspending calls in `withContext(NonCancellable)`. This prevents the cleanup coroutine from being immediately aborted by the active cancellation state."
            }
        ]
    },
    {
        "id": "COR-17",
        "arabic_explanation": (
            "إدارة الـ Timeouts في Kotlin Coroutines تتم عبر دالتين رئيسيتين: `withTimeout` و `withTimeoutOrNull`:\n\n"
            "1. دالة `withTimeout(timeMillis)`:\n"
            "   - بتعلق الـ Coroutine وتحدد مهلة زمنية قصوى لتنفيذ البلوك.\n"
            "   - لو الوقت انتهى قبل اكتمال الكود، بترمي **`TimeoutCancellationException`** (وهي نوع خاص من `CancellationException`).\n"
            "   - **تحذير خطير:** بما إنها ترمي Exception، لو الكود مش محاط بـ `try-catch`، الـ Exception هيلغي الـ Coroutine بالكامل!\n\n"
            "2. دالة `withTimeoutOrNull(timeMillis)`:\n"
            "   - البديل الأكثر أماناً وأناقة في معظم سيناريوهات الـ UI والشبكات.\n"
            "   - لو البلوك انتهى في الوقت المحدد: بترجع النتيجة بنجاح.\n"
            "   - لو الوقت انتهى: تلغي البلوك وترجع **`null`** بدون رمي أي Exception وبدون إلغاء الـ Scope!\n\n"
            "3. نقطة دقيقة للمحترفين (Under the hood Caveat):\n"
            "   - عملية فحص الـ Timeout هي عملية **تعاونية (Cooperative)**. لو الكود الداخلي عبارة عن Loop حسابية مفيهاش أي Suspension point، الـ Timeout مش هيقدر يوقفها حتى لو الوقت خلص!"
        ),
        "practical_walkthrough": (
            "في شاشة جلب الموقع الجغرافي أو المصادقة البيومترية:\n"
            "- المستخدم بيطلب تحديد موقعه الحالي بنظام GPS؛ لو الـ GPS لم يستجب خلال 5 ثوانٍ، نريد استخدام آخر موقع محفوظ في الـ Cache بدلاً من تعليق الشاشة.\n"
            "```kotlin\n"
            "suspend fun getCurrentLocation(): Location {\n"
            "    // نستخدم withTimeoutOrNull بمهلة 5 ثوانٍ:\n"
            "    val freshLocation = withTimeoutOrNull(5_000L) {\n"
            "        gpsClient.awaitSingleFix()\n"
            "    }\n"
            "    \n"
            "    // لو رجع null (حصل timeout)، نستخدم الـ Cache فوراً:\n"
            "    return freshLocation ?: locationCache.getLastKnownLocation()\n"
            "}\n"
            "```"
        ),
        "quick_answer": "withTimeout cancels the block and throws a TimeoutCancellationException if the time limit expires. withTimeoutOrNull cancels the block and safely returns null upon timeout instead of throwing an exception, making it much more ergonomic for fallbacks and retry logic.",
        "best_answer": (
            "Both `withTimeout` and `withTimeoutOrNull` enforce execution time limits on suspending blocks, but they handle deadline expiration differently.\n\n"
            "`withTimeout` cancels the enclosed coroutine block and throws a `TimeoutCancellationException` if the duration elapses before completion. Because `TimeoutCancellationException` inherits from `CancellationException`, it cancels the enclosing coroutine unless explicitly caught with a `try-catch` block around `withTimeout`.\n\n"
            "`withTimeoutOrNull` is much more ergonomic for Android fallback scenarios. When the deadline expires, it cancels the internal block and cleanly returns `null` instead of throwing an exception. This allows elegant fallback expressions using the Elvis operator (`?:`), such as falling back to cached database data if a network request exceeds two seconds."
        ),
        "deep_answer": (
            "Under the hood, both functions schedule a delayed task on the coroutine dispatcher's event loop via `Delay.scheduleResumeAfterDelay()`. When the timer fires, it calls `cancelCoroutine(TimeoutCancellationException)`. "
            "However, timeout cancellation is strictly cooperative. If the code running inside `withTimeout` is executing a non-suspending, blocking loop (like heavy crypto or file I/O), the timeout cannot preempt the thread. It will only cancel when the block reaches a suspension point or checks `ensureActive()`.\n\n"
            "Another critical nuance is resource cleanup. If an unmanaged resource (like a database cursor or network socket) is opened inside `withTimeout`, a timeout cancellation during the open call could leak the resource before the assignment finishes. "
            "To guard against resource leaks, always allocate resources outside the timeout block or protect them with `try-finally`."
        ),
        "follow_ups": [
            {
                "interviewer": "Why does catching `CancellationException` outside `withTimeout` catch the timeout exception?",
                "answer": "Because `TimeoutCancellationException` is a subclass of `CancellationException`. If you catch `CancellationException`, you will catch timeout errors as well, which is why `withTimeoutOrNull` is generally preferred to avoid accidental exception handling confusion."
            },
            {
                "interviewer": "How does `withTimeout` interact with deterministic unit tests?",
                "answer": "When using `runTest` from `kotlinx-coroutines-test`, virtual time is automatically skipped by default. `withTimeout` will either complete instantly if virtual time is advanced, or time out deterministically when calling `advanceTimeBy(delay)`."
            },
            {
                "interviewer": "Can you use `withTimeout` with blocking Java network calls?",
                "answer": "Only if the blocking call is running on `Dispatchers.IO` and explicitly checks for cancellation. Standard blocking calls like `InputStream.read()` will not respond to `withTimeout` until the socket read returns or closes."
            }
        ]
    },
    {
        "id": "COR-18",
        "arabic_explanation": (
            "إعادة المحاولة مع التراجع الأسي والعشوائية (Exponential Backoff with Jitter) هي أفضل نمط إنتاجي للتعامل مع أخطاء الشبكة العابرة (Transient Network Errors):\n\n"
            "1. ما هي مشكلة إعادة المحاولة الثابتة (Fixed Retries)؟\n"
            "   - لو 10,000 مستخدم فتحوا التطبيق في نفس الوقت والسيرفر كان مضغوطاً ورجع خطأ 503، وكل التطبيقات أعادت المحاولة بعد ثانية واحدة بالظبط:\n"
            "   - كل الـ 10,000 جهاز هيضربوا السيرفر في نفس الميلي-ثانية! ده بيعمل **Thundering Herd Problem (أو Retry Storm)** ويوقع السيرفر تماماً.\n\n"
            "2. الـ Exponential Backoff:\n"
            "   - بنضاعف وقت الانتظار بعد كل محاولة فاشلة (مثلاً: 1 ثانية، ثم 2، ثم 4، ثم 8 ثوانٍ).\n\n"
            "3. دور الـ Jitter (العشوائية الضرورية):\n"
            "   - إضافة وقت عشوائي صغير (Random Jitter من 0 إلى 500ms) لكل جهاز، حتى لا ترسل الأجهزة طلباتها في نفس التوقيت المتزامن، فيتم توزيع الحمل بسلاسة على السيرفر.\n\n"
            "4. متى نعيد المحاولة ومتى نتوقف؟\n"
            "   - **نكرر المحاولة فقط في:** أخطاء الشبكة العابرة (Timeout, 502, 503, 504).\n"
            "   - **لا نكرر المحاولة أبداً في:** أخطاء العميل الحتمية (400 Bad Request, 401 Unauthorized, 404 Not Found)، ولا عند إلغاء الـ Coroutine (`CancellationException`)."
        ),
        "practical_walkthrough": (
            "دالة إنتاجية متكاملة لـ Retry with Backoff & Jitter في Kotlin:\n"
            "```kotlin\n"
            "suspend fun <T> retryWithBackoff(\n"
            "    times: Int = 3,\n"
            "    initialDelayMs: Long = 1000L,\n"
            "    maxDelayMs: Long = 10000L,\n"
            "    factor: Double = 2.0,\n"
            "    block: suspend () -> T\n"
            "): T {\n"
            "    var currentDelay = initialDelayMs\n"
            "    repeat(times - 1) { attempt ->\n"
            "        try {\n"
            "            return block()\n"
            "        } catch (e: Exception) {\n"
            "            if (e is CancellationException) throw e // لا تبلع الإلغاء أبداً!\n"
            "            if (!isTransientError(e)) throw e // لا تعيد المحاولة في أخطاء 4xx\n"
            "        }\n"
            "        val jitter = Random.nextLong(0, 500L)\n"
            "        delay(minOf(currentDelay + jitter, maxDelayMs))\n"
            "        currentDelay = (currentDelay * factor).toLong()\n"
            "    }\n"
            "    return block() // المحاولة الأخيرة بدون catch\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Retry with exponential backoff doubles the delay between consecutive failed attempts, while jitter adds a randomized time offset to prevent the 'thundering herd' problem. Crucially, retry loops must never catch CancellationException and must only retry transient server/network failures, never permanent 4xx client errors.",
        "best_answer": (
            "Exponential backoff with jitter is an essential resilience pattern for handling transient network failures without overwhelming backend services.\n\n"
            "When a transient error occurs (like an HTTP 503 or socket timeout), retrying immediately or with a fixed delay causes the 'thundering herd' problem: thousands of mobile clients retry in unison, creating synchronized traffic spikes that keep the recovering server down. With exponential backoff, each retry doubles the wait time (e.g., 1s, 2s, 4s, up to a maximum cap).\n\n"
            "Adding **jitter** injects a randomized offset (e.g., plus a random 0 to 500ms) into the delay calculation. This desynchronizes retry attempts across thousands of distributed devices, smoothing the load curve on backend systems.\n\n"
            "In coroutines, we implement this as an inline suspending helper. Crucially, the retry loop must rethrow `CancellationException` immediately so coroutines cancel properly, and must only retry transient failures—never retrying permanent 4xx client errors like 401 Unauthorized or 404 Not Found."
        ),
        "deep_answer": (
            "From a distributed systems engineering perspective, full jitter (picking a uniform random value between 0 and the exponential backoff ceiling) provides superior desynchronization compared to equal jitter or no jitter.\n\n"
            "When integrating this pattern with reactive streams or Kotlin Flow, the `retryWhen` operator provides the idiomatic abstraction: "
            "```kotlin\n"
            "flow.retryWhen { cause, attempt ->\n"
            "    if (attempt < 3 && cause is IOException) {\n"
            "        val delayTime = minOf(1000L * (1L shl attempt.toInt()) + Random.nextLong(200L), 10_000L)\n"
            "        delay(delayTime)\n"
            "        true\n"
            "    } else false\n"
            "}\n"
            "```\n\n"
            "In unit testing with `runTest`, testing backoff algorithms is straightforward because `delay()` integrates with the test scheduler's virtual clock, advancing time instantaneously with `advanceTimeBy()` without forcing tests to sleep in real time."
        ),
        "follow_ups": [
            {
                "interviewer": "Why shouldn't you retry HTTP 401 or 403 errors with exponential backoff?",
                "answer": "Because 401 and 403 are client authentication and permission failures, not transient network drops. Retrying them without refreshing the authentication token will fail every single time, wasting mobile battery and backend compute."
            },
            {
                "interviewer": "How does OkHttp's Interceptor compare to a coroutine retry wrapper?",
                "answer": "An OkHttp Interceptor handles retries at the transport layer, which is fast and transparent. However, a coroutine-level retry wrapper is superior for business-level logic, such as switching from a failed primary API to a fallback CDN, or updating UI progress messages between retries."
            },
            {
                "interviewer": "What is the maximum delay cap, and why is it necessary?",
                "answer": "Without a maximum delay cap (e.g., 10 or 30 seconds), exponential backoff grows unboundedly (1s, 2s, 4s, 8s, 16s, 32s, 64s...). A cap prevents the user from waiting minutes for an operation that should simply fail fast and prompt manual intervention."
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

    for q in COR_13_18:
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
    print(f"Updated {DATA_FILE} with questions COR-13 to COR-18. Total questions: {len(combined)}")


if __name__ == "__main__":
    main()

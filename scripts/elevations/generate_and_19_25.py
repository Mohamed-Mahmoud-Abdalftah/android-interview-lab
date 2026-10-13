#!/usr/bin/env python3
"""Generator for AND-19 through AND-25 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "and.json"

AND_19_25 = [
    {
        "id": "AND-19",
        "arabic_explanation": (
            "الـ Foreground Services ومتطلبات الإشعارات في أندرويد الحديث (خاصة مع Android 14) خضعت لتغييرات جذرية لحماية خصوصية وبطارية المستخدم:\n\n"
            "1. ما هي الـ Foreground Service؟\n"
            "   - هي Service تعمل في الخلفية ولكنها **مرئية للمستخدم بشكل صريح (User-aware)**.\n"
            "   - النظام يعطيها أولوية قصوى ولا يقتلها لتوفير الذاكرة، ولكن بشرط صارم: **يجب أن تعرض إشعاراً مستمراً (Ongoing Notification)** في شريط الإشعارات لا يمكن للمستخدم حذفه أثناء عملها.\n"
            "   - أمثلة: تشغيل ملفات صوتية (Music Playback)، تتبع مسار الجري بالـ GPS، وتطبيقات الاتصال الصوتي عبر الإنترنت (VoIP).\n\n"
            "2. القيود الصارمة في Android 14 (API 34):\n"
            "   - **إلزامية تحديد الـ Foreground Service Type:** لم يعد مسموحاً إنشاء Foreground Service عامة! يجب أن تحدد نوعها الصريح في الـ `AndroidManifest.xml` (مثل: `android:foregroundServiceType=\"location\"` أو `\"mediaPlayback\"` أو `\"microphone\"`).\n"
            "   - **طلب إذن مخصص لكل نوع:** مثل `<uses-permission android:name=\"android.permission.FOREGROUND_SERVICE_LOCATION\" />`.\n\n"
            "3. متى نستخدمها ومتى نتجنبها؟\n"
            "   - استخدمها **فقط** إذا كان المستخدم يتوقع استمرار العملية فوراً ويرى نتيجتها (مثل ملاحة الـ GPS).\n"
            "   - لو كانت العملية مجرد تحميل ملفات، مزامنة قاعدة بيانات، أو رفع صور: **ممنوع استخدام Foreground Service**؛ يجب استخدام **WorkManager**."
        ),
        "practical_walkthrough": (
            "تنفيذ Foreground Service لتتبع الموقع متوافقة مع Android 14:\n"
            "```xml\n"
            "<!-- في AndroidManifest.xml: -->\n"
            "<uses-permission android:name=\"android.permission.FOREGROUND_SERVICE\" />\n"
            "<uses-permission android:name=\"android.permission.FOREGROUND_SERVICE_LOCATION\" />\n"
            "<uses-permission android:name=\"android.permission.ACCESS_FINE_LOCATION\" />\n"
            "\n"
            "<service\n"
            "    android:name=\".LocationTrackingService\"\n"
            "    android:foregroundServiceType=\"location\" />\n"
            "```\n"
            "في الكود (Kotlin):\n"
            "```kotlin\n"
            "class LocationTrackingService : Service() {\n"
            "    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {\n"
            "        val notification = createNotification() // بناء إشعار مع NotificationChannel\n"
            "        // بدء الخدمة مع تحديد نوعها لـ Android 14:\n"
            "        ServiceCompat.startForeground(\n"
            "            this,\n"
            "            NOTIFICATION_ID,\n"
            "            notification,\n"
            "            ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION\n"
            "        )\n"
            "        startGpsTracking()\n"
            "        return START_STICKY\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Foreground Services perform operations noticeable to the user and require an ongoing, non-dismissible notification. In Android 14+, you must explicitly declare dedicated foregroundServiceType attributes in the manifest and request type-specific permissions (e.g. location, mediaPlayback), reserving them for real-time user-driven tasks while delegating deferred work to WorkManager.",
        "best_answer": (
            "A Foreground Service is an Android execution component that performs operations noticeable to the user, granted elevated process priority by the OS in exchange for transparency.\n\n"
            "The foundational requirements are:\n\n"
            "1. **Ongoing Notification**: The service must display a persistent, non-dismissible notification (`NotificationCompat.Builder`) within a valid `NotificationChannel`. In Android 13+, the user must grant the runtime `POST_NOTIFICATIONS` permission.\n\n"
            "2. **Mandatory Service Types (Android 14+)**: Android 14 (API 34) forbids generic foreground services. Developers must declare a specific `android:foregroundServiceType` in the manifest (e.g., `camera`, `location`, `mediaPlayback`, `microphone`, `phoneCall`, `health`) and declare corresponding type-specific permissions (`FOREGROUND_SERVICE_LOCATION`). Launching a foreground service with an undeclared type throws an immediate `MissingForegroundServiceTypeException`.\n\n"
            "3. **Appropriate Usage**: They should be used strictly for user-active tasks (GPS turn-by-turn navigation, audio playback, active VoIP calls). For background data syncing or file uploading, modern architecture mandates **WorkManager** instead."
        ),
        "deep_answer": (
            "From an OS scheduling and policy perspective, starting a foreground service from the background was largely blocked in Android 12 (Background Start Restrictions). "
            "Calling `startForegroundService()` while the app is in the background throws a fatal `ForegroundServiceStartNotAllowedException`, with very few exceptions (like high-priority FCM push notifications or exact alarms).\n\n"
            "Furthermore, in Android 14, Google Play enforces strict policy reviews: if your app uses `foregroundServiceType=\"dataSync\"`, you must demonstrate to Google Play reviewers that the work cannot be handled by WorkManager or the DownloadManager. "
            "Failing this justification will lead to app rejection. "
            "For network requests that need to complete after the user leaves the screen, WorkManager's `CoroutineWorker` paired with `setForeground()` is the recommended, compliant approach."
        ),
        "follow_ups": [
            {
                "interviewer": "What happens if a service calls `startForeground()` later than 5 seconds after `startForegroundService()`?",
                "answer": "Android triggers an ANR crash. When starting a service via `startForegroundService()`, you have an exact 5-second window to call `startForeground()` with a valid notification, or the system crashes the process with an ANR."
            },
            {
                "interviewer": "How does `START_STICKY` differ from `START_NOT_STICKY`?",
                "answer": "`START_STICKY` instructs the OS to recreate the service if killed due to low memory, delivering a null intent. `START_NOT_STICKY` tells the OS not to recreate the service unless there are pending start intents."
            },
            {
                "interviewer": "Can a user dismiss a Foreground Service notification in Android 13+?",
                "answer": "Yes. Starting in Android 13, users can swipe away foreground service notifications from the notification shade, but the notification remains visible in the active FGS Task Manager in the quick settings drawer."
            }
        ]
    },
    {
        "id": "AND-20",
        "arabic_explanation": (
            "مشاركة البيانات والتواصل عبر العمليات المختلفة (Inter-Process Communication - IPC) في نظام Android:\n\n"
            "1. جوهر الـ IPC في أندرويد: محرك **Binder**:\n"
            "   - كل تطبيق في Android يعمل في **Linux Process منفصل** محمي بـ Sandbox خاص به.\n"
            "   - الـ **Binder** هو الـ Kernel Driver المتخصص في نظام أندرويد الذي يتيح نقل البيانات والـ Remote Method Calls بين العمليات المختلفة بسرعة فائقة عبر الـ Shared Memory مع حماية أمنية للـ UID.\n\n"
            "2. آليات التواصل الأربعة (The 4 IPC Mechanisms):\n"
            "   - **1. الـ AIDL (Android Interface Definition Language):**\n"
            "     * كتابة Interface معيارية لـ Remote Procedure Calls (RPC).\n"
            "     * مناسبة للتواصل عالي الأداء والمتزامن متعدد الخيوط (Multithreaded IPC) بين تطبيقين مختلفين.\n"
            "   - **2. الـ Messenger:**\n"
            "     * أداة مبنية فوق Binder ولكنها تستخدم `Handler` و `Message`.\n"
            "     * مخصصة للـ IPC أحادي الخيط (Single-threaded IPC)؛ تعالج الرسائل في طابور واحد متسلسل بدون تعقيد الـ Multithreading.\n"
            "   - **3. الـ ContentProvider:**\n"
            "     * أسهل وأفضل وسيلة لمشاركة البيانات المهيكلة (CRUD / Database Tables / Files) بين التطبيقات عبر `ContentResolver`.\n"
            "   - **4. الـ BroadcastReceiver:**\n"
            "     * لإرسال إشارات وأحداث عامة لعدة عمليات في نفس الوقت (One-to-Many IPC).\n\n"
            "3. القيد الحرج للـ Binder:\n"
            "   - الـ Binder Buffer له سعة قصوى حوالي **1 ميجابايت** مشتركة بين كل عمليات النظام. محاولة تمرير صور أو ملفات كبيرة عبر Binder سترمي `TransactionTooLargeException` فورا!"
        ),
        "practical_walkthrough": (
            "كيف تختار آلية الـ IPC المناسبة؟\n"
            "- **مشاركة صور أو مستندات ضخمة مع تطبيق آخر:**\n"
            "  استخدم `FileProvider` (وهو ContentProvider) وشارك `content:// URI` مع منح صلاحيات قراءة مؤقتة `FLAG_GRANT_READ_URI_PERMISSION`.\n"
            "- **تطبيق يقدم خدمة حسابية معقدة لعدة تطبيقات أخرى بالتوازي:**\n"
            "  استخدم `Bound Service` مع **AIDL**.\n"
            "- **تواصل بسيط برسائل وإشعارات بين تطبيقين لنفس الشركة:**\n"
            "  استخدم `Bound Service` مع **Messenger**."
        ),
        "quick_answer": "Android IPC is powered by the Linux Binder driver. Choose AIDL for multi-threaded remote procedure calls, Messenger for simple single-threaded Handler messaging, ContentProvider for structured data sharing, and FileProvider for large payloads to avoid Binder's 1MB buffer limit.",
        "best_answer": (
            "Inter-Process Communication (IPC) in Android is powered at the kernel level by the **Binder** driver, which allows processes to invoke methods and exchange data across Linux sandbox boundaries with hardware-backed performance and UID verification.\n\n"
            "We choose between four standard IPC mechanisms depending on requirements:\n\n"
            "1. **AIDL (Android Interface Definition Language)**: The most powerful IPC mechanism. Generates typed Binder stub interfaces that support direct client-to-server RPC calls across processes with concurrent multithreading. Used for complex inter-app SDKs.\n\n"
            "2. **Messenger**: A lightweight wrapper built on top of Binder that serializes messages through a single-threaded `Handler`. Best when thread-safety and sequential message processing are required without the concurrency complexities of AIDL.\n\n"
            "3. **ContentProvider**: The standard abstraction for sharing structured data (tables, files) across processes via SQL-like queries (`ContentResolver`).\n\n"
            "4. **FileProvider**: Crucial for sharing large binary assets (bitmaps, PDFs, videos). Because Binder transactions fail with `TransactionTooLargeException` if payloads exceed 1MB, we never pass heavy data over Binder; we pass secure `content://` URIs granted via temporary URI permissions."
        ),
        "deep_answer": (
            "Under the hood, Binder achieves high performance through **Shared Memory Mapping (`mmap`)**. "
            "When a process opens `/dev/binder`, the kernel maps a read-only shared memory page into the target process's address space. "
            "Data transferred across Binder requires only a **single copy** from the sender's user space to the receiver's mapped kernel buffer, making it significantly faster than standard Linux UNIX domain sockets or pipes.\n\n"
            "However, the Binder transaction buffer is capped at 1MB per process group. In multi-process applications (e.g., declaring `android:process=\":remote\"`), data objects passed across Binder must implement `Parcelable`.\n\n"
            "For security, the server process must inspect `Binder.getCallingUid()` and `Binder.getCallingPid()` to cryptographically verify that the calling process has the appropriate package identity and signature before executing privileged remote actions."
        ),
        "follow_ups": [
            {
                "interviewer": "Why is `Parcelable` preferred over `Serializable` for Binder transactions?",
                "answer": "`Parcelable` is an Android-optimized IPC serialization format designed for low allocations and direct memory streaming. `Serializable` relies on heavy Java runtime reflection, creating excessive object allocations that slow down Binder transactions."
            },
            {
                "interviewer": "What causes a `DeadObjectException` in Binder communication?",
                "answer": "A `DeadObjectException` is thrown when a client invokes a method on a remote Binder handle whose hosting process has crashed or been killed by the OS. Clients should attach a `DeathRecipient` to detect remote process death."
            },
            {
                "interviewer": "Can you pass a Binder object inside an Intent?",
                "answer": "Yes! Android `Bundle` has a `putBinder(key, binder)` method, which allows passing active Binder handles inside Intents to establish two-way communication channels."
            }
        ]
    },
    {
        "id": "AND-21",
        "arabic_explanation": (
            "مقتل شاشة الدفع بواسطة نظام أندرويد في منتصف العملية (Payment Screen killed mid-operation): ماذا يجب إعادة بنائه وما الذي يجب ألا يتكرر؟\n\n"
            "1. ما الذي يجب ألا يتكرر إطلاقاً (MUST NOT BE REPEATED)?\n"
            "   - **خصم الأموال من بطاقة العميل (The Financial Charge Call):**\n"
            "     * لو كان طلب الدفع قد تم إرساله للسيرفر بالفعل، **ممنوع تماماً إعادة إرسال طلب خصم جديد (No duplicate charge)!**\n"
            "     * لا تقم بتوليد `Idempotency Key` جديد؛ استخدم نفس المفتاح القديم.\n\n"
            "2. ما الذي يجب إعادة بنائه واستعادته (MUST BE RECONSTRUCTED)?\n"
            "   - **حالة الشاشة (UI State):** من خلال `SavedStateHandle`، استرجع: `orderId`, `amount`, و `idempotencyKey`.\n"
            "   - **الاستعلام عن حالة العملية (Reconciliation Query):** بدلاً من الدفع مجدداً، أرسل استعلاماً للسيرفر: 'ما هي حالة المعاملة ذات المفتاح X؟' (`GET /orders/{id}/payment-status`).\n"
            "     * لو السيرفر أكد نجاحها: انتقل فوراً لشاشة الإيصال (Receipt Screen).\n"
            "     * لو لم تتم: اسمح للمستخدم بإعادة المحاولة يدوياً.\n\n"
            "3. ضمانات الـ Backend و WorkManager:\n"
            "   - إرسال طلبات الدفع الحيوية يفضل أن يكون عبر `WorkManager` حتى يضمن إكمال العملية حتى لو مات التطبيق بالكامل."
        ),
        "practical_walkthrough": (
            "هندسة استعادة شاشة الدفع بعد Process Death في ViewModel:\n"
            "```kotlin\n"
            "class PaymentViewModel(\n"
            "    private val savedStateHandle: SavedStateHandle,\n"
            "    private val paymentRepository: PaymentRepository\n"
            ") : ViewModel() {\n"
            "\n"
            "    // 1. استعادة معرف العملية ومفتاح التكرار بعد مقتل الشاشة:\n"
            "    private val orderId: String = checkNotNull(savedStateHandle[\"order_id\"])\n"
            "    private val idempotencyKey: String = checkNotNull(savedStateHandle[\"idempotency_key\"])\n"
            "\n"
            "    init {\n"
            "        // 2. التحقق من الحالة الحقيقية أولاً بدون سحب أموال جديدة:\n"
            "        reconcilePaymentStatus()\n"
            "    }\n"
            "\n"
            "    private fun reconcilePaymentStatus() = viewModelScope.launch {\n"
            "        _uiState.value = PaymentUiState.VerifyingStatus\n"
            "        when (val status = paymentRepository.queryPaymentStatus(idempotencyKey)) {\n"
            "            is PaymentStatus.Completed -> _uiState.value = PaymentUiState.Success(status.receipt)\n"
            "            is PaymentStatus.NotFound -> _uiState.value = PaymentUiState.ReadyToPay\n"
            "            is PaymentStatus.Processing -> _uiState.value = PaymentUiState.Processing\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Do NOT repeat the financial charge request or regenerate the idempotency key, preventing double billing. DO reconstruct the order details and original transaction idempotency key via SavedStateHandle, and execute an idempotent reconciliation query (GET /status) to verify whether the payment succeeded on the backend before offering a retry.",
        "best_answer": (
            "When a payment screen is killed by the OS mid-operation, the golden architectural rule is: **Separate state reconstruction from transactional execution**.\n\n"
            "**What must NOT be repeated:**\n\n"
            "- Never re-execute the financial charge API call automatically upon screen recreation.\n"
            "- Never generate a new transaction ID or fresh idempotency key. Repeating a POST charge request will bill the customer twice if the backend already processed the initial request before the app was killed.\n\n"
            "**What MUST be reconstructed:**\n\n"
            "- Restore the transaction metadata (`orderId`, `amount`, and the existing `idempotencyKey`) from `SavedStateHandle`.\n"
            "- Immediately execute an **Idempotent Status Reconciliation Query** (`GET /payments/status?key=<uuid>`). If the backend settled the charge during the process kill, restore the UI straight into `PaymentSuccess(receipt)`. If the backend confirms no transaction occurred, restore the UI to `ReadyToSubmit`, enabling the customer to retry safely."
        ),
        "deep_answer": (
            "From a mission-critical Fintech reliability perspective, payment dispatches should ideally not rely exclusively on in-memory ViewModel scopes. "
            "If the transaction submission was initiated via an application-level CoroutineScope or an expedited **WorkManager** worker, the background task might still be executing on the network thread while the UI is killed.\n\n"
            "By maintaining a local transaction entity in Room:\n\n"
            "```text\n"
            "Order #1234 -> Status: SUBMITTING | Idempotency: 8a7f-43b2\n"
            "```\n\n"
            "When the recreated Activity and ViewModel spin up, they observe the Room entity. "
            "If the background worker finishes in Room with `Status: SUCCESS`, the UI updates automatically to the Success screen without any duplicate API calls, guaranteeing zero financial inconsistencies."
        ),
        "follow_ups": [
            {
                "interviewer": "Where should the idempotency key be generated?",
                "answer": "Locally on the device before the initial submission, persisted immediately in Room and SavedStateHandle so that it survives both configuration changes and process death."
            },
            {
                "interviewer": "What if the user clicks the 'Pay' button and rapidly presses Home?",
                "answer": "The payment request should be handed off to an application-scoped repository coroutine or WorkManager so that backgrounding the screen does not abort the in-flight payment request."
            },
            {
                "interviewer": "How do you prevent the user from clicking 'Pay' twice before the request leaves the device?",
                "answer": "Immediately disable the UI pay button upon the first tap, and guard the ViewModel submit function with a mutual exclusion lock (`Mutex`) or atomic state flag."
            }
        ]
    },
    {
        "id": "AND-22",
        "arabic_explanation": (
            "عطل (Crash) يحدث فقط بعد ترك التطبيق في الخلفية لعدة ساعات: كيف تحقق في هذا العطل وتكتشف علاقته بدورة الحياة والـ Process Restoration؟\n\n"
            "1. تشخيص العطل (The Diagnosis):\n"
            "   - العطل الذي يظهر فقط بعد ساعات في الخلفية هو بنسبة 99% **عطل ناتج عن Process Death غير المعالج (Unmanaged Process Death Crash)**!\n"
            "   - عندما يترك التطبيق لساعات، يقوم نظام أندرويد بقتل الـ Process لتوفير الرام.\n"
            "   - عند عودة المستخدم، يقوم النظام بإعادة فتح **نفس الشاشة الداخلية التي كان يقف عليها** (Restored Activity) من الـ Backstack، ولكن كل الـ In-memory Singletons والـ Static variables والـ Cache أصبحت `null`!\n"
            "   - الكود يحاول قراءة `UserSession.currentUser.id` فيحدث `NullPointerException` فوراً!\n\n"
            "2. كيف تعيد تمثيل العطل في ثوانٍ في بيئة التطوير (Reproduction in 5 seconds)؟\n"
            "   - لا تنتظر ساعات! افتح الشاشة في المحاكي، اضغط زر Home، ثم نفذ أمر:\n"
            "     `adb shell am kill <package_name>`\n"
            "   - ثم افتح التطبيق من Recents؛ سيعاد إنتاج الـ Crash فوراً!\n\n"
            "3. الحل المعماري الجذري:\n"
            "   - عدم الاعتماد على Singletons عائمة في الذاكرة لتمرير البيانات بين الشاشات.\n"
            "   - استخدام `SavedStateHandle` لتمرير المعرفات (IDs)، وإعادة تحميل البيانات من قاعدة بيانات Room أو DataStore عند بدء الشاشة."
        ),
        "practical_walkthrough": (
            "التحقيق والحل في الكود:\n"
            "```kotlin\n"
            "// ❌ الكود المسبب للكراش بعد ساعات:\n"
            "class OrderDetailsActivity : AppCompatActivity() {\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        // كارثة: يفترض أن الـ Singleton يحتوي على بيانات المستخدم!\n"
            "        // بعد ساعات في الخلفية، AppSession تصبح null ويحدث Crash فوراً:\n"
            "        val user = AppSession.currentUser!! // NullPointerException!\n"
            "        loadOrder(user.token)\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ الحل المعماري المستقر:\n"
            "class OrderDetailsViewModel(\n"
            "    savedStateHandle: SavedStateHandle,\n"
            "    authRepository: AuthRepository,\n"
            "    orderRepository: OrderRepository\n"
            ") : ViewModel() {\n"
            "    // نقرأ المعرفات المحفوظة من SavedStateHandle ونقرأ التوكن من DataStore دائم التخزين:\n"
            "    val orderId: String = checkNotNull(savedStateHandle[\"order_id\"])\n"
            "    val uiState = authRepository.observeSessionToken().flatMapLatest {\n"
            "        orderRepository.observeOrder(orderId)\n"
            "    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), Loading)\n"
            "}\n"
            "```"
        ),
        "quick_answer": "This is a classic Process Death crash. After hours in the background, Android killed the app process. Upon return, Android recreates the top Activity while in-memory singletons and static caches are completely null, triggering NullPointerExceptions. Reproduce it instantly via 'adb shell am kill <package>' and fix it using SavedStateHandle and persistent Room/DataStore storage.",
        "best_answer": (
            "A crash that manifests only after the app has been backgrounded for several hours is the quintessential signature of **Unmanaged Process Death**.\n\n"
            "**Why it occurs:**\n\n"
            "While in the background, Android's Low Memory Killer terminated the process. When the user taps the app in Recents hours later, Android attempts to restore user continuity by restoring the exact top Activity the user was on. However, because the process was killed, all in-memory static variables, singletons, Dagger graphs, and cache objects were wiped. When the restored Activity attempts to dereference `AppCache.selectedUser` or `SessionManager.currentUser`, it crashes immediately with a `NullPointerException`.\n\n"
            "**How I investigate and fix it:**\n\n"
            "1. **Instant Reproduction**: Background the app on an emulator, run `adb shell am kill <package_name>`, and click the app in Recents. This reproduces the multi-hour crash in 5 seconds.\n"
            "2. **Inspect Navigation & Bundles**: Verify that the restored Activity/Fragment extracts its required IDs from `SavedStateHandle` or `Intent.extras` rather than relying on global memory caches.\n"
            "3. **Persistent Auth Fallback**: If user authentication is required, retrieve the auth token asynchronously from encrypted DataStore; if expired, gracefully redirect the backstack to the Login screen rather than crashing."
        ),
        "deep_answer": (
            "From a root-cause analysis perspective, inspect the stack trace in Crashlytics: "
            "A process death crash almost always shows the Activity's `onCreate(savedInstanceState)` receiving a non-null `Bundle`, while an in-memory utility class threw NPE.\n\n"
            "In enterprise codebases, we enforce architectural defenses against process death bugs: "
            "1. **Never use static variables or Singletons as cross-screen data transport.** "
            "2. **Enable 'Don't keep activities' during developer QA.** "
            "3. **Session Interceptor Pattern**: In the base Activity or root Navigation Host, evaluate whether a mandatory user session is valid. If the session was purged by process death, immediately navigate to the Splash/Auth screen with a return intent flag, restoring the session before any deep Activity code runs."
        ),
        "follow_ups": [
            {
                "interviewer": "What is the Developer Option 'Don't keep activities' and does it simulate process death?",
                "answer": "'Don't keep activities' only simulates Activity lifecycle destruction and recreation across configuration changes; it does NOT kill the underlying Linux process or wipe in-memory singletons. Full process death must be simulated using `adb shell am kill`."
            },
            {
                "interviewer": "Why does Android restore internal screens instead of always restarting from the launcher?",
                "answer": "To provide a seamless multitasking user experience. If a user was composing an email or editing a profile, Android attempts to bring them back to their exact work in progress rather than kicking them back to the home screen."
            },
            {
                "interviewer": "How do you test this scenario in automated CI/CD UI tests?",
                "answer": "In Espresso or UI Automator tests, invoke `UiDevice.getInstance().pressHome()`, execute the shell command `am kill`, and then reopen the app from the recent task switcher."
            }
        ]
    },
    {
        "id": "AND-23",
        "arabic_explanation": (
            "عندما يحتاج كائن كلاس Singleton إلى كائن `Context`: كيف تختار دورة الحياة الصحيحة وتمنع تسريب الذاكرة (Memory Leak)؟\n\n"
            "1. القاعدة الذهبية الصارمة:\n"
            "   - **الـ Singleton يجب أن يحتفظ حصرياً بـ `Application Context`! (Always use applicationContext).**\n"
            "   - **ممنوع تماماً** أن يحتفظ الـ Singleton بـ `Activity Context`!\n\n"
            "2. لماذا يعد الاحتفاظ بـ Activity Context كارثة؟\n"
            "   - الـ Singleton يعيش طوال فترة تشغيل التطبيق في الذاكرة (Process Lifetime).\n"
            "   - الـ Activity تموت وتُدمر عند التدوير أو عند إغلاق الشاشة.\n"
            "   - إذا احتفظ الـ Singleton بـ Activity Context، فإن الـ Garbage Collector لن يستطيع تحرير الـ Activity المدمرة أبداً لأن الـ Singleton ممسك بها!\n"
            "   - النتيجة: تسريب الـ Activity وشجرة الـ Views والرسومات، وحدوث OutOfMemoryError.\n\n"
            "3. كيفية تطبيق ذلك في الكود:\n"
            "   - عند استقبال Context في الـ Constructor، استخرج منه فوراً: `context.applicationContext`.\n"
            "   - في Dagger/Hilt: استخدم Qualifier الإلزامي `@ApplicationContext`."
        ),
        "practical_walkthrough": (
            "كتابة كلاس Singleton آمن من التسريب بنسبة 100%:\n"
            "```kotlin\n"
            "// ❌ تصميم كارثي يسرب الـ Activity:\n"
            "class BadAnalyticsTracker(private val context: Context) { // لو تم تمرير Activity ستتسرب للأبد!\n"
            "    companion object {\n"
            "        var instance: BadAnalyticsTracker? = null\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ التصميم السليم باستخدام Application Context:\n"
            "@Singleton\n"
            "class SafeAnalyticsTracker @Inject constructor(\n"
            "    @ApplicationContext context: Context // Hilt يحقن Application Context حصرياً\n"
            ") {\n"
            "    private val appContext = context.applicationContext // استخراج آمن دفاعي\n"
            "    \n"
            "    fun logEvent(name: String) {\n"
            "        val prefs = appContext.getSharedPreferences(\"analytics\", Context.MODE_PRIVATE)\n"
            "        // آمن تماماً ولا يسرب أي شاشة\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "A Singleton must strictly retain the Application Context (context.applicationContext), never an Activity Context. Storing an Activity Context inside a process-lived Singleton creates a catastrophic memory leak by preventing destroyed Activities and their view trees from being garbage collected.",
        "best_answer": (
            "When a Singleton requires a `Context`, it must strictly and exclusively hold the **`Application Context`**.\n\n"
            "The lifecycle principle is: **Never retain a shorter-lived context inside a longer-lived component**.\n\n"
            "A Singleton lives for the entire duration of the Linux app process. An Activity Context is transient, destroyed whenever the user presses Back or rotates the screen. If a Singleton retains a reference to an Activity Context, that Activity and its entire attached View hierarchy, drawables, and window managers can never be reclaimed by the garbage collector, causing severe memory leaks and eventual `OutOfMemoryError` crashes.\n\n"
            "To enforce safety:\n\n"
            "1. In plain Kotlin constructors, always call `context.applicationContext` defensively.\n"
            "2. In Dagger/Hilt, inject `@ApplicationContext context: Context`.\n\n"
            "The Application Context is safe to retain because it already shares the same lifespan as the application process."
        ),
        "deep_answer": (
            "At the memory profiling level, LeakCanary flags this defect under the pattern: `Leaking instance of MainActivity held by Singleton.instance.context`.\n\n"
            "However, you must be aware of what `ApplicationContext` **cannot** do inside a Singleton:\n\n"
            "- It cannot display Dialogs (throws `BadTokenException`).\n"
            "- It cannot resolve Activity theme styles and attributes.\n"
            "- It cannot launch activities without `FLAG_ACTIVITY_NEW_TASK`.\n\n"
            "If your Singleton needs to trigger UI operations (like showing a dialog), it must not do so directly. "
            "Instead, the Singleton should expose a `StateFlow` or `Channel` of UI events, and let the active, foreground Activity collect those events and display the UI using its own legitimate Activity Context."
        ),
        "follow_ups": [
            {
                "interviewer": "What happens if someone passes an Activity Context into `context.applicationContext`?",
                "answer": "Calling `.applicationContext` traverses the context wrapper chain and returns the root Application singleton, completely stripping the Activity reference and safely preventing the leak."
            },
            {
                "interviewer": "Can a Singleton use a WeakReference to hold an Activity Context?",
                "answer": "Yes, but it is fragile. If the user rotates the device, the weak reference clears to null, and any operations attempting to use the context will fail or require defensive null-checks everywhere. Observing events via Flows is far cleaner architecture."
            },
            {
                "interviewer": "How do you detect Context leaks in automated testing?",
                "answer": "By integrating `LeakCanary` in debug builds or running automated instrumentation tests with LeakCanary's `DetectLeaksAfterTestSuccess` test rule."
            }
        ]
    },
    {
        "id": "AND-24",
        "arabic_explanation": (
            "فحص وتأمين الروابط العميقة غير الموثوقة (Untrusted Deep Links) قبل التنقل هو أحد أهم اختبارات الأمان في تطبيقات أندرويد لمنع ثغرات الـ Phishing والـ Injection:\n\n"
            "1. ما هي المخاطر الأمنية في الـ Deep Links غير الموثوقة؟\n"
            "   - الـ Deep Link يمكن أن يأتي من رابط ويب خبيث، رسالة SMS تصيد احتيالي، أو تطبيق خبيث على هاتف المستخدم.\n   - **تجاوز المصادقة (Auth Bypass):** رابط يفتح `myapp://checkout/confirm?orderId=123` ويقوم بالشراء بدون التحقق من تسجيل دخول المستخدم.\n   - **هجمات الـ Path Traversal و Parameter Tampering:** التلاعب بالـ URL Parameters لتغيير حساب المستلم أو سرقة بيانات.\n   - **الـ Open Redirect:** رابط خبيث يوجه الـ WebView الداخلي لفتح موقع خارجي مزيف وسرقة بيانات الدفع.\n\n"
            "2. ما هي إجراءات التحقق الإلزامية (The 4-Step Validation Pipeline)؟\n"
            "   - **1. التحقق من المخطط والنطاق (Scheme & Host Validation):** التأكد من أن الرابط يطابق الـ Host الشرعي، وتفضيل Android App Links الموثقة (`https://example.com`).\n   - **2. فحص مسار الوجهة (Path Whitelisting):** مطابقة الـ Path مع قائمة بيضاء صارمة للمسارات المسموح بها في التطبيق.\n   - **3. فحص وتطهير المعاملات (Parameter Sanitization):** التحقق من صحة المعرفات (مثل التأكد من أن `orderId` رقم صالح ولا يحتوي على أكواد حقن).\n   - **4. فحص جلسة المستخدم (Authentication Gate):** التحقق من أن المستخدم مسجل للدخول قبل فتح الشاشات الحساسة؛ وإذا لم يكن مسجلاً، توجيهه لصفحة الدخول أولاً."
        ),
        "practical_walkthrough": (
            "تنفيذ معالج Deep Link آمن في الكود:\n"
            "```kotlin\n"
            "class DeepLinkHandler {\n"
            "    fun parseAndValidate(uri: Uri?, session: UserSession): NavigationTarget? {\n"
            "        if (uri == null) return null\n"
            "        \n"
            "        // 1. التحقق من الـ Host:\n"
            "        if (uri.host != \"app.mycompany.com\") return null\n"
            "        \n"
            "        // 2. مطابقة المسارات مع القائمة البيضاء:\n"
            "        return when (uri.path) {\n"
            "            \"/product\" -> {\n"
            "                val id = uri.getQueryParameter(\"id\")\n"
            "                // 3. التحقق من المعامل:\n"
            "                if (!id.isNullOrBlank() && id.all { it.isLetterOrDigit() }) {\n"
            "                    NavigationTarget.ProductDetails(id)\n"
            "                } else null\n"
            "            }\n"
            "            \"/profile\" -> {\n"
            "                // 4. بوابة المصادقة الحساسة:\n"
            "                if (session.isLoggedIn) NavigationTarget.Profile else NavigationTarget.Login(redirectTo = \"profile\")\n"
            "            }\n"
            "            else -> null // رفض أي مسار غير معتمد\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Validate untrusted deep links by verifying the scheme and host, strictly whitelisting allowed path patterns, sanitizing all query parameters to prevent injection or path traversal, and enforcing an authentication gateway before navigating to protected screens.",
        "best_answer": (
            "Deep links are inherently untrusted external input that must undergo rigorous security validation before driving navigation:\n\n"
            "1. **Scheme & Host Whitelisting**: Verify that incoming URIs strictly match authorized domains. Prefer verified Android App Links (`https://`) backed by `assetlinks.json` over custom schemes (`myapp://`), which any malicious app can register and hijack.\n\n"
            "2. **Strict Path Routing**: Route exclusively against a hardcoded whitelist of allowed destination paths. Never use dynamic reflection or generic string concatenation to instantiate activities from deep link path segments.\n\n"
            "3. **Query Parameter Sanitization**: Validate types and bounds on all parameters (e.g., verifying `id` matches expected alphanumeric UUID formats) to prevent SQL injection or path traversal attacks.\n\n"
            "4. **Authentication and Authorization Gate**: Never assume an authenticated session when processing deep links. If a deep link targets an authenticated screen (like Account Settings or Checkout), the navigation handler must verify active credentials. If unauthenticated, redirect to the Login flow, caching the target route to resume upon successful authentication."
        ),
        "deep_answer": (
            "From an application security standpoint, special care must be taken with **Embedded WebViews** opened via deep links. "
            "If a deep link accepts a parameter like `myapp://webview?url=https://...`, an attacker can craft a link pointing to a phishing website (`https://evil-phishing.com`). "
            "If the internal WebView has JavaScript interfaces enabled (`addJavascriptInterface`), the external website can execute code within the app's context.\n\n"
            "To secure WebView deep links: "
            "1. Strictly enforce domain whitelisting on all target URLs. "
            "2. Never pass arbitrary query parameters directly into database queries or IPC intents without strict parsing. "
            "3. Ensure the receiving Activity validates incoming extras before forwarding them to internal exported components."
        ),
        "follow_ups": [
            {
                "interviewer": "Why are custom URI schemes like `myapp://` considered insecure?",
                "answer": "Because Android does not verify ownership of custom URI schemes. Multiple apps can register `myapp://` in their manifests, allowing a rogue app to intercept user clicks and steal sensitive parameters (like OAuth tokens)."
            },
            {
                "interviewer": "How do Android App Links fix that vulnerability?",
                "answer": "Android App Links use HTTPS domain verification via Digital Asset Links (`.well-known/assetlinks.json`) on your website. Android verifies that your app's signing certificate matches the website's asset links before allowing it to open automatically without user prompts."
            },
            {
                "interviewer": "What is Open Redirect vulnerability in mobile apps?",
                "answer": "An Open Redirect occurs when an app accepts an unvalidated target URL parameter in a deep link and redirects its internal navigation or WebView to that URL, exposing users to phishing attacks."
            }
        ]
    },
    {
        "id": "AND-25",
        "arabic_explanation": (
            "دعم التنقل القابل للتنبؤ (Predictable Navigation) بعد النقر على الإشعارات وإعادة إنشاء العمليات (Process Recreation):\n\n"
            "1. المشكلة التي يواجهها المستخدمون (The Broken Navigation Bug):\n"
            "   - المستخدم ضغط على إشعار وصله: 'تم شحن طلبك #1234'.\n"
            "   - التطبيق فتح شاشة 'تفاصيل الطلب' مباشرة.\n"
            "   - المستخدم ضغط زر الرجوع (Back button) متوقعاً العودة إلى شاشة 'قائمة الطلبات' أو 'الصفحة الرئيسية':\n"
            "   - **الكارثة:** التطبيق أُغلق فجأة وخرج لشاشة الهاتف الرئيسية (Home screen) لأن الـ Backstack لا يحتوي إلا على شاشة التفاصيل فقط!\n\n"
            "2. الحل المعماري القياسي: `TaskStackBuilder`:\n"
            "   - نظام أندرويد يوفر **`TaskStackBuilder`** لبناء **Synthetic Backstack (سجل تنقل اصطناعي كامل)**.\n"
            "   - يتيح لك تحديد الشاشة المستهدفة مع تحديد شاشاتها الأب (Parent Activities) المحددة في الـ `AndroidManifest.xml` عبر `android:parentActivityName`.\n"
            "   - عندما يفتح المستخدم الإشعار ويضغط 'Back'، النظام يعيده للشاشة الأب بشكل طبيعي ومنطقي كأنه دخل إليها بنفسه!\n\n"
            "3. التنفيذ في Jetpack Compose و Navigation Component:\n"
            "   - استخدام `NavDeepLinkBuilder` لبناء نفس السجل الاصطناعي مع دوال الـ Composable."
        ),
        "practical_walkthrough": (
            "بناء Synthetic Backstack حقيقي للإشعارات باستخدام `TaskStackBuilder`:\n"
            "```kotlin\n"
            "fun createOrderNotification(context: Context, orderId: String): Notification {\n"
            "    // 1. إنشاء Intent الشاشة المستهدفة:\n"
            "    val detailsIntent = Intent(context, OrderDetailsActivity::class.java).apply {\n"
            "        putExtra(\"order_id\", orderId)\n"
            "    }\n"
            "\n"
            "    // 2. استخدام TaskStackBuilder لبناء السجل الهرمي للأب:\n"
            "    val pendingIntent = TaskStackBuilder.create(context).run {\n"
            "        // يقرأ parentActivityName من الـ Manifest (مثلاً HomeActivity):\n"
            "        addNextIntentWithParentStack(detailsIntent)\n"
            "        getPendingIntent(0, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)\n"
            "    }\n"
            "\n"
            "    // 3. بناء الإشعار مع الـ PendingIntent:\n"
            "    return NotificationCompat.Builder(context, CHANNEL_ID)\n"
            "        .setContentTitle(\"Order Shipped!\")\n"
            "        .setContentIntent(pendingIntent)\n"
            "        .setAutoCancel(true)\n"
            "        .build()\n"
            "}\n"
            "```\n"
            "في Compose Navigation: نستخدم `navController.createDeepLink().setDestination(R.id.order_details).createPendingIntent()`."
        ),
        "quick_answer": "Support predictable notification navigation using TaskStackBuilder (or NavDeepLinkBuilder in Compose). This creates a synthetic backstack based on parentActivityName declarations, ensuring that pressing Back from a notification-opened detail screen navigates up to the logical parent screen rather than exiting the application.",
        "best_answer": (
            "To support predictable navigation when users tap notifications—even after process death—we construct a **Synthetic Backstack** using **`TaskStackBuilder`** or **`NavDeepLinkBuilder`**.\n\n"
            "If you launch a detail screen directly via a plain Intent from a notification, that Activity becomes the sole task root. When the user taps Back, the application exits immediately to the OS launcher, violating user expectations of hierarchical navigation.\n\n"
            "`TaskStackBuilder` resolves this:\n\n"
            "1. In `AndroidManifest.xml`, we declare hierarchical parent relationships using `android:parentActivityName=\".MainActivity\"`.\n"
            "2. When building the notification's PendingIntent, we use `TaskStackBuilder.create(context).addNextIntentWithParentStack(detailIntent).getPendingIntent(...)`.\n"
            "3. The OS constructs a synthetic task stack: when the notification is tapped, Android launches the detail screen, but synthesizes the parent Activity below it on the backstack. Pressing Back smoothly navigates the user up to the parent list or home screen."
        ),
        "deep_answer": (
            "In modern Jetpack Navigation and Compose, this is streamlined via `NavDeepLinkBuilder`:\n\n"
            "```kotlin\n"
            "val pendingIntent = NavDeepLinkBuilder(context)\n"
            "    .setGraph(R.navigation.nav_graph)\n"
            "    .setDestination(R.id.orderDetailsFragment)\n"
            "    .setArguments(bundleOf(\"order_id\" to orderId))\n"
            "    .createPendingIntent()\n"
            "```\n\n"
            "Under the hood, `NavDeepLinkBuilder` inspects the navigation graph hierarchy and pushes all antecedent destinations onto the synthetic `NavController` backstack. "
            "Even if the process was completely dead when the notification was clicked, Android starts the single Activity and initializes the full navigation stack, allowing fluid Back and Up navigation across the entire application."
        ),
        "follow_ups": [
            {
                "interviewer": "What is the difference between the Up button (toolbar arrow) and the Back button?",
                "answer": "The Up button strictly navigates up the logical hierarchical screen structure within your application (defined by parentActivityName). The Back button navigates through the chronological temporal history of screens the user visited."
            },
            {
                "interviewer": "What happens if you don't declare `parentActivityName` when using `TaskStackBuilder`?",
                "answer": "`TaskStackBuilder` won't know which parent activities to synthesize, and will only launch the target Intent, falling back to exiting on Back press unless parent intents are added manually via `addNextIntent()`."
            },
            {
                "interviewer": "How do you handle deep links in notifications with Navigation Compose?",
                "answer": "Using deep link URIs attached to composable destinations (`composable(\"order/{id}\", deepLinks = listOf(navDeepLink { uriPattern = ... }))`) and setting the deep link URI on the notification Intent."
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

    for q in AND_19_25:
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
    print(f"Updated {DATA_FILE} with questions AND-19 to AND-25. Total questions: {len(combined)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generator for AND-07 through AND-12 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "and.json"

AND_07_12 = [
    {
        "id": "AND-07",
        "arabic_explanation": (
            "الفرق بين الـ Process Death وتغيير الإعدادات (Configuration Change) هو أحد أدق الأسئلة التي تميز الـ Senior Engineer الحقيقي عن غيره:\n\n"
            "1. ما هو الـ Process Death؟\n"
            "   - عندما يضع المستخدم تطبيقك في الخلفية (Background) ويفتح ألعاباً أو تطبيقات أخرى تستهلك الرام (RAM):\n"
            "   - يقوم نظام أندرويد (Low Memory Killer Daemon - LMKD) بـ **قتل الـ Linux Process الخاص بتطبيقك بالكامل من الذاكرة** لتوفير الرام للنظام!\n"
            "   - عند مقتل الـ Process: **كل شيء في الذاكرة يموت تماماً!** الـ Singletons، الكاش، والـ **ViewModels تموت وتُمحى من الـ Heap**!\n\n"
            "2. ما الفرق الجوهري بينه وبين Configuration Change؟\n"
            "   - في الـ Configuration Change (التدوير): الـ Process يظل حياً؛ والـ **ViewModel ينجو تماماً في الذاكرة**.\n"
            "   - في الـ Process Death: الـ Process يموت بالكامل؛ والـ **ViewModel يضيع تماماً ولا ينجو**!\n\n"
            "3. كيف يستعيد المستخدم شاشته بعد الـ Process Death؟\n"
            "   - عندما يضغط المستخدم على التطبيق في قائمة الـ Recent Apps، يقوم النظام بإنشاء New Process جديد، وينشئ New Activity، ويحقن بداخلها الـ **SavedInstanceState Bundle** الذي احتفظ به نظام التشغيل في عملية النظام (System Server) قبل القتل.\n"
            "   - الأداة المنقذة: **`SavedStateHandle`** في الـ ViewModel لحفظ المعرفات وحقول الإدخال."
        ),
        "practical_walkthrough": (
            "كيف تختبر الـ Process Death في Android Studio وتكتشف الـ Crashes:\n"
            "1. افتح شاشة تفاصيل المنتج في التطبيق.\n"
            "2. اضغط زر الـ Home لوضع التطبيق في الـ Background.\n"
            "3. في Terminal شغل الأمر:\n"
            "   `adb shell am kill com.example.myapp`\n"
            "   (أو اضغط علامة الجمجمة/Stop Process في نافذة Logcat).\n"
            "4. افتح التطبيق مجدداً من الـ Recent Apps.\n"
            "5. **النتيجة الكارثية لو الكود غير محمي:** التطبيق يعمل Crash بـ `NullPointerException` لأن الـ ViewModel تم إنشاؤه من جديد وكل المتغيرات فارغة!\n"
            "6. **الحل:** قراءة `productId` من `SavedStateHandle` لإعادة تحميل البيانات تلقائياً."
        ),
        "quick_answer": "In configuration change, the Activity is recreated but the Linux process and ViewModel survive in memory. In process death, the OS kernel kills the entire process due to low RAM, destroying all ViewModels and singletons; only state serialized into the SavedStateHandle Bundle survives in the OS system server.",
        "best_answer": (
            "The distinction between configuration change and process death lies at the operating system memory boundary:\n\n"
            "**Configuration Change** (e.g., screen rotation) is a cosmetic runtime change. The Activity instance is recreated, but the underlying Linux process remains alive. The `ViewModelStore` preserves all ViewModels, `viewModelScope` coroutines, in-memory singletons, and cache trees in RAM without data loss.\n\n"
            "**Process Death** occurs when the app is in the background and the Android Low Memory Killer (LMK) terminates the entire Linux process to reclaim RAM for foreground apps. Everything residing in memory—all ViewModels, Dagger/Hilt instances, and static variables—is permanently erased.\n\n"
            "When the user returns to the app, the OS creates a brand-new process. The only bridge connecting the dead process to the new one is the **Saved Instance State Bundle**, which the OS system server serialized before killing the process. We access this restored state in modern architecture via `SavedStateHandle`."
        ),
        "deep_answer": (
            "At the kernel level, Android assigns an Out-Of-Memory Adjacency score (`oom_adj`) to every process. Foreground apps have low scores (never killed), while background apps have high scores. "
            "When native RAM runs low, LMKD sends `SIGKILL` directly to background processes. This means no Java cleanup methods, `onCleared()`, or `onDestroy()` hooks run during process death.\n\n"
            "Before killing the process, the OS invokes `Activity.onSaveInstanceState(Bundle)`. The serialized Bundle is transferred across Binder IPC to `system_server`. "
            "Because Binder transactions have a strict 1MB transaction buffer limit across the entire system, saving large bitmaps or heavy lists in `SavedStateHandle` causes a `TransactionTooLargeException`.\n\n"
            "Therefore, the golden rule of state preservation is: store large data in Room or local disk storage; store only lightweight IDs (e.g., `userId: String`) and draft inputs in `SavedStateHandle`."
        ),
        "follow_ups": [
            {
                "interviewer": "Why does a ViewModel fail to survive process death if it survives rotation?",
                "answer": "Because a ViewModel lives on the JVM heap of the app's Linux process. Rotation preserves the process, so the heap survives. Process death terminates the Linux process and wipes the JVM heap entirely."
            },
            {
                "interviewer": "How do you test process death deterministically in development?",
                "answer": "By putting the app in the background and executing `adb shell am kill <package_name>`, or enabling 'Don't keep activities' in Developer Options (which simulates lifecycle destruction) combined with adb process termination."
            },
            {
                "interviewer": "Does `rememberSaveable` survive process death in Jetpack Compose?",
                "answer": "Yes! `rememberSaveable` serializes values into Android's `onSaveInstanceState` Bundle mechanism under the hood, restoring them safely across both configuration change and process death."
            }
        ]
    },
    {
        "id": "AND-08",
        "arabic_explanation": (
            "الـ `ViewModel` في Android Jetpack هو حجر الأساس لإدارة الحالة، وفهم توقيت استدعاء `onCleared()` بدقة يمنع تسريب الموارد:\n\n"
            "1. ما هو الـ ViewModel؟\n"
            "   - هو فئة مصممة لتخزين وإدارة البيانات المرتبطة بواجهة المستخدم (UI-related data) بطريقة **تتحمل تدوير الشاشة (Lifecycle-conscious)**.\n"
            "   - يفصل الـ Business Logic وتجهيز البيانات عن الـ Activity والـ Fragment.\n\n"
            "2. أين يتم تخزينه وكيف ينجو من التدوير؟\n"
            "   - يتم تخزينه داخل **`ViewModelStore`** يمتلكه الـ `ViewModelStoreOwner` (مثل الـ Activity أو Fragment).\n"
            "   - عند تدوير الشاشة، النظام يدمر الـ Activity القديمة، ولكن الـ `ViewModelStore` يتم تمريره للـ Activity الجديدة بدون مساس، فيظل الـ ViewModel كما هو في الـ Heap.\n\n"
            "3. متى يتم مسحه واستدعاء `onCleared()` تحديداً؟\n"
            "   - يتم استدعاء `onCleared()` **فقط عندما تنتهي الشاشة نهائياً ولا تعود أبداً (Permanently Finished)**:\n"
            "     * عندما يضغط المستخدم زر الرجوع (Back) وتنتهي الـ Activity (`activity.isFinishing == true`).\n"
            "     * عندما يتم حذف الـ Fragment نهائياً من الـ FragmentManager بدون وضعه في الـ Backstack.\n"
            "     * عندما تنتهي وجهة الـ Navigation في Jetpack Compose ويتم إخراجها من الـ NavBackStackEntry.\n"
            "   - عند استدعاء `onCleared()`: يتم إلغاء الـ `viewModelScope` تلقائياً وإلغاء كافة الـ Coroutines التابعة له."
        ),
        "practical_walkthrough": (
            "دورة حياة الـ ViewModel في الكود:\n"
            "```kotlin\n"
            "class ChatViewModel(private val chatSocket: ChatSocket) : ViewModel() {\n"
            "    init {\n"
            "        // 1. يبدأ الاتصال بالـ Socket:\n"
            "        chatSocket.connect()\n"
            "    }\n"
            "\n"
            "    override fun onCleared() {\n"
            "        super.onCleared()\n"
            "        // 2. onCleared تستدعى فقط عند مغادرة الشاشة نهائياً:\n"
            "        chatSocket.disconnect() // تنظيف المقابس والموارد غير المدارة\n"
            "        Log.d(\"ChatVM\", \"ViewModel cleared permanently!\")\n"
            "    }\n"
            "}\n"
            "```\n"
            "لو دور المستخدم الشاشة 100 مرة: `onCleared()` لن تستدعى ولا مرة! ستستدعى مرة واحدة فقط عندما يضغط المستخدم 'Back' ويغادر شاشة المحادثة."
        ),
        "quick_answer": "ViewModel stores and manages UI state across configuration changes, retained in memory by the ViewModelStore. Its onCleared() callback is invoked exclusively when the host lifecycle permanently finishes (e.g. Activity finishes or Fragment popped from backstack), cancelling viewModelScope automatically.",
        "best_answer": (
            "A Jetpack ViewModel is designed to hold and manage UI-related state in a lifecycle-conscious way, surviving configuration changes and decoupling business logic from UI controllers.\n\n"
            "It survives configuration changes because it is retained by a `ViewModelStore`. During rotation, Android passes the `ViewModelStore` from the destroyed Activity to the newly created Activity via `onRetainNonConfigurationInstance()`.\n\n"
            "**When it is cleared (`onCleared()`):**\n"
            "`onCleared()` is invoked when the associated `ViewModelStoreOwner` is permanently finished and destroyed:\n\n"
            "1. When an Activity finishes intentionally (user taps Back or `finish()` is called, where `isFinishing == true`).\n"
            "2. When a Fragment is permanently removed or popped from the backstack.\n"
            "3. When a Jetpack Compose navigation route (`NavBackStackEntry`) is popped from the backstack.\n\n"
            "When cleared, the framework automatically cancels the built-in `viewModelScope`, cleaning up all active coroutines."
        ),
        "deep_answer": (
            "Under the hood, `ViewModelProvider` retrieves existing ViewModels from `ViewModelStore` using a String key (e.g., `androidx.lifecycle.ViewModelProvider.DefaultKey:MyViewModel`). "
            "If an instance exists, it returns the existing object without invoking the constructor. If not, it uses the `ViewModelProvider.Factory` to instantiate it.\n\n"
            "In modern multi-fragment or Compose architectures, you can scope ViewModels to different owners: "
            "- **Activity-scoped (`activityViewModels()`):** Shares state across sibling fragments or tabs. "
            "- **Navigation Graph-scoped (`navGraphViewModels(R.id.checkout_graph)`):** Scopes the ViewModel to a specific multi-step user flow (like Checkout). When the flow finishes, the ViewModel clears automatically, releasing memory. "
            "- **Fragment/Destination-scoped:** Clears when that specific screen terminates."
        ),
        "follow_ups": [
            {
                "interviewer": "Can a ViewModel hold a reference to an Activity or View?",
                "answer": "Never! Holding an Activity, View, or context reference inside a ViewModel creates a direct memory leak: when the Activity rotates and destroys its view, the ViewModel retains the dead Activity in memory, preventing garbage collection."
            },
            {
                "interviewer": "What is `AndroidViewModel` and when is it acceptable?",
                "answer": "`AndroidViewModel` includes a reference to `ApplicationContext`. It is acceptable if you need an Application Context for system services, but plain ViewModel with an injected context via Hilt is considered much cleaner architecture."
            },
            {
                "interviewer": "Does `onCleared()` get called during Process Death?",
                "answer": "No. When the OS terminates an application process via low memory kill (SIGKILL), the process dies instantly; neither onDestroy() nor onCleared() callbacks are executed."
            }
        ]
    },
    {
        "id": "AND-09",
        "arabic_explanation": (
            "المقارنة الشاملة بين أدوات حفظ الحالة الأربعة في أندرويد:\n\n"
            "1. الـ `ViewModel`:\n"
            "   - **مكان الحفظ:** في الذاكرة الحية (JVM Heap Memory).\n"
            "   - **ماذا ينجو منه؟** ينجو من الـ Configuration Changes فقط.\n"
            "   - **هل ينجو من Process Death؟** **لا!** يضيع بالكامل.\n"
            "   - **الاستخدام:** البيانات الكبيرة، الـ UI State المعقد، والعمليات الجارية في `viewModelScope`.\n\n"
            "2. الـ `SavedStateHandle`:\n"
            "   - **مكان الحفظ:** في الـ OS System Server عبر `onSaveInstanceState` (Bundle Serialized).\n"
            "   - **ماذا ينجو منه؟** ينجو من الـ Configuration Changes **وينجو من الـ Process Death**!\n"
            "   - **حدوده:** محكوم بسعة الـ Binder Buffer (حوالي 50-100KB كحد أقصى للسلامة)؛ مخصص للمعرفات الصغيرة (IDs) والمدخلات النصية فقط.\n\n"
            "3. الـ `rememberSaveable` (في Compose):\n"
            "   - **مكان الحفظ:** في الـ `SaveableStateRegistry` المربوط بـ Bundle الـ Activity.\n"
            "   - **ماذا ينجو منه؟** ينجو من الـ Configuration Changes و Process Death داخل واجهة Compose.\n"
            "   - **الاستخدام:** حالة الـ UI المحلية الخاصة بـ Composable معين (مثل: هل القائمة مفتوحة، موضع الـ Scroll).\n\n"
            "4. الـ Persistent Storage (Room / DataStore / Files):\n"
            "   - **مكان الحفظ:** على القرص الصلب (Flash Storage / Disk).\n"
            "   - **ماذا ينجو منه؟** ينجو من كل شيء: Process Death، إعادة تشغيل الهاتف، وإغلاق التطبيق لأسابيع.\n"
            "   - **الاستخدام:** البيانات الحيوية، المقالات، التوكنز، والإعدادات الدائمة."
        ),
        "practical_walkthrough": (
            "جدول مقارنة معماري واضح:\n"
            "| المعيار | ViewModel | SavedStateHandle | rememberSaveable | Room / DataStore |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n"
            "| **مكان التخزين** | RAM (Heap) | OS Bundle (Binder) | OS Bundle (Binder) | Disk (Flash) |\n"
            "| **ينجو من التدوير؟** | نعم | نعم | نعم | نعم |\n"
            "| **ينجو من Process Death؟** | لا | نعم | نعم | نعم |\n"
            "| **ينجو من Reboot الجهاز؟** | لا | لا | لا | نعم |\n"
            "| **السرعة** | فورية (O(1) memory) | سريعة (Serialization) | سريعة | أبطأ (Disk I/O) |\n"
            "| **حدود الحجم** | حجم الـ Heap المتاح | < 50 KB | < 50 KB | جيجابايت |"
        ),
        "quick_answer": "ViewModel stores complex state in RAM across rotation but dies on process death; SavedStateHandle serializes lightweight IDs in OS Bundles to survive process death; rememberSaveable does the same for local Compose UI state; and Persistent Storage (Room/DataStore) saves arbitrary data to disk across app reboots.",
        "best_answer": (
            "These four state mechanisms represent distinct tiers across longevity, storage location, and size limits:\n\n"
            "1. **`ViewModel`**: Resides in RAM heap. Survives configuration changes, but is completely destroyed upon process death. Ideal for rich domain models, complex UI states, and active coroutine streams.\n\n"
            "2. **`SavedStateHandle`**: Integrated into the ViewModel, backed by Android's `onSaveInstanceState` Bundle in the OS system server. Survives both configuration change and process death. Strictly bounded by Binder IPC limits (<50KB), ideal for saving navigation arguments, active search text, and record IDs.\n\n"
            "3. **`rememberSaveable`**: Compose's UI-layer equivalent of `SavedStateHandle`. Restores transient Composable UI state (scroll positions, expanded dropdown flags, tab indices) across rotation and process death.\n\n"
            "4. **Persistent Storage (Room / DataStore)**: Written directly to flash storage on disk. Survives process death, device reboots, and app updates. Used for domain databases, offline caching, and user authentication credentials."
        ),
        "deep_answer": (
            "Architecturally, a well-engineered screen orchestrates all four in harmony:\n\n"
            "```kotlin\n"
            "class OrderViewModel(savedStateHandle: SavedStateHandle, repository: OrderRepository) : ViewModel() {\n"
            "    // 1. SavedStateHandle: يسترجع ID الطلب بعد process death بأمان:\n"
            "    private val orderId: String = checkNotNull(savedStateHandle[\"order_id\"])\n"
            "    \n"
            "    // 2. Room (Persistent Storage): جلب بيانات الطلب من الديسك:\n"
            "    // 3. ViewModel: حفظ الـ StateFlow في الرام أثناء التدوير:\n"
            "    val orderState: StateFlow<OrderUiState> = repository.observeOrder(orderId)\n"
            "        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), OrderUiState.Loading)\n"
            "}\n"
            "```\n\n"
            "In Compose, `rememberSaveable` manages the local UI scroll state, `SavedStateHandle` tracks the screen's core query, `ViewModel` manages the active stream, and `Room` provides the durable data."
        ),
        "follow_ups": [
            {
                "interviewer": "What error occurs if you put too much data in `SavedStateHandle`?",
                "answer": "`TransactionTooLargeException`. The Android Binder buffer is shared across all inter-process communications with a maximum limit of approximately 1MB total. Storing large lists in SavedStateHandle causes immediate crashes."
            },
            {
                "interviewer": "Can custom objects be saved in `SavedStateHandle`?",
                "answer": "Yes, if they implement `Parcelable` or `Serializable`, or by providing a custom `SavedStateRegistry.AutoSavedStateProvider`."
            },
            {
                "interviewer": "How does `rememberSaveable` handle custom classes in Compose?",
                "answer": "By providing a custom `Saver` object: `rememberSaveable(stateSaver = MyCustomSaver) { mutableStateOf(MyObject()) }`."
            }
        ]
    },
    {
        "id": "AND-10",
        "arabic_explanation": (
            "الـ `Intent` والـ `PendingIntent` هما رسائل التواصل بين المكونات في نظام Android:\n\n"
            "1. ما هو الـ `Intent`؟\n"
            "   - هو **كائن رسالة يصف نية لتنفيذ عملية (Messaging Object)**.\n"
            "   - **نوعان رئيسيان:**\n"
            "     * **Explicit Intent (صريح):** يحدد اسم الكلاس المستهدف بدقة داخل تطبيقك (`Intent(context, ProfileActivity::class.java)`). آمن وسريع.\n"
            "     * **Implicit Intent (ضمني):** يحدد **الأكشن المطلوب** بدون تحديد الكلاس (مثل: `ACTION_VIEW` لفتح رابط موقع، أو `ACTION_SEND` لمشاركة نص). نظام أندرويد يفحص التطبيقات المثبتة التي تدعم هذا الأكشن في الـ Intent Filter ويعرض للمستخدم قائمة للاختيار منها.\n\n"
            "2. ما هو الـ `PendingIntent`؟\n"
            "   - هو **رمز تفويض وتوكيل رسمي (Token of Authorization)** تمنحه لتطبيق خارجي أو لنظام التشغيل (مثل نظام الإشعارات أو Widget).\n"
            "   - يسمح للنظام أو التطبيق الخارجي بتنفيذ الـ Intent المحفوظ بداخله **باسم تطبيقك وبصلاحيات تطبيقك أنت (With your app's permissions and identity)** في وقت لاحق، حتى لو كان تطبيقك مغلقاً تماماً!\n\n"
            "3. الأمان الإلزامي في أندرويد الحديث (Android 12+):\n"
            "   - فرض تحديد `FLAG_IMMUTABLE` أو `FLAG_MUTABLE` عند إنشاء أي PendingIntent لمنع ثغرات التلاعب بالـ Intent."
        ),
        "practical_walkthrough": (
            "تطبيق عملي: فتح تفاصيل الطلب عند الضغط على Notification:\n"
            "```kotlin\n"
            "// 1. إنشاء Explicit Intent صريح للشاشة المستهدفة:\n"
            "val intent = Intent(context, OrderDetailsActivity::class.java).apply {\n"
            "    putExtra(\"order_id\", \"ORD-12345\")\n"
            "}\n"
            "\n"
            "// 2. تغليفه في PendingIntent وتفويض نظام الإشعارات لتشغيله:\n"
            "val pendingIntent = PendingIntent.getActivity(\n"
            "    context,\n"
            "    REQUEST_CODE,\n"
            "    intent,\n"
            "    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE // إلزامي في أندرويد 12+\n"
            ")\n"
            "\n"
            "// 3. إرفاقه بالإشعار:\n"
            "NotificationCompat.Builder(context, CHANNEL_ID)\n"
            "    .setContentIntent(pendingIntent) // عند ضغط المستخدم يفتح الشاشة بتصريح تطبيقك\n"
            "    .build()\n"
            "```"
        ),
        "quick_answer": "An Intent is an asynchronous messaging object requesting an action: Explicit specifies the exact target component, while Implicit declares an action for the OS to resolve. A PendingIntent is a security wrapper granting another application or the OS system server permission to execute your Intent with your app's identity and privileges in the future.",
        "best_answer": (
            "An **`Intent`** is an operational message that requests an action from an Android component:\n\n"
            "- **Explicit Intent**: Explicitly names the target component class (`Intent(context, TargetActivity::class.java)`). Used almost exclusively for internal application navigation.\n"
            "- **Implicit Intent**: Declares a general action to perform (e.g., `Intent.ACTION_DIAL` with `tel:123`, or `ACTION_SEND` for sharing). The Android OS queries all package manifests for matching `<intent-filter>` declarations and displays the system app chooser.\n\n"
            "A **`PendingIntent`** is a security token wrapping an Intent. It delegates execution permission to a foreign application or system process—most commonly `NotificationManager`, `AlarmManager`, or App Widgets. When triggered, the system executes the pre-configured Intent with the permissions and identity of *your application*, even if your app's process is currently dead."
        ),
        "deep_answer": (
            "At the systems and security architecture level, a `PendingIntent` is essentially an IPC handle referencing a token maintained by the system's `ActivityManagerService` (AMS). "
            "Because foreign apps execute it using your app's Linux UID, security vulnerabilities historically arose if malicious apps mutated the underlying intent parameters.\n\n"
            "Starting in Android 12 (API 31), the platform mandates declaring mutability flags on every `PendingIntent`:\n\n"
            "- **`FLAG_IMMUTABLE`**: The default standard. Freezes the Intent parameters completely; the receiving app or system cannot modify its extras or URI.\n"
            "- **`FLAG_MUTABLE`**: Allows callers to inject extra parameters via `fillIn()`. Only used in specialized features like notification inline replies or bubbles.\n\n"
            "Attempting to create a `PendingIntent` without declaring one of these flags on Android 12+ crashes immediately with an `IllegalArgumentException`."
        ),
        "follow_ups": [
            {
                "interviewer": "What is `FLAG_UPDATE_CURRENT` in a PendingIntent?",
                "answer": "If a PendingIntent with the same RequestCode and target already exists in the system server, `FLAG_UPDATE_CURRENT` keeps the existing token but updates its extra bundle with the new Intent's extras."
            },
            {
                "interviewer": "Why must you check `resolveActivity()` before calling `startActivity(implicitIntent)`?",
                "answer": "If an implicit Intent has no matching apps installed on the device (e.g., calling an email app on a device without email clients), calling `startActivity()` throws an unhandled `ActivityNotFoundException` crash. You must verify resolution or wrap it in a try-catch."
            },
            {
                "interviewer": "How does `FLAG_CANCEL_CURRENT` differ from `FLAG_UPDATE_CURRENT`?",
                "answer": "`FLAG_CANCEL_CURRENT` cancels the existing PendingIntent token entirely before creating a new one, ensuring any previous notifications holding that token are invalidated."
            }
        ]
    },
    {
        "id": "AND-11",
        "arabic_explanation": (
            "ملف `AndroidManifest.xml` هو عقد التأسيس والهوية الرسمية للتطبيق أمام نظام تشغيل Android:\n\n"
            "1. ما هو الدور الأساسي لـ `AndroidManifest.xml`؟\n"
            "   - هو **وثيقة التكوين الأساسية (Root Configuration Document)** التي يقرؤها الـ OS Package Manager عند تثبيت الـ APK.\n"
            "   - يخبر نظام التشغيل بكل مكونات وصلاحيات ومتطلبات التطبيق قبل تشغيل أي سطر كود!\n\n"
            "2. ما هي العناصر الرئيسية التي يعلن عنها؟\n"
            "   - **اسم الحزمة والهوية (Package & Application ID):** المعرف الفريد للتطبيق على مستوى النظام.\n"
            "   - **إعلان المكونات الأربعة (Component Registration):** كل Activity, Service, BroadcastReceiver, ContentProvider يجب إعلانها هنا (ما عدا الـ Dynamic BroadcastReceivers المسجلة برمجياً). المكون غير المعلن لن يستطيع النظام تشغيله إطلاقاً.\n"
            "   - **الأذونات والصلاحيات (Permissions):** إعلان الأذونات التي يطلبها التطبيق (`<uses-permission>`) والأذونات التي يفرضها على التطبيقات الأخرى لحماية مكوناته (`<permission>`).\n"
            "   - **متطلبات الهاردوير (Hardware Requirements):** مثل الحاجة للكاميرا أو مستشعر البصمة (`<uses-feature>`) لفلترة الأجهزة في Google Play Store.\n"
            "   - **الـ Intent Filters:** لتحديد أي طلبات عامة أو Deep Links أو أفعال يستطيع التطبيق استقبالها من النظام."
        ),
        "practical_walkthrough": (
            "هيكل واقعي لملف `AndroidManifest.xml` في تطبيق إنتاجي:\n"
            "```xml\n"
            "<manifest xmlns:android=\"http://schemas.android.com/apk/res/android\">\n"
            "    <!-- 1. الصلاحيات المطلوبة: -->\n"
            "    <uses-permission android:name=\"android.permission.INTERNET\" />\n"
            "    <uses-permission android:name=\"android.permission.POST_NOTIFICATIONS\" />\n"
            "\n"
            "    <application\n"
            "        android:name=\".AppApplication\"\n"
            "        android:theme=\"@style/Theme.MyApp\">\n"
            "        \n"
            "        <!-- 2. شاشة البداية مع Intent Filter: -->\n"
            "        <activity\n"
            "            android:name=\".MainActivity\"\n"
            "            android:exported=\"true\">\n"
            "            <intent-filter>\n"
            "                <action android:name=\"android.intent.action.MAIN\" />\n"
            "                <category android:name=\"android.intent.category.LAUNCHER\" />\n"
            "            </intent-filter>\n"
            "        </activity>\n"
            "    </application>\n"
            "</manifest>\n"
            "```"
        ),
        "quick_answer": "AndroidManifest.xml is the root declarative contract between the app and the Android OS. It declares the app's package identity, all 4 platform components, required system permissions (<uses-permission>), intent-filters for deep linking, hardware features, and security attributes like exported flags.",
        "best_answer": (
            "The `AndroidManifest.xml` file is the fundamental configuration contract between an application and the Android OS PackageManager.\n\n"
            "Before launching any application code, the OS parses this manifest at installation time to understand the app's capabilities, entry points, and security boundaries:\n\n"
            "1. **Component Registration**: All Activities, Services, and ContentProviders (plus manifest-declared BroadcastReceivers) must be declared here. Attempting to start an undeclared Activity crashes with `ActivityNotFoundException`.\n"
            "2. **Permissions**: Declares user permissions required by the app (`<uses-permission>`), such as INTERNET, CAMERA, or POST_NOTIFICATIONS, as well as custom permissions defined by the app to protect its own components.\n"
            "3. **Hardware Filtering (`<uses-feature>`)**: Dictates hardware prerequisites (like Bluetooth LE or NFC) that Google Play uses to filter out incompatible devices.\n"
            "4. **Intent Filters**: Exposes entry points to the OS, such as the launcher icon, deep links, or sharing handlers.\n"
            "5. **Application Attributes**: Configures app-wide behavior such as themes, custom `Application` class name, backup rules, and network security configs."
        ),
        "deep_answer": (
            "During the Gradle build process, AGP (Android Gradle Plugin) executes **Manifest Merging**. "
            "It merges the main app manifest with manifests from third-party libraries and build variants (debug/release). "
            "Conflicting attributes are resolved via `tools:node=\"replace\"` or `tools:node=\"remove\"`.\n\n"
            "From an Android 12+ security standpoint, the attribute **`android:exported`** is now strictly mandatory for any component containing an `<intent-filter>`. "
            "If `android:exported` is set to `true`, external apps can launch that component. If `false`, it is strictly internal to your app. "
            "Leaving `exported=\"true\"` on internal components without permission checks creates severe security vulnerabilities, permitting malicious third-party apps to launch privileged internal activities directly."
        ),
        "follow_ups": [
            {
                "interviewer": "What happens if a library you import sets `exported=\"true\"` without you knowing?",
                "answer": "Manifest Merger merges that attribute into your final APK manifest. You must inspect the merged manifest in Android Studio or explicitly override it using `tools:replace=\"android:exported\"`."
            },
            {
                "interviewer": "Can a Fragment be declared in AndroidManifest.xml?",
                "answer": "No! Fragments are framework view abstractions managed by FragmentManager inside an Activity, not top-level OS components recognized by the PackageManager."
            },
            {
                "interviewer": "What is `android:process` in the manifest?",
                "answer": "It specifies that a component should run in a separate Linux process (e.g., `android:process=\":sync\"`). It creates multi-process apps with separate memory heaps."
            }
        ]
    },
    {
        "id": "AND-12",
        "arabic_explanation": (
            "استعادة الشاشة بعد الـ Process Death دون فقدان مدخلات المستخدم (Restoring a screen after process death without losing user input) هي مهارة حاسمة في معمارية تطبيقات أندرويد الاحترافية:\n\n"
            "1. المشكلة التي تحدث في الإنتاج:\n"
            "   - المستخدم ملأ استمارة طلب قرض أو تسجيل حساب طويلة من 10 حقول.\n"
            "   - خرج للرد على مكالمة هاتفية أو فتح الكاميرا لتصوير بطاقة الهوية.\n"
            "   - نظام أندرويد قتل التطبيق في الخلفية (Process Death).\n"
            "   - عند العودة: الاستمارة فارغة تماماً والبيانات ضاعت، والمستخدم يشعر بالإحباط ويحذف التطبيق!\n\n"
            "2. الحل المعماري الكامل (The 3-Step Architecture):\n"
            "   - **الخطوة 1: استخدام `SavedStateHandle` في الـ ViewModel:**\n"
            "     * ربط حقول الإدخال بـ `SavedStateHandle.getStateFlow(key, initialValue)`.\n"
            "     * كل حرف يكتبه المستخدم يتم حفظه تلقائياً في `SavedStateHandle`.\n"
            "   - **الخطوة 2: الحفظ التلقائي للنظام في الـ OS System Server:**\n"
            "     * عند حدوث Process Death، الـ SavedStateHandle يحفظ كل القيم في الـ SavedInstanceState Bundle.\n"
            "   - **الخطوة 3: الاسترجاع الفوري عند إعادة البناء:**\n"
            "     * عند إنشاء الـ ViewModel الجديد بعد عودة التطبيق، يقوم الـ `AbstractSavedStateViewModelFactory` بحقن القيم المحفوظة تلقائياً في `SavedStateHandle`، وتظهر البيانات في الشاشة كأن شيئاً لم يحدث!"
        ),
        "practical_walkthrough": (
            "تنفيذ استمارة تسجيل آمنة تماماً ضد Process Death:\n"
            "```kotlin\n"
            "class RegistrationViewModel(\n"
            "    private val savedStateHandle: SavedStateHandle // يتم حقنه تلقائياً عبر Hilt\n"
            ") : ViewModel() {\n"
            "\n"
            "    // ربط الحقول بـ StateFlow محفوظ في SavedStateHandle:\n"
            "    val fullName = savedStateHandle.getStateFlow(\"full_name\", \"\")\n"
            "    val email = savedStateHandle.getStateFlow(\"email\", \"\")\n"
            "\n"
            "    fun onFullNameChanged(newName: String) {\n"
            "        savedStateHandle[\"full_name\"] = newName // يحفظ فوراً في الـ Bundle\n"
            "    }\n"
            "\n"
            "    fun onEmailChanged(newEmail: String) {\n"
            "        savedStateHandle[\"email\"] = newEmail\n"
            "    }\n"
            "}\n"
            "```\n"
            "في Compose أو XML: الشاشة تقرأ `val name by viewModel.fullName.collectAsStateWithLifecycle()`.\n"
            "لو تم قتل الـ Process بأمر `adb shell am kill` وعاد المستخدم: سيجد اسمه وإيميله مكتوبين في أماكنهم بالكامل."
        ),
        "quick_answer": "Restore screens after process death by binding user inputs and critical identifiers to ViewModel's SavedStateHandle via getStateFlow(). Android serializes this state into the OS system server Bundle before killing the process and automatically restores it into the recreated ViewModel upon app restart.",
        "best_answer": (
            "To restore a screen after process death without losing user input, modern Android architecture relies on **`SavedStateHandle`** in the ViewModel layer:\n\n"
            "1. **Bind Inputs to SavedStateHandle**: Instead of storing draft form inputs in plain in-memory `MutableStateFlow`s, we bind them directly to `SavedStateHandle` using `savedStateHandle.getStateFlow(key, initialValue)`. When the user types, updating `savedStateHandle[key] = input` records the state.\n\n"
            "2. **OS Serialization**: When the app is backgrounded and the OS Low Memory Killer kills the process, Android serializes the `SavedStateHandle` contents into the system server's instance state Bundle.\n\n"
            "3. **Automatic Restoration**: When the user reopens the app from Recents, Android spawns a new process, recreates the Activity, and passes the restored Bundle to the ViewModel factory. The newly created ViewModel reads the saved values immediately, repopulating the UI on its very first frame without loss."
        ),
        "deep_answer": (
            "Under the hood, `SavedStateHandle` hooks into the Activity/Fragment `SavedStateRegistry`. "
            "When `onSaveInstanceState(Bundle)` runs, `SavedStateHandle` converts its key-value map into a nested Bundle. "
            "Because this state is transferred via Binder IPC to `system_server`, strict size discipline is necessary: "
            "Save only user-typed strings, checkboxes, and database primary keys (e.g. `orderId: Long`). "
            "Never save large cached lists, images, or domain response models in `SavedStateHandle`.\n\n"
            "For complex draft objects, if a user fills out a 5-step insurance claim form with photo attachments, `SavedStateHandle` is insufficient due to Binder size limits. "
            "In that scenario, the architectural pattern is **Draft Persistence in Room**: save each form step to a local SQLite draft database as the user types, and save only `draftId: String` in `SavedStateHandle`."
        ),
        "follow_ups": [
            {
                "interviewer": "Why do standard XML EditTexts survive process death even without SavedStateHandle?",
                "answer": "Because standard Android framework Views with unique `android:id`s implement their own internal `onSaveInstanceState()` methods, automatically writing their input text into the view hierarchy bundle."
            },
            {
                "interviewer": "How does `rememberSaveable` fit into this in Jetpack Compose?",
                "answer": "`rememberSaveable` hooks into the same `SavedStateRegistry` mechanism for local Composable state, ensuring TextField values and scroll positions survive process death."
            },
            {
                "interviewer": "What happens if the user clears the app from the Recent Apps switcher?",
                "answer": "Clearing the app from Recents signals intentional user termination. The OS permanently discards the saved instance state Bundle. When the app is opened next, it launches fresh from its home screen."
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

    for q in AND_07_12:
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
    print(f"Updated {DATA_FILE} with questions AND-07 to AND-12. Total questions: {len(combined)}")


if __name__ == "__main__":
    main()

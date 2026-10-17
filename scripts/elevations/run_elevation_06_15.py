#!/usr/bin/env python3
"""Elevation script for AND-06 through AND-15.
Generates full bilingual parity, authentic spoken answers, and validated metadata.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import elevation_engine as ee

TOPIC_AR = "أساسيات أندرويد ودورة الحياة والسياق (Context)"
REVIEWED_DATE_AR = "تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13."

def run():
    print("Starting elevation for AND-06 through AND-15...")
    
    metadata_entries = {}

    # =========================================================================
    # AND-06: What are configuration changes, and what survives them?
    # =========================================================================
    qid = "AND-06"
    concept_en = """Configuration changes represent environmental, hardware, or system-level setting modifications that occur while an Android application is running, forcing the operating system to recalculate its active resource configuration. Common triggers include screen orientation changes between portrait and landscape, system language or locale switching, toggling between light and dark display modes, multi-window mode entry and split-screen resizing, device folding or unfolding on foldable hardware, and dynamic font scale or display density adjustments.

When a configuration change occurs, Android's default architectural behavior is to destroy the active Activity instance through its teardown lifecycle callbacks from onPause through onStop to onDestroy, and immediately recreate a fresh Activity instance from onCreate through onStart to onResume. This destructive recreation cycle is deliberate: it allows the framework to automatically reload resources matching the updated configuration qualifiers from the application package, such as layout-land, values-night, or values-ar.

Understanding what survives this recreation is fundamental to building reliable mobile software. First, Jetpack ViewModels survive intact in process memory because they are retained by the ViewModelStoreOwner across the configuration boundary, preserving ongoing business logic and viewModelScope coroutines. Second, lightweight UI state survives via the SavedStateHandle or onSaveInstanceState Bundle, which serializes key-value pairs across the recreation boundary. Third, application-level singletons, static fields, in-memory caches, and dependency injection graphs remain untouched in the Android Runtime heap because the underlying Linux operating system process is never terminated. Conversely, the old Activity instance, its View hierarchy, Fragments, dialogs, and any coroutines launched inside the unmanaged lifecycleScope are completely destroyed and garbage collected."""

    walkthrough_en = """In a production ecommerce checkout screen, consider what happens when a customer rotates their tablet while completing a payment form:
1. What is destroyed and lost:
The active Activity instance, inflated ViewBinding hierarchies, and Dialogs are destroyed immediately. Any asynchronous tasks launched inside lifecycleScope are canceled as the lifecycle transitions to DESTROYED. Local Activity instance variables, such as temporary boolean flags or unsaved input text not backed by persistent IDs, are dropped from memory.
2. What survives and persists:
The CheckoutViewModel and its StateFlow subscriptions remain uninterrupted in heap memory via the ViewModelStore. Ongoing payment processing coroutines running inside viewModelScope continue execution without interruption. If input fields possess unique android:id attributes, their entered text is automatically serialized into the instance state Bundle and restored into the newly inflated layout.
3. Failure scenario:
If an engineer stores an order submission state in an Activity member variable or launches the payment network request in lifecycleScope, screen rotation cancels the request mid-flight while leaving the user on a blank form. If the user taps submit again upon recreation, duplicate charges or conflicting database records occur. The architectural safeguard is to execute all transactions within viewModelScope, track operation identifiers through SavedStateHandle, and query backend payment status before retrying."""

    short_en = """A configuration change occurs when runtime environment settings change, such as screen rotation, dark mode switching, or locale adjustments. By default, Android completely destroys and recreates the Activity to reload qualifier-matching resources. The ViewModel survives in memory via ViewModelStore, the saved instance state Bundle preserves transient UI keys, and the Linux process remains alive."""

    structured_en = """To begin with, a configuration change occurs when runtime environment variables change, such as device rotation, system language switching, dark mode toggling, or multi-window resizing. Android handles this by destroying the current Activity instance through its lifecycle callbacks and instantiating a fresh one to re-resolve qualifier-specific resources from the APK asset table.

From an architectural standpoint, the system cleanly separates what is destroyed from what survives. The previous Activity instance, its View tree, and any jobs scoped strictly to the UI lifecycle are destroyed. However, the ViewModel survives continuously in process memory because it is retained by the ViewModelStoreOwner, ensuring that viewModelScope coroutines and business state remain uninterrupted.

As for boundary management, transient UI properties like scroll offsets and form inputs survive via SavedStateHandle or the onSaveInstanceState Bundle. Meanwhile, application-level singletons, network clients, and database handles stay alive because the underlying Linux process is never terminated during an ordinary configuration change.

In production scenarios, we avoid using android:configChanges to bypass recreation. Instead, we embrace the recreation cycle, delegate business operations to ViewModelScope, and persist critical transaction identifiers into durable storage, guaranteeing flawless state continuity."""

    deep_senior_en = """At the operating system and Android Runtime level, configuration changes are orchestrated by the ActivityTaskManagerService in the system_server process. When a hardware sensor triggers a display rotation or the user toggles dark mode, the system server evaluates the delta between the device's current Configuration and the Activity's override configuration.

Rather than attempting an in-place mutation of the entire view hierarchy, Android intentionally destroys the Activity. Mutating an existing view tree in-place would require traversing every view, drawable cache, dynamic layout parameter, and dimension resource, which is historically error-prone and invites subtle layout corruption. By invoking performDestroy() followed by performCreate(), the ActivityThread binds a newly configured ResourcesImpl instance to the fresh Activity context, ensuring all layout and drawable inflations pull the exact qualifiers for the new environment.

The survival of the ViewModel across this destruction is managed by the NonConfigurationInstances record. Before the old Activity is destroyed, the framework invokes retainNonConfigurationInstances(), caching the ViewModelStore inside a platform holder in the ActivityClientRecord. When the ActivityThread constructs the new Activity instance, it supplies this cached record back via attach(), allowing the ViewModelProvider to retrieve the identical ViewModel instances from the existing store without executing their onCleared() callback.

Crucially, Staff engineers distinguish between configuration changes and process death. A configuration change preserves the entire JVM heap, including static variables, Dagger or Hilt singleton component graphs, and active background threads. Process death, triggered by the Linux kernel Low Memory Killer daemon, obliterates the process address space entirely. Attempting to bypass configuration recreation by declaring android:configChanges in the manifest transfers the entire burden of manual resource updates onto the developer via onConfigurationChanged(), which frequently breaks accessibility scaling, locale switching, and foldable posture transitions."""

    ee.update_canonical_question(qid, concept_en, walkthrough_en, structured_en, deep_senior_en, short_en)

    metadata_entries[qid] = {
        "id": qid,
        "questionAr": "ما هي الـ Configuration Changes وما الذي ينجو منها؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- التمييز بين إعادة إنشاء الـ Activity عند تدوير الشاشة وبين موت العملية بالكامل (Process Death).\n- توزيع الحالة بين الـ ViewModel والـ SavedStateHandle وقواعد البيانات المحلية بشكل معماري سليم.\n- اختبار سيناريوهات التدوير والوضع الليلي وتغيير اللغة دون افتراض ثبات دورة الحياة.",
        "why_it_matters_ar": "يقوم نظام أندرويد بتدمير الـ Activity الحالية وإعادة إنشائها بالكامل عند حدوث تغيير في إعدادات البيئة المحيطة (Configuration Change) مثل تدوير الشاشة أو تبديل اللغة أو تفعيل الوضع الليلي. الهدف الأساسي من هذه الآلية هو إجبار التطبيق على إعادة تحميل الموارد والرسومات ونصوص الواجهة المتوافقة مع الإعدادات الجديدة من مجلدات الموارد المناسبة مثل `layout-land` و `values-night`. الـ ViewModel المحفوظ في `ViewModelStore` ينجو من هذا التدمير ويبقى حياً في الذاكرة طالما لم تنتهِ العملية، بينما تفقد الـ Activity كافة متغيراتها ومراجع الـ Views الخاصة بها. حفظ المفاتيح الصغيرة في `SavedStateHandle` يضمن استعادة الواجهة حتى لو تطور الأمر لموت العملية، بينما البيانات الدائمة مكانها الحقيقي هو قواعد بيانات Room.",
        "worked_example_ar": "في شاشة البحث وتفاصيل المنتجات، نحتفظ بنص البحث في `SavedStateHandle` بينما تُدار النتائج داخل `ViewModel`:\n```kotlin\nclass SearchViewModel(\n    private val savedState: SavedStateHandle,\n    private val repository: SearchRepository\n) : ViewModel() {\n    private val _results = MutableStateFlow<List<SearchResult>>(emptyList())\n    val results = _results.asStateFlow()\n    val query: String get() = savedState[\"query\"] ?: \"\"\n\n    fun onSearch(queryText: String) {\n        savedState[\"query\"] = queryText\n        viewModelScope.launch {\n            _results.value = repository.search(queryText)\n        }\n    }\n}\n```\nعند تدوير الشاشة، يتم تدمير الـ Activity وتنشأ نسخة جديدة تستعيد نفس الـ ViewModel بنفس الحالة دون الحاجة لتكرار استدعاء الشبكة، ويظل نص البحث محفوظاً في `SavedStateHandle`.",
        "trade_offs_ar": "الاحتفاظ بالبيانات في الـ ViewModel يوفر استجابة فورية وسلسة للواجهة أثناء تدوير الشاشة بدون استهلاك للشبكة، ولكنه مقيد بذاكرة الـ Heap الخاصة بالعملية ولا ينجو إذا أنهى النظام التطبيق في الخلفية. الـ SavedState مناسب للمدخلات البسيطة ومعرفات العناصر لكنه مقيد بحجم الـ IPC Binder Buffer (حوالي 1 ميجابايت للعملية بأكملها). التخزين الدائم في Room يحمي البيانات ضد كل سيناريوهات الفقدان لكنه يتطلب عمليات قراءة وكتابة غير متزامنة على القرص. اللجوء لخاصية `android:configChanges` في الـ Manifest للهروب من تدمير الشاشة يحرم التطبيق من التحديث التلقائي للموارد ويضع عبء معالجة كل التغييرات يدوياً على عاتق المطور.",
        "failure_modes_ar": "تخزين عملية الدفع أو حالة المعاملة المالية في متغير عادي داخل الـ Activity يؤدي لفقدان حالة العملية عند تدوير الشاشة وإرسال طلب دفع مكرر عند إعادة البناء. الاحتفاظ بمرجع الـ Activity القديمة داخل الـ ViewModel أو كائن Singleton يسرب شجرة الـ Views والنافذة بالكامل في الذاكرة ويسبب بطء النظام أو حدوث OOM. تخزين Bitmaps أو قوائم بيانات ضخمة في الـ SavedState يتسبب في كراش `TransactionTooLargeException`. المعالجة السليمة تتطلب إسناد المهام لـ `viewModelScope` وتأمين المعاملات بمعرفات فريدة في التخزين الدائم.",
        "production_perspective_ar": "في شاشات الدفع والشراء في التطبيقات الكبيرة، يتم حفظ معرف الطلب المبدئي في قاعدة بيانات محلية قبل إرسال الطلب للسيرفر، بينما يعرض الـ ViewModel حالة المعاملة عبر StateFlow. عند حدوث تدوير للشاشة، تستعيد الواجهة الجديدة الحالة المعروضة فوراً من الـ ViewModel دون انقطاع، ولو حدث موت مفاجئ للعملية، يُعاد بناء الشاشة من معرف الطلب المخزن محلياً ويتم الاستعلام عن حالته من السيرفر. يتم تشغيل اختبارات آلية تحاكي تدوير الشاشة أثناء تنفيذ طلبات الشبكة للتأكد من عدم تكرار الطلبات أو تسريب الواجهات.",
        "how_to_answer_ar": "- **السبب المعماري:** وضح أن تدمير الـ Activity هو الآلية القياسية لأندرويد لتحديث الموارد المتوافقة مع الإعدادات الجديدة.\n- **طريقة الشرح:** ميز بين ما يتدمر (الـ Activity والـ Views ومراجع الـ LifecycleScope) وما ينجو (الـ ViewModel والـ SavedState والـ Process Heap).\n- **المفاضلات الهندسية:** وضح حدود الـ ViewModel والـ SavedState مقابل التخزين الدائم.\n- **أنماط الفشل:** اذكر تسريب مراجع الـ Activity وخطر تخزين البيانات الحساسة أو الكبيرة في الـ Bundle.\n- **الحل العملي:** استشهد بفصل منطق الأعمال في `viewModelScope` وتخزين معرفات العمليات محلياً.",
        "talking_points_ar": "ناقش دور `ActivityTaskManagerService` في تقييم الفروق بين إعدادات النظام الحالية والسابقة، وكيف يتم الاحتفاظ بـ `ViewModelStore` عبر `retainNonConfigurationInstances`، ولماذا تحذر جوجل من استخدام `android:configChanges` لتفادي إعادة البناء، وحدود حجم الـ Binder Buffer وتفادي `TransactionTooLargeException`، والفرق الجوهري بين التدوير وموت العملية بواسطة الـ LMK.",
        "follow_ups_ar": "- **المحاور:** \"ليه حقول الـ EditText بتسترجع نصوصها تلقائياً بعد تدوير الشاشة حتى لو مفيش ViewModel؟\"\n  **المرشح:** \"لأن عناصر الواجهة القياسية في أندرويد بتنفذ دالة onSaveInstanceState داخلياً. لو العنصر متعرف له android:id فريد في الـ XML، نظام أندرويد بيحفظ نصه ومكانه تلقائياً في حزمة الـ Saved State Bundle وبيرجع يملأه أول ما يعاد بناء الشاشة.\"\n\n- **المحاور:** \"إزاي دالة rememberSaveable في Jetpack Compose بتنجو من الـ Configuration Changes؟\"\n  **المرشح:** \"دالة rememberSaveable بتسجل القيمة مع الـ SaveableStateRegistry، والـ Registry ده متوصل داخلياً بنظام الـ onSaveInstanceState Bundle بتاع أندرويد، فبتتحفظ القيمة في حزمة النظام وتسترجع بعد إعادة بناء الـ Composition.\"\n\n- **المحاور:** \"هل كان ممكن الاحتفاظ بكائنات عبر التدوير قبل ظهور الـ ViewModel؟\"\n  **المرشح:** \"أيوة، تاريخياً كان بيستخدم onRetainCustomNonConfigurationInstance لتمرير الكائنات للنسخة الجديدة من الـ Activity، ومكتبة Jetpack ViewModel اتبنت في الأساس فوق نفس الآلية دي ووفرت واجهة آمنة ومنظمة لاستخدامها.\"",
        "self_check_ar": "اشرح سبباً واحداً للـ Configuration Change وأثره على الشاشة؛ حدد ما ينجو داخل الـ ViewModel وحزمة الـ Saved State؛ بيّن خطورة تسريب مرجع Activity بعد التدوير؛ وصمم مسار استعادة آمن لشاشة دفع إلكتروني.",
        "references_ar": f"- [Activity lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle) — دورة حياة الشاشة والتغيرات البيئية.\n- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — إرشادات حفظ حالة الواجهة وحدود البيانات.\n- [ViewModel overview](https://developer.android.com/topic/libraries/architecture/viewmodel) — نطاق الـ ViewModel وإدارته في الذاكرة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ Configuration Changes زي تدوير الشاشة أو تغيير اللغة أو تفعيل الوضع الليلي بتخلي أندرويد يدمر كائن الـ Activity القديم ويعيد بناءه لتحميل الموارد المناسبة. الـ ViewModel بينجو في الذاكرة عبر الـ ViewModelStore، والـ SavedStateHandle بيحفظ بيانات الواجهة الخفيفة، وعملية التطبيق كلها بتفضل شغالة في الـ Linux Process بدون انقطاع.",
        "best_answer_ar": "لما بيحصل أي تغيير في بيئة تشغيل الجهاز زي تدوير الشاشة من رأسي لأفقي أو تحويل لغة النظام أو تشغيل الوضع الليلي، أندرويد بيهدم الـ Activity الحالية تماماً ويعملها إعادة بناء من الصفر. الهدف من الخطوة دي مش التعقيد، لكن علشان النظام يحمل الموارد المتوافقة مع الإعداد الجديد من ملفات الـ XML زي layout-land أو values-night.\n\nالمهم إننا كمهندسين نعرف إيه اللي بيضيع وإيه اللي بيفضل؛ كائن الـ Activity القديم وشجرة الـ Views بيتدمروا وأي مهمة كانت شغالة في lifecycleScope بتتلغي فوراً. في المقابل، الـ ViewModel بيفضل عايش في الذاكرة بدون أي تأثير بفضل الـ ViewModelStore، وكل الـ StateFlows والكوروتينات اللي شغالة جوه viewModelScope بتفضل مستمرة، وأول ما الشاشة الجديدة تتفتح بتستلم نفس الـ ViewModel بنفس البيانات فوراً.\n\nبالإضافة لكده، حقول الإدخال اللي واخدة IDs بتسترجع نصوصها تلقائياً عبر SavedInstanceState، وميموري التطبيق والـ Singletons بتفضل زي ما هي لأن عملية الـ Linux process نفسها مامتتش.\n\nفي الشغل الفعلي مبنلجأش أبداً لـ configChanges في الـ Manifest للهروب من المشكلة، لإن ده بيعطل التوافق مع الشاشات القابلة للطي وأبعاد الواجهة الحديثة.",
        "deep_answer_ar": "على مستوى الـ Android OS Runtime ونظام الـ Window Manager، الـ Configuration Change بيتم إدارته من خلال ActivityTaskManagerService في الـ system_server. أول ما حساس الحركة يلقط التدوير، السيرفر بيحسب الـ Configuration Delta، وبدل ما يحاول يعدل شجرة الواجهة الحالية في مكانها، بيقرر يهدم الـ Activity القديمة عبر performDestroy وينشئ كائن جديد عبر performCreate.\n\nالسبب الهندسي لقرار الهدم ده هو إن تعديل الـ Views القائمة كان هيتطلب المرور على كل Drawable وStyle وDimension وتحديثهم يدوياً وده عملياً مستحيل ومصدر لأخطاء بصرية لا حصر لها، فإعادة البناء بتوفر Clean Slate بيربط الـ ResourcesImpl الجديدة تلقائياً.\n\nالسر في نجاة الـ ViewModel هو آلية الـ NonConfigurationInstances؛ قبل تدمير الشاشة القديمة بيتم استدعاء retainNonConfigurationInstances، فـ ViewModelStore بيتشال في حامل خاص داخل الـ ActivityClientRecord التابع للـ ActivityThread. ولما النسخة الجديدة تتعمل، الـ ActivityThread بيمرر لها نفس الـ Store القديم في دالة attach، فـ ViewModelProvider يرجع نفس الكائنات بدون ما ينادي onCleared.\n\nلازم نفرق دايماً بين الـ Configuration Change وموت العملية؛ التدوير بيحافظ على الـ JVM Heap بما فيها الـ Singletons ومحقونات Hilt وشبكات الاتصال، بينما الـ Process Death بيمسح الذاكرة بالكامل من خلال الـ Low Memory Killer. ومحاولة تفادي إعادة البناء بـ configChanges بتنقل مسؤولية التعامل مع تغيير الحجم وتغير خطوط الـ Accessibility لرقبة المطور في onConfigurationChanged وده بيسبب مشاكل ضخمة في الإنتاج خصوصاً مع أجهزة الـ Foldables."
    }

    # =========================================================================
    # AND-07: What is process death? How is it different from configuration change?
    # =========================================================================
    qid = "AND-07"
    concept_en = """Process death occurs when the Android operating system kernel, through the Low Memory Killer Daemon (LMKD), forcibly terminates an application's hosting Linux process while it is in the background to reclaim physical RAM for higher-priority foreground applications. Unlike explicit user termination via task swiping, process death happens silently and asynchronously without executing application-level lifecycle teardown methods like onDestroy() or ViewModel onCleared().

The fundamental architectural difference between a configuration change and process death lies at the memory boundary. During a configuration change, such as a device rotation, the Linux process remains alive. The JVM heap, static variables, dependency injection singletons, background coroutines, and retained ViewModelStore instances survive intact in RAM. In contrast, process death completely wipes the application process and its entire virtual memory space, including all ViewModel instances, singletons, and in-memory caches.

When the user navigates back to a killed application from the Recent Apps screen, the operating system spawns an entirely new Linux process and creates a fresh Activity instance. The sole bridge of continuity between the terminated process and the new process is the saved instance state Bundle, which the framework serialized across inter-process communication into system_server prior to termination. Modern Android architectures leverage SavedStateHandle within ViewModels to consume this restored Bundle, enabling automatic recovery of navigational identifiers and draft user input while re-fetching authoritative domain state from durable local databases or remote network APIs."""

    walkthrough_en = """Testing process death and diagnosing restoration bugs in development:
1. Reproducing process death reliably via adb:
Navigate to the order details screen in the application. Press the device Home button to move the application into the background state. In a terminal session, execute:
adb shell am kill com.example.myapp
Alternatively, use the Stop Process action in Android Studio Logcat.
2. Returning to the application:
Relaunch the app from the Recent Apps screen. The Android system creates a new process and restores the previous backstack destination.
3. Common production failure scenario:
If the screen relies on an in-memory repository cache or an unpersisted orderId passed to the ViewModel constructor, the recreated ViewModel initializes with null or empty state, resulting in a fatal NullPointerException or an empty error screen.
4. Robust architectural remediation:
Inject SavedStateHandle into OrderDetailsViewModel:
```kotlin
class OrderDetailsViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val repository: OrderRepository
) : ViewModel() {
    val orderId: String = checkNotNull(savedStateHandle["order_id"])
    val uiState: StateFlow<OrderUiState> = repository.getOrderStream(orderId)
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), OrderUiState.Loading)
}
```
Because the system server caches navigation arguments in the saved state Bundle, orderId is automatically restored, allowing the repository to hydrate the screen seamlessly."""

    short_en = """Process death occurs when Android terminates an idle background process to reclaim physical RAM. Unlike a configuration change where the process and ViewModel survive in memory, process death obliterates all heap memory and singletons. Only state serialized into the SavedStateHandle Bundle via the system server survives, allowing the newly spawned process to reconstruct UI destinations and reload durable data."""

    structured_en = """To begin with, process death occurs when the Android operating system terminates an app's background Linux process to reclaim RAM for foreground tasks. The essential architectural contrast is that a configuration change preserves the hosting process and its JVM heap, allowing ViewModels, dependency graphs, and memory caches to survive untouched.

From an architectural standpoint, process death erases the entire virtual address space. When the Linux kernel executes a kill, all in-memory singletons, background jobs, and ViewModel instances vanish immediately. The framework does not execute onDestroy or onCleared callbacks during this reclamation.

As for boundary management, state recovery depends entirely on the saved instance state Bundle. When an application enters the background, Android serializes transient UI state across Binder IPC to the system server. When the user returns, the OS spawns a fresh process and injects this preserved Bundle back into the Activity and SavedStateHandle.

In production scenarios, we distinguish between transient navigation keys and persistent domain data. We store compact entity identifiers and user draft inputs in SavedStateHandle, while persisting full business records into Room databases, ensuring resilient restoration without risking transaction buffer overflow."""

    deep_senior_en = """At the Linux kernel and platform runtime layer, process death is mediated by the low memory killer daemon, lmkd, interacting with Linux memory control groups and the Out-Of-Memory score adjustment mechanism. The framework ActivityManagerService assigns dynamic oom_adj scores based on component states. An active, focused Activity maintains an oom_adj score of zero in the foreground bucket, while an Activity moved to onStop drops into the cached process bucket with scores scaling up to 900 or higher. When physical system memory breaches configured low watermarks, lmkd issues a direct SIGKILL kernel signal to the highest-scoring background process.

Because SIGKILL terminates the process abruptly at the kernel scheduler level, no userspace signal handlers or Java finalizers can execute. The Android Runtime does not call onDestroy() on Activities nor onCleared() on ViewModels. If an application defers database writes or critical transaction receipts to onDestroy(), that state is permanently lost upon process death.

Before the process becomes eligible for termination, Android invokes Activity.onSaveInstanceState() between onPause() and onStop(). The serialized Bundle is transmitted across Binder IPC to ActivityTaskManagerService inside the system_server process. This IPC boundary is constrained by a global 1MB per-process Binder transaction buffer. Attempting to serialize large lists, network payloads, or Bitmap objects into SavedStateHandle triggers a fatal TransactionTooLargeException during backgrounding.

Consequently, Staff-level mobile system design mandates a clear three-tier state hierarchy: volatile UI state lives in ViewModel memory across rotation; compact reconstruction tokens, pagination indices, and form draft keys live in SavedStateHandle across process death; and domain business entities are persisted immediately to local SQLite or Room databases. When the user returns from a kill, the application uses the restored identity tokens to query local cache or reconcile pending operations against server idempotency keys."""

    ee.update_canonical_question(qid, concept_en, walkthrough_en, structured_en, deep_senior_en, short_en)

    metadata_entries[qid] = {
        "id": qid,
        "questionAr": "ما هو موت العملية (Process Death) وما الفرق بينه وبين الـ Configuration Change؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- إدراك أن موت العملية (Process Death) يمحو كافة الكائنات في الذاكرة بما فيها الـ ViewModels والـ Singletons.\n- شرح كيفية قيام أندرويد بإعادة بناء شاشة سابقة بدون استدعاء `onDestroy()` القديمة.\n- استعادة حالة الواجهة والعمليات الخارجية من معرفات دائمة بدلاً من تكرار الآثار الجانبية بشكل أعمى.",
        "why_it_matters_ar": "عندما ينتقل التطبيق إلى الخلفية، يحتفظ نظام أندرويد بحقه في إنهاء عملية التطبيق (Linux Process) بالكامل لتحرير الذاكرة العشوائية (RAM) للتطبيقات التي تعمل في المقدمة. هذا الإنهاء يتم عبر الـ Low Memory Killer Daemon (LMKD) بإشارة `SIGKILL` مباشرة من النواة، مما يعني أن دوال التنظيف مثل `onDestroy()` أو `onCleared()` لا تُستدعى على الإطلاق. في المقابل، الـ Configuration Change (مثل تدوير الشاشة) يعيد إنشاء الـ Activity فقط داخل نفس العملية الحية، مما يحافظ على الـ ViewModel ومساحة الـ Heap. الجسر الوحيد الذي ينجو من موت العملية هو حزمة `SavedStateHandle` التي يتم نسخها إلى عملية النظام (`system_server`) قبل القتل، بالإضافة إلى البيانات المحفوظة على القرص الصلب في Room.",
        "worked_example_ar": "في شاشة تفاصيل الإيصال، نحفظ معرف العملية `paymentAttemptId` محلياً في قاعدة البيانات فور إرسالها، ونحتفظ برقم الإيصال في `SavedStateHandle`:\n```kotlin\nclass ReceiptViewModel(\n    private val savedStateHandle: SavedStateHandle,\n    private val repository: ReceiptRepository\n) : ViewModel() {\n    private val paymentAttemptId: String = checkNotNull(savedStateHandle[\"payment_attempt_id\"])\n    private val _uiState = MutableStateFlow<ReceiptUiState>(ReceiptUiState.Loading)\n    val uiState = _uiState.asStateFlow()\n\n    init {\n        viewModelScope.launch {\n            // استرجاع حالة المعاملة من السيرفر باستخدام المعرف المحفوظ\n            _uiState.value = repository.reconcilePaymentStatus(paymentAttemptId)\n        }\n    }\n}\n```\nعند موت العملية وعودة المستخدم، يُعاد بناء الـ ViewModel ويقرأ المعرف من `SavedStateHandle` ويستعلم عن حالة الدفع من السيرفر بدلاً من تكرار الخصم.",
        "trade_offs_ar": "الـ SavedState سريع ومثالي للمفاتيح الصغيرة ومعرفات التنقل، ولكنه مقيد بحدود مساحة الـ Binder Buffer التي لا تتعدى 1 ميجابايت على مستوى العملية كلها. التخزين في قاعدة بيانات Room ينجو من موت العملية وإعادة تشغيل الجهاز ويستوعب بيانات ضخمة، لكنه يتطلب تصميم Schema وتنفيذ عمليات Disk I/O غير متزامنة. الاعتماد على WorkManager مناسب لجدولة المهام التي يجب أن تكتمل في الخلفية حتى بعد إغلاق التطبيق، بينما فتح الشاشة مجدداً هو المسؤول عن استعادة الواجهة التفاعلية.",
        "failure_modes_ar": "الافتراض الخاطئ بأن دالة `onDestroy()` مضمونة الاستدعاء دائماً يؤدي لفقدان المعاملات المالية غير المحفوظة. تخزين حالة التحميل أو الدفع في متغير داخل الـ ViewModel فقط يجعلها تختفي تماماً عند موت العملية، مما يترك المستخدم أمام شاشة بيضاء أو استمارة فارغة. إعادة إرسال طلب الشراء (POST) فور استعادة الشاشة بدون التأكد من حالة المحاولة السابقة قد يكرر الخصم من حساب العميل. تخزين قوائم كبيرة في الـ SavedState يؤدي لكراش `TransactionTooLargeException`.",
        "production_perspective_ar": "في تطبيقات التكنولوجيا المالية، يتم حفظ معرف المحاولة ومفتاح عدم التكرار (Idempotency Key) في قاعدة البيانات المحلية قبل الضغط على زر الدفع. عند استعادة الشاشة بعد موت العملية، تسترجع الشاشة المعرف من `SavedStateHandle` وتتصل بالسيرفر عبر نقطة نهاية للقراءة فقط لمعرفة حالة العملية (نجحت، فشلت، قيد المعالجة). يتم اختبار هذا المسار برمجياً باستخدام `adb shell am kill` للتأكد من استعادة الشاشة دون تكرار أي استدعاءات شبكة حساسة أو إرباك المستخدم.",
        "how_to_answer_ar": "- **السبب المعماري:** فرّق بين موت مساحة الذاكرة بالكامل في موت العملية وبين هدم الـ View فقط في التدوير.\n- **طريقة الشرح:** وضح آلية عمل LMK ومستويات الـ oom_adj ولماذا لا تستدعى onDestroy.\n- **المفاضلات:** قارن بين حدود SavedStateHandle وحجم الـ Binder Buffer وتخزين القرص في Room.\n- **أنماط الفشل:** اشرح خطر تكرار المعاملات المالية والـ TransactionTooLargeException.\n- **الحل العملي:** استشهد بنموذج استعادة معرف المعاملة والاستعلام عن حالتها من السيرفر.",
        "talking_points_ar": "ناقش درجات أولوية العمليات في أندرويد (Process Importance Buckets)، وآلية إرسال `SIGKILL` من قِبل الـ LMKD، وتوقيت حفظ الـ Bundle بين `onPause` و `onStop` عبر Binder IPC إلى `system_server`، وكيف يحل `SavedStateHandle` مشكلة حقن الاعتماديات بعد إعادة إحياء الشاشة، وطريقة اختبار استعادة الحالة باستخدام أوامر adb ومراقبة استهلاك الذاكرة.",
        "follow_ups_ar": "- **المحاور:** \"ليه الـ ViewModel بينجو من تدوير الشاشة وبيموت في الـ Process Death؟\"\n  **المرشح:** \"لأن الـ ViewModel بيعيش في الـ JVM Heap الخاص بالـ Linux Process بتاعة التطبيق. في التدوير، الـ Process بتفضل حية والذاكرة بتفضل سليمة. أما في الـ Process Death فالنظام بيمسح الـ Process كلها من الذاكرة فكل حاجة في الـ Heap بتضيع.\"\n\n- **المحاور:** \"إزاي نختبر الـ Process Death بشكل حاسم أثناء التطوير؟\"\n  **المرشح:** \"بنفتح الشاشة المطلوبة في التطبيق، وندوس Home علشان التطبيق يدخل في الـ Background، وبعدين ننفذ في التيرمينال أمر `adb shell am kill <package-name>`، أو ندوس Stop Process من الـ Logcat في أندرويد ستوديو، ولما نفتح التطبيق تاني من الـ Recents بنشوف هل الشاشة هتستعيد حالتها ولا هتعمل كراش.\"\n\n- **المحاور:** \"ما هو الحد الأقصى الآمن لحجم البيانات داخل الـ SavedStateHandle؟\"\n  **المرشح:** \"الحد الأقصى النظري للـ Binder Transaction Buffer هو حوالي 1 ميجابايت مشترك لكل المعاملات في العملية، وعملياً لازم منحطش أكتر من 50 لـ 100 كيلوبايت كحد أقصى، وبنقتصر فقط على المعرفات زي IDs ونصوص حقول الإدخال، وبنخزن البيانات الكبيرة في Room.\"",
        "self_check_ar": "فرّق بين تدمير الشاشة وموت العملية؛ اشرح سبب عدم استدعاء `onDestroy()` عند إرسال `SIGKILL`؛ حدد حجم البيانات المسموح به في الـ Saved State؛ صمم مسار استعادة آمن لعملية شراء؛ واشرح كيفية محاكاة موت العملية من سطر الأوامر.",
        "references_ar": f"- [Processes and app lifecycle](https://developer.android.com/guide/components/activities/process-lifecycle) — أولويات العمليات وسلوك الـ LMK.\n- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — حدود الـ SavedState والحفظ الدائم.\n- [SavedStateHandle documentation](https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate) — تكامل الـ ViewModel مع حالة النظام المحفوظة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "موت العملية أو Process Death بيحصل لما نظام أندرويد يقتل الـ Linux Process في الخلفية لتوفير الرام، وده بيمسح كل كائنات الذاكرة والـ ViewModels تماماً. بخلاف الـ Configuration Change اللي بيحافظ على الـ Process والـ ViewModel، استعادة الشاشة بعد موت العملية بتعتمد حصرياً على الـ SavedStateHandle والبيانات المتخزنة في القرص.",
        "best_answer_ar": "الفرق بين الـ Configuration Change والـ Process Death هو خط فاصل في هندسة تطبيقات أندرويد.\n\nفي التدوير أو تغيير الإعدادات، الـ Activity بتتعدل لكن الـ Linux Process بتفضل شغالة في الذاكرة، وبالتالي كل الـ ViewModels والـ Singletons والكاش بيفضلوا عايشين ومحميين في الـ Heap.\n\nأما في الـ Process Death، المستخدم بيحط التطبيق في الخلفية، ولما النظام يحتاج رام لتطبيقات تانية، الـ Low Memory Killer بيقتل العملية كلها بإشارة SIGKILL فورية. ده معناه إن مفيش كود Java هيلحق يشتغل، وonDestroy مش هتتنفذ، وكل محتويات الـ Heap بما فيها الـ ViewModels هتتمسح تماماً من الذاكرة.\n\nالرابط الوحيد اللي بيخلي التطبيق يرجع لنفس الشاشة لما المستخدم يفتحه من الـ Recents هو الـ SavedInstanceState Bundle، اللي النظام سحبه عبر الـ IPC وخزنه في سيرفر النظام قبل القتل. في المعمارية الحديثة بنقرأ الحزمة دي من خلال SavedStateHandle جوه الـ ViewModel لاستعادة معرفات العناصر ونصوص الحقول، ومنها بنعيد تحميل البيانات الحقيقية من قاعدة بيانات Room أو السيرفر.",
        "deep_answer_ar": "على مستوى نواة لينكس والـ Android OS Runtime، كل عملية بيتعمل لها تقييم ديناميكي لقيم الـ oom_adj score من خلال الـ ActivityManagerService. لما التطبيق يكون في الواجهة بياخد درجة صفر، لكن أول ما يروح للخلفية ويستقر في onStop، درجته بتترفع لمستوى الـ Cached Processes فوق 900. تحت ضغط الذاكرة، عفريت الذاكرة المنخفضة LMKD بيبعت إشارة SIGKILL من النواة للعمليات صاحبة أعلى سكور، وده إنهاء قسري بيتجاوز الـ ART Runtime ومبيديش أي فرصة لاستدعاء onDestroy في الـ Activity أو onCleared في الـ ViewModel.\n\nعلشان كده أندرويد بيستدعي onSaveInstanceState بين onPause وonStop، وبيشيل نسخة serialized من الـ Bundle في ذاكرة الـ system_server. لكن العملية دي مقيدة بـ Binder IPC Buffer سعته 1 ميجابايت للعملية كلها؛ لو المطور حاول يخزن List كبيرة أو Bitmaps جوه SavedStateHandle التطبيق هيعمل كراش TransactionTooLargeException فوري.\n\nالمهندس المحترف بيطبق تدرج ثلاثي صارم للحالة: حالة الواجهة المؤقتة السريعة بتعيش في الـ ViewModel Heap علشان تنجو من التدوير، ومفاتيح إعادة التكوين الخفيفة زي IDs وحقول النصوص بتتسجل في SavedStateHandle علشان تنجو من موت العملية، والبيانات الدائمة الحقيقية بتتحفظ فوراً في Room. ولما المستخدم يرجع بعد موت العملية، الشاشة بتستلم الـ ID من SavedStateHandle وتبعت استعلام آمن للسيرفر بدون أي تكرار للعمليات الحساسة."
    }

    # =========================================================================
    # AND-08: What is ViewModel, and when is it cleared?
    # =========================================================================
    qid = "AND-08"
    concept_en = """The Jetpack ViewModel is a specialized architectural component designed to store and manage UI-related data in a lifecycle-conscious manner, decoupling presentation state and business logic from UI controllers such as Activities and Fragments. Its primary architectural value is configuration resilience: because it is retained in memory across Activity recreations, it eliminates redundant network requests, database re-queries, and expensive data recomputations caused by screen rotation, dark mode switching, or window resizing.

A ViewModel's retention and disposal are dictated by its associated ViewModelStoreOwner. The owner supplies a ViewModelStore—an in-memory dictionary mapping ViewModel class keys to ViewModel instances. During a configuration change, the framework transfers this ViewModelStore from the dying Activity instance to the newly instantiated Activity instance via non-configuration token retention in ActivityThread. Consequently, the ViewModel instance remains undisturbed on the JVM heap.

The ViewModel's terminal lifecycle callback is onCleared(). This method is invoked exclusively when the host ViewModelStoreOwner reaches the end of its lifecycle and is permanently destroyed without recreation. Key triggers include: the user finishing an Activity by pressing the back gesture or calling finish(); a Fragment being permanently detached and popped from the FragmentManager backstack; or a Jetpack Compose navigation destination being popped from the NavBackStackEntry. When onCleared() is invoked, the framework automatically cancels the associated viewModelScope, stopping all active child coroutines and freeing asynchronous resources, after which the ViewModel instance becomes eligible for garbage collection."""

    walkthrough_en = """Examining the ViewModel clearing lifecycle in a real-time messaging application:
```kotlin
class ChatViewModel(
    private val chatSocket: ChatSocketManager,
    private val repository: MessageRepository
) : ViewModel() {

    init {
        // Connect to the WebSocket when ViewModel is created
        chatSocket.connect()
    }

    fun sendMessage(text: String) {
        viewModelScope.launch {
            repository.dispatchMessage(text)
        }
    }

    override fun onCleared() {
        super.onCleared()
        // onCleared is invoked only when the screen is permanently destroyed
        chatSocket.disconnect()
    }
}
```
Lifecycle behavior during user interaction:
1. When the user rotates the device, the host Activity is destroyed and recreated. The ChatViewModel is retained by the ViewModelStore, the WebSocket connection remains uninterrupted, and onCleared() is NOT called.
2. If the user navigates to an image preview and returns, the ChatViewModel persists in memory.
3. When the user presses the Back button or leaves the chat screen permanently, the host Activity finishes (isFinishing == true). The framework clears the ViewModelStore, cancels all jobs running in viewModelScope, and invokes onCleared(), disconnecting the socket cleanly and preventing thread leaks."""

    short_en = """A Jetpack ViewModel is an architectural state holder that survives configuration changes by being retained within the host ViewModelStore. Its onCleared() callback is invoked exclusively when the host ViewModelStoreOwner is permanently finished—such as when an Activity finishes, a Fragment is popped from the backstack, or a Compose destination is cleared—automatically cancelling its viewModelScope."""

    structured_en = """To begin with, a Jetpack ViewModel serves as the presentation state holder and business logic coordinator for a screen, designed specifically to decouple operational state from transient UI controllers like Activities and Fragments. It abstracts asynchronous workflows and exposes reactive state streams to the view layer.

From an architectural standpoint, the ViewModel survives configuration changes because it is managed by a ViewModelStore tied to a ViewModelStoreOwner. When an Activity undergoes recreation due to rotation or theme changes, the underlying Android framework transfers the existing ViewModelStore across the recreation boundary via retained non-configuration instances, ensuring that data pipelines and ongoing coroutines remain continuous.

As for boundary management, the ViewModel must never retain a direct reference to an Activity, Fragment, View, or visual Context. Holding a UI reference inside a ViewModel pins the destroyed view hierarchy in memory across configuration changes, causing severe memory leaks.

In production scenarios, the terminal method onCleared() is executed only when the host owner is permanently destroyed, such as when an Activity calls finish() or a navigation destination is popped from the backstack. At this boundary, the runtime cancels viewModelScope and releases background sockets, caches, or event subscriptions gracefully."""

    deep_senior_en = """At the platform architecture level, ViewModel lifecycle orchestration is governed by the ViewModelStoreOwner contract implemented by ComponentActivity, Fragment, and NavBackStackEntry. When an Activity initializes, its ViewModelProvider looks up the requested ViewModel within the Activity's ViewModelStore. If an instance already exists for that key, it is returned; otherwise, the ViewModelProvider.Factory instantiates a new one and registers it in the internal HashMap.

During an Activity configuration recreation cycle, ComponentActivity invokes onRetainNonConfigurationInstance(), encapsulating the ViewModelStore inside a platform NonConfigurationInstances object. The ActivityTaskManagerService preserves this handle in the system server's ActivityRecord. When the ActivityThread constructs the subsequent Activity instance, it supplies this cached record back via attach(). The new Activity re-adopts the same ViewModelStore, allowing ViewModelProvider to locate the exact identical ViewModel instances from heap memory without invoking their constructors or onCleared().

The invocation of onCleared() occurs strictly when the ViewModelStore.clear() method is called. ComponentActivity listens to its own Lifecycle; if the Activity transitions to DESTROYED and isFinishing() returns true, or if changingConfigurations() returns false, it concludes that the destruction is permanent. At that moment, ViewModelStore iterates over all registered ViewModel instances and triggers their clear() implementation.

Internally, ViewModel.clear() calls the protected onCleared() callback and immediately dispatches cancellation to its Closeable resources, including the internal SupervisorJob backing viewModelScope. In modern multi-module architecture, scoping ViewModels correctly to navigation graph destinations (NavBackStackEntry) or shared parent Fragment backstacks provides bounded data lifetimes, preventing stale state leakage across feature boundaries."""

    ee.update_canonical_question(qid, concept_en, walkthrough_en, structured_en, deep_senior_en, short_en)

    metadata_entries[qid] = {
        "id": qid,
        "questionAr": "ما هو الـ ViewModel ومتى يتم استدعاء دالة onCleared()؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- تحديد الـ ViewModel كحامل لحالة الشاشة مرتبط بنطاق `ViewModelStoreOwner`.\n- التمييز بين النجاة من تدوير الشاشة (Configuration Retention) وبين موت العملية (Process Death).\n- اختيار النطاق الصحيح وتجنب الاحتفاظ بمراجع الـ Activity أو الـ Views لمنع تسريب الذاكرة.",
        "why_it_matters_ar": "الـ ViewModel في Android Jetpack صُمم ليفصل منطق الأعمال والبيانات عن دورة حياة واجهة المستخدم المتغيرة. ميزته المعمارية الأساسية هي النجاة من الـ Configuration Changes؛ فعند تدوير الشاشة، لا يُعاد تحميل البيانات من الشبكة أو قاعدة البيانات لأن كائن الـ ViewModel يظل حياً في الذاكرة داخل `ViewModelStore`. دالة `onCleared()` هي نقطة النهاية الرسمية في دورة حياة الـ ViewModel، وتُستدعى حصرياً عندما تنتهي الشاشة نهائياً ولا تعود للظهور، مثل إنهاء الـ Activity أو إخراج الـ Fragment من الـ Backstack. عند هذه اللحظة، يتم إلغاء `viewModelScope` تلقائياً لتنظيف الكوروتينات وتحرير الموارد.",
        "worked_example_ar": "في شاشة المحادثة الفورية، يتم فتح اتصال WebSocket وإغلاقه عند تدمير الشاشة نهائياً عبر `onCleared()`:\n```kotlin\nclass ChatViewModel(\n    private val chatSocket: ChatSocketManager,\n    private val repository: MessageRepository\n) : ViewModel() {\n    init {\n        chatSocket.connect()\n    }\n\n    fun send(text: String) {\n        viewModelScope.launch { repository.sendMessage(text) }\n    }\n\n    override fun onCleared() {\n        super.onCleared()\n        // تُستدعى فقط عند مغادرة الشاشة نهائياً وليس عند التدوير\n        chatSocket.disconnect()\n    }\n}\n```\nعند تدوير الشاشة 10 مرات، لا تُستدعى `onCleared()` ويظل الاتصال مستمراً، وتُستدعى مرة واحدة فقط عند الضغط على زر الرجوع لإنهاء المحادثة.",
        "trade_offs_ar": "ربط الـ ViewModel بنطاق الـ Activity يسمح بمشاركة البيانات بين عدة Fragments، لكنه قد يحتفظ بالبيانات في الذاكرة لفترة أطول من اللازم. في المقابل، ربط الـ ViewModel بوجهة التنقل (Navigation Destination) يضمن تحرير الذاكرة فور مغادرة الشاشة. الـ ViewModel ممتاز للحالة المؤقتة الكبيرة، لكنه لا يحمي البيانات ضد موت العملية (Process Death) بمفرده بدون `SavedStateHandle`. استخدام الـ ViewModel مع Compose يجب أن يقتصر على مستوى الشاشة (Screen-level) مع تفضيل كائنات الحالة البسيطة للـ Composables الداخلية.",
        "failure_modes_ar": "الاحتفاظ بمرجع لـ Activity أو View أو Context داخل الـ ViewModel يتسبب في تسريب شجرة الـ Views والنافذة في الذاكرة عند كل تدوير للشاشة. إطلاق كوروتينات في نطاقات خارجية غير مرتبطة بـ `viewModelScope` قد يترك مهاماً مهدرة تعمل في الخلفية بعد مغادرة الشاشة. الاعتماد على الـ ViewModel لحفظ بيانات الإدخال أثناء موت العملية يفرغ حقول الشاشة بالكامل عند العودة. يتم فحص هذه التسريبات بأداة LeakCanary واختبارات إنهاء الشاشة.",
        "production_perspective_ar": "في شاشات البحث والمنتجات، يمتلك الـ ViewModel منطق تحويل النصوص المدخلة إلى تدفق نتائج وإلغاء الاستعلامات السابقة غير المكتملة عبر `flatMapLatest`. يتم ربطه بنطاق وجهة الشاشة لضمان استدعاء `onCleared()` فور مغادرتها. يتم دمج `SavedStateHandle` لاستعادة معايير البحث بعد موت العملية، مع كتابة اختبارات وحدة تعتمد على `TestDispatcher` للتحقق من إلغاء كافة المهام فور استدعاء `onCleared()`.",
        "how_to_answer_ar": "- **السبب المعماري:** وضح دور الـ ViewModel في فصل منطق الواجهة والنجاة من التدوير عبر `ViewModelStore`.\n- **طريقة الشرح:** بيّن متى يتم استدعاء `onCleared()` (عند الانتهاء الدائم للشاشة وليس التدوير).\n- **المفاضلات:** قارن بين نطاق الـ Activity ونطاق وجهة التنقل وحجم الموارد المحتفظ بها.\n- **أنماط الفشل:** حذر بقوة من تمرير الـ Context أو الـ Views داخل الـ ViewModel ومخاطر تسريب الذاكرة.\n- **الحل العملي:** استشهد بكود إدارة مقبس المحادثة وتنظيفه الآمن في `onCleared()`.",
        "talking_points_ar": "ناقش عقد `ViewModelStoreOwner`، وكيفية نقل `ViewModelStore` عبر `NonConfigurationInstances` في `ActivityThread`، والتحقق من `isFinishing()` لاستدعاء `onCleared()`، وكيفية إلغاء `SupervisorJob` المرفق بـ `viewModelScope`، وإدارة الـ ViewModels المشتركة بين وجهات Jetpack Navigation عبر `NavBackStackEntry`.",
        "follow_ups_ar": "- **المحاور:** \"هل ينفع نحتفظ بمرجع لـ Activity أو View جوه الـ ViewModel؟\"\n  **المرشح:** \"ممنوع نهائياً. لو الـ ViewModel احتفظ بمرجع لـ Activity أو View، لما الشاشة تدور وتتدمر، الـ ViewModel اللي عايش في الذاكرة هيفضل ماسك الـ Activity القديمة وشجرة الـ Views بتاعتها وهيمنع الـ Garbage Collector من تنظيفها وده بيعمل Memory Leak مباشر وضخم. لو محتاجين Context بنستخدم `AndroidViewModel` مع `Application Context` فقط.\"\n\n- **المحاور:** \"إيه الفرق بين استدعاء finish() وتدوير الشاشة بالنسبة لـ onCleared()؟\"\n  **المرشح:** \"في تدوير الشاشة، الـ Activity بتتدمر بس `isFinishing` بتكون false، فالنظام بينقل الـ ViewModelStore للشاشة الجديدة وonCleared مبترنش. أما مع استدعاء `finish()` فالـ Activity بتنتهي نهائياً و `isFinishing` بتكون true، وهنا الـ ViewModelStore بيتعمله clear وonCleared بتترن فوراً.\"\n\n- **المحاور:** \"إزاي بتشارك ViewModel واحد بين أكتر من Fragment؟\"\n  **المرشح:** \"بنطلب الـ ViewModel باستخدام نطاق الـ Activity كـ `ViewModelStoreOwner` عبر `activityViewModels()`، فساعتها كل الـ Fragments التابعة لنفس الـ Activity بتستلم نفس نسخة الـ ViewModel من نفس الـ Store، أو بنربطه بـ NavGraph المشترك.\"",
        "self_check_ar": "عرّف دور الـ ViewModel ومكان تخزينه؛ حدد الشروط الدقيقة لاستدعاء `onCleared()`؛ اشرح مخاطر الاحتفاظ بمرجع واجهة المستخدم؛ وصمم سيناريو لتنظيف مقبس شبكة في `onCleared()`.",
        "references_ar": f"- [ViewModel overview](https://developer.android.com/topic/libraries/architecture/viewmodel) — معمارية ودورة حياة الـ ViewModel.\n- [ViewModel lifecycle and scopes](https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-factories) — إدارة الـ ViewModelStore ونطاقات المالك.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ ViewModel هو مكون معماري في أندرويد لحفظ وإدارة حالة الواجهة، بينجو من تدوير الشاشة لأن كائن الـ ViewModelStore بيفضل محفوظ في الذاكرة. دالة onCleared بتستدعى حصرياً لما الشاشة تنتهي نهائياً ومترجعش تاني، زي لما المستخدم يدوس Back أو تنادي finish، وساعتها بيتم إلغاء viewModelScope ومسح الموارد.",
        "best_answer_ar": "الـ ViewModel في Jetpack مصمم أساساً علشان يفصل بيانات الواجهة ومنطق الأعمال عن الشاشات، ويوفر استقرار تام للحالة وقت الـ Configuration Changes.\n\nبيفضل عايش في الذاكرة لأن النظام بيخزنه جوه ViewModelStore خاص بالـ ViewModelStoreOwner زي الـ Activity أو الـ Fragment. ولما الشاشة بتدور، النظام بيهدم الـ Activity القديمة بس بينقل الـ Store بالكامل للـ Activity الجديدة بدون ما يلمس الـ ViewModels اللي جواه في الـ Heap.\n\nالسؤال الأهم: إمتى onCleared بتترن؟\n\nonCleared بتستدعى فقط في لحظة الموت النهائي للشاشة؛ يعني لو المستخدم داس زر الرجوع، أو ناديت finish وisFinishing بقت true، أو الـ Fragment اتشال نهائياً من الـ Backstack، أو وجهة الـ Compose طلعت من الـ NavBackStackEntry.\n\nفي اللحظة دي، الـ Store بيتعمله clear، وonCleared بتترن لتنظيف المقابس والكاش، ونظام أندرويد بيلغي الـ viewModelScope تلقائياً فكل الكوروتينات الشغالة بتقف بسلام.\n\nالقاعدة الذهبية في الإنتاج: إياك تحتفظ بأي مرجع لـ Activity أو View جوه الـ ViewModel لتجنب تسريب الذاكرة.",
        "deep_answer_ar": "على مستوى بنية أندرويد الداخلية، الـ ViewModelStoreOwner هو العقد الأساسي اللي بتطبقه كلاسات زي ComponentActivity وFragment وNavBackStackEntry. الـ ViewModelProvider بيبحث جوه HashMap داخلية في الـ ViewModelStore؛ لو الكائن موجود بيرجعه فوراً، ولو مش موجود بينشئه بالـ Factory ويسجله في الـ Map.\n\nأثناء التدوير، الـ ComponentActivity بتنفذ دالة onRetainNonConfigurationInstance، فبتحط الـ ViewModelStore جوه كائن NonConfigurationInstances خاص، والـ ActivityTaskManagerService بيحتفظ بيه في الـ system_server. ولما الـ ActivityThread يرجع ينشئ الـ Activity الجديدة بيبعت لها نفس الكائن في دالة attach، فـ ViewModelProvider يلاقي نفس الـ Store ونفس النسخ بالمللي في الـ Heap بدون ما يستدعي constructor جديد أو ينادي onCleared.\n\nاستدعاء onCleared بيحصل لما الـ Lifecycle يوصل لـ DESTROYED وتكون حالة isFinishing بترجع true، أو لما changingConfigurations تكون false. في التوقيت ده الـ ViewModelStore بينادي دالة clear، اللي بتمر على كل ViewModels وبتستدعي onCleared وبتلغي الـ Closeables المسجلة بما فيها الـ SupervisorJob بتاع viewModelScope.\n\nفي المعمارية الحديثة للشركات الكبيرة بنتحكم في Scope الـ ViewModel بدقة؛ بنربطه بـ NavBackStackEntry لوجه معينة أو لمسار فرعي (Nested Graph) علشان نضمن إن البيانات الحساسة زي بيانات سلة المشتريات تتصفر فوراً من الرام أول ما العميل يتم عملية الدفع ويخرج من مسار الشراء."
    }

    # =========================================================================
    # AND-09: Compare ViewModel, SavedStateHandle, rememberSaveable, and persistent storage.
    # =========================================================================
    qid = "AND-09"
    concept_en = """Managing state across different application lifespans requires a coherent multi-tiered persistence strategy in Android. Modern applications navigate four distinct state storage mechanisms, each serving a unique architectural scope, memory boundary, and survival guarantee:

1. Jetpack ViewModel:
Scoped to the ViewModelStoreOwner, the ViewModel stores presentation and business state directly on the JVM heap. It survives configuration changes seamlessly without serialization overhead, making it ideal for rich domain models, pagination streams, and active coroutine pipelines. However, because it lives purely in volatile process RAM, it is completely erased upon process death or device reboots.

2. SavedStateHandle:
Integrated directly into the Jetpack ViewModel via SavedStateRegistry, SavedStateHandle bridges process death. It serializes state into the Activity's onSaveInstanceState Bundle, which the Android operating system caches inside the system_server process across Binder IPC. It survives both configuration changes and background process death, but not device reboots. Because Binder transactions share a strict global 1MB buffer, SavedStateHandle is restricted to small navigation arguments, search query strings, and entity IDs (strictly keeping payloads under 50KB to avoid TransactionTooLargeException).

3. rememberSaveable (Jetpack Compose):
Operating within the Composable UI tree, rememberSaveable retains transient element state across recomposition, configuration changes, and process death. It delegates to the SaveableStateRegistry, saving primitive or Parcelable UI state (such as text input drafts, scroll positions, or expandable modal visibility) directly into the host Activity Bundle.

4. Persistent Storage (Room, DataStore, EncryptedSharedPreferences):
Stored on non-volatile flash storage (disk), persistent storage outlives everything: configuration changes, process death, task dismissal, and device power reboots. It serves as the single source of truth for critical application data, user authentication tokens, business transaction ledgers, and cached offline feeds, accessed asynchronously via background dispatchers."""

    walkthrough_en = """Comparative architectural decision matrix across state mechanisms:

| Dimension | ViewModel | SavedStateHandle | rememberSaveable | Persistent Storage (Room/DataStore) |
| :--- | :--- | :--- | :--- | :--- |
| Physical Storage | JVM Heap Memory | OS Binder Buffer | OS Binder Buffer | Flash Disk Storage |
| Configuration Change | Survives | Survives | Survives | Survives |
| Process Death | Erased (Lost) | Survives | Survives | Survives |
| Device Reboot | Erased (Lost) | Erased (Lost) | Erased (Lost) | Survives |
| Access Latency | Instantaneous (O(1)) | Fast (Deserialization) | Fast (Recomposition) | Slower (Disk I/O) |
| Safe Payload Size | Unlimited (Heap bound) | Under 50 KB | Under 50 KB | Gigabytes (Disk bound) |
| Architectural Role | Business & UI logic | Restoration keys & IDs | Local UI element state | Single Source of Truth |

Failure scenario in production:
An engineer caches a list of 500 search results or a camera bitmap inside SavedStateHandle. When the user backgrounds the app, the system invokes onSaveInstanceState, throwing a fatal TransactionTooLargeException and terminating the app.
Remediation: Store only the search query string in SavedStateHandle, persist the full search results in Room, and retain the active display list in ViewModel StateFlow."""

    short_en = """ViewModel holds rich state in volatile JVM memory across configuration changes. SavedStateHandle serializes compact restoration keys into the system server to survive process death. rememberSaveable preserves local Composable UI state across both events via the same Bundle mechanism. Persistent storage (Room/DataStore) writes to flash disk, providing the durable single source of truth across process termination and device reboots."""

    structured_en = """To begin with, Android state management requires a structured four-tier strategy based on lifecycle durability, storage location, and size limits. A Jetpack ViewModel maintains complex domain state and active coroutines directly on the JVM heap, surviving configuration changes with zero serialization cost, but it is wiped completely upon process death.

From an architectural standpoint, SavedStateHandle provides the bridge across background process death. It serializes lightweight reconstruction tokens, such as user IDs or filter selections, into the platform Bundle stored in system_server. Because this serialization traverses the shared 1MB Binder transaction buffer, its payload must remain strictly under 50KB.

As for boundary management, rememberSaveable mirrors SavedStateHandle within the Jetpack Compose tree. It preserves transient widget-level state, such as sheet expansions and text drafts, across recomposition, rotation, and process death through Compose's SaveableStateRegistry.

In production scenarios, persistent storage—using Room databases or DataStore—acts as our definitive single source of truth. It writes directly to flash disk, surviving process kills and device reboots. We store durable entity models on disk, retain active UI streams in the ViewModel, and keep only minimal navigation keys in SavedStateHandle."""

    deep_senior_en = """At the operating system and IPC layer, the boundary separating these four mechanisms is defined by Linux memory spaces and Binder transaction mechanics. A ViewModel is hosted exclusively in the application's user-space virtual memory. When the Linux Out-Of-Memory killer terminates the process via SIGKILL, the memory pages mapped to the ART heap are immediately reclaimed, obliterating all ViewModel instances without invocation of finalizers.

To overcome this, Android provides the SavedStateRegistry framework. When an Activity enters onStop, the framework collects registered state providers into a composite Bundle and transfers it via an IPC transaction to ActivityTaskManagerService inside the system_server process. This IPC payload is constrained by the kernel Binder transaction buffer, which is globally capped at 1MB for all concurrent transactions per process.

If an application serializes large Collections, heavy Parcelable objects, or Bitmaps into SavedStateHandle or rememberSaveable, the Binder driver rejects the transaction with a native BR_FAILED_REPLY, causing the Android Runtime to crash with a TransactionTooLargeException. Therefore, SavedStateHandle and rememberSaveable must be treated strictly as reconstruction indices, holding primitive keys, filter criteria, and scroll offsets, never bulk payloads.

Meanwhile, persistent storage engines like Room operate on SQLite databases stored in private app sandboxes. Because disk writes involve synchronous or asynchronous filesystem I/O, writing data on the main thread invites Application Not Responding (ANR) events. Production architectures decouple these tiers cleanly: Room persists authoritative domain models on Dispatchers.IO; the Repository exposes immutable reactive streams; the ViewModel maps these into presentation state in memory; and SavedStateHandle retains the minimal entity ID required to re-query the database following an unexpected process death."""

    ee.update_canonical_question(qid, concept_en, walkthrough_en, structured_en, deep_senior_en, short_en)

    metadata_entries[qid] = {
        "id": qid,
        "questionAr": "قارن بين الـ ViewModel والـ SavedStateHandle والـ rememberSaveable والتخزين الدائم (Persistent Storage).",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- تحديد مكان تخزين ونطاق كل آلية لحفظ الحالة، وعمرها الافتراضي، وضمانات بقائها.\n- تجنب التعامل مع حزمة الـ Bundle كأنها قاعدة بيانات واستيعاب قيود الـ Binder Buffer.\n- تصميم شاشة متكاملة تستعيد حالتها بسلاسة بعد التدوير وموت العملية وإعادة تشغيل الهاتف.",
        "why_it_matters_ar": "إدارة الحالة في أندرويد تتطلب استراتيجية متعددة الطبقات لتغطية كافة سيناريوهات فقدان البيانات. الـ ViewModel يعيش في ذاكرة الـ Heap ويوفر أداءً فورياً أثناء تدوير الشاشة بدون استهلاك للوقت في الـ Serialization، ولكنه يُمحى تماماً عند موت العملية. الـ SavedStateHandle يربط الـ ViewModel بحزمة النظام (`SavedInstanceState`) المحفوظة في `system_server`، مما يجعله ينجو من موت العملية لكنه مقيد بحجم الـ Binder IPC (أقل من 50 كيلوبايت). دالة `rememberSaveable` تطبق نفس الفكرة داخل شجرة Compose للحالة المؤقتة لعناصر الواجهة. والتخزين الدائم في Room أو DataStore هو الوحيد الذي ينجو من إعادة تشغيل الهاتف ويشكل مصدر الحقيقة النهائي للتطبيق.",
        "worked_example_ar": "في شاشة تفاصيل المنتج، نحتفظ بالـ `productId` في `SavedStateHandle`، ونخزن حالة التبويب المحدد في `rememberSaveable`، بينما تُدار بيانات المنتج في الـ ViewModel وتُخزن محلياً في Room:\n```kotlin\n@Composable\nfun ProductDetailScreen(\n    viewModel: ProductViewModel = hiltViewModel()\n) {\n    // حالة محلية للواجهة تنجو من موت العملية\n    var selectedTab by rememberSaveable { mutableStateOf(0) }\n    val uiState by viewModel.uiState.collectAsStateWithLifecycle()\n    // رسم الواجهة بناءً على التدفق القادم من ViewModel\n}\n\n@HiltViewModel\nclass ProductViewModel @Inject constructor(\n    savedStateHandle: SavedStateHandle,\n    repository: ProductRepository\n) : ViewModel() {\n    val productId: String = checkNotNull(savedStateHandle[\"productId\"])\n    val uiState = repository.getProductStream(productId)\n        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), ProductUiState.Loading)\n}\n```",
        "trade_offs_ar": "الـ ViewModel فوري وخفيف على المعالج ولا يتطلب Serialization لكنه يضيع في Process Death. الـ SavedStateHandle ينجو من موت العملية لكنه مقيد بحجم حزمة النظام والـ Parcelable Overhead. دالة `rememberSaveable` سهلة الاستخدام داخل Compose لكنها خاصة بعناصر الواجهة فقط ولا تناسب منطق الأعمال. التخزين في Room أو DataStore دائم ومستقر ويستوعب أحجاماً كبيرة لكنه يستهلك عمليات I/O ويتطلب معالجة خلفية غير متزامنة.",
        "failure_modes_ar": "وضع كائنات كبيرة مثل Bitmaps أو قوائم طويلة في `SavedStateHandle` أو `rememberSaveable` يؤدي فوراً إلى كراش `TransactionTooLargeException` أثناء إغلاق التطبيق. الاكتفاء بالـ ViewModel لحفظ مدخلات المستخدم يعرضه لفقدان كل ما كتبه بمجرد استقبال مكالمة هاتفية تؤدي لقتل العملية في الخلفية. القراءة والكتابة في Room على الـ Main Thread تسبب تجمد التطبيق وظهور خطأ ANR. يتم اختبار هذه الحالات بمحاكاة موت العملية والتأكد من بقاء الحزمة أقل من 50 كيلوبايت.",
        "production_perspective_ar": "في تطبيقات الإنتاج الضخمة، يُعتبر Room أو DataStore هو مصدر الحقيقة الوحيد (Single Source of Truth) لكافة البيانات الهامة. يقتصر دور `SavedStateHandle` على حفظ المعرفات ومفاتيح التنقل فقط (مثل `orderId` أو نص البحث الحالي)، وتُستخدم `rememberSaveable` لحالات الواجهة البسيطة مثل رقم التبويب أو موضع التمرير في القائمة. بهذه الطريقة يتم تفادي استهلاك مساحة الـ Binder Buffer بالكامل، وتستعيد الشاشة حالتها بدقة بعد أي عملية قتل من النظام.",
        "how_to_answer_ar": "- **السبب المعماري:** اعرض هرمية حفظ الحالة الأربعة كطبقات مكملة لبعضها في دورة حياة النظام.\n- **طريقة الشرح:** قارن بينها من حيث مكان التخزين (Heap مقابل Binder مقابل Disk) والقدرة على النجاة.\n- **المفاضلات:** وضح قيود حجم البيانات في الـ SavedStateHandle وسرعة القراءة في الـ ViewModel.\n- **أنماط الفشل:** حذر من `TransactionTooLargeException` وفقدان البيانات عند إهمال موت العملية.\n- **الحل العملي:** استشهد بنموذج شاشة تفاصيل المنتج وتوزيع الحالة بين Compose وViewModel وRoom.",
        "talking_points_ar": "ناقش حدود ذاكرة الـ Binder Buffer البالغة 1 ميجابايت على مستوى العملية، وتكامل `SaveableStateRegistry` مع Compose، وتجنب الـ UI Freezes باستخدام `Dispatchers.IO` للتعامل مع Room، وكيفية التعامل مع الـ Process Death دون استدعاء طلبات شبكة غير مبررة عبر استغلال التخزين المحلي كـ Offline Cache.",
        "follow_ups_ar": "- **المحاور:** \"إيه الخطأ اللي هيحصل لو حطيت بيانات ضخمة جوه SavedStateHandle؟\"\n  **المرشح:** \"التطبيق هيعمل كراش فوري بـ `TransactionTooLargeException`. لأن كل المعاملات اللي بتتنقل عبر الـ Binder IPC لنظام أندرويد بتشترك في Buffer سعته الإجمالية 1 ميجابايت لكل الـ Process، ولو حزمة الشاشة زادت عن الحد ده النظام بيرمي Exception فوراً لما التطبيق يدخل الخلفية.\"\n\n- **المحاور:** \"إمتى استخدم rememberSaveable وإمتى استخدم SavedStateHandle؟\"\n  **المرشح:** \"دالة rememberSaveable مخصصة لحالة الواجهة البحتة جوه الـ Composable زي رقم التاب أو حالة القائمة منسدلة أو نص في TextField بسيط. أما SavedStateHandle فبيكون جوه الـ ViewModel لمفاتيح التنقل والـ IDs اللي بيحتاجها الـ Business Logic علشان يحمل بيانات الشاشة.\"\n\n- **المحاور:** \"هل التخزين الدائم زي Room يغنينا عن استخدام ViewModel؟\"\n  **المرشح:** \"لأ طبعاً. الـ ViewModel بيمثل طبقة العرض والـ In-memory cache السريع اللي بيتعامل مباشرة مع الواجهة في الـ Main Thread بأقل Latency، بينما Room بيتعامل مع القرص وبيحتاج Coroutines وI/O Dispatcher، ومينفعش نربط الواجهة مباشرة بالقرص في كل رندرة.\"",
        "self_check_ar": "حدد مكان تخزين كل آلية من الآليات الأربع؛ بيّن ما ينجو عند تدوير الشاشة وعند موت العملية وعند إعادة التشغيل؛ اشرح سبب خطأ TransactionTooLargeException؛ وصمم بنية حالة متكاملة لشاشة تجارة إلكترونية.",
        "references_ar": f"- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — دليل حفظ حالات واجهة المستخدم.\n- [State and Jetpack Compose](https://developer.android.com/develop/ui/compose/state) — إدارة الحالة ودالة rememberSaveable.\n- [Room persistence library](https://developer.android.com/training/data-storage/room) — التخزين المحلي الدائم.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ ViewModel بيخزن البيانات الكبيرة في الذاكرة الحية وبينجو من التدوير فقط. والـ SavedStateHandle و rememberSaveable بيحفظوا المعرفات وحالة الواجهة البسيطة في حزمة النظام وبينجوا من التدوير وموت العملية عبر الـ Binder. أما التخزين الدائم في Room و DataStore فبيكتب على القرص وهو الوحيد اللي بينجو من كل حاجة بما فيها قفل الموبايل.",
        "best_answer_ar": "في المعمارية النظيفة بنقسم حفظ الحالة لأربع مستويات متكاملة حسب مكان التخزين وفترة الحياة.\n\nأول مستوى هو الـ ViewModel: وده بيعيش في الـ JVM Heap، ممتاز للبيانات الضخمة والـ StateFlows والكوروتينات الشغالة، وبينجو من التدوير بدون أي تكلفة Serialization، لكنه بيتمسح تماماً بمجرد موت العملية أو إغلاق التطبيق.\n\nتاني مستوى هو SavedStateHandle: وده بيحفظ البيانات في حزمة النظام عبر الـ Binder IPC، وبالتالي بينجو من التدوير ومن الـ Process Death، بس لازم يقتصر على الـ IDs ونصوص البحث الصغيرة علشان منعديش مساحة الـ Binder Buffer.\n\nتالت مستوى هو rememberSaveable: وده النسخة المصغرة للـ Compose UI لحفظ حالات العناصر البسيطة زي موضع السكرول أو القوائم المفتوحة داخل حزمة الشاشة عبر SaveableStateRegistry.\n\nرابع مستوى هو التخزين الدائم زي Room و DataStore: وده بيتكتب على الفلاش ديسك، وهو المصدر الحقيقي والدائم للبيانات اللي بينجو من موت العملية ومن إعادة تشغيل الجهاز.\n\nالقاعدة اللي بنطبقها دايماً: خزن البيانات الحقيقية في Room، احتفظ بحالة العرض السريعة في الـ ViewModel، وسجل المعرفات فقط في SavedStateHandle.",
        "deep_answer_ar": "على مستوى إدارة الذاكرة ونظام تشغيل أندرويد، الفرق بين الأدوات دي بيتحدد بمكان التخزين وطبيعة الـ IPC. الـ ViewModel مساحته هي الـ Virtual Memory بتاعة التطبيق؛ لما LMKD يبعت SIGKILL الصفحات بتتحرر فوراً في النواة فكل كائنات الـ ViewModel بتتبخر.\n\nعلشان نحل المشكلة دي، أندرويد بيوفر آلية SavedStateRegistry؛ عند توقف الشاشة، النظام بيجمع الـ Bundles ويبعتها عبر Binder IPC لـ ActivityTaskManagerService داخل عملية الـ system_server. لكن العملية دي محكومة بـ Shared Binder Transaction Buffer سعته الإجمالية 1 ميجابايت لكل العمليات المتزامنة في الـ Process. لو المطور حط قايمة كبيرة أو كائنات Parcelable معقدة جوه SavedStateHandle أو rememberSaveable، الـ Binder Driver بيرفض المعاملة ويرمي كراش TransactionTooLargeException فوري.\n\nعلشان كده بنستخدم SavedStateHandle و rememberSaveable كـ Reconstruction Tokens فقط؛ يعني بنحفظ مثلاً userId أو orderId لا يتعدى حجمهم بضعة بايتات. وفي المقابل، قواعد بيانات Room ومحركات DataStore بتكتب على مساحة التخزين الدائمة في المسار الخاص بالتطبيق في فلاش الموبايل عبر SQLite. وبما إن قراءة القرص بتستهلك وقت وبتعمل Disk I/O، بنشغلها حصرياً على Dispatchers.IO بعيداً عن الـ Main Thread.\n\nفي التطبيقات الكبيرة بنربط الأربعة ببعض بتناغم: الـ Database بتخزن الكيان، الـ Repository بيطلعه كـ Flow، الـ ViewModel بيحوله لـ StateFlow في الـ Heap، والـ SavedStateHandle بيحتفظ بمفتاح الكيان لإعادة تحميله بسلاسة بعد أي استعادة من موت العملية."
    }

    # =========================================================================
    # AND-10: What are Intent and PendingIntent? Explain explicit versus implicit intents.
    # =========================================================================
    qid = "AND-10"
    concept_en = """In the Android operating system, an Intent is an asynchronous messaging object used to request an action from another app component or to broadcast system-wide events. Intents serve as the fundamental inter-process communication (IPC) abstraction binding Activities, Services, and BroadcastReceivers.

Intents are categorized into two core types:
1. Explicit Intent:
Designates the target component explicitly by specifying either its fully qualified Java or Kotlin class name (such as Intent(context, OrderDetailsActivity::class.java)) or an explicit component identifier. Because the target is predetermined, the runtime routes the message directly to that component within the application or a known target package. Explicit intents are type-safe, fast, and secure.

2. Implicit Intent:
Specifies an abstract general action to be performed (such as ACTION_VIEW, ACTION_SEND, or ACTION_DIAL) alongside data URIs, MIME types, and categories, without declaring the destination class. When launched, the Android PackageManagerService queries all installed applications on the device, matching the intent against registered intent-filters declared in their manifests. If multiple applications match, the system displays an app chooser dialog.

In contrast, a PendingIntent is a token of authorization granted to an external system service or foreign application (such as NotificationManager, AlarmManager, or AppWidgetHost). It encapsulates an underlying Intent along with a delegate permission grant: it authorizes the external process to fire the encapsulated Intent at a future timestamp with the exact identity, Linux User ID (UID), and permissions of the originating application, even if the originating application process is terminated. Modern Android (API 31+) mandates declaring explicit mutability flags (FLAG_IMMUTABLE or FLAG_MUTABLE) to prevent malicious intent modification and hijacking."""

    walkthrough_en = """Constructing and dispatching a secure PendingIntent for a system notification:
```kotlin
// 1. Construct the explicit internal intent with payload
val intent = Intent(context, OrderDetailsActivity::class.java).apply {
    putExtra("order_id", "ORD-12345")
    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
}

// 2. Wrap in PendingIntent with mandatory security flags
val pendingIntent = PendingIntent.getActivity(
    context,
    ORDER_REQUEST_CODE,
    intent,
    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE // Mandatory on Android 12+
)

// 3. Attach to NotificationCompat.Builder
val notification = NotificationCompat.Builder(context, CHANNEL_ID)
    .setContentTitle("Order Shipped")
    .setContentText("Tap to view your tracking details")
    .setSmallIcon(R.drawable.ic_shipping)
    .setContentIntent(pendingIntent)
    .setAutoCancel(true)
    .build()
```
Failure scenario:
If an engineer declares an implicit Intent inside a PendingIntent or omits FLAG_IMMUTABLE, a malicious third-party application on the device can intercept the pending token, alter the embedded Intent's extras or target component (Intent Hijacking), and execute privileged code with the victim application's permissions."""

    short_en = """An Intent is a messaging object requesting an action from a component: explicit intents name the target class directly, while implicit intents declare an abstract action resolved by the OS through intent filters. A PendingIntent is a security token granting an external process permission to execute a preconfigured Intent with the originating app's identity and privileges."""

    structured_en = """To begin with, an Intent is Android's core messaging abstraction, facilitating both intra-process and cross-process communication between Activities, Services, and BroadcastReceivers. It encapsulates the action to be performed, target data URIs, and optional bundle extras.

From an architectural standpoint, intents divide into explicit and implicit variants. An explicit intent specifies the target component class directly, ensuring predictable, internal routing. In contrast, an implicit intent declares a generalized action, such as sharing content or viewing a web URL, prompting the operating system's PackageManagerService to resolve matching components across installed applications via their manifest intent filters.

As for boundary management, a PendingIntent wraps an Intent with delegated execution rights. It passes a token to external system actors, such as NotificationManager, AlarmManager, or AppWidgetHost. When triggered, the receiving system service fires the embedded Intent with the exact Linux identity and permissions of the originating application, even if its process is currently dead.

In production scenarios, security is paramount. Starting in Android 12, developers must explicitly designate every PendingIntent as either FLAG_IMMUTABLE or FLAG_MUTABLE. Defaulting to immutable prevents malicious applications from modifying the underlying intent parameters and executing unauthorized privilege escalation."""

    deep_senior_en = """At the operating system and Linux kernel boundary, Intents and PendingIntents leverage the Binder inter-process communication driver and the system_server's ActivityTaskManagerService. When startActivity(intent) is invoked, the call marshals the Intent structure across Binder to the system server. For explicit intents, the system server directly accesses the target package's ComponentInfo. For implicit intents, PackageManagerService executes an Intent Resolution algorithm, querying its internal IntentResolver tables against registered IntentFilters, evaluating actions, categories, data schemes, and MIME types.

The internal architecture of a PendingIntent is fundamentally different from a standard Intent. A PendingIntent does not pass an executable object; instead, it registers an IIntentSender IPC Binder interface inside the system_server process. The system server maintains an internal PendingIntentRecord that stores the calling application's Linux UID, package name, request code, target Intent, and execution flags.

Because the token is maintained by the system server, when a notification or alarm triggers the token, ActivityTaskManagerService dispatches the intent attributing all security permissions and identity to the originating UID rather than the caller's UID. Historically, this presented a critical security vulnerability known as Intent Redirection or Hijacking (CWE-927). If a PendingIntent was mutable, a malicious receiver could populate the empty Intent fields, redirecting the target component to internal, non-exported Activities containing sensitive financial or user data.

To permanently close this attack surface, Android 12 (API level 31) made declaring FLAG_IMMUTABLE or FLAG_MUTABLE mandatory. A Staff engineer enforces immutable tokens by default, reserving FLAG_MUTABLE exclusively for system integrations that require dynamic payload injection, such as inline notification replies via RemoteInput or custom camera capture URIs."""

    ee.update_canonical_question(qid, concept_en, walkthrough_en, structured_en, deep_senior_en, short_en)

    metadata_entries[qid] = {
        "id": qid,
        "questionAr": "ما هو الـ Intent والـ PendingIntent؟ وما الفرق بين الـ Explicit والـ Implicit Intent؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- التمييز بين رسالة تُنفذ حالياً (Intent) وتوكن أمان مفوض لنظام خارجي (PendingIntent).\n- فهم الفارق بين التوجيه الصريح لفئة محددة والتوجيه الضمني عبر الـ Intent Filters.\n- تطبيق قواعد الأمان الصارمة في أندرويد 12+ واستخدام `FLAG_IMMUTABLE` لمنع ثغرات الاختطاف.",
        "why_it_matters_ar": "الـ Intent هو رسالة التواصل الأساسية بين مكونات النظام في أندرويد (Activities, Services, BroadcastReceivers). الـ Explicit Intent يحدد المكون المستهدف بالاسم الصريح وهو آمن ومباشر. الـ Implicit Intent يحدد الإجراء المطلوب مثل `ACTION_VIEW` ويترك للنظام البحث عن التطبيقات التي تدعم هذا الإجراء عبر مرشحات الـ Intent Filters. أما الـ PendingIntent فهو تصريح أمني وتوكن تفويض يُمنح لعملية خارجية (مثل الـ NotificationManager أو AlarmManager) لتنفيذ الـ Intent نيابة عن تطبيقك وبصلاحيات تطبيقك الكاملة، حتى لو كان التطبيق مغلقاً تماماً. فرض أندرويد 12 تحديد `FLAG_IMMUTABLE` أو `FLAG_MUTABLE` جاء لسد ثغرات أمنية خطيرة في اختطاف الرسائل وتعديلها.",
        "worked_example_ar": "بناء إشعار بنكي آمن باستخدام `PendingIntent`:\n```kotlin\nval intent = Intent(context, TransactionDetailsActivity::class.java).apply {\n    putExtra(\"tx_id\", \"TX-98765\")\n    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP\n}\n\nval pendingIntent = PendingIntent.getActivity(\n    context,\n    REQUEST_CODE,\n    intent,\n    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE // إلزامي في أندرويد 12+\n)\n\nval notification = NotificationCompat.Builder(context, CHANNEL_ID)\n    .setContentTitle(\"إشعار تحويل مالي\")\n    .setContentText(\"اضغط لعرض تفاصيل المعاملة\")\n    .setSmallIcon(R.drawable.ic_bank)\n    .setContentIntent(pendingIntent)\n    .setAutoCancel(true)\n    .build()\n```",
        "trade_offs_ar": "الـ Explicit Intent سريع ومضمون الوصول ولا يمكن اختطافه من تطبيقات أخرى، بينما الـ Implicit Intent يوفر مرونة المشاركة وفتح الروابط عبر تطبيقات خارجية بتكلفة إمكانية عدم وجود تطبيق مؤهل (يتطلب فحص `resolveActivity`). الـ PendingIntent غير القابل للتعديل (`FLAG_IMMUTABLE`) يوفر أعلى درجات الأمان وهو الخيار الافتراضي، بينما (`FLAG_MUTABLE`) يُستخدم حصرياً في سيناريوهات تتطلب ملء بيانات ديناميكية بواسطة النظام مثل الرد السريع من الإشعارات (RemoteInput).",
        "failure_modes_ar": "إرسال Implicit Intent بدون فحص وجود تطبيق يدعمه يتسبب في كراش `ActivityNotFoundException`. إنشاء PendingIntent بدون تحديد أعلام الثبات في أندرويد 12 يسبب كراش `IllegalArgumentException` فوري عند التشغيل. إنشاء Mutable PendingIntent يتيح لتطبيقات خبيثة حقن Extras أو إعادة توجيه الـ Intent لشاشات داخلية غير مصرح بها. يتم اختبار الحالات بفحص سجلات الـ Logcat ومراجعة كافة الـ PendingIntents في المشروع بأدوات التحليل الساكن.",
        "production_perspective_ar": "في التطبيقات المصرفية، يتم استخدام الـ Explicit Intents حصرياً للتنقل الداخلي مع تشفير الـ Extras الحساسة أو تمرير مجرد معرفات خفيفة. في الـ PendingIntents الخاصة بالإشعارات والمصادقة، يُلزم الفريق باستخدام `FLAG_IMMUTABLE` منعاً للاختراق، ولا يُسمح بـ `FLAG_MUTABLE` إلا لخاصية الرد المباشر في المحادثات. يتم كتابة اختبارات آلية تتحقق من تطابق أعلام الـ PendingIntent ومطابقة الـ Target Activities.",
        "how_to_answer_ar": "- **السبب المعماري:** وضح أن الـ Intent رسالة تنفيذ فورية والـ PendingIntent توكن تفويض مستقبلي لنظام خارجي.\n- **طريقة الشرح:** فرّق بين الـ Explicit (توجيه مباشر لكلاس) والـ Implicit (توجيه عبر مرشحات النظام).\n- **المفاضلات والأمان:** اشرح ثغرات الـ Intent Hijacking وسبب إلزامية `FLAG_IMMUTABLE` في أندرويد 12.\n- **أنماط الفشل:** اذكر `ActivityNotFoundException` واستغلال التوكنات القابلة للتعديل.\n- **الحل العملي:** استعرض كود إنشاء إشعار بـ PendingIntent مؤمن صراحة.",
        "talking_points_ar": "ناقش دور `ActivityTaskManagerService` في مطابقة الـ IntentFilters، وعقد واجهة `IIntentSender` في `system_server`، وكيف يحتفظ النظام بـ `PendingIntentRecord` بالـ UID الخاص بالتطبيق الأصلي، وآليات الحماية ضد هجمات Intent Redirection (CWE-927)، وضوابط استخدام `Intent.createChooser` في مشاركة المحتوى.",
        "follow_ups_ar": "- **المحاور:** \"ماذا تفعل راية FLAG_UPDATE_CURRENT في الـ PendingIntent؟\"\n  **المرشح:** \"لو في PendingIntent بنفس الـ RequestCode والـ Intent مسجل بالفعل في الـ system_server، الراية دي بتخليه يحتفظ بالـ PendingIntent القائم بس يحدث الـ Extras بتاعته بأحدث بيانات، وده مهم جداً في الإشعارات علشان تفتح تفاصيل أحدث رسالة مش أول رسالة اتبعتت.\"\n\n- **المحاور:** \"إيه اللي يحصل لو شغلت Implicit Intent ومفيش أي تطبيق في الجهاز يدعمه؟\"\n  **المرشح:** \"التطبيق هيعمل كراش فوري بـ `ActivityNotFoundException`. علشان كده في كود الإنتاج لازم نفحص قبلها إن في تطبيق هيستقبل الـ Intent عن طريق `intent.resolveActivity(packageManager) != null` أو نغلف الاستدعاء بـ try/catch، أو نستخدم Android 11+ Package Visibility Queries في الـ Manifest.\"\n\n- **المحاور:** \"إيه الفرق الأمني بين FLAG_IMMUTABLE و FLAG_MUTABLE؟\"\n  **المرشح:** \"الـ FLAG_IMMUTABLE بيمنع أي تطبيق خارجي يستلم الـ PendingIntent إنه يعدل على الـ Intent الداخلي أو يحقن جواه Extras جديدة. أما FLAG_MUTABLE فبيسمح للعملية التانية بتعديل الـ Intent، وده بنحتاجه فقط في حالات محددة زي الـ RemoteInput في الإشعارات لكتابة الرد المباشر.\"",
        "self_check_ar": "فرّق بين الـ Explicit والـ Implicit Intent؛ اشرح طبيعة الـ PendingIntent كتوكن أمان؛ بيّن المخاطر الأمنية لـ Mutable PendingIntent؛ وحدد متى تستخدم `FLAG_UPDATE_CURRENT`.",
        "references_ar": f"- [Intents and Intent Filters](https://developer.android.com/guide/components/intents-filters) — مفاهيم الرسائل والمرشحات في النظام.\n- [PendingIntent security in Android 12](https://developer.android.com/about/versions/12/behavior-changes-12#pending-intent-mutability) — متطلبات الأمان وإلزامية الثبات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ Intent هو رسالة بتطلب تنفيذ عملية: الـ Explicit بيحدد كلاس المكون المستهدف بالاسم، والـ Implicit بيحدد أكشن عام والنظام بيشوف التطبيقات اللي تدعمه. أما الـ PendingIntent فهو تصريح أمني بتديه لنظام خارجي زي الإشعارات علشان ينفذ Intent معين بهوية وصلاحيات تطبيقك حتى لو التطبيق مقفول.",
        "best_answer_ar": "الـ Intent في أندرويد هو وسيلة التواصل والرسائل بين المكونات، والـ PendingIntent هو تفويض أمني مستقبلي.\n\nالـ Intent بنقسمه لنوعين رئيسيين:\nالـ Explicit Intent: بنحدد فيه الكلاس المستهدف مباشرة بالاسم زي فتح ProfileActivity من جوه التطبيق، وده توجيه مباشر وآمن وسريع.\nالـ Implicit Intent: بنطلب فيه أكشن معين زي فتح رابط موقع ACTION_VIEW أو إرسال صورة ACTION_SEND، والنظام بيدور في كل التطبيقات اللي معرفة Intent Filter للأكشن ده ويخير المستخدم بينهم.\n\nأما الـ PendingIntent فهو كائن مختلف تماماً؛ ده عبارة عن Token أمني بنديه لعملية خارجية زي الـ NotificationManager أو الـ AlarmManager، وبنقول للنظام: شغل الـ Intent ده في المستقبل بالصلاحيات والـ UID بتاع تطبيقي حتى لو تطبيقي كان مقفول تماماً في اللحظة دي.\n\nمن أول أندرويد 12، بقى إلزامي نحدد FLAG_IMMUTABLE أو FLAG_MUTABLE مع كل PendingIntent لمنع ثغرات اختطاف الرسائل وتعديلها من تطبيقات خبيثة.",
        "deep_answer_ar": "على مستوى الـ OS Kernel والـ IPC، الـ Intent بيترجم لـ Binder Transaction بتوصل لـ ActivityTaskManagerService في الـ system_server. في حالة الـ Explicit Intent، النظام بيجيب الـ ComponentInfo المستهدف فوراً من الـ Package Manager بدون أي غموض. أما في الـ Implicit Intent، فالنظام بيشغل خوارزمية Intent Resolution بتبحث في جداول الـ IntentResolver الداخلية وتطابق الـ Action والـ Category والـ Data MIME Type مع كل الـ Manifests المتسجلة في النظام مع مراعاة قيود الـ Package Visibility في أندرويد 11.\n\nبنية الـ PendingIntent مختلفة تماماً في النظام؛ إنت مش بتبعت كائن للعملية التانية، إنت بتسجل واجهة IPC اسمها IIntentSender في الـ system_server. سيرفر النظام بيعمل سجل PendingIntentRecord وبيسجل جواه الـ Linux UID الأصلي بتاع تطبيقك وصلاحياته المعرفة في النواة. فلما الإشعار يشتغل في المستقبل، السيرفر بينفذ الـ Intent منسوباً للـ UID بتاعك إنت مش لـ UID مستلم التوكن حتى لو كانت عملية تطبيقك اتقتلت بالكامل في الخلفية.\n\nوده تاريخياً كان ثغرة أمنية شهيرة اسمها Intent Hijacking (CWE-927)؛ لو الـ PendingIntent كان Mutable، تطبيق خبيث على الجهاز ممكن يعيد توجيه الـ Intent لشاشات داخلية غير مصرح بيها مسربة بيانات حساسة للعميل. علشان كده أندرويد 12 فرض FLAG_IMMUTABLE كمعيار إجباري لقفل مساحة الهجوم دي تماماً، ولا نسمح بـ FLAG_MUTABLE إلا لخاصية الـ Inline Replies عبر RemoteInput مع تقييد الـ Component صراحة."
    }

    # =========================================================================
    # AND-11: What is the role of AndroidManifest.xml?
    # =========================================================================
    qid = "AND-11"
    concept_en = """The AndroidManifest.xml file is the foundational declarative contract established between an application and the Android operating system, package installation managers, build toolchains, and distribution marketplaces such as Google Play. Rather than serving as a dynamic runtime configuration file, the manifest serves as the static blueprint declaring an application's structural identity, security perimeters, component boundaries, and hardware prerequisites.

The primary architectural responsibilities of the manifest include:
1. Component Declarations and Entry Points:
Every concrete Activity, Service, and ContentProvider must be declared in the manifest; undeclared Activities or Services cannot be launched by the system. While BroadcastReceivers can be registered dynamically at runtime, manifest-declared receivers serve as static, persistent listeners for allowed system broadcasts.
2. Inter-Component Routing and Export Boundaries:
Through `<intent-filter>` declarations, the manifest specifies the exact actions, categories, and data schemes a component accepts. The mandatory `android:exported` attribute explicitly determines whether a component is accessible to external processes or strictly private to the application.
3. Security Permissions and Governance:
Declares application permission requests via `<uses-permission>` tags, defining the maximum security privileges the app can request. It can also enforce custom permissions guarding component entry points (`android:permission`), configure network security trust anchors via `android:networkSecurityConfig`, and define backup flags.
4. Hardware and Software Compatibility:
Uses `<uses-feature>` and `<supports-screens>` to describe camera requirements, telephony sensors, or OpenGL ES versions, allowing distribution platforms to filter incompatible devices prior to installation."""

    walkthrough_en = """Production manifest declaration demonstrating component isolation, export boundaries, and network policy:
```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Declare dangerous and normal system permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <!-- Restrict store distribution to devices with camera hardware -->
    <uses-feature android:name="android.hardware.camera" android:required="false" />

    <application
        android:name=".MainApplication"
        android:allowBackup="false"
        android:networkSecurityConfig="@xml/network_security_config"
        android:theme="@style/Theme.EnterpriseApp">

        <!-- Exported Deep-Link entry point with strict Intent Filter -->
        <activity
            android:name=".ui.DeepLinkActivity"
            android:exported="true">
            <intent-filter android:autoVerify="true">
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="https" android:host="app.example.com" />
            </intent-filter>
        </activity>

        <!-- Private internal Activity protected from external access -->
        <activity
            android:name=".ui.SettingsActivity"
            android:exported="false" />

    </application>
</manifest>
```
Failure scenario:
If an internal screen containing sensitive user data omits `android:exported="false"` while declaring an intent-filter on Android 11 or older, any third-party malware on the device can launch the Activity directly, bypassing authentication gates."""

    short_en = """The AndroidManifest.xml file is the application's root declarative contract with the Android OS, defining its architectural components, export boundaries, system permissions, hardware prerequisites, and security policies. It informs the package manager during APK installation how components are structured, secured, and resolved by the runtime."""

    structured_en = """To begin with, the AndroidManifest.xml file serves as the official structural contract between an application and the Android platform. It provides the operating system, build tools, and app stores with a static, non-executable blueprint of the application's boundaries, permissions, and runtime capabilities.

From an architectural standpoint, the manifest governs application component exposure. Every Activity, Service, and ContentProvider must be declared here to be executable. Crucially, through the android:exported flag and intent-filter declarations, the manifest dictates whether a component serves as an external system entry point or remains strictly private within the application sandbox.

As for boundary management, the manifest establishes the app's security perimeter. It declares required system permissions via uses-permission, defines network security policies prohibiting unencrypted cleartext traffic, and specifies hardware requirements like camera or NFC support via uses-feature to filter incompatible hardware on Google Play.

In production scenarios, developers must actively inspect the Merged Manifest. Third-party dependencies frequently inject unwanted permissions, background services, or exported components during the Gradle build merge process, requiring explicit node removal markers to maintain zero-trust security."""

    deep_senior_en = """At the operating system and package management level, the manifest is parsed during APK installation by PackageManagerService using the platform PackageParser or modern ParsingPackage engine. The system server reads the binary XML format, extracting component declarations into internal ComponentInfo registries and allocating a unique Linux User ID (UID) to the application sandbox.

During this installation phase, PackageManagerService registers intent filters into internal fast-lookup tables. If a component defines an intent-filter without explicitly declaring android:exported, Android 12 (API level 31) refuses to install the application, throwing a fatal INSTALL_PARSE_FAILED_MANIFEST_MALFORMED error. This enforcement eliminates accidental vulnerability exposures where internal activities were unintentionally made public to foreign processes.

From a build architecture perspective, the Gradle Android Gradle Plugin (AGP) executes the Manifest Merger tool before packaging the final APK. The merger resolves declarations across the main source set, build variant overlays, and every imported Android Archive (AAR) library dependency. A library can silently introduce dangerous permissions (such as ACCESS_FINE_LOCATION) or inject an exported ContentProvider used for zero-code initialization (such as WorkManager or Firebase).

Staff engineers audit the Merged Manifest artifact located in build/intermediates/merged_manifests to verify compliance. They employ tools:node="remove" attributes to purge rogue permissions or unnecessary providers, configure android:networkSecurityConfig to mandate Certificate Transparency and TLS 1.3 pinning, and set android:allowBackup="false" to prevent unauthorized ADB data extraction in financial and enterprise applications."""

    ee.update_canonical_question(qid, concept_en, walkthrough_en, structured_en, deep_senior_en, short_en)

    metadata_entries[qid] = {
        "id": qid,
        "questionAr": "ما هو دور ملف الـ AndroidManifest.xml في التطبيق؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- استيعاب الـ Manifest كعقد إشهار رسمي أمام نظام أندرويد وليس ملف إعدادات ديناميكي.\n- التمييز بين المكونات المصدّرة (`android:exported`) والمكونات الخاصة لحماية حدود التطبيق.\n- مراجعة الـ Merged Manifest واكتشاف الصلاحيات والمكونات التي تحقنها المكتبات الخارجية.",
        "why_it_matters_ar": "ملف الـ `AndroidManifest.xml` هو عقد التأسيس والهوية الرسمية للتطبيق أمام نظام تشغيل أندرويد ومتجر Google Play وأدوات البناء. من خلاله يعلن التطبيق عن مكوناته الأربعة الأساسية (Activities, Services, Receivers, Providers)، ويحدد الصلاحيات المطلوبة من النظام عبر `<uses-permission>`، وميزات العتاد المطلوبة عبر `<uses-feature>`. في أندرويد الحديث (12+)، أصبح تحديد خاصية `android:exported` إلزامياً لمنع تصدير مكونات حساسة للخارج بالخطأ. كما يلعب دوراً محورياً في تحديد سياسات الأمان مثل `networkSecurityConfig` ومنع النسخ الاحتياطي غير الآمن للبيانات.",
        "worked_example_ar": "إعلان شاشة Deep Link خارجية وتأمين شاشة الإعدادات الداخلية:\n```xml\n<manifest xmlns:android=\"http://schemas.android.com/apk/res/android\">\n    <application\n        android:name=\".App\"\n        android:allowBackup=\"false\"\n        android:networkSecurityConfig=\"@xml/network_security\">\n\n        <!-- شاشة خارجية لاستقبال الروابط -->\n        <activity\n            android:name=\".ui.DeepLinkActivity\"\n            android:exported=\"true\">\n            <intent-filter android:autoVerify=\"true\">\n                <action android:name=\"android.intent.action.VIEW\" />\n                <category android:name=\"android.intent.category.DEFAULT\" />\n                <category android:name=\"android.intent.category.BROWSABLE\" />\n                <data android:scheme=\"https\" android:host=\"pay.example.com\" />\n            </intent-filter>\n        </activity>\n\n        <!-- شاشة داخلية خاصة لا يمكن للغير فتحها -->\n        <activity\n            android:name=\".ui.AdminActivity\"\n            android:exported=\"false\" />\n    </application>\n</manifest>\n```",
        "trade_offs_ar": "تعريف الـ BroadcastReceiver في الـ Manifest يجعله يعمل حتى لو كان التطبيق مغلقاً (Static Receiver)، لكن أندرويد يقيد ذلك لتوفير البطارية، ويفضل التسجيل الديناميكي في الكود (`registerReceiver`). جعل `android:exported=\"true\"` يتيح فتح الشاشات عبر الروابط والتطبيقات الأخرى بتكلفة زيادة مساحة الهجوم الأمنية والحاجة للتحقق الصارم من المدخلات.",
        "failure_modes_ar": "نسيان تحديد `android:exported=\"false\"` في شاشة تحتوي على بيانات حساسة في تطبيقات أقدم من أندرويد 12 يسمح لتطبيقات خبيثة بفتح الشاشة مباشرة وتجاوز تسجيل الدخول. قيام مكتبة خارجية بحقن صلاحيات غير مرغوبة عبر الـ Manifest Merger دون علم الفريق يهدد خصوصية التطبيق. إغفال `networkSecurityConfig` قد يسمح بمرور ترافيك غير مشفر (Cleartext HTTP). يتم فحص الـ Merged Manifest في أندرويد ستوديو للتأكد من عدم وجود ثغرات متسللة.",
        "production_perspective_ar": "في تطبيقات الشركات الكبيرة والتطبيقات المالية، يتم تفعيل سياسة Zero-Trust على الـ Manifest؛ كل الشاشات تكون `exported=\"false\"` افتراضياً باستثناء شاشة الـ Splash والشاشات المخصصة للـ Deep Links. يتم استخدام علامة `tools:node=\"remove\"` لإلغاء أي صلاحيات أو Providers زائدة تحقنها مكتبات الإعلانات أو التحليلات، مع تعطيل `android:allowBackup` لمنع سحب قواعد البيانات عبر كابل الـ USB.",
        "how_to_answer_ar": "- **السبب المعماري:** اشرح أن الـ Manifest هو مخطط التأسيس الثابت للنظام أثناء التثبيت وليس مجرد ملف XML عادي.\n- **طريقة الشرح:** وضح المحاور الأربعة: تعريف المكونات، الصلاحيات، متطلبات العتاد، وسياسات الأمان.\n- **المفاضلات والأمان:** ركز على إلزامية `android:exported` في أندرويد 12 وكيفية عمل Manifest Merger.\n- **أنماط الفشل:** استشهد بخطر تصدير المكونات بدون حماية وحقن الصلاحيات من الـ dependencies.\n- **الحل العملي:** استعرض بنية ملف Manifest احترافي يتضمن تأمين الروابط وحظر الـ Cleartext.",
        "talking_points_ar": "ناقش دور `PackageManagerService` في فك تشفير وتثبيت الـ Manifest الثنائي، وتخصيص الـ Linux UID للتطبيق، وآلية عمل Manifest Merger وقواعد الأولوية بين Main وVariants والمكتبات، وطريقة استخدام `tools:node` للتحكم في الدمج، وأثر إعدادات `android:process` و `android:taskAffinity` على هيكل العمليات في النظام.",
        "follow_ups_ar": "- **المحاور:** \"إيه اللي بيحصل لو مكتبة خارجية ضفتها في Gradle حاطة في الـ Manifest بتاعها exported=true أو صلاحية مش عايزها؟\"\n  **المرشح:** \"أثناء البناء، أداة Manifest Merger بتدمج ملفات الـ Manifest لكل المكتبات مع الـ Manifest الرئيسي بتاعك، وبالتالي الصلاحية أو المكون المصدّر هينزل في الـ APK النهائي. علشان نمنع ده، بنستخدم `tools:node=\"remove\"` في الـ Manifest الرئيسي لحذف الصلاحية أو المكون ده صراحة.\"\n\n- **المحاور:** \"ليه أندرويد 12 خلى android:exported إلزامي لكل المكونات اللي ليها Intent Filter؟\"\n  **المرشح:** \"لأن تاريخياً كان أي مكون بيحتوي على intent-filter بيعتبر exported=true تلقائياً لو المطور محددش قيمته، وده كان بيسرب شاشات داخلية ومكونات حساسة للتطبيقات التانية بدون قصد من المطور، فجوجل ألزمت تحديده صراحة لتفادي الكوارث الأمنية دي.\"\n\n- **المحاور:** \"ما الفرق بين uses-permission و uses-feature؟\"\n  **المرشح:** \"الـ uses-permission بتطلب من نظام التشغيل صلاحية وصول لمورد محمي زي الكاميرا أو جهات الاتصال. أما uses-feature فدي متطلبات عتاد بتفهم متجر Google Play إن التطبيق محتاج مستشعر معين زي البلوتوث أو الكاميرا، وبتمنع الأجهزة اللي مفهاش العتاد ده من تحميل التطبيق.\"",
        "self_check_ar": "اشرح دور الـ Manifest أمام مدير الحزم؛ حدد معنى `android:exported` وأثره الأمني؛ بيّن كيف تؤثر المكتبات على الـ Merged Manifest؛ واشرح كيفية إلغاء صلاحية محقونة باستخدام أدوات الدمج.",
        "references_ar": f"- [App manifest overview](https://developer.android.com/guide/topics/manifest/manifest-intro) — البنية الأساسية لملف الـ Manifest.\n- [Manifest Merger](https://developer.android.com/build/manage-manifests) — قواعد دمج الـ Manifests في Gradle.\n- [Component security in Android 12](https://developer.android.com/about/versions/12/behavior-changes-12#exported-components) — معايير الأمان الإلزامية للمكونات المصدّرة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "ملف الـ AndroidManifest.xml هو وثيقة التأسيس والعقد الرسمي بين التطبيق ونظام تشغيل أندرويد، بيعرف مكونات النظام الأربعة الأساسية ونقاط الدخول، والصلاحيات المطلوبة، ومتطلبات العتاد لمتجر Google Play، وسياسات الأمان والحماية زي الـ networkSecurityConfig والـ exported status للمكونات المختلفة.",
        "best_answer_ar": "ملف الـ AndroidManifest.xml مش مجرد ملف إعدادات عادي، ده وثيقة التعريف الرسمية وعقد التأسيس اللي نظام أندرويد بيقرأه وقت تثبيت التطبيق على الجهاز.\n\nمن الناحية المعمارية، الـ Manifest بيلعب أربع أدوار رئيسية:\nأولاً، إشهار المكونات: مفيش Activity أو Service أو ContentProvider يقدر يشتغل في أندرويد إلا لو متسجل جواه، وهو اللي بيحدد هل المكون ده خاص بالتطبيق الداخلي ولا متاح للتطبيقات التانية عن طريق خاصية android:exported.\n\nثانياً، حدود الأمان والصلاحيات: بنحدد فيه الـ permissions اللي التطبيق محتاجها من النظام، وسياسات تأمين الشبكة زي حظر الـ Cleartext HTTP عبر networkSecurityConfig.\n\nثالثاً، متطلبات العتاد لـ Google Play: عن طريق uses-feature بنحدد إذا كان التطبيق محتاج كاميرا أو حساسات معينة، فالمتجر يمنع نزوله على أجهزة غير مدعومة.\n\nرابعاً، نقطة الدمج في أداة الـ Manifest Merger في Gradle اللي بتجمع ملفات كل المكتبات الخارجية في ملف نهائي واحد.",
        "deep_answer_ar": "على مستوى الـ OS Kernel والـ Package Management، الـ Manifest بيتعمله Parse بواسطة PackageManagerService في الـ system_server وقت تثبيت ملف الـ APK. النظام بيفك ضغط الـ Binary XML وبيسجل كل المكونات في جداول داخلية اسمها ComponentInfo، وبيعين للتطبيق Linux UID منفصل بيبني عليه الـ Sandbox الأمني ونطاقات عزل العمليات في النواة.\n\nلو في أي مكون متعرف جواه intent-filter من غير ما يتحدد صراحة android:exported في أندرويد 12 فما فوق، الـ Package Manager بيرفض تثبيت التطبيق فوراً بخطأ INSTALL_PARSE_FAILED_MANIFEST_MALFORMED. وده قرار أمني صارم لمنع الثغرات اللي كانت بتنتج عن جعل المكونات public افتراضياً في الإصدارات القديمة وتسمح للمخترقين بتجاوز بوابات المصادقة.\n\nمن منظور هندسة البناء، أداة Manifest Merger في الـ AGP بتدمج الـ Manifest بتاع الـ main code مع الـ flavors ومع كل مكتبة AAR مضافة للمشروع. وهنا بتظهر خطورة بالغة؛ مكتبة تتبع أو إعلانات خارجية ممكن تحقن صلاحيات حساسة زي الموقع الدقيق أو تحقن ContentProvider شغال على الفاضي لمجرد الـ auto-init وتأخير إقلاع التطبيق.\n\nالـ Staff Engineer بيراجع ملف Merged Manifest النهائي الناتج في مجلد البناء، وبيستخدم أدوات التحكم في الدمج زي tools:node=\"remove\" لحذف أي صلاحيات غير متوافقة مع سياسة الخصوصية، وبيقفل android:allowBackup لحماية قواعد البيانات المشفرة من الاستخراج اليدوي عبر الـ adb."
    }

    # =========================================================================
    # AND-12: How do you restore a screen after process death without losing user input?
    # =========================================================================
    qid = "AND-12"
    concept_en = """Restoring a screen after background process death without losing user input represents a cornerstone of robust Android application engineering. Because the operating system can terminate an idle process at any moment under memory pressure without executing onDestroy(), applications must establish a deliberate architectural strategy separating ephemeral view rendering from durable user input and transaction identity.

The framework provides three complementary layers for input preservation:
1. Framework View State Serialization:
Standard Android framework views (such as EditText, CheckBox, and ScrollView) that possess unique, non-null `android:id` attributes implement View.onSaveInstanceState() internally. When the Activity is stopped, the view hierarchy automatically serializes input text, selection cursors, and scroll positions into the platform instance state Bundle, restoring them seamlessly upon layout recreation.
2. ViewModel SavedStateHandle:
In modern Jetpack MVVM and MVI architectures, UI state holders retain input drafts and query parameters inside `SavedStateHandle`. This key-value dictionary is automatically backed by the platform saved instance state Bundle. When the process is resurrected, the ViewModel retrieves these preserved values during dependency injection, allowing reactive UI state flows to rehydrate immediately.
3. Durable Debounced Persistence (Room or DataStore):
For complex, multi-field workflows (such as loan applications, long-form reviews, or ecommerce checkouts), relying solely on the in-memory Bundle is insufficient. Best-in-class architectures stream input modifications through a debounced coroutine pipeline directly into a local SQLite Room database. This guarantees that user progress survives not only process death, but also explicit app dismissals, battery depletion, and device reboots."""

    walkthrough_en = """Production implementation of a resilient form surviving process death via SavedStateHandle and local persistence:
```kotlin
class FormViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val draftRepository: FormDraftRepository
) : ViewModel() {

    // 1. Restore input draft from SavedStateHandle or initialize empty
    val formInput: StateFlow<String> = savedStateHandle.getStateFlow("input_text", "")

    fun onInputChanged(newText: String) {
        // 2. Immediately update SavedStateHandle for instant process death recovery
        savedStateHandle["input_text"] = newText

        // 3. Debounce and write to persistent storage for reboot durability
        viewModelScope.launch {
            draftRepository.saveDraft(newText)
        }
    }
}
```
Verification procedure:
1. Launch the form screen and enter text into the input field.
2. Background the application using the device Home button.
3. Execute `adb shell am kill com.example.myapp` in the terminal to trigger immediate process death.
4. Reopen the application from the Recent Apps list.
5. The Android system creates a new process and restores the form screen; FormViewModel reads the preserved text from SavedStateHandle without data loss or user disruption."""

    short_en = """To restore a screen after process death without losing input, standard framework Views with unique IDs automatically restore their text from the instance Bundle, while ViewModels consume SavedStateHandle for draft state. For critical forms, inputs are debounced into Room, ensuring seamless restoration upon process resurrection."""

    structured_en = """To begin with, restoring a screen after process death requires separating volatile rendering state from user-authored drafts and entity identifiers. When the OS terminates an application's process in the background, all heap memory is erased, meaning standard ViewModel fields will reset unless properly bound to saved state.

From an architectural standpoint, we solve this through a layered restoration model. At the view tier, giving unique android:id attributes to standard framework views allows the Android platform to serialize input text and scroll offsets automatically via onSaveInstanceState. In Compose, rememberSaveable achieves identical UI-level persistence.

As for boundary management, at the business logic tier, the ViewModel receives a SavedStateHandle. By reading and writing form inputs and query strings into SavedStateHandle, the ViewModel ensures that when a new process is spawned, its constructor can instantly reconstitute the exact user state from the system server's cached Bundle.

In production scenarios involving extensive data entry, we augment SavedStateHandle with debounced local persistence. User input flows through a debounce operator into a local Room database. If the process is killed, the screen rehydrates from SavedStateHandle; if the device reboots, the screen reloads the durable draft from disk."""

    deep_senior_en = """At the operating system and lifecycle controller level, the preservation of user input across process termination is governed by the SavedStateRegistryController and ActivityTaskManagerService. When an Activity enters the stopped state, the framework invokes performSaveInstanceState(), recursively traversing the View hierarchy. Each View's onSaveInstanceState() returns an AbsSavedState parcelable, which is packed into a composite Bundle and transmitted across Binder IPC to system_server.

Because the Binder transaction buffer is capped at 1MB across all concurrent operations for the entire process, storing rich draft entities or attachment bitmaps directly in SavedStateHandle risks a fatal TransactionTooLargeException. Therefore, a Staff engineer restricts SavedStateHandle strictly to primitive IDs, draft text strings, and navigation indices, keeping payloads well under 50KB.

When the user returns to the application, ActivityThread receives an ActivityClientRecord containing the saved Bundle from the system server. During performCreate(), the saved Bundle is delivered to Activity.onCreate(), restoring framework views, while the SavedStateRegistry restores state to the AbstractSavedStateViewModelFactory. Hilt or custom factories inject the rehydrated SavedStateHandle into the ViewModel constructor.

To achieve enterprise-grade resilience, production architectures avoid re-executing non-idempotent network requests or side effects during restoration. The ViewModel inspects the restored state: if a submission was already inflight, it queries the backend or local database for transaction status using an idempotency key rather than repeating the POST request. This multi-tiered strategy—combining View IDs, SavedStateHandle, and debounced Room persistence—guarantees zero input loss even under aggressive Android memory pressure."""

    ee.update_canonical_question(qid, concept_en, walkthrough_en, structured_en, deep_senior_en, short_en)

    metadata_entries[qid] = {
        "id": qid,
        "questionAr": "كيف تستعيد حالة الشاشة بعد موت العملية (Process Death) دون فقدان مدخلات المستخدم؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- الفصل المعماري بين حالة الواجهة المؤقتة والمسودات التي يجب حفظها قبل قتل العملية.\n- استعادة الشاشة باستخدام معرفات بسيطة من `SavedStateHandle` والبيانات المحفوظة محلياً.\n- تفادي تكرار العمليات الحساسة (Side Effects) والطلبات الشبكية عند إعادة البناء.",
        "why_it_matters_ar": "موت العملية (Process Death) هو السيناريو الأكثر شيوعاً لفقدان مدخلات المستخدم في أندرويد؛ فعندما يخرج المستخدم للرد على مكالمة أو فتح تطبيق آخر، قد يقوم النظام بإنهاء العملية فوراً لتحرير الرام. عناصر الواجهة القياسية التي تمتلك `android:id` فريد تسترجع نصوصها تلقائياً عبر `onSaveInstanceState`. وفي معمارية MVVM الحديثة، يتم استخدام `SavedStateHandle` داخل الـ ViewModel للاحتفاظ بنصوص المسودات ومعرفات العناصر. وفي الاستمارات الطويلة أو المعاملات المالية، يتم حفظ المدخلات بشكل دوري (Debounced Autosave) في قاعدة بيانات Room المحلية لحمايتها حتى لو تم إغلاق التطبيق تماماً أو أعيد تشغيل الجهاز.",
        "worked_example_ar": "استمارة تسجيل مدعومة بـ `SavedStateHandle` وحفظ محلي ضد موت العملية:\n```kotlin\nclass RegistrationViewModel(\n    private val savedStateHandle: SavedStateHandle,\n    private val draftRepository: DraftRepository\n) : ViewModel() {\n\n    // 1. ربط حقل الإدخال بـ SavedStateHandle للاستعادة الفورية\n    val emailInput = savedStateHandle.getStateFlow(\"email\", \"\")\n\n    fun onEmailChanged(newEmail: String) {\n        savedStateHandle[\"email\"] = newEmail\n        // 2. حفظ في قاعدة البيانات المحلية بعد فترة تهدئة (Debounce)\n        viewModelScope.launch {\n            draftRepository.saveEmailDraft(newEmail)\n        }\n    }\n}\n```\nعند موت العملية واستدعاء التطبيق مجدداً، يقرأ الـ ViewModel البريد المكتوب مباشرة من `SavedStateHandle` ويعرضه في الواجهة دون أن يشعر المستخدم بأي انقطاع.",
        "trade_offs_ar": "الاعتماد على حفظ الواجهة التلقائي في الـ Views يحفظ النصوص فقط لكنه لا يحفظ الحالة المنطقية في الـ ViewModel. الـ SavedStateHandle يربط بين الاثنين لكنه مقيد بحجم الـ Binder Buffer (أقل من 50 كيلوبايت). الحفظ المستمر في Room يضمن بقاء البيانات للأبد ولكنه يتطلب عمليات I/O ومعالجة غير متزامنة لتجنب تجميد الـ UI.",
        "failure_modes_ar": "نسيان وضع `android:id` لعناصر الواجهة في XML يمنع النظام من حفظ واستعادة نصوصها. وضع كائنات ضخمة في الـ SavedState يسبب كراش `TransactionTooLargeException`. تكرار استدعاءات الـ API الحساسة (مثل عمليات الدفع) فور إعادة إحياء الشاشة قد يؤدي لتنفيذ المعاملة مرتين. يتم اختبار ذلك بأمر `adb shell am kill` والتأكد من استعادة كل الحقول بدقة.",
        "production_perspective_ar": "في استمارات التسجيل والتقديم البنكية الطويلة، يتم حفظ كل خطوة يقوم بها العميل في قاعدة بيانات Room المحلية فوراً مع وضع مؤشر للخطوة الحالية في `SavedStateHandle`. عند عودة المستخدم بعد موت العملية، تستعيد الشاشة آخر خطوة كان واقفاً عندها مع تحميل المسودة الكاملة من قاعدة البيانات، مع إظهار رسالة تفيد باستعادة البيانات بنجاح.",
        "how_to_answer_ar": "- **السبب المعماري:** وضح أن موت العملية في الخلفية أمر حتمي ويجب حماية مدخلات المستخدم استباقياً.\n- **طريقة الشرح:** استعرض الطبقات الثلاث: حفظ الـ Views التلقائي، دور `SavedStateHandle`، والحفظ الدائم في Room.\n- **المفاضلات:** بيّن الفارق بين الحفظ السريع في حزمة النظام والحفظ المستقر على القرص.\n- **أنماط الفشل:** اذكر مشكلة غياب الـ IDs وخطر `TransactionTooLargeException` وتكرار المعاملات.\n- **الحل العملي:** استشهد بكود استخدام `SavedStateHandle` مع الحفظ المؤجل في قاعدة البيانات.",
        "talking_points_ar": "ناقش دور `SavedStateRegistryController` في تجميع حزم الـ Bundle ونقلها عبر Binder IPC لـ `system_server`، وكيفية ربط `AbstractSavedStateViewModelFactory` بـ `SavedStateHandle`، واستراتيجيات الحفظ غير المتزامن باستخدام Coroutines مع Debounce، وكيفية ضمان Idempotency عند استعادة المعاملات المالية.",
        "follow_ups_ar": "- **المحاور:** \"ليه حقول EditText بتفقد نصوصها بعد موت العملية أحياناً رغم إنها عناصر أندرويد قياسية؟\"\n  **المرشح:** \"السبب الأكثر شيوعاً هو نسيان تحديد `android:id` فريد للعنصر في ملف الـ XML. نظام أندرويد بيتجاهل حفظ واستعادة حالة أي View ملوش ID محدد، أو لو الـ View تم توليده ديناميكياً بدون الحفاظ على نفس الـ ID عبر مرات إعادة الإنشاء.\"\n\n- **المحاور:** \"إزاي نضمن عدم تكرار طلب الشبكة (Duplicate Request) لو التطبيق مات وهو بيبعت طلب تسجيل؟\"\n  **المرشح:** \"بنعتمد على معمارية قائمة على Idempotency Keys؛ بنولد UUID فريد للمعاملة وبنحفظه في قاعدة البيانات المحلية وSavedStateHandle قبل إرسال الطلب. ولما الشاشة ترجع بعد موت العملية، بنستعلم الأول من السيرفر بمعرف المعاملة لمعرفة حالتها قبل ما نقرر نبعت الطلب تاني.\"\n\n- **المحاور:** \"ما الفرق في استعادة الحالة بين الـ Views التقليدية وبين Jetpack Compose؟\"\n  **المرشح:** \"في الـ Views التقليدية النظام بيعتمد على View.onSaveInstanceState، أما في Jetpack Compose فبنستخدم دالة `rememberSaveable` اللي بتسجل حالة الـ Composable في الـ SaveableStateRegistry وبتتحفظ داخلياً في نفس الـ Bundle بتاع الـ Activity.\"",
        "self_check_ar": "اشرح دور `android:id` في حفظ مدخلات الـ Views؛ بيّن كيفية استخدام `SavedStateHandle` لحفظ المسودات؛ صمم استراتيجية حفظ محلي غير متزامن؛ واشرح كيفية تفادي تكرار المعاملات بعد الاستعادة.",
        "references_ar": f"- [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) — استراتيجيات حفظ حالات واجهة المستخدم.\n- [ViewModel SavedState](https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate) — إدارة الـ SavedState داخل الـ ViewModel.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "علشان نستعيد الشاشة بعد موت العملية بدون فقدان المدخلات، بنعتمد على الـ android:id في الـ Views لاستعادة النصوص تلقائياً، وبنربط مدخلات الـ ViewModel بـ SavedStateHandle لحفظ المسودات عبر حزمة النظام، وبنحفظ الاستمارات الطويلة دورياً في قاعدة بيانات Room المحلية لضمان بقائها حتى لو قفل الموبايل.",
        "best_answer_ar": "استعادة مدخلات المستخدم بعد الـ Process Death هي مقياس احترافية مهندس الأندرويد، لأن المستخدم ملوش ذنب إن النظام قفل التطبيق في الخلفية علشان يوفر رام.\n\nبنحل المشكلة دي بمعمارية ثلاثية الطبقات:\nأول طبقة على مستوى الـ UI: عناصر الواجهة القياسية زي الـ EditText بتسترجع نصوصها ومكان مؤشر الكتابة تلقائياً عبر onSaveInstanceState بشرط أساسي إن يكون ليها android:id فريد في الـ XML، وفي Compose بنستخدم rememberSaveable لنفس الغرض.\n\nتاني طبقة على مستوى الـ ViewModel: بنحقن SavedStateHandle ونربط بيه نصوص المسودات ومعرفات العناصر؛ ولما العملية تموت والنظام ينشئ عملية جديدة، الـ ViewModel بيقرأ البيانات المحفوظة من حزمة الـ Bundle فوراً ويعرضها في الشاشة.\n\nتالت طبقة على مستوى البيانات الدائمة: في الشاشات الكبيرة والمعاملات البنكية، مينفعش نعتمد على الـ Bundle بس؛ بنعمل Debounced Autosave يحفظ المدخلات في قاعدة بيانات Room في الخلفية أول بأول، بحيث لو التطبيق اتقفل تماماً أو الموبايل فصل شحن، المستخدم يفتح يلاقي مسودته مستنياه.\n\nوالأهم من ده كله إننا مبنكررش أي طلب شبكة حساس بشكل أعمى وقت الاستعادة، وبنتأكد الأول من حالة المعاملة عبر معرف فريد Idempotency Key.",
        "deep_answer_ar": "على مستوى الـ OS Lifecycle، استعادة المدخلات بتدار عبر SavedStateRegistryController و ActivityTaskManagerService. لما الـ Activity تدخل حالة onStop، النظام بيستدعي performSaveInstanceState اللي بتمر تكرارياً على شجرة الـ Views، وكل View بينفذ onSaveInstanceState وبيرجع كائن AbsSavedState بيتجمع جوه Bundle واحدة بتتنقل عبر Binder IPC لذاكرة الـ system_server لحمايتها من الموت المفاجئ.\n\nالمشكلة إن مساحة الـ Binder Buffer محددة بـ 1 ميجابايت على مستوى الـ Process كله لكل العمليات المتزامنة؛ فعلشان نتفادى كراش TransactionTooLargeException، الـ Staff Engineer بيقيد SavedStateHandle في حدود المعرفات والـ Strings البسيطة فقط تحت 50 كيلوبايت ومبيحطش فيها أي صور أو كائنات ضخمة نهائياً.\n\nلما العملية ترجع تشتغل بعد القتل، الـ ActivityThread بيستلم الـ ActivityClientRecord ومعه الـ Bundle المحفوظة، وبيمررها لـ performCreate. الـ SavedStateRegistry بيبعت البيانات لـ AbstractSavedStateViewModelFactory علشان يحقن SavedStateHandle جاهزة في الـ ViewModel constructor فوراً قبل بدء رندرة الواجهة.\n\nمعمارياً، بنبني تدفق استعادة آمن تماماً: الـ ViewModel بيبص على الحالة المسترجعة؛ لو كان في عملية إرسال شغالة وقت القتل، مبنبعتش POST request تاني علشان منخصمش مرتين، إحنا بنستعلم عن حالة العملية عبر UUID فريد كنا حفظناه مسبقاً في Room. بكده بنجمع بين استعادة الواجهة اللحظية من الـ Bundle، وحماية البيانات الدائمة في القرص، وتأمين المعاملات المالية ضد التكرار بأعلى موثوقية إنتاجية."
    }

    # =========================================================================
    # AND-13: How do you handle runtime permissions and denial/permanent denial?
    # =========================================================================
    qid = "AND-13"
    concept_en = """The Android runtime permission model, introduced in Android 6.0 (API level 23) and continuously refined in recent platform releases, requires applications to request dangerous permissions at runtime rather than relying solely on install-time grants. Dangerous permissions guard user privacy and sensitive hardware access, including camera, microphone, precise location, contacts, and media storage.

Handling runtime permissions requires orchestrating four distinct permission states:
1. Already Granted:
Verified via `ContextCompat.checkSelfPermission()`. If granted, the application executes the feature workflow immediately.
2. Initial State / Not Yet Requested:
The permission has never been presented to the user. The application can trigger the system permission prompt directly.
3. Denied (Temporary Denial):
The user tapped Deny once. When the feature is re-triggered, `ActivityCompat.shouldShowRequestPermissionRationale()` returns true. The application must display an educational rationale dialog explaining why the capability is needed for the requested feature, before launching the system prompt again.
4. Permanently Denied ("Don't Ask Again"):
The user denied the permission twice or explicitly checked 'Don't ask again'. In this terminal state, `shouldShowRequestPermissionRationale()` returns false after denial, and the system prompt will no longer appear. The application must gracefully disable the dependent feature and present an informative dialog offering to navigate the user to the application's system settings screen (`Settings.ACTION_APPLICATION_DETAILS_SETTINGS`).

Modern architectures strictly manage permissions via the AndroidX Activity Result API (`ActivityResultContracts.RequestPermission()`), registering typed callback launchers unconditionally during Activity or Fragment initialization."""

    walkthrough_en = """Comprehensive implementation of runtime permission handling using the Activity Result API and rationale routing:
```kotlin
class CameraFeatureActivity : AppCompatActivity() {

    // 1. Unconditionally register the permission launcher during initialization
    private val requestCameraLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            launchCameraHardware()
        } else {
            handlePermissionDenial()
        }
    }

    fun onCaptureButtonClicked() {
        when {
            ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED -> {
                launchCameraHardware()
            }
            ActivityCompat.shouldShowRequestPermissionRationale(this, Manifest.permission.CAMERA) -> {
                showRationaleDialog {
                    requestCameraLauncher.launch(Manifest.permission.CAMERA)
                }
            }
            else -> {
                // First-time request or permanently denied
                requestCameraLauncher.launch(Manifest.permission.CAMERA)
            }
        }
    }

    private fun handlePermissionDenial() {
        if (!ActivityCompat.shouldShowRequestPermissionRationale(this, Manifest.permission.CAMERA)) {
            // Permanently denied: guide user to system settings
            showSettingsRedirectDialog()
        } else {
            // Temporary denial: feature disabled with explanation
            showFeatureDisabledBanner()
        }
    }

    private fun showSettingsRedirectDialog() {
        AlertDialog.Builder(this)
            .setTitle("Camera Permission Required")
            .setMessage("Camera access was permanently disabled. Please enable it in Settings to take photos.")
            .setPositiveButton("Open Settings") { _, _ ->
                val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                    data = Uri.fromParts("package", packageName, null)
                }
                startActivity(intent)
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}
```"""

    short_en = """Runtime permissions must be requested contextually at the point of need using the Activity Result API. If granted, execute the feature; if denied, evaluate shouldShowRequestPermissionRationale to display an educational explanation; if permanently denied, inform the user and direct them to App Settings."""

    structured_en = """To begin with, Android's runtime permission model requires applications to request sensitive capabilities—such as camera, location, and audio recording—in context at the moment of use, rather than requesting blanket access during installation.

From an architectural standpoint, an application must gracefully manage three core user responses: permission grant, temporary denial, and permanent denial. When access is granted, the feature proceeds immediately. If the user denies the request, the platform's shouldShowRequestPermissionRationale API evaluates whether we should present an educational dialog explaining the concrete functional value of the permission before re-requesting it.

As for boundary management, when a user repeatedly denies a permission or selects 'Don't ask again', the operating system suppresses future system permission dialogs. In this permanent denial state, shouldShowRequestPermissionRationale returns false. Our architectural responsibility is to avoid trapping the user in a broken loop; instead, we offer a clear prompt redirecting them to the application's system settings page via Settings.ACTION_APPLICATION_DETAILS_SETTINGS.

In production scenarios, we execute permission workflows through the AndroidX Activity Result API using ActivityResultContracts.RequestPermission. Registering this launcher during initialization guarantees that permission results survive Activity recreation and background process suspension without callback loss."""

    deep_senior_en = """At the operating system and Linux kernel level, runtime permissions are governed by the PermissionManagerService and AppOpsManager running inside system_server. When an application is granted a dangerous permission, the framework dynamically maps the application's Linux User ID (UID) to underlying kernel supplementary groups (GIDs), adjusting file system sandboxes and hardware device driver nodes (such as /dev/video for camera hardware).

The state machine driving shouldShowRequestPermissionRationale() is nuanced and platform-dependent. In the system server's permission database, each permission grant record maintains bitwise flags: USER_SET, USER_FIXED, and POLICY_FIXED. Prior to the initial request, the rationale method returns false. Following a single user denial, the USER_SET flag is applied, causing shouldShowRequestPermissionRationale() to return true. If the user selects 'Don't ask again' or denies the prompt a second time on Android 11+, the USER_FIXED flag is set. Once USER_FIXED is active, the system server immediately rejects future requestPermissions() IPC transactions without showing a prompt, and shouldShowRequestPermissionRationale() permanently returns false.

Modern Android versions introduce additional privacy boundaries: Android 11 added one-time permissions ('Only this time'), where grants expire as soon as the process terminates. Android 12 introduced approximate versus precise location, Android 13 introduced runtime notification permissions, and Android 14 added partial photo access.

Staff engineers structure permission architectures so that core business logic never assumes permanent grants. Features must verify permissions prior to every hardware invocation, provide graceful functional degradation when access is withheld, and implement clean fallback pathways when users return from the system settings screen via onResume() observation."""

    ee.update_canonical_question(qid, concept_en, walkthrough_en, structured_en, deep_senior_en, short_en)

    metadata_entries[qid] = {
        "id": qid,
        "questionAr": "كيف تتعامل مع صلاحيات التشغيل (Runtime Permissions) وحالات الرفض والرفض الدائم؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- طلب الصلاحيات الحساسة في وقت الحاجة الفعلي (Just-in-Time) وليس عند فتح التطبيق.\n- فهم الحالات الأربع لدورة حياة الصلاحية والتعامل السليم مع `shouldShowRequestPermissionRationale`.\n- التعامل الاحترافي مع الرفض الدائم وتوجيه المستخدم لإعدادات التطبيق دون محاصرة الواجهة.",
        "why_it_matters_ar": "نظام صلاحيات التشغيل (Runtime Permissions) الذي بدأ من أندرويد 6.0 وتطور في أندرويد 11 و 13 و 14 صُمم لحماية خصوصية المستخدم ومنع الوصول للعتاد الحساس مثل الكاميرا والموقع الجغرافي والإشعارات بدون موافقة صريحة. التعامل السليم يتطلب طلب الصلاحية في لحظة حاجة المستخدم للميزة (Contextual Request). في حالة الرفض لأول مرة، يجب إظهار حوار توضيحي (Rationale Dialog) يشرح فائدة الصلاحية للمستخدم. وفي حالة الرفض الدائم (Permanent Denial)، يتوقف النظام عن إظهار حوار الصلاحيات تماماً، ويصبح الخيار الوحيد هو توجيه المستخدم لصفحة إعدادات التطبيق عبر `Settings.ACTION_APPLICATION_DETAILS_SETTINGS`. استخدام Activity Result API هو المعيار الحديث لتفادي مشاكل دورة الحياة.",
        "worked_example_ar": "معالجة صلاحية الكاميرا باستخدام Activity Result API وحالات الرفض:\n```kotlin\nclass CameraActivity : AppCompatActivity() {\n    private val requestCameraLauncher = registerForActivityResult(\n        ActivityResultContracts.RequestPermission()\n    ) { isGranted ->\n        if (isGranted) {\n            openCamera()\n        } else if (!ActivityCompat.shouldShowRequestPermissionRationale(this, Manifest.permission.CAMERA)) {\n            // رفض دائم: توجيه لإعدادات النظام\n            showSettingsDialog()\n        } else {\n            // رفض مؤقت: توضيح سبب الاحتياج\n            showRationaleDialog()\n        }\n    }\n\n    private fun showSettingsDialog() {\n        AlertDialog.Builder(this)\n            .setTitle(\"مطلوب صلاحية الكاميرا\")\n            .setMessage(\"تم تعطيل الصلاحية بشكل دائم، يرجى تفعيلها من إعدادات التطبيق للمتابعة.\")\n            .setPositiveButton(\"فتح الإعدادات\") { _, _ ->\n                val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {\n                    data = Uri.fromParts(\"package\", packageName, null)\n                }\n                startActivity(intent)\n            }\n            .setNegativeButton(\"إلغاء\", null)\n            .show()\n    }\n}\n```",
        "trade_offs_ar": "طلب الصلاحية دفعة واحدة عند أول فتح للتطبيق يسهل البرمجة لكنه يرفع معدل الرفض وحذف التطبيق بشكل كبير. في المقابل، طلب الصلاحية لحظياً (Just-in-Time) يحسن معدل قبول المستخدم لكنه يتطلب معالجة برمجية لكل شاشة على حدة. إرسال المستخدم للإعدادات حل فعال للرفض الدائم لكنه يخرجه من سياق التطبيق ويتطلب فحص الصلاحية مجدداً عند الرجوع في `onResume`.",
        "failure_modes_ar": "طلب الصلاحية بدون فحص مسبق أو استدعاء `requestPermissions` المتكرر بعد الرفض الدائم يؤدي لتجاهل النظام للطلب وصمت الواجهة دون استجابة. عدم فحص الصلاحية قبل كل استخدام مباشر للعتاد يسبب كراش فوري بـ `SecurityException`. إهمال الصلاحيات المؤقتة (One-time permissions) التي تنتهي بمجرد خروج التطبيق من الواجهة في أندرويد 11. يتم فحص المسار بمحاكاة حالات الرفض وإلغاء الصلاحيات من الإعدادات أثناء تشغيل التطبيق.",
        "production_perspective_ar": "في تطبيقات التوصيل والخدمات، يتم توفير مسار بديل دائماً عند رفض الصلاحيات؛ فإذا رفض المستخدم صلاحية الـ GPS، يتم فتح خريطة يدوية للبحث عن العنوان بالاسم بدلاً من قفل التطبيق في وجهه. يتم تسجيل نسب قبول ورفض الصلاحيات في التحليلات لمعرفة الشاشات التي تسبب نفور المستخدم وتحسين نصوص الـ Rationale التوضيحية.",
        "how_to_answer_ar": "- **السبب المعماري:** وضح فلسفة أندرويد في حماية الخصوصية وطلب الصلاحيات لحظياً.\n- **طريقة الشرح:** فصّل الحالات الأربع: ممنوحة مسبقاً، لم تُطلب بعد، مرفوضة مؤقتاً، ومرفوضة نهائياً.\n- **المفاضلات وسلوك النظام:** اشرح آلية عمل `shouldShowRequestPermissionRationale` وتغير حالاتها.\n- **أنماط الفشل:** حذر من كراش `SecurityException` ومصيدة تكرار الطلب في الرفض الدائم.\n- **الحل العملي:** استعرض كود Activity Result API والتوجيه لـ `ACTION_APPLICATION_DETAILS_SETTINGS`.",
        "talking_points_ar": "ناقش دور `PermissionManagerService` و `AppOpsManager` في الـ system_server، وتعيين أعلام `USER_SET` و `USER_FIXED` في قاعدة بيانات الصلاحيات، والتطورات الحديثة مثل الصلاحيات لمرة واحدة في أندرويد 11، وصلاحيات الموقع التقريبي في أندرويد 12، وصلاحية الإشعارات في أندرويد 13، والصلاحيات الجزئية للصور في أندرويد 14.",
        "follow_ups_ar": "- **المحاور:** \"إزاي دالة shouldShowRequestPermissionRationale بتشتغل بالتفصيل؟\"\n  **المرشح:** \"قبل ما تطلب الصلاحية لأول مرة بترجع false. لو المستخدم رفض الصلاحية مرة واحدة بترجع true، وهنا المفروض تظهر حوار توضيحي (Rationale) للمستخدم قبل ما تطلبها تاني. لو المستخدم داس 'Don't ask again' أو رفضها مرتين ورا بعض في أندرويد الحديث، الدالة بترجع false تاني، وده معناه إننا دخلنا في حالة الرفض الدائم ولازم نوجهه للإعدادات يدوي.\"\n\n- **المحاور:** \"ليه بنستخدم Activity Result API بدل onRequestPermissionsResult القديمة؟\"\n  **المرشح:** \"لأن الطريقة القديمة كانت بتعتمد على Request Codes رقمية وبتجبرك تكتب كل منطق النتيجة جوه Activity واحدة وده بيعمل تداخل وفوضى في المشاريع الكبيرة، والأخطر إن لو الشاشة اتدمرت وأعيد إنشاؤها أثناء طلب الصلاحية كانت النتيجة بتضيع، بينما Activity Result API منفصلة ونوعية وآمنة عبر دورة الحياة.\"\n\n- **المحاور:** \"ما هي الصلاحيات المؤقتة (One-time permissions) في أندرويد 11 فما فوق؟\"\n  **المرشح:** \"دي ميزة بتسمح للمستخدم يمنح الصلاحية لخيار 'Only this time' (المرة دي فقط). الصلاحية بتفضل صالحة طالما التطبيق في الواجهة، وبمجرد ما المستخدم يقفل التطبيق أو يدخل الخلفية لفترة، النظام بيسحب الصلاحية تلقائياً، علشان كده لازم نفحص الصلاحية برمجياً قبل كل استخدام للعتاد.\"",
        "self_check_ar": "حدد الحالات الأربع للصلاحيات؛ اشرح مخرجات `shouldShowRequestPermissionRationale` في كل مرحلة؛ صمم كود التعامل مع الرفض الدائم؛ وبيّن كيفية التعامل مع صلاحيات أندرويد 11 و 13 الحديثة.",
        "references_ar": f"- [Request runtime permissions](https://developer.android.com/training/permissions/requesting) — الدليل الرسمي لطلب الصلاحيات وإدارة الـ Rationale.\n- [Permissions overview](https://developer.android.com/guide/topics/permissions/overview) — تصنيف الصلاحيات وطبقات الأمان في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "صلاحيات التشغيل بتنطلب لحظياً في وقت الحاجة عبر Activity Result API: لو اتوافقت بنشغل الميزة فوراً، ولو اترفضت بنفحص shouldShowRequestPermissionRationale علشان نوضح للمستخدم أهميتها ونطلبها تاني، ولو اترفضت نهائياً بنظهر حوار يوجه المستخدم لصفحة إعدادات التطبيق في النظام.",
        "best_answer_ar": "التعامل مع الـ Runtime Permissions بيحتاج معمارية منظمة تحترم تجربة المستخدم وتمنع الكراشات.\n\nأول قاعدة بنمشي بيها هي طلب الصلاحية Just-in-Time لما المستخدم يدوس على الزرار المحتاج للكاميرا أو الـ GPS، مش أول ما يفتح التطبيق.\n\nتاني قاعدة هي إدارة الحالات الأربع بوعي هندسي: في البداية لو الصلاحية ممنوحة بالفعل بنفحصها بـ checkSelfPermission ونفتح العتاد فوراً. ولو بتنطلب لأول مرة بنطلبها عبر Activity Result API. أما لو اترفضت مرة واحدة فـ shouldShowRequestPermissionRationale بترجع true، وهنا بنعرض Rationale Dialog يشرح للمستخدم ليه الميزة دي محتاجة الصلاحية قبل ما نطلبها تاني.\n\nوفي حالة الرفض الدائم لما المستخدم يرفض مرتين أو يختار Don't ask again، الدالة بترجع false والنظام مبيرضاش يظهر الدايلوج أصلاً؛ في الحالة دي بنظهر Dialog محترم يوضح له إن الصلاحية مقفولة نهائياً، وبنديله زرار يفتحه صفحة إعدادات التطبيق عبر Settings.ACTION_APPLICATION_DETAILS_SETTINGS.\n\nوبنستخدم Activity Result API حصرياً علشان النتيجة تكون Type-safe ومتربطة بدورة الحياة بدون الحاجة لـ Request Codes القديمة.",
        "deep_answer_ar": "على مستوى الـ OS Kernel والـ Security Subsystems، الصلاحيات بتدار من خلال PermissionManagerService و AppOpsManager داخل الـ system_server. لما الصلاحية بتتمنح، النظام بيعين الـ Linux UID بتاع التطبيق لـ Supplementary GID في النواة بيسمح له بالوصول لملفات العتاد في مجلد /dev الخاص بالكاميرا والصوت.\n\nالدالة shouldShowRequestPermissionRationale بتعكس الـ Bitwise Flags المتسجلة للصلاحية في الـ system_server؛ في البداية بتكون الأعلام فاضية فبترجع false. مع أول رفض من المستخدم بيتحط علم USER_SET فبترجع true علشان تعرض الـ Rationale التوضيحي. لو داس Don't ask again أو رفض مرتين في أندرويد الحديث، بيتحط علم USER_FIXED، وساعتها أي نداء لطلب الصلاحية بيترفض فوراً من سيرفر النظام بدون عرض أي UI، والدالة بترجع false للأبد.\n\nالتطورات الحديثة فرضت قيود إضافية لحماية الخصوصية: أندرويد 11 جاب الـ One-time permissions فبقت الصلاحية تنتهي مع خروج التطبيق من الواجهة، وأندرويد 12 فرق بين الموقع الدقيق والتقريبي، وأندرويد 13 أضاف صلاحية POST_NOTIFICATIONS للإشعارات، وأندرويد 14 أضاف صلاحية READ_MEDIA_VISUAL_USER_SELECTED للمشاركة الجزئية للصور والفيديوهات.\n\nالـ Staff Engineer بيصمم المعمارية بحيث التطبيق ميفترضش أبداً دوام الصلاحية؛ بنعمل فحص أمني قبل كل استدعاء، وبنوفر Graceful Degradation بحيث لو الصلاحية اترفضت التطبيق يكمل تقديم خدمات تانية بديلة، وبنراقب الرجوع من صفحة الإعدادات عبر دورة حياة onResume."
    }

    # =========================================================================
    # AND-14: What is the Activity Result API, and why use it?
    # =========================================================================
    qid = "AND-14"
    concept_en = """The Activity Result API is the modern, type-safe framework introduced in AndroidX to handle cross-activity communication and result retrieval, completely superseding the legacy, deprecated `startActivityForResult()` and `onActivityResult()` pattern.

The legacy approach suffered from severe architectural deficiencies:
1. Lifecycle Coupling and Fragment Collisions:
Result handling was tightly bound to the Activity or Fragment class, forcing developers to route disparate results through a monolithic, error-prone `onActivityResult` switch-case block using integer request codes. Request code collisions frequently occurred across large, multi-module codebases.
2. The Fatal Low-Memory Process Kill Bug:
When launching an external resource-heavy activity—such as the system camera or a file gallery picker—Android frequently terminated the background caller Activity under memory pressure. When the user returned with the captured photo, the calling Activity was recreated from scratch, but its `onActivityResult` callback frequently lost transient references or executed before view models were initialized, leading to blank screens or NullPointerExceptions.

The Activity Result API addresses these problems by decoupling result handling through dedicated contracts (`ActivityResultContract<I, O>`) and registering persistent, type-safe launchers via `registerForActivityResult()`. The framework mandates registering launchers unconditionally during initialization or `onCreate()`. By doing so, if the host Activity is destroyed while the target activity is active, the framework re-registers the callback prior to entering the STARTED lifecycle state, automatically delivering the result to the rehydrated launcher without state loss."""

    walkthrough_en = """Selecting an image and handling results type-safely via the Activity Result API:
```kotlin
class ProfileActivity : AppCompatActivity() {

    // 1. Unconditionally register the typed contract during property initialization
    private val pickImageLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        // 2. Type-safe callback invoked automatically even if Activity was recreated
        if (uri != null) {
            loadAvatarPreview(uri)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_profile)

        findViewById<Button>(R.id.btn_change_avatar).setOnClickListener {
            // 3. Launch with type-safe input parameter
            pickImageLauncher.launch("image/*")
        }
    }

    private fun loadAvatarPreview(imageUri: Uri) {
        findViewById<ImageView>(R.id.avatar_image).setImageURI(imageUri)
    }
}
```
Failure scenario:
If an engineer attempts to register `registerForActivityResult` inside a button click listener or after `onStart()`, the runtime immediately throws an `IllegalStateException: LifecycleOwner is attempting to register while current state is STARTED`. The callback MUST be registered during initialization so the OS can restore it if the Activity is killed in the background."""

    short_en = """The Activity Result API replaces legacy startActivityForResult with a type-safe, decoupled contract pattern. By mandating launcher registration during component initialization, it ensures result callbacks survive caller Activity destruction and background process reclamation when external activities like the camera or gallery consume system RAM."""

    structured_en = """To begin with, the Activity Result API is Android's modern standard for initiating external component flows and processing their return results, completely superseding the deprecated startActivityForResult and onActivityResult pattern.

From an architectural standpoint, the legacy model suffered from two fundamental flaws: tightly coupling all result parsing to a monolithic switch-case method inside the Activity, and failing catastrophically when the calling Activity was destroyed in the background due to low memory while a memory-intensive camera or document picker was active.

As for boundary management, the Activity Result API decouples result handling into modular, type-safe contracts using ActivityResultContract. A launcher specifies typed input parameters and yields strongly typed output objects, eliminating manual integer request codes and Intent parsing boilerplate.

In production scenarios, registration timing is critical. Launchers must be declared unconditionally during initialization or in onCreate before the lifecycle reaches STARTED. This timing contract allows the underlying ActivityResultRegistry to rebind the result listener automatically upon Activity recreation, guaranteeing seamless delivery even after process death."""

    deep_senior_en = """At the framework architecture and lifecycle registry level, the Activity Result API is orchestrated by ComponentActivity's internal ActivityResultRegistry. In the legacy startActivityForResult model, the platform dispatched results directly through ActivityThread into onActivityResult(). If the operating system terminated the calling Activity process while the user was interacting with an external camera application, re-instantiating the Activity frequently led to lost callbacks because the receiving listeners were not yet attached when the system delivered the result bundle.

The ActivityResultRegistry resolves this synchronization race through a durable key-based registry. When registerForActivityResult(contract, callback) is invoked during initialization, the registry generates or retrieves a unique persistent string key for that operation. If the hosting Activity is killed by the Low Memory Killer while the camera is open, the camera returns its result across Binder IPC to ActivityTaskManagerService.

When the caller Activity is reconstructed, ActivityThread invokes performCreate(), restoring the saved state Bundle. Because the launcher is registered unconditionally before onStart(), the ActivityResultRegistry matches the incoming system result against the re-registered key and queues the dispatch until the lifecycle reaches CREATED, delivering the parsed result safely to the developer's callback.

Furthermore, Staff engineers leverage custom ActivityResultContracts to establish clean architectural boundaries. By extending ActivityResultContract<Input, Output>, teams encapsulate complex Intent assembly, URI permissions, and output parsing (such as transforming raw Intent extras into domain-specific DTOs) into isolated, unit-testable components, passing mock ActivityResultRegistry instances during testing without launching actual Android UI components."""

    ee.update_canonical_question(qid, concept_en, walkthrough_en, structured_en, deep_senior_en, short_en)

    metadata_entries[qid] = {
        "id": qid,
        "questionAr": "ما هو الـ Activity Result API ولماذا نستخدمه بدلاً من startActivityForResult؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- معرفة أسباب إلغاء (Deprecation) النموذج القديم `startActivityForResult` ومصيدة تدمير الشاشة.\n- فهم عقد التسجيل الصارم في دورة الحياة وسبب إلزامية الاستدعاء قبل حالة `STARTED`.\n- تصميم عقود مخصصة (`ActivityResultContract<I, O>`) وفصل منطق استلام النتائج بشكل Type-safe.",
        "why_it_matters_ar": "الـ Activity Result API هو البديل الحديث والآمن الذي أطلقته جوجل لاستبدال النموذج القديم `startActivityForResult` و `onActivityResult`. المشكلة الكارثية في النموذج القديم كانت تحدث عندما يفتح التطبيق الكاميرا أو معرض الصور؛ فتطبيق الكاميرا يستهلك كمية رام ضخمة تجبر نظام أندرويد على قتل الـ Activity الأصلية في الخلفية. وعندما يلتقط المستخدم الصورة ويعود، يتم إعادة بناء الـ Activity من الصفر، ولكن دالة `onActivityResult` كانت تفشل في تسليم النتيجة للمكان الصحيح أو تسبب كراش بسبب ضياع المراجع. الـ Activity Result API يحل هذه المعضلة عبر تسجيل الـ Launchers في مرحلة الـ Initialization قبل حالة `STARTED`، مما يضمن تسجيل المستمع تلقائياً حتى لو ماتت الشاشة وأعيد إنشاؤها.",
        "worked_example_ar": "اختيار صورة من المعرض باستخدام عقد جاهز وآمن مع دورة الحياة:\n```kotlin\nclass ProfileActivity : AppCompatActivity() {\n\n    // 1. التسجيل الإلزامي أثناء تهيئة المتغيرات قبل onCreate\n    private val pickImageLauncher = registerForActivityResult(\n        ActivityResultContracts.GetContent()\n    ) { uri: Uri? ->\n        // 2. النتيجة مضمونة الوصول حتى لو تم تدمير الشاشة أثناء اختيار الصورة\n        uri?.let { displayAvatar(it) }\n    }\n\n    override fun onCreate(savedInstanceState: Bundle?) {\n        super.onCreate(savedInstanceState)\n        setContentView(R.layout.activity_profile)\n\n        findViewById<Button>(R.id.btn_select).setOnClickListener {\n            // 3. إطلاق العقد بمعاملات Type-safe\n            pickImageLauncher.launch(\"image/*\")\n        }\n    }\n\n    private fun displayAvatar(uri: Uri) {\n        findViewById<ImageView>(R.id.avatar).setImageURI(uri)\n    }\n}\n```",
        "trade_offs_ar": "النموذج القديم كان يسمح باستدعاء `startActivityForResult` في أي مكان بالكود (مثل داخل زرار)، لكنه يسبب كوارث فقدان البيانات عند موت الشاشة وتضارب الـ Request Codes. الـ Activity Result API يفرض تسجيل الـ Launcher في مرحلة التهيئة فقط، مما يتطلب تنظيماً مسبقاً، لكنه في المقابل يوفر Type-safety كاملة، وعزل تام للمنطق، وضمان استلام النتيجة بعد إعادة الإحياء.",
        "failure_modes_ar": "استدعاء `registerForActivityResult` داخل حدث ضغطة زر أو بعد انتقال الـ Lifecycle لحالة `STARTED` يرمي استثناء `IllegalStateException` فوري من أندرويد. نسيان التعامل مع احتمال رجوع النتيجة بقيمة null (عندما يلغي المستخدم العملية) يسبب كراشات غير متوقعة. يتم اختبار ذلك بتفعيل خيار Don't keep activities في إعدادات المطور للتحقق من صمود استلام النتيجة بعد تدمير الشاشة.",
        "production_perspective_ar": "في التطبيقات الكبيرة، يتم بناء عقود مخصصة (Custom Contracts) للمهام المتكررة مثل التقاط صور الهوية أو مسح الباركود أو فتح شاشات الدفع، بحيث يعزل كود تجميع الـ Intent وفك تشفير الـ Extras داخل كلاس مستقل قابل للاختبار البرمجي (Unit Testing) دون الحاجة لتشغيل واجهات أندرويد حقيقية.",
        "how_to_answer_ar": "- **السبب المعماري:** وضح الفشل الكارثي للنموذج القديم عند استهلاك الكاميرا للرام وموت الشاشة الأصلية.\n- **طريقة الشرح:** اشرح آلية عمل الـ Contracts وفصل الـ Request Codes وتأمين الـ Type-Safety.\n- **قواعد دورة الحياة:** ركز على إلزامية التسجيل قبل `onStart` وكيف يستعيد الـ Registry النتيجة.\n- **أنماط الفشل:** اذكر `IllegalStateException` ومصيدة تسجيل الـ Launcher داخل ضغطة زر.\n- **الحل العملي:** استعرض كود استخدام `GetContent()` وبناء Custom Contract.",
        "talking_points_ar": "ناقش دور `ActivityResultRegistry` في تخزين المفاتيح النصية عبر `ActivityClientRecord`، وكيفية جدولة تسليم النتائج بعد `performCreate`، وكيفية كتابة Custom `ActivityResultContract<I, O>`، وطرق اختبار العقود باستخدام `ActivityResultRegistryOwner` ومضاعفات الاختبار (Test Doubles).",
        "follow_ups_ar": "- **المحاور:** \"ليه النظام بيرمي IllegalStateException لو عملت registerForActivityResult جوه زرار؟\"\n  **المرشح:** \"لأن النظام بيشترط تسجيل الـ Callback أثناء تهيئة الشاشة (في مرحلة INITIALIZED أو onCreate) قبل ما دورة الحياة توصل لـ STARTED. وده علشان لو الشاشة اتدمرت في الخلفية ورجعت، النظام يلحق يسجل نفس الـ Callback بنفس المفتاح قبل ما يستلم النتيجة من الـ system_server، فلو سمح بالتسجيل جوه زرار النتيجة كانت هتضيع لو الشاشة ماتت.\"\n\n- **المحاور:** \"إزاي أعمل Custom Activity Result Contract مخصص لميزتي؟\"\n  **المرشح:** \"بنعمل كلاس بيورث من `ActivityResultContract<I, O>` وبنحدد نوع المدخل I والخرج O، وبنعمل Override لدالتين: `createIntent(context, input)` لبناء الـ Intent بالـ Extras المطلوبة، ودالة `parseResult(resultCode, intent)` لاستخراج النتيجة وتحويلها لـ Type-safe Domain Model أو رجوع null لو المستخدم ألغى العملية.\"\n\n- **المحاور:** \"هل الـ Activity Result API بيشتغل جوه الـ Fragments والـ Composables؟\"\n  **المرشح:** \"أيوة، في الـ Fragments بنستخدم نفس دالة `registerForActivityResult` العادية، وفي Jetpack Compose بنستخدم الدالة المخصصة `rememberLauncherForActivityResult` اللي بتسجل العقد تلقائياً مع دورة حياة الـ Composable وتنجو من إعادة التركيب.\"",
        "self_check_ar": "حدد عيوب `startActivityForResult` القديم؛ اشرح سيناريو فقدان النتيجة مع الكاميرا؛ بيّن شرط توقيت التسجيل الإلزامي؛ وصمم Custom Contract مخصص لشاشة دفع.",
        "references_ar": f"- [Get a result from an activity](https://developer.android.com/training/basics/intents/result) — الدليل الرسمي للـ Activity Result API.\n- [ActivityResultContract reference](https://developer.android.com/reference/androidx/activity/result/contract/ActivityResultContract) — التوثيق المرجعي لبناء العقود المخصصة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ Activity Result API هو البديل الحديث والآمن لـ startActivityForResult القديمة، بيحل مشكلة كراشات وضياع النتائج لما الكاميرا تستهلك الرام والشاشة الأصلية تموت في الخلفية، وده عن طريق عقود Type-safe وتسجيل إلزامي للمستمع أثناء تهيئة الشاشة قبل حالة STARTED.",
        "best_answer_ar": "الـ Activity Result API اتعمل علشان يحل أكبر مشكلتين كانوا موجودين في startActivityForResult القديمة.\n\nالمشكلة الأولى كانت معمارية: كل النتائج كانت بتترمي في دالة onActivityResult واحدة كبيرة بـ switch-case وRequest Codes أرقام يدوية بتعمل تضارب في المشاريع الكبيرة وتعتبر Anti-pattern.\n\nالمشكلة التانية والأخطر كانت Low Memory Process Kill: لما تفتح الكاميرا أو المعرض، التطبيق التاني بيستهلك كمية رام ضخمة، فالنظام بيقتل الشاشة بتاعتك في الخلفية. ولما المستخدم يصور ويرجع، الشاشة بيعاد بناؤها من الصفر، فدالة onActivityResult القديمة كانت بتفشل ومبتعرفش تسلم النتيجة وبتعمل كراشات NullPointerException.\n\nالـ Activity Result API حل المشكلة دي بنظام الـ Contracts؛ إنت بتسجل الـ Launcher إجبارياً في مرحلة الـ Initialization قبل ما دورة الحياة توصل لـ STARTED. ولما الشاشة تموت في الخلفية وترجع تاني، الـ ActivityResultRegistry بيكون مسجل نفس الـ Callback بنفس المفتاح، فيستلم الصورة ويسلمها للكود بنظافة وبدون أي فقدان للبيانات.",
        "deep_answer_ar": "على مستوى الـ Framework والـ Architecture، قلب النظام ده هو كلاس ActivityResultRegistry الموجود جوه ComponentActivity. في النظام القديم، النتيجة كانت بتتبعت مباشرة من الـ system_server عبر Binder IPC للـ ActivityThread ويتم استدعاء onActivityResult فوراً؛ فلو الشاشة كانت ماتت في الخلفية وأعيد إنشاؤها بعد ما النتيجة وصلت، كان بيحصل Race Condition ومفيش أي مستمع مربوط يلحق يستلم النتيجة.\n\nالـ ActivityResultRegistry حل المعضلة دي بـ Key-based Registration؛ لما بتنادي registerForActivityResult في مرحلة الـ Initialization، النظام بيولد Persistent Unique Key للعملية دي ويسجله في الـ Registry. ولما الكاميرا تخلص والـ Process ترجع تشتغل تحت ضغط الذاكرة، الـ ActivityThread بيبدأ ينفذ performCreate. وبما إن الـ Launcher مسجل قبل onStart، الـ Registry بيمسك النتيجة اللي جاية من السيرفر ويحطها في Queue داخلية لحد ما الـ Lifecycle يوصل لـ CREATED وبعدين يسلمها للمستمع بأمان تام.\n\nعلشان كده لو حاولت تسجل الـ Launcher بعد onStart أو جوه ضغطة زرار، النظام بيرمي IllegalStateException فوري لأن العقد ده مينفعش يتسجل بعد فوات الأوان وبدء دورة حياة التفاعل.\n\nفي الفرق الكبيرة بنبني Custom ActivityResultContract؛ الكلاس ده بنعزل جواه صياغة الـ Intent بالـ Permissions المطلوبة وفك تشفير الـ Extras، وبنعمل له Unit Testing بمضاعفات اختبار مستقلة تماماً عن الـ Android UI Framework، وده بيعزز مبدأ Single Responsibility وجودة الكود."
    }

    # =========================================================================
    # AND-15: Compare Activity, Fragment, Compose navigation, and deep links.
    # =========================================================================
    qid = "AND-15"
    concept_en = """Modern Android application architecture spans four evolutionary navigation paradigms, each representing distinct memory boundaries, lifecycle complexities, and routing models:

1. Multi-Activity Navigation:
The historical Android paradigm where every distinct screen is encapsulated in an independent, manifest-declared Activity. Activities represent heavyweight OS-level windows managed directly by the platform ActivityTaskManagerService and the Linux low-memory killer. Transitions incur substantial IPC overhead, window-swapping latency, and isolated memory heaps. State sharing requires Parcelable Intent extras, making intra-app communication clunky and slow.

2. Single-Activity with Fragment Navigation:
Introduced to mitigate multi-activity overhead, this paradigm hosts multiple modular UI sub-trees (Fragments) within a single container Activity using the Jetpack Navigation Component. Destinations share a single Window and process heap, significantly accelerating transition performance. However, it introduces the notorious dual-lifecycle dilemma: a Fragment's object instance outlives its view tree when pushed to the backstack, creating pervasive ViewBinding and observer memory leak hazards.

3. Jetpack Compose Navigation:
The modern declarative paradigm where destinations are pure Composable functions hosted within a single NavHost. It completely eliminates FragmentManager overhead and view lifecycle bifurcation. In modern Navigation Compose (2.8+), destinations are declared type-safely using `@Serializable` Kotlin objects or data classes backed by Kotlinx Serialization, eliminating untyped route strings. Each backstack entry (`NavBackStackEntry`) acts as a dedicated LifecycleOwner, ViewModelStoreOwner, and SavedStateRegistryOwner, providing clean, scoped memory boundaries.

4. Deep Links and Android App Links:
External routing entry points that direct users into specific application destinations from web links, notifications, or third-party applications. Standard deep links rely on custom URI schemes (`myapp://product/42`), while verified Android App Links use standard HTTPS URLs (`https://example.com/product/42`) cryptographically verified against a domain Digital Asset Links JSON file, opening the application directly without an OS chooser dialog while synthesizing proper hierarchical backstacks."""

    walkthrough_en = """Implementing modern Type-Safe Jetpack Compose Navigation with verified Deep Link routing:
```kotlin
// 1. Declare type-safe routes using Kotlinx Serialization
@Serializable
data object HomeRoute

@Serializable
data class ProductDetailRoute(val productId: String)

// 2. Configure NavHost with type-safe destinations and deep links
@Composable
fun AppNavGraph(navController: NavHostController) {
    NavHost(navController = navController, startDestination = HomeRoute) {
        composable<HomeRoute> {
            HomeScreen(onProductClick = { id ->
                navController.navigate(ProductDetailRoute(productId = id))
            })
        }

        composable<ProductDetailRoute>(
            deepLinks = listOf(
                navDeepLink<ProductDetailRoute>(
                    basePath = "https://shop.example.com/products"
                )
            )
        ) { backStackEntry ->
            // Route parameters are extracted with 100% compile-time type safety
            val route: ProductDetailRoute = backStackEntry.toRoute()
            ProductDetailScreen(productId = route.productId)
        }
    }
}
```
Failure scenario:
If an application opening from a deep link does not synthesize a hierarchical backstack (e.g., using NavDeepLinkBuilder), pressing the system Back button closes the application immediately instead of navigating to the parent catalog screen, breaking standard platform navigation expectations."""

    short_en = """Multi-Activity navigation relies on heavyweight OS windows; Fragment navigation uses modular sub-trees within one Activity but introduces dual-lifecycle complexity; Compose Navigation uses lightweight, type-safe declarative Composable destinations scoped to NavBackStackEntry; and Deep Links provide verified external HTTPS entry routes with synthesized backstacks."""

    structured_en = """To begin with, Android navigation has evolved across four distinct paradigms, progressing from heavy system window boundaries toward lightweight, declarative destination graphs.

From an architectural standpoint, the traditional Multi-Activity approach encapsulates each screen in a distinct Activity. While offering rigid OS-level isolation, it introduces heavy IPC transitions and complex Intent data sharing. The Single-Activity with Fragment model improved rendering speed by swapping views inside one window, but introduced the infamous dual-lifecycle mismatch between Fragment instances and view hierarchies.

As for boundary management, Jetpack Compose Navigation represents the modern standard. By mapping routes directly to Composable functions, it abolishes FragmentManager complexity. With modern Navigation Compose, routes are declared type-safely via Kotlinx Serialization, while each NavBackStackEntry provides an isolated scope for ViewModels and saved state.

In production scenarios, Deep Links and verified Android App Links serve as external gateways. Using Digital Asset Links for cryptographic domain ownership verification, App Links allow web URLs to bypass app-chooser dialogs, launching users directly into target screens while seamlessly synthesizing a natural hierarchical backstack."""

    deep_senior_en = """At the operating system, WindowManager, and SurfaceFlinger level, the architectural divide between Multi-Activity and Single-Activity architectures is profound. In a Multi-Activity setup, every Activity maintains its own PhoneWindow, SurfaceControl hierarchy, and dedicated render thread pipelines. Transitioning between activities requires ActivityTaskManagerService to execute an inter-process transition, taking snapshots and swapping hardware display surfaces through the system compositor, which consumes substantial GPU and memory bandwidth.

Transitioning to a Single-Activity architecture collapses this overhead: the entire application shares a single Surface, Window, and view tree root. However, the Fragment-based implementation introduced massive framework baggage. FragmentManager manages its own internal backstack transaction engine, BackStackRecord lists, and view lifecycle transitions, where onDestroyView() destroys the layout while keeping the Fragment instance alive, causing widespread memory leaks when view bindings are not manually nulled.

Jetpack Compose Navigation eliminates this entire abstraction layer. A Composable destination is not a component; it is an emitting node within the Compose runtime node graph. Navigation Compose manages a stack of NavBackStackEntry objects. Each entry implements LifecycleOwner, ViewModelStoreOwner, and SavedStateRegistryOwner. This guarantees that when a Composable destination is popped from the navigation backstack, its scoped ViewModelStore is cleared, triggering onCleared() and freeing memory without FragmentManager gymnastics.

For external ingress, verified Android App Links rely on the system Package Manager verifying the domain's /.well-known/assetlinks.json file during installation. When verified with android:autoVerify="true", the OS routes the HTTPS intent directly to the app without prompting the user. Production navigation architectures intercept these intents via NavDeepLinkBuilder, synthesizing the entire synthetic parent backstack so that pressing Back navigates the user logically upward toward the root screen rather than exiting the application."""

    ee.update_canonical_question(qid, concept_en, walkthrough_en, structured_en, deep_senior_en, short_en)

    metadata_entries[qid] = {
        "id": qid,
        "questionAr": "قارن بين التنقل عبر الـ Activity والـ Fragment والـ Compose Navigation والـ Deep Links.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "- استيعاب التطور المعماري من Multi-Activity إلى Single-Activity مع Compose Navigation.\n- فهم نطاقات دورة الحياة وإدارة الـ ViewModels عبر `NavBackStackEntry`.\n- تصميم وتأمين الـ Deep Links و Android App Links وبناء الـ Synthetic Backstack بشكل سليم.",
        "why_it_matters_ar": "تطور معمارية التنقل (Navigation) في أندرويد يعكس سعي النظام لتقليل استهلاك الذاكرة وتسهيل إدارة الحالة. التنقل التقليدي بين عدة Activities كان يستهلك موارد النظام لإنشاء نوافذ رسم مستقلة (Windows) وتمرير البيانات عبر الـ Intent Extras الثقيلة. التنقل عبر الـ Fragments في Single-Activity قلل الاستهلاك لكنه أدخل تعقيد دورة حياة الـ View المنفصلة عن الـ Fragment. المعيار الحديث في Jetpack Compose Navigation جعل الوجهات عبارة عن دوال Composable خفيفة مع Type-Safety كاملة عبر Kotlinx Serialization، مع ربط كل وجهة بـ `NavBackStackEntry` يدير دورة حياتها والـ ViewModel الخاص بها. وتعتبر الـ Deep Links و App Links بوابات الدخول الخارجية الأساسية لتوجيه المستخدمين من الويب والإشعارات مباشرة للوجهة المطلوبة مع توليد الـ Backstack السليم.",
        "worked_example_ar": "التنقل الحديث Type-Safe Compose Navigation مع دعم الـ Deep Links:\n```kotlin\n@Serializable\ndata object CatalogRoute\n\n@Serializable\ndata class ProductRoute(val id: String)\n\n@Composable\nfun NavigationGraph(navController: NavHostController) {\n    NavHost(navController = navController, startDestination = CatalogRoute) {\n        composable<CatalogRoute> {\n            CatalogScreen(onProductSelect = { id ->\n                navController.navigate(ProductRoute(id = id))\n            })\n        }\n        composable<ProductRoute>(\n            deepLinks = listOf(\n                navDeepLink<ProductRoute>(basePath = \"https://store.example.com/products\")\n            )\n        ) { backStackEntry ->\n            val route: ProductRoute = backStackEntry.toRoute()\n            ProductScreen(productId = route.id)\n        }\n    }\n}\n```",
        "trade_offs_ar": "الـ Multi-Activity يوفر عزلاً تاماً لكل شاشة في النظام لكنه ثقيل جداً في استهلاك الرام والانتقالات البصرية. الـ Fragments خفيفة وسريعة لكنها معقدة في إدارة دورة حياة الـ Views وتسريب الذاكرة في الـ Backstack. الـ Compose Navigation خفيف جداً ونظيف ومعاصر ولكنه يتطلب إعادة التفكير في إدارة الحالة في Compose بالكامل. الـ App Links تتطلب إعداد ملف `assetlinks.json` على السيرفر والتحقق الصارم من النطاق (Domain Verification) لكنها تضمن فتح التطبيق مباشرة دون ظهور App Chooser.",
        "failure_modes_ar": "فتح التطبيق عبر Deep Link بدون بناء الـ Synthetic Backstack يؤدي لخروج المستخدم من التطبيق فور الضغط على زر Back بدلاً من الرجوع للشاشة السابقة. تسريب الـ ViewModels عند ربطها بالـ Activity بدلاً من ربطها بـ `NavBackStackEntry` الخاص بالوجهة. إهمال التحقق من صحة معاملات الـ Deep Link يعرض التطبيق لكراشات وتلاعب بالبيانات. يتم اختبار الـ Deep Links بأوامر `adb shell am start -a android.intent.action.VIEW -d ...`.",
        "production_perspective_ar": "في التطبيقات الضخمة للشركات، يتم اعتماد Single-Activity Architecture مع Compose Navigation وعقود Type-Safe كاملة. يتم عزل مسارات الموديولات المختلفة في Nested Graphs مستقلة، وربط الـ ViewModels الخاصة بكل Feature بـ `NavBackStackEntry` للوجهة لضمان تصفير الذاكرة فور مغادرة الشاشة. يتم إعداد Android App Links للروابط التسويقية والإشعارات مع التأكد من مطابقة الـ SHA-256 fingerprint في ملف `assetlinks.json`.",
        "how_to_answer_ar": "- **السبب المعماري:** استعرض التطور التاريخي من Multi-Activity إلى Fragments وصولاً لـ Compose Navigation.\n- **طريقة الشرح:** قارن بينها من حيث تكلفة إنشاء النوافذ، تعقيد دورة الحياة، وسهولة تمرير البيانات.\n- **إدارة النطاقات:** اشرح كيف يدير `NavBackStackEntry` الـ ViewModelStore لكل شاشة في Compose.\n- **الـ Deep Links:** فرّق بين الـ Custom Schemes والـ App Links الموثقة وكيفية بناء الـ Backstack.\n- **الحل العملي:** استشهد بكود Navigation Type-Safe في Compose 2.8+ مع Kotlinx Serialization.",
        "talking_points_ar": "ناقش تكلفة الـ WindowManager والـ SurfaceFlinger في Multi-Activity مقابل Surface موحد في Single-Activity، وكيف تخلصت Compose من FragmentManager، وآلية عمل Digital Asset Links للتحقق من ملكية الـ Domain، وبناء الـ Synthetic Backstack باستخدام `NavDeepLinkBuilder`، وكيفية عزل الـ ViewModels في مسارات التنقل.",
        "follow_ups_ar": "- **المحاور:** \"إزاي NavBackStackEntry بيدير دورة حياة الـ ViewModels جوه Compose Navigation؟\"\n  **المرشح:** \"كل وجهة بتدخل في الـ Backstack بتتمثل كـ NavBackStackEntry، والكائن ده بيطبق واجهات LifecycleOwner و ViewModelStoreOwner و SavedStateRegistryOwner. فلما تطلب ViewModel جوه الوجهة، الـ ViewModel بيتربط بالـ Store الخاص بالوجهة دي فقط، ولما تخرج منها وتعمل Pop من الـ Backstack، الـ Store بيتعمله clear وonCleared بتترن فوراً لتحرير الرام.\"\n\n- **المحاور:** \"ما الفرق الجوهري بين الـ Deep Link العادي وبين الـ Android App Link؟\"\n  **المرشح:** \"الـ Deep Link العادي بيستخدم Custom Scheme زي `myapp://product` وده لو في تطبيق تاني مسجل نفس الـ Scheme النظام هيسأل المستخدم يختار مين. أما Android App Link فبيستخدم رابط HTTPS قياسي وبيتفعل معاه `android:autoVerify=\"true\"`، والنظام بيتحقق من ملف `assetlinks.json` على السيرفر وقت التثبيت؛ فلو اتطابق، الرابط بيفتح تطبيقك مباشرة بدون أي Dialog.\"\n\n- **المحاور:** \"ليه الـ Compose Navigation الحديثة بقت Type-Safe؟\"\n  **المرشح:** \"لأنها من أول إصدار 2.8+ بقت تدعم استخدام Kotlinx Serialization مع كلاسات @Serializable data class بدل المسارات النصية القديمة اللي كانت زي الـ URLs ومليانة أخطاء كتابية في أسماء الـ Arguments، فبقت كل المعاملات تتفحص وقت الـ Compile Time بأعلى موثوقية.\"",
        "self_check_ar": "قارن بين أساليب التنقل الأربعة؛ اشرح كيف تدير Compose Navigation دورة حياة الوجهات؛ بيّن الفارق الأمني بين Deep Links و App Links؛ وصمم مسار تنقل Type-Safe متكامل.",
        "references_ar": f"- [Navigate with Compose](https://developer.android.com/develop/ui/compose/navigation) — دليل التنقل في Jetpack Compose.\n- [Type safety in Navigation Compose](https://developer.android.com/guide/navigation/design/type-safety) — معمارية التنقل الآمن للأنواع في أندرويد.\n- [Verify Android App Links](https://developer.android.com/training/app-links/verify-site-associations) — إعداد وتوثيق الـ App Links.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الـ Multi-Activity تقيل وبيفتح نوافذ رسم مستقلة للنظام، والـ Fragments خففت الحمل جوه Activity واحدة بس عقدت دورة الحياة، والـ Compose Navigation هو المعيار الحديث بوجهات خفيفة وType-Safe عبر NavBackStackEntry، والـ Deep Links هي بوابات الدخول الخارجية اللي بتفتح وجهة معينة مع بناء الـ Backstack السليم.",
        "best_answer_ar": "معمارية التنقل في أندرويد مرت برحلة تطور هندسية واضحة:\n\nفي البداية كان الـ Multi-Activity Architecture: كل شاشة عبارة عن Activity مستقلة بـ Window منفصل وتواصل ثقيل بالـ Intent Extras عبر نظام التشغيل، وده كان بيهدر موارد الجهاز في الانتقالات.\n\nبعد كده ظهر الـ Single-Activity مع الـ Fragments: خلينا Activity واحدة كحاوية، والتنقل بقى عبارة عن تبديل Fragments جوه نفس الـ Window. ده سرّع الرندرة جداً لكنه جاب معاه معضلة دورة حياة الـ View المنفصلة عن الـ Fragment وتسريبات الـ ViewBinding الشهيرة في الـ Backstack.\n\nدلوقتي المعيار القياسي هو Jetpack Compose Navigation: الوجهات بقت مجرد Composable functions بتترسم جوه NavHost موحد، بدون أي Fragments. ومن أول إصدار 2.8+ بقى التنقل Type-Safe بالكامل بكلاسات Serializable وبدون String URLs. وكل وجهة في الـ Backstack بتتمثل بـ NavBackStackEntry يمتلك ViewModelStore خاص بيه بيتصفر أول ما تخرج من الشاشة.\n\nأما الـ Deep Links و App Links فهي آليات توجيه المستخدم من خارج التطبيق (زي الروابط في المتصفح أو الإشعارات) مباشرة لوجهة معينة جوه الجراف، مع التحقق الأمني من الـ Domain وبناء الـ Backstack السليم بحيث لما يدوس Back ميرميهوش بره التطبيق.",
        "deep_answer_ar": "على مستوى الـ OS WindowManager والـ SurfaceFlinger، الفرق بين الـ Multi-Activity والـ Single-Activity جذري. في الـ Multi-Activity، كل Activity ليها PhoneWindow وSurface مستقلين، والانتقال بينهم بيجبر الـ ActivityTaskManagerService على تبديل الـ Surfaces في الـ Hardware Compositor وده بيستهلك GPU Memory وContext Switching عالي في النواة.\n\nفي الـ Single-Activity كل التطبيق بيشترك في Surface واحد، لكن الـ FragmentManager كان بيضيف تعقيد ضخم في إدارة مصفوفة الـ BackStackRecords، والفرق بين وجود كائن الـ Fragment في الـ Heap وبين هدم شجرة الـ Views في onDestroyView كان سبب 80% من تسريبات الـ ViewBinding.\n\nالـ Compose Navigation لغت الطبقة دي بالكامل؛ الوجهة مبقتش Component ولا كائن في الـ FragmentManager، دي بقت مجرد Node في الـ Compose Slot Table. الـ Navigation Compose بيدير Stack من كائنات NavBackStackEntry، وكل Entry بيطبق LifecycleOwner و ViewModelStoreOwner و SavedStateRegistryOwner مستقلين. ده بيضمن إن لما المستخدم يعمل Pop للشاشة، الـ Store بتاعها بيتعمله clear وonCleared بتترن فوراً لتحرير الرام.\n\nأما في مسار الدخول الخارجي، الـ Android App Links بتعتمد على فحص ملف /.well-known/assetlinks.json المشفر بـ SHA-256 وقت تثبيت التطبيق بواسطة PackageManager. ولما يتحقق autoVerify=\"true\"، النظام بيوجه الرابط مباشرة للتطبيق بدون App Chooser Dialog. وفي الإنتاج بنستخدم NavDeepLinkBuilder علشان نبني الـ Synthetic Parent Backstack بالكامل، بحيث لو العميل دخل على صفحة منتج من رابط على تويتر وضغط Back، يرجع لكاتالوج المنتجات مش يقفل التطبيق في وشه."
    }

    # Write metadata dictionary to metadata_and_06_15.json
    out_file = ee.DATA_DIR / "metadata_and_06_15.json"
    out_file.write_text(json.dumps(metadata_entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved metadata for {len(metadata_entries)} questions to {out_file}")

    # Merge metadata into arabic_lab_metadata.json
    ee.merge_all_metadata()

    # Validate all 10 questions
    print("\n--- Validating AND-06 through AND-15 ---")
    all_valid = True
    for i in range(6, 16):
        qid = f"AND-{i:02d}"
        errs = ee.validate_question(qid)
        if errs:
            print(f"❌ {qid} ERRORS:")
            for e in errs:
                print(f"   - {e}")
            all_valid = False
        else:
            print(f"✅ {qid}: PASSED (0 errors)")

    if all_valid:
        print("\n🎉 ALL 10 QUESTIONS (AND-06 to AND-15) PASSED VALIDATION WITH 0 ERRORS!")
    else:
        print("\n⚠️ SOME QUESTIONS HAD VALIDATION ERRORS. PLEASE FIX BEFORE PROCEEDING.")
        sys.exit(1)

if __name__ == "__main__":
    run()

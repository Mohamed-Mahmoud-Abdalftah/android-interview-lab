#!/usr/bin/env python3
"""Canonical updates and Arabic metadata for AND-16 through AND-20."""

TOPIC_AR = "أساسيات أندرويد ودورة الحياة والسياق (Context)"

CANONICAL_DATA = {}
ARABIC_METADATA = {}

# ==============================================================================
# AND-16: How do you protect exported Android components?
# ==============================================================================
CANONICAL_DATA["AND-16"] = {
    "concept_en": """Exported Android components (Activities, Services, BroadcastReceivers, and ContentProviders) cross the Linux process sandbox and allow external applications installed on the device to invoke them. Beginning in Android 12 (API level 31), every component declaring an intent filter must explicitly specify the android:exported attribute. If a component is inadvertently exported, attackers can exploit it to bypass authentication screens, access sensitive internal logic, inject malicious broadcasts, or exfiltrate private database records via ContentProviders.
Securing exported components requires applying defense-in-depth principles across the application architecture. First, developers must adhere to the principle of least privilege by setting android:exported="false" for all internal components. Second, whenever inter-app communication is required within an enterprise ecosystem, endpoints must be protected using custom permissions configured with android:protectionLevel="signature". This guarantees that only applications signed with the identical cryptographic release certificate can bind or communicate with the component. Third, public entry points such as deep link activities must treat all incoming Intent extras as untrusted, validate caller identities using Binder.getCallingUid(), and sanitize all incoming parameters before routing.""",

    "walkthrough_en": """To protect components in production, configure AndroidManifest.xml to lock internal surfaces and protect shared services with signature permissions:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- 1. Define custom signature permission for inter-app communication: -->
    <permission
        android:name="com.example.myapp.permission.SYNC_DATA"
        android:protectionLevel="signature" />

    <application>
        <!-- 2. Internal component explicitly unexported: -->
        <activity
            android:name=".AdminSettingsActivity"
            android:exported="false" />

        <!-- 3. Inter-app service protected by signature permission: -->
        <service
            android:name=".SyncService"
            android:exported="true"
            android:permission="com.example.myapp.permission.SYNC_DATA" />
    </application>
</manifest>
```

Failure scenario: An application exports an account management activity with an intent filter to handle deep links, but fails to check user authentication state. An attacker on the device issues an explicit intent via adb shell am start -n com.example.myapp/.AccountSettingsActivity, directly opening the sensitive management surface and bypassing biometric and PIN authentication gates.""",

    "short_en": """Enforce least privilege by declaring android:exported false on every internal component. When exposing components to partner applications within the same organization, protect them with custom signature-level permissions so only apps signed with your exact release certificate can invoke them. For public endpoints, validate incoming Intent extras, verify caller UID via Binder, and guard against Intent Redirection attacks.""",

    "structured_en": """To begin with, securing Android components starts with the principle of least privilege by explicitly marking all internal Activities, Services, Receivers, and Providers with android:exported="false". This ensures the operating system rejects foreign package invocations at the sandbox boundary before any application code executes.
From an architectural standpoint, when cross-app communication is required across an organization's suite, we protect endpoints with custom permissions using android:protectionLevel="signature". The Android Package Manager validates cryptographic signing certificates during binding and rejects any caller that is not signed with our release keystore.
In production scenarios where public ingress is necessary, such as deep-link gateways, we treat all incoming Intent extras and URIs as untrusted input. We validate parameter formats, sanitize paths to prevent directory traversal, and avoid reflecting incoming intents into internal components to prevent Intent Redirection vulnerabilities.
As for boundary management, for ContentProviders, we avoid broad read and write permissions, exposing data strictly through temporary URI grants using FLAG_GRANT_READ_URI_PERMISSION scoped to specific records.""",

    "deep_senior_en": """At the operating system level, Android component invocation crosses the Binder kernel driver and the ActivityManagerService. When an external application calls startActivity or bindService, the Linux kernel enforces process isolation and attaches the caller's process credentials. Within the target component, developers should never trust caller package names provided inside Intent extras, as these can be forged. Instead, inspecting Binder.getCallingUid() provides an unforgeable identity token, which can then be matched against PackageManager.getPackagesForUid() to reliably verify the caller's identity and signing certificates.
A major architectural vulnerability in enterprise applications is the Confused Deputy problem and Intent Redirection. If an exported component extracts an Intent from its extras and executes startActivity(nestedIntent) without strict verification, a third-party app with zero permissions can force your application to launch unexported, highly privileged private components on its behalf. To prevent this, we reject explicit target components in received intents, parse data into strongly typed domain models, and validate navigation targets against strict allowlists.
Furthermore, handling PendingIntent objects requires extreme discipline. Following Android 12 guidelines, all PendingIntents must be declared with FLAG_IMMUTABLE unless runtime mutation by the receiving system service is strictly required. Leaving a PendingIntent mutable allows a malicious receiving application to call Intent.fillIn(), modifying underlying parameters and hijacking the originating application's identity. In our continuous integration pipelines, we enforce static analysis with Android Lint and custom detekt rules to verify the final merged manifest, guaranteeing that no third-party dependency silently exports unauthenticated components."""
}

ARABIC_METADATA["AND-16"] = {
    "id": "AND-16",
    "questionAr": "كيف تحمي المكونات البرمجية المصدّرة (Exported Components) في أندرويد؟",
    "topicAr": TOPIC_AR,
    "evaluates_ar": """- مراجعة الـ Merged Manifest وتبرير وجود كل نقطة دخول مكشوفة للتطبيقات الأخرى على الجهاز.
- تطبيق أذونات مستوى التوقيع (Signature Permissions) والتحقق من هوية المتصل عبر Binder.
- فحص وتطهير حمولة الـ Intent والـ URIs لتجنب ثغرات الـ Confused Deputy والـ Intent Redirection.""",
    "why_it_matters_ar": "خاصية android:exported بتتحكم في إمكانية تشغيل المكون بواسطة تطبيقات خارجية مثبتة على الجهاز. فلاتر الـ Intent بتحدد التوجيه الضمني فقط، لكن أي تطبيق يقدر يستدعي المكون صراحة عبر Explicit Intent طالما أنه مصدّر. المكونات المكشوفة اللي بتمتلك صلاحيات حساسة ممكن تتحول لأداة في يد تطبيقات خبيثة لتنفيذ عمليات محظورة بالنيابة عنها. وتأمين الـ ContentProviders بيتطلب ضبط صلاحيات وصول دقيقة على مستوى الـ URIs وليس مجرد الاعتماد على عزل التطبيق.",
    "worked_example_ar": """في تطبيق مصرفي، شاشة تأكيد الحوالة المالية لازم تكون exported="false" ومحمية بجلسة دخول نشطة. لو احتجنا فتح إيصال دفع من المتصفح عبر رابط عميق، بنخلي شاشة الاستقبال فقط هي exported="true" وبنتحقق من هوية الرابط، وبنطلب التوكن من الخادم ولا نعتمد أبداً على معرّف الحساب المبعوث في الـ Intent. ولتكامل التطبيق مع تطبيق نقاط بيع لنفس الشركة، بنعرف إذن مخصص بمستوى signature:
```xml
<permission
    android:name="com.bank.permission.PAYMENT_INTEGRATION"
    android:protectionLevel="signature" />
```""",
    "trade_offs_ar": "جعل المكونات exported=\"false\" هو الخيار الأكثر أماناً لكنه يمنع التكاملات الخارجية الشرعية كالمشاركة وتتبع الروابط. استخدام أذونات التوقيع بمستوى signature ممتاز لحزم التطبيقات المشتركة داخل نفس الشركة، لكنه غير صالح للتعامل مع شركاء خارجيين يملكون مفاتيح توقيع مختلفة. والتحقق اليدوي في الـ Runtime يوفر مرونة أعلى لكنه يضيف تعقيداً كبيراً ويتطلب معالجة أخطاء الـ IPC بعناية.",
    "failure_modes_ar": "افتراض أن وجود فلتر محدد يمنع الاستدعاء المباشر للمكون يؤدي لكشف شاشات الدفع أو التحكم لأي استدعاء صريح. ترك PendingIntent بقيمة FLAG_MUTABLE في مكون مصدّر يسمح للغير بالتعديل على مساره الداخلي. دمج مكتبات طرف ثالث تضيف مزودي محتوى (ContentProviders) مصدّرين بدون صلاحيات يفتح ثغرات تسريب بيانات قاعدة البيانات. يتم اكتشاف ذلك عبر فحص الـ Merged Manifest ومحاكاة هجمات الاختراق عبر adb shell am.",
    "production_perspective_ar": "في بيئات الإنتاج، تُخضع الفرق الهندسية الـ Merged Manifest لفحص أمني دوري في كل إصدار لمنع تصدير أي مكون غير مصرح به. يتم تحويل كل معطيات الـ Intent إلى كائنات بيانات غير قابلة للتعديل وتمريرها لطبقة التحقق الأمني. يتم تسجيل محاولات الوصول المرفوضة في سجلات الأمان مع حجب أي بيانات حساسة كرموز المصادقة.",
    "how_to_answer_ar": """- **السبب الأمني:** وضح أن المكونات المصدّرة هي ثغرات محتملة لكسر عزل الـ Sandbox الخاص بنظام أندرويد.
- **طريقة الشرح:** ابدأ بمبدأ الصلاحيات الدنيا exported="false"، ثم اشرح أذونات الـ signature، وأخيراً فحص المدخلات في المكونات العامة.
- **المفاضلات:** قارن بين أذونات التوقيع الداخلية وبين التعامل مع الشركاء الخارجيين.
- **أنماط الفشل:** استشهد بثغرة Intent Redirection وتسريب الـ PendingIntent المتبدل.
- **الحل الإنتاجي:** اذكر فحص الـ Merged Manifest في الـ CI/CD والتحقق من Binder.getCallingUid().""",
    "talking_points_ar": "ناقش كيفية تتبع الـ Calling UID عبر نواة لينكس، وأخطار الـ Confused Deputy في الـ Activities والـ Services، وقواعد إلزام FLAG_IMMUTABLE في أندرويد 12، وكيفية حماية الـ ContentProviders باستخدام grantUriPermissions والتحقق من التوقيع الرقمي للمتصلين عبر PackageManager.",
    "follow_ups_ar": """- **المحاور:** "كيف تتأكد برمجياً من هوية التطبيق الذي استدعى الـ Service الخاصة بك؟"
  **المرشح:** "بنستخدم Binder.getCallingUid() من كود الـ Service لجلب معرّف المستخدم الفعلي من نواة لينكس، وبعدها نستخدم packageManager.getPackagesForUid() للتحقق من أسماء الحزم والشهادات الرقمية الخاصة بها، ونتجنب الاعتماد على أي بيانات مرسلة في الـ Intent."

- **المحاور:** "ما هي ثغرة Intent Redirection وكيف تتجنبها؟"
  **المرشح:** "بتحصل لما تطبيق مصدّر يستقبل Intent من تطبيق خارجي كـ Extra، ويعمل له startActivity بدون فحص. المهاجم ممكن يبعت Intent موجه لشاشة داخلية محمية داخل تطبيقك. لتجنبها، بنرفض توجيه أي Intent خارجي، وبنقرأ البيانات كـ Primitive values أو كائنات محددة بعد فحصها." """,
    "self_check_ar": "تحقق من تعيين android:exported=\"false\" افتراضياً؛ استخدم إذن signature للتكاملات الداخلية؛ افحص الـ Calling UID في الـ Services؛ امنع ثغرات Intent Redirection؛ وافحص الـ Merged Manifest النهائي.",
    "references_ar": """- [App security best practices](https://developer.android.com/privacy-and-security/security-best-practices) — حماية المكونات والـ Intents.
- [Android 12 Safer component exporting](https://developer.android.com/about/versions/12/behavior-changes-12#exported) — إلزام التصريح الصريح لـ exported.

تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.""",
    "quick_answer_ar": "بنحمي المكونات المصدّرة في أندرويد بتطبيق مبدأ أقل الصلاحيات وجعل android:exported=\"false\" هو الوضع الافتراضي لأي مكون داخلي. لو المكون محتاج يتواصل مع تطبيقات تانية تابعة لنفس الشركة، بنحميه بـ Permission مخصص بمستوى signature علشان نضمن إن التطبيقات الموقعة بنفس الـ Keystore بس هي اللي تقدر توصله. وفي المكونات العامة المفتوحة زي الـ Deep Links، بنفحص الـ Calling UID والمدخلات بدقة ونمنع الـ Intent Redirection.",
    "best_answer_ar": """حماية المكونات المصدّرة في أندرويد بتبدأ من فهم إن كل مكون exported="true" بيكسر عزل الـ Sandbox وبيكون متاح لأي تطبيق على نفس الجهاز يستدعيه.
في المعمارية السليمة، بنمشي على استراتيجية دفاعية واضحة: أولاً، أي Activity أو Service أو Receiver مش مخصص للاستخدام الخارجي لازم يتحدد له صراحة android:exported="false". ده بيقفل الباب تماماً قدام أي محاولة اختراق لتجاوز شاشات الـ Login أو لوحات التحكم.
ثانياً، لو عندنا تكامل بين تطبيقات تابعة لنفس المؤسسة، بنعرف Custom Permission ونخلي android:protectionLevel="signature". نظام أندرويد هنا بيتولى فحص الشهادة الرقمية لمفتاح التوقيع بتاع التطبيق المتصل عبر PackageManagerService، ولو مش موقع بنفس مفتاح الـ Release بتاعنا بيترفض طلبه فوراً.
ثالثاً، لو المكون لازم يكون عام زي شاشات استقبال الروابط، بنعامل كل الـ Intent Extras كبيانات غير موثوقة تماماً؛ بنعمل Validation صارم للمدخلات، وبنتأكد من صلاحيات المستخدم وجلسة تسجيل الدخول قبل عرض أي بيانات حساسة، وبنمنع إعادة توجيه الـ Intent الداخلي لحماية التطبيق من ثغرة Confused Deputy.""",
    "deep_answer_ar": """على مستوى نواة لينكس والـ Android Framework، المكونات المصدّرة بتخضع لإدارة الـ IPC عبر الـ Binder Driver والـ ActivityManagerService. لما تطبيق خارجي بيطلب تشغيل Activity أو الربط بـ Service، النواة بتسجل الـ Linux UID الخاص بالعملية الطالبة، والنظام بيوفر ده برمجياً عن طريق Binder.getCallingUid().
الخطأ الشائع عند مهندسين كتير هو الاعتماد على اسم الحزمة المبعوث في الـ Intent extras أو التحقق السطحي؛ الطريقة الوحيدة الآمنة والمضمونة من الـ OS هي التحقق من Binder.getCallingUid() ومطابقته مع الـ PackageManager للتأكد من هوية المتصل الحقيقية.
من أخطر الثغرات اللي بنشوفها في الـ Code Audits ثغرة Intent Redirection أو الـ Confused Deputy؛ دي بتحصل لما المكون المصدّر يستقبل Intent كامل كـ Extra من تطبيق غريب وينفذ له startActivity مباشرة من غير تطهير. المهاجم هنا بيستغل صلاحيات تطبيقك لتشغيل شاشات داخلية خاصة مفروض تكون محمية. علشان كده بنمنع تمرير الـ Explicit Intents ونحول البيانات لـ Domain Models مجردة.
بالإضافة لكده، مع الـ PendingIntents بنلزم استخدام FLAG_IMMUTABLE في أندرويد 12 والإصدارات الأحدث؛ لأن ترك الـ PendingIntent كـ FLAG_MUTABLE بيسمح للتطبيقات الخبيثة باستغلال Intent.fillIn() وتغيير مسار التنفيذ واستغلال هوية تطبيقك. وفي خطوط الـ CI/CD، بنشغل تحليلات أمنية على الـ Merged Manifest للتأكد إن مفيش أي مكتبة خارجية فتحت Exported Component بدون علمنا."""
}

# ==============================================================================
# AND-17: How should you register/unregister lifecycle-dependent listeners?
# ==============================================================================
CANONICAL_DATA["AND-17"] = {
    "concept_en": """In Android development, lifecycle-dependent listeners—including system location listeners, motion sensors, connectivity broadcast receivers, Bluetooth scanners, and reactive state flows—retain callbacks in memory. If a listener is registered without an unregistration mechanism tied to the host lifecycle, the callback retains a reference to the Activity, Fragment, or View hierarchy, preventing garbage collection and causing substantial memory leaks. Furthermore, continuous background polling of hardware sensors rapidly drains device battery and triggers thermal throttling.
To prevent these regressions, listener lifecycles must strictly mirror component lifecycles. Traditional implementations scattered manual registration calls across Activity callbacks. Modern architecture relies on DefaultLifecycleObserver from Jetpack Lifecycle, which encapsulates registration and unregistration logic within self-contained classes. For reactive streams, coroutine collections should be governed by repeatOnLifecycle, ensuring that subscriptions automatically cancel when the UI is hidden and restart when it becomes visible. In Fragment architectures, UI-bound listeners must observe viewLifecycleOwner to align with the destruction of the View hierarchy.""",

    "walkthrough_en": """A self-contained lifecycle observer decouples sensor registration from the Activity, handling subscription symmetry internally:

```kotlin
class LocationTracker(
    private val context: Context,
    private val onLocationChanged: (Location) -> Unit
) : DefaultLifecycleObserver {

    override fun onStart(owner: LifecycleOwner) {
        startTracking()
    }

    override fun onStop(owner: LifecycleOwner) {
        stopTracking()
    }

    private fun startTracking() {
        // Register location manager updates
    }

    private fun stopTracking() {
        // Remove location updates to conserve power
    }
}
```

In the host Activity or Fragment:

```kotlin
class MapActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val tracker = LocationTracker(this) { location -> updateMap(location) }
        lifecycle.addObserver(tracker)
    }
}
```

Failure scenario: A developer registers a sensor listener in onStart but removes it inside onDestroy. When the user repeatedly opens and closes other applications, the Activity cycles between onStart and onStop. Because onDestroy is never invoked during temporary backgrounding, new listeners accumulate on every restart, resulting in duplicated callback executions and severe battery drain.""",

    "short_en": """Register and unregister lifecycle-dependent listeners with strict symmetry matching resource requirements: use onStart and onStop for visibility, onResume and onPause for exclusive hardware like cameras, and onCreate and onDestroy for process allocations. Encapsulate listeners using DefaultLifecycleObserver or repeatOnLifecycle rather than cluttering Activity callbacks. In Fragments, always bind UI listeners to viewLifecycleOwner.""",

    "structured_en": """To begin with, managing lifecycle-dependent listeners requires strict symmetry across lifecycle boundaries. Every registration must pair with an equivalent unregistration event: onStart pairs with onStop for visibility-dependent events, while onResume pairs with onPause for exclusive hardware access such as camera capture and high-frequency motion sensors.
From an architectural standpoint, rather than cluttering Activities with boilerplate registration calls, we encapsulate listeners using DefaultLifecycleObserver. By attaching the observer directly to the host's LifecycleOwner, the component manages its own subscription lifecycle automatically, decoupling business logic from framework callbacks.
In production scenarios involving asynchronous data streaming, we use repeatOnLifecycle or flowWithLifecycle for Coroutine collections. This suspends upstream data flow when the app is placed in the background, preventing unnecessary background processing and eliminating crashes caused by updating destroyed views.
As for boundary management, in Fragment implementations, we bind all UI-related observers and ViewBinding references to viewLifecycleOwner. This prevents memory leaks when the Fragment's view hierarchy is destroyed in the back stack while the Fragment instance remains retained in memory.""",

    "deep_senior_en": """Under the hood, registering a callback with a system service such as SensorManager or LocationManager passes an interface implementation across a Binder IPC interface or registers a local listener inside the system service's native client stub. If the host Activity fails to unregister the listener before destruction, the system service maintains a strong reference to the listener stub, which in turn holds an implicit reference to the enclosing Activity class. The ART garbage collector cannot reclaim the Activity, leaking its entire View hierarchy, Bitmaps, and ContextImpl structures in the Java heap.
From a threading and state machine perspective, DefaultLifecycleObserver methods are invoked sequentially on the main thread via the LifecycleRegistry. When using lifecycleScope.launch alone without repeatOnLifecycle, a coroutine continues collecting flow emissions even after onStop, consuming CPU cycles and potentially crashing if it interacts with detached UI components. Calling repeatOnLifecycle(Lifecycle.State.STARTED) launches a new child coroutine in onStart and cancels the underlying Job immediately when the state transitions to onStop. When the user navigates back to the screen, a new coroutine is spawned, collecting fresh emissions seamlessly.
In enterprise architectures, we audit listener lifecycles by integrating LeakCanary into debug builds to detect lingering observers. For hardware-intensive features like camera and audio processing, we enforce onResume and onPause bounds to release exclusive device hardware locks immediately when the window loses focus, ensuring reliable multi-window support and preventing system-level hardware lock contention across concurrent applications."""
}

ARABIC_METADATA["AND-17"] = {
    "id": "AND-17",
    "questionAr": "كيف يجب تسجيل وإلغاء تسجيل المستمعين (Listeners) المرتبطين بدورة الحياة؟",
    "topicAr": TOPIC_AR,
    "evaluates_ar": """- مطابقة تسجيل المستمع مع حدود دورة الحياة المناسبة للمورد وظهور الواجهة.
- إزالة دوال الاستدعاء (Callbacks) من مالكها الدقيق والتمييز بين دورة حياة كائن الـ Fragment وواجهته.
- تفادي تسريبات الذاكرة وتكرار استهلاك المعالج الناتج عن المستمعين المتروكين دون إلغاء.""",
    "why_it_matters_ar": "مصدر الأحداث بيحتفظ بمرجع للـ Callbacks لحد ما يتم حذفها صراحة أو تنتهي دورة حياته. مستمعو حساسات النظام أو مستقبلات البث أو مراقبو تدفقات البيانات ممكن يحبسوا الـ Activity أو الـ View في الذاكرة بعد تدميرها لو ماتلغاش تسجيلهم. الاستهلاك المستمر لحساسات الحركة أو الموقع في الخلفية بيستنزف البطارية ويسخن الجهاز، وتكرار التسجيل بيضاعف تنفيذ العمليات مع كل فتح للشاشة.",
    "worked_example_ar": """بناء كائن تتبع موقع ذاتي الإدارة يعتمد على DefaultLifecycleObserver:
```kotlin
class LocationTracker(
    private val context: Context,
    private val onLocationChanged: (Location) -> Unit
) : DefaultLifecycleObserver {

    override fun onStart(owner: LifecycleOwner) {
        // بدء طلب تحديثات الموقع عند ظهور الشاشة
    }

    override fun onStop(owner: LifecycleOwner) {
        // إيقاف التحديثات فور اختفاء الشاشة لتوفير الطاقة
    }
}
```
وفي الشاشة بنكتفي بربطه: `lifecycle.addObserver(LocationTracker(this, ::onLocationChanged))`.""",
    "trade_offs_ar": "حدود Start/Stop هي الأنسب لمعظم واجهات المستخدم وتدفقات البيانات، بينما الموارد الحصرية زي الكاميرا أو الجيروسكوب عالي التردد بتتطلب حدود Resume/Pause لتحرير العتاد بمجرد فقدان التركيز في الشاشات المتعددة. استخدام DefaultLifecycleObserver بيفصل منطق التسجيل عن كود الـ Activity لكنه بيتطلب تمرير Context نظيف، واستخدام repeatOnLifecycle للكوروتينات بيوفر حماية تلقائية لكنه يعيد تشغيل جمع البيانات من الصفر في كل مرة.",
    "failure_modes_ar": "تسجيل المستمع في onStart وإلغاؤه في onDestroy يسبب تضاعف المستمعين في كل مرة تروح فيها الشاشة للخلفية وترجع. مراقبة البيانات في الـ Fragment باستخدام دورة حياة الـ Fragment نفسه بدلاً من viewLifecycleOwner يسرب شجرة الـ Views في الـ Backstack. ترك مستقبلات البث مسجلة يرمي خطأ ReceiverNotRegisteredException أو يسرب الـ Context. يتم كشف هذه المشاكل عبر LeakCanary واختبارات تكرار التدوير.",
    "production_perspective_ar": "في التطبيقات الضخمة، بنحظر كتابة كود التسجيل اليدوي داخل دوال الـ Activity المباشرة، وبنلزم استخدام DefaultLifecycleObserver أو ربط التدفقات بـ repeatOnLifecycle(STARTED). بنفحص تسريبات الذاكرة آلياً في الـ CI، وبنتأكد من تحرير حساسات الـ GPS والمستمعين فور انتقال التطبيق لـ onStop لتقليل استهلاك البطارية في الخلفية.",
    "how_to_answer_ar": """- **السبب الهندسي:** وضح أن المستمعين غير الملغيين يحبسون الشاشات في الذاكرة ويستنزفون بطارية الهاتف.
- **طريقة الشرح:** قسم حدود السيمترية (Create/Destroy للموارد الدائمة، Start/Stop للرؤية، Resume/Pause للموارد الحصرية).
- **المفاضلات:** اشرح ميزة DefaultLifecycleObserver في تنظيف كود الشاشات وفصل المسؤوليات.
- **أنماط الفشل:** اذكر خطأ التسجيل في onStart والإلغاء في onDestroy وتكرار الـ Callbacks.
- **الحل الإنتاجي:** استشهد بـ repeatOnLifecycle مع تدفقات StateFlow وتصفير المراجع في الـ Fragment.""",
    "talking_points_ar": "ناقش كيف تحتفظ خدمات النظام بمراجع الـ IPC في الـ Binder Stubs، وآلية عمل LifecycleRegistry في استدعاء المراقبين بالتسلسل، والفارق الجوهري بين lifecycleScope.launch العادي وبين repeatOnLifecycle، وكيف يدير viewLifecycleOwner تدمير الواجهة في الـ Fragment Backstack.",
    "follow_ups_ar": """- **المحاور:** "إيه الفرق بين التسجيل في onStart والتسجيل في onResume؟"
  **المرشح:** "التسجيل في onStart مرتبط بالرؤية (Visibility)؛ الشاشة بتكون ظاهرة للمستخدم ومحتاجة تعرض البيانات حتى لو مش واخدة التركيز زي وضع Multi-Window. أما التسجيل في onResume فمرتبط بـ Interactive Focus والموارد الحصرية اللي مينفعش تطبيقين يستخدموها في نفس الوقت زي الكاميرا والمايكروفون."

- **المحاور:** "ليه بنفضل repeatOnLifecycle على launchWhenStarted القديمة؟"
  **المرشح:** "لأن launchWhenStarted كانت بتعمل Pause للكوروتين في الخلفية بس بتسيب الـ Producer شغال في الذاكرة يبعت بيانات، وده كان بيسرب الذاكرة ويستهلك موارد بدون داعٍ. أما repeatOnLifecycle فبتعمل Cancel حقيقي للـ Job في onStop وتعمل Restart لكوروتين جديد تماماً في onStart." """,
    "self_check_ar": "حدد السيمترية الصحيحة لكل مرحلة دورة حياة؛ استخدم DefaultLifecycleObserver لتغليف المستمعين؛ اربط واجهات الـ Fragment بـ viewLifecycleOwner؛ واشرح عمل repeatOnLifecycle.",
    "references_ar": """- [Lifecycle-aware components](https://developer.android.com/topic/libraries/architecture/lifecycle) — معمارية المكونات المدركة لدورة الحياة.
- [RepeatOnLifecycle API](https://developer.android.com/reference/kotlin/androidx/lifecycle/package-summary#repeatOnLifecycle) — التجميع الآمن للتدفقات.

تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.""",
    "quick_answer_ar": "تسجيل وإلغاء تسجيل الـ Listeners المرتبطة بدورة الحياة لازم يتبع سيمترية دقيقة: اللي تسجله في onStart تلغيه في onStop للواجهات المرئية، واللي تسجله في onResume تلغيه في onPause للموارد الحصرية زي الكاميرا وحساسات الحركة. والأفضل معمارياً تغليف المستمع داخل DefaultLifecycleObserver أو استخدام repeatOnLifecycle للكوروتينات، وربط مستمعي الواجهة في الـ Fragment بـ viewLifecycleOwner.",
    "best_answer_ar": """القاعدة الذهبية في إدارة الـ Listeners هي السيمترية التامة في حدود دورة الحياة علشان نتفادى تسريبات الذاكرة واستنزاف البطارية.
كل عملية تسجيل لازم تقابلها عملية إلغاء في نفس المستوى: لو بتسجل في onCreate بتلغي في onDestroy للموارد اللي بتعيش بعمر الشاشة كلها؛ ولو بتسجل في onStart بتلغي في onStop للموارد المرتبطة برؤية الشاشة زي الـ Location العادي؛ ولو بتسجل في onResume بتلغي في onPause للموارد الحصرية زي الكاميرا والـ GPS عالي الدقة.
معمارياً، مبنكتبش كود التسجيل والإلغاء مبعثر جوه الـ Callbacks بتاعة الـ Activity؛ بنعمل كلاس منفصل يورث من DefaultLifecycleObserver ونضيفه للـ lifecycle.addObserver. ده بيخلي المكون يدير نفسه بنفسه ويسهل اختباره بشكل معزول.
وبالنسبة للـ Coroutines والـ Flows، بنعتمد على repeatOnLifecycle مع حالة STARTED اللي بتلغي الـ Job تلقائياً أول ما الشاشة تختفي وترجع تشغلها أول ما تظهر، وده بيوفر معالجة آمنة تماماً للموارد ويمنع تحديث واجهات مدمرة.""",
    "deep_answer_ar": """على مستوى الـ Android Runtime وإدارة الذاكرة، لما بتسجل Listener مع System Service زي الـ SensorManager أو الـ LocationManager، الخدمة دي بتحتفظ بمرجع للـ Listener في الـ Binder IPC layer. لو الشاشة اتدمرت وأنت ملغيتش التسجيل، الـ System Service هتفضل ماسكة مرجع قوي للـ Callback، والـ Callback ماسك الـ Activity، والـ Activity ماسكة شجرة الـ Views والـ Bitmaps وموارد الـ Window كلها، وده بيعمل تسريب ذاكرة كارثي بيمنع الـ GC من تحرير الميجابايتس دي.
من ناحية الـ Lifecycle State Machine، مكتبة Jetpack Lifecycle بتقدملنا repeatOnLifecycle كحل جذري لمعضلة جمع تدفقات الـ Flow. لو استخدمت lifecycleScope.launch العادي، الكوروتين هيفضل يجمع بيانات حتى والتطبيق في الـ Background، وده بيستهلك الـ CPU والبطارية، وممكن يرمي Crash لو حاول يعدل على View ميتة. الـ repeatOnLifecycle مع حالة STARTED بتعمل Cancel للـ Job فوراً عند الانتقال لـ onStop، وبتعمل Restart لكوروتين جديد عند العودة لـ onStart.
وفي حالة الـ Fragments، لازم نكون حذرين جداً ونربط الـ Observers بـ viewLifecycleOwner مش بالـ Fragment نفسه؛ لأن كائن الـ Fragment بيفضل عايش في الـ Backstack بعد ما الـ View تتدمر في onDestroyView. لو سجلت Observer على مستوى الـ Fragment، هيتكرر التسجيل مع كل رجوع من الـ Backstack وتتضاعف الـ Callbacks وتتسرب الذاكرة بالكامل."""
}

# ==============================================================================
# AND-18: How do multi-window, rotation, and background/foreground transitions affect state?
# ==============================================================================
CANONICAL_DATA["AND-18"] = {
    "concept_en": """State preservation in Android is driven by three distinct system-level triggers: configuration changes, multi-window visibility transitions, and background process death.
During configuration changes (such as screen rotation, folding/unfolding foldable displays, or system locale updates), the operating system destroys and completely recreates the Activity instance to reload optimized resources. In contrast, multi-window mode (introduced in Android 7.0 and refined with multi-resume in Android 10) decouples window visibility from window focus. In multi-window or picture-in-picture mode, an Activity may remain visible in the STARTED state while another window holds user focus, meaning background transitions must not immediately halt rendering or media playback. Finally, when an application is moved to the background, it transitions through onPause to onStop. Under severe memory pressure, the Linux Low Memory Killer terminates the cached process without warning. Preserving application continuity requires a multi-tiered state management architecture: ephemeral UI state stored in SavedStateHandle, presentation logic retained across configuration changes in a ViewModel, and durable business state persisted immediately in a local Room database.""",

    "walkthrough_en": """A video player implementation must adapt its playback lifecycle to multi-window mode, continuing playback while visible in onStart rather than pausing prematurely in onPause:

```kotlin
class VideoPlayerActivity : AppCompatActivity() {
    private var player: ExoPlayer? = null

    override fun onStart() {
        super.onStart()
        // Initialize player when visible in multi-window mode:
        initializePlayer()
    }

    override fun onResume() {
        super.onResume()
        // Resume full interactive controls
    }

    override fun onPause() {
        super.onPause()
        // Do not release player here in multi-window mode!
    }

    override fun onStop() {
        super.onStop()
        // Release hardware decoding resources when completely hidden:
        releasePlayer()
    }

    private fun initializePlayer() { /* ExoPlayer setup */ }
    private fun releasePlayer() {
        player?.release()
        player = null
    }
}
```

Failure scenario: A banking transfer screen retains the transfer amount only inside a ViewModel. When the user backgrounds the app to copy a verification code, the operating system kills the process. When the user returns, the system recreates the Activity, but the ViewModel is re-instantiated with default null values, wiping out the uncommitted form data and causing severe user frustration.""",

    "short_en": """Manage state across three distinct layers: use ViewModel for transient configuration changes like rotation; use SavedStateHandle and onSaveInstanceState for lightweight navigation state surviving background process death; and persist durable business data immediately in Room or DataStore. In multi-window mode, handle visibility in onStart and onStop rather than onResume and onPause.""",

    "structured_en": """To begin with, handling state transitions requires separating configuration recreation from background process termination. Rotation destroys and recreates the Activity window to reload layout resources, whereas moving an app to the background transitions the process to a cached state where the Linux kernel can kill it silently at any moment.
From an architectural standpoint, we structure state management into three resilient tiers. The ViewModel retains complex presentation state across configuration changes like rotation and screen folding. For surviving background process death, lightweight UI parameters and navigation IDs are preserved in SavedStateHandle via onSaveInstanceState.
In production scenarios involving multi-window and picture-in-picture modes on tablets and foldables, visibility is decoupled from touch focus. An Activity in split-screen remains visible even when unfocused, so continuous operations like video playback must be bound to onStart and onStop rather than prematurely suspended in onPause.
As for boundary management, critical user actions and financial transactions must be persisted immediately to local durable storage like Room or DataStore rather than relying on late lifecycle callbacks.""",

    "deep_senior_en": """Under the hood, configuration changes cause the ActivityThread to execute handleRelaunchActivity, invoking onSaveInstanceState, destroying the current Activity instance via onDestroy, and instantiating a fresh one. The existing ViewModelStore is preserved across this destruction by the NonConfigurationInstances holder maintained by the Android framework. However, during background process death, the entire Linux process is terminated by the Low Memory Killer daemon (lmkd) via a SIGKILL signal. The ViewModelStore and all in-memory static singletons are entirely obliterated.
When the user subsequently restores the task from the Overview screen, the system launches a brand-new process, executes Application.onCreate(), and passes the parcelized savedInstanceState Bundle back to Activity.onCreate(). If an application relies solely on ViewModel properties or static caches without saving state in SavedStateHandle, it will throw a NullPointerException or reset to a broken initial state upon restoration.
Regarding multi-window mechanics, Android 7.0 introduced multi-window where only the top focused app was in RESUMED, while visible side-by-side apps were kept in PAUSED. Android 10 introduced multi-resume, allowing all visible activities in split-screen or multi-display environments to remain in RESUMED if their manifests permit. Stopping video playback or location updates in onPause breaks the user experience in multi-window scenarios; resources tied to visual rendering must remain active throughout the STARTED state and only shut down when transitioning to STOPPED.
Furthermore, developers must respect the 1MB IPC transaction limit when writing to onSaveInstanceState. The saved instance state bundle is marshaled across Binder to the system server process (ActivityTaskManagerService). Exceeding this buffer by attempting to store large bitmaps or extensive JSON lists triggers a TransactionTooLargeException, crashing the process during state preservation."""
}

ARABIC_METADATA["AND-18"] = {
    "id": "AND-18",
    "questionAr": "كيف تؤثر الشاشات المتعددة (Multi-Window) والتدوير وتغيرات الخلفية/الواجهة على حالة التطبيق؟",
    "topicAr": TOPIC_AR,
    "evaluates_ar": """- التمييز بين إعادة البناء الناتجة عن تدوير الجهاز وبين موت العملية في الخلفية.
- توزيع الحالة على طبقاتها المناسبة: حالة الواجهة المؤقتة، وحالة العرض المحتفظ بها، والبيانات الدائمة.
- فهم انفصال الرؤية عن بؤرة التركيز في وضع Multi-Window وضبط دورات الميديا بناءً على ذلك.""",
    "why_it_matters_ar": "تدوير الشاشة بيعيد تحميل الموارد الرسومية عن طريق تدمير الشاشة وإعادة بنائها، بينما وضع الشاشات المتعددة بيخلي التطبيق ظاهراً للمستخدم في وضع onStart حتى لو كان التركيز التفاعلي على تطبيق تاني. الانتقال للخلفية بينقل العملية لقائمة الـ Cached Processes، والنظام ممكن يقتلها في أي لحظة عند نقص الذاكرة. الحفاظ على تجربة المستخدم بيتطلب فصل الحالة لتلات مستويات واضحة: ViewModel للتدوير، SavedStateHandle للنجاة من موت العملية، وقاعدة بيانات Room للبيانات الحقيقية.",
    "worked_example_ar": """في مشغل الفيديو، إدارة الموارد في وضع Multi-Window بتعتمد على onStart و onStop:
```kotlin
class VideoPlayerActivity : AppCompatActivity() {
    private var player: ExoPlayer? = null

    override fun onStart() {
        super.onStart()
        // تهيئة المشغل عند الرؤية حتى في وضع الشاشات المتعددة
        player = ExoPlayer.Builder(this).build()
    }

    override fun onStop() {
        super.onStop()
        // تحرير مفكك التشفير وعتاد الفيديو عند الاختفاء الكامل
        player?.release()
        player = null
    }
}
```
وفي شاشات الإدخال، بنحفظ معرّف المسودة في SavedStateHandle لضمان استعادته بعد موت العملية.""",
    "trade_offs_ar": "حفظ كل البيانات في onSaveInstanceState بيعرض التطبيق لخطأ TransactionTooLargeException لو زادت البيانات عن 1MB؛ الأفضل حفظ المعرّفات الخفيفة فقط. الـ ViewModel ممتاز لسرعة الأداء أثناء التدوير لكنه بيموت تماماً عند قتل العملية. التخزين الدائم في Room آمن بنسبة 100% لكنه بيتطلب عمليات إدخال وإخراج (I/O) غير متزامنة، وعلشان كده بنمزج التلات مستويات معاً.",
    "failure_modes_ar": "إيقاف الفيديو في onPause يؤدي لتجميد الصورة في وضع Multi-Window بينما المستخدم يتفاعل مع تطبيق آخر بجانبه. الاعتماد على كاش الذاكرة في الـ ViewModel فقط يفقد المستخدم كل البيانات المدخلة عند العودة للتطبيق بعد ساعات من الخلفية. حفظ Bitmaps أو كائنات ضخمة في Bundle يرمي خطأ TransactionTooLargeException. يتم التحقق عبر تفعيل خيار Don't keep activities في إعدادات المطور.",
    "production_perspective_ar": "في تطبيقات الإنتاج العالمية، بنختبر استعادة الحالة آلياً بمحاكاة موت العملية عبر adb shell am kill. بنحفظ معرّفات الشاشات في SavedStateHandle، وبنخلي الـ ViewModel يطلب البيانات من قاعدة بيانات Room كـ Single Source of Truth. بنراقب استهلاك الذاكرة في الشاشات القابلة للطي ونتأكد من عدم إعادة تحميل بيانات الشبكة عند مجرد تدوير الجهاز.",
    "how_to_answer_ar": """- **السبب المعماري:** وضح الفروق الجوهرية بين التدوير وانفصال الرؤية عن التركيز وموت العملية بواسطة الـ LMK.
- **طريقة الشرح:** اشرح المستويات الثلاثة لإدارة الحالة (ViewModel للتدوير، SavedStateHandle لموت العملية، Room للبيانات الدائمة).
- **المفاضلات:** بين حدود حجم الـ Bundle المشترك في Binder مقابل سرعة الـ ViewModel.
- **أنماط الفشل:** استشهد بخطأ إيقاف الفيديو في onPause وفقدان البيانات بعد قتل العملية في الخلفية.
- **الحل الإنتاجي:** وضح استخدام SavedStateHandle مع Kotlin StateFlow واختبار الـ Multi-resume.""",
    "talking_points_ar": "ناقش دور NonConfigurationInstances في نجاة ViewModelStore أثناء التدوير، وكيف أتاح أندرويد 10 خاصية Multi-resume لتشغيل عدة شاشات في RESUMED بالتوازي، وحدود الـ 1MB الخاصة بالـ Binder Transaction، وكيف يتعامل الـ LMK مع الـ oom_score_adj للعمليات في الخلفية.",
    "follow_ups_ar": """- **المحاور:** "ليه بنحذر من حفظ كائنات كبيرة في onSaveInstanceState؟"
  **المرشح:** "لأن بيانات Bundle المحفوظة في onSaveInstanceState بتتبعت عبر Binder لعملية الـ System Server. وقناة الـ Binder لها Buffer مشترك بحجم 1 ميجابايت فقط لكل العمليات الجارية؛ لو حاولت تحفظ لستة صور أو بيانات ضخمة، التطبيق هيرمي TransactionTooLargeException ويكرش فوراً."

- **المحاور:** "ما هو الـ Multi-resume الذي تم تقديمه في أندرويد 10؟"
  **المرشح:** "قبل أندرويد 10، كان التطبيق اللي واخد التفاعل فقط هو اللي بيكون في RESUMED والتطبيق التاني في PAUSED رغم إنه ظاهر. أندرويد 10 أتاح تشغيل كل التطبيقات الظاهرة في وضع الشاشات المتعددة في حالة RESUMED في نفس الوقت، وده بيسمح بتشغيل أكثر من تطبيق تفاعلي معاً." """,
    "self_check_ar": "فرّق بدقة بين دور ViewModel و SavedStateHandle؛ حدد دورة تشغيل الميديا في Multi-Window؛ تجنب تخزين بيانات ضخمة في Bundle؛ واختبر التطبيق ضد محاكاة موت العملية.",
    "references_ar": """- [Restore UI state](https://developer.android.com/topic/libraries/architecture/saving-states) — استراتيجيات حفظ واستعادة حالة الواجهة.
- [Multi-window support](https://developer.android.com/guide/topics/ui/multi-window) — دعم الشاشات المتعددة والـ Multi-resume.

تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.""",
    "quick_answer_ar": "إدارة الحالة في أندرويد بتعتمد على تلات مستويات منفصلة: الـ ViewModel للاحتفاظ بحالة الشاشة عبر تدوير الجهاز (Rotation)؛ والـ SavedStateHandle لحفظ معرّفات التنقل والمدخلات الخفيفة للنجاة من موت العملية في الخلفية (Process Death)؛ وقاعدة بيانات Room لحفظ البيانات الحقيقية فوراً. وفي وضع الشاشات المتعددة (Multi-Window)، ربط الموارد بيكون بـ onStart و onStop لأن الشاشة بتفضل مرئية حتى لو فقدت التركيز.",
    "best_answer_ar": """التعامل مع تغيرات الحالة بيتطلب فهم الفرق الجوهري بين التدوير، والـ Multi-Window، وموت العملية في الخلفية.
عند تدوير الشاشة (Rotation) أو فرد الأجهزة القابلة للطي، النظام بيدمر الـ Activity ويعيد بناءها لتحميل الموارد المناسبة للوضع الجديد، وحالة الشاشة بتنجو هنا عن طريق الـ ViewModel اللي بيفضل محتفظ ببياناته في الـ ViewModelStore.
أما في وضع الـ Multi-Window والـ Split-Screen، فالرؤية بتنفصل عن التركيز التفاعلي؛ يعني التطبيق ممكن يكون ظاهر وشغال بس مش واخد الـ Focus، وعلشان كده تشغيل الفيديو أو تحديث الخريطة لازم يرتبط بـ onStart و onStop، ومينفعش نوقفه في onPause.
والحالة الأخطر هي لما المستخدم يخرج من التطبيق؛ التطبيق بيروح لـ onStop والعملية بتنزل لقائمة الـ Cached Processes، والنظام ممكن يقتلها في أي لحظة لتوفير الذاكرة. لما المستخدم يرجع، النظام بينشئ Process جديدة والـ ViewModel بيموت، والمنقذ الوحيد هنا هو SavedStateHandle لاستعادة معرّفات الشاشة، مع قراءة البيانات المستقرة مباشرة من قاعدة بيانات Room.""",
    "deep_answer_ar": """على مستوى الـ OS والـ Runtime، أندرويد بيفرق تماماً بين إعادة البناء الناتجة عن الـ Configuration Change وبين إعادة الإحياء بعد الـ Process Death.
في حالة الـ Rotation، الـ ActivityThread بيمر بـ onDestroy ثم onCreate، لكن الـ NonConfigurationInstances بتنقل الـ ViewModelStore القديم للشاشة الجديدة، فبيفضل الـ ViewModel والبيانات اللي جواه سالمة تماماً في الـ Heap.
لكن لما التطبيق يروح للـ Background، الـ Low Memory Killer daemon بيراقب الـ oom_score_adj للعملية، ولما الذاكرة تضيق، بيبعت إشارة SIGKILL تنهي العملية بكل كائنات الـ Heap والـ Singletons والـ ViewModels. لما المستخدم يرجع يفتح التطبيق من شاشة الـ Recents، نظام التشغيل بيبدأ العملية من الصفر، وبيستدعي Application.onCreate ثم Activity.onCreate ممرراً الـ Bundle اللي اتحفظ وقت onSaveInstanceState. لو التطبيق معتمد على كاش في الذاكرة بدل SavedStateHandle و Room، هيحصل NullPointerException فوراً.
وفيما يخص الـ Multi-Window، أندرويد 10 قدم الـ Multi-resume، وده بيسمح لكل الشاشات الظاهرة في الـ Split-Screen إنها تكون في حالة RESUMED. الخطأ الشائع هو إيقاف مشغل الميديا في onPause؛ لأن في الـ Multi-Window المستخدم بيكون بيتفرج على الفيديو وهو بيقرأ مقال في الشاشة التانية، فالإيقاف لازم يتأجل لحد onStop لما الشاشة تختفي كلياً.
ولا يغيب عن البال قيد الـ Binder Buffer؛ حفظ بيانات ضخمة أو Bitmaps في onSaveInstanceState هيصطدم بحد الـ 1MB المشترك للـ Transaction، ويرمي TransactionTooLargeException ويكرش التطبيق لحظة خروجه للخلفية."""
}

# ==============================================================================
# AND-19: What are foreground services and notification requirements at a high level?
# ==============================================================================
CANONICAL_DATA["AND-19"] = {
    "concept_en": """A Foreground Service is an Android application component designed to execute operations that are actively noticeable to the user and must not be interrupted by the operating system. Unlike background services, which are heavily throttled and subject to aggressive Low Memory Killer reclamation, a foreground service elevates the hosting process's priority to the perceptible tier (oom_adj foreground priority). To ensure complete transparency and user awareness, the operating system strictly mandates that a foreground service must display an ongoing, non-dismissible system notification throughout its active execution.
Beginning with Android 8.0 (API 26), apps targeting modern SDKs cannot start background services arbitrarily while in the background. If started via startForegroundService(), the service must invoke startForeground() within five seconds, or the system crashes the process with a ForegroundServiceDidNotStartInTimeException. Starting in Android 14 (API 34), Google introduced strict policy and platform enforcement: every foreground service must declare an explicit android:foregroundServiceType in the manifest (such as location, mediaPlayback, or dataSync) accompanied by dedicated runtime permissions. Modern Android architecture dictates using WorkManager for persistent, deferrable background tasks, reserving foreground services strictly for real-time user-facing tasks like active audio playback, turn-by-turn navigation, and ongoing workouts.""",

    "walkthrough_en": """Implementing an Android 14 compliant foreground service requires declaring the specific service type and matching permissions in AndroidManifest.xml:

```xml
<!-- In AndroidManifest.xml: -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

<service
    android:name=".TrackingService"
    android:foregroundServiceType="location"
    android:exported="false" />
```

In the Service implementation:

```kotlin
class TrackingService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Active Workout Tracking")
            .setContentText("Tracking route via GPS...")
            .setSmallIcon(R.drawable.ic_run)
            .setOngoing(true)
            .build()

        // Android 14+ requires explicit type parameter:
        ServiceCompat.startForeground(
            this,
            NOTIFICATION_ID,
            notification,
            ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION
        )

        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

Failure scenario: A developer calls context.startForegroundService() when a push notification arrives while the app is in the background, but attempts to perform a slow asynchronous network call before calling startForeground(). Because the 5-second window expires before the notification is posted, the operating system abruptly crashes the app with a ForegroundServiceDidNotStartInTimeException.""",

    "short_en": """A foreground service performs user-noticeable ongoing work while elevating process priority to prevent system termination. It mandates an ongoing, visible notification and must call startForeground within five seconds of creation. Under Android 14+, you must declare a specific foregroundServiceType in the manifest and acquire matching runtime permissions. Reserve foreground services for active real-time operations, using WorkManager for deferrable tasks.""",

    "structured_en": """To begin with, a Foreground Service is designed for operations that are actively noticeable to the user, elevating the process priority to protect it from termination by the Low Memory Killer. The operating system mandates an ongoing, persistent notification so the user remains fully aware of background resource consumption like battery and location tracking.
From an architectural standpoint, modern Android releases have placed strict constraints around service execution. In Android 8.0, starting a foreground service via startForegroundService requires invoking startForeground within five seconds, failing which the OS throws a fatal ForegroundServiceDidNotStartInTimeException. Android 12 further restricted starting foreground services from the background, permitting it only under explicit exemptions such as high-priority FCM messages.
In production scenarios targeting Android 14 and above, every foreground service must declare an explicit android:foregroundServiceType in the manifest, accompanied by dedicated runtime permissions like FOREGROUND_SERVICE_LOCATION. Calling startForeground without matching manifest types results in an immediate SecurityException.
As for boundary management, foreground services should never be used for general background processing or data syncing. We delegate all deferrable, guaranteed background work to WorkManager, reserving foreground services exclusively for real-time, user-visible tasks like turn-by-turn navigation, active workouts, and continuous audio playback.""",

    "deep_senior_en": """Under the hood, transitioning a Service to the foreground fundamentally alters its scheduling priority in the Android framework and Linux kernel. When startForeground is called, the ActivityManagerService updates the process's oom_adj and procState scores, elevating it from a cached or background process (oom_adj >= 900) to FOREGROUND_SERVICE priority (oom_adj = 200). This protects the process from being culled by lmkd during high memory pressure, ranking it just below the actively focused user interface.
However, platform policies have evolved to eliminate battery abuse. Since Android 14 (API 34), platform enforcement requires declaring a concrete foregroundServiceType both in the manifest and programmatically via ServiceCompat.startForeground(). If an app declares dataSync, Google Play policies impose strict runtime limits, and Google Play Console checks reject apps using unwarranted types. For location tracking, the app must hold either ACCESS_COARSE_LOCATION or ACCESS_FINE_LOCATION, along with the FOREGROUND_SERVICE_LOCATION permission, and must present a runtime rationale to the user.
A critical engineering challenge is managing the five-second notification contract. Calling context.startForegroundService(intent) posts a message to the system server. If the target service's onCreate or onStartCommand blocks the main thread with disk I/O, dependency injection initialization, or network requests before calling startForeground, the ActivityManagerService watchdog triggers an immediate ForegroundServiceDidNotStartInTimeException crash. To avoid this, startForeground must be the absolute first statement executed in onCreate or onStartCommand, showing an immediate placeholder notification before delegating heavy processing to background coroutines.
Furthermore, starting in Android 13, users can dismiss active foreground service notifications unless the service type is media playback or ongoing calls, and the Task Manager in the notification shade provides a prominent 'Stop' button. Architects must register onTaskRemoved and monitor onDestroy callbacks to clean up hardware handles and coroutine scopes gracefully when the user terminates the service externally."""
}

ARABIC_METADATA["AND-19"] = {
    "id": "AND-19",
    "questionAr": "ما هي الخدمات الأمامية (Foreground Services) وشروط الإشعارات في أندرويد؟",
    "topicAr": TOPIC_AR,
    "evaluates_ar": """- تعريف الـ Foreground Service كعملية مستمرة وملاحظة بوضوح من المستخدم وتتطلب إشعاراً دائماً.
- التمييز بين مهام الـ Foreground Service المستمرة في الوقت الفعلي وبين مهام WorkManager القابلة للتأجيل.
- استيعاب قيود أندرويد الحديثة: إلزام تحديد نوع الخدمة (Foreground Service Type) في أندرويد 14 ومهلة الـ 5 ثوانٍ.""",
    "why_it_matters_ar": "الـ Foreground Service بترفع أولوية العملية في النظام لدرجة تمنع الـ Low Memory Killer من إنهائها أثناء أداء عمل يدركه المستخدم تماماً، ومع ذلك بتلزم المطور بإشعار دائم لتوفير الشفافية ومنع استنزاف البطارية سراً. أندرويد 14 فرض تحديد نوع الخدمة وأذوناتها المحددة في الـ Manifest لتقييد إساءة استخدام الموارد، بينما أندرويد 12 منع تشغيلها من الخلفية إلا في استثناءات ضيقة.",
    "worked_example_ar": """تنفيذ Foreground Service لتتبع الموقع متوافقة مع أندرويد 14:
```xml
<!-- في AndroidManifest.xml: -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION" />

<service
    android:name=".LocationTrackingService"
    android:foregroundServiceType="location"
    android:exported="false" />
```
وداخل كود الـ Service بنستدعي:
```kotlin
ServiceCompat.startForeground(
    this,
    NOTIFICATION_ID,
    notification,
    ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION
)
```""",
    "trade_offs_ar": "استخدام الـ Foreground Service ممتاز للعمليات الحية كالملاحة وتشغيل الصوت، لكنه يزعج المستخدم بإشعار دائم ويخضع لرقابة صارمة من متجر Google Play. الاعتماد على WorkManager هو البديل الأفضل للمهام غير المرئية والمؤجلة كرفع الملفات ومزامنة قواعد البيانات، لأنه يحترم قيود النظام وتوفير الطاقة بدون إشغال المستخدم بإشعارات لا داعي لها.",
    "failure_modes_ar": "استدعاء startForegroundService والتأخر في استدعاء startForeground لأكثر من 5 ثوانٍ يسبب انهيار التطبيق الفوري بخطأ ForegroundServiceDidNotStartInTimeException. تشغيل الخدمة بدون تحديد foregroundServiceType مطابق في أندرويد 14 يرمي SecurityException. بدء الخدمة من الخلفية بدون استثناء صريح يفشل برمي BackgroundServiceStartNotAllowedException.",
    "production_perspective_ar": "في بيئات الإنتاج، بنجعل استدعاء startForeground هو أول سطر ينفذ في onCreate أو onStartCommand لتفادي مهلة الـ 5 ثوانٍ، مع إسناد العمليات الثقيلة لكوروتين منفصل. بنفصل إشعارات الخدمات في قنوات إشعارات مخصصة، وبنعتمد على WorkManager لجميع عمليات المزامنة غير المستعجلة، وبنراقب معدلات الـ Crashes واستهلاك البطارية في Google Play Console.",
    "how_to_answer_ar": """- **السبب الهندسي:** وضح أن الـ Foreground Service وسيلة لرفع أولوية العملية مع إلزام الشفافية للمستخدم عبر الإشعار.
- **طريقة الشرح:** اشرح مهلة الـ 5 ثوانٍ وقيد أندرويد 14 الخاص بالـ foregroundServiceType.
- **المفاضلات:** قارن صراحة بين استخدام الـ Foreground Service واستخدام WorkManager للمهام المؤجلة.
- **أنماط الفشل:** استشهد بانهيار التطبيق بـ ForegroundServiceDidNotStartInTimeException ومصيدة التأخر على الـ Main Thread.
- **الحل الإنتاجي:** وضح الاستدعاء الفوري للإشعار المبدئي وتحرير الموارد في onDestroy عند إيقاف الخدمة من Task Manager.""",
    "talking_points_ar": "ناقش كيف تغير الـ ActivityManagerService قيمة الـ oom_adj للعملية لتصل لمستوى 200، والقيود الصارمة المفروضة على بدء الخدمات من الخلفية في أندرويد 12، وكيف تتيح لوحة إشعارات أندرويد 14 للمستخدم زر Stop لإيقاف الخدمة قسراً، ولماذا ترفض جوجل بلاي نوع dataSync للمهام الطويلة.",
    "follow_ups_ar": """- **المحاور:** "ماذا يحدث لو استدعيت startForegroundService من الخلفية في أندرويد 12+؟"
  **المرشح:** "النظام هيرمي فوراً استثناء ForegroundServiceStartNotAllowedException لأن أندرويد 12 حظر بدء الـ Foreground Services من الـ Background إلا لو كان التطبيق معاه استثناء محدد زي استلام High-priority FCM أو منبه دقيق من AlarmManager."

- **المحاور:** "هل المستخدم يقدر يمسح إشعار الـ Foreground Service في أندرويد 13 والإصدارات الأحدث؟"
  **المرشح:** "أيوة، بدءاً من أندرويد 13 أصبح بإمكان المستخدم سحب ومسح معظم إشعارات الـ Foreground Services، باستثناء خدمات تشغيل الميديا والمكالمات الجارية. بالإضافة لكده، لوحة الإشعارات بقت بتوفر زرار صريح في الـ Task Manager يقدر المستخدم يضغط عليه ويوقف الخدمة تماماً في أي لحظة." """,
    "self_check_ar": "حدد شرط الإشعار الدائم؛ اشرح مهلة الـ 5 ثوانٍ؛ عيّن foregroundServiceType المناسب في أندرويد 14؛ واستبدل الخدمات غير المرئية بـ WorkManager.",
    "references_ar": """- [Foreground services overview](https://developer.android.com/guide/components/foreground-services) — معمارية الخدمات الأمامية.
- [Android 14 Foreground service types](https://developer.android.com/about/versions/14/changes/fgs-types-required) — أنواع الخدمات وإلزام التصريح.

تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.""",
    "quick_answer_ar": "الـ Foreground Service مخصصة للمهام المستمرة اللي المستخدم واعي بوجودها وشايفها، وبترفع أولوية العملية في النظام علشان الـ LMK ميموتهاش. شرطها الأساسي إظهار إشعار دائم غير قابل للمسح عبر استدعاء startForeground خلال 5 ثوانٍ كحد أقصى. وبدءاً من أندرويد 14، لازم تحدد foregroundServiceType في الـ Manifest وتاخد الـ Permission المناسب لنوع الخدمة زي الـ Location أو الميديا.",
    "best_answer_ar": """الـ Foreground Service هي الآلية اللي بيوفرها أندرويد لتشغيل عمليات طويلة ومستمرة بيكون المستخدم على دراية تامة بيها، زي تشغيل الموسيقى، أو تتبع الجري بالـ GPS، أو المكالمات الصوتية.
النظام بيدي العملية اللي شغالة فيها Foreground Service أولوية عالية جداً بتحميها من القتل بواسطة الـ Low Memory Killer، وفي مقابل الحماية دي، بيفرض وجود إشعار دائم وظاهر للمستخدم في الـ Notification Shade طول فترة تشغيلها علشان الشفافية وحماية البطارية.
من الناحية التنفيذية، لو شغلت الخدمة بـ startForegroundService، النظام بيديك مهلة 5 ثوانٍ فقط لاستدعاء startForeground وإظهار الإشعار؛ لو اتأخرت ثانية واحدة، التطبيق هيجيله Crash فوري بـ ForegroundServiceDidNotStartInTimeException.
ومن أول أندرويد 14، القيود بقت صارمة جداً: لازم تحدد نوع الخدمة صراحة في ملف الـ Manifest بـ android:foregroundServiceType ومعاه إذن الـ Permission المطابق، ولازم تمرر نفس النوع في دالة ServiceCompat.startForeground. ولو مهمتك قابلة للتأجيل ومش مرئية للمستخدم، بنستخدم WorkManager ومبنلجأش أبداً للـ Foreground Service.""",
    "deep_answer_ar": """تحت الكابوت في الـ Android OS Runtime ونواة لينكس، استدعاء startForeground بيغير تصنيف العملية بالكامل عند الـ ActivityManagerService. النظام بينقل قيمة الـ oom_score_adj للعملية من مستويات الـ Cached والـ Background (فوق 900) لمستوى الـ FOREGROUND_SERVICE بقيمة تقارب 200، وده بيحمي العملية من القتل عبر الـ lmkd إلا لو النظام وصل لحالة طوارئ قصوى في الرام.
لكن أندرويد قفل كل الثغرات اللي كانت التطبيقات بتستغلها لإبقاء خدماتها شغالة في الخلفية. في أندرويد 12، تم منع تشغيل الـ Foreground Service من الـ Background تماماً إلا في حالات استثنائية جداً زي استقبال High-priority FCM أو منبه دقيق. وفي أندرويد 14، جوجل فرضت تخصيص الـ foregroundServiceType؛ لو نوع الخدمة location، لازم التطبيق يكون معاه صلاحية الموقع في الـ Runtime وواخد إذن FOREGROUND_SERVICE_LOCATION، وبولندا الـ Play Store بترفض أي تطبيق بيستخدم أنواع زي dataSync لأكتر من مهام محدودة وقصيرة.
أكبر فخ برمجي بيوقع فيه المطورين هو الـ 5-second crash؛ لما تنادي startForegroundService، لو دالة onCreate أو onStartCommand انشغلت بعمليات حقن تبعيات ثقيلة أو قراءة ديسك قبل ما تنادي startForeground، الـ System Server Watchdog هيرمي فوراً ForegroundServiceDidNotStartInTimeException. علشان نتفادى الكارثة دي في الـ Production، أول سطر لازم يتنفذ في الخدمة هو إظهار الإشعار المبدئي فوراً، وبعد كده نعمل Dispatch للعمليات الثقيلة على Coroutine Dispatcher منفصل.
كمان في أندرويد 13 و 14، الـ Task Manager في لوحة الإشعارات بيتيح للمستخدم زرار 'Stop' صريح لإيقاف أي Foreground Service في أي لحظة. لازم معمارياً نكون مهيئين دالة onDestroy لإلغاء الـ CoroutineScope وتحرير حساسات الـ GPS فوراً وبأمان عند إيقاف الخدمة قسراً."""
}

# ==============================================================================
# AND-20: How do you share data or communicate across processes (Binder/IPC)?
# ==============================================================================
CANONICAL_DATA["AND-20"] = {
    "concept_en": """In the Android operating system, every application process executes within its own isolated Linux User ID (UID) and Dalvik/ART virtual machine sandbox. Applications and system servers cannot access memory address spaces across process boundaries directly. Inter-Process Communication (IPC) is facilitated at the operating system foundation by the Binder kernel driver (/dev/binder). Binder provides high-performance, reference-counted remote procedure calls (RPC), capability discovery via ServiceManager, and hardware-level caller identity tracking through Linux UID and PID enforcement.
Android structures IPC into several architectural paradigms tailored to data velocity and complexity. For simple message passing and component activation, Intents and Bundles serialize lightweight parameters across process boundaries via Parcelable. For structured data exchange and relational queries, ContentProvider exposes CRUD operations over Binder, while FileProvider shares binary streams via scoped content:// URIs. For complex, bidirectional client-service communication, developers utilize Messenger for single-threaded queue-based messaging, or AIDL (Android Interface Definition Language) for concurrent multi-threaded RPC interfaces. For massive binary payloads exceeding Binder limits, applications utilize shared memory primitives such as Ashmem or SharedMemory.""",

    "walkthrough_en": """Choosing and implementing IPC mechanisms in Android based on data size and architecture:

```kotlin
// 1. Sharing files safely without memory overhead via FileProvider URI:
val photoUri: Uri = FileProvider.getUriForFile(
    context,
    "com.example.myapp.fileprovider",
    imageFile
)
val shareIntent = Intent(Intent.ACTION_SEND).apply {
    type = "image/jpeg"
    putExtra(Intent.EXTRA_STREAM, photoUri)
    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
}
context.startActivity(Intent.createChooser(shareIntent, "Share image"))
```

For remote RPC operations, an AIDL interface generates client proxies and service stubs:

```kotlin
// IRemoteService.aidl
interface IRemoteService {
    int calculateHash(in byte[] data);
}

// In the Service implementation:
class RemoteComputeService : Service() {
    private val binder = object : IRemoteService.Stub() {
        override fun calculateHash(data: ByteArray): Int {
            // Executed on a Binder thread pool
            return data.contentHashCode()
        }
    }

    override fun onBind(intent: Intent?): IBinder = binder
}
```

Failure scenario: An application attempts to pass a large 2MB Bitmap or extensive JSON payload inside an Intent extra across process boundaries. The Binder transaction exceeds the shared 1MB buffer limit, immediately crashing the process with a fatal TransactionTooLargeException.""",

    "short_en": """Android IPC is powered by the Binder kernel driver providing memory-mapped remote procedure calls. For structured queries, use ContentProvider; for sharing files, use FileProvider with scoped URI permissions; for sequential asynchronous messaging, use Messenger; and for high-performance concurrent RPC, use AIDL. Avoid passing large payloads through Intent Bundles to prevent TransactionTooLargeException, leveraging SharedMemory for high-throughput binary transfer.""",

    "structured_en": """To begin with, Android processes run in isolated memory spaces under distinct Linux UIDs. Inter-process communication relies on the /dev/binder kernel driver, which executes remote method calls and transfers data through shared memory-mapped pages with single-copy efficiency.
From an architectural standpoint, Android offers four distinct IPC mechanisms matched to operational requirements. Intents and Bundles handle asynchronous component navigation; ContentProvider facilitates cross-process tabular queries; Messenger provides a lightweight, single-threaded message queue backed by a Handler; and AIDL defines multi-threaded remote interfaces with full type safety.
In production scenarios requiring heavy inter-process computation, AIDL stubs execute incoming calls on a Binder thread pool in the hosting process. Methods exposed through AIDL must be strictly thread-safe, and all custom arguments must implement Parcelable with explicit directional annotations like in, out, or inout.
As for boundary management, all Binder transactions share a system-wide per-process buffer limit of 1MB. Passing large collections or Bitmaps through Intents triggers an immediate TransactionTooLargeException. For large binary payloads, we bypass Binder marshaling entirely by passing file descriptors or leveraging SharedMemory.""",

    "deep_senior_en": """At the kernel layer, Binder operates through the /dev/binder character driver using ioctl calls. When an application process starts, it opens the Binder driver and memory-maps a 1MB virtual address space (mmap). Traditional UNIX IPC mechanisms like sockets or pipes require two data copies (from user space to kernel space, then kernel space to receiving user space). Binder achieves superior performance through single-copy semantics: the kernel copies data directly from the calling process's user space into the receiving process's mapped memory buffer.
However, this 1MB memory buffer is shared across all ongoing incoming and outgoing Binder transactions within the process. If multiple concurrent IPC operations, asynchronous callbacks, or Intent broadcasts occur simultaneously, the aggregate payload can easily exhaust this buffer, throwing a fatal TransactionTooLargeException. In production architectures, passing raw bitmaps, documents, or large lists over Binder is an anti-pattern. Instead, we use SharedMemory or MemoryFile (backed by Linux ashmem), where data resides in a shared kernel memory region, and only the lightweight integer file descriptor (ParcelFileDescriptor) is transmitted over Binder.
Security is enforced at the kernel layer. When a remote call arrives at a Binder stub, Binder.getCallingUid() and Binder.getCallingPid() return the authentic credentials of the calling process stamped by the Linux kernel. A secure service implementation must check these credentials against PackageManager before executing sensitive business logic.
Furthermore, concurrency in AIDL demands rigorous synchronization. While Messenger processes incoming messages sequentially on the service's main thread Looper, AIDL calls are dispatched to arbitrary worker threads from a Binder thread pool containing up to 16 threads. State variables accessed within AIDL methods must use atomic structures, mutexes, or concurrent collections to prevent race conditions and thread deadlocks across processes."""
}

ARABIC_METADATA["AND-20"] = {
    "id": "AND-20",
    "questionAr": "كيف تشارك البيانات وتتواصل عبر العمليات المنفصلة (Binder/IPC) في أندرويد؟",
    "topicAr": TOPIC_AR,
    "evaluates_ar": """- شرح عزل العمليات في مساحات عناوين مستقلة ودور مشغل الـ Binder كوسيط للنظام.
- اختيار الآلية المناسبة: Intents أو ContentProvider أو Messenger أو AIDL بناءً على حجم البيانات والتزامن.
- إدراك حد الـ 1MB لـ Binder Buffer واستخدام SharedMemory أو الملفات للحمولات الضخمة.""",
    "why_it_matters_ar": "الـ Binder بينقل استدعاءات الدوال عبر حدود عمليات لينكس المعزولة. الـ AIDL بيولد Stubs و Proxies لواجهة محددة، ويقوم بتسلسل البيانات عبر Parcelable، مع إمكانية عبور الثريدات والعمليات. مكالمات الـ IPC ممكن تسبب تجميد الواجهة أو ترمي RemoteException لو ماتت العملية الأخرى. الـ ContentProviders بتمثل المعيار لمشاركة البيانات المهيكلة والملفات عبر URIs بصلاحيات مؤقتة، بينما الـ Intent مناسب للرسائل البسيطة وتشغيل الشاشات.",
    "worked_example_ar": """مشاركة ملف بأمان عبر FileProvider مع تطبيق خارجي:
```kotlin
val photoUri: Uri = FileProvider.getUriForFile(
    context, "com.example.fileprovider", imageFile
)
val shareIntent = Intent(Intent.ACTION_SEND).apply {
    type = "image/jpeg"
    putExtra(Intent.EXTRA_STREAM, photoUri)
    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
}
context.startActivity(Intent.createChooser(shareIntent, "Share"))
```
وعند الحاجة لاتصال متقدم بين تطبيقين، بنعرف واجهة AIDL بمستوى إذن signature للتحقق من هوية المتصل عبر `Binder.getCallingUid()`.""",
    "trade_offs_ar": "الـ ContentProvider هو الأنسب للاستعلامات ومشاركة الملفات بصلاحيات مؤقتة دون كشف مسار الملف في الذاكرة. الـ AIDL بيدعم استدعاءات دوال متزامنة وغنية لكنه يضيف تعقيدات إدارة الثريدات وإصدارات الواجهة. الـ Messenger بيعالج الرسائل بتسلسل وبساطة عبر Handler لكنه أبطأ في العمليات الكبيرة. ونقل البيانات الضخمة بيتطلب استخدام SharedMemory لتفادي استهلاك مساحة الـ Binder المحدودة.",
    "failure_modes_ar": "تنفيذ استدعاء IPC ثقيل على الـ Main Thread يتسبب في تجميد التطبيق وظهور خطأ ANR. محاولة إرسال صورة أو كائن ضخم في Intent Extra يتجاوز سعة الـ 1MB ويرمي فورا خطأ TransactionTooLargeException. افتراض بقاء العملية البعيدة حية دائماً يؤدي لتوقف التطبيق بدون استجابة عند موتها دون فحص Binder Death. يتم فحص المشاكل باختبار انقطاع الاتصال ومحاكاة بطء الشبكة البينية.",
    "production_perspective_ar": "في الأنظمة الضخمة، بنصمم عقود IPC واضحة ومحددة الإصدار، مع معالجة صريحة لكل حالات الـ RemoteException. بنتحقق من هوية المتصل برمجياً عبر الـ Calling UID مع كل استدعاء مصدّر، وبنراقب موت العمليات عبر linkToDeath لإعادة الاتصال تلقائياً. بننقل جميع عمليات الـ IPC بعيداً عن الـ Main Thread ونعتمد على Coroutines أو RxJava لتنظيم التدفق.",
    "how_to_answer_ar": """- **السبب المعماري:** اشرح أن كل تطبيق يعمل في Linux Process مستقلة وأن Binder هو وسيلة التواصل الوحيدة المسموحة بالنظام.
- **طريقة الشرح:** صنف آليات الـ IPC الأربعة (Intents، ContentProvider، Messenger، AIDL) ووضح معيار اختيار كل منها.
- **المفاضلات:** قارن بين Messenger أحادي الخيط و AIDL متعدد الخيوط والـ SharedMemory للملفات الضخمة.
- **أنماط الفشل:** استشهد بـ TransactionTooLargeException والـ ANRs الناتجة عن تنفيذ الـ IPC على الـ Main Thread.
- **الحل الإنتاجي:** وضح استخدام FileProvider لمشاركة الـ URIs الآمنة والتحقق من هوية المتصل عبر Binder.getCallingUid().""",
    "talking_points_ar": "ناقش كيف يعمل مشغل /dev/binder في نواة لينكس عبر تقنية mmap والنسخ الفردي للبيانات (Single-copy)، وحدود مساحة الـ 1MB المشتركة لكل العمليات، وكيف ينشئ AIDL طاقم ثريدات (Thread Pool) يصل لـ 16 ثريد متزامن، وكيفية استخدام SharedMemory لنقل البيانات الضخمة بدون استهلاك الـ Binder.",
    "follow_ups_ar": """- **المحاور:** "ما هو سبب خطأ TransactionTooLargeException وكيف تحله معمارياً؟"
  **المرشح:** "السبب هو تجاوز حد الـ 1 ميجابايت المخصص للـ Binder Buffer للعملية بالكامل لكل الـ Transactions الجارية. حله المعماري هو الامتناع عن إرسال مصفوفات البيانات الكبيرة أو الصور في الـ Intent، واستبدالها بنقل File Descriptors عبر FileProvider أو استخدام SharedMemory المشتركة في الذاكرة."

- **المحاور:** "كيف يختلف تنفيذ الدوال في Messenger عن AIDL من حيث الـ Concurrency؟"
  **المرشح:** "الـ Messenger بيعتمد على Handler، وبالتالي كل الرسائل بتتصافف في طابور واحد وتتنفذ بشكل تسلسلي على ثريد واحد بدون خطر Race Conditions. أما الـ AIDL فاستدعاءاته بتتوزع على Binder Thread Pool في العملية المستقبلة، وبالتالي لازم كود الـ Service يكون Thread-safe بالكامل ويستخدم مزامنة صريحة." """,
    "self_check_ar": "اشرح آلية عمل مشغل Binder؛ حدد متى تختار AIDL أو Messenger أو ContentProvider؛ تجنب تجاوز سعة الـ 1MB؛ وراقب موت العملية عبر linkToDeath.",
    "references_ar": """- [Bound services overview](https://developer.android.com/guide/components/bound-services) — معمارية الخدمات المقيدة و Binder.
- [Android Interface Definition Language (AIDL)](https://developer.android.com/guide/components/aidl) — الاتصال المتقدم بين العمليات.

تمت المراجعة الفنية استناداً إلى الوثائق الرسمية في 2026-10-13.""",
    "quick_answer_ar": "الـ IPC في أندرويد مبني على الـ Binder Kernel Driver لتبادل البيانات بين العمليات المعزولة. لمشاركة الملفات الكبيرة بنستخدم FileProvider مع أذونات مؤقتة للـ URI؛ ولتبادل البيانات المهيكلة بنستخدم ContentProvider؛ وللرسائل المتتالية بنستخدم Messenger؛ وللعمليات المتقدمة المتزامنة بنستخدم AIDL. ولازم نتجنب تمرير بيانات ضخمة في الـ Intents لتفادي خطأ TransactionTooLargeException.",
    "best_answer_ar": """في نظام أندرويد، كل تطبيق بيشتغل في Linux Process منفصلة بـ UID خاص وذاكرة معزولة تماماً في الـ ART Sandbox، ومينفعش تطبيق يقرأ من ذاكرة تطبيق تاني مباشرة.
علشان التطبيقات والـ System Services يتواصلوا مع بعض، أندرويد بيعتمد على الـ Binder Driver الموجود في نواة لينكس. الـ Binder بيتميز بالسرعة الفائقة لأنه بيعمل Single-copy للبيانات من مساحة المستخدم للعملية التانية مباشرة عبر الـ mmap.
عندنا 4 آليات أساسية للـ IPC بنختار بينهم حسب طبيعة البيانات:
أولاً، الـ Intents والـ Bundles للمراسلات البسيطة وتشغيل الشاشات.
ثانياً، الـ ContentProvider و FileProvider لمشاركة البيانات وقواعد البيانات أو مشاركة الملفات والصور عبر content:// URIs مع صلاحيات قراءة مؤقتة.
ثالثاً، الـ Messenger للاتصال الخفيف المعتمد على Queue و Handler بيعالج الرسايل ورا بعض على ثريد واحد بدون تعقيد.
رابعاً، الـ AIDL للـ Remote Procedure Calls المعقدة والسريعة، بس لازم ناخد بالنا إن دوال الـ AIDL بتتنفذ على Binder Thread Pool، وبالتالي لازم كود الـ Service يكون Thread-safe 100%.
وأهم قاعدة في الإنتاج هي الابتعاد عن إرسال بيانات أكبر من مئات الكيلوبايتس في الـ Intent علشان الـ Binder Buffer محكوم بحد أقصى 1MB وأي زيادة هترمي TransactionTooLargeException.""",
    "deep_answer_ar": """على مستوى الـ Linux Kernel والـ OS Architecture، الـ Binder هو العمود الفقري لنظام أندرويد كله؛ كل تواصل بين التطبيق وخدمات النظام زي الـ ActivityManagerService بيتم من خلال /dev/binder باستخدام ioctl system calls. الميزة العبقرية في الـ Binder مقارنة بـ Sockets أو Pipes في لينكس هي الـ Performance والأمان؛ الـ Binder بينقل البيانات بعملية نسخ واحدة فقط (Single Copy) من الـ Address Space بتاع المرسل لمساحة الذاكرة المحجوزة للعملية المستلمة عن طريق mmap.
النقطة الحرجة اللي لازم Staff Engineer يفهمها هي حدود الـ 1MB Binder Buffer. المساحة دي مش مخصصة لكل Transaction لوحدها، دي مساحة مشتركة للعملية كلها لكل الـ Transactions الجارية في نفس اللحظة. لو حاولت تبعت Bitmap كبيرة أو List ضخمة في Intent Extra، هترمي فوراً TransactionTooLargeException ويكرش التطبيق. الحل المعماري لنقل البيانات الضخمة أو الصور بين العمليات هو استخدام SharedMemory أو MemoryFile المدعومة بـ Ashmem في لينكس؛ بنحط البيانات في Shared Memory، وبنبعت بس الـ File Descriptor عبر الـ Binder كـ ParcelFileDescriptor.
من ناحية الأمان، الـ Binder هو اللي بيضمن الـ Sandbox؛ لما يجيلك طلب في AIDL Stub، تقدر تنادي Binder.getCallingUid() و Binder.getCallingPid() ودول قيم مختومة من نواة لينكس مستحيل تزويرها، وتقدر تطابقها مع PackageManager للتحقق من هوية وصلاحيات التطبيق المتصل.
ومن ناحية الـ Concurrency، الـ Messenger بيعالج الرسايل بشكل تسلسلي على الـ Main Thread Looper، بينما الـ AIDL بيوزع الطلبات على Binder Thread Pool بتوصل لـ 16 ثريد شغالين بالتوازي؛ وده معناه إن أي Mutable State جوه كود الـ AIDL لازم تكون محمية بـ Mutexes أو Atomic structures لتفادي الـ Race Conditions والـ Deadlocks."""
}

#!/usr/bin/env python3
"""Generator for AND-13 through AND-18 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "and.json"

AND_13_18 = [
    {
        "id": "AND-13",
        "arabic_explanation": (
            "التعامل مع أذونات التشغيل (Runtime Permissions) في أندرويد الحديث وإدارة حالات الرفض الدائم (Permanent Denial) هي إحدى أهم متطلبات تجربة المستخدم (UX) والأمان:\n\n"
            "1. شجرة القرار المنطقية للأذونات (Permission Decision Flow):\n"
            "   - **الخطوة 1: الفحص المسبق (`ContextCompat.checkSelfPermission`):**\n"
            "     * هل الإذن ممنوح بالفعل؟ لو نعم -> نفذ العملية فوراً (افتح الكاميرا مثلاً).\n"
            "   - **الخطوة 2: فحص مبرر الإذن (`shouldShowRequestPermissionRationale`):**\n"
            "     * لو رجعت `true`: هذا يعني أن المستخدم رفض الإذن مرة واحدة من قبل! هنا **يجب إظهار شاشة توضيحية (Rationale UI/Dialog)** تشرح له بوضوح وفائدة: 'لماذا يحتاج التطبيق إذن الكاميرا لمسح باركود الشحنة'، مع زر لطلب الإذن مجدداً.\n"
            "   - **الخطوة 3: طلب الإذن عبر Activity Result API:**\n"
            "     * استدعاء `requestPermissionLauncher.launch(permission)`.\n\n"
            "2. الرفض الدائم (Permanent Denial - 'Don't ask again'):\n"
            "   - في أندرويد الحديث (Android 11+)، إذا رفض المستخدم الإذن مرتين، النظام يمنع ظهور نافذة الإذن نهائياً، ودالة `shouldShowRequestPermissionRationale` ترجع `false`!\n"
            "   - **كيف يتعامل الـ Senior Engineer مع الرفض الدائم؟**\n"
            "     * لا نستسلم ولا نترك الزر معطلاً بدون شرح؛ نظهر Dialog للمستخدم يشرح: 'تم تعطيل إذن الكاميرا. يرجى تفعيله من إعدادات التطبيق للمتابعة'، مع زر يفتح صفحة إعدادات التطبيق مباشرة عبر Intent: `Settings.ACTION_APPLICATION_DETAILS_SETTINGS`."
        ),
        "practical_walkthrough": (
            "التنفيذ البرمجي الكامل باستخدام Activity Result API:\n"
            "```kotlin\n"
            "class CameraFeatureActivity : AppCompatActivity() {\n"
            "\n"
            "    // 1. تسجيل الـ Launcher في البداية:\n"
            "    private val requestCameraLauncher = registerForActivityResult(\n"
            "        ActivityResultContracts.RequestPermission()\n"
            "    ) { isGranted ->\n"
            "        if (isGranted) {\n"
            "            openCamera()\n"
            "        } else {\n"
            "            // فحص هل الرفض دائم؟\n"
            "            if (!shouldShowRequestPermissionRationale(Manifest.permission.CAMERA)) {\n"
            "                showSettingsRedirectDialog() // توجيه للإعدادات\n"
            "            } else {\n"
            "                showPermissionDeniedToast()\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "\n"
            "    fun onCaptureClicked() {\n"
            "        when {\n"
            "            ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED -> {\n"
            "                openCamera()\n"
            "            }\n"
            "            shouldShowRequestPermissionRationale(Manifest.permission.CAMERA) -> {\n"
            "                showEducationalDialog { requestCameraLauncher.launch(Manifest.permission.CAMERA) }\n"
            "            }\n"
            "            else -> {\n"
            "                requestCameraLauncher.launch(Manifest.permission.CAMERA)\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "\n"
            "    private fun showSettingsRedirectDialog() {\n"
            "        AlertDialog.Builder(this)\n"
            "            .setTitle(\"Camera Permission Required\")\n"
            "            .setMessage(\"You have permanently disabled camera access. Please enable it in Settings to scan QR codes.\")\n"
            "            .setPositiveButton(\"Settings\") { _, _ ->\n"
            "                val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {\n"
            "                    data = Uri.fromParts(\"package\", packageName, null)\n"
            "                }\n"
            "                startActivity(intent)\n"
            "            }\n"
            "            .show()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Check permission with ContextCompat.checkSelfPermission(). If denied, check shouldShowRequestPermissionRationale() to show an educational rationale dialog before requesting. If denied permanently ('Don't ask again'), guide the user to the app's system Settings screen via Settings.ACTION_APPLICATION_DETAILS_SETTINGS.",
        "best_answer": (
            "Handling runtime permissions cleanly requires adhering to Android's modern 4-step permission lifecycle:\n\n"
            "1. **Check Status**: Query `ContextCompat.checkSelfPermission()`. If granted, execute the protected feature immediately.\n"
            "2. **Check Rationale**: If not granted, evaluate `ActivityCompat.shouldShowRequestPermissionRationale()`. If this returns `true`, the user has previously denied the request. Before showing the system dialog again, display an in-app educational rationale dialog explaining *why* the camera or location is required for this specific feature.\n"
            "3. **Request via Activity Result API**: Launch the request using `ActivityResultContracts.RequestPermission()`, which replaces deprecated `onRequestPermissionsResult`.\n"
            "4. **Handle Permanent Denial**: In modern Android, if the user denies the permission twice, the OS permanently suppresses system dialogs. If permission is denied and `shouldShowRequestPermissionRationale()` returns `false`, the permission is permanently denied. Display a clear UI explanation with an actionable button redirecting the user to `Settings.ACTION_APPLICATION_DETAILS_SETTINGS` to enable it manually."
        ),
        "deep_answer": (
            "From an OS policy perspective, Android 11+ introduces **One-time Permissions** and automatic permission resets for unused apps. "
            "When a user grants 'Only this time', the permission is granted only while the Activity is in the foreground and is revoked the moment the process dies.\n\n"
            "Furthermore, in Android 13 (API 33), runtime permissions were added for `POST_NOTIFICATIONS` and granular media (`READ_MEDIA_IMAGES`, `READ_MEDIA_VIDEO`, `READ_MEDIA_AUDIO`), deprecating the old broad `READ_EXTERNAL_STORAGE`. "
            "In Android 14 (API 34), users can grant **Partial Media Access** (`READ_MEDIA_VISUAL_USER_SELECTED`), allowing access to a selected subset of photos. Apps must handle this partial authorization without crashing or assuming full gallery visibility."
        ),
        "follow_ups": [
            {
                "interviewer": "Why must you register the Activity Result launcher before `onStart()`?",
                "answer": "Because the Activity Result API requires registering listeners during `onCreate()` or property initialization so that if the Activity is destroyed and recreated while the permission dialog is visible, the result can be reconnected to the callback."
            },
            {
                "interviewer": "Can you request multiple permissions at once?",
                "answer": "Yes, using `ActivityResultContracts.RequestMultiplePermissions()`, which takes an array of permissions and returns a `Map<String, Boolean>` mapping each permission to its grant result."
            },
            {
                "interviewer": "What happens if you request a permission that is not declared in AndroidManifest.xml?",
                "answer": "The system will immediately deny the permission without showing any dialog to the user, and will log a security warning in Logcat."
            }
        ]
    },
    {
        "id": "AND-14",
        "arabic_explanation": (
            "الـ Activity Result API هو البديل الحديث والموثوق لـ `startActivityForResult` القديمة المعيبة:\n\n"
            "1. المشاكل الكارثية في `startActivityForResult` القديمة:\n"
            "   - كانت تعتمد على دالة عملاقة واحدة `onActivityResult(requestCode, resultCode, data)`.\n"
            "   - تتطلب إدارة أكواد يدوية (`REQUEST_CODE = 101, 102, 103`) وعشرات كتل الـ `switch-case` المعقدة.\n"
            "   - **الكارثة الكبرى (Process Death Bug):** عندما تفتح الكاميرا لتصوير صورة، تطبيق الكاميرا يستهلك 500MB من الرام، فيقوم النظام بـ **قتل الـ Activity الخاصة بتطبيقك في الخلفية**! عند التقاط الصورة والعودة، كانت النتائج تضيع أو يحدث Crash لأن الـ Activity أعيد بناؤها وفقدت سياق الـ Callback!\n\n"
            "2. ما الذي يوفره الـ Activity Result API؟\n"
            "   - **Type-Safety كامل:** عقود محددة (Contracts) تحدد نوع المدخلات والمخرجات بدقة (مثل `GetContent`, `TakePicture`, `RequestPermission`).\n"
            "   - **مقاوم للـ Process Death 100%:** يتم تسجيل الـ Callback في مرحلة الـ Initialization/onCreate عبر `registerForActivityResult`. حتى لو ماتت الـ Activity وتمت إعادة بنائها، النظام يعيد ربط النتيجة بالـ Callback تلقائياً بدون أي سطر كود إضافي.\n\n"
            "3. إمكانية كتابة عقود مخصصة (Custom Contracts):\n"
            "   - يمكنك إنشاء `ActivityResultContract<Input, Output>` مخصص لتغليف أي Intent وتحويل النتيجة مباشرة لـ Domain Model."
        ),
        "practical_walkthrough": (
            "مقارنة بين القديم والحديث لاختيار صورة من المعرض:\n"
            "```kotlin\n"
            "class ProfileActivity : AppCompatActivity() {\n"
            "\n"
            "    // ✅ النمط الحديث باستخدام Activity Result API:\n"
            "    private val pickImageLauncher = registerForActivityResult(\n"
            "        ActivityResultContracts.GetContent()\n"
            "    ) { imageUri: Uri? ->\n"
            "        // يتم استدعاؤها بنجاح حتى لو ماتت الـ Activity أثناء وجود المستخدم في المعرض!\n"
            "        imageUri?.let { avatarImageView.setImageURI(it) }\n"
            "    }\n"
            "\n"
            "    fun onChangeAvatarClicked() {\n"
            "        pickImageLauncher.launch(\"image/*\") // استدعاء نظيف بـ Type-safe contract\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "The Activity Result API replaces error-prone startActivityForResult and onActivityResult with strongly-typed, modular ActivityResultContracts. Crucially, it registers callbacks during initialization so results are safely reconnected even if the calling Activity is killed by process death while the external app is open.",
        "best_answer": (
            "The Activity Result API completely modernizes inter-activity result handling by replacing legacy `startActivityForResult` and monolithic `onActivityResult` overrides.\n\n"
            "It solves three major architectural defects of the old API:\n\n"
            "1. **Process Death Resilience**: When launching memory-heavy external applications (like the camera or gallery), Android frequently kills the calling Activity process in the background. Because `registerForActivityResult()` registers the callback handle before `onStart()`, when the Activity recreates upon returning, the result is re-delivered to the restored callback cleanly without data loss.\n\n"
            "2. **Type-Safe Modular Contracts**: It uses `ActivityResultContract<I, O>` abstractions that explicitly define typed inputs and outputs—such as `TakePicture`, `GetContent`, or `RequestPermission`—eliminating raw `Intent` parsing and fragile `requestCode` integer switch statements.\n\n"
            "3. **Decoupled Architecture**: Result launchers can be registered inside standalone helper classes and lifecycle observers, removing bloated navigation code from the Activity class body."
        ),
        "deep_answer": (
            "Under the hood, the API is managed by `ActivityResultRegistry`. "
            "When you invoke `registerForActivityResult(contract, callback)`, it generates a unique key and registers the callback in the registry. "
            "When `launch(input)` is called, the contract generates an Intent, saves the request key in the instance state Bundle, and dispatches the Intent.\n\n"
            "You can also write powerful **Custom Contracts**:\n\n"
            "```kotlin\n"
            "class SelectUserContract : ActivityResultContract<String, UserProfile?>() {\n"
            "    override fun createIntent(context: Context, input: String): Intent =\n"
            "        Intent(context, UserPickerActivity::class.java).putExtra(\"team_id\", input)\n"
            "\n"
            "    override fun parseResult(resultCode: Int, intent: Intent?): UserProfile? =\n"
            "        if (resultCode == Activity.RESULT_OK) intent?.getParcelableExtra(\"user\") else null\n"
            "}\n"
            "```\n\n"
            "This encapsulates all intent parsing, extras keys, and result code checks into a single reusable component across multi-module codebases."
        ),
        "follow_ups": [
            {
                "interviewer": "Why must `registerForActivityResult` be called unconditionally during initialization?",
                "answer": "Because the callback must be registered before the Activity transitions past `CREATED`. If the Activity was recreated after process death, the framework delivers pending results during `onStart()`, so the callback must already be registered to receive them."
            },
            {
                "interviewer": "Can you use the Activity Result API in a standalone non-UI class?",
                "answer": "Yes! By accepting an `ActivityResultRegistry` and a `LifecycleOwner`, a standalone presenter or repository class can register and launch activity contracts without being an Activity subclass."
            },
            {
                "interviewer": "What contract is used for picking visual media in Android 13+?",
                "answer": "`ActivityResultContracts.PickVisualMedia()`, which opens the modern, privacy-preserving Android Photo Picker without requiring any storage permissions."
            }
        ]
    },
    {
        "id": "AND-15",
        "arabic_explanation": (
            "المقارنة الشاملة بين نماذج التنقل (Navigation Paradigms) في Android: Activity vs Fragment vs Compose Navigation vs Deep Links:\n\n"
            "1. الـ Multi-Activity Navigation (النموذج الكلاسيكي القديم):\n"
            "   - كل شاشة عبارة عن `Activity` منفصلة.\n"
            "   - **العيوب:** استهلاك كبير لموارد النظام (كل Activity لها Window و Context منفصل)؛ انتقال بطيء مع وميض بين الشاشات؛ صعوبة مشاركة البيانات المعقدة؛ وعدم مرونة الـ Animations.\n\n"
            "2. الـ Fragment-based Navigation (Single-Activity Architecture):\n"
            "   - `MainActivity` واحدة تحتوي على `NavHostFragment` وشاشات عبارة عن `Fragments`.\n"
            "   - **المميزات:** أسرع بكثير وأخف في الذاكرة؛ إمكانية مشاركة ViewModel على مستوى الـ Activity أو الـ Graph؛ ودعم كامل للـ Navigation Component XML.\n"
            "   - **العيوب:** تعقيد دورة حياة الـ Fragment View وضرورة إدارة `viewLifecycleOwner` لتجنب الـ Leaks.\n\n"
            "3. الـ Jetpack Compose Navigation (النموذج الحديث 100%):\n"
            "   - التنقل بين دوال `@Composable` عادية تماماً (`NavHost(navController) { composable(\"route\") }`).\n"
            "   - **المميزات:** خفيف جداً بدون أي Fragment overhead؛ يزيل الـ ViewBinding leaks تماماً؛ وتكامل تام مع Type-Safe Navigation (Kotlin Serialization في Compose 2.8+).\n\n"
            "4. الـ Deep Links (الروابط العميقة):\n"
            "   - فتح شاشة معينة داخل التطبيق مباشرة من رابط خارجي (URL أو إشعار).\n"
            "   - تتطلب بناء **Synthetic Backstack** سليم حتى إذا ضغط المستخدم زر 'Back' يعود للشاشة السابقة للتطبيق وليس للخروج من التطبيق فجأة."
        ),
        "practical_walkthrough": (
            "كيف تطورت كتابة الـ Navigation حتى الـ Type-Safe Navigation الحديثة في Compose:\n"
            "```kotlin\n"
            "// مع Compose 2.8+ و Kotlinx Serialization:\n"
            "@Serializable data class ProductDetailsRoute(val productId: String, val fromSearch: Boolean)\n"
            "\n"
            "NavHost(navController = navController, startDestination = HomeRoute) {\n"
            "    composable<HomeRoute> { HomeScreen(onProductClick = { id -> \n"
            "        navController.navigate(ProductDetailsRoute(id, true)) \n"
            "    }) }\n"
            "    \n"
            "    composable<ProductDetailsRoute> { backStackEntry ->\n"
            "        val route: ProductDetailsRoute = backStackEntry.toRoute()\n"
            "        ProductDetailsScreen(productId = route.productId)\n"
            "    }\n"
            "}\n"
            "```\n"
            "وداعاً للـ String URLs والأخطاء الإملائية؛ التنقل أصبح Type-Safe 100%."
        ),
        "quick_answer": "Multi-Activity navigation is heavy and deprecated; Fragment navigation (Single-Activity) is lightweight but has complex view lifecycles; Compose Navigation is modern, declarative, and type-safe with zero Fragment overhead; and Deep Links route external URLs directly to internal screens requiring synthetic backstacks.",
        "best_answer": (
            "Modern Android architecture has evolved through four navigation paradigms:\n\n"
            "1. **Multi-Activity (Legacy)**: Each screen is an Activity. It incurs high memory overhead per window, creates clunky window transitions, and makes complex state sharing difficult. It is now reserved only for truly distinct app entry points (e.g., Auth vs Main App).\n\n"
            "2. **Fragment Navigation (Single-Activity Architecture)**: A single Activity hosts a `NavHostFragment`. It improved transition fluidity and memory efficiency, enabling shared ViewModels. However, managing the dual lifecycle of Fragments and nulling ViewBindings added cognitive overhead.\n\n"
            "3. **Jetpack Compose Navigation (Modern Standard)**: Pure declarative navigation between Composables via `NavHost` and `NavController`. It eliminates Fragment view boilerplate entirely. Starting with Navigation Compose 2.8+, it supports **Type-Safe Navigation** using Kotlinx Serialization classes instead of error-prone String route paths.\n\n"
            "4. **Deep Links**: URL-based ingress allowing notifications, emails, or web links to route directly to internal destinations. They require proper synthetic backstack construction via `TaskStackBuilder` so pressing Back navigates up the logical app hierarchy rather than exiting to the launcher."
        ),
        "deep_answer": (
            "At the architectural boundary, Deep Links pose significant security and state-restoration challenges: "
            "When an external link opens `myapp://order/123`, the app must not assume that the user is authenticated. "
            "The navigation graph must implement a conditional gateway: if the user's session token is missing or expired, intercept the deep link, redirect to the Login route, and upon successful authentication, resume navigation to the intended target route.\n\n"
            "Furthermore, for App Links (`https://example.com/order/123`), verifying Android App Links via Digital Asset Links (`.well-known/assetlinks.json`) is mandatory. "
            "Verified App Links open your app directly without displaying the ambiguous system disambiguation dialog, protecting users against phishing by imposter apps claiming custom schemes."
        ),
        "follow_ups": [
            {
                "interviewer": "How does `NavBackStackEntry` scope ViewModels in Compose Navigation?",
                "answer": "Each destination in the navigation backstack is a `ViewModelStoreOwner`. A ViewModel retrieved inside a composable using `viewModel()` is scoped to that specific `NavBackStackEntry` and is automatically cleared when popped from the backstack."
            },
            {
                "interviewer": "What is the difference between Deep Links and Android App Links?",
                "answer": "Deep Links use custom URI schemes (e.g., `myapp://`) and trigger a system chooser if multiple apps support them. Android App Links use verified HTTP/HTTPS domains backed by a server `assetlinks.json` file, opening your verified app directly without dialogs."
            },
            {
                "interviewer": "How do you share a ViewModel between two destinations in Compose Navigation?",
                "answer": "By retrieving the parent destination's `NavBackStackEntry` via `remember(backStackEntry) { navController.getBackStackEntry(\"parent_route\") }` and passing it to the `viewModel(viewModelStoreOwner = parentEntry)` factory."
            }
        ]
    },
    {
        "id": "AND-16",
        "arabic_explanation": (
            "حماية المكونات المكشوفة (Exported Android Components) هي أحد أهم متطلبات الأمان والتصدي لثغرات الاختراق في تطبيقات Android:\n\n"
            "1. ما هو المكون المكشوف (Exported Component)؟\n"
            "   - هو أي Activity أو Service أو BroadcastReceiver أو ContentProvider يمكن لأي تطبيق آخر مثبت على نفس هاتف المستخدم استدعاؤه وتشغيله!\n"
            "   - في أندرويد 12+، يجب تحديد `android:exported=\"true\"` أو `\"false\"` صراحة لكل مكون يحتوي على `<intent-filter>`.\n\n"
            "2. ما هي الثغرات المحتملة؟\n"
            "   - **تجاوز المصادقة (Auth Bypass):** لو كانت شاشة الدفع أو لوحة التحكم الخاصة بالمسؤول `exported=\"true\"`، يستطيع تطبيق خبيث تشغيلها مباشرة عبر Intent وتجاوز شاشة تسجيل الدخول والـ PIN code!\n"
            "   - **سرقة وتعديل البيانات (Data Leakage):** لو كان الـ ContentProvider مكشوفاً بدون حماية، يمكن لأي تطبيق قراءة وتعديل جداول قاعدة بياناتك.\n\n"
            "3. كيف تحمي المكونات المكشوفة باحترافية (The Defense Strategies)؟\n"
            "   - **القاعدة الأولى: `android:exported=\"false\"` افتراضياً:** أي مكون مخصص للاستخدام الداخلي فقط يجب أن يكون `exported=\"false\"`.\n"
            "   - **القاعدة الثانية: حماية المكونات المكشوفة بـ Permissions:** لو المكون يجب أن يُستدعى من تطبيقاتك الأخرى، احمهِ بـ `<permission>` مخصص بمستوى حماية `android:protectionLevel=\"signature\"`. هذا يضمن أن التطبيقات الموقعة بنفس الـ Keystore الشهادة فقط هي التي تستطيع مناداته!\n"
            "   - **القاعدة الثالثة: التحقق الصارم من المدخلات (Intent Input Validation):** فحص جميع الـ Extras القادمة من الـ Intent والـ Calling UID."
        ),
        "practical_walkthrough": (
            "كود حماية المكونات في `AndroidManifest.xml`:\n"
            "```xml\n"
            "<manifest ...>\n"
            "    <!-- 1. تعريف إذن مخصص بمستوى حماية التوقيع: -->\n"
            "    <permission\n"
            "        android:name=\"com.example.myapp.permission.SYNC_DATA\"\n"
            "        android:protectionLevel=\"signature\" />\n"
            "\n"
            "    <application ...>\n"
            "        <!-- 2. مكون داخلي: محمي بـ exported=\"false\": -->\n"
            "        <activity\n"
            "            android:name=\".AdminSettingsActivity\"\n"
            "            android:exported=\"false\" />\n"
            "\n"
            "        <!-- 3. مكون خارجي لكنه محمي بإذن التوقيع: -->\n"
            "        <service\n"
            "            android:name=\".SyncService\"\n"
            "            android:exported=\"true\"\n"
            "            android:permission=\"com.example.myapp.permission.SYNC_DATA\" />\n"
            "    </application>\n"
            "</manifest>\n"
            "```"
        ),
        "quick_answer": "Protect exported components by defaulting to android:exported='false'. For components that must be exported, enforce custom permissions with android:protectionLevel='signature' so only apps sharing your signing key can access them, and validate all incoming Intent extras and caller UIDs.",
        "best_answer": (
            "Securing exported Android components is a fundamental pillar of mobile application security:\n\n"
            "1. **Enforce Least Privilege (`android:exported=\"false\"`)**: By default, every component intended strictly for internal app usage must explicitly declare `android:exported=\"false\"`. This completely blocks foreign apps from launching internal activities, triggering services, or snooping on internal broadcasts.\n\n"
            "2. **Signature-level Permissions for Inter-App Communication**: If a component must be shared between multiple apps in your company's suite, declare a custom permission with `android:protectionLevel=\"signature\"`. The Android OS verifies the cryptographic signing certificate of the calling application: only apps signed with your exact release signing key can invoke the component.\n\n"
            "3. **Validate Intent Ingress & Calling Identity**: For public components (like Deep Link entry activities), never trust incoming extras. Sanitize all URIs to prevent path traversal attacks, and inspect `callingUid` via `Binder.getCallingUid()` when validating IPC callers.\n\n"
            "4. **Secure ContentProviders**: Set `android:grantUriPermissions=\"true\"` with temporary URI flags (`FLAG_GRANT_READ_URI_PERMISSION`) rather than granting permanent world-readable access."
        ),
        "deep_answer": (
            "From a penetration testing and vulnerability analysis perspective, exported components are the #1 attack vector in Android. "
            "A malicious app installed on the same device can use `PackageManager` and `adb shell am start` to probe unprotected exported components.\n\n"
            "Common critical vulnerabilities include:\n\n"
            "- **Intent Spoofing / Injection**: An attacker fires an implicit broadcast or crafts an intent targeting an exported BroadcastReceiver with spoofed parameters (e.g., simulating a successful payment event).\n"
            "- **SQL Injection in ContentProviders**: Exported ContentProviders that pass raw query parameters directly into SQLite without parameterized `?` arguments allow arbitrary database exfiltration.\n"
            "- **PendingIntent Hijacking**: If an exported component returns a mutable PendingIntent (`FLAG_MUTABLE`), an attacking app can use `Intent.fillIn()` to alter the destination and hijack the victim app's identity.\n\n"
            "Enforcing static analysis scanning in CI via tools like MobSF or Android Lint (`ExportedService`, `ExportedReceiver`) ensures zero unauthorized exported components reach production."
        ),
        "follow_ups": [
            {
                "interviewer": "What does `android:protectionLevel=\"signature\"` mean?",
                "answer": "It means the system grants the permission only if the requesting application is signed with the exact same certificate as the application that declared the permission. It provides cryptographically secure inter-app communication between your own apps."
            },
            {
                "interviewer": "Can a ContentProvider be protected with separate read and write permissions?",
                "answer": "Yes. A ContentProvider can declare `android:readPermission` and `android:writePermission` separately, allowing third-party apps to read public data while restricting data modifications."
            },
            {
                "interviewer": "Why did Android 12 make `android:exported` mandatory in manifests?",
                "answer": "Historically, if an intent-filter was present, Android defaulted `exported` to `true`. Many developers forgot this, inadvertently exposing thousands of internal activities to the public OS. Android 12 forces developers to make an explicit security choice."
            }
        ]
    },
    {
        "id": "AND-17",
        "arabic_explanation": (
            "تسجيل وإلغاء المستمعين المعتمدين على دورة الحياة (Registering/Unregistering Lifecycle-Dependent Listeners) هو الاختبار الحقيقي لمعرفة ما إذا كان المهندس يكتب كوداً نظيفاً يمنع تسريب الذاكرة:\n\n"
            "1. النهج القديم السيئ (The Deprecated / Cluttered Approach):\n"
            "   - كتابة كود التسجيل والفصل داخل دوال الـ Activity نفسها (`onStart` و `onStop`):\n"
            "     * المشكلة: تضخم كود الـ Activity (God Activity)، وصعوبة إعادة استخدام المستمع، ونسيان فصل المستمع مما يسبب تسريب الذاكرة (Memory Leak).\n\n"
            "2. النهج الحديث المعياري: `DefaultLifecycleObserver`:\n"
            "   - إنشاء كلاس مستقل للمستمع ينفذ واجهة `DefaultLifecycleObserver`.\n"
            "   - الكلاس يتولى تسجيل نفسه في `onStart()` وإلغاء تسجيله تلقائياً في `onStop()`.\n"
            "   - الـ Activity تضيف سطراً واحداً فقط: `lifecycle.addObserver(myListener)`.\n\n"
            "3. مطابقة أزواج دورة الحياة بدقة (Symmetric Pairs):\n"
            "   - **لو سجلت في `onCreate()`:** يجب الإلغاء في **`onDestroy()`**.\n"
            "   - **لو سجلت في `onStart()`:** يجب الإلغاء في **`onStop()`** (الأكثر شيوعاً للمستشعرات والـ Location).\n"
            "   - **لو سجلت في `onResume()`:** يجب الإلغاء في **`onPause()`** (للكاميرا أو مستشعرات الحركة الحساسة جداً)."
        ),
        "practical_walkthrough": (
            "بناء مستمع موقع جغرافي ذاتي الإدارة (Self-contained Lifecycle Observer):\n"
            "```kotlin\n"
            "class LocationTracker(\n"
            "    private val context: Context,\n"
            "    private val onLocationChanged: (Location) -> Unit\n"
            ") : DefaultLifecycleObserver {\n"
            "\n"
            "    override fun onStart(owner: LifecycleOwner) {\n"
            "        // 1. تسجيل المستمع عندما تصبح الشاشة مرئية:\n"
            "        startGpsUpdates()\n"
            "    }\n"
            "\n"
            "    override fun onStop(owner: LifecycleOwner) {\n"
            "        // 2. إلغاء المستمع تلقائياً عندما تختفي الشاشة:\n"
            "        stopGpsUpdates()\n"
            "    }\n"
            "}\n"
            "\n"
            "// في الـ Activity أو Fragment: سطر واحد فقط نظيف:\n"
            "class MapActivity : AppCompatActivity() {\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        val tracker = LocationTracker(this) { updatePin(it) }\n"
            "        lifecycle.addObserver(tracker) // يربط نفسه بدورة الحياة تلقائياً بدون تكرار كود\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Encapsulate listeners inside standalone classes implementing DefaultLifecycleObserver, matching symmetric lifecycle pairs: onStart/onStop for sensors and visibility, onResume/onPause for camera, and onCreate/onDestroy for hardware resources, registered via lifecycle.addObserver().",
        "best_answer": (
            "The modern, professional way to manage lifecycle-dependent listeners is by implementing **`DefaultLifecycleObserver`** inside a dedicated, self-contained component rather than cluttering Activity callbacks.\n\n"
            "To prevent memory leaks and battery drain, listeners must follow strict **symmetric lifecycle pairing**:\n\n"
            "1. **`onStart()` and `onStop()` (Standard Default)**: Use for location updates, network monitoring, and UI data streams. The listener registers when the app is visible and unregisters the moment the app is backgrounded, conserving device battery.\n"
            "2. **`onResume()` and `onPause()`**: Use for exclusive foreground hardware that cannot be shared in multi-window mode, such as the camera hardware or high-frequency accelerometer sensors.\n\n"
            "The calling Activity or Fragment simply hooks the component using `lifecycle.addObserver(myListener)`. When the host is destroyed, the lifecycle observer is automatically torn down without manual Activity boilerplate."
        ),
        "deep_answer": (
            "Under the hood, `androidx.lifecycle.LifecycleRegistry` manages an internal state machine. "
            "When you call `lifecycle.addObserver()`, the registry automatically brings the newly added observer up to the current state of the owner (e.g., if added in `onResume`, it immediately executes `onCreate`, `onStart`, and `onResume` in sequence).\n\n"
            "When working with Jetpack Compose, the equivalent paradigm is **`DisposableEffect`**:\n\n"
            "```kotlin\n"
            "DisposableEffect(lifecycleOwner) {\n"
            "    val observer = LifecycleEventObserver { _, event ->\n"
            "        if (event == Lifecycle.Event.ON_START) startListening()\n"
            "        else if (event == Lifecycle.Event.ON_STOP) stopListening()\n"
            "    }\n"
            "    lifecycleOwner.lifecycle.addObserver(observer)\n"
            "    onDispose {\n"
            "        lifecycleOwner.lifecycle.removeObserver(observer)\n"
            "    }\n"
            "}\n"
            "```\n\n"
            "`onDispose` guarantees that the listener is detached when the Composable leaves composition, preventing dangling callbacks."
        ),
        "follow_ups": [
            {
                "interviewer": "Why did `LifecycleObserver` with `@OnLifecycleEvent` annotations get deprecated?",
                "answer": "Because it relied on runtime reflection or compile-time annotation processing code generation. `DefaultLifecycleObserver` uses Java 8 default interface methods, providing direct, fast method invocation with zero reflection overhead."
            },
            {
                "interviewer": "What happens if a listener is registered in `onStart` but unregistered in `onDestroy`?",
                "answer": "Asymmetry bug! Every time the Activity is stopped and restarted (e.g., user presses Home and returns), `onStart` registers another duplicate listener without unregistering the old one, leaking callbacks and stacking duplicate events."
            },
            {
                "interviewer": "How does `repeatOnLifecycle` simplify this for Flows?",
                "answer": "`repeatOnLifecycle` encapsulates this exact onStart/onStop pairing declaratively for coroutines: it launches flow collection on `ON_START` and cancels the coroutine on `ON_STOP` automatically."
            }
        ]
    },
    {
        "id": "AND-18",
        "arabic_explanation": (
            "تأثير الـ Multi-Window (تقسيم الشاشة)، التدوير (Rotation)، والانتقال بين الخلفية والمقدمة (Background/Foreground) على حالة التطبيق:\n\n"
            "1. الـ Multi-Window / Split-Screen (تقسيم الشاشة):\n"
            "   - في وضع تقسيم الشاشة، قد يكون تطبيقك **مرئياً تماماً على الشاشة ولكنه ليس في بؤرة التركيز التفاعلي (Visible but Not Focused)** لأن المستخدم يتفاعل مع التطبيق الآخر في النصف الثاني!\n"
            "   - **حالة الـ Lifecycle:** التطبيق يكون في حالة **`onStart()` / `onPause()`** (أو `RESUMED` في أندرويد 10+ مع ميزة Multi-resume)!\n"
            "   - **الخطأ الكارثي:** لو كنت توقف تحديثات الفيديو أو الرسوم في `onPause()`، فالفيديو سيتوقف ويتجمد أمام عيني المستخدم في وضع تقسيم الشاشة! لذلك يجب إيقاف الفيديو والرسوم في **`onStop()`**، وليس في `onPause()`.\n\n"
            "2. الـ Rotation (تدوير الشاشة):\n"
            "   - يدمر الـ Activity ويعيد بناؤها بالكامل (`onDestroy` -> `onCreate`).\n"
            "   - الـ ViewModel والـ SavedStateHandle ينجوان في الذاكرة.\n\n"
            "3. الـ Background / Foreground Transitions:\n"
            "   - عند الانتقال للخلفية: تستدعى `onPause()` ثم `onStop()`. يدخل التطبيق في تجمع الـ 'Killable' للـ Low Memory Killer.\n"
            "   - حفظ الحالة الإلزامي يتم في `onSaveInstanceState(Bundle)` قبل أن يصبح التطبيق عرضة للـ Process Death."
        ),
        "practical_walkthrough": (
            "تطبيق عملي: مشغل فيديو (Video Player) في وضع Multi-Window:\n"
            "```kotlin\n"
            "class VideoPlayerActivity : AppCompatActivity() {\n"
            "    private var player: ExoPlayer? = null\n"
            "\n"
            "    override fun onStart() {\n"
            "        super.onStart()\n"
            "        // 1. نبدأ تشغيل الفيديو في onStart حتى يعمل في وضع Multi-Window بسلاسة:\n"
            "        initializePlayer()\n"
            "    }\n"
            "\n"
            "    override fun onStop() {\n"
            "        super.onStop()\n"
            "        // 2. نحرر الـ Player في onStop عندما تختفي الشاشة تماماً عن عين المستخدم:\n"
            "        releasePlayer()\n"
            "    }\n"
            "    // لا نوقف الفيديو في onPause() أبداً حتى لا يتجمد في Split-screen!\n"
            "}\n"
            "```"
        ),
        "quick_answer": "In multi-window, the app can be visible (onStart) without having input focus (onPause), so media playback and rendering must be controlled in onStart/onStop, not onResume/onPause. Rotation triggers full Activity recreation with ViewModel preservation, and backgrounding moves the app to onStop where it becomes killable by the OS.",
        "best_answer": (
            "These three transitions impact Android lifecycle states and resource management differently:\n\n"
            "1. **Multi-Window / Foldable Resizing**: The app shares screen real estate with another process. The app is fully visible, but may not have user touch focus. Prior to Android 10, an app without focus was kept in `onPause()`. In Android 10+ with **Multi-Resume**, all visible apps in multi-window remain in `RESUMED`. Therefore, video playback, map rendering, and animations must be bound to **`onStart()` and `onStop()`**; stopping them in `onPause()` causes frozen video playback in split-screen mode.\n\n"
            "2. **Screen Rotation**: Triggers a full Configuration Change: `onPause -> onStop -> onDestroy` followed by recreation. The UI hierarchy and view bindings are destroyed, while the ViewModel and SavedStateHandle survive in memory.\n\n"
            "3. **Background/Foreground Transitions**: Navigating away invokes `onPause()` followed by `onStop()`. The OS calls `onSaveInstanceState()` to serialize state. Once in `onStop()`, the app's process is marked killable by the Low Memory Killer if RAM is constrained."
        ),
        "deep_answer": (
            "On modern **Foldable devices** (e.g., Samsung Galaxy Fold, Google Pixel Fold), unfolding the device transitions the app from a compact external display to a large unfolded inner display. "
            "This triggers dynamic configuration changes where screen size, aspect ratio, and smallest screen width (`sw600dp`) change on the fly.\n\n"
            "To support foldables seamlessly in modern architecture: "
            "1. Use **Jetpack WindowManager** (`WindowInfoTracker.getOrCreate(context).windowLayoutInfo(activity)`) to observe folding postures (Flat, Half-Opened / Tabletop mode, and display hinge folding features). "
            "2. Adopt adaptive UI layouts with Compose (`calculateWindowSizeClass()`), switching dynamically between single-pane, list-detail, and supporting pane layouts without manual Activity recreation hacks."
        ),
        "follow_ups": [
            {
                "interviewer": "What is 'Multi-Resume' in Android 10+?",
                "answer": "In Android 10 (API 29) and above, all visible activities in multi-window mode or split-screen are placed in the `RESUMED` state simultaneously, rather than keeping only the top-focused activity resumed."
            },
            {
                "interviewer": "How does `isInMultiWindowMode` help?",
                "answer": "It is an Activity method (`isInMultiWindowMode`) that returns a boolean indicating whether the activity is currently operating in multi-window split-screen mode, allowing customized UI layouts."
            },
            {
                "interviewer": "Why must you avoid fixed orientation lock (`android:screenOrientation=\"portrait\"`) on foldables and tablets?",
                "answer": "Locking orientation is explicitly ignored or letterboxed by Android 12L+ on large screens and foldables to prevent broken user experiences. Apps must support fluid multi-orientation layouts."
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

    for q in AND_13_18:
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
    print(f"Updated {DATA_FILE} with questions AND-13 to AND-18. Total questions: {len(combined)}")


if __name__ == "__main__":
    main()

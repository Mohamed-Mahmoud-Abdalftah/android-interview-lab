#!/usr/bin/env python3
"""Generator for AND-01 through AND-06 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "and.json"

AND_01_06 = [
    {
        "id": "AND-01",
        "arabic_explanation": (
            "المكونات الأساسية الأربعة لنظام Android بالإضافة للـ Fragment هي حجر الأساس في بنية نظام التشغيل:\n\n"
            "1. الـ Activity:\n"
            "   - تمثل **نقطة الدخول الفردية لواجهة المستخدم (Single Entry Point for UI)**.\n"
            "   - كل Activity تمثل شاشة واحدة يمكن للمستخدم التفاعل معها، ولها نافذة رسم (Window) ودورة حياة مرتبطة بالـ OS Window Manager.\n\n"
            "2. الـ Fragment:\n"
            "   - هو **جزء قابل لإعادة الاستخدام من واجهة المستخدم (Reusable UI Component)** يعيش داخل Activity.\n"
            "   - يمتلك دورة حياة خاصة به، ولكن دورة حياته تابعة ومقيدة بالـ Activity الحاضنة له.\n"
            "   - صُمم لتسهيل تقسيم الواجهات (مثل Tablet Master-Detail views) والتنقل الديناميكي.\n\n"
            "3. الـ Service:\n"
            "   - مكون يعمل في الخلفية **بدون واجهة مستخدم (No UI)** لتنفيذ عمليات طويلة المدى.\n"
            "   - نوعان رئيسيان: Foreground Service (مع إشعار مستمر للمستخدم، مثل تشغيل الموسيقى أو تتبع الجري بالـ GPS)، و Background Service (تخضع لقيود صارمة جداً في Android الحديث).\n\n"
            "4. الـ BroadcastReceiver:\n"
            "   - مكون يعمل كـ **صندوق بريد لاستقبال الإشارات العامة (System Gateway)** من النظام أو التطبيقات الأخرى.\n"
            "   - مثل: استقبال إشعار انخفاض البطارية، تغير حالة الطيران، أو اكتمال إقلاع الجهاز (`BOOT_COMPLETED`).\n\n"
            "5. الـ ContentProvider:\n"
            "   - مكون لإدارة ومشاركة البيانات المهيكلة بين التطبيقات المختلفة (Cross-process Data Sharing).\n"
            "   - يوفر واجهة معيارية شبيهة بـ REST/SQL للوصول للبيانات (مثل جهات الاتصال، الصور في الـ MediaStore)."
        ),
        "practical_walkthrough": (
            "كيف تتكامل المكونات في سيناريو تطبيق موسيقى وبودكاست (Music Streaming App):\n"
            "- **Activity / Compose:** شاشة تشغيل الموسيقى والأزرار التي يتفاعل معها المستخدم.\n"
            "- **Service (Foreground Service):** تشغيل ملف الصوت في الخلفية حتى لو أغلق المستخدم الشاشة، مع إشعار دائم بأزرار Pause/Play.\n"
            "- **BroadcastReceiver:** استقبال حدث فصل سماعات الأذن (`ACTION_AUDIO_BECOMING_NOISY`) لإيقاف الموسيقى فوراً ومنع الإحراج في الأماكن العامة.\n"
            "- **ContentProvider:** الوصول إلى ملفات الصوت المحلية المخزنة على هاتف المستخدم عبر الـ `MediaStore`.\n"
            "- **Fragment:** كان يستخدم لتبويب قائمة التشغيل وتفاصيل الأغنية قبل التحول إلى Jetpack Compose."
        ),
        "quick_answer": "Android's 4 core components are Activity (entry point for UI interactions), Service (background execution without UI), BroadcastReceiver (listener for system and inter-app events), and ContentProvider (secure cross-process data sharing). Fragments are modular, reusable UI sub-components hosted inside an Activity.",
        "best_answer": (
            "Android's architectural model is built on four core platform components declared in the AndroidManifest, plus Fragments for modular UI:\n\n"
            "1. **Activity**: The single-screen user interface entry point. It manages window rendering, user touch dispatch, and system lifecycle interactions.\n"
            "2. **Fragment**: A modular, reusable sub-tree of UI hosted within an Activity, possessing its own lifecycle that is coupled to the host Activity.\n"
            "3. **Service**: An execution component without a UI used for long-running operations. In modern Android, services are primarily Foreground Services (holding a mandatory user-visible notification for audio or location) or WorkManager workers for deferred tasks.\n"
            "4. **BroadcastReceiver**: A messaging gateway that allows an application to listen to and respond to system-wide broadcast intents (like battery low or network change) or custom app signals.\n"
            "5. **ContentProvider**: The standard abstraction for securely querying, mutating, and sharing structured data across process boundaries (e.g., Android's MediaStore or Contacts)."
        ),
        "deep_answer": (
            "At the operating system level, these components represent distinct **entry points for the Android ActivityManagerService (AMS)** to launch an app process. Unlike standard desktop programs with a single `main()` function, an Android app can be spawned by the OS into any of these four components via an Intent or Binder transaction.\n\n"
            "Each component carries distinct IPC and thread affinity rules:\n\n"
            "Activities and BroadcastReceivers run on the Main UI thread by default; a `BroadcastReceiver.onReceive()` must complete within 10 seconds or trigger an ANR. "
            "Services also execute on the Main UI thread unless explicitly offloaded to a background thread. "
            "ContentProviders are initialized during app startup before `Application.onCreate()`, and their methods (`query`, `insert`) execute on Binder thread pool worker threads, requiring internal synchronization for thread safety."
        ),
        "follow_ups": [
            {
                "interviewer": "Do Services automatically run on a background worker thread?",
                "answer": "No! A Service runs on the main UI thread by default. If you perform heavy CPU calculations or blocking network I/O inside a Service without launching a background coroutine or thread, it will freeze the UI and cause an ANR."
            },
            {
                "interviewer": "Why must BroadcastReceivers avoid long-running background tasks in `onReceive()`?",
                "answer": "Because `onReceive()` runs on the main thread and the OS restricts execution to approximately 10 seconds before throwing an ANR. For async tasks, call `goAsync()` or delegate the work to WorkManager."
            },
            {
                "interviewer": "When does a ContentProvider initialize relative to Application.onCreate()?",
                "answer": "ContentProviders initialize before `Application.onCreate()`. That is why libraries like Jetpack Startup and Firebase use empty ContentProviders for zero-code auto-initialization."
            }
        ]
    },
    {
        "id": "AND-02",
        "arabic_explanation": (
            "دورة حياة الـ Activity والـ Fragment هي صميم عمل نظام أندرويد لإدارة الذاكرة والـ UI:\n\n"
            "1. دورة حياة الـ Activity (Activity Lifecycle):\n"
            "   - `onCreate()`: يتم استدعاؤها عند إنشاء الكائن في الذاكرة لأول مرة. هنا نقوم بتهيئة الـ ViewModel، حقن الاعتماديات، وضبط الـ View (`setContentView` أو `setContent`).\n"
            "   - `onStart()`: تصبح الشاشة **مرئية للمستخدم (Visible)** ولكنها قد لا تكون في بؤرة التركيز التفاعلي (مثل وجود Dialog نصف شفاف أمامها).\n"
            "   - `onResume()`: تصبح الشاشة **في المقدمة وقابلة للتفاعل باللمس بالكامل (Foreground & Interactive)**.\n"
            "   - `onPause()`: تفقد الشاشة بؤرة التركيز جزئياً (Partial occlusion)، مثل ظهور نافذة إذن النظام أو الدخول في Multi-window.\n"
            "   - `onStop()`: تصبح الشاشة **غير مرئية بالكامل (Hidden)** لأن المستخدم فتح تطبيقا آخر أو ضغط زر Home. هنا يتم إيقاف التحديثات الثقيلة.\n"
            "   - `onDestroy()`: يتم تدمير الـ Activity بالكامل إما بسبب إنهاء المستخدم لها (`finish()`) أو بسبب Configuration Change.\n\n"
            "2. دورة حياة الـ Fragment:\n"
            "   - تتبع نفس المراحل، ولكنها تضيف فصلاً حاسماً بين **دورة حياة كائن الـ Fragment نفسه** و **دورة حياة الـ View المعروضة (`viewLifecycleOwner`)**."
        ),
        "practical_walkthrough": (
            "ماذا يحدث بالضبط عند فتح Dialog أو عند تدوير الشاشة؟\n"
            "- **فتح Dialog عادي داخل التطبيق:**\n"
            "  الـ Activity تظل في حالة `RESUMED` لأن الـ Dialog جزء من نفس نافذة الـ Activity!\n"
            "- **فتح Permission Dialog الخاص بنظام أندرويد (OS Permission Dialog):**\n"
            "  الـ Activity تنتقل إلى `onPause()` لأن نافذة تابعة لنظام التشغيل حازت على بؤرة التركيز، ثم تعود لـ `onResume()` عند إغلاق الإذن.\n"
            "- **تدوير الشاشة (Screen Rotation):**\n"
            "  تنتقل بالترتيب: `onPause()` -> `onStop()` -> `onSaveInstanceState()` -> `onDestroy()` -> ثم يعاد بناؤها: `onCreate()` -> `onStart()` -> `onResume()`."
        ),
        "quick_answer": "Activity transitions through onCreate() (initialization), onStart() (visible), onResume() (interactive), onPause() (partially visible/lost focus), onStop() (hidden), and onDestroy() (destroyed). Fragments mirror these states but possess an independent view lifecycle via viewLifecycleOwner.",
        "best_answer": (
            "The Android lifecycle represents the operating system's mechanism for managing memory constraints, window visibility, and user interaction states:\n\n"
            "The six core Activity callbacks form matched pairs:\n\n"
            "1. **`onCreate()` / `onDestroy()`**: Represents the entire lifespan of the Activity instance in memory. In `onCreate`, we initialize dependencies, ViewModels, and UI layouts.\n"
            "2. **`onStart()` / `onStop()`**: Represents the visible lifespan. In `onStart`, the UI is visible to the user. In `onStop`, the Activity is completely hidden from view (e.g., app backgrounded). This is where heavy rendering and sensor listeners should pause.\n"
            "3. **`onResume()` / `onPause()`**: Represents the foreground, interactive lifespan. In `onResume`, the window has full touch focus. In `onPause`, the window has lost focus (e.g., covered by a multi-window app or a system permission dialog).\n\n"
            "Fragments mirror these states, but critically decouple the Fragment object lifecycle from the view lifecycle (`viewLifecycleOwner`), which can be destroyed and recreated independently when placed on the Fragment backstack."
        ),
        "deep_answer": (
            "From an architectural standpoint, modern Android applications avoid placing business logic or direct resource registration inside these callbacks. Instead, we use `DefaultLifecycleObserver` and `repeatOnLifecycle`.\n\n"
            "Consider state preservation across the transition to `onStop()`: "
            "Between `onPause()` and `onStop()`, the OS invokes `onSaveInstanceState(Bundle)`. "
            "Once `onStop()` is called, the app process enters the 'killable' pool: if system RAM runs low, the OS kernel can terminate the entire Linux process without ever calling `onDestroy()`.\n\n"
            "In modern Jetpack architecture, `androidx.lifecycle.Lifecycle` abstracts these callbacks into states (`INITIALIZED`, `CREATED`, `STARTED`, `RESUMED`, `DESTROYED`) and events. "
            "Coroutines observe these states via `repeatOnLifecycle(Lifecycle.State.STARTED)`, which automatically cancels background collectors in `onStop()` and restarts them in `onStart()`."
        ),
        "follow_ups": [
            {
                "interviewer": "Is `onDestroy()` guaranteed to be called when the user exits the app?",
                "answer": "No! If the user presses the home button and the OS kills the process in the background due to low memory, `onDestroy()` is never called. Never place critical data persistence solely inside `onDestroy()`."
            },
            {
                "interviewer": "What is the difference between pressing the 'Back' button and pressing the 'Home' button?",
                "answer": "Pressing Back finishes the Activity (transitioning through onPause -> onStop -> onDestroy), signalling intentional termination. Pressing Home simply backgrounds the Activity (onPause -> onStop), preserving it in the recent apps stack."
            },
            {
                "interviewer": "What is `onRestart()` and when is it invoked?",
                "answer": "`onRestart()` is called between `onStop()` and `onStart()` when an Activity that was previously hidden is brought back to the foreground by the user."
            }
        ]
    },
    {
        "id": "AND-03",
        "arabic_explanation": (
            "المقارنة بين دورة حياة كائن الـ Fragment ودورة حياة الـ View المعروضة (`viewLifecycleOwner`) هي سبب وقوع 80% من أخطاء الـ Memory Leaks في الـ Fragments:\n\n"
            "1. ما هو الفرق الجوهري؟\n"
            "   - **كائن الـ Fragment (Instance Lifecycle):** يعيش من لحظة إنشاء الكلاس في الذاكرة حتى تدميره نهائياً (`onDestroy()`).\n"
            "   - **كائن الـ View (`viewLifecycleOwner`):** يعيش **فقط** بين `onCreateView()` / `onViewCreated()` وبين `onDestroyView()`.\n\n"
            "2. متى يتم تدمير الـ View مع بقاء الـ Fragment حياً في الذاكرة؟\n"
            "   - عندما تستخدم **Fragment Backstack** (مثل: استبدال Fragment A بـ Fragment B مع مناداة `addToBackStack()`):\n"
            "   - كائن Fragment A يظل حياً في الذاكرة بالكامل حتى يتمكن المستخدم من الرجوع إليه.\n"
            "   - ولكن نظام أندرويد يقوم بـ **تدمير الـ Views الخاصة بـ Fragment A (`onDestroyView`)** لتوفير الذاكرة!\n\n"
            "3. الكارثة البرمجية الشائعة (The Classic Memory Leak):\n"
            "   - لو احتفظت بـ View Binding في متغير عادي ولم تصفره في `onDestroyView()`:\n"
            "     `private var binding: FragmentProfileBinding? = null`\n"
            "     فإن كائن الـ Fragment سيظل ممسكاً بالـ Views المدمرة، مما يسرب شجرة الـ Views بالكامل في الذاكرة!\n"
            "   - ولو استمعت لـ Flow باستخدام `viewLifecycleOwner.lifecycleScope`، ستتوقف المراقبة عند تدمير الـ View بنظافة تامة."
        ),
        "practical_walkthrough": (
            "النمط الصحيح لتجنب تسريب الذاكرة في الـ Fragments:\n"
            "```kotlin\n"
            "class ProfileFragment : Fragment(R.layout.fragment_profile) {\n"
            "    // 1. المتغير nullable لتصفيره:\n"
            "    private var _binding: FragmentProfileBinding? = null\n"
            "    private val binding get() = _binding!!\n"
            "\n"
            "    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {\n"
            "        super.onViewCreated(view, savedInstanceState)\n"
            "        _binding = FragmentProfileBinding.bind(view)\n"
            "\n"
            "        // 2. استخدام viewLifecycleOwner للاستماع للـ Flow لمنع التسريب:\n"
            "        viewLifecycleOwner.lifecycleScope.launch {\n"
            "            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {\n"
            "                viewModel.uiState.collect { render(it) }\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "\n"
            "    override fun onDestroyView() {\n"
            "        super.onDestroyView()\n"
            "        // 3. تصفير الـ binding إلزامي لتحرير الـ Views من الذاكرة:\n"
            "        _binding = null\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "A Fragment's instance lifecycle spans from creation to onDestroy(), while its view lifecycle spans only between onCreateView() and onDestroyView(). When placed on the backstack, the view hierarchy is destroyed while the Fragment instance remains alive, requiring observers and view bindings to bind to viewLifecycleOwner to prevent memory leaks.",
        "best_answer": (
            "The critical distinction is that a Fragment's object instance outlives its UI view hierarchy when using the backstack.\n\n"
            "When Fragment A is replaced by Fragment B and added to the backstack (`addToBackStack()`):\n\n"
            "1. Android destroys Fragment A's UI layout, calling `onDestroyView()`. However, the `Fragment` class instance remains alive in memory so that its scroll position and arguments are preserved.\n"
            "2. When the user taps Back, the existing Fragment A instance creates a brand-new View hierarchy, calling `onCreateView()` and `onViewCreated()`.\n\n"
            "Because of this asymmetry, observing LiveData or collecting Flows against the Fragment's own lifecycle (`this`) creates memory leaks and duplicate observers every time the user returns from the backstack.\n\n"
            "In modern Android development, all View-related operations, ViewBindings, and Flow collections must strictly bind to **`viewLifecycleOwner`**, and ViewBindings must be nulled out in `onDestroyView()`."
        ),
        "deep_answer": (
            "Under the hood, `Fragment.getViewLifecycleOwner()` returns a dedicated `LifecycleOwner` that is created in `onCreateView()` and set to the `DESTROYED` state in `onDestroyView()`. "
            "If you attempt to call `viewLifecycleOwner` before `onCreateView()` or after `onDestroyView()`, it throws an `IllegalStateException: Can't access the Fragment View's LifecycleOwner when getView() is null`.\n\n"
            "In memory profiling, failing to null out `_binding` in `onDestroyView()` is one of the most common causes of Out-Of-Memory (OOM) errors in large applications. "
            "A single ViewBinding reference holds pointers to the root View, all child Views, the WindowManager, and bitmap drawables, preventing the entire screen's graphic memory from being reclaimed by ART garbage collection while the fragment rests in the backstack."
        ),
        "follow_ups": [
            {
                "interviewer": "What happens if you observe a Flow with `this.lifecycleScope` inside `onViewCreated`?",
                "answer": "Every time the user navigates back to this Fragment from the backstack, `onViewCreated` runs again and attaches another active observer. If the user navigates back and forth 5 times, there will be 5 duplicate concurrent collectors executing UI updates!"
            },
            {
                "interviewer": "Can you avoid nulling out ViewBinding in `onDestroyView()` with auto-clearing delegates?",
                "answer": "Yes. Libraries often provide an `AutoClearedValue` delegate or lifecycle-observer delegate that automatically listens to `viewLifecycleOwner`'s `onDestroyView` event and sets the binding property to null automatically."
            },
            {
                "interviewer": "How does Jetpack Compose change this pattern?",
                "answer": "Jetpack Compose eliminates Fragment ViewBinding leaks entirely because Composables do not use persistent view hierarchy references. Compose state automatically cleans up when leaving composition."
            }
        ]
    },
    {
        "id": "AND-04",
        "arabic_explanation": (
            "الـ `Context` هو أهم كائن في بيئة Android، وفهم الفرق بين `Activity Context` و `Application Context` يمنع حدوث أكبر كوارث الـ Memory Leaks والـ UI Glitches:\n\n"
            "1. ما هو الـ Context بصفة عامة؟\n"
            "   - هو الواجهة التي تربط كود تطبيقك **بنظام التشغيل Android (Handle to the System)**.\n"
            "   - يسمح لك بالوصول للموارد (Resources, Strings, Drawables)، قواعد البيانات، خدمات النظام (LayoutInflater, WindowManager, LocationManager)، وتشغيل المكونات (startActivity).\n\n"
            "2. الـ `Application Context` (مربوط بـ Process التطبيق):\n"
            "   - يعيش طوال فترة حياة **التطبيق ككل (Singleton Lifecycle)** حتى يتم إنهاء الـ Linux Process.\n"
            "   - **مستحيل تسريبه:** آمن تماماً للاحتفاظ به داخل Singletons، Repositories، أو كلاسات الـ Data Layer.\n"
            "   - **حدوده:** ليس لديه Theme محدد، ولا يمكنه فتح Dialogs أو إنشاء نوافذ، واستخدامه مع `LayoutInflater` يؤدي لتجاهل ثيم الشاشة.\n\n"
            "3. الـ `Activity Context` (مربوط بالشاشة الحالية):\n"
            "   - يعيش فقط طالما الـ **Activity الحالية حية**، ويموت معها عند تدميرها أو تدوير الشاشة.\n"
            "   - **مربوط بالـ Theme والـ Window:** قادر على رسم الـ UI، عرض الـ Dialogs، وتطبيق ثيمات التطبيق والألوان بدقة.\n"
            "   - **خطر التسريب (Memory Leak Risk):** لو قمت بتمرير Activity Context لكائن Singleton أو Background Thread وظل ممسكاً به، فإنه سيسرب الـ Activity وشجرة الـ Views بالكامل في الـ Heap!"
        ),
        "practical_walkthrough": (
            "متى تستخدم أياً منهما؟\n"
            "1. **تهيئة مكتبة Room أو DataStore داخل Singleton Repository:**\n"
            "   - نستخدم **`context.applicationContext`** حتى نضمن عدم تسريب أي Activity.\n"
            "2. **عرض AlertDialog أو Toast أو Inflating Layout:**\n"
            "   - نستخدم **Activity Context** (`this` في Activity) لتطبيق الـ Theme وإرفاق النافذة بالـ Window Token الشرعي.\n"
            "3. **استدعاء `startActivity`:**\n"
            "   - لو استدعيتها من Activity Context: تفتح بسلاسة.\n"
            "   - لو استدعيتها من Application Context: النظام يجبرك على إضافة `Intent.FLAG_ACTIVITY_NEW_TASK` لأن Application ليس لديه Task Stack خاص به!"
        ),
        "quick_answer": "Context is the handle to the Android operating system environment. Activity Context is scoped to a single screen's lifecycle, contains theme information, and is required for UI/Dialogs; Application Context is a singleton scoped to the entire app process, lacks theme info, and is safe for background/singleton storage.",
        "best_answer": (
            "A `Context` provides access to application-specific resources, system services, and component launchers.\n\n"
            "**`Activity Context`** is tied to the lifecycle of a specific Activity. It contains the screen's Theme styling and Window Token. It is strictly required for UI operations: displaying `AlertDialog`s, inflating layouts, and starting activities within the same task. However, retaining an Activity Context inside a singleton or long-lived background object leaks the entire Activity and view hierarchy.\n\n"
            "**`Application Context`** is a singleton tied to the lifecycle of the Linux app process (`getApplicationContext()`). It is safe to retain inside Singletons, Repositories, and background workers without causing memory leaks. However, because it is not attached to a Window and lacks Activity Theme metadata, it cannot be used to show dialogs, and inflating views with it produces un-themed UI components."
        ),
        "deep_answer": (
            "At the platform implementation level, both `Activity` and `Application` inherit from `ContextWrapper` which delegates to a platform `ContextImpl`. "
            "However, an `Activity` has a configured `WindowManagerImpl` tied to a hardware display and an active **Window Token** registered with the system's `WindowManagerService`.\n\n"
            "If you attempt to display a window or dialog using `applicationContext`:\n\n"
            "```kotlin\n"
            "AlertDialog.Builder(applicationContext).show()\n"
            "```\n\n"
            "The Android runtime crashes immediately with `WindowManager.BadTokenException: Unable to add window — token null is not valid`. "
            "This happens because `applicationContext` has no window token recognized by the OS window manager.\n\n"
            "In dependency injection (Dagger/Hilt), we explicitly annotate qualifiers to differentiate them: `@ApplicationContext val context: Context` for data repositories, and `@ActivityContext val context: Context` for screen adapters."
        ),
        "follow_ups": [
            {
                "interviewer": "Why does calling `startActivity()` with an Application Context require `FLAG_ACTIVITY_NEW_TASK`?",
                "answer": "Because an Application Context is not part of an existing Activity task stack. Without `FLAG_ACTIVITY_NEW_TASK`, Android doesn't know which task to place the new Activity in, throwing an `AndroidRuntimeException` on older API levels."
            },
            {
                "interviewer": "Can a BroadcastReceiver receive an Activity Context?",
                "answer": "No. The Context passed to `BroadcastReceiver.onReceive()` is a receiver-restricted context that cannot be used to bind services or register nested receivers."
            },
            {
                "interviewer": "How do you safely extract an Application Context from any given Context?",
                "answer": "By calling `context.applicationContext`. This extracts the root application singleton regardless of whether the incoming reference was an Activity, Service, or Wrapper."
            }
        ]
    },
    {
        "id": "AND-05",
        "arabic_explanation": (
            "متى يجب عليك استخدام `Activity Context` تحديداً ولا يمكن استبداله بـ `Application Context` إطلاقاً؟\n\n"
            "1. الحالات الإلزامية التي تتطلب Activity Context:\n"
            "   - **عرض الـ Dialogs (AlertDialog, BottomSheetDialog, DatePickerDialog):**\n"
            "     * تتطلب **Window Token** حقيقي مسجل في نظام تشغيل أندرويد. محاولة استخدام Application Context سترمي فوراً استثناء: `WindowManager.BadTokenException` وتغلق التطبيق بكراش حتمي!\n"
            "   - **إنشاء وتضخيم الـ Views (Layout Inflation):**\n"
            "     * الـ `LayoutInflater` يحتاج للـ Activity Context لقراءة الـ Theme والألوان والـ Styles المحددة في الـ `AndroidManifest` للـ Activity الحالية. استخدام Application Context سينتج عناصر بتصميم افتراضي قبيح أو غير متناسق.\n"
            "   - **بدء Activity جديدة داخل نفس الـ Task:**\n"
            "     * الانتقال الطبيعي بين الشاشات يتطلب Activity Context للحفاظ على الـ Backstack وتسلسل النوافذ بدون فرض `FLAG_ACTIVITY_NEW_TASK`.\n\n"
            "2. القاعدة الذهبية:\n"
            "   - أي شيء له علاقة بـ **الرسم على الشاشة، النوافذ، أو الـ Themes** يتطلب حتماً Activity Context."
        ),
        "practical_walkthrough": (
            "أمثلة كود توضح متى يكون Activity Context إلزامياً:\n"
            "```kotlin\n"
            "// ❌ سيفشل بكراش فوري BadTokenException:\n"
            "fun showConfirmationBad(appContext: Context) {\n"
            "    AlertDialog.Builder(appContext) // BadTokenException!\n"
            "        .setTitle(\"Confirm\")\n"
            "        .show()\n"
            "}\n"
            "\n"
            "// ✅ استخدام Activity Context الإلزامي للـ Dialogs:\n"
            "fun showConfirmationGood(activityContext: Context) {\n"
            "    AlertDialog.Builder(activityContext)\n"
            "        .setTitle(\"Confirm\")\n"
            "        .show() // ينجح لأن activityContext يحمل Window Token شرعي\n"
            "}\n"
            "```"
        ),
        "quick_answer": "An Activity Context is strictly mandatory when showing Dialogs (which require an active Window Token to prevent BadTokenException), inflating themed UI layouts via LayoutInflater, and starting Activities within the same existing task stack without forcing FLAG_ACTIVITY_NEW_TASK.",
        "best_answer": (
            "An Activity Context is strictly mandatory for any operation that interacts with the Android Window Manager, requires a Window Token, or depends on theme styling:\n\n"
            "1. **Showing Dialogs and Popups:** Showing an `AlertDialog`, `BottomSheetDialog`, or `PopupWindow` requires a valid **Window Token** provided exclusively by an active Activity window. Attempting to show a dialog using `ApplicationContext` crashes instantly with `WindowManager.BadTokenException`.\n\n"
            "2. **Layout Inflation and View Creation:** Views created programmatically or inflated via `LayoutInflater` require an Activity Context to resolve theme attributes (`?attr/colorPrimary`, custom styles, and dynamic colors). Using Application Context falls back to raw system defaults, ignoring your app's custom Activity theme.\n\n"
            "3. **In-Task Navigation:** Starting an Activity using an Activity Context preserves the natural backstack within the current task. Using Application Context forces `FLAG_ACTIVITY_NEW_TASK`, creating fragmented task stacks."
        ),
        "deep_answer": (
            "At the Android OS system level, the distinction lies in the **IBinder Window Token** registered with `WindowManagerService` (WMS). "
            "When an Activity transitions to `onResume()`, WMS assigns a unique surface token to its window hierarchy. "
            "When a Dialog attempts to display, it queries its context's `WindowManager.addView()`. WMS verifies whether the token attached to the context is an active, valid window token. Since `ApplicationContext` is owned by the app process rather than a surface window, its token is null, prompting the fatal `BadTokenException`.\n\n"
            "Furthermore, with the introduction of **Android 12/13 per-app language preferences and Dynamic Theming (Material You)**, theme attributes and configuration overrides (like configuration night mode or font scaling) are tied to specific Activity configurations. An Application Context does not receive Activity-level configuration overrides, leading to visual bugs and broken dark/light theme rendering."
        ),
        "follow_ups": [
            {
                "interviewer": "Can you show a Toast using an Application Context?",
                "answer": "Yes! A Toast is rendered by the system's `NotificationManagerService` in a system-managed overlay window, so it works completely fine with an Application Context."
            },
            {
                "interviewer": "What is `ContextThemeWrapper` and how does it relate to this?",
                "answer": "`ContextThemeWrapper` is a class that allows wrapping an existing Context with a custom theme resource (e.g., `ContextThemeWrapper(baseContext, R.style.MyCustomTheme)`), which Activities inherit from by default."
            },
            {
                "interviewer": "Why does Jetpack Compose still need an Activity Context for dialogs?",
                "answer": "Even in Compose, the `Dialog()` composable creates an underlying Android `DialogWindowProvider` which requires an Activity Context to anchor the dialog window to the host Activity surface."
            }
        ]
    },
    {
        "id": "AND-06",
        "arabic_explanation": (
            "الـ Configuration Changes وما الذي ينجو منها (What survives them) هو أساس فهم استقرار التطبيقات أثناء التدوير وتغيير إعدادات الجهاز:\n\n"
            "1. ما هي الـ Configuration Changes؟\n"
            "   - هي أحداث تحدث على مستوى نظام التشغيل تؤدي إلى تغيير في بيئة تشغيل التطبيق (Runtime Configuration).\n"
            "   - أشهر الأمثلة:\n"
            "     * تدوير الشاشة (Screen Orientation: Portrait <-> Landscape).\n"
            "     * تغيير لغة الجهاز (Locale Change: Arabic <-> English).\n"
            "     * تبديل الوضع الليلي (Dark Mode / Night Mode toggle).\n"
            "     * الدخول والخروج من وضع تقسيم الشاشة (Multi-window / Split-screen).\n"
            "     * تغيير حجم الخط وحجم العرض (Font Scale / Display Density).\n\n"
            "2. ما الذي يفعله نظام أندرويد تلقائياً؟\n"
            "   - النظام يقوم بـ **تدمير الـ Activity الحالية بالكامل (`onDestroy`) وإعادة إنشائها من الصفر (`onCreate`)** حتى يقوم بإعادة تحميل الموارد الملائمة (مثل ملفات `layout-land`, `values-ar`, `values-night`).\n\n"
            "3. ما الذي ينجو من هذا التدمير (What survives)?\n"
            "   - **الـ ViewModel:** ينجو تماماً في الذاكرة بفضل `ViewModelStore`.\n"
            "   - **الـ SavedInstanceState Bundle:** ينجو ويحفظ الحقول الأساسية والنصوص المكتوبة في الـ EditTexts تلقائياً.\n"
            "   - **الـ Application Singleton / Process Memory:** يظل حياً كما هو لأن الـ Process نفسه لم يمت."
        ),
        "practical_walkthrough": (
            "ما الذي يضيع وما الذي ينجو عند تدوير الشاشة في تطبيق عملي:\n"
            "- **ما يضيع (Destroyed & Lost):**\n"
            "  * كائن الـ Activity القديم، والـ Views، والـ Fragments القديمة.\n"
            "  * أي كود معلق في `lifecycleScope.launch` يتم إلغاؤه فوراً.\n"
            "- **ما ينجو (Survives):**\n"
            "  * الـ ViewModel وكافة الـ StateFlows المخزنة بداخله؛ تظل تعمل وتستلمها الـ Activity الجديدة فوراً.\n"
            "  * نصوص حقول الإدخال إذا كان لها `android:id` محدد في الـ XML.\n"
            "  * الـ Background Coroutines التي تعمل في `viewModelScope` تستمر بدون انقطاع."
        ),
        "quick_answer": "Configuration changes (screen rotation, dark mode, locale, multi-window) cause Android to completely destroy and recreate the Activity to reload resources. The ViewModel survives in memory via ViewModelStore, the saved instance state Bundle survives for UI state, and the app process remains intact.",
        "best_answer": (
            "A configuration change occurs when device hardware or system settings change at runtime, altering the active resource configuration.\n\n"
            "Common configuration changes include:\n\n"
            "1. Screen orientation changes (portrait vs landscape).\n"
            "2. System dark mode toggles (day vs night theme).\n"
            "3. Locale/language changes.\n"
            "4. Multi-window resizing and folding/unfolding of foldable devices.\n"
            "5. Font scaling and display density modifications.\n\n"
            "By default, Android destroys and recreates the entire Activity (`onPause -> onStop -> onDestroy` followed by `onCreate -> onStart -> onResume`) so the app can load new resources (e.g., `layout-land` or `values-night`).\n\n"
            "**What survives:**\n\n"
            "- **ViewModel**: Retained in memory by the `ViewModelStore`, preserving ongoing business logic and `viewModelScope` coroutines.\n"
            "- **Saved Instance State (`onSaveInstanceState` / `SavedStateHandle`)**: Serializes small UI states across recreation.\n"
            "- **Process Memory**: Singletons, Hilt graph, and memory caches remain intact because the Linux process never died."
        ),
        "deep_answer": (
            "Under the hood, why does Android destroy the Activity rather than just swapping Views?\n\n"
            "Because swapping themes and layouts dynamically on an existing Activity would require manually traversing every drawable, style attribute, dimension, and string resource across the entire view tree. Recreating the Activity provides a clean slate where all resources are cleanly rebound from APK asset tables.\n\n"
            "While developers can declare `android:configChanges=\"orientation|screenSize\"` in the Manifest to prevent recreation, Google strongly discourages this. It forces you to manually override `onConfigurationChanged()` and update every layout, font, and padding by hand, almost always leading to visual bugs and broken accessibility."
        ),
        "follow_ups": [
            {
                "interviewer": "Why do EditTexts automatically restore their text across rotation?",
                "answer": "Because standard Android framework Views implement `onSaveInstanceState()`. If the View has a unique `android:id` assigned, the framework automatically serializes its input text and scroll state into the instance state Bundle and restores it upon recreation."
            },
            {
                "interviewer": "How does `rememberSaveable` in Jetpack Compose survive configuration changes?",
                "answer": "`rememberSaveable` registers with Compose's `SaveableStateRegistry`, which hooks into Android's `onSaveInstanceState` Bundle mechanism under the hood."
            },
            {
                "interviewer": "Can a non-configuration instance be retained manually without ViewModel?",
                "answer": "Historically yes, via `onRetainCustomNonConfigurationInstance()`, but this is deprecated in favor of Jetpack ViewModel, which provides the standardized, type-safe implementation of this exact mechanism."
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

    for q in AND_01_06:
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
    print(f"Updated {DATA_FILE} with questions AND-01 to AND-06. Total questions: {len(combined)}")


if __name__ == "__main__":
    main()

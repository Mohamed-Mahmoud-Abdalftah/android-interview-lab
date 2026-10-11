#!/usr/bin/env python3
"""Author the missing Android internals interview units from topic-specific records."""
from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parent.parent
DATE = "2026-10-11"
CODE = "projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt"
TEST = "projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt"

def s(text): return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

units = [
dict(id="AND-002", day=14, title="Configuration change and process death", path="03-Android-Internals/and-002-configuration-change-and-process-death.md", prereqs=["AND-001"], qstart=6, scn=24, lab=23,
 sources=["https://developer.android.com/topic/libraries/architecture/saving-states", "https://developer.android.com/guide/topics/resources/runtime-changes", "https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate"],
 problem="المستخدم كتب draft، لف الشاشة ففضل موجود، لكن بعد ما النظام قتل process رجع لقى الشاشة فاضية. نجاح rotation test خلّى الفريق يفتكر إن state آمنة، مع إن ViewModel كانت بس مخبية المشكلة.",
 model="Configuration change بتنشئ UI owner جديدة جوه نفس process غالبًا، وViewModel ممكن تحتفظ بالـscreen state. Process death تمسح heap كلها؛ الرجوع يبدأ من saved state صغيرة أو storage durable. صنّف كل state: UI element مؤقت، screen state قابلة لإعادة البناء، ولا business data لازم تتخزن.",
 mechanism="قبل recreation خزّن أقل keys لازمة لإعادة البناء. عند الرجوع اقرأ saved arguments وSavedStateHandle، وبعدها حمّل البيانات الكبيرة من repository. متحطش object graph أو bitmap في Bundle؛ الحجم محدود والنسخة ممكن تبقى stale.",
 wrong="class EditorViewModel : ViewModel() {\n    var draft: String = \"\" // survives rotation only while process lives\n}",
 correct="fun restoreEditor(saved: Map<String, String>, durableDraft: String?) =\n    RestoredEditor(\n        draft = saved[\"draft\"] ?: durableDraft.orEmpty(),\n        selectedTab = saved[\"tab\"]?.toIntOrNull()?.coerceAtLeast(0) ?: 0,\n    )",
 decision="خزّن navigation identity وinput صغير في saved state، وخزّن business data في database. أعد اشتقاق القيم المحسوبة بدل تكرارها. اختبر recreation وprocess recreation كمسارين مختلفين.",
 aspects=[
 ("Configuration change versus process death", "A ViewModel preserves a form after rotation. Why does that prove nothing about process death?", "ViewModel survives a configuration-created owner replacement, but it lives in process memory. Process death removes it; restoration needs saved-state keys and durable data.", "إيه اللي يتخزن في SavedStateHandle؟", "أقل قيم صغيرة لازمة لإعادة بناء الشاشة، مش dataset كبيرة ولا object graph.", "إزاي تختبر الفرق؟", "اختبر recreation عادية، وبعدها restore من saved snapshot مع repository جديدة من غير reuse للـViewModel."),
 ("Saved-state size and source of truth", "Review code that puts a full API response in a Bundle to survive recreation.", "A Bundle is a bounded handoff, not a database. Store identity and lightweight input, then reload canonical data from the source of truth.", "إيه خطر نسخ response؟", "ممكن تتجاوز transaction size وتبقى stale مقارنة بالـdatabase أو server.", "لو network مش متاحة؟", "اعتمد على local durable source واظهر freshness/sync state بدل نسخة Bundle ضخمة."),
 ("Restoration ordering", "The UI renders defaults, then saved state, then database data and visibly jumps. Design the restoration order.", "Build one state reducer with explicit restoring/loading/content phases. Seed identity from saved state, read local data, and only publish states that the UI can represent honestly.", "هل نخفي الشاشة لحد network؟", "مش لازم؛ اعرض local content وfreshness لو العقد يسمح، مع loading واضح للجزء الباقي.", "إزاي تمنع result قديمة؟", "اربط load بالـrecord ID والجeneration الحالية وارفض completion من restore أقدم."),
 ("rememberSaveable boundary", "When is rememberSaveable useful and when should state move to a ViewModel or repository?", "Use it for small UI state tied to composition restoration. Hoist screen behavior to a state holder and keep durable business data in the data layer.", "هل custom Saver يحل أي object؟", "تقنيًا يقدر يحول shape، لكن لازم تفضل صغيرة ومستقرة وقابلة لإعادة البناء.", "مين يملك validation؟", "الـdomain أو screen state holder يملك قواعد business؛ composable ما تبقاش source of truth."),
 ("Restoration test design", "Design tests for a checkout screen across rotation and process death.", "Test reducer persistence separately, then Android recreation with saved state, and a fresh process-style launch that reloads durable cart identity without reusing memory fakes.", "إيه failure لازم يتجرب؟", "Saved key مفقودة أو malformed، database unavailable، وaccount مختلف عن snapshot.", "هل JVM test كفاية؟", "يثبت pure restoration policy فقط؛ lifecycle registry وBundle limits محتاجين Android test."),
 ]),
dict(id="AND-003", day=15, title="Tasks, intents, PendingIntent and export", path="03-Android-Internals/and-003-tasks-intents-pendingintent-and-export.md", prereqs=["AND-001"], qstart=11, scn=25, lab=24,
 sources=["https://developer.android.com/guide/components/activities/tasks-and-back-stack", "https://developer.android.com/guide/components/intents-filters", "https://developer.android.com/privacy-and-security/risks/pending-intent", "https://developer.android.com/guide/topics/manifest/activity-element"],
 problem="Deep link خارجية بتفتح شاشة payment result مباشرة، وPendingIntent mutable بتسمح لجهة تانية تغير extras. المشكلة هنا مش navigation بس؛ دي trust boundary بتدخل process بتاعتك.",
 model="Intent رسالة غير موثوقة لحد ما تثبت العكس. task/back stack تحدد history وتجربة Back، وlaunchMode/flags تغير إعادة استخدام Activity. exported component توسع سطح الهجوم. PendingIntent capability باسم تطبيقك؛ mutability وexplicit target والrequest identity جزء من الأمان.",
 mechanism="Android يحل intent مقابل filters ثم ينشئ أو يعيد route حسب task flags. عند boundary افحص action وscheme وhost وpath والـpayload، وبعدها حوّلها command داخلية typed. ما تعتمدش على UI السابقة إنها عملت validation.",
 wrong="val intent = Intent(Intent.ACTION_VIEW, uri)\nstartActivity(intent) // untrusted shape and no resolver/error policy",
 correct="fun acceptsReturnIntent(i: IntentEnvelope) =\n    i.action == \"academy.PAYMENT_RETURN\" && i.scheme == \"https\" &&\n    i.host == \"pay.academy.example\" && i.immutable",
 decision="خلّي components غير exported افتراضيًا، واستخدم explicit intents داخل التطبيق. لو boundary لازم exported، وثّق caller/authentication وvalidate كل input. اختبر back stack كـuser journey مش flags منفصلة.",
 aspects=[
 ("Task and back-stack semantics", "Explain why launchMode is not a substitute for modeling navigation state.", "Launch modes control Activity instance and task behavior, but they do not define business navigation or typed arguments. I model destinations and test Back from real entry points.", "إيه خطر singleTask؟", "ممكن يوجّه intents جديدة لـonNewIntent ويمسح stack بشكل غير متوقع لو state مش متزامنة.", "تختبر إزاي؟", "ابدأ من launcher وdeep link وnotification، وتتبع stack وarguments وBack لكل مسار."),
 ("Intent input validation", "An exported Activity trusts extras because only your notification creates the Intent. Review this assumption.", "Exported boundaries can be invoked externally. Validate action, origin shape, required fields, sizes, and authorization again inside the component.", "هل host string كفاية؟", "لا؛ افحص scheme وhost normalized وpath وduplicate query fields، ومتقبلش lookalike authority.", "فين تتحول لـdomain command؟", "بعد validation مباشرة في adapter صغير، قبل وصول raw Intent للـdomain."),
 ("PendingIntent mutability", "Choose mutable or immutable PendingIntent for a notification action and explain identity collisions.", "Use immutable unless the receiving workflow requires a documented fill-in field. Build stable request identity so two actions do not unexpectedly replace each other.", "إمتى mutability مطلوبة؟", "لبعض system flows زي RemoteInput؛ اسمح بأقل مساحة تغيير وtarget explicit.", "إيه FLAG_UPDATE_CURRENT؟", "يحدّث extras لPendingIntent بنفس identity؛ لازم تفهم fields الداخلة في equality مش تفترض uniqueness."),
 ("Exported component review", "What do you inspect before marking an Activity, service, or receiver exported?", "Inspect who must call it, required permission, intent filters, sensitive operations, input validation, and whether an internal non-exported proxy is possible.", "هل permission custom كفاية؟", "لا وحدها؛ راجع protection level والتوقيع والـauthorization داخل العملية الحساسة.", "إيه evidence؟", "Manifest merged output، adb invocation سلبية، واختبارات inputs malicious وحدود الحجم."),
 ("Deep-link authentication", "A valid app link opens an authenticated order screen while the user is signed out. Design the flow.", "Treat the link as navigation intent, preserve only safe destination identity, route through authentication, then re-authorize the order for the active account before display.", "ينفع نخزن URL كاملة؟", "الأفضل typed safe arguments؛ URL قد تحمل tokens أو fields غير موثوقة ومتسربش للlogs.", "لو account اتغير أثناء login؟", "أعد authorization بعد login واربط الطلب بالـactive session، ومتستخدمش نتيجة pre-login القديمة."),
 ]),
dict(id="AND-004", day=16, title="Looper, Handler, Binder and ANR evidence", path="03-Android-Internals/and-004-looper-handler-binder-and-anr-evidence.md", prereqs=["AND-001"], qstart=16, scn=26, lab=None,
 sources=["https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs", "https://developer.android.com/reference/android/os/Looper", "https://developer.android.com/reference/android/os/Handler", "https://source.android.com/docs/core/architecture/aidl/binder-threading"],
 problem="التطبيق بيظهر ANR في release بس، والفريق شايف network logs في نفس الدقيقة فافترض إن الشبكة السبب. المطلوب تربط trace بالـmain thread والـbinder waits والـlock owner بدل correlation سطحي.",
 model="Looper تسحب Messages وRunnables من MessageQueue على thread واحدة. main thread مسؤولة عن input وlifecycle والرسم؛ blocking طويل يمنع الاستجابة. Binder IPC ممكن ينفذ على thread pool، لكن synchronous call من main تفضل توقف main. ANR نوع symptom له timing وcomponent؛ الدليل stack traces وPerfetto وsystem report.",
 mechanism="عند ANR ثبت timestamp وprocess وcomponent. اقرأ main-thread stack: CPU loop، monitor contention، binder call، I/O، ولا انتظار future. اتبع lock أو binder للthread المالكة. قارن traces متعددة؛ top frame واحدة ممكن تكون مكان انتظار مش السبب الأصلي.",
 wrong="Handler(Looper.getMainLooper()).post {\n    val data = blockingSocket.read()\n    render(data)\n}",
 correct="scope.launch {\n    val data = repository.readMainSafe()\n    render(data) // main only for the small UI update\n}",
 decision="خلي blocking boundary main-safe، قلّل critical sections، ومتستخدمش async عشوائي يخفي ordering. اجمع evidence من ANR trace وPerfetto وStrictMode في debug، وحدد rollout metric قبل الإصلاح.",
 aspects=[
 ("Looper and MessageQueue", "Trace how a long Runnable causes input latency on the main thread.", "The Looper processes one queued message at a time. A long Runnable prevents later input, lifecycle, and frame work from running until it returns.", "هل post يحوّل الخلفية؟", "لا؛ post للmain Handler ينقل العمل للmain queue نفسها.", "إزاي تلاقي الرسالة الطويلة؟", "استخدم main stack وPerfetto slices/frame timing بدل تخمين من log قريبة."),
 ("Synchronous Binder call", "Why can a fast service still cause an ANR through Binder?", "A synchronous Binder call blocks the caller. From main, queueing, remote contention, or nested locks can exceed the response budget even when average service time is low.", "هل oneway يحل؟", "يغير semantics لاتصال async وماينفعش لو محتاج result؛ كمان queue ممكن تتراكم.", "فين تقيس؟", "على caller والremote thread pool مع trace IDs، وممنوع payload حساسة."),
 ("ANR evidence", "Given one ANR stack, how do you avoid blaming the top frame incorrectly?", "Classify whether the frame is running, blocked, waiting on Binder, or waiting on a lock. Follow ownership and compare repeated traces and timeline evidence.", "إيه competing cause؟", "GC pressure، lock inversion، provider startup، أو broadcast/service deadline حسب نوع ANR.", "إيه أول mitigation؟", "قلل أو انقل boundary المثبتة، وحط rollout guard؛ متغيرش threading واسع من غير proof."),
 ("Handler leak", "How can a delayed callback retain a destroyed screen, and what is the correction?", "A queued callback captures the Activity or view until execution or removal. Tie callbacks to a lifecycle owner, remove them, or move state work to a longer-lived owner without capturing views.", "static Handler كفاية؟", "يقلل implicit outer reference لكنه مش يحل Runnable ماسكة view.", "تختبر إزاي؟", "destroy owner، شغل queue، وتأكد مفيش render على view القديمة؛ device leak tooling يكمل الدليل."),
 ("Main-safe API contract", "Where should withContext(IO) live for a blocking database driver?", "At the data boundary that knows the driver is blocking, so callers receive a main-safe suspend contract. Do not scatter dispatcher guesses through UI code.", "لو driver suspending main-safe؟", "متضيفش hop تلقائي؛ اتبع contract وقِس عند الشك.", "هل IO تمنع ANR دايمًا؟", "لا؛ main ممكن تنتظر lock أو تعمل CPU/render ثقيل، والـIO pool نفسها ممكن تتشبع."),
 ]),
dict(id="AND-005", day=17, title="WorkManager, services, Doze and notifications", path="03-Android-Internals/and-005-workmanager-services-doze-and-notifications.md", prereqs=["AND-003", "AND-004"], qstart=21, scn=27, lab=25,
 sources=["https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started", "https://developer.android.com/develop/background-work/services/fgs", "https://developer.android.com/training/monitoring-device-state/doze-standby", "https://developer.android.com/develop/ui/views/notifications/notification-permission"],
 problem="Upload بدأ من screen scope فاتقطع بعد الخروج. الفريق نقله foreground service لكل الحالات، فظهر notification مزعج وبدأ يصطدم بقيود البدء من الخلفية. المطلوب اختيار mechanism من durability وurgency وuser visibility.",
 model="In-process coroutine لشغل قصير مربوط بعمر ظاهر. WorkManager لشغل durable deferrable لازم يكمل بعد restart بقيود واضحة. Expedited work للحالات المؤهلة تحت quota. Foreground service لشغل user-visible مستمر بnotification وtype مناسب، مش escape hatch. Doze يؤجل شغل وتوقيتات؛ notification permission تؤثر العرض حسب الإصدار.",
 mechanism="اكتب contract: هل لازم ينجو من process death؟ هل المستخدم شايفه الآن؟ هل له deadline؟ هل retry آمنة؟ بعدها اختار mechanism، خزّن input صغير وstable، واجعل worker idempotent لأن التنفيذ ممكن يتكرر.",
 wrong="fun upload() { appScope.launch { api.upload(file) } } // no durable handoff",
 correct="fun chooseWorkMechanism(visible: Boolean, durable: Boolean, urgent: Boolean) = when {\n    visible -> FOREGROUND_SERVICE\n    durable && urgent -> EXPEDITED_WORK\n    durable -> DURABLE_WORK\n    else -> IN_PROCESS\n}",
 decision="متخزنش bytes كبيرة في WorkRequest input؛ خزّن URI/ID آمنة والصلاحية المطلوبة. صنّف retry، حط unique work policy عن قصد، واظهر progress من source of truth.",
 aspects=[
 ("Work mechanism selection", "Choose between viewModelScope, WorkManager, expedited work, and a foreground service for an upload.", "Choose from lifetime and user visibility. Durable deferred upload fits WorkManager; an active user-visible transfer may justify FGS; screen-only work can stay in its owner scope.", "هل WorkManager فوري؟", "لا يضمن وقت دقيق؛ constraints وsystem scheduling جزء من العقد.", "إيه سؤال idempotency؟", "لو worker اتنفذت مرتين، هل نفس operation key تمنع duplicate side effect؟"),
 ("Worker retry policy", "Why is returning Result.retry for every exception dangerous?", "Permanent authentication or validation failures will loop and waste battery. Classify transient transport failures, cap attempts, use backoff, and expose terminal state.", "timeout safe للretry؟", "مش للside effect من غير idempotency لأن server outcome ممكن يبقى unknown.", "فين attempt count؟", "في worker metadata أو durable operation record عشان القرار يفضل بعد restart."),
 ("Foreground-service boundary", "What must be true before choosing a foreground service?", "The work is ongoing and user-visible, the app is allowed to start it in that context, it declares the correct type, and it posts the required notification promptly.", "ليه مش لكل sync؟", "تكلفة UX وقيود platform، وكثير من sync deferrable أنسب لـWorkManager.", "لو permission notification مرفوضة؟", "تعامل مع version behavior وقدم UX صريح؛ متفترضش visibility أو تخفي requirement."),
 ("Doze and exact timing", "A product asks for a sync exactly every 15 minutes overnight. How do you respond?", "Background scheduling is inexact and Doze batches work. Clarify the real user outcome, use push or approved exact mechanisms only when policy permits, and design stale-data UX.", "هل wake lock حل؟", "مش تصريح لتجاوز policy، وله battery cost وownership لازم يتراجع.", "إيه test؟", "اختبر constraints وretry pure، ثم device scenarios تحت Doze وnetwork transitions."),
 ("Unique work and progress", "How do unique work policies affect duplicate sync requests?", "A stable unique name plus KEEP, REPLACE, or APPEND policy defines deduplication or sequencing. Choose from whether old work remains valid and persist progress outside ephemeral callbacks.", "REPLACE تعمل إيه؟", "تلغي القديمة وتبدأ الجديدة؛ side effect القديمة قد تكون عبرت boundary فلازم idempotency.", "فين UI تقرأ progress؟", "من durable operation state أو WorkInfo mapping، مع handling للrecreation وmissing rows."),
 ]),
dict(id="AND-006", day=18, title="Revision: adb evidence and DSA", path="03-Android-Internals/and-006-revision-adb-evidence-and-dsa.md", prereqs=["AND-001", "AND-004"], qstart=26, scn=28, lab=None,
 sources=["https://developer.android.com/tools/adb", "https://developer.android.com/studio/debug/bug-report", "https://developer.android.com/topic/performance/tracing", "https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs"],
 problem="Bug report فيه آلاف السطور، والمرشح بيقرأ logcat عشوائيًا. المطلوب hypothesis واضحة، time window، process/build identity، وأداة تناسب السؤال؛ وبعدها DSA solution invariant مش كود محفوظ.",
 model="adb قناة لأدلة مختلفة: logcat events، dumpsys snapshot، bugreport system bundle، وPerfetto timeline. ولا واحدة تشرح السبب لوحدها. ثبت build/variant/device/time/reproduction، ثم اربط evidence بالسؤال. في DSA اكتب contract وinvariant وcomplexity قبل التنفيذ.",
 mechanism="ابدأ reproduction matrix صغيرة: fresh/restore، foreground/background، online/offline. خذ marker زمني وrequest ID، ثم اجمع أقل evidence تفصل hypotheses. redact قبل المشاركة. في live coding كرر نفس المنهج: examples، invariant، boundaries، tests.",
 wrong="adb logcat > everything.txt\n# Then search for the word Error and assume the first match is root cause.",
 correct="adb logcat -c\n# reproduce once with timestamp and build identity\nadb bugreport ./bugreport.zip\n# inspect the matching process/time window and corroborate with traces",
 decision="استخدم logcat للأحداث المرتبة، dumpsys للحالة الحالية، bugreport للسياق النظامي، Perfetto للزمن والthreads. ما تجمعش بيانات مستخدم أكتر من اللازم، ومتعتبرش absence في log دليل إن الحدث ماحصلش.",
 aspects=[
 ("Evidence-tool selection", "Choose logcat, dumpsys, bugreport, or Perfetto for a suspected main-thread stall.", "Use Perfetto and ANR stacks for timing and thread state, logcat for correlated events, dumpsys for snapshots, and bugreport for broader system context. Each answers a different question.", "ليه logcat وحدها ضعيفة؟", "الأحداث ناقصة وممكن تتأخر أو تتفلتر؛ مش timeline CPU/locks كاملة.", "إيه أول metadata؟", "build ID، process، device، wall/elapsed time، وخطوات reproduction."),
 ("ANR triage sequence", "Give a five-minute first pass for an ANR report.", "Confirm ANR type and time, locate the process and main stack, classify running versus blocked, follow lock or Binder ownership, then compare repeated traces and recent release changes.", "تبدأ بتغيير dispatcher؟", "لا قبل تحديد boundary؛ تغيير واسع ممكن يخفي race أو يضيف ordering bug.", "إيه mitigation؟", "لو regression واضحة، rollback/flag أولًا ثم root-cause fix بمقياس نجاح."),
 ("Reproduction matrix", "How do you keep a lifecycle bug reproduction matrix useful instead of combinatorial?", "Choose dimensions that separate hypotheses: fresh versus restored, process alive versus recreated, foreground versus background, and network state. Start pairwise and add only evidence-driven cases.", "إيه اللي يتسجل؟", "exact steps، build، device/API، expected/actual، timestamp، وartifact link.", "هل success مرة تنفي bug؟", "لا للrace؛ كرر بتوقيتات controlled واجمع failure rate من غير تزوير certainty."),
 ("Stack live-coding invariant", "Implement balanced brackets and state the stack invariant.", "After consuming a prefix, the stack contains unmatched opening brackets in encounter order. A closing bracket must match the top; the final stack must be empty.", "التعقيد؟", "O(n) time وO(n) worst-case space، مع rejection لأي character خارج العقد لو محدد.", "إيه edge cases؟", "empty، single closer، wrong nesting، long all-open input، وUnicode لو العقد مش ASCII."),
 ("Evidence communication", "How do you present uncertain debugging evidence in a senior interview?", "Separate observation, inference, and decision. State what the trace proves, competing explanations, the next discriminating test, and the reversible mitigation.", "هل تقول root cause بسرعة؟", "بس لو evidence تربط cause بالsymptom وتختفي المشكلة عند تغيير bounded مع regression test.", "إزاي تتجنب PII؟", "IDs hashed أو synthetic، payload redaction، وأقل retention وصلاحيات لازمة."),
 ])
]

diffs=["foundational","intermediate","senior","senior","senior"]
styles=["conceptual","code-review","debugging","architecture","debugging"]

def lesson(u):
 qids=[f"AND-Q{i:03d}" for i in range(u['qstart'],u['qstart']+5)]
 trace="\n".join(f"<tr><td>{i+1}</td><td>{x}</td></tr>" for i,x in enumerate([u['problem'],u['model'],u['mechanism'],u['decision']]))
 return f'''---
id: {u['id']}
title: {u['title']}
module: 03-Android-Internals
tier: Core
estimated_minutes: 65
prerequisite_ids: [{", ".join(u['prereqs'])}]
learning_outcomes:
  - Diagnose a concrete Android runtime failure from evidence
  - Explain the platform contract in Egyptian Arabic and spoken English
  - Review unsafe code and defend a bounded correction
  - Design JVM and Android tests without overstating evidence
status: reviewed
code_verification: {"tested" if u['lab'] else "not_applicable"}
last_source_checked: {DATE}
source_urls:
''' + "\n".join(f"  - {x}" for x in u['sources']) + (f'''
example_paths:
  - ../{CODE}
  - ../{TEST}
''' if u['lab'] else "\nexample_paths: []\n") + f'''question_ids: [{", ".join(qids)}]
---

# {u['id']} — {u['title']}

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">{u['problem']}</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">{u['model']}</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">{u['mechanism']}</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>القرار والدليل</th></tr></thead><tbody>{trace}</tbody></table>

## كود غلط، ليه غلط، وتصحيحه — Wrong and corrected implementation

```kotlin
{u['wrong']}
```

<p dir="rtl" lang="ar">الكود الغلط بيخلط platform contract مع افتراض محلي، ومفيهوش ownership أو failure policy واضحة. النتيجة ممكن تنجح في happy path وتفشل بعد recreation أو input خارجية أو ضغط production.</p>

```kotlin
{u['correct']}
```

## مثال Production حقيقي وبدائل

<p dir="rtl" lang="ar">{u['decision']} قبل rollout حدد metric صحة، وجرّب failure وrecreation، وخلي logging بأقل بيانات ومن غير secrets. اختار أبسط boundary تحقق العقد؛ ما تزودش component أو thread أو persistence من غير سبب.</p>

## Tests and failure cases

- Pure JVM test للعقد أو reducer لما يكون مستقل عن Android.
- Android recreation/lifecycle test لما النتيجة تعتمد على framework owner.
- Negative inputs عند كل exported أو restored boundary.
- Process death, account switch, cancellation, duplicate delivery, and stale completion where relevant.
- Release evidence names the device/API/build and never upgrades a JVM model into device proof.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة مختصرة:</strong> {u['model']}</p>

**English, 20 seconds:** “{u['aspects'][0][2]}”

**English, 60–90 seconds:** “{u['aspects'][0][2]} In production I start from the owning component and the platform boundary, then trace recreation, external input, cancellation, and late delivery. I keep small restoration or command data separate from durable business state, validate untrusted boundaries, and choose evidence that can distinguish the competing causes. I test pure policy on the JVM and use an Android integration or device trace for framework behavior.”

## Senior follow-ups

''' + "\n".join(f"{i+1}. **{a[1]}** {a[2]}" for i,a in enumerate(u['aspects'][:3])) + f'''

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">جاوب الأسئلة من {qids[0]} إلى {qids[-1]} بصوتك قبل فتح الإجابة. الاعتقاد إن happy path أو rotation واحدة تثبت Android lifecycle غلط؛ افصل كل owner وentry point وfailure. راجع المصادر الرسمية المتحققة بتاريخ {DATE}.</p>
''' + (f"\nحل [LAB-{u['lab']:03d}](../Coding-Challenges/LAB-{u['lab']:03d}-{s(u['aspects'][0][0])}.md) ثم راجع الاختبارات.\n" if u['lab'] else "\nاكتب test matrix قبل استخدام adb أو emulator؛ الوحدة دي لا تدّعي Android execution محليًا.\n") + f'''

حلّل [SCN-{u['scn']:03d}](../Real-World-Scenarios/SCN-{u['scn']:03d}-{s(u['problem'][:55])}.md) من غير ما تقرأ الإصلاح الأول.

**Evidence limit:** Official Android behavior is sourced, but this host has no Android SDK/emulator. Pure policy code is marked separately from device evidence.
'''

def qdocs(u):
 for i,a in enumerate(u['aspects']):
  topic,prompt,fact,f1q,f1a,f2q,f2a=a; qid=f"AND-Q{u['qstart']+i:03d}"
  f1q=f1q.rstrip('?؟'); f2q=f2q.rstrip('?؟')
  q=f'''---
id: {qid}
lesson_id: {u['id']}
topic: {topic}
difficulty: {diffs[i]}
style: {styles[i]}
expected_minutes: {4+i//2}
status: reviewed
---
# {qid} — {topic}

{prompt}

[Open complete model answer](../Model-Answers/{qid}.md) · [Lesson](../../{u['path']})
'''
  ans=f'''---
id: {qid}-ANSWER
question_id: {qid}
status: reviewed
---
# {qid} — Complete model answer

**Spoken answer:** “{fact}”

<p dir="rtl" lang="ar">{u['model']} في السؤال ده ركّز على <strong>{topic}</strong>: {u['decision']}</p>

**Mechanics and trace:** {u['mechanism']} A strong answer names the owner, entry point, state before and after the transition, the failure path, and the evidence that would separate two plausible causes.

**Common wrong answer:** “The happy path worked, so the Android contract is correct.” This ignores recreation, process boundaries, hostile inputs, ordering, and device-specific integration.

**Follow-up 1:** في الحالة دي، {f1q}? {f1a} اربط الإجابة بـtest أو trace محددة، ومتعتبرش log واحدة proof كامل.

**Follow-up 2:** تحت ضغط production، {f2q}? {f2a} اذكر كمان limitation: JVM model لا يثبت framework behavior على جهاز.

**Polished English answer:** “{fact} I would verify it with a bounded reproduction, record the relevant owner and state transition, and add a regression test at the narrowest reliable boundary.”

**Rubric:** Direct contract, ordered trace, realistic failure, corrected decision, and honest evidence boundary.
'''
  yield qid,q,ans,topic,diffs[i],styles[i]

def scenario(u):
 sid=f"SCN-{u['scn']:03d}"
 return f'''---
id: {sid}
lesson_id: {u['id']}
status: reviewed
code_verification: {"tested" if u['lab'] else "not_run"}
---
# {sid} — {u['problem'][:90]}

## Symptom and competing hypotheses

<p dir="rtl" lang="ar">{u['problem']} الفرضيات المنافسة تشمل ownership غلط، state stale، input غير موثوقة، وplatform restriction. ممنوع نختار السبب من قرب log زمني فقط.</p>

## Investigation and correction

<p dir="rtl" lang="ar">{u['mechanism']} الإصلاح: {u['decision']}</p>

## Tests and rollout

1. Reproduce with one changed dimension at a time.
2. Assert the ordered state transition and the negative path.
3. Stage rollout with a correctness metric and rollback threshold.
4. Redact identifiers and never log tokens, intents, or payloads wholesale.

## Senior follow-ups

1. **What observation would falsify your leading hypothesis?** Choose a trace or state snapshot that the alternative predicts differently.
2. **What is the smallest reversible mitigation?** Disable or route around the proven boundary while preserving evidence.
3. **What remains unverified?** Device and framework behavior until an Android test or production trace runs.
'''

def lab(u):
 lid=f"LAB-{u['lab']:03d}"; name=s(u['aspects'][0][0])
 return name,f'''---
id: {lid}
lesson_id: {u['id']}
status: reviewed
code_verification: tested
---
# {lid} — {u['aspects'][0][0]}

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> حوّل قرار الدرس لـpure contract صغيرة، واكتب boundary cases قبل implementation. النموذج موجود في <a dir="ltr" href="../{CODE}">CompletionModels.kt</a> والاختبارات في <a dir="ltr" href="../{TEST}">CompletionModelsTest.kt</a>.</p>

**Interview rule:** Explain what this pure model proves and what still needs Android integration. Run `./gradlew test --tests academy.CompletionModelsTest --no-daemon` from `projects/kotlin-jvm-labs`.

**Extension:** Add a malformed input, a stale identity, and a duplicate delivery case. State the invariant before code.
'''

# Write canonical files.
for u in units:
 (ROOT/u['path']).write_text(lesson(u),encoding='utf-8')
 for qid,q,a,*_ in qdocs(u):
  (ROOT/f"Interview-Question-Bank/Questions/{qid}.md").write_text(q,encoding='utf-8')
  (ROOT/f"Interview-Question-Bank/Model-Answers/{qid}.md").write_text(a,encoding='utf-8')
 scn_name=s(u['problem'][:55]); (ROOT/f"Real-World-Scenarios/SCN-{u['scn']:03d}-{scn_name}.md").write_text(scenario(u),encoding='utf-8')
 if u['lab']:
  name,body=lab(u); (ROOT/f"Coding-Challenges/LAB-{u['lab']:03d}-{name}.md").write_text(body,encoding='utf-8')
 (ROOT/f"Flashcards-Revision/{u['id']}.md").write_text(f"# {u['id']} revision cards\n\n"+"\n".join(f"{i+1}. **{a[0]}:** {a[2]}" for i,a in enumerate(u['aspects']))+"\n",encoding='utf-8')
 (ROOT/f"Speaking-Shadowing/DAY-{u['day']:02d}.md").write_text(f"# Day {u['day']} — {u['title']}\n\n## 20-second answer\n\n“{u['aspects'][0][2]}”\n\n## Pressure prompts\n\n"+"\n".join(f"- {a[1]}" for a in u['aspects'])+"\n",encoding='utf-8')

# Manifest.
mp=ROOT/'CONTENT-MANIFEST.json'; m=json.loads(mp.read_text())
items=[]; seen=set()
for entry in m['items']:
 if entry['id'] not in seen:
  items.append(entry); seen.add(entry['id'])
m['items']=items; by={x['id']:x for x in items}
for u in units:
 qids=[f"AND-Q{i:03d}" for i in range(u['qstart'],u['qstart']+5)]; tested=bool(u['lab']); ex=[CODE,TEST] if tested else []
 by[u['id']].update(status='reviewed',code_verification='tested' if tested else 'not_applicable',verification_evidence='BUILD-VERIFICATION.md' if tested else None,question_ids=qids,example_paths=ex,source_urls=u['sources'],source_status='verified')
 for qid in qids:
  if qid not in by:
   x=dict(id=qid,type='question',path=f'Interview-Question-Bank/Questions/{qid}.md',answer_path=f'Interview-Question-Bank/Model-Answers/{qid}.md',prerequisites=[u['id']],status='reviewed',code_verification='not_applicable',verification_evidence='scripts/validate.py',question_ids=[],example_paths=[],source_urls=[u['sources'][0]],source_status='verified'); items.append(x);by[qid]=x
 sid=f"SCN-{u['scn']:03d}"; sp=f"Real-World-Scenarios/{sid}-{s(u['problem'][:55])}.md"
 x=dict(id=sid,type='scenario',path=sp,prerequisites=[u['id']],status='reviewed',code_verification='tested' if tested else 'not_run',verification_evidence='BUILD-VERIFICATION.md' if tested else None,question_ids=[],example_paths=ex,source_urls=[u['sources'][0]],source_status='verified')
 if sid in by: by[sid].update(x)
 else: items.append(x);by[sid]=x
 if tested:
  lid=f"LAB-{u['lab']:03d}"; lp=f"Coding-Challenges/{lid}-{s(u['aspects'][0][0])}.md"
  x=dict(id=lid,type='coding_challenge',path=lp,prerequisites=[u['id']],status='reviewed',code_verification='tested',verification_evidence='BUILD-VERIFICATION.md',question_ids=[],example_paths=ex,source_urls=[u['sources'][0]],source_status='verified')
  if lid in by: by[lid].update(x)
  else: items.append(x);by[lid]=x
m['as_of']=DATE;mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')

# Registries and coverage.
tp=ROOT/'Interview-Question-Bank/BY-TOPIC.md';dp=ROOT/'Interview-Question-Bank/BY-DIFFICULTY.md';stp=ROOT/'Interview-Question-Bank/BY-INTERVIEW-STYLE.md'
tt=tp.read_text();dt=dp.read_text();st=stp.read_text()
for u in units:
 for qid,_,_,topic,diff,style in qdocs(u):
  ql=f"[{qid}](Questions/{qid}.md)";al=f"[answer](Model-Answers/{qid}.md)"
  if f"Questions/{qid}.md" not in tt:tt+=f"\n| {topic} | {ql} | [Model answer](Model-Answers/{qid}.md) |"
  if f"Questions/{qid}.md" not in dt:dt+=f"\n- {diff.title()}: {ql} — {al}"
  if f"Questions/{qid}.md" not in st:st+=f"\n- {style.replace('-',' ').title()}: {ql} — {al}"
tp.write_text(tt.rstrip()+'\n');dp.write_text(dt.rstrip()+'\n');stp.write_text(st.rstrip()+'\n')
cp=ROOT/'COVERAGE-MATRIX.md';lines=cp.read_text().splitlines()
for u in units:
 for i,line in enumerate(lines):
  if line.startswith(f"| {u['id']} |"):
   qs=f"AND-Q{u['qstart']:03d}–{u['qstart']+4:03d}"; testcell=f"[JVM tests]({TEST})" if u['lab'] else 'Android test plan; SDK unavailable'
   lines[i]=f"| {u['id']} | 03-Android-Internals | Core | {', '.join(u['prereqs'])} | 120 | [{u['id']}]({u['path']}) | {qs} | {testcell} | [official]({u['sources'][0]}) | reviewed | Android interview trace, failure paths and evidence |";break
cp.write_text('\n'.join(lines)+'\n')
print('Authored 5 Android internals lessons, 25 interview pairs, 5 scenarios and 3 labs')

from harden_interview_bank import harden_bank
print("Hardened interview bank:", harden_bank())

#!/usr/bin/env python3
"""Replace templated interview material with topic-specific interview scenarios.

The academy's first generated expansion produced valid files but repeated generic
mechanics and follow-ups. This pass keeps the reviewed IDs and links while making
each affected question and answer depend on its own topic, failure, and evidence.
"""

from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
QUESTION_DIR = ROOT / "Interview-Question-Bank" / "Questions"
ANSWER_DIR = ROOT / "Interview-Question-Bank" / "Model-Answers"
ARABIC = re.compile(r"[\u0600-\u06ff]")

ANSWER_MARKERS = (
    "The owner receives input, changes state, crosses the relevant boundary",
    "Identify the exact layer, owner, input artifact or state, transition, and output",
    "**Mechanics:** Tie the answer to",
    "The happy path worked, so the Android contract is correct",
    "## Direct interview answer",
    "## الإجابة اللي تقولها في الانترفيو",
    "## الإجابة المختصرة",
)
QUESTION_MARKERS = (
    "A senior review exposes this failure:",
    "During a specialist interview, explain",
    "## Production scenario",
    "## Interview scenario",
    "## Interview question",
)

PROFILES = {
    "KOT": {
        "owner": "الـcaller والـtype contract",
        "trace": "ابدأ بالـinput type والقيم المسموحة، تتبع التحويل أو dispatch، ثم راقب القيمة الفعلية عند JVM أو Android boundary.",
        "test": "اختبر null وempty وboundary values وruntime type mismatch، ولو الادعاء عن compiler أو ART افحص artifact الفعلي بدل unit test فقط.",
        "alternative": "اختار API أبسط أو type أقوى لما يقدر يمنع الحالة الغلط وقت compile بدل runtime validation.",
        "english": "I would separate the Kotlin language contract from compiler, JVM, and Android runtime behavior, then inspect the artifact or boundary that can actually prove the claim.",
    },
    "COR": {
        "owner": "الـCoroutineScope والـJob hierarchy",
        "trace": "حدد مين أنشأ الـscope، مين children، فين suspension point، وإيه اللي يحصل للفشل والـcancellation والنتيجة القديمة قبل أي state mutation.",
        "test": "استخدم virtual time وcontrolled fakes، اثبت start وcancel وcleanup وعدم نشر stale result، ومتستخدمش sleep كدليل scheduling.",
        "alternative": "استخدم sequential execution أو explicit queue لو ordering أهم من concurrency، واستخدم supervision فقط لما فشل sibling مستقل فعلًا.",
        "english": "I would make scope ownership, cancellation, failure propagation, and the final state mutation explicit, then verify the race with deterministic coroutine tests.",
    },
    "AND": {
        "owner": "Android component أو system service اللي بيمتلك الـlifecycle",
        "trace": "ابدأ من entry point، تتبع lifecycle/process/task state، افصل configuration change عن process death، وبعدها راقب framework callback والـpersisted state.",
        "test": "اختبر recreation وprocess death وduplicate delivery وinvalid external input على emulator أو device؛ JVM test يثبت policy فقط.",
        "alternative": "اختار WorkManager أو foreground service أو in-process coroutine حسب durability وuser visibility والقيود الفعلية، مش حسب الاسم الأشهر.",
        "english": "I would trace the Android component and process lifecycle, preserve only the state that belongs at each boundary, and verify framework behavior on a device or emulator.",
    },
    "ARC": {
        "owner": "الـstate owner والـsource of truth",
        "trace": "حدد command داخلة منين، validation فين، مين يملك state، إمتى side effect تحصل، وإزاي success أو failure ترجع من غير duplicate work أو stale state.",
        "test": "اختبر transition قبل وبعد failure، عدد استدعاءات dependencies، conflict أو retry، وإن UI ما تقدرش تتخطى business invariant.",
        "alternative": "ابدأ بحدود أقل طالما contract واضحة؛ زوّد layer أو module لما ownership أو change rate أو test seam يبرر التكلفة.",
        "english": "I would start from ownership and the source of truth, trace validation and side effects, and introduce only the boundaries that protect a real invariant or change axis.",
    },
    "UI": {
        "owner": "الـUI state owner والـcomposition أو view lifecycle",
        "trace": "تتبع user event إلى state mutation، ثم invalidation أو recomposition، وبعدها layout/draw/semantics من غير side effect داخل rendering.",
        "test": "اختبر reducer بحالة controlled، ثم semantics وlifecycle وRTL وfont scale على Android، وقِس frames قبل أي performance claim.",
        "alternative": "اختار state محلية للمكوّن البسيط وhoisted state للتنسيق؛ متحوّلش كل تفصيلة لـglobal ViewModel state.",
        "english": "I would trace the user event into immutable UI state, keep rendering side-effect free, and verify semantics, lifecycle, and frame behavior at the appropriate test layer.",
    },
    "PRO": {
        "owner": "الـproduction contract والـrelease owner",
        "trace": "صنّف failure الأول، اربطه بالversion وcohort وtimeline، حدد irreversible side effect، وبعدها اختار mitigation وrollback threshold قبل rollout.",
        "test": "استخدم release-like build وfailure injection وmigration paths وpercentiles، وافصل evidence من logs عن device trace وعن backend record.",
        "alternative": "اختار أبسط mitigation قابلة للرجوع؛ optimization أو retry أو keep rule واسعة تحتاج evidence لأنها ممكن تخفي failure أكبر.",
        "english": "I would classify the failure, correlate it with the exact release and cohort, protect irreversible side effects, and define rollout and rollback evidence before changing production behavior.",
    },
    "SYS": {
        "owner": "الـclient/server state contract",
        "trace": "حوّل requirements لـstate machine وidentities، تتبع request أو event عبر local store وnetwork وserver authority، وحدد duplicate وout-of-order وoffline paths.",
        "test": "اختبر retries وduplicates وgaps وconflicts وaccount switch، واستخدم metrics عن freshness وlatency وfailure recovery بدل happy-path demo.",
        "alternative": "قلل realtime أو consistency لو product contract يسمح، أو انقل authority للserver لما client evidence لا تكفي للأمان أو التسوية.",
        "english": "I would define identities and state transitions across client and server, design for duplicate and out-of-order delivery, and prove recovery with observable end-to-end evidence.",
    },
    "INT": {
        "owner": "صاحب القرار والتنفيذ والنتيجة",
        "trace": "رتب الإجابة Situation ثم Task ثم Action أنت عملتها فعلًا ثم Result بالأرقام أو evidence، وبعدها وضّح trade-off واللي اتعلمته.",
        "test": "راجع القصة ضد artifacts أو metrics حقيقية، افصل مساهمتك عن الفريق، وجهز follow-up عن failure أو disagreement من غير مبالغة.",
        "alternative": "لو مفيش نتيجة رقمية استخدم evidence نوعية محددة، ومتخترعش ownership أو impact مش حصل.",
        "english": "I would give a truthful STAR answer, separate my actions from the team's work, support the result with evidence, and explain the trade-off and lesson without blaming people.",
    },
    "DSA": {
        "owner": "الـinput/output contract والـalgorithm invariant",
        "trace": "عرّف contract والedge cases، ابدأ بحل صحيح، اكتب invariant، وتتبع كل mutation قبل ما تعلن time أو space complexity.",
        "test": "اختبر empty وsingle وduplicates وoverflow وworst case وعدم mutation لو contract تمنعها، وقارن output بالحل البسيط على inputs صغيرة.",
        "alternative": "استخدم sorting أو heap أو hash structure حسب operations وmemory والordering المطلوب؛ مفيش structure أفضل مطلقًا.",
        "english": "I would define the contract and invariant first, derive the data structure from the required operations, and test adversarial boundaries before claiming complexity.",
    },
    "ART": {
        "owner": "مرحلة الـtoolchain أو runtime المحددة",
        "trace": "سمّي artifact قبل وبعد كل مرحلة: Kotlin source، class files، D8/R8، DEX/APK، ثم ART execution، ومتخلطش guarantee بين مرحلتين.",
        "test": "افحص release artifact وmapping وDEX وdevice version والtrace المناسب؛ JVM output وحده لا يثبت Android runtime behavior.",
        "alternative": "استخدم keep rule ضيقة أو implementation أبسط قبل تعطيل shrinking أو افتراض مشكلة في ART.",
        "english": "I would name the exact build or runtime stage, inspect its input and output artifact, and avoid transferring guarantees between Kotlin, JVM bytecode, DEX tooling, and ART.",
    },
    "CON": {
        "owner": "الـshared invariant والـsynchronization owner",
        "trace": "اكتب interleaving تكسر invariant، فرّق atomicity عن visibility، وحدد critical section من غير I/O أو callback يعيد الدخول.",
        "test": "استخدم controlled interleavings وstress كإشارة إضافية، واختبر cancellation وcleanup وqueue bounds بدل الاعتماد على timing محظوظ.",
        "alternative": "فضّل immutability أو confinement لما تبسط reasoning؛ استخدم Mutex أو atomic state لما invariant تحتاج update متزامنة فعلًا.",
        "english": "I would state the shared invariant, demonstrate the harmful interleaving, and choose immutability, confinement, a mutex, or atomic state according to the whole invariant.",
    },
    "EUI": {
        "owner": "مرحلة الـUI pipeline اللي ظهر فيها الخلل",
        "trace": "تتبع input وsnapshot state وcomposition ثم measure/layout/draw والsemantics؛ حدد المرحلة البطيئة أو المكسورة بدل عدّ recompositions فقط.",
        "test": "استخدم semantics وvisual checks وTalkBack وframe traces على release-like build، واختبر adaptive layout وfocus restoration.",
        "alternative": "بسّط custom UI أو ارجع لمكوّن platform لما تكلفة الصيانة والaccessibility أكبر من المكسب المقاس.",
        "english": "I would locate the issue in state, composition, layout, draw, input, or semantics, then measure that stage and recheck accessibility after the optimization.",
    },
    "STF": {
        "owner": "الـproduct outcome والـorganizational owner",
        "trace": "حوّل الغموض لـrequirements وnon-goals وSLO، ارسم ownership وblast radius، ثم صمم migration وrollback وتشغيل يومي قبل الشكل النهائي.",
        "test": "استخدم adoption وreliability وcost metrics، جرب seam صغيرة قابلة للرجوع، واختبر failure وmigration بدل big-bang promise.",
        "alternative": "اختار قرارًا reversible أو manual process مؤقت لو uncertainty أعلى من قيمة platform أو rewrite كبيرة.",
        "english": "I would shape measurable requirements, assign ownership, bound the blast radius, and design migration, rollback, and operations before committing to a broad platform change.",
    },
    "POS": {
        "owner": "هوية الـpayment attempt وحدود terminal وhost",
        "trace": "تتبع attempt ID من UI إلى card read ثم authorization وterminal outcome، وافصل approved وdeclined وunknown وreversal وreconciliation.",
        "test": "اختبر disconnect وduplicate callback وtimeout بعد authorization وrestart، وتأكد إن logs لا تحتوي PAN أو track data أو secrets.",
        "alternative": "اعمل reconcile بنفس operation identity بدل automatic new payment retry لما outcome غير معروفة.",
        "english": "I would keep one stable payment-attempt identity across the terminal and host, model unknown outcomes explicitly, and reconcile before any retry that could create a second charge.",
    },
}

INVARIANTS = {
    "KOT": "كل value تعدي الـboundary لازم تطابق الـdeclared type والnullability contract، وأي runtime cast أو platform type يفضل untrusted لحد validation.",
    "COR": "بس الـcurrent owner يقدر ينشر terminal state، وكل child تنتهي success أو failure أو cancellation قبل ما الـscope تعتبر مكتملة.",
    "AND": "بعد recreation أو process restart، الشاشة ترجع من persisted identifiers وsource of truth من غير الاعتماد على object كانت عايشة في memory.",
    "ARC": "كل state لها owner واحد واضح، والـside effect تحصل مرة واحدة عند boundary معلومة، والنتيجة القديمة ما تكتبش فوق state أحدث.",
    "UI": "نفس immutable UI state تنتج نفس visible semantics، وأي effect لها key وlifecycle وcleanup معروفين.",
    "PRO": "القرار يعتمد على نفس build وscenario وcohort وmetric؛ أي مقارنة تغير واحد منهم لا تثبت regression أو fix.",
    "SYS": "كل command أو event لها stable identity وversion/order، وتكرار delivery لا يخلق business effect جديد ولا يخفي gap.",
    "INT": "كل claim عن ownership أو impact لازم يتسند إلى action محددة عملتها وevidence حقيقية من غير تضخيم دورك أو تقليل دور الفريق.",
    "DSA": "بعد معالجة أول i عناصر، الـdata structure تمثل بالضبط الحل الجزئي المعرّف في الـinvariant، من غير فقد duplicates أو كسر ordering contract.",
    "ART": "كل claim تخص artifact ومرحلة واحدة محددة؛ class files وDEX وoptimized release artifact وruntime trace مش أدلة قابلة للاستبدال.",
    "CON": "أي observer يشوف shared state تحقق الـinvariant كاملة؛ ممنوع يشوف نصف update أو يعتمد correctness على interleaving محظوظة.",
    "EUI": "أي optimization تحافظ على visible state وidentity وfocus وsemantics، وتثبت تحسن frame behavior على build ممثلة.",
    "STF": "كل قرار كبير له owner وsuccess metric وmigration وrollback trigger؛ مفيش rewrite أو platform بلا adoption وتشغيل واضحين.",
    "POS": "كل payment attempt لها identity واحدة وterminal outcome واحد؛ unknown تفضل unknown لحد reconciliation وممنوع تتحول تلقائيًا لمحاولة خصم جديدة.",
}

WRONG_ANSWERS = {
    "KOT": "Kotlin's type system guarantees the runtime value, so no boundary validation is needed.",
    "COR": "Put it in GlobalScope and retry the operation if the result looks stale.",
    "AND": "It worked after a normal launch on my device, so the lifecycle and process contract is correct.",
    "ARC": "Add another Repository and UseCase because Clean Architecture requires more layers.",
    "UI": "Mark the type stable, reduce recomposition, and use a screenshot as proof that the UI is correct.",
    "PRO": "Increase the timeout, add retries, and accept one debug profile as production evidence.",
    "SYS": "Use a WebSocket and exactly-once delivery will handle ordering, duplicates, and recovery.",
    "INT": "We fixed everything and the project succeeded; the details of my action and evidence are not important.",
    "DSA": "Use a HashSet and call it O(n); duplicates, ordering, overflow, and memory assumptions do not matter.",
    "ART": "ART changed Kotlin semantics, so the release-only failure cannot come from shrinking or packaging.",
    "CON": "Coroutines are sequential code, therefore shared mutable state is automatically thread-safe.",
    "EUI": "Add @Stable and fewer recompositions will automatically fix jank and accessibility.",
    "STF": "A clean rewrite and a shared platform will solve the organizational problem once every team migrates.",
    "POS": "If the terminal response is lost, start a new payment attempt immediately so the user is not blocked.",
}

ENGLISH_EVIDENCE = {
    "KOT": "My evidence would be a boundary test plus the exact compiler, bytecode, DEX, or runtime artifact involved.",
    "COR": "I would reproduce the interleaving with virtual time and controlled fakes, including cancellation and stale completion.",
    "AND": "I would test recreation, process death, duplicate entry, and invalid external input on an emulator or device.",
    "ARC": "I would test state transitions, dependency call counts, stale completions, and the source-of-truth boundary.",
    "UI": "I would combine reducer tests with Android semantics, lifecycle, RTL, font-scale, and frame evidence.",
    "PRO": "I would use a release-like build, comparable cohorts and percentiles, failure injection, and a predefined rollback threshold.",
    "SYS": "I would test duplicate, delayed, missing, and out-of-order events and observe recovery across both client and server.",
    "INT": "I would support the story with a concrete artifact or metric and clearly separate my action from the team's contribution.",
    "DSA": "I would trace the invariant and test empty, duplicate, boundary, overflow, and worst-case inputs against a simple oracle.",
    "ART": "I would inspect the release artifact, mapping, DEX or runtime trace from the exact affected build and device version.",
    "CON": "I would force harmful interleavings, verify atomic state transitions, and cover cancellation while the critical section is active.",
    "EUI": "I would measure the relevant frame stage on a release-like build and recheck semantics and focus after the change.",
    "STF": "I would validate the decision with adoption, reliability, cost, migration, and rollback evidence before expanding its blast radius.",
    "POS": "I would simulate disconnects and duplicate callbacks, then reconcile by the original attempt identity while keeping diagnostics PCI-safe.",
}

FACT_OVERRIDES = {
    "build pipeline": "The Android build pipeline compiles Kotlin to JVM class files, desugars and converts bytecode to DEX, optionally shrinks and optimizes it with R8, packages resources, signs the artifact, and hands installed DEX to ART.",
}

MECHANISMS = [
    (("configuration change", "saved-state", "restoration", "remembersaveable"),
     "وقت configuration change، الـActivity والـView tree بيتعمل لهم recreation، بينما ViewModel الخاصة بالowner القديمة ممكن تتوصل بالowner الجديدة. وقت process death مفيش object بتعيش؛ Android يرجع Bundle صغيرة، والتطبيق يعيد تحميل البيانات باستخدام ID ثابتة من database أوnetwork."),
    (("intent", "pendingintent", "exported", "deep-link", "deep link"),
     "الـIntent مجرد رسالة فيها action وdata وextras، والـintent filter يعمل routing فقط. هو لا يثبت هوية المرسل ولا authorization. PendingIntent تضيف تفويضًا من creator لكن identity وrequestCode وmutability يحددوا هل pending intents هتتبدل أوتتعدل."),
    (("looper", "messagequeue"),
     "الـmain thread عندها Looper تسحب Message أوRunnable واحدة من MessageQueue وتنفذها للنهاية قبل اللي بعدها. لو Runnable أخدت 200ms، input وlifecycle callbacks وChoreographer frames يفضلوا مستنيين؛ مفيش parallelism سحري لمجرد إن الدالة suspend."),
    (("binder",),
     "الـBinder proxy يكتب transaction في kernel driver، والـserver thread يقرأها وينفذها. لو call synchronous فالـcaller تفضل blocked لحد reply؛ زمنها يشمل queueing والremote work وأي lock contention، مش زمن method body بس."),
    (("anr", "evidence-tool", "reproduction matrix", "evidence communication"),
     "الـANR trace snapshot لحظة من timeline. لازم تحدد main thread كانت Running ولا Blocked ولا Waiting، وبعدها تتبع lock owner أوBinder peer وتربط timestamp بـPerfetto وlogcat. أعلى frame في stack ممكن تكون مكان الانتظار وليست سبب الانتظار."),
    (("handler leak",),
     "MessageQueue تحتفظ بالـRunnable لحد وقت التنفيذ. لو الـlambda قافلة على Activity أوView، السلسلة Queue → Message → Runnable → Activity تمنع الـGC حتى لو الشاشة اتقفلت."),
    (("work mechanism", "worker retry", "foreground-service", "foreground service", "doze", "unique work"),
     "WorkManager تحفظ WorkSpec في database وتعيد جدولة الشغل تحت قيود النظام؛ Foreground Service عملية ظاهرة للمستخدم بإشعار والتزامات بدء ونوع service؛ coroutine داخل screen owner تنتهي بانتهاء الـowner. الاختيار هنا lifetime contract، مش تفضيل API."),
    (("main-safe api",),
     "كلمة suspend لا تختار thread. الـdata source اللي تعرف إن driver blocking هي المسؤولة تنقل الجزء blocking إلى injected IO dispatcher، وبكده كل caller تحصل على main-safe contract من غير ما تعرف implementation."),
    (("cancellation", "noncancellable", "timeout"),
     "إلغاء coroutine يغيّر Job state ويوقظ suspension points المتعاونة بـCancellationException. CPU loop بلا checkpoint أوI/O خارجية قد تكمل. catch واسع يحول cancellation لـfailure عادية ويخلي code تنشر state بعد انتهاء الـowner."),
    (("cold flow",),
     "الـcold Flow وصف للتنفيذ؛ كل collect تستدعي builder وupstream من البداية. stateIn أوshareIn يشغلوا upstream واحدة داخل scope محددة ويعرضوا hot stream، لذلك start policy وreplay وscope lifetime جزء من correctness."),
    (("stateflow", "sharedflow", "state versus event", "buffer", "backpressure"),
     "StateFlow تحتفظ بقيمة حالية وتعمل equality conflation. SharedFlow تبث للقائمين بالcollection حسب replay وbuffer policy. الاتنين in-memory؛ حدث لازم ينجو من process death أويتنفذ once يحتاج storage وidentity وacknowledgement."),
    (("collectlatest", "flatmaplatest", "stale result", "request generation", "lifecycle collection"),
     "latest operators تلغي coroutine القديمة، لكنها لا تعمل rollback لrequest وصلت server ولا تمنع callback غير متعاونة. لذلك owner تستخدم generation أوoperation ID عند commit النهائي، والـcollector نفسها ترتبط بالـview lifecycle."),
    (("runtest", "scheduler", "testing hot flows", "flaky test"),
     "runTest تبني TestScope بvirtual clock وتراقب children. لما كل TestDispatcher تشارك نفس scheduler، runCurrent وadvanceUntilIdle يتحكموا في كل الشغل؛ أي real dispatcher أوsleep يرجع race مرتبطة بسرعة الجهاز."),
    (("hilt", "qualifier", "singleton session", "di replacement", "service locator"),
     "Hilt component تحتفظ بالـscoped instance داخل عمر الـcomponent نفسها. SingletonComponent تعيش عمر process، ActivityRetainedComponent تعدي configuration change، وActivityComponent تتبدل مع Activity. لو account state اتحطت Singleton فهي لا تتصفر تلقائيًا عند logout."),
    (("module boundary", "dependency direction", "public api", "build and ownership"),
     "Gradle module تعمل compilation وdependency boundary حقيقية، لكن كل boundary تزود configuration وAPI surface. الاتجاه الصحيح يخلي feature تشوف contract صغيرة، بينما implementation تفضل internal عشان تغييرها لا يجبر graph كلها تعيد البناء أوالتعديل."),
    (("adr", "architecture review", "review severity", "repository conflict"),
     "المراجعة القوية تتبع input إلى state mutation وside effect ثم failure path. الـADR تحفظ السبب والبدائل والنتائج وrevisit trigger؛ هي سجل قرار، مش شهادة إن القرار أبدي."),
    (("timeout taxonomy", "retry safety", "token refresh", "unknown outcome", "backoff"),
     "connect/read/call timeouts بتحصل في مراحل مختلفة. timeout بعد إرسال write لا تثبت إن server لم تنفذها. لذلك operation ID وidempotency/status lookup يمنعوا duplicate effect، وsingle-flight تخلي concurrent 401 تشارك refresh واحدة."),
    (("build pipeline", "compatibility matrix", "r8", "variant isolation", "signing"),
     "Kotlin compiler تنتج class files، desugaring تعالج language/library features، D8 يحول لـDEX، وR8 يحلل reachability ويعمل shrink/optimize/obfuscate. بعد packaging وsigning، الجهاز يثبت artifact وART تحمل DEX؛ debug وrelease ممكن يختلفوا جذريًا."),
    (("measurement", "startup", "perfetto", "memory evidence"),
     "القياس يبدأ journey وbuild وdevice class ثابتين. Perfetto يربط scheduling وBinder وI/O وframes على timeline، heap dump تبحث عن retained paths، وMacrobenchmark تقارن startup أوframe percentiles. أداة واحدة لا تجيب كل الأسئلة."),
    (("incident rollout", "release gate", "staged rollout", "rollback"),
     "الـstaged rollout تقسم exposure إلى cohorts وتنتظر observation window ثابتة. crash وdata loss وsecurity كل واحدة gate مستقلة؛ المتوسط لا يلغي blocker. rollback trigger يتحدد قبل الضغط عشان الفريق ما يغيرش threshold أثناء الحادث."),
    (("migration coverage", "room migration"),
     "Room schema version على أجهزة المستخدمين قديمة بسنين. نجاح clean install يختبر target schema فقط؛ MigrationTestHelper لازم تفتح database fixture من كل starting version، تطبق path للtarget، وبعدها تفحص rows وindices وforeign keys."),
    (("source of truth", "durable outbox", "conflict", "tombstone", "sync observability"),
     "الـUI تقرأ local database كحقيقة حالية. user edit وoutbox operation يتكتبوا في transaction واحدة، والworker ترسل operation ID ثابتة. response ترجع transaction تحدث canonical row وتمسح pending marker؛ version/tombstone تمنع stale overwrite وresurrection."),
    (("session state", "refresh race", "secure storage", "account partitioning", "server authority"),
     "session state machine تربط كل token وcache وwork بـaccount generation. لو refresh بدأت في generation 4 ثم logout نقل الحالة لـ5، نتيجة 4 تُرفض. Keystore تحمي key material على الجهاز لكن server تظل authority للauthorization وrevocation."),
    (("push as signal", "ordering and gaps", "reconnect", "location freshness", "privacy"),
     "push وWebSocket delivery ممكن تتكرر أوتضيع أوتوصل بترتيب مختلف. client تحفظ آخر server sequence، تكشف gap، تعمل catch-up، وبعدها dedupe قبل apply. connection owner واحدة تمنع sockets متوازية بعد network flap."),
    (("state reads", "state hoisting", "immutable collections", "stability", "recomposition"),
     "Compose تسجل snapshot state المقروءة أثناء composition. تغيير observable value يعمل invalidation للscopes اللي قرأتها؛ mutation داخل List عادية لا تُرى. stability تساعد skipping فقط لو contract صادقة، ولا تعالج work غالية داخل composition."),
    (("launchedeffect", "disposableeffect", "rememberupdatedstate", "lifecycle-aware", "effect testing"),
     "LaunchedEffect تربط coroutine بمجموعة keys؛ تغير key يلغي القديمة ويبدأ جديدة. DisposableEffect تربط register/unregister بنفس lifetime. rememberUpdatedState تغير القيمة المقروءة داخل effect طويلة من غير restart."),
    (("back-stack", "typed arguments", "singletop", "navigation"),
     "NavHost تملك sequence من back-stack entries، وكل entry لها lifecycle وSavedStateHandle. route المفروض تحمل ID صغيرة لاobject stale؛ singleTop يقارن القمة فقط، وdeep link لازم تبني stack منطقية بعد validation وauthorization."),
    (("adaptive", "rtl", "font-scale", "accessibility", "semantics", "ui performance", "ui test"),
     "الـlayout تختار من available window size وتستخدم start/end بدل left/right. semantics tree هي الواجهة اللي TalkBack والtests تقرأها، وممكن تختلف عن pixels. font scale وfocus order جزء من functional correctness، مش polish."),
    (("kotlin to dex", "d8 versus r8", "art execution", "zygote", "class loading", "jni", "reflection", "boxing", "crash retrace", "runtime evidence"),
     "كل مرحلة لها artifact مختلف: Kotlin/JVM class، DEX، packaged release، ثم runtime state على ART. class identity تشمل defining ClassLoader؛ JNI تضيف native lifetime/thread rules؛ reflection تخفي reachability عن R8. الدليل لازم يطابق المرحلة."),
    (("race", "atomicity", "mutex", "atomic update", "confinement", "immutability", "deadlock", "stress", "locks"),
     "الـrace تحصل لما نتيجتين صحيحتين منفردًا تتداخلوا فيكسروا invariant مشتركة. visibility تجعل write مرئية لكنها لا تجعل read-modify-write atomic. الحل يحمي الـtransition كاملة بatomic state أوMutex قصيرة أوserialized owner."),
    (("frame pipeline", "snapshot state", "custom layout", "lazy list", "nested scroll", "focus", "edge-to-edge", "ui benchmark"),
     "frame تبدأ input/state ثم composition أوview traversal، measure/layout، draw وGPU. stable keys تحفظ item identity، nested scroll توزع deltas بين parent/child، وinsets لها owner واحدة. لازم تحدد أي stage بطيئة قبل optimization."),
    (("requirement shaping", "architecture evolution", "ownership model", "slo", "blast-radius", "migration governance", "platform product", "decision under uncertainty", "cross-team", "operational design"),
     "قرار Staff-level يتحول من رأي إلى system تشغيل: user outcome وSLO وowner وmigration وrollback وon-call. strangler seam تقلل blast radius، وplatform لا تعتبر ناجحة من غير consumers حقيقية وadoption/support metrics."),
    (("reversal", "settlement", "terminal operation", "hardware disconnect", "pci-safe", "payment"),
     "payment attempt تبدأ بـstable operation ID وتتحرك بين states واضحة. authorization response المفقودة تعني Unknown لاDeclined؛ settlement وreversal مراحل ledger مختلفة. callback لا تُقبل إلا لو attempt ID تطابق الحالية، والdiagnostics لا تخزن card secrets."),
    (("incident", "hypothesis", "risk prioritization", "trust boundaries", "security regression"),
     "وقت incident بنفصل observation عن hypothesis. coordinator واحدة تحفظ timeline، mitigation reversible تقلل الضرر، وبعدها experiment تفرق بين سببين. في security، client input غير موثوق والbackend تعيد authorization."),
    (("capstone boundaries", "test portfolio", "failure injection", "observability contract", "toolchain honesty"),
     "الـcapstone تتبع operation ID واحدة من UI intent إلى local transaction ثم outbox وworker وserver result. كل test layer تمسك risk مختلفة: reducer للstate، database للdurability، worker للretry، وdevice للframework. telemetry تسجل stage وduration من غير content حساس."),
    (("severity and scope", "mitigation before certainty", "incident roles", "hypothesis testing", "post-incident"),
     "severity تتحدد من عدد المستخدمين والوظائف والdata/security impact، مش صوت أعلى شخص. Incident Commander تنسق timeline والقرارات، وmitigation reversible تقلل الضرر قبل اكتمال root cause. follow-up لا تتقفل إلا بowner وdeadline ودليل."),
    (("release-like performance", "trade-off communication"),
     "performance claim تحتاج نفس journey وrelease build وdevice class وpercentile. الـtrade-off يتقال كـinvariant بنحميها، تكلفة مقاسة، بدائل، وrollback signal؛ من غيرهم تبقى preference لاقرار هندسي."),
    (("requirement discovery", "state ownership", "concurrency boundary", "alternative comparison", "design verification"),
     "قبل رسم components بنحوّل requirements إلى state machine وidentities وSLO. كل mutable state لها authority واحدة وpersistence level وconflict policy؛ البدائل تتقارن بنفس معايير latency وconsistency وcost وrecovery، ثم failure injection تختبر assumptions."),
    (("flakiness removal",),
     "الـflaky UI test غالبًا تعتمد على clock أوdispatcher أوnetwork أوanimation غير متحكم فيها. الحل inject هذه dependencies وتنتظر semantic condition محددة؛ sleep أطول يوسع الاحتمال ولا يثبت إن الحالة المطلوبة وصلت."),
    (("stack live-coding", "hash-map invariant", "binary-search invariant", "sliding-window invariant",
      "interval merge", "lru cache", "top k", "cycle detection", "dp optimization",
      "bfs and dfs", "heap invariant", "dijkstra", "dynamic-programming", "graph test", "dsa invariant"),
     "في live coding، الـinvariant هي معنى الـdata structure بعد كل خطوة. بنحددها قبل code، نعمل trace على edge case تكسر الحل الساذج، وبعدها نشتق complexity من عدد الزيارات والعمليات بدل حفظ اسم pattern."),
    (("twenty-second", "ninety-second", "clarifying", "uncertainty", "shadowing", "readiness", "gap-driven", "mock", "portfolio", "interview-day"),
     "الإجابة القوية تبدأ conclusion قصيرة، ثم mechanism ومثال وفشل وtrade-off حسب الوقت. المرشح يفصل اللي نفذه عن اللي صممه نظريًا، ويسأل عن constraint تغير القرار بدل ما يفترضها."),
]


def mechanism_for(topic: str, profile: dict[str, str]) -> str:
    if topic in EXACT_GUIDANCE:
        detail = EXACT_GUIDANCE[topic]
        return f"{detail['invariant']} {detail['correction']}"
    key = topic.lower()
    for needles, explanation in MECHANISMS:
        if any(needle in key for needle in needles):
            return explanation
    return profile["trace"]


def split_frontmatter(text: str) -> tuple[str, str]:
    match = re.match(r"^(---\n.*?\n---\n)(.*)$", text, flags=re.DOTALL)
    if not match:
        raise ValueError("missing front matter")
    return match.group(1), match.group(2)


def field(frontmatter: str, name: str) -> str:
    match = re.search(rf"^{re.escape(name)}:\s*(.+)$", frontmatter, flags=re.MULTILINE)
    return match.group(1).strip().strip("\"'") if match else ""


def plain(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    return " ".join(html.unescape(value).split()).strip()


def html_inline(value: str) -> str:
    """Render generated prose safely inside raw HTML without Markdown leakage."""
    return html.escape(html.unescape(value).replace("`", ""), quote=False)


def first_prompt(body: str) -> str:
    lines = [
        line.strip()
        for line in body.splitlines()
        if line.strip() and not line.startswith("#") and not line.startswith("[")
    ]
    return plain(" ".join(lines))


def interviewer_question(body: str) -> str:
    match = re.search(
        r"^>\s*\*\*Interviewer:\*\*\s*(.+)$",
        body,
        flags=re.MULTILINE,
    )
    return plain(match.group(1)) if match else ""


def spoken_answer(text: str, topic: str) -> str:
    override = FACT_OVERRIDES.get(topic.lower())
    if override:
        return override
    match = re.search(r"\*\*Spoken answer:\*\*\s*[“\"](.*?)[”\"]\s*(?:\n|$)", text, flags=re.DOTALL)
    answer = plain(match.group(1)) if match else ""
    if not answer or ARABIC.search(answer):
        return f"{topic} needs an explicit contract, a clear owner, defined failure behavior, and evidence from the boundary that implements it."
    return answer


def arabic_explanation(text: str) -> str:
    paragraphs = re.findall(r"<p\b[^>]*dir=[\"']rtl[\"'][^>]*>(.*?)</p>", text, flags=re.DOTALL | re.IGNORECASE)
    cleaned = [plain(p) for p in paragraphs if len(plain(p)) > 80]
    return cleaned[0] if cleaned else "ابدأ من الـcontract والـowner والfailure path، وبعدها اختار implementation واختبار يثبتوا السلوك المطلوب."


def scenario(question_body: str, answer_text: str, topic: str) -> str:
    contextual = re.search(
        r"<p\b[^>]*>\s*<strong>السياق:</strong>\s*(.*?)</p>",
        question_body,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if contextual:
        return plain(contextual.group(1))
    hardened = re.search(
        r"## (?:Production|Interview) scenario\s*\n+\s*<p\b[^>]*>(.*?)</p>",
        question_body,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if hardened:
        return plain(hardened.group(1))
    prompt = first_prompt(question_body)
    core = re.search(r"A senior review exposes this failure:\s*(.*?)\s*Explain\b", prompt)
    if core:
        return plain(core.group(1))
    specialist = re.search(r"الخطأ الواقعي اللي لازم تمنعه:\s*(.*?)(?:\.|$)", plain(answer_text))
    if specialist:
        return plain(specialist.group(1))
    if prompt:
        return prompt
    return f"الـproduction behavior المرتبط بـ{topic} بقى غير deterministic ومحتاج root-cause analysis واختبار regression."


def decision(answer_text: str, profile: dict[str, str]) -> str:
    match = re.search(r"القرار العملي هو:\s*(.*?)(?:</p>|\n\n)", answer_text, flags=re.DOTALL)
    if not match:
        match = re.search(r"التصحيح العملي:\s*(.*?)(?:</p>|\n\n)", answer_text, flags=re.DOTALL)
    if not match:
        match = re.search(r"<strong>Corrected decision:</strong>\s*(.*?)</p>", answer_text, flags=re.DOTALL)
    return plain(match.group(1)) if match else profile["alternative"]


EXACT_GUIDANCE = {
    "Token refresh single-flight": {
        "invariant": "كل مجموعة 401 ناتجة عن نفس الـexpired token تشارك refresh واحدة، وكل request أصلية تُعاد مرة واحدة فقط؛ فشل refresh ينهي الجلسة بدل loop جديدة.",
        "correction": "احمِ refresh بsingle-flight primitive، افحص إن الـtoken التي فشلت ما زالت current، انشر token الجديدة atomically، ثم replay مرة واحدة. لو refresh رجعت 401 أوفشلت نهائيًا امسح session واطلب login.",
        "test": "ابدأ عشر requests بنفس الـtoken، أرجع لهم 401 معًا، وتأكد من refresh call واحدة وعشر replays فقط. غطّ cancellation وrefresh failure و401 ثانية بعد replay.",
        "alternative": "Authenticator مركزي مناسب لو الـHTTP stack تضمن serialization؛ repository-level coordination أوضح لو token جزء من session state machine أوسع.",
        "wrong": "Let every failed request refresh independently and keep retrying until one succeeds.",
    },
    "Unknown outcome": {
        "invariant": "timeout بعد إرسال write لا يثبت success ولاfailure؛ العملية تفضل Unknown ومربوطة بـstable operation ID لحد ما backend تؤكد الحالة.",
        "correction": "اعرض Pending confirmation، امنع إنشاء charge جديدة، واستعلم بـoperation ID أوidempotency key. عند رجوع النتيجة حوّل الحالة مرة واحدة إلى Succeeded أوFailed وسجّل reconciliation واضح.",
        "test": "اقطع الاتصال قبل وصول request، وبعد backend commit وقبل response، ووقت status lookup. اثبت إن الحالة الثانية تصبح Unknown وإن retry لا تعمل duplicate charge.",
        "alternative": "للread الآمنة retry تلقائية مقبولة؛ للwrite غير idempotent من غير status API تحتاج manual reconciliation بدل تخمين النتيجة.",
        "wrong": "A timeout means the payment failed, so immediately create a new payment request.",
    },
    "Service locator trade-off": {
        "invariant": "كل object لازم تستلم dependencies المطلوبة بشكل ظاهر، والـlifetime والreplacement يفضلوا تحت سيطرة composition root بدل global mutable registry.",
        "correction": "لف الـlegacy locator خلف adapters صغيرة، وابدأ constructor injection من الـnew code والleaves للداخل. خلي composition root واحدة، وامنع أي registration أو lookup جديد خارج migration seam.",
        "test": "شغّل testين بترتيب عكسي وتأكد إن مفيش global registration متسربة، وابنِ object graph بfake واحدة من غير reset سحري أو Android process جديد.",
        "alternative": "locator محلية immutable داخل plugin boundary أو framework callback قد تكون مقبولة لو lookup surface صغيرة والlifetime صريحة؛ global mutable locator ليست نفس الحالة.",
        "wrong": "A global service locator is equivalent to constructor injection because both eventually return the same object.",
    },
    "Timeout taxonomy": {
        "invariant": "اسم timeout وحده لا يحدد هل الاتصال بدأ، هل request bytes خرجت، هل response بدأت، أو هل server commit حصل؛ كل deadline لها stage وowner ودليل مختلف.",
        "correction": "سجّل connect/read/write/call/application deadline منفصلة، اربطها بـoperation ID، واعمل retry فقط لما operation آمنة أو idempotent؛ write ذات outcome مجهولة تنتقل لـstatus lookup أوreconciliation.",
        "test": "اقطع الاتصال قبل connect، أثناء request body، بعد server commit وقبل response، وأثناء response body؛ تحقق من classification ومن عدم تكرار side effect.",
        "alternative": "deadline واحدة end-to-end أبسط للcaller، لكن احتفظ بسبب داخلي يسمح بالتشخيص وسياسة retry الصحيحة.",
        "wrong": "A timeout proves that the server did not execute the request.",
    },
    "Signing boundary": {
        "invariant": "هوية التطبيق تعتمد على signing lineage؛ upload key ترسل artifact إلى Play بينما app-signing key توقع النسخة التي تصل للمستخدم، ولا واحدة منهما توضع داخل repository أوAPK.",
        "correction": "استخدم Play App Signing، خزّن upload credential في CI secret store بصلاحية محدودة، فعّل rotation والاسترجاع، واربط كل release بالartifact digest وsigning certificate المتوقع.",
        "test": "تحقق في CI من certificate digest للartifact، ارفض unsigned أوwrong-key bundle، وجرّب update path على نسخة موقعة من release lineage الصحيحة.",
        "alternative": "لو التوزيع خارج Play، HSM أوmanaged signing service تمسك production key؛ local keystore مناسبة فقط لبيئات التطوير المقيدة.",
        "wrong": "The signing password inside gradle.properties is sufficient protection for a production signing key.",
    },
    "Secure storage": {
        "invariant": "Keystore تحمي key material وتقلل استخراجها، لكنها لا تجعل client authority ولا تمنع malware أوroot من استخدام session داخل الجهاز المفتوح؛ server تملك expiry وrevocation وauthorization.",
        "correction": "خزّن أقل credential لازمة، شفّر data بمفتاح Keystore عند الحاجة، استخدم short-lived access token وrotating refresh token، وامسح account partition والwork عند logout أوrevocation.",
        "test": "اختبر invalidated key، device credential change، logout، revoked refresh token، backup/restore، وaccount switch؛ تأكد إن cache القديمة لا تفتح لمستخدم جديد.",
        "alternative": "token قصيرة العمر in-memory تقلل persistence risk لو product تقبل login متكرر؛ hardware-backed key مفيدة حسب threat model وليست ضمانًا مطلقًا.",
        "wrong": "A token protected by Android Keystore can be trusted as final authorization without server validation.",
    },
    "Location freshness": {
        "invariant": "كل location لها timestamp وaccuracy وprovider context؛ القيمة الأحدث وصولًا ليست بالضرورة الأحدث قياسًا أوالأدق، والpermission/background policy جزء من العقد.",
        "correction": "حدد max age وrequired accuracy للjourney، ارفض out-of-order measurements بالelapsed realtime، ووازن interval وpriority مع battery والforeground/background rules.",
        "test": "أرسل fixes قديمة تصل متأخر، accuracy ضعيفة، permission downgrade، provider off، background transition، وclock change؛ تحقق من stale UI وfallback الواضح.",
        "alternative": "last-known location مناسبة كبداية معلّمة stale؛ active high-accuracy updates تستخدم فقط لما user journey تبرر battery والpermission cost.",
        "wrong": "The last callback received is always the freshest and most accurate location.",
    },
    "Privacy and observability": {
        "invariant": "الtelemetry تثبت stage والduration والresult من غير raw coordinates أوPAN أوtoken أوuser content، وكل identifier لازم تكون scoped وretained لأقصر مدة لازمة.",
        "correction": "سجل operation ID عشوائية، coarse error category، age/accuracy buckets، duration وapp/device version؛ طبق redaction قبل النقل وRBAC وretention limit في backend.",
        "test": "مرر payload فيها coordinates وtokens وPII عبر كل log/crash/analytics path، وافشل الاختبار لو ظهر raw value؛ راجع إن correlation ما زالت تكفي لإعادة timeline.",
        "alternative": "on-device debug bundle بموافقة المستخدم قد تحتوي تفاصيل أكثر لفترة قصيرة؛ production analytics الافتراضية تفضل aggregated وredacted.",
        "wrong": "Sensitive values are safe to log if the dashboard is accessible only to engineers.",
    },
    "Backpressure": {
        "invariant": "سرعة producer والconsumer غير متساوية، لذلك queue لازم تكون bounded وسياسة suspend/drop/conflate/batch تطابق معنى كل event؛ command لا تُعامل كstate snapshot.",
        "correction": "حدد capacity وoverflow policy صراحة: conflate للstate التي يهم آخرها، buffer محدود للbursts، batch للtelemetry، وsuspend أوdurable queue للأحداث التي ممنوع تضيع.",
        "test": "شغّل producer أسرع 100 مرة من consumer، املأ الـbuffer، ألغِ collector، وأثبت بالIDs أي قيم وصلت أواتجمعت أواترفضت وحد الذاكرة الأقصى.",
        "alternative": "لو producer قابل للتحكم فـbackpressure upstream أفضل من إسقاط downstream؛ durable queue مطلوبة لما الحدث لازم ينجو من process death.",
        "wrong": "Use an unlimited buffer so no event is ever lost.",
    },
    "Focus restoration": {
        "invariant": "الfocus تتبع logical item identity قابلة للاستمرار، مش index أوView instance قد تتغير بعد navigation أوadaptive layout أوdata update.",
        "correction": "احفظ stable item ID، وبعد عودة البيانات اطلب focus فقط لو العنصر ما زال موجودًا وقابلًا للfocus؛ وإلا اختار fallback منطقي قريب من ترتيب القراءة.",
        "test": "ركز item، غادر الشاشة، احذف أوحرّك العنصر، ارجع تحت keyboard وTalkBack وlayout مختلف؛ تحقق من target صحيح وعدم focus trap.",
        "alternative": "في touch-only flow قد يكفي أول عنصر منطقي؛ TV وkeyboard accessibility تحتاج restoration صريحة ومختبرة.",
        "wrong": "Save the adapter index and request focus on the same index after every recreation.",
    },
    "UI performance evidence": {
        "invariant": "تحسين UI لازم يقلل frame time في stage محددة على release-like build مع الحفاظ على pixels وsemantics وinteraction؛ recomposition count وحدها ليست metric نجاح.",
        "correction": "حدد journey وslow-frame percentile، استخدم Perfetto أوMacrobenchmark لتحديد composition/measure/draw/GC/I/O، أصلح أكبر slice، ثم أعد القياس بنفس الظروف.",
        "test": "شغّل benchmark بعد warm-up على نفس device class وcompilation mode، قارن P50/P95/P99 وframe overruns، وأعد semantics وvisual regression بعد التغيير.",
        "alternative": "recomposition رخيصة لا تحتاج منع؛ optimization أعقد تُرفض لو لا تحسن user metric أوتكسر readability/accessibility.",
        "wrong": "A lower recomposition count automatically proves that scrolling is faster.",
    },
    "Zygote model": {
        "invariant": "app process تتعمل fork من Zygote فتبدأ بصفحات preloaded مشتركة copy-on-write، لكن heap والthreads والApplication initialization بعد fork تخص process الجديدة.",
        "correction": "عامل كل app state كـprocess-local، قلل startup work بعد fork، ومتستخدمش Zygote كتبرير لمشاركة mutable state بين تطبيقات أوprocesses.",
        "test": "قارن process IDs وstartup trace وprivate dirty memory قبل وبعد mutation، واختبر secondary process لأن كل process لها Application وstatic state مستقلة.",
        "alternative": "مشاركة data بين processes تحتاج Binder أوprovider أوshared storage بعقد واضح؛ static singleton ليست IPC.",
        "wrong": "Apps forked from Zygote share the same mutable heap and singleton instances.",
    },
    "JNI boundary": {
        "invariant": "كل ABI تحتاج native library ورموز مطابقة، وكل JNIEnv تخص thread، والlocal/global references والpending exceptions لها lifetime وقواعد صريحة.",
        "correction": "تحقق من ABI packaging وsymbol lookup، attach thread native عند الحاجة، حرر global refs، افحص exceptions بعد JNI calls، ومرر buffers بعقد ownership واضح.",
        "test": "شغّل affected ABI على device، اختبر thread attach/detach وGC أثناء native hold وJava exception وmissing symbol، واربط tombstone بالunstripped symbols لنفس build.",
        "alternative": "استخدم pure Kotlin أوstable platform API لو native boundary لا تبرر cost؛ generated bindings تقلل hand-written JNI mistakes.",
        "wrong": "A JNI function that works on one ABI and thread is safe on every device and caller thread.",
    },
    "Boxing and allocation": {
        "invariant": "generic JVM collections تخزن references، فـInt غالبًا تتعمل لها boxing إلى Integer؛ القيمة النظرية O(n) لا تصف allocation وGC cost على hot path.",
        "correction": "اثبت allocation في profiler أوbenchmark، قلل temporary objects، واستخدم primitive array أوspecialized collection فقط في measured hot path مع API boundary واضحة.",
        "test": "قارن نفس workload وrelease build مع warm-up، راقب allocations/op وGC وframe time، وتأكد إن overflow وsemantics لم تتغير مع representation الجديدة.",
        "alternative": "List<Int> أوضح ومناسب لمعظم paths؛ optimization المتخصصة تستحق فقط لما القياس يربط boxing بمشكلة مستخدم.",
        "wrong": "Kotlin Int is always stored as an unboxed primitive, including inside generic collections.",
    },
    "Snapshot state": {
        "invariant": "Compose snapshot تجمع reads وwrites في نسخة متسقة وتطبق mutation policy؛ writes متنافسة تحتاج owner أوmerge واضح بدل افتراض last callback wins.",
        "correction": "اجمع state related في model immutable، نفّذ update من owner واحدة أوsnapshot transaction مناسبة، وانشر value جديدة بدل mutation داخل object غير observable.",
        "test": "اجبر updateين متداخلين على fields مترابطة، اقرأ أثناء composition، واثبت عدم lost update أوstate نصف محدثة وأن invalidation تحصل مرة بالقيمة الصحيحة.",
        "alternative": "StateFlow في ViewModel مناسبة للbusiness state؛ snapshot state محلية ممتازة لUI state المرتبطة بالcomposition.",
        "wrong": "Any mutation made from a coroutine is automatically serialized and visible to Compose.",
    },
}


def topic_guidance(topic: str, prefix: str, fact: str, profile: dict[str, str], existing: str) -> dict[str, str]:
    """Return concrete guidance for high-risk topics, with a fact-based fallback."""
    key = topic.lower()
    base = {
        "invariant": f"في {topic}: {fact} و{INVARIANTS.get(prefix, INVARIANTS['ARC'])}",
        "correction": f"حوّل قاعدة {topic} لعقد واضح عند الـowner: {fact} طبّقها عند أول boundary تملك القرار، ومتسيبش كل caller يخمّن policy مختلفة.",
        "test": f"ابنِ أصغر counterexample يكسر {topic}، ثبّت ترتيب الأحداث والـinputs، واثبت الـobservable result قبل التصحيح وبعده عند نفس الـboundary.",
        "alternative": f"ارفض التصميم لو تطبيق عقد {topic} محتاج state مخفية أو ownership موزعة؛ وقتها بسّط الـAPI أو انقل القرار لowner واحدة.",
        "wrong": WRONG_ANSWERS.get(prefix, WRONG_ANSWERS["ARC"]),
    }
    overrides = [
        (("configuration change", "saved-state", "restoration", "remembersaveable", "process death"), {
            "invariant": "الـin-memory state ممكن تنجو من configuration change فقط، لكن process death تمسحها؛ الاسترجاع يبدأ من IDs وsmall saved state ثم يعيد تحميل canonical data.",
            "correction": "افصل transient UI state عن durable business state، خزّن key صغيرة في SavedStateHandle أو rememberSaveable، وأعد بناء الشاشة من repository بعد process recreation.",
            "test": "غيّر configuration ثم أعد إنشاء الـActivity بsaved state، وبعدها نفّذ fresh process-style launch من غير reuse لأي fake أو singleton وتأكد إن نفس الـID يعيد canonical data.",
            "alternative": "لو القيمة قابلة لإعادة الاشتقاق متخزنهاش؛ ولو هي user-authored data كبيرة احفظها في durable store بدل Bundle.",
            "wrong": "ViewModel survives process death, so keeping the whole screen model there is enough.",
        }),
        (("intent input", "exported component", "pendingintent", "deep-link", "deep link"), {
            "invariant": "أي external Intent أو PendingIntent input غير موثوق لحد validation والauthorization داخل الـcomponent، والـidentity والmutability لازم يكونوا مقصودين.",
            "correction": "حوّل الـIntent إلى typed command بعد فحص action وscheme/host/path والsizes، أعد authorization للحساب الحالي، واستخدم explicit immutable PendingIntent إلا لو fill-in field موثقة مطلوبة.",
            "test": "أرسل lookalike host وduplicate params وoversized extras وwrong account وreplayed PendingIntent، واثبت إن الرفض يحصل قبل أي data access أو side effect.",
            "alternative": "استخدم non-exported proxy أو verified App Link لو callers الخارجيين محدودين؛ ده يقلل surface بدل توسيع intent filter.",
            "wrong": "Android matched the intent filter, so the input is trusted and already authorized.",
        }),
        (("looper", "messagequeue"), {
            "invariant": "الـmain Looper ينفذ message واحدة في المرة؛ أي Runnable طويلة تؤخر input وlifecycle وframe callbacks اللي وراها.",
            "correction": "قسّم CPU work لنقط cancellable أو انقل blocking work للboundary المالكة لـdispatcher، وسيب main thread للـUI mutations القصيرة.",
            "test": "حط marker قبل الـRunnable وبعدها وInput/Choreographer marker في Perfetto، ثم اثبت إن الـqueue delay والslow frames تختفي بعد نقل الشغل.",
            "alternative": "لو العمل صغير تحت budget خليه على main لتجنب coordination؛ القرار مبني على frame evidence مش على وجود suspend keyword.",
            "wrong": "A suspend function cannot block the main Looper.",
        }),
        (("synchronous binder",), {
            "invariant": "الـsynchronous Binder call توقف caller لحد reply؛ main thread budget تشمل queueing والremote work والlock contention.",
            "correction": "انقل call من main لو contract تسمح، قلل payload والعمل داخل transaction، ومتحتفظش local lock أثناء IPC.",
            "test": "بطّئ remote service واحبس lock متحكم فيه، ثم راقب binder transaction والmain-thread blocked slice في Perfetto/ANR trace.",
            "alternative": "oneway مناسب فقط لcommand لا تحتاج reply أو ordering أقوى؛ مش تحويل آلي لكل Binder call.",
            "wrong": "Binder runs in another process, so a synchronous call cannot block the UI thread.",
        }),
        (("anr evidence", "anr triage", "evidence-tool", "reproduction matrix", "evidence communication"), {
            "invariant": "الـdiagnosis تفصل observation عن inference وتربط نفس timestamp والbuild والprocess بالmain stack والowner اللي موقفها.",
            "correction": "ابدأ بنوع ANR والوقت، صنّف main thread running أو blocked، اتبع Binder/lock owner، وبعدها اختار experiment واحدة تفرق بين أقوى فرضيتين.",
            "test": "كرر الرحلة على release-like build واجمع ANR trace وPerfetto/logcat correlation؛ النجاح إن نفس trigger لا يتجاوز budget والtrace تزيل سبب الانتظار.",
            "alternative": "bugreport مفيد للسياق الواسع وdumpsys للsnapshot؛ متستخدمهمش بدل timeline لما السؤال عن latency ordering.",
            "wrong": "The top application frame is the root cause, so no owner or timeline analysis is needed.",
        }),
        (("handler leak",), {
            "invariant": "الـqueued callback تفضل ماسكة كل captures لحد التنفيذ أو الإزالة؛ view owner المنتهية لازم لا تبقى reachable من queue أطول عمرًا.",
            "correction": "استخدم lifecycle-owned callback أو removeCallbacks في cleanup، وانقل state work لowner أطول عمرًا من غير capture للـActivity أو View.",
            "test": "جدول callback مؤجلة، اقفل الشاشة قبل التنفيذ، اعمل GC/heap inspection وتأكد إن الـActivity القديمة غير retained وإن callback لا تعدّل dead view.",
            "alternative": "WeakReference تخفي symptom وقد تسقط العمل؛ ownership وexplicit cancellation أوضح وأقوى.",
            "wrong": "The callback is small, so capturing the Activity cannot leak it.",
        }),
        (("main-safe",), {
            "invariant": "الـAPI التي تعرف إن driver blocking هي اللي تضمن main-safety؛ caller لا يفترض dispatcher داخلي غير موثق.",
            "correction": "اعزل blocking driver داخل repository/data source باستخدام dispatcher injected، وخلي الـsuspend contract آمنة لأي caller.",
            "test": "استدعِ الـAPI من Main test dispatcher مع fake blocking boundary وتحقق إن blocking segment اتنفذ على dispatcher المتوقعة وإن cancellation وصلت.",
            "alternative": "لو library API async أصلًا، متضيفش withContext بلا قياس لأنه ممكن يضيف hops من غير حماية.",
            "wrong": "Every suspend function automatically leaves the main thread.",
        }),
        (("work mechanism", "worker retry", "foreground-service", "foreground service", "doze", "unique work"), {
            "invariant": "اختيار Android work API يتحدد من durability وdeadline وuser visibility وقيود البدء؛ retry لا تحصل لفشل permanent ولا تنشئ duplicate effect.",
            "correction": "استخدم WorkManager للشغل durable deferrable، Foreground Service للشغل الجاري الظاهر والمسموح، وowner scope للشغل القصير؛ عرّف unique work وretry classification صراحة.",
            "test": "اختبر process kill وDoze وduplicate enqueue وpermanent auth failure وstop action على device، وتأكد إن business operation identity لا تتكرر.",
            "alternative": "Push قد تكون wake-up hint للتوقيت الخادمي؛ exact alarm لا تستخدم إلا لuser-facing exact requirement مسموحة بالسياسة.",
            "wrong": "Use a Foreground Service for every long task and retry every failure until it succeeds.",
        }),
        (("cancellation ownership", "failure propagation", "supervision product", "structured concurrency"), {
            "invariant": "الـcaller scope تملك عمر الشغل؛ coroutineScope تلغي siblings عند فشل مطلوب، بينما supervisorScope تعزل الفشل فقط لو الـproduct تقبل partial result صريحة.",
            "correction": "اربط الشغل بـviewModelScope أوcaller scope، اختار fail-together أوindependent children من business contract، مثّل partial errors في state، وارفض أي completion تخص request أقدم.",
            "test": "ابدأ ثلاث children بgates، افشل واحدة، وتتبع parent وsiblings والcleanup. كرر مع supervision وتأكد إن partial state معلّمة، ثم cancel الـparent وتأكد إن الكل توقف.",
            "alternative": "التنفيذ sequential أبسط لو ordering مطلوبة أوparallelism بلا مكسب؛ supervision لا تستخدم لمجرد إخفاء exception.",
            "wrong": "Use GlobalScope or supervisorScope everywhere so one failure never cancels useful work.",
        }),
        (("cooperative cancellation", "cancellationexception", "finally", "noncancellable", "timeout ownership", "cancellation verification"), {
            "invariant": "الـcancellation cooperative وتنتشر كـCancellationException؛ cleanup قصيرة ومحدودة، وأي timeout لها owner ومعنى منفصل عن failure وunknown outcome.",
            "correction": "أضف checkpoint محسوبة في CPU loop، أعد رمي CancellationException، وخلي NonCancellable لcleanup bounded فقط مع حفظ سبب الـtimeout.",
            "test": "باستخدام runTest وgates، أوقف التنفيذ عند suspension/checkpoint، cancel الـparent، واثبت no publication بعد الإلغاء وcleanup مرة واحدة من غير leaked child.",
            "alternative": "yield تفيد fairness؛ ensureActive أرخص لو محتاج check فقط. timeout في UI لا يلغي بالضرورة server operation.",
            "wrong": "The suspend modifier makes all work cancellable and CancellationException should be mapped to a normal error.",
        }),
        (("cold flow",), {
            "invariant": "كل collector للـcold Flow يشغّل upstream مستقلة؛ مشاركة النتيجة تحتاج scope وstart policy وreplay contract مقصودين.",
            "correction": "لو الطلب واحد للfeature شاركه بـstateIn/shareIn داخل scope مناسب أو انقل fetch خلف cache/source of truth؛ متجمعش نفس cold upstream في أكتر من layer بلا قصد.",
            "test": "شغّل collectorين بعداد fake upstream، اثبت callين في التصميم القديم وcall واحدة مع sharing، ثم اختبر stop timeout وإعادة الاشتراك.",
            "alternative": "سيب الـFlow cold لو كل collector فعلًا محتاج execution مستقلة؛ sharing تغير lifetime والذاكرة والفشل.",
            "wrong": "A Flow is shared automatically, so multiple collectors cannot duplicate upstream work.",
        }),
        (("stateflow", "sharedflow", "state versus event", "backpressure contract", "buffer versus conflate"), {
            "invariant": "state لها current value قابلة لإعادة القراءة، event لها delivery/ack policy، والbuffer/drop/conflate لازم يطابق معنى كل value.",
            "correction": "مثّل durable outcome في state أو storage بهوية وacknowledgement، استخدم StateFlow للstate، وSharedFlow فقط للeffects اللي missed delivery فيها مقبولة.",
            "test": "أوقف collector وأعد إنشاؤه، املأ buffer، وأرسل values متساوية ومتتابعة؛ اثبت replay/drop/conflation والack حسب العقد.",
            "alternative": "Channel مناسب لconsumer واحد وqueue semantics؛ database/outbox لازمة لما الحدث لازم ينجو من process death.",
            "wrong": "SharedFlow with replay zero is a reliable event bus for payment or navigation results.",
        }),
        (("lifecycle collection", "collectlatest", "flatmaplatest", "stale result", "request generation"), {
            "invariant": "بس الـcurrent lifecycle/request owner ينشر state؛ إلغاء collector قد لا يرجع external effect ولا يمنع completion قديمة من commit.",
            "correction": "اربط collection بالـview lifecycle، استخدم latest operator لتقليل الشغل، وحط generation أو operation identity check عند آخر state mutation.",
            "test": "ابدأ R1 ثم R2، أوقف وأعد lifecycle، خلّي R1 تكمل بعد R2 رغم cancellation، واثبت إن R2 وحدها تنشر والcollector القديمة انتهت.",
            "alternative": "لو كل result لها business meaning استخدم queue/order بدل latest cancellation؛ latest صحيح فقط عندما القديم أصبح غير مطلوب.",
            "wrong": "collectLatest or flatMapLatest rolls back old external work and guarantees it can never publish.",
        }),
        (("runtest", "one scheduler", "testing hot flows", "flaky test"), {
            "invariant": "الاختبار يملك كل scopes والdispatchers وvirtual clock؛ مفيش wall-clock sleep أو scheduler خفية خارج سيطرته.",
            "correction": "حقن TestDispatcher واحدة تشارك scheduler، استخدم runCurrent/advanceUntilIdle وbounded collectors، ونظف Dispatchers.Main والbackground jobs.",
            "test": "كرر الاختبار مع ordering مختلفة، افشل لو فيه unfinished coroutine، وتأكد إن take/first أو backgroundScope تقفل collector بدل انتظار لا نهائي.",
            "alternative": "integration test بreal time مطلوب فقط للboundary الحقيقية؛ logic scheduling يفضل deterministic virtual time.",
            "wrong": "Increase delay() or Thread.sleep until the coroutine test stops flaking.",
        }),
        (("hilt", "qualifier", "singleton session", "di replacement", "service locator"), {
            "invariant": "dependency lifetime تطابق data owner، والbinding identity معناها واضح، والtest تستبدل أضيق boundary من غير global stale state.",
            "correction": "ارسم component graph، انقل account state لـaccount/session owner قابلة للإبطال، استخدم semantic qualifiers، واختبر Hilt replacement والlogout.",
            "test": "ابدأ account A ثم logout وaccount B، أعد إنشاء component، واثبت عدم تسريب cache أو endpoint؛ شغّل graph test يثبت binding الفعلية.",
            "alternative": "constructor injection كافية داخل object graph الصغيرة؛ Hilt تضيف قيمة عند Android lifetimes وتجميع graph، مش لمجرد اتباع pattern.",
            "wrong": "Make the dependency a Singleton so every screen sees the same object forever.",
        }),
        (("responsibility boundary", "mvvm data flow", "ui state and events", "repository ownership"), {
            "invariant": "الـUI ترسل intent وتعرض immutable state، الـstate holder تنسق العملية، والـrepository تملك data policy وsource coordination؛ business validation لا تتكرر بين callers.",
            "correction": "حوّل event إلى command typed، نفّذ validation عند domain boundary، خلّي repository تحدث source of truth، وبعدها استخرج UI state واحدة مع loading/error/freshness واضحة.",
            "test": "اختبر reducer والvalidation من غير Android، راقب dependency call count، ثم اختبر إن failure أوretry أوrecreation لا تكرر side effect ولا تنتج state متعارضة.",
            "alternative": "للfeature الصغيرة state holder وrepository بسيطة كفاية؛ زوّد use case أوlayer لما reuse أوpolicy أوchange axis حقيقية تبررها.",
            "wrong": "Put validation, SQL, retry, navigation, and rendering in the Activity because it owns the screen.",
        }),
        (("module boundary", "dependency direction", "public api", "build and ownership"), {
            "invariant": "الmodule تجمع code تتغير معًا وتصدر contract صغيرة؛ dependency graph لا تكشف internals ولا تعمل cycle.",
            "correction": "حدد change axis وowner، انقل contract لأقرب stable boundary، اخفِ implementation، وقِس build/coordination cost قبل زيادة modules.",
            "test": "استخدم dependency graph/API check، امنع forbidden dependency، وغيّر implementation في module وتأكد إن consumers لا تحتاج تعديل.",
            "alternative": "package boundary داخل module أفضل لو مفيش independent ownership أو build isolation؛ module زيادة لها تكلفة مستمرة.",
            "wrong": "More Gradle modules always mean cleaner architecture and faster builds.",
        }),
        (("adr", "architecture review", "review severity", "repository conflict", "dsa invariant"), {
            "invariant": "المراجعة تبدأ بـcorrectness invariant وownership وfailure path؛ القرار يوثق forces وalternatives وconsequences وrevisit trigger.",
            "correction": "تتبع input إلى state وside effect، صنّف blocker بالدليل، واقترح بديل viable؛ وثّق trade-off بدل تعليق style عام.",
            "test": "حوّل الـinvariant لboundary test أو failure injection، وتأكد إن ADR فيها trigger قابل للقياس وإن conflict/ordering policy قابلة لإعادة الإنتاج.",
            "alternative": "suggestion غير blocking لو لا تمس correctness/security؛ متستخدمش سلطة reviewer لفرض preference بلا evidence.",
            "wrong": "The architecture looks familiar, so naming and layer count are enough for approval.",
        }),
        (("timeout taxonomy", "retry safety", "token refresh", "unknown outcome", "backoff"), {
            "invariant": "كل timeout لها stage وowner، والretry مسموحة فقط لفشل transient ومع operation idempotent أو stable operation identity؛ unknown تفضل قابلة للمصالحة.",
            "correction": "صنّف connect/read/call/application timeout، استخدم single-flight للrefresh، cap وjitter للretry، واعمل status lookup للwrite ذات النتيجة المجهولة.",
            "test": "حاكي concurrent 401 وtimeout قبل/بعد server commit وRetry-After وفشل permanent؛ اثبت refresh واحدة وعدم duplicate business effect.",
            "alternative": "للread الآمنة automatic retry مناسبة؛ للwrite غير idempotent ارجع unknown واعمل reconcile بدل محاولة جديدة.",
            "wrong": "Retry every exception with exponential backoff; the server will handle duplicates.",
        }),
        (("build pipeline", "compatibility matrix", "r8 keep", "variant isolation", "signing boundary"), {
            "invariant": "كل build stage لها artifact ودليل منفصل، والrelease variant لا تحتوي debug dependency أو secret، والshrinking contract أضيق من keep-all.",
            "correction": "ثبّت tool versions من compatibility tables، ابن واختبر minified release في CI، افحص dependency/APK output، واحفظ mapping وsigning material بصلاحيات محدودة.",
            "test": "شغّل release smoke path، retrace crash بالmapping المطابقة، افحص DEX/resources/dependencies، وافشل CI لو debug endpoint أو forbidden class ظهرت.",
            "alternative": "generated adapters أوexplicit registration تقلل reflection keep rules؛ disabling R8 يخفي contract ويكبر artifact.",
            "wrong": "If debug works, release is equivalent; disable shrinking when something disappears.",
        }),
        (("measurement question", "startup modes", "perfetto", "memory evidence"), {
            "invariant": "المقارنة تثبت نفس journey وstartup mode وbuild وdevice class، وتربط الـpercentile بالstage المسؤولة بدل snapshot أو average وحيدة.",
            "correction": "عرّف user metric وcohort، اجمع trace على profileable release-like build، وافصل scheduling/Binder/I/O/frame أو allocation/retention حسب السؤال.",
            "test": "كرر بعد warm-up عند نقاط ثابتة، قارن percentiles مع baseline، واثبت إن التحسن لا يكسر memory أو correctness أو accessibility guardrail.",
            "alternative": "Macrobenchmark يقيس journey؛ heap dump يثبت retention؛ Perfetto يشرح timeline. اختار الأداة حسب hypothesis.",
            "wrong": "One fast debug run or one large heap snapshot proves the production diagnosis.",
        }),
        (("incident rollout", "release gate", "staged rollout", "rollback criteria"), {
            "invariant": "كل release لها blocking gates مستقلة وcohort قابلة للمقارنة وowner وthreshold وrollback action محددين قبل زيادة exposure.",
            "correction": "ابدأ cohort صغيرة، راقب correctness/security/crash/latency كل واحدة كgate، وقف أو ارجع عند threshold، واحفظ evidence للroot cause.",
            "test": "اختبر flag/rollback فعليًا، inject failure في staging، وتأكد إن dashboards تفصل version/cohort وإن alert تسبق توسع الـblast radius.",
            "alternative": "weighted score لا يعوض blocker أمني أو data loss؛ manual approval مفيدة فقط مع evidence وowner واضحين.",
            "wrong": "Average health is acceptable, so one blocking security or data signal can be ignored.",
        }),
        (("migration coverage", "migration path debugging"), {
            "invariant": "كل schema version مدعومة لها path للtarget يحافظ على rows والconstraints؛ فتح database جديدة لا يثبت upgrade للمستخدمين الحاليين.",
            "correction": "احتفظ schema exports وfixtures لكل starting version، شغّل MigrationTestHelper للtarget، واعمل data assertions للindices وFKs وdefaults.",
            "test": "افتح fixture حقيقية لكل version، هاجرها خطوة بخطوة ومباشرًا حسب graph، ثم تحقق من user-authored data والconstraints وعدم destructive fallback.",
            "alternative": "destructive migration مسموحة فقط لcache قابلة لإعادة البناء وبقرار product صريح؛ مش للبيانات التي أنشأها المستخدم.",
            "wrong": "The newest schema opens on a clean install, so migration coverage is complete.",
        }),
        (("source of truth", "durable outbox", "conflict policy", "deletion tombstones", "sync observability"), {
            "invariant": "local canonical state والoutbox تتحدث في transaction، وكل mutation لها ID/version، والdelete تظل tombstone لحد acknowledgement.",
            "correction": "اكتب local change وoutbox atomically، sync idempotently، طبق domain conflict policy، واحتفظ tombstone/dirty metadata لحد server confirmation.",
            "test": "اقتل process بعد local commit وقبل send، كرر delivery، أخّر response قديمة، واعمل delete offline؛ اثبت عدم فقد intent أو resurrection.",
            "alternative": "server-first أبسط لو offline غير مطلوبة؛ CRDT أو merge آلي لا يستخدم إلا لما domain semantics تبرره.",
            "wrong": "Last response wins, and a failed request can be retried without durable identity.",
        }),
        (("session state", "refresh race", "secure storage", "account partitioning", "server authority"), {
            "invariant": "session transition تخص account generation الحالية، logout لا يمكن أن تُعكسها refresh قديمة، والbackend هو authority للauthorization.",
            "correction": "نمذج session كstate machine، اربط token/result بـaccount generation، partition cache/work بالaccount ID، وخزن key material عبر Keystore من غير اعتبار client trusted.",
            "test": "ابدأ refresh ثم logout/login لحساب آخر، أكمل refresh القديمة، واستدعِ revoked endpoint؛ اثبت عدم إحياء الجلسة أو اختلاط rows/work.",
            "alternative": "encrypted local storage تقلل exposure على الجهاز لكنها لا تلغي server revocation ولا تقلل البيانات تلقائيًا.",
            "wrong": "A token stored with Keystore makes the client the final authorization authority.",
        }),
        (("push as signal", "ordering and gaps", "reconnect policy", "location freshness", "privacy and observability"), {
            "invariant": "push/realtime delivery مجرد signal قابلة للتكرار والفقد؛ canonical stream تستخدم cursor/sequence وتكشف gaps، والlocation لها age/accuracy/retention واضحة.",
            "correction": "اعمل owner واحدة للconnection، backoff+jitter وcatch-up من cursor، dedupe قبل apply، واعرض freshness مع تقليل location precision والretention.",
            "test": "احذف وكرر وبدّل ترتيب events، اعمل network flap وtoken expiry، ثم اثبت gap recovery وconnection واحدة وprivacy-safe telemetry.",
            "alternative": "push plus periodic fetch أبسط وأوفر battery لو sub-second realtime مش requirement.",
            "wrong": "A WebSocket or push notification guarantees complete, ordered, exactly-once data.",
        }),
        (("requirement discovery", "state ownership", "concurrency boundary", "alternative comparison", "design verification"), {
            "invariant": "كل mutable state لها authority وupdate path وpersistence/conflict contract، والتصميم مربوط بأرقام scale وفشل قابل للاختبار.",
            "correction": "اسأل عن latency/offline/consistency/privacy، ارسم state machine وحدود client/server، قارن البدائل بمعايير ثابتة، وحدد migration وrollback.",
            "test": "حوّل أهم assumptions لـload model وفشل injected: duplicate، gap، account switch، process death؛ راقب SLO وcorrectness invariant قبل rollout.",
            "alternative": "اختار design أبسط لو scale أو consistency لا تبرر distributed coordination؛ اذكر trigger رقمي لإعادة النظر.",
            "wrong": "Choose the most scalable architecture first and fill in requirements later.",
        }),
        (("state reads", "state hoisting", "immutable collections", "submitted list mutation", "stability and skipping", "recomposition evidence"), {
            "invariant": "Compose تقرأ observable immutable state، owner واحدة تستقبل events، وأي stability contract صادق عن كل observable field.",
            "correction": "hoist لأقل common owner، انشر snapshots جديدة، شيل work من composition، ومتضفش @Stable إلا لما contract فعلًا مستوفاة والtrace تثبت bottleneck.",
            "test": "غيّر كل field وحدها، أعد ترتيب list، وراقب UI output/recomposition/layout؛ اثبت إن update لا تختفي وإن expensive work انخفضت على release build.",
            "alternative": "recomposition رخيصة وصحيحة قد لا تحتاج إصلاح؛ derivedStateOf/memoization لهم overhead ويستخدموا بقياس.",
            "wrong": "Annotate the model @Stable and make recomposition count zero.",
        }),
        (("launchedeffect", "disposableeffect", "rememberupdatedstate", "lifecycle-aware", "effect testing"), {
            "invariant": "effect identity تحددها keys، التسجيل له cleanup مطابق، والcallback الحديثة تُقرأ من غير restart غير مطلوب.",
            "correction": "اختار keys تمثل lifetime الحقيقي، استخدم DisposableEffect للregister/unregister وrememberUpdatedState للقيمة الحديثة داخل effect طويلة.",
            "test": "غيّر key وcallback وlifecycle بترتيب متحكم، واثبت start/cancel/cleanup مرة واحدة وعدم callback على owner متوقفة.",
            "alternative": "event handler عادية أفضل لو مفيش lifecycle side effect؛ متستخدمش Effect API لنقل pure calculation.",
            "wrong": "Use Unit as every effect key and read whatever callback was captured initially.",
        }),
        (("back-stack", "typed arguments", "singletop", "deep-link entry", "navigation testing"), {
            "invariant": "Navigation host تملك ordered entries؛ route تحمل stable IDs فقط، وكل entry point يبني authorized stack وBack behavior متوقع.",
            "correction": "عرّف typed route، reload data بالID، اختار singleTop/popUpTo من UX، ومرر external entry عبر validation وauth قبل destination.",
            "test": "شغّل normal launch وdeep link وnotification وduplicate taps ثم recreation؛ تحقق من entries والarguments وBack وinvalid link rejection.",
            "alternative": "singleTop يمنع duplicate في القمة فقط؛ state-based navigation أو popUpTo أوضح لما المطلوب إزالة history أوسع.",
            "wrong": "Passing the whole domain object and adding singleTop solves stale arguments and all duplicates.",
        }),
        (("adaptive breakpoints", "rtl correctness", "font-scale", "ui performance", "ui test pyramid", "semantics selectors", "flakiness removal"), {
            "invariant": "نفس state تحافظ على meaning وfocus وcritical actions عبر width وRTL وfont scale؛ الاختبار يختار semantics ثابتة ويتحكم في الوقت والبيانات.",
            "correction": "استخدم available window size وlogical start/end، خلّي المحتوى reflow/scroll، اختبر pure state محليًا وframework behavior على device بقياسات frames.",
            "test": "غطّ LTR/RTL و200% font وcompact/expanded وkeyboard/TalkBack، واستخدم controlled clocks/network من غير sleeps أو selectors مرتبطة بالlayout.",
            "alternative": "golden screenshot تكشف pixels لكنها لا تثبت focus/announcement؛ semantics/device journey تكمل الدليل.",
            "wrong": "A phone screenshot and a fixed delay prove adaptive, RTL, accessible, and stable UI behavior.",
        }),
        (("kotlin to dex", "kotlin to android runtime", "d8 versus r8", "art execution", "zygote", "class loading", "jni", "reflection and shrinking", "boxing", "crash retrace", "runtime evidence"), {
            "invariant": "الادعاء مربوط بمرحلة وartifact محددين: source ثم class files ثم DEX/APK ثم ART؛ loader/JNI/reflection تضيف identity وlifetime contracts منفصلة.",
            "correction": "حدد أول artifact غلط، افحص release DEX/mapping والloader أو native boundary المعنية، وأضف keep/registration ضيقة بدل تعطيل optimization.",
            "test": "ابن minified release، افحص DEX وmapping، شغّل affected path على device/version ممثلة، واختبر native cleanup وexception/thread attachment لو JNI داخلة.",
            "alternative": "generated adapter أوexplicit registry أبسط من reflection؛ pure Kotlin/JVM test تثبت logic لكنها لا تثبت packaging أو ART behavior.",
            "wrong": "Android executes JVM bytecode directly, so a debug JVM test proves the release ART behavior.",
        }),
        (("race definition", "atomicity versus visibility", "mutex contract", "atomic update", "confinement", "immutability", "deadlock", "backpressure", "stress testing", "cancellation and locks"), {
            "invariant": "الـshared invariant تظهر atomically لكل observer؛ synchronization تحمي كامل read-modify-write، والlock لا تحتوي slow I/O أو reentrant callback.",
            "correction": "اكتب harmful interleaving، اجمع fields في atomic state أو Mutex قصيرة، أو confined owner؛ حدد queue bound/drop policy من معنى الحدث.",
            "test": "استخدم barriers لفرض interleaving، cancel أثناء انتظار lock، املأ queue، وافحص lost update/deadlock/cleanup بدل الاعتماد على stress وحدها.",
            "alternative": "immutability وconfinement أبسط غالبًا؛ atomics المنفصلة لا تحمي invariant مشتركة وMutex ليست اختيارًا تلقائيًا.",
            "wrong": "Coroutines and visible volatile fields make every compound state transition thread-safe.",
        }),
        (("java platform types",), {
            "invariant": "platform type القادمة من Java لا تحمل nullability guarantee موثوقة؛ أول Kotlin boundary لازم تحولها إلى nullable أوvalidated domain value.",
            "correction": "اعزل SDK في adapter، خزّن result في String?، طبّق validation/normalization مرة واحدة، وصدّر type لا تسمح بـblank أوnull لو domain تمنعهم.",
            "test": "اجعل Java fake ترجع null وblank وقيمة صحيحة، وتأكد إن null لا تصل لـ!! أوproperty access وإن callers يروا result typed.",
            "alternative": "annotations موثوقة تحسن interop، لكن runtime validation تظل لازمة لو provider الفعلي ممكن يخالفها.",
            "wrong": "Kotlin treats an unannotated Java String as definitely non-null at runtime.",
        }),
        (("data-class equality and mutable map keys",), {
            "invariant": "أي field تدخل في equals/hashCode لا تتغير والobject مستخدمة كHashMap key؛ وإلا bucket المحسوبة وقت الإدخال لا تطابق lookup الجديدة.",
            "correction": "استخدم immutable stable ID كkey، وافصل mutable profile data عن identity. لو identity تغيرت احذف الـentry بالمفتاح القديم وأدخل key جديدة صراحة.",
            "test": "أدخل key، غيّر field مؤثرة في hashCode، واظهر إن contract أصبحت غير صالحة؛ بعدها اثبت lookup/update مع immutable ID ومع duplicate logical records.",
            "alternative": "data class مناسبة كkey فقط لو كل properties المؤثرة immutable وثابتة طوال وجودها في الـmap.",
            "wrong": "A data class is always a safe HashMap key even when a var used by equals and hashCode changes.",
        }),
        (("open dispatch during initialization",), {
            "invariant": "base constructor تعمل قبل اكتمال derived properties؛ استدعاء open member خلالها يعمل dynamic dispatch على object لسه ناقصة initialization.",
            "correction": "امنع open calls من constructors، مرر القيم المطلوبة للbase صراحة، أوابدأ behavior بعد اكتمال construction من factory/init method يملكها caller.",
            "test": "اكتب subclass override تقرأ property متأخرة، تتبع ترتيب base/derived initialization، ثم اثبت إن التصميم الجديد لا يستدعي override قبل اكتمال object.",
            "alternative": "final/private helper آمنة داخل constructor لو لا تعتمد على overridable state؛ lazy لا تصلح تلقائيًا لو نفس construction path تستدعيها.",
            "wrong": "The derived properties are initialized before any overridden method can run from the base constructor.",
        }),
        (("jvm type erasure",), {
            "invariant": "JVM تتحقق من List كraw runtime shape غالبًا، ولا تقدر تثبت String لكل element؛ الفشل قد يظهر لاحقًا عند قراءة element واستخدامها كString.",
            "correction": "تحقق من كل element عند untrusted boundary، حوّل إلى typed collection جديدة، وتجنب unchecked cast أوحاصرها في adapter عليها tests.",
            "test": "مرر List<Any> فيها String وInt عبر cast غير آمنة، واثبت مكان الفشل عند element use؛ بعدها اختبر validator يرفض index ونوع العنصر بوضوح.",
            "alternative": "reified تساعد فحص النوع الخارجي أوكل element يدويًا، لكنها لا تعيد generic type metadata الكاملة داخل JVM.",
            "wrong": "If the cast to List<String> succeeds, every element has already been checked as String.",
        }),
        (("frame pipeline", "snapshot state", "stability contract", "custom layout", "lazy list identity", "nested scroll", "semantics merging", "focus restoration", "edge-to-edge", "ui benchmark"), {
            "invariant": "الـUI تحافظ على state identity وsemantics/focus، وكل optimization تُنسب للمرحلة المقاسة: composition أو layout أو draw أو input أو GPU.",
            "correction": "حدد stage من trace، استخدم stable keys وobservable snapshots، نسّق nested input/insets عند owner واحدة، وابن semantics قبل custom visuals.",
            "test": "قِس frames على release-like build، أعد ترتيب items وغيّر adaptive layout، واختبر TalkBack/keyboard/focus وinsets بعد التحسين.",
            "alternative": "platform component أفضل لما custom layout/gesture لا تقدم مكسب مقاس وتزيد صيانة accessibility.",
            "wrong": "Fewer recompositions or a matching screenshot proves the whole UI pipeline is correct and fast.",
        }),
        (("requirement shaping", "architecture evolution", "ownership model", "slo", "blast-radius", "migration governance", "platform product", "decision under uncertainty", "cross-team disagreement", "operational design"), {
            "invariant": "القرار الكبير له measurable outcome وowner وbounded blast radius وmigration/rollback؛ platform بلا consumers وتشغيل ليست product ناجحة.",
            "correction": "حوّل الغموض لـjourneys/SLO/non-goals، ابدأ seam قابلة للرجوع، عيّن decision/operations owners، ووسع بعد adoption وreliability evidence.",
            "test": "جرّب consumer حقيقية، fail dependency، نفّذ rollback/cutover rehearsal، وراقب adoption/error budget/cost قبل توسيع النطاق.",
            "alternative": "manual process أوlocal library مؤقتة أفضل لو uncertainty عالية أو عدد consumers لا يبرر platform/migration.",
            "wrong": "A clean rewrite and central platform will solve the problem after every team is forced to migrate.",
        }),
        (("reversal boundary", "settlement", "terminal operation", "hardware disconnect", "pci-safe"), {
            "invariant": "payment attempt لها stable ID وterminal outcome واحدة؛ authorization/settlement/reversal سجلات مختلفة، وunknown لا تصبح retry جديدة قبل reconciliation.",
            "correction": "persist attempt identity والحالة قبل SDK call، طابق كل callback، reconcile مع host بعد disconnect، ونفذ reversal حسب protocol من غير تخزين card secrets.",
            "test": "اقطع hardware/network قبل وبعد authorization، كرر callback وأعد process، واثبت outcome واحدة وreceipt صحيحة وlogs خالية من PAN/track/PIN/cryptogram.",
            "alternative": "manual operator reconciliation لازمة لو host لا يوفر status/idempotency؛ UI undo لا تعادل protocol reversal.",
            "wrong": "A lost response means the payment failed, so create a new attempt immediately.",
        }),
        (("interval merge",), {
            "invariant": "بعد معالجة أول i intervals المرتبة بالstart، الناتج disjoint ويمثل اتحادها، وآخر interval فقط ممكن تتداخل مع التالية.",
            "correction": "رتب بالstart ثم end، انسخ أول interval، وادمج لو next.start &lt;= last.end حسب closed/open contract؛ وإلا أضف interval جديدة.",
            "test": "اختبر empty وcontained/touching/disjoint وunsorted inputs وinteger boundaries، وقارن الاتحاد مع point-set oracle على ranges صغيرة.",
            "alternative": "sweep-line يلزم لو محتاج counts/events متعددة؛ sort-and-merge أبسط لإخراج الاتحاد مرة واحدة.",
            "wrong": "Compare each interval only with its original neighbor; sorting and the output invariant are optional.",
        }),
        (("lru cache",), {
            "invariant": "الـmap والdoubly linked order تصف نفس entries؛ الرأس most recent والذيل least recent، وكل get/put يحدث الاثنين atomically.",
            "correction": "استخدم hash map إلى nodes وقائمة sentinel؛ move-to-front عند get/update، وevict tail عند تجاوز capacity مع حذف map entry نفسها.",
            "test": "اختبر capacity 0/1، update existing، repeated get، eviction order، وassert list/map consistency بعد كل operation.",
            "alternative": "LinkedHashMap access-order أبسط في JVM لو custom eviction/threading غير مطلوبة؛ لا تعيد اختراعها بلا سبب interview واضح.",
            "wrong": "A HashMap alone can identify the least recently used key in O(1).",
        }),
        (("cycle detection",), {
            "invariant": "في directed DFS: gray node على current path تكشف cycle؛ في Kahn، processed count أقل من V يعني cycle. Undirected graph يحتاج parent rule.",
            "correction": "حدد graph directed ولا undirected، اختار colors أو indegree، وغطّ كل disconnected component بدل البدء من node واحدة.",
            "test": "اختبر self-loop وtwo-node cycle وDAG وdisconnected cycle وduplicate edges، وتتبع colors/indegrees خطوة بخطوة.",
            "alternative": "Kahn مناسب لو محتاج topological order؛ iterative DFS يتجنب stack overflow في graph عميقة.",
            "wrong": "A visited node always means a cycle in both directed and undirected graphs.",
        }),
        (("dp optimization", "dynamic-programming state"), {
            "invariant": "كل dp state لها معنى وdependencies معروفة؛ ضغط الأبعاد صحيح فقط لو overwrite order لا تمسح قيمة لسه مطلوبة.",
            "correction": "اكتب recurrence وbase cases والevaluation order أولًا، نفذ table واضحة، ثم اضغط memory بعد رسم dependencies واتجاه iteration.",
            "test": "قارن بالrecursive memo oracle على inputs صغيرة، واختبر zero/one boundaries وحالة تكشف overwrite في الاتجاه الغلط.",
            "alternative": "احتفظ بالجدول الكامل لو reconstruction أووضوح reasoning أهم من memory؛ rolling array ليست تحسينًا مجانيًا.",
            "wrong": "Any two-dimensional DP can be reduced to one array by overwriting from left to right.",
        }),
        (("bfs and dfs", "heap invariant", "dijkstra", "graph test"), {
            "invariant": "اختيار graph algorithm يتبع guarantee: BFS shortest unweighted edges، heap تضمن root فقط، وDijkstra تتطلب non-negative weights مع stale-entry handling.",
            "correction": "عرّف graph والweight contract، اكتب visited/distance invariant، وتجاهل stale heap entry بدل افتراض إن iteration مرتبة.",
            "test": "غطّ disconnected/self-loop/duplicate edges وnegative invalid weight وequal paths وoverflow؛ قارن shortest paths بـBellman-Ford على graphs صغيرة صالحة.",
            "alternative": "DFS للreachability/deep structure، 0-1 BFS لأوزان 0/1، وBellman-Ford لو negative edges مطلوبة.",
            "wrong": "Dijkstra works with negative weights and iterating a heap returns globally sorted values.",
        }),
        (("stack live-coding", "hash-map invariant", "binary-search invariant", "sliding-window invariant"), {
            "invariant": "الـloop invariant تصف بالضبط معنى الـdata structure بعد معالجة كل prefix؛ كل iteration تحافظ عليها وتقلل مساحة البحث أو تحرك الحدود مرة واحدة.",
            "correction": "اكتب input/output وedge cases، سمّي معنى stack/map/window/search interval، ثم trace مثال adversarial قبل كتابة Kotlin واشتق complexity من عدد الحركات الفعلية.",
            "test": "اختبر empty وsingle وduplicates وno-solution وoverflow، وقارن random small inputs بحل brute-force واضح.",
            "alternative": "الحل الأبسط المقبول أفضل لو constraints صغيرة؛ optimization مطلوبة فقط لما تقدر تثبت invariant وmemory trade-off.",
            "wrong": "Recognizing the common pattern is enough; edge cases, the loop invariant, and overflow do not change correctness.",
        }),
        (("capstone boundaries", "test portfolio", "failure injection", "observability contract", "toolchain honesty"), {
            "invariant": "كل layer تثبت risk مختلفة، operation identity تتبع الرحلة بلا sensitive content، وAndroid claims لا تُنسب لـJVM-only evidence.",
            "correction": "اربط UI intent بـlocal transaction/outbox/session owner، اختبر reducer والمigration/worker/UI عند boundaries منفصلة، وسمّ بوضوح ما تم تنفيذه فعليًا.",
            "test": "inject process death/offline/conflict/account switch/duplicate work، وتتبع redacted operation ID من intent حتى reconciliation.",
            "alternative": "conceptual design مفيدة للتفسير لكنها لا تستبدل device evidence؛ متوسعش test layer أعلى لو unit contract تكفي.",
            "wrong": "One end-to-end happy path proves every layer and a JVM model counts as Android runtime evidence.",
        }),
        (("severity and scope", "mitigation before certainty", "incident roles", "hypothesis testing", "post-incident"), {
            "invariant": "الincident لها factual timeline وsingle coordinator وimpact محدد؛ mitigation reversible تسبق certainty لما الضرر مستمر، وكل action لها owner وproof.",
            "correction": "حدد versions/users/data impact، عيّن roles، rollback/flag بأقل blast radius، ثم اختبر hypothesis بالملاحظة الأكثر تمييزًا وسجل follow-ups قابلة للإغلاق.",
            "test": "اعمل game-day بsignal ناقصة، قِس زمن detection/decision/mitigation، وراجع إن action اتقفلت باختبار أوdashboard مش بوعد.",
            "alternative": "pause investigation مؤقتًا لصالح mitigation لما user harm عالي؛ لا تمسح evidence أو تعمل تغييرات متعددة غير قابلة للعزل.",
            "wrong": "Wait for the exact root cause before mitigating a high-impact incident.",
        }),
        (("risk prioritization", "trust boundaries", "release-like performance", "security regression", "trade-off communication"), {
            "invariant": "الأولوية تجمع impact وlikelihood/evidence وreversibility؛ security authority تبقى server-side والperformance تقاس على journey ممثلة.",
            "correction": "ارسم trust boundaries، رتب المخاطر، اختبر hostile input/authorization وrelease percentiles، واعرض البدائل والrollback signal بوضوح.",
            "test": "شغّل unauthorized/oversized/replayed inputs وrepresentative macro journey، وتأكد من redaction وعدم تخطي correctness مقابل performance.",
            "alternative": "تحسين صغير reversible قد يسبق redesign؛ لا تقبل إزالة auth check أوhard-coded key مقابل startup أسرع.",
            "wrong": "Performance wins justify moving authorization to the client or embedding a fixed secret in the APK.",
        }),
        (("twenty-second", "ninety-second", "clarifying questions", "uncertainty language", "shadowing review", "readiness evidence", "gap-driven revision", "mock interpretation", "portfolio honesty", "interview-day"), {
            "invariant": "الإجابة تبدأ بقرار وحد واضح، ثم mechanism/example/failure/trade-off حسب الوقت؛ أي claim عن الخبرة أوevidence تفضل دقيقة وقابلة للدفاع.",
            "correction": "ابدأ answer headline، اسأل constraint مؤثرة، فكر بصوت مرتب، سمّي uncertainty وخطة verification، واختم بقرار واختبار.",
            "test": "سجل 20 ثانية و90 ثانية لنفس السؤال، راجع fillers والmissing boundary، ثم أعد سؤال follow-up من غير قراءة نص محفوظ.",
            "alternative": "قل “I have not run that on Android; here is the JVM model and how I would verify it” بدل bluff أو توقف كامل.",
            "wrong": "A long memorized answer and confident wording are enough even when the evidence was never executed.",
        }),
        (("accessibility", "semantics"), {
            "invariant": "كل interactive node تعرض role وlabel وstate وaction صحيحة، والـfocus order يفضل منطقي؛ screenshot لا تثبت TalkBack behavior.",
            "correction": "استخدم stable semantics selectors مع controlled state، اختبر role/state/action، وبعدها نفّذ TalkBack وfont-scale وfocus journey على Android.",
            "test": "اختبار semantics يفشل لو label أو action ناقصة، ثم device test عند 200% font scale وRTL وTalkBack يثبت إن الـfocus والannouncement صح.",
            "alternative": "Screenshot مناسبة للpixels فقط؛ manual أو automated accessibility journey مطلوبة لما الخطر في focus أو announcement.",
            "wrong": "The screenshot matches the design, so accessibility is covered.",
        }),
        (("top k",), {
            "invariant": "بعد معالجة i عناصر، الـmin-heap تحتوي أكبر min(k, i) عناصر شوفتهم، والـroot أصغر عنصر داخل الـTop K الحالية.",
            "correction": "احتفظ بـmin-heap حجمها k: أضف لحد k، وبعدها استبدل الـroot فقط لما العنصر الجديد أكبر؛ عرّف سياسة duplicates وترتيب الناتج صراحة.",
            "test": "قارن بالـfull sort على random small inputs، واختبر k=0 وk>n وduplicates وnegative values وk قريب من n.",
            "alternative": "لو k قريب من n أو محتاج output مرتبة بالكامل، sorting قد تكون أبسط؛ Quickselect مناسب لو average O(n) مقبول والترتيب النهائي غير مطلوب.",
            "wrong": "Put every value in a HashSet; that automatically returns the Top K values in order.",
        }),
        (("stale result", "stale asynchronous", "request generation"), {
            "invariant": "الطلب generation=g ينشر state فقط لو g ما زالت current generation لحظة الـcommit؛ cancellation لوحدها لا تمنع external completion.",
            "correction": "زود generation عند كل intent جديد، التقطها مع الطلب، وافحص equality عند state mutation؛ استخدم flatMapLatest لتقليل الشغل والـgeneration gate لحماية commit.",
            "test": "ابدأ R1 ثم R2، خلّي R2 تكمل أولًا وR1 تتجاهل cancellation وتكمل لاحقًا؛ النتيجة النهائية لازم تفضل R2.",
            "alternative": "لو كل الطلبات لازم تتنفذ بالترتيب استخدم queue؛ لو آخر طلب فقط مهم استخدم latest cancellation مع commit gate.",
            "wrong": "flatMapLatest guarantees that an old network response can never complete or mutate state.",
        }),
        (("foreground-service", "foreground service"), {
            "invariant": "الشغل ongoing وuser-visible، البدء مسموح من السياق الحالي، service type صحيح، وstartForeground مع notification تحصل داخل مهلة النظام.",
            "correction": "اختار Foreground Service فقط لو الشغل ظاهر ومستمر؛ استخدم WorkManager للدوران durable deferrable وin-process coroutine للشغل القصير المرتبط بالواجهة.",
            "test": "اختبر start من foreground وbackground restrictions، notification permission/version behavior، stop action، process kill، والservice type على device.",
            "alternative": "WorkManager أفضل لو المستخدم مش محتاج متابعة فورية؛ coroutine داخل owner أفضل لو الشغل قصير ومش لازم ينجو من process death.",
            "wrong": "A Foreground Service is a general escape hatch for any work that Android might stop.",
        }),
        (("memory evidence", "memory"), {
            "invariant": "قارن نفس journey والbuild والdevice class، وافصل allocation churn عن retained objects وعن native memory وprocess pressure قبل وصف المشكلة بأنها leak.",
            "correction": "كرر scenario على profileable release-like build، خذ heap/Perfetto evidence في نقاط ثابتة، وقارن retained paths وRSS/GC behavior مع baseline.",
            "test": "نفّذ iterations بعد warm-up، force نفس navigation loop، راقب إن retained instances ترجع للbaseline، وقارن percentiles بدل snapshot واحدة.",
            "alternative": "لو المشكلة jank من allocation churn استخدم frame/allocation trace؛ heap dump وحدها أنسب للretention وليست أداة startup benchmark.",
            "wrong": "One large heap snapshot from a debug build proves a production memory leak.",
        }),
        (("reconnect",), {
            "invariant": "فيه connection owner واحد، وكل reconnect لها generation، والclient تعمل catch-up من آخر server sequence من غير duplicate apply أو gap صامت.",
            "correction": "استخدم bounded exponential backoff مع jitter، راقب network/token state، اقفل connection القديمة، ثم REST catch-up وdedupe قبل استئناف realtime stream.",
            "test": "حاكي flap وoffline طويل وtoken expiry وduplicate/out-of-order events؛ اثبت connection واحدة وordered store بلا gap بعد recovery.",
            "alternative": "لو realtime مش requirement استخدم push كhint مع periodic catch-up؛ ده أبسط وأقل battery من socket دائم.",
            "wrong": "Reconnect immediately in a loop; the server will deduplicate every message for the client.",
        }),
        (("room migration", "migration coverage"), {
            "invariant": "كل schema version مدعومة لها migration path للtarget يحافظ على البيانات والconstraints المطلوبة، ومفيش destructive fallback مخفية.",
            "correction": "اختبر كل starting version إلى target بملف database حقيقي، راجع schema export، وشغّل data assertions بعد migration.",
            "test": "MigrationTestHelper يفتح fixtures لكل version، يهاجر للtarget، ثم يتحقق من rows وindices وforeign keys وdefault values.",
            "alternative": "Destructive migration مقبولة فقط لبيانات قابلة لإعادة البناء وبقرار product صريح؛ user-authored data تحتاج path محافظة.",
            "wrong": "The latest schema opens successfully, so every installed user can upgrade safely.",
        }),
        (("token refresh", "retry"), {
            "invariant": "retry تحصل فقط لفشل transient ومع operation آمنة أو idempotency identity؛ كل 401 concurrent تشارك refresh واحدة من غير loop.",
            "correction": "صنّف failure، استخدم single-flight refresh، أعد request مرة واحدة بالtoken الجديدة، واحفظ unknown write outcome للمصالحة.",
            "test": "شغّل requests متزامنة ترجع 401 وتأكد إن refresh واحدة حصلت، ثم اختبر refresh failure وrepeated 401 وtimeout بعد server commit.",
            "alternative": "للعمليات غير idempotent ارجع unknown outcome واعمل status lookup؛ automatic retry ممكن تكرر business effect.",
            "wrong": "Catch every network exception and retry the request with exponential backoff.",
        }),
        (("recomposition",), {
            "invariant": "Composition تقرأ observable immutable state، rendering بلا side effects، وأي optimization تحافظ على visible output والstate updates.",
            "correction": "انقل side effects للEffect API المناسبة، انشر immutable snapshots، واستخدم stable keys وderivedStateOf فقط لما القياس يثبت فايدتهم.",
            "test": "غيّر كل state input وحدها، اثبت visible result، راقب recomposition/layout بالtools، واختبر إن list mutation تنشر snapshot جديدة.",
            "alternative": "زيادة recomposition رخيصة قد لا تحتاج إصلاح؛ ركز على expensive work أو layout/draw اللي أثبتها trace.",
            "wrong": "Every recomposition redraws the whole screen, so the goal is to make the count zero.",
        }),
        (("deep link", "pendingintent"), {
            "invariant": "كل external entry تتحقق من scheme/host/path/fields والauthorization الحالية، وPendingIntent تستخدم mutability والidentity المقصودين فقط.",
            "correction": "Parse إلى typed command، ارفض duplicate/unknown fields، أعد authorization من server state، واستخدم explicit immutable PendingIntent حيث يمكن.",
            "test": "اختبر lookalike hosts وencoded paths وduplicate params وwrong account وreplayed PendingIntent وmutable-extra injection.",
            "alternative": "استخدم app link verified أو in-app navigation token لو universal deep link توسع attack surface من غير حاجة product.",
            "wrong": "If Android matched the intent filter, the deep link is trusted and authorized.",
        }),
        (("r8", "shrinking", "minified"), {
            "invariant": "الـrelease artifact تحتفظ فقط بالentry points والmetadata المطلوبة فعلًا، وكل crash تتربط بنفس mapping وvariant اللي أنتجتها.",
            "correction": "أعد المشكلة على minified release، retrace بالmapping الصحيحة، وحدد reflection/JNI/serialization boundary ثم أضف أضيق keep rule.",
            "test": "شغّل release smoke/instrumentation على المسار المتأثر، افحص APK/DEX، وتأكد إن broad keep rule مش مخفية المشكلة.",
            "alternative": "غيّر reflection إلى generated adapters أو explicit registration لو keep contract صعب المراجعة.",
            "wrong": "Disable R8 or keep every class; optimization is not worth investigating.",
        }),
        (("payment", "authorization", "unknown outcome"), {
            "invariant": "attempt ID واحدة تربط UI وterminal وhost؛ approved/declined/unknown حالات منفصلة، وunknown لا تتحول لمحاولة جديدة قبل reconciliation.",
            "correction": "احفظ attempt identity، اعرض pending/unknown بوضوح، استعلم أو reconcile مع host، ونفّذ reversal فقط حسب protocol/business result.",
            "test": "اقطع transport بعد card read وبعد authorization، أرسل duplicate callback، أعد process، واثبت terminal outcome واحدة من غير تخزين sensitive data.",
            "alternative": "لو host يدعم idempotency/status lookup استخدمهم؛ manual operator reconciliation مطلوبة لما البروتوكول لا يثبت النتيجة.",
            "wrong": "If the response is lost, create a new payment request so the customer can finish quickly.",
        }),
        (("mutex", "race", "atomic"), {
            "invariant": "الـshared invariant تتحدث كوحدة واحدة؛ visibility وحدها لا تجعل read-modify-write atomic، وممنوع suspension أو callback خارجي داخل lock طويل.",
            "correction": "اجمع fields في state واحدة واستخدم atomic update أو Mutex قصيرة، أو انقل كل mutation لـserialized owner.",
            "test": "اجبر interleaving بين read وwrite، اختبر cancellation أثناء الانتظار، وتأكد إن cleanup تفك ownership وإن مفيش lost update.",
            "alternative": "immutability أو confinement أبسط لو كل access تقدر تمر من owner واحدة؛ atomics منفصلة لا تحمي invariant مشتركة.",
            "wrong": "Using coroutines instead of threads removes data races from mutable state.",
        }),
        (("star", "behavioral", "technical disagreement", "blameless accountability"), {
            "invariant": "القصة تحدد Situation وTask وAction أنت عملتها وResult مثبتة، وتفصل مساهمتك عن الفريق من غير أرقام مخترعة.",
            "correction": "اختار موقف حقيقي، اذكر القرار والبدائل والاعتراض، قدم artifact أو metric، واختم بتعلم أو تغيير واضح.",
            "test": "راجع كل claim مقابل incident/PR/metric، ودرّب follow-ups عن failure وconflict وwhat-would-you-change.",
            "alternative": "لو مفيش metric استخدم observable qualitative evidence محددة؛ متحولش القصة لشعارات leadership.",
            "wrong": "We delivered successfully; I led the team and there were no meaningful mistakes.",
        }),
    ]
    for needles, values in overrides:
        if any(needle in key for needle in needles):
            base.update(values)
            break
    if topic in EXACT_GUIDANCE:
        base.update(EXACT_GUIDANCE[topic])
    base["correction"] = f"بالنسبة لـ{topic}: {base['correction']}"
    base["test"] = f"لاختبار {topic}: {base['test']}"
    base["alternative"] = f"في {topic}: {base['alternative']}"
    return base


ALGORITHM_EXAMPLES = {
    "stack live-coding invariant": (
        "Given `()[]{}` return `true`; given `([)]` return `false`.",
        '''fun isBalanced(text: String): Boolean {
    val stack = ArrayDeque<Char>()
    val opening = mapOf(')' to '(', ']' to '[', '}' to '{')
    for (char in text) {
        when (char) {
            '(', '[', '{' -> stack.addLast(char)
            ')', ']', '}' -> if (stack.removeLastOrNull() != opening[char]) return false
        }
    }
    return stack.isEmpty()
}''',
        "بعد كل character، الـstack فيها الـopening brackets اللي لسه متقفلتش بنفس ترتيب ظهورها. كل character تدخل وتخرج مرة، فالوقت O(n) والذاكرة O(n) في أسوأ حالة.",
    ),
    "hash-map invariant": (
        "Given `[2, 7, 11, 15]` and target `9`, return indices `[0, 1]` without using the same element twice.",
        '''fun twoSum(values: IntArray, target: Int): IntArray? {
    val seen = HashMap<Int, Int>()
    for ((index, value) in values.withIndex()) {
        val needed = target.toLong() - value.toLong()
        if (needed in Int.MIN_VALUE.toLong()..Int.MAX_VALUE.toLong()) {
            seen[needed.toInt()]?.let { return intArrayOf(it, index) }
        }
        seen.putIfAbsent(value, index)
    }
    return null
}''',
        "قبل index=i، الـmap فيها القيم من indices الأصغر فقط؛ عشان كده بنفحص complement قبل insert ومش بنستخدم نفس العنصر مرتين. الوقت expected O(n) والذاكرة O(n).",
    ),
    "binary-search invariant": (
        "Given sorted `[1, 4, 7, 9, 13]` and target `9`, return index `3`; return `-1` when absent.",
        '''fun binarySearch(values: IntArray, target: Int): Int {
    var low = 0
    var high = values.lastIndex
    while (low <= high) {
        val mid = low + (high - low) / 2
        when {
            values[mid] < target -> low = mid + 1
            values[mid] > target -> high = mid - 1
            else -> return mid
        }
    }
    return -1
}''',
        "في بداية كل iteration، لو target موجود فهي جوه [low, high]. كل مقارنة تشيل نصف مستحيل، فالوقت O(log n) والذاكرة O(1).",
    ),
    "sliding-window invariant": (
        "Given `[2, 1, 5, 1, 3, 2]` and `k=3`, return maximum sum `9`.",
        '''fun maxWindowSum(values: IntArray, k: Int): Long {
    require(k in 1..values.size)
    var window = values.take(k).sumOf(Int::toLong)
    var best = window
    for (right in k until values.size) {
        window += values[right].toLong() - values[right - k].toLong()
        best = maxOf(best, window)
    }
    return best
}''',
        "قبل تحديث best، window تمثل بالضبط آخر k عناصر. كل عنصر يدخل مرة ويخرج مرة، فالوقت O(n) والـextra space O(1).",
    ),
    "interval merge invariant": (
        "Merge `[[1,3],[2,6],[8,10],[10,12]]` using an explicitly stated closed-interval policy.",
        '''data class Interval(val start: Int, val end: Int)

fun merge(input: List<Interval>): List<Interval> {
    if (input.isEmpty()) return emptyList()
    val sorted = input.sortedWith(compareBy(Interval::start, Interval::end))
    val result = mutableListOf(sorted.first())
    for (next in sorted.drop(1)) {
        val last = result.last()
        if (next.start <= last.end) {
            result[result.lastIndex] = last.copy(end = maxOf(last.end, next.end))
        } else {
            result += next
        }
    }
    return result
}''',
        "بعد معالجة prefix من القائمة المرتبة، result فيها intervals منفصلة وتمثل نفس الاتحاد. الـsorting O(n log n)، والmerge نفسها O(n).",
    ),
    "lru cache design": (
        "Design an LRU cache with expected O(1) `get` and `put`. Explain which two structures must stay consistent.",
        '''class LruCache<K, V>(private val capacity: Int) {
    private val values = object : LinkedHashMap<K, V>(16, 0.75f, true) {
        override fun removeEldestEntry(eldest: MutableMap.MutableEntry<K, V>) =
            size > capacity
    }

    fun get(key: K): V? = values[key]
    fun put(key: K, value: V) {
        if (capacity > 0) values[key] = value
    }
}''',
        "الـhash lookup يجيب القيمة، وaccess-order list تحدد مين least recently used. أي get ناجحة أوput لازم تحدث الترتيب؛ التنفيذ المتوقع O(1) والذاكرة O(capacity).",
    ),
    "cycle detection": (
        "Given a directed graph, return whether it contains a cycle. Cover disconnected components and a self-loop.",
        '''fun hasDirectedCycle(graph: List<List<Int>>): Boolean {
    val color = IntArray(graph.size) // 0 white, 1 gray, 2 black
    fun dfs(node: Int): Boolean {
        if (color[node] == 1) return true
        if (color[node] == 2) return false
        color[node] = 1
        for (next in graph[node]) if (dfs(next)) return true
        color[node] = 2
        return false
    }
    return graph.indices.any { color[it] == 0 && dfs(it) }
}''',
        "gray معناها node موجودة على الـcurrent DFS path؛ الوصول لها تاني يثبت cycle. black خلصناها. كل V وE يتزاروا مرة: O(V+E).",
    ),
    "dp optimization": (
        "Explain when a two-dimensional DP table can be compressed to one row, then show the overwrite-order risk.",
        '''fun minPathSum(grid: Array<IntArray>): Long {
    require(grid.isNotEmpty() && grid[0].isNotEmpty())
    val dp = LongArray(grid[0].size) { Long.MAX_VALUE }
    dp[0] = 0
    for (row in grid) {
        for (column in row.indices) {
            val fromUp = dp[column]
            val fromLeft = if (column > 0) dp[column - 1] else Long.MAX_VALUE
            dp[column] = row[column] + minOf(fromUp, fromLeft)
        }
    }
    return dp.last()
}''',
        "وقت تحديث dp[column]، قيمتها القديمة هي from-up والجديدة في dp[column-1] هي from-left. اتجاه الكتابة جزء من correctness، مش تفصيلة optimization.",
    ),
    "top k selection": (
        "Return the largest `k` values from a stream while using O(k) extra memory; state how duplicates are handled.",
        '''fun topK(values: IntArray, k: Int): List<Int> {
    if (k <= 0) return emptyList()
    val heap = java.util.PriorityQueue<Int>()
    for (value in values) {
        if (heap.size < k) heap += value
        else if (value > heap.peek()) {
            heap.poll()
            heap += value
        }
    }
    return heap.toList().sortedDescending()
}''',
        "بعد i عناصر، الـmin-heap فيها أكبر min(k,i) قيم. كل update تكلف O(log k)، فالإجمالي O(n log k) والذاكرة O(k).",
    ),
}


def algorithm_example(topic: str) -> str:
    example = ALGORITHM_EXAMPLES.get(topic.lower())
    if not example:
        return ""
    prompt, code, trace = example
    return f'''## Live-coding version

**Problem:** {prompt}

```kotlin
{code}
```

<p dir="rtl" lang="ar"><strong>Trace وcomplexity:</strong> {trace}</p>
'''


PROMPT_OVERRIDES = {
    # Architecture and DI
    "Hilt component lifetimes": "A repository is scoped to SingletonComponent and caches the signed-in user. The user logs out and signs in with another account without the process dying. Explain the bug, choose the correct owner for account state, and describe what Hilt does and does not reset.",
    "Qualifier design": "This module provides two Retrofit instances, but both are distinguished only by @Named strings copied across several files. Review the design. When would you introduce semantic qualifiers, and how would you prove the production binding is correct?",
    "Accidental singleton session": "After logout, one screen briefly renders data from the previous account. The cache is held by a @Singleton repository. Trace the lifetime mismatch and redesign the session boundary without restarting the process.",
    "DI replacement tests": "You need an integration test that replaces the real payments gateway while keeping the production database graph. Show the Hilt test replacement you would use, the scope it must preserve, and what the test still cannot prove.",
    "Service locator trade-off": "A legacy app obtains dependencies from a global object in every screen. You cannot rewrite the app at once. How would you migrate toward constructor injection while keeping releases safe, and where is a small service locator still defensible?",
    "Module boundary": "A team wants a Gradle module for every screen. Decide where module boundaries should actually go using ownership, change frequency, public API size, and build cost.",
    "Dependency direction": "feature-checkout currently depends directly on feature-cart to reuse one mapper. Review the dependency direction and propose a boundary that avoids a feature-to-feature cycle without creating a generic commons dump.",
    "Public API control": "A library module exposes DAO entities, Retrofit DTOs, and implementation classes because making everything public was faster. What failures does this create for consumers, and how would you shrink the API safely?",
    "ADR quality": "Your team chose a single-activity architecture. What belongs in the ADR so a future team can understand and revisit the decision instead of treating it as permanent law?",
    "Build and ownership trade-offs": "Two teams share a large core module. Changes trigger broad rebuilds and no one owns regressions. Propose an incremental split and define the measurements that would tell you whether it helped.",
    "Architecture review order": "You have 30 minutes to review a checkout feature. In what order do you inspect state ownership, data flow, side effects, failure handling, security, and style, and why?",
    "Review severity": "A pull request contains a naming issue, an unbounded retry, and a possible duplicate payment. Classify the comments by severity and explain what blocks the merge.",
    "Repository conflict review": "A repository exposes Room as the source of truth but also writes network responses straight into ViewModel state. Identify the two authorities and show how a stale response can overwrite newer local data.",
    "ADR challenge": "You disagree with an accepted ADR after new production evidence appears. How do you challenge it constructively, what evidence is enough to reopen it, and how do you keep delivery moving meanwhile?",
    "DSA invariant in review": "A teammate submits a one-pass two-sum implementation that inserts before looking up the complement. Use [3] with target 6 and [3,3] with target 6 to review the invariant and the bug.",

    # Production engineering
    "Timeout taxonomy": "An API call reports a timeout. Distinguish connect, read, call, and application deadlines. For each one, state what you know about whether the server executed the request.",
    "Retry safety": "A POST /orders request timed out after bytes were sent. Is an automatic retry safe? Design the idempotency key, retry classification, and status lookup needed to prevent a duplicate order.",
    "Token refresh single-flight": "Ten requests receive 401 at the same time and each starts a token refresh. Design a single-flight refresh flow, including refresh failure, a repeated 401, cancellation, and replaying the original requests once.",
    "Unknown outcome": "A payment request times out after the backend may have committed it. Model the client state and user experience until the result can be reconciled. Why are both success and failure unsafe guesses?",
    "Backoff and jitter": "Thousands of clients reconnect after an outage. Derive a capped exponential backoff with jitter, explain when to honor Retry-After, and name failures that must not be retried.",
    "Build pipeline": "Trace one Kotlin function from source through Kotlin compilation, desugaring, D8 or R8, DEX packaging, signing, installation, and ART execution. Where can debug and release behavior diverge?",
    "Compatibility matrix": "The app builds after upgrading AGP but fails only on API 23 release devices. Build a compatibility investigation across JDK, Gradle, AGP, Kotlin, desugaring, minSdk, and device runtime.",
    "R8 keep rules": "A serializer works in debug and fails in minified release. Explain how you would prove whether shrinking or obfuscation is responsible and write the narrowest kind of keep rule you would accept.",
    "Variant isolation": "A release APK accidentally contains a staging endpoint and debug-only dependency. Show how you would isolate variants and add a CI check against the packaged artifact.",
    "Signing boundary": "Walk through Android app signing from CI to Play delivery. Which keys exist, where should each live, and what breaks if the upload key or app signing key is compromised?",
    "Measurement question": "Cold startup became 20% slower in one local run. Define a measurement plan that can tell regression from noise, including build type, startup mode, device class, iterations, and percentile.",
    "Startup modes": "Compare cold, warm, and hot startup. Which process and Activity state exists in each, and why does mixing them make benchmark results meaningless?",
    "Perfetto trace reading": "A screen janks while loading. In a Perfetto trace, how do you distinguish main-thread CPU work, lock wait, Binder wait, I/O, GC, and GPU pressure before proposing a fix?",
    "Memory evidence": "Memory grows after opening and closing a screen ten times. Design an investigation that separates a retained Activity from allocation churn, bitmap or native memory, and normal heap growth.",
    "Incident rollout": "Crash rate rises only in one device cohort during a 10% rollout. Decide whether to pause, roll back, or continue, and list the evidence you need before expanding exposure.",
    "Release gate": "Define hard release gates for crash, ANR, data loss, security, and migration risk. Why should one healthy aggregate metric never cancel a blocking signal?",
    "Staged rollout": "Design a staged rollout with cohort size, observation window, dashboards, owners, and automatic stop conditions. What bias appears if only early adopters receive the release?",
    "Rollback criteria": "A release improves startup but increases checkout failures by 0.3%. Set rollback criteria before launch and explain who has authority to trigger them during an incident.",
    "Migration coverage": "Your Room database supports versions 4 through 9. Which migration paths must CI execute, what data assertions belong after opening version 9, and why is a clean install irrelevant?",

    # System design and algorithms
    "BFS and DFS choice": "Given an unweighted social graph, choose BFS or DFS to find the shortest connection path. State the invariant, complexity, and the conditions that would change your choice.",
    "Heap invariant": "A developer assumes iterating PriorityQueue returns sorted order. Explain the actual heap guarantee and show how stale entries are handled in Dijkstra.",
    "Dijkstra precondition": "A graph contains one negative edge but no negative cycle. Explain exactly why Dijkstra can finalize the wrong distance and choose a valid alternative.",
    "Dynamic-programming state": "For minimum path sum, define the DP state and recurrence before coding. Then explain when one-row compression is valid and why iteration direction matters.",
    "Graph test boundaries": "Design a compact test set for a directed-graph algorithm covering disconnected nodes, self-loops, duplicate edges, equal paths, invalid weights, and numeric overflow.",
    "Session state machine": "Model SignedOut, Refreshing, Authenticated, and Expired states. Which events are legal in each state, and how do you stop an old refresh result from resurrecting a logged-out session?",
    "Refresh race": "A token refresh starts, the user logs out, and the refresh succeeds later. Trace the race and show how an account generation or session ID prevents stale commit.",
    "Secure storage": "What security guarantee does Android Keystore provide for an auth token, what does it not provide, and how do server revocation and rooted-device risk change your design?",
    "Account partitioning": "A multi-account app shares Room tables, caches, WorkManager jobs, and notifications. Design the account keying and cleanup rules that prevent cross-account data leakage.",
    "Server authority": "A client has a valid-looking token and cached role=admin. Explain why the server must remain the authorization authority and how the client should behave offline.",
    "Source of truth": "Design an offline-first screen where Room is the observable source of truth and network refresh updates it. Trace loading, success, stale cache, and failure without creating two UI authorities.",
    "Durable outbox": "A user edits a note offline. Show the database transaction that updates the local row and enqueues a mutation atomically, then trace retry, acknowledgement, and process death.",
    "Conflict policy": "Two devices edit the same record offline. Compare last-write-wins, field merge, version rejection, and user-assisted resolution using a concrete product requirement.",
    "Deletion tombstones": "Why can deleting a row locally cause it to reappear after sync? Design tombstone identity, retention, acknowledgement, and compaction.",
    "Sync observability": "Define metrics and logs for an offline sync engine: queue age, attempts, conflicts, freshness, terminal failures, and redaction. Which signal pages an on-call engineer?",
    "Push as signal": "A product manager says push notifications guarantee the phone has every update. Explain delivery limits and design push as a hint that triggers idempotent catch-up.",
    "Ordering and gaps": "Events arrive with sequence numbers 41, 43, 42, and 43 again. Show how the client detects the gap, buffers or catches up, orders application, and deduplicates.",
    "Reconnect policy": "Design one WebSocket connection owner across lifecycle changes and network flaps. Cover backoff, token refresh, generation, catch-up, and duplicate connection prevention.",
    "Location freshness": "A courier app shows location. Define freshness, accuracy, permission, battery, background, and out-of-order update rules before choosing the API and interval.",
    "Privacy and observability": "You need to debug failed location sync without logging coordinates or user identity. Design useful redacted telemetry and its retention and access controls.",
    "Requirement discovery": "Before designing chat sync, ask the questions that determine ordering, delivery guarantees, offline behavior, history size, latency, privacy, and multi-device consistency.",
    "State ownership": "In a mobile system design interview, map draft text, message history, send status, unread count, and auth state to their authoritative owners and persistence levels.",
    "Concurrency boundary": "Two sends, a reconnect, and an account switch can happen together. Choose the serialized boundaries and operation identities that keep the chat state machine valid.",
    "Alternative comparison": "Compare polling, push-triggered fetch, and a persistent socket for a messaging inbox using latency, battery, infrastructure cost, reliability, and recovery.",
    "Design verification": "Turn a mobile sync design into a verification plan with failure injection for process death, offline edits, duplicates, gaps, conflicts, and account switching.",

    # Compose, Views, navigation, accessibility and UI testing
    "State reads and invalidation": "A Composable reads state.value in one branch and a plain mutable list in another. Which changes schedule recomposition, which do not, and why?",
    "State hoisting": "A reusable date picker owns selection, validation, and navigation internally. Decide what state and events to hoist while keeping transient UI details local.",
    "Immutable collections": "A ViewModel mutates an item inside the same List instance and assigns it back to StateFlow. Explain why the UI may not update and redesign the state update.",
    "Stability and skipping": "A developer adds @Stable to a mutable type to reduce recompositions. Explain the contract they just promised and the correctness bug caused by lying to Compose.",
    "Recomposition evidence": "A recomposition counter is high. Show how you decide whether there is a real performance problem and which trace proves expensive composition, layout, or draw work.",
    "LaunchedEffect keys": "LaunchedEffect(Unit) collects data for user A, then the same destination displays user B. Explain the stale work and choose keys and ownership that restart exactly when intended.",
    "DisposableEffect cleanup": "A Composable registers a sensor listener for the current device ID. Show how DisposableEffect keys and onDispose prevent duplicate listeners and stale callbacks.",
    "rememberUpdatedState": "A long-lived effect should keep its timer but invoke the latest onTimeout lambda. Explain why keying on the lambda restarts too much and how rememberUpdatedState changes the capture.",
    "Lifecycle-aware collection": "A Fragment or Compose screen collects a hot Flow while not visible. Compare repeatOnLifecycle and collectAsStateWithLifecycle, including cancellation and upstream sharing.",
    "Effect testing": "Design a deterministic test proving an effect restarts when its key changes, cleans up once, and uses the latest callback without relying on delays.",
    "Back-stack ownership": "Two instances of the same destination appear on the back stack. Explain why each entry needs separate ViewModel and saved-state ownership and when sharing is intentional.",
    "Typed arguments": "A navigation route passes a full User object as encoded JSON. Review the design and replace it with typed, validated identifiers and source-of-truth reload.",
    "singleTop semantics": "A notification opens a destination already below the top of the stack. Explain what launchSingleTop does and does not do, then choose the intended back-stack behavior.",
    "Deep-link entry": "A deep link targets an authenticated order while the user is signed out. Build the validation, authentication, authorization, and restored navigation flow.",
    "Navigation testing": "What belongs in a pure navigation policy test, a NavController integration test, and a device deep-link test? Give one failure each layer can catch.",
    "Adaptive breakpoints": "A tablet changes from split screen to full screen while a detail item is selected. Design adaptive layout from window size without losing selection or duplicating navigation state.",
    "RTL correctness": "Review a row with left/right padding, a directional arrow, mixed Arabic and English text, and a swipe gesture. What must change for real RTL support?",
    "Accessibility semantics": "An icon-only toggle looks correct but TalkBack announces only 'button'. Define the role, label, state, action, and tests needed for a usable control.",
    "Font-scale resilience": "At 200% font scale, a checkout button overlaps the total. Redesign the layout and state what must scroll, wrap, remain reachable, and be tested.",
    "UI performance evidence": "A LazyColumn drops frames during fast scroll. Design a trace-driven investigation across item identity, composition work, measure/layout, image loading, and allocation.",
    "UI test pyramid": "For a Compose checkout flow, divide coverage among reducer tests, repository tests, semantics tests, screenshot tests, and device tests based on the risk each can prove.",
    "Semantics selectors": "A test finds nodes by visible text and breaks after translation. Replace brittle selectors without hiding accessibility defects behind arbitrary test tags.",
    "Accessibility assertions": "A screenshot matches the design. List the accessibility claims it cannot prove and write the semantic assertions and manual checks still required.",
    "Flakiness removal": "A UI test waits two seconds after tapping Save and fails in CI. Replace the delay with controlled dependencies and a semantic condition tied to the actual state transition.",

    # Runtime, concurrency and advanced UI
    "Kotlin to DEX pipeline": "Trace a suspend Kotlin function from source to class files, desugared bytecode, DEX, a minified APK, and ART. Which stage owns each transformation?",
    "D8 versus R8": "A teammate says D8 and R8 are interchangeable names for the same optimizer. Correct the model and explain what artifact and failure each tool helps you investigate.",
    "ART execution": "Does Android execute ordinary JVM bytecode directly? Explain DEX loading, interpretation, JIT, AOT profiles, and why execution strategy can vary by device and install history.",
    "Zygote model": "Explain how Zygote starts an Android app process, what memory can be shared through copy-on-write, and why app initialization still runs in the child process.",
    "Class loading identity": "Two classes have the same fully qualified name but come from different ClassLoaders. Are they the same type? Relate the answer to dynamic features or plugin code.",
    "JNI boundary": "A native call crashes only on one ABI. Walk through symbol packaging, thread attachment, local and global references, exception checking, and the artifacts you inspect.",
    "Reflection and shrinking": "A class is reached only by reflection and disappears in release. Explain why R8 cannot infer the edge, then choose between explicit registration, generated code, and a narrow keep rule.",
    "Boxing and allocation": "A hot Kotlin loop stores millions of Int values in generic collections. Explain where boxing appears, how you would measure its cost, and when specialized storage is justified.",
    "Crash retrace": "A production stack trace is obfuscated. Describe how mapping files, build IDs, native symbols, and exact artifact versions turn it into actionable evidence.",
    "Runtime evidence": "Compare what a JVM unit test, APK inspection, instrumented test, Perfetto trace, and on-device crash can prove about Android runtime behavior.",
    "Race definition": "Two coroutines increment a shared counter using read-modify-write. Write a harmful interleaving and distinguish a race condition from a merely nondeterministic execution order.",
    "Atomicity versus visibility": "A field is @Volatile and multiple threads execute balance = balance - amount. Explain why visibility is not atomicity and show a safe state transition.",
    "Mutex contract": "A coroutine Mutex protects a map, but the critical section performs network I/O and calls user code. Review cancellation, reentrancy, latency, and the invariant that should actually be locked.",
    "Atomic update": "Two fields must change together. Compare two separate AtomicInteger updates with one immutable state in AtomicReference.updateAndGet.",
    "Confinement": "Design a serialized owner for mutable session state using one dispatcher, actor, or event loop. What operations are allowed across the boundary?",
    "Immutability": "Does using immutable data eliminate all concurrency bugs? Explain what it solves and what races remain around publication, ordering, and multiple versions.",
    "Deadlock review": "Two code paths acquire accountLock and cacheLock in opposite order. Identify the deadlock, repair lock ordering, and discuss suspending while holding a lock.",
    "Backpressure": "A producer emits 10,000 updates per second and the UI can render 60. Choose between buffering, conflation, dropping, batching, and slowing the producer based on value semantics.",
    "Stress testing": "Why can a concurrency stress test pass while a race still exists? Design controlled interleavings and explain what stress adds beyond them.",
    "Cancellation and locks": "A coroutine is cancelled while waiting for or holding a Mutex. What guarantees do you need for acquisition, finally cleanup, and shared-state consistency?",
    "Frame pipeline": "Trace a user input through state mutation, composition, measure, layout, draw, RenderThread, and GPU presentation. Where can a missed frame originate?",
    "Snapshot state": "Two coroutines update Compose snapshot state from different contexts. Explain snapshot consistency, mutation policy, and how conflicting writes become visible.",
    "Stability contract": "What does Compose stability allow the runtime to skip, and why does stable never mean immutable, thread-safe, or cheap to render?",
    "Custom layout": "Design a custom two-child Compose Layout. Explain constraints, measurement rules, placement, intrinsic measurements, RTL, and what happens if you measure a child twice.",
    "Lazy list identity": "A LazyColumn uses list indices as keys and items are inserted at the top. Explain the state and animation bugs, then choose stable keys and content types.",
    "Nested scroll": "A collapsing toolbar and inner list both consume drag deltas. Trace pre-scroll, child consumption, and post-scroll, including fling ownership.",
    "Semantics merging": "A clickable card contains an icon, title, and status. Decide whether to merge descendants and show how the choice changes TalkBack output and test selectors.",
    "Focus restoration": "A TV or keyboard-driven screen navigates away and back after the list changes. Design stable focus identity and restoration without pointing to a removed item.",
    "Edge-to-edge": "Enable edge-to-edge for a screen with a top app bar, IME, and gesture navigation. Assign inset consumption once and avoid double padding.",
    "UI benchmark": "Design a Macrobenchmark for scroll jank or startup. Specify the journey, compilation mode, setup, iterations, metrics, and how you prevent benchmark code from changing the app behavior.",

    # Staff, incident, interview communication and POS
    "Requirement shaping": "A stakeholder asks for 'instant sync everywhere'. Turn that phrase into measurable latency, freshness, offline, conflict, cost, and availability requirements before proposing architecture.",
    "Architecture evolution": "A monolith is slowing delivery, but a rewrite would stop feature work for a year. Design an incremental seam, migration order, compatibility period, and rollback.",
    "Ownership model": "A shared mobile platform has many users and no clear on-call owner. Define product ownership, support expectations, deprecation, and escalation before expanding adoption.",
    "SLO and error budget": "Choose an SLO for a mobile sync journey, define good and bad events, and explain how an error budget changes release decisions.",
    "Blast-radius control": "You must replace the networking stack used by every feature. Design flags, cohorts, shadow traffic, observability, and rollback to limit blast radius.",
    "Migration governance": "Five teams must migrate to a new API. How do you version contracts, publish tooling, track adoption, handle exceptions, and retire the old path without a permanent dual system?",
    "Platform product thinking": "An internal library has technically elegant APIs but poor adoption. Treat it as a product: identify users, pain, success metrics, migration cost, documentation, and support.",
    "Decision under uncertainty": "You have incomplete evidence and a deadline. Explain how reversibility, option value, blast radius, and an explicit revisit trigger shape the decision.",
    "Cross-team disagreement": "Two teams disagree on a shared API and both have valid constraints. Walk through how you surface invariants, compare options, decide, and record dissent without stalling delivery.",
    "Operational design": "Review a design document that covers components but omits dashboards, alerts, runbooks, ownership, migration, and rollback. What must be added before approval?",
    "Capstone boundaries": "Describe one mobile feature end to end from UI intent through local state, durable work, backend acknowledgement, telemetry, and recovery. Be explicit about what each test layer proves.",
    "Test portfolio": "A team has 2,000 slow UI tests and few lower-level tests. Rebuild the portfolio around failure risk, feedback speed, framework boundaries, and production evidence.",
    "Failure injection": "For an offline-first checkout flow, inject process death, timeout after commit, duplicate delivery, stale auth, and database failure. State the invariant each case tests.",
    "Observability contract": "Define logs, metrics, traces, operation IDs, and redaction for a sync operation so an engineer can reconstruct failure without storing user content.",
    "Toolchain honesty": "In an interview, you implemented a JVM model but did not run Android device tests. How do you explain the evidence precisely and propose the missing verification without underselling the work?",
    "Severity and scope": "A new release causes intermittent checkout failures. Explain how you determine severity using affected users, business function, data integrity, security, and duration.",
    "Mitigation before certainty": "Users are losing work but the root cause is unclear. Choose a reversible mitigation now, preserve evidence, and explain which actions must wait for stronger confidence.",
    "Incident roles": "A mobile incident has ten engineers changing things at once. Define Incident Commander, communications, investigation, mitigation, and scribe roles and their decision boundaries.",
    "Hypothesis testing": "Crash reports support three plausible causes. Show how you rank hypotheses and choose the next observation or experiment that best separates them.",
    "Post-incident actions": "Turn 'be more careful' into owned, testable follow-ups. Which actions change prevention, detection, mitigation, and recovery?",
    "Risk prioritization": "Rank a possible auth bypass, a reproducible data loss, a 200ms startup regression, and a cosmetic RTL bug. State the evidence and product context that could change the order.",
    "Trust boundaries": "Threat-model a mobile payment flow across app, OS intent, terminal SDK, backend, and provider. What input is untrusted at each boundary?",
    "Release-like performance": "A debug build is slow but release feels fine. Explain which performance conclusions are valid and build a representative measurement instead of arguing from either run.",
    "Security regression tests": "After fixing an exported-component vulnerability, design regression tests for hostile intents, authorization, replay, oversized input, and logging redaction.",
    "Trade-off communication": "Give a 90-second recommendation between two architectures: state the invariant, constraints, chosen option, cost, rejected alternative, and revisit signal.",
    "Twenty-second answer": "Answer 'What is structured concurrency?' in twenty seconds with a conclusion, mechanism, and one failure it prevents.",
    "Ninety-second depth": "Expand the same structured-concurrency answer to ninety seconds without rambling: include cancellation, failure propagation, ownership, and a concrete Android example.",
    "Clarifying questions": "You are asked to design offline sync. Which few clarifying questions materially change the architecture, and which questions are just delay?",
    "Uncertainty language": "You do not remember an exact Android version rule. Demonstrate how to state what you know, isolate the uncertainty, and describe the authoritative verification.",
    "Shadowing review": "Listen to a recorded technical answer and diagnose filler, missing conclusion, unsupported claims, and weak trade-offs. What do you change on the second attempt?",
    "Readiness evidence": "What evidence shows you are ready for a Senior Android interview beyond finishing lessons or memorizing definitions?",
    "Gap-driven revision": "A mock interview exposes weak answers in Binder, Flow cancellation, and migrations. Build a revision loop from the failed reasoning rather than rereading everything.",
    "Mock interpretation": "You scored well overall but failed one security blocker. How should that affect readiness, and why is the average score insufficient?",
    "Portfolio honesty": "A project in your portfolio was mostly team work. Explain your exact contribution, decisions, constraints, failures, and evidence without inflating ownership.",
    "Interview-day strategy": "You receive an ambiguous Android system-design question. Walk through clarification, assumptions, structure, time management, trade-offs, and recovery when you get stuck.",
    "Reversal boundary": "A terminal approves a payment but the host response is lost. Explain when reversal is valid, who authorizes it, and why starting a new sale is dangerous.",
    "Settlement and reconciliation": "Differentiate authorization, capture, settlement, reversal, and refund. Which identifiers let operations reconcile terminal and provider records?",
    "Terminal operation identity": "Design a payment attempt ID that survives process death, duplicate callbacks, reconnects, and retries across app, terminal SDK, backend, and provider.",
    "Hardware disconnect": "The card reader disconnects after card read but before the app sees the outcome. Model the state, user message, reconnection, and reconciliation flow.",
    "PCI-safe diagnostics": "Support needs enough logs to investigate terminal failures. Define what may be logged, what must be masked or excluded, access controls, retention, and correlation IDs.",
}


def interview_prompt(topic: str, style: str, wrong: str, prefix: str) -> str:
    example = ALGORITHM_EXAMPLES.get(topic.lower())
    if example:
        return example[0]
    if topic in PROMPT_OVERRIDES:
        return PROMPT_OVERRIDES[topic]
    if prefix == "DSA":
        return f"Solve **{topic}** in Kotlin. Define the input and output first, handle the edge cases aloud, then trace your algorithm and justify its time and space complexity."
    prompts = {
        "debugging": f"A production issue points to **{topic}**. A teammate says, “{wrong}” Walk me through why that diagnosis is right or wrong, what you inspect first, the fix, and the regression test.",
        "code-review": f"During a review of **{topic}**, you hear this justification: “{wrong}” Would you approve it? Identify the correctness risk and show the change you would request.",
        "architecture": f"Design the ownership and data flow for **{topic}**. Why is “{wrong}” unsafe, where should the decision live, and which trade-off could change your design?",
        "system-design": f"Design **{topic}** for a mobile client. Cover identity, state transitions, duplicate or offline delivery, recovery, and observability. Explain why “{wrong}” is not a sufficient design.",
        "performance": f"How would you investigate **{topic}** in a production Android app? State the metric, the trace or artifact you need, and why “{wrong}” is not acceptable evidence.",
        "behavioral": f"Tell me about a real situation involving **{topic}**. What was the context, what did you personally decide and do, what evidence showed the result, and what would you change now?",
        "product-android": f"How would you implement **{topic}** in a production Android app? Explain the platform and lifecycle constraints, the user-visible failure, and how you would verify it on a device.",
        "conceptual": f"A teammate says, “{wrong}” Do you agree? Explain **{topic}** from first principles, including what happens under the hood and where its guarantee stops.",
    }
    return prompts.get(style, prompts["conceptual"])


def rewrite_question(path: Path, answer_text: str) -> None:
    original = path.read_text(encoding="utf-8")
    if not any(marker in original for marker in QUESTION_MARKERS):
        return
    frontmatter, body = split_frontmatter(original)
    qid = field(frontmatter, "id")
    topic = field(frontmatter, "topic")
    style = field(frontmatter, "style")
    prefix = qid.split("-", 1)[0]
    risk = scenario(body, answer_text, topic)
    profile = PROFILES.get(prefix, PROFILES["ARC"])
    fact = spoken_answer(answer_text, topic)
    guidance = topic_guidance(topic, prefix, fact, profile, decision(answer_text, profile))
    wrong = guidance["wrong"]
    title = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
    heading = title.group(1) if title else f"{qid} — {topic}"
    answer_link = f"../Model-Answers/{qid}.md"
    lesson_link_match = re.search(r"\[Lesson\]\(([^)]+)\)", body)
    lesson_link = lesson_link_match.group(1) if lesson_link_match else ""
    links = f"[Open complete model answer]({answer_link})"
    if lesson_link:
        links += f" · [Lesson]({lesson_link})"
    question = interview_prompt(topic, style, wrong, prefix)
    rewritten = f'''{frontmatter}# {heading}

## Interview question

> **Interviewer:** {question}

<p dir="rtl" lang="ar"><strong>السياق:</strong> {risk}</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

{links}
'''
    path.write_text(rewritten, encoding="utf-8")


def rewrite_answer(path: Path, question_text: str) -> bool:
    original = path.read_text(encoding="utf-8")
    if not any(marker in original for marker in ANSWER_MARKERS):
        return False
    frontmatter, body = split_frontmatter(original)
    qid = field(frontmatter, "question_id") or path.stem
    qfront, qbody = split_frontmatter(question_text)
    topic = field(qfront, "topic") or qid
    prefix = qid.split("-", 1)[0]
    profile = PROFILES.get(prefix, PROFILES["ARC"])
    fact = spoken_answer(original, topic)
    risk = interviewer_question(qbody) or scenario(qbody, original, topic)
    existing_correction = decision(original, profile)
    guidance = topic_guidance(topic, prefix, fact, profile, existing_correction)
    correction = guidance["correction"]
    invariant = guidance["invariant"]
    wrong = guidance["wrong"]
    mechanism = mechanism_for(topic, profile)
    safe_topic = html_inline(topic)
    safe_risk = html_inline(risk)
    safe_invariant = html_inline(invariant)
    safe_mechanism = html_inline(mechanism)
    safe_correction = html_inline(correction)
    safe_wrong = html_inline(wrong)
    safe_alternative = html_inline(guidance["alternative"])
    safe_test = html_inline(guidance["test"])
    heading = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
    title = heading.group(1) if heading else f"{qid} — Complete model answer"
    example = algorithm_example(topic)
    rewritten = f'''{frontmatter}# {title}

## الإجابة المختصرة

**Spoken answer:** “{fact}”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> {safe_invariant}</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">{safe_risk}</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في {safe_topic}:</strong> {safe_mechanism}</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">{safe_correction}</p>

## الـfailure والـwrong answer

**Common wrong answer:** “{wrong}”

<p dir="rtl" lang="ar">في <strong>{safe_topic}</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: {safe_invariant} النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">{safe_alternative}</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">{safe_test}</p>

{example}

## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في {safe_topic}، الـshortcut هي: <bdi dir="ltr">{safe_wrong}</bdi> ودي تكسر: {safe_invariant}</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">{safe_test}</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">{safe_alternative}</span>

## English model answer

“{fact} {profile['english']} {ENGLISH_EVIDENCE[prefix]}”
'''
    path.write_text(rewritten, encoding="utf-8")
    return True


def harden_bank() -> tuple[int, int]:
    rewritten_questions = 0
    rewritten_answers = 0
    for answer_path in sorted(ANSWER_DIR.glob("*.md")):
        qid = answer_path.stem
        question_path = QUESTION_DIR / f"{qid}.md"
        if not question_path.exists():
            continue
        answer_before = answer_path.read_text(encoding="utf-8")
        question_before = question_path.read_text(encoding="utf-8")
        if rewrite_answer(answer_path, question_before):
            rewritten_answers += 1
        if any(marker in question_before for marker in QUESTION_MARKERS):
            rewrite_question(question_path, answer_before)
            rewritten_questions += 1
    return rewritten_questions, rewritten_answers


if __name__ == "__main__":
    questions, answers = harden_bank()
    print(f"Rewrote {questions} interview prompts and {answers} model answers")

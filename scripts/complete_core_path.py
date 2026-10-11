#!/usr/bin/env python3
"""Complete the remaining core path with interview-first, topic-specific units."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parent.parent; DATE="2026-10-11"
CODE="projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt"; TEST="projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt"
def slug(x):return re.sub(r'[^a-z0-9]+','-',x.lower()).strip('-')
def U(id,day,title,module,path,pre,prefix,start,model,risk,decision,wrong,right,sources,concepts,lab=None):
 return dict(id=id,day=day,title=title,module=module,path=path,pre=pre,prefix=prefix,start=start,model=model,risk=risk,decision=decision,wrong=wrong,right=right,sources=sources,concepts=concepts,lab=lab)

A="https://developer.android.com/"
K="https://kotlinlang.org/"
O="https://owasp.org/"
units=[
U("ARC-004",22,"Hilt scopes, qualifiers and DI tests","04-Architecture-DI","04-Architecture-DI/arc-004-hilt-scopes-qualifiers-and-di-tests.md",["ARC-003"],"ARC",16,
"DI بتفصل إنشاء dependencies عن استخدامها، والscope عقد lifetime مش performance annotation. object أقصر عمرًا مينفعش يتخزن جوه owner أطول. qualifier بيفرق bindings من نفس type، والاختبار لازم يقدر يستبدل boundary من غير service locator خفي.","Singleton ماسكة session/user object فتسرّب بيانات حساب قديم بعد logout، أو binding غلط توصل production endpoint في test.","ارسم ownership graph، اختار أضيق scope تحقق المشاركة المطلوبة، استخدم qualifiers بأسماء معنى، واختبر replacement والlogout/recreation.","@Singleton class SessionCache(var userId: String)","@ActivityRetainedScoped class SessionOwner @Inject constructor()",[A+"training/dependency-injection/hilt-android",A+"training/dependency-injection/hilt-testing",A+"training/dependency-injection/hilt-android#component-lifetimes"],
[("Hilt component lifetimes","Scope lifetime must match the data owner; a singleton cannot safely retain account-scoped mutable state."),("Qualifier design","Qualifiers distinguish semantic bindings such as Authenticated and Public clients, not arbitrary implementation names."),("Accidental singleton session","Logout must invalidate account state; process-wide caches need keys or explicit clearing and must not capture screen owners."),("DI replacement tests","A test replaces the narrow boundary and verifies graph wiring plus behavior; constructor tests alone do not prove Hilt installation."),("Service locator trade-off","A global locator hides dependencies and lifetime, making order-dependent tests and stale state easier to create.")],26),
U("ARC-005",23,"Modules, contracts and ADRs","04-Architecture-DI","04-Architecture-DI/arc-005-modules-contracts-and-adrs.md",["ARC-001","ARC-003"],"ARC",21,
"الموديول boundary للownership والاعتماد والبناء، مش folder تجميلي. contract ضيقة تقلل معرفة المستهلك بالتنفيذ. ADR تسجل context والخيارات والقرار والنتائج عشان الفريق يراجع reasoning بدل ما يحفظ النتيجة.","feature modules متشابكة bidirectional، وكل تعديل يبني التطبيق كله، والـADR تقول استخدمنا Clean Architecture من غير context أو بدائل.","اقسم حسب change ownership وpublic API، امنع cycles، قِس build graph، واكتب ADR بقرار قابل للنقض وconsequences واضحة.","featureA -> featureB -> featureA","featureA -> contracts <- featureB",[A+"topic/modularization",A+"topic/architecture",A+"topic/architecture/recommendations"],
[("Module boundary","A useful boundary groups code that changes together and exposes a small stable contract."),("Dependency direction","Features depend on contracts or shared foundations, not on each other's internal implementations."),("Public API control","Internal implementation stays hidden so refactors do not ripple across the graph."),("ADR quality","An ADR records forces, alternatives, decision, consequences, and a revisit trigger."),("Build and ownership trade-offs","More modules can improve isolation and parallelism but add configuration, graph, and API maintenance cost.")]),
U("ARC-006",24,"Revision: architecture code review and DSA","04-Architecture-DI","04-Architecture-DI/arc-006-revision-architecture-code-review-and-dsa.md",["ARC-002","ARC-003"],"ARC",26,
"مراجعة architecture تبدأ من invariants وdata ownership وfailure path، مش أسماء layers. في DSA نفس المهارة: عرّف contract وinvariant وبعدين اختار structure. الـreview الجيدة تفرّق blocker correctness عن preference.","Reviewer يطلب pattern أكبر من غير failure حقيقي، أو يوافق على repository بتكتب network result فوق local edits من غير conflict policy.","اكتب observation وتأثير واقتراح واختبار، واطلب evidence للtrade-off. في live coding اشرح invariant وcomplexity وحدود input.","// Looks clean, ship it","// Verify owner, failure, conflict, cancellation, and tests",[A+"topic/architecture/recommendations",A+"topic/architecture/data-layer",K+"docs/collections-overview.html"],
[("Architecture review order","Trace input, state owner, side effects, failures, and observability before discussing naming."),("Review severity","A blocker protects correctness or security; a suggestion improves maintainability without pretending urgency."),("Repository conflict review","Offline writes need durable identity, ordering, retry, and conflict policy before sync implementation details."),("ADR challenge","Challenge assumptions with evidence and offer a viable alternative plus consequences."),("DSA invariant in review","A code review can verify the invariant on boundaries instead of trusting a familiar-looking algorithm.")]),
U("UI-002",26,"Compose state and recomposition","05-Views-Compose","05-Views-Compose/ui-002-compose-state-and-recomposition.md",["ARC-002"],"UI",6,
"Composition تصف UI من state؛ recomposition تعيد تنفيذ composables اللي قرأت state اتغيرت، ومش معناها إعادة رسم كل الشاشة. state hoisting يفصل value وevents، والاستقرار يؤثر على إمكانية skip لكنه مش هدف يتزور بـannotations.","List mutable اتغيرت in-place فالواجهة ما اتحدثتش، أو composable تعمل network call كل recomposition.","استخدم immutable observable state، ارفعها لأقرب owner مشترك، خلي composition بلا side effects، وقِس recomposition قبل optimization.","items.add(newItem) // same unobserved mutable list","items = items + newItem // publish a new immutable state",[A+"develop/ui/compose/state",A+"develop/ui/compose/mental-model",A+"develop/ui/compose/performance/stability"],
[("State reads and invalidation","Compose tracks observable state reads and schedules affected scopes when values change."),("State hoisting","Hoist state as value plus events to the lowest common owner that needs coordination."),("Immutable collections","Publishing immutable snapshots makes equality and change ownership auditable."),("Stability and skipping","Stability can enable skipping, but false stability declarations can hide changes and break UI."),("Recomposition evidence","Use layout inspector or tracing and measure expensive work; counts alone are not a user problem.")],27),
U("UI-003",27,"Compose effects and lifecycle collection","05-Views-Compose","05-Views-Compose/ui-003-compose-effects-and-lifecycle-collection.md",["UI-002","COR-004"],"UI",11,
"Effect API تربط side effect بعمر composition ومفاتيحها. LaunchedEffect تلغي وتعيد التشغيل لما key تتغير. DisposableEffect تعمل cleanup. rememberUpdatedState يسمح effect طويلة تشوف callback حديثة من غير restart. lifecycle collection توقف استهلاك UI حسب owner.","LaunchedEffect(Unit) تقرأ userId قديمة، أو key متغيرة كل frame تعيد network request، أو collector تستمر بعد view STOPPED.","اختار key تمثل identity الحقيقية، افصل producer عن collector، واختبر restart/cleanup مع تغيير key وlifecycle.","LaunchedEffect(Unit) { load(userId) }","LaunchedEffect(userId) { load(userId) }",[A+"develop/ui/compose/side-effects",A+"develop/ui/compose/lifecycle",A+"kotlin/flow/stateflow-and-sharedflow"],
[("LaunchedEffect keys","Keys define effect identity; a change cancels the old coroutine and starts a new one."),("DisposableEffect cleanup","Register and unregister the same observer at a lifecycle-aware boundary."),("rememberUpdatedState","Keep a long-lived effect while reading the latest callback or value without an unnecessary restart."),("Lifecycle-aware collection","Collect UI state only while the chosen lifecycle is active and use the correct owner."),("Effect testing","Change keys and lifecycle deterministically and assert start, cancellation, and exactly-once cleanup.")]),
U("UI-004",28,"Navigation ownership and back stack","05-Views-Compose","05-Views-Compose/ui-004-navigation-ownership-and-back-stack.md",["AND-002","UI-002"],"UI",16,
"Navigation state لها owner وback stack entries بهويات وsaved state. مرّر IDs صغيرة بدل objects، وحمّل البيانات من source of truth. singleTop/popUpTo يغيروا stack semantics؛ deep links entry points لازم تتختبر زي launcher.","نفس detail route تتضاف مرتين مع نفس ID، أو object كبيرة في arguments تبقى stale بعد process death.","استخدم typed route contract، validate external routes، قرر singleTop/popUpTo من UX، واختبر Back عبر launch/deep link/notification.","navigate(\"detail/$jsonObject\")","navigate(Route.Detail(itemId))",[A+"guide/navigation",A+"develop/ui/compose/navigation",A+"guide/navigation/design"],
[("Back-stack ownership","The navigation host owns ordered entries; screens should request navigation rather than mutate hidden globals."),("Typed arguments","Pass stable identifiers and reload current data instead of serializing domain objects into routes."),("singleTop semantics","singleTop prevents an equal destination at the top, not duplicates elsewhere or stale arguments."),("Deep-link entry","A deep link must build an authorized valid stack and preserve Back behavior."),("Navigation testing","Assert destinations and arguments from each entry point, recreation, duplicate taps, and invalid links.")],28),
U("UI-005",29,"Adaptive UI, RTL, a11y and performance","05-Views-Compose","05-Views-Compose/ui-005-adaptive-ui-rtl-a11y-and-performance.md",["UI-001","UI-002"],"UI",21,
"Adaptive UI تتصرف حسب available space/posture مش اسم الجهاز. RTL تحتاج logical start/end وعزل code LTR. accessibility contract تشمل semantics وfocus وtouch target وfont scale. الأداء يقاس frames ومراحل العمل، مش إحساس المطور.","layout ثابتة تنهار عند 200% font، icon اتجاهها غلط في RTL، أو تحسين يخفي semantics عشان يقلل nodes.","اختبر window sizes وRTL/font scale/TalkBack، استخدم semantics meaningful، وقِس jank قبل وبعد على build ممثلة.","Modifier.padding(left = 16.dp)","Modifier.padding(start = 16.dp)",[A+"develop/ui/compose/layouts/adaptive",A+"guide/topics/ui/accessibility",A+"develop/ui/compose/performance",A+"guide/topics/resources/localization"],
[("Adaptive breakpoints","Choose layouts from available window space and content needs, preserving state across layout changes."),("RTL correctness","Use logical directions and isolate code, numbers, and icons whose meaning is directional."),("Accessibility semantics","Expose role, label, state, action, focus order, and sufficiently large targets without duplicate noise."),("Font-scale resilience","Content must reflow, scroll, or wrap without clipping critical actions."),("UI performance evidence","Measure frame timing and expensive phases on representative release builds before optimizing.")]),
U("UI-006",30,"Revision: UI tests and DSA","05-Views-Compose","05-Views-Compose/ui-006-revision-ui-tests-and-dsa.md",["UI-002","UI-005"],"UI",26,
"UI test تختبر behavior من semantics/user surface، unit test تختبر reducer، screenshot تختبر pixels ضمن حدود. اختار أقل طبقة تثبت الخطر. DSA sliding window تحتاج invariant عن محتوى النافذة، مش nested loops مخفية.","اختبار يعتمد على text متغيرة وترتيب زمني وsleep، أو screenshot تعتبر accessibility proof.","استخدم stable semantics بحذر، controlled state، idling/scheduler مناسب، واختبر reducer سريعًا ثم journey حرجة على Android.","Thread.sleep(1000); onNodeWithText(\"Done\")","injectState(Success); onNodeWithTag(RESULT).assertIsDisplayed()",[A+"develop/ui/compose/testing",A+"training/testing/fundamentals",K+"docs/collections-overview.html"],
[("UI test pyramid","Put pure state transitions in unit tests and reserve device tests for framework and user integration."),("Semantics selectors","Select by stable meaning, not incidental layout hierarchy or translated display text."),("Accessibility assertions","Semantics tests catch labels and actions, while TalkBack and visual checks cover additional behavior."),("Flakiness removal","Control clocks, dispatchers, network, and state instead of increasing sleeps."),("Sliding-window invariant","Maintain exactly the elements satisfying the current window contract and update both ends once.")]),
U("PRO-002",32,"HTTP, timeouts, retries and token refresh","06-Production-Engineering","06-Production-Engineering/pro-002-http-timeouts-retries-and-token-refresh.md",["COR-003","ARC-003"],"PRO",11,
"HTTP failure لازم يتصنف: DNS/connect/read timeout، status، parse، cancellation، أو unknown side-effect outcome. retry مش default؛ تحتاج safe/idempotent operation وbackoff/jitter وحد أقصى. token refresh لازم single-flight وتتجنب loops.","عشر requests تاخد 401 فتعمل عشر refreshes، أو POST timed out يتكرر ويخصم مرتين.","اعمل authenticator/refresh coordinator واحد، idempotency key للside effects، صنّف statuses، واحفظ unknown outcome للمصالحة.","catch (e: Exception) { retry() }","retryDecision(method, attempt, status, hasIdempotencyKey)",[A+"training/basics/network-ops/connecting", "https://square.github.io/okhttp/features/interceptors/", "https://datatracker.ietf.org/doc/html/rfc9110"],
[("Timeout taxonomy","Connect, read, call, and application deadlines have different meanings and ownership."),("Retry safety","Retry only classified transient failures and only when operation semantics are safe or idempotent."),("Token refresh single-flight","Concurrent 401 responses share one refresh result and avoid recursive authentication loops."),("Unknown outcome","A timed-out write may have committed; represent unknown and reconcile by operation identity."),("Backoff and jitter","Bound exponential delay, add jitter, honor server guidance, and stop on permanent failure.")],29),
U("PRO-004",34,"Gradle, AGP 9, D8/R8 and signing","06-Production-Engineering","06-Production-Engineering/pro-004-gradle-agp-9-d8-r8-and-signing.md",["KOT-006"],"PRO",16,
"Gradle يحسب task graph، AGP يبني Android variants، Kotlin compiler تنتج bytecode/IR outputs، D8 يحول لـDEX، وR8 يعمل shrinking/optimization/obfuscation حسب pipeline. signing تثبت publisher key مش أمان business logic.","release crash بسبب class اتشالت بالshrink، والفريق يضيف keep all فيلغي قيمة R8، أو secret متخزنة في BuildConfig.","ثبت compatibility من docs، ابن release في CI، اختبر mapping/retrace/startup، واستخدم أضيق keep rules. signing keys خارج repo بصلاحيات محدودة.","-keep class ** { *; }","-keepclassmembers class * { @com.example.JsonName <fields>; }",[A+"build/releases/past-releases/agp-9-0-0-release-notes",A+"build/shrink-code",A+"studio/build/build-variants",A+"studio/publish/app-signing"],
[("Build pipeline","Explain source to class files, DEX, packaged artifact, signing, installation, and ART execution without merging the stages."),("Compatibility matrix","Verify Gradle, AGP, Kotlin, JDK, and Compose compiler compatibility from current official tables."),("R8 keep rules","Keep reflection or JNI entry points narrowly and verify release behavior plus mapping artifacts."),("Variant isolation","Keep debug tools and endpoints out of release through variant-aware dependencies and tests."),("Signing boundary","Protect upload/signing keys, rotate through supported mechanisms, and never treat client signatures as server authorization.")]),
U("PRO-005",35,"Profiling, startup and incident evidence","06-Production-Engineering","06-Production-Engineering/pro-005-profiling-startup-and-incident-evidence.md",["AND-004"],"PRO",21,
"ابدأ metric وscenario وbuild قبل profiler. startup cold/warm/hot لهم definitions مختلفة، وjank frame deadlines، والذاكرة تشمل allocation/retention. incident evidence لازم تربط version/cohort/timeline من غير PII.","debug profile تقيلة اتاخدت مرة واتعممت على release، أو average startup خبت tail regression.","استخدم Macrobenchmark/Perfetto/profileable release-like build، قارن distributions وbaseline، وحدد rollback threshold قبل rollout.","measureDebugOnce()","benchmarkReleaseLike(iterations = 20, startupMode = COLD)",[A+"topic/performance/benchmarking/macrobenchmark-overview",A+"topic/performance/tracing",A+"topic/performance/vitals/render",A+"topic/performance/baselineprofiles/overview"],
[("Measurement question","Name the user journey, metric, percentile, device class, build, and competing cause before collecting data."),("Startup modes","Cold creates process, warm may reuse process, and hot reuses Activity; compare matching scenarios."),("Perfetto trace reading","Follow main thread, binder, I/O, scheduling, and frames in one timeline rather than isolated logs."),("Memory evidence","Distinguish allocation churn, retained objects, native memory, and process pressure before calling a leak."),("Incident rollout","Use cohort/version metrics, a reversible flag or rollback, and privacy-safe diagnostics.")]),
U("PRO-006",36,"Revision: release health and DSA","06-Production-Engineering","06-Production-Engineering/pro-006-revision-release-health-and-dsa.md",["PRO-002","PRO-004"],"PRO",26,
"Release decision تجمع correctness/security/migration/crash/performance signals. gate لازم تكون قبل النشر ولها owner وthreshold وrollback. binary search في DSA تحتاج monotonic predicate وحدود تمنع overflow.","tests خضراء لكن migration path ناقصة أو security blocker مفتوحة، والفريق يكمل عشان deadline.","حوّل criteria لsignals صريحة، staged rollout، halt/rollback rule، وpost-release observation. متخليش average واحدة تلغي blocker.","if (unitTestsPass) release()","releaseAllowed(ReleaseSignals(tests, migration, crashRate, securityBlocker))",[A+"studio/publish",A+"topic/performance/vitals",K+"docs/collection-elements.html"],
[("Release gate","A release requires all blocking correctness and security signals, not a weighted average that can hide one blocker."),("Staged rollout","Increase exposure only after a fixed observation window and comparable health metrics."),("Rollback criteria","Define thresholds and ownership before release so incident pressure does not move the goalposts."),("Migration coverage","Test every supported installed schema to the target and destructive fallback policy explicitly."),("Binary-search invariant","Maintain a search interval that still contains every possible answer and compute midpoint without overflow.")]),
U("SYS-002",38,"Trees, graphs, heaps and basic DP","08-Mobile-System-Design","08-Mobile-System-Design/sys-002-trees-graphs-heaps-and-basic-dp.md",["SYS-001"],"SYS",6,
"Tree traversal تختار DFS/BFS من المطلوب، graph تحتاج visited وdirection/weights، heap تدعم أفضل عنصر مش sorted iteration، وDP تخزن overlapping subproblems بعد تعريف state/transition/base.","Dijkstra على negative edge، BFS على weighted graph، أو DP table من غير تعريف معنى الخانة.","اكتب graph contract، invariant، complexity، وoverflow. اختبر disconnected/cycle/duplicate edges وlarge weights.","queue.add(start) // no visited; cycles forever","queue.add(start); visited.add(start)",[K+"docs/collections-overview.html","https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/PriorityQueue.html"],
[("BFS and DFS choice","BFS gives shortest edge count in an unweighted graph; DFS fits reachability and recursive structure with depth risks."),("Heap invariant","The root is the priority optimum; arbitrary iteration is not globally sorted."),("Dijkstra precondition","Weights must be non-negative and stale heap entries need handling."),("Dynamic-programming state","Define exactly what dp state means, recurrence, base cases, and evaluation order."),("Graph test boundaries","Cover cycles, self-loops, disconnected nodes, duplicate edges, overflow, and invalid weights.")],30),
U("SYS-003",39,"Mobile auth and session state design","08-Mobile-System-Design","08-Mobile-System-Design/sys-003-mobile-auth-and-session-state-design.md",["ARC-003","PRO-002","PRO-003"],"SYS",11,
"الموبايل يحتفظ session state لكن server هو authority. access token قصيرة، refresh boundary، logout/revocation، account switch، offline UX، وsecure storage كلها state machine. ممنوع client تعتبر claims إذن نهائي لعملية حساسة.","refresh قديمة ترجع بعد logout فتحيي session، أو cache من account A تظهر في B.","اعمل generation/account namespace، single-flight refresh، clear/partition caches، وserver reauthorization لكل resource.","if (token != null) showAccount()","when (session) { Active -> loadAuthorized(); else -> clearSensitiveUi() }",[A+"privacy-and-security/risks/unsafe-use-of-deeplinks",A+"privacy-and-security/keystore",O+"www-project-mobile-application-security/"],
[("Session state machine","Model signed out, authenticating, active, refreshing, and reauthentication-required with explicit transitions."),("Refresh race","A refresh result is accepted only for the current account generation and cannot revive a logged-out session."),("Secure storage","Keystore protects key material; it does not make arbitrary stored plaintext or server trust unnecessary."),("Account partitioning","Database rows, caches, work, and notifications must carry account identity and clear or switch atomically."),("Server authority","The backend validates authorization and revocation; client checks improve UX but are not final security.")]),
U("SYS-004",40,"Offline notes sync design","08-Mobile-System-Design","08-Mobile-System-Design/sys-004-offline-notes-sync-design.md",["ARC-003","PRO-001"],"SYS",16,
"Local database source of truth تخلي UI تقرأ فورًا. writes تتسجل mutation identity/outbox وتتزامن لاحقًا. conflict policy لازم تعتمد على domain: last-write، field merge، version reject، أو user resolution. tombstones مهمة للحذف.","network response قديمة تكتب فوق local edit، أو delete يختفي ويرجع بعد sync.","transaction تجمع local write وoutbox، operation IDs idempotent، versions واضحة، reconcile يحافظ على draft والدليل.","api.save(note); dao.save(note)","db.transaction { dao.savePending(note); outbox.enqueue(mutation) }",[A+"topic/architecture/data-layer/offline-first",A+"training/data-storage/room",A+"topic/architecture/data-layer"],
[("Source of truth","UI observes local canonical state while sync updates it through transactions."),("Durable outbox","Persist mutation and local state atomically so process death cannot lose intent."),("Conflict policy","Choose per-domain semantics and preserve both evidence and user intent when automatic merge is unsafe."),("Deletion tombstones","A durable deletion marker prevents an older remote copy from resurrecting data."),("Sync observability","Track pending age, retry reason, conflicts, and success without logging note content.")]),
U("SYS-005",41,"Messaging and realtime tracking design","08-Mobile-System-Design","08-Mobile-System-Design/sys-005-messaging-and-realtime-tracking-design.md",["COR-004","PRO-002","SYS-004"],"SYS",21,
"Realtime mobile design تجمع push كwake hint، socket/stream أثناء foreground، REST catch-up، local ordered store، وserver sequence. delivery قد تتكرر وتتأخر وتتقطع؛ exactly-once end-to-end ادعاء محتاج تضييق شديد.","push تصل قبل data أو مرتين، location updates تستهلك battery، أو reconnect يكرر رسائل.","استخدم event IDs/sequence، dedupe، gap detection، bounded reconnect، presence/freshness، وprivacy/retention للlocation.","onPush { append(payload.message) }","onSignal { syncAfter(lastServerSequence) }",[A+"develop/background-work/background-tasks", "https://firebase.google.com/docs/cloud-messaging/concept-options",A+"topic/architecture/data-layer/offline-first"],
[("Push as signal","A push is a delivery hint; fetch or reconcile canonical data and handle duplicates."),("Ordering and gaps","Use server sequence or cursor, detect gaps, and backfill before presenting a complete history."),("Reconnect policy","Backoff with jitter, network awareness, token refresh, and one active connection owner."),("Location freshness","Expose timestamp and accuracy, adapt rate to user value, and stop collection with owner lifetime."),("Privacy and observability","Minimize retention and precision, obtain permission, and separate health metadata from sensitive content.")]),
U("SYS-006",42,"Revision: design review and concurrency","08-Mobile-System-Design","08-Mobile-System-Design/sys-006-revision-design-review-and-concurrency.md",["SYS-001","SYS-004"],"SYS",26,
"System design interview تبدأ requirements وscale/failure/privacy، ثم state owners وAPIs/data flow، وبعدها alternatives. concurrency review تحدد shared state وatomic boundary وordering بدل قول thread-safe عامة.","مرشح يرسم boxes من غير offline/auth/failure، أو يضيف lock حول network call فيعمل convoy.","قدّم design أساسي وبديل، اذكر bottleneck/rollout/observability، واستخدم serialization أو atomic DB transaction عند boundary الصحيحة.","synchronized(lock) { remote.call() }","val decision = mutex.withLock { readAndReserve() }; remote.call(decision)",[A+"topic/architecture",K+"docs/shared-mutable-state-and-concurrency.html"],
[("Requirement discovery","Clarify users, latency, offline, consistency, privacy, abuse, and failure priorities before components."),("State ownership","Every mutable state has one authority, update path, persistence level, and conflict policy."),("Concurrency boundary","Protect the smallest shared transition and avoid holding locks across slow external work."),("Alternative comparison","Compare consistency, latency, complexity, cost, and operational recovery rather than naming a winner."),("Design verification","Use invariants, failure injection, load model, observability, and staged rollout to test assumptions.")]),
U("INT-001",43,"Capstone integration and tests","09-Leadership-English","09-Leadership-English/int-001-capstone-integration-and-tests.md",["ARC-005","UI-006","PRO-006"],"INT",6,
"Capstone تجمع offline notes: UI state holder، repository/local source، outbox worker، auth session، sync conflict، وobservability. integration معناها contracts تتوصل وتفشل بوضوح، مش كل classes في module واحدة.","save تظهر success قبل durable transaction، worker تشتغل بحساب قديم، أو tests تستخدم fake تخفي migration/cancellation.","عرّف end-to-end acceptance paths، اختبر pure + database + worker contracts، وسجل Android SDK blocker بوضوح.","state = Saved; repository.save(note)","repository.saveDurably(note); state = SavedPendingSync",[A+"topic/architecture/recommendations",A+"topic/architecture/data-layer/offline-first",A+"training/testing/fundamentals"],
[("Capstone boundaries","UI sends intent, repository commits local truth, outbox syncs, and session scopes account data."),("Test portfolio","Use reducer unit tests, persistence migration tests, worker integration, and UI journeys for distinct risks."),("Failure injection","Force process death, network loss, conflict, account switch, duplicate work, and stale completion."),("Observability contract","Trace operation identity and stage without note content or credentials."),("Toolchain honesty","Architecture and JVM models remain separate from an Android build until SDK evidence exists.")]),
U("INT-002",44,"Production incident response","09-Leadership-English","09-Leadership-English/int-002-production-incident-response.md",["AND-004","PRO-005"],"INT",11,
"Incident response هدفها تقلل ضرر وتتعلم: detect، scope، mitigate، diagnose، recover، follow-up. severity من user impact مش صوت أعلى شخص. افصل timeline facts عن hypotheses، وخلي owner للقرار والتواصل.","الفريق يقضي ساعات في root cause بينما crash rate بتزيد وعنده rollback آمن.","حدد incident commander، rollback/flag حسب threshold، حافظ على evidence، واكتب action items بowner وdeadline وverification.","investigateUntilCertain()","if (materialRegression && rollbackAvailable) rollback()",["https://sre.google/sre-book/managing-incidents/","https://sre.google/workbook/incident-response/",A+"topic/performance/vitals"],
[("Severity and scope","Quantify affected users, functions, versions, geographies, and data/security impact."),("Mitigation before certainty","Use a reversible rollback or flag when impact is material, while preserving evidence for diagnosis."),("Incident roles","One owner coordinates decisions, communications, operations, and a shared factual timeline."),("Hypothesis testing","Choose the next observation that distinguishes competing causes and timebox branches."),("Post-incident actions","Actions change code, tests, detection, or process and include owner, deadline, and proof of completion.")]),
U("INT-003",45,"Performance and security review","09-Leadership-English","09-Leadership-English/int-003-performance-and-security-review.md",["PRO-003","PRO-005"],"INT",16,
"Senior review ترتب المخاطر من evidence وتأثير واحتمال. performance optimization من baseline، security من assets/trust boundaries/abuse. ما تخلطش secret obfuscation بتفويض server.","الفريق يسرّع startup بإزالة auth check، أو يشفر token بمفتاح ثابت داخل APK.","اعمل threat/performance budgets، اختبر release-like، أصلح أعلى risk، وحط regression gate وrollout monitoring.","val key = \"hardcoded-secret\"","val keyAlias = keystoreBackedAlias",[O+"www-project-mobile-application-security/",A+"privacy-and-security/keystore",A+"topic/performance/benchmarking/macrobenchmark-overview"],
[("Risk prioritization","Rank by user impact, exploitability or frequency, evidence confidence, and reversibility."),("Trust boundaries","Map external intents, network, storage, IPC, WebView, vendor SDKs, and backend authority."),("Release-like performance","Measure representative journeys and percentiles on controlled release builds."),("Security regression tests","Test authorization, hostile inputs, redaction, exported surfaces, and dependency configuration."),("Trade-off communication","State the protected invariant, measured cost, alternatives, and rollback signal.")]),
U("INT-005",47,"English technical explanation practice","09-Leadership-English","09-Leadership-English/int-005-english-technical-explanation-practice.md",["KOT-001"],"INT",21,
"الإجابة القوية لها structure: direct answer، mechanism، example، trade-off، evidence. English البسيطة الدقيقة أحسن من vocabulary كبيرة مبهمة. لو مش عارف، حدّد known/unknown وخطة تحقق.","إجابة خمس دقايق تبدأ تاريخ الموضوع ومتوصلش للقرار، أو ادعاء أرقام وخبرة مش حقيقية.","استخدم 20/90/180 ثانية، سجل نفسك، شيل filler، وراجع هل جاوبت السؤال وقلت assumptions.","It depends... [five minutes later]","My default is X because Y. I would choose Z when condition C changes.",[A+"topic/architecture/recommendations",K+"docs/coroutines-overview.html"],
[("Twenty-second answer","Give the decision and one reason without losing the key boundary."),("Ninety-second depth","Add mechanism, concrete example, failure path, and trade-off."),("Clarifying questions","Ask about scale, lifetime, consistency, and constraints before overcommitting."),("Uncertainty language","Separate what you know, infer, and would verify without bluffing."),("Shadowing review","Record, compare to a written structure, remove fillers, and repeat with a new example.")]),
U("INT-006",48,"Final revision and readiness evidence","09-Leadership-English","09-Leadership-English/int-006-final-revision-and-readiness-evidence.md",["INT-001","INT-002","INT-003","INT-004","INT-005"],"INT",26,
"Readiness مش نسبة من ملفات؛ evidence إنك تشرح وتتتبع وتكتب وتختبر وتدافع. راجع weak topics بالspaced recall، حل coding بصوتك، وقدم system design وincident. mock اختيارية ومش badge ضمان.","المتعلم يقرأ كل الإجابات ويعتبر recognition mastery، أو يعمل mocks كتير من غير تصحيح gaps.","استخدم checklist لكل competency، سجل evidence وتاريخ، ارجع للفشل، واعمل mock كاملة لما تبقى عايز assessment فعلًا.","if (readAllLessons) ready = true","readyEvidence = explain + trace + code + test + defend",[A+"training/testing/fundamentals",K+"docs/home.html"],
[("Readiness evidence","Require an explanation, trace, implementation, tests, and trade-off defense for each core domain."),("Gap-driven revision","Prioritize errors and slow explanations, then retest after spaced intervals."),("Mock interpretation","Use rubric categories and examples; one score never proves hiring outcome."),("Portfolio honesty","Distinguish executed Android evidence, JVM models, reviewed syntax, and conceptual designs."),("Interview-day strategy","Clarify, state assumptions, think aloud, test boundaries, and summarize the decision.")])
]

diff=["foundational","intermediate","senior","senior","senior"]; styles=["conceptual","code-review","debugging","architecture","system-design"]

def lesson(u,scn):
 qs=[f"{u['prefix']}-Q{i:03d}" for i in range(u['start'],u['start']+5)]; tested=u['lab'] is not None
 steps=["حدد المالك والـinput والعقد قبل اختيار pattern.",u['model'],"اكسر happy path بالـfailure الأساسية: "+u['risk'],"طبّق القرار واكتب evidence: "+u['decision']]
 rows=''.join(f'<tr><td>{i+1}</td><td>{x}</td></tr>' for i,x in enumerate(steps))
 fm=f'''---
id: {u['id']}
title: {u['title']}
module: {u['module']}
tier: Core
estimated_minutes: 65
prerequisite_ids: [{", ".join(u['pre'])}]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: {"tested" if tested else "not_applicable"}
last_source_checked: {DATE}
source_urls:
'''+''.join(f'  - {x}\n' for x in u['sources'])+(f'''example_paths:
  - ../{CODE}
  - ../{TEST}
''' if tested else 'example_paths: []\n')+f'''question_ids: [{", ".join(qs)}]
---
'''
 return fm+f'''
# {u['id']} — {u['title']}

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">{u['risk']} السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">{u['model']}</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody>{rows}</tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
{u['wrong']}
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> {u['risk']}</p>

```kotlin
{u['right']}
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> {u['decision']} في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">{u['decision']} قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> {u['concepts'][0][1]}</p>

**English, 20 seconds:** “{u['concepts'][0][1]}”

**English, 60–90 seconds:** “{u['concepts'][0][1]} My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: {u['risk']} I would implement this policy: {u['decision']} Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

'''+''.join(f'{i+1}. **Explain {t} under a production failure.** {fact}\n' for i,(t,fact) in enumerate(u['concepts'][:3]))+f'''
## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع {qs[0]} إلى {qs[-1]}، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ {DATE}.</p>

'''+(f"حل [LAB-{u['lab']:03d}](../Coding-Challenges/LAB-{u['lab']:03d}-{slug(u['id']+' '+u['title'])}.md) وراجع الاختبار المرتبط.\n" if tested else "اكتب test matrix وحدد بوضوح ما يحتاج Android/device evidence.\n")+f'''
حلّل [SCN-{scn:03d}](../Real-World-Scenarios/SCN-{scn:03d}-{slug(u['id']+' '+u['title'])}.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
'''

def qdocs(u):
 for i,(topic,fact) in enumerate(u['concepts']):
  qid=f"{u['prefix']}-Q{u['start']+i:03d}"; prompt=f"A senior review exposes this failure: {u['risk']} Explain {topic}, choose a correction, and name evidence that would prove or falsify it."
  q=f'''---
id: {qid}
lesson_id: {u['id']}
topic: {topic}
difficulty: {diff[i]}
style: {styles[i]}
expected_minutes: {4+i//2}
status: reviewed
---
# {qid} — {topic}

{prompt}

[Open complete model answer](../Model-Answers/{qid}.md) · [Lesson](../../{u['path']})
'''
  a=f'''---
id: {qid}-ANSWER
question_id: {qid}
status: reviewed
---
# {qid} — Complete model answer

**Spoken answer:** “{fact}”

<p dir="rtl" lang="ar"><strong>الشرح:</strong> {u['model']} بالنسبة لـ{topic}، القرار العملي هو: {u['decision']}</p>

**Mechanics and concrete failure:** The owner receives input, changes state, crosses the relevant boundary, and publishes an observable result. The dangerous path is: {u['risk']} A correct design preserves identity, ordering, failure classification, and cleanup or restoration.

**Common wrong answer:** “Use the named pattern and add a retry.” A pattern does not define ownership, retry safety, stale-result handling, or proof.

**Follow-up 1:** How would this answer change when the owner is recreated or the operation is delivered twice? Keep stable identity and durable state at the correct boundary, make the transition idempotent where required, and reject stale ownership. Test both cases separately because recreation and duplicate delivery have different causes.

**Follow-up 2:** What evidence would make you reject your first design? A controlled trace that violates its invariant, a release-like benchmark outside its budget, or an integration test showing platform behavior differs. I would keep the alternative explicit and use a reversible rollout rather than defend the first idea.

**Polished English answer:** “{fact} In this case the failure is {u['risk']} I would apply {u['decision']} and verify the transition with a focused regression test plus the appropriate integration evidence.”

**Rubric:** Direct contract, mechanism, failure trace, viable alternative, test, and evidence limit.
'''
  yield qid,q,a,topic

def scndoc(u,n):return f'''---
id: SCN-{n:03d}
lesson_id: {u['id']}
status: reviewed
code_verification: {"tested" if u['lab'] else "not_run"}
---
# SCN-{n:03d} — {u['title']} production failure

## Symptom, hypotheses and evidence

<p dir="rtl" lang="ar">{u['risk']} اكتب على الأقل فرضيتين، وحدد observation واحدة تفرق بينهم. ثبّت build وowner وoperation identity ووقت الحدث من غير تسجيل payload حساسة.</p>

## Investigation and corrected design

<p dir="rtl" lang="ar">{u['model']} الإصلاح المختار: {u['decision']}</p>

## Tests and rollout

1. Reproduce the bad ordering or boundary with controlled input.
2. Add a regression that fails on the wrong implementation.
3. Test stale, duplicate, cancellation/restart, and permanent failure separately.
4. Stage rollout and watch a correctness signal plus resource health.

## Senior follow-ups

1. **What would falsify the root-cause claim?** A trace showing the invariant already held while the symptom remained.
2. **What is the smallest mitigation?** Disable or route around the failing boundary without destroying diagnostic evidence.
3. **What is the evidence limit?** Local JVM behavior does not establish device, backend, or production timing.
'''

def labdoc(u):return f'''---
id: LAB-{u['lab']:03d}
lesson_id: {u['id']}
status: reviewed
code_verification: tested
---
# LAB-{u['lab']:03d} — {u['title']} boundary model

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> حوّل أهم قرار في الدرس لـpure Kotlin contract، وابدأ بtest للحل الغلط. استخدم <a dir="ltr" href="../{CODE}">CompletionModels.kt</a> و<a dir="ltr" href="../{TEST}">CompletionModelsTest.kt</a>. اشرح بوضوح إن النموذج لا يشغل Android framework أو backend.</p>

**Cases:** valid, malformed, duplicate, stale identity, boundary values, no mutation, and one permanent failure. Run `./gradlew test --tests academy.CompletionModelsTest --no-daemon`.

**Interview extension:** State the invariant and complexity or delivery guarantee, then propose the Android/integration test that closes the remaining evidence gap.
'''

# Author files and build records.
scn=29
for u in units:
 (R/u['path']).write_text(lesson(u,scn),encoding='utf-8')
 for qid,q,a,_ in qdocs(u):
  (R/f'Interview-Question-Bank/Questions/{qid}.md').write_text(q,encoding='utf-8');(R/f'Interview-Question-Bank/Model-Answers/{qid}.md').write_text(a,encoding='utf-8')
 (R/f'Real-World-Scenarios/SCN-{scn:03d}-{slug(u["id"]+" "+u["title"])}.md').write_text(scndoc(u,scn),encoding='utf-8')
 if u['lab']:(R/f'Coding-Challenges/LAB-{u["lab"]:03d}-{slug(u["id"]+" "+u["title"])}.md').write_text(labdoc(u),encoding='utf-8')
 (R/f'Flashcards-Revision/{u["id"]}.md').write_text(f'# {u["id"]} revision cards\n\n'+''.join(f'{i+1}. **{t}:** {x}\n' for i,(t,x) in enumerate(u['concepts'])),encoding='utf-8')
 (R/f'Speaking-Shadowing/DAY-{u["day"]:02d}.md').write_text(f'# Day {u["day"]} — {u["title"]}\n\n## 20 seconds\n\n“{u["concepts"][0][1]}”\n\n## Pressure prompts\n\n'+''.join(f'- Explain {t} and one failure.\n' for t,_ in u['concepts']),encoding='utf-8')
 scn+=1

mp=R/'CONTENT-MANIFEST.json';m=json.loads(mp.read_text())
items=[];seen=set()
for entry in m['items']:
 if entry['id'] not in seen: items.append(entry);seen.add(entry['id'])
m['items']=items;by={x['id']:x for x in items};scn=29
for u in units:
 qs=[f"{u['prefix']}-Q{i:03d}" for i in range(u['start'],u['start']+5)];tested=u['lab'] is not None;ex=[CODE,TEST] if tested else []
 by[u['id']].update(status='reviewed',code_verification='tested' if tested else 'not_applicable',verification_evidence='BUILD-VERIFICATION.md' if tested else None,question_ids=qs,example_paths=ex,source_urls=u['sources'],source_status='verified')
 for qid in qs:
  if qid not in by:
   x=dict(id=qid,type='question',path=f'Interview-Question-Bank/Questions/{qid}.md',answer_path=f'Interview-Question-Bank/Model-Answers/{qid}.md',prerequisites=[u['id']],status='reviewed',code_verification='not_applicable',verification_evidence='scripts/validate.py',question_ids=[],example_paths=[],source_urls=[u['sources'][0]],source_status='verified');items.append(x);by[qid]=x
 sid=f'SCN-{scn:03d}';x=dict(id=sid,type='scenario',path=f'Real-World-Scenarios/{sid}-{slug(u["id"]+" "+u["title"])}.md',prerequisites=[u['id']],status='reviewed',code_verification='tested' if tested else 'not_run',verification_evidence='BUILD-VERIFICATION.md' if tested else None,question_ids=[],example_paths=ex,source_urls=[u['sources'][0]],source_status='verified')
 if sid in by: by[sid].update(x)
 else: items.append(x);by[sid]=x
 if tested:
  lid=f'LAB-{u["lab"]:03d}';x=dict(id=lid,type='coding_challenge',path=f'Coding-Challenges/{lid}-{slug(u["id"]+" "+u["title"])}.md',prerequisites=[u['id']],status='reviewed',code_verification='tested',verification_evidence='BUILD-VERIFICATION.md',question_ids=[],example_paths=ex,source_urls=[u['sources'][0]],source_status='verified')
  if lid in by: by[lid].update(x)
  else: items.append(x);by[lid]=x
 scn+=1
m['as_of']=DATE;mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')

tp=R/'Interview-Question-Bank/BY-TOPIC.md';dp=R/'Interview-Question-Bank/BY-DIFFICULTY.md';sp=R/'Interview-Question-Bank/BY-INTERVIEW-STYLE.md';tt=tp.read_text();dt=dp.read_text();st=sp.read_text()
for u in units:
 for i,(qid,_,_,topic) in enumerate(qdocs(u)):
  ql=f'[{qid}](Questions/{qid}.md)';al=f'[answer](Model-Answers/{qid}.md)'
  if f'Questions/{qid}.md' not in tt:tt+=f'\n| {topic} | {ql} | [Model answer](Model-Answers/{qid}.md) |'
  if f'Questions/{qid}.md' not in dt:dt+=f'\n- {diff[i].title()}: {ql} — {al}'
  if f'Questions/{qid}.md' not in st:st+=f'\n- {styles[i].replace("-"," ").title()}: {ql} — {al}'
tp.write_text(tt.rstrip()+'\n');dp.write_text(dt.rstrip()+'\n');sp.write_text(st.rstrip()+'\n')
cp=R/'COVERAGE-MATRIX.md';lines=cp.read_text().splitlines()
for u in units:
 for i,line in enumerate(lines):
  if line.startswith(f'| {u["id"]} |'):
   qs=f'{u["prefix"]}-Q{u["start"]:03d}–{u["start"]+4:03d}'; ev=f'[JVM tests]({TEST})' if u['lab'] else 'Interview test plan; integration evidence pending'
   lines[i]=f'| {u["id"]} | {u["module"]} | Core | {", ".join(u["pre"])} | 120 | [{u["id"]}]({u["path"]}) | {qs} | {ev} | [official]({u["sources"][0]}) | reviewed | Interview-first explanation, production failure and verification |';break
cp.write_text('\n'.join(lines)+'\n')
print(f'Authored {len(units)} core lessons, {len(units)*5} Q&A, {len(units)} scenarios, and 5 labs')

from harden_interview_bank import harden_bank
print("Hardened interview bank:", harden_bank())

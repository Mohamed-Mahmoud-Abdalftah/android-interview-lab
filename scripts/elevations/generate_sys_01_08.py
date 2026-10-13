#!/usr/bin/env python3
"""Generator for SYS-01 through SYS-08 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "sys.json"

SYS_01_08 = [
    {
        "id": "SYS-01",
        "arabic_explanation": (
            "كيف تبدأ مقابلة Mobile System Design (المتطلبات، المقاييس، القيود، والمفاضلات) باحترافية كمهندس Senior/Staff؟\n\n"
            "1. الهيكل الزمني والتكتيكي لمقابلة الـ Mobile System Design (45 دقيقة):\n"
            "   - **أول 5-7 دقائق (Clarify Scope & Functional Requirements)**: لا تبدأ برسم مربعات أو كتابة كود! اطرح أسئلة توضيحية لتحديد نطاق المشكلة بدقة. ما هي الميزات الأساسية (Core Use Cases) وما الذي يقع خارج النطاق (Out of Scope)؟\n"
            "   - **الدقائق 7-12 (Non-Functional Requirements & Constraints)**: حدد قيود الموبايل الفريدة: هل التطبيق Offline-First؟ ما هو حجم استهلاك البطارية والشبكة المسموح به؟ ما هو الـ Latency المستهدف؟ ما هي طبيعة الأجهزة المستهدفة (Low-end vs Flagship)؟\n"
            "   - **الدقائق 12-25 (High-Level Architecture & End-to-End Flow)**: ارسم المعمارية الكلية (Data Flow): UI (Compose) -> ViewModel -> Domain (UseCases) -> Repository -> Data Sources (Local DB + Remote API) -> Backend Gateway.\n"
            "   - **الدقائق 25-40 (Deep Dive into Complex Subsystems)**: التعمق في التحدي الأكبر (Sync Engine, Concurrency, Cache Eviction, Conflict Resolution).\n"
            "   - **آخر 5 دقائق (Failure Modes & Trade-offs)**: استعراض سيناريوهات الفشل ونقاط الضعف والقرارات البديلة.\n\n"
            "2. الفروق الجوهرية بين Mobile System Design و Backend System Design:\n"
            "   - في الـ Backend: التركيز على QPS, Sharding, Load Balancers, Distributed Consensus.\n   - في الـ Mobile: التركيز على **Resource Scarcity** (محدودية الرام والبطارية)، **Network Flakiness** (انقطاع الاتصال وتبديل الشبكات)، **Process Death**، **State Restoration**، و**Local Source of Truth**."
        ),
        "practical_walkthrough": (
            "هيكلة إطار عمل مقابلة الـ System Design في كود معماري يوضح فصل المسؤوليات والـ High-Level Contracts:\n"
            "```kotlin\n"
            "// 1. تحديد الـ Domain Models والـ Contracts الصريحة قبل الخوض في التفاصيل:\n"
            "interface FeedRepository {\n"
            "    // Local Source of Truth يعيد Flow للـ UI وتحديثات فورية من قاعدة البيانات\n"
            "    fun getFeedStream(): Flow<PagingData<FeedItem>>\n"
            "    \n"
            "    // المزامنة تتم في الخلفية بشكل منفصل\n"
            "    suspend fun syncFeed(fetchStrategy: SyncStrategy): Result<Unit>\n"
            "}\n"
            "\n"
            "sealed interface SyncStrategy {\n"
            "    object CacheFirst : SyncStrategy\n"
            "    object NetworkFirst : SyncStrategy\n"
            "    data class DeltaSync(val lastSyncTimestamp: Long) : SyncStrategy\n"
            "}\n"
            "\n"
            "// 2. نمذجة حالات الواجهة الصريحة (Unidirectional Data Flow) لمعالجة الأخطاء الجزئية:\n"
            "data class FeedUiState(\n"
            "    val isLoading: Boolean = false,\n"
            "    val isOfflineMode: Boolean = false,\n"
            "    val pendingUploadsCount: Int = 0,\n"
            "    val bannerMessage: String? = null\n"
            ")\n"
            "```"
        ),
        "quick_answer": "Begin a mobile system design interview by clarifying functional and non-functional requirements in the first 5 minutes. Establish mobile constraints like offline tolerance, battery consumption, network flakiness, and low-end hardware profiles before proposing high-level data flow, domain contracts, and architectural trade-offs.",
        "best_answer": (
            "A disciplined mobile system design interview follows a structured, collaborative engineering framework:\n\n"
            "1. **Scope Clarification & Functional Requirements (Minutes 0–5)**: Clarify the core user journeys and deliberately define out-of-scope items. For example, in an Instagram-like feed, clarify whether we are designing feed ingestion, media uploading, real-time comments, or strictly offline consumption.\n\n"
            "2. **Mobile Constraints & Non-Functional Requirements (Minutes 5–10)**: Establish concrete operational targets:\n"
            "   - **Network Profile**: Offline-first vs. connected-only, cellular data thrift, latency ceilings (e.g. sub-200ms feed render from local cache).\n   - **Hardware Envelope**: Memory footprints for budget devices (2GB RAM), battery constraints (deferring syncs to Wi-Fi/charging via WorkManager).\n   - **Data Volume**: Cache size ceilings (e.g., maximum 200MB LRU disk cache).\n\n"
            "3. **High-Level Architecture (Minutes 10–25)**: Establish the layered system boundary: presentation state machines, domain business logic, repository local-source-of-truth abstractions, and network/local persistence layers.\n\n"
            "4. **Deep Dive & Bottlenecks (Minutes 25–40)**: Drill down into complex bottlenecks (e.g., two-way sync conflict resolution, binary chunk upload resumption, image pipeline memory management).\n\n"
            "5. **Trade-offs & Failure Modes (Minutes 40–45)**: Explicitly address edge cases (process death, partial backend outages, version skew)."
        ),
        "deep_answer": (
            "From a staff-level perspective, the primary failure mode in mobile system design interviews is treating mobile like a stripped-down backend:\n\n"
            "1. **The Client As An Untrusted, Volatile Runtime**: Backends operate in predictable server clusters; mobile clients operate on hostile, battery-constrained, physically moving devices where the OS can terminate the process at any second. Highlighting Android-specific lifecycle realities (Activity destruction, configuration changes, background execution limits) immediately differentiates senior candidates.\n\n"
            "2. **Driving the Conversation Proactively**: Do not wait for the interviewer to prompt for constraints. Drive the whiteboard by outlining the API schema contract (REST vs. GraphQL vs. gRPC), storage strategy (Room SQLite vs. Proto DataStore), and telemetry footprint upfront.\n\n"
            "3. **Explicit Trade-off Articulation**: Every architectural choice has a cost. If you choose an offline-first Room database with delta synchronization, immediately articulate the complexity trade-off: distributed conflict resolution (Client-Wins vs. Server-Wins), schema migrations, and sync queuing overhead."
        ),
        "follow_ups": [
            {
                "question": "What is the single most common mistake candidates make in mobile system design?",
                "answer": "Jumping straight into UI components or database schemas without clarifying requirements, scale constraints, and network failure modes."
            },
            {
                "question": "How do you handle ambiguous requirements intentionally given by an interviewer?",
                "answer": "Make explicit engineering assumptions out loud, validate them with the interviewer, and document them on the whiteboard before continuing."
            }
        ]
    },
    {
        "id": "SYS-02",
        "arabic_explanation": (
            "كيف تصمم تطبيق أندرويد ضخم متعدد الميزات (Scalable Multi-Feature Android Application) يعمل عليه عشرات الفرق؟\n\n"
            "1. التحديات الهندسية للتطبيقات الضخمة (Multi-Team Scale):\n"
            "   - بطء زمن التجميع والبناء (Build Times > 20 mins).\n   - التبعيات الدائرية (Circular Dependencies) وتداخل الكود بين الفرق.\n   - نزاعات الدمج المستمرة (Merge Conflicts) على ملفات الـ Navigation والـ DI.\n   - صعوبة اختبار وتطوير ميزة معينة بشكل منعزل.\n\n"
            "2. المعمارية المعيارية الموصى بها (Modular Architecture by Feature & Layer):\n   - **قاعدة فصل الواجهة عن التنفيذ (API vs. Implementation Pattern)**: لكل ميزة (Feature) يتم تقسيمها إلى موديولين على الأقل:\n     * `:feature:checkout:api`: يحتوي على الـ Interfaces, Data Transfer Objects, والـ Navigation Routes العامة فقط (كود خفيف جداً يترجم في ثوانٍ).\n     * `:feature:checkout:impl`: يحتوي على الـ Internal Views, ViewModels, Repositories، ولا يعتمد عليه أي موديول آخر مباشرة.\n   - **Core Layer (موديولات النواة)**:\n     * `:core:designsystem`: مكونات Compose العامة والـ Themes.\n     * `:core:network`: إعدادات OkHttp, Retrofit, Auth Interceptors.\n     * `:core:database`: Room DB المشتركة والـ DAOs.\n     * `:core:model`: الـ Shared Domain Entities.\n   - **App Layer (`:app`)**: موديول تجميعي خفيف يربط كل الـ Implementations ببعضها عبر Dagger/Hilt دون أن تعرف الميزات كود بعضها الداخلي.\n\n"
            "3. إدارة التنقل بين الشاشات دون اقتران (Decoupled Navigation):\n   - استخدام Navigation Contracts أو Deep Links أو Service Locator لتوجيه المستخدمين بين الميزات دون أن يستورد موديول الشاشة أ موديول الشاشة ب."
        ),
        "practical_walkthrough": (
            "تصميم نمط Feature API/Impl لعزل الميزات وتسريع التجميع ومنع التبعيات الدائرية:\n"
            "```kotlin\n"
            "// في موديول :feature:payment:api (لا يعتمد على أي موديول خارجي):\n"
            "interface PaymentFeatureLauncher {\n"
            "    fun launchPaymentFlow(orderId: String, amountCents: Long)\n"
            "}\n"
            "\n"
            "// في موديول :feature:cart:impl (يعتمد فقط على :feature:payment:api):\n"
            "class CartViewModel @Inject constructor(\n"
            "    private val paymentLauncher: PaymentFeatureLauncher // حقن عبر الـ Interface بدون معرفة تفاصيل PaymentActivity\n"
            ") : ViewModel() {\n"
            "    fun onCheckoutClicked(orderId: String, amount: Long) {\n"
            "        paymentLauncher.launchPaymentFlow(orderId, amount)\n"
            "    }\n"
            "}\n"
            "\n"
            "// في موديول :feature:payment:impl (ينفذ الـ API):\n"
            "class PaymentFeatureLauncherImpl @Inject constructor(\n"
            "    @ApplicationContext private val context: Context\n"
            ") : PaymentFeatureLauncher {\n"
            "    override fun launchPaymentFlow(orderId: String, amountCents: Long) {\n"
            "        val intent = Intent(context, InternalPaymentActivity::class.java).apply {\n"
            "            flags = Intent.FLAG_ACTIVITY_NEW_TASK\n"
            "            putExtra(\"order_id\", orderId)\n"
            "            putExtra(\"amount\", amountCents)\n"
            "        }\n"
            "        context.startActivity(intent)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design a scalable multi-feature app by splitting features into separate :api and :impl modules, isolating shared functionality into low-level :core modules, enforcing unidirectional dependency rules, using dependency injection to bind interfaces at the root :app module, and decoupling navigation via contract interfaces or deep links.",
        "best_answer": (
            "Scaling an Android codebase across multiple autonomous engineering teams requires decoupling compilation and architectural boundaries:\n\n"
            "1. **The Feature API / Implementation Separation**:\n"
            "   - Split each business domain into two modules: `:feature:name:api` and `:feature:name:impl`.\n   - The `:api` module exposes public interfaces, navigation arguments, and lightweight data contracts. Other features depend strictly on `:api`.\n   - The `:impl` module contains internal composables, ViewModels, and data repositories. No other module depends directly on `:impl`.\n\n"
            "2. **Layered Module Hierarchy**:\n"
            "   - **App Layer (`:app`)**: Thin application orchestrator that includes all `:impl` modules and wires Dagger/Hilt dependency graphs.\n   - **Feature Layer (`:feature:*`)**: Isolated vertical slices owning specific user journeys.\n   - **Core Layer (`:core:*`)**: Horizontal building blocks (`:core:network`, `:core:database`, `:core:designsystem`, `:core:common`).\n\n"
            "3. **Decoupled Navigation & Communication**:\n"
            "   - Features navigate to other features via exposed entry-point interfaces or typed deep link contracts, eliminating direct cross-feature class imports.\n\n"
            "4. **Build Performance Optimization**:\n"
            "   - Decoupled modules leverage Gradle build caching, parallel execution, and configuration caching, preventing full-project recompilations when a single feature changes."
        ),
        "deep_answer": (
            "From an organizational and platform engineering perspective, modularization must be protected by governance tooling:\n\n"
            "1. **Enforcing Dependency Direction via Tooling**: Architecture rules rot without automated guardrails. Use Gradle plugins like `dependency-analysis-android-plugin` or custom ArchUnit/Konsist tests to enforce that no feature module ever imports another feature's `:impl` module, and that `:core` modules never depend on `:feature` modules.\n\n"
            "2. **Independent Standalone Sample Apps**: Each major feature module should maintain a lightweight `:feature:name:sample` runnable app module. Developers on the checkout team can run and iterate on their feature in isolation within 5 seconds without compiling the remaining 50 features of the monolithic app.\n\n"
            "3. **Binary Dependency Substitution**: In mega-apps (100+ engineers), build times can be further reduced by substituting local module projects with pre-compiled AAR artifacts hosted on an internal Maven cache for modules outside the engineer's active feature domain."
        ),
        "follow_ups": [
            {
                "question": "What happens if two feature modules have a circular dependency?",
                "answer": "Gradle refuses to build due to circular task graphs; the circular relationship must be broken by extracting the shared contract into an independent :api module or a shared :core module."
            },
            {
                "question": "Why is it dangerous to put all shared models in a single :core:models module?",
                "answer": "It becomes a god-module; modifying any single entity triggers a complete project-wide recompilation across all dependent modules."
            }
        ]
    },
    {
        "id": "SYS-03",
        "arabic_explanation": (
            "كيف تصمم نظام مصادقة وإدارة جلسات وتجديد آمن للتوكنز (Login, Session Management, and Secure Token Refresh) بمستوى إنتاج ضخم؟\n\n"
            "1. دورة حياة الجلسة الآمنة (Session Lifecycle Architecture):\n"
            "   - **Login**: يرسل المستخدم بيانات الاعتماد (أو عبر OAuth2/OIDC/Biometric) إلى السيرفر المشفر، ويعود الـ Backend بزوج توكنز:\n     * **Access Token (قصير العمر - 5 إلى 15 دقيقة)**: يستخدم في ترويسة الطلبات `Authorization: Bearer <token>`.\n     * **Refresh Token (طويل العمر - 14 إلى 30 يوماً)**: يستخدم حصرياً لتجديد الـ Access Token.\n   - **التخزين**: Access Token يُحفظ في الذاكرة (RAM) لتقليل التعرض، و Refresh Token يُشفر عبر Android Keystore AES-GCM ويُخزن في DataStore.\n\n"
            "2. التجديد التلقائي الشفاف (Transparent Token Refresh):\n   - يجب ألا يشعر المستخدم بأي انقطاع عند انتهاء صلاحية الـ Access Token.\n   - نستخدم `okhttp3.Authenticator` الذي يتم استدعاؤه فقط عند تلقي استجابة `HTTP 401 Unauthorized`.\n\n"
            "3. التحديات القاتلة في بيئات الإنتاج وكيفية حلها:\n   - **مشكلة الـ Thundering Herd (عشرات الطلبات المتزامنة)**: عندما تنتهي صلاحية التوكن، قد تعود 5 طلبات متزامنة بـ 401 في نفس اللحظة! إذا حاولت كلها تجديد التوكن، ستحدث فوضى ويفشل الـ Refresh Token Rotation. **الحل**: مزامنة التجديد باستخدام Coroutines `Mutex` لضمان تشغيل طلب تجديد واحد فقط، وإعادة استخدام النتيجة لباقي الطلبات.\n   - **حلقات الـ 401 اللانهائية (Infinite 401 Loop)**: إذا انتهت صلاحية الـ Refresh Token أيضاً، يجب التوقف فوراً ومسح الجلسة وتوجيه المستخدم لواجهة تسجيل الدخول."
        ),
        "practical_walkthrough": (
            "تنفيذ OkHttp Authenticator احترافي مع Mutex متزامن ومعالجة Race Conditions وإعادة المحاولة:\n"
            "```kotlin\n"
            "class ProductionTokenAuthenticator(\n"
            "    private val sessionRepository: SessionRepository,\n"
            "    private val authApi: AuthApiService\n"
            ") : Authenticator {\n"
            "    private val refreshMutex = Mutex()\n"
            "\n"
            "    override fun authenticate(route: Route?, response: Response): Request? {\n"
            "        // 1. منع الحلقات اللانهائية إذا تكرر الفشل أكثر من مرتين:\n"
            "        if (responseCount(response) >= 2) return null\n"
            "\n"
            "        val staleToken = response.request.header(\"Authorization\")?.removePrefix(\"Bearer \")\n"
            "\n"
            "        return runBlocking {\n"
            "            refreshMutex.withLock {\n"
            "                val currentToken = sessionRepository.getAccessToken()\n"
            "                \n"
            "                // 2. إذا كان هناك طلب آخر قد جدد التوكن بالفعل أثناء انتظار هذا الطلب في الـ Mutex:\n"
            "                if (currentToken != null && currentToken != staleToken) {\n"
            "                    return@withLock response.request.newBuilder()\n"
            "                        .header(\"Authorization\", \"Bearer $currentToken\")\n"
            "                        .build()\n"
            "                }\n"
            "\n"
            "                // 3. طلب تجديد التوكن باستخدام الـ Refresh Token المشفر:\n"
            "                val refreshToken = sessionRepository.getRefreshToken() ?: run {\n"
            "                    sessionRepository.forceLogout()\n"
            "                    return@withLock null\n"
            "                }\n"
            "\n"
            "                val refreshResponse = authApi.refreshToken(RefreshTokenRequest(refreshToken))\n"
            "                if (refreshResponse.isSuccessful && refreshResponse.body() != null) {\n"
            "                    val newSession = refreshResponse.body()!!\n"
            "                    sessionRepository.saveTokens(newSession.accessToken, newSession.refreshToken)\n"
            "                    \n"
            "                    response.request.newBuilder()\n"
            "                        .header(\"Authorization\", \"Bearer ${newSession.accessToken}\")\n"
            "                        .build()\n"
            "                } else {\n"
            "                    // فشل الـ Refresh (مثلاً تم إلغاؤه من السيرفر) -> طرد المستخدم فوراً\n"
            "                    sessionRepository.forceLogout()\n"
            "                    null\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "\n"
            "    private fun responseCount(response: Response): Int = generateSequence(response) { it.priorResponse }.count()\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design secure authentication using short-lived access tokens and Keystore-encrypted refresh tokens. Intercept 401 responses via OkHttp's Authenticator, coordinate concurrent refresh requests using a mutex to prevent thundering-herd issues, support refresh token rotation, and clear session state deterministically when refresh fails.",
        "best_answer": (
            "A production-grade mobile authentication system must handle transient concurrency, key security, and automatic recovery:\n\n"
            "1. **Tiered Token Architecture**:\n"
            "   - **Access Token (Short-lived, ~5-15 min)**: Passed in standard HTTP `Authorization: Bearer` headers. Kept primarily in volatile memory or encrypted DataStore.\n   - **Refresh Token (Long-lived, ~14-30 days)**: Stored encrypted using Android Keystore AES-GCM in private storage.\n\n"
            "2. **Transparent Refresh via OkHttp Authenticator**:\n"
            "   - Attach an `Authenticator` implementation to the primary `OkHttpClient`. When any endpoint returns `401 Unauthorized`, OkHttp automatically triggers this handler.\n\n"
            "3. **Concurrency & Thundering-Herd Synchronization**:\n"
            "   - When multiple parallel requests fail simultaneously with 401, they hit `authenticate()` concurrently. A synchronized `Mutex` serializes execution. The first thread completes the refresh; subsequent threads observe that the current token has already updated and immediately replay with the new token without issuing duplicate refresh calls.\n\n"
            "4. **Terminal Failure Handling**:\n"
            "   - If the refresh token has expired, been revoked, or fails with 401/403, the authenticator returns `null`, wipes local credentials from Keystore and DataStore, and emits an unauthenticated session event to navigate to Login."
        ),
        "deep_answer": (
            "From an enterprise platform design perspective, session management extends beyond simple HTTP headers:\n\n"
            "1. **Refresh Token Rotation (RTR) & Compromise Detection**: Each refresh cycle issues both a new access token and a new refresh token, immediately invalidating the old refresh token on the server. If an attacker intercepts and attempts to use an already-rotated refresh token, the backend detects replay fraud and terminates all sessions across all devices for that user account.\n\n"
            "2. **Cryptographic Token Binding (DPoP)**: In high-security banking architectures, access tokens are cryptographically bound to a device-generated asymmetric EC keypair in Android Keystore. The client signs an HTTP header containing the target URL and a server nonce, ensuring intercepted tokens cannot be replayed from other clients.\n\n"
            "3. **Multi-Process & Global Session State Broadcast**: If an app utilizes multiple processes (e.g. background sync or media playback services), session invalidation must propagate across IPC boundaries using an encrypted ContentProvider or reactive DataStore flows to prevent orphaned background tasks from flooding servers with stale credentials."
        ),
        "follow_ups": [
            {
                "question": "Why should you use an OkHttp Authenticator instead of an Interceptor for refreshing tokens?",
                "answer": "An Interceptor executes on every single request and must inspect response codes manually; an Authenticator is invoked specifically by OkHttp only on 401 responses and natively handles retry loops."
            },
            {
                "question": "What happens if runBlocking in Authenticator blocks an IO thread?",
                "answer": "It blocks one OkHttp background thread during the refresh; because OkHttp thread pools manage network I/O, the UI remains responsive, provided UI operations never block waiting for network responses synchronously."
            }
        ]
    },
    {
        "id": "SYS-04",
        "arabic_explanation": (
            "كيف تصمم نظام Offline-First مع مصدر حقيقة محلي (Single Source of Truth) يضمن تجربة مستخدم سلسة بدون فقدان للبيانات؟\n\n"
            "1. المبدأ المعماري لـ Offline-First:\n"
            "   - **قاعدة البيانات المحلية (Local Room DB) هي مصدر الحقيقة الوحيد (Single Source of Truth - SSOT)**.\n   - واجهة المستخدم (UI) لا تطلب البيانات من الشبكة مباشرة أبداً؛ بل تستمع (Observe) لـ `Flow<List<Item>>` صادر من قاعدة البيانات المحلية دائماً.\n   - عمليات التحديث والإنشاء تُكتب أولاً في قاعدة البيانات المحلية، مما يجعل استجابة الـ UI فورية (Optimistic Updates).\n\n"
            "2. محرك المزامنة (Synchronization Engine & Outbox Pattern):\n   - **Outbox Pattern للعمليات المعلقة**: عند قيام المستخدم بإجراء (مثل كتابة تعليق أو إرسال رسالة) أثناء انقطاع الإنترنت:\n     * يُحفظ الكائن في جدول الـ DB المحلي مع حالة مزامنة: `SYNC_STATUS = PENDING` ومُعرّف محلي مؤقت (`client_id = UUID()`).\n     * يُعرض العنصر فوراً في الـ UI مع أيقونة ساعة صغيرة (Pending).\n     * تضاف المهمة إلى جدول طابور المزامنة `sync_actions_queue`.\n   - **المزامنة في الخلفية عبر WorkManager**: يقوم `WorkManager` بمراقبة اتصال الشبكة (`NetworkType.CONNECTED`) وتنفيذ المهام المعلقة بالترتيب، وإرسالها للسيرفر، ثم تحديث الـ ID المحلي بمعرف السيرفر وتغيير الحالة إلى `SYNC_STATUS = SYNCED`.\n\n"
            "3. فض النزاعات (Conflict Resolution Strategies):\n   - **Last-Write-Wins (LWW) عبر Timestamps**: الحل الأبسط ولكن قد يفقد بيانات إذا لم تكن الساعات متزامنة.\n   - **Vector Clocks / Version Numbers**: السيرفر يرفض التعديل إذا كان رقم الإصدار قديماً ويطلب من العميل دمج البيانات (Merge).\n   - **CRDTs (Conflict-free Replicated Data Types)**: للبيانات التشاركية المعقدة (مثل المستندات النصية المشتركة)."
        ),
        "practical_walkthrough": (
            "تنفيذ نمط الـ Outbox المحلي مع Room وتحديثات الواجهة الفورية (Optimistic UI) وإعادة المحاولة:\n"
            "```kotlin\n"
            "// 1. كيان قاعدة البيانات يمثل مصدر الحقيقة مع حالة المزامنة:\n"
            "@Entity(tableName = \"notes\")\n"
            "data class NoteEntity(\n"
            "@PrimaryKey val localId: String = UUID.randomUUID().toString(),\n"
            "    val remoteId: String? = null,\n"
            "    val content: String,\n"
            "    val syncStatus: SyncStatus = SyncStatus.PENDING,\n"
            "    val updatedAt: Long = System.currentTimeMillis()\n"
            ")\n"
            "\n"
            "enum class SyncStatus { SYNCED, PENDING, FAILED }\n"
            "\n"
            "// 2. مستودع يضمن التحديث الفوري المحلي وتفويض المزامنة للـ WorkManager:\n"
            "class OfflineFirstNoteRepository @Inject constructor(\n"
            "    private val noteDao: NoteDao,\n"
            "    private val workManager: WorkManager\n"
            ") {\n"
            "    // الـ UI يستمع لقاعدة البيانات فقط\n"
            "    val allNotes: Flow<List<Note>> = noteDao.observeNotes().map { entities -> entities.map { it.toDomain() } }\n"
            "\n"
            "    suspend fun saveNote(content: String) {\n"
            "        // 1. حفظ فوري في قاعدة البيانات المحلية (Optimistic Write)\n"
            "        val newNote = NoteEntity(content = content, syncStatus = SyncStatus.PENDING)\n"
            "        noteDao.insert(newNote)\n"
            "\n"
            "        // 2. جدولة مزامنة عبر WorkManager بشرط توفر شبكة إنترنت\n"
            "        val constraints = Constraints.Builder()\n"
            "            .setRequiredNetworkType(NetworkType.CONNECTED)\n"
            "            .build()\n"
            "\n"
            "        val syncRequest = OneTimeWorkRequestBuilder<SyncNotesWorker>()\n"
            "            .setConstraints(constraints)\n"
            "            .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 10, TimeUnit.SECONDS)\n"
            "            .build()\n"
            "\n"
            "        workManager.enqueueUniqueWork(\"sync_notes_work\", ExistingWorkPolicy.APPEND_OR_REPLACE, syncRequest)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design an offline-first system by treating the local database as the single source of truth that the UI observes reactively. Write user modifications immediately to local storage with pending status flags using an Outbox pattern, and schedule reliable background synchronization via WorkManager with network constraints and explicit conflict resolution rules.",
        "best_answer": (
            "An offline-first mobile architecture treats network connectivity as an intermittent enhancement rather than a prerequisite:\n\n"
            "1. **Local Database as Single Source of Truth (SSOT)**:\n"
            "   - The UI observes Room database tables via reactive Coroutine `Flow`. The UI never awaits remote API responses to render content; it renders immediately from SQLite.\n\n"
            "2. **Optimistic Mutations & The Outbox Pattern**:\n"
            "   - When a user performs an action (create, update, delete), the app immediately writes the mutation to the local database flagged with `SYNC_PENDING` and a client-generated UUID.\n   - The UI reflects the change instantaneously without loading spinners.\n   - A corresponding record is added to an internal `outbox_mutations` queue table.\n\n"
            "3. **Resilient Synchronization via WorkManager**:\n"
            "   - Background workers trigger when network connectivity meets constraints (`NetworkType.CONNECTED`). The worker drains the outbox queue sequentially, dispatches requests to the server with idempotency keys, and updates local records to `SYNCED` with authoritative server IDs.\n\n"
            "4. **Conflict Resolution Policy**:\n"
            "   - In most business apps, implement **Server-Reconciliation with Version Vectors**: the client submits its last-known version. If the server detects a concurrent edit, it merges non-conflicting fields or returns a 409 Conflict, prompting client-side user reconciliation."
        ),
        "deep_answer": (
            "From an advanced distributed systems viewpoint, offline-first mobile clients operate as distributed database nodes:\n\n"
            "1. **Handling Deleted Items (Tombstones)**:\n"
            "   - Never delete rows directly in offline SQLite when a user deletes an item while offline. If deleted locally, subsequent sync pulls from the server will interpret the missing row as 'new' and re-insert it! Mark rows as deleted using **Tombstones** (`is_deleted = true`). The sync worker notifies the server to delete the entity remotely, and only removes the row locally once confirmed.\n\n"
            "2. **Two-Way Delta Synchronization**: Avoid downloading entire datasets. Implement delta sync endpoints accepting `last_sync_timestamp` or pagination cursors. The server returns only mutations (`created`, `updated`, `deleted`) that occurred since that timestamp, drastically reducing bandwidth and battery consumption.\n\n"
            "3. **Queue Compaction & Deduplication**: If an offline user edits the same note 5 times, compact the outbox mutations locally before transmitting, collapsing intermediate updates into a single final payload."
        ),
        "follow_ups": [
            {
                "question": "What is a tombstone in database synchronization?",
                "answer": "A record marked with a deletion flag rather than being physically dropped, allowing synchronization engines to propagate the delete operation to remote servers."
            },
            {
                "question": "Why should local database IDs be client-generated UUIDs rather than auto-incrementing integers?",
                "answer": "Client-generated UUIDs prevent ID collisions across distributed offline devices before entities are assigned authoritative server IDs."
            }
        ]
    },
    {
        "id": "SYS-05",
        "arabic_explanation": (
            "كيف تصمم دورة حياة معاملات دفع قوية ومرنة (Robust Payment Transaction Lifecycle) تمنع السحب المزدوج وتتحمل انقطاع الشبكة؟\n\n"
            "1. التحديات القاتلة في مدفوعات الموبايل:\n   - **مشكلة الانقطاع بعد الخصم (Payment in Flight Network Drop)**: المستخدم ضغط \"ادفع الآن\"، البنك خصم المبلغ، ولكن قبل أن تصل استجابة النجاح للهاتف انقطعت شبكة الإنترنت! إذا ضغط المستخدم \"ادفع\" مجدداً، قد يُخصم منه المبلغ مرتين!\n   - **موت التطبيق أثناء معالجة البوابة (Process Death / Crash)**: إغلاق التطبيق أثناء انتظار تأكيد 3D Secure.\n\n"
            "2. الركائز الهندسية لمعاملات الدفع:\n   - **مفتاح عدم التكرار (Client-Side Idempotency Key)**: لكل عملية دفع يتم توليد `idempotencyKey = UUID()` فريد محلياً وتمريره في هيدر الطلب `Idempotency-Key: <uuid>`. إذا أعاد التطبيق إرسال نفس الطلب 10 مرات بسبب مشاكل الشبكة، يدرك السيرفر فوراً أنه نفس الطلب ويعيد نتيجة المعاملة الأولى دون تكرار الخصم!\n   - **آلة حالات المعاملة الصريحة (Explicit State Machine)**:\n     `INITIATED -> PROCESSING -> AUTHORIZED -> CAPTURED` أو `FAILED`.\n   - **المطابقة التلقائية والاستعلام السيرفري (Polling / Reconciliation)**: عند انقطاع الاتصال أو إعادة فتح التطبيق بعد عطل، لا يعيد التطبيق محاولة الدفع، بل يستعلم عن حالة المعاملة الأصلية: `GET /payments/order/{orderId}` لمعرفة هل تم الخصم أم لا.\n   - **Webhooks ومطابقة السيرفر**: السيرفر يعتمد على إشعارات Webhooks المباشرة من بوابة الدفع (Stripe/PayPal) كمصدر الحقيقة النهائي وليس استجابة تطبيق الموبايل."
        ),
        "practical_walkthrough": (
            "تصميم نظام دفع قوي يعتمد على Idempotency Key ومطابقة الحالة عند الفشل وانقطاع الشبكة:\n"
            "```kotlin\n"
            "class PaymentTransactionCoordinator @Inject constructor(\n"
            "    private val paymentApi: PaymentApiService,\n"
            "    private val paymentDao: PaymentTransactionDao\n"
            ") {\n"
            "    suspend fun executePayment(orderId: String, amountCents: Long): PaymentResult {\n"
            "        // 1. جلب أو إنشاء سجل المعاملة محلياً بمفتاح عدم تكرار فريد وثابت:\n"
            "        val existingTx = paymentDao.getTransactionForOrder(orderId)\n"
            "        val idempotencyKey = existingTx?.idempotencyKey ?: UUID.randomUUID().toString()\n"
            "\n"
            "        if (existingTx == null) {\n"
            "            paymentDao.insert(PaymentRecord(orderId, idempotencyKey, status = PaymentStatus.PENDING))\n"
            "        }\n"
            "\n"
            "        return try {\n"
            "            // 2. إرسال طلب الدفع مع الـ Idempotency-Key في الهيدر\n"
            "            val response = paymentApi.chargeOrder(\n"
            "                idempotencyKey = idempotencyKey,\n"
            "                request = ChargeRequest(orderId, amountCents)\n"
            "            )\n"
            "\n"
            "            paymentDao.updateStatus(orderId, PaymentStatus.COMPLETED)\n"
            "            PaymentResult.Success(response.transactionId)\n"
            "        } catch (e: IOException) {\n"
            "            // 3. انقطاع الشبكة أثناء الدفع! لا تعيد المحاولة بالدفع؛ استعلم عن الحالة السيرفرية:\n"
            "            reconcilePaymentStatus(orderId, idempotencyKey)\n"
            "        }\n"
            "    }\n"
            "\n"
            "    private suspend fun reconcilePaymentStatus(orderId: String, idempotencyKey: String): PaymentResult {\n"
            "        return try {\n"
            "            val statusResponse = paymentApi.queryPaymentStatus(idempotencyKey)\n"
            "            if (statusResponse.isPaid) {\n"
            "                paymentDao.updateStatus(orderId, PaymentStatus.COMPLETED)\n"
            "                PaymentResult.Success(statusResponse.transactionId)\n"
            "            } else {\n"
            "                PaymentResult.PendingResolution\n"
            "            }\n"
            "        } catch (e: Exception) {\n"
            "            PaymentResult.NetworkErrorRequiresCheck\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design a robust payment lifecycle by attaching a client-generated UUID idempotency key to each transaction, enforcing an explicit state machine, and never blindly retrying failed charges. If a network drop occurs in-flight, query the backend payment status using the idempotency key to reconcile transaction state without double-charging.",
        "best_answer": (
            "Payment flows require zero-tolerance for duplicate charges and resilient handling of network failures:\n\n"
            "1. **Client-Generated Idempotency Keys**:\n"
            "   - Before dispatching a charge request, generate a cryptographically unique `idempotencyKey = UUID()` and persist it locally in Room associated with the order ID.\n   - Transmit this key in the HTTP header (`Idempotency-Key: <uuid>`). If network drops occur and the request is retried, payment gateways (e.g. Stripe, Adyen) recognize the key and return the original transaction receipt without re-executing charges.\n\n"
            "2. **State Machine Modeling**:\n"
            "   - Model the lifecycle with explicit states: `Created -> PaymentMethodAttached -> ActionRequired (3DS) -> Processing -> Succeeded / Failed`.\n\n"
            "3. **In-Flight Network Disconnection Recovery (Reconciliation)**:\n"
            "   - When an HTTP timeout occurs, the client does not know whether the charge succeeded on the gateway. **Never retry the charge mutation directly**. Instead, trigger a reconciliation query (`GET /payments/reconcile?key=<idempotencyKey>`) to retrieve the authoritative state.\n\n"
            "4. **Server-to-Server Webhook Authority**:\n"
            "   - The backend must not consider orders finalized solely because the mobile client returned success. Final order fulfillment is unlocked exclusively via authenticated server-side webhooks from the payment provider."
        ),
        "deep_answer": (
            "From a staff architecture perspective, payment systems require handling edge cases in client-side lifecycle and user interaction:\n\n"
            "1. **UI Double-Tap & Concurrency Guards**: Prevent duplicate button clicks by disabling the UI immediately and using reactive StateFlow debounce mechanisms. The `executePayment()` method must be bounded by an in-memory Mutex to block concurrent triggers for the same order.\n\n"
            "2. **3D Secure / Biometric Process Death**: When navigating to a 3DS webview or external banking app, the host Android OS may kill the main application under memory pressure. The app must persist order state and idempotency keys in persistent Room storage so that upon returning via Deep Link (`myapp://payment-return`), the activity reconstructs state and polls the backend for final status.\n\n"
            "3. **Telemetry & PCI Auditing**: Mask PAN numbers (showing only first 6/last 4) in all UI logs, and completely eliminate CVV/CVC persistence from memory and storage post-tokenization."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between authorization and capture in payments?",
                "answer": "Authorization holds the funds on the customer's card; Capture actually transfers the money to the merchant's account."
            },
            {
                "question": "Why should the client never generate the charge amount directly?",
                "answer": "To prevent tampering; the client submits the order ID, and the server computes the authoritative amount from verified database inventory."
            }
        ]
    },
    {
        "id": "SYS-06",
        "arabic_explanation": (
            "كيف تصمم نظام تخزين مؤقت (Caching)، تقسيم صفحات (Pagination)، ومزامنة البيانات عن بُعد (Remote Synchronization)؟\n\n"
            "1. استراتيجيات التخزين المؤقت (Multi-Tier Caching Architecture):\n   - **L1 In-Memory Cache (RAM)**: سريع جداً (ميكروثانية) ومناسب للصور والأشياء النشطة في الـ UI، ولكنه يموت بموت التطبيق. نستخدم `LruCache` بحجم محدد.\n   - **L2 Persistent Storage (Disk - Room SQLite)**: يحتفظ بالبيانات عبر جلسات التطبيق والـ Process Death. يعمل كـ Single Source of Truth.\n   - **HTTP Cache Headers (OkHttp Cache)**: احترام هيدرز السيرفر (`ETag`, `Cache-Control: max-age`, `If-None-Match: 304 Not Modified`) لمنع إعادة تحميل بيانات لم تتغير.\n\n"
            "2. تقسيم الصفحات الحديث (Pagination via Jetpack Paging 3):\n   - **Keyset / Cursor-Based Pagination**: أفضل بكثير من Offset/Limit التقليدي لأن الـ Offset يعاني من مشاكل تكرار العناصر أو تفويتها عند إضافة عناصر جديدة في أول القائمة أثناء تصفح المستخدم.\n   - **RemoteMediator**: الجسر الهندسي في Paging 3 الذي يراقب نهاية القائمة في الـ Room DB ويقوم بطلب الصفحة التالية من الـ Network، ثم حفظها في Room، فتقوم Room بتحديث الـ UI تلقائياً بسلاسة وبدون أي فجوات.\n\n"
            "3. سياسة تفريغ الذاكرة المؤقتة (Cache Invalidation & Eviction):\n   - مسح العناصر القديمة بعد فترة زمنية (Time-To-Live - TTL).\n   - وضع سقف أعلى لحجم الكاش على القرص (مثلاً 200MB)، وحذف أقدم العناصر عند الوصول للحد الأقصى (Least Recently Used - LRU)."
        ),
        "practical_walkthrough": (
            "تنفيذ Paging 3 مع RemoteMediator ومصدر حقيقة محلي في Room ومزامنة شبكة ذكية:\n"
            "```kotlin\n"
            "@OptIn(ExperimentalPagingApi::class)\n"
            "class ArticleRemoteMediator(\n"
            "    private val database: AppDatabase,\n"
            "    private val apiService: ArticleApiService\n"
            ") : RemoteMediator<Int, ArticleEntity>() {\n"
            "    private val articleDao = database.articleDao()\n"
            "    private val remoteKeyDao = database.remoteKeyDao()\n"
            "\n"
            "    override suspend fun load(\n"
            "        loadType: LoadType,\n"
            "        state: PagingState<Int, ArticleEntity>\n"
            "    ): MediatorResult {\n"
            "        return try {\n"
            "            // 1. تحديد رقم الصفحة المطلوبة بناءً على نوع الـ LoadType والـ Keys المحفوظة:\n"
            "            val page = when (loadType) {\n"
            "                LoadType.REFRESH -> 1\n"
            "                LoadType.PREPEND -> return MediatorResult.Success(endOfPaginationReached = true)\n"
            "                LoadType.APPEND -> {\n"
            "                    val remoteKey = getRemoteKeyForLastItem(state)\n"
            "                    val nextKey = remoteKey?.nextPage ?: return MediatorResult.Success(endOfPaginationReached = remoteKey != null)\n"
            "                    nextKey\n"
            "                }\n"
            "            }\n"
            "\n"
            "            // 2. جلب البيانات من الشبكة:\n"
            "            val response = apiService.getArticles(page = page, pageSize = state.config.pageSize)\n"
            "            val endOfPaginationReached = response.articles.isEmpty()\n"
            "\n"
            "            // 3. كتابة البيانات ومفاتيح الصفحات في Room ضمن Transaction ذرية:\n"
            "            database.withTransaction {\n"
            "                if (loadType == LoadType.REFRESH) {\n"
            "                    remoteKeyDao.clearRemoteKeys()\n"
            "                    articleDao.clearAll()\n"
            "                }\n"
            "                val nextKey = if (endOfPaginationReached) null else page + 1\n"
            "                remoteKeyDao.insertAll(response.articles.map { ArticleRemoteKey(it.id, nextKey) })\n"
            "                articleDao.insertAll(response.articles.map { it.toEntity() })\n"
            "            }\n"
            "\n"
            "            MediatorResult.Success(endOfPaginationReached = endOfPaginationReached)\n"
            "        } catch (e: Exception) {\n"
            "            MediatorResult.Error(e)\n"
            "        }\n"
            "    }\n"
            "\n"
            "    private suspend fun getRemoteKeyForLastItem(state: PagingState<Int, ArticleEntity>): ArticleRemoteKey? {\n"
            "        return state.pages.lastOrNull { it.data.isNotEmpty() }?.data?.lastOrNull()?.let {\n"
            "            remoteKeyDao.getRemoteKeyByArticleId(it.id)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design caching and pagination using a multi-tiered architecture: L1 in-memory LruCache, L2 persistent Room database as the single source of truth, and HTTP ETag caching. Implement pagination using Jetpack Paging 3 with RemoteMediator and cursor keys to seamlessly stream network pages directly into the local database.",
        "best_answer": (
            "Designing scalable pagination and caching balances UI responsiveness, memory limits, and data freshness:\n\n"
            "1. **Multi-Tiered Cache Architecture**:\n"
            "   - **L1 Memory (LruCache)**: Fast access for decoded bitmaps and active view models; bounded by a strict memory cap (e.g. 25% of available heap).\n   - **L2 Disk (Room Database)**: Persistent single source of truth surviving process death.\n   - **L3 HTTP Layer**: Leverage OkHttp's disk cache with `ETag` and `If-None-Match` to avoid re-downloading unmodified server payloads (`304 Not Modified`).\n\n"
            "2. **Cursor-Based Pagination with Jetpack Paging 3**:\n"
            "   - Avoid traditional `offset/limit` pagination because inserting new items at the head of a live feed causes duplicate items or skipped records during scrolling. Use cursor keys (timestamps or opaque server tokens).\n   - Use `RemoteMediator` to coordinate between network requests and the database. The mediator triggers network loads only when the user approaches the end of cached content, persisting pages directly to Room in an atomic transaction.\n\n"
            "3. **Cache Eviction Strategy**:\n"
            "   - Enforce an LRU eviction policy with a 200MB ceiling or TTL expiration. When refreshing lists, keep the top N items and evict stale records beyond page 5 to conserve device storage."
        ),
        "deep_answer": (
            "From an advanced performance and memory perspective, pagination architectures must prevent memory leaks and UI stutter:\n\n"
            "1. **Paging 3 Flow Lifecycle & Invalidation**: Expose paged streams as `Flow<PagingData<Item>>` cached in `viewModelScope` using `.cachedIn(viewModelScope)`. This ensures that screen rotations or configuration changes do not re-fetch or re-paginate data from scratch, retaining the exact scroll position in Compose `LazyColumn`.\n\n"
            "2. **Boundary Conditions & Placeholders**: Enable placeholders in `PagingConfig` when list items have fixed heights. This allows `LazyColumn` to allocate scrollbar travel accurately without jumping or layout thrashing when new pages append.\n\n"
            "3. **Network Resilience & Partial Failures**: If a page fails to load, `RemoteMediator` returns `MediatorResult.Error(e)`. The UI catches this in `CombinedLoadStates.append` and renders a retry button at the bottom of the list without wiping the already-loaded items from the screen."
        ),
        "follow_ups": [
            {
                "question": "Why is .cachedIn(viewModelScope) essential in Paging 3?",
                "answer": "It caches the active PagingData stream across configuration changes so that ViewModels do not trigger a fresh collection or recreate pages on screen rotation."
            },
            {
                "question": "What is the difference between PagingSource and RemoteMediator?",
                "answer": "PagingSource loads data from a single data source (either memory or DB); RemoteMediator coordinates loading from network into a local database source of truth."
            }
        ]
    },
    {
        "id": "SYS-07",
        "arabic_explanation": (
            "كيف تصمم نظام إشعارات (Push Notifications) مع روابط عميقة (Deep Links) يتعامل مع كل حالات فتح التطبيق (Cold, Warm, Background)؟\n\n"
            "1. معمارية تدفق الإشعارات في أندرويد:\n   - **Data Messages vs. Notification Messages في FCM**:\n     * **Notification Messages**: إذا كان التطبيق في الخلفية، يعرض النظام الإشعار في الـ System Tray تلقائياً دون استدعاء كودك، ويمرر الـ Intent عند نقر المستخدم فقط.\n     * **Data Messages (المفضلة هندسياً)**: يُستدعى `FirebaseMessagingService.onMessageReceived()` دائماً في كود تطبيقك سواء كان التطبيق مفتوحاً أو في الخلفية، مما يسمح لك ببناء إشعار مخصص، تشفير البيانات، والتحكم التام بالـ PendingIntent.\n\n"
            "2. تصميم الـ Deep Link Router الموحد:\n   - **تجنب الفخ الشائع**: فتح الشاشة المستهدفة مباشرة (مثل شاشة تفاصيل الطلب `OrderDetailsActivity`) بشكل منعزل! إذا ضغط المستخدم على زر الرجوع (Back Button)، يُغلق التطبيق فوراً ويخرج للشاشة الرئيسية للهاتف بدلاً من الرجوع للـ Home Screen!\n   - **الحل عبر TaskStackBuilder**: بناء الـ Back Stack برمجياً بحيث يضمن أن الرجوع من شاشة الطلب يعود إلى شاشة قائمة الطلبات ثم الـ Home Screen.\n\n"
            "3. التعامل مع حالات الـ Cold Start والمصادقة (Auth State Guard):\n   - إذا نقر المستخدم على إشعار بتفاصيل معاملة بنكية ولكن جلسته منتهية (Unauthenticated):\n   - يجب أن يوجهه الـ Router لشاشة تسجيل الدخول أولاً، مع حفظ الـ Deep Link كـ Pending Navigation Destination، وبعد نجاح الدخول يتم توجيهه تلقائياً للهدف الأصلي."
        ),
        "practical_walkthrough": (
            "تنفيذ معمارية توجيه الإشعارات وبناء الـ Back Stack وحماية مسارات المصادقة:\n"
            "```kotlin\n"
            "class PushNotificationHandler(private val context: Context) {\n"
            "    fun showOrderNotification(orderId: String, title: String, message: String) {\n"
            "        // 1. إنشاء Intent الشاشة المستهدفة مع معرّف الطلب:\n"
            "        val targetIntent = Intent(context, OrderDetailsActivity::class.java).apply {\n"
            "            putExtra(\"extra_order_id\", orderId)\n"
            "        }\n"
            "\n"
            "        // 2. استخدام TaskStackBuilder لبناء الـ Back Stack الطبيعي (Home -> Orders -> OrderDetails):\n"
            "        val pendingIntent = TaskStackBuilder.create(context).run {\n"
            "            // إضافة الكلاس الأم تلقائياً كما هو معرف في AndroidManifest أو يدوياً:\n"
            "            addNextIntentWithParentStack(targetIntent)\n"
            "            getPendingIntent(\n"
            "                orderId.hashCode(),\n"
            "                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE\n"
            "            )\n"
            "        }\n"
            "\n"
            "        // 3. بناء الإشعار وعرضه عبر NotificationManager\n"
            "        val notification = NotificationCompat.Builder(context, \"orders_channel\")\n"
            "            .setSmallIcon(R.drawable.ic_notification)\n"
            "            .setContentTitle(title)\n"
            "            .setContentText(message)\n"
            "            .setContentIntent(pendingIntent)\n"
            "            .setAutoCancel(true)\n"
            "            .build()\n"
            "\n"
            "        NotificationManagerCompat.from(context).notify(orderId.hashCode(), notification)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design notifications using FCM data-payload messages for deterministic client processing. Construct synthetic back stacks using TaskStackBuilder so pressing Back navigates to parent screens rather than exiting the app. Intercept routing through an AuthGuard to handle expired sessions before resuming deep link navigation.",
        "best_answer": (
            "Designing a reliable push notification and deep linking system requires coordinating across background delivery, synthetic navigation hierarchies, and session states:\n\n"
            "1. **FCM Payload Strategy**:\n"
            "   - Prefer FCM **Data Messages** over standard Notification messages. Data messages invoke `onMessageReceived()` deterministically regardless of whether the app is in foreground, background, or killed, allowing client decryption, local database caching, and custom notification rendering.\n\n"
            "2. **Synthetic Back Stack (TaskStackBuilder)**:\n"
            "   - Direct navigation to a deep link destination creates a broken back stack where pressing the system Back button terminates the application. Use `TaskStackBuilder.create(context).addNextIntentWithParentStack(targetIntent)` to synthesize a natural navigation path (e.g., Home -> Orders -> OrderDetail).\n\n"
            "3. **Authentication & Session Interception (AuthGuard)**:\n"
            "   - When an unauthenticated or logged-out user clicks a sensitive push notification, the deep link router must store the pending destination in memory/DataStore, redirect the user through the Login/MFA flow, and resume navigation to the original deep link target upon successful authentication."
        ),
        "deep_answer": (
            "From a staff-level systems perspective, deep link architectures must support single-activity Compose routing and cold-boot resilience:\n\n"
            "1. **Single-Activity Jetpack Compose Routing**: In modern Single-Activity apps, route deep links to a single `MainActivity` with `launchMode=\"singleTask\"`. Override `onNewIntent(intent: Intent?)` to capture incoming notifications when the app is already running, updating a reactive `NavigationEvents` channel consumed by the top-level Compose `NavHost`.\n\n"
            "2. **Cold Start Race Conditions**: During a cold launch triggered by a notification tap, the app must initialize dependency graphs, load remote feature flags, and restore session credentials before executing the navigation transition. Queue the pending deep link event in an application-scoped state machine until baseline startup initialization signals readiness.\n\n"
            "3. **Deep Link Security & Parameter Sanitization**: Treat all intent parameters as untrusted external input. Validate UUID formats, sanitize URIs, and prevent open redirects where malicious URLs could instruct the app to launch arbitrary internal activities or WebViews."
        ),
        "follow_ups": [
            {
                "question": "What happens if a notification uses FLAG_ACTIVITY_NEW_TASK without TaskStackBuilder?",
                "answer": "The target Activity opens as a standalone task root; pressing Back exits to the Android home launcher rather than parent screens."
            },
            {
                "question": "How do you handle push notifications when the user is actively viewing the screen that the notification refers to?",
                "answer": "Detect the active foreground screen; suppress the system tray notification, update the live UI data directly via StateFlow, and optionally show a subtle in-app snackbar."
            }
        ]
    },
    {
        "id": "SYS-08",
        "arabic_explanation": (
            "كيف تصمم نظام Feature Flags و Staged Rollout يدعم الطرح التدريجي، الإلغاء الفوري (Kill Switch)، والعمل Offline؟\n\n"
            "1. أهداف نظام الـ Feature Flags في تطبيقات الموبايل:\n   - **فصل النشر عن الإطلاق (Decouple Deployment from Release)**: دمج الكود الجديد باستمرار في الفرع الرئيسي ونشره في الـ APK وهو معطل، ثم تفعيله بضغطة زر من لوحة التحكم.\n   - **الإطلاق التدريجي (Staged Rollout & Percentage Targeting)**: تفعيل الميزة لـ 5% من المستخدمين، ثم 25%، ثم 100% مع مراقبة تقارير الأعطال (Crashes) ومعدل الأداء.\n   - **مفتاح الإيقاف الطارئ (Remote Kill Switch)**: تعطيل أي ميزة بها ثغرة أمنية أو خطأ قاتل فوراً في ثوانٍ دون الحاجة لإطلاق تحديث جديد على متجر التطبيقات.\n\n"
            "2. المعمارية الهندسية لنظام الـ Flags:\n   - **التخزين الهجين (Multi-Layer Flag Evaluation)**:\n     * **Default In-App Values (القيم المدمجة في الكود)**: تُستخدم في أول فتحة للتطبيق أو عند غياب الاتصال بالإنترنت.\n     * **Disk-Cached Values (DataStore / SharedPreferences)**: تحتفظ بآخر قيم تم جلبها من السيرفر لتعمل بشكل فوري ومستقر عند فتح التطبيق (No UI Blocking).\n     * **Remote Sync (Firebase Remote Config / LaunchDarkly)**: جلب القيم الجديدة في الخلفية وتطبيقها في أوقات آمنة.\n\n"
            "3. مشكلة التبديل أثناء عمل الواجهة (Mid-Session Flag Changes):\n   - **فخ خطير**: تفعيل Flag أثناء استخدام المستخدم للتطبيق، مما يؤدي إلى تغيير شكل الواجهة فجأة أو تعارض في البيانات!\n   - **الحل**: تفعيل سياسة **Fetch Now, Activate on Next Launch** أو تثبيت قيم الـ Flags للجلسة الحالية (Session-Bound Flags) لمنع التذبذب."
        ),
        "practical_walkthrough": (
            "تصميم نظام Feature Flags احترافي مع قيم افتراضية وتخزين محلي ومفتاح إلغاء طارئ:\n"
            "```kotlin\n"
            "enum class FeatureKey(val defaultValue: Boolean) {\n"
            "    NEW_CHECKOUT_FLOW(false),\n"
            "    BIOMETRIC_AUTH(true),\n"
            "    DYNAMIC_DISCOUNT_BANNER(false)\n"
            "}\n"
            "\n"
            "class FeatureFlagManager @Inject constructor(\n"
            "    private val dataStore: DataStore<Preferences>,\n"
            "    private val remoteConfigClient: FirebaseRemoteConfig\n"
            ") {\n"
            "    // ذاكرة سريعة في الـ RAM لتقييم الـ Flags بشكل متزامن وبدون I/O delay في الـ Composables\n"
            "    private val activeFlags = ConcurrentHashMap<FeatureKey, Boolean>()\n"
            "\n"
            "    suspend fun initialize() {\n"
            "        // 1. تحميل القيم المدمجة الافتراضية أولاً\n"
            "        FeatureKey.values().forEach { key -> activeFlags[key] = key.defaultValue }\n"
            "\n"
            "        // 2. تحميل آخر قيم مخزنة محلياً من DataStore\n"
            "        val cachedPrefs = dataStore.data.first()\n"
            "        FeatureKey.values().forEach { key ->\n"
            "            val stored = cachedPrefs[booleanPreferencesKey(key.name)]\n"
            "            if (stored != null) activeFlags[key] = stored\n"
            "        }\n"
            "    }\n"
            "\n"
            "    fun isEnabled(key: FeatureKey): Boolean = activeFlags[key] ?: key.defaultValue\n"
            "\n"
            "    suspend fun fetchAndCacheLatest() {\n"
            "        try {\n"
            "            // 3. جلب أحدث القيم من السيرفر وحفظها في DataStore للجلسة القادمة (Activate on Next Launch)\n"
            "            val updated = remoteConfigClient.fetch().await()\n"
            "            // حفظ التحديثات في القرص بدون كسر الجلسة الحالية\n"
            "        } catch (e: Exception) {\n"
            "            // الفشل الشبكي لا يؤثر إطلاقاً على عمل التطبيق\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design feature flags using a tiered evaluation model: bundled in-app defaults for zero-latency fallback, persistent local storage for offline tolerance, and background remote fetching. Apply an activate-on-next-launch policy to prevent mid-session UI inconsistencies, and configure high-priority remote kill switches for emergency mitigations.",
        "best_answer": (
            "A production feature flag and staged rollout infrastructure separates deployment from release while insulating the app from network latency:\n\n"
            "1. **Multi-Layered Flag Evaluation**:\n"
            "   - **Static Defaults**: Hardcoded compile-time defaults ensure instant fallback if network or disk fails.\n   - **Local Disk Cache**: Persistent values stored in DataStore allow instant synchronous evaluation on app cold start without blocking UI rendering.\n   - **Remote Provider (Firebase Remote Config / LaunchDarkly)**: Fetches remote updates in the background based on user targeting cohorts and percentage rollouts.\n\n"
            "2. **Activate-On-Next-Launch Policy**:\n"
            "   - Never mutate feature flags dynamically while the user is navigating an active flow. Changing flags mid-session causes jarring UI rebuilds, state fragmentation, or mid-transaction crashes. Fetch updates in the background, cache them locally, and activate on the next application restart.\n\n"
            "3. **Emergency Remote Kill Switch**:\n"
            "   - Reserve a high-priority bypass channel for critical operational kill switches (e.g. disabling a broken payment gateway). Critical kill-switch flags can be observed reactively to terminate broken components immediately."
        ),
        "deep_answer": (
            "From an architectural governance and technical debt standpoint, feature flag systems require strict lifecycle management:\n\n"
            "1. **Flag Expiration & Technical Debt Cleanup**: Flags that remain in codebases indefinitely create exponential combinatorial testing permutations and dead code paths. Enforce an expiration SLA (e.g., maximum 60 days). Once a feature is rolled out to 100% and proven stable, schedule technical debt tickets to delete the flag checks, retire remote configurations, and inline the permanent implementation.\n\n"
            "2. **Consistent Hashing for Percentage Rollouts**: Rollout buckets must be deterministic. Calculate user cohorts using consistent hashing over the `userId` combined with the `flagKey`: `hash(userId + flagKey) % 100 < rolloutPercentage`. This guarantees that an individual user remains in their assigned bucket across app restarts without state drift.\n\n"
            "3. **A/B Testing & Metric Correlation**: Correlate feature flag exposure events directly with analytics pipelines. When a user evaluates a flag, emit an exposure log so data platforms can measure business metric lift (conversion, retention, crashes) between control and treatment groups."
        ),
        "follow_ups": [
            {
                "question": "What is the danger of evaluating remote feature flags synchronously during app launch?",
                "answer": "If the network is slow or the remote config server experiences downtime, app cold start blocks, leading to user drop-off or Android OS ANR crashes."
            },
            {
                "question": "How do you test a feature protected by a feature flag in automated UI tests?",
                "answer": "Inject a mock or fake FeatureFlagManager in test configurations that returns deterministic boolean overrides for targeted flags."
            }
        ]
    }
]


def update_sys_data() -> None:
    data = []
    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    existing_map = {item["id"]: item for item in data}
    for item in SYS_01_08:
        existing_map[item["id"]] = item

    updated = [existing_map[k] for k in sorted(existing_map.keys())]
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions SYS-01 to SYS-08. Total questions: {len(updated)}")


if __name__ == "__main__":
    update_sys_data()

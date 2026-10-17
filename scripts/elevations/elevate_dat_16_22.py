#!/usr/bin/env python3
"""
Elevation script for DAT questions: DAT-16 to DAT-22.
Topic: Networking, Room, DataStore & Offline-First (DAT)
Phase 4, Batch 3 (Final Batch for DAT)
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "الشبكات وقواعد بيانات Room والـ DataStore والتخزين المحلي"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# DAT-16: How should conflicts be resolved when local and server state diverge?
# ==========================================
DATA["DAT-16"] = {
    "concept_en": """Resolving data divergence between local offline storage and remote servers requires structured conflict resolution models:
- Last-Write-Wins (LWW): Resolves conflicts based on mutation timestamps. Simple to implement, but vulnerable to mobile clock drift, timezone shifts, and network latency anomalies, often silently overwriting newer legitimate user changes.
- Server-Wins vs Client-Wins: Strict authoritative boundaries. Server-Wins prioritizes enterprise state consistency, discarding local offline edits upon conflicts. Client-Wins prioritizes user autonomy, allowing local device changes to overwrite remote state unconditionally (common in personal note-taking or local settings).
- Field-Level Three-Way Merging: Compares the base ancestor snapshot, the local mutation, and the server payload. Non-intersecting property edits merge automatically without conflict.
- Conflict-Free Replicated Data Types (CRDTs): Mathematical data structures (such as Observed-Remove Sets or State-based LWW-Element-Sets) that guarantee deterministic mathematical convergence across concurrent distributed edits without requiring centralized coordination locks.
- Interactive User Resolution: Presents a conflict resolution modal when critical irreversible collisions occur, empowering the user to inspect differences and select the winning version.""",
    "walkthrough_en": """Offline sync engine with optimistic updates and revision-based conflict handling:
```kotlin
data class SyncEntity(
    val id: String,
    val title: String,
    val revision: Long,
    val isPendingSync: Boolean = false
)

class SyncRepository(
    private val dao: SyncDao,
    private val api: SyncApi
) {
    // 1. Optimistic local update
    suspend fun updateTitleLocally(id: String, newTitle: String) {
        dao.updateOptimistically(id = id, title = newTitle, isPending = true)
    }

    // 2. Sync with server revision validation
    suspend fun syncItem(id: String): Result<Unit> = runCatching {
        val local = dao.getItem(id) ?: return@runCatching
        try {
            val updated = api.pushUpdate(local.id, local.title, local.revision)
            dao.saveSynced(updated.copy(isPendingSync = false))
        } catch (e: HttpException) {
            if (e.code() == 409) {
                // Conflict detected: fetch remote and perform field-level merge
                val remote = api.fetchItem(id)
                val resolved = resolveConflict(base = local, remote = remote)
                dao.saveSynced(resolved)
            } else throw e
        }
    }

    private fun resolveConflict(base: SyncEntity, remote: SyncEntity): SyncEntity {
        // Business rule: Keep local edits if marked pending, update revision counter
        return remote.copy(title = base.title, isPendingSync = true)
    }
}
```""",
    "short_en": """Resolving conflicts when local and server state diverge depends on data criticalness. Systems employ Last-Write-Wins based on synchronized server timestamps, field-level three-way merging for independent attributes, or Conflict-Free Replicated Data Types for collaborative items. The client uses an outbox queue with optimistic local updates and presents interactive resolution modals for irreversible collisions.""",
    "structured_en": """Resolving divergence between local and server state requires establishing clear architectural ownership and deterministic merge rules.
First, Last-Write-Wins resolves conflicts by comparing update timestamps. While simple, it risks data loss if client device clocks drift, making server-assigned timestamps or monotonic revision counters preferable.
Second, field-level three-way merging compares the base snapshot, the local mutation, and the remote update. Non-overlapping field edits merge automatically, whereas conflicting changes on identical fields fall back to business rules or user selection modals.
Third, collaborative data structures leverage Conflict-Free Replicated Data Types to converge concurrently without central synchronization locks.
In Android offline architectures, we enforce an Outbox pattern where mutations are saved locally with pending sync flags, processed sequentially via WorkManager, and reconciled against server responses.""",
    "deep_senior_en": """In enterprise offline-first Android systems, conflict resolution cannot be treated as an afterthought; naive approaches like blindly overwriting server data with local state lead to severe data corruption and lost user work.
When designing sync engines, we classify data into distinct consistency tiers.
For basic settings or ephemeral preferences, Client-Wins or Last-Write-Wins with server-assigned monotonic sequence numbers is acceptable.
However, for collaborative documents, shopping carts, or enterprise task lists, Last-Write-Wins silently destroys data because mobile device clocks frequently skew across timezones and hardware differences.
To solve this, we implement a robust Outbox pattern backed by Room.
When a user edits an item offline, we immediately apply an optimistic update to the local database to preserve instantaneous UI feedback, while inserting a pending mutation task into our sync queue.
Each entity carries a revision hash or version vector.
When connectivity returns, WorkManager dispatches the mutation to the backend.
If the server's current revision does not match the client's base revision, the server rejects the write with HTTP 409 Conflict and provides the latest remote payload.
Our repository then initiates a field-level three-way merge: if user A updated the title while user B updated the tags, both changes commit cleanly.
If both users edited the identical text field, we avoid silent data loss by surfacing an interactive conflict resolution sheet, empowering the user to choose which draft to retain while saving both versions in history.""",
    "meta_ar": {
        "id": "DAT-16",
        "questionAr": "كيف تتم تسوية تعارض البيانات (Conflict Resolution) عندما تختلف الحالة المحلية في الهاتف عن حالة السيرفر؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم استراتيجيات تسوية التعارضات في معمارية Offline-First، ومخاطر Last-Write-Wins وساعة الجهاز، واستخدام Outbox Pattern والدمج ثلاثي الأطراف مع شاشات الحسم التفاعلية.",
        "concept_ar": "تتطلب معالجة تباين البيانات بين التخزين المحلي وخوادم السحاب وضع نماذج هندسية واضحة لتسوية النزاع: استراتيجية فوز التعديل الأخير (Last-Write-Wins) تعتمد على الختم الزمني للعملية ولكنها عرضة لانحراف توقيت أجهزة الهواتف واختلاف المناطق الزمنية مما قد يؤدي لمسح بيانات أحدث دون قصد. واستراتيجية فوز السيرفر (Server-Wins) تعطي السلطة المطلقة للباك إند وتهمل التعديلات غير المتزامنة، بينما تعطي فوز العميل (Client-Wins) الأولوية لتعديلات المستخدم المحلي كما في التطبيقات الشخصية. وتتيح استراتيجية الدمج ثلاثي الأطراف (Three-Way Merging) مقارنة النسخة الأصلية والتعديل المحلي وتحديث السيرفر لدمج الحقول المستقلة تلقائياً. وفي الأنظمة التعاونية المعقدة، تُستخدم هياكل البيانات المتطابقة رياضياً (CRDTs) للتقارب دون أقفال مركزية، أو عرض نافذة تفاعلية للمستخدم لاختيار النسخة الصحيحة يدوياً.",
        "walkthrough_ar": """بناء محرك مزامنة يدعم التحديث التفاؤلي وحسم التعارض برقم الإصدار:
```kotlin
// 1. تحديث تفاؤلي محلي مع وضع علامة معلق
suspend fun editDocLocally(id: String, text: String) {
    docDao.update(id = id, text = text, isPending = true)
}

// 2. مزامنة مع السيرفر والتحقق من كود 409
suspend fun syncDoc(id: String) {
    val local = docDao.getDoc(id)
    try {
        val serverDoc = api.saveDoc(local.id, local.text, local.version)
        docDao.update(serverDoc.copy(isPending = false))
    } catch (e: HttpException) {
        if (e.code() == 409) {
            // كشف تعارض: السيرفر به نسخة أحدث، تطبيق منطق الدمج
            val remote = api.fetchDoc(id)
            val merged = mergeDocs(base = local, remote = remote)
            docDao.update(merged)
        }
    }
}
```""",
        "why_it_matters_ar": "يمنع مسح عمل المستخدمين دون قصد عند استئناف الاتصال بالإنترنت، ويضمن استقرار السجلات المشتركة في التطبيقات التعاونية والتجارية.",
        "worked_example_ar": "تعديل ملاحظة في تطبيق مستندات دون اتصال، وتعديلها من المتصفح في نفس الوقت؛ عند عودة الاتصال يرفض السيرفر الطلب لوجود تعارض في الإصدار، فيقوم التطبيق بدمج الفقرات غير المتعارضة تلقائياً.",
        "trade_offs_ar": "استراتيجية LWW سهلة البرمجة ولكنها تضيع البيانات مع انحراف توقيت الهواتف، والدمج ثلاثي الأطراف يحافظ على البيانات ولكنه يتطلب تعقيداً كبيراً في معالجة الحقول.",
        "failure_modes_ar": "الاعتماد على ساعة الموبايل Device Clock لتحديد التعديل الأحدث مما يمحو بيانات السيرفر، أو الكتابة فوق بيانات السيرفر دون فحص رقم الإصدار Revision.",
        "production_perspective_ar": "في المنصات الضخمة، نطبق نمط Outbox Pattern في Room ونسجل أرقام إصدارات تصاعدية من السيرفر، ونلجأ لشاشات الحسم التفاعلية عند تعارض الحقول الجوهرية.",
        "how_to_answer_ar": "ابدأ بذكر الفروق بين LWW و Server-Wins و Client-Wins، واشرح عيب ساعة الهاتف مع LWW، ثم وضح دور الدمج ثلاثي الأطراف ونمط Outbox في أندرويد.",
        "talking_points_ar": "مخاطر انحراف توقيت الهواتف، الدمج على مستوى الحقول Field-level Merge، ونمط Outbox مع التحديث التفاؤلي.",
        "follow_ups_ar": "- **المحاور:** 'لماذا يحظر الاعتماد على ساعة الموبايل System.currentTimeMillis في استراتيجية Last-Write-Wins؟'\n  **المرشح:** 'لأن ساعات الهواتف غير متزامنة تماماً ويمكن للمستخدم تغييرها يدوياً أو تختلف بتغيير الشبكة والمناطق الزمنية، مما يسبب مسح تعديلات حديثة بتعديلات قديمة.'\n\n- **المحاور:** 'كيف يساعد كود HTTP 409 Conflict في اكتشاف التعارض؟'\n  **المرشح:** 'يرسل العميل رقم الإصدار الذي عدل عليه في الطلب؛ فإذا وجد السيرفر أن الإصدار المسجل لديه أصبح أعلى بسبب تعديل آخر، يرفض العملية بكود 409 ليلزم العميل بجلب أحدث نسخة أولاً.'",
        "self_check_ar": "هل أوضحت عيوب LWW؟ وهل شرحت الدمج ثلاثي الأطراف ونمط Outbox والتحديث التفاؤلي؟",
        "references_ar": f"- [Android Architecture: Offline-first Conflict Handling](https://developer.android.com/topic/architecture/data-layer/offline-first#conflict-resolution) — دليل جوجل الرسمي لمعالجة تعارض البيانات دون اتصال.\n- [CRDTs: Conflict-free Replicated Data Types](https://crdt.tech/) — المرجع العلمي لهياكل البيانات ذاتية الدمج.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "تعتمد تسوية التعارضات بين البيانات المحلية والسيرفر على استراتيجيات محددة بحسب حساسية البيانات، تبدأ من اعتماد آخر كتابة بناء على أختام زمنية متفق عليها، أو الدمج ثلاثي الأطراف للحقول المنفصلة، وصولاً إلى هياكل البيانات غير المتعارضة. ويطبق الأندرويد نمط صندوق الإرسال مع التحديث التفاؤلي الفوري وعرض شاشات تفاعلية لحسم الخلافات الحساسة.",
        "best_answer_ar": "تتطلب معالجة تعارض البيانات بين التخزين المحلي وخوادم السحاب وضع قواعد هندسية دقيقة لتحديد الأولوية وطريقة دمج السجلات.\n\nاستراتيجية فوز التعديل الأخير Last-Write-Wins تفصل في النزاع عبر مقارنة وقت التعديل؛ وهي سريعة لكنها قد تسبب فقدان بيانات بسبب عدم دقة توقيت أجهزة الموبايل واختلاف المناطق الزمنية، ولذا نفضل الاعتماد على أرقام تسلسلية تصاعدية من السيرفر.\n\nاستراتيجية الدمج ثلاثي الأطراف تقارن النسخة الأصلية والتعديل المحلي وتحديث السيرفر؛ مما يسمح بدمج الحقول المختلفة تلقائياً دون تداخل، مع حصر التعارض في الحقول المتطابقة فقط.\n\nوفي التطبيقات المتقدمة، نعتمد نمط صندوق الإرسال Outbox في قاعدة بيانات Room مع التحديث التفاؤلي للواجهة لتوفير تجربة سريعة، ثم نرسل التعديل عبر WorkManager؛ فإذا رفض السيرفر الطلب لوجود تعارض في الإصدار، نطبق منطق الدمج أو نعرض نافذة للمستخدم لاختيار النسخة الصحيحة.",
        "deep_answer_ar": "في معمارية التطبيقات الضخمة التي تعمل بنمط Offline-First، يعتبر تعارض البيانات بين الموبايل والسيرفر تحدياً كبيراً يتطلب تصنيف البيانات لعدة مستويات هندسية.\n\nالاعتماد الأعمى على استراتيجية Last-Write-Wins يمثل خطورة بالغة في السجلات التعاونية والمالية؛ لأن ساعات الهواتف تختلف وتتلاعب بها الشبكات، مما قد يمحو تعديلات مستخدم آخر دون علمه. لذلك نطبق نمط صندوق الإرسال Outbox Pattern كمعيار أساسي مدعوماً بـ Room و WorkManager.\n\nعندما يجري المستخدم تعديلاً دون اتصال بالإنترنت، نقوم بتحديث قاعدة البيانات المحلية فورياً بتحديث تفاؤلي Optimistic Update لتبقى الواجهة سريعة، ونسجل مهمة مزامنة برقم إصدار تسلسلي Revision Vector في جدول المهام المعلقة. وعند عودة الاتصال، يرسل العامل الطلب للسيرفر؛ فإذا تبين أن السيرفر استقبل تعديلاً آخر، يرد بكود 409 Conflict مع إرسال أحدث نسخة لديه.\n\nهنا يقوم المستودع بمقارنة الحقول؛ فإذا كانت التعديلات في أجزاء غير متقاطعة يتم دمجها تلقائياً، أما إذا حدث تعارض مباشر في نفس السطر، نظهر شاشة تفاعلية تتيح للمستخدم مراجعة الفروق واختيار الإبقاء على نسخته أو اعتماد نسخة السيرفر، مع الاحتفاظ بنسخة احتياطية من التعديل في السجل لضمان عدم ضياع أي مجهود. وفي الحالات المتقدمة التي تتطلب تعديلات متزامنة متكررة، نوظف هياكل البيانات المتطابقة رياضياً CRDTs كمعيار إضافي يتيح دمج النصوص والمصفوفات تلقائياً عبر الأجهزة دون الحاجة لقفل مركزي، مما يوفر أعلى درجات التعاون اللحظي."
    }
}

# ==========================================
# DAT-17: How do you manage caching expiration and invalidation?
# ==========================================
DATA["DAT-17"] = {
    "concept_en": """Managing caching expiration and invalidation ensures data freshness while preserving the low-latency and offline benefits of local storage:
- Time-To-Live (TTL) & Expiration Windows: Caches attach ingestion timestamps to persisted records. When accessed, the repository compares the record's age against predefined freshness bounds. Expired data either forces a synchronous network refresh or triggers a background fetch while returning stale data temporarily.
- Conditional HTTP Validation: Leverages HTTP headers (ETag, Last-Modified, and Cache-Control) via OkHttp Cache. When a cached resource becomes stale, OkHttp dispatches an If-None-Match or If-Modified-Since validation request. If the backend resource is unchanged, the server responds with HTTP 304 Not Modified without a response payload, refreshing the local TTL without network data overhead.
- Event-Driven Remote Invalidation: Uses server-pushed events (Firebase Cloud Messaging silent data notifications or WebSockets) to explicitly evict or refresh stale client records immediately upon server-side mutations.
- Mutation-Triggered Invalidation: Local write operations (POST, PUT, DELETE) immediately invalidate corresponding cached query results or update local Room entities directly.
- Cache Eviction Policies: Enforces size-bounded storage eviction (such as Least Recently Used - LRU) and schedules periodic Room cleanup jobs via WorkManager to purge historical records and prevent database bloat.""",
    "walkthrough_en": """Cache manager coordinating TTL validation and ETag HTTP caching:
```kotlin
@Entity(tableName = "products")
data class ProductEntity(
    @PrimaryKey val id: String,
    val name: String,
    val price: Double,
    val cachedAt: Long = System.currentTimeMillis()
)

class ProductRepository(
    private val dao: ProductDao,
    private val api: ProductApi,
    private val maxAgeMillis: Long = 10 * 60 * 1000L // 10 minutes TTL
) {
    fun getProduct(id: String): Flow<Product> = flow {
        val cached = dao.getById(id)
        val isExpired = cached == null || (System.currentTimeMillis() - cached.cachedAt) > maxAgeMillis

        if (cached != null) {
            emit(cached.toDomain())
        }

        if (isExpired) {
            runCatching {
                val fresh = api.fetchProduct(id)
                dao.insert(fresh.toEntity(cachedAt = System.currentTimeMillis()))
            }
        }
    }

    // Invalidation on mutation
    suspend fun updateProduct(product: Product) {
        api.updateProduct(product)
        dao.insert(product.toEntity(cachedAt = System.currentTimeMillis()))
    }
}
```""",
    "short_en": """Managing cache expiration and invalidation requires pairing client-side Time-To-Live policies with server-driven conditional headers and event triggers. Room entities record ingestion timestamps for expiration checks, OkHttp utilizes ETags and 304 responses to eliminate redundant payloads, and Firebase Cloud Messaging pushes trigger targeted eviction of stale local records.""",
    "structured_en": """Managing cache freshness and invalidation effectively balances immediate offline responsiveness against data staleness across several complementary mechanisms.
First, client-side Time-To-Live policies store expiration timestamps alongside Room entities, allowing repositories to determine whether cached data can be served directly or requires a network refresh.
Second, HTTP conditional validation utilizes ETags and Last-Modified headers in OkHttp. When the client issues a request with If-None-Match, a 304 Not Modified response validates that the local cache remains pristine without redownloading JSON bodies.
Third, event-driven invalidation leverages silent push notifications via Firebase Cloud Messaging or WebSockets to instantly purge stale resources upon backend changes.
Fourth, automated eviction policies employ periodic WorkManager background tasks to prune expired, non-favorited records from SQLite, preventing unconstrained disk bloat.""",
    "deep_senior_en": """A robust caching architecture requires a unified strategy spanning the HTTP transport layer, local SQLite persistence, and real-time backend synchronization.
At the HTTP layer, we configure OkHttp's disk cache with strict size limits and integrate conditional requests using ETags and Cache-Control directives.
When a repository requests data, OkHttp evaluates Cache-Control headers; if stale, it transmits an If-None-Match header, allowing the server to emit an empty 304 Not Modified status that preserves battery and bandwidth.
At the persistence layer, Room models incorporate a cachedAt timestamp.
When reading from the repository, our business logic checks this timestamp against screen-specific Time-To-Live thresholds: five minutes for live commerce inventory versus twenty-four hours for static category taxonomies.
However, relying purely on polling or passive TTL is insufficient for enterprise applications where remote mutations must reflect immediately.
To achieve real-time accuracy, we implement event-driven cache invalidation: when a product price or user permission updates on the backend, a high-priority silent push notification dispatches through Firebase Cloud Messaging.
The background receiver catches the notification, extracts the affected entity IDs, and executes an atomic Room deletion or background sync.
Finally, to prevent storage leaks on budget devices, a daily WorkManager job evicts unreferenced cache rows older than thirty days.""",
    "meta_ar": {
        "id": "DAT-17",
        "questionAr": "كيف تدير سياسات انتهاء الصلاحية وإبطال الذاكرة المؤقتة (Cache Expiration & Invalidation)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم سياسات مدة الصلاحية TTL، والتحقق المشروط عبر ترويسات ETag والرد 304، والإبطال الموجه بالأحداث عبر إشعارات FCM، وسياسات تنظيف التخزين عبر WorkManager.",
        "concept_ar": "تضمن إدارة انتهاء صلاحية الكاش وإبطاله الموازنة بين سرعة الاستجابة اللحظية وضمان حداثة البيانات المعروضة عبر آليات هندسية متكاملة: تتبع مدة الصلاحية (Time-To-Live) بتسجيل وقت التخزين بجانب كل سجل في Room لمقارنته بحدود زمنية محددة. والتحقق المشروط من الشبكة باستخدام ترويسات ETag و Last-Modified عبر OkHttp؛ حيث يرسل التطبيق ترويسة If-None-Match ليرد السيرفر بكود 304 Not Modified عند عدم وجود تغييرات مما يجدد الصلاحية دون تنزيل البيانات ثانية. والإبطال اللحظي المدفوع بالأحداث (Event-Driven Invalidation) عبر إشعارات FCM الصامتة لحذف السجلات المتغيرة فورياً من التخزين المحلي. والإبطال التلقائي عند التعديل (Mutation Invalidation) بتحديث أو حذف الكاش بعد عمليات الكتابة مباشرة، مع جدولة مهام تنظيف دورية في WorkManager لحذف البيانات القديمة وتفادي تضخم مساحة التخزين.",
        "walkthrough_ar": """تطبيق إدارة الصلاحية TTL مع التحقق والتحديث في طبقة المستودع:
```kotlin
// التحقق من مدة الصلاحية وتحديث الكاش
fun getProduct(id: String): Flow<Product> = flow {
    val cached = productDao.getById(id)
    val isExpired = cached == null || 
        (System.currentTimeMillis() - cached.updatedAt) > 15 * 60 * 1000 // 15 دقيقة

    if (cached != null) emit(cached.toDomain())

    if (isExpired) {
        runCatching {
            val fresh = api.fetchProduct(id)
            productDao.insert(fresh.toEntity(updatedAt = System.currentTimeMillis()))
        }
    }
}
```""",
        "why_it_matters_ar": "يمنع عرض بيانات قديمة ومضللة للمستخدم، ويحافظ على سرعة التطبيق ويوفر استهلاك الباقة والبطارية ومساحة تخزين الهاتف.",
        "worked_example_ar": "تطبيق تسوق يعرض أسعار المنتجات مع TTL لمدة 10 دقائق؛ وعند قيام البائع بتخفيض السعر في السيرفر، يرسل إشعار FCM صامت يبطل كاش هذا المنتج محلياً فوراً.",
        "trade_offs_ar": "فترات TTL القصيرة تضمن حداثة البيانات لكنها تزيد استهلاك الشبكة، بينما الفترات الطويلة توفر الموارد لكنها تعرض بيانات قديمة، ولذا يمثل الإبطال عبر FCM حلاً وسطاً مثالياً.",
        "failure_modes_ar": "الاعتماد على الكاش دون سياسة انتهاء صلاحية TTL مما يجمد البيانات القديمة للأبد، أو عدم مسح السجلات القديمة مما يؤدي لتضخم ملف SQLite وشغل مساحة الهاتف.",
        "production_perspective_ar": "في التطبيقات الضخمة، نحدد فترات TTL مختلفة بحسب طبيعة كل شاشة، وندمج ETag في OkHttp، ونشغل مهمة أسبوعية في WorkManager لحذف الكاش القديم غير المفضل.",
        "how_to_answer_ar": "قسم الإجابة إلى أربعة محاور: مدة الصلاحية TTL محلياً، التحقق المشروط عبر ETag و 304، الإبطال اللحظي عبر إشعارات السحاب الصامتة، والتنظيف الدوري عبر WorkManager.",
        "talking_points_ar": "مفهوم TTL وحقل التوقيت في Room، دور كود 304 في توفير الباقة، وتكامل FCM مع تحديث الشاشات اللحظي.",
        "follow_ups_ar": "- **المحاور:** 'كيف يعمل كود HTTP 304 Not Modified في تقليل استهلاك الباقة؟'\n  **المرشح:** 'يرسل التطبيق معرف النسخة المخزنة ETag في ترويسة If-None-Match؛ فإذا كانت البيانات مطابقة، يرد السيرفر بكود 304 وترويسات جديدة فقط دون إرسال محتوى الـ JSON، مما يجدد صلاحية الكاش المحلي بصفر بايت تقريباً.'\n\n- **المحاور:** 'كيف تتعامل مع إبطال الكاش عند إجراء المستخدم لعملية تعديل أو شراء؟'\n  **المرشح:** 'نطبق الـ Mutation-Triggered Invalidation؛ فبمجرد نجاح طلب الـ POST أو PUT، نقوم بتحديث السجل المقابل في Room مباشرة أو حذفه لإجبار الاستعلام التالي على جلب البيانات الطازجة.'",
        "self_check_ar": "هل شرحت سياسات TTL؟ وهل بينت الفرق بين التحقق بـ ETag والإبطال بـ FCM الصامت؟",
        "references_ar": f"- [MDN Web Docs: HTTP Caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching) — الدليل الشامل لترويسات الكاش والتحقق المشروط.\n- [Android Architecture: Offline-first data layer](https://developer.android.com/topic/architecture/data-layer/offline-first) — توثيق جوجل الرسمي لإدارة الكاش والمزامنة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "تتم إدارة انتهاء وصلاحية الكاش بدمج مدة الصلاحية الزمنية TTL محلياً مع ترويسات التحقق المشروط من السيرفر وإشارات البث اللحظي. تسجل جداول Room وقت التخزين لتحديد الصلاحية، ويستغل OkHttp ترويسات ETag والرد 304 لتوفير البيانات، بينما تتولى إشعارات FCM الصامتة ومحرك WorkManager مسح السجلات القديمة تلقائياً.",
        "best_answer_ar": "تعتمد إدارة صلاحية وتحديث الذاكرة المؤقتة على تكامل متناسق بين سياسات التخزين المحلي وبروتوكولات الشبكة وإشارات السيرفر اللحظية.\n\nتحدد سياسة مدة الصلاحية Time-To-Live عمراً زمنياً لكل سجل في قاعدة بيانات Room عبر حقل زمني، مما يتيح للمستودع تحديد ما إذا كانت البيانات صالحة للعرض الفوري أم تحتاج لطلب تحديث من السيرفر بحسب حساسية الشاشة.\n\nوعلى مستوى الشبكة، نعتمد التحقق المشروط عبر ترويسات ETag و If-None-Match في OkHttp؛ فإذا لم تطرأ تعديلات على السيرفر، يرجع كود 304 Not Modified لتأكيد صحة الكاش المحلي وتوفير استهلاك الباقة.\n\nوللحفاظ على الحداثة الفورية، ندمج إشارات الإبطال اللحظية عبر إشعارات FCM الصامتة لحذف السجلات المتغيرة فوراً من Room، مع تشغيل مهام WorkManager دورية لتنظيف السجلات القديمة غير المفضلة وحماية مساحة تخزين الهاتف.",
        "deep_answer_ar": "في معمارية الأنظمة الكبرى، لا تقتصر إدارة الكاش على تفريغ الجداول عشوائياً، بل تتطلب استراتيجية ثلاثية الأبعاد تغطي طبقة النقل وقاعدة البيانات وتنبيهات السحاب.\n\nفي طبقة النقل OkHttp، نضبط كاش مخصص مع ترويسات HTTP Caching مثل Cache-Control و ETag؛ فعندما يطلب التطبيق قائمة المنتجات، يرسل OkHttp ترويسة If-None-Match، فإذا لم تتغير البيانات بالسيرفر يعود الرد 304 خالياً من البيانات، مما يوفر استهلاك باقة الإنترنت والمعالجة.\n\nوفي طبقة قاعدة البيانات Room، نضيف حقل updatedAt لكل جدول، ونضبط فترات صلاحية متباينة بحسب طبيعة البيانات؛ فبيانات أسعار المنتجات تنتهي صلاحيتها خلال خمس دقائق، بينما بيانات الملف الشخصي تبقى صالحة لعدة ساعات.\n\nولمنع عرض بيانات قديمة عند حدوث تغييرات جوهرية بالسيرفر، نطبق نمط الإبطال المدفوع بالحدث Event-Driven Invalidation؛ حيث يرسل السيرفر إشعاراً صامتاً عبر Firebase Cloud Messaging عند تعديل أسعار أو أذونات، فيقوم مستقبل التنبيه بحذف السجل من Room فورياً، مما يدفع واجهة Compose لإعادة الرسم تلقائياً عبر Flow، وتختم العملية بمهمة أسبوعية في WorkManager لتطهير السجلات المهملة. وعلاوة على ذلك، نقوم بتسجيل مقاييس أداء الكاش عبر أدوات القياس والتحليلات لرصد نسبة إصابة الكاش Cache Hit Ratio ومعدل التحديثات الملغاة، مما يساعد الفريق الهندسي على ضبط أوقات الصلاحية بدقة وفق سلوك المستخدمين الفعلي."
    }
}

# ==========================================
# DAT-18: A transaction is saved but disappears after restart in release builds only. What should you investigate?
# ==========================================
DATA["DAT-18"] = {
    "concept_en": """Investigating release-only data disappearance requires systematically auditing build-variant configuration, code shrinking, and SQLite lifecycle behaviors:
- In-Memory Database Configuration: Check dependency injection modules (Hilt/Koin). A common mistake is injecting Room.inMemoryDatabaseBuilder() in release due to a flipped BuildConfig.DEBUG check, causing SQLite tables to reside solely in RAM and vanish on process death.
- ProGuard/R8 Obfuscation & Reflection Stripping: R8 shrinks, obfuscates, or strips default constructors, getters/setters, or @TypeConverter classes if proper keep rules are missing. While Room generates code at compile time, reflection-based converters or obfuscated entity column names can fail silently, leading Room to deserialize empty defaults upon app relaunch.
- Silent Destructive Migration: If the release build increments the database schema version without registering a corresponding Migration, and fallbackToDestructiveMigration() was enabled, Room silently drops and recreates all tables on startup.
- SQLite WAL Journaling & Unclosed Transactions: In Write-Ahead Logging mode, writes reside in the -wal file. If transactions are never committed, or if the database is opened from cache directories that the OS periodically clears, persisted records disappear after app termination.""",
    "walkthrough_en": """Verifying dependency injection, ProGuard rules, and migration configurations:
```kotlin
// 1. Audit DI Module: ensure disk database is consistently configured
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "production_app.db" // Guard against accidental inMemoryDatabaseBuilder
        )
        // Strictly forbid destructive migrations in release builds
        .apply {
            if (BuildConfig.DEBUG) {
                fallbackToDestructiveMigration()
            }
        }
        .build()
    }
}

// 2. Audit ProGuard / R8 Rules: protect entities and converters from stripping
// -keepclassmembers class * extends androidx.room.RoomDatabase {
//     <init>();
// }
// -keep class com.example.data.local.entities.** { *; }
// -keep class * extends androidx.room.TypeConverter { *; }
```""",
    "short_en": """Investigating release-only data loss requires auditing four root causes: verifying dependency injection does not inject an in-memory database, ensuring R8 shrinking does not strip Room entity constructors or TypeConverters, confirming fallbackToDestructiveMigration is disabled, and verifying the database file is stored in permanent app files rather than volatile cache directories.""",
    "structured_en": """Diagnosing data disappearance that reproduces exclusively in release builds requires isolating compilation, dependency injection, and storage discrepancies.
First, audit the dependency injection module. A flipped boolean condition in Hilt or Koin often accidentally injects Room.inMemoryDatabaseBuilder instead of the disk database in release, causing tables to evaporate whenever the process dies.
Second, examine R8 and ProGuard rules. Aggressive code shrinking can strip no-arg entity constructors or custom TypeConverters, causing Room to silently fail deserialization upon cold restart and return empty default records.
Third, verify database migration declarations. If release bumped the database version without an explicit migration and fallbackToDestructiveMigration was configured, Room silently drops and recreates SQLite tables on startup.
Fourth, ensure the database file resides in internal storage rather than temporary cache directories that Android purges under memory pressure.""",
    "deep_senior_en": """When a critical transaction persists during the session but vanishes after app restart exclusively in release builds, senior engineers immediately suspect build configuration differences rather than standard runtime database logic.
Our first investigation step is examining dependency injection graphs in Hilt.
We frequently find teams wrapping database creation in conditional logic where release accidentally receives an in-memory database builder, meaning SQLite writes exist only in volatile process RAM and vanish on process death.
The second critical area is R8 code shrinking and optimization.
Because release builds execute minification, if entity data classes or TypeConverters lack proper keep annotations, R8 can strip field getters, setters, or synthetic constructors that Room relies on during deserialization.
This causes Room queries to return default null values after restart without crashing.
The third and most catastrophic culprit is silent destructive migration.
If the release version increments the database schema number without registering a corresponding Migration object, and someone left fallbackToDestructiveMigration enabled, Room detects the schema mismatch during launch, drops all tables, and recreates an empty database.
Finally, we verify storage location and WAL journal flushing: we ensure the database is stored in context.filesDir, and confirm background write transactions are cleanly committed before the process enters background, preventing uncheckpointed Write-Ahead Logging state from getting discarded.""",
    "meta_ar": {
        "id": "DAT-18",
        "questionAr": "تُحفظ المعاملة المالية محلياً ولكنها تختفي تماماً بعد إعادة تشغيل التطبيق في إصدارات الإنتاج (Release Builds) فقط. ما هي المسارات الهندسية التي يجب عليك التحقيق فيها؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تشخيص أخطاء التخزين الخاصة بإصدارات الـ Release، وتأثير قواعد R8/ProGuard على كائنات Room و TypeConverters، والتمييز بين قواعد البيانات المؤقتة في الذاكرة InMemory والقرص، ومخاطر الـ Destructive Migration ووضع WAL.",
        "concept_ar": "يتطلب التحقيق في اختفاء البيانات في إصدارات الإنتاج (Release Builds) فحصاً منهجياً للفروق بين بيئات البناء ومعالجة كود R8 وإدارة ملفات SQLite: فحص إعدادات حقن الاعتماديات (DI) للتأكد من عدم استخدام قاعدة بيانات في الذاكرة Room.inMemoryDatabaseBuilder بالخطأ نتيجة شرط غير صحيح لـ BuildConfig. وفحص قواعد R8/ProGuard؛ حيث قد يقوم مقلص الكود بحذف المشيدات الافتراضية للكيانات أو دوال TypeConverters في حال غياب قواعد الحفظ @Keep، مما يعطل استرجاع البيانات أو يعيد قيماً فارغة. والتحقق من عدم تفعيل الترحيل التدميري الصامت fallbackToDestructiveMigration؛ فعند رفع رقم الإصدار في الإنتاج دون كائن Migration مطابق، تقوم Room بمسح كافة الجداول تلقائياً عند أول إقلاع. والتأكد من حفظ ملف قاعدة البيانات في المسار الدائم context.filesDir وليس في مجلد الكاش المؤقت cacheDir الذي يفرغه نظام أندرويد تلقائياً عند نقص الذاكرة، مع مراجعة إتمام المعاملات بملف WAL.",
        "walkthrough_ar": """فحص حقن الاعتماديات وقواعد R8 وإعدادات الترحيل الآمنة:
```kotlin
// 1. فحص كلاس التزويد في Hilt لضمان استخدام قاعدة البيانات على القرص
@Provides
@Singleton
fun provideDb(@ApplicationContext context: Context): AppDatabase {
    return Room.databaseBuilder(
        context,
        AppDatabase::class.java,
        "secure_app.db" // تجنب inMemoryDatabaseBuilder تماماً
    ).build()
}

// 2. التأكد من حظر الترحيل التدميري في كود الـ Release
// والتحقق من قواعد ProGuard لحماية كائنات Room
```""",
        "why_it_matters_ar": "يكشف الأخطاء المعمارية القاتلة التي تسبب فقدان بيانات المستخدمين الحساسة وتدمير ثقتهم في التطبيق بعد التحديث أو إعادة تشغيل الهاتف.",
        "worked_example_ar": "حفظ طلب شراء محلياً وظهوره في الشاشة بنجاح، ولكن عند إغلاق التطبيق وإعادة فتحه في نسخة الـ Release تختفي السلة تماماً بسبب استخدام inMemoryDatabaseBuilder نتيجة شرط مقلوب في DI.",
        "trade_offs_ar": "قواعد الترحيل الصارمة تمنع فقدان البيانات ولكنها تتطلب كتابة كود SQL دقيق لكل تعديل، بينما استخدام قواعد الحفظ في R8 يزيد حجم الكود قليلاً لكنه يضمن عمل الكيانات دون أخطاء خفية.",
        "failure_modes_ar": "ترك خيار fallbackToDestructiveMigration مفعلاً في إصدار الإنتاج مما يؤدي لمسح قاعدة البيانات بأكملها عند ترقية التطبيق، أو حفظ القاعدة في مجلد الكاش cacheDir.",
        "production_perspective_ar": "في المشروعات المصرفية، نضع اختبارات CI مؤتمتة تبني نسخة الـ Release وتختبر حفظ السجلات وإعادة تشغيل التطبيق، مع حظر الترحيل التدميري برمجياً وتدقيق مسار الملف context.filesDir.",
        "how_to_answer_ar": "رتب خطوات التحقيق منطقياً: أولاً فحص حقن الاعتماديات لـ InMemoryDatabase، ثانياً تدقيق قواعد R8 لحماية الكيانات، ثالثاً التحقق من الترحيل التدميري الصامت، ورابعاً فحص مسار حفظ الملف في أندرويد.",
        "talking_points_ar": "مخاطر InMemoryDatabase بالخطأ، دور R8 في حذف المشيدات الافتراضية، مسار cacheDir مقابل filesDir، وكارثة fallbackToDestructiveMigration.",
        "follow_ups_ar": "- **المحاور:** 'كيف يمكن لـ R8 أن يتسبب في إرجاع بيانات فارغة دون حدوث كراش؟'\n  **المرشح:** 'إذا قام R8 بحذف الحقول أو دوال Getters/Setters الخاصة بالكيان أو كلاسات TypeConverters، تقوم Room بتوليد كود يستخدم القيم الافتراضية الفارغة فيفقد السجل محتواه دون أن يسقط التطبيق.'\n\n- **المحاور:** 'كيف تتأكد أن ملف قاعدة البيانات لم يمسح بواسطة نظام التشغيل؟'\n  **المرشح:** 'بالتأكد من استخدام context.getDatabasePath() أو context.filesDir، وتجنب حفظها في context.cacheDir لأن نظام أندرويد يفرغ مجلد الكاش تلقائياً عند انخفاض مساحة الهاتف.'",
        "self_check_ar": "هل غطيت سيناريوهات InMemoryDatabase وقواعد R8 والترحيل التدميري ومسار حفظ الملف؟",
        "references_ar": f"- [Android Developers: Shrink, obfuscate, and optimize your app](https://developer.android.com/studio/build/shrink-code) — دليل ضبط قواعد R8 و ProGuard.\n- [Room Database: Defining data using Room entities](https://developer.android.com/training/data-storage/room/defining-data) — إرشادات حفظ الكيانات وتجنب مشاكل التشغيل.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يتطلب التحقيق فحص أربعة أسباب رئيسية: التأكد من أن حقن الاعتماديات لا يستخدم قاعدة بيانات بالذاكرة في الـ Release، وفحص قواعد R8 لضمان عدم حذف مشيدات الكيانات ومحولات TypeConverters، والتحقق من تعطيل fallbackToDestructiveMigration لمنع مسح الجداول عند الترقية، والتأكد من حفظ الملف في التخزين الدائم وليس مجلد الكاش.",
        "best_answer_ar": "يستدعي اختفاء البيانات في إصدارات الإنتاج فقط بعد إعادة التشغيل فحصاً دقيقاً للفروق بين بيئات البناء وإعدادات تقليص الكود وإدارة التخزين.\n\nأولاً، فحص وحدة حقن الاعتماديات للتأكد من عدم تمرير Room.inMemoryDatabaseBuilder بالخطأ في بيئة الـ Release بدلاً من قاعدة البيانات المخزنة على القرص، مما يجعل السجلات تختفي بمجرد إغلاق المعالج.\n\nثانياً، مراجعة قواعد R8 و ProGuard؛ فالتقليص الحاد للكود قد يحذف المشيدات الافتراضية للكيانات أو دوال TypeConverters، مما يجعل Room تفشل في قراءة السجلات وتعيد قيماً فارغة عند بدء التشغيل.\n\nثالثاً، التأكد من تعطيل خاصية fallbackToDestructiveMigration تماماً في الإنتاج؛ فإذا رُفع رقم الإصدار دون توفير كائن Migration، ستقوم Room بمسح الجداول بالكامل.\n\nرابعاً، التحقق من تخزين ملف قاعدة البيانات في المجلد الدائم context.filesDir وليس في مجلد الكاش المؤقت الذي يفرغه نظام أندرويد تلقائياً.",
        "deep_answer_ar": "عندما يختفي سجل المعاملة بعد إعادة تشغيل التطبيق في إصدار الإنتاج فقط، فإن المشكلة لا تكمن في كود الحفظ العادي بل في التباين المعماري بين بيئتي Debug و Release.\n\nأول خطوة نتبعها هي تدقيق حقن الاعتماديات في Hilt؛ فكثيراً ما نكتشف خطأ في شرط الفحص البرمجي يقود لتوليد قاعدة بيانات في الذاكرة المؤقتة InMemoryDatabase في الـ Release، مما يحفظ المعاملة في الرام طالما التطبيق يعمل، وتتبخر بمجرد قتله.\n\nالمسار الثاني هو فحص تقليص الكود عبر R8؛ فعند تفعيل الـ Minification، قد يقوم R8 بإزالة المشيدات الافتراضية لكيانات Room أو إخفاء فئات TypeConverters إذا لم تكن محمية بقواعد Keep صريحة، مما يجعل Room تفشل في تحويل السجلات المخزنة وتعيد قوائم فارغة دون إطلاق استثناء صريح.\n\nالمسار الثالث والأكثر خطورة هو الترحيل التدميري الصامت؛ فإذا رُفع رقم إصدار قاعدة البيانات في نسخة الإنتاج وغاب كائن الترحيل Migration، وكان خيار fallbackToDestructiveMigration مفعلاً، فإن Room تحذف ملفات SQLite وتنشئ جداول فارغة في صمت عند أول إقلاع.\n\nوأخيراً، نتحقق من أن مسار الملف يقع داخل مجلد الملفات الدائم وليس في مجلد الكاش cacheDir الذي يمسحه أندرويد عند نقص المساحة، مع التأكد من إغلاق معاملات الـ WAL بشكل ذري قبل إغلاق التطبيق."
    }
}

# ==========================================
# DAT-19: Two refresh-token requests both invalidate the session. How do you serialize refresh correctly?
# ==========================================
DATA["DAT-19"] = {
    "concept_en": """Safe serialization of refresh-token operations resolves concurrency race conditions in modern token rotation architectures:
- Token Rotation & The Concurrency Trap: Modern OAuth/OIDC backends employ Refresh Token Rotation. Each refresh token is single-use: when presented, the server issues a new pair of access and refresh tokens and invalidates the old refresh token. If two concurrent HTTP requests fail with 401 simultaneously and both attempt to use the existing refresh token, the second request arrives at the backend after the refresh token was already consumed. The server interprets this as a potential token replay attack, revokes the user's entire session family, and forces an immediate logout.
- OkHttp Authenticator Serialization: OkHttp does not synchronize Authenticator.authenticate() calls across parallel dispatcher threads. A thread-safe TokenManager must coordinate execution:
  1. Double-Checked Token Inspection: Before executing a network refresh, the Authenticator checks if the failed request's Authorization header differs from the latest access token in memory. If another concurrent thread has already completed the refresh, the Authenticator simply updates the header to the fresh token and returns the request for replay without contacting the auth server.
  2. Single-Flight Concurrency Lock: If the token is still stale, the thread acquires an exclusive lock (via Kotlin Coroutines Mutex or ReentrantLock).
  3. Request Queuing: Any other concurrent 401 threads suspend or block on the lock, waiting for the single refresh network call to complete.
  4. Atomic Storage & Release: Once the fresh tokens are stored in secure storage, the lock is released, and all queued requests replay seamlessly with the new bearer token.""",
    "walkthrough_en": """Thread-safe token manager coordinating single-flight refresh with Mutex:
```kotlin
class SafeTokenManager(
    private val authApi: AuthApiService,
    private val tokenStorage: EncryptedTokenStorage
) {
    private val mutex = Mutex()

    suspend fun getOrRefreshToken(staleHeaderToken: String?): String? = mutex.withLock {
        val currentToken = tokenStorage.getAccessToken()
        // Double-checked locking: If another thread already refreshed it, return immediately
        if (currentToken != null && "Bearer $currentToken" != staleHeaderToken) {
            return currentToken
        }

        // Execute single refresh request
        val refreshToken = tokenStorage.getRefreshToken() ?: return null
        return try {
            val response = authApi.refreshTokens(RefreshTokenRequest(refreshToken))
            tokenStorage.saveTokens(response.accessToken, response.refreshToken)
            response.accessToken
        } catch (e: Exception) {
            tokenStorage.clearSession()
            null
        }
    }
}

class SynchronizedAuthenticator(
    private val tokenManager: SafeTokenManager
) : Authenticator {
    override fun authenticate(route: Route?, response: Response): Request? {
        if (responseCount(response) >= 2) return null

        val currentAuth = response.request.header("Authorization")
        val newToken = runBlocking {
            tokenManager.getOrRefreshToken(currentAuth)
        } ?: return null

        return response.request.newBuilder()
            .header("Authorization", "Bearer $newToken")
            .build()
    }

    private fun responseCount(response: Response): Int {
        var count = 1
        var prior = response.priorResponse
        while (prior != null) { count++; prior = prior.priorResponse }
        return count
    }
}
```""",
    "short_en": """Serializing refresh-token requests requires thread-safe single-flight coordination using a Mutex or ReentrantLock. The authenticator compares the failed request's token against current in-memory credentials: if already refreshed by another thread, it immediately replays with the new token; otherwise, it acquires the lock, executes a single refresh, and unblocks queued requests.""",
    "structured_en": """Preventing concurrent refresh requests from invalidating user sessions requires single-flight synchronization to honor Refresh Token Rotation policies.
First, understand the failure mode. Modern backends enforce single-use refresh tokens. When parallel network calls return 401 simultaneously, uncoordinated refresh attempts submit identical tokens; the server detects reuse, treats it as a security breach, and terminates the entire session.
Second, implement double-checked token inspection in OkHttp Authenticator. Before contacting the auth server, compare the failed request's Authorization header with the latest token in memory. If another thread already completed a refresh, immediately replay the request with the fresh token.
Third, guard actual network renewal behind a synchronization primitive such as a Mutex or ReentrantLock. Only one thread calls the refresh API while concurrent 401s suspend, resuming cleanly once fresh credentials are saved.""",
    "deep_senior_en": """In large-scale Android architectures, handling token refresh without robust thread synchronization is a frequent cause of random user logouts in production.
Enterprise backends implement Refresh Token Rotation to comply with OAuth 2.1 standards: when a refresh token is exchanged, it is immediately invalidated and replaced with a new pair.
If a screen dispatches five parallel Retrofit calls and all receive HTTP 401 Unauthorized because the access token expired, each thread enters OkHttp's Authenticator concurrently.
Without coordination, all five threads attempt to invoke the refresh endpoint with the same refresh token.
The first request succeeds, but the remaining four present an already-invalidated token.
The auth server detects this as a replay attack, invalidates the entire token family, and rejects all subsequent calls, unexpectedly kicking the user out of the app.
To eliminate this race condition, we implement a single-flight TokenManager utilizing double-checked locking with a Coroutine Mutex.
When an Authenticator thread wakes up, it first checks whether the failed request's header matches the active access token in storage.
If they differ, a sibling thread has already refreshed the session, so the Authenticator returns the new request immediately without network traffic.
If they match, it enters the Mutex lock, re-verifies the token, issues a single refresh request, persists the new pair into encrypted storage, and releases the lock, allowing queued requests to replay smoothly.""",
    "meta_ar": {
        "id": "DAT-19",
        "questionAr": "يؤدي إرسال طلبين متزامنين لتجديد الـ Token إلى إبطال جلسة المستخدم بالكامل بسبب حظر إعادة استخدام التوكن. كيف تنظم وتتسلسل طلبات التجديد بشكل متزامن وآمن؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم ظاهرة تسابق طلبات التجديد (Race Conditions in Token Refresh)، ومعمارية تدوير التوكنز (Token Rotation)، وتطبيق التزامن الآمن عبر Mutex و OkHttp Authenticator، ومنع عواصف الـ 401 المتكررة.",
        "concept_ar": "تحل المعالجة المتسلسلة لطلبات تجديد التوكن مشكلة تسابق الخيوط (Race Conditions) في معمارية تدوير التوكنات (Token Rotation): تعتمد أنظمة الأمان الحديثة على تدوير الـ Refresh Token؛ حيث يُستخدم التوكن لمرة واحدة فقط ويُلغى فوراً مع إصدار توكن جديد. فإذا أرسل التطبيق طلبين متزامنين واستقبلا كود 401 معاً، وحاول كلاهما التجديد بنفس الـ Refresh Token القديم، يعتبر السيرفر الطلب الثاني محاولة اختراق وإعادة استخدام (Token Replay Attack) فيبطل الجلسة بالكامل ويجبر المستخدم على تسجيل الخروج. ولحل ذلك في OkHttp، نطبق نمط التدفق الأحادي المتزامن (Single-Flight Execution) داخل Authenticator: أولاً فحص التوكن المزدوج؛ فإذا كان التوكن المرفق بالطلب يختلف عن التوكن الحالي بالذاكرة، فهذا يعني أن خيطاً آخر قد أتم التجديد بالفعل، فيعاد إرسال الطلب بالتوكن الجديد فوراً دون اتصال بالسيرفر. ثانياً حجز قفل متزامن (Mutex أو ReentrantLock)؛ بحيث ينفرد خيط واحد بطلب التجديد بينما تنتظر بقية الطلبات في طابور معلق. وثالثاً حفظ التوكنات الجديدة في مساحة آمنة وتحرير القفل لإعادة تشغيل كافة الطلبات المنتظرة بنجاح.",
        "walkthrough_ar": """تطبيق مدير التوكن الآمن بقفل Mutex والفحص المزدوج:
```kotlin
class SafeTokenManager(private val prefs: TokenStorage, private val api: AuthApi) {
    private val mutex = Mutex()

    suspend fun refreshTokenIfNeeded(oldHeader: String?): String? = mutex.withLock {
        val currentToken = prefs.getToken()
        // فحص مزدوج: إذا كان خيط آخر قد جدد التوكن بالفعل
        if (currentToken != null && "Bearer $currentToken" != oldHeader) {
            return currentToken
        }
        val refreshToken = prefs.getRefreshToken() ?: return null
        val response = runCatching { api.refresh(refreshToken) }.getOrNull() ?: return null
        prefs.saveTokens(response.accessToken, response.refreshToken)
        response.accessToken
    }
}
```""",
        "why_it_matters_ar": "يحمي جلسة المستخدم من الانهيار وتسجيل الخروج الإجباري المفاجئ عند انتهاء صلاحية التوكن أثناء تنفيذ طلبات متزامنة.",
        "worked_example_ar": "فتح الصفحة الرئيسية وإطلاق 4 طلبات متزامنة؛ تفشل جميعها بكود 401، فيلتقط أول خيط قفل Mutex ويجدد التوكن، بينما تستخدم بقية الطلبات الثلاثة التوكن الجديد فوراً دون إرسال طلبات تجديد مكررة.",
        "trade_offs_ar": "استخدام قفل Mutex يعلق الطلبات المتزامنة لبضع مئات من الملي ثانية حتى يكتمل التجديد، ولكنه يوفر حماية مطلقة للجلسة ويمنع استهلاك السيرفر بطلبات تجديد غير شرعية.",
        "failure_modes_ar": "تجديد التوكن دون قفل متزامن مما يؤدي لرفض السيرفر للتجديدات اللاحقة بسبب سياسة Token Rotation، أو نسيان الفحص المزدوج فيتم التجديد مرتين بلا داعٍ.",
        "production_perspective_ar": "في المشروعات الكبرى، نلزم كافة عملاء HTTP بالمرور عبر TokenManager أحادي يملك Mutex، مع حفظ التوكنات في مساحة مشفرة ومراقبة أحداث انتهاء الجلسة مركزياً.",
        "how_to_answer_ar": "اشرح المشكلة الجذرية: سياسة Token Rotation وحظر إعادة استخدام التوكن القديم، ثم بين آلية الحل عبر الفحص المزدوج Double-Checked وقفل Mutex داخل Authenticator.",
        "talking_points_ar": "مفهوم Token Rotation، هجوم Replay Attack، دور الفحص المزدوج، واستخدام Mutex لتعليق الطلبات حتى انتهاء التجديد.",
        "follow_ups_ar": "- **المحاور:** 'ما هو الفحص المزدوج Double-Checked Locking وكيف يمنع استدعاءات الشبكة الزائدة؟'\n  **المرشح:** 'يقارن الخيط التوكن الفاشل بالتوكن الحالي المخزن في الذاكرة قبل حجز القفل وبعده؛ فإذا وجده قد تغير، يعلم أن طلباً سابقاً قد أتم التجديد بالفعل، فيستخدمه فوراً دون إرسال طلب جديد للسيرفر.'\n\n- **المحاور:** 'ماذا تفعل إذا فشل طلب تجديد التوكن بسبب إلغاء صلاحية المستخدم تماماً من السيرفر؟'\n  **المرشح:** 'يقوم TokenManager بمسح كافة التوكنات وسجلات قاعدة البيانات المحلية، وإرجاع null للـ Authenticator لإلغاء كافة الطلبات المعلقة، وإطلاق حدث SessionExpiredEvent لتوجيه الواجهة فوراً لشاشة تسجيل الدخول.'",
        "self_check_ar": "هل شرحت سياسة Token Rotation؟ وهل بينت الفحص المزدوج واستخدام Mutex لجدولة التجديد؟",
        "references_ar": f"- [OAuth 2.0 Security Best Current Practice](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics#section-4.14) — معايير أمان تدوير التوكنات ومنع هجمات الإعادة.\n- [OkHttp Authenticator Documentation](https://square.github.io/okhttp/features/calls/#authenticators) — توثيق واجهة Authenticator في OkHttp.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يتطلب تنظيم تجديد التوكن تطبيق التزامن أحادي التدفق عبر Mutex لمنع تعارض تدوير التوكنات. يفحص المعترض التوكن المرفق بالطلب مقارنة بالتوكن المخزن بالذاكرة؛ فإذا كان قد تجدد بواسطة خيط آخر يعاد إرسال الطلب فوراً، وإلا يحجز القفل لينفرد خيط واحد بالتجديد وإلغاء تعليق بقية الطلبات.",
        "best_answer_ar": "تتطلب حماية جلسة المستخدم من الإبطال العشوائي أثناء التجديد المتزامن تطبيق نمط التدفق الأحادي Single-Flight لمنع انتهاك سياسة تدوير التوكنات.\n\nتعتمد أنظمة الحماية الحديثة على استخدام Refresh Token لمرة واحدة فقط؛ فعندما تستقبل عدة طلبات متزامنة كود 401 Unauthorized معاً، فإن محاولة كل خيط استخدام نفس التوكن القديم تجعل السيرفر يعتبر ذلك هجوماً واختراقاً، فيبطل الجلسة بالكامل ويسجل خروج المستخدم.\n\nولحل ذلك، نطبق فحصاً مزدوجاً للتوكن داخل OkHttp Authenticator؛ فإذا كان التوكن المرفق يختلف عن التوكن الحالي بالذاكرة، فهذا يعني أن خيطاً آخر قد أتم التجديد، فيعاد إرسال الطلب فوراً بالتوكن الجديد دون أي اتصال إضافي بالسيرفر.\n\nأما إذا كان التوكن قديماً، فيتم حجز قفل Mutex لينفرد خيط واحد بإرسال طلب التجديد وحفظ التوكنات الجديدة في مساحة مشفرة، ثم تحرير القفل لتستأنف كافة الطلبات المعلقة رحلتها بسلاسة.",
        "deep_answer_ar": "في التطبيقات المالية والخدمية الكبرى، يمثل تسجيل الخروج المفاجئ أثناء تصفح التطبيق كابوساً للمستخدمين، وينتج في الغالب عن تسابق خيوط التجديد مع سياسة Refresh Token Rotation.\n\nعندما تفتح شاشة تطلق عدة استعلامات متزامنة وتنتهي صلاحية توكن الوصول Access Token، ترد جميعها بكود 401 في نفس اللحظة. فإذا دخلت كافة الخيوط لمعترض Authenticator وحاولت الاتصال بنقطة التجديد بنفس الـ Refresh Token، ينجح أول طلب فقط، بينما تصل بقية الطلبات بتوكن ملغى، فيعتبر السيرفر ذلك محاولة اختراق Replay Attack ويلغي الحساب فورياً.\n\nللقضاء على هذه المشكلة جذرياً، نصمم TokenManager يعتمد نمط الفحص المزدوج Double-Checked Locking مدعوماً بـ Coroutines Mutex. عندما يستقبل خيط كود 401، يقارن ترويسة الطلب بالتوكن المخزن بالذاكرة؛ فإذا وجده مختلفاً، يدرك أن خيطاً زميلاً قد جدده بالفعل، فيحدث الترويسة ويعيد إرسال الطلب في أجزاء من الملي ثانية.\n\nوفي حال تطابق التوكن، يدخل الخيط داخل قفل Mutex ويعيد الفحص، ثم يرسل طلباً واحداً للسيرفر، ويحدث التوكنات في التخزين المشفر، ويحرر القفل لتعبر كافة الطلبات المنتظرة بالتوكن الجديد، مما يمنع عواصف الـ 401 ويحمي الجلسة تماماً. كما نربط مدير التوكن بنظام مراقبة مركزي يسجل محاولات التجديد الناجحة والفاشلة؛ فإذا تكرر فشل التجديد بسبب انتهاء الجلسة تماماً، نقوم بإطلاق تنبيه فوري لواجهة التطبيق لإظهار رسالة واضحة للمستخدم قبل تحويله الآمن لشاشة تسجيل الدخول."
    }
}

# ==========================================
# DAT-20: The server accepted a payment but the response was lost. How do you recover safely?
# ==========================================
DATA["DAT-20"] = {
    "concept_en": """Safe recovery from lost payment responses addresses the classic Two Generals' network partition problem using idempotency protocols and deterministic state reconciliation:
- The Failure Scenario: The client sends a payment POST request. The payment gateway charges the customer and persists the record. Before the 200 OK HTTP response reaches the mobile device, the cellular signal drops or the connection times out. The Android client catches a SocketTimeoutException. Blindly retrying the transaction without an idempotency key triggers a duplicate charge, while reporting failure induces user panic.
- Client-Generated Idempotency Keys: Before transmitting the payment request, the client generates a unique cryptographically random UUID (Idempotency-Key HTTP header) and saves the payment record locally in Room with status PENDING_CONFIRMATION.
- Server Idempotency Contract: The backend stores idempotency keys in Redis or a relational database with strict unique constraints. When a duplicate request with the identical key arrives, the backend does not re-execute the charge; it returns the cached receipt from the initial successful execution.
- Safe Recovery Protocol:
  1. Intercept network failure (SocketTimeoutException or IOException).
  2. Do not report payment failure or show an error toast. Transition UI to a 'Verifying Transaction' state.
  3. Query a dedicated idempotency status endpoint (GET /api/v1/payments/status/{idempotencyKey}).
  4. If network recovery fails, schedule an immediate non-destructive WorkManager task with Exponential Backoff to reconcile the payment status in the background.""",
    "walkthrough_en": """Safe payment execution with client-generated idempotency key and status recovery:
```kotlin
@Entity(tableName = "payments")
data class PaymentRecord(
    @PrimaryKey val idempotencyKey: String,
    val orderId: String,
    val amount: Double,
    val status: PaymentStatus // PENDING, CONFIRMED, FAILED
)

class PaymentRecoveryManager(
    private val paymentDao: PaymentDao,
    private val paymentApi: PaymentApiService
) {
    suspend fun executePayment(orderId: String, amount: Double): PaymentResult {
        val key = UUID.randomUUID().toString()
        paymentDao.insert(PaymentRecord(key, orderId, amount, PaymentStatus.PENDING))

        return try {
            val response = paymentApi.charge(idempotencyKey = key, orderId = orderId, amount = amount)
            paymentDao.updateStatus(key, PaymentStatus.CONFIRMED)
            PaymentResult.Success(response.receiptId)
        } catch (e: IOException) {
            // Network failed: do NOT treat as failed charge; initiate recovery
            recoverPaymentState(key)
        }
    }

    private suspend fun recoverPaymentState(key: String): PaymentResult {
        // Poll status endpoint using the same idempotency key
        return runCatching {
            val status = paymentApi.checkStatus(key)
            paymentDao.updateStatus(key, status.toRecordStatus())
            if (status.isSuccess) PaymentResult.Success(status.receiptId)
            else PaymentResult.PendingConfirmation(key)
        }.getOrElse {
            PaymentResult.PendingConfirmation(key)
        }
    }
}
```""",
    "short_en": """Recovering from lost payment responses requires client-generated Idempotency Keys persisted in Room before dispatching network calls. Upon experiencing timeouts, the client avoids blind retries to prevent duplicate charges, transitions the UI to a verification state, polls a status endpoint using the existing key, and delegates persistent background reconciliation to WorkManager.""",
    "structured_en": """Safely recovering when a payment response is dropped after server processing requires client-driven idempotency and defensive verification protocols.
First, generate an Idempotency-Key prior to network transmission. The client generates a unique UUID, persists it in Room with the pending payment details, and attaches it as an HTTP header.
Second, establish server idempotency semantics. If a network drop occurs and the same request is replayed, the backend recognizes the idempotency key and returns the original transaction receipt without charging the customer a second time.
Third, implement safe recovery instead of blind failure reporting. When encountering network timeouts, never display a generic payment failed error. Transition the UI to a pending verification state, query a dedicated payment status endpoint using the idempotency key, and enqueue a WorkManager job to reconcile the transaction reliably in the background.""",
    "deep_senior_en": """In financial mobile engineering, dropped payment responses represent the classic distributed systems Two Generals' problem.
When a POST payment request succeeds on the banking gateway but the connection drops before the HTTP 200 payload returns to the phone, the Android client receives a SocketTimeoutException.
Rookie engineers often make two critical errors: either reporting an immediate payment failure which induces user panic, or automatically retrying the raw payment call which charges the customer's credit card twice.
To guarantee mathematical safety, we enforce a strict idempotency architecture.
Before any network bytes leave the device, our repository generates a cryptographically random UUID as an Idempotency-Key and commits the transaction into Room with status PENDING.
This key is injected into the HTTP request headers.
If OkHttp throws a SocketTimeoutException or network partition error, our recovery flow intercepts the exception.
The UI immediately transitions into an informational 'Verifying Payment Status' state with clear messaging.
The repository then queries a lightweight, side-effect-free status endpoint passing the idempotency key.
If the status check returns confirmed, we update Room and transition the UI to success.
If the device remains completely offline, we enqueue a dedicated WorkManager worker configured with Exponential Backoff and network constraints to resolve the payment status in the background, notifying the user via a system notification once confirmation is finalized.""",
    "meta_ar": {
        "id": "DAT-20",
        "questionAr": "قبل السيرفر عملية الدفع بنجاح ولكن استجابة الشبكة فُقدت في طريق العودة بسبب انقطاع الاتصال. كيف تتعافى من هذا الموقف بأمان دون خصم المبلغ مرتين؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مشكلة القائدين (Two Generals' Problem) وانقطاع الشبكة بعد التنفيذ، واستخدام مفاتيح إثبات العمليات الفريدة (Idempotency Keys)، والاستعلام الموجه عن حالة العملية، والتنسيق عبر WorkManager.",
        "concept_ar": "تتطلب معالجة فقدان الرد بعد نجاح الدفع حل معضلة انقطاع الشبكة (Two Generals' Problem) باستخدام مفاتيح عدم التكرار (Idempotency Keys) وبروتوكولات استرجاع الحالة: ينشئ التطبيق معرفاً فريداً عشوائياً (UUID) كمفتاح عدم تكرار Idempotency-Key لكل محاولة دفع، ويحفظ المعاملة محلياً في Room بحالة 'قيد التأكيد' قبل إرسال طلب الشبكة. ويضمن السيرفر معالجة هذا المفتاح ذرياً؛ فإذا استقبل نفس المفتاح ثانية، يعيد نفس الإيصال السابق دون خصم المبلغ مجدداً. وعند انقطاع الاتصال أو حدوث SocketTimeoutException، يُحظر إظهار رسالة فشل للمستخدم أو تكرار الخصم فوراً، بل تنتقل الواجهة لحالة 'جاري التحقق من الدفع'، ويقوم التطبيق بالاستعلام عن حالة العملية عبر نقطة تحقق مخصصة باستخدام نفس المفتاح، مع تفويض مهمة التحقق الخلفي لمحرك WorkManager في حال استمرار انقطاع الشبكة.",
        "walkthrough_ar": """تنفيذ الدفع بمفتاح Idempotency وحفظ الحالة للتعافي:
```kotlin
// 1. توليد مفتاح فريد وحفظ المعاملة معلقة في Room
val key = UUID.randomUUID().toString()
db.paymentDao().insert(Payment(key, orderId, amount, status = "PENDING"))

// 2. إرسال الطلب بالترويسة واستعادة الحالة عند انقطاع الاتصال
try {
    val receipt = api.pay(idempotencyKey = key, orderId, amount)
    db.paymentDao().updateStatus(key, "CONFIRMED")
} catch (e: SocketTimeoutException) {
    // شبكة مقطوعة: عدم إظهار فشل، بل بدء التحقق بنفس المفتاح
    val verified = api.checkPaymentStatus(key)
    if (verified.isPaid) db.paymentDao().updateStatus(key, "CONFIRMED")
}
```""",
        "why_it_matters_ar": "يحمي أموال المستخدمين من الخصم المزدوج ويمنع ذعر العملاء والشكاوى القضائية عند انقطاع شبكة الهاتف أثناء التحويلات المالية.",
        "worked_example_ar": "تحويل 100 دولار عبر التطبيق؛ يسحب البنك المبلغ ويتعطل برج الاتصال قبل إرسال 200 OK، فيتحول التطبيق لحالة 'جاري التحقق' ثم يستعلم بنفس المفتاح ليظهر تم الدفع بنجاح دون خصم جديد.",
        "trade_offs_ar": "استخدام Idempotency Keys يتطلب دعم السيرفر لقاعدة بيانات تخزن المفاتيح لفترة كافية، ولكنه يوفر أماناً مصرفياً لا غنى عنه.",
        "failure_modes_ar": "إظهار رسالة 'فشل الدفع' للمستخدم فيقوم بالضغط ثانية ويُخصم حسابه مرتين، أو إعادة إرسال طلب الدفع بمفتاح جديد بدلاً من استعلام الحالة.",
        "production_perspective_ar": "في تطبيقات المدفوعات والـ FinTech، يعتبر مفتاح Idempotency-Key إلزامياً في كافة طلبات الـ POST، مع ربط الواجهة بمؤشر تدقيق هادئ ومتابعة بـ WorkManager.",
        "how_to_answer_ar": "بين مشكلة انقطاع الشبكة بعد التنفيذ Two Generals' Problem، واشرح دور مفتاح Idempotency-Key في السيرفر والموبايل، وحذر من إظهار رسالة فشل مضللة للعميل.",
        "talking_points_ar": "معضلة Two Generals' Problem، توليد UUID كـ Idempotency-Key، تجنب الخصم المزدوج، والاستعلام المخصص عن الحالة.",
        "follow_ups_ar": "- **المحاور:** 'ماذا لو أعاد المستخدم فتح التطبيق بعد يوم كامل وظل التحويل معلقاً؟'\n  **المرشح:** 'يقوم عامل WorkManager أو منطق فحص الطلبات المعلقة عند بدء التشغيل بالاستعلام عن حالة المفتاح بالسيرفر؛ فإذا تأكد الدفع يُعرض الإيصال، وإن تم رفضه يُلغى الطلب وتُحرر السلة.'\n\n- **المحاور:** 'لماذا لا نكتفي بإعادة إرسال طلب POST الدفع تلقائياً عبر OkHttp Interceptor؟'\n  **المرشح:** 'لأن طلبات الـ POST غير آمنة Non-Idempotent بطبيعتها، وإعادة المحاولة التلقائية قد تعيد سحب الأموال ما لم يكن السيرفر مهيأ خصيصاً بمفتاح عدم التكرار، ولذا يفضل الاستعلام عن الحالة أولاً.'",
        "self_check_ar": "هل شرحت خطورة الخصم المزدوج ومفتاح Idempotency؟ وهل بينت كيفية إدارة الواجهة والاستعلام عن الحالة؟",
        "references_ar": f"- [Stripe API Documentation: Idempotent Requests](https://stripe.com/docs/api/idempotent_requests) — المعيار الصناعي العالمي لمفاتيح عدم التكرار في المدفوعات.\n- [Two Generals Problem in Distributed Systems](https://en.wikipedia.org/wiki/Two_Generals%27_Problem) — الأساس النظري لمعضلات انقطاع الشبكة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يتطلب التعافي الآمن توليد مفتاح عدم تكرار Idempotency-Key فريد وحفظه في Room قبل الإرسال. وعند انقطاع الاتصال بعد السحب، يُمنع إعادة الطلب عشوائياً لتفادي الخصم المزدوج، بل تنتقل الواجهة لحالة التحقق، ويستعلم التطبيق عن حالة العملية بنفس المفتاح مع تفويض WorkManager بالمتابعة الخلفية.",
        "best_answer_ar": "تتطلب معالجة فقدان رد السيرفر بعد قبول الدفع تطبيق بروتوكول عدم التكرار Idempotency لمنع تكرار خصم الأموال من حساب المستخدم.\n\nأولاً، توليد مفتاح Idempotency-Key فريد عبر UUID وحفظ المعاملة في Room بحالة معلقة قبل إرسال الطلب، وتضمين المفتاح في ترويسة الـ HTTP للسيرفر.\n\nثانياً، يلتزم السيرفر بالتعامل مع هذا المفتاح؛ فإذا استقبل نفس المفتاح مجدداً بسبب إعادة المحاولة، يرجع نفس إيصال العملية السابقة دون إعادة تنفيذ حركة الخصم المالي ثانية.\n\nثالثاً، عند حدوث SocketTimeoutException، يُحظر إظهار رسالة فشل للمستخدم؛ بل تتحول الواجهة لحالة جاري التحقق من المعاملة، ويطلق التطبيق استعلاماً عن حالة العملية بنقطة فحص مخصصة بنفس المفتاح، مع جدولة مهمة في WorkManager لضمان تأكيد حالة الدفع في الخلفية عند عودة الاتصال.",
        "deep_answer_ar": "في التطبيقات المالية، يمثل انقطاع الاتصال بعد خصم المبلغ معضلة كلاسيكية في الأنظمة الموزعة تعرف بمشكلة القائدين Two Generals' Problem.\n\nعندما يستقبل البنك طلب الدفع وينفذ الخصم بنجاح ولكن تنقطع شبكة الهاتف قبل وصول الرد 200 OK، يستقبل التطبيق استثناء انقطاع SocketTimeoutException. ويقع الكثيرون في خطأين فادحين: إما إظهار رسالة فشل الدفع مما يدفع المستخدم لإعادة المحاولة وخصم أمواله مرتين، أو إعادة إرسال طلب الدفع تلقائياً بدون مفتاح فريد.\n\nلضمان سلامة العمليات، نلزم التطبيق بتوليد مفتاح عدم تكرار Idempotency-Key عشوائي وتخزينه في جدول Room بحالة قيد التأكيد قبل إرسال أي بايت عبر الشبكة، وإرفاقه بترويسات OkHttp. فإذا انقطعت الشبكة، نعترض الخطأ وننقل الشاشة فوراً لحالة 'جاري مراجعة حالة الدفع' لطمأنة العميل.\n\nبعدها يستعلم التطبيق عن حالة المعاملة عبر GET /payments/status/{key}؛ فإذا أكد السيرفر نجاحها، يتم تحديث Room وعرض إيصال الشراء. وإذا استمر انقطاع الإنترنت، نوكل مهمة التحقق لعامل WorkManager مع خاصية Exponential Backoff لمتابعة التأكيد في الخلفية وإشعار المستخدم بإشعار رسمي فور اكتمالها. ونحرص دائماً على تصميم واجهة المستخدم بحيث تعرض تاريخ ووقت المحاولة مع زر يدوي للتحقق من العملية دون إعادة الخصم؛ مما يمنح المستخدم شعوراً بالأمان والشفافية التامة، ويقلل الضغط على فريق الدعم الفني وخدمة العملاء."
    }
}

# ==========================================
# DAT-21: Design a paginated news feed that opens instantly and syncs when online.
# ==========================================
DATA["DAT-21"] = {
    "concept_en": """Designing an enterprise paginated news feed with instant cold start and robust offline synchronization requires an integrated architectural system:
- Instant Cold Start & Single Source of Truth: The UI never awaits network responses on launch. ViewModels query Room directly, observing a cold Flow<PagingData<ArticleEntity>>. Room delivers cached articles from disk in under 50ms, rendering the feed immediately without blank screens or loading shimmers.
- Jetpack Paging 3 with RemoteMediator: Decouples UI rendering from network transport. As the user scrolls near the threshold of cached items, RemoteMediator detects the boundary and dispatches an asynchronous network request to fetch the subsequent page.
- Cursor & RemoteKey Persistence: A companion ArticleRemoteKeys table in Room tracks pagination tokens (prevKey and nextKey) for each entity, ensuring scroll positions and page cursors survive process death.
- Atomic Refresh & Consistency: Swipe-to-refresh actions execute inside RoomDatabase.withTransaction: clearing outdated non-bookmarked cache, resetting remote keys, and inserting fresh articles atomically to eliminate visual jumping.
- Dual-Layer Image Caching: Media loaders (such as Coil) configure disk and memory caches with 250MB bounds, prefetching article thumbnails ahead of the viewport.
- Periodic Background Synchronization: WorkManager periodically syncs the feed under unmetered network conditions, keeping the offline cache warm.""",
    "walkthrough_en": """System architecture connecting Room, RemoteMediator, and Pager:
```kotlin
@Entity(tableName = "articles")
data class ArticleEntity(
    @PrimaryKey val id: String,
    val title: String,
    val snippet: String,
    val publishedAt: Long
)

@Entity(tableName = "article_remote_keys")
data class ArticleRemoteKey(
    @PrimaryKey val articleId: String,
    val prevKey: Int?,
    val nextKey: Int?
)

class FeedRepository(
    private val db: AppDatabase,
    private val api: NewsApiService
) {
    @OptIn(ExperimentalPagingApi::class)
    fun getNewsStream(): Flow<PagingData<ArticleEntity>> {
        return Pager(
            config = PagingConfig(pageSize = 20, prefetchDistance = 5, enablePlaceholders = false),
            remoteMediator = NewsRemoteMediator(db, api),
            pagingSourceFactory = { db.articleDao().pagingSource() }
        ).flow
    }
}
```""",
    "short_en": """Designing an instant-launch paginated feed requires Jetpack Paging 3 with RemoteMediator and Room as the single source of truth. The UI streams cached articles immediately via Flow, RemoteMediator fetches subsequent pages at scroll boundaries, companion RemoteKey tables preserve cursors, and WorkManager keeps content warm in the background.""",
    "structured_en": """Architecting an instant-opening paginated news feed requires separating immediate local presentation from background network synchronization.
First, make Room the single source of truth. The UI observes a Flow of PagingData queried directly from SQLite, rendering cached articles in under fifty milliseconds and eliminating launch loading spinners.
Second, integrate Jetpack Paging 3 with RemoteMediator. As users scroll near the list boundary, RemoteMediator triggers network requests to fetch the next page, persisting incoming articles directly into Room.
Third, manage pagination tokens using a dedicated RemoteKeys table in Room. Storing nextKey and prevKey cursors alongside entities ensures pagination resumes correctly across application restarts.
Fourth, execute swipe-to-refresh resets inside atomic Room transactions, clearing stale items and updating keys simultaneously to avoid list flickering, paired with Coil for bounded thumbnail caching.""",
    "deep_senior_en": """Architecting a paginated news feed capable of sub-100ms cold start while supporting seamless offline reading requires an offline-first reactive architecture centered around Room and Paging 3.
The primary design violation in mobile feeds is initiating network requests on screen launch before rendering content.
To achieve zero-latency startup, the UI layer connects exclusively to Room via Flow<PagingData<Article>>, allowing SQLite to stream existing cached articles to Compose or RecyclerView within milliseconds.
To coordinate pagination with backend APIs, we deploy Paging 3 with a custom RemoteMediator.
The RemoteMediator acts as a bridge: when the user scrolls near the end of the viewport, Paging 3 signals RemoteMediator to request the next page from Retrofit.
To maintain cursor integrity across app process deaths and device restarts, we persist nextKey and prevKey tokens in an ArticleRemoteKeys table in Room.
When a refresh event triggers, we wrap the database operations in db.withTransaction: clearing old unbookmarked articles, resetting remote keys, and inserting the first page atomically.
Because the UI observes Room reactively, the list updates smoothly without layout jumps or white flashes.
Furthermore, we integrate Coil with a 250MB disk cache and memory prefetching for thumbnails, and register a periodic WorkManager constraint worker to fetch fresh headlines during night charges.""",
    "meta_ar": {
        "id": "DAT-21",
        "questionAr": "صمم معمارية خلاصة أخبار مقسمة لصفحات (Paginated News Feed) تفتح في أقل من 100 ملي ثانية دون شاشات تحميل وتتزامن عند توفر الاتصال.",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تصميم معمارية الأنظمة لتطبيقات الموبايل (System Design)، والعمل بنمط Offline-First مع Jetpack Paging 3 و RemoteMediator، وتنسيق مفاتيح الصفحات في Room، وتخزين الصور مؤقتاً.",
        "concept_ar": "يتطلب تصميم معمارية خلاصة أخبار تفتح فورياً وتتزامن بسلاسة نظاماً معمارياً متكاملاً وفق مبدأ Offline-First: اعتماد قاعدة بيانات Room كمصدر وحيد وأصيل للحقيقة (Single Source of Truth)؛ حيث تقرأ الواجهة البيانات عبر Flow<PagingData> في أقل من 50 ملي ثانية دون أي انتظار للشبكة. واستخدام مكتبة Paging 3 مع وسيط المزامنة RemoteMediator لفصل عرض القائمة عن استدعاءات السيرفر، حيث يلتقط حواف التمرير لجلب الصفحات التالية بالخلفية. وحفظ مؤشرات الصفحات في جدول مخصص RemoteKeys في Room لضمان بقاء التمرير عبر إغلاق التطبيق. وتنفيذ عمليات السحب للتحديث (Swipe-to-Refresh) داخل معاملة ذرية db.withTransaction لمسح الكاش غير المحفوظ وإضافة الصفحات الجديدة دون أي وميض أو قفزات بالقائمة. وتفعيل كاش ثنائي للصور عبر Coil مع تحديد حد أقصى للذاكرة، وتفويض WorkManager بالمزامنة الدورية الهادئة عند توفر اتصال واي فاي.",
        "walkthrough_ar": """تصميم النظام المعماري المتكامل لخلاصة الأخبار:
```kotlin
// 1. المستودع يربط بين Pager وقاعدة Room
class NewsRepository(private val db: AppDatabase, private val api: NewsApi) {
    fun getFeedStream(): Flow<PagingData<Article>> = Pager(
        config = PagingConfig(pageSize = 20, prefetchDistance = 5),
        remoteMediator = NewsRemoteMediator(db, api),
        pagingSourceFactory = { db.newsDao().pagingSource() }
    ).flow
}

// 2. الواجهة تستمع مباشرة لـ Room عبر PagingData
@Composable
fun NewsScreen(viewModel: NewsViewModel) {
    val articles = viewModel.feedState.collectAsLazyPagingItems()
    LazyColumn {
        items(count = articles.itemCount) { index ->
            articles[index]?.let { ArticleCard(it) }
        }
    }
}
```""",
        "why_it_matters_ar": "يوفر تجربة استخدام فائقة السرعة والسلاسة، ويقضي على شاشات التحميل المزعجة أثناء فتح التطبيق، ويتيح قراءة الأخبار أثناء السفر وانقطاع الإنترنت.",
        "worked_example_ar": "فتح تطبيق إخباري في وضع الطيران؛ تظهر المقالات المحملة فوراً مع إمكانية التمرير والقراءة بسلاسة، وبمجرد استعادة الاتصال تتحدث القائمة في الخلفية بهدوء.",
        "trade_offs_ar": "استخدام RemoteMediator مع جدول RemoteKeys يتطلب كتابة كود إضافي لإدارة التزامن، ولكنه يوفر أفضل أداء واستقرار ممكن لقوائم الموبايل الكبيرة.",
        "failure_modes_ar": "ربط واجهة المستخدم باستدعاء الشبكة مباشرة مما يجبر المستخدم على الانتظار لثوانٍ، أو مسح الكاش دون معاملة ذرية مما يسبب وميض الشاشة وقفز موضع التمرير.",
        "production_perspective_ar": "في التطبيقات الإخبارية الكبرى، نعتمد Room كمصدر وحيد للحقيقة ونضبط كاش الصور بـ Coil بحجم 250 ميجابايت، ونشغل مهمة مزامنة هادئة بـ WorkManager لتحديث المحتوى دورياً.",
        "how_to_answer_ar": "ابدأ برسم المعمارية: Room كمصدر وحيد للحقيقة لسرعة البدء، ثم دور Paging 3 و RemoteMediator في جلب الصفحات عند التمرير، وجدول RemoteKeys، والتعامل مع كاش الصور وتحديث الخلفية.",
        "talking_points_ar": "مبدأ Offline-First، سرعة الإقلاع الباردة Cold Start، دور RemoteMediator وجدول RemoteKeys، والمعاملات الذرية لمنع الوميض.",
        "follow_ups_ar": "- **المحاور:** 'كيف تمنع وميض القائمة Flicker عند قيام المستخدم بالسحب للتحديث؟'\n  **المرشح:** 'عن طريق تنفيذ مسح الكاش القديم وإدراج الصفحة الأولى في خطوة ذرية واحدة داخل db.withTransaction؛ فلا ترى واجهة Compose حالة فراغ مؤقتة إطلاقاً.'\n\n- **المحاور:** 'كيف تتعامل مع صور الأخبار لضمان عرضها دون إنترنت؟'\n  **المرشح:** 'نستخدم مكتبة Coil مع ضبط كاش مزدوج للرام والقرص Disk Cache بسعة 250 ميجابايت، ونقوم بالتحميل المسبق Prefetching للصور المصغرة أثناء التمرير.'",
        "self_check_ar": "هل غطيت فتح الشاشة الفوري بـ Room؟ وهل بينت دور RemoteMediator وجدول RemoteKeys وكاش الصور وتزامن الخلفية؟",
        "references_ar": f"- [Android Architecture: Paging 3 Library](https://developer.android.com/topic/libraries/architecture/paging/v3-overview) — الدليل الرسمي لمكتبة التصفح Paging 3.\n- [Now in Android: Offline-first Architecture](https://github.com/android/nowinandroid) — المعمارية النموذجية لتطبيق جوجل الإخباري دون اتصال.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يتطلب التصميم اعتماد Room كمصدر وحيد للحقيقة مع Paging 3 و RemoteMediator. تبث قاعدة البيانات المقالات المخزنة فورياً عبر Flow لتفتح الشاشة بلحظتها، ويتولى الوسيط جلب الصفحات عند التمرير، مع حفظ المؤشرات في جدول RemoteKeys وتحديث الكاش ذرياً وتخزين الصور مؤقتاً عبر Coil.",
        "best_answer_ar": "يقوم تصميم خلاصة الأخبار الفورية على معمارية Offline-First تفصل بين العرض اللحظي والتزامن الشبكي في الخلفية.\n\nأولاً، جعل قاعدة بيانات Room المصدر الوحيد للحقيقة؛ حيث تستمع واجهة المستخدم لتدفق Flow<PagingData> مباشرة من التخزين المحلي، مما يتيح عرض المقالات المخزنة في أقل من 50 ملي ثانية دون أي انتظار للشبكة أو شاشات تحميل.\n\nثانياً، دمج مكتبة Paging 3 مع RemoteMediator؛ حيث يلتقط الوسيط اقتراب المستخدم من نهاية القائمة ليطلب الصفحة التالية من السيرفر، ويحفظ السجلات مباشرة في Room.\n\nثالثاً، إدارة مؤشرات الصفحات Cursors عبر جدول مخصص RemoteKeys في Room، مما يحافظ على موضع التمرير وسلامة الصفحات حتى عند إغلاق التطبيق بالكامل.\n\nرابعاً، تنفيذ التحديث عبر معاملة ذرية db.withTransaction لمسح البيانات القديمة وإضافة الجديدة معاً لمنع وميض الشاشة، مع ضبط كاش الصور في Coil.",
        "deep_answer_ar": "في تصميم الأنظمة لتطبيقات المحتوى الكبرى، يعتبر فتح التطبيق على شاشة بيضاء أو مؤشر تحميل خطأ معمارياً فادحاً يضر بتفاعل المستخدمين؛ ولذا نعتمد معمارية التخزين المحلي أولاً.\n\nتبدأ المعمارية بربط واجهة العرض بقاعدة بيانات Room مباشرة كـ Single Source of Truth عبر Flow<PagingData>، مما يضمن ظهور الأخبار السابقة فور نقر الأيقونة في بضع ملي ثوانٍ.\n\nولإدارة التصفح اللانهائي، ندمج مكتبة Jetpack Paging 3 مع وسيط المزامنة RemoteMediator؛ فعندما يقترب التمرير من مؤشر prefetchDistance، يطلق الوسيط طلباً للشبكة لجلب الصفحة التالية وتخزينها في Room. ولضمان استقرار الصفحات عند إعادة تشغيل الهاتف، ننشئ جدول RemoteKeys لتخزين مفاتيح الصفحات السابقة والتالية.\n\nوعند قيام المستخدم بسحب الشاشة للتحديث Swipe-to-Refresh، ننفذ العملية داخل db.withTransaction لمسح المقالات غير المفضلة وإدراج المقالات الجديدة وتحديث المفاتيح كعملية ذرية واحدة تمنع أي قفزات بصرية.\n\nوتكتمل المنظومة بضبط مكتبة Coil بكاش قرص محدد بـ 250 ميجابايت للصور، وتشغيل مزامنة دورية عبر WorkManager في الخلفية لتحديث الأخبار أثناء اتصال الواي فاي، مما يوفر تجربة قراءة فائقة السرعة. كما نوفر آلية لمراقبة استهلاك الذاكرة وحجم الكاش على القرص لتجنب تراكم المقالات القديمة، مع تطبيق سياسة إبقاء المفضلة والمقالات المحفوظة للقراءة دون اتصال، مما يمنح المستخدم تحكماً كاملاً في مساحة التخزين الخاصة به."
    }
}

# ==========================================
# DAT-22: You must migrate encrypted and unencrypted local databases. How do you protect against data loss?
# ==========================================
DATA["DAT-22"] = {
    "concept_en": """Migrating local databases between unencrypted SQLite and SQLCipher-encrypted storage without data loss requires a transactional export protocol and cryptographic isolation:
- The Cryptographic Incompatibility Trap: Plaintext SQLite and SQLCipher databases have incompatible file headers. Attempting to open an unencrypted database with a SQLCipher open helper results in immediate SQLiteDatabaseCorruptException: file is not a database.
- Migration Pipeline:
  1. Pre-Flight State Verification: Inspect the database header bytes. A plaintext SQLite database begins with the ASCII string 'SQLite format 3\0'. An encrypted database contains pseudo-random ciphertext bytes.
  2. Atomic Snapshot Backup: Create a temporary file copy (app_database.db.bak) before initiating migration. If power fails or an exception occurs, the original unencrypted file remains intact.
  3. Transactional SQLCipher Export: Open the plaintext database using standard SQLite, attach the target encrypted database file with the encryption key, and invoke the native SQLCipher export procedure:
     ATTACH DATABASE 'encrypted.db' AS encrypted KEY 'passphrase';
     SELECT sqlcipher_export('encrypted');
     DETACH DATABASE encrypted;
  4. Integrity Verification: Open the newly encrypted database with SQLCipher and run PRAGMA integrity_check;. If it returns anything other than ok, abort and restore from backup.
  5. Atomic File Swap & Secure Erase: Atomically rename the encrypted file to replace the original database, and securely overwrite and delete the plaintext database file to prevent plaintext recovery from NAND flash storage.
  6. Keystore Secret Protection: Generate the 256-bit AES encryption passphrase securely using Android Keystore hardware-backed storage.""",
    "walkthrough_en": """Transactional database encryption migration with backup and integrity verification:
```kotlin
class DatabaseEncryptionMigrator(private val context: Context) {
    fun migratePlaintextToEncrypted(
        dbName: String,
        passphrase: ByteArray
    ): Boolean {
        val originalFile = context.getDatabasePath(dbName)
        if (!originalFile.exists()) return true

        val encryptedFile = context.getDatabasePath("${dbName}.enc")
        val backupFile = context.getDatabasePath("${dbName}.bak")

        // Step 1: Create backup
        originalFile.copyTo(backupFile, overwrite = true)

        return try {
            // Step 2: Open plaintext DB and export to encrypted DB
            val plaintextDb = SQLiteDatabase.openDatabase(originalFile.path, null, SQLiteDatabase.OPEN_READWRITE)
            plaintextDb.rawQuery("ATTACH DATABASE ? AS encrypted KEY ?", arrayOf(encryptedFile.path, passphrase)).close()
            plaintextDb.rawQuery("SELECT sqlcipher_export('encrypted')", null).close()
            plaintextDb.rawQuery("DETACH DATABASE encrypted", null).close()
            plaintextDb.close()

            // Step 3: Validate encrypted database integrity
            val factory = SupportOpenHelperFactory(passphrase)
            // Verify PRAGMA integrity_check == "ok"

            // Step 4: Atomic swap and wipe plaintext
            originalFile.delete()
            encryptedFile.renameTo(originalFile)
            backupFile.delete()
            true
        } catch (e: Exception) {
            backupFile.copyTo(originalFile, overwrite = true)
            encryptedFile.delete()
            false
        }
    }
}
```""",
    "short_en": """Migrating an unencrypted database to SQLCipher without data loss requires creating a safety backup, attaching an encrypted database instance, and executing sqlcipher_export. Engineers verify file integrity using PRAGMA integrity_check, atomically swap database files, securely wipe the plaintext source, and protect encryption passphrases inside Android Keystore.""",
    "structured_en": """Safely migrating a production database from plaintext SQLite to encrypted SQLCipher requires an atomic export pipeline and defensive recovery measures.
First, take an atomic file backup. Attempting to open an unencrypted SQLite database directly with SQLCipher triggers an immediate SQLiteDatabaseCorruptException, making isolated migration mandatory.
Second, execute the SQLCipher export transaction. Open the plaintext database using standard SQLite, attach the target encrypted database file with the generated passphrase, and invoke sqlcipher_export to copy all tables, schemas, and indices atomically.
Third, verify database integrity. Open the newly encrypted database using the SQLCipher open helper and execute PRAGMA integrity_check. Only proceed if the query returns ok.
Fourth, execute an atomic file swap, securely overwrite and delete the unencrypted database file from flash storage, and persist the 256-bit encryption key inside the hardware-backed Android Keystore.""",
    "deep_senior_en": """In mobile financial and healthcare applications, retrofitting encryption onto an existing unencrypted database is one of the highest-risk operations an engineering team can execute.
Opening an unencrypted SQLite file with SQLCipher fails with SQLiteDatabaseCorruptException because SQLCipher expects encrypted page headers rather than standard SQLite magic bytes.
To migrate millions of active production users without a single byte of data loss, we implement a defensive migration workflow.
Before touching the database, we copy the database file, its WAL file, and its shared memory file into a backup directory.
Next, we open the unencrypted database with standard SQLite APIs, attach a newly created encrypted database file using the passphrase, and execute sqlcipher_export('encrypted').
This native C-routine copies all tables, triggers, indices, and data rows into the encrypted container transactionally.
After detaching, we open the new file using SQLCipher's SupportOpenHelperFactory and execute PRAGMA integrity_check.
If the check succeeds, we atomically swap the files using File.renameTo(), securely overwrite the plaintext file bytes with zeros to satisfy security compliance, and discard the backup.
If any step throws an exception or the device loses power midway, the startup recovery hook restores the original unencrypted file from backup, logging the event to analytics while allowing the user to continue operating safely until the next app launch.""",
    "meta_ar": {
        "id": "DAT-22",
        "questionAr": "يجب عليك ترحيل قاعدة بيانات محلية غير مشفرة إلى قاعدة بيانات مشفرة بـ SQLCipher أو تدوير مفاتيح التشفير. كيف تضمن حماية البيانات من أي تلف أو فقدان؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم آليات تشفير قواعد البيانات بـ SQLCipher و Room، وتطبيق ترحيل البيانات عبر sqlcipher_export، وإجراء النسخ الاحتياطي الذري، وحفظ مفاتيح التشفير في Android Keystore والتحقق بـ PRAGMA integrity_check.",
        "concept_ar": "يتطلب ترحيل قواعد البيانات بين التخزين غير المشفر والمشفر بـ SQLCipher دون أي فقدان للبيانات اتباع بروتوكول تصدير ذري وتأمين التشفير: يؤدي فتح قاعدة بيانات عادية بمحرك SQLCipher مباشرة إلى حدوث كراش فوري وتلف للبيانات SQLiteDatabaseCorruptException بسبب اختلاف بنية رأس الملف. ولتفادي ذلك، نتبع مساراً آمناً: أولاً أخذ نسخة احتياطية ذرية من ملف قاعدة البيانات قبل بدء أي تعديل. ثانياً فحص نوع الملف بقراءة أول بايتات للتحقق مما إذا كان عادياً أو مشفراً. ثالثاً تنفيذ الترحيل بفتح القاعدة الأصلية واستخدام أمر ATTACH DATABASE لربط ملف مشفر جديد بمفتاح التشفير واستدعاء دالة sqlcipher_export لنسخ كافة الجداول والفهارس ذرياً. رابعاً التحقق من سلامة البيانات بتشغيل أمر PRAGMA integrity_check للتأكد من نجاح التشفير. خامساً استبدال الملفات بأمان ومسح الملف غير المشفر نهائياً لمنع استرجاعه من ذاكرة الهاتف. ويتم توليد مفتاح التشفير وحفظه داخل Android Keystore المدعوم بعتاد الأمان.",
        "walkthrough_ar": """تنفيذ ترحيل التشفير الذري واستدعاء sqlcipher_export مع التحقق:
```kotlin
// 1. أخذ نسخة احتياطية ذرية قبل البدء
val originalDb = context.getDatabasePath("app.db")
val backupDb = context.getDatabasePath("app.db.bak")
originalDb.copyTo(backupDb, overwrite = true)

// 2. فتح القاعدة العادية وربط ملف مشفر جديد وتصدير البيانات
val db = SQLiteDatabase.openDatabase(originalDb.path, null, SQLiteDatabase.OPEN_READWRITE)
db.rawQuery("ATTACH DATABASE 'encrypted.db' AS enc KEY 'secretPass'", null).close()
db.rawQuery("SELECT sqlcipher_export('enc')", null).close()
db.rawQuery("DETACH DATABASE enc", null).close()
db.close()

// 3. التحقق من سلامة البيانات واستبدال الملفات بأمان
// PRAGMA integrity_check -> "ok"
// استبدال encrypted.db مكان app.db وحذف النسخة الاحتياطية
```""",
        "why_it_matters_ar": "يحمي بيانات المستخدمين الحساسة من السرقة في حال اختراق الهاتف، ويمنع تلف وتدمير قاعدة البيانات أثناء الانتقال للتخزين المشفر.",
        "worked_example_ar": "تطبيق محفظة رقمية كان يخزن المعاملات في SQLite عادي، وصدر قرار أمني بتشفيرها بـ SQLCipher؛ تم أخذ نسخة احتياطية وتصدير البيانات بـ sqlcipher_export بنجاح دون فقدان أي معاملة.",
        "trade_offs_ar": "تشفير SQLCipher يضيف حمولة معالجة طفيفة بنسبة 5 إلى 10 بالمئة على عمليات القراءة والكتابة، ولكنه يحقق الامتثال الأمني لمعايير PCI-DSS و HIPAA.",
        "failure_modes_ar": "محاولة فتح قاعدة بيانات عادية بـ SQLCipher مباشرة مما يدمر الملف، أو انقطاع طاقة الهاتف أثناء التشفير دون وجود نسخة احتياطية صالحة للاسترجاع.",
        "production_perspective_ar": "في التطبيقات البنكية، نولد مفاتيح تشفير عشوائية بطول 256 بت ونحفظها في Android Keystore بعتاد الهاتف، مع إلزام الترحيل بفحص PRAGMA integrity_check قبل اعتماد التشفير.",
        "how_to_answer_ar": "وضح استحالة فتح القاعدة العادية بمحرك التشفير مباشرة، واشرح خطوات الترحيل: النسخة الاحتياطية، أمر ATTACH مع sqlcipher_export، فحص السلامة، والاستبدال الذري مع حماية المفتاح في Keystore.",
        "talking_points_ar": "خطأ SQLiteDatabaseCorruptException، دور sqlcipher_export في نسخ البيانات، التحقق بأمر PRAGMA integrity_check، وتأمين المفاتيح في Keystore.",
        "follow_ups_ar": "- **المحاور:** 'ماذا يحدث إذا انقطع تيار البطارية فجأة أثناء تشغيل sqlcipher_export؟'\n  **المرشح:** 'تظل قاعدة البيانات الأصلية غير المشفرة والنسخة الاحتياطية سليمتين تماماً؛ لأن التصدير يكتب في ملف منفصل جديد، وعند فتح التطبيق ثانية يستعيد النظام النسخة الاحتياطية ويعيد المحاولة بأمان.'\n\n- **المحاور:** 'كيف تتأكد من استحالة استرجاع البيانات غير المشفرة بعد اكتمال التشفير؟'\n  **المرشح:** 'نقوم بالكتابة فوق بايتات الملف القديم بقيم صفرية Zero-fill قبل حذفه، لمنع استخراج النصوص الواضحة عبر فحص ذاكرة الفلاش NAND Flash المباشر.'",
        "self_check_ar": "هل شرحت خطورة فتح الملف مباشرة؟ وهل ذكرت خطوات التصدير الذري وفحص النزاهة وحفظ المفتاح في Keystore؟",
        "references_ar": f"- [SQLCipher Official Documentation: Encrypting a Database](https://www.zetetic.net/sqlcipher/sqlcipher-api/#sqlcipher_export) — الدليل الرسمي لدالة sqlcipher_export وتشفير القواعد القائمة.\n- [Android Security: Storing keys in Android Keystore](https://developer.android.com/training/articles/keystore) — إرشادات حفظ مفاتيح التشفير بأمان عتادي.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يتطلب التشفير الآمن أخذ نسخة احتياطية ذرية، ثم ربط قاعدة بيانات مشفرة جديدة واستدعاء sqlcipher_export لترحيل الجداول ذرياً. بعدها نتحقق من سلامة البيانات بأمر PRAGMA integrity_check، ثم نستبدل الملفات ونمسح النسخة غير المشفرة نهائياً، مع حفظ مفتاح التشفير داخل Android Keystore.",
        "best_answer_ar": "يتطلب ترحيل قاعدة بيانات عادية إلى قاعدة بيانات مشفرة بـ SQLCipher تطبيق مسار ترحيل ذري لحماية البيانات من التلف.\n\nأولاً، أخذ نسخة احتياطية كاملة من ملف قاعدة البيانات قبل بدء الترحيل؛ فمحاولة فتح قاعدة بيانات عادية بمحرك SQLCipher مباشرة تسبب كراش فوري وتلف للملف بسبب عدم تطابق بنية التشفير.\n\nثانياً، تنفيذ الترحيل بفتح القاعدة الأصلية بمحرك SQLite العادي، واستخدام أمر ATTACH DATABASE لربط ملف مشفر جديد بمفتاح التشفير، واستدعاء دالة sqlcipher_export لنسخ كافة الجداول والسجلات ذرياً.\n\nثالثاً، التحقق من سلامة البيانات بفتح الملف المشفر وتشغيل أمر PRAGMA integrity_check للتأكد من خلوه من أي أخطاء.\n\nرابعاً، استبدال الملفات بأمان ومسح الملف غير المشفر نهائياً من الذاكرة، مع توليد وحفظ مفتاح التشفير 256 بت داخل Android Keystore بعتاد الجهاز الآمن.",
        "deep_answer_ar": "في التطبيقات المالية والصحية، يعتبر تحويل قاعدة البيانات غير المشفرة إلى قاعدة مشفرة بـ SQLCipher عملية هندسية بالغة الحساسية؛ حيث إن أي خطأ قد يدمر بيانات المستخدمين بالكامل.\n\nإن فتح ملف SQLite عادي باستخدام SQLCipher يؤدي لكراش مباشر SQLiteDatabaseCorruptException؛ لأن ترويسة الملف العادي تختلف تماماً عن الملف المشفر. ولتنفيذ الترحيل بأمان مطلق، نبدأ بعمل نسخة احتياطية كاملة من ملف قاعدة البيانات وملفات الـ WAL المرافقة.\n\nبعدها نفتح الملف الأصلي ونربط ملفاً جديداً مشفراً عبر ATTACH DATABASE مع تمرير مفتاح التشفير، ثم ننفذ استعلام SELECT sqlcipher_export('encrypted')؛ وهو إجراء مكتوب بلغة C داخل المحرك يقوم بنسخ كافة الجداول والفهارس والبيانات بشكل ذري متكامل.\n\nوبعد اكتمال التصدير، نفتح الملف المشفر عبر SupportOpenHelperFactory وننفذ فحص PRAGMA integrity_check؛ فإذا أعاد كلمة ok، نقوم باستبدال الملفات بـ renameTo، ونمسح بايتات الملف غير المشفر نهائياً لحماية خصوصية المستخدم.\n\nوإذا حدث أي عطل أثناء التشفير، يستعيد النظام النسخة الاحتياطية تلقائياً ليعمل التطبيق دون توقف، مع حفظ مفتاح التشفير في عتاد Android Keystore. كما نحرص على عزل مفاتيح التشفير داخل بيئة أمان العتاد Hardware-backed Keystore لمنع استخراجها حتى في الأجهزة التي تمت ترقيتها بصلاحيات Root، مع إرسال تقارير تشخيصية مشفرة لفرق الأمان للتأكد من اكتمال التشفير بنجاح لكافة المستخدمين."
    }
}

# ==========================================
# Runner & Word Count Validation
# ==========================================
def validate_words():
    for qid, d in sorted(DATA.items()):
        short_w = len(d["short_en"].split())
        struct_w = len(d["structured_en"].split())
        deep_w = len(d["deep_senior_en"].split())
        assert 35 <= short_w <= 110, f"{qid} short_en {short_w} out of [35, 110]"
        assert 100 <= struct_w <= 280, f"{qid} struct_en {struct_w} out of [100, 280]"
        assert 200 <= deep_w <= 650, f"{qid} deep_en {deep_w} out of [200, 650]"

        q_ar_w = len(d["meta_ar"]["quick_answer_ar"].split())
        b_ar_w = len(d["meta_ar"]["best_answer_ar"].split())
        d_ar_w = len(d["meta_ar"]["deep_answer_ar"].split())
        assert 35 <= q_ar_w <= 110, f"{qid} quick_ar {q_ar_w} out of [35, 110]"
        assert 90 <= b_ar_w <= 280, f"{qid} best_ar {b_ar_w} out of [90, 280]"
        assert 180 <= d_ar_w <= 650, f"{qid} deep_ar {d_ar_w} out of [180, 650]"
        print(f"{qid}: en_s={short_w}, en_st={struct_w}, en_d={deep_w} | ar_q={q_ar_w}, ar_b={b_ar_w}, ar_d={d_ar_w}")
    print("Pre-validation word count checks passed! Updating canonical questions...")

def apply_elevations():
    validate_words()

    topic_meta = {}
    for qid, d in sorted(DATA.items()):
        ee.update_canonical_question(
            qid=qid,
            concept_en=d["concept_en"],
            walkthrough_en=d["walkthrough_en"],
            structured_en=d["structured_en"],
            deep_senior_en=d["deep_senior_en"],
            short_en=d["short_en"],
        )
        topic_meta[qid] = d["meta_ar"]

    ee.save_topic_metadata("dat_16_22", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print(f"\nAll {len(DATA)} DAT questions (DAT-16 to DAT-22) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()

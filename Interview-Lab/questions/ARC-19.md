---
id: "ARC-19"
question: "How do you handle cache and server updates within the data layer?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "B"
phase: 2
priority: "P1"
order: 164
editorial_status: "reviewed"
---

# ARC-19

## Original interview question

How do you handle cache and server updates within the data layer?

## What the interviewer evaluates

Design cache/server synchronization with a source of truth, stale policy, conflict rules and errors.

## Explanation in Arabic

كيف تدير تحديثات الكاش (Cache) والسيرفر (Server) داخل طبقة البيانات (Data Layer) باحترافية؟

1. استراتيجيات مزامنة البيانات الشائعة:
   - **Network-Bound Resource (Offline-First / Cache-First)**:
     * نقرأ ونعرض البيانات المحفوظة محلياً في الـ Database فوراً للمستخدم.
     * في نفس الوقت نطلب أحدث البيانات من السيرفر في الخلفية.
     * عند نجاح الطلب، نحدث الـ Database محلياً، فتقوم قاعدة البيانات بإطلاق تحديث تلقائي للواجهة.
   - **Cache-Aside / Read-Through**:
     * فحص الكاش في الذاكرة أولاً؛ إذا كانت منتهية الصلاحية (Stale)، يتم طلب السيرفر وتحديث الكاش.
   - **Optimistic Updates (التحديث التفاؤلي)**:
     * عند اتخاذ المستخدم لإجراء (مثل عمل Like لبوست)، نقوم بتحديث الـ Database المحلية والـ UI فوراً دون انتظار رد السيرفر!
     * إذا فشل طلب السيرفر لاحقاً، نقوم بالتراجع (Rollback) وإظهار تنبيه للمستخدم.

2. دور الـ Invalidation Tracker وإدارة تضارب التعديلات:
   - استخدام الـ ETag و `If-None-Match` في طلبات HTTP لتجنب تنزيل البيانات غير المعدلة (304 Not Modified).
   - إدارة المعاملات في قاعدة البيانات عبر `@Transaction` لضمان كتابة البيانات دفعة واحدة دون تشويه الحالة.

## Practical walkthrough

تنفيذ نمط Network-Bound Resource وتحديث الـ Cache في طبقة البيانات:
```kotlin
class ProductRepositoryImpl(
    private val localDao: ProductDao,
    private val remoteApi: ProductApi
) : ProductRepository {

    // نمط Offline-First: يقرأ من DB فوراً، ويطلب السيرفر ويحدث DB عند النجاح:
    override fun getProducts(): Flow<Resource<List<Product>>> = flow {
        // 1. انبعاث البيانات المتاحة في الكاش فوراً:
        val cached = localDao.getProductsSync().map { it.toDomain() }
        emit(Resource.Loading(cached))

        try {
            // 2. جلب أحدث البيانات من السيرفر:
            val remoteDtos = remoteApi.fetchProducts()
            // 3. تحديث قاعدة البيانات داخل Transaction:
            localDao.updateProductsTransaction(remoteDtos.map { it.toEntity() })
        } catch (e: Exception) {
            emit(Resource.Error(e.message ?: "Sync failed", cached))
        }

        // 4. انبعاث البيانات النهائية المحدثة من الـ DB:
        emitAll(localDao.observeProducts().map { Resource.Success(it.map { e -> e.toDomain() }) })
    }
}
```

## Why it matters and how it works

A repository coordinates local and remote sources and gives consumers one observation contract. Offline-first guidance favors a local source of truth. Sync must define write order, staleness, conflict handling and failure behavior.

## Worked example

Conceptual flow: `observeProducts()` reads Room Flow; `refreshProducts()` fetches API pages and writes validated entities in a Room transaction. UI sees the database stream. A failed refresh leaves cached products visible with an error/freshness indicator.

## Trade-offs and decision criteria

Local-first design improves offline UX but adds storage, migration and sync complexity. A simple online-only screen may fetch directly through a repository without a database. Choose based on offline requirements and data authority.

## Failure modes

Two refreshes race: older response arrives last and overwrites newer status. Compare server versions or serialize writes; do not trust client wall-clock alone. Another failure is clearing cache before refresh succeeds, leaving an empty screen offline.

## Production perspective

A delivery app stores route tasks in Room for offline display and queues permitted edits with IDs; server reconciliation resolves conflicts. Sensitive server-authoritative status is confirmed before showing final completion.

## Interview answer — short

Manage cache and server updates within the data layer using the Offline-First (Network-Bound Resource) pattern: emit local cached data from Room immediately, fetch updates from the network in the background, write payloads into the database inside a transaction, and let Room reactively emit updated state.

## Interview answer — structured

Managing cache and server synchronization is the primary responsibility of the Data layer, isolating presentation code from networking and storage complexity.

First, **The Offline-First (Network-Bound Resource) Pattern**. Next, an Immediate Local Emission is the repository reads from the local database (Room) and emits cached data immediately, providing instantaneous screen loads.
Additionally, with Background Synchronization, concurrently, the repository triggers an asynchronous network fetch. With Atomic Ingestion, when the network succeeds, the repository writes the new entities into Room inside a database transaction (`@Transaction`), clearing obsolete records.
With Reactive Propagation, Room's `InvalidationTracker` detects the write and emits the fresh dataset on the active `Flow`, updating observers automatically. **Optimistic Updates**.
For interactive user mutations (e.g. Liking a post or archiving an email), waiting for server roundtrips introduces unacceptable UI latency. Finally, the repository modifies local database state immediately. If the network request fails, the repository rolls back the mutation and surfaces an actionable error.


## Interview answer — deep senior

Under the hood, HTTP cache headers play a pivotal role. By configuring OkHttp's `Cache` directory and leveraging `ETag` and `If-None-Match` headers, the server can return HTTP `304 Not Modified` with zero body payload. This conserves battery and mobile bandwidth while confirming that local cache is fresh.

For conflict resolution (when both client and server update data concurrently), enterprise repositories employ **Conflict Resolution Policies**.

First, *Server-Wins*: The default in most consumer apps; server timestamps overwrite local modifications. Next, *Client-Wins / Last-Write-Wins (LWW)*: Based on monotonic client timestamps.
Finally, *Merge Policies*: Employed in collaborative apps where fields are merged individually.

In testing, repository synchronization is verified by asserting that simulated network failures still yield cached data, and network successes overwrite stale database records.


## How to answer in the interview

- **Why:** cache/server races cause stale or lost data.
- **How:** define authority, write path and merge.
- **Trade-off:** offline speed versus consistency complexity.
- **Failure case:** refresh overwrites pending mutation.
- **Production solution:** transactional projection and conflict tests.

## Deep-dive talking points

Walk cache miss, successful refresh, stale data and racing refresh responses; define authority for payment status.

## Follow-up questions

- **Interviewer:** "What is an Optimistic Update, and how do you handle rollbacks?"
  **Answer:** "An optimistic update mutates the local database immediately to provide zero-latency UI feedback. If the subsequent network call fails, the repository executes a compensating transaction to revert the change and notify the UI."

- **Interviewer:** "Why should database writes be wrapped in `@Transaction`?"
  **Answer:** "Transactions ensure atomicity: either all records are updated or none are. If an error occurs halfway through, the database rolls back, preventing corrupt partial states."

## Self-check rubric

Describe one observable path, one conflict rule and the UI behavior after network failure with cached data.

## References and reviewed-on date

- [Android offline-first guide](https://developer.android.com/topic/architecture/data-layer/offline-first) — local source of truth and sync.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository role.

Technically reviewed against primary documentation on 2026-10-13.

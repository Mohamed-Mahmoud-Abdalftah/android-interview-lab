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

## Concept and technical explanation

Handling cache and server updates within the Data Layer requires establishing the local persistent database (such as Room) as the authoritative Single Source of Truth. In an offline-first architecture, read queries expose continuous Flow streams directly from local storage, allowing the UI to render cached data instantaneously without blocking on remote endpoints. When background synchronizations or explicit user refreshes fetch updated payloads from Retrofit, the repository writes the raw data into the local database inside an atomic transaction. Room's InvalidationTracker automatically detects the table mutations and pushes fresh data downstream to active UI collectors. For interactive user actions, repositories perform optimistic updates by mutating local storage immediately, rolling back changes with compensating transactions if subsequent network calls fail.

## Practical walkthrough (English)

Implementing offline-first cache and server synchronization in a repository:
```kotlin
class ProductRepositoryImpl(
    private val localDao: ProductDao,
    private val remoteApi: ProductApi,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) : ProductRepository {
    // 1. Single Source of Truth: UI always observes local Room database
    override fun observeProducts(): Flow<List<Product>> =
        localDao.observeAllProducts().map { entities -> entities.map { it.toDomain() } }

    // 2. Network sync writes directly into Room inside an atomic transaction
    override suspend fun syncProducts(): Result<Unit> = withContext(ioDispatcher) {
        runCatching {
            val networkDtos = remoteApi.fetchProducts()
            localDao.replaceProductsTransaction(networkDtos.map { it.toEntity() })
        }
    }

    // 3. Optimistic update: mutate local cache immediately, rollback on failure
    override suspend fun toggleFavorite(productId: String, isFav: Boolean): Result<Unit> = withContext(ioDispatcher) {
        localDao.updateFavoriteStatus(productId, isFav) // Immediate UI update via Room Flow
        runCatching {
            remoteApi.postFavoriteStatus(productId, isFav)
        }.onFailure {
            localDao.updateFavoriteStatus(productId, !isFav) // Compensating rollback on network error
        }
    }
}
```

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

Manage cache and server updates using an offline-first data layer where the local database serves as the single source of truth. The repository exposes a continuous Flow from Room, immediately delivering cached entities to the UI. Concurrently, it triggers background network synchronization, writing fresh remote payloads directly into the database within an atomic transaction. For user mutations, apply optimistic updates locally with compensating rollback mechanisms if network requests fail.

## Interview answer — structured

Handling cache and server synchronization is the primary responsibility of the data layer, isolating UI consumers from transport protocols and storage mechanics.
In an offline-first architecture, the local database acts as the authoritative source of truth. Repositories expose reactive Flow streams directly from persistent storage, guaranteeing instant UI loading with cached data upon screen launch.
Concurrently, the repository dispatches an asynchronous network fetch. When fresh payloads arrive from Retrofit, they are committed to the local database inside an atomic transaction. Room's internal invalidation tracker automatically detects table modifications and pushes fresh snapshots downstream to active collectors without requiring manual UI refresh coordination.
For interactive mutations, we utilize optimistic updates. The repository applies changes immediately to the local database so the interface reacts with zero perceived latency. If the backend network call fails, the repository triggers a compensating rollback and emits an error event. Furthermore, leveraging HTTP ETags and conditional headers avoids re-downloading unchanged server state.

## Interview answer — deep senior

Under the hood, orchestrating cache and remote synchronizations safely requires formalizing concurrency and conflict resolution. A common architectural defect is having repositories return combined network and database models directly into presentation coroutines, which invites race conditions when multiple screens request refreshes simultaneously.
By enforcing that all write operations route exclusively into persistent storage, the repository serializes mutations. Room handles atomic writes via transactions, guaranteeing that partial ingestion never leaves the local database in a corrupted state.
When dealing with concurrent modifications across distributed clients, repositories must implement explicit conflict resolution policies. In standard mobile workflows, server-authoritative reconciliation takes precedence, where incoming server records overwrite local drafts. However, in collaborative or offline-heavy enterprise applications, field-level merge strategies or last-write-wins based on monotonic server sequence numbers prevent local edits from obliterating remote changes.
At the HTTP layer, configuring an OkHttp Cache alongside ETag and If-None-Match headers allows the backend to respond with HTTP 304 Not Modified. This conserves mobile bandwidth, reduces radio wakeup cycles, and confirms cache validity with zero payload parsing overhead.
Staff engineers also safeguard against racing sync responses by attaching client-side sequence counters or timestamps to outbound requests. If an older network response arrives after a newer one has already been committed, the data layer identifies the stale generation and silently discards the payload, guaranteeing monotonic state progression.

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

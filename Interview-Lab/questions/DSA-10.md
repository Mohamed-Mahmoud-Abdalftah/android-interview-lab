---
id: "DSA-10"
question: "How do you design and analyze an LRU cache?"
topic: "Data Structures, Algorithms & Big O"
code: "DSA"
group: "B"
phase: 5
priority: "P2"
order: 449
editorial_status: "reviewed"
---

# DSA-10

## Original interview question

How do you design and analyze an LRU cache?

## What the interviewer evaluates

- O(1) lookup and recency update using map plus ordered links.
- Capacity, expiry, concurrency and Android cache policy.

## Explanation in Arabic

كيف تقوم بتصميم وتحليل كاش الـ LRU (Least Recently Used Cache) برمجياً، وما هو دوره في أندرويد؟

1. ما هو كاش الـ LRU؟
   - كاش ذو حجم ثابت ومحدود. عندما يمتلئ الكاش ونحتاج لإضافة عنصر جديد، نقوم بطرد العنصر **الأقل استخداماً في الآونة الأخيرة (Least Recently Used)**.
   - الشرط الهندسي الصارم: يجب أن تكون عمليتا القراءة (`get`) والإضافة والتحديث (`put`) في **وقت ثابت $O(1)$**.

2. هيكل البيانات المثالي لتحقيق $O(1)$:
   - **قائمة ثنائية الترابط (Doubly Linked List)**:
     * تحفظ ترتيب الاستخدام الزمني.
     * الرأس (Head): أحدث عنصر تم استخدامه (Most Recently Used).
     * الذيل (Tail): أقدم عنصر وأقلها استخداماً (Least Recently Used - المرشح للطرد).
     * ميزتها: إزالة أي عقدة أو إضافتها في البداية تتم في **$O(1)$** بشرط امتلاك مؤشر العقدة.
   - **خريطة هاش (HashMap)**:
     * تربط المفتاح (Key) بمؤشر العقدة في القائمة (`Node`).
     * ميزتها: البحث عن العقدة في **$O(1)$**.
   - في كوتلن/جافا القياسية: كلاس `LinkedHashMap(capacity, loadFactor, accessOrder = true)` يدمج كلا الهيكلين جاهزاً.

3. كاش الـ LruCache في أندرويد:
   - يوفر أندرويد `androidx.collection.LruCache`.
   - الاستخدام الأهم: كاش الصور (Bitmap Memory Cache). يتم قياس حجم الكاش بالبايت (`sizeOf { _, bitmap -> bitmap.byteCount }`) وتحديد حد أقصى (مثلاً $\frac{1}{8}$ من ذاكرة الـ Heap المتاحة) لمنع الـ OOM.

## Practical walkthrough

تصميم LRU Cache متكامل في كوتلن، واستخدام `LruCache` الرسمي في أندرويد:
```kotlin
// 1. تصميم LRU Cache من الصفر باستخدام Doubly LinkedList + HashMap:
class CustomLruCache<K, V>(private val capacity: Int) {
    private class Node<K, V>(val key: K, var value: V, var prev: Node<K, V>? = null, var next: Node<K, V>? = null)
    private val map = HashMap<K, Node<K, V>>()
    private val head = Node<K?, V?>(null, null)
    private val tail = Node<K?, V?>(null, null)

    init { head.next = tail; tail.prev = head }

    fun get(key: K): V? {
        val node = map[key] ?: return null
        moveToHead(node) // O(1) نقل للمقدمة كأحدث عنصر
        return node.value
    }

    fun put(key: K, value: V) {
        map[key]?.let {
            it.value = value
            moveToHead(it)
        } ?: run {
            if (map.size >= capacity) removeTail() // O(1) طرد الأقدم
            val newNode = Node(key, value)
            map[key] = newNode
            addToHead(newNode)
        }
    }

    private fun removeNode(node: Node<K, V>) {
        node.prev?.next = node.next
        node.next?.prev = node.prev
    }
    private fun addToHead(node: Node<K, V>) {
        node.next = head.next
        node.prev = head
        head.next?.prev = node
        head.next = node
    }
    private fun moveToHead(node: Node<K, V>) { removeNode(node); addToHead(node) }
    private fun removeTail() { tail.prev?.takeIf { it != head }?.let { removeNode(it); map.remove(it.key) } }
}
```

## Why it matters and how it works

A map alone gives lookup but not least-recent ordering; a list alone gives ordering but linear lookup. Combined, node removal and move are constant time if each node has previous/next links. Android LruCache provides a library implementation with synchronized operations under its documented contract.

## Worked example

Image thumbnail cache keyed by URL/size: `get` refreshes recency, `put` evicts until size budget. Do not cache full-resolution bitmaps with “100 entries” if each varies wildly in bytes. `LruCache` can size by `Bitmap.byteCount` where applicable.

## Trade-offs and decision criteria

LRU is simple but can evict frequently accessed items under scan workloads; LFU/TTL may fit other patterns. More cache memory reduces I/O but increases OOM pressure. Disk cache has different durability and eviction needs.

## Failure modes

A custom cache forgets to unlink node before reinserting, creating a cycle/leak. Concurrent get/put without lock corrupts list. Cache is not source of truth: process death clears it.

## Production perspective

Profile hit rate, byte use, GC and OOMs; cap by device class and clear on memory pressure as appropriate. Keep repository/network as authoritative source.

## Interview answer — short

An LRU cache maintains a fixed capacity, evicting the least recently accessed item when full. It achieves O(1) get and put operations by combining a Doubly Linked List (for O(1) access-order tracking) with a HashMap (for O(1) key-to-node lookups). Android provides this natively via androidx.collection.LruCache.

## Interview answer — structured

Designing an LRU cache requires coupling two data structures to guarantee constant-time access and eviction.

First, **The Combined Data Structure Architecture**. Next, a Doubly Linked List tracks recency of access. The most recently accessed node is placed at the head; the least recently accessed node sits at the tail. Given a direct node reference, unlinking and prepending operates in $O(1)$ without element shifting.
Additionally, with HashMap (`HashMap<Key, Node>`), maps keys directly to their corresponding doubly linked list node pointers, enabling $O(1)$ lookups. **Operational Workflow ($O(1)$ Time)**.
With get(key), lookup node in map. If present, unlink the node and move it to the head of the list; return value ($O(1)$). With put(key, value), if key exists, update value and move node to head. If absent, create new node, insert at head, and store in map. If size exceeds capacity, evict the tail node from both list and map in $O(1)$.
**Android Platform `LruCache`**. Finally, Android's `androidx.collection.LruCache` is internally backed by a Java `LinkedHashMap(capacity, 0.75f, true)` configured with `accessOrder = true`. It supports custom metric weighting via `sizeOf()`.


## Interview answer — deep senior

In Android production systems, LRU cache tuning determines stability against OutOfMemory crashes.

First, with Byte-Weighted Cache Sizing, when caching memory-heavy assets like Android `Bitmap`s, sizing by element count (`capacity = 50`) is fatal because a single uncompressed 4K Bitmap can consume 33MB of RAM while an icon consumes 10KB. Always override `sizeOf(key, value)` to return byte count, sizing the cache dynamically against available runtime memory: `val cacheSize = (Runtime.getRuntime().maxMemory() / 1024 / 8).toInt()`. Next, with Thread Safety, Android's `LruCache` methods are synchronized internally using intrinsic locks (`synchronized (this)`). If accessed across hundreds of parallel coroutine workers, lock contention can stall threads. High-concurrency systems use sharded LRU partitions or lock-free concurrent caches.
Finally, with Eviction Hooks (`entryRemoved`), in Android, when Bitmaps or native buffers are evicted from an LRU cache, overriding `entryRemoved(evicted, key, oldValue, newValue)` enables recycling pooled buffers (e.g. `BitmapPool`) to prevent memory allocation churn on subsequent renders.


## How to answer in the interview

- **Why:** cache improves repeated read latency.
- **How:** describe map plus recency and byte budget.
- **Trade-off:** hit rate versus memory pressure.
- **Failure case:** cache mistaken for durable ledger.
- **Production solution:** use LruCache and monitor eviction.

## Deep-dive talking points

Prompt for map+list mechanics, byte sizing, concurrency, process-death disposal.

## Follow-up questions

- **Interviewer:** "Why is a Doubly Linked List required instead of a Singly Linked List for an LRU Cache?"
  **Answer:** "Because deleting a node in $O(1)$ requires an immediate reference to its predecessor (`prev`), which a Singly Linked List lacks without an $O(n)$ scan."

- **Interviewer:** "How does `LinkedHashMap` support LRU eviction out of the box in Java/Kotlin?"
  **Answer:** "By passing `accessOrder = true` in its constructor and overriding `removeEldestEntry()` to return true when size exceeds capacity."

## Self-check rubric

Specify hash map plus doubly linked recency list or a suitable ordered map, show get/put/eviction invariants, and state capacity, synchronization and stale-value policy.

## References and reviewed-on date

- [Android LruCache](https://developer.android.com/reference/android/util/LruCache) — API and sizing.
- [Kotlin collection overview](https://kotlinlang.org/docs/collections-overview.html) — map semantics.

Technically reviewed against primary documentation on 2026-10-13.

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

## Concept and technical explanation

A Least Recently Used (LRU) Cache discards the oldest unaccessed items when reaching capacity, requiring strictly constant-time eviction and retrieval:
- Dual-Structure Architecture for $O(1)$ Operations:
  - Hash Map (`HashMap<K, Node<K, V>>`): Provides $O(1)$ constant-time lookup by mapping keys directly to corresponding node references on the heap.
  - Doubly-Linked List (`head` <-> `tail`): Tracks access recency. Adding to the front (Most Recently Used / MRU) and evicting from the back (Least Recently Used / LRU) execute in strictly $O(1)$ time by manipulating neighboring pointers without shifting elements.
- Algorithmic Mechanics:
  - `get(key)`: If missing, return `null`. If present, locate `Node` via HashMap, detach it from its current list position, reinsert it at the head (MRU), and return value. Complexity: $O(1)$.
  - `put(key, value)`: If key exists, update value and move `Node` to head. If key is new: instantiate `Node`, insert at head, and insert reference into HashMap. If `size > capacity`, evict the node immediately preceding dummy `tail` (LRU), remove its key from HashMap, and decrement size. Complexity: $O(1)$.
- Android Platform Standards (`LruCache`):
  - Android provides `android.util.LruCache` (and `androidx.collection.LruCache`).
  - Internally wraps a Java `LinkedHashMap(capacity, 0.75f, accessOrder = true)`.
  - Memory-Sized Caching: In Android image and bitmap caching, overriding `sizeOf(key, value)` to measure memory bytes (`bitmap.byteCount`) rather than item counts prevents OutOfMemoryError crashes.
  - Sizing Rule: Cache budgets are allocated as a fraction of available heap: `val cacheSize = (Runtime.getRuntime().maxMemory() / 8).toInt()`.

## Practical walkthrough (English)

Custom O(1) LRU Cache implementation and Android LruCache usage:
```kotlin
// Custom O(1) LRU Cache combining HashMap and DoublyLinkedList
class CustomLruCache<K, V>(private val capacity: Int) {
    private class Node<K, V>(val key: K, var value: V) {
        var prev: Node<K, V>? = null
        var next: Node<K, V>? = null
    }

    private val map = HashMap<K, Node<K, V>>()
    private val head = Node<K, V>(null as K, null as V) // Dummy head
    private val tail = Node<K, V>(null as K, null as V) // Dummy tail

    init {
        head.next = tail
        tail.prev = head
    }

    fun get(key: K): V? {
        val node = map[key] ?: return null
        moveToHead(node) // Mark as MRU
        return node.value
    }

    fun put(key: K, value: V) {
        val node = map[key]
        if (node != null) {
            node.value = value
            moveToHead(node)
        } else {
            val newNode = Node(key, value)
            map[key] = newNode
            addNode(newNode)
            if (map.size > capacity) {
                val lru = popTail()
                map.remove(lru.key)
            }
        }
    }

    private fun addNode(node: Node<K, V>) {
        node.prev = head
        node.next = head.next
        head.next?.prev = node
        head.next = node
    }

    private fun removeNode(node: Node<K, V>) {
        node.prev?.next = node.next
        node.next?.prev = node.prev
    }

    private fun moveToHead(node: Node<K, V>) {
        removeNode(node)
        addNode(node)
    }

    private fun popTail(): Node<K, V> {
        val res = tail.prev!!
        removeNode(res)
        return res
    }
}
```

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

An LRU cache achieves O(1) get and put operations by combining a HashMap for constant-time key lookup with a Doubly-Linked List for constant-time recency tracking. On access, nodes move to the head, and upon capacity overflow, the tail node is evicted. Android provides LruCache, which teams size by memory bytes rather than count to manage Bitmaps safely.

## Interview answer — structured

Designing a Least Recently Used cache requires pairing two complementary data structures to guarantee constant-time performance across all operations.
A standalone HashMap provides O(1) lookups but cannot maintain order without scanning. A standalone array or list maintains order but requires O(n) time to find or shift elements. By combining a HashMap with a Doubly-Linked List, we achieve the best of both worlds.
The HashMap maps each key to its corresponding list node in O(1) time. The Doubly-Linked List maintains access recency: newly inserted or accessed items are moved to the head as Most Recently Used, while the tail represents the Least Recently Used item.
When capacity is exceeded during a put operation, the node preceding the tail is removed from both the list and the map in O(1) pointer updates. In Android development, the platform provides LruCache, which wraps LinkedHashMap with access-order mode. For media apps, overriding sizeOf to budget cache limits by bitmap byte counts rather than item counts prevents out-of-memory crashes.

## Interview answer — deep senior

From a systems architecture and memory management perspective, the LRU cache represents the canonical design pattern for bounded in-memory caching under resource constraints.
The architectural brilliance of an LRU cache lies in its zero-shifting pointer mechanics. If an engineer attempts to implement an LRU cache using an ArrayList, accessing an element requires an O of n linear search, followed by an O of n array copy to shift elements forward. By employing a Doubly-Linked List flanked by sentinel dummy head and dummy tail nodes, detaching and prepending a node involves exactly four pointer reassignments, completing in strictly deterministic O of one time. Pairing this with a HashMap that stores direct memory references to these nodes eliminates traversal overhead completely.
In the Android ecosystem, the framework provides android.util.LruCache, which delegates internally to Java's LinkedHashMap configured with access-order set to true. However, senior Android engineers recognize that item-count sizing is a dangerous anti-pattern for mobile image caching. A cache limited to fifty items could hold fifty thumbnail images consuming five megabytes, or fifty high-resolution camera photos consuming four hundred megabytes, instantly exhausting the ART heap and triggering an OutOfMemoryError.
The production solution is memory-weighted caching. We allocate a safe fraction of the application's runtime memory—typically one-eighth of maxMemory—and override LruCache.sizeOf() to return the exact byte footprint of each cached Bitmap via bitmap.byteCount. Furthermore, we synchronize operations or utilize concurrent wrappers to prevent race conditions across parallel Coroutine dispatchers, guaranteeing thread-safe, sub-millisecond retrieval without risking heap exhaustion.

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

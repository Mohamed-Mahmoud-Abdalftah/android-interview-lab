---
id: EXT-DSA-01
title: Algorithms
module: 07-DSA-Live-Coding
tier: Important
estimated_minutes: 65
prerequisite_ids: [SYS-002]
learning_outcomes:
  - Choose Dijkstra only when edge weights are non-negative
  - State and maintain the distance and heap invariants during a live trace
  - Reconstruct a path and ignore stale priority-queue entries safely
  - Analyze time, space, overflow and input-contract failure cases
status: reviewed
code_verification: tested
last_source_checked: 2026-10-10
source_urls:
  - https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/PriorityQueue.html
  - https://kotlinlang.org/docs/collections-overview.html
  - https://kotlinlang.org/docs/collection-operations.html
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/ShortestPath.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/ShortestPathTest.kt
question_ids: [DSA-Q001, DSA-Q002, DSA-Q003, DSA-Q004, DSA-Q005, DSA-Q006, DSA-Q007, DSA-Q008, DSA-Q009, DSA-Q010]
---

# EXT-DSA-01 — Algorithms: weighted graphs and live coding

ده مسار practice إضافي بعد SYS-002، والمتطلب نفسه لسه planned في المنهج الأساسي. استخدم الدرس كتدريب مستقل على graph invariants، وبعد اكتمال SYS-002 ارجع له كمراجعة. **جلسة ساعتين:** 65 دقيقة شرح وتتبع، 20 دقيقة أسئلة، 25 دقيقة [LAB-013](../Coding-Challenges/LAB-013-dijkstra-shortest-path.md)، و10 دقائق [سيناريو debugging](../Real-World-Scenarios/SCN-014-routing-overflow.md).

## Mental model — اختار الخوارزمية من عقد الـ input

<p dir="rtl" lang="ar">الgraph مجموعة nodes وروابط edges. لو كل edge لها cost غير سالبة وعايز أقل مجموع من start لكل node، Dijkstra مناسبة. لو كل edges نفس الوزن، BFS أبسط. لو فيه وزن سالب، invariant بتاعة Dijkstra تتكسر ومحتاج algorithm مختلفة حسب المسألة. أول جملة في live coding لازم تكون عقد input: directed ولا undirected؟ أوزان سالبة؟ النتيجة path ولا distance؟ وهل overflow ممكن؟</p>

<p dir="rtl" lang="ar">الفكرة الأساسية: عندنا أفضل distance معروفة لكل node، وmin-heap تطلع أقل candidate. لما نطلع entry مسافتها تساوي أحدث قيمة في map، نقدر نعمل relaxation لجيرانها: نشوف هل الطريق عبرها أقل من المسافة القديمة. لو أقل، نحدث distance وparent ونضيف entry جديدة للheap. Java <code dir="ltr">PriorityQueue</code> مبنية على priority heap؛ <code dir="ltr">offer/poll</code> تقريبًا <code dir="ltr">O(log n)</code> و<code dir="ltr">peek</code> ثابتة حسب توثيق Java 17. <a dir="ltr" href="https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/PriorityQueue.html">PriorityQueue API</a>.</p>

## Mechanism and execution trace

<p dir="rtl" lang="ar">مثال: A→B بتكلفة 10، A→C بتكلفة 1، C→B بتكلفة 1، وB→D بتكلفة 1. نبدأ <code dir="ltr">dist[A]=0</code>. نطلع A، فنضيف B=10 وC=1. نطلع C، نلاقي B=2 أحسن من 10، فنحدثها ونضيف entry ثانية لـB. نطلع B=2، نضيف D=3. نطلع D=3 ونقدر نوقف لو الهدف D. entry القديمة B=10 قد تظل في heap؛ لو وصلنا لها بعدين نتجاهلها لأن <code dir="ltr">10 != dist[B]</code>.</p>

<table dir="rtl" lang="ar"><thead><tr><th>بعد استخراج</th><th>Distances معروفة</th><th>Heap المهم</th><th>Parent</th></tr></thead><tbody>
<tr><td dir="ltr">A(0)</td><td dir="ltr">A=0, B=10, C=1</td><td dir="ltr">C(1), B(10)</td><td dir="ltr">B←A, C←A</td></tr>
<tr><td dir="ltr">C(1)</td><td dir="ltr">B=2</td><td dir="ltr">B(2), B(10)</td><td dir="ltr">B←C</td></tr>
<tr><td dir="ltr">B(2)</td><td dir="ltr">D=3</td><td dir="ltr">D(3), B(10)</td><td dir="ltr">D←B</td></tr>
<tr><td dir="ltr">D(3)</td><td>الهدف اتثبت بأقل مسافة.</td><td>نوقف.</td><td dir="ltr">D←B←C←A</td></tr>
</tbody></table>

<p dir="rtl" lang="ar">ليه entry stale موجودة؟ <code dir="ltr">PriorityQueue</code> لا توفر decrease-key بسيط. بدل البحث والحذف الخطي، بنضيف candidate الجديدة ونرفض القديمة وقت poll. الـ invariant: map تحمل أفضل distance مكتشفة، وأي heap entry أكبر منها قديمة. وجود entries مكررة صحيح وظيفيًا، لكنه يدخل في تحليل المساحة والزمن.</p>

```kotlin
while (queue.isNotEmpty()) {
    val current = queue.poll()
    if (distances[current.label] != current.distance) continue
    for (edge in graph[current.label].orEmpty()) {
        val candidate = current.distance + edge.weight
        if (candidate < distances.getOrDefault(edge.to, Long.MAX_VALUE)) {
            distances[edge.to] = candidate
            previous[edge.to] = current.label
            queue += QueueNode(edge.to, candidate)
        }
    }
}
```

<p dir="rtl" lang="ar">لإرجاع path، كل تحسين يسجل parent. بعد الوصول للهدف نمشي بالعكس من target إلى start، ثم نعكس list. لو target unreachable، ما فيش distance فنرجع <code dir="ltr">null</code>. الكود يعتبر labels الموجودة فقط كdestination nodes جزءًا من graph، فـ A→B تقدر ترجع path حتى لو B مش key منفصلة في map. راجع <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/ShortestPath.kt">التنفيذ</a>.</p>

## Wrong and corrected implementation

<p dir="rtl" lang="ar"><strong>غلط 1:</strong> تستخدم BFS لأنك عايز “أقصر” طريق، لكنها تقلل عدد edges مش مجموع الأوزان. <strong>غلط 2:</strong> تعلم node visited أول مرة تدخل heap؛ ممكن طريق أرخص يظهر قبل تثبيت node. <strong>غلط 3:</strong> تجمع <code dir="ltr">Long</code> من غير overflow guard؛ رقم كبير يلف لسالب ويبدو أرخص.</p>

```kotlin
// Wrong for weighted routes: minimizes hop count only.
queue.add(start)
while (queue.isNotEmpty()) {
    val node = queue.removeFirst()
    for (next in graph[node].orEmpty()) if (visited.add(next.to)) queue += next.to
}
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> validate إن كل weight غير سالبة قبل البحث، واستخدم min-heap على accumulated distance، واعمل stale-entry guard. قبل الجمع افحص <code dir="ltr">current.distance &gt; Long.MAX_VALUE - edge.weight</code>، أو استخدم domain bounds أصغر موثقة. ما تخفيش invalid negative edge بتجاهلها؛ ارفض العقد لأن نتيجة جزئية ستكون مضللة.</p>

## Live-coding communication

<ol dir="rtl" lang="ar"><li><strong>Clarify:</strong> graph direction، negative weights، missing nodes، expected output، وحجم input.</li><li><strong>State invariant:</strong> heap أقل candidate، وdistance map أفضل قيمة مكتشفة، والentry القديمة تتجاهل.</li><li><strong>Trace صغير:</strong> ارسم 4 nodes فيها direct expensive route وindirect cheap route.</li><li><strong>Code core:</strong> validation، initialization، poll/skip، relaxation، reconstruction.</li><li><strong>Test aloud:</strong> unreachable، start=target، negative، overflow، destination-only node، stale entry.</li><li><strong>Complexity:</strong> مع adjacency list وheap: غالبًا <code dir="ltr">O((V+E) log V)</code>؛ lazy duplicates قد تجعل heap entries مرتبطة بعدد relaxations، فتقدر تقول <code dir="ltr">O((V+E) log E)</code> كحد تنفيذي محافظ.</li></ol>

<p dir="rtl" lang="ar">في المقابلة، ما تكتبش بسرعة قبل ما تثبت contract. لو interviewer قال graph dense أو weights صغيرة ومحدودة، ناقش بدائل. لو محتاج shortest paths لكل pairs، Dijkstra من كل node قد لا تكون أفضل اختيار. الهدف إنك تربط data structure بالقيود، مش تحفظ template.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">سبعة اختبارات JUnit بدأت بفشل compile ثم نجحت: طريق أقل cost رغم edges أكثر، stale heap entry، unreachable/missing target، start=target، negative rejection، Long overflow، وdestination-only node. استخدمنا graph directed وأوزان <code dir="ltr">Long</code>. الاختبارات لا تقيس performance على ملايين nodes ولا memory pressure ولا concurrency.</p>

<p dir="rtl" lang="ar">راجع <a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/ShortestPathTest.kt">الاختبارات</a>. أضف بنفسك: disconnected cycles، zero-weight edges، equal-cost alternatives، وتحديد tie-break contract لو المنتج محتاج path ثابتة. ترتيب iterator للـ <code dir="ltr">PriorityQueue</code> ليس sorted حسب التوثيق؛ استعمل poll، وما تختبرش ترتيب iteration الداخلي.</p>

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> باختار Dijkstra لما weights غير سالبة. distance map تحفظ أحسن cost، والmin-heap تطلع أقل candidate. لما يظهر طريق أحسن لنفس node، أضيف entry جديدة وأتجاهل القديمة وقت poll. بسجل parent لإعادة المسار، وأحمي جمع Long من overflow. الاختبارات تشمل unreachable وnegative وstale heap entry.</p>

**English, 20 seconds:** “Dijkstra works here because every edge is non-negative. I keep the best known distance in a map, pop candidates from a min-heap, skip stale entries, and store parents to reconstruct the path.”

**English, 60–90 seconds:** “I first confirm the graph is directed and weights are non-negative. The invariant is that the distance map stores the best discovered cost, while the priority queue orders candidate distances. Java's PriorityQueue has no convenient decrease-key, so I insert improved candidates and skip an entry if its distance no longer matches the map. During relaxation I guard Long addition from overflow. When the target is popped with the current best distance, I reconstruct the path through parent pointers. The implementation is roughly O((V+E) log E) with lazy duplicates and O(V+E) graph storage.”

## Senior follow-ups

<ol dir="rtl" lang="ar"><li><strong>ليه negative edge تكسر الفكرة؟</strong> node اتثبتت كأقل candidate ممكن يظهر لها طريق أقل لاحقًا عبر edge سالبة.</li><li><strong>ليه ما نحذفش entry القديمة من heap؟</strong> <code dir="ltr">remove(Object)</code> خطية في Java PriorityQueue؛ lazy deletion أبسط وغالبًا أفضل.</li><li><strong>هل التوقف أول ما target تدخل heap صحيح؟</strong> لأ؛ candidate أرخص قد تظهر. توقف لما target تتعمل poll بقيمتها الحالية.</li><li><strong>إزاي تختار بين BFS وDijkstra؟</strong> BFS للأوزان المتساوية/unweighted، Dijkstra لغير السالبة المختلفة.</li></ol>

## Misconceptions and revision

<ul dir="rtl" lang="ar"><li>“أقل edges يعني أقل cost.” غلط في weighted graph.</li><li>“أول مرة أشوف node خلاص.” غلط؛ ثبتها لما أقل current entry تخرج.</li><li>“PriorityQueue iteration sorted.” غلط؛ استخدم poll.</li><li>“Long يمنع overflow.” غلط؛ له حد ويحتاج guard أو domain bound.</li><li>“Dijkstra تعمل مع negative weights.” غلط.</li></ul>

**Evidence limit:** Seven Kotlin/JVM cases verify this directed non-negative graph implementation. No large benchmark, Android main-thread use, concurrent mutation, network routing service, or negative-weight algorithm is tested.

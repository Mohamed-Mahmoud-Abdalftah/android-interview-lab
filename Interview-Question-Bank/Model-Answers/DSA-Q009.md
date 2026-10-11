---
id: DSA-Q009-ANSWER
question_id: DSA-Q009
status: reviewed
---
# DSA-Q009 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “DFS colors or Kahn indegrees detect directed cycles; a parent check changes the undirected case.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> في directed DFS: gray node على current path تكشف cycle؛ في Kahn، processed count أقل من V يعني cycle. Undirected graph يحتاج parent rule.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Given a directed graph, return whether it contains a cycle. Cover disconnected components and a self-loop.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Cycle detection:</strong> في live coding، الـinvariant هي معنى الـdata structure بعد كل خطوة. بنحددها قبل code، نعمل trace على edge case تكسر الحل الساذج، وبعدها نشتق complexity من عدد الزيارات والعمليات بدل حفظ اسم pattern.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـCycle detection: حدد graph directed ولا undirected، اختار colors أو indegree، وغطّ كل disconnected component بدل البدء من node واحدة.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “A visited node always means a cycle in both directed and undirected graphs.”

<p dir="rtl" lang="ar">في <strong>Cycle detection</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: في directed DFS: gray node على current path تكشف cycle؛ في Kahn، processed count أقل من V يعني cycle. Undirected graph يحتاج parent rule. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Cycle detection: Kahn مناسب لو محتاج topological order؛ iterative DFS يتجنب stack overflow في graph عميقة.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Cycle detection: اختبر self-loop وtwo-node cycle وDAG وdisconnected cycle وduplicate edges، وتتبع colors/indegrees خطوة بخطوة.</p>

## Live-coding version

**Problem:** Given a directed graph, return whether it contains a cycle. Cover disconnected components and a self-loop.

```kotlin
fun hasDirectedCycle(graph: List<List<Int>>): Boolean {
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
}
```

<p dir="rtl" lang="ar"><strong>Trace وcomplexity:</strong> gray معناها node موجودة على الـcurrent DFS path؛ الوصول لها تاني يثبت cycle. black خلصناها. كل V وE يتزاروا مرة: O(V+E).</p>


## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Cycle detection، الـshortcut هي: <bdi dir="ltr">A visited node always means a cycle in both directed and undirected graphs.</bdi> ودي تكسر: في directed DFS: gray node على current path تكشف cycle؛ في Kahn، processed count أقل من V يعني cycle. Undirected graph يحتاج parent rule.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Cycle detection: اختبر self-loop وtwo-node cycle وDAG وdisconnected cycle وduplicate edges، وتتبع colors/indegrees خطوة بخطوة.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Cycle detection: Kahn مناسب لو محتاج topological order؛ iterative DFS يتجنب stack overflow في graph عميقة.</span>

## English model answer

“DFS colors or Kahn indegrees detect directed cycles; a parent check changes the undirected case. I would define the contract and invariant first, derive the data structure from the required operations, and test adversarial boundaries before claiming complexity. I would trace the invariant and test empty, duplicate, boundary, overflow, and worst-case inputs against a simple oracle.”

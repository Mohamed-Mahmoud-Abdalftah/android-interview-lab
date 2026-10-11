---
id: SYS-Q006-ANSWER
question_id: SYS-Q006
status: reviewed
---
# SYS-Q006 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “BFS gives shortest edge count in an unweighted graph; DFS fits reachability and recursive structure with depth risks.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> اختيار graph algorithm يتبع guarantee: BFS shortest unweighted edges، heap تضمن root فقط، وDijkstra تتطلب non-negative weights مع stale-entry handling.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Given an unweighted social graph, choose BFS or DFS to find the shortest connection path. State the invariant, complexity, and the conditions that would change your choice.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في BFS and DFS choice:</strong> في live coding، الـinvariant هي معنى الـdata structure بعد كل خطوة. بنحددها قبل code، نعمل trace على edge case تكسر الحل الساذج، وبعدها نشتق complexity من عدد الزيارات والعمليات بدل حفظ اسم pattern.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـBFS and DFS choice: عرّف graph والweight contract، اكتب visited/distance invariant، وتجاهل stale heap entry بدل افتراض إن iteration مرتبة.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Dijkstra works with negative weights and iterating a heap returns globally sorted values.”

<p dir="rtl" lang="ar">في <strong>BFS and DFS choice</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: اختيار graph algorithm يتبع guarantee: BFS shortest unweighted edges، heap تضمن root فقط، وDijkstra تتطلب non-negative weights مع stale-entry handling. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في BFS and DFS choice: DFS للreachability/deep structure، 0-1 BFS لأوزان 0/1، وBellman-Ford لو negative edges مطلوبة.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار BFS and DFS choice: غطّ disconnected/self-loop/duplicate edges وnegative invalid weight وequal paths وoverflow؛ قارن shortest paths بـBellman-Ford على graphs صغيرة صالحة.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في BFS and DFS choice، الـshortcut هي: <bdi dir="ltr">Dijkstra works with negative weights and iterating a heap returns globally sorted values.</bdi> ودي تكسر: اختيار graph algorithm يتبع guarantee: BFS shortest unweighted edges، heap تضمن root فقط، وDijkstra تتطلب non-negative weights مع stale-entry handling.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار BFS and DFS choice: غطّ disconnected/self-loop/duplicate edges وnegative invalid weight وequal paths وoverflow؛ قارن shortest paths بـBellman-Ford على graphs صغيرة صالحة.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في BFS and DFS choice: DFS للreachability/deep structure، 0-1 BFS لأوزان 0/1، وBellman-Ford لو negative edges مطلوبة.</span>

## English model answer

“BFS gives shortest edge count in an unweighted graph; DFS fits reachability and recursive structure with depth risks. I would define identities and state transitions across client and server, design for duplicate and out-of-order delivery, and prove recovery with observable end-to-end evidence. I would test duplicate, delayed, missing, and out-of-order events and observe recovery across both client and server.”

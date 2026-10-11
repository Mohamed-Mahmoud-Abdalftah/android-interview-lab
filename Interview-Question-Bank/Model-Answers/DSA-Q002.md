---
id: DSA-Q002-ANSWER
question_id: DSA-Q002
status: reviewed
---
# DSA-Q002 — Complete model answer

<p dir="rtl" lang="ar">استخدم BFS لما graph unweighted أو كل edge لها نفس cost، لأنها تزور حسب عدد الخطوات وتعمل O(V+E). لو costs غير سالبة ومختلفة، Dijkstra تقلل مجموعها باستخدام heap. اختيار BFS لمجرد كلمة shortest يطلع route قليلة edges لكنها أغلى.</p>

**Spoken answer:** “BFS is the simpler linear-time choice when every edge has equal cost. Dijkstra is needed when non-negative edge costs differ and the objective is minimum total cost.”

**Common wrong answer:** Using Dijkstra for every graph, adding complexity when a queue and BFS already satisfy the contract.

**Follow-up 1:** What about weights that are only zero or one? A 0-1 BFS with a deque can be more efficient than a general heap.

**Follow-up 2:** What clarification changes the choice most? Ask whether shortest means fewest edges, minimum sum, or another product-specific objective.

**Rubric:** Connect edge contract, objective, data structure, complexity, and one specialized alternative.

---
id: DSA-Q005-ANSWER
question_id: DSA-Q005
status: reviewed
---
# DSA-Q005 — Complete model answer

<p dir="rtl" lang="ar">أوضح contract الأول: direction، weights، missing nodes، output والحجم. أختار Dijkstra وأقول invariant، أتتبع مثال فيه direct غالي وindirect رخيص، ثم أكتب validation والheap والrelaxation والparent reconstruction. في الآخر أختبر unreachable وnegative وoverflow وstale entries وأحسب time/space.</p>

**Spoken answer:** “I clarify the graph contract, state the invariant, trace a counterexample to BFS, implement relaxation and parent reconstruction, then test edge cases and give complexity with lazy heap entries.”

**Common wrong answer:** Writing a memorized template silently and mentioning complexity only after the interviewer finds a contract mismatch.

**Follow-up 1:** What if requirements remain ambiguous? State the assumption explicitly, choose one contract, and explain which line changes under the alternative.

**Follow-up 2:** How do you recover after finding a bug mid-interview? Name the broken invariant, build a minimal counterexample, correct it, and rerun the trace aloud.

**Rubric:** Cover clarification, selection, invariant, trace, implementation order, tests, complexity, and correction behavior.

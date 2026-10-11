---
id: SCN-014
lesson_id: EXT-DSA-01
status: reviewed
code_verification: not_run
---
# SCN-014 — Route cost becomes negative and wins

**Hypothetical debugging scenario.** A routing service picks an impossible path after importing a very large synthetic edge cost.

<p dir="rtl" lang="ar">افحص input bounds ونوع الرقم قبل الخوارزمية. لو <code dir="ltr">distance + weight</code> عمل overflow، النتيجة تلف لسالب وتكسب comparison. فرضيات تانية: negative edge دخلت رغم العقد، unit conversion غلط، أو stale heap entry ما اتفلترتش. سجل node IDs وbounds بشكل آمن، مش dataset كاملة.</p>

## Reproduction and correction

1. Add an edge with `Long.MAX_VALUE`, then another positive edge; verify no wrapped candidate appears.
2. Reject negative weights before any partial search result.
3. Compare the popped distance with the current distance map to skip stale candidates.
4. Add domain-level maximum cost if the real product has a smaller meaningful bound.

<p dir="rtl" lang="ar">الإصلاح في المعمل يعمل guard قبل الجمع. في production راجع schema والserialization والوحدات كمان. rollout يراقب rejected graphs وoverflow guard hits، ويقارن مسارات عينة مع implementation مرجعية. لا تحول overflow إلى zero أو max بصمت من غير contract.</p>

[LAB-013](../Coding-Challenges/LAB-013-dijkstra-shortest-path.md) covers the local algorithm; it does not reproduce a production routing system.

## Senior follow-ups

1. **Would BigInteger solve the whole issue?** It avoids numeric overflow but not invalid units, negative edges, or performance constraints.
2. **What is the safer API?** Accept domain-bounded weights with explicit units and reject invalid graphs at ingestion.

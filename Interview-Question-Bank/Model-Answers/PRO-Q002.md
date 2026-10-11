---
id: PRO-Q002-ANSWER
question_id: PRO-Q002
status: reviewed
---
# PRO-Q002 — Complete model answer

<p dir="rtl" lang="ar"><code dir="ltr">contains</code> تقبل host شبيه أو اسم الدومين داخل path/query. parser تستخدم URI API وتقارن scheme وhost وport وpath كحقول، وترفض user-info وfragment حسب العقد. الـ query لازم allowlist بأسماء وتكرار وأنواع وحدود طول واضحة. وبعد parsing، authorization تظل منفصلة.</p>

**Spoken answer:** “I parse the URL structurally and compare an exact allowed origin and path. I reject duplicate or unknown fields and convert accepted values to constrained types. Parsing still does not authorize the operation.”

**Common wrong answer:** Decoding the whole URL repeatedly and comparing strings, which can introduce ambiguous normalization behavior.

**Follow-up 1:** Why reject duplicate query fields? Different layers may choose the first or last value, creating parser disagreement an attacker can exploit.

**Follow-up 2:** Should every percent-encoded value be rejected? No; define one canonical decoding contract and test it. This small lab deliberately accepts only unreserved identifiers.

**Rubric:** Cover structural parsing, exact origin, canonical query rules, typed values, and authorization separation.

---
id: KOT-Q022-ANSWER
question_id: KOT-Q022
status: reviewed
---
# KOT-Q022 — Complete model answer

<p dir="rtl" lang="ar">declaration-site variance تتحط على تعريف abstraction كلها: Producer&lt;out T&gt; تطلع T وConsumer&lt;in T&gt; تستقبلها. projection تقيد instance invariant لعملية واحدة: source من Array&lt;out Cat&gt; نقرأ منه، وdestination من Array&lt;in Cat&gt; نكتب له Cat. من destination نقرأ Any? فقط لأن النوع الفعلي ممكن يكون Animal، ومن source ما نكتبش لأن النوع الفعلي قد يكون subtype أضيق.</p>

**Spoken answer:** “Declaration-site variance states the direction for the whole abstraction. A use-site projection restricts one operation, such as reading from `Array<out Cat>` and writing to `Array<in Cat>`. The compiler removes operations that would violate the unknown concrete type.”

**Common wrong answer:** `out` makes an object immutable and `in` makes it mutable.

**Follow-up 1:** What can you read from Array<in Cat>? Only a broadly typed value such as `Any?`, because the actual array element type is unknown.

**Follow-up 2:** Why not put out on every collection? A type that must accept T in its public contract cannot safely declare T as output-only.

**Rubric:** Distinguish declaration and use sites, producer and consumer directions, and permitted operations.

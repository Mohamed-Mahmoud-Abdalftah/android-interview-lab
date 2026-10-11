# Day 5 optional speaking — generics and runtime types

Read [KOT-005](../01-Kotlin-JVM-ART/kot-005-generics-variance-erasure-and-reified.md).

**20 seconds:** “Generics are invariant by default. Producer-only types can be covariant with out, while consumer-only types can be contravariant with in.”

**90 seconds:** “A mutable generic container cannot usually widen its type because callers could insert an incompatible value. Kotlin models safe direction with declaration-site variance and use-site projections. On the JVM, generic arguments are generally erased, so an unchecked cast can fail much later. Reified inline parameters expose a direct runtime type, but they do not validate an entire nested generic graph. At untyped boundaries I use explicit type tokens or serializers, validate early, and isolate any unavoidable cast.”

<p dir="rtl" lang="ar"><strong>راجع نفسك:</strong> ادّي مثال يثبت ليه MutableBox invariant، وبعده اشرح الفرق بين <code dir="ltr">List&lt;*&gt;</code> و<code dir="ltr">List&lt;Any?&gt;</code>.</p>

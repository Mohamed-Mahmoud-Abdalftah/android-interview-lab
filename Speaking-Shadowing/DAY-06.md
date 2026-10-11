# Day 6 optional speaking — JVM, DEX, ART and complexity

Read [KOT-006](../01-Kotlin-JVM-ART/kot-006-revision-jvm-dex-art-boundary-and-big-o.md).

**20 seconds:** “Kotlin/JVM produces class files, D8 converts Java bytecode to DEX, and ART executes DEX. That runtime pipeline is separate from algorithmic complexity.”

**90 seconds:** “I separate source semantics, build artifacts and runtime behavior. Kotlin/JVM compiles source to Java-compatible class files. Android build tools use D8 to produce DEX, and ART executes that DEX in the application process. For complexity, a nested duplicate scan has quadratic worst-case work and constant extra space. A hash-set scan is expected linear time with linear extra space. Operation counts can verify the implementation path, but I still need a representative Android benchmark for latency, allocation or ART optimization claims.”

<p dir="rtl" lang="ar"><strong>راجع نفسك:</strong> اشرح السلسلة من غير ما تقول إن DEX native code، وبعدها وضح الفرق بين worst case وbest case، وبين operation count وdevice benchmark.</p>

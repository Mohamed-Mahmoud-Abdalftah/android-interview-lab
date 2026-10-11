---
id: KOT-Q026-ANSWER
question_id: KOT-Q026
status: reviewed
---
# KOT-Q026 — Complete model answer

<p dir="rtl" lang="ar">Kotlin/JVM compiler يحول source إلى Java-compatible class files ومعاها metadata. في Android build، D8 تقرأ Java bytecode من التطبيق والـdependencies وتحولها إلى DEX. ART داخل process التطبيق تحمل وتنفذ DEX، وممكن تستخدم interpreter أو JIT أو AOT حسب النظام وحالة التشغيل. التفاصيل الداخلية مش ثابتة لكل جهاز، ومعنى الدالة لازم يفضل راجع لعقد اللغة والكود.</p>

**Spoken answer:** “Kotlin/JVM compiles the source into Java-compatible class files. Android build tools then use D8 to convert Java bytecode into DEX. ART loads and executes that DEX in the app process, using runtime strategies such as interpretation, JIT or AOT as appropriate. I avoid treating Android as if it directly executes desktop JVM class files.”

**Common wrong answer:** Kotlin compiles straight to native ARM code, or ART runs the original `.class` files directly.

**Follow-up 1:** Where does desugaring fit? D8 can rewrite supported language and library features for the configured Android targets while producing DEX; the exact behavior depends on the build configuration.

**Follow-up 2:** What would you inspect for a release-only artifact issue? The exact variant, dependency graph, generated class files, DEX/APK contents, mapping and keep rules, plus a reproducible device trace.

**Rubric:** Name class bytecode, D8, DEX and ART in order, distinguish bytecode from native code, and avoid universal JIT/AOT claims.

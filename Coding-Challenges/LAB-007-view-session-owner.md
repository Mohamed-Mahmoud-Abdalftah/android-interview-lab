---
id: LAB-007
lesson_id: AND-001
status: reviewed
code_verification: tested
---
# LAB-007 — Detach a view-owned renderer

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> نفّذ pure JVM class اسمها <code dir="ltr">ViewSession</code>. عند <code dir="ltr">attach(render)</code> تحفظ renderer الحالية. <code dir="ltr">show(value)</code> تناديها وترجع true لو موجودة، أو ترجع false لو مفيش view. <code dir="ltr">detach()</code> تزيل المرجع، وبعدها تقدر تربط view جديدة. لا تسمِّها Android LifecycleOwner؛ هي نموذج مبسط لقرار ownership.</p>

**Acceptance cases:** The [JUnit tests](../projects/kotlin-jvm-labs/src/test/kotlin/academy/ViewSessionTest.kt) cover no renderer before attach, value delivered while attached, no delivery after detach, and a new renderer after old view is detached. Try implementing before viewing the [reference](../projects/kotlin-jvm-labs/src/main/kotlin/academy/ViewSession.kt).

<p dir="rtl" lang="ar"><strong>التفسير:</strong> ليه Fragment ممكن تفضل موجودة بعد view؟ إيه owner الصحيحة لـ observer بتعدل binding؟ وهل نجاح الاختبار ده يثبت Android process death؟ الإجابة الأخيرة لأ؛ راجع <a dir="ltr" href="../Real-World-Scenarios/SCN-007-fragment-view-leak.md">السيناريو</a> وخطة Android integration.</p>

**Complexity and limitations:** Attach/detach/show perform O(1) local operations, excluding renderer work. The model has no Android callbacks, View objects, concurrency guarantee or measured leak behavior. In a real app, use the platform lifecycle and test navigation/recreation.

**Verification:** Run `./gradlew clean test check run --no-daemon` in `projects/kotlin-jvm-labs`, then inspect [BUILD-VERIFICATION](../BUILD-VERIFICATION.md). Optional rubric: 3 attach/show behavior, 3 detach and rebind, 2 ownership explanation, 2 clear JVM-versus-Android evidence. No timer or score is required.

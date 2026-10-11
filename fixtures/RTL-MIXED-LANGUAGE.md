# RTL and LTR rendering fixture

This synthetic page checks source parsing and visual layout. It does not assert a lesson's technical claims.

<h2 dir="rtl" lang="ar" id="arabic-heading">عنوان عربي واضح</h2>

<p dir="rtl" lang="ar">دي فقرة عربية كاملة. الجملة التانية بتكمّل من اليمين للشمال، وعلامة الوقف في آخرها.</p>

<p dir="rtl" lang="ar">لما تستخدم <code dir="ltr">StateFlow</code> مع <code dir="ltr">ViewModel</code>، لازم تفهم إزاي الـ <span dir="ltr">Coroutine</span> بتتعامل مع الـ <code dir="ltr">Lifecycle</code>.</p>

<p dir="rtl" lang="ar">الاسم بين قوسين <span dir="ltr">(ViewModel + StateFlow)</span>، والمسار <code dir="ltr">src/main/kotlin/ProfileName.kt</code>، والرابط <a dir="ltr" href="../01-Kotlin-JVM-ART/KOT-001-nullability-java-boundary.md">KOT-001 lesson</a> لازم يفضلوا مقروئين. اسأل: «إيه السبب؟»</p>

<ol dir="rtl" lang="ar">
<li>اقرأ <code dir="ltr">String?</code> قبل التحويل.</li>
<li>افحص <code dir="ltr">null</code> والقيمة الفاضية.</li>
<li>اكتب اختبارًا يوضح السلوك.</li>
</ol>

<table dir="rtl" lang="ar">
<thead><tr><th>الخطوة</th><th>القيمة</th><th>الشرح</th></tr></thead>
<tbody>
<tr><td>القراءة</td><td dir="ltr"><code dir="ltr">String?</code></td><td>ممكن تكون القيمة غايبة.</td></tr>
<tr><td>البديل</td><td dir="ltr"><code dir="ltr">"Guest"</code></td><td>قرار العرض واضح.</td></tr>
</tbody>
</table>

<p dir="rtl" lang="ar">الكود التالي يبقى LTR وقابل للنسخ:</p>

```kotlin
val raw: String? = LegacyProfileApi.nameFor("ada")
val label = raw?.trim()?.takeIf { it.isNotEmpty() } ?: "Guest"
```

## English technical interview answer

“I make the Java boundary explicit, validate the nullable result once, and choose a fallback only when the product contract allows it.”

[Open the original lesson](../01-Kotlin-JVM-ART/KOT-001-nullability-java-boundary.md).

---
id: KOT-005
title: Generics, variance, erasure and reified
module: 01-Kotlin-JVM-ART
tier: Core
estimated_minutes: 120
prerequisite_ids: [KOT-003, KOT-004]
learning_outcomes:
  - Explain invariance and choose declaration-site out or in from read/write behavior
  - Use type projections and star projections without pretending the element type is known
  - Identify JVM type-erasure boundaries and contain unavoidable unchecked casts
  - Use reified type parameters and explicit KClass tokens with accurate limits
status: reviewed
code_verification: tested
last_source_checked: 2026-10-10
source_urls:
  - https://kotlinlang.org/docs/generics.html
  - https://kotlinlang.org/docs/inline-functions.html#reified-type-parameters
  - https://kotlinlang.org/docs/java-to-kotlin-interop.html#variant-generics
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/RuntimeTypeRegistry.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/RuntimeTypeRegistryTest.kt
question_ids: [KOT-Q021, KOT-Q022, KOT-Q023, KOT-Q024, KOT-Q025]
---

# KOT-005 — Generics, variance, erasure and reified

**مسار الساعتين:** 55 دقيقة شرح وتتبع، 20 دقيقة [أسئلة وإجابات كاملة](../Interview-Question-Bank/BY-TOPIC.md)، 25 دقيقة [LAB-016](../Coding-Challenges/LAB-016-runtime-type-registry.md)، 10 دقائق [مراجعة](../Flashcards-Revision/KOT-005.md)، و10 دقائق شرح بصوتك من [Day 5](../Speaking-Shadowing/DAY-05.md).

## Mental model — النوع العام وعد بالأمان

<p dir="rtl" lang="ar">الـgeneric type مش مجرد طريقة تقلل تكرار الكود؛ هي عقد يربط أنواع المدخلات والمخرجات. لما دالة تستقبل <code dir="ltr">Box&lt;Cat&gt;</code>، الـcompiler لازم يعرف هل الكود هيقرأ Cat فقط، ولا ممكن يكتب Dog جوه نفس الـbox. السؤال ده هو أصل variance. لو النوع يقرأ ويكتب <code dir="ltr">T</code>، التحويل بين <code dir="ltr">Box&lt;Cat&gt;</code> و<code dir="ltr">Box&lt;Animal&gt;</code> خطر، لذلك default في Kotlin هو invariance.</p>

```kotlin
open class Animal
class Cat : Animal()

class MutableBox<T>(var value: T)

val cats: MutableBox<Cat> = MutableBox(Cat())
// val animals: MutableBox<Animal> = cats // must not compile
// animals.value = Animal()              // would break cats' promise
```

<p dir="rtl" lang="ar">فكر في اتجاه حركة القيمة. Producer يطلع <code dir="ltr">T</code> للخارج، فيقدر يبقى <code dir="ltr">out T</code>. Consumer يستقبل <code dir="ltr">T</code> للداخل، فيقدر يبقى <code dir="ltr">in T</code>. النوع اللي يعمل الاثنين يفضل invariant. القاعدة المختصرة “producer out, consumer in” مفيدة، بس راجع كل member فعلًا؛ النوع ممكن يحتوي method تحط <code dir="ltr">T</code> في مكان غير مباشر.</p>

## Mechanism and execution trace — variance خطوة بخطوة

```kotlin
fun interface Producer<out T> { fun produce(): T }
fun interface Consumer<in T> { fun accept(value: T) }

val catProducer: Producer<Cat> = Producer { Cat() }
val animalProducer: Producer<Animal> = catProducer

val animalConsumer: Consumer<Animal> = Consumer { save(it) }
val catConsumer: Consumer<Cat> = animalConsumer
```

<p dir="rtl" lang="ar">في السطر الأول للتحويل، أي حد طالب Animal يقدر يستقبل Cat لأنها Animal؛ ومفيش method تسمح له يحط Animal عامة جوه producer. في التحويل الثاني، consumer يعرف يتعامل مع أي Animal، إذن أكيد يعرف يستقبل Cat؛ لكن قراءة قيمة <code dir="ltr">T</code> منه غير متاحة. الـcompiler بيمنع العمليات المخالفة للاتجاه، وده اللي يخلي التحويل sound.</p>

<p dir="rtl" lang="ar">لو class نفسها invariant لكن call site محتاجة اتجاه مؤقت، استخدم type projection. <code dir="ltr">Array&lt;out Animal&gt;</code> تسمح بالقراءة كـAnimal وتمنع الكتابة غير الآمنة. <code dir="ltr">Array&lt;in Cat&gt;</code> تسمح بكتابة Cat، لكن القراءة نوعها الآمن العام <code dir="ltr">Any?</code>. ده use-site contract للعملية الحالية، مش تغيير لتعريف Array.</p>

```kotlin
fun copyCats(from: Array<out Cat>, to: Array<in Cat>) {
    for (index in from.indices) to[index] = from[index]
}
```

<p dir="rtl" lang="ar"><code dir="ltr">List&lt;*&gt;</code> معناها list لعنصر نوعه غير معروف. تقدر تقرأ العناصر كـ<code dir="ltr">Any?</code>، لكن ما ينفعش تفترض إنها Strings ولا تضيف قيمة arbitrary. الـstar projection مفيدة عند logging أو routing لا تحتاج نوع العنصر؛ لو business logic محتاجة النوع، اطلب token أو parser بدل cast عشوائي.</p>

## Type erasure and runtime evidence

<p dir="rtl" lang="ar">على JVM أغلب generic arguments بتتمسح وقت runtime. تقدر تسأل إن object هي <code dir="ltr">List&lt;*&gt;</code>، لكن <code dir="ltr">value is List&lt;String&gt;</code> غير متاحة بشكل عام. وحتى لو عندك <code dir="ltr">inline reified T</code> وتحققّت إن outer value هي List، عناصر nested generic لسه محتاجة فحص أو serialization metadata. كلمة reified مش بترجع كل generic graph بعد erasure.</p>

```kotlin
fun unsafeNames(value: Any): List<String> {
    @Suppress("UNCHECKED_CAST")
    return value as List<String> // A List<Int> passes the outer runtime check.
}
```

<p dir="rtl" lang="ar">المشكلة بتظهر متأخر: الـcast على list نفسها قد تعدي، وبعدها أول element يتقري كـString يحصل <code dir="ltr">ClassCastException</code>. التصحيح إنك تتحقق عند boundary وتحوّل لـrepresentation مملوكة، أو تمرر serializer/type token يعرف الشكل الكامل. خلي أي unchecked cast في مكان واحد صغير، وبعد validation، ومع tests للمدخلات العدائية.</p>

```kotlin
fun parseNames(value: Any): List<String>? {
    val elements = value as? List<*> ?: return null
    if (elements.any { it !is String }) return null
    return elements.filterIsInstance<String>().toList()
}
```

## Reified and explicit type tokens

<p dir="rtl" lang="ar">الدالة العادية <code dir="ltr">fun &lt;T&gt;</code> ما تقدرش تستخدم <code dir="ltr">T::class</code> لأن T ممسوحة. لو الدالة <code dir="ltr">inline</code> والـparameter <code dir="ltr">reified</code>، compiler ينسخ body عند call site ويقدر يحط runtime class الفعلية. ده ممتاز لfactory صغيرة أو wrapper لـAPI، لكنه يزود generated code لو body كبيرة، وما ينفعش لو function value محتاجة تتنقل ككيان عادي من غير specialization.</p>

```kotlin
data class TypeKey<T : Any>(val name: String, val type: KClass<T>)

inline fun <reified T : Any> typeKey(name: String): TypeKey<T> =
    TypeKey(name, T::class)
```

<p dir="rtl" lang="ar">في <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/RuntimeTypeRegistry.kt">المعمل</a>، الـkey تحمل name و<code dir="ltr">KClass</code>. <code dir="ltr">putUnknown</code> تمثل boundary جاية من plugin أو parser: تفحص <code dir="ltr">isInstance</code> قبل التخزين. <code dir="ltr">get</code> فيها unchecked cast واحدة بعد invariant check؛ call sites تفضل typed. وجود نفس الاسم مع Int وString لا يخلط القيم لأن runtime type جزء من key.</p>

```text
typeKey<Int>("value")    -> ("value", Int::class)    -> 7
typeKey<String>("value") -> ("value", String::class) -> "seven"
unknown "three" + Int key -> rejected before storage
```

<p dir="rtl" lang="ar">الـregistry دي teaching model، مش DI container ولا serialization framework. <code dir="ltr">KClass&lt;List&lt;String&gt;&gt;</code> عمليًا لا تثبت نوع كل عنصر بعد erasure؛ لو محتاج nested shape استخدم serializer أو descriptor يحتفظ بالgeneric structure. راجع <a dir="ltr" href="https://kotlinlang.org/docs/generics.html">Kotlin generics</a> و<a dir="ltr" href="https://kotlinlang.org/docs/inline-functions.html#reified-type-parameters">reified parameters</a>؛ تم فحصهم 2026-10-10.</p>

## Wrong and corrected implementation

<p dir="rtl" lang="ar"><strong>غلط:</strong> API عامة تخزن <code dir="ltr">Any</code> بالاسم وترجع generic cast من غير token. الـcompiler يصدق caller، لكن مفيش علاقة runtime بين النوع المطلوب والقيمة المخزنة. الغلط يظهر بعيد عن boundary ويصعب تتبعه.</p>

```kotlin
class UnsafeRegistry {
    private val values = mutableMapOf<String, Any>()

    @Suppress("UNCHECKED_CAST")
    fun <T> get(name: String): T? = values[name] as T?
}
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> اربط الاسم بـtype token، وافحص input غير الموثوق وقت الدخول، وخلي cast الداخلي بعد invariant واضح. لو النوع nested أو polymorphic استخدم serializer typed بدل <code dir="ltr">KClass</code> فقط. ولو API مجرد producer أو consumer، عبّر عن الاتجاه بـ<code dir="ltr">out</code> أو <code dir="ltr">in</code> عشان call sites تستفيد من substitution الآمن.</p>

## Java interop and wildcards

<p dir="rtl" lang="ar">Java تستخدم wildcards في call site زي <code dir="ltr">? extends Animal</code> و<code dir="ltr">? super Cat</code>، بينما Kotlin تفضل declaration-site variance مع projections وقت الحاجة. عند عبور Java boundary افحص التوقيع الفعلي اللي Java شايفاه؛ compiler ممكن يولد أو يلغي wildcards حسب موضع النوع وannotations. ما تضيفش <code dir="ltr">@JvmSuppressWildcards</code> لمجرد إزالة شكل مزعج؛ استخدمها لما عقد Java caller محتاج signature محددة واختبر compilation من Java.</p>

<p dir="rtl" lang="ar">platform types تضيف خطر تاني: Java collection ممكن تحتوي null أو تتغير من alias. عند boundary اعمل validation وsnapshot حسب عقدك. variance لا تحول mutable Java list إلى immutable data، وread-only Kotlin <code dir="ltr">List</code> لا تضمن deep immutability.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">سبعة اختبارات JUnit بدأت بفشل compile، وبعد التنفيذ غطت reified token، round trip typed، نفس الاسم بنوعين، rejection لقيمة غلط، missing key، covariance وcontravariance. الاختبارات تجمع الأمثلة وتثبت runtime behavior؛ أما العلاقات اللي لازم ما تعملش compile فبنثبتها من signature ومراجعة compiler، مش باختبار runtime يحاول يشغل كود مستحيل يتجمع.</p>

<p dir="rtl" lang="ar">حالات إضافية في production: nested generics، class loaders لو plugin system، serialization schema، Java callers، nullability من Java، وAPI compatibility. اعمل compile test من Java لو التوقيع public، واختبر malformed payload قبل أي unchecked cast. ما تستخدمش reflection كبديل تلقائي لعقد serialization واضح.</p>

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> الـgenerics بتربط الأنواع وقت compile. النوع mutable غالبًا invariant عشان ما ندخلش Animal في container موعود إنه Cat. producer يبقى <code dir="ltr">out</code> وconsumer يبقى <code dir="ltr">in</code>. على JVM generic arguments غالبًا erased؛ <code dir="ltr">reified</code> تدي runtime token للنوع المباشر في inline function، لكنها ما تثبتش nested element types. عند boundary أستخدم token أو serializer وأحصر unchecked cast بعد validation.</p>

**English interview answer:** “Kotlin generics are invariant by default because a mutable container can both consume and produce its type. I mark producer-only APIs `out` and consumer-only APIs `in`, or use projections for a single operation. On the JVM, generic arguments are generally erased. Reified inline parameters expose the direct runtime type at the call site, but they do not validate an entire nested generic structure, so boundaries still need explicit tokens or serializers.”

## Senior follow-ups

1. **Why is MutableList<Cat> not a MutableList<Animal>?** The broader reference could insert a non-Cat and violate the original list's contract.
2. **What can you safely read from List<*>?** Elements as `Any?`; the concrete element type remains unknown.
3. **Does reified T solve List<T> validation?** It can expose T at the call site, but the elements must still be checked and nested generic structure needs richer metadata.
4. **Where can an unchecked cast be acceptable?** In a small encapsulated boundary after a runtime invariant check, with adversarial tests and no unchecked caller contract.
5. **How do Kotlin variance and Java wildcards meet?** Kotlin declaration-site variance and projections map to JVM signatures; verify the generated Java-facing contract and add wildcard annotations only for an explicit interop need.

## Misconceptions and revision

<ul dir="rtl" lang="ar">
<li><strong>“List&lt;Cat&gt; دايمًا subtype من List&lt;Animal&gt;”:</strong> صح للـread-only covariant Kotlin List، مش لأي mutable generic.</li>
<li><strong>“star projection معناها Any”:</strong> معناها النوع مجهول؛ القراءة الآمنة <code dir="ltr">Any?</code> والكتابة مقيدة.</li>
<li><strong>“reified تلغي erasure”:</strong> بتوفر direct runtime type داخل inline call؛ مش generic reflection كاملة.</li>
<li><strong>“unchecked cast اشتغلت يبقى صح”:</strong> ممكن الفشل يتأخر لأول element access.</li>
<li><strong>“variance تحمي من mutation كلها”:</strong> تحمي اتجاه type operations؛ ما تمنعش aliasing أو Java mutation أو state races.</li>
</ul>

**حدود الدليل:** اتنفذ JVM model واختباراته. ما اتعملش bytecode inspection، Java compilation test، serialization framework integration، Android build أو benchmark للـinline expansion.

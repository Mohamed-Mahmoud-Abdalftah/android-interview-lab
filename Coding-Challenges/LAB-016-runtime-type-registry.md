---
id: LAB-016
lesson_id: KOT-005
status: reviewed
code_verification: tested
---
# LAB-016 — Runtime type registry

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> اعمل <code dir="ltr">TypeKey&lt;T&gt;</code> تربط stable name بـ<code dir="ltr">KClass&lt;T&gt;</code>، وreified factory، وregistry فيها typed <code dir="ltr">put/get</code>. أضف boundary تستقبل <code dir="ltr">TypeKey&lt;*&gt;</code> و<code dir="ltr">Any</code> وترفض القيمة لو runtime token مش مطابقة. احصر أي unchecked cast بعد invariant check.</p>

**Acceptance:** [سبعة اختبارات](../projects/kotlin-jvm-labs/src/test/kotlin/academy/RuntimeTypeRegistryTest.kt) تغطي token، round trip، same name/different type، hostile boundary، missing key، covariance وcontravariance. ابدأ بالاختبارات قبل [reference](../projects/kotlin-jvm-labs/src/main/kotlin/academy/RuntimeTypeRegistry.kt).

<p dir="rtl" lang="ar"><strong>شرح مطلوب:</strong> وضح ليه <code dir="ltr">KClass</code> المباشرة لا تكفي للتحقق من عناصر <code dir="ltr">List&lt;String&gt;</code>، وإمتى تحتاج serializer يحتفظ بالgeneric shape. اكتب مثال compile-time يبين إن Producer covariant وConsumer contravariant.</p>

**Limits:** This lab is an in-memory teaching model. It does not provide thread safety, persistence, nested generic validation, dependency injection, serialization, or class-loader isolation.

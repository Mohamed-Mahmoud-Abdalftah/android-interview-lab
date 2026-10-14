---
id: "PAT-10"
question: "Compare Factory and Abstract Factory."
topic: "Design Patterns"
code: "PAT"
group: "B"
phase: 2
priority: "P1"
order: 201
editorial_status: "reviewed"
---

# PAT-10

## Original interview question

Compare Factory and Abstract Factory.

## What the interviewer evaluates

Explain one product construction versus related product families and prevent mismatched configurations.

## Explanation in Arabic

المقارنة بين نمط المصنع (Factory Method) ونمط المصنع المجرد (Abstract Factory) مع أمثلة عملية في Android:

1. نمط دالة المصنع (Factory Method Pattern):
   - **الهدف**: إنشاء **كائن منتج واحد (Single Product)** وتفويض قرار اختيار الكلاس الملموس إلى دالة المصنع.
   - **التركيز**: إنشاء كائن من عائلة محددة بناءً على بارامتر.
   - **في Android**: `ViewModelProvider.Factory`؛ مسؤوليته إنشاء كائن ViewModel واحد بناءً على كلاس الـ ViewModel المطلوب.

2. نمط المصنع المجرد (Abstract Factory Pattern):
   - **الهدف**: مصنع للمصانع! توفير واجهة لإنشاء **عائلات كاملة من الكائنات المرتبطة والمتوافقة (Families of Related Products)** دون تحديد كلاساتها الملموسة.
   - **التركيز**: الاتساق والتطابق بين مجموعة كائنات كاملة.
   - **في Android**: نظام الثيمات الموحد؛ `DesignSystemFactory` ينشئ (زر + مربع حوار + بطاقة) متطابقة تماماً لثيم معين (DarkTheme vs LightTheme)؛ مما يضمن استحالة وضع زر من ثيم النهار داخل حوار من ثيم الليل بالخطأ!

## Practical walkthrough

المقارنة بين Factory Method و Abstract Factory في كود Kotlin:
```kotlin
// 1. FACTORY METHOD: ينشئ كائناً واحداً فقط من نوع محدد:
interface NotificationFactory {
    fun createNotification(type: String): Notification
}
class AppNotificationFactory : NotificationFactory {
    override fun createNotification(type: String): Notification = when(type) {
        "PROMO" -> PromoNotification()
        "ALERT" -> AlertNotification()
        else -> DefaultNotification()
    }
}

// 2. ABSTRACT FACTORY: ينشئ عائلة كاملة من المكونات المتوافقة معاً:
interface DialogComponentFactory { // عائلة مكونات كاملة
    fun createHeader(): DialogHeader
    fun createButton(): DialogButton
    fun createBackground(): DialogBackground
}

class PremiumDialogFactory : DialogComponentFactory {
    override fun createHeader() = GoldHeader()
    override fun createButton() = GoldButton()
    override fun createBackground() = BlurBackground()
}

class StandardDialogFactory : DialogComponentFactory {
    override fun createHeader() = SimpleHeader()
    override fun createButton() = StandardButton()
    override fun createBackground() = FlatBackground()
}
```

## Why it matters and how it works

A regular factory encapsulates creation/selection of one product role. An abstract factory defines construction of a family of related products without clients naming concrete classes. The benefit is consistent combinations; the cost is another abstraction layer.

## Worked example

Conceptual Kotlin:
```kotlin
interface EnvironmentFactory {
    fun api(): PaymentsApi
    fun signer(): RequestSigner
}
interface PaymentsApi
interface RequestSigner
```
A sandbox factory returns both sandbox implementations; a production factory returns matching production ones. This contract alone is not credential storage.

## Trade-offs and decision criteria

A simple constructor or factory is easier if only one object varies. Abstract Factory helps when several products must change together, but adding a new product method can affect all factories. Hilt qualifiers may be clearer for a static Android graph.

## Failure modes

A test build accidentally combines sandbox API with production signer because clients independently create them. Factory family or DI validation prevents mismatch; secrets still belong in backend, not APK.

## Production perspective

A payment SDK wrapper has test and production client families with compatible endpoint/signature strategies. Integration tests verify environment pairing and no production charge from test configuration.

## Interview answer — short

Factory Method creates a single product by delegating instantiation to a method (`ViewModelProvider.Factory`). Abstract Factory creates entire families of related or dependent products without specifying concrete classes (e.g. creating matching themed buttons, headers, and backgrounds for dark vs light themes).

## Interview answer — structured

The distinction between Factory Method and Abstract Factory hinges on product scope and familial relationship guarantees.

First, **Factory Method (Single Product Focus)**. Next, defines an interface with a method that creates a **single product object**.
Subclasses or implementers decide which concrete class to instantiate. *Android Example*: `ViewModelProvider.Factory`. It defines `create(modelClass: Class<T>): T`, instantiating a single specific ViewModel requested by the UI controller.
**Abstract Factory (Product Family Focus)**. Defines an interface with multiple methods designed to create **an entire family of mutually compatible products**.
Guarantees that clients never accidentally mix incompatible products (e.g. Mixing an iOS-styled button with an Android Material dialog). Finally, *Android Example*: A multi-brand design system where `BrandFactory` exposes `createButton()`, `createCard()`, and `createTextField()`. The `EnterpriseBrandFactory` produces enterprise-styled variants of all three components, guaranteeing complete visual cohesion across the suite.


## Interview answer — deep senior

Under the hood, an Abstract Factory is often implemented as a class whose individual methods are Factory Methods. In modern Dagger/Hilt architectures, **Dagger Component and Subcomponent interfaces are essentially compile-time Abstract Factories**! When Dagger declares an interface providing various dependencies for an Activity scope, Dagger generates the concrete factory implementation under the hood.

In Kotlin, using Factory patterns can often be simplified using top-level functions or companion objects: `companion object { fun create(...) = ... }`. Senior architects reserve explicit Factory and Abstract Factory classes for scenarios where instantiation requires dynamic dependency injection or complex configuration policies.


## How to answer in the interview

- **Why:** Prevent invalid construction and incompatible product families.
- **How:** Compare provider-for-method Factory with environment API+signer Abstract Factory.
- **Trade-off:** Use one function/constructor when no family exists.
- **Failure case:** Sandbox signer paired with production endpoint or god-factory growth.
- **Production solution:** Validate combinations and test unsupported routes.

## Deep-dive talking points

Distinguish product versus family, environment invariant, and DI qualifier alternative.

## Follow-up questions

- **Interviewer:** "How does Dagger use the Abstract Factory pattern?"
  **Answer:** "Dagger Components are Abstract Factories. You declare an abstract component interface with methods returning various dependencies, and Dagger generates the concrete factory class (`DaggerAppComponent`) implementing it."

- **Interviewer:** "When should you prefer a Factory over direct constructor invocation?"
  **Answer:** "When object construction involves complex conditional logic, requires caching or pooling existing instances, or when the calling client must remain decoupled from concrete implementation types."

## Self-check rubric

Design a single gateway factory and a two-product environment family; justify which is necessary.

## References and reviewed-on date

- [Android Hilt guide](https://developer.android.com/training/dependency-injection/hilt-android) — qualifier/graph alternative for product-family wiring.
- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — Factory Method and Abstract Factory.

Technically reviewed against primary documentation on 2026-10-13.

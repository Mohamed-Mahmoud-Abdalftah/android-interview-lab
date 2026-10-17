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

## Concept and technical explanation

The Factory Method and Abstract Factory patterns are creational abstractions designed to decouple client code from concrete class instantiation, but they operate at fundamentally different structural scopes. Factory Method defines an interface containing a single creation method, delegating the instantiation of an individual product to subclasses or specialized providers. In contrast, Abstract Factory provides an overarching interface for creating entire families of related or dependent products without specifying their concrete classes. While Factory Method focuses on creating one polymorphic product variant, Abstract Factory guarantees familial consistency, ensuring that products created across multiple factory methods are mutually compatible and visually or operationally cohesive.

## Practical walkthrough (English)

Contrasting Factory Method with Abstract Factory in Kotlin:
```kotlin
// 1. FACTORY METHOD: Creates a single polymorphic product
interface ChartRenderer { fun render(canvas: Canvas) }
interface ChartFactory { fun createRenderer(): ChartRenderer }

class BarChartFactory : ChartFactory {
    override fun createRenderer(): ChartRenderer = BarChartRenderer()
}

// 2. ABSTRACT FACTORY: Creates an entire family of related products
interface DesignSystemFactory {
    fun createPrimaryButton(): ButtonComponent
    fun createInputField(): InputComponent
    fun createCardContainer(): CardComponent
}

class Material3DesignFactory : DesignSystemFactory {
    override fun createPrimaryButton() = Material3Button()
    override fun createInputField() = Material3Input()
    override fun createCardContainer() = Material3Card()
}

class CupertinoDesignFactory : DesignSystemFactory {
    override fun createPrimaryButton() = CupertinoButton()
    override fun createInputField() = CupertinoInput()
    override fun createCardContainer() = CupertinoCard()
}
```

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

Factory Method focuses on creating a single product by delegating instantiation to a specific method, such as ViewModelProvider.Factory creating a ViewModel. Abstract Factory focuses on creating entire families of related or dependent products without specifying concrete classes, such as a design system factory creating matching buttons, cards, and input fields. Factory Method produces one object, whereas Abstract Factory guarantees familial compatibility across multiple collaborating objects.

## Interview answer — structured

Comparing Factory Method and Abstract Factory requires evaluating their structural scope, object relationships, and operational guarantees.
Factory Method centers on a single product hierarchy. An interface declares a creation signature, leaving implementing subclasses or lambdas to determine the concrete type instantiated. A textbook Android example is ViewModelProvider.Factory, where a single create method produces an individual ViewModel instance based on the requested class token. The client code consumes the resulting product polymorphically without knowing its concrete constructor mechanics.
Abstract Factory elevates this concept to families of interdependent products. Instead of creating an isolated object, an Abstract Factory exposes multiple creation methods that yield distinct products designed to collaborate seamlessly. For instance, in a multi-brand white-label Android application, an Abstract Factory can produce the full suite of UI components, such as headers, cards, and buttons, corresponding to a specific brand theme. Clients interact with the abstract family interface, ensuring that components from different design languages are never accidentally mixed in the same screen hierarchy.
While Factory Method relies heavily on class inheritance or single-method delegation, Abstract Factory relies on object composition, often using individual Factory Methods under the hood to instantiate each family member.

## Interview answer — deep senior

Under the hood, Abstract Factory is conceptually a composite of multiple Factory Methods bound by an architectural consistency invariant.
In modern Android architecture powered by Dagger and Hilt, Dagger Components and Subcomponents are direct compile-time implementations of the Abstract Factory pattern. When you define an ActivityComponent or SingletonComponent with multiple provision methods, Dagger generates a concrete factory class under the hood that produces mutually compatible graph instances sharing identical scope and lifecycle boundaries.
In pure Kotlin development, traditional Factory boilerplate is frequently replaced by idiomatic language features. A companion object function or top-level constructor-like function often replaces a standalone Factory class when no dynamic state is required. However, senior architects deliberately retain explicit Abstract Factories when designing multi-tenant SDKs, cross-platform design systems, or plugin architectures where entire component suites must be swapped atomically based on remote configuration or runtime device capabilities.
Automated dependency injection engines eliminate manual factory wiring, but understanding Abstract Factory remains essential when authoring custom Dagger assisted factories via AssistedFactory. Assisted injection allows developers to pass runtime screen parameters while letting Dagger inject compile-time dependencies, effectively combining Factory Method flexibility with container-managed dependency graphs without runtime reflection penalties. Additionally, Abstract Factories can be combined with dynamic feature delivery to instantiate brand-specific visual themes on demand, reducing baseline APK size while guaranteeing architectural encapsulation.

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

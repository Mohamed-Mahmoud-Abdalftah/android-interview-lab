#!/usr/bin/env python3
"""
Elevation script for BLD questions: BLD-08 to BLD-14.
Topic: Build & Gradle (BLD)
Phase 4, Batch 2
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "أنظمة البناء و Gradle و AGP و R8 والـ Signing وإصدار التطبيقات"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# BLD-08: How do you debug crashes that occur only in release builds?
# ==========================================
DATA["BLD-08"] = {
    "concept_en": """Investigating release-only crashes requires systematically isolating code minification, resource stripping, and configuration discrepancies:
- Root Cause Categories:
  1. R8 Minification & Obfuscation: Stripping reflection targets (Gson, Moshi, Retrofit call adapters), renaming serialization properties lacking explicit serial annotations, or stripping default no-arg constructors and JNI entry points.
  2. Missing Keep Rules: Dynamic class loading (Class.forName() or ServiceLoader) failing due to renamed or pruned classes.
  3. Resource Shrinking: shrinkResources replacing dynamically queried resources (via getIdentifier()) with empty dummy stubs.
  4. Bytecode Inlining: Aggressive R8 method inlining changing synchronization timing and exposing underlying thread race conditions.
  5. Configuration Divergence: Release builds enforcing strict SSL pinning, pointing to production endpoints, or missing production API keys.
- Systematic Debugging Protocol:
  - De-obfuscate the release stack trace using the exact mapping.txt and Retrace.
  - Create a benchmark debuggable minified variant (isDebuggable = true alongside isMinifyEnabled = true).
  - Inspect DEX composition with APK Analyzer to confirm symbol preservation.
  - Review R8 usage.txt and configuration.txt diagnostic reports.""",
    "walkthrough_en": """Configuring a debuggable minified variant to debug release crashes with breakpoints:
```kotlin
android {
    buildTypes {
        getByName("release") {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }

        // Dedicated debuggable release variant for local troubleshooting
        create("debugRelease") {
            initWith(getByName("release"))
            matchingFallbacks += listOf("release")
            isDebuggable = true // Enables connecting Android Studio debugger to minified DEX
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}

// Retracing crash via command-line:
// retrace.sh -verbose build/outputs/mapping/release/mapping.txt crash_trace.txt
```""",
    "short_en": """Debugging release-only crashes requires isolating R8 minification and environment discrepancies. Engineers de-obfuscate stack traces using mapping.txt and Retrace, create a debuggable minified build variant to attach Studio's interactive debugger, inspect stripped classes in APK Analyzer, and audit configuration differences like strict SSL pinning or missing keep rules.""",
    "structured_en": """Diagnosing crashes that reproduce exclusively in release builds requires isolating code minification, resource stripping, and build-type configuration differences.
First, de-obfuscate the stack trace. Using the exact release mapping.txt file with Google's Retrace tool restores obfuscated symbols, identifying whether classes, methods, or JSON serialization models were stripped by R8.
Second, create an intermediate debugRelease build variant. By configuring isDebuggable = true alongside isMinifyEnabled = true and release ProGuard rules, engineers can attach the Android Studio debugger directly to minified release bytecode to set breakpoints and inspect runtime state.
Third, inspect binary outputs using APK Analyzer. Verify that required classes, native libraries, and resources exist in the DEX.
Fourth, audit environmental discrepancies between variants, including SSL certificate pinning, ProGuard-stripped reflection targets, and missing production API keys.""",
    "deep_senior_en": """When an application functions perfectly in debug builds but crashes on launch or during user interactions exclusively in release, senior engineers avoid blind guessing by methodically dissecting the delta between build types.
The primary cause in ninety percent of cases is R8 code shrinking and obfuscation.
Because debug builds keep isMinifyEnabled false to maximize compilation speed, reflection-heavy libraries—such as Gson, Moshi, Retrofit call adapters, or custom dependency injection graphs—work fine locally but crash in release because R8 stripped or renamed fields lacking explicit keep rules.
Our first triage step is de-obfuscating the production crash trace using the exact mapping.txt artifact archived during the release build.
If the trace reveals ClassNotFoundException, NoSuchMethodError, or NullPointerException during deserialization, we trace the symbol against R8's usage.txt report to confirm it was erroneously pruned as dead code.
To reproduce and fix the defect, we define a hybrid benchmark build variant: debuggable true combined with minifyEnabled true using production ProGuard files.
This allows us to deploy the minified binary locally, attach Android Studio's interactive debugger, inspect variable states, and verify targeted @Keep annotations or consumer rules.
Finally, we audit non-compiler variances: release builds enforce strict network security configurations such as SSL pinning, ProGuard optimization may expose thread race conditions through aggressive inlining, and release keystore signing may reject invalid third-party SDK certificates.""",
    "meta_ar": {
        "id": "BLD-08",
        "questionAr": "كيف تشخص وتعالج الانهيارات (Crashes) التي تحدث حصرياً في إصدارات الإنتاج (Release Builds) بينما تعمل نسخة الـ Debug بشكل طبيعي؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تشخيص أخطاء الـ Release الحصرية، وفك تشفير تقارير الكراش عبر mapping.txt و Retrace، واستخدام متغير debugRelease لتوصيل الـ Debugger، وفحص تقارير usage.txt و APK Analyzer.",
        "concept_ar": "يتطلب تشخيص الانهيارات الحصرية لإصدارات الإنتاج عزلاً منهجياً لآليات تقليص الكود وحذف الموارد والتباين البيئي: تشكل معالجة R8 السبب الأكبر نتيجة حذف أو تشويش الكلاسات المستهدفة بالـ Reflection (مثل مكتبات تحويل JSON كـ Moshi و Gson أو واجهات JNI) في غياب قواعد Keep صريحة. وتتضمن أسباب الفشل الأخرى حذف الموارد المستدعاة برمجياً عبر getIdentifier بـ shrinkResources، وتغيير توقيت الخيوط بسبب الـ Inlining الحاد. ويتبع المهندس بروتوكولاً علمياً: أولاً فك تشفير الكراش باستخدام ملف mapping.txt وأداة Retrace. ثانياً إنشاء متغير بناء هجين debugRelease يدمج isDebuggable مع تقليص R8 وقواعد الإنتاج لتوصيل مصحح الأخطاء ووضع نقاط التوقف. ثالثاً فحص ملفات classes.dex بـ APK Analyzer ومراجعة ملف usage.txt للتأكد من سبب حذف الرموز. ورابعاً تدقيق الفروق البيئية كشهادات SSL Pinning ومفاتيح API الخاصة بالإنتاج.",
        "walkthrough_ar": """إنشاء متغير بناء debugRelease للتصحيح وفك التشفير بـ Retrace:
```kotlin
android {
    buildTypes {
        getByName("release") {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
        // متغير مخصص لاختبار كود الـ Release مع إمكانية ربط الـ Debugger
        create("debugRelease") {
            initWith(getByName("release"))
            matchingFallbacks += listOf("release")
            isDebuggable = true // يتيح توصيل مصحح الأخطاء
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}
// فك التشفير عبر سطر الأوامر:
// retrace.sh mapping.txt obfuscated_trace.txt
```""",
        "why_it_matters_ar": "يحل المشاكل الأكثر تعقيداً وخطورة التي تفاجئ فرق التطوير بعد نشر التطبيق في المتاجر رغم نجاح كافة الاختبارات في بيئة الـ Debug.",
        "worked_example_ar": "كراش في شاشة الدفع بنسخة المتجر بسبب حذف كلاس الاستجابة PaymentResponse؛ بفك التشفير بـ Retrace تبين أن R8 حذفه لعدم وجود @Keep فتمت معالجته بنجاح.",
        "trade_offs_ar": "إنشاء متغير debugRelease يزيد وقت البناء قليلاً ولكنه يوفر ساعات من التخمين العشوائي ويتيح فحص المشكلة على جهاز حقيقي بدقة تامة.",
        "failure_modes_ar": "التخمين العشوائي وإضافة قواعد -dontobfuscate مما يعطل حماية التطبيق، أو محاولة فك تشفير الكراش بملف mapping من إصدار بناء مختلف.",
        "production_perspective_ar": "في المشروعات الكبرى، نلزم خطوط الـ CI برفع ملف mapping.txt إلى Firebase Crashlytics آلياً، ونختبر متغير debugRelease في مرحلة الـ QA قبل كل إصدار رسمي.",
        "how_to_answer_ar": "رتب خطوات التشخيص: أولاً فك تشفير الكراش بـ Retrace و mapping.txt، ثانياً عزل المشكلة بإنشاء متغير debugRelease، ثالثاً فحص ملف usage.txt و APK Analyzer، ورابعاً تدقيق شهادات SSL والمفاتيح.",
        "talking_points_ar": "تأثير R8 على Reflection، دور أداة Retrace، متغير debugRelease، وفحص usage.txt للرموز المحذوفة.",
        "follow_ups_ar": "- **المحاور:** 'ما الفائدة من فحص ملف usage.txt عند حدوث كراش في الـ Release؟'\n  **المرشح:** 'ملف usage.txt يحتوي على القائمة الكاملة لكافة الكلاسات والدوال والمتغيرات التي اعتبرها R8 كوداً ميتاً وقام بحذفها من الـ DEX؛ فإذا وجدنا الكلاس المنهار بداخله، نتأكد فوراً أنه حُذف بسبب نقص قواعد الحفظ Keep Rules.'\n\n- **المحاور:** 'كيف يمكن لـ SSL Pinning أن يسبب كراش أو فشل في الـ Release فقط؟'\n  **المرشح:** 'في كثير من التطبيقات يتم تعطيل فحص شهادات SSL في الـ Debug لتسهيل فحص الشبكة بـ Charles أو Proxyman، بينما يطبق بصرامة في الـ Release؛ فإذا كانت بصمة الشهادة غير محدثة أو منتهية، تفشل كافة اتصالات الشبكة في الإنتاج فقط.'",
        "self_check_ar": "هل غطيت خطوات فك التشفير بـ Retrace ومتغير debugRelease وفحص usage.txt والفروق البيئية كالـ SSL؟",
        "references_ar": f"- [Android Developers: Shrink, obfuscate, and optimize your app](https://developer.android.com/build/shrink-code) — الدليل الشامل لمعالجة مشاكل R8 والـ Release.\n- [R8 Retrace Tool](https://developer.android.com/tools/retrace) — توثيق أداة فك تشفير تقارير الكراش في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يتطلب تشخيص كراش الإنتاج فك تشفير تتبع الخطأ عبر mapping.txt وأداة Retrace، وإنشاء متغير بناء debuggable مع تفعيل R8 لربط مصحح الأخطاء، وفحص ملفات DEX بـ APK Analyzer لاكتشاف الكلاسات المحذوفة، وتدقيق قواعد الحماية للـ Reflection وشهادات SSL.",
        "best_answer_ar": """يستدعي انهيار التطبيق في إصدار الـ Release فقط بينما يعمل في Debug فحصاً منهجياً للفروق التقنية بين البيئتين.

الخطوة الأولى هي فك تشفير تقرير الكراش باستخدام ملف mapping.txt الخاص بنفس الإصدار عبر أداة Retrace؛ مما يكشف الأسماء الحقيقية للكلاسات والدوال ويحدد ما إذا كان الخطأ ناتجاً عن حذف حقول الـ Reflection في تحويل الـ JSON أو دوال JNI.

الخطوة الثانية هي إنشاء متغير بناء هجين debugRelease؛ حيث نفعل فيه isDebuggable مع تفعيل تقليص R8 وقواعد ProGuard، مما يتيح ربط الـ Debugger في Android Studio ووضع نقاط التوقف وفحص الذاكرة على الكود المشوش مباشرة.

الخطوة الثالثة هي فحص الحزمة بـ APK Analyzer للتأكد من وجود الكلاسات المطلوبة في ملفات DEX، ومراجعة الفروق البيئية مثل تشديد فحص شهادات SSL في الإنتاج أو غياب مفاتيح API المخصصة لنسخة المتجر.""",
        "deep_answer_ar": """في قيادة هندسة المنصات، يعتبر انهيار نسخة الإنتاج فقط كابوساً يتكرر عند إهمال الفروق المعمارية بين بيئات البناء، ويتطلب حله مساراً هندسياً صارماً.

أولاً، في الغالبية الساحقة من الحالات، يكون السبب هو تقليص وتشويش الكود عبر R8؛ فنسخة Debug تعطل التقليص، مما يخفي أخطاء مكتبات الـ Reflection كـ Gson أو Moshi. فعند تفعيل R8 في Release، يحذف المحرك الحقول غير المستخدمة ظاهرياً أو يغير أسماءها، مما يسبب NullPointerException أثناء قراءة بيانات السيرفر. ولتشخيص ذلك، نستخدم ملف mapping.txt المطابق تماماً للإصدار لفك تشفير الـ Stack Trace ومعرفة السطر المتسبب بدقة.

ثانياً، لإعادة إنتاج المشكلة محلياً، ننشئ Build Variant يجمع بين debuggable = true و minifyEnabled = true، مما يسمح بتوصيل أداة التصحيح في أندرويد ستوديو وفحص سلوك الكود المقلص لحظياً.

ثالثاً، نستخدم APK Analyzer لفحص محتويات ملف classes.dex والتأكد من عدم حذف المشيدات الافتراضية، مع تدقيق الفروق الأمنية كـ SSL Pinning ومفاتيح الـ SDKs التي تنشط في الإنتاج فقط لضمان سلامة الإصدار قبل إطلاقه للمستخدمين. كما نلزم الفرق بكتابة اختبارات أتمتة على أجهزة حقيقية لنسخة الـ Release داخل خط الـ CI للتأكد من سلامة الشاشات الرئيسية وقدرتها على العمل دون كراش قبل إرسال النسخة للمتجر."""
    }
}

# ==========================================
# BLD-09: How do you decide R8 keep rules for reflection, serialization, JNI, and SDKs?
# ==========================================
DATA["BLD-09"] = {
    "concept_en": """Authoring production R8 keep rules balances runtime safety against aggressive code and resource reduction:
- Core Guiding Principle: Keep rules must be surgical. Sweeping wildcards (e.g., -keep class com.mycompany.** { *; }) defeat tree-shaking, re-introduce dead code, and bloat the final DEX.
- Reflection & Serialization:
  * Prefer Compile-Time Code Generation: Modern pipelines replace reflection serializers with Kotlinx Serialization (@Serializable) or Moshi with code generation (@JsonClass(generateAdapter = true)), completely eliminating reflection keep rules.
  * Surgical Rules for Reflection: When using Gson or reflective parsers, preserve only fields via -keepclassmembers class com.example.models.** { <fields>; }, allowing R8 to obfuscate and optimize class names and unused constructors.
- JNI Native Integration:
  * Preserve native method declarations via -keepclasseswithmembernames class * { native <methods>; }.
  * Protect Java/Kotlin classes and callback methods invoked from C++ via explicit @Keep annotations.
- Third-Party SDKs & Dependencies:
  * Rely on bundled consumerProguardFiles packaged within official AARs.
  * Avoid manual SDK keep rules unless an unmaintained library lacks consumer declarations.""",
    "walkthrough_en": """Surgical keep rules and compile-time annotations:
```kotlin
// 1. Preferred modern approach: Compile-time serialization (Zero ProGuard rules needed!)
@Serializable
data class UserDto(val id: String, val username: String)

// 2. Direct code annotation via @Keep
@Keep
class NativeBridgeCallback {
    fun onNativePayloadReceived(data: ByteArray) { /* Invoked from C++ */ }
}

// 3. Surgical proguard-rules.pro:
// Preserve native method signatures globally
-keepclasseswithmembernames class * {
    native <methods>;
}

// Preserve only JSON fields for legacy reflective models (allow class renaming)
-keepclassmembers class com.example.legacy.models.** {
    <fields>;
}

// Preserve enum values() and valueOf() methods
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}
```""",
    "short_en": """Deciding R8 keep rules requires precision to avoid disabling tree-shaking. Engineers prefer compile-time serialization like Kotlinx Serialization or Moshi codegen to eliminate reflection rules, use targeted keepclassmembers for JSON fields, protect native JNI signatures, and rely on consumerProguardFiles while strictly avoiding broad package-level wildcards.""",
    "structured_en": """Authoring R8 keep rules requires surgically protecting runtime dynamic symbols while preserving maximal dead-code elimination.
First, eliminate reflection where possible. Modern architectures replace reflection-heavy serializers with compile-time code generation such as Kotlinx Serialization or Moshi with generateAdapter, making manual keep rules unnecessary.
Second, for legacy reflection or Gson, use targeted member rules: apply -keepclassmembers to preserve only serializable fields rather than preserving entire classes and methods.
Third, protect native JNI bridges using -keepclasseswithmembernames to preserve methods declared external alongside their associated parameter types and C-callback classes.
Fourth, for third-party SDKs, rely on bundled consumerProguardFiles rather than authoring external rules.
Fifth, enforce strict code review rejecting broad wildcards like -keep class com.**, which disables tree-shaking across thousands of classes.""",
    "deep_senior_en": """In enterprise Android codebases, poorly authored ProGuard and R8 rules represent one of the fastest paths to binary bloat and technical debt.
A common anti-pattern when encountering a release crash is adding a sweeping wildcard like -keep class com.company.** { *; }.
This brute-force approach immediately disables tree shaking, dead code elimination, and obfuscation across the entire package, defeating the core benefits of R8 and bloating DEX size.
Senior engineers adhere to a principled hierarchy.
Our first strategy is replacing runtime reflection with compile-time code generation.
By migrating from Gson to Kotlinx Serialization or Moshi with KSP code generation, serializers generate explicit adapter classes during compilation, completely removing the need for reflection keep rules.
When reflection is unavoidable—such as interacting with legacy backend DTOs—we write surgical rules: -keepclassmembers class com.example.dto.** { <fields>; }.
This preserves the field names required for JSON key mapping while allowing R8 to obfuscate and optimize class names, constructors, and unused helper methods.
For native C++ integration, we configure -keepclasseswithmembernames class * { native <methods>; } and annotate Java callback classes invoked from C++ with @Keep.
Finally, for third-party libraries, we verify that dependencies supply clean consumerProguardFiles, and use R8's configuration artifact to audit that imported rules do not pollute global compilation.""",
    "meta_ar": {
        "id": "BLD-09",
        "questionAr": "كيف تحدد وتصيغ قواعد الحفظ (Keep Rules) في R8 للتعامل مع الـ Reflection وتحويل البيانات (Serialization) ودوال JNI ومكتبات الـ SDKs دون إهدار التقليص؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم صياغة قواعد R8 الجراحية، واستبدال الـ Reflection بالتوليد الآلي Compile-Time Codegen، والتعامل مع دوال النيتف JNI، والتحذير من القواعد العامة الواسعة.",
        "concept_ar": "تتطلب صياغة قواعد الحفظ (Keep Rules) في R8 توازناً دقيقاً بين حماية الرموز الديناميكية وأقصى تقليص ممكن للكود والموارد: المبدأ الجوهري هو الصياغة الجراحية الدقيقة وتجنب القواعد الشاملة كـ -keep class com.** التي تعطل التقليص وتعيد إدخال الأكواد الميتة. وفي تحويل البيانات (Serialization)، نفضل الانتقال للمكتبات المعتمدة على التوليد البرمجي وقت التجميع كـ Kotlinx Serialization أو Moshi Codegen للاستغناء كلياً عن قواعد الحفظ؛ وعند الاضطرار لاستخدام Gson نقتصر على حفظ الحقول فقط بـ keepclassmembers للسماح بتشويش الكلاسات والمشيدات. وفي دوال النيتف JNI، نستخدم keepclasseswithmembernames لحفظ الدوال المعلنة كـ native مع استخدام تعليق @Keep لحماية الكلاسات المستدعاة من C++. وفي مكتبات الـ SDKs، نعتمد على قواعد consumerProguardFiles المدمجة في حزم AAR، ونراجع ملف configuration.txt للتأكد من خلو المشروع من قواعد عشوائية ضارة.",
        "walkthrough_ar": """صياغة قواعد جراحية واستخدام التوليد المكتبي الآمن:
```kotlin
// 1. الحل الأمثل: Kotlinx Serialization (لا يتطلب أي قواعد R8)
@Serializable
data class ArticleDto(val id: String, val title: String)

// 2. حماية كلاسات الاستدعاء من C++ بتعليق @Keep
@Keep
class JniDispatcher {
    fun onEvent(code: Int) {}
}

// 3. قواعد جراحية في proguard-rules.pro
// حفظ أسماء حقول الـ DTO القديمة فقط دون حجز كامل الكلاس
-keepclassmembers class com.example.models.** {
    <fields>;
}

// حفظ كافة دوال النيتف JNI
-keepclasseswithmembernames class * {
    native <methods>;
}
```""",
        "why_it_matters_ar": "يمنع تضخم حجم التطبيق بآلاف الأسطر الميتة نتيجة القواعد الفضفاضة، ويحمي استقرار التطبيق من كراش الـ Reflection والـ JNI في بيئة الإنتاج.",
        "worked_example_ar": "تطبيق كان يستخدم -keep class com.mycompany.** بحجم 45 ميجابايت؛ وبإعادة صياغة القواعد جراحياً واستخدام Kotlinx Serialization انخفض الحجم إلى 26 ميجابايت.",
        "trade_offs_ar": "القواعد الجراحية تتطلب دقة وفهماً عميقاً لبنية الكود ولكنها توفر أعلى درجات التقليص، بينما القواعد الواسعة سهلة الكتابة لكنها تهدر مساحة الـ DEX بالكامل.",
        "failure_modes_ar": "استخدام قواعد فضفاضة بعلامات النجمة { *; } مما يحفظ كل شيء ويعطل R8، أو نسيان حماية دوال C++ التي تستدعي كود كوتلن فينهار التطبيق عند تنفيذ JNI.",
        "production_perspective_ar": "في المشروعات الكبرى، نفرض مراجعة كود صارمة لأي سطر يضاف لملف proguard-rules.pro، ونلزم الفرق بالانتقال لـ Kotlinx Serialization للتخلص من قواعد الـ Reflection نهائياً.",
        "how_to_answer_ar": "وضح المبدأ: القواعد الجراحية مقابل القواعد الفضفاضة، ثم بين كيفية الاستغناء عن القواعد بـ Compile-time Codegen، وصياغة قواعد الحقول لـ Gson وقواعد JNI لـ C++.",
        "talking_points_ar": "خطورة القواعد العامة، ميزة Kotlinx Serialization، استخدام keepclassmembers للحقول، وحماية واجهات JNI بـ @Keep.",
        "follow_ups_ar": "- **المحاور:** 'ما الفرق بين -keep و -keepclassmembers في قواعد R8؟'\n  **المرشح:** 'قاعدة -keep تحفظ الكلاس بالكامل وأسماءه ومشيداته وحقوله وتمنع تشويشه أو تقليصه، بينما -keepclassmembers تسمح لـ R8 بتشويش اسم الكلاس وحذف دواله غير المستخدمة مع الاقتصار على حفظ أعضاء معينة كالحقول فقط، مما يوفر تقليصاً أفضل بكثير.'\n\n- **المحاور:** 'لماذا لا تحتاج مكتبة Kotlinx Serialization إلى قواعد ProGuard لحقول الـ JSON؟'\n  **المرشح:** 'لأنها لا تستخدم الـ Reflection وقت التشغيل؛ بل يولد المترجم كود Serializer ثابت يحتوي على أسماء المفاتيح كنصوص ثابتة مشفرة في البايت كود، فيستطيع R8 تشويش أسماء حقول الكلاس دون أن تتأثر عملية قراءة الـ JSON.'",
        "self_check_ar": "هل شرحت مخاطر القواعد الفضفاضة؟ وهل بينت الفرق بين keep و keepclassmembers وميزة التوليد الآلي بـ Kotlinx Serialization؟",
        "references_ar": f"- [Android Developers: ProGuard Rule Syntax Reference](https://www.guardsquare.com/manual/configuration/usage) — المرجع الشامل لقواعد ProGuard و R8.\n- [Kotlinx Serialization Guide](https://github.com/Kotlin/kotlinx.serialization) — التوثيق الرسمي لمكتبة كوتلن للتحويل المكتبي.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "تعتمد صياغة قواعد R8 على الدقة الجراحية لمنع تعطيل تقليص الكود؛ فنفضل أدوات التوليد المكتبي كـ Kotlinx Serialization للاستغناء عن قواعد الـ Reflection، ونستخدم keepclassmembers لحفظ حقول الـ JSON فقط، ونحمي دوال JNI، ونعتمد على consumerProguardFiles مع حظر القواعد العامة.",
        "best_answer_ar": """تتطلب كتابة قواعد الحفظ Keep Rules في R8 دقة هندسية بالغة لحماية الكود الديناميكي دون إهدار فوائد تقليص حجم التطبيق.

القاعدة الأولى هي تفضيل البدائل البرمجية في وقت التجميع Compile-time؛ حيث نعتمد على Kotlinx Serialization أو Moshi مع مولدات الكود، مما يلغي الحاجة تماماً لكتابة قواعد حماية للـ Reflection.

القاعدة الثانية عند التعامل مع تحويلات JSON الانعكاسية مثل Gson، هي استخدام قواعد جراحية دقيقة؛ فنستخدم keepclassmembers لحفظ أسماء الحقول فقط دون منع تشويش أسماء الكلاسات والمشيدات الأخرى.

القاعدة الثالثة هي حماية دوال C++ ومكتبات JNI عبر keepclasseswithmembernames لحفظ الدوال المعلنة كـ external، مع وضع تعليق Keep على الكلاسات التي تستدعى من كود النيتف.

القاعدة الرابعة هي الاعتماد على consumerProguardFiles الخاصة بحزم الـ SDKs، والحظر التام لاستخدام الرموز العامة الواسعة مثل -keep class com.** التي تعطل التقليص بالكامل.""",
        "deep_answer_ar": """في إدارة التطبيقات الضخمة، تمثل كتابة قواعد R8 العشوائية أحد أكبر أسباب تضخم حجم التطبيق وضعف أمانه؛ فكثير من المطورين يلجأون لحفظ حزم كاملة بقواعد عامة مثل -keep class com.app.** { *; } بمجرد حدوث كراش، مما يعطل ميزة حذف الكود الميت تماماً.

المهندس الأول يتبع نهجاً مدروساً يبدأ بالقضاء على الـ Reflection؛ بالانتقال إلى مكتبات التوليد الآلي كـ Kotlinx Serialization، حيث يولد المترجم كود التحويل مسبقاً فلا تحتاج نماذج البيانات لأي قواعد حفظ في R8.

وإذا اضطررنا للتعامل مع نماذج قديمة، نكتب قواعد ميكروسكوبية تحفظ الحقول فقط عبر keepclassmembers class com.app.models.** { <fields>; }، مما يسمح لـ R8 بتشويش اسم الكلاس وحذف الدوال غير المستخدمة بداخله.

وفي التعامل مع لغة C++ عبر JNI، نحمي الدوال الأصلية عبر keepclasseswithmembernames class * { native <methods>; }، ونضع تعليق @Keep المباشر فوق الكلاسات التي تستدعيها دوال C++.

وأخيراً، نراجع ملف configuration.txt في الـ CI للتأكد من أن مكتبات الـ SDKs لا تفرض قواعد جائرة تعطل التقليص، ونرفض أي Pull Request يضيف قواعد حفظ واسعة النطاق لضمان بقاء التطبيق خفيفاً وآمناً. كما نوثق أسباب كل قاعدة حفظ بدقة داخل الكود، لضمان مراجعتها دورياً وحذف أي قواعد لم تعد ضرورية بعد ترقية المكتبات البرمجية."""
    }
}

# ==========================================
# BLD-10: How do you use retrace with mapping files?
# ==========================================
DATA["BLD-10"] = {
    "concept_en": """The Retrace tool restores human-readable source code symbols from obfuscated production stack traces using cryptographic mapping files:
- Mapping File Lifecycle: During release builds, R8 outputs a mapping.txt file (located at build/outputs/mapping/{variant}/mapping.txt). This text file contains a bidirectional symbol dictionary recording how original package names, class names, field identifiers, and method signatures were transformed into obfuscated tokens (e.g., a.b.c: void a() -> com.example.repo.UserRepository: void fetchUser()).
- Execution Mechanics: The Retrace CLI tool (available via Android SDK commandline-tools or bundled R8 jars) takes the raw obfuscated stack trace and the corresponding mapping.txt, reconstructing original file names, line numbers, and inlined call frames.
- Automated Production Pipelines: In enterprise architectures, mapping files are automatically uploaded to crash reporting platforms (such as Firebase Crashlytics or Google Play Console) via Gradle plugins during release publication.
- Strict Version Fidelity: A mapping file is valid exclusively for the exact git commit, versionCode, and build hash that produced it. Retracing an obfuscated trace against a mismatched mapping file produces corrupt or entirely hallucinated method mappings.""",
    "walkthrough_en": """Executing Retrace via command-line and configuring automated Crashlytics uploads:
```bash
# 1. Command-line de-obfuscation using SDK Retrace tool
$ANDROID_HOME/cmdline-tools/latest/bin/retrace \
    -verbose \
    app/build/outputs/mapping/release/mapping.txt \
    obfuscated_crash.txt
```

```kotlin
// 2. build.gradle.kts: Automated Crashlytics mapping upload in CI
plugins {
    alias(libs.plugins.google.services)
    alias(libs.plugins.firebase.crashlytics)
}

android {
    buildTypes {
        getByName("release") {
            isMinifyEnabled = true
            firebaseCrashlytics {
                mappingFileUploadEnabled = true // Uploads mapping.txt automatically upon release build
            }
        }
    }
}
```""",
    "short_en": """Retrace uses the compilation-specific mapping.txt generated by R8 to translate obfuscated, minified stack traces back into original class names, methods, and line numbers. It executes via the Android SDK command-line tool, Android Studio, or automated CI plugins uploading maps to Firebase Crashlytics and Google Play Console.""",
    "structured_en": """Using Retrace with mapping files is essential for diagnosing production exceptions generated by obfuscated release binaries.
First, understand the artifact. During release compilation, R8 outputs mapping.txt, which records a bidirectional cryptographic dictionary mapping obfuscated symbols (such as a.b.c) to original human-readable source classes, method names, and line numbers.
Second, execute de-obfuscation via the command-line tool bundled in the Android SDK commandline-tools directory: retrace.sh mapping.txt obfuscated_trace.txt.
Third, automate de-obfuscation in enterprise pipelines. CI pipelines archive mapping.txt alongside the release AAB in artifact repositories, and leverage the Firebase Crashlytics Gradle plugin or Play Developer API to upload mapping files automatically during release deployment.
Fourth, preserve strict version coupling: a mapping file is valid exclusively for the exact commit and versionCode that generated it.""",
    "deep_senior_en": """In production crash monitoring and platform engineering, the ability to rapidly decipher obfuscated stack traces is critical for maintaining application stability and meeting service-level agreements.
When an application is compiled with R8 obfuscation, class names, method signatures, and file references are transformed into terse identifiers to shrink DEX tables and protect proprietary logic.
Consequently, a raw production crash report appears as an indecipherable hierarchy of at a.b.c.d(SourceFile:42).
To restore full stack readability, Google provides the Retrace utility, packaged inside Android SDK build-tools and R8 distributions.
Retrace ingests two inputs: the obfuscated stack trace text and the exact mapping.txt file emitted by R8 during that specific build at build/outputs/mapping/{variant}/mapping.txt.
Parsing the line-number intervals and ambiguity tables in the map, Retrace reconstructs the original packages, classes, inlined call frames, and source code line numbers.
In professional production pipelines, engineers never perform manual command-line retracing for daily triage.
Instead, we automate the de-obfuscation pipeline: our GitHub Actions CI pipeline uses the Firebase Crashlytics Gradle plugin to upload mapping.txt directly to Google during the release deployment step.
Furthermore, we mandate immutable artifact archiving in AWS S3 or Artifactory, indexing each mapping.txt by the exact git commit SHA and versionCode.
Because a single source modification alters R8's symbol generation, attempting to retrace a crash with a mapping file from a neighboring build produces corrupt, hallucinated method names, making strict version fidelity mandatory.""",
    "meta_ar": {
        "id": "BLD-10",
        "questionAr": "كيف تستخدم أداة Retrace مع ملفات المخطط (mapping.txt) لفك تشفير تقارير الأخطاء المشوشة في الإنتاج؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم دور ملف mapping.txt في فك تشفير تقارير الكراش، واستخدام أداة Retrace، وأتمتة الرفع لـ Firebase Crashlytics و Play Console في الـ CI، ومبدأ التطابق الحصري للإصدار.",
        "concept_ar": "تعد أداة Retrace الوسيلة القياسية لاستعادة أسماء الكلاسات والدوال وأرقام الأسطر الأصلية من تقارير الأخطاء المشوشة في إصدارات الإنتاج: يقوم محرك R8 أثناء بناء نسخة الـ Release بتوليد ملف mapping.txt في مسار المخرجات؛ وهو قاموس تشفير ثنائي الاتجاه يسجل المقابلة بين الرموز المختصرة مثل a.b() والأسماء الحقيقية في كود كوتلن الأصلي. وتستقبل أداة Retrace (المتاحة في أدوات سطر أوامر أندرويد) تقرير الكراش المشفر مع ملف الـ mapping لتعيد رسم تسلسل الخطأ الحقيقي بدقة متناهية متضمنة الدوال المدمجة بـ Inlining. وفي المعماريات الحديثة، تتم أتمتة هذه العملية برفع الملف لمنصات مثل Firebase Crashlytics و Google Play Console تلقائياً عبر ملحقات Gradle في خط الـ CI، مع التأكيد الصارم على أن ملف الـ mapping فريد وحصري لرقم الإصدار ورمز Commit SHA الدقيق الذي أنتجه.",
        "walkthrough_ar": """تشغيل أداة Retrace وأتمتة الرفع لمنصة Crashlytics في Gradle:
```bash
# 1. فك تشفير تقرير الكراش عبر سطر الأوامر
retrace mapping.txt obfuscated_trace.txt
```

```kotlin
// 2. رفع ملف الـ mapping آلياً في خط الـ CI عبر Gradle
plugins {
    alias(libs.plugins.firebase.crashlytics)
}
android {
    buildTypes.getByName("release") {
        isMinifyEnabled = true
        firebaseCrashlytics {
            mappingFileUploadEnabled = true // رفع الملف تلقائياً فور البناء
        }
    }
}
```""",
        "why_it_matters_ar": "يمكن الفرق الهندسية من قراءة تقارير الكراش وفهم أسباب الانهيارات الغامضة في الإنتاج وحلها فوراً بدلاً من إهدار الوقت في فك شفرات مبهمة.",
        "worked_example_ar": "استقبال كراش مبهم في Crashlytics يشير إلى at c.a.b(SourceFile:1)؛ وبفك تشفيره بـ Retrace و mapping.txt تبين أنه NullPointerException في دالة ProfileRepository.getUser().",
        "trade_offs_ar": "أرشفة ورفع ملفات mapping.txt تتطلب مساحة تخزين وتنسيقاً في خط الـ CI ولكنها لا غنى عنها على الإطلاق لتشخيص أي مشكلة إنتاجية.",
        "failure_modes_ar": "فقدان ملف mapping.txt بعد إصدار النسخة مما يجعل قراءة كراش الإنتاج مستحيلة، أو استخدام ملف mapping لإصدار مختلف فينتج أسماء دوال وهمية ومضللة.",
        "production_perspective_ar": "في المشروعات الكبرى، نؤرشف ملف mapping.txt في مستودع سحابي دائم S3 مفهرساً برقم الـ Build والـ Git SHA، ونفعل الرفع التلقائي لـ Crashlytics مع كل إطلاق.",
        "how_to_answer_ar": "اشرح دور mapping.txt كقاموس للمقابلة بين الأسماء المشوشة والأصلية، ثم بين كيفية عمل أداة Retrace، واختم بأهمية الأتمتة في الـ CI والحذر من خلط ملفات الإصدارات المختلفة.",
        "talking_points_ar": "مفهوم قاموس mapping.txt، استرجاع الدوال المدمجة Inlined Methods، الأتمتة عبر Crashlytics Plugin، وخطورة عدم تطابق الإصدارات.",
        "follow_ups_ar": "- **المحاور:** 'ماذا يحدث إذا حاولت فك تشفير كراش بملف mapping.txt مأخوذ من Commit مجاور؟'\n  **المرشح:** 'ستنتج أداة Retrace نتائج مضللة تماماً تُعرف بالـ Hallucinated Traces؛ لأن R8 يعيد توزيع الحروف المبهمة مثل a و b مع أي تعديل طفيف في الكود، فتشير الأداة لكلاسات ودوال لا علاقة لها بالخطأ الحقيقي وتضلل الفريق.'\n\n- **المحاور:** 'كيف يتعامل Retrace مع الدوال التي تم دمجها بأسلوب Inlining أثناء التحسين؟'\n  **المرشح:** 'يسجل R8 فترات أرقام الأسطر Line Number Ranges الخاصة بالدوال المدمجة داخل ملف الـ mapping؛ فتستطيع Retrace تفكيك السطر الواحد إلى عدة أسطر استدعاء متسلسلة تعكس مسار الكود الأصلي بدقة.'",
        "self_check_ar": "هل شرحت بنية mapping.txt ودور Retrace؟ وهل بينت كيفية الأتمتة في CI ومخاطر استخدام ملف من إصدار مختلف؟",
        "references_ar": f"- [Android Developers: Retrace Obfuscated Stack Traces](https://developer.android.com/tools/retrace) — التوثيق الرسمي لأداة Retrace وفك التشفير.\n- [Firebase Crashlytics: Get de-obfuscated crash reports](https://firebase.google.com/docs/crashlytics/get-deobfuscated-reports) — دليل أتمتة رفع خرائط R8 لـ Crashlytics.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "تستخدم أداة Retrace ملف mapping.txt الناتج عن تجميع R8 لإعادة ترجمة تقارير الكراش المشوشة والمختصرة إلى الأسماء الحقيقية للكلاسات والدوال وأرقام الأسطر الأصلية. وتعمل عبر سطر الأوامر أو آلياً برفع الملف إلى Crashlytics ومتجر Google Play في خط الـ CI.",
        "best_answer_ar": """تعد أداة Retrace الركيزة الأساسية لتشخيص وقراءة تقارير الأخطاء الناتجة عن نسخ الإنتاج المقلصة والمشوشة بـ R8.

يولد محرك R8 أثناء بناء نسخة الـ Release ملفاً يسمى mapping.txt في مسار المخرجات؛ وهو قاموس تحويل ثنائي يسجل المقابلة الدقيقة بين الأسماء المشوشة مثل a.b.c() والأسماء الأصلية للكلاسات والدوال وأرقام الأسطر في كود كوتلن.

تستقبل أداة Retrace ملف الـ mapping مع نص تقرير الكراش المشفر، وتقوم باسترجاع شجرة الاستدعاءات الأصلية بالكامل بما فيها الدوال التي تم دمجها عبر الـ Inlining.

وفي بيئات العمل الاحترافية، لا نعتمد على فك التشفير اليدوي؛ بل نبرمج خطوط الـ CI لرفع ملف mapping.txt تلقائياً لمنصة Firebase Crashlytics ومتجر Google Play فور إتمام بناء النسخة، مع أرشفته في مستودع آمن مرتبط برقم الإصدار ورمز Commit SHA.""",
        "deep_answer_ar": """في إدارة استقرار التطبيقات بالإنتاج، يمثل فك تشفير تقارير الكراش مسألة حيوية لحل المشاكل الحرجة؛ فعند تشغيل R8، يتحول تتبع الخطأ إلى نصوص مبهمة مثل at x.y.z(SourceFile:12) يستحيل فهمها يدوياً.

هنا يأتي دور أداة Retrace المدمجة في حزمة أدوات أندرويد؛ حيث تقرأ ملف mapping.txt المولد في مجلد build/outputs/mapping/release؛ وتقوم بمطابقة كل رمز مبهم بالدالة الأصلية وملف كوتلن الأصلي، بل وتفكك الدوال التي دمجها المترجم بأسلوب Inlining لتعيد رسم تسلسل الاستدعاء الحقيقي بدقة.

ولكن يحذر مهندسو المنصات من التهاون في إدارة ملفات المخطط؛ فملف mapping.txt فريد وحصري للنسخة التي ولدته؛ ومحاولة فك تشفير كراش باستخدام ملف مأخوذ من Commit مختلف سينتج أسطر وأسماء دوال وهمية وخاطئة تماماً.

لذلك نلزم خطوط الـ CI برفع ملف mapping.txt آلياً لمنصتي Google Play Console و Firebase Crashlytics فور إطلاق النسخة، مع حفظ نسخة احتياطية مشفرة في خوادم التخزين السحابية ومفهرسة برقم versionCode الدقيق لضمان القدرة على تشخيص أي كراش مستقبلي بنقرة زر. وعند استقبال تقارير كراش معقدة، نستخدم أدوات Retrace المتقدمة للتحقق من سلامة فك الشفرة واستخراج المتغيرات المحلية، مما يوفر رؤية هندسية واضحة تساعد المطورين على إصلاح المشكلة وتفادي تكرارها في التحديثات القادمة بأعلى معايير الدقة والاحترافية الهندسية."""
    }
}

# ==========================================
# BLD-11: How do you analyze APK/AAB size and bundled native ABIs?
# ==========================================
DATA["BLD-11"] = {
    "concept_en": """Auditing application package size and managing compiled native processor architectures prevents download abandonment:
- APK Analyzer Inspection: Android Studio's APK Analyzer and command-line apkanalyzer decompose release artifacts into primary storage buckets:
  1. classes.dex: Total method counts, field counts, and byte consumption per package/dependency.
  2. res & assets: High-resolution raster images, uncompressed audio/video, and localized string XML tables.
  3. lib/ Directory: Shared native libraries (.so) compiled across Application Binary Interfaces (ABIs: armeabi-v7a, arm64-v8a, x86, x86_64).
- The Native ABI Bloat Problem: Bundling all four architectures into a monolithic universal APK quadruples the size of native libraries (such as WebRTC, SQLCipher, or TensorFlow Lite).
- Modern Remediation:
  * Android App Bundles: Google Play dynamically generates per-device ABI split APKs, delivering exclusively arm64-v8a to modern devices and eliminating unused 32-bit and x86 binaries.
  * Gradle abiFilters: Restricts compiled and bundled architectures using ndk.abiFilters to prune obsolete ABIs from release artifacts.""",
    "walkthrough_en": """Inspecting APK composition with apkanalyzer and configuring ABI filters:
```bash
# 1. Analyze APK breakdown via CLI tool
apkanalyzer apk summary app-release.apk
apkanalyzer dex methods app-release.apk
```

```kotlin
// 2. build.gradle.kts: Pruning unwanted native ABIs and configuring splits
android {
    defaultConfig {
        ndk {
            // Include only modern mobile ARM architectures, pruning x86
            abiFilters += listOf("armeabi-v7a", "arm64-v8a")
        }
    }

    // Optional for standalone APK distribution: generate per-ABI APK splits
    splits {
        abi {
            isEnable = true
            reset()
            include("armeabi-v7a", "arm64-v8a")
            isUniversalApk = false
        }
    }
}
```""",
    "short_en": """Analyzing APK/AAB size requires APK Analyzer in Android Studio or command-line apkanalyzer to audit DEX method counts, media assets, and native libraries. Engineers eliminate ABI bloat by publishing AABs for dynamic split delivery, configuring ndk.abiFilters to prune legacy architectures, and converting images to WebP.""",
    "structured_en": """Auditing and reducing application download footprints requires structural binary analysis and targeted ABI optimization.
First, utilize APK Analyzer in Android Studio or the apkanalyzer command-line tool. It decomposes the binary into classes.dex method counts, raw resources, compressed assets, and native .so shared libraries.
Second, diagnose native ABI overhead inside the lib directory. A monolithic APK bundling binaries for all architectures (armeabi-v7a, arm64-v8a, x86, x86_64) quadruples native code footprint.
Third, publish via Android App Bundles. Google Play's dynamic delivery partitions the AAB, serving users a tailored ABI split containing exclusively their device's target architecture.
Fourth, configure ndk.abiFilters in build.gradle.kts to exclude obsolete architectures like x86 from production builds, paired with R8 resource shrinking and WebP image conversion.""",
    "deep_senior_en": """In consumer mobile applications, binary size directly correlates with user acquisition metrics: Google's research proves that every six-megabyte increase in APK size decreases store install conversion rates by one percent.
To combat binary bloat, platform teams conduct automated size audits using APK Analyzer and CLI tooling.
Our first analysis targets the raw archive composition.
Using apkanalyzer apk summary, we inspect the top three contributors: classes.dex byte allocation, the res and assets directories, and the lib/ native architecture folders.
For DEX bloat, we examine the method count and third-party dependency graph, applying R8 tree shaking and replacing bulky transitive libraries with lightweight alternatives.
For resources, we enforce lossless WebP conversion and migrate static vector assets into XML VectorDrawables.
The most severe bloat often occurs within native C++ libraries stored in lib/.
If an app includes native libraries—such as WebRTC, SQLCipher, or TensorFlow Lite—packaging all four ABIs (armeabi-v7a, arm64-v8a, x86, and x86_64) into a universal APK duplicates binary code four times over.
To eliminate this, we publish exclusively using Android App Bundles.
Play Console automatically generates per-device ABI split APKs, delivering only 64-bit ARM binaries to modern phones and slashing the download footprint by twenty to forty megabytes.
In CI, we enforce automated size budgets, failing pull requests that introduce more than two hundred kilobytes of unapproved binary weight.""",
    "meta_ar": {
        "id": "BLD-11",
        "questionAr": "كيف تحلل حجم حزم APK و AAB والمكتبات المترجمة (Native ABIs) المدمجة بها لتقليص حجم التطبيق؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم تقنيات تحليل حجم الحزم بأداة APK Analyzer، وإدارة معمارية المعالجات ABIs في مجلد lib، ودور AAB في تجزئة المعالجات، واستخدام ndk.abiFilters وميزانيات الحجم في CI.",
        "concept_ar": "يحمي التحليل الدوري لحجم التطبيق وإدارة مكتبات المعالجات المترجمة (Native ABIs) من تراجع معدلات التحميل والتثبيت: توفر أداة APK Analyzer تفكيكاً دقيقاً لمكونات ملف التثبيت عبر ثلاثة أقسام رئيسية: أولاً ملفات classes.dex وعدد الدوال والمكتبات الخارجية المستهلكة للمساحة. ثانياً مجلد الموارد res والوسائط وتأثير الصور النقطية غير المضغوطة. ثالثاً مجلد lib الذي يضم مكتبات C++ المشتركة (.so) مقسمة حسب معمارية المعالجات (armeabi-v7a, arm64-v8a, x86, x86_64). ويحدث التضخم الأكبر عند دمج كافة المعالجات في حزمة APK شاملة مما يضاعف حجم كود النيتف أربع مرات. ولحل ذلك، نعتمد حزم AAB لتوليد حزم ABI مجزأة ترسل لكل مستخدم كود معالجه فقط، مع ضبط ndk.abiFilters في Gradle لحذف المعالجات المهملة كـ x86 من نسخ الإنتاج، وتطبيق ميزانيات حجم برمجية صارمة في الـ CI.",
        "walkthrough_ar": """تحليل الحزمة بأداة apkanalyzer وتصفية المعالجات في Gradle:
```bash
# 1. تحليل مكونات الحزمة عبر سطر الأوامر
apkanalyzer apk summary app-release.apk
```

```kotlin
// 2. build.gradle.kts: استبعاد معالجات x86 وحصر الحزمة على ARM
android {
    defaultConfig {
        ndk {
            // حصر المكتبات المترجمة على معالجات الموبايل الحقيقية فقط
            abiFilters += listOf("armeabi-v7a", "arm64-v8a")
        }
    }
}
```""",
        "why_it_matters_ar": "يرفع معدلات إتمام التثبيت من المتاجر؛ حيث يؤدي كل توفير في الميجابايتات إلى تقليل استهلاك باقة الإنترنت وسرعة التنزيل لدى ملايين المستخدمين.",
        "worked_example_ar": "تطبيق محادثة يضم مكتبة WebRTC بحجم 60 ميجابايت لكافة المعالجات؛ بحصرها عبر AAB واستبعاد معالجات x86 انخفض حجم التنزيل على هواتف المستخدمين إلى 18 ميجابايت فقط.",
        "trade_offs_ar": "استبعاد معالجات x86 يوفر حجماً هائلاً في الإنتاج ولكنه قد يعطل تشغيل التطبيق على بعض المحاكيات القديمة ما لم يتم استخدام محاكيات تدعم معمارية ARM.",
        "failure_modes_ar": "نشر حزمة Universal APK تضم كافة المعالجات واللغات للمستخدمين، أو نسيان ضغط الصور النقطية عالية الدقة مما يضخم مجلد الموارد بلا مبرر.",
        "production_perspective_ar": "في الفرق الكبرى، نضع اختبارات CI تقيس حجم الحزمة آلياً وترفض أي PR يتجاوز الميزانية المحددة بـ 200 كيلوبايت، مع النشر الحصري بصيغة AAB في Google Play.",
        "how_to_answer_ar": "وضح أدوات التحليل كـ APK Analyzer، وفكك الحزمة لأقسامها (DEX, Resources, Lib)، واشرح تضخم المعالجات وكيف تحله حزم AAB وخاصية ndk.abiFilters.",
        "talking_points_ar": "أداة APK Analyzer، تضخم معالجات النيتف في مجلد lib، دور AAB في إرسال ABI المطابق فقط، واستخدام ndk.abiFilters وميزانيات الحجم.",
        "follow_ups_ar": "- **المحاور:** 'لماذا تستهلك مكتبات المعالجات في مجلد lib حجماً هائلاً في حزم الـ APK العادية؟'\n  **المرشح:** 'لأن الحزمة العادية تضطر لتضمين نفس ملفات C++ .so مترجمة أربع مرات: لمعالج arm 32-bit و arm 64-bit و x86 32-bit و x86 64-bit لضمان التوافق مع كافة الأجهزة، مما يضاعف حجم كود النيتف أربع مرات.'\n\n- **المحاور:** 'كيف تحل حزم AAB مشكلة تضخم المعالجات المتعددة؟'\n  **المرشح:** 'يقوم متجر Google Play بإنشاء Split APK مخصص لكل معمارية؛ فعندما يحمل مستخدم يملك هاتفاً بمعالج arm64، يرسل له المتجر حزمة النيتف الخاصة بـ arm64 فقط، دون تنزيل بايت واحد من معالجات x86 أو 32-bit.'",
        "self_check_ar": "هل شرحت أقسام APK Analyzer الثلاثة؟ وهل بينت مشكلة تضخم المعالجات ودور AAB وخاصية abiFilters؟",
        "references_ar": f"- [Android Developers: Analyze your build with APK Analyzer](https://developer.android.com/studio/build/apk-analyzer) — دليل فحص وتحليل الحزم في أندرويد ستوديو.\n- [Reduce your app size](https://developer.android.com/topic/performance/reduce-app-size) — إرشادات جوجل الهندسية لتقليص حجم التطبيقات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يتم تحليل الحجم باستخدام أداة APK Analyzer لفحص استهلاك ملفات DEX والموارد والمكتبات في مجلد lib. ويقضي المهندسون على تضخم المعالجات بنشر حزم AAB لتوليد حزم ABI مجزأة لكل جهاز، وتحديد ndk.abiFilters لإزالة المعالجات القديمة، وتحويل الصور إلى صيغة WebP.",
        "best_answer_ar": """يمثل تحليل حجم التطبيق خطوة محورية لرفع معدلات التحميل وتقليل معدلات التراجع لدى المستخدمين.

نبدأ التحليل بأداة APK Analyzer المدمجة في أندرويد ستوديو أو عبر سطر الأوامر apkanalyzer؛ حيث تفكك الحزمة لعرض حجم ملفات classes.dex وعدد الدوال، وحجم مجلد الموارد res والوسائط، والمكتبات المترجمة في مجلد lib.

ويعد مجلد المكتبات المترجمة lib المصدر الأكبر للتضخم؛ فإذا كان التطبيق يدمج مكتبات C++ لمعالجات armeabi-v7a و arm64-v8a و x86، فإن الحزمة التقليدية تكرر ملفات النيتف أربع مرات لكل معالج.

ولحل ذلك، ننشر التطبيق بصيغة Android App Bundle؛ حيث يتولى متجر جوجل تجزئة الحزمة وإرسال كود المعالج المطابق لهاتف المستخدم فقط، مع ضبط خاصية ndk.abiFilters في Gradle لحذف المعالجات القديمة وتحويل الصور لصيغة WebP المضغوطة.""",
        "deep_answer_ar": """في هندسة تطبيقات الموبايل ذات ملايين المستخدمين، تؤكد أبحاث جوجل أن زيادة حجم التطبيق بمقدار 6 ميجابايت تخفض نسبة اكتمال التثبيت بمقدار 1%؛ ولذا نخضع كل إصدار لتحليل حجم صارم.

نستخدم أداة apkanalyzer في خط الـ CI لتفكيك الحزمة إلى ثلاثة أجزاء رئيسية: ملفات classes.dex ومجلد الموارد ومجلد مكتبات النيتف lib. فإذا لاحظنا تضخم كود DEX، نراجع شجرة الاعتماديات ونفعل R8 لحذف الأكواد الميتة. وفي الموارد، نلزم المطورين بتحويل الصور إلى WebP واستخدام Vector Drawables.

أما في ملفات النيتف C++ مثل مكتبات التشفير أو معالجة الصور، فإن تضمين كافة المعالجات في حزمة APK عادية يضاعف حجم التطبيق ثلاث أو أربع مرات. وللقضاء على هذا الهدر، نعتمد حزم AAB في متجر Google Play لتوليد حزم ABI Splits ترسل كود معالج arm64 فقط للهواتف الحديثة، مما يوفر عشرات الميجابايتات.

كما نضبط ميزانيات حجم برمجية Size Budgets في خطوط الـ CI لرفض أي Pull Request يرفع حجم الحزمة بأكثر من 200 كيلوبايت دون موافقة مسبقة من مهندسي المنصة. ونقوم بأرشفة تقارير تفكيك الحزم دورياً لمقارنة نمو الحجم عبر الإصدارات المتتابعة وتحديد أي مكتبات طرف ثالث تتسبب في تضخم مفاجئ، مما يضمن بقاء التطبيق خفيفاً وسريع التثبيت لكافة المستخدمين."""
    }
}

# ==========================================
# BLD-12: How do you configure signing keys and Play App Signing safely?
# ==========================================
DATA["BLD-12"] = {
    "concept_en": """Configuring release signing keys and Google Play App Signing requires cryptographic isolation and automated secret injection:
- Enterprise Keystore Protection: Keystore files (.jks / .p12) and their corresponding passwords must never be checked into version control. Doing so causes permanent credential exposure. They are stored in secure Secret Managers (AWS Secrets Manager, HashiCorp Vault, GitHub Encrypted Secrets) and injected into CI runner environments ephemerally during build execution.
- Play App Signing Dual-Key Architecture:
  1. Upload Key: Generated and held by the developer/CI system. Used exclusively to sign the AAB uploaded to Google Play.
  2. Master App Signing Key: Generated and retained within Google's tamper-resistant Key Management Service (KMS). Google Play verifies the upload key, strips it, signs the dynamically generated device-specific split APKs with the master app signing key, and distributes them to end users.
- Disaster Recovery & Key Rotation: If a traditional standalone release key is lost or compromised, the application can never be updated again. Under Play App Signing, if the Upload Key is compromised or lost, the developer submits an authenticated key reset request in the Play Console to register a new upload certificate without impacting existing users.""",
    "walkthrough_en": """Configuring secure signing retrieval via environment variables in Gradle:
```kotlin
android {
    signingConfigs {
        create("release") {
            val keystorePath = System.getenv("KEYSTORE_FILE_PATH")
            if (keystorePath != null && file(keystorePath).exists()) {
                storeFile = file(keystorePath)
                storePassword = System.getenv("KEYSTORE_PASSWORD")
                keyAlias = System.getenv("KEY_ALIAS")
                keyPassword = System.getenv("KEY_PASSWORD")
                enableV1Signing = true
                enableV2Signing = true
            }
        }
    }

    buildTypes {
        getByName("release") {
            signingConfig = signingConfigs.findByName("release") ?: signingConfigs.getByName("debug")
        }
    }
}
```""",
    "short_en": """Configuring signing keys safely requires keeping keystores and credentials out of version control, injecting them via CI environment secrets or secure vaults. Under Google Play App Signing, the CI signs bundles with an Upload Key while Google safeguards the master distribution key, enabling safe key rotation if upload credentials are compromised.""",
    "structured_en": """Securing Android release signing requires strict credential hygiene and leveraging Google Play App Signing's two-tier architecture.
First, enforce strict secret isolation. Keystore binaries and passphrases must never be committed to Git. Instead, store the base64-encoded keystore and passwords inside secure secret managers like GitHub Actions Secrets or HashiCorp Vault, injecting them into Gradle builds via environment variables.
Second, adopt Google Play App Signing. Decouple upload authentication from device distribution: developers sign App Bundles with an Upload Key, while Google manages the master App Signing Key inside secure hardware modules to sign user-delivered split APKs.
Third, implement disaster recovery protocols. If an upload key is lost or compromised, administrators request an upload key reset directly in Play Console, preventing the catastrophic loss of user update paths.""",
    "deep_senior_en": """In mobile DevSecOps, managing signing certificates is a mission-critical responsibility; a compromised or lost release key represents an existential threat to an Android application.
Historically, developers managed monolithic private keystores locally.
If the private key was lost, the app became permanently orphaned because Android's PackageManager rejects upgrades signed with mismatched certificates, forcing teams to republish under a new package name and forfeit their entire user base.
To prevent this single point of failure, enterprise architectures mandate Google Play App Signing.
Under this model, we generate an Upload Keystore dedicated solely to authenticating builds dispatched to the Play Store.
During CI execution, Gradle retrieves the keystore binary and credentials from encrypted environment variables populated by our secrets manager.
The CI signs the AAB with this upload certificate and transmits it via the Play Developer Publishing API.
Google Play validates the upload signature, discards it, and re-signs the derived configuration-split APKs using the master App Signing Key stored securely within Google's cloud Key Management Service.
If our CI runner is compromised or an engineer misplaces the upload credentials, we execute an automated key rotation workflow in Google Play Console.
Google revokes the old upload certificate and registers our new upload key without impacting end users or breaking signature continuity on existing devices.""",
    "meta_ar": {
        "id": "BLD-12",
        "questionAr": "كيف تضبط مفاتيح التوقيع الرقمي وخدمة توقيع التطبيقات Play App Signing بأمان في خطوط الإنتاج والـ CI؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تأمين مفاتيح التوقيع الرقمي Keystores، ومنع تسريب الأسرار في Git، ودور المتغيرات البيئية و Key Management Services، ومعمارية Play App Signing بالمفتاح المزدوج (Upload Key vs App Signing Key) وتدوير المفاتيح.",
        "concept_ar": "يتطلب تأمين مفاتيح التوقيع الرقمي وخدمة Google Play App Signing عزلاً مشفراً وحقناً آمناً للأسرار في خطوط الـ CI: يحظر حظراً تاماً إيداع ملفات Keystore أو كلمات السر في مستودعات Git لتفادي تسريب الهوية الرقمية، بل تُحفظ في منصات إدارة الأسرار (مثل Vault أو GitHub Secrets) وتُحقن كمتغيرات بيئية مؤقتة وقت البناء. وتعتمد معمارية Play App Signing على نموذج المفتاح المزدوج: أولاً مفتاح الرفع (Upload Key) ويحتفظ به المطور أو خادم الـ CI لتوقيع حزمة الـ AAB المرفوعة للمتجر. ثانياً مفتاح توقيع التطبيق الرئيسي (App Signing Key) وتديره جوجل داخل بنيتها التحتية المشفرة وخوادم KMS العتادية؛ حيث تفحص جوجل مفتاح الرفع وتستبدله بالمفتاح الرئيسي لتوقيع حزم Split APKs الموزعة للهواتف. وتكمن الميزة الكبرى في التعافي من الكوارث؛ فإذا تسرب مفتاح الرفع أو فُقد، يمكن للمطور تقديم طلب إعادة ضبط المفتاح عبر Play Console واستخراج مفتاح رفع جديد دون انقطاع التحديثات عن ملايين المستخدمين القائمين.",
        "walkthrough_ar": """حقن مفاتيح التوقيع عبر متغيرات بيئة الـ CI في Gradle:
```kotlin
android {
    signingConfigs {
        create("release") {
            val keyPath = System.getenv("KEYSTORE_PATH")
            if (keyPath != null && file(keyPath).exists()) {
                storeFile = file(keyPath)
                storePassword = System.getenv("KEYSTORE_PASS")
                keyAlias = System.getenv("KEY_ALIAS")
                keyPassword = System.getenv("KEY_PASS")
                enableV1Signing = true
                enableV2Signing = true
            }
        }
    }
}
```""",
        "why_it_matters_ar": "يمنع سرقة مفاتيح التطبيق وتزوير التحديثات، ويحمي استمرارية المشروع من الانهيار التام في حال فقدان مفتاح التوقيع.",
        "worked_example_ar": "تسريب مفتاح الرفع في خادم CI قديم؛ بفضل Play App Signing تم طلب تدوير مفتاح الرفع في Play Console وتسجيل مفتاح جديد دون أي تأثير على ملايين المستخدمين.",
        "trade_offs_ar": "تأمين المفاتيح في منصات Vault يتطلب إعداداً إضافياً لخط الـ CI ولكنه يوفر حماية مؤسسية مطلقة تمنع الكوارث الأمنية.",
        "failure_modes_ar": "رفع ملف release.jks وكلمات السر داخل مستودع Git العام، أو الاعتماد على مفتاح محلي دون Play App Signing وفقدانه للأبد.",
        "production_perspective_ar": "في المشروعات الكبرى، نشفر ملف Keystore بصيغة Base64 في مخزن الأسرار، ونفرغ الملف مؤقتاً في مسار الـ Runner أثناء البناء ثم نحذفه فور اكتمال التوقيع.",
        "how_to_answer_ar": "ابدأ بقاعدة عزل الأسرار عن Git، ثم اشرح نموذج المفتاح المزدوج في Play App Signing (مفتاح الرفع ومفتاح التطبيق)، واختم بمزايا التعافي من الكوارث وتدوير المفتاح.",
        "talking_points_ar": "حظر حفظ المفاتيح في Git، معمارية المفتاح المزدوج في Play App Signing، دور خوادم KMS في جوجل، وإجراءات تدوير مفتاح الرفع.",
        "follow_ups_ar": "- **المحاور:** 'كيف يتم حقن ملف Keystore الثنائي داخل خوادم GitHub Actions دون حفظه في المستودع؟'\n  **المرشح:** 'نقوم بترميز ملف الـ Keystore إلى نص Base64 وتخزينه كـ Secret مشفر في إعدادات GitHub Actions؛ وفي خط البناء، يقوم سكريبت الـ CI بفك ترميز النص وإعادة تكوين ملف الـ jks مؤقتاً في مسار آمن على القرص، ثم مسحه فور اكتمال عملية التوقيع.'\n\n- **المحاور:** 'ماذا تفعل إذا اكتشفت أن مفتاح الرفع Upload Key قد تم تسريبه علناً؟'\n  **المرشح:** 'نقوم فوراً بالدخول إلى لوحة Google Play Console وطلب إعادة ضبط مفتاح الرفع Upload Key Reset، وتوليد مفتاح جديد محلياً وتصدير شهادته العامة لجوجل لاعتمادها، مما يبطل المفتاح المسرب فوراً دون المساس بالمستخدمين الحاليين.'",
        "self_check_ar": "هل شرحت نموذج المفتاح المزدوج؟ وهل بينت كيفية عزل الأسرار عن Git ومزايا Play App Signing في تدوير المفاتيح؟",
        "references_ar": f"- [Android Developers: Sign your app](https://developer.android.com/build/app-signing) — الدليل الشامل لتأمين التوقيع الرقمي.\n- [Google Play Console: Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756) — التوثيق الرسمي لمعمارية المفتاح المزدوج وتدوير المفاتيح.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يتطلب الضبط الآمن حظر حفظ ملفات Keystore وكلمات السر في Git وحقنها كأسرار مشفرة في خوادم الـ CI. ونعتمد على خدمة Play App Signing حيث نوقع الحزمة بمفتاح رفع Upload Key، بينما تحمي جوجل مفتاح التوقيع الرئيسي في خوادمها الآمنة مع إمكانية تدوير المفاتيح عند الطوارئ.",
        "best_answer_ar": """تعتمد إدارة مفاتيح التوقيع الرقمي الآمنة على العزل التام للأسرار وتفعيل خدمة Google Play App Signing لضمان استمرارية التحديثات.

أولاً، نمنع نهائياً حفظ ملفات الـ Keystore أو كلمات السر في كود Git؛ بل يتم تشفير ملف المفتاح وحفظه مع كلمات السر داخل منصات إدارة الأسرار مثل GitHub Secrets أو Vault، ليتم فك تشفيرها وحقنها كمتغيرات بيئية مؤقتة أثناء تشغيل خط الـ CI فقط.

ثانياً، نطبق معمارية المفتاح المزدوج عبر Play App Signing؛ حيث يوقع خط البناء حزمة AAB بمفتاح رفع Upload Key، بينما تتولى خوادم جوجل تأمين مفتاح التوقيع الفعلي وتوقيع الحزم النهائية للمستخدمين.

ثالثاً، يوفر هذا النموذج حماية مطلقة ضد الكوارث؛ فإذا فُقد مفتاح الرفع أو تسرب، يمكن للمطور استبداله بمفتاح رفع جديد عبر لوحة تحكم المتجر دون أن يفقد ملايين المستخدمين القدرة على تحديث التطبيق.""",
        "deep_answer_ar": """في أمان خطوط الإنتاج والـ DevSecOps لتطبيقات أندرويد، يعتبر مفتاح التوقيع الرقمي هوية التطبيق القانونية والمشفرة التي لا يمكن التهاون في حمايتها.

في السابق، كانت إدارة المفاتيح محلياً تمثل نقطة فشل وحيدة وقاتلة Single Point of Failure؛ فإذا فُقد المفتاح أو غادر المطور الشركة ومعه كلمة السر، يصبح من المستحيل إصدار أي تحديث للتطبيق لأن نظام أندرويد يرفض أي توقيع مختلف، مما يجبر الشركة على نشر تطبيق جديد وفقدان كافة المستخدمين.

وللقضاء على هذا الخطر، نلزم كافة المشروعات بالانضمام لخدمة Google Play App Signing. في هذه المعمارية، نقوم بإنشاء Upload Key نخصصه حصرياً لخوادم الـ CI لتوقيع حزم AAB؛ وتُحقن بياناته عبر أسرار مشفرة في بيئة البناء وتُمسح فور اكتمال المهمة. وعند وصول الحزمة لجوجل، تفحص مفتاح الرفع ثم تستبدله بمفتاح التوقيع الرئيسي المحفوظ داخل خوادم الأمان العتادية KMS التابعة لجوجل.

والميزة الاستراتيجية الكبرى هي مرونة التعافي؛ فإذا تسرب مفتاح الرفع، نقوم بتقديم طلب فوري عبر Play Console لإلغاء المفتاح القديم وتسجيل مفتاح رفع جديد خلال دقائق، دون أن يشعر المستخدمون بأي انقطاع، مما يحقق أعلى معايير الحوكمة والأمان المؤسسي. كما نلزم الفرق بتوثيق صلاحيات الوصول للمفاتيح والتدقيق الدوري على حسابات المطورين في Google Play Console لضمان أعلى معايير الحوكمة المؤسسية."""
    }
}

# ==========================================
# BLD-13: How do you manage versionCode/versionName and release notes?
# ==========================================
DATA["BLD-13"] = {
    "concept_en": """Managing Android version identifiers and release notes requires separating OS-enforced monotonic integers from user-facing semantic strings and automating metadata delivery:
- versionCode (Operating System Contract): A strictly positive integer evaluated by Android's PackageManager and Google Play. It must be strictly monotonically increasing with every published artifact. Android prevents app downgrades: an installed application cannot be overwritten by an APK possessing an equal or lower versionCode. The maximum allowable value is 2,100,000,000.
- versionName (User & Marketing Interface): A human-readable string displayed to users in device settings and app stores (e.g., 2.4.0 or 3.1.2-beta01). It typically adheres to Semantic Versioning (MAJOR.MINOR.PATCH) but has zero mechanical influence over the operating system's installation lifecycle.
- Automated Version Calculation in CI/CD:
  * Monotonic CI counters: Using GitHub Actions ${{ github.run_number }} or total Git commit count (git rev-list --count HEAD) ensures deterministic, clash-free versionCode generation.
  * Flavor/ABI Encoding: Bit-shifting or multiplying versionCode for ABI splits so 64-bit APKs always hold a higher versionCode than 32-bit APKs.
- Automated Release Notes Delivery: Managing localized whatsnew files under distribution/whatsnew/ (e.g. whatsnew-en-US, whatsnew-ar) integrated with deployment tools like Fastlane (supply) or Gradle Play Publisher (GPP) to sync release changelogs directly to Google Play tracks automatically upon merge.""",
    "walkthrough_en": """Automated version generation and Fastlane release notes synchronization:
```kotlin
// build.gradle.kts: Automated monotonic versionCode from git commit depth
fun computeVersionCode(): Int {
    return runCatching {
        val process = ProcessBuilder("git", "rev-list", "--count", "HEAD").start()
        process.inputStream.bufferedReader().readText().trim().toInt()
    }.getOrDefault(100)
}

val semanticVersionName = "2.4.0"

android {
    defaultConfig {
        versionCode = computeVersionCode()
        versionName = semanticVersionName
    }
}

// Localized release notes directory structure for Fastlane supply:
// fastlane/metadata/android/en-US/changelogs/1042.txt
// fastlane/metadata/android/ar/changelogs/1042.txt
```""",
    "short_en": """versionCode is an OS-enforced monotonic integer preventing downgrades, automated in CI via Git commit counts or build numbers. versionName is a semantic string for user display. Localized release notes reside in structured project directories, synced directly to Google Play tracks using Fastlane or Gradle Play Publisher.""",
    "structured_en": """Managing application versioning and release notes requires separating operational operating-system contracts from user-facing metadata in automated deployment pipelines.
First, versionCode is a strictly positive, monotonically increasing integer evaluated by Android's package manager and Google Play. Android strictly rejects package installations if the incoming versionCode is equal to or lower than the currently installed build.
Second, versionName is an arbitrary display string shown in app store listings and system settings, traditionally formatted according to Semantic Versioning (MAJOR.MINOR.PATCH).
Third, automate versionCode generation within CI/CD using deterministic sources, such as git rev-list --count HEAD or CI run numbers, eliminating manual increment errors.
Fourth, structure localized release notes inside standard directories (such as src/main/play/release-notes/), deploying them automatically to Google Play release tracks via Fastlane supply or Gradle Play Publisher.""",
    "deep_senior_en": """In professional mobile release engineering, treating version numbers and release notes as manual edits in build.gradle.kts is an anti-pattern that leads to merge conflicts, duplicate build errors, and broken deployment pipelines.
The Android operating system establishes an unyielding technical contract through versionCode.
PackageManager compares the integer value of an incoming package against the installed binary: if the incoming versionCode is not strictly higher, the update fails immediately with INSTALL_FAILED_VERSION_DOWNGRADE.
Furthermore, Google Play Console rejects any bundle whose versionCode has already been uploaded to any release track.
Conversely, versionName is purely informative metadata formatted to communicate feature milestones to end users via Semantic Versioning.
To eliminate human error across distributed engineering teams, we automate version calculation in CI/CD.
In our Gradle configuration, versionCode derives deterministically from the total commit depth on the release branch using git rev-list --count HEAD or from the monotonic pipeline run number ${{ github.run_number }}.
When deploying multi-ABI APK splits, we multiply the base semantic version and add an architecture offset, guaranteeing that 64-bit packages hold a higher versionCode than 32-bit alternatives so Google Play installs the optimal binary.
For release notes, we maintain localized markdown files under src/main/play/release-notes/ corresponding to BCP-47 language codes.
Our deployment pipeline integrates Fastlane or Gradle Play Publisher to push the compiled AAB, mapping file, and localized release changelogs to internal, beta, and production tracks in a single atomic pipeline run.""",
    "meta_ar": {
        "id": "BLD-13",
        "questionAr": "كيف تدير وتؤتمت ترقيم الإصدارات (versionCode و versionName) وملفات الملاحظات (Release Notes) في خطوط الـ CI/CD؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم الفارق التقني بين versionCode و versionName، وتجنب أخطاء تراجع الإصدارات، وأتمتة الترقيم عبر Git commits أو CI build numbers، وإدارة ملاحظات الإصدار متعددة اللغات بـ Fastlane أو Gradle Play Publisher.",
        "concept_ar": "تتطلب إدارة ترقيم الإصدارات وملاحظات النشر فصلاً دقيقاً بين المعايير التقنية لنظام التشغيل والواجهات التسويقية للمستخدم: يمثل versionCode رقماً صحيحاً تصاعدياً إجبارياً يتعامل معه نظام أندرويد ومتجر جوجل؛ ويشترط أن يزداد مع كل إصدار جديد لمنع أخطاء التراجع (Downgrade Prevention)، حيث يرفض النظام تثبيت أي حزمة تحمل رقماً مساوياً أو أقل من المثبت بالهاتف. بينما يمثل versionName نصاً وصفياً يظهر للمستخدم في المتجر وإعدادات الهاتف (مثل 2.4.1) ويتبع عادة قواعد الترقيم الدلالي Semantic Versioning دون أي تأثير على قبول النظام للتثبيت. وفي خطوط الـ CI/CD، تتم أتمتة حساب versionCode باستخدام عدد الـ Commits في Git أو رقم تشغيل الـ CI لضمان تفرد الأرقام. وتدار ملاحظات الإصدار (Release Notes) عبر ملفات نصية مجزأة حسب اللغات داخل المشروع مثل whatsnew-ar و whatsnew-en-US، وترفع تلقائياً للمتجر باستخدام أدوات الأتمتة كـ Fastlane أو Gradle Play Publisher.",
        "walkthrough_ar": """أتمتة حساب versionCode في Gradle وتنظيم مجلدات Fastlane:
```kotlin
// build.gradle.kts: حساب رقم الإصدار تصاعدياً عبر عدد commits
fun getCommitCount(): Int = runCatching {
    ProcessBuilder("git", "rev-list", "--count", "HEAD")
        .start().inputStream.bufferedReader().readText().trim().toInt()
}.getOrDefault(1)

android {
    defaultConfig {
        versionCode = getCommitCount() // رقم تصاعدي تلقائي
        versionName = "2.4.0"          // اسم تسويقي دلالي
    }
}
// مجلد ملاحظات الإصدار لـ Fastlane:
// fastlane/metadata/android/ar/changelogs/default.txt
```""",
        "why_it_matters_ar": "يمنع تعطل خطوط الإنتاج بسبب تكرار أرقام الإصدارات أو نسيان زيادتها يدوياً، ويضمن تحديث ملاحظات المتاجر بكافة اللغات بسلاسة مع كل إطلاق.",
        "worked_example_ar": "فريق يضم 20 مطوراً؛ بدلاً من تعديل versionCode يدوياً وحدوث تعارضات Git، يولد الـ CI رقماً تصاعدياً آلياً من Git ويرفع الملاحظات المترجمة لـ Google Play بنجاح.",
        "trade_offs_ar": "الاعتماد على عدد commits يوفر أتمتة ممتازة ولكنه يتطلب الانتباه عند دمج الفروع أو إعادة ترتيب التاريخ البرمجي Rebase للحفاظ على تصاعدية الرقم.",
        "failure_modes_ar": "محاولة رفع حزمة لـ Google Play بنفس رقم versionCode السابق مما يرفضه المتجر فوراً، أو كتابة رقم أقل فيرفض هاتف المستخدم تثبيت التحديث.",
        "production_perspective_ar": "في المشروعات الكبرى، نعتمد على رقم البناء في GitHub Actions كمصدر للـ versionCode، ونستخدم أداة Fastlane supply لنشر التحديث والملاحظات للمسار الداخلي تلقائياً.",
        "how_to_answer_ar": "فرق بين الدور التقني لـ versionCode (رقم صحيح تصاعدي للنظام) و versionName (نص للمستخدم)، واشرح كيفية الأتمتة في CI وإدارة الملاحظات المترجمة بأدوات النشر.",
        "talking_points_ar": "مبدأ منع التراجع Downgrade Prevention، أتمتة versionCode من Git أو CI، ترقيم SemVer، وأدوات Fastlane و GPP للملاحظات.",
        "follow_ups_ar": "- **المحاور:** 'ماذا يحدث إذا حاولت تثبيت APK يحمل versionCode مساوياً أو أقل من المثبت على الجهاز؟'\n  **المرشح:** 'يرفض مدير الحزم PackageManager التثبيت فوراً بخطأ INSTALL_FAILED_VERSION_DOWNGRADE؛ لأن أندرويد يحظر التراجع البرمجي لحماية بيانات المستخدم من الاستغلال الأمني بالعودة لنسخ قديمة غير آمنة.'\n\n- **المحاور:** 'كيف يتم التعامل مع versionCode عند بناء نسخ مجزأة للمعالجات Split APKs؟'\n  **المرشح:** 'نضيف رقماً إضافياً كبادئة أو لاحقة للـ versionCode (مثلاً إضافة 2 لمعالجات arm64 وإضافة 1 لمعالجات armeabi-v7a)، لضمان أن تكون نسخة الـ 64-bit دائماً ذات versionCode أعلى فيقوم متجر جوجل بتثبيتها تلقائياً على الهواتف الحديثة.'",
        "self_check_ar": "هل وضحت الفارق الجوهري بين versionCode و versionName؟ وهل بينت كيفية الأتمتة وإدارة ملاحظات الإصدار بأدوات Fastlane؟",
        "references_ar": f"- [Android Developers: Version your app](https://developer.android.com/studio/publish/versioning) — التوثيق الرسمي لقواعد ترقيم تطبيقات أندرويد.\n- [Fastlane Supply Documentation](https://docs.fastlane.tools/actions/supply/) — دليل أتمتة رفع الملاحظات والحزم لمتجر Google Play.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يمثل versionCode رقماً صحيحاً تصاعدياً إجبارياً لنظام التشغيل يمنع التراجع ويؤتمت بحساب عدد commits في Git، بينما يمثل versionName نصاً دلالياً لعرض الإصدار للمستخدم. وتدار ملاحظات الإصدار بملفات مترجمة في المشروع وترفع للمتجر آلياً عبر Fastlane أو Gradle Play Publisher.",
        "best_answer_ar": """تعتمد إدارة الإصدارات الاحترافية على الفصل التام بين المتطلبات التقنية لنظام أندرويد والمعلومات المعروضة للمستخدم، مع أتمتة النشر عبر خط الـ CI/CD.

يمثل versionCode رقماً صحيحاً تصاعدياً لا يتكرر تفرضه أداة PackageManager في أندرويد؛ حيث يمنع النظام تثبيت أي حزمة تحمل رقماً مساوياً أو أقل لحماية المستخدم من تثبيت إصدارات قديمة تحتوي على ثغرات أمنية.

بينما يمثل versionName نصاً تسويقياً يتبع قواعد الترقيم الدلالي مثل 2.4.0 لإعلام المستخدم بطبيعة الميزات الجديدة دون أي تأثير تشغيلي على التثبيت.

وفي بيئات الإنتاج، نؤتمت توليد versionCode عبر قراءة عدد الـ Commits في Git لضمان التفرد التام، وندير ملاحظات الإصدار عبر ملفات نصية مخصصة لكل لغة وترفع تلقائياً لمتجر Google Play عبر Fastlane أو Gradle Play Publisher فور اعتماد الإصدار.""",
        "deep_answer_ar": """في هندسة الإصدارات المؤتمتة، يعتبر تعديل أرقام الإصدارات وكتابة الملاحظات يدوياً داخل ملفات gradle ممارسة بدائية تسبب تعارضات الفروع وتوقف خطوط الـ CI.

يفرض نظام أندرويد شرطاً تقنياً صارماً عبر versionCode؛ فهو رقم صحيح تصاعدي يجب أن يزيد في كل بناء جديد، وإذا حاول المستخدم تثبيت حزمة برقم مساوٍ أو أقل يرفض النظام التثبيت بخطأ INSTALL_FAILED_VERSION_DOWNGRADE لمنع التراجع، كما يرفض متجر جوجل رفع أي حزمة مكررة الرقم. في المقابل، يعتبر versionName نصاً حراً للمستخدمين يتبع معايير SemVer للتعبير عن الإضافات وإصلاحات الأخطاء.

وللقضاء على الأخطاء البشرية، نربط حساب versionCode آلياً بعدد الـ Commits في Git عبر أمر git rev-list --count HEAD أو رقم مهمة الـ CI؛ مما يضمن توليد رقم تصاعدي فريد ومستمر في كل عملية دمج.

وعند إصدار حزم مقسمة للمعالجات، نضيف إزاحة رقمية Offset لمعالج arm64 لضمان حصوله على versionCode أعلى من معالج 32-bit. ونكمل المنظومة بحفظ ملاحظات الإصدار بملفات مجزأة حسب اللغات كـ whatsnew-ar و whatsnew-en-US وترفع تلقائياً عبر Fastlane supply أو Gradle Play Publisher لربط الكود والملاحظات في عملية نشر واحدة متكاملة. كما نربط إشعارات التحديث بخطوط الـ Slack لإعلام الفريق الهندسي وفريق المنتجات فور اعتماد الإصدار ونشر الملاحظات في المتجر، مما يضمن تناسق العمل وتكامل خطط التسويق والدعم."""
    }
}

# ==========================================
# BLD-14: How do you diagnose missing native libraries or ABI incompatibility?
# ==========================================
DATA["BLD-14"] = {
    "concept_en": """Diagnosing native library crashes and ABI incompatibilities requires understanding how Android's dynamic linker and 64-bit zygote process resolve native binaries:
- The Error Signature: java.lang.UnsatisfiedLinkError: dlopen failed: library "libcustom.so" not found or has text relocations or 32-bit instead of 64-bit.
- The Partial ABI Coverage Trap: The most insidious native packaging bug occurs when third-party libraries supply mismatched ABI sets. If Library A supplies arm64-v8a and armeabi-v7a, but Library B supplies only armeabi-v7a, Android's OS loader sees that the APK contains an arm64-v8a directory. Consequently, on modern 64-bit hardware, the OS launches the application inside a 64-bit Zygote process and configures the native library search path to point exclusively to the app's 64-bit native lib directory. When code attempts to load Library B via System.loadLibrary(), the linker cannot locate a 64-bit .so, throwing an immediate UnsatisfiedLinkError at runtime!
- Diagnostic Protocol:
  1. Inspect APK composition with APK Analyzer: Open the lib/ directory and ensure that every single .so file present in armeabi-v7a also exists in arm64-v8a.
  2. Inspect binary dependencies with readelf -d libcustom.so: Examine the NEEDED dynamic section to verify all required runtime dependencies (such as libc++_shared.so) are bundled.
  3. Enforce ABI Symmetry via ndk.abiFilters: Configure Gradle to prune unsupported ABIs or restrict packaging to uniform targets.""",
    "walkthrough_en": """Inspecting dynamic linkage with readelf and enforcing uniform ABI filters in Gradle:
```bash
# 1. Inspect dynamic shared library requirements via readelf
aarch64-linux-android-readelf -d libcustom.so | grep NEEDED
# Example output: (NEEDED) Shared library: [libc++_shared.so]
```

```kotlin
// 2. build.gradle.kts: Enforcing uniform ABI coverage
android {
    defaultConfig {
        ndk {
            // Strictly enforce symmetric dual-ARM architecture support
            abiFilters += listOf("armeabi-v7a", "arm64-v8a")
        }
    }

    packaging {
        jniLibs {
            // Ensure first copy of shared C++ STL is selected
            pickFirsts += listOf("**/libc++_shared.so")
        }
    }
}
```""",
    "short_en": """Diagnosing native UnsatisfiedLinkError crashes requires resolving partial ABI coverage where libraries provide mismatched architectures, causing 64-bit devices to fail when loading 32-bit binaries. Engineers use APK Analyzer to verify symmetric lib folders, inspect shared dependencies with readelf, and enforce consistent architectures using ndk.abiFilters.""",
    "structured_en": """Diagnosing UnsatisfiedLinkError exceptions and native ABI mismatches requires understanding Android's dynamic linker and process architecture.
First, identify the root cause. The most frequent failure is partial ABI coverage: if one dependency provides an arm64-v8a binary while another provides only armeabi-v7a, a 64-bit device launches a 64-bit Zygote process and searches solely within 64-bit directories, failing to load the 32-bit library.
Second, inspect binary packaging with APK Analyzer. Verify that every .so file in armeabi-v7a has an identical 64-bit counterpart inside arm64-v8a.
Third, inspect dynamic linkage using readelf -d on the compiled library to identify missing dependencies like libc++_shared.so.
Fourth, enforce uniform ABI packaging in build.gradle.kts using ndk.abiFilters, ensuring all bundled libraries support the declared target architectures.""",
    "deep_senior_en": """In Android platform engineering, native C++ runtime crashes—typically manifesting as java.lang.UnsatisfiedLinkError: dlopen failed—are among the most catastrophic defects because they bypass standard Java exception handlers and crash the process immediately.
The classic trap in native packaging is the Partial ABI Coverage phenomenon.
Modern Android devices run a 64-bit kernel and launch applications using a 64-bit Zygote process whenever possible.
When the Android package manager installs an APK, it inspects the lib/ directory.
If it discovers an arm64-v8a folder, it marks the application as 64-bit capable and restricts the native linker (dlopen) to searching the 64-bit library directory.
If a legacy third-party dependency only ships a 32-bit armeabi-v7a binary without an arm64-v8a slice, the app runs fine on old 32-bit hardware but crashes instantly on modern devices the moment System.loadLibrary() executes, because the 64-bit loader refuses to load 32-bit binaries.
To diagnose this, our platform triage workflow opens the APK inside APK Analyzer.
We verify symmetry across architecture folders: every .so file in armeabi-v7a must have an exact equivalent in arm64-v8a.
Next, we run readelf -d on the failing binary to inspect its NEEDED header tags, identifying unbundled shared dependencies such as libc++_shared.so.
Finally, in build.gradle.kts, we enforce strict ndk.abiFilters to eliminate incomplete architectures or declare pickFirsts in packaging.jniLibs to resolve duplicate shared library clashes.""",
    "meta_ar": {
        "id": "BLD-14",
        "questionAr": "كيف تشخص وتعالج أخطاء غياب مكتبات C++ النيتف أو عدم توافق المعالجات (UnsatisfiedLinkError و ABI Incompatibility)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تشخيص أخطاء UnsatisfiedLinkError و dlopen failed، وفهم ظاهرة التغطية الجزئية للمعالجات Partial ABI Coverage واختيار Zygote، واستخدام readelf و APK Analyzer و ndk.abiFilters.",
        "concept_ar": "يتطلب تشخيص أعطال مكتبات C++ وعدم توافق المعالجات فهماً دقيقاً لآلية عمل الرابط الديناميكي Dynamic Linker ومعالج الـ Zygote في أندرويد: يظهر الخطأ عادة كـ UnsatisfiedLinkError: dlopen failed بسبب غياب ملف المكتبة أو عدم تطابق المعمارية. ويكمن الفخ الأكثر شيوعاً في التغطية الجزئية للمعالجات (Partial ABI Coverage)؛ فعندما تحتوي المكتبة (أ) على ملفات لمعالجي arm64 و armeabi-v7a، بينما تحتوي المكتبة (ب) على ملف لمعالج 32-bit فقط، يرى نظام أندرويد وجود مجلد arm64-v8a في الحزمة، فيقوم على الهواتف الحديثة بتشغيل التطبيق في بيئة 64-bit Zygote ويحصر مسار البحث في مجلد الـ 64-bit فقط. وعند محاولة تحميل المكتبة (ب)، يفشل النظام في العثور على نسخة 64-bit وينهار التطبيق فوراً. ولتشخيص ذلك، نتبع مساراً منهجياً: أولاً فحص تماثل مجلدات lib/ عبر APK Analyzer للتأكد من وجود كافة ملفات .so في كافة المعالجات بالتساوي. ثانياً فحص اعتماديات المكتبة بأداة readelf -d للتأكد من وجود مكتبات النظام مثل libc++_shared.so. وثالثاً ضبط ndk.abiFilters في Gradle لحظر المعالجات غير المتماثلة وضمان استقرار التشغيل.",
        "walkthrough_ar": """فحص اعتماديات المكتبة بـ readelf وتوحيد المعالجات في Gradle:
```bash
# 1. فحص المكتبات المشتركة المطلوبة بواسطة readelf
readelf -d libnative.so | grep NEEDED
```

```kotlin
// 2. build.gradle.kts: توحيد المعالجات المدعومة وحل التعارضات
android {
    defaultConfig {
        ndk {
            // ضمان وجود معالجات متماثلة فقط
            abiFilters += listOf("armeabi-v7a", "arm64-v8a")
        }
    }
    packaging.jniLibs {
        pickFirsts += listOf("**/libc++_shared.so")
    }
}
```""",
        "why_it_matters_ar": "يمنع كراش التطبيق الفوري والمفاجئ عند استدعاء مكتبات C++ على أجهزة المستخدمين الحديثة العاملة بمعالجات 64-bit.",
        "worked_example_ar": "دمج مكتبة مسح ضوئي قديمة تدعم 32-bit فقط مع مكتبة أمان تدعم 64-bit؛ انهار التطبيق على Pixel 8 فوراً بخطأ UnsatisfiedLinkError، وحُل باستبعاد arm64 مؤقتاً أو ترقية المكتبة.",
        "trade_offs_ar": "حصر التطبيق على معمارية 32-bit يحل التعارض مؤقتاً ولكنه يخالف متطلبات متجر Google Play الإلزامية لدعم معالجات 64-bit، ولذا يجب توفير نسخ 64-bit لكافة المكتبات.",
        "failure_modes_ar": "استخدام مكتبات نيتف ذات تغطية غير متماثلة للمعالجات، أو نسيان حزم مكتبة C++ STL المشتركة libc++_shared.so في الـ APK.",
        "production_perspective_ar": "في المشروعات الكبرى، نلزم خطوط الـ CI بفحص ملفات الـ DEX و lib عبر APK Analyzer والتأكد التام من تطابق ملفات .so في كافة المعالجات المعتمدة.",
        "how_to_answer_ar": "اشرح الفخ الأكبر: التغطية الجزئية للمعالجات Partial ABI واختيار 64-bit Zygote، ثم بين خطوات التشخيص بـ APK Analyzer وأداة readelf -d والحل عبر ndk.abiFilters.",
        "talking_points_ar": "ظاهرة Partial ABI Coverage، آلية اختيار Zygote في أندرويد، فحص Dynamic Linker بـ readelf، ومتطلبات 64-bit في Google Play.",
        "follow_ups_ar": "- **المحاور:** 'لماذا يعمل التطبيق بشكل طبيعي على هاتف قديم وينهار بـ UnsatisfiedLinkError على هاتف حديث لنفس الحزمة؟'\n  **المرشح:** 'لأن الهاتف القديم يعمل بمعالج 32-bit فيبحث حصرياً داخل مجلد armeabi-v7a حيث توجد كافة المكتبات؛ بينما يملك الهاتف الحديث معالج 64-bit فيشغل Zygote بنمط 64-bit ويبحث حصرياً في arm64-v8a، فإذا كانت إحدى المكتبات تفتقد لملف 64-bit تفشل عملية dlopen فوراً.'\n\n- **المحاور:** 'ماذا تفعل إذا أبلغت أداة readelf أن المكتبة تحتاج إلى libc++_shared.so غير موجودة؟'\n  **المرشح:** 'نقوم بتعديل إعدادات CMake أو NDK لربط مكتبة C++ STL كـ static (c++_static)، أو التأكد من استخراج ملف libc++_shared.so داخل مجلد lib/ لكل معمارية وتضمينه صراحة عبر packaging.jniLibs.'",
        "self_check_ar": "هل شرحت فخ Partial ABI Coverage واختيار Zygote؟ وهل بينت كيفية استخدام APK Analyzer و readelf وضبط ndk.abiFilters؟",
        "references_ar": f"- [Android NDK: Common Problems with Native Libraries](https://developer.android.com/ndk/guides/common-problems) — دليل جوجل لحل أخطاء UnsatisfiedLinkError.\n- [64-bit Requirement on Google Play](https://developer.android.com/distribute/best-practices/develop/64-bit) — التوثيق الإلزامي لدعم معالجات 64-bit في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يتطلب تشخيص خطأ UnsatisfiedLinkError حل مشكلة التغطية الجزئية للمعالجات؛ حيث يؤدي غياب نسخة 64-bit لمكتبة معينة إلى انهيار التطبيق على الهواتف الحديثة. ويفحص المهندسون تماثل مجلدات lib بـ APK Analyzer واعتماديات الـ C++ بـ readelf وضبط ndk.abiFilters في Gradle.",
        "best_answer_ar": """يحدث خطأ UnsatisfiedLinkError وانهيار مكتبات C++ نتيجة عدم توافق المعماريات أو فقدان ملفات الربط الديناميكي داخل نظام أندرويد.

السبب الأكثر شيوعاً هو التغطية الجزئية للمعالجات Partial ABI Coverage؛ فعندما توفر إحدى المكتبات ملفات لمعالج arm64 بينما توفر مكتبة أخرى ملفات لمعالج 32-bit فقط، يقوم هاتف أندرويد الحديث بتشغيل التطبيق في وضع 64-bit Zygote ويحصر مسار البحث في مجلد الـ 64-bit، فيفشل في العثور على المكتبة الأخرى وينهار فوراً.

ولتشخيص ذلك، نفتح الحزمة بأداة APK Analyzer للتأكد من التماثل الكامل بين مجلدات lib/armeabi-v7a و lib/arm64-v8a وتطابق ملفات .so بداخلها.

ثم نستخدم أمر readelf -d لفحص المكتبات المشتركة المطلوبة مثل libc++_shared.so، ونضبط خاصية ndk.abiFilters وخيارات packaging.jniLibs في ملف build.gradle.kts لضمان استقرار تحميل كافة المكتبات.""",
        "deep_answer_ar": """في هندسة منصات أندرويد المتقدمة، تمثل أخطاء النيتف UnsatisfiedLinkError أخطر أنواع الانهيارات لأنها تحدث على مستوى الربط الثنائي المباشر وتسقط التطبيق فورياً دون المرور عبر معالجات الأخطاء العادية.

الفخ الهندسي الأكبر هو ظاهرة التغطية الجزئية للمعالجات Partial ABI؛ فالهواتف الحديثة تعمل بمعالجات 64-bit وتشغل التطبيقات عبر 64-bit Zygote. فعند تثبيت التطبيق، إذا وجد النظام مجلد arm64-v8a، يصنف التطبيق كـ 64-bit ويمنع محرك dlopen من البحث في مجلدات الـ 32-bit نهائياً. فإذا كانت هناك مكتبة طرف ثالث قديمة لا تملك نسخة 64-bit، سيعمل التطبيق بشكل طبيعي على الهواتف القديمة، ولكنه سينهار فوراً على كافة الهواتف الحديثة بمجرد استدعاء System.loadLibrary.

ولحل هذه المشكلة، نفتح الحزمة في APK Analyzer ونتحقق من وجود تماثل تام بين مجلدات المعالجات بحيث يحتوي كل مجلد على نفس ملفات .so تماماً دون أي نقص.

ثم نستخدم أداة readelf -d لفحص ترويسات المكتبة والتأكد من تضمين المكتبات التابعة مثل libc++_shared.so، ونلزم إعدادات Gradle بضبط ndk.abiFilters لتوحيد المعالجات المدعومة وحل أي تعارض في مكتبات C++ المشتركة. كما نلزم خطوط الـ CI بتشغيل اختبارات الأجهزة السحابية عبر Firebase Test Lab لاختبار التطبيق على أجهزة بمعالجات 32-bit و 64-bit للتأكد التام من استقرار تحميل المكتبات قبل النشر."""
    }
}

# ==========================================
# Runner & Word Count Validation
# ==========================================
def validate_words():
    for qid, d in sorted(DATA.items()):
        short_w = len(d["short_en"].split())
        struct_w = len(d["structured_en"].split())
        deep_w = len(d["deep_senior_en"].split())
        assert 35 <= short_w <= 110, f"{qid} short_en {short_w} out of [35, 110]"
        assert 100 <= struct_w <= 280, f"{qid} struct_en {struct_w} out of [100, 280]"
        assert 200 <= deep_w <= 650, f"{qid} deep_en {deep_w} out of [200, 650]"

        q_ar_w = len(d["meta_ar"]["quick_answer_ar"].split())
        b_ar_w = len(d["meta_ar"]["best_answer_ar"].split())
        d_ar_w = len(d["meta_ar"]["deep_answer_ar"].split())
        assert 35 <= q_ar_w <= 110, f"{qid} quick_ar {q_ar_w} out of [35, 110]"
        assert 90 <= b_ar_w <= 280, f"{qid} best_ar {b_ar_w} out of [90, 280]"
        assert 180 <= d_ar_w <= 650, f"{qid} deep_ar {d_ar_w} out of [180, 650]"
        print(f"{qid}: en_s={short_w}, en_st={struct_w}, en_d={deep_w} | ar_q={q_ar_w}, ar_b={b_ar_w}, ar_d={d_ar_w}")
    print("Pre-validation word count checks passed! Updating canonical questions...")

def apply_elevations():
    validate_words()

    topic_meta = {}
    for qid, d in sorted(DATA.items()):
        ee.update_canonical_question(
            qid=qid,
            concept_en=d["concept_en"],
            walkthrough_en=d["walkthrough_en"],
            structured_en=d["structured_en"],
            deep_senior_en=d["deep_senior_en"],
            short_en=d["short_en"],
        )
        topic_meta[qid] = d["meta_ar"]

    ee.save_topic_metadata("bld_08_14", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print(f"\nAll {len(DATA)} BLD questions (BLD-08 to BLD-14) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()

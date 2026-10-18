# Arabic Interview Lab terminology and voice

Use professional spoken Egyptian Arabic for the explanation. Keep the technical term in English when Android and Kotlin engineers ordinarily use its English name. The English term should clarify the mechanism, not replace an ordinary Arabic sentence. Prefer a direct answer, a concrete example, and a qualification when behavior depends on an API or provider contract.

| Keep in English | Avoid as the primary term |
| --- | --- |
| Structured Concurrency | التزامن المهيكل |
| Dispatchers | الموزعات |
| Higher-Order Functions | الدوال ذات الرتب العليا |
| Covariance / Contravariance / Invariance | التباين المشترك / التباين المعاكس / اللاتباين |
| State Machine | آلة الحالات |
| Dependency Injection | حقن التبعيات |
| Job Hierarchy | شجرة المهام الهرمية |
| Flow Collection | تجميع البيانات المتدفقة |
| Thread | خيط التنفيذ |
| Trade-offs | المفاضلات الهندسية |
| Common Pitfalls | مصائد الأخطاء |

Keep API names and identifiers exactly as written: `Coroutine`, `Flow`, `StateFlow`, `SharedFlow`, `Channel`, `Job`, `SupervisorJob`, `CancellationException`, `Dispatchers.IO`, `ViewModel`, `Lifecycle`, `Room`, `R8`, `Gradle`, `ANR`, `Mutex`, `WorkManager`, `Authorization`, `Capture`, `Settlement`, `Reversal`, `Reconciliation`, `EMV`, and `ISO 8583`. Use inline code for literal identifiers and paths. Keep code blocks and quoted English source questions LTR.

Natural Arabic exceptions are useful for ordinary concepts: **إلغاء** for cancellation, **فشل** for failure, **حالة** for state when it is not a named API, **مزامنة** for ordinary synchronization, **مصدر الحقيقة** for source of truth, **سؤال متابعة** for follow-up, and **مراجعة** for review. Do not switch every Arabic noun into English. A first mention can pair a plain Arabic explanation with the English term when that helps comprehension.

Avoid absolute claims such as “zero leaks,” “no overhead,” “always reverses,” or “exactly once” unless the specific documented contract establishes them. A local database write is not atomic with a remote payment. Cancellation is cooperative. A test or code example is described as tested only when the corresponding check has actually run.

For each question, read the immutable English wording first. Write `questionAr` as something an interviewer would ask aloud without adding a narrower requirement. Use the quick answer for an immediate response, the best answer for a practical explanation, and the deep answer for mechanisms and limits. The explanation fields should teach the concept rather than restate the spoken answer. Automated style signals are prompts for manual review, not editorial approval.

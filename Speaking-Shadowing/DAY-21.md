# Day 21 optional speaking — offline source of truth

Read [ARC-003](../04-Architecture-DI/arc-003-repository-source-of-truth-and-offline-first.md).

**20 seconds:** “The UI observes one local source of truth. A durable outbox synchronizes local intent with the server using stable mutation identities.”

**90 seconds:** “My repository owns the local and remote data policy. A local edit updates the entity and outbox atomically, so it appears immediately and survives restart. The worker sends one stable idempotency identity. A transport failure leaves the edit pending; an accepted response writes the canonical server version locally; a version conflict preserves the user's draft and remote evidence for an explicit resolution policy. Unit tests cover transitions, while Room, WorkManager, and API behavior need integration tests.”

<p dir="rtl" lang="ar"><strong>راجع نفسك:</strong> اشرح ليه local source of truth لا تعني إن client تحسم كل conflict، وفرق transport failure عن conflict.</p>

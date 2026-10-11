# Optional payment state-machine simulator

**Status: planned, outside the 96-hour core.** No simulator code or tests exist. A later educational implementation should use fake server, fake device, and fake network interfaces to model timeout, unknown outcome, idempotency, reversal queue, and recovery. It must not use real PAN/PIN, private keys, funds, vendor production SDKs, or claim EMV/PCI certification. Server acceptance and reconciliation cannot be guaranteed solely by the Android client. [Roadmap](../../ROADMAP.md).

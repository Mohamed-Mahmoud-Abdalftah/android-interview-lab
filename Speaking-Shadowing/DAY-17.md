# Day 17 — WorkManager, services, Doze and notifications

## 20-second answer

“Choose from lifetime and user visibility. Durable deferred upload fits WorkManager; an active user-visible transfer may justify FGS; screen-only work can stay in its owner scope.”

## Pressure prompts

- Choose between viewModelScope, WorkManager, expedited work, and a foreground service for an upload.
- Why is returning Result.retry for every exception dangerous?
- What must be true before choosing a foreground service?
- A product asks for a sync exactly every 15 minutes overnight. How do you respond?
- How do unique work policies affect duplicate sync requests?

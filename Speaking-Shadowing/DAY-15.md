# Day 15 — Tasks, intents, PendingIntent and export

## 20-second answer

“Launch modes control Activity instance and task behavior, but they do not define business navigation or typed arguments. I model destinations and test Back from real entry points.”

## Pressure prompts

- Explain why launchMode is not a substitute for modeling navigation state.
- An exported Activity trusts extras because only your notification creates the Intent. Review this assumption.
- Choose mutable or immutable PendingIntent for a notification action and explain identity collisions.
- What do you inspect before marking an Activity, service, or receiver exported?
- A valid app link opens an authenticated order screen while the user is signed out. Design the flow.

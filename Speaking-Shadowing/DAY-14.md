# Day 14 — Configuration change and process death

## 20-second answer

“ViewModel survives a configuration-created owner replacement, but it lives in process memory. Process death removes it; restoration needs saved-state keys and durable data.”

## Pressure prompts

- A ViewModel preserves a form after rotation. Why does that prove nothing about process death?
- Review code that puts a full API response in a Bundle to survive recreation.
- The UI renders defaults, then saved state, then database data and visibly jumps. Design the restoration order.
- When is rememberSaveable useful and when should state move to a ViewModel or repository?
- Design tests for a checkout screen across rotation and process death.

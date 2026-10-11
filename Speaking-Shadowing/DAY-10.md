# Day 10 — Flow cold/hot, StateFlow and SharedFlow

## 20-second answer

“I choose a stream from data semantics. Cold Flow restarts per collector. StateFlow represents a current state value and conflates equal updates. SharedFlow broadcasts future emissions with an explicit replay and buffer policy. The sharing scope owns upstream lifetime.”

## Pressure prompts

- Two collectors collect the same cold Flow and duplicate a network request. Explain the behavior and valid fixes.
- Why might assigning an equal data-class value to MutableStateFlow produce no new emission?
- Choose replay and buffer behavior for analytics events versus a critical payment result.
- A snackbar says Save failed. Should it be StateFlow or SharedFlow?
- Why is collecting a UI Flow in a plain launch risky on Android?

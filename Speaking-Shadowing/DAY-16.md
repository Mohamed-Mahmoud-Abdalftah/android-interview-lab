# Day 16 — Looper, Handler, Binder and ANR evidence

## 20-second answer

“The Looper processes one queued message at a time. A long Runnable prevents later input, lifecycle, and frame work from running until it returns.”

## Pressure prompts

- Trace how a long Runnable causes input latency on the main thread.
- Why can a fast service still cause an ANR through Binder?
- Given one ANR stack, how do you avoid blaming the top frame incorrectly?
- How can a delayed callback retain a destroyed screen, and what is the correction?
- Where should withContext(IO) live for a blocking database driver?

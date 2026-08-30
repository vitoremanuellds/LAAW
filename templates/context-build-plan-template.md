# Context build plan

Written by `build-context`'s `build-context.plan` sub-operation,
from [`context.temp.md`](context.temp.md). Copy target:
`.ai/workbench/build-plan.md`. Tracks which files still need reading
(`queued`) vs. already incorporated into `.ai/context/*.md`
(`read`) — updated by `build-context.iterate` every call.

```yaml
batch_size: 5   # files read per build-context.iterate call — set by the human at .plan time
```

| File | Status |
|---|---|
<!-- src/main.ts | queued -->
<!-- src/api/routes.ts | read -->

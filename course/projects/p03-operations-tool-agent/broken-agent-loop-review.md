# Broken Agent Loop Review

An AI coding agent proposed this pseudocode:

```python
while True:
    response = model.ask(history, tools=all_internal_functions)
    if response.tool_name:
        arguments = json.loads(response.arguments)
        result = globals()[response.tool_name](**arguments)
        history.append(str(result))
    else:
        return {"success": True, "answer": response.text}
```

The implementation exposes every internal function, performs no schema
validation, discards call IDs, has no iteration or repeated-call limits, catches
all tool exceptions and retries forever, logs the full history, and marks any
text response successful even after terminal tool failure.

## Learner task

Create `reports/broken-loop-review.md` covering:

1. Execution and authorization risks.
2. Argument and unknown-tool failures.
3. Call/result correlation.
4. Required state and trace data.
5. Stop and repetition limits.
6. Error categories and retry ownership.
7. Evidence requirements for a successful final answer.
8. A corrected transition diagram.

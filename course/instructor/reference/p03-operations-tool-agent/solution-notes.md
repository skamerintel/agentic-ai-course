# Project 3 Reference Notes

The reference implementation deliberately avoids an agent framework.

- `ToolRegistry` owns schema generation, strict validation, dispatch, bounds,
  and tool-error classification.
- `run_agent` owns iterations, repeated signatures, total calls, traces, and
  stop reasons.
- `ScriptedModelSession` verifies exact call-ID correlation offline.
- `OpenAIResponsesSession` uses Responses function calls and returns
  `function_call_output` items with matching call IDs.
- Retryable tool failures are returned to the model; the loop does not
  automatically repeat tool calls.

The reference does not prove that every completed final answer is factually
supported. Project 4 introduces systematic ground truth and evaluation for that
problem.

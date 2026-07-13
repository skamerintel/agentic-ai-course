# Project 3 AI Review Rubric

The AI reviewer reports evidence-backed findings and questions. It does not
grant final approval.

## Tool design

- Are tools narrow, read-only, typed, and clearly distinguished?
- Are schemas strict and result sizes bounded?
- Are unknown tools and invalid arguments handled without arbitrary dispatch?
- Are error categories useful to the model and operator?

## Agent loop

- Does the application own execution and stopping?
- Are tool results returned with the correct call IDs?
- Are sequential and parallel calls supported?
- Are iteration, total-call, and repeated-signature limits enforced?
- Can an empty model turn or provider error stop explicitly?

## Evidence and traces

- Does every model turn, call, result, and stop appear in the trace?
- Can unsupported answers after not-found or terminal errors be detected?
- Are logs bounded and sanitized?
- Are duplicate incidents and stale data handled transparently?

## Testing and ownership

- Can tests run without model credentials?
- Do scripted scenarios cover every required path?
- Is the live OpenAI adapter thin and current?
- Does the work log document rejected loop or tool proposals?

## Output format

1. Critical findings.
2. Important findings.
3. Questions for the learner.
4. Evidence supporting mentor review.
5. Unverified claims.

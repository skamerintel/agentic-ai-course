# Project 8 Reference Notes

The reference material solves the studio validator, not the capstone product.
That distinction preserves independent system design while still giving the
learner comparison material for strict Pydantic contracts and cross-field gate
logic.

The validator separates structural validation from architectural judgment. It
can detect missing workflow modes, decorative integrations, unsafe authority,
shallow evaluation, unjustified state, incomplete delivery plans, and missing
portfolio evidence. It cannot decide whether a business outcome is genuinely
valuable or whether an implementation is correct; mentor defense and executable
evidence remain required.

The exemplar support-escalation proposal is intentionally detailed enough to
demonstrate the standard. It is not a hidden product specification. A learner
may choose it, adapt another supplied brief, or defend a custom domain.

`examples/complete-artifact-manifest.json` demonstrates the final evidence
contract with placeholder repository locations. It proves shape, not completion;
the learner's paths and evidence statements must be independently reviewable.

FastMCP is disabled in the exemplar because no real MCP client is identified.
This is a positive architecture decision, not a missing checkbox. Redis is used
only for transient progress and coordination, while PostgreSQL remains durable
truth. Consequential writes are approved through a non-model-callable FastAPI
administrative boundary.

Mentor holdouts target checklist gaming: polished architecture language with a
chatbot interface, Redis as truth, model-controlled approval, decorative APIs,
and incomplete portfolio evidence.

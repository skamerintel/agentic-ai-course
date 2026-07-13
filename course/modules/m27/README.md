# M27: Portfolio, Résumé, and Interview Defense

## Learning objectives

By the end of this module, you can:

- Present a project as evidence of engineering decisions rather than a feature list.
- Communicate evaluation results with denominators, caveats, and limitations.
- Write truthful résumé bullets that connect action, system, and measured result.
- Give concise architecture, debugging, reliability, and AI-collaboration stories.
- Demonstrate a system without relying on a fragile live model or external API.
- Defend what remains before production use.

## Portfolio principle

The repository is the evidence. A polished landing page cannot compensate for
missing setup instructions, unverifiable metrics, unclear authority, leaked
secrets, or unexplained generated code.

The final narrative should answer:

1. What workflow problem mattered?
2. Why did this design fit the problem?
3. How was behavior measured?
4. What failed and what changed?
5. Which actions remained human-controlled?
6. What would be required for real production operation?

## Repository presentation

The public or reviewable repository should provide, in this order:

- a one-paragraph problem and outcome summary;
- an architecture and workflow diagram;
- a deterministic fixture-backed quick start;
- a live-provider configuration path without secrets;
- an evaluation summary linking to reproducible details;
- a success demo and at least two failure/recovery demos;
- security, privacy, cost, latency, and production limitations;
- package, container, and test commands;
- an explicit description of coding-agent use and human verification.

Archive scratch prompts and irrelevant generated files. Preserve useful design
decisions, experiment history, issue discussion, and review evidence.

## Metrics without theater

“Improved accuracy” is not a credible claim by itself. State the dataset,
sample count, metric definition, baseline, final result, important slice
regressions, model configuration, and whether the result came from development
or holdout data.

Do not call a fixture-backed portfolio system production-ready. Describe it as
a tested prototype or portfolio implementation and name the missing production
controls.

## Résumé bullets

Use this shape:

> Built **what system** for **which workflow**, using **relevant architecture**;
> demonstrated **measured result** on **named evaluation evidence**, while
> enforcing **important reliability or safety boundary**.

Avoid inflated user counts, invented savings, model-name trivia, and claims that
equate framework use with impact. Two precise bullets are stronger than six
technology lists.

## Five-minute technical walkthrough

1. **0:00-0:40 — problem:** user, current pain, measurable target.
2. **0:40-1:30 — architecture:** data flow, model boundary, state, APIs, approval.
3. **1:30-2:30 — evidence:** ground truth, baseline, failure slice, two iterations.
4. **2:30-3:30 — reliability:** failure/recovery demo and consequential-action guard.
5. **3:30-4:20 — judgment:** rejected feature or AI suggestion and tradeoff.
6. **4:20-5:00 — limits:** production gaps and next highest-value work.

Keep a fixture-backed recording or script available when live services fail.

## Interview story bank

Prepare concise Situation–Constraint–Decision–Evidence–Reflection stories for:

- ambiguous requirements and scope reduction;
- model failure discovered through evaluation;
- deterministic versus model-assisted design;
- external API or rate-limit failure;
- state, replay, or approval bug;
- unsafe or incorrect coding-agent output;
- a measured iteration that failed or regressed a slice;
- a production-readiness tradeoff under limited time.

The interviewer may ask you to modify a requirement. Explain what changes in
contracts, graph state, persistence, tests, evaluation, and operating risk.

## Adversarial defense questions

- Why is this an agent rather than a normal service or batch job?
- What happens if the model output is valid JSON but factually unsupported?
- How could untrusted GitHub or business-API text influence behavior?
- Where can duplicate or partial execution occur?
- Why is Redis present, and what breaks if it is flushed?
- What prevents the model from approving its own action?
- Which metric could be gamed, and which slice worries you most?
- What code did AI generate, and how did you establish that it was correct?
- What would you remove first if the operating budget were cut in half?
- What specifically prevents you from calling this production-ready?

## Guided lab

Rewrite three weak résumé bullets, then deliver the five-minute walkthrough.
The mentor interrupts at two points and requests deeper evidence. Revise the
demo so the evidence is reachable without searching the repository live.

## Independent challenge

Complete the portfolio packet, run a fixture-backed demo from a clean clone,
and answer the private interview challenge set without coding-agent assistance.

## Failure-analysis exercise

Remove or rewrite every claim containing “production ready,” “accurate,”
“robust,” “secure,” “scalable,” or “improved” unless the adjacent evidence
defines and supports it.

## Comprehension gate: G9C final defense

The mentor reviews the repository, selects code for explanation, runs one
private scenario, changes one design constraint, and conducts a mock interview.
Passing requires accurate technical ownership, evidence-backed claims, clear
limitations, and a coherent explanation of coding-agent collaboration.

## Required GitHub evidence

- Final portfolio README and architecture diagrams.
- Reproducible evaluation summary and failure report.
- Fixture-backed demo script and optional recording.
- Two résumé bullets and a project summary.
- Interview story bank and production-gap statement.
- Final review-resolution log.

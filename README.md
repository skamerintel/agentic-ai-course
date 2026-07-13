# LLM Application and Agent Engineering Course

This repository contains a self-paced, mentor-supported course for experienced
Python developers preparing for professional LLM application and agent
engineering roles.

## Course design

- [Formal course specification](docs/course-specification.md)
- [Curriculum roadmap](docs/curriculum-roadmap.md)
- [Project sequence](docs/project-sequence.md)
- [Official reference catalog](docs/reference-catalog.md)
- [Implementation status](docs/implementation-status.md)

Course-wide behavior, including reference-solution access, is configured in
[`course.toml`](course.toml).

## Implemented materials

- [M00-M24 and Projects 1-7](course/README.md)

Create the Project 1 learner workspace:

```bash
python coursectl.py start p01 work/p01
```

Create the Project 2 learner workspace:

```bash
python coursectl.py start p02 work/p02
```

Create the Project 3 learner workspace:

```bash
python coursectl.py start p03 work/p03
```

Create the Project 4 learner workspace:

```bash
python coursectl.py start p04 work/p04
```

Create the Project 5 learner workspace:

```bash
python coursectl.py start p05 work/p05
```

Create the Project 6 learner workspace:

```bash
python coursectl.py start p06 work/p06
```

Create the Project 7 learner workspace:

```bash
python coursectl.py start p07 work/p07
```

Inspect configured reference-solution access:

```bash
python coursectl.py status
```

In `gated` mode, the mentor unlocks a reference by copying
`course/progress.example.toml` to `.course-progress.toml` and changing the
project value to `true`. This is an honor-system learning gate, not a security
boundary.

# Review Exercise: Unsafe Package and Container

An AI-generated build configuration:

- Packages the entire repository, including `.env`, fixtures, reports, and local
  SQLite state.
- Uses `python src/github_workflow_mcp/server.py` as the runtime command.
- Copies source into the image after installing the wheel.
- Installs dev dependencies and compilers in the final image.
- Runs as root.
- Bakes a GitHub token and webhook secret into image layers.
- Has no health check or `.dockerignore`.

## Required review

Produce an approved wheel inventory, `.dockerignore` policy, multi-stage build,
runtime configuration map, non-root execution plan, and clean-environment smoke
test. Explain how copying source after wheel installation can hide packaging
defects.

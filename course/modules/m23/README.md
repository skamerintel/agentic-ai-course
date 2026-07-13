# M23: Docker and Local Multi-Service Delivery

## Learning objectives

By the end of this module, you can:

- Build a runtime image from an installed wheel.
- Control Docker build context with `.dockerignore`.
- Separate build and runtime stages.
- Run as a non-root application user.
- Configure health checks, ports, volumes, and environment variables.
- Validate a Compose-based local evaluation path.

## Prerequisite diagnostic

Review a Dockerfile that copies the entire repository, installs development
dependencies, embeds `.env`, runs as root, and starts `python src/server.py`.
Identify risks to reproducibility, package verification, image size, and secret
handling.

## Required reading

- [Docker references](../../../docs/reference-catalog.md#ref-docker)
- [uv build references](../../../docs/reference-catalog.md#ref-uv-build)

## Concept lesson

### The image should run the artifact you tested

Build the wheel in a builder stage and install that wheel into the runtime
environment. Do not copy the development source tree into the final image and
silently bypass packaging verification.

### Build context is an input boundary

Use `.dockerignore` to exclude Git history, virtual environments, caches,
reports, local state, secrets, and unrelated course material. A file omitted
from `COPY` can still be sent to the builder if the context is uncontrolled.

### Runtime images need fewer privileges and tools

Use a small runtime base, run as a non-root user, avoid compilers and package
managers in the final stage, and mount mutable state outside the image.

### Configuration belongs at runtime

Tokens, webhook secrets, API URLs, state paths, and fixture mode are environment
or secret inputs. Do not bake them into layers. Health checks should verify the
process boundary without exposing sensitive configuration.

### Compose documents local evaluation

Project 7 uses Compose to mount fixture data and durable SQLite state and expose
the HTTP MCP/webhook service. Production deployment would replace local fixture
mode and likely use a managed durable store.

## Guided lab

Build Project 7's multi-stage image, inspect its user and installed files, start
the Compose service, and run an external health and MCP smoke test.

## Independent challenge

Repair a development Dockerfile that copies source after installing the wheel,
thereby hiding missing package files.

## Failure-analysis exercise

Diagnose a container that passes local tests but fails in a clean build because
the application reads repository fixtures absent from the wheel and image.

## Comprehension gate

The learner explains each Docker stage, build-context exclusion, runtime mount,
environment value, health check, and difference between local Compose and a
production deployment.

## Required GitHub evidence

- Dockerfile and `.dockerignore` review.
- Compose configuration.
- Image-content notes.
- External smoke-test transcript.

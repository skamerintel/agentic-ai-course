# M22: Customer-Facing Packages with uv and Hatchling

## Learning objectives

By the end of this module, you can:

- Distinguish a distribution package from an import package.
- Configure a `src` layout and Hatchling build targets.
- Build wheel and source distributions with uv.
- Inspect artifacts for missing runtime files and accidental secrets.
- Install the wheel into a clean environment.
- Run a public API smoke test outside the repository checkout.

## Prerequisite diagnostic

Explain why `python src/server.py` succeeding does not prove an installed wheel
works. List files that should and should not appear in Project 7's wheel.

## Required reading

- [uv build references](../../../docs/reference-catalog.md#ref-uv-build)
- [Hatchling references](../../../docs/reference-catalog.md#ref-hatchling)
- [Python packaging references](../../../docs/reference-catalog.md#ref-python-packaging)

## Concept lesson

### The repository and distribution serve different audiences

The development repository contains tests, fixtures, reports, and mentor
material. The customer-facing wheel contains the import package and required
runtime assets. Do not ship `.env` files, local databases, test credentials, or
course fixtures by accident.

### A `src` layout exposes accidental imports

Tests should import the installed package rather than relying on the repository
root. This catches code that works only because local paths are present.

### Inspect both wheel and source distribution

Build with `uv build`, list artifact contents, and compare them with an approved
inventory. A wheel can omit a runtime file while the source distribution still
contains it, or vice versa.

### Clean installation is the real smoke test

Create an empty environment, install the built wheel, import the public API,
construct the server, and run one deterministic client call without the source
checkout on `sys.path`.

### Versioning communicates compatibility

Package versions, public API changes, tool schema changes, and deployment
configuration need an intentional compatibility story even for an internal
service.

## Guided lab

Build Project 7, inspect both artifacts, and test its public server factory from
a clean temporary environment.

## Independent challenge

Repair an over-inclusive build that ships tests, fixture tokens, reports, and a
local SQLite database. Preserve only required runtime code and metadata.

## Failure-analysis exercise

Diagnose a wheel that imports successfully from the repository but fails after
installation because it reads `../fixtures/github-api.json` at import time.

## Comprehension gate

The learner builds, inventories, clean-installs, and invokes the package while
explaining every included runtime file and excluded development file.

## Required GitHub evidence

- Build configuration.
- Wheel and sdist inventory.
- Clean-install transcript.
- Public API smoke test.

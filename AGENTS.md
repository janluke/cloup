# Agent instructions

Read `README.rst` for the project overview and `CONTRIBUTING.rst` for the complete
development workflow.
Keep this file focused on repository-specific operating rules instead of duplicating
those documents.

## Sources of truth

- Define Python project metadata, build settings, and supported Python versions in
  `pyproject.toml`.
- Define development environments and their scripts in `hatch.toml`.
- Use `taskfile.yml` as the local orchestration interface over Hatch.
- Keep the Python and Click matrices in `hatch.toml` and `.github/workflows/ci.yml`
  synchronized.
- Treat `.readthedocs.yml` as a separate deployment path from the local Hatch docs
  environment: RTD does not invoke Hatch. Both must remain functional and use
  `pylock.docs.toml`.

## Development workflow

- Use Task for local aggregate workflows and Hatch for commands within a specific
  environment.
- Run targeted checks while iterating.
- Run `task qa` for routine changes and `task qa:all` for changes that may affect
  supported Python or Click versions.
- Run `task build` after changing packaging, project metadata, package layout, or build
  hooks.
- Keep GitHub Actions jobs expressed directly in terms of Hatch so matrix entries and
  independent checks remain visible in the GitHub UI; do not replace them with one
  aggregate Task invocation.

## Dependencies and lockfiles

- Keep dependencies scoped to the Hatch environments that use them.
- The development and test environments intentionally resolve compatible dependencies
  afresh.
- Lint, documentation, and package-checking environments use committed PEP 751
  lockfiles.
- Regenerate an affected lockfile with `hatch env lock ENV_NAME` after changing a
  locked environment.
- Use `--upgrade` and `--upgrade-package <pkg>` only for an intentional dependency
  refresh.
- Commit each changed `pylock.*.toml` file with the configuration change that required
  it.

## Editing conventions

- Preserve unrelated user changes and keep work within the requested scope.
- Do not fix unrelated lint, typing, or test failures unless explicitly asked.
- Keep structural changes and repository-wide mechanical formatting in separate
  commits so history remains reviewable.
- Use the `.yml` extension for YAML files in this repository.
- Do not edit generated files such as `src/cloup/_version.py` or documentation build
  output.

## Reviews and Git operations

- Perform a detailed review only when explicitly requested.
- When asked only to commit existing work, limit validation to a quick status and diff
  sanity check unless the user requests broader verification.
- Do not create commits, push branches, or modify pull requests unless explicitly
  requested.
- Never push changes to a remote unless the user explicitly authorizes it.

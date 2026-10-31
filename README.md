# Quizzivy

Web app for a private English-teaching practice. Students take tests assigned by
their teacher; the teacher builds tests, assigns them, monitors attempts, grades
open answers, and reviews results.

Product language is Vietnamese. Code, comments and docs are English.

This repository holds what the code repositories share: the spec, the plan, the
standing rules and the agent team's records. It publishes the
[wiki](https://github.com/Quizzivy/docs/wiki), which also carries the
documentation of the code repositories.

| Repository | What it holds |
|---|---|
| [`Quizzivy/sdk`](https://github.com/Quizzivy/sdk) | the API contract (`api/openapi.yaml`) and `@quizzivy/sdk` built from it. **A contract change starts there.** |
| [`Quizzivy/api`](https://github.com/Quizzivy/api) | the Go server, the migrations, the seed, the worker images; setup and operations in `docs/setup/` |
| [`Quizzivy/web`](https://github.com/Quizzivy/web) | the React app and the design deck (`docs/design/`) |
| `Quizzivy/docs` (this one) | spec, plan, standing rules, the wiki, the project sync |
| [`Quizzivy/infra`](https://github.com/Quizzivy/infra) | the VPS: Compose, Caddy, deploy scripts |

Until the end of October 2026 everything lived in one repository,
`SekiroKenjii/Quizzivy`, which stays readable as an archive. Each new repository
kept the history of its files (D-082). A path written in these documents, such
as `server/internal/...` or `web/src/...`, is the same path in the repository
that now holds it; the wiki links each one there.

## Documents, in order of authority

| | |
|---|---|
| [`docs/quizzivy-spec-v0.3.md`](docs/quizzivy-spec-v0.3.md) | Product and engineering spec. Source of truth. |
| [`docs/plan/`](docs/plan/) | Implementation plan derived from it. Start at [`00-overview.md`](docs/plan/00-overview.md). |
| [`api/openapi.yaml`](https://github.com/Quizzivy/sdk/blob/develop/api/openapi.yaml) | The API contract, in `Quizzivy/sdk`. Spec §15 documents it. |
| [`AGENTS.md`](AGENTS.md) | Standing rules for every repository. Read before touching anything. |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Branch model and PR expectations. |

The schema lives in [`docs/plan/20-data-model.md`](docs/plan/20-data-model.md),
including a register of every deliberate deviation from the spec sketch.

## Stack

Vite + React 19 + TypeScript (strict), TanStack Query, Zustand, Tailwind v4 +
shadcn/ui, i18next. Go backend, PostgreSQL 18, Cloudflare R2. Fixed by spec §2;
do not swap libraries without approval.

To run the app, start with the README of `Quizzivy/api`, then that of
`Quizzivy/web`.

## This repository

- **The wiki.** `scripts/wiki/build.py` builds it from the files here and from
  the `develop` branch of sdk, api and web (`docs/wiki.md`). Edit the source
  file, never the wiki page.
- **The project sync.** `.github/workflows/project-sync.yml` mirrors issue labels
  and `Task: #N` lines onto the org's GitHub Project
  (`scripts/ci/project-sync.mjs` says how). Other repositories can call it.
- **CI** builds the wiki with every link checked and runs the scripts' tests;
  the required check is **CI result**.

# Contributing

Read [`AGENTS.md`](AGENTS.md) first. It is the standing rule set for every
Quizzivy repository; each code repository's own `AGENTS.md` and
`CONTRIBUTING.md` add what is specific to it.

## Which repository

| The change | Where |
|---|---|
| An endpoint, a schema, a shared catalogue | [`Quizzivy/sdk`](https://github.com/Quizzivy/sdk) first, then api and web pin the version it publishes |
| Server, migrations, seed, setup and operations docs | [`Quizzivy/api`](https://github.com/Quizzivy/api) |
| The app, the design deck | [`Quizzivy/web`](https://github.com/Quizzivy/web) |
| Spec, plan, standing rules, team records, the wiki build, the project sync | here |

## Branch model

Gitflow, in every repository.

| Branch | Purpose |
|---|---|
| `main` | Released only. Never committed to directly. |
| `develop` | Integration. Every PR targets this. |
| `feature/<task>-<slug>` | One task. Branch off `develop`. |
| `hotfix/<slug>` | Off `main`. Merged to **both** `main` and `develop`. |
| `chore/<slug>` | Off `develop`. Work that is not a task: tooling, layout. |

Merge the pull request with a merge commit, never a squash, so each task stays
a visible unit in the history. Here nothing deploys and nothing is tagged:
`main` follows `develop` when the owner merges it.

## One task, one PR

Tasks are issues on the org's GitHub Project. A PR names its issue in a line
`Task: #N` (moves it to In Progress, and to Done when the PR merges) or
`Part of: #N` (links only). Labels `status:`, `next:`, `priority:`, `release:`
and `workstream:` on an issue set those fields; `scripts/ci/project-sync.mjs`
has the details.

If a task turns out to be bigger than its stated size (S < 2h, M half day,
L full day), split it and record the split in the plan. Do not let a task
grow past L. Do not merge a task whose dependencies are unmerged.

## Commit messages

An imperative summary that starts with the task id when there is one
(`T-R6.4: ...`), then a body explaining *why*. English.

Reference the spec by section number (`§13.3`), never by quoting it back.

## Before opening a PR here

```bash
python3 -m unittest discover -s scripts/wiki/tests
node --test "scripts/ci/tests/*.test.mjs"
# with sdk, api and web checked out next to this repository:
python3 scripts/wiki/build.py . /tmp/wiki --strict \
  --with sdk=../sdk --with api=../api --with web=../web
```

CI runs the same; the required check is **CI result**.

## Documentation and the wiki

The files here, and the documentation in sdk, api and web, are the source. The
wiki is generated from them (`docs/wiki.md`). Edit the file, never the wiki
page: the next run overwrites it.

## Things that will get a PR sent back

- A generated file edited by hand (`server/gen/` in api, `sdk/` in sdk)
- A new dependency with no reason in the description
- English-only user-facing text
- A public endpoint without both §6.5 boxes ticked in the same PR
- A failing test deleted or skipped rather than fixed
- `SELECT *` in application code
- DDL that contradicts `docs/plan/20-data-model.md` without a new `D-nn` entry

## Open questions

Check `docs/plan/40-open-items.md` before asking. Most questions are already
there with a stated default; build the default and move on. Ask one precise
question only when the answer changes what you build.

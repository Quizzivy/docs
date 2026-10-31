# The wiki

The [wiki](https://github.com/Quizzivy/docs/wiki) is generated. Its pages come
from the Markdown in this repository and in the `develop` branch of
`Quizzivy/sdk`, `Quizzivy/api` and `Quizzivy/web`; edit those files, never a
wiki page, which the next run overwrites.

## How it is built

`scripts/wiki/build.py` reads this checkout and one checkout of each other
repository:

```bash
python3 scripts/wiki/build.py . /tmp/wiki --strict \
  --with sdk=../sdk --with api=../api --with web=../web
```

- The table `DOCS` in the script names each published file, its repository,
  page name, sidebar title and group. A Markdown file it does not list (under
  `docs/`, a directory README, a repository's root README, `AGENTS.md` or
  `CONTRIBUTING.md`) is still published, under "Other", with a warning: add it
  to the table.
- A relative link resolves in the repository of the file that holds it first,
  then in sdk, api and web in that order. So the plan's link to
  `../../server/main.go` lands on `Quizzivy/api`, and `api/openapi.yaml` on
  `Quizzivy/sdk`, which owns the contract (api keeps a synced copy).
- A link to a published file becomes a link to its wiki page; a link to any
  other file or directory becomes a link to it on GitHub, in the repository
  that has it. A Markdown file named in backticks becomes a link too; a bare
  name such as `deploy.md` means the file of that name in the first repository
  of the same order (api's `docs/setup/deploy.md` from a plan document, web's
  `docs/deploy.md` from a web document).
- A symbolic link is never published, and a link that climbs out of its
  repository is left as written, which fails the build.
- Large documents (the spec, the data model, R4 and D4) are split into several
  pages; the build checks that the split loses no text.
- The build fails when a link between wiki pages does not resolve, and with
  `--strict` when a link names a path that no repository has.

## When it runs

- **CI** (every PR and push): the script's tests, then a `--strict` build
  against the `develop` branch of the other repositories. A broken link in any
  of them fails it.
- **Wiki** (`.github/workflows/wiki.yml`): on a push to `develop` here, once a
  day for changes in the other repositories, and from Run workflow. It clones
  the wiki, builds into it without `--strict`, and pushes the difference.

The wiki has to exist before the first run: Settings → Features → Wikis on, and
one page saved by hand (the build replaces it).

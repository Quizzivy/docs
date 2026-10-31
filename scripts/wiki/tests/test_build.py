import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SPEC = importlib.util.spec_from_file_location("wiki_build", Path(__file__).resolve().parents[1] / "build.py")
build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build)

TABLE = [
    ("docs", "docs/plan/00-overview.md", "Plan-00-Overview", "Overview", "Implementation plan", None),
    ("docs", "docs/plan/20-data-model.md", "Plan-20-Data-Model", "Data model", "Implementation plan", "greedy"),
    ("api", "docs/setup/ci.md", "Setup-CI", "API: CI", "Setup and operations", None),
]


def write(root, path, text):
    target = Path(root) / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def big_model():
    sections = []
    for n in range(1, 41):
        body = "\n".join(f"Row {n}.{k} " + "x" * 120 for k in range(1, 40))
        sections.append(f"## {n}. Section {n}\n\n### Detail {n}\n\n{body}\n")
    return "# 20 — Data Model\n\nIntro.\n\n" + "\n".join(sections)


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.src = os.path.join(self.tmp.name, "src")
        self.api = os.path.join(self.tmp.name, "api")
        self.out = os.path.join(self.tmp.name, "wiki")
        write(self.src, "README.md", "# Quizzivy\n\nSee [the plan](docs/plan/).\n")
        write(self.src, "docs/plan/00-overview.md",
              "# 00\n\nSchema: `20-data-model.md`, [section 7](20-data-model.md#7-section-7), "
              "[code](../../server/main.go), `docs/setup/ci.md`.\n\n```\n[x](20-data-model.md) `20-data-model.md`\n```\n")
        write(self.src, "docs/plan/20-data-model.md", big_model())
        write(self.api, "README.md", "# Quizzivy API\n\nRules: [AGENTS.md](AGENTS.md).\n")
        write(self.api, "AGENTS.md", "# API rules\n")
        write(self.api, "server/main.go", "package main\n")
        write(self.api, "docs/setup/ci.md", "# CI\n\nThe [plan](../../docs/plan/00-overview.md) and [main](../../server/main.go).\n")
        patcher = mock.patch.object(build, "DOCS", TABLE)
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_build(self, *extra, code=0):
        self.assertEqual(build.main([self.src, self.out, "--owner", "o", "--with", f"api={self.api}", *extra]), code)

    def read(self, name):
        return Path(self.out, name + ".md").read_text(encoding="utf-8")

    def test_a_large_document_splits_and_links_land_on_the_part_holding_the_heading(self):
        self.run_build()
        parts = [f for f in os.listdir(self.out) if f.startswith("Plan-20-Data-Model-Part-")]
        self.assertGreater(len(parts), 1)
        overview = self.read("Plan-00-Overview")
        self.assertIn("[`20-data-model.md`](Plan-20-Data-Model)", overview)
        part = next(p for p in parts if "## 7. Section 7" in Path(self.out, p).read_text(encoding="utf-8"))
        self.assertIn(f"(Plan-20-Data-Model-{part[len('Plan-20-Data-Model-'):-3]}#7-section-7)", overview)
        self.assertIn("(https://github.com/o/api/blob/develop/server/main.go)", overview)

    def test_fenced_code_is_left_as_written(self):
        self.run_build()
        self.assertIn("```\n[x](20-data-model.md) `20-data-model.md`\n```", self.read("Plan-00-Overview"))

    def test_a_second_run_changes_nothing(self):
        self.run_build()
        first = {f: Path(self.out, f).read_bytes() for f in os.listdir(self.out)}
        self.run_build()
        self.assertEqual(first, {f: Path(self.out, f).read_bytes() for f in os.listdir(self.out)})

    def test_pages_the_build_did_not_write_survive_and_stale_generated_ones_go(self):
        write(self.out, "For-team.md", "Written by hand in the wiki.\n")
        write(self.out, "Old-Page.md", f"Gone from the repository.\n{build.MARKER}\n")
        write(self.out, "Home.md", "Welcome to the wiki!\n")
        self.run_build()
        self.assertEqual(self.read("For-team"), "Written by hand in the wiki.\n")
        self.assertFalse(Path(self.out, "Old-Page.md").exists())
        self.assertIn("Quizzivy", self.read("Home"))

    def test_a_document_missing_from_the_table_is_still_published(self):
        write(self.src, "docs/plan/95-new.md", "# 95 — New\n\nBody.\n")
        self.run_build()
        self.assertIn("Body.", self.read("Docs-Plan-95-New"))
        self.assertIn("(Docs-Plan-95-New)", self.read("_Sidebar"))

    def test_a_link_lands_in_the_repository_that_has_the_file(self):
        self.run_build()
        ci = self.read("Setup-CI")
        self.assertIn("[main](https://github.com/o/api/blob/develop/server/main.go)", ci)
        self.assertIn("[plan](Plan-00-Overview)", ci)
        self.assertIn("in o/api.", ci)
        self.assertIn("[`docs/setup/ci.md`](Setup-CI)", self.read("Plan-00-Overview"))

    def test_a_path_in_the_linking_repository_wins_over_the_same_path_elsewhere(self):
        write(self.src, "server/main.go", "package docs\n")
        self.run_build()
        self.assertIn("(https://github.com/o/docs/blob/develop/server/main.go)", self.read("Plan-00-Overview"))
        self.assertIn("(https://github.com/o/api/blob/develop/server/main.go)", self.read("Setup-CI"))

    def test_another_repositorys_readme_and_rules_are_published_under_its_name(self):
        self.run_build()
        self.assertIn("Rules: [AGENTS.md](Api-AGENTS)", self.read("Api-README"))

    def test_a_link_to_a_path_no_repository_has_fails_only_when_strict(self):
        write(self.src, "docs/plan/95-new.md", "# 95\n\n[gone](../../server/gone.go)\n")
        self.run_build()
        self.run_build("--strict", code=1)

    def test_a_missing_repository_is_a_warning_not_a_failure(self):
        self.assertEqual(build.main([self.src, self.out, "--owner", "o"]), 0)
        self.assertIn("(https://github.com/o/docs/blob/develop/server/main.go)", self.read("Plan-00-Overview"))

    def test_a_bare_file_name_in_several_repositories_means_the_first_in_order(self):
        web = os.path.join(self.tmp.name, "web")
        write(self.api, "docs/setup/deploy.md", "# Deploying the API\n\nSee `ci.md`.\n")
        write(web, "docs/deploy.md", "# Deploying the web\n\nSee `deploy.md` and `ci.md`.\n")
        write(web, "docs/ci.md", "# Web CI\n")
        write(web, "README.md", "# Quizzivy web\n\nCI: `ci.md`.\n")
        write(self.src, "docs/plan/95-new.md", "# 95\n\nSee `deploy.md`.\n")
        self.run_build("--with", f"web={web}")
        self.assertIn("[`deploy.md`](Api-Docs-Setup-Deploy)", self.read("Docs-Plan-95-New"))
        self.assertIn("[`ci.md`](Setup-CI)", self.read("Api-Docs-Setup-Deploy"))
        self.assertNotIn("[`deploy.md`]", self.read("Web-Docs-Deploy"))
        self.assertIn("[`ci.md`](Web-Docs-Ci)", self.read("Web-Docs-Deploy"))
        self.assertIn("[`ci.md`](Web-Docs-Ci)", self.read("Web-README"))

    def test_a_link_that_climbs_out_of_the_repository_is_refused(self):
        for target in ("../../../../etc/hostname", "/docs/../../../../etc/hostname"):
            with self.subTest(target=target):
                write(self.src, "docs/plan/95-new.md", f"# 95\n\n[out]({target})\n")
                self.run_build(code=1)

    def test_a_symbolic_link_is_not_published(self):
        secret = os.path.join(self.tmp.name, "secret.md")
        write(self.tmp.name, "secret.md", "# Secret\n\ncanary\n")
        os.makedirs(os.path.join(self.api, "docs"), exist_ok=True)
        os.symlink(secret, os.path.join(self.api, "docs", "linked.md"))
        self.run_build()
        self.assertFalse(Path(self.out, "Api-Docs-Linked.md").exists())
        self.assertFalse(any("canary" in Path(self.out, f).read_text(encoding="utf-8") for f in os.listdir(self.out)))


if __name__ == "__main__":
    unittest.main()

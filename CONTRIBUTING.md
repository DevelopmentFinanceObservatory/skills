# Contributing

Issues and pull requests are welcome, whether you want to correct a skill or add one. The ONE Data team maintains this repository. For a large change, such as a new skill or a restructure, open an issue first so we can agree on scope before you write it.

Everyone taking part follows the [Code of Conduct](https://github.com/DevelopmentFinanceObservatory/.github/blob/main/CODE_OF_CONDUCT.md). Report a security problem through GitHub's private vulnerability reporting, as the [security policy](https://github.com/DevelopmentFinanceObservatory/.github/blob/main/SECURITY.md) describes, and do not open a public issue. [SUPPORT.md](https://github.com/DevelopmentFinanceObservatory/.github/blob/main/SUPPORT.md) says where to ask questions.

By contributing you agree that your work is released under the repository's licences: code in `scripts/`, `tests/` and `.github/workflows/` under [MIT](LICENSE-CODE), and everything else, including the skills, under [CC BY 4.0](LICENSE).

## Add or correct a skill

To correct a skill, edit its `SKILL.md` or the file under its `references/` directory and open a pull request. State the source for any changed fact in the pull request.

To add a skill:

1. Copy `template/` to `skills/<name>/`. The directory name is the skill's name, in lowercase with hyphens.
2. Write `SKILL.md`, and delete or replace `references/example.md`.
3. Edit `attachments.yaml`.
4. List the skill in `skills/categories.yaml` and in the skill list in `README.md`.
5. Run the checks below.

## Format

Each skill directory holds a `SKILL.md` with YAML front matter, following the [Agent Skills](https://agentskills.io/specification) convention so that any agent can load it. It uses three fields:

- `name`, matching the directory name.
- `description`, the text discovery matches against. It says what expertise the skill carries and when an agent should load it.
- `license`, always `CC-BY-4.0`. A skill downloaded on its own has no `LICENSE` file beside it, so each skill names its licence itself.

Supporting files such as reference tables and longer method notes sit in a `references/` directory inside the skill. `SKILL.md` points at each one with a relative Markdown link whose label is the path, such as `[references/flow-types.md](references/flow-types.md)`, and says when to read it. The agent loads the cheap summary first and the heavy material on demand.

Keep those pointers one level deep. `SKILL.md` names every reference file the skill has, and a reference file that sends the agent on to another one makes the skill harder to load a piece at a time.

Each paragraph and each list item sits on one line, however long, with a blank line between paragraphs. The text is published somewhere that joins the words either side of a line break, so a break inside a paragraph would corrupt the sentence it splits.

Skills live under one of two roots. `skills/` holds the skills offered for install, and the plugin at the repository root loads every directory there. `internal/skills/` holds skills published on the DFO platform and left out of the install routes. A skill name sits under one root only, and a name that starts with `_` fails the validator. Add new skills under `skills/`.

### Attachments

Each skill directory holds an `attachments.yaml` that names the DFO knowledge-graph nodes the skill explains. The file is required. It takes two optional keys, each a list of unique strings:

- `applies_to`, ontology nodes whose series the skill explains, such as `dcid:CRSPurposeCode930`.
- `sources`, the provenance node of each data export the skill explains as a whole, such as `dcid:provenance/OECDCreditorReportingSystem`. Only a skill about one dataset, such as `oda-crs`, uses this key.

```yaml
applies_to:
  # references/core-oda.md subtracts in-donor refugee costs from total ODA.
  - dcid:CRSPurposeCode930
sources: []
```

A skill that attaches nowhere holds `applies_to: []` and `sources: []`. Attach a node only when a series carrying it would be misread without a section of the skill, and only when a minority of a source's series carry it. Put a comment beside each entry that gives the reason and names the reference file that covers it. An entry that is not a node in the DFO ontology fails CI. Ask in your pull request if you are unsure which node fits.

### Categories

`skills/categories.yaml` files every skill in `skills/` under one category. It takes three keys:

- `sources`, skills that explain one dataset, such as `oda-crs`.
- `domains`, skills that explain a subject across datasets, each listed under a domain such as `development-assistance` or `sovereign-debt`.
- `uncategorised`, skills that are neither.

```yaml
sources:
  - oda-crs
domains:
  development-assistance:
    - oda-measures
  sovereign-debt:
    - debt-concepts
uncategorised: []
```

Add a new skill's name to one list. To start a domain, add a key under `domains`, named like a skill.

## Check your change

Python 3.13 matches CI. From the repository root:

```bash
pip install -r requirements-dev.txt
python -m unittest discover
python scripts/validate_skills.py
```

The validator checks every skill against the format above and prints each problem with its file. Errors fail the run, and warnings do not. CI runs the same tests and validator on every pull request once it is ready for review, and also compiles the DFO ontology to check `applies_to` entries. The ontology compiler is in a public repository, so you can run that check locally. [docs/development.md](docs/development.md) has the commands and the full list of validator rules.

## Pull requests

Branch from `dev` and open the pull request against `dev`. Branch names such as `feat/skill-name`, `fix/short-description` and `docs/short-description` match the history. Commit messages use a [Conventional Commits](https://www.conventionalcommits.org) prefix, such as `feat:`, `fix:`, `docs:`, `ci:` or `build:`, but no check enforces it.

A pull request needs:

- A passing `Validate skills` check.
- The skill list in `README.md` and `skills/categories.yaml` updated when a skill is added.
- A source for every fact you add or change.

Open the pull request as a draft while you work. CI runs when you mark it ready for review.

Maintainer notes on publishing, versioning, and the checks CI runs are in [docs/development.md](docs/development.md).

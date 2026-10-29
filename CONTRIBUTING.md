# Contributing to the Development Finance Observatory skills

Every skill in this repository follows one format, and a validator checks it in CI. `README.md` says what the skills are and how to install them.

## How skills reach an agent

Each skill is registered as a node in the DFO knowledge graph, carrying its front matter and the links to the graph nodes its `attachments.yaml` declares. The DFO AI harness consumes that registry at launch. Any other agent loads the skills through the install routes in `README.md`.

The DFO docs hub publishes each skill as a page, with one child page per reference file and its first heading as the title. Renaming or deleting a skill or a reference file changes or removes a published page's address with no redirect, so a link to the old page from elsewhere breaks.

## Format

One directory per skill, named for the skill, under one of two roots:

- `skills/` holds the skills offered for install. The plugin at the repository root loads every directory there, so each one must be a valid skill.
- `internal/skills/` holds the skills the DFO publishes to its knowledge graph and docs hub and keeps out of the install routes, such as `dfo-faq`.

A skill's name is its id in the graph, the Skills API and the docs hub, so a name sits under one root. The validator fails a directory under either root whose name starts with `_`. `template/` holds a skill to copy when starting a new one. A new skill under `skills/` also goes in the `README.md` list, under its group. A test fails if the list omits a skill.

Each skill directory holds a `SKILL.md` with YAML front matter, following the Agent Skills convention so agents outside the DFO can load these packages too. Three fields do the work:

- `name`, matching the directory name.
- `description`, the text discovery matches against. It says what expertise the skill carries and when an agent should load it.
- `license`, always `CC-BY-4.0`. A skill downloaded on its own has no `LICENSE` file beside it, so each skill names its licence itself.

Supporting files (reference tables, longer method notes) sit in a `references/` directory inside the skill, and `SKILL.md` points at each one with a relative Markdown link whose label is the path, such as `[references/flow-types.md](references/flow-types.md)`. The body tells the agent when to read them, so a skill loads its cheap summary first and its heavy material only on demand. The link also lets the published documentation site take a reader from the skill's page to each reference page.

Keep those pointers one level deep. `SKILL.md` names every reference file the skill has, and a reference file that sends the agent on to another one makes the skill harder to load a piece at a time.

Each paragraph and each list item sits on one line, however long, with a blank line between paragraphs. dfo-pipelines publishes this text to the knowledge graph, which drops line breaks and joins the words on either side of one, so a line break inside a paragraph or a list item would silently corrupt the sentence it splits.

### Graph attachments

Each skill directory also holds an `attachments.yaml` naming the knowledge-graph nodes the skill explains. dfo-pipelines reads it, checks that every entry resolves, and links the skill to each node, leaving the file itself out of the graph. It takes two keys, each a list of unique strings:

- `applies_to`, ontology nodes whose series the skill explains, such as `dcid:CRSPurposeCode930`.
- `sources`, the provenance node of each dfo-pipelines export the skill explains as a whole, such as `dcid:provenance/OECDCreditorReportingSystem`. A data-source skill such as `oda-crs` attaches here, and so reaches every series that export publishes.

```yaml
applies_to:
  # references/core-oda.md subtracts in-donor refugee costs from total ODA.
  - dcid:CRSPurposeCode930
sources: []
```

Both keys are optional, and a missing key is an empty list, but the file is required: a skill that attaches nowhere holds `applies_to: []` and `sources: []`. Any other key, a duplicate entry, an entry of the wrong shape, or a YAML anchor or alias fails the validator. `template/attachments.yaml` is the copy to start from.

Attach a skill to an ontology node only when a series carrying that node would be misread without a section of the skill, and only when a minority of a source's series carry it. An attachment covers the node's descendants in the ontology's own hierarchy, so a parent code stands for its children. A node every series of a source carries adds no information over the source itself, so it is not worth attaching. A comment beside each entry gives the reason and names the reference file that covers it, so the attachment moves or goes with the material that justifies it.

### Categories

`skills/categories.yaml` files every skill in `skills/` under one category. The DFO docs hub reads it to group the skill pages, and shows the categories, and the skills within each, in the file's order. It takes three keys:

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

Add a new skill's name to one list. To start a domain, add a key under `domains`. A domain's name follows the skill name format, and the docs hub shows it in sentence case, so `sovereign-debt` appears as "Sovereign debt". The validator fails a directory under `skills/` that the file leaves out, a skill listed more than once, and an entry that names no directory under `skills/`, which includes a skill under `internal/skills/`.

### Shared rules

Some hosts load one skill at a time, so a rule that several skills need is written into each of them. The rule's text lives once, in `shared-rules/<rule-id>.md` at the repository root, and each skill holds a copy between two marker lines, each a paragraph of its own:

```markdown
<!-- shared:oecd-region-readings -->

The rule's text.

<!-- /shared:oecd-region-readings -->
```

To change a shared rule, edit its source file and run `python scripts/sync_shared_rules.py`, which writes the source into every marked copy. To share a new rule, add its source file and put the markers where each skill states it. Wording that applies to one dataset alone goes outside the markers. The validator fails on a copy that differs from its source, a marker that names no source, a source no skill copies, and markers that do not pair up. The markers are HTML comments, so they stay in the published skill and the ChatGPT package and render as nothing.

### Plugin

The repository root is one plugin, `dfo`. `.claude-plugin/plugin.json` names it and lists no components, so Claude and Codex load every directory under `skills/` as a skill and load nothing from `internal/skills/` or `template/`. `.claude-plugin/marketplace.json` offers that plugin to a user who adds the repository as a plugin marketplace, which is also named `dfo`. A new skill under `skills/` needs no change to either file.

The root `plugin.json` and `mcp.json` describe the same plugin for ChatGPT's plugin directory, and `.mcp.json` connects the DFO MCP server in the Claude plugin. When skills change, raise `version` in `plugin.json` and `.claude-plugin/plugin.json` together, since each directory publishes an update only under a new version. Then run `python scripts/build_chatgpt_plugin.py`, which writes `dist/dfo-chatgpt-plugin.zip` for upload. It checks the listing against OpenAI's limits and the two manifests against each other, and writes nothing if a check fails.

## Checking a skill before you open a pull request

CI runs the validator's tests and the validator on every push to `dev` or `main` and on every pull request once it is ready for review, and they run locally the same way. CI also compiles the DFO ontology and fails an `applies_to` entry that is not a node in it. The workflow installs the compiler from the public `DevelopmentFinanceObservatory/ontology` repository at the commit `DFO_ONTOLOGY_REF` names. To run that check locally, compile the ontology with `dfo-ontology compile --bench prod --output dfo.mcf` and add `--ontology-mcf dfo.mcf` to the validator command.

```bash
pip install -r requirements-dev.txt
python -m unittest discover -s tests
python scripts/validate_skills.py
```

The validator checks the skills under `skills/` and `internal/skills/`, and enforces this repository's front matter and reference-pointer conventions. It errors on a front matter field outside the Agent Skills specification; a pointer in `SKILL.md` written as a bare path outside a Markdown link; a pointer that fails to resolve; an orphaned reference file; a reference file that names another reference file by bare filename, breaking the one-level-deep rule; a front matter description containing a line break; a soft line break in a skill's or reference file's prose; a reference file or directory name outside the skill name format; a symlink, or a file other than `SKILL.md`, `attachments.yaml` and Markdown under `references/`; a file over 256 KiB or not valid UTF-8; more than 50 reference files; a path longer than 512 characters; a skill directory or front matter name equal to an id the Skills API reader reserves (`healthz`); a YAML anchor or alias in front matter; a front matter `license` that is missing or is not `CC-BY-4.0`; an `attachments.yaml` that is missing, malformed, or breaks the rules under "Graph attachments"; a `skills/categories.yaml` that is missing, malformed, or breaks the rules under "Categories"; a directory under either root whose name starts with `_`; a symlink, or a file other than `skills/categories.yaml`, directly under either root; `skills/`, `internal/` or `internal/skills/` being a symlink; anything under `internal/` other than `skills/`; a skill name that appears under both roots; a `shared-rules/` directory that is a symlink or holds anything other than non-empty UTF-8 `<rule-id>.md` files; and a marked copy of a shared rule that differs from its source, names a rule with no source, or leaves its markers unpaired, or a source that no skill copies. It warns, without failing, on a field outside what this repository documents and on a long reference file with no contents list.

## Repo map

| Repo           | What it is                                                                                                                             |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `dfo-dcp`      | The knowledge graph engine, ONE's fork of Data Commons, serving the graph and its mixer and SDMX APIs.                                 |
| `dfo-apis`     | The DFO's product APIs, Datasets and Search, served over the graph.                                                                    |
| `dfo-ai`       | The agent harness and the DFO's MCP servers, deployed as one Cloud Run service.                                                        |
| `dfo-spec-kit` | Shared spec models (spec-id hashing, materialisation, manifest and component-spec schemas), published for Python and TS [forthcoming]. |
| `dfo-website`  | The public Next.js site and the proxy that fronts the platform for external traffic.                                                   |
| `dfo-skills`   | This repo, the open repository of domain-knowledge packages agents load dynamically at runtime.                                        |
| `dfo-infra`    | Infrastructure as code: the Cloud Run service definitions, service accounts, scaling, and secrets.                                     |

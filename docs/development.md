# Maintainer notes

Detail for the ONE Data team that publishes these skills. A contributor to a skill needs only [CONTRIBUTING.md](../CONTRIBUTING.md), which has the format and the checks.

## How skills reach an agent

Each skill is registered as a node in the DFO knowledge graph, carrying its front matter and the links to the graph nodes its `attachments.yaml` declares. The DFO AI harness consumes that registry. Any other agent loads the skills through the install routes in [README.md](../README.md).

The DFO docs hub publishes each skill as a page, with one child page per reference file and its first heading as the title. Renaming or deleting a skill or a reference file changes or removes a published page's address with no redirect, so a link to the old page from elsewhere breaks.

dfo-pipelines publishes skill text to the knowledge graph, which drops line breaks and joins the words on either side of one. This is why each paragraph and list item in a skill sits on one line.

## Graph attachments

dfo-pipelines reads each skill's `attachments.yaml`, checks that every entry resolves, and links the skill to each node, leaving the file itself out of the graph.

- `applies_to` lists ontology nodes whose series the skill explains, such as `dcid:CRSPurposeCode930`.
- `sources` lists the provenance node of each dfo-pipelines export the skill explains as a whole, such as `dcid:provenance/OECDCreditorReportingSystem`. A data-source skill such as `oda-crs` attaches here, and so reaches every series that export publishes.

An attachment covers the node's descendants in the ontology's own hierarchy, so a parent code stands for its children. A node that every series of a source carries adds nothing over the source itself, so it is not worth attaching.

## Categories

The docs hub reads `skills/categories.yaml` to group the skill pages, and shows the categories, and the skills within each, in the file's order. A domain's name follows the skill name format, and the hub shows it in sentence case, so `sovereign-debt` appears as "Sovereign debt".

## Plugin and ChatGPT package

The repository root is one plugin, `dfo`. `.claude-plugin/plugin.json` names it and lists no components, so Claude and Codex load every directory under `skills/` as a skill and load nothing from `internal/skills/` or `template/`. `.claude-plugin/marketplace.json` offers that plugin to a user who adds the repository as a plugin marketplace, also named `dfo`. A new skill under `skills/` needs no change to either file.

The root `plugin.json` and `mcp.json` describe the same plugin for ChatGPT's plugin directory. `.mcp.json` connects the DFO MCP server in the Claude plugin.

When skills change, raise `version` in `plugin.json` and `.claude-plugin/plugin.json` together, since each directory publishes an update only under a new version. Then run the build script, which writes `dist/dfo-chatgpt-plugin.zip` for upload. It checks the listing against OpenAI's limits and the two manifests against each other, and writes nothing if a check fails.

```bash
python scripts/build_chatgpt_plugin.py
```

## CI

`.github/workflows/validate-skills.yml` runs the validator's tests and the validator on every push to `dev` or `main` and on every pull request once it is ready for review. A draft pull request runs no job.

The job also compiles the DFO ontology and fails an `applies_to` entry that is not a node in it. It installs the compiler from the public `DevelopmentFinanceObservatory/ontology` repository at the commit named by `DFO_ONTOLOGY_REF` in the workflow file. Move that commit to pick up ontology changes.

To run the ontology check locally, install the compiler at that commit, compile the ontology, and pass the result to the validator.

```bash
dfo-ontology compile --bench prod --output dfo.mcf
python scripts/validate_skills.py --ontology-mcf dfo.mcf
```

## What the validator enforces

`scripts/validate_skills.py` checks the skills under `skills/` and `internal/skills/`. It errors on:

- a front matter field outside the Agent Skills specification, a `license` that is missing or is not `CC-BY-4.0`, a description containing a line break, or a YAML anchor or alias;
- a skill directory or front matter name that is outside the skill name format, equal to an id the Skills API reader reserves (`healthz`), or present under both roots;
- a pointer in `SKILL.md` written as a bare path outside a Markdown link, a pointer that fails to resolve, an orphaned reference file, or a reference file that names another reference file by bare filename;
- a soft line break in the prose of a skill or reference file;
- a symlink, a file other than `SKILL.md`, `attachments.yaml` and Markdown under `references/`, a file over 256 KiB or not valid UTF-8, more than 50 reference files, or a path longer than 512 characters;
- an `attachments.yaml` that is missing, malformed, or breaks the attachment rules;
- a `skills/categories.yaml` that is missing, malformed, or breaks the category rules, including a directory under `skills/` that it leaves out;
- a directory under either root whose name starts with `_`, a file other than `skills/categories.yaml` directly under either root, `skills/`, `internal/` or `internal/skills/` being a symlink, or anything under `internal/` other than `skills/`.

It warns, without failing, on a front matter field outside what CONTRIBUTING.md documents and on a long reference file with no contents list.

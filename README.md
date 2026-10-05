# dfo-skills

The open repository of DFO skills: structured packages of development-finance domain knowledge that agents discover and load at runtime. A skill carries what a domain expert would bring to an analysis: definitions, methodological considerations, validation rules, analytical recipes. Skills are what make the agent actually good at development finance instead of generically ok at retrieval.

## Status

Ten skills cover ODA analysis: `oda-measures`, `oda-channels`, `oda-concepts`, `policy-markers`, `oda-dataset-selection`, and one skill per data source, `oda-dac1`, `oda-dac2a`, `oda-dac2b`, `oda-crs` and `oda-imputed-multilateral-sectors`. Skills carry context and methodology for an agent to build its own plan, rather than steps to follow, and agents find each one through its description. `oda-dataset-selection` covers which dataset answers a question, and each data-source skill carries the context for working with its dataset, including its double-counting and aggregation traps. An eleventh skill, `dfo-faq`, answers questions about the DFO platform itself: its sources, update cadence, citations and data privacy. `imf-weo` covers the IMF World Economic Outlook database. Debt analysis and health financing follow, alongside the registration and dynamic-loading mechanism these skills ride on. Sectoral skills and community contribution pathways come after launch.

## How skills reach an agent

Each skill is registered as a node in the DFO knowledge graph, carrying its front matter and the links to the graph nodes its `attachments.yaml` declares. The DFO AI harness consumes that registry at launch. After launch, any agent that can discover skills is a consumer, potentially through vendor-specific skill marketplaces. The exact delivery mechanism (how pointers to relevant skills reach an agent mid-task) is still being designed.

The DFO docs hub publishes each skill as a page, with one child page per reference file and its first heading as the title. Renaming or deleting a skill or a reference file changes a published page's address, so the dfo-docs build fails until its `redirects.yaml` declares where the old page went.

## Format

One directory per skill under `skills/`, named for the skill. Each holds a `SKILL.md` with YAML front matter, following the Agent Skills convention so agents outside the DFO can load these packages too. Two fields do the work:

- `name`, matching the directory name.
- `description`, the text discovery matches against. It says what expertise the skill carries and when an agent should load it.

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

Both keys are optional, and a missing key is an empty list, but the file is required: a skill that attaches nowhere holds `applies_to: []` and `sources: []`. Any other key, a duplicate entry, an entry of the wrong shape, or a YAML anchor or alias fails the validator. `skills/_template/attachments.yaml` is the copy to start from.

Attach a skill to an ontology node only when a series carrying that node would be misread without a section of the skill, and only when a minority of a source's series carry it. An attachment covers the node's descendants in the ontology's own hierarchy, so a parent code stands for its children. A node every series of a source carries adds no information over the source itself, so it is not worth attaching. A comment beside each entry gives the reason and names the reference file that covers it, so the attachment moves or goes with the material that justifies it.

## Checking a skill before you open a pull request

CI runs the same two commands on every push and pull request, and they run locally the same way. CI also compiles the DFO ontology and fails an `applies_to` entry that is not a node in it; the workflow reads the private `ONEcampaign/dfo-ontology` repository with a read-only token minted from the organisation's reader GitHub App. To run that check locally, compile the ontology with `dfo-ontology compile --bench prod --output dfo.mcf` and add `--ontology-mcf dfo.mcf` to the validator command.

```bash
pip install -r requirements-dev.txt
python scripts/validate_skills.py
```

The validator enforces this repository's front matter and reference-pointer conventions. It errors on a front matter field outside the Agent Skills specification; a pointer in `SKILL.md` written as a bare path outside a Markdown link; a pointer that fails to resolve; an orphaned reference file; a reference file that names another reference file by bare filename, breaking the one-level-deep rule; a front matter description containing a line break; a soft line break in a skill's or reference file's prose; a reference file or directory name outside the skill name format; a symlink, or a file other than `SKILL.md`, `attachments.yaml` and Markdown under `references/`; a file over 256 KiB or not valid UTF-8; more than 50 reference files; a path longer than 512 characters; a skill directory or front matter name equal to an id the Skills API reader reserves (`healthz`); a YAML anchor or alias in front matter; and an `attachments.yaml` that is missing, malformed, or breaks the rules under "Graph attachments". It warns, without failing, on a field outside what this repository documents and on a long reference file with no contents list.

## Repo map

| Repo           | What it is                                                                                                                             |
|----------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| `dfo-dcp`      | The knowledge graph engine, ONE's fork of Data Commons, serving the graph and its mixer and SDMX APIs.                                  |
| `dfo-apis`     | The DFO's product APIs, Datasets and Search, served over the graph.                                                                    |
| `dfo-ai`       | The agent harness and the DFO's MCP servers, deployed as one Cloud Run service.                                                        |
| `dfo-spec-kit` | Shared spec models (spec-id hashing, materialisation, manifest and component-spec schemas), published for Python and TS [forthcoming].  |
| `dfo-website`  | The public Next.js site and the proxy that fronts the platform for external traffic.                                                   |
| `dfo-skills`   | This repo, the open repository of domain-knowledge packages agents load dynamically at runtime.                                        |
| `dfo-infra`    | Infrastructure as code: the Cloud Run service definitions, service accounts, scaling, and secrets.                                     |



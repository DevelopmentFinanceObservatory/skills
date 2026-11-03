# DFO skills

Open-source domain-knowledge packages for AI assistants working with development-finance data. Each skill is a folder of plain-text method, definitions, and dataset caveats in the [Agent Skills](https://agentskills.io/specification) format, which an assistant loads when a question calls for it. They say which measure fits, what a dataset covers, and where its totals double count.

The skills are part of the [Development Finance Observatory](https://github.com/DevelopmentFinanceObservatory) (DFO), an initiative of [ONE Data](https://data.one.org) at the ONE Campaign. The DFO AI layer loads them at runtime, and you can load them in your own agent or in Claude.

This repository is under active development. Interfaces, schemas, and data may change without notice.

## What the skills cover

### Sources

- `oda-dac1`: OECD DAC1, donor totals of official development assistance (ODA) and other official flows.
- `oda-dac2a`: OECD DAC2A, ODA disbursements by donor and recipient.
- `oda-dac2b`: OECD DAC2B, other official flows and export credits by donor and recipient.
- `oda-crs`: the OECD Creditor Reporting System, ODA and other flows by activity.
- `oda-imputed-multilateral-sectors`: ONE's estimate of the sectors that core multilateral contributions reach.
- `debt-ids`: the World Bank's International Debt Statistics on external debt.
- `imf-weo`: the IMF World Economic Outlook, macroeconomic estimates and projections.

### Development assistance

- `oda-dataset-selection`: which dataset answers an ODA question.
- `oda-concepts`: core definitions, such as the 0.7% ODA/GNI target, Core ODA, and donor groupings.
- `oda-measures`: flow types, price bases, and how grants and loans count as ODA.
- `oda-channels`: bilateral, multilateral, and earmarked routes from donor to recipient.

### Sovereign debt

- `debt-concepts`: definitions that hold across sources, such as external debt, concessionality, and debt relief.
- `debt-profile`: what a country owes, to whom, on what terms, and what it pays each year.
- `debt-sustainability`: the IMF and World Bank frameworks, with the IMF's risk ratings for low-income countries.

## What you can ask

- "Should I use grant equivalents or gross disbursements to compare Japan's and France's ODA effort?" (`oda-measures`)
- "A country is rated at high risk of debt distress. Does that mean its debt is unsustainable?" (`debt-sustainability`)
- "Can I rank countries by last year's GDP growth using the World Economic Outlook?" (`imf-weo`)

## Use the skills

Every route below installs from this repository.

- Claude (web, desktop, and Cowork) installs every skill as one plugin, `dfo`, when you add this repository as a plugin marketplace, also named `dfo`.
- Claude Code installs the same plugin.

  ```text
  /plugin marketplace add DevelopmentFinanceObservatory/skills
  /plugin install dfo@dfo
  ```

- Codex installs the same plugin.

  ```bash
  codex plugin marketplace add DevelopmentFinanceObservatory/skills
  codex plugin add dfo@dfo
  ```

- Any other assistant that reads the Agent Skills format takes one skill at a time. Copy a folder from `skills/` into that assistant's skills directory, or zip it and upload it in the assistant's skills settings.

The plugin also connects the DFO MCP server at `https://developmentfinance.org/mcp`, which serves the data these skills explain. The skills themselves are text and work without it.

A plugin install updates from this repository. A copied folder or zip stays as it was on the day you took it.

## What's inside

- `skills/`: the skills offered for install, one folder each, plus `categories.yaml`, which groups them on the DFO docs site.
- `internal/skills/`: skills published on the DFO platform and left out of the install routes.
- `template/`: a working skill to copy when you start a new one.
- `scripts/` and `tests/`: the validator that CI runs on every skill, and the build script for the ChatGPT plugin package.
- `.claude-plugin/`, `plugin.json`, `mcp.json`, `.mcp.json`: the plugin manifests for Claude, Codex, and ChatGPT.

## Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md) covers the skill format and the checks to run before a pull request.
- [docs/development.md](docs/development.md) holds maintainer notes on how skills reach the DFO platform and how the plugin is versioned and released.

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

The code in `scripts/`, `tests/` and `.github/workflows/` is released under the MIT licence; see [LICENSE-CODE](LICENSE-CODE). Everything else, including the skills, is released under CC BY 4.0; see [LICENSE](LICENSE).

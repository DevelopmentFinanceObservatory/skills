# Development Finance Observatory skills

The Development Finance Observatory (DFO) skills give an AI assistant the methods a development-finance analyst brings to a question: which measure fits, what each dataset covers, and where its totals double count. They are Agent Skills, plain-text packages of method, definitions, and dataset caveats that an assistant loads when a question calls for them. The DFO team at ONE Campaign writes them.

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

## Install

Every route installs from `DevelopmentFinanceObservatory/skills`. The DFO docs site page "Use skills in your own agent" has the steps for each assistant.

- Claude (web, desktop, and Cowork) installs every skill as one plugin, `dfo`, when you add that repository as a plugin marketplace, also named `dfo`.
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

- ChatGPT, Gemini, and other assistants that read the Agent Skills format take one skill at a time, as a zip downloaded from the skill's page on the DFO docs site and uploaded in the assistant's skills settings.

## Updates

A plugin install updates from the repository. A zip is a copy from the day you downloaded it.

## Licence

The skills, their reference files, and this documentation are licensed under Creative Commons Attribution 4.0 International (CC BY 4.0), copyright ONE Campaign. The full text is in `LICENSE`.

## Contributing

`CONTRIBUTING.md` describes the skill format and the checks.

# Sector groupings

What this covers: ONE's sector definitions by CRS purpose code and where they depart from the raw CRS structure.

## Concepts and definitions

ONE's usual sector groupings are below. Each row contains the DAC sector code a grouping draws on and a three-digit purpose code beneath it. A CRS record's five-digit purpose code starts with that three-digit code, so a record coded 12220 (basic health care) falls under 122. Where a DAC sector has no subdivisions, such as 130 or 140, its sector and purpose codes are the same. A few CRS records carry only a heading-level code, such as 100 or 200, which falls outside every sector here, so those records count as unallocated.

| Sector name | Sector code | Purpose name | Purpose code |
| --- | --- | --- | --- |
| Education | 110 | Education, level unspecified | 111 |
| Education | 110 | Basic education | 112 |
| Education | 110 | Secondary education | 113 |
| Education | 110 | Post-secondary education | 114 |
| Health | 120 | Health, general | 121 |
| Health | 120 | Basic health | 122 |
| Health | 120 | Non-communicable diseases (NCDs) | 123 |
| Health | 130 | Population policies/programmes and reproductive health | 130 |
| Water supply and sanitation | 140 | Water supply and sanitation | 140 |
| Government and civil society | 150 | Government and civil society, general | 151 |
| Conflict, peace and security | 150 | Conflict, peace and security | 152 |
| Social infrastructure, protection and services | 160 | Other social infrastructure and services | 160 |
| Transport, storage and communications | 210 | Transport and storage | 210 |
| Transport, storage and communications | 220 | Communications | 220 |
| Energy | 230 | Energy policy | 231 |
| Energy | 230 | Energy generation, renewable sources | 232 |
| Energy | 230 | Energy generation, non-renewable sources | 233 |
| Energy | 230 | Hybrid energy plants | 234 |
| Energy | 230 | Nuclear energy plants | 235 |
| Energy | 230 | Energy distribution | 236 |
| Banking, financial services and business | 240 | Banking and financial services | 240 |
| Banking, financial services and business | 250 | Business and other services | 250 |
| Agriculture, forestry and fishing | 310 | Agriculture | 311 |
| Agriculture, forestry and fishing | 310 | Forestry | 312 |
| Agriculture, forestry and fishing | 310 | Fishing | 313 |
| Industry, mining and construction | 320 | Industry | 321 |
| Industry, mining and construction | 320 | Mineral resources and mining | 322 |
| Industry, mining and construction | 320 | Construction | 323 |
| Trade policies and regulations (incl. tourism) | 330 | Trade policies and regulations | 331 |
| Trade policies and regulations (incl. tourism) | 330 | Tourism | 332 |
| Environment protection | 410 | General environment protection | 410 |
| Multi-sector (incl. rural development) | 430 | Other multisector | 430 |
| General budget support | 510 | General budget support | 510 |
| Other (food aid and commodity assistance) | 520 | Development food assistance | 520 |
| Other (food aid and commodity assistance) | 530 | Other commodity assistance | 530 |
| Action relating to debt | 600 | Action relating to debt | 600 |
| Humanitarian | 720 | Emergency response | 720 |
| Humanitarian | 730 | Reconstruction relief and rehabilitation | 730 |
| Humanitarian | 740 | Disaster prevention and preparedness | 740 |
| Administrative costs of donors | 910 | Administrative costs of donors | 910 |
| Refugees in donor countries | 930 | Refugees in donor countries | 930 |
| Unallocated and unspecified | 998 | Unallocated/unspecified | 998 |

These groupings are ONE's analytical convention.

Health: ONE's health grouping combines DAC sectors 120 (health) and 130 (population policies and programmes, and reproductive health), and a request for "health" with no code is read as that grouping. Non-communicable diseases, including mental health, sit under 123, within 120. A request that names a code, such as "CRS 120", "basic health" (122) or "reproductive health" (130), is read as that code alone. Reading 120 alone leaves out 130, which gives a smaller number.

Humanitarian: a request for "humanitarian aid" with no code is read as ONE's humanitarian grouping, 720, 730 and 740 together. A request that names one of the three reads that code alone.

Users and other organisations often define sectors differently. A non-default definition changes the figures, so state the difference when comparing results across definitions.

## Pitfalls

- A sector definition that changes between calculations, such as 120 for one figure and 120 + 130 for another, makes the figures incomparable.
- Presenting ONE's groupings as official OECD definitions misstates their source.
- A sub-sector share, such as malaria within health, is calculated against the parent sector total, so dividing by total ODA gives a different and smaller figure.

## What makes a result verifiable

A sector result is verifiable when it lists the CRS codes that define each sector, notes any difference from ONE's usual grouping and the reason, and names the purpose codes and parent-sector denominator for any sub-sector share.

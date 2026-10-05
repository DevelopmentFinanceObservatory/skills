---
name: oda-dac2b
description: >-
  Context for working with the OECD DAC2B table, other official flows (OOF) and officially supported export credits by donor and recipient. Covers its measures, why bilateral donors' figures sit at regional or income-group level while country detail comes from multilateral lenders, and the double-counting traps with donor and recipient aggregates and nested measures. Load once DAC2B has been chosen for an analysis, or when working with DAC2B figures. For choosing between DAC datasets, use oda-dataset-selection.
---

# DAC2B: other official flows by recipient

## What it is

DAC2B reports other official flows (OOF) and officially supported export credits from each donor to each recipient country, region and income group. Donors include DAC countries, non-DAC reporters and multilateral lenders reporting their own non-concessional lending. Its measures are:

- OOF grants, loan disbursements, loan repayments, equity, interest received, offsetting entries for debt relief on OOF claims, and gross and net OOF
- Export credits gross, repayments and net, and offsetting entries for debt relief on export credit claims
- Official non-concessional flows, net, which combine OOF and export credits, and from 2023 also private sector instruments
- Private sector instruments, net

Values are in USD at current and constant prices.

## Reporting level

DAC2B publishes bilateral DAC donors' figures only against regional and income-group aggregates, such as sub-Saharan Africa, LDCs or ACP states, and country-level detail comes from multilateral lenders such as IBRD. A bilateral donor with no figure for a country has its flows to that country inside those aggregates.

The DAC countries total carries country-level OOF that no published individual donor accounts for, so a country total built by summing individual donors differs from the aggregate.

## Agreement with the CRS

The OECD compiles DAC2B from donors' CRS reporting, so the two agree for multilateral lenders and for donor totals across all developing countries. Beyond the country detail that DAC2B holds back for bilateral donors, which the CRS shows, they disagree in three places. Some donors' OOF appears in DAC2B with no matching CRS records, Japan's being the largest case. DAC2B's gross OOF is net of amounts received back on grants and leaves out guarantees, both of which CRS OOF records keep. Export credits appear in DAC2B but not as CRS records.

## Double counting and aggregates

Donors and recipients both come as individual entries and as aggregates, and a sum that includes an aggregate alongside its members double counts.

- Donor aggregates are official donors (DAC countries, non-DAC countries and multilaterals), DAC countries, DAC countries plus EU Institutions, DAC EU countries, DAC EU countries plus EU Institutions, the G7, non-DAC countries, other countries and multilaterals. Multilaterals also split into sub-aggregates (the UN, the World Bank, the World Bank Group, regional development banks and others) that overlap one another and the multilaterals total.
- Recipient aggregates are regions, income groups, other country groups, the developing countries total, multilateral recipients and all recipients. Regions overlap (Africa contains Northern Africa and Sub-Saharan Africa, and Sub-Saharan Africa overlaps Eastern, Middle, Southern and Western Africa), and most regions have an "unspecified" bucket for amounts not allocated to a country. Income groups come in DAC and World Bank classifications. Other country groups (LDCs, SIDS, LLDCs, HIPCs, ACP states, fragile contexts and basin groupings) cut across regions and income groups.

A regional total built from individual countries misses the region's unspecified bucket.

The measures include gross and net totals alongside their components. Net OOF is gross OOF minus repayments, and official non-concessional flows combine OOF, export credits and, from 2023, private sector instruments. Adding measures across levels counts flows twice.

Total official flows to a recipient are its ODA plus its OOF. Export credits include privately extended credits and sit outside that total.

## Particularities

Net flows to a recipient are negative in years when repayments exceed new lending.

Export credits are counted at face value.

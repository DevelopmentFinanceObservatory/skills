---
name: oda-crs
description: >-
  Context for working with the OECD Creditor Reporting System (CRS), the activity-level dataset of ODA, OOF, private sector instruments and private philanthropy reported by bilateral providers, multilateral organisations and foundations. Covers its attributes, coverage by year and against DAC1, the flow categories and bilateral/multilateral flags, the April 2026 core contribution records and their treatment in the DFO, and the double-counting traps with multilateral outflows, foundation funding and regional buckets. Load once the CRS has been chosen for an analysis, or when working with CRS records. For choosing between DAC datasets, use oda-dataset-selection.
license: CC-BY-4.0
---

# Creditor Reporting System (CRS)

## What it is

The CRS is the OECD's activity-level database. Each record is a project, programme, or contribution reported by a provider. Reporters are DAC members, non-DAC countries that report to the DAC, multilateral organisations reporting their own outflows, and private foundations such as the Gates Foundation.

The main attributes are year, provider and agency, recipient country or region, purpose and sector, channel of delivery, aid type, finance type, flow category, commitment and disbursement amounts, grant equivalent, loan terms, policy markers, and text descriptions. Purposes roll up into sectors.

Amounts are provided in USD at current prices and at constant prices, deflated with the provider's own deflator. Multilaterals use the total DAC deflator. The constant-price base year moves with each release. Commitments and gross disbursements are reported at face value, and loan repayments are recorded separately. Grant equivalents exist for ODA flows and ODA-eligible private sector instruments from 2018.

## Coverage against DAC1

DAC1 is the authoritative total, and CRS totals will not match it exactly. The OECD measures CRS coverage against donors' DAC reporting, and some items are reported in aggregate in the CRS (administrative costs, scholarships, small technical co-operation). Historic gaps are larger.

- Commitments cover about 70% in 1995, over 90% in 2000, and nearly 100% from 2003.
- Disbursements cover less than 60% before 2002, around 90% from 2002, and nearly 100% from 2007. The OECD advises against using CRS disbursements for flows before 2002.
- Records start in 1973, and pre-1995 data are incomplete.
- Aid type was introduced for 2010 flows, and earlier years are partly back-mapped and incomplete.

## Distinctions that decide what a total means

The flow category separates the kinds of money: ODA, OOF other than export credits, officially supported export credits, private development finance from foundations, private sector instruments, private foreign direct investment, and other private flows at market terms. Private sector instruments are a separate category that an ODA total includes only by choice.

A bilateral/multilateral flag separates who controls the money.

- Bilateral flows
- Core contributions to multilateral organisations, recorded as inflows to the multilateral
- Core contributions to NGOs, other private bodies and public-private partnerships
- Multilateral outflows, reported by multilateral agencies only
- Private grants, reported by DAC members and private providers
- Ex-post reporting on NGO activities funded through core contributions
- Triangular co-operation

Aid type also flags core funding. Its core categories are support to NGOs and research institutes, contributions to multilateral institutions (B021), and contributions to global funds (B022). The last two were one category (B02) before 2022. Earmarked funding through multilaterals is bilateral. Its channel of delivery is a multilateral organisation, and it can carry any aid type, including projects, specific-purpose programmes, and pooled funds.

## Double counting and aggregates

Since the April 2026 release, the CRS includes providers' core contributions to multilaterals as records flagged as multilateral inflows. The OECD says these records must be excluded to calculate bilateral flows and avoid double counting.

The CRS in the DFO knowledge graph has these records filtered out. CRS data drawn directly from the OECD include them, so exclude them before building a bilateral total.

A provider's core contribution to a multilateral and the multilateral's own outflows are the same money, just at two different points in time. A total across all reporters that keeps both counts it twice. Donor-side totals retain the contribution, and recipient-side and sector-wide totals retain the outflow.

Multilateral reporters include only core-funded activities in the CRS, so earmarked trust funds reported by a bilateral provider do not reappear as the multilateral's outflow. Foundation grants to Gavi or the Global Fund are private flows that then fund those organisations' outflows. A total that adds foundations and multilaterals counts that money twice.

Recipients include regional and unspecified buckets alongside countries, such as "developing countries, unspecified" and "South of Sahara, regional". A sum over a region from the CRS adds the region's own regional and unspecified buckets, and those of its sub-regions, to its countries. A listing or ranking of the region's countries counts members only. A country figure that includes a share of a regional or unspecified amount rests on an assumption about how that amount was spread.

## Particularities

Commitments are lumpy. A multi-year programme is committed in one year and disbursed over several, so commitment series jump and disbursement series lag.

The purpose list grows over time. COVID-19 control is one example. A subsector series can start mid-way through a time range. Broad sector totals include multisector and unallocated purposes, which are part of the total and belong to no single sector.

Policy markers (gender, climate, biodiversity, and others) are scored per activity. A significant-objective score counts the whole activity amount, and blank scores mean the activity was not screened. A share computed over all activities, screened and unscreened together, understates the marked share. The CRS in the DFO knowledge graph carries no policy markers, so a question that depends on them, such as climate- or gender-tagged ODA, needs another source.

Private sector instruments reported under the instrument approach, where each loan, equity stake, or guarantee to a company is recorded, appear in the CRS with a recipient and sector. Under the institutional approach, which records capital injections to development finance institutions, the money has no specific recipient country or sector.

CRS data are revised between annual releases. New reporters are added and records corrected, so results depend on the release.

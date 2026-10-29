---
name: oda-dac2a
description: >-
  Context for working with the OECD DAC2A table, ODA disbursements by donor and recipient country or region. Covers its measures, multilateral agencies reporting as donors and appearing as recipients, how its totals reconcile with DAC1, the OECD's imputed multilateral ODA by recipient, and the double-counting traps with donor and recipient aggregates, EU aggregates and imputed figures. Load once DAC2A has been chosen for an analysis, or when working with DAC2A figures. For choosing between DAC datasets, use oda-dataset-selection.
license: CC-BY-4.0
---

# DAC2A: ODA disbursements to countries and regions

## What it is

DAC2A reports ODA disbursements from each donor to each recipient country, region, and income group. It holds gross ODA, net ODA, and their components (grants, loans, debt relief, technical co-operation, humanitarian aid, and others). All values are disbursements in USD at current and constant prices.

Donors include DAC countries, non-DAC reporters, multilateral agencies reporting their own outflows (such as IDA, the regional development banks, UN agencies, Gavi, and the Global Fund), and private foundations.

The table also carries recipient-side indicators, ODA per capita, and ODA as a percentage of the recipient's GNI.

## Totals against DAC1

At the developing countries total, a donor's DAC2A net ODA equals its DAC1 bilateral ODA in net disbursements. In-donor refugee costs, administrative costs, and similar items sit in "developing countries, unspecified", so the sum of individual countries is lower than DAC1 bilateral ODA, and much lower for donors with high refugee costs.

DAC2A is provided on a cash basis. Its net ODA subtracts loan repayments, so it will not match the grant-equivalent headline in DAC1 for years from 2018.

Net disbursements are the default measure for a recipient's all-sector total from any donors, because they are the receipts the recipient gets after repayments. A sector, a channel, a CRS type of finance (instrument), or a cooperation modality is not published here and takes gross disbursements from the CRS. The components listed above (grants, loans, debt relief, and the others) are DAC2A's own aid types, which are a different cut.

## Imputed multilateral ODA

Imputed multilateral ODA is the OECD's estimate of how much of each donor's core multilateral contributions reached each recipient. It is published for DAC countries, non-DAC countries, and EU Institutions. It takes each agency's geographical breakdown of its gross disbursements from core resources in the reference year and applies that breakdown to the donor's core contributions to the agency. It is a memo item, outside net ODA, and it does not sum to DAC1 multilateral ODA.

<!-- shared:dac2a-named-donor-to-recipient -->

A named donor's total to a named recipient, with no sector, is DAC2A total ODA in net disbursements, which counts bilateral flows only. The bilateral-plus-imputed sum applies only when the user asks for the donor's contribution through multilateral channels as well.

<!-- /shared:dac2a-named-donor-to-recipient -->

Bilateral net ODA plus imputed multilateral ODA is the DAC's measure of a donor's total contribution to a recipient. When you build a figure on this convention from DAC2A, say in the reply that the bilateral part is net and why: "net bilateral, as DAC counts a donor's total contribution". A total for a named donor read from the CRS is counted in gross disbursements, so it differs in basis from this sum. The OECD figure attributes core contributions to recipients, while ONE's imputed multilateral sectors dataset attributes them to sectors with a different method, so the two do not reconcile.

## Double counting and aggregates

Donors and recipients are provided as both individual entries and aggregates, and a sum that includes an aggregate alongside its members double counts.

- Donor aggregates are official donors (DAC countries, non-DAC countries, and multilaterals), DAC countries, DAC countries plus EU Institutions, DAC EU countries, DAC EU countries plus EU Institutions, the G7, non-DAC countries, other countries, multilaterals, and private donors. Multilaterals also split into sub-aggregates (the UN, the World Bank, the World Bank Group, regional development banks, and others) that overlap one another and the multilaterals total.
- Recipient aggregates are regions, income groups, other country groups, the developing countries total, and all recipients. Regions overlap (Africa contains Northern Africa and Sub-Saharan Africa, and Sub-Saharan Africa overlaps Eastern, Middle, Southern, and Western Africa), and most regions have an "unspecified" bucket for amounts not allocated to a country. Other country groups (SIDS, LLDCs, HIPCs, ACP states, fragile contexts, basin groupings, and more advanced developed countries) cut across regions and income groups. Income groups (LDCs, other low-income, lower-middle-income, and upper-middle-income countries, and unallocated by income) come in DAC and World Bank classifications. The developing countries total includes "developing countries, unspecified", and all recipients equals the developing countries total plus multilateral recipients.

Multilateral agencies appear as both recipients and donors. Multilateral recipients hold donors' core contributions to IDA, UNICEF, EU Institutions, and others. A total that counts money going into multilaterals and money they provide to developing countries counts it twice.

The two aggregates that add EU Institutions to member states (DAC countries plus EU Institutions, and DAC EU countries plus EU Institutions) contain both the members' contributions to EU Institutions and EU Institutions' own ODA. The members' contributions sit under multilateral recipients, so to the developing countries total these aggregates count EU money once. To all recipients they count it twice.

<!-- shared:official-donors-total -->

A recipient question that leaves donors unnamed ("flows to Kenya", "what Kenya receives") reads as the OECD's official donors total, which sums DAC countries, non-DAC countries, and multilaterals and is the recipient's total receipts from official donors. State that reading in the answer, and offer the donors listed one by one as the other reading.

<!-- /shared:official-donors-total -->

Private donors sit outside the official donors total. A question about "all donors" adds the private donors' total, which DAC2A publishes from 2009, so before 2009 it holds official donors alone. The DAC countries total that DAC1 reads for unnamed donors applies to donor-side questions answered from DAC1.

A recipient's total receipts are the sum of bilateral donors and multilateral donors. Adding a donor's imputed multilateral ODA to the multilateral agencies' own outflows counts the same money twice.

A regional total built from individual countries misses the region's unallocated-by-country buckets.

<!-- shared:oecd-region-readings -->

Nine regions have an OECD reading: sub-Saharan Africa, North Africa, East Africa, Middle Africa, West Africa, Asia, Europe, the Middle East, and South America. A sum over one of them counts the OECD's member list for the region and adds the region's own regional and unspecified buckets, and those of its sub-regions. The other reading is the region on the UN's list, with the Middle East read as the UN's Western Asia. The two lists differ for six of the nine. Sudan sits in the OECD's sub-Saharan Africa and East Africa, and in the UN's North Africa. The OECD's Asia leaves out Cyprus, Japan, and Türkiye. The OECD's Europe holds only the 13 European countries eligible for ODA. The OECD's Middle East holds Iran, and the UN's Western Asia holds Armenia, Azerbaijan, Cyprus, Georgia, and Türkiye. Middle Africa, West Africa, and South America hold the same countries on both lists. Any other region counts its countries on the UN's list and adds the buckets the OECD keys to that region, as Africa and Oceania do. East Asia and South Asia count the UN's countries alone, because the OECD's Far East Asia and South and Central Asia hold different countries. A listing or ranking of a region's countries counts the countries on the UN's list, with no buckets.

The OECD names North Africa "North of Sahara" and sub-Saharan Africa "South of Sahara". Africa takes the buckets of Africa and of Eastern, Middle, North of Sahara, South of Sahara, Southern, and Western Africa, and sub-Saharan Africa takes those of Eastern, Middle, South of Sahara, Southern, and Western Africa.

<!-- /shared:oecd-region-readings -->

## Particularities

Net ODA can be negative for a donor-recipient pair when loan repayments or debt-relief offsets exceed new disbursements.

The DAC list of ODA recipients changes as countries graduate, and historical data include a separate group of countries in transition. A long series for one recipient can stop, and aggregate recipient totals shift as countries join or leave the list.

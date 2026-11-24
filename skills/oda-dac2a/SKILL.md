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

At the developing countries total, a donor's DAC2A net ODA equals its DAC1 bilateral ODA in net disbursements. In-donor refugee costs, administrative costs, and similar items sit in "developing countries, unspecified", labelled "Bilateral, unallocated (DAC)" in the DFO, so the sum of individual countries is lower than DAC1 bilateral ODA, and much lower for donors with high refugee costs.

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

- Donor aggregates are official donors (DAC countries, non-DAC countries, and multilaterals), DAC countries, DAC EU members, DAC EU members and EU institutions, the G7, non-DAC countries, other donor countries, multilaterals, and private donors. Multilaterals also split into sub-aggregates (the UN, the World Bank, the World Bank Group, regional development banks, and others) that overlap one another and the multilaterals total.
- Recipient aggregates are regions, income groups, other country groups, the developing countries total, and all recipients. Regions overlap (Africa contains Northern Africa and Sub-Saharan Africa, and Sub-Saharan Africa overlaps Eastern, Middle, Southern, and Western Africa), and most regions have an "unspecified" bucket for amounts not allocated to a country. Other country groups (SIDS, LLDCs, HIPCs, ACP states, fragile contexts, basin groupings, and more advanced developing countries and territories) cut across regions and income groups. Income groups (LDCs, other low-income, lower-middle-income, and upper-middle-income countries, and unallocated by income) come in DAC and World Bank classifications. The developing countries total includes "developing countries, unspecified", labelled "Bilateral, unallocated (DAC)" in the DFO, and all recipients equals the developing countries total plus multilateral recipients.

Multilateral agencies appear as both recipients and donors. Multilateral recipients hold donors' core contributions to IDA, UNICEF, EU Institutions, and others. A total that counts money going into multilaterals and money they provide to developing countries counts it twice.

For the total ODA of one donor or one donor aggregate across recipients, or a list of its recipients, read the developing countries total, labelled "developing countries (DAC)" in answers, and the countries, territories, and unallocated buckets under it. Leave out the regions, income groups, and other country groups under it, which hold the same money again. A ranking by region or by income group follows the ranking rules below. State that reading in the answer, and name the figure by the measure it reads, such as net ODA or gross ODA.

For a DAC country, a non-DAC country, or EU Institutions, and for five aggregates of these donors alone (DAC countries, the G7, DAC EU members, non-DAC countries, and other donor countries, a residual group of donor countries), the developing countries total is the donor's bilateral ODA, and its net ODA there equals DAC1 bilateral ODA in net disbursements. Name the figure as the donor's bilateral ODA, and offer all recipients as another reading and, for net ODA, the bilateral-plus-imputed sum. Build the bilateral-plus-imputed sum by adding the donor's imputed multilateral ODA to its net ODA at "developing countries (DAC)". When the imputed figure is available only at "all recipients (DAC)", take only the imputed figure from there, keep the net ODA at "developing countries (DAC)", and say in the answer that the imputed part is read at all recipients. The imputed figure is the same at both totals. Read an aggregate's imputed figure under the aggregate's own name, such as "DAC EU members", since a sum of its members can differ from the OECD's figure for the aggregate. When the imputed figure is missing for the donor, or for any donor in a sum of donors, offer no bilateral-plus-imputed sum, and say which imputed figures are missing. All recipients is the developing countries total plus the donor's core contributions to multilateral agencies. The imputed figure spreads those same contributions across recipients, so adding the imputed figure to the donor's ODA at all recipients counts the contributions twice.

The aggregate that adds EU Institutions to member states, DAC EU members and EU institutions, contains both the members' contributions to EU Institutions and EU Institutions' own ODA. The members' contributions sit under multilateral recipients, so the developing countries total counts EU money once and all recipients counts it twice. For this aggregate, read the developing countries total, name it as the members' bilateral ODA plus EU Institutions' own ODA, and offer neither all recipients nor the bilateral-plus-imputed sum. The members' imputed figures spread their contributions to EU Institutions across recipients as well, so the bilateral-plus-imputed sum also counts EU money twice.

For a multilateral donor other than EU Institutions, such as IDA or the African Development Fund, the developing countries total is the agency's own ODA, and no imputed multilateral ODA is published for the agency. For official donors, or any aggregate that includes multilaterals, except DAC EU members and EU institutions, the developing countries total sums the members' bilateral ODA and the multilaterals' own ODA. For a multilateral, official donors, or such an aggregate, name the figure as the donors' own ODA to developing countries. All recipients for such an aggregate adds the members' core contributions to multilaterals, which the multilaterals' own ODA spends again, so all recipients counts that money twice.

For a private donor, such as the Gates Foundation, or the private donors total, the developing countries total is the donor's own disbursements. DAC2A files these disbursements under its ODA aid type, while the DAC counts them as private development finance, outside ODA. Name the figure as the donor's private development finance in the measure it reads, such as net disbursements, and say that the DAC does not count it as ODA.

<!-- shared:recipient-country-ranking -->

A ranking of recipients ranks the countries and territories among them, whether the ODA is one donor's or a donor total. The recipients also include amounts not allocated to a country, which the DFO tags with the entity type `DACRecipientUnallocatedByCountry`, such as "Bilateral, unallocated (DAC)" and "South of Sahara, unallocated by country (DAC)". In a ranking of countries, leave every recipient of that type out, state in the answer that the ranking leaves them out, and give the combined amount of the buckets inside the ranking's scope: every bucket for a ranking across all recipients, and the buckets the OECD region readings add to a region for a ranking within that region. A ranking by region, unless the question names the regions, ranks Africa, America, Asia, Europe, and Oceania, each read as the OECD region readings in this skill set out. Each region's line keeps the buckets those readings add to it, and "Bilateral, unallocated (DAC)" goes on a line of its own, since it belongs to no region.

<!-- /shared:recipient-country-ranking -->

In DAC2A, a ranking of recipients with no donor named reads the official donors total. State that reading in the answer. A ranking by income group, for one donor or a donor total, ranks the DAC income groups (LDCs, other low-income, lower-middle-income, and upper-middle-income countries) and gives unallocated by income on a line of its own. State that reading in the answer, and offer the World Bank classification as the other reading.

<!-- shared:official-donors-total -->

A recipient question that leaves donors unnamed ("flows to Kenya", "what Kenya receives"), or calls them major, main, or big donors without ranking them ("how much do the major donors provide to Ethiopia?"), reads as the OECD's official donors total, which sums DAC countries, non-DAC countries, and multilaterals and is the recipient's total receipts from official donors. State that reading in the answer, and offer the top 10 donors to the recipient by latest year as the other reading. A question that ranks the donors ("top donors to Ethiopia") lists them.

<!-- /shared:official-donors-total -->

Private donors sit outside the official donors total. A question about "all donors" adds the private donors' total, which DAC2A publishes from 2009, so before 2009 it holds official donors alone. Name that sum as official donors' ODA plus private donors' development finance. The DAC countries total that DAC1 reads for unnamed donors applies to donor-side questions answered from DAC1.

A recipient's total receipts are the sum of bilateral donors and multilateral donors. Adding a donor's imputed multilateral ODA to the multilateral agencies' own outflows counts the same money twice.

A regional total built from individual countries misses the region's unallocated-by-country buckets.

<!-- shared:oecd-region-readings -->

Nine regions have an OECD reading: sub-Saharan Africa, North Africa, East Africa, Middle Africa, West Africa, Asia, Europe, the Middle East, and South America. A sum over one of them counts the OECD's member list for the region and adds the region's own regional and unspecified buckets, and those of its sub-regions. The other reading is the region on the UN's list, with the Middle East read as the UN's Western Asia. The two lists differ for six of the nine. Sudan sits in the OECD's sub-Saharan Africa and East Africa, and in the UN's North Africa. The OECD's Asia leaves out Cyprus, Japan, and Türkiye. The OECD's Europe holds only the 13 European countries eligible for ODA. The OECD's Middle East holds Iran, and the UN's Western Asia holds Armenia, Azerbaijan, Cyprus, Georgia, and Türkiye. Middle Africa, West Africa, and South America hold the same countries on both lists. Any other region counts its countries on the UN's list and adds the buckets the OECD keys to that region and to its sub-regions, as Africa, America, and Oceania do. East Asia and South Asia count the UN's countries alone, because the OECD's Far East Asia and South and Central Asia hold different countries. A listing or ranking of a region's countries counts the countries on the UN's list, with no buckets.

The OECD names North Africa "North of Sahara" and sub-Saharan Africa "South of Sahara". Africa takes the buckets of Africa and of Eastern, Middle, North of Sahara, South of Sahara, Southern, and Western Africa, and sub-Saharan Africa takes those of Eastern, Middle, South of Sahara, Southern, and Western Africa. America takes the buckets of America, Caribbean and Central America, Caribbean, Central America, and South America. Asia takes those of Asia, Far East Asia, the Middle East, South and Central Asia, South Asia, and Central Asia. Europe takes those of Europe and the States of the former Yugoslavia. Oceania takes those of Oceania, Melanesia, Micronesia, and Polynesia.

<!-- /shared:oecd-region-readings -->

## Particularities

Net ODA can be negative for a donor-recipient pair when loan repayments or debt-relief offsets exceed new disbursements.

The DAC list of ODA recipients changes as countries graduate, and historical data include a separate group of countries in transition. A long series for one recipient can stop, and aggregate recipient totals shift as countries join or leave the list.

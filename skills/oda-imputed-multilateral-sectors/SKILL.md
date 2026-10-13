---
name: oda-imputed-multilateral-sectors
description: >-
  Context for working with ONE's imputed multilateral sectors dataset, which estimates how much of each provider's core (unearmarked) contributions to multilateral organisations reached each sector and recipient. Covers how the estimate is built from Multisystem core contributions and multilaterals' CRS spending, its dimensions and price basis, how it relates to the OECD's imputed multilateral ODA and the discontinued OECD sectoral method, how contributions with borrowed or no shares are published, and the double-counting traps when combining it with bilateral CRS data or multilateral outflows. Load once this dataset has been chosen for an analysis, or when working with its figures. For choosing between datasets, use oda-dataset-selection.
license: CC-BY-4.0
---

# ONE imputed multilateral sectors

## What it is

The dataset estimates how much of each provider's core multilateral ODA reached each sector and recipient. Core contributions carry no sector or recipient, because the multilateral pools them with other providers' money and decides how to spend them. The estimate spreads each provider's core contribution to a multilateral based on the way that multilateral spent its own resources.

Two datasets go in. Each provider's core ODA contributions to each multilateral in year n come from the OECD Multisystem database. Each multilateral's shares by recipient and purpose come from its own CRS spending, pooled over years n, n-1 and n-2. The imputed amount is the contribution times the share, summed across multilaterals.

Figures are by year, provider, recipient, and purpose, from 2011, the first year Multisystem covers. All values are modelled estimates in gross disbursements at current USD. The dataset has no channel dimension, so it gives the total across all multilaterals and does not show which multilateral a given amount passed through.

The shares pool ODA and OOF spending, following past OECD practice. The amount imputed back to a provider is still only its ODA contribution.

The public methodology is at https://docs.one.org/methodologies/data/oda/imputed-multilateral-sectors/.

## Relation to other estimates

The OECD's imputed multilateral ODA in DAC2A attributes each donor's core contributions to recipients using each agency's spending in the reference year alone. ONE's dataset pools three years and adds the sector, so the two give different figures for the same provider and recipient.

ONE's method follows the OECD's discontinued sectoral imputations, which used commitments, and uses gross disbursements instead. A few donors publish their own imputations, such as the United Kingdom, and France for some sectors. Those cover single donors and use their own methods, so they are not comparable across donors or with ONE's figures.

## Particularities

The figures assume a provider's core money is spent in the same proportions as the multilateral's whole portfolio. Multilateral outflows in a year rarely match that year's core inflows because of reporting delays, gaps in multilateral reporting, grants turned into loans, and pooling rules.

A value is dated to the year of the contribution, while its sector mix comes from the three years up to that year. A value for year n can change when the CRS is revised for years n-1 or n-2, with no change in the contribution itself.

Matching Multisystem organisations to CRS reporters uses a reviewed list, because the two databases identify organisations differently. Not every core contribution gets the multilateral's own current shares.

- Most core money uses the multilateral's own shares for the three years ending in that year.
- A multilateral that has stopped reporting, or whose latest CRS data lag the contributions, uses its most recent three years with data, up to five years old.
- A sub-fund with no CRS reporting of its own borrows a related multilateral's shares. IDA's Multilateral Debt Relief Initiative uses IDA's ordinary lending mix, which is a judgement call, since treating that money as debt relief is also defensible. UN peacekeeping core contributions go entirely to the peacekeeping purpose, published against the recipient "Bilateral, unallocated/unspecified".
- Core money with no usable share is published against the recipient "Bilateral, unallocated/unspecified" and the purpose "Unallocated/unspecified". It is mostly UN bodies with no CRS-reporting peer (general UN core contributions, OCHA, UNESCO) and IFC.

A provider's total across the dataset equals its core contributions in Multisystem, unallocated money included. A sum over named sectors leaves out the unallocated money and understates the provider's multilateral ODA.

Pooling ODA and OOF in the shares matters for IBRD, EBRD, and IDB Invest, which report only OOF to the CRS. IFC has no usable share on either basis.

A sum with bilateral figures holds only when both sides are on the same price basis.

## Double counting and aggregates

A provider's full sector picture is its bilateral ODA to the sector from the CRS plus its imputed multilateral aid to the sector. That sum holds only if the bilateral side excludes the CRS records of core contributions to multilaterals, which are the input this dataset spreads. The CRS in the DFO knowledge graph already excludes them.

Earmarked (bi-multi) contributions are already accounted for in bilateral ODA with their own sectors. Imputing them again counts the money twice.

The dataset restates each provider's contributions. A total for a recipient or a sector across all providers comes from the CRS alone, where the multilaterals' outflows already count that money. Adding imputed figures to such a total counts it twice.

EU Institutions are a DAC member and can appear as a provider with their own core contributions. EU member states' contributions to the EU budget and the European Development Fund are core multilateral ODA, so the members' imputed figures already include a share of EU spending. Adding EU Institutions' figures to the members' figures in one total double counts.

## Pitfalls

Reading an imputed share as the provider's choice. A provider that gives heavily to IDA inherits IDA's sector mix. The result describes where the multilateral system spends the provider's money. The provider did not direct it.

# IDS series codes

What this covers: how World Bank IDS series codes are built, what each code segment means, and the codes that cover less debt, or a narrower creditor set, than their names suggest.

## Contents

- How a code is built
- What is measured
- Debt aggregates and components
- Creditors
- Debtor sectors, denominators and units
- Code-level traps
- Codes in the DFO

## How a code is built

A series code is a sequence of dot-separated segments. The first names the topic, and DT covers external debt. Context series use other prefixes, such as NY.GNP.MKTP.CD for GNI and BX.GSR.TOTL.CD for exports of goods, services and primary income. The second segment says what is measured, the third names the debt aggregate, component or creditor, an optional fourth gives a debtor sector or a ratio denominator, and the last gives the unit.

- DT.DOD.DECT.CD is the stock of total external debt in current US dollars.
- DT.AMT.BLAT.CB.CD is principal repaid by the central bank to bilateral creditors.
- DT.TDS.DECT.EX.ZS is total debt service as a percentage of exports.
- DT.GRE.DPPG is the average grant element on new PPG commitments, a three-segment code with no unit segment.

## What is measured

| Code | Meaning |
| --- | --- |
| DOD | Debt outstanding and disbursed (stock) |
| DIS | Disbursements |
| AMT | Principal repayments (amortisation) |
| INT | Interest payments |
| TDS | Debt service (principal plus interest) |
| NFL | Net flows (disbursements minus principal) |
| NTR | Net transfers (net flows minus interest) |
| COM | Commitments |
| UND | Undisbursed debt |
| AXA, IXA | Principal arrears, interest arrears |
| AXR, IXR | Principal rescheduled, interest rescheduled (capitalised) |
| AXF, IXF | Principal forgiven, interest forgiven |
| DXR, TXR | Debt stock rescheduled, total amount rescheduled |
| DFR, DSB, DSF | Debt forgiveness or reduction, debt buyback, debt stock reduction |
| INR, MAT, GPA, GRE | Average interest rate, maturity, grace period and grant element on new commitments |
| CUR | Currency composition of PPG debt |

## Debt aggregates and components

| Code | Meaning |
| --- | --- |
| DECT | Total external debt |
| DLXF | Long-term external debt |
| DLTF | Long-term external debt plus IMF credit |
| DPPG | Public and publicly guaranteed (PPG) debt |
| PRPG | Private debt guaranteed by the public sector, part of PPG |
| DPNG | Private non-guaranteed (PNG) debt |
| DSTC | Short-term debt |
| DIMF | Use of IMF credit, including SDR allocations for stocks |
| DSDR | IMF SDR allocations |
| PUBS, PRVS | Long-term debt of the public sector, of the private sector |
| DECB, DEGG, DEPS, DOPS | PPG debt of the central bank, general government, public sector, other public sector |
| ALLC | Concessional debt |
| VTOT, VPPG | Variable-rate debt, total and PPG |
| PVLX | Present value of external debt |

## Creditors

| Code | Meaning |
| --- | --- |
| OFFT | Official creditors (bilateral plus multilateral), PPG |
| BLAT, BLTC | Bilateral creditors, and their concessional part, PPG |
| MLAT, MLTC | Multilateral creditors, and their concessional part, PPG |
| PRVT | Private creditors (bonds, commercial banks and other private), PPG |
| PBND, PCBK, PROP | Bondholders, commercial banks, other private creditors, PPG |
| PNGB, PNGC | PNG debt to bondholders, PNG debt to commercial banks and other creditors |
| MIBR, MIDA, IDAG | IBRD, IDA, IDA grants |
| IMFC, IMFN | IMF concessional and non-concessional credit |
| NEBR, NIFC | EBRD and IFC lending to the private sector, PNG |
| RDBC, RDBN, MOTH | Regional development banks, concessional and non-concessional, and other multilaterals |

Currency codes after CUR name the currency of denomination, such as USDL (US dollar), EURO, JYEN (yen), SDRW (SDR), MULC (multiple currencies) and OTHC (other currencies), plus legacy currencies such as DMAK and FFRC.

## Debtor sectors, denominators and units

A fourth segment before the unit names the PPG debtor sector, CB (central bank), GG (general government), OPS (other public sector), PS (public sector) or PRVG (private sector with a public guarantee), or a ratio denominator, GN (GNI) or EX (exports of goods, services and primary income). PC marks a per capita figure, and US marks IMF credit excluding SDR allocations, as in DT.DOD.DIMF.US.CD.

The last segment is the unit. CD is current US dollars, ZS a percentage, and CG an annual change. Some context codes add DT after the unit, as in BX.GRT.TECH.CD.DT, marking the version compiled for the debt statistics. Codes for average terms have no unit segment, and their names give the unit (years for maturity and grace period, percent for interest rate and grant element).

## Code-level traps

Total external debt (DECT) has no disbursement or principal repayment series. Gross flows exist for long-term debt (DLXF), long-term debt plus IMF credit (DLTF), PPG, PNG and IMF credit, and short-term debt has only a net flow. DT.NFL.DECT.CD is the total net flow.

Every creditor-type code from OFFT to PROP covers PPG debt. Stock and gross flow names say so ("PPG, bilateral"), while net flow, commitment, undisbursed debt and terms names leave it out. PNG debt has only the PNGB and PNGC split, plus named lenders EBRD and IFC (NEBR, NIFC).

IMF credit (DIMF, IMFC, IMFN) is separate from the multilateral creditor codes, and MLAT totals cover the other multilateral creditors.

Codes with a debtor-sector segment (CB, GG, OPS, PS, PRVG) are PPG figures for that sector.

A ratio code shares its first segments with the amount it divides, so DT.DOD.DECT.GN.ZS (debt to GNI) and DT.DOD.DECT.CD (the stock) differ only in the unit and denominator segments.

## Codes in the DFO

The DFO decomposes each code into named dimensions, such as the type of flow, creditor type, guarantee status, debtor sector and unit, and keeps the original World Bank code on each variable as its source indicator code. Some variables carry more than one code, where several World Bank series describe the same measure for different lenders. The DFO version excludes the present value codes (PVLX), debt forgiveness grants (DT.DOD.MDRI.CD), the stock-flow residual (DT.DOD.RSDL.CD), the annual change codes ending in CG, and the non-DT context series other than GNI, exports and the two grant series (BX.GRT.EXTA.CD.DT, BX.GRT.TECH.CD.DT).

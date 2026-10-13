---
name: dfo-faq
description: >-
  Context for answering questions about the Development Finance Observatory itself: what it is, who builds and funds it, what data it holds and from which sources, how answers are sourced and cited, how often data updates, privacy, and where to get help. Load when a user asks about the DFO or this assistant.
license: CC-BY-4.0
---

# The Development Finance Observatory

## What it is

The Development Finance Observatory (DFO) is an open platform for development finance data. It brings data from the OECD, World Bank, IMF, and other publishers into one knowledge graph, so a Creditor Reporting System (CRS) disbursement, a World Bank debt figure, and a World Development Indicators series share the same countries, codes, and years. Every number is traceable to its source. The DFO has data on aid (including health aid), debt, and related economic, health, and social indicators.

It exists because this data is public but challenging to access and use. Each institution publishes a portion, in its own codes and formats, and anyone who needs to follow the money ends up reconciling sources manually.

The DFO is infrastructure that anyone can use in their work. People reach it through the website, DFO Studio (this assistant, with a chat and a canvas for charts and tables), data search and download, REST APIs, an MCP server for AI assistants, and ONE Data's open-source Python packages (oda_reader, imf-reader, tossd-reader, pydeflate and bblocks). The website is developmentfinance.org, and its documentation lives under /docs.

## Who is behind it

The DFO is an initiative by ONE Data, with support from The Rockefeller Foundation, through its public charity RF Catalytic Capital, and Google.org. ONE Data is part of the ONE Campaign. The DFO is built on Data Commons, Google's open knowledge graph.

## Who it is for

The DFO serves researchers and analysts, journalists, policy advisers, government officials and planners, and the developers who build tools for them.

## What data it holds

The DFO holds data on aid, debt, and related economic, health, and social indicators. ONE Data builds and maintains the core development finance datasets itself, such as the OECD Creditor Reporting System (CRS), World Bank International Debt Statistics (IDS), and IMF World Economic Outlook (WEO). The graph also carries datasets from Data Commons by Google and the UN System Data Commons, among them the World Bank's World Development Indicators, which cover real growth, inflation, government finance, and trade.

The `sources` tool returns the current catalogue: each dataset with its publisher, years, update cadence, and licence. Called with one dataset's ref, it returns that dataset's documentation, including methodology, citation, and release history. The catalogue does not state country coverage per dataset.

## How answers are made

The assistant answers using only the data in the DFO's knowledge graph: the datasets ONE Data builds and the datasets it draws from Data Commons by Google and the UN System Data Commons. It does not draw on the open web or the model's general knowledge of figures. The model does not do the arithmetic either: values come from the data and from tested calculation code, and a question that needs a calculation gets a plan the user approves before it runs. Every figure comes with its source, licence, and period.

When no source matches a question, the assistant says the data is not available and why. For example, no dataset in the DFO has the requested breakdown or year. It does not estimate.

Compared with going directly to the OECD Data Explorer or a World Bank portal, the DFO puts sources from many publishers in one graph with shared codes, applies the methodological choices an experienced analyst would make (which flow type, which price basis, how to avoid double counting), and cites every figure.

The assistant describes what the data show. It takes no position on policy questions, including ONE's own campaign positions, and gives no verdict of its own on whether a country's debt is sustainable. Where an official IMF and World Bank assessment exists, it reports that.

## How current the data is

The DFO checks each source daily for a new release. When one appears, the pipeline downloads it, runs its checks, and rebuilds the data. A failed check stops the release, and the previous release stays live. How often data changes therefore depends on each publisher's own calendar. Each source's page under Sources on the website lists its licence, update cadence, last update, and next expected update.

## Citing the DFO

Provide credit to the organisation that first published the data, then the DFO as the route. For example, "OECD Creditor Reporting System (2026), via the Development Finance Observatory". When the DFO has changed the figures, for example by converting currency, write "processed by the Development Finance Observatory" instead of "via". Cite a snapshot link, which pins the numbers, with the retrieval date. A live link can change after a refresh.

Each source's licence governs its data and appears on that source's page under "License & Updates".

## Privacy

The AI policy at developmentfinance.org/ai-policy sets out the DFO's commitments. The DFO accepts no file uploads. Questions run through enterprise-tier channels. Query text, search history, and session details are confidential and are not used to train any public AI model. Query text is processed only to produce an answer and is not linked to a persistent profile beyond the active session. The assistant runs on Google's Gemini models. ONE's privacy policy covers the rest of the website.

If you have questions regarding privacy, please reach out to data@one.org.

## Getting help

Report an inaccurate or unsourced answer, a bug, or a data request to data@one.org.

## What is coming

The DFO's public roadmap is on the website. Data from the International Aid Transparency Initiative (IATI) is in development. A nowcasting method for official development assistance (ODA), to estimate current-year aid before official figures arrive, is planned. Further aid, debt, and health-financing methods are under consideration.

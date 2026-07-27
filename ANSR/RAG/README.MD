# Simple Contract Knowledge Base Demo

## Purpose

This is the simplest version of the demonstration.

The starting point is a folder containing approximately 25 legal-contract PDFs
that have already been converted into Markdown (`.md`) files. The Markdown files
may be numbered `01` through `25`.

The team then runs **one prompt**. The agent reads the Markdown contracts, adds
useful metadata, identifies the natural contract categories, creates the
knowledge-base folders and indexes, and moves the contract files into the
appropriate folders.

## Starting folder

```text
contract_knowledge_base/
├── 01_contract.md
├── 02_contract.md
├── 03_contract.md
├── ...
└── 25_contract.md
```

Each Markdown file should contain the complete text of one contract. Preserve
the contract's headings, clauses, tables, schedules, and page references as
faithfully as possible during PDF conversion.

## The one prompt

Copy the following prompt into an agent that can read and edit files in the
starting folder:

```text
You are a contract knowledge-base organizer.

CONTEXT
The current folder contains approximately 25 legal contracts that have already
been converted from PDF into Markdown files. Build a simple, navigable knowledge
base from these files.

OBJECTIVE
Read the contract Markdown files, classify them by their dominant business and
legal purpose, add consistent metadata, organize them into useful folders, and
create indexes that another LLM can use for index-first retrieval.

WORKFLOW
1. Inventory every contract Markdown file in the current folder.
2. Read each contract sufficiently to identify its title, parties, agreement
   type, dominant purpose, subject matter, jurisdiction, effective date, term,
   status, and important legal or commercial topics.
3. Add or normalize YAML front matter at the top of each contract. Do not change
   the contractual body text while adding metadata.
4. Infer a small and practical taxonomy from the actual contracts. Prefer
   approximately 4 to 6 non-overlapping main categories. Do not invent a
   category before examining the corpus.
5. Assign every contract exactly one main category. A contract may have several
   secondary topics and RAG tags.
6. Create one filesystem-safe folder for each main category.
7. Move each contract Markdown file into its assigned category folder. Preserve
   its document ID and filename unless a filename is unsafe or misleading.
8. Create an index.md inside every category folder.
9. Create a root index.md that routes questions to the correct category index.
10. Validate all links, metadata, document counts, and file locations.

USE THIS YAML SHAPE
---
document_id: "CONTRACT-001"
title: "Full contract title"
document_type: "Agreement type"
main_category: "One primary category"
secondary_topics:
  - "Topic one"
  - "Topic two"
rag_tags:
  - "lowercase-kebab-case-tag"
  - "another-search-tag"
parties:
  - name: "Party name"
    role: "Provider, Client, Vendor, Landlord, Employee, or other role"
jurisdiction: "Named governing jurisdiction or Unknown"
effective_date: "YYYY-MM-DD or Unknown"
expiration_date: "YYYY-MM-DD, Indefinite, or Unknown"
status: "Active, Expired, Draft, Terminated, or Unknown"
source_file: "Original PDF filename if known"
summary: "One or two factual sentences describing the agreement"
key_topics:
  - "Important clause or commercial topic"
---

METADATA RULES
- Use only facts supported by the contract.
- Use "Unknown" when a value cannot be established.
- Do not infer that a contract is active only because it has an effective date.
- Keep main_category broad enough to contain multiple related contracts.
- Put granular concepts in secondary_topics, key_topics, and rag_tags.
- Use lowercase kebab-case for rag_tags.
- Keep summaries factual and neutral.
- Do not add confidential facts that are not already in the contract.

EACH CATEGORY INDEX.MD MUST CONTAIN
- Category name and plain-language description.
- Types of questions that should be routed to the category.
- A Markdown table listing every contract in the folder.
- For each contract: document ID, title, document type, parties, important
  topics, dates or status when available, and a relative Markdown link.
- Useful search terms and RAG tags.
- Important overlaps with other categories, if any.
- An instruction to open the underlying contract before answering clause-level
  questions.

THE ROOT INDEX.MD MUST CONTAIN
- A short explanation of the knowledge base.
- The total contract count and category count.
- A category-routing table containing the category name, purpose, example
  questions, contract count, and relative link to its index.md.
- A compact contract directory listing all contracts and their locations.
- Cross-category routing guidance.
- The following retrieval procedure:
  1. Read the root index.md.
  2. Select the most relevant category or categories.
  3. Read the selected category index.md.
  4. Select the smallest relevant set of contracts.
  5. Read the selected contracts.
  6. Answer using contract-supported facts and cite the document ID, filename,
     and relevant section or clause.
- A warning not to treat index summaries as a substitute for the contract text.

SAFETY AND QUALITY RULES
- Never fabricate a clause, date, party, obligation, or legal conclusion.
- Preserve the original contract body text.
- Do not delete source content.
- If classification is uncertain, choose the best-supported main category and
  record the uncertainty in the category index.
- Use relative Markdown links.
- Use deterministic, filesystem-safe folder names.
- Resolve duplicate document IDs before completing the task.
- Confirm that every inventoried contract appears exactly once in the organized
  knowledge base.
- Report missing, unreadable, duplicated, or incomplete files.

FINAL RESPONSE
After completing the work, report:
- Number of contracts inventoried.
- Number of contracts organized.
- Categories created and their document counts.
- Files that need human review.
- Validation errors or unresolved uncertainties.
- Path to the root index.md.
```

## Expected result

The exact category names should be derived from the 25 contracts. A typical
result will look like this:

```text
contract_knowledge_base/
├── index.md
├── category-one/
│   ├── index.md
│   ├── 01_contract.md
│   └── 07_contract.md
├── category-two/
│   ├── index.md
│   ├── 02_contract.md
│   └── 09_contract.md
└── category-three/
    ├── index.md
    └── ...
```

The category labels shown above are placeholders. The agent should determine
meaningful categories from the contracts rather than copying generic names.

## How the demo works

When a user asks a question, the answering agent follows this path:

```text
User question
    ↓
Root index.md
    ↓
Relevant category index.md
    ↓
Relevant contract file or files
    ↓
Grounded answer with document and clause references
```

For example, if the user asks, “Which agreements allow termination for
convenience?”, the agent:

1. reads the root `index.md`;
2. selects the categories most likely to contain termination provisions;
3. reads those category indexes;
4. opens the relevant contracts;
5. compares the actual termination clauses; and
6. answers with the supporting document IDs and clause references.

## Suggested demo questions

- Which contracts expire in the next 12 months?
- Which agreements contain automatic renewal?
- Which contracts allow termination for convenience?
- What notice periods apply to termination?
- Which agreements contain data-protection obligations?
- Which contracts are governed by Indian law?
- Compare the payment terms in the relevant service agreements.
- Which contracts require a parent guarantee, deposit, or other security?
- Show contracts where the effective date or expiration date is missing.
- Which documents require human review because their classification is
  uncertain?

## Demo success criteria

The demo is successful when:

1. all 25 Markdown contracts are represented exactly once;
2. every contract contains consistent YAML metadata;
3. each contract is placed in one meaningful category;
4. the root and category indexes contain working relative links;
5. an agent can navigate from the root index to relevant evidence without
   reading all 25 files; and
6. answers cite the underlying contracts rather than relying only on index
   summaries.


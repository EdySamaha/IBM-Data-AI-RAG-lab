# Architecture — one diagram, three boxes, one arrow of trust

This lab stands up three components and connects them. By the end you will have
built all three yourself.

```
   ┌─────────────────────────────────────────────────────────────┐
   │                        watsonx.data                           │
   │                   (open, governed lakehouse)                  │
   │                                                               │
   │   ┌──────────────────┐          ┌──────────────────────┐      │
   │   │  Presto / SQL     │          │  Milvus               │      │
   │   │  engine           │          │  (vector database)    │      │
   │   │                   │          │                       │      │
   │   │  queries the      │          │  search-by-meaning    │      │
   │   │  Iceberg table    │          │  over the PDF         │      │
   │   │  IN PLACE          │          │  (RAG)                │      │
   │   └──────────────────┘          └──────────────────────┘      │
   │            ▲                               ▲                   │
   │            │        Trusted catalog         │                   │
   │            │     (access · lineage · metadata)                 │
   └────────────┼───────────────────────────────┼───────────────────┘
                │                               │
                │   governed connection (no copy of the data)
                │                               │
   ┌────────────┴───────────────────────────────┴───────────────────┐
   │                        watsonx.ai                                │
   │                     (the AI runtime / studio)                    │
   │                                                                  │
   │   Notebook  +  Granite foundation model  +  embedding model      │
   │                                                                  │
   │   • reads the catalogued table through the connection            │
   │   • embeds the PDF and writes vectors into the Milvus above       │
   │   • turns a plain-English question into SQL, runs it, charts it   │
   └──────────────────────────────────────────────────────────────────┘
```

## The three boxes

- **watsonx.data** — an open lakehouse with a **trusted catalog**. Presto /
  Prestissimo queries Iceberg tables (and other sources) **in place** — no ETL,
  no copies. The catalog is where access, lineage, and metadata are managed.
- **Milvus** — a **vector database** inside the same platform, for semantic
  search / RAG over unstructured text (today, a PDF).
- **watsonx.ai** — the runtime where notebooks and **Granite** foundation models
  run, reading the catalogued data through a **governed connection**.

## The one claim this lab proves

You could rebuild each box tonight with Postgres, a Jupyter kernel, and a hosted
model API. What you **couldn't** easily rebuild is the property this lab
demonstrates:

> The data never leaves your organization's governed environment, and **one
> access / lineage fabric spans both the data and the AI.**

Watch for it at every step: the data is read where it sits, and the model is
given only a **schema and a question** — never the rows themselves. The document
is embedded by watsonx.ai but the vectors land in the Milvus **you** provisioned,
so the PDF never leaves your environment either.

## Why that matters (the pivot)

The cod dataset is public. Re-run the whole pipeline in your head with the table
swapped for genomics data, student records, or unpublished research — and the PDF
for a confidential report. Every step is identical, and at no point does the data
leave your environment or reach an outside model service. That guarantee, plus
one governance and lineage fabric across both the data and the AI, is the
capability this platform gives you.

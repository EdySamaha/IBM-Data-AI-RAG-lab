# Non-Technical Track · Humanities

# AI Insights from a Trusted Data Catalog

A guided, hands-on introduction to **watsonx.data + watsonx.ai** — build a
trusted catalog and ask it questions in plain language. ~2 hours, online,
self-guided. **No coding required.**

> **Companion notebook:** [`watsonx_lab_guided.ipynb`](watsonx_lab_guided.ipynb)
> — every step is pre-written; you click **Run** and, in one cell, type a question.

---

## What you'll walk out with

A chart you produced yourself from a real dataset — by creating a trusted
catalog, loading the data, and asking a question in plain English. You'll also
have a clear sense of **why the data never left your own governed environment**,
and why that matters for research and student data.

Everything is written out step by step, and the notebook has every step
pre-written for you. Follow along on your own screen at your own pace — you won't
need to write any code.

### At a glance

| | |
|---|---|
| **Audience** | Students & researchers of any major — approachable for any background |
| **Duration** | ~2 hours, online, self-guided |
| **Format** | Follow the written steps at your own pace, running the provided notebook cells |
| **You'll build** | A trusted catalog, a query engine, a vector engine loaded from a PDF, a data table, and a live AI connection — all yourself |
| **Products** | watsonx.data (the governed lakehouse & catalog) + watsonx.ai (the AI studio) |
| **Dataset** | Newfoundland cod fishery landings, 1955–2024 ([CSV](../../data/cod_landings_nl.csv)) + a short background [PDF](../../docs/cod_background.pdf) (both provided) |
| **Outcome** | One chart, produced by asking a question in plain English, from data you catalogued — plus the sensitive-data 'aha' |

---

## Before you begin

You don't need to install anything in advance or write any code — the notebook
already has every step written for you, and you'll run them one at a time. You
only need two things ready at the start:

1. **Access to a raw environment** — a watsonx.data instance and a watsonx.ai
   project, both empty. Everything inside them, you'll create today.
2. **The lab files from this repo** — the dataset
   ([`data/cod_landings_nl.csv`](../../data/cod_landings_nl.csv)), a short
   background PDF ([`docs/cod_background.pdf`](../../docs/cod_background.pdf)), and
   the lab notebook ([`watsonx_lab_guided.ipynb`](watsonx_lab_guided.ipynb)).
   Have your API key and project ID on hand (the instructor will show you where to
   find them).

> **How the notebook works:** a notebook is just a page made of boxes called
> *cells*. Each cell has a step already written in it; you click a cell and press
> **Run**, and it does that step. You'll never have to write anything — at most
> you'll type a question in plain English into one cell. The first cell signs you
> in: paste your API key and project ID there and run it once.
>
> Work through the cells **in order, top to bottom**. Each one builds on the one
> before it, so running them out of order can cause confusing errors — if
> something looks wrong, start again from the first cell.

> 📎 Reference — [New to notebooks? A 5-minute Jupyter overview](https://docs.jupyter.org/en/latest/start/index.html)

One thing to keep in mind: a query engine and a vector engine **cost money while
they are running**. You'll start them at the beginning so they're ready when you
need them — and you'll **stop them at the very end** so they don't keep billing.

---

## The two-hour flow

| Session | Time | What you'll do |
|---|---|---|
| Opening | 15 min | What the two tools are and what you'll build today; log in |
| watsonx.data — set up & explore | 30 min | Create your catalog and engines in a few clicks; load the dataset and see its columns; run one guided query |
| watsonx.ai — Connect to the AI | 30 min | See how the AI reads your table in place; then upload a PDF and search it by meaning — nothing leaves your environment |
| Ask a question, get a visual | 30 min | Type a plain-English question; the AI writes the query, shows it, and draws a chart; try a second question together |
| Wrap-up & Q&A | 15 min | "Now imagine this were student or health data"; where to go next; open Q&A |

---

## Opening

**15 minutes.** Log in to watsonx.data and open your project so you're ready to
build. Then, before you open any tool in earnest, here's the lay of the land in
plain terms:

- **watsonx.data** is where the organization keeps and queries its data — think
  of it as a well-organized, governed catalog of tables that stays inside your own
  environment.
- **watsonx.ai** is the AI studio that can read that data and help you make sense
  of it — summarize, analyze, and draw a chart.
- In this lab you'll build each piece yourself — the catalog, the tools, the
  loaded data, and the connection — and then go from a table of numbers to a
  picture by asking a question in plain English.

**One promise to hold onto:** everything you do today stays inside your
organization's own environment. Nothing is uploaded to an outside website, and
nothing is copied somewhere you can't see. That is the whole reason these tools
are chosen for sensitive work — and by the end you'll have watched it stay true at
every step. (See [`docs/architecture.md`](../../docs/architecture.md) for the
picture.)

---

## watsonx.data · set up & explore

**30 minutes.** This is the "I built something" moment — all of it done by
pointing and clicking, no code. Create your catalog and both engines first so
they're ready while you load the data.

### 1 · Create your catalog and query engine

- Open watsonx.data and go to **Infrastructure manager**. Add (or associate) a
  catalog — the governed, trusted container that will hold your table. This lab
  uses one named **`iceberg_data`**.
- Click **Add component → Presto engine**, give it a name, pick the smallest
  size, and click **Create**. A "query engine" is simply the thing that answers
  questions about your data.
- Associate the engine with your catalog, then let it start — it takes a couple
  of minutes to come alive. Leave it starting and move straight on.

### 2 · Create your vector engine

- Still in Infrastructure manager, click **Add component → Milvus**, name it,
  pick the smallest size, and click **Create**.
- Let it start alongside the query engine. This is the piece that lets us search a
  document by meaning later. It starts out empty, and you won't find a place to
  drop a PDF here — you'll fill it from watsonx.ai in a later step, because
  turning a document into something searchable is a job for the AI studio.

> **While both engines start:** they warm up in the background and take a couple
> of minutes each — that's normal. You've just provisioned, in a few clicks, the
> two services this whole lab runs on.

### 3 · Load the dataset yourself

- Open the **Data manager** from the left navigation. Inside your `iceberg_data`
  catalog, create (or open) a schema to hold your data — a schema is just a
  labeled folder for related tables.
- Choose **Create table from file** and upload
  [`cod_landings_nl.csv`](../../data/cod_landings_nl.csv) — the file you downloaded
  from the repo.
- Give the table a name (e.g. `cod_landings_nl`) and confirm. watsonx.data
  registers it as a governed table in your catalog that you can now query.
- Open the table and look at the columns: **year, landings (tonnes), licensed
  fishers, and a short status note**. Take a moment to recognize what each means —
  you'll ask questions about them shortly.

> **Notice what just happened:** you loaded the data into the governed catalog,
> not onto your laptop. From here on it lives here, under access controls — it
> isn't sitting in a spreadsheet or on a public website.

### 4 · Run one query (guided)

- Open the query workspace and pick your Presto engine from the dropdown.
- Paste the one line below and run it. In plain terms it says: *show me year and
  landings, ordered by year.*

```sql
SELECT year, landings_tonnes FROM cod_landings_nl ORDER BY year;
```

- A tidy table of results appears in seconds, one row per year.

> **What you just did matters:** you asked the data a question *where it lives*.
> You didn't export it, email it, or paste it into a website — that's what "query
> in place" means, and it's the habit the rest of the lab builds on.

---

## watsonx.ai · Connect to the AI

**30 minutes.** Now point the AI studio at the same catalogued data — without
moving it. You'll build the connection, open the notebook that reads your table
where it lives, and then upload the PDF and search it by meaning, right here in
watsonx.ai.

### 1 · Build the connection to your data

- Open watsonx.ai and go to your (empty) project. Add a **connection to
  watsonx.data**: point it at your query engine and the catalog/schema where your
  table lives, and give it a name. You're telling the AI studio **where to read,
  not handing it a copy**.
- Open the lab notebook ([`watsonx_lab_guided.ipynb`](watsonx_lab_guided.ipynb))
  in the project. Run its **Setup** cell, then the **Sign in** cell (paste the API
  key, project ID, and the Presto values your instructor gives you).

### 2 · See how the AI reads your data in place

- Run the **"Read your table"** cell. It uses your connection to pull a preview of
  `cod_landings_nl` straight from the catalog — nothing was uploaded, and no copy
  was made.
- Look at the few rows it prints back. This is the AI studio reading your governed
  data where it lives; from here on, every question you ask works against this same
  catalogued table.

> That is the whole idea of **"connect, don't copy"**: the AI gets a live,
> governed view of your data through the connection, so your access controls and
> lineage still apply to everything that happens next.

### 3 · Upload a PDF and search it by meaning

Here's the button you couldn't find in watsonx.data — it lives here, because
searching a document by meaning first needs the AI to turn its text into numbers,
and that's what the AI studio does. You'll point it at the empty vector engine you
created earlier so the document still stays in your own environment.

- In your watsonx.ai project, choose **New asset → Vector index**.
- **Upload the background PDF** ([`cod_background.pdf`](../../docs/cod_background.pdf)).
  This is the upload button that doesn't exist on the watsonx.data side.
- Pick the **embedding model** that's offered (the thing that turns text into
  searchable meaning), and choose your watsonx.data **Milvus** as where to store
  it — so the document stays inside your governed environment. Then create the
  index: watsonx.ai reads the PDF, splits it into passages, and loads them into
  your vector engine for you.
- Open the index and **search by meaning**: type a phrase like *"what happened to
  the fishery in the early 1990s?"* It brings back the right passages by meaning,
  not just exact-word matches — so it finds the moratorium passage even if your
  words don't match. Try a second phrase of your own.

> **The point to take away:** the AI did the vectorizing, but the result landed in
> the governed vector engine you created — the PDF never left your organization or
> got uploaded to an outside website. The same trusted catalog that holds your
> numbers now searches your documents by meaning too.

---

## Ask a question, get a visual

**30 minutes · the payoff.** Here's the moment it all comes together — and you'll
see the AI isn't a black box. (Back in the notebook.)

- Find the **"Ask your question"** cell. In plain English, type something like
  *"Show cod landings by year and mark the 1992 moratorium,"* then press **Run**.
- The AI turns your sentence into a precise query, **shows you the exact query it
  wrote**, runs it on your data in watsonx.data, and brings back the answer as a
  table. Nothing is hidden — read the query it ran and check that it matches what
  you asked.
- Run the **"Make the chart"** cell. A line chart appears: the enormous
  late-1960s peak, the steep fall, and the 1992 collapse.
- Try a **second question** of your own — for example *"What's the single biggest
  year-over-year drop?"* — and watch it write a new query and answer from the same
  data. Compare answers as a group.

> **Step back and notice:** you built the tools, catalogued the data, and then got
> an analysis and a chart just by asking a question in plain English. The AI even
> showed you the exact query it used — and the data never left your environment.

---

## Wrap-up & Q&A

**15 minutes.** This is where the value clicks. The cod numbers are public, and so
is that background PDF — nothing secret. But look back at every step, and now
imagine that table wasn't cod landings, and that document wasn't a public report.
Imagine it was **student records, patient data, or unpublished research**.

The steps would be exactly the same — and nothing would have left your
organization's environment. No upload to an outside website, no copy on a laptop,
no data handed to a company you don't control.

Here's why that held true at every step you built:

- The data stayed **queried in place** in your catalog — you never made copies to
  lose track of.
- The AI **ran beside the data**, inside the governed environment — and only ever
  saw your question, not a copy of the records.
- Access was **governed the whole time** by your own controls.

That is the difference between "I used an AI" and "I used AI responsibly on data
I'm accountable for." It's why the tool of choice for real research and
institutional data isn't a public chatbot.

### Where to go next

- Free, self-paced courses to keep exploring: [IBM SkillsBuild](https://skillsbuild.org/)
  and [Cognitive Class](https://cognitiveclass.ai/).
- For text-heavy research: the document-search pattern you built today extends to
  much larger collections — a natural next lab.
- Bring your own dataset to office hours — the same steps work on it: catalog it,
  connect it, ask.

---

## ⚠️ Before you close — stop your engines

You created your own query engine and vector engine, and they **bill while
running**. Stop both now so they don't keep costing money after the session.

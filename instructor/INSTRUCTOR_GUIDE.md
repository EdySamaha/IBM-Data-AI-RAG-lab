# Instructor Guide — Run of Show

Facilitation notes for the 2-hour lab, covering **both** tracks. Timing totals
2:00. The two tracks run the same five segments on the same clock; the only real
difference is **how** attendees do the PDF/vector step and whether they read code.

> **Prep:** complete [`PROVISIONING.md`](PROVISIONING.md) first, and run the
> [preflight check](../scripts/verify_setup.py) with real credentials.

---

## The one message

Everything in this lab serves a single claim. Say it at the start, prove it at
each step, and name it at the end:

> **The data never leaves your governed environment, and one access/lineage fabric
> spans both the data and the AI. The model only ever sees a schema and a question
> — never the rows.**

If attendees leave remembering only that sentence and that they produced a chart
by asking in plain English, the session succeeded.

---

## Timing at a glance

| Segment | Time | Running total |
|---|---|---|
| Opening — tools, architecture, log in | 15 min | 0:15 |
| watsonx.data — set up & explore | 30 min | 0:45 |
| watsonx.ai — connect to the AI | 30 min | 1:15 |
| Ask a question, get a visual | 30 min | 1:45 |
| Wrap-up & Q&A | 15 min | 2:00 |

**Start the engines early.** During the Opening, have attendees (or you, for a
shared instance) kick off the Presto and Milvus engines so they're *running* by
the time they're needed in segment 2–3. Nothing kills momentum like waiting on a
spinner.

---

## Opening · 15 min

- Introduce the two tools in one line each: watsonx.data = the governed catalog
  where data lives and is queried; watsonx.ai = the AI studio that reads it.
- Show the diagram ([`docs/architecture.md`](../docs/architecture.md)): three
  boxes, one arrow of trust.
- State the one message (above). Tell them to watch for it at every step.
- Everyone logs in and opens their empty project.

**Track note:** identical for both. For the non-technical room, add a 60-second
"how a notebook works" (cells, press Run) — it removes most of the anxiety.

---

## watsonx.data · set up & explore · 30 min

Attendees create the catalog (`iceberg_data`), the Presto engine (`lab-presto`),
and the Milvus engine (`lab-milvus`), then ingest `cod_landings_nl.csv` into the
`marine` schema as `cod_landings_nl`, and run one query.

- Have them **create all three (catalog + both engines) first**, then ingest
  while the engines warm up.
- The Milvus engine starts **empty** on purpose — there's no PDF button here.
  Flag this now; it pays off in the next segment ("the button you're looking for
  lives in watsonx.ai, and here's why").
- Land the point after the first query: *you queried the data where it lives — no
  export, no copy.*

**Technical room:** they run the federated `SELECT ... WHERE year BETWEEN 1955
AND 2024`. Mention federation across sources as the "no ETL" value.
**Non-technical room:** they run the single-line `SELECT year, landings_tonnes
... ORDER BY year`. Keep it about "asking the data a question where it lives."

**Common stumbles:** engine still "starting" (wait, or pre-start for shared);
catalog/schema name mismatch (`iceberg_data.marine`); wrong column types on
ingest.

---

## watsonx.ai · connect to the AI · 30 min

Attendees create the governed connection, read the table from the notebook, and
load the PDF into Milvus and search it by meaning.

**This is where the two tracks diverge most:**

- **Technical:** in the notebook, `pypdf` → `Embeddings` (slate) → `pymilvus`
  insert/index/load → semantic search, in code. Make the point that watsonx.ai
  did the embedding but the vectors landed in *their* Milvus — the doc never left.
- **Non-technical:** point-and-click **New asset → Vector index**, upload the PDF,
  pick the embedding model, store in their Milvus, then search in the UI. Same
  outcome, lid on.

Either way, run the semantic query *"what happened to the fishery in the early
1990s?"* and highlight that it surfaces the **moratorium** passage **without those
words appearing** — meaning, not keyword match.

**Common stumbles:** auth error (API key / project ID / region mismatch); Presto
host unreachable (engine not running); Milvus dimension mismatch (schema `dim`
must equal `len(vectors[0])`) — technical room only.

---

## Ask a question, get a visual · 30 min — the payoff

- Plain-English question → Granite writes SQL → run it → chart.
- **Always show the generated SQL** and the read-only validation. For the
  non-technical room this is the "the AI isn't a black box" moment — the notebook
  prints the exact query before running it.
- Draw the chart: late-1960s peak (~800k tonnes), decline, **1992 collapse**
  marked on the axis.
- Do the **analytical follow-up** live together: change the question (e.g.
  *"biggest year-over-year drop"* or *"average landings per decade"*) and re-run.
  This shows the pipeline flexing without hand-written SQL.

**Technical:** also let Granite generate the matplotlib and `exec` it after a
read-through; note the "read before you run" habit, and that a wrong column name
is the usual fix.
**Non-technical:** the chart is drawn by a tidy helper from the AI's answer — keep
attention on *they asked in English and got a governed answer + picture*.

---

## Wrap-up & Q&A · 15 min — the pivot

Deliver the **sensitive-data pivot** deliberately; it's the emotional core:

> The cod data is public. Now imagine the table were student records, patient
> data, or unpublished research — and the PDF a confidential report. **Every step
> would be identical, and nothing would have left your organization.**

Then name why it held: queried in place (no copies), AI ran beside the data (saw
only the question), governed by your controls throughout. Contrast with pasting
institutional data into a public chatbot.

Close with **where to go next** (SkillsBuild, Cognitive Class, the
watsonx-ai-samples repo) and open Q&A — invite attendees to describe a dataset
from their own field and talk through the same catalog-to-chart path.

---

## ⚠️ Close every session the same way

Make attendees **stop their Presto and Milvus engines** before they leave —
they bill while running. Don't let this be optional or an afterthought; it's the
literal last step in both notebooks and both READMEs.

---

## Quick divergence table

| Step | Technical | Non-technical |
|---|---|---|
| Reads code? | Yes — runs each block | No — presses Run; types one question |
| watsonx.data setup | Same point-and-click | Same point-and-click |
| PDF → vectors | In the notebook (`pypdf`/`pymilvus`) | Vector Index UI asset |
| Text-to-SQL | Writes/validates in code | Helper does it; SQL is shown |
| Chart | Granite generates code → `exec` | Helper draws it from the answer |
| Payoff | Same chart, same pivot | Same chart, same pivot |

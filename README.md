# IBM Data & AI — RAG Lab

### AI Insights from a Trusted Data Catalog · watsonx.data + watsonx.ai

A 2-hour, hands-on enablement lab. You build a **trusted data catalog**, a **SQL
(Presto) engine**, a **Milvus vector database**, and a **governed connection** to
the AI runtime — then go from a plain-English question to an **AI-generated
chart**, using a real Newfoundland cod-fishery dataset.

The one claim the lab proves:

> **The data never leaves your organization's governed environment, and one
> access / lineage fabric spans both the data and the AI.** The model is only ever
> given a schema and a question — never the rows.

---

## ▶ Pick your track

The lab comes in two versions covering the same story. Start with your track's
README and run its notebook.

| Track | For | Start here |
|---|---|---|
| 🧑‍💻 **Technical** | Computer-science students & data-curious folks comfortable with SQL/Python. You read and run the code. | **[labs/technical/README.md](labs/technical/README.md)** |
| 📚 **Non-technical** | Students & researchers of any background. Point-and-click + run pre-written cells; type one question in plain English. **No coding.** | **[labs/non-technical/README.md](labs/non-technical/README.md)** |

Not sure? If you'd be comfortable editing a line of Python, take the technical
track; otherwise take the non-technical one. Both end with the same chart and the
same "sensitive-data" insight.

---

## Before you begin (both tracks)

Nothing is pre-loaded — you provision every component live. You need:

1. **A raw environment** — an empty watsonx.data instance and an empty
   watsonx.ai project. (Instructors: see [`instructor/PROVISIONING.md`](instructor/PROVISIONING.md).)
2. **The lab files from this repo** — the [dataset](data/cod_landings_nl.csv),
   the [background PDF](docs/cod_background.pdf), and your track's notebook.
3. **Your credentials** — an IBM Cloud API key and your watsonx.ai project ID
   (project → Manage → General).

> 💸 **Cost:** the Presto and Milvus engines bill while running. Start them early,
> and **stop both at the end** — the last step of either track.

---

## What's in this repo

| Path | What it is |
|---|---|
| [`labs/technical/`](labs/technical/) | Technical track — full written lab + fully-coded notebook |
| [`labs/non-technical/`](labs/non-technical/) | Non-technical track — guided lab + run-only notebook |
| [`data/`](data/) | The cod-fishery dataset ([`cod_landings_nl.csv`](data/cod_landings_nl.csv)) + its [data dictionary](data/README.md) |
| [`docs/`](docs/) | Background [PDF](docs/cod_background.pdf) (+ its [source](docs/cod_background.md)) and the [architecture explainer](docs/architecture.md) |
| [`config/lab_config.yaml`](config/lab_config.yaml) | Single source of truth for catalog/schema/table names, model IDs, and settings |
| [`scripts/`](scripts/) | Helper module, dataset + PDF generators, and a [preflight check](scripts/verify_setup.py) |
| [`instructor/`](instructor/) | **Facilitators only** — [provisioning checklist](instructor/PROVISIONING.md) and [run-of-show guide](instructor/INSTRUCTOR_GUIDE.md) |
| [`.env.template`](.env.template) | Copy to `.env` and fill in credentials (for the local preflight script) |
| [`requirements.txt`](requirements.txt) | Python dependencies (match the notebooks' install cell) |

---

## The shape of a session

| Session | Time | What happens |
|---|---|---|
| Opening | 15 min | The two tools, the architecture, and today's goal; log in |
| watsonx.data — set up & explore | 30 min | Create the catalog + both engines; ingest the table; query it in place |
| watsonx.ai — connect to the AI | 30 min | Governed connection; read the table in place; load the PDF into Milvus and search by meaning |
| Ask a question, get a visual | 30 min | Plain-English question → SQL → chart |
| Wrap-up & Q&A | 15 min | Why it beats a DIY stack; the sensitive-data pivot; where to go next |

---

## For instructors

The environments don't exist until you create them. Before the session:

1. Follow **[`instructor/PROVISIONING.md`](instructor/PROVISIONING.md)** to stand
   up the watsonx.data instance, catalog, engines, and watsonx.ai project.
2. (Optional) Fill in a local `.env` and run the preflight check to confirm
   connectivity:
   ```bash
   pip install -r requirements.txt
   cp .env.template .env   # then edit .env
   python scripts/verify_setup.py
   ```
3. Use **[`instructor/INSTRUCTOR_GUIDE.md`](instructor/INSTRUCTOR_GUIDE.md)** for
   the run-of-show, timing, and talking points.

---

## Dataset note

`cod_landings_nl.csv` is a **realistic synthetic reconstruction** of Northern cod
landings built for teaching — it follows the real history (late-1960s peak, 1992
moratorium) but the exact numbers are generated, not official DFO figures. It is
reproducible via [`scripts/generate_dataset.py`](scripts/generate_dataset.py).
See [`data/README.md`](data/README.md). To use real figures, drop in a CSV with
the same four columns and everything downstream works unchanged.

## License

[MIT](LICENSE).

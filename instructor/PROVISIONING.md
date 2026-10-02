# Provisioning Checklist (Instructors)

Stand up the environments **before** the session. Learners arrive to an *empty*
watsonx.data instance and an *empty* watsonx.ai project — the lab is them filling
those in. This checklist gets you to that starting line.

> ⏱️ Do this at least a day ahead. Some provisioning steps take time to activate,
> and you want to run the [preflight check](../scripts/verify_setup.py) once with
> real credentials before anyone shows up.

---

## 0 · Decide the delivery model

| Model | What it means | When to use |
|---|---|---|
| **Each attendee their own** | Everyone has their own watsonx.data instance + watsonx.ai project. | Small groups; cleanest "I built it myself" experience. |
| **Shared instance, own engines** | One watsonx.data instance; each attendee creates their own catalog/engines inside it. | Medium groups; controls instance count. |
| **Fully shared** | One instance, one set of engines/catalog that everyone associates with. | Large groups or tight budgets; attendees still run the notebook. |

The lab's SQL and notebook code are **identical** across all three — only the
"who creates what" differs. The learner steps already call out the shared-vs-own
fork inline.

> 💸 **Cost reminder for every model:** Presto and Milvus engines bill while
> running. Keep them stopped until shortly before the session, and make the
> "stop your engines" close non-optional.

---

## 1 · IBM Cloud account & entitlement

- [ ] An IBM Cloud account with access to **watsonx.data** and **watsonx.ai**
      (Dallas `us-south` is the common default; `eu-de` / `ca-tor` also work —
      just keep the region consistent and update [`config/lab_config.yaml`](../config/lab_config.yaml) `url`).
- [ ] Confirm your plan allows creating Presto and Milvus engines.
- [ ] (If attendees use their own IBM Cloud accounts) send them the sign-up link
      and the free-tier notes ahead of time.

## 2 · Object storage bucket

- [ ] Provision (or identify) a **Cloud Object Storage** bucket to back the
      catalog. Note the bucket name, endpoint, and access/secret keys.

## 3 · watsonx.data instance

- [ ] Provision a watsonx.data instance in your chosen region.
- [ ] In **Infrastructure manager**, confirm you can **Add component** (Presto,
      Milvus) — this is what attendees will do live.
- [ ] For the **fully shared** model only: pre-create the catalog
      `iceberg_data`, the `lab-presto` and `lab-milvus` engines, and the
      `marine` schema, and ingest `cod_landings_nl.csv` so attendees skip
      straight to querying. For the other two models, leave this to the learners.

## 4 · watsonx.ai project

- [ ] Create a watsonx.ai project (or one per attendee / group).
- [ ] Associate a **Watson Machine Learning** service instance with the project
      (required for the foundation-model SDK calls — Granite + embeddings).
- [ ] Upload the lab files into the project so attendees can open them directly:
      - [`labs/technical/watsonx_lab_technical.ipynb`](../labs/technical/watsonx_lab_technical.ipynb)
        (technical attendees)
      - [`labs/non-technical/watsonx_lab_guided.ipynb`](../labs/non-technical/watsonx_lab_guided.ipynb)
        (non-technical attendees)
      - [`data/cod_landings_nl.csv`](../data/cod_landings_nl.csv)
      - [`docs/cod_background.pdf`](../docs/cod_background.pdf)
- [ ] Confirm the needed models are available in the region:
      `ibm/granite-3-8b-instruct` and `ibm/slate-125m-english-rtrvr`. If a model
      ID has changed, update it once in [`config/lab_config.yaml`](../config/lab_config.yaml)
      and in the notebook cells.

## 5 · Credentials for attendees

Each attendee needs:

- [ ] An **IBM Cloud API key** — IBM Cloud console → Manage → Access (IAM) → API
      keys. (Decide: shared lab key, or each person makes their own.)
- [ ] Their **watsonx.ai project ID** — project → Manage → General → Project ID.
- [ ] The **Presto engine** connection values (host, port, user, password) from
      the engine's *Connect* panel — needed by both notebooks.
- [ ] The **Milvus engine** connection values — needed by the *technical* notebook
      (the non-technical track reaches Milvus through the Vector Index UI, so those
      attendees don't paste Milvus creds).

Prepare a short handout (or slide) with exactly which value goes in which cell.

## 6 · Preflight — do this once yourself

From a machine with Python:

```bash
pip install -r requirements.txt
cp .env.template .env     # then fill in real values
python scripts/verify_setup.py
```

A clean run confirms: config loads, credentials present, watsonx.ai
authenticates, Presto answers a COUNT on `iceberg_data.marine.cod_landings_nl`,
and Milvus accepts a connection. Fix anything red before the session.

> For the **fully shared** model, this also seeds the table so the first query
> works instantly. For own-engine models, the Presto check only passes after you
> (or a test attendee) have ingested the CSV once.

## 7 · Just before the session

- [ ] Start the shared engines (if using the shared model) ~10 min ahead so
      they're *running*.
- [ ] Re-run the preflight check.
- [ ] Have [`INSTRUCTOR_GUIDE.md`](INSTRUCTOR_GUIDE.md) open for the run-of-show.

---

## Reference links

- watsonx.data docs — <https://www.ibm.com/docs/en/watsonx/watsonxdata>
- watsonx.ai docs — <https://www.ibm.com/docs/en/watsonx/saas>
- watsonx.ai Python SDK — <https://ibm.github.io/watsonx-ai-python-sdk/>
- Runnable sample notebooks — <https://github.com/IBM/watsonx-ai-samples>

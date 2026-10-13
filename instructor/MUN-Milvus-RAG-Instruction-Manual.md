# Milvus + watsonx.ai RAG — Complete Setup Instruction Manual
### IBM Technology Zone (ITZ) Environment Edition

> **What this guide builds:** A working RAG (Retrieval-Augmented Generation) pipeline where a document is stored as vectors in a Milvus engine (inside watsonx.data) and an LLM in watsonx.ai can answer questions about it.
>
> **Who this is for:** Anyone using an IBM Technology Zone (ITZ) provisioned watsonx environment. The specific instance names will differ but the steps are identical.
>
> **Time to complete Phases 1–3:** Approximately 60-75 minutes (first time).

---

## Before You Begin — Know Your Environment

Your ITZ environment provisions several services automatically. Before starting, go to **[cloud.ibm.com/resources](https://cloud.ibm.com/resources)** and note the names of your instances. You will need:

| Service | Found under section | What it's for |
|---|---|---|
| **watsonx.data** | Databases | Hosts the Milvus vector engine |
| **watsonx.ai Runtime** | AI / Machine Learning | Runs embedding models and LLMs |
| **watsonx.ai Studio** | AI / Machine Learning | The project workspace UI |
| **Cloud Object Storage** | Storage | Storage backend for Milvus |

> ⚠️ **Critical — Region:** All your ITZ services are in **London (eu-gb)**. Every time you log into the watsonx.ai portal, confirm the region selector in the top-right corner shows **"London"**. If it shows Dallas or any other region, your services will not be visible and dropdowns will appear empty.

---

## Phase 1 — Provision Milvus in watsonx.data

**Goal:** Add a running Milvus vector database engine to your watsonx.data instance.

---

### Step 1.1 — Open the watsonx.data Web Console

1. Go to **[cloud.ibm.com/resources](https://cloud.ibm.com/resources)**
2. Under the **Databases** section, find your watsonx.data instance (named something like `itz-wxdata-XXXXXXXX-lgrfa94k`)
3. Click on the instance name to open its details page
4. Click **"Open web console"**

> ⚠️ **Important:** Click **"Open web console"** — NOT **"Launch in watsonx"**. The "Launch in watsonx" button takes you to a data query interface. The "Open web console" button opens the watsonx.data admin console where Infrastructure Manager lives.

---

### Step 1.2 — Register IBM Cloud Object Storage

Before adding Milvus, you must register a storage bucket for Milvus to use. Milvus (Starter size and above) requires external object storage.

**Step 1.2a — Create a bucket in IBM Cloud Object Storage**

1. Open a new browser tab and go to **[cloud.ibm.com/resources](https://cloud.ibm.com/resources)**
2. Under **Storage**, click on your Cloud Object Storage instance (named something like `itz-cos-XXXXXXXX-lgrfa94k`)
3. Click **"Buckets"** in the left sidebar
4. Click **"Create bucket"** (top right)
5. Choose **"Quickly create a bucket"**
6. Give the bucket a simple lowercase name (e.g. `milvus-poc-bucket`)
7. Click **"Create bucket"**
8. When asked to upload files — click **"Next"** to skip. Files will be added later through watsonx.ai.
9. Note down the bucket name — you will need it shortly.

> ⚠️ **Important — Bucket region:** When the bucket is created, it may default to a US region (e.g. Washington DC / us-east) even if your COS instance is in London. To find the actual region of your bucket:
> - Click on the bucket → click **"Configuration"** tab → look at the **"Location"** field
> - Note whether it says `us-east`, `eu-gb`, or another region — this determines which endpoint URL to use later.

**Step 1.2b — Create HMAC credentials**

1. From your COS instance page, click **"Service credentials"** in the left sidebar
2. Check if any credentials already exist — if one exists, expand it and look for a `cos_hmac_keys` section containing `access_key_id` and `secret_access_key`
3. If no HMAC keys exist, click **"New credential"**:
   - **Name**: anything (e.g. `milvus-hmac-creds`)
   - **Role**: `Writer`
   - **Include HMAC Credential**: toggle this **ON** ✅ — this is mandatory
   - **Control by Secrets Manager**: toggle this **OFF** ✅ — leave it off or you will get an error
4. Click **Add**
5. Expand the new credential and note down:
   - `access_key_id` (this is your **Access key**)
   - `secret_access_key` (this is your **Secret key**)

> ⚠️ **The HMAC toggle is mandatory.** Without it, the credential will only contain IAM keys, not the S3-compatible access/secret keys that watsonx.data needs to connect to COS.

**Step 1.2c — Find your bucket endpoint URL**

The endpoint depends on the region your bucket was created in:

| Bucket region | Endpoint URL to use |
|---|---|
| Washington DC (us-east) | `https://s3.us-east.cloud-object-storage.appdomain.cloud` |
| London (eu-gb) | `https://s3.eu-gb.cloud-object-storage.appdomain.cloud` |
| US South (us-south) | `https://s3.us-south.cloud-object-storage.appdomain.cloud` |
| EU Cross-region (eu-geo) | `https://s3.eu.cloud-object-storage.appdomain.cloud` |

> ⚠️ **Do NOT use** the `endpoints` URL from the service credential JSON (it shows `https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints`) — that is a directory listing URL, not the actual S3 endpoint.
>
> To confirm the exact endpoint: In your COS instance → click **"Endpoints"** in the left sidebar → set **Resiliency** to `Regional` and **Location** to your bucket's region → copy the **Public** endpoint.

**Step 1.2d — Register the storage in watsonx.data**

1. Go back to the **watsonx.data web console**
2. Click **"Infrastructure Manager"** in the left sidebar
3. Click **"Add component"** (top right)
4. Select **"IBM Cloud Object Storage"** → click **Next**
5. Fill in the fields:
   - **Display name**: anything (e.g. `My-cos-mun`)
   - **Bucket name**: the exact bucket name you created (e.g. `milvus-poc-bucket`)
   - **Endpoint**: the endpoint URL from the table above (matching your bucket's region)
   - **Region**: select the region matching your bucket
   - **Access key**: paste your `access_key_id`
   - **Secret key**: paste your `secret_access_key`
6. Click **"Test connection"**
   - ✅ If successful → click **"Associate"**
   - ❌ If it fails → double-check the bucket name, endpoint, and region match exactly. The most common cause of failure is a mismatch between the bucket's actual region and the endpoint/region entered.

---

### Step 1.3 — Add the Milvus Engine

1. In the **Infrastructure Manager**, click **"Add component"** (top right)
2. Select **"Milvus"** → click **Next**
3. Fill in:
   - **Display name**: anything (e.g. `my-milvus-MUN`)
   - **Size**: **Starter** (suitable for POC — supports up to 1 million vectors)
4. In the **Storage** dropdown — select the COS storage you just registered (e.g. `My-cos-mun`)
5. In the **Path** field — type `milvus` (watsonx.data will append a unique service ID automatically)
6. Click **"Create"**
7. Wait ~2–5 minutes for the Milvus status to show **"Running"** ✅

> ℹ️ **Why Starter and not Lite?** In ITZ environments the free "Lite" size is not available. Starter is the smallest available size. It uses Resource Units (RUs) from your ITZ allocation — not your personal credit card.

**Once Milvus is Running — note down your connection details:**

1. Click on your Milvus tile in Infrastructure Manager
2. Click **"View connect details"**
3. Note down:
   - **GRPC host** (long UUID-format hostname ending in `.lakehouse.cloud.ibm.com`)
   - **GRPC port** (typically `31775`)
   - **SSL Certificate** (the full `-----BEGIN CERTIFICATE-----` block — you can use **"Copy JSON snippet"** or **"Export JSON"** to capture everything at once)

---

## Phase 2 — Set Up the watsonx.ai Project

**Goal:** Create a watsonx.ai project (not Watson Studio) and associate the watsonx.ai Runtime service so that foundation model tools are available.

---

### Step 2.1 — Navigate to the Correct Portal

1. Go to **[dataplatform.cloud.ibm.com/wx/home](https://dataplatform.cloud.ibm.com/wx/home)**

> ⚠️ **This is not the same as IBM Cloud Pak for Data.** If the top navigation bar shows links like **"Foundation models"**, **"Projects"**, and **"Deployments"** — you are in the right place.
>
> ⚠️ **Check the region selector** in the top-right corner. It must show **"London"**. If it shows anything else, click it and switch to London before continuing. All ITZ services are in London and will not appear in dropdowns if you are in the wrong region.

---

### Step 2.2 — Use the Sandbox Project

When you navigate to `dataplatform.cloud.ibm.com/wx/home` in the correct region, you will find a **pre-existing sandbox project** in your Projects list. Its name will look like:

`student_lgrfa94k_XXXXXXXXXXXXXXXX@techzone.ibm.com's sandbox`

**Use this project** — do not create a new one. The sandbox project is pre-configured for your ITZ environment.

> ⚠️ **Do NOT use any project created from IBM Cloud Pak for Data** (the non-`/wx/` URL). Those projects are Watson Studio type and do not have foundation model tools (Prompt Lab, Ground gen AI, etc.). They will show options like "Build ML models automatically", "Visual flow", and "Notebooks" — but NOT "Ground gen AI with vectorized documents". If you see only those options, you are in the wrong project type.

---

### Step 2.3 — Associate the watsonx.ai Runtime Service

This step is **mandatory**. Without it, the "watsonx.data Milvus" vector store option will be visible but unclickable (greyed out) in Phase 3.

> ⚠️ **You must complete the pre-registration step below BEFORE attempting to associate the service.** In ITZ environments, the Runtime service will not appear or will have a greyed-out checkbox in the Associate service list until it has been launched into the watsonx context at least once. Do not skip this.

---

#### Part A — Pre-register the Runtime (do this first)

1. Go to **[cloud.ibm.com/resources](https://cloud.ibm.com/resources)**
2. Expand the **"AI / Machine Learning"** section by clicking the arrow on the left
3. Find the row for your watsonx.ai Runtime — it will show:
   - **Name**: `itz-ml-XXXXXXXX-lgrfa94k`
   - **Product**: `watsonx.ai Runtime`
   - **Location**: `London (eu-gb)`
4. Click the **instance name as a hyperlink** (the blue underlined text in the Name column) — hovering over it will show a tooltip with the full name confirming it is the correct row
5. This opens the instance detail page in a new view
6. On that page, find the **"Launch in"** button (may show as a dropdown with an arrow) → click the dropdown → select **"IBM watsonx"**
7. You will be redirected to **[dataplatform.cloud.ibm.com/wx/home](https://dataplatform.cloud.ibm.com/wx/home)**

> ℹ️ Simply being redirected to the watsonx home page is all that is needed. The Runtime is now registered in the correct context. You do not need to do anything further on that page.

---

#### Part B — Associate the Runtime with your project

1. Navigate back to your sandbox project → click the **"Manage"** tab (top navigation bar)
2. Click **"Services & integrations"** in the left sidebar
3. Click **"Associate service"** (blue button, top right)
4. The list will now show your watsonx.ai Runtime instance (`itz-ml-XXXXXXXX-lgrfa94k`) with a **checkable checkbox** ✅
5. Check the checkbox next to the Runtime instance
6. Click **"Associate"**
7. Confirm the Runtime now appears under the **"IBM services"** tab of Services & integrations ✅

> ⚠️ **If the checkbox is still greyed out after completing Part A:** Make sure you are in the correct region (**London**) in the watsonx portal before going to Manage → Services & integrations. A region mismatch will still cause the checkbox to be unclickable.

---

## Phase 3 — Connect to Milvus, Upload a Document, and Create a Vector Index

**Goal:** Upload a document, have watsonx.ai vectorize it, and store the vectors in your Milvus engine.

---

### Step 3.1 — Open "Ground gen AI with vectorized documents"

1. Inside your sandbox project, click the **"Assets"** tab
2. Click **"New asset"**
3. In the asset catalog, look for the section **"Work with foundation models"**
4. Click **"Ground gen AI with vectorized documents"**

> ⚠️ **If you don't see "Work with foundation models" or the option is missing:**
> - You are either in the wrong project type (Watson Studio instead of watsonx.ai) → go back to Step 2.2
> - Or the Runtime service is not associated → go back to Step 2.3
> - Try searching for `vector` in the search bar at the top of the asset catalog

---

### Step 3.2 — Select watsonx.data Milvus as the Vector Store

1. In the left panel you will see three options: **In memory**, **watsonx.data Milvus**, **Elasticsearch**
2. Click **"watsonx.data Milvus"**

> ⚠️ **If "watsonx.data Milvus" is visible but not clickable (greyed out):** The Runtime service is not associated. Go back to Step 2.3 and complete it, then return here.

3. Fill in the **"Define details"** section on the left:
   - **Name**: anything (e.g. `milvus-rag-index`)
   - **Description**: optional

4. Fill in the **"Vector database details"** section on the right:
   - Select **"Automatically connect to Milvus on watsonx.data"**
   - In the **watsonx.data instance** dropdown, select your instance (e.g. `itz-wxdata-XXXXXXXX-lgrfa94k`)
   - In the **Milvus instance** dropdown, select your Milvus engine (e.g. `my-milvus-MUN`)
   - Click **"Create connection"**

---

### Step 3.3 — Complete the Milvus Connection Form

Clicking "Create connection" opens a **"Connect to a data source: IBM watsonx.data Milvus"** form. This form has several sections in the left sidebar. Complete them as follows:

**Connection overview:**
- **Name**: auto-filled (e.g. `watsonX-data-milvus-my-milvus-MUN`) — leave as-is or rename

**Connection details:**
- **Hostname**: your Milvus **GRPC host** (from Step 1.3 connect details)
- **Port**: your Milvus **GRPC port** (typically `31775`)
- **Database**: leave **empty** (defaults to `default`)

**Credentials:**

> ⚠️ **Credential type:** When asked Personal vs Shared — select **Personal**.

- Click the **pencil/edit icon** next to the credential field
- **Username**: `ibmlhapikey_` followed immediately by your full ITZ email address
  - Example: `ibmlhapikey_student_lgrfa94k_6ac549b58be887b17d66083d_1@techzone.ibm.com`
  - The `ibmlhapikey_` prefix is **fixed** — do not replace or remove it
- **Password**: your IBM Cloud API key (NOT an IAM token — see warning below)

> ⚠️ **How to get your IBM Cloud API key:**
> 1. Go to **[cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys)**
> 2. Do NOT use the pre-existing `cpd-apikey-...` key — it is a system key managed by Watson Studio and must not be used
> 3. Click **"Create"** → give it a name (e.g. `milvus-poc-key`)
> 4. When creating: **"Control by Secrets Manager"** must be toggled **OFF**, **Role** set to `Writer`
> 5. **Copy the key value immediately** — it is only shown once and cannot be retrieved later
> 6. Paste this value as the **Password** in the connection form

> ⚠️ **API key vs IAM token — common mistake:** The password must be a short IBM Cloud API key (typically 44 characters, containing letters, numbers, hyphens and underscores). It must NOT be an IAM token (a very long JWT string containing dots, starting with `eyJ...`). If you use the JSON snippet import feature, it may auto-populate an IAM token into the password field — if so, manually clear the password field and paste your API key directly.

**Certificates:**
- Check **"Port is SSL-enabled"** ✅ — this is mandatory for watsonx.data Milvus
- In the **SSL Certificate** field, paste the full SSL certificate from your Milvus connect details page
- The certificate will contain **3 certificates chained together** — this is normal. Paste the entire block from the first `-----BEGIN CERTIFICATE-----` to the last `-----END CERTIFICATE-----`

> ℹ️ **Easiest way to get the SSL certificate and all connection details at once:**
> In the watsonx.data web console → Infrastructure Manager → click your Milvus tile → **"View connect details"** → click **"Copy JSON snippet"** or **"Export JSON"**. Then in the connection form, click **"Enter JSON snippet"** on the Connection overview page and paste the JSON. This auto-fills the hostname, port, and SSL certificate. **However**, after importing the JSON, manually verify and re-enter the password field with your plain API key — the JSON import may overwrite it with an IAM token.

**Test and create:**
1. Click **"Test connection"** (top right of the form)
2. ✅ If successful → click **"Create"**
3. ❌ If it fails with `token is malformed` → the password field contains an IAM token, not an API key. Clear and re-enter your API key.
4. ❌ If it fails with `bucket does not exist or credentials are not valid` → the hostname, port, or SSL certificate is incorrect. Re-copy from "View connect details".

---

### Step 3.4 — Select a Database and Embedding Model

After the connection is created, you are returned to the vector index setup page:

1. **Connection** dropdown: your newly created connection should be auto-selected (e.g. `my-milvus-MUN`)
2. **Database** dropdown: select **`default`**
3. **Embeddings model** dropdown: select **`granite-embedding-278m-multilingual`**
   - This is IBM's own multilingual embedding model and the best choice for a general POC
   - Other options (slate, multilingual-e5) are also valid but granite is recommended for first-time setup
4. Click **"Next"**

---

### Step 3.5 — Create a Collection and Upload a Document

The next page asks you to **"Select collection"**. A collection is like a table in Milvus that holds your vectors.

1. Click **"New collection"** (blue button, top right)
2. Enter a collection name (e.g. `mun`)
   - The `wx_` prefix is added automatically — your collection will be saved as `wx_mun`
3. Click **Create/Confirm** — you are taken to the **"Create collection"** page

On the **Create collection** page:

4. **Collection name**: already filled in ✅
5. **Add files**: click **"Browse"** and select your document from your computer
   - Supported formats: **PDF, DOCX, PPTX, TXT, JSON, HTML, CSV, YAML, XML, XLSX**
   - Recommended for a first test: a simple 1–5 page PDF
6. **Settings — use these values for best retrieval accuracy:**
   - **Text chunk size**: `512`
   - **Text chunk overlap**: `100`
   - **Split PDF**: `On` ✅
   - **Distance metric**: `COSINE`

   > ⚠️ **Do NOT leave chunk size at the default `2000`.** Large chunks cause poor retrieval accuracy because each chunk covers too much content — the similarity search cannot pinpoint specific facts. `512` with `100` overlap is the recommended setting for short-to-medium policy documents.
   >
   > ⚠️ **Distance metric must be COSINE** for text/NLP tasks. The default `L2 (Euclidean)` is designed for image and numerical data, not text embeddings. Cosine measures the angle between vectors which correctly captures semantic similarity between sentences.

7. Click **"Create"** (bottom right)

watsonx.ai will now:
- Split the document into chunks
- Vectorize each chunk using the granite embedding model
- Write the resulting vectors into your Milvus collection

This takes approximately **1–3 minutes** for a small document.

---

### Step 3.6 — Confirm the Vector Index Was Created Successfully

After creation completes, you are taken to the **vector index details page**. Confirm the following:

| Field | Expected value |
|---|---|
| Vector store | `watsonx.data` |
| Vector store connection | your connection name (e.g. `my-milvus-MUN`) |
| Embeddings model | `ibm/granite-embedding-278m-multilingual` |
| Milvus database | `default` |
| Milvus collection | `wx_mun` (or whatever you named it) |
| Text chunk size | `512` |
| Text chunk overlap | `100` |
| Split PDF | `On` |
| Distance metric | `COSINE` |

Click the **"Data"** tab to confirm the document chunks were written successfully.

### Step 3.7 — Update Search Settings (Top K)

1. On the vector index details page, click **"Edit search settings"** (next to Search settings)
2. Change **Top K** from `3` to `6`
3. Click **Save**

> ℹ️ **Top K** controls how many chunks Milvus retrieves per query. The default of `3` is often too few for policy documents where relevant information may be spread across multiple sections. `6` gives the LLM more context to work with without overwhelming it.

**Phase 3 is complete.** ✅ Your document is now vectorized and stored in Milvus with optimal retrieval settings.

---

---

## Phase 4 — Query the Document with an LLM (Prompt Lab)

**Goal:** Ask questions about your document using a foundation model grounded in your Milvus vector index.

---

### Step 4.1 — Open Prompt Lab from the Vector Index

1. Go to your project → **Assets** tab → click **`milvus-rag-index`**
2. In the right sidebar, click **"Open in Prompt Lab"**

> ℹ️ Always open Prompt Lab this way — it automatically attaches `milvus-rag-index` as the grounding source. If you open Prompt Lab directly from New Asset, you will need to attach the index manually (see Step 4.3).

---

### Step 4.2 — Select a Foundation Model

1. Click the **Model** dropdown in the top bar (shows the current model name)
2. The available models depend on your ITZ environment. You will see options such as:
   - `llama-3-3-70b-instruct` (Meta)
   - `llama-4-maverick-17b-128e-instruct` (Meta) — recommended for best accuracy
   - `mistral-small-3-1-24b-instruct` (Mistral AI)
3. Select **`llama-4-maverick-17b-128e-instruct`** for best results

> ⚠️ **IBM Granite models (granite-13b-chat etc.) may not be available** in ITZ environments. Use `llama-4-maverick` as the best available alternative.

---

### Step 4.3 — Attach the Milvus Vector Index as Grounding (if not already attached)

If you opened Prompt Lab directly (not via "Open in Prompt Lab"), the grounding index will not be attached. Look at the bottom of the chat input area:

- ✅ If you see a grey pill tag showing **`milvus-rag-index ×`** → grounding is already attached, skip this step
- ❌ If the tag is not there → attach it now:
  1. Click the **document/grounding icon** at the bottom left of the chat input (looks like a page with lines)
  2. A panel opens on the right — click **"Select or create vec..."** dropdown
  3. Select **`milvus-rag-index`**
  4. The tag will appear at the bottom of the chat input ✅

> ⚠️ **The grounding index must be attached every new Prompt Lab session.** It does not persist automatically between sessions. Every time you log back in and open Prompt Lab, re-attach `milvus-rag-index` using the steps above before asking questions.

---

### Step 4.4 — Add a System Prompt

A system prompt instructs the LLM to stay faithful to the retrieved document context and not use its own training knowledge. Without it, the model may hallucinate answers that contradict the document.

1. Click the **⚙️ gear icon** in the top right toolbar (tooltip: "Edit system prompt")
2. Paste the following system prompt:

```
You are a helpful assistant answering questions about a
university policy document. Answer ONLY based on the document
context retrieved and provided to you. Do not use any outside
knowledge or training data. If the answer appears in the
context, quote the relevant text exactly and precisely.
If the answer is not found in the context, respond with:
"I cannot find that information in the provided document."
```

3. Close the system prompt dialog

> ⚠️ **The system prompt must be re-entered every new session** unless you save the prompt (see Step 4.6). Without a system prompt, the LLM may answer "10 business days" when the document clearly states "15 business days" — it overrides retrieved context with its own training data.

---

### Step 4.5 — Ask Questions About Your Document

Type a question in the **"Type something..."** chat input and press Enter. The pipeline will:

1. Convert your question to a vector using the embedding model
2. Search Milvus for the `6` most similar chunks (Top K = 6)
3. Pass those chunks as context to the LLM
4. Generate an answer grounded in your document

**Example questions for the MUN Code of Conduct document:**

| Question | Expected answer |
|---|---|
| What are the consequences for plagiarism? | Formal warning up to expulsion |
| How many business days does a student have to submit a written appeal? | 15 business days |
| What support resources are available to students? | Counselling Centre, Student Advocacy Office, Ombudsperson, etc. |
| What behaviours violate academic integrity? | Plagiarism, cheating, fabrication, contract cheating, etc. |
| What is the appeals process? | Submit written appeal to Senate Appeals Committee within 15 business days |

Each answer will include a **Sources** section showing which document the chunks came from, confirming that Milvus retrieval is working.

---

### Step 4.6 — Save Your Prompt for Future Sessions

To avoid re-entering the system prompt every session:

1. Click **"Unsaved"** in the top bar
2. Click **"Save as"**
3. Select **"Prompt"** (not Session)
4. Name it `milvus-rag-prompt`
5. Click **Save**

Next session, find it under **"Saved prompts"** in the left sidebar (the `[...]` icon).

---

### How to Return to This Exact Setup After Logging Out

| Step | Action |
|---|---|
| 1 | Go to [dataplatform.cloud.ibm.com/wx/home](https://dataplatform.cloud.ibm.com/wx/home) |
| 2 | Confirm region is **London** (top right) |
| 3 | Projects → open sandbox project |
| 4 | Assets → click `milvus-rag-index` → **"Open in Prompt Lab"** |
| 5 | Re-attach `milvus-rag-index` grounding if not auto-attached |
| 6 | Click ⚙️ gear → re-enter system prompt (or load saved prompt) |
| 7 | If you get a `401 Authorization failed` error → your API key expired. Go to [cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys), create a new key, and update the password in the `watsonX-data-milvus-my-milvus-MUN` connection asset |

---

### Understanding RAG Accuracy

The RAG pipeline has two separate components that can each affect accuracy:

| Component | What it does | How to improve it |
|---|---|---|
| **Milvus retrieval** | Finds relevant chunks from your document | Smaller chunk size (`512`), COSINE metric, higher Top K (`6`) |
| **LLM generation** | Generates an answer from the retrieved chunks | System prompt, lower Temperature (`0`), correct model choice |

> ℹ️ If the **Sources** section in a response is empty → retrieval failed (Milvus issue)
> If Sources shows the document but the answer is wrong → generation failed (LLM/prompt issue)

**Phase 4 is complete.** ✅ You now have a fully working end-to-end RAG pipeline.

---

## Common Issues and Fixes

| Issue | Cause | Fix |
|---|---|---|
| "Ground gen AI with vectorized documents" not visible | Wrong project type (Watson Studio) | Use the sandbox project at `/wx/home` in London region |
| "watsonx.data Milvus" is greyed out | Runtime service not associated | Complete Step 2.3 — associate `itz-ml-...` Runtime via "Launch in IBM watsonx" workaround |
| Associate service list is empty | Wrong region (Dallas instead of London) | Switch region selector to London (top-right of watsonx portal) |
| COS storage test connection fails | Wrong endpoint or bucket region mismatch | Check bucket Configuration tab for actual region; use matching endpoint from table in Step 1.2c |
| Milvus test connection fails with `token is malformed` | IAM token used as password instead of API key | Clear password field; paste plain API key from `cloud.ibm.com/iam/apikeys` |
| Milvus test connection fails with `401 Unauthorized` | Wrong username format or wrong API key | Username must be `ibmlhapikey_<full-email>`. Create a fresh API key if unsure. |
| Runtime checkbox greyed out in Associate service | ITZ permissions restriction | Use the "Launch in IBM watsonx" workaround described in Step 2.3 |
| Cannot create new services (permission error) | ITZ account has restricted permissions | Do not create new services — use the pre-provisioned ITZ instances only |
| `401 Authorization failed` grounding error | API key expired between sessions | Create a new API key at `cloud.ibm.com/iam/apikeys` and update the connection asset password |
| `{"loginUrl":"/auth/iamid/login..."}` error | Session timed out | Log back in at `dataplatform.cloud.ibm.com/wx/home` |
| LLM gives wrong answer despite correct retrieval | Model hallucinating over retrieved context | Add system prompt (Step 4.4) and set Temperature to `0` |
| Sources section is empty in LLM response | Retrieval returning no chunks | Verify `milvus-rag-index` is attached; check Top K is `6`; re-test index on the Test tab |
| Grounding index not attached after login | Does not persist between sessions | Re-attach `milvus-rag-index` every session via the grounding icon (Step 4.3) |

---

## Architecture Summary

```
MUN_Code_of_Conduct.pdf (or any document)
            │
            ▼
  watsonx.ai Embedding Model
  ibm/granite-embedding-278m-multilingual
  (chunks document → converts each chunk to a vector)
            │
            ▼
  Milvus Vector DB — collection: wx_mun
  hosted in watsonx.data (itz-wxdata-...)
  backed by IBM Cloud Object Storage (itz-cos-...)
            │
            ▼  ← vector similarity search at query time
  watsonx.ai LLM — Prompt Lab
  (itz-ml-... Runtime, London region)
            │
            ▼
  Answer grounded in document content  ← Phase 4
```

---

## Quick Reference

| Item | Value |
|---|---|
| watsonx.ai portal URL | [dataplatform.cloud.ibm.com/wx/home](https://dataplatform.cloud.ibm.com/wx/home) |
| IBM Cloud resource list | [cloud.ibm.com/resources](https://cloud.ibm.com/resources) |
| IBM Cloud API keys | [cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys) |
| Required region | **London (eu-gb)** for all ITZ services |
| Milvus auth username format | `ibmlhapikey_<your-full-itz-email>` |
| Milvus auth password | IBM Cloud API key (short string, NOT a JWT token) |
| Milvus GRPC port | `31775` |
| SSL required | Yes — paste full certificate chain (3 certs) |
| Supported document formats | PDF, DOCX, PPTX, TXT, JSON, HTML, CSV, YAML, XML, XLSX |
| Recommended embedding model | `granite-embedding-278m-multilingual` |
| Recommended chunk size | 2000 (default) |
| Recommended chunk overlap | 200 (default) |

#!/usr/bin/env python3
"""
Shared helper functions for the lab.

These wrap the same operations the technical notebook spells out cell-by-cell,
so the *guided* (non-technical) notebook can keep each visible cell to a single
line. They are also used by `verify_setup.py` for the local preflight check.

Heavy third-party imports (ibm_watsonx_ai, prestodb, pymilvus, …) are done
lazily inside the functions that need them, so this module imports cleanly even
in an environment where only some packages are installed.

Config comes from config/lab_config.yaml; credentials come from the environment
(a local .env file, or values you paste into the notebook).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "lab_config.yaml"


# --------------------------------------------------------------------------- #
# Config + credentials
# --------------------------------------------------------------------------- #
def load_config(path: Optional[Path] = None) -> dict:
    """Load config/lab_config.yaml into a dict."""
    import yaml  # PyYAML

    path = path or _CONFIG_PATH
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_env() -> None:
    """Load a local .env file into os.environ if python-dotenv is available."""
    try:
        from dotenv import load_dotenv

        load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    except ImportError:
        pass  # fine — values may already be in the real environment


def _require(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        raise RuntimeError(
            f"Missing credential: {name}. Set it in your .env file "
            f"(copy .env.template) or paste it into the notebook cell."
        )
    return val


# --------------------------------------------------------------------------- #
# watsonx.ai client
# --------------------------------------------------------------------------- #
def get_client(url: Optional[str] = None,
               api_key: Optional[str] = None,
               project_id: Optional[str] = None):
    """Return an authenticated watsonx.ai APIClient."""
    from ibm_watsonx_ai import APIClient, Credentials

    cfg = load_config()
    url = url or os.environ.get("WATSONX_URL") or cfg["url"]
    api_key = api_key or _require("IBM_CLOUD_API_KEY")
    project_id = project_id or _require("WATSONX_PROJECT_ID")
    return APIClient(Credentials(url=url, api_key=api_key), project_id=project_id)


# --------------------------------------------------------------------------- #
# Presto (SQL) — read the catalogued table in place
# --------------------------------------------------------------------------- #
def get_presto_connection():
    """Open a Presto DB-API connection using env credentials + config catalog/schema."""
    import prestodb

    cfg = load_config()
    host = _require("PRESTO_HOST")
    port = int(os.environ.get("PRESTO_PORT", "443"))
    user = _require("PRESTO_USER")
    pwd = _require("PRESTO_PWD")
    return prestodb.dbapi.connect(
        host=host, port=port, user=user,
        catalog=cfg["catalog"], schema=cfg["schema"],
        http_scheme="https",
        auth=prestodb.auth.BasicAuthentication(user, pwd),
    )


def run_sql(sql: str, conn=None):
    """Run a SQL query and return a pandas DataFrame."""
    import pandas as pd

    conn = conn or get_presto_connection()
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return pd.DataFrame(cur.fetchall(), columns=cols)


# --------------------------------------------------------------------------- #
# PDF -> chunks -> embeddings -> Milvus  (RAG)
# --------------------------------------------------------------------------- #
def read_pdf_chunks(pdf_path: str,
                    size: Optional[int] = None,
                    step: Optional[int] = None,
                    min_len: Optional[int] = None) -> list[str]:
    """Extract text from a PDF and split into overlapping fixed-size chunks."""
    from pypdf import PdfReader

    cfg = load_config()
    size = size or cfg["chunk_size"]
    step = step or cfg["chunk_step"]
    min_len = min_len or cfg["chunk_min_len"]

    reader = PdfReader(pdf_path)
    full = "\n".join((p.extract_text() or "") for p in reader.pages)
    chunks = []
    for i in range(0, len(full), step):
        piece = full[i:i + size].strip()
        if len(piece) > min_len:
            chunks.append(piece)
    return chunks


def embed_and_insert(chunks: list[str], client, project_id: Optional[str] = None):
    """Embed chunks with the watsonx.ai model and insert them into Milvus.

    Returns the loaded pymilvus Collection, ready to search.
    """
    from ibm_watsonx_ai.foundation_models import Embeddings
    from pymilvus import (connections, Collection, FieldSchema,
                          CollectionSchema, DataType, utility)

    cfg = load_config()
    project_id = project_id or _require("WATSONX_PROJECT_ID")

    emb = Embeddings(model_id=cfg["embedding_model_id"],
                     api_client=client, project_id=project_id)
    vectors = emb.embed_documents(texts=chunks)

    connections.connect(host=_require("MILVUS_HOST"),
                        port=os.environ["MILVUS_PORT"],
                        user=_require("MILVUS_USER"),
                        password=_require("MILVUS_PWD"), secure=True)

    name = cfg["milvus_collection"]
    if utility.has_collection(name):
        utility.drop_collection(name)  # keep reruns clean
    schema = CollectionSchema([
        FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema("text", DataType.VARCHAR, max_length=4000),
        FieldSchema("vector", DataType.FLOAT_VECTOR, dim=len(vectors[0])),
    ])
    col = Collection(name, schema)
    col.insert([chunks, vectors])
    col.create_index("vector", {"metric_type": "L2", "index_type": "AUTOINDEX"})
    col.load()
    return col, emb


def semantic_search(query: str, col, emb, limit: int = 3):
    """Return the most relevant passages for a natural-language query."""
    q = emb.embed_query(text=query)
    hits = col.search([q], "vector", {"metric_type": "L2"},
                      limit=limit, output_fields=["text"])
    return [(round(h.distance, 2), h.entity.get("text")) for h in hits[0]]


# --------------------------------------------------------------------------- #
# Text-to-SQL + charting with Granite
# --------------------------------------------------------------------------- #
def _granite(client, project_id: Optional[str] = None, max_new_tokens: int = 200):
    from ibm_watsonx_ai.foundation_models import ModelInference

    cfg = load_config()
    project_id = project_id or _require("WATSONX_PROJECT_ID")
    return ModelInference(
        model_id=cfg["granite_model_id"], api_client=client, project_id=project_id,
        params={"decoding_method": "greedy", "max_new_tokens": max_new_tokens})


_FORBIDDEN = (" insert", " update", " delete", " drop", " alter", " create", " merge")


def assert_read_only(sql: str) -> None:
    """Guard: raise unless `sql` is a single read-only SELECT."""
    low = sql.lower()
    assert low.startswith("select"), "Not a SELECT"
    assert not any(k in low for k in _FORBIDDEN), "Mutation blocked"


def question_to_sql(question: str, client, project_id: Optional[str] = None) -> str:
    """Ask Granite to turn an English question into ONE read-only Presto query."""
    cfg = load_config()
    fq = f"{cfg['catalog']}.{cfg['schema']}.{cfg['table']}"
    schema_ddl = (f"{cfg['table']}(year INT, landings_tonnes DOUBLE, "
                  f"licensed_fishers INT, fishery_status VARCHAR)")
    prompt = (f"Translate the question into ONE Presto SQL query.\n"
              f"Table: {fq} as {schema_ddl}\n"
              f"Rules: SELECT only, no DDL/DML, add LIMIT 1000. Return ONLY the SQL.\n"
              f"Question: {question}")
    sql = _granite(client, project_id).generate_text(prompt=prompt).strip().strip("`").strip()
    assert_read_only(sql)  # never run model SQL blind
    return sql


def generate_chart_code(df, client, project_id: Optional[str] = None,
                        instruction: str = "plot landings_tonnes vs year as a line chart, "
                                           "add a vertical marker and label at 1992 "
                                           "(the cod moratorium)") -> str:
    """Ask Granite to write matplotlib code against df's columns."""
    prompt = (f"You are a Python data-viz assistant. A pandas dataframe `df` has "
              f"columns: {list(df.columns)}.\n"
              f"Write matplotlib code to {instruction}, give it a clear title, and "
              f"call plt.show(). Return ONLY code.")
    return _granite(client, project_id, max_new_tokens=400).generate_text(prompt=prompt)

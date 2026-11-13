import chromadb

from conftest import make_client

# Self-contained test data, so the tests do not depend on files on disk.
TEXTS = {
    "python.txt": (
        "Python is a high-level, general-purpose programming language developed by "
        "Guido van Rossum and first released in 1991. It has a clean, readable syntax "
        "and is widely used for web development, data science and automation."
    ),
    "got.txt": (
        "Game of Thrones is a popular fantasy television series that aired on HBO. "
        "It is based on the book series A Song of Ice and Fire by George R.R. Martin "
        "and is set in the fictional world of Westeros and Essos."
    ),
    "llm.txt": (
        "A large language model is a neural network trained on huge amounts of text "
        "to predict the next token. Modern LLMs use the transformer architecture and "
        "can answer questions, summarize documents and write code."
    ),
}


def post_doc(client, doc_id, text, name=None, headers=None):
    return client.post(
        "/documents",
        json={"document_id": doc_id, "file_name": name or f"{doc_id}.txt", "text": text},
        headers=headers or {},
    )


def read(name):
    return TEXTS[name]


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_index_search_and_filter(client):
    for name in ("python.txt", "got.txt", "llm.txt"):
        r = post_doc(client, name.removesuffix(".txt"), read(name), name)
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "indexed"

    r = client.post("/search", json={"query": "Python programming language", "top_k": 3})
    assert r.status_code == 200
    body = r.json()
    assert body["count"] >= 1
    assert body["results"][0]["document_id"] == "python"
    scores = [h["score"] for h in body["results"]]
    assert scores == sorted(scores, reverse=True)

    # Filtering to one document must only return that document's chunks.
    r = client.post(
        "/search",
        json={"query": "Python programming language", "top_k": 5, "document_ids": ["got"]},
    )
    assert {h["document_id"] for h in r.json()["results"]} == {"got"}


def test_reindex_unchanged_and_updated(client):
    text = read("python.txt")
    assert post_doc(client, "doc1", text).json()["status"] == "indexed"
    assert post_doc(client, "doc1", text).json()["status"] == "unchanged"

    r = post_doc(client, "doc1", "Completely different content about volcanoes and lava.")
    assert r.json()["status"] == "updated"

    # Old content must be gone.
    r = client.post("/search", json={"query": "Python programming language", "top_k": 5})
    texts = " ".join(h["text"].lower() for h in r.json()["results"])
    assert "python" not in texts
    assert client.get("/documents/doc1").json()["chunks"] == 1


def test_update_to_shorter_leaves_no_stale_chunks(tmp_path):
    c = make_client(tmp_path, chunk_size=10, overlap=2)
    long_text = " ".join(f"word{i}" for i in range(100))
    n_long = post_doc(c, "d", long_text).json()["chunks"]
    assert n_long > 3

    n_short = post_doc(c, "d", "just a short text now").json()["chunks"]
    assert n_short == 1
    assert c.get("/documents/d").json()["chunks"] == 1


def test_delete(client):
    post_doc(client, "a", read("python.txt"))
    post_doc(client, "b", read("got.txt"))

    r = client.delete("/documents/a")
    assert r.status_code == 200
    assert r.json()["deleted_chunks"] >= 1

    assert client.delete("/documents/a").status_code == 404
    assert client.get("/documents/a").status_code == 404

    r = client.post("/search", json={"query": "Python programming language", "top_k": 5})
    assert all(h["document_id"] != "a" for h in r.json()["results"])


def test_min_score_filters_everything(client):
    post_doc(client, "a", read("python.txt"))
    r = client.post(
        "/search",
        json={"query": "quantum chromodynamics gluon plasma", "top_k": 3, "min_score": 0.9},
    )
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_group_by_document(tmp_path):
    c = make_client(tmp_path, chunk_size=10, overlap=2)
    repeated = " ".join(["python is a programming language used widely"] * 12)
    post_doc(c, "x", repeated)
    post_doc(c, "y", "python programming language basics for beginners and learners")

    ungrouped = c.post("/search", json={"query": "python programming language", "top_k": 5}).json()
    grouped = c.post(
        "/search",
        json={"query": "python programming language", "top_k": 5, "group_by_document": True},
    ).json()

    assert [h["document_id"] for h in ungrouped["results"]].count("x") > 1
    ids = [h["document_id"] for h in grouped["results"]]
    assert len(ids) == len(set(ids)) == 2


def test_search_empty_store(client):
    r = client.post("/search", json={"query": "anything at all"})
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_validation_errors(client):
    assert post_doc(client, "bad id with spaces", "text").status_code == 422
    assert post_doc(client, "ok", "   ").status_code == 422
    assert client.post("/search", json={"query": "  a "}).status_code == 422
    assert client.post("/search", json={"query": "valid query", "top_k": 99}).status_code == 422


def test_auth(auth_client):
    c = auth_client
    assert c.get("/health").status_code == 200  # health stays open for Docker
    assert post_doc(c, "a", "hello world text").status_code == 401
    assert post_doc(c, "a", "hello world text", headers={"X-API-Key": "wrong"}).status_code == 401
    ok = post_doc(c, "a", "hello world text", headers={"X-API-Key": "secret"})
    assert ok.status_code == 200
    assert c.post("/search", json={"query": "hello world"}).status_code == 401
    r = c.post("/search", json={"query": "hello world"}, headers={"X-API-Key": "secret"})
    assert r.status_code == 200


def test_persistence_across_restart(tmp_path):
    c = make_client(tmp_path)
    post_doc(c, "keep", read("python.txt"))

    # New client = new PersistentClient on the same directory.
    c2 = make_client(tmp_path)
    assert c2.get("/documents/keep").status_code == 200
    r = c2.post("/search", json={"query": "Python programming language"})
    assert r.json()["results"][0]["document_id"] == "keep"
    assert chromadb  # imported to make the dependency explicit
from Search.search_engine import SearchEngine


engine = SearchEngine()


# USER INPUT

path = input("Enter Path: ").strip()

query = input(
    "Enter Your Question: "
).strip()

# SEARCH
engine.search(
    path,
    query,
    top_k=3
)
import embeddings_ctrl as ec
import os
import ollama, chromadb, time
from mattsollamatools import chunk_text_by_sentences
import config
from os import listdir
from os.path import isfile, join


# Load settings from configuration file.
cfg = config.Config('models.cfg')
EMBED_MODEL = cfg["embedmodel"]
COLLECTION_NAME = cfg['collection_name']
REF_DOCS_PATH = cfg['reference_docs_path']

chroma = chromadb.HttpClient(host="localhost", port=8000)
print(chroma.list_collections())
if any(
    collection.name == COLLECTION_NAME
    for collection in chroma.list_collections()
):
    print("deleting collection")
    chroma.delete_collection(COLLECTION_NAME)
collection = chroma.get_or_create_collection(
    name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
)

print(f'{EMBED_MODEL} embeddings selected.')

start_time = time.time()
files = [f for f in listdir(REF_DOCS_PATH) if isfile(join(REF_DOCS_PATH, f))]
text = ''
for path in files:
    relative_path = REF_DOCS_PATH + '/' + path
    filename = os.path.abspath(relative_path)
    print(f"\nDocument: {filename}")
    with open(filename, "rb") as f:

        text = f.read().decode("utf-8")
    chunks = chunk_text_by_sentences(
        source_text=text, sentences_per_chunk=7, overlap=0
    )
    print(f"{len(chunks)} chunks")
    for index, chunk in enumerate(chunks):
        if EMBED_MODEL == "navec":
            embed = ec.navec_embeddings(chunk)["embedding"]
        else:
            embed = ollama.embeddings(model=EMBED_MODEL, prompt=chunk)[
                "embedding"
            ]
        print(".", end="", flush=True)

        collection.add(
            [filename + str(index)],
            [embed],
            documents=[chunk],
            metadatas={"source": filename},
        )

print(f"\n--- {time.time() - start_time} seconds ---")

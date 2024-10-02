import embeddings_ctrl as ec
import ollama
import chromadb
import config


# Load settings from configuration file.
cfg = config.Config('models.cfg')
EMBED_MODEL = cfg["embedmodel"]
MAIN_MODEL = cfg["mainmodel"]
USE_CHAT = cfg['use_chat']
COLLECTION_NAME = cfg['collection_name']
PRINT_CONTEXT = cfg['print_context']


def get_collection() -> chromadb.Collection:
    """
    Creates and returns a Chroma collection. Collection contains reference
    documents and corresponding embeddings.

    Returns:
        chromadb.Collection: A Chroma collection.
    """
    chroma = chromadb.HttpClient(host="localhost", port=8000)
    collection = chroma.get_or_create_collection(COLLECTION_NAME)
    return collection


def make_answer(user_query: str) -> str:
    """ Make single answer."""

    collection = get_collection()
    query = user_query
    if EMBED_MODEL == 'navec':
        emb = ec.navec_embeddings(query)
    else:
        emb = ollama.embeddings(model=EMBED_MODEL, prompt=query)
    queryembed = emb["embedding"]
    relevantdocs = collection.query(
        query_embeddings=[queryembed], n_results=5)["documents"][0]
    context = "\n\n".join(relevantdocs)
    modelquery = f"{query} - Answer in Russian that question," \
                 + " point source, chapter number and page number" \
                 + " where it is," \
                 + " using the following text as a resource:" \
                 + f"{context}"

    if PRINT_CONTEXT is True:
        print("----------------------Request-------------------------")
        print(query)
        print("----------------------Context begin-------------------")
        print("docs: ", context)
        print("----------------------Context end---------------------")

    if USE_CHAT is True:
        response = ollama.chat(model=MAIN_MODEL, messages=[
            {
                'role': 'user',
                'content': query,
                'prompt': modelquery
            },
        ])

        print(response['message']['content'])
    else:
        stream = ollama.generate(model=MAIN_MODEL, prompt=modelquery,
                                 stream=True)
        res = ''
        for chunk in stream:
            if chunk["response"]:
                res += chunk['response']
    print('res=', res)
    return res


def main():
    """
    The main function.
    """

    collection = get_collection()
    run_flag = True
    print(f'Embedding model: {EMBED_MODEL}')
    print(f'Main model: {MAIN_MODEL}')

    print('\nAssistant for bike Suzuki Djebel 200 service is running.\n'
          'Enter your question or type "q" to exit.\n')

    if EMBED_MODEL == 'navec':
        print('Navec embeddings selected.\nType questions in Russian.\n')

    answer_tag = ">>> "
    query_tag = "<<< "

    while run_flag is True:
        query = input(query_tag)
        if query.capitalize() != 'Q' and query.capitalize() != 'Й':
            if EMBED_MODEL == 'navec':
                emb = ec.navec_embeddings(query)
            else:
                emb = ollama.embeddings(model=EMBED_MODEL, prompt=query)
            queryembed = emb["embedding"]
            relevantdocs = collection.query(
                query_embeddings=[queryembed], n_results=5)["documents"][0]
            context = "\n\n".join(relevantdocs)
            modelquery = f"{query} - Answer in Russian that question," \
                         + " point source, chapter number and page number" \
                         + " where it is," \
                         + " using the following text as a resource:" \
                         + f"{context}"

            if PRINT_CONTEXT is True:
                print("----------------------Request-------------------------")
                print(query)
                print("----------------------Context begin-------------------")
                print("docs: ", context)
                print("----------------------Context end---------------------")

            if USE_CHAT is True:
                response = ollama.chat(model=MAIN_MODEL, messages=[
                    {
                        'role': 'user',
                        'content': query,
                        'prompt': modelquery
                    },
                ])

                print(response['message']['content'])
            else:
                stream = ollama.generate(model=MAIN_MODEL, prompt=modelquery,
                                         stream=True)
                print(f'{answer_tag} Thinking...', end="", flush=True)
                shift_back_cursor = True
                for chunk in stream:
                    if chunk["response"]:
                        if shift_back_cursor is True:
                            print(f'\r{answer_tag}', end="", flush=True)
                            shift_back_cursor = False
                        print(chunk["response"], end="", flush=True)

            print("\n")
        else:
            print("Exit.")
            run_flag = False


if __name__ == "__main__":
    main()

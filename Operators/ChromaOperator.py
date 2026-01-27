import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from typing import List,Dict
from chromadb.api.models import Collection
import hashlib
from .WebOperator import WebOperator

class ChromaOperator:
    """"
    Performs various chroma db related operations
    """
    def __init__(self):
        load_dotenv()

    def save_rss_details(self,feeds:List[Dict]):
        """
        saves the relevant data from the rss feed
        in a chromadb
        """
        client = chromadb.PersistentClient(path=os.getenv("db_path"))
        embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=os.getenv("embedding_model")
        )

        collection = client.get_or_create_collection(
            name=os.getenv("feed_collection_name"),
            embedding_function=embedder,
            metadata={"hnsw:space": "cosine"}
        )

        for feed in feeds:
            self.__add_rss_details(feed, collection)

    def __add_rss_details(self, feed, vector_collection:Collection):
        """"
        Adds rss details to the db
        """
        try:
            article_text = f"{feed['title']}\n\n{feed['summary']}"
            id=self.__create_rss_id(feed)
            metadata = {
                "link": feed["link"],
                "downloadcomplete": "false"
            }
            ids=[id]
            docs=[article_text]
            metas=[metadata]

            vector_collection.add(ids=ids, documents=docs, metadatas=metas)

        except Exception as e:
            print(f"Error in adding rss feed to db :-{e}")

    def __create_rss_id(self,feed:Dict)->str:
        """"
        Generates a unique id for the rss feed
        """
        unique_str = f"{feed['link']}|{feed.get('published', '')}"
        return hashlib.sha256(unique_str.encode("utf-8")).hexdigest()

    def complete_downloads(self):
        """"
        scans the db
        checks if the any of the articles have not been completely downloaded
        downloads them
        """
        self.__get_incomplete_downloads();

    def search_db(self,query:str):
        """"
        Searching the vector collection
        """
        client = chromadb.PersistentClient(path=os.getenv("full_article_db_path"))
        embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=os.getenv("embedding_model")
        )
        collection = client.get_collection(
            name=os.getenv("articles_collection_name"),
            embedding_function=embedder
        )
        results = collection.query(
            query_texts=[query],
            n_results=int(os.getenv("top_k")),
        )
        ids = results["ids"]
        documents = results["documents"]
        distances = results["distances"]

        if not ids:
            print("Need to pass it to the main")

        print(distances)




    def __get_incomplete_downloads(self):
        client = chromadb.PersistentClient(path=os.getenv("db_path"))
        embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=os.getenv("embedding_model")
        )

        vector_collection = client.get_collection(
            name=os.getenv("feed_collection_name"),
            embedding_function=embedder,
        )

        results = vector_collection.get(
            where={"downloadcomplete": "false"}
        )
        ids = results["ids"]
        metadatas = results["metadatas"]

        if not ids:
            print("No pending downloads")
            return
        ids_to_update = []
        metas_to_update = []
        web_operator = WebOperator()
        for doc_id,meta in zip(ids, metadatas):
            link = meta.get("link")
            result=web_operator.get_webpage_text(link)
            if result['result']:
                full_article_stored= self.__store_complete_article(result['content'],link)
                if full_article_stored==True:
                    new_meta = dict(meta or {})
                    new_meta["downloadcomplete"] = "true"
                    ids_to_update.append(doc_id)
                    metas_to_update.append(new_meta)

        if ids_to_update:
            vector_collection.update(
                ids=ids_to_update,
                metadatas=metas_to_update
            )


    def __store_complete_article(self,article_text:str,link:str)->bool:
        """"
        saves the complete article in
        a vector db
        """
        client = chromadb.PersistentClient(path=os.getenv("full_article_db_path"))
        embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=os.getenv("embedding_model")
        )

        vector_collection = client.get_or_create_collection(
            name=os.getenv("articles_collection_name"),
            embedding_function=embedder,
            metadata={"hnsw:space": "cosine"}
        )
        try:
            id=hashlib.sha256(link.encode("utf-8")).hexdigest()
            metadata = {
                "link": link

            }
            ids=[id]
            docs=[article_text]
            metas=[metadata]

            vector_collection.add(ids=ids, documents=docs, metadatas=metas)
            return True

        except Exception as e:
            print(f"Error in adding rss feed to db :-{e}")
            return False




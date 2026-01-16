import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from typing import List,Dict
from chromadb.api.models import Collection
from sympy import false
import hashlib

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
            text = f"{feed['title']}\n\n{feed['summary']}"
            id=self.__create_rss_id(feed)
            metadata = {
                "link": feed["link"],
                "downloadcomplete": false
            }

        except Exception as e:
            print(f"Error in adding rss feed to db :-{e}")

    def __create_rss_id(self,feed:Dict)->str:
        """"
        Generates a unique id for the rss feed
        """
        unique_str = f"{feed['link']}|{feed.get('published', '')}"
        return hashlib.sha256(unique_str.encode("utf-8")).hexdigest()
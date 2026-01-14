import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from typing import List,Dict

class ChromaOperator:
    """"
    Performs various chroma db related operations
    """
    def __init_(self):
        load_dotenv()

    def save_rss_details(self,):
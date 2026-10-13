import pandas as pd
import chromadb
import uuid

class Portfolio:
    def __init__(self, file_path="app/resource/my_portfolio.csv"):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        # Persistent storage creates a 'vectorstore' directory in your workspace
        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self):
        # Populate the database only if it is currently empty
        if not self.collection.count():
            for _, row in self.data.iterrows():
                self.collection.add(
                    documents=row["Techstack"],
                    metadatas={"links": row["Links"]},
                    ids=[str(uuid.uuid4())]
                )

    def query_links(self, skills):
        # Query ChromaDB using semantic similarity search
        results = self.collection.query(query_texts=skills, n_results=2)
        
        # Flatten metadata list to extract portfolio links
        links = []
        for metadata in results.get('metadatas', []):
            for item in metadata:
                if 'links' in item:
                    links.append(item['links'])
        return list(set(links))
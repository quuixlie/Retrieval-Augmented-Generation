from pymilvus import MilvusClient, DataType, CollectionSchema, Collection, connections
from pymilvus.model.reranker import BGERerankFunction


class VectorDB:
    def __init__(self):
        self.client = MilvusClient(
            uri="http://localhost:19530",
            token="root:Milvus"
        )

    def create_collection(self, conversation_d: int, dimension: int) -> None:
        """
        Create a collection in the vector database.
        """
        collection_name = self.__get_collection_name_by_id(conversation_d)
        self.client.create_collection(collection_name, dimension, schema = self.__create_schema(dimension))
        self.client.create_index(collection_name, index_params = self.__create_index())

    def __get_collection_name_by_id(self, conversation_id: int) -> str:
        """
        Get the collection name by conversation ID.
        :param conversation_id: ID of the conversation
        :return: collection name
        """
        return f"conversation_{conversation_id}"

    def __create_schema(self, dimension: int) -> CollectionSchema:
        """
        Create a schema for the vector database collection.
        :return: schema
        """
        schema = MilvusClient.create_schema()

        # Add fields to the schema
        schema.add_field("id", datatype = DataType.INT64, is_primary = True, auto_id = True)
        schema.add_field("embedding", datatype = DataType.FLOAT_VECTOR, dim = dimension)
        schema.add_field("text", datatype = DataType.VARCHAR, max_length = 65535)

        return schema


    def __create_index(self):
        """
        Create an index for embedding field in the collection.
        """

        # Create an index for the embedding field
        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name = "embedding",
            index_type = "FLAT", # or "HNSW"
            metric_type = "COSINE",
        )

        return index_params


    def remove_collection(self, conversation_id: int) -> None:
        """
        Remove a collection from the vector database.
        """
        collection_name = self.__get_collection_name_by_id(conversation_id)
        self.client.drop_collection(collection_name)


    def insert_data(self, conversation_id: int, data: list):
        """
        Insert data into the vector database.
        """
        collection_name = self.__get_collection_name_by_id(conversation_id)
        self.client.insert(collection_name, data = data)


    def search(self, conversation_id: int, query_embedding: list):
        """
        Search for similar vectors in the vector database.
        """
        collection_name = self.__get_collection_name_by_id(conversation_id)
        self.client.load_collection(collection_name)
        search_params = {
            "metric_type": "COSINE",
        }

        try:
            results = self.client.search(collection_name, anns_field = "embedding", data = query_embedding, search_params = search_params,
                                        limit = 11, output_fields = ["text"])
        finally:
            self.client.release_collection(collection_name)

        return results


    def rerank(self, results: list, query: str, top_k: int = 4) -> list:
        """
        Rerank the results based on the query embedding.
        """
        # Rerank the results based on the query embedding
        reranker = BGERerankFunction(model_name = "BAAI/bge-reranker-v2-m3", device="cpu")
        initial_docs = [result['entity']['text'] for result in results[0]]
        reranked_results = reranker(query, initial_docs)

        output = []
        for i in range(top_k):
            output.append(reranked_results[i].text)

        return output
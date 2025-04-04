from pymilvus import MilvusClient, DataType, CollectionSchema, Collection, connections


class VectorDB:
    def __init__(self):
        self.client = MilvusClient("instance/vector_database.db")


    def create_collection(self, collection_name: str, dimension: int) -> None:
        """
        Create a collection in the vector database.
        """
        self.client.create_collection(collection_name, dimension, schema = self.__create_schema(dimension),
                                      index = self.__create_index())


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


    def remove_collection(self, collection_name: str):
        """
        Remove a collection from the vector database.
        """
        self.client.drop_collection(collection_name)


    def insert_data(self, collection_name: str, data: list):
        """
        Insert data into the vector database.
        """
        self.client.insert(collection_name, data = data)


    def search(self, collection_name: str, query_embedding: list):
        """
        Search for similar vectors in the vector database.
        """
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }

        results = self.client.search(collection_name, anns_field = "embedding", data = query_embedding, search_params = search_params,
                                     limit = 1)

        return results
from fastapi import Path

from app.database.database_connection import my_db
import json
from bson import json_util


async def get_all(collection):
    """
    Fetches all documents from a specified collection.
    Args:
        collection (Collections): The collection to fetch documents from.
            Should be a value from the Collections enum.
    Returns:
        list: A list of documents retrieved from the specified collection.
    Raises:
        RuntimeError: If there is an error fetching data from the collection.
    """
    collection_name = collection.name
    try:
        return list(my_db[collection_name].find({}))
    except Exception as e:
        raise RuntimeError(f"Error fetching data from collection {collection_name}: {e}")


async def get_by_id(collection, document_id):
    """
    Fetches a document from a specified collection by its ID.
    Args:
        collection (Collections): The collection to fetch the document from.
            Should be a value from the Collections enum.
        document_id (str): The ID of the document to fetch.
    Returns:
        dict: The document retrieved from the specified collection.
    Raises:
        RuntimeError: If there is an error fetching data from the collection.
    """
    collection_name = collection.name
    try:
        return my_db[collection_name].find_one({"id": document_id})
    except Exception as e:
        raise RuntimeError(f"Error fetching data from collection {collection_name}: {e}")


async def add(collection, document):
    """
    Adds a new document to a specified collection.
    Args:
        collection (Collections): The collection to add the document to.
            Should be a value from the Collections enum.
        document (dict): The document to add to the collection.
    Returns:
        dict: The inserted document ID.
    Raises:
        RuntimeError: If there is an error adding the document to the collection.
    """
    print(f"insert:  {document}")
    collection_name = collection.name
    try:
        result = my_db[collection_name].insert_one(document)
        return {"id": str(result.inserted_id)}
    except Exception as e:
        raise RuntimeError(f"Error adding document to collection {collection_name}: {e}")


async def update(collection, document_id, updated_data):
    """
    Updates an existing document in a specified collection.
    Args:
        collection (Collections): The collection containing the document to update.
            Should be a value from the Collections enum.
        document_id (str): The ID of the document to update.
        updated_data (dict): The updated data for the document.
    Returns:
        dict: The updated document.
    Raises:
        RuntimeError: If there is an error updating the document in the collection.
    """
    collection_name = collection.name
    try:
        result = my_db[collection_name].update_one({"id": document_id}, {"$set": updated_data})
        return updated_data
    except Exception as e:
        raise RuntimeError(f"Error updating document in collection {collection_name}: {e}")


async def delete(collection, document_id):
    """
    Deletes a document from a specified collection by its ID.
    Args:
        collection (Collections): The collection to delete the document from.
            Should be a value from the Collections enum.
        document_id (str): The ID of the document to delete.
    Returns:
        dict: The deleted document.
    Raises:
        RuntimeError: If there is an error deleting the document from the collection.
        ValueError: If the document with the specified ID is not found in the collection.
    """
    collection_name = collection.name
    try:
        deleted_document = my_db[collection_name].find_one_and_delete({"id": document_id})
        if not deleted_document:
            raise ValueError(f"No document with ID {document_id} found in collection {collection_name}")
        return deleted_document
    except Exception as e:
        raise RuntimeError(f"Error deleting document from collection {collection_name}: {e}")

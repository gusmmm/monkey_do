"""
MongoDB Configuration Module

This module provides configuration and utilities for connecting
to and interacting with MongoDB databases in the Monkey Do project.
"""
import logging
from typing import List, Dict, Any, Optional, Union
import time

# Import MongoDB driver
import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import (
    ConnectionFailure, 
    ServerSelectionTimeoutError, 
    OperationFailure,
    ConfigurationError
)

# Configure logger
logger = logging.getLogger(__name__)

class MongoDBConfig:
    """MongoDB connection configuration and utility methods."""
    
    def __init__(self, 
                 host: str = "localhost", 
                 port: int = 27017, 
                 db_name: str = "uq",
                 connect_timeout: int = 5000,
                 username: Optional[str] = None,
                 password: Optional[str] = None):
        """
        Initialize MongoDB configuration.
        
        Args:
            host: MongoDB server hostname or IP
            port: MongoDB server port
            db_name: Database name to connect to
            connect_timeout: Connection timeout in milliseconds
            username: Optional username for authentication
            password: Optional password for authentication
        """
        self.host = host
        self.port = port
        self.db_name = db_name
        self.connect_timeout = connect_timeout
        self.username = username
        self.password = password
        
        # Connection objects (initialized to None)
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None
        
    @property
    def client(self) -> MongoClient:
        """
        Get the MongoDB client, connecting if not already connected.
        
        Returns:
            MongoClient: MongoDB client instance
            
        Raises:
            ConnectionError: If connection fails
        """
        if self._client is None:
            self.connect()
            
        return self._client
    
    @property
    def db(self) -> Database:
        """
        Get the database instance, connecting if not already connected.
        
        Returns:
            Database: MongoDB database instance
            
        Raises:
            ConnectionError: If connection fails
        """
        if self._db is None:
            self.connect()
            
        return self._db
    
    def connect(self) -> bool:
        """
        Connect to MongoDB server and specified database.
        
        Returns:
            bool: True if connection successful, False otherwise
            
        Raises:
            ConnectionError: If connection fails after retries
        """
        try:
            # Construct MongoDB connection URI
            if self.username and self.password:
                uri = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.db_name}"
            else:
                uri = f"mongodb://{self.host}:{self.port}/{self.db_name}"
                
            # Connect with timeout settings
            self._client = MongoClient(
                uri,
                serverSelectionTimeoutMS=self.connect_timeout
            )
            
            # Test connection by issuing a command
            self._client.admin.command('ping')
            
            # Get database reference
            self._db = self._client[self.db_name]
            
            logger.info(f"Successfully connected to MongoDB database: {self.db_name}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB connection error: {str(e)}")
            raise ConnectionError(f"Failed to connect to MongoDB at {self.host}:{self.port}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected MongoDB error: {str(e)}")
            raise
    
    def close(self) -> None:
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed")
    
    def list_collections(self) -> List[str]:
        """
        List all collections in the database.
        
        Returns:
            List[str]: List of collection names
        """
        try:
            return self.db.list_collection_names()
        except Exception as e:
            logger.error(f"Failed to list collections: {str(e)}")
            raise
    
    def get_collection(self, collection_name: str) -> Collection:
        """
        Get a specific collection by name.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection: MongoDB collection object
        """
        return self.db[collection_name]
    
    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists in the database.
        
        Args:
            collection_name: Collection name to check
            
        Returns:
            bool: True if collection exists, False otherwise
        """
        return collection_name in self.list_collections()
    
    def collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics about a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dict: Collection statistics
        """
        if not self.collection_exists(collection_name):
            raise ValueError(f"Collection '{collection_name}' does not exist")
            
        return self.db.command("collStats", collection_name)


# Utility functions for common operations

def connect_to_mongodb() -> MongoDBConfig:
    """
    Create and test a connection to the MongoDB database.
    
    Returns:
        MongoDBConfig: Configured and connected instance
        
    Raises:
        ConnectionError: If connection fails
    """
    print("Connecting to MongoDB database 'uq'...")
    
    # Create MongoDB configuration
    mongo_config = MongoDBConfig(db_name="uq")
    
    try:
        # Test connection
        if (mongo_config.connect()):
            print("✅ Successfully connected to MongoDB")
            return mongo_config
            
    except ConnectionError as e:
        print(f"❌ Connection error: {str(e)}")
        raise
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        raise
        
    return mongo_config


def print_collections(mongo_config: MongoDBConfig) -> None:
    """
    Print all collections in the database.
    
    Args:
        mongo_config: MongoDB configuration instance
    """
    try:
        collections = mongo_config.list_collections()
        
        if not collections:
            print("📂 No collections found in the database")
            return
            
        print(f"\n📂 Collections in database '{mongo_config.db_name}':")
        for idx, collection in enumerate(collections, 1):
            print(f"  {idx}. {collection}")
            
    except Exception as e:
        print(f"❌ Error listing collections: {str(e)}")


def test_mongodb_connection() -> None:
    """
    Test the MongoDB connection and print collections.
    This function is useful for command-line testing.
    """
    try:
        # Connect to MongoDB
        mongo = connect_to_mongodb()
        
        # Print collections
        print_collections(mongo)
        
        # Close connection
        mongo.close()
        print("\n🔌 MongoDB connection closed")
        
    except Exception as e:
        print(f"\n❌ Failed to connect to MongoDB: {str(e)}")


if __name__ == "__main__":
    # When run directly, test the connection
    test_mongodb_connection()
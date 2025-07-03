from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Dict, Any, Optional
import logging
from lyikpluginmanager import GenericFormRecordModel

logger = logging.getLogger(__name__)


class TTKStorage:
    """
    MongoDB manager: maintains one Motor client
    for the entire process, re-using its pool for every database request.
    """

    _instance: Optional["TTKStorage"] = None

    def __new__(cls, db_conn_url: str, db_name: str | None = None):
        # Create the singleton on first use; afterwards always return it
        if cls._instance is None:
            logger.info("Creating MongoManager singleton for URL '%s'.", db_conn_url)
            cls._instance = super().__new__(cls)
            cls._instance._conn_url = db_conn_url  # save for later warnings
        else:
            # Optional: warn if somebody tries to pass a different URL later on
            if db_conn_url != cls._instance._conn_url:
                logger.warning(
                    "TTKStorage already initialised with '%s'; "
                    "ignoring new URL '%s'.",
                    cls._instance._conn_url,
                    db_conn_url,
                )
        return cls._instance

    def __init__(self, db_conn_url: str, db_name: str | None = None):
        # Initialise only once
        if getattr(self, "_initialised", False):
            # Allow updating the default DB when the singleton is reused
            if db_name:
                self._default_db = db_name
            return

        logger.info("Initialising MongoDB client for URL '%s'.", db_conn_url)
        self._client: AsyncIOMotorClient = AsyncIOMotorClient(db_conn_url)
        self._default_db: Optional[str] = db_name
        self._initialised = True

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def get_db(self, db_name: str | None = None) -> AsyncIOMotorDatabase:
        """
        Return a Motor database handle.
        • If db_name is given, that database is returned.
        • Else, the default passed in the constructor is returned.
        """
        name = db_name or self._default_db
        if not name:
            raise ValueError("Database name not specified and no default set.")
        return self._client[name]

    async def save_primary_info(
        self,
        org_id: str,
        order_id: str,
        data: Dict[str, Any],
        collection_name: str,
    ):
        db = self.get_db(org_id)
        try:
            document = {"_id": order_id, "data": data}
            result = await db[collection_name].replace_one(
                {"_id": order_id},
                document,
                upsert=True,
            )
            logger.info(
                "%s document in '%s.%s'.",
                "Upserted" if result.upserted_id else "Updated",
                order_id,
                db.name,
                collection_name,
            )
            return str(result.upserted_id)
        except Exception as e:
            logger.error("Error upserting into '%s': %s", collection_name, e)
            raise Exception(
                f"Failed to insert document in the {collection_name}. Error: {e}"
            )

    async def query_primary_info(
        self,
        org_id: str,
        order_id: str,
        collection_name: str,
    ) -> Optional[GenericFormRecordModel]:
        """
        Fetches the document with _id = order_id from the given org_id's DB.
        Returns the 'data' field if the document is found, else None.
        """
        db = self.get_db(org_id)
        try:
            document = await db[collection_name].find_one({"_id": order_id})
            if document:
                logger.info(
                    "Fetched primary info for _id '%s' from '%s.%s'.",
                    order_id,
                    db.name,
                    collection_name,
                )
                data = document.get("data")
                return GenericFormRecordModel(**data)
            else:
                logger.warning(
                    "No document found for _id '%s' in '%s.%s'.",
                    order_id,
                    db.name,
                    collection_name,
                )
                return None
        except Exception as e:
            logger.error("Error querying from '%s': %s", collection_name, e)
            raise Exception(
                f"Failed to query document from {collection_name}: {e}"
            ) from e

    @property
    def client(self) -> AsyncIOMotorClient:
        """Expose the raw Motor client if advanced operations are needed."""
        return self._client

import asyncio
from typing import Any

from pymongo import AsyncMongoClient

from src.enums import MongoColl
from src.exceptions import StorageException
from src.settings import Settings


class Storage:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = AsyncMongoClient(
            f"mongodb://"
            f"{settings.mongo_user}:"
            f"{settings.mongo_password}@"
            f"{settings.mongo_host}:"
            f"{settings.mongo_port}/",
            serverSelectionTimeoutMS=5000,
        )

        if self._client.test_database is None:
            raise StorageException("MongoDB connection failed")

        self._db = self._client.db
        self._blocks_coll = self._db.blocks
        self._transactions_coll = self._db.transactions
        self._coll_map = {
            MongoColl.blocks: self._blocks_coll,
            MongoColl.transactions: self._transactions_coll,
        }

    async def acreate_indexes(self) -> None:
        """
        Create MongoDB indexes to optimize query performance.
        """
        await self._transactions_coll.create_index("blockNumber")
        await self._transactions_coll.create_index("to")

    async def ainsert(self, data: list[dict]) -> int:
        """
        Insert block and transaction data into MongoDB.

        For each block, extracts transactions and inserts them separately.
        Performs insertions concurrently using asyncio.

        Args:
            data: List of block data dictionaries with optional transactions

        Returns:
            Total number of documents inserted
        """
        block_tasks = []
        transaction_tasks = []
        total_inserted = 0
        for item in data:
            block = item["result"]
            transactions = block.pop("transactions", [])
            block_tasks.append(self._blocks_coll.insert_one(block))
            total_inserted += 1
            if transactions:
                transaction_tasks.append(
                    self._transactions_coll.insert_many(transactions)
                )
                total_inserted += len(transactions)

        await asyncio.gather(*block_tasks, *transaction_tasks)
        return total_inserted

    async def asearch(
        self, coll_name: MongoColl, filters: dict[str, Any]
    ) -> list[dict]:
        """
        Search for documents in a specified collection using filters.

        Args:
            coll_name: The collection to search in (blocks or transactions)
            filters: MongoDB query filters to apply

        Returns:
            list[dict]: List of matching documents

        Raises:
            StorageException: If an invalid collection name is provided
        """
        coll = self._coll_map.get(coll_name)
        if coll is None:
            raise StorageException("Unexpected coll name")
        return await coll.find(filters).to_list()

    async def arefresh_db(self) -> None:
        """
        Refresh the MongoDB by deleting all items in the blocks and transactions collections.
        """
        await asyncio.gather(
            self._blocks_coll.delete_many({}), self._transactions_coll.delete_many({})
        )

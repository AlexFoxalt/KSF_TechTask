import asyncio
import json
from pathlib import Path

import typer

from src.enums import MongoColl
from src.logger import get_logger
from src.retrieval import RetrievalAgent
from src.settings import settings
from src.storage import Storage

logger = get_logger()
app = typer.Typer(help="CLI app to interact with blockchain data")


@app.command()
def fill_db() -> None:
    """
    Retrieve blockchain data from third-party API and store it in MongoDB.

    This command creates necessary MongoDB indexes, fetches block data using
    the RetrievalAgent, and stores both blocks and their transactions in
    the database.

    Example:
        $ python main.py fill-db
    """
    logger.info("Retrieving and storing data...")

    async def _fill_db() -> None:
        storage = Storage(settings)
        retrieval = RetrievalAgent(settings)
        await storage.acreate_indexes()
        logger.info("MongoDB indexes created.")

        data = await retrieval.aget_blocks()
        logger.info(f"Retrieved {len(data)} valid block(s).")

        total_inserted = await storage.ainsert(data)
        logger.info(f"Successfully inserted {total_inserted} objects.")

    asyncio.run(_fill_db())


@app.command()
def refresh_db() -> None:
    """
    Delete data from MongoDB collections

    Example:
        $ python main.py refresh-db
    """

    async def _refresh_db() -> None:
        storage = Storage(settings)
        await storage.arefresh_db()
        logger.info("MongoDB collections refreshed.")

    asyncio.run(_refresh_db())


@app.command()
def search(
    field: str = typer.Argument(..., help="Field name to search by"),
    value: str = typer.Argument(..., help="Value to search for"),
    collection: MongoColl = typer.Option(
        MongoColl.transactions.value, help="MongoDB collection to search in"
    ),
    output: Path = typer.Option(
        "output.json", help="Output file path for search results"
    ),
) -> None:
    """
    Search for documents in MongoDB by field and value.

    Example:
        $ python main.py search to 0x123abc --collection transactions --output results.json
    """
    logger.info(f"Searching for {field}={value} in {collection}...")

    async def _search() -> list[dict]:
        storage = Storage(settings)
        resp = await storage.asearch(
            coll_name=MongoColl(collection),
            filters={field: value},
        )
        return resp

    results = asyncio.run(_search())

    with open(output, "w") as f:
        json.dump(results, f, indent=2, default=str)

    logger.info(f'{len(results)} results saved to "{output}"')


if __name__ == "__main__":
    app()

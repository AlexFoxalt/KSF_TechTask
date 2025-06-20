import asyncio

import aiohttp
from aiohttp import ClientSession

from src.exceptions import RetrievalException
from src.logger import get_logger
from src.settings import Settings

logger = get_logger()


class RetrievalAgent:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._semaphore = asyncio.Semaphore(settings.concurrency_limit)

    async def aget_blocks(self) -> list[dict]:
        """
        Fetch a range of Ethereum blocks from the blockchain.

        Retrieves the latest block number first, then calculates a range of blocks to fetch
        based on configuration settings. Filters out any invalid blocks from the results.

        Returns:
            A list of valid block data dictionaries
        """
        async with aiohttp.ClientSession() as session:
            logger.info("Fetching latest block number...")
            latest_block = await self._get_latest_block_number(session)
            logger.info(f"Latest block: {latest_block}")

            start_block = (
                latest_block
                - self._settings.skip_latest_n_blocks
                - self._settings.block_fetch_count
            )
            end_block = latest_block - self._settings.skip_latest_n_blocks - 1
            logger.info(f"Fetching blocks from {start_block} to {end_block}...")

            blocks = await self._fetch_blocks(session, start_block, end_block)

            valid_blocks = [b for b in blocks if b and b.get("result")]
            logger.info(f"\nFetched {len(valid_blocks)} valid blocks.")

        if valid_blocks:
            return valid_blocks
        else:
            return []

    async def _fetch_blocks(
        self, session: ClientSession, start: int, end: int
    ) -> list[dict]:
        """
        Fetch multiple blocks concurrently within the given range.

        Args:
            session: Active client session for making HTTP requests
            start: Starting block number (inclusive)
            end: Ending block number (inclusive)

        Returns:
            List of block data responses
        """
        tasks = [
            self._fetch_block(session, block_num) for block_num in range(start, end + 1)
        ]
        return await asyncio.gather(*tasks)

    async def _get_latest_block_number(self, session: ClientSession) -> int:
        """
        Get the current highest block number from the Ethereum network.

        Args:
            session: Active client session for making HTTP requests

        Returns:
            The latest block number

        Raises:
            RetrievalException: If unable to retrieve the latest block number
        """
        response = await self._make_rpc_call(
            session=session, method="eth_blockNumber", params=[]
        )
        block_hex = response.get("result")
        if block_hex:
            return int(block_hex, 16)
        raise RetrievalException("Could not retrieve latest block number")

    async def _make_rpc_call(
        self, session: ClientSession, method: str, params: list
    ) -> dict:
        """
        Make a JSON-RPC call to the Ethereum node.

        Args:
            session: Active client session for making HTTP requests
            method: The JSON-RPC method name to call

        Returns:
            The JSON response from the Ethereum node

        Raises:
            RetrievalException: If the RPC call fails with a non-200 status
        """
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        headers = {"Content-Type": "application/json"}

        async with session.post(
            self._settings.eth_node_url, json=payload, headers=headers
        ) as resp:
            if resp.status != 200:
                raise RetrievalException(f"RPC call failed: {resp.status}")
            return await resp.json()

    async def _fetch_block(
        self, session: ClientSession, block_number: int
    ) -> dict | None:
        """
        Fetch a single block by its number.

        Uses a semaphore to limit concurrent requests. Converts the block number to hex
        format before making the RPC call.

        Args:
            session: Active client session for making HTTP requests
            block_number: The block number to fetch

        Returns:
            Block data if successful, None if an error occurs
        """
        async with self._semaphore:
            block_hex = hex(block_number)
            try:
                response = await self._make_rpc_call(
                    session=session,
                    method="eth_getBlockByNumber",
                    params=[block_hex, True],
                )
                logger.info(f"Fetched block {block_number}")
                return response
            except RetrievalException as e:
                logger.error(f"Error fetching block {block_number}: {e}")
                return None

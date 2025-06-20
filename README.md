# Ethereum Block Retrieval and Storage

A Python application for retrieving Ethereum blockchain data, storing it in MongoDB, and providing search capabilities.

## Project Description

This project fetches Ethereum blocks and their transactions from a blockchain node, stores them in MongoDB, and allows users to search through the data. It uses asynchronous programming for efficient network requests and database operations.

## Technology Stack

- **Python**: Core programming language
- **Typer**: CLI interface
- **AsyncIO**: Asynchronous programming for concurrent operations
- **aiohttp**: Asynchronous HTTP client for blockchain node interaction
- **PyMongo (AsyncMongoClient)**: MongoDB async driver
- **Docker & Docker Compose**: Containerization and service orchestration
- **Make**: Build automation

## Setup and Installation

### Env file

Replace `.env.example` with real one containing the following required envs:
```text
MONGO_HOST=<replace>
MONGO_PORT=<replace>
MONGO_USER=<replace>
MONGO_PASSWORD=<replace>

ETH_NODE_URL=<replace>
```

### Prerequisites

- Docker and Docker Compose
- Python 3.13
- Make (optional, for convenience)

### Starting the Database

Use the provided Makefile to start MongoDB:

```bash
make docker_build
```

This will start MongoDB using Docker Compose in the background.

To stop the database:

```bash
make docker_stop
```

## Usage

### Available Commands

The application provides the following CLI commands:

#### Fill the Database

Retrieve blockchain data from an Ethereum node and store it in MongoDB:

```bash
python main.py fill-db
```

This command:
1. Creates necessary MongoDB indexes
2. Fetches blocks from the Ethereum network
3. Extracts transactions from blocks
4. Stores both blocks and transactions in separate collections

#### Refresh the Database

Delete all data from MongoDB collections:

```bash
python main.py refresh-db
```

You will be prompted to confirm deletion.

#### Search Data

Search for documents in MongoDB by field and value:

```bash
python main.py search [FIELD] [VALUE] --collection [COLLECTION] --output [OUTPUT_FILE]
```

Arguments:
- `FIELD`: Field name to search by
- `VALUE`: Value to search for

Options:
- `--collection`: MongoDB collection to search in (`transactions` or `blocks`, default: `transactions`)
- `--output`: Output file path for search results (default: `output.json`)

Example:
```bash
python main.py search to 0x123abc --collection transactions --output results.json
```

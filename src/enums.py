from enum import Enum


class MongoColl(str, Enum):
    blocks = "blocks"
    transactions = "transactions"

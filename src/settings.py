from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )

    mongo_user: str
    mongo_password: str
    mongo_host: str
    mongo_port: int

    eth_node_url: str = Field("http://192.168.172.44:8545")
    concurrency_limit: int = Field(10)
    block_fetch_count: int = Field(1000)
    skip_latest_n_blocks: int = Field(100)


settings = Settings()

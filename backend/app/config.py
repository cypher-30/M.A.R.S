"""Application settings. Every value comes from the environment or .env."""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Core ---------------------------------------------------------------
    app_name: str = "AEAS"
    cors_allowed_origins: str = "http://localhost:3000"
    # Cron jobs stay off until you have working connectors. Flip to false
    # in .env once ingestion is real.
    scheduler_paused: bool = True
    environment: Literal["local", "staging", "production"] = "local"
    database_url: str = "postgresql+psycopg://aeas:aeas@localhost:5432/aeas"

    # --- Market data --------------------------------------------------------
    mystocks_api_key: str = ""
    mystocks_base_url: str = "https://api.mystocks.co.ke"
    etf_ticker: str = "WSA"
    constituent_tickers: str = "KCB,EQTY,COOP,ABSA,SCBK,NCBA,SBIC,IMH"

    # --- Macro data sources -------------------------------------------------
    cbk_rates_url: str = "https://www.centralbank.go.ke"
    knbs_cpi_url: str = "https://www.knbs.or.ke"
    # knbs.or.ke serves an incomplete certificate chain (verified 2026-08-16:
    # httpx/curl report "unable to get local issuer certificate" — a missing
    # intermediate on their end). Defaults to secure; set false only if you've
    # confirmed the failure is this same chain issue and accept the risk for
    # this read-only public-data fetch.
    knbs_verify_tls: bool = True

    # --- Document parser ----------------------------------------------------
    llm_provider: Literal["openai", "gemini"] = "openai"
    openai_api_key: str = ""
    gemini_api_key: str = ""
    llm_model: str = "gpt-4o-mini"

    # --- Alerting -----------------------------------------------------------
    alert_email_to: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # --- Trading economics --------------------------------------------------
    brokerage_exit_fee_pct: float = 2.1   # worst-case all-in exit cost, %
    exit_fee_safety_buffer_pct: float = 0.5

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]

    @property
    def constituents(self) -> list[str]:
        return [t.strip().upper() for t in self.constituent_tickers.split(",") if t.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

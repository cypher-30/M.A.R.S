"""ORM models. One table per durable artifact the system produces."""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MacroIndicator(Base):
    """A single observation of a macroeconomic series (CBR, CPI, bond yield)."""

    __tablename__ = "macro_indicators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), index=True)      # CBR | CPI | T91 | T364 | BOND_10Y
    observed_on: Mapped[date] = mapped_column(Date, index=True)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(16), default="percent")
    source: Mapped[str] = mapped_column(String(64))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("uq_macro_code_date", "code", "observed_on", unique=True),)


class PriceBar(Base):
    """Daily close for the ETF and each constituent bank."""

    __tablename__ = "price_bars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    traded_on: Mapped[date] = mapped_column(Date, index=True)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="mystocks")

    __table_args__ = (Index("uq_price_ticker_date", "ticker", "traded_on", unique=True),)


class BankReport(Base):
    """A quarterly report PDF that has been ingested and parsed."""

    __tablename__ = "bank_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    period: Mapped[str] = mapped_column(String(16))                # e.g. 2026Q1
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    npl_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    profit_after_tax: Mapped[float | None] = mapped_column(Float, nullable=True)
    loan_book: Mapped[float | None] = mapped_column(Float, nullable=True)
    extraction_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    needs_review: Mapped[bool] = mapped_column(default=True)
    raw_extraction: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("uq_report_ticker_period", "ticker", "period", unique=True),)


class SectorScore(Base):
    """The daily 1-100 Sector Health Score plus its component breakdown."""

    __tablename__ = "sector_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scored_on: Mapped[date] = mapped_column(Date, unique=True, index=True)
    score: Mapped[float] = mapped_column(Float)
    signal: Mapped[str] = mapped_column(String(8))                 # BUY | HOLD | SELL
    components: Mapped[str] = mapped_column(Text)                  # JSON blob of sub-scores
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    alerts: Mapped[list["Alert"]] = relationship(back_populates="sector_score")


class Alert(Base):
    """An alert that was (or would have been) sent to the operator."""

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sector_score_id: Mapped[int | None] = mapped_column(ForeignKey("sector_scores.id"), nullable=True)
    level: Mapped[str] = mapped_column(String(16))                 # INFO | WARNING | CRITICAL
    signal: Mapped[str] = mapped_column(String(8))
    headline: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    delivered: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    sector_score: Mapped["SectorScore | None"] = relationship(back_populates="alerts")

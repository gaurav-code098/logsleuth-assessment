from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy import Text, DateTime, String
from sqlalchemy.sql import func

Base = declarative_base()

class LogAnalysis(Base):
    __tablename__ = "log_analyses"


    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    raw_log: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending") 
    severity: Mapped[str | None] = mapped_column(String, nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_fix: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, JSON, DateTime, func, UniqueConstraint

class Base(DeclarativeBase):
    pass

class SurveyRow(Base):
    __tablename__ = "surveys"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prompt: Mapped[str] = mapped_column(String(512), nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint("prompt", name="uq_surveys_prompt"),)
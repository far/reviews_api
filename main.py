from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, Text, text
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Query
from pydantic import BaseModel
from typing import List
from datetime import datetime
from enum import Enum

words_positive = ["хорош", "люблю"]
words_negative = ["плох", "ненавиж"]

DATABASE_URL = "sqlite+aiosqlite:///./reviews.db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()


class Sentiment(str, Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"


def get_sentiment(text: str) -> str:
    if any(word in text.lower() for word in words_positive):
        return Sentiment.positive
    if any(word in text.lower() for word in words_negative):
        return Sentiment.negative
    return Sentiment.neutral


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    sentiment = Column(Text)
    created_at = Column(Text)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


class ReviewRequest(BaseModel):
    text: str


class ReviewResponse(BaseModel):
    id: int
    text: str
    sentiment: Sentiment
    created_at: str


app = FastAPI(lifespan=lifespan)


@app.post("/reviews/", response_model=ReviewResponse)
async def create_review(
    review: ReviewRequest, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        text(
            "INSERT INTO reviews(text, sentiment, created_at) "
            "VALUES(:text, :sentiment, :created_at) RETURNING *"
        ),
        {
            "text": review.text,
            "sentiment": get_sentiment(review.text),
            "created_at": datetime.utcnow().isoformat(),
        },
    )
    await db.commit()
    row = result.fetchone()
    return ReviewResponse(
        id=row[0], text=row[1], sentiment=Sentiment(row[2]), created_at=row[3]
    )


@app.get("/reviews/", response_model=List[ReviewResponse])
async def read_reviews(
    sentiment: Sentiment = Query(...), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        text(
            "SELECT id, text, sentiment, created_at "
            "FROM reviews WHERE sentiment = :sentiment"
        ),
        {"sentiment": sentiment},
    )
    return [
        ReviewResponse(
            id=row[0],
            text=row[1],
            sentiment=Sentiment(row[2]),
            created_at=row[3],
        )
        for row in result.fetchall()
    ]

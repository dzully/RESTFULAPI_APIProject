from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from supabase import Client, create_client

DATABASE_URL = "postgresql+asyncpg://sa:tMhskzvCkmPQ6BA6uYwP6mIMqZ5Yf0mT@dpg-cptgcb6ehbks73fe9430-a.singapore-postgres.render.com/ms_sql"

engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()
security = HTTPBearer()


app = FastAPI()

url: str = "https://bteeehesqyliqdystvnl.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ0ZWVlaGVzcXlsaXFkeXN0dm5sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTkzNDAzMjAsImV4cCI6MjAzNDkxNjMyMH0.M-ykpgJ7O1PM_J3ApEhQvKgl7Pbbe3NzIOFSwH_fSkw"
supabase: Client = create_client(url, key)

origins = [
    "http://localhost:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Blog(Base):
    __tablename__ = 'blogs'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String, index=True)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Make sure all tables are created
        await conn.run_sync(Base.metadata.create_all)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user = supabase.auth.get_user(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


@app.get("/api/v1/get-all-post")
async def read_blogs(user: dict = Depends(get_current_user)):
    async with SessionLocal() as session:
        result = await session.execute(select(Blog).order_by(Blog.id))
        blogs = result.scalars().all()
        return blogs


class PostUpdate(BaseModel):
    title: str
    content: str


@app.put("/api/v1/update-post/{id}")
async def update_item(id: str, post_update: PostUpdate, user: dict = Depends(get_current_user)):
    async with SessionLocal() as session:
        db_item = await session.get(Blog, int(id))
        db_item.title = post_update.title
        db_item.content = post_update.content
        await session.commit()

        result = await session.execute(select(Blog).order_by(Blog.id))
        blogs = result.scalars().all()
        return blogs


@app.post("/api/v1/create-post")
async def create_item(post: PostUpdate, user: dict = Depends(get_current_user)):
    async with SessionLocal() as session:
        new_post = Blog(title=post.title, content=post.content)
        session.add(new_post)
        await session.commit()

        result = await session.execute(select(Blog).order_by(Blog.id))
        blogs = result.scalars().all()
        return blogs


@app.delete("/api/v1/delete-post/{id}")
async def delete_item(id: str, user: dict = Depends(get_current_user)):
    async with SessionLocal() as session:
        db_item = await session.get(Blog, int(id))
        print(db_item)
        await session.delete(db_item)
        await session.commit()

        result = await session.execute(select(Blog).order_by(Blog.id))
        blogs = result.scalars().all()
        return blogs

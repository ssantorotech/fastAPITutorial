from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import PostCreate, PostResponse, UserRead, UserUpdate, UserCreate
from app.db import Post, create_db_and_tables, get_async_session, User
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
import shutil
import os
import uuid
import tempfile

from pathlib import Path
from app.users import auth_backend, current_active_user, fastapi_users





@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix='/auth/jwt', tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix='/auth', tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix='/auth', tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])




@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    temp_file = None
    temp_path = None
    
    try:
        suffix = os.path.splitext(file.filename or "")[1]

        with tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=os.path.splitext(file.filename)[1]
            ) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        with open(temp_path, "rb") as image_file:
            response = imagekit.files.upload(
                file=image_file,
                file_name=file.filename or "upload",
                folder="/uploads",
                tags=["backend-upload"],
                use_unique_file_name=True,
            )

        post = Post(
            user_id=user.id,
            caption=caption,
            url=response.url,
            file_type=file.content_type,
            file_name=file.filename or "upload"
        )

        session.add(post)
        await session.commit()
        await session.refresh(post)
    

        return {
            "url": post.url,
            "file_name": post.file_name,
            "caption": post.caption
        }

    except Exception as e:
        await session.rollback()
        print(f"Upload error: {e}")
        raise HTTPException(
            status_code=500,
            detail="File upload failed",
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        await file.close()

    

    


@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]
    
    
    result = await session.execute(select(User))
    users = [row[0] for row in result.all()]
    user_dict = {u.id: u.email for u in users}

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                "is_owner": post.user_id == user.id,
                "email": user_dict.get(post.user_id, "Unknown")
            }
        )
    return {"posts": posts_data}


@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: str, 
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")

        await session.delete(post)
        await session.commit()

        return {"success": True, "message": "Post deleted successfully"}
    except Exception as e:
        await session.rollback()
        print(f"Delete error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Post deletion failed",
        )
    finally:
        await session.close()
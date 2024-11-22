from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from app.models import User
from app.database import get_db
from app.helpers import create_access_token

router = APIRouter()
bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/", response_class=HTMLResponse)
async def show_login_page(request: Request):
    return {"request": request}

@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user or not bcrypt.verify(password, user.password):
        return {"error": "Invalid credentials"}

    access_token = create_access_token(data={"sub": username})
    response = RedirectResponse(url="/menu", status_code=302)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

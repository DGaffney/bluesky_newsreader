import os
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi_login import LoginManager
from atproto_helper import get_user_timeline
import db
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
SECRET = os.getenv("SECRET_KEY", "foo")
app.add_middleware(SessionMiddleware, secret_key=SECRET)

# Set up template directory and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure LoginManager
manager = LoginManager(SECRET, token_url="/login", use_cookie=True)
manager.cookie_name = "auth_cookie"

# Simulated user database for demo purposes
fake_users_db = {
    "user1": {"username": "user1", "password": "password1"}
}

@manager.user_loader
def load_user(username: str):
    return fake_users_db.get(username)

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = load_user(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    response = RedirectResponse(url="/timeline", status_code=302)
    manager.set_cookie(response, username)
    request.session['username'] = username
    return response

@app.get("/timeline", response_class=HTMLResponse)
async def show_timeline(request: Request):
    username = request.session.get('username')
    if not username:
        return RedirectResponse(url="/", status_code=302)
    
    client = BlueskyAPI('devingaffney.com', 'q4ms-zudd-h2l5-2444')
    timeline = client.get_news_feed()

    return templates.TemplateResponse("timeline.html", {"request": request, "timeline": timeline})
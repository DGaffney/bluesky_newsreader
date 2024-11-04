import os
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from bluesky_api import BlueskyAPI
import db
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
SECRET = os.getenv("SECRET_KEY", "foo")
app.add_middleware(SessionMiddleware, secret_key=SECRET)

templates = Jinja2Templates(directory="templates")

# Configure LoginManager
manager = LoginManager(SECRET, token_url="/login", use_cookie=True)
manager.cookie_name = "auth_cookie"
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    response = RedirectResponse(url="/timeline", status_code=302)
    manager.set_cookie(response, username)
    request.session['username'] = username
    if is_app_passwordy(password):
        request.session['password'] = password
    else:
        raise HTTPException(status_code=401, detail="This doesn't look app-passwordy - please go generate one!")
    return response

@app.get("/timeline", response_class=HTMLResponse)
async def show_timeline(request: Request):
    client = BlueskyAPI(request.session['username'], request.session['password'])
    timeline = client.get_news_feed()
    return templates.TemplateResponse("timeline.html", {"request": request, "timeline": timeline})
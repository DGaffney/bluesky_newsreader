import os
import pickle
import time
from fastapi import FastAPI, Request, Form, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from bluesky_api import BlueskyAPI, is_app_passwordy
import db
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from datetime import datetime

app = FastAPI()
SECRET = os.getenv("SECRET_KEY", "foo")
app.add_middleware(SessionMiddleware, secret_key=SECRET)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure LoginManager
manager = LoginManager(SECRET, token_url="/login", use_cookie=True)
manager.cookie_name = "auth_cookie"
CACHE_DIR = "cache"
CACHE_EXPIRY_SECONDS = 5 * 60  # 5 minutes

def is_cache_valid(cache_file_path):
    if not os.path.exists(cache_file_path):
        return False
    file_age = time.time() - os.path.getmtime(cache_file_path)
    return file_age < CACHE_EXPIRY_SECONDS

def save_to_cache(cache_file_path, data):
    with open(cache_file_path, "wb") as f:
        pickle.dump(data, f)

def load_from_cache(cache_file_path):
    with open(cache_file_path, "rb") as f:
        return pickle.load(f)

# Define the custom filter function
def datetimeformat(value, format='%Y-%m-%d %I:%M %p'):
    # Replace 'Z' with '+00:00' for compatibility with fromisoformat
    if value.endswith('Z'):
        value = value.replace('Z', '+00:00')
    dt = datetime.fromisoformat(value)
    return dt.strftime(format)

# Register the custom filter with the Jinja2 environment
templates.env.filters['datetimeformat'] = datetimeformat

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
    if request.session.get("username"):
        client = BlueskyAPI(request.session['username'], request.session['password'])
        timeline = client.get_linked_timeline()  # This returns a dict with URLs as keys and lists of skeets as values

        # Sort the timeline
        sorted_timeline = sorted(
            timeline.items(),
            key=lambda item: (
                len({skeet.post.author.handle for skeet in item[1]}),  # Number of distinct users
                sum(skeet.post.like_count for skeet in item[1]),       # Total likes
                sum(skeet.post.repost_count for skeet in item[1])      # Total reskeets
            ),
            reverse=True  # Sort in descending order
        )
        return templates.TemplateResponse("timeline.html", {"request": request, "timeline": sorted_timeline})
    else:
        return templates.TemplateResponse("login.html", {"request": request})

@app.get("/feed/{did}/{ns}/{rkey}", response_class=HTMLResponse)
async def show_feed(request: Request, feed_path: str, cache_bust: bool = Query(False)):
    if request.session.get("username"):
        # Ensure the cache directory exists
        os.makedirs(CACHE_DIR, exist_ok=True)
        feed_path = f"{did}/{ns}/{rkey}"
        cache_file_path = os.path.join(CACHE_DIR, f"{feed_path.replace('/', '_')}_timeline.pkl")
        # Check if the cache_bust parameter is True or the cache is invalid
        if cache_bust or not is_cache_valid(cache_file_path):
            # Fetch live data and update cache
            client = BlueskyAPI(request.session['username'], request.session['password'])
            timeline = client.get_feed_aggregation(f"at://{feed_path}")
            save_to_cache(cache_file_path, timeline)
        else:
            # Load cached timeline using pickle
            timeline = load_from_cache(cache_file_path)
        # Sort the timeline based on the given criteria
        sorted_timeline = sorted(
            timeline.items(),
            key=lambda item: (
                len({skeet.post.author.handle for skeet in item[1]}),  # Number of distinct users
                sum(skeet.post.like_count for skeet in item[1]),       # Total likes
                sum(skeet.post.repost_count for skeet in item[1])      # Total reskeets
            ),
            reverse=True  # Sort in descending order
        )
        return templates.TemplateResponse("timeline.html", {"request": request, "timeline": sorted_timeline})
    else:
        return templates.TemplateResponse("login.html", {"request": request})
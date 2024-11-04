from fastapi import APIRouter, Request, Depends, HTTPException
from atproto import Client

import db

router = APIRouter()

@router.get("/login")
async def login():
    # Replace with actual URL and client credentials
    auth_url = "https://example.com/oauth/authorize?client_id=YOUR_CLIENT_ID"
    return {"auth_url": auth_url}

@router.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Code not provided")
    
    # Exchange code for an access token
    client = Client()
    token_response = client.exchange_code_for_token(code)

    # Save the user data in the database
    user_id = token_response["user_id"]
    access_token = token_response["access_token"]
    db.save_user(user_id, access_token)

    return {"message": "Login successful. You can now view your timeline."}
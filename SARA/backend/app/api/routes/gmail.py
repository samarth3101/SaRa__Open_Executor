import os

from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, Depends, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.db.models import GmailToken, User
from app.services.gmail_service import get_latest_emails

router = APIRouter(prefix="/auth/google", tags=["gmail"])

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

def build_flow():
    settings = get_settings()

    if not settings.google_client_id or not settings.google_client_secret or not settings.google_redirect_uri:
        raise HTTPException(status_code=500, detail="Missing Google OAuth env vars")

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.google_redirect_uri],
            }
        },
        scopes=SCOPES,
        autogenerate_code_verifier=True,
    )
    flow.redirect_uri = settings.google_redirect_uri
    return flow


@router.get("/login")
def google_login(request: Request):
    flow = build_flow()
    app_state = str(uuid4())

    auth_url, _google_state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
        state=app_state,
    )

    request.session["google_oauth_state"] = app_state
    request.session["google_pkce_verifier"] = flow.code_verifier
    return RedirectResponse(url=auth_url)


@router.get("/callback")
def google_callback(
    request: Request,
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    expected_state = request.session.pop("google_oauth_state", None)
    code_verifier = request.session.pop("google_pkce_verifier", None)

    if not expected_state or expected_state != state or not code_verifier:
        raise HTTPException(status_code=400, detail="Missing PKCE verifier. Start again from /auth/google/login")

    flow = build_flow()
    flow.code_verifier = code_verifier
    flow.fetch_token(code=code)

    credentials = flow.credentials
    service = build("gmail", "v1", credentials=credentials)
    profile = service.users().getProfile(userId="me").execute()
    gmail_email = profile.get("emailAddress")

    user = db.query(User).filter(User.email == gmail_email).first()
    if not user:
        user = User(
            full_name=gmail_email.split("@")[0],
            email=gmail_email,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token_row = db.query(GmailToken).filter(GmailToken.user_id == user.id).first()
    if not token_row:
        token_row = GmailToken(
            user_id=user.id,
            email=gmail_email,
            refresh_token=credentials.refresh_token or "",
            access_token=credentials.token,
            scopes=" ".join(SCOPES),
        )
        db.add(token_row)
    else:
        if credentials.refresh_token:
            token_row.refresh_token = credentials.refresh_token
        token_row.access_token = credentials.token
        token_row.email = gmail_email
        token_row.scopes = " ".join(SCOPES)

    db.commit()

    return {
        "message": "Google connected successfully",
        "connected": True,
        "email": gmail_email,
        "user_id": user.id,
    }


@router.get("/latest-emails")
def latest_emails(db: Session = Depends(get_db)):
    token_row = db.query(GmailToken).first()
    if not token_row:
        raise HTTPException(status_code=404, detail="Gmail not connected")

    emails = get_latest_emails(token_row, limit=3)

    suggested_action = "ignore_for_now"
    joined = " ".join(f"{e['subject']} {e['preview']}".lower() for e in emails)

    if any(word in joined for word in ["urgent", "asap", "reply", "approval", "action required", "meeting", "invoice"]):
        suggested_action = "reply"
    elif emails:
        suggested_action = "review"

    summary = "No recent important emails found."
    if emails:
        senders = ", ".join(email["sender"].split("<")[0].strip() for email in emails[:2])
        summary = f"You have {len(emails)} recent inbox emails. Top senders: {senders}."

    return {
        "ok": True,
        "source": "gmail",
        "summary": summary,
        "emails": emails,
        "suggestedAction": suggested_action,
        "commandText": "latest_emails",
        "estimatedTime": "5s",
    }

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from app.core.config import get_settings
from app.db.models import GmailToken

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def build_gmail_credentials(token_row: GmailToken):
    settings = get_settings()

    creds = Credentials(
        token=token_row.access_token,
        refresh_token=token_row.refresh_token,
        token_uri=token_row.token_uri,
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=SCOPES,
    )

    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())

    return creds


def extract_header(headers, name: str):
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value")
    return ""


def get_latest_emails(token_row: GmailToken, limit: int = 3):
    creds = build_gmail_credentials(token_row)
    service = build("gmail", "v1", credentials=creds)

    results = (
        service.users()
        .messages()
        .list(
            userId="me",
            maxResults=limit,
            q="in:inbox category:primary -category:promotions -category:social -category:forums",
        )
        .execute()
)


    messages = results.get("messages", [])
    output = []

    for msg in messages:
        detail = (
            service.users()
            .messages()
            .get(userId="me", id=msg["id"], format="metadata", metadataHeaders=["From", "Subject"])
            .execute()
        )

        payload = detail.get("payload", {})
        headers = payload.get("headers", [])
        snippet = detail.get("snippet", "")

        output.append(
            {
                "id": detail.get("id"),
                "subject": extract_header(headers, "Subject") or "(No subject)",
                "sender": extract_header(headers, "From") or "Unknown sender",
                "preview": snippet,
            }
        )

    return output
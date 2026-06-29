import secrets, hashlib, base64
from urllib.parse import urlencode
import requests

def _b64(b): return base64.urlsafe_b64encode(b).rstrip(b'=').decode()

class OIDCClient:
    """'Login with AgentOS' (Authorization Code + PKCE). Framework-free.
    public_issuer = browser-reachable base (authorize redirect); issuer = server-to-server base (token/userinfo).
    """
    def __init__(self, issuer, client_id, client_secret, redirect_uri,
                 scope="openid email org", public_issuer=None):
        self.issuer = (issuer or "").rstrip('/')
        self.public_issuer = (public_issuer or issuer or "").rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope

    def start(self):
        verifier = _b64(secrets.token_bytes(32))
        challenge = _b64(hashlib.sha256(verifier.encode()).digest())
        state = secrets.token_urlsafe(8)
        q = urlencode({
            "response_type": "code", "client_id": self.client_id,
            "redirect_uri": self.redirect_uri, "scope": self.scope,
            "state": state, "code_challenge": challenge, "code_challenge_method": "S256",
        })
        return f"{self.public_issuer}/o/authorize/?{q}", state, verifier   # browser-facing

    def exchange(self, code, verifier):
        r = requests.post(f"{self.issuer}/o/token/", data={                # server-to-server
            "grant_type": "authorization_code", "code": code,
            "redirect_uri": self.redirect_uri, "client_id": self.client_id,
            "client_secret": self.client_secret, "code_verifier": verifier,
        }, timeout=15)
        r.raise_for_status(); return r.json()

    def userinfo(self, access_token):
        r = requests.get(f"{self.issuer}/o/userinfo/",
                         headers={"Authorization": "Bearer " + access_token}, timeout=15)
        r.raise_for_status(); return r.json()

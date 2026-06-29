from rest_framework.authentication import SessionAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # first-party same-origin SPA; skip CSRF (re-add or use bearer tokens for prod)

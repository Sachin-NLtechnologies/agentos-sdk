"""Reusable 'Login with AgentOS' for Django agents. Wiring = ~3 lines:
   from agentos_sdk.django_auth import sso_urls
   urlpatterns += sso_urls()
   + set AGENTOS_OIDC_ISSUER / AGENTOS_OIDC_PUBLIC_ISSUER / AGENTOS_CLIENT_ID /
     AGENTOS_CLIENT_SECRET / AGENTOS_REDIRECT_URI.
"""
import os, importlib
from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import path
from .oidc import OIDCClient

def _g(k, default=None):
    return getattr(settings, k, os.getenv(k, default))

def _client():
    return OIDCClient(
        _g('AGENTOS_OIDC_ISSUER'),
        _g('AGENTOS_CLIENT_ID'),
        _g('AGENTOS_CLIENT_SECRET'),
        _g('AGENTOS_REDIRECT_URI'),
        scope=_g('AGENTOS_SCOPE', 'openid email org'),
        public_issuer=_g('AGENTOS_OIDC_PUBLIC_ISSUER'),
        insecure_tls=(_g('AGENTOS_INSECURE_TLS') == '1' or _g('AGENTOS_INSECURE_TLS') == 1)
    )

def agentos_start(request):
    url, state, verifier = _client().start()
    request.session['aos_s'] = state
    request.session['aos_v'] = verifier
    return redirect(url)

def agentos_callback(request):
    if request.GET.get('state') != request.session.get('aos_s'):
        return HttpResponseBadRequest('state mismatch')
    c = _client()
    tok = c.exchange(request.GET.get('code'), request.session.get('aos_v'))
    info = c.userinfo(tok['access_token'])
    User = get_user_model()
    user, _ = User.objects.get_or_create(username=info['email'], defaults={'email': info['email']})
    login(request, user)
    request.session['aos_org'] = info.get('org')
    request.session['aos_role'] = info.get('role')
    hook = _g('AGENTOS_ON_LOGIN')
    if hook:
        m, fn = hook.rsplit('.', 1)
        getattr(importlib.import_module(m), fn)(request, user, info)
    return redirect(_g('AGENTOS_LOGIN_REDIRECT', '/'))

def sso_urls(prefix='auth/agentos/'):
    return [
        path(prefix + 'start/', agentos_start, name='agentos_start'),
        path(prefix + 'callback/', agentos_callback, name='agentos_callback'),
    ]

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

import time
from django.urls import reverse
from django.http import HttpResponse

def agentos_start(request):
    url, state, verifier = _client().start()
    
    states = request.session.get('aos_states', [])
    now = time.time()
    states = [s for s in states if now - s['t'] < 600]
    states.append({'s': state, 'v': verifier, 't': now})
    states = states[-3:]
    
    request.session['aos_states'] = states
    
    if 'aos_s' in request.session: del request.session['aos_s']
    if 'aos_v' in request.session: del request.session['aos_v']
    
    response = redirect(url)
    response['Cache-Control'] = 'no-store'
    return response

def agentos_callback(request):
    received_state = request.GET.get('state')
    states = request.session.get('aos_states', [])
    now = time.time()
    
    matched = None
    for s in states:
        if s['s'] == received_state and (now - s['t'] < 600):
            matched = s
            break
            
    if not matched:
        if received_state and request.session.get('aos_s') == received_state:
            matched = {'s': request.session['aos_s'], 'v': request.session['aos_v']}
            if 'aos_s' in request.session: del request.session['aos_s']
            if 'aos_v' in request.session: del request.session['aos_v']
        else:
            url = reverse('agentos_start')
            html = f"""<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
            <body style="font-family: sans-serif; text-align: center; padding: 40px 20px; background: #1a1a1a;">
                <h3 style="color: #eee;">Login session expired</h3>
                <a href="{url}" style="display: inline-block; padding: 12px 24px; background: #FACC15; color: #241a03; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 10px;">Tap to try again</a>
            </body></html>"""
            return HttpResponse(html)

    if 'aos_states' in request.session:
        request.session['aos_states'] = [s for s in request.session['aos_states'] if s['s'] != received_state]

    c = _client()
    tok = c.exchange(request.GET.get('code'), matched['v'])
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

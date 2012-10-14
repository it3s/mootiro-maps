# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from annoying.decorators import render_to

from .models import User
from .utils import logout as auth_logout
from .utils import login as auth_login


@render_to('komoo_user/login.html')
def login(request):
    """
    GET: Displays a page with login options.
    POST: Receives email and password and authenticate the user.
    """
    if request.method == 'GET':
        next = request.GET.get('next', '')
        return dict(next=next)

    email = request.POST['email']
    password = request.POST['password']
    if not email or not password:
        return dict(login_error='wrong_credentials')

    password = User.calc_hash(password)
    q = User.objects.filter(email=email, _password=password)
    if not q.exists():
        return dict(login_error='wrong_credentials')

    user = q.get()
    if not user.is_active:
        return dict(login_error='user_not_active')

    auth_login(request, user)
    next = request.POST.get('next', '') or reverse('root')
    return redirect(next)


def logout(request):
    next_page = request.GET.get('next', '/')
    auth_logout(request)
    return redirect(next_page)

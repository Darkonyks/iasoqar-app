from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve, reverse
import re

class RequireLoginMiddleware:
    """
    Middleware koji zahteva autentifikaciju za sve stranice osim izuzetih.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Putanje koje ne zahtevaju autentifikaciju
        self.exempt_urls = [
            re.compile(settings.LOGIN_URL.lstrip('/')),
            re.compile(r'^accounts/login/$'),
            re.compile(r'^accounts/logout/$'),
            re.compile(r'^admin/login/$'),
            re.compile(r'^admin/.*$'),  # Admin stranice imaju svoju autentifikaciju
            re.compile(r'^static/.*$'),
            re.compile(r'^media/.*$'),
        ]

    def __call__(self, request):
        # Ako korisnik nije autentifikovan i URL nije izuzet, preusmeri na login
        if not request.user.is_authenticated:
            path = request.path_info.lstrip('/')
            
            # Proveri da li je URL izuzet
            if not any(m.match(path) for m in self.exempt_urls):
                return redirect(settings.LOGIN_URL)
                
        response = self.get_response(request)
        return response

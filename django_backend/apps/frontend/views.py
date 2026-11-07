from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect


SLUG_REDIRECTS = {
    'p0landing': '/',
    'p1home': '/',
    'p5home2': '/',
    'p23home3': '/',
    'p3login': '/accounts/login/',
    'p4signup': '/users/register/',
    'p9profile': '/users/profile/',
    'p6companies': '/companies/directory/',
    'p7companies2': '/companies/directory/',
    'p8companies3': '/companies/directory/',
    'p10tcs': '/companies/1/',
    'p11intileo': '/companies/3/',
    'p12infosys': '/companies/2/',
    'p17quizp': '/users/quizzes/',
    'p18quizp2': '/users/quizzes/',
    'p19quizp3': '/users/quizzes/',
    'p20quizp4': '/users/quizzes/',
    'p21quizp5': '/users/quizzes/',
    'p25re': '/companies/directory/',
    'p26repostjob': '/jobs/create/',
    'p28companylogin': '/companies/directory/',
}


def page(request: HttpRequest, slug: str) -> HttpResponse:
    if slug in SLUG_REDIRECTS:
        return redirect(SLUG_REDIRECTS[slug])
    return redirect('/')

"""
views.py — HTTP request handlers for AttendanceChimp.

Each view corresponds to one URL endpoint.  Views receive an HTTP request,
interact with the database via models.py, and return an HTTP response.
"""

from django.shortcuts import render, redirect
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseBadRequest, JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import datetime
import zoneinfo
import json
import io

# from .models import (InstructorProfile, StudentProfile, Course, Enrollment,
#                      Lecture, QRCodeUpload, is_instructor, is_student,
#                      getUploadsForCourse)
from .models import InstructorProfile, StudentProfile

CDT = zoneinfo.ZoneInfo("America/Chicago")


# ---------------------------------------------------------------------------
# HW2  — index, time, sum
# ---------------------------------------------------------------------------

def index(request):
    """
    Input: request (an HTTP request)

    Builds the home page with the current Chicago time and the logged-in user.

    Output: the rendered index.html page
    """
    
    context = {
        'time': datetime.now(CDT).strftime("%H:%M"),
        'user': request.user,
    }
    return render(request, 'app/index.html', context)

def time_view(request):
    chicago = zoneinfo.ZoneInfo("America/Chicago")
    now = datetime.now(chicago)
    return HttpResponse(now.strftime("%H:%M"))

def sum_view(request):
    n1 = float(request.GET["n1"])
    n2 = float(request.GET["n2"])
    return HttpResponse("<p>" + str(n1 + n2) + "</p>")

# ---------------------------------------------------------------------------
# HW4  — user creation
# ---------------------------------------------------------------------------

def new(request):
    """
    Input: request (an HTTP request)

    Shows the sign-up form. Only GET requests are allowed.

    Output: the rendered new.html page, or an error
    """
    if request.method != 'GET':
        return HttpResponse("Error: not a GET request", status=400)
    return render(request, 'app/new.html')

@csrf_exempt
def createUser(request):
    """
    Input: request (a POST with user_name, email, password, is_student)

    Creates a new user with a student or instructor profile and signs them in.
    Returns an error if the email is already used.

    Output: a success response, or an error
    """
    if request.method != 'POST':
        return HttpResponse("Error: not a POST request", status=400)
    user_name = request.POST['user_name']
    email = request.POST['email']
    password = request.POST['password']
    is_student = request.POST['is_student']
    if User.objects.filter(email=email).count() > 0:
        return HttpResponse("Error: email already exists", status=400)
    user = User.objects.create_user(username=user_name, email=email, password=password)
    if is_student == '1':
        StudentProfile(user=user).save()
    else:
        InstructorProfile(user=user).save()
    login(request, user)
    return HttpResponse("User created")


# ---------------------------------------------------------------------------
# HW5  — courses, lectures, QR uploads, dump
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# HW6  — getUploads
# ---------------------------------------------------------------------------




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
from .models import InstructorProfile, StudentProfile, Course, is_instructor, is_student, Lecture, QRCodeUpload

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

def new_course(request):
    """
    Input: request (HTTP request)

    Shows the form for creating a course.

    Output: the new_course.html page
    """
    return render(request, 'app/new_course.html')

def new_lecture(request):
    """
    Input: request (HTTP request)

    Shows the form for creating a lecture, with the courses to pick from.

    Output: the new_lecture.html page
    """
    return render(request, 'app/new_lecture.html', {'courses': Course.objects.all()})

def new_qr_upload(request):
    """
    Input: request (HTTP request)

    Shows the form for uploading a QR code image.

    Output: the new_qr_upload.html page
    """
    return render(request, 'app/new_qr_upload.html')

@csrf_exempt
def createCourse(request):
    """
    Input: request (HTTP POST with course-name, start-time, end-time, day-mon to day-fri)

    Creates a Course row for the logged-in instructor.

    Output: HTTP 200, or 401 if the user is not an instructor
    """
    if not request.user.is_authenticated or not is_instructor(request.user):
        return HttpResponse("Error: instructors only", status=401)
    if request.method != "POST":
        return HttpResponse("Error: not a POST request", status=400)
    days = ""
    for day in ["mon", "tue", "wed", "thu", "fri"]:
        if "day-" + day in request.POST:
            days = days + day + " "
    schedule = days + request.POST["start-time"] + "-" + request.POST["end-time"]
    instructor = InstructorProfile.objects.filter(user=request.user)[0]
    course = Course(name=request.POST["course-name"], instructor=instructor, schedule=schedule)
    course.save()
    return HttpResponse(status=200)

@csrf_exempt
def createLecture(request):
    """
    Input: request (HTTP POST with choice, a course name)

    Creates a Lecture row linked to the chosen course.

    Output: HTTP 200, or 401 if the user is not an instructor
    """
    if not request.user.is_authenticated or not is_instructor(request.user):
        return HttpResponse("Error: instructors only", status=401)
    if request.method != "POST":
        return HttpResponse("Error: not a POST request", status=400)
    course = Course.objects.filter(name=request.POST["choice"])[0]
    now = datetime.now(zoneinfo.ZoneInfo("America/Chicago"))
    lecture = Lecture(course=course, date=now, qr_code=str(now))
    lecture.save()
    return HttpResponse(status=200)

@csrf_exempt
def createQRCodeUpload(request):
    """
    Input: request (HTTP POST with a file field imageUpload)

    Creates a QRCodeUpload row for the logged-in student.

    Output: HTTP 200, or 401 if the user is not a student
    """
    if not request.user.is_authenticated or not is_student(request.user):
        return HttpResponse("Error: students only", status=401)
    if request.method != "POST":
        return HttpResponse("Error: not a POST request", status=400)
    student = StudentProfile.objects.filter(user=request.user)[0]
    upload = QRCodeUpload(student=student, image=request.FILES["imageUpload"])
    upload.save()
    return HttpResponse(status=200)

def dumpUploads(request):
    """
    Input: request (HTTP GET)

    Lists every QR code upload with the student's username and the upload time.

    Output: a JSON list of dictionaries, or 401 if the user is not an instructor
    """
    if not request.user.is_authenticated or not is_instructor(request.user):
        return HttpResponse("Error: instructors only", status=401)
    data = []
    for upload in QRCodeUpload.objects.all():
        data.append({"username": upload.student.user.username,
                     "upload_time": upload.uploaded_at.strftime("%Y-%m-%d %H:%M:%S")})
    return JsonResponse(data, safe=False)

# ---------------------------------------------------------------------------
# HW6  — getUploads
# ---------------------------------------------------------------------------




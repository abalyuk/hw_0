"""
models.py: Data model for AttendanceChimp.

Instructors create courses and lectures. Each lecture has a QR code.
Students upload a photo of the QR code to record attendance.
"""

from django.db import models
from django.contrib.auth.models import User


class InstructorProfile(models.Model):
    """
    Input: user (a Django User)

    Creates the InstructorProfile table. Each instructor is linked to exactly one User.

    Output: an InstructorProfile row
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class StudentProfile(models.Model):
    """
    Input: user (a Django User)

    Creates the StudentProfile table. Each student is linked to exactly one User.

    Output: a StudentProfile row
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Course(models.Model):
    """
    Input: name (string), instructor (InstructorProfile), schedule (string, e.g. "MWF 10:30-11:20")

    Creates the Course table. Each course has one instructor.

    Output: a Course row
    """
    name = models.CharField(max_length=100)
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE)
    schedule = models.CharField(max_length=100)


class Enrollment(models.Model):
    """
    Input: student (StudentProfile), course (Course)

    Creates the Enrollment table. Links students to courses (many-to-many).

    Output: an Enrollment row
    """
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class Lecture(models.Model):
    """
    Input: course (Course), date (datetime), qr_code (string)

    Creates the Lecture table. Each lecture belongs to one course and has a unique QR code.

    Output: a Lecture row
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateTimeField()
    qr_code = models.CharField(max_length=100, unique=True)


class QRCodeUpload(models.Model):
    """
    Input: student (StudentProfile), lecture (Lecture or None), image (file)

    Creates the QRCodeUpload table. Stores a student's QR code photo and the upload time.
    The lecture is set to NULL if that lecture is deleted.

    Output: a QRCodeUpload row
    """
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.SET_NULL, null=True)
    image = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


def is_instructor(user):
    """
    Input: user (a Django User)

    Checks if the user has an InstructorProfile.

    Output: True or False
    """
    return InstructorProfile.objects.filter(user=user).count() > 0


def is_student(user):
    """
    Input: user (a Django User)

    Checks if the user has a StudentProfile.

    Output: True or False
    """
    return StudentProfile.objects.filter(user=user).count() > 0


def getUploadsForCourse(course):
    """
    Input: course (Course)

    Finds all QR code uploads for lectures of that course.

    Output: a QuerySet of QRCodeUpload rows
    """
    return QRCodeUpload.objects.filter(lecture__course=course)

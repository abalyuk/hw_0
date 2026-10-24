# LLM: Claude Opus 5.5 (Anthropic), run in a fresh chat with no other context.
#
# Prompt:
# "Write a Django models.py for an app called AttendanceChimp that tracks class
# attendance via QR codes. Users are students and instructors (two roles); use
# separate InstructorProfile and StudentProfile tables instead of one Users table.
# Each Course has one instructor, a name, and a meeting schedule. Students can
# enroll in multiple courses through an Enrollment table (many-to-many). Each
# Lecture belongs to a course and has a date and a QR identifier. A QRCodeUpload
# is a photo uploaded by a student, linked to a student and optionally a lecture.
# The design should be simple to use, support attendance analytics, and be robust
# to cheating. Include docstrings."

"""Database models for AttendanceChimp, a QR code based class attendance tracker."""

import uuid

from django.conf import settings
from django.db import models


class InstructorProfile(models.Model):
    """An instructor who teaches courses and displays lecture QR codes."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="instructor_profile"
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class StudentProfile(models.Model):
    """A student who enrolls in courses and uploads QR code photos to check in."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile"
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Course(models.Model):
    """A course taught by one instructor on a weekly meeting schedule."""

    name = models.CharField(max_length=200)
    instructor = models.ForeignKey(
        InstructorProfile, on_delete=models.PROTECT, related_name="courses"
    )
    meeting_days = models.CharField(
        max_length=7, help_text="Days the class meets, e.g. 'MWF' or 'TR'."
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    students = models.ManyToManyField(
        StudentProfile, through="Enrollment", related_name="courses"
    )

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    """Links a student to a course. A student can be enrolled in a course only once."""

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_enrollment")
        ]

    def __str__(self):
        return f"{self.student} in {self.course}"


class Lecture(models.Model):
    """A single class meeting with a unique, unguessable QR identifier."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lectures")
    date = models.DateField()
    qr_identifier = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        ordering = ["date"]
        constraints = [
            models.UniqueConstraint(fields=["course", "date"], name="unique_lecture_per_day")
        ]

    def __str__(self):
        return f"{self.course} on {self.date}"


class QRCodeUpload(models.Model):
    """A photo of a lecture QR code uploaded by a student as proof of attendance.

    The lecture is optional so an upload is still saved when its QR code cannot be
    decoded or matched. Upload time is set by the server, a student can count only
    once per lecture, and the image hash flags the same photo submitted twice.
    """

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="uploads")
    lecture = models.ForeignKey(
        Lecture, on_delete=models.SET_NULL, null=True, blank=True, related_name="uploads"
    )
    image = models.ImageField(upload_to="qr_uploads/")
    image_hash = models.CharField(max_length=64, unique=True, help_text="SHA-256 of the image file.")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        constraints = [
            models.UniqueConstraint(fields=["student", "lecture"], name="one_upload_per_lecture")
        ]

    def __str__(self):
        return f"{self.student} at {self.uploaded_at:%Y-%m-%d %H:%M}"

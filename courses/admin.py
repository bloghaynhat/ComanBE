from django.contrib import admin
from .models import Course, Section, Lesson, Enrollment, LessonProgress, Event, EventRegister

admin.site.register(Course)
admin.site.register(Section)
admin.site.register(Lesson)
admin.site.register(Enrollment)
admin.site.register(LessonProgress)
admin.site.register(Event)
admin.site.register(EventRegister)

from django.db import models
from django.contrib.auth.models import User

# Course
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='course_img/', blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

    def total_lessons(self):
        return self.lessons.count()

    def total_enrollments(self):
        return self.enrollment_set.count()

    def formatted_price(self):
        return f"{self.price:,.0f} VNĐ"

# Section
class Section(models.Model):
    course = models.ForeignKey(Course, related_name='sections', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} - {self.course.title}"
    
# Lesson
class Lesson(models.Model):
    section = models.ForeignKey('Section', related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    video_url = models.URLField(blank=True, null=True)
    article_content = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} - {self.section.title}"
    
    def has_video(self):
        return bool(self.video_url)

    def has_article(self):
        return bool(self.article_content)

# Enrollment
class Enrollment(models.Model):
    user = models.ForeignKey(User, related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    
# LessonProgress
class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progresses')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progresses')
    watched = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} - {'✅' if self.watched else '❌'}"

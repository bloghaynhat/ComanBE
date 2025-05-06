from django.db import models
from django.contrib.auth.models import User


# Course
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='course_img/', blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
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

# Event
class Event(models.Model):
    CATEGORY_CHOICES = [
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('webinar', 'Webinar'),
        ('conference', 'Conference'),
        # ... thêm nếu có nhiều loại khác
    ]
    
    title = models.CharField(max_length=255)
    date = models.DateField()
    time = models.CharField(max_length=50)
    location = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image_url = models.URLField(blank=True, null=True)
    image_upload = models.ImageField(upload_to='event_images/', blank=True, null=True)
    instructor = models.CharField(max_length=100)
    attendees = models.PositiveIntegerField(default=0)
    description = models.TextField()
    additional_description = models.TextField()
    duration = models.CharField(max_length=50)
    target_audience = models.TextField()
    prerequisites = models.TextField()
    price = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')  # admin tạo

    def image(self):
        return self.image_upload.url if self.image_upload else self.image_url
    
    def __str__(self):
        return self.title

# Moi sự kiện 1 người đăng kí 1 lần    
class EventRegister(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')  # mỗi user chỉ đăng ký 1 event 1 lần

    def __str__(self):
        return f"{self.user.username} đăng ký {self.event.title}"

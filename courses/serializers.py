from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Course, Enrollment, Lesson, LessonProgress, Section, Event, EventRegister
from django.contrib.auth.models import User

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        
class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'
        
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        
class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = '__all__'
        
class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        
class EventRegisterSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # hiển thị username
    event = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = EventRegister
        fields = '__all__'
        
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Lấy thông tin nhóm người dùng
        user = self.user
        groups = user.groups.values_list('name', flat=True)

        # Thêm role vào trong dữ liệu trả về
        data['role'] = groups[0] if groups else 'user'
        
        return data
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
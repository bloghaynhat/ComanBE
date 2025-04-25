from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response

from .models import Course, Enrollment, Lesson, LessonProgress, Section, Event, EventRegister
from .serializers import CourseSerializer, EnrollmentSerializer, LessonSerializer, LessonProgressSerializer, SectionSerializer, EventSerializer, EventRegisterSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    
class LessonProgressViewSet(viewsets.ModelViewSet):
    queryset = LessonProgress.objects.all()
    serializer_class = LessonProgressSerializer
    
class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]  # chỉ admin tạo/sửa/xóa
        return [IsAuthenticatedOrReadOnly()]  # người dùng thường chỉ xem

class EventRegisterViewSet(viewsets.ModelViewSet):
    queryset = EventRegister.objects.all()
    serializer_class = EventRegisterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        event_id = request.data.get("event_id")

        if EventRegister.objects.filter(user=user, event_id=event_id).exists():
            return Response({"detail": "Bạn đã đăng ký sự kiện này rồi."}, status=400)

        register = EventRegister.objects.create(user=user, event_id=event_id)
        serializer = self.get_serializer(register)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        event_id = request.data.get("event_id")
        register = EventRegister.objects.filter(user=user, event_id=event_id).first()

        if not register:
            return Response({"detail": "Bạn chưa đăng ký sự kiện này."}, status=404)

        register.delete()
        return Response({"detail": "Đã hủy đăng ký sự kiện."}, status=204)

    @action(detail=False, methods=['get'], url_path='is-registered/(?P<event_id>[^/.]+)')
    def is_registered(self, request, event_id=None):
        user = request.user
        registered = EventRegister.objects.filter(user=user, event_id=event_id).exists()
        return Response({"registered": registered})

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, EnrollmentViewSet, LessonProgressViewSet, SectionViewSet, LessonViewSet, EventViewSet, EventRegisterViewSet, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from .views_auth import CurrentUserView

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'lessonprogresses', LessonProgressViewSet)
router.register(r'events', EventViewSet)
router.register(r'event-registers', EventRegisterViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/user/', CurrentUserView.as_view(), name='current-user'),
]
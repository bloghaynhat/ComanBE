from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.utils.timezone import now, timedelta
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.contrib.auth.models import User, Group

from .models import Course, Enrollment, Lesson, LessonProgress, Section, Event, EventRegister
from .serializers import CourseSerializer, EnrollmentSerializer, LessonSerializer, LessonProgressSerializer, SectionSerializer, EventSerializer, EventRegisterSerializer, SectionWithLessonsSerializer, UserSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    @action(detail=True, methods=['get'], url_path="sections")
    def get_sections(self, request, pk=None):
        sections = Section.objects.filter(course_id=pk)
        serializer = SectionSerializer(sections, many=True)
        return Response(serializer.data)
       
    @action(detail=True, methods=["get"], url_path="sections-with-lessons")
    def sections_with_lessons(self, request, pk=None):
        sections = Section.objects.filter(course_id=pk)
        serializer = SectionWithLessonsSerializer(sections, many=True)
        return Response(serializer.data)
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]
    
    @action(detail=False, methods=['get'], url_path='latest-with-students', permission_classes=[permissions.AllowAny])
    def student_counts(self, request):
        top = request.query_params.get('top')
        courses = Course.objects.annotate(student_count=Count('enrollments')).order_by('-created_at')

        if top and top.isdigit():
            courses = courses[:int(top)]

        data = [
            {
                "course_id": course.id,
                "title": course.title,
                "image": course.image.url if course.image else None,
                "created_at": course.created_at,
                "price": course.price,
                "student_count": course.student_count
            } for course in courses
        ]
        return Response(data)
    
    @action(detail=False, methods=['get'], url_path='top-revenue', permission_classes=[permissions.AllowAny])
    def top_revenue_courses(self, request):
        top = request.query_params.get('top')  # Nếu không truyền tham số top, nó sẽ là None

        if top:
            try:
                top = int(top)
            except ValueError:
                return Response({"detail": "Tham số 'top' phải là một số nguyên hợp lệ."}, status=400)
            courses = Course.objects.annotate(
                total_revenue=Sum('enrollments__course__price'),
                total_enrollments=Count('enrollments')
            ).order_by('-total_revenue')[:top]  # Giới hạn số lượng theo 'top' nếu có
        else:
            courses = Course.objects.annotate(
                total_revenue=Sum('enrollments__course__price'),
                total_enrollments=Count('enrollments')
            ).order_by('-total_revenue')  # Lấy tất cả khóa học nếu không có tham số 'top'

        data = [
            {
                "course_id": course.id,
                "title": course.title,
                "image": course.image.url if course.image else None,
                "created_at": course.created_at,
                "total_revenue": course.total_revenue if course.total_revenue else 0,
                "total_enrollments": course.total_enrollments
            }
            for course in courses
        ]
        return Response(data)

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.AllowAny]  # Cho phép truy cập công khai

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Enrollment.objects.filter(user=user)
        return Enrollment.objects.all()

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"detail": "Bạn cần đăng nhập để mua khóa học."}, status=401)

        user = request.user
        course_id = request.data.get("course_id")

        if Enrollment.objects.filter(user=user, course_id=course_id).exists():
            return Response({"detail": "Bạn đã đăng ký khóa học này rồi."}, status=400)

        register = Enrollment.objects.create(user=user, course_id=course_id)
        serializer = self.get_serializer(register)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='is-enrolled/(?P<course_id>[^/.]+)')
    def is_enrolled(self, request, course_id=None):
        user = request.user
        if not user.is_authenticated:
            return Response({"enrolled": False})
        enrolled = Enrollment.objects.filter(user=user, course_id=course_id).exists()
        return Response({"enrolled": enrolled})

    @action(detail=False, methods=['get'], url_path='paid', permission_classes=[permissions.AllowAny])
    def paid_enrollments(self, request):
        # Lấy group "user"
        try:
            user_group = Group.objects.get(name='user')
        except Group.DoesNotExist:
            return Response({"detail": "Group 'user' không tồn tại."}, status=400)

        # Lấy enrollment thỏa điều kiện
        enrollments = Enrollment.objects.select_related('course', 'user') \
            .filter(
                course__price__gt=0,
                user__groups=user_group
            ).order_by('-enrolled_at')

        # Chuẩn bị dữ liệu trả về
        data = [
            {
                "user_id": enrollment.user.id,
                "username": enrollment.user.username,
                "first_name": enrollment.user.first_name,
                "last_name": enrollment.user.last_name,
                "course_title": enrollment.course.title,
                "price": enrollment.course.price,
                "enrolled_at": enrollment.enrolled_at,
            }
            for enrollment in enrollments
        ]

        return Response(data)

    
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    
class LessonProgressViewSet(viewsets.ModelViewSet):
    queryset = LessonProgress.objects.all()
    serializer_class = LessonProgressSerializer
    
class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    
    @action(detail=True, methods=["get"], url_path="lessons")
    def get_lessons(self, request, pk=None):
        lessons = Lesson.objects.filter(section_id=pk)
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

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
    permission_classes = [permissions.AllowAny]  # Cho phép truy cập công khai

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return EventRegister.objects.filter(user=user)
        return EventRegister.objects.all()

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"detail": "Bạn cần đăng nhập để đăng ký sự kiện."}, status=401)

        user = request.user
        event_id = request.data.get("event_id")

        # Kiểm tra sự kiện có tồn tại trong cơ sở dữ liệu không
        try:
            event = Event.objects.get(id=event_id)  # Tìm sự kiện theo event_id
        except Event.DoesNotExist:
            return Response({"detail": "Sự kiện không tồn tại."}, status=400)

        # Kiểm tra nếu người dùng đã đăng ký sự kiện này
        if EventRegister.objects.filter(user=user, event=event).exists():
            return Response({"detail": "Bạn đã đăng ký sự kiện này rồi."}, status=400)

        # Tạo bản ghi đăng ký sự kiện mới
        register = EventRegister.objects.create(user=user, event=event)
        serializer = self.get_serializer(register)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"detail": "Bạn cần đăng nhập để hủy đăng ký."}, status=401)

        user = request.user
        event_id = kwargs.get("pk")  # Lấy event_id từ URL

        if not event_id:
            return Response({"detail": "Không có event_id trong yêu cầu."}, status=400)

        register = EventRegister.objects.filter(user=user, event_id=event_id).first()

        if not register:
            return Response({"detail": "Bạn chưa đăng ký sự kiện này."}, status=404)

        register.delete()
        return Response({"detail": "Đã hủy đăng ký sự kiện."}, status=204)

    @action(detail=False, methods=['get'], url_path='is-registered/(?P<event_id>[^/.]+)')
    def is_registered(self, request, event_id=None):
        user = request.user
        if not user.is_authenticated:
            return Response({"registered": False})
        registered = EventRegister.objects.filter(user=user, event_id=event_id).exists()
        return Response({"registered": registered})

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
# Tổng quan 4 ô 
class DashboardStatsView(APIView):
    def get(self, request):
        today = now().date()

        # Tuần này
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=7)

        # Tuần trước
        start_of_last_week = start_of_week - timedelta(days=7)
        end_of_last_week = start_of_week
        
        # Lấy ngày đầu tháng này
        start_of_this_month = today.replace(day=1)

        # Lấy ngày cuối tháng trước = ngày đầu tháng này - 1
        end_of_last_month = start_of_this_month - timedelta(days=1)

        # Ngày đầu tháng trước
        start_of_last_month = end_of_last_month.replace(day=1)

        # Doanh thu: lấy trong tháng hiện tại
        start_of_month = today.replace(day=1)

        # -------- THỐNG KÊ -------- #
        total_courses = Course.objects.count()
        new_courses_this_week = Course.objects.filter(created_at__range=(start_of_week, end_of_week)).count()
        new_courses_last_week = Course.objects.filter(created_at__range=(start_of_last_week, end_of_last_week)).count()

        total_users = User.objects.count()
        new_users_this_week = User.objects.filter(date_joined__range=(start_of_week, end_of_week)).count()
        new_users_last_week = User.objects.filter(date_joined__range=(start_of_last_week, end_of_last_week)).count()

        total_enrollments = Enrollment.objects.count()
        new_enrollments_this_week = Enrollment.objects.filter(enrolled_at__range=(start_of_week, end_of_week)).count()
        new_enrollments_last_week = Enrollment.objects.filter(enrolled_at__range=(start_of_last_week, end_of_last_week)).count()

        # Doanh thu tháng này
        enrollments_this_month = Enrollment.objects.filter(enrolled_at__gte=start_of_month)
        revenue = enrollments_this_month.aggregate(total=Sum('course__price'))['total'] or 0
        # Truy vấn doanh thu tháng trước
        enrollments_last_month = Enrollment.objects.filter(enrolled_at__range=(start_of_last_month, end_of_last_month))
        revenue_last_month = enrollments_last_month.aggregate(total=Sum('course__price'))['total'] or 0

        # -------- TÍNH % THAY ĐỔI -------- #
        def percent_change(current, previous):
            if previous == 0:
                return "+∞%" if current > 0 else "0%"
            change = ((current - previous) / previous) * 100
            return f"{change:+.0f}%"

        data = {
            "total_courses": {
                "title": "Tổng khóa học",
                "icon": "BookOpen",
                "value": total_courses,
                "change": (
                    f"-{new_courses_this_week - new_courses_last_week} so với tuần trước"
                    if new_courses_this_week - new_courses_last_week < 0
                    else f"+{new_courses_this_week - new_courses_last_week} so với tuần trước"
                    )
            },
            "total_users": {
                "title": "Tổng người dùng",
                "icon": "Users",
                "value": total_users,
                "change": (
                    f"-{new_users_this_week - new_users_last_week} so với tuần trước"
                    if new_users_this_week - new_users_last_week < 0
                    else f"+{new_users_this_week - new_users_last_week} so với tuần trước"
                )
            },
            "monthly_revenue": {
                "title": "Doanh thu tháng",
                "icon": "DollarSign",
                "value": f"{revenue:,.0f}đ",
                "change": f"+{percent_change(revenue, revenue_last_month)} so với tháng trước"
            },
            "new_enrollments": {
                "title": "Đăng kí mới",
                "icon": "PlusCircle",
                "value": total_enrollments,
                "change": (
                    f"-{new_enrollments_this_week - new_enrollments_last_week} so với tuần trước"
                    if new_enrollments_this_week - new_enrollments_last_week < 0
                    else f"+{new_enrollments_this_week - new_enrollments_last_week} so với tuần trước"
                )
            }
        }
        return Response(data)

class UserAPIView(APIView):
    def get(self, request, user_id=None):
        # Lọc user trong group 'user'
        group = Group.objects.get(name='user')
        
        if user_id:
            try:
                # Lấy user theo ID và kiểm tra group
                user = User.objects.get(pk=user_id, groups=group)
                serializer = UserSerializer(user)
                return Response(serializer.data)
            except User.DoesNotExist:
                return Response({'error': 'User not found or does not belong to the "user" group'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Lọc tất cả user thuộc group 'user'
            users = User.objects.filter(groups=group)
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
    
    def patch(self, request, user_id=None):
        group = Group.objects.get(name='user')
        
        if user_id:
            try:
                # Lấy user theo ID và kiểm tra group
                user = User.objects.get(pk=user_id, groups=group)
                
                # Cập nhật trạng thái is_active từ dữ liệu request
                is_active = request.data.get('is_active')
                if is_active is not None:
                    user.is_active = is_active
                    user.save()
                    return Response({'message': 'User status updated successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Missing is_active field'}, status=status.HTTP_400_BAD_REQUEST)
            
            except User.DoesNotExist:
                return Response({'error': 'User not found or does not belong to the "user" group'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
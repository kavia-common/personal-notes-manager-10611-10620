from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, viewsets, permissions, filters
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

from .models import Note, Profile
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ProfileSerializer,
    NoteSerializer,
)

# PUBLIC_INTERFACE
@api_view(['GET'])
def health(request):
    """Health check endpoint."""
    return Response({"message": "Server is up!"})


# AUTH & USER MANAGEMENT

# PUBLIC_INTERFACE
class RegisterView(APIView):
    """
    Register a new user.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUBLIC_INTERFACE
class LoginView(APIView):
    """
    Log in a user (returns auth token).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({"detail": "Username and password required."},
                            status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({"detail": "Invalid credentials."},
                            status=status.HTTP_401_UNAUTHORIZED)

        # Use DRF's Token for simplicity
        token, _ = Token.objects.get_or_create(user=user)
        login(request, user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})


# PUBLIC_INTERFACE
class LogoutView(APIView):
    """
    Log out the current user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Only using Django session auth here for compatibility; token deletion also possible.
        logout(request)
        return Response({"detail": "Logged out"}, status=status.HTTP_200_OK)


# PUBLIC_INTERFACE
class ProfileView(APIView):
    """
    Retrieve or update the current user's profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# NOTES CRUD AND SEARCH

class NotesPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

# PUBLIC_INTERFACE
class NoteViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD operations, listing, searching, and filtering for notes.
    """
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotesPagination

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['updated_at', 'created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = Note.objects.filter(user=user)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        # Optionally add date filtering
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start:
            queryset = queryset.filter(updated_at__date__gte=start)
        if end:
            queryset = queryset.filter(updated_at__date__lte=end)
        return queryset.order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Note, Profile

# PUBLIC_INTERFACE
class UserSerializer(serializers.ModelSerializer):
    """Serializer for built-in User; excludes sensitive fields."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


# PUBLIC_INTERFACE
class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        Profile.objects.create(user=user)  # Create empty profile for the new user
        return user


# PUBLIC_INTERFACE
class ProfileSerializer(serializers.ModelSerializer):
    """User profile serializer."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'bio', 'updated_at']


# PUBLIC_INTERFACE
class NoteSerializer(serializers.ModelSerializer):
    """Note serializer for CRUD and listing."""
    class Meta:
        model = Note
        fields = ['id', 'user', 'title', 'content', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


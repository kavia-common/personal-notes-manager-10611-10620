from django.db import models
from django.contrib.auth.models import User

# PUBLIC_INTERFACE
class Profile(models.Model):
    """
    User profile model for extending the built-in User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

# PUBLIC_INTERFACE
class Note(models.Model):
    """
    Model representing a user's personal note.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Note({self.title}) by {self.user.username}'

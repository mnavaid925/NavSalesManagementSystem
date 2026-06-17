"""Authentication backend that accepts either a username or an email address."""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        if username is None or password is None:
            return None
        try:
            # Case-insensitive match on either field; fetch one to run the password check.
            user = User.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).order_by("id").first()
        except User.DoesNotExist:
            return None
        if user is None:
            # Run the default hasher anyway to mitigate timing-based user enumeration.
            User().set_password(password)
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

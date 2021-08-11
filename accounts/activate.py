from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from .models import User

@require_http_methods(["GET"])
def activate(request, uidb64, token):
  try:
    uid = force_text(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=uid)
  except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
    messages.add_message(request, messages.WARNING, str(e))
    user = None

  if user is not None and account_activation_token.check_token(user, token):
    user.is_active = True
    user.save()
    login(request, user)
    messages.add_message(request, messages.INFO, f'Hi {request.user}')
  else:
    messages.add_message(request, messages.WARNING, 'Account activation link is invalid.')

  redirection_url = 'home' if user.user_role == 'S' else 'cms_home_page'
  return redirect(redirection_url)

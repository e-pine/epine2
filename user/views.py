from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from .forms import *
from .decorators import *
from .models import UserProfile

# email verify
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token

# Create your views here.
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user: None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Thank you! you can now login to your account.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid!")
    return redirect('login')

def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("user/template_activate_account.html",{
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'We sent an email to your account, clik the link to verified your registration!')
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')
        
@unauthenticated_user
def user_register(request):
    page = 'register'
    form = CreateUserForm()
    
    if request.method == 'POST':
        form = CreateUserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
           
            activateEmail(request, user, form.cleaned_data.get('email'))
            
         
            # role = form.cleaned_data.get('role')
            role = 'buyer'
            try:
                group = Group.objects.get(name=role)
                group.user_set.add(user)
            except Group.DoesNotExist:
                user.delete()
                messages.error(request, 'Invalid role. Please select a valid role.')
                return redirect('register')
          
            UserProfile.objects.create(user=user, role=role)
            
            return redirect('login')
        else:
            for error in form.errors.values():
                messages.error(request, error)

    context = {'form': form, 'page': page}
    return render(request, 'register.html', context)


@unauthenticated_user
def user_login(request):
    page = 'login'
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user is not None and user.check_password(password):
            login(request, user)
            return redirect('index')
        else:
            if user is None:
                messages.error(request, 'Username does not exist.')
            else:
                messages.error(request, 'Incorrect password.')

    return render(request, 'login.html', {'page': page})

def user_logout(request):
    logout(request)
    return redirect('login')

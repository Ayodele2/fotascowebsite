from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import bcrypt

def home(request):
    return render(request,"index.html")

@login_required
def dashboard(request):
    return render(request, "staff.html")

@login_required
def attendance(request):
    return render(request, "attendance.html")


def application(request):
    return render(request, "leaveapplicatio.html")

def chatroom(request):
    return render(request, "chat.html")

def load_application(request):
    return render(request, "loanapplcation.html")

def user_role(request):
    return render(request, 'newroles.html')


def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password = password_byte_enc , hashed_password = hashed_password_bytes)

def get_password_hash(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password


def create_user(request):
    if request.method == "POST":
        username = str(request.POST['username']).lower()
        email = str(request.POST['email']).lower()
        password = str(request.POST['password']).lower()
        confirm_password = str(request.POST['confirm_password']).lower()
        print("password", password)
        print("confirm", confirm_password)
        if password == confirm_password:
            hash_password = get_password_hash(password)
            if User.objects.filter(username=username).exists():
                 messages.warning(request, "Username already exists")
                 return redirect('login') 
            if User.objects.filter(email=email).exists():
                messages.warning(request, "Email already exists")
                return redirect('login') 
            user = User.objects.create_user(username=username,email=email, password=password)
            if user:
                user.save()
                messages.success(request, "User created successfully!,redirect to profile details")
                return redirect("register")
        else:
             messages.warning(request, "Passwords do not match.")
    return render(request, "user.html")



def create_user_profile(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  
            messages.success(request, "User profile created successfully!")
            return redirect('login') 
        else:
            messages.error(request, "Please correct this error before proceed.\n")
            for index, field in enumerate(form,start=1):
                for error in field.errors:
                    messages.error(request, f"\n{error}\n")
                    
            # for error in form.non_field_errors():
            #     messages.error(request, error)
    else:
        form = UserRegistrationForm()

    return render(request, 'form.html', {'form': form})



def login_user(request):
    if request.method == 'POST':
       username = str(request.POST['username']).lower()
       password = str(request.POST['password']).lower()
       hash_password = get_password_hash(password)
       print(username)
       print(password)
       user = authenticate(username=username, password=password)
       if user is not None:
           login(request,user)
           return redirect('dashboard')

       else:
           messages.error(request, "Invalid Credientials")
           return redirect('login') 
        
        
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('/')
from django.shortcuts import get_object_or_404, render,redirect
from accounts.models import Account,UserProfile
from carts.models import Cart
from store.models import Variation
from .forms import RegistrationForm,UserProfileForm,UserForm 
from .models import Account
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.core.mail import EmailMessage 
from django.contrib.auth.tokens import default_token_generator 
from carts.views import _cart_id
from carts.models import Cart,CartItem
import requests 
from orders.models import Order, OrderProduct

# REGISTRATION
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username=email.split("@")[0]

            user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
            user.phone_number = phone_number
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,'Registraton successful ; We have send you a Verification email to Activate your Account')
            return redirect('register')
    else:
         form = RegistrationForm()
   
    context = {
        'form':form,
    }
    return render(request,'accounts/register.html',context)

def activate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Your Account is activated')
        return redirect('login')
    else:
        messages.error(request,'Something Wrong')
        return redirect('register')


# FORGOT PASSWORD
def forgotPassword(request,*args,**kwargs):
    if request.method  == 'POST':
        email = request.POST.get('email')
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html',{
                'user':user,
                'domain':current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,'Password reset email is sent to your mail')
            return redirect('login')

        else:
            messages.error(request,'Account does not exist!')
            return redirect('forgotPassword')

    return render(request,'accounts/forgotPassword.html')

def resetpassword_validate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,'Please reset your Password.')
        return redirect('resetPassword')
    else:
        messages.error(request,'This link was expired.')
        return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Your Password Changed Successfully')
            return redirect('login')
        else:
            messages.error(request,'Password do not match') 
            return redirect('resetPassword')

    else:
        return render(request,'accounts/resetPassword.html')
    

# LOGIN
def login_page(request):
    if request.method == 'POST':

        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email,password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                
                if is_cart_item_exists:

                    cart_item = CartItem.objects.filter(cart=cart)

                    product_variation = []

                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []

                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity = item.quantity + 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)

                    for item in cart_item:
                        item.user = user
                        item.save()
            except:
                pass

            login(request, user)
            messages.success(request,'You are logged in')
            url= request.META.get('HTTP_REFERER')

            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('home')
        
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('login')
    return render(request,'accounts/login.html')


# LOGOUT
@login_required(login_url = 'login')
def logout_page(request):
    logout(request)
    messages.success(request,'You are logged out')
    return redirect('home')



@login_required(login_url = 'login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)
    orders_count = orders.count()
    context={

        'orders_count':orders_count,

    }
    return render(request,'accounts/dashboard.html',context)


@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user = request.user,is_ordered=True).order_by('-created_at')
    context = {

        'orders': orders,

    }
    return render(request,'accounts/my_orders.html',context)



@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile,user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST,instance=request.user)
        profile_form = UserProfileForm(request.POST,instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid(): 
            user_form.save()
            profile_form.save()
            messages.success(request,'Your Profile Has Been Changed')
            return redirect('dashboard')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {

        'user_form':user_form,
        'profile_form':profile_form,

    }
    return render(request,'accounts/edit_profile.html',context)



@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['Confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request,'Password Changed Successfully')
                return redirect('dashboard')
            else:
                messages.error(request,'Please Enter Valid Password')
                return redirect('change_password')
        else:
            messages.error(request,'Password Does Not Match ! try agian')
            return redirect('change_password')

    return render(request,'accounts/change_password.html')


@login_required(login_url='login')
def order_detail(request,order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context = {

        'order_detail':order_detail,
        'order':order,
        'subtotal':subtotal,

    }
    return render(request,'accounts/order_detail.html',context)

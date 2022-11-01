from itertools import product
from unicodedata import category
from django.shortcuts import redirect, render
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from django.db.models import Q

from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from accounts.models import Account
from manager.forms import ProductForm, VariationForm
from store.models import Product, Variation
from orders.models import Order
from category.models import Category


# Create your views here.
@never_cache
def manager_login(request):
  if request.user.is_authenticated:
    if request.user.is_superadmin:
      return redirect('manager_dashboard')
    else:
      return redirect('home')
  else:
    if request.method == 'POST':
      email = request.POST['email']
      password = request.POST['password']
      
      user = authenticate(request, username=email, password=password)
      if user is not None:
        if user.is_active:
          if user.is_superadmin:
            login(request, user)
            return redirect('manager_dashboard')
          else:
            messages.warning(request, 'You are logged in a non-staff account')
        else:
          messages.warning(request, 'Your account is not verified. Please verify your account')

      else:
        messages.error(request, 'Email or Password is incorrect')
  return render(request, 'manager/manager_signin.html')

@never_cache
def manager_logout(request):
  logout(request)
  return redirect('manager_login')




@login_required(login_url='manager_login')
def manager_dashboard(request):
    if request.user.is_superadmin:
        user_count = Account.objects.filter(is_superadmin=False).count()
        product_count = Product.objects.all().count()
        order_count = Order.objects.filter(is_ordered=True).count()
        category_count = Category.objects.all().count()

        total_sales = 0
        orders = Order.objects.filter(is_ordered = True)

        for order in orders:
            total_sales += order.order_total

        context = {

            'user_count':user_count,
            'product_count':product_count,
            'order_count':order_count,
            'category_count':category_count,
            'total_sales':total_sales,
        }

        return render(request,'manager/manager_dashboard.html',context)
    else:
        return redirect('home')

@login_required(login_url='manager_login')
def category_view(request):
  if request.user.is_superadmin:
    category = Category.objects.all()
    
    product = Category.objects.filter()
    count=product.count()
    print(count)
  
    context = {

      'category':category,
      'count':count,
     }

    return render(request,'manager/categoryview.html',context)
  else:
    return redirect('home')




@login_required(login_url='manager_login')
def manage_user(request):
  if request.user.is_superadmin:
    if request.method == 'POST':
      keyword = request.POST['keyword']
      users = Account.objects.filter(Q(first_name__startswith=keyword) | Q(last_name__startswith=keyword) | Q(username__startswith=keyword) | Q(email__startswith=keyword) | Q(phone_number__startswith=keyword)).order_by('id')
    
    else:
      users = Account.objects.filter(is_superadmin=False) .order_by('id')
    
    paginator = Paginator(users, 10)
    page = request.GET.get('page')
    paged_users = paginator.get_page(page)
    
    context = {
      'users': paged_users,
    }
    return render(request, 'manager/user_management.html', context)
  
  else:
    return redirect('home')

@login_required(login_url='manager_login')
def ban_user(request,user_id):
    if request.user.is_superadmin:
        user = Account.objects.get(id=user_id)
        user.is_active = False
        user.save()

        return redirect('manage_user')
  
    else:
        return redirect('home')

@login_required(login_url='manager_login')
def unban_user(request,user_id):
    if request.user.is_superadmin:
        user = Account.objects.get(id=user_id)
        user.is_active = True
        user.save()

        return redirect('manage_user')
  
    else:
        return redirect('home')




@login_required(login_url='manager_login')
def manage_product(request):
    if request.user.is_superadmin:
        if request.method == 'POST':
            keyword = request.POST['keyword']
            products = Product.objects.filter(Q(product_name__startswith=keyword) | Q(slug__startswith=keyword) | Q(category__category_name__startswith=keyword)).order_by('id')
        else:
            products = Product.objects.all().order_by('id')
        
        paginator = Paginator(products, 10)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

        context = {

            'products' : products,
            'paged_products':paged_products,
        }

        return render(request,'manager/product_management.html',context)

    else:
        return redirect('home')

@login_required(login_url='manager_login')
def delete_product(request,product_id):
    if request.user.is_superadmin:
        product = Product.objects.get(id=product_id)
        product.delete()
        return redirect('manage_product')
    else:
        return redirect('home')

@login_required(login_url='manager_login')
def add_product(request):
    form=None
    if request.user.is_superadmin:
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('manage_product')
        else:
            form = ProductForm()
            context = {
                'form': form
            }
            return render(request, 'manager/add_product.html', context)

    else:
        return redirect('home')

@login_required(login_url='manager_login')
def edit_product(request,product_id):
    if request.user.is_superadmin:
      product = Product.objects.get(id=product_id)
      form = ProductForm(instance=product)

      if request.method == 'POST':
        try:
          form = ProductForm(request.POST, request.FILES, instance=product)
          if form.is_valid():
            form.save()
            
            return redirect('manage_product')
      
        except Exception as e:
          raise e

      context = {
        'product': product,
        'form': form
      }
      return render(request, 'manager/edit_product.html', context)

    else:
      return redirect('home')




@login_required(login_url='manager_login')
def manage_order(request):
  if request.user.is_superadmin:
    if request.method == 'POST':
      keyword = request.POST['keyword']
      orders = Order.objects.filter(Q(is_ordered = True),Q(first_name__startswith = keyword) | Q(last_name__startswith = keyword) | Q(email__startswith = keyword) | Q(order_number__startswith = keyword) | Q(user__username__startswith = keyword)).order_by('-order_number')
    else:
      orders = Order.objects.filter(is_ordered=True).order_by('-order_number')
    
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    
    context = {
      
      'orders': paged_orders
    }

    return render(request, 'manager/order_management.html', context)
  
  else:
    return redirect('home')

@login_required(login_url='manager_login')
def cancel_order(request,order_number):
  if request.user.is_superadmin:
    order = Order.objects.get(order_number=order_number)
    order.status = 'Cancelled'
    order.save()
    return redirect('manage_order')

  else:
    return redirect('home')

@login_required(login_url='manager_login')
def accept_order(request,order_number):
  if request.user.is_superadmin:
    order = Order.objects.get(order_number=order_number)
    order.status = 'Accepted'
    order.save()
    return redirect('manage_order')

  else:
    return redirect('home')

@login_required(login_url='manager_login')
def complete_order(request,order_number):
  if request.user.is_superadmin:
    order = Order.objects.get(order_number=order_number)
    order.status = 'Completed'
    order.save()
    return redirect('manage_order')

  else:
    return redirect('home')




@login_required(login_url='manager_login')
def manage_variation(request):
  if request.user.is_superadmin:
    if request.method == 'POST':
      keyword = request.POST['keyword']
      variations = Variation.objects.filter(Q(product__product_name__startswith=keyword) | Q(variation_value__startswith=keyword)).order_by('id')
    
    else:
      variations = Variation.objects.all().order_by('id')
    
    paginator = Paginator(variations, 10)
    page = request.GET.get('page')
    paged_variations = paginator.get_page(page)
    
    context = {
      'variations': paged_variations
    }
    return render(request, 'manager/variation_management.html', context)

  else:
    return redirect('home')

@login_required(login_url='manager_login')
def add_variation(request):
  if request.user.is_superadmin:
    if request.method == 'POST':
      form = VariationForm(request.POST)
      if form.is_valid():
        form.save()
        return redirect('manage_variation')
    
    else:
      form = VariationForm()
    
    context = {
      'form': form
    }
    return render(request, 'manager/add_variation.html', context)
  
  else:
    return redirect('home')

@login_required(login_url='manager_login')
def update_variation(request, variation_id):
  if request.user.is_superadmin:
    variation = Variation.objects.get(id=variation_id)
  
    if request.method == 'POST':
      form = VariationForm(request.POST ,instance=variation)
      if form.is_valid():
        form.save()
        return redirect('manage_variation')
    
    else:
      form = VariationForm(instance=variation)
    
    context = {
      'variation': variation,
      'form': form
    }
    return render(request, 'manager/update_variation.html', context)
  
  else:
    return redirect('home')

@login_required(login_url='manager_login')
def delete_variation(request, variation_id):
  if request.user.is_superadmin:
    variation = Variation.objects.get(id=variation_id)
    variation.delete()
    return redirect('manage_variation')

  else:
    return redirect('home')




@login_required(login_url='manager_login')
def admin_order(request):
  if request.user.is_superadmin:
    current_user = request.user
  
    if request.method == 'POST':
      keyword = request.POST['keyword']
      orders = Order.objects.filter(Q(user=current_user), Q(is_ordered=True), Q(order_number__startswith=keyword) | Q(user__email__startswith=keyword) | Q(first_name__startswith=keyword) | Q(last_name__startswith=keyword) | Q(phone__startswith=keyword)).order_by('-created_at')
      
    else:
      orders = Order.objects.filter(user=current_user, is_ordered=True).order_by('-created_at')
    
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    context = {
      'orders': paged_orders,
    }
    return render(request, 'manager/admin_orders.html', context)
  
  else:
    return redirect('home')




@login_required(login_url='manager_login')
def admin_change_password(request):
  if request.user.is_superadmin:
    if request.method == 'POST':
      current_user = request.user
      current_password = request.POST['current_password']
      password = request.POST['password']
      confirm_password = request.POST['confirm_password']
      
      if password == confirm_password:
        if check_password(current_password, current_user.password):
          if check_password(password, current_user.password):
            messages.warning(request, 'Current password and new password is same')
          else:
            hashed_password = make_password(password)
            current_user.password = hashed_password
            current_user.save()
            messages.success(request, 'Password changed successfully')
        else:
          messages.error(request, 'Wrong password')
      else:
        messages.error(request, 'Passwords does not match')
    
    return render(request, 'manager/admin_change_password.html')
  
  else:
    return redirect('home')

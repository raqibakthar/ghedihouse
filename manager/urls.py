from django.urls import path
from . import views
from .views import *


urlpatterns = [

    path('login/',views.manager_login, name='manager_login'),
    path('logout/', manager_logout, name='manager_logout'),

    path('manager_dashboard/',views.manager_dashboard,name='manager_dashboard'),

    path('category_view/',category_view,name='category_view'),

    path('manage_user/',views.manage_user,name='manage_user'),
    path('ban_user/<int:user_id>/',views.ban_user, name='ban_user'),
    path('unban_user/<int:user_id>/',views.unban_user, name='unban_user'),

    path('manage_product/',views.manage_product,name='manage_product'),
    path('delete_product/<int:product_id>/',views.delete_product,name='delete_product'),
    path('add_product/',views.add_product,name='add_product'),
    path('edit_product/<int:product_id>/', edit_product, name='edit_product'),

    path('manage_order/',views.manage_order,name='manage_order'),
    path('cancel_order/<int:order_number>/',views.cancel_order,name='cancel_order'),
    path('accept_order/<int:order_number>/', accept_order, name='accept_order'),
    path('complete_order/<int:order_number>/', complete_order, name='complete_order'),

    path('manage_variation/',manage_variation, name='manage_variation'),
    path('add_variation/', add_variation, name='add_variation'),
    path('update_variation/<int:variation_id>/', update_variation, name='update_variation'),
    path('delete_variation/<int:variation_id>/', delete_variation, name='delete_variation'),

    path('admin_orders/', admin_order, name='admin_orders'),
    path('admin_cancel_order/<int:order_number>/', cancel_order, name='admin_cancel_order'),

    path('change_password/', admin_change_password, name='admin_change_password'),


] 
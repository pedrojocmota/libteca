from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('catalog/', views.catalog_view, name='catalog'),
    path('borrow/<int:book_id>/', views.borrow_request_view, name='borrow'),
    path('my-books/', views.my_books_view, name='my_books'),
    path('admin-panel/', views.admin_panel_view, name='admin_panel'),
    path('admin-panel/<int:request_id>/<str:action>/', views.handle_request_view, name='handle_request'),
    path('', views.index_view, name='index'),
]
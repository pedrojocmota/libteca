from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta
from .models import Book, BorrowRequest
import json as json_module

# ─── Auth ───────────────────────────────────────────────

def index_view(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('/admin-panel/')
            return redirect('/catalog/')
        return render(request, 'login.html', {'error': 'Invalid credentials or account locked'})
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        User.objects.create_user(username=username, password=password)
        return redirect('/login/')
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('/login/')

# ─── User ────────────────────────────────────────────────

@login_required(login_url='/login/')
def catalog_view(request):
    if request.user.is_staff:
        return redirect('/admin-panel/')
    books = Book.objects.all()
    
    # IDs dos livros que o utilizador tem ativos
    borrowed_book_ids = set(BorrowRequest.objects.filter(
        user=request.user,
        status='accepted'
    ).values_list('book_id', flat=True))
    
    books_data = []
    for book in books:
        books_data.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'available': book.available,
            'borrowed_by_me': book.id in borrowed_book_ids
        })
    
    books_json = json_module.dumps(books_data)
    return render(request, 'catalog.html', {'books_json': books_json})

@login_required(login_url='/login/')
def borrow_request_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if not book.available:
        return redirect('/catalog/')

    if request.method == 'POST':
        now = timezone.now()

        # Limite 1 — máximo 10 pedidos por hora
        one_hour_ago = now - timedelta(hours=1)
        requests_last_hour = BorrowRequest.objects.filter(
            user=request.user,
            request_date__gte=one_hour_ago
        ).count()

        if requests_last_hour >= 10:
            return render(request, 'borrow_confirm.html', {
                'book': book,
                'error': 'You have reached the limit of 10 requests per hour. Please try again later.'
            })

        # Limite 2 — apenas 1 pedido do mesmo livro por dia
        one_day_ago = now - timedelta(days=1)
        already_requested_today = BorrowRequest.objects.filter(
            user=request.user,
            book=book,
            request_date__gte=one_day_ago
        ).exists()

        if already_requested_today:
            return render(request, 'borrow_confirm.html', {
                'book': book,
                'error': 'You have already requested this book in the last 24 hours.'
            })

        BorrowRequest.objects.create(user=request.user, book=book)
        return redirect('/my-books/')

    return render(request, 'borrow_confirm.html', {'book': book})

@login_required(login_url='/login/')
def my_books_view(request):
    requests = BorrowRequest.objects.filter(user=request.user).order_by('-request_date')
    return render(request, 'my_books.html', {'requests': requests})


# ─── Admin Panel ─────────────────────────────────────────

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('/login/')
        return view_func(request, *args, **kwargs)
    return wrapper

@admin_required
def admin_panel_view(request):
    pending = BorrowRequest.objects.filter(status='pending').order_by('request_date')  # ← asc em vez de -request_date
    active = BorrowRequest.objects.filter(status='accepted').order_by('due_date')
    return render(request, 'admin_panel.html', {'pending': pending, 'active': active})

@admin_required
def handle_request_view(request, request_id, action):
    borrow = get_object_or_404(BorrowRequest, id=request_id)
    if action == 'accept':
        borrow.status = 'accepted'
        borrow.book.available = False
        borrow.book.save()
        borrow.due_date = date.today() + timedelta(weeks=2)
    elif action == 'reject':
        borrow.status = 'rejected'
    elif action == 'return':
        borrow.status = 'returned'
        borrow.book.available = True
        borrow.book.save()
    borrow.save()
    return redirect('/admin-panel/')

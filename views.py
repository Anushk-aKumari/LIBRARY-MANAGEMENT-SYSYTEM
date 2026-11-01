from django.shortcuts import render, redirect
from .models import Book, Student, Issue, IssuedBook
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Student
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse


# Create your views here.
def home(request):
    books = Book.objects.all()
    return render(request, 'home.html', {'books': books})

@login_required
def add_book(request):
    if request.method == "POST":
        title = request.POST['title']
        author = request.POST['author']
        isbn = request.POST['isbn']
        quantity = request.POST['quantity']
        Book.objects.create(title=title, author=author, isbn=isbn, quantity=quantity)
        return redirect('home')
    return render(request, 'add_book.html')

@login_required
def issue_book(request):
    books = Book.objects.all()
    
    if request.method == 'POST':
        book_id = request.POST.get('book')
        book = Book.objects.get(id=book_id)

        # Check if already issued
        already_issued = IssuedBook.objects.filter(user=request.user, book=book).exists()
        if not already_issued:
            IssuedBook.objects.create(user=request.user, book=book)

        return redirect('my_issued_books')  # or your home page

    return render(request, 'issue_book.html', {'books': books})

@login_required    
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Student.objects.create(user=user, roll_no="Temp", course="Unknown")
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def my_issued_books(request):
    issued_books = IssuedBook.objects.filter(user=request.user)
    return render(request, 'my_issued_books.html', {'issued_books': issued_books})

    
@login_required
def return_book(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id, student__user=request.user)
    if request.method == 'POST':
        issue.return_date = timezone.now().date()
        issue.save()
        # Increase the book quantity since it's returned
        book = issue.book
        book.quantity += 1
        book.save()
        return redirect('my_issued_books')
    return render(request, 'return_book.html', {'issue': issue})

def dashboard(request):
    context = {
        'total_books': Book.objects.count(),
        'total_issues': Issue.objects.count(),
        'total_students': Student.objects.count(),
        'recent_issues': Issue.objects.order_by('-issue_date')[:5],
    }
    return render(request, 'dashboard.html', context)

def search_books(request):
    query = request.GET.get('query', '')
    results = Book.objects.filter(title__icontains=query) if query else []
    return render(request, 'search.html', {'query': query, 'results': results})

@login_required
def student_profile(request):
    student = Student.objects.get(user=request.user)
    issued = Issue.objects.filter(student=student)
    return render(request, 'student_profile.html', {'student': student, 'issued': issued})

def user_logout(request):
    logout(request)
    return redirect('home')

def download_issued_pdf(request):
    issues = Issue.objects.all()
    template = get_template('issued_pdf.html')
    html = template.render({'issues': issues})
    response = HttpResponse(content_type='application/pdf')
    pisa.CreatePDF(html, dest=response)
    return response
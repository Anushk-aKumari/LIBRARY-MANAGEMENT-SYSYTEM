from django.contrib import admin
from .models import Book, Student, Issue, IssuedBook
# Register your models here.
admin.site.register(Book)
admin.site.register(Student)
admin.site.register(Issue)
admin.site.register(IssuedBook)
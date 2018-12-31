from django.contrib import admin
from .models import Teacher, Student, Batch, Subject, User
# Register your models here.

admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Batch)
admin.site.register(Subject)
admin.site.register(User)

#admin.site.register()

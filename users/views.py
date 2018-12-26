# Create your views here.
from django.views.generic import CreateView

from users.models import User
from .forms import TeacherRegisterForm


class TeacherRegisterView(CreateView):
    model = User
    form_class = TeacherRegisterForm
    template_name = 'users/register.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'teacher'
        return super().get_context_data(**kwargs)

# def register(request):
#     if request.method == 'POST':
#         form = TeacherRegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             user.refresh_from_db()  # load the profile instance created by the signal
#             subjects = form.cleaned_data.get('subjects')
#             user.teacher.subjects.set(subjects)
#             batches = form.cleaned_data.get('batches')
#             user.teacher.batches.set(batches)
#             user.save()
#             # raw_password = form.cleaned_data.get('password1')
#             # user = authenticate(username=user.username, password=raw_password)
#             return redirect('add-quiz')
#     else:
#         form = TeacherRegisterForm()
#
#     return render(request, 'users/register.html', {'form': form})

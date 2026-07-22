from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect
from django.db.utils import OperationalError, ProgrammingError


class LoginCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__

        auth_allowed_paths = {
            reverse('login_page'),
            reverse('user_login'),
            reverse('user_logout'),
        }

        try:
            user = request.user
        except (OperationalError, ProgrammingError):
            # Allow login pages even if the database isn't fully initialized
            if (
                request.path in auth_allowed_paths
                or modulename.startswith('django.contrib.auth')
                or request.path.startswith('/admin/')
            ):
                return None
            return redirect(reverse('login_page'))

        if user.is_authenticated:
            if str(user.user_type) == '1':  # Admin/HOD
                if modulename == 'main_app.student_views':
                    return redirect(reverse('admin_home'))

            elif str(user.user_type) == '2':  # Staff
                if modulename in ['main_app.student_views', 'main_app.hod_views']:
                    return redirect(reverse('staff_home'))

            elif str(user.user_type) == '3':  # Student
                if modulename in ['main_app.hod_views', 'main_app.staff_views']:
                    return redirect(reverse('student_home'))

            else:
                return redirect(reverse('login_page'))

        else:
            if (
                request.path == reverse('login_page')
                or request.path == reverse('user_login')
                or request.path == reverse('user_logout')
                or modulename == 'django.contrib.auth.views'
            ):
                return None
            return redirect(reverse('login_page'))
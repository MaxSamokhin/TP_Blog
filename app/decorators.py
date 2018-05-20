from django.contrib.auth.decorators import login_required

# login required with 'continue' arg
def need_login(func):
    return login_required(func, redirect_field_name='continue')
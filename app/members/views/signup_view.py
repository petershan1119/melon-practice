from django.contrib.auth import get_user_model

from django.shortcuts import render, redirect
from django.template.loader import get_template

from members.forms import SignupForm

__all__ = (
    'signup_view',
)

User = get_user_model()

def signup_view(request):
    # if request.method == "POST":
    #     form = UserCreationForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         username = form.cleaned_data.get('username')
    #         raw_password = form.cleaned_data.get('password')
    #         user = authenticate(username=username, password=raw_password)
    #         login(request, user)
    #         return redirect('index')
    # else:
    #     form = UserCreationForm()
    # return render(request, 'members/signup.html', {'form': form})

    # context = {
    #     "errors": [],
    # }

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # password2 = form.cleaned_data['password2']

            is_valid2 = True
            # if User.objects.filter(username=username).exists():
            #     form.add_error('username', '이미 사용되고 있는 아이디입니다.')
            #     is_valid2 = False
            # if password != password2:
            #     form.add_error('password2', '비밀번호와 비밀번호 확인란의 값이 다릅니다.')
            #     is_valid2 = False
            # if is_valid2:
            User.objects.create_user(username=username, password=password)
            return redirect('index')

    else:
        form = SignupForm()

    parent_template = get_template('base.html')
    context = {
        'parent': parent_template,
        'signup_form': form,
    }

    # # 전달받은 데이터에 문제가 있을 경우, context['errors']를 채우고
    # # 해당 내용을 signup.html템플릿에서 출력
    # if request.method == 'POST':
    #     username = request.POST['username']
    #     password = request.POST['password']
    #     password2 = request.POST['password2']
    #
        # is_valid = True
        # if User.objects.filter(username=username).exists():
        #     context['errors'].append('Username already exists')
        #     is_valid = False
        # if password != password2:
        #     context['errors'].append('Password and Password2 is not equal')
        #     is_valid = False
        # if is_valid:
        #     User.objects.create_user(username=username, password=password)
        #     return redirect('index')
    return render(request, 'members/signup.html', context)
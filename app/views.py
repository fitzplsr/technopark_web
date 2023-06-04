from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, reverse
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.forms import model_to_dict
from django.contrib import auth
from .models import Question, QuestionLike, AnswerLike, Answer, Tag, Profile
from .forms import LoginForm, RegistrationForm, SettingsForm, QuestionForm, AnswerForm
from django.http import Http404


def paginate(request, data, count=10):
    paginator = Paginator(data, count)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    last_page = len(paginator.page_range)
    return page_obj, last_page


@require_http_methods(['GET'])
def index(request):
    questions = Question.objects.get_all_ids()
    page_obj, last_page = paginate(request, questions, 10)
    data = Question.objects.get_all(page_obj)
    context = {
        'last_page': last_page,
        'page_obj': page_obj,
        'data': data,
        'ptags': Tag.objects.get_popular(),
        'bmembers': Profile.objects.get_best()
    }
    return render(request, 'all_questions.html', context=context)


@require_http_methods(['GET'])
def tag_questions(request, tag):
    questions = Question.objects.get_by_tag_ids(tag)
    page_obj, last_page = paginate(request, questions, 10)
    data = Question.objects.get_all(page_obj)
    context = {
        'tag': tag,
        'page_obj': page_obj,
        'data': data,
        'last_page': last_page,
        'ptags': Tag.objects.get_popular(),
        'bmembers': Profile.objects.get_best()
    }
    return render(request, 'tag_questions.html', context=context)


@require_http_methods(['GET'])
def hot_questions(request):
    questions = Question.objects.get_hot_ids(30)
    page_obj, last_page = paginate(request, questions, 10)
    data = Question.objects.get_all(page_obj)
    context = {
        'page_obj': page_obj,
        'data': data,
        'last_page': last_page,
        'ptags': Tag.objects.get_popular(),
        'bmembers': Profile.objects.get_best()
    }
    return render(request, 'hot_questions.html', context=context)


@require_http_methods(['GET'])
def best_questions(request):
    questions = Question.objects.get_best_ids(30)
    page_obj, last_page = paginate(request, questions, 10)
    data = Question.objects.get_all(page_obj)
    context = {
        'page_obj': page_obj,
        'data': data,
        'last_page': last_page,
        'ptags': Tag.objects.get_popular(),
        'bmembers': Profile.objects.get_best()
    }
    return render(request, 'best_questions.html', context=context)


@require_http_methods(['GET'])
def new_questions(request):
    questions = Question.objects.get_new_ids()
    page_obj, last_page = paginate(request, questions, 10)
    data = Question.objects.get_all(page_obj)
    context = {
        'page_obj': page_obj,
        'data': data,
        'last_page': last_page,
        'ptags': Tag.objects.get_popular(),
        'bmembers': Profile.objects.get_best()
    }
    return render(request, 'new_questions.html', context=context)


@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.method == 'GET':
        user_form = RegistrationForm()
    if request.method == 'POST':
        user_form = RegistrationForm(request.POST, request.FILES)
        if user_form.is_valid():
            user = user_form.save()
            if user:
                login_form = LoginForm(request.POST)
                login_form.is_valid()
                user_auth = auth.authenticate(request=request, **login_form.cleaned_data)
                auth.login(request, user_auth)
                return redirect(reverse('index'))
    context = {
        'ptags': Tag.objects.get_popular(),
        'bmembers': Profile.objects.get_best(),
        'form': user_form
    }
    return render(request, 'signup.html', context=context)


@require_http_methods(['GET', 'POST'])
def log_in(request):
    cont = request.GET.get('continue')
    if request.method == 'GET':
        login_form = LoginForm()
    else:
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = auth.authenticate(request=request, **login_form.cleaned_data)
            if user:
                auth.login(request, user)
                cont = request.POST.get("continue", None)
                return redirect(cont if cont and cont != "None" else reverse('index'))

    context = {
        'ptags': Tag.objects.get_popular(),
        'bmembers': Profile.objects.get_best(),
        'form': login_form,
        'continue': cont
    }
    return render(request, 'login.html', context=context)


@login_required(login_url="login", redirect_field_name="continue")
@require_http_methods(['POST'])
def logout(request):
    auth.logout(request)
    cont = request.POST.get("continue")
    return redirect(cont if cont and cont != "None" else reverse('index'))


@login_required(login_url="login", redirect_field_name="continue")
@require_http_methods(['GET', 'POST'])
def settings(request):
    user = get_object_or_404(User, id=request.user.id)
    user_id = user.id
    if request.method == "GET":
        initial_data = model_to_dict(user)
        nickname = user.profile.nickname
        avatar = user.profile.avatar
        initial_data["nickname"] = nickname
        initial_data["avatar"] = avatar
        form = SettingsForm(initial=initial_data)
    if request.method == "POST":
        form = SettingsForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            user = get_object_or_404(User, id=user_id)
            data = {
                'username': user.username,
                'password': user.password
            }
            login_form = LoginForm(data)
            login_form.is_valid()
            user_auth = auth.authenticate(request=request, **login_form.cleaned_data)
            auth.login(request, user_auth)

    context = {
        'ptags': Tag.objects.get_popular(),
        'bmembers': Profile.objects.get_best(),
        'form': form
    }
    return render(request, 'settings.html', context=context)


@login_required(login_url="login", redirect_field_name="continue")
@require_http_methods(['GET', 'POST'])
def ask(request):
    if request.method == 'GET':
        question_form = QuestionForm()
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            q_id = question_form.save(request.user.profile)
            return redirect('question', q_id)
    context = {
        'ptags': Tag.objects.get_popular(),
        'bmembers': Profile.objects.get_best(),
        'form': question_form
    }
    return render(request, 'ask.html', context=context)


def custom_paginate(obj, data, count=10):
    page = obj // count + 1
    paginator = Paginator(data, count)
    page_obj = paginator.get_page(page)
    last_page = len(paginator.page_range)
    return page_obj, last_page


@require_http_methods(['GET', 'POST'])
def question(request, question_id: int):
    question_item = get_object_or_404(Question, pk=question_id)

    if request.method == 'POST':
        if not hasattr(request.user, 'profile'):
            return redirect('login')
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            ans_id = answer_form.save(request.user.profile, question_item)
            answers_ids = Answer.objects.get_all_ids(question_id)
            ind = list(answers_ids).index(ans_id)
            page_obj, last_page = custom_paginate(ind, answers_ids, 5)
            data = Answer.objects.get_all(page_obj)
        answer_form = AnswerForm()
    else:
        answer_form = AnswerForm()
        answers = Answer.objects.get_all_ids(question_id)
        page_obj, last_page = paginate(request, answers, 5)
        data = Answer.objects.get_all(page_obj)

    is_author = False
    if question_item.author.user == request.user:
        is_author = True
    context = {
        'question': Question.objects.get_obj(question_item),
        'page_obj': page_obj,
        'data': data,
        'last_page': last_page,
        'ptags': Tag.objects.get_popular(),
        'bmembers': Profile.objects.get_best(),
        'form': answer_form,
        'author': is_author
    }
    return render(request, 'question.html', context=context)


@login_required(login_url="login", redirect_field_name="continue")
@require_http_methods(['POST'])
def vote(request):
    id = request.POST.get("id")
    vote = request.POST.get("vote")
    type = request.POST.get("type")
    if not (id and vote and type):
        raise Http404
    if vote not in ["like", "dislike"]:
        raise Http404
    if not hasattr(request.user, 'profile'):
        raise Http404
    if type == "question":
        question_item = get_object_or_404(Question, pk=id)
        QuestionLike.objects.create_or_change_like(question_item, request.user.profile, vote)
        likes = Question.objects.get_likes(id)
    if type == 'answer':
        answer_item = get_object_or_404(Answer, pk=id)
        AnswerLike.objects.create_or_change_like(answer_item, request.user.profile, vote)
        likes = Answer.objects.get_likes(id)
    return JsonResponse({
        'likes': likes
    })


@login_required(login_url="login", redirect_field_name="continue")
@require_http_methods(['POST'])
def correct(request):
    id = request.POST.get("id")
    correct = request.POST.get("correct")
    enum_states = {"true": True, "false": False}
    if not (id and correct):
        raise Http404
    if not hasattr(request.user, 'profile'):
        raise Http404
    if correct not in enum_states.keys():
        raise Http404
    answer = get_object_or_404(Answer, pk=id)
    if answer.question.author != request.user.profile:
        raise Http404
    answer.is_correct = enum_states[correct]
    answer.save()
    return JsonResponse({
        'correct': correct
    })

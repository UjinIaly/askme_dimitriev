from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.core.paginator import Paginator
import random
from pprint import pformat

from app.models import Question, Answer, Profile, Mark
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from django.views.decorators.http import require_POST
from django.http import JsonResponse

from app.forms import *


def paginate(request, object_list, per_page=5):
    paginator = Paginator(object_list, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def paginate_new(request, paginator):
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def new_questions(request):
    # sample how to use data in session storage
    print(f'HELLO: {request.session.get("hello")}')

    new_questions = Question.objects.new_questions()
    question_pages = paginate(request, new_questions)

    return render(request, 'index.html', {
        'page_obj': question_pages,
    })


def hot_questions(request):
    hot_questions = Question.objects.best_questions()
    question_pages = paginate(request, hot_questions)

    return render(request, 'hot_questions.html', {
        'page_obj': question_pages,
    })


def tag_questions(request, tag):
    questions_for_this_tag = Question.objects.questions_by_tag(tag)
    page_obj = paginate(request, questions_for_this_tag)

    return render(request, 'tag_questions.html', {
        'page_obj': page_obj,
        'tag': tag,
    })


def question_answers(request, question_id):
    question = Question.objects.question_by_id(question_id)
    question_answers = Answer.objects.question_answers(question_id)
    OBJECTS_PER_PAGE = 3
    paginator = Paginator(question_answers, OBJECTS_PER_PAGE)
    page_obj = paginate_new(request, paginator)

    if request.method == 'GET':
        form = AnswerForm()
    else:
        form = AnswerForm(data=request.POST, user=request.user, question_pk=question_id)
        if form.is_valid():
            if request.user.is_authenticated:
                answer = form.save()

                # redirect logic
                if paginator.count % OBJECTS_PER_PAGE == 0:
                    page_number_for_ref = paginator.num_pages + 1
                else:
                    page_number_for_ref = paginator.num_pages
                return redirect(reverse('question_answers', kwargs={
                    'question_id': question.pk}) + f'?page={page_number_for_ref}#{answer.id}')
            else:
                path = reverse('login') + f'?next=/question/{question_id}&anchor=scroll-to-form'
                return redirect(path)

    ctx = {
        'page_obj': page_obj,
        'question': question,
        'tags': question.tags.get_all_tags(),
        'form': form}
    return render(request, 'answers.html', ctx)


@login_required
def ask_question(request):
    if request.method == 'GET':
        form = AskForm()
    else:
        form = AskForm(data=request.POST, user=request.user)
        if form.is_valid():
            question = form.save(tags=form.cleaned_data['tags'])
            return redirect(reverse('question_answers', kwargs={'question_id': question.pk}))

    ctx = {'form': form}
    return render(request, 'ask_question.html', ctx)


def login(request):
    redirect_to = request.GET.get('next', '/')
    anchor = request.GET.get('anchor')
    if anchor is not None:
        redirect_to += '#' + anchor
    error_message = None
    if request.method == 'GET':
        form = LoginForm()
    else:
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user is not None:
                # sample how to store data in sessions
                request.session['hello'] = 'world'

                auth.login(request, user)
                return redirect(redirect_to)
            else:
                error_message = "Incorrect login or password"

    ctx = {'form': form, 'redirect_to': redirect_to, 'error_message': error_message}
    return render(request, 'login.html', ctx)


def logout(request):
    auth.logout(request)
    redirect_path = request.GET.get('next', '/')
    return redirect(redirect_path)


def sign_up(request):
    if request.method == 'GET':
        form_user = CreateUserForm()
        form_profile = CreateProfileForm()
    else:
        pdata = request.POST
        user_data = {'username': pdata.get('username'), 'email': pdata.get('email'), 'password': pdata.get('password'),
                     'repeat_password': pdata.get('repeat_password')}
        form_user = CreateUserForm(data=user_data)
        form_profile = CreateProfileForm(data={'image': pdata.get('image')}, files=request.FILES)
        if form_profile.is_valid() and form_user.is_valid():
            data = form_user.cleaned_data
            user = User.objects.create_user(username=data.get('username'), email=data.get('email'),
                                            password=data.get('password'))
            # add validation if image is none
            profile = Profile.objects.create(
                user=user,
                user_name=data.get('username'),
                email=data.get('email'),
                image=request.FILES.get('image', None))
            auth.login(request, user)
            return redirect("/")

    ctx = {'form_profile': form_profile, 'form_user': form_user}
    return render(request, 'login.html', ctx)


@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'GET':
        form = EditProfileForm(
            data={'user_name': user.profile.user_name, 'email': user.profile.email, 'image': user.profile.image})
    else:
        form = EditProfileForm(
            data=request.POST,
            files=request.FILES,
            instance=request.user.profile)
        if form.is_valid():
            data = form.cleaned_data
            user.profile.user_name = data.get('user_name')
            user.profile.email = data.get('email')
            user.profile.image = request.FILES.get('image', None)
            user.username = data.get('user_name')
            user.email = data.get('email')
            user.profile.save()
            user.save()
    ctx = {'form': form}

    return render(request, 'settings.html', ctx)


# обработка лайков/дизлайков
@require_POST
@login_required
def vote(request):
    data = request.POST
    print(f'HERE: {pformat(data)}')

    res = Mark.objects.set_mark(
        user_id=request.user.profile.id,
        content_object_type=data.get('object_type'),
        content_object_id=data.get('object_id'),
        mark_type=data.get('action'))
    print(res)

    # return new rating for js to update rating state on page
    return JsonResponse({'object_rating': res, 'action': data.get('action')})


# обработка кнопки выставления правильного ответа
@require_POST
@login_required
def correct_answer(request):
    data = request.POST
    print(f'HERE: {pformat(data)}')

    if Question.objects.get(pk=data['question_id']).author.user == request.user:
        answer = Answer.objects.get(pk=data['answer_id'])
        answer.is_correct = not answer.is_correct
        answer.save()
        print('answer correct status changed')

    return JsonResponse({})

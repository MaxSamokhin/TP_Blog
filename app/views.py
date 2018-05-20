from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.generic import TemplateView
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from cgi import parse_qsl, escape
from django.template import RequestContext, loader
from django.core import validators
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib import auth
from django.utils.decorators import method_decorator
from django.views import View

from app.models import *
from app.forms import LoginForm, SignupForm, ProfileEditForm, AskForm, AnswerForm
from app.decorators import need_login
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from app import helpers
import json


def getQuestionPageLikes(question_, answers, User):
    likes = []
    dislikes = []
    for ans in answers:
        try:
            query = AnswerLike.objects.get(answer=ans, author=User)
        except:
            query = None
        if query is not None:
            if query.value == 1:
                likes.append(ans.id)
            else:
                dislikes.append(ans.id)
    try:
        query = QuestionLike.objects.get(question=question_, author=User)
        if query.value == 1:
            islike = 1
        else:
            islike = -1
    except:
        islike = 0
    result = [likes, dislikes, islike]
    return result


def getQuestionListLikes(questions, User):
    likes = []
    dislikes = []

    for question in questions:
        try:
            query = QuestionLike.objects.get(question=question, author=User)
        except:
            query = None

        if query is not None:
            if query.value == 1:
                likes.append(question.id)
            else:
                dislikes.append(question.id)
    result = [likes, dislikes]
    return result


@csrf_exempt
def getpost(request):
    result = ['<h1>Django</h1>']
    result.append('Post:')
    result.append('<form method="post">')
    result.append('<input type="text" name = "test">')
    result.append('<input type="submit" value="Send">')
    result.append('</form>')

    if request.method == 'POST':
        result.append('<h1>Post data:</h1>')
        result.append(request.POST.get('test'))

    if request.method == 'GET':
        if request.GET:
            result.append('<h1>Get data:</h1>')
            for key, value in request.GET.items():
                list = request.GET.getlist(key)
                for elem in list:
                    keyvalue = key + " = " + elem
                    result.append(keyvalue)

    return HttpResponse('<br>'.join(result))


# @need_login
def logout(request):
    redirect = request.GET.get('continue', '/')
    auth.logout(request)
    return HttpResponseRedirect(redirect)


@login_required
def ask(request):
    tags = Tag.objects.count_popular()
    if request.method == "POST":
        form = AskForm(request.POST)
        if form.is_valid():
            q = form.save(request.user)
            return HttpResponseRedirect(reverse('question', kwargs={'question_id': q.id}))
    else:
        form = AskForm()
    return render(request, 'ask.html', {'tags': tags, 'form': form})


def login(request):
    tags = Tag.objects.count_popular()
    redirect = request.GET.get('continue', '/')
    if request.user.is_authenticated():
        return HttpResponseRedirect(redirect)

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            auth.login(request, form.cleaned_data['user'])
            return HttpResponseRedirect(redirect)
    else:
        form = LoginForm()

    return render(request, 'login.html', {
        'form': form,
        'tags': tags,
    })


def signup(request):
    tags = Tag.objects.count_popular()
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    form = SignupForm(request.POST, request.FILES)
    if request.method == "POST":

        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return HttpResponseRedirect('/')
    else:
        form = SignupForm()

    return render(request, 'register.html', {
        'form': form,
        'tags': tags,
    })


def get_page(query, request, number_of_list):
    paginator = Paginator(query, number_of_list)
    page = request.GET.get('page')
    try:
        curr_page = paginator.page(page)
    except PageNotAnInteger:
        curr_page = paginator.page(1)
    except EmptyPage:
        curr_page = paginator.page(paginator.num_pages)
    return curr_page


def base(request):
    questions_query = Question.objects.list_new()
    question = get_page(questions_query, request, 3)

    likes = getQuestionListLikes(question, request.user)

    tags = Tag.objects.count_popular()
    return render(request, 'index.html', {'questions': question,
                                          'tags': tags,
                                          'likes': likes[0],
                                          'dislikes': likes[1]
                                          })


def hot(request):
    questions_query = Question.objects.list_hot()
    question = get_page(questions_query, request, 3)

    likes = getQuestionListLikes(question, request.user)

    tags = Tag.objects.count_popular()
    return render(request, 'hot.html', {'questions': question,
                                        'tags': tags,
                                        'likes':likes[0],
                                        'dislikes':likes[1]
                                        })


def question(request, question_id):
    try:
        question = Question.objects.get_single(int(question_id))
    except Question.DoesNotExist:
        raise Http404()

    # answers = question.answer_set.all()

    # question_ = get_object_or_404(Question, pk=question_id)
    answers = question.answer_set.all()

    likes = getQuestionPageLikes(question, answers, request.user)

    page = get_page(answers, request, 3)
    tags = Tag.objects.count_popular()
    form = AnswerForm()

    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            ans = form.save(question, request.user)
            return HttpResponseRedirect(
                '%s?page=%d' % (reverse('question', kwargs={'question_id': question.id}), ans.id))
        else:
            form = AnswerForm()
    return render(request, 'question.html', {'question': question,
                                             'answers': page,
                                             'tags': tags,
                                             'form': form,
                                             'likes': likes[0],
                                             'dislikes': likes[1],
                                             'islike': likes[2]
                                             })


class settings(View):
    @method_decorator(need_login)
    def get(self, request):
        tags = Tag.objects.count_popular()
        u = model_to_dict(request.user)
        form = ProfileEditForm(u)

        return render(request, 'settings.html', {
            'form': form,
            'u': request.user,
            'tags': tags,
        })

    @method_decorator(need_login)
    def post(self, request):
        form = ProfileEditForm(request.POST, request.FILES)
        tags = Tag.objects.count_popular()
        if form.is_valid():
            form.save(request.user)
            return HttpResponseRedirect(reverse('settings'))

        return render(request, 'settings.html', {
            'form': form,
            'u': request.user,
            'tags': tags,
        })


def tag(request, tag):
    context = RequestContext(request, {'tag': tag})

    try:
        tag = Tag.objects.get_by_title(tag)
    except Tag.DoesNotExist:
        raise Http404()

    tags = Tag.objects.count_popular()
    questions_query = Question.objects.list_tag(tag)
    questions = get_page(questions_query, request, 4)

    likes = getQuestionListLikes(questions, request.user)

    return render(request, 'tag.html', {'questions': questions,
                                        "context": context,
                                        'tags': tags,
                                        'likes': likes[0],
                                        'dislikes': likes[1]
                                        })


@login_required
def ajax_question_like(request, id):
    if request.method == "POST":
        try:
            q = Question.objects.get(pk=id)
            likesid = '#qRating' + str(q.id)
            value = int(request.POST.get('value'))
            QuestionLike.objects.add_or_update(author=request.user, question=q, value=value)

            # content_dis = "<span class =\"glyphicon glyphicon-menu-down\" style=\"color: black;\"> </span></a>"
            if value == 1:
                # like = AnswerLike.objects.add_or_update(user, answer, 1)
                content_dis = "<span class=\"page-like-img dislikebtn\"/>"
                content_like = "<span class=\"page-like-img islikebtn\"/>"
            elif value == -1:
                # like = AnswerLike.objects.add_or_update(user, answer, -1)
                content_dis = "<span class=\"page-like-img isdislikebtn\"/>"
                content_like = "<span class=\"page-like-img likebtn\"/>"


            content = {'like': content_like, 'dislike': content_dis}

            return helpers.HttpResponseAjax(content, likesid=likesid, likes=q.likes, qid=id, )
        except QuestionLike.AlreadyLike as e1:
            q = Question.objects.get(pk=id)
            id = '#error' + str(q.id)
            return helpers.HttpResponseAjaxError(code='already_like',
                                                 id=id,
                                                 identificate='question',
                                                 message=e1.message)
    raise Http404()

#sudo vim /etc/nginx/nginx.conf

# @login_required
# def ajax_answer_like(request, id):
#     if request.method == "POST":
#         try:
#             ans = Answer.objects.get(pk=id)
#             likesid = '#aRating' + str(ans.id)
#             value = int(request.POST.get('value'))
#             AnswerLike.objects.add(author=request.user, answer=ans, value=value)
#             return helpers.HttpResponseAjax(likesid=likesid, likes=ans.likes)
#         except AnswerLike.AlreadyLike as e1:
#             return helpers.HttpResponseAjaxError(code='already_like',
#                                                  message=e1.message)
#     raise Http404()


@login_required
def ajax_answer_like(request, id):
    if request.method == "POST":
        try:
            ans = Answer.objects.get(pk=id)
            likesid = '#aRating' + str(ans.id)
            value = int(request.POST.get('value'))
            AnswerLike.objects.add_or_update(author=request.user, answer=ans, value=value)

            if value == 1:
                content_dis = "<span class=\"page-like-img dislikebtn\"/>"
                content_like = "<span class=\"page-like-img islikebtn\"/>"
            elif value == -1:
                content_dis = "<span class=\"page-like-img isdislikebtn\"/>"
                content_like = "<span class=\"page-like-img likebtn\"/>"

            content = {'like': content_like, 'dislike': content_dis}

            return helpers.HttpResponseAjax(content, likesid=likesid, likes=ans.likes, aid=id)
        except AnswerLike.AlreadyLike as e1:
            ans = Answer.objects.get(pk=id)
            id = '#error' + str(ans.id)
            return helpers.HttpResponseAjaxError(code='already_like',
                                                 id=id,
                                                 identificate='answer',
                                                 message=e1.message)
    raise Http404()

@login_required
def ajax_answer_correct(request, id):
    if request.method == "POST":
        user = request.user
        answer = Answer.objects.get(pk=id)

        if answer.question.author == user:
            answer.correct = True
            answer.save()
            answer.question.save()
            content = {
                'new': "<div class=\"label label-default\" style=\"width:120px; height: 20px; margin: 4px 4px;text-align: center;background-color: #5cb85c;\">correct answer!</div>"}
            response = {'result': 'true', 'content': content, 'aid': id}
        else:
            response = {'result': 'false'}

        return HttpResponse(json.dumps(response), content_type='application/json')
    raise Http404()

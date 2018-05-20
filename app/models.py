from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count, Sum
from django.core.urlresolvers import reverse
from app import helpers
import datetime

from django.core.cache import cache


class ProfileManager(models.Manager):
    def get_name(self, user_name):
        return self.filter(user__username=user_name)

    def get_username(self, id):
        return self.filter(user__id=id)


class TagManager(models.Manager):
    def with_question_count(self):
        return self.annotate(questions_count=Count('question'))

    def order_by_question_count(self):
        return self.with_question_count().order_by('-questions_count')

    def count_popular(self):
        return self.order_by_question_count().all()[:20]

    def get_by_title(self, title):
        return self.get(title=title)

from django.db.models import Avg
from django.db.models import Max

class QuestionLikeManager(models.Manager):

    def has_question(self, question):
        return self.filter(question=question)

    def sum_for_question(self, question):
        return self.has_question(question).aggregate(sum=Sum('value'))['sum']


    def get_value(self, question):
        return self.has_question(question).aggregate(Max('value'))

    def add(self, author, question, value):
        try:
            obj = self.get(
                author=author,
                question=question
            )
        except QuestionLike.DoesNotExist:
            obj = self.create(
                author=author,
                question=question,
                value=value
            )
            question.likes = self.sum_for_question(question)
            question.save()
        else:
            raise QuestionLike.AlreadyLike

    def add_or_update(self, author, question, value):
        obj, new = self.update_or_create(
            author=author,
            question=question,
            defaults={'value': value}
        )

        question.likes = self.sum_for_question(question)
        question.save()
        return new


class QuestionManager(models.Manager):
    def list_new(self):
        return self.order_by('-date')

    def list_hot(self):
        return self.order_by('-likes')

    def list_tag(self, tag):
        return self.filter(tags=tag)

    def get_single(self, id):
        return self.get(pk=id)


# class AnswerQuerySet(models.QuerySet):
#     def with_author(self):
#         return self.select_related('author').select_related('author__profile')
#
#     def with_question(self):
#         return self.select_related('question')
#
#     def order_by_popularity(self):
#         return self.order_by('-likes')


class AnswerLikeManager(models.Manager):
    def has_answer(self, answer):
        return self.filter(answer=answer)

    def sum_for_answer(self, answer):
        return self.has_answer(answer).aggregate(sum=Sum('value'))['sum']

    def add(self, author, answer, value):
        try:
            obj = self.get(
                author=author,
                answer=answer
            )
        except AnswerLike.DoesNotExist:
            obj = self.create(
                author=author,
                answer=answer,
                value=value
            )
            answer.likes = self.sum_for_answer(answer)
            answer.save()
        else:
            raise AnswerLike.AlreadyLike

    def add_or_update(self, author, answer, value):
        obj, new = self.update_or_create(
            author=author,
            answer=answer,
            defaults={'value': value}
        )

        answer.likes = self.sum_for_answer(answer)
        answer.save()
        return new


class Profile(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField(upload_to='avatars')

    objects = ProfileManager()

    def __str__(self):
        return self.user


class Tag(models.Model):
    objects = TagManager()
    title = models.CharField(max_length=30)


class Question(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    author = models.ForeignKey(User)
    date = models.DateTimeField(default=timezone.now)
    tags = models.ManyToManyField(Tag)
    likes = models.IntegerField(default=0)
    isVote = models.BooleanField(default = True)

    objects = QuestionManager()

    def get_answer_on_id(self, id):
        try:
            ans = Answer.objects.get(pk=id)
        except Answer.DoesNotExist:
            ans = None
        return ans

    def __str__(self):
        return self.text


class QuestionLike(models.Model):
    class AlreadyLike(Exception):
        def __init__(self):
            super(QuestionLike.AlreadyLike, self).__init__('You voted for this question')

    UP = 1
    DOWN = -1

    question = models.ForeignKey(Question)
    author = models.ForeignKey(User)
    value = models.SmallIntegerField(default=1)

    objects = QuestionLikeManager()


class Answer(models.Model):
    text = models.TextField()
    question = models.ForeignKey(Question)
    author = models.ForeignKey(User)
    date = models.DateTimeField(default=timezone.now)
    correct = models.BooleanField(default=False)
    likes = models.IntegerField(default=0)


class AnswerLike(models.Model):
    class AlreadyLike(Exception):
        def __init__(self):
            super(AnswerLike.AlreadyLike, self).__init__('You voted for this answer')

    UP = 1
    DOWN = -1

    answer = models.ForeignKey(Answer)
    author = models.ForeignKey(User)
    value = models.SmallIntegerField(default=0)

    objects = AnswerLikeManager()
    def __str__(self):
        return self.rating


class ProjectCache:

    POPULAR_TAGS = 'tags_popular'
    @classmethod
    def get_popular_tags(cls):
        return cache.get(ProjectCache.POPULAR_TAGS, [])

    @classmethod
    def update_popular_tags(cls):
        popular = Tag.objects.count_popular()
        cache.set(ProjectCache.POPULAR_TAGS, popular, 60 * 60 * 24)


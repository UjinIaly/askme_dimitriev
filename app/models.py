from random import random, randint

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from coolname import generate_slug
from django.dispatch import receiver
from django.db.models.signals import post_save

TITLE_LENGTH = 1024
CONTENT_LENGTH = 65536
TAG_LENGTH = 128

NUMBER_OF_USERS = 2
NUMBER_OF_QUESTIONS = 200
NUMBER_OF_ANSWERS = 2000
NUMBER_OF_TAGS = 20

LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque tempor id risus vel facilisis. Nunc " \
              "commodo non orci a mattis. Fusce nulla erat, mollis non ipsum ac, finibus accumsan ligula. Nam et " \
              "nulla eget neque consequat imperdiet. Ut pharetra odio aliquam lacinia lacinia. Curabitur non dui sed " \
              "est finibus tempor nec vitae dui. Donec fermentum leo arcu, nec finibus mi pretium nec. Proin finibus " \
              "semper purus vel convallis. Quisque eget fermentum dui. Morbi sollicitudin sit amet odio eget " \
              "dignissim. Curabitur nec nisi hendrerit neque rhoncus egestas at quis tellus. Pellentesque quam sem, " \
              "elementum eu sapien a, iaculis cursus lectus. Etiam ut nulla vel est ultricies fringilla. Maecenas " \
              "pretium ultricies nibh, efficitur cursus ante volutpat sit amet. "


# Create your models here.
class TagManager(models.Manager):
    pass


class Tag(models.Model):
    tag = models.CharField(max_length=TAG_LENGTH, blank=True)
    objects = TagManager()


class ProfileManager(models.Manager):
    pass


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='images', null=True)
    bio = models.TextField(null=True)
    questions = models.ForeignKey('Question', on_delete=models.CASCADE)

    objects = ProfileManager()


class AnswerManager(models.Manager):
    pass


class Answer(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    user_rating = models.IntegerField(null=True)

    objects = AnswerManager()


class QuestionManager(models.Manager):
    def get_tags(self, question_id: int):
        return Tag.objects.filter(question_id=question_id).all().values()

    def get_hot(self):
        return self.filter(hot=True)

    def get_popular(self):
        return self.filter(number_of_answers=10)

    def get_question_by_id(self, question_id):
        return self.filter(id=question_id)

    def get_questions_by_user_id(self, user_id):
        return Profile.objects.filter(id=user_id)

    def get_questionos_by_tag(self, tag: str):
        return self.get_tag

    def get_questions_tags(self, question_id: int):
        return Tag.objects.filter(question_id=question_id)

    def get_question_answers(self, question_id: int):
        return Answer.objects.filter(question_id=question_id)


class Question(models.Model):
    title = models.CharField(max_length=TITLE_LENGTH, blank=True)
    content = models.CharField(max_length=CONTENT_LENGTH, blank=True)
    tags = models.ForeignKey(Tag, on_delete=models.DO_NOTHING)
    hot = models.BooleanField()
    published_date = models.DateTimeField()
    number_of_answers = models.IntegerField(null=True)

    # user_rating = models.IntegerField(len(list(Answer.question.id=id))

    objects = QuestionManager()

    def __str__(self):
        return self.title



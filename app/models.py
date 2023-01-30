from django.db import models
import sys
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation


class ProfileManager(models.Manager):
    def get_all_users(self):
        return self.all()

    def get_best_users(self):
        return self.all()[:15]

    def get_user_vote(self, user, obj_type, obj_id):
        type = ContentType.objects.get(app_label='app', model=obj_type)  # model='question'

        # get will throw doesNotExist
        return self.get(user=user).mark_set.filter(object_id=obj_id, content_type=type).first()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=256, verbose_name='Имя в системе')
    email = models.EmailField(verbose_name='E-mail', default='email@mail.com', blank=True)
    image = models.ImageField(
        upload_to='avatar/%Y/%m/%d/',
        default='no_avatar.jpg',
        blank=True,
        verbose_name='Аватарка'
    )

    objects = ProfileManager()

    def __str__(self):
        return self.user_name

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class MarkManager(models.Manager):
    def count_rating(self):
        return self.filter(mark_type=Mark.MarkType.LIKE).count() - self.filter(mark_type=Mark.MarkType.DISLIKE).count()

    def set_mark(self, user_id, content_object_type, content_object_id, mark_type):
        if mark_type == 'dislike':
            mark_type_enum = Mark.MarkType.DISLIKE
        else:
            mark_type_enum = Mark.MarkType.LIKE

        content_type = ContentType.objects.get(app_label='app', model=content_object_type)
        obj, created = Mark.objects.get_or_create(
            user_id=user_id,
            content_type=content_type,
            object_id=content_object_id
        )

        if content_object_type == 'question':
            content_object = Question.objects.get(pk=content_object_id)
        elif content_object_type == 'answer':
            content_object = Answer.objects.get(pk=content_object_id)

        if created:
            obj.mark_type = mark_type_enum
            obj.save()

            if mark_type_enum == Mark.MarkType.LIKE:
                content_object.rating += 1
            else:
                content_object.rating -= 1
            content_object.save()
        else:

            if obj.mark_type != mark_type_enum:
                obj.mark_type = mark_type_enum
                obj.save()

                if mark_type_enum == Mark.MarkType.LIKE:
                    content_object.rating += 2
                else:
                    content_object.rating -= 2
                content_object.save()
            else:
                print("TRYING TO ADD SAME MARK")
                return None

        return content_object.rating


class Mark(models.Model):
    class MarkType(models.TextChoices):
        LIKE = 'LIKE', _('Like')
        DISLIKE = 'DIS', _('Dislike')

    mark_type = models.CharField(max_length=4, choices=MarkType.choices, default=MarkType.LIKE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    user = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name='Автор')

    objects = MarkManager()

    def __str__(self):
        return self.mark_type

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        unique_together = ('content_type', 'object_id', 'user',)


class QuestionManager(models.Manager):
    def new_questions(self):
        return self.all().prefetch_related('author').order_by('-date_create', '-rating')

    def best_questions(self):
        return self.all().prefetch_related('author').order_by('-rating', '-date_create')

    def questions_by_tag(self, tag):
        return self.filter(tags__name=tag)

    def question_by_id(self, question_id):
        return self.get(pk=question_id)


class Question(models.Model):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    author = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name='Автор')
    tags = models.ManyToManyField('Tag', verbose_name='Тэги', blank=True)

    rating = models.IntegerField(default=0, blank=True, verbose_name='Рейтинг')
    marks = GenericRelation(Mark)

    objects = QuestionManager()

    def __str__(self):
        return self.title

    def count_answers(self):
        return Answer.objects.question_answers(self.pk).count()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class AnswerManager(models.Manager):
    def question_answers(self, question_id):
        return self.filter(question__id=question_id).order_by('-rating', 'date_create')


class Answer(models.Model):
    text = models.TextField(verbose_name='Текст')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    is_correct = models.BooleanField(default=False, verbose_name='Правильность')
    question = models.ForeignKey('Question', on_delete=models.CASCADE, verbose_name='Вопрос')
    author = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name='Автор')

    rating = models.IntegerField(default=0, blank=True, verbose_name='Рейтинг')
    marks = GenericRelation(Mark)

    objects = AnswerManager()

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'


class TagManager(models.Manager):
    def get_all_tags(self):
        return self.all()

    def get_best_tags(self):
        return self.all()[:25]


class Tag(models.Model):
    name = models.CharField(max_length=256, unique=True, verbose_name='Название тэга')

    objects = TagManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

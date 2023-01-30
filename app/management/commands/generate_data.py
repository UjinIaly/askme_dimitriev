from django.core.management.base import BaseCommand, CommandError
from app.models import *
from django.contrib.auth.models import User
from random import choice
from faker import Faker
from django.db import IntegrityError

f = Faker()


class Command(BaseCommand):
    help = 'Generates Data'

    def add_arguments(self, parser):
        # parser.add_argument(
        # '--db_size',
        # choices=['test', 'small', 'medium', 'large', 'max'],
        # help='choose how many data to generate'
        # )
        # parser.add_argument('--add_users', type=int, help='users creation')
        # parser.add_argument('--add_tags', type=int, help='tags creation')
        # parser.add_argument('--add_questions', type=int, help='questions creation')
        # parser.add_argument('--add_answers', type=int, help='answers creation')
        # parser.add_argument('--add_marks', type=int, help='marks creation')
        parser.add_argument('--fill_db', type=int, help='filling')

    def handle(self, *args, **options):
        # opt = options['db_size']
        #    if (opt):
        #        part = {
        #            'test': 0.0001,
        #            'small': 0.0005,
        #            'medium': 0.001,
        #            'large': 0.01,
        #            'max': 1,
        #        }.get(opt, 0.00005)
        #        self.generate_database(part)
        #
        #    if (options['add_users']):
        #        self.generate_users(options['add_users'])
        #    if (options['add_tags']):
        #        self.generate_tags(options['add_tags'])
        #    if (options['add_questions']):
        #        self.generate_questions(options['add_questions'])
        #    if (options['add_answers']):
        #        self.fill_questions_with_answers(options['add_answers'], [])
        # if (options['add_marks']):
        #     self.generate_marks(options['add_marks'])
        if options['fill_db']:
            self.generate_database(options['fill_db'])

    def generate_database(self, ratio):
        MIN_COUNT_USER = 10000

        self.generate_users(ratio)
        self.generate_tags(ratio)
        self.generate_questions(ratio)
        # self.generate_marks(ratio)
        # self.fill_questions_with_answers(ratio * 100)

    def generate_marks(self, mark_object):
        users_ids = User.objects.values_list(
            'id', flat=True
        )

        if f.random_int(min=1, max=10) > 3:
            mark_type = Mark.MarkType.LIKE
        else:
            mark_type = Mark.MarkType.DISLIKE

        try:
            mark = Mark.objects.create(
                mark_type=mark_type,
                content_object=mark_object,
                user_id=choice(users_ids)
            )
            if mark_type == Mark.MarkType.LIKE:
                mark_object.rating += 1
            else:
                mark_object.rating -= 1
            mark_object.save()
        except IntegrityError:
            a = 1

    def generate_users(self, cnt):
        for i in range(cnt):
            num_ava = f.random_int(min=1, max=17)

            name = f.name()
            email = f.email()
            try:
                user = User.objects.create_user(username=name, email=email, password='xxx')
            except IntegrityError:
                name = f.name() + ' ' + f.name()
                user = User.objects.create_user(username=name, email=email, password='xxx')

            profile = Profile.objects.create(
                user=user,
                user_name=name,
                email=email,
                image=f'{num_ava}.jpg'
            )

    def generate_tags(self, cnt):
        for i in range(cnt):
            try:
                Tag.objects.create(
                    name=f.word()
                )
            except IntegrityError:
                a = 1

    def generate_questions(self, cnt):
        tags_ids = Tag.objects.values_list(
            'id', flat=True
        )
        users_ids = Profile.objects.values_list(
            'id', flat=True
        )

        added_questions_ids = []
        for i in range(cnt):
            question = Question.objects.create(
                title=f.sentence()[:128],
                text='. '.join(f.sentences(f.random_int(min=2, max=5))),
                author_id=choice(users_ids)
            )
            added_questions_ids.append(question.id)
            for j in range(f.random_int(min=1, max=5)):
                question.tags.add(choice(tags_ids))

            for j in range(20):
                self.generate_marks(question)

        self.fill_questions_with_answers(cnt * 10, added_questions_ids)

    def fill_questions_with_answers(self, cnt, question_ids):
        if len(question_ids) == 0:
            question_ids = Question.objects.values_list(
                'id', flat=True
            )

        users_ids = Profile.objects.values_list(
            'id', flat=True
        )

        for i in range(cnt):
            answer = Answer.objects.create(
                text='. '.join(f.sentences(f.random_int(min=2, max=5))),
                question_id=choice(question_ids),
                author_id=choice(users_ids),
            )
            for j in range(f.random_int(min=1, max=2)):
                self.generate_marks(answer)

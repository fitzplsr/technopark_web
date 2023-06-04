from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Question, Answer, AnswerLike, QuestionLike, Tag, Profile
from django.utils.crypto import get_random_string
from faker import Faker
import random

Fake = Faker()


class Command(BaseCommand):
    help = 'Fiil database with fake data'
    images = ['img/avatar-1.png', 'img/avatar-2.jpeg', 'img/avatar-3.jpeg']

    def handle(self, *args, **options):
        ratio = options['ratio']
        words = list(set([get_random_string(int((random.random() * 100)) % 6 + 1) for _ in range(ratio * 2)]))[:ratio]
        # tags_words = list(set([Fake.word() for _ in range(ratio * 2)]))[:ratio]
        print(len(words))
        tags = [Tag(title=word) for word in words]
        Tag.objects.bulk_create(tags)
        users = []
        profiles = []
        for i in range(ratio):
            user = User(username=get_random_string(7), email='', password='1234567890')
            users.append(user)
            profiles.append(Profile(user=user, avatar=Fake.word(ext_word_list=self.images)))
        User.objects.bulk_create(users)
        Profile.objects.bulk_create(profiles)
        questions = []
        answers = []
        questions_likes = []
        answers_likes = []
        for i in range(ratio * 10):
            time = Fake.date_between()
            question = Question(
                author=profiles[int((random.random() * 10000)) % ratio],
                title=Fake.text(max_nb_chars=int((random.random() * 10000)) % 20 + 10),
                description=Fake.text(max_nb_chars=int((random.random() * 10000)) % 700 + 30),
                creating_time=Fake.date_time_between()
            )
            for _ in range(int((random.random() * 100)) % 10):
                questions_likes.append(QuestionLike(
                    question=question,
                    type=1 if int((random.random() * 100)) % 2 == 0 else -1,
                    author=profiles[int((random.random() * 10000)) % ratio]
                ))
            for _ in range(int((random.random() * 100)) % 10):
                answer = Answer(
                    author=profiles[int((random.random() * 10000)) % ratio],
                    description=Fake.text(max_nb_chars=int((random.random() * 10000)) % 300 + 30),
                    creating_time=Fake.date_time_between(time),
                    question=question
                )
                for _ in range(int((random.random() * 100)) % 10):
                    answers_likes.append(AnswerLike(
                        answer=answer,
                        type=1 if int((random.random() * 100)) % 2 == 0 else -1,
                        author=profiles[int((random.random() * 10000)) % ratio]
                    ))
                answers.append(answer)
            questions.append(question)
        Question.objects.bulk_create(questions)
        Answer.objects.bulk_create(answers)
        AnswerLike.objects.bulk_create(answers_likes)
        QuestionLike.objects.bulk_create(questions_likes)
        q_obj = Question.objects.filter(tags__isnull=True)
        tags_obj = Tag.objects.order_by('?')
        tags_ids = list(tags_obj.values_list('id'))
        print((int((random.random() * 10)) % 4 + 1))
        for query in q_obj:
            for i in range(int((random.random() * 10)) % 3 + 1):
                query.tags.add(Tag.objects.get(pk=tags_ids[int((random.random() * 100000)) % len(tags_ids)][0]))

    def add_arguments(self, parser):
        parser.add_argument(
            'ratio',
            type=int,
            default=0,
            help='Коэфициент заполнения сущностей'
        )
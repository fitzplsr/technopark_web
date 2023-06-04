from django.db import models
from django.db.models import Count, Sum
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


class QuestionManager(models.Manager):

    def get_obj(self, query):
        return {
                'id': query.pk,
                'tags': query.tags.all(),
                'answer_number': query.answer.count(),
                'title': query.title,
                'text': query.description,
                'like': query.like.all().aggregate(Sum('type', default=0))['type__sum'],
                'image': query.author.avatar
            }

    def get_likes(self, q_id):
        query = self.filter(pk=q_id).last()
        return query.like.all().aggregate(Sum('type', default=0))['type__sum']

    def get_all(self, ids):
        data = []
        for id in ids:
            data.append(self.get_obj(self.filter(pk=id).last()))
        return data

    def get_all_ids(self):
        return self.values_list('id', flat=True)

    def get_new_ids(self, count=10):
        return self.get_all_ids()[:count]

    def get_best_ids(self, count=10):
        return self.annotate(order=Sum('like__type', default=0)).order_by('-order').values_list('id', flat=True)[:count]

    def get_hot_ids(self, count=10):
        return self.annotate(order=Count('answer')).order_by('-order').values_list('id', flat=True)[:count]

    def get_by_tag_ids(self, tag):
        return self.filter(tags__title=tag).values_list('id', flat=True)


class Question(models.Model):

    class Meta:
        ordering = ['-creating_time']
        verbose_name = 'Вопрос',
        verbose_name_plural = 'Вопросы'

    title = models.CharField(
        max_length=255,
        verbose_name='Вопрос'
    )
    description = models.CharField(
        max_length=1000,
        verbose_name='Описание'
    )
    creating_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время создания'
    )
    editing_time = models.DateTimeField(
        auto_now=True,
        verbose_name='Время редактирования'
    )
    is_editing = models.BooleanField(
        default=False,
        verbose_name='Отредактировано'
    )
    author = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
        related_name='question',
        verbose_name='Автор'
    )

    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        related_name='questions',
        verbose_name='Тег'
    )

    objects = QuestionManager()

    def __str__(self):
        return f'Question #{self.pk} by {self.author}'


class AnswerManager(models.Manager):

    def get_obj(self, query):
        return {
                'id': query.pk,
                'text': query.description,
                'like': query.like.all().aggregate(Sum('type', default=0))['type__sum'],
                'image': query.author.avatar,
                'correct': query.is_correct
            }

    def get_likes(self, q_id):
        query = self.filter(pk=q_id).last()
        return query.like.all().aggregate(Sum('type', default=0))['type__sum']

    def get_all(self, ids):
        data = []
        for id in ids:
            data.append(self.get_obj(self.filter(pk=id).last()))
        return data

    def get_all_ids(self, q_id):
        return self.filter(question__pk=q_id).annotate(o=Sum('like__type', default=0)).order_by('-o').values_list('id', flat=True)


class Answer(models.Model):
    objects = AnswerManager()

    class Meta:
        verbose_name = 'Ответ',
        verbose_name_plural = 'Ответы'

    author = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
        related_name='answer',
        verbose_name='Ответчик'
    )
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name='answer',
        verbose_name='Вопрос'
    )
    description = models.CharField(
        max_length=1000,
        verbose_name='Ответ'
    )
    creating_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время ответа'
    )
    editing_time = models.DateTimeField(
        auto_now=True,
        verbose_name='Время редактирования'
    )
    is_editing = models.BooleanField(
        default=False,
        verbose_name='Отредактировано'
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name='Корректный ответ'
    )

    def __str__(self):
        return f'Answer #{self.pk} by {self.author}'


class TagManager(models.Manager):
    def get_popular(self, count=10):
        return self.annotate(cnt=Count('questions')).order_by('-cnt')[:count]


class Tag(models.Model):

    objects = TagManager()

    class Meta:
        verbose_name = 'Тег',
        verbose_name_plural = 'Теги'

    title = models.CharField(
        max_length=20,
        verbose_name='Тег'
    )

    def __str__(self):
        return f'{self.title}'


class ProfileManager(models.Manager):

    def get_user_by_username(self, username):
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            user = None

        return user

    def get_user_by_email(self, email):
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            user = None

        return user

    def get_best(self, count=5):
        ids = self.annotate(cnt=Count('answer')).order_by('-cnt').values_list('id')[:count]
        names = []
        for i in ids:
            names.append(self.get(pk=i[0]).user.username)
        return names


class Profile(models.Model):

    objects = ProfileManager()

    class Meta:
        verbose_name = 'Профиль',
        verbose_name_plural = 'Профили'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    avatar = models.ImageField(
        upload_to='img',
        default='img/base.jpg',
        verbose_name='Аватарка',
        blank=True,
        null=True
    )
    nickname = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name='Ник'
    )
    birthday = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата рождения'
    )

    def __str__(self):
        return f'{self.user.username}'


class AnswerLikeManager(models.Manager):

    def create_or_change_like(self, answer, profile, vote):
        like_enum = {"like": 1, "dislike": -1}

        like = AnswerLike.objects.filter(answer=answer).filter(author=profile).last()
        if not like:
            AnswerLike.objects.create(
                answer=answer,
                author=profile,
                type=like_enum[vote]
            )
        elif like.type != like_enum[vote]:
            like.type = like_enum[vote]
            like.save()
        else:
            like.type = 0
            like.save()


class AnswerLike(models.Model):

    objects = AnswerLikeManager()

    class Meta:
        verbose_name = 'Лайк ответа',
        verbose_name_plural = 'Лайки ответов'
        unique_together = ['answer', 'author']

    LIKE = 1
    DISLIKE = -1
    CHOICE = (
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike')
    )

    type = models.IntegerField(
        choices=CHOICE,
        default=1
    )
    answer = models.ForeignKey(
        'Answer',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='like',
        verbose_name='Ответ'
    )
    author = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Лайкнул'
    )

    def __str__(self):
        return f'Liked by {self.author}'


class QuestionLikeManager(models.Manager):

    def create_or_change_like(self, question, profile, vote):
        like_enum = {"like": 1, "dislike": -1}

        like = QuestionLike.objects.filter(question=question).filter(author=profile).last()
        if not like:
            QuestionLike.objects.create(
                question=question,
                author=profile,
                type=like_enum[vote]
            )
        elif like.type != like_enum[vote]:
            like.type = like_enum[vote]
            like.save()
        else:
            like.type = 0
            like.save()


class QuestionLike(models.Model):

    objects = QuestionLikeManager()

    class Meta:
        verbose_name = 'Лайк вопроса',
        verbose_name_plural = 'Лайки вопросов'
        unique_together = ['question', 'author']

    LIKE = 1
    DISLIKE = -1
    CHOICE = (
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike')
    )

    type = models.IntegerField(
        choices=CHOICE,
        default=1
    )
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='like',
        verbose_name='Вопрос'
    )
    author = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Лайкнул'
    )

    def __str__(self):
        return f'Liked by {self.author}'

from django.db import models


class FeedbackModel(models.Model):
    """Абстрактная модель. Хранит мнение пользователя (отзыв, комментарий
    и т.д.), а также дату создания."""
    author = models.ForeignKey(
        'reviews.User',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата создания'
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)


class ClassificationModel(models.Model):
    """Абстрактная модель. Хранит название и его псевдоним."""
    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Псевдоним'
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:30]

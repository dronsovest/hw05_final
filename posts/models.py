from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField("Текст",
                            help_text="Не забудте проверить орфографию, "
                            "пунктуацию и наличие смысла")
    pub_date = models.DateTimeField("Опубликовано", auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              blank=True,
                              null=True,
                              related_name="posts",
                              verbose_name="Сообщество",
                              help_text="Выберете сообщество. Если хотите."
                              )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ["-pub_date"]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name="comments",
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name="comments",
        on_delete=models.CASCADE
    )
    text = models.TextField(
        "Текст комментария",
        help_text="Прокомментировать пост"
    )
    created = models.DateTimeField("Опубликовано", auto_now_add=True)

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name="follower",
        on_delete = models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name="following",
        on_delete = models.CASCADE
    )

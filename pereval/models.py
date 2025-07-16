from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class User(models.Model):
    email = models.EmailField(unique=True)
    last_name = models.CharField(max_length=150)  # вместо fam
    first_name = models.CharField(max_length=150)  # вместо name
    middle_name = models.CharField(max_length=150, blank=True)  # вместо otc
    phone = models.CharField(max_length=20)

    class Meta:
        db_table = 'pereval_user'  # явное имя таблицы

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"


class Coords(models.Model):
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    height = models.IntegerField()

    class Meta:
        db_table = 'pereval_coords'  # явное имя таблицы

    def __str__(self):
        return f"Широта: {self.latitude}, Долгота: {self.longitude}, Высота: {self.height}"


class Level(models.Model):
    winter = models.CharField(max_length=10, blank=True, null=True)
    summer = models.CharField(max_length=10, blank=True, null=True)
    autumn = models.CharField(max_length=10, blank=True, null=True)
    spring = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'pereval_level'  # явное имя таблицы

    def __str__(self):
        return f"Зима: {self.winter}, Лето: {self.summer}, Осень: {self.autumn}, Весна: {self.spring}"


class Pereval(models.Model):
    STATUS_CHOICES = [
        ('new', 'новый'),
        ('pending', 'модератор взял в работу'),
        ('accepted', 'модерация прошла успешно'),
        ('rejected', 'модерация прошла, информация не принята'),
    ]

    beauty_title = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255)
    other_titles = models.CharField(max_length=255, blank=True)
    connect = models.TextField(blank=True)

    add_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coords = models.OneToOneField(Coords, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)

    class Meta:
        db_table = 'pereval_pereval'  # явное имя таблицы
        verbose_name = 'Перевал'
        verbose_name_plural = 'Перевалы'

    def __str__(self):
        return self.title


class Image(models.Model):
    pereval = models.ForeignKey(Pereval, related_name='images', on_delete=models.CASCADE)
    file_path = models.CharField(max_length=255)  # вместо data
    title = models.CharField(max_length=255)

    class Meta:
        db_table = 'pereval_image'  # явное имя таблицы

    def __str__(self):
        return self.title
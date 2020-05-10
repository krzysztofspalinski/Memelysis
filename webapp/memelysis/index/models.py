from django.db import models

# Create your models here.


class Memes(models.Model):
    meme_id = models.CharField(
        max_length=128, verbose_name='ID mema', unique=True)
    url = models.CharField(max_length=256, verbose_name="Adres url")
    image_path = models.CharField(
        max_length=256, verbose_name="Ścieżka do obrazka")
    source = models.ForeignKey('Sources', on_delete=models.CASCADE)
    meme_datetime = models.DateTimeField()

    def __str__(self):
        return f"{self.source}: {self.meme_id}"


class Sources(models.Model):
    name = models.CharField(
        max_length=32, verbose_name="Nazwa źródła", unique=True)

    def __str__(self):
        return self.name


class MemesUpvotesStatistics(models.Model):
    meme = models.OneToOneField('Memes', on_delete=models.CASCADE)
    upvotes = models.IntegerField(verbose_name="")
    upvotes_centile = models.FloatField(verbose_name="")

    def __str__(self):
        return f"{self.meme} upvotes: {self.upvotes}, upvotes centile: {self.upvotes_centile}"


class MemesClusters(models.Model):
    meme = models.OneToOneField('Memes', on_delete=models.CASCADE)
    cluster = models.CharField(max_length=64)

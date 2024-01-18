from django.db import models
from django.utils.text import slugify
from django.urls import reverse

# Create your models here.
class Statistic(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)

    def get_absolute_url(self):
        if self.slug:
            return reverse("dashboard", kwargs={"slug": self.slug})
        else:
            # Handle the case where slug is empty
            return reverse("main")

    @property
    def data(self):
        return self.dataitem_set.all()
    
    def __str__(self):
        return str(self.name)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class DataItem(models.Model):
    statistic = models.ForeignKey(Statistic, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField()
    owner = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.owner}: {self.value}"
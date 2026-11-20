import datetime
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.hashers import make_password


class Question(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    # ------------------------------------

    secret_token = models.CharField(max_length=255, blank= True, null=True, verbose_name="Secret token")
    
    def save(self, *args, **kwargs):
        
        #if self.secret_token:
        #    self.secret_token = make_password(self.secret_token)
        
        super().save(*args, **kwargs)

    # ------------------------------------
    
    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

from django.db import models

# Create your models here.
class TwitBot(models.Model):
    since_id = models.CharField(max_length=40, default="0")

    def __unicode__(self):
        return '%s' % (self.since_id)
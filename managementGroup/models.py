from django.db import models

# Create your models here.
class Group(models.Model):
    groupname = models.CharField(max_length=200, null=True)
    # gid = models.IntegerField(null=True)
    class Meta:
        db_table = 'Group'
    def __str__(self):
        return self.groupname

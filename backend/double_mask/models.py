from django.db import models
from django.utils import timezone
# Create your models here.
class DoubleMask(models.Model):
    active = models.BooleanField(default=False)
    taux_compression=models.FloatField(default=0)
    created_at = models.DateTimeField(default=timezone.now, editable=False, null=True)
    updated_at = models.DateTimeField(default=timezone.now, editable=False, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(DoubleMask, self).save(*args, **kwargs)
    class Meta:
        db_table = 'double_mask'    
    
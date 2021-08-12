from django.db import models

# Create your models here.


class Selnium_data(models.Model):
    loto_type = models.CharField(verbose_name='loto6 or 7', max_length=50, null=True, blank=True)
    loto_no = models.CharField(verbose_name='抽選回', max_length=50, null=True, blank=True)
    day = models.CharField(verbose_name='抽選日時', max_length=50, null=True, blank=True)
    num = models.CharField(verbose_name='当選番号', max_length=50, null=True, blank=True)
    one = models.CharField(verbose_name='１等', max_length=50, null=True, blank=True)
    one_money = models.CharField(verbose_name='１等賞金', max_length=50, null=True, blank=True)
    twe = models.CharField(verbose_name='2等', null=True, max_length=50, blank=True)
    twe_money = models.CharField(verbose_name='2等賞金', max_length=50, null=True, blank=True)
    three = models.CharField(verbose_name='3等', max_length=50, null=True, blank=True)
    three_money = models.CharField(verbose_name='3等賞金', max_length=50, null=True, blank=True)
    foru = models.CharField(verbose_name='4等', max_length=50, null=True, blank=True)
    foru_money = models.CharField(verbose_name='4等賞金', max_length=50, null=True, blank=True)
    five = models.CharField(verbose_name='5等', max_length=50, null=True, blank=True)
    five_money = models.CharField(verbose_name='5等賞金', max_length=50, null=True, blank=True)
    six = models.CharField(verbose_name='6等', max_length=50, null=True, blank=True)
    six_money = models.CharField(verbose_name='6等賞金', max_length=50, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'selnium_data'

        def __str__(self):
            return self.day

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.


class Stock_Code(models.Model):
    """
    stock_code…企業コード
    stock_year…上場から数えた年度
    """
    stock_code = models.IntegerField(verbose_name='企業コード',
                                     null=True,
                                     blank=True,
                                     default=0,
                                     validators=[MinValueValidator(0), MaxValueValidator(9999)]
                                     )

    stock_name = models.CharField(verbose_name='企業名',
                                  max_length=200,
                                  null=True,
                                  blank=True,
                                  )

    stock_year = models.CharField(verbose_name='年度',
                                  max_length=200,
                                  null=True,
                                  blank=True,
                                  )

    def __int__(self):
        return self.stock_code

from django.db import models


# Create your models here.

class Auction_data(models.Model):
    """
    seller_name…出品者
    serrch_name…検索商品
    shop_good…商品名
    price…落札値段
    price_tax…消費税
    bid_numder…入札数
    goods_quantity…出品個数
    price_start…開始値段
    auction_starttime…開始時間
    auction_endtime…終了時間
    photo_goods　オークションの写真
    """
    seller_name = models.CharField(verbose_name='出品者', max_length=50, null=True, blank=True)
    search_name = models.CharField(verbose_name='検索商品', max_length=50, null=True, blank=True)
    shop_good = models.CharField(verbose_name='商品名', max_length=150, null=True, blank=True)
    price = models.CharField(verbose_name='落札値段', max_length=50, null=True, blank=True)
    price_tax = models.CharField(verbose_name='消費税', max_length=50, null=True, blank=True)
    bid_numder = models.CharField(verbose_name='入札数', max_length=50, null=True, blank=True)
    goods_quantity = models.CharField(verbose_name='出品個数', max_length=50, null=True, blank=True)
    price_start = models.CharField(verbose_name='開始値段', max_length=50, null=True, blank=True)
    auction_starttime = models.CharField(verbose_name='開始時間', max_length=50, null=True, blank=True)
    auction_endtime = models.CharField(verbose_name='終了時間', max_length=50, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'オークションdata'

        def __str__(self):
            return self.seller_name


class Photo_Goods(models.Model):
    """
    オークションの写真（Auction_Dataのidにグループ化）
    """
    photo_goods = models.ImageField(upload_to='images')
    img_seller = models.CharField(verbose_name='写真', max_length=150, null=True, blank=True)

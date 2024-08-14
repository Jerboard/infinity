from django.contrib import admin
from django.db.models import Sum, FloatField
from django.db.models.functions import Cast
from django.utils.html import mark_safe


# Register your models here.
from .models import Msg
# from .models import User, Order, CashbackLevel, CashbackOrder
#
#
# @admin.register(User)
# class ViewAdminTable(admin.ModelAdmin):
#     list_display = ['user_id', 'first_name', 'last_name', 'username', 'first_visit', 'referrer',
#                     'custom_referral_lvl', 'balance', 'used_points_count', 'total_points_count',
#                     'count_invited_users']
#     search_fields = ['user_id', 'username', 'referrer']
#     list_filter = ('user_id', 'username')
#
#     def count_invited_users(self, obj):
#         count_users = User.objects.filter(referrer=obj.user_id).count()
#
#         referral_level = CashbackLevel.objects.filter(count_users__lte=count_users).order_by('-count_users').first()
#         if not referral_level:
#             referral_level = 1
#         return f'Ур. {referral_level} Пригл. {count_users}'
#
#     count_invited_users.short_description = 'Приглашенных'
#
#     def used_points_count(self, obj):
#         total = Orders.objects.filter(user_id=obj.user_id, status='successful').aggregate(total=Sum('used_points'))[
#             'total']
#         cashback = CashbackLevel.objects.filter(user_id=obj.user_id, status='successful').aggregate(total=Sum('sum'))[
#             'total']
#         if not total:
#             total = 0
#         if not cashback:
#             cashback = 0
#         return str(total + cashback)
#
#     used_points_count.short_description = 'Баллов потрачено'
#
#     def total_points_count(self, obj):
#         used_points = self.used_points_count(obj)
#         return str(float(used_points) + obj.balance)
#
#     total_points_count.short_description = 'Всего баллов'
#
#
# @admin.register(Order)
# class ViewOperationsTable(admin.ModelAdmin):
#     list_display = ['id', 'user_id', 'name_user', 'coin', 'pay_method', 'used_points', 'amount', 'exchange_rate',
#                     'display_profit']
#     search_fields = ['user_id']
#
#     def display_profit(self, obj):
#         return round(obj.profit, 2) if obj.profit is not None else 0
#
#     display_profit.short_description = 'Прибыль'
#
#
# @admin.register(CashbackLevel)
# class RefLvlTable(admin.ModelAdmin):
#     list_display = ['id', 'count_users', 'percent']
#     search_fields = ['user_id']


# админка новости
@admin.register(Msg)
class ViewAdminMsg(admin.ModelAdmin):
    list_display = ['comment', 'text', 'cover_image_preview']
    readonly_fields = ['updated_at', 'cover_image_preview_in']
    # list_editable = ['comment']

    def cover_image_preview(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo_path.url}" style="max-width:100px; max-height:100px;">')
        else:
            return "No image"

    def cover_image_preview_in(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo_path.url}" style="max-width:300px; max-height:300px;">')
        else:
            return "No image"

    cover_image_preview.short_description = 'Фото'
    cover_image_preview_in.short_description = 'Фото'

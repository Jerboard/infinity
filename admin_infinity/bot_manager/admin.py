from django.contrib import admin
from django.db.models import Sum, FloatField
from django.utils.html import mark_safe
from django.utils.functional import cached_property
from unfold.admin import ModelAdmin

from admin_infinity.settings import DEBUG
from .models import Msg
from .models import User, Order, CashbackLevel, Currency, PayMethod, Promo, CashbackOrder, Info

import logging


@admin.register(User)
class ViewUserTable(ModelAdmin):
    list_display = [
        'user_id',
        'full_name',
        'username',
        'last_visit',
        'referrer',
        'custom_referral_lvl',
        'referral_points',
        'cashback',
        'balance',
        'used_points_count',
        'total_points_count',
        'count_invited_users'
    ]
    search_fields = ['user_id', 'username', 'referrer']
    ordering = ['-last_visit']
    readonly_fields = ['first_visit', 'last_visit']

    @cached_property
    def cached_user_data(self):
        return {
            user.user_id: user
            for user in User.objects.all()
        }

    def count_invited_users(self, obj):
        count_users = User.objects.filter(referrer=obj.user_id).count()
        # print('------')
        # print(obj.custom_referral_lvl)
        logging.warning('------')
        logging.warning(obj.full_name)
        logging.warning(obj.custom_referral_lvl)

        if obj.custom_referral_lvl:
            referral_level = obj.custom_referral_lvl

        else:
            referral_level = CashbackLevel.objects.filter(count_users__lte=count_users).order_by('-count_users').first()
            if not referral_level:
                referral_level = 1

        # print(referral_level, count_users)
        logging.warning(f'Ур. {referral_level} Пригл. {count_users}')
        return f'Ур. {referral_level} Пригл. {count_users}'

    count_invited_users.short_description = 'Приглашенных'

    def balance(self, obj):
        referral_points = obj.referral_points or 0
        cashback = obj.cashback or 0
        return str(referral_points + cashback)

    balance.short_description = 'Баланс'

    def used_points_count(self, obj):
        user_orders = Order.objects.filter(user_id=obj.user_id, status='successful')
        cashback_orders = CashbackOrder.objects.filter(user_id=obj.user_id, status='successful')

        total_points = user_orders.aggregate(total=Sum('used_points'))['total'] or 0
        total_cashback = user_orders.aggregate(total=Sum('used_cashback'))['total'] or 0
        cashback = cashback_orders.aggregate(total=Sum('sum'))['total'] or 0

        return str(total_points + total_cashback + cashback)

    used_points_count.short_description = 'Баллов потрачено'

    def total_points_count(self, obj):
        used_points = int(self.used_points_count(obj))
        return str(used_points + (obj.referral_points or 0) + (obj.cashback or 0))

    total_points_count.short_description = 'Всего баллов'


# admin_infinity_bot
# dQ6tWhJ5
# @admin.register(User)
# class ViewUserTable(admin.ModelAdmin):
#     list_display = [
#         'user_id',
#         'full_name',
#         'username',
#         'last_visit',
#         'referrer',
#         'custom_referral_lvl',
#         'referral_points',
#         'cashback',
#         'balance',
#         'used_points_count',
#         'total_points_count',
#         'count_invited_users'
#     ]
#     search_fields = ['user_id', 'username', 'referrer']
#     ordering = ['-last_visit']
#     readonly_fields = ['first_visit', 'last_visit']
#
#     def count_invited_users(self, obj):
#         count_users = User.objects.filter(referrer=obj.user_id).count()
#
#         if obj.custom_referral_lvl:
#             referral_level = obj.custom_referral_lvl
#
#         else:
#             referral_level = CashbackLevel.objects.filter(count_users__lte=count_users).order_by('-count_users').first()
#             if not referral_level:
#                 referral_level = 1
#
#         return f'Ур. {referral_level} Пригл. {count_users}'
#
#     count_invited_users.short_description = 'Приглашенных'
#
#     def balance(self, obj):
#         referral_points = obj.referral_points or 0
#         cashback = obj.cashback or 0
#         return str(referral_points + cashback)
#
#     balance.short_description = 'Баланс'
#
#     def used_points_count(self, obj):
#         total_points = Order.objects.filter(user_id=obj.user_id, status='successful').aggregate(total=Sum('used_points'))[
#             'total']
#         total_cashback = Order.objects.filter(user_id=obj.user_id, status='successful').aggregate(total=Sum('used_cashback'))[
#             'total']
#         cashback = CashbackOrder.objects.filter(user_id=obj.user_id, status='successful').aggregate(total=Sum('sum'))[
#             'total']
#         # потрачено баллов
#         if not total_points:
#             total_points = 0
#         # потрачено кешбека
#         if not total_cashback:
#             total_cashback = 0
#         # выведено кешбека
#         if not cashback:
#             cashback = 0
#         return str(total_points + total_cashback + cashback)
#
#     used_points_count.short_description = 'Баллов потрачено'
#
#     def total_points_count(self, obj):
#         used_points = self.used_points_count(obj)
#         return str(int(used_points) + obj.referral_points + obj.cashback)
#
#     total_points_count.short_description = 'Всего баллов'


@admin.register(Order)
class ViewOrderTable(ModelAdmin):
    list_display = [
        'id',
        'user',
        'coin',
        'status',
        'pay_method',
        'used_points',
        'amount',
        'exchange_rate',
        'display_profit'
    ]
    search_fields = ['user__user_id', 'id']
    readonly_fields = ['created_at', 'updated_at']

    def display_profit(self, obj):
        return round(obj.profit, 2) if obj.profit is not None else 0

    display_profit.short_description = 'Прибыль'


@admin.register(CashbackLevel)
class RefLvlTable(ModelAdmin):
    list_display = ['id', 'count_users', 'percent']


# админка новости
@admin.register(Msg)
class ViewAdminMsg(ModelAdmin):
    if DEBUG:
        list_display = ['key', 'comment', 'text', 'cover_image_preview', 'custom_order']
        readonly_fields = ['updated_at', 'cover_image_preview_in', 'photo_id']
    else:
        list_display = ['comment', 'text', 'cover_image_preview', 'custom_order']
        readonly_fields = ['updated_at', 'cover_image_preview_in', 'photo_id', 'bot_id', 'key']
    list_editable = ['custom_order']
    ordering = ['custom_order']

    def cover_image_preview(self, obj):
        if obj.photo_path:
            return mark_safe(f'<img src="{obj.photo_path.url}" style="max-width:100px; max-height:100px;">')
        else:
            return "No image"

    def cover_image_preview_in(self, obj):
        if obj.photo_path:
            return mark_safe(f'<img src="{obj.photo_path.url}" style="max-width:300px; max-height:300px;">')
        else:
            return "No image"

    cover_image_preview.short_description = 'Фото'
    cover_image_preview_in.short_description = 'Фото'


# Валюты
@admin.register(Currency)
class ViewAdminMsg(ModelAdmin):
    list_display = ['code', 'rate', 'ratio', 'commission', 'buy_price', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active']


# способы оплаты
@admin.register(PayMethod)
class ViewAdminMsg(ModelAdmin):
    list_display = ['name', 'card', 'is_active']
    list_editable = ['is_active']


# способы оплаты
@admin.register(Promo)
class ViewAdminMsg(ModelAdmin):
    list_display = ['promo', 'rate', 'created_at', 'is_active', 'is_onetime']
    readonly_fields = ['created_at']


# способы оплаты
@admin.register(Info)
class ViewAdminMsg(ModelAdmin):
    list_display = ['cashback']
    readonly_fields = ['update_at']

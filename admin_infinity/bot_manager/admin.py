from django.contrib import admin
from django.db.models import Sum, FloatField
from django.db.models.functions import Cast
from django.utils.html import mark_safe


from admin_infinity.settings import DEBUG
from .models import Msg
from .models import User, Order, CashbackLevel, Currency, PayMethod, Promo, CashbackOrder, Info


@admin.register(User)
class ViewUserTable(admin.ModelAdmin):
    list_display = ['user_id', 'full_name',  'username', 'last_visit', 'referrer',
                    'custom_referral_lvl_id', 'balance', 'used_points_count', 'total_points_count',
                    'count_invited_users']
    # list_display = ['user_id', 'full_name',  'username', 'last_visit']
    search_fields = ['user_id', 'username', 'referrer']
    ordering = ['-last_visit']
    list_filter = ['user_id', 'username']
    readonly_fields = ['first_visit', 'last_visit']

    def count_invited_users(self, obj):
        count_users = User.objects.filter(referrer=obj.user_id).count()

        referral_level = CashbackLevel.objects.filter(count_users__lte=count_users).order_by('-count_users').first()
        if not referral_level:
            referral_level = 1
        return f'Ур. {referral_level} Пригл. {count_users}'

    count_invited_users.short_description = 'Приглашенных'

    def balance(self, obj):
        return str(obj.referral_points + obj.cashback)

    balance.short_description = 'Баланс'

    def used_points_count(self, obj):
        total_points = Order.objects.filter(user_id=obj.user_id, status='successful').aggregate(total=Sum('used_points'))[
            'total']
        total_cashback = Order.objects.filter(user_id=obj.user_id, status='successful').aggregate(total=Sum('used_cashback'))[
            'total']
        cashback = CashbackOrder.objects.filter(user_id=obj.user_id, status='successful').aggregate(total=Sum('sum'))[
            'total']
        # потрачено баллов
        if not total_points:
            total_points = 0
        # потрачено кешбека
        if not total_cashback:
            total_cashback = 0
        # выведено кешбека
        if not cashback:
            cashback = 0
        return str(total_points + total_cashback + cashback)

    used_points_count.short_description = 'Баллов потрачено'

    def total_points_count(self, obj):
        used_points = self.used_points_count(obj)
        return str(int(used_points) + obj.referral_points + obj.cashback)

    total_points_count.short_description = 'Всего баллов'


@admin.register(Order)
class ViewOrderTable(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'coin', 'pay_method', 'used_points', 'amount', 'exchange_rate',
                    'display_profit']
    search_fields = ['user_id']

    def display_profit(self, obj):
        return round(obj.profit, 2) if obj.profit is not None else 0

    display_profit.short_description = 'Прибыль'


@admin.register(CashbackLevel)
class RefLvlTable(admin.ModelAdmin):
    list_display = ['id', 'count_users', 'percent']


# админка новости
@admin.register(Msg)
class ViewAdminMsg(admin.ModelAdmin):
    if DEBUG:
        list_display = ['key', 'comment', 'text', 'cover_image_preview']
        readonly_fields = ['updated_at', 'cover_image_preview_in', 'photo_id']
    else:
        list_display = ['comment', 'text', 'cover_image_preview']
        readonly_fields = ['updated_at', 'cover_image_preview_in', 'photo_id', 'bot_id', 'key']
    # list_editable = ['comment']

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
class ViewAdminMsg(admin.ModelAdmin):
    list_display = ['code', 'rate', 'ratio', 'commission', 'buy_price', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active']


# способы оплаты
@admin.register(PayMethod)
class ViewAdminMsg(admin.ModelAdmin):
    list_display = ['name', 'card', 'is_active']
    list_editable = ['is_active']


# способы оплаты
@admin.register(Promo)
class ViewAdminMsg(admin.ModelAdmin):
    list_display = ['promo', 'rate', 'created_at']
    readonly_fields = ['created_at']


# способы оплаты
@admin.register(Info)
class ViewAdminMsg(admin.ModelAdmin):
    list_display = ['cashback']
    readonly_fields = ['update_at']

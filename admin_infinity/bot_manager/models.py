from django.db import models


# Уровни кешбека
# class CashbackLevel(models.Model):
#     id = models.IntegerField("№", primary_key=True, auto_created=True, editable=False)
#     count_users = models.IntegerField('Количество пользователей', null=True, blank=True)
#     percent = models.FloatField('Кешбек', null=True, blank=True)
#
#     objects: models.Manager = models.Manager()
#
#     def __str__(self):
#         return f'{self.id}'
#
#     class Meta:
#         verbose_name = 'Уровни кешбека'
#         verbose_name_plural = 'Уровни кешбека'
#         db_table = 'cashback_levels'
#         managed = False
#
#
# # Пользователи
# class User(models.Model):
#     id = models.IntegerField("№", primary_key=True, auto_created=True, editable=False)
#     user_id = models.CharField('№ тг', max_length=50, null=True, blank=True)
#     first_name = models.CharField('Имя', max_length=100, null=True, blank=True)
#     last_name = models.CharField('Фамилия', max_length=100, null=True, blank=True, default=None)
#     username = models.CharField('Юзернейм', max_length=100, null=True, blank=True)
#     first_visit = models.DateTimeField('Дата первого визита', null=True, blank=True, auto_now_add=True)
#     referrer = models.CharField('Реферер', max_length=50, null=True, blank=True)
#     balance = models.IntegerField('Баланс', null=True, blank=True)
#     custom_refferal_lvl = models.ForeignKey(
#         CashbackLevel,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         verbose_name='Уровень Рефферала',
#     )
#     ban = models.BooleanField('Забанить', null=True, blank=True, default=False)
#
#     objects: models.Manager = models.Manager()
#
#     def __str__(self):
#         return self.username or 'no name'
#
#     class Meta:
#         verbose_name = 'Пользователь'
#         verbose_name_plural = 'Пользователи'
#         db_table = 'users'
#         managed = False
#
#
# # заказы
# class Order(models.Model):
#     id = models.IntegerField("№", primary_key=True, auto_created=True, editable=False)
#     time = models.DateTimeField('Время поступления', null=True, blank=True)
#     status = models.CharField('Статус', max_length=50, null=True, blank=True)
#     user_id = models.CharField('ID пользователя', max_length=50, null=True, blank=True)
#     coin = models.CharField('Монета', max_length=50, null=True, blank=True)
#     pay_method = models.CharField('Способ оплаты', max_length=50, null=True, blank=True)
#     coin_sum = models.CharField('Сумма к получению', max_length=50, null=True, blank=True)
#     wallet = models.CharField('Кошелёк', max_length=255, null=True, blank=True)
#     promo = models.CharField('Промокод', max_length=50, null=True, blank=True)
#     promo_rate = models.FloatField('Скидка', null=True, blank=True)
#     exchange_rate = models.FloatField('Курс', null=True, blank=True)
#     percent = models.FloatField('Наценка', null=True, blank=True)
#     amount = models.FloatField('Сумма', null=True, blank=True)
#     used_points = models.FloatField('Использовано балов', null=True, blank=True)
#     total_amount = models.FloatField('Итог к оплате', null=True, blank=True)
#     message_chat_id = models.CharField('Чат', max_length=50, null=True, blank=True)
#     message_message_id = models.CharField('Сообщение', max_length=50, null=True, blank=True)
#     hash = models.CharField('Хеш', max_length=255, null=True, blank=True)
#     commission = models.FloatField('Комиссия', null=True, blank=True)
#     cashback = models.FloatField('Кешбек', null=True, blank=True)
#     profit = models.FloatField('Прибыль', null=True, blank=True)
#     referrer = models.CharField('ID реферера', max_length=50, null=True, blank=True)
#     promo_used_id = models.IntegerField('ID промокода', null=True, blank=True)
#     name_user = models.CharField('Имя пользователя', max_length=150, null=True, blank=True)
#
#     user_key = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='orders')
#
#     objects: models.Manager = models.Manager()
#
#     def __str__(self):
#         return str(self.id)
#
#     class Meta:
#         verbose_name = 'Заказ'
#         verbose_name_plural = 'Заказы'
#         db_table = 'orders'
#         managed = False
#
#
# # проверенные кошельки
# class CheckedWallet(models.Model):
#     id = models.IntegerField("№", primary_key=True, auto_created=True, editable=False)
#     user_id = models.CharField('ID пользователя', max_length=50, null=True, blank=True)
#     check_time = models.DateTimeField('Время проверки', null=True, blank=True)
#     coin_code = models.CharField('Монета', max_length=50, null=True, blank=True)
#     wallet = models.CharField('Кошелёк', max_length=255, null=True, blank=True)
#
#     objects: models.Manager = models.Manager()
#
#     def __str__(self):
#         return self.wallet
#
#     class Meta:
#         verbose_name = 'Проверенный кошелёк'
#         verbose_name_plural = 'Проверенные кошельки'
#         db_table = 'checked_wallets'
#         managed = False
#
#
# # валюты
# class Currency(models.Model):
#     id = models.IntegerField("№", primary_key=True, auto_created=True, editable=False)
#     name = models.CharField('Название', max_length=50, null=True, blank=True)
#     code = models.CharField('Код', max_length=255, null=True, blank=True)
#     rate = models.FloatField('Курс', null=True, blank=True)
#     ratio = models.FloatField('Наценка', null=True, blank=True)
#     min = models.FloatField('Минимальная сумма', null=True, blank=True)
#     max = models.FloatField('Максимальная сумма', null=True, blank=True)
#     commission = models.FloatField('Комиссия', null=True, blank=True)
#     buy_price = models.FloatField('Цена покупки', null=True, blank=True)
#     is_active = models.BooleanField('Активна', default=True)
#     round = models.IntegerField('Округление', null=True, blank=True)
#
#     objects: models.Manager = models.Manager()
#
#     def __str__(self):
#         return self.code
#
#     class Meta:
#         verbose_name = 'Валюта'
#         verbose_name_plural = 'Валюты'
#         db_table = 'currency'
#         managed = False
#
#
# # способы оплаты
# class PayMethod(models.Model):
#     id = models.IntegerField("№", primary_key=True, auto_created=True, editable=False)
#     name = models.CharField('Название', max_length=255, null=True, blank=True)
#     card = models.CharField('Номер карты', max_length=255, null=True, blank=True)
#     is_active = models.BooleanField('Активный', default=True)
#
#     objects: models.Manager = models.Manager()
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name = 'Карта'
#         verbose_name_plural = 'Карты'
#         db_table = 'pay_methods'
#         managed = False
#
#
# # промокоды
# class Promo(models.Model):
#     id = models.IntegerField("№", primary_key=True, auto_created=True, editable=False)
#     promo = models.CharField('Промокод', max_length=50, null=True, blank=True)
#     rate = models.FloatField('Скидка', max_length=50, null=True, blank=True)
#     start_date = models.DateField('Дата начала', null=True, blank=True)
#     end_date = models.DateField('Дата окончания', null=True, blank=True)
#     many = models.IntegerField('Кратность', default=False)
#     is_active = models.BooleanField('Активный', default=True)
#     is_onetime = models.BooleanField('Одноразовый', default=False)
#
#     objects: models.Manager = models.Manager()
#
#     def __str__(self):
#         return self.promo
#
#     class Meta:
#         verbose_name = 'Промокод'
#         verbose_name_plural = 'Промокоды'
#         db_table = 'promo'
#         managed = False
#
#
# # использованные одноразовые промокоды
# class UsedPromo(models.Model):
#     id = models.IntegerField("№", primary_key=True, auto_created=True, editable=False)
#     promo = models.CharField('Промокод', max_length=50, null=True, blank=True)
#     user_id = models.CharField('ID пользователя', max_length=50, null=True, blank=True)
#     end_date = models.DateTimeField('Дата использования', null=True, blank=True)
#
#     objects: models.Manager = models.Manager()
#
#     db_table = 'used_promo'
#     managed = False
#
#
# # заказы на кешбек
# class CashbackOrder(models.Model):
#     id = models.IntegerField("ID", primary_key=True, auto_created=True, editable=False)
#     time = models.DateTimeField('Время', null=True, blank=True)
#     status = models.CharField('Статус', max_length=50, null=True, blank=True)
#     user_id = models.CharField('ID пользователя', max_length=100, null=True, blank=True)
#     name_user = models.CharField('Имя', max_length=150, null=True, blank=True)
#     username = models.CharField('Юзернейм', max_length=50, null=True, blank=True)
#     card = models.CharField('Реквизиты', max_length=255, null=True, blank=True)
#     sum = models.IntegerField('Сумма', null=True, blank=True)
#     chat_id = models.CharField('Чат', max_length=50, null=True, blank=True)
#     message_id = models.CharField('Сообщение', max_length=50, null=True, blank=True)
#
#     objects: models.Manager = models.Manager()
#
#     def __str__(self):
#         return str(self.id)
#
#     class Meta:
#         verbose_name = 'Заказ на кешбек'
#         verbose_name_plural = 'Заказы на кешбек'
#         db_table = 'cashback_orders'
#         managed = False


# Тексты и фото
class Msg(models.Model):
    id = models.IntegerField("№", primary_key=True, auto_created=True, editable=False)
    updated_at = models.DateTimeField('Последнее обновление', auto_now=True)
    text = models.TextField('Текст')
    key = models.CharField('Ключ', max_length=255, unique=True)
    comment = models.CharField('Название', max_length=255, unique=True)
    photo_id = models.CharField('Фото ID', null=True, blank=True, max_length=255)
    photo_path = models.FileField('Путь', upload_to='photo')

    objects: models.Manager = models.Manager()

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        db_table = 'messages'
        managed = False


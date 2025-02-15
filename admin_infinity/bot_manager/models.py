from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


order_status = (
    ('not_conf', 'Ожидает оплаты'),
    ('new', 'Оплачен'),
    ('successful', 'Завершён'),
    ('failed', 'Отменён'),
)


# Уровни кешбека
class CashbackLevel(models.Model):
    id = models.AutoField(primary_key=True)
    count_users = models.IntegerField('Количество пользователей')
    percent = models.FloatField('Кешбек')

    objects: models.Manager = models.Manager()

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = 'Уровни кешбека'
        verbose_name_plural = 'Уровни кешбека'
        db_table = 'cashback_levels'
        managed = False


# Пользователи
class User(models.Model):
    user_id = models.BigIntegerField('№ тг', primary_key=True)
    full_name = models.CharField('Имя', max_length=255, null=True, blank=True)
    username = models.CharField('Юзернейм', max_length=255, null=True, blank=True)
    first_visit = models.DateTimeField('Дата первого визита')
    last_visit = models.DateTimeField('Дата последнего визита')
    referrer = models.BigIntegerField('Реферер', null=True, blank=True)
    referral_points = models.IntegerField('Реф. баллы', default=0, null=True, blank=True)
    cashback = models.IntegerField('Кешбек', default=0, null=True, blank=True)
    custom_referral_lvl = models.ForeignKey(
        CashbackLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Уровень рефералки',
    )
    ban = models.BooleanField('Забанить', default=False)

    def save(self, *args, **kwargs):
        if not self.referral_points:
            self.referral_points = 0
        if not self.cashback:
            self.cashback = 0
        super(User, self).save(*args, **kwargs)

    objects: models.Manager = models.Manager()

    def __str__(self):
        return self.full_name or 'no name'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'users'
        managed = False


# заказы
class Order(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', auto_now=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Пользователь', null=True, blank=True)
    status = models.CharField('Статус', max_length=255, null=True, blank=True, choices=order_status)
    coin = models.CharField('Монета', max_length=255, null=True, blank=True)
    pay_method = models.CharField('Способ оплаты', max_length=255, null=True, blank=True)
    card = models.CharField('Карта', max_length=255, null=True, blank=True)
    coin_sum = models.FloatField('Сумма к получению', null=True, blank=True)
    wallet = models.CharField('Кошелёк', max_length=255, null=True, blank=True)
    promo = models.CharField('Промокод', max_length=255, null=True, blank=True)
    promo_rate = models.IntegerField('Скидка', null=True, blank=True)
    exchange_rate = models.IntegerField('Курс', null=True, blank=True)
    percent = models.FloatField('Наценка', null=True, blank=True)
    amount = models.IntegerField('Сумма', null=True, blank=True)
    total_amount = models.IntegerField('Итог к оплате', null=True, blank=True)
    used_points = models.IntegerField('Исп. реф. баллов', default=0)
    used_cashback = models.IntegerField('Исп. кешбека', default=0)
    message_id = models.IntegerField('Сообщение', null=True, blank=True)
    hash = models.CharField('Хеш', max_length=255, null=True, blank=True)
    commission = models.IntegerField('Комиссия', default=0)
    cashback = models.IntegerField('Кешбек', default=0)
    profit = models.FloatField('Прибыль', null=True, blank=True)
    referrer = models.BigIntegerField('ID реферрера', null=True, blank=True)
    promo_used_id = models.IntegerField('ID промокода', null=True, blank=True)
    add_ref_points = models.IntegerField('Начислено баллов', null=True, blank=True)
    add_cashback = models.IntegerField('Начислено кешбека', null=True, blank=True)
    request_id = models.IntegerField('ID запроса реквизитов', null=True, blank=True)
    # user_key = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='orders')

    objects: models.Manager = models.Manager()

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        db_table = 'orders'
        managed = False


# проверенные кошельки
class CheckedWallet(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.BigIntegerField('ID пользователя')
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    coin_code = models.CharField('Монета', max_length=255)
    wallet = models.CharField('Кошелёк', max_length=255)

    objects: models.Manager = models.Manager()

    def __str__(self):
        return self.wallet

    class Meta:
        verbose_name = 'Проверенный кошелёк'
        verbose_name_plural = 'Проверенные кошельки'
        db_table = 'checked_wallets'
        managed = False


# валюты
class Currency(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлёна', auto_now=True)
    name = models.CharField('Название', max_length=255)
    code = models.CharField('Код', max_length=255)
    rate = models.FloatField('Курс', null=True, blank=True)
    ratio = models.FloatField('Наценка', null=True, blank=True)
    min = models.FloatField('Минимальная сумма', null=True, blank=True)
    max = models.FloatField('Максимальная сумма', null=True, blank=True)
    commission = models.FloatField('Комиссия', null=True, blank=True)
    buy_price = models.FloatField('Цена покупки', null=True, blank=True)
    is_active = models.BooleanField('Активна', default=True)
    round = models.IntegerField('Округление', null=True, blank=True)

    objects: models.Manager = models.Manager()

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = 'Валюта'
        verbose_name_plural = 'Валюты'
        db_table = 'currency'
        managed = False


# способы оплаты
class PayMethod(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('Название', max_length=255, null=True, blank=True)
    card = models.CharField('Номер карты', max_length=255, null=True, blank=True)
    is_active = models.BooleanField('Активный', default=True)

    objects: models.Manager = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Карта'
        verbose_name_plural = 'Карты'
        db_table = 'pay_methods'
        managed = False


# промокоды
class Promo(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Использован', auto_now_add=True)
    # user_id = models.IntegerField('Юзер ид', null=True, blank=True)
    rate = models.IntegerField('Скидка', null=True, blank=True)
    promo = models.CharField('Промокод', max_length=255, null=True, blank=True)
    is_active = models.BooleanField('Активен', default=True)
    is_onetime = models.BooleanField('Одноразовый', default=False)

    objects: models.Manager = models.Manager()

    def __str__(self):
        return self.promo

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'
        db_table = 'promo'
        managed = False


# использованные одноразовые промокоды
class UsedPromo(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    promo = models.CharField('Промокод', max_length=255)
    user_id = models.BigIntegerField('ID пользователя')

    objects: models.Manager = models.Manager()

    db_table = 'used_promo'
    managed = False


# заказы на кешбек
class CashbackOrder(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Использован', auto_now_add=True)
    user_id = models.BigIntegerField('ID пользователя')
    status = models.CharField('Статус', max_length=50)
    coin = models.CharField('Валюта', max_length=10)
    wallet = models.CharField('Кошелёк', max_length=255)
    sum = models.IntegerField('Сумма')
    sum_coin = models.FloatField('Сумма btc', null=True, blank=True)
    points = models.IntegerField('Реферральные баллы')
    cashback = models.IntegerField('Кешбек')
    message_id = models.IntegerField('Сообщение')

    objects: models.Manager = models.Manager()

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Заказ на кешбек'
        verbose_name_plural = 'Заказы на кешбек'
        db_table = 'cashback_orders'
        managed = False


# Тексты и фото
class Msg(models.Model):
    id = models.AutoField(primary_key=True)
    updated_at = models.DateTimeField('Последнее обновление', auto_now=True)
    text = models.TextField(
        verbose_name='Текст',
        help_text='&lt;b&gt;&lt;/b&gt; - <b>жирный</b> '
                  '&lt;i&gt;&lt;/i&gt; - <i>италик</i> '
                  '&lt;u&gt;&lt;/u&gt; - <u>подчёркнутый</u> '
                  '&lt;s&gt;&lt;/s&gt; - <s>зачёркнутый</s> '
                  '&lt;code&gt;&lt;/code&gt; - <code>моноширинный (копируется)</code>'
    )
    # text = CKEditor5Field('Текст', config_name='default')
    key = models.CharField('Ключ', max_length=255, unique=True)
    comment = models.CharField('Название', max_length=255, unique=True)
    photo_id = models.CharField('Фото ID', max_length=255, null=True, blank=True)
    bot_id = models.BigIntegerField('Бот ID', null=True, blank=True)
    photo_path = models.FileField('Путь', upload_to='photo')
    custom_order = models.IntegerField('Порядок', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk:
            self.photo_id = None
        super(Msg, self).save(*args, **kwargs)  # Сохраняем объект

    objects: models.Manager = models.Manager()

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        db_table = 'messages'
        managed = False


# Тексты и фото
class Info(models.Model):
    id = models.AutoField(primary_key=True)
    update_at = models.DateTimeField('Последнее обновление', auto_now=True)
    cashback = models.IntegerField('Кешбек')

    objects: models.Manager = models.Manager()

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = 'Инфо'
        verbose_name_plural = 'Инфо'
        db_table = 'info'
        managed = False

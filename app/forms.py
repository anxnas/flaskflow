from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, NumberRange

class UserForm(FlaskForm):
    username = StringField("Имя пользователя", validators=[DataRequired()])
    password = PasswordField("Пароль")
    balance = DecimalField("Баланс", validators=[DataRequired()])
    commission_rate = DecimalField("Ставка комиссии", validators=[DataRequired()])
    webhook_url = StringField("Webhook URL")
    role = SelectField("Роль", choices=[("Администратор", "Администратор"), ("Пользователь", "Пользователь")])
    usdt_wallet = StringField("USDT-кошелёк")
    submit = SubmitField("Сохранить")

class TransactionForm(FlaskForm):
    amount = DecimalField("Сумма", validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Создать")

class UpdateTransactionForm(FlaskForm):
    status = SelectField("Статус", choices=[
        ("Ожидание", "Ожидание"),
        ("Подтверждена", "Подтверждена"),
        ("Отменена", "Отменена"),
        ("Истекла", "Истекла")
    ])
    submit = SubmitField("Обновить")

class AutoRefreshForm(FlaskForm):
    auto_refresh = SelectField("Интервал автообновления", choices=[])
    submit = SubmitField("Применить")

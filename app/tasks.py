import datetime
import requests
from .extensions import celery, db, logger
from .models import Transaction, User
from app import create_app

flask_app = create_app()
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs) -> None:
    sender.add_periodic_task(60.0, check_pending_transactions.s(), name='check_pending_transactions')
    sender.add_periodic_task(300.0, check_usdt_wallet_balances.s(), name='check_usdt_wallet_balances')

@celery.task
def check_pending_transactions() -> None:
    with flask_app.app_context():
        logger.info("Проверяем просроченные транзакции (pending > 15 минут)")
        now = datetime.datetime.utcnow()
        cutoff = now - datetime.timedelta(minutes=15)

        txs = Transaction.query.filter(
            Transaction.status == "pending",
            Transaction.created_at < cutoff
        ).all()

        for tx in txs:
            tx.status = "expired"
            db.session.commit()

            if tx.user.webhook_url:
                try:
                    requests.post(
                        tx.user.webhook_url,
                        json={"transaction_id": tx.id, "status": tx.status},
                        timeout=5
                    )
                except Exception as e:
                    logger.error(f"Ошибка при отправке webhook: {e}")

@celery.task
def check_usdt_wallet_balances() -> None:
    with flask_app.app_context():
        logger.info("Проверяем USDT-кошельки пользователей")
        users = User.query.all()
        for user in users:
            if not user.usdt_wallet:
                user.usdt_wallet = f"testusdtwallet_{user.id}"
                db.session.commit()
                logger.info(f"Сгенерирован USDT-кошелёк для пользователя {user.id}")

            pseudo_balance = 123.45
            logger.info(f"Пользователь {user.username}, кошелёк={user.usdt_wallet}, баланс={pseudo_balance}")

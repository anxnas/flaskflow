from . import cli_bp
from app.extensions import db, logger
from app.models import User
from app.utils import hash_password
import click

@cli_bp.cli.command("create-user")
@click.option("--username", prompt=True, help="Имя пользователя (login)")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Пароль")
@click.option("--role", type=click.Choice(["admin", "user"]), default="user", prompt=True, help="Роль пользователя")
def create_user(username: str, password: str, role: str) -> None:
    """
    Создаёт пользователя с указанными username, password, role.
    Пример:
      flask create-user --username myadmin --password secret --role admin
    Или без аргументов — интерактивно.
    """
    existing = User.query.filter_by(username=username).first()
    if existing:
        logger.info(f"Пользователь '{username}' уже существует.")
        return

    new_user = User(
        username=username,
        password_hash=hash_password(password),
        role=role
    )
    db.session.add(new_user)
    db.session.commit()
    logger.info(f"Пользователь '{username}' (роль={role}) создан!")

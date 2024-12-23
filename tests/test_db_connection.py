import pytest
import psycopg2
def test_database_connection():
   """Тест проверяет возможность подключения к базе данных"""
   try:
       conn = psycopg2.connect(
           dbname="flaskflow_db",
           user="postgres",
           password="Mudar_Mudar_bek92920902",
           host="localhost",
           port="5433"
       )
       assert conn is not None, "Соединение не установлено"
       conn.close()
   except Exception as e:
       pytest.fail(f"Не удалось подключиться к базе данных: {str(e)}")
def test_database_credentials():
   """Тест проверяет правильность учетных данных"""
   with pytest.raises(psycopg2.OperationalError):
       psycopg2.connect(
           dbname="flaskflow_db",
           user="postgres",
           password="неверный_пароль",
           host="localhost",
           port="5433"
       )
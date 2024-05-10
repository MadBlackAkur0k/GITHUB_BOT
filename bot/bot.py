import logging
import re
import subprocess
import psycopg2
import paramiko
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
RM_HOST = os.getenv("RM_HOST")
RM_PORT = int(os.getenv("RM_PORT"))
RM_USER = os.getenv("RM_USER")
RM_PASSWORD = os.getenv("RM_PASSWORD")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")

logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')

def help(update: Update, context):
   # Создание строки справки, в которой будут перечислены доступные команды
    help_text = "Доступные команды:\n"
    help_text = "Доступные команды:\n"
    help_text += "/start - Начать диалог\n"
    help_text += "/help - Получить справку о доступных командах\n"
    help_text += "/find_email - Найти email-адреса в тексте\n"
    help_text += "/find_phone_number - Найти телефонные номера в тексте\n"
    help_text += "/verify_password - Проверить сложность пароля\n"
    help_text += "/get_release - Получить информацию о релизе Linux системы\n"
    help_text += "/get_uname - Получить информацию об архитектуре процессора, имени хоста системы и версии ядра\n"
    help_text += "/get_uptime - Получить информацию о времени работы системы\n"
    help_text += "/get_df - Получить информацию о состоянии файловой системы\n"
    help_text += "/get_free - Получить информацию о состоянии оперативной памяти\n"
    help_text += "/get_mpstat - Получить информацию о производительности системы\n"
    help_text += "/get_w - Получить информацию о работающих пользователях\n"
    help_text += "/get_auths - Получить последние 10 входов в систему\n"
    help_text += "/get_critical - Получить последние 5 критических событий\n"
    help_text += "/get_ps - Получить информацию о запущенных процессах\n"
    help_text += "/get_ss - Получить информацию об используемых портах\n"
    help_text += "/get_apt_list - Получить список установленных пакетов или информацию о конкретном пакете\n"
    help_text += "/get_services - Получить информацию о запущенных сервисах\n"
    help_text += "/get_repl_logs - Получить информацию о репликации PostgreSQL\n"
    help_text += "/get_emails - Вывести список email-адресов из базы данных\n"
    help_text += "/get_phone_numbers - Вывести список телефонных номеров из базы данных\n"
    
    # Отправка сообщения справки пользователю
    update.message.reply_text(help_text)

# Запускает процесс поиска email-адресов в тексте.
def find_email_command(update: Update, context):
    update.message.reply_text('Введите текст для поиска email-адресов: ')
    return 'find_email'
  
# Поиск email-адресов в тексте сообщения и предложение добавить их в базу данных.
def find_email(update: Update, context):
    user_input = update.message.text
    context.user_data['user_input'] = user_input
    email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    email_list = email_regex.findall(user_input)
    if not email_list:
        update.message.reply_text('Email-адреса не найдены')
        return ConversationHandler.END
    emails = '\n'.join(email_list)
    update.message.reply_text(emails)
    update.message.reply_text('Хотите занести найденные email-адреса в базу данных? (Да/Нет)')
    return 'add_emails_to_db'

# Добавление email-адресов в базу данных.
def add_emails_to_db(update: Update, context):
    user_response = update.message.text.lower()
    try:
        conn = psycopg2.connect(dbname=DB_DATABASE, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_emails (
                user_id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL
            )
        """)

        email_list = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', context.user_data['user_input'])
        for email in email_list:
            cursor.execute("INSERT INTO users_emails (email) VALUES (%s) ON CONFLICT DO NOTHING", (email,))

        if user_response == 'да':
            conn.commit()
            update.message.reply_text('Email-адреса успешно добавлены в базу данных.')
        elif user_response == 'нет':
            update.message.reply_text('Хорошо, данные не будут добавлены в базу данных.')
        else:
            update.message.reply_text('Пожалуйста, ответьте "Да" или "Нет".')

    except Exception as e:
        update.message.reply_text(f"Ошибка при работе с базой данных: {e}")

    finally:
        if 'conn' in locals():
            conn.close()
            cursor.close()

    return ConversationHandler.END

# Команда для поиска телефонных номеров в тексте.
def find_phone_number_command(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'find_phone_number'

# Поиск и вывод телефонных номеров из текста.
def find_phone_number(update: Update, context):
    user_input = update.message.text
    context.user_data['user_input'] = user_input
    phone_regex = re.compile(r'(?:\+7|8)\s?(?:\(|-)?\d{3}(?:\)|-)?\s?\d{3}(?:(?:-|\s)?\d{2}){2}\b')
    phone_list = phone_regex.findall(user_input)

    if not phone_list:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END

    valid_phone_numbers = []
    for match in phone_list:
        valid_phone_numbers.append(''.join(match))

    phone_numbers = '\n'.join(valid_phone_numbers)
    update.message.reply_text(phone_numbers)

    # Предложение занести данные в базу данных
    update.message.reply_text('Хотите занести найденные телефонные номера в базу данных? (Да/Нет)')
    return 'add_phone_numbers_to_db'

# Добавление телефонных номеров в базу данных.
def add_phone_numbers_to_db(update: Update, context):
    user_response = update.message.text.lower()
    if user_response == 'да':
        try:
            conn = psycopg2.connect(dbname=DB_DATABASE, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
            cursor = conn.cursor()

            # Проверка наличия таблицы users_phone и ее создание при отсутствии
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users_phone (
                    user_id SERIAL PRIMARY KEY,
                    phone_number VARCHAR(20) UNIQUE
                )
            """)

            phone_list = [match for match in re.findall(r'(?:\+7|8)\s?(?:\(|-)?\d{3}(?:\)|-)?\s?\d{3}(?:(?:-|\s)?\d{2}){2}\b', context.user_data['user_input'])]

            for phone in phone_list:
                cursor.execute("INSERT INTO users_phone (phone_number) VALUES (%s) ON CONFLICT DO NOTHING", (''.join(phone),))
            conn.commit()
            update.message.reply_text('Телефонные номера успешно добавлены в базу данных.')
        except Exception as e:
            update.message.reply_text(f"Ошибка при добавлении в базу данных: {e}")
        finally:
            cursor.close()
            conn.close()
    elif user_response == 'нет':
        update.message.reply_text('Хорошо, данные не будут добавлены в базу данных.')
    else:
        update.message.reply_text('Пожалуйста, ответьте "Да" или "Нет".')
    return ConversationHandler.END

# Команда для проверки сложности пароля.
def verify_password_command(update: Update, context):
    update.message.reply_text('Введите пароль для проверки сложности:')
    return 'verify_password'

# Проверка сложности пароля.
def verify_password(update: Update, context):
    user_input = update.message.text
    password_regex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()])[A-Za-z\d!@#$%^&*()]{8,}$')
    if password_regex.match(user_input):
        update.message.reply_text("Пароль сложный")
    else:
        update.message.reply_text("Пароль простой")
    return ConversationHandler.END

# Получение информации о релизе.
def get_release(update: Update, context):
    update.message.reply_text('Получение информации о релизе...')
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD)
        stdin, stdout, stderr = client.exec_command('lsb_release -a')
        release_info = stdout.read().decode('utf-8')
        client.close()
        update.message.reply_text(release_info)
    except Exception as e:
        logger.error(f"Ошибка при получении информации о релизе: {str(e)}")
        update.message.reply_text('Произошла ошибка при получении информации о релизе.')
    return ConversationHandler.END

# Получение информации о системе.
def get_uname(update: Update, context):
    update.message.reply_text('Получение информации о системе...')
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD)
        stdin, stdout, stderr = client.exec_command('uname -a')
        system_info = stdout.read().decode('utf-8')
        client.close()
        update.message.reply_text(system_info)
    except Exception as e:
        logger.error(f"Ошибка при получении информации о системе: {str(e)}")
        update.message.reply_text('Произошла ошибка при получении информации о системе.')
    return ConversationHandler.END

# Получение информации о времени работы системы.
def get_uptime(update: Update, context):
    update.message.reply_text('Получение информации о времени работы системы...')
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD)
        stdin, stdout, stderr = client.exec_command('uptime')
        uptime_info = stdout.read().decode('utf-8')
        client.close()
        update.message.reply_text(uptime_info)
    except Exception as e:
        logger.error(f"Ошибка при получении информации о времени работы системы: {str(e)}")
        update.message.reply_text('Произошла ошибка при получении информации о времени работы системы.')
    return ConversationHandler.END

# Получение информации о состоянии файловой системы.
def get_df(update: Update, context):
    update.message.reply_text('Получение информации о состоянии файловой системы...')
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD)
        stdin, stdout, stderr = client.exec_command('df -h')
        df_info = stdout.read().decode('utf-8')
        client.close()
        update.message.reply_text(df_info)
    except Exception as e:
        logger.error(f"Ошибка при получении информации о состоянии файловой системы: {str(e)}")
        update.message.reply_text('Произошла ошибка при получении информации о состоянии файловой системы.')
    return ConversationHandler.END

# Получение информации о состоянии оперативной памяти.
def get_free(update: Update, context):
    update.message.reply_text('Получение информации о состоянии оперативной памяти...')
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD)
        stdin, stdout, stderr = client.exec_command('free -h')
        free_info = stdout.read().decode('utf-8')
        client.close()
        update.message.reply_text(free_info)
    except Exception as e:
        logger.error(f"Ошибка при получении информации о состоянии оперативной памяти: {str(e)}")
        update.message.reply_text('Произошла ошибка при получении информации о состоянии оперативной памяти.')
    return ConversationHandler.END

# Получение информации о производительности системы.
def get_mpstat(update: Update, context):
    update.message.reply_text('Получение информации о производительности системы...')
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD)
        stdin, stdout, stderr = client.exec_command('mpstat')
        mpstat_info = stdout.read().decode('utf-8')
        client.close()
        update.message.reply_text(mpstat_info)
    except Exception as e:
        logger.error(f"Ошибка при получении информации о производительности системы: {str(e)}")
        update.message.reply_text('Произошла ошибка при получении информации о производительности системы.')
    return ConversationHandler.END

# Получение информации о работающих пользователях.
def get_w(update: Update, context):
    update.message.reply_text('Получение информации о работающих пользователях...')
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD)
        stdin, stdout, stderr = client.exec_command('w')
        w_info = stdout.read().decode('utf-8')
        client.close()
        update.message.reply_text(w_info)
    except Exception as e:
        logger.error(f"Ошибка при получении информации о работающих пользователях: {str(e)}")
        update.message.reply_text('Произошла ошибка при получении информации о работающих пользователях.')
    return ConversationHandler.END

# Получение информации о последних 10 входах в систему.
def get_auths(update: Update, context):
    update.message.reply_text('Получение информации о последних 10 входах в систему...')
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD)
        stdin, stdout, stderr = client.exec_command('tail /var/log/auth.log')
        auths_info_lines = stdout.readlines()
        client.close()
        for line in auths_info_lines:
            update.message.reply_text(line.strip())
    except Exception as e:
        logger.error(f"Ошибка при получении информации о последних 10 входах в систему: {str(e)}")
        update.message.reply_text('Произошла ошибка при получении информации о последних 10 входах в систему.')
    return ConversationHandler.END

# Получение информации о последних 5 критических событиях.
def get_critical(update: Update, context):
    update.message.reply_text('Получение информации о последних 5 критических событиях...')
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD)
        stdin, stdout, stderr = client.exec_command('journalctl -p crit -n 5')
        critical_info_lines = stdout.readlines()
        client.close()
        for line in critical_info_lines:
            update.message.reply_text(line.strip())
    except Exception as e:
        logger.error(f"Ошибка при получении информации о последних 5 критических событиях: {str(e)}")
        update.message.reply_text('Произошла ошибка при получении информации о последних 5 критических событиях.')
    return ConversationHandler.END

# Получение информации о запущенных процессах.
def get_ps(update: Update, context):
    update.message.reply_text('Получение информации о запущенных процессах...')
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD)
        stdin, stdout, stderr = client.exec_command('ps -aux --sort=-%cpu | head -n 11')
        ps_info = stdout.read().decode('utf-8')
        client.close()
        ps_lines = ps_info.strip().split('\n')
        for line in ps_lines:
            update.message.reply_text(line)
    except Exception as e:
        logger.error(f"Ошибка при получении информации о запущенных процессах: {str(e)}")
        update.message.reply_text('Произошла ошибка при получении информации о запущенных процессах.')
    return ConversationHandler.END

# Получение информации об используемых портах.
def get_ss(update: Update, context):
    update.message.reply_text('Получение информации об используемых портах...')
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD)
        stdin, stdout, stderr = client.exec_command('ss -tuln')
        ss_info = stdout.read().decode('utf-8')
        client.close()
        ss_lines = ss_info.strip().split('\n')
        for line in ss_lines:
            update.message.reply_text(line)
    except Exception as e:
        logger.error(f"Ошибка при получении информации об используемых портах: {str(e)}")
        update.message.reply_text('Произошла ошибка при получении информации об используемых портах.')
    return ConversationHandler.END

# Получение списка установленных пакетов или информации о конкретном пакете.
def get_apt_list_command(update: Update, context):
    update.message.reply_text('Введите "all" или "все" для получения списка всех установленных пакетов(20 пакетов), '
                              'или введите название пакета: ')
    return 'get_apt_list'

# Получение списка установленных пакетов или информации о конкретном пакете.
def get_apt_list(update: Update, context):
    package_name = update.message.text.strip()

    if package_name.lower() in ['all', 'все']:
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD)
            stdin, stdout, stderr = client.exec_command('apt list --installed | head -n 21')
            package_list = stdout.read().decode('utf-8')
            client.close()

            # Разделяем список на пакеты
            packages = package_list.strip().split('\n')

            # Отправляем каждый пакет по очереди
            for package in packages:
                update.message.reply_text(package)
        except Exception as e:
            logger.error(f"Ошибка при получении списка установленных пакетов: {str(e)}")
            update.message.reply_text('Произошла ошибка при получении списка установленных пакетов.')
    else:
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD)
            stdin, stdout, stderr = client.exec_command(f'apt show {package_name}')
            package_info = stdout.read().decode('utf-8')
            client.close()
            update.message.reply_text(package_info)
        except Exception as e:
            logger.error(f"Ошибка при получении информации о пакете {package_name}: {str(e)}")
            update.message.reply_text(f'Произошла ошибка при получении информации о пакете {package_name}.')

    return ConversationHandler.END

# Получение информации о запущенных сервисах.
def get_services(update: Update, context):
    update.message.reply_text('Получение информации о запущенных сервисах...')
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD)
        stdin, stdout, stderr = client.exec_command('systemctl list-units --type=service')
        for line in stdout:
            update.message.reply_text(line.strip())
        client.close()
    except Exception as e:
        logger.error(f"Ошибка при получении информации о запущенных сервисах: {str(e)}")
        update.message.reply_text('Произошла ошибка при получении информации о запущенных сервисах.')

    return ConversationHandler.END

# Получение логов репликации.
def get_repl_logs(update: Update, context):
    update.message.reply_text('Получение логов репликации...')
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD)
        stdin, stdout, stderr = client.exec_command('tail -n 20 /var/log/postgresql/postgresql-15-main.log')
        repl_logs = stdout.read().decode('utf-8')
        client.close()
        repl_logs_lines = repl_logs.strip().split('\n')
        for line in repl_logs_lines:
            update.message.reply_text(line)
    except Exception as e:
        logger.error(f"Ошибка при получении логов репликации: {str(e)}")
        update.message.reply_text('Произошла ошибка при получении логов репликации.')

    return ConversationHandler.END

# Выполнение SQL-запроса к базе данных.
def execute_sql(query):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_DATABASE
        )
        cursor = connection.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        return records
    except (Exception, psycopg2.Error) as error:
        print("Ошибка при работе с PostgreSQL:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

# Получение списка email-адресов из базы данных.
def get_emails(update: Update, context):
    query = "SELECT email FROM users_emails;"
    records = execute_sql(query)
    if records:
        emails = '\n'.join([record[0] for record in records])
        update.message.reply_text("Список email-адресов:\n" + emails)
    else:
        update.message.reply_text("В базе данных нет email-адресов.")

# Получение списка номеров телефона из базы данных.
def get_phone_numbers(update: Update, context):
    query = "SELECT phone_number FROM users_phone;"
    records = execute_sql(query)
    if records:
        phone_numbers = '\n'.join([record[0] for record in records])
        update.message.reply_text("Список номеров телефона:\n" + phone_numbers)
    else:
        update.message.reply_text("В базе данных нет номеров телефона.")

def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    # Обработчики диалогов
    conv_handler_email = ConversationHandler(
        entry_points=[CommandHandler('find_email', find_email_command)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'add_emails_to_db': [MessageHandler(Filters.text & ~Filters.command, add_emails_to_db)]
        },
        fallbacks=[]
    )
    dp.add_handler(conv_handler_email)

    conv_handler_phone = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_number_command)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'add_phone_numbers_to_db': [MessageHandler(Filters.text & ~Filters.command, add_phone_numbers_to_db)]
        },
        fallbacks=[]
    )
    dp.add_handler(conv_handler_phone)

    conv_handler_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_password_command)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)]
        },
        fallbacks=[]
    )
    dp.add_handler(conv_handler_password)

    # Обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))

    conv_handler_apt_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list_command)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)]
        },
        fallbacks=[]
    )
    dp.add_handler(conv_handler_apt_list)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()

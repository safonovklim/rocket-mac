import os
from datetime import datetime

MILES_CURRENCY_CODE = "RR"
CURRENCIES = { 'RUB': "\u20BD", 'USD': "\u0024", 'EUR': "\u20AC", MILES_CURRENCY_CODE: "рр." }
MAX_TITLE_LENGTH = 25
BREAK_LINE = 'BREAK_LINE'


def format_currency(currency):
    return CURRENCIES[currency] if currency in CURRENCIES else currency


def format_money(amount, currency, show_plus = False):
    result = str(amount) + ' ' + format_currency(currency)
    if amount > 0 and show_plus:
        return "+" + result
    return result


def format_datetime(timestamp):
    return timestamp


def format_feed_title(title):
    if (len(title) > MAX_TITLE_LENGTH):
        return title[0:MAX_TITLE_LENGTH] + '...'
    else:
        return title


def format_transaction(transaction):
    type = transaction[0]
    info = transaction[1]

    ts = datetime.fromtimestamp(info['happened_at'])

    money = format_money(info['display_money']['amount'], info['display_money']['currency_code'])
    merchant = info['merchant']

    result = money
    result += " "
    result += format_feed_title(merchant['name'])

    result += '|length=45'

    return result


def format_transaction_status(status):
    if status == "hold":
        return "Авторизовано"
    if status == "confirmed":
        return "Подтверждено"
    return None


def format_transaction_details(transaction):
    type = transaction[0]
    info = transaction[1]

    rows = []

    ts = datetime.fromtimestamp(info['happened_at'])
    rows.append("📆 " + ts.strftime("%d.%m.%Y %H:%m"))

    if info['mimimiles'] != 0:
        rows.append(format_money(info['mimimiles'], MILES_CURRENCY_CODE, show_plus=True))

    if info['comment']:
        rows.append(info['comment'])

    rows.append(BREAK_LINE)

    status = format_transaction_status(info['status'])

    if status != None:
        rows.append("Статус: " + status)

    rows.append("Категория: " + info['category']['display_name'])

    if info['has_receipt']:
        rows.append(BREAK_LINE)
        rows.append('📠 Квитанция|href=' + info['receipt_url'])

    return rows


def format_sub_level(string, level = 1):
    result = ""

    for x in range(1, level):
        result += "--"

    if string == BREAK_LINE:
        result += "---"
        return result
    else:
        result += " " + string
        return result


def format_friends(friends_count):
    return "Друзей в Рокетбанке: " + str(friends_count)


def format_push(push):
    info = push[1]
    return info['body']


def app_is_not_configured():
    return "Мы еще не готовы к запуску! Настройте свою учетную запись!|bash=" + os.path.dirname(os.path.realpath(__file__)) + "/INSTALLER"
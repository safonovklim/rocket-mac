import os
from datetime import datetime

MILES_CURRENCY_CODE = "RR"
CURRENCIES = { 'RUB': "\u20BD", 'USD': "\u0024", 'EUR': "\u20AC", MILES_CURRENCY_CODE: "рр." }
MAX_TITLE_LENGTH = 25
BREAK_LINE = '---'


def currency(c):
    return CURRENCIES[c] if c in CURRENCIES else c


def money(amount, cur, show_plus = False):
    result = str(amount) + ' ' + currency(cur)
    if amount > 0 and show_plus:
        return "+" + result
    return result


def feed_title(title):
    if len(title) > MAX_TITLE_LENGTH:
        return title[0:MAX_TITLE_LENGTH] + '...'
    else:
        return title


def transaction(tr):
    info = tr[1]

    display_money = money(info['display_money']['amount'], info['display_money']['currency_code'])
    merchant = info['merchant']

    result = display_money
    result += " "
    result += feed_title(merchant['name'])

    result += '|length=45'

    return result


def transaction_status(status):
    if status == "hold":
        return "Авторизовано"
    if status == "confirmed":
        return "Подтверждено"
    return None


def transaction_details(tr):
    info = tr[1]

    rows = []

    ts = datetime.fromtimestamp(info['happened_at'])
    rows.append("📆 " + ts.strftime("%d.%m.%Y %H:%m"))

    if info['mimimiles'] != 0:
        rows.append(money(info['mimimiles'], MILES_CURRENCY_CODE, show_plus=True))

    if info['comment']:
        rows.append(info['comment'])

    rows.append(BREAK_LINE)

    status = transaction_status(info['status'])

    if status != None:
        rows.append("Статус: " + status)

    rows.append("Категория: " + info['category']['display_name'])

    if info['has_receipt']:
        rows.append(BREAK_LINE)
        rows.append('📠 Квитанция|href=' + info['receipt_url'])

    return rows


def sub_level(string, level = 1):
    result = ""

    for x in range(1, level):
        result += "--"

    if string == BREAK_LINE:
        result += "---"
        return result
    else:
        result += " " + string
        return result


def friends(friends_count):
    return "Друзей в Рокетбанке: " + str(friends_count)


def push(push_item):
    info = push_item[1]
    return info['body']


def safe_account(account):
    return money(account['balance'], account['currency']) + ' (' + account['title'] + ')'


def get_account_details(account):
    d = account['account_details']
    rows = []
    if account['currency'] == 'RUB':
        rows.append('БИК: ' + d['bic'])
        rows.append('Банк: ' + d['bank_name'])
        rows.append('Корреспондентский счет: ' + d['ks'])
        rows.append('Номер счета: ' + d['account'])
        rows.append('Получатель: ' + d['owner'])
        rows.append('Назначение платежа: ' + d['goal'])
        rows.append('ИНН: ' + d['inn'])
        rows.append('КПП: ' + d['kpp'])
    else:
        rows.append('Банк корреспондент: ' + d['corr'])
        rows.append('Банк получателя: ' + d['benef_bank'])
        rows.append('Адрес банка получателя: ' + d['benef_bank_address'])
        rows.append('SWIFT: ' + d['benef_swift'])
        rows.append('Получатель: ' + d['owner'])
        rows.append('Номер счета: ' + d['account'])

    return rows


def get_deposit_currency(deposit_item):
    return deposit_item['rocket_deposit']['currency']


def deposit(deposit_item):
    d_currency = get_deposit_currency(deposit_item)
    return money(deposit_item['balance'], d_currency) + ' (' + deposit_item['title'] + ')'


def deposit_statement(statement_item, curr):
    return money(statement_item['amount'], curr, show_plus=True) + ' ' + statement_item['description']


def get_install_link():
    return os.path.dirname(os.path.realpath(__file__)) + "/INSTALLER"


def app_version(version, build):
    return 'Версия ' + version + ' (' + str(build) + ')'


def new_version(available = False, nvjson = {}):
    if available:
        return 'Установите новую версию ' + nvjson['build_label'] + '|href=' + nvjson['upgrade_faq_url']
    else:
        return 'Нет обновлений'


def re_login():
    return "Запустить установщик|bash=" + get_install_link()


def app_unable_to_login():
    return "Не получилось войти\nВозможно, Вы сменили код от приложения\n📲 Авторизоваться|bash=" + get_install_link()


def app_is_not_configured():
    return "Мы еще не готовы к запуску! Настройте свою учетную запись!|bash=" + get_install_link()
#!/usr/bin/env PYTHONIOENCODING=UTF-8 /usr/local/bin/python3

# <bitbar.title>Rocketbank</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>Klim Safonov</bitbar.author>
# <bitbar.author.github>safonovklim</bitbar.author.github>
# <bitbar.desc>It showing short info about your account</bitbar.desc>
# <bitbar.dependencies>python</bitbar.dependencies>
import sys
from rocket import formatters as f, core

print('🚀') # Logo in status bar
print('---')

CONFIG = core.get_config()

if not CONFIG[core.CFG_USER_CONFIGURED]:
    print(f.app_is_not_configured())
    sys.exit(0)

OUT = []


def po(string):
    OUT.append(string) 


fresh_data = False
login_required = core.is_login_required(CONFIG)
if login_required:
    login_result = core.login(CONFIG[core.CFG_AUTH_LOGIN], CONFIG[core.CFG_AUTH_PASSCODE])
    login_result_json = login_result.json()

    # Require reinstall
    if not core.is_response_ok(login_result):
        print(f.app_unable_to_login())
        sys.exit(0)
    else:
        token = login_result_json['token']
        user = login_result_json['user']
        feed = core.get_transactions(token, 1, 20)
        feed_json = feed.json()
        core.write_file_config({
            core.CFG_USER_TOKEN: token,
            core.CFG_TOKEN_UNSUCCESSFUL_USAGE: 0
        })
        fresh_data = True
else:
    token = CONFIG[core.CFG_USER_TOKEN]
    get_profile_result = core.get_profile(token)
    if core.is_response_ok(get_profile_result):
        core.write_file_config({ core.CFG_TOKEN_UNSUCCESSFUL_USAGE: 0 })
        user = get_profile_result.json()['user']
        feed = core.get_transactions(token, 1, 20)
        feed_json = feed.json()
        fresh_data = True
    else:
        core.write_file_config({ core.CFG_TOKEN_UNSUCCESSFUL_USAGE: CONFIG[core.CFG_TOKEN_UNSUCCESSFUL_USAGE] + 1 })
        user = core.read_json(core.PROFILE_JSON_FILE_NAME)
        feed_json = core.read_json(core.FEED_JSON_FILE_NAME)


if fresh_data:
    core.write_json(feed_json, core.FEED_JSON_FILE_NAME)
    core.write_json(user, core.PROFILE_JSON_FILE_NAME)

# User info
po(user['first_name'] + ' ' + user['last_name'])
po(user['first_name'] + ' ' + user['last_name'] + ' (ID: ' + str(user['id']) + ')|alternate=true')
po(str(user['miles']) + ' рокетрублей')

# Push info
all_pushes = core.collect_push(feed_json['feed'])
if CONFIG[core.CFG_SHOW_PUSH] and len(all_pushes) > 0:
    po(f.BREAK_LINE)
    for push in all_pushes:
        po(f.push(push))


# Friends
if CONFIG[core.CFG_SHOW_FRIENDS]:
    po(f.BREAK_LINE)
    if user['invites']['friends'] > 0:
        po(f.friends(user['invites']['friends']))

# Cards
if CONFIG[core.CFG_SHOW_CARDS]:
    po(f.BREAK_LINE)
    po('💳 Карты')
    for card in user['accounts']:
        po(f.money(card['balance'], card['currency']) + ' (' + card['title'] + ')')

        po('-- ' + card['pan'] + ' (до ' +  str(card['month']) + '/' + str(card['year']) + ')')
        po('--  ' + f.money(card['balance'], card['currency']) + '')
        po('-----')

        # Tariff
        tariff = card['current_tariff']
        po('-- Тариф - ' + tariff['name'] + '|href=' + tariff['url'])

        # Limits
        po(
            f.sub_level(
                'Лимиты|size=14',
                2
            )
        )
        for limits_group in card['better_limits']:
            po('-------')
            po('---- ' + limits_group[0] + ':')
            for limit_item in limits_group[1]:
                po('---- ' + limit_item[0] + ' ' + limit_item[1])

        # Account details
        po(f.sub_level('📫 Реквизиты', 2))
        details = f.get_account_details(card)
        for detail in details:
            po(f.sub_level(detail + '|length=45', 3))


# Safe accounts
if CONFIG[core.CFG_SHOW_SAFE_ACCOUNTS] and len(user['safe_accounts']) > 0:
    po(f.BREAK_LINE)
    po('💰 Счета')
    for account in user['safe_accounts']:
        po(f.safe_account(account))
        po(f.sub_level('📄 Условия счета|href=' + account['url'], 2))
        po(f.sub_level('📫 Реквизиты', 2))
        details = f.get_account_details(account)
        for detail in details:
            po(f.sub_level(detail + '|length=45', 3))

# Deposits
if CONFIG[core.CFG_SHOW_DEPOSITS] and len(user['deposits']) > 0:
    po(f.BREAK_LINE)
    po('💸 Вклады')
    for deposit in user['deposits']:
        deposit_currency = f.get_deposit_currency(deposit)

        po(f.deposit(deposit))
        po(f.sub_level('📄 Условия вклада|href=' + deposit['rocket_deposit']['url'], 2))
        po(f.sub_level('До ' + deposit['end_date'], 2))

        if len(deposit['statements']) > 0:
            po(f.sub_level('История операций', 2))
            for statement in deposit['statements']:
                po(f.sub_level(f.deposit_statement(statement_item=statement, curr=deposit_currency), 3))

# Exchange
if CONFIG[core.CFG_SHOW_EXCHANGE_RATES]:
    po(f.BREAK_LINE)
    po('⚖️ Курс валют|href='+user['rates']['url'])
    po('1 ' + f.currency('USD') + ' = ' + str(user['rates']['card_usd']) + ' ' + f.currency('RUB'))
    po('1 ' + f.currency('EUR') + ' = ' + str(user['rates']['card_eur']) + ' ' + f.currency('RUB'))

# Transactions
if CONFIG[core.CFG_SHOW_LATEST_TRANSACTIONS]:
    po(f.BREAK_LINE)
    po('🍷 Последние операции')

    transactions = list(filter(lambda item: item[1]['visible'] and item[0] == 'operation', feed_json['feed']))

    for t in transactions[:5]:
        po(f.transaction(t))
        details = f.transaction_details(t)
        for detail in details:
            po(f.sub_level(detail, 2))

    po('Ещё')
    for t in transactions[5:]:
        po(f.sub_level(f.transaction(t), 2))
        details = f.transaction_details(t)
        for detail in details:
            po(f.sub_level(detail, 3))


po(f.BREAK_LINE)

po('👩‍🚀 Поддержка')
po(f.sub_level('8 (800) 200-07‑08 - по России', 2))
po(f.sub_level('+7 (495) 133-07‑08 - из-за границы', 2))

po(f.sub_level(f.BREAK_LINE, 2))
po(f.sub_level('👩‍💻 Рокетбанк для macOS', 2))

po(f.sub_level(f.app_version(core.APP_VERSION, core.APP_BUILD), 3))
is_new_version_available, nvjson = core.is_update_available()
po(f.sub_level(
    f.new_version(
        is_new_version_available,
        nvjson
    ),
    3
))

po(f.sub_level(f.BREAK_LINE, 3))
po(f.sub_level(f.re_login(), 3))

po(f.sub_level(f.BREAK_LINE, 3))
po(f.sub_level('Telegram|href=' + core.APP_LINK_TELEGRAM, 3))
po(f.sub_level('GitHub|href=' + core.APP_LINK_GITHUB, 3))

# Output
for info_string in OUT:
    print(info_string.replace('\n', ' '))

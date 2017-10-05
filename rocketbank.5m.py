#!/usr/bin/env PYTHONIOENCODING=UTF-8 /usr/local/bin/python3

# <bitbar.title>Rocketbank</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>Klim Safonov</bitbar.author>
# <bitbar.author.github>safonovklim</bitbar.author.github>
# <bitbar.desc>It showing short info about your account</bitbar.desc>
# <bitbar.dependencies>python</bitbar.dependencies>
import sys
import requests
from rocket import formatters, core

print('🚀') # Logo in status bar
print('---')

CONFIG = core.get_config()

if CONFIG[core.CFG_USER_CONFIGURED] == False:
    print(formatters.app_is_not_configured())
    sys.exit(0)

login_result = core.login(CONFIG[core.CFG_AUTH_LOGIN], CONFIG[core.CFG_AUTH_PASSCODE])

if login_result.status_code == requests.codes.ok:
    login_result_json = login_result.json()

    user = login_result_json['user']
    token = login_result_json['token']

    feed = core.get_transactions(token, 1, 20)
    IS_FEED_OK = feed.status_code == requests.codes.ok
    feed_json = feed.json()

    OUT = []

    # User info
    OUT.append(user['first_name'] + ' ' + user['last_name'])
    OUT.append(user['first_name'] + ' ' + user['last_name'] + ' (ID: ' + str(user['id']) + ')|alternate=true')
    OUT.append(str(user['miles']) + ' рокетрублей')

    # Push info
    all_pushes = core.collect_push(feed_json['feed']) if IS_FEED_OK else []
    if CONFIG[core.CFG_SHOW_PUSH] and len(all_pushes) > 0:
        OUT.append('---')
        for push in all_pushes:
            OUT.append(formatters.format_push(push))


    # Friends
    if CONFIG[core.CFG_SHOW_FRIENDS]:
        OUT.append('---')
        if user['invites']['friends'] > 0:
            OUT.append(formatters.format_friends(user['invites']['friends']))

    # Cards
    if CONFIG[core.CFG_SHOW_CARDS]:
        OUT.append('---')
        OUT.append('💳 Карты')
        for card in user['accounts']:
            OUT.append(formatters.format_money(card['balance'], card['currency']) + ' (' + card['title'] + ')')

            OUT.append('-- ' + card['pan'] + ' (до ' +  str(card['month']) + '/' + str(card['year']) + ')')
            OUT.append('--  ' + formatters.format_money(card['balance'], card['currency']) + '')
            OUT.append('-----')

            # Tariff
            tariff = card['current_tariff']
            OUT.append('-- Тариф - ' + tariff['name'] + '|href=' + tariff['url'])

            # Limits
            OUT.append('-- Лимиты|size=14')
            for limits_group in card['better_limits']:
                OUT.append('-------')
                OUT.append('---- ' + limits_group[0] + ':')
                for limit_item in limits_group[1]:
                    OUT.append('---- ' + limit_item[0] + ' ' + limit_item[1])

    # Exchange
    if CONFIG[core.CFG_SHOW_EXCHANGE_RATES]:
        OUT.append('---')
        OUT.append('⚖️ Курс валют')
        OUT.append('1 ' + formatters.format_currency('USD') + ' = ' + str(user['rates']['card_usd']) + ' ' + formatters.format_currency('RUB'))
        OUT.append('1 ' + formatters.format_currency('EUR') + ' = ' + str(user['rates']['card_eur']) + ' ' + formatters.format_currency('RUB'))

    # Transactions
    if CONFIG[core.CFG_SHOW_LATEST_TRANSACTIONS]:
        OUT.append('---')
        OUT.append('🍷 Последние операции')

        if IS_FEED_OK:
            transactions = list(filter(lambda item: item[1]['visible'] and item[0] == 'operation', feed_json['feed']))

            for t in transactions[:5]:
                OUT.append(formatters.format_transaction(t))
                details = formatters.format_transaction_details(t)
                for detail in details:
                    OUT.append(
                        formatters.format_sub_level(detail, 2)
                    )

            OUT.append('Ещё')
            for t in transactions[5:]:
                OUT.append(
                    formatters.format_sub_level(
                        formatters.format_transaction(t),
                        2
                    )
                )
                details = formatters.format_transaction_details(t)
                for detail in details:
                    OUT.append(formatters.format_sub_level(detail, 3))
        else:
            OUT.append('Ошибка :(')


    # Support
    if CONFIG[core.CFG_SHOW_SUPPORT]:
        OUT.append('---')
        OUT.append('👩‍🚀 Поддержка')
        OUT.append('-- 8 (800) 200-07‑08 - по России')
        OUT.append('-- +7 (495) 133-07‑08 - из-за границы')

    # Output
    for info_string in OUT:
        print(info_string)
else:
    # todo: добавить запускатор установщика
    print('Мы не смогли войти')
    print('Возможно, вы сменили код от приложения')
    print('Запустите установщик заново')
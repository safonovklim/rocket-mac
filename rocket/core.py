import time
import requests
import base64
import hashlib
import os
import uuid
import json

CONFIG_FILE_NAME = os.path.dirname(os.path.realpath(__file__)) + '/my.cfg'
PROFILE_JSON_FILE_NAME = os.path.dirname(os.path.realpath(__file__)) + '/_profile.json'
FEED_JSON_FILE_NAME = os.path.dirname(os.path.realpath(__file__)) + '/_feed.json'

APP_VERSION = '1.0.1'
APP_BUILD = 2
APP_LINK_GITHUB = 'https://github.com/safonovklim/rocket-mac'
APP_LINK_TELEGRAM = 'https://t.me/rocket_mac'
APP_LATEST_VERSION_URL = 'https://raw.githubusercontent.com/safonovklim/rocket-mac/master/LATEST_BUILD.json'


API_HOST = 'https://rocketbank.ru/api/v5/'
APN_TOKEN = '0c2c476d4c5dd54b6b429bd9c00159f36f50b13338df728326e8fb8976936330'

API_ROUTE_LOGIN = 'login'
API_ROUTE_PROFILE = 'profile'
API_ROUTE_GET_TRANSACTIONS = 'operations/nano_feed'
API_ROUTE_REGISTER = 'devices/register'

CFG_SHOW_PUSH = 'CFG_SHOW_PUSH'
CFG_SHOW_FRIENDS = 'CFG_SHOW_FRIENDS'
CFG_SHOW_CARDS = 'CFG_SHOW_CARDS'
CFG_SHOW_SAFE_ACCOUNTS = 'CFG_SHOW_SAFE_ACCOUNTS'
CFG_SHOW_DEPOSITS = 'CFG_SHOW_DEPOSITS'
CFG_SHOW_EXCHANGE_RATES = 'CFG_SHOW_EXCHANGE_RATES'
CFG_SHOW_LATEST_TRANSACTIONS = 'CFG_SHOW_LATEST_TRANSACTIONS'
CFG_EXPIRED_TOKEN_TIMEOUT = 'CFG_EXPIRED_TOKEN_TIMEOUT'
CFG_AUTH_LOGIN = 'CFG_AUTH_LOGIN'
CFG_AUTH_PASSCODE = 'CFG_AUTH_PASSCODE'
CFG_DEVICE_ID = 'CFG_DEVICE_ID'
CFG_USER_CONFIGURED = 'CFG_USER_CONFIGURED'
CFG_TOKEN_UNSUCCESSFUL_USAGE = 'CFG_TOKEN_UNSUCCESSFUL_USAGE'
CFG_USER_TOKEN = 'CFG_USER_TOKEN'
CFG_TOKEN_MAX_UNSUCCESSFUL_USAGE = 'CFG_TOKEN_MAX_UNSUCCESSFUL_USAGE'

# ===================================================================================================
# Configuration file
# ===================================================================================================


def read_file_config():
    with open(CONFIG_FILE_NAME, "r") as f:
        content = f.readlines()

    content = [x.strip() for x in content]

    file_config = {}

    for line in content:
        key, value = line.split('=')
        file_config[key] = value

    f.close()

    return file_config


def write_file_config(config):
    new_config = {}

    current_config = read_file_config()
    for key, value in current_config.items():
        new_config[key] = value
    for key, value in config.items():
        new_config[key] = value

    f = open(CONFIG_FILE_NAME, 'w+')

    for key, value in new_config.items():
        f.write(str(key) + "=" + str(value) + "\n")

    f.close()
    return new_config


def parse_cfg_string(key, config):
    return str(config[key]) if key in config else ''


def parse_cfg_bool(key, config):
    return config[key] == '1' if key in config else False


def parse_cfg_int(key, config):
    return int(config[key]) if key in config else 0


def get_config():
    file_config = read_file_config()
    config = {
        CFG_SHOW_PUSH: False,
        CFG_SHOW_FRIENDS: False,
        CFG_SHOW_CARDS: True,
        CFG_SHOW_SAFE_ACCOUNTS: True,
        CFG_SHOW_DEPOSITS: True,
        CFG_SHOW_EXCHANGE_RATES: True,
        CFG_SHOW_LATEST_TRANSACTIONS: True,
        CFG_EXPIRED_TOKEN_TIMEOUT: 3600,
        CFG_TOKEN_MAX_UNSUCCESSFUL_USAGE: 2,
        CFG_AUTH_LOGIN: parse_cfg_string(CFG_AUTH_LOGIN, file_config),
        CFG_AUTH_PASSCODE: parse_cfg_int(CFG_AUTH_PASSCODE, file_config),
        CFG_DEVICE_ID: parse_cfg_string(CFG_DEVICE_ID, file_config),
        CFG_USER_CONFIGURED: parse_cfg_bool(CFG_USER_CONFIGURED, file_config),
        CFG_TOKEN_UNSUCCESSFUL_USAGE: parse_cfg_int(CFG_TOKEN_UNSUCCESSFUL_USAGE, file_config),
        CFG_USER_TOKEN: parse_cfg_string(CFG_USER_TOKEN, file_config),
    }
    return config


# ===================================================================================================
# API
# ===================================================================================================

def get_now_timestamp():
    ts = time.time()
    return str(ts).split('.')[0]


def get_signature_by_timestamp(ts):
    sig = hashlib.md5()
    string_to_encode = '0Jk211uvxyyYAFcSSsBK3+etfkDPKMz6asDqrzr+f7c=_' + ts + '_dossantos'
    sig.update(string_to_encode.encode())
    return sig.hexdigest()


def get_headers(custom_headers = {}):
    now = get_now_timestamp()
    signature = get_signature_by_timestamp(now)

    default_headers = {
        'x-app-version': '4.7.2 (73)',
        'x-device-os': 'iPhone OS 10.0',
        'x-device-id': get_config()[CFG_DEVICE_ID],
        'x-device-locale': 'en_RU',
        'x-time': now,
        'x-sig': signature,
    }

    headers = default_headers.copy()
    headers.update(custom_headers)

    return headers


def get_full_route(route):
    return API_HOST + route


def api_get(endpoint, options):
    route = get_full_route(endpoint)

    headers = get_headers(options['headers'] if 'headers' in options else {})
    query = options['query'] if 'query' in options else {}

    return requests.get(route, params=query, headers=headers)


def api_post(endpoint, options):
    route = get_full_route(endpoint)

    headers = get_headers(options['headers'] if 'headers' in options else {})
    query = options['query'] if 'query' in options else {}
    body = options['body'] if 'body' in options else {}

    return requests.post(route, params=query, headers=headers, data=body)


def api_patch(endpoint, options):
    route = get_full_route(endpoint)

    headers = get_headers(options['headers'] if 'headers' in options else {})
    query = options['query'] if 'query' in options else {}
    body = options['body'] if 'body' in options else {}

    return requests.patch(route, params=query, headers=headers, data=body)


def login(username, password):
    string_to_encode = username + ':' + str(password)
    encoded_auth_string = base64.b64encode(string_to_encode.encode()).decode('ascii')
    options = {
        'headers': {
            "Authorization": 'Basic ' + encoded_auth_string
        },
        'query': {
            'apn_token': APN_TOKEN
        }
    }
    return api_get(API_ROUTE_LOGIN, options)


def create_authorization_header_by_token(token):
    return 'Token token=' + token


def get_profile(token):
    options = {
        'headers': {
            "Authorization": create_authorization_header_by_token(token)
        },
        'query': {
            'apn_token': APN_TOKEN
        }
    }
    return api_get(API_ROUTE_PROFILE, options)


def get_transactions(token, page = 1, per_page = 10):
    options = {
        'headers': {
            "Authorization": create_authorization_header_by_token(token)
        },
        'query': {
            'page': page,
            'per_page': per_page
        }
    }
    return api_get(API_ROUTE_GET_TRANSACTIONS, options)


def register(phone_number):
    options = {
        'body': {
            'phone': phone_number,
            'apn_token': APN_TOKEN
        }
    }
    return api_post(API_ROUTE_REGISTER, options)


def api_verify_sms_code(challenge_id, code):
    route = 'sms_verifications/' + challenge_id + '/verify'
    options = {
        'body': {
            'code': str(code),
            'apn_token': APN_TOKEN
        }
    }
    return api_patch(route, options)


def is_response_ok(response):
    return response.status_code == requests.codes.ok


# ===================================================================================================
# Helpers
# ===================================================================================================

def collect_push(feed):
    return list(filter(lambda item: item[1]['visible'] and item[0] == 'push', feed))


def reset_device_id():
    file_config = read_file_config()
    file_config[CFG_DEVICE_ID] = uuid.uuid1()
    write_file_config(file_config)


def register_phone_number(phone_number):
    result = register(phone_number)
    result_ok = is_response_ok(result)
    if result_ok:
        return result_ok, result.json()['sms_verification']['id']
    else:
        return result_ok, result.json()['response']['description']


def verify_sms_code(challenge_id, code):
    result = api_verify_sms_code(challenge_id, code)
    result_ok = is_response_ok(result)
    if result_ok:
        return result_ok, result.json()
    else:
        return result_ok, result.json()['response']['description']


def confirm_app_code(login_token, passcode):
    result = login(login_token, passcode)
    result_ok = is_response_ok(result)
    if result_ok:
        return result_ok, result.json()
    else:
        return result_ok, result.json()['response']['description']


def is_update_available():
    response = requests.get(APP_LATEST_VERSION_URL)

    if is_response_ok(response):
        response_json = response.json()
        if response_json['build'] > APP_BUILD:
            return True, response_json

    return False, {}


def is_login_required(config):
    if not config[CFG_USER_TOKEN]:
        return True
    if config[CFG_TOKEN_UNSUCCESSFUL_USAGE] >= config[CFG_TOKEN_MAX_UNSUCCESSFUL_USAGE]:
        return True
    return False

# ===================================================================================================
# JSON cache files
# ===================================================================================================


def read_json(file):
    with open(file, "r") as f:
        data = json.load(f)

    f.close()
    return data


def write_json(data, file):
    with open(file, "w+") as f:
        json.dump(data, f)
    f.close()

import core

if __name__ == "__main__":
    new_device_id = core.reset_device_id()

    phone_number = input("Шаг 1 - Введите Ваш номер телефона (например: +79998765432): ")
    step1_ok, step1_meta = core.register_phone_number(phone_number)

    if step1_ok:
        sms_code = input("Шаг 2 - Введите код из смс: ")
        step2_ok, step2_meta = core.verify_sms_code(step1_meta, sms_code)

        if step2_ok:
            user = step2_meta['user']
            auth_login = user['login_token']

            app_code = input("Шаг 3 - Введите код приложения: ")
            step3_ok, step3_meta = core.confirm_app_code(auth_login, app_code)

            if step3_ok:
                core.write_file_config({
                    core.CFG_AUTH_LOGIN: auth_login,
                    core.CFG_AUTH_PASSCODE: app_code,
                    core.CFG_USER_CONFIGURED: '1'
                })

                print('Все отлично, ' + user['first_name'] + '!')
                print('Теперь Вы можете пользоваться Рокетбанком для Mac')
                print('Справа наверху нажмите BitBar -> Refresh all (Пункт "BitBar" скоро пропадет)\n\n')
                print('Можете закрыть это окно (Command + Q)\n\n\n\n')
            else:
                print(step3_meta)
                print('Попробуйте снова.')
        else:
            print(step2_meta)
            print('Попробуйте снова.')
    else:
        print(step1_meta)
        print('Попробуйте снова.')
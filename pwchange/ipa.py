import python_freeipa
import python_freeipa.exceptions

from pwchange import config


def pwchange(username, password, new_password, otp=None):
    client = python_freeipa.ClientMeta(config.ipa_server, verify_ssl=config.verify_ssl)

    try:
        try:
            client.login(username, password + (otp if otp else ''))
            if config.group and client.group_find(o_cn=config.group, o_user=username)['count'] == 0:
                raise RuntimeError('User {} not allowed to use utility'.format(repr(username)))
            client.passwd(a_principal=username, a_password=new_password, a_current_password=password)
            client.logout()
        except python_freeipa.exceptions.PasswordExpired:
            client.change_password(username, new_password, password + (otp if otp else ''))
    except python_freeipa.exceptions.Unauthorized as err:
        raise NameError('Unknown user or invalid password or one-time-password for username {}'.format(repr(username))) from err
    except python_freeipa.exceptions.BadRequest as err:
        raise ValueError('Password does not meet policy requirements: {}'.format(err)) from err
    except python_freeipa.exceptions.FreeIPAError as err:
        raise RuntimeError('Unexpected FreeIPA error: {}'.format(err)) from err
    except RuntimeError as err:
        raise ValueError('Checks failed: {}'.format(err)) from err
    except Exception as err:
        raise RuntimeError('Unexpected error: {}'.format(err)) from err

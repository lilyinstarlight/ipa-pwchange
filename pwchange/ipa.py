import python_freeipa
import python_freeipa.exceptions

from pwchange import config


def pwchange(username, password, new_password, otp=None):
    client = python_freeipa.ClientMeta(config.ipa_server, verify_ssl=config.verify_ssl)

    try:
        client.change_password(username=username, new_password=new_password, old_password=password, otp=otp)
    except python_freeipa.exceptions.PWChangeInvalidPassword as err:
        raise NameError('Unknown user or invalid password or one-time-password for username {}'.format(repr(username))) from err
    except python_freeipa.exceptions.PWChangePolicyError as err:
        raise ValueError('Password does not meet policy requirements: {}'.format(err.policy_error)) from err
    except python_freeipa.exceptions.FreeIPAError as err:
        raise RuntimeError('Unexpected FreeIPA error: {}'.format(err)) from err
    except Exception as err:
        raise RuntimeError('Unexpected error: {}'.format(err)) from err

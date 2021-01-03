import argparse
import importlib.util
import logging
import signal

from pwchange import config


def main():
    parser = argparse.ArgumentParser(description='start password change utility')
    parser.add_argument('-a', '--address', dest='address', help='address to bind')
    parser.add_argument('-p', '--port', type=int, dest='port', help='port to bind')
    parser.add_argument('-t', '--template', dest='template', help='template directory to use')
    parser.add_argument('-l', '--log', dest='log', help='log directory to use')
    parser.add_argument('-b', '--base', dest='base', help='base URL path to use')
    parser.add_argument('-s', '--ipa-server', dest='ipa_server', help='IPA server host')

    args = parser.parse_args()

    if args.address:
        config.addr = (args.address, config.addr[1])

    if args.port:
        config.addr = (config.addr[0], args.port)

    if args.template:
        config.template = args.template

    if args.log:
        if args.log == 'none':
            config.log = None
            config.http_log = None
        else:
            config.log = args.log + '/pwchange.log'
            config.http_log = args.log + '/http.log'

    if args.base:
        config.base = config_loaded.base
        if not config.base.startswith('/'):
            config.base = '/' + config.base
        if not config.base.endswith('/'):
            config.base = config.base + '/'

    if args.ipa_server:
        config.ipa_server = args.ipa_server

    config._apply()


    from pwchange import __version__
    from pwchange import http


    log = logging.getLogger('pwchange')

    log.info('pwchange ' + __version__ + ' starting...')

    # start everything
    http.start()


    # cleanup function
    def exit(signum, frame):
        http.stop()


    # use the function for both SIGINT and SIGTERM
    for sig in signal.SIGINT, signal.SIGTERM:
        signal.signal(sig, exit)

    # join against the HTTP server
    http.join()


if __name__ == '__main__':
    main()

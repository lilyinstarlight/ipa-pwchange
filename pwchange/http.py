import html
import logging

import fooster.web
import fooster.web.form
import fooster.web.page

from pwchange import config, ipa


http = None

routes = {}
error_routes = {}


log = logging.getLogger('pwchange')


class Interface(fooster.web.form.FormMixIn, fooster.web.page.PageHandler):
    directory = config.template
    page = 'index.html'
    message = ''

    def format(self, page):
        return page.format(message=self.message, username=html.escape(self.request.body.get('username', '') if self.method == 'post' else ''))

    def do_post(self):
        try:
            username = self.request.body['username'].strip().lower()
            password = self.request.body['password']
            otp = self.request.body['otp']
            new_password = self.request.body['new_password']
            verify_password = self.request.body['verify_password']
        except (KeyError, TypeError):
            raise fooster.web.HTTPError(400)

        try:
            if new_password == verify_password:
                ipa.pwchange(username=username, password=password, otp=otp, new_password=new_password)

                self.message = 'Successfully changed password'
            else:
                self.message = 'New password and verify password do not match'
        except (NameError, ValueError, RuntimeError) as err:
            log.warn('Error occured while trying to change password: {}'.format(err))

            self.message = str(err)
        except Exception:
            log.exception('Caught exception while trying to change password')

            self.message = 'Unexpected error occured'

        return self.do_get()


class ErrorInterface(fooster.web.page.PageErrorHandler):
    directory = config.template
    page = 'error.html'


routes.update({config.base: Interface})
error_routes.update(fooster.web.page.new_error(handler=ErrorInterface))


def start():
    global http

    http = fooster.web.HTTPServer(config.addr, routes, error_routes)
    http.start()


def stop():
    global http

    http.stop()
    http = None


def join():
    global http

    http.join()

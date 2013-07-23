from packages.gaesessions import SessionMiddleware

COOKIE="c4047563e84e0dab8ddfbf78780542e59713396005fa232ec017e5a852eb7d687f28ff4b341f2802a4d597bd1357bdf14d4ba5c344c555b44cf55ed4f36d547c"


def webapp_add_wsgi_middleware(app):
    app = SessionMiddleware(app, cookie_key=COOKIE)
    return app
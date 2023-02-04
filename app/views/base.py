from app.controllers.main import MainController


def base(address):
    return MainController.init(address)

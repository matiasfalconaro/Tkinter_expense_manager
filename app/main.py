import logging

from config import setup_logging
from mvc.model import Model
from mvc.view import View
from mvc.controller import Controller

setup_logging()
logger = logging.getLogger(__name__)


def main():
    try:
        model = Model()
        controller = Controller(model)
        view = View(controller)

        controller.set_view(view)
        view.create_view()
    except Exception as e:
        logger.error(
            f"An error occurred during application initialization: {e}"
        )


if __name__ == "__main__":
    main()

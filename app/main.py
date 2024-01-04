from mvc.model import Model
from mvc.view import View
from mvc.controller import Controller


def main():
    try:
        model = Model()
        controller = Controller(model)
        view = View(controller)

        controller.set_view(view)
        view.create_view()
    except Exception as e:
        print(f"An error occurred during application initialization: {e}")


if __name__ == "__main__":
    main()

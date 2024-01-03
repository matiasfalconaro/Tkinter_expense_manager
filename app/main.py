from mvc.model import Model
from mvc.view import View
from mvc.controller import Controller


def main():

    model = Model()
    controller = Controller(model)
    # Create the View instance and pass the Controller reference to it
    view = View(controller)
    # Provide the View instance to the Controller
    controller.set_view(view)

    view.create_view()  # Start the application


if __name__ == "__main__":
    main()

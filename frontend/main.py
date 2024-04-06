from PySide2 import QtCore, QtGui, QtWidgets
import requests
from PySide2.QtWidgets import QDialogButtonBox
from typing import List
from dataclasses import dataclass
from enum import Enum, auto


class Role(Enum):
    PERSON_ROLE = QtCore.Qt.UserRole + 1
    ID_ROLE = QtCore.Qt.UserRole + 2


@dataclass(frozen=True)
class Person:
    id: int
    name: str


def get_persons() -> List[Person]:
    request_response: requests.Response = requests.get("http://127.0.0.1:8000/people")
    data = request_response.json()["people"]
    persons: List[Person] = [Person(int(person["id"]), person["name"]) for person in data]

    return sorted(persons, key=lambda person: person.name.lower())


def delete_persons(persons_id: List[int]):
    requests.delete("http://127.0.0.1:8000/player/remove", json={"ids": persons_id})  # [1, 2, 3]


class CreatePersonDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent,
                         f=QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle("Create new Person")

        label_name = QtWidgets.QLabel("Name")
        self.input_name = QtWidgets.QLineEdit()

        box_layout = QtWidgets.QHBoxLayout()
        box_layout.addWidget(label_name)
        box_layout.addWidget(self.input_name)

        button_box = QtWidgets.QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        button_box.accepted.connect(self.dialog_accepted)
        button_box.rejected.connect(self.dialog_cancelled)

        box_layout_3 = QtWidgets.QVBoxLayout(self)
        box_layout_3.addLayout(box_layout)
        box_layout_3.addWidget(button_box)

    @QtCore.Slot()
    def dialog_accepted(self):
        name = self.input_name.text()
        result: bool = self.create_person(name)
        if result:
            self.close()

    @QtCore.Slot()
    def dialog_cancelled(self):
        self.close()

    def create_person(self, name: str) -> bool:
        if name == "":
            QtWidgets.QMessageBox.warning(self, "Error", "Name cannot be empty")
            return False

        requests.post("http://127.0.0.1:8000/player/create/", json={"name": name})
        return True


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_persons_id: List[int] = []
        self.setWindowTitle('Wdinow')
        self.resize(QtGui.QGuiApplication.primaryScreen().availableGeometry().size() * 0.7)

        self.dialog = CreatePersonDialog()

        button_widget = QtWidgets.QPushButton("Create Person")
        button_widget.clicked.connect(self.open_person_create_dialog)

        label_widget = QtWidgets.QLabel("Persons")
        self.list_widget = QtWidgets.QListWidget(self)
        self.list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)

        self.update_list()

        v_box_layout = QtWidgets.QVBoxLayout()
        v_box_layout.addWidget(button_widget)
        v_box_layout.addWidget(label_widget)
        v_box_layout.addWidget(self.list_widget)

        main_widget = QtWidgets.QWidget()
        main_widget.setLayout(v_box_layout)

        self.setCentralWidget(main_widget)

    @QtCore.Slot()
    def open_person_create_dialog(self):
        self.dialog.exec_()
        self.update_list()

    @QtCore.Slot()
    def on_selection_changed(self):
        self.selected_persons_id = [selected_item.data(Role.ID_ROLE.value) for selected_item in
                                    self.list_widget.selectedItems()]

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        key_combination = [event.key(), event.modifiers()]
        match key_combination:
            case [QtCore.Qt.Key_Delete, QtCore.Qt.NoModifier]:
                delete_persons(self.selected_persons_id)
                self.update_list()
            case [QtCore.Qt.Key_A, *_]:
                print("Voila")
            case _:
                #https://www.youtube.com/watch?v=ij0XZ3BbvlQ&t=3s
                pass


    def update_list(self):
        self.list_widget.clear()
        persons: List[Person] = get_persons()
        for person in persons:
            item = QtWidgets.QListWidgetItem()
            item.setData(QtCore.Qt.DisplayRole, person.name)
            item.setData(Role.PERSON_ROLE.value, person)
            item.setData(Role.ID_ROLE.value, person.id)
            self.list_widget.addItem(item)


def main():
    app = QtWidgets.QApplication()
    window = MainWindow()

    window.show()
    app.exec_()


if __name__ == '__main__':
    main()

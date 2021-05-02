import sys
import datetime
import pyperclip
import random
import json
import string
import os
from PyQt5 import uic
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt5.QtWidgets import QTableWidgetItem, QTreeWidgetItem
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView


class PyPass(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.setFixedSize(990, 600)
        self.table.setRowCount(0)
        self.table.setColumnCount(6)
        self.table.resizeRowsToContents()
        self.table.resizeColumnsToContents()
        # allData - все данные базы с которой работает программа
        self.allData = {}
        # data - данные которые вы добавляете в программу
        self.data = ''
        # иконка внимание
        self.image = QImage('icons/warning.png')
        q = Qt.SmoothTransformation
        self.pixmap = QPixmap(self.image).scaledToHeight(32, q)
        self.treeWidget.hide()
        self.table.verticalHeader().setVisible(False)
        # кнопки меню
        self.open.triggered.connect(self.openning)
        self.add.triggered.connect(self.adding)
        self.exit.triggered.connect(self.closing)
        self.save.triggered.connect(self.saving)
        self.add_data.triggered.connect(self.adding_data)
        self.passwordgenerator.triggered.connect(self.passwordgenerating)
        self.edit.triggered.connect(self.editing)
        self.helper.triggered.connect(self.helping)
        # реакция на клик мыши
        self.treeWidget.itemClicked.connect(self.changer_tree)
        # self.table.itemClicked.connect(self.changer_table)
        self.enabled_false()

    # открыть
    def openning(self):
        try:
            self.file = QFileDialog.getOpenFileName(self, 'Открыть',
                                                    'База данных',
                                                    "Text files (*.json)")[0]
            self.file_name = self.file.split('/')[-1]
            if len(self.file_name) != 0:
                self.allData = {}
                self.from_json()
                self.add_to_tree()
                self.treeWidget.show()
                self.enabled_true()
                self.treeWidget.setHeaderLabels((f"{self.file_name}".split('.json')[0],))
        except:
            pass

    # создать
    def adding(self):
        try:
            self.file = QFileDialog.getSaveFileName(self, 'Сохранить', 'База данных', "Text files (*.json)")[0]
            self.file_name = self.file.split('/')[-1]
            self.table.setRowCount(0)
            if len(self.file_name) != 0:
                self.allData = {}
                self.add_to_tree()
                self.treeWidget.show()
                self.enabled_true()
        except:
            pass

    # выйти
    def closing(self):
        try:
            if not self.isSaved:
                isSaved = QMessageBox()
                isSaved.setWindowIcon(QIcon('icons/main.png'))
                isSaved.setWindowTitle(' ')
                isSaved.setIconPixmap(self.pixmap)
                isSaved.setText('Имеются несохраненные изменения.')
                isSaved.setInformativeText(f'Сохранить или закрыть?')
                isSaved.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                res = isSaved.exec_()
                if res == QMessageBox.Ok:
                    self.to_json()
                    self.saving_status(True)
                    self.close()
            else:
                self.close()
        except:
            self.close()

    # сохранить
    def saving(self):
        try:
            self.to_json()
            self.saving_status(True)
        except:
            pass

    # добавить данные
    def adding_data(self):
        self.dialog = AddData()
        self.dialog.show()
        self.dialog.exec_()
        self.data = self.dialog.data
        if self.data is not None:
            self.to_AllData()
            self.add_to_tree()
            self.saving_status(False)

    # сгенерировать пароль
    def passwordgenerating(self):
        self.p = PasswordGenerator()
        self.p.show()

    # редактор
    def editing(self):
        self.e = Editor(self.allData)
        self.e.show()
        self.e.exec_()
        try:
            self.allData = eval(self.e.data)
            self.view_data
        except:
            self.allData = dict()
        self.add_to_tree()
    def helping(self):
        self.h = Help()
        self.h.show()

    # включение / выключение / статус сохранения
    def enabled_false(self):
        self.add_data.setEnabled(False)
        self.edit.setEnabled(False)
        self.save.setEnabled(False)

    def enabled_true(self):
        self.add_data.setEnabled(True)
        self.edit.setEnabled(True)
        self.save.setEnabled(True)

    def saving_status(self, isSaved):
        self.isSaved = isSaved
        if not isSaved:
            self.setWindowTitle('PyPass * ')
        else:
            self.setWindowTitle('PyPass')

    # таблицы
    def view_info(self, from_all_data):
        name = from_all_data['name']
        login = from_all_data['login']
        password = from_all_data['password']
        url = from_all_data['url']
        time = from_all_data['time']
        notes = from_all_data['notes']
        group = from_all_data['group']
        self.info.setText('<html><b>Название: </b>' + name +
                          '; <b>Логин: </b>' + login +
                          '; <b>Пароль: </b>' + password +
                          '; <b>URL:</b> <a href=' + ';>' + url +
                          '</a>; <b>Группа: </b>' + group +
                          '; <b>Дата создания: </b>' + time +
                          '<br><b>Заметки: </b>' + notes + '</html>')

    def view_data(self, from_all_data):
        count = self.table.rowCount() + 1
        c1 = count - 1
        self.table.setRowCount(count)
        self.table.setItem(c1, 0, QTableWidgetItem(from_all_data['name']))
        self.table.setItem(c1, 1, QTableWidgetItem(from_all_data['login']))
        self.table.setItem(c1, 2, QTableWidgetItem(from_all_data['password']))
        self.table.setItem(c1, 3, QTableWidgetItem(from_all_data['url']))
        self.table.setItem(c1, 4, QTableWidgetItem(from_all_data['notes']))
        self.table.setItem(c1, 5, QTableWidgetItem(from_all_data['group']))

    # "дерево"
    def add_to_tree(self):
        self.treeWidget.clear()
        for key, val in self.allData.items():
            g = QTreeWidgetItem(self.treeWidget, [key])
            for i in val:
                it = QTreeWidgetItem(g, [i['name']])

    def changer_tree(self, item):
        isChild = item.childCount()
        item_text = item.text(self.treeWidget.indexFromItem(item).column())
        item_index = self.treeWidget.indexFromItem(item).row()
        if isChild == 0:
            p_text = item.parent().text(self.treeWidget.indexFromItem(item).column())
            self.table.setRowCount(0)
            self.view_data(self.allData[p_text][item_index])
            self.view_info(self.allData[p_text][item_index])
        if isChild > 0:
            p_text = item.text(self.treeWidget.indexFromItem(item).column())
            self.table.setRowCount(0)
            self.info.setText('')
            for i in self.allData[p_text]:
                self.view_data(i)
                #self.view_info(i)

    # распаковка
    def to_AllData(self): 
        object_d = self.data['group']
        if object_d not in self.allData:
            self.allData[object_d] = []
            self.allData[object_d].append(self.data)
        else:
            self.allData[object_d].append(self.data)

    def to_json(self):
        with open(f"{self.file_name}", "w", encoding="utf-8") as file:
            json.dump(self.allData, file)

    def from_json(self):
        self.allData = {}
        with open(self.file_name, 'r') as file:
            self.allData = json.loads(file.read())


class AddData(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('add_data.ui', self)
        self.data = None
        # иконка внимание
        self.image = QImage('icons/warning.png')
        q = Qt.SmoothTransformation
        self.pixmap = QPixmap(self.image).scaledToHeight(32, q)
        # генерировать пароль
        self.passwordGeneratorButton.clicked.connect(self.pw)
        # оk
        self.ok.pressed.connect(self.get_data)
        # cancel
        self.cancel.pressed.connect(self.canceling)

    # запуск генерации пароля
    def pw(self):
        self.p = PasswordGenerator()
        self.p.show()
        self.p.exec_()
        try:
            self.password.setText(self.p.pword)
        except AttributeError:
            self.password.setText('')

    # отмена
    def canceling(self):
        self.data = None
        self.close()

    def get_data(self):
        today = datetime.datetime.today()
        self.data = {
            'name': self.name.text(),
            'login': self.login.text(),
            'password': self.password.text(),
            'url': self.url.text(),
            'time': today.strftime("%d.%m.%Y %H:%M:%S"),
            'notes': self.notes.toPlainText(),
            'group': self.group.text().capitalize()
            }
        # если проверка поля "Пароль" не пройдена
        if not self.checker_pass():
            passwordErrorMessage = QMessageBox()
            passwordErrorMessage.setWindowIcon(QIcon('icons/main.png'))
            passwordErrorMessage.setWindowTitle(' ')
            passwordErrorMessage.setIconPixmap(self.pixmap)
            passwordErrorMessage.setText('<html><b style="font-size: 13px;">'
                                         'Введите пароль!</b</html>')
            passwordErrorMessage.setInformativeText('Нажмите на "..."'
                                                    '(справа от поля'
                                                    '"Пароль"),'
                                                    'чтобы сгенерировать '
                                                    'пароль.')
            passwordErrorMessage.exec_()
        # если все нужные элементы присутствуют, закрываем окно
        if all([self.checker_pass(), self.checker_group()]):
            self.close()

    # проверка поля "Пароль" на отсутствие
    def checker_pass(self):
        password = self.data['password']
        if len(password) != 0:
            return True
        else:
            return False

    # проверка поля "Группа" на отсутствие.
    # если поле Группа пустое, задаем название Untitled
    def checker_group(self):
        if len(self.data['group']) == 0:
            self.data['group'] = 'Untitled'
        return True


class PasswordGenerator(QDialog):
    def __init__(self):
            super().__init__()
            uic.loadUi('passwordgenerator.ui', self)
            self.setFixedSize(740, 160)
            # иконка 'ok'
            self.image = QImage('icons/ok.png')
            q = Qt.SmoothTransformation
            self.pixmap = QPixmap(self.image).scaledToHeight(32, q)
            # копирование
            self.copyingButton.clicked.connect(self.clipboard)
            # генерация
            self.generatingButton.clicked.connect(self.checker)
            # слайдер длины пароля
            self.lenghtSlider.valueChanged[int].connect(self.changeValue)

    # создание пароля на основе условий с использованием библиотеки string
    def checker(self):
        if self.digits.isChecked() and self.symbols.isChecked():
            self.generator(string.digits + string.punctuation +
                           string.ascii_lowercase + string.ascii_uppercase)
        elif self.digits.isChecked():
            self.generator(string.ascii_lowercase +
                           string.ascii_uppercase + string.digits)
        elif self.symbols.isChecked():
            self.generator(string.ascii_lowercase +
                           string.ascii_uppercase + string.punctuation)
        else:
            self.generator(string.ascii_lowercase + string.ascii_uppercase)
        self.password.setText(self.pword)

    # генератор пароля
    def generator(self, string):
        self.pword = ''
        for i in range(int(self.lenght.text())):
            self.pword += random.choice(string)

    # копирование пароля
    def clipboard(self):
        pyperclip.copy(self.password.text())
        # сообщение о копировании пароля
        inClipboardMessage = QMessageBox()
        inClipboardMessage.setWindowIcon(QIcon('icons/ok.png'))
        inClipboardMessage.setWindowTitle(' ')
        inClipboardMessage.setIconPixmap(self.pixmap)
        inClipboardMessage.setText('<html><b style="font-size: 13px;">'
                                   'Скопировано!</b</html>')
        inClipboardMessage.setInformativeText('<html>Ваш сгенериро'
                                              'ванный пароль:<br><b>' +
                                              self.password.text() +
                                              '</b> скопирован.</html>')
        inClipboardMessage.exec_()

    def changeValue(self, value):
        self.lenght.setText(str(value))


class Editor(QDialog):
    def __init__(self, data):
        super().__init__()
        uic.loadUi('editor.ui', self)
        self.setFixedSize(570, 628)
        self.data = data
        self.textEdit.setText(str(self.data))
        self.save.clicked.connect(self.saving)
        self.cancel.clicked.connect(self.canceling)

    def saving(self):
        self.data = self.textEdit.toPlainText()
        self.close()

    def canceling(self):
        self.close()

class Help(QMainWindow): 
    def __init__(self ):
        super(QMainWindow, self).__init__()
        self.setWindowTitle('Помощь')
        self.setFixedSize(990, 600)
        self.setWindowIcon(QIcon('icons/main.png'))
        self.browser = QWebEngineView()  
        d = os.path.dirname(os.path.abspath(__file__))
        url = d.replace("\\", '/') + '/help.html'
        self.browser.load(QUrl(url))  
        self.setCentralWidget(self.browser)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PyPass()
    ex.show()
    sys.exit(app.exec_())

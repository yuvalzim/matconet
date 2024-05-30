from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import pickle
import process_check
from consts import *
import protocol as protocol
import time
import server_side.filesUtil as filesUtil


class Ui_Form(object):
    def setupUi(self, form, ip, sock, obj):
        self.obj = obj
        self.sock = sock
        self.form = form
        self.ip = ip
        self.form.setObjectName("Form")
        self.form.resize(756, 606)
        self.label = QtWidgets.QLabel(self.form)
        self.label.setGeometry(QtCore.QRect(180, 30, 331, 101))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(True)
        font.setUnderline(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(self.form)
        self.pushButton.setGeometry(QtCore.QRect(100, 130, 541, 81))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.initiate_scan)
        self.pushButton_2 = QtWidgets.QPushButton(self.form)
        self.pushButton_2.setGeometry(QtCore.QRect(100, 230, 541, 81))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.show_quarantine_folder)
        self.pushButton_3 = QtWidgets.QPushButton(self.form)
        self.pushButton_3.setGeometry(QtCore.QRect(100, 330, 541, 81))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_2")
        self.pushButton_3.clicked.connect(self.show_processes)
        self.retranslateUi(self.form)
        QtCore.QMetaObject.connectSlotsByName(self.form)

        self.widgets = QtWidgets.QStackedWidget()
        self.widgets.addWidget(self.form)
        self.widgets.setFixedWidth(756)
        self.widgets.setFixedHeight(606)
        self.widgets.show()

    def initiate_scan(self):
        request = self.obj.encryption("START_SCAN")
        protocol.send_data(self.sock, request)
        disc_names_encrypted = self.sock.recv(BUFFER_SIZE)
        disc_names_pickled = self.obj.decryption(disc_names_encrypted)
        disc_names = pickle.loads(disc_names_pickled)
        print(disc_names)
        self.scan_win = ScanWin()
        self.scan_win.start_ui(self.widgets, self.sock, self.obj, disc_names, False)
        self.widgets.addWidget(self.scan_win)
        self.widgets.setCurrentIndex(self.widgets.currentIndex() + 1)

    def show_quarantine_folder(self):
        request = self.obj.encryption("VIEW_QUARANTINE")
        protocol.send_data(self.sock, request)
        files_encrypted = protocol.get_data(self.sock)
        file_names_pickled = self.obj.decryption(files_encrypted)
        file_names = pickle.loads(file_names_pickled)
        self.scan_win = ScanWin()
        self.scan_win.start_ui(self.widgets, self.sock, self.obj, file_names, True)
        self.widgets.addWidget(self.scan_win)
        self.widgets.setCurrentIndex(self.widgets.currentIndex() + 1)

    def show_processes(self):
        protocol.send_data(self.sock, self.obj.encryption("PROCESS_CHECK"))
        print(self.widgets.__len__())
        self.form.close()
        self.proc_win = ProcessWin()
        self.proc_win.start_ui(self.widgets, self.sock, self.obj)
        self.widgets.addWidget(self.proc_win)
        self.widgets.setCurrentIndex(self.widgets.currentIndex() + 1)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", f"Options for {self.ip}"))
        self.pushButton.setText(_translate("Form", "Scan files"))
        self.pushButton_2.setText(_translate("Form", "Manage quarantine folder"))
        self.pushButton_3.setText(_translate("Form", "Check processes"))


class ScanWin(QtWidgets.QWidget):
    def start_ui(self, widget, sock, obj, content, is_quarantine):
        self.content = content
        self.current_content = ""
        self.obj = obj
        self.sock = sock
        self.widget = widget
        font = QtGui.QFont()
        font.setPointSize(16)

        self.selected_index = -1
        self.formlayout = QtWidgets.QFormLayout()
        self.group_box = QtWidgets.QGroupBox("Folder content:")
        self.group_box.setAlignment(QtCore.Qt.AlignCenter)
        self.group_box.setFont(font)

        self.label_list = []
        self.button_list = []
        for i in range(len(self.content)):
            self.draw_box(font, i)

        self.group_box.setLayout(self.formlayout)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidget(self.group_box)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(400)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.scroll)
        self.setLayout(self.layout)

        self.back_button = QtWidgets.QPushButton(self)
        self.back_button.setGeometry(QtCore.QRect(325, 520, 100, 50))
        self.back_button.setText("Go back")
        self.back_button.clicked.connect(self.go_back)

        b1_text = "Scan"
        b2_text = "Select"
        if is_quarantine:
            b1_text = "Delete"
            b2_text = "Restore"

        self.scan_button = QtWidgets.QPushButton(self)
        self.scan_button.setGeometry(QtCore.QRect(175, 520, 100, 50))
        self.scan_button.setText(b1_text)


        self.select_button = QtWidgets.QPushButton(self)
        self.select_button.setGeometry(QtCore.QRect(475, 520, 100, 50))
        self.select_button.setText(b2_text)

        if is_quarantine:
            self.delete_all = QtWidgets.QPushButton(self)
            self.delete_all.setGeometry(QtCore.QRect(50, 520, 100, 50))
            self.delete_all.setText("Delete all")


            self.restore_all = QtWidgets.QPushButton(self)
            self.restore_all.setGeometry(QtCore.QRect(600, 520, 100, 50))
            self.restore_all.setText("Restore all")

            self.delete_all.clicked.connect(lambda: self.delete_all_files())
            self.restore_all.clicked.connect(lambda: self.restore_all_files())
        else:
            self.scan_button.clicked.connect(lambda: self.scan_folder())
            self.select_button.clicked.connect(lambda: self.select_folder())

    def go_back(self):
        protocol.send_data(self.sock, self.obj.encryption("BACK"))
        self.close()
        self.widget.removeWidget(self)
        self.widget.setCurrentIndex(self.widget.currentIndex() - 1)

    def select_folder(self):
        msg = f"SELECT_DIR {self.current_content}"
        encrypted_msg = self.obj.encryption(msg)
        protocol.send_data(self.sock, encrypted_msg)
        folder_content_encrypted = protocol.get_data(self.sock)
        bytes_content = self.obj.decryption(folder_content_encrypted)
        folder_content = pickle.loads(bytes_content)
        print(self.content)
        if folder_content == "START_SCAN":
            self.scan_loading()
            return
        self.new_content_win(folder_content)

    def new_content_win(self, content):
        self.scan_win = ScanWin()
        self.scan_win.start_ui(self.widget, self.sock, self.obj, content, False)
        self.widget.addWidget(self.scan_win)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
        self.widget.removeWidget(self)
        self.close()

    def scan_folder(self):
        if not self.current_content:
            return
        msg = f"SCAN_DIR {self.current_content}"
        encrypted_msg = self.obj.encryption(msg)
        protocol.send_data(self.sock, encrypted_msg)
        folder_content_encrypted = protocol.get_data(self.sock)
        bytes_content = self.obj.decryption(folder_content_encrypted)
        folder_content = pickle.loads(bytes_content)
        self.scan_loading()

    def restore_file(self):
        if not self.current_content:
            return
        msg = f"RESTORE_FILE {self.current_content}"
        msg_encrypted = self.obj.encryption(msg)
        protocol.send_data(self.sock, msg_encrypted)

    def delete_file(self):
        if not self.current_content:
            return
        msg = f"DELETE_FILE {self.current_content}"
        msg_encrypted = self.obj.encryption(msg)
        protocol.send_data(self.sock, msg_encrypted)

    def delete_all_files(self):
        msg = "DELETE_ALL"
        msg_encrypted = self.obj.encryption(msg)
        protocol.send_data(self.sock, msg_encrypted)

    def restore_all_files(self):
        msg = "RESTORE_ALL"
        msg_encrypted = self.obj.encryption(msg)
        protocol.send_data(self.sock, msg_encrypted)

    def scan_loading(self):
        loading = loading_win()
        loading.start_ui(self.widget, self.sock, self.obj, self.current_content)
        self.widget.addWidget(loading)

        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
        self.widget.removeWidget(self)
        self.close()

    def draw_box(self, font, i):
        self.label_list.append(QtWidgets.QLabel(f"Name: {self.content[i]}"))
        self.button_list.append(QtWidgets.QPushButton(f"Select"))
        self.label_list[i].setFont(font)
        self.button_list[i].setFont(font)
        self.button_list[i].setStyleSheet("background-color : white")
        self.button_list[i].clicked.connect(lambda: self.highlight_button(i))
        self.formlayout.addRow(self.label_list[i], self.button_list[i])

    def highlight_button(self, i):
        if self.selected_index != -1:
            self.button_list[self.selected_index].setStyleSheet("background-color : white")
        self.button_list[i].setStyleSheet("background-color : blue")
        self.selected_index = i
        self.current_content = self.content[self.selected_index]


class loading_win(QtWidgets.QWidget):
    def start_ui(self, widget, sock, obj, content):
        self.currently_scanning = False
        self.obj = obj
        self.sock = sock
        self.widget = widget
        self.content = content
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.headline = QtWidgets.QLabel(self)
        self.headline.setGeometry(275, 100, 500, 50)
        self.headline.setText(f"Do you want to scan {content} ?")
        self.headline.setFont(font)

        self.check_box = QtWidgets.QCheckBox(self)
        self.check_box.setText("Scan sub directories")
        self.check_box.setGeometry(300, 250, 200, 20)

        self.button = QtWidgets.QPushButton(self)
        self.button.setGeometry(270, 300, 200, 50)
        self.button.setText("Start scan")
        self.button.clicked.connect(self.start_scan)

        self.back_button = QtWidgets.QPushButton(self)
        self.back_button.setGeometry(QtCore.QRect(325, 520, 100, 50))
        self.back_button.setText("Go back")
        self.back_button.clicked.connect(self.go_back)

    def go_back(self):
        if self.currently_scanning:
            return
        protocol.send_data(self.sock, self.obj.encryption("BACK"))
        self.close()
        self.widget.removeWidget(self)
        self.widget.setCurrentIndex(self.widget.currentIndex() - 1)

    def start_scan(self):
        if self.currently_scanning:
            return
        self.currently_scanning = True
        msg = self.content
        if self.check_box.isChecked():
            msg += " SUB"
        protocol.send_data(self.sock, self.obj.encryption(msg))
        self.pbar = QtWidgets.QProgressBar(self)
        self.pbar.setGeometry(300, 200, 200, 25)
        self.pbar.setValue(0)  # Set initial value to 0
        self.pbar.show()  # Show the progress bar
        QtWidgets.QApplication.processEvents()  # Process events to ensure UI updates

        while True:
            data = pickle.loads(self.obj.decryption(protocol.get_data(self.sock)))
            if type(data) is list:
                break
            else:
                self.pbar.setValue(int(data))
                QtWidgets.QApplication.processEvents()  # Process events to ensure UI updates

        self.pbar.close()
        self.button.close()
        self.check_box.close()
        self.headline.close()

        self.files = data

        font = QtGui.QFont()
        font.setPointSize(16)

        self.formlayout = QtWidgets.QFormLayout()
        self.group_box = QtWidgets.QGroupBox("Files:")
        self.group_box.setAlignment(QtCore.Qt.AlignCenter)
        self.group_box.setFont(font)

        self.label_list = []
        self.button_list = []
        for i in range(len(self.files)):
            self.draw_box(font, i)

        self.group_box.setLayout(self.formlayout)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidget(self.group_box)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(400)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.scroll)
        self.setLayout(self.layout)

        self.currently_scanning = False

    def draw_box(self, font, i):
        self.label_list.append(QtWidgets.QLabel(f"File: {self.files[i]}"))
        self.button_list.append(QtWidgets.QPushButton("Select"))
        self.label_list[i].setFont(font)
        self.button_list[i].setFont(font)
        self.button_list[i].clicked.connect(lambda: self.file_select(i))
        self.formlayout.addRow(self.label_list[i], self.button_list[i])

    def file_select(self, i):
        self.file_opt = File_options()
        self.file_opt.start_ui(self.widget, self.sock, self.obj, self.files[i])
        self.widget.addWidget(self.file_opt)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
        print(self.files[i])


class File_options(QtWidgets.QWidget):
    def start_ui(self, widget, socket, obj, file):
        self.widget = widget
        self.obj = obj
        self.socket = socket
        self.file_name = file
        self.proc_lable = QtWidgets.QLabel(self)
        self.proc_lable.setGeometry(QtCore.QRect(80, 40, 600, 50))
        self.proc_lable.setText(f"File: {file}")
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.proc_lable.setAlignment(QtCore.Qt.AlignCenter)
        self.proc_lable.setFont(font)

        self.back_button = QtWidgets.QPushButton(self)
        self.back_button.setGeometry(QtCore.QRect(325, 520, 100, 50))
        self.back_button.setText("Go back")
        self.back_button.clicked.connect(self.go_back)

        self.reduce_privs_button = QtWidgets.QPushButton(self)
        self.reduce_privs_button.setGeometry(120, 330, 200, 50)
        self.reduce_privs_button.setText("Delete file")
        self.reduce_privs_button.clicked.connect(self.delete_file)

        self.close_proc_button = QtWidgets.QPushButton(self)
        self.close_proc_button.setGeometry(425, 330, 200, 50)
        self.close_proc_button.setText("Move to quarantine")
        self.close_proc_button.clicked.connect(self.quarantine_file)

    def delete_file(self):
        msg = f"DELETE_FILE {self.file_name}"
        protocol.send_data(self.socket, self.obj.encryption(msg))

    def quarantine_file(self):
        msg = f"QUARANTINE_FILE {self.file_name}"
        protocol.send_data(self.socket, self.obj.encryption(msg))

    def go_back(self):
        self.widget.setCurrentIndex(self.widget.currentIndex() - 1)
        self.widget.removeWidget(self)


class ProcessWin(QtWidgets.QWidget):
    def start_ui(self, widget, sock, obj):
        self.obj = obj
        self.sock = sock
        self.widget = widget
        data = self.obj.decryption(self.sock.recv(BUFFER_SIZE))
        self.proc_dict = pickle.loads(data)
        font = QtGui.QFont()
        font.setPointSize(16)

        self.formlayout = QtWidgets.QFormLayout()
        self.group_box = QtWidgets.QGroupBox("Elevated processes:")
        self.group_box.setAlignment(QtCore.Qt.AlignCenter)
        self.group_box.setFont(font)

        self.label_list = []
        self.button_list = []
        for i in range(len(self.proc_dict)):
            self.draw_box(font, i)

        self.group_box.setLayout(self.formlayout)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidget(self.group_box)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(400)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.scroll)
        self.setLayout(self.layout)

        self.back_button = QtWidgets.QPushButton(self)
        self.back_button.setGeometry(QtCore.QRect(325, 520, 100, 50))
        self.back_button.setText("Go back")
        self.back_button.clicked.connect(self.go_to_main_screen)

    def draw_box(self, font, i):
        print(list(self.proc_dict.values())[i])
        self.label_list.append(QtWidgets.QLabel(f"PID: {str(list(self.proc_dict.values())[i])}"))
        self.button_list.append(QtWidgets.QPushButton(f"Process name: {list(self.proc_dict.keys())[i]}"))
        self.label_list[i].setFont(font)
        self.button_list[i].setFont(font)
        self.button_list[i].clicked.connect(lambda: self.clicked_proc(i))
        self.formlayout.addRow(self.label_list[i], self.button_list[i])

    def clicked_proc(self, index):
        self.proc_opt = ProcessOptions()
        self.proc_opt.start_ui(self.widget, list(self.proc_dict.keys())[index],
                               int(list(self.proc_dict.values())[index]), self.sock, self.obj)
        self.widget.addWidget(self.proc_opt)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)

    def go_to_main_screen(self):
        self.close()
        self.widget.removeWidget(self)
        self.widget.setCurrentIndex(0)


class ProcessOptions(QtWidgets.QWidget):
    def start_ui(self, widget, pname, pid, socket, obj):
        self.widget = widget
        self.obj = obj
        self.socket = socket
        self.pname = pname
        self.pid = pid

        self.proc_lable = QtWidgets.QLabel(self)
        self.proc_lable.setGeometry(QtCore.QRect(80, 40, 600, 50))
        self.proc_lable.setText(f"Process: {pname}")
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.proc_lable.setAlignment(QtCore.Qt.AlignCenter)
        self.proc_lable.setFont(font)

        self.back_button = QtWidgets.QPushButton(self)
        self.back_button.setGeometry(QtCore.QRect(325, 520, 100, 50))
        self.back_button.setText("Go back")
        self.back_button.clicked.connect(self.go_back)

        self.reduce_privs_button = QtWidgets.QPushButton(self)
        self.reduce_privs_button.setGeometry(120, 330, 200, 50)
        self.reduce_privs_button.setText("Reduce process privileges")
        self.reduce_privs_button.clicked.connect(self.reduce_privs)

        self.close_proc_button = QtWidgets.QPushButton(self)
        self.close_proc_button.setGeometry(425, 330, 200, 50)
        self.close_proc_button.setText("Close process")
        self.close_proc_button.clicked.connect(self.close_proc)

    def go_back(self):
        self.widget.setCurrentIndex(self.widget.currentIndex() - 1)
        self.widget.removeWidget(self)

    def reduce_privs(self):
        protocol.send_data(self.socket, self.obj.encryption(f"REDUCE_PRIVS {str(self.pid)}"))
        # process_check.disable_privs(self.pid)

    def close_proc(self):
        protocol.send_data(self.socket, self.obj.encryption(f"CLOSE_PROC {str(self.pid)}"))

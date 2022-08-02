import cv2
import os
import time
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import threading


class Ui(QtWidgets.QDialog):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('main.ui', self)
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())
        self.show()

        self.is_start = False
        self.btn_open.clicked.connect(self.clicked_open_btn)
        self.btn_proc.clicked.connect(self.clicked_proc_btn)
        self.btn_next.clicked.connect(self.clicked_next_btn)
        self.btn_prev.clicked.connect(self.clicked_prev_btn)
        self.btn_output.clicked.connect(self.clicked_output_btn)
        # #

        self.width = self.lbl_screen.geometry().width()
        self.height = self.lbl_screen.geometry().height()

    def clicked_open_btn(self):
        if self.is_start:
            return

        if self.cbox_src_type.currentIndex(): # file selection
            try:
                src_file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', './',
                                                                      filter="MP4 File(*.mp4);;AVI File(*.avi);;MOV File(*.mov);;H264 File(*.h264);;H265 File(*.265);;All Files(*.*)")[0]
                if (src_file_name is None or src_file_name == ""):
                    msg = QtWidgets.QMessageBox(self)
                    msg.setIcon(QtWidgets.QMessageBox.Critical)
                    msg.setText("Warning")
                    msg.setInformativeText('There are no any Video File in the Selected Directory.')
                    msg.setWindowTitle("Warning")
                    msg.exec_()
                else:

                    cap = cv2.VideoCapture(src_file_name)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret:
                            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            h, w, ch = rgbImage.shape
                            bytesPerLine = ch * w
                            image = QtGui.QImage(rgbImage.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)
                            p = image.scaled(self.width, self.height, Qt.KeepAspectRatio)
                            self.lbl_screen.setPixmap(QtGui.QPixmap(p))
                            cv2.waitKey(1)
                        cap.release()

                        self.lbl_total_cnt.setText('1')
                        self.lbl_cur_cnt.setText('1')
                        self.lbl_cur_file_path.setText(src_file_name)
                        self.btn_next.setEnabled(False)
                        self.btn_prev.setEnabled(False)

                        self.src_file_name = src_file_name

                    else:
                        msg = QtWidgets.QMessageBox(self)
                        msg.setIcon(QtWidgets.QMessageBox.Critical)
                        msg.setText("Warning")
                        msg.setInformativeText('Can not Open Video File.')
                        msg.setWindowTitle("Warning")
                        msg.exec_()
            except:
                print("Error in \'clicked_open_btn\'")
                exit(0)

        else:
            try:
                src_file_dir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select video directory')
                if (src_file_dir is None or src_file_dir == ""):
                    msg = QtWidgets.QMessageBox(self)
                    msg.setIcon(QtWidgets.QMessageBox.Critical)
                    msg.setText("Warning")
                    msg.setInformativeText('Please select the video source directory.')
                    msg.setWindowTitle("Warning")
                    msg.exec_()
                else:
                    files = os.listdir(src_file_dir)

                    video_files = [os.path.join(src_file_dir, file) for file in files if os.path.splitext(file)[1].lower() in [".mp4", ".avi", ".h264", ".265", ".mov"]]
                    if video_files.__len__() < 1:
                        msg = QtWidgets.QMessageBox(self)
                        msg.setIcon(QtWidgets.QMessageBox.Critical)
                        msg.setText("Warning")
                        msg.setInformativeText('There are no exist the video files in the current directory.')
                        msg.setWindowTitle("Warning")
                        msg.exec_()
                        return

                    self.video_files = video_files
                    self.cur_index = 0
                    self.lbl_total_cnt.setText(str(video_files.__len__()))
                    self.lbl_cur_cnt.setText(str(self.cur_index + 1))
                    self.lbl_cur_file_path.setText(video_files[0])

                    if video_files.__len__() < 2:
                        self.btn_next.setEnabled(False)
                    else:
                        self.btn_next.setEnabled(True)

                    self.src_file_name = video_files[0]

                    cap = cv2.VideoCapture(video_files[0])
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret:
                            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            h, w, ch = rgbImage.shape
                            bytesPerLine = ch * w
                            image = QtGui.QImage(rgbImage.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)
                            p = image.scaled(self.width, self.height, Qt.KeepAspectRatio)
                            self.lbl_screen.setPixmap(QtGui.QPixmap(p))
                            cv2.waitKey(1)
                        cap.release()

                    else:
                        msg = QtWidgets.QMessageBox(self)
                        msg.setIcon(QtWidgets.QMessageBox.Critical)
                        msg.setText("Warning")
                        msg.setInformativeText('Can not Open Video File.')
                        msg.setWindowTitle("Warning")
                        msg.exec_()
            except:
                print("Error in \'clicked_open_btn\'")
                exit(0)

    def clicked_output_btn(self):
        if self.is_start:
            return
        try:
            output_dir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select output directory')
            if (output_dir is None or output_dir == ""):
                msg = QtWidgets.QMessageBox(self)
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setText("Warning")
                msg.setInformativeText('Please select the output directory.')
                msg.setWindowTitle("Warning")
                msg.exec_()
            else:
                self.lbl_output_path.setText(output_dir)

                output_day_dir = os.path.join(output_dir, 'image-day')
                output_night_dir = os.path.join(output_dir, 'image-night')
                if not os.path.isdir(output_day_dir):
                    os.mkdir(output_day_dir)

                if not os.path.isdir(output_night_dir):
                    os.mkdir(output_night_dir)

                self.output_day_dir = output_day_dir
                self.output_night_dir = output_night_dir


                image_day = os.listdir(self.output_day_dir)
                image_night = os.listdir(self.output_night_dir)

                day_files = [file for file in image_day if os.path.splitext(file)[1].lower() == '.jpg']
                night_files = [file for file in image_night if os.path.splitext(file)[1].lower() == '.jpg']

                self.cnt_day = day_files.__len__()
                self.cnt_night = night_files.__len__()

                self.cnt_total = self.cnt_day + self.cnt_night

                self.lbl_cnt_total_image.setText(str(self.cnt_total))
                self.lbl_cnt_day.setText('D: ' + str(self.cnt_day))
                self.lbl_cnt_night.setText('N: ' + str(self.cnt_night))

        except:
            pass

    def next_prev(self, direct):
        if self.is_start:
            return
        self.btn_next.setEnabled(True)
        self.btn_prev.setEnabled(True)
        if direct:
            self.cur_index += 1
        else:
            self.cur_index -= 1
        if self.cur_index == self.video_files.__len__() - 1:
            self.btn_next.setEnabled(False)
        if self.cur_index == 0:
            self.btn_prev.setEnabled(False)

        self.lbl_cur_cnt.setText(str(self.cur_index + 1))
        self.lbl_cur_file_path.setText(self.video_files[self.cur_index])

        self.src_file_name = self.video_files[self.cur_index]
        cap = cv2.VideoCapture(self.src_file_name)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                image = QtGui.QImage(rgbImage.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)
                p = image.scaled(self.width, self.height, Qt.KeepAspectRatio)
                self.lbl_screen.setPixmap(QtGui.QPixmap(p))
                cv2.waitKey(1)
            cap.release()

    def clicked_next_btn(self):
        self.next_prev(True)

    def clicked_prev_btn(self):
        self.next_prev(False)

    def clicked_proc_btn(self):
        if self.is_start:

            self.btn_proc.setText("Start")
        else:
            try:
                if self.output_day_dir is None or self.output_day_dir == "" \
                        or self.output_night_dir is None or self.output_night_dir == "":
                    return
            except:
                return
            self.btn_proc.setText("Stop")

        self.is_start = not self.is_start

        self.thread = threading.Thread(target=self.process)
        self.thread.start()

    def process(self):

        cap = cv2.VideoCapture(self.src_file_name)
        if not cap.isOpened():
            self.is_start = False
            self.btn_proc.setText("Start")
            return

        skip_num = self.sbox_skip.value()
        cur_cnt = 1
        cnt_image = 0
        while self.is_start:
            ret, image = cap.read()
            if not ret:
                break
            if cur_cnt % skip_num:
                cur_cnt += 1
            else:
                cur_cnt = 1
                fname = str(int(time.time() * 100000))[5:]
                if self.cbox_day_night.currentIndex():
                    fname = os.path.join(self.output_night_dir, f"night_{fname}.jpg")
                    self.cnt_night += 1
                else:
                    fname = os.path.join(self.output_day_dir, f"day_{fname}.jpg")
                    self.cnt_day += 1
                self.cnt_total += 1
                cnt_image += 1
                cv2.imwrite(fname, image)

            self.lbl_cnt_total_image.setText(str(self.cnt_total))
            self.lbl_cnt_day.setText("D: " + str(self.cnt_day))
            self.lbl_cnt_night.setText("N: " + str(self.cnt_night))
            self.lbl_cnt_image.setText(str(cnt_image))

            rgbImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w
            image = QtGui.QImage(rgbImage.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)
            p = image.scaled(self.width, self.height, Qt.KeepAspectRatio)
            self.lbl_screen.setPixmap(QtGui.QPixmap(p))
            cv2.waitKey(10)

        self.is_start = False
        self.btn_proc.setText("Start")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
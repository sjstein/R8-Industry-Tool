# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'industryDetailDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QFormLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_IndustryDetailDialog(object):
    def setupUi(self, IndustryDetailDialog):
        if not IndustryDetailDialog.objectName():
            IndustryDetailDialog.setObjectName(u"IndustryDetailDialog")
        IndustryDetailDialog.resize(900, 700)
        self.verticalLayout = QVBoxLayout(IndustryDetailDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = QScrollArea(IndustryDetailDialog)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 878, 644))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.basicInfoGroup = QGroupBox(self.scrollAreaWidgetContents)
        self.basicInfoGroup.setObjectName(u"basicInfoGroup")
        self.formLayout = QFormLayout(self.basicInfoGroup)
        self.formLayout.setObjectName(u"formLayout")
        self.labelName = QLabel(self.basicInfoGroup)
        self.labelName.setObjectName(u"labelName")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelName)

        self.name_edit = QLineEdit(self.basicInfoGroup)
        self.name_edit.setObjectName(u"name_edit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.name_edit)

        self.labelLocalName = QLabel(self.basicInfoGroup)
        self.labelLocalName.setObjectName(u"labelLocalName")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelLocalName)

        self.local_name_edit = QLineEdit(self.basicInfoGroup)
        self.local_name_edit.setObjectName(u"local_name_edit")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.local_name_edit)

        self.labelSymbol = QLabel(self.basicInfoGroup)
        self.labelSymbol.setObjectName(u"labelSymbol")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelSymbol)

        self.symbol_edit = QLineEdit(self.basicInfoGroup)
        self.symbol_edit.setObjectName(u"symbol_edit")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.symbol_edit)

        self.labelProcessBlocks = QLabel(self.basicInfoGroup)
        self.labelProcessBlocks.setObjectName(u"labelProcessBlocks")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelProcessBlocks)

        self.process_blocks_check = QCheckBox(self.basicInfoGroup)
        self.process_blocks_check.setObjectName(u"process_blocks_check")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.process_blocks_check)


        self.verticalLayout_2.addWidget(self.basicInfoGroup)

        self.tracksGroup = QGroupBox(self.scrollAreaWidgetContents)
        self.tracksGroup.setObjectName(u"tracksGroup")
        self.verticalLayout_3 = QVBoxLayout(self.tracksGroup)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.tracks_table = QTableWidget(self.tracksGroup)
        if (self.tracks_table.columnCount() < 3):
            self.tracks_table.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.tracks_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tracks_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tracks_table.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.tracks_table.setObjectName(u"tracks_table")
        self.tracks_table.setColumnCount(3)

        self.verticalLayout_3.addWidget(self.tracks_table)

        self.trackButtonLayout = QHBoxLayout()
        self.trackButtonLayout.setObjectName(u"trackButtonLayout")
        self.remove_track_button = QPushButton(self.tracksGroup)
        self.remove_track_button.setObjectName(u"remove_track_button")

        self.trackButtonLayout.addWidget(self.remove_track_button)

        self.trackButtonSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.trackButtonLayout.addItem(self.trackButtonSpacer)


        self.verticalLayout_3.addLayout(self.trackButtonLayout)


        self.verticalLayout_2.addWidget(self.tracksGroup)

        self.producersGroup = QGroupBox(self.scrollAreaWidgetContents)
        self.producersGroup.setObjectName(u"producersGroup")
        self.verticalLayout_4 = QVBoxLayout(self.producersGroup)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.producers_table = QTableWidget(self.producersGroup)
        if (self.producers_table.columnCount() < 6):
            self.producers_table.setColumnCount(6)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.producers_table.setHorizontalHeaderItem(0, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.producers_table.setHorizontalHeaderItem(1, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.producers_table.setHorizontalHeaderItem(2, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.producers_table.setHorizontalHeaderItem(3, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.producers_table.setHorizontalHeaderItem(4, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.producers_table.setHorizontalHeaderItem(5, __qtablewidgetitem8)
        self.producers_table.setObjectName(u"producers_table")
        self.producers_table.setColumnCount(6)

        self.verticalLayout_4.addWidget(self.producers_table)


        self.verticalLayout_2.addWidget(self.producersGroup)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.buttonSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.buttonSpacer)

        self.save_button = QPushButton(IndustryDetailDialog)
        self.save_button.setObjectName(u"save_button")

        self.buttonLayout.addWidget(self.save_button)

        self.cancel_button = QPushButton(IndustryDetailDialog)
        self.cancel_button.setObjectName(u"cancel_button")

        self.buttonLayout.addWidget(self.cancel_button)


        self.verticalLayout.addLayout(self.buttonLayout)


        self.retranslateUi(IndustryDetailDialog)

        QMetaObject.connectSlotsByName(IndustryDetailDialog)
    # setupUi

    def retranslateUi(self, IndustryDetailDialog):
        IndustryDetailDialog.setWindowTitle(QCoreApplication.translate("IndustryDetailDialog", u"Industry Details", None))
        self.basicInfoGroup.setTitle(QCoreApplication.translate("IndustryDetailDialog", u"Industry information", None))
        self.labelName.setText(QCoreApplication.translate("IndustryDetailDialog", u"Name:", None))
        self.labelLocalName.setText(QCoreApplication.translate("IndustryDetailDialog", u"Local Name:", None))
        self.labelSymbol.setText(QCoreApplication.translate("IndustryDetailDialog", u"Track Symbol:", None))
        self.labelProcessBlocks.setText(QCoreApplication.translate("IndustryDetailDialog", u"Process in Blocks:", None))
        self.process_blocks_check.setText("")
        self.tracksGroup.setTitle(QCoreApplication.translate("IndustryDetailDialog", u"Tracks", None))
        ___qtablewidgetitem = self.tracks_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("IndustryDetailDialog", u"Route Prefix", None));
        ___qtablewidgetitem1 = self.tracks_table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("IndustryDetailDialog", u"Track Section", None));
        ___qtablewidgetitem2 = self.tracks_table.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("IndustryDetailDialog", u"Track Direction", None));
        self.remove_track_button.setText(QCoreApplication.translate("IndustryDetailDialog", u"Remove Selected Track", None))
        self.producersGroup.setTitle(QCoreApplication.translate("IndustryDetailDialog", u"Incoming cars", None))
        ___qtablewidgetitem3 = self.producers_table.horizontalHeaderItem(0)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("IndustryDetailDialog", u"ID", None));
        ___qtablewidgetitem4 = self.producers_table.horizontalHeaderItem(1)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("IndustryDetailDialog", u"Car Type", None));
        ___qtablewidgetitem5 = self.producers_table.horizontalHeaderItem(2)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("IndustryDetailDialog", u"Processed Tags", None));
        ___qtablewidgetitem6 = self.producers_table.horizontalHeaderItem(3)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("IndustryDetailDialog", u"Capacity", None));
        ___qtablewidgetitem7 = self.producers_table.horizontalHeaderItem(4)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("IndustryDetailDialog", u"Hours", None));
        ___qtablewidgetitem8 = self.producers_table.horizontalHeaderItem(5)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("IndustryDetailDialog", u"Produces", None));
        self.save_button.setText(QCoreApplication.translate("IndustryDetailDialog", u"Update", None))
        self.cancel_button.setText(QCoreApplication.translate("IndustryDetailDialog", u"Cancel", None))
    # retranslateUi


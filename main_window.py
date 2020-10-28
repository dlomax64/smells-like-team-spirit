import os
import sys
import time
import platform
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from app_widget import AppWidget
from permissions import check_permission, add_permission
from save_window import SaveWindow
from open_window import OpenWindow


FONT_SIZES = [5, 5.5, 6.5, 7.5, 8, 9, 10, 10.5, 11]
FONT_SIZES.extend(range(12, 30, 2))
FONT_SIZES.extend([36, 48, 72])


class MainWindow(QMainWindow):
    """ This class inherits from QMainWindow and will be used to set up the applications GUI """

    def __init__(self):
        super().__init__()

        # Global Variables
        # ================

        if 'Darwin' in platform.system():
            icon_size = 18

        else:
            icon_size = 36

        self.Edited = False

        self.setAcceptDrops(True)

        # Get screen resolution
        screenBounds = QDesktopWidget().screenGeometry(0)

        self.window_title = 'Notepad App - untitled.txt'
        self.setWindowTitle(self.window_title)

        self.setGeometry(0, 0, screenBounds.width() *
                         0.5, screenBounds.height() * 0.6)

        # Center the screen
        rect = self.frameGeometry()
        centerScreen = QDesktopWidget().availableGeometry().center()
        rect.moveCenter(centerScreen)
        self.move(rect.topLeft())

        # Set central widget for window
        self.centralWidget = AppWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.textBox.textChanged.connect(self.textEditedEvent)
        self.centralWidget.textBox.cursorPositionChanged.connect(
            self.cursorMovedEvent)
        self.centralWidget.textBox.mainWindow = self
        self.needsSave = False

        # Create save window and open window
        self.saveWindow = None
        self.openWindow = None

        # Begin menu bars
        # ===============

        # Define menu bar
        menuBar = self.menuBar()

        # Define status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # --------------------
        # Create File menu bar
        fileMenu = menuBar.addMenu('File')

        newButton = QAction('New', self)
        newButton.setShortcut('Ctrl+N')
        newButton.triggered.connect(lambda: self.openEvent(True))
        fileMenu.addAction(newButton)

        openButton = QAction('Open...', self)
        openButton.setShortcut('Ctrl+O')
        openButton.triggered.connect(lambda: self.openEvent(False))
        fileMenu.addAction(openButton)

        closeButton = QAction('Close', self)
        closeButton.setShortcut('Ctrl+W')
        closeButton.triggered.connect(lambda: self.closeEvent)
        fileMenu.addAction(closeButton)

        fileMenu.addSeparator()

        saveIcon = QIcon.fromTheme('document-save')
        saveButton = QAction(saveIcon, 'Save', self)
        saveButton.setShortcut('Ctrl+S')
        saveButton.triggered.connect(self.saveEvent)
        self.currentFile = ''
        fileMenu.addAction(saveButton)

        saveAsButton = QAction(saveIcon, 'Save As...', self)
        saveAsButton.setShortcut('Ctrl+Shift+S')
        saveAsButton.triggered.connect(self.saveAsEvent)
        fileMenu.addAction(saveAsButton)

        printButton = QAction(saveIcon, 'Print', self)
        printButton.setShortcut('Ctrl+P')
        printButton.triggered.connect(self.printEvent)
        fileMenu.addAction(printButton)

        # -------------------
        # Create Edit menu bar
        editMenu = menuBar.addMenu('Edit')

        undoButton = QAction('Undo', self)
        undoButton.setShortcut(QKeySequence.Undo)
        undoButton.triggered.connect(self.centralWidget.textBox.undo)
        editMenu.addAction(undoButton)

        redoButton = QAction('Redo', self)
        redoButton.setShortcut(QKeySequence.Redo)
        redoButton.triggered.connect(self.centralWidget.textBox.redo)
        editMenu.addAction(redoButton)

        editMenu.addSeparator()

        cutButton = QAction('Cut', self)
        cutButton.setShortcut(QKeySequence.Cut)
        cutButton.triggered.connect(self.centralWidget.textBox.cut)
        editMenu.addAction(cutButton)

        copyButton = QAction('Copy', self)
        copyButton.setShortcut(QKeySequence.Copy)
        copyButton.triggered.connect(self.centralWidget.textBox.copy)
        editMenu.addAction(copyButton)

        paste_action = QAction('Paste', self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.centralWidget.textBox.paste)
        editMenu.addAction(paste_action)

        editMenu.addSeparator()

        findButton = QAction('Find', self)
        findButton.setShortcut(QKeySequence.Find)
        findButton.triggered.connect(
            self.centralWidget.findWindow.createWindow)
        editMenu.addAction(findButton)

        searchSelectedActn = QAction('Find Using Selection', self)
        searchSelectedActn.setShortcut('Ctrl+E')
        searchSelectedActn.triggered.connect(self.SearchSelection)
        editMenu.addAction(searchSelectedActn)

        selectButton = QAction('Select All', self)
        selectButton.setShortcut(QKeySequence.SelectAll)
        selectButton.triggered.connect(self.centralWidget.textBox.selectAll)
        editMenu.addAction(selectButton)

        # ----------------------
        # Create Format menu bar
        formatMenu = menuBar.addMenu('Format')

        fontButton = QAction('Fonts...', self)
        fontButton.setShortcut('Ctrl+T')
        fontButton.triggered.connect(self.fontChoice)
        formatMenu.addAction(fontButton)

        self.centralWidget.textBox.setTextColor(
            Qt.black)  # Set initial text color HTML
        colorButton = QAction('Font Color...', self)
        colorButton.triggered.connect(self.colorPicker)
        formatMenu.addAction(colorButton)

        imageButton = QAction('Insert Image...', self)
        imageButton.triggered.connect(self.centralWidget.insertImage)
        formatMenu.addAction(imageButton)

        # Begin toolbars
        # ==============

        # --------------------
        # Create edit toolbar
        edit_toolbar = QToolBar("Edit")
        edit_toolbar.setIconSize(QSize(icon_size, icon_size))
        self.addToolBar(edit_toolbar)

        cut_action = QAction(
            QIcon(os.path.join('images', 'icons8-cut-80.png')), 'Cut', self)
        cut_action.setStatusTip('Cut Selected Text (Copy and Delete)')
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.centralWidget.textBox.cut)
        edit_toolbar.addAction(cut_action)

        copy_action = QAction(
            QIcon(os.path.join('images', 'icons8-copy-80.png')), 'Copy', self)
        copy_action.setStatusTip('Copy Selected Text to Clipboard')
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.centralWidget.textBox.copy)
        edit_toolbar.addAction(copy_action)

        paste_action = QAction(
            QIcon(os.path.join('images', 'icons8-paste-80.png')), 'Paste', self)
        paste_action.setStatusTip('Paste From Clipboard')
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.centralWidget.textBox.paste)
        edit_toolbar.addAction(paste_action)

        imageAction = QAction(
            QIcon(os.path.join('images', 'icons8-add-image-80.png')), 'Image', self)
        imageAction.setStatusTip('Insert an image')
        imageAction.triggered.connect(self.centralWidget.insertImage)
        edit_toolbar.addAction(imageAction)

        findAction = QAction(
            QIcon(os.path.join('images', 'icons8-search-80.png')), 'Find', self)
        findAction.setStatusTip('Open Find Text Window')
        findAction.setShortcut(QKeySequence.Find)
        findAction.triggered.connect(
            self.centralWidget.findWindow.createWindow)
        edit_toolbar.addAction(findAction)

        # -------------------
        # Create font toolbar
        font_toolbar = QToolBar("Font")
        font_toolbar.setIconSize(QSize(icon_size, icon_size))
        self.addToolBar(font_toolbar)

        self.fonts = QFontComboBox()
        self.fonts.currentFontChanged.connect(
            self.centralWidget.textBox.setCurrentFont)
        font_toolbar.addWidget(self.fonts)

        self.fontsize = QComboBox()
        self.fontsize.addItems([str(s) for s in FONT_SIZES])
        self.fontsize.setCurrentIndex(FONT_SIZES.index(16))
        self.fontsize.currentIndexChanged[str].connect(
            lambda s: self.centralWidget.textBox.setFontPointSize(float(s)))
        font_toolbar.addWidget(self.fontsize)

        FONT_COLORS = ["Black", "Red", "Green",
                       "Blue", "Yellow", "Gray", "Magenta"]

        self.fontcolor = QComboBox()
        self.fontcolor.addItems(FONT_COLORS)
        self.fontcolor.setCurrentIndex(FONT_COLORS.index("Black"))
        self.fontcolor.currentIndexChanged.connect(self.TextColor)
        font_toolbar.addWidget(self.fontcolor)

        # ---------------------
        # Create format toolbar
        format_toolbar = QToolBar("Format")
        format_toolbar.setIconSize(QSize(icon_size, icon_size))
        self.addToolBar(format_toolbar)

        self.colorLabel = QLabel()
        self.setColorIcon(Qt.black)
        format_toolbar.addWidget(self.colorLabel)

        colorAction = QAction(
            QIcon(os.path.join('images', 'icons8-text-color-80.png')), 'Font Color', self)
        colorAction.setStatusTip('Select Font Color')
        colorAction.triggered.connect(self.colorPicker)
        format_toolbar.addAction(colorAction)

        self.bold_action = QAction(
            QIcon(os.path.join('images', 'icons8-bold-80.png')), "Bold", self)
        self.bold_action.setStatusTip("Set selected text to Bold (strong)")
        self.bold_action.setShortcut(QKeySequence.Bold)
        self.bold_action.setCheckable(True)
        self.bold_action.toggled.connect(lambda x: self.centralWidget.textBox.setFontWeight(
            QFont.Bold if x else QFont.Normal))
        format_toolbar.addAction(self.bold_action)

        self.italic_action = QAction(
            QIcon(os.path.join('images', 'icons8-italic-80.png')), "Italic", self)
        self.italic_action.setStatusTip("Set selected text to Italic (emphasis)")
        self.italic_action.setShortcut(QKeySequence.Italic)
        self.italic_action.setCheckable(True)
        self.italic_action.toggled.connect(self.centralWidget.textBox.setFontItalic)
        format_toolbar.addAction(self.italic_action)
        # formatMenu.addAction(italic_action)

        self.underline_action = QAction(
            QIcon(os.path.join('images', 'icons8-underline-80.png')), "Underline", self)
        self.underline_action.setStatusTip("Set selected text to Underline")
        self.underline_action.setShortcut(QKeySequence.Underline)
        self.underline_action.setCheckable(True)
        self.underline_action.toggled.connect(
            self.centralWidget.textBox.setFontUnderline)
        format_toolbar.addAction(self.underline_action)

        bullet_action = QAction(
            QIcon(os.path.join('images', 'icons8-bulleted-list-80.png')), "Bulleted List", self)
        bullet_action.setStatusTip('Add a Bullet List')
        bullet_action.triggered.connect(self.BulletList)
        format_toolbar.addAction(bullet_action)

        numbered_action = QAction(
            QIcon(os.path.join('images', 'icons8-numbered-list-80.png')), "Numbered List", self)
        numbered_action.setStatusTip('Add a Numbered List')
        numbered_action.triggered.connect(self.NumberedList)
        format_toolbar.addAction(numbered_action)

        font = QFont('Helvetica', 16)
        self.centralWidget.textBox.setFont(font)
        self.centralWidget.textBox.setFontPointSize(16)

        # ------------------------
        # Create paragraph toolbar
        paragraph_toolbar = QToolBar("Paragraph")
        paragraph_toolbar.setIconSize(QSize(icon_size, icon_size))
        self.addToolBar(paragraph_toolbar)

        self.aln_left_action = QAction(
            QIcon(os.path.join('images', 'icons8-align-left-80.png')), "Align Left", self)
        self.aln_left_action.setStatusTip("Align Text Left")
        self.aln_left_action.setCheckable(True)
        self.aln_left_action.triggered.connect(
            lambda: self.centralWidget.textBox.setAlignment(Qt.AlignLeft))
        paragraph_toolbar.addAction(self.aln_left_action)

        self.aln_center_action = QAction(
            QIcon(os.path.join('images', 'icons8-align-center-80.png')), "Center", self)
        self.aln_center_action.setStatusTip("Center Text")
        self.aln_center_action.setCheckable(True)
        self.aln_center_action.triggered.connect(
            lambda: self.centralWidget.textBox.setAlignment(Qt.AlignCenter))
        paragraph_toolbar.addAction(self.aln_center_action)

        self.aln_right_action = QAction(QIcon(os.path.join(
            'images', 'icons8-align-right-80.png')), "Align Right", self)
        self.aln_right_action.setStatusTip("Align Text Right")
        self.aln_right_action.setCheckable(True)
        self.aln_right_action.triggered.connect(
            lambda: self.centralWidget.textBox.setAlignment(Qt.AlignRight))
        paragraph_toolbar.addAction(self.aln_right_action)

        self.aln_justify_action = QAction(
            QIcon(os.path.join('images', 'icons8-align-justify-80.png')), "Justify", self)
        self.aln_justify_action.setStatusTip("Justify Text")
        self.aln_justify_action.setCheckable(True)
        self.aln_justify_action.triggered.connect(
            lambda: self.centralWidget.textBox.setAlignment(Qt.AlignJustify))
        paragraph_toolbar.addAction(self.aln_justify_action)

        self.aln_left_action.setChecked(True)
        format_group = QActionGroup(self)
        format_group.setExclusive(True)
        format_group.addAction(self.aln_left_action)
        format_group.addAction(self.aln_center_action)
        format_group.addAction(self.aln_right_action)
        format_group.addAction(self.aln_justify_action)

    # Classes
    # =======

    def BulletList(self):
        textSelected = self.centralWidget.textBox.textCursor().selectedText()

        if textSelected == '':
            self.centralWidget.textBox.insertHtml("<ul><li>_</li></ul>")

        else:
            self.centralWidget.textBox.insertHtml(
                "<ul><li>" + textSelected + "</li></ul>")

    def NumberedList(self):
        textSelected = self.centralWidget.textBox.textCursor().selectedText()

        if textSelected == '':
            self.centralWidget.textBox.insertHtml("<ol><li>_</li></ol>")

        else:
            self.centralWidget.textBox.insertHtml(
                "<ol><li>" + textSelected + "</li></ol>")

    def fontChoice(self):
        font, valid = QFontDialog.getFont()
        if valid:
            self.centralWidget.textBox.setFont(font)

    # Opens the color dialog
    def colorPicker(self):
        cursor = self.centralWidget.textBox.textCursor()
        color = QColorDialog.getColor(self.centralWidget.textBox.textColor())

        if color.isValid():
            self.setColorIcon(color)
            self.centralWidget.textBox.setTextColor(color)

    def SearchSelection(self):
        cursor = self.centralWidget.textBox.textCursor()
        textSelected = cursor.selectedText()
        flags = QTextDocument.FindFlags()
        r = self.centralWidget.textBox.find(textSelected, flags)

        if not r:
            self.centralWidget.textBox.moveCursor(QTextCursor.Start)
            r = self.centralWidget.textBox.find(textSelected, flags)

            if not r:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText('Text Not Found.')
                msg.setWindowTitle('Error')
                msg.exec_()

        return r

    # Sets color of text
    def TextColor(self, i):

        if i == 0:
            self.setColorIcon(Qt.black)
            self.centralWidget.textBox.setTextColor(Qt.black)
            return

        if i == 1:
            self.setColorIcon(Qt.red)
            self.centralWidget.textBox.setTextColor(Qt.red)
            return

        if i == 2:
            self.setColorIcon(Qt.green)
            self.centralWidget.textBox.setTextColor(Qt.green)
            return

        if i == 3:
            self.setColorIcon(Qt.blue)
            self.centralWidget.textBox.setTextColor(Qt.blue)
            return

        if i == 4:
            self.setColorIcon(Qt.yellow)
            self.centralWidget.textBox.setTextColor(Qt.yellow)
            return

        if i == 5:
            self.setColorIcon(Qt.gray)
            self.centralWidget.textBox.setTextColor(Qt.gray)
            return

        if i == 6:
            self.setColorIcon(Qt.magenta)
            self.centralWidget.textBox.setTextColor(Qt.magenta)
            return

        else:
            return

    # Sets the color icon on the QToolBar
    def setColorIcon(self, color):
        pixelMap = QPixmap(64, 24)
        pixelMap.fill(color)
        self.colorLabel.setPixmap(pixelMap)

    # Called when the QMainWindow is closed
    def closeEvent(self, event):
        if self.needsSave:
            self.promptSaveMessage()
            if self.saveMessageCancel:
                event.ignore()
            elif self.needsSave:
                self.saveWindow.closeOnSave = True
                event.ignore()

    # Called when any key is pressed
    def keyPressEvent(self, e):
        self.statusBar().clearMessage()

    # Called when text in the AppWidget QTextEdit is changed
    def textEditedEvent(self):
        self.needsSave = True
        self.statusBar().clearMessage()

        if not self.Edited:
            self.window_title = self.window_title + " -- Edited"
            self.setWindowTitle(self.window_title)
            self.Edited = True

    # Called when the QTextCursor in the AppWidget QTextEdit is moved
    def cursorMovedEvent(self):

        # Do not update formatting while the user is selecting text
        if not self.centralWidget.textBox.textCursor().hasSelection():

            # Update current text color under cursor for color button display
            self.setColorIcon(self.centralWidget.textBox.textColor())

            # Update the current font formatting (bold, italics, underline, etc.)
            self.bold_action.setChecked(self.centralWidget.textBox.fontWeight() == QFont.Bold)
            self.italic_action.setChecked(self.centralWidget.textBox.fontItalic())
            self.underline_action.setChecked(self.centralWidget.textBox.fontUnderline())
            self.aln_right_action.setChecked(self.centralWidget.textBox.alignment() == Qt.AlignRight)
            self.aln_left_action.setChecked(self.centralWidget.textBox.alignment() == Qt.AlignLeft)
            self.aln_center_action.setChecked(self.centralWidget.textBox.alignment() == Qt.AlignCenter)
            self.aln_justify_action.setChecked(self.centralWidget.textBox.alignment() == Qt.AlignJustify)
            self.fonts.setCurrentFont(self.centralWidget.textBox.currentFont())
            self.fontsize.setCurrentIndex(FONT_SIZES.index(self.centralWidget.textBox.fontPointSize()))

    # Opens the file dialog to save a new file or saves the working file.
    def saveEvent(self):

        if self.Edited:
            self.window_title = self.window_title[:-10]
            self.setWindowTitle(self.window_title)
            self.Edited = False

        if not self.saveWindow:
            self.saveWindow = SaveWindow(self)
            self.saveWindow.initSaveEvent()

    # Opens the file dialog even if a file is already open.
    def saveAsEvent(self):

        if not self.saveWindow:
            self.saveWindow = SaveWindow(self)
            self.saveWindow.saveAsEvent()

    # Opens a file (isNew defines if the file is a new, empty file)
    def openEvent(self, isNew: bool):

            # New file
            if isNew:
                
                # Prompt save message
                if self.needsSave:
                    self.promptSaveMessage()

                if not self.needsSave or self.saveMessageSuccess:
                    self.currentFile = ''
                    self.centralWidget.textBox.clear()
                    self.centralWidget.textBox.setTextColor(Qt.black)
                    self.setColorIcon(Qt.black)
                    self.window_title = 'Notepad App - untitled.txt'
                    self.setWindowTitle(self.window_title)
                    self.needsSave = False
                    self.Edited = False

            # Open file
            elif not self.openWindow:
                self.openWindow = OpenWindow(self)
                self.openWindow.show()

    # Creates the save message prompt window
    def promptSaveMessage(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText('Do you want to save changes to the current file?')
        msg.setWindowTitle('Notepad App Save Message')
        msg.setStandardButtons(
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        msg.buttonClicked.connect(self.saveMessageEvent)
        msg.exec_()

    # Handles the save prompt button event when opening a new file
    def saveMessageEvent(self, button):

        self.saveMessageCancel = False

        # Save the file and store the result
        if button.text() == '&Yes':
            self.saveMessageSuccess = self.saveEvent()

        # Skip saving the file
        elif button.text() == '&No':
            self.needsSave = False

        else:
            self.saveMessageCancel = True

    # Opens the print dialog
    def printEvent(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialogue = QPrintDialog(printer, self)

        if dialogue.exec_() == QPrintDialog.Accepted:
            self.centralWidget.textBox.print_(printer)

from PySide6 import (QtCore, QtGui)
from PySide6.QtWidgets import QMainWindow, QFileDialog, QGraphicsScene, QLabel, QProgressDialog
from UiMainwindow import Ui_MainWindow
import os.path
import math
import time


class MyGraphicsScene(QGraphicsScene):

    # Dichiaro un segnale
    signalMousePos = QtCore.Signal(QtCore.QPointF)

    # Override della funzione mouseMoveEvent per emettere il segnale custom
    def mouseMoveEvent(self, event):
        pos = event.lastScenePos()
        # Emetto il segnale passandogli la posizione del mouse
        self.signalMousePos.emit(pos)


class MainWindow(QMainWindow):

    iso_files = ''
    scale_factor = 1
    # Dimensioni della scena
    scene_w = 0
    scene_h = 0

    # Setting the antialiasing for the canvas (active by default)
    # self.ui.canvas.DontAdjustForAntialiasing(False)
    # the canvas area is extended by 4 pixels over the visible area, and the mouse position
    # is offset by 4px, this will compensate this difference. Must be set to 0
    # if the antialiasing is not in use
    canvas_expanded = 4

    # Min and Max positions
    x_min = 10000
    y_min = 10000
    x_max = 0
    y_max = 0
    z_max = 0

    # Last Z position, to be updated for each segment, this will be used to know
    # how much the tool must be raised to leave the working surface
    last_z = 0

    # If needed, these will be set to make all the coordinates positive
    offset_x = 0
    offset_y = 0

    # Says whether anything was drawn or not
    iso_drawn = False
    # Says whether the timer to delay the drawing regeneration is active or not
    resize_timer_running = False

    # Contains the ful
    selected_files_full_string = ''

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowIcon(QtGui.QIcon('favicon.png'))

        self.ui.btn_draw.clicked.connect(self.draw)
        self.ui.btn_reset.clicked.connect(self.resetScene)
        self.ui.btn_browse_file.clicked.connect(self.browseFile)
        self.scene = MyGraphicsScene()
        # Intercepts the signal emitted and connects it to the mousePosition() method
        self.scene.signalMousePos.connect(self.mousePosition)

        self.ui.canvas.setScene(self.scene)
        self.ui.canvas.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.ui.lbl_x_min_value.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB;')
        self.ui.lbl_x_max_value.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB;')
        self.ui.lbl_y_min_value.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB;')
        self.ui.lbl_y_max_value.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB;')
        self.ui.lbl_z_max_value.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB;')
        self.ui.lbl_rectangle_value.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB;')
        self.ui.lbl_working_time_value.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB;')
        self.ui.lbl_mouse_pos_x.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB;')
        self.ui.lbl_mouse_pos_y.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB;')
        self.ui.lbl_offset_value.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB;')
        self.ui.lbl_eng_dst_value.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB;')
        self.ui.lbl_pos_dst_value.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB;')
        # To center the checkbox
        self.ui.chk_autoresize.setStyleSheet("padding-left:20px;")

        self.setTabOrder(self.ui.in_width, self.ui.in_height)
        self.setTabOrder(self.ui.in_height, self.ui.in_tool_speed)
        self.setTabOrder(self.ui.in_tool_speed, self.ui.chk_autoresize)

        # Timer to manage the delay when regenerating the drawing when the scene is resized
        self.reset_timer = QtCore.QTimer(self)
        # Set the timer as single shot.
        # I'm not using a a singleshot timer because it doesn't have the stop() method which
        # is required to simulate a reset as implemented in the resizeEvent() method
        self.reset_timer.setSingleShot(True)
        self.reset_timer.timeout.connect(self.draw)
        # Says whether the timer must be used or not
        self.delayEnabled = True
        # Delay in milliseconds
        self.delayTimeout = 500

    def resizeEvent(self, event):
        '''
        Overrides the QMainWindow resizeEvent() called when the window is resized
        '''
        # When the main window is resized, the scen size must be adjusted
        self.scene_w, self.scene_h = self.getCanvasSize()
        # Delete the selected files label content
        self.ui.lbl_selected_file.setText('')

        # If there is something on the scene and the auto-resize is enabled
        if self.iso_drawn and self.ui.chk_autoresize.isChecked():
            # If the timer is enabled
            if self.delayEnabled:
                # If the timer has been started
                if self.resize_timer_running:
                    # Stop the timer, because the user is still resizing the window
                    self.reset_timer.stop()
                    # Says that the timer is no more active
                    self.resize_timer_running = False

                # Start the timer
                self.reset_timer.start(self.delayTimeout)
                # Says that the timer is active
                self.resize_timer_running = True
            # If the timer is not enabled
            else:
                # Regenerate the drawing
                self.draw()

        self.elideText(self.ui.lbl_selected_file,
                       self.selected_files_full_string)

    def elideText(self, label, text):
        '''
        Elide a long text to fit the label width
        '''
        # Get the metrix for the font used inside the label
        metrix = QtGui.QFontMetrics(label.font())
        # Elide the text at a width of 15px less than the label width to leave some padding
        elideded_text = metrix.elidedText(
            text, QtCore.Qt.ElideRight, label.width() - 15)
        # Print the elided text into the label
        label.setText(elideded_text)

    def showEvent(self, event):
        '''
        Overrides the QMainWindow resizeEvent() called when the window is shown
        '''
        # Initialize the scene's size to also have a valid position for the mouse pointer
        self.scene_w, self.scene_h = self.getCanvasSize()

        # print(str(self.scene_w) + ' X ' + str(self.scene_h))

    def getCanvasSize(self):
        '''Returns the visible size of the canvas'''
        return (self.ui.canvas.width() - self.canvas_expanded, self.ui.canvas.height() - self.canvas_expanded)

    def resetCoordinatesLimits(self):
        '''Resets the min and max values'''
        self.x_min = 10000
        self.y_min = 10000
        self.z_max = 0
        self.x_max = 0
        self.y_max = 0
        self.offset_x = 0
        self.offset_y = 0

    def browseFile(self):
        '''Opens the file browser'''
        # Filter to show only PGR files
        filter = "pgr(*.PGR)"
        # Allows multiple files selection
        self.iso_files, _ = QFileDialog.getOpenFileNames(
            self, 'OpenFile', filter=filter)

        for file in self.iso_files:
            filename = os.path.basename(file)
            self.selected_files_full_string += '"' + filename + '" '

        self.elideText(self.ui.lbl_selected_file,
                       self.selected_files_full_string)

    def resetErrors(self):
        '''
        Resets the input fields, the selected files label and the status bar to
        remove eventual error messages and relative highlighting
        '''
        self.ui.in_width.setStyleSheet("border: 1px solid black")
        self.ui.in_height.setStyleSheet("border: 1px solid black")
        self.ui.in_tool_speed.setStyleSheet("border: 1px solid black")
        self.ui.lbl_selected_file.setStyleSheet("border: none")
        self.ui.statusbar.showMessage('')

    def checkData(self):
        '''Validates the data'''

        # For each selected file
        for file in self.iso_files:
            # Verify that the file exists and has the proper extension
            if not os.path.isfile(file) or not file[-3:] == 'PGR':
                self.ui.lbl_selected_file.setStyleSheet(
                    "border: 1px solid red")
                self.ui.statusbar.showMessage(
                    'Selezionare solo file ISO validi')
                return False
            # If the file exists and it has the PGR extension
            else:
                with open(file) as f:
                    # If the file does not begin with the string "QUOTE RELATIVE"
                    if f.readline().rstrip() != 'QUOTE RELATIVE':
                        self.ui.lbl_selected_file.setStyleSheet(
                            "border: 1px solid red")
                        self.ui.statusbar.showMessage(
                            'Selezionare solo file ISO validi')
                        return False

        # If the width field is empty
        if self.ui.in_width.text() == '':
            # Set to 0
            self.ui.in_width.setText('0')
        # Check if the width value is valid
        if not self.ui.in_width.text().isnumeric() or int(self.ui.in_width.text()) < 0:
            self.ui.in_width.setStyleSheet("border: 1px solid red")
            self.ui.statusbar.showMessage(
                'Indicare una larghezza valida (numero intero positivo o 0)')
            return False
        # The value is valid
        else:
            # But it could be a decimal number, get only the integer part
            self.ui.in_width.setText(str(int(self.ui.in_width.text())))

        # If the height field is empty
        if self.ui.in_height.text() == '':
            # Set to 0
            self.ui.in_height.setText('0')
        # Check if the height value is valid
        if not self.ui.in_height.text().isnumeric() or int(self.ui.in_height.text()) < 0:
            self.ui.in_height.setStyleSheet("border: 1px solid red")
            self.ui.statusbar.showMessage(
                'Indicare un\'altezza valida (numero intero positivo o 0)')
            return False
        # The value is valid
        else:
            # But it could be a decimal number, get only the integer part
            self.ui.in_height.setText(str(int(self.ui.in_height.text())))

        # If the speed tool value field is empty
        if self.ui.in_tool_speed.text() == '':
            # Set to 1000
            self.ui.in_tool_speed.setText('1000')
        # Check if the speed tool value is valid
        if not self.ui.in_tool_speed.text().isnumeric() or int(self.ui.in_tool_speed.text()) <= 0:
            self.ui.in_tool_speed.setStyleSheet("border: 1px solid red")
            self.ui.statusbar.showMessage(
                'Indicare una velocità valida (numero intero positivo)')
            return False
        # The value is valid
        else:
            # But it could be a decimal number, get only the integer part
            self.ui.in_tool_speed.setText(
                str(int(self.ui.in_tool_speed.text())))

        # Check if only the width has been set
        if int(self.ui.in_width.text()) > 0 and self.ui.in_height.text() == '0':
            # Both the sizes must be set or none of them
            self.ui.in_height.setStyleSheet("border: 1px solid red")
            self.ui.statusbar.showMessage(
                'Indicare entrambe le dimensioni o nessuna')
            return False

        # Check if only the height has been set
        if int(self.ui.in_height.text()) > 0 and self.ui.in_width.text() == '0':
            # Both the sizes must be set or none of them
            self.ui.in_width.setStyleSheet("border: 1px solid red")
            self.ui.statusbar.showMessage(
                'Indicare entrambe le dimensioni o nessuna')
            return False

        return True

    def scaleFactor(self, w, h):
        '''
        Calculates the scale factor to resize the drawing to fit the scene size
        '''
        # I do not use self.scene_w and self.scene_h set into showEvent()
        # for the size of the scene, because after that the window is shown it could have been
        # resized and the canvas size could be changed

        # Canvas size
        canvas_w, canvas_h = self.getCanvasSize()

        # Calculates the scale factor to fit the width
        scale_x = canvas_w / w
        # Calculates the scale factor to fit the hight
        scale_y = canvas_h / h

        # Return the smallest scale factor
        return scale_x if scale_x <= scale_y else scale_y

    def resetScene(self, reset_to_draw=False):
        '''
        Reset the scene to the initial state
        Param - boolean draw: if False also reset the selected files
        '''
        # Remove the scene from the view
        # this is not really required, but it speeds up the reset process
        self.ui.canvas.setScene(None)
        # Reset the scene
        self.scene.clear()
        self.scale_factor = 1
        self.ui.lbl_x_min_value.setText('')
        self.ui.lbl_x_max_value.setText('')
        self.ui.lbl_y_min_value.setText('')
        self.ui.lbl_y_max_value.setText('')
        self.ui.lbl_z_max_value.setText('')
        self.ui.lbl_rectangle_value.setText('')
        self.ui.lbl_offset_value.setText('')
        self.ui.lbl_working_time_value.setText('')
        if not reset_to_draw:
            self.iso_files = ''
            self.selected_files_full_string = ''
            self.ui.lbl_selected_file.setText('')
        # Says that no drowing is on the scene
        self.iso_drawn = False

        # Reassign the scene to the canvas
        self.ui.canvas.setScene(self.scene)

    def setScene(self):
        '''
        Set the scen to contain the drawing just elaborated
        '''

        # Reset the scene
        self.resetScene(True)

        # Size set for the slab
        width = float(self.ui.in_width.text())
        height = float(self.ui.in_height.text())

        # Canvas size
        canvas_w, canvas_h = self.getCanvasSize()

        # If a width has been set, also the hight is set, the validate() method takes care of that
        if width > 0:
            # Calculate the scale factor to fit the scene
            self.scale_factor = self.scaleFactor(width, height)

            # Assign the slab size resized according to the scale factor
            self.scene_w = width * self.scale_factor
            self.scene_h = height * self.scale_factor
        # The slab size has not been set
        else:
            # To calculate the scale factor, consider the drwaing size
            self.scale_factor = self.scaleFactor(self.x_max, self.y_max)

            # Assign the canvas size
            self.scene_w = canvas_w
            self.scene_h = canvas_h

        # Set the scene as big as the canvas
        self.scene.setSceneRect(0, 0, canvas_w, canvas_h)

        # If the size for the slab has been set
        if width > 0:
            # Draw a rectangle defining it
            self.scene.addRect(QtCore.QRectF(0, 0, self.scene_w, self.scene_h))

    def cancelDrawing(self):
        '''
        Resets the both scene and the scene and the limits
        '''
        self.resetScene()
        self.resetCoordinatesLimits()

    def getCoordinates(self):
        '''
        Read the ISO files and gets the coordinates useful for the drawing
        '''

        # Reset the min and max values
        self.resetCoordinatesLimits()
        # List containing the useful coordinates
        coords = []

        iso = []

        for file in self.iso_files:
            # Opens the ISO file
            original_file = open(file, 'r')
            # Copy the file content
            iso += original_file.readlines()
            # Close the file
            original_file.close()

        num_rows = len(iso)

        pd = QProgressDialog('Estrapolazione coordinate',
                             'Annulla', 0, num_rows-1, self)
        pd.setModal(True)
        pd.setMinimumDuration(0)

        # It is not convenient to update the progress bar at each loop iteration, that would
        # result in a very slow execution, this sets the update to be executed once every
        # 1/500 of the total iterations
        progress_step = int(num_rows / 500)

        i = 0

        # Says if the tool is over the first point where it lowes to engrave
        first_down = False
        # The position where the engraving starts is after the second G12 Z0
        # thi variable is a counter to recognize it
        z_down = 0

        # Loop over all the rows of the file
        for line_of_code in iso:

            if i % progress_step == 0:
                pd.setValue(i)

                if pd.wasCanceled():
                    self.cancelDrawing()
                    break

            # Rows starting with G02 X indicate positions which produce engravings - i.e.: G02 X508 Y556 Z-13
            if line_of_code.find('G02 X') == 0:
                # Split the code
                subline = line_of_code.split(' ')

                # The second element is the X coordinate, remove the first character (X)
                # limit the number to 3 decimals
                x = float('{:.3f}'.format(float(subline[1][1:])))

                # Update the x min
                if x <= self.x_min:
                    self.x_min = x
                # Update the x max
                if x >= self.x_max:
                    self.x_max = x

                # The third element is the Y coordinate, remove the first character (Y)
                # limit the number to 3 decimals
                y = float('{:.3f}'.format(float(subline[2][1:])))

                # Update the y min
                if y <= self.y_min:
                    self.y_min = y
                # Update the y max
                if y >= self.y_max:
                    self.y_max = y

                # The fourth element is the Z coordinate, remove the first character (Z)
                # limit the number to 3 decimals
                z = float('{:.3f}'.format(float(subline[3][1:])))
                # Update the z max
                if z < self.z_max:
                    self.z_max = z

                # Add the coordinates to the list
                coords.append((x, y, z))

            # Rows starting with G12 X indicate a repositioning over the XY plane
            elif line_of_code.find('G12 X') == 0:
                # Considering the positioning, X an Y min/max must not be calculated from where the tool starts
                # or X and Y min would always be 0 since it is the origin of the job, they must be considered
                # from the next position, that is where the the tool lowers for the first time to engrave.
                # It is not sure that this will be the min or max, but it is a valid position to consider.

                # Split the code
                subline = line_of_code.split(' ')

                # The second element is the X coordinate, remove the first character (X)
                # limit the number to 3 decimals
                x = float('{:.3f}'.format(float(subline[1][1:])))

                # The third element is the Y coordinate, remove the first character (Y)
                # limit the number to 3 decimals
                y = float('{:.3f}'.format(float(subline[2][1:])))

                # If this is the first place where the tool lowers to engrave
                if first_down:
                    # Update the x min
                    if x <= self.x_min:
                        self.x_min = x
                    # Update the x max
                    if x >= self.x_max:
                        self.x_max = x

                    # Update the y min
                    if y <= self.y_min:
                        self.y_min = y
                    # Update the y max
                    if y >= self.y_max:
                        self.y_max = y

                    # Reset the flag, from now on it will not be used anymore
                    first_down = False

                # Add the coordinates to the list, this will always be preceded by an "up"
                coords.append((x, y, 0))

            # Rows starting with G02 Z indicate the only vertical movement to start to engrave
            elif line_of_code.find('G02 Z') == 0:
                # Split the code
                subline = line_of_code.split(' ')

                # Says that the next coordinate will be the tool lowering
                coords.append(('down', 0, 0))

                # Says how much the tool lowers
                coords.append(
                    (0, 0, float('{:.3f}'.format(float(subline[1][1:])))))

            # Rows starting with G12 Z0 indicate the only vertical movement to raise the tool from the working plane
            elif line_of_code.find('G12 Z0') == 0:
                # If the second G12 Z0 has not yet been found
                if z_down < 2:
                    # Increment the counter
                    z_down += 1
                # If the second G12 Z0 has just been found
                if z_down == 2:
                    # Set the flag to True to say that here the tool will lower for the first time
                    first_down = True

                # Example
                # G02 X100 Y0 Z-10
                # G02 X0 Y0 Z-10
                # G12 Z0
                # G12 X150 Y100
                # G02 Z-10
                # G02 X150 Y200 Z-10
                # In this case, the coordinates list would contain
                # ((100, 0), (0, 0), (150, 100))
                # but the segment from (0, 0) to (150, 100) must not be drawn, thus "up" will indicate this situation.
                # When an "up" is found, the last Z coordinate must be read to know how much the tool will be raised
                # the absolute value of the Z must be considered, since the Z is always negative or 0
                coords.append(('up', 0, 0))

            i += 1

        # Check whether the X and/or Y Csomewhere become negative and take everything back to positive values
        # or it will not be possible to draw on the scene, which only accepts positive coordinates
        if self.x_min < 0:
            self.offset_x = abs(self.x_min)
            self.x_min = 0
            self.x_max += self.offset_x

        if self.y_min < 0:
            self.offset_y = abs(self.y_min)
            self.y_min = 0
            self.y_max += self.offset_y

        # If at least one of the offset has been set
        if self.offset_x > 0 or self.offset_y > 0:
            num_coords = len(coords)

            # For each coordinate in the list
            for i in range(num_coords-1):
                # If the current tuple does not contain a movement indication
                if coords[i][0] != 'up' and coords[i][0] != 'down':
                    # Add the offsets to move the drawing into the positive area
                    new_x = float(coords[i][0]) + self.offset_x
                    new_y = float(coords[i][1]) + self.offset_y
                    coords[i] = (new_x, new_y, coords[i][2])

        pd.setValue(num_rows-1)

        # Return the list
        return coords

    def workingTime(self, eng_dst, pos_dst):
        '''
        Estimates the working time
        '''
        tot_dst = eng_dst + pos_dst

        seconds = (tot_dst / float(self.ui.in_tool_speed.text())) * 60

        self.ui.lbl_working_time_value.setText(
            time.strftime('%H:%M:%S', time.gmtime(seconds)))

    def mousePosition(self, pos):
        '''
        Gets and shows the mouse pointer coordinates
        '''
        self.ui.lbl_mouse_pos_x.setText(
            str('{:.1f}'.format(float(pos.x() * (1/self.scale_factor)))))
        self.ui.lbl_mouse_pos_y.setText(
            str('{:.1f}'.format(float((self.scene_h - pos.y()) * (1/self.scale_factor)))))

        # print('x: ' + str(int(pos.x())) + ' | y: ' + str(int(pos.y())))

    def draw(self):
        '''
        Displays the drawing
        '''

        self.resetErrors()

        if self.checkData():
            coords = self.getCoordinates()
            num_coords = len(coords)
            self.setScene()

            # Limit the valueas to the 3 decimals and print them on the proper label
            self.ui.lbl_x_min_value.setText('{:.3f}'.format(self.x_min))
            self.ui.lbl_x_max_value.setText('{:.3f}'.format(self.x_max))
            self.ui.lbl_y_min_value.setText('{:.3f}'.format(self.y_min))
            self.ui.lbl_y_max_value.setText('{:.3f}'.format(self.y_max))
            self.ui.lbl_z_max_value.setText('{:.3f}'.format(self.z_max))

            # Print over the offset label if the drawing has been moved
            if self.offset_x > 0 and self.offset_y > 0:
                self.ui.lbl_offset_value.setText('X - Y')
            elif self.offset_x > 0 and self.offset_y == 0:
                self.ui.lbl_offset_value.setText('X')
            elif self.offset_x == 0 and self.offset_y > 0:
                self.ui.lbl_offset_value.setText('Y')
            else:
                self.ui.lbl_offset_value.setText('No')

            # Drawing size
            drawing_w = self.x_max - self.x_min
            drawing_h = self.y_max - self.y_min

            # Print the drawing size on its label
            self.ui.lbl_rectangle_value.setText(
                '{:.3f}'.format(drawing_w) + ' X ' + '{:.3f}'.format(drawing_h))

            # These keep track of the distance covered by the tool
            engraving_dst = 0
            positioning_dst = 0

            # Current position of the tool, initialized over the origin
            current_position = (0, 0, 0)
            # Number of segments drawn
            lines = 0

            # Says if the tool is currently lowering
            lowering = False
            # Says if the tool is engraving
            drawing = False
            # Says if a repositioning is required
            repositioning = False

            pd = QProgressDialog('Elaborazione primitive',
                                 'Annulla', 0, num_coords-1, self)
            pd.setModal(True)
            pd.setMinimumDuration(0)

            # It is not convenient to update the progress bar at each loop iteration, that would
            # result in a very slow execution, this sets the update to be executed once every
            # 1/500 of the total iterations
            progress_step = int(num_coords / 200)

            for i in range(num_coords):
                if i % progress_step == 0:
                    pd.setValue(i)

                    if pd.wasCanceled():
                        self.cancelDrawing()
                        break

                # If this is not the end of the file and the tool must be raised
                # that means that the next movement will be to position the tool
                if i < num_coords and coords[i][0] == 'up':
                    # Add the vertical movement lenght to the positioning distance
                    positioning_dst += abs(self.last_z)

                    # Set the flags
                    lowering = False
                    drawing = False
                    repositioning = True

                    # Terminate the iteration
                    continue

                # If this is the end of the file and the tool must be raised,
                # the only distance to considerate is the vertical movement, then everything is over
                elif coords[i][0] == 'up':
                    # Add the the absolute last z value to the positioning distance
                    positioning_dst += abs(self.last_z)

                    # Update the current position
                    current_position = (
                        current_position[0], current_position[1], 0)

                    # Set the flags
                    lowering = False
                    drawing = False
                    repositioning = False

                    # Terminate the iteration
                    continue

                # If the tool must be lowered (no need to check if we are at the end of the file
                # because if the tool lowerd, for sure there is something else to do)
                if coords[i][0] == 'down':
                    # I do not update the Z distance now, because I should read the next tuple to know it.
                    # I postpone that to the next iteration, which reading lowering=True
                    # will know that it has to calculate the distance.

                    # Set the flags
                    lowering = True
                    drawing = False
                    repositioning = False

                    # Terminate the iteration
                    continue

                # From here on, there will only be tuples with coordinates and not movement indication

                # If the tool is repositioning on the XY plane
                if repositioning:
                    dx = pow(coords[i][0] - current_position[0], 2)
                    dy = pow(coords[i][1] - current_position[1], 2)
                    positioning_dst += math.sqrt(dx + dy)

                    # Update the current position, Z position does not change over repositionings
                    current_position = (
                        coords[i][0], coords[i][1], current_position[2])

                    # Set the flags
                    lowering = False
                    drawing = False
                    repositioning = False

                    # Terminate the iteration
                    continue

                # If the tool is lowering
                if lowering:
                    # Here there will certainly be a tuple containing only a Z coordinate changing
                    positioning_dst += abs(coords[i][2])

                    # Update the current position
                    current_position = (
                        current_position[0], current_position[1], coords[i][2])

                    # Set the flags
                    lowering = False
                    drawing = True
                    repositioning = False

                    # Terminate the iteration
                    continue

                # If the tool is engraving
                if drawing:
                    # Calculate the engraving distance
                    dx = pow(coords[i][0] - current_position[0], 2)
                    dy = pow(coords[i][1] - current_position[1], 2)
                    dz = pow(coords[i][2] - current_position[2], 2)
                    engraving_dst += math.sqrt(dx + dy + dz)

                    # Draw the segment until the point indicated by the coordinate
                    # X stays as read from the file, the Y must be calculated because the Y tha machine's axis
                    # values increas from bottom to top, in the canvas instead goes from top to bottom
                    p1 = QtCore.QPoint(
                        current_position[0] * self.scale_factor,
                        self.scene_h -
                        (current_position[1] * self.scale_factor)
                    )

                    p2 = QtCore.QPoint(
                        coords[i][0] * self.scale_factor,
                        self.scene_h - (coords[i][1] * self.scale_factor)
                    )

                    # Add the segment to the scene
                    self.scene.addLine(QtCore.QLine(p1, p2))

                    # Update the current position
                    current_position = (
                        coords[i][0], coords[i][1], coords[i][2])

                    # Update the last z value
                    self.last_z = coords[i][2]

                    # Update the lines count
                    lines += 1

                    # Set the flags
                    lowering = False
                    drawing = True
                    repositioning = False

                    # Terminate the iteration
                    continue

            pd.setValue(num_coords-1)
            # Says that there is something on the scene
            self.iso_drawn = True
            # Estimate the woking time
            self.workingTime(engraving_dst, positioning_dst)

            # Print the engraving and repositioning distances to the relative labels
            self.ui.lbl_eng_dst_value.setText('{:.3f}'.format(engraving_dst))
            self.ui.lbl_pos_dst_value.setText('{:.3f}'.format(positioning_dst))

            # If the flag is set to True, that means that the drawing has ben regenerated
            # after that the scene was resized
            if self.resize_timer_running:
                # Says that the timer timed out and it not running anymore
                self.resize_timer_running = False

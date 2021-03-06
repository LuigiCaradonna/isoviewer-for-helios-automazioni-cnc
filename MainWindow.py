from PySide6 import (QtCore, QtGui)
from PySide6.QtWidgets import QMainWindow, QFileDialog, QGraphicsScene, QProgressDialog
from more_itertools import padded
from UiMainwindow import Ui_MainWindow
import os.path
import math
import time


class MyGraphicsScene(QGraphicsScene):

    # Declares a signal
    signalMousePos = QtCore.Signal(QtCore.QPointF)

    # Override of the method mouseMoveEvent to emit a custom signal
    def mouseMoveEvent(self, event):
        pos = event.lastScenePos()
        # Emits the signal passing the mouse posizion
        self.signalMousePos.emit(pos)


class MainWindow(QMainWindow):

    iso_files = ''
    scale_factor = 1
    # Scene size
    scene_w = 0
    scene_h = 0

    config_file = 'config.cfg'

    # Setting the antialiasing for the canvas, active by default,
    # (self.ui.canvas.DontAdjustForAntialiasing(False) to disable)
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

    # Contains the full string of the selected files, only their names
    # If needed there will be another variable containing a cut string returned by elideText()
    selected_files_full_string = ''

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Sets an icon for the window
        self.setWindowIcon(QtGui.QIcon('favicon.png'))

        # Bind the buttons to the corresponding method to fire
        self.ui.btn_draw.clicked.connect(self.draw)
        self.ui.btn_reset.clicked.connect(self.fullReset)
        self.ui.btn_browse_file.clicked.connect(self.browseFile)

        # Bind the checkboxes to the corresponding method to persist the selection
        self.ui.chk_fit.stateChanged.connect(self.changeFit)
        self.ui.chk_autoresize.stateChanged.connect(self.changeAutoResize)
        self.ui.chk_color.stateChanged.connect(self.changeColor)
        self.ui.chk_gradient.stateChanged.connect(self.changeGradient)

        # Instantiates a scene
        self.scene = MyGraphicsScene()
        # Intercepts the signal emitted and connects it to the mousePosition() method
        self.scene.signalMousePos.connect(self.mousePosition)

        # Assign the scene to the canvas
        self.ui.canvas.setScene(self.scene)
        # Set the canvas alignment
        self.ui.canvas.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        # Input fields and labels styling
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

        # If the config file does not exist
        if not os.path.isfile(self.config_file):
            # Create a new one with default values
            with open(self.config_file, 'w') as f:
                f.write('0,0,0,0')
                f.close()

        # Set the checkboxes according to the config file
        self.initOptions()

        # Timer to manage the delay when regenerating the drawing when the scene is resized
        self.reset_timer = QtCore.QTimer(self)
        # Set the timer as single shot.
        # I'm not directly using a singleshot timer because it doesn't have the stop() method which
        # is required to simulate a reset as implemented in the resizeEvent() method
        self.reset_timer.setSingleShot(True)
        self.reset_timer.timeout.connect(self.draw)
        # Says whether the timer must be used or not
        self.delayEnabled = True
        # Delay in milliseconds
        self.delayTimeout = 500

    def initOptions(self):
        '''
        Reads the config file and sets the corresponding checkboxes
        '''
        with open(self.config_file, "r") as f:
            config = f.readline()
            f.close()

            config = config.split(',')

            if config[0] == '1':
                self.ui.chk_fit.setChecked(True)
            else:
                self.ui.chk_fit.setChecked(False)

            if config[1] == '1':
                self.ui.chk_autoresize.setChecked(True)
            else:
                self.ui.chk_autoresize.setChecked(False)

            if config[2] == '1':
                self.ui.chk_color.setChecked(True)
            else:
                self.ui.chk_color.setChecked(False)
                
            if config[3] == '1':
                self.ui.chk_gradient.setChecked(True)
            else:
                self.ui.chk_gradient.setChecked(False)

    def updateConfig(self, position, value):
        '''
        Updates the content of the config file according to the checkboxes status
        '''
        
        with open(self.config_file, "r+") as f:
            content = f.read()
            content = content.split(',')
            content[position] = value
            content = ','.join(content)
            f.seek(0)
            f.write(content)
            f.truncate()

    def changeFit(self):
        '''
        Updates the setting value for the fit option inside the config file 
        '''
        value = '1' if self.ui.chk_fit.isChecked() else '0'

        self.updateConfig(0, value)

    def changeAutoResize(self):
        '''
        Updates the setting value for the auto resize option inside the config file 
        '''

        value = '1' if self.ui.chk_autoresize.isChecked() else '0'

        self.updateConfig(1, value)

    def changeColor(self):
        '''
        Updates the setting value for the color option inside the config file 
        '''

        value = '1' if self.ui.chk_color.isChecked() else '0'

        self.updateConfig(2, value)
        
    def changeGradient(self):
        '''
        Updates the setting value for the gradient option inside the config file 
        '''

        value = '1' if self.ui.chk_gradient.isChecked() else '0'

        self.updateConfig(3, value)

    def resizeEvent(self, event):
        '''
        Overrides the QMainWindow resizeEvent() called when the window is resized
        '''
        # When the main window is resized, the scen size must be adjusted
        self.scene_w, self.scene_h = self.getCanvasSize()

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
        elided_text = metrix.elidedText(
            text, QtCore.Qt.ElideRight, label.width() - 15)
        # Print the elided text into the label
        label.setText(elided_text)

    def showEvent(self, event):
        '''
        Overrides the QMainWindow resizeEvent() called when the window is shown
        '''
        # Initialize the scene's size to also have a valid position for the mouse pointer
        self.scene_w, self.scene_h = self.getCanvasSize()

    def getCanvasSize(self):
        '''
        Returns the visible size of the canvas, applying a compensation for the px difference introduced by the antialiasing if necessary
        '''
        return (self.ui.canvas.width() - self.canvas_expanded, self.ui.canvas.height() - self.canvas_expanded)

    def resetCoordinatesLimits(self):
        '''
        Resets the coordinates' min and max values and the offsets
        '''
        self.x_min = 10000
        self.y_min = 10000
        self.z_max = 0
        self.x_max = 0
        self.y_max = 0
        self.offset_x = 0
        self.offset_y = 0

    def browseFile(self):
        '''
        Opens the file browser
        '''
        # Filter to show only PGR files
        filter = "pgr(*.PGR)"
        # Allows multiple files selection
        self.iso_files, _ = QFileDialog.getOpenFileNames(
            self, 'OpenFile', filter=filter)

        # Builds the string containing all the names of the selected files
        for file in self.iso_files:
            filename = os.path.basename(file)
            self.selected_files_full_string += '"' + filename + '" '

        # Elides, if necessary, the string to fit the selected files label and prints it
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
                'Indicare una velocit?? valida (numero intero positivo)')
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

    def fullReset(self):
        '''
        Resets all the input fields, the errors  and the scene
        '''
        self.resetErrors()
        self.resetScene()
        self.ui.in_width.setText('0')
        self.ui.in_height.setText('0')
        self.ui.in_tool_speed.setText('1000')
        self.ui.chk_sculpture.setChecked(False)

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
        self.ui.lbl_eng_dst_value.setText('')
        self.ui.lbl_pos_dst_value.setText('')
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

        # If the drawing must be adapted to the canvas size
        if self.ui.chk_fit.isChecked():
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
        else:
            # If a width has been set, also the hight is set, the validate() method takes care of that
            if width > 0:
                self.scale_factor = self.scaleFactor(width, height)

                # The scale factor must be != 1 only if the regular drawing's size exceeds the canvas
                # which happens if the scale factor calculated is less than 1
                if self.scale_factor > 1:
                    self.scale_factor = 1

                # Assign the slab size
                self.scene_w = width * self.scale_factor
                self.scene_h = height * self.scale_factor

            # The slab size has not been set
            else:
                # To calculate the scale factor, consider the drwaing size
                self.scale_factor = self.scaleFactor(self.x_max, self.y_max)

                # As above
                if self.scale_factor > 1:
                    self.scale_factor = 1

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
        Resets the both the scene and the coordinates' limits
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

        # List of all the instructions contained inside the selected files
        iso = []

        # For each selected file
        for file in self.iso_files:
            # Opens the ISO file
            original_file = open(file, 'r')

            # Add the file content to the list of instructions
            iso += original_file.readlines()
            # Close the file
            original_file.close()

        # The PGR files conatining a sculpture are slightly different from a general one
        # If the file to show contains a sculpture (the user has to tell us)
        if self.ui.chk_sculpture.isChecked():
            j = 0
            start_position = []
            for loc in iso:
                if loc.find('QUOTE RELATIVE') == 0:
                    start_position.insert(0, j)
                j += 1

            for pos in start_position:
                # Add this two lines to adapt it to a general PGR file
                iso.insert(pos+5, 'G12 Z0')
                iso.insert(pos+7, 'G02 Z-10')

        num_rows = len(iso)

        # Progress dialog shown while processing the list of instructions
        pd = QProgressDialog('Estrapolazione coordinate',
                             'Annulla', 0, num_rows-1, self)
        pd.setModal(True)
        pd.setMinimumDuration(0)

        # It is not convenient to update the progress bar at each loop iteration, that would
        # result in a very slow execution, this sets the update to be executed once every
        # 1/500 of the total iterations
        progress_step = int(num_rows / 500)

        # Counter for the prograss dialog
        i = 0

        # Says if the tool is over the first point where it lowes to engrave
        first_down = False
        # The position where the engraving starts is after the second G12 Z0
        # the variable is a counter to recognize it
        z_down = 0

        # Loop over all the rows of the list of instructions
        for line_of_code in iso:

            # If 1/500 of the instructions have been processed
            if progress_step != 0 and i % progress_step == 0:
                # Update the progress dialog
                pd.setValue(i)

                # If the cancel button of the progress dialog was clicked
                if pd.wasCanceled():
                    # Abort the drawing resetting the changed variables
                    self.cancelDrawing()
                    # Stop the loop
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
                    # Increment the counter to have z_down > 2 to not trigger the first_down=True again
                    z_down += 1

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
            coords = self.translateCoords(coords, self.offset_x, self.offset_y)

        pd.setValue(num_rows-1)

        # Return the list
        return coords

    def translateCoords(self, coords, dx, dy):
        '''
        translate the provided coordinates along x any axes by the given amount dx and dy
        '''
        # For each coordinate in the list
        for i in range(len(coords)-1):
            # If the current tuple does not contain a movement indication
            if coords[i][0] != 'up' and coords[i][0] != 'down':
                # Add the offsets to move the drawing into the positive area
                new_x = float(coords[i][0]) + dx
                new_y = float(coords[i][1]) + dy
                coords[i] = (new_x, new_y, coords[i][2])

        return coords

    def workingTime(self, eng_dst, pos_dst):
        '''
        Estimates the working time
        '''
        # Total distance in millimiters
        tot_dst = eng_dst + pos_dst

        # Seconds to complete the job (distance is in mm, speed in mm/min)
        seconds = (tot_dst / float(self.ui.in_tool_speed.text())) * 60

        # Estimated time formatted and printed to the corresponding label
        self.ui.lbl_working_time_value.setText(
            time.strftime('%H:%M:%S', time.gmtime(seconds)))

    def mousePosition(self, pos):
        '''
        Gets and shows the mouse pointer coordinates
        '''
        # X coordinate
        self.ui.lbl_mouse_pos_x.setText(
            str('{:.1f}'.format(float(pos.x() * (1/self.scale_factor)))))
        # Y coordinate
        self.ui.lbl_mouse_pos_y.setText(
            str('{:.1f}'.format(float((self.scene_h - pos.y()) * (1/self.scale_factor)))))

    def mapRange(self, value, source_min, source_max, target_min, target_max):
        '''
        Maps a value from a range to another.
        Here it is used to convert a depth value to a color, the deeper is the engraving, the higher is the color value.
        '''
        # Figure out how 'wide' each range is
        left_span = source_max - source_min
        right_span = target_max - target_min

        # Convert the left range into a 0-1 range (float)
        value_scaled = float(value - source_min) / float(left_span)

        # Convert the 0-1 range into a value in the right range.
        return int(target_min + (value_scaled * right_span))

    def draw(self):
        '''
        Displays the drawing
        '''

        self.resetErrors()

        # If all the inputs are correct
        if self.checkData():
            # List of coordinates extracted by the iso files
            coords = self.getCoordinates()
            num_coords = len(coords)
            # Prepare the scene
            self.setScene()

            # Absolute z_max value used to calculate the color of the segments
            abs_z_max = abs(self.z_max)

            draw_color = self.ui.chk_color.isChecked()
            draw_gradient = self.ui.chk_gradient.isChecked()

            # If the user doesn't want to fit the visible area AND the scale factor is > 1
            # The second condition is to force the scaling down when the drawing size exceeds the canvas size
            # in that case the scale factor will be < 1 and must not be changed or part of it will not be visible
            if not self.ui.chk_fit.isChecked() and self.scale_factor > 1:
                # Set the scale factor to a neutral value
                self.scale_factor = 1

            # Limit the values to the 3 decimals and print them on the proper label
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

            # Progress dialog to show while processing the list of coordinates
            pd = QProgressDialog('Elaborazione primitive',
                                 'Annulla', 0, num_coords-1, self)
            pd.setModal(True)
            pd.setMinimumDuration(0)

            # It is not convenient to update the progress bar at each loop iteration, that would
            # result in a very slow execution, this sets the update to be executed once every
            # 1/200 of the total iterations
            progress_step = int(num_coords / 200)

            for i in range(num_coords):

                # If 1/200 of the instructions have been processed
                if progress_step != 0 and i % progress_step == 0:
                    # Update the progress dialog
                    pd.setValue(i)

                    # If the cancel button of the progress dialog was clicked
                    if pd.wasCanceled():
                        # Abort the drawing resetting the changed variables
                        self.cancelDrawing()
                        # Stop the loop
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

                    if draw_gradient:

                        start_mapped_color = self.mapRange(
                            abs(current_position[2]), 10, abs_z_max, 0, 255)

                        end_mapped_color = self.mapRange(
                            abs(coords[i][2]), 10, abs_z_max, 0, 255)

                        if draw_color:
                            # Yellow to Blue color
                            start_color = QtGui.QColor(
                                255-start_mapped_color, 255-start_mapped_color, start_mapped_color)

                            end_color = QtGui.QColor(
                                255-end_mapped_color, 255-end_mapped_color, end_mapped_color)
                        else:
                            # Grayscale
                            start_color = QtGui.QColor(
                                255-start_mapped_color, 255-start_mapped_color, 255-start_mapped_color)

                            end_color = QtGui.QColor(
                                255-end_mapped_color, 255-end_mapped_color, 255-end_mapped_color)

                        gradient = QtGui.QLinearGradient(p1, p2)
                        gradient.setColorAt(0, start_color)
                        gradient.setColorAt(1, end_color)

                        pen = QtGui.QPen(QtGui.QBrush(gradient), 1)
                    else:
                        if draw_color:
                            color = QtGui.QColor(0, 0, 255)
                            pen = QtGui.QPen(QtGui.QBrush(color), 1)
                        else:
                            color = QtGui.QColor(0, 0, 0)
                            pen = QtGui.QPen(QtGui.QBrush(color), 1)

                    # Add the segment to the scene
                    self.scene.addLine(QtCore.QLine(p1, p2), pen=pen)

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

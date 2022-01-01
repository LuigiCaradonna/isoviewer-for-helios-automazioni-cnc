from PySide6 import (QtCore)
from PySide6.QtWidgets import QMainWindow, QFileDialog, QGraphicsScene
from UiMainwindow import Ui_MainWindow
import os.path
import math
import time
from ResettableTimer import ResettableTimer


class MyGraphicsScene(QGraphicsScene):

    # Dichiaro un segnale
    signalMousePos = QtCore.Signal(QtCore.QPointF)

    # Override della funzione mouseMoveEvent per emettere il segnale custom
    def mouseMoveEvent(self, event):
        pos = event.lastScenePos()
        # Emetto il segnale passandogli la posizione del mouse
        self.signalMousePos.emit(pos)


class MainWindow(QMainWindow):

    iso_file = ''
    scale_factor = 1
    # Dimensioni della scena
    scene_w = 0
    scene_h = 0

    # Usando l'antialiasing per il canvas (attivo per default)
    # self.ui.canvas.DontAdjustForAntialiasing(False)
    # l'area del canvas viene estesa di 4 pixel oltre l'area visibile, facendo sballare
    # di 4px la posizione del mouse, questo servirà a compensazione. Va messo a 0 se
    # l'antialiasing non si usa
    canvas_expanded = 4

    # Posizioni minime e massime della lavorazione
    x_min = 10000
    y_min = 10000
    z_max = 0
    x_max = 0
    y_max = 0

    # Da aggiornare ad ogni tracciamento di una linea, servirà per calcolare di quanto
    # si alza l'utensile quando si deve staccare dal piano di incisione
    last_z = 0

    # Saranno valorizzati per portare tutte le coordinate in area positiva se necessario
    offset_x = 0
    offset_y = 0

    # Indica se è stata disegnata una primitiva sulla scena
    iso_drawn = False
    # Indica se è stato avviato il thread del timer
    timer_running = False
    # Indica se è stato avviato un timer
    timer_started = False

    tmr = None

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.btn_draw.clicked.connect(self.draw)
        self.ui.btn_reset.clicked.connect(self.resetScene)
        self.ui.btn_browse_file.clicked.connect(self.browseFile)
        self.scene = MyGraphicsScene()
        # Intercetta il segnale emesso dalla sottoclasse e collegalo alla funzione mousePosition()
        self.scene.signalMousePos.connect(self.mousePosition)
        # Per abilitare il tracciamento del mouse senza bisogno di cliccare
        self.ui.canvas.setMouseTracking(True)
        # L'antialiasing può servire solo se si muovono oggetti sulla scena, non è questo lo scopo del tool
        # inoltre se l'antialiasing è attivo, l'area del canvas si espande di 4px
        # self.ui.canvas.DontAdjustForAntialiasing(True)
        self.ui.canvas.setScene(self.scene)
        self.ui.canvas.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.ui.lbl_x_min_value.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB')
        self.ui.lbl_x_max_value.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB')
        self.ui.lbl_y_min_value.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB')
        self.ui.lbl_y_max_value.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB')
        self.ui.lbl_z_max_value.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB')
        self.ui.lbl_rectangle_value.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB')
        self.ui.lbl_working_time_value.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB')
        self.ui.lbl_mouse_pos_x.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB')
        self.ui.lbl_mouse_pos_y.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB')
        self.ui.lbl_offset_value.setStyleSheet(
            'background-color: #DDDDDD; border: 1px solid #BBBBBB')

        self.tmr = ResettableTimer(timeout=3, callback=self.draw)

    def timerManager(self):
        # Se il thread del timer non è ancora stato avviato
        if not self.timer_running:
            # Avvia il thread
            self.tmr.start()
            # Indica che il thread è attivo
            self.timer_running = True
            # Avvia il timer
            self.tmr.start_timer()
            # Indica che il timer è stato avviato
            self.timer_started = True
        # Il thread è attivo, ma se non c'è un timer attivo
        elif not self.timer_started:
            # Avvia il timer
            self.tmr.start_timer()

            # Indica che il timer è stato avviato
            self.timer_started = True
        # Se sia il thread che il timer sono attivi
        else:
            # Resetta il timer
            self.tmr.restart_timer()

    def resizeEvent(self, event):
        '''
        Override del metodo della classe QMainWindow
        '''
        # Se c'è qualcosa sulla scena
        if self.iso_drawn:
            # Gestisci il timer che invocherà la rigenerazione del disegno
            self.timerManager()

        # Quando si ridimensiona la finestra, vanno reimpostate le misure della scena
        self.scene_w, self.scene_h = self.getCanvasSize()

    def showEvent(self, event):
        '''
        Override del metodo chiamato quando la MainWindow è pronta e visualizzata
        '''
        # Inizializzo le dimensioni della scena per avere una posizione valida del mouse anche prima
        # di caricare una primitiva
        self.scene_w, self.scene_h = self.getCanvasSize()

        # print(str(self.scene_w) + ' X ' + str(self.scene_h))

    def getCanvasSize(self):
        '''Restituisce le dimensioni visibili del canvas'''
        return (self.ui.canvas.width() - self.canvas_expanded, self.ui.canvas.height() - self.canvas_expanded)

    def resetCoordinatesLimits(self):
        '''Resetta le posizioni minime e massime della lavorazione'''
        self.x_min = 10000
        self.y_min = 10000
        self.z_max = 0
        self.x_max = 0
        self.y_max = 0
        self.offset_x = 0
        self.offset_y = 0

    def browseFile(self):
        '''Apre la finestra di dialogo per la scelta del file iso'''
        self.iso_file, _ = QFileDialog.getOpenFileName(self, 'OpenFile')
        self.ui.lbl_selected_file.setText(self.iso_file)

    def resetErrors(self):
        '''
        Resetta i campi di input, la label contenente il file iso scelto e la status bar
        per eliminare eventuali indicazioni di errore
        '''
        self.ui.in_width.setStyleSheet("border: 1px solid black")
        self.ui.in_height.setStyleSheet("border: 1px solid black")
        self.ui.in_tool_speed.setStyleSheet("border: 1px solid black")
        self.ui.lbl_selected_file.setStyleSheet("border: none")
        self.ui.statusbar.showMessage('')

    def checkData(self):
        '''Valida i dati immessi prima di elaborare il file iso'''

        # Verifica se il file indicato esiste e se è un file PGR
        if not os.path.isfile(self.iso_file) or not self.iso_file[-3:] == 'PGR':
            self.ui.lbl_selected_file.setStyleSheet("border: 1px solid red")
            self.ui.statusbar.showMessage('Indicare un file ISO valido')
            return False
        # Se il file indicato esiste ed ha estensione PGR
        else:
            with open(self.iso_file) as f:
                # Se non inizia con "QUOTE RELATIVE"
                if f.readline().rstrip() != 'QUOTE RELATIVE':
                    self.ui.lbl_selected_file.setStyleSheet(
                        "border: 1px solid red")
                    self.ui.statusbar.showMessage(
                        'Indicare un file ISO valido')
                    return False

        # Se il campo width è vuoto, impostalo a 0
        if self.ui.in_width.text() == '':
            self.ui.in_width.setText('0')
        # Controlla se è stato inserito un valore non valido nel campo larghezza
        if not self.ui.in_width.text().isnumeric() or int(self.ui.in_width.text()) < 0:
            self.ui.in_width.setStyleSheet("border: 1px solid red")
            self.ui.statusbar.showMessage(
                'Indicare una larghezza valida (numero intero positivo o 0)')
            return False
        # E' stato indicato un numero valido
        else:
            # Ma potrebbe essere un decimale, lo rimpiazzo con la sola parte intera
            self.ui.in_width.setText(str(int(self.ui.in_width.text())))

        # Se il campo height è vuoto, impostalo a 0
        if self.ui.in_height.text() == '':
            self.ui.in_height.setText('0')
        # Verifica se è stato inserito un numero valido nel campo altezza
        if not self.ui.in_height.text().isnumeric() or int(self.ui.in_height.text()) < 0:
            self.ui.in_height.setStyleSheet("border: 1px solid red")
            self.ui.statusbar.showMessage(
                'Indicare un\'altezza valida (numero intero positivo o 0)')
            return False
        # E' stato indicato un numero valido
        else:
            # Ma potrebbe essere un decimale, lo rimpiazzo con la sola parte intera
            self.ui.in_height.setText(str(int(self.ui.in_height.text())))

        # Se il campo tool speed è vuoto, impostalo a 0
        if self.ui.in_tool_speed.text() == '':
            self.ui.in_tool_speed.setText('0')
        # Verifica se è stato inserito un numero valido nel campo tool speed
        if not self.ui.in_tool_speed.text().isnumeric() or int(self.ui.in_tool_speed.text()) < 0:
            self.ui.in_tool_speed.setStyleSheet("border: 1px solid red")
            self.ui.statusbar.showMessage(
                'Indicare una velocità valida (numero intero positivo)')
            return False
        # E' stato indicato un numero valido
        else:
            # Ma potrebbe essere un decimale, lo rimpiazzo con la sola parte intera
            self.ui.in_tool_speed.setText(
                str(int(self.ui.in_tool_speed.text())))

        # Controllo se è stata indicata solo la larghezza e non l'altezza
        if int(self.ui.in_width.text()) > 0 and self.ui.in_height.text() == '0':
            self.ui.in_height.setStyleSheet("border: 1px solid red")
            self.ui.statusbar.showMessage(
                'Indicare entrambe le dimensioni o nessuna')
            return False

        # Controllo se è stata indicata solo l'altezza e non la larghezza
        if int(self.ui.in_height.text()) > 0 and self.ui.in_width.text() == '0':
            self.ui.in_width.setStyleSheet("border: 1px solid red")
            self.ui.statusbar.showMessage(
                'Indicare entrambe le dimensioni o nessuna')
            return False

        return True

    def scaleFactor(self, w, h):
        '''
        Calcola il fattore di scala per ridimensionare il disegno della lavorazione
        in modo che si adatti alle dimensioni della scena
        '''
        # N.B. non uso self.scene_w e self.scene_h impostate in showEvent() al posto di
        # per le dimensioni della scena, perché dopo l'apparizione della finestra, questa può essere
        # ridimensionata e quindi le dimensioni del canvas potrebbero essere diverse

        # Dimensioni del canvas
        canvas_w, canvas_h = self.getCanvasSize()

        # Calcola il fattore di scala che porta la larghezza della scena ad eguagliare quella del canvas
        scale_x = canvas_w / w
        # Calcola il fattore di scala che porta l'altezza della scena ad eguagliare quella del canvas
        scale_y = canvas_h / h

        return scale_x if scale_x <= scale_y else scale_y

    def resetScene(self, reset_to_draw=False):
        '''
        Reimposta la scena allo stato iniziale
        Param - boolean draw: se false resetta anche il file selezionato
        '''
        # Resetta la scena
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
            self.iso_file = ''
            self.ui.lbl_selected_file.setText('')
        # Indica che la scena è vuota
        self.iso_drawn = False

    def setScene(self):
        '''Prepara la scena per contenere il disegno della lavorazione appena elaborata'''

        # Resetta la scena
        self.resetScene(True)

        # Dimensioni indicate per la lastra
        width = float(self.ui.in_width.text())
        height = float(self.ui.in_height.text())

        # Dimensioni del canvas
        canvas_w, canvas_h = self.getCanvasSize()

        # Se è stata indicata una larghezza è stata anche indicata un'altezza, se ne accerta checkData()
        if width > 0:
            # Calcola il fattore di scala per adeguarsi alla dimensione del canvas
            self.scale_factor = self.scaleFactor(width, height)

            # Assegna la dimensione della lastra scalata in base alla dimensione del canvas
            self.scene_w = width * self.scale_factor
            self.scene_h = height * self.scale_factor

        else:
            # Le dimensioni della lastra non sono state indicate, quindi come dimensione
            # per calcolare il fattore di scala ed adeguarsi alla dimensione del canvas
            # si prende l'ingombro della lavorazione
            self.scale_factor = self.scaleFactor(self.x_max, self.y_max)

            # Assegna le dimensioni del canvas
            self.scene_w = canvas_w
            self.scene_h = canvas_h

        # Imposta la scena grande quanto il canvas
        self.scene.setSceneRect(0, 0, canvas_w, canvas_h)

        # print(str(self.scale_factor))

        # Se è stata indicata una dimensione per la lastra
        if width > 0:
            # Traccia il rettangolo che la definisce. Nel caso in cui la dimensione non è indicata
            # il rettangolo sarebbe sempre pari alla dimensione del canvas e non serve
            self.scene.addRect(QtCore.QRectF(0, 0, self.scene_w, self.scene_h))

    def getCoordinates(self):
        '''Legge il file iso ed estrapola coordinate e dati utili al tracciamento del disegno della lavorazione'''
        # Indica se ci si trova sul primo punto in cui l'utensile si abbassa per la lavorazione
        first_down = False
        # Il posizionamento per il punto su cui si inizia a lavorare è dopo il secondo G12 Z0
        # in questa variabile porto il conto per riconoscerlo
        z_down = 0

        # apri il file ISO
        original_file = open(self.iso_file, 'r')
        # copia il contenuto del file
        iso = original_file.readlines()
        # chiudi il file
        original_file.close()

        # Resetta i valori massimi e minimi delle coordinate
        self.resetCoordinatesLimits()
        # Lista di coordinate ed indicazioni di movimento per disegnare il percorso dell'utensile
        coords = []

        # Cicla su tutte le righe del file
        for line_of_code in iso:
            # Righe che iniziano con "G02 X" indicano posizioni che producono incisioni - Es.: G02 X508 Y556 Z-13
            if line_of_code.find('G02 X') == 0:
                # Dividi la riga di codice
                subline = line_of_code.split(' ')

                # Il secondo elemento è la coordinata X, parto da 1 per eliminare il carattere X iniziale
                x = float('{:.3f}'.format(float(subline[1][1:])))

                # Aggiorna la x minima se necessario
                if x <= self.x_min:
                    self.x_min = x
                # Aggiorna la x massima se necessario
                if x >= self.x_max:
                    self.x_max = x

                # Il terzo elemento è la coordinata Y, parto da 1 per eliminare il carattere Y iniziale
                y = float('{:.3f}'.format(float(subline[2][1:])))

                # Aggiorna la y minima se necessario
                if y <= self.y_min:
                    self.y_min = y
                # Aggiorna la y massima se necessario
                if y >= self.y_max:
                    self.y_max = y

                # Il quarto elemento è la coordinata Z, parto da 1 per eliminare il carattere Z iniziale
                z = float('{:.3f}'.format(float(subline[3][1:])))
                # Aggiorna la z massima se necessario
                if z < self.z_max:
                    self.z_max = z

                # Aggiungo alla lista delle coordinate utili
                coords.append((x, y, z))

            # Righe che iniziano con "G12 X" indicano un riposizionamento sul piano XY
            elif line_of_code.find('G12 X') == 0:
                # Quando si considerano gli spostamenti si devono calcolare X e Y min/max solo se
                # è la coordinata di inizio lavorazione (non da dove parte l'utensile, ma il primo punto
                # su cui si abbassa per iniziare la lavorazione)
                # altrimenti X e Y min sarebbero sempre 0 visto che ci si muove partendo dall'origine
                # mentre X e Y max negli spostamenti al più eguagliano i valori
                # che si hanno durante l'incisione

                # Dividi la riga di codice
                subline = line_of_code.split(' ')

                # Prendo la coordinata X, parto da 1 per eliminare il carattere X iniziale
                x = float('{:.3f}'.format(float(subline[1][1:])))

                # Prendo la coordinata Y, parto da 1 per eliminare il carattere Y iniziale
                y = float('{:.3f}'.format(float(subline[2][1:])))

                # Se ci si trova sul primo punto in cui l'utensile si abbassa per lavorare
                if first_down:
                    # Aggiorna la x minima se necessario
                    if x <= self.x_min:
                        self.x_min = x
                    # Aggiorna la x massima se necessario
                    if x >= self.x_max:
                        self.x_max = x

                    # Aggiorna la y minima se necessario
                    if y <= self.y_min:
                        self.y_min = y
                    # Aggiorna la y massima se necessario
                    if y >= self.y_max:
                        self.y_max = y

                    # Resetto la variabile, da ora in poi non si userà più
                    first_down = False

                # Aggiungo alla lista delle coordinate utili, nella lista sarà sempre preceduta da un "up"
                coords.append((x, y, 0))

            # Le righe "G02 Z" indicano il movimento solo verticale dell'utensile per iniziare un'incisione
            elif line_of_code.find('G02 Z') == 0:
                # Dividi la riga di codice
                subline = line_of_code.split(' ')

                # Indico che la prossima coordinata sarà la discesa dell'utensile
                coords.append(('down', 0, 0))

                # Riporto di quanto si abbassa l'utensile
                coords.append(
                    (0, 0, float('{:.3f}'.format(float(subline[1][1:])))))

            # Le righe "G12 Z0" indicano il movimento solo verticale dell'utensile per terminare un'incisione
            elif line_of_code.find('G12 Z0') == 0:
                # Se non sono ancora al secondo G12 Z0
                if z_down < 2:
                    # Incrementa il contatore
                    z_down += 1
                # Se ho appena trovato il secondo G12 Z0
                if z_down == 2:
                    # Imposta il flag a True per indicare che qui si abbasserà l'utensile per la prima volta
                    first_down = True

                # Riporto l'informazione nella lista delle incisioni, esempio:
                # G02 X100 Y0 Z-10
                # G02 X0 Y0 Z-10
                # G12 Z0
                # G12 X150 Y100
                # G02 Z-10
                # G02 X150 Y200 Z-10
                # In questo caso, nella lista delle coordinate per le incisioni ci sarebbero
                # ((100, 0), (0, 0), (150, 100))
                # ma la linea da (0, 0) a (150, 100) non è da disegnare, quindi "up" indicherà questa situazione.
                # Inoltre quando si incontra un "up" si dovrà leggere l'ultima quota Z per sapere di quanto si alza l'utensile
                # nello specifico sarà il valore assoluto dell'ultima quota Z
                coords.append(('up', 0, 0))

        # Controlla se la x e/o la y in qualche punto diventano negative e riporta tutto in area positiva
        # altrimenti non sarà possibile la visualizzazione visto che il canvas accetta solo
        # coordinate positive
        if self.x_min < 0:
            self.offset_x = abs(self.x_min)
            self.x_min = 0
            self.x_max += self.offset_x

        if self.y_min < 0:
            self.offset_y = abs(self.y_min)
            self.y_min = 0
            self.y_max += self.offset_y

        # Se almeno uno degli offset è stato impostato
        if self.offset_x > 0 or self.offset_y > 0:
            num_coords = len(coords)

            # Per ogni entry della lista delle coordinate
            for i in range(num_coords-1):
                # Se la tupla corrente non contiene indicazioni di movimento
                if coords[i][0] != 'up' and coords[i][0] != 'down':
                    # Addiziona gli offset per portare il disegno in area positiva, la z resta invariata
                    new_x = float(coords[i][0]) + self.offset_x
                    new_y = float(coords[i][1]) + self.offset_y
                    coords[i] = (new_x, new_y, coords[i][2])

        return coords

    def workingTime(self, eng_dst, pos_dst):
        '''Calcola una stima del tempo di lavorazione'''
        tot_dst = eng_dst + pos_dst

        seconds = (tot_dst / float(self.ui.in_tool_speed.text())) * 60

        self.ui.lbl_working_time_value.setText(
            time.strftime('%H:%M:%S', time.gmtime(seconds)))

    def mousePosition(self, pos):
        '''Mostra sull'interfaccia le coordinate del puntatore del mouse adeguate al fattore di scala in uso'''
        self.ui.lbl_mouse_pos_x.setText(
            str('{:.1f}'.format(float(pos.x() * (1/self.scale_factor)))))
        self.ui.lbl_mouse_pos_y.setText(
            str('{:.1f}'.format(float((self.scene_h - pos.y()) * (1/self.scale_factor)))))

        # print('x: ' + str(int(pos.x())) + ' | y: ' + str(int(pos.y())))

    def draw(self):
        '''Traccia il disegno della lavorazione'''

        # Se è stato avviato un timer, vuol dire che la funzione
        # è stata chiamata al suo scadere
        if self.timer_started:
            # Indica che non c'è più un timer attivo
            self.timer_started = False

        self.resetErrors()

        if self.checkData():
            coords = self.getCoordinates()
            num_coords = len(coords)
            self.setScene()

            # Limita il valore a 3 decimali e stampa il valore sulla label corrispondente
            self.ui.lbl_x_min_value.setText('{:.3f}'.format(self.x_min))
            self.ui.lbl_x_max_value.setText('{:.3f}'.format(self.x_max))
            self.ui.lbl_y_min_value.setText('{:.3f}'.format(self.y_min))
            self.ui.lbl_y_max_value.setText('{:.3f}'.format(self.y_max))
            self.ui.lbl_z_max_value.setText('{:.3f}'.format(self.z_max))

            # Stampa sulla label offset se il disegno è stato spostato,
            # in tal caso vorrebbe dire che ci sono coordinate negative sulla primitiva
            if self.offset_x > 0 and self.offset_y > 0:
                self.ui.lbl_offset_value.setText('X - Y')
            elif self.offset_x > 0 and self.offset_y == 0:
                self.ui.lbl_offset_value.setText('X')
            elif self.offset_x == 0 and self.offset_y > 0:
                self.ui.lbl_offset_value.setText('Y')
            else:
                self.ui.lbl_offset_value.setText('No')

            # Ingombro della lavorazione
            drawing_w = self.x_max - self.x_min
            drawing_h = self.y_max - self.y_min

            self.ui.lbl_rectangle_value.setText(
                '{:.3f}'.format(drawing_w) + ' X ' + '{:.3f}'.format(drawing_h))

            engraving_dst = 0
            positioning_dst = 0
            # Indica la posizione corrente dell'utensile, inizializzata sull'origine
            current_position = (0, 0, 0)
            lines = 0

            # Indica se si sta correntemente abbassando l'utensile
            lowering = False
            # Indica se si sta eseguendo un'incisione
            drawing = False
            # Indica se ci si deve riposizionare
            repositioning = False

            for i in range(num_coords):
                # Se non sono alla fine della primitiva ed è indicato di alzare l'utensile
                # vuol dire che sta per aver luogo un riposizionamento
                if i < num_coords and coords[i][0] == 'up':
                    # Addiziona il cambio di quota alla distanza degli spostamenti
                    positioning_dst += abs(self.last_z)

                    # Imposta i flag
                    lowering = False
                    drawing = False
                    repositioning = True

                    # Termina l'iterazione
                    continue

                # Se sono alla fine della primitiva e si deve alzare l'utensile,
                # l'unica distanza da considerare è lo spostamento verticale perché poi finirà la lavorazione
                elif coords[i][0] == 'up':
                    # Addiziona il cambio di quota alla distanza degli spostamenti
                    positioning_dst += abs(self.last_z)

                    # Aggiorna la posizione corrente
                    current_position = (
                        current_position[0], current_position[1], 0)

                    # Imposta i flag
                    lowering = False
                    drawing = False
                    repositioning = False

                    # Termina l'iterazione
                    continue

                # Se è indicato di abbassare l'utensile (non controllo di essere alla fine della primitiva
                # perché se si abbassa l'utensile, di sicuro c'è ancora qualcosa da fare)
                if coords[i][0] == 'down':
                    # Non aggiorno qui la quota Z perché dovrei leggere la tupla seguente per saperlo
                    # Rimando quindi l'operazione alla prossima iterazione, che leggendo lowering=True
                    # saprà che si dovrà eseguire il calcolo

                    # Imposta i flag
                    lowering = True
                    drawing = False
                    repositioning = False

                    # Termina l'iterazione
                    continue

                # Da qui, sicuramente ci sono solo tuple con coordinate e non indicazioni di movimenti

                # Se si sta riposizionando l'utensile sul piano XY
                if repositioning:
                    dx = pow(coords[i][0] - current_position[0], 2)
                    dy = pow(coords[i][1] - current_position[1], 2)
                    positioning_dst += math.sqrt(dx + dy)

                    # Aggiorno la posizione corrente, la Z non cambia sui riposizionamenti XY
                    current_position = (
                        coords[i][0], coords[i][1], current_position[2])

                    # Imposto i flag
                    lowering = False
                    drawing = False
                    repositioning = False

                    # Termina l'iterazione
                    continue

                # Se si sta abbassando l'utensile
                if lowering:
                    # Di sicuro qui ci sarà la tupla contenente solo il cambio di quota Z
                    positioning_dst += abs(coords[i][2])

                    # Aggiorna la coortinata corrente
                    current_position = (
                        current_position[0], current_position[1], coords[i][2])

                    # Imposto i flag
                    lowering = False
                    drawing = True
                    repositioning = False

                    # Termina l'iterazione
                    continue

                # Se si sta incidendo
                if drawing:
                    # Calcolo la distanza dell'incisione
                    dx = pow(coords[i][0] - current_position[0], 2)
                    dy = pow(coords[i][1] - current_position[1], 2)
                    dz = pow(coords[i][2] - current_position[2], 2)
                    engraving_dst += math.sqrt(dx + dy + dz)

                    # Disegno il segmento fino al punto indicato dalla coordinata
                    # la X resta come indicata nel file PGR, la Y invece va ricalcolata perché
                    # l'asse Y nel PGR è considerato dal basso verso l'alto, nel Canvas invece
                    # è considerato dall'alto verso il basso
                    p1 = QtCore.QPoint(
                        current_position[0] * self.scale_factor,
                        self.scene_h -
                        (current_position[1] * self.scale_factor)
                    )

                    p2 = QtCore.QPoint(
                        coords[i][0] * self.scale_factor,
                        self.scene_h - (coords[i][1] * self.scale_factor)
                    )

                    # Aggiungo il segmento alla scena
                    self.scene.addLine(QtCore.QLine(p1, p2))

                    # Aggiorna la posizione corrente
                    current_position = (
                        coords[i][0], coords[i][1], coords[i][2])

                    # Aggiorno il valore della Z da usare per calcolare la distanza del movimento quando si alza l'utensile
                    self.last_z = coords[i][2]

                    # Aggiorno il conto delle linee
                    lines += 1

                    # Imposto i flag
                    lowering = False
                    drawing = True
                    repositioning = False

                    # Termina l'iterazione
                    continue

            # Indico che sulla scena è stato disegnato qualcosa
            self.iso_drawn = True
            # Calcolo la stima del tempo di lavorazione
            self.workingTime(engraving_dst, positioning_dst)

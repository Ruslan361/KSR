from PySide6.QtWidgets import QCheckBox, QApplication, QPushButton, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, QDoubleSpinBox, QVBoxLayout, QLineEdit, QLabel, QDialog, QTableWidget, QTableWidgetItem, QComboBox, QFileDialog
from PySide6.QtGui import QDoubleValidator, QIntValidator
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import sys
import json
import os
import typing
import ctypes
import platform
import subprocess
import pandas as pd
from RK import l1_2  # Импортируем l1_2
from custom_loyauts import LatexRendererLayout, GraphLayout, IntNumberInput, FloatNumberInput, NumericalIntegrationParametersInput, StartConditions2, XlimitsInput, NewWindow, ABInput, ErrorDialog

class MainTask2Plotter:
    def __init__(self, graph_layout, graph_combobox):
        self.graph_layout = graph_layout
        self.graph_combobox = graph_combobox

    def plot(self, x, u, du):
        self.graph_layout.clear()
        selected_graph = self.graph_combobox.currentText()

        if selected_graph == "x - v(x)":
            self.graph_layout.plot(x, u, label="v(x)")
            self.graph_layout.set_ylabel('v') 
            self.graph_layout.set_xlabel("x")
        elif selected_graph == "x - v'(x)":
            self.graph_layout.plot(x, du, label="v'(x)")
            self.graph_layout.set_xlabel("x")
            self.graph_layout.set_ylabel('$\\dot{x}$')
        elif selected_graph == "v - v'(x)":
            self.graph_layout.plot(u, du, label="v`(u)")
            self.graph_layout.set_ylabel('$\\dot{v}$')
            self.graph_layout.set_xlabel('v')
        elif selected_graph == "v`-v":
            self.graph_layout.plot(du, u, label="u(u`)")
            self.graph_layout.set_xlabel('$\\dot{v}$')
            self.graph_layout.set_ylabel('v')

        self.graph_layout.set_title(f"График: {selected_graph}")
        
        self.graph_layout.legend()
        self.graph_layout.draw()

class MainTask2SettingsManager:
    def __init__(self, settings_file, ui_elements):
        self.settings_file = settings_file
        self.ui_elements = ui_elements

    def save_settings(self, df, filename):
        # Сохранение DataFrame в CSV файл
        csv_filename = filename + ".csv"
        df.to_csv(csv_filename, sep=";", index=False, header=False)

        # Сохранение настроек в JSON файл
        settings = {
            "initialConditions": {
                "X0": self.ui_elements["initialConditions"].X0Input.floatNumberLineEdit.text(),
                "UX0": self.ui_elements["initialConditions"].UX0Input.floatNumberLineEdit.text(),
                "DUX0": self.ui_elements["initialConditions"].DUX0Input.floatNumberLineEdit.text()
            },
            "xlimits": {
                "endX": self.ui_elements["xlimitsInput"].endXInput.floatNumberLineEdit.text(),
                "epsilonBorder": self.ui_elements["xlimitsInput"].epsilonBorderInput.floatNumberLineEdit.text()
            },
            "numericalIntegrationParameters": {
                "h0": self.ui_elements["numericalIntegrationParametersInput"].h0Input.floatNumberLineEdit.text(),
                "epsilon": self.ui_elements["numericalIntegrationParametersInput"].epsilonInput.floatNumberLineEdit.text()
            },
            "abinput": {
                "a": self.ui_elements["abinput"].AInput.floatNumberLineEdit.text(),
                "b": self.ui_elements["abinput"].BInput.floatNumberLineEdit.text()
            },
            "amountOfSteps": self.ui_elements["amountOfStepsInput"].intNumberLineEdit.text(),
            "selectedGraph": self.ui_elements["graphComboBox"].currentText(),
            "csv_filename": os.path.relpath(csv_filename, os.path.dirname(filename)),  # Относительный путь
            "task_number": 2
        }

        json_filename = filename + ".json"
        #dirname, file = os.path.split(os.path.abspath(__file__))
        #json_filename = os.path.join(dirname, (filename + ".json"))
        try:
            with open(json_filename, "w") as f:
                json.dump(settings, f, indent=4)
            print(f"Настройки сохранены в файлы {json_filename} и {csv_filename}")
        except Exception as e:
            print(f"Ошибка при сохранении настроек: {e}", file=sys.stderr)
            ErrorDialog(f"Ошибка при сохранении настроек: {e}").exec()

    def load_settings(self):
        filename, _ = QFileDialog.getOpenFileName(
            None, "Загрузить настройки", "", "JSON files (*.json)"
        )
        if filename:
            try:
                with open(filename, "r") as f:
                    settings = json.load(f)

                if "task_number" not in settings or settings["task_number"] != 2:
                    print("Ошибка: Загруженный файл настроек не соответствует основной задаче 2.")
                    ErrorDialog("Ошибка: Загруженный файл настроек не соответствует основной задаче 2.").exec()
                    return

                self.ui_elements["initialConditions"].X0Input.floatNumberLineEdit.setText(settings["initialConditions"]["X0"])
                self.ui_elements["initialConditions"].UX0Input.floatNumberLineEdit.setText(settings["initialConditions"]["UX0"])
                self.ui_elements["initialConditions"].DUX0Input.floatNumberLineEdit.setText(settings["initialConditions"]["DUX0"])
                self.ui_elements["xlimitsInput"].endXInput.floatNumberLineEdit.setText(settings["xlimits"]["endX"])
                self.ui_elements["xlimitsInput"].epsilonBorderInput.floatNumberLineEdit.setText(settings["xlimits"]["epsilonBorder"])
                self.ui_elements["numericalIntegrationParametersInput"].h0Input.floatNumberLineEdit.setText(settings["numericalIntegrationParameters"]["h0"])
                self.ui_elements["numericalIntegrationParametersInput"].epsilonInput.floatNumberLineEdit.setText(settings["numericalIntegrationParameters"]["epsilon"])
                self.ui_elements["abinput"].AInput.floatNumberLineEdit.setText(settings["abinput"]["a"])
                self.ui_elements["abinput"].BInput.floatNumberLineEdit.setText(settings["abinput"]["b"])
                self.ui_elements["amountOfStepsInput"].intNumberLineEdit.setText(settings["amountOfSteps"])
                self.ui_elements["graphComboBox"].setCurrentText(settings["selectedGraph"])

                csv_filename = os.path.join(os.path.dirname(filename), settings["csv_filename"])
                self.ui_elements["parent"].load_dataframe(csv_filename)
                self.ui_elements["parent"].refreshPlot()  # Обновление графика после загрузки

                print(f"Настройки загружены из файла {filename}")
            except Exception as e:
                print(f"Ошибка при загрузке настроек: {e}", file=sys.stderr)
                ErrorDialog(f"Ошибка при загрузке настроек: {e}").exec()

class TabMainTask2(QWidget):
    def __init__(self):
        super().__init__()
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.RK = l1_2()  # Инициализируем l1_2
        self.settings_file = "main_task_2"  # Базовое имя файла без расширения
        self.df = None  # Переменная для хранения DataFrame

        # UI элементы
        #testTaskLayout = LatexRendererLayout()
        #texTask1 = r"$\frac{d^2 u}{dx^2} + a\frac{du}{dx} + b \sin(u) = 0$"
        #testTaskLayout.render(texTask1)
        #self.mainLayout.addLayout(testTaskLayout, 1)

        self.abinput = ABInput()
        self.mainLayout.addLayout(self.abinput)

        self.initialConditions = StartConditions2()
        self.mainLayout.addLayout(self.initialConditions)

        self.xlimitsInput = XlimitsInput()
        self.mainLayout.addLayout(self.xlimitsInput)

        self.numericalIntegrationParametersInput = NumericalIntegrationParametersInput()
        self.mainLayout.addLayout(self.numericalIntegrationParametersInput)

        calculatePushButton = QPushButton()
        calculatePushButton.setText("Начать вычисления")
        self.mainLayout.addWidget(calculatePushButton)
        calculatePushButton.clicked.connect(self.calculateClick)

        self.amountOfStepsInput = IntNumberInput("Максимальное количество шагов")
        self.mainLayout.addLayout(self.amountOfStepsInput)

        self.graph = GraphLayout()
        self.mainLayout.addLayout(self.graph, 3)

        # ComboBox для выбора графика
        self.graphComboBox = QComboBox()
        self.graphComboBox.addItems(["x - v(x)", "x - v'(x)", "v - v'(x)", "v`-v"])
        self.graphComboBox.currentIndexChanged.connect(self.refreshPlot)  # Обновление при выборе
        self.mainLayout.addWidget(self.graphComboBox)

        aboutLoyaut = QHBoxLayout()
        referenceButton = QPushButton()
        referenceButton.setText("Справка")
        referenceButton.clicked.connect(self.referenceButtonClick)
        aboutLoyaut.addWidget(referenceButton)
        ShowTableButton = QPushButton()
        ShowTableButton.setText("Вывести таблицу")
        ShowTableButton.clicked.connect(self.ShowTableButtonClick)
        aboutLoyaut.addWidget(ShowTableButton)

        # Сохранение и загрузка настроек
        saveSettingsButton = QPushButton()
        saveSettingsButton.setText("Сохранить настройки")
        saveSettingsButton.clicked.connect(self.saveSettings)
        aboutLoyaut.addWidget(saveSettingsButton)
        loadSettingsButton = QPushButton()
        loadSettingsButton.setText("Загрузить настройки")
        loadSettingsButton.clicked.connect(self.loadSettings)
        aboutLoyaut.addWidget(loadSettingsButton)

        self.mainLayout.addLayout(aboutLoyaut)

        self.plotter = MainTask2Plotter(self.graph, self.graphComboBox)
        self.settings_manager = MainTask2SettingsManager(self.settings_file, {
            "initialConditions": self.initialConditions,
            "xlimitsInput": self.xlimitsInput,
            "numericalIntegrationParametersInput": self.numericalIntegrationParametersInput,
            "abinput": self.abinput,
            "amountOfStepsInput": self.amountOfStepsInput,
            "graphComboBox": self.graphComboBox,
            "parent": self  # Добавлено для доступа к методам TabMainTask2
        })
        #self.loadSettings()  # Загрузка настроек после создания UI


    def calculateClick(self):
        # ... (код для получения параметров из UI)
        if self._validate_input():
            self._perform_calculation()
            self.tryLoadResult()
            self.refreshPlot()

    def _validate_input(self):
        x_end = self.xlimitsInput.getEndX()
        x0 = self.initialConditions.getX0()
        amount_of_steps = self.amountOfStepsInput.getIntNumber()
        h0 = self.numericalIntegrationParametersInput.getStartStep()
        local_error = self.numericalIntegrationParametersInput.getEpsilonLocalError()
        l = self.abinput.getB()
        if l < x_end:
            self.show_error("Ошибка: Конечная длина вычисления должна быть меньше общей длины стержня.")
            return False

        if x_end <= x0:
            self.show_error("Ошибка: Конечное значение X должно быть больше начального.")
            return False

        if amount_of_steps <= 0:
            self.show_error("Ошибка: Количество шагов должно быть положительным числом.")
            return False

        if h0 <= 0:
            self.show_error("Ошибка: Начальный шаг должен быть положительным числом.")
            return False

        if local_error <= 0:
            self.show_error("Ошибка: Допустимая локальная погрешность должна быть положительным числом.")
            return False

        return True

    def _perform_calculation(self):
        x_end = self.xlimitsInput.getEndX()
        x0 = self.initialConditions.getX0()
        u_x0 = self.initialConditions.getUX0()
        du_x0 = self.initialConditions.getDUX0()
        a = self.abinput.getA()
        b = self.abinput.getB()
        epsilon_border = self.xlimitsInput.getEndEpsilon()
        amountOfSteps = self.amountOfStepsInput.getIntNumber()
        h0 = self.numericalIntegrationParametersInput.getStartStep()
        local_error = self.numericalIntegrationParametersInput.getEpsilonLocalError()

        try:
            self.RK.rk4_adaptive(x0, u_x0, du_x0, x_end, h0, a, b, amountOfSteps, local_error,
                                    epsilon_border)  # Вызываем rk4_adaptive из l1_2
            #else:
                #self.RK.rk_4(x0, u_x0, du_x0, h0, x_end, a, b, amountOfSteps)  # Вызываем rk_4 из l1_2
        except Exception as e:
            self.show_error(f"Ошибка во время вычислений: {e}")

    def refreshPlot(self):
        # x0 = self.ui.initial_conditions.getX0()
        # u_x0 = self.ui.initial_conditions.getUX0()
        # du_x0 = self.ui.initial_conditions.getDUX0()
        x0 = 0
        u_x0 = 0
        du_x0 = 0
        if self.df is not None:
            X = self.getColumnValues(self.df, 'x')
            X.insert(0, x0)
            V = self.getColumnValues(self.df, 'v')
            V.insert(0, u_x0)
            dV = self.getColumnValues(self.df, 'v\'')
            dV.insert(0, du_x0)
        if self.df is not None:
            self.plotter.plot(self.getColumnValues(self.df, 'x'), self.getColumnValues(self.df, 'v'), self.getColumnValues(self.df, 'v\''))

    def closeEvent(self, event):
        self.saveSettings()
        event.accept()

    def ShowTableButtonClick(self):
        if self.df is None:
            self.show_error("Ошибка: Сначала необходимо выполнить вычисления.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Таблица результатов")
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        layout.addWidget(table)

        self.columns = ['x', 'v', 'v2i', 'v\'', 'v\'2i', 'v-v2i', 'v\'-v\'2i', 'h', 'Общая ОЛП', 'ОЛП для компоненты V', 'ОЛП для компоненты V`',
                        'c1', 'c2', 'currentLength']  # Замена 'E' на 'e'
        self.data = self.df.values.tolist()[1:]  # Данные для таблицы
        self.data.insert(0, [0, 0, "---", 0, "---", "---", "---", "---", "---", "---", "---", 0, 0, 0])

        table.setColumnCount(len(self.columns))
        table.setRowCount(len(self.data))
        table.setHorizontalHeaderLabels(self.columns)

        for row, data_row in enumerate(self.data):
            for col, value in enumerate(data_row):
                item = QTableWidgetItem(str(value))
                table.setItem(row, col, item)

        dialog.exec()

    def referenceButtonClick(self):
        if self.df is None:
            self.show_error("Ошибка: Сначала необходимо выполнить вычисления.")
            return

        try:
            report = ""
            amountOfIterations = len(self.df['x']) - 1
            report += f"Количество итераций: {amountOfIterations} \n"
            x = self.getColumnValues(self.df, 'x')
            v = self.getColumnValues(self.df, 'v')
            dv = self.getColumnValues(self.df, 'v\'')
            currentLength = self.getColumnValues(self.df, 'currentLength')
            l = len(x)
            difference_between_the_right_border_and_the_last_calculated_point = abs(
                currentLength[l - 1] - self.xlimitsInput.getEndX())
            report += f'Разница между правой границей и последней вычисленной точкой: {difference_between_the_right_border_and_the_last_calculated_point}\n'
            report += f'Начальная и последняя точка численной траектории\n'
            report += f'x0 = 0 v0 = 0 v\'0 = 0\n'
            report += f'xn = {x[l - 1]} vn = {v[l - 1]} v\'n = {dv[l - 1]}\n'
            e = self.getColumnValues(self.df, 'e')  # Замена 'E' на 'e'
            maxError = max(e)  # Замена 'E' на 'e'
            max_error_index = e.index(maxError)
            report += f'Максимальное значение ОЛП {maxError} при x = {x[max_error_index]}\n'
            doubling = self.getColumnValues(self.df, 'c2')
            countOfDoubling = max(doubling)
            report += f'Количество удвоений {countOfDoubling}\n'
            doubling = self.getColumnValues(self.df, 'c1')
            countOfDoubling = max(doubling)
            report += f'Количество делений {countOfDoubling}\n'
            h = self.getColumnValues(self.df, 'h')
            maxStep = max(h)
            minStep = min(h)
            xMinStep = h.index(minStep)
            xMinStep = x[xMinStep]
            xMaxStep = h.index(maxStep)
            xMaxStep = x[xMaxStep]
            report += f'максимальный шаг {maxStep} при x={xMaxStep}\n'
            report += f'Минимальный шаг {minStep} при x={xMinStep}\n'
            window = NewWindow('Справка', report)
            window.show()
            window.exec()

        except Exception as e:
            self.show_error(f"Ошибка во время анализа: {e}")

    def tryLoadResult(self):
        try:
            current_file_path = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file_path)
            current_dir = os.path.join(current_dir, "..") 
            current_dir = os.path.join(current_dir, "output")
            file_path = os.path.join(current_dir, 'output_ksr11.csv')
            self.df = pd.read_csv(file_path, delimiter=";", header=None,
                                 names=['x', 'v', 'v2i', 'v\'', 'v\'2i', 'v-v2i', 'v\'-v\'2i', 'h', 'e', 'e_v', 'e_v\'',
                            'c1', 'c2', 'currentLength'])  # Замена 'E' на 'e'
            
        except Exception as e:
            self.show_error(f"Ошибка во время загрузки: {e}")

    def getColumnValues(self, df, column):
        return pd.to_numeric(df[column][1:], errors='coerce').dropna().tolist()

    def saveSettings(self):
        if self.df is not None:
            filename, _ = QFileDialog.getSaveFileName(None, "Сохранить настройки", self.settings_file, "JSON files (*.json)")
            if filename:
                self.settings_manager.save_settings(self.df, filename[:-5])  # Сохранение DataFrame и настроек

    def loadSettings(self):
        self.settings_manager.load_settings()

    def load_dataframe(self, csv_filename):
        """Загружает DataFrame из CSV файла в зависимости от control_local_error."""
        current_file_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file_path)
        current_dir = os.path.join(current_dir, "..") 
        current_dir = os.path.join(current_dir, "output")
        file_path = os.path.join(current_dir, csv_filename)
        try:
            self.df = pd.read_csv(file_path, delimiter=";", low_memory=False, header=None,
                                    names=['x', 'v', 'v2i', 'v\'', 'v\'2i', 'v-v2i', 'v\'-v\'2i', 'h', 'e', 'e_v',
                                    'e_v\'', 'c1', 'c2', 'currentLength'])  # Замена 'E' на 'e'
        except Exception as e:
            self.show_error(f"Ошибка при загрузке DataFrame: {e}")

    def show_error(self, message):
        """Отображает сообщение об ошибке."""
        print(message, file=sys.stderr)
        ErrorDialog(message).exec()
import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
                             QInputDialog, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import matplotlib.pyplot as plt
import numpy as np

class SearchableTableWidget(QTableWidget):
    pass

class EnvironmentalImpactCalculator(QMainWindow):
    def __init__(self, project):
        super().__init__()
        self.project = project
        self.setWindowTitle(f"Materials for {project.name}")
        self.setGeometry(200, 200, 1000, 800)
        self.setStyleSheet("background-color: #0f1c29; color: white;")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Project name display
        self.project_label = QLabel(f"Project Name: {str(project.name).capitalize()}")
        self.layout.addWidget(self.project_label)

        # Import button
        self.import_button = QPushButton("Import Materials File")
        self.import_button.clicked.connect(self.import_file)
        self.layout.addWidget(self.import_button)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for material...")
        self.search_input.textChanged.connect(self.search_table)
        self.layout.addWidget(self.search_input)
        
        self.title_label = QLabel("Results Table", self)
        # Results table
        self.results_table = QTableWidget()
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.results_table)
        
        # Results label
        self.results_label = QLabel("Results for materials will be displayed here.")
        self.layout.addWidget(self.results_label)

        # Chart controls
        self.chart_combo = QComboBox()
        self.chart_combo.addItems(["GWP", "ODP", "PENRT","PERT","ADPF","POCP","AP","EP","ADPE"])
        self.layout.addWidget(self.chart_combo)
        
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["Pie Chart", "Bar Chart", "Line Chart", "Histogram"])
        self.layout.addWidget(self.chart_type_combo)

        self.chart_button = QPushButton("Show Chart")
        self.chart_button.clicked.connect(self.show_chart)
        self.layout.addWidget(self.chart_button)
        self.flag = True
        self.df = None
        self.selected_materials = []
        self.materials = {}
        self.materials_name = {}

    def import_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if file_name:
            try:
                if file_name.endswith(".csv"):
                    self.df = pd.read_csv(file_name)
                else:
                    self.df = pd.read_excel(file_name)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Unable to open file: {str(e)}")
                return

    def search_table(self):
        
        search_text = self.search_input.text().strip().lower()
        if not search_text:
            self.clear_table()
            return 
        
        if not self.df.empty and self.flag:
            self.table = SearchableTableWidget()
            self.table.itemDoubleClicked.connect(self.process_selected_material)
            # self.table.hide()
            self.layout.addWidget(self.table)
            self.flag = False
            
        if self.table.isHidden():
            self.table.show() 
            
        if self.df is not None:
            matching_rows = self.df[self.df.iloc[:, 0].astype(str).str.strip().str.lower().str.contains(search_text, case=False, na=False)]
            if not matching_rows.empty:
                self.table.setRowCount(len(matching_rows))
            else:
                self.clear_table()
                QMessageBox.warning(self, "No Results", "No result found!")
                return
            self.table.setColumnCount(self.df.shape[1])
            self.table.setHorizontalHeaderLabels(self.df.columns)
            for row in range(self.df.shape[0]):
                for col in range(self.df.shape[1]):
                    item = QTableWidgetItem(str(self.df.iloc[row, col]))
                    item.setBackground(QColor(15, 28, 41)) 
                    item.setForeground(QColor(255, 255, 255)) 

                    self.table.setItem(row, col, item)
            self.table.setStyleSheet("background-color: rgb(15, 28, 41); color: white;")
            
        
    def clear_table(self):
        if self.table is not None:
            self.table.hide()

    def process_selected_material(self, item):
        row = item.row()

    # Collect all the row data
        row_data = {}
        for col in range(self.table.columnCount()):
            column_name = self.table.horizontalHeaderItem(col).text()
            cell_value = self.table.item(row, col).text()
            row_data[column_name] = cell_value

        material_name = row_data.get('Material', 'Unknown')

        quantity, ok = QInputDialog.getDouble(self, "Enter Quantity", f"Enter quantity for {material_name}:", min=0)
        if ok:
            self.clear_table() 
            self.add_material_to_project(material_name,quantity,row_data)
            

    def add_material_to_project(self, material, quantity, row_data):
        index = 2
        excluded_columns = ['Bezugsgroesse', 'Material', 'Bezugseinheit']
        data_list = [col for col in row_data.keys() if col not in excluded_columns]
        self.results_table.setColumnCount(len(data_list) + 2) 
        self.results_table.setHorizontalHeaderLabels(['Material', 'Unit'] + data_list)
        unit = row_data.get('Bezugsgroesse', '')
        unit_symbol = row_data.get('Bezugseinheit', '')
        row_position = self.results_table.rowCount()
        self.results_table.insertRow(row_position)
        self.results_table.setItem(row_position, 0, QTableWidgetItem(material))
        self.results_table.setItem(row_position, 1, QTableWidgetItem(str(unit)+str(unit_symbol)))
        for _, (col, value) in enumerate(row_data.items()):
            if col not in excluded_columns:
                calculated_value = self.calculate_row_result(row_data, quantity, col, unit)
                print("calculated value is ", calculated_value)
                if calculated_value != float(0):
                    if col not in self.materials:
                         self.materials[col] = []
                         self.materials_name[col] = []
                    self.results_table.setItem(row_position, index, QTableWidgetItem(f"{calculated_value:.4f}"))
                    self.materials[col].append(calculated_value)
                    self.materials_name[col].append(material)
                index += 1
    
        self.update_cumulative_results()

        
    def calculate_row_result(self, row, quantity, indicator, unit):
        value = row.get(indicator, None)
        try:
            value = float(value)
        except Exception as err:
            print(err)
            value = value
            
        if value is not None and not pd.isna(value)  and not isinstance(value, str) and value != unit:
            try:
                return quantity * float(value)
            except ValueError:
                print(f"Invalid value for {indicator}: {value}")
        
        return 0.0
    

    def update_cumulative_results(self):
            results_text = ""
            computed_value = {key:sum(value) for key , value in self.materials.items()}
            for key, value in computed_value.items():
                print(f"Total {key} for all materials: {value:.4f}")
                results_text += f"Total {key} for all materials: {value:.4f}\n"
            self.results_label.setText(results_text)


    def show_chart(self):
        if not self.materials:
            QMessageBox.warning(self, "No Results", "Please add materials before viewing the chart.")
            return

        indicator = self.chart_combo.currentText()
        print(indicator)
        chart_type = self.chart_type_combo.currentText()
        values = {key:value for key , value in self.materials.items()}
        labels = {key:value for key , value in self.materials_name.items()}
        if indicator not in values or indicator not in labels:
            QMessageBox.warning(self, "Indicator Error", "Selected indicator is not available in the data.")
            return
        
        if chart_type == "Pie Chart":
            print(values[indicator])
            self.show_pie_chart(labels[indicator], values[indicator], indicator)
        elif chart_type == "Bar Chart":
            print(values[indicator])
            self.show_bar_chart(labels[indicator], values[indicator], indicator)
        elif chart_type == "Line Chart":
            print(values[indicator])
            self.show_line_chart(labels[indicator], values[indicator], indicator)
        elif chart_type == "Histogram":
            print(values[indicator])
            self.show_histogram(labels[indicator], values[indicator], indicator)
            
            
            

    def show_pie_chart(self, labels, sizes, indicator):
        plt.figure(figsize=(7, 7))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title(f'{indicator} - Pie Chart')
        plt.show()

    def show_bar_chart(self, labels, values, indicator):
        plt.figure(figsize=(10, 6))
        plt.bar(labels, values, color='skyblue')
        plt.xlabel('Materials')
        plt.ylabel(indicator)
        plt.title(f'{indicator} - Bar Chart')
        plt.show()

    def show_line_chart(self, labels, values, indicator):
        plt.figure(figsize=(10, 6))
        plt.plot(labels, values, marker='o', color='green')
        plt.xlabel('Materials')
        plt.ylabel(indicator)
        plt.title(f'{indicator} - Line Chart')
        plt.grid(True)
        plt.show()

    def show_histogram(self, values, indicator):
        plt.figure(figsize=(10, 6))
        plt.hist(values, bins=10, color='orange', edgecolor='black')
        plt.xlabel(f'{indicator} Value Ranges')
        plt.ylabel('Frequency')
        plt.title(f'{indicator} - Histogram')
        plt.show()


import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
                             QInputDialog, QMessageBox, QComboBox,QMenu,QAction,QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import matplotlib.pyplot as plt
import numpy as np
import core
import warnings
import re
import os

class SearchableTableWidget(QTableWidget):
    pass

class EnvironmentalImpactCalculator(QMainWindow):
    def __init__(self, project):
        super().__init__()
        self.project = project
        print(self.project)
        self.flag = False
        self.project_name = str(project).lower()
        self.setWindowTitle(f"Materialien für {project}")
        # self.setGeometry(100, 100, 1000, 800)
        # self.showFullScreen()
        self.showMaximized()
        self.setStyleSheet("""
    background-color: #0f1c29;
    color: white;
    font-size: 25px;
    font-family: Arial;
    font-weight: bold;
""")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Project name display
        self.project_label = QLabel(f"Projektname: {str(project).capitalize()}")
        self.layout.addWidget(self.project_label)

        # Import button
        self.import_button = QPushButton("Materialdatei importieren")
        self.import_button.clicked.connect(self.import_file)
        self.layout.addWidget(self.import_button)

        # Search input
        # self.search_input = QLineEdit()
        # self.search_input.setPlaceholderText("Nach Material suchen...")
        # self.search_input.textChanged.connect(self.search_table)
        # self.layout.addWidget(self.search_input)
        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nach Material suchen...")
        self.search_input.textChanged.connect(self.search_table)
        self.search_layout.addWidget(self.search_input)
        self.show_database_button = QPushButton("Datenbank anzeigen")
        self.show_database_button.clicked.connect(self.show_database) 
        self.search_layout.addWidget(self.show_database_button)
        self.save_current_work_button = QPushButton("Projekt speichern")
        self.save_current_work_button.clicked.connect(self.export_work) 
        self.search_layout.addWidget(self.save_current_work_button)
        self.layout.addLayout(self.search_layout)
        
        self.title_label = QLabel("Ergebnistabelle", self)
        # Results table
        self.results_table = QTableWidget()
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.results_table)
        self.results_table.itemDoubleClicked.connect(self.on_item_double_clicked)


        self.flag = False
        self.df = None
        self.table = None
        self.data_list = []
        self.selected_materials = []
        self.materials = {}
        self.materials_name = {}
        self.value_list = {}
        try:
            result_data = core.get_result_table(str(self.project_name).lower())
        except Exception as e:
            result_data = None
        if result_data:
            self.cols = core.get_table_column()
            excluded_columns = ['Bezugsgroesse', 'Material', 'Bezugseinheit','Name (de)','']
            self.data_list = [col for col in self.cols if col not in excluded_columns]
            self.results_table.setColumnCount(len(self.data_list) + 2)
            self.results_table.setHorizontalHeaderLabels(['Material', 'Einheit'] + self.data_list)
            self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.results_table.horizontalHeader().setStyleSheet("""
                                                                    QHeaderView::section{
                                                                     background-color: #0f1c29;
                                                                     color: white;
                                                                     font-weight:bold;   
                                                                    }
                                                                """)
            self.results_table.verticalHeader().setStyleSheet("""
                                                                    QHeaderView::section{
                                                                     background-color: #0f1c29;
                                                                     color: white;
                                                                     font-weight:bold;   
                                                                    }
                                                                """)
            for res in result_data:
                row_position = self.results_table.rowCount()
                self.results_table.insertRow(row_position)
                self.results_table.setItem(row_position, 0, QTableWidgetItem(res['material']))
                self.results_table.setItem(row_position, 1, QTableWidgetItem(str(res['unit']).replace(".",",")))
                for index, col in enumerate(self.data_list, start=2):
                    value = res['data'].get(col, '') 
                    self.results_table.setItem(row_position, index, QTableWidgetItem(str(value).replace(".",",")))
            
            
        
        self.results_label = QLabel("Die Ergebnisse für Materialien werden hier angezeigt.")
        self.layout.addWidget(self.results_label)
        if self.results_table.rowCount()> 0:
            self.update_cumulative_results()

        # Chart controls
        self.chart_combo = QComboBox()
        self.chart_combo.addItems(self.data_list)
        self.layout.addWidget(self.chart_combo)
        
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["Pie Chart", "Bar Chart", "Line Chart", "Histogram"])
        self.layout.addWidget(self.chart_type_combo)

        self.chart_button = QPushButton("Diagramm anzeigen")
        self.chart_button.clicked.connect(self.show_chart)
        self.layout.addWidget(self.chart_button)

                

    
    def import_file(self):
        if core.table_exist():
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setStyleSheet("""    
    font-size: 23px;
    font-family: Arial;
    font-weight: bold;
    """)
            msg_box.setWindowTitle("Warnung: Dateiüberschreibung")

            msg_box.setText(
    """Sie haben bereits eine Datei hochgeladen. Das Hochladen einer neuen Datei überschreibt die vorhandene Datei und löscht alle bisherigen Arbeiten.
Bitte exportieren Sie Ihre vorherige Arbeit, bevor Sie fortfahren. Möchten Sie fortfahren?"""
)
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            response = msg_box.exec_()
            if response == QMessageBox.Yes:
                print("ok continue")
                core.drop_user_table()
                self.close()
            else:
                print("Action canceled.") 
                return
            
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if file_name:
            try:
                warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
                if file_name.endswith(".csv"):
                    self.df = pd.read_csv(file_name)
                else:
                    self.df = pd.read_excel(file_name)
                res = core.create_table(self.df, "materials")
                if res:
                 QMessageBox.information(self,"Erfolgreich",f"Datei erfolgreich in die Datenbank hochgeladen")
                    
            except Exception as e:
                print(e)
                QMessageBox.critical(self, "Fehler", f"Daten konnten nicht in die Datenbanktabelle hochgeladen werden:")
                return
            
            
            
    def export_work(self):
        default_csv = "default.csv"
        default_excel = "default.xlsx"
        default_pdf = "default.pdf"
        
        options = QFileDialog.Options()
        df = core.fetch_result_data(self.project_name) 
        if df is not None and not df.empty:
            # Display the dialog with the appropriate default file name based on user selection
            file_name, _ = QFileDialog.getSaveFileName(self, "Ergebnisse exportieren", "", 
                                                    "Excel Files (*.xlsx);;CSV Files (*.csv);;PDF Files (*.pdf)", 
                                                    options=options,
                                                    initialFilter="CSV Files (*.csv)" if default_csv.endswith('.csv') else "Excel Files (*.xlsx)")
            if file_name:
                if file_name.endswith('.xlsx'):
                    self.export_to_excel(file_name, df)
                elif file_name.endswith('.csv'):
                    self.export_to_csv(file_name, df)
                elif file_name.endswith('.pdf'):
                    self.export_to_pdf(file_name, df)
        else:
            QMessageBox.warning(self,"Nicht gefunden", f"Tabelle ist leer für {self.project_name}")

    def export_to_excel(self, file_name, df):
        df.to_excel(file_name, index=False)
        QMessageBox.information(self, "Exportieren", "Ergebnisse exportiert als: {file_name}")

    def export_to_csv(self, file_name, df):
        df.to_csv(file_name, index=False)
        QMessageBox.information(self, "Exportieren", "Ergebnisse exportiert als: {file_name}")

    def export_to_pdf(self, file_name, df):
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(file_name, pagesize=letter)
        elements = []

        # Convert dataframe to list of lists
        data = [df.columns.tolist()] + df.values.tolist()
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)

        doc.build(elements)
        QMessageBox.information(self, "Exportieren", "Ergebnisse exportiert als: {file_name}")

    
    def search_table(self):
        search_text = self.search_input.text().strip().lower()
        if not search_text:
            # self.clear_table()
            self.show_database()

            return

        if not self.flag:
            if self.table is None:
                self.table = SearchableTableWidget()
                self.table.itemDoubleClicked.connect(self.process_selected_material)
                self.layout.addWidget(self.table)
            self.flag = True

        if self.table.isHidden():
            self.table.show()

        results,col = core.search_result(search_text)
        if results:
            self.table.setRowCount(len(results))
            if col:
                self.table.setColumnCount(len(col))
                self.table.setHorizontalHeaderLabels(col)
                

            # Populate table with data
            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setBackground(QColor(15, 28, 41)) 
                    item.setForeground(QColor(255, 255, 255)) 
                    self.table.setItem(row_idx, col_idx, item)
            
            self.table.setStyleSheet("background-color: rgb(15, 28, 41); color: white;")
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        else:
            self.clear_table()
            self.search_input.clear()
            QMessageBox.warning(self, "Keine Ergebnisse", "Kein Ergebnis gefunden!")
            
            
    def show_database(self):
        self.clear_table()  # Clear existing content

        if not self.flag:
            if self.table is None:
                self.table = SearchableTableWidget()
                self.table.itemDoubleClicked.connect(self.process_selected_material)
                self.layout.addWidget(self.table)
            self.flag = True

        if self.table.isHidden():
            self.table.show()

        results,col = core.get_all_results()
        if results:
            self.table.setRowCount(len(results))
            if col:
                self.table.setColumnCount(len(col))
                self.table.setHorizontalHeaderLabels(col)

            self.table.setRowCount(len(results))

            # Populate table with data
            for row_idx, row_data in enumerate(results):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setBackground(QColor(15, 28, 41))
                    item.setForeground(QColor(255, 255, 255))
                    self.table.setItem(row_idx, col_idx, item)

            self.table.setStyleSheet("background-color: rgb(15, 28, 41); color: white;")
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        else:
            self.clear_table()
            QMessageBox.warning(self, "Keine Daten", "Keine Daten in der Datenbank gefunden!")


            
        
    def clear_table(self):
        if self.table is not None:
            self.table.hide()

    def process_selected_material(self, item):
        row = item.row()
        row_data = {}
        for col in range(self.table.columnCount()):
            column_name = self.table.horizontalHeaderItem(col).text()
            cell_value = self.table.item(row, col).text()
            row_data[column_name] = cell_value
        material_name = row_data.get(self.table.horizontalHeaderItem(0).text(), 'Unbekannt')
        quantity_input, ok = QInputDialog.getText(self, "Menge eingeben", f"Bitte Menge für {material_name} eingeben (Dezimalformat mit Komma, z.B. 12,34):")
        
        if ok:
            self.search_input.clear()
            quantity_input = quantity_input.replace(',', '.')
            
            try:
                quantity = float(quantity_input)
                print(quantity)
                self.clear_table() 
                self.add_material_to_project(material_name, quantity, row_data)

            except ValueError:
                QMessageBox.warning(self, "Ungültige Eingabe", "Bitte geben Sie eine gültige numerische Menge ein.")


    def add_material_to_project(self, material, quantity, row_data):

        unit = row_data.get('Bezugsgroesse', '')
        unit_symbol = row_data.get('Bezugseinheit', '')
            
            
        excluded_columns = ['Bezugsgroesse', 'Material', 'Bezugseinheit', 'Name (de)',""]

        # Dynamically create or update the table columns
        if self.results_table.rowCount() == 0:
            self.setup_results_table(row_data, excluded_columns)

        row_position = self.find_material_row(material)

        if row_position is None:
            row_position = self.results_table.rowCount()
            self.results_table.insertRow(row_position)
        else:
            print(f"Material '{material}' exists, updating row {row_position}.")
        self.results_table.setItem(row_position, 0, QTableWidgetItem(material))
        self.results_table.setItem(row_position, 1, QTableWidgetItem(f"{str(unit).replace('.', ',')}{unit_symbol}"))

        index = 2
        for col in [col for col in row_data.keys() if col not in excluded_columns]:
            calculated_value = self.calculate_row_result(row_data, quantity, col, unit)
            print("calculated value", calculated_value)
            if calculated_value != 0:
                if col not in self.materials:
                    self.materials[col] = []
                    self.materials_name[col] = []
                self.results_table.setItem(row_position, index, QTableWidgetItem(f"{calculated_value:.4f}".replace('.', ',')))

                self.materials[col].append(round(calculated_value, 2))
                # self.materials_name[col].append(material)
            index += 1
        item_count = self.chart_combo.count()
        print("item list",item_count)
        if item_count == 0:
            self.chart_combo.addItems(self.data_list)
        res = core.insert_result(self.project_name, material, str(unit), str(unit_symbol), self.materials)
        if res:
            print("Result table updated successfully")

        self.update_cumulative_results()
        
        
        
        

    def find_material_row(self, material):
        """Check if the material already exists in the results table."""
        for row in range(self.results_table.rowCount()):
            item = self.results_table.item(row, 0) 
            if item is not None and item.text() == material:
                return row
        return None

    def setup_results_table(self, row_data, excluded_columns):
        self.data_list = [col for col in row_data.keys() if col not in excluded_columns]
        self.results_table.setColumnCount(len(self.data_list) + 2)
        self.results_table.setHorizontalHeaderLabels(['Material', 'Einheit'] + self.data_list)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setStyleSheet("""
                                                                    QHeaderView::section {
                                                                        background-color: #0f1c29;
                                                                        color: white;
                                                                        font-weight: bold;
                                                                    }
                                                                """)
        self.results_table.verticalHeader().setStyleSheet("""
                                                                QHeaderView::section {
                                                                    background-color: #0f1c29;
                                                                    color: white;
                                                                    font-weight: bold;
                                                                }
                                                            """)

    def on_item_double_clicked(self, item):
        row = item.row()
        material = self.results_table.item(row, 0).text()
        
        self.dialog = QDialog(self)
        self.dialog.setWindowTitle("Aktion")
        
        layout = QVBoxLayout(self.dialog)
        
        edit_button = QPushButton("Bearbeiten", self.dialog)
        delete_button = QPushButton("Löschen", self.dialog)
        
        layout.addWidget(QLabel(f"Möchten Sie den Eintrag für bearbeiten oder löschen? '{material}'?", self.dialog))
        layout.addWidget(edit_button)
        layout.addWidget(delete_button)
        
        edit_button.clicked.connect(lambda: self.edit_entry(material, row))
        delete_button.clicked.connect(lambda: self.delete_entry(material, row))
        
        self.dialog.exec_()
        
        
    def edit_entry(self, material, row):
        self.dialog.close()
        row_data = core.get_row_data(material)
        if row_data:
            quantity_input, ok = QInputDialog.getText(self, "Menge eingeben", f"Bitte Menge für {material} eingeben (Dezimalformat mit Komma, z.B. 12,34):")
            
            if ok:
                self.search_input.clear()
                quantity_input = quantity_input.replace(',', '.')
                
                try:
                    quantity = float(quantity_input)
                    print("the quantity",quantity)
                    self.clear_table() 
                    print(row_data)
                    self.add_material_to_project(material, quantity, row_data)

                except ValueError:
                    QMessageBox.warning(self, "Ungültige Eingabe", "Bitte geben Sie eine gültige numerische Menge ein.")
        else:
            QMessageBox.warning(self, "Ungültige Eingabe", "Bitte geben Sie eine gültige numerische Menge ein.")
                
                

    def delete_entry(self, material, row):
        self.dialog.close()
        reply = QMessageBox.question(self, "Eintrag löschen", f"Sind Sie sicher, dass Sie den Eintrag für '{material}'?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.results_table.removeRow(row)
            core.delete_row(self.project_name,material)
            
            

    def separate_numbers_and_alphabets(self,text):
        numbers = ''.join(re.findall(r'\d+', text))
        alphabets = ''.join(re.findall(r'[a-zA-Z]+', text))
        return numbers, alphabets    
            

    def calculate_row_result(self, row, quantity, indicator, unit):
        value = row.get(indicator, None)
        try:
            value = float(str(value).replace(",","."))
            # value = float(value)
            print(value)
        except ValueError as e:
            print(e)
            print(f"Invalid value for {indicator}: {value}")
            return 0.0
        
        if value is not None and not pd.isna(value) and value != float(unit):
            try:
                return quantity * value
            except ValueError:
                print(f"Error calculating result for {indicator}: {value}")
        
        return 0.0
    
    

    def update_cumulative_results(self):
        cumulative_totals = {}

        try:
            self.data = core.get_result_table(str(self.project_name).lower())
        except Exception as e:
            print(f"Error fetching result data: {e}")
            return

        if self.data:
            self.value_list.clear()
            self.materials_name.clear()
            for result in self.data:
                material_data = result['data']
                material_name = result['material']
                for key, value in material_data.items():
                    if key not in cumulative_totals:
                        cumulative_totals[key] = 0.0
                    cumulative_totals[key] += value

                    if key not in self.value_list:
                        self.value_list[key] = [] 
                    if key not in self.materials_name:
                        self.materials_name[key] = [] 
                    self.value_list[key].append(value) 
                    self.materials_name[key].append(material_name)
            results_text = ""
            for key, value in cumulative_totals.items():
                results_text += f"Gesamt {key} für alle Materialien: {value:.4f}\n".replace('.', ',')
            
            self.results_label.setText(results_text)
            


    def show_chart(self):
        if not self.value_list:
            QMessageBox.warning(self, "Keine Ergebnisse", "Bitte fügen Sie Materialien hinzu, bevor Sie das Diagramm anzeigen.")
            return

        indicator = self.chart_combo.currentText() 
        chart_type = self.chart_type_combo.currentText()

        values = self.value_list.get(indicator,'')  
        labels = self.materials_name.get(indicator,'')  
        print(values)
        print(labels)

        if not values or not labels:
            QMessageBox.warning(self, "Indikatorfehler", "Der ausgewählte Indikator ist in den Daten nicht verfügbar.")
            return

        if len(labels) != len(values):
            QMessageBox.warning(self, "Datenfehler", "Die Anzahl der Labels und Werte stimmt nicht überein!")
            return
        # Based on chart type, display the appropriate chart
        if chart_type == "Pie Chart":
            self.show_pie_chart(labels, values, indicator)
        elif chart_type == "Bar Chart":
            self.show_bar_chart(labels, values, indicator)
        elif chart_type == "Line Chart":
            self.show_line_chart(labels, values, indicator)
        elif chart_type == "Histogram":
            self.show_histogram(values, indicator)


            
            
            

    def show_pie_chart(self, labels, sizes, indicator):
        plt.figure(figsize=(7, 7))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')  
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


import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QPushButton, QLineEdit, QFrame, QTableWidgetItem, QTableWidget,
    QListWidget, QMessageBox, QFileDialog,QListWidgetItem,QSizePolicy,QHeaderView
)
import pyqtgraph as pg
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QPieSeries
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from app import EnvironmentalImpactCalculator
from PyQt5.QtCore import QThread, pyqtSignal
import core
data =None


# class WorkerThread(QThread):
#     finished = pyqtSignal()

#     def run(self):
#         import time
#         time.sleep(5)
#         self.finished.emit()

class ProjectItem:
    def __init__(self, name, number):
        self.name = name
        self.number = number
        self.materials = []
        
    def __str__(self):
        return f"{self.name} (#{self.number})"

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.projects = []
        self.current_materials = []
        # self.thread = WorkerThread()
        # self.thread.finished.connect(self.on_task_finished)
        self.project_creation_layout = QHBoxLayout()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.initUI()
    def resizeEvent(self, event):
        super().resizeEvent(event)

    def initUI(self):
        self.setWindowTitle("Dashboard")
        self.setGeometry(100, 100, 800, 600)
        # self.showMaximized()

        self.setStyleSheet("""
    background-color: #0f1c29;
    color: white;
    font-size: 27px;
    font-family: Arial;
    font-weight: bold;
""")
        self.setFont(QFont('Arial', 18))
        
        # Main container
        main_widget = QWidget(self)
        self.main_layout = QHBoxLayout(main_widget)

        # Sidebar
        self.sidebar_layout = QVBoxLayout()
        sidebar_frame = QFrame()
        sidebar_frame.setStyleSheet("background-color: #1f2e40;")
        sidebar_frame.setFont(QFont('Arial', 18))
        self.sidebar_layout = QVBoxLayout(sidebar_frame)

        # Sidebar buttons
        self.add_sidebar_button("Dashboard", self.sidebar_layout, self.show_dashboard_interface)
        self.add_sidebar_button("Neues Projekt", self.sidebar_layout, self.show_project_management_interface)
        self.add_sidebar_button("Mein Projekt", self.sidebar_layout,self.my_projects)

        self.main_layout.addWidget(sidebar_frame)
        
        # Content area
        self.content_layout = QVBoxLayout()
        content_widget = QWidget()
        content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(content_widget)

        self.setCentralWidget(main_widget)
        self.show_dashboard_interface()  # Default to show the dashboard
        
        
    def show_sign_in_interface(self):
        # Clear existing layout
        self.clear_content_layout()
        self.clear_project()

        sign_in_frame = QFrame()
        sign_in_frame.setStyleSheet("background-color: #1f2e40; border-radius: 10px;")
        sign_in_layout = QVBoxLayout(sign_in_frame)

        # Sign in label
        sign_in_label = QLabel("Sign In", self)
        sign_in_label.setFont(QFont('Arial', 24))
        sign_in_label.setStyleSheet("color: white;")
        sign_in_layout.addWidget(sign_in_label, alignment=Qt.AlignCenter)

        # Username input
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFont(QFont('Arial', 14))
        self.username_input.setStyleSheet("""
            background-color: #0f1c29; 
            color: white; 
            border: 2px solid #1f2e40; 
            border-radius: 10px; 
            padding: 10px;
        """)
        sign_in_layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setFont(QFont('Arial', 14))
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            background-color: #0f1c29; 
            color: white; 
            border: 2px solid #1f2e40; 
            border-radius: 10px; 
            padding: 10px;
        """)
        sign_in_layout.addWidget(self.password_input)

        # Sign in button
        sign_in_button = QPushButton("Sign In", self)
        sign_in_button.setFont(QFont('Arial', 14))
        sign_in_button.setStyleSheet("""
            background-color: #007bff; 
            color: white; 
            border-radius: 10px; 
            padding: 10px;
        """)
        sign_in_button.clicked.connect(self.handle_sign_in)
        sign_in_layout.addWidget(sign_in_button, alignment=Qt.AlignCenter)

        self.content_layout.addWidget(sign_in_frame, alignment=Qt.AlignCenter)
        
    def show_sign_up_interface(self):
        # Clear existing layout
        self.clear_content_layout()
        self.clear_project()

        sign_in_frame = QFrame()
        sign_in_frame.setStyleSheet("background-color: #1f2e40; border-radius: 10px;")
        sign_in_layout = QVBoxLayout(sign_in_frame)

        # Sign in label
        sign_in_label = QLabel("Sign Up", self)
        sign_in_label.setFont(QFont('Arial', 24))
        sign_in_label.setStyleSheet("color: white;")
        sign_in_layout.addWidget(sign_in_label, alignment=Qt.AlignCenter)

        # Username input
        username_input = QLineEdit(self)
        username_input.setPlaceholderText("Username")
        username_input.setFont(QFont('Arial', 14))
        username_input.setStyleSheet("""
            background-color: #0f1c29; 
            color: white; 
            border: 2px solid #1f2e40; 
            border-radius: 10px; 
            padding: 10px;
        """)
        sign_in_layout.addWidget(username_input)
        
        email_input = QLineEdit(self)
        email_input.setPlaceholderText("Email")
        email_input.setFont(QFont('Arial', 14))
        email_input.setStyleSheet("""
            background-color: #0f1c29; 
            color: white; 
            border: 2px solid #1f2e40; 
            border-radius: 10px; 
            padding: 10px;
        """)
        sign_in_layout.addWidget(email_input)

        # Password input
        password_input = QLineEdit(self)
        password_input.setPlaceholderText("Password")
        password_input.setFont(QFont('Arial', 14))
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setStyleSheet("""
            background-color: #0f1c29; 
            color: white; 
            border: 2px solid #1f2e40; 
            border-radius: 10px; 
            padding: 10px;
        """)
        sign_in_layout.addWidget(password_input)

        # Sign in button
        sign_in_button = QPushButton("Sign Up", self)
        sign_in_button.setFont(QFont('Arial', 14))
        sign_in_button.setStyleSheet("""
            background-color: #007bff; 
            color: white; 
            border-radius: 10px; 
            padding: 10px;
        """)
        sign_in_button.clicked.connect(self.handle_sign_up)
        sign_in_layout.addWidget(sign_in_button, alignment=Qt.AlignCenter)

        self.content_layout.addWidget(sign_in_frame, alignment=Qt.AlignCenter)

    def handle_sign_in(self):
        # Handle sign in logic here (e.g., authentication)
        print(self.username_input.text(),self.password_input.text())
        if self.username_input.text() == "pythondev" and self.password_input.text() == '1234':
            QMessageBox.information(self, "Login", f"user login successfully")
            self.show_project_management_interface()
        else:
            QMessageBox.warning(self, "Login", f"Invalid credientials")
        
        
    def handle_sign_up(self):
        # Handle sign in logic here (e.g., authentication)
        print("Sign in button clicked")

        
    def show_product_interface(self):
        # Clear existing layout
        self.clear_content_layout()

        if data is None:
            no_data_label = QLabel("Keine Daten geladen. Bitte importieren Sie eine Excel-Datei.")
            no_data_label.setFont(QFont('Arial', 18))
            no_data_label.setStyleSheet("color: white;")
            self.content_layout.addWidget(no_data_label)
            return

        # Create chart frame
        chart_frame = QFrame()
        chart_frame.setStyleSheet("background-color: #1f2e40; border-radius: 10px;")
        chart_layout = QVBoxLayout(chart_frame)

        # Add line chart
        self.update_chart()
        self.content_layout.addWidget(chart_frame)
        
        

    def clear_content_layout(self):
        if hasattr(self, 'content_layout'):
            while self.content_layout.count():
                child = self.content_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()


                
                

    def add_line_chart(self, layout):
        # Plotting the line chart with PyQtGraph
        if data is not None:
            line_chart = pg.PlotWidget()
            x = data.iloc[:, 0]  # First column
            y = data.iloc[:, 1]  # Second column
            line_chart.plot(x, y, pen=pg.mkPen('b', width=2))

            line_chart.setTitle("Line Chart")
            line_chart.setLabel('left', 'Y-Axis')
            line_chart.setLabel('bottom', 'X-Axis')
            layout.addWidget(line_chart)

    def add_bar_chart(self, layout):
        if data is not None:
            # Bar chart using Matplotlib
            fig, ax = plt.subplots()
            x = data.iloc[:, 0]  # First column
            y = data.iloc[:, 1]  # Second column
            ax.bar(x, y, color='skyblue')

            ax.set_title("Bar Chart")
            ax.set_xlabel("X-Axis")
            ax.set_ylabel("Y-Axis")

            # Convert Matplotlib plot to PyQt5 widget
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)

    def add_pie_chart(self, layout):
        if data is not None:
            # Pie chart using Matplotlib
            fig, ax = plt.subplots()
            y = data.iloc[:, 1]  # Second column
            labels = data.iloc[:, 0]  # First column
            ax.pie(y, labels=labels, autopct='%1.1f%%', startangle=90)

            ax.set_title("Pie Chart")
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)

    def add_histogram(self, layout):
        if data is not None:
            # Histogram using Matplotlib
            fig, ax = plt.subplots()
            y = data.iloc[:, 1]  # Second column
            ax.hist(y, bins=10, color='purple')

            ax.set_title("Histogram")
            ax.set_xlabel("Value")
            ax.set_ylabel("Frequency")

            # Convert Matplotlib plot to PyQt5 widget
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)


    def add_sidebar_button(self, text, layout, on_click=None):
        button = QPushButton(text)
        button.setFont(QFont('Arial', 12))
        button.setStyleSheet("color: white; background-color: #1f2e40; border: none;")
        if on_click:
            button.clicked.connect(on_click)
        layout.addWidget(button)
        
    def add_sales_chart(self, layout):
        # Example of a line chart (sales analytics)
        series = QLineSeries()
        series.append(0, 6)
        series.append(2, 4)
        series.append(3, 8)
        series.append(7, 4)
        series.append(10, 5)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Sales Analytics")
        chart_view = QChartView(chart)
        layout.addWidget(chart_view)
        
        
    def show_dashboard_interface(self):
        self.clear_project_creation_layout()
        self.clear_content_layout()

        # Welcome Label
        welcome_label = QLabel("WILLKOMMEN IM PROJEKT-DASHBOARD!", self)
        welcome_label.setFont(QFont('Arial', 18, QFont.Bold))
        welcome_label.setStyleSheet("color: #f0f0f0;")
        self.content_layout.addWidget(welcome_label, alignment=Qt.AlignLeft)

        # Table Frame
        table_frame = QFrame()
        table_frame.setStyleSheet(
            "background-color: #2c3e50; "  # Darker background color
            "border-radius: 12px; "
            "padding: 15px; "
            "border: 2px solid #34495e;"  # Slightly lighter border color
        )
        table_layout = QVBoxLayout(table_frame)

        # Table Label
        table_label = QLabel("Aktuelles Projekt", self)
        table_label.setFont(QFont('Arial', 14, QFont.Bold))
        table_label.setStyleSheet("color: #ecf0f1;")
        table_layout.addWidget(table_label, alignment=Qt.AlignLeft)

        # Create Table
        table = QTableWidget()
        table.setColumnCount(2)  # Adjust the column count
        table.setHorizontalHeaderLabels(["Index", "Description"])

        # Fetch Data
        try:
            all_project = core.get_all_project()
        except Exception as e:
            print(f"Error retrieving projects: {e}")
            all_project = []

        if all_project:
            table.setRowCount(len(all_project))  # Set the number of rows

            for idx, (index, values) in enumerate(all_project):
                if "#" in values:
                    name, number = values.split("#", 1)
                else:
                    name, number = values, ""  # Handle case where `#` is not present

                # Set table items
                table.setItem(idx, 0, QTableWidgetItem(str(idx + 1)))
                table.setItem(idx, 1, QTableWidgetItem(f"{name} (#{number})"))

        # Table Header Style
        table.horizontalHeader().setStyleSheet(
            "background-color: #34495e; "  # Darker header background
            "color: #ecf0f1; "  # Light header text color
            "font-weight: bold;"
        )
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Table Item Style
        table.setStyleSheet(
            "background-color: #2c3e50; "  # Table background color
            "color: #ecf0f1; "  # Table text color
            "border: 1px solid #34495e;"  # Border color
        )

        table.setAlternatingRowColors(True)
        table.setStyleSheet(
            "alternate-background-color: #1e272e;"  # Alternating row color
        )

        table_layout.addWidget(table)

        self.content_layout.addWidget(table_frame)

        # self.show_chart()
        
        
    def show_chart(self):

        # Create a small bar chart
        bar_chart_frame = QFrame()
        bar_chart_frame.setStyleSheet("background-color: #2c3e50; border-radius: 12px; padding: 10px; border: 2px solid #34495e;")
        bar_chart_layout = QVBoxLayout(bar_chart_frame)
        bar_chart_label = QLabel("Sales Overview", self)
        bar_chart_label.setFont(QFont('Arial', 12, QFont.Bold))
        bar_chart_label.setStyleSheet("color: #ecf0f1;")
        bar_chart_layout.addWidget(bar_chart_label, alignment=Qt.AlignLeft)

        # Plotting Bar Chart
        bar_fig, bar_ax = plt.subplots(figsize=(5, 2))  # Adjust size to fit the page
        bar_ax.bar(['Jan', 'Feb', 'Mar', 'Apr'], [10, 20, 15, 25], color='#3498db')
        bar_ax.set_title('Monthly Usage', fontsize=10)
        bar_ax.set_xlabel('Month')
        bar_ax.set_ylabel('Sales')
        bar_ax.set_facecolor('#2c3e50')
        bar_ax.xaxis.label.set_color('#ecf0f1')
        bar_ax.yaxis.label.set_color('#ecf0f1')

        bar_canvas = FigureCanvas(bar_fig)
        bar_chart_layout.addWidget(bar_canvas)
        bar_canvas.draw()
        
        self.content_layout.addWidget(bar_chart_frame)

        # Create a small pie chart
        pie_chart_frame = QFrame()
        pie_chart_frame.setStyleSheet("background-color: #2c3e50; border-radius: 12px; padding: 10px; border: 2px solid #34495e;")
        pie_chart_layout = QVBoxLayout(pie_chart_frame)
        pie_chart_label = QLabel("Project Breakdown", self)
        pie_chart_label.setFont(QFont('Arial', 12, QFont.Bold))
        pie_chart_label.setStyleSheet("color: #ecf0f1;")
        pie_chart_layout.addWidget(pie_chart_label, alignment=Qt.AlignLeft)

        # Plotting Pie Chart
        pie_fig, pie_ax = plt.subplots(figsize=(5, 2))  # Adjust size to fit the page
        pie_ax.pie([30, 20, 15, 35], labels=['Rent', 'Utilities', 'Groceries', 'Entertainment'], autopct='%1.1f%%', colors=['#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6'])
        pie_ax.set_title('Project Breakdown', fontsize=10, color='#ecf0f1')
        pie_ax.set_facecolor('#2c3e50')

        pie_canvas = FigureCanvas(pie_fig)
        pie_chart_layout.addWidget(pie_canvas)
        pie_canvas.draw()

        self.content_layout.addWidget(pie_chart_frame)

        
    def my_projects(self):
        self.clear_project_creation_layout()
        self.clear_content_layout()
        self.title_label = QLabel("Meine Projekte", self)

        self.title_label.setStyleSheet("font-size: 22px; border-radius: 12px; padding: 15px; font-weight: bold; border: 2px solid #34495e; color: white; padding: 10px;")
        self.content_layout.addWidget(self.title_label)

        try:
            all_project = core.get_all_project()
        except Exception as e:
            print(f"Error retrieving projects: {e}")
            all_project = None

        if all_project:
            self.project_list = QListWidget()
            self.project_list.setStyleSheet("""
                QListWidget {
                    font-size: 16px;
                    background-color: #1f2e40;
                    border: 2px solid #ddd;
                    border-radius: 12px;
                }
                QListWidget::item {
                    padding: 15px;
                }
                QListWidget::item:selected {
                    background-color: #007bff;
                    color: white;
                }
            """)
            self.project_list.itemDoubleClicked.connect(self.open_project)

            for index, values in all_project:
                if "#" in values:
                    name, number = values.split("#", 1)
                    # project = ProjectItem(name, number)
                    # self.projects.append(project)
                    # self.project_list.addItem(f"{index}. {name} (#{number})")
                    project = ProjectItem(name, number)
                    self.projects.append(project)
                    # self.project_list.addItem(f"{name} (#{number})")
                    list_item = QListWidgetItem(str(project))  # Display string format
                    list_item.setData(Qt.UserRole, project)  # Store the actual ProjectItem
                    self.project_list.addItem(list_item)
                else:
                    print(f"Invalid project format: {values}")
            self.content_layout.addWidget(self.project_list)
        else:
            self.my_project_lists = QListWidget()
            self.my_project_lists.setStyleSheet("""
                QListWidget {
                    font-size: 20px;
                    background-color:  #1f2e40;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
                QListWidget::item {
                    padding: 10px;
                }
                QListWidget::item:selected {
                    background-color: #007bff;
                    color: white;
                }
            """)
            self.my_project_lists.addItem("Keine Projekte verfügbar. Besuchen Sie die Seite 'Projekt erstellen', um ein neues Projekt zu erstellen.")
            self.content_layout.addWidget(self.my_project_lists)


        
        
    def show_project_management_interface(self):
        self.clear_content_layout()

        # Project creation section
        self.project_creation_layout = QHBoxLayout()
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Projektname")
        self.project_number_input = QLineEdit()
        self.project_number_input.setPlaceholderText("Projektnummer")
        create_project_button = QPushButton("Projekt erstellen")
        create_project_button.clicked.connect(self.create_project)

        self.project_creation_layout.addWidget(self.project_name_input)
        self.project_creation_layout.addWidget(self.project_number_input)
        self.project_creation_layout.addWidget(create_project_button)

        # Project list
        self.project_list = QListWidget()
        self.project_list.itemDoubleClicked.connect(self.open_project)

        # Results section
        self.results_label = QLabel("Ergebnisse werden hier angezeigt")
        self.chart_widget = QLabel("Diagramm wird hier angezeigt")
        self.chart_widget.setAlignment(Qt.AlignCenter)

        # Export button
        export_button = QPushButton("Ergebnisse exportieren")
        export_button.clicked.connect(self.export_results)

        # Add widgets to content layout
        self.content_layout.addLayout(self.project_creation_layout)
        self.content_layout.addWidget(self.project_list)
        self.content_layout.addWidget(self.results_label)
        self.content_layout.addWidget(self.chart_widget)
        self.content_layout.addWidget(export_button)

    def create_project(self):
        name = self.project_name_input.text()
        number = self.project_number_input.text()
        if name and number:
            try:
                res = core.create_project_table(f"{str(name+"#"+number).lower()}")
                if not res:
                    QMessageBox.warning(self, "Fehler", "Projektname existiert bereits! Besuchen Sie meine Projektseite, um darauf zuzugreifen.")
                    self.project_name_input.clear()
                    self.project_number_input.clear()
                    return
                    
            except Exception as err:
                QMessageBox.warning(self, "Fehler", "Projekt konnte nicht erstellt werden, bitte versuchen Sie es erneut.")
                return  
            project = ProjectItem(name, number)
            self.projects.append(project)
            # self.project_list.addItem(f"{name} (#{number})")
            list_item = QListWidgetItem(str(project))  # Display string format
            list_item.setData(Qt.UserRole, project)  # Store the actual ProjectItem
            self.project_list.addItem(list_item)
            self.project_name_input.clear()
            self.project_number_input.clear()
        else:
            QMessageBox.warning(self, "Fehler", "Bitte geben Sie einen Namen und eine Nummer für das Projekt ein.")

    def open_project(self, item):
        # project = self.projects[self.project_list.row(item)]
        project = item.data(Qt.UserRole)
        # project = str(f"{project.name}{project.number}").lower()
        print("project",type(project))
        self.env_impact_calculator = EnvironmentalImpactCalculator(project)  # Instantiate the class
        self.env_impact_calculator.show()
        
        

    def update_results(self, materials):
        self.current_materials = materials
        
        if hasattr(self, 'results_table'):
            self.results_table.clear()
            self.results_table.setRowCount(0)  # Reset the row count
        if not hasattr(self, 'results_table'):
            self.results_table = QTableWidget(self)
            self.results_table.setColumnCount(3)  # Number of columns (Material, Quantity, Unit)
            self.results_table.setHorizontalHeaderLabels(["Material", "Quantity", "Unit"])
            self.results_table.setStyleSheet("background-color: #1f2e40; color: white; border: 1px solid #1f2e40;")

            # Add the table to the layout (assuming you have a layout named `content_layout`)
            self.content_layout.addWidget(self.results_table)

        # Populate the table with data
        self.results_table.setRowCount(len(materials))
        for row, (material, unit, quantity) in enumerate(materials):
            if material is not None and unit is not None and quantity is not None:
                self.results_table.setItem(row, 0, QTableWidgetItem(str(material)))
                self.results_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
                self.results_table.setItem(row, 2, QTableWidgetItem(str(unit)))
        
        self.update_chart()

        
    def clear_project_creation_layout(self):
        if hasattr(self, 'project_creation_layout'):
            while self.project_creation_layout.count() > 0:
                item = self.project_creation_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()





    def export_results(self):
        # Set default file names for different file types
        default_csv = "default.csv"
        default_excel = "default.xlsx"
        default_pdf = "default.pdf"
        
        options = QFileDialog.Options()
        
        # Display the dialog with the appropriate default file name based on user selection
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Results", "", 
                                                "Excel Files (*.xlsx);;CSV Files (*.csv);;PDF Files (*.pdf)", 
                                                options=options,
                                                initialFilter="CSV Files (*.csv)" if default_csv.endswith('.csv') else "Excel Files (*.xlsx)")
        if file_name:
            df = core.fecth_data_table()  # Fetch data from the database
            if file_name.endswith('.xlsx'):
                self.export_to_excel(file_name, df)
            elif file_name.endswith('.csv'):
                self.export_to_csv(file_name, df)
            elif file_name.endswith('.pdf'):
                self.export_to_pdf(file_name, df)

    def export_to_excel(self, file_name, df):
        df.to_excel(file_name, index=False)
        QMessageBox.information(self, "Export", f"Results exported as: {file_name}")

    def export_to_csv(self, file_name, df):
        df.to_csv(file_name, index=False)
        QMessageBox.information(self, "Export", f"Results exported as: {file_name}")

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
        QMessageBox.information(self, "Export", f"Results exported as: {file_name}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec_())
import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QPushButton, QLineEdit, QFrame, QTableWidgetItem, QTableWidget,
    QListWidget, QMessageBox, QFileDialog, QDialog, QHeaderView, QAbstractItemView
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
data =None

class ProjectItem:
    def __init__(self, name, number):
        self.name = name
        self.number = number
        self.materials = []

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.projects = []
        self.current_materials = []
        self.project_creation_layout = QHBoxLayout()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Dashboard")
        # self.setGeometry(100, 100, 1200, 700)
        self.showMaximized()

        self.setStyleSheet("background-color: #0f1c29; color: white;")

        # Main container
        main_widget = QWidget(self)
        self.main_layout = QHBoxLayout(main_widget)

        # Sidebar
        self.sidebar_layout = QVBoxLayout()
        sidebar_frame = QFrame()
        sidebar_frame.setStyleSheet("background-color: #1f2e40;")
        self.sidebar_layout = QVBoxLayout(sidebar_frame)

        # Sidebar buttons
        self.add_sidebar_button("Dashboard", self.sidebar_layout, self.show_dashboard_interface)
        self.add_sidebar_button("New Project", self.sidebar_layout, self.show_project_management_interface)
        self.add_sidebar_button("Recent Work", self.sidebar_layout)
        self.add_sidebar_button("Settings", self.sidebar_layout)
        self.add_sidebar_button("Login", self.sidebar_layout, self.show_sign_in_interface)
        self.add_sidebar_button("Sign up", self.sidebar_layout, self.show_sign_up_interface)
        self.add_sidebar_button("Documentation", self.sidebar_layout)

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
            no_data_label = QLabel("No data loaded. Please import an Excel file.")
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
        # self.add_line_chart(chart_layout)

        # # Add bar chart
        # self.add_bar_chart(chart_layout)

        # # Add pie chart
        # self.add_pie_chart(chart_layout)

        # # Add histogram
        # self.add_histogram(chart_layout)

        # Add chart_frame to the main layout
        self.content_layout.addWidget(chart_frame)

    def clear_content_layout(self):
        while self.content_layout.count() > 0:
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

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
        # Clear existing layout
        self.clear_content_layout()
        self.clear_project()

        # Welcome Label
        welcome_label = QLabel("Hi, Taylor Kareem!", self)
        welcome_label.setFont(QFont('Arial', 18))
        welcome_label.setStyleSheet("color: white;")
        self.content_layout.addWidget(welcome_label, alignment=Qt.AlignLeft)

        table_frame = QFrame()
        table_frame.setStyleSheet("background-color: #1f2e40; border-radius: 10px;")
        table_layout = QVBoxLayout(table_frame)

        table_label = QLabel("Last Invoice", self)
        table_label.setFont(QFont('Arial', 14))
        table_layout.addWidget(table_label, alignment=Qt.AlignLeft)

        # Create table
        table = QTableWidget(4, 4)
        table.setHorizontalHeaderLabels(["#Invoice", "Description", "Status", "Amount"])
        table.setItem(0, 0, QTableWidgetItem("#42526"))
        table.setItem(0, 1, QTableWidgetItem("Home Chair"))
        table.setItem(0, 2, QTableWidgetItem("Paid"))
        table.setItem(0, 3, QTableWidgetItem("$389.05"))

        table.setItem(1, 0, QTableWidgetItem("#45456"))
        table.setItem(1, 1, QTableWidgetItem("Circle Chair"))
        table.setItem(1, 2, QTableWidgetItem("Pending"))
        table.setItem(1, 3, QTableWidgetItem("$124.42"))

        table.setItem(2, 0, QTableWidgetItem("#47480"))
        table.setItem(2, 1, QTableWidgetItem("Home Chair"))
        table.setItem(2, 2, QTableWidgetItem("Paid"))
        table.setItem(2, 3, QTableWidgetItem("$389.05"))

        table.setItem(3, 0, QTableWidgetItem("#31349"))
        table.setItem(3, 1, QTableWidgetItem("Wooden Chair"))
        table.setItem(3, 2, QTableWidgetItem("Unpaid"))
        table.setItem(3, 3, QTableWidgetItem("$543.53"))

        table.setStyleSheet("background-color: #1f2e40; color: white; border: 1px solid #1f2e40;")
        table_layout.addWidget(table)

        self.content_layout.addWidget(table_frame)
        
        
    def show_project_management_interface(self):
        self.clear_content_layout()

        # Project creation section
        self.project_creation_layout = QHBoxLayout()
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Project Name")
        self.project_number_input = QLineEdit()
        self.project_number_input.setPlaceholderText("Project Number")
        create_project_button = QPushButton("Create Project")
        create_project_button.clicked.connect(self.create_project)

        self.project_creation_layout.addWidget(self.project_name_input)
        self.project_creation_layout.addWidget(self.project_number_input)
        self.project_creation_layout.addWidget(create_project_button)

        # Project list
        self.project_list = QListWidget()
        self.project_list.itemDoubleClicked.connect(self.open_project)

        # Results section
        self.results_label = QLabel("Results will be displayed here")
        self.chart_widget = QLabel("Chart will be displayed here")
        self.chart_widget.setAlignment(Qt.AlignCenter)

        # Export button
        export_button = QPushButton("Export Results")
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
            project = ProjectItem(name, number)
            self.projects.append(project)
            self.project_list.addItem(f"{name} (#{number})")
            self.project_name_input.clear()
            self.project_number_input.clear()
        else:
            QMessageBox.warning(self, "Error", "Please enter a name and number for the project.")

    def open_project(self, item):
        project = self.projects[self.project_list.row(item)]
        self.env_impact_calculator = EnvironmentalImpactCalculator(project)  # Instantiate the class
        self.env_impact_calculator.show()

    # def update_results(self, materials):
    #     self.current_materials = materials
    #     result_text = "Calculated Materials:\n\n"
    #     for material, unit, quantity in materials:
    #         if material is  not None and unit is not None and quantity is not None:
    #           result_text += f"{material}: {quantity} {unit}\n"
    #     self.results_label.setText(result_text)
    #     self.update_chart()
    def update_results(self, materials):
        self.current_materials = materials
        
        # Clear the existing content in the table if it exists
        if hasattr(self, 'results_table'):
            self.results_table.clear()
            self.results_table.setRowCount(0)  # Reset the row count
        
        # Initialize QTableWidget if it does not exist
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

        
    def clear_project(self):
        # if self.project_creation_layout.count() > 0:
        #     while self.project_creation_layout.count():
        #         child = self.project_creation_layout.takeAt(0)
        #         if child.widget():
        #             child.widget().deleteLater()
        if hasattr(self, 'project_creation_layout') and self.project_creation_layout.count() > 0:
            for i in reversed(range(self.project_creation_layout.count())):
                widget = self.project_creation_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

    def update_chart(self):
        # Clear any existing charts from the layout
        if self.project_creation_layout.count() > 0:
            while self.project_creation_layout.count():
                child = self.project_creation_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # Prepare data for charts
        materials = [m[1] for m in self.current_materials]
        quantities = [m[2] for m in self.current_materials]

        # Check for valid quantities
        valid_quantities = [q for q in quantities if not pd.isna(q) and q > 0]
        valid_materials = [materials[i] for i in range(len(quantities)) if not pd.isna(quantities[i]) and quantities[i] > 0]

        # Bar Chart
        if valid_materials and valid_quantities:
            bar_fig, bar_ax = plt.subplots(figsize=(5, 4))
            bar_ax.bar(valid_materials, valid_quantities)
            bar_ax.set_title("Material Quantities")
            bar_ax.set_xlabel("Bezugsgroesse")
            bar_ax.set_ylabel("GWP")
            bar_ax.set_xticks(range(len(valid_materials)))
            bar_ax.set_xticklabels(valid_materials, rotation=45, ha='right')
            bar_canvas = FigureCanvas(bar_fig)
            bar_canvas.draw()
            plt.close(bar_fig)
            self.project_creation_layout.addWidget(bar_canvas)

        # Pie Chart
        if valid_materials and valid_quantities and sum(valid_quantities) > 0:
            pie_fig, pie_ax = plt.subplots(figsize=(5, 4))
            pie_ax.pie(valid_quantities, labels=valid_materials, autopct='%1.1f%%', startangle=90)
            pie_ax.set_title("Material Distribution")
            pie_canvas = FigureCanvas(pie_fig)
            pie_canvas.draw()
            plt.close(pie_fig)
            self.project_creation_layout.addWidget(pie_canvas)

        # Line Chart
        if valid_materials and valid_quantities:
            line_fig, line_ax = plt.subplots(figsize=(5, 4))
            line_ax.plot(valid_materials, valid_quantities, marker='o', linestyle='-', color='b')
            line_ax.set_title("Material Trend Over Time")
            line_ax.set_xlabel("Bezugsgroesse")
            line_ax.set_ylabel("GWP")
            line_ax.set_xticks(range(len(valid_materials)))
            line_ax.set_xticklabels(valid_materials, rotation=45, ha='right')
            line_canvas = FigureCanvas(line_fig)
            line_canvas.draw()
            plt.close(line_fig)
            self.project_creation_layout.addWidget(line_canvas)


    def export_results(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Results", "", 
                                                   "Excel Files (*.xlsx);;PDF Files (*.pdf)", 
                                                   options=options)
        if file_name:
            if file_name.endswith('.xlsx'):
                self.export_to_excel(file_name)
            elif file_name.endswith('.pdf'):
                self.export_to_pdf(file_name)

    def export_to_excel(self, file_name):
        df = pd.DataFrame(self.current_materials, columns=['Material', 'Unit', 'Quantity'])
        df.to_excel(file_name, index=False)
        QMessageBox.information(self, "Export", f"Results exported as: {file_name}")

    def export_to_pdf(self, file_name):
        doc = SimpleDocTemplate(file_name, pagesize=letter)
        elements = []

        data = [['Material', 'Unit', 'Quantity']] + self.current_materials
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
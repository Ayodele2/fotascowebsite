import sqlite3
import ast 
import pandas as pd
import os 
import sys

if getattr(sys, 'frozen', False):
    # If the app is running from a bundled executable
    db_path = os.path.join(sys._MEIPASS, 'database.db')
else:
    db_path = 'database.db'

def create_tables(df, table_name: str):
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
            table_exists = cur.fetchone()
            
            if table_exists:
                print(f"Table '{table_name}' exists. Dropping the table...")
                cur.execute(f"DROP TABLE {table_name};")
            
            columns = df.columns.tolist()
            escaped_columns = [f'"{col}" TEXT' for col in columns]
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(escaped_columns)});"
            cur.execute(create_table_query)
            
            for _, row in df.iterrows():
                row_data = tuple(row)
                insert_query = f"INSERT INTO {table_name} ({', '.join([f'\"{col}\"' for col in columns])}) VALUES ({', '.join(['?' for _ in columns])});"
                cur.execute(insert_query, row_data)
            
            conn.commit()
            print(f"Data successfully imported into table '{table_name}' in the 'desktop_app' database.")
            return len(df)
    except Exception as err:
        print(f"An error occurred: {err}")
        return None
    
    
    
def drop_table(table_name:str):
     try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        cur.close()
        
     except Exception as err:
        print(f"An error occurred: {err}")
        return False
     finally:
        conn.close()
    
    
def materials_table_exist():
     try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM materials LIMIT 2")
        result = cur.fetchall()
        if result:
            return True
        
        return False
        
     except Exception as err:
        print(f"An error occurred: {err}")
        return False
    
    
def query_database(search_text: str,table_name:str):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Construct query to search across all columns in the table
        columns = get_table_columns(cur, table_name)
        escaped_columns = [f'"{col}"' for col in columns]

        # Construct query to search across all columns
        search_query = f"SELECT * FROM {table_name} WHERE " + " OR ".join([f"{col} LIKE ?" for col in escaped_columns])
        search_values = [f"%{search_text}%" for _ in columns]
        # search_query = f"SELECT * FROM {table_name} WHERE " + " OR ".join([f"{col} LIKE ?" for col in columns])
        # search_values = [f"%{search_text}%" for _ in columns]

        cur.execute(search_query, search_values)
        results = cur.fetchall()
        conn.close()
        return results,columns
    except Exception as err:
        print(f"An error occurred: {err}")
        return None,None

def get_table_columns(cur, table_name: str):
    try:
        cur.execute(f"PRAGMA table_info({table_name});")
        columns = [row[1] for row in cur.fetchall()]
        return columns
    except Exception as err:
        print(f"An error occurred: {err}")
        return []
    
    
def get_columns(table_name: str):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({table_name});")
        columns = [row[1] for row in cur.fetchall()]
        return columns[2:]
    except Exception as err:
        print(f"An error occurred: {err}")
        return []
    
    
def result_tables():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(f'''
        CREATE TABLE IF NOT EXISTS result_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            material TEXT,
            unit TEXT,
            column_names TEXT,  -- Store column names as a comma-separated string
            calculated_values TEXT,  -- Store values as a comma-separated string
            UNIQUE(project_name, material)  -- Ensure unique combination of project_name and material
        )
    ''')

    conn.commit()
    conn.close()
    print("table created successfully")
    return True


def create_project_name(p_name: str):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS project_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL UNIQUE
            )
        ''')
        
        cur.execute("INSERT INTO project_table (project_name) VALUES(?)", (p_name,))
        
        conn.commit()
        print("Project added successfully.")
        return cur.rowcount 
        
    except sqlite3.IntegrityError:
        print(f"Error: Project name '{p_name}' already exists.")
        return False

    except sqlite3.Error as err:
        print(f"Database Error: {err}")
        return False
    
        
    finally:
        conn.close()
        
        
def get_projects():
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT project_name, material, unit,column_names, calculated_values FROM result_table")
        result = cur.fetchall()
        
        return result if result else None
    
    except sqlite3.Error as err:
        print(f"Database Error: {err}")
        return None
    
    finally:
        cur.close()  
        conn.close() 
        
        
        
def fetch_results_from_db():
    try:
        conn = sqlite3.connect(db_path)
        query = "SELECT material, unit, column_names, calculated_values FROM result_table" 
        df = pd.read_sql_query(query, conn) 
        conn.close() 

        if df.empty: 
            print("No results found.")
            return None

        results = []
        cumulative_sums = {}

        for index, row in df.iterrows():
            material, unit, column_names, calculated_values = row
            
            column_names_list = column_names.split(',')
            values_list = [v.strip('[]') for v in calculated_values.split('],[')]
            
            try:
                calculated_values_lists = [list(map(float, filter(None, v.split(',')))) for v in values_list]
            except (ValueError, SyntaxError) as e:
                print(f"Error parsing calculated_values: {e}")
                continue

            result_entry = {
                'material': material,
                'unit': unit,
                **{key: value[-1] for key, value in zip(column_names_list, calculated_values_lists)}
            }
            results.append(result_entry)

        results_df = pd.DataFrame(results)

        # # Save the DataFrame to an Excel file
        # output_file = 'calculated_results.xlsx'
        # results_df.to_excel(output_file, index=False)

        # print(f"Results successfully saved to {output_file}")
        return results_df

    except Exception as e:
        print(f"Error fetching results: {e}")
        return None
    
    



def get_result_from_db(pro_name:str):
    try:
        conn = sqlite3.connect(db_path)
        query = "SELECT material, unit, column_names, calculated_values FROM result_table WHERE project_name=?"  
        df = pd.read_sql_query(query, conn,params=(pro_name,)) 
        conn.close() 

        if df.empty: 
            print("No results found.")
            return None

        results = []
        cumulative_sums = {}

        for index, row in df.iterrows():
            material, unit, column_names, calculated_values = row
            
            column_names_list = column_names.split(',')
            values_list = [v.strip('[]') for v in calculated_values.split('],[')]
            
            try:
                calculated_values_lists = [list(map(float, filter(None, v.split(',')))) for v in values_list]
            except (ValueError, SyntaxError) as e:
                print(f"Error parsing calculated_values: {e}")
                continue

            result_entry = {
                'material': material,
                'unit': unit,
                **{key: value[-1] for key, value in zip(column_names_list, calculated_values_lists)}
            }
            results.append(result_entry)

        results_df = pd.DataFrame(results)

        return results_df

    except Exception as e:
        print(f"Error fetching results: {e}")
        return None
    
        
        
def get_projects():
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM project_table")
        result = cur.fetchall()
        
        return result if result else None
    
    except sqlite3.Error as err:
        print(f"Database Error: {err}")
        return None
    
    finally:
        cur.close()  
        conn.close() 
        
#get_all_materials_result

def get_all_materials_result():
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        columns = get_table_columns(cur, "materials")
        cur.execute("SELECT * FROM materials")
        
        result = cur.fetchall()
        if result and columns:
            return result,columns
        
        return None,None
    
    except sqlite3.Error as err:
        print(f"Database Error: {err}")
        return None,None
    
    finally:
        cur.close()  
        conn.close() 




def insert_or_update_result(project_name: str, material: str, unit: str, unit_symbol: str, row_data: dict):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        excluded_columns = ['Bezugsgroesse', 'Material', 'Bezugseinheit']
        columns = [col for col in row_data.keys() if col not in excluded_columns]
        values = [row_data.get(col, 0) for col in columns]
        
        column_names = ','.join(columns)
        calculated_values = ','.join(map(str, values))
        
        cur.execute('''
            INSERT INTO result_table (project_name, material, unit, column_names, calculated_values)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(project_name, material) DO UPDATE SET
                unit = excluded.unit,
                column_names = excluded.column_names,
                calculated_values = excluded.calculated_values
        ''', (project_name, material, f"{unit}{unit_symbol}", column_names, calculated_values))
        
        conn.commit()
        conn.close()
        print("Data inserted or updated successfully")
        return True
    except Exception as err:
        print(f"An error occurred: {err}")
        return False





def retrieve_project_results(project_name: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute('''
        SELECT material, unit, column_names, calculated_values 
        FROM result_table 
        WHERE project_name = ?
    ''', (project_name,))

    # Fetch all results
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print(f"No results found for project: {project_name}")
        return None

    results = []
    cumulative_sums = {}

    for row in rows:
        material, unit, column_names, calculated_values = row
        
        column_names_list = column_names.split(',')
        values_list = [v.strip('[]') for v in calculated_values.split('],[')]
        try:
            calculated_values_lists = [list(map(float, filter(None, v.split(',')))) for v in values_list]
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing calculated_values: {e}")
            continue
        
        # calculated_values_lists = [list(map(float, v.split(','))) for v in values_list]

        result_entry = {
            'material': material,
            'unit': unit,
            'data': {key:value[-1] for key,value in zip(column_names_list, calculated_values_lists)}
        }
        results.append(result_entry)


    return results

def delete_row_table(pro_name: str, materials: str):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        query = "DELETE FROM result_table WHERE project_name = ? AND material = ?"
        cur.execute(query, (pro_name, materials))
        conn.commit()
        
    except Exception as err:
        print(f"An error occurred: {err}")
        
    finally:
        if conn:
            conn.close()
            
            
            
            
def get_materials_row_data(search_text:str, table_name:str="materials"):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        columns = get_table_columns(cur, table_name)
        escaped_columns = [f'"{col}"' for col in columns]

        search_query = f"SELECT * FROM {table_name} WHERE " + " OR ".join([f"{col} LIKE ?" for col in escaped_columns])
        search_values = [f"%{search_text}%" for _ in columns]
        # search_query = f"SELECT * FROM {table_name} WHERE " + " OR ".join([f"{col} LIKE ?" for col in columns])
        # search_values = [f"%{search_text}%" for _ in columns]

        cur.execute(search_query, search_values)
        result = cur.fetchone()
        if result:
            row_data = dict(zip(columns, result))
            return row_data
        
        return None
    
    except Exception as err:
        print(f"An error occurred: {err}")
        return None
        
    finally:
        if conn:
            conn.close()
        
        

    
    

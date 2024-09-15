import db



def create_table(df, table:str):
    res = db.create_tables(df, table)
    return res

def search_result(search_text,table_name="materials"):
    res,col = db.query_database(search_text,table_name)
    return res,col


def insert_result(project_name:str,
                  material,unit, symbol,row_data):
    db.result_tables()
    res = db.insert_or_update_result(project_name,material,unit,symbol,row_data)
    if res:
         return res
 
    return None

def get_result_table(project_name:str):
    res = db.retrieve_project_results(project_name)
    if res:
        return res
    return None

def drop_user_table(table_name:str="result_table"):
    db.drop_table(table_name)



def get_table_column(table_name:str ="materials"):
    res = db.get_columns(table_name)
    if res:
        return res
    
    return None


def fecth_data_table():
    res = db.fetch_results_from_db()
    return res


def create_project_table(p_name:str):
    res = db.create_project_name(p_name)
    return res


def fetch_result_data(pro_name:str):
    res = db.get_result_from_db(pro_name)
    return res



def table_exist():
    res = db.materials_table_exist()
    return res


def get_all_project():
    res = db.get_projects()
    return res


def get_all_results():
    res,col = db.get_all_materials_result()
    return res,col


def delete_row(pro_name:str, material:str):
    db.delete_row_table(pro_name,material)
    
    
def get_row_data(material:str):
    res = db.get_materials_row_data(material)
    return res
def init_database(sql_settings : dict, sql_type : str) -> tuple[str, bool]:
    """
    根据提供的 SQL 设置和类型初始化数据库连接字符串。
    此函数使用提供的设置为 SQL Server 构建数据库连接字符串。
    它会检查所需连接参数的存在和完整性。
    如果参数有效，则返回构建好的连接字符串和 True。
    否则返回错误信息和 False。

    Args:
        sql_settings (dict): 包含数据库连接参数的字典。
        sql_type (str): 要使用的 SQL 数据库类型（例如："sqlserver"）。

    Returns:
        (str, bool): 包含连接字符串或错误信息的元组，以及一个表示是否成功的布尔值。

    """
    # TODO:未来可以支持更多的sql数据保存方式
    if sql_type == "sqlserver":
        if not sql_settings:
            result_msg = "检测到data_save_type为sqlserver,但未在config中配置数据库连接参数"
            return result_msg, False
        required_keys = {"server", "port", "database", "UID", "PWD"}
        if not all(key in sql_settings for key in required_keys):
            result_msg = "数据库连接参数不完整，缺少必要字段"
            return result_msg, False
        result_msg = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={sql_settings['server']},{str(sql_settings['port'])};DATABASE={sql_settings['database']};UID={sql_settings['UID']};PWD={sql_settings['PWD']}"
        return result_msg, True
    
def init_filetext(file_settings : dict) -> tuple[str, bool]:
    pass
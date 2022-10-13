def columns_dict_to_string(columns_dict):
  columns_str = ""
  for item in columns_dict:
    buffer_str = f"\"{item['name']}\" {item['sql_type']['name']}"
    if "limit" in item["sql_type"]:
      buffer_str= f"{buffer_str}({item['sql_type']['limit']})"

    if "constrain" in item:
      buffer_str= f"{buffer_str} {item['constrain']}"
    
    columns_str= f"{columns_str} {buffer_str},"
  columns_str = columns_str[:-1]
  return columns_str

def columns_dict_w_include_list(columns_dict, include_fields):
  for item in columns_dict:
    for k in list(item.keys()):
        if any([k not in include_fields]):
          del item[k]
  return columns_dict


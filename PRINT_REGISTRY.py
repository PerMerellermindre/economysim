def print_registry(REG):
    print("REGISTRY:")
    print_dict(REG)
    
def print_dict(dic: dict,
               tail: str = ""):
    try:
        for key, value in dic.items():
            if not isinstance(value, dict) and not (isinstance(value, list) and isinstance(value[0], dict)):
                head = "\033[93m \033[4m" + str(value) + "\033[0m"
            else:
                head = ""
            if key == list(dic.keys())[-1]:
                print(tail + "└ " + str(key) + ":" + head)
                print_dict(dic[key], tail + "  ")
            else:
                print(tail + "├ " + str(key) + ":" + head)
                print_dict(dic[key], tail + "│ ")
    except:
        if isinstance(dic, list) and isinstance(dic[0], dict):
            for idx, item in enumerate(dic):
                if item == dic[-1]:
                    print(tail + f"└ Product {idx + 1}:")
                    print_dict(item, tail + "  ")
                else:
                    print(tail + f"├ Product {idx + 1}:")
                    print_dict(item, tail + "│ ")
        else: pass


    
def print_dict_compact(dic: dict,
                       tail: str = ""):
    try:
        for key, value in dic.items():
            head = ""
            if not any([isinstance(item, dict) for item in value.values()]):
                for subkey, subvalue in value.items():
                    head += str(subkey) + ": \033[93m \033[4m" + str(subvalue) + "\033[0m, "
            # else:
            #     head = ""
            if key == list(dic.keys())[-1]:
                print(tail + "└ " + str(key) + ": " + head)
                print_dict(dic[key], tail + "  ")
            else:
                print(tail + "├ " + str(key) + ": " + head)
                print_dict(dic[key], tail + "│ ")
    except:
        if isinstance(dic, list) and isinstance(dic[0], dict):
            for idx, item in enumerate(dic):
                if item == dic[-1]:
                    print(tail + f"└ Product {idx + 1}: ")
                    print_dict(item, tail + "  ")
                else:
                    print(tail + f"├ Product {idx + 1}: ")
                    print_dict(item, tail + "│ ")
        else: pass
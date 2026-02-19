def print_registry(REG):
    print("REGISTRY:")
    print_dict(REG)
    
def print_dict(dic: dict,
               tail: str = "",
               seen: set[int, ...] = set(),
               firstRun: bool = True) -> None:
    
    if firstRun:
        if len(seen) != 0:
            seen = set()
        seen.add(id(dic)) # Overview of printed entries to prevent infinite recursion in case of self-references
    
    prettystr = lambda x: ("\033[93m\033[4m" + str(x) + "\033[0m")
    
    try:
        for key in dic.keys():
            item = dic[key] # Pointer to dic item value (distinct from value, which is a copy of the item value)
            is_dict = isinstance(item, dict)
            if not is_dict:
                head = prettystr(item)
            else:
                if id(item) in seen:
                    try:
                        head = prettystr(f"{item['label']}") # Covers self-references to owners, producers and workers
                    except:
                        head = prettystr("{...}") # Catch-all
                else:
                    head = ""
            if key == list(dic.keys())[-1]:
                print(tail + "└ " + str(key) + ": " + head)
                if id(item) not in seen and is_dict:
                    seen.add(id(item))
                    print_dict(item, tail + "  ", seen, False)
            else:
                print(tail + "├ " + str(key) + ": " + head)
                if id(item) not in seen and is_dict:
                    seen.add(id(item))
                    print_dict(item, tail + "│ ", seen, False)
    except:
        print("Error: Not a dictionary.")
        return
    
if __name__ == "__main__":
    A = {'O1': {'label': 'O1', 'money': 50, 'balance': 0.0, 'inventory': {}, 'A': {'label': 'A', 'owner': {...}, 'balance': 0, 'profitRate': 0.15, 'recipe': {'inputs': {'materials': {'B': 1}, 'workers': 1}, 'output': 3}, 'inventory': {'inputs': {'materials': {'B': 1}, 'workers': 1}, 'output': 0}, 'productionCost': 0, 'workers': {'label': 'WA', 'product': {...}, 'money': 0.0, 'number': 0, 'wage': 4.0, 'inventory': {}}}}}
    A['O1']['A']['owner'] = A['O1']
    A['O1']['A']['workers']['product'] = A['O1']['A']['recipe']
    print_registry(A)
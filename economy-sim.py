from PRINT_REGISTRY import print_registry as pr
from MONEY import MONEY, ACCOUNT, COMMODITY
from MONEY import value_to_money as vtm

'''
Note: For the moment, we consider currency and value to be equal, effectively locking currency to labor hours.

Fix:

'''

workday: float = vtm(8.) #8 h workday expressed in money

class ECONOMY: #economy
    def __init__(self,
                 money_value: float):
        self.REG = {} #registry
        
def add_owner(E: ECONOMY,
              owner: str,
              money: float) -> dict:
    E.REG[owner] = {"label": owner,
                    "money": ACCOUNT(money)}
    E.REG[owner]["balance"] = ACCOUNT(0., E.REG[owner]["money"])
    return E.REG[owner]

def add_product(E: ECONOMY,
                owner: dict,
                product: str,
                recipe: dict[float, ...],
                inventory: dict[list[float, float], ...],
                productionCost: float,
                balance: float,
                profitRate: float) -> dict:
    owner_label = owner["label"]
    
    if recipe.keys() != inventory.keys():
            raise Exception("Inventory and recipe keys must be the same.")

    if product not in E.REG[owner_label]:
        free_workers = recipe["inputs"]["workers"] - inventory["inputs"]["workers"]
        wage = vtm(4.) #NB: currently assuming a wage of 4 h upon instantiation. Should be made arbitrary
        money_workers = MONEY(0.) #inventory["inputs"]["workers"][0] * wage
        E.REG[owner_label][product] = {"label": product,
                                 "recipe": recipe,
                                 "inventory": inventory,
                                 "productionCost": MONEY(productionCost),
                                 "balance": ACCOUNT(balance, owner["balance"]),
                                 "profitRate": profitRate,
                                 "owner": owner_label,
                                 "workers": {"money": money_workers,
                                             "number": free_workers,
                                             # "labor": workday.amount * free_workers,
                                             "wage": wage,
                                             "inventory": {}}}
        
    # if f"all_{product}" in E.REG:
    #     E.REG[f"all_{product}"].append(E.REG[owner_label][product])
    # else:
    #     E.REG[f"all_{product}"] = [E.REG[owner_label][product]]
    
    return E.REG[owner_label][product]

def set_unit_price(product: dict) -> None:
    #NB: implement logic to determine profit rate. E.g., tendency to increase profit rate until sale revenue begins to decline.
    product["inventory"]["output"].unit_value = product["productionCost"] * (1. + product["profitRate"]) / product["inventory"]["output"].amount
    product["recipe"]["output"].unit_value = product["productionCost"] * (1. + product["profitRate"]) / product["inventory"]["output"].amount

def produce(E: ECONOMY,
            product: dict) -> None:
    
    inputs = product["recipe"]["inputs"]
    inventory = product["inventory"]["inputs"]
    output = product["recipe"]["output"]
    stocks = inventory["materials"]
    materials = inputs["materials"]
    labor = inputs["workers"]
    paid_wage = labor.value
    
    if any([i < j for i,j in zip(stocks.values(), materials.values())]): #wait if not enough material for cycle
        print(f"Not enough material for owner {product['owner']} to produce {product['label']}.")
        return
    
    if inventory["workers"] < labor: #wait if not enough labor for cycle
        print(f"Not enough labor for owner {product['owner']} to produce {product['label']}.")
        return
    
    material_cost = sum([units.amount * units.unit_value for units in stocks.values()], MONEY(0.))
    
    production_cost = paid_wage + material_cost #NB: Value, not money
    
    for material in materials.values():
        stocks[material.category] -= material
    inventory["workers"] -= labor

    product["productionCost"] += production_cost
    product["inventory"]["output"] += output
    set_unit_price(product)
    
def pay_wages(E: ECONOMY,
              product: dict) -> None:
    producer = E.REG[product["owner"]]
    labor = product["recipe"]["inputs"]["workers"]
    workers = product["workers"]
    payout = workers["wage"] * labor.amount #NB: assuming all labor paid at once, maybe change to piecemeal payments?
    
    if producer["money"] < payout: #wait if not enough money to pay workers for one cycle
        print(f"Not enough money for producer {product['owner']} of product {product['label']} to pay workers.")
        return
    
    workers["money"] += payout
    product["balance"] -= payout

def sell(E: ECONOMY,
         product: dict,
         buyer: dict,
         units_amount: float) -> None:
    stock = product["inventory"]["output"]
    units = COMMODITY(stock.category, units_amount, stock.unit_value)
    inventory = buyer["inventory"]
    prod = product["label"]
    seller = E.REG[product["owner"]]
    price = units.value
    
    product["productionCost"] *= (stock.amount - units.amount) / stock.amount #production cost of remaining stock
    product["inventory"]["output"] -= units
    product["balance"] += price
    
    if "money" in buyer.keys(): #if worker or owner (for personal consumption, MOS)
        try:
            inventory[prod] += units
        except:
            inventory[prod] = units
        
        try: #if owner
            buyer["balance"] -= price
        except: #if worker
            buyer["money"] -= price

    else: #if producer (for productive consumption, MOP)
        try:
            inventory["inputs"]["materials"][prod] += units
        except:
            inventory["inputs"]["materials"][prod] = units #include value on rhs
        buyer["balance"] -= price

    if product["balance"] < MONEY(0.):
        print(f"Note: Producer {seller['label']} of {product['label']} sees negative balance after sale.")

def reproduce_labor(product: dict) -> None:
    workers = product["workers"]
    for key, value in workers["inventory"].items(): #NB: currently assuming 1 item in the inventory is sufficient to reproduce 1 worker. Generalize later
        units = int(value.amount) #floor to whole number when positive
        if units >= 1:
            workers["inventory"][key] -= units
            workers["number"] += units
            break
        else:
            print(f"No MOS for reproduction for workers of product {product['label']} ({product['owner']}).")
        

if __name__ == "__main__":
    E = ECONOMY(1)
    pr(E.REG)
    print("\nAdd owners")
    O1 = add_owner(E, "O1", 50)
    O2 = add_owner(E, "O2", 50)
    O3 = add_owner(E, "O3", 50)
    pr(E.REG)
    print("\nAdd products")
    A = add_product(E, O1, "A", {"inputs":
                                 {"materials":
                                  {"B": COMMODITY("B", 1, 16)},
                                  "workers": COMMODITY("workers", 1, 4)},
                                 "output": COMMODITY("A", 3, 0.)},
                                {"inputs":
                                 {"materials":
                                 {"B": COMMODITY("B", 1, 16)},
                                  "workers": COMMODITY("workers", 1, 4)},
                                 "output": COMMODITY("A", 0, 0.)}, 0, 0, 0.15)
    B = add_product(E, O2, "B", {"inputs":
                                 {"materials":
                                  {"A": COMMODITY("A", 1, 8.)},
                                  "workers": COMMODITY("workers", 1, 4)},
                                 "output": COMMODITY("B", 1, 0.)},
                                {"inputs":
                                 {"materials":
                                 {"A": COMMODITY("A", 0, 8.)},
                                  "workers": COMMODITY("workers", 1, 4)},
                                 "output": COMMODITY("B", 0, 0.)}, 0, 0, 0.15)
    V = add_product(E, O3, "V", {"inputs":
                                 {"materials":
                                  {"A": COMMODITY("A", 2, 8.)},
                                  "workers": COMMODITY("workers", 2, 4)},
                                 "output": COMMODITY("V", 8, 0.)},
                                {"inputs":
                                 {"materials":
                                 {"A": COMMODITY("A", 0, 8.)},
                                  "workers": COMMODITY("workers", 2, 4)},
                                 "output": COMMODITY("V", 0, 0.)}, 0, 0, 0.15)
    pr(E.REG)
    print("\nProduce A")
    produce(E, A)
    # pr(E.REG)
    print("\nPay workers A")
    pay_wages(E, A)
    # pr(E.REG)
    print("\nSell A to O2")
    sell(E, A, B, 1)
    # pr(E.REG)
    print("\nProduce B")
    produce(E, B)
    # pr(E.REG)
    print("\nPay workers B")
    pay_wages(E, B)
    # pr(E.REG)
    print("\nSell A to O3")
    sell(E, A, V, 2)
    # pr(E.REG)
    print("\nProduce V")
    produce(E, V)
    # pr(E.REG)
    print("\nPay workers V")
    pay_wages(E, V)
    pr(E.REG)
    print("\nWorkers buy V")
    sell(E, V, A["workers"], 1)
    sell(E, V, B["workers"], 1)
    sell(E, V, V["workers"], 2)
    pr(E.REG)
    print("\nWorkers reproduce")
    reproduce_labor(A)
    reproduce_labor(B)
    reproduce_labor(V)
    pr(E.REG)

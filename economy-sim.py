from PRINT_REGISTRY import print_registry as pr
from MONEY import MONEY, ACCOUNT, COMMODITY
from MONEY import value_to_money as vtm

'''
Note: For the moment, we consider currency and value to be equal, effectively locking currency to labor hours.

Fix:

'''

workday: float = vtm(8.) # 8 h workday expressed in money

class ECONOMY: # Registry to keep track of items and actors in the economy
    def __init__(self,
                 money_value: float):
        self.REG = {} # Registry
        
def add_owner(E: ECONOMY,
              owner: str,
              money: float) -> dict:
    E.REG[owner] = {"label": owner,
                    "money": ACCOUNT(money)}
    E.REG[owner]["balance"] = ACCOUNT(0., E.REG[owner]["money"])
    E.REG[owner]["inventory"] = {}
    return E.REG[owner]

def add_product(owner: dict,
                product: str,
                recipe: dict[float, ...],
                inventory: dict[list[float, float], ...],
                productionCost: float,
                balance: float,
                profitRate: float) -> dict:
    
    if recipe.keys() != inventory.keys():
            raise Exception("Inventory and recipe keys must be the same.")

    if product not in owner:
        free_workers = recipe["inputs"]["workers"] - inventory["inputs"]["workers"]
        wage = vtm(4.) #NB: Currently assuming a wage of 4 h upon instantiation. Should be made arbitrary
        money_workers = MONEY(0.)
        owner[product] = {"label": product,
                          "owner": owner,
                          "balance": ACCOUNT(balance, owner["balance"]),
                          "profitRate": profitRate,
                          "recipe": recipe,
                          "inventory": inventory,
                          "productionCost": MONEY(productionCost),
                          "workers": {"label": f"W{product}",
                                      "product": {},
                                      "money": money_workers,
                                      "number": free_workers,
                                      "wage": wage,
                                      "inventory": {}}}
        owner[product]["workers"]["product"] = owner[product]
    
    return (owner[product], owner[product]["workers"])

def set_unit_price(product: dict) -> None:
    #NB: Implement logic to determine profit rate. E.g., tendency to increase profit rate until sale revenue begins to decline.
    product["inventory"]["output"].unit_value = product["productionCost"] * (1. + product["profitRate"]) / product["inventory"]["output"].amount
    product["recipe"]["output"].unit_value = product["productionCost"] * (1. + product["profitRate"]) / product["inventory"]["output"].amount

def produce(product: dict) -> None:
    
    inputs = product["recipe"]["inputs"]
    inventory = product["inventory"]["inputs"]
    output = product["recipe"]["output"]
    stocks = inventory["materials"]
    materials = inputs["materials"]
    labor = inputs["workers"]
    paid_wage = labor.value
    
    if any([i < j for i,j in zip(stocks.values(), materials.values())]): # Wait if not enough material for production cycle
        print(f"Not enough material for owner {product['owner']} to produce {product['label']}.")
        return
    
    if inventory["workers"] < labor: # Wait if not enough labor for production cycle
        print(f"Not enough labor for owner {product['owner']} to produce {product['label']}.")
        return
    
    material_cost = sum([units.amount * units.unit_value for units in stocks.values()], MONEY(0.))
    production_cost = paid_wage + material_cost
    
    for material in materials.values():
        stocks[material.category] -= material
        
    inventory["workers"] -= labor
    product["productionCost"] += production_cost
    product["inventory"]["output"] += output
    set_unit_price(product)
    
def pay_wages(product: dict) -> None:
    owner = product["owner"]
    workers = product["workers"]
    labor = product["recipe"]["inputs"]["workers"]
    payout = workers["wage"] * labor.amount #NB: Assuming all labor paid at once, maybe change to piecemeal payments?
    
    if owner["money"] < payout: # Wait if not enough money to pay workers for one production cycle
        print(f"Not enough money for producer {owner['label']} of product {product['label']} to pay workers.")
        return
    
    workers["money"] += payout
    product["balance"] -= payout

def sell(product: dict,
         buyer: dict,
         units_amount: float) -> None:
    stock = product["inventory"]["output"]
    units = COMMODITY(stock.category, units_amount, stock.unit_value)
    inventory = buyer["inventory"]
    prod = product["label"]
    seller = product["owner"]
    price = units.value
    
    product["productionCost"] *= (stock.amount - units.amount) / stock.amount # Production cost of remaining stock
    product["inventory"]["output"] -= units
    product["balance"] += price
    
    if "money" in buyer.keys(): # If worker or owner (for personal consumption, MOS)
        try:
            inventory[prod] += units
        except:
            inventory[prod] = units
        
        try: #if owner
            buyer["balance"] -= price
        except: #if worker
            buyer["money"] -= price

    else: # If producer (for productive consumption, MOP)
        try:
            inventory["inputs"]["materials"][prod] += units
        except:
            inventory["inputs"]["materials"][prod] = units
        buyer["balance"] -= price

    if product["balance"] < MONEY(0.):
        print(f"Note: Producer {seller['label']} of {product['label']} sees negative balance after sale.")

def reproduce_labor(product: dict) -> None:
    workers = product["workers"]
    inventory = workers["inventory"]
    for key, value in inventory.items(): #NB: Currently assuming 1 item in the inventory is sufficient to reproduce 1 worker. Generalize later
        units = int(value.amount) # Floor to whole number when positive
        if units >= 1:
            inventory[key] -= units
            workers["number"] += units
            break
        else:
            print(f"No MOS for reproduction for workers of product {product['label']} ({product['owner']}).")

def luxury_consumption(consumer: dict,
                       consume_all: bool = True,
                       *units: tuple[COMMODITY, ...]) -> None:
    inventory = consumer["inventory"]
    if consume_all:
        for key in inventory: inventory[key].amount = 0.
    else:
        for item in units:
            try:
                if item.amount > inventory[item.category].amount:
                    inventory[item.category] -= item
                else:
                    inventory[item.category] = 0.
                    print(f"Not enough {item.category} in inventory; inventory set to 0.")
            except:
                print(f"{item.category} not found in inventory.")
            
if __name__ == "__main__":
    E = ECONOMY(1)
    pr(E.REG)
    print("\nAdd owners")
    O1 = add_owner(E, "O1", 50)
    O2 = add_owner(E, "O2", 50)
    O3 = add_owner(E, "O3", 50)
    pr(E.REG)
    print("\nAdd products")
    A, WA = add_product(O1, "A", {"inputs":
                                 {"materials":
                                  {"B": COMMODITY("B", 1, 16)},
                                  "workers": COMMODITY("workers", 1, 4)},
                                 "output": COMMODITY("A", 3, 0.)},
                                {"inputs":
                                 {"materials":
                                 {"B": COMMODITY("B", 1, 16)},
                                  "workers": COMMODITY("workers", 1, 4)},
                                 "output": COMMODITY("A", 0, 0.)}, 0, 0, 0.15)
    B, WB = add_product(O2, "B", {"inputs":
                                 {"materials":
                                  {"A": COMMODITY("A", 1, 8.)},
                                  "workers": COMMODITY("workers", 1, 4)},
                                 "output": COMMODITY("B", 1, 0.)},
                                {"inputs":
                                 {"materials":
                                 {"A": COMMODITY("A", 0, 8.)},
                                  "workers": COMMODITY("workers", 1, 4)},
                                 "output": COMMODITY("B", 0, 0.)}, 0, 0, 0.15)
    V, WV = add_product(O3, "V", {"inputs":
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
    produce(A)
    # pr(E.REG)
    print("\nPay workers A")
    pay_wages(A)
    # pr(E.REG)
    print("\nSell A to O2")
    sell(A, B, 1)
    # pr(E.REG)
    print("\nProduce B")
    produce(B)
    # pr(E.REG)
    print("\nPay workers B")
    pay_wages(B)
    # pr(E.REG)
    print("\nSell A to O3")
    sell(A, V, 2)
    # pr(E.REG)
    print("\nProduce V")
    produce(V)
    # pr(E.REG)
    print("\nPay workers V")
    pay_wages(V)
    pr(E.REG)
    print("\nWorkers buy V")
    sell(V, A["workers"], 1)
    sell(V, B["workers"], 1)
    sell(V, V["workers"], 2)
    pr(E.REG)
    print("\nWorkers reproduce")
    reproduce_labor(A)
    reproduce_labor(B)
    reproduce_labor(V)
    pr(E.REG)
    
    # print("\nAdd owner")
    # add_owner("O2", [50, 50])
    # pr(E.REG)
    # print("\nAdd product")
    # add_product({"inputs": {"materials": {"B": [1, 16]}, "workers": [1, 4]}, "output": 2}, {"inputs": {"materials": {"B": [1, 16]}, "workers": [0, 4]}, "output": 1},"A","O2")
    # pr(E.REG)
    # print("\nChange A workers")
    # E.REG["O1"]["A"]["inventory"]["workers"] = 1
    # pr(E.REG)

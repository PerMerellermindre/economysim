from PRINT_REGISTRY import print_registry as pr
from MONEY import MONEY, ACCOUNT, COMMODITY
from MONEY import value_to_money as vtm
from random import choices
from collections import Counter

'''
Note: For the moment, we consider currency and value to be equal, effectively locking currency to labor hours.

Fix:

'''

workday: float = vtm(8.) # 8 h workday expressed in money

class ECONOMY: # Registry to keep track of items and actors in the economy
    def __init__(self,
                 label: str = "E"):
        self.REG = {"label": label,
                    "MOS": dict(), # Means of subsistence. NB: Lists producers, but pr(E.REG) displays them as their specific output to prevent clutter
                    "MOP": dict()} # Means of production. NB: Lists producers, but pr(E.REG) displays them as their specific output to prevent clutter
                    
        print(f"Initializing economy {self.REG['label']}.")

    def __iter__(self):
            yield self
            yield self.REG["MOS"]
            yield self.REG["MOP"]

def add_owner(E: ECONOMY,
              owner: str,
              money: float) -> dict:
    E.REG[owner] = {"economy": E.REG,
                    "label": owner,
                    "holdings": ACCOUNT(money)}
    E.REG[owner]["money"] = ACCOUNT(money, E.REG[owner]["holdings"])
    E.REG[owner]["balance"] = ACCOUNT(0., E.REG[owner]["money"])
    E.REG[owner]["inventory"] = {}
    
    print(f"Adding owner {owner}.")
    
    return E.REG[owner]

def add_producer(owner: dict,
                label: str,
                department: str,
                recipe: dict[float, ...],
                inventory: dict[list[float, float], ...],
                productionCost: float,
                balance: float,
                profitRate: float) -> dict:
    
    if recipe.keys() != inventory.keys():
            raise Exception("Inventory and recipe keys must be the same.")

    if label not in owner:
        free_workers = recipe["inputs"]["workers"] - inventory["inputs"]["workers"]
        wage = vtm(4.) #NB: Currently assuming a wage of 4 h upon instantiation. Should be made arbitrary
        money_workers = MONEY(0.)
        owner[label] = {"label": label,
                        "owner": owner,
                        "balance": ACCOUNT(balance, owner["balance"]),
                        "profitRate": profitRate,
                        "recipe": recipe,
                        "inventory": inventory,
                        "productionCost": MONEY(productionCost),
                        "workers": {"label": f"W{label}",
                                    "product": {},
                                    "money": money_workers,
                                    "number": free_workers,
                                    "wage": wage,
                                    "inventory": {}}}
        producer = owner[label]
        money = owner["money"]
        for item in inventory["inputs"]["materials"].values(): # Subtracting initial investments from money
            money.amount -= item.value.amount # Subtracting amounts to not affect holdings (i.e. to not trigger the ACCOUNT .parent chain)
        money.amount -= inventory["inputs"]["workers"].value.amount # See last comment
        producer["workers"]["producer"] = producer
        category = recipe["output"].category
        if department in ("MOS", "MOP"):
            try:
                producers = owner["economy"][department][category]
                producers.append(producer)
                order_by_price(producers, len(producers) - 1)
            except:
                owner["economy"][department][category] = [producer] # NB: Make unique to owner. Currently not unique.
        else:
            print("Invalid department.")
        producer["sameProducts"] = owner["economy"][department][category]
    else:
        print(f"Owner {owner['label']} already produces {label}.")
        
    print(f"Adding producer {producer['label']} of product {producer['recipe']['output'].category} to the portofolio of {owner['label']}.")
    
    return (owner[label], owner[label]["workers"])

def set_unit_price(producer: dict) -> None:
    #NB: Implement logic to determine profit rate. E.g., tendency to increase profit rate until sale revenue begins to decline.
    producer["inventory"]["output"].unit_value = producer["productionCost"] * (1. + producer["profitRate"]) / producer["inventory"]["output"].amount
    producer["recipe"]["output"].unit_value = producer["productionCost"] * (1. + producer["profitRate"]) / producer["inventory"]["output"].amount

def produce(producer: dict) -> None:
    
    inputs = producer["recipe"]["inputs"]
    inventory = producer["inventory"]["inputs"]
    output = producer["recipe"]["output"]
    stocks = inventory["materials"]
    materials = inputs["materials"]
    labor = inputs["workers"]
    paid_wage = labor.value
    
    if any([i < j for i,j in zip(stocks.values(), materials.values())]): # Wait if not enough material for production cycle
        print(f"Not enough material for producer {producer['label']} to produce {producer['inventory']['output'].category}.")
        return
    
    if inventory["workers"] < labor: # Wait if not enough labor for production cycle
        print(f"Not enough labor for producer {producer['label']} to produce {producer['inventory']['output'].category}.")
        return
    
    material_cost = sum([units.amount * units.unit_value for units in stocks.values()], MONEY(0.))
    production_cost = paid_wage + material_cost
    
    for material in materials.values():
        stocks[material.category] -= material
        
    inventory["workers"] -= labor
    producer["productionCost"] += production_cost
    producer["inventory"]["output"] += output
    set_unit_price(producer)
    
    print(f"{producer['label']} produces {producer['recipe']['output'].category}.")
    
def pay_wages(producer: dict) -> None:
    owner = producer["owner"]
    workers = producer["workers"]
    labor = producer["recipe"]["inputs"]["workers"]
    payout = workers["wage"] * labor.amount #NB: Assuming all labor paid at once, maybe change to piecemeal payments?
    
    if owner["money"] < payout: # Wait if not enough money to pay workers for one production cycle
        print(f"Not enough money for producer {owner['label']} of producer {producer['label']} to pay workers.")
        return
    
    workers["money"] += payout
    producer["balance"] -= payout
    
    print(f"{owner['label']} pays workers {workers['label']}.")
    

def buy(producers: dict | list,
        buyer: dict,
        units: float = 1) -> None:
    
    print(f"{buyer['label']} buys {units} {producers[0]['inventory']['output'].category}.")
    
    if isinstance(producers, dict): # Passing individual producer
        sell(producers, buyer, units)
        return
    elif isinstance(producers, list): # Passing department list of producers of same product
        basket = []
        amount = 0.
        bought = 0.
        bought_idx = 0
        intermediate_amount = 0.
    
        for i in range(len(producers) - 1):
            output = producers[i]["inventory"]["output"]
            next_output = producers[i + 1]["inventory"]["output"]
            if output.amount > 0.:
                amount += output.amount
                basket.append(output)
    
            if next_output.unit_value == output.unit_value:
                continue
    
            if basket:
                basket_amount = amount - intermediate_amount
                units_to_buy = round(min(basket_amount, units - bought)) # NB: Rounding to integer to make choices-function below work. Should be made to work with floats in case of wholesale liquids etc.
                if len(basket) == 1:
                    sell(producers[i], buyer, units_to_buy)
                else:
                    items_chosen = choices(range(len(basket)),
                                           weights = [item.amount/basket_amount for item in basket],
                                           k = units_to_buy)
                    for basket_idx, tally in Counter(items_chosen).items():
                        sell(producers[bought_idx + basket_idx], buyer, tally)
                bought += units_to_buy
                bought_idx = i + 1
                intermediate_amount = amount
                basket.clear()
    
            if bought >= units:
                return
    
        output = producers[-1]["inventory"]["output"]  # Handle last element
        if output.amount > 0.:
            basket.append(output)
        if basket:
            basket_amount = amount - intermediate_amount + (output.amount if output.amount > 0. else 0.)
            units_to_buy = round(min(basket_amount, units - bought)) # NB: Rounding to integer to make choices-function below work. Should be made to work with floats in case of wholesale liquids etc.
            if len(basket) == 1:
                sell(producers[-1], buyer, units_to_buy)
                bought += units_to_buy
            else:
                items_chosen = choices(range(len(basket)),
                                       weights = [item.amount/basket_amount for item in basket],
                                       k = units_to_buy)
                for basket_idx, tally in Counter(items_chosen).items():
                    sell(producers[bought_idx + basket_idx], buyer, tally)
                bought += units_to_buy
        if bought < units:
            print(f"NB: Sales request of {producers[0]['inventory']['output'].category} exceeds all stocks. Depleting all stocks.")
        return
    else: 
        raise NotImplementedError()
    

def order_by_price(producers: list,
                   idx: float) -> None: # Sorting algorithm optimized for an already sorted list with one perturbed element, generally close in value to its neighbors.
    prices = [item["inventory"]["output"].unit_value for item in producers]    
    new_idx = idx
    while new_idx < len(prices) - 1 and prices[new_idx + 1] < prices[idx]:
        new_idx += 1
    while new_idx > 0 and prices[new_idx - 1] > prices[idx]:
        new_idx -= 1
    if new_idx != idx:
        producers.insert(new_idx, producers.pop(idx))

def sell(producer: dict,
         buyer: dict,
         units: float) -> None:
    stock = producer["inventory"]["output"]
    units = COMMODITY(stock.category, units, MONEY(stock.unit_value.amount))
    inventory = buyer["inventory"]
    category = stock.category
    seller = producer["owner"]
    if units > stock:
        units = stock
        print(f"NB: Sales request of {producer['label']} exceeds stock of producer {seller['label']}. Depleting stock.")
    price = units.value
    
    producer["productionCost"] *= (stock.amount - units.amount) / stock.amount # Production cost of remaining stock
    producer["inventory"]["output"] -= units
    producer["balance"] += price
    
    if "money" in buyer.keys(): # If worker or owner (for personal consumption, MOS)
        try:
            inventory[category] += units
        except:
            inventory[category] = units
        
        try: #if owner
            buyer["balance"] -= price
        except: #if worker
            buyer["money"] -= price

    else: # If producer (for productive consumption, MOP)
        try:
            inventory["inputs"]["materials"][category] += units
        except:
            inventory["inputs"]["materials"][category] = units
        buyer["balance"] -= price

    # if producer["balance"] < MONEY(0.):
    #     print(f"Note: Producer {seller['label']} of {producer['label']} sees negative balance after sale.")

def reproduce_labor(workers: dict) -> None:
    producer = workers["producer"]
    inventory = workers["inventory"]
    for key, value in inventory.items(): #NB: Currently assuming 1 item in the inventory is sufficient to reproduce 1 worker. Generalize later
        units = int(value.amount) # Floor to whole number when positive
        if units >= 1:
            inventory[key] -= units
            workers["number"] += units
            break
        else:
            print(f"No MOS for reproduction for workers of producer {producer['label']} ({producer['owner']}).")
    
    print(f"Reproducing {workers['label']}.")

def luxury_consumption(consumer: dict,
                       consume_all: bool = True,
                       *units: tuple[COMMODITY, ...]) -> None:
    inventory = consumer["inventory"]
    if consume_all:
        for key in inventory: inventory[key].amount = 0.
        
        print(f"{consumer['label']} consumes all their MOS.")
    else:
        for item in units:
            try:
                if item.amount > inventory[item.category].amount:
                    inventory[item.category] -= item
                    print(f"{consumer['label']} consumes {item}.")
                else:
                    inventory[item.category] = 0.
                    print(f"Not enough {item.category} in inventory; {consumer['label']} consumes entire inventory.")
            except:
                print(f"{item.category} not found in inventory of {consumer['label']}.")
            
    
if __name__ == "__main__":
    E, MOS, MOP = ECONOMY()
    O1 = add_owner(E, "O1", 50)
    O2 = add_owner(E, "O2", 50)
    O3 = add_owner(E, "O3", 50)
    A1, WA = add_producer(O1, "A1", "MOP", {"inputs":
                                            {"materials":
                                             {"B": COMMODITY("B", 1, 16)},
                                             "workers": COMMODITY("workers", 1, 4)},
                                            "output": COMMODITY("A", 3, 0.)},
                                           {"inputs":
                                            {"materials":
                                             {"B": COMMODITY("B", 1, 16)},
                                             "workers": COMMODITY("workers", 1, 4)},
                                            "output": COMMODITY("A", 3, 5.)}, 0, 0, 0.15)
    B2, WB = add_producer(O2, "B2", "MOP", {"inputs":
                                            {"materials":
                                             {"A": COMMODITY("A", 1, 8.)},
                                             "workers": COMMODITY("workers", 1, 4)},
                                             "output": COMMODITY("B", 1, 0.)},
                                            {"inputs":
                                             {"materials":
                                             {"A": COMMODITY("A", 0, 8.)},
                                              "workers": COMMODITY("workers", 1, 4)},
                                             "output": COMMODITY("B", 0, 0.)}, 0, 0, 0.15)
    A2, WA2 = add_producer(O2, "A2", "MOP", {"inputs":
                                             {"materials":
                                              {"B": COMMODITY("B", 1, 16)},
                                              "workers": COMMODITY("workers", 1, 4)},
                                             "output": COMMODITY("A", 3, 0.)},
                                            {"inputs":
                                             {"materials":
                                             {"B": COMMODITY("B", 1, 16)},
                                              "workers": COMMODITY("workers", 1, 4)},
                                             "output": COMMODITY("A", 1, 1.)}, 0, 0, 0.15)
    V3, WV = add_producer(O3, "V3", "MOS", {"inputs":
                                            {"materials":
                                             {"A": COMMODITY("A", 2, 8.)},
                                             "workers": COMMODITY("workers", 2, 4)},
                                            "output": COMMODITY("V", 8, 0.)},
                                           {"inputs":
                                            {"materials":
                                             {"A": COMMODITY("A", 0, 8.)},
                                             "workers": COMMODITY("workers", 2, 4)},
                                            "output": COMMODITY("V", 0, 0.)}, 0, 0, 0.15)
    A3, WA3 = add_producer(O3, "A3", "MOP", {"inputs":
                                             {"materials":
                                              {"B": COMMODITY("B", 1, 16)},
                                              "workers": COMMODITY("workers", 1, 4)},
                                             "output": COMMODITY("A", 3, 0.)},
                                            {"inputs":
                                             {"materials":
                                             {"B": COMMODITY("B", 1, 16)},
                                              "workers": COMMODITY("workers", 1, 4)},
                                             "output": COMMODITY("A", 2, 5.)}, 0, 0, 0.15)
    produce(A1)
    pay_wages(A1)
    buy(MOP["A"], B2, 1)
    produce(B2)
    pay_wages(B2)
    buy(MOP["A"], V3, 2)
    produce(V3)
    pay_wages(V3)
    buy(MOS["V"], WA, 1)
    buy(MOS["V"], WB, 1)
    buy(MOS["V"], WV, 2)
    reproduce_labor(WA)
    reproduce_labor(WB)
    reproduce_labor(WV)
    buy(MOS["V"], O1, 1)
    buy(MOS["V"], O2, 1)
    buy(MOS["V"], O3, 2)
    luxury_consumption(O1)
    luxury_consumption(O2)
    luxury_consumption(O3)
    pr(E.REG)

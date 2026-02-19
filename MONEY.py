class MONEY:
    unit_value = 1 # Unit value of money
    
    def __init__(self,
                 amount: float):
        self.amount = amount
        
    @property
    def value(self):
        return self.amount * MONEY.unit_value
    
    def new_unit_value(self,
                  new: float) -> None:
        MONEY.unit_value = new
        
    def __add__(self,
                other: "MONEY" or int or float) -> "MONEY":
        if isinstance(other, (int, float)):
            return MONEY(self.amount + other)
        elif isinstance(other, MONEY):
            return MONEY(self.amount + other.amount)
        else:
            raise NotImplementedError()
    
    def __sub__(self,
                other: "MONEY" or int or float) -> "MONEY":
        if isinstance(other, (int, float)):
            return MONEY(self.amount - other)
        elif isinstance(other, MONEY):
            return MONEY(self.amount - other.amount)
        else:
            raise NotImplementedError()
    
    def __mul__(self,
                other: int | float) -> "MONEY":
        return MONEY(self.amount * other)
    
    def __rmul__(self,
                other: int | float) -> "MONEY":
        return self.__mul__(other)
    
    def __truediv__(self,
                other: int | float) -> "MONEY":
        return MONEY(self.amount / other)
    
    def __eq__(self,
                other: "MONEY") -> bool:
        return self.amount == other.amount
    
    def __ne__(self,
                other: "MONEY") -> bool:
        return self.amount != other.amount
    
    def __lt__(self,
                other: "MONEY") -> bool:
        return self.amount < other.amount
    
    def __gt__(self,
                other: "MONEY") -> bool:
        return self.amount > other.amount
    
    def __le__(self,
                other: "MONEY") -> bool:
        return self.amount <= other.amount
    
    def __ge__(self,
                other: "MONEY") -> bool:
        return self.amount >= other.amount
    
    def __str__(self):
        if self.amount < 0.: return f"-£{round(-self.amount, 2)}"
        else: return f"£{round(self.amount, 2)}"
    
    def __repr__(self):
        return self.__str__()
    
def value_to_money(amount: float) -> MONEY:
    return MONEY(amount / MONEY.unit_value)

class ACCOUNT(MONEY):
    def __init__(self,
                 amount: float,
                 parent: "ACCOUNT" = None):
        super().__init__(amount)
        self.parent = parent
    
    def __iadd__(self,
                other: "MONEY"):
        if isinstance(other, MONEY):
            p = self.parent
            while True:
                p.amount += other.amount
                if p.parent is not None:
                    p = p.parent
                else: break
            self.amount += other.amount
            return self
        else:
            raise NotImplementedError()
    
    def __isub__(self,
                other: "MONEY") -> "MONEY":
        if isinstance(other, MONEY):
            p = self.parent
            while True:
                p.amount -= other.amount
                if p.parent is not None:
                    p = p.parent
                else: break
            self.amount -= other.amount
            return self
        else:
            raise NotImplementedError()
            
class COMMODITY:
    categories = {}
    def __init__(self,
                 category: str,
                 amount: float,
                 unit_value: MONEY | float):
        if not category in COMMODITY.categories.keys():
            COMMODITY.categories[category] = None
        self.category = category
        self.amount = amount
        if isinstance(unit_value, MONEY): self.unit_value = unit_value
        else: self.unit_value = MONEY(unit_value)
    
    @property
    def value(self):
        return self.amount * self.unit_value
    
    def __add__(self,
                other: "COMMODITY" or int or float) -> "COMMODITY":
        if isinstance(other, (int, float)):
            return COMMODITY(self.category,
                             self.amount + other,
                             self.unit_value)
        elif isinstance(other, COMMODITY) and other.category == self.category:
            return COMMODITY(self.category,
                             self.amount + other.amount,
                             (self.amount * self.unit_value + other.amount * other.unit_value) \
                              / (self.amount + other.amount))
        else:
            raise NotImplementedError()
    
    def __sub__(self,
                other: "COMMODITY" or int or float) -> "COMMODITY":
        if isinstance(other, (int, float)):
            return COMMODITY(self.category,
                             self.amount - other,
                             self.unit_value)
        elif isinstance(other, COMMODITY) and other.category == self.category:
            return COMMODITY(self.category,
                             self.amount - other.amount,
                             self.unit_value) #NB: Assuming the new stock has the unit value of the lhs of the operator. The unit value of the rhs is discarded.
        else:
            raise NotImplementedError()
    
    def __iadd__(self,
                other: "COMMODITY" or int or float) -> "COMMODITY":
        if isinstance(other, (COMMODITY, int, float)):
            self = self.__add__(other)
            return self
        else:
            raise NotImplementedError()
    
    def __isub__(self,
                other: "COMMODITY" or int or float) -> "COMMODITY":
        if isinstance(other, (COMMODITY, int, float)):
            self = self.__sub__(other)
            return self
        else:
            raise NotImplementedError()
    
    def __mul__(self,
                other: int | float) -> "COMMODITY":
        if not isinstance(other, (int, float)): raise NotImplementedError()
        else: return COMMODITY(self.category,
                               self.amount * other,
                               self.unit_value)
    
    def __rmul__(self,
                other: int | float) -> "COMMODITY":
        return self.__mul__(other)
    
    def __truediv__(self,
                other: int | float) -> "COMMODITY":
        if not isinstance(other, (int, float)): raise NotImplementedError()
        else: return COMMODITY(self.category,
                               self.amount / other,
                               self.unit_value)
    
    def __eq__(self,
                other: "COMMODITY") -> bool:
        return self.amount == other.amount
    
    def __ne__(self,
                other: "COMMODITY") -> bool:
        return self.amount != other.amount
    
    def __lt__(self,
                other: "COMMODITY") -> bool:
        return self.amount < other.amount
    
    def __gt__(self,
                other: "COMMODITY") -> bool:
        return self.amount > other.amount
    
    def __le__(self,
                other: "COMMODITY") -> bool:
        return self.amount <= other.amount
    
    def __ge__(self,
                other: "COMMODITY") -> bool:
        return self.amount >= other.amount
    
    def __str__(self):
        return f"{round(self.amount, 2)} {self.category} (" + self.unit_value.__str__() + "/u)"
    
    def __repr__(self):
        return self.__str__()
    
if __name__ == "__main__":
    A1 = COMMODITY("A", 2, 10)
    A2 = COMMODITY("A", 4, 5)
    print(A1 + A2)
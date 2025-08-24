from abc import ABC, abstractmethod
from ReportParsers import Transaction
import re
from datetime import date
from typing import List, Tuple, Union
from enum import Enum

class FlowDirection(Enum):
    EARNINGS = "earnings"
    EXPENSES = "expenses"
    NEUTRAL = "neutral"

def match_receiver_and_date(pattern: re.Pattern, match_date:Union[date, Tuple[date]], transaction: Transaction)-> bool:
    result = pattern.search(transaction.receiver) 
    if match_date is None:
        return result
    if isinstance(match_date, tuple):
        assert len(match_date) == 2
        return result and transaction.date >= match_date[0] and transaction.date <= match_date[1]
    elif isinstance(match_date, date):
        return result and transaction.date == match_date
    else:
        raise ValueError(f"Unexpected type of match_date {match_date}, {type(match_date)}")


class Category(ABC):
    def __init__(self, name: str):
        self._name = name
        self._transactions: List[Transaction] = []
        self._total: float = 0.0

    def get_name(self) -> str:
        return self._name

    def add_transaction(self, transaction: Transaction) -> None:
        self._transactions.append(transaction)
        self._total += transaction.amount

    def get_total(self) -> float:
        return self._total

    def get_transactions(self) -> List[Transaction]:
        self._transactions.sort()
        return self._transactions

    @abstractmethod
    def is_matched(self, transaction: Transaction) -> bool:
        pass
    
    @abstractmethod
    def get_flow_direction(self) -> FlowDirection:
        pass


class Groceries(Category):
    def __init__(self):
        super().__init__('Groceries')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^(bck\*)?jumbo"),
            re.compile(r"^(bck\*)?kiosk"),
            re.compile(r"^albert heijn(?:\s|$)"),
            re.compile(r"^(bck\*)?(.*)ah to go(?:\s|$)"),
            re.compile(r"^smak$"),
        ]
        return any(p.search(transaction.receiver) for p in patterns)
    
    def get_flow_direction(self):
        return FlowDirection.EXPENSES


class Transport(Category):
    def __init__(self):
        super().__init__('Transport')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^nlov[a-z0-9]{14}$"),
            re.compile(r"^uber$"),
            re.compile(r"^ns groep iz ns reizigers$"),
            re.compile(r"^greenwheels\s"),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class Insurance(Category):
    def __init__(self):
        super().__init__('Insurance')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^abn amro schadev nv$"),
            re.compile(r"^zilveren kruis\s"),
            re.compile(r"^allianz\s"),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class HouseholdGoods(Category):
    def __init__(self):
        super().__init__('Household goods')

    def is_matched(self, transaction: Transaction) -> bool:
        match_args = [
            (re.compile(r"^amazon [a-z0-9]+"), None),
            (re.compile(r"^ikea bv$"), None),
            (re.compile(r"^hema(?:\s|$)"), None),
            (re.compile(r"^gamma(?:$|-nl|\s)"), None),
            (re.compile(r"^bol\.com$"), None),
            (re.compile(r"^rituals(cosmetics)?$"), None),
            (re.compile(r"^action [0-9]+$"), None),
            (re.compile(r"^lush\s"), None),
            (re.compile(r"^coolblue$"), None),
            (re.compile(r"motel a miio"), None),
            (re.compile(r"^patelnia\.nl$"), None),
            (re.compile(r"^klusbedrijf mrfix\.nl b\.v\."), None),
            (re.compile(r"^klarna bank\s"), date(2025, 1, 15)),
            (re.compile(r"^jysk\s"), None),
            (re.compile(r"^de gouden sleutel$"), None),
            (re.compile(r"^actievloeren\s"), None),
        ]
        return any(match_receiver_and_date(p, d, transaction) for p, d in match_args)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class Restaurants(Category):
    def __init__(self):
        super().__init__('Restaurants')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^de cafe new babylon$"),
            re.compile(r"^coffee district"),
            re.compile(r"^uber eats$"),
            re.compile(r"^(bck\*)?bakers house$"),
            re.compile(r"^(ccv\*)?starbucks\s"),
            re.compile(r"^(zettle_\*)?perron x coffe$"),
            re.compile(r"^mcturfmarkt$"),
            re.compile(r"^(zettle_\*)?house of tribe$"),
            re.compile(r"^(zettle_\*)?coffee garden$"),
            re.compile(r"^(zettle_\*)?circle lunchro$"),
            re.compile(r"^joe\s+the juice\s"),
            re.compile(r"^coffee and coconuts$"),
            re.compile(r"^chco den haag$"),
            re.compile(r"^bk den haag spui$"),
            re.compile(r"^(cm\.\*)?rdvr$"),
            re.compile(r"^(ccv\*)?pqnl gelderland$"),
            re.compile(r"^the villy the roofs$"),
            re.compile(r"^noodlebar herengracht$"),
            re.compile(r"^madame croissant$"),
            re.compile(r"^eetcafe el mamma booga$"),
            re.compile(r"^(ccv\*)?multivlaai\s"),
            re.compile(r"^benji\s"),
            re.compile(r"^(bck\*)?durak sweets$"),
            re.compile(r"^(bck\*)?cafe van beek$")
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class Gina(Category):
    def __init__(self):
        super().__init__('Gina')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^pp_amsterdam$"),
            re.compile(r"^zooplus\s"),
            re.compile(r"^petsplace"),
            re.compile(r"^(ccv\*)?dier van nu$"),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class Health(Category):
    def __init__(self):
        super().__init__('Health')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^etos [a-z0-9\.]+"),
            re.compile(r"^holland \& barrett$"),
            re.compile(r"^ondalinda$"),         # SEKTA
            re.compile(r"^newpharma\s"),
            re.compile(r"^dap bezuidenhout\s"),
            re.compile(r"^coderscourse\.com$"),
            re.compile(r"^(ccv\*)?stichting dienstap$"),
            re.compile(r"apotheek\s"),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class Clothes(Category):
    def __init__(self):
        super().__init__('Clothes')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^shein\.com$"),
            re.compile(r"^schiesser\s"),
            re.compile(r"^h\.m online$"),
            re.compile(r"^globale$"),
            re.compile(r"^otherstories$"),
            re.compile(r"^nimara\s"),
            re.compile(r"^manfield\s"),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class Child(Category):
    def __init__(self):
        super().__init__('Child')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^baby-dump b\.?v\.?$"),
            re.compile(r"^babywinkel b\.v\."),
            re.compile(r"^kruidvat(?:\s|$)"),
            re.compile(r"^uwv$"),
            re.compile(r"^lovevery\s"),
            re.compile(r"^zeeman$"),
            re.compile(r"^simply colors nederland b\.v\."),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class Entertainment(Category):
    def __init__(self):
        super().__init__('Entertainment')

    def is_matched(self, transaction: Transaction) -> bool:
        return False

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class Taxes(Category):
    def __init__(self):
        super().__init__('Taxes')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^immigratie en naturalisatie dienst$"), 
            re.compile(r"^gemeente\s"),
            re.compile(r"belasting"),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class Documents(Category):
    def __init__(self):
        super().__init__('Documents')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^publiekszaken$"),
            re.compile(r"^lvov a\.m\.\s"),
            re.compile(r"^printed\.nl$"),
            re.compile(r"^kudinova via tikkie$"),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class VVE(Category):
    def __init__(self):
        super().__init__('VVE')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^vve la fenetre$"),
            re.compile(r"^vereniging van eigenaars la fen"),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class Bills(Category):
    def __init__(self):
        super().__init__('Bills')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^odido netherlands b.v.$"),
            re.compile(r"^ziggo services bv$"),
            re.compile(r"^eneco services$"),
            re.compile(r"^magticom$"),
            re.compile(r"^dunea duin\s"),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class Banks(Category):
    def __init__(self):
        super().__init__('Banks')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^abn amro bank n.v.$"),
            re.compile(r"^kosten tweede rekeninghouder$"),
            re.compile(r"^kosten oranjepakket$"),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class InternalTransfers(Category):
    def __init__(self):
        super().__init__('InternalTransfers')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^safe net$"),
            re.compile(r"^d\.? krymova$"),
            re.compile(r"^hr b lakatosh,mw d krymova"),
            re.compile(r"^mpay\*dkrymova$"),
            re.compile(r"^(b|bohdan) lakatosh$"),
            re.compile(r"^necessities$"),
            re.compile(r"^revolut.*3740.*$"),
            re.compile(r"^revolut bank uab$"),
            re.compile(r"^oranje spaarrekening$"),
            re.compile(r"^ideal top-up$"), # TODO amount should be positive to match
            re.compile(r"^apple pay top-up\s"), # TODO amount should be positive
            re.compile(r"^moonpay$"),
            re.compile(r"^interactive brokers ireland limited$"),
            re.compile(r"^a lakatosh$"),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.NEUTRAL

class Apartment(Category):
    def __init__(self):
        super().__init__('Apartment')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^ing hypotheken$"),
            re.compile(r"^teilingen residence b\.v\.$"),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class Income(Category):
    def __init__(self):
        super().__init__('Income')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^imc trading bv$"),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EARNINGS

class Services(Category):
    def __init__(self):
        super().__init__('Services')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^azarova consulting$"),
            re.compile(r"^openai$"),
            re.compile(r"^apple$"),
            re.compile(r"^tilda$"),
            re.compile(r"^spotify$"),
            re.compile(r"^shopify$"),
            re.compile(r"^ngrok\.com$"),
            re.compile(r"^google one$"),
            re.compile(r"^audible$"),
            re.compile(r"^youtube$"),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class Others(Category):
    def __init__(self):
        super().__init__('Others')

    def is_matched(self, transaction: Transaction) -> bool:
        
        match_args = [
            (re.compile(r"^(ccv\*)?kroonenberg groep$"), None),
            # Trip to Prague
            (re.compile(r"^albert$"), (date(2025, 3, 8), date(2025, 3, 9))),
            (re.compile(r"^infobus\.eu$"), None),   # tickets for my parents
            # End of Prague trip 
            (re.compile(r"^tunity$"), None),    # haircut
            (re.compile(r"^transfer to revolut user$"), (date(2025,4,11), date(2025, 4,14))),
            (re.compile(r"^shared packaging$"), (date(2025,1,15), date(2025,1,27))),
            (re.compile(r"^postnl holding b.v.$"), date(2025,2,12)),
            (re.compile(r"^booking$"), date(2025,3,6)),
            (re.compile(r"^hotel on booking.com$"), date(2025,3,6)),
            (re.compile(r"^parfenchikova via tikkie$"), date(2025,4,19)),
            (re.compile(r"^aab inz tikkie$"), date(2025,4,30)),
            (re.compile(r"^den haag cs$"), date(2025,1,16)),
            (re.compile(r"^eye wish opticiens$"), date(2025,3,8)),
            (re.compile(r"^maghnouji via tikkie$"), date(2025,3,21)),
            (re.compile(r"^amsterdam zuid 4208-11$"), date(2025,4,22)),
            (re.compile(r"^to petr petrov$"), date(2025,3,17)),
            (re.compile(r"^swift transfer$"), date(2025,4,28)),
            (re.compile(r"^dopravní podnik hlavního města prahy"), date(2025,3,7)),
            (re.compile(r"^monastery garden$"), date(2025,3,7)),
            (re.compile(r"^u červeného páva$"), date(2025,3,7)),
            (re.compile(r"^bubbletee$"), date(2025,3,8)),
            (re.compile(r"^praha lodě$"), date(2025,3,8)),
            (re.compile(r"^trdelnik shop$"), date(2025,3,7)),
            (re.compile(r"^the cozy asian kitche$"), date(2025,3,9)),
            (re.compile(r"^restaurace malostranská beseda$"), date(2025,3,8)),
            (re.compile(r"^pražský hrad$"), date(2025,3,9)),
            (re.compile(r"^stolk via tikkie$"), date(2025,2,7)),
        ]
        return any(match_receiver_and_date(p, d, transaction) for p, d in match_args) 

    def get_flow_direction(self):
        return FlowDirection.EXPENSES


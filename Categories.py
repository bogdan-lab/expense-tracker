from abc import ABC, abstractmethod
from ReportParsers import Transaction
import re
from datetime import date
from typing import List, Tuple, Union
from enum import Enum
from TransactionTransformers import is_new_transaction

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
        if is_new_transaction(self._transactions, transaction):
            self._transactions.append(transaction)
            self._total += transaction.amount
    
    def add_transactions(self, transactions: List[Transaction]) -> None:
        for tx in transactions:
            self.add_transaction(tx)

    def get_total(self) -> float:
        return self._total

    def get_transactions(self) -> List[Transaction]:
        self._transactions.sort()
        return self._transactions

    def clear(self) -> None:
        self._transactions.clear()
        self._total = 0.0

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
            re.compile(r"^factor\s"),
            re.compile(r"^lidl\b", re.IGNORECASE),
            re.compile(r"^marqt\b", re.IGNORECASE),
            re.compile(r"\brewe(?:\s*to\s*go)?\b", re.IGNORECASE),              
            re.compile(r"^condis\b", re.IGNORECASE),
            re.compile(r"^g20\s+supermarch(?:é|e)s?\b", re.IGNORECASE),
            re.compile(r"\bla\s+grande\s+[eé]picerie\b", re.IGNORECASE),
            re.compile(r"^vlaamsch\s+broodhuys\b", re.IGNORECASE),
            re.compile(r"^villagegrocer\b", re.IGNORECASE),
            re.compile(r"^coles\b", re.IGNORECASE),
            re.compile(r"^woolworths\b", re.IGNORECASE),
            re.compile(r"^ullrich\b", re.IGNORECASE),
            re.compile(r"^areas paris nor$", re.IGNORECASE), 
            re.compile(r"^schoko shop$", re.IGNORECASE), 
            re.compile(r"^tgtg\s+[a-z0-9]+$", re.IGNORECASE), 
            re.compile(r"^theo automaten$", re.IGNORECASE), 
            re.compile(r"\bvb den haag\b", re.IGNORECASE), 
            re.compile(r"^chocoladefabriken lind", re.IGNORECASE), 
            re.compile(r"^f\.h\.w\. gastronomie gmb$", re.IGNORECASE)
        ]
        return any(p.search(transaction.receiver) for p in patterns)
    
    def get_flow_direction(self):
        return FlowDirection.EXPENSES


class Transport(Category):
    def __init__(self):
        super().__init__('Transport')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^nlov[a-z0-9]{14}", re.IGNORECASE),
            re.compile(r"^uber$", re.IGNORECASE),
            re.compile(r"^ns groep iz ns reizigers$", re.IGNORECASE),
            re.compile(r"^ns internationaal\b", re.IGNORECASE),
            re.compile(r"^greenwheels\b", re.IGNORECASE),
            re.compile(r"ovpay", re.IGNORECASE),
            re.compile(r"^easyjet\b", re.IGNORECASE),
            re.compile(r"^eurostar\b", re.IGNORECASE),
            re.compile(r"^vueling\b", re.IGNORECASE),
            re.compile(r"^lufthansa\b", re.IGNORECASE),
            re.compile(r"^pegasus airlines\b", re.IGNORECASE),
            re.compile(r"^international air transport\b", re.IGNORECASE),
            re.compile(r"^kbb gmbh ticket office\b", re.IGNORECASE),
            re.compile(r"^s-bahn berlin automat\b", re.IGNORECASE),
            re.compile(r"\btransport for nsw\b", re.IGNORECASE),
            re.compile(r"^tmb\b$", re.IGNORECASE),
            re.compile(r"^taxibetrieb\b", re.IGNORECASE),
            re.compile(r"^taxi\b", re.IGNORECASE),
            re.compile(r"^charter$", re.IGNORECASE),
            re.compile(r"^azerbaijan airlines$", re.IGNORECASE),
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
            (re.compile(r"^amazon\b"), None),
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
            (re.compile(r"^temu\.com$", re.IGNORECASE), None),
            (re.compile(r"^marktplaats\b", re.IGNORECASE), None),
            (re.compile(r"^het sleutelhuis design$", re.IGNORECASE), None),
            (re.compile(r"\bpaagman\b", re.IGNORECASE), None), 
            (re.compile(r"^lib\. abbesses$", re.IGNORECASE), None), 
            (re.compile(r"\bhering sanikonzept\b", re.IGNORECASE), None), 
            (re.compile(r"^prins-vermolen vof$", re.IGNORECASE), None), 
            (re.compile(r"^aircotech klimaattechniek", re.IGNORECASE), None), 
            (re.compile(r"^downtown souvenirs$", re.IGNORECASE), None),
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
            re.compile(r"^(ccv\*)?starbucks(?:$|\s)"),
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
            re.compile(r"^(bck\*)?cafe van beek$"),
            re.compile(r"dutch language"),
            re.compile(r"luciano"),
            re.compile(r"hms host international"),
            re.compile(r"^austi beach cafe$", re.IGNORECASE),
            re.compile(r"^bagels\s*&\s*beans\b", re.IGNORECASE),
            re.compile(r"^bar shang tung$", re.IGNORECASE),
            re.compile(r"^buenas migas$", re.IGNORECASE),
            re.compile(r"^cafe\b", re.IGNORECASE),
            re.compile(r"\bgelato\b", re.IGNORECASE),
            re.compile(r"\bcoffeecom(?:\.|p)\b", re.IGNORECASE),
            re.compile(r"^coffeeworksvoorburg$", re.IGNORECASE),
            re.compile(r"^de pizzabakkers\b", re.IGNORECASE),
            re.compile(r"^dunkin donuts\b", re.IGNORECASE),
            re.compile(r"^exclusive coffee$", re.IGNORECASE),
            re.compile(r"^grill\s*&\s*broast", re.IGNORECASE),
            re.compile(r"^mcdonald's\b", re.IGNORECASE),
            re.compile(r"^noglu$", re.IGNORECASE),
            re.compile(r"^nonna titti$", re.IGNORECASE),
            re.compile(r"^pret a manger\b", re.IGNORECASE),
            re.compile(r"^restaurant corner$", re.IGNORECASE),
            re.compile(r"^venchi\b", re.IGNORECASE),
            re.compile(r"^world of pizza\b", re.IGNORECASE),
            re.compile(r"^the cozy restaurant$", re.IGNORECASE),
            re.compile(r"^the french bastards$", re.IGNORECASE),
            re.compile(r"\bpadre coffee\b", re.IGNORECASE),
            re.compile(r"\bwakuli\b", re.IGNORECASE),
            re.compile(r"\bthe blue lagoon\b", re.IGNORECASE),
            re.compile(r"^dépôt légal$", re.IGNORECASE), 
            re.compile(r"^die espressonisten$", re.IGNORECASE), 
            re.compile(r"^hmshost international$", re.IGNORECASE), 
            re.compile(r"^in\.gredienti$", re.IGNORECASE), 
            re.compile(r"^le 17 45$", re.IGNORECASE), 
            re.compile(r"^le pain retrouvé$", re.IGNORECASE), 
            re.compile(r"^le recrutement$", re.IGNORECASE), 
            re.compile(r"^luca kin-za alexanderp$", re.IGNORECASE), 
            re.compile(r"^mambo beach exploitati", re.IGNORECASE), 
            re.compile(r"^manta beach$", re.IGNORECASE), 
            re.compile(r"^maximilians$", re.IGNORECASE), 
            re.compile(r"^mcstrandweg$", re.IGNORECASE), 
            re.compile(r"^sonya\b.*takeaway\.com$", re.IGNORECASE), 
            re.compile(r"\bal teatro\b", re.IGNORECASE), 
            re.compile(r"^dudok\b", re.IGNORECASE), 
            re.compile(r"^miss maui beach house$", re.IGNORECASE), 
            re.compile(r"\bfauve cofee\b", re.IGNORECASE), 
            re.compile(r"^bavaria berlin$", re.IGNORECASE),
            re.compile(r"^coffeecom\.\s*-\s*albron$", re.IGNORECASE),
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
            re.compile(r"^veterfina", re.IGNORECASE),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class Health(Category):
    def __init__(self):
        super().__init__('Health')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^etos\s+[a-z0-9\.]+", re.IGNORECASE),
            re.compile(r"^holland\s*(?:&\s*)?barrett$", re.IGNORECASE),   
            re.compile(r"^ondalinda$", re.IGNORECASE),                    # SEKTA
            re.compile(r"^newpharma\s", re.IGNORECASE),
            re.compile(r"^dap bezuidenhout\s", re.IGNORECASE),
            re.compile(r"^coderscourse\.com$", re.IGNORECASE),
            re.compile(r"^(?:ccv\*)?stichting dienstap$", re.IGNORECASE),
            re.compile(r"apotheek\s", re.IGNORECASE),
            re.compile(r"sportcity", re.IGNORECASE),
            re.compile(r"infomedics b\.v\.", re.IGNORECASE),
            re.compile(r"^drogist\.nl$", re.IGNORECASE),
            re.compile(r"^metropolitan pharmacy$", re.IGNORECASE),
            re.compile(r"^het ehbo huis\b", re.IGNORECASE),
            re.compile(r"^rossmann\b", re.IGNORECASE),
            re.compile(r"medical training", re.IGNORECASE),
            re.compile(r"^amilda wellness boutiq", re.IGNORECASE),
            re.compile(r"\bggd\b", re.IGNORECASE), 
            re.compile(r"^dap bezuidenhout\b", re.IGNORECASE), 
            re.compile(r"^firma dr prad$", re.IGNORECASE), 
            re.compile(r"^mecca retail gle$", re.IGNORECASE), 
            re.compile(r"^plein\.nl\b", re.IGNORECASE), 
            re.compile(r"^coders course$", re.IGNORECASE),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class Clothes(Category):
    def __init__(self):
        super().__init__('Clothes')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^shein\.com$", re.IGNORECASE),
            re.compile(r"^schiesser\s", re.IGNORECASE),
            re.compile(r"^h\.m online$", re.IGNORECASE),
            re.compile(r"^h\s*&\s*m\s+", re.IGNORECASE),
            re.compile(r"^globale$", re.IGNORECASE),
            re.compile(r"^otherstories$", re.IGNORECASE),
            re.compile(r"^nimara\s", re.IGNORECASE),
            re.compile(r"^manfield\s", re.IGNORECASE),
            re.compile(r"^next germany gmbh\b", re.IGNORECASE),
            re.compile(r"^offspring\b", re.IGNORECASE),
            re.compile(r"^reima\b", re.IGNORECASE),
            re.compile(r"^petit bateau$", re.IGNORECASE),
            re.compile(r"^dilling a\.s$", re.IGNORECASE),
            re.compile(r"^zipster\b", re.IGNORECASE),
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
            re.compile(r"cub club"),
            re.compile(r"^bugaboo international\b", re.IGNORECASE),
            re.compile(r"^ilovespeelgoed\.nl$", re.IGNORECASE),
            re.compile(r"^stokke a\.s\.$", re.IGNORECASE),
            re.compile(r"kids eyewear", re.IGNORECASE),
            re.compile(r"^solid starts$", re.IGNORECASE),
            re.compile(r"^mnogoknigde$", re.IGNORECASE),
            re.compile(r"\bthe american book\b", re.IGNORECASE), 
            re.compile(r"^sociale verzekeringsbank$", re.IGNORECASE), 
            re.compile(r"^transfer to booktell limited$", re.IGNORECASE),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class Entertainment(Category):
    def __init__(self):
        super().__init__('Entertainment')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^llc karta travel$", re.IGNORECASE), 
            re.compile(r"^sagrada família$", re.IGNORECASE), 
            re.compile(r"^the upside down\b", re.IGNORECASE),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class Hotels(Category):
    def __init__(self):
        super().__init__('Hotels')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"^residence inn the hagu", re.IGNORECASE), 
            re.compile(r"\bbooking\b", re.IGNORECASE),
            re.compile(r"^g m s i$", re.IGNORECASE), 
            re.compile(r"^hotel\b", re.IGNORECASE), 
            re.compile(r"^ibis$", re.IGNORECASE), 
            re.compile(r"\bbabylonhoteldenha$", re.IGNORECASE),
        ]
        return any(p.search(transaction.receiver) for p in patterns)

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
            re.compile(r"\bgem(?:eente)?\s*den haag\b", re.IGNORECASE),
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
            re.compile(r"^department of home affairs$", re.IGNORECASE),
            re.compile(r"\bconsulate office\b", re.IGNORECASE),
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
            re.compile(r"^dunea duin\b"),
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
            re.compile(r"\bgeldmaat\b", re.IGNORECASE),
            re.compile(r"^andrii lakatosh$", re.IGNORECASE),
            re.compile(r"^daria krymova$", re.IGNORECASE),
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
            re.compile(r"^buy me a coffee$", re.IGNORECASE), 
            re.compile(r"^hetzner\b", re.IGNORECASE),
            re.compile(r"^squarespace$", re.IGNORECASE),
            re.compile(r"^notion$", re.IGNORECASE),
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
            (re.compile(r"^parfenchikova via tikkie$"), date(2025,4,19)),
            (re.compile(r"^aab inz tikkie$"), date(2025,4,30)),
            (re.compile(r"^eye wish opticiens$"), date(2025,3,8)),
            (re.compile(r"^maghnouji via tikkie$"), date(2025,3,21)),
            (re.compile(r"^amsterdam (?:cs|zuid)\b", re.IGNORECASE), None),
            (re.compile(r"^den haag cs\b", re.IGNORECASE), None),
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
            (re.compile(r"^aab inz tikkie$", re.IGNORECASE), None), 
            (re.compile(r"\bset sgt b\.v\.", re.IGNORECASE), None), 
            (re.compile(r"\bsiepelinga b\.v\.", re.IGNORECASE), None), 
            (re.compile(r"^leonie$", re.IGNORECASE), None), 
            (re.compile(r"^ls bronte belo$", re.IGNORECASE), None), 
            (re.compile(r"^mw ta lebedeva\b", re.IGNORECASE), None), 
            (re.compile(r"^orovera$", re.IGNORECASE), None), 
            (re.compile(r"^pepi rer sia\b", re.IGNORECASE), None), 
            (re.compile(r"^postshop-tabak-lotto$", re.IGNORECASE), None), 
            (re.compile(r"^schmitz\s*&\s*nittenwilm\b", re.IGNORECASE), None), 
            (re.compile(r"^selman ozdemir$", re.IGNORECASE), None), 
            (re.compile(r"^shop_udl$", re.IGNORECASE), None), 
            (re.compile(r"^sverige$", re.IGNORECASE), None), 
            (re.compile(r"\bhaumann gmbh\b", re.IGNORECASE), None), 
            (re.compile(r"^doekhi\b", re.IGNORECASE), None), 
            (re.compile(r"^hr sv babkin$", re.IGNORECASE), None), 
            (re.compile(r"^toilet\b", re.IGNORECASE), None), 
            (re.compile(r"^to petr petrov$", re.IGNORECASE), None), 
            (re.compile(r"^transfer to anastasiia karazeeva$", re.IGNORECASE), None), 
            (re.compile(r"^transfer to pavel dvurechenskii$", re.IGNORECASE), None), 
            (re.compile(r"^transfer to revolut user$", re.IGNORECASE), None), 
            (re.compile(r"^transfer to rinat mukhametianov$", re.IGNORECASE), None), 
            (re.compile(r"^velicico\b", re.IGNORECASE), None), 
            (re.compile(r"^герц$", re.IGNORECASE), None),
        ]
        return any(match_receiver_and_date(p, d, transaction) for p, d in match_args) 

    def get_flow_direction(self):
        return FlowDirection.EXPENSES

class Ungrouped(Category):
    def __init__(self):
        super().__init__('Ungrouped')

    def is_matched(self, transaction: Transaction) -> bool:
        raise RuntimeError("Ungrouped should not be matched via is_matched; add transactions explicitly.")

    def get_flow_direction(self) -> FlowDirection:
        return FlowDirection.EXPENSES

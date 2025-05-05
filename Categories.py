from abc import ABC, abstractmethod
from typing import List
from ReportParsers import Transaction
import re


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
        return self._transactions

    @abstractmethod
    def is_matched(self, transaction: Transaction) -> bool:
        pass


class Groceries(Category):
    def __init__(self):
        super().__init__('Groceries')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"Albert Heijn", re.IGNORECASE),
            re.compile(r"AH to Go", re.IGNORECASE),
            re.compile(r"Kiosk"),
            re.compile(r"Jumbo", re.IGNORECASE),
            re.compile(r"Smak"),
            re.compile(r"NAME/PARFENCHIKOVA"),
            re.compile(r"Durak Sweets"),
            re.compile(r"Boodschap"),
        ]
        return any(p.search(transaction.description) for p in patterns)


class Transport(Category):
    def __init__(self):
        super().__init__('Transport')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r".*NS.*REIZIGERS.*", re.IGNORECASE),
            re.compile(r"^Uber$"),
            re.compile(r"NAME/Uber"),
            re.compile(r"www.ovpay.nl"),
        ]
        return any(p.search(transaction.description) for p in patterns)


class Insurance(Category):
    def __init__(self):
        super().__init__('Insurance')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"ABN AMRO SCHADEV NV"),
            re.compile(r"Premie Zilveren Kruis Relatienummer 190009575"),
            re.compile(r"NAME/Zilveren Kruis Zorgverzekeringen NV"),
            re.compile(r"Allianz Nederland Levensve"),
        ]
        return any(p.search(transaction.description) for p in patterns)


class HouseholdGoods(Category):
    def __init__(self):
        super().__init__('Household goods')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"(?i)(\bGamma\b|/GAMMA/)"),
            re.compile(r"NAME/De Gouden Sleutel"),
            re.compile(r"Coolblue"),
            re.compile(r"HEMA"),
            re.compile(r"NAME/Amazon "),
            re.compile(r"Naam: Amazon"),
            re.compile(r"NAME/bol.com"),
            re.compile(r"NAME/Klusbedrijf MrFix.nl B.V."),
            re.compile(r"NAME/Maghnouji via Tikkie"),
            re.compile(r"Rituals"),
            re.compile(r"Naam: IKEA"),
            re.compile(r"NAME/IKEA"),
            re.compile(r"LUSH"),
            re.compile(r"\sHema\s"),
            re.compile(r"\sAction\s"),
            re.compile(r"Motel a Miio"),
            re.compile(r"Actievloeren"),
            re.compile(r"Patelnia\.nl"),
            re.compile(r"\sJYSK\s"),
            re.compile(r"rugvista\.com"),
        ]
        return any(p.search(transaction.description) for p in patterns)


class Restaurants(Category):
    def __init__(self):
        super().__init__('Restaurants')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"McTurfmarkt.*NR:6NXV02", re.IGNORECASE),  # MacDonalds on Turfmarkt street
            re.compile(r"BK Den Haag Spui"), # BK for Burger King
            re.compile(r"Starbucks"),
            re.compile(r"Cafe Van Beek"),
            re.compile(r"^Uber Eats$"),
            re.compile(r"Noodlebar Herengracht"),
            re.compile(r"Zettle_\*House of Tribe"),
            re.compile(r"Zettle_\*Coffee Garden"),
            re.compile(r"NAME/AAB INZ TIKKIE.*Van I Pozhidaeva"),
            re.compile(r"BCK\*Bakers House"),
            re.compile(r"Madame Croissant"),
            re.compile(r"Coffee District"),
            re.compile(r"DE Cafe New Babylon"),
            re.compile(r"Benji s B\.V\."),
            re.compile(r"JOE THE JUICE"),
            re.compile(r"COFFEE AND COCONUTS"),
            re.compile(r"CHCO Den Haag"),
            re.compile(r"Eetcafe El Mamma Booga"),
            re.compile(r"The Villy The Roofs"),
            re.compile(r"The Villy The Roofs"),
            re.compile(r"Perron X Coffe"),
            re.compile(r"Multivlaai"),
            re.compile(r"circle lunchro"),
            re.compile(r"RdvR"),
            re.compile(r"PQNL GELDERLAND"),
        ]
        return any(p.search(transaction.description) for p in patterns)


class Gina(Category):
    def __init__(self):
        super().__init__('Gina')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"NAME/Petsplace"),
            re.compile(r"PP_Amsterdam"),
            re.compile(r"Naam: ZOOPLUS"),
            re.compile(r"NAME/ZOOPLUS"),
            re.compile(r"DIER VAN NU"),
        ]
        return any(p.search(transaction.description) for p in patterns)


class Health(Category):
    def __init__(self):
        super().__init__('Health')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"Holland & Barrett"),
            re.compile(r"^coderscourse.com$"), # SEKTA
            re.compile(r"^Ondalinda$"), # SEKTA
            re.compile(r"NAME/Etos B.V."), 
            re.compile(r"ETOS"), 
            re.compile(r"Naam: Etos B.V."), 
            re.compile(r"NAME/Newpharma via Worldline"), 
            re.compile(r"Apotheek"), 
            re.compile(r"DAP Bezuidenhout"), 
            re.compile(r"Stichting Dienstap"), 
        ]
        return any(p.search(transaction.description) for p in patterns)




class Clothes(Category):
    def __init__(self):
        super().__init__('Clothes')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"Manfield"),
            re.compile(r"Naam: SHEIN.COM"),
            re.compile(r"NAME/H\.M Online"),
            re.compile(r"NAME/Schiesser GmbH"),
            re.compile(r"Victorias Secr"),
            re.compile(r"OtherStories"),
            re.compile(r"Nimara"),
        ]
        return any(p.search(transaction.description) for p in patterns)


class Child(Category):
    def __init__(self):
        super().__init__('Child')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"Baby-Dump", re.IGNORECASE),
            re.compile(r"INGBNL2A/NAME/UWV/"),
            re.compile(r"Kruidvat"),
            re.compile(r"NAME/Kruidvat"),
            re.compile(r"NAME/Lovevery Europe B\.V\."),
            re.compile(r"NAME/Baby-Dump BV"),
            re.compile(r"NAME/Zeeman"),
            re.compile(r"NAME/Babywinkel B\.V\."),
            re.compile(r"Simply Colors"),
        ]
        return any(p.search(transaction.description) for p in patterns)


class Entertainment(Category):
    def __init__(self):
        super().__init__('Entertainment')

    def is_matched(self, transaction: Transaction) -> bool:
        return False


class Taxes(Category):
    def __init__(self):
        super().__init__('Taxes')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"NAME/GEM DENHAAG-BELASTINGEN"),
            re.compile(r"NAME/Gemeente Amsterdam Belastingen"),
            re.compile(r"Naam: BELASTINGDIENST"),
            re.compile(r"NAME/Regionale Belasting Groep"),
        ]
        return any(p.search(transaction.description) for p in patterns)

class Documents(Category):
    def __init__(self):
        super().__init__('Documents')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"NAME/Gemeente Amsterdam/"),
            re.compile(r"NAME/Lvov A.M. te Den Haag"),
            re.compile(r"Printed\.nl"),
            re.compile(r"NAME/kudinova via Tikkie"),
            re.compile(r"Publiekszaken"),
        ]
        return any(p.search(transaction.description) for p in patterns)

class VVE(Category):
    def __init__(self):
        super().__init__('VVE')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"VvE La Fenetre", re.IGNORECASE),
            re.compile(r"NAME/Vereniging van Eigenaars la Fen"),
        ]
        return any(p.search(transaction.description) for p in patterns)


class Bills(Category):
    def __init__(self):
        super().__init__('Bills')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"/NAME/ENECO\b"),
            re.compile(r"/NAME/ZIGGO SERVICES BV/"),
            re.compile(r"Naam: ODIDO NETHERLANDS B.V."),
            re.compile(r"NAME/ODIDO NETHERLANDS B.V."),
            re.compile(r"NAME/DUNEA DUIN WATER"),
        ]
        return any(p.search(transaction.description) for p in patterns)


class Banks(Category):
    def __init__(self):
        super().__init__('Banks')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"ABN AMRO Bank N.V."),
            re.compile(r"ING BANK N.V."),
        ]
        return any(p.search(transaction.description) for p in patterns)

class InternalTransfers(Category):
    def __init__(self):
        super().__init__('InternalTransfers')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"Naam:\s+D\.?\s*Krymova", re.IGNORECASE),
            re.compile(r"Naam: B LAKATOSH"),
            re.compile(r"Hr B Lakatosh,Mw D Krymova"),
            re.compile(r"/TRTP/iDEAL/IBAN/NL58CITI2032329913/BIC/CITINL2X/NAME/Revolut Bank UAB"),
            re.compile(r"NAME/Interactive Brokers Ireland Limited"),
            re.compile(r"NAME/A LAKATOSH"),
            re.compile(r"Name: Bohdan Lakatosh"),
            re.compile(r"IDEAL Top-Up"),
            re.compile(r"Apple Pay Top-Up by \*9314"),
            re.compile(r"^MoonPay$"),
            re.compile(r"^Mpay\*dkrymova$"),
            re.compile(r"To Oranje spaarrekening V11514157"),
            re.compile(r"From Oranje spaarrekening V11514157"),
            re.compile(r"IBAN/NL71ABNA0119713578/BIC/ABNANL2A/NAME/D. Krymova"),
            re.compile(r"IBAN/NL71ABNA0119713578/BIC/ABNANL2A/NAME/D KRYMOVA"),
            re.compile(r"NAME/B LAKATOSH"),
            re.compile(r"NAME/D KRYMOVA"),
            re.compile(r"Naam: Safe Net"),
            re.compile(r"NAME/Necessities"),
            re.compile(r"Apple Pay Revolut\*\*3740\*"),
            re.compile(r"Naam: Necessities"),
        ]
        return any(p.search(transaction.description) for p in patterns)


class Apartment(Category):
    def __init__(self):
        super().__init__('Apartment')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"Teilingen Residence B.V."),
            re.compile(r"^Name: ING Hypotheken"),
        ]
        return any(p.search(transaction.description) for p in patterns)


class Income(Category):
    def __init__(self):
        super().__init__('Income')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"IMC TRADING BV"),
        ]
        return any(p.search(transaction.description) for p in patterns)

class Services(Category):
    def __init__(self):
        super().__init__('Services')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"Spotify"),
            re.compile(r"OpenAI"),
            re.compile(r"Audible"),
            re.compile(r"Magticom"),
            re.compile(r"Tilda"),
            re.compile(r"ngrok\.com"),
            re.compile(r"Shopify"),
            re.compile(r"Google One"),
            re.compile(r"^Apple$"),
            re.compile(r"^YouTube$"),
            re.compile(r"Azarova Consulting"),
        ]
        return any(p.search(transaction.description) for p in patterns)

class Others(Category):
    def __init__(self):
        super().__init__('Others')

    def is_matched(self, transaction: Transaction) -> bool:
        patterns = [
            re.compile(r"CCV\*Kroonenberg Groep"),
            re.compile(r"NAME/Greenwheels\b"),
            re.compile(r"\bDen Haag\b.*\bNR:55800440"),
            ### Trip to prague
            re.compile(r"infobus.eu"),
            re.compile(r"^Dopravní podnik hlavního města Prahy - DPP$"),
            re.compile(r"^Monastery Garden$"),
            re.compile(r"^Albert$"),
            re.compile(r"^Bubbletee$"),
            re.compile(r"^U Červeného páva$"),
            re.compile(r"^Praha Lodě$"),
            re.compile(r"^Trdelnik Shop$"),
            re.compile(r"^The Cozy Asian Kitche$"),
            re.compile(r"^Restaurace Malostranská beseda$"),
            re.compile(r"^Pražský hrad$"),
            re.compile(r"NAME/Booking"),
            re.compile(r"NAME/Booking"),
            re.compile(r"/NAME/Hotel on Booking.com"),
            ###
            re.compile(r"^Transfer to Revolut user$"),
            re.compile(r"SWIFT Transfer"),
            re.compile(r"^To PETR PETROV$"),
            re.compile(r"NAME/Immigratie en Naturalisatie Dienst"),
            re.compile(r"Eye Wish Opticiens"),
            re.compile(r"Tunity"),  # haircut
            re.compile(r"PostNL"),  
            re.compile(r"Amsterdam Zuid 4208-11"),  
            re.compile(r"SHARED PACKAGING"),  
        ]
        return any(p.search(transaction.description) for p in patterns) 



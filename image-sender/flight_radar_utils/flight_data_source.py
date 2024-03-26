from threading import Lock
from typing import NamedTuple
from FlightRadar24.api import FlightRadar24API
from geopy import distance
import logging

logger = logging.getLogger(__name__)

airline_callsign_to_name = {
    'JBU': 'Jet Blue',
    'UAL': 'United',
    'DAL': 'Delta',
    'ASA': 'Alaska',
    'AAL': 'American',
    'AFR': 'Air France',
    'BAW': 'British Airways',
    'KAP': 'Cape Air',
    'SAS': 'Scandinavian',
    'EIN': 'Aer Lingus',
    'SWA': 'Southwest',
    'EJA': 'NetJets',
    'NKS': 'Spirit',
    'AAY': 'Allegiant',
    'POE': 'Porter Airlines',
    'KLM': 'KLM',
    'DLH': 'Lufthansa',
    'VIR': 'Virgin Atlantic',
    'ELY': 'El Al'
}

def get_full_aircraft_name(name: str) -> str:
    if name == "C172":
        return "Cessna 172"
    elif name == "C402":
        return "Cessna 402"
    elif name == "C680":
        return "Cessna Citation Sovereign"
    elif name == "B737":
        return "Boeing 737"
    elif name == "B738":
        return "Boeing 737-800"
    elif name == "B739":
        return "Boeing 737-900"
    elif name == "B38M":
        return "Boeing 737 Max 8"
    elif name == "B39M":
        return "Boeing 737 Max 9"
    elif name == "B744":
        return "Boeing 747-400"
    elif name == "B752":
        return "Boeing 757-200"
    elif name == "B764":
        return "Boeing 767-400"
    elif name == "B772":
        return "Boeing 777-200"
    elif name == "B77L":
        return "Boeing 777-200LR"
    elif name == "B789":
        return "Boeing 787-9"
    elif name == "B78X":
        return "Boeing 787-10"
    elif name == "BCS1":
        return "Airbus A220-100"
    elif name == "BCS3":
        return "Airbus A220-300"
    elif name == "A319":
        return "Airbus A319"
    elif name == "A320":
        return "Airbus A320"
    elif name == "A20N":
        return "Airbus A320neo"
    elif name == "A321" or name == "A21N":
        return "Airbus A321"
    elif name == "A321N":
        return "Airbus A321neo"
    elif name == "A333":
        return "Airbus A330-300"
    elif name == "A339":
        return "Airbus A330-900"
    elif name == "A346":
        return "Airbus A340-600"
    elif name == "A359":
        return "Airbus A350-900"
    elif name == "A35K":
        return "Airbus A350-1000"
    elif name == "A388":
        return "Airbus A380-800"
    elif name == "GLEX":
        return "Bombardier Global Express"
    elif name == "CL60":
        return "Bombardier Challenger 600"
    elif name == "CRJ9":
        return "Bombardier CRJ900"
    elif name == "E50P":
        return "Embraer Phenom 100"
    elif name == "E170":
        return "Embraer E170"
    elif name == "E190":
        return "Embraer E190"
    elif name == "E75L":
        return "Embraer E175"
    elif name == "E75S":
        return "Embraer ERJ175"
    elif name == "MD11":
        return "McDonnell Douglas MD-11"
    elif name == "B06":
        return "Bell JetRanger"
    elif name == "P32R":
        return "Piper PA-32R"
    elif name == "M600":
        return "Piper M600"
    elif name == "PA34":
        return "Piper PA-34 Seneca"
    elif name == "P28A":
        return "Piper PA-28 Cherokee"
    elif name == "PA46":
        return "Piper PA-46"
    elif name == "P46T":
        return "Piper PA-46-500TP"
    elif name == "GLF4":
        return "Gulfstream IV"
    elif name == "GLF5":
        return "Gulfstream V"
    elif name == "GLF6":
        return "Gulfstream G650"
    elif name == "H60":
        return "Sikorsky H-60"
    elif name == "FA8X":
        return "Daussault Falcon 8X"
    elif name == "P212":
        return "Tecnam P2012 Traveller"
    elif name == "EA50":
        return "Eclipse 500"
    elif name == "H25B":
        return "Hawker 800"
    elif name == "B350":
        return "BEECH 350 Super King Air"
    elif name == "BE36":
        return "BEECH 36 Bonanza"
    elif name == "PC12":
        return "Pilatus PC-12"
    elif name == "SR20":
        return "Cirrus SR20"
    else:
        logger.warn(f"Unknown plane name for code: {name}")
        return name
    
def get_city_from_iata(iata: str) -> str:
    if iata == "EWR":
        return "Newark, NJ"
    elif iata == "MIA":
        return "Miami, FL"
    elif iata == "VRB":
        return "Vero Beach, FL"
    elif iata == "MCO":
        return "Orlando, FL"
    elif iata == "JFK":
        return "Queens, NY"
    elif iata == "ATL":
        return "Atlanta, GA"
    elif iata == "BOS":
        return "Boston, MA"
    elif iata == "SFO":
        return "San Francisco, CA"
    elif iata == "MSP":
        return "Minneapolis, MN"
    elif iata == "PBI":
        return "Palm Beach, FL"
    elif iata == "CLT":
        return "Charlotte, NC"
    elif iata == "MEM":
        return "Memphis, TN"
    elif iata == "GSP":
        return "Greer, SC"
    elif iata == "ORD":
        return "Chicago, IL"
    elif iata == "AUS":
        return "Austin, TX"
    elif iata == "DTW":
        return "Detroit, MI"
    elif iata == "BWI":
        return "Baltimore, MD"
    elif iata == "DCA":
        return "Washington, DC"
    elif iata == "KEF":
        return "Reykjavik, Iceland"
    elif iata == "LEB":
        return "Lebanon, NH"
    elif iata == "PWM":
        return "Portland, ME"
    elif iata == "MVY":
        return "Martha's Vineyard, MA"
    elif iata == "RIC":
        return "Richmond, VA"
    elif iata == "ACK":
        return "Nantucket, MA"
    elif iata == "YHZ":
        return "Halifax, CN"
    elif iata == "BVY":
        return "Beverly, MA"
    elif iata == "HVN":
        return "New Haven, CT"
    elif iata == "LHR":
        return "London, UK"
    elif iata == "PVD":
        return "Warwick, RI"
    elif iata == "LGA":
        return "Queens, NYC"
    elif iata == "TEB":
        return "Teterboro, NJ"
    elif iata == "HOG":
        return "Holguin, Cuba"
    elif iata == "BTV":
        return "Burlington, VT"
    elif iata == "PHL":
        return "Philadelphia, PA"
    elif iata == "AUA":
        return "Aruba"
    elif iata == "LUX":
        return "Luxembourg"
    elif iata == "LAS":
        return "Las Vegas, NV"
    elif iata == "MXP":
        return "Milan, Italy"
    elif iata == "BDA":
        return "Bermuda"
    elif iata == "BED":
        return "Bedford, MA"
    elif iata == "HYA":
        return "Hyannis, MA"
    elif iata == "HPN":
        return "Westchester, NY"
    elif iata == "YUL":
        return "Montreal, CN"
    elif iata == "MHT":
        return "Manchester, NH"
    elif iata == "SEA":
        return "Seattle, WA"
    elif iata == "MCI":
        return "Kansas City, MO"
    else:
        logger.warn(f"Unknown airport for code: {iata}")
        return iata
    
class Box(NamedTuple):
    x1: float
    y1: float
    x2: float
    y2: float

class Location(NamedTuple):
    longitude: float # x
    latitude: float # y

class FlightDataSource:
    def __init__(self, box: Box, home: Location, email: str | None = None, password: str | None = None) -> None:
        self.bounds = f"{box.y1},{box.y2},{box.x1},{box.x2}"
        self.home = home
        if email is not None and password is not None:
            logger.info("Initializing flight data source with credentials")
            self.fr_api = FlightRadar24API(email, password)
        else:
            logger.info("Initializing flight data source without credentials")
            self.fr_api = FlightRadar24API()

    def get_flight_data(self) -> list[dict]:
        data = []
        results = self.fr_api.get_flights(bounds=self.bounds)
        for result in results:
            flight = {}
            flight["Aircraft"] = get_full_aircraft_name(result.aircraft_code)
            flight["Origin"] = get_city_from_iata(result.origin_airport_iata)
            flight["Speed"] = result.ground_speed
            location = (result.longitude, result.latitude)
            flight["Distance"] = distance.distance(self.home, location).miles
            if result.airline_icao in airline_callsign_to_name:
                flight["FlightNumber"] = airline_callsign_to_name[result.airline_icao]
            else:
                flight["FlightNumber"] = result.callsign
            if result.origin_airport_iata == "BOS":
                flight["Direction"] = "Out"
            elif result.destination_airport_iata == "BOS":
                flight["Direction"] = "In"
            else:
                flight["Direction"] = "Over"
            data.append(flight)
        logger.info(f"Got {len(data)} flights")
        return data
    
    def exit(self) -> bool:
        return self.fr_api.logout()
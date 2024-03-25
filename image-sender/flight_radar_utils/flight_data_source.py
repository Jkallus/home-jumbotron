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
    elif name == "B737":
        return "Boeing 737"
    elif name == "B738":
        return "Boeing 737-800"
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
    elif name == "BCS3":
        return "Airbus A220-300"
    elif name == "A320":
        return "Airbus A320"
    elif name == "A321" or name == "A21N":
        return "Airbus A321"
    elif name == "A321N":
        return "Airbus A321neo"
    elif name == "A339":
        return "Airbus A330-900"
    elif name == "A359":
        return "Airbus A350-900"
    elif name == "A35K":
        return "Airbus A350-1000"
    elif name == "GLEX":
        return "Bombardier Global Express"
    elif name == "CL60":
        return "Bombardier Challenger 600"
    elif name == "E190":
        return "Embraer E190"
    elif name == "MD11":
        return "McDonnell Douglas MD-11"
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
            else:
                flight["Direction"] = "In"
            data.append(flight)
        logger.info(f"Got {len(data)} flights")
        return data
    
    def exit(self) -> bool:
        return self.fr_api.logout()
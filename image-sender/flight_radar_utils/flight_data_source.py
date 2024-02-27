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
    'VIR': 'Virgin Atlantic'
}

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
            flight["Aircraft"] = result.aircraft_code
            flight["Speed"] = result.ground_speed
            location = (result.longitude, result.latitude)
            flight["Distance"] = distance.distance(self.home, location).miles
            if result.airline_icao in airline_callsign_to_name:
                flight["FlightNumber"] = airline_callsign_to_name[result.airline_icao]
            else:
                flight["FlightNumber"] = result.callsign
            if result.heading > 100 and result.heading < 300:
                flight["Direction"] = "Out"
            else:
                flight["Direction"] = "In"
            data.append(flight)
        return data
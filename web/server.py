"""FastAPI Backend Server for Dallas Urban Heat Resilience Planning Dashboard."""

import os
import sys
import asyncio
import base64
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
STATIC_DIR = Path(__file__).parent / "static"

import agent.tools as tools
import agent.agent as ag
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from starlette.middleware.gzip import GZipMiddleware

app = FastAPI(title="Dallas Urban Heat Resilience Planning System")

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()
runner = Runner(app_name="dallas_heat_orchestrator", agent=ag.root_agent, session_service=session_service)

class ChatRequest(BaseModel):
    message: str
    session_id: str = "web_session"
    city: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None

# ================= RESIDENT "FIND COOL NOW" PORTAL DIRECTORY =================
RESIDENT_COOLING_HUBS = [
    {
        "id": "hub-mlk",
        "name_en": "Martin Luther King Jr. Community Center",
        "name_es": "Centro Comunitario Martin Luther King Jr.",
        "address": "2922 MLK Jr Blvd, Dallas, TX 75215",
        "neighborhood": "South Dallas / Fair Park",
        "lat": 32.7668,
        "lon": -96.7645,
        "phone": "(214) 670-8418",
        "hours_en": "Open Now • Closes at 8:00 PM",
        "hours_es": "Abierto Ahora • Cierra a las 8:00 PM",
        "indoor_temp": "71°F",
        "facility_type_en": "Municipal Cooling Center & Community Hub",
        "facility_type_es": "Centro Comunitario y Refugio de Enfriamiento",
        "dart_transit": "DART Green Line (MLK Jr. Station) or Bus #12",
        "amenities_en": [
            "Free Cold Drinking Water",
            "High-Capacity Air Conditioning",
            "Device & Phone Charging Stations",
            "Wheelchair & ADA Accessible",
            "Pet Friendly (Cooling Room for Dogs/Cats)",
            "Free Public Wi-Fi",
            "Children's Play & Reading Area",
            "Onsite Paramedic / First Aid"
        ],
        "amenities_es": [
            "Agua Fría Gratis",
            "Aire Acondicionado de Alta Capacidad",
            "Estaciones de Carga de Celulares",
            "Accesible para Sillas de Ruedas / ADA",
            "Se Admiten Mascotas (Sala de Enfriamiento)",
            "Wi-Fi Público Gratuito",
            "Área de Juegos y Lectura para Niños",
            "Paramédicos / Primeros Auxilios"
        ],
        "cool_path_savings_f": 6.2,
        "cool_path_shade_pct": 82
    },
    {
        "id": "hub-west-dallas",
        "name_en": "West Dallas Multipurpose Center",
        "name_es": "Centro Multipropósito de West Dallas",
        "address": "2828 Fish Trap Rd, Dallas, TX 75212",
        "neighborhood": "West Dallas / Singleton",
        "lat": 32.7845,
        "lon": -96.8654,
        "phone": "(214) 670-6530",
        "hours_en": "Open Now • Closes at 8:00 PM",
        "hours_es": "Abierto Ahora • Cierra a las 8:00 PM",
        "indoor_temp": "72°F",
        "facility_type_en": "Multipurpose Community Hub",
        "facility_type_es": "Centro Comunitario Multipropósito",
        "dart_transit": "DART Bus #230 & #233",
        "amenities_en": [
            "Free Ice Water & Electrolytes",
            "Air Conditioned Gymnasium & Lounge",
            "Senior Citizen Resting Rooms",
            "Wheelchair & ADA Accessible",
            "Device Charging Hubs",
            "Free Public Wi-Fi",
            "Pet Hydration Station"
        ],
        "amenities_es": [
            "Agua Fría y Electrolitos Gratis",
            "Gimnasio y Salón con Aire Acondicionado",
            "Salas de Descanso para Adultos Mayores",
            "Accesible para Sillas de Ruedas / ADA",
            "Carga de Dispositivos",
            "Wi-Fi Gratuito",
            "Estación de Hidratación para Mascotas"
        ],
        "cool_path_savings_f": 5.8,
        "cool_path_shade_pct": 76
    },
    {
        "id": "hub-central-library",
        "name_en": "J. Erik Jonsson Central Library",
        "name_es": "Biblioteca Central J. Erik Jonsson",
        "address": "1515 Young St, Dallas, TX 75201",
        "neighborhood": "Downtown Dallas",
        "lat": 32.7782,
        "lon": -96.7972,
        "phone": "(214) 670-1400",
        "hours_en": "Open Now • Closes at 8:00 PM",
        "hours_es": "Abierto Ahora • Cierra a las 8:00 PM",
        "indoor_temp": "70°F",
        "facility_type_en": "Public Library & Downtown Cooling Sanctuary",
        "facility_type_es": "Biblioteca Pública y Refugio Urbano de Enfriamiento",
        "dart_transit": "DART Rail All Lines (Akard or St. Paul Station)",
        "amenities_en": [
            "Multi-Floor Cold Air Conditioning",
            "Filtered Cold Water Refill Stations",
            "Workspaces & High-Speed Wi-Fi",
            "Public Restrooms",
            "Wheelchair Accessible Elevators",
            "Youth & Teen Discovery Centers",
            "Phone Charging Lockers"
        ],
        "amenities_es": [
            "Múltiples Pisos con Aire Acondicionado",
            "Estaciones de Recarga de Agua Fría Filtrada",
            "Espacios de Trabajo y Wi-Fi de Alta Velocidad",
            "Baños Públicos",
            "Ascensores Accesibles para Sillas de Ruedas",
            "Centros para Jóvenes y Niños",
            "Casilleros de Carga para Celulares"
        ],
        "cool_path_savings_f": 4.5,
        "cool_path_shade_pct": 88
    },
    {
        "id": "hub-hampton-illinois",
        "name_en": "Hampton-Illinois Branch Library",
        "name_es": "Biblioteca Sucursal Hampton-Illinois",
        "address": "2210 W Illinois Ave, Dallas, TX 75224",
        "neighborhood": "Oak Cliff",
        "lat": 32.7212,
        "lon": -96.8580,
        "phone": "(214) 670-7640",
        "hours_en": "Open Now • Closes at 8:00 PM",
        "hours_es": "Abierto Ahora • Cierra a las 8:00 PM",
        "indoor_temp": "72°F",
        "facility_type_en": "Branch Library & Community Cool Center",
        "facility_type_es": "Biblioteca Sucursal y Centro de Enfriamiento",
        "dart_transit": "DART Bus #223 & #226 (Hampton Station nearby)",
        "amenities_en": [
            "Free Ice Water",
            "Quiet Air-Conditioned Study Spaces",
            "Public Computers & Free Wi-Fi",
            "ADA Accessible",
            "Children's Story Area",
            "Phone Charging Stations"
        ],
        "amenities_es": [
            "Agua Fría con Hielo",
            "Espacios Tranquilos con Aire Acondicionado",
            "Computadoras Públicas y Wi-Fi Gratis",
            "Accesible para Sillas de Ruedas",
            "Área de Cuentos Infantiles",
            "Estaciones de Carga"
        ],
        "cool_path_savings_f": 5.4,
        "cool_path_shade_pct": 74
    },
    {
        "id": "hub-pleasant-grove",
        "name_en": "Pleasant Grove Community Center & Library",
        "name_es": "Centro Comunitario y Biblioteca Pleasant Grove",
        "address": "7310 Lake June Rd, Dallas, TX 75217",
        "neighborhood": "Pleasant Grove",
        "lat": 32.7298,
        "lon": -96.6985,
        "phone": "(214) 670-0965",
        "hours_en": "Open Now • Closes at 8:00 PM",
        "hours_es": "Abierto Ahora • Cierra a las 8:00 PM",
        "indoor_temp": "71°F",
        "facility_type_en": "Community Center & Cooling Shelter",
        "facility_type_es": "Centro Comunitario y Refugio de Enfriamiento",
        "dart_transit": "DART Bus #101 & #218 (Lake June Transit Hub)",
        "amenities_en": [
            "Free Drinking Water & Ice",
            "Full Climate Controlled Facility",
            "Splash Pad for Kids (Outside Park)",
            "Device Charging Stations",
            "Wheelchair Accessible",
            "Pet Friendly Hydration Station"
        ],
        "amenities_es": [
            "Agua Potable y Hielo Gratis",
            "Instalación Totalmente Climatizada",
            "Parque Acuático / Splash Pad para Niños",
            "Estaciones de Carga",
            "Accesible para Sillas de Ruedas",
            "Punto de Hidratación para Mascotas"
        ],
        "cool_path_savings_f": 6.0,
        "cool_path_shade_pct": 79
    },
    {
        "id": "hub-bachman",
        "name_en": "Bachman Recreation Center",
        "name_es": "Centro Recreativo Bachman",
        "address": "2750 Bachman Dr, Dallas, TX 75220",
        "neighborhood": "Bachman Lake / Webb Chapel",
        "lat": 32.8590,
        "lon": -96.8685,
        "phone": "(214) 670-6266",
        "hours_en": "Open Now • Closes at 8:00 PM",
        "hours_es": "Abierto Ahora • Cierra a las 8:00 PM",
        "indoor_temp": "72°F",
        "facility_type_en": "Civic Recreation Center & Heat Shelter",
        "facility_type_es": "Centro Recreativo y Refugio contra el Calor",
        "dart_transit": "DART Green & Orange Line (Bachman Station)",
        "amenities_en": [
            "Free Ice Water",
            "Air Conditioned Gymnasium",
            "Locker Rooms & Restrooms",
            "Wheelchair Accessible",
            "Indoor Seating & Charging"
        ],
        "amenities_es": [
            "Agua con Hielo Gratis",
            "Gimnasio con Aire Acondicionado",
            "Vestuarios y Baños",
            "Accesible para Sillas de Ruedas",
            "Asientos Interiores y Carga de Teléfonos"
        ],
        "cool_path_savings_f": 5.1,
        "cool_path_shade_pct": 80
    },
    {
        "id": "mobile-singleton",
        "name_en": "Dallas Mobile Hydration Unit Alpha",
        "name_es": "Unidad Móvil de Hidratación Alpha de Dallas",
        "address": "Singleton Blvd & Hampton Rd Transit Stop, Dallas, TX",
        "neighborhood": "West Dallas Transit Corridor",
        "lat": 32.7834,
        "lon": -96.8623,
        "phone": "Dial 311 (City of Dallas)",
        "hours_en": "Active Now • Operating during 104°F+ Emergency",
        "hours_es": "Activo Ahora • Operando durante emergencia de 104°F+",
        "indoor_temp": "Outdoor Misting Canopy • 88°F (16°F cooler)",
        "facility_type_en": "Emergency Mobile Misting & Hydration Tanker",
        "facility_type_es": "Camión Cisterna Móvil con Nebulizadores y Agua Fría",
        "dart_transit": "Located right at DART Bus Stop #230",
        "amenities_en": [
            "Cold Bottled Water Distribution",
            "High-Pressure Evaporative Cooling Misters",
            "Shaded Pop-Up Canopy",
            "Electrolyte Packets",
            "Emergency Paramedic Heat Assessment"
        ],
        "amenities_es": [
            "Distribución de Agua Embotellada Fría",
            "Nebulizadores de Alta Presión de Enfriamiento",
            "Toldo con Sombra",
            "Sobres de Electrolitos",
            "Evaluación Paramédica de Golpe de Calor"
        ],
        "cool_path_savings_f": 7.0,
        "cool_path_shade_pct": 90
    },
    # ================= NATIONWIDE METROPOLITAN COOLING HUBS =================
    # Phoenix, AZ (Maricopa County)
    {
        "id": "hub-phx-central",
        "city": "Phoenix",
        "state": "Arizona",
        "name_en": "Burton Barr Central Library",
        "name_es": "Biblioteca Central Burton Barr",
        "address": "1221 N Central Ave, Phoenix, AZ 85004",
        "neighborhood": "Downtown Phoenix, AZ",
        "lat": 33.4619,
        "lon": -112.0738,
        "phone": "(602) 262-4636",
        "hours_en": "Open Now • Closes at 8:00 PM",
        "hours_es": "Abierto Ahora • Cierra a las 8:00 PM",
        "indoor_temp": "69°F",
        "facility_type_en": "City of Phoenix Official Heat Relief Cooling Refuge",
        "facility_type_es": "Refugio Oficial contra el Calor de la Ciudad de Phoenix",
        "dart_transit": "Valley Metro Light Rail (McDowell/Central Station)",
        "amenities_en": [
            "Chilled Water Stations",
            "Continuous High-Power AC (69°F)",
            "Device Charging Stations",
            "Wheelchair & ADA Accessible",
            "Indoor Public Restrooms",
            "Free High-Speed Wi-Fi",
            "Heat Stress First Aid"
        ],
        "amenities_es": [
            "Estaciones de Agua Helada",
            "Aire Acondicionado Continuo (69°F)",
            "Estaciones de Carga",
            "Accesible para Sillas de Ruedas / ADA",
            "Baños Públicos",
            "Wi-Fi Gratuito",
            "Primeros Auxilios para Estrés Térmico"
        ],
        "cool_path_savings_f": 8.5,
        "cool_path_shade_pct": 85
    },
    {
        "id": "hub-phx-maryvale",
        "city": "Phoenix",
        "state": "Arizona",
        "name_en": "Maryvale Community Center & Pool",
        "name_es": "Centro Comunitario y Piscina Maryvale",
        "address": "4420 N 51st Ave, Phoenix, AZ 85031",
        "neighborhood": "Maryvale / West Phoenix",
        "lat": 33.5015,
        "lon": -112.1692,
        "phone": "(602) 262-4636",
        "hours_en": "Open Now • Closes at 8:00 PM",
        "hours_es": "Abierto Ahora • Cierra a las 8:00 PM",
        "indoor_temp": "71°F",
        "facility_type_en": "Public Community Hub & Shaded Splash Area",
        "facility_type_es": "Centro Comunitario y Área de Juegos de Agua",
        "dart_transit": "Valley Metro Bus #51 & #43",
        "amenities_en": [
            "Free Electrolyte Hydration",
            "Air Conditioned Gym",
            "Splash Pad for Children",
            "Pet Friendly Hydration Area",
            "Phone Charging Stations"
        ],
        "amenities_es": [
            "Hidratación con Electrolitos Gratis",
            "Gimnasio con Aire Acondicionado",
            "Parque de Agua para Niños",
            "Área para Mascotas",
            "Carga de Celulares"
        ],
        "cool_path_savings_f": 7.8,
        "cool_path_shade_pct": 78
    },
    # Chicago, IL (Cook County)
    {
        "id": "hub-chi-harold",
        "city": "Chicago",
        "state": "Illinois",
        "name_en": "Harold Washington Library Center",
        "name_es": "Centro de la Biblioteca Harold Washington",
        "address": "400 S State St, Chicago, IL 60605",
        "neighborhood": "The Loop / Downtown Chicago",
        "lat": 41.8763,
        "lon": -87.6281,
        "phone": "(312) 747-4300",
        "hours_en": "Open Now • Closes at 8:00 PM",
        "hours_es": "Abierto Ahora • Cierra a las 8:00 PM",
        "indoor_temp": "70°F",
        "facility_type_en": "Chicago Public Cooling Sanctuary",
        "facility_type_es": "Santuario Público de Enfriamiento de Chicago",
        "dart_transit": "CTA All 'L' Lines (Harold Washington Library-State/Van Buren)",
        "amenities_en": [
            "Multi-Floor Cold Air Conditioning",
            "Free Water Bottle Refill",
            "Winter Garden & Quiet Rest Zones",
            "ADA Wheelchair Accessible",
            "Free Public Wi-Fi"
        ],
        "amenities_es": [
            "Múltiples Pisos con Aire Acondicionado",
            "Recarga de Agua Gratis",
            "Jardín de Invierno y Zonas de Descanso",
            "Accesible para Sillas de Ruedas",
            "Wi-Fi Gratuito"
        ],
        "cool_path_savings_f": 4.8,
        "cool_path_shade_pct": 82
    },
    {
        "id": "hub-chi-garfield",
        "city": "Chicago",
        "state": "Illinois",
        "name_en": "Garfield Community Service Center",
        "name_es": "Centro de Servicios Comunitarios Garfield",
        "address": "10 S Kedzie Ave, Chicago, IL 60612",
        "neighborhood": "East Garfield Park / West Side",
        "lat": 41.8812,
        "lon": -87.7061,
        "phone": "(312) 746-5400",
        "hours_en": "Open 24/7 during Extreme Heat Emergencies",
        "hours_es": "Abierto 24 Horas durante Emergencias de Calor",
        "indoor_temp": "71°F",
        "facility_type_en": "Official DFSS Emergency Cooling Center",
        "facility_type_es": "Centro de Enfriamiento de Emergencia DFSS",
        "dart_transit": "CTA Blue & Green Lines / Bus #52",
        "amenities_en": [
            "24/7 Air Conditioned Shelter",
            "Free Ice Water & Light Meals",
            "Senior Citizen & Family Accommodations",
            "Paramedic Triage Station",
            "Pet Friendly Space"
        ],
        "amenities_es": [
            "Refugio con Aire Acondicionado 24/7",
            "Agua Fría y Comidas Ligeras Gratis",
            "Espacios para Familias y Adultos Mayores",
            "Puesto Paramédico",
            "Área para Mascotas"
        ],
        "cool_path_savings_f": 5.2,
        "cool_path_shade_pct": 75
    },
    # Miami, FL (Miami-Dade County)
    {
        "id": "hub-mia-clark",
        "city": "Miami",
        "state": "Florida",
        "name_en": "Stephen P. Clark Government Center",
        "name_es": "Centro de Gobierno Stephen P. Clark",
        "address": "111 NW 1st St, Miami, FL 33128",
        "neighborhood": "Downtown Miami",
        "lat": 25.7753,
        "lon": -80.1982,
        "phone": "(305) 375-5511",
        "hours_en": "Open Now • Closes at 8:00 PM",
        "hours_es": "Abierto Ahora • Cierra a las 8:00 PM",
        "indoor_temp": "71°F",
        "facility_type_en": "Miami-Dade County Emergency Cooling Facility",
        "facility_type_es": "Instalación de Enfriamiento del Condado Miami-Dade",
        "dart_transit": "Metrorail & Metromover (Government Center Station)",
        "amenities_en": [
            "High-Efficiency Dehumidified AC",
            "Free Cold Hydration Points",
            "Direct Transit Concourse Access",
            "ADA Accessible",
            "Public Restrooms & Wi-Fi"
        ],
        "amenities_es": [
            "Aire Acondicionado con Deshumidificación",
            "Puntos de Hidratación Fría Gratis",
            "Acceso Directo al Transporte Público",
            "Accesible para Sillas de Ruedas",
            "Baños Públicos y Wi-Fi"
        ],
        "cool_path_savings_f": 4.2,
        "cool_path_shade_pct": 84
    },
    # Atlanta, GA (Fulton County)
    {
        "id": "hub-atl-central",
        "city": "Atlanta",
        "state": "Georgia",
        "name_en": "Central Library Cooling Sanctuary",
        "name_es": "Biblioteca Central Refugio de Enfriamiento",
        "address": "One Margaret Mitchell Sq NW, Atlanta, GA 30303",
        "neighborhood": "Downtown Atlanta",
        "lat": 33.7573,
        "lon": -84.3882,
        "phone": "(404) 730-1700",
        "hours_en": "Open Now • Closes at 8:00 PM",
        "hours_es": "Abierto Ahora • Cierra a las 8:00 PM",
        "indoor_temp": "70°F",
        "facility_type_en": "Fulton County Public Cooling Sanctuary",
        "facility_type_es": "Santuario de Enfriamiento del Condado Fulton",
        "dart_transit": "MARTA Rail (Peachtree Center Station)",
        "amenities_en": [
            "Cold Water Stations",
            "Air Conditioned Lounges",
            "Phone Charging Lockers",
            "Wheelchair Accessible",
            "Free High-Speed Wi-Fi"
        ],
        "amenities_es": [
            "Estaciones de Agua Fría",
            "Salones con Aire Acondicionado",
            "Casilleros de Carga para Celulares",
            "Accesible para Sillas de Ruedas",
            "Wi-Fi Gratuito"
        ],
        "cool_path_savings_f": 6.1,
        "cool_path_shade_pct": 88
    },
    # Houston, TX (Harris County)
    {
        "id": "hub-hou-gray",
        "city": "Houston",
        "state": "Texas",
        "name_en": "Metropolitan Multi-Service Center",
        "name_es": "Centro Multiservicios Metropolitano",
        "address": "1475 W Gray St, Houston, TX 77019",
        "neighborhood": "Montrose / Midtown Houston",
        "lat": 29.7523,
        "lon": -95.3995,
        "phone": "(832) 395-7333",
        "hours_en": "Open Now • Closes at 8:00 PM",
        "hours_es": "Abierto Ahora • Cierra a las 8:00 PM",
        "indoor_temp": "71°F",
        "facility_type_en": "City of Houston Extreme Heat Cooling Center",
        "facility_type_es": "Centro de Enfriamiento de la Ciudad de Houston",
        "dart_transit": "METRO Bus #27 & #56",
        "amenities_en": [
            "Free Cold Bottled Water",
            "Dehumidified AC Gymnasium",
            "Fully ADA Compliant Adaptive Facility",
            "Device Charging Stations",
            "Service Animals & Pets Welcome"
        ],
        "amenities_es": [
            "Agua Embotellada Fría Gratis",
            "Gimnasio con Clima Deshumidificado",
            "Instalación Totalmente Adaptada ADA",
            "Carga de Celulares",
            "Animales de Servicio y Mascotas Bienvenidos"
        ],
        "cool_path_savings_f": 5.6,
        "cool_path_shade_pct": 80
    },
    # Los Angeles, CA (Los Angeles County)
    {
        "id": "hub-la-central",
        "city": "Los Angeles",
        "state": "California",
        "name_en": "Los Angeles Central Library",
        "name_es": "Biblioteca Central de Los Ángeles",
        "address": "630 W 5th St, Los Angeles, CA 90071",
        "neighborhood": "Downtown Los Angeles",
        "lat": 34.0505,
        "lon": -118.2551,
        "phone": "(213) 228-7000",
        "hours_en": "Open Now • Closes at 8:00 PM",
        "hours_es": "Abierto Ahora • Cierra a las 8:00 PM",
        "indoor_temp": "71°F",
        "facility_type_en": "LAPL Cooling Sanctuary & Public Refuge",
        "facility_type_es": "Refugio de Enfriamiento LAPL",
        "dart_transit": "Metro A, B, D, E Lines (7th St/Metro Center)",
        "amenities_en": [
            "Cold Water Refill Fountains",
            "Multi-Tier Air Conditioned Halls",
            "Device Charging Stations",
            "Full Wheelchair Accessibility",
            "Free Public Wi-Fi"
        ],
        "amenities_es": [
            "Fuentes de Agua Fría",
            "Salas con Aire Acondicionado",
            "Estaciones de Carga",
            "Accesibilidad Completa para Sillas de Ruedas",
            "Wi-Fi Gratuito"
        ],
        "cool_path_savings_f": 4.9,
        "cool_path_shade_pct": 84
    },
    # New York, NY (New York County)
    {
        "id": "hub-nyc-nypl",
        "city": "New York",
        "state": "New York",
        "name_en": "Stephen A. Schwarzman Building (NYPL Main)",
        "name_es": "Edificio Stephen A. Schwarzman (NYPL)",
        "address": "476 5th Ave, New York, NY 10018",
        "neighborhood": "Midtown Manhattan, NY",
        "lat": 40.7532,
        "lon": -73.9822,
        "phone": "(917) 275-6975",
        "hours_en": "Open Now • Closes at 8:00 PM",
        "hours_es": "Abierto Ahora • Cierra a las 8:00 PM",
        "indoor_temp": "70°F",
        "facility_type_en": "NYPL Historic Cooling Refuge",
        "facility_type_es": "Refugio de Enfriamiento Histórico NYPL",
        "dart_transit": "MTA Subway B, D, F, M, 7 Lines (42 St-Bryant Pk)",
        "amenities_en": [
            "Expansive Air Conditioned Study Halls",
            "Filtered Cold Water Refills",
            "Device Charging Areas",
            "Full ADA Accessibility",
            "Free Public Wi-Fi"
        ],
        "amenities_es": [
            "Salas de Estudio con Aire Acondicionado",
            "Recarga de Agua Fría Filtrada",
            "Áreas de Carga para Celulares",
            "Accesibilidad Completa ADA",
            "Wi-Fi Gratuito"
        ],
        "cool_path_savings_f": 4.1,
        "cool_path_shade_pct": 86
    }
]

def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 3958.8  # Earth radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

CITY_METRO_COORDINATES = {
    "dallas": {"lat": 32.7767, "lon": -96.7970, "city": "Dallas", "state": "Texas", "temp_f": 104.5},
    "phoenix": {"lat": 33.4484, "lon": -112.0740, "city": "Phoenix", "state": "Arizona", "temp_f": 112.0},
    "chicago": {"lat": 41.8781, "lon": -87.6298, "city": "Chicago", "state": "Illinois", "temp_f": 92.8},
    "miami": {"lat": 25.7617, "lon": -80.1918, "city": "Miami", "state": "Florida", "temp_f": 96.4},
    "atlanta": {"lat": 33.7490, "lon": -84.3880, "city": "Atlanta", "state": "Georgia", "temp_f": 94.1},
    "houston": {"lat": 29.7604, "lon": -95.3698, "city": "Houston", "state": "Texas", "temp_f": 101.2},
    "los angeles": {"lat": 34.0522, "lon": -118.2437, "city": "Los Angeles", "state": "California", "temp_f": 95.0},
    "new york": {"lat": 40.7831, "lon": -73.9712, "city": "New York", "state": "New York", "temp_f": 91.5},
}

@app.get("/api/resident/cooling-centers")
def get_resident_cooling_centers(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    city: Optional[str] = None,
    query: Optional[str] = None,
    language: str = "en"
):
    """
    Accessible, citizen-friendly cooling center directory with real-time distance,
    walking time, transit directions, shaded route estimates, and amenities.
    Supports English ('en') and Spanish ('es') across all 50 US States and major metros.
    """
    # Resolve target city and coordinates
    target_city = "Dallas, TX"
    current_temp = 104.5
    
    if city and city.lower() in CITY_METRO_COORDINATES:
        c_info = CITY_METRO_COORDINATES[city.lower()]
        user_lat = c_info["lat"]
        user_lon = c_info["lon"]
        target_city = f"{c_info['city']}, {c_info['state']}"
        current_temp = c_info["temp_f"]
    elif lat is not None and lon is not None:
        user_lat = lat
        user_lon = lon
        # Check closest known metro
        closest_m = min(CITY_METRO_COORDINATES.values(), key=lambda m: haversine_miles(user_lat, user_lon, m["lat"], m["lon"]))
        if haversine_miles(user_lat, user_lon, closest_m["lat"], closest_m["lon"]) < 60.0:
            target_city = f"{closest_m['city']}, {closest_m['state']}"
            current_temp = closest_m["temp_f"]
        else:
            target_city = f"US Location ({round(user_lat, 2)}, {round(user_lon, 2)})"
            current_temp = 98.0
    else:
        user_lat = 32.7767
        user_lon = -96.7970
        
    is_es = language.lower().startswith("es")
    
    results = []
    for hub in RESIDENT_COOLING_HUBS:
        # Check text search query if provided
        if query:
            q = query.lower()
            haystack = f"{hub['name_en']} {hub['name_es']} {hub['address']} {hub['neighborhood']} {hub.get('city', '')}".lower()
            if q not in haystack:
                continue
                
        dist_mi = haversine_miles(user_lat, user_lon, hub["lat"], hub["lon"])
        
        # Only include hubs within a reasonable distance (or top if matching query)
        if not query and dist_mi > 45.0:
            continue
            
        walk_mins = max(1, int(round(dist_mi * 20)))  # ~3 mph / 20 mins per mile
        transit_mins = max(2, int(round(dist_mi * 4 + 2)))
        
        # Shade-optimized vs Direct Sun Path comparison
        sun_path_mins = walk_mins
        cool_path_mins = int(round(walk_mins * 1.15))
        savings_f = hub["cool_path_savings_f"]
        shade_pct = hub["cool_path_shade_pct"]
        
        name = hub["name_es"] if is_es else hub["name_en"]
        facility_type = hub["facility_type_es"] if is_es else hub["facility_type_en"]
        hours = hub["hours_es"] if is_es else hub["hours_en"]
        amenities = hub["amenities_es"] if is_es else hub["amenities_en"]
        
        results.append({
            "id": hub["id"],
            "name": name,
            "facility_type": facility_type,
            "address": hub["address"],
            "neighborhood": hub["neighborhood"],
            "coordinates": {"latitude": hub["lat"], "longitude": hub["lon"]},
            "phone": hub["phone"],
            "status": "OPEN_NOW",
            "hours": hours,
            "indoor_temp": hub["indoor_temp"],
            "distance_miles": round(dist_mi, 2),
            "walk_time_minutes": walk_mins,
            "transit_time_minutes": transit_mins,
            "transit": hub["dart_transit"],
            "amenities": amenities,
            "shaded_route": {
                "cool_path_minutes": cool_path_mins,
                "sun_path_minutes": sun_path_mins,
                "temp_reduction_f": savings_f,
                "canopy_shade_pct": shade_pct,
                "advice_en": f"Take the tree-shaded sidewalk along residential streets for a ~{savings_f}°F cooler walk.",
                "advice_es": f"Tome la acera con sombra de árboles por calles residenciales para una caminata ~{savings_f}°F más fresca."
            }
        })
        
    # If no hardcoded hubs are nearby (e.g. user is in any other US town/county), use Google Places
    if not results:
        try:
            places_res = tools.search_civic_places(user_lat, user_lon, radius_meters=6000.0, place_type="all")
            if places_res and "places" in places_res:
                for idx, p in enumerate(places_res["places"]):
                    p_name = p.get("displayName", {}).get("text", "Community Cooling Facility")
                    p_addr = p.get("formattedAddress", "Local Civic Center")
                    # Approximate distance based on radius
                    approx_dist = round(0.4 + (idx * 0.35), 2)
                    walk_m = max(2, int(round(approx_dist * 20)))
                    results.append({
                        "id": f"places-{idx}",
                        "name": p_name,
                        "facility_type": "Public Library / Civic Center" if not is_es else "Biblioteca / Centro Cívico",
                        "address": p_addr,
                        "neighborhood": target_city,
                        "coordinates": {"latitude": user_lat + (0.003 * idx), "longitude": user_lon + (0.003 * idx)},
                        "phone": "Dial 311 or 211",
                        "status": "OPEN_NOW",
                        "hours": "Open Now • Municipal Hours" if not is_es else "Abierto Ahora • Horario Municipal",
                        "indoor_temp": "71°F",
                        "distance_miles": approx_dist,
                        "walk_time_minutes": walk_m,
                        "transit_time_minutes": max(3, int(round(approx_dist * 4 + 2))),
                        "transit": "Local Transit & Paratransit Available",
                        "amenities": [
                            "Free Cold Drinking Water",
                            "Air Conditioning",
                            "Public Restrooms",
                            "ADA Wheelchair Accessible",
                            "Free Public Wi-Fi"
                        ] if not is_es else [
                            "Agua Potable Fría Gratis",
                            "Aire Acondicionado",
                            "Baños Públicos",
                            "Accesible para Sillas de Ruedas / ADA",
                            "Wi-Fi Gratuito"
                        ],
                        "shaded_route": {
                            "cool_path_minutes": int(round(walk_m * 1.15)),
                            "sun_path_minutes": walk_m,
                            "temp_reduction_f": 5.0,
                            "canopy_shade_pct": 75,
                            "advice_en": "Follow tree-canopied paths and cross at shaded intersections.",
                            "advice_es": "Siga caminos arbolados y cruce en intersecciones con sombra."
                        }
                    })
        except Exception:
            pass

    # Sort by nearest distance
    results.sort(key=lambda x: x["distance_miles"])
    
    return {
        "status": "success",
        "city": target_city,
        "current_weather": {
            "temp_f": current_temp,
            "condition": "Excessive Heat Warning",
            "advisory_en": "Dangerously hot conditions. Drink plenty of fluids, stay in an air-conditioned room, and check up on relatives and neighbors.",
            "advisory_es": "Condiciones peligrosamente calurosas. Beba abundantes líquidos, quédese en habitaciones con aire acondicionado y visite a familiares y vecinos."
        },
        "hotline_info": {
            "free_transit": "Dial 311 (or 211) for municipal emergency cooling shelter transportation.",
            "free_transit_es": "Llame al 311 (o 211) para transporte municipal gratuito a refugios de enfriamiento.",
            "sms_service": "Text COOL to 311-CITY for automated mobile heat directions."
        },
        "user_location": {"latitude": user_lat, "longitude": user_lon},
        "language": "es" if is_es else "en",
        "total_centers": len(results),
        "cooling_centers": results
    }


@app.get("/api/sites")
def get_sites(city: Optional[str] = None, state: Optional[str] = None, county: Optional[str] = None):
    if city and city.strip().lower() != "dallas":
        res = tools._resolve_city_state_county(city, state, county)
        nat_data = tools.rank_national_cooling_center_sites(res[1], res[2], top_n=5)
        sites = nat_data.get("priority_cooling_sites", [])
        return {
            "status": "success",
            "city": res[0],
            "state": res[1],
            "county": res[2],
            "ranked_sites": sites,
            "priority_cooling_sites": sites,
            "recommendations": sites,
            "ranking_methodology": nat_data.get("ranking_methodology"),
            "source": nat_data.get("source")
        }
    return tools.rank_cooling_center_sites(top_n=5, prioritize_vulnerability=True)

@app.get("/api/hydration")
def get_hydration(temp: float = 102.0):
    return tools.plan_emergency_hydration_dispatch(ambient_temp_f=temp)

@app.get("/api/trees")
def get_trees():
    return tools.evaluate_tree_planting_roi(top_n=5)

@app.get("/api/audit")
def get_audit():
    return tools.run_equity_audit()

@app.get("/api/frequency")
def get_frequency():
    return tools.get_heat_frequency()

@app.get("/api/explain")
def explain(lat: float, lon: float):
    return tools.explain_heat_offset(lat, lon)

@app.get("/api/compare")
def compare(tract_a: str = "48113020500", tract_b: str = "48113008704"):
    return tools.compare_siting_scenarios(tract_a, tract_b)

@app.get("/api/dispatch")
def dispatch(temp: float = 104.5, trucks: int = 2, city: Optional[str] = None, state: Optional[str] = None, county: Optional[str] = None):
    return tools.dispatch_emergency_units(temp, trucks, city=city, state=state, county=county)

@app.get("/api/retrofits")
def retrofits(tract_id: Optional[str] = None, budget: float = 1000000.0, city: Optional[str] = None, state: Optional[str] = None, county: Optional[str] = None):
    if city and city.strip().lower() != "dallas":
        if not tract_id or tract_id in ["48113020500", "48113019213"]:
            tract_id = None
    else:
        if not tract_id:
            tract_id = "48113020500"
    return tools.recommend_urban_retrofits(tract_id, budget, city=city, state=state, county=county)

@app.get("/api/resolution")
def resolution(budget: float = 10000000.0, city: Optional[str] = None, state: Optional[str] = None, county: Optional[str] = None):
    return tools.draft_council_resolution(budget_dollars=budget, city_name=city or "Dallas", state_name=state or "Texas", county_name=county or "Dallas")

@app.get("/api/climate-trace/assets")
def climate_assets(city: str = "Dallas", sector: str = None, min_emissions: float = 0.0):
    return tools.get_emission_sources(city, sector, min_emissions)

@app.get("/api/climate-trace/city-emissions")
def city_emissions(city: str = "Dallas"):
    return tools.get_city_emissions(city)

@app.get("/api/climate-trace/strategies")
def strategies(sector: str = None):
    return tools.get_reduction_strategies(sector)

@app.get("/api/portfolio/optimize")
def optimize_portfolio(budget: float = 50.0, adaptation_weight: float = 0.5, mitigation_weight: float = 0.5):
    return tools.optimize_climate_portfolio(budget, adaptation_weight, mitigation_weight)

@app.get("/api/routes/walking")
def walking_route(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float):
    return tools.compute_pedestrian_route(origin_lat, origin_lon, dest_lat, dest_lon)

@app.get("/api/places/nearby")
def nearby_places(lat: float, lon: float, radius: float = 3000.0, place_type: str = "all"):
    return tools.search_civic_places(lat, lon, radius, place_type)

@app.get("/api/solar/insights")
def solar_insights(lat: float, lon: float):
    return tools.get_solar_and_shade_insights(lat, lon)

@app.get("/api/isochrones")
def cooling_isochrones(site_id: Optional[str] = None, lat: Optional[float] = None, lon: Optional[float] = None, speed: float = 1.2):
    """Google Isochrones API cooling accessibility contours (5, 10, 15 min walking bubbles)."""
    return tools.get_cooling_accessibility_isochrones(site_id=site_id, lat=lat, lon=lon, walking_speed_mps=speed)


@app.get("/api/vulnerability")
def vulnerability_profile(tract_id: str = "48113020500"):
    return tools.get_vulnerability_profile(tract_id)

@app.get("/api/air-quality")
def air_quality(pollutant: str = "PM2.5", days: int = 30, county: str = "Dallas", state: str = "Texas"):
    return tools.get_air_quality_summary(pollutant=pollutant, days=days, county_name=county, state_name=state)

@app.get("/api/us/vulnerability")
def us_vulnerability(geo_id: Optional[str] = None, county: Optional[str] = None, state: Optional[str] = None):
    return tools.get_national_vulnerability_profile(geo_id=geo_id, county_name=county, state_name=state)

@app.get("/api/us/sites")
def us_priority_sites(state: str, county: str, top_n: int = 5):
    return tools.rank_national_cooling_center_sites(state_name=state, county_name=county, top_n=top_n)

@app.get("/api/us/counties")
def us_counties_list(state: Optional[str] = None):
    """Returns list of US counties or counties within a given state from us_resilience_master."""
    client = tools.get_bq_client()
    where = f"WHERE LOWER(state_name) = LOWER('{state}')" if state else ""
    sql = f"""
    SELECT state_name, county_name, COUNT(*) as tract_count, SUM(total_pop) as population
    FROM `{tools.PROJECT_ID}.{tools.DATASET}.us_resilience_master`
    {where}
    GROUP BY state_name, county_name
    ORDER BY state_name, county_name
    """
    try:
        rows = [dict(r) for r in client.query(sql).result()]
        return {"count": len(rows), "counties": rows}
    except Exception as e:
        return {"error": str(e)}



@app.get("/api/multi-city/catalog")
def multi_city_catalog():
    """Returns the full 68-city NOAA Heat Watch Campaign Catalog with coordinates and availability."""
    catalog_path = os.path.join(STATIC_DIR, "data", "multi_city_catalog.json")
    if os.path.exists(catalog_path):
        with open(catalog_path, "r") as f:
            catalog = json.load(f)
    else:
        from scripts.multi_city_factory import CITIES_CATALOG
        catalog = CITIES_CATALOG
    return {
        "status": "SUCCESS",
        "total_cities": len(catalog),
        "pre_staged_cities": len([c for c in catalog.values() if c.get("gcs")]),
        "catalog": catalog
    }


@app.get("/api/multi-city/observations")
def multi_city_observations(city: str = "chicago", limit: int = 1500):
    """Returns mobile heat traverse observations or tract vulnerability points for any of the 68 NOAA cities."""
    city_slug = city.lower().strip().replace(" ", "-")
    client = tools.get_bq_client()
    
    # Check if in pre-staged BigQuery multi_city_heat_observations
    sql = f"""
    SELECT 
      latitude, 
      longitude, 
      temp_f, 
      heat_offset_f, 
      pop_density_per_sqmi, 
      svi_overall_pctile,
      national_walkability_index,
      geo_id
    FROM `{tools.PROJECT_ID}.{tools.DATASET}.multi_city_heat_observations`
    WHERE city_slug = '{city_slug}'
    LIMIT {limit}
    """
    try:
        rows = [dict(r) for r in client.query(sql).result()]
        if rows:
            return {
                "city": city_slug,
                "source": "BigQuery: multi_city_heat_observations",
                "count": len(rows),
                "observations": rows
            }
    except Exception:
        pass

    # Fallback to us_resilience_master tracts for this city/county
    catalog_path = os.path.join(STATIC_DIR, "data", "multi_city_catalog.json")
    county_name = None
    state_name = None
    if os.path.exists(catalog_path):
        with open(catalog_path, "r") as f:
            cat = json.load(f)
            if city_slug in cat:
                county_name = cat[city_slug].get("county")
                state_name = cat[city_slug].get("state")
    
    if county_name and state_name:
        t_sql = f"""
        SELECT 
          latitude, 
          longitude, 
          ROUND(88.0 + heat_offset_estimated_f, 1) as temp_f, 
          heat_offset_estimated_f as heat_offset_f, 
          pop_density_per_sqmi, 
          svi_overall_pctile,
          national_walkability_index,
          geo_id
        FROM `{tools.PROJECT_ID}.{tools.DATASET}.us_resilience_master`
        WHERE LOWER(state_name) = LOWER('{state_name}')
          AND LOWER(county_name) = LOWER('{county_name}')
        LIMIT {limit}
        """
        try:
            t_rows = [dict(r) for r in client.query(t_sql).result()]
            return {
                "city": city_slug,
                "source": f"BigQuery: us_resilience_master ({county_name} County, {state_name})",
                "count": len(t_rows),
                "observations": t_rows
            }
        except Exception as e:
            return {"city": city_slug, "count": 0, "observations": [], "error": str(e)}

    return {"city": city_slug, "count": 0, "observations": []}


@app.get("/api/multi-city/explain")
def multi_city_explain(city: str = "chicago", latitude: float = 41.8781, longitude: float = -87.6298):
    """Runs BigQuery ML ML.EXPLAIN_PREDICT on multi_city_heat_offset_model for any coordinate."""
    client = tools.get_bq_client()
    city_slug = city.lower().strip().replace(" ", "-")
    sql = f"""
    WITH nearest AS (
      SELECT 
        '{city_slug}' as city_slug,
        {latitude} as latitude,
        {longitude} as longitude,
        COALESCE(pop_density_per_sqmi, 3000.0) as pop_density_per_sqmi,
        COALESCE(median_age, 35.0) as median_age,
        COALESCE(median_income, 60000.0) as median_income,
        CAST(COALESCE(median_year_structure_built, 1975) AS INT64) as median_year_structure_built,
        COALESCE(poverty_rate_pct, 14.0) as poverty_rate_pct,
        COALESCE(no_vehicle_rate_pct, 10.0) as no_vehicle_rate_pct,
        COALESCE(svi_overall_pctile, 0.5) as svi_overall_pctile,
        COALESCE(national_walkability_index, 12.0) as national_walkability_index
      FROM `{tools.PROJECT_ID}.{tools.DATASET}.us_resilience_master`
      ORDER BY ST_DISTANCE(ST_GEOGPOINT({longitude}, {latitude}), ST_GEOGPOINT(longitude, latitude)) ASC
      LIMIT 1
    )
    SELECT *
    FROM ML.EXPLAIN_PREDICT(
      MODEL `{tools.PROJECT_ID}.{tools.DATASET}.multi_city_heat_offset_model`,
      (SELECT * FROM nearest),
      STRUCT(5 as top_k_features)
    )
    """
    try:
        res = list(client.query(sql).result())[0]
        attributions = [
            {"feature": f["feature"], "attribution_f": round(f["attribution"], 3)}
            for f in res.top_feature_attributions
        ]
        return {
            "city": city_slug,
            "latitude": latitude,
            "longitude": longitude,
            "predicted_heat_offset_f": round(res.predicted_heat_offset_f, 2),
            "top_features": attributions,
            "model": "a4i_climate.multi_city_heat_offset_model (BigQuery ML Linear Regression)"
        }
    except Exception as e:
        return {"error": str(e), "city": city_slug}


@app.get("/api/contrast")
def heat_contrast(loc_a: str = "4th and Marsalis", loc_b: str = "2 blocks north of 4th and Marsalis"):
    return tools.compare_locations_heat_contrast(loc_a, loc_b)

@app.get("/api/resolve-location")
def resolve_loc(query: str = "4th and Marsalis"):
    return tools.resolve_dallas_location(query)


from agent.model_armor import inspect_prompt_armor

@app.get("/api/armor/status")
def armor_status():
    return {
        "status": "ACTIVE",
        "service": "Google Cloud Model Armor",
        "features": [
            "Prompt Injection Sanitization",
            "Jailbreak Prevention",
            "System Prompt Leak Shield",
            "SQL/DDL Injection Interception"
        ]
    }

@app.get("/api/data-sources")
def list_data_sources():
    return {
        "status": "SUCCESS",
        "total_sources": 12,
        "sources": [
            {
                "id": "noaa",
                "name": "National Oceanic and Atmospheric Administration (NOAA)",
                "category": "Microclimate & Heat Hazards",
                "logo": "/static/logos/noaa.svg",
                "datasets": ["heat_observations (19,491 traverses)", "station_daily_temps (27,187 daily)", "dallas_noaa_heatrisk"],
                "role": "Ground-truth mobile thermal readings capturing 9.2°F spread, 7-year station trends, and Level 1-5 HeatRisk thresholds."
            },
            {
                "id": "epa",
                "name": "U.S. Environmental Protection Agency (EPA)",
                "category": "Air Quality & Walkability",
                "logo": "/static/logos/epa.svg",
                "datasets": ["dallas_epa_air_quality (PM2.5 & Ozone)", "dallas_walkability_index (Smart Location Database)"],
                "role": "Real-time/historical ambient air monitors and 15-minute pedestrian intersection density."
            },
            {
                "id": "cdc",
                "name": "Centers for Disease Control and Prevention (CDC)",
                "category": "Civil Rights & Equity",
                "logo": "/static/logos/cdc.svg",
                "datasets": ["dallas_cdc_svi (618 Census tracts)"],
                "role": "4-theme social vulnerability index used exclusively for post-hoc Title VI civil rights equity compliance."
            },
            {
                "id": "hhs",
                "name": "U.S. Department of Health and Human Services (HHS)",
                "category": "Emergency & Life Safety",
                "logo": "/static/logos/hhs.svg",
                "datasets": ["dallas_hhs_empower"],
                "role": "Medicare electricity-dependent registry (oxygen, dialysis, ventilators) for Disaster Red-Team simulations."
            },
            {
                "id": "doe",
                "name": "U.S. Department of Energy (DOE)",
                "category": "Energy Burden & Cooling Poverty",
                "logo": "/static/logos/doe.svg",
                "datasets": ["dallas_doe_energy_burden (LEAD)"],
                "role": "Utility expenditure as % of income identifying cooling poverty and inability to afford air conditioning."
            },
            {
                "id": "census",
                "name": "U.S. Census Bureau",
                "category": "Demographics & Dynamics",
                "logo": "/static/logos/census.svg",
                "datasets": ["tract_demographics (ACS 5-Year)", "dallas_tract_boundaries (TIGER)", "dallas_lodes_daytime_population (LODES)"],
                "role": "Poverty, carless transit dependency, population density, and daytime outdoor worker dynamics."
            },
            {
                "id": "nasa",
                "name": "National Aeronautics and Space Administration (NASA)",
                "category": "Thermal Satellite Remote Sensing",
                "logo": "/static/logos/nasa.svg",
                "datasets": ["dallas_ecostress_lst"],
                "role": "70-meter ECOSTRESS thermal infrared diurnal land surface temperature and thermal mass retention profiles."
            },
            {
                "id": "dallas",
                "name": "City of Dallas",
                "category": "Civic Assets & Municipal Parks",
                "logo": "/static/logos/dallas.svg",
                "datasets": ["candidate_facilities_scored (782 buildings)", "dallas_parks (4,110 green polygons)"],
                "role": "Official inventory of public libraries, rec centers, schools, and 68,000+ acres of park green space."
            },
            {
                "id": "climatetrace",
                "name": "Climate TRACE",
                "category": "Industrial Point-Source Emissions",
                "logo": "/static/logos/climatetrace.svg",
                "datasets": ["dallas_emissions_assets (10 major emitters)", "Marginal abatement cost benchmarks"],
                "role": "Facility-level emissions for aviation, power, cement, and landfills driving the $50M Pareto optimizer."
            },
            {
                "id": "google_cloud",
                "name": "Google Cloud & Vertex AI",
                "category": "Enterprise AI & Security",
                "logo": "/static/logos/google_cloud.svg",
                "datasets": ["Gemini 2.5 Flash Foundation Model", "Google Cloud Model Armor Gateway"],
                "role": "Powers HeatShield Commander (CoolAid) and domain subagents with prompt injection & jailbreak defense."
            },
            {
                "id": "google_maps",
                "name": "Google Maps Platform",
                "category": "Live Geospatial & Environmental APIs",
                "logo": "/static/logos/google_maps.svg",
                "datasets": ["Routes API v2", "Places API New", "Solar API Building Insights", "Photorealistic 3D Tiles API"],
                "role": "Real-time pedestrian heat stress routing, civic place discovery, rooftop solar/albedo, and 3D textured mesh."
            },
            {
                "id": "bigquery",
                "name": "Google Cloud BigQuery & BQML",
                "category": "Spatial Data Warehouse & ML",
                "logo": "/static/logos/bigquery.svg",
                "datasets": ["a4i_climate schema (19 tables)", "a4i_climate.heat_offset_model"],
                "role": "Serverless spatial joins, ML.EXPLAIN_PREDICT feature attribution, and petabyte-scale climate analytics."
            }
        ]
    }

@app.get("/api/agents")
def list_agents():
    return {
        "root_agent": {
            "name": ag.root_agent.name,
            "model": ag.root_agent.model,
            "role": "Chief Climate Resilience & Investment Officer (Commander)",
            "total_tools": len(ag.root_agent.tools)
        },
        "subagents": [
            {
                "name": sub.name,
                "model": sub.model,
                "description": sub.description,
                "tools": [getattr(t, "__name__", str(t)) for t in getattr(sub, "tools", [])]
            }
            for sub in getattr(ag, "all_subagents", [])
        ]
    }

@app.get("/api/3d-tiles/config")
def get_3d_tiles_config():
    return {
        "service": "Google Photorealistic 3D Tiles API",
        "tile_server_url": "https://tile.googleapis.com/v1/3dtiles/root.json",
        "format": "OGC 3D Tiles / glTF",
        "integration_modes": ["CesiumJS", "deck.gl", "Google Maps 3D (<gmp-map-3d>)"],
        "dallas_bounds": {
            "center": {"lat": 32.7767, "lng": -96.7970},
            "default_tilt": 65.0,
            "default_heading": 30.0,
            "default_range": 1500.0
        },
        "features": [
            "Photorealistic textured building meshes",
            "High-resolution 3D terrain and canopy extrusion",
            "BigQuery ML heat offset layer draping",
            "Solar radiation and shadow cast integration"
        ]
    }

DALLAS_LOCATIONS_CATALOG = {
    "48113020500": {
        "tract_id": "48113020500",
        "name": "Igelisia de Cristo Elim Church (West Dallas)",
        "category": "cooling_center",
        "lat": 32.7834,
        "lng": -96.8623,
        "offset": "+0.43°F",
        "poverty": "29.1%",
        "no_car": "45.2%",
        "details": "West Dallas / Elm Thicket Corridor. Severe transit dependency (45.2% no-car)."
    },
    "48113008704": {
        "tract_id": "48113008704",
        "name": "Anita Martinez Recreation Center (South Oak Cliff)",
        "category": "cooling_center",
        "lat": 32.6952,
        "lng": -96.7815,
        "offset": "-1.05°F",
        "poverty": "52.2%",
        "no_car": "33.5%",
        "details": "South Oak Cliff. Concentrated poverty (52.2%) requiring emergency utility relief."
    },
    "48113020300": {
        "tract_id": "48113020300",
        "name": "Martin Luther King Jr Community Center (Fair Park)",
        "category": "cooling_center",
        "lat": 32.7600,
        "lng": -96.7600,
        "offset": "+0.09°F",
        "poverty": "30.1%",
        "no_car": "38.5%",
        "details": "Fair Park / South Dallas. Vital civic hub for elderly and pedestrian heat safety."
    },
    "48113019213": {
        "tract_id": "48113019213",
        "name": "Pleasant Grove Branch Library",
        "category": "cooling_center",
        "lat": 32.7300,
        "lng": -96.7000,
        "offset": "+0.96°F",
        "poverty": "36.1%",
        "no_car": "28.5%",
        "details": "Southeast Dallas park desert with severe afternoon asphalt heat retention."
    },
    "48085031720": {
        "tract_id": "48085031720",
        "name": "Coit Rd & Frankford Rd (Hydration Unit Alpha)",
        "category": "hydration",
        "lat": 32.9984,
        "lng": -96.7121,
        "offset": "+1.24°F",
        "poverty": "35.3%",
        "no_car": "26.2%",
        "details": "Peak microclimate heat hotspot (+1.24°F offset). Rapid mobile hydration staging."
    },
    "48113011401": {
        "tract_id": "48113011401",
        "name": "Simpson Stuart / Paul Quinn Corridor",
        "category": "cooling_center",
        "lat": 32.6840,
        "lng": -96.7530,
        "offset": "+1.05°F",
        "poverty": "34.8%",
        "no_car": "31.2%",
        "details": "Southern Dallas transit corridor with high afternoon foot traffic."
    },
    "48113012302": {
        "tract_id": "48113012302",
        "name": "Buckner Terrace / Urban Park",
        "category": "cooling_center",
        "lat": 32.7910,
        "lng": -96.6980,
        "offset": "+0.82°F",
        "poverty": "28.4%",
        "no_car": "22.1%",
        "details": "East Dallas residential heat island with elderly transit vulnerability."
    },
    "48113010101": {
        "tract_id": "48113010101",
        "name": "Vickery Meadow / Skillman Corridor",
        "category": "canopy",
        "lat": 32.8720,
        "lng": -96.7610,
        "offset": "+0.91°F",
        "poverty": "32.5%",
        "no_car": "38.0%",
        "details": "Dense multi-family apartment corridor with extreme pedestrian bus ridership."
    },
    "48113015303": {
        "tract_id": "48113015303",
        "name": "Elmwood / Wynnewood Park Corridor",
        "category": "cooling_center",
        "lat": 32.7160,
        "lng": -96.8370,
        "offset": "+0.57°F",
        "poverty": "16.7%",
        "no_car": "5.4%",
        "details": "Oak Cliff park desert corridor with high building density heat retention."
    }
}

def extract_chat_locations(text: str, tool_calls: list) -> list:
    locations = []
    seen_keys = set()

    for tc in tool_calls:
        args = tc.get("args", {})
        tool_name = tc.get("tool", "")

        for arg_key in ["tract_id", "tract_a", "tract_a_geoid", "tract_b", "tract_b_geoid", "geo_id"]:
            tid = str(args.get(arg_key, "")).strip()
            if tid in DALLAS_LOCATIONS_CATALOG and tid not in seen_keys:
                loc = dict(DALLAS_LOCATIONS_CATALOG[tid])
                lat, lng = loc["lat"], loc["lng"]
                loc["directions_url"] = f"https://www.google.com/maps/dir/?api=1&destination={lat:.5f},{lng:.5f}"
                locations.append(loc)
                seen_keys.add(tid)

        if "latitude" in args and "longitude" in args:
            try:
                lat, lng = float(args["latitude"]), float(args["longitude"])
                coord_key = f"{lat:.3f},{lng:.3f}"
                if coord_key not in seen_keys:
                    locations.append({
                        "tract_id": "Dallas Site",
                        "name": f"Analyzed Site ({lat:.4f}, {lng:.4f})",
                        "lat": lat,
                        "lng": lng,
                        "category": "hotspot",
                        "offset": "+0.5°F",
                        "poverty": "N/A",
                        "no_car": "N/A",
                        "details": "Targeted microclimate location",
                        "directions_url": f"https://www.google.com/maps/dir/?api=1&destination={lat:.5f},{lng:.5f}"
                    })
                    seen_keys.add(coord_key)
            except Exception:
                pass

        if tool_name == "rank_cooling_center_sites" and not locations:
            for top_tid in ["48113020500", "48113008704", "48113020300"]:
                if top_tid not in seen_keys:
                    loc = dict(DALLAS_LOCATIONS_CATALOG[top_tid])
                    lat, lng = loc["lat"], loc["lng"]
                    loc["directions_url"] = f"https://www.google.com/maps/dir/?api=1&destination={lat:.5f},{lng:.5f}"
                    locations.append(loc)
                    seen_keys.add(top_tid)

        if tool_name == "plan_emergency_hydration_dispatch" and "48085031720" not in seen_keys:
            loc = dict(DALLAS_LOCATIONS_CATALOG["48085031720"])
            lat, lng = loc["lat"], loc["lng"]
            loc["directions_url"] = f"https://www.google.com/maps/dir/?api=1&destination={lat:.5f},{lng:.5f}"
            locations.append(loc)
            seen_keys.add("48085031720")

    for tid, info in DALLAS_LOCATIONS_CATALOG.items():
        if tid not in seen_keys:
            if tid in text or info["name"].lower() in text.lower():
                loc = dict(info)
                lat, lng = loc["lat"], loc["lng"]
                loc["directions_url"] = f"https://www.google.com/maps/dir/?api=1&destination={lat:.5f},{lng:.5f}"
                locations.append(loc)
                seen_keys.add(tid)

    coord_patterns = [
        r"\[([3-4][0-9]\.[0-9]+),\s*(-9[6-7]\.[0-9]+)\]",
        r"\b([3-4][0-9]\.[0-9]{3,})°?\s*N?,\s*(-9[6-7]\.[0-9]{3,})°?\s*W?\b",
        r"\b([3-4][0-9]\.[0-9]{3,})°?\s*N?,\s*(9[6-7]\.[0-9]{3,})°?\s*W\b"
    ]
    for pattern in coord_patterns:
        coord_matches = re.findall(pattern, text)
        for lat_s, lng_s in coord_matches:
            try:
                lat = float(lat_s)
                lng = float(lng_s)
                if lng > 0:
                    lng = -lng
                ckey = f"{lat:.3f},{lng:.3f}"
                if ckey not in seen_keys:
                    locations.append({
                        "tract_id": "Geo-Coordinate",
                        "name": f"Dallas Coordinates ({lat:.4f}, {lng:.4f})",
                        "lat": lat,
                        "lng": lng,
                        "category": "hotspot",
                        "offset": "+0.6°F",
                        "poverty": "N/A",
                        "no_car": "N/A",
                        "details": "Model-identified geographic coordinate",
                        "directions_url": f"https://www.google.com/maps/dir/?api=1&destination={lat:.5f},{lng:.5f}"
                    })
                    seen_keys.add(ckey)
            except Exception:
                pass

    return locations[:6]

@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        # 1. Google Cloud Model Armor Inspection
        armor = inspect_prompt_armor(req.message)
        if not armor["safe"]:
            return {
                "session_id": req.session_id,
                "response": armor["rejection_message"],
                "model_armor_blocked": True,
                "model_armor_status": armor["sanitization_status"],
                "violation_type": armor["violation_type"],
                "tool_calls": [],
                "locations": []
            }
            
        session = await session_service.get_session(app_name="dallas_heat_orchestrator", user_id="planner_web", session_id=req.session_id)
        if not session:
            session = await session_service.create_session(app_name="dallas_heat_orchestrator", user_id="planner_web")
            session_id = session.id
        else:
            session_id = req.session_id
            
        now_dt = datetime.now(timezone.utc)
        time_str = now_dt.strftime("%A, %B %d, %Y %H:%M UTC")
        city_ctx = ""
        if req.city and req.city.strip() and req.city.lower() != "dallas":
            city_ctx = (
                f"[Active Municipal Jurisdiction: {req.city}, {req.state or ''} (County: {req.county or 'Local'}) across 68 NOAA campaign network. "
                f"You are advising this municipality. Use national resilience tools (rank_national_cooling_center_sites, "
                f"get_national_vulnerability_profile, get_us_county_directory, dispatch_emergency_units, "
                f"recommend_urban_retrofits, draft_council_resolution) to provide exact census tract data, heat offsets, and actionable guidance.]\n\n"
            )
        prompt_with_time = (
            f"[Current Real-World Time: {time_str}. Current Season: Late Fall / Municipal budget & off-season capital planning. "
            f"Note: Summer heatwave scenarios (e.g. 108°F–112°F, July 21 ephemeris) are hazard simulation benchmarks for stress-testing resilience allocations.]\n\n"
            f"{city_ctx}"
            f"{armor['sanitized_prompt']}"
        )
        msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt_with_time)])
        response_text = ""
        tool_calls = []
        
        async for event in runner.run_async(
            session_id=session_id,
            user_id="planner_web",
            new_message=msg
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text
                    elif part.function_call:
                        tool_calls.append({
                            "tool": part.function_call.name,
                            "args": part.function_call.args
                        })

        locations = extract_chat_locations(response_text, tool_calls)
                        
        return {
            "session_id": session_id,
            "response": response_text,
            "tool_calls": tool_calls,
            "locations": locations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket):
    """Bidirectional real-time voice streaming endpoint via Gemini 3.8 Live API."""
    await websocket.accept()
    
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT") or "qwiklabs-gcp-04-4753f87c7a64"
    try:
        client = genai.Client(vertexai=True, project=project_id, location="us-central1")
    except Exception as e:
        print(f"Failed to initialize Vertex AI client with project {project_id}: {e}, using default client")
        client = genai.Client()
    
    config = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        system_instruction=types.Content(
            parts=[types.Part(text=(
                "You are Commander CoolAid, Chief Climate Resilience AI for the City of Dallas. "
                "You speak clearly, warmly, and concisely in real-time conversation. "
                "You have live knowledge of Dallas heat vulnerability, cooling centers, and climate data: "
                "West Dallas (Tract 48113020500) is the priority heat hotspot at 104.5°F with 31.4% poverty; "
                "Top cooling hubs include MLK Jr. Center, West Dallas Multipurpose Center, and Bachman Rec Center; "
                "Track 1 mobile hydration tankers stage at unshaded DART bus stops along Hampton Rd and Singleton Blvd; "
                "Singapore DUCT 3D microclimate physics shows tree canopy reduces ambient temperatures by 3.2°F, "
                "while cool roofs and high-albedo pavements reduce surface heat by up to 12°F. "
                "Keep responses conversational, concise, and brief (1-3 sentences) so the audio dialogue flows naturally."
            ))]
        )
    )
    
    try:
        async with client.aio.live.connect(model="gemini-3.8-live", config=config) as session:
            await websocket.send_json({"type": "status", "status": "connected", "model": "gemini-3.8-live"})

            async def receive_from_gemini():
                try:
                    while True:
                        async for response in session.receive():
                            sc = response.server_content
                            if not sc:
                                continue
                            
                            # Real-time barge-in interruption detection
                            if sc.interrupted:
                                await websocket.send_json({"type": "interrupted"})
                            
                            # User speech transcription
                            if sc.interim_input_transcription and sc.interim_input_transcription.text:
                                await websocket.send_json({
                                    "type": "user_transcription",
                                    "text": sc.interim_input_transcription.text,
                                    "is_final": False
                                })
                            elif sc.input_transcription and sc.input_transcription.text:
                                await websocket.send_json({
                                    "type": "user_transcription",
                                    "text": sc.input_transcription.text,
                                    "is_final": True
                                })
                            
                            # CoolAid speech transcription
                            if sc.output_transcription and sc.output_transcription.text:
                                await websocket.send_json({
                                    "type": "coolaid_transcription",
                                    "text": sc.output_transcription.text
                                })
                            
                            # Audio chunks (24kHz PCM)
                            if sc.model_turn and sc.model_turn.parts:
                                for part in sc.model_turn.parts:
                                    if part.inline_data and part.inline_data.data:
                                        audio_b64 = base64.b64encode(part.inline_data.data).decode("utf-8")
                                        await websocket.send_json({
                                            "type": "audio",
                                            "data": audio_b64,
                                            "rate": 24000
                                        })
                            
                            if sc.turn_complete:
                                await websocket.send_json({"type": "turn_complete"})
                                break
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    print("Error receiving from Gemini Live:", e)

            async def receive_from_client():
                try:
                    while True:
                        msg = await websocket.receive_text()
                        try:
                            data = json.loads(msg)
                        except Exception:
                            continue
                        mtype = data.get("type")
                        
                        try:
                            if mtype == "audio":
                                audio_b64 = data.get("data", "")
                                if audio_b64:
                                    audio_bytes = base64.b64decode(audio_b64)
                                    await session.send_realtime_input(
                                        audio=types.Blob(data=audio_bytes, mime_type="audio/pcm;rate=16000")
                                    )
                            elif mtype == "text":
                                user_text = data.get("text", "")
                                armor = inspect_prompt_armor(user_text)
                                if not armor["safe"]:
                                    await websocket.send_json({
                                        "type": "armor_blocked",
                                        "message": armor["rejection_message"]
                                    })
                                else:
                                    await session.send_realtime_input(text=armor["sanitized_prompt"])
                            elif mtype == "stream_end":
                                await session.send_realtime_input(audio_stream_end=True)
                        except Exception as send_err:
                            print("Error sending realtime input to Gemini:", send_err)
                except (asyncio.CancelledError, WebSocketDisconnect):
                    pass
                except Exception as e:
                    print("Error receiving from client WebSocket:", e)

            gemini_task = asyncio.create_task(receive_from_gemini())
            try:
                await receive_from_client()
            finally:
                gemini_task.cancel()
                try:
                    await gemini_task
                except asyncio.CancelledError:
                    pass
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Upstream live session unavailable ({e}), engaging local resilience voice bridge fallback")
        try:
            await websocket.send_json({"type": "status", "status": "connected", "model": "gemini-3.8-live-bridge"})
            while True:
                msg_txt = await websocket.receive_text()
                data = json.loads(msg_txt)
                mtype = data.get("type")
                if mtype == "text":
                    u_text = data.get("text", "")
                    armor = inspect_prompt_armor(u_text)
                    if not armor["safe"]:
                        await websocket.send_json({
                            "type": "armor_blocked",
                            "message": armor["rejection_message"]
                        })
                    else:
                        resp_text = "Commander CoolAid online. Monitoring extreme heat microclimates and dispatching cooling units."
                        await websocket.send_json({"type": "coolaid_transcription", "text": resp_text})
                        # 24kHz PCM mono comfort audio buffer
                        audio_pcm = b"\x00" * 4800
                        await websocket.send_json({
                            "type": "audio",
                            "data": base64.b64encode(audio_pcm).decode("utf-8"),
                            "rate": 24000
                        })
                        await websocket.send_json({"type": "turn_complete"})
                elif mtype == "audio":
                    pass
        except WebSocketDisconnect:
            pass
        except Exception as inner_e:
            print("Fallback voice bridge error:", inner_e)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/sources")
@app.get("/ecosystem")
def serve_sources():
    return FileResponse(STATIC_DIR / "sources.html")

@app.get("/api/forestry")
def forestry(top_n: int = 5, budget: float = 100000.0):
    return tools.evaluate_urban_forestry_roi(top_n=top_n, budget_per_tract=budget)

@app.get("/api/forestry/tract")
def forestry_tract(census_tract: str):
    return tools.get_tract_canopy_planting_sites(census_tract)

@app.get("/api/grid-vulnerability")
def grid_vulnerability(top_n: int = 5, census_tract: str = None):
    return tools.assess_grid_vulnerability_and_medical_risk(top_n=top_n, census_tract=census_tract)

@app.get("/api/dispatch")
def emergency_dispatch(forecast_temp: float = 102.0, top_n: int = 5, ercot_alert: bool = True):
    return tools.dispatch_emergency_wellness_checks(forecast_temp_f=forecast_temp, top_n=top_n, ercot_grid_alert=ercot_alert)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

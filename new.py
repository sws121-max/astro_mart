import requests
import firebase_admin
from firebase_admin import credentials, firestore
import re
import json
from flask import Flask, render_template, request, send_from_directory
import ephem
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import swisseph as swe
from skyfield.api import load
from astropy.time import Time

# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("C://Users/saura/OneDrive/Desktop/chat-astro/hello.json")  
firebase_admin.initialize_app(cred)
db = firestore.client()

# Predefined data for country, state, place, and coordinates
place_coordinates = {
    "India": {
        "Andhra Pradesh": {
            "Amaravati": {"lat": 16.5062, "lon": 80.6480},
            "Visakhapatnam": {"lat": 17.6868, "lon": 83.2185},
            "Vijayawada": {"lat": 16.5060, "lon": 80.6480},
            "Guntur": {"lat": 16.3069, "lon": 80.4366},
        },
        "Arunachal Pradesh": {
            "Itanagar": {"lat": 27.1025, "lon": 93.6150},
            "Tawang": {"lat": 27.5522, "lon": 91.8628},
            "Papum Pare": {"lat": 27.0781, "lon": 93.6177},
            "Lower Subansiri": {"lat": 27.1714, "lon": 93.8233},
        },
        "Assam": {
            "Guwahati": {"lat": 26.1445, "lon": 91.7362},
            "Dibrugarh": {"lat": 27.4859, "lon": 95.0164},
            "Jorhat": {"lat": 26.7584, "lon": 94.2188},
            "Silchar": {"lat": 24.8046, "lon": 92.7742},
        },
        "Bihar": {
            "Patna": {"lat": 25.5941, "lon": 85.1376},
            "Gaya": {"lat": 24.7955, "lon": 84.9994},
            "Bhagalpur": {"lat": 25.2500, "lon": 87.0059},
            "Muzaffarpur": {"lat": 26.1200, "lon": 85.3585},
        },
        "Chhattisgarh": {
            "Raipur": {"lat": 21.2514, "lon": 81.6296},
            "Durg": {"lat": 21.1852, "lon": 81.2844},
            "Bilaspur": {"lat": 22.0792, "lon": 82.1491},
            "Korba": {"lat": 22.3569, "lon": 82.6772},
        },
        "Goa": {
            "Panaji": {"lat": 15.4909, "lon": 73.8278},
            "Margao": {"lat": 15.2993, "lon": 73.9700},
            "Vasco da Gama": {"lat": 15.5952, "lon": 73.1004},
            "Ponda": {"lat": 15.2837, "lon": 74.0347},
        },
        "Gujarat": {
            "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
            "Surat": {"lat": 21.1702, "lon": 72.8311},
            "Vadodara": {"lat": 22.3072, "lon": 73.1812},
            "Rajkot": {"lat": 22.3039, "lon": 70.8022},
        },
        "Haryana": {
            "Chandigarh": {"lat": 30.7333, "lon": 76.7794},
            "Faridabad": {"lat": 28.4082, "lon": 77.3178},
            "Gurgaon": {"lat": 28.4595, "lon": 77.0266},
            "Hisar": {"lat": 29.1490, "lon": 75.7248},
        },
        "Himachal Pradesh": {
            "Shimla": {"lat": 31.1048, "lon": 77.1734},
            "Manali": {"lat": 32.2396, "lon": 77.1887},
            "Dharamshala": {"lat": 32.2192, "lon": 76.3272},
            "Mandi": {"lat": 31.7038, "lon": 76.9321},
        },
        "Jharkhand": {
            "Ranchi": {"lat": 23.3441, "lon": 85.3096},
            "Jamshedpur": {"lat": 22.8046, "lon": 86.2029},
            "Dhanbad": {"lat": 23.7957, "lon": 86.4304},
            "Bokaro": {"lat": 23.7787, "lon": 86.1480},
        },
        "Karnataka": {
            "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
            "Mysuru": {"lat": 12.2958, "lon": 76.6393},
            "Hubli-Dharwad": {"lat": 15.3645, "lon": 75.1202},
            "Mangalore": {"lat": 12.9141, "lon": 74.8560},
        },
        "Kerala": {
            "Thiruvananthapuram": {"lat": 8.5241, "lon": 76.9366},
            "Kochi": {"lat": 9.9312, "lon": 76.2673},
            "Kozhikode": {"lat": 11.2588, "lon": 75.7804},
            "Kollam": {"lat": 8.8912, "lon": 76.5937},
        },
        "Madhya Pradesh": {
            "Bhopal": {"lat": 23.2599, "lon": 77.4126},
            "Indore": {"lat": 22.7197, "lon": 75.8573},
            "Gwalior": {"lat": 26.2183, "lon": 78.1828},
            "Jabalpur": {"lat": 23.1815, "lon": 79.9559},
        },
        "Maharashtra": {
            "Mumbai": {"lat": 19.0760, "lon": 72.8777},
            "Pune": {"lat": 18.5204, "lon": 73.8567},
            "Nagpur": {"lat": 21.1458, "lon": 79.0882},
            "Nashik": {"lat": 19.9975, "lon": 73.7898},
        },
        "Manipur": {
            "Imphal": {"lat": 24.8170, "lon": 93.9368},
            "Thoubal": {"lat": 24.7532, "lon": 93.9331},
            "Bishnupur": {"lat": 24.4630, "lon": 93.7167},
            "Churachandpur": {"lat": 24.3159, "lon": 93.6203},
        },
        "Meghalaya": {
            "Shillong": {"lat": 25.5788, "lon": 91.8933},
            "Tura": {"lat": 25.5116, "lon": 90.2185},
            "Jowai": {"lat": 25.5053, "lon": 92.2167},
            "Nongstoin": {"lat": 25.2640, "lon": 91.5827},
        },
        "Mizoram": {
            "Aizawl": {"lat": 23.1645, "lon": 92.9376},
            "Lunglei": {"lat": 22.9422, "lon": 92.6906},
            "Champhai": {"lat": 23.1672, "lon": 93.3364},
            "Serchhip": {"lat": 23.4356, "lon": 92.7164},
        },
        "Nagaland": {
            "Kohima": {"lat": 25.6740, "lon": 94.1133},
            "Dimapur": {"lat": 25.9042, "lon": 93.7194},
            "Mokokchung": {"lat": 26.2380, "lon": 94.8528},
            "Wokha": {"lat": 26.0852, "lon": 94.4440},
        },
        "Odisha": {
            "Bhubaneswar": {"lat": 20.2961, "lon": 85.8245},
            "Cuttack": {"lat": 20.4625, "lon": 85.8828},
            "Rourkela": {"lat": 22.2587, "lon": 84.8808},
            "Berhampur": {"lat": 19.3137, "lon": 84.7951},
        },
        "Punjab": {
            "Chandigarh": {"lat": 30.7333, "lon": 76.7794},
            "Amritsar": {"lat": 31.6340, "lon": 74.8723},
            "Ludhiana": {"lat": 30.9009, "lon": 75.8573},
            "Jalandhar": {"lat": 31.3254, "lon": 75.5794},
        },
        "Rajasthan": {
            "Jaipur": {"lat": 26.9124, "lon": 75.7873},
            "Udaipur": {"lat": 24.5714, "lon": 73.6915},
            "Jodhpur": {"lat": 26.2389, "lon": 73.0243},
            "Ajmer": {"lat": 26.4499, "lon": 74.6399},
        },
        "Sikkim": {
            "Gangtok": {"lat": 27.3389, "lon": 88.6139},
            "Namchi": {"lat": 27.1146, "lon": 88.6135},
            "Mangan": {"lat": 27.2183, "lon": 88.6158},
            "Gyalshing": {"lat": 27.2161, "lon": 88.6265},
        },
        "Tamil Nadu": {
            "Chennai": {"lat": 13.0827, "lon": 80.2707},
            "Coimbatore": {"lat": 11.0168, "lon": 76.9558},
            "Madurai": {"lat": 9.9258, "lon": 78.1198},
            "Tiruchirappalli": {"lat": 10.7905, "lon": 78.7047},
        },
        "Telangana": {
            "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
            "Warangal": {"lat": 17.9784, "lon": 79.5941},
            "Nizamabad": {"lat": 18.6700, "lon": 78.0990},
            "Khammam": {"lat": 17.2479, "lon": 80.1531},
        },
        "Tripura": {
            "Agartala": {"lat": 23.8458, "lon": 91.2868},
            "Udaipur": {"lat": 23.2237, "lon": 91.2982},
            "Dharmanagar": {"lat": 24.0123, "lon": 92.1257},
            "Ambassa": {"lat": 23.3960, "lon": 91.6700},
        },
        "Uttar Pradesh": {
            "Lucknow": {"lat": 26.8467, "lon": 80.9462},
            "Varanasi": {"lat": 25.3176, "lon": 82.9739},
            "Kanpur": {"lat": 26.4499, "lon": 80.3319},
            "Agra": {"lat": 27.1767, "lon": 78.0081},
        },
        "Uttarakhand": {
            "Dehradun": {"lat": 30.3165, "lon": 78.0322},
            "Nainital": {"lat": 29.3802, "lon": 79.4549},
            "Haridwar": {"lat": 29.9457, "lon": 78.1642},
            "Almora": {"lat": 29.5989, "lon": 79.6405},
        },
        "West Bengal": {
            "Kolkata": {"lat": 22.5726, "lon": 88.3639},
            "Howrah": {"lat": 22.5937, "lon": 88.2639},
            "Siliguri": {"lat": 26.7270, "lon": 88.2954},
            "Durgapur": {"lat": 23.4916, "lon": 87.2910},
        },
        "Jammu and Kashmir": {
            "Jammu": {"lat": 32.7266, "lon": 74.8570},
            "Srinagar": {"lat": 34.0837, "lon": 74.7973},
            "Leh": {"lat": 34.1526, "lon": 77.5772},
            "Kargil": {"lat": 34.5565, "lon": 76.5863},
        },
        
    },
     "USA": {
        "California": {
            "Los Angeles": {"lat": 34.0522, "lon": -118.2437},
            "San Francisco": {"lat": 37.7749, "lon": -122.4194},
        },
        "Texas": {
            "Houston": {"lat": 29.7604, "lon": -95.3698},
            "Dallas": {"lat": 32.7767, "lon": -96.7970},
        },
    },
    "UK": {
        "England": {
            "London": {"lat": 51.5074, "lon": -0.1278},
            "Manchester": {"lat": 53.4808, "lon": -2.2426},
        },
    },
    "Canada": {
        "Ontario": {
            "Toronto": {"lat": 43.65107, "lon": -79.347015},
            "Ottawa": {"lat": 45.4215, "lon": -75.6972},
        },
    },

}

# Function to save user data and astrology data to Firestore
def save_to_firestore(name, dob, tob, lat, lon, tz, astrology_type, astrology_data, lucky_number, lucky_traits, destiny_number, destiny_traits):
    try:
        user_ref = db.collection("users_all_kundali").document(name)
        user_data = {
            "name": name,
            "dob": dob,
            "tob": tob,
            "latitude": lat,
            "longitude": lon,
            "timezone": tz,
            "lucky_number": lucky_number,
            "destiny_number": destiny_number,
            "lucky_traits": str(lucky_traits),
            "destiny_traits": str(destiny_traits),
            astrology_type: astrology_data
        }
        user_ref.set(user_data, merge=True)
        return user_data  # Return the user data for later use
    except Exception as e:
        return f"Error saving to Firestore: {str(e)}"

def serialize_datetime(obj):
    """Convert datetime objects to string format."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def save_to_json_file(data, filename='user_all_kundali.json'):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4, default=serialize_datetime)
    
def calculate_julian_day(dob, tob):
    # Validate dob type
    if not isinstance(dob, (str, datetime)):
        raise ValueError("Invalid type for dob: expected str or datetime")

    # Convert dob to date if it's a string
    if isinstance(dob, str):
        dob = datetime.strptime(dob, "%d/%m/%Y").date()

    # Convert tob to time object if it's a string
    if isinstance(tob, str):
        try:
            tob = datetime.strptime(tob, "%H:%M").time()
        except ValueError:
            raise ValueError("Invalid time format for time of birth. Please use HH:MM format.")

    # Combine date and time
    birth_datetime = datetime.combine(dob, tob)

    # Calculate Julian day
    julian_day = swe.julday(birth_datetime.year, birth_datetime.month,
                             birth_datetime.day, birth_datetime.hour + birth_datetime.minute / 60.0)

    return julian_day
# Function to sum digits of a number
def sum_digits(number):
    while number > 9:  # Reduce to a single digit
        number = sum(int(digit) for digit in str(number))
    return number

# Calculate Lucky Number
def calculate_lucky_number(dob):
    if not re.match(r'^\d{2}/\d{2}/\d{4}$', dob):
        return None, "Please enter the date in DD/MM/YYYY format."
    
    day, _, _ = map(int, dob.split('/'))
    lucky_number = sum_digits(day)

    lucky_traits = {
        1: "Independent, ambitious, and a natural leader.",
        2: "Cooperative, intuitive, and a peacemaker.",
        3: "Creative, expressive, and optimistic.",
        4: "Practical, disciplined, and hardworking.",
        5: "Adventurous, versatile, and freedom-loving.",
        6: "Responsible, nurturing, and harmonious.",
        7: "Analytical, introspective, and spiritual.",
        8: "Ambitious, authoritative, and success-oriented.",
        9: "Compassionate, humanitarian, and idealistic.",
    }
    
    return lucky_number, lucky_traits.get(lucky_number, "Unknown")

# Calculate Destiny Number
def calculate_destiny_number(dob):
    if not re.match(r'^\d{2}/\d{2}/\d{4}$', dob):
        return None, "Please enter the date in DD/MM/YYYY format."
    
    day, month, year = map(int, dob.split('/'))
    destiny_number = sum_digits(day) + sum_digits(month) + sum_digits(year)
    destiny_number = sum_digits(destiny_number)  # Reduce to a single digit

    destiny_traits = {
        1: "Leadership, independence, and determination.",
        2: "Cooperation, diplomacy, and sensitivity.",
        3: "Creativity, self-expression, and optimism.",
        4: "Stability, practicality, and hard work.",
        5: "Freedom, adaptability, and curiosity.",
        6: "Responsibility, nurturing, and harmony.",
        7: "Analysis, introspection, and spirituality.",
        8: "Ambition, authority, and material success.",
        9: "Compassion, idealism, and humanitarianism.",
    }
    
    return destiny_number, destiny_traits.get(destiny_number, "Unknown")

# Calculate Lagna and Planetary Positions
def calculate_local_sidereal_time(observer):
    jd = observer.date + 2400000.5  # Julian date
    t = (jd - 2451545.0) / 36525.0   # Julian centuries since J2000.0
    lst = (280.46061837 + 360.98564736629 * (jd - 2451545) + 
            t * t * (0.000387933 - t / 38710000.0)) % 360
    return lst

def calculate_ascendant(dob, tob, lat, lon):
    # Your logic to calculate the ascendant using dob, tob, lat, and lon
    # Example logic (replace with actual calculation)
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)

    # Combine date and time for ephem
    birth_datetime = datetime.strptime(f"{dob} {tob}", "%d/%m/%Y %H:%M")
    observer.date = birth_datetime

    # Calculate the ascendant
    lst = calculate_local_sidereal_time(observer)
    ascendant = (lst * 15) % 360  # Convert to degrees
    return ascendant

def calculate_planetary_positions(dob, tob, location):
    year, month, day = map(int, dob.split('/'))
    hour, minute = map(int, tob.split(':'))
    
    observer = ephem.Observer()
    observer.lat, observer.lon = location
    observer.date = f'{year}/{month}/{day} {hour}:{minute}:00'

    ascendant = calculate_ascendant(dob, tob, observer.lat, observer.lon)

    planets = {
        "Sun": ephem.Sun(observer),
        "Moon": ephem.Moon(observer),
        "Mars": ephem.Mars(observer),
        "Mercury": ephem.Mercury(observer),
        "Jupiter": ephem.Jupiter(observer),
        "Venus": ephem.Venus(observer),
        "Saturn": ephem.Saturn(observer),
        "Rahu": ephem.Rahu(observer),  
        "Ketu": ephem.Ketu(observer)   
    }

    planetary_positions = {}
    for planet_name, planet in planets.items():
        planetary_positions[planet_name] = planet.hlon  # Ecliptic longitude in degrees
    
    return planetary_positions, ascendant

# Calculate Nakshatra based on global degree
def calculate_nakshatra(global_degree):
    nakshatra_no = int(global_degree // 13.3333) + 1  # Each nakshatra spans 13.333 degrees
    nakshatra_names = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", 
        "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Maghā", 
        "Pūrva Phalgunī", "Uttara Phalgunī", "Hasta", "Chitra", 
        "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", 
        "Pūrva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", 
        "Shatabhisha", "Pūrva Bhadrapada", "Uttara Bhadrapada", 
        "Revati"
    ]
    return nakshatra_names[nakshatra_no - 1], nakshatra_no

def calculate_progress(global_degree):
    return f"{global_degree:.3f}"
def calculate_house(global_degree, ascendant):
    # Calculate the house based on the planet's position relative to the Ascendant
    house_position = (global_degree - ascendant + 360) % 360
    return int(house_position // 30) + 1  # Each house spans 30 degrees

def calculate_zodiac(global_degree):
    zodiac_no = int(global_degree // 30) + 1  # Each zodiac sign spans 30 degrees
    zodiac_names = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", 
        "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", 
        "Aquarius", "Pisces"
    ]
    return zodiac_names[zodiac_no - 1], zodiac_no

def get_zodiac_lord(zodiac_no):
    zodiac_lords = {
        1: "Mars",      # Aries
        2: "Venus",     # Taurus
        3: "Mercury",   # Gemini
        4: "Moon",      # Cancer
        5: "Sun",       # Leo
        6: "Mercury",   # Virgo
        7: "Venus",     # Libra
        8: "Mars",      # Scorpio
        9: "Jupiter",   # Sagittarius
        10: "Saturn",   # Capricorn
        11: "Saturn",   # Aquarius
        12: "Jupiter"   # Pisces
    }
    return zodiac_lords.get(zodiac_no, "Unknown")

def is_exalted(planet_name, position):
    exaltation_degrees = {
        "Sun": 10,    # Aries
        "Moon": 3,    # Taurus
        "Mars": 28,   # Capricorn
        "Mercury": 15, # Virgo
        "Jupiter": 5, # Cancer
        "Venus": 27,  # Pisces
        "Saturn": 20, # Libra
    }
    return abs(position - exaltation_degrees.get(planet_name, 0)) < 5  # Example threshold

def check_combustion(planet_name, global_degree, sun_degree):
    return abs(global_degree - sun_degree) < 6  # Example threshold

def check_planet_set(global_degree):
    return global_degree >= 210  # Example threshold for being set

def get_lord_status(planet_name):
    return "Benefic" if planet_name in ["Jupiter", "Venus"] else "Malefic"

def get_nakshatra_lord(nakshatra):
    nakshatra_lords = {
        "Ashwini": "Ketu",
        "Bharani": "Venus",
        "Krittika": "Sun",
        "Rohini": "Moon",
        "Mrigashirsha": "Mars",
        "Ardra": "Rahu",
        "Punarvasu": "Jupiter",
        "Pushya": "Saturn",
        "Ashlesha": "Mercury",
        "Maghā": "Ketu",
        "Pūrva Phalgunī": "Venus",
        "Uttara Phalgunī": "Sun",
        "Hasta": "Mercury",
        "Chitra": "Venus",
        "Swati": "Rahu",
        "Vishakha": "Jupiter",
        "Anuradha": "Saturn",
        "Jyeshtha": "Mercury",
        "Mula": "Ketu",
        "Pūrva Ashadha": "Venus",
        "Uttara Ashadha": "Sun",
        "Shravana": "Moon",
        "Dhanishta": "Mars",
        "Shatabhisha": "Rahu",
        "Pūrva Bhadrapada": "Jupiter",
        "Uttara Bhadrapada": "Saturn",
        "Revati": "Mercury"
    }
    return nakshatra_lords.get(nakshatra, "Unknown")

def is_own_sign(planet_name, position):
    own_sign_degrees = {
        "Sun": 0,     # Leo
        "Moon": 0,    # Cancer
        "Mars": 0,    # Aries, Scorpio
        "Mercury": 0, # Gemini, Virgo
        "Jupiter": 0, # Sagittarius, Pisces
        "Venus": 0,   # Taurus, Libra
        "Saturn": 0,  # Capricorn, Aquarius
    }
    return position // 30 == own_sign_degrees.get(planet_name, -1)

def get_avastha_name(planet_name, house, is_exalted, is_own_sign):
    if house in [1, 4, 7, 10]:  # Strong houses
        return "Kumara"  # Change to Kumara for strong houses
    elif is_exalted or is_own_sign:
        return "Bala"  # Exalted or own sign
    elif house in [6, 8, 12]:  # Weak houses
        return "Mrityu"  # Change to Mrityu for weak houses
    else:
        return "Vriddha"  # Default case for other houses

def calculate_nakshatra_pada(global_degree):
    degree_within_nakshatra = global_degree % 13.3333
    return int(degree_within_nakshatra // (13.3333 / 4)) + 1  # 4 padas per nakshatra

def calculate_houses(planet_position):
    # Calculate the house number based on the planet's position
    
    # Each house spans 30 degrees
    house_number = (planet_position // 30) + 1
    return house_number

def calculate_mangal_dosh(planetary_positions, dob):
    mars_position = planetary_positions.get("Mars")
    if mars_position is None:
        return {
            "is_dosha_present": False,
            "bot_response": "Mars position not available.",
            "percentage": 0
        }
    
    # Calculate the house number for Mars
    mars_house = calculate_houses(mars_position)

    # Houses that indicate Mangal Dosh
    mangal_dosh_houses = [1, 4, 7, 8, 12]
    is_dosha_present = mars_house in mangal_dosh_houses

    # Common factors for Mangal Dosh
    factors = [
        "House Placement" ":" "Mangal Dosh arises when Mars is positioned in specific houses: 1st, 4th, 7th, 8th, or 12th in the natal chart.",
        "Impact on Relationships" ":" "It is commonly believed that Mangal Dosh can lead to difficulties in marriage, including delays, conflicts, and potential mismatches.",
        "Mars Influence" ":" "The presence of Mangal Dosh indicates a strong influence of Mars, which may manifest as aggression, impulsiveness, or strong desires in personal relationships.",
        "Health Concerns" ":" "Some astrologers suggest that individuals with Mangal Dosh may face health issues related to blood pressure, injuries, or surgeries.",
        "Financial Instability" ":" "There is a belief that Mangal Dosh can lead to financial instability or unexpected expenses, particularly in the context of partnerships.",
        "Karmic Implications" ":" "Mangal Dosh is sometimes viewed as a karmic lesson, suggesting that individuals may need to work through past life issues related to aggression or conflict."
    ]
     

    if is_dosha_present:
        # Calculate percentage based on the house's index in the Mangal Dosh houses
        percentage = (mangal_dosh_houses.index(mars_house) + 1) * (100 / len(mangal_dosh_houses))
        
        # Remedies for Mangal Dosh
        remedies = [
            "Perform Mangal Dosh Nivaran Puja.",
            "Offer red flowers to Lord Hanuman or Lord Ganesha.",
            "Recite Mangal Dosh removal mantras, such as the Mangal Gayatri Mantra.",
            "Donate red items (like lentils, cloth, etc.) on Tuesdays.",
            "Wear a coral gemstone after consulting an astrologer.",
            "Fast on Tuesdays to appease Mars."
        ]

        return {
            "is_dosha_present": True,
            "bot_response": "Yes, Mangal Dosh exists in your Kundali.",
            "percentage": percentage,
            "factors": factors,
            "remedies": remedies
        }
    else:
        return {
            "is_dosha_present": False,
            "bot_response": "No Mangal Dosh exists in your Kundali.",
            "percentage": 0,
            "factors": factors
        }
def generate_aspects_and_factors(planet_positions):
    aspects = []
    factors = []

    # Logic for determining aspects based on planetary positions
    for planet, position in planet_positions.items():
        if planet == "Rahu":
            if position == 1:
                aspects.append("Rahu in the 1st is aspecting the 7th")
                factors.append("manglik dosha is created by rahu-ketu in 1-7 axis.")
        elif planet == "Ketu":
            if position == 7:
                aspects.append("Ketu in the 7th is aspecting the 1st")
        elif planet == "Mars":
            if position in [1, 2]:
                aspects.append(f"Mars in the {position} is aspecting the {position + 6}")
                factors.append(f"Manglik dosha is created by Mars in the {position} house in Lagna chart.")
        elif planet == "Saturn":
            if position == 10:
                factors.append("Saturn's position may influence Manglik dosha.")

    return aspects, factors


def calculate_manglik_dosh(planet_positions):
    aspects, factors = generate_aspects_and_factors(planet_positions)

    # Initialize the response structure
    response = {
        "dosha_manglik_dosh": {},
        "aspects": aspects,
        "factors": factors,
        "bot_response": "",
        "manglik_by_mars": False,
        "manglik_by_rahuketu": False,
        "manglik_by_saturn": False,
        "score": 0
    }

    # Scoring logic
    score = 0

    # Check for Mars-related aspects
    if any("Mars" in aspect for aspect in aspects):
        response["manglik_by_mars"] = True
        score += 30  # Points for Mars aspect

    # Check for Rahu-Ketu aspects
    if any("Rahu" in aspect and "Ketu" in aspect for aspect in aspects):
        response["manglik_by_rahuketu"] = True
        score += 20  # Points for Rahu-Ketu aspect

    # Check factors for specific placements and associations
    if any("Mars in the" in factor for factor in factors):
        score += 15  # Points for specific Mars placement
    if any("rahu-ketu in 1-7 axis" in factor for factor in factors):
        score += 10  # Points for Rahu-Ketu axis

    # Check for Saturn (example condition)
    if any("Saturn" in factor for factor in factors):
        response["manglik_by_saturn"] = True
        score += 5  # Points for Saturn (if any)

    # Final score calculation
    response["score"] = min(score, 100)  # Cap at 100%

    # Generate bot response
    response["bot_response"] = f"You are {response['score']}% manglik."

    # Return the response structure
    return response


# Define the Nakshatras and their indices
nakshatras = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra",
    "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
    "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

def calculate_moon_position(dob, tob, lat, lon):
    # Combine date of birth and time of birth
    birth_datetime = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    
    # Use PyEphem to calculate the Moon's position
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.date = birth_datetime
    
    # Get the Moon's position
    moon = ephem.Moon(observer)
    moon_position = moon.ecliptic_long  # Moon's position in degrees
    
    # Calculate Nakshatra index (each Nakshatra spans 13°20' or 13.33 degrees)
    nakshatra_index = int(moon_position // 13.333)
    
    # Get the Nakshatra name
    moon_nakshatra = nakshatras[nakshatra_index]
    
    return moon_nakshatra, nakshatra_index

def calculate_pitra_dosh(planetary_positions):
    # Extract positions
    mars_position = planetary_positions.get("Mars", None)
    rahu_position = planetary_positions.get("Rahu", None)
    saturn_position = planetary_positions.get("Saturn", None)
    sun_position = planetary_positions.get("Sun", None)
    moon_position = planetary_positions.get("Moon", None)

    # Initialize Pitra Dosh response
    pitra_dosh_info = {
        "dosha_pitra-dosh": {
            "bot_response": "",
            "effects": [],
            "is_dosha_present": False,
            "remedies": []
        }
    }

    # Check for Pitra Dosh conditions
    if (saturn_position in [sun_position, moon_position]) or \
       (rahu_position in [sun_position, moon_position]) or \
       (saturn_position == rahu_position) or \
       (mars_position in [sun_position, moon_position]):  # Added Mars condition for completeness
        pitra_dosh_info["dosha_pitra-dosh"]["is_dosha_present"] = True

        # Populate bot response, effects, and remedies if Pitra Dosh is present
        pitra_dosh_info["dosha_pitra-dosh"]["bot_response"] = "Pitra dosha happens when Saturn / Rahu is conjunct or aspects Sun or Moon. This occurs in your horoscope and thus this dosha is present in your birth chart."
        
        pitra_dosh_info["dosha_pitra-dosh"]["effects"] = [
            "Children may face mental and physical disabilities.",
            "Unfavorable environment and arguments with the life partner.",
            "Delay in marriage.",
            "Financial and physical problems due to continuous sickness.",
            "Struggles to achieve success in various endeavors.",
            "Continuous scarcity and financial issues.",
            "Dreams related to snakes may indicate this dosha.",
            "Dreams of ancestors asking for food or clothing."
        ]

        pitra_dosh_info["dosha_pitra-dosh"]["remedies"] = [
            "Offer water to a Banyan tree regularly.",
            "Keep fasts to mitigate the effects of the dosha.",
            "Organize Pooja or Mantra Jap to nullify past sins.",
            "Feed Brahmins on every Amavasya.",
            "Donate food, blankets, and clothes on Ardh-Kumbha-Snaan day.",
            "Feed cows, street dogs, crows, and ants.",
            "Perform Trapandi Shraad.",
            "Help the poor, needy, and elderly as much as possible.",
            "Chant Devi Kaalika Stotram mantras, especially during Navratri.",
            "Take a holy dip in places like Ujjain, Nasik, Ganga Sagar, Haridwar.",
            "Offer water mixed with sesame seeds to the rising Sun and chant Gayatri Mantra."
        ]
    else:
        pitra_dosh_info["dosha_pitra-dosh"]["bot_response"] = "No Pitra Dosh is present in your horoscope."
        pitra_dosh_info["dosha_pitra-dosh"]["effects"].append("No specific effects are observed.")
        pitra_dosh_info["dosha_pitra-dosh"]["remedies"].append("No specific remedies are required.")

    return pitra_dosh_info

def calculate_dasha_predictions(dob, tob, lat, lon):
    # Step 1: Calculate Moon's position and Nakshatra
    moon_nakshatra, nakshatra_index = calculate_moon_position(dob, tob, lat, lon)
    
    # Step 2: Get Dasha durations based on Nakshatra
    dasha_durations = get_dasha_durations(nakshatra_index)
    
    # Start date for Dasha calculation
    start_date = datetime.strptime(dob, "%d/%m/%Y")
    
    # Calculate Dasha predictions
    dasha_predictions = []
    dasha_start_date = start_date
    
    for planet, duration in dasha_durations.items():
        dasha_end_date = dasha_start_date + timedelta(days=duration * 365.25)  # Approximate days in a year
        
        # Generate a prediction for each Dasha
        prediction = generate_prediction(planet)
        
        dasha_predictions.append({
            "dasha": planet,
            "dasha_start_year": dasha_start_date.strftime("%A %b %d %Y"),
            "dasha_end_year": dasha_end_date.strftime("%A %b %d %Y"),
            "planet_in_zodiac": f"{planet} in {get_zodiac_sign(dasha_start_date)}: {get_zodiac_description(planet)}",
            "prediction": prediction
        })
        
        # Move to the next Dasha start date
        dasha_start_date = dasha_end_date

    return dasha_predictions


def generate_prediction(planet):
    # Generate a prediction based on the planet
    predictions = {
        "Rahu": "With Rahu in your chart, you are likely to have an insatiable desire for recognition and status. You thrive in roles that place you at the forefront, where your talents can shine. This placement often drives you to seek unconventional paths, and you may find yourself drawn to careers in media, politics, or any field that allows you to influence public perception. However, be cautious of becoming overly ambitious; balance your desire for success with humility to avoid potential pitfalls.",
        "Jupiter": "Jupiter’s influence suggests a profound spiritual connection, particularly with your mother or maternal figures. This placement often indicates a nurturing relationship that fosters your personal growth and wisdom. You may find yourself drawn to philosophical pursuits or teaching, as sharing knowledge becomes a significant part of your life. Embrace opportunities for learning and growth, as they will lead you to deeper understanding and fulfillment.",
        "Saturn": "Saturn in your chart bestows a serious and disciplined approach to life. You likely possess a strong work ethic and a commitment to your studies or career. This placement encourages you to take responsibility and face challenges head-on, which can lead to significant achievements over time. However, be mindful of becoming too rigid or pessimistic; allowing for flexibility and optimism can enhance your overall well-being.",
        "Mercury": "With Mercury influencing your chart, communication is key to your success. You excel in roles that require clear expression of ideas, whether in writing, speaking, or teaching. This placement often indicates a quick intellect and a knack for problem-solving. You may find yourself gravitating towards careers in journalism, marketing, or education. Embrace your curiosity and continue to seek knowledge, as it will serve you well in both personal and professional realms.",
        "Ketu": "Ketu’s placement suggests a career path that may undergo significant transformation. You might find yourself drawn to spiritual or humanitarian pursuits, often feeling a calling to serve others. This placement can indicate a tendency to detach from material concerns, seeking deeper meaning in your work. Embrace this transformative journey, as it can lead to profound personal growth and fulfillment. Remember to balance your spiritual pursuits with practical considerations.",
        "Venus": "With Venus in your chart, you are likely to attract wealth through creative endeavors or large organizations. This placement suggests a natural affinity for beauty, art, and aesthetics, which can translate into lucrative careers in design, fashion, or the arts. Your charm and social skills may also open doors in business and networking. Cultivate your artistic talents and foster relationships, as both will play a crucial role in your financial success.",
        "Sun": "The Sun’s influence indicates a strong desire for authority and recognition. You are likely to pursue leadership roles, where your confidence and charisma can shine. This placement often suggests a career in management, politics, or any field where you can assert your influence. Embrace your natural leadership abilities, but be cautious of becoming overly egotistical; grounding yourself in humility will enhance your effectiveness as a leader.",
        "Moon": "With the Moon influencing your career path, you may find success in family-oriented businesses or roles that nurture others. This placement suggests a deep emotional connection to your work, often leading you to fields such as healthcare, education, or hospitality. Your intuition and empathy will guide you in making decisions that benefit both yourself and those around you. Embrace your nurturing qualities, as they will be key to your professional fulfillment.",
        "Mars": "Mars in your chart signifies a strong drive for achievement, particularly in higher education or research. You are likely to put in considerable effort towards your studies or professional development, often excelling in competitive environments. This placement suggests a career in fields such as sports, military, or any area that requires determination and courage. Channel your energy effectively, as it will propel you toward your goals."
    }
    return predictions.get(planet, "No prediction available.")

def get_zodiac_sign(date):
    # Determine zodiac sign based on the date
    month = date.month
    day = date.day
    if (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "Aquarius"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "Pisces"
    elif (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "Aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "Taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "Gemini"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "Cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "Scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "Sagittarius"
    else:
        return "Capricorn"

def get_zodiac_description(planet):
    # Provide a description based on the planet's zodiac sign
    descriptions = {
        "Rahu": "A mix of wisdom and duality.",
        "Jupiter": "Wisdom stabilizes emotions.",
        "Saturn": "Resilience and hard work.",
        "Mercury": "Communication and intellect.",
        "Ketu": "Confusion and independence.",
        "Venus": "Emotional connections and creativity.",
        "Sun": "Intelligence and debate.",
        "Moon": "Balance and relationships.",
        "Mars": "Emotional strength and independence."
    }
    return descriptions.get(planet, "No description available.")
def get_dasha_durations(nakshatra_index):
    # Dasha durations for each planet in Vimshottari Dasha
    dasha_durations = {
    0: {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17},  # Ashwini
    1: {"Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17, "Ketu": 7},  # Bharani
    2: {"Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20},  # Krittika
    3: {"Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20, "Sun": 6},  # Rohini
    4: {"Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10},  # Mrigashira
    5: {"Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7},  # Ardra
    6: {"Jupiter": 16, "Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18},  # Punarvasu
    7: {"Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16},  # Pushya
    8: {"Mercury": 17, "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19},  # Ashlesha
    9: {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17},  # Magha
    10: {"Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17, "Ketu": 7},  # Purva Phalguni
    11: {"Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20},  # Uttara Phalguni
    12: {"Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20, "Sun": 6},  # Hasta
    13: {"Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10},  # Chitra
    14: {"Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7},  # Swati
    15: {"Jupiter": 16, "Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18},  # Vishakha
    16: {"Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16},  # Anuradha
    17: {"Mercury": 17, "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19},  # Jyeshtha
    18: {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17},  # Mula
    19: {"Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17, "Ketu": 7},  # Purva Ashadha
    20: {"Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20},  # Uttara Ashadha
    21: {"Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20, "Sun": 6},  # Shravana
    22: {"Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10},  # Dhanishta
    23: {"Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7},  # Shatabhisha
    24: {"Jupiter": 16, "Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18},  # Purva Bhadrapada
    25: {"Saturn": 19, "Mercury": 17, "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16},  # Uttara Bhadrapada
    26: {"Mercury": 17, "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19}   # Revati
}

    return dasha_durations.get(nakshatra_index, {})

# def get_dasha_periods():
#     return {
#         "Ketu": 7,
#         "Venus": 20,
#         "Sun": 6,
#         "Moon": 10,
#         "Mars": 7,
#         "Rahu": 18,
#         "Jupiter": 16,
#         "Saturn": 19,
#     }

def get_nakshatra_and_dasha_start(moon_position):
    nakshatras = [
        ("Ashwini", "Ketu"),
        ("Bharani", "Venus"),
        ("Krittika", "Sun"),
        ("Rohini", "Moon"),
        ("Mrigashira", "Mars"),
        ("Ardra", "Rahu"),
        ("Punarvasu", "Jupiter"),
        ("Pushya", "Saturn"),
        ("Ashlesha", "Ketu"),
        ("Magha", "Rahu"),
        ("Purva Phalguni", "Venus"),
        ("Uttara Phalguni", "Sun"),
        ("Hasta", "Moon"),
        ("Chitra", "Mars"),
        ("Swati", "Rahu"),
        ("Vishakha", "Jupiter"),
        ("Anuradha", "Saturn"),
        ("Jyeshtha", "Mercury"),
        ("Mula", "Ketu"),
        ("Purva Ashadha", "Venus"),
        ("Uttara Ashadha", "Sun"),
        ("Shravana", "Moon"),
        ("Dhanishta", "Mars"),
        ("Shatabhisha", "Rahu"),
        ("Purva Bhadrapada", "Jupiter"),
        ("Uttara Bhadrapada", "Saturn"),
        ("Revati", "Mercury"),
    ]

    # Determine Nakshatra based on moon position
    nakshatra_index = int(moon_position // 13.333)  # Each Nakshatra spans 13°20'
    nakshatra_name, dasha_start_planet = nakshatras[nakshatra_index]

    return nakshatra_name, dasha_start_planet

def calculate_moon_position(dob, tob, lat, lon):
    # Combine date of birth and time of birth
    birth_datetime = datetime.strptime(f"{dob} {tob}", "%d/%m/%Y %H:%M")
    
    # Use PyEphem to calculate the Moon's position
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.date = birth_datetime
    
    # Get the Moon's position
    moon = ephem.Moon(observer)
    
    # Convert the Moon's right ascension to degrees
    moon_position = moon.a_ra * (180.0 / np.pi)  # Convert from radians to degrees
    
    # Calculate Moon sign index (each zodiac sign spans 30 degrees)
    moon_sign_index = int(moon_position // 30)  # Each zodiac sign spans 30 degrees
    moon_signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", 
        "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", 
        "Aquarius", "Pisces"
    ]
    moon_sign = moon_signs[moon_sign_index]

    return moon_sign, moon_sign_index


def calculate_sun_position(dob, tob, lat, lon):
    # Combine date of birth and time of birth
    birth_datetime = datetime.strptime(f"{dob} {tob}", "%d/%m/%Y %H:%M")
    
    # Use PyEphem to calculate the Sun's position
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.date = birth_datetime
    
    # Get the Sun's position
    sun = ephem.Sun(observer)
    
    # Convert the Sun's right ascension to degrees
    sun_position = sun.a_ra * (180.0 / np.pi)  # Convert from radians to degrees
    
    # Calculate Sun sign
    sun_sign_index = int(sun_position // 30)  # Each zodiac sign spans 30 degrees
    sun_signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", 
        "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", 
        "Aquarius", "Pisces"
    ]
    sun_sign = sun_signs[sun_sign_index]

    return sun_sign




def calculate_maha_dasha(dob, tob,lat,lon):
    # Fetch Dasha periods dynamically
    dasha_periods = get_dasha_durations()

    # Calculate Moon's position
    moon_nakshatra, starting_planet = calculate_moon_position(dob, tob,lon,lat)  # Pass lat and lon

    total_years = sum(dasha_periods.values())
    
    # Parse birth date and time of birth
    start_date = datetime.strptime(dob, "%d/%m/%Y")  # Birth date
    current_time = datetime.strptime(tob, "%H:%M")  # Time of birth
    current_date = datetime.combine(start_date.date(), current_time.time())  # Combine date and time

    # Calculate remaining Dasha at birth
    dasha_remaining = {}
    dasha_start_date = start_date

    # Find the starting point based on the Nakshatra
    for planet, duration in dasha_periods.items():
        if planet == starting_planet:
            break
        dasha_start_date += timedelta(days=duration * 365.25)  # Move to the next Dasha

    # Calculate remaining Dasha at birth
    for planet, duration in dasha_periods.items():
        dasha_end_date = dasha_start_date + timedelta(days=duration * 365.25)  # Approximate days in a year
        if dasha_end_date > current_date:
            days_remaining = (dasha_end_date - current_date).days
            dasha_remaining['years'] = days_remaining // 365
            dasha_remaining['months'] = (days_remaining % 365) // 30
            dasha_remaining['days'] = days_remaining % 30
            break
        dasha_start_date = dasha_end_date

    maha_dasha_order = []
    dasha_start_dates = []

    dasha_start_date = start_date
    for planet, duration in dasha_periods.items():
        dasha_start_dates.append(dasha_start_date.strftime("%A %b %d %Y"))
        maha_dasha_order.append(planet)
        dasha_start_date += timedelta(days=duration * 365.25)  # Approximate days in a year

    return {
        "nakshatra": moon_nakshatra,
        "starting_planet": starting_planet,
        "dasha_remaining_at_birth": f"{dasha_remaining.get('years', 0)} years {dasha_remaining.get('months', 0)} months {dasha_remaining.get('days', 0)} days",
        "dasha_start_date": dasha_start_dates[0],
        "mahadasha": maha_dasha_order,
        "mahadasha_order": dasha_start_dates
    }

# Define colors for each planet
planet_colors = {
    "Mercury": "green",
    "Mars": "red",
    "Saturn": "darkgreen",
    "Venus": "pink",
    "Rahu": "darkblue",
    "Ketu": "purple",
    "Jupiter": "orange",
    "Moon": "grey",
    "Sun": "gold"
}
def calculate_global_degree(local_degree, house):
    """
    Calculates the global degree of a planet based on its local degree and house position.
    """
    global_degree = local_degree + (house - 1) * 30
    return global_degree

# Calculate Lagna and Planetary Positions
def calculate_lagna(birth_date, birth_time, latitude, longitude):
    birth_datetime = datetime.combine(birth_date, birth_time)
    julian_day = swe.julday(birth_datetime.year, birth_datetime.month,
                             birth_datetime.day, birth_datetime.hour + birth_datetime.minute / 60.0)
    sidereal_time = swe.sidtime(julian_day) + (longitude / 15.0)
    lagna = (sidereal_time * 15 + 360) % 360
    rasi_number = int(lagna // 30) + 1
    return lagna, rasi_number

def calculate_karana(tithi):
    # Calculate Karana based on Tithi (simplified logic)
    karanas = [
        "Bava", "Balava", "Kaulava", "Taitula", "Garaja", 
        "Vanija", "Vishti", "Shakuni", "Chatushpad", "Nagava", 
        "Kintughna", "Karan", "Kula", "Naga"
    ]
    tithi_index = int(tithi) % 11
    return karanas[tithi_index]
    
    # return [tithi_index]
def calculate_sunrise_sunset(lat, lon, birth_datetime):
    # Using ephem to calculate sunrise and sunset times
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.date = birth_datetime

    sunrise = observer.next_rising(ephem.Sun()).datetime()
    sunset = observer.next_setting(ephem.Sun()).datetime()

    return sunrise.strftime("%H:%M:%S"), sunset.strftime("%H:%M:%S")

def calculate_dasha_predictions(dob, tob, lat, lon):
    # Step 1: Calculate Moon's position and Nakshatra
    moon_nakshatra, nakshatra_index = calculate_moon_position(dob, tob, lat, lon)
    
    # Step 2: Get Dasha durations based on Nakshatra
    dasha_durations = get_dasha_durations(nakshatra_index)
    
    # Start date for Dasha calculation
    start_date = datetime.strptime(dob, "%d/%m/%Y")
    
    # Calculate Dasha predictions
    dasha_predictions = []
    dasha_start_date = start_date
    
    for planet, duration in dasha_durations.items():
        dasha_end_date = dasha_start_date + timedelta(days=duration * 365.25)  # Approximate days in a year
        
        # Generate a prediction for each Dasha
        prediction = generate_prediction(planet)
        
        dasha_predictions.append({
            "dasha": planet,
            "dasha_start_year": dasha_start_date.strftime("%A %b %d %Y"),
            "dasha_end_year": dasha_end_date.strftime("%A %b %d %Y"),
            "planet_in_zodiac": f"{planet} in {get_zodiac_sign(dasha_start_date)}: {get_zodiac_description(planet)}",
            "prediction": prediction
        })
        
        # Move to the next Dasha start date
        dasha_start_date = dasha_end_date

    return {
        "dasha_char_dasha_current": {
            "main_dasha": list(dasha_durations.keys())[0],  # Example for main Dasha
            "main_dasha_lord": list(dasha_durations.keys())[0],  # Example for main Dasha lord
            "sub_dasha_end_dates": [dasha["dasha_end_year"] for dasha in dasha_predictions],
            "sub_dasha_list": [dasha["dasha"] for dasha in dasha_predictions],
            "sub_dasha_start_date": dasha_predictions[0]["dasha_start_year"]  # Example for start date of first sub Dasha
        },
        "dasha_char_dasha_main": {
            "dasha_end_dates": [dasha["dasha_end_year"] for dasha in dasha_predictions],
            "dasha_list": [dasha["dasha"] for dasha in dasha_predictions],
            "start_date": start_date.strftime("%A %b %d %Y")
        },
        "dasha_maha_dasha_predictions": {
            "dashas": dasha_predictions
        }
    }

def calculate_planet_positions(dob, tob, lat, lon):
    """Calculate planetary positions based on date of birth, time of birth, latitude, and longitude."""
    # Combine date of birth and time of birth into a single datetime object
    birth_datetime = datetime.combine(dob, tob)
    
    # Calculate Julian Day
    julian_day = swe.julday(birth_datetime.year, birth_datetime.month,
                             birth_datetime.day, birth_datetime.hour + birth_datetime.minute / 60.0)

    # Define planets and their corresponding IDs
    planets = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Mars': swe.MARS,
        'Mercury': swe.MERCURY,
        'Jupiter': swe.JUPITER,
        'Venus': swe.VENUS,
        'Saturn': swe.SATURN,
        'Rahu': swe.MEAN_NODE,
        'Ketu': swe.TRUE_NODE
    }
    
    # Initialize a dictionary to store planet positions
    planet_positions = {}
    
    # Calculate positions for each planet
    for planet, planet_id in planets.items():
        # Calculate the position of the planet
        position = swe.calc_ut(julian_day, planet_id)[0][0]
        # Normalize the position to be within 0-360 degrees
        planet_positions[planet] = position % 360
    
    # Return the dictionary of planet positions
    return planet_positions



def rasi_and_house(planet_positions):
    rasi_info = {}
    for planet, position in planet_positions.items():
        rasi_number = int(position // 30) + 1
        house_number = rasi_number  # Assuming Lagna is the first house
        rasi_info[planet] = {
            'Rasi Number': rasi_number,
            'House Number': house_number
        }
    return rasi_info

def calculate_horoscope_data(dob, tob, lat, lon):
    # Parse date of birth and time of birth
    birth_date = datetime.strptime(dob, "%d/%m/%Y").date()  # Ensure dob is a date object
    birth_time = datetime.strptime(tob, "%H:%M").time()     # Ensure tob is a time object

    # Now call the planet positions calculation with the correct types
    planet_positions = calculate_planet_positions(birth_date, birth_time, lat, lon)

    # Calculate Lagna and its Rasi number
    lagna, lagna_rasi_number = calculate_lagna(birth_date, birth_time, lat, lon)

    # Get Rasi and House information for each planet
    rasi_info = rasi_and_house(planet_positions)

    return lagna, lagna_rasi_number, planet_positions, rasi_info  # Now returns four values



planet_colors = {
    "Mercury": "green",
    "Mars": "red",
    "Saturn": "darkred",
    "Venus": "pink",
    "Rahu": "darkblue",
    "Ketu": "purple",
    "Jupiter": "orange",
    "Moon": "grey",
    "Sun": "gold"
}

# Abbreviated names for planets
abbreviated_names = {
    "Mercury": "Me",
    "Mars": "Ma",
    "Saturn": "Sa",
    "Venus": "Ve",
    "Rahu": "Ra",
    "Ketu": "Ke",
    "Jupiter": "Ju",
    "Moon": "Mo",
    "Sun": "Su"
}
def calculate_tatva(rasi):
    fire_rasis = ["Aries", "Leo", "Sagittarius"]
    earth_rasis = ["Taurus", "Virgo", "Capricorn"]
    air_rasis = ["Gemini", "Libra", "Aquarius"]
    water_rasis = ["Cancer", "Scorpio", "Pisces"]

    if rasi in fire_rasis:
        return "Fire"
    elif rasi in earth_rasis:
        return "Earth"
    elif rasi in air_rasis:
        return "Air"
    elif rasi in water_rasis:
        return "Water"
    else:
        return "Unknown"  # Fallback case
 
def calculate_hora_lord(birth_datetime):
    # Determine Hora Lord based on the day of the week
    day_of_week = birth_datetime.strftime("%A")
    hora_lord_mapping = {
        "Monday": "Moon",
        "Tuesday": "Mars",
        "Wednesday": "Mercury",
        "Thursday": "Jupiter",
        "Friday": "Venus",
        "Saturday": "Saturn",
        "Sunday": "Sun"
    }
    return hora_lord_mapping.get(day_of_week, "Unknown")
def calculate_yoga(tithi):
    # Calculate Yoga based on the Tithi (simplified logic)
    yogas = [
        "Vishkumbh", "Priti", "Ayushman", "Saubhagya", "Shobhan", 
        "Atiganda", "Sukarman", "Dhriti", "Shula", "Gandha", 
        "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", 
        "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva", 
        "Siddha", "Sadhya", "Shubha", "Shukla"
    ]
    #  Calculate the index based on tithi
    tithi_index = (tithi - 1) % len(yogas)  # Ensure it's within bounds

    if tithi_index < 0 or tithi_index >= len(yogas):
        raise ValueError(f"Invalid tithi index: {tithi_index}")

    return yogas[tithi_index]  # There are 27 Yogas

def calculate_panchang(dob, tob, lat, lon):
    # Parse date of birth and time of birth
    birth_date = datetime.strptime(dob, "%d/%m/%Y").date()
    birth_time = datetime.strptime(tob, "%H:%M").time()
    
    # Combine date and time into a datetime object
    birth_datetime = datetime.combine(birth_date, birth_time)

    # Calculate Julian Day
    julian_day = (birth_datetime - datetime(2000, 1, 1)).days + 2451545

    # Tithi Calculation (Lunar Day)
    tithi = (julian_day % 30) + 1  # Simplified calculation (1 to 30)
    
    # Nakshatra Calculation
    nakshatra_index = int((julian_day * 27) % 27)  # Simplified calculation
    nakshatras = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", 
        "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Maghā", 
        "Pūrva Phalgunī", "Uttara Phalgunī", "Hasta", "Chitra", 
        "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", 
        "Pūrva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", 
        "Shatabhisha", "Pūrva Bhadrapada", "Uttara Bhadrapada", 
        "Revati"
    ]
    
    nakshatra = nakshatras[nakshatra_index]

    # Calculate Rasi
    rasi_index = (nakshatra_index // 3) % 12  # Simplified mapping from Nakshatra to Rasi
    rasis = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", 
        "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", 
        "Aquarius", "Pisces"
    ]
    rasi = rasis[rasi_index]

    # Calculate lucky number
    lucky_num = (tithi % 9) + 1  # Example calculation for lucky number

    # Determine lucky colors, gems, letters, etc.
    lucky_colors = {
        "Aries": ["red", "orange"],
        "Taurus": ["green", "pink"],
        "Gemini": ["yellow", "light green"],
        "Cancer": ["white", "silver"],
        "Leo": ["gold", "orange"],
        "Virgo": ["brown", "green"],
        "Libra": ["blue", "pink"],
        "Scorpio": ["red", "black"],
        "Sagittarius": ["purple", "blue"],
        "Capricorn": ["dark green", "brown"],
        "Aquarius": ["blue", "electric blue"],
        "Pisces": ["light blue", "green"]
    }.get(rasi, ["silver grey"])  # Default if not found

    lucky_gems = {
        "Aries": ["Red Coral"],
        "Taurus": ["Emerald"],
        "Gemini": ["Pearl"],
        "Cancer": ["Moonstone"],
        "Leo": ["Ruby"],
        "Virgo": ["Emerald"],
        "Libra": ["Diamond"],
        "Scorpio": ["Red Coral"],
        "Sagittarius": ["Yellow Sapphire"],
        "Capricorn": ["Blue Sapphire"],
        "Aquarius": ["Garnet"],
        "Pisces": ["Aquamarine"]
    }.get(rasi, ["yellow sapphire"])  # Default if not found

    lucky_letters = {
        "Ashwini": ["A", "E"],
        "Bharani": ["B", "V"],
        "Krittika": ["A", "I"],
        "Rohini": ["O", "W"],
        "Mrigashirsha": ["M", "D"],
        "Ardra": ["A", "N"],
        "Punarvasu": ["P", "R"],
        "Pushya": ["S", "H"],
        "Ashlesha": ["S", "Z"],
        "Maghā": ["M", "Y"],
        "Pūrva Phalgunī": ["F", "B"],
        "Uttara Phalgunī": ["T", "P"],
        "Hasta": ["H", "R"],
        "Chitra": ["C", "L"],
        "Swati": ["R", "D"],
        "Vishakha": ["V", "K"],
        "Anuradha": ["A", "T"],
        "Jyeshtha": ["J", "N"],
        "Mula": ["M", "Y"],
        "Pūrva Ashadha": ["A", "T"],
        "Uttara Ashadha": ["U", "D"],
        "Shravana": ["S", "H"],
        "Dhanishta": ["D", "N"],
        "Shatabhisha": ["S", "B"],
        "Pūrva Bhadrapada": ["P", "R"],
        "Uttara Bhadrapada": ["U", "D"],
        "Revati": ["R", "D"]
    }.get(nakshatra, ["S", "D"])  # Default if not found

    # Placeholder values for Ayanamsa, Hora Lord, Karana, Sunrise/Sunset
    # ayanamsa = calculate_ayanamsa(birth_datetime,tob)  # Calculate Ayanamsa
    # ayanamsa_name = "Lahiri"  # Example Ayanamsa name
    hora_lord = calculate_hora_lord(birth_datetime)  # Calculate Hora Lord
    karana = calculate_karana(tithi)  # Calculate Karana
    sunrise_at_birth, sunset_at_birth = calculate_sunrise_sunset(lat, lon, birth_datetime)  # Calculate Sunrise/Sunset
    yoga = calculate_yoga(tithi)  # Calculate Yoga
    # Calculate Tatva
    tatva = calculate_tatva(rasi)
    global_degree = (julian_day % 360)
    # Compile all Panchang details
    panchang = {
        "day": birth_datetime.strftime("%A"),
        "lord": get_nakshatra_lord(nakshatra),  # Get Nakshatra Lord
        "nakshatra": nakshatra,
        "rasi": rasi,
        "tatva": tatva,  # Placeholder for Tatva, can be derived further
        "tithi": f"{tithi} (Tithi {tithi})",
        "lucky_colors": lucky_colors,
        "lucky_gem": lucky_gems,
        "lucky_letters": lucky_letters,
        "lucky_name_start": lucky_letters,  # Using lucky letters for name starts
        "lucky_num": lucky_num,  # No need to wrap in a list
        "nakshatra_pada": calculate_nakshatra_pada(global_degree),  # Calculate Nakshatra Pada
        # "ayanamsa": ayanamsa,
        # "ayanamsa_name": calculate_ayanamsa(ayanamsa,tob),
        "day_lord": get_zodiac_lord(rasi_index + 1),  # Get the lord of the Rasi
        "day_of_birth": birth_datetime.strftime("%A"),
        "hora_lord": hora_lord,
        "karana": karana,
        "sunrise_at_birth": sunrise_at_birth,
        "sunset_at_birth": sunset_at_birth,
        "yoga": yoga
    }
    
    return panchang

def calculate_sade_sati(dob, tob, lat, lon):
    # Step 1: Calculate planetary positions
    lagna, lagna_rasi_number, planetary_positions, rasi_info = calculate_horoscope_data(dob, tob, lat, lon)
    moon_position = planetary_positions.get("Moon")
    saturn_position = planetary_positions.get("Saturn")
    retrograde_positions = planetary_positions.get("Retrograde", [])

    # Step 2: Determine if currently in Sade Sati
    is_in_sade_sati = False
    if moon_position is not None and saturn_position is not None:
        moon_sign = int(moon_position // 30) + 1  # Moon sign index
        if (saturn_position >= (moon_sign - 1) * 30) and (saturn_position < (moon_sign + 1) * 30):
            is_in_sade_sati = True

    # Step 3: Determine if Saturn is retrograde
    saturn_retrograde = saturn_position in retrograde_positions

    # Step 4: Determine Shani period type
    shani_period_type = is_in_sade_sati  # This can be adjusted based on your logic

    # Step 5: Generate Sade Sati details
    current_date = datetime.now()
    age = (current_date - datetime.strptime(dob, "%d/%m/%Y")).days // 365
    date_considered = current_date.strftime("%b %d %Y")

    description = (
        '''
        "Sadhe Sati refers to the seven-and-a-half year period in which Saturn moves through three signs, the moon sign
        one before the moon and the one after it. Sadhe Sati starts when Saturn (Shani) enters the 12th sign from the birth Moon sign
        and ends when Saturn leaves 2nd sign from the birth Moon sign. Since Saturn approximately takes around two and half years to 
        transit a sign which is called Shanis dhaiya it takes around seven and half year to transit three signs and that is why it is known as Sadhe Sati.
        Generally Sade-Sati comes thrice in a horoscope in the life time - first in childhood, second in youth & third in old-age. First Sade-Sati has effect on education & parents.
        Second Sade-Sati has effect on profession, finance & family. The last one affects health more than anything else."
'''
    )

    remedies = [
        "Chant the Shani Mool Mantra daily 108 times, 'Aum Shan Shanishcharay Namah'",
        "Chant the Shani Mantra from Navagraha Stotra 108 times on Saturdays.",
        "Do fasting, eating only urad dal and chant Shani Chalisa on Saturdays.",
        "Donate urad dal and black clothes to the poor and physically challenged on a Saturday.",
        "Perform Havan on Hanuman Jayanti or Shani Amavasya."
    ]

    return {
        "age": age,
        "bot_response": "You are currently in Sade Sati." if is_in_sade_sati else "You are not currently in Sade Sati.",
        "date_considered": date_considered,
        "description": description,
        "remedies": remedies,  # Remedies are shown regardless of Sade Sati presence
        "is_in_sade_sati": is_in_sade_sati,
        "saturn_retrograde": saturn_retrograde,
        "shani_period_type": shani_period_type,
        "planetary_positions": planetary_positions,
        "ascendant": calculate_ascendant(dob, tob, lat, lon)  # Calculate Ascendant
    }




def fetch_friendship_rules():
    # Automatically fetch friendship rules based on astrological principles
    return {
        "Sun": {"friends": ["Moon"], "enemies": ["Saturn", "Rahu"]},
        "Moon": {"friends": ["Sun", "Jupiter"], "enemies": ["Mars"]},
        "Mars": {"friends": ["Sun"], "enemies": ["Venus", "Saturn"]},
        "Mercury": {"friends": ["Venus"], "enemies": ["Mars"]},
        "Jupiter": {"friends": ["Moon"], "enemies": ["Rahu"]},
        "Venus": {"friends": ["Mercury"], "enemies": ["Mars"]},
        "Saturn": {"friends": [], "enemies": ["Sun", "Moon"]},
        "Rahu": {"friends": [], "enemies": ["Sun", "Jupiter"]},
        "Ketu": {"friends": [], "enemies": []}
    }

def calculate_friendship_dynamics(planetary_positions):
    # Initialize friendship dynamics
    friendships = {
        "friendship_map": {}
    }

    # Fetch friendship rules
    friendship_rules = fetch_friendship_rules()

    # Calculate friendship dynamics based on planetary positions
    for planet in planetary_positions.keys():
        friendships["friendship_map"][planet] = {
            "friends": [],
            "enemies": []
        }

        # Determine friendships and enmities based on rules
        if planet in friendship_rules:
            friendships["friendship_map"][planet]["friends"].extend(friendship_rules[planet]["friends"])
            friendships["friendship_map"][planet]["enemies"].extend(friendship_rules[planet]["enemies"])

    return friendships
def calculate_dasha(dob):
   # Step 1: Calculate Moon's position and Nakshatra
    moon_nakshatra, nakshatra_index = calculate_moon_position(dob, tob, lat, lon)
    # Define Dasha periods and their durations
    dasha_periods=get_dasha_durations(nakshatra_index)
    # Start date for Dasha calculation
    start_date = datetime.strptime(dob, "%d/%m/%Y")
    
    # Calculate the current Dasha based on the birth date
    dasha_start_dates = []
    dasha_end_dates = []
    sub_dasha_list = []
    
    current_date = datetime.now()
    total_years = sum(dasha_periods.values())
    
    # Calculate Dasha and Sub-Dasha
    dasha_start_date = start_date
    for planet, duration in dasha_periods.items():
        dasha_end_date = dasha_start_date + timedelta(days=duration * 365.25)  # Approximate days in a year
        dasha_start_dates.append(dasha_start_date.strftime("%A %b %d %Y"))
        dasha_end_dates.append(dasha_end_date.strftime("%A %b %d %Y"))
        
        # Generate Sub-Dasha (example: divide each Dasha into 12 parts)
        for i in range(12):
            sub_dasha_start = dasha_start_date + timedelta(days=(i * (duration * 365.25 / 12)))
            sub_dasha_end = sub_dasha_start + timedelta(days=(duration * 365.25 / 12))
            sub_dasha_list.append({
                "sub_dasha": f"{planet} {i + 1}",
                "start_date": sub_dasha_start.strftime("%A %b %d %Y"),
                "end_date": sub_dasha_end.strftime("%A %b %d %Y"),
            })
        
        dasha_start_date = dasha_end_date

    return {
        "main_dasha": dasha_periods,
        "main_dasha_lord": dasha_start_dates,
        "sub_dasha_end_dates": dasha_end_dates,
        "sub_dasha_list": sub_dasha_list,
        "sub_dasha_start_date": dasha_start_dates # Example for the first sub Dasha
    }

def get_prediction_for_sign(sign):
    # Define predictions for each Moon and Sun sign
    predictions = {
        "Aries": "Aries, the 1st Sign of the Zodiac, is ruled by Mars, the planet of action and desire. You are known for your leadership qualities, often taking the initiative in both personal and professional settings. Adventurous and energetic, you thrive in environments that allow you to explore new ideas and experiences. Your enthusiasm is contagious, inspiring those around you to join in your pursuits. However, be mindful of your impulsive nature; sometimes, slowing down to consider the consequences can lead to better outcomes.",
        "Taurus": "Taurus, the 2nd Sign, is ruled by Venus, symbolizing beauty and comfort. You value stability and security, often seeking to create a nurturing environment for yourself and loved ones. Your strong sense of determination drives you to achieve your goals, and you take great pleasure in the finer things in life, such as good food, art, and nature. While your steadfastness is a strength, be cautious of becoming too stubborn or resistant to change, flexibility can open new doors for you.",
        "Gemini": "Gemini, the 3rd Sign, is ruled by Mercury, the planet of communication. Characterized by duality and adaptability, you possess a curious mind and a wonderful ability to connect with others. Socializing comes naturally to you, making you a delightful companion in any setting. Your versatility allows you to thrive in various situations, but be wary of scattering your energy too thin; focusing on a few passions can lead to deeper fulfillment.",
        "Cancer": "Cancer, the 4th Sign, is ruled by the Moon, representing emotions and intuition. Devoted to home and family, you are deeply emotional and sensitive, often prioritizing the needs of loved ones above your own. Your nurturing nature makes you a comforting presence, and you cherish the bonds you create. However, be mindful of your tendency to retreat into your shell during tough times; opening up to trusted individuals can provide the support you need.",
        "Leo": "Leo, the 5th Sign, is ruled by the Sun, symbolizing vitality and self-expression. Known for your charisma and leadership, you radiate confidence and ambition, often finding yourself in the spotlight. Your creativity shines in all endeavors, and you inspire others with your passion and enthusiasm. While your strong presence is admirable, be cautious of becoming overly proud or demanding; humility can enhance your relationships and personal growth.",
        "Virgo": "Virgo, the 6th Sign, is ruled by Mercury, focusing on intellect and analysis. Practical and detail-oriented, you possess a keen analytical mind that excels in problem-solving. Your dedication to hard work and service to others is commendable, making you a reliable friend and colleague. However, be aware of your tendency to be overly critical, both of yourself and others; practicing self-compassion and acceptance can lead to greater happiness.",
        "Libra": "Libra, the 7th Sign, is ruled by Venus, embodying harmony and balance. Symbolized by the scales, you value fairness and justice, often seeking to create equilibrium in your relationships and surroundings. Your diplomatic nature makes you an excellent mediator, and you have a natural flair for aesthetics. While your desire for harmony is a strength, be cautious of indecisiveness; trusting your instincts can lead to more fulfilling choices.",
        "Scorpio": "Scorpio, the 8th Sign, is ruled by Pluto, representing transformation and depth. Intense and passionate, you are resourceful and brave, often delving deep into the mysteries of life. Your strong will empowers you to overcome challenges, making you a formidable force. However, be mindful of your tendency to hold grudges or become overly secretive; embracing vulnerability can foster deeper connections with others.",
        "Sagittarius": "Sagittarius, the 9th Sign, is ruled by Jupiter, the planet of expansion and philosophy. Known for your love of freedom and adventure, you possess an optimistic outlook and a philosophical mindset. Your thirst for knowledge drives you to explore diverse cultures and ideas, making you a lifelong learner. While your enthusiasm is infectious, be cautious of restlessness; grounding yourself in the present can lead to more meaningful experiences.",
        "Capricorn": "Capricorn, the 10th Sign, is ruled by Saturn, symbolizing discipline and responsibility. You value ambition and organization, often setting high standards for yourself and others. Your work ethic is unmatched, and you strive for success in all endeavors. However, be aware of your tendency to be overly serious or rigid; allowing yourself moments of joy and spontaneity can enhance your overall well-being.",
        "Aquarius": "Aquarius, the 11th Sign, is ruled by Uranus, representing innovation and humanitarianism. Known for your originality and independence, you are a forward-thinking individual who values friendship and community. Your unique perspective allows you to challenge norms and inspire change. While your progressive mindset is admirable, be cautious of detachment; nurturing emotional connections can enrich your life.",
        "Pisces": "Pisces, the 12th Sign, is ruled by Neptune, symbolizing intuition and compassion. You are compassionate and artistic, often feeling deeply connected to the emotions of others. Your intuitive nature allows you to navigate the world with empathy and creativity. However, be aware of your tendency to escape reality; grounding yourself in practical matters can help you harness your gifts more effectively."
    }
    return predictions.get(sign, "No prediction available.")   


def generate_friendship_rules(planetary_positions):
    # Initialize friendship dynamics
    friendships = {
        "five_fold_friendship": {},
        "permanent_table": {},
        "temporary_friendship": {}
    }

    # Define basic relationships based on astrological principles
    for planet, position in planetary_positions.items():
        # Initialize each planet's friendship data
        friendships["five_fold_friendship"][planet] = {
            "BitterEnemy": [],
            "Enemies": [],
            "Friends": [],
            "IntimateFriend": [],
            "Neutral": []
        }
        
        friendships["permanent_table"][planet] = {
            "Enemies": [],
            "Friends": [],
            "Neutral": []
        }
        
        friendships["temporary_friendship"][planet] = {
            "Enemies": [],
            "Friends": []
        }

        # Determine relationships dynamically based on positions
        for other_planet, other_position in planetary_positions.items():
            if planet == other_planet:
                continue  # Skip self comparison

            degree_difference = abs(position - other_position) % 360
            
            # Define friendship and enmity rules based on degree differences
            if degree_difference < 30 or degree_difference > 330:  # Close in zodiac
                friendships["five_fold_friendship"][planet]["Friends"].append(other_planet)
                friendships["permanent_table"][planet]["Friends"].append(other_planet)
                friendships["temporary_friendship"][planet]["Friends"].append(other_planet)
            elif 30 <= degree_difference < 90:  # Neutral
                friendships["five_fold_friendship"][planet]["Neutral"].append(other_planet)
                friendships["permanent_table"][planet]["Neutral"].append(other_planet)
            elif 90 <= degree_difference < 150:  # Enemies
                friendships["five_fold_friendship"][planet]["Enemies"].append(other_planet)
                friendships["permanent_table"][planet]["Enemies"].append(other_planet)
            elif 150 <= degree_difference < 210:  # Bitter enemies
                friendships["five_fold_friendship"][planet]["BitterEnemy"].append(other_planet)

            # Example condition for intimate friends
            if degree_difference < 10:  # Very close in zodiac
                friendships["five_fold_friendship"][planet]["IntimateFriend"].append(other_planet)

    return friendships



# Function to plot KP Houses
def plot_kp_houses(planet_positions, lagna_position):
    num_houses = 12
    house_angles = [(lagna_position + i * (360 / num_houses)) % 360 for i in range(num_houses)]

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title("KP Houses Chart", fontsize=16, fontweight='bold')
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.axis('off')

    # Draw house boundaries
    ax.add_patch(plt.Rectangle((-3, -3), 6, 6, fill=False, linewidth=2))
    ax.add_patch(plt.Polygon([(-3, 0), (0, -3), (3, 0), (0, 3)], fill=False, linewidth=2))
    ax.plot([-3, 3], [-3, 3], color='black', linewidth=2)
    ax.plot([-3, 3], [3, -3], color='black', linewidth=2)

    house_positions = {i: [] for i in range(num_houses)}

    for planet, global_degree in planet_positions.items():
        house_index = int(global_degree // (360 / num_houses)) % num_houses
        house_positions[house_index].append(planet)

    for i in range(num_houses):
        rad = np.deg2rad(house_angles[i])
        x, y = np.cos(rad) * 2.5, np.sin(rad) * 2.5
        ax.text(x, y, f"House {i + 1}:", ha='center', va='center', fontsize=13)  # Shift house label left

        for j, planet in enumerate(house_positions[i]):
            color = planet_colors.get(planet, "blue")
            ax.text(x, y - 0.2 - j * 0.2, abbreviated_names.get(planet, planet[:2]), ha='center', va='center', fontsize=12, color=color)  # Shift planet name left

    plt.tight_layout()
    plt.savefig('static/kp_houses_chart.png')
    plt.close(fig)

def plot_navamsa_chart(planet_positions):
    num_houses = 12
    house_angles = [(i * 30) % 360 for i in range(num_houses)]  # Each house is 30 degrees

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title("Navamsa Chart", fontsize=16, fontweight='bold')
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.axis('off')

    ax.add_patch(plt.Rectangle((-3, -3), 6, 6, fill=False, linewidth=2))
    ax.add_patch(plt.Polygon([(-3, 0), (0, -3), (3, 0), (0, 3)], fill=False, linewidth=2))
    ax.plot([-3, 3], [-3, 3], color='black', linewidth=2)
    ax.plot([-3, 3], [3, -3], color='black', linewidth=2)

    house_positions = {i: [] for i in range(num_houses)}

    for planet, global_degree in planet_positions.items():
        navamsa_position = (global_degree // 3.3333) % 9  # 3.3333 degrees per Navamsa
        house_index = int(navamsa_position // (9 / num_houses)) % num_houses
        house_positions[house_index].append(planet)

    for i in range(num_houses):
        rad = np.deg2rad(house_angles[i])
        x = np.cos(rad) * 2.5
        y = np.sin(rad) * 2.5
        house_label = f"House {i + 1}:"
        ax.text(x, y, house_label, ha='center', va='center', fontsize=13, color='black')

        for j, planet in enumerate(house_positions[i]):
            color = planet_colors.get(planet, "blue")
            ax.text(x, y - 0.2 - j * 0.2, abbreviated_names.get(planet, planet[:2]), ha='center', va='center', fontsize=12, color=color)

    plt.tight_layout()
    plt.savefig('static/navamsa_chart.png')
    plt.close(fig)
    

# Function to plot Rashi Chart
def plot_rashi_chart(planet_positions):
    num_houses = 12
    house_angles = [(i * 30) % 360 for i in range(num_houses)]

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title("Rashi Chart", fontsize=16, fontweight='bold')
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.axis('off')

    # Draw house boundaries
    ax.add_patch(plt.Rectangle((-3, -3), 6, 6, fill=False, linewidth=2))
    ax.add_patch(plt.Polygon([(-3, 0), (0, -3), (3, 0), (0, 3)], fill=False, linewidth=2))
    ax.plot([-3, 3], [-3, 3], color='black', linewidth=2)
    ax.plot([-3, 3], [3, -3], color='black', linewidth=2)

    house_positions = {i: [] for i in range(num_houses)}

    for planet, global_degree in planet_positions.items():
        house_index = int(global_degree // 30) % num_houses
        house_positions[house_index].append(planet)

    for i in range(num_houses):
        rad = np.deg2rad(house_angles[i])
        x, y = np.cos(rad) * 2.5, np.sin(rad) * 2.5
        ax.text(x, y, f"House {i + 1}:", ha='center', va='center', fontsize=13)

        for j, planet in enumerate(house_positions[i]):
            color = planet_colors.get(planet, "blue")
            ax.text(x, y - 0.2 - j * 0.2, abbreviated_names.get(planet, planet[:2]), ha='center', va='center', fontsize=12, color=color)

    plt.tight_layout()
    plt.savefig('static/rashi_chart.png')
    plt.close(fig)



# Define the house ownership and aspect rules
house_ownership = {
    'Aries': 1, 'Taurus': 2, 'Gemini': 3, 'Cancer': 4,
    'Leo': 5, 'Virgo': 6, 'Libra': 7, 'Scorpio': 8,
    'Sagittarius': 9, 'Capricorn': 10, 'Aquarius': 11, 'Pisces': 12
}

# Define the points allocation
def get_points(planet, house):
    if planet == house:
        return 7  # Own house
    elif (planet == 'Sun' and house == 'Leo') or \
         (planet == 'Moon' and house == 'Cancer') or \
         (planet == 'Mars' and house == 'Aries') or \
         (planet == 'Mercury' and house == 'Virgo') or \
         (planet == 'Jupiter' and house == 'Sagittarius') or \
         (planet == 'Venus' and house == 'Taurus') or \
         (planet == 'Saturn' and house == 'Capricorn'):
        return 6  # Exalted
    elif (planet == 'Mars' and house in ['Aries', 'Scorpio']) or \
         (planet == 'Jupiter' and house in ['Cancer', 'Pisces']) or \
         (planet == 'Venus' and house in ['Taurus', 'Libra']):
        return 5  # Friendly
    elif (planet == 'Mercury' and house in ['Gemini', 'Virgo']):
        return 4  # Neutral
    elif (planet == 'Saturn' and house in ['Aquarius', 'Capricorn']):
        return 3  # Enemy
    elif (planet == 'Rahu' and house == 'Aquarius'):
        return 4  # Neutral
    else:
        return 0  # No influence

# Calculate Ashtakavarga points for each house
def calculate_ashtakavarga(planet_positions):
    houses = {i: 0 for i in range(1, 13)}  # Houses 1 to 12

    for planet, position in planet_positions.items():
        for house in range(1, 13):
            points = get_points(house_ownership[position], house)
            houses[house] += points

    return houses

# Plot Ashtakavarga chart with total points
def plot_ashtakavarga_chart(planet_positions):
    houses = calculate_ashtakavarga(planet_positions)  # Get points for each house
    num_houses = 12

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title("Ashtakavarga Chart", fontsize=16, fontweight='bold')
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.axis('off')

    ax.add_patch(plt.Rectangle((-3, -3), 6, 6, fill=False, linewidth=2))
    ax.add_patch(plt.Polygon([(-3, 0), (0, -3), (3, 0), (0, 3)], fill=False, linewidth=2))
    ax.plot([-3, 3], [-3, 3], color='black', linewidth=2)
    ax.plot([-3, 3], [3, -3], color='black', linewidth=2)

    for i in range(num_houses):
        rad = np.deg2rad((i * 30) % 360)
        x = np.cos(rad) * 2.5
        y = np.sin(rad) * 2.5
        house_label = f"House {i + 1}:{houses[i + 1]}"
        ax.text(x, y, house_label, ha='center', va='center', fontsize=13, color='black')

    plt.tight_layout()
    plt.savefig('static/ashtakavarga_chart.png')
    plt.close(fig)

# Example usage
planet_positions = {
    'Sun': 'Leo', 
    'Moon': 'Cancer', 
    'Mars': 'Aries', 
    'Mercury': 'Virgo', 
    'Jupiter': 'Sagittarius', 
    'Venus': 'Taurus', 
    'Saturn': 'Capricorn',
    'Rahu': 'Aquarius'
}

def plot_lagna_chart(planet_positions, lagna_position):
    num_houses = 12
    house_angles = [(lagna_position + i * (360 / num_houses)) % 360 for i in range(num_houses)]

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title("Lagna Chart", fontsize=16, fontweight='bold')
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.axis('off')

    # Draw the outer rectangle and diagonal lines
    ax.add_patch(plt.Rectangle((-3, -3), 6, 6, fill=False, linewidth=2))
    ax.add_patch(plt.Polygon([(-3, 0), (0, -3), (3, 0), (0, 3)], fill=False, linewidth=2))
    ax.plot([-3, 3], [-3, 3], color='black', linewidth=2)
    ax.plot([-3, 3], [3, -3], color='black', linewidth=2)

    # Initialize house positions
    house_positions = {i: [] for i in range(num_houses)}

    for planet, global_degree in planet_positions.items():
        # Determine which house the planet is in based on Lagna position
        house_index = (int(global_degree // (360 / num_houses)) + (lagna_position // (360 / num_houses))) % num_houses
        house_positions[house_index].append(planet)

    # Plot the houses with planet names
    for i in range(num_houses):
        rad = np.deg2rad(house_angles[i])
        x = np.cos(rad) * 2.5
        y = np.sin(rad) * 2.5
        house_label = f"House {i + 1}:"
        ax.text(x, y, house_label, ha='center', va='center', fontsize=13, color='black')

        for j, planet in enumerate(house_positions[i]):
            color = planet_colors.get(planet, "blue")  # Use a default color if not specified
            ax.text(x, y - 0.2 - j * 0.2, abbreviated_names.get(planet, planet[:2]), ha='center', va='center', fontsize=12, color=color)

    plt.tight_layout()
    plt.savefig('static/lagna_chart.png')
    plt.close(fig)

def calculate_papa_samaya(planetary_positions):
    # Initialize a dictionary to hold Papa Samaya values
    papa_samaya_values = {}
    
    # Example logic to calculate Papa Samaya based on planetary positions
    # This is a placeholder; replace with actual calculation logic.
    if "Mars" in planetary_positions:
        mars_position = planetary_positions["Mars"]
        # Example calculation for Mars
        papa_samaya_values["mars_papa"] = round(mars_position * 0.75, 2)  # Adjust the calculation as needed
    
    if "Rahu" in planetary_positions:
        rahu_position = planetary_positions["Rahu"]
        # Example calculation for Rahu
        papa_samaya_values["rahu_papa"] = round(rahu_position * 0.5, 2)  # Adjust the calculation as needed
        
    if "Saturn" in planetary_positions:
        saturn_position = planetary_positions["Saturn"]
        # Example calculation for Saturn
        papa_samaya_values["saturn_papa"] = round(saturn_position * 1.25, 3)  # Adjust the calculation as needed
        
    if "Sun" in planetary_positions:
        sun_position = planetary_positions["Sun"]
        # Example calculation for Sun
        papa_samaya_values["sun_papa"] = round(sun_position * 0.1, 2)  # Adjust the calculation as needed

    return papa_samaya_values

def fetch_horoscope_data(birth_time, birth_location):
    """Fetch horoscope data based on birth time and location."""
    observer = ephem.Observer()
    observer.date = birth_time
    observer.lat, observer.lon = birth_location  # Set latitude and longitude

    houses_data = calculate_house_data(observer)
    planets_data = calculate_planet_data(observer)

    return {
        "extended_horoscope_kp_houses": {
            "houses": houses_data,
            "planets": planets_data
        }
    }

# Define nakshatra data
nakshatra_data = {
    "Ashvini": {"start": 0, "lord": "Ketu"},
    "Bharani": {"start": 13.333, "lord": "Venus"},
    "Krittika": {"start": 26.666, "lord": "Sun"},
    "Rohini": {"start": 40, "lord": "Moon"},
    "Mrigashira": {"start": 53.333, "lord": "Mars"},
    "Ardra": {"start": 66.666, "lord": "Rahu"},
    "Punarvasu": {"start": 80, "lord": "Jupiter"},
    "Pushya": {"start": 93.333, "lord": "Saturn"},
    "Ashlesha": {"start": 106.666, "lord": "Mercury"},
    "Magha": {"start": 120, "lord": "Ketu"},
    "PurvaPhalguni": {"start": 133.333, "lord": "Venus"},
    "UttaraPhalguni": {"start": 146.666, "lord": "Sun"},
    "Hasta": {"start": 160, "lord": "Moon"},
    "Chitra": {"start": 173.333, "lord": "Mars"},
    "Swati": {"start": 186.666, "lord": "Rahu"},
    "Vishakha": {"start": 200, "lord": "Jupiter"},
    "Anuradha": {"start": 213.333, "lord": "Saturn"},
    "Jyeshtha": {"start": 226.666, "lord": "Mercury"},
    "Mula": {"start": 240, "lord": "Ketu"},
    "PurvaAshadha": {"start": 253.333, "lord": "Venus"},
    "UttaraAshadha": {"start": 266.666, "lord": "Sun"},
    "Shravana": {"start": 280, "lord": "Moon"},
    "Dhanishta": {"start": 293.333, "lord": "Mars"},
    "Shatabhisha": {"start": 306.666, "lord": "Rahu"},
    "PurvaBhadra": {"start": 320, "lord": "Jupiter"},
    "UttaraBhadra": {"start": 333.333, "lord": "Saturn"},
    "Revati": {"start": 346.666, "lord": "Mercury"},
}

def get_nakshatra(position):
    """Determine nakshatra based on the position in degrees."""
    for nakshatra_name, details in nakshatra_data.items():
        if details["start"] <= position < details["start"] + 13.333:
            return nakshatra_name, details["lord"]
    return None, None  # If not found

def calculate_house_data(observer, lat, lon):
    """Calculate house data based on the observer's position."""
    houses_data = []
    for house in range(1, 13):
        # Calculate the midpoint (Bhav Madhya) for the house
        bhavmadhya = (house - 1) * 30 + 15  # Example calculation for mid-point
        bhavmadhya = round(bhavmadhya, 6)

        # Calculate the cusp sub lord and sub sub lord
        cusp_sub_lord = calculate_cusp_sub_lord(bhavmadhya, observer, lat, lon)
        cusp_sub_sub_lord = calculate_cusp_sub_sub_lord(bhavmadhya, observer, lat, lon)

        # Determine the end nakshatra and its lord based on the bhavmadhya
        end_nakshatra, end_nakshatra_lord = get_nakshatra(bhavmadhya)

        # Determine Rasi based on bhavmadhya
        end_rasi, end_rasi_lord = get_zodiac(bhavmadhya)

        house_data = {
            "bhavmadhya": bhavmadhya,
            "cusp_sub_lord": cusp_sub_lord,
            "cusp_sub_sub_lord": cusp_sub_sub_lord,
            "end_nakshatra": end_nakshatra,
            "end_nakshatra_lord": end_nakshatra_lord,
            "end_rasi": end_rasi,
            "end_rasi_lord": end_rasi_lord,
            "global_end_degree": bhavmadhya + 30,  # Example calculation
            "global_start_degree": bhavmadhya,  # Example calculation
            "house": house,
            "length": 30,  # Example length of each house
            "local_end_degree": bhavmadhya + 15,  # Example calculation
            "local_start_degree": bhavmadhya - 15,  # Example calculation
            
        }
        houses_data.append(house_data)
    return houses_data


def calculate_cusp_sub_lord(bhavmadhya, observer, lat, lon):
    """Calculate the cusp sub lord based on the bhavmadhya."""
    # Convert ephem.Date to datetime
    observer_datetime = observer.date.datetime()  # Get the datetime object
    planetary_positions = calculate_planet_positions(observer_datetime.date(), observer_datetime.time(), lat, lon)
    
    cusp_sub_lord = None

    # Logic to determine the sub lord from planetary positions
    for planet, position in planetary_positions.items():
        if bhavmadhya % 30 < position % 30:  # Check if the bhavmadhya is in the range of a planet
            cusp_sub_lord = planet
            break

    return cusp_sub_lord if cusp_sub_lord else "Unknown"



def calculate_cusp_sub_sub_lord(bhavmadhya, observer, lat, lon):
    """Calculate the cusp sub sub lord based on the bhavmadhya."""
    observer_datetime = observer.date.datetime()  # Get the datetime object
    planetary_positions = calculate_planet_positions(observer_datetime.date(), observer_datetime.time(), lat, lon)
    
    cusp_sub_sub_lord = None

    # Logic to determine the sub sub lord from planetary positions
    for planet, position in planetary_positions.items():
        if bhavmadhya % 30 < position % 30:  # Check if the bhavmadhya is in the range of a planet
            cusp_sub_sub_lord = planet
            break

    return cusp_sub_sub_lord if cusp_sub_sub_lord else "Unknown"



def calculate_planet_data(observer):
    """Calculate planet data based on the observer's position."""
    planets_data = []
    for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        # Compute the position of the planet
        planet_obj = getattr(ephem, planet)()
        planet_obj.compute(observer)
        planet_position_deg = planet_obj.ra * 180 / np.pi  # Convert to degrees

        # Get Nakshatra and its lord
        nakshatra, nakshatra_lord = get_nakshatra(planet_position_deg)
        
        # Calculate Nakshatra Pada
        nakshatra_pada = calculate_nakshatra_pada(planet_position_deg)

        # Get Rasi and its lord
        start_rasi, start_rasi_lord = get_zodiac(planet_position_deg)

        planet_data = {
            "full_name": planet,
            "nakshatra": nakshatra,
            "nakshatra_no": list(nakshatra_data.keys()).index(nakshatra) + 1 if nakshatra else None,
            "nakshatra_pada": nakshatra_pada,  # Actual calculation for nakshatra pada
            "name": planet[:2],  # First two letters of the planet's name
            "planetId": str(["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"].index(planet)),
            "retro": False,  # Placeholder for retrograde status (implement logic if needed)
            "start_nakshatra": nakshatra,
            "start_nakshatra_lord": nakshatra_lord,
            "start_rasi": start_rasi,  # Actual Rasi calculation
            "start_rasi_lord": start_rasi_lord  # Actual Rasi lord
        }
        planets_data.append(planet_data)

    # Calculate positions for Rahu and Ketu based on the Moon's position
    moon_obj = ephem.Moon()
    moon_obj.compute(observer)
    moon_position_deg = moon_obj.ra * 180 / np.pi  # Convert to degrees

    # Calculate Rahu and Ketu positions (approximately 180 degrees apart)
    rahu_position_deg = moon_position_deg + 180
    ketu_position_deg = moon_position_deg - 180

    # Add Rahu and Ketu to the planets data
    for node, position in zip(["Rahu", "Ketu"], [rahu_position_deg, ketu_position_deg]):
        nakshatra, nakshatra_lord = get_nakshatra(position)
        rasi, rasi_lord = get_zodiac(position)  # Get Rasi and its lord

        node_data = {
            "full_name": node,
            "nakshatra": nakshatra,
            "nakshatra_no": list(nakshatra_data.keys()).index(nakshatra) + 1 if nakshatra else None,
            "nakshatra_pada": calculate_nakshatra_pada(position),  # Calculate Nakshatra Pada
            "name": node[:2],  # First two letters of the node's name
            "planetId": str(7 + ["Rahu", "Ketu"].index(node)),  # Assign IDs after the planets
            "retro": False,  # Placeholder for retrograde status
            "start_nakshatra": nakshatra,
            "start_nakshatra_lord": nakshatra_lord,
            "start_rasi": rasi,
            "start_rasi_lord": rasi_lord  # Add Rasi lord here
        }
        planets_data.append(node_data)

    return planets_data

def calculate_nakshatra_pada(degree):
    """Calculate Nakshatra Pada based on the degree."""
    degree_within_nakshatra = degree % 13.3333  # Each Nakshatra spans 13°20'
    return int(degree_within_nakshatra // (13.3333 / 4)) + 1  # 4 Padas per Nakshatra

def get_zodiac(degree):
    """Determine zodiac sign and its lord based on the degree."""
    # Normalize the degree to be within the range of 0 to 360
    degree = degree % 360
    zodiac_no = int(degree // 30) + 1  # Each zodiac sign spans 30 degrees
    
    # Zodiac names and their corresponding lords
    zodiac_names = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", 
        "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", 
        "Aquarius", "Pisces"
    ]
    zodiac_lords = {
        1: "Mars",      # Aries
        2: "Venus",     # Taurus
        3: "Mercury",   # Gemini
        4: "Moon",      # Cancer
        5: "Sun",       # Leo
        6: "Mercury",   # Virgo
        7: "Venus",     # Libra
        8: "Mars",      # Scorpio
        9: "Jupiter",   # Sagittarius
        10: "Saturn",   # Capricorn
        11: "Saturn",   # Aquarius
        12: "Jupiter"   # Pisces
    }
    
    # Validate zodiac_no to ensure it's within the correct range
    if zodiac_no < 1 or zodiac_no > 12:
        raise ValueError(f"Invalid degree: {degree}. Zodiac number must be between 1 and 12.")

    zodiac_name = zodiac_names[zodiac_no - 1]
    zodiac_lord = zodiac_lords.get(zodiac_no, "Unknown")
    

    return zodiac_name, zodiac_lord



def calculate_dasha(dob, tob, lat, lon):
    moon_nakshatra, nakshatra_index = calculate_moon_position(dob, tob, lat, lon)
    
    # Get Dasha periods based on Nakshatra index
    dasha_periods = get_dasha_durations(nakshatra_index)
    
    # Start date for Dasha calculation
    start_date = datetime.strptime(dob, "%d/%m/%Y")
    
    # Initialize the structure for Dasha Mahadasha Current
    dasha_mahadasha_current = {
        "Paryantardasha": {},
        "Pranadasha": {},
        "Shookshamadasha": {},
        "Antardasha": {},
        "Mahadasha": {},
        "Order_names": [],
        "Order_of_dashas": {}
    }
    
    # Calculate Dasha and Sub-Dasha
    dasha_start_date = start_date
    for planet, duration in dasha_periods.items():
        dasha_end_date = dasha_start_date + timedelta(days=duration * 365.25)  # Approximate days in a year
        
        # Fill Mahadasha
        dasha_mahadasha_current["Mahadasha"][planet] = {
            "key": planet,
            "name": planet,
            "start": dasha_start_date.strftime("%Y-%m-%d %H:%M:%S"),
            "end": dasha_end_date.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Calculate Antardasha (1/8 of Mahadasha duration)
        antardasha_duration = duration / 8
        antardasha_start = dasha_start_date
        antardasha_end = antardasha_start + timedelta(days=(antardasha_duration * 365.25))
        dasha_mahadasha_current["Antardasha"][planet] = {
            "key": planet,
            "name": planet,
            "start": antardasha_start.strftime("%Y-%m-%d %H:%M:%S"),
            "end": antardasha_end.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Calculate Pranadasha (1/12 of Antardasha duration)
        pranadasha_duration = antardasha_duration / 12
        pranadasha_start = antardasha_start
        pranadasha_end = pranadasha_start + timedelta(days=(pranadasha_duration * 365.25))
        dasha_mahadasha_current["Pranadasha"][planet] = {
            "key": planet,
            "name": planet,
            "start": pranadasha_start.strftime("%Y-%m-%d %H:%M:%S"),
            "end": pranadasha_end.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Calculate Shookshamadasha (1/12 of Pranadasha duration)
        shookshamadasha_duration = pranadasha_duration / 12
        shookshamadasha_start = pranadasha_start
        shookshamadasha_end = shookshamadasha_start + timedelta(days=(shookshamadasha_duration * 365.25))
        dasha_mahadasha_current["Shookshamadasha"][planet] = {
            "key": planet,
            "name": planet,
            "start": shookshamadasha_start.strftime("%Y-%m-%d %H:%M:%S"),
            "end": shookshamadasha_end.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Calculate Paryantardasha (1/12 of Antardasha duration)
        paryantardasha_duration = antardasha_duration / 12
        paryantardasha_start = antardasha_start
        paryantardasha_end = paryantardasha_start + timedelta(days=(paryantardasha_duration * 365.25))
        dasha_mahadasha_current["Paryantardasha"][planet] = {
            "key": planet,
            "name": planet,
            "start": paryantardasha_start.strftime("%Y-%m-%d %H:%M:%S"),
            "end": paryantardasha_end.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Update order names and order of dashas
        dasha_mahadasha_current["Order_names"].append(planet)
        dasha_mahadasha_current["Order_of_dashas"][planet] = {
            "key": planet,
            "name": planet,
            "start": dasha_start_date.strftime("%Y-%m-%d %H:%M:%S"),
            "end": dasha_end_date.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Move to the next Dasha start date
        dasha_start_date = dasha_end_date

    return dasha_mahadasha_current



def generate_yogini_maha_dasha(start_year, end_year):
    # Initialize the structure for yogini Maha Dasha
    yogini_maha_dasha = {
        "dasha_yogini-dasha-main": {
            "dasha_end_dates": [],
            "dasha_list": [],
            "dasha_lord_list": [],
            "start_date": datetime.now().strftime("%A %b %d %Y")  # Current date as start date
        }
    }
    
    # Define the Dasha names and their corresponding lords
    dasha_names = [
        "Pingala", "Dhanya", "Bhramari", "Bhadrika", "Ulka", 
        "Siddha", "Sankata", "Mangala"
    ]
    dasha_lords = [
        "Sun", "Jupiter", "Mars", "Mercury", "Saturn", 
        "Venus", "Rahu/Ketu", "Moon"
    ]

    # Define the duration for each Dasha in years
    dasha_duration = 6  # Assuming each Dasha lasts approximately 6 years

    # Generate Dasha end dates and populate the lists
    current_date = datetime(start_year, 7, 28)  # Starting from July 28 of the start year
    index = 0

    while current_date.year <= end_year:
        # Append Dasha end date
        yogini_maha_dasha["dasha_yogini-dasha-main"]["dasha_end_dates"].append(
            current_date.strftime("%a %b %d %Y 00:00:00 GMT+0000 (Coordinated Universal Time)")
        )
        
        # Append Dasha name and lord
        yogini_maha_dasha["dasha_yogini-dasha-main"]["dasha_list"].append(
            dasha_names[index % len(dasha_names)]
        )
        yogini_maha_dasha["dasha_yogini-dasha-main"]["dasha_lord_list"].append(
            dasha_lords[index % len(dasha_lords)]
        )

        # Move to the next Dasha end date
        current_date += timedelta(days=dasha_duration * 365.25)  # Approximate days in a year
        index += 1

    return yogini_maha_dasha

def calculate_current_mahadasha(dob, tob, lat, lon):
    moon_nakshatra, nakshatra_index = calculate_moon_position(dob, tob, lat, lon)
    # Fetch Dasha periods dynamically
    dasha_periods = get_dasha_durations(nakshatra_index)

    # Calculate Moon's position
    moon_nakshatra, starting_planet = calculate_moon_position(dob, tob, lat, lon)

    # Start date for Dasha calculation
    start_date = datetime.strptime(dob, "%d/%m/%Y")
    current_date = datetime.utcnow()  # Use UTC for consistency

    # Calculate Mahadasha end date
    dasha_start_date = start_date
    for planet, duration in dasha_periods.items():
        dasha_end_date = dasha_start_date + timedelta(days=duration * 365.25)
        if dasha_end_date > current_date:
            return {
                "end": dasha_end_date.strftime("%A %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)"),
                "key": planet,
                "name": planet,
                "start": dasha_start_date.strftime("%A %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)")
            }
        dasha_start_date = dasha_end_date

    return None

def calculate_shookshamahadasha(dob, tob, lat, lon):
    # Calculate Moon's position
    moon_nakshatra, starting_planet = calculate_moon_position(dob, tob, lat, lon)

    # Fetch the duration for Shookshamahadasha based on the Moon's position
    shookshamahadasha_duration = 7  # Example duration in days; adjust as needed

    # Calculate the start date based on the current date
    start_date = datetime.utcnow()  # Use UTC for consistency
    end_date = start_date + timedelta(days=shookshamahadasha_duration)

    return {
        "end": end_date.strftime("%A %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)"),
        "key": moon_nakshatra,  # Use the moon's nakshatra as key
        "name": "Moon",
        "start": start_date.strftime("%A %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)")
    }

def calculate_antardasha_durations():
    # Get the Mahadasha durations
    mahadasha_durations = get_dasha_durations()
    
    # Define Antardasha durations based on the Mahadasha durations
    antardasha_durations = {}

    # Calculate Antardasha durations
    for planet, duration in mahadasha_durations.items():
        # Each Mahadasha has its own Antardasha periods
        # Assuming each Mahadasha has 9 Antardashas (including itself)
        antardasha_count = 9
        
        # Calculate the duration for each Antardasha
        antardasha_duration = duration / antardasha_count
        
        # Assign the calculated duration to the Antardasha mapping
        for i in range(antardasha_count):
            # Create a unique Antardasha name
            antardasha_name = f"{planet}_{i+1}"
            antardasha_durations[antardasha_name] = antardasha_duration

    return antardasha_durations


def calculate_antardasha(dob, tob, lat, lon):
    # Calculate the current Mahadasha to find the corresponding Antardasha
    current_mahadasha = calculate_current_mahadasha(dob, tob, lat, lon)

    if current_mahadasha:
        # Get the nakshatra_index from the current Mahadasha
        nakshatra_index = current_mahadasha['key']  # Adjust as needed to get the correct index

        # Define Antardasha durations based on the current Mahadasha
        antardasha_durations = get_dasha_durations(nakshatra_index)  # Call to get durations

        # Extract the duration in days from the returned dictionary
        duration_in_days = antardasha_durations.get('duration', 0)  # Adjust the key as needed

        # Calculate start and end dates for the current Antardasha
        start_date = datetime.utcnow()  # Use UTC for consistency
        end_date = start_date + timedelta(days=duration_in_days)  # Use the extracted duration

        return {
            "end": end_date.strftime("%A %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)"),
            "key": current_mahadasha['key'],  # Current Mahadasha key
            "name": current_mahadasha['name'],  # Current Mahadasha name
            "start": start_date.strftime("%A %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)")
        }
    return None


def calculate_paryantardasha(start_date, planet, duration_days):
    """
    Calculate the Paryantardasha based on the start date, planet name, and duration.
    
    Parameters:
    - start_date (datetime): The starting date as a datetime object.
    - planet (str): The name of the planet.
    - duration_days (int): The duration of the Paryantardasha in days.
    
    Returns:
    - dict: A dictionary containing the Paryantardasha details.
    """
    # Ensure duration_days is an integer
    if isinstance(duration_days, dict):
        raise ValueError("Expected an integer for duration_days, but got a dictionary.")
    # Check if start_date is a datetime object
    if isinstance(start_date, datetime):
        start_datetime = start_date  # Use it directly
    else:
        # If it's a string, parse it (if needed)
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")

    # Calculate the end date
    end_datetime = start_datetime + timedelta(days=duration_days)
    
    # Create the Paryantardasha dictionary
    paryantardasha = {
        "key": planet,
        "name": planet,
        "start": start_datetime.strftime("%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)"),
        "end": end_datetime.strftime("%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)")
    }
    
    return paryantardasha



def calculate_current_mahadasha_full(dob, tob, lat, lon):
    moon_nakshatra, nakshatra_index = calculate_moon_position(dob, tob, lat, lon)
    # Fetch Dasha periods
    dasha_periods = get_dasha_durations(nakshatra_index)  # Ensure this contains all 9 planets

    # Calculate Moon's position
    moon_nakshatra, starting_planet = calculate_moon_position(dob, tob, lat, lon)

    # Start date for Dasha calculation
    start_date = datetime.strptime(dob, "%d/%m/%Y")
    current_date = datetime.utcnow()  # Use UTC for consistency

    # Initialize the full Mahadasha structure
    mahadasha_full = {
        "Pranadasha": [],
        "Shookshamadasha": [],
        "Antardasha": [],
        "Mahadasha": [],
        "Paryantardasha": []  
    }

    # Calculate Mahadasha periods
    dasha_start_date = start_date
    for planet, duration in dasha_periods.items():
        dasha_end_date = dasha_start_date + timedelta(days=duration * 365.25)
        
        # Append to Mahadasha list
        mahadasha_full["Mahadasha"].append({
            "key": planet,
            "name": planet,
            "start": dasha_start_date.strftime("%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)"),
            "end": dasha_end_date.strftime("%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)")
        })
        
        # Calculate Paryantardasha for this planet (example duration, adjust as needed)
        paryantardasha_duration = 10  # Example duration in days
        paryantardasha = calculate_paryantardasha(dasha_start_date.strftime("%Y-%m-%d %H:%M:%S"), planet, paryantardasha_duration)
        mahadasha_full["Paryantardasha"].append(paryantardasha)
        
        # Move to the next Dasha start date
        dasha_start_date = dasha_end_date

    # Calculate Shookshamadasha for all planets
    shookshamadasha_start = start_date  # Adjust as necessary for the start date
    for planet in dasha_periods.keys():  # Ensure all 9 planets are included
        shookshamadasha_end = shookshamadasha_start + timedelta(days=7)  # Example duration
        mahadasha_full["Shookshamadasha"].append({
            "key": planet,
            "name": planet,
            "start": shookshamadasha_start.strftime("%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)"),
            "end": shookshamadasha_end.strftime("%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)")
        })
        shookshamadasha_start = shookshamadasha_end  # Update for next planet

    # Calculate Antardasha for all planets
    antardasha_start = start_date  # Example; adjust as needed
    for planet in dasha_periods.keys():  # Ensure all 9 planets are included
        antardasha_end = antardasha_start + timedelta(days=30)  # Example duration
        mahadasha_full["Antardasha"].append({
            "key": planet,
            "name": planet,
            "start": antardasha_start.strftime("%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)"),
            "end": antardasha_end.strftime("%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)")
        })
        antardasha_start = antardasha_end  # Update for next planet

    # Calculate Pranadasha for all planets
    pranadasha_start = start_date  # Adjust as necessary
    for planet in dasha_periods.keys():  # Ensure all 9 planets are included
        pranadasha_end = pranadasha_start + timedelta(days=10)  # Example duration
        mahadasha_full["Pranadasha"].append({
            "key": planet,
            "name": planet,
            "start": pranadasha_start.strftime("%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)"),
            "end": pranadasha_end.strftime("%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)")
        })
        pranadasha_start = pranadasha_end  # Update for next planet

    return mahadasha_full



def calculate_dasha_order(dob, tob, lat, lon):
    # Step 1: Calculate Moon's position and Nakshatra
    moon_nakshatra, nakshatra_index = calculate_moon_position(dob, tob, lat, lon)
    
    # Define the duration of each planet in Mahadasha (in years)
    dasha_durations = get_dasha_durations(nakshatra_index)

    # Ensure we only consider the first nine planets
    planets = list(dasha_durations.keys())[:9]  # Limit to 9 planets
    
    # Initialize the current Dasha
    dashas = {
        "current": {
            "name": moon_nakshatra,
            "start": datetime.strptime(dob, "%d/%m/%Y"),
            "end": datetime.strptime(dob, "%d/%m/%Y") + timedelta(days=sum(dasha_durations.values()) * 365.25),
        },
        "minors": [],
        "sub_minors": [],
        "sub_sub_minors": []
    }

    # Calculate minors based on the current Dasha
    current_start = dashas["current"]["start"]

    # Calculate minor Dasha periods for the first nine planets
    for planet in planets:
        duration = dasha_durations[planet]
        end_date = current_start + timedelta(days=duration * 365.25)  # Approximate year length
        dashas["minors"].append({
            "key": planet,
            "name": planet,  # Name matches the key
            "start": current_start,
            "end": end_date
        })
        current_start = end_date  # Update start for next planet

    # Calculate sub-minors (1/3 of each minor) limited to the first nine
    for minor in dashas["minors"][:9]:  # Limit to 9 minors
        minor_duration = (minor["end"] - minor["start"]) / 3
        for i in range(3):
            sub_minor_start = minor["start"] + (i * minor_duration)
            sub_minor_end = sub_minor_start + minor_duration
            if len(dashas["sub_minors"]) < 9:  # Ensure we don't exceed 9 sub-minors
                dashas["sub_minors"].append({
                    "key": minor["key"],
                    "name": minor["name"],  # Name matches the minor's key
                    "start": sub_minor_start,
                    "end": sub_minor_end
                })

    # Calculate sub-sub-minors (1/3 of each sub-minor) limited to the first nine
    for sub_minor in dashas["sub_minors"][:9]:  # Limit to 9 sub-minors
        sub_minor_duration = (sub_minor["end"] - sub_minor["start"]) / 3
        for i in range(3):
            sub_sub_minor_start = sub_minor["start"] + (i * sub_minor_duration)
            sub_sub_minor_end = sub_sub_minor_start + sub_minor_duration
            if len(dashas["sub_sub_minors"]) < 9:  # Ensure we don't exceed 9 sub-sub-minors
                dashas["sub_sub_minors"].append({
                    "key": sub_minor["key"],
                    "name": sub_minor["name"],  # Name matches the sub-minor's key
                    "start": sub_sub_minor_start,
                    "end": sub_sub_minor_end
                })

    return {
        "dasha_names": planets,
        "dasha_orders": dashas
    }

def calculate_pranadasha(dob, tob, lat, lon):
    # Step 1: Calculate Moon's position and Nakshatra
    moon_nakshatra, nakshatra_index = calculate_moon_position(dob, tob, lat, lon)
    
    # Step 2: Get Dasha durations based on Nakshatra index
    dasha_periods = get_dasha_durations(nakshatra_index)
    
    # Start date for Dasha calculation
    start_date = datetime.strptime(dob, "%d/%m/%Y")
    
    # Initialize the structure for Pranadasha
    pranadasha_detail = {}
    
    # Calculate Dasha and Sub-Dasha
    dasha_start_date = start_date
    for planet, duration in dasha_periods.items():
        dasha_end_date = dasha_start_date + timedelta(days=duration * 365.25)  # Approximate days in a year
        
        # Calculate Antardasha (1/8 of Mahadasha duration)
        antardasha_duration = duration / 8
        antardasha_start = dasha_start_date
        antardasha_end = antardasha_start + timedelta(days=(antardasha_duration * 365.25))
        
        # Calculate Pranadasha (1/12 of Antardasha duration)
        pranadasha_duration = antardasha_duration / 12
        pranadasha_start = antardasha_start
        pranadasha_end = pranadasha_start + timedelta(days=(pranadasha_duration * 365.25))
        
        # Fill Pranadasha details for the first planet only
        pranadasha_detail = {
            "end": pranadasha_end.strftime("%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)"),
            "key": planet,
            "name": planet,
            "start": pranadasha_start.strftime("%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)")
        }

        # Break after the first entry
        break

    return pranadasha_detail


def check_horoscope(name, dob, tob, lat, lon, tz):
    # Validate time of birth format
    if not re.match(r'^\d{2}:\d{2}$', tob):
        return "Please enter the time of birth in HH:MM format."
    
    # Calculate horoscope data
    lagna, lagna_rasi_number, planetary_positions, rasi_info = calculate_horoscope_data(dob, tob, lat, lon)
    
    # Calculate lucky and destiny numbers with traits
    lucky_number, lucky_traits = calculate_lucky_number(dob)
    destiny_number, destiny_traits = calculate_destiny_number(dob)

    # Prepare extended horoscope details dynamically
    observer = ephem.Observer()
    observer.date = f"{dob} {tob}"
    observer.lat, observer.lon = lat, lon

    # Calculate houses and planets data
    houses_data = calculate_house_data(observer, lat, lon)
    planets_data = calculate_planet_data(observer)

    extended_horoscope_kp_houses = {
        "houses": houses_data,
        "planets": planets_data
    }

    # Calculate Panchang data
    panchang_info = calculate_panchang(dob, tob, lat, lon)

    # Generate the extended horoscope friendship map automatically
    extended_horoscope_friendship = generate_friendship_rules(planetary_positions)
    
    # Calculate Dasha details
    maha_dasha_info = calculate_current_mahadasha(dob, tob, lat, lon)
    
    # Calculate Pitra Dosh dynamically
    pitra_dosh_info = calculate_pitra_dosh(planetary_positions)
   
    # Calculate Sade Sati
    sade_sati_info = calculate_sade_sati(dob, tob, lat, lon)
     # Calculate the current year
    current_year = datetime.now().year

    # Extract the year of birth from the DOB
    year_of_birth = int(dob.split("/")[-1])  # Assuming dob is in "DD/MM/YYYY" format

    # Define the start year as the year of birth
    start_year = year_of_birth

    # Define the end year as the current year
    end_year = current_year

    # Call the function with the required arguments
    yogini_dasha = generate_yogini_maha_dasha(start_year, end_year)
    # Calculate Ascendant
    ascendant = calculate_ascendant(dob, tob, lat, lon)
    # Maanglik Dosha
    manglik_dosh = calculate_manglik_dosh(planet_positions)
    #  dasha prediction
    dasha_predictions=calculate_dasha_predictions(dob,tob,lat,lon)
    # Mangal-dosha Calculation
    mangal_dosh_info = calculate_mangal_dosh(planetary_positions,dob)

    # Prepare Nakshatra details
    nakshatra, nakshatra_index = calculate_nakshatra(ascendant)

    # Calculate Moon and Sun signs
    moon_sign, moon_sign_index = calculate_moon_position(dob, tob, lat, lon)
    sun_sign = calculate_sun_position(dob, tob, lat, lon)

    # Fetch predictions for Moon and Sun signs
    moon_prediction = get_prediction_for_sign(moon_sign)
    sun_prediction = get_prediction_for_sign(sun_sign)

    # Prepare horoscope details
    horoscope_planet_details = []
    for planet, info in rasi_info.items():
        planet_description = get_zodiac_description(planet)
        planet_position_deg = planetary_positions[planet]

        nakshatra, nakshatra_lord = get_nakshatra(planet_position_deg)
        nakshatra_pada = calculate_nakshatra_pada(planet_position_deg)
        start_rasi, start_rasi_lord = get_zodiac(planet_position_deg)

        planet_details = {
            "full_name": planet,
            "rasi_no": info['Rasi Number'],
            "house": info['House Number'],
            "position": planet_position_deg,
            "lagna": lagna,
            "lagna_rasi_number": lagna_rasi_number,
            "nakshatra": nakshatra,
            "nakshatra_no": list(nakshatra_data.keys()).index(nakshatra) + 1 if nakshatra else None,
            "nakshatra_pada": nakshatra_pada,
            "start_rasi": start_rasi,
            "start_rasi_lord": start_rasi_lord,
            "description": planet_description
        }
        horoscope_planet_details.append(planet_details)
    # Fetch Dasha periods dynamically
    dasha_periods = get_dasha_durations(nakshatra_index)
   
    # Plot the KP houses chart and Lagna chart
    plot_kp_houses(planetary_positions, lagna)
    
    
    # Plot the Ashtakavarga, Rashi, and Navamsa charts
   
    plot_lagna_chart(planetary_positions, lagna)
    plot_rashi_chart(planetary_positions)
    plot_ashtakavarga_chart(planet_positions)
    # Calculate current Mahadasha details
    current_mahadasha_full = calculate_current_mahadasha_full(dob, tob, lat, lon)
    # Combine Dasha info into a single structure
    dasha_order_info = calculate_dasha_order(dob, tob, lat, lon)
    dasha_periods=get_dasha_durations(nakshatra_index)
    planet=planet
    # Combine Dasha info into a single structure
    dasha_mahadasha_current = {
        "Mahadasha": maha_dasha_info,
        "Shookshamahadasha": calculate_shookshamahadasha(dob, tob, lat, lon),
        "Antardasha": calculate_antardasha(dob, tob, lat, lon),
        "Pranadasha": calculate_pranadasha(dob, tob, lat, lon),
        "Paryantardasha": calculate_paryantardasha(datetime.strptime(dob, "%d/%m/%Y"), planet, dasha_periods.get(planet, 0)), 
        "order_names": dasha_order_info["dasha_names"],  # Add order names
        "order_of_dasha": dasha_order_info["dasha_orders"] 
    }

    # Prepare current Mahadasha full info separately
    dasha_mahadasha_current_full = current_mahadasha_full
   
    # Save user data
    user_data = save_to_firestore(
        name, dob, tob, lat, lon, tz, 
        "horoscope", {
            "horoscope_planet_details": horoscope_planet_details,
            "lagna": lagna,
            "lagna_rasi_number": lagna_rasi_number,
            "lucky_number": lucky_number,
            "lucky_traits": lucky_traits,
            "destiny_number": destiny_number,
            "destiny_traits": destiny_traits,
            "panchang": panchang_info,
            "dasha_current_mahadasha": dasha_mahadasha_current, 
            "dasha_mahadasha_current_full": dasha_mahadasha_current_full,
            "dasha-char-dasha-full":dasha_predictions,
            "dasha-yogini-dasha-main":yogini_dasha,
            "Mangal-dosh": mangal_dosh_info,  
            "extended_horoscope_find-moon-sign": {
                "moon_sign": moon_sign,
                "prediction": moon_prediction
            },
            "extended_horoscope_find-sun-sign": {
                "sun_sign": sun_sign,
                "prediction": sun_prediction
            },
            "pitra_dosh": pitra_dosh_info,
            "sade_sati_info": sade_sati_info,
            "papa-samaya": calculate_papa_samaya(planetary_positions),
            "Maanglik-Dosh":manglik_dosh,
            "extended-horoscope_friendships": extended_horoscope_friendship,
            "extended_horoscope_kp_houses": extended_horoscope_kp_houses
        },
        lucky_number, lucky_traits, destiny_number, destiny_traits
    )

    if isinstance(user_data, str) and "Error" in user_data:
        return user_data

    save_to_json_file(user_data)

    return {
    "name": name,
    "lat": lat,
    "lon": lon,
    "dob": dob,
    "horoscope": {
        "planetary_positions": planetary_positions,
        "horoscope_planet_details": horoscope_planet_details,
        "lagna": lagna,
        "lagna_rasi_number": lagna_rasi_number,
        "lucky_number": lucky_number,
        "lucky_traits": lucky_traits,
        "destiny_number": destiny_number,
        "destiny_traits": destiny_traits,
        "panchang": panchang_info,
        "dasha_current_mahadasha": dasha_mahadasha_current, 
        "dasha_mahadasha_current_full": dasha_mahadasha_current_full, 
        "dasha-char-dasha-full": dasha_predictions,
        "dasha-yogini-dasha-main": yogini_dasha,
        "Mangal-dosh": mangal_dosh_info,  
        "extended_horoscope_find-moon-sign": {
            "moon_sign": moon_sign,
            "prediction": moon_prediction
        },
        "extended_horoscope_find-sun-sign": {
            "sun_sign": sun_sign,
            "prediction": sun_prediction
        },
        "pitra_dosh": pitra_dosh_info,
        "sade_sati_info": sade_sati_info,
        "Papa-samaya": calculate_papa_samaya(planetary_positions),
        "Maanglik-Dosh": manglik_dosh,
        "extended-horoscope_friendships": extended_horoscope_friendship,
        "extended_horoscope_kp_houses": extended_horoscope_kp_houses
    }
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        tob = request.form['tob']
        country = request.form['country']
        state = request.form['state']
        place = request.form['place']
        tz = float(request.form['tz'])

        coordinates = place_coordinates.get(country, {}).get(state, {}).get(place, {})
        lat = coordinates.get("lat")
        lon = coordinates.get("lon")
        
        # Check Horoscope
        horoscope_result = check_horoscope(name, dob, tob, lat, lon, tz)
        
        return render_template('index13.html', result=horoscope_result, place_coordinates=place_coordinates)

    return render_template('index13.html', result=None, place_coordinates=place_coordinates)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True)
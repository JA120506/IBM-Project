import os
from pathlib import Path

import requests
from flask import Flask, jsonify, render_template, request
from summarizer import calculate_flood_risk

BASE_DIR = Path(__file__).resolve().parent
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)

# Indian States and Union Territories with representative coordinates
INDIAN_STATES_UTS = {
    # States
    "Andhra Pradesh": {"lat": 15.9129, "lon": 78.6675, "type": "state"},
    "Arunachal Pradesh": {"lat": 28.2180, "lon": 94.7278, "type": "state"},
    "Assam": {"lat": 26.2006, "lon": 92.9376, "type": "state"},
    "Bihar": {"lat": 25.5941, "lon": 85.1376, "type": "state"},
    "Chhattisgarh": {"lat": 21.2787, "lon": 81.8661, "type": "state"},
    "Goa": {"lat": 15.2993, "lon": 73.8243, "type": "state"},
    "Gujarat": {"lat": 22.2587, "lon": 71.1924, "type": "state"},
    "Haryana": {"lat": 29.0588, "lon": 77.0745, "type": "state"},
    "Himachal Pradesh": {"lat": 31.1048, "lon": 77.1734, "type": "state"},
    "Jharkhand": {"lat": 23.6102, "lon": 85.2799, "type": "state"},
    "Karnataka": {"lat": 15.3173, "lon": 75.7139, "type": "state"},
    "Kerala": {"lat": 10.8505, "lon": 76.2711, "type": "state"},
    "Madhya Pradesh": {"lat": 22.9375, "lon": 78.6553, "type": "state"},
    "Maharashtra": {"lat": 19.7515, "lon": 75.7139, "type": "state"},
    "Manipur": {"lat": 24.6637, "lon": 93.9063, "type": "state"},
    "Meghalaya": {"lat": 25.4670, "lon": 91.3662, "type": "state"},
    "Mizoram": {"lat": 23.1815, "lon": 92.9789, "type": "state"},
    "Nagaland": {"lat": 26.1584, "lon": 94.5624, "type": "state"},
    "Odisha": {"lat": 20.9517, "lon": 85.0985, "type": "state"},
    "Punjab": {"lat": 31.5497, "lon": 74.3436, "type": "state"},
    "Rajasthan": {"lat": 27.0238, "lon": 74.2179, "type": "state"},
    "Sikkim": {"lat": 27.5330, "lon": 88.5122, "type": "state"},
    "Tamil Nadu": {"lat": 11.1271, "lon": 79.2787, "type": "state"},
    "Telangana": {"lat": 18.1124, "lon": 79.0193, "type": "state"},
    "Tripura": {"lat": 23.9408, "lon": 91.9882, "type": "state"},
    "Uttar Pradesh": {"lat": 26.8467, "lon": 80.9618, "type": "state"},
    "Uttarakhand": {"lat": 30.0668, "lon": 79.0193, "type": "state"},
    "West Bengal": {"lat": 24.8765, "lon": 88.3630, "type": "state"},
    
    # Union Territories
    "Andaman and Nicobar Islands": {"lat": 11.7401, "lon": 92.6586, "type": "ut"},
    "Chandigarh": {"lat": 30.7333, "lon": 76.7794, "type": "ut"},
    "Dadra and Nagar Haveli and Daman and Diu": {"lat": 20.1809, "lon": 73.0505, "type": "ut"},
    "Lakshadweep": {"lat": 12.2381, "lon": 73.1948, "type": "ut"},
    "Delhi": {"lat": 28.7041, "lon": 77.1025, "type": "ut"},
    "Puducherry": {"lat": 11.9416, "lon": 79.8083, "type": "ut"},
    "Ladakh": {"lat": 34.1526, "lon": 77.5770, "type": "ut"},
    "Jammu and Kashmir": {"lat": 33.7782, "lon": 76.5769, "type": "ut"},
}

# Major Indian Cities
MAJOR_INDIAN_CITIES = {
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946, "state": "Karnataka"},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777, "state": "Maharashtra"},
    "Delhi": {"lat": 28.7041, "lon": 77.1025, "state": "Delhi"},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639, "state": "West Bengal"},
    "Chennai": {"lat": 13.0827, "lon": 80.2707, "state": "Tamil Nadu"},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867, "state": "Telangana"},
    "Pune": {"lat": 18.5204, "lon": 73.8567, "state": "Maharashtra"},
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714, "state": "Gujarat"},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873, "state": "Rajasthan"},
    "Surat": {"lat": 21.1458, "lon": 72.8336, "state": "Gujarat"},
    "Lucknow": {"lat": 26.8467, "lon": 80.9618, "state": "Uttar Pradesh"},
    "Kanpur": {"lat": 26.4499, "lon": 80.3319, "state": "Uttar Pradesh"},
    "Nagpur": {"lat": 21.1458, "lon": 79.0882, "state": "Maharashtra"},
    "Indore": {"lat": 22.7196, "lon": 75.8577, "state": "Madhya Pradesh"},
    "Kochi": {"lat": 9.9312, "lon": 76.2673, "state": "Kerala"},
    "Thiruvananthapuram": {"lat": 8.5241, "lon": 76.9366, "state": "Kerala"},
    "Kozhikode": {"lat": 11.2588, "lon": 75.7804, "state": "Kerala"},
    "Ernakulam": {"lat": 9.9312, "lon": 76.2673, "state": "Kerala"},
    "Kottayam": {"lat": 9.5941, "lon": 76.5214, "state": "Kerala"},
    "Patna": {"lat": 25.5941, "lon": 85.1376, "state": "Bihar"},
    "Guwahati": {"lat": 26.1445, "lon": 91.7362, "state": "Assam"},
    "Bhubaneswar": {"lat": 20.2961, "lon": 85.8245, "state": "Odisha"},
    "Raipur": {"lat": 21.2514, "lon": 81.6296, "state": "Chhattisgarh"},
    "Ranchi": {"lat": 23.3441, "lon": 85.3096, "state": "Jharkhand"},
    "Vadodara": {"lat": 22.3072, "lon": 73.1812, "state": "Gujarat"},
    "Pimpri-Chinchwad": {"lat": 18.6298, "lon": 73.7997, "state": "Maharashtra"},
    "Nashik": {"lat": 19.9975, "lon": 73.7898, "state": "Maharashtra"},
    "Aurangabad": {"lat": 19.8762, "lon": 75.3433, "state": "Maharashtra"},
    "Amritsar": {"lat": 31.6340, "lon": 74.8723, "state": "Punjab"},
    "Ludhiana": {"lat": 30.9010, "lon": 75.8573, "state": "Punjab"},
    "Chandigarh": {"lat": 30.7333, "lon": 76.7794, "state": "Chandigarh"},
    "Bhopal": {"lat": 23.1815, "lon": 79.9864, "state": "Madhya Pradesh"},
    "Ghaziabad": {"lat": 28.6692, "lon": 77.4538, "state": "Uttar Pradesh"},
    "Noida": {"lat": 28.5355, "lon": 77.3910, "state": "Uttar Pradesh"},
    "Coimbatore": {"lat": 11.0081, "lon": 76.9875, "state": "Tamil Nadu"},
    "Madurai": {"lat": 9.9252, "lon": 78.1198, "state": "Tamil Nadu"},
    "Salem": {"lat": 11.6643, "lon": 78.1460, "state": "Tamil Nadu"},
    "Visakhapatnam": {"lat": 17.6869, "lon": 83.2185, "state": "Andhra Pradesh"},
    "Vijayawada": {"lat": 16.5062, "lon": 80.6480, "state": "Andhra Pradesh"},
    "Agra": {"lat": 27.1767, "lon": 78.0081, "state": "Uttar Pradesh"},
    "Varanasi": {"lat": 25.3356, "lon": 82.9856, "state": "Uttar Pradesh"},
    "Prayagraj": {"lat": 25.4358, "lon": 81.8463, "state": "Uttar Pradesh"},
    "Meerut": {"lat": 28.9845, "lon": 77.7064, "state": "Uttar Pradesh"},
    "Mathura": {"lat": 27.4924, "lon": 77.6737, "state": "Uttar Pradesh"},
    "Jhansi": {"lat": 25.4484, "lon": 78.5685, "state": "Uttar Pradesh"},
    "Indore": {"lat": 22.7196, "lon": 75.8577, "state": "Madhya Pradesh"},
    "Jabalpur": {"lat": 23.1815, "lon": 79.9864, "state": "Madhya Pradesh"},
    "Ujjain": {"lat": 23.1815, "lon": 75.7776, "state": "Madhya Pradesh"},
    "Gwalior": {"lat": 26.2183, "lon": 78.1629, "state": "Madhya Pradesh"},
}

# Predefined flood-prone areas for demo presets
DEMO_PRESETS = {
    "miami": {
        "name": "Miami, USA",
        "lat": 25.7617,
        "lon": -80.1918,
        "description": "High risk of coastal storm surge and high-tide street flooding."
    },
    "venice": {
        "name": "Venice, Italy",
        "lat": 45.4387,
        "lon": 12.3271,
        "description": "Historical tidal flooding (Acqua Alta) vulnerability."
    },
    "mumbai": {
        "name": "Mumbai, India",
        "lat": 19.0760,
        "lon": 72.8777,
        "description": "Heavy monsoon rainfall and drainage capacity strain."
    },
    "jakarta": {
        "name": "Jakarta, Indonesia",
        "lat": -6.2088,
        "lon": 106.8456,
        "description": "Rapid land subsidence and heavy river runoff."
    },
    "queensland": {
        "name": "Queensland (Brisbane), Australia",
        "lat": -27.4705,
        "lon": 153.0260,
        "description": "Vulnerable to heavy riverine flooding and coastal cyclones."
    },
    "london": {
        "name": "London, UK",
        "lat": 51.5074,
        "lon": -0.1278,
        "description": "Low baseline risk due to Thames Barrier protection."
    }
}

# Weather code interpretations for climatic conditions
WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Foggy", 48: "Depositing Rime Fog",
    51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
    61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
    71: "Slight Snow", 73: "Moderate Snow", 75: "Heavy Snow",
    80: "Slight Rain Showers", 81: "Moderate Rain Showers", 82: "Violent Rain Showers",
    95: "Thunderstorm", 96: "Thunderstorm with Slight Hail", 99: "Thunderstorm with Heavy Hail"
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/presets")
def get_presets():
    return jsonify(DEMO_PRESETS)

@app.route("/api/search")
def search_locations():
    query = request.args.get("q", "").strip()
    if not query or len(query) < 2:
        return jsonify([])
    
    query_lower = query.lower()
    results = []
    
    # First, search Indian states and UTs
    for state_name, state_data in INDIAN_STATES_UTS.items():
        if query_lower in state_name.lower():
            results.append({
                "name": state_name,
                "full_name": state_name,
                "latitude": state_data["lat"],
                "longitude": state_data["lon"],
                "type": "state"
            })
    
    # Then, search major Indian cities
    for city_name, city_data in MAJOR_INDIAN_CITIES.items():
        if query_lower in city_name.lower():
            results.append({
                "name": city_name,
                "full_name": f"{city_name}, {city_data['state']}",
                "latitude": city_data["lat"],
                "longitude": city_data["lon"],
                "type": "city"
            })
    
    # If still searching, fetch from geocoding API for international locations
    if len(results) < 5:
        try:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=50&language=en&format=json"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                api_results = data.get("results", [])
                
                for item in api_results:
                    city_name = item.get("name", "")
                    state_name = item.get("admin1", "")
                    country_name = item.get("country", "")
                    
                    # Skip if already in results
                    if any(r["latitude"] == item.get("latitude") and r["longitude"] == item.get("longitude") for r in results):
                        continue
                    
                    if query_lower in city_name.lower() or query_lower in state_name.lower() or query_lower in country_name.lower():
                        name_parts = [city_name]
                        if state_name:
                            name_parts.append(state_name)
                        if country_name:
                            name_parts.append(country_name)
                        
                        results.append({
                            "name": city_name,
                            "full_name": ", ".join(name_parts),
                            "latitude": item.get("latitude"),
                            "longitude": item.get("longitude"),
                            "type": "location"
                        })
                    
                    if len(results) >= 10:
                        break
        except:
            pass
    
    # Limit results to 10
    return jsonify(results[:10])

@app.route("/api/summary")
def get_summary():
    location = request.args.get("location", "").strip()
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    lang = request.args.get("lang", "en").strip().lower()
    location_name = "Custom Coordinates"

    try:
        # 1. Geocoding
        if not lat or not lon:
            if not location:
                return jsonify({"error": "No location or coordinates provided."}), 400
            
            preset_key = location.lower().replace(" ", "")
            if preset_key in DEMO_PRESETS:
                lat = DEMO_PRESETS[preset_key]["lat"]
                lon = DEMO_PRESETS[preset_key]["lon"]
                location_name = DEMO_PRESETS[preset_key]["name"]
            else:
                geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=en&format=json"
                response = requests.get(geocode_url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                results = data.get("results")
                if not results:
                    return jsonify({"error": f"Could not find coordinates for location '{location}'."}), 404
                
                res = results[0]
                lat = res["latitude"]
                lon = res["longitude"]
                
                parts = [res.get("name")]
                if res.get("admin1"):
                    parts.append(res.get("admin1"))
                if res.get("country"):
                    parts.append(res.get("country"))
                location_name = ", ".join(parts)
        else:
            lat = float(lat)
            lon = float(lon)
            location_name = request.args.get("name", f"Coordinates: {lat:.4f}, {lon:.4f}")

        # 2. Fetch Weather Forecast (Precipitation + Additional Climatic Telemetry)
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&hourly=precipitation,temperature_2m,relative_humidity_2m,wind_speed_10m,surface_pressure"
            f"&daily=precipitation_sum,precipitation_hours,temperature_2m_max,temperature_2m_min,wind_speed_10m_max,uv_index_max,weather_code"
            f"&timezone=auto"
        )
        weather_res = requests.get(weather_url, timeout=10)
        weather_res.raise_for_status()
        weather_data = weather_res.json()

        # 3. Fetch Hydrological Forecast
        flood_url = (
            f"https://flood-api.open-meteo.com/v1/flood?"
            f"latitude={lat}&longitude={lon}"
            f"&daily=river_discharge"
            f"&timezone=auto"
        )
        flood_res = requests.get(flood_url, timeout=10)
        
        if flood_res.status_code == 200:
            try:
                import json
                cleaned_text = flood_res.text.replace("nan", "null").replace("NaN", "null")
                flood_data = json.loads(cleaned_text)
            except Exception:
                flood_data = {"daily": {"river_discharge": [None] * 7}}
        else:
            flood_data = {"daily": {"river_discharge": [None] * 7}}

        # 4. Process Summarization (including selected language)
        risk_profile = calculate_flood_risk(weather_data, flood_data, lang=lang)
        
        # 5. Extract Climatic Conditions for Dashboard displays
        daily_weather = weather_data.get("daily", {})
        hourly_weather = weather_data.get("hourly", {})
        
        # Get weather description
        w_code = daily_weather.get("weather_code", [0])[0]
        weather_desc = WEATHER_CODES.get(w_code, "Variable Clouds")
        
        # Current climatic values (take first hour or average)
        current_humidity = hourly_weather.get("relative_humidity_2m", [65])[0]
        current_pressure = hourly_weather.get("surface_pressure", [1013])[0]
        peak_wind = daily_weather.get("wind_speed_10m_max", [0.0])[0]
        max_uv = daily_weather.get("uv_index_max", [0.0])[0]
        temp_max = daily_weather.get("temperature_2m_max", [20.0])[0]
        temp_min = daily_weather.get("temperature_2m_min", [15.0])[0]

        # Inject details
        risk_profile["location"] = {
            "name": location_name,
            "latitude": lat,
            "longitude": lon
        }
        
        risk_profile["climate"] = {
            "weather_code": w_code,
            "weather_description": weather_desc,
            "humidity": current_humidity,
            "surface_pressure": round(current_pressure, 1),
            "max_wind_speed": round(peak_wind, 1),
            "max_uv_index": round(max_uv, 1),
            "temp_max": round(temp_max, 1),
            "temp_min": round(temp_min, 1)
        }
        
        risk_profile["visuals"] = {
            "dates": weather_data.get("daily", {}).get("time", []),
            "precipitation": weather_data.get("daily", {}).get("precipitation_sum", []),
            "river_discharge": flood_data.get("daily", {}).get("river_discharge", [0.0]*7),
            "temp_max": daily_weather.get("temperature_2m_max", []),
            "temp_min": daily_weather.get("temperature_2m_min", [])
        }
        
        return jsonify(risk_profile)

    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Failed to connect to weather or flood telemetry database.",
            "details": str(e)
        }), 502
    except Exception as e:
        return jsonify({
            "error": "An internal error occurred during telemetry processing.",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


def extract_location_from_message(message):
    import urllib.parse
    clean = message.replace("?", "").replace(".", "").replace(",", "").replace("!", "").strip()
    words = clean.split()
    
    stop_words = {
        "what", "is", "the", "weather", "in", "about", "for", "how", "to", "danger", 
        "flood", "risk", "level", "of", "in", "at", "on", "discharge", "rain", 
        "precipitation", "safety", "kit", "bag", "hello", "hi", "hey", "please", "tell", "me",
        "a", "an", "and", "but", "or", "if", "you", "he", "she", "they", "we", "us", "are", "have", "has", "had", "was", "were",
        "where", "when", "why", "there", "here", "who", "whom", "whose", "which"
    }
    
    # Pre-calculated typo dictionary to resolve citizen misspells
    TYPO_CORRECTIONS = {
        "antartica": "antarctica",
        "antartic": "antarctica",
        "indias": "india",
        "belgum": "belgium",
    }
    
    candidates = [w for w in words if w.lower() not in stop_words]
    if not candidates:
        return None
        
    for word in reversed(candidates):
        if len(word) > 2:
            word_clean = word.lower().strip()
            word_corrected = TYPO_CORRECTIONS.get(word_clean, word_clean)
            try:
                url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(word_corrected)}&count=1&language=en&format=json"
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    results = res.json().get("results", [])
                    if results:
                        item = results[0]
                        parts = [item.get("name")]
                        if item.get("admin1"):
                            parts.append(item.get("admin1"))
                        if item.get("country"):
                            parts.append(item.get("country"))
                        return {
                            "name": item.get("name"),
                            "full_name": ", ".join(parts),
                            "latitude": item.get("latitude"),
                            "longitude": item.get("longitude")
                        }
            except Exception:
                pass
    return None

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Simulates a generative AI Chatbot responder for flood safety queries.
    Utilizes current telemetry context, but dynamically overrides and queries
    weather and flood metrics if the user asks about a different location (e.g. Antarctica).
    """
    req_data = request.get_json() or {}
    message = req_data.get("message", "").strip()
    context = req_data.get("context", {})
    
    if not message:
        return jsonify({"response": "I didn't receive your question. How can I assist you with flood preparedness?"})

    # Heuristic: Check if user is inquiring about a different location
    resolved_loc = extract_location_from_message(message)
    if resolved_loc:
        loc_name = resolved_loc["name"]
        loc_full = resolved_loc["full_name"]
        lat = resolved_loc["latitude"]
        lon = resolved_loc["longitude"]
        
        try:
            # Query target location weather
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}"
                f"&hourly=precipitation,temperature_2m"
                f"&daily=precipitation_sum,precipitation_hours,weather_code"
                f"&timezone=auto"
            )
            weather_res = requests.get(weather_url, timeout=10)
            weather_res.raise_for_status()
            weather_data = weather_res.json()

            # Query target location river discharge
            flood_url = (
                f"https://flood-api.open-meteo.com/v1/flood?"
                f"latitude={lat}&longitude={lon}"
                f"&daily=river_discharge"
                f"&timezone=auto"
            )
            flood_res = requests.get(flood_url, timeout=10)
            if flood_res.status_code == 200:
                try:
                    import json
                    cleaned_text = flood_res.text.replace("nan", "null").replace("NaN", "null")
                    flood_data = json.loads(cleaned_text)
                except Exception:
                    flood_data = {"daily": {"river_discharge": [None] * 7}}
            else:
                flood_data = {"daily": {"river_discharge": [None] * 7}}

            # Run risk computations
            risk_profile = calculate_flood_risk(weather_data, flood_data)
            
            risk_level = risk_profile["risk_level"]
            risk_score = risk_profile["risk_score"]
            risk_badge = risk_profile["risk_badge"]
            precip = risk_profile["metrics"]["total_precip_7d"]
            discharge = risk_profile["metrics"]["peak_discharge"]
            
            # Weather status description
            w_code = weather_data.get("daily", {}).get("weather_code", [0])[0]
            weather_desc = WEATHER_CODES.get(w_code, "Variable Skies")
            
            discharge_str = f"{discharge} m³/s" if discharge is not None else "N/A (No river nearby)"
            
            # Build custom localized AI response
            response = (
                f"### 🌐 Dynamic Sensor Telemetry: {loc_full}\n\n"
                f"I detected that you are asking about **{loc_name}** and have scanned the active meteorological sensors for its coordinates (Lat: {lat:.4f}, Lon: {lon:.4f}):\n\n"
                f"* **Current Climate Status**: **{weather_desc}**\n"
                f"* **Early Warning Badge**: **{risk_badge}** (Threat Score: **{risk_score}/10**)\n"
                f"* **Cumulative Rain (7D)**: **{precip} mm**\n"
                f"* **Projected River Flow**: **{discharge_str}**\n\n"
                f"**Assessment**: "
            )
            
            if risk_level == "EXTREME":
                response += f"Severe flood warning active for {loc_name}. Evacuate immediately if local authorities instruct you. Avoid low-lying river banking."
            elif risk_level == "HIGH":
                response += f"High flood warnings active for {loc_name}. Heavy rain sums of {precip}mm forecast. Secure outdoor items and prepare emergency checklists."
            elif risk_level == "MODERATE":
                response += f"Moderate risk in {loc_name}. Some local street water pooling could occur during peak hours. Gutters and sump pumps should be cleared."
            else:
                response += f"Conditions are stable and normal in {loc_name}. Telemetry readings show no danger levels or thunderstorm risks."
            
            return jsonify({"response": response})
        except Exception as e:
            # Fallback to general context if location query fails
            pass
        
    location = context.get("location_name", "Unknown Location")
    risk_level = context.get("risk_level", "NORMAL")
    risk_score = context.get("risk_score", 0.0)
    precip = context.get("precipitation", 0.0)
    discharge = context.get("discharge", None)
    
    msg_lower = message.lower()
    
    # AI Dialogue Engine
    if "hello" in msg_lower or "hi" in msg_lower or "hey" in msg_lower:
        response = (
            f"Hello! I am your **HydroGuard Generative Safety Assistant**.\n\n"
            f"I have scanned the telemetry metrics for **{location}** (Risk Level: **{risk_level}** with score **{risk_score}/10**).\n\n"
            f"How can I help you prepare today? You can ask me about emergency kits, evacuation advice, "
            f"or specific warnings related to {location}."
        )
    elif "evacuate" in msg_lower or "evacuation" in msg_lower or "leave" in msg_lower:
        if risk_level in ["EXTREME", "HIGH"]:
            response = (
                f"### 🚨 Critical Evacuation Protocol for {location}\n\n"
                f"With a **{risk_level}** risk alert active, you should prepare for immediate evacuation if local officials issue orders:\n\n"
                f"1. **Identify Escape Routes**: Pinpoint higher-ground locations. Avoid any path crossing waterways or underpasses.\n"
                f"2. **Disconnect Utilities**: Turn off water, gas, and electricity at main breakers before leaving if safe.\n"
                f"3. **Do Not Walk or Drive Through Floodwaters**: Just 15cm of flowing water can knock an adult down. Vehicles float easily in 60cm of water.\n"
                f"4. **Emergency Services**: Keep local municipal helplines pre-saved. Monitor regional radio bulletins."
            )
        else:
            response = (
                f"### 🛡️ Evacuation Preparedness Advice for {location}\n\n"
                f"Currently, the warning status for **{location}** is **{risk_level}** (Score: {risk_score}/10). Evacuation is **not** currently required.\n\n"
                f"However, it is always a best practice to know your zone's evacuation routes and have a planned meeting spot for family members. "
                f"Would you like advice on how to build an emergency bag?"
            )
    elif "kit" in msg_lower or "bag" in msg_lower or "supplies" in msg_lower or "emergency" in msg_lower:
        response = (
            f"### 📦 AI Safety Checklist: Emergency Go-Bag\n\n"
            f"For residents in **{location}**, having a pre-packed emergency kit is vital. Pack these essential items in waterproof bags:\n\n"
            f"* **Hydration & Nutrition**: 3 gallons of fresh water per person, dry high-energy foods (nuts, bars, canned goods).\n"
            f"* **Medical Support**: First-aid supplies, essential medications, and copies of prescriptions.\n"
            f"* **Power & Communication**: Fully-charged power banks, AA batteries, and a battery-powered weather radio.\n"
            f"* **Verification Papers**: ID cards, insurance policies, property deeds, and cash (ATMs may go offline).\n"
            f"* **Sanitation**: Wet wipes, trash bags, change of dry clothes, and blankets."
        )
    elif "m3/s" in msg_lower or "discharge" in msg_lower or "river" in msg_lower or "water" in msg_lower:
        if discharge is not None and discharge > 0.1:
            response = (
                f"### 🌊 Hydrological Analysis for {location}\n\n"
                f"The maximum river discharge projection is **{discharge} m³/s** during the 7-day forecast cycle.\n\n"
                f"**What does this metric mean?**\n"
                f"* *Cubic Meters per Second (m³/s)* measures the volume of water passing a sensor point. A higher multiplier relative to baseline shows potential channel overflow.\n"
                f"* Current analysis shows a risk rating of **{risk_level}** due to this flow rate. "
                f"If the rate surges rapidly, localized creek banking will saturate neighboring channels, driving immediate flooding."
            )
        else:
            response = (
                f"### 🌊 River Flow Telemetry\n\n"
                f"There are no major registered river telemetry gauges within the immediate coordinates of **{location}**.\n\n"
                f"However, flash flooding is still possible from heavy precipitation and urban runoff. Runoff velocity is estimated at **{risk_score}/10** based on local surface terrain."
            )
    elif "rain" in msg_lower or "precipitation" in msg_lower or "weather" in msg_lower:
        response = (
            f"### 🌧️ Meteorological Telemetry Review\n\n"
            f"Our forecast registers a cumulative 7-day rain volume of **{precip} mm** for **{location}**.\n\n"
            f"**Precipitation Scale Index:**\n"
            f"* **< 15 mm**: Low/Safe. Infiltration carries water directly into aquifers.\n"
            f"* **15 - 50 mm**: Moderate. Local street pooling and drainage clogging are possible.\n"
            f"* **50 - 120 mm**: High. Storm sewers back up, driving street flooding.\n"
            f"* **> 120 mm**: Extreme. Flash flood triggers occur quickly.\n\n"
            f"With **{location}** sitting at **{precip} mm**, the forecast suggests a meteorological threat tier of **{risk_level}**."
        )
    elif "lean canvas" in msg_lower or "business" in msg_lower or "revenue" in msg_lower:
        response = (
            f"### 📋 Lean Canvas Business Model Integration\n\n"
            f"The **HydroGuard AI** startup is structured around the **Lean Canvas** business model shown on the Product tab:\n\n"
            f"* **The Problem**: Late weather warnings, confusing metrics, and lack of localized warnings in vulnerable rural areas.\n"
            f"* **The Solution**: An AI-powered early warning dashboard compiling real-time weather/hydrology data and summarizing risks using local translations.\n"
            f"* **Unfair Advantage**: Generative AI-driven multilingual reports and integrated chatbots rather than raw sensor telemetry spreadsheets.\n"
            f"* **Revenue Channels**: B2G subscriptions, NGO partnerships, enterprise API licensing, and corporate CSR sponsorships."
        )
    else:
        response = (
            f"I understand your query regarding flood safety in **{location}**.\n\n"
            f"Based on the **{risk_level}** risk alert status (Score: **{risk_score}/10**), you should remain alert. "
            f"For flash floods, seek higher ground. For river overflows, pack sandbags and monitor warning streams. "
            f"Please specify if you want to know about **Emergency Kits**, **Evacuation Paths**, or **Rainfall Metrics**."
        )
        
    return jsonify({"response": response})

if __name__ == "__main__":
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static/css", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)

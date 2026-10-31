import json
import os
import urllib.parse
import urllib.request
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# 1. Environment & API Key Setup
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback: simple .env parser if python-dotenv is not installed
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY environment variable is not set. "
        "Please create a .env file with GEMINI_API_KEY=your_key or set it in your system."
    )

client = genai.Client(api_key=api_key)

# ---------------------------------------------------------------------------
# 2. Tool Implementation (Free Open-Meteo Weather API)
#    No API key required for Open-Meteo. Uses built-in urllib (no extra pip installs).
# ---------------------------------------------------------------------------
def _fetch_json(url: str, params: dict) -> dict:
    """Helper to perform HTTP GET requests using Python standard library."""
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    req = urllib.request.Request(full_url, headers={"User-Agent": "WeatherAgent/1.0"})
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def get_current_weather(city: str) -> dict:
    """
    Fetches the current weather for a specified city using free public APIs:
    1. Open-Meteo Geocoding API to resolve city name to latitude/longitude.
    2. Open-Meteo Forecast API to obtain real-time temperature, windspeed, and weather conditions.
    """
    try:
        # Step A: Convert city name to coordinates
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {"name": city, "count": 1, "language": "en", "format": "json"}
        geo_data = _fetch_json(geo_url, geo_params)

        if not geo_data.get("results"):
            return {"error": f"City '{city}' not found."}

        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        resolved_name = f"{location.get('name')}, {location.get('country')}"

        # Step B: Fetch current weather metrics
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
        }
        weather_data = _fetch_json(weather_url, weather_params)

        current = weather_data.get("current_weather", {})
        
        return {
            "city": resolved_name,
            "temperature_celsius": current.get("temperature"),
            "windspeed_kmh": current.get("windspeed"),
            "weather_code": current.get("weathercode"),
            "time": current.get("time"),
        }
    except Exception as e:
        return {"error": f"Failed to retrieve weather data: {str(e)}"}


def get_current_time(timezone: str = "Europe/Prague") -> dict:
    """
    Fetches the current local time and date for a given IANA timezone (e.g. Europe/Prague, America/New_York, Asia/Tokyo).
    Uses standard library datetime & zoneinfo (no external API needed).
    """
    try:
        tz = zoneinfo.ZoneInfo(timezone)
        now = datetime.now(tz)
        return {
            "timezone": timezone,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "day_of_week": now.strftime("%A"),
        }
    except Exception as e:
        return {"error": f"Invalid timezone '{timezone}'. Example valid timezones: 'Europe/Prague', 'UTC', 'America/New_York'. Error: {str(e)}"}


# Map tool names to their corresponding Python callable
AVAILABLE_TOOLS = {
    "get_current_weather": get_current_weather,
    "get_current_time": get_current_time,
}

# ---------------------------------------------------------------------------
# 3. Tool Declarations for Gemini
# ---------------------------------------------------------------------------
weather_tool_declaration = {
    "name": "get_current_weather",
    "description": "Get real-time weather information such as temperature and windspeed for a given city.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The name of the city, e.g. Prague, London, Tokyo",
            }
        },
        "required": ["city"],
    },
}

time_tool_declaration = {
    "name": "get_current_time",
    "description": "Get the current time, date and day of the week for a specific timezone (e.g. 'Europe/Prague', 'America/New_York', 'Asia/Tokyo').",
    "parameters": {
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": "The IANA timezone name, e.g. 'Europe/Prague', 'America/New_York', 'Asia/Tokyo'. Defaults to 'Europe/Prague'.",
            }
        },
        "required": [],
    },
}

gemini_tools = types.Tool(function_declarations=[weather_tool_declaration, time_tool_declaration])
config = types.GenerateContentConfig(tools=[gemini_tools])

# ---------------------------------------------------------------------------
# 4. Agent Execution Loop
# ---------------------------------------------------------------------------
# 2. Tool Implementation (Free Open-Meteo API)
#    No API key required for Open-Meteo. Uses built-in urllib (no extra pip installs).
# ---------------------------------------------------------------------------
def _fetch_json(url: str, params: dict) -> dict:
    """Helper to perform HTTP GET requests using Python standard library."""
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    req = urllib.request.Request(full_url, headers={"User-Agent": "WeatherAgent/1.0"})
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def get_current_weather(city: str) -> dict:
    """
    Fetches the current weather for a specified city using free public APIs:
    1. Open-Meteo Geocoding API to resolve city name to latitude/longitude.
    2. Open-Meteo Forecast API to obtain real-time temperature, windspeed, and weather conditions.
    """
    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {"name": city, "count": 1, "language": "en", "format": "json"}
        geo_data = _fetch_json(geo_url, geo_params)

        if not geo_data.get("results"):
            return {"error": f"City '{city}' not found."}

        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        resolved_name = f"{location.get('name')}, {location.get('country')}"

        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
        }
        weather_data = _fetch_json(weather_url, weather_params)
        current = weather_data.get("current_weather", {})
        
        return {
            "city": resolved_name,
            "temperature_celsius": current.get("temperature"),
            "windspeed_kmh": current.get("windspeed"),
            "weather_code": current.get("weathercode"),
            "time": current.get("time"),
        }
    except Exception as e:
        return {"error": f"Failed to retrieve weather data: {str(e)}"}


def get_current_time(city: str) -> dict:
    """
    Fetches the current local time, timezone, and date for any city or location
    via Open-Meteo API (works across all platforms without local tzdata).
    """
    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {"name": city, "count": 1, "language": "en", "format": "json"}
        geo_data = _fetch_json(geo_url, geo_params)

        if not geo_data.get("results"):
            return {"error": f"City '{city}' not found."}

        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        timezone_name = location.get("timezone", "auto")
        resolved_name = f"{location.get('name')}, {location.get('country')}"

        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "timezone": timezone_name,
        }
        data = _fetch_json(weather_url, weather_params)
        current = data.get("current_weather", {})
        iso_time = current.get("time", "")

        # Format time and date nicely
        date_part, time_part = (iso_time.split("T") if "T" in iso_time else (iso_time, ""))

        return {
            "city": resolved_name,
            "timezone": data.get("timezone", timezone_name),
            "current_date": date_part,
            "current_time": time_part,
        }
    except Exception as e:
        return {"error": f"Failed to retrieve current time: {str(e)}"}


# Map tool names to their corresponding Python callable
AVAILABLE_TOOLS = {
    "get_current_weather": get_current_weather,
    "get_current_time": get_current_time,
}

# ---------------------------------------------------------------------------
# 3. Tool Declarations for Gemini
# ---------------------------------------------------------------------------
weather_tool_declaration = {
    "name": "get_current_weather",
    "description": "Get real-time weather information such as temperature and windspeed for a given city.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The name of the city, e.g. Prague, London, Tokyo",
            }
        },
        "required": ["city"],
    },
}

time_tool_declaration = {
    "name": "get_current_time",
    "description": "Get the current local time, date, and timezone for any city in the world.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city to query local time for, e.g. Tokyo, New York, Prague",
            }
        },
        "required": ["city"],
    },
}

gemini_tools = types.Tool(function_declarations=[weather_tool_declaration, time_tool_declaration])
config = types.GenerateContentConfig(tools=[gemini_tools])

# ---------------------------------------------------------------------------
# 4. Agent Execution Loop
# ---------------------------------------------------------------------------
def run_agent_turn(user_prompt: str, model: str = "gemini-3.6-flash"):
    print(f"\nUser: {user_prompt}\n" + "-" * 50)

    # Conversation history tracking
    contents = [
        types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)])
    ]

    while True:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )

        candidate = response.candidates[0]
        # Append assistant's turn to conversation history
        contents.append(candidate.content)

        function_calls = [
            part.function_call
            for part in candidate.content.parts
            if part.function_call is not None
        ]

        # If no tool calls requested, we reached the final text answer
        if not function_calls:
            print("\n--- Final Agent Response ---")
            print(response.text)
            break

        # Process each tool call and prepare tool responses
        tool_response_parts = []
        for call in function_calls:
            tool_name = call.name
            tool_args = call.args

            print(f"Tool Requested: '{tool_name}' with arguments: {dict(tool_args)}")

            if tool_name not in AVAILABLE_TOOLS:
                tool_result = {"error": f"Tool '{tool_name}' is not recognized."}
            else:
                tool_result = AVAILABLE_TOOLS[tool_name](**tool_args)

            print(f"Tool Execution Output: {json.dumps(tool_result, ensure_ascii=False)}")

            tool_response_parts.append(
                types.Part.from_function_response(
                    name=tool_name,
                    response={"result": tool_result},
                )
            )

        # Feed the tool responses back as the next user turn
        contents.append(types.Content(role="user", parts=tool_response_parts))


if __name__ == "__main__":
    # Test 1: Model should choose 'get_current_time'
    run_agent_turn("Kolik je právě teď hodin v Tokiu?", model="gemini-3.6-flash")

    # Test 2: Model should choose 'get_current_weather'
    run_agent_turn("Jaká je aktuální teplota v Londýně?", model="gemini-3.6-flash")
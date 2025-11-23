from typing import Any
import sys
import httpx
from mcp.server.fastmcp import FastMCP


def debug(msg: str):
    """Print debug message to stderr (stdout is reserved for MCP protocol)"""
    print(f"[DEBUG] {msg}", file=sys.stderr)


mcp = FastMCP("weather")
debug("Weather MCP server initialized")

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling"""

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPError, httpx.TimeoutException, KeyError, ValueError):
        return None
        
def format_alert(feature: dict) -> str:
    """Format an alert feature into readable string"""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

@mcp.tool()
async def get_alert(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    debug(f"get_alert called with state={state}")

    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)
    debug(f"get_alert response: {data is not None}")

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."
    
    if not data["features"]:
        return "No active alerts for this state."
    
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    debug(f"get_forecast called with latitude={latitude}, longitude={longitude}")

    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)
    debug(f"get_forecast points response: {points_data is not None}")

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

def main():
    # Initialize and run the server
    debug("Starting MCP server with stdio transport...")
    mcp.run(transport='stdio')
    debug("MCP server stopped")

if __name__ == "__main__":
    main()

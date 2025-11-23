import requests

# Replace this with your actual ORS API key
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6Ijg4MDczNmU1MmMzYjQ4YjBhNWE0MDRiOTFmOTllZDM2IiwiaCI6Im11cm11cjY0In0="

def get_road_distance(source_lat, source_lon, dest_lat, dest_lon):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            [source_lon, source_lat],  # Note: ORS expects [lon, lat]
            [dest_lon, dest_lat]
        ]
    }

    try:
        response = requests.post(url, json=body, headers=headers)

        if response.status_code != 200:
            print("❌ API Error or Invalid Response:")
            print(response.text)
            return 0, 0  # default fallback

        data = response.json()
        print("✅ Route successfully received!")

        distance_meters = data['routes'][0]['summary']['distance']
        duration_seconds = data['routes'][0]['summary']['duration']

        # Convert to kilometers and minutes
        distance_km = distance_meters / 1000
        duration_min = duration_seconds / 60

        return distance_km, duration_min

    except Exception as e:
        print("❌ Exception while fetching route:", e)
        return 0, 0

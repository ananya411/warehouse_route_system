import requests

def get_optimized_route(url, body, headers):
    response = requests.post(url, json=body, headers=headers)

    if response.status_code != 200:
        print("❌ API Error or Invalid Response:")
        print(response.text)
        return None
    else:
        data = response.json()
        print("✅ Route successfully received!")
        print(f"Total Distance: {data['routes'][0]['summary']['distance']} meters")
        print(f"Total Duration: {data['routes'][0]['summary']['duration']} seconds")
        return data

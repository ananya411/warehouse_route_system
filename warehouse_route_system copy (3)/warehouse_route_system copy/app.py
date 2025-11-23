from flask import Flask, render_template, session, redirect, request
from auth import auth_bp
from warehouse_manager import warehouse_bp, load_warehouses
import os
from ors_utils import get_road_distance

app = Flask(__name__)
app.secret_key = 'super_secret_key'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.register_blueprint(auth_bp)
app.register_blueprint(warehouse_bp)

# 👇 Store your OpenRouteService API key (either from env or hardcoded)
ORS_API_KEY = os.getenv('ORS_API_KEY', 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6Ijg4MDczNmU1MmMzYjQ4YjBhNWE0MDRiOTFmOTllZDM2IiwiaCI6Im11cm11cjY0In0=')  # Replace with your key

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    warehouses = load_warehouses()
    warehouse_names = [w['name'] for w in warehouses]
    item_counts = [len(w['items']) for w in warehouses]

    return render_template(
        'dashboard.html',
        user=session['user'],
        role=session['role'],
        warehouses=warehouses,
        chart_labels=warehouse_names,
        chart_data=item_counts,
        route=session.get('route'),
        ors_api_key=ORS_API_KEY  # 👈 Pass to template
    )

@app.route('/optimize-route', methods=['POST'])
def optimize_route():
    warehouses = load_warehouses()
    source_idx = int(request.form['source'])
    dest_idx = int(request.form['destination'])

    source = warehouses[source_idx]
    destination = warehouses[dest_idx]

    distance_km, duration_min = get_road_distance(
        source['location']['lat'], source['location']['lon'],
        destination['location']['lat'], destination['location']['lon']
    )

    session['route'] = {
        'source': source['city'],
        'destination': destination['city'],
        'distance_km': round(distance_km, 2),
        'duration_min': round(duration_min, 1),
        'source_lat': source['location']['lat'],
        'source_lon': source['location']['lon'],
        'destination_lat': destination['location']['lat'],
        'destination_lon': destination['location']['lon']
    }

    return redirect('/dashboard')

if __name__ == '__main__':
    os.makedirs("data", exist_ok=True)
    app.run(debug=True)

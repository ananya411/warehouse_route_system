import json
import os
from flask import Blueprint, render_template, request, redirect, session, flash, url_for, current_app
from werkzeug.utils import secure_filename

warehouse_bp = Blueprint('warehouse', __name__)

WAREHOUSE_FILE = 'data/warehouses.json'
UPLOAD_FOLDER = 'static/uploads'

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 📥 Load warehouse data
def load_warehouses():
    if not os.path.exists(WAREHOUSE_FILE):
        return []
    with open(WAREHOUSE_FILE, 'r') as f:
        return json.load(f)

# 💾 Save updated warehouse data
def save_warehouses(data):
    with open(WAREHOUSE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# 🏢 Add a new warehouse (Admin only)
@warehouse_bp.route('/add-warehouse', methods=['GET', 'POST'])
def add_warehouse():
    if 'user' not in session or session['role'] != 'admin':
        return redirect('/')

    if request.method == 'POST':
        try:
            name = request.form['name']
            city = request.form['city']
            lat = float(request.form['lat'])
            lon = float(request.form['lon'])

            warehouses = load_warehouses()
            warehouses.append({
                'name': name,
                'city': city,
                'location': {'lat': lat, 'lon': lon},
                'items': []
            })
            save_warehouses(warehouses)
            flash("✅ Warehouse added successfully.")
            return redirect('/dashboard')

        except (KeyError, ValueError):
            flash("⚠️ Invalid data. Please fill out all fields correctly.")
            return redirect('/add-warehouse')

    return render_template('add_warehouse.html')

# 📦 Manage items in a warehouse
@warehouse_bp.route('/warehouse/<int:wid>', methods=['GET', 'POST'])
def manage_items(wid):
    if 'user' not in session or session['role'] != 'admin':
        return redirect('/')

    warehouses = load_warehouses()

    if wid < 0 or wid >= len(warehouses):
        return "Warehouse not found", 404

    if request.method == 'POST':
        try:
            item_name = request.form['item']
            qty = int(request.form['quantity'])
            image_url = request.form.get('image_url', '').strip()
            image_file = request.files.get('image_file')

            # Default to URL unless file is uploaded
            image_path = image_url
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                image_file.save(filepath)
                image_path = url_for('static', filename=f'uploads/{filename}')

            warehouses[wid].setdefault('items', [])
            warehouses[wid]['items'].append({
                'name': item_name,
                'quantity': qty,
                'image': image_path
            })
            save_warehouses(warehouses)
            flash("✅ Item added successfully.")
            return redirect(f'/warehouse/{wid}')

        except (KeyError, ValueError):
            flash("⚠️ Invalid item input.")

    selected = warehouses[wid]
    items = selected.get('items', [])
    return render_template('manage_items.html', warehouse=selected, wid=wid, items=items)

# ❌ Delete item
@warehouse_bp.route('/warehouse/<int:wid>/delete/<int:item_id>')
def delete_item(wid, item_id):
    warehouses = load_warehouses()

    if wid < 0 or wid >= len(warehouses):
        return "Warehouse not found", 404

    if item_id < 0 or item_id >= len(warehouses[wid].get('items', [])):
        return "Item not found", 404

    del warehouses[wid]['items'][item_id]
    save_warehouses(warehouses)
    flash("🗑️ Item deleted successfully.")
    return redirect(f'/warehouse/{wid}')

# ✏️ Edit item
@warehouse_bp.route('/warehouse/<int:wid>/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(wid, item_id):
    warehouses = load_warehouses()

    if wid < 0 or wid >= len(warehouses):
        return "Warehouse not found", 404

    items = warehouses[wid].get('items', [])
    if item_id < 0 or item_id >= len(items):
        return "Item not found", 404

    item = items[item_id]

    if request.method == 'POST':
        item['name'] = request.form['item']
        item['quantity'] = int(request.form['quantity'])
        image_url = request.form.get('image_url', '').strip()
        image_file = request.files.get('image_file')

        # Prefer uploaded file over URL
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(filepath)
            item['image'] = url_for('static', filename=f'uploads/{filename}')
        elif image_url:
            item['image'] = image_url

        save_warehouses(warehouses)
        flash("✏️ Item updated successfully.")
        return redirect(f'/warehouse/{wid}')

    return render_template('edit_item.html', item=item, wid=wid, item_id=item_id)

from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

vehicle_data = {}

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/update', methods=['POST'])
def update_dashboard():
    vehicle_id = request.form.get('vehicle_id')
    points_size = request.form.get('points_size')

    if vehicle_id not in vehicle_data:
        vehicle_data[vehicle_id] = {
            'points_size': points_size,
        }
        print(f'New vehicle joined: {vehicle_id}')

    else:
        vehicle_data[vehicle_id]['points_size'] = points_size

    print(f'Updated vehicle {vehicle_id}: points_size={points_size}')
    return 'OK'

@app.route('/get_vehicle_data')
def get_vehicle_data():
    return jsonify(vehicle_data)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)

# from flask import Flask, request

# app = Flask(__name__)

# vehicle_data = {}


# @app.route('/update', methods=['POST'])
# def update_dashboard():
#     vehicle_id = request.form.get('vehicle_id')
#     points_size = request.form.get('points_size')

#     if vehicle_id not in vehicle_data:
#         vehicle_data[vehicle_id] = {
#             'points_size': points_size,
#         }
#         print(f'New vehicle joined: {vehicle_id}')

#     else:
#         vehicle_data[vehicle_id]['points_size'] = points_size

#     print(f'Updated vehicle {vehicle_id}: points_size={points_size}')
#     return 'OK'


# if __name__ == '__main__':
#     app.run(debug=True,host='127.0.0.1', port=5001)

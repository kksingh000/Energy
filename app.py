from flask import Flask, render_template, request, jsonify
from electricity_prediction_model import ElectricityPredictor
from datetime import datetime

app = Flask(__name__)

# Load the trained model
predictor = ElectricityPredictor.load_model('electricity_predictor.joblib')

def get_current_season():
    month = datetime.now().month
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Summer'
    elif month in [6, 7, 8]:
        return 'Monsoon'
    else:
        return 'Autumn'

APPLIANCE_BRANDS = {
    'LED Bulb': {
        'Philips': ['Essential 9W', 'Ultra 9W', 'Smart 9W', 'Master 10W'],
        'Havells': ['Bright 9W', 'Neo 9W', 'Adore 8W', 'Prime 10W'],
        'Wipro': ['Garnet 9W', 'Tejas 9W', 'Next 8W', 'Primo 10W'],
        'Bajaj': ['LEDZ 9W', 'Corona 9W', 'IVORA 8W', 'Elite 10W'],
        'Syska': ['SSK-PAG 9W', 'SSK-BTS 9W', 'RayCE 8W', 'ProX 10W']
    },
    'Ceiling Fan': {
        'Havells': ['Andria 75W', 'Nicola 75W', 'Stealth 75W', 'Festiva 75W'],
        'Orient': ['Ecotech 65W', 'Aeroquiet 75W', 'Electric 70W', 'PSPO 75W'],
        'Crompton': ['HS Plus 60W', 'Energion 75W', 'Aura 75W', 'High Speed 75W'],
        'Usha': ['Striker 75W', 'Technix 75W', 'Aerostyle 75W', 'Swift 70W'],
        'Bajaj': ['Maxima 75W', 'Regal 75W', 'New Bahar 75W', 'Cruise 75W']
    },
    'Air Conditioner': {
        'Daikin': ['FTKF 1.5T', 'JTKJ 1.5T', 'MTKM 1.5T', 'ATKX 1.5T'],
        'Voltas': ['SAC 185V', 'VAC 183V', 'Adjustable 184V', '185V ZZee'],
        'Blue Star': ['IC318', 'IC518', 'LS318', 'FS318'],
        'Hitachi': ['RSOG518', 'KAZE 518', 'ZUNOH 518', 'MERAI 518'],
        'LG': ['MS-Q18', 'PS-Q18', 'LS-Q18', 'KS-Q18']
    },
    'Refrigerator': {
        'LG': ['GL-B201', 'GL-T302', 'GL-D241', 'GL-I302'],
        'Samsung': ['RT28', 'RT30', 'RR20', 'RF28'],
        'Whirlpool': ['IF INV278', 'IF INV305', 'NEO IF278', 'PRO 355'],
        'Godrej': ['RD Edge 200', 'RD AXIS 240', 'RB 210', 'RT EON 240'],
        'Haier': ['HRD-1954', 'HRB-2764', 'HRF-2984', 'HED-2054']
    },
    'Television': {
        'Sony': ['Bravia X75K', 'Bravia X80J', 'Bravia X90J', 'Bravia A80J'],
        'Samsung': ['Crystal 4K', 'QLED Q60A', 'Neo QLED', 'The Frame'],
        'LG': ['UHD 4K', 'NanoCell', 'OLED C1', 'OLED G1'],
        'OnePlus': ['Y Series', 'U Series', 'Q Series', 'TV 55 U1S'],
        'Mi': ['TV 5X', 'TV Q1', 'TV 4X', 'TV P1']
    },
    'Washing Machine': {
        'LG': ['FHM1207', 'T65SKSF4Z', 'FHD1409', 'THD8524'],
        'Samsung': ['WA65A4002VS', 'WW80T504DAN', 'WA65T4262VS', 'WW70T502DAX'],
        'Whirlpool': ['360 BW9061', '360 FF7515', 'Supreme 7014', 'Elite 7212'],
        'IFB': ['Senator Plus', 'Executive Plus', 'Senorita Plus', 'Elite Plus'],
        'Bosch': ['WAJ2426WIN', 'WAJ2846WIN', 'WAB16161IN', 'WLJ2016TIN']
    },
    'Water Heater': {
        'Havells': ['Monza EC 15L', 'Instanio 3L', 'Adonia 25L', 'Primo 15L'],
        'Bajaj': ['New Shakti 15L', 'Juvel 3L', 'Popular 25L', 'Calenta 15L'],
        'AO Smith': ['HSE-VAS 15L', 'EWS-3L', 'HAS-25L', 'SDS-15L'],
        'Racold': ['Pronto Neo 3L', 'Eterno 2 15L', 'Omnis 25L', 'Andris 15L'],
        'V-Guard': ['Sprinhot 3L', 'Divino 15L', 'Pebble 25L', 'Crystal 15L']
    },
    'Room Heater': {
        'Bajaj': ['Majesty RX11', 'Room Heater 2000', 'Flashy 1000', 'Minor 1000'],
        'Havells': ['Cista 2000W', 'Comforter 2000W', 'Calido 2000W', 'Warmio 1000W'],
        'Orient': ['HC2003D', 'HC1801D', 'HC2000D', 'HC1501D'],
        'Usha': ['HC 812T', 'HC 3620', 'HC 3820', 'HC 3420'],
        'Morphy Richards': ['OFR 09', 'OFR 11', 'Room Heater 2000', 'Heat Convector']
    },
    'Water Pump': {
        'Crompton': ['Mini Champ I', 'Mini Champ II', 'Solus', 'Aqua'],
        'Kirloskar': ['Mega 54S', 'Mega 64S', 'Jalraaj', 'Chhotu'],
        'CRI': ['MHBS-2', 'MHBS-3', 'XCHS-2', 'XCHS-3'],
        'V-Guard': ['Revo Plus', 'Stallion Plus', 'Prime', 'Ultron'],
        'KSB': ['Peribloc', 'Etaline', 'Movitec', 'Etanorm']
    },
    'Microwave Oven': {
        'LG': ['MC2846SL', 'MC3286BRUM', 'MJEN326UH', 'MC2886BFUM'],
        'Samsung': ['CE73JD', 'CE1041DSB2', 'MC28H5013AK', 'CE77JD'],
        'IFB': ['20SC2', '25SC4', '30SC4', '20PM1S'],
        'Panasonic': ['NN-CT353B', 'NN-CT36H', 'NN-GT23H', 'NN-GT45H'],
        'Whirlpool': ['Magicook 20L', 'Magicook 25L', 'Magicook 30L', 'Magicook 23L']
    }
}

@app.route('/')
def home():
    return render_template('index.html', appliance_brands=APPLIANCE_BRANDS)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        # Extract family details
        family_details = data['familyDetails']
        appliances = data['appliances']
        
        # Process each appliance and make predictions
        total_consumption = 0
        appliance_predictions = []
        
        for appliance in appliances:
            appliance_data = {
                'family_members': int(family_details['totalMembers']),
                'male': int(family_details['maleMembers']),
                'female': int(family_details['femaleMembers']),
                'children': int(family_details['children']),
                'household_type': family_details['householdType'],
                'appliance_type': appliance['type'],
                'brand': appliance['brand'],
                'model': appliance.get('model', ''),
                'daily_usage_hours': float(appliance['avgUsageHours']),
                'quantity': int(appliance['quantity']),
                'season': get_current_season()
            }
            
            consumption = predictor.predict_consumption(appliance_data)
            
            # Create detailed appliance name with brand and model
            appliance_name = f"{appliance['type']}"
            if appliance['brand']:
                appliance_name += f" ({appliance['brand']}"
                if appliance.get('model'):
                    appliance_name += f" - {appliance['model']}"
                appliance_name += ")"
            
            appliance_predictions.append({
                'type': appliance_name,
                'consumption': round(consumption, 2)
            })
            
            total_consumption += consumption
        
        return jsonify({
            'success': True,
            'total_consumption': round(total_consumption, 2),
            'appliance_predictions': appliance_predictions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True) 
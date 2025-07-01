import asyncio
import aiohttp
import random
from datetime import datetime

async def MonitoringData():
    url = "https://parseapi.back4app.com/classes/UserData"
    headers = {
        'X-Parse-Application-Id':'v1QfYYDQnBWjlWdSGpa40CYw9bLufSzZtR2FWOeX',
        'X-Parse-REST-API-Key': '0PNFHpzpJXWGVYdMhLoQdXNr7oSWTLzbGMdBjXFq',
        'Content-Type': 'application/json',
    }
    
    async with aiohttp.ClientSession() as session:
        while True:
            # Menghasilkan data acak setiap iterasi
            now = datetime.now()
            Day = now.strftime("%a")
            Date = now.strftime("%d/%m/%Y")
            time = now.strftime("%H:%M:%S")
            Position_X = random.randint(0, 360)
            Position_Y = random.randint(0, 360) 
            Yaw = random.randint(0, 360) 
            COG = random.randint(0, 360) 
            SOG_Knot = random.randint(0, 360) 
            SOG_kmperhours = random.randint(0, 360) 
            Lattitude = random.uniform(-90, 90)  # Latitude acak antara -90 dan 90
            Longitude = random.uniform(-180, 180)  # Longitude acak antara -180 dan 180

            data = {
                "Day": Day,
                "Date": Date,
                "Time": time,
                "Position_X": Position_X,
                "Position_Y": Position_Y,
                "Yaw": Yaw,
                "COG": COG,
                "SOG_Knot": SOG_Knot,
                "SOG_kmperhours": SOG_kmperhours,
                "Lattitude": Lattitude,
                "Longitude": Longitude
            }

            await send_data(session, url, headers, data)
            await asyncio.sleep(1)  # Tunggu 1 detik sebelum iterasi berikutnya
            
async def send_data(session, url, headers, data):
    async with session.post(url, json=data, headers=headers) as response:
        if response.status == 201:
            print(data['COG'])
        else:
            print(f"Error: {response.status} - {await response.text()}")

# Jalankan program
asyncio.run(MonitoringData())
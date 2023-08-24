import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from datetime import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)

'''
This code doesn't work as effectively as it should
It creates new variables "Data_Entries" and "Most_Recent_Date", etc. with underscores instead of spaces since Firebase SDK for python doesn't allow spaces

This is the firestore service that will when given a string, patient UID and destination, will send data to the firebase database

To be used in conjunction with the Apple Watch Health app if ever used since the Apple Watch Health app doesn't have the Firebase SDK
'''

# Initialize Firebase
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

'''
Example URL:
http://127.0.0.1:5000/send_string?data=86.00,86.00,2023-08-24T10:42:18&destination=heartRate&patient_uid=9GbhGVsx6bbyeSTsJ1If7XLMW4M2

Sending in the data string in the format the database uses it

Destination: the destination string that is used in firestore

PatientUID: The patient's user identifier

This code does not have bug testing
'''
@app.route('/send_string', methods=['GET'])
async def send_string():

    data_to_send = str(request.args.get('data', 0))
    destination = str(request.args.get('destination', 0))
    patient_uid = str(request.args.get('patient_uid', 0))

    print(data_to_send)

    doc_ref = db.collection("swiftTest").document(patient_uid).collection(destination).document("recordings")
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    try:
        document = doc_ref.get()

        if document.exists:
            data_entries = document._data["Data Entries"]

            try: update_data = {
                "Data_Entries": data_entries + 1,
                str(data_entries + 1): data_to_send,
                "Most_Recent_Date": current_time
            }
            except Exception as f: print(f"Error writing patient profile to Firestore ({f})")

            doc_ref.update(update_data)

            print(f"New recording successfully added {data_to_send}")
            return {"response": "True"}
        else:
            print(f"Document not found, setting new document {data_to_send}")

            # Create a new document if it doesn't exist
            await db.collection("swiftTest").document(patient_uid).set({"docExists": True})

            new_data = {
                "Data_Entries": 1,
                "1": data_to_send,
                "Oldest_Date": current_time,
                "Most_Recent_Date": current_time
            }

            doc_ref.set(new_data)

            return {"response": "True"}
    except Exception as e:
        print(f"Error updating document: {e}")
        return {"response": "False"}

    

# if __name__ == '__main__':
#     asyncio.run(send_string("86.00,86.00,2023-08-24T10:28:18", "heartRate", "9GbhGVsx6bbyeSTsJ1If7XLMW4M2"))

if __name__ == '__main__':
    app.run(debug=False)#, host='0.0.0.0', port=5001)  # Change the port if needed
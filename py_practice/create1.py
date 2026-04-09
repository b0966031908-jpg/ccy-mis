import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc = {
  "name": "楊承智",
  "mail": "b0966031908@gmail.com",
  "lab": 823
}

doc_ref = db.collection("靜宜資管").document("ccy")
doc_ref.set(doc)
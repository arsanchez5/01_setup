import streamlit as st
from pymongo import MongoClient
from bson import ObjectId

# Configuración de MongoDB
MONGO_URI = "mongodb+srv://arsanchez5:OOSnhqHfqXwZw1Bs@cluster-historical.73hxx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster-Historical"
client = MongoClient(MONGO_URI)
db = client["AttackHistory"]
temp_collection = db["TemporaryAlerts"]
historical_collection = db["Alerts"]

# Función para listar alertas pendientes
def list_pending_alerts():
    return list(temp_collection.find({"status": "pending_review"}))

# Función para listar alertas confirmadas
def list_confirmed_alerts():
    return list(historical_collection.find())

# Función para confirmar una alerta como DDoS
def confirm_alert(alert_id):
    alert = temp_collection.find_one({"_id": ObjectId(alert_id)})
    if alert:
        alert['Label'] = 1
        alert.pop('_id')  # Quitar el ID temporal
        alert['recurrence'] = 1
        historical_collection.insert_one(alert)
        temp_collection.delete_one({"_id": ObjectId(alert_id)})
        return f"Alert {alert_id} confirmed as DDoS."
    return f"Alert {alert_id} not found."

# Interfaz de Streamlit
st.title("Alert Management Dashboard")

# Panel de opciones
option = st.sidebar.selectbox("Select Action", ["Pending Alerts", "Confirmed Alerts"])

if option == "Pending Alerts":
    st.header("Pending Alerts")
    pending_alerts = list_pending_alerts()
    for alert in pending_alerts:
        st.subheader(f"Alert ID: {alert['_id']}")
        st.write(f"Source: {alert['src_ap']}")
        st.write(f"Destination: {alert['dst_ap']}")
        st.write(f"Count: {alert['count']}")
        if st.button(f"Confirm as DDoS (ID: {alert['_id']})"):
            result = confirm_alert(str(alert['_id']))
            st.success(result)

elif option == "Confirmed Alerts":
    st.header("Confirmed Alerts")
    confirmed_alerts = list_confirmed_alerts()
    for alert in confirmed_alerts:
        st.subheader(f"Alert ID: {alert['_id']}")
        st.write(f"Source: {alert['src_ap']}")
        st.write(f"Destination: {alert['dst_ap']}")
        st.write(f"Count: {alert['count']}")
        st.write(f"Label: {alert['Label']}")

import requests
import json
import time                          
from kafka import KafkaProducer
from datetime import datetime


crypto_producer = KafkaProducer(
    bootstrap_servers="localhost:9092"
)

url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=false"

while True:
    
    resp = requests.get(url)
    data = resp.json()
    
    for x in data:
        coin_data = {
            'Coin_Name': x['name'],
            "Current_Price": f"{x['current_price']} $",
            "Total_Volume": f"{x['market_cap']} $",
            "High_24h" : x['high_24h'],
            "Low_24h" : x['low_24h'],
            "Image" : x['image'],
            "Updated_At": datetime.now().strftime("%I:%M %p")
        } 
        
        kafka_data = json.dumps(coin_data).encode('utf-8')
        crypto_producer.send("crypto.prices", kafka_data)
  
    crypto_producer.flush()
    print("All messages sent to Kafka!")

    time.sleep(20)     #Wait 1 minute, then repeat

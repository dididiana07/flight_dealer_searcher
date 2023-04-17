import os
import requests
import datetime
from twilio.rest import Client

current_date = datetime.datetime.now()
sheety_endpoint = "https://api.sheety.co/1022e180f0ac414bc9f54f2e2113f351/flightDeals/flights"
ACCOUNT_SID, AUTH_TOKEN = os.environ["ACCOUNT_SID"], os.environ["AUTH_TOKEN"]
client = Client(ACCOUNT_SID, AUTH_TOKEN)

apikey = os.environ["KIWI_API_KEY"]
endpoint = "https://api.tequila.kiwi.com/v2/search"
headers = {
    "apikey": f"{apikey}"
}


def extract_data_from_sheet(url_sheety):
    """Extract the flights key from your Google sheet.
    Return a list of dictionaries in json format."""
    flights_sheet = requests.request(method="GET",
                                     url=url_sheety)
    flights = flights_sheet.json()["flights"]
    return flights


my_flights = extract_data_from_sheet(url_sheety=sheety_endpoint)


for flight in my_flights:
    city = flight["city"]
    iata_code = flight["iataCode"]
    price = flight["lowestPrice"]

    parameters = {
        "fly_from": "BCN",
        "fly_to": f"{iata_code}",
        "date_from": f"{current_date.day}/{current_date.month}/{current_date.year}",
        "date_to": f"{current_date.day}/{(current_date.month + 6) % 12}/{current_date.year}",
        "price_from": "0",
        "price_to": f"{price}"
    }
    kiwi_response = requests.get(url=endpoint, headers=headers, params=parameters)
    kiwi_data = kiwi_response.json()
    try:
        search = kiwi_data["data"][0]
    except IndexError:
        pass
    else:
        messages = client.messages.create(from_=os.environ["TWILIO_PHONE_NUMBER"],
                                          to="",
                                          body="Hey✈️\n"
                                               f"I just found a flight to {city} for the day"
                                               f" {search['local_departure'].split('T')[0]} and for "
                                               f"the price of {search['price']}€.\n"
                                               f"Click link to see more: {search['deep_link']}")


import os
import datetime
import smtplib
import requests

YAHOO_EMAIL = os.environ["YAHOO_EMAIL"]
AUTH_YAHOO = os.environ["AUTH_YAHOO"]
TEQUILA_API_KEY = os.environ["KIWI_API_KEY"]

SHEETY_ENDPOINT_FLIGHTS = ""
SHEETY_ENDPOINT_USERS = ""
TEQUILA_ENDPOINT = "https://api.tequila.kiwi.com/v2/search"


def check_email(email):
    """Unless the email matches, keep asking for it."""
    while True:
        repeat_email = input("Reenter the email:\n")
        if repeat_email == email:
            return True


def create_user():
    """Get the data for a new user."""
    print("Welcome to Diana's Flight Club.\n"
          "We find the best flight deals and email you.")
    name = input("What is your first name?\n")
    last_name = input("What is your last name?\n")
    email = input("What is your email?\n")
    if check_email(email):
        print("Thanks for subscribing to our deals.")
        return name, last_name, email


def add_user(**kwargs):
    """Add the user to the Google sheet."""
    new_user = {
        "user":
            {"name": kwargs["name"],
             "lastName": kwargs["last_name"],
             "email": kwargs["email"]}
    }
    response = requests.request(method="POST", url=SHEETY_ENDPOINT_USERS, json=new_user)
    print(response.status_code)


def get_users_data() -> list:
    """Retrieve all the emails for each user subscribed."""
    response = requests.request(method="GET", url=SHEETY_ENDPOINT_USERS)
    data = [user["email"] for user in response.json()["users"]]
    return data


def get_flights_info() -> list:
    """Returns a list containing dictionaries."""
    response = requests.request(method="GET", url=SHEETY_ENDPOINT_FLIGHTS)
    data = response.json()["flights"]
    return data


def send_mails(users: list, flights_data: list):
    current_date = datetime.datetime.now()
    headers = {
        "apikey": f"{TEQUILA_API_KEY}"
    }
    for flight in flights_data:
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
        response = requests.get(url=TEQUILA_ENDPOINT,
                                headers=headers,
                                params=parameters)
        data = response.json()
        try:
            search = data["data"][0]
        except IndexError:
            pass
        else:
            for user in users:
                with smtplib.SMTP("smtp.mail.yahoo.com") as connection:
                    connection.starttls()
                    connection.login(user=YAHOO_EMAIL, password=AUTH_YAHOO)
                    connection.sendmail(from_addr=YAHOO_EMAIL,
                                        to_addrs=user,
                                        msg=f"Subject:New Deals Alert\n\nI just found a flight to {city} for the day"
                                            f" {search['local_departure'].split('T')[0]} and for the "
                                            f"price of {search['price']} EUR. "
                                            f"\nClick link to see more: {search['deep_link']}")


send_mails(users=get_users_data(), flights_data=get_flights_info())

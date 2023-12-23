import requests
import logging
import json
import getpass

class Better():
    def __init__(self, base_url="https://better-admin.org.uk/api/", origin_url="https://bookings.better.org.uk"):
        self.base_url = base_url
        self.origin_url = origin_url
        self.session = requests.Session()
        self.token = self.getLocalToken()
        # print(self.token)
        if self.token is None or self.token == "":
            self.token = self.getNewToken()
        if self.token is None or self.token == "":
            logging.exception(f"Unable to get a token. Terminating.")
            raise SystemExit()

        self.headers = {}
        self.headers["Origin"] = self.origin_url
        self.headers["Authorization"] = "Bearer " + self.token
        self.headers["Content-Type"] = "application/json"

        # print(self.headers)


    def getLocalToken(self):
        try:
            f = open("token.json", encoding="utf-8")
        except FileNotFoundError as e:
            logging.exception(f"File Not Found error: {e}")
            return
        except e:
            logging.exception(f"Something else happend: {e}")
        
        with f:
            data = json.load(f)
            return data.get("token")


    def _request_wrapper(self, method, path, body):
        url = self.base_url + path
        req = requests.Request(method, url, json=body, headers=self.headers)
        prepped = self.session.prepare_request(req)

        try:
            response = self.session.send(prepped, timeout=30)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logging.exception(f"HTTP error: {e}")
            raise SystemExit()
        except requests.exceptions.Timeout as e:
            logging.exception(f"The request timed out: {e}")
            raise SystemExit()
        except requests.exceptions.RequestException as e:
            logging.exception(f"Exception: {e}")
            raise SystemExit(e)

        if response.text:
            # print(response.text)
            try:
                data = response.json()
            except ValueError as e:
                logging.exception(f"Response parse error: No json returned {e}")
                raise SystemExit(e)
                
        return data
            
    def getNewToken(self):
        username = input("Enter username:")
        password = getpass.getpass('Password:')
        path = f"auth/customer/login"
        body = {
            "username": username,
            "password": password
        }

        response = self._request_wrapper("POST", path, body)

        token = response.get("token")
        if token:
            self.saveLocalToken(token)
            return token
        else:
            logging.exception(f"Faild to get token:")
            raise SystemExit()

    def saveLocalToken(self, token):
        try:
            f = open("token.json", "w", encoding="utf-8")
        except:
            logging.exception(f"Something else happend")
            return
        
        with f:
            json.dump({ "token": token}, f)
            
    def getUser(self):
        path = f"auth/user"

        response = self._request_wrapper("GET", path, "")

        data = response.get("data")
        result = data.get("membership_user").get("id")
        # print(result)
        return result
    
    def getAvailableDates(self, venue_slug, category_slug):
        path = f"activities/venue/{venue_slug}/activity-category/{category_slug}/dates"

        response = self._request_wrapper("GET", path, "")

        data = response.get("data")
        
        result = list(map(lambda x: x.get("raw"), data))
        # print(result)
        return result
    
    
    def getAvailableTimes(self, venue_slug, category_slug, date):
        path = f"activities/venue/{venue_slug}/activity/{category_slug}/times?date={date}"

        response = self._request_wrapper("GET", path, "")

        data = response.get("data")
        result = []
        for i in data:
            if i.get("action_to_show").get("status") == "BOOK" and i.get("spaces") > 0:
                item = {"starts_at": i.get("starts_at").get("format_24_hour"),
                        "ends_at": i.get("ends_at").get("format_24_hour")}
                result.append(item)
        # print(result)
        return result
    
    def getSlotObj(self, venue_slug, category_slug, date, startTime, endTime):
        path = f"activities/venue/{venue_slug}/activity/{category_slug}/slots?date={date}&start_time={startTime}&end_time={endTime}"

        response = self._request_wrapper("GET", path, "")

        data = response.get("data")[0]
        result = {
            "id": data.get("id"),
            "pricing_option_id": data.get("pricing_option_id")
        }
        
        # print(result)
        return result
    
    def addToCart(self, membership_user_id, slot):
        path = f"activities/cart/add"
        body = {
                "items": [
                    {
                        "id": slot["id"],
                        "type": "activity",
                        "pricing_option_id": slot["pricing_option_id"],
                        "apply_benefit": True,
                        "activity_restriction_ids": []
                    }
                ],
                "membership_user_id": membership_user_id,
                "selected_user_id": None
        }

        response = self._request_wrapper("POST", path, body)
        # print(response)
        return
    
    def getCartTotal(self):
        path = f"activities/cart"

        response = self._request_wrapper("GET", path, "")
        data = response.get("data")
        result = data.get("total")
        # print(result)
        return result
       
    def checkout(self):
        path = f"checkout/complete"
        body = {
            "completed_waivers": [],
            "payments": [],
            "selected_user_id": None,
            "source": "activity-booking",
            "terms": [
                1
            ]
        }

        response = self._request_wrapper("POST", path, body)
        result = response.get("complete_order_id")
        print(result)
        return result
    
    def getOrder(self, order_id):
        path = f"activities/orders/{order_id}"

        response = self._request_wrapper("GET", path, "")

        data = response.get("data")
        # print(data)
        return data

    
if __name__ == "__main__":
    logging.basicConfig(
        handlers=[
            logging.StreamHandler()
        ],
        level=logging.INFO, 
        format="%(asctime)s %(message)s", datefmt="%Y/%m/%d %H:%M:%S"
    )
    better = Better()


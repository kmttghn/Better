import logging
from better import Better


class BetterAccount(Better):
    def __init__(self, base_url="https://better-admin.org.uk/api/", origin_url="https://myaccount.better.org.uk",):
        super().__init__(base_url, origin_url)
        # print(self.headers)

    def getBookings(self):
        path = f"my-account/bookings?filter=future"

        response = self._request_wrapper("GET", path, "")

        bookings = response.get("data")
        result = []
        for x in bookings:
            item = {
                "venue_slug": x.get("item").get("location").get("venue_slug"),
                "category_slug": "sauna-steam" if x.get("category") == "Sauna & Steam" else "swim-for-fitness" if x.get("category") == "Swim for Fitness" else "unknown",
                "date": x.get("item").get("date").get("raw"),
                "starts_at": x.get("item").get("starts_at").get("format_24_hour"),
                "status": x.get("status"),
            }
            result.append(item)

        # print(result)
        return result


if __name__ == "__main__":
    logging.basicConfig(
        handlers=[logging.StreamHandler()],
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    betterAccount = BetterAccount()

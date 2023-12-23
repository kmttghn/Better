from better import Better
from betterAccount import BetterAccount
import logging
import datetime

def getNextWeekday(weekdayNum):
    current_date = datetime.date.today()
    return (
        current_date
        + datetime.timedelta((weekdayNum - current_date.weekday() + 7) % 7)
    ).strftime("%Y-%m-%d")

schedules = [
        # {
        #     "venue_slug": "kings-hall-leisure-centre",
        #     "category_slug": "sauna-steam",
        #     "date": getNextWeekday(1),
        #     "starts_at": "18:00",
        #     "ends_at": None,
        #     "status": None,
        # },
        # {
        #     "venue_slug": "britannia-leisure-centre",
        #     "category_slug": "swim-for-fitness",
        #     "date": getNextWeekday(1),
        #     "starts_at": "18:00",
            # "ends_at": None,
        #     "status": None,
        # },
        {
            "venue_slug": "oasis-sports-centre",
            "category_slug": "swim-for-fitness",
            "date": getNextWeekday(2),
            "starts_at": "17:00",
            "ends_at": None,
            "status": None,
        },
        # {
        #     "venue_slug": "kings-hall-leisure-centre",
        #     "category_slug": "sauna-steam",
        #     "date": getNextWeekday(3),
        #     "starts_at": "18:00",
        #     "ends_at": None,
        #     "status": None,
        # },
        # {
        #     "venue_slug": "clissold-leisure-centre",
        #     "category_slug": "sauna-steam",
        #     "date": getNextWeekday(6),
        #     "starts_at": "16:00",
        #     "ends_at": None,
        #     "status": None,
        # },
    ]


def isDateAvailable(date, availableDates):
    for i in availableDates:
        if i == date:
            return True
        
    return False

def isTimeAvailable(time, availableTimes):
    for i in availableTimes:
        if i["starts_at"] == time:
            return True
        
    return False

def getEndTime(time, availableTimes):
    for i in availableTimes:
        if i["starts_at"] == time:
            return i["ends_at"]
        
    return None

def main():
    betterAccount = BetterAccount()
    better = Better()
    membership_user_id = better.getUser()
    bookings = betterAccount.getBookings()

    for schedule in schedules:
        for booked in bookings:
            if (
                schedule["venue_slug"] == booked["venue_slug"]
                and schedule["category_slug"] == booked["category_slug"]
                and schedule["date"] == booked["date"]
                and schedule["starts_at"] == booked["starts_at"]
            ):
                schedule["status"] = "already_booked"
                logging.info(f"The {schedule['category_slug']} on {schedule['date']} at {schedule['starts_at']} in {schedule['venue_slug']} is {schedule['status']}")

#    print(schedules)
    for schedule in filter(lambda x: x["status"] is None, schedules):
        logging.info(f"Processing: The {schedule['category_slug']} on {schedule['date']} at {schedule['starts_at']} in {schedule['venue_slug']} ...")
        availableDates = better.getAvailableDates(schedule["venue_slug"], schedule["category_slug"])
        if not isDateAvailable(schedule["date"], availableDates):
            logging.info(f"The date {schedule['date']} is not available")
            break
        availableTimes = better.getAvailableTimes(schedule["venue_slug"], schedule["category_slug"], schedule["date"])
        if not isTimeAvailable(schedule["starts_at"], availableTimes):
            logging.info(f"The slot {schedule['starts_at']} is not available")
            break
        schedule["ends_at"] = getEndTime(schedule["starts_at"], availableTimes)
        slot = better.getSlotObj(schedule["venue_slug"], schedule["category_slug"], schedule["date"], schedule["starts_at"], schedule["ends_at"])
        if not slot:
            logging.info(f"Failed to fetch slot id")
            break
        better.addToCart(membership_user_id, slot)
        total = better.getCartTotal()
        if total != 0:
            logging.exception(f"The total amount is not 0. Terminating")
            raise SystemExit()
        complete_order_id = better.checkout()
        if complete_order_id:
            logging.info(f"The {schedule['category_slug']} on {schedule['date']} at {schedule['starts_at']} in {schedule['venue_slug']} has been booked!")
            logging.info(better.getOrder(complete_order_id))
 
if __name__ == "__main__":
    logging.basicConfig(
        handlers=[
            logging.FileHandler(r"./better.log", mode="a"),
            logging.StreamHandler(),
        ],
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    logging.info("Started")
    main()
    logging.info("Finished")

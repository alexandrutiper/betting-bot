import storage
import config

FILE = "bankroll.json"


def get_bankroll():

    data = storage.load_json(FILE)

    if not data:

        data = {
            "bankroll": config.START_BANKROLL,
            "history": []
        }

        storage.save_json(FILE, data)

    return data


def update_bankroll(profit):

    data = get_bankroll()

    data["bankroll"] += profit

    data["history"].append(profit)

    storage.save_json(FILE, data)

    return data["bankroll"]
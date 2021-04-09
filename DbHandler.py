import json


def create_user_database():
    data = {'users': []}
    with open("Users.json", "w") as write_file:
        json.dump(data, write_file)


def create_reservation_database():
    date = {'reservations': []}
    with open("reservations.json", "w") as write_file:
        json.dump(date, write_file)


def check_if_user_db_exsists():
    global f
    try:
        f = open("Users.json")
    except IOError:
        create_user_database()
    finally:
        f.close()


def check_if_reservation_db_exsists():
    global f
    try:
        f = open("reservations.json")
    except IOError:
        create_reservation_database()
    finally:
        f.close()


def create_new_user(chat_id, name, cel_number):
    user = {
        chat_id: [
            'name', name,
            'Telefoonnummer', cel_number
        ]
    }
    print(user)

    with open('Users.json', 'r') as json_file:
        data = json.load(json_file)
        json_file.close()

        print(data['users'])
        data["users"].append(user)
        print(data)

    with open('Users.json', 'w') as json_file:
        json.dump(data, json_file)
        json_file.close()


def check_user(chat_id):
    with open('Users.json') as json_file:
        data = json.load(json_file)
        for p in data['users']:
            for key, value in p.items():
                print(key)
                if str(key) == str(chat_id):
                    return True
        return False


def write_away_reservation(data):
    f = open("tempreservation.txt", "a+")
    f.write(data)
    f.close()


def create_new_reservation(chat_id):
    with open("tempreservation.txt", "r+") as temp_reservation:
        data = temp_reservation.read()
        new_data = data.split('-')
        print(new_data)
        temp_reservation.close()

    reservation = {
        chat_id: [
            'CarType', new_data[0],
            'Car', new_data[1],
            'AddressFrom', new_data[2],
            'AddressTO', new_data[3],
            'Time', new_data[4],
            'Date', new_data[5],
        ]
    }

    check_if_reservation_db_exsists()

    with open('reservations.json', 'r') as json_file:
        data = json.load(json_file)
        json_file.close()
        data["reservations"].append(reservation)

    with open('reservations.json', 'w') as json_file:
        json.dump(data, json_file)
        json_file.close()

    f = open("tempreservation.txt", "w")
    f.close()


def get_reservation(chat_id):
    reservations_list = []
    with open('reservations.json', 'r') as json_file:
        data = json.load(json_file)
        for p in data['reservations']:
            for key, value in p.items():
                if str(key) == str(chat_id):
                    reservation = reservation_to_string(value)
                    reservations_list.append(reservation)
        return reservations_list

def reservation_to_string(data):
    message_block = "Car type: " + data[1] + \
                    '\nCar: ' + data[3] + \
                    '\nFrom: ' + data[5] + \
                    '\nTo:' + data[7] + \
                    '\nTime: ' + data[9] + \
                    '\nDate: ' + data[11]
    return message_block


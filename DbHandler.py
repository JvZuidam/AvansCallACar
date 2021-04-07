import json


def create_database():
    data = {'users': []}
    with open("Users.json", "w") as write_file:
        json.dump(data, write_file)


def check_if_db_exsists():
    global f
    try:
        f = open("Users.json")
    except IOError:
        create_database()
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

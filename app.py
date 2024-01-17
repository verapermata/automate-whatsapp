from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://vera:vera@atlascluster.foatsdb.mongodb.net/")
db = cluster["bakery"]
users = db["users"]
orders = db["orders"]


app = Flask(__name__)

@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:","")
    res = MessagingResponse()
    user = users.find_one({"number":number})





    if bool(user) == False:
        res.message("Hi, thanks for contacting *Pramrule*\nYou can choose from one of the options below: "
                    "\n\n*Type*\n\n1️⃣. To *contact* us \n2️⃣. To *Order* snacks \n3️⃣. To know our *working hours*"
                    "\n4️⃣. To get our *address*")

        users.insert_one({"number": number, "status":"main", "messages":[]})
    elif user["status"]=="main":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            res.message("\n\n*Type*\n\n1️⃣. To *contact* us \n2️⃣. To *Order* snacks \n3️⃣. To know our *working hours*"
                        "\n4️⃣. To get our *address*")
            return str(res)

        if option == 1:
            res.message("You can contact us through phone or e-mail.\n\n*Phone:*123\nEmail: a@email.com")
        elif option == 2:
            res.message("You have entered *ordering mode*")
            users.update_one({"number":number}, {"$set": {"status":"ordering"}})
            res.message("You can select one of the following snacks:\n1️⃣. Me-O snacks kitten \n2️⃣. Me-O snacks adult\n3️⃣. Royal Canin skin and beauty\n0️⃣.Back to main menu")
        elif option == 3:
            res.message("We are open everyday from *9 AM to 9 PM*")
        elif option == 4:
            res.message("Our address is in *Cimahi*")
    elif user["status"]=="ordering":
        try:
            option = int(text)
        except:
            res.message("please enter a valid response")
            res.message(
                "\nYou can select one of the following snacks:\n1️⃣. Me-O snacks kitten \n2️⃣. Me-O snacks adult\n3️⃣. Royal Canin skin and beauty\n0️⃣.Back to main menu")
            return str(res)

        if option == 0:
            res.message("Thank you for contacting us")
        elif 1 <= option <= 3:
            cakes = ["me-o kitten", "me-o adult", "RC skin and beauty"]
            selected = cakes[option-1]
            users.update_one({"number":number}, {"$set":{"status":"address"}})
            users.update_one({"number":number}, {"$set":{"item":selected}})
            res.message("That is an excellent choice 😊"
                        "\nPlease enter your address to confirm the order")
        else:
            res.message("please enter a valid response")
            res.message(
                "\nYou can select one of the following snacks:\n1️⃣. Me-O snacks kitten \n2️⃣. Me-O snacks adult\n3️⃣. Royal Canin skin and beauty\n0️⃣.Back to main menu")
    elif user["status"] == "address":
        selected = user["item"]
        res.message("Thanks for shopping with us!")
        res.message(f"Your order for {selected} has been received and will be delivered within *an hour*")
        orders.insert_one({"number":number, "item":selected, "address:":text, "order_time:": datetime.now()})
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        res.message("Thank you for contact *Pramrule* again"
                    "\n\n*Type*\n\n1️⃣. To *contact* us \n2️⃣. To *Order* snacks \n3️⃣. To know our *working hours*"
                    "\n4️⃣. To get our *address*")
        users.update_one({"number": number}, {"$set": {"status": "main"}})
    users.update_one({"number": number}, {"$push": {"message": {"text": text, "date": datetime.now()}}})
    return str(res)

if __name__ == "__main__":
    app.run()

    

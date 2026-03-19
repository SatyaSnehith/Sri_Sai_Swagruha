from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
import urllib.parse

app = Flask(__name__)

# =============================
# Upload Configuration
# =============================
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

cart = []

# =============================
# Product Data (UPDATED WITH IMAGES)
# =============================
products = {
    "Garelu (Pappu)": {
        "desc": "1 Kg - 50 Units | Rice flour, Channa dal, Salt, Red mirchi, Sesame seeds, Spring onion, Coriander, Curry leaves",
        "image": "images/pappu_garelu.jpeg"
    },
    "Garelu (Palli)": {
        "desc": "1 Kg - 50 Units | Rice flour, Ground nut, Salt, Red mirchi, Sesame seeds, Spring onion, Coriander, Curry leaves",
        "image": "images/palli_garelu.jpeg"
    },
    "Murukulu (Regular)": {
        "desc": "1 Kg - 40 Units | Channa dal, Jeera, Sesame seeds, Coriander cumin powder, Red mirchi, Salt",
        "image": "images/murukulu_regular.jpeg"
    },
    "Murukulu (Broad)": {
        "desc": "1 Kg - 40 Units | Channa dal, Jeera, Sesame seeds, Coriander cumin powder, Red mirchi, Salt",
        "image": "images/murukulu_broad.jpeg"
    },
    "Arisalu": {
        "desc": "1 Kg - 24 Units | Jaggery, Rice flour, Sesame seeds",
        "image": "images/arisalu.jpeg"
    },
    "Karjikayalu": {
        "desc": "1 Kg - 20 Units | Maida, Wheat, Groundnut, Coconut, Sesame seeds, Jaggery, Ravva, Sugar",
        "image": "images/karjikayalu.jpeg"
    },
    "Sunnundalu": {
        "desc": "1 Kg - 24 Units | Ghee, Urad dal, Moong dal, Sugar",
        "image": "images/sunnundalu.jpeg"
    },
    "Boondhi Laddu": {
        "desc": "1 Kg - 24 Units | Channa dal, Sugar, Dry fruits",
        "image": "images/boondhi_laddu.jpeg"
    },
    "Ravva Laddu": {
        "desc": "1 Kg - 24 Units | Ravva, Sugar, Dry fruits",
        "image": "images/ravva_laddu.jpeg"
    },
    "Palli Laddu": {
        "desc": "1 Kg - 20 Units | Groundnut, Jaggery, Sesame seeds",
        "image": "images/palli_laddu.jpeg"
    },
    "Sakinalu (Salted)": {
        "desc": "1 Kg - 55 Units | Rice flour, Jeera, Vamu, Salt",
        "image": "images/sakinalu_salted.jpeg"
    },
    "Sakinalu (Karam)": {
        "desc": "1 Kg - 55 Units | Rice flour, Jeera, Red/Green mirchi, Garlic, Vamu, Coriander leaves, Salt",
        "image": "images/sakinalu_karam.jpeg"
    },
    "Gavvalu": {
        "desc": "1 Kg - 24 Units | Wheat, Maida, Sugar/Jaggery, Ravva",
        "image": "images/gavvalu.jpeg"
    },
    "salividi": {
        "desc": "rice flour, sugar, Dryfruits",
        "image": "images/salividi.jpeg"
    },
    "chuduva": {
        "desc": "karam boondhi",
        "image": "images/chuduva.jpeg"
    }
}

# =============================
# Routes
# =============================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/menu")
def menu():
    return render_template("menu.html", products=products)


@app.route("/add", methods=["POST"])
def add():
    item = request.form.get("item")
    qty = int(request.form.get("qty"))

    cart.append({
        "item": item,
        "qty": qty
    })

    return redirect(url_for("cart_page"))


@app.route("/delete/<int:index>")
def delete(index):
    if index < len(cart):
        cart.pop(index)
    return redirect(url_for("cart_page"))


@app.route("/cart")
def cart_page():
    total = sum(i["qty"] * 399 for i in cart)
    advance = round(total * 0.20, 2)
    return render_template("cart.html", cart=cart, total=total, advance=advance)


@app.route("/booking", methods=["GET", "POST"])
def booking():
    total = sum(i["qty"] * 399 for i in cart)
    advance = round(total * 0.20, 2)

    if request.method == "POST":

        name = request.form.get("name")
        phone = request.form.get("phone")
        slip = request.files.get("slip")

        if not slip or slip.filename == "":
            return "⚠️ Please upload payment slip to confirm order!"

        filename = secure_filename(slip.filename)
        slip.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        message = f"""
New Order Placed!

Name: {name}
Customer Phone: {phone}

Order Details:
"""

        for item in cart:
            message += f"- {item['item']} x {item['qty']}\n"

        message += f"""
Total Amount: ₹{total}
Advance Required (20%): ₹{advance}

Payment slip uploaded successfully.
"""

        encoded_message = urllib.parse.quote(message)

        whatsapp_number = "918247336418"

        whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_message}"

        cart.clear()

        return redirect(whatsapp_url)

    return render_template("booking.html", cart=cart, total=total, advance=advance)


if __name__ == "__main__":
    app.run(debug=True)
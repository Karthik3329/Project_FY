from flask_bcrypt import Bcrypt
from config import users_collection

bcrypt = Bcrypt(app)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = bcrypt.generate_password_hash(
            request.form["password"]
        ).decode("utf-8")

        users_collection.insert_one({
            "name": name,
            "email": email,
            "password": password,
            "role": "user"
        })

        return redirect("/login")

    return render_template("register.html")
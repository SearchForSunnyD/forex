from flask import Flask, request, render_template, session, jsonify
from forex import Forex

app = Flask(__name__)
app.secret_key = "super_secret"

# api_key = "96c6f66da45b139370b9a8d7305135fe"
api_key = "2"

module = Forex(api_key)


@app.route("/")
def show_home():
    """
    Display the home page.
    """
    session["currencies"] = module.supported
    return render_template("home.html")


@app.route("/conv")
def reply():
    """Run the conversion"""
    try:
        con_from = request.args.get("from")
        con_to = request.args.get("to")
        con_amount = float(request.args.get("amount"))
        if module.is_valid(con_amount):
            response = module.conv_string(con_from, con_to, con_amount)
            return response
    except ValueError as err:
        response = jsonify({"error": "Value Error", "message": str(err)})
    except KeyError as err:
        response = jsonify({"error": "Key Error", "message": str(err)})
    except TypeError as err:
        response = jsonify({"error": "Type Error", "message": str(err)})
    response.status_code = 400
    return response

from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os
app = Flask(__name__)
CORS(app)


# MySQL Connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST","host.docker.internal"),
        user="securebank",
        password="SecureBank@123",
        database="securebank"
    )


# Home API
@app.route("/")
def home():
    return jsonify({
        "message": "SecureBank Backend is running successfully"
    })


# Health Check API
@app.route("/api/health")
def health():
    try:
        db = get_db_connection()
        db.close()

        return jsonify({
            "status": "UP",
            "database": "Connected",
            "service": "Banking Application Backend"
        })

    except Exception as e:
        return jsonify({
            "status": "DOWN",
            "database": "Connection failed",
            "error": str(e)
        }), 500


# Register API
@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json()

    full_name = data.get("full_name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")

    if not full_name or not email or not password:
        return jsonify({
            "message": "Name, email and password are required"
        }), 400

    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Check existing email
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        if cursor.fetchone():
            cursor.close()
            db.close()

            return jsonify({
                "message": "Email already registered"
            }), 409

        # Insert new user
        cursor.execute(
            """
            INSERT INTO users
            (full_name, email, phone, password)
            VALUES (%s, %s, %s, %s)
            """,
            (full_name, email, phone, password)
        )

        db.commit()

        cursor.close()
        db.close()

        return jsonify({
            "message": "Registration successful"
        }), 201

    except Exception as e:
        return jsonify({
            "message": "Registration failed",
            "error": str(e)
        }), 500

# Login API
@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, full_name, email, password FROM users WHERE email = %s",
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if not user:
            return jsonify({
                "message": "Invalid email or password"
            }), 401

        if user["password"] != password:
            return jsonify({
                "message": "Invalid email or password"
            }), 401

        return jsonify({
            "message": "Login successful",
            "user_id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"]
        }), 200

    except Exception as e:
        return jsonify({
            "message": "Login failed",
            "error": str(e)
        }), 500
# Account API
@app.route("/api/account/<int:user_id>", methods=["GET"])
def get_account(user_id):

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT account_number, balance
            FROM accounts
            WHERE user_id = %s
            """,
            (user_id,)
        )

        account = cursor.fetchone()

        cursor.close()
        db.close()

        if not account:
            return jsonify({
                "message": "Account not found"
            }), 404

        return jsonify(account), 200

    except Exception as e:
        return jsonify({
            "message": "Failed to get account",
            "error": str(e)
        }), 500
# Transactions API
@app.route("/api/transactions/<int:user_id>", methods=["GET"])
def get_transactions(user_id):

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, transaction_type, amount, description, transaction_date
            FROM transactions
            WHERE user_id = %s
            ORDER BY transaction_date DESC
        """, (user_id,))

        transactions = cursor.fetchall()

        cursor.close()
        db.close()

        return jsonify(transactions), 200

    except Exception as e:
        return jsonify({
            "message": "Failed to get transactions",
            "error": str(e)
        }), 500
# Start Flask
@app.route("/api/transfer", methods=["POST"])
def transfer_money():

    try:
        data = request.get_json()

        user_id = data["user_id"]
        receiver_account = data["receiver_account"]
        amount = float(data["amount"])
        description = data.get("description", "Money Transfer")

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Check sender account
        cursor.execute(
            "SELECT balance FROM accounts WHERE user_id = %s",
            (user_id,)
        )
        sender = cursor.fetchone()

        if not sender:
            return jsonify({"message": "Sender account not found"}), 404

        # Check balance
        if sender["balance"] < amount:
            return jsonify({"message": "Insufficient balance"}), 400

        # Check receiver account
        cursor.execute(
            "SELECT user_id FROM accounts WHERE account_number = %s",
            (receiver_account,)
        )
        receiver = cursor.fetchone()

        if not receiver:
            return jsonify({"message": "Receiver account not found"}), 404

        # Deduct from sender
        cursor.execute(
            """
            UPDATE accounts
            SET balance = balance - %s
            WHERE user_id = %s
            """,
            (amount, user_id)
        )

        # Add to receiver
        cursor.execute(
            """
            UPDATE accounts
            SET balance = balance + %s
            WHERE account_number = %s
            """,
            (amount, receiver_account)
        )

        # Sender transaction
        cursor.execute(
            """
            INSERT INTO transactions
            (user_id, transaction_type, amount, description)
            VALUES (%s, 'TRANSFER', %s, %s)
            """,
            (user_id, amount, description)
        )

        # Receiver transaction
        cursor.execute(
            """
            INSERT INTO transactions
            (user_id, transaction_type, amount, description)
            VALUES (%s, 'CREDIT', %s, %s)
            """,
            (receiver["user_id"], amount, "Money Received")
        )

        db.commit()

        cursor.close()
        db.close()

        return jsonify({
            "message": "Money transferred successfully"
        }), 200

    except Exception as e:

        return jsonify({
            "message": "Transfer failed",
            "error": str(e)
        }), 500
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )

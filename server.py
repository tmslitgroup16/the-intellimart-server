from flask import Flask, request, jsonify  # type: ignore
from datetime import datetime
from flask_cors import CORS  # type: ignore
from ml_model_1 import final_recommendation_1, diet_1
from ml_model_2 import final_recommendation_2, diet_2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import time
import razorpay  # type: ignore
from email.mime.base import MIMEBase
from email import encoders
from twilio.rest import Client
import os
from dotenv import load_dotenv  # type: ignore

load_dotenv()

app = Flask(__name__)

# Enable CORS for a specific route
# CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/", methods=["GET"])
def display():
    return "This is the Production Server of \"The Intellimart\""


@app.route("/recommend1", methods=["POST"])
def get_recommendations_1():
    try:
        ingredients = request.get_json().get("ingredients")
        current_day = datetime.now().strftime("%A")
        recommended_dishes = final_recommendation_1(current_day, ingredients)
        recommended_diet = diet_1(current_day, ingredients)
        response_data = {"recommendations": recommended_dishes,
                         "diet": recommended_diet
                         }
        return jsonify(response_data)
    except Exception as e:
        print("The error is:", e)


@app.route("/recommend2", methods=["POST"])
def get_recommendations_2():
    try:
        ingredients = request.get_json().get("ingredients")
        recommended_dishes = final_recommendation_2(ingredients)
        recommended_diet = diet_2(ingredients)
        response_data = {"recommendations": recommended_dishes,
                         "diet": recommended_diet
                         }
        return jsonify(response_data)
    except Exception as e:
        print("The error is:", e)


@app.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')
    otp = str(random.randint(100000, 999999))

    sender_email = 'tmslitgroup16@gmail.com'
    sender_password = 'vxaywctiywpnohlj'

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = 'The Intellimart - Email Verification OTP'

    body = f'Dear customer,\n\nYour OTP for email verification is {otp}\n\n Happy Intelli Shopping!❤️'
    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())

        return jsonify({'status': 'success', 'otp': otp})
    except Exception as e:
        return jsonify({'status': 'error', 'error_message': str(e)})


razorpay_key_id = os.getenv("RAZORPAY_KEY_ID")
razorpay_key_secret = os.getenv("RAZORPAY_KEY_SECRET")
razorpay_client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))


@app.route('/create_order', methods=['POST'])
def create_order():
    try:
        data = request.json
        amount = data.get('amount')
        currency = data.get('currency', 'INR')
        order_data = {
            'amount': int(amount) * 100,
            'currency': currency,
            'receipt': 'order_id_' + str(int(time.time())),
            'payment_capture': 1
        }
        order = razorpay_client.order.create(order_data)
        return jsonify(order)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/verify_payment', methods=['POST'])
def verify_payment():
    try:
        data = request.json
        payment_id = data.get('razorpay_payment_id')
        signature = data.get('razorpay_signature')
        order_id = data.get('razorpay_order_id')
        amount = data.get('amount')
        email = data.get('customer_email')
        phone = data.get('customer_phone')

        if not payment_id or not signature or not order_id or not amount:
            raise ValueError("Missing required parameters")

        if email == '' and phone == '':
            raise ValueError(
                "At least one of customer_email or customer_phone must be provided")

        # Verify payment signature
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
        })

        return jsonify({'success': True, 'payment_id': payment_id}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/send_invoice', methods=['POST'])
def upload_pdf():
    pdf_file = request.files['pdfFile']
    Email = request.form['userEmail']
    PurchaseId = request.form['PurchaseId']
    # phone_number = request.form['userPhone']
    # invoice_pdf_url = request.form['invoiceUrl']

    pdf_blob = pdf_file.read()
    send_email_with_attachment(pdf_blob, Email, PurchaseId)

    # send_invoice_sms(phone_number, invoice_pdf_url)

    return 'PDF received and sent successfully'


def send_email_with_attachment(pdf_blob, Email, PurchaseId):
    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")
    subject = f'Invoice for Purchase ID: {PurchaseId}'
    body = """
    Dear Customer,
        Please find the attached invoice for your recent purchase.

    Thank you for shopping with us!

    Regards,
    The Intellimart Team
    """

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = Email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Attach PDF
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(pdf_blob)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment',
                    filename=f'invoice_{PurchaseId}.pdf')
    msg.attach(part)

    # Connect to SMTP server and send email
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.login(sender_email, password)
    smtp_server.sendmail(sender_email, Email, msg.as_string())
    smtp_server.quit()


def send_invoice_sms(phone_number, invoice_pdf_url):
    # Initialize Twilio client with your Twilio credentials
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_client = Client(account_sid, auth_token)

    invoice_text = f"""
Dear Customer,
    Please download the invoice for your recent purchase from the link given below.

Thank you for shopping with us!

Regards,
The Intellimart team

Invoice download link:"""

    # Send invoice text
    twilio_client.messages.create(
        body=invoice_text,
        media_url=[invoice_pdf_url],
        from_="+17078760023",
        to=phone_number
    )


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)

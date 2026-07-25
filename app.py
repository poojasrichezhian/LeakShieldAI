from flask import Flask, render_template, request
import os
import pandas as pd

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload")
def upload_page():
    return render_template("upload.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    file = request.files["file"]

    if file:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        data = pd.read_csv(filepath)
        # Monthly spending analysis

    data["Date"] = pd.to_datetime(data["Date"])

    monthly_spending = (
        data.groupby(data["Date"].dt.strftime("%B"))["Amount"]
        .sum()
        .to_dict()
)

    recurring = data["Description"].value_counts()

    subscriptions = []
    total = 0
    price_hikes = []
    unused_subscriptions = []
    potential_savings = 0

    for service, count in recurring.items():

            if count > 1:

                amount = data[data["Description"] == service]["Amount"].sum()

                total += amount

                subscriptions.append({
                    "service": service,
                    "count": count,
                    "amount": amount
                })
    for service in recurring.index:

            service_data = data[data["Description"] == service]

            if len(service_data) > 1:

                first_price = service_data.iloc[0]["Amount"]
                latest_price = service_data.iloc[-1]["Amount"]

            if latest_price > first_price:

                price_hikes.append({
                    "service": service,
                    "old": first_price,
                    "new": latest_price
            })

    for service, count in recurring.items():

            if count >= 3:

                service_amount = data[data["Description"] == service]["Amount"].sum()

                unused_subscriptions.append({
                    "service": service,
                    "payments": count,
                    "spent": service_amount
                })
                potential_savings += service_amount

            if total < 50:
                leak_score = 95
            elif total < 100:
                leak_score = 80
            elif total < 200:
                leak_score = 65
            else:
                leak_score = 40

            if leak_score >= 90:
                recommendation = "Excellent! Your subscriptions are under control."
            elif leak_score >= 70:
                recommendation = "Good. Consider cancelling unused subscriptions."
            else:
                recommendation = "High monthly leakage detected. Review all recurring payments."

            return render_template(
            "dashboard.html",
            subscriptions=subscriptions,
            total=total,
            leak_score=leak_score,
            recommendation=recommendation,
            price_hikes=price_hikes,
            unused_subscriptions=unused_subscriptions,
            monthly_spending=monthly_spending,
            potential_savings=potential_savings
        )

    return "No File Selected"
@app.route("/chat", methods=["POST"])
def chat():

    question = request.form["question"].lower()

    if "save" in question or "reduce" in question:
        answer = "You can reduce expenses by reviewing unused subscriptions and cancelling unnecessary services."

    elif "subscription" in question or "cancel" in question:
        answer = "Check your unused subscriptions section and review services with frequent payments."

    elif "price" in question or "increase" in question:
        answer = "Price hike alerts show subscriptions where the payment amount has increased."

    else:
        answer = "I can help you analyze subscriptions, spending patterns, and possible savings."

    return answer
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


@app.route("/report")
def report():

    file_path = "LeakShield_Report.pdf"

    pdf = canvas.Canvas(file_path, pagesize=letter)

    pdf.setFont("Helvetica", 14)

    pdf.drawString(100, 750, "LeakShield AI Financial Report")

    pdf.setFont("Helvetica", 12)

    pdf.drawString(100, 700, "AI-powered subscription analysis report")

    pdf.drawString(100, 650, "Generated successfully")

    pdf.save()

    return file_path

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
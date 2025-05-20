from server.extensions import send_receipt

# Replace this with your actual email and test data
response = send_receipt("your-email@example.com", "Test Case", "PayPal")

if response:
    print("Status:", response.status_code)
    print("Response:", response.text)
else:
    print("Failed to send email.")

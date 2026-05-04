from flask import Flask, request
import requests

# Initialize Flask application
app = Flask(__name__)

# Configuration: Meta WhatsApp API credentials
# Note: These should be stored in environment variables for security
# For development, you can set them directly here
ACCESS_TOKEN = "YOUR_META_ACCESS_TOKEN_HERE"
PHONE_NUMBER_ID = "YOUR_PHONE_NUMBER_ID_HERE"
VERIFY_TOKEN = "YOUR_VERIFY_TOKEN_HERE"

# Store locations data - Mia stores in New Delhi with latitude/longitude
# This data is used to find the nearest store based on user location
stores = [
    {
        "name": "Mia by Tanishq - South Extension",
        "address": "South Extension Part 1, New Delhi",
        "lat": 28.5682,
        "lon": 77.2197,
        "map_link": "https://maps.google.com/?q=28.5682,77.2197"
        },
        {
        "name": "Mia by Tanishq - Ambience Mall Vasant Kunj",
        "address": "Ambience Mall, Vasant Kunj, New Delhi",
        "lat": 28.5416,
        "lon": 77.1558,
        "map_link": "https://maps.google.com/?q=28.5416,77.1558"
        },
        {
        "name": "Mia by Tanishq - Lajpat Nagar",
        "address": "Central Market, Lajpat Nagar",
        "lat": 28.5677,
        "lon": 77.2430,
        "map_link": "https://maps.google.com/?q=28.5677,77.2430"
    }
]


def find_closest_store(user_lat, user_lon):
    """
    Calculate and return the closest store to user's location using Euclidean distance.
    
    Args:
        user_lat (float): User's latitude
        user_lon (float): User's longitude
        
    Returns:
        dict: Store information with the smallest distance to user
    """
    closest = None
    min_dist = float('inf')
    for store in stores:
        # Calculate Euclidean distance (simplified - doesn't account for Earth's curvature)
        dist = (store['lat'] - user_lat)**2 + (store['lon'] - user_lon)**2
        if dist < min_dist:
            min_dist = dist
            closest = store
    return closest


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    """
    Main webhook endpoint for Meta WhatsApp API.
    
    GET: Webhook verification (Meta sends hub.verify_token and hub.challenge)
    POST: Receives incoming messages and processes them
    
    Returns:
        tuple: Response message and HTTP status code
    """
    # Webhook Verification (Meta checks this once during setup)
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    # Handle Incoming Messages from WhatsApp users
    if request.method == "POST":
        data = request.json
        print("Received Data:", data)

        try:
            # Check if message exists in the webhook payload
            if "messages" in data["entry"][0]["changes"][0]["value"]:

                message_data = data["entry"][0]["changes"][0]["value"]["messages"][0]
                sender = message_data["from"]  # User's WhatsApp number

                # ===== HANDLE BUTTON CLICK (Interactive Messages) =====
                if "interactive" in message_data:

                    button_id = message_data["interactive"]["button_reply"]["id"]

                    if button_id == "find_store":
                        # User clicked "Find Nearest Store" - ask for location
                        reply_text = (
                            "📍 Please send your location to find the nearest Mia store.\n\n"
                            "Tap ➕ → Location → Send Current Location."
                        )
                        send_whatsapp_message(sender, reply_text)

                    elif button_id == "store_timings":
                        # User clicked "Store Timings"
                        reply_text = "🕒 Store Timings:\nMon – Sun : 10 AM – 9 PM"
                        send_whatsapp_message(sender, reply_text)

                    elif button_id == "contact_store":
                        # User clicked "Contact Store"
                        reply_text = "📞 Call us at +91-9999999999\n🌐 Mia by Tanishq: https://www.miabytanishq.com"
                        send_whatsapp_message(sender, reply_text)

                    return "ok", 200

            # ===== HANDLE TEXT MESSAGE =====
            if "text" in message_data:

                user_text = message_data["text"]["body"]
                print("Message from user:", user_text)

                user_text_lower = user_text.lower()

                # ===== MAIN MENU =====
                if user_text_lower in ["hi", "hii", "hello", "start"]:
                    send_main_menu(sender)
                    return "ok", 200

                # fallback keyword for contact info
                elif "contact" in user_text_lower or "phone" in user_text_lower:
                    reply_text = "📞 Call us at +91-9999999999"
                    send_whatsapp_message(sender, reply_text)
                    return "ok", 200

                else:
                    reply_text = "❓ I didn’t understand. Please type 'Hi' to start again."
                    send_whatsapp_message(sender, reply_text)

            # ===== HANDLE LOCATION MESSAGE - User sends their location =====
            if "location" in message_data:
                user_lat = message_data["location"]["latitude"]
                user_lon = message_data["location"]["longitude"]
                # Find nearest store and send details
                closest_store = find_closest_store(user_lat, user_lon)
                reply_text = (
                    f"📍 Nearest Store:\n"
                    f"{closest_store['name']}\n"
                    f"{closest_store['address']}\n"
                    f"{closest_store['map_link']}"
                )
                send_whatsapp_message(sender, reply_text)
                return "ok", 200

        except Exception as e:
            print("Error:", e)

        return "ok", 200


def send_main_menu(to):
    """
    Send interactive button menu to user via WhatsApp.
    Displays 3 main options: Find Nearest Store, Store Timings, Contact Store.
    
    Args:
        to (str): User's WhatsApp phone number
    """
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "👋 Welcome to our Mia Store!\n\nPlease choose an option:"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "find_store",
                            "title": "Find Nearest Store"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "store_timings",
                            "title": "Store Timings"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "contact_store",
                            "title": "Contact Store"
                        }
                    }
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("Main menu sent:", response.status_code, response.text)
    # if interactive template is rejected, fall back to simple text menu
    if response.status_code != 200:
        print("Interactive menu failed, reverting to text menu")
        fallback = (
            "👋 Welcome to Mia Store!\n\n"
            "1️⃣ Find Nearest Store\n"
            "2️⃣ Store Timings\n"
            "3️⃣ Contact Store\n"
            "🔗 Website: https://www.yourstore.com"
        )
        send_whatsapp_message(to, fallback)


def send_back_to_menu(to):
    """
    Send a 'returning to main menu' message and display the main menu.
    
    Args:
        to (str): User's WhatsApp phone number
    """
    # simple wrapper to send a back-to-menu prompt and then the menu
    send_whatsapp_message(to, "🔄 Returning to main menu...")
    send_main_menu(to)


def send_whatsapp_message(to, message):
    """
    Send a text message to user via Meta WhatsApp API.
    
    Args:
        to (str): User's WhatsApp phone number
        message (str): Message content to send
        
    Returns:
        Response from Meta API with status code and message details
    """

    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    print("Message sent:", response.status_code, response.text)

if __name__ == "__main__":
    app.run(port=5000)
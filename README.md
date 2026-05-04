# 🤖 Mia WhatsApp Chatbot

A **production-ready WhatsApp chatbot** built with Flask and Meta's WhatsApp Business API. The bot intelligently handles customer queries, provides store locations using geolocation, and offers real-time customer support.

**Live Demo:** Working with Ngrok tunnel & Meta Developer Account ✅

---

## 📋 Features

✨ **Key Capabilities:**

- **Interactive Menu System** - User-friendly button-based navigation
- **Location-Based Store Finder** - Finds nearest store using geolocation (Euclidean distance)
- **Real-time Response** - Instant WhatsApp message replies
- **Webhook Integration** - Receives and processes incoming messages
- **Error Handling** - Graceful exception handling for API failures
- **Fallback Support** - Text menu fallback if interactive buttons fail
- **Multi-Store Support** - Pre-configured with 3 store locations

---

## 🏗️ Architecture Overview

```
┌─────────────────┐
│  WhatsApp User  │
└────────┬────────┘
         │ Sends Message
         ↓
  ┌─────────────┐
  │   Webhook   │  (GET verification / POST messages)
  └────┬────────┘
       ↓
  ┌────────────────────────┐
  │  Message Processing    │
  │  - Button clicks       │
  │  - Text messages       │
  │  - Location data       │
  └────┬───────────────────┘
       ↓
  ┌─────────────────────────────┐
  │  Response Handler           │
  │  - Find Store               │
  │  - Send Menu                │
  │  - Location-based Search    │
  └────┬────────────────────────┘
       ↓
  ┌─────────────────────┐
  │  Meta WhatsApp API  │  (Send reply)
  └─────────────────────┘
```

---

## 🔧 Technical Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | Flask 2.3.2 |
| **API Integration** | Meta WhatsApp Business API |
| **Language** | Python 3.8+ |
| **HTTP Client** | Requests Library |
| **Tunneling** | Ngrok (for development) |

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Meta Business Account with WhatsApp API access
- WhatsApp Business Phone Number
- Access Token from Meta Developer Console
- Ngrok (for tunneling during development)

### Step 1: Clone & Environment Setup

```bash
# Clone repository
git clone https://github.com/yourusername/mia-chatbot.git
cd mia-chatbot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Credentials

Edit `app.py` and add your Meta credentials:

```python
ACCESS_TOKEN = "YOUR_META_ACCESS_TOKEN_HERE"
PHONE_NUMBER_ID = "YOUR_PHONE_NUMBER_ID_HERE"
VERIFY_TOKEN = "YOUR_VERIFY_TOKEN_HERE"
```

> ⚠️ **Security Note:** For production, use environment variables instead of hardcoding tokens.

### Step 3: Run the Application

```bash
python app.py
```

Server runs on `http://localhost:5000`

### Step 4: Setup Webhook with Ngrok

In a **new terminal**:

```bash
ngrok http 5000
```

This generates a public URL like: `https://abc123.ngrok.io`

### Step 5: Configure Meta Dashboard

1. Go to [Meta App Dashboard](https://developers.facebook.com)
2. Navigate to WhatsApp > Configuration
3. Set **Webhook URL** to: `https://abc123.ngrok.io/webhook`
4. Set **Verify Token** to: `YOUR_VERIFY_TOKEN_HERE`
5. Subscribe to **messages** and **message_status** events
6. Save and verify webhook

---

## 🚀 API Endpoints

### GET /webhook
**Purpose:** Webhook verification by Meta

**Query Parameters:**
```
hub.verify_token: Your verification token
hub.challenge: Challenge string from Meta
```

**Response:**
```
200 OK: Returns challenge string (if token matches)
403 Forbidden: Returns "Verification failed" (if token mismatches)
```

---

### POST /webhook
**Purpose:** Receive and process incoming messages

**Request Body Example:**
```json
{
  "entry": [
    {
      "changes": [
        {
          "value": {
            "messages": [
              {
                "from": "919999999999",
                "type": "text",
                "text": { "body": "Hi" }
              }
            ]
          }
        }
      ]
    }
  ]
}
```

**Message Types Handled:**
1. **Text Messages** - `"type": "text"`
2. **Button Clicks** - `"type": "interactive"`
3. **Location** - `"type": "location"`

---

## 💬 Supported User Interactions

### 1. **Start Conversation**
```
User: "Hi" / "Hello" / "Start"
Bot: Shows interactive menu with 3 buttons
```

### 2. **Find Nearest Store**
```
User: Clicks "Find Nearest Store" button
Bot: Asks for location
User: Sends current location
Bot: Calculates nearest store & sends address + map link
```

### 3. **Store Timings**
```
User: Clicks "Store Timings" button
Bot: Sends store hours (10 AM - 9 PM, Mon-Sun)
```

### 4. **Contact Store**
```
User: Clicks "Contact Store" button
Bot: Sends phone number & website
```

---

## 📍 Store Data Structure

Stores are stored as a list of dictionaries:

```python
stores = [
    {
        "name": "Store Name",
        "address": "Address",
        "lat": 28.5682,
        "lon": 77.2197,
        "map_link": "https://maps.google.com/?q=28.5682,77.2197"
    }
]
```

**How It Works:**
1. User sends their GPS coordinates
2. `find_closest_store(user_lat, user_lon)` calculates Euclidean distance
3. Returns store with minimum distance

---

## 📊 Key Functions Explained

### `find_closest_store(user_lat, user_lon)`
- **Purpose:** Locate nearest store using geolocation
- **Algorithm:** Euclidean distance formula
- **Input:** User's latitude & longitude
- **Output:** Closest store object with address & map link

### `send_main_menu(to)`
- **Purpose:** Display interactive button menu
- **Method:** Meta Interactive API with button reply template
- **Fallback:** Sends text menu if interactive fails

### `send_whatsapp_message(to, message)`
- **Purpose:** Send text messages via Meta API
- **Method:** POST request to Meta Graph API
- **Authentication:** Bearer token in Authorization header

### `webhook()`
- **Purpose:** Main entry point for all incoming messages
- **Flow:** Verify → Parse → Route → Respond
- **Error Handling:** Try-catch blocks prevent crashes

---

## 🔐 Security Best Practices

✅ **Implemented:**
- Token validation on webhook verification
- Exception handling for API errors
- Graceful error messages to users

🔒 **Recommendations for Production:**
- Use environment variables for sensitive data
- Implement rate limiting
- Add request signature verification from Meta
- Use HTTPS/TLS encryption
- Implement user authentication
- Add logging & monitoring
- Use database for user sessions

---

## 📝 File Structure

```
mia-chatbot/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── responses.json        # Future: store responses
├── templates/
│   ├── index.html       # Chat UI (optional)
│   └── admin.html       # Admin dashboard (optional)
└── .gitignore           # Git ignore rules
```

---

## 🐛 Troubleshooting

### Issue: "Verification failed"
**Solution:** Ensure `VERIFY_TOKEN` matches token in Meta Dashboard

### Issue: Webhook not receiving messages
**Solution:** 
- Check Ngrok tunnel is running
- Verify webhook URL in Meta Dashboard
- Ensure events are subscribed (messages, message_status)

### Issue: "No attribute 'button_reply'"
**Solution:** User sent non-interactive message; check message type

### Issue: API rate limiting
**Solution:** Implement request queue or use Meta's batching API

---

## 🎯 Future Enhancements

- [ ] Database integration (store user sessions)
- [ ] NLP/AI for intent classification
- [ ] Multi-language support
- [ ] Order management system
- [ ] Payment integration
- [ ] Analytics dashboard
- [ ] Message templates library
- [ ] Auto-reply scheduling

---

## 📚 API References

- [Meta WhatsApp API Documentation](https://developers.facebook.com/docs/whatsapp/cloud-api/reference)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Requests Library](https://docs.python-requests.org/)

---

## 👨‍💻 Author

Created as a demo project for WhatsApp Bot integration

---

## 📄 License

MIT License - Feel free to use in your projects

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

---

**Made with ❤️ for WhatsApp Business Automation**

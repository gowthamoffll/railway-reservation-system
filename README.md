# Railway Reservation System

This is a professional **Streamlit** application integrated with an **SQLite** backend to manage train ticket bookings. It features a modern web UI with custom styling and an interactive seat map.

---

## 🚀 Features
* [cite_start]**Live Dashboard**: Real-time metrics for total bookings and daily travelers[cite: 1].
* [cite_start]**Interactive Booking**: Visual seat map for selecting seats across multiple coaches[cite: 1].
* [cite_start]**Full CRUD**: View, Book, Modify, and Cancel reservations through a tabbed interface[cite: 1].
* [cite_start]**Data Export**: Search functionality and CSV download for all records[cite: 1].
* [cite_start]**Hybrid Backend**: Shared logic between the Streamlit web app and a Terminal-based menu[cite: 1, 3].

---

## 🛠️ Tech Stack
* [cite_start]**Frontend**: Streamlit [cite: 1]
* [cite_start]**Data Analysis**: Pandas [cite: 1]
* **Database**: SQLite
* [cite_start]**Typography**: Playfair Display & DM Sans (via Google Fonts) [cite: 1]

---

## 📂 File Structure
* [cite_start]`app.py`: The main web application and UI logic[cite: 1].
* `railway.py`: Database operations and the CLI menu interface.
* `railway.db`: SQLite database storing the `bookings` table.

---

## 🔧 Database Schema
The system manages data in a `bookings` table with the following fields:
* `ticket_id`: Primary Key (Auto-increment)
* `passenger_name`: Text
* `train_no`: Text
* `source` / `destination`: Text
* `travel_date`: Text (DD.MM.YYYY)
* `seat_no`: Text (e.g., A1, C11)

---

## 🏃 Setup & Execution

### 1. Install Requirements
```bash
pip install streamlit pandas
```

### 2. Launch the Application
[cite_start]To run the web interface[cite: 1]:
```bash
streamlit run app.py
```

To run the terminal-based system:
```bash
python railway.py
```
### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/gowthamoffll/railway-reservation-system.git](https://github.com/gowthamoffll/railway-reservation-system.git)
   cd railway-reservation-system
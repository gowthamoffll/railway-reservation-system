import sqlite3

DB = "railway.db"

# ── DB setup ──────────────────────────────────────────────────────────────────

def get_connection():
    con = sqlite3.connect(DB)
    # Create table with seat_no column
    con.execute("""
        CREATE TABLE IF NOT EXISTS bookings(
            ticket_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            passenger_name TEXT NOT NULL,
            train_no       TEXT NOT NULL,
            source         TEXT NOT NULL,
            destination    TEXT NOT NULL,
            travel_date    TEXT NOT NULL,
            seat_no        TEXT NOT NULL DEFAULT 'N/A'
        )
    """)
    # Migrate existing DB: add seat_no column if it doesn't exist
    try:
        con.execute("ALTER TABLE bookings ADD COLUMN seat_no TEXT NOT NULL DEFAULT 'N/A'")
    except Exception:
        pass  # Column already exists
    con.commit()
    return con


# ── Helper: get all booked seats for a train on a date ───────────────────────

def get_booked_seats(train_no, travel_date):
    """Return a list of already booked seat numbers for a train+date combo."""
    con = get_connection()
    cur = con.execute(
        "SELECT seat_no FROM bookings WHERE train_no=? AND travel_date=?",
        (train_no, travel_date)
    )
    seats = [row[0] for row in cur.fetchall()]
    con.close()
    return seats


# ── Core functions (importable, no input() calls) ─────────────────────────────

def book_ticket(name, train, src, dest, date, seat_no):
    """Insert a new booking. Returns the new ticket_id."""
    con = get_connection()
    cur = con.execute(
        "INSERT INTO bookings(passenger_name, train_no, source, destination, travel_date, seat_no) VALUES (?,?,?,?,?,?)",
        (name, train, src, dest, date, seat_no)
    )
    con.commit()
    ticket_id = cur.lastrowid
    con.close()
    return ticket_id

def view_bookings():
    """Return all bookings as a list of tuples."""
    con = get_connection()
    cur = con.execute("SELECT * FROM bookings ORDER BY ticket_id DESC")
    rows = cur.fetchall()
    con.close()
    return rows

def modify_booking(ticket_id, new_train, new_date, new_seat):
    """Update train, date and seat for a given ticket_id. Returns rows affected."""
    con = get_connection()
    cur = con.execute(
        "UPDATE bookings SET train_no=?, travel_date=?, seat_no=? WHERE ticket_id=?",
        (new_train, new_date, new_seat, ticket_id)
    )
    con.commit()
    affected = cur.rowcount
    con.close()
    return affected

def cancel_booking(ticket_id):
    """Delete a booking by ticket_id. Returns rows affected."""
    con = get_connection()
    cur = con.execute("DELETE FROM bookings WHERE ticket_id=?", (ticket_id,))
    con.commit()
    affected = cur.rowcount
    con.close()
    return affected


# ── Terminal menu (only runs when executed directly) ──────────────────────────

if __name__ == "__main__":
    while True:
        print("\n🚂 RAILWAY RESERVATION SYSTEM")
        print("1. Book Ticket")
        print("2. View All Bookings")
        print("3. Modify Booking")
        print("4. Cancel Booking")
        print("5. Exit")

        choice = input("\nSelect an option (1-5): ")

        if choice == '1':
            name  = input("Passenger Name: ")
            train = input("Train Number/Name: ")
            src   = input("From: ")
            dest  = input("To: ")
            date  = input("Date (DD/MM/YYYY): ")
            booked = get_booked_seats(train, date)
            print(f"Already booked seats: {', '.join(booked) if booked else 'None'}")
            seat  = input("Seat No (e.g. A1, B12): ").upper()
            if seat in booked:
                print(f"❌ Seat {seat} is already booked. Please choose another.")
            else:
                tid = book_ticket(name, train, src, dest, date, seat)
                print(f"\n✅ Ticket booked for {name}! Seat: {seat} | Ticket ID: {tid}")

        elif choice == '2':
            rows = view_bookings()
            print("\n🎫 CURRENT RESERVATIONS")
            print("-" * 70)
            if not rows:
                print("No bookings found.")
            else:
                for row in rows:
                    print(f"ID: {row[0]} | Name: {row[1]} | Train: {row[2]} | "
                          f"{row[3]} -> {row[4]} | Date: {row[5]} | Seat: {row[6]}")
            print("-" * 70)

        elif choice == '3':
            t_id      = int(input("Enter Ticket ID to modify: "))
            new_train = input("Enter new Train Number: ")
            new_date  = input("Enter new Date (DD/MM/YYYY): ")
            booked    = get_booked_seats(new_train, new_date)
            print(f"Already booked seats: {', '.join(booked) if booked else 'None'}")
            new_seat  = input("Enter new Seat No: ").upper()
            if new_seat in booked:
                print(f"❌ Seat {new_seat} is already booked. Please choose another.")
            elif modify_booking(t_id, new_train, new_date, new_seat):
                print("✅ Booking updated successfully.")
            else:
                print("❌ Ticket ID not found.")

        elif choice == '4':
            t_id = int(input("Enter Ticket ID to cancel: "))
            if cancel_booking(t_id):
                print("🗑️ Reservation cancelled successfully.")
            else:
                print("❌ Ticket ID not found.")

        elif choice == '5':
            print("Thank you for using the Railway System. Goodbye!")
            break

        else:
            print("⚠️ Invalid choice. Please try again.")

import streamlit as st
import pandas as pd
from datetime import datetime

# ── Import directly from railway.py ──────────────────────────────────────────
from railway import book_ticket, view_bookings, modify_booking, cancel_booking, get_booked_seats

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Railway Reservation System",
    page_icon="🚂",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.hero {
    background: linear-gradient(135deg, #1A1A2E 60%, #2D3748);
    border-bottom: 4px solid #C9A84C;
    padding: 1.8rem 2rem 1.4rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
}
.hero h1 { font-family: 'Playfair Display', serif; color: #C9A84C; font-size: 2rem; margin: 0; }
.hero p  { color: #9AA5B4; font-size: 0.88rem; letter-spacing: 0.1em; text-transform: uppercase; margin: 4px 0 0; }

.metric-card {
    background: #1A1A2E;
    border: 1px solid #C9A84C44;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    text-align: center;
    margin-bottom: 0.6rem;
}
.metric-card .val { font-size: 2rem; font-weight: 700; color: #C9A84C; }
.metric-card .lbl { font-size: 0.78rem; color: #9AA5B4; text-transform: uppercase; letter-spacing: 0.08em; }

.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    color: #1A1A2E;
    border-left: 4px solid #C9A84C;
    padding-left: 0.75rem;
    margin-bottom: 1rem;
}

.ticket-card {
    background: white;
    border: 1px solid #E8E2D9;
    border-left: 5px solid #C9A84C;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}
.ticket-card .route { font-size: 1.05rem; font-weight: 600; color: #1A1A2E; }
.ticket-card .meta  { font-size: 0.82rem; color: #4A5568; margin-top: 4px; }
.badge-success { background:#D4EDDA; color:#155724; padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:500; }

/* Seat grid */
.seat-grid { display: flex; flex-wrap: wrap; gap: 8px; margin: 0.75rem 0; }
.seat-btn {
    width: 48px; height: 40px;
    border-radius: 6px;
    border: 2px solid #C9A84C;
    background: white;
    color: #1A1A2E;
    font-size: 0.75rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
    display: flex; align-items: center; justify-content: center;
}
.seat-btn.booked {
    background: #E53E3E;
    border-color: #E53E3E;
    color: white;
    cursor: not-allowed;
}
.seat-btn.selected {
    background: #C9A84C;
    border-color: #C9A84C;
    color: white;
}
.seat-legend { display: flex; gap: 1.5rem; font-size: 0.8rem; margin-top: 0.5rem; align-items: center; }
.dot { width: 14px; height: 14px; border-radius: 3px; display: inline-block; margin-right: 4px; vertical-align: middle; }
</style>
""", unsafe_allow_html=True)


# ── Seat configuration ────────────────────────────────────────────────────────
COACHES = ["A", "B", "C", "D", "S"]
SEATS_PER_COACH = 12

def all_seats():
    """Generate all seat labels: A1–A12, B1–B12, ..."""
    return [f"{coach}{num}" for coach in COACHES for num in range(1, SEATS_PER_COACH + 1)]

def render_seat_map(booked_seats, selected_seat=None):
    """Render an interactive seat map using Streamlit buttons grouped by coach."""
    chosen = None
    for coach in COACHES:
        st.markdown(f"**Coach {coach}**")
        cols = st.columns(SEATS_PER_COACH)
        for i, num in enumerate(range(1, SEATS_PER_COACH + 1)):
            seat = f"{coach}{num}"
            with cols[i]:
                if seat in booked_seats:
                    st.button(seat, key=f"seat_{seat}", disabled=True,
                              help="Already booked")
                else:
                    label = f"✓{seat}" if seat == selected_seat else seat
                    if st.button(label, key=f"seat_{seat}",
                                 type="primary" if seat == selected_seat else "secondary"):
                        chosen = seat
    return chosen


# ── Helper: load all bookings into a DataFrame ────────────────────────────────
def load_df():
    rows = view_bookings()
    cols = ["ticket_id", "passenger_name", "train_no", "source", "destination", "travel_date", "seat_no"]
    if rows:
        # Handle old rows that may not have seat_no (6 columns)
        padded = [r if len(r) == 7 else r + ("N/A",) for r in rows]
        return pd.DataFrame(padded, columns=cols)
    return pd.DataFrame(columns=cols)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div style="font-size:2.4rem;margin-bottom:4px">🚂</div>
  <h1>Railway Reservation System</h1>
  <p>Book · View · Modify · Cancel</p>
</div>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗂 Navigation")
    page = st.radio(
        "Go to",
        ["📋 All Bookings", "🎫 Book a Ticket", "✏️ Modify Booking", "🗑️ Cancel Booking"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    df_all    = load_df()
    today_str = datetime.today().strftime("%d.%m.%Y")
    total         = len(df_all)
    today_count   = int((df_all["travel_date"] == today_str).sum()) if not df_all.empty else 0
    unique_routes = df_all[["source","destination"]].drop_duplicates().shape[0] if not df_all.empty else 0

    st.markdown(f"""
    <div class="metric-card"><div class="val">{total}</div><div class="lbl">Total Bookings</div></div>
    <div class="metric-card"><div class="val">{today_count}</div><div class="lbl">Travelling Today</div></div>
    <div class="metric-card"><div class="val">{unique_routes}</div><div class="lbl">Unique Routes</div></div>
    """, unsafe_allow_html=True)


# ─── Page 1: All Bookings ─────────────────────────────────────────────────────
if page == "📋 All Bookings":
    st.markdown('<div class="section-title">All Reservations</div>', unsafe_allow_html=True)
    df = load_df()

    if df.empty:
        st.info("No bookings found. Book a ticket to get started!")
    else:
        col1, col2 = st.columns([3, 2])
        with col1:
            search = st.text_input("🔍 Search passenger or train", placeholder="Type to filter...")
        with col2:
            sources    = ["All"] + sorted(df["source"].unique().tolist())
            src_filter = st.selectbox("Filter by source", sources)

        filtered = df.copy()
        if search:
            mask = (
                filtered["passenger_name"].str.contains(search, case=False, na=False) |
                filtered["train_no"].str.contains(search, case=False, na=False)
            )
            filtered = filtered[mask]
        if src_filter != "All":
            filtered = filtered[filtered["source"] == src_filter]

        st.markdown(f"**{len(filtered)}** record(s) found")
        display = filtered.rename(columns={
            "ticket_id": "ID", "passenger_name": "Passenger", "train_no": "Train",
            "source": "From", "destination": "To", "travel_date": "Date", "seat_no": "Seat"
        })
        st.dataframe(display.set_index("ID"), use_container_width=True,
                     height=min(400, 60 + len(filtered) * 35))

        csv = display.to_csv(index=False).encode()
        st.download_button("⬇️ Download CSV", csv, "bookings.csv", "text/csv")


# ─── Page 2: Book a Ticket ────────────────────────────────────────────────────
elif page == "🎫 Book a Ticket":
    st.markdown('<div class="section-title">New Reservation</div>', unsafe_allow_html=True)

    # Step 1 — passenger + journey details
    with st.form("book_details_form"):
        col1, col2 = st.columns(2)
        with col1:
            name  = st.text_input("👤 Passenger Name", placeholder="Full name")
            train = st.text_input("🚆 Train Number / Name", placeholder="e.g. 12696")
        with col2:
            src  = st.text_input("📍 From (Source)", placeholder="Departure station")
            dest = st.text_input("📍 To (Destination)", placeholder="Arrival station")
        date = st.date_input("📅 Travel Date", min_value=datetime.today())
        details_ok = st.form_submit_button("🪑 Choose Seat →", use_container_width=True)

    if details_ok:
        if not all([name.strip(), train.strip(), src.strip(), dest.strip()]):
            st.error("Please fill in all passenger and journey details.")
        else:
            st.session_state["book_details"] = {
                "name": name.strip(), "train": train.strip(),
                "src": src.strip(), "dest": dest.strip(),
                "date": date.strftime("%d.%m.%Y")
            }

    # Step 2 — seat selection (shown after details are filled)
    if "book_details" in st.session_state:
        d = st.session_state["book_details"]
        booked = get_booked_seats(d["train"], d["date"])
        available = len(all_seats()) - len(booked)

        st.markdown("---")
        st.markdown(f"#### 🪑 Select a Seat — Train **{d['train']}** on **{d['date']}**")

        # Legend
        st.markdown(f"""
        <div class="seat-legend">
            <span><span class="dot" style="background:#E53E3E;"></span> Booked ({len(booked)})</span>
            <span><span class="dot" style="background:white;border:2px solid #C9A84C;"></span> Available ({available})</span>
            <span><span class="dot" style="background:#C9A84C;"></span> Your Selection</span>
        </div>
        """, unsafe_allow_html=True)

        # Keep track of selected seat in session state
        if "selected_seat" not in st.session_state:
            st.session_state["selected_seat"] = None

        chosen = render_seat_map(booked, st.session_state.get("selected_seat"))
        if chosen:
            st.session_state["selected_seat"] = chosen

        selected = st.session_state.get("selected_seat")

        if selected:
            st.success(f"✅ Seat **{selected}** selected")
            if st.button("🎫 Confirm Booking", use_container_width=True, type="primary"):
                tid = book_ticket(d["name"], d["train"], d["src"], d["dest"], d["date"], selected)
                st.success(f"🎉 Ticket booked for **{d['name']}**! (Ticket ID: #{tid})")
                st.balloons()
                st.markdown(f"""
                <div class="ticket-card">
                  <div class="route">🚉 {d['src']} → {d['dest']}</div>
                  <div class="meta">
                    👤 {d['name']} &nbsp;|&nbsp; 🚆 {d['train']} &nbsp;|&nbsp;
                    📅 {d['date']} &nbsp;|&nbsp; 🪑 Seat: <strong>{selected}</strong> &nbsp;|&nbsp; ID: #{tid}
                  </div>
                  <div style="margin-top:8px;"><span class="badge-success">Confirmed</span></div>
                </div>
                """, unsafe_allow_html=True)
                # Clear session state
                del st.session_state["book_details"]
                del st.session_state["selected_seat"]
        else:
            st.info("Click a seat above to select it.")


# ─── Page 3: Modify Booking ───────────────────────────────────────────────────
elif page == "✏️ Modify Booking":
    st.markdown('<div class="section-title">Modify a Reservation</div>', unsafe_allow_html=True)
    df = load_df()

    if df.empty:
        st.info("No bookings available to modify.")
    else:
        with st.expander("📋 View current bookings"):
            st.dataframe(df.set_index("ticket_id"), use_container_width=True)

        with st.form("modify_form"):
            ticket_id = st.number_input("🎟️ Ticket ID to modify", min_value=1, step=1)
            col1, col2 = st.columns(2)
            with col1:
                new_train = st.text_input("🚆 New Train Number / Name")
            with col2:
                new_date = st.date_input("📅 New Travel Date", min_value=datetime.today())
            new_seat = st.selectbox("🪑 New Seat Number", options=all_seats())
            submitted = st.form_submit_button("✏️ Update Booking", use_container_width=True)

        if submitted:
            if not new_train.strip():
                st.error("Please enter a train number.")
            else:
                date_str = new_date.strftime("%d.%m.%Y")
                booked   = get_booked_seats(new_train.strip(), date_str)
                if new_seat in booked:
                    st.error(f"❌ Seat **{new_seat}** is already booked on that train/date. Please choose another.")
                else:
                    # ✅ Calls railway.modify_booking() with seat
                    affected = modify_booking(int(ticket_id), new_train.strip(), date_str, new_seat)
                    if affected:
                        st.success(f"✅ Ticket #{int(ticket_id)} updated! New seat: **{new_seat}**")
                    else:
                        st.error(f"❌ Ticket ID {int(ticket_id)} not found.")


# ─── Page 4: Cancel Booking ───────────────────────────────────────────────────
elif page == "🗑️ Cancel Booking":
    st.markdown('<div class="section-title">Cancel a Reservation</div>', unsafe_allow_html=True)
    df = load_df()

    if df.empty:
        st.info("No bookings available to cancel.")
    else:
        with st.expander("📋 View current bookings"):
            st.dataframe(df.set_index("ticket_id"), use_container_width=True)

        st.warning("⚠️ Cancellation is permanent and cannot be undone.")

        with st.form("cancel_form"):
            ticket_id = st.number_input("🎟️ Ticket ID to cancel", min_value=1, step=1)
            confirm   = st.checkbox("I confirm I want to cancel this ticket.")
            submitted = st.form_submit_button("🗑️ Cancel Booking", use_container_width=True)

        if submitted:
            if not confirm:
                st.error("Please tick the confirmation checkbox first.")
            else:
                # ✅ Calls railway.cancel_booking()
                affected = cancel_booking(int(ticket_id))
                if affected:
                    st.success(f"🗑️ Ticket #{int(ticket_id)} cancelled successfully.")
                else:
                    st.error(f"❌ Ticket ID {int(ticket_id)} not found.")

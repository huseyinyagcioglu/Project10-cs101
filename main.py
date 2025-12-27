import json
import os
import uuid
from datetime import datetime

DATA_DIR = "data"
EVENTS_FILE = os.path.join(DATA_DIR, "events.json")
ATTENDEES_FILE = os.path.join(DATA_DIR, "attendees.json")
REGISTRATIONS_FILE = os.path.join(DATA_DIR, "registrations.json")

os.makedirs(DATA_DIR, exist_ok=True)


def load_json(path):
    """Loads a JSON file that stores a list. Returns [] if file missing or invalid."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_json(path, data):
    """Saves a list to JSON file safely."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def prompt_int(label, min_value=None):
    while True:
        raw = input(label).strip()
        try:
            val = int(raw)
            if min_value is not None and val < min_value:
                print(f" Must be at least {min_value}.")
                continue
            return val
        except ValueError:
            print(" Please enter a valid integer.")


def prompt_float(label, min_value=None):
    while True:
        raw = input(label).strip()
        try:
            val = float(raw)
            if min_value is not None and val < min_value:
                print(f" Must be at least {min_value}.")
                continue
            return val
        except ValueError:
            print(" Please enter a valid number.")


def prompt_date(label):
    while True:
        raw = input(label).strip()
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print(" Date format must be YYYY-MM-DD (e.g., 2025-12-27).")


events = load_json(EVENTS_FILE)
attendees = load_json(ATTENDEES_FILE)
registrations = load_json(REGISTRATIONS_FILE)


# ---------------- EVENT MANAGEMENT ----------------

def create_event():
    name = input("Event name: ").strip()
    if not name:
        print(" Event name cannot be empty.")
        return

    # optional: prevent duplicate event name (simple check)
    if any(e["name"].lower() == name.lower() for e in events):
        print(" An event with the same name already exists.")
        return

    start_date = prompt_date("Start date (YYYY-MM-DD): ")
    end_date = prompt_date("End date (YYYY-MM-DD): ")

    # quick validation: end >= start
    if end_date < start_date:
        print(" End date cannot be earlier than start date.")
        return

    event = {
        "id": str(uuid.uuid4()),
        "name": name,
        "location": input("Location: ").strip(),
        "start_date": start_date,
        "end_date": end_date,
        "capacity": prompt_int("Capacity: ", min_value=1),
        "price": prompt_float("Ticket price: ", min_value=0.0),
        "description": input("Description: ").strip(),
        "sessions": []
    }

    events.append(event)
    save_json(EVENTS_FILE, events)
    print(" Event created.")


def list_events():
    if not events:
        print(" No events found. Create one first.")
        return
    for e in events:
        print(f"{e['id']} | {e['name']} | {e.get('location','')} | Capacity: {e['capacity']}")


def get_event_by_id(event_id):
    return next((e for e in events if e["id"] == event_id), None)


#ATTENDEE MANAGEMENT 

def register_attendee():
    email = input("Email: ").strip().lower()
    if not email:
        print("❌ Email cannot be empty.")
        return

    # prevent duplicate attendee by email
    if any(a["email"].lower() == email for a in attendees):
        print("⚠️ This email is already registered as an attendee.")
        return

    pin = str(uuid.uuid4())[:4].upper()
    attendee = {
        "id": str(uuid.uuid4()),
        "name": input("Full name: ").strip(),
        "email": email,
        "organization": input("Organization: ").strip(),
        "dietary": input("Dietary needs: ").strip(),
        "pin": pin
    }

    attendees.append(attendee)
    save_json(ATTENDEES_FILE, attendees)
    print(f"✅ Attendee registered. PIN: {pin}")


def get_attendee_by_email(email):
    email = (email or "").strip().lower()
    return next((a for a in attendees if a["email"].lower() == email), None)


#REGISTRATION 

def create_registration():
    if not events:
        print(" No events available. Create an event first.")
        return

    list_events()
    event_id = input("Enter event ID: ").strip()
    event = get_event_by_id(event_id)
    if not event:
        print(" Event not found.")
        return

    email = input("Attendee email: ").strip().lower()
    attendee = get_attendee_by_email(email)
    if not attendee:
        print(" Attendee not found. Register the attendee first.")
        return

    # prevent duplicate registration for same attendee+event
    already = any(
        r["event_id"] == event_id and r["attendee_id"] == attendee["id"]
        for r in registrations
    )
    if already:
        print(" This attendee is already registered for this event.")
        return

    confirmed_regs = [
        r for r in registrations
        if r["event_id"] == event_id and r["status"] == "CONFIRMED"
    ]

    status = "CONFIRMED" if len(confirmed_regs) < event["capacity"] else "WAITLIST"

    registration = {
        "id": str(uuid.uuid4()),
        "event_id": event_id,
        "attendee_id": attendee["id"],
        "status": status,
        "confirmation_code": str(uuid.uuid4())[:8].upper(),
        "checked_in": False,
        "created_at": datetime.now().isoformat()
    }

    registrations.append(registration)
    save_json(REGISTRATIONS_FILE, registrations)

    print(f" Registration {status}. Code: {registration['confirmation_code']}")


# ---------------- CHECK-IN ----------------

def check_in():
    code = input("Confirmation code: ").strip().upper()
    reg = next((r for r in registrations if r["confirmation_code"].upper() == code), None)

    if not reg:
        print(" Invalid code.")
        return

    if reg.get("checked_in"):
        print(" Already checked in.")
        return

    if reg.get("status") != "CONFIRMED":
        print(" Cannot check-in a WAITLIST registration.")
        return

    reg["checked_in"] = True
    reg["checkin_time"] = datetime.now().isoformat()
    save_json(REGISTRATIONS_FILE, registrations)

    print(" Check-in successful.")


# ---------------- REPORTS ----------------

def attendance_report():
    if not events:
        print(" No events found.")
        return

    for event in events:
        total = len([r for r in registrations if r["event_id"] == event["id"]])
        confirmed = len([r for r in registrations if r["event_id"] == event["id"] and r["status"] == "CONFIRMED"])
        waitlist = len([r for r in registrations if r["event_id"] == event["id"] and r["status"] == "WAITLIST"])
        checked = len([r for r in registrations if r["event_id"] == event["id"] and r.get("checked_in")])

        print(
            f"{event['name']} | Total: {total} | Confirmed: {confirmed} | "
            f"Waitlist: {waitlist} | Checked-in: {checked}"
        )


# ---------------- MENU ----------------

def menu():
    while True:
        print("""
1. Create Event
2. List Events
3. Register Attendee
4. Create Registration
5. Check-In
6. Attendance Report
0. Exit
        """.strip())

        choice = input("\nSelect: ").strip()

        if choice == "1":
            create_event()
        elif choice == "2":
            list_events()
        elif choice == "3":
            register_attendee()
        elif choice == "4":
            create_registration()
        elif choice == "5":
            check_in()
        elif choice == "6":
            attendance_report()
        elif choice == "0":
            break
        else:
            print(" Invalid choice.")


if __name__ == "__main__":
    menu()

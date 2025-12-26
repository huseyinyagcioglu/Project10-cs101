events = []
registrations = []

def create_event():
    name = input("Event name: ")
    capacity = int(input("Capacity: "))

    event = {
        "id": len(events) + 1,
        "name": name,
        "capacity": capacity
    }
    events.append(event)
    print("Event created successfully.\n")

def list_events():
    if not events:
        print("No events available.\n")
        return

    for e in events:
        registered = sum(1 for r in registrations if r["event_id"] == e["id"])
        print(f"{e['id']}. {e['name']} ({registered}/{e['capacity']})")
    print()

def register_attendee():
    if not events:
        print("No events to register.\n")
        return

    list_events()
    event_id = int(input("Choose event ID: "))
    name = input("Your name: ")

    event = next((e for e in events if e["id"] == event_id), None)
    if event is None:
        print("Invalid event.\n")
        return

    registered = sum(1 for r in registrations if r["event_id"] == event_id)
    status = "CONFIRMED" if registered < event["capacity"] else "WAITLIST"

    registration = {
        "event_id": event_id,
        "name": name,
        "status": status
    }

    registrations.append(registration)
    print(f"Registration status: {status}\n")

def list_registrations():
    if not registrations:
        print("No registrations yet.\n")
        return

    for r in registrations:
        event_name = next(e["name"] for e in events if e["id"] == r["event_id"])
        print(f"{r['name']} → {event_name} [{r['status']}]")
    print()

def menu():
    while True:
        print("====== EVENT REGISTRATION SYSTEM ======")
        print("1. Create Event (Organizer)")
        print("2. List Events")
        print("3. Register for Event (Attendee)")
        print("4. View Registrations")
        print("0. Exit")

        choice = input("Choose: ")

        if choice == "1":
            create_event()
        elif choice == "2":
            list_events()
        elif choice == "3":
            register_attendee()
        elif choice == "4":
            list_registrations()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.\n")

menu()

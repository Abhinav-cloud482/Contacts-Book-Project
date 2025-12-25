import json
import os
import datetime
import csv
from colorama import init, Fore, Style
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

init(autoreset=True)

CONTACTS_FILE = 'contacts.json'
POPULARITY_FILE = 'popularity.json'
RECENT_FILE = 'recent.json'

# Training sample
names = ["John Smith", "Mom", "Dr. Patel", "James HR", "Sis", "Client XYZ"]
emails = ["john@company.com", "mom@gmail.com", "patel@hospital.org", "hr@work.com", "sis@yahoo.com", "client@business.com"]
labels = ["Work", "Family", "Work", "Work", "Family", "Client"]
features = [f"{name} {email}" for name, email in zip(names, emails)]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(features)
model = MultinomialNB()
model.fit(X, labels)

# Utility functions
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_json(file_path, default):
    if not os.path.exists(file_path):
        return default
    with open(file_path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default

def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def load_contacts():
    return load_json(CONTACTS_FILE, [])

def save_contacts(contacts):
    save_json(CONTACTS_FILE, contacts)

def load_popularity():
    return load_json(POPULARITY_FILE, {})

def save_popularity(popularity):
    save_json(POPULARITY_FILE, popularity)

def predict_category(name, email):
    input_text = f"{name} {email}"
    x_input = vectorizer.transform([input_text])
    return model.predict(x_input)[0]

def increment_popularity(name):
    popularity = load_popularity()
    popularity[name] = popularity.get(name, 0) + 1
    save_popularity(popularity)

def update_recent(name):
    recent = load_json(RECENT_FILE, [])
    if name in recent:
        recent.remove(name)
    recent.insert(0, name)
    recent = recent[:5]
    save_json(RECENT_FILE, recent)

# Feature Functions
def is_duplicate(new_name, new_email, new_phone, contacts):
    for contact in contacts:
        if fuzz.ratio(contact['name'].lower(), new_name.lower()) > 90:
            return f"Name is very similar to '{contact['name']}'"
        if contact['email'].lower() == new_email.lower():
            return "Email already exists"
        if contact['phone'] == new_phone:
            return "Phone number already exists"
    return None

def add_contact():
    clear_screen()
    print(Fore.CYAN + Style.BRIGHT + "Add New Contact\n")

    name = input("Enter name: ")
    phone = input("Enter phone number: ")
    email = input("Enter email: ")
    note = input("Enter note or tag (optional): ")
    date_added = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    contacts = load_contacts()

    reason = is_duplicate(name, email, phone, contacts)
    if reason:
        print(Fore.YELLOW + f"Contact not added. Reason: {reason}\n")
        return

    category = predict_category(name, email)

    contact = {
        "name": name,
        "phone": phone,
        "email": email,
        "date_added": date_added,
        "category": category,
        "note": note
    }

    contacts.append(contact)
    save_contacts(contacts)
    print(Fore.GREEN + f"Contact '{name}' added successfully! Predicted category: {category}\n")

def view_contacts():
    clear_screen()
    contacts = load_contacts()
    if not contacts:
        print(Fore.LIGHTBLACK_EX + "No contacts found.\n")
        return

    popularity = load_popularity()
    contacts.sort(key=lambda c: (-popularity.get(c['name'], 0), c['name'].lower()))

    print(Fore.MAGENTA + Style.BRIGHT + "\nContact List (Sorted by Popularity):\n")
    for idx, contact in enumerate(contacts, start=1):
        views = popularity.get(contact['name'], 0)
        print(f"{idx}. {Fore.CYAN}Name: {contact['name']} [{contact['category']}], "
              f"Phone: {contact['phone']}, Email: {contact['email']}, "
              f"Note: {contact.get('note', 'None')}, "
              f"Added: {contact.get('date_added', 'N/A')}, Views: {views}")
    print("")

def search_contact():
    clear_screen()
    query = input("Enter name, phone, or email to search: ").lower()
    contacts = load_contacts()
    popularity = load_popularity()
    results = []

    threshold = 60
    for contact in contacts:
        scores = [
            fuzz.partial_ratio(query, contact['name'].lower()),
            fuzz.partial_ratio(query, contact['email'].lower()),
            fuzz.partial_ratio(query, contact['phone'])
        ]
        if max(scores) >= threshold:
            results.append(contact)

    if results:
        print(Fore.GREEN + f"\nFound {len(results)} result(s):\n")
        for contact in results:
            print(f"Name: {contact['name']} [{contact['category']}], Phone: {contact['phone']}, "
                  f"Email: {contact['email']}, Note: {contact.get('note', 'None')}")
            increment_popularity(contact['name'])
            update_recent(contact['name'])
    else:
        print(Fore.RED + "No contact matched your query.\n")

def edit_contact():
    contacts = load_contacts()
    view_contacts()

    try:
        index = int(input("Enter contact number to edit: ")) - 1
        if index < 0 or index >= len(contacts):
            print(Fore.RED + "Invalid selection.\n")
            return

        contact = contacts[index]
        print(Fore.CYAN + f"Editing '{contact['name']}'")

        new_name = input(f"New name [{contact['name']}]: ") or contact['name']
        new_phone = input(f"New phone [{contact['phone']}]: ") or contact['phone']
        new_email = input(f"New email [{contact['email']}]: ") or contact['email']
        new_note = input(f"New note [{contact.get('note', '')}]: ") or contact.get('note', '')

        for i, c in enumerate(contacts):
            if i != index:
                if fuzz.ratio(c['name'].lower(), new_name.lower()) > 90:
                    print(Fore.YELLOW + f"Another contact with similar name '{new_name}' exists.")
                    return
                if c['phone'] == new_phone:
                    print(Fore.YELLOW + "Phone number already in use.")
                    return
                if c['email'].lower() == new_email.lower():
                    print(Fore.YELLOW + "Email already in use.")
                    return

        contacts[index]['name'] = new_name
        contacts[index]['phone'] = new_phone
        contacts[index]['email'] = new_email
        contacts[index]['note'] = new_note
        contacts[index]['category'] = predict_category(new_name, new_email)

        save_contacts(contacts)
        print(Fore.GREEN + "Contact updated.\n")

    except ValueError:
        print(Fore.RED + "Invalid input.\n")

def delete_contact():
    contacts = load_contacts()
    view_contacts()

    try:
        index = int(input("Enter contact number to delete: ")) - 1
        if index < 0 or index >= len(contacts):
            print(Fore.RED + "Invalid selection.\n")
            return

        confirm = input(f"Are you sure you want to delete '{contacts[index]['name']}'? (y/n): ").lower()
        if confirm == 'y':
            deleted = contacts.pop(index)
            save_contacts(contacts)
            popularity = load_popularity()
            popularity.pop(deleted['name'], None)
            save_popularity(popularity)
            print(Fore.GREEN + f"Contact '{deleted['name']}' deleted.\n")
        else:
            print(Fore.YELLOW + "Deletion canceled.\n")

    except ValueError:
        print(Fore.RED + "Invalid input.\n")

def sort_contacts():
    contacts = load_contacts()
    contacts.sort(key=lambda c: c['name'].lower())
    save_contacts(contacts)
    print(Fore.GREEN + "Contacts sorted by name.\n")
    view_contacts()

def export_to_csv():
    contacts = load_contacts()
    if not contacts:
        print(Fore.LIGHTBLACK_EX + "No contacts to export.\n")
        return

    with open('contacts_export.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["name", "phone", "email", "date_added", "category", "note"])
        writer.writeheader()
        writer.writerows(contacts)

    print(Fore.GREEN + "Contacts exported to 'contacts_export.csv'.\n")

def filter_by_category():
    contacts = load_contacts()
    categories = sorted(set(c['category'] for c in contacts))
    if not categories:
        print(Fore.YELLOW + "No categories found.")
        return

    print("Available Categories:")
    for cat in categories:
        print(f"- {cat}")

    selected = input("Enter category to filter: ").strip()
    filtered = [c for c in contacts if c['category'].lower() == selected.lower()]
    if not filtered:
        print(Fore.RED + f"No contacts in category '{selected}'.\n")
        return

    print(Fore.GREEN + f"\nContacts in '{selected}':\n")
    for c in filtered:
        print(f"{c['name']} - {c['phone']} - {c['email']} - Note: {c.get('note', 'None')}")

def backup_contacts():
    contacts = load_contacts()
    if not contacts:
        print(Fore.YELLOW + "No contacts to backup.")
        return
    filename = f'contacts_backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    save_json(filename, contacts)
    print(Fore.GREEN + f"Backup saved as {filename}.")

def restore_contacts():
    filename = input("Enter backup filename to restore: ").strip()
    if not os.path.exists(filename):
        print(Fore.RED + "File not found.")
        return
    try:
        contacts = load_json(filename, [])
        save_contacts(contacts)
        print(Fore.GREEN + f"Contacts restored from {filename}.")
    except:
        print(Fore.RED + "Failed to load backup.")

def import_from_csv():
    filepath = input("Enter path to CSV file: ").strip()
    if not os.path.exists(filepath):
        print(Fore.RED + "File not found.")
        return

    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        new_contacts = list(reader)

    contacts = load_contacts()
    added = 0
    for contact in new_contacts:
        name, phone, email = contact.get("name"), contact.get("phone"), contact.get("email")
        if not name or not phone or not email:
            continue
        if not is_duplicate(name, email, phone, contacts):
            contact['category'] = predict_category(name, email)
            contact['note'] = contact.get("note", "")
            contact['date_added'] = contact.get("date_added") or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            contacts.append(contact)
            added += 1
    save_contacts(contacts)
    print(Fore.GREEN + f"{added} contacts imported.")

def show_dashboard():
    contacts = load_contacts()
    popularity = load_popularity()
    clear_screen()
    print(Fore.BLUE + Style.BRIGHT + "Dashboard\n")
    print(f"Total Contacts: {len(contacts)}")
    if contacts:
        latest = sorted(contacts, key=lambda c: c.get("date_added", ""), reverse=True)[0]
        print(f"Most Recently Added: {latest['name']} ({latest.get('date_added', 'N/A')})")
        most_viewed = max(popularity.items(), key=lambda x: x[1], default=(None, 0))
        if most_viewed[0]:
            print(f"Most Viewed: {most_viewed[0]} (Views: {most_viewed[1]})")
    recent = load_json(RECENT_FILE, [])
    if recent:
        print("Recently Viewed:")
        for name in recent:
            print(f"  - {name}")
    print("")

# Main Menu
def main():
    while True:
        show_dashboard()
        print(Style.BRIGHT + "\n====== Contact Book Menu ======")
        print("1. Add Contact")
        print("2. View Contacts")
        print("3. Search Contact")
        print("4. Edit Contact")
        print("5. Delete Contact")
        print("6. Sort Contacts by Name")
        print("7. Export to CSV")
        print("8. Filter by Category")
        print("9. Backup Contacts")
        print("10. Restore Contacts")
        print("11. Import from CSV")
        print("12. Exit")
        choice = input("\nChoose an option (1-12): ")

        match choice:
            case '1': add_contact()
            case '2': view_contacts()
            case '3': search_contact()
            case '4': edit_contact()
            case '5': delete_contact()
            case '6': sort_contacts()
            case '7': export_to_csv()
            case '8': filter_by_category()
            case '9': backup_contacts()
            case '10': restore_contacts()
            case '11': import_from_csv()
            case '12':
                print(Fore.MAGENTA + "Goodbye!")
                break
            case _: print(Fore.RED + "Invalid option. Try again.\n")

        input(Fore.LIGHTBLACK_EX + "\nPress Enter to return to menu...")

if __name__ == '__main__':
    main()

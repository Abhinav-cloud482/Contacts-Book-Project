## Contacts-Book-Project

# Contacts Book (Python CLI)

A command-line Contacts Book application built with Python that stores and manages contacts using local JSON files.
The project includes fuzzy search, automatic category prediction, and basic analytics like popularity tracking.

# Files

contacts book.py   # Main application
contacts.json      # Contact data storage
popularity.json    # View counts (auto-created)
recent.json        # Recently viewed contacts (auto-created)
contacts_export.csv # CSV export (generated)
contacts_backup_*.json # Backup files (generated)

# Features

- Add, view, edit, and delete contacts

- Automatic category prediction (Work / Family / Client)

- Fuzzy search by name, phone, or email

- Duplicate detection (name similarity, phone, email)

- Popularity-based sorting (most viewed first)

- Recently viewed contacts tracking

- Filter contacts by category

- Export contacts to CSV

- Import contacts from CSV

- Backup and restore contacts using JSON files

# Technologies Used

- Python 3

- JSON & CSV

- Colorama (CLI colors)

- RapidFuzz (fuzzy matching)

- scikit-learn (Naive Bayes classifier)

# How It Works

- Contacts are stored in contacts.json

- Categories are predicted using a Naive Bayes model trained on sample name–email data

- Searches use fuzzy matching for partial or mistyped input

- Contact views update popularity and recent history automatically

# Run the Project
```
pip install colorama rapidfuzz scikit-learn
python "contacts book.py"
```

# Summary

This project demonstrates a Python-based contact management system with persistent storage, intelligent searching, and basic machine learning — all implemented in a menu-driven CLI.

# Author

Abhinav Dixit

Python Developer | Data & ML Enthusiast

- Feel free to fork, star, or contribute to this project!

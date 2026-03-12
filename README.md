# KBT - Fishing Tournament App

This project is a Python application with a PostgreSQL database used to manage fishing tournaments.  
The database tracks tournaments, directors, anglers, livewells, fish, and fish photos.

## Project Structure

KBT/
│
├── app/ # Python application code
├── database/ # SQL schema and database scripts
│ └── schema.sql
├── scripts/ # Utility scripts (ex: database initialization)
│ └── init_db.py
│
├── requirements.txt # Python dependencies
├── .env.example # Example environment variables
└── README.md


## Database Overview

The schema models the following relationships:

- **Users** are the base entity.
- Users can be either **Directors** or **Anglers**.
- Each **Tournament** is managed by one Director.
- **Anglers can participate in many tournaments**, and tournaments can have many anglers.
- Each angler's participation in a tournament has **one livewell**.
- A **livewell contains many fish**.
- Each **fish has exactly one photo**.

Main tables:

- `users`
- `directors`
- `anglers`
- `tournaments`
- `tournament_anglers`
- `livewell`
- `fish`
- `fish_photo`

## Setup

### 1. Clone the repository

### 2. Create a Python virtual environment


Activate it:

**Mac/Linux**

**Windows**

### 3. Install dependencies

### 4. Configure environment variables

Copy the example file:

Edit `.env` with your database credentials.

### 5. Create the database schema

Run the schema file in PostgreSQL:

## Technologies Used

- Python
- PostgreSQL
- Git / GitHub

## Author

Cha Vue, Justin Halvorson






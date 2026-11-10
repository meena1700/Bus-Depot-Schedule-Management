# Bus Depot & Schedule Management Dashboard

## Project Description
This project is a Python-based Bus Depot and Schedule Management Dashboard developed using SQLite and Tkinter. It helps manage bus depots, bus schedules and stop allocations through a simple graphical user interface.

## Technologies Used
- Python
- SQLite
- Tkinter

## Features
- Add new depot and schedule records.
- Reuse existing depot IDs to avoid duplicate entries.
- Manage stop allocations and fare details.
- View records in four different tabs.
- Delete selected records.
- Automatic cascading deletion using foreign keys.
- Input validation.
- Automatic database creation and sample data insertion.

## Database Structure
The project consists of three relational tables:

1. Depots
2. Bus Schedules
3. Stop Allocations

## How to Run

1. Install Python on your computer.
2. Download the Python file from this repository.
3. Open the terminal in the folder containing the file.
4. Run the following command:

`python bus_depot_dashboard.py`

The application automatically creates an SQLite database if one does not already exist.

## Project Outcome
The application provides a simple and organized way to manage bus depot information, schedules and stop allocations while maintaining database relationships and data consistency.

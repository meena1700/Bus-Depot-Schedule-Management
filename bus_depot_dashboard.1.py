
"""
BUS DEPOT AND SCHEDULE MANAGEMENT SYSTEM
Single-file runnable Python desktop application using SQLite and Tkinter.
"""

import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date


# ==========================================
# DATABASE CLASS
# ==========================================

class Database:
    def __init__(self, db_path):
        self.con = sqlite3.connect(db_path)
        self.con.execute("PRAGMA foreign_keys = ON")
        self.cur = self.con.cursor()
        self.create_tables()
        self.insert_sample_data()

    def create_tables(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS depots (
                depot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                depot_name TEXT UNIQUE NOT NULL,
                manager_email TEXT NOT NULL
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS bus_schedules (
                schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                depot_id INTEGER NOT NULL,
                route_name TEXT NOT NULL,
                schedule_date TEXT NOT NULL,
                FOREIGN KEY (depot_id)
                    REFERENCES depots(depot_id)
                    ON DELETE CASCADE
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS stop_allocations (
                allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id INTEGER NOT NULL,
                stop_name TEXT NOT NULL,
                fare REAL NOT NULL CHECK (fare >= 0),
                FOREIGN KEY (schedule_id)
                    REFERENCES bus_schedules(schedule_id)
                    ON DELETE CASCADE
            )
        """)
        self.con.commit()

    # Insert sample records only when all three tables are empty
    def insert_sample_data(self):
        self.cur.execute("""
            SELECT
                (SELECT COUNT(*) FROM depots) +
                (SELECT COUNT(*) FROM bus_schedules) +
                (SELECT COUNT(*) FROM stop_allocations)
        """)
        total_records = self.cur.fetchone()[0]

        if total_records != 0:
            return

        today = date.today().isoformat()

        depots = [
            ("Yeshwanthpur Depot", "yeshwanthpur@gmail.com"),
            ("Majestic Depot", "majestic@gmail.com"),
            ("Vijayanagar Depot", "vijayanagar@gmail.com")
        ]

        depot_ids = {}

        for depot_name, manager_email in depots:
            self.cur.execute(
                "INSERT INTO depots (depot_name, manager_email) VALUES (?, ?)",
                (depot_name, manager_email)
            )
            depot_ids[depot_name] = self.cur.lastrowid

        schedules = [
            (depot_ids["Yeshwanthpur Depot"], "Route 42", today),
            (depot_ids["Yeshwanthpur Depot"], "Route 15", today),
            (depot_ids["Majestic Depot"], "Route 10", today),
            (depot_ids["Vijayanagar Depot"], "Route 25", today)
        ]

        schedule_ids = []

        for depot_id, route_name, schedule_date in schedules:
            self.cur.execute("""
                INSERT INTO bus_schedules (depot_id, route_name, schedule_date)
                VALUES (?, ?, ?)
            """, (depot_id, route_name, schedule_date))
            schedule_ids.append(self.cur.lastrowid)

        allocations = [
            (schedule_ids[0], "Majestic", 25),
            (schedule_ids[0], "Malleshwaram", 15),
            (schedule_ids[1], "Yeshwanthpur", 20),
            (schedule_ids[2], "City Market", 30),
            (schedule_ids[3], "Vijayanagar", 20)
        ]

        self.cur.executemany("""
            INSERT INTO stop_allocations (schedule_id, stop_name, fare)
            VALUES (?, ?, ?)
        """, allocations)

        self.con.commit()

    # Insert a depot if it does not exist, then add schedule and allocation
    def add_record(self, depot_name, manager_email, route_name, stop_name, fare):
        self.cur.execute(
            "SELECT depot_id FROM depots WHERE depot_name = ?",
            (depot_name,)
        )
        result = self.cur.fetchone()

        if result:
            depot_id = result[0]
        else:
            self.cur.execute("""
                INSERT INTO depots (depot_name, manager_email)
                VALUES (?, ?)
            """, (depot_name, manager_email))
            depot_id = self.cur.lastrowid

        self.cur.execute("""
            INSERT INTO bus_schedules (depot_id, route_name, schedule_date)
            VALUES (?, ?, ?)
        """, (depot_id, route_name, date.today().isoformat()))

        schedule_id = self.cur.lastrowid

        self.cur.execute("""
            INSERT INTO stop_allocations (schedule_id, stop_name, fare)
            VALUES (?, ?, ?)
        """, (schedule_id, stop_name, fare))

        self.con.commit()

    # Fetch records from all tables
    def fetch_depots(self):
        self.cur.execute("SELECT * FROM depots ORDER BY depot_id")
        return self.cur.fetchall()

    def fetch_schedules(self):
        self.cur.execute("SELECT * FROM bus_schedules ORDER BY schedule_id")
        return self.cur.fetchall()

    def fetch_allocations(self):
        self.cur.execute("SELECT * FROM stop_allocations ORDER BY allocation_id")
        return self.cur.fetchall()

    def fetch_combined(self):
        self.cur.execute("""
            SELECT
                bs.schedule_id,
                d.depot_name,
                bs.route_name,
                bs.schedule_date,
                sa.stop_name,
                sa.fare
            FROM bus_schedules bs
            JOIN depots d ON bs.depot_id = d.depot_id
            JOIN stop_allocations sa ON bs.schedule_id = sa.schedule_id
            ORDER BY bs.schedule_id, sa.allocation_id
        """)
        return self.cur.fetchall()

    # Delete one selected record; foreign keys handle cascading deletion
    def delete_record(self, table_name, record_id):
        allowed_tables = {
            "depots": "depot_id",
            "bus_schedules": "schedule_id",
            "stop_allocations": "allocation_id"
        }

        if table_name not in allowed_tables:
            raise ValueError("Invalid table name")

        id_column = allowed_tables[table_name]

        self.cur.execute(
            f"DELETE FROM {table_name} WHERE {id_column} = ?",
            (record_id,)
        )
        self.con.commit()

    def close(self):
        self.con.close()


# ==========================================
# GUI APPLICATION SETUP
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bus_depot.db")
db = Database(DB_PATH)

root = tk.Tk()
root.title("BUS DEPOT AND SCHEDULE MANAGEMENT")
root.geometry("1180x760")
root.minsize(950, 650)

# Form variables
depot_name = tk.StringVar()
manager_email = tk.StringVar()
route_name = tk.StringVar()
stop_name = tk.StringVar()
fare_value = tk.StringVar()
delete_choice = tk.StringVar()
delete_id = tk.StringVar()

# Main title
title = tk.Label(
    root,
    text="BUS DEPOT & SCHEDULE MANAGEMENT DASHBOARD",
    font=("Calibri", 20, "bold"),
    bg="#174A6E",
    fg="white",
    pady=14
)
title.pack(fill=tk.X)


# ==========================================
# INSERT RECORDS FRAME
# ==========================================

insert_frame = tk.LabelFrame(
    root, text=" Add New Record ",
    font=("Calibri", 13, "bold"), padx=10, pady=10
)
insert_frame.pack(fill=tk.X, padx=12, pady=10)

fields = [
    ("Depot Name", depot_name),
    ("Manager Email", manager_email),
    ("Route Name", route_name),
    ("Stop Name", stop_name),
    ("Fare Value", fare_value)
]

for index, (field_label, variable) in enumerate(fields):
    row = index // 3
    column = (index % 3) * 2

    tk.Label(
        insert_frame, text=field_label, font=("Calibri", 11, "bold")
    ).grid(row=row, column=column, padx=6, pady=7, sticky="w")

    tk.Entry(
        insert_frame, textvariable=variable, font=("Calibri", 11), width=25
    ).grid(row=row, column=column + 1, padx=6, pady=7, sticky="w")


# ==========================================
# TABLE DISPLAY FUNCTIONS
# ==========================================

tree_views = {}


def create_table_tab(notebook, tab_name, columns, headings):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=tab_name)

    tree = ttk.Treeview(frame, columns=columns, show="headings")

    for column, heading in zip(columns, headings):
        tree.heading(column, text=heading)
        tree.column(column, width=150, anchor="center")

    vertical_scroll = ttk.Scrollbar(
        frame, orient="vertical", command=tree.yview
    )

    horizontal_scroll = ttk.Scrollbar(
        frame, orient="horizontal", command=tree.xview
    )

    tree.configure(
        yscrollcommand=vertical_scroll.set,
        xscrollcommand=horizontal_scroll.set
    )

    tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    vertical_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    horizontal_scroll.pack(side=tk.BOTTOM, fill=tk.X)

    tree_views[tab_name] = tree


# ==========================================
# NOTEBOOK WITH FOUR TABS
# ==========================================

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=5)

create_table_tab(
    notebook, "Combined View",
    ("schedule_id", "depot", "route", "date", "stop", "fare"),
    ("Schedule ID", "Depot Name", "Route Name",
     "Schedule Date", "Stop Name", "Fare")
)

create_table_tab(
    notebook, "Depots",
    ("depot_id", "depot_name", "manager_email"),
    ("Depot ID", "Depot Name", "Manager Email")
)

create_table_tab(
    notebook, "Bus Schedules",
    ("schedule_id", "depot_id", "route_name", "schedule_date"),
    ("Schedule ID", "Depot ID", "Route Name", "Schedule Date")
)

create_table_tab(
    notebook, "Stop Allocations",
    ("allocation_id", "schedule_id", "stop_name", "fare"),
    ("Allocation ID", "Schedule ID", "Stop Name", "Fare")
)


def fill_tree(tree, records):
    tree.delete(*tree.get_children())

    for record in records:
        tree.insert("", tk.END, values=record)


def display_all():
    fill_tree(tree_views["Combined View"], db.fetch_combined())
    fill_tree(tree_views["Depots"], db.fetch_depots())
    fill_tree(tree_views["Bus Schedules"], db.fetch_schedules())
    fill_tree(tree_views["Stop Allocations"], db.fetch_allocations())

    refresh_delete_dropdowns()


# ==========================================
# ADD, DELETE AND CLEAR FUNCTIONS
# ==========================================

def clear_inputs():
    depot_name.set("")
    manager_email.set("")
    route_name.set("")
    stop_name.set("")
    fare_value.set("")


def add_record():
    depot = depot_name.get().strip()
    email = manager_email.get().strip()
    route = route_name.get().strip()
    stop = stop_name.get().strip()
    fare_text = fare_value.get().strip()

    if not all([depot, email, route, stop, fare_text]):
        messagebox.showerror("Input Error", "Please fill in all the fields.")
        return

    if "@" not in email or "." not in email.split("@")[-1]:
        messagebox.showerror("Input Error", "Please enter a valid email address.")
        return

    try:
        fare = float(fare_text)

        if fare < 0:
            raise ValueError

    except ValueError:
        messagebox.showerror(
            "Input Error", "Fare must be a valid non-negative number."
        )
        return

    try:
        db.add_record(depot, email, route, stop, fare)
        messagebox.showinfo("Success", "Record added successfully.")

        clear_inputs()
        display_all()

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


def refresh_delete_dropdowns():
    depot_options = [
        f'{row[0]} - {row[1]}' for row in db.fetch_depots()
    ]

    schedule_options = [
        f'{row[0]} - {row[2]}' for row in db.fetch_schedules()
    ]

    allocation_options = [
        f'{row[0]} - {row[2]}' for row in db.fetch_allocations()
    ]

    depot_delete_combo["values"] = depot_options
    schedule_delete_combo["values"] = schedule_options
    allocation_delete_combo["values"] = allocation_options

    depot_delete_combo.set("")
    schedule_delete_combo.set("")
    allocation_delete_combo.set("")


def delete_selected():
    selections = [
        ("depots", depot_delete_combo.get()),
        ("bus_schedules", schedule_delete_combo.get()),
        ("stop_allocations", allocation_delete_combo.get())
    ]

    selected = [
        (table, value) for table, value in selections if value
    ]

    if len(selected) != 1:
        messagebox.showwarning(
            "Selection Required",
            "Please select exactly one record from one delete dropdown."
        )
        return

    table_name, selected_value = selected[0]
    record_id = int(selected_value.split(" - ", 1)[0])

    if not messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete the selected record?"
    ):
        return

    try:
        db.delete_record(table_name, record_id)
        messagebox.showinfo("Success", "Selected record deleted.")
        display_all()

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


# ==========================================
# BUTTONS AND DELETE PANEL
# ==========================================

button_frame = tk.Frame(insert_frame)
button_frame.grid(row=2, column=0, columnspan=6, pady=10, sticky="w")

tk.Button(
    button_frame, text="Add Record", command=add_record,
    font=("Calibri", 11, "bold"), bg="#1E8449", fg="white",
    width=16, cursor="hand2"
).pack(side=tk.LEFT, padx=5)

tk.Button(
    button_frame, text="Clear Fields", command=clear_inputs,
    font=("Calibri", 11, "bold"), width=16, cursor="hand2"
).pack(side=tk.LEFT, padx=5)

delete_frame = tk.LabelFrame(
    root, text=" Delete Records ",
    font=("Calibri", 12, "bold"), padx=10, pady=8
)
delete_frame.pack(fill=tk.X, padx=12, pady=5)

tk.Label(delete_frame, text="Depot:", font=("Calibri", 10, "bold")).grid(
    row=0, column=0, padx=5, pady=5
)

depot_delete_combo = ttk.Combobox(
    delete_frame, textvariable=delete_choice, state="readonly", width=25
)
depot_delete_combo.grid(row=0, column=1, padx=5, pady=5)

tk.Label(delete_frame, text="Bus Schedule:", font=("Calibri", 10, "bold")).grid(
    row=0, column=2, padx=5, pady=5
)

schedule_delete_combo = ttk.Combobox(
    delete_frame, state="readonly", width=25
)
schedule_delete_combo.grid(row=0, column=3, padx=5, pady=5)

tk.Label(delete_frame, text="Stop Allocation:", font=("Calibri", 10, "bold")).grid(
    row=0, column=4, padx=5, pady=5
)

allocation_delete_combo = ttk.Combobox(
    delete_frame, state="readonly", width=25
)
allocation_delete_combo.grid(row=0, column=5, padx=5, pady=5)

tk.Button(
    delete_frame, text="DELETE SELECTED", command=delete_selected,
    font=("Calibri", 10, "bold"), bg="#B03A2E", fg="white",
    width=18, cursor="hand2"
).grid(row=0, column=6, padx=8, pady=5)


# ==========================================
# INITIAL LOAD AND APPLICATION CLOSE
# ==========================================

display_all()


def close_application():
    db.close()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_application)
root.mainloop()

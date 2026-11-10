import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date


# =====================================================
# 1. DATABASE CONNECTION AND INITIALIZATION
# =====================================================

conn = sqlite3.connect("bus_depot.db")
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()


# CREATE DEPOTS TABLE

cur.execute("""
CREATE TABLE IF NOT EXISTS depots (
    depot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    depot_name TEXT UNIQUE NOT NULL,
    manager_email TEXT NOT NULL
)
""")


# CREATE BUS SCHEDULES TABLE

cur.execute("""
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


# CREATE STOP ALLOCATIONS TABLE

cur.execute("""
CREATE TABLE IF NOT EXISTS stop_allocations (
    allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id INTEGER NOT NULL,
    stop_name TEXT NOT NULL,
    fare REAL NOT NULL CHECK(fare >= 0),

    FOREIGN KEY (schedule_id)
    REFERENCES bus_schedules(schedule_id)
    ON DELETE CASCADE
)
""")

conn.commit()


# =====================================================
# 2. AUTOMATIC SAMPLE DATA INSERTION
# =====================================================

cur.execute("""
SELECT
    (SELECT COUNT(*) FROM depots) +
    (SELECT COUNT(*) FROM bus_schedules) +
    (SELECT COUNT(*) FROM stop_allocations)
""")

total_records = cur.fetchone()[0]


if total_records == 0:

    today = date.today().isoformat()

    # Insert sample depots

    depots = [
        ("Yeshwanthpur Depot", "yeshwanthpur@gmail.com"),
        ("Majestic Depot", "majestic@gmail.com"),
        ("Vijayanagar Depot", "vijayanagar@gmail.com")
    ]

    cur.executemany("""
    INSERT INTO depots (depot_name, manager_email)
    VALUES (?, ?)
    """, depots)


    # Insert sample bus schedules

    schedules = [
        (1, "Route 42", today),
        (1, "Route 15", today),
        (2, "Route 10", today),
        (3, "Route 25", today)
    ]

    cur.executemany("""
    INSERT INTO bus_schedules
    (depot_id, route_name, schedule_date)
    VALUES (?, ?, ?)
    """, schedules)


    # Insert sample stop allocations

    allocations = [
        (1, "Majestic", 25),
        (1, "Malleshwaram", 15),
        (2, "Yeshwanthpur", 20),
        (3, "City Market", 30),
        (4, "Vijayanagar", 20)
    ]

    cur.executemany("""
    INSERT INTO stop_allocations
    (schedule_id, stop_name, fare)
    VALUES (?, ?, ?)
    """, allocations)

    conn.commit()

    print("Sample data inserted successfully!")

else:
    print("Database already contains records.")


# =====================================================
# 3. CREATE MAIN TKINTER WINDOW
# =====================================================

root = tk.Tk()

root.title("Bus Depot & Schedule Management Dashboard")
root.geometry("1150x750")
root.configure(bg="#EAF2F8")


# MAIN HEADING

heading = tk.Label(
    root,
    text="BUS DEPOT & SCHEDULE MANAGEMENT",
    font=("Arial", 20, "bold"),
    bg="#17365D",
    fg="white",
    pady=15
)

heading.pack(fill="x")


# =====================================================
# 4. INSERT PANEL
# =====================================================

insert_frame = tk.LabelFrame(
    root,
    text="Insert New Record",
    font=("Arial", 12, "bold"),
    bg="#EAF2F8",
    padx=15,
    pady=10
)

insert_frame.pack(fill="x", padx=15, pady=10)


# INPUT VARIABLES

depot_var = tk.StringVar()
email_var = tk.StringVar()
route_var = tk.StringVar()
stop_var = tk.StringVar()
fare_var = tk.StringVar()


# INPUT FIELDS

labels = [
    "Depot Name:",
    "Manager Email:",
    "Route Name:",
    "Stop Name:",
    "Fare Value:"
]

variables = [
    depot_var,
    email_var,
    route_var,
    stop_var,
    fare_var
]

for i, (label, variable) in enumerate(zip(labels, variables)):

    tk.Label(
        insert_frame,
        text=label,
        font=("Arial", 10),
        bg="#EAF2F8"
    ).grid(row=i, column=0, padx=10, pady=5, sticky="w")

    tk.Entry(
        insert_frame,
        textvariable=variable,
        width=35
    ).grid(row=i, column=1, padx=10, pady=5)


# =====================================================
# 5. INSERT RECORD FUNCTION
# =====================================================

def add_record():

    depot = depot_var.get().strip()
    email = email_var.get().strip()
    route = route_var.get().strip()
    stop = stop_var.get().strip()
    fare = fare_var.get().strip()


    # CHECK EMPTY FIELDS

    if not all([depot, email, route, stop, fare]):

        messagebox.showerror(
            "Input Error",
            "All fields are required!"
        )

        return


    # VALIDATE EMAIL

    if "@" not in email or "." not in email.split("@")[-1]:

        messagebox.showerror(
            "Input Error",
            "Enter a valid email address!"
        )

        return


    # VALIDATE FARE

    try:
        fare_value = float(fare)

        if fare_value < 0:
            raise ValueError

    except ValueError:

        messagebox.showerror(
            "Input Error",
            "Fare must be a non-negative number!"
        )

        return


    try:

        # CHECK WHETHER DEPOT ALREADY EXISTS

        cur.execute("""
        SELECT depot_id
        FROM depots
        WHERE depot_name = ?
        """, (depot,))

        result = cur.fetchone()


        if result:

            depot_id = result[0]

        else:

            # CREATE NEW DEPOT

            cur.execute("""
            INSERT INTO depots
            (depot_name, manager_email)
            VALUES (?, ?)
            """, (depot, email))

            depot_id = cur.lastrowid


        # CREATE BUS SCHEDULE

        cur.execute("""
        INSERT INTO bus_schedules
        (depot_id, route_name, schedule_date)
        VALUES (?, ?, ?)
        """, (depot_id, route, date.today().isoformat()))

        schedule_id = cur.lastrowid


        # CREATE STOP ALLOCATION

        cur.execute("""
        INSERT INTO stop_allocations
        (schedule_id, stop_name, fare)
        VALUES (?, ?, ?)
        """, (schedule_id, stop, fare_value))


        conn.commit()


        # CLEAR INPUT FIELDS

        for variable in variables:
            variable.set("")


        # REFRESH ALL DISPLAYS

        refresh_all()


        messagebox.showinfo(
            "Success",
            "Record added successfully!"
        )


    except sqlite3.Error as e:

        conn.rollback()

        messagebox.showerror(
            "Database Error",
            str(e)
        )


# ADD RECORD BUTTON

tk.Button(
    insert_frame,
    text="ADD RECORD",
    command=add_record,
    bg="#2874A6",
    fg="white",
    font=("Arial", 10, "bold"),
    width=20
).grid(row=5, column=1, pady=10)


# =====================================================
# 6. DELETE PANEL
# =====================================================

delete_frame = tk.LabelFrame(
    root,
    text="Delete Records",
    font=("Arial", 12, "bold"),
    bg="#EAF2F8",
    padx=15,
    pady=10
)

delete_frame.pack(fill="x", padx=15, pady=10)


# DROPDOWN VARIABLES

delete_depot_var = tk.StringVar()
delete_schedule_var = tk.StringVar()
delete_allocation_var = tk.StringVar()


# DEPOT DROPDOWN

tk.Label(
    delete_frame,
    text="Select Depot:",
    bg="#EAF2F8"
).grid(row=0, column=0, padx=10, pady=5)

depot_dropdown = ttk.Combobox(
    delete_frame,
    textvariable=delete_depot_var,
    state="readonly",
    width=30
)

depot_dropdown.grid(row=0, column=1, padx=10, pady=5)


# SCHEDULE DROPDOWN

tk.Label(
    delete_frame,
    text="Select Bus Schedule:",
    bg="#EAF2F8"
).grid(row=1, column=0, padx=10, pady=5)

schedule_dropdown = ttk.Combobox(
    delete_frame,
    textvariable=delete_schedule_var,
    state="readonly",
    width=30
)

schedule_dropdown.grid(row=1, column=1, padx=10, pady=5)


# ALLOCATION DROPDOWN

tk.Label(
    delete_frame,
    text="Select Stop Allocation:",
    bg="#EAF2F8"
).grid(row=2, column=0, padx=10, pady=5)

allocation_dropdown = ttk.Combobox(
    delete_frame,
    textvariable=delete_allocation_var,
    state="readonly",
    width=30
)

allocation_dropdown.grid(row=2, column=1, padx=10, pady=5)


# =====================================================
# 7. REFRESH DROPDOWN VALUES
# =====================================================

def refresh_dropdowns():

    # DEPOTS

    cur.execute("""
    SELECT depot_id, depot_name
    FROM depots
    ORDER BY depot_id
    """)

    depot_values = [
        f"{row[0]} - {row[1]}"
        for row in cur.fetchall()
    ]

    depot_dropdown["values"] = depot_values

    delete_depot_var.set("")


    # BUS SCHEDULES

    cur.execute("""
    SELECT schedule_id, route_name
    FROM bus_schedules
    ORDER BY schedule_id
    """)

    schedule_values = [
        f"{row[0]} - {row[1]}"
        for row in cur.fetchall()
    ]

    schedule_dropdown["values"] = schedule_values

    delete_schedule_var.set("")


    # STOP ALLOCATIONS

    cur.execute("""
    SELECT allocation_id, stop_name
    FROM stop_allocations
    ORDER BY allocation_id
    """)

    allocation_values = [
        f"{row[0]} - {row[1]}"
        for row in cur.fetchall()
    ]

    allocation_dropdown["values"] = allocation_values

    delete_allocation_var.set("")


# =====================================================
# 8. DELETE RECORD FUNCTION
# =====================================================

def delete_record():

    depot = delete_depot_var.get()
    schedule = delete_schedule_var.get()
    allocation = delete_allocation_var.get()


    # CHECK WHETHER A RECORD IS SELECTED

    selected = sum(bool(x) for x in [depot, schedule, allocation])

    if selected != 1:

        messagebox.showwarning(
            "Selection Error",
            "Select exactly one record to delete!"
        )

        return


    try:

        if depot:

            record_id = int(depot.split(" - ")[0])

            action = "Depot"

            cur.execute("""
            DELETE FROM depots
            WHERE depot_id = ?
            """, (record_id,))


        elif schedule:

            record_id = int(schedule.split(" - ")[0])

            action = "Bus Schedule"

            cur.execute("""
            DELETE FROM bus_schedules
            WHERE schedule_id = ?
            """, (record_id,))


        else:

            record_id = int(allocation.split(" - ")[0])

            action = "Stop Allocation"

            cur.execute("""
            DELETE FROM stop_allocations
            WHERE allocation_id = ?
            """, (record_id,))


        if cur.rowcount == 0:

            conn.rollback()

            messagebox.showwarning(
                "Not Found",
                "Selected record no longer exists."
            )

            refresh_all()

            return


        conn.commit()

        refresh_all()


        messagebox.showinfo(
            "Success",
            action + " deleted successfully!"
        )


    except sqlite3.Error as e:

        conn.rollback()

        messagebox.showerror(
            "Database Error",
            str(e)
        )


# DELETE BUTTON

tk.Button(
    delete_frame,
    text="DELETE SELECTED",
    command=delete_record,
    bg="#C0392B",
    fg="white",
    font=("Arial", 10, "bold"),
    width=20
).grid(row=3, column=1, pady=10)


# =====================================================
# 9. TAB DISPLAY PANEL
# =====================================================

display_frame = tk.LabelFrame(
    root,
    text="Database Records",
    font=("Arial", 12, "bold"),
    bg="#EAF2F8",
    padx=10,
    pady=10
)

display_frame.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=10
)


# CREATE NOTEBOOK

notebook = ttk.Notebook(display_frame)

notebook.pack(fill="both", expand=True)


# CREATE FOUR TABS

tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)
tab4 = ttk.Frame(notebook)


notebook.add(tab1, text="Combined View")
notebook.add(tab2, text="Depots")
notebook.add(tab3, text="Bus Schedules")
notebook.add(tab4, text="Stop Allocations")


# =====================================================
# 10. CREATE TABLE DISPLAY FUNCTION
# =====================================================

def create_table(parent, columns):

    frame = ttk.Frame(parent)

    frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings"
    )


    for column in columns:

        tree.heading(
            column,
            text=column.replace("_", " ").title()
        )

        tree.column(
            column,
            width=140,
            anchor="center"
        )


    # SCROLLBAR

    scrollbar = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(
        yscrollcommand=scrollbar.set
    )

    tree.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    return tree


# CREATE FOUR TABLE VIEWS

combined_tree = create_table(
    tab1,
    (
        "Schedule_ID",
        "Depot_Name",
        "Route_Name",
        "Schedule_Date",
        "Stop_Name",
        "Fare"
    )
)


depot_tree = create_table(
    tab2,
    (
        "Depot_ID",
        "Depot_Name",
        "Manager_Email"
    )
)


schedule_tree = create_table(
    tab3,
    (
        "Schedule_ID",
        "Depot_ID",
        "Route_Name",
        "Schedule_Date"
    )
)


allocation_tree = create_table(
    tab4,
    (
        "Allocation_ID",
        "Schedule_ID",
        "Stop_Name",
        "Fare"
    )
)


# =====================================================
# 11. REFRESH TABLE DATA
# =====================================================

def refresh_tree(tree, query):

    # REMOVE OLD RECORDS

    for item in tree.get_children():

        tree.delete(item)


    # FETCH NEW RECORDS

    cur.execute(query)

    records = cur.fetchall()


    # INSERT UPDATED RECORDS

    for record in records:

        tree.insert(
            "",
            tk.END,
            values=record
        )


# =====================================================
# 12. REFRESH ALL FOUR TABS
# =====================================================

def refresh_all():

    # TAB 1: COMBINED JOIN VIEW

    refresh_tree(
        combined_tree,
        """
        SELECT
            bs.schedule_id,
            d.depot_name,
            bs.route_name,
            bs.schedule_date,
            sa.stop_name,
            sa.fare

        FROM bus_schedules bs

        JOIN depots d
        ON bs.depot_id = d.depot_id

        JOIN stop_allocations sa
        ON bs.schedule_id = sa.schedule_id

        ORDER BY bs.schedule_id
        """
    )


    # TAB 2: DEPOTS

    refresh_tree(
        depot_tree,
        """
        SELECT * FROM depots
        ORDER BY depot_id
        """
    )


    # TAB 3: BUS SCHEDULES

    refresh_tree(
        schedule_tree,
        """
        SELECT * FROM bus_schedules
        ORDER BY schedule_id
        """
    )


    # TAB 4: STOP ALLOCATIONS

    refresh_tree(
        allocation_tree,
        """
        SELECT * FROM stop_allocations
        ORDER BY allocation_id
        """
    )


    # UPDATE DELETE DROPDOWNS

    refresh_dropdowns()


# =====================================================
# 13. INITIAL REFRESH
# =====================================================

refresh_all()


# =====================================================
# 14. RUN APPLICATION
# =====================================================

root.mainloop()


# CLOSE DATABASE CONNECTION

conn.close()
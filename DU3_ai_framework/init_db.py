import sqlite3

def create_sample_db():
    conn = sqlite3.connect("company_data.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT NOT NULL,
        project_type TEXT NOT NULL,
        budget_czk INTEGER NOT NULL,
        status TEXT NOT NULL
    )
    """)

    sample_data = [
        ("Alza.cz", "Data Warehouse Migration", 450000, "Completed"),
        ("Rohlík.cz", "AI Customer Support Agent", 320000, "In Progress"),
        ("Škoda Auto", "Predictive Maintenance Pipeline", 890000, "In Progress"),
        ("Místní Pekárna s.r.o.", "n8n Invoice OCR Automation", 45000, "Completed"),
    ]

    cursor.executemany(
        "INSERT INTO projects (client_name, project_type, budget_czk, status) VALUES (?, ?, ?, ?)",
        sample_data
    )
    conn.commit()
    conn.close()
    print("Databáze company_data.db byla úspěšně inicializována.")

if __name__ == "__main__":
    create_sample_db()
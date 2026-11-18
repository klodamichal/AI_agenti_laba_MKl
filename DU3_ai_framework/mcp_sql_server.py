import sqlite3
from mcp.server.fastmcp import FastMCP

# Inicializace MCP serveru
mcp = FastMCP("CompanySQLServer")
DB_PATH = "company_data.db"

@mcp.tool()
def list_tables() -> str:
    """Vrátí seznam všech tabulek v firemní databázi a jejich schéma."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return "\n".join([f"Tabulka: {t[0]}\nSchéma: {t[1]}" for t in tables])

@mcp.tool()
def run_readonly_sql(query: str) -> str:
    """
    Spustí SELECT SQL dotaz nad databází company_data.db a vrátí výsledky.
    Povoleny jsou pouze dotazy začínající klíčovým slovem SELECT.
    """
    if not query.strip().upper().startswith("SELECT"):
        return "Chyba: Z bezpečnostních důvodů jsou povoleny pouze SELECT dotazy."
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "Dotaz nevrátil žádné výsledky."
        
        result = [f"Sloupce: {', '.join(columns)}"]
        for row in rows:
            result.append(str(row))
        return "\n".join(result)
    except Exception as e:
        return f"Chyba při vykonávání SQL: {str(e)}"

if __name__ == "__main__":
    # Spustí server přes standardní vstup/výstup (stdio)
    mcp.run(transport="stdio")
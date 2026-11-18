# AI Data Analyst Agent (LangGraph + MCP)

Domácí úkol zaměřený na návrh a implementaci AI agenta využívajícího standardizovaný **Model Context Protocol (MCP)** pro oddělení nástrojů od samotného agentního frameworku.

## Architektura řešení

* **Agentní architektura:** ReAct (Reason + Act)
* **Framework:** LangGraph / LangChain (`langchain.agents.create_agent`)
* **LLM:** OpenAI (`gpt-4o-mini`)
* **Protokol nástrojů:** MCP (Model Context Protocol) přes `FastMCP` (`stdio` transport) a `langchain-mcp-adapters`
* **Nástroje (MCP Server `mcp_sql_server.py`):**
  * `list_tables` – inspekce schématu databáze SQLite
  * `run_readonly_sql` – bezpečné spouštění `SELECT` dotazů nad firemní databází

## Struktura projektu

* `init_db.py` – inicializační skript pro vytvoření testovací SQLite databáze (`company_data.db`)
* `mcp_sql_server.py` – samostatný MCP server vystavující databázové nástroje
* `agent.py` – klient a ReAct agent napojený na MCP server
* `requirements.txt` – seznam Python závislostí
* `.env.example` – šablona pro konfiguraci API klíče

## Postup spuštění

1. **Vytvoření a aktivace virtuálního prostředí (doporučen Python 3.12+):**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\Activate.ps1
   # Linux/macOS:
   source venv/bin/activate
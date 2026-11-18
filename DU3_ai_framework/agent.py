import asyncio
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

async def main():
    # 1. Definice MCP serverů (sys.executable zajistí spuštění z aktivního venv)
    mcp_servers = {
        "company_sql": {
            "command": sys.executable,
            "args": ["mcp_sql_server.py"],
            "transport": "stdio",
        }
    }

    # 2. Inicializace OpenAI LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # 3. Připojení k MCP serveru a dynamické načtení nástrojů
    client = MultiServerMCPClient(mcp_servers)
    tools = await client.get_tools()
    print(f"Načtené MCP nástroje: {[t.name for t in tools]}\n")

    # 4. Vytvoření ReAct agenta
    system_prompt = (
        "Jsi precizní datový analytik. Na dotazy ohledně firemních projektů "
        "vždy nejprve zkontroluj schéma databáze a poté sestav přesný SQL dotaz."
    )
    agent = create_agent(llm, tools, system_prompt=system_prompt)

    # 5. Testovací dotaz
    user_query = (
        "Jaký je celkový rozpočet našich projektů, které jsou aktuálně 'In Progress', "
        "a pro jakého klienta děláme nejdražší projekt?"
    )
    
    print(f"Dotaz uživatele: {user_query}\n" + "-" * 50)
    
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": user_query}]}
    )

    # Výpis finální odpovědi
    final_message = response["messages"][-1].content
    print("\nOdpověď agenta:\n", final_message)

if __name__ == "__main__":
    asyncio.run(main())
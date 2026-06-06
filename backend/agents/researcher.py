from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, ToolMessage
from tools.web_search import web_search
from tools.scraper import scrape_url
from agents.graph import ResearchState
from core.config import settings

tools = [web_search, scrape_url]

llm = ChatGroq(
    api_key = settings.groq_api_key,
    model = "llama-3.1-8b-instant"
).bind_tools(tools)

tool_map = {t.name: t for t in tools}

async def researcher_node(state: ResearchState) -> dict:
    all_docs = []

    for task in state["tasks"]:
        print(f"\n[RESEARCHER] Working on: {task['task']}")

        messages = [
            HumanMessage(content=f"""You are a research assistant. Investigate this task thoroughly.
            Use web_search to find information, then scrape_url to read promising pages.
            Make 2-4 tool calls, then summarize your findings.
            
            Task: {task['task']}""")
        ]

        max_iterations = 6
        for i in range(max_iterations):
            try:
                response = await llm.ainvoke(messages)
            except Exception as e:
                print(f"  [ERROR] LLM call failed: {e}")
                response = type("FakeResponse", (), {"content": "Research could not be completed for this task.", "tool_calls": []})()
                break

            messages.append(response)

            if not response.tool_calls:
                print(f"  [DONE] Finished after {i + 1} iterations")
                break

            for tc in response.tool_calls:
                print(f"  [TOOL] Calling {tc['name']}({tc['args']})")
                try:
                    tool_fn = tool_map[tc["name"]]
                    result = tool_fn.invoke(tc["args"])
                except Exception as e:
                    result = f"Tool call failed: {e}"

                messages.append(ToolMessage(
                    content=str(result),
                    tool_call_id=tc["id"]
                ))

        all_docs.append({
            "task": task["task"],
            "content": response.content
        })

    return {"raw_docs": all_docs}
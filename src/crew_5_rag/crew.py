from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, SeleniumScrapingTool, ScrapeWebsiteTool
from .tools.custom_tool import StoreReportTool, RAGRetrievalTool, make_store_callback
import os

# ── LLM with retry + timeout — survives 503 overload bursts ──────────────────
# num_retries: LiteLLM will retry up to 10x with exponential backoff on 429/503
# timeout:     give the model 120s to respond before giving up
_model_name = os.environ.get("MODEL", "groq/openai/gpt-oss-120b")
_api_key = os.environ.get("GROQ_API_KEY") if "groq" in _model_name else (
    os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY")
)

_llm = LLM(
    model=_model_name,
    api_key=_api_key,
    temperature=0,
    num_retries=10,
    timeout=120,
)

search_tool          = SerperDevTool()
store_tool           = StoreReportTool()
rag_tool             = RAGRetrievalTool()
web_scrape_tool      = ScrapeWebsiteTool()
web_scrape_selenium  = SeleniumScrapingTool()

tool_kit = [search_tool, store_tool, rag_tool, web_scrape_tool, web_scrape_selenium]

@CrewBase
class MarketResearchCrew:

    agents_config = "config/agents.yaml"
    tasks_config  = "config/tasks.yaml"

    # ── Agents ────────────────────────────────────────────────────────────────

    @agent
    def market_research_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["market_research_analyst"],  # type: ignore[index]
            llm=_llm,
            tools=tool_kit,
            verbose=True,
            max_retry_limit=5,
        )

    @agent
    def competitor_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["competitor_researcher"],  # type: ignore[index]
            llm=_llm,
            tools=tool_kit,
            verbose=True,
            max_retry_limit=5,
        )

    @agent
    def customer_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["customer_researcher"],  # type: ignore[index]
            llm=_llm,
            tools=tool_kit,
            verbose=True,
            max_retry_limit=5,
        )

    @agent
    def product_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["product_researcher"],  # type: ignore[index]
            llm=_llm,
            tools=tool_kit,
            verbose=True,
            max_retry_limit=5,
        )

    @agent
    def business_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["business_analyst"],  # type: ignore[index]
            llm=_llm,
            tools=[rag_tool],
            verbose=True,
            max_retry_limit=5,
        )

    # ── Tasks — callback here, NOT on agent ───────────────────────────────────

    @task
    def market_research_task(self) -> Task:
        return Task(
            config=self.tasks_config["market_research_task"],
            callback=make_store_callback("market_research_analyst")
        )

    @task
    def competitor_research_task(self) -> Task:
        return Task(
            config=self.tasks_config["competitor_research_task"],
            callback=make_store_callback("competitor_researcher")
        )

    @task
    def customer_research_task(self) -> Task:
        return Task(
            config=self.tasks_config["customer_research_task"],
            callback=make_store_callback("customer_researcher")
        )

    @task
    def product_research_task(self) -> Task:
        return Task(
            config=self.tasks_config["product_research_task"],
            callback=make_store_callback("product_researcher")
        )

    @task
    def business_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["business_analysis_task"],
            output_file="final_report_2.md",
        )

    # ── Crew ──────────────────────────────────────────────────────────────────

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_rpm=3,   # Conservative pacing — avoids hammering overloaded 503 model
        )
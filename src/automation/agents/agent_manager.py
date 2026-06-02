from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from .email.pydantic_models import ResumeSelection, EmailDraft


class AgentManager:
    """Manages all agents for the session lifecycle."""

    def __init__(self, model_name: str = 'gemini-2.5-flash'):
        self.model_name = model_name
        self.model = GeminiModel(model_name)
        self._resume_selector_agent = None
        self._email_personalization_agent = None
        self._db_query_agent = None

    @property
    def resume_selector_agent(self):
        if self._resume_selector_agent is None:
            self._resume_selector_agent = Agent(
                model=self.model,
                output_type=ResumeSelection,
                system_prompt='You are a resume selection assistant. Your task is to analyze company information and select the most appropriate resume type that maximizes the chances of a positive response to a cold email.',
                tools=[]
            )
        return self._resume_selector_agent

    @property
    def email_personalization_agent(self):
        if self._email_personalization_agent is None:
            self._email_personalization_agent = Agent(
                model=self.model,
                output_type=EmailDraft,
                system_prompt='You are a cold email personalization assistant. Your task is to craft personalized, professional cold emails for internship opportunities that maximize response rates while maintaining authenticity and showcasing relevant experience.',
                tools=[]
            )
        return self._email_personalization_agent

    @property
    def db_query_agent(self):
        if self._db_query_agent is None:
            self._db_query_agent = Agent(
                model=self.model,
                system_prompt='',
                tools=[]
            )
        return self._db_query_agent



    #######******* SCRAPER AGENTS *******#######

    @property # decides final verdict too
    def scraper_orchestrator_agent(self): 
        if self._db_query_agent is None:
            self._db_query_agent = Agent(
                model=self.model,
                system_prompt='',
                tools=[] # provide function calls to fire sub-agents
            )
        return self._db_query_agent
        
    @property 
    def ebay_agent(self): 
        if self._db_query_agent is None:
            self._db_query_agent = Agent(
                model=self.model,
                system_prompt='',
                tools=[]
            )
        return self._db_query_agent

    #### TODO: LATER, FOCUS ON EBAY AGENT FOR WORKING MVP
    @property 
    def grailed_agent(self): 
        if self._db_query_agent is None:
            self._db_query_agent = Agent(
                model=self.model,
                system_prompt='',
                tools=[]
            )
        return self._db_query_agent
    

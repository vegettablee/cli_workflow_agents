# Current Requirement in Progress: Draft Workflow Agent Implementation 

Workflow classes/functions: 

Class: DraftEmailWorkflow 
Responsibility: Contains all of the relevant functions/services to complete the email draft workflow
Dependencies: Needs data inside of database first 

class DraftEmailWorkflow: 

  def query_database() -> tuple (list, list): # this only gets run once for a batch of emails 
    # get all of the emails that can be sent(use queries.py) 
    # use these emails and run find_recruiter_emails(), emails returned are recruiter emails, and those not part of the original
    -- COMPLETED -- 
  
  def find_valid_emails(emails : list) -> tuple(list, list, list, list): 
    # takes a list of emails to check, the first element in the tuple contains the company emails, and the second list contains the company ids from the actual email, the third list is recruiter emails, the idea is that when checking if an email exists inside of the recruiter_email table, since it is a binary operation, these can be easily separated, the fourth list is the company_ids tied to the recruiter emails. need to keep track of the ids for context injection later for email personalization and other purposes
    -- COMPLETED -- 
  
  def get_company_context(company_email : str, company_id : int) -> dict:
    # use the company_id to query the company table and then pull the relevant data 
    # return context where context is a dictionary with the same fields as the COMPANY entity in the DDL script 
    -- COMPLETED -- 

  def get_recruiter_context(recruiter_email : str, company_id : int) -> dict: 
    # use the company_id to query the company table then pull relevant data 
    -- COMPLETED -- 

# -- Current focus on implementations: 

class AgentManager: 
-- Purpose: lazy initializes different agents/tools when called and returns them, or if they already exist just return 
-- Currently, this just contains the different placeholder agent initializations.

Orchestrator class: 
  def run_draft_email_workflow(self, email_count : int):
  - right now, the orchestrator is intializing the agent manager class, which contains the the agents/tools that can be run, and 
    are passed down to run_draft_agent inside of /agents/email_personalization.py
  
email_personalization.py: this file is specifically for handling the generation of a personalized email given context, includes multiple helper functions, and can handle both non-recruiters and recruiters 


def run_draft_agent(context : dict, agent : any, resume_type : str, is_recruiter : bool) -> dict: 
          Does: Runs the actual draft agent to generate the personalized email, based on the type of the resume, right to the right path, 
                - all of the resumes are inside of src/resumes, and the first path will be src/resumes/fullstack.pdf 
                - it makes sense to just have this function responsible for making sure the paths are right without bloating the generate_instructions function
                - runs generate_instructions, passing down context and if it is a recruiter 
          Given: context is a dict that contains the company and personal context(name, year, grad date), if is_recruiter is true,
                  - then, context includes recruiter context as well. these are modeled directly after SQLAlchemy models in models.py, with the exception of the personal context
                  - agent is an agent lazy initialized from agent_manager.py
                  - resume_type is one of four types, for now it defaults to "fullstack" for the sake of MVP 
          
          Returns: returns a dict of necessary fields of an email that can be supplemented directly in an Gmail API call for formatting later, this dict contains 
                  - contains three keys mapped to strings: to, subject, body 
          Errors: For now, add a placeholder where a logging system using python's module would be placed, but leave it blank
                  - print the error 

def generate_instructions(context : dict, resume_type : str, is_recruiter : bool) -> dict: 
          """
          Does: generates the valid fields in order to be reviewed later, and can be sent later via GMAIL api 
          Given: context passed down from run_draft_agent 
          Returns: a dict of necessary fields of an email that can be supplemented directly in an Gmail API call for formatting later, this dict contains 
                  - contains three keys mapped to strings: to, subject, body 
          Errors: For now, add a placeholder where a logging system using python's module would be placed, but leave it blank 
                  - print the error 






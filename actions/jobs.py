from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from db.database import HRDatabase

# Initialize the HR database connection
hr_db = HRDatabase()

class ActionSearchJobs(Action):
    def name(self) -> Text:
        return "action_search_jobs"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        job_title = tracker.get_slot("job_title")
        job_location = tracker.get_slot("job_location")
        job_department = tracker.get_slot("job_department")
        
        # Search for matching jobs
        jobs = hr_db.search_jobs(job_title, job_department, job_location)
        
        if jobs:
            response = "I found the following job openings that match your criteria:\n\n"
            for job in jobs:
                response += f"**{job['title']}** - {job['department']}\n"
                response += f"Location: {job['location']}\n"
                response += f"Requirements: {job['requirements']}\n"
                response += f"Application Deadline: {job['deadline']}\n\n"
                
            response += "To apply, please visit careers.techcorp.com and search for these positions."
            dispatcher.utter_message(text=response)
        else:
            dispatcher.utter_message(text="I couldn't find any job openings matching your criteria. Try broadening your search parameters or check back later as new positions are posted regularly.")
            
        return []

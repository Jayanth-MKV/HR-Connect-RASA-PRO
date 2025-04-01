from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from db.database import HRDatabase

class ActionIdentifyUserType(Action):
    def name(self) -> Text:
        return "action_identify_user_type"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id")
        employee_info = HRDatabase().get_employee_info(employee_id)
        
        is_new_employee = employee_info.get("is_new_employee", False)
        
        # Return the identified user type
        return [SlotSet("is_new_employee", is_new_employee)]

class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Initialize session and set any default values
        employee_id = tracker.get_slot("employee_id")
        employee_info = HRDatabase().get_employee_info(employee_id)

        # Optional: Send a welcome message
        # dispatcher.utter_message(text="Welcome to HR Connect! 😊")
        
        return [
            SlotSet("user_name", employee_info.get("name")),
            SlotSet("department", employee_info.get("department")),
            SlotSet("manager", employee_info.get("manager"))
        ]

class ActionGreetUser(Action):
    def name(self) -> Text:
        return "action_greet_user"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_name = tracker.get_slot("user_name")
        is_new_employee = tracker.get_slot("is_new_employee")
        
        if is_new_employee:
            dispatcher.utter_message(template="utter_welcome_new_employee", user_name=user_name)
        else:
            dispatcher.utter_message(template="utter_welcome_existing_employee", user_name=user_name)
            
        return []

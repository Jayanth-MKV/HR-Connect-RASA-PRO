from typing import Any, Text, Dict, List
from datetime import datetime
import re
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from db.database import HRDatabase

class ValidateLeaveAction(Action):
    def name(self) -> Text:
        return "validate_leave_action"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        leave_action = tracker.get_slot("leave_action")
        valid_actions = ["check_balance", "request", "cancel", "status"]
        
        if leave_action not in valid_actions:
            return {"leave_action": None}
        return {"leave_action": leave_action}

class ValidateLeaveType(Action):
    def name(self) -> Text:
        return "validate_leave_type"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        leave_type = tracker.get_slot("leave_type")
        valid_types = ["annual", "sick", "personal", "other"]
        
        if leave_type not in valid_types:
            return {"leave_type": None}
        return {"leave_type": leave_type}

class ValidateDateFormat(Action):
    def name(self) -> Text:
        return "validate_date_format"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        date_string = tracker.get_slot(tracker.active_loop.get("name"))
        date_format = tracker.get_slot("format") or "%Y-%m-%d"
        
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        
        if not date_pattern.match(date_string):
            return {tracker.active_loop.get("name"): None}
        
        try:
            datetime.strptime(date_string, date_format)
            return {tracker.active_loop.get("name"): date_string}
        except ValueError:
            return {tracker.active_loop.get("name"): None}

class ValidateDateOrder(Action):
    def name(self) -> Text:
        return "validate_date_order"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        start_date = tracker.get_slot("leave_start_date")
        end_date = tracker.get_slot("leave_end_date")
        
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            if end < start:
                return {"leave_end_date": None}
            return {"leave_end_date": end_date}
        except (ValueError, TypeError):
            return {"leave_end_date": None}

class ValidateLeaveId(Action):
    def name(self) -> Text:
        return "validate_leave_id"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        leave_id = tracker.get_slot("leave_to_cancel")
        # Pattern for leave ID (e.g., LR202504010001)
        id_pattern = re.compile(r'^LR\d{12}$')
        
        if not id_pattern.match(leave_id):
            return {"leave_to_cancel": None}
        return {"leave_to_cancel": leave_id}

class ActionGetLeaveBalance(Action):
    def name(self) -> Text:
        return "action_get_leave_balance"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id")
        employee_info = HRDatabase().get_employee_info(employee_id)
        leave_balance = employee_info.get("leave_balance", {})
        
        # Format the leave balance message
        balance_message = f"Your current leave balance is:\n"
        balance_message += f"- Annual Leave: {leave_balance.get('annual', 0)} days\n"
        balance_message += f"- Sick Leave: {leave_balance.get('sick', 0)} days\n"
        balance_message += f"- Personal Leave: {leave_balance.get('personal', 0)} days"
        
        dispatcher.utter_message(text=balance_message)
        
        return [SlotSet("leave_balance", balance_message)]

class ActionSubmitLeaveRequest(Action):
    def name(self) -> Text:
        return "action_submit_leave_request"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id")
        leave_type = tracker.get_slot("leave_type")
        leave_start_date = tracker.get_slot("leave_start_date")
        leave_end_date = tracker.get_slot("leave_end_date")
        leave_reason = tracker.get_slot("leave_reason")
        
        # Submit leave request to database
        result = HRDatabase().submit_leave_request(
            employee_id, leave_type, leave_start_date, leave_end_date, leave_reason)
        
        leave_status = result.get("status", "unknown")
        
        return [SlotSet("leave_status", leave_status)]

class ActionGetPendingLeaves(Action):
    def name(self) -> Text:
        return "action_get_pending_leaves"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # In a real implementation, this would query pending leave requests
        # Mock data for demonstration
        pending_leaves = [
            {"id": "LR202504010001", "type": "annual", "dates": "2025-04-15 to 2025-04-20"},
            {"id": "LR202504010002", "type": "personal", "dates": "2025-05-01 to 2025-05-01"}
        ]
        
        if pending_leaves:
            message = "You have the following pending leave requests:\n"
            for i, leave in enumerate(pending_leaves, 1):
                message += f"{i}. {leave['type'].capitalize()} leave from {leave['dates']} (ID: {leave['id']})\n"
            
            message += "\nWhich leave would you like to cancel? (Please provide the ID)"
        else:
            message = "You don't have any pending leave requests that can be cancelled."
            
        dispatcher.utter_message(text=message)
        
        return []

class ActionCancelLeave(Action):
    def name(self) -> Text:
        return "action_cancel_leave"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        leave_to_cancel = tracker.get_slot("leave_to_cancel")
        
        # In a real implementation, this would update the leave status in the database
        # For now, we'll just assume it's successful
        
        return [SlotSet("leave_to_cancel", leave_to_cancel)]

class ActionGetLeaveStatus(Action):
    def name(self) -> Text:
        return "action_get_leave_status"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # In a real implementation, this would query the status of all leave requests
        # Mock data for demonstration
        leave_requests = [
            {"id": "LR202504010001", "type": "annual", "dates": "2025-04-15 to 2025-04-20", "status": "pending"},
            {"id": "LR202503250001", "type": "sick", "dates": "2025-03-26 to 2025-03-27", "status": "approved"},
            {"id": "LR202503010002", "type": "personal", "dates": "2025-03-15", "status": "rejected"}
        ]
        
        if leave_requests:
            message = "Here are your recent leave requests:\n"
            for leave in leave_requests:
                message += f"- {leave['type'].capitalize()} leave from {leave['dates']}: {leave['status'].upper()}\n"
        else:
            message = "You don't have any leave requests in the system."
            
        dispatcher.utter_message(text=message)
        
        return []

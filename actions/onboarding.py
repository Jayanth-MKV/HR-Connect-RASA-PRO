from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from db.database import HRDatabase

class ActionGetOnboardingStatus(Action):
    def name(self) -> Text:
        return "action_get_onboarding_status"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id") or "EMP001"  # Default to sample employee
        tasks = HRDatabase().get_onboarding_tasks(employee_id)
        
        if not tasks:
            return [SlotSet("onboarding_progress", "No onboarding tasks found.")]
        
        # Calculate progress percentage
        completed_tasks = sum(1 for task in tasks if task["status"] == "completed")
        total_tasks = len(tasks)
        progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        # Format task list
        task_list = ""
        for i, task in enumerate(tasks, 1):
            status_symbol = "✅" if task["status"] == "completed" else "⏳" if task["status"] == "pending" else "⬜"
            task_list += f"{i}. {status_symbol} {task['name']}\n"
        
        # Find the next task
        next_task = next((task["name"] for task in tasks if task["status"] != "completed"), "All tasks completed!")
        current_step = next((i+1 for i, task in enumerate(tasks) if task["status"] != "completed"), 0)
        
        return [
            SlotSet("onboarding_progress", task_list),
            SlotSet("onboarding_progress_percentage", progress_percentage),
            SlotSet("onboarding_next_task", next_task),
            SlotSet("current_onboarding_step", current_step)
        ]

class ActionUpdateOnboardingTask(Action):
    def name(self) -> Text:
        return "action_update_onboarding_task"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id") or "EMP001"
        current_step = tracker.get_slot("current_onboarding_step") or 1
        
        # Update the task in the database
        HRDatabase().update_task_status(employee_id, int(current_step) - 1, "completed")
        
        # Recalculate progress
        tasks = HRDatabase().get_onboarding_tasks(employee_id)
        completed_tasks = sum(1 for task in tasks if task["status"] == "completed")
        total_tasks = len(tasks)
        progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        dispatcher.utter_message(text=f"Great! I've marked '{tasks[int(current_step) - 1]['name']}' as completed. Your onboarding progress is now {progress_percentage:.0f}%.")
        
        return [SlotSet("onboarding_progress_percentage", progress_percentage)]

class ActionGetTeamInformation(Action):
    def name(self) -> Text:
        return "action_get_team_information"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id") or "EMP001"
        team_members = HRDatabase().get_team_information(employee_id)
        
        if not team_members:
            return [SlotSet("team_information", "No team information available.")]
        
        # Format team information
        team_info = ""
        for member in team_members:
            team_info += f"{member['name']} ({member['role']}), "
        
        team_info = team_info.rstrip(", ")
        
        return [SlotSet("team_information", team_info)]

class ActionGetPolicyList(Action):
    def name(self) -> Text:
        return "action_get_policy_list"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        policies = HRDatabase().get_policies()
        policy_list = ", ".join(policies.keys())
            
        return [SlotSet("policy_list", policy_list)]

class ActionAnswerPolicyQuestions(Action):
    def name(self) -> Text:
        return "action_answer_policy_questions"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        policy_questions = tracker.get_slot("policy_questions") or ""
        
        if not policy_questions or policy_questions.lower() == "no":
            dispatcher.utter_message(text="Great! Let me know if you have any questions in the future.")
            return []
        
        policy_answer = HRDatabase().get_policy_information(policy_questions)
        dispatcher.utter_message(text=f"About your question: {policy_answer}")
        
        return []

class ActionVerifyOnboardingCompletion(Action):
    def name(self) -> Text:
        return "action_verify_onboarding_completion"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id") or "EMP001"
        tasks = HRDatabase().get_onboarding_tasks(employee_id)
        
        all_completed = all(task["status"] == "completed" for task in tasks)
        
        if all_completed:
            return [SlotSet("onboarding_completed", True)]
        else:
            pending_tasks = [task["name"] for task in tasks if task["status"] != "completed"]
            pending_list = ", ".join(pending_tasks)
            
            dispatcher.utter_message(text=f"You're almost there! Please complete the following tasks to finish onboarding: {pending_list}")
            return [SlotSet("onboarding_completed", False)]

class ActionUpdateEmployeeStatus(Action):
    def name(self) -> Text:
        return "action_update_employee_status"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id") or "EMP001"
        HRDatabase().update_employee(employee_id, {"is_new_employee": False})
        
        return [SlotSet("is_new_employee", False)]

class ActionManageOnboardingSteps(Action):
    def name(self) -> Text:
        return "action_manage_onboarding_steps"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id") or "EMP001"
        current_step = tracker.get_slot("current_onboarding_step") or 0
        
        # Get the tasks from the database
        tasks = HRDatabase().get_onboarding_tasks(employee_id)
        
        # Determine which flow to link to based on the current step
        if current_step == 0 or current_step >= len(tasks):
            # Start from the beginning or if somehow beyond the end
            return [SlotSet("current_onboarding_step", 1)]
        
        # Otherwise, current step is already set correctly
        return []

class ActionProvideTrainingMaterials(Action):
    def name(self) -> Text:
        return "action_provide_training_materials"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="I've sent the training materials to your email. Please complete them at your earliest convenience.")
        
        return []

class ActionGuideBenefitsSelection(Action):
    def name(self) -> Text:
        return "action_guide_benefits_selection"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="Our company offers comprehensive health, dental, vision, and retirement benefits. Please visit the HR portal to make your selections.")
        
        return []

class ActionShowUserProfile(Action):
    def name(self) -> Text:
        return "action_show_user_profile"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id") or "EMP001"
        employee_info = HRDatabase().get_employee_info(employee_id)
        
        if not employee_info:
            dispatcher.utter_message(text="I couldn't find your profile information.")
            return [SlotSet("show_profile_requested", False)]
        
        name = tracker.get_slot("user_name") or employee_info.get("name", "Not provided")
        department = tracker.get_slot("department") or employee_info.get("department", "Not provided")
        manager = tracker.get_slot("manager") or employee_info.get("manager", "Not provided")
        progress = tracker.get_slot("onboarding_progress_percentage") or 0
        
        profile_text = f"""
Here's your current profile information:

Name: {name}
Department: {department}
Manager: {manager}

Onboarding progress: {progress}%
        """
        
        dispatcher.utter_message(text=profile_text)
        
        return [SlotSet("show_profile_requested", False)]

class ActionCheckProfileRequest(Action):
    def name(self) -> Text:
        return "action_check_profile_request"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Check if the user is asking to see their profile or progress
        last_message = tracker.latest_message.get("text", "").lower()
        profile_keywords = ["profile", "my details", "my information", "show my", "progress", "status"]
        
        show_profile = any(keyword in last_message for keyword in profile_keywords)
        
        return [SlotSet("show_profile_requested", show_profile)]

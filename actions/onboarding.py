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
        
        employee_id = tracker.get_slot("employee_id") or "EMP001"  # Default to first employee for testing
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
        next_task = next((task["name"] for task in tasks if task["status"] != "completed"), None)
        
        return [
            SlotSet("onboarding_progress", task_list),
            SlotSet("onboarding_progress_percentage", progress_percentage),
            SlotSet("onboarding_next_task", next_task)
        ]

class ActionUpdateOnboardingTask(Action):
    def name(self) -> Text:
        return "action_update_onboarding_task"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id") or "EMP001"
        tasks = HRDatabase().get_onboarding_tasks(employee_id)
        current_step = tracker.get_slot("current_onboarding_step") or 0
        
        if tasks and 0 <= int(current_step) < len(tasks):
            # Update the task at the current step to completed
            task_name = tasks[int(current_step)]["name"]
            
            # In a real implementation, this would update the database
            # For now, we'll just simulate updating progress
            current_progress = tracker.get_slot("onboarding_progress_percentage") or 0
            new_progress = min(current_progress + 12.5, 100)  # Assuming 8 tasks (100/8 = 12.5%)
            
            # Move to the next step
            next_step = min(int(current_step) + 1, len(tasks) - 1)
            
            dispatcher.utter_message(f"Great! I've marked '{task_name}' as completed.")
            
            return [
                SlotSet("onboarding_progress_percentage", new_progress),
                SlotSet("current_onboarding_step", next_step)
            ]
        
        return []

class ActionAssignBuddy(Action):
    def name(self) -> Text:
        return "action_assign_buddy"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # In a real implementation, this would assign an onboarding buddy
        department = tracker.get_slot("department")
        
        if department == "Engineering":
            buddy = "John Smith"
        elif department == "Marketing":
            buddy = "Emma Davis"
        elif department == "Sales":
            buddy = "Michael Wong"
        else:
            buddy = "Taylor Brown"
            
        dispatcher.utter_message(text=f"Great news! {buddy} has been assigned as your onboarding buddy. They'll reach out to you shortly to schedule a welcome meeting.")
        
        return []

class ActionNotifyTeam(Action):
    def name(self) -> Text:
        return "action_notify_team"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # In a real implementation, this would send notifications to team members
        user_name = tracker.get_slot("user_name")
        department = tracker.get_slot("department")
        
        dispatcher.utter_message(text=f"I've notified your team in the {department} department about your arrival. They're looking forward to meeting you!")
        
        return []

class ActionGetTeamInformation(Action):
    def name(self) -> Text:
        return "action_get_team_information"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id") or "EMP001"
        team_members = HRDatabase().get_team_information(employee_id)
        
        if not team_members:
            return []
        
        # Format team information
        team_info = ""
        for member in team_members:
            team_info += f"{member['name']} ({member['role']}), "
        
        team_info = team_info.rstrip(", ")
        
        return [SlotSet("team_information", team_info)]

class ActionGetRequiredTrainings(Action):
    def name(self) -> Text:
        return "action_get_required_trainings"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        department = tracker.get_slot("department")
        
        # In a real implementation, this would fetch trainings from a training system
        # Mock data based on department
        if department == "Engineering":
            trainings = "Code of Conduct (1 hour), IT Security (2 hours), Engineering Best Practices (3 hours)"
        elif department == "Marketing":
            trainings = "Code of Conduct (1 hour), Brand Guidelines (2 hours), Marketing Compliance (1 hour)"
        elif department == "Sales":
            trainings = "Code of Conduct (1 hour), Sales Techniques (3 hours), CRM Training (2 hours)"
        else:
            trainings = "Code of Conduct (1 hour), Company Orientation (2 hours)"
            
        return [SlotSet("required_trainings", trainings)]

class ActionScheduleTrainings(Action):
    def name(self) -> Text:
        return "action_schedule_trainings"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        training_preferences = tracker.get_slot("training_preferences")
        
        # In a real implementation, this would schedule trainings based on preferences
        dispatcher.utter_message(text=f"I've scheduled your training sessions based on your preferences: {training_preferences}. You'll receive calendar invites shortly.")
        
        return []

class ActionGetPolicyList(Action):
    def name(self) -> Text:
        return "action_get_policy_list"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # In a real implementation, this would fetch policy list from a document system
        policies = "Code of Conduct, Work from Home Policy, IT Security Policy, Travel Policy, Expense Policy"
            
        return [SlotSet("policy_list", policies)]

class ActionAnswerPolicyQuestions(Action):
    def name(self) -> Text:
        return "action_answer_policy_questions"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        policy_questions = tracker.get_slot("policy_questions")
        
        # In a real implementation, this would use a more sophisticated retrieval system
        policy_answer = HRDatabase().get_policy_information(policy_questions)
            
        dispatcher.utter_message(text=f"Regarding your question about policies: {policy_answer}")
        
        return []

class ActionVerifyOnboardingCompletion(Action):
    def name(self) -> Text:
        return "action_verify_onboarding_completion"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        progress_percentage = tracker.get_slot("onboarding_progress_percentage") or 0
        
        if progress_percentage >= 100:
            return [SlotSet("onboarding_completed", True)]
        else:
            dispatcher.utter_message(text=f"You have completed {progress_percentage}% of your onboarding tasks. Please complete all remaining tasks to finish the onboarding process.")
            return [SlotSet("onboarding_completed", False)]

class ActionUpdateEmployeeStatus(Action):
    def name(self) -> Text:
        return "action_update_employee_status"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # In a real implementation, this would update the employee status in the database
        
        return [SlotSet("is_new_employee", False)]
    
class ActionManageOnboardingSteps(Action):
    def name(self) -> Text:
        return "action_manage_onboarding_steps"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        steps = [
            "Complete personal information",
            "Set up company email",
            "Complete IT security training",
            "Review company policies",
            "Set up direct deposit",
            "Meet with team members",
            "Complete benefits enrollment",
            "Finish onboarding"
        ]
        
        current_step = tracker.get_slot("current_onboarding_step") or 0
        
        if current_step < len(steps):
            next_step = steps[int(current_step)]
        else:
            next_step = "All steps completed"
        
        return [
            SlotSet("onboarding_next_task", next_step),
            SlotSet("current_onboarding_step", current_step)
        ]

class ActionCollectPersonalInfo(Action):
    def name(self) -> Text:
        return "action_collect_personal_info"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_name = tracker.get_slot("user_name")
        department = tracker.get_slot("department")
        manager = tracker.get_slot("manager")
        
        # In a real implementation, this would save the information to a database
        
        dispatcher.utter_message(text=f"Thank you, {user_name}! I've recorded that you'll be joining the {department} department under {manager}.")
        
        return [SlotSet("employee_id", "EMP001")]  # Assign a default employee ID for testing

class ActionSetupCompanyEmail(Action):
    def name(self) -> Text:
        return "action_setup_company_email"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_name = tracker.get_slot("user_name") or "New Employee"
        
        # In a real implementation, this would integrate with email systems
        
        dispatcher.utter_message(text=f"I've verified your company email is now active. Your email address is {user_name.lower().replace(' ', '.')}@techcorp.com")
        
        return []

class ActionProvideTrainingMaterials(Action):
    def name(self) -> Text:
        return "action_provide_training_materials"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # In a real implementation, this would provide links to training materials
        
        dispatcher.utter_message(text="I've sent you an email with links to all required security training materials. Please complete them at your earliest convenience.")
        
        return []

class ActionVerifyTrainingCompletion(Action):
    def name(self) -> Text:
        return "action_verify_training_completion"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # In a real implementation, this would check training completion status
        
        dispatcher.utter_message(text="I've confirmed that you've completed all required security training modules. Great job!")
        
        return []

class ActionSetupDirectDeposit(Action):
    def name(self) -> Text:
        return "action_setup_direct_deposit"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # In a real implementation, this would integrate with payroll systems
        
        dispatcher.utter_message(text="Your direct deposit information has been securely saved in our payroll system. Your first paycheck will be deposited directly to your account.")
        
        return []

class ActionGuideBenefitsSelection(Action):
    def name(self) -> Text:
        return "action_guide_benefits_selection"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # In a real implementation, this would guide through benefits options
        
        dispatcher.utter_message(text="I've recorded your benefits selections: Health Plan B, Dental Plan A, and 5% 401(k) contribution with company matching. You can change these selections during the annual enrollment period.")
        
        return []

class ActionCheckPendingDocuments(Action):
    def name(self) -> Text:
        return "action_check_pending_documents"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id") or "EMP001"
        pending_docs = HRDatabase().get_pending_documents(employee_id)
        
        if pending_docs:
            doc_list = ", ".join(pending_docs)
            dispatcher.utter_message(text=f"You have the following documents pending: {doc_list}. However, for this simplified onboarding, we'll consider them optional.")
        else:
            dispatcher.utter_message(text="You don't have any pending documents to submit.")
        
        return []

class ActionITSupport(Action):
    def name(self) -> Text:
        return "action_it_support"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # In a real implementation, this would create IT support tickets
        
        dispatcher.utter_message(text="I've notified the IT team to help you set up your computer, access card, and system credentials. They will reach out to you shortly.")
        
        return []

from typing import Any, Text, Dict, List
from datetime import datetime

class HRDatabase:
    """HR database to simulate backend operations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HRDatabase, cls).__new__(cls)
            cls._instance._initialize_data()
        return cls._instance
    
    def _initialize_data(self):
        """Initialize the database with mock data"""
        self.employees = {
            "EMP001": {
                "name": "Sarah Johnson",
                "department": "Engineering",
                "manager": "Alex Chen",
                "is_new_employee": True,
                "join_date": "2025-03-15",
                "leave_balance": {
                    "annual": 20,
                    "sick": 10,
                    "personal": 5
                }
            },
            "EMP002": {
                "name": "Michael Brown",
                "department": "Marketing",
                "manager": "Lisa Wong",
                "is_new_employee": False,
                "join_date": "2023-06-10",
                "leave_balance": {
                    "annual": 15,
                    "sick": 8,
                    "personal": 3
                }
            }
        }
        
        self.onboarding_tasks = {
            "EMP001": [
                {"name": "Complete personal information", "status": "completed"},
                {"name": "Set up company email", "status": "completed"},
                {"name": "Complete IT security training", "status": "pending"},
                {"name": "Review company policies", "status": "not_started"},
                {"name": "Set up direct deposit", "status": "completed"},
                {"name": "Meet with team members", "status": "not_started"},
                {"name": "Complete benefits enrollment", "status": "pending"},
                {"name": "Finish onboarding", "status": "not_started"}
            ]
        }
        
        self.teams = {
            "EMP001": [
                {"name": "Alex Chen", "role": "Engineering Manager"},
                {"name": "John Smith", "role": "Senior Developer"},
                {"name": "Emily Wong", "role": "Developer"},
                {"name": "David Kim", "role": "QA Engineer"},
                {"name": "Rachel Green", "role": "UX Designer"}
            ]
        }
        
        self.pending_documents = {
            "EMP001": [
                "Government ID",
                "Proof of address",
                "Educational certificates",
                "Previous employment references"
            ]
        }
        
        self.policies = {
            "work from home": "Employees can work from home up to 2 days per week with manager approval. Request must be submitted at least 24 hours in advance.",
            "dress code": "Business casual attire is required Monday through Thursday. Fridays are casual dress days.",
            "vacation": "Full-time employees accrue vacation at a rate of 1.67 days per month (20 days per year).",
            "sick leave": "Employees receive 10 sick days at the beginning of each calendar year. Unused sick days do not carry over.",
            "parental leave": "Eligible employees can take up to 12 weeks of paid parental leave following the birth or adoption of a child."
        }
    
    def get_employee_info(self, employee_id: str) -> Dict[str, Any]:
        """Get employee details from database"""
        return self.employees.get(employee_id, {})
    
    def get_onboarding_tasks(self, employee_id: str) -> List[Dict[str, str]]:
        """Get onboarding tasks and status"""
        return self.onboarding_tasks.get(employee_id, [])
    
    def get_policy_information(self, policy_query: str) -> str:
        """Get information about company policies"""
        # Simple keyword matching
        for key, value in self.policies.items():
            if key in policy_query.lower():
                return value
        
        return "I couldn't find specific information about that policy. Please contact HR directly for detailed information."
    
    def submit_leave_request(self, employee_id: str, leave_type: str, 
                            start_date: str, end_date: str, reason: str) -> Dict[str, str]:
        """Submit a leave request"""
        # In a real implementation, this would insert a record in the database
        # and trigger notifications
        return {"status": "submitted", "reference_id": "LR" + datetime.now().strftime("%Y%m%d%H%M")}
    
    def get_team_information(self, employee_id: str) -> List[Dict[str, str]]:
        """Get information about the employee's team"""
        return self.teams.get(employee_id, [])
    
    def get_pending_documents(self, employee_id: str) -> List[str]:
        """Get list of documents pending submission"""
        return self.pending_documents.get(employee_id, [])
    
    def update_employee(self, employee_id: str, updates: Dict[str, Any]) -> bool:
        """Update employee information"""
        if employee_id in self.employees:
            self.employees[employee_id].update(updates)
            return True
        return False
    
    def update_onboarding_task(self, employee_id: str, task_name: str, new_status: str) -> bool:
        """Update the status of an onboarding task"""
        if employee_id in self.onboarding_tasks:
            for task in self.onboarding_tasks[employee_id]:
                if task["name"] == task_name:
                    task["status"] = new_status
                    return True
        return False

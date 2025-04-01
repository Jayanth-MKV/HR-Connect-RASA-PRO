from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from db.database import HRDatabase

class ValidateDocumentType(Action):
    def name(self) -> Text:
        return "validate_document_type"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        document_type = tracker.get_slot("document_type")
        valid_types = ["id proof", "address proof", "educational certificates", "employment references", "tax forms"]
        
        if not any(doc_type in document_type.lower() for doc_type in valid_types):
            return {"document_type": None}
        return {"document_type": document_type}

class ValidateRequestedDocumentType(Action):
    def name(self) -> Text:
        return "validate_requested_document_type"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        document_type = tracker.get_slot("requested_document_type")
        valid_types = ["employment certificate", "salary slip", "tax document", "experience letter"]
        
        if not any(doc_type in document_type.lower() for doc_type in valid_types):
            return {"requested_document_type": None}
        return {"requested_document_type": document_type}

class ActionVerifyDocuments(Action):
    def name(self) -> Text:
        return "action_verify_documents"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        document_type = tracker.get_slot("document_type")
        
        # In a real implementation, this would initiate a document verification process
        # For now, we'll just assume it's successful
        
        return [SlotSet("document_status", "verified")]

class ActionCheckPendingDocuments(Action):
    def name(self) -> Text:
        return "action_check_pending_documents"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        employee_id = tracker.get_slot("employee_id")
        pending_documents = HRDatabase().get_pending_documents(employee_id)
        
        pending_docs_text = ", ".join(pending_documents)
        
        return [SlotSet("pending_documents", pending_docs_text)]

class ActionProcessDocumentRequest(Action):
    def name(self) -> Text:
        return "action_process_document_request"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        requested_document_type = tracker.get_slot("requested_document_type")
        
        # In a real implementation, this would initiate a document request process
        # For now, we'll just assume it's successful
        
        return []

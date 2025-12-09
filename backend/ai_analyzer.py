import os
from typing import List, Dict

class AIAnalyzer:
    """AI-powered analysis of emails and documents"""
    
    def __init__(self):
        # Initialize OpenAI client
        # You can set OPENAI_API_KEY environment variable or pass it here
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                self.enabled = True
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
                self.client = None
                self.enabled = False
        else:
            self.client = None
            self.enabled = False
    
    def analyze_data(self, prompt: str, emails: List[Dict], documents: List[Dict], 
                     email_contents: Dict[str, str] = None, 
                     document_contents: Dict[str, str] = None,
                     conversation_history: List[Dict] = None) -> str:
        """
        Analyze emails and documents based on user prompt
        
        Args:
            prompt: User's analysis question/request
            emails: List of email metadata
            documents: List of document metadata
            email_contents: Optional dict of email_id -> full email content
            document_contents: Optional dict of doc_id -> full document content
            conversation_history: Optional list of previous messages for context
        
        Returns:
            AI-generated analysis response
        """
        if not self.enabled:
            return "AI analysis is not available. Please set OPENAI_API_KEY environment variable."
        
        try:
            # Build context from available data
            context_parts = []
            
            # Add email summaries
            if emails:
                context_parts.append(f"EMAILS ({len(emails)} total):")
                for i, email in enumerate(emails[:20], 1):  # Limit to 20 for context
                    email_info = f"{i}. Subject: {email.get('subject', 'No Subject')}\n"
                    email_info += f"   From: {email.get('from_', 'Unknown')}\n"
                    email_info += f"   Date: {email.get('date', 'Unknown')}\n"
                    email_info += f"   Preview: {email.get('snippet', '')}\n"
                    
                    # Add full content if available
                    if email_contents and email.get('id') in email_contents:
                        full_content = email_contents[email['id']]
                        if full_content:
                            email_info += f"   Full Content: {full_content[:500]}...\n"
                    
                    context_parts.append(email_info)
            
            # Add document summaries
            if documents:
                context_parts.append(f"\nDOCUMENTS ({len(documents)} total):")
                for i, doc in enumerate(documents[:20], 1):  # Limit to 20 for context
                    doc_info = f"{i}. Name: {doc.get('name', 'Untitled')}\n"
                    doc_info += f"   Type: {doc.get('type', 'Unknown')}\n"
                    doc_info += f"   Modified: {doc.get('modified_time', 'Unknown')}\n"
                    
                    # Add parsed content if available
                    if document_contents and doc.get('id') in document_contents:
                        content = document_contents[doc['id']]
                        if content:
                            doc_info += f"   Content Preview: {content[:500]}...\n"
                    
                    context_parts.append(doc_info)
            
            context = "\n".join(context_parts)
            
            # Create the system message
            system_message = """You are an AI assistant helping to analyze emails and documents. 
            You have access to email and document metadata, and in some cases, their full content.
            Your task is to answer questions about this data, find patterns, summarize information,
            and provide insights based on the user's query. Be specific and reference the actual data.
            You can remember context from previous messages in the conversation."""
            
            # Build messages list with conversation history
            messages = [{"role": "system", "content": system_message}]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current context and user query
            messages.append({
                "role": "user", 
                "content": f"Context:\n{context}\n\nUser Query: {prompt}"
            })
            
            # Create the completion
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # or "gpt-3.5-turbo" for faster/cheaper
                messages=messages,
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error performing AI analysis: {str(e)}"
    
    def quick_summary(self, emails: List[Dict], documents: List[Dict]) -> str:
        """Generate a quick summary of the search results"""
        if not self.enabled:
            summary = f"Found {len(emails)} emails and {len(documents)} documents.\n"
            if emails:
                summary += f"First email: {emails[0].get('subject', 'No Subject')}\n"
            if documents:
                summary += f"First document: {documents[0].get('name', 'Untitled')}\n"
            return summary
        
        try:
            # Create a brief context
            context = f"Emails: {len(emails)}\n"
            if emails:
                context += f"Recent subjects: {', '.join([e.get('subject', 'No Subject')[:50] for e in emails[:5]])}\n"
            
            context += f"\nDocuments: {len(documents)}\n"
            if documents:
                context += f"Document names: {', '.join([d.get('name', 'Untitled')[:50] for d in documents[:5]])}\n"
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Provide a brief 2-3 sentence summary of these search results."},
                    {"role": "user", "content": context}
                ],
                max_tokens=150,
                temperature=0.5
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Found {len(emails)} emails and {len(documents)} documents."


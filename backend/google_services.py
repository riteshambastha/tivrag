import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from typing import List, Dict
import base64
from email.utils import parsedate_to_datetime
from email.mime.text import MIMEText

class GoogleServicesManager:
    """Manages Google API interactions for Gmail and Drive"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/documents.readonly',
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/presentations.readonly'
    ]
    
    def __init__(self):
        # You need to create a Google Cloud project and download OAuth credentials
        # For now, we'll use placeholders - replace with your actual credentials
        self.client_id = os.getenv("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "YOUR_GOOGLE_CLIENT_SECRET")
        self.redirect_uri = "http://localhost:5175/configuration/callback"
    
    def get_authorization_url(self) -> str:
        """Generate Google OAuth authorization URL"""
        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.redirect_uri]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return auth_url
    
    def exchange_code(self, code: str) -> Credentials:
        """Exchange authorization code for credentials"""
        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.redirect_uri]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        flow.fetch_token(code=code)
        return flow.credentials
    
    def search_emails(self, credentials: Credentials, person: str, date_from: str = None, date_to: str = None) -> List[Dict]:
        """Search emails from a specific person with date filtering - searches ALL folders including Updates"""
        try:
            print(f"\n=== Starting Gmail Search ===")
            print(f"Searching for emails from: {person}")
            print(f"Date range: {date_from} to {date_to}")
            
            service = build('gmail', 'v1', credentials=credentials)
            
            # Build query with date filters
            # Note: Gmail API searches ALL folders by default (Primary, Social, Updates, Promotions, etc.)
            query = f'from:{person}'
            if date_from:
                query += f' after:{date_from}'
            if date_to:
                query += f' before:{date_to}'
            
            print(f"Gmail query: {query}")
            print(f"Note: Searching across ALL Gmail folders (Primary, Updates, Social, Promotions, etc.)")
            
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=100
            ).execute()
            
            messages = results.get('messages', [])
            print(f"Found {len(messages)} email messages across all folders")
            emails = []
            
            folder_counts = {}
            
            for msg in messages:
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                snippet = message.get('snippet', '')
                
                # Get labels to determine folder
                labels = message.get('labelIds', [])
                folder = 'Unknown'
                if 'CATEGORY_PERSONAL' in labels or 'INBOX' in labels:
                    folder = 'Primary'
                if 'CATEGORY_UPDATES' in labels:
                    folder = 'Updates'
                if 'CATEGORY_SOCIAL' in labels:
                    folder = 'Social'
                if 'CATEGORY_PROMOTIONS' in labels:
                    folder = 'Promotions'
                if 'CATEGORY_FORUMS' in labels:
                    folder = 'Forums'
                
                # Track folder distribution
                folder_counts[folder] = folder_counts.get(folder, 0) + 1
                
                # Check if this is a Drive sharing notification
                is_drive_share = 'shared' in subject.lower() and 'drive' in subject.lower()
                if is_drive_share:
                    print(f"  ✓ Found Drive sharing email in {folder}: {subject}")
                
                emails.append({
                    'id': message['id'],
                    'subject': subject,
                    'from_': from_email,
                    'date': date,
                    'snippet': snippet,
                    'folder': folder,
                    'is_drive_share': is_drive_share
                })
            
            print(f"\n=== Gmail Folder Distribution ===")
            for folder, count in folder_counts.items():
                print(f"  {folder}: {count} emails")
            
            print(f"=== Gmail Search Complete: {len(emails)} emails ===\n")
            return emails
        except Exception as e:
            print(f"CRITICAL ERROR in search_emails: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def search_documents(self, credentials: Credentials, person: str, date_from: str = None, date_to: str = None) -> List[Dict]:
        """Search documents shared by a specific person - includes both owned AND shared files"""
        try:
            print(f"\n=== Starting Google Drive Search ===")
            print(f"Searching for documents from: {person}")
            print(f"Date range: {date_from} to {date_to}")
            
            service = build('drive', 'v3', credentials=credentials)
            
            # Build multiple query strategies to find documents:
            # 1. Files owned by this person
            # 2. Files shared with me from this person
            # 3. All shared files (we'll filter by person later)
            queries = []
            
            # Query 1: Files owned by specific person
            queries.append(f"'{person}' in owners")
            
            # Query 2: All files shared with me (we'll filter by owner)
            queries.append("sharedWithMe=true")
            
            # Query 3: Files where this person is mentioned
            queries.append(f"'{person}' in writers")
            
            all_files = []
            seen_ids = set()
            
            for query_index, base_query in enumerate(queries, 1):
                # Add date filters if provided
                full_query = base_query
                if date_from:
                    # date_from is already in ISO format (YYYY-MM-DDTHH:MM:SS), just use it
                    full_query += f" and modifiedTime >= '{date_from}'"
                if date_to:
                    # date_to is already in ISO format (YYYY-MM-DDTHH:MM:SS), just use it
                    full_query += f" and modifiedTime <= '{date_to}'"
                
                try:
                    print(f"\n[Query {query_index}] Executing: {full_query}")
                    results = service.files().list(
                        q=full_query,
                        pageSize=100,
                        fields="files(id, name, mimeType, modifiedTime, webViewLink, owners, sharingUser, shared, permissions)",
                        orderBy="modifiedTime desc",
                        supportsAllDrives=True,
                        includeItemsFromAllDrives=True
                    ).execute()
                    
                    files = results.get('files', [])
                    print(f"[Query {query_index}] Returned {len(files)} files")
                    
                    for file in files:
                        # Avoid duplicates
                        if file['id'] in seen_ids:
                            continue
                        
                        # Get owner information
                        owners = file.get('owners', [])
                        owner_emails = [owner.get('emailAddress', '').lower() for owner in owners]
                        
                        # Get sharing user (person who shared it with you)
                        sharing_user = file.get('sharingUser', {})
                        sharing_email = sharing_user.get('emailAddress', '').lower() if sharing_user else ''
                        
                        # Check if file is related to this person (owner OR sharer)
                        person_lower = person.lower()
                        is_owner_match = any(person_lower in email for email in owner_emails)
                        is_sharer_match = person_lower in sharing_email if sharing_email else False
                        
                        if is_owner_match or is_sharer_match:
                            mime_type = file.get('mimeType', '')
                            doc_type = 'Document'
                            
                            if 'spreadsheet' in mime_type:
                                doc_type = 'Spreadsheet'
                            elif 'presentation' in mime_type:
                                doc_type = 'Presentation'
                            elif 'pdf' in mime_type:
                                doc_type = 'PDF'
                            elif 'image' in mime_type:
                                doc_type = 'Image'
                            elif 'document' in mime_type:
                                doc_type = 'Document'
                            elif 'folder' in mime_type:
                                continue  # Skip folders
                            
                            match_reason = []
                            if is_owner_match:
                                match_reason.append(f"owned by {owner_emails}")
                            if is_sharer_match:
                                match_reason.append(f"shared by {sharing_email}")
                            
                            print(f"  ✓ Adding: {file['name']} (Type: {doc_type}, {', '.join(match_reason)})")
                            
                            all_files.append({
                                'id': file['id'],
                                'name': file['name'],
                                'type': doc_type,
                                'mime_type': mime_type,
                                'modified_time': file.get('modifiedTime', ''),
                                'web_view_link': file.get('webViewLink', ''),
                                'owner_emails': owner_emails,
                                'shared_by': sharing_email,
                                'match_reason': ', '.join(match_reason)
                            })
                            seen_ids.add(file['id'])
                        else:
                            print(f"  ✗ Skipping: {file['name']} (owners: {owner_emails}, sharer: {sharing_email}, looking for: {person})")
                except Exception as e:
                    print(f"[Query {query_index}] ERROR: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            print(f"\n=== Drive Search Complete ===")
            print(f"Total unique files found: {len(all_files)}")
            if len(all_files) > 0:
                print(f"Files by type:")
                type_counts = {}
                for f in all_files:
                    type_counts[f['type']] = type_counts.get(f['type'], 0) + 1
                for doc_type, count in type_counts.items():
                    print(f"  {doc_type}: {count}")
            return all_files
        except Exception as e:
            print(f"CRITICAL ERROR in search_documents: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def send_email(self, credentials: Credentials, to: str, subject: str, body: str) -> Dict:
        """Send an email via Gmail API"""
        try:
            print(f"\n=== Sending Email ===")
            print(f"To: {to}")
            print(f"Subject: {subject}")
            
            service = build('gmail', 'v1', credentials=credentials)
            
            # Create the email
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send the email
            sent_message = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"Email sent successfully. Message ID: {sent_message['id']}")
            print(f"Thread ID: {sent_message.get('threadId', 'N/A')}")
            
            return {
                'status': 'success',
                'message_id': sent_message['id'],
                'thread_id': sent_message.get('threadId')
            }
        except Exception as e:
            print(f"ERROR sending email: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to send email: {str(e)}")


import io
import os
from typing import Dict, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import PyPDF2
from docx import Document

class DocumentParser:
    """Parse content from various document types"""
    
    @staticmethod
    def parse_google_doc(credentials: Credentials, file_id: str) -> str:
        """Extract text from Google Docs"""
        try:
            service = build('docs', 'v1', credentials=credentials)
            document = service.documents().get(documentId=file_id).execute()
            
            content = []
            for element in document.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    paragraph = element['paragraph']
                    for text_element in paragraph.get('elements', []):
                        if 'textRun' in text_element:
                            content.append(text_element['textRun']['content'])
            
            return ''.join(content)
        except Exception as e:
            print(f"Error parsing Google Doc: {e}")
            return ""
    
    @staticmethod
    def parse_pdf(credentials: Credentials, file_id: str) -> str:
        """Extract text from PDF files"""
        try:
            service = build('drive', 'v3', credentials=credentials)
            request = service.files().get_media(fileId=file_id)
            
            file_handle = io.BytesIO()
            downloader = MediaIoBaseDownload(file_handle, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_handle.seek(0)
            pdf_reader = PyPDF2.PdfReader(file_handle)
            
            text = []
            for page in pdf_reader.pages:
                text.append(page.extract_text())
            
            return '\n'.join(text)
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return ""
    
    @staticmethod
    def parse_docx(credentials: Credentials, file_id: str) -> str:
        """Extract text from DOCX files"""
        try:
            service = build('drive', 'v3', credentials=credentials)
            request = service.files().get_media(fileId=file_id)
            
            file_handle = io.BytesIO()
            downloader = MediaIoBaseDownload(file_handle, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_handle.seek(0)
            doc = Document(file_handle)
            
            text = []
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
            
            return '\n'.join(text)
        except Exception as e:
            print(f"Error parsing DOCX: {e}")
            return ""
    
    @staticmethod
    def parse_spreadsheet(credentials: Credentials, file_id: str) -> str:
        """Extract text from Google Sheets"""
        try:
            service = build('sheets', 'v4', credentials=credentials)
            
            # Get sheet metadata to find all sheets
            spreadsheet = service.spreadsheets().get(spreadsheetId=file_id).execute()
            sheets = spreadsheet.get('sheets', [])
            
            all_data = []
            for sheet in sheets:
                sheet_title = sheet['properties']['title']
                range_name = f"{sheet_title}"
                
                result = service.spreadsheets().values().get(
                    spreadsheetId=file_id,
                    range=range_name
                ).execute()
                
                values = result.get('values', [])
                if values:
                    all_data.append(f"Sheet: {sheet_title}")
                    for row in values:
                        all_data.append(' | '.join(str(cell) for cell in row))
            
            return '\n'.join(all_data)
        except Exception as e:
            print(f"Error parsing spreadsheet: {e}")
            return ""
    
    @staticmethod
    def parse_presentation(credentials: Credentials, file_id: str) -> str:
        """Extract text from Google Slides"""
        try:
            service = build('slides', 'v1', credentials=credentials)
            presentation = service.presentations().get(presentationId=file_id).execute()
            
            slides = presentation.get('slides', [])
            text_content = []
            
            for i, slide in enumerate(slides):
                text_content.append(f"Slide {i + 1}:")
                for element in slide.get('pageElements', []):
                    if 'shape' in element:
                        shape = element['shape']
                        if 'text' in shape:
                            for text_element in shape['text'].get('textElements', []):
                                if 'textRun' in text_element:
                                    text_content.append(text_element['textRun']['content'])
            
            return '\n'.join(text_content)
        except Exception as e:
            print(f"Error parsing presentation: {e}")
            return ""
    
    @staticmethod
    def parse_document(credentials: Credentials, file_id: str, mime_type: str) -> str:
        """Parse document based on its type"""
        if 'google-apps.document' in mime_type:
            return DocumentParser.parse_google_doc(credentials, file_id)
        elif 'google-apps.spreadsheet' in mime_type:
            return DocumentParser.parse_spreadsheet(credentials, file_id)
        elif 'google-apps.presentation' in mime_type:
            return DocumentParser.parse_presentation(credentials, file_id)
        elif 'pdf' in mime_type:
            return DocumentParser.parse_pdf(credentials, file_id)
        elif 'wordprocessingml' in mime_type or 'msword' in mime_type:
            return DocumentParser.parse_docx(credentials, file_id)
        else:
            return f"[Unsupported file type: {mime_type}]"
    
    @staticmethod
    def get_email_body(credentials: Credentials, message_id: str) -> str:
        """Extract full body from email"""
        try:
            service = build('gmail', 'v1', credentials=credentials)
            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            payload = message.get('payload', {})
            body = ""
            
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            import base64
                            body = base64.urlsafe_b64decode(data).decode('utf-8')
                            break
            elif 'body' in payload:
                data = payload['body'].get('data', '')
                if data:
                    import base64
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
            
            return body
        except Exception as e:
            print(f"Error getting email body: {e}")
            return ""


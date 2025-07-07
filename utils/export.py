import csv
import json
import os
from typing import List, Dict, Optional
from datetime import datetime
import re
import logging
from models.schemas import Lead

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExportManager:
    """
    Manager for exporting leads to various formats
    """
    
    def __init__(self, export_dir: str = "exports"):
        self.export_dir = export_dir
        self._ensure_export_dir()
    
    def _ensure_export_dir(self):
        """Ensure export directory exists"""
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
    
    def export_to_csv(self, leads: List[Lead], filename: Optional[str] = None) -> str:
        """
        Export leads to CSV file
        """
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"leads_{timestamp}.csv"
            
            # Ensure .csv extension
            if not filename.endswith('.csv'):
                filename += '.csv'
            
            filepath = os.path.join(self.export_dir, filename)
            
            # Define CSV headers
            headers = [
                'Name',
                'Address',
                'Phone',
                'Email',
                'Website',
                'Category',
                'Rating',
                'Reviews Count',
                'Google Maps URL',
                'Place ID',
                'Coordinates'
            ]
            
            # Write CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                
                for lead in leads:
                    # Format coordinates
                    coords = ""
                    if lead.coordinates:
                        coords = f"{lead.coordinates.get('lat', '')},{lead.coordinates.get('lng', '')}"
                    
                    row = [
                        lead.name or "",
                        lead.address or "",
                        lead.phone or "",
                        lead.email or "",
                        lead.website or "",
                        lead.category or "",
                        lead.rating or "",
                        lead.reviews_count or "",
                        lead.google_maps_url or "",
                        lead.place_id or "",
                        coords
                    ]
                    writer.writerow(row)
            
            logger.info(f"Exported {len(leads)} leads to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"CSV export error: {str(e)}")
            raise e
    
    def export_to_json(self, leads: List[Lead], filename: Optional[str] = None) -> str:
        """
        Export leads to JSON file
        """
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"leads_{timestamp}.json"
            
            # Ensure .json extension
            if not filename.endswith('.json'):
                filename += '.json'
            
            filepath = os.path.join(self.export_dir, filename)
            
            # Convert leads to dictionaries
            leads_data = []
            for lead in leads:
                lead_dict = {
                    'name': lead.name,
                    'address': lead.address,
                    'phone': lead.phone,
                    'email': lead.email,
                    'website': lead.website,
                    'category': lead.category,
                    'rating': lead.rating,
                    'reviews_count': lead.reviews_count,
                    'google_maps_url': lead.google_maps_url,
                    'place_id': lead.place_id,
                    'coordinates': lead.coordinates
                }
                leads_data.append(lead_dict)
            
            # Write JSON
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(leads_data, jsonfile, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(leads)} leads to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"JSON export error: {str(e)}")
            raise e
    
    def export_to_sheets(self, leads: List[Lead], sheets_url: str) -> bool:
        """
        Export leads to Google Sheets (simplified implementation)
        Note: This is a basic implementation. For production use, you'd want to use
        the Google Sheets API with proper authentication.
        """
        try:
            # For now, we'll create a CSV and provide instructions
            # In production, you'd use the Google Sheets API
            
            logger.warning("Google Sheets export not fully implemented.")
            logger.info("Creating CSV file that can be imported to Google Sheets")
            
            # Create CSV for manual import
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"leads_for_sheets_{timestamp}.csv"
            csv_path = self.export_to_csv(leads, csv_filename)
            
            logger.info(f"CSV created at {csv_path}")
            logger.info("To import to Google Sheets:")
            logger.info("1. Open Google Sheets")
            logger.info("2. File > Import > Upload")
            logger.info(f"3. Upload the file: {csv_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Sheets export error: {str(e)}")
            return False
    
    def export_to_excel(self, leads: List[Lead], filename: Optional[str] = None) -> str:
        """
        Export leads to Excel file (basic implementation without pandas)
        """
        try:
            # For basic Excel export without external dependencies
            # We'll create a CSV that can be opened in Excel
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"leads_{timestamp}.xlsx"
            
            # Ensure .xlsx extension
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            # Create CSV version (Excel can open CSV files)
            csv_filename = filename.replace('.xlsx', '.csv')
            csv_path = self.export_to_csv(leads, csv_filename)
            
            logger.info(f"Excel-compatible CSV created at {csv_path}")
            logger.info("This file can be opened in Excel and saved as .xlsx")
            
            return csv_path
            
        except Exception as e:
            logger.error(f"Excel export error: {str(e)}")
            raise e
    
    def get_export_summary(self, leads: List[Lead]) -> Dict:
        """
        Get summary statistics for the leads
        """
        try:
            total_leads = len(leads)
            leads_with_email = len([l for l in leads if l.email])
            leads_with_phone = len([l for l in leads if l.phone])
            leads_with_website = len([l for l in leads if l.website])
            
            # Calculate average rating
            ratings = [l.rating for l in leads if l.rating is not None]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            # Get categories
            categories = {}
            for lead in leads:
                if lead.category:
                    categories[lead.category] = categories.get(lead.category, 0) + 1
            
            return {
                'total_leads': total_leads,
                'leads_with_email': leads_with_email,
                'leads_with_phone': leads_with_phone,
                'leads_with_website': leads_with_website,
                'email_coverage': round((leads_with_email / total_leads) * 100, 2) if total_leads > 0 else 0,
                'phone_coverage': round((leads_with_phone / total_leads) * 100, 2) if total_leads > 0 else 0,
                'website_coverage': round((leads_with_website / total_leads) * 100, 2) if total_leads > 0 else 0,
                'average_rating': round(avg_rating, 2),
                'categories': categories
            }
            
        except Exception as e:
            logger.error(f"Summary generation error: {str(e)}")
            return {}
    
    def validate_leads_data(self, leads: List[Lead]) -> Dict:
        """
        Validate leads data quality
        """
        try:
            issues = []
            
            for i, lead in enumerate(leads):
                lead_issues = []
                
                # Check required fields
                if not lead.name:
                    lead_issues.append("Missing name")
                
                # Validate email format
                if lead.email:
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
                    if not re.match(email_pattern, lead.email):
                        lead_issues.append("Invalid email format")
                
                # Validate phone format (basic)
                if lead.phone:
                    phone_clean = re.sub(r'[^\d+]', '', lead.phone)
                    if len(phone_clean) < 10:
                        lead_issues.append("Phone number too short")
                
                # Validate website URL
                if lead.website:
                    if not (lead.website.startswith('http://') or lead.website.startswith('https://') or '.' in lead.website):
                        lead_issues.append("Invalid website URL")
                
                if lead_issues:
                    issues.append({
                        'lead_index': i,
                        'lead_name': lead.name,
                        'issues': lead_issues
                    })
            
            return {
                'total_leads': len(leads),
                'leads_with_issues': len(issues),
                'issues': issues,
                'data_quality_score': round(((len(leads) - len(issues)) / len(leads)) * 100, 2) if leads else 0
            }
            
        except Exception as e:
            logger.error(f"Data validation error: {str(e)}")
            return {}
    
    def cleanup_old_exports(self, days_old: int = 7):
        """
        Clean up old export files
        """
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            
            for filename in os.listdir(self.export_dir):
                filepath = os.path.join(self.export_dir, filename)
                if os.path.isfile(filepath):
                    file_time = os.path.getmtime(filepath)
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        logger.info(f"Deleted old export: {filename}")
                        
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
    
    def list_exports(self) -> List[Dict]:
        """
        List all available export files
        """
        try:
            exports = []
            
            for filename in os.listdir(self.export_dir):
                filepath = os.path.join(self.export_dir, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    exports.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            return sorted(exports, key=lambda x: x['modified'], reverse=True)
            
        except Exception as e:
            logger.error(f"List exports error: {str(e)}")
            return []
import asyncio
import re
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, Browser
from models.schemas import Lead
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleMapsScraper:
    """
    Google Maps scraper using Playwright for dynamic content
    """
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def _init_browser(self):
        """Initialize browser instance"""
        if not self.browser:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            self.page = await self.browser.new_page()
            
            # Set user agent to avoid detection
            await self.page.set_user_agent(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
    
    async def _close_browser(self):
        """Close browser instance"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None
    
    async def scrape_businesses(self, query: str, location: str, max_results: int = 50) -> List[Lead]:
        """
        Scrape businesses from Google Maps
        """
        await self._init_browser()
        
        try:
            # Construct search URL
            search_url = f"https://www.google.com/maps/search/{query}+{location}"
            logger.info(f"Starting scrape for: {query} in {location}")
            
            # Navigate to Google Maps
            await self.page.goto(search_url, wait_until='networkidle')
            await asyncio.sleep(2)
            
            # Wait for results to load
            await self.page.wait_for_selector('[data-value="Search results"]', timeout=10000)
            
            leads = []
            processed_places = set()
            
            # Scroll and collect results
            for i in range(max_results // 10):  # Approximate scroll cycles
                await self._scroll_results()
                await asyncio.sleep(1)
                
                # Extract business data
                business_elements = await self.page.query_selector_all('[data-result-index]')
                
                for element in business_elements:
                    if len(leads) >= max_results:
                        break
                    
                    lead_data = await self._extract_business_data(element)
                    if lead_data and lead_data.get('name') not in processed_places:
                        lead = Lead(**lead_data)
                        leads.append(lead)
                        processed_places.add(lead_data['name'])
                        logger.info(f"Scraped: {lead.name}")
                
                if len(leads) >= max_results:
                    break
            
            logger.info(f"Scraping completed. Found {len(leads)} leads")
            return leads
            
        except Exception as e:
            logger.error(f"Scraping error: {str(e)}")
            raise e
        finally:
            await self._close_browser()
    
    async def _scroll_results(self):
        """Scroll the results panel to load more businesses"""
        try:
            # Find and scroll the results panel
            await self.page.evaluate("""
                const resultsPanel = document.querySelector('[data-value="Search results"]');
                if (resultsPanel) {
                    resultsPanel.scrollTop = resultsPanel.scrollHeight;
                }
            """)
            await asyncio.sleep(1)
        except Exception as e:
            logger.warning(f"Scroll error: {str(e)}")
    
    async def _extract_business_data(self, element) -> Optional[Dict]:
        """Extract business data from a single business element"""
        try:
            # Extract business name
            name_element = await element.query_selector('[data-value="Business name"]')
            if not name_element:
                return None
            
            name = await name_element.text_content()
            if not name:
                return None
            
            # Initialize business data
            business_data = {
                'name': name.strip(),
                'address': None,
                'phone': None,
                'website': None,
                'rating': None,
                'reviews_count': None,
                'category': None,
                'google_maps_url': None,
                'place_id': None,
                'coordinates': None
            }
            
            # Extract address
            address_element = await element.query_selector('[data-value="Address"]')
            if address_element:
                address = await address_element.text_content()
                business_data['address'] = address.strip() if address else None
            
            # Extract rating
            rating_element = await element.query_selector('[data-value="Rating"]')
            if rating_element:
                rating_text = await rating_element.text_content()
                if rating_text:
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        business_data['rating'] = float(rating_match.group(1))
            
            # Extract reviews count
            reviews_element = await element.query_selector('[data-value="Reviews"]')
            if reviews_element:
                reviews_text = await reviews_element.text_content()
                if reviews_text:
                    reviews_match = re.search(r'(\d+)', reviews_text.replace(',', ''))
                    if reviews_match:
                        business_data['reviews_count'] = int(reviews_match.group(1))
            
            # Extract category
            category_element = await element.query_selector('[data-value="Category"]')
            if category_element:
                category = await category_element.text_content()
                business_data['category'] = category.strip() if category else None
            
            # Try to get more details by clicking on the business
            try:
                await element.click()
                await asyncio.sleep(1)
                
                # Extract phone number
                phone_element = await self.page.query_selector('[data-value="Phone number"]')
                if phone_element:
                    phone = await phone_element.text_content()
                    business_data['phone'] = phone.strip() if phone else None
                
                # Extract website
                website_element = await self.page.query_selector('[data-value="Website"]')
                if website_element:
                    website_link = await website_element.query_selector('a')
                    if website_link:
                        website = await website_link.get_attribute('href')
                        business_data['website'] = website
                
                # Extract Google Maps URL
                current_url = self.page.url
                if 'place/' in current_url:
                    business_data['google_maps_url'] = current_url
                    
                    # Extract Place ID from URL
                    place_id_match = re.search(r'place/([^/]+)', current_url)
                    if place_id_match:
                        business_data['place_id'] = place_id_match.group(1)
                
                # Go back to results
                await self.page.go_back()
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.warning(f"Error extracting detailed info for {name}: {str(e)}")
            
            return business_data
            
        except Exception as e:
            logger.error(f"Error extracting business data: {str(e)}")
            return None
    
    async def get_business_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information for a specific business"""
        await self._init_browser()
        
        try:
            # Navigate to specific place
            place_url = f"https://www.google.com/maps/place/{place_id}"
            await self.page.goto(place_url, wait_until='networkidle')
            await asyncio.sleep(2)
            
            # Extract detailed information
            details = {}
            
            # Extract hours
            hours_element = await self.page.query_selector('[data-value="Hours"]')
            if hours_element:
                hours_text = await hours_element.text_content()
                details['hours'] = hours_text.strip() if hours_text else None
            
            # Extract additional info
            # This can be extended based on specific needs
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting business details: {str(e)}")
            return None
        finally:
            await self._close_browser()
    
    def __del__(self):
        """Cleanup on destruction"""
        if self.browser:
            asyncio.create_task(self._close_browser())
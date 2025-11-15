import random
import re
from decimal import Decimal
from django.db.models import Q, Avg
from services.models import (
    BuyProperties, PropertyLocation, NearbyPlaces, FeatureAmenity,
    SellResidentialProperties, SellCommercialProperties,
    InteriorDesignRequest, PropertyCalculatorInquiry
)
from django.db import models

class PropertyChatBot:
    def __init__(self):
        self.bhk_types = ['1bhk', '2bhk', '3bhk', '4bhk', '5bhk', 'villa', 'bungalow', 'duplex', 'tenament']
        self.commercial_types = ['showroom', 'office', 'shop', 'corporate_floors', 'corporate floor']
        self.property_statuses = ['new', 'resale', 'rent', 'lease']
        self.budget_keywords = ['budget', 'under', 'below', 'above', 'lakhs', 'lakh', 'crore', 'crores']
        
        self.property_keywords = [
            'property', 'house', 'home', 'flat', 'apartment', 'buy', 'sell', 'rent', 'lease',
            'real estate', 'builder', 'construction', 'project', 'location', 'area', 'sqft',
            'bedroom', 'bathroom', 'kitchen', 'balcony', 'parking', 'amenities', 'gym', 'pool',
            'security', 'garden', 'club', 'investment', 'roi', 'appreciation', 'price', 'cost',
            'interior', 'design', 'decoration', 'turnkey', 'consultancy', 'market', 'trend'
        ]
        
        self.friendly_responses = [
            "Hey there! I'm doing great, thanks for asking—how about you? 😄 Ready to find your dream home?",
            "Aww, you're sweet! I'm just a bot, but I'm super excited to help you find a property! 🏠 What's on your mind?",
            "Haha, I'm blushing in binary! 😊 Let's chat about your dream property—any ideas?",
            "Yo, what's good? I'm just chilling in the cloud, ready to find you a perfect place! 🏡 Tell me what you're looking for!",
            "Well, aren't you a charmer? 😎 I'm here to help you find a cozy home or a cool office—whatcha thinking?"
        ]
        
        self.friendly_keywords = [
            'how are you', 'how you doing', 'what\'s up', 'wanna chat', 'hey cutie', 'love you', 'miss you', 'cutie',
            'flirt', 'friend', 'just chatting', 'hanging out', 'timepass'
        ]
        
        self.goodbye_responses = [
            "Goodbye! 👋 It was great helping you with your property search. Come back anytime you need assistance! 🏠",
            "See you later! 😊 Hope you find your perfect property soon. Feel free to reach out whenever you need help! 🏡",
            "Take care! 💙 Thanks for chatting with me. I'm always here when you need property advice. Bye! 👋",
            "Bye bye! 🌟 Best of luck with your property journey. Don't hesitate to contact me again! 🏠✨",
            "Farewell! 🤗 It's been a pleasure assisting you. Come back soon for more property insights! 🏡💫",
            "Catch you later! 😄 Hope I helped you get closer to your dream home. See you next time! 👋🏠"
        ]
        
        self.goodbye_keywords = [
            'bye', 'goodbye', 'good bye', 'see you', 'see ya', 'catch you later', 'talk to you later', 
            'ttyl', 'farewell', 'take care', 'gotta go', 'have to go', 'leaving now', 'exit', 'quit'
        ]
        
        self.out_of_concept_response = (
            "I'm HorizonBot, your property assistant! 🏠 I specialize in helping with real estate queries.\n\n"
            "I can help you with:\n"
            "🏠 Finding properties (2BHK, 3BHK, villas, commercial)\n"
            "📍 Properties by location\n"
            "💰 Budget-based searches\n"
            "🏢 Commercial properties\n"
            "🎨 Interior design services\n"
            "📊 Market insights\n\n"
            "Try asking: '2BHK in [location] under 50 lakhs' or 'Show me villas in [area]'"
        )

    def is_property_related(self, user_input):
        """Check if the user input is related to property/real estate."""
        user_input_lower = user_input.lower()
        
        greeting_keywords = ['hello', 'hi', 'hey', 'start', 'help']
        if any(keyword in user_input_lower for keyword in greeting_keywords):
            return True
        
        if any(keyword in user_input_lower for keyword in self.friendly_keywords):
            return True
        
        if any(keyword in user_input_lower for keyword in self.goodbye_keywords):
            return True
        
        if any(keyword in user_input_lower for keyword in self.property_keywords):
            return True
        
        if any(bhk in user_input_lower for bhk in self.bhk_types):
            return True
        
        if any(comm in user_input_lower for comm in self.commercial_types):
            return True
        
        if any(status in user_input_lower for status in self.property_statuses):
            return True
        
        if self.extract_budget_range(user_input):
            return True
        
        if self.extract_area_range(user_input):
            return True
        
        all_locations = PropertyLocation.objects.values_list('name', flat=True)
        if any(location.lower() in user_input_lower for location in all_locations):
            return True
        
        return False

    def extract_budget_range(self, user_input):
        """Extract budget information from user input."""
        budget_pattern = r'(\d+(?:\.\d+)?)\s*(lakh|lakhs|crore|crores)'
        matches = re.findall(budget_pattern, user_input.lower())
        
        budgets = []
        for amount, unit in matches:
            amount = float(amount)
            if 'crore' in unit:
                amount = amount * 100
            budgets.append(amount)
        
        return budgets
    
    def extract_area_range(self, user_input):
        """Extract area information from user input."""
        area_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:sq\s*ft|sqft|square\s*feet)',
            r'(\d+(?:\.\d+)?)\s*(?:sq\s*yards|sqyards|square\s*yards)',
        ]
        
        for pattern in area_patterns:
            matches = re.findall(pattern, user_input.lower())
            if matches:
                return [float(match) for match in matches]
        return []

    def format_buy_property_response(self, properties, query_type="general"):
        """Format response for buy properties with clickable links - each field on new line."""
        if not properties:
            suggestions = [
                "Try searching with different location or configuration",
                "Check out our new projects section", 
                "Browse properties by budget range",
                "Ask about upcoming projects"
            ]
            return f"Sorry, no matching properties found. {random.choice(suggestions)}"

        response = f"Found {properties.count()} properties for you:<br><br>"

        for prop in properties[:5]:
            budget_range = f"₹{int(prop.min_budget)}-{int(prop.max_budget)} {prop.min_budget_unit.title()}"
            
            response += f"🏠 **{prop.project_name}**<br><br>"
            response += f"📍 Location: {prop.locations.name}<br><br>"
            response += f"🏗️ Type: {prop.configuration.upper() if prop.configuration else prop.commercial_type}<br><br>"
            response += f"📐 Area: {prop.area} sq ft<br><br>"
            response += f"💰 Budget: {budget_range}<br><br>"
            status = prop.status.title() if prop.status else "Not specified"
            response += f"📅 Status: {status}<br><br>"
            
            property_url = f"/property/{prop.slug}/"
            response += f'🔗 <a href="{property_url}" target="_blank" class="property-link">View Details</a><br><br>'
            response += f"<br>"
        if properties.count() > 5:
            response += f"... and {properties.count() - 5} more properties available!<br><br>"
            
        return response.strip()

    def format_sell_property_response(self, residential_props, commercial_props):
        """Format response for sell properties - each field on new line."""
        total_count = len(residential_props) + len(commercial_props)
        
        if total_count == 0:
            return "No properties available for sale right now. Would you like to list your property with us?"
        
        response = f"Found {total_count} properties for sale:<br><br>"
        
        for prop in residential_props[:3]:
            response += f"🏠 **{prop.project_name}** (Residential)<br><br>"
            response += f"📍 Location: {prop.locations.name}<br><br>"
            response += f"🏗️ Type: {prop.configuration.upper()}<br><br>"
            response += f"📐 Area: {prop.area} sq ft<br><br>"
            response += f"💰 Budget: ₹{prop.budget:,}<br><br>"
            response += f"👤 Contact: {prop.contact_name}<br><br>"
            response += f"📞 Phone: {prop.contact_number}<br><br>"
        
        for prop in commercial_props[:2]:
            response += f"🏢 **{prop.project_name}** (Commercial)<br><br>"
            response += f"📍 Location: {prop.locations.name}<br><br>"
            response += f"🏗️ Type: {prop.commercial_type.title()}<br><br>"
            response += f"📐 Area: {prop.area} sq ft<br><br>"
            response += f"💰 Budget: ₹{prop.budget:,}<br><br>"
            response += f"👤 Contact: {prop.contact_name}<br><br>"
            response += f"📞 Phone: {prop.contact_number}<br><br>"
        return response.strip()

    def get_location_suggestions(self, user_input):
        """Get location-based suggestions."""
        all_locations = PropertyLocation.objects.values_list('name', flat=True)
        found_location = next((location for location in all_locations if location.lower() in user_input.lower()), None)
        
        if found_location:
            buy_count = BuyProperties.objects.filter(
                locations__name__icontains=found_location,
                is_property_active=True
            ).count()
            
            response = f"📍 **Properties in {found_location}:**<br><br>"
            response += f"• {buy_count} properties available for purchase<br><br>"
            
            popular_configs = BuyProperties.objects.filter(
                locations__name__icontains=found_location,
                is_property_active=True
            ).values_list('configuration', flat=True).distinct()
            
            if popular_configs:
                configs = [config for config in popular_configs if config]
                response += f"• Popular types: {', '.join(configs[:5])}<br><br>"
            
            return response        
        return None

    def get_amenity_info(self, user_input):
        """Get amenity-based information."""
        amenity_keywords = ['gym', 'pool', 'swimming', 'parking', 'security', 'garden', 'club', 'amenities']

        if any(keyword in user_input.lower() for keyword in amenity_keywords):
            feature_amenities = FeatureAmenity.objects.all()[:10]
            nearby_places = NearbyPlaces.objects.all()[:10]
            
            response = "🏗️ **Available Amenities:**<br><br>"
            
            if feature_amenities:
                response += "**Property Features:**<br><br>"
                for amenity in feature_amenities:
                    response += f"• {amenity.name}<br><br>"
                response += "<br><br>"
            
            if nearby_places:
                response += "**Nearby Places:**<br><br>"
                for place in nearby_places:
                    response += f"• {place.name} ({place.distance_value} {place.distance_unit})<br><br>"
            
            return response
        return None
    
    def get_interior_design_info(self, user_input):
        """Handle interior design queries."""
        interior_keywords = ['interior', 'design', 'decoration', 'turnkey', 'consultancy']
        
        if any(keyword in user_input.lower() for keyword in interior_keywords):
            response = "🎨 **Interior Design Services:**<br><br>"
            response += "We offer professional interior design services:<br><br>"
            response += "**Service Types:**<br><br>"
            response += "• Turn Key Solutions - Complete interior setup<br><br>"
            response += "• Consultancy Services - Design guidance and planning<br><br>"
            response += "**Property Types We Handle:**<br><br>"
            response += "• Flats & Apartments<br><br>"
            response += "• Bungalows<br><br>"
            response += "• Penthouses<br><br>"
            response += "Contact us to discuss your interior design requirements!"
            
            return response
        
        return None

    def get_market_insights(self, user_input):
        """Provide market insights and statistics."""
        insight_keywords = ['market', 'price', 'trend', 'investment', 'roi', 'appreciation']
        
        if any(keyword in user_input.lower() for keyword in insight_keywords):
            total_properties = BuyProperties.objects.filter(is_property_active=True).count()
            locations_count = PropertyLocation.objects.count()
            
            residential_props = BuyProperties.objects.filter(
                property_type='residential',
                is_property_active=True
            )
            
            response = "📊 **Market Insights:**<br><br>"
            response += f"• Total Active Properties: {total_properties}<br><br>"
            response += f"• Locations Covered: {locations_count}<br><br>"
            
            if residential_props.exists():
                avg_area = residential_props.aggregate(avg_area=models.Avg('area'))['avg_area']
                if avg_area:
                    response += f"• Average Property Size: {avg_area:.0f} sq ft<br><br>"
            
            response += "<br>**Investment Tips:**<br><br>"
            response += "• Consider location connectivity and infrastructure<br><br>"
            response += "• Check for upcoming developments in the area<br><br>"
            response += "• Evaluate builder reputation and project completion history<br><br>"
            
            return response
        
        return None

    def get_bot_response(self, user_input):
        """Main method to get bot response."""
        user_input_lower = user_input.lower().strip()
        
        if not self.is_property_related(user_input):
            return self.out_of_concept_response
        
        is_goodbye = any(keyword in user_input_lower for keyword in self.goodbye_keywords)
        if is_goodbye:
            return random.choice(self.goodbye_responses)
        
        is_friendly = any(keyword in user_input_lower for keyword in self.friendly_keywords)
        
        all_locations = PropertyLocation.objects.values_list('name', flat=True)
        found_location = next((loc for loc in all_locations if loc.lower() in user_input_lower), None)
        
        is_property_query = (
            any(bhk in user_input_lower for bhk in self.bhk_types) or
            any(comm in user_input_lower for comm in self.commercial_types) or
            any(status in user_input_lower for status in self.property_statuses) or
            self.extract_budget_range(user_input) or
            self.extract_area_range(user_input) or
            any(keyword in user_input_lower for keyword in ['for sale', 'sell', 'selling', 'owner']) or
            found_location is not None
        )

        if is_friendly and not is_property_query:
            return random.choice(self.friendly_responses)
        
        if any(x in user_input_lower for x in ['hello', 'hi', 'hey', 'start']):
            return (
                "Hi! 👋 I'm HorizonBot, your property assistant.\n\n"
                "I can help you with:\n"
                "🏠 Finding properties (2BHK, 3BHK, villas, commercial)\n"
                "📍 Properties by location\n"
                "💰 Budget-based searches\n"
                "🏢 Commercial properties\n"
                "🎨 Interior design services\n"
                "📊 Market insights\n\n"
                "Try asking: '2BHK in [location] under 50 lakhs' or 'Show me villas in [area]'"
            )
        
        if 'help' in user_input_lower:
            return (
                "🤖 **How to use HorizonBot:**\n\n"
                "**Property Search Examples:**\n"
                "• '2BHK in [location name]'\n"
                "• 'Villas under 2 crores'\n"
                "• 'Commercial office space in [area]'\n"
                "• 'Properties in [location] under 80 lakhs'\n\n"
                "**Other Services:**\n"
                "• Ask about 'interior design'\n"
                "• Get 'market insights'\n"
                "• Browse 'amenities'\n"
                "• Check properties 'for sale by owner'\n"
            )
        
        response = ""
        
        if is_friendly:
            response += random.choice(self.friendly_responses) + "\n\n"
        
        interior_response = self.get_interior_design_info(user_input)
        if interior_response:
            return response + interior_response
        
        amenity_response = self.get_amenity_info(user_input)
        if amenity_response:
            return response + amenity_response
            
        market_response = self.get_market_insights(user_input)
        if market_response:
            return response + market_response
        
        if any(keyword in user_input_lower for keyword in ['for sale', 'sell', 'selling', 'owner']):
            residential_sell = SellResidentialProperties.objects.filter(is_approved=True)
            commercial_sell = SellCommercialProperties.objects.filter(is_approved=True)
            
            if found_location:
                residential_sell = residential_sell.filter(locations__name__icontains=found_location)
                commercial_sell = commercial_sell.filter(locations__name__icontains=found_location)
            
            return response + self.format_sell_property_response(
                list(residential_sell[:3]), 
                list(commercial_sell[:2])
            )
        
        query = Q(is_property_active=True)
        
        found_bhk = next((bhk for bhk in self.bhk_types if bhk in user_input_lower), None)
        if found_bhk:
            query &= Q(configuration=found_bhk)
        
        found_commercial = next((comm for comm in self.commercial_types if comm in user_input_lower), None)
        if found_commercial:
            if found_commercial == 'corporate floor':
                found_commercial = 'corporate_floors'
            query &= Q(commercial_type=found_commercial)
        
        if found_location:
            query &= Q(locations__name__icontains=found_location)
        
        found_status = next((status for status in self.property_statuses if status in user_input_lower), None)
        if found_status:
            query &= Q(status=found_status)
        
        budget_range = self.extract_budget_range(user_input)
        if budget_range:
            if len(budget_range) == 1:
                if 'above' in user_input_lower or 'over' in user_input_lower:
                    query &= Q(min_budget__gte=budget_range[0])
                else:
                    query &= Q(max_budget__lte=budget_range[0])
            elif len(budget_range) == 2:
                query &= Q(min_budget__gte=min(budget_range), max_budget__lte=max(budget_range))
        
        area_range = self.extract_area_range(user_input)
        if area_range:
            if len(area_range) == 1:
                if 'above' in user_input_lower or 'over' in user_input_lower:
                    query &= Q(area__gte=area_range[0])
                else:
                    query &= Q(area__lte=area_range[0])
        
        properties = BuyProperties.objects.filter(query).order_by('-id')
        
        if properties.exists():
            return response + self.format_buy_property_response(properties)
        
        if found_location and not any([found_bhk, found_commercial, budget_range, area_range]):
            location_info = self.get_location_suggestions(user_input)
            if location_info:
                return response + location_info
        
        suggestions = []
        if not found_location:
            suggestions.append("Try specifying a location")
        if not found_bhk and not found_commercial:
            suggestions.append("Mention property type (2BHK, villa, office, etc.)")
        if not budget_range:
            suggestions.append("Add budget range (e.g., 'under 50 lakhs')")
        
        fallback_response = "I couldn't find matching properties. "
        if suggestions:
            fallback_response += "Try: " + ", ".join(suggestions) + ". "
        
        fallback_response += "\n\nExample queries:\n"
        fallback_response += "• '2BHK in [location] under 50 lakhs'\n"
        fallback_response += "• 'Villas in [your area]'\n"
        fallback_response += "• 'Commercial office space for rent'"
        
        return response + fallback_response

def get_bot_response(user_input):
    """Wrapper function to maintain compatibility with existing code."""
    bot = PropertyChatBot()
    return bot.get_bot_response(user_input)
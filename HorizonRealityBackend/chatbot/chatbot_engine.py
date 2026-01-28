import random
import re
from decimal import Decimal
from django.db.models import Q, Avg, Min, Max, Count
from services.models import (
    BuyProperties, PropertyLocation, NearbyPlaces, FeatureAmenity,
    SellResidentialProperties, SellCommercialProperties,
    InteriorDesignRequest, PropertyCalculatorInquiry
)
from django.db import models
from datetime import datetime, timedelta

class EnhancedPropertyChatBot:
    """
    Advanced AI-powered real estate chatbot for Horizon Reality
    Features: Natural language processing, contextual responses, market analytics
    """
    
    def __init__(self):
        # Property Types & Configurations
        self.bhk_types = {
            '1bhk': ['1bhk', '1 bhk', 'one bhk', 'studio'],
            '2bhk': ['2bhk', '2 bhk', 'two bhk'],
            '3bhk': ['3bhk', '3 bhk', 'three bhk'],
            '4bhk': ['4bhk', '4 bhk', 'four bhk'],
            '5bhk': ['5bhk', '5 bhk', 'five bhk', 'luxury apartment'],
            'villa': ['villa', 'villas', 'independent house'],
            'bungalow': ['bungalow', 'bungalows'],
            'duplex': ['duplex', 'duplex house'],
            'tenament': ['tenament', 'row house', 'townhouse']
        }
        
        self.commercial_types = {
            'showroom': ['showroom', 'retail space', 'shop space'],
            'office': ['office', 'office space', 'commercial office'],
            'shop': ['shop', 'retail shop', 'store'],
            'corporate_floors': ['corporate floor', 'corporate floors', 'entire floor']
        }
        
        self.property_statuses = ['new', 'resale', 'rent', 'lease', 'ready to move', 'under construction']
        
        # Advanced keyword categorization
        self.search_keywords = {
            'budget': ['budget', 'under', 'below', 'above', 'between', 'lakhs', 'lakh', 'crore', 'crores', 'price', 'cost'],
            'location': ['in', 'at', 'near', 'around', 'location', 'area', 'locality'],
            'amenities': ['gym', 'pool', 'swimming', 'parking', 'security', 'garden', 'club', 'amenities', 'facilities'],
            'investment': ['investment', 'roi', 'returns', 'appreciation', 'growth', 'rental yield'],
            'urgency': ['urgent', 'immediately', 'asap', 'quick', 'fast', 'soon'],
            'comparison': ['compare', 'vs', 'versus', 'difference', 'better', 'best'],
            'finance': ['loan', 'emi', 'financing', 'mortgage', 'home loan', 'down payment'],
        }
        
        # Corporate greeting responses
        self.greeting_responses = [
            "Welcome to Horizon Reality! 🏠 I'm your dedicated property consultant. How may I assist you in finding your ideal property today?",
            "Good day! I'm the Horizon Reality AI Assistant, here to provide expert guidance on all your real estate needs. What can I help you with?",
            "Hello and welcome! 🌟 As your virtual property advisor at Horizon Reality, I'm here to help you discover exceptional real estate opportunities. How may I assist you?",
            "Greetings from Horizon Reality! I'm your AI-powered property specialist, ready to help you navigate the real estate market. What are you looking for today?",
        ]
        
        # Professional goodbye responses
        self.goodbye_responses = [
            "Thank you for choosing Horizon Reality! 🏠 Our team is available 24/7 to assist you further. For immediate assistance, call us at +91 9104828680. Have a wonderful day!",
            "It's been my pleasure assisting you today. 😊 Should you need any further information, our property experts are just a call away at +91 9104828680. Best regards from Horizon Reality!",
            "Thank you for your time! 🌟 We look forward to helping you find your dream property. For personalized consultation, reach out to us at +91 9104828680. Goodbye!",
            "Goodbye from Horizon Reality! 💼 Remember, we're here whenever you need expert real estate guidance. Connect with us at +91 9104828680 for immediate assistance.",
        ]
        
        self.goodbye_keywords = [
            'bye', 'goodbye', 'good bye', 'see you', 'see ya', 'catch you later', 
            'talk to you later', 'ttyl', 'farewell', 'take care', 'gotta go', 
            'have to go', 'leaving now', 'exit', 'quit', 'thanks bye', 'thank you bye'
        ]
        
        # Out of scope response
        self.out_of_concept_response = (
            "I appreciate your message! However, I specialize in real estate services. 🏠<br><br>"
            "**My Expertise Includes:**<br><br>"
            "🏘️ Residential Properties (1BHK to 5BHK, Villas, Bungalows)<br>"
            "🏢 Commercial Spaces (Offices, Showrooms, Retail)<br>"
            "💰 Investment Consultation & Market Analysis<br>"
            "📊 Budget Planning & Financial Guidance<br>"
            "🎨 Interior Design Services<br>"
            "📍 Location-based Property Search<br><br>"
            "**Try asking:**<br>"
            "• '3BHK apartment in Bopal under 80 lakhs'<br>"
            "• 'Commercial office space near SG Highway'<br>"
            "• 'Investment properties with good ROI'<br>"
            "• 'What are the market trends in Ahmedabad?'<br><br>"
            "How may I assist you with your real estate needs?"
        )
        
        # Service offerings
        self.services = {
            'interior_design': {
                'keywords': ['interior', 'design', 'decoration', 'turnkey', 'consultancy', 'furnish', 'decor'],
                'response': self._get_interior_design_response
            },
            'legal_services': {
                'keywords': ['legal', 'documentation', 'paperwork', 'registration', 'lawyer', 'advocate'],
                'response': self._get_legal_services_response
            },
            'vastu': {
                'keywords': ['vastu', 'vastu shastra', 'direction', 'feng shui'],
                'response': self._get_vastu_response
            },
            'loan': {
                'keywords': ['loan', 'emi', 'financing', 'mortgage', 'home loan', 'bank'],
                'response': self._get_loan_assistance_response
            }
        }

    def is_property_related(self, user_input):
        """Enhanced check for property-related queries with better context understanding."""
        user_input_lower = user_input.lower()
        
        # Check greetings
        greeting_keywords = ['hello', 'hi', 'hey', 'start', 'help', 'good morning', 'good afternoon', 'good evening']
        if any(keyword in user_input_lower for keyword in greeting_keywords):
            return True
        
        # Check goodbyes
        if any(keyword in user_input_lower for keyword in self.goodbye_keywords):
            return True
        
        # Check all property types
        for bhk_variations in self.bhk_types.values():
            if any(variation in user_input_lower for variation in bhk_variations):
                return True
        
        for comm_variations in self.commercial_types.values():
            if any(variation in user_input_lower for variation in comm_variations):
                return True
        
        # Check search keywords
        for keyword_category in self.search_keywords.values():
            if any(keyword in user_input_lower for keyword in keyword_category):
                return True
        
        # Check services
        for service_data in self.services.values():
            if any(keyword in user_input_lower for keyword in service_data['keywords']):
                return True
        
        # Check property statuses
        if any(status in user_input_lower for status in self.property_statuses):
            return True
        
        # Check locations
        all_locations = PropertyLocation.objects.values_list('name', flat=True)
        if any(location.lower() in user_input_lower for location in all_locations):
            return True
        
        # Check numeric patterns (likely budget or area)
        if re.search(r'\d+', user_input):
            return True
        
        return False

    def extract_configuration(self, user_input):
        """Extract property configuration with enhanced pattern matching."""
        user_input_lower = user_input.lower()
        
        for config, variations in self.bhk_types.items():
            if any(variation in user_input_lower for variation in variations):
                return config
        
        return None

    def extract_commercial_type(self, user_input):
        """Extract commercial property type."""
        user_input_lower = user_input.lower()
        
        for comm_type, variations in self.commercial_types.items():
            if any(variation in user_input_lower for variation in variations):
                return comm_type
        
        return None

    def extract_budget_range(self, user_input):
        """Advanced budget extraction with support for ranges and comparisons."""
        budget_pattern = r'(\d+(?:\.\d+)?)\s*(lakh|lakhs|crore|crores|L|Cr)'
        matches = re.findall(budget_pattern, user_input.lower())
        
        budgets = []
        for amount, unit in matches:
            amount = float(amount)
            if 'crore' in unit.lower() or 'cr' in unit.lower():
                amount = amount * 100  # Convert to lakhs
            budgets.append(amount)
        
        return budgets if budgets else None
    
    def extract_area_range(self, user_input):
        """Extract area information with multiple unit support."""
        area_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:sq\s*ft|sqft|square\s*feet|sq\.ft)',
            r'(\d+(?:\.\d+)?)\s*(?:sq\s*yards|sqyards|square\s*yards)',
            r'(\d+(?:\.\d+)?)\s*(?:sq\s*m|sqm|square\s*meters)',
        ]
        
        for pattern in area_patterns:
            matches = re.findall(pattern, user_input.lower())
            if matches:
                return [float(match) for match in matches]
        return None

    def extract_location(self, user_input):
        """Extract location from user input."""
        all_locations = PropertyLocation.objects.values_list('name', flat=True)
        user_input_lower = user_input.lower()
        
        for location in all_locations:
            if location.lower() in user_input_lower:
                return location
        
        return None

    def format_property_card(self, prop, index=1):
        """Format a single property with professional styling."""
        budget_range = f"₹{int(prop.min_budget)}-{int(prop.max_budget)} {prop.min_budget_unit.title()}"
        
        config_display = prop.configuration.upper() if prop.configuration else prop.commercial_type.replace('_', ' ').title()
        
        property_url = f"/property/{prop.slug}/"
        
        card = f"**🏠 Property #{index}: {prop.project_name}**<br><br>"
        card += f"📍 **Location:** {prop.locations.name}<br>"
        card += f"🏗️ **Type:** {config_display}<br>"
        card += f"📐 **Carpet Area:** {prop.area} sq ft<br>"
        card += f"💰 **Budget Range:** {budget_range}<br>"
        
        if prop.status:
            status_display = prop.status.replace('_', ' ').title()
            card += f"📅 **Status:** {status_display}<br>"
        
        # Add key amenities if available
        if hasattr(prop, 'feature_amenities') and prop.feature_amenities.exists():
            amenities = list(prop.feature_amenities.values_list('name', flat=True))[:3]
            if amenities:
                card += f"✨ **Amenities:** {', '.join(amenities)}<br>"
        
        card += f'<br>🔗 <a href="{property_url}" target="_blank" class="property-link">View Complete Details →</a><br><br>'
        card += "─────────────────────<br><br>"
        
        return card

    def format_buy_property_response(self, properties, query_context=None):
        """Enhanced property response with analytics and recommendations."""
        if not properties.exists():
            return self._get_no_results_response(query_context)

        count = properties.count()
        response = f"**🎯 Perfect! I found {count} propert{'y' if count == 1 else 'ies'} matching your requirements:**<br><br>"
        
        # Add quick stats
        if count > 1:
            avg_price = properties.aggregate(
                avg_min=Avg('min_budget'),
                avg_max=Avg('max_budget')
            )
            if avg_price['avg_min']:
                response += f"💡 **Average Budget Range:** ₹{avg_price['avg_min']:.1f}-{avg_price['avg_max']:.1f} Lakhs<br><br>"
        
        # Display properties (limit to top 5)
        display_limit = min(5, count)
        for idx, prop in enumerate(properties[:display_limit], 1):
            response += self.format_property_card(prop, idx)
        
        if count > display_limit:
            response += f"<br>**📊 Plus {count - display_limit} more properties available!**<br><br>"
            response += "💬 Narrow your search by specifying:<br>"
            response += "• Budget range (e.g., 'under 70 lakhs')<br>"
            response += "• Specific amenities (e.g., 'with swimming pool')<br>"
            response += "• Property status (e.g., 'ready to move')<br><br>"
        
        # Add personalized recommendations
        response += self._get_personalized_suggestions(properties, query_context)
        
        # Call to action
        response += "<br>**📞 Need Expert Assistance?**<br>"
        response += "Connect with our property consultants: **+91 9104828680**<br>"
        response += "Available Mon-Sat, 9 AM - 8 PM<br>"
        
        return response.strip()

    def _get_no_results_response(self, query_context):
        """Professional no results response with alternatives."""
        response = "**🔍 No Exact Matches Found**<br><br>"
        response += "I couldn't find properties matching your exact criteria. However, let me help you:<br><br>"
        
        response += "**💡 Suggestions:**<br><br>"
        response += "1️⃣ **Adjust Your Search:**<br>"
        response += "   • Try a broader budget range<br>"
        response += "   • Consider nearby locations<br>"
        response += "   • Explore similar property types<br><br>"
        
        response += "2️⃣ **Popular Alternatives:**<br>"
        
        # Get similar properties
        similar_props = BuyProperties.objects.filter(
            is_property_active=True
        ).order_by('-id')[:3]
        
        if similar_props.exists():
            response += "   Here are some trending properties:<br><br>"
            for idx, prop in enumerate(similar_props, 1):
                response += f"   • {prop.project_name} - {prop.locations.name} ({prop.configuration or prop.commercial_type})<br>"
        
        response += "<br>3️⃣ **Talk to Our Experts:**<br>"
        response += "   📞 Call: +91 9104828680<br>"
        response += "   Our consultants can help you find the perfect property!<br><br>"
        
        response += "**Try searching like:**<br>"
        response += "• '2BHK in Bopal under 60 lakhs'<br>"
        response += "• 'Ready to move villas in Thaltej'<br>"
        response += "• 'Commercial office space near SG Highway'<br>"
        
        return response

    def _get_personalized_suggestions(self, properties, query_context):
        """Generate personalized property suggestions."""
        suggestions = "<br>**🎯 Personalized Recommendations:**<br><br>"
        
        # Analyze property features
        has_new = properties.filter(status='new').exists()
        has_resale = properties.filter(status='resale').exists()
        
        if has_new and has_resale:
            suggestions += "💡 Mix of new launches and resale options available<br>"
        elif has_new:
            suggestions += "⭐ These are brand new properties with modern amenities<br>"
        elif has_resale:
            suggestions += "🏠 Ready-to-move resale properties - immediate possession<br>"
        
        # Location insights
        locations = properties.values('locations__name').annotate(
            count=Count('id')
        ).order_by('-count')[:3]
        
        if locations:
            suggestions += f"📍 Popular areas: {', '.join([loc['locations__name'] for loc in locations])}<br>"
        
        return suggestions

    def _get_interior_design_response(self):
        """Professional interior design service response."""
        response = "**🎨 Interior Design & Turnkey Solutions**<br><br>"
        response += "Transform your property into a dream space with Horizon Reality's comprehensive interior design services!<br><br>"
        
        response += "**📋 Our Services:**<br><br>"
        response += "**1. Design Consultancy**<br>"
        response += "   • Space planning & layout optimization<br>"
        response += "   • 3D visualization & mood boards<br>"
        response += "   • Material selection guidance<br>"
        response += "   • Budget planning & cost estimation<br><br>"
        
        response += "**2. Turnkey Solutions**<br>"
        response += "   • Complete project execution<br>"
        response += "   • Modular kitchen & wardrobes<br>"
        response += "   • Flooring & ceiling work<br>"
        response += "   • Furniture & fixtures<br>"
        response += "   • Electrical & plumbing<br><br>"
        
        response += "**3. Property Types We Handle:**<br>"
        response += "   🏠 Apartments & Flats<br>"
        response += "   🏡 Villas & Bungalows<br>"
        response += "   🏢 Office Spaces<br>"
        response += "   🏬 Commercial Properties<br><br>"
        
        response += "**✨ Why Choose Us?**<br>"
        response += "• Experienced design team<br>"
        response += "• Quality materials & craftsmanship<br>"
        response += "• On-time project delivery<br>"
        response += "• Competitive pricing<br>"
        response += "• End-to-end solutions<br><br>"
        
        response += "**📞 Get a Free Consultation:**<br>"
        response += "Contact: +91 9104828680<br>"
        response += "Let's bring your vision to life! 🌟"
        
        return response

    def _get_legal_services_response(self):
        """Legal documentation service response."""
        response = "**⚖️ Legal Documentation & Support Services**<br><br>"
        response += "Navigate property transactions smoothly with expert legal assistance from Horizon Reality!<br><br>"
        
        response += "**📋 Our Legal Services:**<br><br>"
        response += "**1. Property Documentation**<br>"
        response += "   • Sale deed preparation & review<br>"
        response += "   • Agreement drafting<br>"
        response += "   • Title verification<br>"
        response += "   • Encumbrance certificate check<br><br>"
        
        response += "**2. Registration Services**<br>"
        response += "   • Property registration assistance<br>"
        response += "   • Stamp duty calculation<br>"
        response += "   • Sub-registrar office liaison<br><br>"
        
        response += "**3. Legal Advisory**<br>"
        response += "   • Property law consultation<br>"
        response += "   • RERA compliance check<br>"
        response += "   • Dispute resolution support<br><br>"
        
        response += "**✅ We Ensure:**<br>"
        response += "• Complete documentation transparency<br>"
        response += "• Legal compliance & safety<br>"
        response += "• Protection of your interests<br>"
        response += "• Smooth transaction process<br><br>"
        
        response += "**📞 Consult Our Legal Experts:**<br>"
        response += "Call: +91 9104828680<br>"
        response += "Secure your property investment with proper legal guidance!"
        
        return response

    def _get_vastu_response(self):
        """Vastu consultation service response."""
        response = "**🧭 Vastu Shastra Consultation Services**<br><br>"
        response += "Harmonize your living space with ancient wisdom! Horizon Reality offers expert Vastu guidance.<br><br>"
        
        response += "**📋 Vastu Services:**<br><br>"
        response += "**1. Pre-Purchase Consultation**<br>"
        response += "   • Property direction analysis<br>"
        response += "   • Plot evaluation<br>"
        response += "   • Construction timing guidance<br><br>"
        
        response += "**2. Interior Vastu Planning**<br>"
        response += "   • Room placement optimization<br>"
        response += "   • Furniture positioning<br>"
        response += "   • Color recommendations<br>"
        response += "   • Entrance & main door guidance<br><br>"
        
        response += "**3. Vastu Remedies**<br>"
        response += "   • Defect identification<br>"
        response += "   • Correction solutions<br>"
        response += "   • Energy balancing tips<br><br>"
        
        response += "**🌟 Benefits:**<br>"
        response += "• Enhanced positive energy<br>"
        response += "• Improved health & prosperity<br>"
        response += "• Better work-life balance<br>"
        response += "• Peaceful living environment<br><br>"
        
        response += "**📞 Book Vastu Consultation:**<br>"
        response += "Contact: +91 9104828680<br>"
        response += "Align your property with positive cosmic energies!"
        
        return response

    def _get_loan_assistance_response(self):
        """Home loan assistance response."""
        response = "**💳 Home Loan & Financing Assistance**<br><br>"
        response += "Make your dream home affordable with our comprehensive financing support!<br><br>"
        
        response += "**🏦 Our Loan Services:**<br><br>"
        response += "**1. Loan Facilitation**<br>"
        response += "   • Partnership with leading banks & NBFCs<br>"
        response += "   • Competitive interest rates<br>"
        response += "   • Quick approval process<br>"
        response += "   • Flexible repayment options<br><br>"
        
        response += "**2. Financial Planning**<br>"
        response += "   • EMI calculations<br>"
        response += "   • Eligibility assessment<br>"
        response += "   • Down payment planning<br>"
        response += "   • Tax benefit guidance<br><br>"
        
        response += "**3. Documentation Support**<br>"
        response += "   • Loan application assistance<br>"
        response += "   • Document verification<br>"
        response += "   • Processing follow-up<br><br>"
        
        response += "**💰 Loan Features:**<br>"
        response += "• Up to 90% property financing<br>"
        response += "• Tenure up to 30 years<br>"
        response += "• Minimal processing time<br>"
        response += "• Balance transfer options<br><br>"
        
        response += "**📞 Discuss Your Financing Needs:**<br>"
        response += "Contact: +91 9104828680<br>"
        response += "Let's make homeownership easier for you!"
        
        return response

    def get_market_insights(self, user_input):
        """Advanced market insights and analytics."""
        response = "**📊 Ahmedabad Real Estate Market Insights**<br><br>"
        
        # Get statistics
        total_props = BuyProperties.objects.filter(is_property_active=True).count()
        locations_count = PropertyLocation.objects.count()
        
        response += f"**📈 Market Overview:**<br>"
        response += f"• Active Listings: {total_props} properties<br>"
        response += f"• Coverage: {locations_count} prime locations<br><br>"
        
        # Configuration distribution
        config_dist = BuyProperties.objects.filter(
            is_property_active=True,
            property_type='residential'
        ).values('configuration').annotate(count=Count('id')).order_by('-count')[:5]
        
        if config_dist:
            response += "**🏠 Popular Configurations:**<br>"
            for item in config_dist:
                if item['configuration']:
                    response += f"• {item['configuration'].upper()}: {item['count']} listings<br>"
            response += "<br>"
        
        # Budget analysis
        residential = BuyProperties.objects.filter(
            is_property_active=True,
            property_type='residential'
        )
        
        if residential.exists():
            avg_budget = residential.aggregate(
                avg_min=Avg('min_budget'),
                avg_max=Avg('max_budget'),
                min_price=Min('min_budget'),
                max_price=Max('max_budget')
            )
            
            response += "**💰 Budget Trends (Residential):**<br>"
            response += f"• Average Range: ₹{avg_budget['avg_min']:.1f} - {avg_budget['avg_max']:.1f} Lakhs<br>"
            response += f"• Entry Level: ₹{avg_budget['min_price']:.1f} Lakhs onwards<br>"
            response += f"• Premium: Up to ₹{avg_budget['max_price']:.1f} Lakhs<br><br>"
        
        # Hot locations
        hot_locations = BuyProperties.objects.filter(
            is_property_active=True
        ).values('locations__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        if hot_locations:
            response += "**🔥 Trending Locations:**<br>"
            for loc in hot_locations:
                response += f"• {loc['locations__name']}: {loc['count']} properties<br>"
            response += "<br>"
        
        # Investment insights
        response += "**💡 Investment Tips:**<br>"
        response += "• Focus on areas with upcoming metro connectivity<br>"
        response += "• Consider properties near IT hubs for better ROI<br>"
        response += "• Verify RERA registration before investing<br>"
        response += "• Assess builder's track record & reputation<br>"
        response += "• Check for social infrastructure development<br><br>"
        
        response += "**📞 Need Personalized Investment Advice?**<br>"
        response += "Call our property experts: +91 9104828680"
        
        return response

    def search_properties(self, user_input):
        """Advanced property search with NLP capabilities."""
        query = Q(is_property_active=True)
        query_context = {}
        
        # Extract configuration
        config = self.extract_configuration(user_input)
        if config:
            query &= Q(configuration=config)
            query_context['configuration'] = config
        
        # Extract commercial type
        comm_type = self.extract_commercial_type(user_input)
        if comm_type:
            query &= Q(commercial_type=comm_type)
            query_context['commercial_type'] = comm_type
        
        # Extract location
        location = self.extract_location(user_input)
        if location:
            query &= Q(locations__name__icontains=location)
            query_context['location'] = location
        
        # Extract budget
        budgets = self.extract_budget_range(user_input)
        if budgets:
            if 'above' in user_input.lower() or 'more than' in user_input.lower():
                query &= Q(min_budget__gte=budgets[0])
            elif 'below' in user_input.lower() or 'under' in user_input.lower():
                query &= Q(max_budget__lte=budgets[0])
            elif len(budgets) == 2:
                query &= Q(min_budget__gte=min(budgets), max_budget__lte=max(budgets))
            else:
                query &= Q(max_budget__lte=budgets[0])
            query_context['budget'] = budgets
        
        # Extract area
        areas = self.extract_area_range(user_input)
        if areas:
            if 'above' in user_input.lower() or 'more than' in user_input.lower():
                query &= Q(area__gte=areas[0])
            else:
                query &= Q(area__lte=areas[0])
            query_context['area'] = areas
        
        # Status filter
        for status in self.property_statuses:
            if status in user_input.lower():
                query &= Q(status=status.replace(' ', '_'))
                query_context['status'] = status
                break
        
        # Execute search
        properties = BuyProperties.objects.filter(query).order_by('-id')
        
        return properties, query_context

    def get_bot_response(self, user_input):
        """Main response handler with advanced routing."""
        user_input_lower = user_input.lower().strip()
        
        # Check if property-related
        if not self.is_property_related(user_input):
            return self.out_of_concept_response
        
        # Handle goodbye
        if any(keyword in user_input_lower for keyword in self.goodbye_keywords):
            return random.choice(self.goodbye_responses)
        
        # Handle greetings
        greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(keyword in user_input_lower for keyword in greeting_keywords) and len(user_input.split()) <= 3:
            return random.choice(self.greeting_responses)
        
        # Handle help
        if 'help' in user_input_lower and len(user_input.split()) <= 2:
            return self._get_help_response()
        
        # Check for specific services
        for service_name, service_data in self.services.items():
            if any(keyword in user_input_lower for keyword in service_data['keywords']):
                return service_data['response']()
        
        # Market insights
        if any(word in user_input_lower for word in ['market', 'trend', 'insight', 'analysis', 'statistics']):
            return self.get_market_insights(user_input)
        
        # Amenities info
        if any(word in user_input_lower for word in self.search_keywords['amenities']):
            return self._get_amenities_info()
        
        # Property search
        properties, query_context = self.search_properties(user_input)
        
        if properties.exists():
            return self.format_buy_property_response(properties, query_context)
        
        # No results - provide helpful alternatives
        return self._get_no_results_response(query_context)

    def _get_help_response(self):
        """Comprehensive help guide."""
        response = "**🤖 HorizonBot - Your AI Property Assistant**<br><br>"
        response += "I'm here to help you find the perfect property! Here's how to use me effectively:<br><br>"
        
        response += "**🔍 Property Search Examples:**<br><br>"
        response += "**By Configuration:**<br>"
        response += "• '2BHK apartments in Bopal'<br>"
        response += "• 'Villas under 2 crores'<br>"
        response += "• '3BHK ready to move'<br><br>"
        
        response += "**By Budget:**<br>"
        response += "• 'Properties under 50 lakhs'<br>"
        response += "• 'Flats between 60-80 lakhs in Thaltej'<br>"
        response += "• 'Commercial space under 1 crore'<br><br>"
        
        response += "**By Location:**<br>"
        response += "• 'Properties in SG Highway area'<br>"
        response += "• 'Apartments near Science City'<br>"
        response += "• 'Houses in Satellite'<br><br>"
        
        response += "**🛠️ Other Services:**<br>"
        response += "• 'Interior design services'<br>"
        response += "• 'Home loan assistance'<br>"
        response += "• 'Vastu consultation'<br>"
        response += "• 'Legal documentation help'<br>"
        response += "• 'Market trends and insights'<br><br>"
        
        response += "**💡 Pro Tips:**<br>"
        response += "• Be specific about your requirements<br>"
        response += "• Mention budget range for better results<br>"
        response += "• Specify preferred locations<br>"
        response += "• Ask about amenities you need<br><br>"
        
        response += "**📞 Need Personal Assistance?**<br>"
        response += "Our experts are available at: +91 9104828680<br>"
        response += "Mon-Sat, 9 AM - 8 PM"
        
        return response

    def _get_amenities_info(self):
        """Detailed amenities information."""
        response = "**✨ Premium Amenities & Facilities**<br><br>"
        response += "Properties in our portfolio offer world-class amenities:<br><br>"
        
        # Get actual amenities from database
        amenities = FeatureAmenity.objects.all()[:15]
        
        if amenities:
            response += "**🏗️ Standard Features:**<br>"
            categories = {}
            for amenity in amenities:
                # Simple categorization
                name_lower = amenity.name.lower()
                if any(x in name_lower for x in ['gym', 'pool', 'club', 'sports']):
                    category = 'Recreation'
                elif any(x in name_lower for x in ['security', 'cctv', 'guard']):
                    category = 'Security'
                elif any(x in name_lower for x in ['parking', 'lift', 'power']):
                    category = 'Essential'
                else:
                    category = 'Lifestyle'
                
                if category not in categories:
                    categories[category] = []
                categories[category].append(amenity.name)
            
            for category, items in categories.items():
                response += f"<br>**{category}:**<br>"
                for item in items[:5]:
                    response += f"• {item}<br>"
        
        # Nearby places
        nearby = NearbyPlaces.objects.all()[:10]
        if nearby:
            response += "<br>**📍 Nearby Conveniences:**<br>"
            for place in nearby:
                response += f"• {place.name} - {place.distance_value} {place.distance_unit} away<br>"
        
        response += "<br>**💡 Note:** Amenities vary by property. Check individual listings for specific details.<br><br>"
        response += "**📞 Want to know more?** Call: +91 9104828680"
        
        return response


def get_bot_response(user_input):
    """Main entry point for chatbot responses."""
    bot = EnhancedPropertyChatBot()
    return bot.get_bot_response(user_input)
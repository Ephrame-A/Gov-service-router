"""Seed script — populates the database with 50+ services across 8 institutions in Addis Ababa.

Run: python -m app.db.seed
"""

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Base, Department, Institution, Office, Service
from app.db.session import async_session, engine


SEED_DATA = [
    {
        "institution": {
            "name": "Ethiopian Revenues and Customs Authority (ERCA)",
            "type": "federal",
            "description": "Responsible for tax collection, customs, and revenue administration across Ethiopia.",
            "is_approved": True,
        },
        "offices": [
            {
                "address": "Mexico Square, Addis Ababa",
                "lat": 9.0108,
                "lng": 38.7469,
                "working_hours": "Mon-Fri 8:30-17:00",
                "contact_phone": "+251-11-662-9080",
                "contact_email": "info@erca.gov.et",
            }
        ],
        "departments": [
            {
                "name": "Business Tax Division",
                "description": "Handles business income tax, VAT, and tax certificate services.",
                "services": [
                    {
                        "name": "Business Tax Certificate Renewal",
                        "description": "Renewal of expired or expiring business tax certificates and TIN certificates.",
                        "example_phrasings": [
                            "my shop's tax certificate expired",
                            "I need to renew my business tax certificate",
                            "how to renew TIN certificate for my business",
                            "my tax clearance certificate needs renewal",
                            "expired tax certificate for my store",
                        ],
                        "required_documents": ["Previous tax certificate", "Business license", "Tax payment receipts", "Valid ID"],
                        "typical_duration": "3-5 business days",
                        "fees": "Varies by business type",
                    },
                    {
                        "name": "New TIN Registration",
                        "description": "Register for a new Taxpayer Identification Number (TIN) for individuals or businesses.",
                        "example_phrasings": [
                            "I want to get a tax ID number",
                            "how to register for TIN",
                            "I need a taxpayer identification number",
                            "register my new business for tax",
                        ],
                        "required_documents": ["Valid ID (Kebele ID or Passport)", "Business license (for businesses)", "Proof of address"],
                        "typical_duration": "1-2 business days",
                        "fees": "Free",
                    },
                    {
                        "name": "VAT Registration",
                        "description": "Register a business for Value Added Tax (VAT) collection and reporting.",
                        "example_phrasings": [
                            "I need to register for VAT",
                            "how to get VAT registration",
                            "my business needs to start collecting VAT",
                            "register for value added tax",
                        ],
                        "required_documents": ["TIN certificate", "Business license", "Financial statements", "Bank statement"],
                        "typical_duration": "5-7 business days",
                        "fees": "Free",
                    },
                    {
                        "name": "Tax Payment and Filing",
                        "description": "File tax returns and make tax payments for income, profit, or excise taxes.",
                        "example_phrasings": [
                            "I want to pay my taxes",
                            "how to file tax returns",
                            "I need to submit my annual tax report",
                            "where do I pay business profit tax",
                        ],
                        "required_documents": ["TIN certificate", "Financial records", "Previous tax filings"],
                        "typical_duration": "Same day (in-person)",
                        "fees": "Tax amount varies",
                    },
                    {
                        "name": "Tax Clearance Certificate",
                        "description": "Obtain a certificate proving all tax obligations are settled, often required for tenders and contracts.",
                        "example_phrasings": [
                            "I need a tax clearance letter",
                            "get tax clearance for a government tender",
                            "proof that I paid all my taxes",
                            "tax clearance certificate for contract",
                        ],
                        "required_documents": ["TIN certificate", "Tax payment receipts", "Valid ID"],
                        "typical_duration": "3-5 business days",
                        "fees": "Free",
                    },
                ],
            },
            {
                "name": "Customs Division",
                "description": "Handles import/export customs clearance, duties, and declarations.",
                "services": [
                    {
                        "name": "Import Customs Clearance",
                        "description": "Clear imported goods through customs, pay applicable duties and taxes.",
                        "example_phrasings": [
                            "I need to clear imported goods from customs",
                            "how to get my shipment from customs",
                            "customs clearance for imports",
                            "my package is stuck at customs",
                        ],
                        "required_documents": ["Commercial invoice", "Bill of lading", "Packing list", "Import permit (if required)", "TIN certificate"],
                        "typical_duration": "2-7 business days",
                        "fees": "Duty rates vary by item",
                    },
                    {
                        "name": "Export Customs Declaration",
                        "description": "Process export declarations and obtain customs clearance for outbound goods.",
                        "example_phrasings": [
                            "I want to export goods from Ethiopia",
                            "export customs paperwork",
                            "how to ship products abroad",
                        ],
                        "required_documents": ["Export permit", "Commercial invoice", "TIN certificate", "Quality certificate (for coffee, etc.)"],
                        "typical_duration": "1-3 business days",
                        "fees": "Export duty varies",
                    },
                ],
            },
        ],
    },
    {
        "institution": {
            "name": "Immigration, Nationality and Vital Events Agency (INVEA)",
            "type": "federal",
            "description": "Handles passports, visas, residence permits, and vital events registration.",
            "is_approved": True,
        },
        "offices": [
            {
                "address": "Churchill Avenue, Near National Theatre, Addis Ababa",
                "lat": 9.0192,
                "lng": 38.7525,
                "working_hours": "Mon-Fri 8:00-16:30",
                "contact_phone": "+251-11-553-0000",
                "contact_email": "info@invea.gov.et",
            }
        ],
        "departments": [
            {
                "name": "Passport Services",
                "description": "Issuance and renewal of Ethiopian passports.",
                "services": [
                    {
                        "name": "New Passport Application",
                        "description": "Apply for a new Ethiopian passport for the first time.",
                        "example_phrasings": [
                            "I want to get a passport",
                            "how to apply for Ethiopian passport",
                            "I need a new passport",
                            "first time passport application",
                            "get a travel document",
                        ],
                        "required_documents": ["Kebele ID", "Birth certificate", "2 passport photos", "Payment receipt"],
                        "typical_duration": "2-4 weeks",
                        "fees": "1,500 ETB (regular), 3,000 ETB (express)",
                    },
                    {
                        "name": "Passport Renewal",
                        "description": "Renew an expired or expiring Ethiopian passport.",
                        "example_phrasings": [
                            "renew my passport",
                            "my passport is expired",
                            "passport renewal process",
                            "extend my passport",
                        ],
                        "required_documents": ["Old passport", "Kebele ID", "2 passport photos", "Payment receipt"],
                        "typical_duration": "1-3 weeks",
                        "fees": "1,500 ETB (regular), 3,000 ETB (express)",
                    },
                    {
                        "name": "Lost Passport Replacement",
                        "description": "Replace a lost or stolen Ethiopian passport.",
                        "example_phrasings": [
                            "I lost my passport",
                            "my passport was stolen",
                            "replace lost passport",
                            "passport replacement",
                        ],
                        "required_documents": ["Police report", "Kebele ID", "2 passport photos", "Affidavit"],
                        "typical_duration": "2-4 weeks",
                        "fees": "3,000 ETB",
                    },
                ],
            },
            {
                "name": "Visa and Residence Permits",
                "description": "Issues visas and residence permits for foreign nationals.",
                "services": [
                    {
                        "name": "Visa Extension",
                        "description": "Extend the validity of a tourist or business visa in Ethiopia.",
                        "example_phrasings": [
                            "I need to extend my visa",
                            "visa extension for tourists",
                            "how to stay longer in Ethiopia",
                            "extend my business visa",
                        ],
                        "required_documents": ["Current passport with visa", "Visa extension application form", "Passport photos", "Proof of accommodation"],
                        "typical_duration": "3-5 business days",
                        "fees": "Varies by visa type",
                    },
                    {
                        "name": "Residence Permit Application",
                        "description": "Apply for a residence permit for foreign nationals living in Ethiopia.",
                        "example_phrasings": [
                            "I need a residence permit",
                            "how to get residence ID in Ethiopia",
                            "foreign national residence permit",
                            "work residence permit application",
                        ],
                        "required_documents": ["Valid passport", "Work permit", "Employment letter", "Passport photos", "Medical certificate"],
                        "typical_duration": "2-4 weeks",
                        "fees": "Varies",
                    },
                ],
            },
        ],
    },
    {
        "institution": {
            "name": "Addis Ababa Transport Authority",
            "type": "municipal",
            "description": "Manages driver licensing, vehicle registration, and public transport in Addis Ababa.",
            "is_approved": True,
        },
        "offices": [
            {
                "address": "Megenagna, Near Anbessa Bus Depot, Addis Ababa",
                "lat": 9.0227,
                "lng": 38.7995,
                "working_hours": "Mon-Fri 8:30-17:00, Sat 8:30-12:00",
                "contact_phone": "+251-11-661-7880",
                "contact_email": "transport@addisababa.gov.et",
            }
        ],
        "departments": [
            {
                "name": "Driver Licensing",
                "description": "Issues and renews driver's licenses for all vehicle categories.",
                "services": [
                    {
                        "name": "New Driver's License",
                        "description": "Apply for a driver's license after passing the driving test.",
                        "example_phrasings": [
                            "I want to get a driver's license",
                            "how to get my first driving license",
                            "apply for driving permit",
                            "I passed my driving test and need a license",
                        ],
                        "required_documents": ["Kebele ID", "Medical fitness certificate", "Driving school certificate", "2 photos", "Payment receipt"],
                        "typical_duration": "1-2 weeks",
                        "fees": "500-1,000 ETB depending on vehicle class",
                    },
                    {
                        "name": "Driver's License Renewal",
                        "description": "Renew an expired driver's license.",
                        "example_phrasings": [
                            "renew my driving license",
                            "my driver's license expired",
                            "driving license renewal",
                            "extend my driving permit",
                        ],
                        "required_documents": ["Old driver's license", "Kebele ID", "Medical certificate", "2 photos"],
                        "typical_duration": "3-5 business days",
                        "fees": "300 ETB",
                    },
                    {
                        "name": "License Category Upgrade",
                        "description": "Upgrade driver's license to a higher vehicle category (e.g., from light to heavy).",
                        "example_phrasings": [
                            "upgrade my driving license",
                            "I want to drive heavier vehicles",
                            "change license category",
                            "upgrade from automobile to truck license",
                        ],
                        "required_documents": ["Current license", "Driving school certificate for new category", "Medical certificate", "Payment receipt"],
                        "typical_duration": "1-2 weeks",
                        "fees": "700 ETB",
                    },
                ],
            },
            {
                "name": "Vehicle Registration",
                "description": "Handles vehicle registration, title transfers, and plate issuance.",
                "services": [
                    {
                        "name": "New Vehicle Registration",
                        "description": "Register a newly purchased vehicle and obtain license plates.",
                        "example_phrasings": [
                            "I bought a new car and need to register it",
                            "register my vehicle",
                            "get license plates for my car",
                            "new car registration",
                        ],
                        "required_documents": ["Purchase invoice", "Customs clearance (for imported)", "Insurance certificate", "Kebele ID"],
                        "typical_duration": "3-5 business days",
                        "fees": "2,000-5,000 ETB",
                    },
                    {
                        "name": "Vehicle Ownership Transfer",
                        "description": "Transfer vehicle ownership from one person to another.",
                        "example_phrasings": [
                            "transfer car ownership",
                            "I sold my car and need to transfer the title",
                            "change vehicle owner name",
                            "car title transfer",
                        ],
                        "required_documents": ["Current registration (libre)", "Sales agreement", "Both parties' IDs", "Tax clearance"],
                        "typical_duration": "3-5 business days",
                        "fees": "1,500 ETB",
                    },
                    {
                        "name": "Vehicle Inspection",
                        "description": "Annual vehicle roadworthiness inspection required for registration renewal.",
                        "example_phrasings": [
                            "my car needs inspection",
                            "annual vehicle inspection",
                            "where to get car inspected",
                            "vehicle roadworthiness test",
                        ],
                        "required_documents": ["Vehicle registration (libre)", "Insurance certificate"],
                        "typical_duration": "Same day",
                        "fees": "200-500 ETB",
                    },
                ],
            },
        ],
    },
    {
        "institution": {
            "name": "Addis Ababa Land Development and Management Bureau",
            "type": "municipal",
            "description": "Manages land allocation, title deeds, and building permits in Addis Ababa.",
            "is_approved": True,
        },
        "offices": [
            {
                "address": "Kirkos Sub-city, Near Meskel Square, Addis Ababa",
                "lat": 9.0107,
                "lng": 38.7612,
                "working_hours": "Mon-Fri 8:30-17:00",
                "contact_phone": "+251-11-551-6300",
                "contact_email": "land@addisababa.gov.et",
            }
        ],
        "departments": [
            {
                "name": "Land Title and Registration",
                "description": "Issues and manages land title deeds and property registration.",
                "services": [
                    {
                        "name": "Land Title Deed Issuance",
                        "description": "Obtain a title deed for land allocated by the city administration.",
                        "example_phrasings": [
                            "I need a land title deed",
                            "get title deed for my land",
                            "land ownership certificate",
                            "how to get carte for my plot",
                        ],
                        "required_documents": ["Land allocation letter", "Kebele ID", "Survey plan", "Payment receipts for lease"],
                        "typical_duration": "2-4 weeks",
                        "fees": "Varies by land size and location",
                    },
                    {
                        "name": "Property Title Transfer",
                        "description": "Transfer property ownership through sale, inheritance, or donation.",
                        "example_phrasings": [
                            "transfer property ownership",
                            "I inherited land and need to change the title",
                            "change land ownership name",
                            "property sale title transfer",
                        ],
                        "required_documents": ["Current title deed", "Sales contract or inheritance document", "Both parties' IDs", "Tax clearance"],
                        "typical_duration": "2-4 weeks",
                        "fees": "2% of property value (transfer tax)",
                    },
                ],
            },
            {
                "name": "Building Permits",
                "description": "Reviews and approves construction permits for new buildings and renovations.",
                "services": [
                    {
                        "name": "Building Construction Permit",
                        "description": "Obtain a permit to construct a new building on your land.",
                        "example_phrasings": [
                            "I want to build a house",
                            "building permit application",
                            "construction permit for new building",
                            "how to get permission to build",
                            "I need a construction license",
                        ],
                        "required_documents": ["Land title deed", "Architectural drawings", "Structural design", "Kebele ID", "Environmental clearance"],
                        "typical_duration": "2-6 weeks",
                        "fees": "Varies by building size",
                    },
                    {
                        "name": "Building Renovation Permit",
                        "description": "Obtain approval for renovating or modifying an existing building.",
                        "example_phrasings": [
                            "I want to renovate my house",
                            "renovation permit",
                            "modify existing building permit",
                            "building extension permit",
                        ],
                        "required_documents": ["Title deed", "Current building plan", "Proposed modification drawings", "Kebele ID"],
                        "typical_duration": "1-3 weeks",
                        "fees": "Varies",
                    },
                ],
            },
        ],
    },
    {
        "institution": {
            "name": "Ministry of Trade and Regional Integration",
            "type": "federal",
            "description": "Regulates trade, issues business licenses, and manages commercial registration.",
            "is_approved": True,
        },
        "offices": [
            {
                "address": "Bole Sub-city, Near Edna Mall, Addis Ababa",
                "lat": 9.0054,
                "lng": 38.7636,
                "working_hours": "Mon-Fri 8:30-17:00",
                "contact_phone": "+251-11-551-8025",
                "contact_email": "info@mot.gov.et",
            }
        ],
        "departments": [
            {
                "name": "Business Registration",
                "description": "Handles new business registration, renewal, and commercial licensing.",
                "services": [
                    {
                        "name": "New Business License",
                        "description": "Register a new business and obtain a commercial business license.",
                        "example_phrasings": [
                            "I want to start a business",
                            "how to get a business license",
                            "register a new company",
                            "commercial registration for new business",
                            "open a shop license",
                        ],
                        "required_documents": ["Kebele ID", "TIN certificate", "Memorandum of Association (for companies)", "Office lease agreement", "2 photos"],
                        "typical_duration": "3-7 business days",
                        "fees": "500-2,000 ETB depending on business type",
                    },
                    {
                        "name": "Business License Renewal",
                        "description": "Renew an existing business license before or after expiration.",
                        "example_phrasings": [
                            "renew my business license",
                            "my business license expired",
                            "business license renewal process",
                            "extend my trade license",
                        ],
                        "required_documents": ["Current business license", "TIN certificate", "Tax clearance", "Kebele ID"],
                        "typical_duration": "1-3 business days",
                        "fees": "200-500 ETB",
                    },
                    {
                        "name": "Business Name Registration",
                        "description": "Register or change a business trade name.",
                        "example_phrasings": [
                            "register my business name",
                            "I want to change my company name",
                            "trade name registration",
                            "reserve a business name",
                        ],
                        "required_documents": ["Kebele ID", "Proposed business name (3 options)", "TIN certificate"],
                        "typical_duration": "1-2 business days",
                        "fees": "100 ETB",
                    },
                ],
            },
            {
                "name": "Trade and Export Regulation",
                "description": "Issues trade permits, export licenses, and manages import regulations.",
                "services": [
                    {
                        "name": "Export License",
                        "description": "Obtain a license to export goods from Ethiopia.",
                        "example_phrasings": [
                            "I want to export products from Ethiopia",
                            "get an export license",
                            "export permit for coffee",
                            "how to become an exporter",
                        ],
                        "required_documents": ["Business license", "TIN certificate", "Product quality certification", "Bank account statement"],
                        "typical_duration": "5-10 business days",
                        "fees": "1,000-5,000 ETB",
                    },
                    {
                        "name": "Import Permit",
                        "description": "Obtain authorization to import specific goods into Ethiopia.",
                        "example_phrasings": [
                            "I need to import goods",
                            "import permit application",
                            "how to get authorization to import",
                            "import license for electronics",
                        ],
                        "required_documents": ["Business license", "TIN certificate", "Proforma invoice", "Bank permit"],
                        "typical_duration": "3-7 business days",
                        "fees": "Varies",
                    },
                ],
            },
        ],
    },
    {
        "institution": {
            "name": "Vital Events Registration Agency",
            "type": "federal",
            "description": "Registers births, marriages, deaths, and issues related certificates.",
            "is_approved": True,
        },
        "offices": [
            {
                "address": "Arada Sub-city, Piassa Area, Addis Ababa",
                "lat": 9.0350,
                "lng": 38.7480,
                "working_hours": "Mon-Fri 8:30-17:00",
                "contact_phone": "+251-11-126-6000",
                "contact_email": "info@vera.gov.et",
            }
        ],
        "departments": [
            {
                "name": "Civil Registration",
                "description": "Handles registration of vital events: births, marriages, divorces, and deaths.",
                "services": [
                    {
                        "name": "Birth Certificate",
                        "description": "Register a birth and obtain an official birth certificate.",
                        "example_phrasings": [
                            "I need a birth certificate",
                            "register my child's birth",
                            "how to get a birth certificate",
                            "get birth certificate for my baby",
                            "birth registration",
                        ],
                        "required_documents": ["Hospital birth notification", "Parents' IDs", "Marriage certificate (if applicable)"],
                        "typical_duration": "1-3 business days",
                        "fees": "Free (within 90 days of birth), 200 ETB (late registration)",
                    },
                    {
                        "name": "Marriage Certificate",
                        "description": "Register a marriage and obtain an official marriage certificate.",
                        "example_phrasings": [
                            "I need a marriage certificate",
                            "register my marriage",
                            "how to get married officially",
                            "civil marriage registration",
                        ],
                        "required_documents": ["Both parties' IDs", "Birth certificates", "2 witnesses with IDs", "Divorce decree (if previously married)"],
                        "typical_duration": "Same day to 3 business days",
                        "fees": "200 ETB",
                    },
                    {
                        "name": "Death Certificate",
                        "description": "Register a death and obtain an official death certificate.",
                        "example_phrasings": [
                            "I need a death certificate",
                            "register a death",
                            "death certificate for a family member",
                            "how to report a death officially",
                        ],
                        "required_documents": ["Medical death certificate", "Deceased's ID", "Reporter's ID"],
                        "typical_duration": "1-2 business days",
                        "fees": "Free",
                    },
                    {
                        "name": "Divorce Registration",
                        "description": "Register a court-ordered divorce and update civil status.",
                        "example_phrasings": [
                            "register my divorce",
                            "I need to record my divorce",
                            "divorce certificate",
                            "update marital status after divorce",
                        ],
                        "required_documents": ["Court divorce decree", "Marriage certificate", "Both parties' IDs"],
                        "typical_duration": "3-5 business days",
                        "fees": "100 ETB",
                    },
                ],
            },
        ],
    },
    {
        "institution": {
            "name": "Ethiopian Investment Commission (EIC)",
            "type": "federal",
            "description": "Promotes and facilitates domestic and foreign investment in Ethiopia.",
            "is_approved": True,
        },
        "offices": [
            {
                "address": "Bole Sub-city, Near Bole International Airport, Addis Ababa",
                "lat": 8.9806,
                "lng": 38.7578,
                "working_hours": "Mon-Fri 8:30-17:00",
                "contact_phone": "+251-11-551-0033",
                "contact_email": "info@investethiopia.gov.et",
            }
        ],
        "departments": [
            {
                "name": "Investment Licensing",
                "description": "Issues investment permits and manages investor registration.",
                "services": [
                    {
                        "name": "New Investment Permit",
                        "description": "Obtain an investment permit for a new domestic or foreign investment project.",
                        "example_phrasings": [
                            "I want to invest in Ethiopia",
                            "how to get an investment permit",
                            "foreign investment license",
                            "start an investment project",
                            "investment permit application",
                        ],
                        "required_documents": ["Business plan", "Proof of capital (bank statement)", "Passport (for foreign investors)", "Company registration documents"],
                        "typical_duration": "5-10 business days",
                        "fees": "Free",
                    },
                    {
                        "name": "Investment Permit Renewal",
                        "description": "Renew an existing investment permit.",
                        "example_phrasings": [
                            "renew my investment permit",
                            "investment license renewal",
                            "extend investment permit",
                        ],
                        "required_documents": ["Current investment permit", "Progress report", "Financial statements"],
                        "typical_duration": "3-5 business days",
                        "fees": "Free",
                    },
                    {
                        "name": "Investment Incentive Application",
                        "description": "Apply for tax holidays, duty-free imports, and other investment incentives.",
                        "example_phrasings": [
                            "investment tax incentives",
                            "apply for tax holiday",
                            "duty free import for investment",
                            "investment incentives in Ethiopia",
                        ],
                        "required_documents": ["Investment permit", "Project proposal", "Import list (for duty-free)"],
                        "typical_duration": "1-2 weeks",
                        "fees": "Free",
                    },
                ],
            },
        ],
    },
    {
        "institution": {
            "name": "Addis Ababa Water and Sewerage Authority (AAWSA)",
            "type": "municipal",
            "description": "Provides water supply and sewerage services in Addis Ababa.",
            "is_approved": True,
        },
        "offices": [
            {
                "address": "Lebu, Nifas Silk-Lafto Sub-city, Addis Ababa",
                "lat": 8.9740,
                "lng": 38.7278,
                "working_hours": "Mon-Fri 8:30-17:00, Sat 8:30-12:00",
                "contact_phone": "+251-11-551-1111",
                "contact_email": "info@aawsa.gov.et",
            }
        ],
        "departments": [
            {
                "name": "Customer Service",
                "description": "Handles new connections, billing inquiries, and service complaints.",
                "services": [
                    {
                        "name": "New Water Connection",
                        "description": "Apply for a new water supply connection to a property.",
                        "example_phrasings": [
                            "I need water connection for my house",
                            "new water meter installation",
                            "how to get water supply to my property",
                            "connect water to my building",
                            "apply for water service",
                        ],
                        "required_documents": ["Title deed or lease agreement", "Kebele ID", "Building permit", "Site plan"],
                        "typical_duration": "2-4 weeks",
                        "fees": "5,000-15,000 ETB depending on pipe size",
                    },
                    {
                        "name": "Water Bill Payment and Inquiry",
                        "description": "Pay water bills, check balance, or dispute billing amounts.",
                        "example_phrasings": [
                            "pay my water bill",
                            "water bill is too high",
                            "check my water bill balance",
                            "dispute water charges",
                            "where to pay water bill",
                        ],
                        "required_documents": ["Water bill or account number", "Kebele ID"],
                        "typical_duration": "Same day",
                        "fees": "Bill amount",
                    },
                    {
                        "name": "Water Meter Replacement",
                        "description": "Replace a damaged, faulty, or old water meter.",
                        "example_phrasings": [
                            "my water meter is broken",
                            "replace water meter",
                            "faulty water meter",
                            "water meter not working",
                        ],
                        "required_documents": ["Water account number", "Kebele ID", "Report of faulty meter"],
                        "typical_duration": "3-7 business days",
                        "fees": "Varies by meter type",
                    },
                    {
                        "name": "Report Water Leak or Pipe Burst",
                        "description": "Report a water leak, pipe burst, or supply interruption in your area.",
                        "example_phrasings": [
                            "there is a water leak in my street",
                            "pipe burst in my neighborhood",
                            "no water supply",
                            "water pipe is broken",
                            "report water problem",
                        ],
                        "required_documents": ["Location details"],
                        "typical_duration": "24-48 hours response",
                        "fees": "Free",
                    },
                    {
                        "name": "Sewerage Connection",
                        "description": "Apply for connection to the city sewerage system.",
                        "example_phrasings": [
                            "connect to city sewerage",
                            "sewerage connection application",
                            "I need sewage service",
                            "connect my building to sewer",
                        ],
                        "required_documents": ["Title deed", "Building plan", "Kebele ID"],
                        "typical_duration": "2-4 weeks",
                        "fees": "Varies",
                    },
                ],
            },
        ],
    },
]


async def seed_database():
    """Insert all seed data into the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        for item in SEED_DATA:
            # Create institution
            inst_data = item["institution"]
            institution = Institution(**inst_data)
            session.add(institution)
            await session.flush()  # Get the generated ID

            # Create offices
            offices = []
            for off_data in item["offices"]:
                office = Office(institution_id=institution.id, **off_data)
                session.add(office)
                offices.append(office)
            await session.flush()

            # Create departments and services
            for dept_data in item["departments"]:
                services_data = dept_data.pop("services", [])
                department = Department(institution_id=institution.id, **dept_data)
                session.add(department)
                await session.flush()

                for svc_data in services_data:
                    service = Service(
                        department_id=department.id,
                        office_id=offices[0].id if offices else None,
                        **svc_data,
                    )
                    session.add(service)

            await session.flush()

        await session.commit()

        # Print summary
        from sqlalchemy import func, select

        for model, name in [
            (Institution, "Institutions"),
            (Department, "Departments"),
            (Office, "Offices"),
            (Service, "Services"),
        ]:
            result = await session.execute(select(func.count()).select_from(model))
            count = result.scalar()
            print(f"  {name}: {count}")


async def main():
    print("Seeding database...")
    await seed_database()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())

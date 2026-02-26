from __future__ import annotations

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Subpages to check for emails and signals
EXTRA_PATHS = ["/contact", "/contact-us", "/about", "/about-us"]

# ── Tech Stack Detection Signals ─────────────────────────────────────────────

TECH_SIGNALS = {
    # Productivity / Cloud
    "Microsoft 365":     ["microsoft365", "office365", "outlook.com", "microsoftonline"],
    "Google Workspace":  ["workspace.google", "gsuite", "google workspace"],
    "Microsoft Teams":   ["teams.microsoft", "microsoft.com/teams"],
    "Slack":             ["slack.com", "slack-edge"],
    "Zoom":              ["zoom.us"],
    # CMS
    "WordPress":         ["wp-content", "wp-includes", "wordpress"],
    "Shopify":           ["shopify", "myshopify.com"],
    "Wix":               ["wix.com", "wixsite", "wixpress"],
    "Squarespace":       ["squarespace.com", "sqsp.net"],
    # CRM / Marketing
    "HubSpot":           ["hubspot.com", "hs-scripts", "hs-analytics"],
    "Salesforce":        ["salesforce.com", "force.com"],
    "Zoho":              ["zoho.com", "zohocdn"],
    # MSP-Relevant (RMM / PSA / Backup) — NEGATIVE signals
    "ConnectWise":       ["connectwise.com", "screenconnect", "connectwise"],
    "Datto":             ["datto.com", "datto"],
    "Kaseya":            ["kaseya.com", "kaseya"],
    # Security / Network
    "SonicWall":         ["sonicwall.com", "sonicwall"],
    "Fortinet":          ["fortinet.com", "fortigate", "fortinet"],
    "Meraki":            ["meraki.com", "meraki"],
    "Cloudflare":        ["cloudflare"],
    # VoIP / Comms
    "RingCentral":       ["ringcentral.com", "ringcentral"],
    "Vonage":            ["vonage.com", "nexmo"],
    # Cloud Hosting
    "AWS":               ["amazonaws.com", "cloudfront.net"],
    "Azure":             ["azure.com", "azurewebsites.net", "msecnd.net"],
    "Google Cloud":      ["googleapis.com", "cloud.google"],
    # Payments / POS
    "Square":            ["squareup.com", "square.com"],
    "Toast":             ["toasttab.com", "toast"],
    # Industry-Specific
    "QuickBooks":        ["quickbooks.com", "intuit.com/quickbooks"],
    "Mindbody":          ["mindbodyonline.com", "mindbody"],
    "Athenahealth":      ["athenahealth.com", "athena"],
    "Practice Fusion":   ["practicefusion.com"],
    "Dentrix":           ["dentrix.com", "dentrix"],
    "Epic":              ["epic.com", "mychart"],
}

# If any of these are detected, business likely already has an MSP
MSP_TOOL_SIGNALS = {"ConnectWise", "Datto", "Kaseya"}

# IT staff keywords — presence suggests they DON'T need an MSP
IT_KEYWORDS = [
    "it department", "it director", "it manager", "sys admin",
    "sysadmin", "chief technology officer", "cto", "it staff",
]

# Compliance keywords — presence is a POSITIVE MSP signal
COMPLIANCE_KEYWORDS = [
    "hipaa", "pci", "pci-dss", "compliance", "phi ",
    "protected health", "ferpa", "sox compliance", "gdpr",
]

# ── Verticals Registry (68 verticals across 13 sectors) ─────────────────────

VERTICALS = {
    # Healthcare & Medical (HIPAA-driven)
    "dental office":              {"icon": "🦷", "sector": "Healthcare", "msp_fit": 95, "reason": "HIPAA, no IT staff, high revenue per patient"},
    "medical clinic":             {"icon": "🏥", "sector": "Healthcare", "msp_fit": 93, "reason": "HIPAA, EMR/EHR systems, always need IT"},
    "chiropractic office":        {"icon": "🩺", "sector": "Healthcare", "msp_fit": 90, "reason": "HIPAA, small staff, EHR systems"},
    "optometry clinic":           {"icon": "👁️", "sector": "Healthcare", "msp_fit": 88, "reason": "HIPAA, specialized imaging software"},
    "physical therapy clinic":    {"icon": "💪", "sector": "Healthcare", "msp_fit": 87, "reason": "HIPAA, billing software, no IT"},
    "veterinary clinic":          {"icon": "🐾", "sector": "Healthcare", "msp_fit": 80, "reason": "Practice mgmt software, small teams"},
    "pharmacy":                   {"icon": "💊", "sector": "Healthcare", "msp_fit": 88, "reason": "HIPAA, POS + inventory systems, compliance"},
    "mental health practice":     {"icon": "🧠", "sector": "Healthcare", "msp_fit": 86, "reason": "HIPAA, telehealth platforms, sensitive data"},
    "dermatology clinic":         {"icon": "🔬", "sector": "Healthcare", "msp_fit": 87, "reason": "HIPAA, imaging systems, cosmetic revenue"},
    "urgent care center":         {"icon": "🚑", "sector": "Healthcare", "msp_fit": 89, "reason": "HIPAA, EMR, high uptime requirements"},
    "home health agency":         {"icon": "🏠", "sector": "Healthcare", "msp_fit": 84, "reason": "HIPAA, mobile workforce, scheduling software"},
    "medical laboratory":         {"icon": "🧪", "sector": "Healthcare", "msp_fit": 85, "reason": "HIPAA, LIMS software, data-heavy"},
    "imaging center":             {"icon": "📡", "sector": "Healthcare", "msp_fit": 86, "reason": "HIPAA, PACS systems, massive file storage"},
    "plastic surgery center":     {"icon": "✨", "sector": "Healthcare", "msp_fit": 88, "reason": "HIPAA, high revenue, patient portals"},
    "fertility clinic":           {"icon": "🌱", "sector": "Healthcare", "msp_fit": 87, "reason": "HIPAA, specialized software, sensitive data"},
    "podiatry office":            {"icon": "🦶", "sector": "Healthcare", "msp_fit": 85, "reason": "HIPAA, small practice, EHR"},
    "orthodontist office":        {"icon": "😁", "sector": "Healthcare", "msp_fit": 86, "reason": "HIPAA, imaging, practice management"},
    "oral surgery office":        {"icon": "🦷", "sector": "Healthcare", "msp_fit": 87, "reason": "HIPAA, surgical scheduling, imaging"},
    "audiology clinic":           {"icon": "👂", "sector": "Healthcare", "msp_fit": 84, "reason": "HIPAA, hearing aid software, small staff"},
    "ambulatory surgery center":  {"icon": "🏨", "sector": "Healthcare", "msp_fit": 90, "reason": "HIPAA, surgical systems, high compliance"},

    # Legal & Compliance
    "law firm":                   {"icon": "⚖️", "sector": "Legal", "msp_fit": 92, "reason": "Sensitive client data, strict uptime, no IT dept"},
    "immigration law office":     {"icon": "🌍", "sector": "Legal", "msp_fit": 88, "reason": "Document-heavy, compliance, client portals"},
    "family law practice":        {"icon": "👨‍👩‍👧", "sector": "Legal", "msp_fit": 86, "reason": "Sensitive data, document management"},
    "patent law firm":            {"icon": "📜", "sector": "Legal", "msp_fit": 89, "reason": "IP-sensitive data, large document repos"},

    # Financial & Accounting
    "accounting firm":            {"icon": "📊", "sector": "Financial", "msp_fit": 89, "reason": "Compliance needs, tax season crunch, sensitive data"},
    "financial advisor":          {"icon": "💼", "sector": "Financial", "msp_fit": 85, "reason": "SEC/FINRA compliance, high trust requirements"},
    "insurance agency":           {"icon": "📋", "sector": "Financial", "msp_fit": 83, "reason": "Data-sensitive, compliance-driven, quoting software"},
    "tax preparation service":    {"icon": "📄", "sector": "Financial", "msp_fit": 84, "reason": "IRS compliance, seasonal load, sensitive data"},
    "wealth management firm":     {"icon": "💎", "sector": "Financial", "msp_fit": 87, "reason": "SEC compliance, portfolio software, high-value clients"},
    "mortgage broker":            {"icon": "🏦", "sector": "Financial", "msp_fit": 82, "reason": "TRID compliance, loan origination software"},
    "credit union":               {"icon": "🏛️", "sector": "Financial", "msp_fit": 86, "reason": "NCUA compliance, banking software, member data"},
    "bookkeeping service":        {"icon": "📒", "sector": "Financial", "msp_fit": 78, "reason": "Cloud accounting tools, QuickBooks"},

    # Professional Services
    "architecture firm":          {"icon": "📐", "sector": "Professional", "msp_fit": 72, "reason": "CAD/BIM software, large file management"},
    "engineering firm":           {"icon": "🔧", "sector": "Professional", "msp_fit": 74, "reason": "CAD software, project management, large files"},
    "marketing agency":           {"icon": "📣", "sector": "Professional", "msp_fit": 70, "reason": "SaaS-heavy, remote teams, fast growth"},
    "consulting firm":            {"icon": "🤝", "sector": "Professional", "msp_fit": 73, "reason": "Remote workforce, data security, collaboration tools"},
    "staffing agency":            {"icon": "👥", "sector": "Professional", "msp_fit": 76, "reason": "ATS software, distributed offices, payroll systems"},
    "PR firm":                    {"icon": "📰", "sector": "Professional", "msp_fit": 68, "reason": "Media databases, content management, remote teams"},
    "interior design firm":       {"icon": "🎨", "sector": "Professional", "msp_fit": 65, "reason": "Design software, project management"},
    "event planning company":     {"icon": "🎉", "sector": "Professional", "msp_fit": 64, "reason": "CRM, payment processing, vendor coordination"},

    # Real Estate & Property
    "real estate agency":         {"icon": "🏡", "sector": "Real Estate", "msp_fit": 78, "reason": "Cloud-heavy, distributed teams, CRM-dependent"},
    "property management company":{"icon": "🏢", "sector": "Real Estate", "msp_fit": 80, "reason": "Tenant portals, maintenance software, multi-site"},
    "title company":              {"icon": "📝", "sector": "Real Estate", "msp_fit": 82, "reason": "Sensitive documents, compliance, wire fraud risk"},
    "commercial real estate firm":{"icon": "🏬", "sector": "Real Estate", "msp_fit": 79, "reason": "CRM, analytics, deal management"},

    # Construction & Trades
    "construction company":       {"icon": "🏗️", "sector": "Construction", "msp_fit": 75, "reason": "Field + office IT, project management tools"},
    "general contractor":         {"icon": "🔨", "sector": "Construction", "msp_fit": 73, "reason": "Estimating software, job costing, field mobility"},
    "electrical contractor":      {"icon": "⚡", "sector": "Construction", "msp_fit": 70, "reason": "Scheduling, estimating, fleet management"},
    "plumbing company":           {"icon": "🔧", "sector": "Construction", "msp_fit": 68, "reason": "Dispatching software, fleet management"},
    "HVAC company":               {"icon": "❄️", "sector": "Construction", "msp_fit": 70, "reason": "IoT monitoring, dispatching, service management"},

    # Manufacturing
    "manufacturing company":      {"icon": "🏭", "sector": "Manufacturing", "msp_fit": 74, "reason": "ERP systems, CNC/PLC networks, OT security"},
    "machine shop":               {"icon": "⚙️", "sector": "Manufacturing", "msp_fit": 70, "reason": "CNC software, CAD/CAM, job tracking"},
    "printing company":           {"icon": "🖨️", "sector": "Manufacturing", "msp_fit": 68, "reason": "Production management, prepress software"},

    # Automotive
    "auto dealership":            {"icon": "🚗", "sector": "Automotive", "msp_fit": 80, "reason": "DMS software, CRM, multi-department IT needs"},
    "auto repair shop":           {"icon": "🔧", "sector": "Automotive", "msp_fit": 65, "reason": "Shop management software, diagnostics"},
    "auto body shop":             {"icon": "🚙", "sector": "Automotive", "msp_fit": 63, "reason": "Estimating software (CCC/Mitchell), photos"},

    # Education & Childcare
    "private school":             {"icon": "🎓", "sector": "Education", "msp_fit": 78, "reason": "LMS, student info systems, parent portals"},
    "tutoring center":            {"icon": "📚", "sector": "Education", "msp_fit": 62, "reason": "Scheduling, online platforms, small staff"},
    "daycare center":             {"icon": "👶", "sector": "Education", "msp_fit": 64, "reason": "Parent communication apps, compliance, cameras"},

    # Nonprofit & Religious
    "nonprofit organization":     {"icon": "💚", "sector": "Nonprofit", "msp_fit": 70, "reason": "Donor management, grant tracking, tight budgets"},
    "church":                     {"icon": "⛪", "sector": "Nonprofit", "msp_fit": 65, "reason": "AV systems, member management, streaming"},

    # Logistics & Transportation
    "trucking company":           {"icon": "🚛", "sector": "Logistics", "msp_fit": 72, "reason": "ELD compliance, fleet tracking, dispatch"},
    "freight broker":             {"icon": "📦", "sector": "Logistics", "msp_fit": 74, "reason": "TMS software, load boards, EDI"},
    "logistics company":          {"icon": "🌐", "sector": "Logistics", "msp_fit": 75, "reason": "WMS, shipping software, multi-site operations"},

    # Hospitality
    "hotel":                      {"icon": "🏨", "sector": "Hospitality", "msp_fit": 76, "reason": "PMS, POS, WiFi infrastructure, guest data"},
    "catering company":           {"icon": "🍽️", "sector": "Hospitality", "msp_fit": 62, "reason": "Event management, POS, kitchen displays"},

    # Fitness & Wellness
    "gym":                        {"icon": "🏋️", "sector": "Fitness", "msp_fit": 68, "reason": "Member management, access control, POS"},
    "med spa":                    {"icon": "💆", "sector": "Fitness", "msp_fit": 82, "reason": "HIPAA-adjacent, EMR, payment processing"},
    "multi-location salon":       {"icon": "💇", "sector": "Fitness", "msp_fit": 66, "reason": "POS, booking software, multi-site management"},
}

# Extract sector list for grouping
SECTORS = sorted(set(v["sector"] for v in VERTICALS.values()))

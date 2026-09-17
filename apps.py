"""
The 100-app research set.
Each entry: (name, category, hint_url, likely_composio_slug_guess)

"""

APPS = [
    # 1. CRM and Sales
    ("Salesforce", "CRM & Sales", "salesforce.com", "salesforce"),
    ("HubSpot", "CRM & Sales", "hubspot.com", "hubspot"),
    ("Pipedrive", "CRM & Sales", "pipedrive.com", "pipedrive"),
    ("Attio", "CRM & Sales", "attio.com", "attio"),
    ("Twenty", "CRM & Sales", "twenty.com", "twenty"),
    ("Podio", "CRM & Sales", "podio.com", "podio"),
    ("Zoho CRM", "CRM & Sales", "zoho.com/crm", "zoho_crm"),
    ("Close", "CRM & Sales", "close.com", "close"),
    ("Copper", "CRM & Sales", "copper.com", "copper"),
    ("DealCloud", "CRM & Sales", "api.docs.dealcloud.com", "dealcloud"),

    # 2. Support and Helpdesk
    ("Zendesk", "Support & Helpdesk", "zendesk.com", "zendesk"),
    ("Intercom", "Support & Helpdesk", "intercom.com", "intercom"),
    ("Freshdesk", "Support & Helpdesk", "freshdesk.com", "freshdesk"),
    ("Front", "Support & Helpdesk", "front.com", "front"),
    ("Pylon", "Support & Helpdesk", "usepylon.com", "pylon"),
    ("LiveAgent", "Support & Helpdesk", "liveagent.com", "liveagent"),
    ("Plain", "Support & Helpdesk", "plain.com", "plain"),
    ("Help Scout", "Support & Helpdesk", "helpscout.com", "helpscout"),
    ("Gorgias", "Support & Helpdesk", "gorgias.com", "gorgias"),
    ("Gladly", "Support & Helpdesk", "gladly.com", "gladly"),

    # 3. Communications and Messaging
    ("Slack", "Communications", "slack.com", "slack"),
    ("Twilio", "Communications", "twilio.com", "twilio"),
    ("Zoho Cliq", "Communications", "zoho.com/cliq", "zoho_cliq"),
    ("Lark (Larksuite)", "Communications", "open.larksuite.com", "larksuite"),
    ("Pumble", "Communications", "pumble.com", "pumble"),
    ("Discord", "Communications", "discord.com", "discord"),
    ("Telegram", "Communications", "core.telegram.org", "telegram"),
    ("WhatsApp Business", "Communications", "developers.facebook.com/docs/whatsapp", "whatsapp"),
    ("Aircall", "Communications", "aircall.io", "aircall"),
    ("Vonage", "Communications", "developer.vonage.com", "vonage"),

    # 4. Marketing, Ads, Email and Social
    ("Google Ads", "Marketing & Ads", "developers.google.com/google-ads", "googleads"),
    ("Meta Ads", "Marketing & Ads", "developers.facebook.com/docs/marketing-apis", "meta_ads"),
    ("LinkedIn Ads", "Marketing & Ads", "learn.microsoft.com/linkedin/marketing", "linkedin_ads"),
    ("GoHighLevel", "Marketing & Ads", "highlevel.stoplight.io", "gohighlevel"),
    ("Mailchimp", "Marketing & Ads", "mailchimp.com/developer", "mailchimp"),
    ("Klaviyo", "Marketing & Ads", "developers.klaviyo.com", "klaviyo"),
    ("systeme.io", "Marketing & Ads", "systeme.io", "systeme_io"),
    ("Pinterest", "Marketing & Ads", "developers.pinterest.com", "pinterest"),
    ("Threads (Meta)", "Marketing & Ads", "developers.facebook.com/docs/threads", "threads"),
    ("SendGrid", "Marketing & Ads", "sendgrid.com", "sendgrid"),

    # 5. Ecommerce
    ("Shopify", "Ecommerce", "shopify.dev", "shopify"),
    ("WooCommerce", "Ecommerce", "woocommerce.com/document/woocommerce-rest-api", "woocommerce"),
    ("BigCommerce", "Ecommerce", "developer.bigcommerce.com", "bigcommerce"),
    ("Salesforce Commerce Cloud", "Ecommerce", "developer.salesforce.com/docs/commerce", "sfcc"),
    ("Magento (Adobe Commerce)", "Ecommerce", "developer.adobe.com/commerce", "magento"),
    ("Squarespace", "Ecommerce", "developers.squarespace.com", "squarespace"),
    ("Ecwid", "Ecommerce", "api-docs.ecwid.com", "ecwid"),
    ("Gumroad", "Ecommerce", "gumroad.com/api", "gumroad"),
    ("Amazon Selling Partner", "Ecommerce", "developer-docs.amazon.com/sp-api", "amazon_sp"),
    ("fanbasis", "Ecommerce", "fanbasis.com", "fanbasis"),

    # 6. Data, SEO and Scraping
    ("DataForSEO", "Data, SEO & Scraping", "docs.dataforseo.com", "dataforseo"),
    ("SE Ranking", "Data, SEO & Scraping", "seranking.com/api", "se_ranking"),
    ("Ahrefs", "Data, SEO & Scraping", "ahrefs.com/api", "ahrefs"),
    ("MrScraper", "Data, SEO & Scraping", "docs.mrscraper.com", "mrscraper"),
    ("Apify", "Data, SEO & Scraping", "docs.apify.com", "apify"),
    ("Firecrawl", "Data, SEO & Scraping", "firecrawl.dev", "firecrawl"),
    ("Bright Data", "Data, SEO & Scraping", "brightdata.com", "brightdata"),
    ("Sherlock", "Data, SEO & Scraping", "github.com/sherlock-project/sherlock", "sherlock"),
    ("Waterfall.io", "Data, SEO & Scraping", "waterfall.io", "waterfall"),
    ("Clay", "Data, SEO & Scraping", "clay.com", "clay"),

    # 7. Developer, Infra and Data platforms
    ("GitHub", "Dev & Infra", "docs.github.com/rest", "github"),
    ("Vercel", "Dev & Infra", "vercel.com/docs/rest-api", "vercel"),
    ("Netlify", "Dev & Infra", "docs.netlify.com/api", "netlify"),
    ("Cloudflare", "Dev & Infra", "developers.cloudflare.com/api", "cloudflare"),
    ("Supabase", "Dev & Infra", "supabase.com/docs", "supabase"),
    ("Neo4j", "Dev & Infra", "neo4j.com/docs/api", "neo4j"),
    ("Snowflake", "Dev & Infra", "docs.snowflake.com", "snowflake"),
    ("MongoDB Atlas", "Dev & Infra", "mongodb.com/docs/atlas/api", "mongodb"),
    ("Datadog", "Dev & Infra", "docs.datadoghq.com/api", "datadog"),
    ("Sentry", "Dev & Infra", "docs.sentry.io/api", "sentry"),

    # 8. Productivity and Project Management
    ("Notion", "Productivity & PM", "developers.notion.com", "notion"),
    ("Airtable", "Productivity & PM", "airtable.com/developers", "airtable"),
    ("Linear", "Productivity & PM", "developers.linear.app", "linear"),
    ("Jira", "Productivity & PM", "developer.atlassian.com", "jira"),
    ("Asana", "Productivity & PM", "developers.asana.com", "asana"),
    ("Monday.com", "Productivity & PM", "developer.monday.com", "monday"),
    ("ClickUp", "Productivity & PM", "clickup.com/api", "clickup"),
    ("Coda", "Productivity & PM", "coda.io/developers", "coda"),
    ("Smartsheet", "Productivity & PM", "smartsheet.com/developers", "smartsheet"),
    ("Harvest", "Productivity & PM", "help.getharvest.com/api-v2", "harvest"),

    # 9. Finance and Fintech
    ("Stripe", "Finance & Fintech", "stripe.com/docs/api", "stripe"),
    ("Plaid", "Finance & Fintech", "plaid.com/docs", "plaid"),
    ("Binance", "Finance & Fintech", "binance-docs.github.io", "binance"),
    ("Paygent Connect", "Finance & Fintech", "paygent (NMI-powered)", "paygent"),
    ("iPayX", "Finance & Fintech", "ipayx.ai/docs", "ipayx"),
    ("QuickBooks", "Finance & Fintech", "developer.intuit.com", "quickbooks"),
    ("Xero", "Finance & Fintech", "developer.xero.com", "xero"),
    ("Brex", "Finance & Fintech", "developer.brex.com", "brex"),
    ("Ramp", "Finance & Fintech", "docs.ramp.com", "ramp"),
    ("PitchBook", "Finance & Fintech", "pitchbook.com", "pitchbook"),

    # 10. AI, Research and Media-native
    ("NotebookLM", "AI & Media-native", "cloud.google.com/gemini", "notebooklm"),
    ("Otter AI", "AI & Media-native", "help.otter.ai", "otter"),
    ("Fathom", "AI & Media-native", "fathom.video", "fathom"),
    ("Consensus", "AI & Media-native", "consensus.app", "consensus"),
    ("Reducto", "AI & Media-native", "reducto.ai", "reducto"),
    ("Devin", "AI & Media-native", "docs.devin.ai", "devin"),
    ("higgsfield", "AI & Media-native", "higgsfield.ai/cli", "higgsfield"),
    ("Mermaid CLI", "AI & Media-native", "github.com/mermaid-js/mermaid-cli", "mermaid_cli"),
    ("YouTube Transcript", "AI & Media-native", "transcriptapi.com", "youtube_transcript"),
    ("Grain", "AI & Media-native", "grain.com", "grain"),
]

assert len(APPS) == 100, f"expected 100 apps, got {len(APPS)}"

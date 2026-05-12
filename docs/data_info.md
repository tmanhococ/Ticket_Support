It includes priorities, queues, types, tags, and business types. This preview offers a detailed structure with classifications by department, type, priority, language, subject, full email text, and agent answers.

Features / Attributes
Field	Description	Values
🔀 Queue	Specifies the department to which the email ticket is routed	e.g. Technical Support, Customer Service, Billing and Payments, …
🚦 Priority	Indicates the urgency and importance of the issue	🟢Low
🟠Medium
🔴Critical
🗣️ Language	Indicates the language in which the email is written	EN, DE, ES, FR, PT
Subject	Subject of the customer's email	
Body	Body of the customer's email	
Answer	The response provided by the helpdesk agent	
Type	The type of ticket as picked by the agent	e.g. Incident, Request, Problem, Change …
🏢 Business Type	The business type of the support helpdesk	e.g. Tech Online Store, IT Services, Software Development Company
Tags	Tags/categories assigned to the ticket, split into ten columns in the dataset	e.g. "Software Bug", "Warranty Claim"
Queue
Specifies the department to which the email ticket is categorized. This helps in routing the ticket to the appropriate support team for resolution.

💻 Technical Support: Technical issues and support requests.
🈂️ Customer Service: Customer inquiries and service requests.
💰 Billing and Payments: Billing issues and payment processing.
🖥️ Product Support: Support for product-related issues.
🌐 IT Support: Internal IT support and infrastructure issues.
🔄 Returns and Exchanges: Product returns and exchanges.
📞 Sales and Pre-Sales: Sales inquiries and pre-sales questions.
🧑‍💻 Human Resources: Employee inquiries and HR-related issues.
❌ Service Outages and Maintenance: Service interruptions and maintenance.
📮 General Inquiry: General inquiries and information requests.
Priority
Indicates the urgency and importance of the issue. Helps in managing the workflow by prioritizing tickets that need immediate attention.

🟢 1 (Low): Non-urgent issues that do not require immediate attention. Examples: general inquiries, minor inconveniences, routine updates, and feature requests.
🟠 2 (Medium): Moderately urgent issues that need timely resolution but are not critical. Examples: performance issues, intermittent errors, and detailed user questions.
🔴 3 (High): Urgent issues that require immediate attention and quick resolution. Examples: system outages, security breaches, data loss, and major malfunctions.
Language
Indicates the language in which the email is written. Useful for language-specific NLP models and multilingual support analysis.

en (English)
de (German)
Answer
The response provided by the helpdesk agent, containing the resolution or further instructions. Useful for analyzing the quality and effectiveness of the support provided.

Types
Different types of tickets categorized to understand the nature of the requests or issues.

❗ Incident: Unexpected issue requiring immediate attention.
📝 Request: Routine inquiry or service request.
⚠️ Problem: Underlying issue causing multiple incidents.
🔄 Change: Planned change or update.
Business Type
The business type of the support helpdesk. Helps in understanding the context of the support provided.

Examples: "Tech Online Store," "IT Services," "Software Development Company."
Tags
Tags/categories assigned to the ticket to further classify and identify common issues or topics.

Examples: "Product Support," "Technical Support," "Sales Inquiry."
Use Cases

mockdata:
subject,body,answer,type,queue,priority,language,version,tag_1,tag_2,tag_3,tag_4,tag_5,tag_6,tag_7,tag_8
Wesentlicher Sicherheitsvorfall,"Sehr geehrtes Support-Team,\n\nich möchte einen gravierenden Sicherheitsvorfall melden, der gegenwärtig mehrere Komponenten unserer Infrastruktur betrifft. Betroffene Geräte umfassen Projektoren, Bildschirme und Speicherlösungen auf Cloud-Plattformen. Der Grund für die Annahme ist, dass der Vorfall eine potenzielle Datenverletzung im Zusammenhang mit einer Cyberattacke darstellt, was ein erhebliches Risiko für sensible Informationen und den laufenden Geschäftsbetrieb unserer Organisation bedeutet.\n\nUnsere initialen Untersuchungen haben ungewöhnliche Aktivitäten und Abweichungen bei den Geräten ergeben. Trotz der Umsetzung unserer standardisierten Behebungs- und Eindämmungsmaßnahmen konnte die Bedrohung bislang nicht vollständig eliminiert.","Vielen Dank für die Meldung des kritischen Sicherheitsvorfalls und die Bereitstellung der Übersicht über die betroffenen Geräte sowie der ergriffenen ersten Maßnahmen. Wir erkennen die Dringlichkeit und Schwere der Lage an und setzen alles daran, den Fall prioritär zu bearbeiten. Für eine umgehende Untersuchung benötigen wir zusätzliche Informationen: Bitte senden Sie uns spezifische Protokolle der betroffenen Projektoren, Bildschirme und Cloud-Speichersysteme, inklusive Zeitstempel verdächtiger Aktivitäten sowie ungewöhnlicher Fehlermeldungen. Falls möglich, fügen Sie auch eine Zusammenfassung der bereits durchgeführten Maßnahmen bei.",Incident,Technical Support,high,de,51,Security,Outage,Disruption,Data Breach,,,,
Account Disruption,"Dear Customer Support Team,\n\nI am writing to report a significant problem with the centralized account management portal, which currently appears to be offline. This outage is blocking access to account settings, leading to substantial inconvenience. I have attempted to log in multiple times using different browsers and devices, but the issue persists.\n\nCould you please provide an update on the outage status and an estimated time for resolution? Also, are there any alternative ways to access and manage my account during this downtime?","Thank you for reaching out, <name>. We are aware of the outage affecting the centralized account management system, and our technical team is actively working to resolve the issue. In the meantime, we suggest using alternative methods to manage your account, with a focus on restoring service as quickly as possible. We will provide an update as soon as the service is back online. We apologize for the inconvenience and appreciate your patience. If you have any further questions, please let us know.",Incident,Technical Support,high,en,51,Account,Disruption,Outage,IT,Tech Support,,,
Query About Smart Home System Integration Features,"Dear Customer Support Team,\n\nI hope this message reaches you well. I am reaching out to request detailed information about the capabilities of your smart home integration products listed on your website. As a potential customer aiming to develop a seamlessly interconnected home environment, it is essential to understand how your products interact with various smart home platforms.\n\nCould you kindly provide detailed compatibility information with popular smart home ecosystems such as Amazon Alexa, Google Assistant, and Apple?","Thank you for your inquiry. Our products support integration with Amazon Alexa, Google Assistant, and Apple HomeKit. Compatibility details can differ depending on the specific item; please let us know which models you are interested in. The setup process is generally user-friendly but may require professional installation. We regularly update our software to provide enhanced features. For comprehensive information on compatibility with upcoming updates, please specify the models you are considering.",Request,Returns and Exchanges,medium,en,51,Product,Feature,Tech Support,,,,,

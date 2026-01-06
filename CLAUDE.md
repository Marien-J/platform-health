# Platform Health Dashboard

## Context
Dashboard for director-level health monitoring of EDLAP, SAP B/W, Tableau, Alteryx.

## Key Design Decisions
- At-a-glance RAG status (Healthy/Attention/Critical)
- Click platform card → filters ticket table
- Thresholds configurable in src/data.py

## Next Steps
- Connect to real data sources (ServiceNow, Databricks, SAP)
- Define status thresholds with director
- Add drill-down links to existing platform dashboards


This content is to summarize all the information on what I can find out the dashboard should do. 

1) the dashboard is to serve has a general health indicator for the platforms managed by the platforms and architecture department. These include: EDLAP (the enterprise data lake, mainly for analytics and built on databricks), SAP B/W (complex platform with lots of scaling issues, definitely need to involve the SAP teams), Alteryx and Tableau (actively working with this team)

2) For EDLAP, it seems some form or indicator of open tickets, overdue items etc. is in order. This might have to be a general thing. Since it is built on databricks, scaling is typically a non issue. Might have to look into linking to an existing dashboard on data-loading, as a lot of data is coming by flat file transfer. The platform is self service, so seems unnecessary to go to pipeline level. 

3) Alteryx and Tableau: Seems to have some differences in their set up (and alteryx being a self service platform). Perhaps the most meaningful way to get something here is to periodically run representative dashboards, and get some average and peak loading times. They seem to definitely be CPU limited, question remains to be seen if this limit is ever reached on peak usage times.

4) SAP B/W: clearly memory limited, system is on an enormous 24TB machine and has a dedicated team managing it. It would already be great to get the memory readouts on a periodic basis, so that we can reasonably see when the machine is running into its limits. Perhaps something with data load times and quality too? 

5) It is clear that the director wants to "not be surprised", in the sense that it sounds like he receives some urgent message (perhaps from another or other director(s)?), and gets blindsided by ongoing issues. He wants to then be able to open a dashboard and see some general health for each of the platforms (simple, but perhaps green-red is too oversimplified). It does have to give him a statement on a glance. 
He then wishes to also be able to deep dive (could be another dashboard that already exists, or can be built in the future). In specific, he would also like to then go into open tickets, and see specific issues (and maybe even open a specific ticket from the person messaging him?). It feels to me like just a ticket list will be overwhelming. Perhaps some filtering options?
# Logic Apps (Cloud & Hybrid) vs BizTalk Server — Feature & Connector Comparison

_Researched 2026-05-27. Scope: comparing **BizTalk Server 2020** (on-prem), **Logic Apps Standard** (cloud + hybrid on Azure Arc-enabled Kubernetes), and **Logic Apps Consumption** (cloud-only multitenant), with connector focus on **SQL, SAP, File, FTP, Service Bus**. Assumption: "SQAP" in the brief = **SAP**._

## TL;DR

Microsoft has positioned **Azure Logic Apps Standard as the successor to BizTalk Server** [1][2], and that's the direction every new investment is going — including a dedicated Migration Agent in VS Code that automates the discovery → conversion → deployment loop [3]. For the customer's connector list (SQL, SAP, File, FTP, Service Bus), **Logic Apps Standard ships native built-in connectors** for SQL Server, FTP, SFTP, Service Bus and Event Hubs that run in-process with the workflow — meaning higher throughput, lower latency, and lower cost at scale than the equivalent managed-connector versions [4][5]. With the **hybrid deployment model** introduced for Logic Apps Standard, you can run those same workflows on **your own Azure Arc-enabled Kubernetes cluster — on-prem, on Azure Local, or on Windows Server** — keeping data local while staying on Microsoft's modern integration platform [6][7]. BizTalk Server 2020 is still fully supported (Mainstream until **April 11, 2028**, End-of-Support **April 9, 2030**) [8][9], and remains the right choice today only when you depend on capabilities Microsoft has not yet ported (mature on-prem-only EDI, Business Rules Engine, the BizTalk Mapper) — but no new BizTalk version is on the roadmap [1].

## Key findings

- Logic Apps Standard is Microsoft's official BizTalk successor and the only product receiving new investment in this space [1][2].
- **Hybrid deployment for Logic Apps Standard** lets you run workflows on your own Kubernetes (AKS, Azure Local, or Windows Server) via Azure Arc — true on-prem execution with a cloud control plane [6][7].
- All five connectors the customer asked about (SQL, SAP, File, FTP, Service Bus) are covered in Logic Apps Standard; SQL, FTP, SFTP and Service Bus are **built-in** (in-process), which Consumption does not offer [4].
- BizTalk Server 2020 is the last major release; **Mainstream support ends 2028-04-11, full End-of-Support 2030-04-09** [8][9]. Customers should plan a migration runway, not a re-platform onto BizTalk.
- Microsoft ships an **AI-powered Logic Apps Migration Agent** (VS Code) that automates discovery, analysis, and conversion of BizTalk artifacts in five stages [3][10].

## Product positioning

BizTalk Server 2020 remains in support but is in a clear wind-down. Microsoft's lifecycle pages list Mainstream End-of-Support as **April 11, 2028** (extended three years from the original date) and full End-of-Support as **April 9, 2030** [8][9]. The same lifecycle announcement is explicit: *"customers are encouraged to consider cloud solutions in Azure as an alternative to BizTalk"* [8]. There is no BizTalk Server 2023/2024/2025 — 2020 is the last release.

Logic Apps Standard, by contrast, is described in Microsoft's own documentation as the *"Successor to BizTalk"* [1], and the BizTalk-to-Logic-Apps migration guidance explicitly steers customers toward Standard (not Consumption) for integration workloads [2]. New capabilities — hybrid deployment, the Migration Agent, Liquid/XML operations without an integration account, .NET-assembly support in XSLT maps — all land on Standard first [1][6][3].

## Hosting and where it runs

The three options the customer is comparing differ most in **where the runtime executes**:

| Aspect | BizTalk Server 2020 | Logic Apps Standard (hybrid) | Logic Apps Standard (cloud) | Logic Apps Consumption |
|---|---|---|---|---|
| Where it runs | On-prem Windows Servers you manage | Your **Azure Arc-enabled Kubernetes** cluster (AKS, Azure Local, or Windows Server) [6][7] | Single-tenant Workflow Service Plan or ASE v3 in Azure [11][4] | Multitenant Azure Logic Apps service [11] |
| Storage for state | SQL Server (MessageBox, tracking) on-prem | **Your** SQL DB + SMB file share, on the same network as the cluster [6][12] | Azure Storage (or external SQL for stateful) [11] | Azure-managed storage [11] |
| Control plane | Fully on-prem | Azure portal (semi-connected — tolerates up to **24h** offline) [7] | Azure portal | Azure portal |
| Workflows per resource | Many (Applications/Orchestrations) | Many stateful + stateless [4] | Many stateful + stateless [4] | **One** workflow per resource [11] |
| Region availability (hybrid only) | n/a | 9 Azure regions today (Central US, East/North Central/West US, East Asia, Southeast Asia, Sweden Central, UK South, West Europe) [7] | All Azure regions | All Azure regions |

The hybrid model gives the customer the strongest argument to *modernise without re-locating data*: built-in connectors execute locally against on-prem SQL/SAP/File systems for high throughput, and managed connectors in Azure are still available when you need SaaS reach [6].

## Pricing model

| BizTalk Server 2020 | Logic Apps Standard | Logic Apps Consumption |
|---|---|---|
| Per-core Windows Server licence (Enterprise / Standard / Branch / Developer editions) + hardware and Windows/SQL Server licences you own. | App Service plan (Workflow Service Plan tier — WS1/WS2/WS3) or ASE v3 — **flat hourly billing regardless of execution count** [4][13]. Stateful workflows additionally incur Azure Storage transactions [4]. | **Pay-per-execution** — billed per action, per trigger, per connector call [11][13]. |

For steady, high-volume integration (the BizTalk profile), Standard is generally cheaper than Consumption at scale because built-in connector calls (SQL, Service Bus, etc.) don't incur per-call connector charges — they run in the workflow process [4][5]. Consumption stays attractive for spiky, low-volume scenarios.

## Connector coverage — SQL, SAP, File, FTP, Service Bus

This is the heart of the comparison for the customer. In Logic Apps, connectors come in two flavours: **built-in** (runs in-process, lower cost, higher throughput, only available in Standard) and **managed** (runs in Azure-shared infrastructure, available in both SKUs, may need the **on-premises data gateway** to reach on-prem systems) [4][14].

| Connector | BizTalk Server 2020 | Logic Apps Standard (hybrid or cloud) | Logic Apps Consumption |
|---|---|---|---|
| **SQL Server** | Native SQL adapter (WCF-SQL) — mature, supports composite operations, polling | **Built-in** SQL Server connector (in-process) **and** managed connector [4]. In hybrid, runs locally against on-prem SQL with no gateway. | Managed connector only; on-prem SQL needs the data gateway [14] |
| **SAP** | Native SAP adapter (WCF-SAP) — IDoc, RFC, BAPI; long-standing reference customer base | **Built-in** SAP connector (in-process, no gateway) **and** managed connector. The built-in version is the recommended path going forward [15][4] | Managed connector only; on-prem SAP needs the data gateway [15] |
| **File** (local filesystem) | Native File adapter — battle-tested for on-prem batch | **File System** managed connector — reaches on-prem file shares via the data gateway in cloud, or runs locally in hybrid [4] | Managed connector only via the data gateway |
| **FTP / SFTP** | Native FTP and SFTP adapters | **Built-in** FTP and SFTP connectors (in-process) **and** managed counterparts [4] | Managed connectors only |
| **Service Bus** | Native WCF-NetMessaging / SB-Messaging adapter | **Built-in** Azure Service Bus connector (in-process) — uses connection string, Entra ID, or managed identity [4][16] | Managed connector only |

**Honest call-outs:**
- BizTalk's adapters are older but extremely battle-tested — particularly for SAP IDoc-heavy workloads and SQL composite operations. Customers with thousands of lines of SAP/SQL adapter configuration won't see a 1:1 port; the Migration Agent helps but human review is needed [3][2].
- File-system / FTP triggers on BizTalk have decades of operational tuning; the Logic Apps built-in versions are now feature-rich but newer.
- In hybrid mode, the Logic Apps Standard built-in connectors run **locally** on your Kubernetes cluster — this is the key narrative for customers who picked BizTalk in the first place because they couldn't move data to the cloud [6][7].

## Developer experience, ops, and lifecycle

| Area | BizTalk Server 2020 | Logic Apps Standard | Logic Apps Consumption |
|---|---|---|---|
| Designer | Visual Studio (BizTalk project templates) | Browser designer **+** VS Code (Azure Logic Apps Standard extension), local debugging, breakpoints in `workflow.json` actions [11] | Browser designer only |
| Source control / CI/CD | MSI deploy of compiled BizTalk applications | Project model — workflows are JSON + artifacts; deploy via zip, Bicep/ARM, or pipelines; **Terraform not supported for full infra** [11] | ARM templates; designer-first |
| Workflow types | Orchestrations (always durable) | **Stateful and stateless** in the same app [4] | Stateful only |
| BizTalk-specific assets | BRE, BAM, EDI, mapper, pipeline components | Liquid + XML schema ops built-in; **integration account** for B2B/EDI artefacts; .NET assemblies callable from XSLT maps to ease migration [1] | Integration account required for B2B |
| Migration tooling | n/a (it's the source) | **Logic Apps Migration Agent for VS Code** — 5 stages (Discovery, Planning, Conversion, Validation, Deployment), built on GitHub Copilot [3][10] | Same agent targets Standard, not Consumption |
| Lifecycle | Mainstream EOS **2028-04-11**, EOS **2030-04-09** [8][9] | Actively developed; primary Microsoft investment [1] | Actively maintained; investment focus is on Standard |

## Where BizTalk still has a real edge (honest)

To keep the comparison credible — these are the genuine reasons a customer might *defer* (not avoid) migrating:

- **Business Rules Engine (BRE)**: BizTalk's BRE is mature and policy-versioned. Logic Apps has no direct equivalent; the migration guide recommends expressing rules in workflow logic or pushing them to dedicated rule engines [2].
- **BizTalk Mapper**: visually richer than current Logic Apps data mapper for very large XSDs.
- **EDI / AS2 maturity**: both products support EDI via integration accounts in Logic Apps, but BizTalk EDI has 15+ years of corner-case handling.
- **Fully disconnected operation**: BizTalk runs with **no** Azure dependency. Logic Apps Standard hybrid is *semi-connected* — it tolerates up to **24 hours** offline before logging data is at risk [7]. If your environment must be air-gapped indefinitely, BizTalk still wins.
- **Managed identity for connector operations** is **not yet supported** in hybrid deployments [7].

These should be weighed during the discovery sprint, not used as a reason to skip migration — Microsoft's clear direction is Logic Apps Standard, and the Migration Agent is designed to surface exactly these gaps so they can be planned.

## Recommended path for this customer

Given the customer's connector set (SQL, SAP, File, FTP, Service Bus) maps cleanly onto Logic Apps Standard's **built-in** connector inventory [4], and most of those workloads likely need to keep talking to on-prem systems:

1. **Run the Logic Apps Migration Agent (VS Code)** on the existing BizTalk solution — automated Discovery + Planning will produce a concrete inventory and effort estimate [3][10].
2. **Default target = Logic Apps Standard hybrid** (Azure Arc-enabled Kubernetes) for workloads that need on-prem data locality; **Logic Apps Standard in Azure** for greenfield cloud-friendly workloads [6][7].
3. **Reserve Consumption** for the small, spiky, cloud-only integrations where pay-per-execution wins on cost [11][13].
4. **Plan around 2028** as the practical Mainstream cliff for BizTalk 2020, with the hard 2030 deadline as the absolute backstop [8][9].

## Open questions

- **Exact built-in connector parity for SAP on hybrid**: the SAP built-in connector exists; confirming whether every IDoc/BAPI scenario the customer uses is supported in the hybrid runtime would require a workload-specific check, not just docs.
- **Pricing comparison vs current BizTalk licence cost**: not computed here — needs the customer's actual core count, environment count (dev/test/prod), and current Software Assurance status.
- **EDI scope**: if the customer has a heavy EDI/AS2 footprint, a separate deep-dive on Logic Apps integration accounts vs BizTalk EDI is warranted.

## Sources

1. *Why migrate from BizTalk Server to Azure Logic Apps Standard?* — https://learn.microsoft.com/azure/logic-apps/biztalk-server-migration-overview (Microsoft Learn)
2. *Migration approaches for BizTalk Server to Azure Logic Apps Standard* — https://learn.microsoft.com/azure/logic-apps/biztalk-server-migration-approaches (Microsoft Learn)
3. *Quickstart: Automate migration for integration projects to Azure Logic Apps (Standard) (preview)* — https://learn.microsoft.com/azure/logic-apps/migration/migration-agent-quickstart (Microsoft Learn)
4. *Differences between Standard single-tenant logic apps versus Consumption multitenant logic apps — Built-in connectors for Standard* — https://learn.microsoft.com/azure/logic-apps/single-tenant-overview-compare#built-in-connectors-for-standard (Microsoft Learn)
5. *Differences between Standard single-tenant logic apps versus Consumption multitenant logic apps — Standard logic app and workflow* — https://learn.microsoft.com/azure/logic-apps/single-tenant-overview-compare#standard-logic-app-and-workflow (Microsoft Learn)
6. *Set up your own infrastructure for Standard logic apps using hybrid deployment — How hybrid deployment works* — https://learn.microsoft.com/azure/logic-apps/set-up-standard-workflows-hybrid-deployment-requirements#how-hybrid-deployment-works (Microsoft Learn)
7. *Set up your own infrastructure for Standard logic apps using hybrid deployment — Limitations* — https://learn.microsoft.com/azure/logic-apps/set-up-standard-workflows-hybrid-deployment-requirements#how-hybrid-deployment-works (Microsoft Learn)
8. *Mainstream support extended for BizTalk Server 2020 and Host Integration Server 2020* — https://learn.microsoft.com/lifecycle/announcements/biztalk-server-2020-host-integration-server-2020-support-extended (Microsoft Learn, 2024-01-09 announcement)
9. *Ending Support in 2030 — Products reaching End of Support* — https://learn.microsoft.com/lifecycle/end-of-support/end-of-support-2030#products-reaching-end-of-support (Microsoft Learn)
10. *Migration approaches for BizTalk Server to Azure Logic Apps Standard — Deliver a BizTalk migration project* — https://learn.microsoft.com/azure/logic-apps/biztalk-server-migration-approaches#deliver-a-biztalk-migration-project (Microsoft Learn)
11. *Differences between Standard single-tenant logic apps versus Consumption multitenant logic apps — Logic app workflow types and environments* — https://learn.microsoft.com/azure/logic-apps/single-tenant-overview-compare#logic-app-workflow-types-and-environments (Microsoft Learn)
12. *Set up your own infrastructure for Standard logic apps using hybrid deployment — Create SQL Server storage provider* — https://learn.microsoft.com/azure/logic-apps/set-up-standard-workflows-hybrid-deployment-requirements#create-sql-server-storage-provider (Microsoft Learn)
13. *Azure Logic Apps pricing model* — https://learn.microsoft.com/azure/logic-apps/logic-apps-pricing (Microsoft Learn)
14. *Managed connectors for Azure Logic Apps* — https://learn.microsoft.com/azure/connectors/managed (Microsoft Learn)
15. *Logic Apps SAP connector* — https://learn.microsoft.com/azure/connectors/connectors-create-api-sap (Microsoft Learn)
16. *Logic Apps Azure Service Bus connector (built-in)* — https://learn.microsoft.com/azure/connectors/connectors-create-api-servicebus (Microsoft Learn)

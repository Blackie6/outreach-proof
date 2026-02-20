**Onchain Lead Journal**

Product Requirements Document

0G Hackathon 2025 \| Version 1.0 \| Built on Zero Gravity (0G) Storage

  -----------------------------------------------------------------------
  **Field**              **Value**
  ---------------------- ------------------------------------------------
  Project Name           Onchain Lead Journal

  Author                 Sergey

  Version                1.0

  Status                 Hackathon MVP

  Platform               0G Storage + 0G Compute

  Primary Market         Real Estate (Mexico / Seminia)

  Date                   2025
  -----------------------------------------------------------------------

**1. Problem Statement**

AI sales agents are making calls and sending WhatsApp messages on behalf
of real estate developers at scale. No tamper-proof record exists of
what was said, when, and what outcome resulted. CRMs can be edited. Logs
can be deleted. Deals get disputed.

In emerging markets like Mexico, where legal infrastructure around
digital outreach is immature, developers have no credible way to prove
to investors, regulators, or partners that leads were contacted,
qualified, and handled professionally.

**Core pain points:**

-   No verifiable audit trail for AI-driven sales outreach

-   CRM data is mutable and untrustworthy as proof

-   Disputes between developers and investors about outreach quality
    have no resolution mechanism

-   Compliance with emerging data laws requires documented, time-stamped
    interaction records

-   Multi-channel outreach (voice + WhatsApp) creates fragmented,
    unconnected logs

**2. Product Overview**

Lead Journal writes every AI touchpoint to 0G Storage as an immutable,
append-only event chain. Personal data stays hashed client-side. The
ledger is permanent and cryptographically verifiable.

The output is a Proof of Outreach report: a machine-readable and
human-readable artifact that any stakeholder can independently verify
without trusting the operator.

**One-line pitch:**

\"Every AI sales call leaves a tamper-proof receipt on-chain. Your CRM
can lie. The ledger can\'t.\"

**3. Target Users**

  ------------------------------------------------------------------------
  **User**         **Role**           **Primary Need**
  ---------------- ------------------ ------------------------------------
  Real estate      Primary customer   Prove outreach quality to
  developer                           investors/regulators

  Sales ops        Admin user         Monitor AI agent performance with
  manager                             verifiable logs

  Investor /       External verifier  Independently verify that leads were
  auditor                             contacted

  AI agent (Lisa)  Data producer      Write call outcomes to ledger
                                      automatically

  WhatsApp bot     Data producer      Write message events to ledger
                                      automatically
  ------------------------------------------------------------------------

**4. Core Data Model**

**4.1 Lead Record**

One record per lead. Stored in 0G Storage. Append-only. Never
overwritten.

> {
>
> \"lead_id\": \"uuid-v4\",
>
> \"phone_hash\": \"sha256(+52\...)\",
>
> \"created_at\": \"ISO8601\",
>
> \"events\": \[ \... \]
>
> }

**4.2 Event Object**

> {
>
> \"event_id\": \"uuid-v4\",
>
> \"type\": \"call_completed \| call_failed \| whatsapp_sent \|
> whatsapp_reply\",
>
> \"timestamp\": \"ISO8601\",
>
> \"content_hash\": \"sha256(transcript or message text)\",
>
> \"outcome\": \"interested \| not_interested \| callback \| no_answer
> \| pending\",
>
> \"agent\": \"Lisa \| WhatsApp-bot \| human\",
>
> \"duration_seconds\": 142,
>
> \"storage_tx_id\": \"0G Storage TX hash\",
>
> \"metadata\": {}
>
> }

**4.3 Privacy Rules**

-   Phone numbers: always hashed (SHA-256) before writing to chain

-   Message content: hash only; raw content never stored on-chain

-   Transcripts: hash only; full transcript stored off-chain or omitted

-   PII compliance: GDPR-compatible by design; conforms to Mexican Ley
    Federal de Proteccion de Datos Personales

**5. Feature Specification**

**5.1 Write API (Ingest Layer)**

Accepts POST events from any agent (Lisa, WhatsApp bot, or manual
trigger). Validates schema, hashes sensitive fields, writes to 0G
Storage, returns storage_tx_id.

  ---------------------------------------------------------------------------------
  **Endpoint**            **Method**   **Description**
  ----------------------- ------------ --------------------------------------------
  POST /events            POST         Ingest a new event for a lead

  POST /leads             POST         Create a new lead record

  GET /leads/:lead_id     GET          Retrieve full event chain for a lead

  GET                     GET          Generate Proof of Outreach report
  /leads/:lead_id/proof                
  ---------------------------------------------------------------------------------

**5.2 Event Types**

  -----------------------------------------------------------------------
  **Event Type**   **Trigger**         **Required Fields**
  ---------------- ------------------- ----------------------------------
  call_completed   Lisa finishes a     outcome, duration_seconds,
                   call                content_hash

  call_failed      Call not connected  outcome (no_answer), timestamp

  whatsapp_sent    Bot sends message   content_hash, agent

  whatsapp_reply   Lead replies        content_hash, timestamp
  -----------------------------------------------------------------------

**5.3 Read & Verify Layer**

Given a lead_id, the system retrieves the full ordered event chain from
0G Storage and renders a human-readable timeline. Every entry includes
its storage_tx_id for independent verification.

-   Event timeline view: ordered by timestamp, grouped by channel (voice
    / WhatsApp)

-   Outcome summary: total contacts, outcomes breakdown, last
    interaction date

-   Verification link: direct 0G Storage TX link for each event

**5.4 Proof of Outreach Report**

The core deliverable. A structured artifact containing:

-   Lead identifier (hashed phone + lead_id)

-   Total touchpoints: N calls + M WhatsApp messages

-   Date range of outreach

-   Final outcome status

-   Table of all events with TX IDs

-   Verification statement: \"All records verifiable on 0G Storage
    Network\"

Export format: JSON (machine-readable) + plain text / PDF
(human-readable).

**6. Technical Architecture**

**6.1 Stack**

  -----------------------------------------------------------------------
  **Layer**       **Technology**     **Notes**
  --------------- ------------------ ------------------------------------
  Blockchain      0G Storage         Primary ledger; immutable
  storage                            append-only

  Backend         Python / FastAPI   Lightweight; hackathon-appropriate

  Hashing         SHA-256 (hashlib)  Client-side before write

  Mock data       JSON POST / cURL   Simulates Lisa + WhatsApp bot events
  source                             

  Proof export    fpdf2 or plain     MVP: JSON; stretch: PDF
                  JSON               
  -----------------------------------------------------------------------

**6.2 Data Flow**

1.  Agent (Lisa / WhatsApp bot) completes interaction

2.  POST /events with raw event payload

3.  Backend validates schema, hashes phone + content

4.  Event appended to lead record in 0G Storage

5.  storage_tx_id returned and logged

6.  GET /leads/:id/proof generates Proof of Outreach

**7. MVP Scope (2-Hour Hackathon Build)**

  ------------------------------------------------------------------------
  **Feature**                 **In       **Notes**
                              Scope**    
  --------------------------- ---------- ---------------------------------
  Write call event to 0G      YES        Core feature
  Storage                                

  Write WhatsApp event to 0G  YES        Core feature
  Storage                                

  Read event chain by lead_id YES        Core feature

  Proof of Outreach JSON      YES        Core deliverable
  export                                 

  Real Lisa / Retell          NO         Mock POST instead
  integration                            

  Real WhatsApp webhook       NO         Mock POST instead

  PDF export                  NO         Stretch goal

  Frontend UI                 NO         CLI / cURL demo is sufficient

  Authentication              NO         Out of scope for MVP
  ------------------------------------------------------------------------

**8. Build Timeline**

  ------------------------------------------------------------------------
  **Time**      **Task**                       **Output**
  ------------- ------------------------------ ---------------------------
  0:00 - 0:20   Project setup, 0G SDK install, Working skeleton
                schema definition              

  0:20 - 0:50   Write layer: POST /events,     Events writing to chain
                hash, 0G Storage write         

  0:50 - 1:10   Read layer: GET /leads/:id,    Readable event history
                timeline render                

  1:10 - 1:30   Proof export: GET              JSON proof artifact
                /leads/:id/proof               

  1:30 - 2:00   Demo script + pitch slide +    Presentation-ready demo
                buffer                         
  ------------------------------------------------------------------------

**9. Success Criteria**

**Demo must show:**

-   A mock call event written to 0G Storage with a real TX ID

-   A mock WhatsApp event written to 0G Storage with a real TX ID

-   Full lead timeline retrieved and displayed correctly

-   Proof of Outreach JSON generated and readable

**Pitch must convey:**

-   The problem is real and affects a specific market (Mexican real
    estate)

-   0G Storage is the right solution: immutable, cheap, fast

-   The product is immediately deployable to an existing client
    (Seminia)

**10. Future Roadmap (Post-Hackathon)**

  ------------------------------------------------------------------------
  **Phase**   **Feature**                **Value**
  ----------- -------------------------- ---------------------------------
  Phase 1     Live Retell AI (Lisa)      Real call data on-chain
              webhook integration        

  Phase 2     WhatsApp Business API      Real message data on-chain
              webhook integration        

  Phase 3     Developer dashboard with   Sellable SaaS product
              lead timeline UI           

  Phase 4     PDF Proof of Outreach with Legal-grade artifact
              QR verification            

  Phase 5     Multi-client / multi-agent Platform play
              support                    

  Phase 6     0G Compute for AI call     Verifiable quality scores
              scoring on-chain           
  ------------------------------------------------------------------------

**11. Risks & Mitigations**

  -----------------------------------------------------------------------------
  **Risk**               **Likelihood**   **Mitigation**
  ---------------------- ---------------- -------------------------------------
  0G SDK integration     Medium           Test write/read first, build around
  issues during                           it
  hackathon                               

  0G Storage latency     Low              Pre-cache a demo TX ID as fallback
  affects demo flow                       

  Privacy law conflict   Low              Hashing all PII eliminates this by
  (PII on-chain)                          design

  Market skepticism      Medium           Position as compliance tool, not
  about blockchain                        crypto product
  adoption                                
  -----------------------------------------------------------------------------

Built at 0G Hackathon 2025

Onchain Lead Journal \| Powered by Zero Gravity (0G) Storage

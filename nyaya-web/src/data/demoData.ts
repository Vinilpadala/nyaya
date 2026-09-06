import { JudicialCase, StatuteItem, CommercialSuitDossier, ChambersUser, AuditLogEntry } from '../types';

export const DEMO_USERS: ChambersUser[] = [
  {
    id: 'user-judge-01',
    fullName: "Hon'ble Justice A. K. Sharma — DEMO ACCOUNT",
    role: 'JUDGE',
    title: 'Judge, Commercial Appellate Division (Demo)',
    courtDivision: 'High Court of Delhi',
    chambersNumber: 'Courtroom 14 / Chambers 402',
    email: 'justice.sharma@commercialcourt.gov.in',
  },
  {
    id: 'user-clerk-02',
    fullName: 'R. K. Verma, Law Clerk (DEMO ACCOUNT)',
    role: 'RESEARCH_CLERK',
    title: 'Law Clerk-cum-Research Assistant (Demo)',
    courtDivision: 'Commercial Appellate Division',
    chambersNumber: 'Chambers 402 Library Desk',
    email: 'clerk.verma@commercialcourt.gov.in',
  },
  {
    id: 'user-reg-03',
    fullName: 'P. N. Gupta, Registrar (DEMO ACCOUNT)',
    role: 'REGISTRAR',
    title: 'Registrar (Judicial - Commercial Division) (Demo)',
    courtDivision: 'Commercial Registry & Docket Wing',
    chambersNumber: 'Registry Wing Room 108',
    email: 'registrar.commercial@delhihighcourt.nic.in',
  },
];

export const DEMO_CASES: JudicialCase[] = [
  {
    id: 'case-patil-2022',
    title: 'Patil Automation Private Limited and Others v. Rakheja Engineers Private Limited',
    neutralCitation: '2022 INSC 834',
    standardCitation: '(2022) 10 SCC 1',
    court: 'Supreme Court of India',
    judgmentDate: '17 August 2022',
    benchQuorum: 'K. M. Joseph and Hrishikesh Roy, JJ.',
    benchStrength: 2,
    commercialCategory: 'Commercial Courts Act - Pre-Institution Mediation',
    relevantStatute: 'Commercial Courts Act, 2015, Section 12A; CPC Order VII Rule 11',
    isGoodLaw: true,
    statusSummary: 'Settled Law (Landmark Division Bench)',
    isDemoData: true,
    factsSummary:
      'The appellant instituted a commercial suit without first exhausting pre-institution mediation under Section 12A of the Commercial Courts Act, 2015. The respondent filed an application under Order VII Rule 11 of the Code of Civil Procedure, 1808 for rejection of the plaint. Divergence of views existed between various High Courts regarding whether Section 12A is mandatory or directory.',
    ratioDecidendi:
      'Held: Section 12A of the Commercial Courts Act, 2015 is MANDATORY in nature. A commercial suit which does not contemplate any urgent interim relief cannot be instituted without first exhausting the remedy of pre-institution mediation. Non-compliance renders the plaint liable to rejection under Order VII Rule 11 CPC. To prevent disruption of existing decrees, this declaration was made prospective with effect from 20-08-2022.',
    keyParagraphs: [
      {
        number: 84,
        text: 'The Act was enacted to provide for speedy disposal of commercial disputes. A commercial dispute under Section 2(1)(c) encompasses diverse business transactions. Section 12A was inserted by Act 28 of 2018. The words "shall not be instituted" are peremptory, clear and unambiguous. The legislative intent was to compel parties to attempt pre-institution mediation before choking court dockets.',
        highlightReason: 'Statutory mandate interpretation of "shall not be instituted"',
      },
      {
        number: 91,
        text: 'Consequently, we declare that Section 12A of the Act is mandatory and hold that any suit instituted violating the mandate of Section 12A must be visited with rejection of the plaint under Order VII Rule 11. This declaration is made effective prospectively from 20 August 2022.',
        highlightReason: 'Operative ratio and prospective applicability cutoff',
      },
      {
        number: 93,
        text: 'Where urgent interim relief is contemplated, the plaint must contain specific pleadings demonstrating genuine urgency. A mere cosmetic prayer for interim relief invented to bypass Section 12A shall be scrutinized by the Commercial Court.',
        highlightReason: 'Standard for contemplated urgent interim relief',
      },
    ],
    fullJudgmentText: [
      '[1] These appeals raise a seminal question concerning the interpretation of Section 12A of the Commercial Courts Act, 2015 (hereinafter referred to as "the Act"). The question is whether the remedy of pre-institution mediation under Section 12A is mandatory or directory.',
      '[2] Under the Act as originally enacted in 2015, there was no provision for pre-institution mediation. The legislature, observing the heavy pendency and the necessity for expedited dispute resolution in commercial matters, enacted Act 28 of 2018 with effect from 3 May 2018.',
      '[84] The Act was enacted to provide for speedy disposal of commercial disputes. A commercial dispute under Section 2(1)(c) encompasses diverse business transactions. Section 12A was inserted by Act 28 of 2018. The words "shall not be instituted" are peremptory, clear and unambiguous. The legislative intent was to compel parties to attempt pre-institution mediation before choking court dockets.',
      '[91] Consequently, we declare that Section 12A of the Act is mandatory and hold that any suit instituted violating the mandate of Section 12A must be visited with rejection of the plaint under Order VII Rule 11. This declaration is made effective prospectively from 20 August 2022.',
      '[93] Where urgent interim relief is contemplated, the plaint must contain specific pleadings demonstrating genuine urgency. A mere cosmetic prayer for interim relief invented to bypass Section 12A shall be scrutinized by the Commercial Court.',
    ],
    citationsMade: [
      {
        id: 'cit-1',
        caseName: 'Ganga Taro Vazirani v. Deepak Raheja',
        citation: '2021 SCC OnLine Bom 195',
        treatment: 'OVERRULED',
        pinpointPara: 'para 72',
        benchStrength: 1,
        court: 'Bombay High Court',
        year: 2021,
      },
      {
        id: 'cit-2',
        caseName: 'Laxmi Polyfab Pvt. Ltd. v. Eden Realty Ventures',
        citation: '2021 SCC OnLine Cal 1457',
        treatment: 'AFFIRMED',
        pinpointPara: 'para 64',
        benchStrength: 1,
        court: 'Calcutta High Court',
        year: 2021,
      },
      {
        id: 'cit-3',
        caseName: 'Yamini Manohar v. T.K.D. Keerthi',
        citation: '(2024) 5 SCC 815',
        treatment: 'CONSIDERED',
        pinpointPara: 'para 11',
        benchStrength: 2,
        court: 'Supreme Court of India',
        year: 2024,
      },
    ],
  },
  {
    id: 'case-cox-2023',
    title: 'Cox and Kings Ltd. v. SAP India Pvt. Ltd. and Another',
    neutralCitation: '2023 INSC 1051',
    standardCitation: '(2024) 4 SCC 1',
    court: 'Supreme Court of India',
    judgmentDate: '6 December 2023',
    benchQuorum: 'D. Y. Chandrachud CJI, S. K. Kaul, Sanjiv Khanna, B. R. Gavai, Surya Kant, JJ.',
    benchStrength: 5,
    commercialCategory: 'Arbitration - Group of Companies Doctrine',
    relevantStatute: 'Arbitration and Conciliation Act, 1996, Section 7, 8 & 11',
    isGoodLaw: true,
    statusSummary: 'Settled Law (5-Judge Constitution Bench)',
    isDemoData: true,
    factsSummary:
      'Reference to a 5-Judge Constitution Bench regarding the validity, scope, and parameters of the "Group of Companies" doctrine in Indian arbitration law, specifically whether non-signatory affiliates can be joined in arbitral proceedings without express written assent.',
    ratioDecidendi:
      'Held: The "Group of Companies" doctrine is retained in Indian arbitration jurisprudence under Section 7 of the Arbitration Act, 1996. The definition of "parties" under Section 2(1)(h) read with Section 7 includes both signatory and non-signatory corporate affiliates who mutually intended to be bound. Such intent is discernible from the negotiation, performance, and commercial reality of the transaction.',
    keyParagraphs: [
      {
        number: 142,
        text: 'The group of companies doctrine is founded on the mutual intention of all parties to bind the non-signatory. It does not operate as an exception to consent, but rather as an application of modern consensual principles where complex commercial transactions involve parent companies, subsidiaries, and SPVs.',
        highlightReason: 'Core foundation: Consensual intent in complex corporate structuring',
      },
      {
        number: 168,
        text: 'At the referral stage under Section 8 and Section 11, the referral court must only look into the prima facie existence of the arbitration agreement. The question of whether the non-signatory is indeed a party must be left to the Arbitral Tribunal under Section 16 (competence-competence).',
        highlightReason: 'Jurisdictional boundary between Section 11 referral court and Arbitral Tribunal',
      },
    ],
    fullJudgmentText: [
      '[1] The Indian commercial landscape frequently involves conglomerates operating through complex webs of wholly owned subsidiaries and joint venture vehicles. In this reference, we examine whether a non-signatory affiliate can be compelled to arbitrate.',
      '[142] The group of companies doctrine is founded on the mutual intention of all parties to bind the non-signatory. It does not operate as an exception to consent, but rather as an application of modern consensual principles where complex commercial transactions involve parent companies, subsidiaries, and SPVs.',
      '[168] At the referral stage under Section 8 and Section 11, the referral court must only look into the prima facie existence of the arbitration agreement. The question of whether the non-signatory is indeed a party must be left to the Arbitral Tribunal under Section 16 (competence-competence).',
    ],
    citationsMade: [
      {
        id: 'cit-cox-1',
        caseName: 'Chloro Controls India (P) Ltd. v. Severn Trent Water Purification Inc.',
        citation: '(2013) 1 SCC 641',
        treatment: 'AFFIRMED',
        pinpointPara: 'para 70',
        benchStrength: 3,
        court: 'Supreme Court of India',
        year: 2013,
      },
      {
        id: 'cit-cox-2',
        caseName: 'Reckitt Benckiser (India) (P) Ltd. v. Reynders Label Printing (India) (P) Ltd.',
        citation: '(2019) 7 SCC 62',
        treatment: 'DISTINGUISHED',
        pinpointPara: 'para 12',
        benchStrength: 2,
        court: 'Supreme Court of India',
        year: 2019,
      },
    ],
  },
  {
    id: 'case-sms-2011',
    title: 'SMS Tea Estates Pvt. Ltd. v. Chandmari Tea Co. Pvt. Ltd.',
    neutralCitation: '2011 INSC 582',
    standardCitation: '(2011) 14 SCC 66',
    court: 'Supreme Court of India',
    judgmentDate: '20 July 2011',
    benchQuorum: 'R. V. Raveendran and A. K. Patnaik, JJ.',
    benchStrength: 2,
    commercialCategory: 'Arbitration - Stamp Duty & Referrals',
    relevantStatute: 'Arbitration and Conciliation Act, 1996, Section 11; Indian Stamp Act, 1899',
    isGoodLaw: false,
    statusSummary: 'OVERRULED by 7-Judge Bench in In Re Interplay (2023)',
    isDemoData: true,
    factsSummary:
      'Whether an arbitration clause contained in an unregistered and unstamped commercial lease agreement can be acted upon by the Chief Justice or designated judge under Section 11 of the 1996 Act.',
    ratioDecidendi:
      '[HISTORICAL / OVERRULED] Held that an unstamped commercial agreement cannot be acted upon or received in evidence, and the court under Section 11 must impound the document before referring parties to arbitration. (THIS POSITION IS NO LONGER GOOD LAW).',
    keyParagraphs: [
      {
        number: 22,
        text: '[OVERRULED] The court must first examine whether the agreement is stamped properly, and if not stamped, impound it before referring the dispute to arbitration under Section 11.',
        highlightReason: 'Overruled by 7-Judge Bench in Curative Petition No. 44 of 2023',
      },
    ],
    fullJudgmentText: [
      '[1] The question is whether an arbitration clause in an unstamped document can be given effect to under Section 11 of the Arbitration and Conciliation Act, 1996.',
      '[22] [OVERRULED PRINCIPLE] The court must first examine whether the agreement is stamped properly, and if not stamped, impound it before referring the dispute to arbitration under Section 11.',
    ],
    citationsMade: [],
  },
  {
    id: 'case-kailash-2015',
    title: 'Kailash Nath Associates v. Delhi Development Authority',
    neutralCitation: '2015 INSC 22',
    standardCitation: '(2015) 4 SCC 136',
    court: 'Supreme Court of India',
    judgmentDate: '9 January 2015',
    benchQuorum: 'Ranjan Gogoi and R. F. Nariman, JJ.',
    benchStrength: 2,
    commercialCategory: 'Contract Act - Liquidated Damages vs Forfeiture',
    relevantStatute: 'Indian Contract Act, 1872, Section 73 & 74',
    isGoodLaw: true,
    statusSummary: 'Settled Law (Landmark Division Bench)',
    isDemoData: true,
    factsSummary:
      'DDA auctioned a commercial plot; the appellant deposited earnest money of Rs 78 lakhs. Upon non-payment of balance due to pending approvals, DDA cancelled the allotment and forfeited the entire earnest money without proving any actual commercial damage.',
    ratioDecidendi:
      'Held: Section 74 of the Contract Act applies to forfeiture of earnest money. Reasonable compensation can only be awarded where damage or loss is actually suffered. Where loss is ascertainable, proof of actual damage is an indispensable prerequisite for claiming liquidated damages or executing a forfeiture clause.',
    keyParagraphs: [
      {
        number: 43,
        text: 'Where it is possible to prove actual damage or loss, such proof is not dispensed with. It is only in cases where damage or loss is difficult or impossible to prove that the liquidated amount stipulated in the contract can be awarded as reasonable compensation.',
        highlightReason: 'Requirement of proving actual damage when ascertainable',
      },
    ],
    fullJudgmentText: [
      '[1] This appeal concerns the law of liquidated damages and forfeiture of earnest money under Section 74 of the Indian Contract Act, 1872.',
      '[43] Where it is possible to prove actual damage or loss, such proof is not dispensed with. It is only in cases where damage or loss is difficult or impossible to prove that the liquidated amount stipulated in the contract can be awarded as reasonable compensation.',
    ],
    citationsMade: [
      {
        id: 'cit-kn-1',
        caseName: 'Fateh Chand v. Balkishan Dass',
        citation: '(1964) 1 SCR 515',
        treatment: 'AFFIRMED',
        pinpointPara: 'para 8',
        benchStrength: 5,
        court: 'Supreme Court of India',
        year: 1963,
      },
    ],
  },
];

export const DEMO_STATUTES: StatuteItem[] = [
  {
    id: 'statute-cca-2015',
    shortTitle: 'Commercial Courts Act, 2015',
    actNumber: 'Act No. 4 of 2016',
    enactmentYear: 2015,
    jurisdiction: 'Union of India',
    overview:
      'An Act to provide for the constitution of Commercial Courts, Commercial Appellate Courts, Commercial Division and Commercial Appellate Division in the High Courts for adjudicating commercial disputes of Specified Value and for matters connected therewith.',
    isDemoData: true,
    sections: [
      {
        id: 'sec-cca-12a',
        sectionNumber: 'Section 12A',
        heading: 'Pre-Institution Mediation and Settlement',
        content:
          '(1) A suit, which does not contemplate any urgent interim relief under this Act, shall not be instituted unless the plaintiff exhausts the remedy of pre-institution mediation in accordance with such manner and procedure as may be prescribed by rules made by the Central Government.\n\n(2) The Central Government may, by notification, authorise the Authorities constituted under the Legal Services Authorities Act, 1987 (39 of 1987), for the purposes of pre-institution mediation.\n\n(3) Notwithstanding anything contained in the Legal Services Authorities Act, 1987, the Authority authorised by the Central Government under sub-section (2) shall complete the process of mediation within a period of three months from the date of application made by the plaintiff.\n\nProvided that the period of mediation may be extended for a further period of two months with the consent of the parties.\n\n(4) If a settlement of the commercial dispute is arrived at by the parties, the settlement agreement shall be signed by the parties to the dispute and the mediator, and shall have the same status and effect of an arbitral award under section 30(4) of the Arbitration and Conciliation Act, 1996.',
        isAmended: true,
        amendmentNotes: 'Inserted by Commercial Courts Amendment Act, 2018 (Act 28 of 2018, w.e.f. 3-5-2018).',
        practicalGuidelines: [
          'Scrutinize whether the plaint contains real and specific pleadings of urgent interim relief or mere boilerplate language.',
          'If no urgent relief is prayed for and pre-institution mediation was bypassed, the plaint is rejected under Order VII Rule 11 CPC.',
          'Mediation settlement reached under Section 12A is directly executable as an arbitral decree.',
        ],
        landmarkPrecedents: ['(2022) 10 SCC 1 (Patil Automation)', '(2024) 5 SCC 815 (Yamini Manohar)'],
        isDemoData: true,
      },
      {
        id: 'sec-cca-2-1-c',
        sectionNumber: 'Section 2(1)(c)',
        heading: "Definition of 'Commercial Dispute'",
        content:
          "'commercial dispute' means a dispute arising out of—\n(i) ordinary transactions of merchants, bankers, financiers and traders such as those relating to mercantile documents, including enforcement and interpretation of such documents;\n(ii) export or import of merchandise or services;\n(iii) issues relating to admiralty and maritime law;\n(vi) construction and infrastructure contracts, including tenders;\n(vii) agreements relating to aircraft, aircraft engines, aircraft equipment;\n(xviii) intellectual property rights relating to trade marks, copyright, patent, design, domain names;\n(xx) partnership agreements;\nand other mercantile transactions specified under clauses (i) to (xxii).",
        isAmended: false,
        practicalGuidelines: [
          'Verify that the dispute directly relates to commercial transactions and meets the Specified Value threshold (Rs 3 Lakhs or higher as notified).',
        ],
        landmarkPrecedents: ['(2020) 15 SCC 585 (Ambalal Sarabhai Enterprises)'],
        isDemoData: true,
      },
      {
        id: 'sec-cca-order-xi',
        sectionNumber: 'Order XI CPC (Commercial)',
        heading: 'Disclosure, Discovery and Inspection of Documents',
        content:
          'Rule 1(1): Plaintiff shall file a list of all documents and photocopies of all documents in its power, possession, control or custody, pertaining to the suit, along with the plaint.\n\nRule 1(3): The plaint shall contain a declaration on oath from the plaintiff that all documents in the power, possession, control or custody of the plaintiff, pertaining to the facts and circumstances of the proceedings, have been disclosed.\n\nRule 3: The plaint and written statement shall be accompanied by a Statement of Truth in the prescribed statutory format. Non-filing of Statement of Truth renders the pleading non-est.',
        isAmended: true,
        amendmentNotes: 'Replaced the standard CPC Order XI for commercial benches to eliminate delay tactics.',
        practicalGuidelines: [
          'Strict 120-day outer limit for filing Written Statement in commercial suits (Order VIII Rule 1 as amended).',
          'Documents not filed with the plaint cannot be brought on record subsequently without leave of court upon showing reasonable cause.',
        ],
        landmarkPrecedents: ['(2019) 12 SCC 210 (SCG Contracts India)'],
        isDemoData: true,
      },
    ],
  },
  {
    id: 'statute-arb-1996',
    shortTitle: 'Arbitration and Conciliation Act, 1996',
    actNumber: 'Act No. 26 of 1996',
    enactmentYear: 1996,
    jurisdiction: 'Union of India',
    overview:
      'An Act to consolidate and amend the law relating to domestic arbitration, international commercial arbitration and enforcement of foreign arbitral awards.',
    isDemoData: true,
    sections: [
      {
        id: 'sec-arb-9',
        sectionNumber: 'Section 9',
        heading: 'Interim measures, etc., by Court',
        content:
          '(1) A party may, before or during arbitral proceedings or at any time after the making of the arbitral award but before it is enforced in accordance with section 36, apply to a court for an interim measure of protection...\n\n(2) Where, before the commencement of arbitral proceedings, a court passes an order for any interim measure of protection under sub-section (1), the arbitral proceedings shall be commenced within a period of ninety days from the date of such order.',
        isAmended: true,
        amendmentNotes: '90-day time limit inserted by Act 3 of 2016.',
        practicalGuidelines: [
          'Verify if Section 12A Commercial Courts Act interacts: When Section 9 petition contemplates urgent interim relief, Section 12A mediation is not a prerequisite.',
        ],
        landmarkPrecedents: ['(2007) 7 SCC 125 (Adhunik Steels)'],
        isDemoData: true,
      },
      {
        id: 'sec-arb-34',
        sectionNumber: 'Section 34',
        heading: 'Application for setting aside arbitral award',
        content:
          '(1) Recourse to a Court against an arbitral award may be made only by an application for setting aside such award in accordance with sub-section (2) and sub-section (3).\n\n(2A) An arbitral award arising out of an arbitration other than international commercial arbitrations, may also be set aside by the Court, if the Court finds that the award is vitiated by patent illegality appearing on the face of the award: Provided that an award shall not be set aside merely on the ground of an erroneous application of the law or by reappreciation of evidence.',
        isAmended: true,
        amendmentNotes: 'Patent illegality sub-section (2A) added by Act 3 of 2016.',
        practicalGuidelines: [
          'Commercial Court cannot sit as a court of appeal over arbitral tribunal findings.',
        ],
        landmarkPrecedents: ['(2019) 15 SCC 131 (Ssangyong Engineering)'],
        isDemoData: true,
      },
    ],
  },
];

export const DEMO_DOSSIERS: CommercialSuitDossier[] = [
  {
    id: 'dossier-cs-104-2024',
    suitNumber: '[DEMO MATTER] CS (COMM) 104/2024',
    parties: 'M/s Bharat Infra Projects Ltd. v. Delhi Metro Logistics Pvt. Ltd.',
    commercialSubject: 'Infrastructure EPC Contract - Section 12A vs Urgent Relief',
    filingDate: '12 January 2024',
    nextHearingDate: '15 September 2026',
    stage: 'Order VII Rule 11 Application for Rejection of Plaint',
    judicialNotes:
      'Plaintiff instituted commercial suit without Section 12A pre-institution mediation, praying for ex-parte ad-interim injunction restraining invocation of Bank Guarantee. Defendant moved application under Order VII Rule 11 CPC citing Patil Automation ((2022) 10 SCC 1). Scrutiny required on whether the urgency was bona fide or cosmetic.',
    pinnedCases: ['(2022) 10 SCC 1', '(2024) 5 SCC 815'],
    pinnedSections: ['Section 12A', 'Order XI CPC (Commercial)'],
    isUrgentReliefContemplated: true,
    isSec12AExhausted: false,
    dossierNotes: [
      {
        id: 'note-1',
        type: 'BENCH_DIRECTION',
        content:
          'Direct plaintiff counsel to address paragraph 93 of Patil Automation regarding specific demonstration of urgency in plaint paragraphs 24 to 28.',
        sourceReference: '(2022) 10 SCC 1 @ para 93',
        timestamp: '04-09-2026 11:30 AM',
      },
      {
        id: 'note-2',
        type: 'STATUTE_CHECK',
        content:
          'Verify compliance of Statement of Truth in terms of Commercial Courts Act Order XI Rule 3.',
        sourceReference: 'Order XI CPC Rule 3',
        timestamp: '04-09-2026 11:45 AM',
      },
    ],
  },
  {
    id: 'dossier-cs-312-2024',
    suitNumber: 'CS (COMM) 312/2024',
    parties: 'Sterling Pharma Chemicals Ltd. v. Apex Life Sciences Corp.',
    commercialSubject: 'Mercantile Supply Agreement - Order XIII-A Summary Judgment',
    filingDate: '28 March 2024',
    nextHearingDate: '22 September 2026',
    stage: 'Hearing on Order XIII-A Application',
    judicialNotes:
      'Suit for recovery of Rs 4.85 Crores under admitted commercial invoices. Defendant entered appearance but failed to raise any real prospect of defending the claim.',
    pinnedCases: ['(2015) 4 SCC 136'],
    pinnedSections: ['Section 2(1)(c)'],
    isUrgentReliefContemplated: false,
    isSec12AExhausted: true,
    dossierNotes: [
      {
        id: 'note-3',
        type: 'HOLDING',
        content: 'Check whether invoices contain an arbitration agreement or if jurisdiction lies squarely with Commercial Court.',
        sourceReference: 'Plaint Document Annexure P-4',
        timestamp: '04-09-2026 12:15 PM',
      },
    ],
  },
];

export const DEMO_AUDIT_LOGS: AuditLogEntry[] = [
  {
    id: 'audit-001',
    timestamp: '2026-09-04 15:10:22 IST',
    chambersUser: "Hon'ble Justice A. K. Sharma (DEMO ACCOUNT)",
    action: 'PRECEDENT_LOOKUP',
    target: 'Patil Automation v. Rakheja Engineers ((2022) 10 SCC 1)',
    division: 'Commercial Appellate Division',
    ipAddress: '127.0.0.1 (Local Chambers Host)',
  },
  {
    id: 'audit-002',
    timestamp: '2026-09-04 14:55:04 IST',
    chambersUser: 'R. K. Verma (DEMO ACCOUNT)',
    action: 'STATUTE_SEARCH',
    target: 'Commercial Courts Act, 2015 - Section 12A & Order XI CPC',
    division: 'Chambers Research Wing',
    ipAddress: '127.0.0.1 (Local Chambers Host)',
  },
  {
    id: 'audit-003',
    timestamp: '2026-09-04 14:32:11 IST',
    chambersUser: "Hon'ble Justice A. K. Sharma (DEMO ACCOUNT)",
    action: 'BENCH_MEMO_UPDATE',
    target: '[DEMO MATTER] CS (COMM) 104/2024: M/s Bharat Infra v. Delhi Metro Logistics',
    division: 'Commercial Appellate Division',
    ipAddress: '127.0.0.1 (Local Chambers Host)',
  },
];

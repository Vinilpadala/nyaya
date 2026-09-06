export type SupportedLanguage = 'en' | 'hi' | 'te';

export interface LanguageOption {
  code: SupportedLanguage;
  label: string;
  nativeLabel: string;
  status: 'active' | 'future_scope';
}

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
  { code: 'en', label: 'English', nativeLabel: 'English', status: 'active' },
  { code: 'hi', label: 'Hindi', nativeLabel: 'हिन्दी', status: 'active' },
  { code: 'te', label: 'Telugu', nativeLabel: 'తెలుగు', status: 'active' },
];

export interface UiTranslations {
  appTitle: string;
  appSubtitle: string;
  languageSelectLabel: string;
  searchPanelTitle: string;
  queryLabel: string;
  queryPlaceholder: string;
  contextLabel: string;
  contextPlaceholder: string;
  jurisdictionLabel: string;
  benchQuorumLabel: string;
  includeOverruledLabel: string;
  searchButton: string;
  searchingButton: string;
  searchingStatus: string;
  verifiedFooterNote: string;
  sihScenariosTitle: string;
  section1Title: string;
  section2Title: string;
  section3Title: string;
  translationNoticePill: string;
  translationEnginePrefix: string;
  showOriginalEnglishBtn: string;
  showTranslatedBtn: string;
  sourceLawIntegrityBanner: string;
  copyCitation: string;
  citationCopied: string;
  pinToDossier: string;
  pinned: string;
}

export const TRANSLATIONS: Record<SupportedLanguage, UiTranslations> = {
  en: {
    appTitle: 'NYAYA AI',
    appSubtitle: 'Commercial Courts & Appellate Divisions Judicial Research Engine • SIH Judicial Decision-Support Demonstration',
    languageSelectLabel: 'Court Language',
    searchPanelTitle: 'Commercial Court Legal Research Engine & Precedent Synthesizer',
    queryLabel: 'Natural-Language Judicial Issue / Legal Proposition:',
    queryPlaceholder: 'e.g. Whether pre-institution mediation under Section 12A Commercial Courts Act is mandatory...',
    contextLabel: 'Ongoing Matter Factual Context (Optional — for commercial nexus):',
    contextPlaceholder: 'e.g. Commercial suit for recovery arising out of software supply contract; application moved under Order VII Rule 11 CPC...',
    jurisdictionLabel: 'Jurisdiction / Target Court:',
    benchQuorumLabel: 'Minimum Bench Quorum Strength:',
    includeOverruledLabel: 'Include Overruled Authorities (for historical tracing)',
    searchButton: 'Search & Synthesize',
    searchingButton: 'Grounding Synthesis...',
    searchingStatus: 'Consulting Commercial Precedents & Statutes • Evaluating Quorums • Grounding Judicial Synthesis...',
    verifiedFooterNote: 'Verified against official law reporters and central statutory enactments',
    sihScenariosTitle: 'Smart India Hackathon (SIH) Demonstration Scenarios:',
    section1Title: '1. AI-GENERATED RESEARCH BRIEFING: Objective Judicial Summary (Settled Law)',
    section2Title: '2. AUTHORITATIVE SOURCE: Retrieved Primary Judicial Authorities',
    section3Title: '3. AUTHORITATIVE SOURCE: Statutory Enactments & Legislative Provisions',
    translationNoticePill: 'Judicial Translation: Assistive Chamber Aid • Primary Law Reports Remain Authoritative in English',
    translationEnginePrefix: 'Translation Engine:',
    showOriginalEnglishBtn: 'View Authoritative English Text',
    showTranslatedBtn: 'View Translated Explanation',
    sourceLawIntegrityBanner: 'Judicial Integrity Standard: Source Materials (Judgments & Statutes) are strictly separated from AI-Generated Analysis & Inferences.',
    copyCitation: 'Copy Citation',
    citationCopied: 'Copied!',
    pinToDossier: 'Add to Bench Dossier',
    pinned: 'Pinned to Docket',
  },
  hi: {
    appTitle: 'न्याय एआई | NYAYA AI',
    appSubtitle: 'वाणिज्यिक न्यायालय एवं अपीलीय प्रभाग न्यायिक अनुसंधान इंजन • एसआईएच न्यायिक निर्णय-सहायक प्रोटोटाइप',
    languageSelectLabel: 'न्यायालय भाषा',
    searchPanelTitle: 'वाणिज्यिक न्यायालय विधिक अनुसंधान इंजन एवं पूर्वनिर्णय विश्लेषक',
    queryLabel: 'प्राकृतिक-भाषा न्यायिक प्रश्न / विधिक प्रस्थापना:',
    queryPlaceholder: 'उदा. क्या वाणिज्यिक न्यायालय अधिनियम की धारा 12A के तहत संस्थान-पूर्व मध्यस्थता अनिवार्य है...',
    contextLabel: 'विचाराधीन वाद के तथ्यात्मक संदर्भ (वैकल्पिक — वाणिज्यिक संबंध हेतु):',
    contextPlaceholder: 'उदा. सॉफ्टवेयर आपूर्ति अनुबंध से उत्पन्न वसूली का वाणिज्यिक वाद; आदेश VII नियम 11 सीपीसी के तहत आवेदन...',
    jurisdictionLabel: 'अधिकार क्षेत्र / लक्षित न्यायालय:',
    benchQuorumLabel: 'न्यूनतम पीठ (कोरम) संख्या:',
    includeOverruledLabel: 'अधिप्रमाणित / निरस्त पूर्वनिर्णय सम्मिलित करें (ऐतिहासिक विश्लेषण हेतु)',
    searchButton: 'खोजें एवं विश्लेषण करें',
    searchingButton: 'विश्लेषण प्रगति पर...',
    searchingStatus: 'वाणिज्यिक पूर्वनिर्णयों एवं संविधियों का संदर्भ • पीठ कोरम मूल्यांकन • न्यायिक विश्लेषण...',
    verifiedFooterNote: 'आधिकारिक विधि रिपोर्टों (SCC/SCR) एवं केंद्रीय अधिनियमों के आधार पर सत्यापित',
    sihScenariosTitle: 'स्मार्ट इंडिया हैकाथॉन (SIH) प्रदर्शन परिदृश्य:',
    section1Title: '1. एआई-जनित अनुसंधान ब्रीफिंग: वस्तुनिष्ठ न्यायिक सारांश (स्थापित विधि)',
    section2Title: '2. आधिकारिक स्रोत: प्राथमिक न्यायिक पूर्वनिर्णय',
    section3Title: '3. आधिकारिक स्रोत: संविधिक रूपरेखा एवं विधायी उपबंध',
    translationNoticePill: 'न्यायिक अनुवाद सूचना: केवल चैंबर संदर्भ हेतु • आधिकारिक विधि रिपोर्ट अंग्रेजी में ही मान्य है',
    translationEnginePrefix: 'अनुवाद इंजन:',
    showOriginalEnglishBtn: 'मूल अंग्रेजी पाठ देखें',
    showTranslatedBtn: 'हिंदी अनुवाद देखें',
    sourceLawIntegrityBanner: 'न्यायिक सत्यनिष्ठा मानक: मूल निर्णय एवं संविधियां एआई विश्लेषण से पूर्णतः पृथक रखी गई हैं।',
    copyCitation: 'उद्धरण कॉपी करें',
    citationCopied: 'कॉपी हो गया!',
    pinToDossier: 'न्यायिक डॉजियर में जोड़ें',
    pinned: 'डॉकेट में संलग्न',
  },
  te: {
    appTitle: 'న్యాయ ఏఐ | NYAYA AI',
    appSubtitle: 'వాణిజ్య న్యాయస్థానాలు & అప్పిలేట్ డివిజన్లు న్యాయ పరిశోధన ఇంజిన్ • SIH న్యాయ నిర్ణయ-మద్దతు నమూనా',
    languageSelectLabel: 'కోర్టు భాష',
    searchPanelTitle: 'వాణిజ్య న్యాయస్థాన న్యాయ పరిశోధన ఇంజిన్ & పూర్వ తీర్పుల సంశ్లేషణ',
    queryLabel: 'సహజ భాషా న్యాయ ప్రశ్న / చట్టపరమైన ప్రతిపాదన:',
    queryPlaceholder: 'ఉదా. వాణిజ్య న్యాయస్థానాల చట్టం సెక్షన్ 12A ప్రకారం మధ్యవర్తిత్వం తప్పనిసరా...',
    contextLabel: 'కేసు వాస్తవ సందర్భం (ఐచ్ఛికం — వాణిజ్య సంబంధం కొరకు):',
    contextPlaceholder: 'ఉదా. సాఫ్ట్‌వేర్ సరఫరా కాంట్రాక్ట్ ఉల్లంఘన రికవరీ దావా; ఆర్డర్ 7 రూల్ 11 CPC కింద వాజ్యం తిరస్కరణ దరఖాస్తు...',
    jurisdictionLabel: 'అధికార పరిధి / లక్ష్య న్యాయస్థానం:',
    benchQuorumLabel: 'కనిష్ట న్యాయమూర్తుల సంఖ్య (కోరం):',
    includeOverruledLabel: 'కొట్టివేయబడిన తీర్పులను చేర్చండి (చారిత్రక పరిశీలన కొరకు)',
    searchButton: 'శోధించండి & విశ్లేషించండి',
    searchingButton: 'విశ్లేషిస్తోంది...',
    searchingStatus: 'వాణిజ్య పూర్వ తీర్పులు & చట్టాల సమీక్ష • ధర్మాసన బలం లెక్కింపు • న్యాయ విశ్లేషణ...',
    verifiedFooterNote: 'అధికారిక న్యాయ నివేదికలు (SCC/SCR) మరియు కేంద్ర చట్టాల ప్రకారం ధృవీకరించబడింది',
    sihScenariosTitle: 'స్మార్ట్ ఇండియా హ్యాకథాన్ (SIH) ప్రదర్శన దృశ్యాలు:',
    section1Title: '1. AI పరిశోధన బ్రీఫింగ్: నిష్పాక్షిక న్యాయ సారాంశం (స్థిరపడిన చట్టం)',
    section2Title: '2. అధికారిక మూలం: సేకరించిన ప్రాథమిక న్యాయ తీర్పులు',
    section3Title: '3. అధికారిక మూలం: చట్టబద్ధమైన నిబంధనలు & శాసన సవరణలు',
    translationNoticePill: 'న్యాయ అనువాద గమనిక: ఛాంబర్స్ అధ్యయనం కొరకు మాత్రమే • అధికారిక నివేదిక ఆంగ్లంలో ప్రామాణికమైనది',
    translationEnginePrefix: 'అనువాద ఇంజిన్:',
    showOriginalEnglishBtn: 'అసలు ఆంగ్ల పాఠం చూడండి',
    showTranslatedBtn: 'తెలుగు వివరణ చూడండి',
    sourceLawIntegrityBanner: 'న్యాయ సమగ్రత ప్రమాణం: అసలు తీర్పులు మరియు చట్టాలు AI రూపొందించిన విశ్లేషణ నుండి ఖచ్చితంగా వేరు చేయబడ్డాయి.',
    copyCitation: 'సైటేషన్ కాపీ చేయండి',
    citationCopied: 'కాపీ చేయబడింది!',
    pinToDossier: 'డాజియర్‌కు పిన్ చేయండి',
    pinned: 'డాకెట్‌కు చేర్చబడింది',
  },
};

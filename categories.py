"""SOR category classification.

The official SOR dataset (chss_sor_2023.csv) has no category column. Categories
are derived at seed time from the treatment / procedure name using the ordered
keyword rules below. The first matching rule wins; anything unmatched falls
back to ``DEFAULT_CATEGORY``.
"""

DEFAULT_CATEGORY = "Others"

# The CSV orders entries in specialty blocks with a continuous running number.
# The laboratory and imaging blocks are fully unambiguous, so entries in these
# numeric ranges are mapped directly regardless of the item name.
_LABORATORY_RANGE = (1496, 1969)
_RADIOLOGY_RANGE = (1970, 2154)

CATEGORY_ORDER = [
    "Vaccination",
    "Dental",
    "Radiology & Imaging",
    "Ophthalmology",
    "ENT",
    "Oncology & Radiotherapy",
    "Cardiology & Cardiac Surgery",
    "Orthopaedics",
    "Neurology & Neurosurgery",
    "Urology",
    "Gynaecology & Obstetrics",
    "Dermatology",
    "Plastic & Reconstructive Surgery",
    "Anaesthesia",
    "Pain Management",
    "Neonatology & Paediatrics",
    "Gastroenterology",
    "Respiratory",
    "Physiotherapy & Rehabilitation",
    "Psychiatry",
    "General Surgery",
    "General & Miscellaneous",
    "Laboratory",
]

# Rules are evaluated in order; the first matching category wins.
_RULES = [
    (
        "Vaccination",
        [
            "vaccine", "vaccination", "immunization", "immunisation",
            "bcg", "opv", "ipv", "dpt", "mmr", "polio", "varicella",
            "rabies", "tetanus", "meningococcal", "rota virus",
            "papilloma", "diphtheria", "pertussis", "measles", "hib",
            "hepatitis-b",
        ],
    ),
    (
        "Dental",
        [
            "tooth", "teeth", "dental", "denture", "root can", "scaling",
            "gingivectomy", "alveolectomy", "apicotomy", "obturator",
            "frenectomy", "vestibuloplasty", "molar", "dental crown",
            "filling", "extraction", "space maintainer", "periapical",
            "opg", "occlusal", "inlay", "i & d under", "orthodontic",
            "gingival", "periodont",
        ],
    ),
    (
        "Radiology & Imaging",
        [
            "x-ray", "radiograph", "c.t.", "mri", "ultrasound",
            "ultra sound", "sonography", "sonomammography",
            "mammography", "scan", "fluoroscop", "venogram",
            "myelogram", "urogram", "sialogram", "sinogram",
            "fistulogram", "cholangiograph", "pyelogram", "pyelograph",
            "doppler", "bmd", "bone densit", "ebus", "nuclear", "ivp",
            "ivu", "rgu", "angioembolisation", "imaging", "pet",
            "spect", "dsa", "tomography",
        ],
    ),
    (
        "Ophthalmology",
        [
            "eye", "cornea", "corneal", "kerato", "cataract", "glaucoma",
            "retina", "retinal", "vitrect", "lens", "iris", "eyelid",
            "orbit", "orbital", "pterygium", "lacrimal", "squint",
            "strabism", "ophthalm", "sclera", "cyclocryo",
            "trabeculectomy", "iridectomy", "enucleation",
            "evisceration", "conjunctival", "dacryo", "fundus", "iol",
            "macula",             "optic nerve", "retcam", "erg", "vep",
            "laser photo", "retinopexy", "vitreo", "gonioscopy",
            "pachymetry", "tonometry", "vision therapy", "yag",
            "amniotic membrane", "canthoplasty", "epilation",
            "hordeolum", "punctoplasty", "goniotomy", "cryopexy",
            "socket", "argon", "electroretinograph", "keratectom",
            "ectropion", "entropion", "ptosis",
        ],
    ),
    (
        "ENT",
        [
            "nose", "nasal", "sinus", "larynx", "laryngeal",
            "laryngo", "pharynx", "pharyngeal", "pharyngo", "tonsil",
            "adenoid", "mastoid", "stapes", "cochlear", "vocal",
            "tinnitus", "rhino", "tympan", "parotid", "submandibular",
            "salivary", "sial", "turbinate", "choanal", "stroboscopy",
            "audiometry", "auditory", "ossicular", "uvulo",
            "uvulectomy", "styloid", "myringotomy", "grommet", "aural",
            "hearing aid", "endolymphatic", "vestibular", "tracheo",
            "tracheal", "tracheostom", "cordectomy", "laryngopharyng",
            "atticotomy", "oropharyngeal", "nasopharynx", "palate",
            "uvulopalato", "antrostomy", "antral", "turbinoplasty",
            "suspension laryngoscopic", "peritonsillar",
            "retropharyngeal", "choana", "epley", "meatoplasty",
            "myringoplasty", "ossiculoplasty", "tone decay",
            "antroscopy", "epistaxis", "caldwell", "s.m.r",
            "diathermy", "cord lateralisation", "te puncture",
            "thyroplasty", "cochleography", "labyrinth", "staped",
            "maxillectomy", "laryngectom", "glossectom",
            "nystagmograph", "neck dissection", "omohyoid",
            "septoplasty", "ear lobe", "ear reconstruction",
            "removal - ear", "clearance ear", "middle ear",
            "inner ear", "external ear", "otoplast",
        ],
    ),
    (
        "Oncology & Radiotherapy",
        [
            "cancer", "carcinoma", "oncol", "chemotherapy", "chemo",
            "radiotherapy", "radiation", "brachy", "cobalt", "imrt",
            "igrt", "vmat", "imat", "prrt", "linear accelerator",
            "stereotactic radio", "cyber knife", "cyberknife",
            "bone marrow transplant", "microwave ablation",
            "irradiation", "hipec", "melanoma", "leuk", "lymphoma",
            "sarcoma", "glioma", "selectron", "electron beam",
            "planning", "therapy (package", "radionuclide", "chemoport",
            "chemo port", "radio surgery", "rfa) for", "ca.",
            "tele therapy",
        ],
    ),
    (
        "Cardiology & Cardiac Surgery",
        [
            "cardiac", "cardi", "heart", "coronary", "aortic", "aorta",
            "angioplasty", "pacemaker", "defibrill", "valve", "valvulo",
            "atrial", "ventricular", "arrhythm", "echo", "treadmill",
            "holter", "stress test", "stress study", "ffr", "ptca",
            "cabg", "aicd", "tavi", "cardioversion", "pericardial",
            "pericardiocentesis", "aneurysm", "endarterectomy",
            "thoracotomy", "thoracoscopy", "vats", "mediastin",
            "pneumonectomy", "bilobectomy", "endovascular",
            "balloon pump", "ecg", "intraaortic", "pulse generator",
            "stent graft", "angiogram", "angiography", "myocard",
            "rotablation", "electrophysiology", "ep study", "rf ablation",
            "bypass", "eps", "bp monitoring", "loop recorder",
            "varicose", "thoracic", "decortication", "profundo",
            "ambulatory bp", "thymect", "asd", "pda",
        ],
    ),
    (
        "Orthopaedics",
        [
            "ortho", "bone", "fracture", "osteo", "arthro", "arthroscop",
            "ligament", "tendon", "muscle", "hip", "knee", "ankle",
            "shoulder", "elbow", "wrist", "spinal fusion", "scoliosis",
            "lumbar interbody", "spinal surgery", "vertebr",
            "costo transversectomy", "decompression instrumentation",
            "amputation", "joint", "splint", "plaster", "pop", "cast",
            "traction", "disc", "k wire", "k'wire", "k'wiring",
            "clavicle", "femur", "tibia", "humerus", "radius", "ulna",
            "patella", "calcaneal", "scapula", "pelvic", "sacrum",
            "carpal", "tarsal", "metatarsal", "tendo achilles",
            "rotator cuff", "meniscal", "meniscectom", "cruciate",
            "synovectomy", "chondro", "fracture", "skeletal traction",
            "skin traction", "subluxation", "dislocation", "myotomy",
            "osteotom", "tenotomi", "fasciotomy", "nail avulsion",
            "strapping", "trigger finger", "acromioclavicular", "condyle",
            "tension band", "de quervain", "galeazzi", "pinning",
            "acetabulum", "blair", "club foot", "ctev", "stendler",
            "subtalar", "triple fusion", "laminoplasty", "pedicular",
            "kyphoplasty", "tkr", "open reduction", "amputation",
            "carpectom", "fibulectom", "hammer toe", "hallux",
            "talectom", "laminectom", "multi level decompression",
            "instrumental fixation",
        ],
    ),
    (
        "Neurology & Neurosurgery",
        [
            "brain", "cranial", "cranio", "crani", "skull", "cerebral",
            "cerebellum", "intracranial", "ventricul", "mening",
            "subdural", "extradural", "intradural", "neuro", "nerve",
            "carpal tunnel", "spinal", "spine", "trigeminal",
            "stereotactic", "hydrocephalus", "cisternal", "plexus",
            "neuroma", "cauda equina", "pituitary", "spinal cord",
            "malformation", "sympathect", "sympathetect", "lumbar puncture", "epilepsy",
            "myelomeningocele", "craniostomy", "craniotomy",
            "v.p.shunt", "vp shunt", "ventriculoperitonial shunt",
            "ventriculo peritoneal shunt", "intracerebral", "intramedulary", "tentorial", "ganglion cyst",
            "deep brain", "electroencephal", "eng", "eeg", "emg", "ncv",
            "evoked potential", "bilateral reimplant", "neurectomy",
            "nerve graft", "nerve repair", "rhizotomy", "neuralgia",
            "dystonia", "spasticity", "epileptic", "status epilepticus",
            "menigioma", "astrocytom", "ependymom", "acoustic",
            "microvascular decompression", "lumbar pressure", "icp",
            "e.e.g",
        ],
    ),
    (
        "Urology",
        [
            "urethra", "ureter", "uretero", "urinary", "urine", "bladder",
            "cysto", "nephro", "nephrectomy", "kidney", "renal",
            "prostate", "turp", "lithotripsy", "calculi", "calculus",
            "urolith", "vasectomy", "vasoepididymal", "vasography",
            "varicocele", "epididym", "testicular", "testis", "scrotum",
            "scrotal", "hydrocoele", "penile", "penis", "phimosis",
            "circumcision", "haemodialysis", "dialysis", "capd", "crrt",
            "a v fistula", "av fistula", "uroflowmetry", "urologic",
            "urology", "vesical", "cystoplasty", "spermatic",
            "spermatocele", "orchidopexy", "orchid", "hypogonadism",
            "catheterisation", "catheterization", "urological",
            "ureterolithotomy", "pyelolithotomy", "pyeloplasty",
            "nephrolithotomy", "hydronephrosis", "prostatic",
            "hypospadias", "urethroplasty", "urethrotomy", "uro dynamic",
            "cavernos", "dorsal slit", "cryofreezing", "femoral access",
            "subclavian access", "meatotomy", "genitoplasty", "magpi",
            "priapism", "d j",
        ],
    ),
    (
        "Gynaecology & Obstetrics",
        [
            "gynae", "gyne", "hysterect", "uterus", "uterine", "ovarian",
            "ovary", "tubal", "fallopian", "colpo", "vagin", "vulvect",
            "vulval", "cervix", "cervical encirclage", "caesarean",
            "cesarean", "caesarian", "pregnancy", "pregnant", "obstetric",
            "delivery", "amniocentesis", "chorionic villous",
            "cordocentesis", "foetal", "fetal", "endometri",
            "menstrual", "fibroid", "myomect", "oophor", "salping",
            "tubectomy", "sterilisation", "sterilization",
            "intra uterine", "iucd", "hysteroscopy", "hysterosalpingo",
            "colposcopy", "embryo", "ivf", "iui", "episiotomy",
            "perineal", "placenta", "vesicular mole", "ectopic",
            "molar pregnancy", "prenatal", "antenatal", "anovulatory",
            "polycystic ovarian", "pcod", "labour", "uterovaginal",
            "vault", "ovarian drilling", "oocyte", "surrogacy",
            "lithopede", "puerperal", "lochia", "culdocentesis",
            "hymenectom", "oopherectom", "curettage",
            "dilatation & curettage", "d&c",
        ],
    ),
    (
        "Dermatology",
        [
            "skin", "derm", "vitiligo", "wart", "verruca", "molluscum",
            "electrocautr", "chemical cautery", "cautery", "prick test",
            "patch test", "allergen", "allergy", "psoriasis", "eczema",
            "fungal scraping", "tzanck", "podophyllin", "puva", "uvb",
            "phototherapy", "photo therapy", "cryo therapy", "hair",
            "scalp", "alopecia", "onycho", "nail",
            "haemangioma", "keloid", "scar", "naevus", "nevus", "lentigo",
            "dermatophyt", "sebaceous cyst", "pilar cyst", "lipoma",
            "mole", "nevus", "acrochordon", "fibroma", "mycosis",
            "leprosy", "lepra", "urticaria", "ichthyosis",
            "hyperpigmentation", "hypopigmentation", "scleroderm",
            "lupus", "sarcoid", "rosacea", "cellulitis", "abscess",
            "boil", "carbuncle", "hidradenitis", "folliculitis",
        ],
    ),
    (
        "Plastic & Reconstructive Surgery",
        [
            "plastic", "reconstruc", "flap", "graft", "burn", "cleft",
            "rhinoplasty", "abdominoplasty", "liposuction", "mammoplast",
            "breast", "dermabrasion", "escharotomy", "escharectomy",
            "z plasty", "replantation", "microvascular flap",
            "tissue expansion", "resurfacing", "collagen application",
            "contracture", "ssg", "alveolar bone graft", "tm joint",
            "mandible", "maxilla", "maxillofacial", "lip", "palatoplast",
            "phalloplasty", "vaginal reconstruction", "ear reconstruction",
            "nose reconstruction", "eyebrow", "free flap", "pedicled",
            "microtia", "gynecomastia", "pectus", "scar revision",
            "degloving", "avulsion", "amputation", "blepharoplasty",
            "reimplant", "revascularis", "frontal advancement",
            "arch bar", "assymetry", "alar correction", "campodactyly",
            "mandibulectom",
        ],
    ),
    (
        "Pain Management",
        [
            "facet joint", "epidural steroid", "steroid injection",
            "intrathecal", "medial branch", "impar block", "trigger point",
            "joint injection", "plantar fasciitis", "nerve injection",
            "plexus block", "regional nerve block", "nerve block",
            "tendinitis injection", "thermal radiofrequency",
            "sympathetic ganglion", "ganglion impar", "pain",
            "radiofrequency ablation for", "transforaminal",
            "neuromodulation", "spinal cord stimulation",
        ],
    ),
    (
        "Neonatology & Paediatrics",
        [
            "neonat", "neonatal", "paediatric", "pediatric", "child",
            "infant", "newborn", "incubator", "surfactant",
            "exchange transfusion", "meconium", "congenital",
            "intussusception", "hirschsprung", "pyloric stenosis",
            "pyloromyotomy", "anorectal malformation", "psarp",
            "imperforate", "omphalocele", "gastroschisis",
            "duodenal atresia", "oesophageal atresia", "tracheo-oesophageal",
            "tracheoesophageal", "tef", "sacrococcygeal teratoma",
            "branchial", "cystic hygroma", "tongue tie", "ladd's",
            "herniotomies", "hydrocoele", "kasal", "kasai",
            "portoenterostomy", "thalassemia", "thalassaemia",
            "sickle",             "g6pd", "phenylketonuria", "galactosemia",
            "down syndrome", "rickets", "adenoidectomy", "tonsillectomy",
            "umbilical cannulation",
        ],
    ),
    (
        "Gastroenterology",
        [
            "gastro", "oesophago", "esophago", "oesophag", "esophag",
            "endoscopy", "endoscope", "sigmoid", "colono", "procto",
            "liver", "hepatic", "pancreat", "choledoch", "cholecyst",
            "biliar", "hepato",             "gastrostomy", "peg tube", "sengstaken",
            "stoma", "paracentesis", "cirrhosis", "portal hypertension",
            "tace", "tare", "tips", "polypectomy", "fundoplication",
            "duodenal", "duodenostom", "gastric", "splen", "colectomy",
            "ph monitoring", "argon beam", "bowel", "intestine",
            "intestinal", "mesenteric", "peritonitis", "peritoneal",
            "hepatitis", "gall bladder", "gallbladder", "biliary",
            "lithotripsy", "cholangiograph", "jaundice", "ascites",
            "rectum", "rectal", "anal sphincter", "anal stretch",
            "transanal", "anus", "fissure", "fistula",
            "haemorrhoid", "hemorrhoid", "piles", "ileo", "ileostomy",
            "ileal", "cecal", "caecum", "appendix", "appendic",
            "hernia", "herniorrhaphy", "hiatus", "diaphragm",
            "inguinal", "umbilical", "ventral", "incisional",
            "paraumbilical", "oesophago-gastrectomy", "pouch",
            "enteroscopy", "sclerotherapy", "ercp", "ryles tube",
            "vagotomy", "pyloroplasty", "ivor", "gastrectom",
            "hepatectom", "peritonectom", "rectopexy",
            "porta caval", "portosystemic", "spleno renal",
            "portal shunt", "shunt surgery",
        ],
    ),
    (
        "Respiratory",
        [
            "bronch", "bipap", "c-pap", "cpap", "spirometry",
            "peak flow", "dlco", "d.l.c.o", "feno", "chest tube", "pleural",
            "thoracentesis", "oxygen", "nebulis", "nebuliz", "inhal",
            "ventilator", "pulse oximetry", "oximeter", "lung function",
            "pulmonary function", "airway", "respiratory",
            "alveolar lavage", "broncho", "pleurodesis",
        ],
    ),
    (
        "Physiotherapy & Rehabilitation",
        [
            "physiotherapy", "physio", "rehabilitation", "rehab",
            "occupational therapy", "speech therapy", "exercise therapy",
            "hydrotherapy", "electrotherapy", "mobilization",
            "mobilisation", "functional training", "gait",
            "muscle strengthening", "range of motion", "speech",
        ],
    ),
    (
        "Psychiatry",
        [
            "psych", "mental health", "mental retardation", "mental illness",
            "behaviour", "behavior", "counselling",
            "counseling", "autism", "dyslexia", "e.c.t",
            "narcotherapy", "cognitive", "group therapy", "family therapy",
            "psychological", "rehabilitation counselling", "i.q",
            "iq assessment", "anxiety", "depression", "bipolar",
            "schizophrenia", "psychosis", "addiction", "substance abuse",
            "sleep disorder", "insomnia", "attention deficit", "adhd",
            "learning disability", "behavioural", "behavioral",
            "psychotherapist", "psychotherapy", "psychiatrist",
            "assessment (limited", "assessment (not more",
        ],
    ),
    (
        "General Surgery",
        [
            "surgery", "surgical", "operation", "resection", "excision",
            "biopsy", "removal", "repair", "anastomosis", "colostomy",
            "ileostomy", "stoma", "mastectomy", "thyroidectom",
            "parathyroidectom", "lymph node", "lymphadenectomy",
            "lumpectomy", "appendicect", "laparotomy", "laparoscopy",
            "laparoscopic", "lavage", "abscess", "drainage", "incision",
            "perforation", "adhesion", "cyst", "polyp", "haemorrhoid",
            "hemorrhoid", "piles", "proctolog", "anal", "anus", "rectal",
            "rectum", "sphincter", "wound", "suture", "debridement",
            "omental", "omentum", "mesentery", "sebaceous", "lipoma",
            "hydatid", "echinococc", "foreign body", "fistulectomy",
            "fistulotomy", "exploration", "exploratory", "spigelian",
            "pilonidal", "sinus tract", "groin", "inguinal lymph",
            "femoral hernia", "epigastric", "diverticulectomy",
            "diverticulum", "stricturoplasty", "resection and anastomosis",
            "bowel resection", "thyroid", "parathyroid", "adrenal",
            "endocrine", "necrosis", "necrosectomy", "sequestrectomy",
            "toilet", "curottage", "curettage", "surgical toilet",
            "i & d", "eua", "seton", "sutur", "coagulator",
            "procedures done", "sitz bath", "laproscopic", "anoplasty",
            "venesection", "rrhoid", "embolectom",
        ],
    ),
    (
        "General & Miscellaneous",
        [
            "bandage", "dressing", "enema", "douche", "glucometer",
            "glucose monitoring", "dvt", "stoma care", "colostomy care",
            "machine", "wheelchair", "walker", "corset", "mattress",
            "belt", "chair", "diet", "bed", "monitoring system",
            "glucose monitor", "insulin pump", "syringe", "ampule",
            "vial", "disposable", "gloves", "mask", "gown", "catheter",
            "splint", "stocking", "crepe", "gauze", "cotton", "spirit",
            "ointment", "lotion", "cream", "gel", "powder", "tablet",
            "capsule", "injection", "infusion", "iv fluids", "saline",
            "ringer", "dextrose", "oxygen", "dietary", "nutrition",
            "feeding", "food", "formula", "infra red", "mortuary",
            "intraosseous", "cvad",
        ],
    ),
    (
        "Anaesthesia",
        [
            "anaesthesia", "anesthesia", "analgesia", "sedation",
            "epidural", "intubation", "cannulation", "stellate",
            "peripheral nerve block", "arterial line", "anaesthetic",
            "anesthetic", "monitored anaesthesia", "general anaesthesia",
        ],
    ),
    (
        "Laboratory",
        [
            "test", "test for", "blood", "serum", "plasma", "urine",
            "urinary", "stool", "sputum", "culture", "smear", "count",
            "level", "hormone", "antibody", "antigen", "profile", "panel",
            "electrophores", "assay", "estimation", "screening", "marker",
            "hpe", "fnac", "cytology", "histopath", "pathology",
            "immuno", "immunoglob", "pcr", "elisa", "esr", "haemoglobin",
            "hemoglobin", "hla", "karyotyp", "vitamin", "glucose", "sugar",
            "protein", "albumin", "bilirubin", "enzyme", "amylase",
            "lipase", "creatinine", "urea", "uric acid", "electrolyte",
            "sodium", "potassium", "calcium", "phosphate", "magnesium",
            "iron", "ferritin", "thyroid", "thyroxine", "tsh", "cortisol",
            "aldosterone", "renin", "insulin", "c-peptide", "troponin",
            "crp", "d-dimer", "fibrinogen", "platelet", "reticulocyte",
            "prothrombin", "coagulation", "bleeding time", "clotting",
            "cross match", "blood group", "compatibility", "hepatitis",
            "hiv", "vdrl", "widal", "malaria", "dengue", "typhoid",
            "afb", "tubercul", "microscopy", "sensitivity", "abg",
            "osmolality", "osmotic fragility", "sickling", "serology",
            "tissue typing", "quantitative", "qualitative", "fractionation",
            "genetic", "gene mutation", "chromosom", "dna", "rna",
            "metabolite", "catecholamine", "vma", "5 hiaa",
            "ketosteroid", "drug level", "therapeutic drug", "trough",
            "peak level", "hormone", "glucose tolerance", "fbs", "ppbs",
            "hba1c", "ghb", "ldh", "sgpt", "sgot", "ggt", "afp", "cea",
            "psa", "hcg", "prolactin", "testosterone", "estrogen",
            "estradiol", "progesterone", "fsh", "lh", "dhea", "igf",
            "growth hormone", "insulin antibody", "gad", "ana", "anca",
            "antinuclear", "rheumatoid", "autoantibody", "hormonal",
            "metabolic panel", "lipid profile", "thyroid profile",
            "hormone profile", "androgen", "glycosylated", "glycated",
            "urine analysis", "routine analysis", "body fluid",
            "asciitc fluid", "cerebrospinal", "csf", "peripheral smear",
            "bone marrow aspiration", "bone marrow smear", "stem cell",
            "flow cytometry", "pcr", "rt-pcr", "microarray", "sequencing",
            "abg blood gas", "arterial blood gas", "blood gas analysis",
            "rbs", "random blood sugar", "post prandial",
            "fasting blood", "homa", "leptin", "adiponectin", "apoe",
            "apo", "lipoprotein", "chylomicron", "triglyceride",
            "cholesterol", "hdl", "ldl", "vldl", "homocysteine",
            "methylmalonic", "folate", "b12", "vitamin d", "vitamin b",
            "zinc", "copper", "selenium", "chromium", "manganese",
            "trace element", "heavy metal", "toxicolog", "poison",
            "ethanol", "alcohol", "paracetamol", "salicylate",
            "drug screen", "drug screening", "tlc", "dlc", "cbc",
            "total count", "differential count", "packed cell", "pcv",
            "mcv", "mch", "rdw", "red cell", "white cell", "leukocyte",
            "neutrophil", "lymphocyte", "eosinophil", "basophil",
            "monocyte", "band cell", "plasma cell", "blast cell",
            "hemato", "haemato", "hematolog", "haematolog",
        ],
    ),
]


def classify_category(name, sor_code=None):
    """Return the best category for a SOR item.

    ``sor_code`` is optional; when provided and numeric it is used to apply
    the dataset block overrides for the laboratory and imaging sections.
    """
    if sor_code is not None:
        try:
            code = int(str(sor_code).strip())
        except (TypeError, ValueError):
            code = None
        if code is not None:
            if _LABORATORY_RANGE[0] <= code <= _LABORATORY_RANGE[1]:
                return "Laboratory"
            if _RADIOLOGY_RANGE[0] <= code <= _RADIOLOGY_RANGE[1]:
                return "Radiology & Imaging"

    # Names often embed notes after a "|" separator (guidelines, inclusions,
    # eligibility etc.). Only the leading segment is the service name itself.
    text = (name or "").split("|", 1)[0].lower()
    if not text:
        return DEFAULT_CATEGORY
    # "E.C.T." (electroconvulsive therapy) contains "c.t." and would otherwise
    # be matched by the imaging rule; it is a psychiatric procedure.
    if "e.c.t" in text:
        return "Psychiatry"
    for category, keywords in _RULES:
        if any(keyword in text for keyword in keywords):
            return category
    return DEFAULT_CATEGORY


def sort_categories(categories):
    """Return categories sorted by display order (Others last)."""
    index = {name: i for i, name in enumerate(CATEGORY_ORDER)}
    known = sorted(
        (c for c in categories if c in index),
        key=lambda c: index[c],
    )
    unknown = sorted(c for c in categories if c not in index and c != DEFAULT_CATEGORY)
    others = [DEFAULT_CATEGORY] if DEFAULT_CATEGORY in categories else []
    return known + unknown + others

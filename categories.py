"""SOR category classification.

The SOR dataset has categories pre-assigned in the database. This module
provides:

* ``CATEGORY_ORDER`` — display order for the category dropdown / filters.
* ``classify_category()`` — keyword-based fallback for fresh CSV seeding or
  Excel imports that lack a category column.
* ``sort_categories()`` — sort a list of category names by display order.
"""

DEFAULT_CATEGORY = "Others"

# Display order for the 66 categories.  Groups are arranged logically:
# Clinical specialties → Paediatrics → Radiology & Imaging → Pathology →
# Body fluids → Vaccinations → Others.
CATEGORY_ORDER = [
    # -- Clinical specialties (alphabetical) --
    "Anaesthesiology",
    "Cardiology",
    "CVTS",
    "CVTS Paediatric",
    "Dentistry",
    "Dermatology",
    "ENT-Ear",
    "ENT-Ear: Hearing Aids",
    "ENT-General",
    "ENT-Nose",
    "ENT-Throat",
    "Gastro-Enterology",
    "General Medicine",
    "General Procedure",
    "General Surgery",
    "Gynaecology",
    "Histopathology",
    "Interventional Radiology",
    "NEPHROLOGY",
    "Neonatal Surgery",
    "Neonatology",
    "Neurology",
    "Neurosurgery",
    "Obstetrics",
    "Oncology",
    "Oncology-Robotic Surgery",
    "Ophthalmology",
    "Orthopaedics",
    "PAEDIATRIC SURGERY",
    "PAEDIATRIC SURGERY - GIT",
    "PAEDIATRIC SURGERY - HEAD & NECK",
    "PAEDIATRIC SURGERY - HERNIAS",
    "PAEDIATRIC SURGERY - THORAX",
    "PAEDIATRIC SURGERY - UROLOGY",
    "PAEDIATRIC SURGERY- HEPATOBILIARY & PANCREATIC",
    "PAEDIATRICS",
    "Pain Management",
    "PHYSIOTHERAPY",
    "PLASTIC SURGERY",
    "PSYCHIATRY",
    "UROLOGY",
    # -- Radiology & Imaging --
    "BMD",
    "C. T. - SPECIAL",
    "C. T. SCAN",
    "DOPPLER",
    "MRI",
    "MRI-Special",
    "NUCLEAR MEDICINE",
    "NUCLEAR MEDICINE- Thyrotoxicosis Therapy",
    "PET",
    "Radiology",
    "Radiology - Routine X-Ray",
    "Radiology-Special Investigation",
    "Ultrasound",
    "Ultrasound-Special",
    # -- Pathology & Laboratory --
    "Bio-Chemistry",
    "Blood banking",
    "Clinical Pathology",
    "CSF",
    "Microbiology",
    "Special Tests",
    # -- Body fluids --
    "Semen",
    "Stool",
    "Urine",
    # -- Vaccinations --
    "VACCINATIONS",
    "VACCINATIONS (inadmissible)",
]

# Keyword rules for auto-classifying items when the category is missing
# (e.g. fresh CSV seed or Excel import without a category column).
# Rules are evaluated in order; the first matching category wins.
_RULES = [
    (
        "VACCINATIONS",
        [
            "vaccine", "vaccination", "immunization", "immunisation",
            "bcg", "opv", "ipv", "dpt", "mmr", "polio", "varicella",
            "rabies", "tetanus", "meningococcal", "rota virus",
            "papilloma", "diphtheria", "pertussis", "measles", "hib",
            "hepatitis-b",
        ],
    ),
    (
        "Dentistry",
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
        "C. T. SCAN",
        [
            "c.t.", "ct scan", "ct abdomen", "ct brain", "ct chest",
            "ct guided", "computed tomography",
        ],
    ),
    (
        "C. T. - SPECIAL",
        [
            "ct enteroclysis", "ct cisternography", "ct cardiac",
            "ct angiogram", "ct duel", "ct pelvis", "ct sinogram",
        ],
    ),
    (
        "MRI",
        [
            "mri", "magnetic resonance",
        ],
    ),
    (
        "MRI-Special",
        [
            "mra", "mri angiogram", "mri mr spectroscopy",
            "mri functional",
        ],
    ),
    (
        "Ultrasound-Special",
        [
            "ante-natal", "anomaly scan", "doppler study",
            "endoscopic bronchial ultrasound", "ebus",
            "transesophageal ultrasound", "endorinal ultrasound",
        ],
    ),
    (
        "Ultrasound",
        [
            "ultrasound", "ultra sound", "sonography",
            "sonomammography", "usg",
        ],
    ),
    (
        "DOPPLER",
        [
            "doppler", "colour doppler",
        ],
    ),
    (
        "BMD",
        [
            "bmd", "bone densit", "dexa scan",
        ],
    ),
    (
        "PET",
        [
            "pet scan", "p e t", "pet ct", "pet brain", "pet cardiac",
        ],
    ),
    (
        "NUCLEAR MEDICINE- Thyrotoxicosis Therapy",
        [
            "i-131", "thyrotoxicosis therapy", "radioactive iodine",
        ],
    ),
    (
        "NUCLEAR MEDICINE",
        [
            "nuclear medicine", "bone scan", "thyroid scan",
            "renal scan", "gallium scan", "ventilation perfusion",
            "v q scan", "mibi", "spect",
        ],
    ),
    (
        "Radiology - Routine X-Ray",
        [
            "x-ray", "x'ray", "radiograph", "xray",
        ],
    ),
    (
        "Radiology-Special Investigation",
        [
            "barium", "ivp", "ivu", "rgu", "mcu", "rgc",
            "fistulogram", "sinogram", "venogram", "myelogram",
            "sialogram", "cholangiograph", "pyelogram", "pyelograph",
            "urogram", "fluoroscop",
        ],
    ),
    (
        "Interventional Radiology",
        [
            "angioembolisation", "ivc filter", "interventional radiology",
            "tace", "tare", "tips", "embolisation",
        ],
    ),
    (
        "Radiology",
        [
            "radiology", "portable", "c arm",
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
            "macula", "optic nerve", "retcam", "erg", "vep",
            "laser photo", "retinopexy", "vitreo", "gonioscopy",
            "pachymetry", "tonometry", "vision therapy", "yag",
            "amniotic membrane", "canthoplasty", "epilation",
            "hordeolum", "punctoplasty", "goniotomy", "cryopexy",
            "socket", "argon", "electroretinograph", "keratectom",
            "ectropion", "entropion", "ptosis",
        ],
    ),
    (
        "ENT-Ear",
        [
            "audiometry", "auditory", "ossicular", "myringotomy",
            "grommet", "aural", "hearing aid", "endolymphatic",
            "vestibular", "atticotomy", "stapes", "cochlear",
            "tinnitus", "mastoid", "ossiculoplasty", "tone decay",
            "antroscopy", "meatoplasty", "myringoplasty",
            "middle ear", "inner ear", "external ear", "otoplast",
            "ear lobe", "ear reconstruction", "removal - ear",
            "clearance ear", "stapedectomy",
        ],
    ),
    (
        "ENT-Nose",
        [
            "nose", "nasal", "sinus", "rhino", "turbinate", "choanal",
            "antrostomy", "antral", "turbinoplasty", "septoplasty",
            "epistaxis", "caldwell", "s.m.r", "maxillectomy",
            "nasopharynx", "antroscopy", "antral wash",
        ],
    ),
    (
        "ENT-Throat",
        [
            "larynx", "laryngeal", "laryngo", "pharynx", "pharyngeal",
            "pharyngo", "tonsil", "adenoid", "vocal", "uvulo",
            "uvulectomy", "styloid", "tracheo", "tracheal",
            "tracheostom", "cordectomy", "laryngopharyng",
            "oropharyngeal", "palate", "uvulopalato",
            "suspension laryngoscopic", "peritonsillar",
            "retropharyngeal", "choana", "thyroplasty",
            "stroboscopy", "cord lateralisation",
        ],
    ),
    (
        "ENT-General",
        [
            "parotid", "submandibular", "salivary", "sial",
            "neck dissection", "omohyoid", "debridement",
            "adenotonsillectomy",
        ],
    ),
    (
        "Oncology",
        [
            "cancer", "carcinoma", "oncol", "chemotherapy", "chemo",
            "radiotherapy", "radiation", "brachy", "cobalt", "imrt",
            "igrt", "vmat", "imat", "prrt", "linear accelerator",
            "stereotactic radio", "cyber knife", "cyberknife",
            "bone marrow transplant", "microwave ablation",
            "irradiation", "hipec", "melanoma", "leuk", "lymphoma",
            "sarcoma", "glioma", "selectron", "electron beam",
            "planning", "radionuclide", "chemoport", "chemo port",
            "radio surgery", "ca.", "tele therapy",
        ],
    ),
    (
        "Oncology-Robotic Surgery",
        [
            "robotic surgery",
        ],
    ),
    (
        "Cardiology",
        [
            "cardiac", "cardi", "heart", "coronary", "aortic", "aorta",
            "angioplasty", "pacemaker", "defibrill", "valve", "valvulo",
            "atrial", "ventricular", "arrhythm", "echo", "treadmill",
            "holter", "stress test", "stress study", "ffr", "ptca",
            "aicd", "tavi", "cardioversion", "pericardial",
            "pericardiocentesis", "aneurysm", "endarterectomy",
            "balloon pump", "ecg", "intraaortic", "pulse generator",
            "stent graft", "angiogram", "angiography", "myocard",
            "rotablation", "electrophysiology", "ep study", "rf ablation",
            "bypass", "eps", "bp monitoring", "loop recorder",
            "ambulatory bp", "varicose", "asd", "pda",
        ],
    ),
    (
        "CVTS",
        [
            "thoracotomy", "thoracoscopy", "vats", "mediastin",
            "pneumonectomy", "lobectomy", "bilobectomy", "endovascular",
            "thoracic", "decortication", "profundo", "thymect",
            "aneurysm - aortic", "cabg", "valve replacement",
            "mitral", "aortic valve", "tricuspid",
        ],
    ),
    (
        "Orthopaedics",
        [
            "ortho", "bone", "fracture", "osteo", "arthro", "arthroscop",
            "ligament", "tendon", "muscle", "hip", "knee", "ankle",
            "shoulder", "elbow", "wrist", "spinal fusion", "scoliosis",
            "lumbar interbody", "spinal surgery", "vertebr",
            "amputation", "joint", "splint", "plaster", "pop", "cast",
            "traction", "disc", "k wire", "k'wire", "k'wiring",
            "clavicle", "femur", "tibia", "humerus", "radius", "ulna",
            "patella", "calcaneal", "scapula", "pelvic", "sacrum",
            "carpal", "tarsal", "metatarsal", "tendo achilles",
            "rotator cuff", "meniscal", "meniscectom", "cruciate",
            "synovectomy", "chondro", "skeletal traction",
            "skin traction", "subluxation", "dislocation", "myotomy",
            "osteotom", "tenotomi", "fasciotomy", "nail avulsion",
            "strapping", "trigger finger", "acromioclavicular", "condyle",
            "tension band", "de quervain", "galeazzi", "pinning",
            "acetabulum", "blair", "club foot", "ctev", "stendler",
            "subtalar", "triple fusion", "laminoplasty", "pedicular",
            "kyphoplasty", "tkr", "open reduction",
            "carpectom", "fibulectom", "hammer toe", "hallux",
            "talectom", "laminectom", "multi level decompression",
            "instrumental fixation",
        ],
    ),
    (
        "Neurosurgery",
        [
            "brain", "cranial", "cranio", "crani", "skull", "cerebral",
            "cerebellum", "intracranial", "ventricul", "mening",
            "subdural", "extradural", "intradural", "stereotactic",
            "hydrocephalus", "cisternal", "craniostomy", "craniotomy",
            "v.p.shunt", "vp shunt", "ventriculoperitonial shunt",
            "ventriculo peritoneal shunt", "intracerebral",
            "tentorial", "deep brain", "ganglion cyst",
            "microvascular decompression",
        ],
    ),
    (
        "Neurology",
        [
            "neuro", "nerve", "carpal tunnel", "spinal", "spine",
            "trigeminal", "plexus", "neuroma", "cauda equina",
            "pituitary", "spinal cord", "malformation", "sympathect",
            "lumbar puncture", "epilepsy", "myelomeningocele",
            "intramedulary", "electroencephal", "eng", "eeg", "emg",
            "ncv", "evoked potential", "neurectomy", "nerve graft",
            "nerve repair", "rhizotomy", "neuralgia", "dystonia",
            "spasticity", "epileptic", "status epilepticus",
            "menigioma", "astrocytom", "ependymom", "acoustic",
            "lumbar pressure", "icp", "e.e.g", "autonomic function",
            "bera", "brain stem",
        ],
    ),
    (
        "UROLOGY",
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
            "priapism", "d j", "adrenalectomy",
        ],
    ),
    (
        "Gynaecology",
        [
            "gynae", "gyne", "hysterect", "uterus", "uterine", "ovarian",
            "ovary", "tubal", "fallopian", "colpo", "vagin", "vulvect",
            "vulval", "cervix", "cervical encirclage",
            "myomect", "oophor", "salping",
            "tubectomy", "sterilisation", "sterilization",
            "intra uterine", "iucd", "hysteroscopy", "hysterosalpingo",
            "colposcopy", "embryo", "ivf", "iui",
            "perineal", "fibroid", "polycystic ovarian", "pcod",
            "vault", "ovarian drilling", "oocyte",
            "lithopede", "hymenectom", "oopherectom",
        ],
    ),
    (
        "Obstetrics",
        [
            "caesarean", "cesarean", "caesarian", "pregnancy", "pregnant",
            "obstetric", "delivery", "amniocentesis", "chorionic villous",
            "cordocentesis", "foetal", "fetal", "episiotomy",
            "placenta", "vesicular mole", "ectopic",
            "molar pregnancy", "prenatal", "antenatal",
            "labour", "puerperal", "breech",
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
            "mole", "acrochordon", "fibroma", "mycosis",
            "leprosy", "lepra", "urticaria", "ichthyosis",
            "hyperpigmentation", "hypopigmentation", "scleroderm",
            "lupus", "sarcoid", "rosacea", "cellulitis", "abscess",
            "boil", "carbuncle", "hidradenitis", "folliculitis",
        ],
    ),
    (
        "PLASTIC SURGERY",
        [
            "plastic", "reconstruc", "flap", "graft", "burn", "cleft",
            "rhinoplasty", "abdominoplasty", "liposuction", "mammoplast",
            "breast", "dermabrasion", "escharotomy", "escharectomy",
            "z plasty", "replantation", "microvascular flap",
            "tissue expansion", "resurfacing", "collagen application",
            "contracture", "ssg", "alveolar bone graft", "tm joint",
            "mandible", "maxilla", "maxillofacial", "lip", "palatoplast",
            "phalloplasty", "vaginal reconstruction",
            "nose reconstruction", "eyebrow", "free flap", "pedicled",
            "microtia", "gynecomastia", "pectus", "scar revision",
            "degloving", "avulsion", "blepharoplasty",
            "reimplant", "revascularis", "frontal advancement",
            "arch bar", "assymetry", "alar correction", "campodactyly",
            "mandibulectom",
        ],
    ),
    (
        "Anaesthesiology",
        [
            "anaesthesia", "anesthesia", "analgesia", "sedation",
            "epidural", "intubation", "cannulation", "stellate",
            "peripheral nerve block", "arterial line", "anaesthetic",
            "anesthetic", "monitored anaesthesia", "general anaesthesia",
            "caudal block",
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
        "PAEDIATRICS",
        [
            "paediatric", "pediatric", "child", "infant", "newborn",
            "neonat", "neonatal", "incubator", "surfactant",
            "exchange transfusion", "meconium",
        ],
    ),
    (
        "Neonatal Surgery",
        [
            "congenital", "intussusception", "hirschsprung",
            "pyloric stenosis", "pyloromyotomy", "anorectal malformation",
            "psarp", "imperforate", "omphalocele", "gastroschisis",
            "duodenal atresia", "oesophageal atresia",
            "tracheo-oesophageal", "tracheoesophageal", "tef",
            "sacrococcygeal teratoma", "branchial", "cystic hygroma",
            "tongue tie", "ladd's", "herniotomies",
            "portoenterostomy", "kasal", "kasai",
        ],
    ),
    (
        "NEPHROLOGY",
        [
            "haemodialysis", "dialysis", "capd", "crrt",
            "a v fistula", "av fistula", "nephro", "bicarbonate haemodialysis",
        ],
    ),
    (
        "Gastro-Enterology",
        [
            "gastro", "oesophago", "esophago", "oesophag", "esophag",
            "endoscopy", "endoscope", "sigmoid", "colono", "procto",
            "liver", "hepatic", "pancreat", "choledoch", "cholecyst",
            "biliar", "hepato", "gastrostomy", "peg tube", "sengstaken",
            "stoma", "paracentesis", "cirrhosis", "portal hypertension",
            "polypectomy", "fundoplication",
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
        "General Medicine",
        [
            "bandage", "dressing", "enema", "douche", "glucometer",
            "glucose monitoring", "dvt", "stoma care", "colostomy care",
            "machine", "wheelchair", "walker", "corset", "mattress",
            "belt", "chair", "diet", "bed", "monitoring system",
            "glucose monitor", "insulin pump", "syringe", "ampule",
            "vial", "disposable", "gloves", "mask", "gown", "catheter",
            "stocking", "crepe", "gauze", "cotton", "spirit",
            "ointment", "lotion", "cream", "gel", "powder", "tablet",
            "capsule", "injection", "infusion", "iv fluids", "saline",
            "ringer", "dextrose", "oxygen", "dietary", "nutrition",
            "feeding", "food", "formula", "infra red", "mortuary",
            "intraosseous", "cvad", "arterial line",
            "bronch", "bipap", "c-pap", "cpap", "spirometry",
            "peak flow", "dlco", "d.l.c.o", "feno", "chest tube", "pleural",
            "thoracentesis", "nebulis", "nebuliz", "inhal",
            "ventilator", "pulse oximetry", "oximeter", "lung function",
            "pulmonary function", "airway", "respiratory",
            "alveolar lavage", "broncho", "pleurodesis",
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
            "laparoscopic", "lavage", "drainage", "incision",
            "perforation", "adhesion", "cyst", "polyp",
            "proctolog", "anal", "rectal",
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
        "Histopathology",
        [
            "hpe", "histopath", "pathology", "frozen section",
            "bone marrow smear", "bone marrow aspiration",
            "cell block", "cytology", "fnac",
        ],
    ),
    (
        "Clinical Pathology",
        [
            "blood group", "abo", "rh typing", "eosinophil",
            "absolute eosinophil", "bleeding time", "clotting time",
            "esr", "cbc", "tlc", "dlc", "haemoglobin", "hemoglobin",
            "total count", "differential count", "packed cell", "pcv",
            "mcv", "mch", "rdw", "red cell", "white cell", "leukocyte",
            "neutrophil", "lymphocyte", "eosinophil", "basophil",
            "monocyte", "band cell", "plasma cell", "blast cell",
            "peripheral smear", "reticulocyte",
        ],
    ),
    (
        "Bio-Chemistry",
        [
            "test", "test for", "blood", "serum", "plasma",
            "culture", "smear", "count",
            "level", "hormone", "antibody", "antigen", "profile", "panel",
            "electrophores", "assay", "estimation", "screening", "marker",
            "immuno", "immunoglob", "pcr", "elisa",
            "hla", "karyotyp", "vitamin", "glucose", "sugar",
            "protein", "albumin", "bilirubin", "enzyme", "amylase",
            "lipase", "creatinine", "urea", "uric acid", "electrolyte",
            "sodium", "potassium", "calcium", "phosphate", "magnesium",
            "iron", "ferritin", "thyroid", "thyroxine", "tsh", "cortisol",
            "aldosterone", "renin", "insulin", "c-peptide", "troponin",
            "crp", "d-dimer", "fibrinogen", "platelet",
            "prothrombin", "coagulation",
            "cross match", "compatibility", "hepatitis",
            "hiv", "vdrl", "widal", "malaria", "dengue", "typhoid",
            "afb", "tubercul", "microscopy", "sensitivity", "abg",
            "osmolality", "osmotic fragility", "sickling", "serology",
            "tissue typing", "quantitative", "qualitative", "fractionation",
            "genetic", "gene mutation", "chromosom", "dna", "rna",
            "metabolite", "catecholamine", "vma", "5 hiaa",
            "ketosteroid", "drug level", "therapeutic drug", "trough",
            "peak level", "glucose tolerance", "fbs", "ppbs",
            "hba1c", "ghb", "ldh", "sgpt", "sgot", "ggt", "afp", "cea",
            "psa", "hcg", "prolactin", "testosterone", "estrogen",
            "estradiol", "progesterone", "fsh", "lh", "dhea", "igf",
            "growth hormone", "insulin antibody", "gad", "ana", "anca",
            "antinuclear", "rheumatoid", "autoantibody", "hormonal",
            "metabolic panel", "lipid profile", "thyroid profile",
            "hormone profile", "androgen", "glycosylated", "glycated",
            "urine analysis", "routine analysis", "body fluid",
            "asciitc fluid", "cerebrospinal",
            "rbs", "random blood sugar", "post prandial",
            "fasting blood", "homa", "leptin", "adiponectin", "apoe",
            "apo", "lipoprotein", "chylomicron", "triglyceride",
            "cholesterol", "hdl", "ldl", "vldl", "homocysteine",
            "methylmalonic", "folate", "b12", "vitamin d", "vitamin b",
            "zinc", "copper", "selenium", "chromium", "manganese",
            "trace element", "heavy metal", "toxicolog", "poison",
            "ethanol", "alcohol", "paracetamol", "salicylate",
            "drug screen", "drug screening",
            "complement", "fta", "abs",
        ],
    ),
    (
        "Microbiology",
        [
            "culture", "sensitivity", "aerobic", "anaerobic",
            "fungal", "bacterial", "viral", "serology",
            "anti hbe", "hbe ag", "hepatitis",
        ],
    ),
    (
        "Blood banking",
        [
            "blood transfusion", "blood components", "blood bank",
            "bleeding charges", "collection of blood",
        ],
    ),
    (
        "CSF",
        [
            "csf", "c.s.f", "cerebrospinal fluid",
        ],
    ),
    (
        "Special Tests",
        [
            "special test", "complement", "fta", "abs",
            "assa", "immunofluorescence",
        ],
    ),
    (
        "PHYSIOTHERAPY",
        [
            "physiotherapy", "physio", "rehabilitation", "rehab",
            "occupational therapy", "speech therapy", "exercise therapy",
            "hydrotherapy", "electrotherapy", "mobilization",
            "mobilisation", "functional training", "gait",
            "muscle strengthening", "range of motion", "speech",
            "home physiotherapy",
        ],
    ),
    (
        "PSYCHIATRY",
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
]


def classify_category(name, sor_code=None):
    """Return the best category for a SOR item.

    ``sor_code`` is kept for API compatibility but is no longer used for
    block-range overrides (the dataset's sequential numbering has changed).
    """
    text = (name or "").split("|", 1)[0].lower()
    if not text:
        return DEFAULT_CATEGORY
    if "e.c.t" in text:
        return "PSYCHIATRY"
    for category, keywords in _RULES:
        if isinstance(keywords, str):
            # Handle malformed rule (single string instead of list)
            keywords = [keywords]
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

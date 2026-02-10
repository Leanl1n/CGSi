"""Application constants: keywords, columns, output config, paths."""

KEYWORDS = {
    "ID": "Indonesia",
    "SG": "Singapore",
    "TH": "Thailand",
    "MY": "Malaysia",
}

NAME_COLUMN_CANDIDATES = ("Input Name", "input name", "Name", "name", "InputName")

MARKET_BY_CODE = {
    "th": "Thailand",
    "sg": "Singapore",
    "my": "Malaysia",
    "id": "Indonesia",
}

MEDIA_PLATFORM_SOCIAL = {
    "FB": "Facebook",
    "IG": "Instagram",
    "Twitter": "Twitter",
}

OWNED_ACCOUNTS = [
    "ajaib.investasi", "ajaib_investasi", "bnisekuritas46", "bualuangsec",
    "cgscimbth", "cgsi_id", "cgsi_my", "cgsi_sg", "cgsiid", "cgsimy", "cgsisg",
    "cimbmalaysia", "dbsbank", "finansiasyrus", "fnsyrus", "ig.singapore.official",
    "ig_singapore", "igcomsingapore", "indopremier", "indopremieronlinetechnology",
    "innovestx", "innovestxsecurities", "invxsecurities", "k_securities", "kenangagroup",
    "kenangagroupofficial", "kiatnakinphatra", "krungsrisec", "ksecurities",
    "kss.krungsrisecurities", "liberator.co.th", "liberator_securities", "mandiri_olt",
    "mandiri_sekuritas", "maybanksecurities", "maybanksekuritas", "maybanksg",
    "maybanksingapore", "miraeassetid", "miraeassetsekuritas_id", "miraeassetsekuritasid",
    "moomoomalaysia", "moomoosingapore", "mostmandirisekuritas", "mplus.global",
    "mplusonline", "mymaybank", "ocbc.singapore", "ocbcbank", "phillipcapital",
    "phillipcapitalmalaysia", "pi_securities", "pisecurities", "rakutentrade",
    "saxo_singapore", "saxosingapore", "sgmaybank", "sinarmas_sekuritas",
    "sm.sekuritas", "sm_sekuritas", "stockbit", "syfesg", "talktophillip",
    "th_liberator", "tigerbrokerssg", "uobkayhian.sg", "uobkayhianmalaysia",
    "wahedinvest", "yuantathai", "yuantathailand", "yuantaresearchthailand"
]

ENGAGEMENT_COLS = [
    "likes", "shares", "comments", "retweets", "replies",
    "reactions", "threads",
]

OUTPUT_CSV_COLUMNS = (
    "Day",
    "MonthName",
    "Year",
    "Quarter",
    "Date (For Trendline)",
    "Market",
    "Media Platform",
    "Brand",
    "Date",
    "Headline",
    "URL",
    "Hit Sentence",
    "Source",
    "Influencer",
    "Country",
    "Reach",
    "Engagement",
    "AVE",
    "Sentiment",
    "Input Name",
    "Keywords",
    "Media Type",
)

CANONICAL_OUTPUT_COLUMNS = (
    "Market",
    "Media Platform",
    "Brand",
    "Date",
    "Headline",
    "URL",
    "Hit Sentence",
    "Source",
    "Influencer",
    "Country",
    "Reach",
    "Engagement",
    "AVE",
    "Sentiment",
    "Input Name",
    "Keywords",
    "Media Type",
)

OUTPUT_DIR = "output"
OUTPUT_ENCODING = "utf-8-sig"
RAW_DATA_PATH = r"C:\Users\Lerry\Desktop\test\raw_data"
BRAND_JSON_FILENAME = "data/brand.json"

# Encodings to try for CSV (UTF-8, UTF-16, etc.). Used by Annual CSV Merger.
COMMON_ENCODINGS = [
    "utf-8-sig",
    "utf-8",
    "utf-16",
    "utf-16-be",
    "utf-16-le",
    "utf-32",
    "utf-32-be",
    "utf-32-le",
    "cp1252",
    "latin-1",
    "iso-8859-1",
    "cp1250",
    "cp1251",
]

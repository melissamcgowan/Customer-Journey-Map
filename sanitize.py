import json, re, copy

with open("extracted.json") as f:
    data = json.load(f)

TOKEN_MAP = [
    (r"\bSalesForce\b", "CRM"),
    (r"\bSalesforce\b", "CRM"),
    (r"\bSFDC\b", "CRM"),
    (r"\bGS\b", "CSP"),
    (r"\bTechnical Support  \(TS\)", "Technical Support (TS)"),
    (r"\bPatner Manager\b", "Partner Manager"),
    (r"\bleadersthip\b", "leadership"),
]

def sanitize_text(s):
    if not isinstance(s, str):
        return s
    for pattern, repl in TOKEN_MAP:
        s = re.sub(pattern, repl, s)
    return s

def walk(obj):
    if isinstance(obj, str):
        return sanitize_text(obj)
    elif isinstance(obj, list):
        return [walk(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: walk(v) for k, v in obj.items()}
    else:
        return obj

data = walk(data)

# Special-case the champion / stakeholders fields (full replacement, not token-level)
data["sheet1"]["meta"]["champion"] = "TAM Leadership"
data["sheet1"]["meta"]["stakeholders"] = "Cross-functional CS, Sales & Onboarding Leadership"
data["sheet2"]["meta"]["champion"] = "Onboarding Leadership"
data["sheet2"]["meta"]["stakeholders"] = "Cross-functional CS, Sales & Onboarding Leadership"

with open("sanitized.json", "w") as f:
    json.dump(data, f, indent=2)

# Verify no banned tokens remain
banned = ["Matt","Gerhard","Zack","Jessica","Karina","Kris","Paolo","Artur",
          "Gainsight","Totango","Salesforce","SalesForce","SFDC"]
raw = json.dumps(data)
hits = [b for b in banned if re.search(r"\b"+re.escape(b)+r"\b", raw)]
print("Remaining banned tokens:", hits)
print("GS token count remaining:", len(re.findall(r"\bGS\b", raw)))

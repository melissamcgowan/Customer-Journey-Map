# -*- coding: utf-8 -*-
import json, html, re

with open("sanitized.json") as f:
    DATA = json.load(f)

def h(x):
    if x is None:
        return ""
    return html.escape(str(x))

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")

def is_light(hexcolor):
    hexcolor = hexcolor.lstrip("#")
    r, g, b = int(hexcolor[0:2],16), int(hexcolor[2:4],16), int(hexcolor[4:6],16)
    lum = (0.299*r + 0.587*g + 0.114*b)
    return lum > 170

def tag_list(items, cls="tag"):
    if not items:
        return ""
    return "".join(f'<span class="{cls}">{h(i)}</span>' for i in items)

def who_chips(who):
    if not who:
        return ""
    out = []
    for w in who:
        role = h(w["role"])
        note = w.get("note")
        if note:
            out.append(f'<span class="chip" title="{h(note)}">{role}<sup>*</sup></span>')
        else:
            out.append(f'<span class="chip">{role}</span>')
    return "".join(out)

def bullets(items):
    if not items:
        return ""
    return "<ul>" + "".join(f"<li>{h(i)}</li>" for i in items) + "</ul>"

def numbered(items):
    if not items:
        return ""
    return "<ol>" + "".join(f"<li>{h(i)}</li>" for i in items) + "</ol>"

def render_card(col, stage_color, view_prefix):
    all_roles = [w["role"] for w in col.get("who", [])]
    roles_attr = h("|".join(all_roles))
    parts = []
    parts.append(f'<article class="card" data-roles="{roles_attr}">')
    parts.append('<button class="card-head" type="button" onclick="toggleCard(this)">')
    parts.append(f'<h3>{h(col["event"])}</h3>')
    if col.get("trigger"):
        parts.append(f'<p class="trigger"><span class="label">Trigger</span>{h(col["trigger"])}</p>')
    parts.append('<span class="chev" aria-hidden="true">&#8250;</span>')
    parts.append('</button>')
    parts.append('<div class="card-body">')

    if col.get("objectives"):
        parts.append('<div class="field"><span class="field-label">Objectives</span>' + bullets(col["objectives"]) + '</div>')

    if col.get("who"):
        parts.append('<div class="field"><span class="field-label">Who\'s Involved</span><div class="chips">' + who_chips(col["who"]) + '</div></div>')

    if col.get("key_activities"):
        parts.append('<div class="field"><span class="field-label">Key Activities</span>' + numbered(col["key_activities"]) + '</div>')

    meta_bits = []
    if col.get("templates"):
        meta_bits.append('<div class="field small"><span class="field-label">Templates &amp; Collateral</span><div class="chips">' + tag_list(col["templates"], "tag tag-outline") + '</div></div>')
    if col.get("systems"):
        meta_bits.append('<div class="field small"><span class="field-label">Systems</span><div class="chips">' + tag_list(col["systems"], "tag tag-system") + '</div></div>')
    if col.get("metrics"):
        meta_bits.append('<div class="field small"><span class="field-label">Success Metrics</span><div class="chips">' + tag_list(col["metrics"], "tag tag-metric") + '</div></div>')
    if col.get("education"):
        meta_bits.append('<div class="field small"><span class="field-label">Education / Training</span><div class="chips">' + tag_list(col["education"], "tag tag-outline") + '</div></div>')
    if col.get("digital_assets"):
        meta_bits.append(f'<div class="field small"><span class="field-label">Digital Assets</span><p>{h(col["digital_assets"])}</p></div>')
    parts.append('<div class="meta-grid">' + "".join(meta_bits) + '</div>')

    if col.get("celebration"):
        parts.append(f'<div class="celebration">&#127881; Moment of Value / Celebration</div>')

    parts.append('</div>')  # card-body
    parts.append('</article>')
    return "".join(parts)

def render_view(sheet, view_id, view_prefix):
    stages = sheet["stages"]
    pills = []
    sections = []
    total_touch = 0
    for st in stages:
        slug = f"{view_prefix}-{slugify(st['title'])}"
        color = st["color"]
        n = len(st["columns"])
        total_touch += n
        text_color = "#1a1a1a" if is_light(color) else "#ffffff"
        pills.append(f'<a href="#{slug}" class="pill" style="--pill-color:{color}; --pill-text:{text_color}">{h(st["title"])}</a>')

        cards_html = "".join(render_card(c, color, view_prefix) for c in st["columns"])
        sections.append(f'''
        <section class="stage" id="{slug}" style="--accent:{color}; --accent-text:{text_color}">
          <div class="stage-header">
            <h2>{h(st["title"])}</h2>
            <span class="count">{n} touchpoint{"s" if n != 1 else ""}</span>
          </div>
          <div class="card-row">{cards_html}</div>
        </section>''')
    return "".join(pills), "".join(sections), total_touch

pills1, sections1, total1 = render_view(DATA["sheet1"], "view-lifecycle", "lc")
pills2, sections2, total2 = render_view(DATA["sheet2"], "view-onboarding", "ob")

meta1 = DATA["sheet1"]["meta"]
meta2 = DATA["sheet2"]["meta"]

# stats for hero
def collect_roles(sheet):
    roles = set()
    systems = set()
    for st in sheet["stages"]:
        for c in st["columns"]:
            for w in c.get("who", []):
                roles.add(w["role"])
            for s in c.get("systems", []):
                systems.add(s)
    return roles, systems

roles1, systems1 = collect_roles(DATA["sheet1"])
stage_count1 = len(DATA["sheet1"]["stages"])

# Stage color legend bar (mini visual for hero)
legend = "".join(
    f'<div class="legend-seg" style="--seg-color:{st["color"]}; flex-grow:{max(len(st["columns"]),1)}" title="{h(st["title"])}"></div>'
    for st in DATA["sheet1"]["stages"]
)

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Customer Success Lifecycle Journey Map</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap" rel="stylesheet">
<style>
:root {{
  --ink: #14181f;
  --ink-soft: #4a5160;
  --bg: #f6f5f2;
  --card-bg: #ffffff;
  --border: #e6e3db;
  --radius: 14px;
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{
  margin: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: var(--ink);
  background: var(--bg);
  line-height: 1.5;
}}
a {{ color: inherit; }}

/* ---------- HERO ---------- */
.hero {{
  background: linear-gradient(135deg, #14181f 0%, #262b36 55%, #1c2430 100%);
  color: #fff;
  padding: 64px 32px 40px;
  position: relative;
  overflow: hidden;
}}
.hero::after {{
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 85% 20%, rgba(255,255,255,0.08), transparent 55%);
  pointer-events: none;
}}
.hero-inner {{
  max-width: 1080px;
  margin: 0 auto;
  position: relative;
}}
.eyebrow {{
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 12.5px;
  font-weight: 600;
  color: #ffd479;
  margin: 0 0 14px;
}}
.hero h1 {{
  font-family: 'Source Serif 4', serif;
  font-size: clamp(32px, 5vw, 48px);
  font-weight: 600;
  margin: 0 0 16px;
  max-width: 780px;
}}
.hero p.objective {{
  font-size: 17px;
  color: #cdd2dd;
  max-width: 640px;
  margin: 0 0 28px;
}}
.hero-meta {{
  display: flex;
  flex-wrap: wrap;
  gap: 28px;
  margin-bottom: 32px;
}}
.hero-meta div {{
  font-size: 13px;
  color: #9aa2b1;
}}
.hero-meta strong {{
  display: block;
  color: #fff;
  font-size: 14.5px;
  font-weight: 600;
  margin-bottom: 2px;
}}
.stat-row {{
  display: flex;
  gap: 40px;
  flex-wrap: wrap;
  margin-bottom: 28px;
}}
.stat {{
  min-width: 90px;
}}
.stat .num {{
  font-size: 30px;
  font-weight: 800;
  font-family: 'Source Serif 4', serif;
  color: #ffd479;
}}
.stat .lbl {{
  font-size: 12.5px;
  color: #9aa2b1;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}}
.legend {{
  display: flex;
  height: 10px;
  border-radius: 6px;
  overflow: hidden;
  max-width: 700px;
  box-shadow: 0 0 0 1px rgba(255,255,255,0.12);
}}
.legend-seg {{ background: var(--seg-color); }}

/* ---------- NAV ---------- */
.view-tabs {{
  position: sticky;
  top: 0;
  z-index: 30;
  background: #fff;
  border-bottom: 1px solid var(--border);
  display: flex;
  gap: 4px;
  padding: 0 32px;
}}
.view-tabs button {{
  border: none;
  background: none;
  font-family: inherit;
  font-size: 14.5px;
  font-weight: 600;
  color: var(--ink-soft);
  padding: 16px 18px 14px;
  cursor: pointer;
  border-bottom: 3px solid transparent;
}}
.view-tabs button.active {{
  color: var(--ink);
  border-bottom-color: #1c2430;
}}

.toolbar {{
  position: sticky;
  top: 49px;
  z-index: 25;
  background: rgba(246,245,242,0.94);
  backdrop-filter: blur(6px);
  border-bottom: 1px solid var(--border);
  padding: 12px 32px;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}}
.pill-row {{
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  flex: 1;
}}
.pill {{
  text-decoration: none;
  font-size: 12.5px;
  font-weight: 600;
  padding: 6px 13px;
  border-radius: 999px;
  background: var(--pill-color);
  color: var(--pill-text);
  opacity: 0.88;
  white-space: nowrap;
}}
.pill:hover {{ opacity: 1; }}
.role-filter {{
  font-family: inherit;
  font-size: 13px;
  padding: 7px 12px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: #fff;
  color: var(--ink);
  min-width: 190px;
}}

/* ---------- MAIN ---------- */
main {{ max-width: 1200px; margin: 0 auto; padding: 32px; }}
.stage {{ margin-bottom: 46px; scroll-margin-top: 110px; }}
.stage-header {{
  display: flex;
  align-items: baseline;
  gap: 14px;
  padding: 10px 18px;
  border-radius: 10px;
  background: var(--accent);
  color: var(--accent-text);
  margin-bottom: 18px;
}}
.stage-header h2 {{
  font-family: 'Source Serif 4', serif;
  font-size: 21px;
  margin: 0;
  font-weight: 600;
}}
.stage-header .count {{
  font-size: 12.5px;
  opacity: 0.85;
  font-weight: 500;
}}

.card-row {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}}
.card {{
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-left: 4px solid var(--accent);
  border-radius: var(--radius);
  transition: box-shadow .15s ease, opacity .15s ease;
}}
.card.dimmed {{ opacity: 0.28; }}
.card-head {{
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  font-family: inherit;
  padding: 16px 18px;
  cursor: pointer;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 4px 10px;
  align-items: start;
}}
.card-head h3 {{
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  line-height: 1.35;
  grid-column: 1;
}}
.card-head .chev {{
  grid-column: 2;
  grid-row: 1 / span 2;
  font-size: 20px;
  color: #b9b3a6;
  align-self: center;
  transition: transform .18s ease;
}}
.card.open .card-head .chev {{ transform: rotate(90deg); color: var(--accent); }}
.trigger {{
  grid-column: 1;
  font-size: 12.5px;
  color: var(--ink-soft);
  margin: 2px 0 0;
}}
.trigger .label {{
  font-weight: 700;
  color: var(--accent);
  margin-right: 6px;
  text-transform: uppercase;
  font-size: 10.5px;
  letter-spacing: 0.05em;
}}
.card-body {{
  max-height: 0;
  overflow: hidden;
  padding: 0 18px;
}}
.card.open .card-body {{
  max-height: 4000px;
  padding: 0 18px 18px;
}}
.field {{ margin-top: 12px; }}
.field-label {{
  display: block;
  font-size: 10.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--accent);
  margin-bottom: 4px;
}}
.field ul, .field ol {{
  margin: 0;
  padding-left: 18px;
  font-size: 13.5px;
  color: var(--ink);
}}
.field ul li, .field ol li {{ margin-bottom: 3px; }}
.chips {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.chip {{
  font-size: 11.5px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 999px;
  background: #eef1f6;
  color: #33394a;
}}
.tag {{
  font-size: 11px;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 6px;
  background: #f1efe9;
  color: #5a5546;
}}
.tag-system {{ background: #eaf2ee; color: #2f5d43; }}
.tag-metric {{ background: #eef0fb; color: #38408f; }}
.tag-outline {{ background: #fff; border: 1px solid var(--border); color: var(--ink-soft); }}
.meta-grid {{
  display: grid;
  grid-template-columns: 1fr;
  gap: 2px;
}}
.field.small {{ margin-top: 10px; }}
.celebration {{
  margin-top: 14px;
  font-size: 12.5px;
  font-weight: 700;
  background: #fff6e0;
  color: #8a5a00;
  padding: 7px 12px;
  border-radius: 8px;
  display: inline-block;
}}

footer {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 26px 32px 60px;
  color: var(--ink-soft);
  font-size: 12.5px;
  border-top: 1px solid var(--border);
}}

#view-onboarding {{ display: none; }}

@media (max-width: 640px) {{
  .hero {{ padding: 44px 18px 28px; }}
  main {{ padding: 20px 16px; }}
  .toolbar {{ padding: 10px 16px; }}
  .view-tabs {{ padding: 0 16px; overflow-x:auto; }}
}}

@media print {{
  .view-tabs, .toolbar {{ display: none !important; }}
  #view-lifecycle, #view-onboarding {{ display: block !important; }}
  .card-body {{ max-height: none !important; padding: 0 18px 18px !important; }}
  .card-head .chev {{ display: none; }}
  .stage {{ page-break-inside: avoid; }}
  .hero {{ background: #14181f !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  .stage-header {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
}}
</style>
</head>
<body>

<header class="hero">
  <div class="hero-inner">
    <p class="eyebrow">Customer Success &middot; Portfolio Artifact</p>
    <h1>{h(meta1["doc_name"] or "Customer Lifecycle Journey Map")}</h1>
    <p class="objective">{h(meta1["objective"])}</p>
    <div class="stat-row">
      <div class="stat"><div class="num">{stage_count1}</div><div class="lbl">Journey Stages</div></div>
      <div class="stat"><div class="num">{total1 + total2}</div><div class="lbl">Mapped Touchpoints</div></div>
      <div class="stat"><div class="num">{len(roles1)}</div><div class="lbl">Roles Orchestrated</div></div>
      <div class="stat"><div class="num">{len(systems1)}</div><div class="lbl">Systems of Record</div></div>
    </div>
    <div class="legend">{legend}</div>
    <div class="hero-meta">
      <div><strong>{h(meta1["champion"])}</strong>Process Champion</div>
      <div><strong>{h(meta1["stakeholders"])}</strong>Core Stakeholders</div>
    </div>
  </div>
</header>

<nav class="view-tabs">
  <button class="active" onclick="showView('view-lifecycle', this)">Full Customer Lifecycle</button>
  <button onclick="showView('view-onboarding', this)">Onboarding Deep-Dive</button>
</nav>

<div class="toolbar">
  <div class="pill-row" id="pills-lifecycle">{pills1}</div>
  <div class="pill-row" id="pills-onboarding" style="display:none">{pills2}</div>
  <select class="role-filter" id="roleFilter" onchange="filterByRole()">
    <option value="">Filter by role&hellip;</option>
  </select>
</div>

<main id="view-lifecycle">{sections1}</main>
<main id="view-onboarding">{sections2}</main>

<footer>
  Customer Success Lifecycle Journey Map &mdash; portfolio sample. Names and internal tool references have been
  generalized for public sharing; process structure and content reflect real Customer Success program design work.
</footer>

<script>
function toggleCard(btn) {{
  btn.parentElement.classList.toggle('open');
}}
function showView(id, btn) {{
  document.getElementById('view-lifecycle').style.display = id === 'view-lifecycle' ? 'block' : 'none';
  document.getElementById('view-onboarding').style.display = id === 'view-onboarding' ? 'block' : 'none';
  document.getElementById('pills-lifecycle').style.display = id === 'view-lifecycle' ? 'flex' : 'none';
  document.getElementById('pills-onboarding').style.display = id === 'view-onboarding' ? 'flex' : 'none';
  document.querySelectorAll('.view-tabs button').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  populateRoleFilter();
  document.getElementById('roleFilter').value = '';
}}
function populateRoleFilter() {{
  const activeView = document.getElementById('view-lifecycle').style.display !== 'none' ? 'view-lifecycle' : 'view-onboarding';
  const cards = document.querySelectorAll('#' + activeView + ' .card');
  const roles = new Set();
  cards.forEach(c => {{
    c.classList.remove('dimmed');
    (c.dataset.roles || '').split('|').forEach(r => r && roles.add(r));
  }});
  const sel = document.getElementById('roleFilter');
  sel.innerHTML = '<option value="">Filter by role&hellip;</option>' +
    [...roles].sort().map(r => `<option value="${{r}}">${{r}}</option>`).join('');
}}
function filterByRole() {{
  const val = document.getElementById('roleFilter').value;
  const activeView = document.getElementById('view-lifecycle').style.display !== 'none' ? 'view-lifecycle' : 'view-onboarding';
  document.querySelectorAll('#' + activeView + ' .card').forEach(c => {{
    if (!val) {{ c.classList.remove('dimmed'); return; }}
    const roles = (c.dataset.roles || '').split('|');
    c.classList.toggle('dimmed', !roles.includes(val));
  }});
}}
populateRoleFilter();
</script>

</body>
</html>
"""

with open("index.html", "w") as f:
    f.write(HTML)

print("Wrote index.html, length:", len(HTML))

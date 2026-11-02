
PY
# ---------------------------------------------------------------
# UÚBA UNIFIED ADMIN HOME
# ---------------------------------------------------------------

RUN python - <<'PY'
from pathlib import Path

ADMIN_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Uúba Admin</title>
<style>
*{box-sizing:border-box}
body{
  margin:0;
  font-family:Arial,sans-serif;
  background:#f4f7fa;
  color:#152238;
}
header{
  background:#fff;
  border-bottom:1px solid #dce3ea;
}
.wrap{
  max-width:1100px;
  margin:auto;
  padding:0 22px;
}
.top{
  min-height:68px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:20px;
}
.brand{
  font-size:24px;
  font-weight:800;
}
nav a{
  color:#152238;
  text-decoration:none;
  font-weight:700;
  margin-left:22px;
}
nav a.active{color:#0f7f78}
main{
  max-width:1100px;
  margin:auto;
  padding:40px 22px 70px;
}
.eyebrow{
  color:#536a7d;
  margin-bottom:8px;
}
h1{
  font-size:42px;
  margin:0 0 12px;
}
.lead{
  font-size:18px;
  color:#586b7d;
  margin-bottom:28px;
}
.panel{
  background:#fff;
  border:1px solid #d7e0e8;
  border-radius:16px;
  padding:22px;
  margin-bottom:24px;
}
.loginGrid{
  display:grid;
  grid-template-columns:1fr auto;
  gap:12px;
}
input{
  width:100%;
  padding:14px;
  font-size:17px;
  border:1px solid #cbd6df;
  border-radius:10px;
}
button,.btn{
  border:0;
  border-radius:10px;
  padding:14px 18px;
  font-weight:800;
  cursor:pointer;
  text-decoration:none;
  display:inline-block;
}
.teal{
  background:#117f78;
  color:white;
}
.light{
  background:#edf3f5;
  color:#152238;
}
.muted{
  color:#607184;
  font-size:14px;
}
.dashboard{
  display:none;
}
body.authorised .dashboard{
  display:block;
}
body.authorised .loginPanel{
  display:none;
}
.stats{
  display:grid;
  grid-template-columns:repeat(4,1fr);
  gap:14px;
  margin-bottom:24px;
}
.stat{
  background:#fff;
  border:1px solid #d7e0e8;
  border-radius:14px;
  padding:18px;
}
.stat span{
  display:block;
  color:#637488;
  font-size:14px;
}
.stat strong{
  display:block;
  font-size:29px;
  margin-top:6px;
}
.cards{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:20px;
}
.card{
  background:#fff;
  border:1px solid #d7e0e8;
  border-radius:16px;
  padding:26px;
}
.card h2{
  margin-top:0;
}
.card p{
  color:#5a6d7f;
  min-height:75px;
}
.actions{
  display:flex;
  gap:12px;
  flex-wrap:wrap;
}
.logout{
  margin-top:26px;
}
@media(max-width:760px){
  .stats,.cards{grid-template-columns:1fr}
  .loginGrid{grid-template-columns:1fr}
  h1{font-size:34px}
}
</style>
</head>

<body>
<header>
<div class="wrap top">
  <div class="brand">Uúba</div>
  <nav>
    <a class="active" href="/admin">Admin Home</a>
    <a href="/community-moderator.html">Consumer Voices</a>
    <a href="/admin/casework">Caseworker</a>
  </nav>
</div>
</header>

<main>
<div class="eyebrow">Private admin area</div>
<h1>Uúba Admin</h1>
<p class="lead">
One private workspace for Consumer Voices moderation and Personal Case Reviews.
</p>

<section class="panel loginPanel">
  <div class="loginGrid">
    <input id="token" type="password"
      autocomplete="off"
      placeholder="Enter UUBA_ADMIN_TOKEN">
    <button class="teal" onclick="connectAdmin()">Open Uúba Admin</button>
  </div>
  <div id="loginMsg" class="muted" style="margin-top:10px">
    Enter your private Uúba admin token.
  </div>
</section>

<div class="dashboard">

<section class="stats">
  <div class="stat">
    <span>Pending Consumer Voices</span>
    <strong id="pending">—</strong>
  </div>

  <div class="stat">
    <span>Open reports</span>
    <strong id="reports">—</strong>
  </div>

  <div class="stat">
    <span>Active case reviews</span>
    <strong id="activeCases">—</strong>
  </div>

  <div class="stat">
    <span>Awaiting information</span>
    <strong id="awaiting">—</strong>
  </div>
</section>

<section class="cards">

<div class="card">
  <h2>Consumer Voices</h2>
  <p>
    Review submitted experiences, approve or reject posts,
    deal with reports and monitor recent community activity.
  </p>

  <div class="actions">
    <a class="btn teal" href="/community-moderator.html">
      Open Consumer Voices
    </a>
  </div>
</div>

<div class="card">
  <h2>Personal Case Reviews</h2>
  <p>
    Triage customer cases, assess eligibility, scope and price reviews,
    track work, complete quality checks and close cases.
  </p>

  <div class="actions">
    <a class="btn teal" href="/admin/casework">
      Open Caseworker
    </a>
  </div>
</div>

</section>

<div class="logout">
  <button class="light" onclick="logoutAdmin()">Log out of admin</button>
</div>

</div>

</main>

<script>
let adminToken = sessionStorage.getItem('helper_admin_token') || '';

function headers(){
  return {Authorization:`Bearer ${adminToken}`};
}

async function api(path){
  const r = await fetch(path,{headers:headers()});
  let d = {};
  try{ d = await r.json(); }catch(e){}
  if(!r.ok) throw new Error(d.detail || `Request failed (${r.status})`);
  return d;
}

async function connectAdmin(){
  adminToken = token.value.trim();

  if(!adminToken){
    loginMsg.textContent = 'Enter your admin token.';
    return;
  }

  try{
    const [community,casework] = await Promise.all([
      api('/api/admin/community/summary'),
      api('/api/admin/casework/summary')
    ]);

    sessionStorage.setItem('helper_admin_token',adminToken);

    pending.textContent = community.pending ?? 0;
    reports.textContent = community.open_reports ?? 0;
    activeCases.textContent = casework.active_reviews ?? 0;
    awaiting.textContent = casework.awaiting_information ?? 0;

    document.body.classList.add('authorised');
    token.value = '';
  }
  catch(e){
    sessionStorage.removeItem('helper_admin_token');
    adminToken = '';
    document.body.classList.remove('authorised');
    loginMsg.textContent = 'Admin access was not accepted.';
  }
}

function logoutAdmin(){
  sessionStorage.removeItem('helper_admin_token');
  adminToken = '';
  document.body.classList.remove('authorised');
  loginMsg.textContent = 'Admin session ended.';
}

if(adminToken){
  token.value = adminToken;
  connectAdmin();
}
</script>

</body>
</html>
'''

Path("admin.html").write_text(ADMIN_HTML, encoding="utf-8")


# ---------------------------------------------------------------
# Add /admin route
# ---------------------------------------------------------------

p = Path("app.py")
s = p.read_text(encoding="utf-8")

route = '''
@app.get("/admin", response_class=HTMLResponse)
def unified_admin_home():
    return FileResponse(ROOT / "admin.html")

'''

if '@app.get("/admin", response_class=HTMLResponse)' not in s:

    marker = '@app.get("/admin/casework"'

    if marker in s:
        s = s.replace(marker, route + marker, 1)
    else:
        # Safe fallback: place before an existing page route.
        marker = '@app.get("/specialists"'
        if marker in s:
            s = s.replace(marker, route + marker, 1)
        else:
            s += '\n' + route

p.write_text(s, encoding="utf-8")


# ---------------------------------------------------------------
# Add Admin Home link to existing private pages
# ---------------------------------------------------------------

for filename in ["caseworker-admin.html", "community-moderator.html"]:

    f = Path(filename)

    if not f.exists():
        continue

    text = f.read_text(encoding="utf-8")

    if 'href="/admin">Admin Home</a>' not in text:

        text = text.replace(
            '<nav class="nav">',
            '<nav class="nav"><a href="/admin">Admin Home</a>',
            1
        )

    f.write_text(text, encoding="utf-8")


# Validation
assert Path("admin.html").exists()
assert '@app.get("/admin", response_class=HTMLResponse)' in p.read_text(encoding="utf-8")

print("Unified Uúba Admin Home installed")
PY
RUN pip install --no-cache-dir -r requirements.txt
# ---------------------------------------------------------------
# UÚBA PERSONAL CASE REVIEW & CONSULTANCY  

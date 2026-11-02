def uuba_case_review_payment_link(reference:str,request:Request):
    _require_caseworker_admin(request); stripe=_stripe()
    # The launch-intake data lives in the same PostgreSQL DB but uses SQLAlchemy in the launch patch.
    try:
        import sqlalchemy as _sa
        _dbu=DATABASE_URL
        if _dbu.startswith('postgres://'): _dbu='postgresql://'+_dbu[len('postgres://'):]
        if not _dbu: raise Exception('database unavailable')
        _e=_sa.create_engine(_dbu,pool_pre_ping=True)
        with _e.begin() as c: row=c.execute(_sa.text("SELECT reference,email,customer_name,quote_amount,status FROM uuba_case_intake WHERE reference=:r"),{'r':reference}).mappings().first()
    except Exception: row=None
    if not row: raise HTTPException(404,'Case review request not found.')
    if row['quote_amount'] is None or float(row['quote_amount'])<=0: raise HTTPException(400,'Set the agreed quote before creating a payment link.')
    session=stripe.checkout.Session.create(
      mode='payment',customer_email=row['email'],
      line_items=[{'price_data':{'currency':'gbp','unit_amount':int(round(float(row['quote_amount'])*100)),'product_data':{'name':'Uúba Personal Case Review','description':f"Case review {reference}"}},'quantity':1}],
      success_url=BASE_URL+'/case-review.html?payment=success&reference='+reference,
      cancel_url=BASE_URL+'/case-review.html?payment=cancelled&reference='+reference,
      metadata={'uuba_type':'case_review','case_reference':reference}
    )
    try:
        with _e.begin() as c: c.execute(_sa.text("UPDATE uuba_case_intake SET status='payment_pending',payment_reference=:p,updated_at=NOW() WHERE reference=:r"),{'p':session.id,'r':reference})
    except Exception: pass
    return {'url':session.url,'reference':reference,'amount':float(row['quote_amount'])}
'''
    app += billing

# Gate live AI in Ask Uuba for Plus when enforcement enabled.
# Keep rules fallback available to Core.
app=app.replace("allow_live=bool(u.get('ai_enabled'))", "allow_live=bool(u.get('ai_enabled')) and (user_has_plus(u['id']) or not UUBA_BILLING_ENFORCE)")
app=app.replace("u.get('ai_enabled',False)", "u.get('ai_enabled',False) and (user_has_plus(u['id']) or not UUBA_BILLING_ENFORCE)")

# Core = one active case. Insert just before case creation INSERT.
needle="def create_case(data:CaseIn, request:Request):\n    u=current_user(request,True); check_rate(request,u['id'],30)"
if needle in app and 'Core includes one active case workspace' not in app:
    repl=needle+"\n    if UUBA_BILLING_ENFORCE and not user_has_plus(u['id']):\n        con=db(); n=con.execute(\"SELECT COUNT(*) FROM cases WHERE user_id=? AND status='Open'\",(u['id'],)).fetchone()[0]; con.close()\n        if n>=1: raise HTTPException(402,\"Core includes one active case workspace. Upgrade to Uúba Plus for multi-case support.\")"
    app=app.replace(needle,repl,1)

# Specialist review: consume one paid credit when enforcement is on.
needle2="def specialist_review(data:SpecialistReviewIn, request:Request):\n    u=current_user(request,True)"
if needle2 in app and 'AI Specialist Review requires a one-off purchase' not in app:
    repl2=needle2+"\n    if UUBA_BILLING_ENFORCE and not consume_ai_review_credit(u['id']):\n        raise HTTPException(402,\"AI Specialist Review requires a one-off purchase.\")"
    app=app.replace(needle2,repl2,1)

app_path.write_text(app,encoding='utf-8')

# Frontend paid flow
if 'id="uuba-billing-account"' not in idx:
    plus_old='<p class="muted">Provisional private-beta price.</p></article>'
    plus_new='''<div class="actions" style="margin-top:16px"><button class="btn" type="button" onclick="startPlusCheckout('monthly')">Choose monthly — £14.99</button><button class="btn alt" type="button" onclick="startPlusCheckout('annual')">Choose annual — £129</button></div><p class="muted">Annual saves £50.88 compared with 12 monthly payments. Renews automatically until cancelled. You can cancel online from your Uúba account.</p></article>'''
    idx=idx.replace(plus_old,plus_new,1)
    ai_old='<p class="muted">Not legal advice or a prediction of outcome.</p></article>'
    ai_new='''<div class="actions" style="margin-top:16px"><button class="btn" type="button" onclick="startAiReviewCheckout()">Buy review — £34.99</button></div><p class="muted">One-off purchase. Not legal advice or a prediction of outcome.</p></article>'''
    idx=idx.replace(ai_old,ai_new,1)
    billing_html='''<section class="section" id="billing-account"><div class="sectionhead"><div><span class="tag">Account & billing</span><h2>Your Uúba plan</h2><p>See your current plan, renewal status and manage or cancel Plus online.</p></div></div><article class="card" id="uuba-billing-account"><h3 id="uubaPlanName">Uúba Core</h3><p id="uubaPlanStatus" class="muted">Sign in to view your plan.</p><div class="actions" id="uubaBillingActions"><button class="btn" type="button" onclick="openAuth('login')">Sign in</button></div><div id="uubaPaymentNotice" class="notice" style="display:none;margin-top:14px"></div></article></section>'''
    idx=idx.replace('<section class="section" id="about">',billing_html+'<section class="section" id="about">',1)

# Add Billing nav item after Plans
if '>Billing<' not in idx:
    idx=idx.replace('<a href="#plans">Plans</a>','<a href="#plans">Plans</a><a href="#billing-account">Billing</a>',1)

# JS flow appended before body close, avoids touching large existing script.
if 'UUBA_BILLING_UI_V1' not in idx:
    js=r'''
<script id="UUBA_BILLING_UI_V1">
let UUBA_PENDING_PURCHASE=null;
function uubaNeedAccount(kind){UUBA_PENDING_PURCHASE=kind;if(typeof openAuth==='function')openAuth('register');}
async function uubaPost(url,body){const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':HELPER_CSRF||''},body:JSON.stringify(body||{})});const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.detail||'Request failed');return d}
window.startPlusCheckout=async function(interval){if(!HELPER_USER){uubaNeedAccount('plus:'+interval);return}try{const d=await uubaPost('/api/billing/checkout/plus',{interval});location.href=d.url}catch(e){alert(e.message)}}
window.startAiReviewCheckout=async function(){if(!HELPER_USER){uubaNeedAccount('ai-review');return}try{const d=await uubaPost('/api/billing/checkout/ai-review',{});location.href=d.url}catch(e){alert(e.message)}}
window.resumePendingPurchase=async function(){const p=UUBA_PENDING_PURCHASE;UUBA_PENDING_PURCHASE=null;if(!p)return;if(p.startsWith('plus:'))return startPlusCheckout(p.split(':')[1]);if(p==='ai-review')return startAiReviewCheckout()}
window.refreshBillingStatus=async function(){const name=document.getElementById('uubaPlanName'),status=document.getElementById('uubaPlanStatus'),actions=document.getElementById('uubaBillingActions');if(!name||!status||!actions)return;if(!HELPER_USER){name.textContent='Uúba Core';status.textContent='Sign in to view your plan.';actions.innerHTML='<button class="btn" type="button" onclick="openAuth(\'login\')">Sign in</button>';return}try{const r=await fetch('/api/billing/status');const d=await r.json();if(!r.ok)throw new Error(d.detail||'Unable to load billing');if(d.plan==='plus'){name.textContent='Uúba Plus';let bits=[d.billing_interval==='annual'?'Annual — £129/year':'Monthly — £14.99/month'];if(d.current_period_end)bits.push('Current period ends '+new Date(d.current_period_end).toLocaleDateString());if(d.cancel_at_period_end)bits.push('Cancellation scheduled');status.textContent=bits.join(' · ');actions.innerHTML='<button class="btn alt" type="button" onclick="openBillingPortal()">Manage billing</button>'+(d.cancel_at_period_end?'<button class="btn" type="button" onclick="resumePlus()">Keep Plus</button>':'<button class="btn" style="background:#991b1b" type="button" onclick="cancelPlus()">Cancel Plus</button>')}else{name.textContent='Uúba Core';status.textContent='Free plan · one active case workspace.';actions.innerHTML='<button class="btn" type="button" onclick="startPlusCheckout(\'monthly\')">Upgrade monthly — £14.99</button><button class="btn alt" type="button" onclick="startPlusCheckout(\'annual\')">Upgrade annual — £129</button>'}if(d.ai_review_credits>0)status.textContent+=' · '+d.ai_review_credits+' Specialist Review credit'+(d.ai_review_credits===1?'':'s')}catch(e){status.textContent=e.message}}
window.openBillingPortal=async function(){try{const d=await uubaPost('/api/billing/portal',{});location.href=d.url}catch(e){alert(e.message)}}
window.cancelPlus=async function(){if(!confirm('Cancel Uúba Plus at the end of the current paid period? You will keep Plus access until then.'))return;try{const d=await uubaPost('/api/billing/cancel-plus',{});alert(d.message);refreshBillingStatus()}catch(e){alert(e.message)}}
window.resumePlus=async function(){try{await uubaPost('/api/billing/resume-plus',{});refreshBillingStatus()}catch(e){alert(e.message)}}
(function(){const p=new URLSearchParams(location.search).get('payment');const box=document.getElementById('uubaPaymentNotice');if(p&&box){box.style.display='block';box.textContent=p.includes('success')?'Payment completed. Your account will update automatically once the payment confirmation arrives.':'Checkout cancelled — no new purchase was completed.'}setTimeout(()=>{if(typeof refreshBillingStatus==='function')refreshBillingStatus()},500)})();
</script>
'''
    idx=idx.replace('</body>',js+'\n</body>',1)

# Patch existing auth success/sign in/out to refresh billing and continue pending checkout.
idx=idx.replace("closeAuth();showSignedIn();await loadServerCases()", "closeAuth();showSignedIn();await loadServerCases();if(typeof refreshBillingStatus==='function')await refreshBillingStatus();if(typeof resumePendingPurchase==='function')await resumePendingPurchase()")
idx=idx.replace("document.getElementById('signOutBtn').style.display='inline-block'}", "document.getElementById('signOutBtn').style.display='inline-block';if(typeof refreshBillingStatus==='function')refreshBillingStatus()}",1)
idx=idx.replace("document.getElementById('signOutBtn').style.display='none'}", "document.getElementById('signOutBtn').style.display='none';if(typeof refreshBillingStatus==='function')refreshBillingStatus()}",1)

idx_path.write_text(idx,encoding='utf-8')

# Admin billing panel + quoted payment action documentation/visibility.
if 'id="uubaBillingAdmin"' not in admin:
    panel=r'''
<section id="uubaBillingAdmin" style="max-width:1180px;margin:22px auto;padding:0 18px">
<div style="background:#fff;border:1px solid #d8e8eb;border-radius:16px;padding:22px">
<h2>Billing & subscriptions</h2>
<p id="uubaBillingSummary">Enter the Admin token above, then refresh billing.</p>
<div style="display:flex;gap:10px;flex-wrap:wrap"><button onclick="loadUubaBillingAdmin()">Refresh billing</button></div>
<div id="uubaBillingList" style="margin-top:16px;overflow:auto"></div>
<p style="font-size:13px;color:#607786">Personal Case Review payment links are created only after a quote has been set. API: <code>POST /api/admin/case-intake/{reference}/payment-link</code>.</p>
</div></section>
<script id="uuba-admin-billing-js">
async function loadUubaBillingAdmin(){const token=sessionStorage.getItem('helper_admin_token')||sessionStorage.getItem('uuba_admin_token')||'';if(!token){document.getElementById('uubaBillingSummary').textContent='Enter the Admin token first.';return}const h={Authorization:'Bearer '+token};try{const [a,b]=await Promise.all([fetch('/api/admin/billing/summary',{headers:h}),fetch('/api/admin/billing/subscriptions',{headers:h})]);const s=await a.json(),d=await b.json();if(!a.ok)throw new Error(s.detail||'Billing summary failed');document.getElementById('uubaBillingSummary').textContent=`Plus: ${s.plus_total} · Monthly: ${s.plus_monthly} · Annual: ${s.plus_annual} · AI reviews sold: ${s.ai_reviews_sold}`;document.getElementById('uubaBillingList').innerHTML=(d.items||[]).length?'<table style="width:100%;border-collapse:collapse"><tr><th>Email</th><th>Plan</th><th>Interval</th><th>Status</th><th>Period end</th></tr>'+d.items.map(x=>`<tr><td>${x.email||''}</td><td>${x.plan}</td><td>${x.billing_interval||''}</td><td>${x.status}</td><td>${x.current_period_end||''}</td></tr>`).join('')+'</table>':'No billing records yet.'}catch(e){document.getElementById('uubaBillingSummary').textContent=e.message}}
</script>
'''
    admin=admin.replace('</body>',panel+'\n</body>',1)
    admin_path.write_text(admin,encoding='utf-8')

# Environment examples
for fname in ['.env.example','.env.production.example']:
    p=ROOT/fname
    if p.exists():
        t=p.read_text(encoding='utf-8')
        if 'STRIPE_SECRET_KEY=' not in t:
            t += '''\n# Payments / billing\nSTRIPE_SECRET_KEY=\nSTRIPE_WEBHOOK_SECRET=\nSTRIPE_PRICE_PLUS_MONTHLY=\nSTRIPE_PRICE_PLUS_YEARLY=\nSTRIPE_PRICE_AI_REVIEW=\nUUBA_BILLING_ENFORCE=0\n'''
            p.write_text(t,encoding='utf-8')

# Create payment setup doc for production operator, not end users.
(ROOT/'PAYMENTS_SETUP.md').write_text('''# Uúba payments production setup\n\nThe application code now supports:\n- Uúba Plus monthly £14.99 subscription\n- Uúba Plus annual £129 subscription\n- £34.99 AI Specialist Review one-off purchase\n- Stripe customer portal\n- direct online cancellation at period end and resume\n- webhook-backed plan state\n- admin billing summary\n- quoted Personal Case Review checkout sessions\n\nRequired production environment variables:\n- STRIPE_SECRET_KEY\n- STRIPE_WEBHOOK_SECRET\n- STRIPE_PRICE_PLUS_MONTHLY\n- STRIPE_PRICE_PLUS_YEARLY\n- STRIPE_PRICE_AI_REVIEW\n- UUBA_BILLING_ENFORCE=1 after live products/prices and webhook have been verified\n\nWebhook endpoint: /api/stripe/webhook\nEvents: checkout.session.completed, customer.subscription.created, customer.subscription.updated, customer.subscription.deleted.\n\nDo not commit payment secret values to GitHub.\n''',encoding='utf-8')

print('billing patch applied')

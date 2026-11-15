#!/usr/bin/env python3
"""Uúba chat-first entry: preserves the existing, authenticated case organiser."""
from pathlib import Path
root=Path("/app")
index=root/"index.html"
html=index.read_text(encoding="utf-8")
if 'id="uuba-chat-first"' in html:
    print("Chat-first entry already installed")
    raise SystemExit(0)
if 'id="prompt-form"' not in html or 'id="complaint"' not in html:
    raise RuntimeError("Existing Uúba case entry was not found; refusing unsafe homepage change")
widget = r"""
<section id="uuba-chat-first" aria-label="Uúba guided assistant">
  <div class="ucf-top"><span class="ucf-indicator" aria-hidden="true"></span><strong>Uúba Assistant</strong><span class="ucf-meta">Free to start</span></div>
  <div id="ucf-history" class="ucf-history" aria-live="polite">
    <p class="ucf-bubble ucf-bot">Hello! What do you need help with? Describe what happened in your own words. I'll help you take the next step.</p>
  </div>
  <form id="ucf-form">
    <label for="ucf-message" class="ucf-label">Your message</label>
    <div class="ucf-entry">
      <textarea id="ucf-message" required minlength="20" maxlength="20000" rows="3" placeholder="For example: I bought a car and it keeps breaking down. The dealer won't respond."></textarea>
      <button type="submit" id="ucf-send">Continue &#8594;</button>
    </div>
  </form>
  <div class="ucf-examples" aria-label="Example issues">
    <button type="button" data-ucf-example="I bought a car from a dealer and it keeps breaking down. The dealer has not replied.">Car problem</button>
    <button type="button" data-ucf-example="I have problems with my new-build home and the builder has not resolved them.">New-build home</button>
    <button type="button" data-ucf-example="My broadband provider is not resolving my service and billing complaint.">Broadband</button>
    <button type="button" data-ucf-example="I want help making a complaint about a faulty product and asking for a remedy.">Shopping</button>
  </div>
  <p class="ucf-note">Your message is used to begin the existing Uúba case process. AI case organisation is available after sign-in when enabled; otherwise a basic checklist is shown. Do not enter passwords, bank details or highly sensitive personal information.</p>
</section>
<style id="uuba-chat-first-style">
#uuba-chat-first{max-width:810px;margin:22px auto 30px;background:white;border:1px solid #d8e5e9;border-radius:20px;box-shadow:0 16px 48px rgba(12,42,64,.08);overflow:hidden;text-align:left}
#uuba-chat-first *{box-sizing:border-box}
.ucf-top{padding:18px 22px;display:flex;align-items:center;gap:10px;border-bottom:1px solid #e6edef;color:#17384b}
.ucf-indicator{background:#168277;width:10px;height:10px;border-radius:50%}
.ucf-meta{margin-left:auto;font-size:12px;color:#667a87}
.ucf-history{padding:22px;min-height:100px;display:flex;flex-direction:column;gap:12px;max-height:330px;overflow:auto}
.ucf-bubble{padding:13px 16px;border-radius:16px;max-width:90%;line-height:1.5;margin:0;font-size:15px}
.ucf-bot{background:#eff6f7;align-self:flex-start;color:#244453}
.ucf-user{background:#e2f0fc;align-self:flex-end;color:#173b62}
#ucf-form{padding:0 22px 14px}
.ucf-label{display:block;font-size:13px;font-weight:700;margin-bottom:8px;color:#355466}
.ucf-entry{display:flex;gap:10px;align-items:end}
#ucf-message{width:100%;min-height:82px;resize:vertical;font:inherit;font-size:15px;padding:13px;border:1px solid #c5d7df;border-radius:12px}
#ucf-send{flex:none;border:none;background:#0e716f;color:white;border-radius:11px;padding:15px 18px;font-weight:750;cursor:pointer}
.ucf-examples{padding:0 22px 14px;display:flex;gap:7px;flex-wrap:wrap}
.ucf-examples button{border:1px solid #c6d9de;border-radius:999px;padding:7px 11px;background:#f8fbfc;color:#285369;cursor:pointer;font-size:12px}
.ucf-note{border-top:1px solid #e6edef;padding:14px 22px;margin:0;color:#607685;font-size:12px;line-height:1.5}
#prompt-form{display:none!important}
@media(max-width:600px){.ucf-entry{flex-direction:column;align-items:stretch}#ucf-send{width:100%}.ucf-bubble{max-width:100%}}
</style>
<script id="uuba-chat-first-js">
(function(){
  function init(){
    var form=document.getElementById('ucf-form');
    var field=document.getElementById('ucf-message');
    var original=document.getElementById('complaint');
    var existing=document.getElementById('prompt-form');
    var history=document.getElementById('ucf-history');
    if(!form||!field||!original||!existing)return;
    if(original.value)field.value=original.value;
    document.querySelectorAll('[data-ucf-example]').forEach(function(button){
      button.addEventListener('click',function(){field.value=button.getAttribute('data-ucf-example');field.focus();});
    });
    form.addEventListener('submit',function(e){
      e.preventDefault();
      var text=field.value.trim();
      if(text.length<20){field.setCustomValidity('Please add at least 20 characters.');field.reportValidity();return;}
      field.setCustomValidity('');
      original.value=text;
      original.dispatchEvent(new Event('input',{bubbles:true}));
      var message=document.createElement('p');message.className='ucf-bubble ucf-user';message.textContent=text;history.appendChild(message);
      var reply=document.createElement('p');reply.className='ucf-bubble ucf-bot';
      reply.textContent='Thank you. Next, add a few details so Uúba can organise your case and show the appropriate next steps.';
      history.appendChild(reply);history.scrollTop=history.scrollHeight;
      existing.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
    });
    field.addEventListener('input',function(){field.setCustomValidity('');});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);
  else init();
})();
</script>
"""
html=html.replace('<form class="entry" id="prompt-form">',widget+'\n<form class="entry" id="prompt-form">',1)
index.write_text(html,encoding="utf-8")
assert 'id="uuba-chat-first"' in index.read_text(encoding="utf-8")
print("Uúba chat-first entry installed; existing case APIs preserved")

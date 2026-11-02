          ? '<p><strong>Desired outcome</strong><br>'+esc(x.desired_outcome).replace(/\n/g,'<br>')+'</p>'
          : ''}

        ${x.evidence_notes
          ? '<p><strong>Evidence held</strong><br>'+esc(x.evidence_notes).replace(/\n/g,'<br>')+'</p>'
          : ''}

        <div class="uuba-detail-grid">
          <label>Status
            <select id="uubaEditStatus">
              ${['new','triage','awaiting_information','scoped','quoted','accepted','in_review','qa','completed','declined']
                .map(s=>`<option value="${s}" ${x.status===s?'selected':''}>${pretty(s)}</option>`).join('')}
            </select>
          </label>

          <label>Scope level
            <select id="uubaEditScope">
              <option value="">Not set</option>
              ${['standard','complex','bespoke']
                .map(s=>`<option value="${s}" ${x.scope_level===s?'selected':''}>${pretty(s)}</option>`).join('')}
            </select>
          </label>

          <label>Quote (£)
            <input id="uubaEditQuote" type="number" min="0" step="0.01" value="${x.quote_amount??''}">
          </label>

          <label>Assigned to
            <input id="uubaEditAssigned" value="${esc(x.assigned_to||'')}">
          </label>

          <label class="uuba-full">Quote / scope notes
            <textarea id="uubaEditQuoteNotes" rows="4">${esc(x.quote_notes||'')}</textarea>
          </label>

          <label class="uuba-full">Internal caseworker notes
            <textarea id="uubaEditInternal" rows="6">${esc(x.internal_notes||'')}</textarea>
          </label>

          <div class="uuba-full">
            <button type="button" onclick="uubaSaveIntake('${esc(x.reference)}')">Save case assessment</button>
            <span id="uubaIntakeSaveMsg"></span>
          </div>
        </div>
      `;

      box.scrollIntoView({behavior:'smooth',block:'start'});

    }catch(e){
      alert(e.message);
    }
  }

  window.uubaSaveIntake=async function(ref){
    const payload={
      status:document.getElementById('uubaEditStatus').value,
      scope_level:document.getElementById('uubaEditScope').value||null,
      quote_amount:document.getElementById('uubaEditQuote').value||null,
      assigned_to:document.getElementById('uubaEditAssigned').value,
      quote_notes:document.getElementById('uubaEditQuoteNotes').value,
      internal_notes:document.getElementById('uubaEditInternal').value
    };

    const m=document.getElementById('uubaIntakeSaveMsg');
    m.textContent='Saving…';

    try{
      await req('/api/admin/case-intake/'+encodeURIComponent(ref),{
        method:'PATCH',
        body:JSON.stringify(payload)
      });

      m.textContent='Saved';
      await uubaLoadIntake();

    }catch(e){
      m.textContent=e.message;
    }
  }

  document.addEventListener('DOMContentLoaded',function(){
    const f=document.getElementById('uubaIntakeFilter');
    if(f){
      f.addEventListener('change',uubaLoadIntake);
      if(token()) uubaLoadIntake();
    }
  });
})();
</script>
"""

p = Path("caseworker-admin.html")
if p.exists():
    s = p.read_text(encoding="utf-8")

    if 'id="uuba-intake-queue"' not in s:
        if "</main>" in s:
            s = s.replace("</main>", ADMIN_SECTION + "\n</main>", 1)
        else:
            s = s.replace("</body>", ADMIN_SECTION + "\n</body>", 1)

    if 'id="uuba-case-intake-admin-js"' not in s:
        s = s.replace("</body>", ADMIN_JS + "\n</body>", 1)

    p.write_text(s, encoding="utf-8")

assert APP_MARKER in Path("app.py").read_text(encoding="utf-8")
assert 'id="uuba-review-request"' in Path("case-review.html").read_text(encoding="utf-8")
assert 'id="uuba-intake-queue"' in Path("caseworker-admin.html").read_text(encoding="utf-8")

print("Uúba case review intake pipeline installed")
PY

RUN mkdir -p /app/data/uploads /app/data/backups && \
    useradd --create-home --uid 10001 uuba && \
    chown -R uuba:uuba /app

USER uuba

EXPOSE 10000

CMD ["sh","-c","python -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000} --proxy-headers --forwarded-allow-ips='*'"]

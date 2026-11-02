FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY ["Uuba-production-Render-PostgreSQL-uuba.co.uk-INLINE-LOGO-FIXED (1).zip", "/tmp/uuba.zip"]

RUN python -m zipfile -e /tmp/uuba.zip /app && rm /tmp/uuba.zip

RUN python - <<'PY'
from pathlib import Path
import base64, zlib, re

def unpack(s):
    return zlib.decompress(base64.b64decode(s)).decode('utf-8')

CV_MAIN = unpack("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")

SP_MAIN = unpack("eNqdVsuO5DQU3fMVVpAQSNVVmpndUB2padFSCyQQrQGxQi7nJrHKsY3tdE1YseILRuJf2PIn8yWca1fqxTQ0SF1dKce+vvfcc469HqS2QhkZ43W1C9JX9TqSStodRnsKjke9PAwl2VX1vW3IE/7ZJKInpaXRMYmejF+veHa97l/U3wbyMpBodYhpKW575yIJfbJWNo9akXDWTGLXkxWTG4NQEtMsUROFTsv1CqHWvn7z5x8bmbeIwoVOWo1Zx/nSNsLvN5QipjCqNAZqRI837pHCUtwnoaOwDvsKI3ec15DXNY7KeCQDABYC6bmAoC6IbpRB2kQ5qjNa6YTRFh/sjeQ857aWMzybZCvRB2qvKy707bJPg/n4iNEVF1AdoBmmkj0aketbr2SdY672nag/uuxJowMGXJjQmP5lfYdtzjAtTcCbtZ+XDGOipqrfYCOKSW6QSE/nqyIFbkUUyQEXhDytlv82idnSjiGBFEI5G8cBD3H03oVUgGj047xlF3RToQ2TofLjKtHgjUx0pZwZBxtfAwKS6dOXixdt+AzFyJC0MjRHUDI0F9xD7mmMVf1N22rG8yTFAyoH/r2qv0aPH5zSlCbx/td34q7U9TAvAkqvuHsPJIPqc08PAWMmxsySyA360naGB/nzgzTAajMJNFEK1+aZeYVTkrv1j8zoU/Lx9Wp13G2J9bGkugS5l+N2VYkkQ0fpuvppg323lQhkrivrHHoG5K1DLAqBQlXfXXbs/W+/H6m0B/a/IHwX6Fyp+z6foHurk/6FbBQ3WcQzmKfWoC0wHTIeGZx9ELAHetS2O9LIB7cxNERIDyxx04DlC9G7MWLaQgzO0pRDuEw/wvqpkRP0HEeKHwRbSJMuAd/tdku1z7t4z/9B+3sddRIX9T8B+QqaOBMGbIYY9BSc7eofs3/1jgMEYkOOp7CjsP3EYg+Yo0g/ZrcSJSGoQLlhABCMchvcIAARlH5Q9JnDHe0MLJFKkU8IFD0aoTfaaEiFdSDtdK5/RgsR2fQ4Xxg5GzqpraC3Hs0kq2ghWtrvR7aTHXEXRSLWT9GnmZZ7RJ7tb18Q8slGD2CKrXN2IEQxuUvPeYrlYOdsusAHqjYHyn5F5POg6oG1M66bFmILwikXCjZNKY8edX7KJY4W75x5ZCPNLIR1gkBMz+ggRlC6pdwVbhEkNiIMDkJemzdj3/951GqbUXmGUFl0R8gT+jFXcBO3fH7mzTn2sXWButHIgPO1IWmi2OnUl1MzTZ7YuRodPc6HBQI4vDYmn5imwATxon+53l0vUx7TFsxn81WuRNi5sMWoMmMza/EZpdx07DHKxRTLDeG0GOZg6QhUyU6xkVHDHYzeEmrJ86+AZVciHBPspfcsSt0ezqqcXoYC94MIShZD4qsA7hjULD8o2ROCPqneW8dHmrao4BM5+M9Zkuhy/JtsC6KRlTovkBs3wiHx5HZ2Fiu+wVAcklwjS5l1uG9QlkC+M0grGZOlgN8VfzPUSbM6Rs+3jqr+jmThWsnCMysmNqlZhYcbQutQGKytTPyXWxKYzULYcwtXC5H3vwB4KW7urxAclx7MyGwv97Mj/GWPvBaHQMbCg115rdnJCYBlviu80wqzWqnS3tBQmtH2wDe2zvovHPDqGA==")

IDX_CV = unpack("eNp9VMFuGjEQ/ZXR5tBLAKmXqtFmpYCapodGVWh7d+xhdxSvbXlsCL/Wa3+s412gUEIvSPbMG7957y01o07kHWirmG+rw9E7zj3Gn5408oPv8bsPFZC5rfalyXqoTTopVk1taL0fcgqeK2feRP4P9DmSGetNzUEd+CXVVsBpa7EgrI83V+ojavxQNYvdABgn1LOCa+ruffOEygK+BoyETkpT+BaV7Knl2iKzAKf1TBrrUHoN9N5gVAnNQYdjOMhCwIiw6VSCgD5YhCRFcz1edWiDYEvbeFYhoJMbh69pCsvkpVnGRBR0lOeFh9LaZ5f4Gl4wJBkfVGEAq+h7+PH717N6x7AWCit5B9pMRgkXoR1OVByUvRs8LPqqk/t5chV0EVdnVky71NtqXP5MR/XGHFA27Wdd/ZsI7mS1CTlLTpKxLCfY+nws4jB1Ntg7/iomgyevfCVHsgKn6F3b3Is6YoqIcOyE8xsgp202eCOGj61/U9PsQvCIm8lzJmvA4EoSPlooqXp8mC9E65Qs9ujSjssZfvmylST0wSpyCZAlOEM6OGthwats7RaSh8WX5d3y0pB7lW3aQmYBrrEjLakpNA56P1HbCTVxD9Tg4KVJn4SJ3xbCYIh7YpYAmRzJtbJMJJ8ZyFon1C6NWHTKWnRtgSj5CFplJ0VYx6IqCaEohLzkDdhb0iSRBd0VW/auDYadejjb/Xs0fwDfhZH5")

IDX_SPEC = unpack("eNqdVs2O2zYQvucpCPWSAF67TXvJwjaQLNIm6N8iRhv0VNDSyCJMkQJJ2auecuoTFOgb9CF67ZvkSfoNKVuSdzeHLGBjTQ5nht/3zQyXnvKgrBG5lt6vsv5nJlSBHw3lSmrlw1VFusnWT5aFOpxNz7uvpClEbutG5mFzXmVz38iz6yB3mfCh07TKcqutu/7ixQv6piiz9VtTUEP4MkEMbgUHXS7YB1xVz9e3jhrpSHS2dSKXnkSpnA9zcVNZi19q5EbTTuroQVijO3GsyPBBYYgKocJ8uYDHJ8tm/ct//24l3Blh3U4a5ccB+GZNH1Yie9fmoXXwUGHHHsjNxLYN8CeUF8YGGGl55LzqeLawlNbzlKJ1Agla56M7q1WuAtZKfBB0Lt6WMckCGBQ05JtuI4uDymkWlx3VUhlROiIR7Ml9TNweTTT15HDL5jHWvnOqGEP2BljxGvMmXVC5ptOhXDosT9jshfK9yvfksvW3cDS+UU/bsvp6/QPw2NhcUejExw9/id50M5jCCDxsSLq8EqECSmWpOEsxPlsoh5jWdRGtcyQfcWbAPW4jXpud5gX+vJca6G+7Hj7lfZsY1TaXnH2EB6GX8nStbYD2K0flKqtCaPz1YjFEmoNan7KZQyvzdr/IRJBuR2GV/b5F3H0GYvQqM9YCVXKgHr7IuQEjM5HpIIGPf/69XMh1zGjR4/9ZTLAiJiHaprEujBi5UUH9QcaLl1FQJwIulqF7e4AK/cSbMkC/juhFKHvvgluINb6tuSSobrTtatjPRGVbr8xuJmprqItnLDhGHaB6ukJ2HGerqfYPsiGkDpeMHI/Hed4nm2ric+j4VXmU7eWlH6FhgRKaFtLWtqaQUGPf+F71v5md4KzZTboa6pPTBAlp79x3zg0C4iZ14LaQUoRgSzBZOltzTaC4Uc+cop82ll0rnTSBYm8Jck847xtQobZKq5CqRZpuJDVeSP0htpLUO7iLUr4HoSrIdHTGGaRwgbi+Ugmim24JXllmqSOCXw4BghOHPVr3QRu6zzs6KDreSkMaiI1NkpwrksV5XNQgVZmrrQ3B1tdfPW/u0plPFsLLt2k8XDXYBSgcb1QEp2FSd/0oYVRG02doSxp+eUse0InZdi5+Y9gki9NbAf+BYt/SMhDmVmOhLC6QHvnGKkiAoW6iolotHY8k0DYJyY2c7mStJjhO73g2/tEWdDmmX6q4uo5MMinAwAcZWv/xwz+nuyennyAlDYGxRalI85KWW9KM1PjQDRBJIA3S35yxGhS/iKdhkgCdZj5xYpuI3kHqFuTzdeJwG1OwXCQjuE3+HrjXJOtzau8rCaArdZJErKT7WY78HLh0Nx1Irn+yAfD+3L8T/MVDodRy59OY8VFPVVuDuhQHsz2MqjaVum9zFLQXPudywok0qdBEVfDCNsqkKRWv9vAFRdlq/Rg3r++CkwMtPyR9QvmQ3wJawy637YD/xNOEqNTP7qPBBigWecFaci9qeafJ7EK1yp5/ib9MNFrmVFldENK5vayPvkHhJVMo37QBnMYSweC4awjDpMTEYflyr4qz4pQj11AsG2Vy3Rb8kjPR8+k5NsdlF6dsH4IMYAkZ+4SHKd5uYXj8xuFv4RkdZJW51mwuKuPpMwyYroEo08Fs/a41YrAS7/ouk7Yf8J/G2TlGbptuOH4r8/39EDew6R0Lthi8PyKLcT37luNNWUu++r1PK/0knDf2yG/co3V7f32WhziqUAnNUkajISMxxouZSIMNRPJLwbPK8VY16Hv3+7HYOR6bA49DhceKAqMKKi96n7tWFdJgjor3iGzx8O6Dzzi7HJQHnlcCqjSeuzuU4lo8Aq+28Hh6yafHC2b2Pg4wDJpphfXf/ThZ/w/e6L9H")

IDX_PLANS = unpack("eNqVVdtu4zYQ/ZWBXxvb3WubVBHgzTZAgG0bNOgH0ORIIkKTLEnZ0f5O/2If2x/roShfEiNA++KE1Mxw5pwzM1VkmbSzJI2I8Xo2HWek1fXMG2HjrK6U3r743rFQ5UNdRS8O7km0s/pBb7xh8kFLbdtqmQ3qqntbPyQREjWBeUH3YiBnzUCNCySU0jmsMCRFZErOmbiolvCpfH3jAlPbayWsZIpJDJH6yE1vaKdT5/pEXgwbtimH1Yqcz8FiDkuK2XMoYWPvvUMGwipkx14EMda+f87X1XIsqfyelN0GnetF+lqitOlWipBvzwDICR/Kflf/8c+3taByieNp3IwRz+pbQDI96utbABJTELrtEsDZ4RGSKKffTHVMqfamrozGY+XTPGSHSI/W7QyrlmkN22oJk2z2m2US4G7LBYudC4/IUB4tRpilA3dC23RBsoNdGMHiKIUpWBlOiUM8eH0SUUv6naNHHkwrcDjA7fD9561WnHnLcWQXnHXGtQNCRhCmhZlCLXM5ywng/4z0Sm2zKNQZ2vemj6+h/fdfb94vLi+XG2dTRyVoTIPh61mDq3nUX/lq8eEjb34azzvOyF798OH7WQ1u4P72cjmwCPtXT5k70dtcgDsUHqOGaJHmM94+nxmu7mjXsSW2Ym1yTROEv2RiRAE2jjgqJ/usd2rZchHxwXoPCfEryI9qP5h/RicbbYtVgoZaJAVkdHJh7N59Er1Jen7WRvyU/z3l0O/R3vSJQdp9cFsdS3ODgK1IPF9zEuN8mCD537xDzXPXNCe0A7wHzxKCAtjQ41bzjr7DPJCPr+vgXdbBgb77cSQAidIF/FQ6Zc1NJiAyPwIQpO0aiLcUJNRWv+D1pkC02YgwvID+yJGU7IHOBSkdfcZptOwt5u2OA47eoQfjeRdpq5DXOMAckoBOqBX+aHgLZUT4/9lzLENwnK92zPS0L1flPA/gf6AOEd0WzPsRr1fJ/NUlTID2UDnl4HmWKl3WiGsI8xj4nTF7NlPXrrcKIM32zQfEWm3nyfmrNz/6p8x7AnRtfYeiPeMHin8Gf8fG453JDBSW5lcOfWKRquxDgBO2jPO5TzK3Pm+I6AyWEyROgRsOAbEspzwTF3TX0OB6nAHjaa0X47XMSuyciznWMYw+pojXEijv2w5/mb6IHT04qTkNGa0so3EFHtqoCW5DN9h/Xxl0rYqi6EUlgSXn2S2OCTeIMfpiBWbJcciez/fYtK7rfwHGP9V0")

CLEAN_CSS = unpack("eNqVVMtOwzAQvPcrAqdWaiAJUKIUEAIJegEhQNzdeCkr+SXHKami/jtO24TYFCQulq2dXc/Ojn1RmBWDAOnlYVnOSZgzIAJ0yMhKliZMomRyeDU4KiA3KEWtCKUoFqGRKjtLVHWAXEltiDDTNjSXxkjuRddthQ8gtOZEL1C0yDh1kQuNdHxUKMiRMCzM/easNOaw3VLUtpjUq+ZYL4jK4lO3RE50m3Jrty3tH1c1uED1kIFqyTUdWvTU4xqpapdWsn5eyfqJO5jkiuTmpeuk45F4PFBQUGAXYWbA1LYvu4QGuGLEQJhLVnJRZNriiBkmY46Ck2oYjeN3PRr15tCnkfZo3MhSUKJXDk9fNxfaqZFNVBVEQdQhHqWxnX/rGtu4W2zHY3NFELmXiKLkoN+kLVHMJIdXqWrPPsnEZ9ZPugOgjhd9QV1455PEM+WyCT+gwO9OJr8gAorLvnTnnr27IT/DEuHzyb4i1xIuw8E1B4pkaGcYfiI1H1maWNOM6n94wU5+zwtzdDlJ/3qjJ+ne8e8zrCvcenBxvPk4rr4AaSecWQ==")

p = Path('index.html')
s = p.read_text(encoding='utf-8')

s = s.replace(
    "})();</script></body></html>`);w.document.close();w.print()",
    "})();<\\/script></body></html>`);w.document.close();w.print()"
)

s = s.replace(
    '\n<script id="helper-workspace-tabs">\n',
    '\n'
)

s = s.replace(
    "Uúba"+chr(39)+"s verified guidance",
    "Uúba"+chr(92)+chr(39)+"s verified guidance"
)

if 'uuba-cleaner-layout-2026' not in s:
    s = s.replace('</head>', CLEAN_CSS + '</head>', 1)

s, n1 = re.subn(
    r'<section class="section consumerVoicesHomeTop".*?(?=<section class="section" id="consumer-voices-share-inline">)',
    IDX_CV,
    s,
    count=1,
    flags=re.S
)

s, n2 = re.subn(
    r'<section class="section" id="specialist-help">.*?(?=<section class="section" id="plans">)',
    IDX_SPEC,
    s,
    count=1,
    flags=re.S
)

s, n3 = re.subn(
    r'<section class="section" id="plans">.*?(?=<section class="section" id="about">)',
    IDX_PLANS,
    s,
    count=1,
    flags=re.S
)

assert (n1, n2, n3) == (1, 1, 1), \
    'Public section patch failed: ' + repr((n1, n2, n3))

p.write_text(s, encoding='utf-8')

p = Path('consumer-voices.html')
s = p.read_text(encoding='utf-8')

s, n = re.subn(
    r'<main>.*?</main>',
    CV_MAIN,
    s,
    count=1,
    flags=re.S
)

assert n == 1, 'Consumer Voices page patch failed'

p.write_text(s, encoding='utf-8')

p = Path('specialists.html')
s = p.read_text(encoding='utf-8')

s, n = re.subn(
    r'<main class="wrap">.*?</main>',
    SP_MAIN,
    s,
    count=1,
    flags=re.S
)

assert n == 1, 'Specialist Help page patch failed'

p.write_text(s, encoding='utf-8')

# Pricing and terminology updates
files = list(Path('.').rglob('*.html')) + list(Path('.').rglob('*.md'))

repls = {
    '£6.99': '£14.99',
    '£59/year': '£129/year',
    '£24.99': '£34.99'
}

for q in files:
    t = q.read_text(encoding='utf-8')

    for old, new in repls.items():
        t = t.replace(old, new)

    t = t.replace(
        'Partner Transparency',
        'External Help & Independence'
    )

    t = t.replace(
        'Specialist partners and external services',
        'External professional help and services'
    )

    q.write_text(t, encoding='utf-8')

remaining = [
    (str(q), old)
    for q in files
    for old in repls
    if old in q.read_text(encoding='utf-8')
]

assert not remaining, \
    'Old pricing remains: ' + repr(remaining)

# ------------------------------------------------------------------
# FIX STANDALONE PAGE NAVIGATION
#
# The FastAPI application serves the main site at "/".
# It does not use "/index.html" as the homepage.
#
# This fixes Consumer Voices -> Home and the equivalent links from
# the other standalone pages.
# ------------------------------------------------------------------

for page_name in [
    'consumer-voices.html',
    'consumer-voices-share.html',
    'specialists.html',
    'community-moderator.html'
]:
    page = Path(page_name)

    if page.exists():
        t = page.read_text(encoding='utf-8')

        # index.html#section -> /#section
        t = t.replace(
            'href="index.html#',
            'href="/#'
        )

        # plain index.html -> /
        t = t.replace(
            'href="index.html"',
            'href="/"'
        )

        # also catch ./index.html versions
        t = t.replace(
            'href="./index.html#',
            'href="/#'
        )

        t = t.replace(
            'href="./index.html"',
            'href="/"'
        )

        page.write_text(t, encoding='utf-8')

# Validation
idx = Path('index.html').read_text(encoding='utf-8')
cv = Path('consumer-voices.html').read_text(encoding='utf-8')
sp = Path('specialists.html').read_text(encoding='utf-8')

assert "Founder's experiences" in cv
assert '£130,000' in cv
assert '£150 compensation' in cv

assert 'Law Society' in sp
assert 'Citizens Advice' in sp

assert 'Partner being appointed' not in idx
assert 'Partner being appointed' not in sp

# Navigation validation
assert 'href="index.html"' not in cv
assert 'href="index.html#' not in cv
assert 'href="./index.html"' not in cv
assert 'href="./index.html#' not in cv

print('Uúba public-content and navigation patch checks passed')
PY
# Serve Personal Case Review page
RUN python - <<'PY'
from pathlib import Path

p = Path("app.py")
s = p.read_text(encoding="utf-8")

marker = '@app.get("/specialists", response_class=HTMLResponse)'

routes = '''
@app.get("/case-review", response_class=HTMLResponse)
def case_review_page():
    return FileResponse(ROOT / "case-review.html")

@app.get("/case-review.html", response_class=HTMLResponse)
def case_review_page_html():
    return FileResponse(ROOT / "case-review.html")

'''

if '@app.get("/case-review"' not in s:
    s = s.replace(marker, routes + marker, 1)

p.write_text(s, encoding="utf-8")

assert '@app.get("/case-review"' in s
assert '@app.get("/case-review.html"' in s

print("Personal Case Review routes added")
PY
# ---------------------------------------------------------------
# UÚBA PERSONAL REVIEW - LIMITED AVAILABILITY POSITIONING
# ---------------------------------------------------------------

RUN python - <<'PY'
from pathlib import Path

# Main Personal Case Review page
p = Path("case-review.html")
if p.exists():
    s = p.read_text(encoding="utf-8")

    s = s.replace(
        "PERSONAL CASE REVIEW & CONSULTANCY",
        "PERSONAL CASE REVIEW — LIMITED AVAILABILITY"
    )

    s = s.replace(
        "Uúba can provide a structured personal review of eligible consumer disputes.",
        "For cases that need more than automated guidance, Uúba can provide a structured human review on a limited-availability basis."
    )

    s = s.replace(
        "We organise the history, identify the main issues, review the evidence and\nresponses, and help you understand practical next steps.",
        "We organise the history, identify the main issues, review the evidence and responses, and help you understand practical next steps. We assess the scope first and confirm the price before substantive work begins."
    )

    s = s.replace(
        '<div class="price">From £350</div>',
        '<div class="price">From £350</div><p><strong>Quoted after initial scope assessment.</strong></p>'
    )

    p.write_text(s, encoding="utf-8")


# Homepage wording
p = Path("index.html")
s = p.read_text(encoding="utf-8")

s = s.replace(
    "<h2>Personal Case Review & Consultancy</h2>",
    "<h2>Personal Case Review — limited availability</h2>"
)

s = s.replace(
    "Some disputes need more than automated guidance. For eligible car dealer,\nnew-build, consumer, phone and broadband, trades, energy and travel disputes,\nUúba can provide a structured individual review of your case.",
    "Some disputes need more than automated guidance. For eligible car dealer, new-build, consumer, phone and broadband, trades, energy and travel disputes, Uúba can provide a structured human review on a limited-availability basis."
)

s = s.replace(
    "Complex Review from £350",
    "Complex Review from £350 — quoted after initial scope assessment"
)

if "We assess the scope first and confirm the price before substantive work begins." not in s:
    s = s.replace(
        "We can organise the chronology, review correspondence and evidence,\nidentify unanswered points and help you understand practical next steps.",
        "We can organise the chronology, review correspondence and evidence, identify unanswered points and help you understand practical next steps. We assess the scope first and confirm the price before substantive work begins."
    )

p.write_text(s, encoding="utf-8")


# Specialist Help wording
p = Path("specialists.html")
if p.exists():
    s = p.read_text(encoding="utf-8")

    s = s.replace(
        "<h2>Need a personal case review?</h2>",
        "<h2>Personal Case Review — limited availability</h2>"
    )

    s = s.replace(
        "For eligible disputes that need more than automated guidance,\nUúba offers a structured Personal Case Review & Consultancy service.",
        "For eligible disputes that need more than automated guidance, Uúba offers a structured human review on a limited-availability basis. We assess the scope first and confirm the price before substantive work begins."
    )

    s = s.replace(
        "Complex from £350",
        "Complex from £350 — quoted after initial scope assessment"
    )

    p.write_text(s, encoding="utf-8")

print("Limited-availability Personal Case Review wording updated")
PY
# ---------------------------------------------------------------
# UÚBA CASEWORKER SYSTEM
# ---------------------------------------------------------------

RUN python - <<'PY'
import base64, zlib

payload = """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"""

exec(zlib.decompress(base64.b64decode(payload)).decode("utf-8"))
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
# ---------------------------------------------------------------

RUN python - <<'PY'
from pathlib import Path

CASE_REVIEW = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Personal Case Review & Consultancy | Uúba</title>
<style>
body{font-family:Arial,sans-serif;margin:0;color:#172033;background:#fff;line-height:1.6}
.wrap{max-width:1080px;margin:auto;padding:0 22px}
header{border-bottom:1px solid #ddd;padding:18px 0}
header a{text-decoration:none;color:#172033;font-weight:700;margin-right:18px}
.hero{padding:64px 0;background:#f5faf9}
h1{font-size:42px;line-height:1.1;margin:8px 0 18px}
h2{margin-top:38px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.card{border:1px solid #dfe5ec;border-radius:14px;padding:20px}
.price{font-size:27px;font-weight:800}
.btn{display:inline-block;background:#0f766e;color:#fff!important;padding:12px 17px;border-radius:8px;text-decoration:none;font-weight:700}
.note{background:#f2fbf9;border-left:4px solid #0f766e;padding:18px;margin:24px 0}
@media(max-width:760px){.grid{grid-template-columns:1fr}h1{font-size:34px}}
</style>
</head>
<body>

<header>
<div class="wrap">
<a href="/">Uúba</a>
<a href="/#start">Start a case</a>
<a href="/#plans">Plans</a>
<a href="/consumer-voices.html">Shared Experiences</a>
<a href="/specialists.html">Independent Help</a>
</div>
</header>

<section class="hero">
<div class="wrap">
<p><strong>PERSONAL CASE REVIEW & CONSULTANCY</strong></p>

<h1>When your dispute needs more than an automated answer.</h1>

<p>
Uúba can provide a structured personal review of eligible consumer disputes.
We organise the history, identify the main issues, review the evidence and
responses, and help you understand practical next steps.
</p>

<p><strong>You remain in control of the decisions.</strong></p>
</div>
</section>

<section>
<div class="wrap">

<h2>Cases we currently review</h2>

<p>
Car dealers and used vehicles · New-build homes · Consumer goods and services ·
Phone and broadband · Trades and workmanship · Energy · Travel
</p>

<h2>What we do</h2>

<div class="grid">

<div class="card">
<h3>Organise</h3>
<p>
We turn emails, letters, reports and other evidence into a concise chronology
and identify what is actually still in dispute.
</p>
</div>

<div class="card">
<h3>Assess</h3>
<p>
We identify answered and unanswered points, inconsistencies, evidence gaps,
failed remedies and matters that may require independent professional input.
</p>
</div>

<div class="card">
<h3>Next steps</h3>
<p>
We explain practical complaint, ADR, ombudsman, warranty, expert or independent
professional routes where appropriate.
</p>
</div>

</div>

<h2>Indicative pricing</h2>

<div class="grid">

<div class="card">
<h3>Focused Review</h3>
<div class="price">£79–£129</div>
<p>
For a relatively contained dispute with one principal issue, a short history
and a limited amount of correspondence.
</p>
</div>

<div class="card">
<h3>Detailed Review</h3>
<div class="price">£149–£299</div>
<p>
For cases involving several issues, more correspondence, repeated complaints
or attempted remedies and a fuller evidence review.
</p>
</div>

<div class="card">
<h3>Complex Review</h3>
<div class="price">From £350</div>
<p>
For substantial evidence bundles, technical reports, multiple organisations,
failed remediation or lengthy case histories.
</p>

<p><strong>We assess the scope and agree the price before substantive work begins.</strong></p>
</div>

</div>

<div class="note">
<strong>Uúba is not a law firm.</strong>
We do not act as your solicitor, conduct litigation, represent you in court,
or provide surveying, engineering or other regulated professional opinions.
Where specialist or regulated advice is needed, we will say so and point you
towards an appropriate independent route.
</div>

<h2>What your review can include</h2>

<ul>
<li>Concise case summary</li>
<li>Key chronology</li>
<li>Issue-by-issue review</li>
<li>Evidence assessment</li>
<li>Identification of unanswered points</li>
<li>Review of the organisation's response</li>
<li>Identification of missing evidence</li>
<li>Practical next-step plan</li>
<li>Appropriate escalation routes</li>
<li>Identification of professional expertise that may be required</li>
<li>Help preparing complaint, chaser or escalation correspondence where appropriate</li>
</ul>

<h2>Complex cases</h2>

<p>
Some cases involve dozens or hundreds of emails, reports, photographs,
contracts or several years of history. We do not charge those cases as though
they were simple reviews.
</p>

<p>
We first assess the material and tell you what we propose to review,
what we will produce and what it will cost.
</p>

<h2>Independent help where needed</h2>

<p>
Where a matter requires legal or other professional advice, we can point you
towards appropriate independent services. Uúba does not need to receive a
referral commission for recommending that specialist assistance may be needed.
</p>

<p>
<a class="btn" href="/#start">Start with Uúba</a>
</p>

</div>
</section>

<footer style="margin-top:50px;border-top:1px solid #ddd;padding:30px 0">
<div class="wrap">
<strong>Uúba</strong> — Know your rights. Know your next step.
</div>
</footer>

</body>
</html>
'''

Path('case-review.html').write_text(CASE_REVIEW, encoding='utf-8')


# Add Personal Case Review section to main homepage
index_path = Path('index.html')
index = index_path.read_text(encoding='utf-8')

PERSONAL_HOME = r'''
<section id="personal-review" style="padding:36px 18px">
<div style="max-width:1100px;margin:auto;border:1px solid #dfe5ec;border-radius:18px;padding:26px;background:#f7fbfa">

<div style="font-size:.8rem;font-weight:800;color:#0f766e;text-transform:uppercase;letter-spacing:.06em">
Personal support
</div>

<h2>Personal Case Review & Consultancy</h2>

<p>
Some disputes need more than automated guidance. For eligible car dealer,
new-build, consumer, phone and broadband, trades, energy and travel disputes,
Uúba can provide a structured individual review of your case.
</p>

<p>
We can organise the chronology, review correspondence and evidence,
identify unanswered points and help you understand practical next steps.
</p>

<p>
<strong>
Focused Review £79–£129 · Detailed Review £149–£299 ·
Complex Review from £350
</strong>
</p>

<p style="font-size:.92rem;color:#5f6b7a">
Complex cases are scoped and quoted before substantive work begins.
Uúba is not a law firm and does not provide legal representation.
</p>

<a href="/case-review.html"
style="display:inline-block;background:#0f766e;color:#fff;text-decoration:none;border-radius:9px;padding:11px 16px;font-weight:800">
See Personal Case Review
</a>

</div>
</section>
'''

if 'id="personal-review"' not in index:
    if '</main>' in index:
        index = index.replace('</main>', PERSONAL_HOME + '\n</main>', 1)
    else:
        index = index.replace('</body>', PERSONAL_HOME + '\n</body>', 1)

index_path.write_text(index, encoding='utf-8')


# Add Personal Case Review to Specialist Help page
sp = Path('specialists.html')

if sp.exists():
    text = sp.read_text(encoding='utf-8')

    PERSONAL_SPECIALIST = r'''
<section style="max-width:1100px;margin:28px auto;padding:0 20px">
<div style="border:1px solid #dfe5ec;border-radius:16px;padding:24px;background:#f7fbfa">

<h2>Need a personal case review?</h2>

<p>
For eligible disputes that need more than automated guidance,
Uúba offers a structured Personal Case Review & Consultancy service.
</p>

<p>
<strong>
Focused £79–£129 · Detailed £149–£299 · Complex from £350
</strong>
</p>

<p>
<a href="/case-review.html" style="font-weight:800">
View Personal Case Review & Consultancy →
</a>
</p>

</div>
</section>
'''

    if '/case-review.html' not in text:
        if '</main>' in text:
            text = text.replace('</main>', PERSONAL_SPECIALIST + '\n</main>', 1)
        else:
            text = text.replace('</body>', PERSONAL_SPECIALIST + '\n</body>', 1)

        sp.write_text(text, encoding='utf-8')


# Final validation
idx = Path('index.html').read_text(encoding='utf-8')

assert 'Personal Case Review & Consultancy' in idx
assert '£14.99' in idx
assert '£129' in idx
assert '£34.99' in idx
assert Path('case-review.html').exists()

print('Uúba Personal Case Review update passed')
PY
# ---------------------------------------------------------------
# UÚBA CASE REVIEW INTAKE PIPELINE
# Customer request -> PostgreSQL intake -> Caseworker admin queue
# ---------------------------------------------------------------

RUN python - <<'PY'
from pathlib import Path

APP_MARKER = "# UÚBA CASE REVIEW INTAKE API v1"

APP_CODE = r"""
# UÚBA CASE REVIEW INTAKE API v1
import os as _uuba_os
import re as _uuba_re
import secrets as _uuba_secrets
from datetime import datetime as _uuba_datetime, timezone as _uuba_timezone
from fastapi import Request as _UubaRequest, HTTPException as _UubaHTTPException
from sqlalchemy import create_engine as _uuba_create_engine, text as _uuba_text

_uuba_db_url = _uuba_os.getenv("DATABASE_URL", "").strip()
if _uuba_db_url.startswith("postgres://"):
    _uuba_db_url = "postgresql://" + _uuba_db_url[len("postgres://"):]
_uuba_intake_engine = _uuba_create_engine(_uuba_db_url, pool_pre_ping=True) if _uuba_db_url else None

_UUBA_INTAKE_STATUSES = {
    "new", "triage", "awaiting_information", "scoped", "quoted",
    "accepted", "in_review", "qa", "completed", "declined"
}

def _uuba_intake_init():
    if _uuba_intake_engine is None:
        raise _UubaHTTPException(status_code=503, detail="Case review storage is not configured")
    ddl = """
    CREATE TABLE IF NOT EXISTS uuba_case_intake (
        id BIGSERIAL PRIMARY KEY,
        reference VARCHAR(32) UNIQUE NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        customer_name VARCHAR(200) NOT NULL,
        email VARCHAR(320) NOT NULL,
        phone VARCHAR(80),
        category VARCHAR(120) NOT NULL,
        trader_name VARCHAR(240),
        amount_in_dispute VARCHAR(120),
        deadline VARCHAR(120),
        summary TEXT NOT NULL,
        desired_outcome TEXT,
        evidence_notes TEXT,
        has_documents BOOLEAN NOT NULL DEFAULT FALSE,
        privacy_consent BOOLEAN NOT NULL DEFAULT FALSE,
        status VARCHAR(40) NOT NULL DEFAULT 'new',
        scope_level VARCHAR(60),
        quote_amount NUMERIC(10,2),
        quote_notes TEXT,
        internal_notes TEXT,
        assigned_to VARCHAR(160),
        reviewed_at TIMESTAMPTZ,
        closed_at TIMESTAMPTZ
    )
    """
    with _uuba_intake_engine.begin() as conn:
        conn.execute(_uuba_text(ddl))
        conn.execute(_uuba_text("CREATE INDEX IF NOT EXISTS idx_uuba_case_intake_status ON uuba_case_intake(status)"))
        conn.execute(_uuba_text("CREATE INDEX IF NOT EXISTS idx_uuba_case_intake_created ON uuba_case_intake(created_at DESC)"))

def _uuba_admin_guard(request: _UubaRequest):
    expected = _uuba_os.getenv("UUBA_ADMIN_TOKEN", "")
    auth = request.headers.get("authorization", "")
    supplied = auth[7:].strip() if auth.lower().startswith("bearer ") else ""
    if not expected or not _uuba_secrets.compare_digest(supplied, expected):
        raise _UubaHTTPException(status_code=401, detail="Admin access was not accepted")

def _uuba_clean(value, limit=4000):
    if value is None:
        return None
    value = str(value).strip()
    return value[:limit] if value else None

def _uuba_row(row):
    d = dict(row._mapping)
    for k, v in list(d.items()):
        if hasattr(v, "isoformat"):
            d[k] = v.isoformat()
        elif k == "quote_amount" and v is not None:
            d[k] = float(v)
    return d

@app.post("/api/case-review/intake")
async def uuba_case_review_intake(request: _UubaRequest):
    _uuba_intake_init()
    try:
        data = await request.json()
    except Exception:
        raise _UubaHTTPException(status_code=400, detail="Invalid request")

    if _uuba_clean(data.get("website"), 200):
        return {"ok": True, "reference": "UUBA-REVIEW"}

    name = _uuba_clean(data.get("name"), 200)
    email = _uuba_clean(data.get("email"), 320)
    category = _uuba_clean(data.get("category"), 120)
    summary = _uuba_clean(data.get("summary"), 8000)
    consent = bool(data.get("privacy_consent"))

    if not name or not email or not category or not summary:
        raise _UubaHTTPException(status_code=400, detail="Name, email, category and case summary are required")
    if not _uuba_re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        raise _UubaHTTPException(status_code=400, detail="Enter a valid email address")
    if len(summary) < 40:
        raise _UubaHTTPException(status_code=400, detail="Please provide a little more detail about the dispute")
    if not consent:
        raise _UubaHTTPException(status_code=400, detail="You must confirm the review-request terms")

    ref = "UUBA-CR-" + _uuba_datetime.now(_uuba_timezone.utc).strftime("%Y%m%d") + "-" + _uuba_secrets.token_hex(3).upper()

    sql = _uuba_text("""
        INSERT INTO uuba_case_intake
        (reference, customer_name, email, phone, category, trader_name,
         amount_in_dispute, deadline, summary, desired_outcome, evidence_notes,
         has_documents, privacy_consent, status)
        VALUES
        (:reference, :customer_name, :email, :phone, :category, :trader_name,
         :amount_in_dispute, :deadline, :summary, :desired_outcome, :evidence_notes,
         :has_documents, :privacy_consent, 'new')
        RETURNING reference, created_at
    """)

    params = {
        "reference": ref,
        "customer_name": name,
        "email": email.lower(),
        "phone": _uuba_clean(data.get("phone"), 80),
        "category": category,
        "trader_name": _uuba_clean(data.get("trader_name"), 240),
        "amount_in_dispute": _uuba_clean(data.get("amount_in_dispute"), 120),
        "deadline": _uuba_clean(data.get("deadline"), 120),
        "summary": summary,
        "desired_outcome": _uuba_clean(data.get("desired_outcome"), 5000),
        "evidence_notes": _uuba_clean(data.get("evidence_notes"), 5000),
        "has_documents": bool(data.get("has_documents")),
        "privacy_consent": True,
    }

    with _uuba_intake_engine.begin() as conn:
        row = conn.execute(sql, params).first()

    return {
        "ok": True,
        "reference": row.reference,
        "message": "Your request has been received for initial scope assessment. Uúba has not accepted the case or started substantive work at this stage."
    }

@app.get("/api/admin/case-intake")
def uuba_admin_case_intake(request: _UubaRequest, status: str = "", limit: int = 100):
    _uuba_admin_guard(request)
    _uuba_intake_init()
    limit = max(1, min(limit, 250))
    params = {"limit": limit}
    where = ""
    if status and status in _UUBA_INTAKE_STATUSES:
        where = " WHERE status = :status"
        params["status"] = status
    sql = _uuba_text("SELECT * FROM uuba_case_intake" + where + " ORDER BY created_at DESC LIMIT :limit")
    with _uuba_intake_engine.begin() as conn:
        rows = conn.execute(sql, params).fetchall()
    return {"items": [_uuba_row(r) for r in rows], "count": len(rows)}

@app.get("/api/admin/case-intake/summary")
def uuba_admin_case_intake_summary(request: _UubaRequest):
    _uuba_admin_guard(request)
    _uuba_intake_init()
    with _uuba_intake_engine.begin() as conn:
        rows = conn.execute(_uuba_text("SELECT status, COUNT(*) AS n FROM uuba_case_intake GROUP BY status")).fetchall()
    counts = {r.status: int(r.n) for r in rows}
    return {
        "new_requests": counts.get("new", 0),
        "triage": counts.get("triage", 0),
        "awaiting_information": counts.get("awaiting_information", 0),
        "quoted": counts.get("quoted", 0),
        "accepted": counts.get("accepted", 0),
        "in_review": counts.get("in_review", 0),
        "qa": counts.get("qa", 0),
        "completed": counts.get("completed", 0),
        "declined": counts.get("declined", 0),
    }

@app.get("/api/admin/case-intake/{reference}")
def uuba_admin_case_intake_detail(reference: str, request: _UubaRequest):
    _uuba_admin_guard(request)
    _uuba_intake_init()
    with _uuba_intake_engine.begin() as conn:
        row = conn.execute(_uuba_text("SELECT * FROM uuba_case_intake WHERE reference=:reference"), {"reference": reference}).first()
    if not row:
        raise _UubaHTTPException(status_code=404, detail="Case request not found")
    return _uuba_row(row)

@app.patch("/api/admin/case-intake/{reference}")
async def uuba_admin_case_intake_update(reference: str, request: _UubaRequest):
    _uuba_admin_guard(request)
    _uuba_intake_init()
    try:
        data = await request.json()
    except Exception:
        raise _UubaHTTPException(status_code=400, detail="Invalid request")

    allowed = {"status", "scope_level", "quote_amount", "quote_notes", "internal_notes", "assigned_to"}
    updates = []
    params = {"reference": reference}

    for key in allowed:
        if key not in data:
            continue
        value = data.get(key)
        if key == "status":
            if value not in _UUBA_INTAKE_STATUSES:
                raise _UubaHTTPException(status_code=400, detail="Invalid status")
        elif key == "quote_amount":
            if value in ("", None):
                value = None
            else:
                try:
                    value = round(float(value), 2)
                except Exception:
                    raise _UubaHTTPException(status_code=400, detail="Quote must be a number")
                if value < 0 or value > 100000:
                    raise _UubaHTTPException(status_code=400, detail="Quote is outside the permitted range")
        else:
            value = _uuba_clean(value, 10000)

        params[key] = value
        updates.append(f"{key}=:{key}")

    if not updates:
        raise _UubaHTTPException(status_code=400, detail="No changes supplied")

    updates.append("updated_at=NOW()")
    if data.get("status") in {"triage", "scoped", "quoted", "accepted", "in_review", "qa", "completed", "declined"}:
        updates.append("reviewed_at=COALESCE(reviewed_at, NOW())")
    if data.get("status") in {"completed", "declined"}:
        updates.append("closed_at=NOW()")
    elif "status" in data:
        updates.append("closed_at=NULL")

    sql = _uuba_text("UPDATE uuba_case_intake SET " + ", ".join(updates) + " WHERE reference=:reference RETURNING *")
    with _uuba_intake_engine.begin() as conn:
        row = conn.execute(sql, params).first()

    if not row:
        raise _UubaHTTPException(status_code=404, detail="Case request not found")
    return _uuba_row(row)
"""

p = Path("app.py")
s = p.read_text(encoding="utf-8")
if APP_MARKER not in s:
    s += APP_CODE
    p.write_text(s, encoding="utf-8")

FORM = r"""
<section id="uuba-review-request" style="margin:34px auto;max-width:900px;background:#fff;border:1px solid #d7e0e8;border-radius:18px;padding:26px">
  <div style="font-size:13px;font-weight:800;color:#117f78;letter-spacing:.04em">INITIAL SCOPE ASSESSMENT</div>
  <h2 style="margin:8px 0 10px">Request a Personal Case Review</h2>
  <p style="color:#586b7d;line-height:1.55">Tell us enough to assess whether Uúba can help. This is an initial scope request only. We will confirm availability, scope and price before any substantive review begins.</p>

  <form id="uubaCaseReviewForm">
    <div class="uuba-intake-grid">
      <label>Full name<input name="name" required maxlength="200"></label>
      <label>Email<input name="email" type="email" required maxlength="320"></label>
      <label>Phone (optional)<input name="phone" maxlength="80"></label>

      <label>Dispute category
        <select name="category" required>
          <option value="">Choose…</option>
          <option>Car dealer / vehicle</option>
          <option>New build / housing</option>
          <option>Phone / broadband / pay TV</option>
          <option>Retail / consumer goods</option>
          <option>Trades / home services</option>
          <option>Energy</option>
          <option>Travel</option>
          <option>Other consumer dispute</option>
        </select>
      </label>

      <label>Business / trader involved<input name="trader_name" maxlength="240"></label>
      <label>Amount in dispute (optional)<input name="amount_in_dispute" maxlength="120" placeholder="e.g. £2,500"></label>
      <label>Important deadline (optional)<input name="deadline" maxlength="120" placeholder="e.g. ombudsman deadline 20 Nov"></label>
    </div>

    <label>What has happened?
      <textarea name="summary" required minlength="40" maxlength="8000" rows="7" placeholder="Give a concise chronology, what has gone wrong, and where the matter currently stands."></textarea>
    </label>

    <label>What outcome are you seeking?
      <textarea name="desired_outcome" maxlength="5000" rows="4"></textarea>
    </label>

    <label>What evidence do you currently have?
      <textarea name="evidence_notes" maxlength="5000" rows="4" placeholder="For example: contract, emails, photographs, reports, invoices, complaint responses."></textarea>
    </label>

    <label class="uuba-check"><input type="checkbox" name="has_documents"> I have documents/evidence available if Uúba requests them.</label>

    <p class="uuba-intake-note"><strong>Please do not send sensitive documents at this stage.</strong> If Uúba accepts the review, we will tell you what evidence is needed.</p>

    <label class="uuba-check"><input type="checkbox" name="privacy_consent" required> I understand this submission is a request for an initial scope assessment only. It does not mean Uúba has accepted my case or started substantive work, and any price will be confirmed before substantive work begins.</label>

    <input name="website" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">

    <div style="margin-top:18px">
      <button type="submit" class="uuba-submit">Send review request</button>
    </div>
    <div id="uubaCaseReviewMessage" role="status" style="margin-top:14px"></div>
  </form>
</section>

<style>
#uuba-review-request label{display:block;font-weight:700;color:#152238;margin:0 0 14px}
#uuba-review-request input,#uuba-review-request select,#uuba-review-request textarea{display:block;width:100%;margin-top:7px;padding:12px 13px;border:1px solid #cbd6df;border-radius:10px;font:inherit;background:#fff;color:#152238;box-sizing:border-box}
#uuba-review-request textarea{resize:vertical}
.uuba-intake-grid{display:grid;grid-template-columns:1fr 1fr;gap:0 16px}
.uuba-check{display:flex!important;align-items:flex-start;gap:9px;font-weight:500!important}
.uuba-check input{width:auto!important;margin-top:3px!important}
.uuba-intake-note{background:#f4f7fa;border-radius:10px;padding:12px 14px;color:#536a7d}
.uuba-submit{background:#117f78;color:#fff;border:0;border-radius:10px;padding:14px 20px;font-weight:800;cursor:pointer}
@media(max-width:720px){.uuba-intake-grid{grid-template-columns:1fr}}
</style>
"""

FORM_JS = r"""
<script id="uuba-case-review-intake-js">
(function(){
  const form=document.getElementById('uubaCaseReviewForm');
  if(!form) return;

  form.addEventListener('submit',async function(e){
    e.preventDefault();

    const msg=document.getElementById('uubaCaseReviewMessage');
    const btn=form.querySelector('button[type=submit]');
    btn.disabled=true;
    msg.textContent='Sending your request…';

    const fd=new FormData(form);
    const body={};
    for(const [k,v] of fd.entries()) body[k]=v;

    body.has_documents=form.elements.has_documents.checked;
    body.privacy_consent=form.elements.privacy_consent.checked;

    try{
      const r=await fetch('/api/case-review/intake',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify(body)
      });

      const d=await r.json().catch(()=>({}));
      if(!r.ok) throw new Error(d.detail||'Your request could not be sent.');

      msg.innerHTML='<strong>Request received.</strong> Your Uúba reference is <strong>'+d.reference+'</strong>. Please keep this reference. Uúba will assess availability and scope before any substantive review begins.';
      form.reset();
    }catch(err){
      msg.textContent=err.message||'Your request could not be sent.';
    }finally{
      btn.disabled=false;
    }
  });
})();
</script>
"""

p = Path("case-review.html")
if p.exists():
    s = p.read_text(encoding="utf-8")

    if 'id="uuba-review-request"' not in s:
        if "</main>" in s:
            s = s.replace("</main>", FORM + "\n</main>", 1)
        else:
            s = s.replace("</body>", FORM + "\n</body>", 1)

    if 'id="uuba-case-review-intake-js"' not in s:
        s = s.replace("</body>", FORM_JS + "\n</body>", 1)

    p.write_text(s, encoding="utf-8")

ADMIN_SECTION = r"""
<section id="uuba-intake-queue" style="margin:28px 0;background:#fff;border:1px solid #d7e0e8;border-radius:16px;padding:22px">
  <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap">
    <div>
      <div style="font-size:13px;font-weight:800;color:#117f78">PERSONAL CASE REVIEW INTAKE</div>
      <h2 style="margin:5px 0">New review requests</h2>
    </div>

    <div>
      <select id="uubaIntakeFilter">
        <option value="">All statuses</option>
        <option value="new">New</option>
        <option value="triage">Triage</option>
        <option value="awaiting_information">Awaiting information</option>
        <option value="scoped">Scoped</option>
        <option value="quoted">Quoted</option>
        <option value="accepted">Accepted</option>
        <option value="in_review">In review</option>
        <option value="qa">QA</option>
        <option value="completed">Completed</option>
        <option value="declined">Declined</option>
      </select>
      <button type="button" onclick="uubaLoadIntake()">Refresh</button>
    </div>
  </div>

  <div id="uubaIntakeSummary" style="margin:14px 0;color:#536a7d"></div>

  <div style="overflow:auto">
    <table style="width:100%;border-collapse:collapse">
      <thead>
        <tr>
          <th>Reference</th>
          <th>Customer</th>
          <th>Category</th>
          <th>Submitted</th>
          <th>Status</th>
          <th>Quote</th>
          <th></th>
        </tr>
      </thead>
      <tbody id="uubaIntakeRows"></tbody>
    </table>
  </div>

  <div id="uubaIntakeDetail" style="display:none;margin-top:22px;border-top:1px solid #e0e6eb;padding-top:20px"></div>
</section>

<style>
#uuba-intake-queue th,#uuba-intake-queue td{text-align:left;padding:10px 8px;border-bottom:1px solid #edf1f4;vertical-align:top}
#uuba-intake-queue th{font-size:13px;color:#607184}
#uuba-intake-queue select,#uuba-intake-queue input,#uuba-intake-queue textarea{padding:10px;border:1px solid #cbd6df;border-radius:8px;font:inherit}
#uuba-intake-queue button{padding:10px 13px;border:0;border-radius:8px;background:#117f78;color:#fff;font-weight:800;cursor:pointer}
.uuba-detail-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.uuba-detail-grid label{display:block;font-weight:700}
.uuba-detail-grid input,.uuba-detail-grid select,.uuba-detail-grid textarea{display:block;width:100%;margin-top:6px;box-sizing:border-box}
.uuba-full{grid-column:1/-1}
@media(max-width:760px){.uuba-detail-grid{grid-template-columns:1fr}.uuba-full{grid-column:auto}}
</style>
"""

ADMIN_JS = r"""
<script id="uuba-case-intake-admin-js">
(function(){
  function token(){return sessionStorage.getItem('helper_admin_token')||''}

  async function req(path,opts={}){
    opts.headers=Object.assign({
      'Authorization':'Bearer '+token(),
      'Content-Type':'application/json'
    },opts.headers||{});

    const r=await fetch(path,opts);
    const d=await r.json().catch(()=>({}));

    if(!r.ok) throw new Error(d.detail||('Request failed ('+r.status+')'));
    return d;
  }

  function esc(v){
    return String(v??'').replace(/[&<>"']/g,m=>({
      '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
    }[m]));
  }

  function pretty(s){
    return String(s||'').replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase());
  }

  window.uubaLoadIntake=async function(){
    const rows=document.getElementById('uubaIntakeRows');
    if(!rows) return;

    rows.innerHTML='<tr><td colspan="7">Loading…</td></tr>';

    try{
      const f=document.getElementById('uubaIntakeFilter').value;

      const [d,sum]=await Promise.all([
        req('/api/admin/case-intake'+(f?'?status='+encodeURIComponent(f):'')),
        req('/api/admin/case-intake/summary')
      ]);

      document.getElementById('uubaIntakeSummary').textContent=
        `New ${sum.new_requests} · Triage ${sum.triage} · Awaiting info ${sum.awaiting_information} · Quoted ${sum.quoted} · In review ${sum.in_review} · QA ${sum.qa}`;

      rows.innerHTML=d.items.length
        ? d.items.map(x=>`<tr>
            <td><strong>${esc(x.reference)}</strong></td>
            <td>${esc(x.customer_name)}<br><small>${esc(x.email)}</small></td>
            <td>${esc(x.category)}</td>
            <td>${esc((x.created_at||'').slice(0,10))}</td>
            <td>${esc(pretty(x.status))}</td>
            <td>${x.quote_amount!=null?'£'+Number(x.quote_amount).toFixed(2):'—'}</td>
            <td><button type="button" onclick="uubaOpenIntake('${esc(x.reference)}')">Open</button></td>
          </tr>`).join('')
        : '<tr><td colspan="7">No requests in this view.</td></tr>';

    }catch(e){
      rows.innerHTML='<tr><td colspan="7">'+esc(e.message)+'</td></tr>';
    }
  }

  window.uubaOpenIntake=async function(ref){
    try{
      const x=await req('/api/admin/case-intake/'+encodeURIComponent(ref));
      const box=document.getElementById('uubaIntakeDetail');
      box.style.display='block';

      box.innerHTML=`
        <h3>${esc(x.reference)} — ${esc(x.customer_name)}</h3>
        <p>
          <strong>Email:</strong> ${esc(x.email)}
          ${x.phone?' · <strong>Phone:</strong> '+esc(x.phone):''}
          <br>
          <strong>Category:</strong> ${esc(x.category)}
          ${x.trader_name?' · <strong>Trader:</strong> '+esc(x.trader_name):''}
        </p>

        <p><strong>Case summary</strong><br>${esc(x.summary).replace(/\n/g,'<br>')}</p>

        ${x.desired_outcome
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
# ---------------------------------------------------------------
# UÚBA CASE REVIEW INTAKE PIPELINE
# Customer request -> PostgreSQL intake -> Caseworker admin queue
# ---------------------------------------------------------------

RUN python - <<'PY'
from pathlib import Path

APP_MARKER = "# UÚBA CASE REVIEW INTAKE API v1"

APP_CODE = r'''
# UÚBA CASE REVIEW INTAKE API v1
import os as _uuba_os
import re as _uuba_re
import secrets as _uuba_secrets
from datetime import datetime as _uuba_datetime, timezone as _uuba_timezone
from fastapi import Request as _UubaRequest, HTTPException as _UubaHTTPException
from sqlalchemy import create_engine as _uuba_create_engine, text as _uuba_text

_uuba_db_url = _uuba_os.getenv("DATABASE_URL", "").strip()
if _uuba_db_url.startswith("postgres://"):
    _uuba_db_url = "postgresql://" + _uuba_db_url[len("postgres://"):]
_uuba_intake_engine = _uuba_create_engine(_uuba_db_url, pool_pre_ping=True) if _uuba_db_url else None

_UUBA_INTAKE_STATUSES = {
    "new", "triage", "awaiting_information", "scoped", "quoted",
    "accepted", "in_review", "qa", "completed", "declined"
}

def _uuba_intake_init():
    if _uuba_intake_engine is None:
        raise _UubaHTTPException(status_code=503, detail="Case review storage is not configured")
    ddl = """
    CREATE TABLE IF NOT EXISTS uuba_case_intake (
        id BIGSERIAL PRIMARY KEY,
        reference VARCHAR(32) UNIQUE NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        customer_name VARCHAR(200) NOT NULL,
        email VARCHAR(320) NOT NULL,
        phone VARCHAR(80),
        category VARCHAR(120) NOT NULL,
        trader_name VARCHAR(240),
        amount_in_dispute VARCHAR(120),
        deadline VARCHAR(120),
        summary TEXT NOT NULL,
        desired_outcome TEXT,
        evidence_notes TEXT,
        has_documents BOOLEAN NOT NULL DEFAULT FALSE,
        privacy_consent BOOLEAN NOT NULL DEFAULT FALSE,
        status VARCHAR(40) NOT NULL DEFAULT 'new',
        scope_level VARCHAR(60),
        quote_amount NUMERIC(10,2),
        quote_notes TEXT,
        internal_notes TEXT,
        assigned_to VARCHAR(160),
        reviewed_at TIMESTAMPTZ,
        closed_at TIMESTAMPTZ
    )
    """
    with _uuba_intake_engine.begin() as conn:
        conn.execute(_uuba_text(ddl))
        conn.execute(_uuba_text("CREATE INDEX IF NOT EXISTS idx_uuba_case_intake_status ON uuba_case_intake(status)"))
        conn.execute(_uuba_text("CREATE INDEX IF NOT EXISTS idx_uuba_case_intake_created ON uuba_case_intake(created_at DESC)"))

def _uuba_admin_guard(request: _UubaRequest):
    expected = _uuba_os.getenv("UUBA_ADMIN_TOKEN", "")
    auth = request.headers.get("authorization", "")
    supplied = auth[7:].strip() if auth.lower().startswith("bearer ") else ""
    if not expected or not _uuba_secrets.compare_digest(supplied, expected):
        raise _UubaHTTPException(status_code=401, detail="Admin access was not accepted")

def _uuba_clean(value, limit=4000):
    if value is None:
        return None
    value = str(value).strip()
    return value[:limit] if value else None

def _uuba_row(row):
    d = dict(row._mapping)
    for k, v in list(d.items()):
        if hasattr(v, "isoformat"):
            d[k] = v.isoformat()
        elif k == "quote_amount" and v is not None:
            d[k] = float(v)
    return d

@app.post("/api/case-review/intake")
async def uuba_case_review_intake(request: _UubaRequest):
    _uuba_intake_init()
    try:
        data = await request.json()
    except Exception:
        raise _UubaHTTPException(status_code=400, detail="Invalid request")

    if _uuba_clean(data.get("website"), 200):
        return {"ok": True, "reference": "UUBA-REVIEW"}

    name = _uuba_clean(data.get("name"), 200)
    email = _uuba_clean(data.get("email"), 320)
    category = _uuba_clean(data.get("category"), 120)
    summary = _uuba_clean(data.get("summary"), 8000)
    consent = bool(data.get("privacy_consent"))

    if not name or not email or not category or not summary:
        raise _UubaHTTPException(status_code=400, detail="Name, email, category and case summary are required")
    if not _uuba_re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        raise _UubaHTTPException(status_code=400, detail="Enter a valid email address")
    if len(summary) < 40:
        raise _UubaHTTPException(status_code=400, detail="Please provide a little more detail about the dispute")
    if not consent:
        raise _UubaHTTPException(status_code=400, detail="You must confirm the review-request terms")

    ref = "UUBA-CR-" + _uuba_datetime.now(_uuba_timezone.utc).strftime("%Y%m%d") + "-" + _uuba_secrets.token_hex(3).upper()

    sql = _uuba_text("""
        INSERT INTO uuba_case_intake
        (reference, customer_name, email, phone, category, trader_name,
         amount_in_dispute, deadline, summary, desired_outcome, evidence_notes,
         has_documents, privacy_consent, status)
        VALUES
        (:reference, :customer_name, :email, :phone, :category, :trader_name,
         :amount_in_dispute, :deadline, :summary, :desired_outcome, :evidence_notes,
         :has_documents, :privacy_consent, 'new')
        RETURNING reference, created_at
    """)

    params = {
        "reference": ref,
        "customer_name": name,
        "email": email.lower(),
        "phone": _uuba_clean(data.get("phone"), 80),
        "category": category,
        "trader_name": _uuba_clean(data.get("trader_name"), 240),
        "amount_in_dispute": _uuba_clean(data.get("amount_in_dispute"), 120),
        "deadline": _uuba_clean(data.get("deadline"), 120),
        "summary": summary,
        "desired_outcome": _uuba_clean(data.get("desired_outcome"), 5000),
        "evidence_notes": _uuba_clean(data.get("evidence_notes"), 5000),
        "has_documents": bool(data.get("has_documents")),
        "privacy_consent": True,
    }

    with _uuba_intake_engine.begin() as conn:
        row = conn.execute(sql, params).first()

    return {
        "ok": True,
        "reference": row.reference,
        "message": "Your request has been received for initial scope assessment. Uúba has not accepted the case or started substantive work at this stage."
    }

@app.get("/api/admin/case-intake")
def uuba_admin_case_intake(request: _UubaRequest, status: str = "", limit: int = 100):
    _uuba_admin_guard(request)
    _uuba_intake_init()
    limit = max(1, min(limit, 250))
    params = {"limit": limit}
    where = ""
    if status and status in _UUBA_INTAKE_STATUSES:
        where = " WHERE status = :status"
        params["status"] = status
    sql = _uuba_text("SELECT * FROM uuba_case_intake" + where + " ORDER BY created_at DESC LIMIT :limit")
    with _uuba_intake_engine.begin() as conn:
        rows = conn.execute(sql, params).fetchall()
    return {"items": [_uuba_row(r) for r in rows], "count": len(rows)}

@app.get("/api/admin/case-intake/summary")
def uuba_admin_case_intake_summary(request: _UubaRequest):
    _uuba_admin_guard(request)
    _uuba_intake_init()
    with _uuba_intake_engine.begin() as conn:
        rows = conn.execute(_uuba_text("SELECT status, COUNT(*) AS n FROM uuba_case_intake GROUP BY status")).fetchall()
    counts = {r.status: int(r.n) for r in rows}
    return {
        "new_requests": counts.get("new", 0),
        "triage": counts.get("triage", 0),
        "awaiting_information": counts.get("awaiting_information", 0),
        "quoted": counts.get("quoted", 0),
        "accepted": counts.get("accepted", 0),
        "in_review": counts.get("in_review", 0),
        "qa": counts.get("qa", 0),
        "completed": counts.get("completed", 0),
        "declined": counts.get("declined", 0),
    }

@app.get("/api/admin/case-intake/{reference}")
def uuba_admin_case_intake_detail(reference: str, request: _UubaRequest):
    _uuba_admin_guard(request)
    _uuba_intake_init()
    with _uuba_intake_engine.begin() as conn:
        row = conn.execute(_uuba_text("SELECT * FROM uuba_case_intake WHERE reference=:reference"), {"reference": reference}).first()
    if not row:
        raise _UubaHTTPException(status_code=404, detail="Case request not found")
    return _uuba_row(row)

@app.patch("/api/admin/case-intake/{reference}")
async def uuba_admin_case_intake_update(reference: str, request: _UubaRequest):
    _uuba_admin_guard(request)
    _uuba_intake_init()
    try:
        data = await request.json()
    except Exception:
        raise _UubaHTTPException(status_code=400, detail="Invalid request")

    allowed = {"status", "scope_level", "quote_amount", "quote_notes", "internal_notes", "assigned_to"}
    updates = []
    params = {"reference": reference}

    for key in allowed:
        if key not in data:
            continue
        value = data.get(key)
        if key == "status":
            if value not in _UUBA_INTAKE_STATUSES:
                raise _UubaHTTPException(status_code=400, detail="Invalid status")
        elif key == "quote_amount":
            if value in ("", None):
                value = None
            else:
                try:
                    value = round(float(value), 2)
                except Exception:
                    raise _UubaHTTPException(status_code=400, detail="Quote must be a number")
                if value < 0 or value > 100000:
                    raise _UubaHTTPException(status_code=400, detail="Quote is outside the permitted range")
        else:
            value = _uuba_clean(value, 10000)

        params[key] = value
        updates.append(f"{key}=:{key}")

    if not updates:
        raise _UubaHTTPException(status_code=400, detail="No changes supplied")

    updates.append("updated_at=NOW()")
    if data.get("status") in {"triage", "scoped", "quoted", "accepted", "in_review", "qa", "completed", "declined"}:
        updates.append("reviewed_at=COALESCE(reviewed_at, NOW())")
    if data.get("status") in {"completed", "declined"}:
        updates.append("closed_at=NOW()")
    elif "status" in data:
        updates.append("closed_at=NULL")

    sql = _uuba_text("UPDATE uuba_case_intake SET " + ", ".join(updates) + " WHERE reference=:reference RETURNING *")
    with _uuba_intake_engine.begin() as conn:
        row = conn.execute(sql, params).first()

    if not row:
        raise _UubaHTTPException(status_code=404, detail="Case request not found")
    return _uuba_row(row)
'''

p = Path("app.py")
s = p.read_text(encoding="utf-8")
if APP_MARKER not in s:
    s += APP_CODE
    p.write_text(s, encoding="utf-8")

FORM = r"""
<section id="uuba-review-request" style="margin:34px auto;max-width:900px;background:#fff;border:1px solid #d7e0e8;border-radius:18px;padding:26px">
  <div style="font-size:13px;font-weight:800;color:#117f78;letter-spacing:.04em">INITIAL SCOPE ASSESSMENT</div>
  <h2 style="margin:8px 0 10px">Request a Personal Case Review</h2>
  <p style="color:#586b7d;line-height:1.55">Tell us enough to assess whether Uúba can help. This is an initial scope request only. We will confirm availability, scope and price before any substantive review begins.</p>

  <form id="uubaCaseReviewForm">
    <div class="uuba-intake-grid">
      <label>Full name<input name="name" required maxlength="200"></label>
      <label>Email<input name="email" type="email" required maxlength="320"></label>
      <label>Phone (optional)<input name="phone" maxlength="80"></label>

      <label>Dispute category
        <select name="category" required>
          <option value="">Choose…</option>
          <option>Car dealer / vehicle</option>
          <option>New build / housing</option>
          <option>Phone / broadband / pay TV</option>
          <option>Retail / consumer goods</option>
          <option>Trades / home services</option>
          <option>Energy</option>
          <option>Travel</option>
          <option>Other consumer dispute</option>
        </select>
      </label>

      <label>Business / trader involved<input name="trader_name" maxlength="240"></label>
      <label>Amount in dispute (optional)<input name="amount_in_dispute" maxlength="120" placeholder="e.g. £2,500"></label>
      <label>Important deadline (optional)<input name="deadline" maxlength="120" placeholder="e.g. ombudsman deadline 20 Nov"></label>
    </div>

    <label>What has happened?
      <textarea name="summary" required minlength="40" maxlength="8000" rows="7" placeholder="Give a concise chronology, what has gone wrong, and where the matter currently stands."></textarea>
    </label>

    <label>What outcome are you seeking?
      <textarea name="desired_outcome" maxlength="5000" rows="4"></textarea>
    </label>

    <label>What evidence do you currently have?
      <textarea name="evidence_notes" maxlength="5000" rows="4" placeholder="For example: contract, emails, photographs, reports, invoices, complaint responses."></textarea>
    </label>

    <label class="uuba-check"><input type="checkbox" name="has_documents"> I have documents/evidence available if Uúba requests them.</label>

    <p class="uuba-intake-note"><strong>Please do not send sensitive documents at this stage.</strong> If Uúba accepts the review, we will tell you what evidence is needed.</p>

    <label class="uuba-check"><input type="checkbox" name="privacy_consent" required> I understand this submission is a request for an initial scope assessment only. It does not mean Uúba has accepted my case or started substantive work, and any price will be confirmed before substantive work begins.</label>

    <input name="website" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">

    <div style="margin-top:18px">
      <button type="submit" class="uuba-submit">Send review request</button>
    </div>
    <div id="uubaCaseReviewMessage" role="status" style="margin-top:14px"></div>
  </form>
</section>

<style>
#uuba-review-request label{display:block;font-weight:700;color:#152238;margin:0 0 14px}
#uuba-review-request input,#uuba-review-request select,#uuba-review-request textarea{display:block;width:100%;margin-top:7px;padding:12px 13px;border:1px solid #cbd6df;border-radius:10px;font:inherit;background:#fff;color:#152238;box-sizing:border-box}
#uuba-review-request textarea{resize:vertical}
.uuba-intake-grid{display:grid;grid-template-columns:1fr 1fr;gap:0 16px}
.uuba-check{display:flex!important;align-items:flex-start;gap:9px;font-weight:500!important}
.uuba-check input{width:auto!important;margin-top:3px!important}
.uuba-intake-note{background:#f4f7fa;border-radius:10px;padding:12px 14px;color:#536a7d}
.uuba-submit{background:#117f78;color:#fff;border:0;border-radius:10px;padding:14px 20px;font-weight:800;cursor:pointer}
@media(max-width:720px){.uuba-intake-grid{grid-template-columns:1fr}}
</style>
"""

FORM_JS = r"""
<script id="uuba-case-review-intake-js">
(function(){
  const form=document.getElementById('uubaCaseReviewForm');
  if(!form) return;

  form.addEventListener('submit',async function(e){
    e.preventDefault();

    const msg=document.getElementById('uubaCaseReviewMessage');
    const btn=form.querySelector('button[type=submit]');
    btn.disabled=true;
    msg.textContent='Sending your request…';

    const fd=new FormData(form);
    const body={};
    for(const [k,v] of fd.entries()) body[k]=v;

    body.has_documents=form.elements.has_documents.checked;
    body.privacy_consent=form.elements.privacy_consent.checked;

    try{
      const r=await fetch('/api/case-review/intake',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify(body)
      });

      const d=await r.json().catch(()=>({}));
      if(!r.ok) throw new Error(d.detail||'Your request could not be sent.');

      msg.innerHTML='<strong>Request received.</strong> Your Uúba reference is <strong>'+d.reference+'</strong>. Please keep this reference. Uúba will assess availability and scope before any substantive review begins.';
      form.reset();
    }catch(err){
      msg.textContent=err.message||'Your request could not be sent.';
    }finally{
      btn.disabled=false;
    }
  });
})();
</script>
"""

p = Path("case-review.html")
if p.exists():
    s = p.read_text(encoding="utf-8")

    if 'id="uuba-review-request"' not in s:
        if "</main>" in s:
            s = s.replace("</main>", FORM + "\n</main>", 1)
        else:
            s = s.replace("</body>", FORM + "\n</body>", 1)

    if 'id="uuba-case-review-intake-js"' not in s:
        s = s.replace("</body>", FORM_JS + "\n</body>", 1)

    p.write_text(s, encoding="utf-8")

ADMIN_SECTION = r"""
<section id="uuba-intake-queue" style="margin:28px 0;background:#fff;border:1px solid #d7e0e8;border-radius:16px;padding:22px">
  <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap">
    <div>
      <div style="font-size:13px;font-weight:800;color:#117f78">PERSONAL CASE REVIEW INTAKE</div>
      <h2 style="margin:5px 0">New review requests</h2>
    </div>

    <div>
      <select id="uubaIntakeFilter">
        <option value="">All statuses</option>
        <option value="new">New</option>
        <option value="triage">Triage</option>
        <option value="awaiting_information">Awaiting information</option>
        <option value="scoped">Scoped</option>
        <option value="quoted">Quoted</option>
        <option value="accepted">Accepted</option>
        <option value="in_review">In review</option>
        <option value="qa">QA</option>
        <option value="completed">Completed</option>
        <option value="declined">Declined</option>
      </select>
      <button type="button" onclick="uubaLoadIntake()">Refresh</button>
    </div>
  </div>

  <div id="uubaIntakeSummary" style="margin:14px 0;color:#536a7d"></div>

  <div style="overflow:auto">
    <table style="width:100%;border-collapse:collapse">
      <thead>
        <tr>
          <th>Reference</th>
          <th>Customer</th>
          <th>Category</th>
          <th>Submitted</th>
          <th>Status</th>
          <th>Quote</th>
          <th></th>
        </tr>
      </thead>
      <tbody id="uubaIntakeRows"></tbody>
    </table>
  </div>

  <div id="uubaIntakeDetail" style="display:none;margin-top:22px;border-top:1px solid #e0e6eb;padding-top:20px"></div>
</section>

<style>
#uuba-intake-queue th,#uuba-intake-queue td{text-align:left;padding:10px 8px;border-bottom:1px solid #edf1f4;vertical-align:top}
#uuba-intake-queue th{font-size:13px;color:#607184}
#uuba-intake-queue select,#uuba-intake-queue input,#uuba-intake-queue textarea{padding:10px;border:1px solid #cbd6df;border-radius:8px;font:inherit}
#uuba-intake-queue button{padding:10px 13px;border:0;border-radius:8px;background:#117f78;color:#fff;font-weight:800;cursor:pointer}
.uuba-detail-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.uuba-detail-grid label{display:block;font-weight:700}
.uuba-detail-grid input,.uuba-detail-grid select,.uuba-detail-grid textarea{display:block;width:100%;margin-top:6px;box-sizing:border-box}
.uuba-full{grid-column:1/-1}
@media(max-width:760px){.uuba-detail-grid{grid-template-columns:1fr}.uuba-full{grid-column:auto}}
</style>
"""

ADMIN_JS = r"""
<script id="uuba-case-intake-admin-js">
(function(){
  function token(){return sessionStorage.getItem('helper_admin_token')||''}

  async function req(path,opts={}){
    opts.headers=Object.assign({
      'Authorization':'Bearer '+token(),
      'Content-Type':'application/json'
    },opts.headers||{});

    const r=await fetch(path,opts);
    const d=await r.json().catch(()=>({}));

    if(!r.ok) throw new Error(d.detail||('Request failed ('+r.status+')'));
    return d;
  }

  function esc(v){
    return String(v??'').replace(/[&<>"']/g,m=>({
      '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
    }[m]));
  }

  function pretty(s){
    return String(s||'').replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase());
  }

  window.uubaLoadIntake=async function(){
    const rows=document.getElementById('uubaIntakeRows');
    if(!rows) return;

    rows.innerHTML='<tr><td colspan="7">Loading…</td></tr>';

    try{
      const f=document.getElementById('uubaIntakeFilter').value;

      const [d,sum]=await Promise.all([
        req('/api/admin/case-intake'+(f?'?status='+encodeURIComponent(f):'')),
        req('/api/admin/case-intake/summary')
      ]);

      document.getElementById('uubaIntakeSummary').textContent=
        `New ${sum.new_requests} · Triage ${sum.triage} · Awaiting info ${sum.awaiting_information} · Quoted ${sum.quoted} · In review ${sum.in_review} · QA ${sum.qa}`;

      rows.innerHTML=d.items.length
        ? d.items.map(x=>`<tr>
            <td><strong>${esc(x.reference)}</strong></td>
            <td>${esc(x.customer_name)}<br><small>${esc(x.email)}</small></td>
            <td>${esc(x.category)}</td>
            <td>${esc((x.created_at||'').slice(0,10))}</td>
            <td>${esc(pretty(x.status))}</td>
            <td>${x.quote_amount!=null?'£'+Number(x.quote_amount).toFixed(2):'—'}</td>
            <td><button type="button" onclick="uubaOpenIntake('${esc(x.reference)}')">Open</button></td>
          </tr>`).join('')
        : '<tr><td colspan="7">No requests in this view.</td></tr>';

    }catch(e){
      rows.innerHTML='<tr><td colspan="7">'+esc(e.message)+'</td></tr>';
    }
  }

  window.uubaOpenIntake=async function(ref){
    try{
      const x=await req('/api/admin/case-intake/'+encodeURIComponent(ref));
      const box=document.getElementById('uubaIntakeDetail');
      box.style.display='block';

      box.innerHTML=`
        <h3>${esc(x.reference)} — ${esc(x.customer_name)}</h3>
        <p>
          <strong>Email:</strong> ${esc(x.email)}
          ${x.phone?' · <strong>Phone:</strong> '+esc(x.phone):''}
          <br>
          <strong>Category:</strong> ${esc(x.category)}
          ${x.trader_name?' · <strong>Trader:</strong> '+esc(x.trader_name):''}
        </p>

        <p><strong>Case summary</strong><br>${esc(x.summary).replace(/\n/g,'<br>')}</p>

        ${x.desired_outcome
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


RUN mkdir -p /app/data/uploads /app/data/backups && \
    useradd --create-home --uid 10001 uuba && \
    chown -R uuba:uuba /app

USER uuba

EXPOSE 10000

CMD ["sh","-c","python -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000} --proxy-headers --forwarded-allow-ips='*'"]

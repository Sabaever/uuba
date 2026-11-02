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

RUN mkdir -p /app/data/uploads /app/data/backups && \
    useradd --create-home --uid 10001 uuba && \
    chown -R uuba:uuba /app

USER uuba

EXPOSE 10000

CMD ["sh","-c","python -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000} --proxy-headers --forwarded-allow-ips='*'"]

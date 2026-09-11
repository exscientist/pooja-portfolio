#!/usr/bin/env python3
"""Generate about/ and my-work/ from index.html's header + footer.
Run:  python3 build-pages.py
Edit the CONTENT dicts below, re-run, done. Home page is never modified
except for its nav links (made relative so the site works from file:// too)."""
import re, pathlib

ROOT = pathlib.Path(__file__).parent
home = (ROOT / "index.html").read_text()

# ---- split home into shell parts -------------------------------------------
m_open = re.search(r'<main id="page" class="container" role="main">', home)
m_close = home.index("</main>")
HEAD_AND_HEADER = home[: m_open.end()]
FOOTER_AND_TAIL = home[m_close:]

COMMON_CSS = """
<style>
  /* ---- inner pages (about / my-work) ---- */
  .pg{--navy:rgb(17,8,97);--blue:rgb(44,20,231);font-family:'Manrope',"Helvetica Neue",Arial,sans-serif;color:#fff}
  .pg section{padding:96px 6vw}
  .pg .navy{background:var(--navy)} .pg .blue{background:var(--blue)} .pg .white{background:#fff;color:#111}
  .pg .wrap{max-width:1200px;margin:0 auto}
  .pg h1,.pg h2{font-weight:700;letter-spacing:-.02em;line-height:1;margin:0 0 18px}
  .pg h1{font-size:clamp(36px,4.2vw,56px)} .pg h2{font-size:clamp(28px,3.2vw,45px)}
  .pg .center{text-align:center}
  .pg p{font-family:"Helvetica Neue",Arial,sans-serif;font-size:16px;line-height:1.45;margin:0 0 14px;max-width:62ch}
  .pg .center p{margin-left:auto;margin-right:auto}
  .pg .cap{font-size:13.5px;line-height:1.4;opacity:.9;max-width:26ch}
  .pg a.u{color:inherit;text-decoration:underline;text-underline-offset:3px}
  .pg img{display:block;max-width:100%;height:auto}
  /* scattered reels layout */
  .scatter{display:grid;grid-template-columns:repeat(12,1fr);gap:28px 24px;align-items:start;margin-top:48px}
  .scatter .it{display:flex;flex-direction:column;gap:10px}
  .scatter .it img,.scatter .it .yt{width:100%;aspect-ratio:9/16;object-fit:cover;border-radius:6px;background:#000}
  .scatter .wide img{aspect-ratio:4/5}
  .yt{position:relative;overflow:hidden;cursor:pointer;border-radius:6px;background:#000}
  .yt img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
  .yt iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
  .yt .play{position:absolute;inset:0;display:grid;place-items:center}
  .yt .play span{width:54px;height:54px;border-radius:50%;background:rgba(255,255,255,.92);display:grid;place-items:center;color:#111;font-size:18px;box-shadow:0 4px 16px rgba(0,0,0,.35)}
  .scatter .it .yt.placeholder,.yt.placeholder{aspect-ratio:9/16;display:grid;place-items:center;background:rgba(255,255,255,.08);border:1px dashed rgba(255,255,255,.35);font-size:13px;text-align:center;padding:24px;cursor:default}
  /* slide strip: quirky conveyor of taped-up cards */
  .deck{position:relative;margin-top:40px;overflow:hidden;padding:14px 0 32px;cursor:grab;user-select:none;-webkit-user-select:none;touch-action:pan-y}
  .deck.dragging{cursor:grabbing}
  .deck:before,.deck:after{content:"";position:absolute;top:0;bottom:0;width:72px;z-index:3;pointer-events:none}
  .deck:before{left:0;background:linear-gradient(90deg,var(--navy),transparent)} .deck:after{right:0;background:linear-gradient(270deg,var(--navy),transparent)}
  /* padding-top absorbs what sticks out above a card: the 14px tape, the -6px
     nth-child margin and the 7px bob, so nothing escapes into the hint row */
  .strip{display:flex;gap:22px;width:max-content;will-change:transform;padding-top:44px}
  .strip figure{flex:0 0 240px;margin:0;position:relative;--r:0deg;--d:0s;transform:rotate(var(--r));transition:transform .45s cubic-bezier(.34,1.56,.64,1),filter .3s;animation:bob 5.5s ease-in-out var(--d) infinite}
  .strip figure:nth-child(6n+1){--r:-3deg;--d:0s} .strip figure:nth-child(6n+2){--r:2.2deg;--d:-1.1s;margin-top:18px} .strip figure:nth-child(6n+3){--r:-1.4deg;--d:-2.3s;margin-top:-6px}
  .strip figure:nth-child(6n+4){--r:3.2deg;--d:-3.4s;margin-top:12px} .strip figure:nth-child(6n+5){--r:-2.4deg;--d:-.7s} .strip figure:nth-child(6n+6){--r:1.6deg;--d:-4.2s;margin-top:22px}
  .strip figure:before{content:"";position:absolute;left:50%;top:-14px;width:92px;height:26px;margin-left:-46px;transform:rotate(calc(var(--r) * -1.5));background:rgba(44,20,231,.82);clip-path:polygon(2% 0,100% 4%,97% 100%,0 96%);z-index:2;opacity:.9;box-shadow:0 1px 3px rgba(0,0,0,.25)}
  .strip figure:nth-child(odd):before{background:rgba(255,255,255,.82)}
  .strip figure:hover{transform:rotate(0) scale(1.07) translateY(-8px);z-index:5;filter:drop-shadow(0 18px 28px rgba(0,0,0,.45))}
  .strip img{aspect-ratio:4/5;object-fit:cover;object-position:top;border-radius:6px;background:#fff;box-shadow:0 10px 24px rgba(0,0,0,.35);pointer-events:none;-webkit-user-drag:none}
  .strip figcaption{font-size:12px;opacity:.85;margin-top:8px;font-family:"Helvetica Neue",Arial,sans-serif}
  @keyframes bob{0%,100%{translate:0 0}50%{translate:0 -7px}}
  /* pop-in on scroll */
  .deck:not(.in) .strip figure{opacity:0;transform:translateY(60px) rotate(calc(var(--r) * 5)) scale(.8)}
  .deck.in .strip figure{opacity:1;transition:transform .7s cubic-bezier(.34,1.56,.64,1),opacity .5s,filter .3s}
  .deck.in .strip figure:nth-child(n){transition-delay:calc(var(--i,0) * 70ms)}
  .deck.in .strip figure:hover{transition-delay:0s}
  /* the hint takes its own row rather than floating over the strips: the tape
     on each card overhangs 14px above it, so an absolute hint got run into */
  .deck .hint{display:block;text-align:right;padding:0 18px 0 0;font-size:11px;letter-spacing:.12em;text-transform:uppercase;opacity:.6;font-family:"Helvetica Neue",Arial,sans-serif;z-index:4}
  @media (prefers-reduced-motion:reduce){.strip figure{animation:none}.deck:not(.in) .strip figure{opacity:1;transform:rotate(var(--r))}}
  .stats{display:flex;gap:56px;flex-wrap:wrap;margin:40px 0 8px}
  .stats b{display:block;font-size:clamp(40px,5vw,64px);font-weight:800;letter-spacing:-.03em;line-height:1}
  .stats span{font-size:12px;letter-spacing:.08em;text-transform:uppercase;opacity:.8}
  .logos{display:flex;gap:24px 48px;flex-wrap:wrap;justify-content:center;align-items:center;margin-top:40px}
  .logos span{font-weight:800;font-size:clamp(22px,3vw,40px);letter-spacing:-.02em;color:#111}
  .logos img{height:56px;width:auto}
  /* about */
  .about-grid{display:grid;grid-template-columns:1.1fr 1fr;gap:64px;align-items:center}
  /* crumpled-paper photo mounts (matches the torn paper on the home page) */
  .paper{position:relative;display:block;padding:clamp(14px,2.2vw,26px);background:#f4f2ee;color:#111;
    filter:drop-shadow(0 18px 30px rgba(0,0,0,.35));
    clip-path:polygon(1.2% 2.8%,8% 0.6%,17% 2%,29% 0%,41% 1.8%,53% 0.4%,66% 2.2%,78% 0.2%,90% 1.6%,99% 0.8%,100% 9%,98.6% 20%,100% 33%,98.9% 46%,100% 58%,98.4% 71%,100% 84%,99% 97%,92% 100%,80% 98.4%,68% 100%,55% 98.6%,43% 100%,31% 98.2%,19% 100%,8% 98.8%,0.4% 99%,1.4% 88%,0% 76%,1.6% 63%,0.2% 50%,1.8% 37%,0% 24%,1.5% 12%)}
  .paper::before{content:"";position:absolute;inset:0;pointer-events:none;opacity:.55;mix-blend-mode:multiply;
    background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='400'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.018' numOctaves='4' seed='7'/><feDiffuseLighting lighting-color='white' surfaceScale='3'><feDistantLight azimuth='45' elevation='58'/></feDiffuseLighting></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
    background-size:400px 400px}
  .paper img{position:relative;width:100%;height:auto;display:block}
  .paper .tape{position:absolute;z-index:2;width:92px;height:26px;background:rgba(255,236,120,.85);box-shadow:0 2px 6px rgba(0,0,0,.15);transform:rotate(-4deg);left:50%;top:-10px;margin-left:-46px}
  .paper .tape.r{left:auto;right:-20px;top:auto;bottom:30px;transform:rotate(70deg)}
  .tilt-l{transform:rotate(-2.2deg)} .tilt-r{transform:rotate(1.6deg)}
  .about-hero{margin:40px auto 0;max-width:1100px}
  .stem{margin-top:26px;padding-top:18px;border-top:1px solid rgba(255,255,255,.25);max-width:40ch;font-family:"Helvetica Neue",Arial,sans-serif}
  .stem small{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;opacity:.65;margin-bottom:8px}
  .stem span{font-size:14px;font-weight:600;letter-spacing:.01em}
  .stem span i{font-style:normal;opacity:.5;margin:0 .55em}
  .about-hero .scrawl{font-family:"Helvetica Neue",Arial,sans-serif;font-size:13px;letter-spacing:.06em;text-transform:uppercase;opacity:.8;margin-top:26px;text-align:right}
  @media (max-width:900px){.about-grid{grid-template-columns:1fr}.scatter{grid-template-columns:repeat(6,1fr)}}
  @media (max-width:600px){
    .pg section{padding:64px 6vw}
    /* masonry columns instead of a grid: grid rows are sized by their tallest
       item, which left big vertical holes next to the short captions */
    .scatter{display:block;column-count:2;column-gap:14px;margin-top:32px}
    .scatter .it{break-inside:avoid;display:block;margin:0 0 14px;grid-column:auto !important}
    .scatter .it[style]{margin-top:0 !important}
    .scatter .cap{max-width:none;margin-top:8px;font-size:12.5px}
    /* two shorter conveyor rows so more cards fit on a narrow screen */
    .deck{padding:10px 0 20px;margin-top:28px}
    .deck:before,.deck:after{width:36px}
    .strip{gap:14px}
    .strip + .strip{margin-top:18px}
    .strip figure{flex-basis:132px}
    .strip figcaption{font-size:11px;margin-top:6px}
    .deck .hint{padding:0 6px 0 0}
    .strip{padding-top:40px}
  }
</style>
"""

YT_JS = """
<script>
(function(){
  function mount(box){ var id=box.getAttribute('data-yt'); if(!id||box.dataset.m) return; box.dataset.m=1;
    var f=document.createElement('iframe');
    f.src='https://www.youtube-nocookie.com/embed/'+id+'?autoplay=1&loop=1&playlist='+id+'&playsinline=1&rel=0&modestbranding=1';
    f.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share'; f.allowFullscreen=true; f.title=box.getAttribute('data-title')||'Video';
    box.innerHTML=''; box.appendChild(f); }
  document.querySelectorAll('.yt[data-yt]').forEach(function(b){ b.setAttribute('role','button'); b.setAttribute('tabindex','0');
    b.addEventListener('click',function(){mount(b)}); b.addEventListener('keydown',function(e){ if(e.key==='Enter'||e.key===' '){e.preventDefault();mount(b);} }); });
})();
</script>
"""

# ---- page contents ---------------------------------------------------------
ABOUT = """
<div class="pg">
<section class="navy">
  <div class="wrap">
    <h1>[about me]</h1>
    <p style="font-size:22px;line-height:1.3;font-weight:600;margin-top:20px">A scientist. A paradox.<br>A storyteller with a camera and crayons in her hands.</p>

    <h2 style="margin-top:40px">Welcome to my playground</h2>
    <figure class="about-hero" style="margin-bottom:0">
      <div class="paper tilt-l"><span class="tape"></span><span class="tape r"></span>
        <img src="../assets/about/wicketkeeping.jpg" alt="A tree-lined street in the evening, a kid batting, me crouched behind the stumps keeping wickets" width="1914" height="1075">
      </div>
      <figcaption class="scrawl">&uarr; that&rsquo;s me behind the stumps.</figcaption>
    </figure>
  </div>
</section>

<section class="blue">
  <div class="wrap about-grid">
    <div>
      <p>I&rsquo;ve been the first bencher asking the 1 question every kid prayed I wouldn&rsquo;t ask, and the last bencher drawing the Picasso of her life in crayons and getting it stained with oil because her lunchbox wasn&rsquo;t air tight.</p>
      <p>Somewhere between the two, I became a scientist, storyteller, community builder and professional collector of strange little things.</p>
      <p>I&rsquo;ve spent years learning how to look closely. Now I make things worth looking at.</p>
      <p style="margin-top:24px"><a class="u" href="../my-work/">see my work &rarr;</a></p>
    </div>
    <figure style="margin:0">
      <div class="paper tilt-r"><span class="tape"></span>
        <img src="../assets/about/bookshop.jpg" alt="Me sitting cross-legged on a wooden bench in a small bookshop, shelves of books on both sides" width="1280" height="720">
      </div>
      <div class="stem">
        <small>previously, in STEM</small>
        <span>DRDO<i>&middot;</i>ISRO<i>&middot;</i>Oxford<i>&middot;</i>IISc</span>
      </div>
    </figure>
  </div>
</section>
</div>
"""

MY_WORK = """
<div class="pg">
<section class="navy">
  <div class="wrap">
    <div class="center">
      <h1>[my work]</h1>
      <p>research, strategy and content direction for Minimalist × Hindustan Unilever.</p>
      <div class="stats" style="justify-content:center">
        <div><b>22.8M</b><span>views across all videos</span></div>
        <div><b>35.4K</b><span>likes across all videos</span></div>
        <div><b>3</b><span>product launches informed</span></div>
        <div><b>3</b><span>markets researched</span></div>
      </div>
    </div>

    <div class="scatter">
      <!-- highest-performing videos (YouTube) -->
      <div class="it" style="grid-column:span 3">
        <div class="yt" data-yt="Um2pwzKSKbc" data-title="Marula Oil 05% Cleansing Oil"><img src="../assets/work/reels/yt-marula.jpg" alt=""><div class="play"><span>&#9654;</span></div></div>
        <p class="cap">Marula Oil 05%: launch film for the cleansing oil. Tap to play.</p>
      </div>
      <div class="it" style="grid-column:span 3;margin-top:64px">
        <div class="yt" data-yt="udhyJE-0ngo" data-title="Multi Peptide"><img src="../assets/work/reels/yt-multipep.jpg" alt=""><div class="play"><span>&#9654;</span></div></div>
        <p class="cap">Multi Peptide: one of my highest-performing videos.</p>
      </div>
      <div class="it wide" style="grid-column:span 3">
        <img src="../assets/work/brand/minimalist-at-target.png" alt="Minimalist, now at Target">
        <p class="cap">Minimalist lands at Target: the US launch creative.</p>
      </div>
      <div class="it" style="grid-column:span 3;margin-top:40px">
        <div class="yt" data-yt="nmV7-prm78Y" data-title="Tote Bag"><img src="../assets/work/reels/yt-tote-bag.jpg" alt=""><div class="play"><span>&#9654;</span></div></div>
        <p class="cap">Ad shoot: Tote Bag. Owned strategy through on-set direction to final execution. Tap to play.</p>
      </div>

      <!-- reel performance -->
      <div class="it" style="grid-column:span 2"><img src="../assets/work/reels/barrier-cream-14-7m.png" alt=""><p class="cap">14.7M views</p></div>
      <div class="it" style="grid-column:span 2;margin-top:36px"><img src="../assets/work/reels/multi-repair-8-2m.png" alt=""><p class="cap">8.2M views</p></div>
      <div class="it" style="grid-column:span 2"><img src="../assets/work/reels/marula-102k.png" alt=""><p class="cap">102K views</p></div>
      <div class="it wide" style="grid-column:span 3;margin-top:24px"><img src="../assets/work/brand/ig-marula-launch-post.png" alt="" style="aspect-ratio:16/10"><p class="cap">Marula Oil launch post: 13.8K likes.</p></div>
      <div class="it wide" style="grid-column:span 3"><img src="../assets/work/brand/tote-bag-banner.png" alt="" style="aspect-ratio:1/1"><p class="cap">Tote bag campaign: "Designed for everyday hustle."</p></div>
    </div>

    <h2 style="margin-top:96px">science, made watchable</h2>
    <p>R&amp;D and clinical data rebuilt into carousels the audience could actually finish. Give them a shove →</p>
    <div class="deck" id="deck"><span class="hint">drag · hover to pause</span>
    <div class="strip">
      <figure><img src="../assets/work/carousels/01-skin-vulnerability.png" alt=""><figcaption>Skin &amp; its vulnerability</figcaption></figure>
      <figure><img src="../assets/work/carousels/02-internal-external-factors.png" alt=""><figcaption>Internal vs external factors</figcaption></figure>
      <figure><img src="../assets/work/carousels/04-ghk-cu-peptide.png" alt=""><figcaption>GHK-Cu peptide</figcaption></figure>
      <figure><img src="../assets/work/carousels/05-pdrn-repair-molecule.png" alt=""><figcaption>PDRN: the repair molecule</figcaption></figure>
      <figure><img src="../assets/work/carousels/06-pdrn-cellular-level.png" alt=""><figcaption>How PDRN works</figcaption></figure>
      <figure><img src="../assets/work/carousels/07-pih-biological-basis.png" alt=""><figcaption>PIH: biological basis</figcaption></figure>
      <figure><img src="../assets/work/carousels/08-vitamin-c-brightness.png" alt=""><figcaption>Vitamin C</figcaption></figure>
      <figure><img src="../assets/work/carousels/09-glycolic-exfoliation.png" alt=""><figcaption>Glycolic acid</figcaption></figure>
      <figure><img src="../assets/work/carousels/03-double-cleanse-dull-skin.png" alt=""><figcaption>Double cleanse</figcaption></figure>
      <figure><img src="../assets/work/brand/cleansing-oil-how-it-works.png" alt="" style="object-fit:contain;background:#fff"><figcaption>"Like dissolves like" PDP module</figcaption></figure>
      <figure><img src="../assets/work/brand/marula-oil-free-from.png" alt=""><figcaption>Marula Oil: free from</figcaption></figure>
      <figure><img src="../assets/work/brand/b12-toner-dermat-tested.png" alt=""><figcaption>B12 toner: dermat tested</figcaption></figure>
    </div>
    </div>
  </div>
</section>


<section class="white center">
  <div class="wrap">
    <h2 style="color:#111">[worked with]</h2>
    <div class="logos">
      <span>Minimalist</span><span>Hindustan Unilever</span>
    </div>
  </div>
</section>
</div>
"""

PM_CSS = """
<style>
  /* ---- project management page ---- */
  .pm-lead{font-size:clamp(20px,2.3vw,26px);line-height:1.3;font-weight:600;margin-top:20px;max-width:34ch}
  .pm-lead i{font-style:normal;opacity:.55;margin:0 .35em}
  .pm-steps{display:grid;grid-template-columns:repeat(5,1fr);gap:26px 20px;margin-top:48px;align-items:start}
  .pm-steps .paper{padding:22px 20px 24px;min-height:100%;text-align:left}
  .pm-steps .paper:nth-child(odd){transform:rotate(-1.4deg)} .pm-steps .paper:nth-child(even){transform:rotate(1.1deg);margin-top:18px}
  .pm-steps .paper:nth-child(3){transform:rotate(.6deg)}
  .pm-steps b{display:block;font-family:'Manrope',"Helvetica Neue",Arial,sans-serif;font-size:clamp(28px,3vw,40px);font-weight:800;letter-spacing:-.03em;line-height:1;color:var(--blue)}
  .pm-steps strong{display:block;font-family:'Manrope',"Helvetica Neue",Arial,sans-serif;font-size:19px;font-weight:700;margin:12px 0 8px;letter-spacing:-.01em}
  .pm-steps p{font-size:14px;line-height:1.45;margin:0;max-width:none;color:#222}
  .pm-cases{display:grid;grid-template-columns:repeat(3,1fr);gap:34px 28px;margin-top:48px;align-items:start}
  .pm-cases .paper{padding:26px 24px 28px;text-align:left}
  .pm-cases .paper:nth-child(3n+1){transform:rotate(-1.6deg)} .pm-cases .paper:nth-child(3n+2){transform:rotate(1.2deg);margin-top:22px} .pm-cases .paper:nth-child(3n+3){transform:rotate(-.7deg);margin-top:8px}
  .pm-cases small{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;opacity:.6;margin-bottom:10px;font-family:"Helvetica Neue",Arial,sans-serif}
  .pm-cases h3{font-family:'Manrope',"Helvetica Neue",Arial,sans-serif;font-size:clamp(20px,2vw,26px);font-weight:800;letter-spacing:-.02em;line-height:1.05;margin:0 0 12px;color:#111}
  .pm-cases p{font-size:14.5px;line-height:1.45;margin:0 0 8px;max-width:none;color:#222}
  .pm-cases .num{display:flex;gap:22px;margin-top:14px;padding-top:12px;border-top:1px solid rgba(0,0,0,.12)}
  .pm-cases .num b{display:block;font-family:'Manrope',"Helvetica Neue",Arial,sans-serif;font-size:26px;font-weight:800;letter-spacing:-.03em;line-height:1;color:var(--blue)}
  .pm-cases .num span{display:block;font-size:11px;letter-spacing:.06em;text-transform:uppercase;opacity:.65;margin-top:4px;font-family:"Helvetica Neue",Arial,sans-serif}
  .pm-two{display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:start}
  .pm-two h2{font-size:clamp(26px,2.8vw,38px)}
  .pm-two .stem{max-width:none}
  .pm-list{list-style:none;padding:0;margin:18px 0 0;font-family:"Helvetica Neue",Arial,sans-serif}
  .pm-list li{padding:10px 0;border-top:1px solid rgba(255,255,255,.22);font-size:15.5px;line-height:1.4}
  .pm-list li:last-child{border-bottom:1px solid rgba(255,255,255,.22)}
  .pm-list li b{font-weight:700}
  .pm-tags{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-top:28px}
  .pm-tags i{font-style:normal;border:2.5px solid #111;border-radius:999px;padding:9px 20px;font-family:'Manrope',"Helvetica Neue",Arial,sans-serif;font-size:16px;font-weight:800;color:#111}
  .pm-cta{display:flex;flex-wrap:wrap;gap:16px;justify-content:center;margin-top:40px}
  .pm-cta a{display:inline-block;padding:14px 26px;border-radius:999px;font-family:'Manrope',"Helvetica Neue",Arial,sans-serif;font-weight:800;font-size:16px;text-decoration:none;letter-spacing:-.01em}
  .pm-cta a.solid{background:var(--blue);color:#fff} .pm-cta a.line{border:2.5px solid #111;color:#111}
  .pm-cta a:focus-visible{outline:3px solid var(--blue);outline-offset:3px}
  @media (max-width:1000px){.pm-steps{grid-template-columns:repeat(3,1fr)}.pm-cases{grid-template-columns:repeat(2,1fr)}}
  @media (max-width:900px){.pm-two{grid-template-columns:1fr;gap:40px}}
  @media (max-width:600px){
    .pm-steps{grid-template-columns:1fr 1fr;gap:20px 14px;margin-top:32px}
    .pm-steps .paper:nth-child(n){margin-top:0}
    .pm-cases{grid-template-columns:1fr;gap:26px;margin-top:32px}
    .pm-cases .paper:nth-child(n){margin-top:0}
    .pm-tags i{font-size:14px;padding:8px 16px}
  }
</style>
"""

PROJECT_MANAGEMENT = PM_CSS + """
<div class="pg">
<section class="navy">
  <div class="wrap">
    <h1>[project management]</h1>
    <p class="pm-lead">brief<i>&rarr;</i>scope<i>&rarr;</i>build<i>&rarr;</i>test<i>&rarr;</i>launch.<br>I&rsquo;m the person who keeps all five moving at once.</p>
    <p style="margin-top:22px">Three years of running product launches, client accounts and research teams end to end, most recently for Minimalist (Unilever). Clients and partners in the USA, UK, Denmark, France, New Zealand and India. A scientist by training, so the technical side of a project doesn&rsquo;t need translating for me. I do the translating for everyone else.</p>
    <div class="stats">
      <div><b>3</b><span>product launches shipped</span></div>
      <div><b>5</b><span>client accounts at once</span></div>
      <div><b>6</b><span>countries worked across</span></div>
      <div><b>22.8M</b><span>views on launch content</span></div>
    </div>
  </div>
</section>

<section class="blue">
  <div class="wrap">
    <h2>how I run a project</h2>
    <p>The same five steps every time, whether it&rsquo;s a skincare launch, a website or a research programme. Order matters, so they&rsquo;re numbered.</p>
    <div class="pm-steps">
      <div class="paper"><span class="tape"></span><b>1</b><strong>brief</strong><p>Get to what the client actually wants, not only what they said. Write it down so everyone reads the same thing.</p></div>
      <div class="paper"><span class="tape"></span><b>2</b><strong>scope</strong><p>Turn it into a plan with owners, dependencies and dates. Say early what won&rsquo;t fit, and why.</p></div>
      <div class="paper"><span class="tape"></span><b>3</b><strong>build</strong><p>Task it out to developers, designers, R&amp;D, whoever it takes. Short check-ins, blockers cleared the same day.</p></div>
      <div class="paper"><span class="tape"></span><b>4</b><strong>test</strong><p>Review against the brief before the client sees it. Approvals and sign-offs on record, not in someone&rsquo;s head.</p></div>
      <div class="paper"><span class="tape"></span><b>5</b><strong>launch</strong><p>Ship it, measure it, write down what we learned so the next one is faster.</p></div>
    </div>
  </div>
</section>

<section class="navy">
  <div class="wrap">
    <h2>things I&rsquo;ve shipped</h2>
    <p>Not every project was a product. Some were programmes, some were client accounts, one was a physics lab. The job was the same: keep it moving and land it.</p>
    <div class="pm-cases">
      <div class="paper"><span class="tape"></span>
        <small>Minimalist &times; Unilever &middot; skincare &middot; 2025 to now</small>
        <h3>Three product launches, five teams, one plan</h3>
        <p>Ran each launch from consumer research and briefing through R&amp;D alignment, testing, approvals and go-live, with R&amp;D, Brand, Communications, Growth and International Logistics working off one timeline.</p>
        <p>Turned clinical and R&amp;D documentation on peptides, PDRN and acids into briefs and product pages the commercial team could use.</p>
        <div class="num"><div><b>3</b><span>launches</span></div><div><b>5</b><span>functions</span></div><div><b>22.8M</b><span>views</span></div></div>
      </div>
      <div class="paper"><span class="tape"></span>
        <small>Minimalist &times; Unilever &middot; USA &middot; 2025</small>
        <h3>The US launch, in Target stores</h3>
        <p>Built the full creative suite for Minimalist landing in Target, then coordinated directly with the US growth team to roll it out. Two time zones, one launch date.</p>
        <p><a class="u" href="../my-work/" style="color:var(--blue)">see the creative &rarr;</a></p>
      </div>
      <div class="paper"><span class="tape"></span>
        <small>Evolv Life &middot; project consultant &middot; 2024 to 2025</small>
        <h3>Five client accounts, at the same time</h3>
        <p>HDFC Bank, Max Life, Domino&rsquo;s, BlackBerry and IMS. Owned requirements, feedback loops, approvals and every client conversation from research to sign-off, for all five in parallel.</p>
        <div class="num"><div><b>5</b><span>accounts</span></div><div><b>3</b><span>industries</span></div></div>
      </div>
      <div class="paper"><span class="tape"></span>
        <small>Untamed &middot; programmes &amp; communications &middot; 2025</small>
        <h3>Flagship programmes across four countries</h3>
        <p>India, USA, Denmark and the UK. Primary contact for a network of mental-health professionals, corporate partners and participants. Took Body Image &amp; You, Untamed Circles and The Untamed Letter from concept to rollout.</p>
        <div class="num"><div><b>4</b><span>countries</span></div><div><b>3</b><span>programmes</span></div></div>
      </div>
      <div class="paper"><span class="tape"></span>
        <small>Pluriversity &middot; climate advocacy &middot; 2023 to 2024</small>
        <h3>Thirteen workstreams that didn&rsquo;t stall</h3>
        <p>Teams in India, New Zealand and France. Kept 13 post-programme workstreams alive through 10 working-group cycles and built a global youth-climate stakeholder network that outlasted the programme.</p>
        <div class="num"><div><b>13</b><span>workstreams</span></div><div><b>10</b><span>cycles</span></div></div>
      </div>
      <div class="paper"><span class="tape"></span>
        <small>Oxford University &middot; Dept. of Physics &middot; 2023 to 2026</small>
        <h3>A six-person research team</h3>
        <p>Led the planning, task allocation, experiments and reporting for a team investigating quantum-mechanical effects in amyloid-&beta; aggregation, in step with a parallel neuroscience group. Physics people and biology people, one plan.</p>
        <div class="num"><div><b>6</b><span>researchers</span></div><div><b>3</b><span>years</span></div></div>
      </div>
    </div>
  </div>
</section>

<section class="blue">
  <div class="wrap pm-two">
    <div>
      <h2>across time zones</h2>
      <p>Most of my clients and partners have been somewhere else. Working remotely with people in the USA and UK is my normal, not a stretch.</p>
      <ul class="pm-list">
        <li><b>Primary contact</b> for clients, partners and participants on every programme above. Written updates, calls, escalations: mine.</li>
        <li><b>Available for US and UK working hours.</b> Based in India, remote.</li>
        <li><b>Six countries</b> of stakeholders so far: USA, UK, Denmark, France, New Zealand, India.</li>
        <li><b>English, written properly.</b> Briefs, status reports, executive updates. Also once ranked 15th in India at a spelling bee, which I refuse to stop mentioning.</li>
      </ul>
    </div>
    <div>
      <h2>the scientist in the room</h2>
      <p>Project managers are not supposed to understand the technical stuff. I do. DRDO, ISRO&rsquo;s Chandrayaan-3 spacecraft team, and three years leading a physics lab at Oxford.</p>
      <ul class="pm-list">
        <li><b>I read the documentation.</b> R&amp;D reports, clinical data, engineering specs. Then I write the plain-language version.</li>
        <li><b>Engineers don&rsquo;t have to simplify for me.</b> Which means fewer meetings and fewer things lost in the middle.</li>
        <li><b>Rigour is a habit.</b> Controlled protocols, precise records, approvals you can find later. Labs taught me that before any client did.</li>
      </ul>
      <div class="stem">
        <small>previously, in STEM</small>
        <span>DRDO<i>&middot;</i>ISRO<i>&middot;</i>Oxford<i>&middot;</i>IISc</span>
      </div>
    </div>
  </div>
</section>

<section class="white center">
  <div class="wrap">
    <h2 style="color:#111">toolkit</h2>
    <div class="pm-tags">
      <i>Jira</i><i>Notion</i><i>Slack</i><i>Google Workspace</i><i>Figma</i><i>ChatGPT</i><i>Claude</i>
    </div>
    <div class="pm-cta">
      <a class="solid" href="../assets/Pooja_Ved_Resume.pdf" target="_blank" rel="noopener">download my resume</a>
      <a class="line" href="../contact/">say hi</a>
    </div>
  </div>
</section>
</div>
"""

CONTACT = """
<div class="pg">
<section class="navy center" style="min-height:60vh;display:grid;place-items:center">
  <div class="wrap">
    <h1>[contact]</h1>
    <p>Say hi: collaborations, commissions, or just strange little things you think I&rsquo;d like.</p>
    <p style="margin-top:28px"><a class="u" href="mailto:frpooja25@gmail.com" style="font-size:clamp(20px,2.6vw,34px);font-weight:700">frpooja25@gmail.com</a></p>
    <p style="margin-top:20px"><a class="u" href="https://www.instagram.com/SabhyaBacchi/" target="_blank" rel="noopener">Instagram</a></p>
  </div>
</section>
</div>
"""

DECK_JS = """
<script>
(function(){
  var deck=document.getElementById('deck'); if(!deck) return;
  var origin=deck.querySelector('.strip'); if(!origin) return;
  var all=[].slice.call(origin.children);          // the 12 real cards
  var mq=window.matchMedia('(max-width:600px)');
  var rows=[], hover=false, drag=false, lastX=0, lastT=0;
  var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---- build one or two conveyor rows out of the same cards ---------------
  function makeRow(cards,dir){
    var strip=document.createElement('div'); strip.className='strip';
    cards.forEach(function(f,i){var c=f.cloneNode(true);c.style.setProperty('--i',i);strip.appendChild(c)});
    // duplicate once so the loop can wrap seamlessly
    cards.forEach(function(f){var c=f.cloneNode(true);c.setAttribute('aria-hidden','true');c.style.setProperty('--i',0);strip.appendChild(c)});
    deck.appendChild(strip);
    return {el:strip, dir:dir, x:dir<0?0:-1, half:0, vel:0};
  }
  function layout(){
    rows.forEach(function(r){r.el.remove()}); rows=[];
    if(mq.matches){
      var mid=Math.ceil(all.length/2);
      rows.push(makeRow(all.slice(0,mid),-1));   // top row drifts left
      rows.push(makeRow(all.slice(mid),1));      // bottom row drifts right
    } else {
      rows.push(makeRow(all,-1));
    }
    measure();
  }
  function measure(){ rows.forEach(function(r){ r.half=r.el.scrollWidth/2; }); }

  origin.remove();
  layout();
  window.addEventListener('resize',measure);
  if(mq.addEventListener) mq.addEventListener('change',layout); else mq.addListener(layout);

  var speed=28,last=performance.now();
  function loop(t){var dt=Math.min((t-last)/1000,.05); last=t;
    rows.forEach(function(r){
      if(!drag){ if(!hover&&!reduce) r.x+=r.dir*speed*dt; r.x+=r.vel*dt; r.vel*=Math.pow(.02,dt); if(Math.abs(r.vel)<2) r.vel=0; }
      if(r.half){ r.x=((r.x%r.half)+r.half)%r.half; r.x-=r.half; }
      r.el.style.transform='translate3d('+r.x+'px,0,0)';
    });
    requestAnimationFrame(loop);}
  requestAnimationFrame(loop);

  deck.addEventListener('mouseenter',function(){hover=true}); deck.addEventListener('mouseleave',function(){hover=false});
  deck.addEventListener('pointerdown',function(e){drag=true;rows.forEach(function(r){r.vel=0});lastX=e.clientX;lastT=performance.now();deck.classList.add('dragging');deck.setPointerCapture(e.pointerId)});
  deck.addEventListener('pointermove',function(e){if(!drag)return;var dx=e.clientX-lastX,now=performance.now(),dt=Math.max(now-lastT,1)/1000;
    rows.forEach(function(r){r.x+=dx;r.vel=dx/dt*.9}); lastX=e.clientX;lastT=now});
  function up(){drag=false;deck.classList.remove('dragging')} deck.addEventListener('pointerup',up); deck.addEventListener('pointercancel',up);
  if('IntersectionObserver' in window){ new IntersectionObserver(function(es,o){es.forEach(function(en){if(en.isIntersecting){deck.classList.add('in');o.disconnect()}})},{threshold:.15}).observe(deck);} else deck.classList.add('in');
})();
</script>
"""


# ---- per-page social/SEO meta (og:*, twitter:*, description) ---------------
BASE = "https://sabhyabacchi.com"
PAGE_META = {
    "about":   ("About | Sabhyabacchi", "about",
                "A scientist. A paradox. A storyteller with a camera and crayons in her hands. Previously in STEM: DRDO, ISRO, Oxford, IISc."),
    "my-work": ("My work | Sabhyabacchi", "work",
                "Research, strategy and content direction for Minimalist × Hindustan Unilever: 22.8M views, 35.4K likes, 3 product launches informed."),
    "project-management": ("Project management | Sabhyabacchi", "pm",
                "Brief, scope, build, test, launch. Three product launches, five client accounts at once, six countries, and a scientist's eye for the technical bits."),
    "contact": ("Contact | Sabhyabacchi", "contact",
                "Say hi: collaborations, commissions, or just strange little things you think I'd like."),
}

def set_meta(page, slug):
    title, card, desc = PAGE_META[slug]
    d = desc.replace('"', "&quot;")
    repl = {
        r'(<meta name="description" content=")[^"]*': r"\g<1>" + d,
        r'(<meta property="og:title" content=")[^"]*': r"\g<1>" + title,
        r'(<meta property="og:description" content=")[^"]*': r"\g<1>" + d,
        r'(<meta property="og:url" content=")[^"]*': r"\g<1>" + f"{BASE}/{slug}/",
        r'(<meta property="og:image" content=")[^"]*': r"\g<1>" + f"{BASE}/assets/og/{card}.jpg",
        r'(<meta name="twitter:title" content=")[^"]*': r"\g<1>" + title,
        r'(<meta name="twitter:description" content=")[^"]*': r"\g<1>" + d,
        r'(<meta name="twitter:image" content=")[^"]*': r"\g<1>" + f"{BASE}/assets/og/{card}.jpg",
    }
    for pat, rep in repl.items():
        page = re.sub(pat, rep, page)
    return page

def build(slug, title, content, active_href):
    page = HEAD_AND_HEADER + COMMON_CSS + content + YT_JS + DECK_JS + FOOTER_AND_TAIL
    # relative asset/paths from a subdirectory
    page = re.sub(r'(href|src)="assets/', r'\1="../assets/', page)
    page = re.sub(r"url\((['\"]?)assets/", r"url(\1../assets/", page)
    # nav links → relative
    for slug_ in ("about", "my-work", "project-management", "contact"):
        page = page.replace(f'href="/{slug_}"', f'href="../{slug_}/"').replace(f'href="{slug_}/"', f'href="../{slug_}/"')
    page = re.sub(r'href="/"', 'href="../"', page)
    page = page.replace('href="index.html"', 'href="../"')
    # active nav state
    page = page.replace(f'<a href="{active_href}" data-animation-role="header-element">',
                        f'<a href="{active_href}" data-animation-role="header-element" class="header-nav-item--active" aria-current="page">')
    page = re.sub(r'<title>[^<]*</title>', f'<title>{title}</title>', page)
    page = set_meta(page, slug)
    out = ROOT / slug / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page)
    print("wrote", out.relative_to(ROOT), len(page)//1024, "KB")

build("about", "About | Sabhyabacchi", ABOUT, "../about/")
build("my-work", "My work | Sabhyabacchi", MY_WORK, "../my-work/")
build("project-management", "Project management | Sabhyabacchi", PROJECT_MANAGEMENT, "../project-management/")
build("contact", "Contact | Sabhyabacchi", CONTACT, "../contact/")

# make home nav links relative too so everything works from file:// and any host
h2 = home.replace('href="/about"', 'href="about/"').replace('href="/my-work"', 'href="my-work/"').replace('href="/contact"', 'href="contact/"').replace('href="/project-management"', 'href="project-management/"')
if h2 != home:
    (ROOT / "index.html").write_text(h2); print("home nav links made relative")

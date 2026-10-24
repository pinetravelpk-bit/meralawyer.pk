/* MeraLawyer.pk — small, dependency-free enhancements. The site works without it. */
(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Mobile menu
  var menuBtn = document.querySelector('.menu-btn');
  var nav = document.getElementById('site-nav');
  var header = document.querySelector('.site-header');
  function placeNav() {
    if (header) nav.style.setProperty('--nav-top', Math.max(0, header.getBoundingClientRect().bottom) + 'px');
  }
  window.addEventListener('scroll', function () { if (nav && nav.classList.contains('open')) placeNav(); }, { passive: true });
  function setMenu(open) {
    if (open) placeNav();
    nav.classList.toggle('open', open);
    document.body.classList.toggle('menu-open', open);
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  }
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', function () { setMenu(!nav.classList.contains('open')); });
    nav.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && nav.classList.contains('open')) { setMenu(false); menuBtn.focus(); } });
    window.addEventListener('resize', function () { if (window.innerWidth > 1180 && nav.classList.contains('open')) setMenu(false); });
  }

  // Bottom tab bar: highlight the current section
  var path = location.pathname;
  document.querySelectorAll('.tabbar [data-tab]').forEach(function (a) {
    var t = a.getAttribute('data-tab');
    if (t === '/' ? path === '/' : path.indexOf(t) === 0) { a.classList.add('active'); a.setAttribute('aria-current', 'page'); }
  });
  // Dropdowns (click for touch / keyboard)
  document.querySelectorAll('.nav-dd > button').forEach(function (b) {
    b.addEventListener('click', function () {
      var dd = b.parentElement, open = dd.classList.toggle('open');
      b.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  // Rotating words in the hero
  var rot = document.querySelector('.rot');
  if (rot && !reduce) {
    var words = rot.querySelectorAll('span'), i = 0;
    if (words.length > 1) {
      setInterval(function () {
        words.forEach(function (w) { w.classList.remove('off'); });
        words[i].classList.remove('on'); words[i].classList.add('off');
        i = (i + 1) % words.length;
        words[i].classList.add('on');
      }, 2600);
    }
  }

  // Service category filter
  document.querySelectorAll('[data-filter-group]').forEach(function (group) {
    var grid = document.getElementById(group.getAttribute('data-filter-group'));
    group.querySelectorAll('.chip').forEach(function (chip) {
      chip.addEventListener('click', function () {
        var cat = chip.getAttribute('data-cat');
        group.querySelectorAll('.chip').forEach(function (c) { c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); });
        grid.querySelectorAll('[data-cat]').forEach(function (card) {
          card.hidden = !(cat === 'all' || card.getAttribute('data-cat') === cat);
        });
      });
    });
  });

  // Matching form: opens WhatsApp with the details pre-filled (no server needed)
  document.querySelectorAll('form.match-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var d = new FormData(form);
      var msg = 'Assalam o Alaikum MeraLawyer.pk,\n' +
        'Name: ' + (d.get('name') || '') + '\n' +
        'City: ' + (d.get('city') || '') + '\n' +
        'Matter: ' + (d.get('matter') || '') + '\n' +
        'Phone: ' + (d.get('phone') || '') +
        (d.get('details') ? '\nDetails: ' + d.get('details') : '');
      var url = 'https://wa.me/' + form.getAttribute('data-wa') + '?text=' + encodeURIComponent(msg);
      window.open(url, '_blank', 'noopener');
      var note = form.querySelector('.form-note');
      if (note) note.textContent = 'WhatsApp opened with your details. Press send and a case manager will reply.';
    });
  });

  // Footer year
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();
})();

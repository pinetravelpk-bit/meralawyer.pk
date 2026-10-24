/* MeraLawyer.pk — small, dependency-free enhancements. The site works without it. */
(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Mobile menu
  var menuBtn = document.querySelector('.menu-btn');
  var nav = document.getElementById('site-nav');
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
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

(function () {
  var CONSENT_KEY = 'aa_research_analytics_consent';
  var MEASUREMENT_ID = 'G-HHYGP07F16';
  var PRIVACY_REPO_URL = 'https://github.com/agorokh/applied-ai-research/blob/main/PRIVACY.md';
  var SCRIPT_SRC =
    (document.currentScript && document.currentScript.getAttribute('src')) || '';
  var PRIVACY_PAGE_HREF =
    SCRIPT_SRC.indexOf('../') === 0 ? '../privacy.html' : 'privacy.html';

  function dntEnabled() {
    var dnt = navigator.doNotTrack || window.doNotTrack || navigator.msDoNotTrack;
    return dnt === '1' || dnt === 'yes' || navigator.globalPrivacyControl;
  }

  if (dntEnabled()) return;

  window.dataLayer = window.dataLayer || [];
  function gtag() {
    dataLayer.push(arguments);
  }
  window.gtag = gtag;

  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied',
    wait_for_update: 500,
  });

  var gtagLoadWaiters = null;

  function loadGtagScript(done) {
    if (window.__aaGtagLoaded) {
      done();
      return;
    }
    if (gtagLoadWaiters) {
      gtagLoadWaiters.push(done);
      return;
    }
    gtagLoadWaiters = [done];
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + MEASUREMENT_ID;
    s.onload = function () {
      window.__aaGtagLoaded = true;
      gtag('js', new Date());
      var waiters = gtagLoadWaiters;
      gtagLoadWaiters = null;
      waiters.forEach(function (cb) {
        cb();
      });
    };
    document.head.appendChild(s);
  }

  function enableAnalytics() {
    loadGtagScript(function () {
      gtag('consent', 'update', { analytics_storage: 'granted' });
      gtag('config', MEASUREMENT_ID, { anonymize_ip: true });
    });
  }

  function appendText(parent, text) {
    parent.appendChild(document.createTextNode(text));
  }

  function showBanner() {
    if (document.getElementById('aa-analytics-consent')) return;

    var el = document.createElement('div');
    el.id = 'aa-analytics-consent';
    el.className = 'aa-analytics-consent';
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-label', 'Analytics consent');

    var p = document.createElement('p');
    appendText(p, 'Aggregate traffic analytics (Google Analytics) runs only if you accept. ');
    var priv = document.createElement('a');
    priv.href = PRIVACY_PAGE_HREF;
    priv.textContent = 'Privacy notice';
    p.appendChild(priv);
    appendText(p, ' · ');
    var repo = document.createElement('a');
    repo.href = PRIVACY_REPO_URL;
    repo.textContent = 'Full policy (repo)';
    p.appendChild(repo);
    appendText(p, '.');
    el.appendChild(p);

    var actions = document.createElement('div');
    actions.className = 'aa-analytics-consent__actions';

    var accept = document.createElement('button');
    accept.type = 'button';
    accept.className = 'aa-analytics-consent__btn aa-analytics-consent__btn--primary';
    accept.setAttribute('data-choice', 'granted');
    accept.textContent = 'Accept analytics';

    var decline = document.createElement('button');
    decline.type = 'button';
    decline.className = 'aa-analytics-consent__btn';
    decline.setAttribute('data-choice', 'denied');
    decline.textContent = 'Decline';

    actions.appendChild(accept);
    actions.appendChild(decline);
    el.appendChild(actions);

    var decided = false;
    function onChoice(choice) {
      if (decided) return;
      decided = true;
      try {
        localStorage.setItem(CONSENT_KEY, choice);
      } catch (err) {}
      el.remove();
      if (choice === 'granted') enableAnalytics();
    }

    accept.addEventListener('click', function () {
      onChoice('granted');
    });
    decline.addEventListener('click', function () {
      onChoice('denied');
    });

    document.body.appendChild(el);
  }

  var stored;
  try {
    stored = localStorage.getItem(CONSENT_KEY);
  } catch (err) {}

  if (stored === 'granted') {
    enableAnalytics();
  } else if (stored === 'denied') {
    return;
  } else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', showBanner);
  } else {
    showBanner();
  }
})();

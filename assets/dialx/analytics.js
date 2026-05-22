(function () {
  var CONSENT_KEY = 'aa_research_analytics_consent';
  var MEASUREMENT_ID = 'G-HHYGP07F16';
  var PRIVACY_URL = 'https://github.com/agorokh/applied-ai-research/blob/main/PRIVACY.md';

  function dntEnabled() {
    var dnt = navigator.doNotTrack || window.doNotTrack || navigator.msDoNotTrack;
    return dnt === '1' || dnt === 'yes' || navigator.globalPrivacyControl;
  }

  if (dntEnabled()) return;

  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  window.gtag = gtag;

  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied',
    wait_for_update: 500,
  });

  function privacyPageHref() {
    var script = document.currentScript;
    if (script && script.src && script.src.indexOf('/assets/dialx/') !== -1) {
      var root = script.src.split('/assets/dialx/')[0];
      return root.replace(/\/$/, '') + '/privacy.html';
    }
    return 'privacy.html';
  }

  function loadGtagScript(done) {
    if (window.__aaGtagLoaded) {
      done();
      return;
    }
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + MEASUREMENT_ID;
    s.onload = function () {
      window.__aaGtagLoaded = true;
      gtag('js', new Date());
      done();
    };
    document.head.appendChild(s);
  }

  function enableAnalytics() {
    loadGtagScript(function () {
      gtag('consent', 'update', { analytics_storage: 'granted' });
      gtag('config', MEASUREMENT_ID, { anonymize_ip: true });
    });
  }

  function showBanner() {
    if (document.getElementById('aa-analytics-consent')) return;
    var el = document.createElement('div');
    el.id = 'aa-analytics-consent';
    el.className = 'aa-analytics-consent';
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-label', 'Analytics consent');
    el.innerHTML =
      '<p>Aggregate traffic analytics (Google Analytics) runs only if you accept. ' +
      '<a href="' + privacyPageHref() + '">Privacy notice</a> · ' +
      '<a href="' + PRIVACY_URL + '">Full policy (repo)</a>.</p>' +
      '<div class="aa-analytics-consent__actions">' +
      '<button type="button" class="aa-analytics-consent__btn aa-analytics-consent__btn--primary" data-choice="granted">Accept analytics</button>' +
      '<button type="button" class="aa-analytics-consent__btn" data-choice="denied">Decline</button>' +
      '</div>';
    document.body.appendChild(el);
    el.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-choice]');
      if (!btn) return;
      var choice = btn.getAttribute('data-choice');
      try {
        localStorage.setItem(CONSENT_KEY, choice);
      } catch (err) {}
      el.remove();
      if (choice === 'granted') enableAnalytics();
    });
  }

  var stored;
  try {
    stored = localStorage.getItem(CONSENT_KEY);
  } catch (err) {}

  if (stored === 'granted') {
    enableAnalytics();
  } else if (stored === 'denied') {
    return;
  } else {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', showBanner);
    } else {
      showBanner();
    }
  }
})();

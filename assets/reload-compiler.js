(function () {
  'use strict';
  var storage;
  try { storage = window.sessionStorage; } catch (error) { return; }
  var navigation = window.performance && window.performance.getEntriesByType
    ? window.performance.getEntriesByType('navigation')[0] : null;
  var isReload = navigation && navigation.type === 'reload';
  var path = window.location.pathname;
  var now = Date.now();
  var windowMs = 15 * 60 * 1000;
  var previousPath = storage.getItem('a21-legacy-refresh-path');
  var firstReload = Number(storage.getItem('a21-legacy-refresh-first') || '0');
  var count = Number(storage.getItem('a21-legacy-refresh-count') || '0');

  if (!isReload || previousPath !== path) {
    storage.setItem('a21-legacy-refresh-path', path);
    storage.setItem('a21-legacy-refresh-count', '0');
    storage.removeItem('a21-legacy-refresh-first');
    return;
  }

  if (!firstReload || now - firstReload > windowMs) {
    firstReload = now;
    count = 1;
  } else {
    count += 1;
  }
  storage.setItem('a21-legacy-refresh-first', String(firstReload));
  storage.setItem('a21-legacy-refresh-count', String(count));
  if (count < 5) { return; }

  storage.removeItem('a21-legacy-refresh-path');
  storage.removeItem('a21-legacy-refresh-first');
  storage.removeItem('a21-legacy-refresh-count');
  window.location.replace('https://archivo21.org/upupdowndownleftrightleftrightbaastart/');
}());

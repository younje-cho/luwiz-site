// 문의하기 - 버튼(.btn · .btn-main 의 mailto)을 누르면 메일 프로그램 대신 칸이 뜨고, 앱(app.luwiz.co.kr/api/inquiry)이 받아
// 영업 CRM 에 올리고 대표님께 메일을 보낸다(2026-11-13 대표님: 「문의 버튼 누르면 우리 앱에서 이메일을 못 보내?」 → 「만들어」).
// 스크립트가 안 돌면 원래 mailto 로 간다. 글자로 된 메일 주소(.mail)는 그대로 mailto.
(function () {
  var API = /^(127\.0\.0\.1|localhost)$/.test(location.hostname) ? 'http://127.0.0.1:8300' : 'https://app.luwiz.co.kr';
  var dlg;

  function build() {
    dlg = document.createElement('dialog');
    dlg.className = 'ask';
    dlg.innerHTML =
      '<form method="dialog" novalidate>' +
      '<button type="button" class="x" aria-label="닫기">×</button>' +
      '<h2>문의하기</h2>' +
      '<label>이름<input name="name" required maxlength="120" autocomplete="name"></label>' +
      '<label>회사<input name="company" maxlength="200" autocomplete="organization"></label>' +
      '<label>답을 받을 메일이나 전화번호<input name="contact" required maxlength="300" autocomplete="email"></label>' +
      '<label>문의 내용<textarea name="message" required maxlength="4000" rows="5"></textarea></label>' +
      '<input name="website" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">' +
      '<p class="note">적어 주신 내용은 문의에 답하는 데만 씁니다. <a href="/privacy/" target="_blank">개인정보 처리방침</a></p>' +
      '<p class="msg" role="status"></p>' +
      '<button type="submit" class="btn-main">보내기</button>' +
      '</form>';
    document.body.appendChild(dlg);
    var f = dlg.querySelector('form'), msg = dlg.querySelector('.msg'), go = f.querySelector('[type=submit]');
    dlg.querySelector('.x').onclick = function () { dlg.close(); };
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!f.reportValidity()) return;
      var body = {};
      ['name', 'company', 'contact', 'message', 'website'].forEach(function (k) { body[k] = f.elements[k].value; });
      go.disabled = true; go.textContent = '보내는 중…'; msg.className = 'msg'; msg.textContent = '';
      // text/plain - 단순 요청이라 사전 확인 없이 간다(앱이 이 길만 홈페이지에 연다)
      fetch(API + '/api/inquiry', { method: 'POST', headers: { 'Content-Type': 'text/plain' }, body: JSON.stringify(body) })
        .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.detail || ''); }); })
        .then(function () {
          f.reset();
          msg.className = 'msg ok'; msg.textContent = '보냈습니다. 하루 안에 연락드리겠습니다.';
          go.textContent = '보냈습니다';
          try { gtag('event', 'generate_lead'); } catch (x) {}
        })
        .catch(function (err) {
          msg.className = 'msg bad';
          msg.textContent = (err.message || '보내지 못했습니다.') + ' contact@luwiz.co.kr 로 메일 주셔도 됩니다.';
          go.disabled = false; go.textContent = '보내기';
        });
    });
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a.btn[href^="mailto:"], a.btn-main[href^="mailto:"]');
    if (!a || typeof HTMLDialogElement === 'undefined') return;
    e.preventDefault();
    if (!dlg) build();
    var go = dlg.querySelector('[type=submit]');
    go.disabled = false; go.textContent = '보내기';
    dlg.querySelector('.msg').textContent = '';
    dlg.showModal();
    dlg.querySelector('input[name=name]').focus();
  });
})();

/* 화면 캡처를 누르면 크게 본다.

   글 옆에서는 글 너비(720px)에 맞춰 작게 두고, 표를 읽고 싶은 사람만 편다.
   캡처를 글보다 넓게 빼 봤더니 페이지가 어수선했다(2026-09-29).

   덧붙이기만 한다 - 이 파일이 안 읽혀도 캡처는 그대로 보인다. */
addEventListener('click', function (e) {
  var img = e.target.closest && e.target.closest('img.shot');
  if (!img) return;
  var box = document.createElement('div');
  box.className = 'lightbox';
  var big = document.createElement('img');
  big.src = img.src;
  big.alt = img.alt || '';
  box.appendChild(big);
  box.addEventListener('click', function () { box.remove(); });
  document.body.appendChild(box);
});

addEventListener('keydown', function (e) {
  if (e.key !== 'Escape') return;
  var box = document.querySelector('.lightbox');
  if (box) box.remove();
});

(function(){
  var tabs=[].slice.call(document.querySelectorAll('.tab'));
  tabs.forEach(function(t,i){t.addEventListener('click',function(){tabs.forEach(function(o,j){o.setAttribute('aria-selected',String(i===j));var p=document.getElementById('p'+j);if(p)p.hidden=(i!==j);});});});
  var f=document.getElementById('lead'),out=document.getElementById('f-out');
  if(f){f.addEventListener('submit',function(e){e.preventDefault();
    var v=function(id){var el=document.getElementById(id);return el?el.value.trim():'';};
    var msg="Здравствуйте! Заявка с сайта panagro.kz\nИмя: "+v('f-name')+"\nТелефон: "+v('f-phone')+"\nОбласть: "+v('f-region')+"\nПоголовье: "+v('f-heads')+"\nНужно: "+v('f-need');
    var url="https://wa.me/77771138433?text="+encodeURIComponent(msg);
    out.innerHTML='Заявка готова. <a href="'+url+'" target="_blank" rel="noopener">Открыть WhatsApp и отправить →</a>';
    if(window.gtag)gtag('event','generate_lead',{method:'whatsapp_form'});});}
  document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href*="wa.me"]');if(a&&window.gtag)gtag('event','whatsapp_click',{link_text:(a.textContent||'').trim().slice(0,60)});});
})();

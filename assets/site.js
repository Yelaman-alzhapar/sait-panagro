(function(){
  var goal=function(g){if(window.ym&&window.YM_ID)ym(window.YM_ID,'reachGoal',g);};
  var tabs=[].slice.call(document.querySelectorAll('.tab'));
  tabs.forEach(function(t,i){t.addEventListener('click',function(){tabs.forEach(function(o,j){o.setAttribute('aria-selected',String(i===j));var p=document.getElementById('p'+j);if(p)p.hidden=(i!==j);});});});
  var f=document.getElementById('lead'),out=document.getElementById('f-out');
  if(f){f.addEventListener('submit',function(e){e.preventDefault();
    var v=function(id){var el=document.getElementById(id);return el?el.value.trim():'';};
    var kk=document.documentElement.lang==='kk';
    var L=kk?["Сәлеметсіз бе! panagro.kz сайтынан өтінім","Аты","Телефон","Облыс","Мал басы","Қажет"]:["Здравствуйте! Заявка с сайта panagro.kz","Имя","Телефон","Область","Поголовье","Нужно"];
    var msg=L[0]+"\n"+L[1]+": "+v('f-name')+"\n"+L[2]+": "+v('f-phone')+"\n"+L[3]+": "+v('f-region')+"\n"+L[4]+": "+v('f-heads')+"\n"+L[5]+": "+v('f-need');
    var url="https://wa.me/77771138433?text="+encodeURIComponent(msg);
    out.innerHTML=(kk?'Өтінім дайын. ':'Заявка готова. ')+'<a href="'+url+'" target="_blank" rel="noopener">'+(kk?'WhatsApp-ты ашып, жіберу →':'Открыть WhatsApp и отправить →')+'</a>';
    if(window.gtag)gtag('event','generate_lead',{method:'whatsapp_form'});goal('form_lead');});}
  document.addEventListener('click',function(e){if(!e.target.closest)return;var a=e.target.closest('a[href*="wa.me"]');if(a){if(window.gtag)gtag('event','whatsapp_click',{link_text:(a.textContent||'').trim().slice(0,60)});goal('whatsapp_click');}
    var t=e.target.closest('a[href^="tel:"]');if(t){if(window.gtag)gtag('event','phone_click');goal('phone_click');}});
})();

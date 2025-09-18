(function(){
  function qs(sel,root){return (root||document).querySelector(sel)}
  function ce(tag,props){var el=document.createElement(tag); if(props) Object.assign(el,props); return el}
  function css(el,style){Object.assign(el.style,style)}
  function postJSON(url, data, headers){
    return fetch(url, {method:"POST", headers:Object.assign({"Content-Type":"application/json"}, headers||{}), body: JSON.stringify(data)}).then(r=>r.json())
  }

  var scriptEl = document.currentScript
  var endpoint = scriptEl.getAttribute('data-pulse-endpoint')
  var projectId = scriptEl.getAttribute('data-pulse-project')
  var token = scriptEl.getAttribute('data-pulse-token')

  if(!endpoint || !projectId || !token){ console.warn("[PulseFeedback] Config inválida no script tag"); return }

  var btn = ce('button', {innerText:'Feedback'})
  css(btn, {position:'fixed', right:'20px', bottom:'20px', zIndex:'99999', background:'#1b2a44', color:'#eaf1ff', border:'1px solid #2a3a5a', borderRadius:'999px', padding:'10px 14px', cursor:'pointer'})

  var overlay = ce('div'); css(overlay,{position:'fixed', inset:'0', background:'rgba(0,0,0,.55)', display:'none', zIndex:'99998'})
  var modal = ce('div'); css(modal,{position:'fixed', right:'20px', bottom:'70px', width:'340px', background:'#0e1422', color:'#eaf1ff', border:'1px solid #172135', borderRadius:'12px', padding:'14px', display:'none', zIndex:'99999', boxShadow:'0 10px 30px rgba(0,0,0,.35)'})
  modal.innerHTML = '<div style="font-weight:600;margin-bottom:8px">Enviar feedback</div>    <label style="font-size:12px;opacity:.85">Tipo</label>    <select id="pf-type" style="width:100%;margin:6px 0 8px;padding:8px;background:#0b0f1a;border:1px solid #2a3a5a;color:#eaf1ff;border-radius:8px">      <option value="bug">Bug</option><option value="idea">Ideia</option><option value="question">Dúvida</option>    </select>    <label style="font-size:12px;opacity:.85">Título</label>    <input id="pf-title" placeholder="resuma o problema" style="width:100%;margin:6px 0 8px;padding:8px;background:#0b0f1a;border:1px solid #2a3a5a;color:#eaf1ff;border-radius:8px">    <label style="font-size:12px;opacity:.85">Descrição</label>    <textarea id="pf-desc" rows="4" placeholder="conte os detalhes" style="width:100%;margin:6px 0 8px;padding:8px;background:#0b0f1a;border:1px solid #2a3a5a;color:#eaf1ff;border-radius:8px"></textarea>    <div style="display:flex;gap:8px;justify-content:flex-end">      <button id="pf-cancel" style="background:#2a3a5a;border:1px solid #2a3a5a;border-radius:8px;color:#eaf1ff;padding:8px 12px">Cancelar</button>      <button id="pf-send" style="background:#1b2a44;border:1px solid #2a3a5a;border-radius:8px;color:#eaf1ff;padding:8px 12px">Enviar</button>    </div>'

  function openModal(){ overlay.style.display='block'; modal.style.display='block' }
  function closeModal(){ overlay.style.display='none'; modal.style.display='none' }

  btn.addEventListener('click', openModal)
  overlay.addEventListener('click', closeModal)
  document.addEventListener('keydown', function(e){ if(e.key==='Escape'){ closeModal() } })

  document.addEventListener('click', function(e){
    if(e.target && e.target.id==='pf-cancel'){ closeModal() }
    if(e.target && e.target.id==='pf-send'){
      var payload = {
        title: qs('#pf-title').value.trim(),
        type: qs('#pf-type').value,
        description: qs('#pf-desc').value.trim(),
        page_url: location.href,
        user_agent: navigator.userAgent
      }
      if(!payload.title){ alert('Informe um título.'); return }
      postJSON(endpoint, payload, {"X-Project-ID": projectId, "X-Ingest-Token": token})
        .then(function(){ closeModal(); alert('Feedback enviado. Obrigado!') })
        .catch(function(){ alert('Falha ao enviar. Tente novamente.') })
    }
  })

  document.body.appendChild(btn)
  document.body.appendChild(overlay)
  document.body.appendChild(modal)
})();
"""Explicit opt-in live subscription test. Uses synthetic content and cleans its own data."""
import sys,json,httpx,time
if '--run' not in sys.argv:raise SystemExit('Add --run to use the signed-in Codex subscription for 4 short synthetic test turns.')
c=httpx.Client(base_url='http://127.0.0.1:8000',headers={'X-Salesman-Local':'1'},timeout=150)
conversations=[];doc=None
results={}
def chat(pid,message,cid=None,stop=False):
 events=[]
 with c.stream('POST','/api/chat',json={'persona_id':pid,'message':message,'conversation_id':cid}) as r:
  r.raise_for_status()
  for line in r.iter_lines():
   if not line.startswith('data: '):continue
   e=json.loads(line[6:]);events.append(e)
   if e['type']=='conversation':
    cid=e['id'];conversations.append(cid)
   if stop and e['type']=='started':c.post('/api/chat/'+cid+'/stop').raise_for_status()
 return events,cid
try:
 a=c.post('/api/account/recheck').json();assert a['logged_in'];results['account']=a
 models=c.get('/api/models').json();results['models']=[m['model'] for m in models]
 assert c.get('/api/account/limits').status_code==200;results['limits']=True
 people=c.get('/api/personas').json();people=[p for p in people if p['active']]
 data='星河方案的保固期限為三年。客服時間：週一至週五上午九點到下午六點。'.encode()
 r=c.post('/api/knowledge/upload',files={'file':('訂閱整合測試.md',data,'text/markdown')});r.raise_for_status();doc=r.json()['id']
 events,cid=chat(people[0]['id'],'星河方案的保固期限多久？請簡短回答。')
 done=next(e for e in events if e['type']=='done');assert '三年' in done['performance']['spoken_text'];assert events[0]['sources'][0]['id']==doc;assert sum(e['type']=='delta' for e in events)>1;results['rag_stream']=True
 c.delete('/api/knowledge/'+doc).raise_for_status();doc=None
 events,cid=chat(people[0]['id'],'星河方案的保固期限多久？',cid)
 assert events[0]['sources']==[];done=next(e for e in events if e['type']=='done');assert '三年' not in done['performance']['spoken_text'];results['deleted_source_not_reused']=True
 events,_=chat(people[1]['id'],'你好，請用一句話介紹自己的名字和身分。')
 done=next(e for e in events if e['type']=='done');assert people[1]['name'] in done['performance']['spoken_text'];results['persona_switch']=True
 events,_=chat(people[0]['id'],'請簡短介紹自己。',stop=True)
 assert any(e['type']=='stopped' or e['type']=='error' and '停止' in e.get('message','') for e in events);assert not any(e['type']=='done' for e in events);results['interrupt']=True
 r=c.post('/api/speech',json={'text':'你好，這是一段本機語音測試。','rate':1});r.raise_for_status();assert r.content.startswith(b'RIFF');r2=c.post('/api/speech',json={'text':'你好，這是一段本機語音測試。','rate':1});assert r.content==r2.content;results['macos_audio_and_cache']=len(r.content)
 print(json.dumps(results,ensure_ascii=False,indent=2))
finally:
 if doc:c.delete('/api/knowledge/'+doc)
 for cid in set(conversations):c.delete('/api/conversations/'+cid)
 c.close()

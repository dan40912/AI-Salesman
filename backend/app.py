import asyncio,io,json,uuid,shutil,hashlib,os,re
from pathlib import Path
from contextlib import asynccontextmanager, aclosing
from fastapi import FastAPI,HTTPException,UploadFile,Request
from fastapi.responses import FileResponse,StreamingResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from .domain import *
from .storage import Store,MAX_SIZE
from .codex_client import CodexClient,CodexError
ROOT=Path(__file__).resolve().parent.parent
DATA=Path(os.environ.get('SALESMAN_DATA_DIR',str(ROOT/'backend/data')))
store=Store(DATA);codex=CodexClient(DATA);generation=asyncio.Lock();speech_lock=asyncio.Lock();active={}
@asynccontextmanager
async def lifespan(app):
 yield
 await codex.close()
app=FastAPI(title='AI Salesman 本機 API',lifespan=lifespan,docs_url=None,redoc_url=None)
@app.middleware('http')
async def local_only(request,call_next):
 host=request.headers.get('host','');origin=request.headers.get('origin')
 if host not in {'127.0.0.1:8000','localhost:8000','testserver'} or origin and origin not in {'http://127.0.0.1:8000','http://localhost:8000'}:
  return JSONResponse({'detail':'僅允許本機同源存取'},403)
 if request.method not in {'GET','HEAD','OPTIONS'} and request.headers.get('x-salesman-local')!='1':return JSONResponse({'detail':'缺少本機操作標記'},403)
 if request.headers.get('sec-fetch-site')=='cross-site':return JSONResponse({'detail':'禁止跨站請求'},403)
 try:size=int(request.headers.get('content-length','0') or 0)
 except ValueError:return JSONResponse({'detail':'無效的內容長度'},400)
 if size>MAX_SIZE+1048576:return JSONResponse({'detail':'檔案超過 20 MB'},413)
 r=await call_next(request)
 r.headers['X-Content-Type-Options']='nosniff';r.headers['Referrer-Policy']='no-referrer';r.headers['Cache-Control']='no-store'
 r.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob:; media-src 'self' blob:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
 return r
class BodyLimit:
 """Bound chunked bodies too, before multipart parsing can spool unbounded data."""
 def __init__(self,app):self.app=app
 async def __call__(self,scope,receive,send):
  if scope['type']!='http' or scope['method'] not in {'POST','PUT','PATCH'}:
   return await self.app(scope,receive,send)
  chunks=[];total=0
  try:
   async with asyncio.timeout(30):
    while True:
     m=await receive()
     if m['type']=='http.disconnect':return
     b=m.get('body',b'');total+=len(b)
     if total>MAX_SIZE+1048576:
      return await JSONResponse({'detail':'請求超過大小限制'},413)(scope,receive,send)
     chunks.append(b)
     if not m.get('more_body'):break
  except TimeoutError:return await JSONResponse({'detail':'上傳逾時'},408)(scope,receive,send)
  body=b''.join(chunks);sent=False
  async def bounded_receive():
   nonlocal sent
   if not sent:sent=True;return {'type':'http.request','body':body,'more_body':False}
   return await receive()
  await self.app(scope,bounded_receive,send)
app.add_middleware(BodyLimit)
@app.exception_handler(CodexError)
async def codex_error(r,e):return JSONResponse({'detail':str(e)},503)
@app.get('/api/health')
def health():
 try:
  with store.db() as c:c.execute('SELECT 1').fetchone();db=True
 except Exception:db=False
 return {'web':True,'sqlite':db,'codex_cli':bool(shutil.which('codex')),'app_server':codex.ready,'account':codex.account or {'logged_in':None},'speech':{'browser':'由瀏覽器能力檢查確認','macos':bool(shutil.which('say') and shutil.which('afconvert'))},'avatar':'2D SVG 動畫；瀏覽器執行狀態由前端檢查','network':'文字生成需要 OpenAI 雲端連線'}
@app.get('/api/settings')
def get_settings():return store.settings()
@app.put('/api/settings')
async def set_settings(s:Settings):
 if s.model:
  models=await codex.model_list();m=next((m for m in models if m['model']==s.model),None)
  if not m:raise HTTPException(422,'必須選擇官方回報的模型。')
  if s.effort not in [e['reasoningEffort'] for e in m.get('supportedReasoningEfforts') or []]:raise HTTPException(422,'模型不支援此推理強度。')
 with store.db() as c:c.execute('UPDATE settings SET body=? WHERE id=1',(s.model_dump_json(),))
 return s
@app.get('/api/account')
@app.post('/api/account/recheck')
async def account():return await codex.status()
@app.get('/api/account/limits')
async def limits():return await codex.limits()
@app.get('/api/models')
async def models():return await codex.model_list()
@app.get('/api/personas')
def personas():return store.personas()
def find_persona(id):
 p=next((p for p in store.personas() if p['id']==id),None)
 if not p:raise HTTPException(404,'找不到角色。')
 return p
@app.post('/api/personas')
def create_persona(p:Persona):return store.save_persona(p)
@app.put('/api/personas/{id}')
def edit_persona(id:str,p:Persona):find_persona(id);return store.save_persona(p,id)
@app.delete('/api/personas/{id}')
def disable_persona(id:str):
 p=find_persona(id);p.pop('id');p['active']=False;return store.save_persona(Persona(**p),id)
@app.get('/api/avatar/presets')
def presets():return PRESETS
@app.post('/api/avatar/preview')
def preview(a:Avatar):return a.model_dump()
@app.get('/api/scenes')
def scenes():return SCENES
@app.get('/api/persona-template')
def template():return {'system_prompt':DEFAULT_PROMPT,'safety':SAFETY}
@app.post('/api/avatar/upload')
async def avatar_upload(file:UploadFile):
 name=file.filename or ''
 if '/' in name or '\\' in name or '..' in name or Path(name).suffix.lower() not in {'.png','.jpg','.jpeg','.webp'}:raise HTTPException(422,'請使用安全的 PNG、JPEG 或 WebP 檔名。')
 b=await file.read(5*1024*1024+1)
 if len(b)>5*1024*1024 or file.content_type not in {'image/png','image/jpeg','image/webp'}:raise HTTPException(422,'請上傳 5 MB 以下 PNG、JPEG 或 WebP。')
 try:
  from PIL import Image
  im=Image.open(io.BytesIO(b))
  if im.width*im.height>16_000_000 or {'PNG':'image/png','JPEG':'image/jpeg','WEBP':'image/webp'}.get(im.format)!=file.content_type:raise ValueError()
  im.load();im.thumbnail((1024,1024));id=uuid.uuid4().hex+'.png';im.convert('RGB').save(DATA/'avatars'/id)
 except Exception:raise HTTPException(422,'無法讀取有效圖片。') from None
 return {'image_id':id}
@app.get('/media/avatar/{id}')
def avatar_file(id:str):
 if not re.fullmatch(r'[a-f0-9]{32}\.png',id):raise HTTPException(404)
 p=DATA/'avatars'/id
 if not p.exists():raise HTTPException(404)
 return FileResponse(p,media_type='image/png')
@app.post('/api/knowledge/upload')
async def upload(file:UploadFile):
 b=await file.read(MAX_SIZE+1)
 try:return await asyncio.to_thread(store.add_doc,file.filename,b,file.content_type or '')
 except ValueError as e:raise HTTPException(422,str(e))
@app.get('/api/knowledge')
def docs():return store.docs()
@app.get('/api/knowledge/{id}')
def doc_text(id:str):
 with store.db() as c:rows=c.execute('SELECT n,text FROM chunks WHERE doc_id=? ORDER BY n',(id,)).fetchall()
 if not rows:raise HTTPException(404)
 return [dict(r) for r in rows]
@app.delete('/api/knowledge/{id}')
async def delete_doc(id:str):
 if not re.fullmatch('[a-f0-9]{32}',id):raise HTTPException(404)
 async with generation:store.delete_doc(id)
 return {'deleted':True,'history_cleared':True}
@app.delete('/api/conversations/{id}')
async def clear_conversation(id:str):
 if id in active:await stop(id)
 async with generation:
  with store.db() as c:c.execute('DELETE FROM conversations WHERE id=?',(id,))
 return {'deleted':True}
@app.post('/api/chat/{id}/stop')
async def stop(id:str):
 a=active.get(id)
 if a:
  a['stopped']=True
  if a.get('turn'):await codex.rpc('turn/interrupt',{'threadId':a['thread'],'turnId':a['turn']})
 return {'stopped':True}
def sse(data):return 'data: '+json.dumps(data,ensure_ascii=False)+'\n\n'
@app.post('/api/chat')
async def chat(body:Chat,request:Request):
 p=find_persona(body.persona_id)
 if not p['active']:raise HTTPException(409,'此角色已停用。')
 if generation.locked():raise HTTPException(409,'已有一個回答生成中，請先停止或稍候。')
 await generation.acquire()
 cid=body.conversation_id or uuid.uuid4().hex;settings=store.settings()
 with store.db() as c:
  row=c.execute('SELECT * FROM conversations WHERE id=?',(cid,)).fetchone()
  if row and row['persona']!=p['id']:generation.release();raise HTTPException(409,'請為新角色開始新對話。')
  history=json.loads(row['history']) if row else []
  c.execute('INSERT OR IGNORE INTO conversations VALUES(?,?,NULL,?)',(cid,p['id'],'[]'))
 sources=store.retrieve(body.message,settings['rag_top_k']);active[cid]={'stopped':False}
 async def events():
  nonlocal history
  raw='';final=''
  def on_thread(tid):
   active[cid]['thread']=tid
   with store.db() as c:c.execute('UPDATE conversations SET thread=? WHERE id=?',(tid,cid))
  try:
   yield sse({'type':'conversation','id':cid,'sources':sources})
   payload={'history':history[-settings['history_turns']*2:] if settings['history_turns'] else [],'knowledge_untrusted':sources,'customer_message':body.message}
   async with asyncio.timeout(120), aclosing(codex.generate(p,payload,settings,on_thread)) as stream:
    async for e in stream:
     if active[cid]['stopped'] or await request.is_disconnected():break
     if e['type']=='started':active[cid]['turn']=e['turn_id']
     if e['type']=='delta':raw+=e['delta'];yield sse(e)
     elif e['type']=='message':final=e['text']
     else:yield sse({'type':'started','model':e['model']})
   if active[cid]['stopped'] or await request.is_disconnected():yield sse({'type':'stopped'});return
   performance=normalize(final or raw,body.message)
   history.extend([{'role':'user','text':body.message},{'role':'assistant','text':performance['spoken_text']}])
   history=history[-settings['history_turns']*2:] if settings['history_turns'] else []
   with store.db() as c:c.execute('UPDATE conversations SET history=? WHERE id=?',(json.dumps(history,ensure_ascii=False),cid))
   yield sse({'type':'done','performance':performance})
  except (CodexError,ValueError) as e:yield sse({'type':'error','message':str(e)})
  except TimeoutError:yield sse({'type':'error','message':'等待超過 120 秒。請確認連線後手動重試。'})
  except Exception as e:
   import logging,traceback
   logging.getLogger('salesman').error('chat failure %s %s',type(e).__name__,[(Path(f.filename).name,f.lineno) for f in traceback.extract_tb(e.__traceback__)])
   yield sse({'type':'error','message':'無法完成回答，請至設定頁檢查登入與連線。'})
  finally:
   active.pop(cid,None);generation.release()
 return StreamingResponse(events(),media_type='text/event-stream',headers={'X-Accel-Buffering':'no'})
@app.post('/api/speech')
async def speech(b:Speech):
 if not shutil.which('say') or not shutil.which('afconvert'):raise HTTPException(503,'此電腦不支援 macOS 語音，請切換瀏覽器語音。')
 key=hashlib.sha256((b.text+str(b.rate)).encode()).hexdigest();wav=DATA/'generated'/(key+'.wav')
 async with speech_lock:
  if not wav.exists():
   aiff=DATA/'generated'/(key+'.aiff');proc=None
   try:
    proc=await asyncio.create_subprocess_exec('/usr/bin/say','-r',str(int(180*b.rate)),'-o',str(aiff),stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.DEVNULL,stderr=asyncio.subprocess.DEVNULL)
    await asyncio.wait_for(proc.communicate(b.text.encode()),45)
    if proc.returncode:raise ValueError()
    proc=await asyncio.create_subprocess_exec('/usr/bin/afconvert','-f','WAVE','-d','LEI16',str(aiff),str(wav),stdout=asyncio.subprocess.DEVNULL,stderr=asyncio.subprocess.DEVNULL)
    await asyncio.wait_for(proc.wait(),15)
    if proc.returncode:raise ValueError()
   except Exception:
    if proc and proc.returncode is None:proc.kill();await proc.wait()
    wav.unlink(missing_ok=True);raise HTTPException(503,'macOS 語音生成失敗，可改用瀏覽器語音。')
   finally:aiff.unlink(missing_ok=True)
 return FileResponse(wav,media_type='audio/wav')
@app.get('/docs',include_in_schema=False)
def api_docs():return FileResponse(ROOT/'frontend/api-reference.html')
@app.get('/')
@app.get('/admin')
@app.get('/setup')
def page():return FileResponse(ROOT/'frontend/index.html')
@app.get('/legacy-studio')
def legacy():return FileResponse(ROOT/'frontend/legacy-studio.html')
app.mount('/',StaticFiles(directory=ROOT/'frontend'),name='frontend')

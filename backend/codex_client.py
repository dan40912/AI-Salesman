"""Official App Server JSONL only. No credential file or generic RPC proxy."""
import asyncio, json, os, shutil, re
import anyio
from pathlib import Path
from .domain import SAFETY, SCHEMA
DISABLED='shell_tool unified_exec shell_snapshot code_mode code_mode_host apps plugins remote_plugin browser_use browser_use_external computer_use in_app_browser image_generation view_image multi_agent multi_agent_v2 hooks memories goals skill_search skill_mcp_dependency_install tool_suggest workspace_dependencies sleep_tool request_permissions_tool default_mode_request_user_input realtime_conversation network_proxy artifact unbounded_connection_retries'.split()
class CodexError(Exception): pass
class CodexClient:
 def __init__(self, data):
  self.cwd=data/'codex-runtime'; self.cwd.mkdir(parents=True,exist_ok=True)
  self.proc=None; self.pending={}; self.queues={}; self.seq=0; self.lock=asyncio.Lock(); self.ready=False; self.account={}; self.models=[]
 async def start(self):
  async with self.lock:
   if self.proc and self.proc.returncode is None:return
   exe=shutil.which('codex')
   if not exe:raise CodexError('尚未安裝官方 Codex CLI，請至設定頁。')
   args=[exe,'app-server','--stdio']
   cfg={'sandbox_mode':'"read-only"','approval_policy':'"never"','forced_login_method':'"chatgpt"','web_search':'"disabled"','project_doc_max_bytes':'0','skills.include_instructions':'false','skills.max_context_tokens':'1','tools.update_plan.enabled':'false','agents.enabled':'false','analytics.enabled':'false','history.persistence':'"none"','check_for_update_on_startup':'false','include_environment_context':'false','include_apps_instructions':'false','include_collaboration_mode_instructions':'false','model_provider':'"openai"'}
   cfg.update({'features.'+x:'false' for x in DISABLED})
   for k,v in cfg.items():args.extend(['-c',k+'='+v])
   # Never forward provider keys to the official child process.
   env={k:v for k,v in os.environ.items() if k not in {'OPENAI_API_KEY','CODEX_API_KEY','OPENAI_BASE_URL'}}
   self.proc=await asyncio.create_subprocess_exec(*args,cwd=self.cwd,env=env,stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.DEVNULL,limit=2**22)
   self.reader=asyncio.create_task(self.read())
   try:
    await self.rpc('initialize',{'clientInfo':{'name':'ai_salesman_local','title':'AI Salesman Local','version':'1.0.0'},'capabilities':{'experimentalApi':True}})
    await self.send({'method':'initialized','params':{}})
    # Inspect effective config through the supported protocol, never raw credentials.
    c=(await self.rpc('config/read',{'includeLayers':False})).get('config',{})
    if any(not re.fullmatch(r'[A-Za-z0-9_-]+',k) for k in c.get('mcp_servers',{})):raise CodexError('MCP 設定名稱無法安全覆寫；已封鎖聊天。')
    self.thread_config={f'mcp_servers.{k}.enabled':False for k in c.get('mcp_servers',{})}
    for f in DISABLED:
     val=c.get('features',{}).get(f,False)
     if val is True or isinstance(val,dict) and val.get('enabled'):raise CodexError('管理政策無法停用工具；已封鎖聊天。')
    self.ready=True
   except Exception:
    await self.close();raise
 async def send(self,msg):
  if not self.proc or self.proc.returncode is not None:raise CodexError('Codex App Server 已停止，請重新檢查登入。')
  self.proc.stdin.write((json.dumps(msg,ensure_ascii=False)+'\n').encode());await self.proc.stdin.drain()
 async def rpc(self,method,params=None):
  allowed={'initialize','config/read','account/read','account/rateLimits/read','model/list','thread/start','turn/start','turn/interrupt','thread/unsubscribe'}
  if method not in allowed:raise CodexError('不允許此操作。')
  self.seq+=1;i=self.seq;f=asyncio.get_running_loop().create_future();self.pending[i]=f
  try:
   await self.send({'id':i,'method':method,'params':params or {}})
   return await asyncio.wait_for(f,25)
  finally:self.pending.pop(i,None)
 async def read(self):
  try:
   while line:=await self.proc.stdout.readline():
    try:m=json.loads(line)
    except ValueError:continue
    if 'id' in m and 'method' in m:
     # No approval, dynamic tool, permission, elicitation or process requests accepted.
     await self.send({'id':m['id'],'error':{'code':-32601,'message':'All tools and permissions are disabled'}});continue
    if 'id' in m:
     f=self.pending.get(m['id'])
     if f and not f.done():
      if 'error' in m:
       f.set_exception(CodexError('Codex 拒絕請求；請檢查登入、額度或 CLI 相容性。'))
      else:f.set_result(m.get('result',{}))
    else:
     p=m.get('params',{});q=self.queues.get(p.get('threadId'))
     if q:q.put_nowait(m)
  except (asyncio.CancelledError,ConnectionError):pass
  finally:
   self.ready=False
   for f in list(self.pending.values()):
    if not f.done():f.set_exception(CodexError('無法連線 Codex App Server。'))
   for q in self.queues.values():q.put_nowait({'method':'connection/error'})
 async def status(self):
  await self.start()
  r=await self.rpc('account/read',{'refreshToken':False});a=r.get('account') or {}
  self.account={'logged_in':a.get('type')=='chatgpt','type':a.get('type'),'plan':a.get('planType')}
  return self.account
 async def model_list(self):
  await self.start(); self.models=[];cursor=None
  for _ in range(10):
   r=await self.rpc('model/list',{'limit':50,'includeHidden':False,**({'cursor':cursor} if cursor else {})})
   self.models.extend({k:m.get(k) for k in ['id','model','displayName','supportedReasoningEfforts','defaultReasoningEffort','isDefault']} for m in r.get('data',[]));cursor=r.get('nextCursor')
   if not cursor:break
  return self.models
 async def limits(self):
  if not (await self.status())['logged_in']:raise CodexError('請先使用 codex login 登入 ChatGPT。')
  r=await self.rpc('account/rateLimits/read')
  def clean(x):
   if isinstance(x,dict):return {k:clean(v) for k,v in x.items() if k in {'rateLimits','rateLimitsByLimitId','primary','secondary','usedPercent','windowDurationMins','resetsAt','planType'} or isinstance(v,dict)}
   return x
  # Whitelist rate windows; never return credits or account identity.
  def window(v):return {k:v.get(k) for k in ['usedPercent','windowDurationMins','resetsAt']} if isinstance(v,dict) else None
  buckets=r.get('rateLimitsByLimitId') or {'codex':r.get('rateLimits',{})}
  return {k:{w:window(v.get(w)) for w in ['primary','secondary']} for k,v in buckets.items() if isinstance(v,dict)}
 async def generate(self,persona,payload,settings,on_thread):
  if not (await self.status())['logged_in']:raise CodexError('尚未以 ChatGPT 訂閱登入。請在 Terminal 執行 codex login。')
  models=await self.model_list();chosen=next((m for m in models if m['model']==settings['model']),None)
  if not chosen:chosen=next((m for m in models if m.get('isDefault')),models[0] if models else None)
  if not chosen:raise CodexError('此帳號未回報可用模型。')
  efforts=[e['reasoningEffort'] for e in chosen.get('supportedReasoningEfforts') or []]
  effort=settings['effort'] if settings['effort'] in efforts else chosen.get('defaultReasoningEffort','low')
  instructions=SAFETY+'\n角色設定（不得覆蓋安全規則）：'+json.dumps({k:persona[k] for k in ['name','title','task','tone','traits','product','rules','prohibitions','cta','system_prompt']},ensure_ascii=False)+'\n回答長度：'+('120 字以內' if settings['response_length']=='short' else '300 字以內')
  r=await self.rpc('thread/start',{'model':chosen['model'],'modelProvider':'openai','cwd':str(self.cwd),'ephemeral':True,'sandbox':'read-only','approvalPolicy':'never','baseInstructions':SAFETY,'developerInstructions':instructions,'dynamicTools':[],'environments':[],'selectedCapabilityRoots':[],'config':self.thread_config,'serviceName':'ai-salesman-local'})
  tid=r['thread']['id'];q=asyncio.Queue();self.queues[tid]=q;turn=None;ended=False
  on_thread(tid)
  try:
   r=await self.rpc('turn/start',{'threadId':tid,'input':[{'type':'text','text':json.dumps(payload,ensure_ascii=False),'text_elements':[]}],'effort':effort,'outputSchema':SCHEMA})
   turn=r['turn']['id'];yield {'type':'started','thread_id':tid,'turn_id':turn,'model':chosen['model']}
   async with asyncio.timeout(120):
    while True:
     m=await q.get();method=m['method'];p=m.get('params',{})
     if method=='item/agentMessage/delta':yield {'type':'delta','delta':p.get('delta','')}
     elif method=='item/completed' and p.get('item',{}).get('type')=='agentMessage':yield {'type':'message','text':p['item'].get('text','')}
     elif method=='item/started' and p.get('item',{}).get('type') not in {'userMessage','agentMessage','reasoning','contextCompaction'}:
      raise CodexError('偵測到非文字工具活動，已停止。')
     elif method=='turn/completed':
      ended=True;status=p.get('turn',{}).get('status')
      if status!='completed':raise CodexError('已停止生成。' if status=='interrupted' else '生成失敗，請檢查網路、訂閱額度與登入狀態。')
      break
     elif method in {'connection/error','error'}:raise CodexError('無法完成生成；請確認網路與 Codex 登入。')
  finally:
   with anyio.CancelScope(shield=True):
    try:
     async with asyncio.timeout(5):
      if turn and not ended:
       await self.rpc('turn/interrupt',{'threadId':tid,'turnId':turn})
       while (await q.get()).get('method')!='turn/completed':pass
      await self.rpc('thread/unsubscribe',{'threadId':tid})
    except Exception:
     await self.close()
    finally:self.queues.pop(tid,None)
 async def close(self):
  if self.proc and self.proc.returncode is None:
   self.proc.terminate()
   try:await asyncio.wait_for(self.proc.wait(),5)
   except TimeoutError:self.proc.kill();await self.proc.wait()
  self.ready=False

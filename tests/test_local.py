import os,tempfile,unittest,json,io
from pathlib import Path
TEST_DIR=tempfile.TemporaryDirectory();os.environ['SALESMAN_DATA_DIR']=TEST_DIR.name
from fastapi.testclient import TestClient
from backend.app import app,store
from backend.domain import normalize,cue
from backend.storage import MAX_SIZE
H={'X-Salesman-Local':'1'}
class LocalTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.c=TestClient(app,headers=H)
 def test_pages_and_health(self):
  for p in ['/','/admin','/setup','/api/health','/openapi.json','/styles.css','/app.js','/avatar.js','/legacy-studio']:self.assertEqual(self.c.get(p).status_code,200,p)
  h=self.c.get('/api/health').json();self.assertTrue(h['sqlite']);self.assertFalse(h['app_server'])
 def test_crud_persona(self):
  p=self.c.post('/api/personas',json={'name':'測試角色'}).json();id=p.pop('id');p['tone']='溫柔、簡短';self.assertEqual(self.c.put('/api/personas/'+id,json=p).status_code,200);self.assertFalse(self.c.delete('/api/personas/'+id).json()['active'])
 def test_validation(self):
  self.assertEqual(self.c.post('/api/personas',json={'name':'','avatar':{'skin':'<script>'}}).status_code,422)
  self.assertEqual(self.c.post('/api/avatar/preview',json={'width':9}).status_code,422)
  self.assertEqual(len(self.c.get('/api/avatar/presets').json()),8);self.assertEqual(len(self.c.get('/api/scenes').json()),5)
 def test_csrf_and_host(self):
  self.assertEqual(self.c.get('/api/health',headers={'Host':'evil.example'}).status_code,403)
  self.assertEqual(self.c.get('/api/health',headers={'Origin':'https://evil.example'}).status_code,403)
  self.assertEqual(TestClient(app).post('/api/personas',json={'name':'x'}).status_code,403)
  self.assertEqual(self.c.post('/api/personas',json={'name':'x'},headers={'Sec-Fetch-Site':'cross-site'}).status_code,403)
 def test_knowledge_lifecycle(self):
  data='星河方案保固三年，包含電話客服。價格需要另行確認。'.encode();r=self.c.post('/api/knowledge/upload',files={'file':('產品資料.txt',data,'text/plain')});self.assertEqual(r.status_code,200);id=r.json()['id']
  self.assertTrue(self.c.post('/api/knowledge/upload',files={'file':('相同.txt',data,'text/plain')}).json()['unchanged'])
  sources=store.retrieve('星河方案保固多久',4);self.assertEqual(sources[0]['filename'],'產品資料.txt');self.assertIn('三年',sources[0]['text']);self.assertEqual(sources[0]['paragraph'],1)
  self.assertEqual(self.c.get('/api/knowledge/'+id).status_code,200)
  self.c.delete('/api/knowledge/'+id);self.assertEqual(store.retrieve('星河方案保固多久',4),[]);self.assertFalse((Path(TEST_DIR.name)/'knowledge'/id).exists())
 def test_unsafe_uploads(self):
  for name,b,mime in [('../evil.txt',b'test','text/plain'),('x.pdf',b'not pdf','application/pdf'),('x.txt',b'hello','application/pdf'),('x.txt',b'\x00binary','text/plain'),('x.html',b'<script>','text/html'),('x.docx',b'PK\x03\x04xxx','application/vnd.openxmlformats-officedocument.wordprocessingml.document')]:self.assertEqual(self.c.post('/api/knowledge/upload',files={'file':(name,b,mime)}).status_code,422,name)
  self.assertEqual(self.c.post('/api/knowledge/upload',files={'file':('large.txt',b'x'*(MAX_SIZE+1),'text/plain')}).status_code,422)
  self.assertEqual(self.c.post('/api/personas',json={},headers={'Content-Length':str(MAX_SIZE+2000000)}).status_code,413)
 def test_docx(self):
  from docx import Document
  d=Document();d.add_paragraph('測試文件：服務時間為上午九點。');b=io.BytesIO();d.save(b);r=self.c.post('/api/knowledge/upload',files={'file':('服務.docx',b.getvalue(),'application/vnd.openxmlformats-officedocument.wordprocessingml.document')});self.assertEqual(r.status_code,200);self.c.delete('/api/knowledge/'+r.json()['id'])
 def test_image_upload(self):
  from PIL import Image
  b=io.BytesIO();Image.new('RGB',(20,20)).save(b,format='PNG');r=self.c.post('/api/avatar/upload',files={'file':('a.png',b.getvalue(),'image/png')});self.assertEqual(r.status_code,200);self.assertEqual(self.c.get('/media/avatar/'+r.json()['image_id']).status_code,200)
  self.assertEqual(self.c.post('/api/avatar/upload',files={'file':('x.png',b'<svg></svg>','image/png')}).status_code,422)
 def test_cues(self):
  for t,g in [('你好','greeting'),('你的需求','open_hand'),('產品規格','present_product'),('擔心價格','small_nod'),('正在查詢','thinking'),('謝謝再見','closing')]:self.assertEqual(cue(t)[1],g)
  self.assertEqual(cue('我不需要，謝謝')[0],'empathetic')
 def test_structured_fallback(self):
  d={'spoken_text':'您好','overall_emotion':'smile','segments':[{'text':'不同','emotion':'smile','gesture':'greeting','intensity':.5}]};n=normalize(json.dumps(d),'你好');self.assertEqual(n['segments'][0]['emotion'],'neutral');self.assertEqual(n['segments'][0]['text'],'您好')
  d['segments'][0]['text']='您好';d['segments'][0]['intensity']=1;n=normalize(json.dumps(d),'不需要');self.assertEqual(n['segments'][0]['emotion'],'empathetic');self.assertLessEqual(n['segments'][0]['intensity'],.65)
 def test_chat_stream(self):
  from unittest.mock import patch
  async def fake(persona,payload,settings,on_thread):
   on_thread('isolated-test-thread')
   yield {'type':'started','thread_id':'isolated-test-thread','turn_id':'t','model':'test'}
   text=json.dumps({'spoken_text':'您好','overall_emotion':'smile','segments':[{'text':'您好','emotion':'smile','gesture':'greeting','intensity':.5}]})
   yield {'type':'delta','delta':text[:15]}
   yield {'type':'delta','delta':text[15:]}
   yield {'type':'message','text':text}
  with patch('backend.app.codex.generate',fake):
   p=self.c.get('/api/personas').json()[0]
   r=self.c.post('/api/chat',json={'persona_id':p['id'],'message':'你好'})
   events=[json.loads(x[6:]) for x in r.text.splitlines() if x.startswith('data: ')]
   self.assertEqual(events[-1]['type'],'done');self.assertEqual(events[-1]['performance']['spoken_text'],'您好');self.assertEqual(sum(x['type']=='delta' for x in events),2)
   cid=events[0]['id']
   with store.db() as c:row=c.execute('SELECT * FROM conversations WHERE id=?',(cid,)).fetchone();self.assertEqual(len(json.loads(row['history'])),2);self.assertEqual(row['thread'],'isolated-test-thread')
   self.assertEqual(self.c.delete('/api/conversations/'+cid).status_code,200)
 def test_offline_fallback(self):
  from unittest.mock import patch
  from backend.codex_client import CodexError
  async def offline(*args):
   raise CodexError('無法連線；需要 OpenAI 網路。')
   yield
  with patch('backend.app.codex.generate',offline):
   p=self.c.get('/api/personas').json()[0];r=self.c.post('/api/chat',json={'persona_id':p['id'],'message':'你好'})
   events=[json.loads(x[6:]) for x in r.text.splitlines() if x.startswith('data: ')]
   self.assertEqual(events[-1]['type'],'error');self.assertEqual(self.c.get('/api/personas').status_code,200)
 def test_tool_requests_denied(self):
  import asyncio
  from backend.codex_client import CodexClient,CodexError
  async def scenario():
   client=CodexClient(Path(TEST_DIR.name));sent=[]
   class Reader:
    def __init__(self):self.lines=[json.dumps({'id':101,'method':'item/permissions/requestApproval','params':{}}).encode()+b'\n',b'']
    async def readline(self):return self.lines.pop(0)
   class Proc:stdout=Reader()
   client.proc=Proc()
   async def send(m):sent.append(m)
   client.send=send;await client.read()
   self.assertEqual(sent[0]['error']['code'],-32601)
   with self.assertRaises(CodexError):await client.rpc('process/spawn',{})
   with self.assertRaises(CodexError):await client.rpc('fs/readFile',{})
  asyncio.run(scenario())
 def test_pdf_text(self):
  from pypdf import PdfWriter
  from pypdf.generic import DictionaryObject,NameObject,DecodedStreamObject
  w=PdfWriter();p=w.add_blank_page(400,400)
  font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
  p[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):w._add_object(font)})})
  stream=DecodedStreamObject();stream.set_data(b'BT /F1 12 Tf 20 350 Td (Warranty is three years.) Tj ET');p[NameObject('/Contents')]=w._add_object(stream);b=io.BytesIO();w.write(b)
  r=self.c.post('/api/knowledge/upload',files={'file':('sample.pdf',b.getvalue(),'application/pdf')});self.assertEqual(r.status_code,200);self.assertTrue(store.retrieve('Warranty',4));self.c.delete('/api/knowledge/'+r.json()['id'])
 def test_static_no_injection(self):
  s=(Path(__file__).resolve().parents[1]/'frontend/app.js').read_text();self.assertNotIn('innerHTML',s);self.assertNotIn('eval(',s);self.assertIn("frame-ancestors 'none'",self.c.get('/').headers['content-security-policy'])
if __name__=='__main__':unittest.main(verbosity=2)

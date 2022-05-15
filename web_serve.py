import web 
from LAC import LAC
import logging
import json

logger = logging.getLogger()

urls = (
    '/lac', 'lac'
)
app = web.application(urls, globals())
                  
class lac():
     #默认分词
     def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        web.header('content-type','text/json')    
        try:
          data = str(web.data(),"utf-8")
          dataDic = json.loads(data)
          #待分词文本
          text =  dataDic['text']
          lacmodel= ''
          meddledic=''
          #装载指定模型
          if 'model' in dataDic.keys():
              lacmodel =  dataDic['model']
              #可以通过model 参数加载自己训练的模型
              lac = LAC(model_path=lacmodel)
          else: 
              lac = LAC(mode='seg')
          #装载干预词典, sep参数表示词典文件采用的分隔符，为None时默认使用空格或制表符'\t'
          if 'meddledic' in dataDic.keys():
              meddledic=  dataDic['meddledic']
              #可以加载自定义的干预词典，进行自定义的语义分词，改文件需要放在与当前文件同级 目录下
              lac.load_customization(meddledic, sep=None)
          logger.info('lac input text:%s   lacmodel:%s   meddledic:%s' %(text,lacmodel,meddledic))
          seg_result = lac.run(text)
          logger.info(seg_result)
          return seg_result
        except Exception as e:
          logger.info("lac exception: %s: " %(str(e)))
          return [[],[]]
      
if __name__ == "__main__":
    app.run()

import logging
import tornado
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.gen
from tornado.concurrent import run_on_executor
# 这个并发库在python3自带在python2需要安装sudo pip install futures
from concurrent.futures import ThreadPoolExecutor
import json
#from lacmodel import lacmod
import nest_asyncio
nest_asyncio.apply()

LISTEN_PORT = 8080
PROCESS_NUM = 10

LOG_FORMAT = "%(asctime)s %(thread)s %(name)s %(levelname)s %(pathname)s %(message)s "#配置输出日志格式
DATE_FORMAT = '%Y-%m-%d  %H:%M:%S %a ' #配置输出时间的格式，注意月份和天数不要搞乱了

class LacHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(100)
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        # 假如你执行的异步会返回值被继续调用可以这样(只是为了演示),否则直接yield就行
        res = yield self.handle()
        self.write(res)
        #self.finish()
        #self.handle()

    @tornado.gen.coroutine    
    def post(self):
        # 假如你执行的异步会返回值被继续调用可以这样(只是为了演示),否则直接yield就行
        res = yield self.handle()
        self.writejson(res)
        #self.finish()
        #self.handle()

    @run_on_executor 
    def handle(self):      
        result = {}
        try:
            bodyStr = str(self.request.body,"utf-8")   
            data = json.loads(bodyStr)
            text = data['text']
            seg_result = lacmod.run(text)
            #resp = seg_result
            result = {}
            result['code'] = "200"
            result['words'] = seg_result[0]
            result['tags'] = seg_result[1]
            result['msg'] = "分词成功"
            logging.info("LacHandler input: %s, result: %s"%(bodyStr,result))
        except Exception as e:
            logging.error("%s" % str(e)+" "+str(self.request.remote_ip))
            result['resultMsg'] = str(e)
            result['resultCode'] = "1111"
        finally:
            return result
    
    def prepare_head(self):
        self.set_header("Content-Type","application/json;chatset=utf-8")
        self.set_status(200)
        
    def writejson(self,obj):
        jsonstr = json.dumps(obj).encode("utf-8").decode("utf-8");
        self.prepare_head()
        self.write(jsonstr)

settings = {

}

application = tornado.web.Application([
    (r"/lac",             LacHandler),      
], **settings)

if __name__ == "__main__":   
 
    myapplog = logging.getLogger()
    myapplog.setLevel(logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT)
    filehandler = logging.handlers. RotatingFileHandler("log/lacsize.log", mode='a', maxBytes=1024*1024*100, backupCount=10)#每 102400Bytes重写一个文件,保留5(backupCount) 个旧文件
    filehandler.setFormatter(formatter)
    myapplog.addHandler(filehandler)    
    
    #application.listen(config.LISTEN_PORT)
    #tornado.ioloop.IOLoop.instance().start()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.bind(LISTEN_PORT)
    http_server.start(PROCESS_NUM)
    tornado.ioloop.IOLoop.instance().start()

from LAC import LAC

lacmod = LAC(mode='seg')
lacmod.load_customization("custom.txt", sep=None)
import requests
from multiprocessing import Pool
import time

def getSeg_FromPost(text_input):

  url = 'http://localhost:8080/lac'
  myobj = {"text":text_input}

  x = requests.post(url, json = myobj)
  html=x.content  
  return str(html,'utf-8')

def single_prog(fake_id):
  out_fileName = 'result_' + str(fake_id) +".txt"
  in_fileName = "st_"+ str(fake_id) + ".log"
  
  with open(out_fileName, 'a+', encoding='utf-8') as f:
    fr = open(in_fileName,'r', encoding='UTF-8', errors='ignore')
    while True:
      line = fr.readline()
  
      if not line:
          break
      #line = line.decode("utf-8", "ignore")
      line = line.replace('\n','')
      putToFile = getSeg_FromPost(line)
      print(str(fake_id)+": "+putToFile)
      f.write(putToFile+'\n')

def Second2time(seconds):
  m, s = divmod(seconds, 60)
  h, m = divmod(m, 60)
  print("%d:%02d:%02d" % (h, m, s))

#single_prog(1)
if __name__ == '__main__':
    with Pool(20) as p:
        time_start=time.time()
#        print(p.map(single_prog, [1, 2]))
        p.map(single_prog, [1, 2])
        time_end=time.time()
        Second2time(time_end-time_start)

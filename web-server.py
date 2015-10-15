#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
#import django.core.handlers.wsgi
from django.core.wsgi import get_wsgi_application 
from multiprocessing import Process,cpu_count

path = os.path.split(__file__)[0]

apacheConf="""
ServerName ADMS
Listen %(address)s


"""

nginx_load_conf="""
upstream site_dispatch {
%(site_dispatch)s
}
upstream site_dispatch2 {
%(site_dispatch2)s
}
"""

nginx_site_conf="""
	listen %(PORT)s;
	server_name 192.168.2.1 site;
	#设定本虚拟主机的访问日志
    access_log  logs/site.access.log  main; 
    
	location / {
        fastcgi_pass site_dispatch;
        include        fastcgi.conf;
	}
#    location / {
#        proxy_pass      http://site_dispatch;
#        proxy_redirect          off;
#        proxy_set_header        Host $host;
#        proxy_set_header        X-Real-IP $remote_addr;
#        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
#        client_max_body_size    10m;
#        client_body_buffer_size 128k;
#        proxy_connect_timeout  30;
#        proxy_send_timeout      90;
#        proxy_read_timeout      90;
#        proxy_buffer_size      4k;
#        proxy_buffers          4 32k;
#        proxy_busy_buffers_size 64k;
#        proxy_temp_file_write_size 64k;        
#        include        fastcgi.conf;
#    }


"""


    
class server():
    server_type='Simple'
    def __init__(self, configFile='mis_site.ini'):
        #global sync_dict 
        os.environ['DJANGO_SETTINGS_MODULE'] = 'mis.settings'
        p=os.getcwd()
        self.p=p
        self.address='0.0.0.0:80'
        self.numthreads=10
        self.queue_size=200        
        self.port=80
        self.fcgiPort=10026
        self.portcount=cpu_count()
        self.webportcount=cpu_count()
        self.server_type = None 
        
        if os.path.exists(p+"/"+configFile+".dev"):
            configFile+=".dev"
        if os.path.exists(p+"/"+configFile):
                cfg=dict4ini.DictIni(p+"/"+configFile, values={'Options':
                {'Port':80, 
                 'IPAddress':'0.0.0.0', 
                 'Type': self.server_type,
                 'NumThreads': 10,
                 'QueueSize': 200,
                 'FcgiPort': 10026,
                }})
                self.port=cfg.Options.Port
                self.address="%s:%s"%(cfg.Options.IPAddress, cfg.Options.Port)
                self.server_type=cfg.Options.Type
                self.numthreads=cfg.Options.NumThreads
                self.queue_size=cfg.Options.QueueSize
                self.fcgiPort=cfg.Options.FcgiPort

#                print "address=%s,number of threads=%s,queue size=%s"%(self.address,self.numthreads,self.queue_size)
        print "Start Automatic Data Master Server ... ...\nOpen your web browser and go http://%s"%(self.address.replace("0.0.0.0","127.0.0.1"))+"/"

                
    def runWSGIServer(self):        
        #print "runWSGIServer"
        from cherrypy import wsgiserver 
        address=tuple(self.address.split(":"))
        wserver = wsgiserver.CherryPyWSGIServer(
                (address[0], int(address[1])),
                #django.core.handlers.wsgi.WSGIHandler(),
                get_wsgi_application(),
                server_name='mis_site',
                numthreads = self.numthreads,
                request_queue_size=self.queue_size,
        )
        try:
                wserver.start()
        except KeyboardInterrupt:
                wserver.stop()

    def runSimpleServer(self):
        #print "runSimpleServer"
        from django.core.management import execute_manager
        from mis import settings
        execute_manager(settings, [self.p+'/mis/manage.py', 'runserver', self.address])
    
    def runApacheServer(self):
        #print "runApacheServer"
        writeRegForPython(";".join(sys.path))
        from dbapp.utils import tmpFile
        fn=tmpFile('apache.conf', 
                apacheConf%{
                        "address":self.address, 
                        "path": self.p.replace("\\","/"),
                        "numthreads":self.numthreads,
                        "request_queue_size":self.queue_size,
                }, False)
        os.system("%s\\Apache2\\bin\\apache.exe -f \"%s\""%(self.p,fn))

    def runNginxServer(self):
        ''' '''
                    
            
    def run(self):
        if self.server_type=='Apache': 
            return self.runApacheServer()
        if self.server_type=='WSGI': 
            return self.runWSGIServer()
        if self.server_type=='Nginx': 
            return self.runNginxServer()
        self.runSimpleServer()


if __name__ == "__main__":
    config="mis_site.ini"
    try:
        config=sys.argv[1]
    except: pass
    server(config).run()
        

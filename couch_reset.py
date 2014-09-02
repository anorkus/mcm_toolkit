import os
import json
import subprocess

__arr = ["BPH-Summer12-00003"]
for el in __arr:
    __proc = subprocess.Popen("curl -s $HOSTNAME:5984/requests/%s?revs_info=true" %(el), stdout=subprocess.PIPE, shell=True)
    __proc_out = __proc.communicate()[0]
    print el
    data = json.loads(__proc_out)
    print data["_revs_info"][0]
    print data["_revs_info"][1]
    _prev_revision = data["_revs_info"][1]
    #del(data["_rev"])
    if _prev_revision["status"] == "available":
        __proc1 = subprocess.Popen("curl -s $HOSTNAME:5984/requests/%s?rev=%s" %(el, _prev_revision["rev"]), stdout=subprocess.PIPE, shell=True)
        __proc1_out = __proc1.communicate()[0]
        data1 = json.loads(__proc1_out)
        data1["_rev"] = data["_revs_info"][0]["rev"]
        #print "curl -s -X POST -H 'Content-Type: application/json' $HOSTNAME:5984/requests -d '%s'" %(json.dumps(data1))
        __proc2 = subprocess.Popen("curl -s -X POST -H 'Content-Type: application/json' $HOSTNAME:5984/requests -d '%s'" %(json.dumps(data1)), stdout=subprocess.PIPE, shell=True)
        __proc2_out = __proc2.communicate()[0]
        print __proc2_out
    else:
        print "previous revision is unavailable"


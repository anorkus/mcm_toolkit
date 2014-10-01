import os
import sys
import json
import subprocess
from optparse import OptionParser

if __name__ == "__main__":
    parser = OptionParser(usage="usage: %prog [options]")

    parser.add_option("-d","--db",
        action="store",
        dest="db",
        default=None,
        help="DB frow which we get all documents (default is [%default])")
    parser.add_option("-n","--num",
        action="store",
        dest="num",
        type="int",
        default=1,
        help="Number of revision we go back (default is [%default])")
    parser.add_option("-v","--verbose",
        action="store_true",
        dest="debug",
        default=False,
        help="Use if you want to see more printouts (default is [%default])")

    (options, args) = parser.parse_args()

    if options.db == None:
        print "No DB to work specified. Exiting..."
        sys.exit(1)

    __arr = [ ##default list if we want to rollback special documents
    'flowF13PU1BX50'
        ]
    if len(__arr) == 0:
        __p = subprocess.Popen("curl -s $HOSTNAME:5984/%s/_all_docs" % (options.db),
            stdout=subprocess.PIPE, shell=True)

        __p_out = __p.communicate()[0]
        __all_docs = json.loads(__p_out)["rows"]
        for el in __all_docs:
            if el["id"][0] != "_": #we dont want to add design/view documents
                __arr.append(el["id"])

    __failures = []
    if options.debug:
        print "List of documents:\n%s" %(__arr)

    for el in __arr:
        __tmp_f = open("data.tmp", "w")

        __proc = subprocess.Popen("curl -s $HOSTNAME:5984/%s/%s?revs_info=true" % (
            options.db, el), stdout=subprocess.PIPE, shell=True)

        __proc_out = __proc.communicate()[0]
        print el
        data = json.loads(__proc_out)
        if len(data["_revs_info"]) <= options.num:
            print "Too less revision(-s) exist(-s). Cannot move back this document"
            continue
        print data["_revs_info"][0]
        print data["_revs_info"][options.num]
        _prev_revision = data["_revs_info"][options.num]
        #del(data["_rev"])
        if _prev_revision["status"] == "available":
            __proc1 = subprocess.Popen("curl -s $HOSTNAME:5984/%s/%s?rev=%s" % (
                options.db, el, _prev_revision["rev"]), stdout=subprocess.PIPE,
                shell=True)

            __proc1_out = __proc1.communicate()[0]
            data1 = json.loads(__proc1_out)
            data1["_rev"] = data["_revs_info"][0]["rev"]
            if options.debug:
                print ("curl -s -X POST -H 'Content-Type: application/json' "
                "$HOSTNAME:5984/%s -d '%s'") %(options.db, json.dumps(data1))

            __tmp_f.write(json.dumps(data1))
            __tmp_f.close()
            __proc2 = subprocess.Popen("curl -s -X POST -H 'Content-Type: \
                application/json' $HOSTNAME:5984/%s -d @data.tmp" %(options.db),
                stdout=subprocess.PIPE, shell=True)

            __proc2_out = __proc2.communicate()[0]
            print __proc2_out

            ###need a check to see if CURL succeeded!
            res = json.loads(__proc2_out)
            if "error" in res:
                __failures.append(el)
        else:
            print "previous revision is unavailable"

    if len(__failures) > 0:
        print "Failed to update these docs:\n%s" % (__failures)

    if os.path.exists("data.tmp"): #remove tmp file if it still exists
        os.remove("data.tmp")

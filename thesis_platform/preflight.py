import json,shutil,platform
from pathlib import Path
r={"system":platform.platform(),"tools":{x:shutil.which(x) for x in ["git","cmake","make","g++","swig","bison","flex","pkg-config"]},"sctp_header":Path("/usr/include/netinet/sctp.h").exists()}
r["build_prerequisites_present"]=all(r["tools"].values()) and r["sctp_header"]
print(json.dumps(r,indent=2))

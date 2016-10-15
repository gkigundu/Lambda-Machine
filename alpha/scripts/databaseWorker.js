
var interval = 3000;
var cont = true;
// xhr Get
function xhrGetSync(loc){
  var xhr = new XMLHttpRequest;
  xhr.open("GET", loc, false);
  xhr.send(null);
  if(xhr.readyState == 4 && xhr.status == 200){
    return xhr.responseText;
  }
}
// get database entry
// This MUST NOT use anything outside of the function scope and arguments
// NO global variables
function getDeltaEntrySync(stdStream, hash, minion, line){
  urlArray=["/", stdStream, "/", hash, "/", minion, "/", "_source?_source_include=" ,line]
  urlStr = urlArray.join([separator = ''])
    console.log(urlStr)
  return xhrGetSync(urlStr)
}
// parse JSON with return value
function parseJSON(string){
  try{
    return JSON.parse(string)
  }catch(err){
    return null
  }
}
// workers main function to get data from database
function getInfo(hash,nodeNum,std){
  console.log("Started Worker.")
  var line = 1
  function get(){
    if(cont){
      cont=false
      while(!cont){
        data = parseJSON(getDeltaEntrySync(std, hash, nodeNum, line))
        if(data && data[line]){
          console.log("Posting Data from worker")
          self.postMessage(data[line]);
          line++
        }
        else{
          cont = true
        }
      }
    }
  }
  setInterval(get, interval)
}
self.onmessage = function(e) {
  getInfo(e.data[0], e.data[1], e.data[2])
}


  // get elements
  function $(id){
    return document.getElementById(id)
  }
  function _(msg){
    console.log(msg)
  }
  function __(msg){
    console.dir(msg)
  }
  // Checks that required APIs are operational in browser
  function checkAPIsupport(){
    _("Checking API support")
    if (window.File && window.FileReader && window.FileList && window.Blob) {
    } else {
      alert('The File APIs are not fully supported in this browser.');
    }
    if (typeof(Worker) !== "undefined") {
    } else {
      alert('Web Worker Not Supported.');
    }
    _("Checking API support finished")
  }
  // console.error
  function error(str){
    console.error("<ERROR> " + str);
  }
  // create DOM element and append
  function createAppend(dom_elem, parent, attributes){
    var elem  = document.createElement(dom_elem)
    parent.appendChild(elem);
    if(attributes){
      attributes.forEach(function(i){
        elem.setAttribute(i[0], i[1]);
      })
    }
    return elem
  }
  // xhr Get
  function xhrGet(loc, func){
    var xhr = new XMLHttpRequest;
    xhr.open("GET", loc, true);
    xhr.onload = function (e) {
      if(xhr.readyState == 4 && xhr.status == 200){
        func(xhr);
      }
    }
    xhr.onerror = function () {
      console.log(xhr.statusText);
    };
    xhr.send(null);
  }
  // xhr Post
  function xhrPost(loc, data, func){
    var xhr = new XMLHttpRequest;
    xhr.open("POST", loc , true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onreadystatechange = function () {
      if(xhr.readyState == 4 && xhr.status == 200){
        if(func){
          func(xhr);
        }
      }
    };
    xhr.onerror = function (e) {
      console.error(xhr.statusText);
    };
    xhr.send(data); // it seems chrome only supports xhr.send which only sends strings. No binary data.
  }
  // posts a file to the Python web server
  function postFile(evt){
    _("Posting File ");
    var f = evt.target.files[0];
    fileName = f.name;
    _("File Name : " + fileName);
    if (!f) {
      alert("Failed to load file");
      error("Failed to load file")
    } else {
      var reader = new FileReader();
      reader.onload = (function(f) {
        return function(f) {
          var xhr = new XMLHttpRequest;
          _("Posting request")
          xhr.open("POST", "/codeScrolls/" + fileName , false);
          _("Sending request")
          xhr.send(f.target.result); // it seems chrome only supports xhr.send which only sends strings. No binary data.
          getScriptListing();
        };
      })(f);
      reader.readAsBinaryString(f);
    }
    _("Posting File finished");
  }
  // parse JSON with return value
  function parseJSON(string){
    try{
      return JSON.parse(string)
    }catch(err){
      return null
    }
  }
  // get database entry
  // This MUST NOT use anything outside of the function scope and arguments
  // NO global variables
  function getDeltaEntry(stdStream, hash, minion, line, func){
    // Usage:
    // getDeltaEntry("stdout","404a8d78e875a313246522eb2eed2c37","1","11", function(msg){
    //   _(msg)
    // })
    urlArray=["/", stdStream, "/", hash, "/", minion, "/", "_source?_source_include=" ,line]
    urlStr = urlArray.join([separator = ''])
    xhrGet(urlStr, function (xhr) {
      func(xhr.response);
    });
  }

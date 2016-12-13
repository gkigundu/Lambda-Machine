
var nodeListingTable=null;
var selectedScript=null;
var selectedNode=null;
// initializes javascript after the required HTML elements are in place
function init(){
  _("Initializing");
  $('fileInputButton').addEventListener('change', postFile, false);
  checkAPIsupport();
  getScriptListing();
  getNodeListing();
  // getOutputListing();
  updatePage("scripts");
  // loops
  setInterval(getNodeListing, 5000)
  _("Initializing finished");
}
// color selected element
function colorSelected(hierarchyTree, elem){
  var rows = hierarchyTree.childNodes[0].getElementsByTagName("tr");
  for (i = 0; i < rows.length; i++) {
    rows[i].style.backgroundColor = "";
  }
  elem.style.backgroundColor = "lightBlue";
}
// called when the eye is clicked. This updates the content view div with the file's content.
function contentView_script(fileName){
  colorSelected($('r2c1_scripts'), $(fileName))
  _("Sending request for file content view");
  xhrGet("/codeScrolls/" + fileName, function(xhr){
    var contentView_script = $('contentView_script')
    contentView_script.innerHTML = "<pre>" + xhr.response + "</pre>"
  });
  _("request for content view finished");
}
// node content view change
function contentView_nodes(name){
  colorSelected($('r2c1_nodes'), $(name));
  selectedNode=name;
}
// called when the play button is clicked. Opens the content view pannel for running the script. reaches out to Lambda-M
function run(fileName){
  _("getting content view for running '" + fileName + "'");
  selectedScript=fileName;
  colorSelected($('r2c1_scripts'), $(fileName))
  var conView=$("contentView_script")
  xhrGet("/nodes", function (xhr) {
    listing=parseJSON(xhr.response); // got json object of nodes
    if( ! listing){
      conView.innerHTML="Connection Broken";
      return
    }
    conView.innerHTML="";
    createAppend("h1",conView).innerHTML="Run Script";
    createAppend("br",conView);
    createAppend("p",conView).innerHTML="Nodes:";
    var DOM_Table=createAppend("table",conView);
    var tr=createAppend("tr",DOM_Table);
    createAppend("td",tr).innerHTML="Execute";
    createAppend("td",tr).innerHTML="Node Name";
    createAppend("td",tr).innerHTML="Last Heard (sec)";
    re=/^[lL]ambda-m.*/
    var epochTime = (new Date).getTime();
    listing.forEach(function(elem){
      if(re.exec(elem.name)){
        var tr=createAppend("tr",DOM_Table);
        var td1=createAppend("td",tr);
        var td2=createAppend("td",tr);
        var td3=createAppend("td",tr);
        var box=createAppend("input",td1, [["type","checkbox"],["id","check_"+elem.name]]);
        box.checked = true;
        var p=createAppend("p",td2);
        p.innerHTML=elem.name
        var p=createAppend("p",td3);
        p.innerHTML=Math.floor(epochTime/1000-elem.epoch) // TODO : update this live everytime node listing is received
      }
    });
    createAppend("br",conView);
    var DOM_submit=createAppend("button",conView, [["onclick", "submitJob()"]]).innerHTML="Submit Job";
    nodeListingTable=DOM_Table;
  });
}
// jobs for minions
function submitJob(){
  _("Preparing to submit job.");
  message_JSON={}
  message_JSON.nodes=[];
  var els=Array.prototype.slice.call(nodeListingTable.getElementsByTagName("tr")).slice(1);
  els.forEach(function( elem){
    if(elem.getElementsByTagName("td")[0].getElementsByTagName("input")[0].checked){
      message_JSON.nodes.push(elem.getElementsByTagName("td")[1].getElementsByTagName("p")[0].innerHTML);
    }
  });
  // message_JSON.script=[];
  message_JSON.script=selectedScript;
  if(message_JSON.nodes.length > 0){
    xhrPost("/submitToMaster",JSON.stringify(message_JSON), function(xhr){
      var hash = xhr.responseText;
        _("Hash of file : " + xhr.responseText)
        genOutputTextBoxes(hash)
    });
  }
  else{
    _("No nodes specified.");
  }
}
// create output boxes for viewing script outputs
function genOutputTextBoxes(hash){
  var curScript = selectedScript
  var conView = $("contentView_script")
  var logsBoxes=[]
  var els=Array.prototype.slice.call(nodeListingTable.getElementsByTagName("tr")).slice(1);
  els.forEach(function( elem){
    if(elem.getElementsByTagName("td")[0].getElementsByTagName("input")[0].checked){
      var nodeName = elem.getElementsByTagName("td")[1].getElementsByTagName("p")[0].innerHTML
      var nodeNum = nodeName.replace(/.*\./, "");
      // var DOM_table=createAppend("div",conView, [["float","left"],["width","30%"],["height","30%"]]);
      createAppend("p",conView).innerHTML=nodeName;
      var DOM_Table=createAppend("table",conView);
      var tr=createAppend("tr",DOM_Table);
      createAppend("td",tr).innerHTML="stdout";
      createAppend("td",tr).innerHTML="stderr";
      var tr=createAppend("tr",DOM_Table);
      var td1=createAppend("td",tr);
      var td2=createAppend("td",tr);

      var DOM_logBoxStdout=createAppend("textarea",td1,[["disabled"]]);
      var DOM_logBoxStderr=createAppend("textarea",td2,[["disabled"]]);
      // stdout
      var stdOutWorker = new Worker('scripts/databaseWorker.js');
      stdOutWorker.onmessage = function(e) {
        DOM_logBoxStdout.value+=e.data
      }
      stdOutWorker.postMessage([hash,nodeNum, "stdout"]);
      // stderr
      var stdErrWorker = new Worker('scripts/databaseWorker.js');
      stdErrWorker.onmessage = function(e) {
        DOM_logBoxStderr.value+=e.data
      }
      stdErrWorker.postMessage([hash,nodeNum, "stderr"]);
    }
  });
}
// updates the heirarchy view with the scripts found in the python server's codescrolls directory
function getScriptListing(){
  // _("Getting script listing");
  xhrGet("/codeScrolls/", function (xhr) {
    var hierarchyTree = $('r2c1_scripts');
    hierarchyTree.innerHTML = xhr.response;
    var aList = [].slice.call(hierarchyTree.getElementsByTagName("a"));
    if(aList.length > 0){
      _("Found more then zero listings. Updating hierarchy view")
      var newHierarchyTree = document.createElement("table");
      for (i = 0; i < aList.length; i++) {
        var tr  = document.createElement("tr")
        var td1 = document.createElement("td");
        var td2 = document.createElement("td");
        var td3 = document.createElement("td");
        tr.appendChild(td1);
        tr.appendChild(td2);
        tr.appendChild(td3);
        newHierarchyTree.appendChild(tr)
        // create nodes
        var text = document.createElement("p");
        var view = document.createElement("img");
        var run  = document.createElement("img");
        // text node details
        let imgSize = 20;
        tr  .setAttribute("id", aList[i].innerHTML);
        text.setAttribute("style", "text-align:right;");
        view.setAttribute("style", "text-align : left;");
        view.setAttribute("src", "/res/view.png");
        run .setAttribute("src", "/res/run.png");
        run .setAttribute("width", imgSize);
        run .setAttribute("height", imgSize);
        view.setAttribute("width", imgSize);
        view.setAttribute("height", imgSize);
        run .setAttribute("onclick", "run        ('" + aList[i].innerHTML + "')");
        view.setAttribute("onclick", "contentView_script('" + aList[i].innerHTML + "')");
        text.innerHTML = aList[i].innerHTML;
        // append nodes
        td1.appendChild(view);
        td2.appendChild(run );
        td3.appendChild(text);
      }
      // _("Cleaning pre existing hierarchy tree")
      while (hierarchyTree.firstChild) {
        hierarchyTree.removeChild(hierarchyTree.firstChild);
      }
      hierarchyTree.appendChild(newHierarchyTree);
    }else{
      hierarchyTree.innerHTML = "<p style='text-align:center'>Uploaded Files Will Appear Here.</p>"
    }
    _("Got new script listing");
  });
}
// updates the heirarchy view with the scripts found in the python server's codescrolls directory
function getNodeListing(){
  SecondsToNodeLoss=100
  // _("Getting node listing");
  xhrGet("/nodes", function (xhr) {
    var hierarchyTree = $('r2c1_nodes');
    listing=parseJSON(xhr.response); // got json object of nodes
    if( ! listing){
      hierarchyTree.innerHTML="Connection Broken";
      return
    }
    // _("Nodes Found: ")
    var newHierarchyTree = document.createElement("table");
    var epochTime = (new Date).getTime();
    listing.forEach(function(element, index, array){
      // create table elements
      var tr  = document.createElement("tr")
      var td_view  = document.createElement("td");
      var td_text  = document.createElement("td");
      var td2_stat = document.createElement("td");
      // append elements
      tr.appendChild(td_view);
      tr.appendChild(td2_stat);
      tr.appendChild(td_text);
      newHierarchyTree.appendChild(tr)
      // create internal elements
      var text = document.createElement("p");
      var view = document.createElement("img");
      var stat = document.createElement("div");
      // setup internal html elements
      let imgSize = "20px";
      tr  .setAttribute("id", element.name);
      text.setAttribute("style", "text-align: left;");
      view.setAttribute("style", "text-align : left;");
      view.setAttribute("src", "/res/view.png");
      view.setAttribute("width", imgSize);
      view.setAttribute("height", imgSize);
      stat.setAttribute("class",      "circle");
      // status indicator
      deltaT=Math.floor(epochTime/1000-element.time);
      redFactor=deltaT/SecondsToNodeLoss; // BUG : not changeing color
      if(redFactor > 1){
        redFactor = 1;
      }
      red     = Math.floor(255 * redFactor)
      green   = Math.floor(255 * (1-redFactor) )
      stat.style.background="rgb("+red+","+green+",0)"
      // text field
      text.innerHTML = element.name;
      text.style.width="100%"
      view.setAttribute("onclick", "contentView_nodes('" + element.name + "')");
      td_view.appendChild(view);
      td_text.appendChild(text);
      td2_stat.appendChild(stat);
    });
    // _("Cleaning pre existing hierarchy tree")
    while (hierarchyTree.firstChild) {
      hierarchyTree.removeChild(hierarchyTree.firstChild);
    }
    hierarchyTree.appendChild(newHierarchyTree);
    if(selectedNode){
      colorSelected($('r2c1_nodes'), $(selectedNode));
    }
    _("Got new node listing");
    _(listing)
  });
}
// change view
function updatePage(page){
  var pages=[$("nodes"),$("debug"),$("scripts"),$("progs"),$("data")];
  pages.forEach(function(element, index, array){
    element.style.visibility= "hidden";
  });
  $(page).style.visibility= "visible";
}

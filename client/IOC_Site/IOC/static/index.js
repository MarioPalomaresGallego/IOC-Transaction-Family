RESULTS_PER_PAGE = 4

/* SAWTOOTH NAMESPACE CALCULATION */

function calculate_namespace(){
    const generic_array = crypto.subtle.digest('SHA-512', 'ioc');
    const typed_array = Array.from(new Uint8Array(hashBuffer)); 
    window.IOC_NAMESPACE = crypto.subtle.digest('SHA-512', 'ioc')
                        .map(b => b.toString(16).padStart(2, '0')).join('').substring(0,6);
}


function generate_keys(){

    // Generate the pair of keys
    const context = window.createContext('secp256k1');
    const privateKey = context.newRandomPrivateKey().asHex();

    // Store the keys on the local storage
    localStorage.setItem("privkey",privateKey);

}


/* WEBSOCKET USED TO REFRESH THE WEB INTERFACE */

let ws = new WebSocket('ws:localhost:8008/subscriptions')

ws.onopen = () => {
    ws.send(JSON.stringify({
      'action': 'subscribe',
    }))
  }

var initial = 0;
ws.onmessage = (event) =>{

    if(initial == 0){
        initial = 1;
        return
    }

    console.log(event.data)
    info = JSON.parse(event.data)
    block_id = info.block_id
    window.state_changes = info.state_changes
    http_req(window.location.href + "block/?block_id=" + block_id,0)
}


function process_block(xhttp){
    return function (){
        if (xhttp.readyState == 4 && xhttp.status == 200) {

            batches = JSON.parse(xhttp.responseText).data.batches
            console.log(xhttp.responseText)
            for(const b of batches){
                for(const t of b.transactions){

                    console.log("ey que pasa")
                    if(t.header.family_name != "ioc") continue;

                    type = "Root Report"
                    for(const c of window.state_changes){
                        if(atob(c.value).includes(t.header_signature) && atob(c.value).split(",").length >1) type = "Addition"
                    }
                    report_raw = atob(t.payload)
                    report = JSON.parse(report_raw)

                    table = document.getElementById("table_submissions");
                    template = document.getElementsByClassName("tr")[1];
                    new_tr = template.cloneNode(true);

                    new_tr.setAttribute('onclick','details("' + t.header_signature + '")')
                    new_tr.getElementsByClassName("machine")[0].innerText = "Windows 7";
                    new_tr.getElementsByClassName("date")[0].innerText = report.info.started;
                    new_tr.getElementsByClassName("sandbox")[0].innerText = report.info.version;
                    new_tr.getElementsByClassName("type")[0].innerText = type;
                    new_tr.getElementsByClassName("md5")[0].innerText = report.target.file.md5;
                    new_tr.getElementsByClassName("sha1")[0].innerText = report.target.file.sha1;
                    new_tr.getElementsByClassName("sha256")[0].innerText = report.target.file.sha256;

                    table.insertBefore(new_tr,table.children[2])

                    window.total_items = window.total_items + 1;
                    window.total_pages = Math.ceil(window.total_items/RESULTS_PER_PAGE);

                    if(window.total_items % RESULTS_PER_PAGE ==1){
                        adjust_pages(window.total_pages,window.total_pages+1)

                    }
                    change_page("page",current_page);

                }
            }
        }else if(xhttp.readyState == 4 && xhttp.status!=200){
            console.error("Error requesting block information") 
        }
    }
}

function update_DOM(xhttp){
    return function(){
        if (xhttp.readyState == 4 || xhttp.status == 200) {
            
        }else if(xhttp.readyState == 4 && xhttp.status!=200){
            
        }
    }

}

/* FUNCTIONS FOR THE CONTRIBUTE POPUP */


/* Makes the contribute pop-up appear and disappear*/
function contribute(action){
    if(action==1){
        document.getElementById("background_black").style.display="block";
        document.getElementById("contribute").style.display="block";

    }else{
        document.getElementById("contribute").style.display="none";
        document.getElementById("background_black").style.display="none";
        document.getElementById("contribute_form").style.display="block";
        document.getElementById("success").style.display="none";
        document.getElementById("error").style.display="none";
    }
}

/* Uploads the file to the server */
function upload(){
    if(localStorage.getItem("privkey") == null){
        generate_keys()
    }
    http_req(window.location.href + "upload/",2);
    document.getElementById("contribute_form").style.display="none";
    document.getElementById("loading").style.display="block";
}

function upload_finish(xhttp){
    return function(){
        document.getElementById("loading").style.display="none";
        if (xhttp.readyState == 4 && xhttp.status == 200) {

            document.getElementById("success").style.display="block";
            report = document.getElementById("report").value
            sample = document.getElementById("sample").value
            date = (new Date()).toISOString().replace("T", " ").replace(/\.[0-9]*Z/,"")
            table = document.getElementById("table_uploads")
            new_upload = document.getElementsByClassName("upload")[0].cloneNode(true)

            new_upload.getElementsByClassName("sample")[0].innerText = sample 
            new_upload.getElementsByClassName("report")[0].innerText = report
            new_upload.getElementsByClassName("date")[0].innerText = date
            //new_upload.getElementsByClassName("batch_id")[0].innerText = xhttp.responseText
            new_upload.getElementsByClassName("state")[0].innerText = "PENDING"

            table.insertBefore(new_upload,table.children[2])
            

        }else if(xhttp.readyState == 4 && xhttp.status!=200){
            document.getElementById("error").style.display="block";
        }
    }
}

/* GENERIC XML REQUEST FUNCTION */

function http_req(url,type) {

    var xhttp = new XMLHttpRequest();
    
    if(type == 0){
        xhttp.onreadystatechange = process_block(xhttp);
    }else if (type==1){
        xhttp.onreadystatechange = update_DOM(xhttp);
    }else{
        xhttp.onreadystatechange = upload_finish(xhttp);
    }

    if(type <2) xhttp.open("GET", url, true);
    else  xhttp.open("POST",url,true)

    if(type==2){

        var formData = new FormData(document.forms.namedItem("contribute_form"));
        formData.append("privkey",localStorage.getItem("privkey"));
        formData.append("csrfmiddlewaretoken",document.getElementsByName("csrfmiddlewaretoken")[0].value);
        xhttp.send(formData)

    }else{
        xhttp.send();
    }
}


function details(tx_id,sha256){
    window.location.href = window.location.href + "details/?tx_id=" + tx_id + "&sha256=" + sha256;
}

current_page = 0
window.onload = function() {
    window.total_items = document.getElementsByClassName("content").length
    window.total_pages = Math.ceil(total_items/RESULTS_PER_PAGE)
    window.current_info = "content"
    change_page("page",0)
    document.getElementById("page0").checked = true
};

function change_page(action,value,class_name){

    past_page = current_page

    if(action == "left") {
        if (current_page == 0) return;
        current_page = current_page - 1;
    }else if(action == "page") current_page = value;
    else{
        if(current_page == total_pages -1) return;
        current_page = current_page +1;
    } 
    //Hide all invalid elements
    hide = document.querySelectorAll('div[show="false"]')
    for( elem of hide){
        elem.style.display="none"
    }

    //Hide current visible elements
    shown = document.querySelectorAll('.'+ current_info + '[show="true"][style*="block"]')
    for(elem of shown){
        elem.style.display="none";
    }

    //Show proper elements
    show = document.querySelectorAll('.' + current_info + '[show="true"]')
    for(let i=current_page*RESULTS_PER_PAGE;i<current_page*RESULTS_PER_PAGE+ RESULTS_PER_PAGE;i++){
        if(i>=total_items) break;
        document.getElementsByClassName(current_info)[i].style.display="block";
    }

    document.getElementById("page" +current_page).checked = true
}

function isValidHash(type,hash) {
    if(type=="md5" && hash.match("[a-fA-F0-9]{32}")) return true
    else if(type="sha1" && hash.match("[a-fA-F0-9]{40}")) return true
    else if(type="sha256" && hash.match("[a-fA-F0-9]{64}")) return true
    else return false;
}


function search(){
    type = document.querySelector('input[name = "hash"]:checked').value
    input = document.getElementById("search_bar")
    hash = input.value

    if(!isValidHash(type,hash)){
        alert("Invalid Hash Format")
        input.value=""
    }else{
        total_items = 0
        for(elem of document.getElementsByClassName("content")){
            if (elem.getElementsByClassName(type)[0].innerText == hash){
                elem.setAttribute("show","true"); 
                total_items = total_items + 1;
            }
            else elem.setAttribute("show","false")
        }
        prev_total_pages = total_pages
        total_pages = Math.ceil(total_items/RESULTS_PER_PAGE)
        change_page("page",0)
        adjust_pages(prev_total_pages,total_pages)
    }
}

function _clear(){
    total_items = 0

    for(elem of document.getElementsByClassName(current_info)){
        elem.setAttribute("show","true"); 
        total_items = total_items + 1;
    }
    prev_total_pages = total_pages
    total_pages = Math.ceil(total_items/RESULTS_PER_PAGE)
    input = document.getElementById("search_bar")
    adjust_pages(prev_total_pages,total_pages)
    change_page("page",0)
}

function adjust_pages(prev, post){

    page_list = document.getElementsByClassName("page_num")[0]
    if(prev<post){
        template = document.getElementById("page0").parentElement
        for(let i = prev; i<post;i++){
            new_page = template.cloneNode(true);
            new_page_input = new_page.children[0]
            new_page_input.setAttribute("id","page" + i);
            new_page_input.setAttribute("value", i);
            new_page_label = new_page.children[1];
            new_page_label.setAttribute("for","page" + i);
            new_page_label.innerText = i+1;
            page_list.append(new_page);
        }
    }
    if(prev>post){
        for(let i=prev; i>post;i--){
            page_list.removeChild(document.getElementById("page" + (i-1)).parentElement)
        }
    }
}

function change_content(id){
    prev_total_pages = total_pages
    if(id==1){
        document.getElementById("table_submissions").style.display="block"
        document.getElementById("table_uploads").style.display="none"
        current_info = "content"
    }else{
        document.getElementById("table_submissions").style.display="none"
        document.getElementById("table_uploads").style.display="block" 
        current_info = "upload"
    }
    _clear()
}
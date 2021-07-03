RESULTS_PER_PAGE = 5

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

                    table = document.getElementById("table");
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

                    table.insertBefore(new_tr,table.childNodes[3])

                    window.total_items = window.total_items + 1;
                    window.total_pages = Math.ceil(window.total_items/RESULTS_PER_PAGE);

                    if(window.total_items % RESULTS_PER_PAGE ==1){
                        page_list = document.getElementsByClassName("page_num")[0]
                        template = document.getElementById("page")

                        new_page = template.cloneNode(true);
                        new_page_input = new_page.children[0]
                        new_page_input.setAttribute("id","page" + window.total_pages);
                        new_page_input.setAttribute("value", window.total_pages);
                        new_page_label = new_page.children[1];
                        new_page_label.setAttribute("for","page" + window.total_pages);
                        new_page_label.innerText = total_pages;

                        page_list.append(new_page);

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


function details(tx_id){
    window.location.href = window.location.href + "details/?tx_id=" + tx_id;
}

current_page = 0
window.onload = function() {
    window.total_items = document.getElementsByClassName("content").length
    window.total_pages = Math.ceil(total_items/RESULTS_PER_PAGE)

};

function change_page(action,value){

    past_page = current_page

    if(action == "left") {
        if (current_page == 0) return;
        current_page = current_page - 1;
    }else if(action == "page") current_page = value;
    else{
        if(current_page == total_pages -1) return;
        current_page = current_page +1;
    } 

    //Hide all currernt elements
    for(let i=past_page*RESULTS_PER_PAGE;i<=past_page*RESULTS_PER_PAGE+RESULTS_PER_PAGE;i++){
        if(i==total_items) break;
        document.getElementsByClassName("content")[i].style.display="none";
    }

    document.getElementById("page" + (current_page + 1)).checked = true
    
    for(let i=current_page*RESULTS_PER_PAGE;i<current_page*RESULTS_PER_PAGE+ RESULTS_PER_PAGE;i++){
        if(i==total_items) break;
        document.getElementsByClassName("content")[i].style.display="block";
    }
}

function isValidHash(type) {
    if(type=="md5" && s.match("/[a-fA-F0-9]{30}/")) return true
    else if(type="sha1" && s.match("/[a-fA-F0-9]{40}/")) return true
    else if(type="sha256" && s.match("/[a-fA-F0-9]{64}/")) return true
    else return false;
}


function search(){
    hash = document.querySelector('input[name = "hash"]:checked').value
    input = document.getElementById("search_bar").value

    if(!isValidHash(hash)){
        alert("Invalid Hash Format")
        input.value=""
    }else{
        for(elem of document.getElementsByClassName("content")){
            if (elem.getElementsByClassName(hash) == input) elem.style.display="block"
            else elem.style.display = "block"
        }
    }

    change_page(0)

    list_hashes = document.getElementById
}

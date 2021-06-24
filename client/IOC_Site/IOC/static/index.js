
/* SAWTOOTH NAMESPACE CALCULATION */

function calculate_namespace(){
    const generic_array = crypto.subtle.digest('SHA-512', 'ioc');
    const typed_array = Array.from(new Uint8Array(hashBuffer)); 
    window.IOC_NAMESPACE = crypto.subtle.digest('SHA-512', 'ioc')
                        .map(b => b.toString(16).padStart(2, '0')).join('').substring(0,6)
}


/* WEBSOCKET USED TO REFRESH THE WEB INTERFACE */

let ws = new WebSocket('ws:localhost:8008/subscriptions')

ws.onopen = () => {
    ws.send(JSON.stringify({
      'action': 'subscribe',
      'event_type': 'sawtooth/block-commit',
    }))
  }

ws.onmessage = (event) =>{
    if (event.wasClean){
        block_id = JSON.parse(event.data).block_id
        http_req("http://localhost:8008/blocks/" + block_id,0)
    }
}

function process_block(xhttp){
    return function (){
        if (xhttp.readyState == 4 && xhttp.status == 200) {

            batches = JSON.parse(xhttp.responseText).data.batches
            for(let b=0;i<batches.length;b++){
                for(let t=0;t<b.transactions;t++){
                    window.tx_id = t.header_signature
                    addr = IOC_NAMESPACE + t.payload_sha512.substring(0,64)
                    http_req("http://localhost:8000/transactions/" + addr,1)
                }
            }
        }else{
            console.error("Error requesting block information") 
        }
    }
}

function update_DOM(xhttp){
    return function(){
        if (xhttp.readyState == 4 || xhttp.status == 200) {
            
        }else{
            
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
    }
}

/* Uploads the file to the server */
function upload(){
    http_req("http://localhost:8000/ioc/upload/",2);
    document.getElementById("contribute_form").style.display="none";
    document.getElementById("loading").style.display="block";
}

function upload_finish(xhttp){
    return function(){
        console.log(xhttp.readyState)
        console.log(xhttp.status)
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            document.getElementById("loading").style.display="none";
            document.getElementById("success").style.display="block";
        }else{
            console.log("Error on the request")
            console.log(this.status)
            console.log(this.responseText)
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
    else xhttp.open("POST",url,true)

    if(type==2){
        var formData = new FormData();
        formData.append("csrfmiddlewaretoken",document.getElementsByName("csrfmiddlewaretoken")[0].value)
        formData.append("file",document.getElementById("behavioural").files[0])
        formData.append("file",document.getElementById("sample").files[0])
        xhttp.send(formData)
    }else{
        xhttp.send();
    }
  }
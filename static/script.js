function uploadInvoice(){
    let file = document.getElementById("file").files[0];
    if(!file){ alert("Select a file"); return; }
    if(!["application/pdf","image/png","image/jpeg"].includes(file.type)){
        alert("Only PDF/PNG/JPG allowed"); return;
    }

    let formData = new FormData();
    formData.append("file", file);

    fetch("/process_invoice",{method:"POST",body:formData})
    .then(res=>res.json())
    .then(data=>{
        if(data.error){ alert(data.error); return; }

        document.getElementById("invoice_number").value = data.invoice_number || "";
        document.getElementById("date").value = data.date || "";
        document.getElementById("total").value = data.total || "";

        let tbody = document.querySelector("#result_table tbody");
        tbody.innerHTML = "";
        for(let field of ["invoice_number","date","total","vendor_name","bill_to","ship_to","subtotal","tax"]){
            let val = data[field] || "Not Found";
            let conf = data.confidence[field] || 0;
            let color = conf>=90 ? "#c8e6c9" : (conf>=70 ? "#fff9c4" : "#ffcdd2");
            let row = `<tr style="background:${color}">
                        <td>${field}</td>
                        <td>${val}</td>
                        <td>${conf}</td>
                       </tr>`;
            tbody.innerHTML += row;
        }
    })
    .catch(err=>{ console.error(err); alert("Invoice processing failed"); });
}

function saveData(){
    let data = {
        invoice_number: document.getElementById("invoice_number").value,
        date: document.getElementById("date").value,
        total: document.getElementById("total").value
    };
    fetch("/save_invoice",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)})
    .then(res=>res.json())
    .then(resp=>{ alert(resp.message); })
    .catch(err=>{ console.error(err); alert("Failed to save invoice"); });
}
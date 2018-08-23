/**
 * Created by Mario on 2/8/18.
 */

function previewfile(file) {
    if (tests.filereader === true && acceptedTypes[file.type] === true) {
        var reader = new FileReader();
        reader.onload = function (event) {
            var image = new Image();
            image.src = event.target.result;
            image.name = "imagen-drop"
            image.id = "imagen-drop"
            image.width = 250; // a fake resize
            holder.appendChild(image);
        };

        reader.readAsDataURL(file);
    } else {
        holder.innerHTML += '<p>Uploaded ' + file.name + ' ' + (file.size ? (file.size / 1024 | 0) + 'K' : '');
        console.log(file);
    }
}

function readfiles(files) {
    var formData = tests.formdata ? new FormData() : null;
    for (var i = 0; i < files.length; i++) {
        if (tests.formdata) formData.append('file', files[i]);
        previewfile(files[i]);
    }

    // now post a new XHR request
    if (tests.formdata) {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/devnull.php');
        xhr.onload = function () {
            progress.value = progress.innerHTML = 100;
        };

        if (tests.progress) {
            xhr.upload.onprogress = function (event) {
                if (event.lengthComputable) {
                    var complete = (event.loaded / event.total * 100 | 0);
                    progress.value = progress.innerHTML = complete;
                }
            }
        }

        xhr.send(formData);
    }
}

function addNewRow() {
    var table = document.getElementById("order_details").getElementsByTagName('tbody')[0];
    var row = table.insertRow(table.rows.length);
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    var cell3 = row.insertCell(2);
    var cell4 = row.insertCell(3);
    var cell5 = row.insertCell(4);

    var element_1 = document.createElement('div');
    element_1.innerHTML = '<input type="number" disabled="true" name="nombre_producto-' + table.rows.length + '" style="max-width: 74px" id="id_id_producto-' + table.rows.length + '"/>';
    cell1.appendChild(element_1);

    var element_2 = document.createElement('div');
    element_2.innerHTML = '<input type="text" class="form-control" onchange="$(this).AutocompleteRemainingFields(' + table.rows.length + ')" onkeyup="$(this).AutocompleteName(' + table.rows.length + ');" name="nombre_producto-' + table.rows.length + '" id="id_nombre_producto-' + table.rows.length + '" autocomplete="on" placeholder="Escriba el nombre">';
    cell2.appendChild(element_2);

    var element_3 = document.createElement('div');
    element_3.innerHTML = '<input disabled="true" type="text" disabled="true" style="max-width: 51px" name="precio-producto-' + table.rows.length + '" id="precio_id_producto-' + table.rows.length + '"/>€';
    cell3.appendChild(element_3);

    var element_4 = document.createElement('div');
    element_4.innerHTML = '<input disabled="true" type="text" disabled="true" style="max-width: 74px" name="precio_oferta_producto-' + table.rows.length + '" id="precio_oferta_id_producto-' + table.rows.length + '"/>€';
    cell4.appendChild(element_4);

    var element_5 = document.createElement('div');
    element_5.innerHTML = '<button type="button" name="trash-row-' + table.rows.length + '" onclick="deleteThisRow(' + table.rows.length + ')" class="btn btn-default"><span class="glyphicon glyphicon-trash"></span></button>';
    cell5.appendChild(element_5);
}

function setZero(id) {
    document.getElementById("producto-" + id).value = "0";
    document.getElementById("fila-" + id).classList.add("strikeout");
}

function deleteThisRow(row_index) {
    var table = document.getElementById("order_details").getElementsByTagName('tbody')[0];
    table.deleteRow(row_index - 1)
}

function deleteThisRowWithDatabase(row_index, object_name, object_pk) {
    var table = document.getElementById("order_details").getElementsByTagName('tbody')[0];
    var value = table.rows[row_index - 1].cells[0].innerHTML.replace('#','').trim()
    $.ajax({
        url: "/ajax/remove_product_from_list",
        data: {
            'id': value,
            'object_name': object_name,
            'object_pk': object_pk,
        },
        dataType: 'json',
        success: function (data) {
            table.deleteRow(row_index - 1)
            alert("Eliminado correctamente")
        }
    });

}

function setZero(id) {
    document.getElementById("producto-" + id).value = "0";
    document.getElementById("fila-" + id).classList.add("strikeout");
}

function onlyNumbers(evt) {
    evt = (evt) ? evt : window.event;
    var charCode = (evt.which) ? evt.which : evt.keyCode;
    return !((charCode < 48 || charCode > 57) && charCode != 44 && charCode > 31);
}
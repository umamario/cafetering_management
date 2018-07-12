
jQuery(function() {
    $("#id_sell_currency").on('keyup', function(){
        var value = $(this).val();
        $.ajax({
            url: "/ajax/autocomplete_sell_currency",
            data: {
              'search': value
            },
            dataType: 'json',
            success: function (data) {
                $("#id_sell_currency").autocomplete({
                source: data.list,
                minLength: 1
                });
            }
        });
    });
  });

jQuery(function() {
    $("#id_buy_currency").on('keyup', function(){
        var value = $(this).val();
        $.ajax({
            url: "/ajax/autocomplete_buy_currency",
            data: {
              'search': value
            },
            dataType: 'json',
            success: function (data) {
                $("#id_buy_currency").autocomplete({
                source: data.list,
                minLength: 1
                });
            }
        });
    });
  });

$(function() {
    $( ".datepicker" ).datepicker({
      changeMonth: true,
      changeYear: true,
      minDate: 0,
      dateFormat: 'dd/mm/yy',
    });
  });


function getRate(sell, buy) {
    $.ajax({
        url: '/ajax/get_rate',
        data: {
            'sell_currency': sell,
            'buy_currency': buy,
        },
        dataType: 'json',
        success: function (data) {
            document.getElementById('id_client_rate').value = data.rate;
        }
    });
}


function setRate(){
    if (document.getElementById('id_buy_currency').value.length == 3 && document.getElementById('id_sell_currency').value.length == 3){
        getRate(document.getElementById('id_sell_currency').value, document.getElementById('id_buy_currency').value)
    }
}

function setBuyAmount(){
    if (document.getElementById('id_client_rate').value != "") {
        buy_amount = document.getElementById('id_sell_amount').value * document.getElementById('id_client_rate').value;
        document.getElementById('id_buy_amount').value = buy_amount.toFixed(4);
    }
}
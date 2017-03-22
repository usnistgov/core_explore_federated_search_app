var timeout_federated = null;

/*
* Wait for Jquery to be ready
* */
var defer_loadListProviderFederated = function(){
    $(document).ready(function() {
        $('#error-div-federated').hide();
        loadListProviderFederated();
    })
};

// Waiting JQuery
onjQueryReady(defer_loadListProviderFederated);

/*
* Load provider's list from federated search
* */
loadListProviderFederated = function() {
    $('#error-div-federated').hide();
    var query_id = $("#query_id").html();
    $.ajax({
        url: getDataSourceFederatedUrl,
        type : "GET",
        data: {
            id_query: query_id
        },
        success: function(data){
            // Display federated search's data sources
            $("#list-data-sources-federated-content").html(data);
            // Add action on each federated search's checkbox
            $("input.checkbox-federated:checkbox").on(  "click",
                                                        {id_query: query_id},
                                                        updateQueryDataSourcesFederatedTimeout);
        },
        error: function(data){
            if (data.responseText != ""){
                showErrorMessageFederated(data.responseText);
            }else{
                return (true);
            }
        }
    });
};

/*
* Update the timeout
* And update query data sources when it done
* */
updateQueryDataSourcesFederatedTimeout = function(event){
    // Clear the timeout
    if(timeout_federated) {
        clearTimeout(timeout_federated);
    }
    // Start timeout
    timeout_federated = setTimeout(updateQueryDataSourcesFederated(event), 500);
};

/*
* AJAX: Update query data sources
* */
updateQueryDataSourcesFederated = function(event){
    $.ajax({
        url: updateQueryDataSourcesFederatedUrl,
        type : "GET",
        data: {
            'id_query': event.data.id_query,
            'id_instance': event.target.value,
            'to_be_added': event.target.checked
        },
        success: function(data){
        },
        error: function(data){
            if (data.responseText != ""){
                showErrorMessageFederated(data.responseText);
            }else{
                return (true);
            }
        }
    });
};

/*
* Show label error with message
* */
showErrorMessageFederated = function(message){
    $('#error-div-federated').show();
    $('#error-message').text(message);
};
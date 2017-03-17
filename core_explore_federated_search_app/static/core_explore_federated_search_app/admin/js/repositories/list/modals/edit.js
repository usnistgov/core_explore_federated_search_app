$(document).ready(function() {
    $('.edit').on('click', editRepositoryOpenModal);
    $('#edit-repository-form').on('submit', editRepositorySave);
    $('#edit-repository-save').on('click', editRepositorySave);
});


/**
 * Edit general information of a repository
 */
editRepositoryOpenModal = function(event) {
    event.preventDefault();

    var repositoryName = $(this).parent().siblings(':first').text();
    var repositoryId = $(this).parent().attr('id');

    $("#edit-repository-name").val(repositoryName);
    $("#edit-repository-id").val(repositoryId);
    $("#edit-repository-modal").modal("show");
};

editRepositorySave = function(event) {
    event.preventDefault();

    var repositoryId = $("#edit-repository-id").val();
    var repositoryName = $("#edit-repository-name").val();

    $.ajax({
        url : editRepositoryPostUrl,
        type : "POST",
        data: {
            "id": repositoryId,
            "title": repositoryName
        },
        success: function(data){
            location.reload();
        },
        error: function(data){

        }
    });
};

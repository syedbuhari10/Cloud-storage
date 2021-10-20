function deleteNote(noteId) {
    fetch("/delete-note", {
      method: "POST",
      body: JSON.stringify({ noteId: noteId }),
    }).then((_res) => {
      window.location.href = "/";
    });
  }
function download(url){
    $('<iframe>', { id:'idown', src:url }).hide().appendTo('body').click();
}

function url(id,filename){
  console.log("Entered function")
    $.ajax({
        url: '/download-file?id='+id+'&filename='+filename,
        success: function(url){
            console.log(url)
            download(url);
        }
    })
    return false;
}
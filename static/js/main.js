window.onload = function(){
const sidebar = document.querySelector('.sidebar');
const mainContent = document.querySelector('.main-content');
const sidebar_button = document.querySelector('.sidebar-button');
const sidebar_content = document.querySelector('.sidebar-content');
const index_select = document.querySelector('#index-select');
const favorites_button = document.querySelector('.favorites-button');
const favorites_text = document.querySelector('.inline-p')
var trigger = document.getElementById('progress-bar-trigger');
if(favorite_index!="pas de favorie"){
    index_select.value = favorite_index;
}

trigger.addEventListener('click', function(e) {
  var web_socket_url = 'ws://'+window.location.host + window.location.pathname+ `/ws/${index_select.value}`
  console.log(web_socket_url);
  var ws = new WebSocket(web_socket_url);
  ws.onmessage = function(event) {
    var json_message = JSON.parse(event.data)
    var bar = document.getElementById("progress-bar");
    var barMessage = document.getElementById("progress-bar-message");
    barMessage.textContent = json_message['progess'] +'%\n'+json_message['message']
    bar.style.width = json_message['progess'] +'%'
  };
})
define_title = function () {
    document.getElementById('index_name').textContent = index_select.options[index_select.selectedIndex].text;
}

check_favorite = function () {
    if (index_select.value == favorite_index){
        if (!favorites_button.classList.contains('favorites-selected')){
            favorites_button.classList.toggle('favorites-selected')
        }
        favorites_text.textContent = "suprimer favoris ?";
    }else{
        if (favorites_button.classList.contains('favorites-selected')){
            favorites_button.classList.toggle('favorites-selected')
        }
        favorites_text.textContent = "mettre en favoris ?";
    }


}
define_title()
check_favorite()
sidebar_button.onclick = function () {
    sidebar.classList.toggle('sidebar_small');
    sidebar_content.classList.toggle('sidebar-content_disable');
    mainContent.classList.toggle('main-content_large')
    if (sidebar_button.textContent == ">"){
        sidebar_button.textContent="<";
    }else{
        sidebar_button.textContent=">";
    }
}


document.getElementById("deconection-button").onclick = function () {
    location.href = "/disconnect";
};

favorites_button.onclick = function() {
    var endPoint = window.location.origin + '/change_favorite'
    var client = new XMLHttpRequest();
    client.open("POST", endPoint, false);
    client.withCredentials = true;
    client.setRequestHeader("Content-Type","application/json");

    if (!favorites_button.classList.contains('favorites-selected')){
        favorites_button.classList.toggle('favorites-selected')
        favorites_text.textContent = "suprimer favoris ?";
        favorite_index = index_select.value;
        var data = JSON.stringify({index: index_select.value, how: "change"});
        console.log(data)
        client.send(data);

    }else{
        favorites_button.classList.toggle('favorites-selected')
        favorites_text.textContent = "mettre en favoris ?";
        favorite_index = null;
        var data=JSON.stringify({index: index_select.value, how: "del"});
        console.log(data)
        client.send(data);

    }
}

index_select.addEventListener("change", define_title)
index_select.addEventListener("change", check_favorite)
}



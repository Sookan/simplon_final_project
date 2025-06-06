window.onload = function(){
const document.getElementById('progress-bar-trigger');
var trigger = document.getElementById('progress-bar-trigger');
trigger.addEventListener('click', function(e) {
  var web_socket_url = 'ws://'+window.location.origin+/ws/
  var ws = new WebSocket(`ws://127.0.0.1:8000/train/ws`);
  ws.onmessage = function(event) {
    var json_message = JSON.parse(event.data)
    var bar = document.getElementById("progress-bar");
    var barMessage = document.getElementById("progress-bar-message");
    barMessage.textContent = json_message['message']
    bar.style.width = json_message['progess'] +'%'
  };
})
}